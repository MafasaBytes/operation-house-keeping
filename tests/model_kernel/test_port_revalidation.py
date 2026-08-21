"""PT-001 Slice A adversarial record and architecture trust boundaries."""

import hashlib
import json
from pathlib import Path

import pytest

from backend.model_kernel import ModelIntegrityError, ModelQueries, ModelStore
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.contracts import RelationshipAssertion
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import ENT_A, registration as entity_registration
from tests.model_kernel.test_demo_model import CURRENT_REVISION, DEMO_MODEL
from tests.model_kernel.test_port_records import (
    PORT_A,
    PORT_B,
    compatibility,
    connection,
    domain_token,
    interface,
    registration,
    withdrawal,
)


def valid_members(record):
    entity = entity_registration(ENT_A)
    port_a = registration()
    port_b = registration(anchor=port_a.anchor.model_copy(update={
        "anchor_id": PORT_B, "display_name": "Port B"}))
    members = [entity, port_a]
    if record.record_kind in ("port_connection_assertion",
                              "port_compatibility_declaration"):
        members.append(port_b)
    if record.record_kind == "port_compatibility_declaration":
        members.extend((interface(PORT_A), interface(PORT_B)))
    if (record.record_kind == "port_claim_withdrawal"
            and record.withdraws.startswith("pif_")):
        target = interface(PORT_A)
        # A well-shaped withdrawal fixture names its actual selected target;
        # invalid-target forgeries must remain untouched for revalidation.
        if record.withdraws == "pif_" + "a" * 64:
            record = withdrawal(target.record_id).model_copy(update={
                "record_id": record.record_id, "note": record.note})
        members.append(target)
    members.append(record)
    return record, {item.record_id: item for item in members}


def assert_collection_rejects(record, code="MODEL_RECORD_INVALID"):
    record, members = valid_members(record)
    with pytest.raises(ModelIntegrityError) as error:
        validate_record_collection("demo-printer", members,
                                   verify_hashes=False)
    assert error.value.error_code == code


@pytest.mark.parametrize("factory,update", [
    (registration, {"owner_entity_anchor_id": "ent_NOT_HEX"}),
    (interface, {"port_anchor_id": "prt_NOT_HEX"}),
    (connection, {"endpoint_port_anchor_ids": (PORT_A,)}),
    (compatibility, {"outcome": "looks_compatible"}),
    (withdrawal, {"withdraws": "prg_" + "a" * 64}),
])
def test_top_level_model_construct_and_model_copy_forgeries_are_rejected(
        factory, update):
    valid = factory()
    constructed = type(valid).model_construct(
        **{**valid.model_dump(), **update})
    copied = valid.model_copy(update=update)
    assert_collection_rejects(constructed)
    assert_collection_rejects(copied)


def test_nested_anchor_token_body_citation_and_evidence_forgeries_are_rejected():
    valid = registration()
    bad_anchor = valid.anchor.model_construct(
        anchor_id="prt_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    assert_collection_rejects(valid.model_copy(update={"anchor": bad_anchor}))

    claim = interface()
    bad_token = domain_token().model_copy(update={"token_kind": "interface_type"})
    bad_body = claim.declaration.model_copy(update={"value": bad_token})
    assert_collection_rejects(claim.model_copy(update={"declaration": bad_body}))

    pcm = compatibility()
    item = pcm.basis.dimensions[0]
    bad_citation = item.citations[0].model_copy(
        update={"port_anchor_id": "prt_NOT_HEX"})
    bad_item = item.model_copy(update={
        "citations": (bad_citation, item.citations[1])})
    bad_basis = pcm.basis.model_copy(update={"dimensions": (bad_item,)})
    assert_collection_rejects(pcm.model_copy(update={"basis": bad_basis}))

    bad_evidence = claim.evidence[0].model_copy(update={"statement": ""})
    assert_collection_rejects(claim.model_copy(update={
        "evidence": (bad_evidence,)}))


@pytest.mark.parametrize("factory", [
    registration, interface, connection, compatibility, withdrawal,
])
def test_valid_shape_with_stale_id_is_a_typed_hash_failure(factory):
    original = factory()
    changed = original.model_copy(update={"note": "changed after hashing"})
    changed, members = valid_members(changed)
    with pytest.raises(ModelIntegrityError) as error:
        validate_record_collection("demo-printer", members, verify_hashes=True)
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def test_hostile_unicode_is_rejected_path_free_at_public_boundary():
    hostile = json.loads('"\\ud800"')
    forged = interface().model_copy(update={"note": hostile})
    with pytest.raises(ModelIntegrityError) as error:
        _, members = valid_members(forged)
        validate_record_collection("demo-printer", members, verify_hashes=True)
    assert "/" not in str(error.value) and "\\" not in str(error.value)


def test_append_failure_is_atomic_and_crafted_load_and_replay_revalidate(tmp_path):
    entity = entity_registration(ENT_A)
    store = ModelStore(tmp_path / "demo-printer")
    store.append(entity)
    before = tuple(store.records_dir.iterdir())
    forged = registration().model_copy(update={
        "owner_entity_anchor_id": "ent_NOT_HEX"})
    with pytest.raises(ModelIntegrityError):
        store.append(forged)
    assert tuple(store.records_dir.iterdir()) == before

    crafted = ModelStore(tmp_path / "crafted")
    valid = registration()
    payload = {**canonical_payload(valid), "record_id": valid.record_id}
    payload["anchor"]["anchor_id"] = "prt_NOT_HEX"
    (crafted.records_dir / f"{valid.record_id}.json").write_text(
        json.dumps(payload), encoding="utf-8")
    with pytest.raises(ModelIntegrityError):
        crafted.load()

    complete = ModelStore(tmp_path / "complete")
    complete.append(entity)
    complete.append(valid)
    with pytest.raises(ModelIntegrityError):
        complete.replay((valid.record_id,))


def test_hostile_on_disk_pt_record_fails_load_all_or_nothing(tmp_path):
    store = ModelStore(tmp_path / "hostile")
    entity = entity_registration(ENT_A)
    valid = registration()
    store.append(entity)
    payload = {**canonical_payload(valid), "record_id": valid.record_id}
    payload["anchor"]["namespace"] = "bad namespace"
    (store.records_dir / f"{valid.record_id}.json").write_text(
        json.dumps(payload, sort_keys=True), encoding="utf-8")
    with pytest.raises(ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_slice_b_adds_queries_without_store_or_relationship_port_endpoint():
    assert not any(path.name.startswith(("port_", "connectivity"))
                   for path in Path("backend").iterdir())
    for name in ("port", "ports_of_entity", "port_interface",
                 "connections_exact", "connections_of_port",
                 "connections_containing", "port_assertion",
                 "interface_compatibility"):
        assert hasattr(ModelQueries, name)
    assert not hasattr(ModelQueries, "connection")
    assert "source_anchor_id" in RelationshipAssertion.model_fields
    assert "target_anchor_id" in RelationshipAssertion.model_fields
    assert "endpoint_port_anchor_ids" not in RelationshipAssertion.model_fields


def test_demo_ledger_remains_the_byte_frozen_eighteen_record_cn_revision():
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(paths) == 18
    assert ModelStore(DEMO_MODEL).load().revision.revision_id == CURRENT_REVISION
    assert not any(path.name.startswith(
        ("prg_", "pif_", "pcn_", "pcm_", "ptw_")) for path in paths)
    # Pin one digest over the entire accepted file-name/byte sequence so any
    # mutation, addition, deletion, or reorder changes this guard.
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    assert digest.hexdigest() == "62802b5728396049e8874d48b987d3cda4ba0250cb720599bc1df81ae50f067d"
