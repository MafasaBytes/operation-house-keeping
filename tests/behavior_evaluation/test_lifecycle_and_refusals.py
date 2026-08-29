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


def test_inconsistent_occurrence_evidence_is_not_numeric_shape_refusal(tmp_path):
    temporal = observed_stack(tmp_path)
    craft_occurrence(temporal, value_json="true", json_type="number")
    result = evaluate(tmp_path, temporal=temporal)
    reasons = _reasons(result)
    assert "evidence_not_assessable" in reasons
    assert "numeric_value_shape_mismatch" not in reasons
    assert result.participants[0].numeric_admission == "not_evaluated"


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
