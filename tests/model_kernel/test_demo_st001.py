"""ST-001 Slice D: approved authoritative two-record state fixture."""

import hashlib
import json
from pathlib import Path

import pytest

from backend.model_kernel import ModelQueries, ModelStore
from backend.model_kernel.canonical import (
    canonical_bytes,
    compute_record_id,
    verify_record_id,
)
from tests.model_kernel.st001_slice_d_rehearsal import (
    BASE_REVISION,
    CONTEXT,
    DEMO_MODEL,
    DISCLAIMER,
    DISCLOSURE_PATH,
    MANIFEST_PATH,
    WARNINGS,
    candidate_records,
    manifest_content,
    reproduction_summary,
    run_rehearsal,
    sha256_bytes,
)
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CURRENT_REVISION,
    FL001_MEMBERSHIP,
    PRE_FL001_REVISION,
    ST001_MEMBERSHIP,
    ST001_MODEL_RECORDS,
)


STATE_ID = "sta_ec739d80d5a843d28a91f4cf96de3883"
SRG_ID, STD_ID = ST001_MODEL_RECORDS
MANIFEST_SHA256 = (
    "990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7")
DISCLOSURE_SHA256 = (
    "23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9")
PREDECESSOR_AGGREGATE_SHA256 = (
    "eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58")
FILE_CONTRACTS = {
    SRG_ID: {
        "bytes": 1278,
        "sha256": (
            "a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781"),
    },
    STD_ID: {
        "bytes": 1474,
        "sha256": (
            "5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6"),
    },
}


@pytest.fixture(scope="module")
def reproduced(tmp_path_factory):
    first = run_rehearsal(tmp_path_factory.mktemp("st001-final-one"))
    second = run_rehearsal(
        tmp_path_factory.mktemp("st001-final-two"),
        predecessor_copy_order=tuple(reversed(BH001_MEMBERSHIP)),
    )
    return first, second


def test_owner_approved_gate_artifacts_remain_byte_frozen():
    assert hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() == (
        MANIFEST_SHA256)
    assert hashlib.sha256(DISCLOSURE_PATH.read_bytes()).hexdigest() == (
        DISCLOSURE_SHA256)
    payload = json.loads(DISCLOSURE_PATH.read_bytes())
    assert payload["disclaimer"] == DISCLAIMER
    assert payload["warnings"] == list(WARNINGS)
    # This remains the approved pre-append disclosure, not a rewritten claim.
    assert payload["content"]["scope"]["authoritative_append_performed"] is False


def test_exact_authoritative_membership_revision_and_historical_boundary():
    store = ModelStore(DEMO_MODEL)
    current = store.load()
    predecessor = store.replay(BH001_MEMBERSHIP)
    accepted_st001 = store.replay(ST001_MEMBERSHIP)
    assert current.revision.record_ids == FL001_MEMBERSHIP
    assert current.revision.record_count == 36
    assert current.revision.revision_id == CURRENT_REVISION
    assert accepted_st001.revision.record_ids == ST001_MEMBERSHIP
    assert accepted_st001.revision.record_count == 34
    assert accepted_st001.revision.revision_id == PRE_FL001_REVISION
    assert predecessor.revision.record_ids == BH001_MEMBERSHIP
    assert predecessor.revision.record_count == 32
    assert predecessor.revision.revision_id == BASE_REVISION
    assert set(ST001_MEMBERSHIP) - set(BH001_MEMBERSHIP) == set(
        ST001_MODEL_RECORDS)
    assert len(current.state_registrations) == 1
    assert len(current.state_declarations) == 1
    assert not current.state_declaration_withdrawals


def test_authoritative_records_equal_the_frozen_semantics_and_bytes():
    _, content, anchor, _ = manifest_content()
    built = candidate_records(anchor)
    loaded = ModelStore(DEMO_MODEL).load()
    assert anchor.anchor_id == STATE_ID
    assert tuple(record.record_id for record in built) == ST001_MODEL_RECORDS
    assert content["candidate_contract"]["append_order"] == list(
        ST001_MODEL_RECORDS)
    for record in built:
        assert loaded.records[record.record_id] == record
        assert compute_record_id(record) == record.record_id
        assert verify_record_id(record) is True
        assert sha256_bytes(canonical_bytes(record)) == record.record_id.split(
            "_", 1)[1]
        raw = (DEMO_MODEL / "records" / f"{record.record_id}.json").read_bytes()
        expected = FILE_CONTRACTS[record.record_id]
        assert len(raw) == expected["bytes"]
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"]
        contract = next(
            row for row in content["candidate_contract"]["record_contracts"]
            if row["record_id"] == record.record_id)
        assert raw.decode("utf-8") == contract["stored_json"]


def test_public_kernel_disclosures_are_the_approved_healthy_single_root():
    queries = ModelQueries(ModelStore(DEMO_MODEL).load())
    state = queries.state(STATE_ID)
    declaration = queries.state_declaration(STATE_ID, context=CONTEXT)
    reverse = queries.states_of_entity(
        "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50", context=CONTEXT)
    registration_assertion = queries.state_assertion(SRG_ID)
    declaration_assertion = queries.state_assertion(STD_ID)
    assert state.status == "registered"
    assert declaration.conclusion == "declared"
    assert declaration.lineage_summary == "healthy"
    assert declaration.agreement_findings == ("one_healthy_root",)
    assert len(reverse.entries) == 1
    assert registration_assertion.lookup_status == "found"
    assert declaration_assertion.lookup_status == "found"
    assert declaration_assertion.activity == "current"
    assert declaration_assertion.containing_lineage_health == "healthy"


def test_two_independent_reproductions_equal_the_approved_contract(reproduced):
    first, second = reproduced
    assert reproduction_summary(first) == reproduction_summary(second)
    assert first["record_ids"] == second["record_ids"] == list(
        ST001_MODEL_RECORDS)
    assert first["append_order"] == second["append_order"] == list(
        ST001_MODEL_RECORDS)
    assert first["membership"] == second["membership"] == list(
        ST001_MEMBERSHIP)
    assert first["revision"]["revision_id"] == PRE_FL001_REVISION
    assert first["predecessor_aggregate_sha256"] == (
        PREDECESSOR_AGGREGATE_SHA256)
    assert first["artifact"] == second["artifact"] == DISCLOSURE_PATH.read_bytes()
    assert first["artifact_sha256"] == second["artifact_sha256"] == (
        DISCLOSURE_SHA256)
    assert first["queries"]["summary"] == {
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
    assert first["evaluation"]["summary"]["constraint_verdict"] == "satisfied"
    assert first["evaluation"]["summary"]["condition_coverage"] == "complete"
    assert first["evaluation"]["summary"]["temporal_alignment"] == (
        "not_asserted")
    assert first["evaluation"]["summary"]["execution"] == "executed"
    assert first["evaluation"]["summary"]["computed_match"] == "matches"
    assert first["evaluation"]["summary"]["refusals"] == []


def test_no_unapproved_state_record_or_second_root_exists():
    paths = tuple((DEMO_MODEL / "records").glob("*.json"))
    assert {path.stem for path in paths if path.name.startswith("srg_")} == {
        SRG_ID}
    assert {path.stem for path in paths if path.name.startswith("std_")} == {
        STD_ID}
    assert not any(path.name.startswith("stw_") for path in paths)
    loaded = ModelStore(DEMO_MODEL).load()
    assert set(loaded.state_registrations_by_anchor) == {STATE_ID}
