"""FL-001 Slice A hostile reconstruction and deterministic-integrity gates."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_bytes, canonical_payload
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import (
    FLOW_DECLARATION_CLAIM,
    complete_records,
    direction_pin,
    flow_declaration,
    flow_fixture,
    flow_registration,
    flow_withdrawal,
    world,
)


def tree_snapshot(store):
    return {
        path.relative_to(store.records_dir.parent).as_posix(): path.read_bytes()
        for path in sorted(store.records_dir.parent.rglob("*"))
        if path.is_file()
    }


def claims():
    _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs)
    return registration, declaration, flow_withdrawal(declaration)


def test_collection_reconstructs_forged_anchor_token_pin_context_and_evidence():
    registration, declaration, withdrawal = claims()
    hostile_anchor = registration.anchor.model_construct(
        anchor_id="flo_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    hostile_token = registration.flow_kind.model_copy(update={"code": ""})
    hostile_pin = declaration.source_direction_pins[0].model_copy(update={
        "declaration_record_id": "pif_NOT_HEX"})
    hostile_context = declaration.context.model_copy(update={"view": "future"})
    hostile_evidence = FLOW_DECLARATION_CLAIM.model_copy(update={
        "statement": ""})
    hostile_authority = declaration.authority.model_copy(update={
        "kind": "future"})
    forged_values = (
        registration.model_copy(update={"anchor": hostile_anchor}),
        registration.model_copy(update={"flow_kind": hostile_token}),
        declaration.model_copy(update={"source_direction_pins": (
            hostile_pin,)}),
        declaration.model_copy(update={"context": hostile_context}),
        declaration.model_copy(update={"evidence": (hostile_evidence,)}),
        withdrawal.model_copy(update={"authority": hostile_authority}),
    )
    for forged in forged_values:
        records = complete_records(declaration, withdrawal)
        records.pop(forged.record_id, None)
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "test-model", records, verify_hashes=False)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_hidden_extras_and_private_state_fail_at_every_flow_nesting_level():
    registration, declaration, withdrawal = claims()
    private_pin = declaration.source_direction_pins[0].model_copy()
    object.__setattr__(private_pin, "__pydantic_private__", {"forged": True})
    attacks = (
        registration.model_copy(update={"activity": "forged"}),
        declaration.model_copy(update={"occurrence": "forged"}),
        withdrawal.model_copy(update={"reason_code": "forged"}),
        registration.model_copy(update={
            "anchor": registration.anchor.model_copy(
                update={"connection_anchor_id": "con_" + "a" * 32})}),
        registration.model_copy(update={
            "flow_kind": registration.flow_kind.model_copy(
                update={"mechanism": "forged"})}),
        declaration.model_copy(update={
            "source_direction_pins": (private_pin,)}),
        declaration.model_copy(update={
            "context": declaration.context.model_copy(
                update={"cutoff": "2026-09-02T12:00:00Z"})}),
        declaration.model_copy(update={
            "evidence": (
                declaration.evidence[0].model_copy(
                    update={"flowing": True}),
                *declaration.evidence[1:])}),
    )
    for forged in attacks:
        records = complete_records(declaration, withdrawal)
        records.pop(forged.record_id, None)
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", records)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_falsey_top_level_extra_rejects_collection_and_store_append(tmp_path):
    class FalseyExtra(dict):
        def __bool__(self):
            return False

    registration, declaration, _ = claims()
    forged = registration.model_copy()
    object.__setattr__(
        forged, "__pydantic_extra__", FalseyExtra({"activity": True}))
    records = complete_records(declaration)
    records.pop(registration.record_id)
    records[registration.record_id] = forged
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", records)
    assert error.value.error_code == "MODEL_RECORD_INVALID"

    store, *_ = world(tmp_path)
    before = tree_snapshot(store)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(forged)
    assert error.value.error_code == "MODEL_RECORD_INVALID"
    assert tree_snapshot(store) == before


def test_equal_reappend_is_noop_and_same_id_different_content_rejects(
        tmp_path):
    registration, declaration, withdrawal = claims()
    store, *_ = world(tmp_path, declaration, withdrawal)
    for record in (registration, declaration, withdrawal):
        before = tree_snapshot(store)
        revision = store.load().revision
        assert store.append(record) == record.record_id
        assert tree_snapshot(store) == before
        assert store.load().revision == revision
        stale = record.model_copy(update={"note": "stale same-id content"})
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.append(stale)
        assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
        assert tree_snapshot(store) == before


def test_tampered_target_and_sibling_block_idempotent_reappend(tmp_path):
    registration, declaration, _ = claims()
    store, *_ = world(tmp_path / "target", declaration)
    target = store.records_dir / f"{declaration.record_id}.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["note"] = "tampered"
    target.write_text(json.dumps(payload), encoding="utf-8")
    tampered = target.read_bytes()
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(declaration)
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
    assert target.read_bytes() == tampered

    sibling, *_ = world(tmp_path / "sibling")
    prior = next(iter(sibling.load().port_registrations_by_anchor.values()))
    sibling_path = sibling.records_dir / f"{prior.record_id}.json"
    sibling_payload = json.loads(sibling_path.read_text(encoding="utf-8"))
    sibling_payload["note"] = "corrupted sibling"
    sibling_path.write_text(json.dumps(sibling_payload), encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        sibling.append(registration)
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def test_correctly_hashed_semantically_invalid_file_fails_on_load(tmp_path):
    _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    store, *_ = world(tmp_path)
    wrong_pin = direction_pin(
        registration.source_port_anchor_ids[0], sink_pifs[0].record_id)
    invalid = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs,
        source_direction_pins=(wrong_pin,), note="wrong pinned port")
    payload = {**canonical_payload(invalid), "record_id": invalid.record_id}
    path = store.records_dir / f"{invalid.record_id}.json"
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_FLOW_DECLARATION_INVALID"


def test_crafted_cycle_rejects_iteratively_without_hash_verification():
    one = claims()[1]
    two = claims()[1].model_copy(update={"note": "two"})
    first_id = "fld_" + "1" * 64
    second_id = "fld_" + "2" * 64
    one = one.model_copy(update={
        "record_id": first_id, "supersedes": (second_id,)})
    two = two.model_copy(update={
        "record_id": second_id, "supersedes": (first_id,)})
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection(
            "test-model", complete_records(one, two), verify_hashes=False)
    assert error.value.error_code == "MODEL_FLOW_LINEAGE_INVALID"


def test_replay_requires_every_flow_dependency_and_extra_evidence(tmp_path):
    registration, declaration, _ = claims()
    parent = flow_declaration(
        registration,
        port_records=flow_fixture()[2], pcn=flow_fixture()[3],
        source_pifs=flow_fixture()[4], sink_pifs=flow_fixture()[5],
        note="required parent")
    extra_support = flow_declaration(
        registration,
        port_records=flow_fixture()[2], pcn=flow_fixture()[3],
        source_pifs=flow_fixture()[4], sink_pifs=flow_fixture()[5],
        note="extra evidence support")
    dependent = flow_declaration(
        registration,
        port_records=flow_fixture()[2], pcn=flow_fixture()[3],
        source_pifs=flow_fixture()[4], sink_pifs=flow_fixture()[5],
        evidence=(*declaration.evidence, kernel.ModelRecordEvidence(
            kind="model_record", record_id=extra_support.record_id)),
        supersedes=(parent.record_id,),
        note="dependent")
    store, _, ports, *_ = world(
        tmp_path, parent, extra_support, dependent)
    loaded = store.load()
    mandatory = (
        next(record.record_id for record in loaded.records.values()
             if record.record_kind == "entity_registration"),
        registration.record_id,
        *(record.record_id for record in ports),
        dependent.connection_assertion_record_id,
        dependent.source_direction_pins[0].declaration_record_id,
        dependent.sink_direction_pins[0].declaration_record_id,
        parent.record_id,
        extra_support.record_id,
    )
    for omitted in mandatory:
        membership = tuple(
            record_id for record_id in loaded.revision.record_ids
            if record_id != omitted)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.replay(membership)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_mixed_world_membership_cannot_substitute_another_flow_registration():
    records, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs)
    other = flow_registration(
        flow_anchor_id="flo_" + "b" * 32,
        port_records=ports,
        kind=registration.flow_kind.model_copy(update={
            "code": "other_logical_flow"}))
    mixed = {record.record_id: record for record in (
        *records, other, declaration)}
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", mixed)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_hash_seed_does_not_change_flow_identity_revision_or_indexes():
    script = r'''
import json
from backend.model_kernel.canonical import canonical_bytes
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import (
    complete_records, flow_declaration, flow_fixture, flow_withdrawal)

_, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
def claim(**kwargs):
    return flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs, **kwargs)
root = claim(note="root")
left = claim(supersedes=(root.record_id,), note="left")
right = claim(supersedes=(root.record_id,), note="right")
inactive = claim(note="inactive")
event = flow_withdrawal(inactive)
values = tuple(complete_records(root, left, right, inactive, event).values())
loaded = validate_record_collection(
    "test-model", {record.record_id: record for record in reversed(values)})
flow_records = (registration, root, left, right, inactive, event)
def pairs(mapping, value=lambda item: item):
    return [[repr(key), value(item)] for key, item in mapping.items()]
print(json.dumps({
    "ids": [record.record_id for record in flow_records],
    "canonical": [[record.record_id, canonical_bytes(record).hex()]
                  for record in flow_records],
    "revision": loaded.revision.revision_id,
    "registrations": pairs(
        loaded.flow_registrations, lambda item: item.record_id),
    "anchors": pairs(
        loaded.flow_registrations_by_anchor, lambda item: item.record_id),
    "signatures": pairs(loaded.flow_anchor_id_by_semantic_signature),
    "ports": pairs(loaded.flow_anchor_ids_by_port, list),
    "roles": pairs(loaded.flow_role_by_anchor_and_port),
    "declarations": pairs(
        loaded.flow_declarations, lambda item: item.record_id),
    "keys": pairs(loaded.flow_declaration_ids_by_key, list),
    "parents": pairs(loaded.flow_declaration_parent_ids, list),
    "successors": pairs(loaded.flow_declaration_successor_ids, list),
    "roots": pairs(loaded.flow_declaration_root_by_id),
    "ancestry": pairs(loaded.flow_declaration_ancestry_by_id, list),
    "tips": pairs(loaded.current_flow_declaration_tips_by_root,
                  lambda items: [item.record_id for item in items]),
    "bodies": pairs(loaded.flow_declaration_effective_body_by_id,
                    lambda item: item.hex()),
    "groups": pairs(loaded.flow_declaration_ids_by_effective_body, list),
    "withdrawn": pairs(loaded.flow_declaration_withdrawn_by, list),
    "withdrawals": pairs(
        loaded.flow_declaration_withdrawals, lambda item: item.record_id),
    "withdrawals_by_target": pairs(
        loaded.flow_declaration_withdrawals_by_target, list),
}, sort_keys=True, separators=(",", ":")))
'''
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ, PYTHONHASHSEED=seed,
                           PYTHONDONTWRITEBYTECODE="1")
        outputs.append(subprocess.check_output(
            [sys.executable, "-c", script], text=True,
            env=environment, cwd=Path.cwd()))
    assert len(set(outputs)) == 1
