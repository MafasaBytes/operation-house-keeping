"""TS-001 repair-slice regression tests: adapter-scoped coverage,
checkpoint non-regression under interleaving, honest incomplete rebuild,
cutoff validation, and version-mismatch rebuild guards."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend.data_sources.contracts import AcquisitionAttempt
from backend.temporal_state.contracts import (
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalQueryError,
)
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import (
    happy_script,
    make_runner,
)

FIXTURES = Path("backend/data_sources/testing/fixtures/api")

SUBJECT = SourceSubjectRef(
    source_id="printer-1", adapter_id="moonraker", subject_identifier="extruder")
PROP = SourcePropertyRef(
    extraction_route="api:moonraker:v1", item_key="printer_objects",
    json_pointer="/result/status/extruder/temperature")

AS_OF = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)


def build(tmp_path):
    runner, ds_store, transport = make_runner(tmp_path / "ds", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db",
                             evidence_root=ds_store.base_dir)
    projector = TemporalProjector(ds_store, temporal)
    queries = TemporalQueries(temporal)
    return runner, ds_store, transport, temporal, projector, queries


def foreign_adapter_attempt(ds_store, outcome="failed",
                            adapter_id="other_adapter",
                            attempt_id="f" * 32,
                            started=datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)):
    """Hand-written evidence: a later attempt for the SAME source and item
    key but a different adapter — the owner's contamination reproduction."""
    success = outcome == "succeeded"
    return AcquisitionAttempt(
        attempt_id=attempt_id, ingestion_run_id="run-printer-1-0099",
        source_id="printer-1", item_key="printer_objects",
        adapter_id=adapter_id, endpoint_id="printer_objects_query",
        sweep_position=0, started_at=started, finished_at=started,
        received_at=started if success else None,
        outcome=outcome, request_fingerprint="sha256:" + "ab" * 32,
        request_canonical="GET /other/api", target_origin="http://127.0.0.1:9",
        status_code=200 if success else None, allowlisted_headers={},
        transport_security="plaintext_http_explicit",
        response_size_bytes=None if not success else 2, retries_used=0,
        payload_checksum=None, raw_record_id=None, payload_reused=False,
        failure=None if success else {
            "error_code": "ACQUIRE_TIMEOUT", "redacted_message": "x"},
    )


class TestAdapterScopedCoverage:
    def test_other_adapter_failure_does_not_contaminate(self, tmp_path):
        runner, ds_store, _, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        ds_store.put_attempt(foreign_adapter_attempt(ds_store))
        projector.project("printer-1")

        latest = queries.latest_observed(SUBJECT, PROP, AS_OF)
        # adapter B's later failure must not touch adapter A's evidence
        assert latest.evidence_quality.intervening_failed_attempts == 0
        assert latest.evidence_quality.latest_applicable_attempt_outcome == (
            "observations_projected")

        fresh = queries.freshness("printer-1", AS_OF)
        moonraker_entries = [e for e in fresh
                             if e.subject.adapter_id == "moonraker"]
        assert all(e.failed_attempts_since == 0 for e in moonraker_entries)

    def test_other_adapter_ledger_rows_do_not_contaminate(self, tmp_path):
        """Quarantined, empty-snapshot, and non-observing attempts from
        adapter B (same source and item key) must not affect adapter A's
        latest-observed evidence quality."""
        from backend.temporal_state.contracts import TemporalAttemptEvent

        runner, _, _, temporal, projector, queries = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")

        later = datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)

        def ledger_row(attempt_id, outcome, code, count):
            return TemporalAttemptEvent(
                attempt_id=attempt_id, source_id="printer-1",
                adapter_id="other_adapter",
                endpoint_id="printer_objects_query",
                item_key="printer_objects", sweep_position=0,
                ingestion_run_id="run-printer-1-0099",
                attempt_started_at=later, received_at=later,
                finished_at=later, effective_wall_time=later,
                effective_time_basis="received_at", outcome=outcome,
                observation_count=count, failure_or_quarantine_code=code,
                source_warning_count=0, projector_version="1.0.0")

        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                temporal.insert_attempt_event(conn, ledger_row(
                    "a" * 32, "quarantined", "EXTRACT_MALFORMED", 0))
                temporal.insert_attempt_event(conn, ledger_row(
                    "b" * 32, "observations_projected", None, 0))  # empty
                temporal.insert_attempt_event(conn, ledger_row(
                    "c" * 32, "observations_projected", None, 3))  # non-obs.

        quality = queries.latest_observed(SUBJECT, PROP, AS_OF).evidence_quality
        assert quality.intervening_failed_attempts == 0
        assert quality.intervening_quarantined_attempts == 0
        assert quality.later_empty_snapshots == 0
        assert quality.later_snapshots_without_property == 0
        assert quality.latest_applicable_attempt_outcome == (
            "observations_projected")

    def test_moonraker_failure_still_counts_for_moonraker(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportError

        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = TransportError(
            "timeout", "x")
        runner.run("printer-1")
        projector.project("printer-1")
        latest = queries.latest_observed(SUBJECT, PROP, AS_OF)
        assert latest.evidence_quality.intervening_failed_attempts == 1
        assert latest.evidence_quality.latest_applicable_attempt_outcome == (
            "acquisition_failed")


class TestCutoffValidation:
    def test_naive_cutoffs_rejected_with_typed_error(self, tmp_path):
        runner, _, _, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        naive = datetime(2026, 8, 7, 23, 0, 0)  # no tzinfo
        with pytest.raises(TemporalQueryError) as excinfo:
            queries.latest_observed(SUBJECT, PROP, naive)
        assert excinfo.value.error_code == "TEMPORAL_NAIVE_CUTOFF"
        with pytest.raises(TemporalQueryError) as excinfo:
            queries.freshness("printer-1", naive)
        assert excinfo.value.error_code == "TEMPORAL_NAIVE_CUTOFF"

    def test_aware_non_utc_cutoff_normalized(self, tmp_path):
        from datetime import timedelta, timezone

        runner, _, _, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        offset = timezone(timedelta(hours=2))
        result = queries.latest_observed(
            SUBJECT, PROP, datetime(2026, 8, 8, 1, 0, 0, tzinfo=offset))
        assert result is not None  # 01:00+02:00 == 23:00Z
