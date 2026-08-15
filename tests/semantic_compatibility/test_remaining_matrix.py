"""Remaining feasible ES-001 Group 8 gates and lifecycle mappings."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.identity_binding.contracts import (
    AppliesScope, DeclaredBoundary, UnknownBoundary)
from backend.model_kernel import (
    QuantityKindDeclaration, QuantityKindReference,
    VariableSemanticDeclaration, build_record)
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.source_interpretation import (
    InterpretationResolver, InterpretationRetraction, InterpretationStore,
    ObservationRoleInterpretation, QuantityKindInterpretation,
    SourcePropertyInterpretation, UnitInterpretation,
    build_record as spi_build)
from tests.model_state.helpers import (
    AS_OF, PROP_TARGET, PROP_TEMP, SUBJECT, V1, entity_declaration, hour,
    prop_assertion, standard_bindings, var_declaration)
from tests.observation_compatibility.helpers import (
    NO_UNIT, compatibility, craft_occurrence, model_with, observed_stack)
from tests.semantic_compatibility.test_facade import (
    EVIDENCE, INTERP_AUTH, MODEL_AUTH, QUANTITY, ROLE, T0, UNIT,
    interpretation_resolver, model_semantics)


def facade_with(tmp_path, model, resolver, *, temporal=None,
                binding_records=None):
    values, _, _ = compatibility(
        tmp_path, model_store=model, temporal=temporal,
        binding_records=binding_records)
    return SemanticCompatibilityQueries(values, resolver)


def qrecord(*, body=None, applies=None, parents=(), note=""):
    return spi_build(
        SourcePropertyInterpretation, subject=SUBJECT, property=PROP_TEMP,
        interpretation=body or QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=QUANTITY),
        applies=applies or hour(), supersedes=parents, recorded_at=T0,
        authority=INTERP_AUTH, note=note)


def resolver_records(tmp_path, *quantity_records):
    # Quantity is supplied by the scenario; role/unit remain positive so each
    # quantity reason is independently visible through the facade.
    base = interpretation_resolver(tmp_path)
    loaded = base.loaded
    role_unit = [record for record in loaded.interpretations.values()
                 if record.interpretation.dimension != "quantity_kind"]
    ledger = InterpretationStore(tmp_path / "scenario" / "demo-printer")
    for record in (*quantity_records, *role_unit):
        ledger.append(record)
    return InterpretationResolver(ledger.load())


def result_for(tmp_path, resolver, *, model=None, temporal=None,
               binding_records=None):
    model = model or model_semantics(model_with(tmp_path))
    return facade_with(
        tmp_path, model, resolver, temporal=temporal,
        binding_records=binding_records).variable_semantic_compatibility(
            V1, as_of=AS_OF).candidates[0]


def test_observed_unattached_still_carries_interpretation_but_no_verdict(tmp_path):
    v2 = "var_" + "4" * 32
    bindings = (entity_declaration(), var_declaration(V1), var_declaration(v2),
                prop_assertion(target=V1),
                prop_assertion(target=v2, note="competing"))
    item = result_for(
        tmp_path, interpretation_resolver(tmp_path), binding_records=bindings)
    assert item.value_candidate.state_candidate.bound is not None
    assert item.value_candidate.state_candidate.attachment != "attached"
    assert item.interpretation is not None
    assert item.quantity_kind_not_evaluated_reason == "observation_not_attached"
    assert item.observation_role_not_evaluated_reason == "observation_not_attached"
    assert item.unit_identity_not_evaluated_reason == "observation_not_attached"
    assert "observation_not_attached" in item.semantic_findings
    assert "declared_semantics_compatible" not in item.semantic_findings


def test_conflicted_model_meaning_is_a_distinct_gate(tmp_path):
    model = model_semantics(model_with(tmp_path))
    alternate = QuantityKindReference(
        system_id="project_local", system_edition="ohk-quantities-1",
        code="pressure")
    model.append(build_record(
        VariableSemanticDeclaration, variable_anchor_id=V1,
        declaration=QuantityKindDeclaration(
            dimension="quantity_kind", quantity_kind=alternate),
        evidence=EVIDENCE, supersedes=(), recorded_at=T0,
        authority=MODEL_AUTH, note="competing"))
    item = result_for(tmp_path, interpretation_resolver(tmp_path), model=model)
    assert item.quantity_kind_not_evaluated_reason == "model_meaning_conflicted"
    assert item.observation_role_compatibility == "token_identical"
    assert "model_meaning_conflicted" in item.semantic_findings


def test_conflicted_specification_is_a_distinct_unit_gate(tmp_path):
    model = model_with(tmp_path, specifications=(
        ("number", False, None), ("string", False, NO_UNIT)))
    model_semantics(model)
    item = result_for(tmp_path, interpretation_resolver(tmp_path), model=model)
    assert item.unit_identity_not_evaluated_reason == (
        "model_specification_conflicted")
    assert item.quantity_kind_compatibility == "token_identical"
    assert "model_specification_conflicted" in item.semantic_findings


@pytest.mark.parametrize("scenario,expected", [
    ("outside", "source_interpretation_inapplicable"),
    ("unknown", "source_interpretation_applicability_unknown"),
    ("ambiguous", "source_interpretation_ambiguous"),
    ("conflicted", "source_interpretation_conflicted"),
    ("retracted", "source_interpretation_retracted"),
    ("inactive", "source_interpretation_inactive"),
])
def test_each_reachable_nonpositive_interpretation_status_maps_distinctly(
        tmp_path, scenario, expected):
    other = QuantityKindInterpretation(
        dimension="quantity_kind", quantity_kind=QuantityKindReference(
            system_id="project_local", system_edition="ohk-quantities-1",
            code="pressure"))
    if scenario == "outside":
        records = (qrecord(applies=AppliesScope(
            axis="ingestion_received_at",
            start_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 6, tzinfo=UTC)),
            end_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 6, 1, tzinfo=UTC)),
            interval_semantics="half_open")),)
    elif scenario == "unknown":
        records = (qrecord(applies=AppliesScope(
            axis="ingestion_received_at",
            start_boundary=UnknownBoundary(kind="unknown"),
            end_boundary=UnknownBoundary(kind="unknown"),
            interval_semantics="half_open")),)
    elif scenario == "ambiguous":
        records = (qrecord(), qrecord(body=other, applies=AppliesScope(
            axis="ingestion_received_at",
            start_boundary=UnknownBoundary(kind="unknown"),
            end_boundary=UnknownBoundary(kind="unknown"),
            interval_semantics="half_open")))
    elif scenario == "conflicted":
        records = (qrecord(note="one"), qrecord(body=other, note="two"))
    elif scenario == "retracted":
        root = qrecord()
        records = (root, spi_build(
            InterpretationRetraction, retracts=root.record_id,
            recorded_at=T0, authority=INTERP_AUTH, note=""))
    else:
        root = qrecord(note="root")
        successor = qrecord(parents=(root.record_id,), note="successor")
        records = (root, successor, spi_build(
            InterpretationRetraction, retracts=successor.record_id,
            recorded_at=T0, authority=INTERP_AUTH, note=""))
    item = result_for(tmp_path, resolver_records(tmp_path, *records))
    assert item.quantity_kind_compatibility == "not_evaluated"
    assert item.quantity_kind_not_evaluated_reason == expected
    assert expected in item.semantic_findings


@pytest.mark.parametrize("lexeme", [
    "9" * 5000,
    "[" * 20000 + "]" * 20000,
])
def test_huge_and_deep_evidence_are_gated_without_crashing(tmp_path, lexeme):
    temporal = observed_stack(tmp_path / "evidence")
    json_type = "array" if lexeme.startswith("[") else "number"
    craft_occurrence(temporal, value_json=lexeme, json_type=json_type)
    item = result_for(
        tmp_path, interpretation_resolver(tmp_path), temporal=temporal)
    assert item.value_candidate.evidence_consistency == "value_not_representable"
    assert item.quantity_kind_not_evaluated_reason == "evidence_not_assessable"
    assert item.observation_role_not_evaluated_reason == "evidence_not_assessable"
    assert item.unit_identity_not_evaluated_reason == "evidence_not_assessable"
    assert "evidence_inconsistent" in item.semantic_findings


def test_two_candidates_remain_index_parallel_and_semantically_independent(
        tmp_path):
    ledger = InterpretationStore(tmp_path / "two" / "demo-printer")
    target_role = ROLE.model_copy(update={"code": "commanded_target"})
    for prop, role in ((PROP_TEMP, ROLE), (PROP_TARGET, target_role)):
        for body in (
            QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=QUANTITY),
            ObservationRoleInterpretation(
                dimension="observation_role", observation_role=role),
            UnitInterpretation(dimension="unit", unit=UNIT),
        ):
            ledger.append(spi_build(
                SourcePropertyInterpretation, subject=SUBJECT, property=prop,
                interpretation=body, applies=hour(), supersedes=(),
                recorded_at=T0, authority=INTERP_AUTH, note=""))
    bindings = (*standard_bindings(), prop_assertion(
        prop=PROP_TARGET, note="target candidate"))
    model = model_semantics(model_with(tmp_path))
    facade = facade_with(
        tmp_path, model, InterpretationResolver(ledger.load()),
        binding_records=bindings)
    result = facade.variable_semantic_compatibility(V1, as_of=AS_OF)
    assert len(result.candidates) == 2
    assert tuple(item.value_candidate for item in result.candidates) == (
        result.value_compatibility.candidates)
    by_property = {item.value_candidate.state_candidate.property: item
                   for item in result.candidates}
    assert by_property[PROP_TEMP].observation_role_compatibility == (
        "token_identical")
    assert by_property[PROP_TARGET].observation_role_compatibility == (
        "token_differs")
    assert {item.quantity_kind_compatibility for item in result.candidates} == {
        "token_identical"}


def test_lower_layer_typed_errors_propagate_unchanged(tmp_path, monkeypatch):
    from backend.model_kernel import ModelQueryError

    model = model_semantics(model_with(tmp_path))
    facade = facade_with(tmp_path, model, interpretation_resolver(tmp_path))
    original = ModelQueryError("MODEL_ANCHOR_ID_INVALID", "synthetic lower error")

    def fail(*args, **kwargs):
        raise original

    monkeypatch.setattr(
        facade.compatibility, "variable_value_compatibility", fail)
    with pytest.raises(ModelQueryError) as error:
        facade.variable_semantic_compatibility(V1, as_of=AS_OF)
    assert error.value is original


def test_semantic_tokens_never_enter_the_carried_source_candidate_subtree(
        tmp_path):
    item = result_for(tmp_path, interpretation_resolver(tmp_path))
    source_tree = item.model_dump(mode="json")["value_candidate"]

    def leaves(value):
        if isinstance(value, dict):
            for child in value.values():
                yield from leaves(child)
        elif isinstance(value, list):
            for child in value:
                yield from leaves(child)
        else:
            yield value

    source_values = set(value for value in leaves(source_tree)
                        if isinstance(value, str))
    assert "degree_celsius" not in source_values
    assert "ohk-units-1" not in source_values
    assert "project_local" not in source_values
    assert "measured_actual" not in source_values
    assert item.interpretation.unit.interpretation.unit.code == "degree_celsius"
