"""Exact BH-001 Slice C public vocabulary and facade boundary."""

import inspect
from typing import get_args

import pytest

import backend.behavior_evaluation as behavior


EXPECTED_EXPORTS = [
    "BehaviorEvaluationError",
    "BehaviorEvaluationConfigurationError",
    "BehaviorEvaluationInputError",
    "NumericParityBreachError",
    "BehaviorParticipantSource",
    "BehaviorEvaluationExecution",
    "BehaviorComputedRelation",
    "BehaviorParticipantAdmission",
    "BehaviorParticipantModelAdmission",
    "BehaviorParticipantObservationAvailability",
    "BehaviorParticipantAttachmentAdmission",
    "BehaviorParticipantSemanticAdmission",
    "BehaviorParticipantUnitAdmission",
    "BehaviorParticipantLockAdmission",
    "BehaviorParticipantNumericAdmission",
    "BehaviorAcquisitionCohortAdmission",
    "BehaviorEvaluationRefusalReason",
    "BehaviorEvaluationRefusal",
    "BehaviorEvaluationParticipantResult",
    "BehaviorEvaluationResult",
    "BehaviorEvaluationQueries",
]

REFUSALS = (
    "behavior_not_registered", "behavior_not_declared", "behavior_inactive",
    "behavior_conflicted", "participant_model_not_registered",
    "observation_absent", "observation_not_attached", "binding_not_positive",
    "evidence_not_assessable", "numeric_specification_not_available",
    "numeric_specification_conflicted", "model_quantity_kind_not_available",
    "model_observation_role_not_available", "model_unit_not_available",
    "source_semantics_not_admitted", "quantity_kind_lock_mismatch",
    "observation_role_lock_mismatch", "unit_lock_mismatch",
    "numeric_value_absent", "numeric_value_shape_mismatch",
    "numeric_value_out_of_bounds", "acquisition_cohort_mismatch",
)


def test_exact_public_exports_and_cn_error_identity():
    from backend.constraint_evaluation import NumericParityBreachError

    assert behavior.__all__ == EXPECTED_EXPORTS
    assert behavior.NumericParityBreachError is NumericParityBreachError
    assert not hasattr(behavior, "parse_observed_decimal")
    assert not hasattr(behavior, "CanonicalObservedDecimal")


def test_exact_status_literals_and_refusal_order():
    assert get_args(behavior.BehaviorEvaluationExecution) == (
        "not_executed", "executed")
    assert get_args(behavior.BehaviorComputedRelation) == ("equal", "different")
    assert get_args(behavior.BehaviorParticipantAdmission) == (
        "admitted", "not_admitted")
    assert get_args(behavior.BehaviorParticipantModelAdmission) == (
        "admitted", "not_admitted")
    assert get_args(behavior.BehaviorParticipantObservationAvailability) == (
        "observed", "none_before_cutoff", "not_evaluated")
    assert get_args(behavior.BehaviorParticipantAttachmentAdmission) == (
        "not_evaluated", "attached", "not_attached")
    assert get_args(behavior.BehaviorParticipantSemanticAdmission) == (
        "not_evaluated", "admitted", "not_admitted")
    assert get_args(behavior.BehaviorParticipantUnitAdmission) == (
        "not_evaluated", "exact", "mismatch")
    assert get_args(behavior.BehaviorParticipantLockAdmission) == (
        "not_evaluated", "matched", "mismatched")
    assert get_args(behavior.BehaviorParticipantNumericAdmission) == (
        "not_evaluated", "admitted", "out_of_bounds")
    assert get_args(behavior.BehaviorAcquisitionCohortAdmission) == (
        "not_evaluated", "same_acquisition_cohort",
        "different_acquisition_cohort")
    assert get_args(behavior.BehaviorEvaluationRefusalReason) == REFUSALS


def test_exact_contract_fields_and_signature():
    assert tuple(behavior.BehaviorParticipantSource.model_fields) == (
        "variable_anchor_id", "entity_anchor_id", "source")
    assert tuple(behavior.BehaviorEvaluationRefusal.model_fields) == (
        "reason", "participant_index")
    assert tuple(behavior.BehaviorEvaluationParticipantResult.model_fields) == (
        "participant_index", "variable_anchor_id", "source_index",
        "semantic_result_index", "candidate_index", "model_admission",
        "observation_availability", "attachment_admission",
        "semantic_admission", "unit_admission", "lock_admission",
        "numeric_admission", "admission", "refusal_reasons",
        "canonical_decimal")
    assert tuple(behavior.BehaviorEvaluationResult.model_fields) == (
        "behavior", "behavior_anchor_id", "context", "as_of",
        "ruleset_version", "participant_sources",
        "participant_semantic_results", "participants", "cohort_admission",
        "execution", "not_executed_reasons", "computed_relation")
    assert str(inspect.signature(
        behavior.BehaviorEvaluationQueries.behavior_evaluation)) == (
        "(self, behavior_anchor_id, *, context, as_of, participants) -> "
        "'BehaviorEvaluationResult'")


def test_public_error_tree_and_codes():
    assert issubclass(
        behavior.BehaviorEvaluationConfigurationError,
        behavior.BehaviorEvaluationError)
    assert issubclass(
        behavior.BehaviorEvaluationInputError, behavior.BehaviorEvaluationError)
    with pytest.raises(behavior.BehaviorEvaluationConfigurationError) as error:
        behavior.BehaviorEvaluationQueries(object())
    assert error.value.error_code == "BEHAVIOR_EVALUATION_CONFIGURATION_INVALID"


@pytest.mark.parametrize("bad", [True, 1, None, (), object()])
def test_facade_rejects_structurally_invalid_requests(tmp_path, bad):
    from tests.behavior_evaluation.helpers import semantic_queries

    facade = behavior.BehaviorEvaluationQueries(semantic_queries(tmp_path))
    with pytest.raises(behavior.BehaviorEvaluationInputError) as error:
        facade.behavior_evaluation(
            bad, context={}, as_of=True, participants=())
    assert error.value.error_code == "BEHAVIOR_EVALUATION_INPUT_INVALID"


@pytest.mark.parametrize("case", [
    "malformed_context", "naive_cutoff", "zero_participants",
    "one_participant", "three_participants", "duplicate_variable",
    "forged_source", "extra_participant_field",
])
def test_each_request_structure_guard_is_independently_reachable(
        tmp_path, monkeypatch, case):
    from datetime import datetime

    from backend.model_state import SourceSelector
    from tests.behavior_evaluation.helpers import (
        AS_DESIGNED, AS_OF, BEHAVIOR_A, participant_sources,
        semantic_queries,
    )

    semantic = semantic_queries(tmp_path)
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("invalid request must not access lower evidence")

    monkeypatch.setattr(
        semantic, "variable_semantic_compatibility", forbidden)
    context = AS_DESIGNED
    as_of = AS_OF
    participants = participant_sources()
    if case == "malformed_context":
        context = {"kind": "unknown_context"}
    elif case == "naive_cutoff":
        as_of = datetime(2026, 8, 7, 20, 30)
    elif case == "zero_participants":
        participants = ()
    elif case == "one_participant":
        participants = participants[:1]
    elif case == "three_participants":
        participants = (*participants, participants[0].model_copy(update={
            "variable_anchor_id": "var_" + "8" * 32}))
    elif case == "duplicate_variable":
        participants = (participants[0], participants[0])
    elif case == "forged_source":
        participants = (
            participants[0].model_construct(
                variable_anchor_id=participants[0].variable_anchor_id,
                entity_anchor_id=participants[0].entity_anchor_id,
                source=SourceSelector.model_construct(
                    subject=participants[0].source.subject, property=None)),
            participants[1],
        )
    else:
        participants = (
            {**participants[0].model_dump(mode="python"),
             "implicit_discovery": True},
            participants[1],
        )
    with pytest.raises(behavior.BehaviorEvaluationInputError) as error:
        behavior.BehaviorEvaluationQueries(semantic).behavior_evaluation(
            BEHAVIOR_A, context=context, as_of=as_of,
            participants=participants)
    assert error.value.error_code == "BEHAVIOR_EVALUATION_INPUT_INVALID"
    assert calls == []
