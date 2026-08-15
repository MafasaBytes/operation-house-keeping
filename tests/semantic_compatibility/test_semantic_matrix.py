"""ES-001 Group 8 dimensional, clause, and evidence-separation matrix."""

import inspect
import json
from datetime import UTC, datetime

import pytest

from backend.model_kernel import (
    ObservationRoleReference, QuantityKindReference, UnitReference)
from backend.semantic_compatibility import SemanticCompatibilityQueries
from tests.model_state.helpers import BEFORE_RECEIPT, PROP_TEMP, SUBJECT, V1
from tests.observation_compatibility.helpers import (
    NO_UNIT, compatibility, craft_occurrence, model_with, observed_stack,
    )
from tests.semantic_compatibility.test_facade import (
    interpretation_resolver, model_semantics, queries)

AS_OF = datetime(2026, 8, 7, 20, 30, tzinfo=UTC)


def candidate(tmp_path, **kwargs):
    facade, _ = queries(tmp_path, **kwargs)
    return facade.variable_semantic_compatibility(V1, as_of=AS_OF).candidates[0]


def composed(tmp_path, *, specifications, temporal=None):
    model = model_semantics(model_with(
        tmp_path, specifications=specifications))
    values, _, _ = compatibility(
        tmp_path, model_store=model, temporal=temporal)
    return SemanticCompatibilityQueries(
        values, interpretation_resolver(tmp_path))


def test_quantity_mismatch_does_not_suppress_role_or_unit(tmp_path):
    pressure = QuantityKindReference(
        system_id="project_local", system_edition="ohk-quantities-1",
        code="pressure")
    result = candidate(tmp_path, quantity=pressure)
    assert result.quantity_kind_compatibility == "token_differs"
    assert result.observation_role_compatibility == "token_identical"
    assert result.unit_identity_compatibility == "unit_identity_exact"
    assert "quantity_kind_mismatch" in result.semantic_findings
    assert "declared_semantics_compatible" not in result.semantic_findings


def test_role_mismatch_does_not_suppress_quantity_or_unit(tmp_path):
    target = ObservationRoleReference(
        system_id="project_local", system_edition="ohk-observation-roles-1",
        code="commanded_target")
    result = candidate(tmp_path, role=target)
    assert result.quantity_kind_compatibility == "token_identical"
    assert result.observation_role_compatibility == "token_differs"
    assert result.unit_identity_compatibility == "unit_identity_exact"
    assert "observation_role_mismatch" in result.semantic_findings
    assert "declared_semantics_compatible" not in result.semantic_findings


@pytest.mark.parametrize("member,replacement", [
    ("system_edition", "ohk-units-2"),
    ("code", "degree_fahrenheit"),
])
def test_unit_identity_is_sensitive_to_each_open_triple_member(
        tmp_path, member, replacement):
    original = UnitReference(system_id="project_local",
                             system_edition="ohk-units-1",
                             code="degree_celsius")
    changed = original.model_copy(update={member: replacement})
    result = candidate(tmp_path, unit=changed)
    assert result.unit_identity_compatibility == "unit_identity_mismatch"
    assert result.value_candidate.state_candidate.bound.observed.occurrence.value_json == (
        "60.1")
    serialized = result.model_dump_json()
    assert "140" not in serialized


def test_no_observation_has_no_interpretation_or_verdicts(tmp_path):
    facade, _ = queries(tmp_path)
    result = facade.variable_semantic_compatibility(V1, as_of=BEFORE_RECEIPT)
    [item] = result.candidates
    assert item.interpretation is None
    assert item.quantity_kind_compatibility == "not_evaluated"
    assert item.observation_role_compatibility == "not_evaluated"
    assert item.unit_identity_compatibility == "not_evaluated"
    assert item.semantic_findings == ("observation_absent",)


def test_each_missing_interpretation_dimension_has_specific_finding(tmp_path):
    result = candidate(tmp_path, interpreted=False)
    assert result.quantity_kind_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert result.observation_role_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert result.unit_identity_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert result.semantic_findings == ("source_interpretation_not_declared",)


def test_model_meaning_absence_precedes_source_absence_per_dimension(tmp_path):
    result = candidate(tmp_path, semantic=False, interpreted=False)
    assert result.quantity_kind_not_evaluated_reason == (
        "model_meaning_not_declared")
    assert result.observation_role_not_evaluated_reason == (
        "model_meaning_not_declared")
    assert result.unit_identity_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert "model_meaning_not_declared" in result.semantic_findings


def test_absent_source_unit_remains_null_and_confined_to_source_subtree(tmp_path):
    result = candidate(tmp_path)
    occurrence = result.value_candidate.state_candidate.bound.observed.occurrence
    assert occurrence.declared_unit is None
    assert result.value_candidate.source_unit_evidence == "absent"
    payload = result.model_dump(mode="json")
    state_payload = payload["value_candidate"]["state_candidate"]
    encoded_state = json.dumps(state_payload, sort_keys=True)
    assert '"declared_unit": null' in encoded_state
    # ``temperature`` itself legitimately occurs in the source-native JSON
    # pointer.  The identity-token editions/codes and role must not leak.
    for token in ("degree_celsius", "ohk-units-1", "project_local",
                  "measured_actual"):
        assert token not in encoded_state
    assert "source_unit_absent_but_interpreted" in result.semantic_findings


def test_public_api_has_no_conversion_or_target_unit_parameter():
    signature = inspect.signature(
        SemanticCompatibilityQueries.variable_semantic_compatibility)
    assert "target_unit" not in signature.parameters
    forbidden = {"converted_value", "normalized_value", "canonical_value",
                 "winner", "current_value", "usable", "effective_value"}
    from backend.semantic_compatibility import CandidateSemanticCompatibility
    assert forbidden.isdisjoint(CandidateSemanticCompatibility.model_fields)


def test_full_result_serialization_has_no_aggregate_or_selected_value(tmp_path):
    facade, _ = queries(tmp_path)
    result = facade.variable_semantic_compatibility(V1, as_of=AS_OF)
    text = result.model_dump_json()
    for needle in ("normalized", "converted", "canonical_value", "winner",
                   "current_value", "usable", "effective_value"):
        assert needle not in text


@pytest.mark.parametrize("specifications,reason", [
    ((), "model_specification_not_available"),
    (("number", False, NO_UNIT), "model_unit_not_declared"),
])
def test_specification_absence_and_declared_no_unit_are_distinct(
        tmp_path, specifications, reason):
    specs = specifications if specifications == () else (specifications,)
    facade = composed(tmp_path, specifications=specs)
    result = facade.variable_semantic_compatibility(V1, as_of=AS_OF).candidates[0]
    assert result.quantity_kind_compatibility == "token_identical"
    assert result.observation_role_compatibility == "token_identical"
    assert result.unit_identity_compatibility == "not_evaluated"
    assert result.unit_identity_not_evaluated_reason == reason
    assert reason in result.semantic_findings
    assert "declared_semantics_compatible" not in result.semantic_findings


def test_inconsistent_evidence_gates_all_semantic_verdicts(tmp_path):
    temporal = observed_stack(tmp_path / "evidence")
    crafted = craft_occurrence(
        temporal, value_json="NaN", json_type="number")
    facade = composed(tmp_path, specifications=(("number", False, None),),
                      temporal=temporal)
    result = facade.variable_semantic_compatibility(
        V1, as_of=crafted.received_at).candidates[0]
    assert result.value_candidate.evidence_consistency in (
        "value_not_representable", "value_json_malformed")
    assert result.quantity_kind_not_evaluated_reason == "evidence_not_assessable"
    assert result.observation_role_not_evaluated_reason == "evidence_not_assessable"
    assert result.unit_identity_not_evaluated_reason == "evidence_not_assessable"
    assert "evidence_inconsistent" in result.semantic_findings
    assert "declared_semantics_compatible" not in result.semantic_findings


def test_source_lexeme_interpretation_and_model_unit_remain_three_facts(tmp_path):
    temporal = observed_stack(tmp_path / "lexeme")
    crafted = craft_occurrence(
        temporal, value_json="60.4", json_type="number", declared_unit="degC")
    facade = composed(tmp_path, specifications=(("number", False, None),),
                      temporal=temporal)
    result = facade.variable_semantic_compatibility(
        V1, as_of=crafted.received_at).candidates[0]
    occurrence = result.value_candidate.state_candidate.bound.observed.occurrence
    assert occurrence.declared_unit == "degC"
    assert result.interpretation.unit.interpretation.unit.code == "degree_celsius"
    assert result.value_candidate.source_unit_evidence == "present"
    assert result.interpreted_unit_source_lexeme_relation == "lexeme_differs"
    assert "interpreted_unit_lexeme_differs_from_source" in result.semantic_findings
