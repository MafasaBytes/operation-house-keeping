"""ST-001 Slice A red-first exact record-contract tests."""

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel

from tests.model_kernel.builders import CON_A, CON_B
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
    AUTHORITY,
    STATE_A,
    T0,
    state_declaration,
    state_registration,
    state_withdrawal,
)


def test_state_registration_exact_contract_and_defaults():
    value = state_registration()
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "anchor",
        "subject_entity_anchor_id", "condition_constraint_anchor_ids",
        "condition_family", "evidence", "recorded_at", "authority", "note")
    assert value.record_kind == "state_registration"
    assert value.schema_version == "1"
    assert value.record_id.startswith("srg_") and len(value.record_id) == 68
    assert value.condition_constraint_anchor_ids == (CON_A, CON_B)
    assert value.condition_family == "all_of_constraints"


def test_state_pin_and_declaration_exact_contracts():
    value = state_declaration()
    assert tuple(kernel.StateConstraintDeclarationPin.model_fields) == (
        "constraint_anchor_id", "constraint_declaration_record_id")
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "state_anchor_id",
        "context", "conditions", "evaluation_basis", "evidence",
        "supersedes", "recorded_at", "authority", "note")
    assert value.record_kind == "state_declaration"
    assert value.schema_version == "1"
    assert value.record_id.startswith("std_") and len(value.record_id) == 68
    assert value.evaluation_basis == \
        "independent_latest_at_or_before_cutoff"
    assert tuple(pin.constraint_anchor_id for pin in value.conditions) == (
        CON_A, CON_B)


def test_state_withdrawal_is_exactly_minimal():
    target = state_declaration()
    value = state_withdrawal(target)
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert value.record_kind == "state_declaration_withdrawal"
    assert value.record_id.startswith("stw_") and len(value.record_id) == 68


@pytest.mark.parametrize("constraints", [(), (CON_A, CON_A)])
def test_registration_rejects_empty_and_duplicate_constraints(constraints):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        state_registration(constraints=constraints, evidence=(
            kernel.OwnerDeclarationEvidence(
                kind="owner_declaration", statement="explicit"),))
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_registration_accepts_one_and_64_constraints_and_rejects_65():
    values = tuple(f"con_{index:032x}" for index in range(65))
    evidence = (kernel.OwnerDeclarationEvidence(
        kind="owner_declaration", statement="explicit"),)
    assert len(state_registration(
        constraints=values[:1], evidence=evidence
    ).condition_constraint_anchor_ids) == 1
    assert len(state_registration(
        constraints=tuple(reversed(values[:64])), evidence=evidence
    ).condition_constraint_anchor_ids) == 64
    with pytest.raises(kernel.ModelIntegrityError):
        state_registration(constraints=values, evidence=evidence)


def test_constraint_and_pin_input_order_is_canonical_and_identity_stable():
    registration_one = state_registration(constraints=(CON_B, CON_A))
    registration_two = state_registration(constraints=(CON_A, CON_B))
    assert registration_one == registration_two
    assert registration_one.record_id == registration_two.record_id
    forward = state_declaration(registration_one)
    reverse = state_declaration(
        registration_one, condition_pins=tuple(reversed(forward.conditions)))
    assert forward == reverse
    assert forward.record_id == reverse.record_id


@pytest.mark.parametrize("parents", [
    ("std_" + "a" * 64, "std_" + "a" * 64),
    ("srg_" + "a" * 64,),
    ("stw_" + "a" * 64,),
    ("std_NOT_HEX",),
])
def test_declaration_rejects_duplicate_or_non_std_parents(parents):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        state_declaration(supersedes=parents)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_declaration_rejects_self_supersession_at_direct_boundary():
    value = state_declaration()
    payload = value.model_dump()
    payload["supersedes"] = (value.record_id,)
    with pytest.raises(ValidationError):
        kernel.StateDeclaration(**payload)


@pytest.mark.parametrize("target", [
    "srg_" + "a" * 64,
    "stw_" + "a" * 64,
    "bhd_" + "a" * 64,
    "std_NOT_HEX",
])
def test_withdrawal_target_accepts_only_std_identity(target):
    with pytest.raises(kernel.ModelIntegrityError):
        kernel.build_record(
            kernel.StateDeclarationWithdrawal, withdraws=target,
            recorded_at=T0, authority=AUTHORITY, note="")


def test_srg_and_std_are_citable_but_stw_is_not():
    for record_id in ("srg_" + "a" * 64, "std_" + "b" * 64):
        assert kernel.ModelRecordEvidence(
            kind="model_record", record_id=record_id).record_id == record_id
    with pytest.raises(ValidationError):
        kernel.ModelRecordEvidence(
            kind="model_record", record_id="stw_" + "a" * 64)


def test_model_record_union_accepts_exact_three_state_arms():
    registration = state_registration()
    declaration = state_declaration(registration)
    withdrawal = state_withdrawal(declaration)
    adapter = TypeAdapter(kernel.ModelRecord)
    for record in (registration, declaration, withdrawal):
        rebuilt = adapter.validate_python(record.model_dump())
        assert type(rebuilt) is type(record)


def test_slice_a_public_surface_is_records_only():
    required = {
        "StateRegistration", "StateConstraintDeclarationPin",
        "StateDeclaration", "StateDeclarationWithdrawal",
    }
    assert required <= set(kernel.__all__)
    for forbidden in (
        "StateLookupResult", "StateDeclarationResult", "EntityStatesResult",
        "StateAssertionDisclosureResult", "StateClassificationQueries",
        "StateClassificationResult",
    ):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)


@pytest.mark.parametrize("field,value", [
    ("context", AS_OPERATED),
    ("supersedes", ("std_" + "a" * 64,)),
    ("outcome", "matches"),
    ("source", {"source_id": "x"}),
    ("transition", "start"),
])
def test_registration_forbids_context_lifecycle_result_and_transition_fields(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError):
        state_registration(**{field: value})


@pytest.mark.parametrize("field,value", [
    ("predicate", {"kind": "exact_numeric_upper_bound"}),
    ("as_of", "2026-08-30T12:00:00Z"),
    ("computed_match", "matches"),
    ("exclusive", True),
    ("priority", 1),
    ("from_state", STATE_A),
])
def test_declaration_forbids_inline_predicates_temporal_results_and_transitions(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError):
        state_declaration(**{field: value})


@pytest.mark.parametrize("field,value", [
    ("evidence", (kernel.OwnerDeclarationEvidence(
        kind="owner_declaration", statement="no"),)),
    ("context", AS_OPERATED),
    ("supersedes", ("std_" + "a" * 64,)),
    ("outcome", "does_not_match"),
    ("reason_code", "false"),
])
def test_withdrawal_forbids_claim_context_parent_outcome_and_reason(field,
                                                                    value):
    target = state_declaration()
    with pytest.raises(kernel.ModelIntegrityError):
        kernel.build_record(
            kernel.StateDeclarationWithdrawal, withdraws=target.record_id,
            recorded_at=T0, authority=AUTHORITY, note="", **{field: value})
