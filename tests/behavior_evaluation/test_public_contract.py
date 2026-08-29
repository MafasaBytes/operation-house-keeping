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
