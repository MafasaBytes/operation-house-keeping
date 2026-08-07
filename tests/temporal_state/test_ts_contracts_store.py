"""TS-001 contract and store tests: order keys, non-null occurrence
timestamps, path guard, busy behavior, transactions, logical dumps."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.temporal_state.contracts import (
    AttemptOrderKey,
    ClockSegmentOpening,
    ProjectionCheckpoint,
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalAttemptEvent,
    TemporalConfigurationError,
    TemporalOccurrence,
    TemporalStoreBusyError,
)
from backend.temporal_state.store import (
    PROJECTOR_VERSION,
    SCHEMA_VERSION,
    TemporalStore,
)

T0 = datetime(2026, 8, 8, 9, 0, 0, tzinfo=UTC)
T1 = datetime(2026, 8, 8, 9, 0, 1, tzinfo=UTC)

SUBJECT = SourceSubjectRef(
    source_id="printer-1", adapter_id="moonraker", subject_identifier="extruder"
)
PROP = SourcePropertyRef(
    extraction_route="api:moonraker:v1", item_key="printer_objects",
    json_pointer="/result/status/extruder/temperature",
)


def make_attempt_event(attempt_id="a" * 32, **overrides) -> TemporalAttemptEvent:
    base = dict(
        attempt_id=attempt_id, source_id="printer-1", adapter_id="moonraker",
        endpoint_id="printer_objects_query", item_key="printer_objects",
        sweep_position=1, ingestion_run_id="run-printer-1-0001",
        attempt_started_at=T0, received_at=T1, finished_at=T1,
        effective_wall_time=T1, effective_time_basis="received_at",
        outcome="observations_projected",
        raw_record_id="b" * 32, payload_checksum="sha256:" + "cd" * 32,
        observation_count=11, failure_or_quarantine_code=None,
        source_warning_count=0, projector_version=PROJECTOR_VERSION,
    )
    base.update(overrides)
    return TemporalAttemptEvent(**base)


def make_occurrence(occurrence_id="c" * 32, attempt_id="a" * 32,
                    **overrides) -> TemporalOccurrence:
    base = dict(
        occurrence_id=occurrence_id, attempt_id=attempt_id,
        subject=SUBJECT, property=PROP,
        observation_id="d" * 32, raw_record_id="b" * 32,
        payload_checksum="sha256:" + "cd" * 32,
        attempt_started_at=T0, ingestion_run_id="run-printer-1-0001",
        sweep_position=1, received_at=T1, finished_at=T1,
        source_time={"kind": "monotonic", "value": "3721.845",
                     "unit": "seconds", "clock_id": "klipper_host_monotonic",
                     "origin": "unknown", "pointer": "/result/eventtime"},
        clock_segment_id="e" * 32,
        value_json="60.1", json_type="number", declared_unit=None,
        change_class="first_seen", previous_occurrence_id=None,
        quality_flags=["unit_not_declared"],
    )
    base.update(overrides)
    return TemporalOccurrence(**base)


class TestContracts:
    def test_order_key_tiebreaks_deterministically(self):
        a = AttemptOrderKey(attempt_started_at=T0, ingestion_run_id="run-1",
                            sweep_position=0, attempt_id="a" * 32)
        b = AttemptOrderKey(attempt_started_at=T0, ingestion_run_id="run-1",
                            sweep_position=1, attempt_id="a" * 32)
        c = AttemptOrderKey(attempt_started_at=T0, ingestion_run_id="run-2",
                            sweep_position=0, attempt_id="a" * 32)
        assert a.sort_tuple() < b.sort_tuple() < c.sort_tuple()
        later = AttemptOrderKey(attempt_started_at=T1, ingestion_run_id="run-1",
                                sweep_position=0, attempt_id="a" * 32)
        assert c.sort_tuple() < later.sort_tuple()

    def test_occurrence_received_at_is_required(self):
        with pytest.raises(ValidationError):
            make_occurrence(received_at=None)

    def test_zero_observation_snapshot_is_representable(self):
        event = make_attempt_event(observation_count=0)
        assert event.observation_count == 0

    def test_no_response_ledger_row(self):
        event = make_attempt_event(
            outcome="acquisition_failed", received_at=None,
            raw_record_id=None, payload_checksum=None, observation_count=0,
            failure_or_quarantine_code="ACQUIRE_TIMEOUT",
            effective_wall_time=T1, effective_time_basis="finished_at_no_response",
        )
        assert event.effective_time_basis == "finished_at_no_response"

    def test_segment_boundary_reasons_are_epistemic(self):
        opening = ClockSegmentOpening(
            segment_id="e" * 32, source_id="printer-1", adapter_id="moonraker",
            clock_id="klipper_host_monotonic",
            boundary_reason="monotonic_decrease_observed",
            opened_by_attempt_id="a" * 32, opened_at_effective_wall_time=T1,
        )
        assert opening.boundary_reason == "monotonic_decrease_observed"
        with pytest.raises(ValidationError):
            ClockSegmentOpening(
                segment_id="e" * 32, source_id="s", adapter_id="m",
                clock_id="c", boundary_reason="source_restarted",  # not a claim we make
                opened_by_attempt_id="a" * 32, opened_at_effective_wall_time=T1,
            )


class TestStorePathGuard:
    def test_rejects_paths_at_or_inside_evidence_root(self, tmp_path):
        evidence = tmp_path / "raw_store"
        evidence.mkdir()
        with pytest.raises(TemporalConfigurationError):
            TemporalStore(evidence, evidence_root=evidence)
        with pytest.raises(TemporalConfigurationError):
            TemporalStore(evidence / "temporal.db", evidence_root=evidence)
        with pytest.raises(TemporalConfigurationError):
            TemporalStore(evidence / "sub" / "t.db", evidence_root=evidence)
        # sibling and dot-dot-outside are fine
        TemporalStore(tmp_path / "temporal.db", evidence_root=evidence)
        TemporalStore(evidence / ".." / "elsewhere.db", evidence_root=evidence)


@pytest.fixture
def store(tmp_path):
    evidence = tmp_path / "raw_store"
    evidence.mkdir()
    return TemporalStore(tmp_path / "temporal.db", evidence_root=evidence)


class TestStoreTransactions:
    def test_attempt_txn_commits_and_is_write_once(self, store):
        event = make_attempt_event()
        with store.writer() as conn:
            with store.attempt_txn(conn):
                store.insert_attempt_event(conn, event)
            assert store.has_attempt(conn, event.attempt_id)

    def test_rollback_leaves_no_partial_rows(self, store):
        event = make_attempt_event()
        occurrence = make_occurrence(clock_segment_id=None)
        with store.writer() as conn:
            with pytest.raises(RuntimeError):
                with store.attempt_txn(conn):
                    store.insert_attempt_event(conn, event)
                    store.insert_occurrence(conn, occurrence)
                    raise RuntimeError("simulated crash")
            assert not store.has_attempt(conn, event.attempt_id)
            dump = store.ordered_logical_dump()
            assert dump["temporal_occurrences"] == []

    def test_foreign_key_enforced(self, store):
        orphan = make_occurrence(attempt_id="f" * 32)  # no such ledger row
        with store.writer() as conn:
            with pytest.raises(sqlite3.IntegrityError):
                with store.attempt_txn(conn):
                    store.insert_occurrence(conn, orphan)

    def test_write_contention_is_typed_busy(self, store):
        with store.writer() as conn_a:
            conn_a.execute("BEGIN IMMEDIATE")
            with store.writer() as conn_b:
                with pytest.raises(TemporalStoreBusyError):
                    with store.attempt_txn(conn_b):
                        pass
            conn_a.execute("ROLLBACK")

    def test_reader_concurrent_with_writer(self, store):
        event = make_attempt_event()
        with store.writer() as conn:
            with store.attempt_txn(conn):
                store.insert_attempt_event(conn, event)
        with store.reader() as read_conn:
            rows = read_conn.execute(
                "SELECT count(*) FROM temporal_attempts").fetchone()[0]
            assert rows == 1


class TestLogicalDump:
    def test_dump_ordered_and_round_trips(self, store, tmp_path):
        events = [make_attempt_event(attempt_id=c * 32,
                                     ingestion_run_id=f"run-{c}")
                  for c in ("b", "a")]
        with store.writer() as conn:
            for event in events:
                with store.attempt_txn(conn):
                    store.insert_attempt_event(conn, event)
        dump = store.ordered_logical_dump()
        ids = [row[0] for row in dump["temporal_attempts"]]
        assert ids == sorted(ids)
        assert "checkpoints" not in dump  # excluded from determinism claim

    def test_checkpoint_round_trip(self, store):
        checkpoint = ProjectionCheckpoint(
            source_id="printer-1",
            last_attempt_started_at=T0, last_ingestion_run_id="run-1",
            last_sweep_position=1, last_attempt_id="a" * 32,
            projector_version=PROJECTOR_VERSION, schema_version=SCHEMA_VERSION,
        )
        with store.writer() as conn:
            with store.attempt_txn(conn):
                store.upsert_checkpoint(conn, checkpoint)
            assert store.load_checkpoint(conn, "printer-1") == checkpoint

    def test_remove_database_files_exact_sidecars_only(self, store, tmp_path):
        with store.writer() as conn:
            with store.attempt_txn(conn):
                store.insert_attempt_event(conn, make_attempt_event())
        bystander = store.db_path.parent / "unrelated.txt"
        bystander.write_text("keep me")
        store.remove_database_files()
        for suffix in ("", "-wal", "-shm"):
            assert not Path(str(store.db_path) + suffix).exists()
        assert bystander.exists()
