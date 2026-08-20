"""PT-001 Slice A canonical identity, grammar, and permutation vectors."""

import re

import pytest
from pydantic import TypeAdapter, ValidationError

from backend.model_kernel import (
    InterfaceDomainDeclaration,
    InterfaceTypeDeclaration,
    ModelRecord,
    ModelRecordEvidence,
    PortCompatibilityBasis,
    PortInterfaceDeclaration,
    build_record,
)
from backend.model_kernel.canonical import canonical_bytes, verify_record_id
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN
from tests.model_kernel.test_port_records import (
    AUTHORITY,
    CONTEXT,
    EVIDENCE,
    PORT_A,
    PORT_B,
    T0,
    compatibility,
    connection,
    dimension_basis,
    domain_token,
    interface,
    registration,
    type_token,
    withdrawal,
)


GOLDENS = {
    "prg_3c63f81929fdc26b814db57bbb26dc2a932af7b975f2f8a6fa655e54968d70fb":
        '{"anchor":{"anchor_id":"prt_11111111111111111111111111111111","display_name":"Synthetic interface","namespace":"demo-printer","role_name":null},"authority":{"agent":"pt001_test_fixture","kind":"test_fixture","method":"manual_declaration"},"evidence":[{"kind":"owner_declaration","statement":"synthetic PT-001 claim"}],"note":"","owner_entity_anchor_id":"ent_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","record_kind":"port_registration","recorded_at":"2026-08-20T12:00:00+00:00","schema_version":"1"}',
    "pif_3df46652baa5e36b10d79db2f04280894e9a2d79270437e4e54b3bd28935100d":
        '{"authority":{"agent":"pt001_test_fixture","kind":"test_fixture","method":"manual_declaration"},"context":{"kind":"lifecycle_view","view":"as_designed"},"declaration":{"dimension":"interface_domain","value":{"code":"electrical","system_edition":"ohk-interface-domains-1","system_id":"project_local","token_kind":"interface_domain"}},"evidence":[{"kind":"owner_declaration","statement":"synthetic PT-001 claim"}],"note":"","port_anchor_id":"prt_11111111111111111111111111111111","record_kind":"port_interface_declaration","recorded_at":"2026-08-20T12:00:00+00:00","schema_version":"1","supersedes":[]}',
    "pcn_420d1ef1d47c1d9e0660ecf3a71a29bb62d90195749872241762a28a311503bb":
        '{"authority":{"agent":"pt001_test_fixture","kind":"test_fixture","method":"manual_declaration"},"context":{"kind":"lifecycle_view","view":"as_designed"},"endpoint_port_anchor_ids":["prt_11111111111111111111111111111111","prt_22222222222222222222222222222222"],"evidence":[{"kind":"owner_declaration","statement":"synthetic PT-001 claim"}],"note":"","record_kind":"port_connection_assertion","recorded_at":"2026-08-20T12:00:00+00:00","schema_version":"1","supersedes":[]}',
    "pcm_417303c5c91ca89ef1f2214616e78f1221f4f36a449f2ea8024fb2643b0f99c4":
        '{"authority":{"agent":"pt001_test_fixture","kind":"test_fixture","method":"manual_declaration"},"basis":{"dimensions":[{"citations":[{"declaration_record_id":"pif_3df46652baa5e36b10d79db2f04280894e9a2d79270437e4e54b3bd28935100d","port_anchor_id":"prt_11111111111111111111111111111111"},{"declaration_record_id":"pif_648e2252e2b5388f34b2b8315219de2ba0fc25cca491a30cd96e60daae68e7d9","port_anchor_id":"prt_22222222222222222222222222222222"}],"dimension":"interface_domain"}],"statement":"Synthetic explicit compatibility claim"},"context":{"kind":"lifecycle_view","view":"as_designed"},"endpoint_port_anchor_ids":["prt_11111111111111111111111111111111","prt_22222222222222222222222222222222"],"evidence":[{"kind":"owner_declaration","statement":"synthetic PT-001 claim"}],"note":"","outcome":"declared_compatible","record_kind":"port_compatibility_declaration","recorded_at":"2026-08-20T12:00:00+00:00","schema_version":"1","supersedes":[]}',
    "ptw_f36a5b140b137094135d5e50dc35a9909084d008991f09889d59e83341ed8197":
        '{"authority":{"agent":"pt001_test_fixture","kind":"test_fixture","method":"manual_declaration"},"note":"","record_kind":"port_claim_withdrawal","recorded_at":"2026-08-20T12:00:00+00:00","schema_version":"1","withdraws":"pif_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}',
}


def records():
    return registration(), interface(), connection(), compatibility(), withdrawal()


def test_all_five_kinds_have_literal_canonical_bytes_and_ids():
    actual = {record.record_id: canonical_bytes(record).decode()
              for record in records()}
    assert actual == GOLDENS
    assert all(verify_record_id(record) for record in records())


def test_domain_and_type_tokens_are_distinct_canonical_identity_material():
    domain = interface(declaration=InterfaceDomainDeclaration(
        dimension="interface_domain", value=domain_token("signal")))
    type_ = build_record(
        PortInterfaceDeclaration, port_anchor_id=PORT_A, context=CONTEXT,
        declaration=InterfaceTypeDeclaration(
            dimension="interface_type", value=type_token("signal")),
        evidence=EVIDENCE, supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note="")
    assert domain.record_id != type_.record_id
    assert canonical_bytes(domain) != canonical_bytes(type_)
    assert b'"token_kind":"interface_domain"' in canonical_bytes(domain)
    assert b'"token_kind":"interface_type"' in canonical_bytes(type_)


@pytest.mark.parametrize("token_factory,declaration_cls,dimension", [
    (domain_token, InterfaceDomainDeclaration, "interface_domain"),
    (type_token, InterfaceTypeDeclaration, "interface_type"),
])
def test_token_kind_is_required_direct_dict_and_nested(
        token_factory, declaration_cls, dimension):
    payload = token_factory().model_dump(exclude={"token_kind"})
    with pytest.raises(ValidationError):
        type(token_factory())(**payload)
    with pytest.raises(ValidationError):
        declaration_cls(dimension=dimension, value=payload)

    valid = interface() if dimension == "interface_domain" else build_record(
        PortInterfaceDeclaration, port_anchor_id=PORT_A, context=CONTEXT,
        declaration=InterfaceTypeDeclaration(
            dimension="interface_type", value=type_token()),
        evidence=EVIDENCE, supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note="")
    record_payload = valid.model_dump()
    del record_payload["declaration"]["value"]["token_kind"]
    with pytest.raises(ValidationError):
        TypeAdapter(ModelRecord).validate_python(record_payload)


def test_evidence_parent_endpoint_and_basis_permutations_are_canonical():
    extra = EVIDENCE[0].model_copy(update={"statement": "other support"})
    assert registration(evidence=(extra, *EVIDENCE)).record_id == registration(
        evidence=(*EVIDENCE, extra, *EVIDENCE)).record_id

    first = interface(note="first")
    second = interface(note="second")
    forward = interface(supersedes=(first.record_id, second.record_id),
                        note="merge")
    reverse = interface(supersedes=(second.record_id, first.record_id),
                        note="merge")
    assert forward.record_id == reverse.record_id
    assert connection((PORT_A, PORT_B)).record_id == connection(
        (PORT_B, PORT_A)).record_id

    domain = dimension_basis("interface_domain")
    direction = dimension_basis("direction_role")
    basis_a = PortCompatibilityBasis(
        statement="ordered", dimensions=(domain, direction))
    basis_b = PortCompatibilityBasis(
        statement="ordered", dimensions=(direction.model_copy(update={
            "citations": tuple(reversed(direction.citations))}), domain))
    assert compatibility((PORT_A, PORT_B), basis=basis_a).record_id == \
        compatibility((PORT_B, PORT_A), basis=basis_b).record_id


def test_model_record_union_and_prefix_grammar_accept_exact_pt_kinds():
    adapter = TypeAdapter(ModelRecord)
    for record in records():
        assert type(adapter.validate_python(record.model_dump())) is type(record)
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, record.record_id)
    for prefix in ("prt", "pot", "pcx"):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN,
                                prefix + "_" + "a" * 64)


@pytest.mark.parametrize("prefix", ["prg", "pif", "pcn", "pcm"])
def test_claim_and_registration_records_are_citable(prefix):
    record = ModelRecordEvidence(kind="model_record",
                                 record_id=prefix + "_" + "a" * 64)
    assert record.record_id.startswith(prefix + "_")


def test_ptw_is_structurally_uncitable():
    with pytest.raises(ValidationError):
        ModelRecordEvidence(kind="model_record",
                            record_id="ptw_" + "a" * 64)
