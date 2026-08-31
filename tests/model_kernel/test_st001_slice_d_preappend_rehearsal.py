"""Owner-gated ST-001 Slice D disposable pre-append rehearsal."""

import ast
import hashlib
import json
from pathlib import Path
from uuid import UUID

import pytest

from backend.model_kernel import ModelStore
from backend.model_kernel.canonical import (
    canonical_bytes as kernel_canonical_bytes,
    canonical_payload as kernel_canonical_payload,
    compute_record_id,
    verify_record_id,
)
from tests.model_kernel.st001_slice_d_rehearsal import (
    ACCEPTED_SLICE_C_HEAD,
    BASE_REVISION,
    CONSTRAINT,
    CONSTRAINT_DECLARATION,
    CONTEXT,
    DEMO_MODEL,
    DISCLAIMER,
    DISCLOSURE_PATH,
    MANIFEST_PATH,
    SUBJECT_ENTITY,
    WARNINGS,
    candidate_records,
    canonical_json_bytes,
    manifest_content,
    reproduction_summary,
    run_rehearsal,
    sha256_bytes,
)
from tests.model_kernel.test_demo_model import BH001_MEMBERSHIP


STATE_ID = "sta_ec739d80d5a843d28a91f4cf96de3883"
SRG_ID = "srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a"
STD_ID = "std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0"
FINAL_REVISION = (
    "mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41")
MANIFEST_BYTES = 31834
MANIFEST_SHA256 = (
    "990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7")
ARTIFACT_BYTES = 510943
ARTIFACT_SHA256 = (
    "23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9")
PREDECESSOR_AGGREGATE = (
    "eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58")
RECORD_CONTRACTS = {
    SRG_ID: {
        "canonical_payload_bytes": 1012,
        "canonical_payload_sha256": (
            "ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a"),
        "bytes": 1278,
        "sha256": (
            "a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781"),
    },
    STD_ID: {
        "canonical_payload_bytes": 1169,
        "canonical_payload_sha256": (
            "d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0"),
        "bytes": 1474,
        "sha256": (
            "5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6"),
    },
}


@pytest.fixture(scope="module")
def rehearsals(tmp_path_factory):
    roots = (
        tmp_path_factory.mktemp("st001-rehearsal-one"),
        tmp_path_factory.mktemp("st001-rehearsal-two"),
    )
    first = run_rehearsal(roots[0])
    second = run_rehearsal(
        roots[1], predecessor_copy_order=tuple(reversed(BH001_MEMBERSHIP)))
    return first, second


def test_manifest_and_disclosure_are_exact_canonical_owner_gate_artifacts():
    payload, content, anchor, raw = manifest_content()
    assert len(raw) == MANIFEST_BYTES
    assert sha256_bytes(raw) == MANIFEST_SHA256
    assert raw == canonical_json_bytes(payload)
    assert content["accepted_source_head"] == ACCEPTED_SLICE_C_HEAD
    assert content["base_model_revision"] == BASE_REVISION
    assert anchor.anchor_id == STATE_ID
    assert anchor.namespace == "demo-printer"
    assert anchor.display_name == "Synthetic Region Alpha"
    assert anchor.role_name is None
    parsed = UUID(anchor.anchor_id.removeprefix("sta_"))
    assert parsed.version == 4
    assert parsed.variant == "specified in RFC 4122"

    disclosure = DISCLOSURE_PATH.read_bytes()
    assert len(disclosure) == ARTIFACT_BYTES
    assert sha256_bytes(disclosure) == ARTIFACT_SHA256
    assert json.loads(disclosure)["schema_version"] == "1"


def test_candidate_semantics_are_exact_and_neutrally_worded():
    _, content, anchor, _ = manifest_content()
    semantic = content["semantic_inputs"]
    registration, declaration = content["candidate_contract"]["records"]
    assert registration["record_id"] == SRG_ID
    assert registration["anchor"] == anchor.model_dump(mode="json")
    assert registration["subject_entity_anchor_id"] == SUBJECT_ENTITY
    assert registration["condition_constraint_anchor_ids"] == [CONSTRAINT]
    assert registration["condition_family"] == "all_of_constraints"
    assert declaration["record_id"] == STD_ID
    assert declaration["state_anchor_id"] == STATE_ID
    assert declaration["context"] == CONTEXT.model_dump(mode="json")
    assert declaration["conditions"] == [{
        "constraint_anchor_id": CONSTRAINT,
        "constraint_declaration_record_id": CONSTRAINT_DECLARATION,
    }]
    assert declaration["evaluation_basis"] == (
        "independent_latest_at_or_before_cutoff")
    assert declaration["supersedes"] == []
    assert semantic["anchor_allocation"]["api"] == (
        "backend.system_identity.mint_state_anchor")
    assert "exactly once" in semantic["anchor_allocation"]["statement"]

    wording = json.dumps({
        "anchor": content["state_anchor"],
        "registration_evidence": semantic["state_registration"]["evidence"],
        "registration_note": semantic["state_registration"]["note"],
        "declaration_evidence": semantic["state_declaration"]["evidence"],
        "declaration_note": semantic["state_declaration"]["note"],
    }).lower()
    for forbidden in (
        "hot", "ready", "operating", "normal", "safe", "fault", "alarm",
        "target", "command", "control", "sensor", "actuator", "health",
        "correctness", "diagnosis", "required action", "recommended action",
    ):
        assert forbidden not in wording


def test_disclosed_canonical_contract_is_the_normative_kernel_contract():
    _, content, anchor, _ = manifest_content()
    records = candidate_records(anchor)
    contracts = {
        row["record_id"]: row
        for row in content["candidate_contract"]["record_contracts"]
    }
    for record in records:
        disclosed = contracts[record.record_id]
        normative_payload = kernel_canonical_payload(record)
        normative_bytes = kernel_canonical_bytes(record)
        assert disclosed["canonical_payload"] == normative_payload
        assert disclosed["canonical_bytes"].encode("utf-8") == normative_bytes
        assert disclosed["canonical_payload_bytes"] == len(normative_bytes)
        assert disclosed["canonical_payload_sha256"] == sha256_bytes(
            normative_bytes)
        assert disclosed["canonical_payload_sha256"] == (
            record.record_id.split("_", 1)[1])
        assert compute_record_id(record) == record.record_id
        assert verify_record_id(record) is True

        legacy_payload = record.model_dump(
            mode="json", exclude={"record_id"})
        legacy_bytes = json.dumps(
            legacy_payload, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        assert legacy_bytes != normative_bytes
        assert b'"recorded_at":"2026-08-31T12:' in legacy_bytes
        assert legacy_bytes.count(b'Z"') == 1
        assert b'Z"' not in normative_bytes
        assert normative_bytes.count(b'+00:00"') == 1
        assert legacy_bytes.replace(b'Z"', b'+00:00"') == normative_bytes

    assert content["canonicalization"] == {
        "module": "backend.model_kernel.canonical",
        "payload_function": "canonical_payload",
        "bytes_function": "canonical_bytes",
        "record_id_function": "compute_record_id",
        "verification_function": "verify_record_id",
        "utc_representation": "+00:00",
        "statement": (
            "Every field named canonical is derived directly from the model "
            "kernel's normative canonical_payload(record) or "
            "canonical_bytes(record) result."
        ),
    }

    artifact = json.loads(DISCLOSURE_PATH.read_bytes())
    artifact_records = {
        row["record"]["record_id"]: row
        for row in artifact["content"]["model"]["candidate_records"]
    }
    for record in records:
        disclosed = artifact_records[record.record_id]
        assert disclosed["canonical_payload"] == kernel_canonical_payload(
            record)
        assert disclosed["canonical_bytes"].encode("utf-8") == (
            kernel_canonical_bytes(record))
        assert disclosed["canonical_payload_sha256"] == (
            record.record_id.split("_", 1)[1])
        assert disclosed["record_id_verification"] == {
            "computed_record_id": record.record_id,
            "verified": True,
        }


def test_exact_record_bytes_ids_membership_and_revision(rehearsals):
    first, second = rehearsals
    assert first["record_ids"] == second["record_ids"] == [SRG_ID, STD_ID]
    assert first["append_order"] == second["append_order"] == [SRG_ID, STD_ID]
    assert first["membership"] == second["membership"] == sorted(
        (*BH001_MEMBERSHIP, SRG_ID, STD_ID))
    assert first["revision"] == second["revision"]
    assert first["revision"]["record_count"] == 34
    assert first["revision"]["revision_id"] == FINAL_REVISION
    assert set(first["membership"]) - set(BH001_MEMBERSHIP) == {
        SRG_ID, STD_ID}

    for row in first["record_contracts"]:
        expected = RECORD_CONTRACTS[row["record_id"]]
        assert {key: row[key] for key in expected} == expected
    assert first["record_contracts"] == second["record_contracts"]
    assert first["candidate_record_bytes"] == second[
        "candidate_record_bytes"]


def test_public_kernel_query_contract_is_exact(rehearsals):
    query = rehearsals[0]["queries"]
    assert query["summary"] == {
        "lookup_status": "registered",
        "declaration_conclusion": "declared",
        "lineage_summary": "healthy",
        "agreement_findings": ["one_healthy_root"],
        "root_count": 1,
        "entity_entry_count": 1,
        "registration_assertion_lookup": "found",
        "declaration_assertion_activity": "current",
        "declaration_assertion_lineage_health": "healthy",
    }
    declaration = query["state_declaration"]
    assert declaration["current_declaration_indices"]
    assert len(declaration["roots"]) == 1
    root = declaration["roots"][0]
    assert root["lineage_health"] == "healthy"
    assert len(root["current_tip_indices"]) == 1
    assert root["withdrawal_indices"] == []
    historical = query["historical_32"]
    assert historical["state"]["status"] == "not_registered"
    assert historical["state_declaration"]["conclusion"] == "not_registered"
    assert historical["states_of_entity"]["entries"] == []
    assert historical["registration_assertion"]["lookup_status"] == "not_found"
    assert historical["declaration_assertion"]["lookup_status"] == "not_found"


def test_direct_cn_and_state_classification_are_exact(rehearsals):
    evaluation = rehearsals[0]["evaluation"]
    assert evaluation["summary"] == {
        "constraint_status": "declared",
        "current_constraint_declaration_id": CONSTRAINT_DECLARATION,
        "observed_decimal": "60.4",
        "predicate": {
            "kind": "upper_bound",
            "upper": {"value": "80", "inclusion": "inclusive"},
        },
        "constraint_verdict": "satisfied",
        "state_conclusion": "declared",
        "state_lineage_summary": "healthy",
        "declaration_alignment": "exact_current",
        "condition_outcome": "satisfied",
        "condition_coverage": "complete",
        "temporal_alignment": "not_asserted",
        "execution": "executed",
        "refusals": [],
        "computed_match": "matches",
    }
    classification = evaluation["state_classification"]
    assert classification["constraint_evaluations"] == [
        evaluation["direct_constraint_evaluation"]]
    assert classification["refusals"] == []
    assert evaluation["occurrence"]["value_json"] == "60.4"
    assert evaluation["occurrence"]["received_at"] == (
        "2026-08-07T20:00:18Z")
    assert evaluation["provenance_axes"]["temporal_cutoff"] == (
        "2026-08-07T20:30:00+00:00")
    assert evaluation["provenance_axes"]["declaration_recorded_at"] == (
        "2026-08-31T12:01:00+00:00")
    assert "neither declaration existence" in evaluation[
        "provenance_axes"]["statement"]


def test_two_roots_and_artifact_are_directly_byte_identical(rehearsals):
    first, second = rehearsals
    assert reproduction_summary(first) == reproduction_summary(second)
    assert first["artifact"] == second["artifact"] == DISCLOSURE_PATH.read_bytes()
    assert first["artifact_bytes"] == second["artifact_bytes"] == ARTIFACT_BYTES
    assert first["artifact_sha256"] == second["artifact_sha256"] == (
        ARTIFACT_SHA256)
    assert first["predecessor_aggregate_sha256"] == second[
        "predecessor_aggregate_sha256"] == PREDECESSOR_AGGREGATE
    assert first["runtime_evidence_unchanged"] is True
    assert second["runtime_evidence_unchanged"] is True


def test_artifact_disclaimer_checksum_limitations_and_non_inference():
    payload = json.loads(DISCLOSURE_PATH.read_bytes())
    assert payload["disclaimer"] == DISCLAIMER
    assert payload["warnings"] == list(WARNINGS)
    content = payload["content"]
    assert payload["artifact_checksum"] == {
        "algorithm": "sha256",
        "scope": "content",
        "value": sha256_bytes(canonical_json_bytes(content)),
    }
    assert content["scope"]["authoritative_append_performed"] is False
    assert content["scope"]["candidate_records"] == {
        "state_registration": 1,
        "state_declaration": 1,
        "state_declaration_withdrawal": 0,
        "correction": 0,
        "second_root": 0,
        "other": 0,
    }
    assert "does not independently authenticate" in content[
        "raw_authenticity_limitation"]
    assert "does not persist it as state truth" in payload["warnings"][1]


def test_explicit_histories_predecessors_and_accepted_artifacts_are_frozen(
        rehearsals):
    first = rehearsals[0]
    assert len(first["predecessor_sha256"]) == 32
    assert first["predecessor_aggregate_sha256"] == PREDECESSOR_AGGREGATE
    artifact = json.loads(first["artifact"])
    assert [row["record_count"] for row in
            artifact["content"]["historical_replay"]] == [
                9, 10, 11, 14, 16, 18, 28, 29, 32]
    assert first["accepted_artifacts"] == {
        "pt": {
            "bytes": 33855,
            "sha256": (
                "53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8"),
        },
        "vp": {
            "bytes": 17824,
            "sha256": (
                "a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3"),
        },
        "bh": {
            "bytes": 122406,
            "sha256": (
                "4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3"),
        },
    }


def test_authoritative_ledger_remains_exactly_32_and_has_no_state_records():
    loaded = ModelStore(DEMO_MODEL).load()
    assert loaded.revision.revision_id == BASE_REVISION
    assert loaded.revision.record_count == 32
    assert loaded.revision.record_ids == BH001_MEMBERSHIP
    assert not loaded.state_registrations
    assert not loaded.state_declarations
    assert not loaded.state_declaration_withdrawals
    for record_id in (SRG_ID, STD_ID):
        assert not (DEMO_MODEL / "records" / f"{record_id}.json").exists()


def test_rehearsal_helper_cannot_remint_and_imports_only_normative_canonical():
    helper = Path("tests/model_kernel/st001_slice_d_rehearsal.py")
    tree = ast.parse(helper.read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "mint_state_anchor" not in imported_names
    assert not any(
        isinstance(node, ast.Call)
        and ((isinstance(node.func, ast.Name)
              and node.func.id == "mint_state_anchor")
             or (isinstance(node.func, ast.Attribute)
                 and node.func.attr == "mint_state_anchor"))
        for node in ast.walk(tree)
    )
    assert {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
        and node.module.startswith("backend.model_kernel.")
    } == {"backend.model_kernel.canonical"}


def test_manifest_and_artifact_hashes_are_not_accidental_constants():
    assert hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() == (
        MANIFEST_SHA256)
    assert hashlib.sha256(DISCLOSURE_PATH.read_bytes()).hexdigest() == (
        ARTIFACT_SHA256)
