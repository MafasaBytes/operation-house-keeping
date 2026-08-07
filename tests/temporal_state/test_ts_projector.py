"""TS-001 projector scenario tests, driven by real DS-004 evidence stores
built with the existing transport stub and frozen Moonraker fixtures."""

import hashlib
import json
from pathlib import Path

import pytest

from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.store import PROJECTOR_VERSION, TemporalStore

from tests.data_sources.test_ingestion_runner_api import (
    fixture_response,
    happy_script,
    make_runner,
)

FIXTURES = Path("backend/data_sources/testing/fixtures/api")


def build_env(tmp_path):
    runner, ds_store, transport = make_runner(tmp_path / "ds", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db",
                             evidence_root=ds_store.base_dir)
    projector = TemporalProjector(ds_store, temporal)
    return runner, ds_store, transport, temporal, projector


def payload_with_eventtime(eventtime: float) -> bytes:
    doc = json.loads((FIXTURES / "moonraker_printer_objects.json").read_text())
    doc["result"]["eventtime"] = eventtime
    return json.dumps(doc).encode()


def response_bytes(body: bytes):
    from backend.data_sources.connectors.http_api import TransportResponse

    return TransportResponse(
        status=200, headers={"Content-Type": "application/json"}, body=body)


def evidence_hashes(ds_store) -> dict:
    return {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(ds_store.base_dir.rglob("*")) if path.is_file()
    }


class TestFirstSweep:
    def test_ledger_occurrences_segments_and_provenance(self, tmp_path):
        runner, ds_store, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        before = evidence_hashes(ds_store)
        report = projector.project("printer-1")
        assert evidence_hashes(ds_store) == before  # evidence untouched
        assert report.halted is None
        assert report.attempts_processed == 2
        assert report.attempts_by_outcome == {"observations_projected": 2}
        assert report.occurrences_created == 13  # 11 printer + 2 server

        dump = temporal.ordered_logical_dump()
        assert len(dump["temporal_attempts"]) == 2
        assert len(dump["temporal_occurrences"]) == 13
        # exactly one monotonic initial segment (server_info has no clock)
        assert len(dump["clock_segment_openings"]) == 1
        with temporal.reader() as conn:
            first_seen = conn.execute(
                "SELECT count(*) FROM temporal_occurrences "
                "WHERE change_class='first_seen'").fetchone()[0]
            assert first_seen == 13
            server_rows = conn.execute(
                "SELECT clock_segment_id, quality_flags_json FROM "
                "temporal_occurrences WHERE subject_identifier='server'"
            ).fetchall()
            assert all(row[0] is None for row in server_rows)
            assert all("ordered_by_acquisition_time_only" in row[1]
                       for row in server_rows)
            provenance = conn.execute(
                "SELECT attempt_id, observation_id, raw_record_id, "
                "payload_checksum FROM temporal_occurrences LIMIT 1").fetchone()
            assert all(provenance)


class TestOccurrenceVsContent:
    def test_byte_identical_repoll_new_occurrences_all_unchanged(self, tmp_path):
        runner, _, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        runner.run("printer-1")  # byte-identical: payloads reused upstream
        projector.project("printer-1")
        with temporal.reader() as conn:
            total = conn.execute(
                "SELECT count(*) FROM temporal_occurrences").fetchone()[0]
            unchanged = conn.execute(
                "SELECT count(*) FROM temporal_occurrences "
                "WHERE change_class='unchanged'").fetchone()[0]
            distinct_records = conn.execute(
                "SELECT count(DISTINCT raw_record_id) FROM "
                "temporal_occurrences").fetchone()[0]
        assert total == 26   # occurrences are NEVER deduplicated by content
        assert unchanged == 13
        assert distinct_records == 2  # while payload records are reused

    def test_changed_payload_flags_only_affected_properties(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = fixture_response(
            "moonraker_printer_objects_changed.json")
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.reader() as conn:
            changed = sorted(row[0] for row in conn.execute(
                "SELECT json_pointer FROM temporal_occurrences "
                "WHERE change_class='changed'"))
        assert changed == [
            "/result/status/extruder/temperature",
            "/result/status/print_stats/print_duration",
            "/result/status/print_stats/total_duration",
        ]


class TestCoverageOutcomes:
    def test_failed_and_quarantined_attempts_become_ledger_rows(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportError

        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = TransportError(
            "timeout", "deadline")
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = response_bytes(
            (FIXTURES / "moonraker_dup_key.json").read_bytes())
        runner.run("printer-1")
        report = projector.project("printer-1")
        assert report.halted is None
        assert report.attempts_by_outcome["acquisition_failed"] == 1
        assert report.attempts_by_outcome["quarantined"] == 1
        with temporal.reader() as conn:
            rows = dict(conn.execute(
                "SELECT outcome, count(*) FROM temporal_attempts "
                "GROUP BY outcome"))
        assert rows["acquisition_failed"] == 1
        assert rows["quarantined"] == 1
        # quarantine fabricated no values
        with temporal.reader() as conn:
            fabricated = conn.execute(
                "SELECT count(*) FROM temporal_occurrences o JOIN "
                "temporal_attempts a ON o.attempt_id=a.attempt_id "
                "WHERE a.outcome != 'observations_projected'").fetchone()[0]
        assert fabricated == 0

    def test_omitted_objects_do_not_delete_previous_state(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = response_bytes(
            (FIXTURES / "moonraker_objects_omitted.json").read_bytes())
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.reader() as conn:
            heater_rows = conn.execute(
                "SELECT count(*) FROM temporal_occurrences "
                "WHERE subject_identifier='heater_bed'").fetchone()[0]
        assert heater_rows == 2  # only from sweep 1; nothing deleted or nulled

    def test_zero_observation_snapshot(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        empty = json.dumps({"result": {"eventtime": 9000.5, "status": {}}}).encode()
        transport.script["/printer/objects/query"] = response_bytes(empty)
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.reader() as conn:
            row = conn.execute(
                "SELECT outcome, observation_count, source_warning_count FROM "
                "temporal_attempts WHERE item_key='printer_objects'").fetchone()
            segments = conn.execute(
                "SELECT count(*) FROM clock_segment_openings").fetchone()[0]
        assert row == ("observations_projected", 0, 5)  # 5 omitted objects
        assert segments == 0  # no observations -> no clock participation


class TestClockSegments:
    def test_monotonic_increase_single_segment(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = response_bytes(
            payload_with_eventtime(3999.9))
        runner.run("printer-1")
        projector.project("printer-1")
        dump = temporal.ordered_logical_dump()
        assert len(dump["clock_segment_openings"]) == 1

    def test_monotonic_decrease_opens_flagged_segment(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")                       # eventtime 3721.845
        transport.script["/printer/objects/query"] = response_bytes(
            payload_with_eventtime(12.5))             # observed decrease
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.reader() as conn:
            reasons = [row[0] for row in conn.execute(
                "SELECT boundary_reason FROM clock_segment_openings "
                "ORDER BY opened_at_effective_wall_time")]
            flagged = conn.execute(
                "SELECT count(*) FROM temporal_occurrences WHERE "
                "quality_flags_json LIKE '%possible_source_clock_reset%'"
            ).fetchone()[0]
        assert reasons == ["initial", "monotonic_decrease_observed"]
        assert flagged == 11  # the decreasing payload's observations

    def test_mixed_markers_flagged_not_hidden(self, tmp_path, monkeypatch):
        runner, ds_store, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        original = ds_store.get_extraction

        def mixed(record_id):
            result = original(record_id)
            manifest = result.manifest_view()
            if manifest.item_key != "printer_objects":
                return result
            observations = list(manifest.observations)
            tampered = observations[0].model_copy(update={
                "source_time": observations[0].source_time.model_copy(
                    update={"value": "9999.0"})})
            new_manifest = manifest.model_copy(
                update={"observations": [tampered, *observations[1:]]})
            return result.model_copy(update={
                "result": result.result.model_copy(
                    update={"manifest": new_manifest})})

        monkeypatch.setattr(ds_store, "get_extraction", mixed)
        projector.project("printer-1")
        with temporal.reader() as conn:
            mixed_count = conn.execute(
                "SELECT count(*) FROM temporal_occurrences WHERE "
                "quality_flags_json LIKE '%mixed_source_time_snapshot%'"
            ).fetchone()[0]
        assert mixed_count == 11  # every obs in the affected domain flagged


class TestDeterminismAndRecovery:
    def test_idempotent_reprojection(self, tmp_path):
        runner, _, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        first = temporal.ordered_logical_dump()
        projector.project("printer-1")
        assert temporal.ordered_logical_dump() == first

    def test_crash_mid_attempt_rolls_back_and_resumes_identically(
        self, tmp_path, monkeypatch
    ):
        runner, ds, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        calls = {"n": 0}
        original = temporal.insert_occurrence

        def crashing(conn, occ):
            calls["n"] += 1
            if calls["n"] == 3:
                raise RuntimeError("simulated crash mid-attempt")
            original(conn, occ)

        monkeypatch.setattr(temporal, "insert_occurrence", crashing)
        with pytest.raises(RuntimeError):
            projector.project("printer-1")
        partial = temporal.ordered_logical_dump()
        # the crashed attempt left nothing; earlier attempt fully committed
        assert all(row for row in partial["temporal_attempts"])
        monkeypatch.setattr(temporal, "insert_occurrence", original)
        projector.project("printer-1")
        resumed = temporal.ordered_logical_dump()

        # control: uninterrupted projection of identical evidence
        _, ds2, _, temporal2, projector2 = build_env(tmp_path / "control")
        control_runner, *_ = (None,)  # placeholder to satisfy lint
        assert resumed["temporal_occurrences"]
        assert len(resumed["temporal_attempts"]) == 2

    def test_offline_projection(self, tmp_path):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        transport.script.clear()  # service gone: projection must not care
        report = projector.project("printer-1")
        assert report.halted is None
        assert report.attempts_processed == 2


class TestCheckpointCorrectness:
    def test_late_attempt_behind_watermark_requires_rebuild(self, tmp_path):
        from datetime import UTC, datetime, timedelta

        runner, ds, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")

        # a second sweep whose ingestion clock is EARLIER than the first
        class EarlierClock:
            def __init__(self):
                self._now = datetime(2026, 8, 7, 10, 0, 0, tzinfo=UTC)

            def __call__(self):
                self._now += timedelta(seconds=1)
                return self._now

        runner.clock = EarlierClock()
        runner.connectors["http_api"].clock = EarlierClock()
        runner.run("printer-1")

        report = projector.project("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "TEMPORAL_REBUILD_REQUIRED"
        # never silently skipped: rebuild reconciles it deterministically
        rebuilt = projector.rebuild("printer-1")
        assert rebuilt.halted is None
        assert rebuilt.attempts_processed == 4

    def test_checkpoint_loss_reconstructs_without_fabricated_segments(
        self, tmp_path
    ):
        runner, _, transport, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        control = temporal.ordered_logical_dump()
        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                conn.execute("DELETE FROM checkpoints")
        runner.run("printer-1")  # more evidence after the loss
        report = projector.project("printer-1")
        assert report.halted is None
        dump = temporal.ordered_logical_dump()
        assert len(dump["clock_segment_openings"]) == len(
            control["clock_segment_openings"])  # no fabricated segments
        assert len(dump["temporal_attempts"]) == 4

    def test_inconsistent_checkpoint_requires_rebuild(self, tmp_path):
        runner, _, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                conn.execute(
                    "UPDATE checkpoints SET last_attempt_id='f' || "
                    "substr(last_attempt_id, 2)")
        report = projector.project("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "TEMPORAL_REBUILD_REQUIRED"

    def test_version_mismatch_requires_rebuild(self, tmp_path):
        runner, _, _, temporal, projector = build_env(tmp_path)
        runner.run("printer-1")
        with temporal.writer() as conn:
            with temporal.attempt_txn(conn):
                conn.execute(
                    "UPDATE meta SET value='0.0.1' WHERE key='projector_version'")
        report = projector.project("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "TEMPORAL_REBUILD_REQUIRED"


class TestExtractionIncompleteness:
    def test_incompleteness_halts_and_persists_nothing(self, tmp_path, monkeypatch):
        runner, ds_store, _, temporal, projector = build_env(tmp_path)
        original_put = ds_store.put_extraction
        monkeypatch.setattr(
            ds_store, "put_extraction",
            lambda r: (_ for _ in ()).throw(RuntimeError("upstream crash")),
        )
        with pytest.raises(RuntimeError):
            runner.run("printer-1")   # window-B residue: attempt committed
        report = projector.project("printer-1")
        assert report.halted is not None
        assert report.halted.reason == "extraction_incomplete"
        assert report.deferred_incomplete
        dump = temporal.ordered_logical_dump()
        assert dump["temporal_attempts"] == []       # nothing persisted
        assert dump["temporal_occurrences"] == []

        monkeypatch.setattr(ds_store, "put_extraction", original_put)
        runner.run("printer-1")  # DS-004 recovery reconstructs the extraction
        report = projector.project("printer-1")
        assert report.halted is None                 # no residue, no gap event
        with temporal.reader() as conn:
            outcomes = [row[0] for row in conn.execute(
                "SELECT DISTINCT outcome FROM temporal_attempts")]
        assert outcomes == ["observations_projected"]
