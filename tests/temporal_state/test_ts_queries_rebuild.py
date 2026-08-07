"""TS-001 query and rebuild scenarios: as-of closure, five-way later-
coverage distinction, freshness, provenance, per-source rebuild."""

import json
from datetime import UTC, datetime
from pathlib import Path

from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import (
    fixture_response,
    happy_script,
    make_runner,
    make_source,
)

FIXTURES = Path("backend/data_sources/testing/fixtures/api")

SUBJECT = SourceSubjectRef(
    source_id="printer-1", adapter_id="moonraker", subject_identifier="extruder")
PROP = SourcePropertyRef(
    extraction_route="api:moonraker:v1", item_key="printer_objects",
    json_pointer="/result/status/extruder/temperature")
HEATER_PROP = SourcePropertyRef(
    extraction_route="api:moonraker:v1", item_key="printer_objects",
    json_pointer="/result/status/heater_bed/temperature")
HEATER_SUBJECT = SourceSubjectRef(
    source_id="printer-1", adapter_id="moonraker",
    subject_identifier="heater_bed")


def at(h, m, s):
    return datetime(2026, 8, 7, h, m, s, tzinfo=UTC)


def build(tmp_path):
    runner, ds_store, transport = make_runner(tmp_path / "ds", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db",
                             evidence_root=ds_store.base_dir)
    projector = TemporalProjector(ds_store, temporal)
    queries = TemporalQueries(temporal)
    return runner, ds_store, transport, temporal, projector, queries


def response_bytes(body: bytes):
    from backend.data_sources.connectors.http_api import TransportResponse

    return TransportResponse(
        status=200, headers={"Content-Type": "application/json"}, body=body)


class TestAsOfClosure:
    def test_before_between_after(self, tmp_path):
        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")                        # received ~19:00:0x
        transport.script["/printer/objects/query"] = fixture_response(
            "moonraker_printer_objects_changed.json")
        runner.run("printer-1")                        # received later
        projector.project("printer-1")

        assert queries.latest_observed(SUBJECT, PROP, at(18, 0, 0)) is None
        history = queries.history(SUBJECT, PROP)
        first_time = history[0].received_at
        second_time = history[1].received_at
        between = first_time + (second_time - first_time) / 2

        mid = queries.latest_observed(SUBJECT, PROP, between)
        assert mid.occurrence.value_json == "60.1"
        assert mid.evidence_quality.intervening_failed_attempts == 0
        assert mid.evidence_quality.later_snapshots_without_property == 0

        after = queries.latest_observed(SUBJECT, PROP, at(23, 0, 0))
        assert after.occurrence.value_json == "60.4"
        assert after.staleness_seconds > 0

    def test_answers_are_historically_closed(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportError

        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        cutoff = at(23, 0, 0)
        before_more = queries.latest_observed(SUBJECT, PROP, cutoff)

        # ingest a later failure + a later changed snapshot, re-project
        transport.script["/printer/objects/query"] = TransportError(
            "timeout", "x")
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = fixture_response(
            "moonraker_printer_objects_changed.json")
        runner.run("printer-1")
        projector.project("printer-1")

        # ...but the later evidence has LATER wall times than the cutoff?
        # The connector clock continues past 19:00:xx, still before 23:00 —
        # so recompute at a cutoff BEFORE the new evidence instead:
        history = queries.history(SUBJECT, PROP)
        closed_cutoff = history[0].received_at  # exactly the first occurrence
        answer_now = queries.latest_observed(SUBJECT, PROP, closed_cutoff)
        assert answer_now.occurrence.occurrence_id == (
            before_more.occurrence.occurrence_id)
        assert answer_now.evidence_quality.intervening_failed_attempts == 0
        assert answer_now.evidence_quality.latest_applicable_attempt_outcome == (
            "observations_projected")

    def test_intervening_failure_surfaces_at_later_cutoff(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportError

        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = TransportError(
            "timeout", "x")
        runner.run("printer-1")
        projector.project("printer-1")
        latest = queries.latest_observed(SUBJECT, PROP, at(23, 0, 0))
        assert latest.occurrence.value_json == "60.1"  # value NOT erased
        assert latest.evidence_quality.intervening_failed_attempts == 1
        assert latest.evidence_quality.latest_applicable_attempt_outcome == (
            "acquisition_failed")


class TestLaterCoverageDistinction:
    def test_later_snapshot_without_property(self, tmp_path):
        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = response_bytes(
            (FIXTURES / "moonraker_objects_omitted.json").read_bytes())
        runner.run("printer-1")
        projector.project("printer-1")
        latest = queries.latest_observed(HEATER_SUBJECT, HEATER_PROP, at(23, 0, 0))
        assert latest.occurrence.value_json == "45.2"  # never deleted/nulled
        assert latest.evidence_quality.later_snapshots_without_property == 1
        assert latest.evidence_quality.later_empty_snapshots == 0

    def test_later_empty_snapshot(self, tmp_path):
        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        empty = json.dumps({"result": {"eventtime": 9000.5, "status": {}}}).encode()
        transport.script["/printer/objects/query"] = response_bytes(empty)
        runner.run("printer-1")
        projector.project("printer-1")
        latest = queries.latest_observed(SUBJECT, PROP, at(23, 0, 0))
        assert latest.evidence_quality.later_empty_snapshots == 1
        assert latest.evidence_quality.later_snapshots_without_property == 0


class TestOtherQueries:
    def test_change_history_and_freshness_and_segments(self, tmp_path):
        runner, _, transport, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = fixture_response(
            "moonraker_printer_objects_changed.json")
        runner.run("printer-1")
        projector.project("printer-1")

        changes = queries.change_history(SUBJECT, PROP)
        assert [c.change_class for c in changes] == ["first_seen", "changed"]

        fresh = queries.freshness("printer-1", at(23, 0, 0))
        assert len(fresh) == 13  # every distinct six-dimension key
        assert all(entry.staleness_seconds > 0 for entry in fresh)

        segments = queries.clock_segments("printer-1")
        assert len(segments) == 1 and segments[0].boundary_reason == "initial"

    def test_provenance_chain_resolves_into_evidence_store(self, tmp_path):
        runner, ds_store, _, _, projector, queries = build(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        latest = queries.latest_observed(SUBJECT, PROP, at(23, 0, 0))
        chain = queries.provenance(latest.occurrence.occurrence_id)
        # every link resolves against the immutable evidence store
        attempt = ds_store.get_attempt(chain.attempt_id)
        assert attempt.raw_record_id == chain.raw_record_id
        payload = ds_store.get_payload(chain.payload_checksum)
        parsed = json.loads(payload.decode())
        assert parsed["result"]["status"]["extruder"]["temperature"] == 60.1
        extraction = ds_store.get_extraction(chain.raw_record_id)
        assert any(o.observation_id == chain.observation_id
                   for o in extraction.manifest_view().observations)


class TestRebuild:
    def _two_sources(self, tmp_path):
        runner, ds_store, transport, temporal, projector, queries = build(tmp_path)
        runner.catalog.register(make_source().model_copy(
            update={"source_id": "printer-2", "display_name": "printer-2"}))
        runner.run("printer-1")
        runner.run("printer-2")
        projector.project("printer-1")
        projector.project("printer-2")
        return runner, temporal, projector

    def test_per_source_rebuild_preserves_other_source(self, tmp_path):
        _, temporal, projector = self._two_sources(tmp_path)
        before = temporal.ordered_logical_dump()
        other_before = [r for r in before["temporal_occurrences"]
                        if r[2] == "printer-2"]
        report = projector.rebuild("printer-1")
        assert report.halted is None
        after = temporal.ordered_logical_dump()
        other_after = [r for r in after["temporal_occurrences"]
                       if r[2] == "printer-2"]
        assert other_after == other_before
        assert after == before  # deterministic replay reproduces everything

    def test_full_rebuild_matches_fresh_projection(self, tmp_path):
        _, temporal, projector = self._two_sources(tmp_path)
        before = temporal.ordered_logical_dump()
        projector.rebuild_all(["printer-1", "printer-2"])
        assert projector.store.ordered_logical_dump() == before
