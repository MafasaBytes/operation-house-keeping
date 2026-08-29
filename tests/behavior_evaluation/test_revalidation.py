"""Public BH result boundary rejects forged nested and derived content."""

import pytest
from pydantic import ValidationError

from backend.behavior_evaluation import BehaviorEvaluationResult
from tests.behavior_evaluation.helpers import evaluate


@pytest.mark.parametrize("field,value", [
    ("execution", "not_executed"),
    ("computed_relation", "equal"),
    ("cohort_admission", "different_acquisition_cohort"),
    ("ruleset_version", "bh001.2"),
])
def test_outer_derived_fields_cannot_be_forged(tmp_path, field, value):
    result = evaluate(tmp_path)
    forged = result.model_copy(update={field: value})
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(forged)


def test_nested_model_copy_and_construct_forgeries_are_rebuilt(tmp_path):
    result = evaluate(tmp_path)
    forged_row = result.participants[0].model_copy(
        update={"participant_index": True, "canonical_decimal": "999"})
    forged = result.model_construct(
        **{**result.model_dump(mode="python"),
           "participants": (forged_row, result.participants[1])})
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(forged)


def test_reordered_membership_or_participants_is_rejected(tmp_path):
    result = evaluate(tmp_path)
    payload = result.model_dump(mode="python")
    payload["participant_sources"] = tuple(reversed(payload["participant_sources"]))
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


def test_implication_bearing_extra_field_is_rejected(tmp_path):
    payload = evaluate(tmp_path).model_dump(mode="python")
    payload["behavior_valid"] = True
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


def test_coherent_lower_content_mutation_boundary_is_explicit(tmp_path):
    """BH re-proves coherence, not raw-source authenticity.

    The lower contracts can accept a fully coherent occurrence-content change
    whose payload bytes are not carried. This executable limitation must stay
    visible rather than being mislabeled as checksum authentication.
    """
    result = evaluate(tmp_path)
    assert result.participant_semantic_results[0].candidates[0].value_candidate
