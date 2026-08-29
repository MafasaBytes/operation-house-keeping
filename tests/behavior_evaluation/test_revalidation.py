"""Public BH result boundary rejects forged nested and derived content."""

import pytest
from pydantic import ValidationError

from backend.behavior_evaluation import BehaviorEvaluationResult
from backend.semantic_compatibility import VariableSemanticCompatibilityResult
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


def _replace_mapping_values(value, replacements):
    if isinstance(value, dict):
        rebuilt = {}
        for key, item in value.items():
            replacement_key = ((key, item)
                               if isinstance(item, (str, int, float, bool, type(None)))
                               else None)
            rebuilt[key] = (replacements[replacement_key]
                            if replacement_key in replacements else
                            _replace_mapping_values(item, replacements))
        return rebuilt
    if isinstance(value, list):
        return [_replace_mapping_values(item, replacements) for item in value]
    if isinstance(value, tuple):
        return tuple(_replace_mapping_values(item, replacements)
                     for item in value)
    return value


def test_carried_model_facts_must_equal_authoritative_behavior_material(tmp_path):
    result = evaluate(tmp_path)
    lower_payload = _replace_mapping_values(
        result.participant_semantic_results[0].model_dump(mode="python"),
        {
            ("value_shape", "number"): "string",
            ("value_shape_compatibility", "satisfies_value_shape"):
                "does_not_satisfy_value_shape",
            ("value_shape_finding", "shape_matches"): "shape_differs",
        })
    forged_lower = VariableSemanticCompatibilityResult.model_validate(
        lower_payload)
    payload = result.model_dump(mode="python")
    payload["participant_semantic_results"] = (
        forged_lower.model_dump(mode="python"),
        payload["participant_semantic_results"][1],
    )
    with pytest.raises(ValidationError, match="carried participant model facts"):
        BehaviorEvaluationResult.model_validate(payload)
