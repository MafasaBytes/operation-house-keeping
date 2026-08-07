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


class TestCheckpointNonRegression:
    def test_stale_projector_does_not_regress_checkpoint(self, tmp_path):
        runner, ds_store, _, temporal, projector_a, _ = build(tmp_path)
        runner.run("printer-1")

        projector_b = TemporalProjector(ds_store, temporal)
        # B validates an EMPTY watermark and pauses (stale local state)...
        import unittest.mock as mock

        stale_attempts = projector_b._ordered_attempts("printer-1")[:1]
        with mock.patch.object(projector_b, "_validate_state",
                               return_value=None), \
             mock.patch.object(projector_b, "_ordered_attempts",
                               return_value=stale_attempts):
            # ...A projects everything and advances the checkpoint...
            projector_a.project("printer-1")
            with temporal.reader() as conn:
                expected_max = temporal.ledger_max_order_key(conn, "printer-1")
            control = temporal.ordered_logical_dump()
            # ...then B resumes, sees only attempt 1 (already in the
            # ledger), and must NOT write the checkpoint back to it.
            report_b = projector_b.project("printer-1")

        assert report_b.halted is None
        with temporal.writer() as conn:
            checkpoint = temporal.load_checkpoint(conn, "printer-1")
            ledger_max = temporal.ledger_max_order_key(conn, "printer-1")
        assert checkpoint.order_key().sort_tuple() == tuple(ledger_max)
        assert tuple(ledger_max) == tuple(expected_max)  # never regressed
        assert temporal.ordered_logical_dump() == control  # no duplicates

        # the next projection is idempotent and does NOT request rebuild
        report_next = TemporalProjector(ds_store, temporal).project("printer-1")
        assert report_next.halted is None
        assert temporal.ordered_logical_dump() == control


class TestIncompleteRebuildReport:
    def _make_incomplete_evidence(self, runner, ds_store, transport,
                                  monkeypatch):
        """Crash the run after acquisition commits but before extraction
        persists — the DS-004 crash shape that leaves committed attempts
        with incomplete extraction. Trailing whitespace gives each sweep
        genuinely NEW payload bytes (identical payloads are checksum-
        reused and already extracted, so put_extraction is never
        reached)."""
        from backend.data_sources.connectors.http_api import TransportResponse

        for path, response in list(transport.script.items()):
            transport.script[path] = TransportResponse(
                status=response.status, headers=dict(response.headers),
                body=response.body + b" ")
        original = ds_store.put_extraction
        monkeypatch.setattr(
            ds_store, "put_extraction",
            lambda r: (_ for _ in ()).throw(RuntimeError("upstream crash")))
        with pytest.raises(RuntimeError):
            runner.run("printer-1")
        monkeypatch.setattr(ds_store, "put_extraction", original)

    def test_rebuild_from_incomplete_evidence_returns_public_report(
        self, tmp_path, monkeypatch
    ):
        runner, ds_store, transport, temporal, projector, _ = build(tmp_path)
        self._make_incomplete_evidence(runner, ds_store, transport,
                                       monkeypatch)
        report = projector.rebuild("printer-1")  # must NOT raise
        assert report.halted is not None
        assert report.halted.reason == "extraction_incomplete"
        assert report.deferred_incomplete
        assert report.attempts_processed == 0     # rolled back == zero committed
        assert report.occurrences_created == 0
        dump = temporal.ordered_logical_dump()
        assert dump["temporal_attempts"] == []    # nothing persisted
        assert dump["temporal_occurrences"] == []

    def test_rebuild_rollback_preserves_previous_projection_exactly(
        self, tmp_path, monkeypatch
    ):
        runner, ds_store, transport, temporal, projector, _ = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        before = temporal.ordered_logical_dump()

        # a later incomplete attempt appears in the evidence
        self._make_incomplete_evidence(runner, ds_store, transport,
                                       monkeypatch)
        report = projector.rebuild("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "extraction_incomplete"
        assert report.attempts_processed == 0
        # previous temporal projection byte-for-byte preserved
        assert temporal.ordered_logical_dump() == before


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


class TestVersionMismatchRebuildGuard:
    def test_source_local_inconsistency_allows_rebuild(self, tmp_path):
        runner, _, _, temporal, projector, _ = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                conn.execute("UPDATE checkpoints SET last_attempt_id="
                             "'f' || substr(last_attempt_id, 2)")
        assert projector.project("printer-1").halted is not None
        report = projector.rebuild("printer-1")   # local repair allowed
        assert report.halted is None
        assert projector.project("printer-1").halted is None

    def test_global_version_mismatch_refuses_per_source_rebuild(self, tmp_path):
        runner, _, _, temporal, projector, _ = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        before = temporal.ordered_logical_dump()
        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                conn.execute("UPDATE meta SET value='0.0.1' "
                             "WHERE key='projector_version'")
        report = projector.rebuild("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "TEMPORAL_REBUILD_REQUIRED"
        assert "rebuild_all" in report.halted.detail
        assert temporal.ordered_logical_dump() == before  # nothing written

    def test_rebuild_all_metadata_matches_row_stamps(self, tmp_path):
        runner, _, _, temporal, projector, _ = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        projector.rebuild_all(["printer-1"])
        schema, proj = projector.store.meta_versions()
        with projector.store.reader() as conn:
            stamps = {row[0] for row in conn.execute(
                "SELECT DISTINCT projector_version FROM temporal_attempts")}
        assert stamps == {proj}
