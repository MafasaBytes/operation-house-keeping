"""ST-002 Slice A hostile reconstruction and append-integrity gates."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    TRANSITION_DECLARATION_CLAIM,
    transition_declaration,
    transition_fixture,
    transition_registration,
    transition_withdrawal,
    world,
)
from tests.model_kernel.test_transition_store import complete_records


def tree_snapshot(store):
    return {
        path.relative_to(store.records_dir.parent).as_posix(): path.read_bytes()
        for path in sorted(store.records_dir.parent.rglob("*"))
        if path.is_file()
    }


def test_collection_reconstructs_forged_anchor_pin_context_evidence_authority():
    registration = transition_registration()
    declaration = transition_declaration(registration)
    hostile_anchor = registration.anchor.model_construct(
        anchor_id="trn_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    hostile_context = AS_OPERATED.model_copy(update={"view": "future_view"})
    hostile_pin = declaration.from_endpoint.model_copy(update={
        "declaration_record_id": "std_NOT_HEX"})
    hostile_evidence = TRANSITION_DECLARATION_CLAIM.model_copy(update={
        "statement": ""})
    hostile_authority = declaration.authority.model_copy(update={
        "kind": "future"})
    forged_values = (
        registration.model_copy(update={"anchor": hostile_anchor}),
        declaration.model_copy(update={"context": hostile_context}),
        declaration.model_copy(update={"from_endpoint": hostile_pin}),
        declaration.model_copy(update={"evidence": (hostile_evidence,)}),
        declaration.model_copy(update={"authority": hostile_authority}),
    )
    for forged in forged_values:
        records = complete_records(declaration)
        records.pop(forged.record_id, None)
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "test-model", records, verify_hashes=False)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_hidden_extras_fail_at_every_transition_nesting_level():
    registration = transition_registration()
    declaration = transition_declaration(registration)
    withdrawal = transition_withdrawal(declaration)
    attacks = (
        registration.model_copy(update={"trigger": "forged"}),
        declaration.model_copy(update={"assessment": "forged"}),
        withdrawal.model_copy(update={"reason_code": "forged"}),
        registration.model_copy(update={
            "anchor": registration.anchor.model_copy(
                update={"from_state_anchor_id": "sta_" + "a" * 32})}),
        declaration.model_copy(update={
            "context": declaration.context.model_copy(
                update={"cutoff": "2026-09-02T09:00:00Z"})}),
        declaration.model_copy(update={
            "from_endpoint": declaration.from_endpoint.model_copy(
                update={"role": "from"})}),
        declaration.model_copy(update={
            "evidence": (
                declaration.evidence[0].model_copy(update={"activity": True}),
                *declaration.evidence[1:])}),
        declaration.model_copy(update={
            "authority": declaration.authority.model_copy(
                update={"priority": 1})}),
    )
    for forged in attacks:
        records = complete_records(declaration, withdrawal)
        records.pop(forged.record_id, None)
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", records)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_equal_reappend_is_noop_and_stale_same_id_rejects_for_all_new_kinds(
        tmp_path):
    _, registration, from_registration, to_registration, from_declaration, \
        to_declaration = transition_fixture()
    declaration = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration)
    withdrawal = transition_withdrawal(declaration)
    store, *_ = world(tmp_path, declaration, withdrawal)
    for record in (registration, declaration, withdrawal):
        before = tree_snapshot(store)
        revision = store.load().revision
        assert store.append(record) == record.record_id
        assert tree_snapshot(store) == before
        assert store.load().revision == revision

        stale = record.model_copy(update={"note": "mutated with stale id"})
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.append(stale)
        assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
        assert tree_snapshot(store) == before
        assert store.load().revision == revision


def test_tampered_target_and_corrupted_sibling_block_idempotent_reappend(
        tmp_path):
    declaration = transition_declaration()
    withdrawal = transition_withdrawal(declaration)
    store, registration, *_ = world(tmp_path / "target", declaration,
                                     withdrawal)
    target = store.records_dir / f"{declaration.record_id}.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["note"] = "tampered"
    target.write_text(json.dumps(payload), encoding="utf-8")
    tampered = target.read_bytes()
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(declaration)
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
    assert target.read_bytes() == tampered

    sibling_store, sibling_registration, *_ = world(
        tmp_path / "sibling", declaration)
    state_sibling = next(
        record for record in sibling_store.load().records.values()
        if record.record_kind == "state_registration")
    sibling_path = sibling_store.records_dir / f"{state_sibling.record_id}.json"
    sibling_payload = json.loads(sibling_path.read_text(encoding="utf-8"))
    sibling_payload["note"] = "corrupted sibling"
    sibling_path.write_text(json.dumps(sibling_payload), encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        sibling_store.append(sibling_registration)
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def test_correctly_hashed_semantically_invalid_file_fails_on_load(tmp_path):
    store, registration, from_registration, to_registration, \
        from_declaration, to_declaration = world(tmp_path)
    declaration_pin = kernel.TransitionStateDeclarationPin(
        state_anchor_id=to_registration.anchor.anchor_id,
        declaration_record_id=from_declaration.record_id)
    invalid = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration, from_endpoint=declaration_pin,
        note="wrong role")
    assert declaration_pin.state_anchor_id == to_registration.anchor.anchor_id
    payload = {**canonical_payload(invalid), "record_id": invalid.record_id}
    path = store.records_dir / f"{invalid.record_id}.json"
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_TRANSITION_DECLARATION_INVALID"


def test_crafted_cycle_rejects_iteratively_without_hash_verification():
    one = transition_declaration(note="one")
    two = transition_declaration(note="two")
    first_id = "trd_" + "1" * 64
    second_id = "trd_" + "2" * 64
    one = one.model_copy(update={
        "record_id": first_id, "supersedes": (second_id,)})
    two = two.model_copy(update={
        "record_id": second_id, "supersedes": (first_id,)})
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection(
            "test-model", complete_records(one, two), verify_hashes=False)
    assert error.value.error_code == "MODEL_TRANSITION_LINEAGE_INVALID"


def test_hash_seed_does_not_change_transition_identity_revision_or_indexes():
    script = r'''
import json
from datetime import timedelta
from backend.model_kernel import ModelQueries
from backend.model_kernel.canonical import canonical_bytes
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.st001_slice_a_helpers import state_declaration
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED, STATE_A, T1, TRANSITION_A, transition_declaration,
    transition_fixture, transition_withdrawal)

records, registration, from_registration, to_registration, from_std, to_std = (
    transition_fixture())
def claim(**kwargs):
    return transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_std,
        to_declaration=to_std, **kwargs)
root = claim(note="root")
left = claim(supersedes=(root.record_id,), note="left")
right = claim(supersedes=(root.record_id,), note="right")
corroborating_one = claim(recorded_at=T1, note="corroborating-one")
corroborating_two = claim(
    recorded_at=T1 + timedelta(seconds=1), note="corroborating-two")
successor = state_declaration(
    from_registration, state_anchor_id=STATE_A,
    supersedes=(from_std.record_id,), recorded_at=T1,
    note="hash-seed endpoint successor")
divergent = transition_declaration(
    registration, from_registration=from_registration,
    to_registration=to_registration, from_declaration=successor,
    to_declaration=to_std, recorded_at=T1 + timedelta(seconds=2),
    note="divergent")
inactive = claim(
    recorded_at=T1 + timedelta(seconds=3), note="inactive")
event = transition_withdrawal(
    inactive, recorded_at=T1 + timedelta(seconds=4))
transition_records = (
    registration, root, left, right, corroborating_one, corroborating_two,
    divergent, inactive, event)
values = (*records, successor, *transition_records)
loaded = validate_record_collection(
    "test-model", {record.record_id: record for record in reversed(values)})
queries = ModelQueries(loaded)
print(json.dumps({
    "ids": [record.record_id for record in transition_records],
    "revision": loaded.revision.revision_id,
    "canonical": [[item.record_id, canonical_bytes(item).hex()] for item in
                  transition_records],
    "registrations": [[key, value.record_id] for key, value in
                      loaded.transition_registrations.items()],
    "anchors": [[key, value.record_id] for key, value in
                loaded.transition_registrations_by_anchor.items()],
    "subjects": [[key, list(value)] for key, value in
                 loaded.transition_anchor_ids_by_subject_entity.items()],
    "ordered_endpoints": [[list(key), value] for key, value in
        loaded.transition_registration_id_by_ordered_subject_endpoints.items()],
    "declarations": [[key, value.record_id] for key, value in
                     loaded.transition_declarations.items()],
    "declaration_keys": [[[key[0], key[1].model_dump(mode="json")],
                           list(value)] for key, value in
                          loaded.transition_declaration_ids_by_key.items()],
    "parents": [[key, list(value)] for key, value in
                loaded.transition_declaration_parent_ids.items()],
    "successors": [[key, list(value)] for key, value in
                   loaded.transition_declaration_successor_ids.items()],
    "roots": list(loaded.transition_declaration_root_by_id.items()),
    "ancestry": [[key, list(value)] for key, value in
                 loaded.transition_declaration_ancestry_by_id.items()],
    "tips": [[key, [item.record_id for item in value]] for key, value in
             loaded.current_transition_declaration_tips_by_root.items()],
    "withdrawn": [[key, list(value)] for key, value in
                  loaded.transition_declaration_withdrawn_by.items()],
    "withdrawals": [[key, value.record_id] for key, value in
                    loaded.transition_declaration_withdrawals.items()],
    "withdrawals_by_target": [[key, list(value)] for key, value in
        loaded.transition_declaration_withdrawals_by_target.items()],
    "query_serialization": {
        "lookup": json.loads(queries.transition(
            TRANSITION_A).model_dump_json()),
        "declaration": json.loads(queries.transition_declaration(
            TRANSITION_A, context=AS_OPERATED).model_dump_json()),
        "entity": json.loads(queries.transitions_of_entity(
            registration.subject_entity_anchor_id,
            context=AS_OPERATED).model_dump_json()),
        "assertions": [json.loads(queries.transition_assertion(
            record.record_id).model_dump_json())
            for record in transition_records],
    },
}, sort_keys=True, separators=(",", ":")))
'''
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ, PYTHONHASHSEED=seed)
        outputs.append(subprocess.check_output(
            [sys.executable, "-c", script], text=True,
            env=environment, cwd=Path.cwd()))
    assert len(set(outputs)) == 1
