"""Disposable accepted lower-result builders for EA-001 Slice C1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from backend.evidence_assurance import EvidenceAssuranceQueries
from backend.model_state import SourceSelector
from backend.observation_compatibility import VariableValueCompatibilityResult
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

from tests.evidence_assurance.test_selection import (
    AS_OF,
    HORIZON,
    _captured_world,
    _request as ea_request,
)
from tests.model_state.helpers import PROP_TEMP, SUBJECT, V1
from tests.observation_compatibility.helpers import (
    compatibility,
    entity_declaration,
    model_with,
    var_declaration,
)


@dataclass(frozen=True)
class AlignmentWorld:
    root: object
    source: object
    temporal: object
    consumer_queries: object
    selection: object
    compatibility: VariableValueCompatibilityResult


def build_world(tmp_path) -> AlignmentWorld:
    _, _, source, temporal = _captured_world(tmp_path / "evidence")
    selection = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(ea_request())
    consumer_queries, _, _ = compatibility(
        tmp_path / "consumer", temporal=temporal)
    consumer = consumer_queries.variable_value_compatibility(V1, as_of=AS_OF)
    snapshot = selection.snapshot
    assert snapshot is not None
    selected = snapshot.temporal_material.occurrence_membership[
        snapshot.selected.temporal_occurrence_index]
    assert consumer.candidates[0].state_candidate.bound.observed.occurrence == selected
    return AlignmentWorld(
        root=tmp_path, source=source, temporal=temporal,
        consumer_queries=consumer_queries, selection=selection,
        compatibility=consumer)


def alignment_api():
    from backend.evidence_alignment.contracts import (
        EvidenceAlignmentError,
        EvidenceAlignmentQueryError,
        EvidenceAlignmentQueryErrorCode,
        OperationalEvidenceAlignmentReason,
        OperationalEvidenceAlignmentRequest,
        OperationalEvidenceAlignmentResult,
        OperationalEvidenceAlignmentStatus,
    )
    from backend.evidence_alignment.derivation import (
        align_operational_evidence_with_value_compatibility,
    )
    return {
        "EvidenceAlignmentError": EvidenceAlignmentError,
        "EvidenceAlignmentQueryError": EvidenceAlignmentQueryError,
        "EvidenceAlignmentQueryErrorCode": EvidenceAlignmentQueryErrorCode,
        "OperationalEvidenceAlignmentReason": OperationalEvidenceAlignmentReason,
        "OperationalEvidenceAlignmentRequest": OperationalEvidenceAlignmentRequest,
        "OperationalEvidenceAlignmentResult": OperationalEvidenceAlignmentResult,
        "OperationalEvidenceAlignmentStatus": OperationalEvidenceAlignmentStatus,
        "align": align_operational_evidence_with_value_compatibility,
    }


def align(world: AlignmentWorld, *, selection=None, consumer=None, expected=None):
    api = alignment_api()
    request = api["OperationalEvidenceAlignmentRequest"](
        schema_version="1",
        selection=world.selection if selection is None else selection,
        compatibility=world.compatibility if consumer is None else consumer,
        expected_snapshot_fingerprint=expected,
    )
    return api["align"](request)


def selected_occurrence(selection):
    snapshot = selection.snapshot
    assert snapshot is not None
    return snapshot.temporal_material.occurrence_membership[
        snapshot.selected.temporal_occurrence_index]


def pre_horizon_pair(world: AlignmentWorld):
    occurrence = selected_occurrence(world.selection)
    start = occurrence.received_at + timedelta(minutes=1)
    end = start + timedelta(minutes=1)
    selection = EvidenceAssuranceQueries(
        source=world.source, temporal=world.temporal,
    ).select_operational_evidence(ea_request(start=start, end=end))
    consumer = world.consumer_queries.variable_value_compatibility(V1, as_of=end)
    return selection, consumer


def no_observation_selection(world: AlignmentWorld):
    early = HORIZON - timedelta(days=3650)
    return EvidenceAssuranceQueries(
        source=world.source, temporal=world.temporal,
    ).select_operational_evidence(
        ea_request(start=early - timedelta(hours=1), end=early))


def explicit_consumer(world: AlignmentWorld, *, subject=SUBJECT, prop=PROP_TEMP,
                      as_of=AS_OF):
    return world.consumer_queries.variable_value_compatibility(
        V1, as_of=as_of, source=SourceSelector(subject=subject, property=prop))


def differing_scope_consumer(world: AlignmentWorld, field: str):
    subject = SUBJECT.model_dump(mode="python")
    prop = PROP_TEMP.model_dump(mode="python")
    target = subject if field in subject else prop
    target[field] = "different"
    return explicit_consumer(
        world,
        subject=SourceSubjectRef.model_validate(subject),
        prop=SourcePropertyRef.model_validate(prop),
    )


def mutate_consumer_occurrence(
    consumer: VariableValueCompatibilityResult,
    updates: dict,
    *, candidate_updates: dict | None = None,
):
    payload = consumer.model_dump(mode="python", warnings=False)
    for candidate in (
        payload["state"]["candidates"][0],
        payload["candidates"][0]["state_candidate"],
    ):
        candidate["bound"]["observed"]["occurrence"].update(updates)
        if "received_at" in updates:
            observed = candidate["bound"]["observed"]
            observed["staleness_seconds"] = (
                observed["as_of"] - updates["received_at"]
            ).total_seconds()
    if candidate_updates:
        payload["candidates"][0].update(candidate_updates)
    return VariableValueCompatibilityResult.model_validate(payload)


def consumer_without_observation(consumer: VariableValueCompatibilityResult):
    payload = consumer.model_dump(mode="python", warnings=False)
    state_candidate = payload["state"]["candidates"][0]
    state_candidate["bound"] = None
    state_candidate["attachment"] = "not_evaluated"
    payload["state"]["observation_availability"] = "none_before_cutoff"
    compatibility_candidate = payload["candidates"][0]
    compatibility_candidate["state_candidate"] = state_candidate
    compatibility_candidate.update({
        "value_presence": "no_observation",
        "evidence_consistency": "not_evaluated",
        "observed_shape": None,
        "value_shape_compatibility": "not_evaluated",
        "value_shape_finding": None,
        "value_shape_not_evaluated_reason": "no_observation",
        "source_unit_evidence": "not_evaluated",
        "declared_unit_lexeme_relation": "not_evaluated",
        "unit_lexeme_not_evaluated_reason": "no_observation",
    })
    return VariableValueCompatibilityResult.model_validate(payload)


def duplicate_consumer(consumer: VariableValueCompatibilityResult):
    payload = consumer.model_dump(mode="python", warnings=False)
    state_candidate = payload["state"]["candidates"][0]
    compatibility_candidate = payload["candidates"][0]
    payload["state"]["candidates"] = [state_candidate, state_candidate]
    payload["state"]["declared_locator_count"] = 2
    payload["state"]["selection"] = "multiple"
    payload["candidates"] = [compatibility_candidate, compatibility_candidate]
    return VariableValueCompatibilityResult.model_validate(payload)


def alternate_model_consumer(world: AlignmentWorld, *, conflicted=False,
                             registered=True):
    specs = (("number", False, None),)
    if conflicted:
        from tests.observation_compatibility.helpers import NO_UNIT
        specs = (("number", False, None), ("string", False, NO_UNIT))
    variables = ((V1, "ent_" + "1" * 32),) if registered else ()
    store = model_with(
        world.root / ("conflicted" if conflicted else "unregistered"),
        specifications=specs if registered else (), variables=variables,
        name="model",
    )
    queries, _, _ = compatibility(
        world.root / ("conflicted-consumer" if conflicted else
                      "unregistered-consumer"),
        temporal=world.temporal, model_store=store,
    )
    return queries.variable_value_compatibility(V1, as_of=AS_OF)


def no_candidates_consumer(world: AlignmentWorld):
    queries, _, _ = compatibility(
        world.root / "no-candidates-consumer",
        temporal=world.temporal,
        binding_records=(entity_declaration(), var_declaration()),
    )
    return queries.variable_value_compatibility(V1, as_of=AS_OF)
