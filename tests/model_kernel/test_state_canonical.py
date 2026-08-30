"""ST-001 Slice A canonical identity and hostile reconstruction vectors."""

import json
import re

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.canonical import (
    _state_effective_body_bytes,
    canonical_bytes,
    verify_record_id,
)
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN

from tests.model_kernel.builders import CON_A, CON_B
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
    STATE_DECLARATION,
    state_declaration,
    state_registration,
    state_withdrawal,
)


SRG_ID = "srg_c87954c50e92c35d4143e016bf90383d6a6a5f64347741336218bcbcaa027b73"
STD_ID = "std_2c3cb8783acadd8add368efcbf2782a165f591e06c6a77109caad7de018f4bb8"
STW_ID = "stw_b811c3b4c435aff8421a4ebdb4fa133ff3b86a8b8b5d4d9dc228aff312fe0cd0"


def test_exact_golden_ids_byte_lengths_and_verification():
    registration = state_registration()
    declaration = state_declaration(registration)
    withdrawal = state_withdrawal(declaration)
    assert tuple(record.record_id for record in (
        registration, declaration, withdrawal)) == (SRG_ID, STD_ID, STW_ID)
    assert tuple(len(canonical_bytes(record)) for record in (
        registration, declaration, withdrawal)) == (1000, 1409, 297)
    assert all(verify_record_id(record)
               for record in (registration, declaration, withdrawal))


def test_record_grammar_accepts_only_exact_state_prefixes():
    for prefix in ("srg", "std", "stw"):
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, prefix + "_" + "a" * 64)
    for malformed in (
        "STD_" + "a" * 64,
        "st_" + "a" * 64,
        "std_" + "A" * 64,
        "std_" + "a" * 63,
        "std_" + "a" * 65,
    ):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN, malformed)


def test_condition_evidence_and_parent_permutations_have_one_identity():
    registration = state_registration(constraints=(CON_B, CON_A))
    root = state_declaration(registration, note="root")
    other = state_declaration(registration, note="other")
    base = state_declaration(registration)
    extra = STATE_DECLARATION.model_copy(
        update={"statement": "additional synthetic support"})
    evidence = (*base.evidence, extra)
    forward = state_declaration(
        registration, condition_pins=tuple(reversed(base.conditions)),
        evidence=tuple(reversed(evidence)),
        supersedes=(root.record_id, other.record_id), note="merge")
    reverse = state_declaration(
        registration, condition_pins=base.conditions, evidence=evidence,
        supersedes=(other.record_id, root.record_id), note="merge")
    assert forward.record_id == reverse.record_id
    assert canonical_bytes(forward) == canonical_bytes(reverse)


def test_stale_id_and_kind_prefix_substitution_fail_authoritative_parsing():
    adapter = TypeAdapter(kernel.ModelRecord)
    valid = state_declaration()
    stale = adapter.validate_python({
        **valid.model_dump(), "record_id": "std_" + "0" * 64})
    assert verify_record_id(stale) is False
    for attack in (
        {**valid.model_dump(), "record_id": "stw_" + "0" * 64},
        {**valid.model_dump(), "record_kind": "state_declaration_withdrawal"},
    ):
        with pytest.raises(ValidationError):
            adapter.validate_python(attack)


def test_nested_construct_and_copy_forgery_is_reconstructed_not_trusted():
    adapter = TypeAdapter(kernel.ModelRecord)
    registration = state_registration()
    declaration = state_declaration(registration)
    hostile_anchor = registration.anchor.model_construct(
        anchor_id="sta_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    hostile_context = AS_OPERATED.model_copy(update={"view": "future_view"})
    hostile_pin = declaration.conditions[0].model_copy(
        update={"constraint_declaration_record_id": "vcn_NOT_HEX"})
    hostile_evidence = STATE_DECLARATION.model_copy(update={"statement": ""})
    hostile_authority = declaration.authority.model_copy(
        update={"kind": "future"})
    for forged in (
        registration.model_copy(update={"anchor": hostile_anchor}),
        declaration.model_copy(update={"context": hostile_context}),
        declaration.model_copy(update={
            "conditions": (hostile_pin, declaration.conditions[1])}),
        declaration.model_copy(update={"evidence": (hostile_evidence,)}),
        declaration.model_copy(update={"authority": hostile_authority}),
    ):
        with pytest.raises(ValidationError):
            adapter.validate_python(forged)


def test_effective_body_projection_is_exact_and_excludes_audit_fields():
    registration = state_registration()
    first = state_declaration(registration, note="authority one")
    second = state_declaration(
        registration, recorded_at=first.recorded_at.replace(hour=14),
        note="authority two")
    expected_fields = {
        "state_anchor_id", "context", "conditions", "evaluation_basis"}
    decoded = json.loads(_state_effective_body_bytes(first))
    assert set(decoded) == expected_fields
    assert _state_effective_body_bytes(first) == \
        _state_effective_body_bytes(second)
    changed = state_declaration(
        registration, context={"kind": "lifecycle_view", "view": "as_built"})
    assert _state_effective_body_bytes(first) != \
        _state_effective_body_bytes(changed)


def test_existing_record_golden_vectors_remain_unchanged():
    from tests.model_kernel.test_behavior_canonical import (
        BHD_ID, BHW_ID, BRG_ID, behavior_declaration,
        behavior_registration, behavior_withdrawal,
    )

    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    withdrawal = behavior_withdrawal(declaration)
    assert (registration.record_id, declaration.record_id,
            withdrawal.record_id) == (BRG_ID, BHD_ID, BHW_ID)
