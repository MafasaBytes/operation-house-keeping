"""ST-002 Slice A canonical transition identity vectors."""

from datetime import timedelta, timezone
import hashlib
import json
import re

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.canonical import (
    _transition_effective_body_bytes,
    canonical_bytes,
    compute_record_id,
    verify_record_id,
)
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN
from backend.model_kernel.store import _FILENAME

from tests.model_kernel.st002_slice_a_helpers import (
    T0,
    TRANSITION_DECLARATION_CLAIM,
    transition_declaration,
    transition_registration,
    transition_withdrawal,
)


TRG_ID = "trg_ed2c47d29a82dd515e0c54f5675439bfd94b30be1eb9a8c254e059fe82c6a3e6"
TRD_ID = "trd_df488538ce135c51a350c8e23eb7faec5afa4c3813d2ac12b33b47307ac55873"
TRW_ID = "trw_3f7e1eba701284af490aa3f4f80b4f021903e0e2f3974f2b7df1505cf55a2ce3"


def test_transition_ids_equal_normative_canonical_sha256_and_use_plus_utc():
    registration = transition_registration()
    declaration = transition_declaration(registration)
    withdrawal = transition_withdrawal(declaration)
    assert (registration.record_id, declaration.record_id,
            withdrawal.record_id) == (TRG_ID, TRD_ID, TRW_ID)
    assert tuple(len(canonical_bytes(record)) for record in (
        registration, declaration, withdrawal)) == (983, 1343, 302)
    for record in (registration, declaration, withdrawal):
        payload = canonical_bytes(record)
        assert record.record_id.rsplit("_", 1)[1] == hashlib.sha256(
            payload).hexdigest()
        assert compute_record_id(record) == record.record_id
        assert verify_record_id(record) is True
        assert b"+00:00" in payload
        assert b"Z" not in payload


def test_record_grammar_accepts_exactly_three_transition_prefixes():
    for prefix in ("trg", "trd", "trw"):
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, prefix + "_" + "a" * 64)
        assert _FILENAME.fullmatch(prefix + "_" + "a" * 64 + ".json")
    for malformed in (
        "TRD_" + "a" * 64, "tro_" + "a" * 64,
        "trd_" + "A" * 64, "trd_" + "a" * 63,
    ):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN, malformed)
        assert not _FILENAME.fullmatch(malformed + ".json")


def test_equal_instants_evidence_and_parent_order_have_stable_identity():
    registration = transition_registration()
    root = transition_declaration(registration, note="root")
    other = transition_declaration(
        registration, recorded_at=T0.replace(hour=11), note="other")
    base = transition_declaration(registration)
    extra = TRANSITION_DECLARATION_CLAIM.model_copy(update={
        "statement": "Additional synthetic transition support."})
    eastern = timezone(timedelta(hours=2))
    forward = transition_declaration(
        registration, evidence=tuple(reversed((*base.evidence, extra))),
        supersedes=(other.record_id, root.record_id),
        recorded_at=T0.astimezone(eastern), note="merge")
    reverse = transition_declaration(
        registration, evidence=(*base.evidence, extra),
        supersedes=(root.record_id, other.record_id),
        recorded_at=T0, note="merge")
    assert forward == reverse
    assert canonical_bytes(forward) == canonical_bytes(reverse)


def test_endpoint_role_reversal_changes_identity_and_bytes():
    forward = transition_registration()
    reverse = transition_registration(
        from_state=forward.to_state_anchor_id,
        to_state=forward.from_state_anchor_id,
        evidence=forward.evidence)
    assert forward.record_id != reverse.record_id
    assert canonical_bytes(forward) != canonical_bytes(reverse)


def test_effective_body_projection_is_exact_and_audit_independent():
    first = transition_declaration(note="authority one")
    second = transition_declaration(
        recorded_at=T0.replace(hour=12), note="authority two")
    decoded = json.loads(_transition_effective_body_bytes(first))
    assert set(decoded) == {
        "transition_anchor_id", "context", "from_endpoint", "to_endpoint"}
    assert _transition_effective_body_bytes(first) == \
        _transition_effective_body_bytes(second)


def test_stale_id_kind_substitution_and_hostile_nested_pins_fail():
    adapter = TypeAdapter(kernel.ModelRecord)
    declaration = transition_declaration()
    stale = adapter.validate_python({
        **declaration.model_dump(), "record_id": "trd_" + "0" * 64})
    assert verify_record_id(stale) is False
    with pytest.raises(ValidationError):
        adapter.validate_python({
            **declaration.model_dump(), "record_id": "trw_" + "0" * 64})
    hostile_pin = declaration.from_endpoint.model_copy(update={
        "declaration_record_id": "std_NOT_HEX"})
    hostile = declaration.model_copy(update={"from_endpoint": hostile_pin})
    with pytest.raises(ValidationError):
        adapter.validate_python(hostile)
