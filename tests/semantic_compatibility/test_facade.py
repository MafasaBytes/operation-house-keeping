"""ES-001 Group 8 semantic composition acceptance."""

from datetime import UTC, datetime

import pytest

from backend.identity_binding.contracts import AuthorityRef as IbAuthorityRef
from backend.model_kernel import (
    ObservationRoleDeclaration, ObservationRoleReference,
    OwnerDeclarationEvidence, QuantityKindDeclaration, QuantityKindReference,
    UnitReference, VariableSemanticDeclaration, build_record)
from backend.semantic_compatibility import (
    SemanticCompatibilityConfigurationError, SemanticCompatibilityQueries)
from backend.source_interpretation import (
    InterpretationResolver, InterpretationStore,
    ObservationRoleInterpretation, QuantityKindInterpretation,
    SourcePropertyInterpretation, UnitInterpretation,
    build_record as spi_build)
from tests.model_state.helpers import BEFORE_RECEIPT, PROP_TEMP, SUBJECT, V1, hour
from tests.observation_compatibility.helpers import compatibility, model_with

T0 = datetime(2026, 8, 13, 12, tzinfo=UTC)
MODEL_AUTH = __import__("backend.model_kernel", fromlist=["AuthorityRef"]).AuthorityRef(
    kind="test_fixture", agent="es001_semantic_fixture",
    method="manual_declaration")
INTERP_AUTH = IbAuthorityRef(kind="test_fixture",
                             agent="es001_semantic_fixture",
                             method="manual_declaration")
EVIDENCE = (OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic semantics"),)
QUANTITY = QuantityKindReference(system_id="project_local",
                                 system_edition="ohk-quantities-1",
                                 code="temperature")
ROLE = ObservationRoleReference(system_id="project_local",
                                system_edition="ohk-observation-roles-1",
                                code="measured_actual")
UNIT = UnitReference(system_id="project_local", system_edition="ohk-units-1",
                     code="degree_celsius")


def test_package_surface_exists():
    assert SemanticCompatibilityQueries is not None


def model_semantics(store):
    for declaration in (
        QuantityKindDeclaration(dimension="quantity_kind", quantity_kind=QUANTITY),
        ObservationRoleDeclaration(dimension="observation_role",
                                   observation_role=ROLE)):
        store.append(build_record(
            VariableSemanticDeclaration, variable_anchor_id=V1,
            declaration=declaration, evidence=EVIDENCE, supersedes=(),
            recorded_at=T0, authority=MODEL_AUTH, note=""))
    return store


def interpretation_resolver(tmp_path, *, quantity=QUANTITY, role=ROLE, unit=UNIT):
    store = InterpretationStore(tmp_path / "interpretations" / "demo-printer")
    bodies = (
        QuantityKindInterpretation(dimension="quantity_kind",
                                   quantity_kind=quantity),
        ObservationRoleInterpretation(dimension="observation_role",
                                      observation_role=role),
        UnitInterpretation(dimension="unit", unit=unit))
    for body in bodies:
        store.append(spi_build(
            SourcePropertyInterpretation, subject=SUBJECT, property=PROP_TEMP,
            interpretation=body, applies=hour(), supersedes=(), recorded_at=T0,
            authority=INTERP_AUTH, note=""))
    return InterpretationResolver(store.load())


def queries(tmp_path, *, interpreted=True, semantic=True, **interpretation_kw):
    model = model_with(tmp_path)
    if semantic:
        model_semantics(model)
    values, _, _ = compatibility(tmp_path, model_store=model)
    resolver = (interpretation_resolver(tmp_path, **interpretation_kw)
                if interpreted else InterpretationResolver(
                    InterpretationStore(tmp_path / "empty" / "demo-printer").load()))
    return SemanticCompatibilityQueries(values, resolver), values


def test_exact_three_dimensional_match_and_absent_source_unit(tmp_path):
    facade, values = queries(tmp_path)
    result = facade.variable_semantic_compatibility(V1, as_of=datetime(
        2026, 8, 7, 20, 30, tzinfo=UTC))
    [candidate] = result.candidates
    assert result.value_compatibility == values.variable_value_compatibility(
        V1, as_of=datetime(2026, 8, 7, 20, 30, tzinfo=UTC))
    assert candidate.quantity_kind_compatibility == "token_identical"
    assert candidate.observation_role_compatibility == "token_identical"
    assert candidate.unit_identity_compatibility == "unit_identity_exact"
    assert candidate.interpreted_unit_source_lexeme_relation == "not_evaluated"
    assert candidate.interpreted_unit_source_lexeme_not_evaluated_reason == (
        "source_unit_absent")
    assert candidate.semantic_findings == (
        "declared_semantics_compatible", "source_unit_absent_but_interpreted",
        "unit_identity_exact")
    occurrence = candidate.value_candidate.state_candidate.bound.observed.occurrence
    assert occurrence.declared_unit is None and occurrence.value_json == "60.1"


def test_each_mismatch_is_independent_and_conversion_is_never_inferred(tmp_path):
    other = UnitReference(system_id="project_local", system_edition="other",
                          code="degree_celsius")
    facade, _ = queries(tmp_path, unit=other)
    candidate = facade.variable_semantic_compatibility(
        V1, as_of=datetime(2026, 8, 7, 20, 30, tzinfo=UTC)).candidates[0]
    assert candidate.quantity_kind_compatibility == "token_identical"
    assert candidate.observation_role_compatibility == "token_identical"
    assert candidate.unit_identity_compatibility == "unit_identity_mismatch"
    assert "unit_identities_differ_conversion_not_attempted" in (
        candidate.semantic_findings)
    assert "declared_semantics_compatible" not in candidate.semantic_findings


def test_model_absence_precedes_interpretation_absence_and_no_observation_locks(
        tmp_path):
    facade, _ = queries(tmp_path, semantic=False, interpreted=False)
    present = facade.variable_semantic_compatibility(
        V1, as_of=datetime(2026, 8, 7, 20, 30, tzinfo=UTC)).candidates[0]
    assert present.quantity_kind_not_evaluated_reason == (
        "model_meaning_not_declared")
    absent = facade.variable_semantic_compatibility(
        V1, as_of=BEFORE_RECEIPT).candidates[0]
    assert absent.interpretation is None
    assert absent.quantity_kind_not_evaluated_reason == "no_observation"
    assert absent.semantic_findings == ("observation_absent",)


def test_constructor_refuses_wrong_injected_types():
    with pytest.raises(SemanticCompatibilityConfigurationError) as error:
        SemanticCompatibilityQueries(object(), object())
    assert error.value.error_code == "SEMANTIC_COMPATIBILITY_INPUT_INVALID"
