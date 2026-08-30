"""BH-001 Slice A hostile persistence, replay, and preservation gates."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import backend.model_kernel as kernel
import backend.system_identity as identity
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.bh001_slice_a_helpers import (
    AS_DESIGNED,
    BEHAVIOR_A,
    BEHAVIOR_B,
    RULE_DECLARATION,
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
    semantic_lock,
    snapshot,
    variable_records,
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
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_BH001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION,
    PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES as PT_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as PT_ARTIFACT_SHA256,
    _artifact_bytes as pt_artifact_bytes,
)
from tests.model_state.test_demo_vp001 import (
    ARTIFACT_BYTES as VP_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as VP_ARTIFACT_SHA256,
    _artifact_bytes as vp_artifact_bytes,
)


DEMO_MODEL = Path("models/demo-printer")


def complete_records(*claims):
    registration = behavior_registration()
    records = (*variable_records(), registration, *claims)
    return {record.record_id: record for record in records}


def write_crafted(store, record, *, filename=None):
    payload = {**canonical_payload(record), "record_id": record.record_id}
    path = store.records_dir / (filename or f"{record.record_id}.json")
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    return path


def test_record_collection_reconstructs_forged_anchor_lock_context_and_rule():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    forged_anchor = registration.anchor.model_construct(
        anchor_id="bhv_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    bad_registration = registration.model_copy(update={"anchor": forged_anchor})

    bad_context = AS_DESIGNED.model_copy(update={"view": "future_view"})
    bad_signature = declaration.participant_semantics[0].signature.model_copy(
        update={"unit": declaration.participant_semantics[0].signature.unit
                .model_copy(update={"code": ""})})
    bad_lock = declaration.participant_semantics[0].model_copy(
        update={"signature": bad_signature})
    bad_rule = declaration.rule.model_construct(kind="affine")
    for forged in (
        bad_registration,
        declaration.model_copy(update={"context": bad_context}),
        declaration.model_copy(update={
            "participant_semantics": (
                bad_lock, declaration.participant_semantics[1])}),
        declaration.model_copy(update={"rule": bad_rule}),
    ):
        records = {record.record_id: record for record in variable_records()}
        if forged.record_kind != "behavior_registration":
            records[registration.record_id] = registration
        records[forged.record_id] = forged
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("demo-printer", records,
                                       verify_hashes=False)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_record_collection_rejects_stale_content_ids_for_all_behavior_arms():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    withdrawal = behavior_withdrawal(declaration)
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
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    store = world(tmp_path / "nested", declaration)
    payload = declaration.model_dump(mode="json")
    payload["participant_semantics"][0]["signature"]["unit"]["code"] = ""
    path = store.records_dir / f"{declaration.record_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"

    mismatch = world(tmp_path / "mismatch")
    wrong_name = "bhd_" + "0" * 64 + ".json"
    write_crafted(mismatch, declaration, filename=wrong_name)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        mismatch.load()
    assert error.value.error_code in {
        "MODEL_RECORD_KEY_MISMATCH", "MODEL_RECORD_HASH_MISMATCH"}


def test_crafted_load_enforces_behavior_model_evidence_closure(tmp_path):
    missing = kernel.ModelRecordEvidence(
        kind="model_record", record_id="reg_" + "f" * 64)
    registration = behavior_registration(evidence=(
        *behavior_registration().evidence, missing))
    store = kernel.ModelStore(tmp_path / "missing-evidence")
    for record in variable_records():
        store.append(record)
    write_crafted(store, registration)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_failed_behavior_append_is_atomic_even_with_hostile_nested_instance(
        tmp_path):
    store = world(tmp_path)
    before = snapshot(store)
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    forged = declaration.model_copy(update={
        "evidence": (RULE_DECLARATION.model_copy(update={"statement": ""}),)})
    with pytest.raises(kernel.ModelIntegrityError):
        store.append(forged)
    assert snapshot(store) == before


def test_all_explicit_pre_bh_histories_replay_with_empty_immutable_indexes():
    cases = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION, 9),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION, 10),
        (VS001_MEMBERSHIP, GOLDEN_REVISION, 11),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, 14),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION, 16),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION, 18),
        (PT001_MEMBERSHIP, PRE_VP001_REVISION, 28),
        (VP001_MEMBERSHIP, PRE_BH001_REVISION, 29),
    )
    store = kernel.ModelStore(DEMO_MODEL)
    empty_names = (
        "behavior_registrations", "behavior_registrations_by_anchor",
        "behavior_anchor_ids_by_variable", "behavior_rule_declarations",
        "behavior_rule_ids_by_key", "behavior_rule_root_by_id",
        "behavior_rule_ancestry_by_id", "behavior_rule_superseded_by",
        "current_behavior_rule_tips_by_root", "behavior_rule_withdrawals",
        "behavior_rule_withdrawn_by", "behavior_rule_withdrawals_by_target",
    )
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        for name in empty_names:
            mapping = getattr(loaded, name)
            assert mapping == {}
            with pytest.raises(TypeError):
                mapping["forged"] = ()


def test_current_demo_ledger_and_every_model_byte_remain_frozen():
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(paths) == 32
    assert sum(path.name.startswith("brg_") for path in paths) == 1
    assert sum(path.name.startswith("bhd_") for path in paths) == 1
    assert not any(path.name.startswith("bhw_") for path in paths)
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
            (DEMO_MODEL / "records" / filename).read_bytes()).hexdigest() == digest


def test_pt_and_vp_artifacts_remain_byte_frozen(tmp_path):
    pt = pt_artifact_bytes()
    vp = vp_artifact_bytes(tmp_path / "vp-artifact")
    assert len(pt) == PT_ARTIFACT_BYTES
    assert hashlib.sha256(pt).hexdigest() == PT_ARTIFACT_SHA256
    assert len(vp) == VP_ARTIFACT_BYTES
    assert hashlib.sha256(vp).hexdigest() == VP_ARTIFACT_SHA256


def test_slice_d_adds_fixture_without_kernel_import_or_evaluator_leakage():
    required_methods = (
        "behavior", "behavior_declaration",
        "behaviors_involving_variable", "behavior_assertion",
    )
    for method in required_methods:
        assert hasattr(kernel.ModelQueries, method)
    assert Path("backend/behavior_evaluation").is_dir()
    assert Path("tests/behavior_evaluation").is_dir()
    paths = tuple((DEMO_MODEL / "records").glob("*.json"))
    assert sum(path.name.startswith("brg_") for path in paths) == 1
    assert sum(path.name.startswith("bhd_") for path in paths) == 1
    assert not any(path.name.startswith("bhw_") for path in paths)
    assert hasattr(kernel, "BehaviorRuleResult")
    assert not hasattr(kernel, "BehaviorEvaluationResult")


def test_model_kernel_imports_remain_downward_only_and_behavior_free_upward():
    forbidden = (
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
    assert not Path("backend/model_kernel/behavior_evaluation.py").exists()


def test_behavior_anchor_and_records_do_not_create_port_or_vpa_meaning():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    forbidden_words = (
        "port", "vpa", "flow", "direction", "causes", "controls",
        "influences", "compatible", "safe", "input", "output",
    )
    public_fields = {
        *identity.BehaviorAnchor.model_fields,
        *kernel.BehaviorRegistration.model_fields,
        *kernel.BehaviorRuleDeclaration.model_fields,
        *kernel.BehaviorRuleWithdrawal.model_fields,
    }
    assert not public_fields.intersection(forbidden_words)
    assert registration.rule_family == declaration.rule.kind == \
        "exact_numeric_equality"


def test_record_map_order_and_hash_seed_do_not_change_indexes_or_revision():
    script = r'''import json
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.bh001_slice_a_helpers import (
    behavior_declaration, behavior_registration, behavior_withdrawal,
    variable_records)
r = behavior_registration()
root = behavior_declaration(r, note="root")
left = behavior_declaration(r, supersedes=(root.record_id,), note="left")
right = behavior_declaration(r, supersedes=(root.record_id,), note="right")
event = behavior_withdrawal(left)
records = (*variable_records(), r, root, left, right, event)
one = validate_record_collection("demo-printer", {
    item.record_id: item for item in records})
two = validate_record_collection("demo-printer", {
    item.record_id: item for item in reversed(records)})
def projection(value):
    return {
        "revision": value.revision.model_dump(mode="json"),
        "registrations": list(value.behavior_registrations),
        "anchors": list(value.behavior_registrations_by_anchor),
        "variables": [[key, list(items)] for key, items in
                      value.behavior_anchor_ids_by_variable.items()],
        "rules": list(value.behavior_rule_declarations),
        "roots": list(value.behavior_rule_root_by_id.items()),
        "ancestry": [[key, list(items)] for key, items in
                     value.behavior_rule_ancestry_by_id.items()],
        "tips": [[key, [item.record_id for item in items]] for key, items in
                 value.current_behavior_rule_tips_by_root.items()],
        "withdrawals": list(value.behavior_rule_withdrawals),
    }
assert projection(one) == projection(two)
print(json.dumps(projection(one), sort_keys=True, separators=(",", ":")))
'''
    outputs = []
    for seed in ("1", "17", "31337"):
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = seed
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(), env=environment,
            text=True, capture_output=True, check=True)
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1] == outputs[2]


def test_every_behavior_mapping_key_order_is_input_order_independent():
    first_registration = behavior_registration()
    second_registration = behavior_registration(
        behavior_anchor_id=BEHAVIOR_B, note="second")
    first_root = behavior_declaration(first_registration, note="first root")
    first_child = behavior_declaration(
        first_registration, supersedes=(first_root.record_id,), note="child")
    second_root = behavior_declaration(
        second_registration, behavior_anchor_id=BEHAVIOR_B,
        note="second root")
    first_event = behavior_withdrawal(first_child, note="first event")
    second_event = behavior_withdrawal(second_root, note="second event")
    records = (*variable_records(), first_registration, second_registration,
               first_root, first_child, second_root, first_event, second_event)
    forward = validate_record_collection(
        "demo-printer", {record.record_id: record for record in records})
    reverse = validate_record_collection(
        "demo-printer", {
            record.record_id: record for record in reversed(records)})
    names = (
        "behavior_registrations", "behavior_registrations_by_anchor",
        "behavior_anchor_ids_by_variable", "behavior_rule_declarations",
        "behavior_rule_ids_by_key", "behavior_rule_root_by_id",
        "behavior_rule_ancestry_by_id", "behavior_rule_superseded_by",
        "current_behavior_rule_tips_by_root", "behavior_rule_withdrawals",
        "behavior_rule_withdrawn_by",
        "behavior_rule_withdrawals_by_target",
    )
    for name in names:
        assert tuple(getattr(forward, name)) == tuple(getattr(reverse, name))
