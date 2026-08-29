"""Every BH lifecycle and newly adjudicated ordinary refusal stays explicit."""

from datetime import UTC, datetime

from backend.model_kernel import ModelStore, UnitNotDeclared

from tests.behavior_evaluation.helpers import (
    AS_DESIGNED,
    E1,
    PROP_TARGET,
    PROP_TEMP,
    VAR_A,
    VAR_B,
    evaluate,
    interpretation_resolver,
    model_store,
    semantic_queries,
)
from tests.model_kernel.bh001_slice_a_helpers import (
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
)
from tests.model_kernel.builders import (
    observation_role,
    quantity_kind,
    specification,
    variable_registration,
)
from tests.model_state.helpers import (
    BEFORE_RECEIPT,
    entity_declaration,
    observed_stack,
    prop_assertion,
    var_declaration,
)
from tests.observation_compatibility.helpers import (
    craft_occurrence,
    observed_value,
)
from backend.source_interpretation import InterpretationResolver, InterpretationStore


def _reasons(result, participant=0):
    return result.participants[participant].refusal_reasons


def test_inactive_declaration_keeps_both_observation_paths(tmp_path):
    registration = behavior_registration(owners=("ent_" + "9" * 32,) * 2)
    declaration = behavior_declaration(registration)
    model = model_store(
        tmp_path, declaration_records=(declaration, behavior_withdrawal(declaration)))
    result = evaluate(tmp_path, model=model)
    assert result.behavior.conclusion == "inactive"
    assert result.not_executed_reasons[0].reason == "behavior_inactive"
    assert all(row.observation_availability == "observed"
               for row in result.participants)


def test_same_root_fork_conflict_keeps_both_observation_paths(tmp_path):
    registration = behavior_registration(owners=("ent_" + "9" * 32,) * 2)
    root = behavior_declaration(registration, note="root")
    left = behavior_declaration(
        registration, supersedes=(root.record_id,), note="left")
    right = behavior_declaration(
        registration, supersedes=(root.record_id,), note="right")
    model = model_store(
        tmp_path, declaration_records=(root, left, right))
    result = evaluate(tmp_path, model=model)
    assert result.behavior.conclusion == "conflicted"
    assert result.not_executed_reasons[0].reason == "behavior_conflicted"
    assert all(row.observation_availability == "observed"
               for row in result.participants)


def test_identical_independent_roots_corroborate_without_a_winner(tmp_path):
    registration = behavior_registration(owners=(E1, E1))
    first = behavior_declaration(registration, note="first authority claim")
    second = behavior_declaration(registration, note="second authority claim")
    result = evaluate(
        tmp_path,
        model=model_store(tmp_path, declaration_records=(first, second)))
    assert result.behavior.conclusion == "declared"
    assert result.behavior.agreement_findings == (
        "corroborating_healthy_roots",)
    assert len(result.behavior.roots) == 2
    assert result.execution == "executed"


def test_different_independent_engineering_bodies_conflict(tmp_path):
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock

    registration = behavior_registration(owners=(E1, E1))
    first = behavior_declaration(registration, note="first body")
    second = behavior_declaration(
        registration,
        locks=(
            semantic_lock(VAR_A, role="reported"),
            semantic_lock(VAR_B, role="reported"),
        ),
        note="different body",
    )
    result = evaluate(
        tmp_path,
        model=model_store(tmp_path, declaration_records=(first, second)))
    assert result.behavior.conclusion == "conflicted"
    assert "cross_root_effective_body_disagreement" in (
        result.behavior.agreement_findings)
    assert result.not_executed_reasons[0].reason == "behavior_conflicted"


def test_nonnumeric_specification_is_not_available_and_never_parsed(tmp_path):
    model = model_store(
        tmp_path, specification_overrides={VAR_A: {"value_shape": "string"}})
    result = evaluate(tmp_path, model=model)
    assert "numeric_specification_not_available" in _reasons(result)
    assert result.participants[0].numeric_admission == "not_evaluated"
    assert result.participants[0].canonical_decimal is None
    assert result.execution == "not_executed"


def test_missing_model_unit_has_exact_admission_mapping(tmp_path):
    model = model_store(tmp_path, specification_overrides={
        VAR_A: {"unit": UnitNotDeclared(kind="not_declared")}})
    result = evaluate(tmp_path, model=model)
    participant = result.participants[0]
    assert "model_unit_not_available" in participant.refusal_reasons
    assert participant.unit_admission == "not_evaluated"
    assert participant.numeric_admission == "not_evaluated"
    assert participant.canonical_decimal is None
    assert result.cohort_admission == "same_acquisition_cohort"


def test_explicit_null_precedes_shape_mismatch_even_when_nonnullable(tmp_path):
    temporal = observed_value(tmp_path, "null")
    result = evaluate(tmp_path, temporal=temporal)
    participant = result.participants[0]
    assert "numeric_value_absent" in participant.refusal_reasons
    assert "numeric_value_shape_mismatch" not in participant.refusal_reasons
    assert participant.numeric_admission == "not_evaluated"
    assert result.execution == "not_executed"


def test_present_string_is_numeric_shape_mismatch_and_not_different(tmp_path):
    temporal = observed_value(tmp_path, '"synthetic"')
    result = evaluate(tmp_path, temporal=temporal)
    participant = result.participants[0]
    assert "numeric_value_shape_mismatch" in participant.refusal_reasons
    assert "numeric_value_absent" not in participant.refusal_reasons
    assert participant.numeric_admission == "not_evaluated"
    assert result.computed_relation is None


def test_numeric_out_of_bounds_is_ordinary_refusal(tmp_path):
    temporal = observed_value(tmp_path, "1" * 257)
    result = evaluate(tmp_path, temporal=temporal)
    participant = result.participants[0]
    assert "numeric_value_out_of_bounds" in participant.refusal_reasons
    assert participant.numeric_admission == "out_of_bounds"
    assert result.execution == "not_executed"
    assert result.computed_relation is None


def test_observation_absence_is_disclosed_without_cohort_invention(tmp_path):
    result = evaluate(tmp_path, as_of=BEFORE_RECEIPT)
    assert all(row.observation_availability == "none_before_cutoff"
               for row in result.participants)
    assert all("observation_absent" in row.refusal_reasons
               for row in result.participants)
    assert result.cohort_admission == "not_evaluated"


def test_nonpositive_binding_and_attachment_are_separate_refusals(tmp_path):
    bindings = (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    semantic = semantic_queries(tmp_path, binding_records=bindings)
    result = evaluate(tmp_path, semantic=semantic)
    reasons = _reasons(result)
    assert "observation_not_attached" in reasons
    assert "binding_not_positive" in reasons
    assert result.participants[0].attachment_admission == "not_attached"


def test_positive_resolution_to_other_variable_is_attachment_only_refusal(
        tmp_path):
    bindings = (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_B, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    result = evaluate(
        tmp_path,
        semantic=semantic_queries(tmp_path, binding_records=bindings))
    reasons = _reasons(result)
    assert "observation_not_attached" in reasons
    assert "binding_not_positive" not in reasons


def test_divergent_binding_anchor_is_attachment_only_refusal(tmp_path):
    bindings = (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Divergent variable name"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_A, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    result = evaluate(
        tmp_path,
        semantic=semantic_queries(tmp_path, binding_records=bindings))
    reasons = _reasons(result)
    assert "observation_not_attached" in reasons
    assert "binding_not_positive" not in reasons


def test_inconsistent_occurrence_evidence_is_not_numeric_shape_refusal(
        tmp_path, monkeypatch):
    import backend.behavior_evaluation.derivation as derivation

    temporal = observed_stack(tmp_path)
    craft_occurrence(temporal, value_json="true", json_type="number")
    original = derivation.parse_observed_decimal
    calls = []

    def parser(value):
        calls.append(value)
        return original(value)

    monkeypatch.setattr(derivation, "parse_observed_decimal", parser)
    result = evaluate(tmp_path, temporal=temporal)
    reasons = _reasons(result)
    assert "evidence_not_assessable" in reasons
    assert "numeric_value_shape_mismatch" not in reasons
    assert result.participants[0].numeric_admission == "not_evaluated"
    assert calls == ["60.0", "60.0"]


def test_missing_and_conflicted_numeric_specifications_are_distinct(tmp_path):
    missing = evaluate(
        tmp_path / "missing",
        model=model_store(
            tmp_path / "missing", omit_specifications=(VAR_A,)))
    assert "numeric_specification_not_available" in _reasons(missing)

    conflicting = specification(VAR_A, note="independent competing root")
    conflict = evaluate(
        tmp_path / "conflict",
        model=model_store(
            tmp_path / "conflict", extra_records=(conflicting,)))
    assert "numeric_specification_conflicted" in _reasons(conflict)
    assert "numeric_specification_not_available" not in _reasons(conflict)


def test_missing_model_meaning_dimensions_are_independent(tmp_path):
    result = evaluate(
        tmp_path,
        model=model_store(tmp_path, omit_semantics=(
            (VAR_A, "quantity_kind"), (VAR_A, "observation_role"))))
    reasons = _reasons(result)
    assert "model_quantity_kind_not_available" in reasons
    assert "model_observation_role_not_available" in reasons
    assert result.participants[0].semantic_admission == "not_evaluated"


def test_conflicted_model_meaning_dimensions_are_independent(tmp_path):
    from tests.behavior_evaluation.helpers import _semantic_record
    from backend.model_kernel import (
        ObservationRoleDeclaration,
        QuantityKindDeclaration,
    )

    extras = (
        _semantic_record(VAR_A, QuantityKindDeclaration(
            dimension="quantity_kind",
            quantity_kind=quantity_kind(code="other_quantity"))),
        _semantic_record(VAR_A, ObservationRoleDeclaration(
            dimension="observation_role",
            observation_role=observation_role("other_role"))),
    )
    result = evaluate(
        tmp_path,
        model=model_store(tmp_path, extra_records=extras))
    reasons = _reasons(result)
    assert "model_quantity_kind_not_available" in reasons
    assert "model_observation_role_not_available" in reasons


def test_source_semantic_and_unit_mismatch_is_not_conversion(tmp_path):
    from backend.model_kernel import UnitReference

    other_unit = UnitReference(
        system_id="project_local", system_edition="ohk-units-1",
        code="synthetic_other_unit")
    resolver = interpretation_resolver(tmp_path, overrides={
        PROP_TEMP: {
            "quantity_kind": quantity_kind(code="synthetic_other_quantity"),
            "unit": other_unit,
        }})
    semantic = semantic_queries(tmp_path, interpretations=resolver)
    result = evaluate(tmp_path, semantic=semantic)
    participant = result.participants[0]
    assert "source_semantics_not_admitted" in participant.refusal_reasons
    assert participant.semantic_admission == "not_admitted"
    assert participant.unit_admission == "mismatch"


def test_absent_source_interpretation_is_an_ordinary_semantic_refusal(tmp_path):
    resolver = InterpretationResolver(
        InterpretationStore(tmp_path / "empty-interpretations").load())
    result = evaluate(
        tmp_path,
        semantic=semantic_queries(tmp_path, interpretations=resolver))
    assert "source_semantics_not_admitted" in _reasons(result)
    assert result.participants[0].semantic_admission == "not_admitted"


def test_conflicted_source_interpretation_is_an_ordinary_semantic_refusal(
        tmp_path):
    from backend.source_interpretation import QuantityKindInterpretation
    from tests.behavior_evaluation.helpers import _interpretation_record

    conflict = _interpretation_record(
        PROP_TEMP,
        QuantityKindInterpretation(
            dimension="quantity_kind",
            quantity_kind=quantity_kind(code="other_quantity")))
    resolver = interpretation_resolver(tmp_path, extra_records=(conflict,))
    result = evaluate(
        tmp_path,
        semantic=semantic_queries(tmp_path, interpretations=resolver))
    assert "source_semantics_not_admitted" in _reasons(result)
    assert result.participants[0].semantic_admission == "not_admitted"


def test_nullable_explicit_null_has_the_same_exact_precedence(tmp_path):
    temporal = observed_value(tmp_path, "null")
    model = model_store(
        tmp_path, specification_overrides={VAR_A: {"nullable": True}})
    result = evaluate(tmp_path, model=model, temporal=temporal)
    reasons = _reasons(result)
    assert "numeric_value_absent" in reasons
    assert "numeric_value_shape_mismatch" not in reasons
    assert result.participants[0].numeric_admission == "not_evaluated"


def test_source_unit_only_mismatch_refuses_semantic_admission(tmp_path):
    from backend.model_kernel import UnitReference

    resolver = interpretation_resolver(tmp_path, overrides={
        PROP_TEMP: {"unit": UnitReference(
            system_id="project_local", system_edition="ohk-units-1",
            code="synthetic_other_unit")}})
    result = evaluate(
        tmp_path,
        semantic=semantic_queries(tmp_path, interpretations=resolver))
    participant = result.participants[0]
    assert participant.semantic_admission == "not_admitted"
    assert participant.unit_admission == "mismatch"
    assert participant.refusal_reasons.count(
        "source_semantics_not_admitted") == 1


def test_known_lock_mismatch_survives_an_unavailable_peer_dimension(tmp_path):
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock

    registration = behavior_registration(owners=(E1, E1))
    declaration = behavior_declaration(registration, locks=(
        semantic_lock(VAR_A, quantity="other_quantity"),
        semantic_lock(VAR_B, quantity="other_quantity", role="reported"),
    ))
    model = model_store(
        tmp_path,
        declaration_records=(declaration,),
        omit_semantics=((VAR_A, "observation_role"),))
    result = evaluate(tmp_path, model=model)
    participant = result.participants[0]
    assert "model_observation_role_not_available" in participant.refusal_reasons
    assert "quantity_kind_lock_mismatch" in participant.refusal_reasons
    assert participant.lock_admission == "mismatched"


def test_known_source_mismatch_survives_an_unavailable_peer_dimension(tmp_path):
    resolver = interpretation_resolver(tmp_path, overrides={
        PROP_TEMP: {"quantity_kind": quantity_kind(
            code="synthetic_other_quantity")}})
    model = model_store(
        tmp_path,
        omit_semantics=((VAR_A, "observation_role"),))
    result = evaluate(
        tmp_path, model=model,
        semantic=semantic_queries(
            tmp_path, model=model, interpretations=resolver))
    participant = result.participants[0]
    assert "model_observation_role_not_available" in participant.refusal_reasons
    assert "source_semantics_not_admitted" in participant.refusal_reasons
    assert participant.semantic_admission == "not_admitted"


def test_each_semantic_lock_mismatch_is_independently_named(tmp_path):
    from backend.model_kernel import UnitReference
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock

    registration = behavior_registration(owners=(E1, E1))
    other_unit = UnitReference(
        system_id="project_local", system_edition="ohk-units-1",
        code="other_unit")
    locks = (
        semantic_lock(VAR_A, quantity="other_quantity", role="other_role",
                      unit=other_unit.code),
        semantic_lock(VAR_B, quantity="other_quantity", role="reported",
                      unit=other_unit.code),
    )
    declaration = behavior_declaration(registration, locks=locks)
    result = evaluate(
        tmp_path,
        model=model_store(tmp_path, declaration_records=(declaration,)))
    first = _reasons(result)
    assert "quantity_kind_lock_mismatch" in first
    assert "observation_role_lock_mismatch" in first
    assert "unit_lock_mismatch" in first
    assert result.participants[0].lock_admission == "mismatched"


def test_each_lock_refusal_is_independently_reachable(tmp_path):
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock

    cases = (
        ("quantity_kind_lock_mismatch", (
            semantic_lock(VAR_A, quantity="other_quantity"),
            semantic_lock(VAR_B, quantity="other_quantity", role="reported"))),
        ("observation_role_lock_mismatch", (
            semantic_lock(VAR_A, role="other_role"),
            semantic_lock(VAR_B, role="reported"))),
        ("unit_lock_mismatch", (
            semantic_lock(VAR_A, unit="other_unit"),
            semantic_lock(VAR_B, unit="other_unit", role="reported"))),
    )
    lock_reasons = {
        "quantity_kind_lock_mismatch", "observation_role_lock_mismatch",
        "unit_lock_mismatch"}
    for index, (expected, locks) in enumerate(cases):
        root = tmp_path / str(index)
        registration = behavior_registration(owners=(E1, E1))
        declaration = behavior_declaration(registration, locks=locks)
        result = evaluate(
            root,
            model=model_store(root, declaration_records=(declaration,)))
        actual = lock_reasons.intersection(_reasons(result))
        assert actual == {expected}


def test_multiple_refusals_follow_exact_global_gate_order(tmp_path):
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock

    registration = behavior_registration(owners=(E1, E1))
    declaration = behavior_declaration(registration, locks=(
        semantic_lock(VAR_A, quantity="other_quantity", role="other_role",
                      unit="other_unit"),
        semantic_lock(VAR_B, quantity="other_quantity", role="reported",
                      unit="other_unit"),
    ))
    result = evaluate(
        tmp_path,
        model=model_store(
            tmp_path,
            declaration_records=(declaration,),
            omit_semantics=((VAR_A, "observation_role"),)))
    reasons = _reasons(result)
    expected_order = (
        "model_observation_role_not_available",
        "quantity_kind_lock_mismatch",
        "unit_lock_mismatch",
    )
    assert tuple(reason for reason in reasons if reason in expected_order) == (
        expected_order)


def test_absent_behavior_can_disclose_an_unregistered_participant(tmp_path):
    from tests.model_kernel.bh001_slice_a_helpers import variable_records

    records = variable_records(owners=(E1, E1))
    store = ModelStore(tmp_path / "model" / "demo-printer")
    store.append(records[0])
    store.append(records[2])
    store.append(specification(VAR_B))
    semantic = semantic_queries(tmp_path, model=store)
    result = evaluate(tmp_path, semantic=semantic)
    assert result.behavior.conclusion == "not_registered"
    assert "participant_model_not_registered" in _reasons(result)
