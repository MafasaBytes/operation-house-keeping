"""BH-001 Slice D: approved 32-record fixture and disclosure artifact."""

import hashlib
import json
from pathlib import Path

import pytest

from backend.model_kernel import ModelStore
from tests.model_kernel.bh001_slice_d_rehearsal import (
    DISCLAIMER,
    WARNINGS,
    _assert_binding_seam,
    authoritative_reproduction,
    candidate_records,
)
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    BH001_MODEL_RECORDS,
    PRE_ST001_REVISION,
    PRE_BH001_REVISION,
    VP001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")
MANIFEST = Path(
    "docs/superpowers/reports/"
    "2026-08-30-bh001-slice-d-candidate-identities.json")
MANIFEST_SHA256 = (
    "8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07")
COMPLETION_REPORT = Path(
    "docs/superpowers/reports/"
    "2026-08-30-bh001-slice-d-completion-report.md")
COMPLETION_REPORT_SHA256 = (
    "3d0485e92dff57df43f31fcd2774acf6099f4f61102246dc6d8777c7ee326b5a")
IMPLEMENTATION_HEAD = "6fdf4d009538ddd169c1342508a104c9d61560b6"
VARIABLE_ID = "var_ab2d312466054c20b0ac764e9bc0114e"
BEHAVIOR_ID = "bhv_80e21f1682e449ca9c65a5e2ee051ea0"
VRG_ID, BRG_ID, BHD_ID = BH001_MODEL_RECORDS
PREDECESSOR_AGGREGATE_SHA256 = (
    "962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf")
ARTIFACT_BYTES = 122406
ARTIFACT_SHA256 = (
    "4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3")
FINAL_STATUS = (
    "BH-001 complete, owner accepted, adversarially reviewed, full-suite "
    "verified, and dual-clean-checkout verified."
)
FILE_GOLDENS = {
    f"{VRG_ID}.json": {
        "bytes": 630,
        "sha256": (
            "0652fd7ca32de43d3e21c5a41a5117eb3c19d2a469ffa30f37b407f91937e285"),
    },
    f"{BRG_ID}.json": {
        "bytes": 1376,
        "sha256": (
            "19068707d3bb5423eab4db189208d85749ef18cc3447135d8cfa4ea7f0e89edb"),
    },
    f"{BHD_ID}.json": {
        "bytes": 2333,
        "sha256": (
            "fa1a40272d100eb81cc15e64cff782a654b3369a91da62bc36b1f26a2cf655cf"),
    },
}


@pytest.fixture(scope="module")
def disclosure(tmp_path_factory):
    return authoritative_reproduction(
        tmp_path_factory.mktemp("bh001-authoritative"))


def test_owner_approved_manifest_remains_byte_frozen():
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256
    manifest, variable, behavior, _ = candidate_records()
    assert manifest["status"] == "non_authoritative_candidate"
    assert variable.anchor_id == VARIABLE_ID
    assert behavior.anchor_id == BEHAVIOR_ID


def test_owner_accepted_completion_report_remains_byte_frozen():
    assert hashlib.sha256(COMPLETION_REPORT.read_bytes()).hexdigest() == (
        COMPLETION_REPORT_SHA256)


def test_exact_three_record_append_and_explicit_revision(disclosure):
    store = ModelStore(DEMO_MODEL)
    current = store.replay(BH001_MEMBERSHIP)
    predecessor = store.replay(VP001_MEMBERSHIP)
    assert current.revision.revision_id == PRE_ST001_REVISION
    assert current.revision.record_ids == BH001_MEMBERSHIP
    assert current.revision.record_count == 32
    assert predecessor.revision.revision_id == PRE_BH001_REVISION
    assert predecessor.revision.record_count == 29
    assert set(BH001_MEMBERSHIP) - set(VP001_MEMBERSHIP) == set(
        BH001_MODEL_RECORDS)
    assert tuple(disclosure["record_ids"]) == BH001_MODEL_RECORDS
    assert tuple(disclosure["membership"]) == BH001_MEMBERSHIP
    assert disclosure["revision"] == current.revision.model_dump(mode="json")

    added = [current.records[record_id] for record_id in BH001_MODEL_RECORDS]
    assert [record.record_kind for record in added] == [
        "variable_registration",
        "behavior_registration",
        "behavior_rule_declaration",
    ]
    assert not current.behavior_rule_withdrawals
    assert added[2].supersedes == ()
    assert len(current.behavior_rule_root_by_id) == 1


def test_canonical_records_and_files_equal_the_approved_contract(disclosure):
    _, variable, behavior, built = candidate_records()
    assert disclosure["variable_anchor"] == variable.model_dump(mode="json")
    assert disclosure["behavior_anchor"] == behavior.model_dump(mode="json")
    assert disclosure["records"] == [
        record.model_dump(mode="json") for record in built]
    assert disclosure["candidate_files"] == FILE_GOLDENS
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(paths) == 34
    for filename, expected in FILE_GOLDENS.items():
        raw = (DEMO_MODEL / "records" / filename).read_bytes()
        assert len(raw) == expected["bytes"]
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"]
        assert raw == disclosure["candidate_record_bytes"][filename]


def test_kernel_queries_disclose_one_current_healthy_declaration(disclosure):
    queries = disclosure["queries"]
    assert queries["registration"] == {
        "status": "registered",
        "record_id": BRG_ID,
        "participant_variable_anchor_ids": [
            VARIABLE_ID,
            "var_b7e2d3c4f5a6172839405a6b7c8d9e0f",
        ],
    }
    declaration = queries["declaration"]
    assert declaration["conclusion"] == "declared"
    assert declaration["lineage_summary"] == "healthy"
    assert declaration["agreement_findings"] == ["one_healthy_root"]
    assert declaration["current_declaration_ids"] == [BHD_ID]
    assert declaration["root_count"] == 1
    [root] = declaration["roots"]
    assert root == {
        "root_record_id": BHD_ID,
        "lineage_record_ids": [BHD_ID],
        "current_tip_ids": [BHD_ID],
        "withdrawal_ids": [],
        "lineage_health": "healthy",
        "effective_body_group_indices": [0],
    }
    for key in (
        "behaviors_involving_existing_variable",
        "behaviors_involving_candidate_variable",
    ):
        assert queries[key]["status"] == "registered"
        assert len(queries[key]["entries"]) == 1
        assert queries[key]["entries"][0]["conclusion"] == "declared"
        assert queries[key]["entries"][0]["lineage_summary"] == "healthy"
    assertion = queries["declaration_assertion"]
    assert assertion["lookup_status"] == "found"
    assert assertion["activity"] == "current"
    assert assertion["root_record_id"] == BHD_ID
    assert assertion["successor_ids"] == []
    assert assertion["withdrawal_ids"] == []


def test_explicit_29_record_history_discloses_structured_absence(disclosure):
    assert disclosure["queries"]["historical_29"] == {
        "registration_status": "not_registered",
        "declaration_conclusion": "not_registered",
        "existing_variable_status": "registered",
        "existing_variable_entry_count": 0,
        "registration_assertion_lookup": "not_found",
        "declaration_assertion_lookup": "not_found",
    }


def test_evaluator_is_honestly_not_executed_and_preserves_existing_evidence(
        disclosure):
    evaluator = disclosure["evaluator"]
    assert evaluator["execution"] == "not_executed"
    assert evaluator["computed_relation"] is None
    assert evaluator["cohort_admission"] == "not_evaluated"
    candidate, existing = evaluator["participants"]
    assert candidate["variable_anchor_id"] == VARIABLE_ID
    assert candidate["refusal_reasons"] == [
        "observation_absent",
        "numeric_specification_not_available",
        "model_quantity_kind_not_available",
        "model_observation_role_not_available",
    ]
    assert evaluator["not_executed_reasons"] == [
        {"participant_index": 0, "reason": reason}
        for reason in candidate["refusal_reasons"]
    ]
    assert existing["variable_anchor_id"] == (
        "var_b7e2d3c4f5a6172839405a6b7c8d9e0f")
    assert existing["observation_availability"] == "observed"
    assert existing["attachment_admission"] == "attached"
    assert existing["semantic_admission"] == "admitted"
    assert existing["unit_admission"] == "exact"
    assert existing["lock_admission"] == "matched"
    assert existing["refusal_reasons"] == []
    occurrence = evaluator["existing_participant_occurrence"]
    assert occurrence["value_json"] == "60.4"
    assert occurrence["received_at"] == "2026-08-07T20:00:18+00:00"
    assert evaluator["direct_participant_semantic_results_equal"] is True
    assert evaluator["direct_participant_state_results_equal"] is True
    assert evaluator["direct_temporal_occurrence_equal"] is True


def test_binding_seam_has_one_exact_exception_and_hostile_twins_fail(
        disclosure):
    seam = disclosure["evaluator"]["binding_seam"]
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
        "candidate_model_state_anchor_agreement": (
            "binding_declaration_absent"),
    }
    _, variable, _, records = candidate_records()
    vrg, _, _ = records
    altered = variable.model_copy(update={"display_name": "Hostile twin"})
    stale_records = (
        vrg.model_copy(update={"anchor": altered}),
        type(vrg).model_construct(**{**vrg.__dict__, "anchor": altered}),
    )
    loaded = ModelStore(DEMO_MODEL).load()
    for hostile in stale_records:
        variable_map = dict(loaded.variable_registrations_by_anchor)
        variable_map[VARIABLE_ID] = hostile
        with pytest.raises(AssertionError):
            _assert_binding_seam(
                entity_registrations=loaded.registrations_by_anchor,
                variable_registrations=variable_map,
                candidate_vrg=vrg,
            )


def test_binding_seam_rejects_each_omitted_preexisting_anchor():
    _, _, _, records = candidate_records()
    vrg, _, _ = records
    loaded = ModelStore(DEMO_MODEL).load()
    entity_map = dict(loaded.registrations_by_anchor)
    variable_map = dict(loaded.variable_registrations_by_anchor)
    preexisting_ids = sorted(
        set(entity_map) | (set(variable_map) - {VARIABLE_ID}))
    assert len(preexisting_ids) == 6
    for omitted in preexisting_ids:
        hostile_entities = dict(entity_map)
        hostile_variables = dict(variable_map)
        hostile_entities.pop(omitted, None)
        hostile_variables.pop(omitted, None)
        with pytest.raises(AssertionError):
            _assert_binding_seam(
                entity_registrations=hostile_entities,
                variable_registrations=hostile_variables,
                candidate_vrg=vrg,
            )


def test_predecessors_and_accepted_artifacts_remain_byte_frozen(disclosure):
    assert disclosure["predecessor_aggregate_sha256"] == (
        PREDECESSOR_AGGREGATE_SHA256)
    assert len(disclosure["predecessor_sha256"]) == 29
    assert disclosure["artifact_bytes"] == ARTIFACT_BYTES
    assert disclosure["artifact_sha256"] == ARTIFACT_SHA256
    artifact = json.loads(disclosure["artifact"])
    assert artifact["schema_version"] == "1"
    assert artifact["disclaimer"] == DISCLAIMER
    assert artifact["warnings"] == list(WARNINGS)
    assert artifact["content"]["scope"][
        "authoritative_append_performed"] is False
    assert artifact["content"]["scope"]["records_proposed"] == {
        "variable_registration": 1,
        "behavior_registration": 1,
        "behavior_rule_declaration": 1,
        "behavior_rule_withdrawal": 0,
        "other": 0,
    }
    assert artifact["content"]["preservation"]["pt_artifact"] == {
            "bytes": 33855,
            "sha256": (
                "53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8"),
        }
    assert artifact["content"]["preservation"]["vp_artifact"] == {
            "bytes": 17824,
            "sha256": (
                "a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3"),
        }


def test_living_documentation_pins_final_slice_d_status_and_limits():
    paths = (
        Path("CLAUDE.md"),
        Path("backend/model_kernel/README.md"),
        Path("backend/model_state/README.md"),
        Path("backend/behavior_evaluation/README.md"),
        Path("backend/system_identity/README.md"),
        Path("models/README.md"),
        Path("models/demo-printer/README.md"),
        Path("docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"),
        Path("docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md"),
    )
    for path in paths:
        normalized = " ".join(path.read_text(encoding="utf-8").split())
        assert PRE_ST001_REVISION in normalized, path
        assert FINAL_STATUS in normalized, path
    demo = (Path("models/demo-printer/README.md").read_text(encoding="utf-8"))
    normalized_demo = " ".join(demo.split())
    assert DISCLAIMER in normalized_demo
    assert "not evidence that the declared relation is false" in normalized_demo
    assert "no BHW, successor, correction, fork, or second root" in normalized_demo
    assert "pre-append candidate disclosure artifact" in normalized_demo
    assert "describe the frozen rehearsal scope, not the current" in normalized_demo


def test_final_owner_acceptance_is_recorded_in_every_applicable_plan_and_matrix():
    paths = (
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-a-implementation-plan.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-b-implementation-plan.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md"),
    )
    for path in paths:
        normalized = " ".join(path.read_text(encoding="utf-8").split())
        assert FINAL_STATUS in normalized, path
        assert IMPLEMENTATION_HEAD in normalized, path


def test_final_acceptance_pins_the_accepted_boundary_without_changing_meaning():
    for path in (
        Path("CLAUDE.md"),
        Path("docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"),
        Path("docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md"),
        Path("docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md"),
    ):
        normalized = " ".join(path.read_text(encoding="utf-8").split())
        assert IMPLEMENTATION_HEAD in normalized, path
        assert COMPLETION_REPORT_SHA256 in normalized, path
    specification = Path(
        "docs/superpowers/specs/"
        "2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"
    ).read_text(encoding="utf-8")
    normalized_specification = " ".join(specification.split())
    for accepted_value in (
        VARIABLE_ID,
        BEHAVIOR_ID,
        VRG_ID,
        BRG_ID,
        BHD_ID,
        PREDECESSOR_AGGREGATE_SHA256,
        ARTIFACT_SHA256,
        "53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8",
        "a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3",
    ):
        assert accepted_value in specification
    assert "exactly 32 records" in normalized_specification
    assert "remains `not_executed`" in normalized_specification
    assert "does not convert it into observed equality" in normalized_specification
