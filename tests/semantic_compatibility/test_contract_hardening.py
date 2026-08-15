"""ES-001 Group 8 adversarial result-contract invariants (FC2/FC3/HD1)."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from backend.model_kernel import SemanticDimensionResult, VariableSemanticsResult
from backend.semantic_compatibility import (
    CandidateSemanticCompatibility, VariableSemanticCompatibilityResult,
    derive_semantic_findings)
from backend.source_interpretation import (
    DimensionInterpretationResolution, PropertyInterpretationResult)
from tests.model_state.helpers import V1
from tests.semantic_compatibility.test_facade import queries

AS_OF = datetime(2026, 8, 7, 20, 30, tzinfo=UTC)


def successful(tmp_path):
    facade, _ = queries(tmp_path)
    return facade.variable_semantic_compatibility(V1, as_of=AS_OF)


def candidate_fields(candidate, **updates):
    fields = dict(
        value_candidate=candidate.value_candidate,
        interpretation=candidate.interpretation,
        quantity_kind_compatibility=candidate.quantity_kind_compatibility,
        quantity_kind_not_evaluated_reason=(
            candidate.quantity_kind_not_evaluated_reason),
        observation_role_compatibility=candidate.observation_role_compatibility,
        observation_role_not_evaluated_reason=(
            candidate.observation_role_not_evaluated_reason),
        unit_identity_compatibility=candidate.unit_identity_compatibility,
        unit_identity_not_evaluated_reason=(
            candidate.unit_identity_not_evaluated_reason),
        interpreted_unit_source_lexeme_relation=(
            candidate.interpreted_unit_source_lexeme_relation),
        interpreted_unit_source_lexeme_not_evaluated_reason=(
            candidate.interpreted_unit_source_lexeme_not_evaluated_reason))
    fields.update(updates)
    return fields


def rebuilt_candidate(candidate, **updates):
    fields = candidate_fields(candidate, **updates)
    draft = CandidateSemanticCompatibility.model_construct(
        **fields, semantic_findings=())
    return CandidateSemanticCompatibility(
        **fields, semantic_findings=derive_semantic_findings(draft))


def test_outer_as_of_must_equal_carried_value_result(tmp_path):
    result = successful(tmp_path)
    with pytest.raises(ValidationError):
        VariableSemanticCompatibilityResult(
            **{**result.model_dump(), "as_of": result.as_of + timedelta(days=1)})


def test_unit_exact_cannot_coexist_with_noninterpreted_unit(tmp_path):
    candidate = successful(tmp_path).candidates[0]
    interpretation = PropertyInterpretationResult(
        **{**candidate.interpretation.model_dump(),
           "unit": DimensionInterpretationResolution(
               dimension="unit", status="not_declared")})
    with pytest.raises(ValidationError):
        rebuilt_candidate(candidate, interpretation=interpretation)


def test_compatible_candidate_cannot_coexist_with_absent_model_meaning(tmp_path):
    result = successful(tmp_path)
    absent = VariableSemanticsResult(
        anchor_id=V1,
        quantity_kind=SemanticDimensionResult(
            dimension="quantity_kind", status="not_declared"),
        observation_role=SemanticDimensionResult(
            dimension="observation_role", status="not_declared"),
        revision=result.semantics_result.revision)
    with pytest.raises(ValidationError):
        VariableSemanticCompatibilityResult(
            **{**result.model_dump(), "semantics_result": absent,
               "candidates": result.candidates})


@pytest.mark.parametrize("field,verdict,reason", [
    ("quantity_kind", "token_identical", "model_meaning_not_declared"),
    ("observation_role", "token_differs", "source_interpretation_conflicted"),
    ("unit_identity", "unit_identity_exact", "model_unit_not_declared"),
    ("interpreted_unit_source_lexeme", "lexeme_identical", "source_unit_absent"),
])
def test_verdict_and_reason_are_mutually_exclusive(
        tmp_path, field, verdict, reason):
    candidate = successful(tmp_path).candidates[0]
    with pytest.raises(ValidationError):
        CandidateSemanticCompatibility(**candidate_fields(candidate, **{
            f"{field}_compatibility" if field != "interpreted_unit_source_lexeme"
            else "interpreted_unit_source_lexeme_relation": verdict,
            f"{field}_not_evaluated_reason": reason,
            "semantic_findings": candidate.semantic_findings}))


def test_findings_are_exact_sorted_unique_and_validator_derived(tmp_path):
    candidate = successful(tmp_path).candidates[0]
    for findings in (
        (), candidate.semantic_findings[::-1],
        candidate.semantic_findings + (candidate.semantic_findings[0],),
        tuple(sorted((*candidate.semantic_findings, "observation_absent"))),
    ):
        with pytest.raises(ValidationError):
            CandidateSemanticCompatibility(
                **candidate_fields(candidate), semantic_findings=findings)


def test_mismatch_mandatorily_coemits_no_conversion_finding(tmp_path):
    candidate = successful(tmp_path).candidates[0]
    fields = candidate_fields(
        candidate, unit_identity_compatibility="unit_identity_mismatch")
    draft = CandidateSemanticCompatibility.model_construct(
        **fields, semantic_findings=())
    expected = derive_semantic_findings(draft)
    assert "unit_identity_mismatch" in expected
    assert "unit_identities_differ_conversion_not_attempted" in expected
    with pytest.raises(ValidationError):
        CandidateSemanticCompatibility(
            **fields, semantic_findings=tuple(item for item in expected if item
                != "unit_identities_differ_conversion_not_attempted"))


def test_candidate_reordering_and_substitution_are_rejected(tmp_path):
    result = successful(tmp_path)
    candidate = result.candidates[0]
    foreign_value = candidate.value_candidate.model_copy(update={
        "value_presence": "explicit_null"})
    forged = candidate.model_copy(update={"value_candidate": foreign_value})
    with pytest.raises(ValidationError):
        VariableSemanticCompatibilityResult(
            **{**result.model_dump(), "candidates": (forged,)})


def test_outer_rejects_interpretation_revision_mismatch(tmp_path):
    result = successful(tmp_path)
    revision = result.interpretation_revision.model_copy(update={
        "revision_id": "irv_" + "f" * 64})
    with pytest.raises(ValidationError):
        VariableSemanticCompatibilityResult(
            **{**result.model_dump(), "interpretation_revision": revision})
