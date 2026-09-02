"""ST-002 Slice A red-first exact transition record contracts."""

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel

from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    AUTHORITY,
    STATE_A,
    STATE_B,
    TRANSITION_A,
    T0,
    transition_declaration,
    transition_registration,
    transition_withdrawal,
)


def test_transition_registration_exact_contract():
    value = transition_registration()
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "anchor",
        "subject_entity_anchor_id", "from_state_anchor_id",
        "to_state_anchor_id", "evidence", "recorded_at", "authority", "note")
    assert value.record_kind == "transition_registration"
    assert value.schema_version == "1"
    assert value.record_id.startswith("trg_") and len(value.record_id) == 68
    assert (value.from_state_anchor_id, value.to_state_anchor_id) == (
        STATE_A, STATE_B)


def test_transition_pin_and_declaration_exact_contracts():
    value = transition_declaration()
    assert tuple(kernel.TransitionStateDeclarationPin.model_fields) == (
        "state_anchor_id", "declaration_record_id")
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id",
        "transition_anchor_id", "context", "from_endpoint", "to_endpoint",
        "evidence", "supersedes", "recorded_at", "authority", "note")
    assert value.transition_anchor_id == TRANSITION_A
    assert value.from_endpoint.state_anchor_id == STATE_A
    assert value.to_endpoint.state_anchor_id == STATE_B
    assert "evaluation_basis" not in type(value).model_fields


def test_transition_withdrawal_is_exactly_minimal():
    value = transition_withdrawal(transition_declaration())
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert value.record_kind == "transition_declaration_withdrawal"
    assert value.record_id.startswith("trw_") and len(value.record_id) == 68


def test_public_builder_direct_construction_and_union_have_parity():
    registration = transition_registration()
    declaration = transition_declaration(registration)
    withdrawal = transition_withdrawal(declaration)
    adapter = TypeAdapter(kernel.ModelRecord)
    for record in (registration, declaration, withdrawal):
        direct = type(record)(**record.model_dump())
        rebuilt = adapter.validate_python(record.model_dump())
        assert direct == record
        assert type(rebuilt) is type(record)


def test_direct_contract_and_public_builder_reject_hidden_nested_fields():
    registration = transition_registration()
    declaration = transition_declaration(registration)
    withdrawal = transition_withdrawal(declaration)
    cases = (
        (registration, "anchor", registration.anchor.model_copy(
            update={"occurrence": True})),
        (registration, "authority", registration.authority.model_copy(
            update={"priority": 1})),
        (registration, "evidence", (
            registration.evidence[0].model_copy(update={"activity": True}),
            *registration.evidence[1:])),
        (declaration, "context", declaration.context.model_copy(
            update={"cutoff": "2026-09-02T09:00:00Z"})),
        (declaration, "from_endpoint", declaration.from_endpoint.model_copy(
            update={"occurred": True})),
        (declaration, "to_endpoint", declaration.to_endpoint.model_copy(
            update={"assessment": "forged"})),
        (declaration, "authority", declaration.authority.model_copy(
            update={"recommendation": "none"})),
        (declaration, "evidence", (
            declaration.evidence[0].model_copy(update={"alignment": "forged"}),
            *declaration.evidence[1:])),
        (withdrawal, "authority", withdrawal.authority.model_copy(
            update={"reason": "forged"})),
    )
    for record, field, forged in cases:
        payload = record.model_dump(mode="python")
        payload[field] = forged
        with pytest.raises(ValidationError):
            type(record)(**payload)
        payload.pop("record_id")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            kernel.build_record(type(record), **payload)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("parents", [
    ("trd_" + "a" * 64, "trd_" + "a" * 64),
    ("trg_" + "a" * 64,), ("trw_" + "a" * 64,), ("trd_NOT_HEX",),
])
def test_declaration_rejects_duplicate_or_non_trd_parents(parents):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        transition_declaration(supersedes=parents)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_declaration_rejects_self_supersession_at_direct_boundary():
    value = transition_declaration()
    with pytest.raises(ValidationError):
        kernel.TransitionDeclaration(**{
            **value.model_dump(), "supersedes": (value.record_id,)})


@pytest.mark.parametrize("target", [
    "trg_" + "a" * 64, "trw_" + "a" * 64,
    "std_" + "a" * 64, "trd_NOT_HEX",
])
def test_withdrawal_accepts_only_trd_identity(target):
    with pytest.raises(kernel.ModelIntegrityError):
        kernel.build_record(
            kernel.TransitionDeclarationWithdrawal, withdraws=target,
            recorded_at=T0, authority=AUTHORITY, note="")


def test_rc4_trg_and_trd_are_citable_but_trw_is_not():
    existing = (
        "reg", "rtd", "rel", "vrg", "vsp", "vsm", "crg", "vcn",
        "prg", "pif", "pcn", "pcm", "vpa", "brg", "bhd", "srg", "std",
    )
    for prefix in (*existing, "trg", "trd"):
        record_id = prefix + "_" + "a" * 64
        assert kernel.ModelRecordEvidence(
            kind="model_record", record_id=record_id).record_id == record_id
    for prefix in ("trw", "rwd", "ptw", "vpw", "bhw", "stw"):
        with pytest.raises(ValidationError):
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=prefix + "_" + "a" * 64)


@pytest.mark.parametrize(("factory", "forbidden"), [
    (transition_registration, {
        "context": AS_OPERATED, "transition_family": "mechanism",
        "trigger": "changed", "occurrence": True, "outcome": "matches"}),
    (transition_declaration, {
        "evaluation_basis": "independent_latest_at_or_before_cutoff",
        "cutoff": "2026-09-02T09:00:00Z", "guard": "true",
        "action": "none", "assessment": "consistent"}),
])
def test_positive_claims_forbid_assessment_occurrence_and_mechanism_fields(
        factory, forbidden):
    for field, value in forbidden.items():
        with pytest.raises(kernel.ModelIntegrityError):
            factory(**{field: value})


@pytest.mark.parametrize(("field", "value"), [
    ("evidence", ()), ("context", AS_OPERATED),
    ("supersedes", ("trd_" + "a" * 64,)),
    ("reason_code", "false"), ("outcome", "inactive"),
])
def test_withdrawal_forbids_claim_context_parents_and_outcomes(field, value):
    with pytest.raises(kernel.ModelIntegrityError):
        transition_withdrawal(
            transition_declaration(), **{field: value})


def test_slice_a_exports_only_four_transition_record_contracts():
    required = {
        "TransitionRegistration", "TransitionStateDeclarationPin",
        "TransitionDeclaration", "TransitionDeclarationWithdrawal",
    }
    assert required <= set(kernel.__all__)
    for forbidden in ("TransitionAssessment", "TransitionOccurrence"):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)
