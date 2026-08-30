"""ST-001 Slice A hostile persistence, replay, and preservation gates."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
    STATE_DECLARATION,
    condition_world_records,
    snapshot,
    state_declaration,
    state_registration,
    state_withdrawal,
    world,
)
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CN001_MEMBERSHIP,
    CURRENT_REVISION,
    FROZEN_BH001_MODEL_RECORDS,
    FROZEN_CN001_MODEL_RECORDS,
    FROZEN_ES001_MODEL_RECORDS,
    FROZEN_MK001_RECORDS,
    FROZEN_PT001_MODEL_RECORDS,
    FROZEN_SN001_MODEL_RECORDS,
    FROZEN_VM001_RECORD,
    FROZEN_VP001_MODEL_RECORDS,
    FROZEN_VS001_RECORD,
    GOLDEN_REVISION,
    PRE_BH001_REVISION,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION,
    PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")


def complete_records(*claims):
    registration = state_registration()
    records = (*condition_world_records(), registration, *claims)
    return {record.record_id: record for record in records}


def write_crafted(store, record, *, filename=None):
    payload = {**canonical_payload(record), "record_id": record.record_id}
    path = store.records_dir / (filename or f"{record.record_id}.json")
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    return path


def test_collection_reconstructs_forged_anchor_pin_context_evidence_authority():
    registration = state_registration()
    declaration = state_declaration(registration)
    forged_anchor = registration.anchor.model_construct(
        anchor_id="sta_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    forged_context = AS_OPERATED.model_copy(update={"view": "future_view"})
    forged_pin = declaration.conditions[0].model_copy(update={
        "constraint_declaration_record_id": "vcn_NOT_HEX"})
    forged_evidence = STATE_DECLARATION.model_copy(update={"statement": ""})
    forged_authority = declaration.authority.model_copy(
        update={"kind": "future"})
    for forged in (
        registration.model_copy(update={"anchor": forged_anchor}),
        declaration.model_copy(update={"context": forged_context}),
        declaration.model_copy(update={
            "conditions": (forged_pin, declaration.conditions[1])}),
        declaration.model_copy(update={"evidence": (forged_evidence,)}),
        declaration.model_copy(update={"authority": forged_authority}),
    ):
        records = {record.record_id: record
                   for record in condition_world_records()}
        if forged.record_kind != "state_registration":
            records[registration.record_id] = registration
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "demo-printer", records, verify_hashes=False)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_collection_rejects_stale_content_ids_for_every_state_arm():
    registration = state_registration()
    declaration = state_declaration(registration)
    withdrawal = state_withdrawal(declaration)
    for record in (registration, declaration, withdrawal):
        forged = record.model_copy(update={"note": "mutated with stale id"})
        records = complete_records(declaration, withdrawal)
        records.pop(record.record_id, None)
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("demo-printer", records)
        assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def test_hostile_on_disk_nested_content_and_filename_mismatch_fail_closed(
        tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration)
    store = world(tmp_path / "nested", declaration)
    payload = declaration.model_dump(mode="json")
    payload["conditions"][0]["constraint_declaration_record_id"] = \
        "vcn_NOT_HEX"
    path = store.records_dir / f"{declaration.record_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"

    mismatch = world(tmp_path / "mismatch")
    wrong_name = "std_" + "0" * 64 + ".json"
    write_crafted(mismatch, declaration, filename=wrong_name)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        mismatch.load()
    assert error.value.error_code in {
        "MODEL_RECORD_KEY_MISMATCH", "MODEL_RECORD_HASH_MISMATCH"}


def test_failed_hostile_append_is_atomic(tmp_path):
    store = world(tmp_path)
    before = snapshot(store)
    revision = store.load().revision
    declaration = state_declaration()
    forged = declaration.model_copy(update={
        "evidence": (STATE_DECLARATION.model_copy(
            update={"statement": ""}),)})
    with pytest.raises(kernel.ModelIntegrityError):
        store.append(forged)
    assert snapshot(store) == before
    assert store.load().revision == revision


def test_all_explicit_pre_st_histories_replay_with_empty_immutable_indexes():
    cases = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION, 9),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION, 10),
        (VS001_MEMBERSHIP, GOLDEN_REVISION, 11),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, 14),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION, 16),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION, 18),
        (PT001_MEMBERSHIP, PRE_VP001_REVISION, 28),
        (VP001_MEMBERSHIP, PRE_BH001_REVISION, 29),
        (BH001_MEMBERSHIP, CURRENT_REVISION, 32),
    )
    empty_names = (
        "state_registrations", "state_registrations_by_anchor",
        "state_anchor_ids_by_subject_entity",
        "state_condition_constraint_ids_by_anchor", "state_declarations",
        "state_declaration_ids_by_key", "state_declaration_parent_ids",
        "state_declaration_successor_ids", "state_declaration_root_by_id",
        "state_declaration_ancestry_by_id",
        "current_state_declaration_tips_by_root",
        "state_declaration_withdrawals", "state_declaration_withdrawn_by",
        "state_declaration_withdrawals_by_target",
    )
    store = kernel.ModelStore(DEMO_MODEL)
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        for name in empty_names:
            mapping = getattr(loaded, name)
            assert mapping == {}
            with pytest.raises(TypeError):
                mapping["forged"] = ()


def test_current_32_record_ledger_and_every_predecessor_byte_remain_frozen():
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(paths) == 32
    assert not any(path.name.startswith(prefix)
                   for path in paths for prefix in ("srg_", "std_", "stw_"))
    loaded = kernel.ModelStore(DEMO_MODEL).load()
    assert loaded.revision.revision_id == CURRENT_REVISION
    assert loaded.revision.record_ids == BH001_MEMBERSHIP
    frozen = {
        **FROZEN_MK001_RECORDS,
        **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD,
        **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS,
        **FROZEN_CN001_MODEL_RECORDS,
        **FROZEN_PT001_MODEL_RECORDS,
        **FROZEN_VP001_MODEL_RECORDS,
        **FROZEN_BH001_MODEL_RECORDS,
    }
    assert len(frozen) == 32
    assert set(frozen) == {path.name for path in paths}
    for filename, digest in frozen.items():
        assert hashlib.sha256(
            (DEMO_MODEL / "records" / filename).read_bytes()).hexdigest() == \
            digest


def test_hash_seed_does_not_change_state_identity_or_index_order():
    script = """
import json
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.st001_slice_a_helpers import (
    condition_world_records, state_declaration, state_registration)
r = state_registration()
one = state_declaration(r, note='one')
two = state_declaration(r, note='two')
records = (*condition_world_records(), r, one, two)
loaded = validate_record_collection(
    'demo-printer', {item.record_id: item for item in reversed(records)})
print(json.dumps({
    'registration': r.record_id,
    'declarations': sorted((one.record_id, two.record_id)),
    'revision': loaded.revision.revision_id,
    'keys': [str(key) for key in loaded.state_declaration_ids_by_key],
    'roots': list(loaded.current_state_declaration_tips_by_root),
}, sort_keys=True, separators=(',', ':')))
"""
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ, PYTHONHASHSEED=seed)
        outputs.append(subprocess.check_output(
            [sys.executable, "-c", script], text=True,
            env=environment, cwd=Path.cwd()))
    assert len(set(outputs)) == 1


def test_kernel_import_direction_and_slice_boundary_remain_exact():
    forbidden = (
        "backend.state_classification",
        "backend.behavior_evaluation",
        "backend.model_state",
        "backend.temporal_state",
        "backend.identity_binding",
        "backend.observation_compatibility",
        "backend.semantic_compatibility",
        "backend.constraint_evaluation",
        "backend.source_interpretation",
        "backend.data_sources",
        "backend.structural_evidence",
    )
    imports = []
    for path in Path("backend/model_kernel").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
    assert not any(name.startswith(forbidden) for name in imports)
    assert not Path("backend/state_classification").exists()
    for method in (
        "state", "state_declaration", "states_of_entity", "state_assertion"):
        assert not hasattr(kernel.ModelQueries, method)


def test_slice_a_readme_documents_state_truth_and_non_transition_boundary():
    text = Path("backend/model_kernel/README.md").read_text(encoding="utf-8")
    for required in (
        "StateRegistration", "StateDeclaration",
        "StateDeclarationWithdrawal", "all_of_constraints",
        "independent_latest_at_or_before_cutoff",
        "does not implement state transitions",
    ):
        assert required in text
