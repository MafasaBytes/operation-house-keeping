"""BH-001 Slice D owner gate: disposable candidate rehearsal only."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

import pytest

from tests.model_kernel.bh001_slice_d_rehearsal import (
    BASE_REVISION,
    CONTEXT,
    DISCLAIMER,
    MANIFEST_PATH,
    VP001_MEMBERSHIP,
    WARNINGS,
    candidate_manifest,
    candidate_records,
    canonical_json_bytes,
    historical_revisions,
    _assert_binding_seam,
    record_inventory,
    run_rehearsal,
    sha256_bytes,
    tree_inventory,
    verify_accepted_artifacts,
)


VARIABLE_ID = "var_ab2d312466054c20b0ac764e9bc0114e"
BEHAVIOR_ID = "bhv_80e21f1682e449ca9c65a5e2ee051ea0"
VRG_ID = "vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6"
BRG_ID = "brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e"
BHD_ID = "bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e"
FINAL_REVISION = "mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b"
MANIFEST_SHA256 = "8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07"
ARTIFACT_BYTES = 122406
ARTIFACT_SHA256 = "4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3"
PREDECESSOR_AGGREGATE = "962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf"
FILE_GOLDENS = {
    f"{VRG_ID}.json": {
        "bytes": 630,
        "sha256": "0652fd7ca32de43d3e21c5a41a5117eb3c19d2a469ffa30f37b407f91937e285",
    },
    f"{BRG_ID}.json": {
        "bytes": 1376,
        "sha256": "19068707d3bb5423eab4db189208d85749ef18cc3447135d8cfa4ea7f0e89edb",
    },
    f"{BHD_ID}.json": {
        "bytes": 2333,
        "sha256": "fa1a40272d100eb81cc15e64cff782a654b3369a91da62bc36b1f26a2cf655cf",
    },
}


@pytest.fixture(scope="module")
def rehearsals(tmp_path_factory):
    protected_roots = (
        Path("models/demo-printer"),
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
        Path("interpretations/demo-printer"),
        Path("var/raw_store"),
        Path("showcases/demo-printer"),
    )
    before = tree_inventory(*protected_roots)
    first = run_rehearsal(tmp_path_factory.mktemp("bh001-first"))
    middle = tree_inventory(*protected_roots)
    second = run_rehearsal(tmp_path_factory.mktemp("bh001-second"))
    after = tree_inventory(*protected_roots)
    assert before == middle == after
    return first, second


def test_frozen_candidate_manifest_is_exact_and_revalidated():
    manifest, variable, behavior, raw = candidate_manifest()
    assert len(raw) == 678
    assert sha256_bytes(raw) == MANIFEST_SHA256
    assert manifest == {
        "accepted_base_model_revision": BASE_REVISION,
        "allocation_apis": {
            "behavior_anchor": "backend.system_identity.mint_behavior_anchor",
            "variable_anchor": "backend.system_identity.mint_variable_anchor",
        },
        "behavior_anchor": {
            "anchor_id": BEHAVIOR_ID,
            "display_name": "Synthetic exact numeric equality",
            "namespace": "demo-printer",
            "role_name": None,
        },
        "status": "non_authoritative_candidate",
        "variable_anchor": {
            "anchor_id": VARIABLE_ID,
            "display_name": "Synthetic comparison variable",
            "entity_anchor_id": "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50",
            "namespace": "demo-printer",
            "role_name": None,
        },
    }
    assert variable.anchor_id == VARIABLE_ID
    assert behavior.anchor_id == BEHAVIOR_ID
    for anchor_id in (variable.anchor_id, behavior.anchor_id):
        parsed = UUID(anchor_id.split("_", 1)[1])
        assert parsed.version == 4
        assert parsed.variant == "specified in RFC 4122"
    assert "timestamp" not in manifest
    assert "machine_path" not in manifest
    assert "random_seed" not in manifest


def test_candidate_is_exactly_one_vrg_one_brg_one_parentless_bhd():
    _, variable, behavior, records = candidate_records()
    vrg, brg, bhd = records
    assert (vrg.record_id, brg.record_id, bhd.record_id) == (
        VRG_ID, BRG_ID, BHD_ID)
    assert [record.record_kind for record in records] == [
        "variable_registration",
        "behavior_registration",
        "behavior_rule_declaration",
    ]
    assert vrg.anchor == variable
    assert vrg.anchor.display_name == "Synthetic comparison variable"
    assert vrg.anchor.entity_anchor_id == "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
    assert vrg.recorded_at.isoformat() == "2026-08-30T12:00:00+00:00"
    assert vrg.authority.model_dump(mode="json") == {
        "kind": "test_fixture",
        "agent": "bh001_demo_fixture",
        "method": "manual_declaration",
    }
    assert vrg.note == "BH-001 bounded neutral synthetic participant."
    assert brg.anchor == behavior
    assert brg.participant_variable_anchor_ids == tuple(sorted((
        VARIABLE_ID, "var_b7e2d3c4f5a6172839405a6b7c8d9e0f")))
    assert brg.rule_family == "exact_numeric_equality"
    assert len(brg.evidence) == 3
    model_evidence = [evidence.record_id for evidence in brg.evidence
                      if evidence.kind == "model_record"]
    assert model_evidence == [VRG_ID,
        "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7"]
    assert [evidence.kind for evidence in brg.evidence].count(
        "owner_declaration") == 1
    assert next(item.statement for item in brg.evidence
                if item.kind == "owner_declaration") == (
        "BH-001 fixture authority explicitly registers this unordered pair "
        "of synthetic variables for the exact-numeric-equality rule family; "
        "shared ownership, names, topology, VPA associations, semantics, "
        "constraints, and observations did not create or corroborate this "
        "behavior registration.")
    assert brg.note == "BH-001 bounded synthetic registration."
    assert bhd.behavior_anchor_id == BEHAVIOR_ID
    assert bhd.context == CONTEXT
    assert bhd.rule.kind == "exact_numeric_equality"
    assert bhd.evaluation_basis == "same_acquisition_cohort"
    assert bhd.supersedes == ()
    assert len(bhd.evidence) == 2
    owner_evidence = next(item for item in bhd.evidence
                          if item.kind == "owner_declaration")
    assert owner_evidence.statement == (
        "BH-001 fixture authority explicitly declares this exact-numeric-"
        "equality relationship under the same-acquisition-cohort evaluation "
        "basis in the as-designed lifecycle view; illustrative declaration "
        "only, not an observed equality or real-machine behavior claim.")
    assert next(item.record_id for item in bhd.evidence
                if item.kind == "model_record") == BRG_ID
    assert bhd.note == "BH-001 bounded synthetic declaration."
    locks = {lock.variable_anchor_id: lock.signature
             for lock in bhd.participant_semantics}
    assert tuple(locks) == tuple(sorted((VARIABLE_ID,
        "var_b7e2d3c4f5a6172839405a6b7c8d9e0f")))
    assert {lock.quantity_kind.code for lock in locks.values()} == {"temperature"}
    assert {lock.unit.code for lock in locks.values()} == {"degree_celsius"}
    assert {lock.observation_role.code for lock in locks.values()} == {
        "synthetic_comparison", "measured_actual"}
    dumped = [record.model_dump(mode="json") for record in records]
    forbidden = ("port_anchor_id", "vpa", "constraint_anchor_id", "flow",
                 "direction", "control", "causality", "safety")
    for record in dumped:
        assert all(term not in record for term in forbidden)


def test_two_independent_disposable_ledgers_are_byte_identical(rehearsals):
    first, second = rehearsals
    for key in (
        "variable_anchor",
        "behavior_anchor",
        "records",
        "record_ids",
        "candidate_files",
        "candidate_record_bytes",
        "membership",
        "revision",
        "queries",
        "evaluator",
        "predecessor_sha256",
        "predecessor_aggregate_sha256",
        "binding_sha256",
        "interpretation_sha256",
    ):
        assert first[key] == second[key]
    assert first["artifact"] == second["artifact"]
    assert first["artifact_bytes"] == second["artifact_bytes"] == ARTIFACT_BYTES
    assert first["artifact_sha256"] == second["artifact_sha256"] == ARTIFACT_SHA256


def test_exact_membership_revision_and_record_files(rehearsals):
    first, _ = rehearsals
    assert first["record_ids"] == [VRG_ID, BRG_ID, BHD_ID]
    assert first["candidate_files"] == FILE_GOLDENS
    assert first["membership"] == sorted((
        *VP001_MEMBERSHIP, VRG_ID, BRG_ID, BHD_ID))
    assert first["revision"] == {
        "revision_id": FINAL_REVISION,
        "record_ids": first["membership"],
        "record_count": 32,
        "model_id": "demo-printer",
    }
    assert first["predecessor_aggregate_sha256"] == PREDECESSOR_AGGREGATE
    assert len(first["predecessor_sha256"]) == 29


def test_public_query_disclosure_and_historical_absence(rehearsals):
    query = rehearsals[0]["queries"]
    assert query["registration"] == {
        "status": "registered",
        "record_id": BRG_ID,
        "participant_variable_anchor_ids": [VARIABLE_ID,
            "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"],
    }
    declaration = query["declaration"]
    assert declaration["conclusion"] == "declared"
    assert declaration["lineage_summary"] == "healthy"
    assert declaration["agreement_findings"] == ["one_healthy_root"]
    assert declaration["current_declaration_ids"] == [BHD_ID]
    assert declaration["root_count"] == 1
    assert declaration["roots"] == [{
        "root_record_id": BHD_ID,
        "lineage_record_ids": [BHD_ID],
        "current_tip_ids": [BHD_ID],
        "withdrawal_ids": [],
        "lineage_health": "healthy",
        "effective_body_group_indices": [0],
    }]
    for key, opposite in (
        ("behaviors_involving_existing_variable", VARIABLE_ID),
        ("behaviors_involving_candidate_variable",
         "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"),
    ):
        reverse = query[key]
        assert reverse["status"] == "registered"
        assert len(reverse["entries"]) == 1
        assert reverse["entries"][0] == {
            "entry_index": 0,
            "behavior_anchor_id": BEHAVIOR_ID,
            "other_variable_anchor_id": opposite,
            "conclusion": "declared",
            "lineage_summary": "healthy",
            "agreement_findings": ["one_healthy_root"],
        }
    assert query["registration_assertion"]["lookup_status"] == "found"
    assert query["registration_assertion"]["activity"] is None
    assertion = query["declaration_assertion"]
    assert assertion["lookup_status"] == "found"
    assert assertion["activity"] == "current"
    assert assertion["containing_lineage_health"] == "healthy"
    assert assertion["root_record_id"] == BHD_ID
    assert assertion["successor_ids"] == []
    assert assertion["withdrawal_ids"] == []
    assert query["historical_29"] == {
        "registration_status": "not_registered",
        "declaration_conclusion": "not_registered",
        "existing_variable_status": "registered",
        "existing_variable_entry_count": 0,
        "registration_assertion_lookup": "not_found",
        "declaration_assertion_lookup": "not_found",
    }


def test_evaluator_is_honestly_not_executed_and_preserves_evidence(rehearsals):
    evaluator = rehearsals[0]["evaluator"]
    assert evaluator["execution"] == "not_executed"
    assert evaluator["computed_relation"] is None
    assert evaluator["cohort_admission"] == "not_evaluated"
    assert evaluator["direct_participant_semantic_results_equal"] is True
    assert evaluator["direct_participant_state_results_equal"] is True
    assert evaluator["direct_temporal_occurrence_equal"] is True
    assert evaluator["not_executed_reasons"] == [
        {"reason": "observation_absent", "participant_index": 0},
        {"reason": "numeric_specification_not_available", "participant_index": 0},
        {"reason": "model_quantity_kind_not_available", "participant_index": 0},
        {"reason": "model_observation_role_not_available", "participant_index": 0},
    ]
    candidate, existing = evaluator["participants"]
    assert candidate == {
        "participant_index": 0,
        "variable_anchor_id": VARIABLE_ID,
        "model_admission": "admitted",
        "observation_availability": "none_before_cutoff",
        "attachment_admission": "not_evaluated",
        "semantic_admission": "not_evaluated",
        "unit_admission": "not_evaluated",
        "lock_admission": "not_evaluated",
        "numeric_admission": "not_evaluated",
        "admission": "not_admitted",
        "refusal_reasons": [
            "observation_absent",
            "numeric_specification_not_available",
            "model_quantity_kind_not_available",
            "model_observation_role_not_available",
        ],
        "canonical_decimal": None,
    }
    assert existing["variable_anchor_id"] == "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
    assert existing["observation_availability"] == "observed"
    assert existing["attachment_admission"] == "attached"
    assert existing["semantic_admission"] == "admitted"
    assert existing["unit_admission"] == "exact"
    assert existing["lock_admission"] == "matched"
    assert existing["numeric_admission"] == "not_evaluated"
    assert existing["admission"] == "not_admitted"
    assert existing["refusal_reasons"] == []
    occurrence = evaluator["existing_participant_occurrence"]
    assert occurrence["value_json"] == "60.4"
    assert occurrence["received_at"] == "2026-08-07T20:00:18+00:00"
    assert occurrence["raw_record_id"] == "698aa72a05a317e62b62274ffcb3bbfb"


def test_binding_seam_has_one_pinned_exception_and_negative_controls(rehearsals):
    seam = rehearsals[0]["evaluator"]["binding_seam"]
    assert seam == {
        "candidate_exception": {
            "variable_anchor_id": VARIABLE_ID,
            "variable_registration_id": VRG_ID,
        },
        "candidate_binding_declaration_present": False,
        "preexisting_anchor_count": 6,
        "preexisting_anchors_exact": True,
        "second_undeclared_variable_gate_failed": True,
        "divergent_candidate_gate_failed": True,
        "candidate_model_state_anchor_agreement": "binding_declaration_absent",
    }


def test_explicit_histories_and_accepted_artifacts_remain_frozen(tmp_path):
    histories = historical_revisions()
    assert [item["record_count"] for item in histories] == [
        9, 10, 11, 14, 16, 18, 28, 29]
    assert histories[-1]["revision_id"] == BASE_REVISION
    assert histories[-1]["record_ids"] == list(VP001_MEMBERSHIP)
    assert verify_accepted_artifacts(tmp_path) == {
        "pt": {
            "bytes": 33855,
            "sha256": "53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8",
        },
        "vp": {
            "bytes": 17824,
            "sha256": "a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3",
        },
    }
    assert len(record_inventory(Path("models/demo-printer"), VP001_MEMBERSHIP)) == 29


def test_artifact_disclaimer_and_non_authoritative_scope(rehearsals):
    artifact = json.loads(rehearsals[0]["artifact"])
    assert artifact["disclaimer"] == DISCLAIMER
    assert artifact["warnings"] == list(WARNINGS)
    assert artifact["content"]["scope"]["authoritative_append_performed"] is False
    assert artifact["content"]["scope"]["records_proposed"] == {
        "variable_registration": 1,
        "behavior_registration": 1,
        "behavior_rule_declaration": 1,
        "behavior_rule_withdrawal": 0,
        "other": 0,
    }
    assert artifact["artifact_checksum"] == {
        "algorithm": "sha256",
        "scope": "content",
        "value": hashlib.sha256(
            canonical_json_bytes(artifact["content"])).hexdigest(),
    }


def test_binding_seam_rejects_stale_model_copy_and_construct(rehearsals):
    from backend.model_kernel import ModelStore

    _, variable, _, records = candidate_records()
    vrg, _, _ = records
    altered = variable.model_copy(update={
        "display_name": "Hostile substituted candidate"})
    stale_copy = vrg.model_copy(update={"anchor": altered})
    stale_construct = type(vrg).model_construct(
        **{**vrg.__dict__, "anchor": altered})

    final_material = rehearsals[0]["evaluator"]["full_result"][
        "behavior"]["material"]
    loaded = ModelStore(Path("models/demo-printer")).load()
    # The current authoritative model supplies the unchanged entity seam;
    # add only the hostile candidate into disposable mappings.
    for hostile in (stale_copy, stale_construct):
        variable_map = dict(loaded.variable_registrations_by_anchor)
        variable_map[VARIABLE_ID] = hostile
        with pytest.raises(AssertionError):
            _assert_binding_seam(
                entity_registrations=loaded.registrations_by_anchor,
                variable_registrations=variable_map,
                candidate_vrg=vrg,
            )
    assert final_material["revision"]["revision_id"] == FINAL_REVISION


def test_hash_seed_runs_reproduce_candidate_contract():
    code = """
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.model_kernel.bh001_slice_d_rehearsal import run_rehearsal
with TemporaryDirectory(dir='/tmp') as root:
    result = run_rehearsal(Path(root))
print(json.dumps({
    'artifact_bytes': result['artifact_bytes'],
    'artifact_sha256': result['artifact_sha256'],
    'record_ids': result['record_ids'],
    'candidate_files': result['candidate_files'],
    'membership': result['membership'],
    'revision': result['revision'],
}, sort_keys=True, separators=(',', ':')))
"""
    outputs = []
    for seed in ("1", "9173"):
        environment = dict(os.environ)
        environment.update({
            "PYTHONHASHSEED": seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=Path.cwd(),
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1]
    payload = json.loads(outputs[0])
    assert payload["artifact_bytes"] == ARTIFACT_BYTES
    assert payload["artifact_sha256"] == ARTIFACT_SHA256
    assert payload["record_ids"] == [VRG_ID, BRG_ID, BHD_ID]
    assert payload["candidate_files"] == FILE_GOLDENS
    assert payload["revision"]["revision_id"] == FINAL_REVISION


def test_all_append_and_copy_targets_are_disposable(tmp_path, monkeypatch):
    import shutil

    from backend.model_kernel import ModelStore

    original_append = ModelStore.append
    original_copy = shutil.copyfile
    appends = []
    copies = []

    def guarded_append(store, record):
        assert store.records_dir.resolve().is_relative_to(tmp_path.resolve())
        appends.append((store.records_dir, record.record_id))
        return original_append(store, record)

    def guarded_copy(source, target, *args, **kwargs):
        target = Path(target)
        assert target.resolve().is_relative_to(tmp_path.resolve())
        copies.append((Path(source), target))
        return original_copy(source, target, *args, **kwargs)

    monkeypatch.setattr(ModelStore, "append", guarded_append)
    monkeypatch.setattr(shutil, "copyfile", guarded_copy)
    result = run_rehearsal(
        tmp_path / "guarded",
        predecessor_copy_order=tuple(reversed(VP001_MEMBERSHIP)),
    )
    assert [record_id for _, record_id in appends] == [VRG_ID, BRG_ID, BHD_ID]
    assert len(copies) == 29
    assert result["artifact_sha256"] == ARTIFACT_SHA256


def test_rehearsal_helper_cannot_remint_and_only_appends_to_supplied_root():
    helper_path = Path("tests/model_kernel/bh001_slice_d_rehearsal.py")
    tree = ast.parse(helper_path.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "mint_variable_anchor" not in imported
    assert "mint_behavior_anchor" not in imported
    private_kernel_modules = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
        and node.module.startswith("backend.model_kernel.")
    }
    assert private_kernel_modules == set()
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert not any(
        ((isinstance(call.func, ast.Name)
          and call.func.id in {"mint_variable_anchor", "mint_behavior_anchor"})
         or (isinstance(call.func, ast.Attribute)
             and call.func.attr in {
                 "mint_variable_anchor", "mint_behavior_anchor"}))
        for call in calls)
    assert not any(
        isinstance(call.func, ast.Name)
        and call.func.id == "getattr"
        and any(isinstance(argument, ast.Constant)
                and argument.value in {
                    "mint_variable_anchor", "mint_behavior_anchor"}
                for argument in call.args)
        for call in calls)
    append_calls = [
        call for call in calls
        if isinstance(call.func, ast.Attribute)
        and call.func.attr == "append"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "store"
    ]
    assert len(append_calls) == 1
    assert isinstance(append_calls[0].func.value, ast.Name)
    assert append_calls[0].func.value.id == "store"
    assert MANIFEST_PATH.as_posix().endswith("candidate-identities.json")
