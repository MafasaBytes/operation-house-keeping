"""VM-001 Task 0: temporal storage failures typed at the public read
boundary. Missing, corrupted, and unreadable storage surface as
TemporalStoreError("TEMPORAL_STORE_UNAVAILABLE") with a path-free message
and the original sqlite error chained — never a raw sqlite3 exception,
and never conflated with an empty (None/[]) answer from a healthy store."""

import os
import sqlite3
from datetime import UTC, datetime

import pytest

from backend.temporal_state.contracts import (
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalError,
    TemporalQueryError,
    TemporalStoreError,
)
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")
AS_OF = datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)


def build(tmp_path):
    store = TemporalStore(tmp_path / "temporal.db",
                          evidence_root=tmp_path / "evidence")
    return store, TemporalQueries(store)


READ_CALLS = [
    pytest.param(lambda q: q.latest_observed(SUBJECT, PROP, AS_OF),
                 id="latest_observed"),
    pytest.param(lambda q: q.history(SUBJECT, PROP), id="history"),
    pytest.param(lambda q: q.change_history(SUBJECT, PROP),
                 id="change_history"),
    pytest.param(lambda q: q.attempt_coverage("printer-1"),
                 id="attempt_coverage"),
    pytest.param(lambda q: q.freshness("printer-1", AS_OF), id="freshness"),
    pytest.param(lambda q: q.provenance("0" * 32), id="provenance"),
    pytest.param(lambda q: q.clock_segments("printer-1"),
                 id="clock_segments"),
]


def destroy_missing(store):
    store.db_path.unlink()
    for suffix in ("-wal", "-shm"):
        side = store.db_path.with_name(store.db_path.name + suffix)
        if side.exists():
            side.unlink()


def destroy_corrupt(store):
    store.db_path.write_bytes(b"this is not a database at all\x00\xff")


def destroy_unreadable(store):
    os.chmod(store.db_path, 0)


DESTROYERS = [
    pytest.param(destroy_missing, id="missing"),
    pytest.param(destroy_corrupt, id="corrupted"),
    pytest.param(destroy_unreadable, id="unreadable"),
]


class TestStorageFailuresAreTyped:
    @pytest.mark.parametrize("call", READ_CALLS)
    @pytest.mark.parametrize("destroy", DESTROYERS)
    def test_destroyed_store_is_typed_and_path_free(self, tmp_path, call,
                                                    destroy):
        store, queries = build(tmp_path)
        destroy(store)
        try:
            with pytest.raises(TemporalError) as excinfo:
                call(queries)
        finally:
            if store.db_path.exists():  # restore so tmp_path cleanup works
                os.chmod(store.db_path, 0o600)
        assert isinstance(excinfo.value, TemporalStoreError)
        assert excinfo.value.error_code == "TEMPORAL_STORE_UNAVAILABLE"
        assert str(tmp_path) not in str(excinfo.value)
        assert "sqlite" not in str(excinfo.value).lower()
        assert isinstance(excinfo.value.__cause__, sqlite3.Error)

    def test_healthy_empty_store_still_answers_absence(self, tmp_path):
        """Unavailability is never conflated with absence: a healthy empty
        store answers None/[] exactly as before."""
        _, queries = build(tmp_path)
        assert queries.latest_observed(SUBJECT, PROP, AS_OF) is None
        assert queries.history(SUBJECT, PROP) == []
        assert queries.provenance("0" * 32) is None

    def test_naive_cutoff_still_typed_before_store_access(self, tmp_path):
        store, queries = build(tmp_path)
        destroy_missing(store)
        with pytest.raises(TemporalQueryError) as excinfo:
            queries.latest_observed(SUBJECT, PROP,
                                    datetime(2026, 8, 7, 21, 0, 0))
        assert excinfo.value.error_code == "TEMPORAL_NAIVE_CUTOFF"


class TestQueryMisuseIsNotUnavailability:
    """Gate repair R1: malformed ARGUMENTS on a healthy store are query
    misuse — never storage unavailability. The distinction is the whole
    point of TEMPORAL_STORE_UNAVAILABLE."""

    @pytest.mark.parametrize("call", [
        pytest.param(lambda q: q.provenance({}), id="provenance_dict"),
        pytest.param(lambda q: q.provenance(["x"]), id="provenance_list"),
        pytest.param(lambda q: q.history(SUBJECT, PROP, limit={}),
                     id="history_dict_limit"),
        pytest.param(lambda q: q.freshness({}, AS_OF), id="freshness_dict"),
        pytest.param(lambda q: q.clock_segments({}), id="segments_dict"),
    ])
    def test_malformed_arguments_are_typed_query_misuse(self, tmp_path, call):
        _, queries = build(tmp_path)  # healthy, readable store
        with pytest.raises(TemporalQueryError) as excinfo:
            call(queries)
        assert excinfo.value.error_code == "TEMPORAL_QUERY_INVALID"
        assert str(tmp_path) not in str(excinfo.value)

    def test_destroyed_store_still_reports_unavailability(self, tmp_path):
        store, queries = build(tmp_path)
        destroy_missing(store)
        with pytest.raises(TemporalStoreError) as excinfo:
            queries.provenance("0" * 32)
        assert excinfo.value.error_code == "TEMPORAL_STORE_UNAVAILABLE"
