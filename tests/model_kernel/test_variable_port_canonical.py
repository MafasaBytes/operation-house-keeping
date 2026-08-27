"""VP-001 Slice A canonical bytes, record union, and grammar vectors."""

import re

import pytest
from pydantic import TypeAdapter, ValidationError

from backend.model_kernel import ModelRecord, ModelRecordEvidence
from backend.model_kernel.canonical import canonical_bytes, verify_record_id
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN
from tests.model_kernel.test_variable_port_records import (
    AUTHORITY, CONTEXT, EVIDENCE, PORT, T0, VARIABLE,
    association, withdrawal,
)


VPA_ID = "vpa_4f13bcb49c3a5ad1fcabfe9581d41affbe19caa40dbd4201004534d5ad04fba1"
VPA_BYTES = (
    '{"authority":{"agent":"vp001_test_fixture","kind":"test_fixture",'
    '"method":"manual_declaration"},"context":{"kind":"lifecycle_view",'
    '"view":"as_designed"},"evidence":[{"kind":"owner_declaration",'
    '"statement":"synthetic VP-001 association"}],"note":"",'
    '"port_anchor_id":"prt_11111111111111111111111111111111",'
    '"record_kind":"variable_port_association",'
    '"recorded_at":"2026-08-28T12:00:00+00:00","schema_version":"1",'
    '"supersedes":[],"variable_anchor_id":'
    '"var_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}')
VPW_ID = "vpw_4b3146a6810535b921aaec495aefbb1ae7428c481abe833a30c656683f970172"
VPW_BYTES = (
    '{"authority":{"agent":"vp001_test_fixture","kind":"test_fixture",'
    '"method":"manual_declaration"},"note":"",'
    '"record_kind":"variable_port_association_withdrawal",'
    '"recorded_at":"2026-08-28T12:00:00+00:00","schema_version":"1",'
    '"withdraws":"vpa_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    'aaaaaaaaaaaaaaaa"}')


def test_literal_canonical_bytes_ids_and_verification():
    vpa, vpw = association(), withdrawal()
    assert (vpa.record_id, canonical_bytes(vpa).decode()) == (
        VPA_ID, VPA_BYTES)
    assert (vpw.record_id, canonical_bytes(vpw).decode()) == (
        VPW_ID, VPW_BYTES)
    assert verify_record_id(vpa) and verify_record_id(vpw)


def test_every_identity_bearing_field_changes_canonical_identity():
    base = association()
    other_evidence = EVIDENCE[0].model_copy(
        update={"statement": "different support"})
    variants = (
        association(variable_anchor_id="var_" + "c" * 32),
        association(port_anchor_id="prt_" + "2" * 32),
        association(context={"kind": "lifecycle_view", "view": "as_built"}),
        association(evidence=(other_evidence,)),
        association(authority=AUTHORITY.model_copy(update={"agent": "other"})),
        association(note="different"),
    )
    assert all(item.record_id != base.record_id for item in variants)
    assert all(canonical_bytes(item) != canonical_bytes(base)
               for item in variants)


def test_parent_and_evidence_permutations_have_one_identity():
    first, second = association(note="first"), association(note="second")
    extra = EVIDENCE[0].model_copy(update={"statement": "extra"})
    left = association(evidence=(extra, *EVIDENCE),
                       supersedes=(first.record_id, second.record_id),
                       note="merge")
    right = association(evidence=(*EVIDENCE, extra),
                        supersedes=(second.record_id, first.record_id),
                        note="merge")
    assert left.record_id == right.record_id
    assert canonical_bytes(left) == canonical_bytes(right)


def test_model_record_union_and_record_id_grammar_accept_both_exact_kinds():
    adapter = TypeAdapter(ModelRecord)
    for record in (association(), withdrawal()):
        rebuilt = adapter.validate_python(record.model_dump())
        assert type(rebuilt) is type(record)
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, record.record_id)
    for prefix in ("vpr", "vap", "vp", "VPA"):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN,
                                prefix + "_" + "a" * 64)


def test_kind_prefix_substitution_is_rejected_and_stale_id_fails_verification():
    adapter = TypeAdapter(ModelRecord)
    payload = association().model_dump()
    attacks = (
        {**payload, "record_id": "vpw_" + payload["record_id"][4:]},
        {**payload, "record_kind": "variable_port_association_withdrawal"},
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            adapter.validate_python(attack)
    stale = adapter.validate_python(
        {**payload, "record_id": "vpa_" + "0" * 64})
    assert verify_record_id(stale) is False


def test_citation_grammar_adds_vpa_without_making_vpw_citable():
    assert ModelRecordEvidence(
        kind="model_record", record_id="vpa_" + "a" * 64).record_id
    with pytest.raises(ValidationError):
        ModelRecordEvidence(
            kind="model_record", record_id="vpw_" + "a" * 64)


def test_direct_contracts_reject_malformed_prefixes_and_extra_fields():
    from backend import model_kernel as kernel

    with pytest.raises(ValidationError):
        kernel.VariablePortAssociation(
            record_kind="variable_port_association", schema_version="1",
            record_id="vpa_NOT_HEX", variable_anchor_id=VARIABLE,
            port_anchor_id=PORT, context=CONTEXT, evidence=EVIDENCE,
            supersedes=(), recorded_at=T0, authority=AUTHORITY, note="")
    with pytest.raises(ValidationError):
        kernel.VariablePortAssociationWithdrawal(
            record_kind="variable_port_association_withdrawal",
            schema_version="1", record_id="vpw_" + "0" * 64,
            withdraws="vpa_" + "a" * 64, recorded_at=T0,
            authority=AUTHORITY, note="", evidence=EVIDENCE)
