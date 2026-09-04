"""EA-001 Slice A: bounded one-transaction temporal selection material."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    Ds004OperationalEvidenceScope,
    UnavailableTimeMarker,
)
from backend.temporal_state.contracts import (
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalAttemptEvent,
    TemporalOccurrence,
    TemporalQueryError,
    TemporalSelectionInventoryToken,
    TemporalSelectionMaterial,
    temporal_selection_digest,
)
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import (
    fixture_response,
    happy_script,
    make_runner,
)


def _scope(**updates):
    values = {
        "source_id": "printer-1", "adapter_id": "moonraker",
        "endpoint_id": "printer_objects_query", "item_key": "printer_objects",
        "subject_identifier": "extruder",
        "extraction_route": "api:moonraker:v1",
        "json_pointer": "/result/status/extruder/temperature",
    }
    values.update(updates)
    return Ds004OperationalEvidenceScope(**values)


def _world(tmp_path):
    runner, raw, transport = make_runner(tmp_path / "raw", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db", evidence_root=raw.base_dir)
    projector = TemporalProjector(raw, temporal)
    return runner, raw, transport, temporal, projector, TemporalQueries(temporal)


def test_exact_temporal_contract_fields():
    assert tuple(TemporalSelectionInventoryToken.model_fields) == (
        "schema_version", "projector_version", "scope", "horizon_started_at",
        "as_of", "occurrence_membership_sha256",
        "attempt_coverage_membership_sha256", "clock_opening_membership_sha256",
    )
    assert tuple(TemporalSelectionMaterial.model_fields) == (
        "schema_version", "projector_version", "scope", "horizon_started_at",
        "as_of", "selected_occurrence_index",
        "selected_occurrence_is_pre_horizon_seed", "occurrence_membership",
        "attempt_coverage_membership", "clock_segment_openings",
        "transaction_membership_sha256",
    )


def test_separate_memberships_latest_and_full_order_are_deterministic(tmp_path):
    runner, _, transport, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    transport.script["/printer/objects/query"] = fixture_response(
        "moonraker_printer_objects_changed.json")
    runner.run("printer-1")
    projector.project("printer-1")
    history = queries.history(
        SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                         subject_identifier="extruder"),
        SourcePropertyRef(extraction_route="api:moonraker:v1",
                          item_key="printer_objects",
                          json_pointer="/result/status/extruder/temperature"))
    horizon = history[0].received_at
    as_of = history[-1].received_at
    material = queries.selection_material(
        _scope(), horizon_started_at=horizon, as_of=as_of)
    token = queries.selection_inventory_token(
        _scope(), horizon_started_at=horizon, as_of=as_of)

    assert [o.value_json for o in material.occurrence_membership] == ["60.1", "60.4"]
    assert material.occurrence_membership[material.selected_occurrence_index].value_json == "60.4"
    assert material.selected_occurrence_is_pre_horizon_seed is False
    assert all(horizon <= a.effective_wall_time <= as_of
               for a in material.attempt_coverage_membership)
    assert token.occurrence_membership_sha256.startswith("sha256:")
    assert material.transaction_membership_sha256.startswith("sha256:")
    assert queries.selection_material(
        _scope(), horizon_started_at=horizon, as_of=as_of) == material


def test_selected_pre_horizon_seed_is_one_and_not_coverage(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    subject = SourceSubjectRef(
        source_id="printer-1", adapter_id="moonraker",
        subject_identifier="extruder")
    prop = SourcePropertyRef(
        extraction_route="api:moonraker:v1", item_key="printer_objects",
        json_pointer="/result/status/extruder/temperature")
    occurrence = queries.history(subject, prop)[0]
    horizon = occurrence.received_at + timedelta(hours=1)
    material = queries.selection_material(
        _scope(), horizon_started_at=horizon,
        as_of=horizon + timedelta(hours=1))
    assert material.selected_occurrence_is_pre_horizon_seed is True
    assert len(material.occurrence_membership) == 1
    assert material.occurrence_membership[0] == occurrence
    assert material.selected_occurrence_index == 0
    assert material.attempt_coverage_membership == ()


def test_no_observation_at_or_before_cutoff_is_exact(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    early = datetime(2020, 1, 1, tzinfo=UTC)
    material = queries.selection_material(
        _scope(), horizon_started_at=early - timedelta(hours=1), as_of=early)
    assert material.selected_occurrence_index is None
    assert material.selected_occurrence_is_pre_horizon_seed is False
    assert material.occurrence_membership == ()
    assert material.attempt_coverage_membership == ()


def test_no_response_failure_uses_finished_at_coverage_axis(tmp_path):
    from backend.data_sources.connectors.http_api import TransportError

    runner, _, transport, _, projector, queries = _world(tmp_path)
    transport.script["/printer/objects/query"] = TransportError("timeout", "x")
    runner.run("printer-1")
    projector.project("printer-1")
    attempt = next(a for a in queries.attempt_coverage("printer-1")
                   if a.endpoint_id == "printer_objects_query")
    material = queries.selection_material(
        _scope(), horizon_started_at=attempt.finished_at,
        as_of=attempt.finished_at)
    [covered] = material.attempt_coverage_membership
    assert covered.outcome == "acquisition_failed"
    assert covered.received_at is None
    assert covered.effective_wall_time == covered.finished_at
    assert covered.effective_time_basis == "finished_at_no_response"


def test_naive_and_reversed_horizons_reject_before_reader(tmp_path, monkeypatch):
    _, _, _, temporal, _, queries = _world(tmp_path)
    touched = False
    original = temporal.reader

    def observed_reader():
        nonlocal touched
        touched = True
        return original()

    monkeypatch.setattr(temporal, "reader", observed_reader)
    with pytest.raises(TemporalQueryError):
        queries.selection_material(
            _scope(), horizon_started_at=datetime(2026, 1, 1),
            as_of=datetime(2026, 1, 2, tzinfo=UTC))
    with pytest.raises(TemporalQueryError):
        queries.selection_material(
            _scope(), horizon_started_at=datetime(2026, 1, 2, tzinfo=UTC),
            as_of=datetime(2026, 1, 1, tzinfo=UTC))
    with pytest.raises(TemporalQueryError):
        queries.selection_material(
            _scope(), horizon_started_at="not-a-datetime",
            as_of=datetime(2026, 1, 2, tzinfo=UTC))
    assert touched is False


def test_prehorizon_seed_cannot_overflow_occurrence_bound(
    tmp_path, monkeypatch,
):
    import backend.temporal_state.queries as implementation

    runner, _, transport, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    transport.script["/printer/objects/query"] = fixture_response(
        "moonraker_printer_objects_changed.json")
    runner.run("printer-1")
    projector.project("printer-1")
    history = queries.history(
        SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                         subject_identifier="extruder"),
        SourcePropertyRef(extraction_route="api:moonraker:v1",
                          item_key="printer_objects",
                          json_pointer="/result/status/extruder/temperature"))
    monkeypatch.setattr(implementation, "MAX_SELECTION_OCCURRENCES", 0)
    with pytest.raises(TemporalQueryError) as exc:
        queries.selection_material(
            _scope(),
            horizon_started_at=history[-1].received_at + timedelta(seconds=1),
            as_of=history[-1].received_at + timedelta(seconds=2))
    assert exc.value.error_code == "TEMPORAL_SELECTION_LIMIT_EXCEEDED"


def test_scope_is_exact_and_view_does_not_merge_endpoints(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    horizon = datetime(2026, 8, 7, 19, 0, tzinfo=UTC)
    as_of = datetime(2026, 8, 7, 21, 0, tzinfo=UTC)
    material = queries.selection_material(
        _scope(endpoint_id="server_info"),
        horizon_started_at=horizon, as_of=as_of)
    assert material.attempt_coverage_membership == ()
    assert material.occurrence_membership == ()


def test_hostile_nested_temporal_material_revalidates():
    forged = TemporalSelectionMaterial.model_construct(
        schema_version="1", projector_version="1", scope=_scope(),
        horizon_started_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 2, tzinfo=UTC),
        selected_occurrence_index=True,
        selected_occurrence_is_pre_horizon_seed=False,
        occurrence_membership=(), attempt_coverage_membership=(),
        clock_segment_openings=(), transaction_membership_sha256="sha256:" + "0" * 64)
    with pytest.raises(ValidationError):
        TemporalSelectionMaterial.model_validate(
            forged.model_dump(mode="python", warnings=False))


def _attempt(index: int, when: datetime) -> TemporalAttemptEvent:
    return TemporalAttemptEvent(
        attempt_id=f"{index:032x}", source_id="printer-1",
        adapter_id="moonraker", endpoint_id="printer_objects_query",
        item_key="printer_objects", sweep_position=index,
        ingestion_run_id="run-bounds", attempt_started_at=when,
        received_at=None, finished_at=when, effective_wall_time=when,
        effective_time_basis="finished_at_no_response",
        outcome="acquisition_failed", raw_record_id=None,
        payload_checksum=None, observation_count=0,
        failure_or_quarantine_code="ACQUIRE_TIMEOUT",
        source_warning_count=0, projector_version="1.0.0")


def _insert_attempts(store: TemporalStore, rows):
    with store.writer() as conn:
        with store.attempt_txn(conn):
            for row in rows:
                store.insert_attempt_event(conn, row)


def test_lifetime_over_4096_succeeds_when_horizon_is_bounded(tmp_path):
    store = TemporalStore(tmp_path / "temporal.db",
                          evidence_root=tmp_path / "evidence")
    old = datetime(2020, 1, 1, tzinfo=UTC)
    horizon = datetime(2026, 1, 1, tzinfo=UTC)
    rows = [_attempt(i, old + timedelta(seconds=i)) for i in range(4_097)]
    rows.extend(_attempt(5_000 + i, horizon + timedelta(seconds=i))
                for i in range(2))
    _insert_attempts(store, rows)
    material = TemporalQueries(store).selection_material(
        _scope(), horizon_started_at=horizon,
        as_of=horizon + timedelta(seconds=5))
    assert len(material.attempt_coverage_membership) == 2


def test_more_than_4096_attempts_inside_horizon_refuses_without_truncation(
    tmp_path,
):
    store = TemporalStore(tmp_path / "temporal.db",
                          evidence_root=tmp_path / "evidence")
    horizon = datetime(2026, 1, 1, tzinfo=UTC)
    _insert_attempts(store, (
        _attempt(i, horizon + timedelta(microseconds=i)) for i in range(4_097)))
    with pytest.raises(TemporalQueryError) as exc:
        TemporalQueries(store).selection_material(
            _scope(), horizon_started_at=horizon,
            as_of=horizon + timedelta(seconds=1))
    assert exc.value.error_code == "TEMPORAL_SELECTION_LIMIT_EXCEEDED"


def test_equal_receipt_time_uses_complete_attempt_order_key(tmp_path):
    store = TemporalStore(tmp_path / "temporal.db",
                          evidence_root=tmp_path / "evidence")
    received = datetime(2026, 1, 2, tzinfo=UTC)
    subject = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                               subject_identifier="extruder")
    prop = SourcePropertyRef(extraction_route="api:moonraker:v1",
                             item_key="printer_objects",
                             json_pointer="/result/status/extruder/temperature")
    events = []
    occurrences = []
    for index, value in ((1, "1"), (2, "2")):
        started = received - timedelta(seconds=3 - index)
        event = TemporalAttemptEvent(
            attempt_id=f"{index:032x}", source_id="printer-1",
            adapter_id="moonraker", endpoint_id="printer_objects_query",
            item_key="printer_objects", sweep_position=index,
            ingestion_run_id="run-tie", attempt_started_at=started,
            received_at=received, finished_at=received,
            effective_wall_time=received, effective_time_basis="received_at",
            outcome="observations_projected", raw_record_id=f"{index + 10:032x}",
            payload_checksum="sha256:" + f"{index:064x}", observation_count=1,
            failure_or_quarantine_code=None, source_warning_count=0,
            projector_version="1.0.0")
        events.append(event)
        occurrences.append(TemporalOccurrence(
            occurrence_id=f"{index + 20:032x}", attempt_id=event.attempt_id,
            subject=subject, property=prop, observation_id=f"{index + 30:032x}",
            raw_record_id=event.raw_record_id,
            payload_checksum=event.payload_checksum,
            attempt_started_at=started, ingestion_run_id="run-tie",
            sweep_position=index, received_at=received, finished_at=received,
            source_time=UnavailableTimeMarker(kind="unavailable", reason="none"),
            clock_segment_id=None, value_json=value, json_type="number",
            declared_unit=None, change_class="first_seen",
            previous_occurrence_id=None, quality_flags=[]))
    with store.writer() as conn:
        with store.attempt_txn(conn):
            for event, occurrence in zip(events, occurrences, strict=True):
                store.insert_attempt_event(conn, event)
                store.insert_occurrence(conn, occurrence)
    material = TemporalQueries(store).selection_material(
        _scope(), horizon_started_at=received - timedelta(days=1), as_of=received)
    assert material.occurrence_membership[
        material.selected_occurrence_index].value_json == "2"


def test_occurrence_membership_cannot_claim_no_selection(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    material = queries.selection_material(
        _scope(), horizon_started_at=datetime(2026, 8, 7, 19, 0, tzinfo=UTC),
        as_of=datetime(2026, 8, 7, 21, 0, tzinfo=UTC))
    payload = material.model_dump(
        mode="python", exclude={"transaction_membership_sha256"})
    payload["selected_occurrence_index"] = None
    payload["selected_occurrence_is_pre_horizon_seed"] = False
    payload["transaction_membership_sha256"] = temporal_selection_digest(payload)
    with pytest.raises(ValidationError):
        TemporalSelectionMaterial.model_validate(payload)


def test_hostile_nested_attempt_instance_is_rebuilt(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    material = queries.selection_material(
        _scope(), horizon_started_at=datetime(2026, 8, 7, 19, 0, tzinfo=UTC),
        as_of=datetime(2026, 8, 7, 21, 0, tzinfo=UTC))
    bad = material.attempt_coverage_membership[0].model_copy(
        update={"observation_count": -1})
    payload = material.model_dump(
        mode="python", exclude={"transaction_membership_sha256"})
    payload["attempt_coverage_membership"] = (bad,)
    payload["transaction_membership_sha256"] = temporal_selection_digest(payload)
    with pytest.raises(ValidationError):
        TemporalSelectionMaterial.model_validate(payload)


def test_in_horizon_occurrence_attempt_substitution_is_rejected(tmp_path):
    runner, _, _, _, projector, queries = _world(tmp_path)
    runner.run("printer-1")
    projector.project("printer-1")
    material = queries.selection_material(
        _scope(), horizon_started_at=datetime(2026, 8, 7, 19, 0, tzinfo=UTC),
        as_of=datetime(2026, 8, 7, 21, 0, tzinfo=UTC))
    payload = material.model_dump(
        mode="python", exclude={"transaction_membership_sha256"})
    payload["occurrence_membership"][0]["raw_record_id"] = "0" * 32
    payload["transaction_membership_sha256"] = temporal_selection_digest(payload)
    with pytest.raises(ValidationError):
        TemporalSelectionMaterial.model_validate(payload)
