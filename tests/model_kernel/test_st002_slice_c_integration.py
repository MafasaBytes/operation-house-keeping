"""ST-002 Slice C integrated disposable-world acceptance gates."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_bytes, verify_record_id
from tests.model_kernel.builders import ENT_A
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    TRANSITION_A,
    TRANSITION_B,
    VIEW_INDEPENDENT,
    transition_declaration,
)
from tests.model_kernel.st002_slice_c_reproduction import (
    FIXTURE_DISCLAIMER,
    reproduce,
)


EXPECTED_ARTIFACT_SHA256 = (
    "fe7112a210d881f4f0533298ab4002497a1370f913348f4e59d2331db2735997")
EXPECTED_STORED_AGGREGATE_SHA256 = (
    "93b58616bbd5311d0cde4db313abf2c59667263735f38ae76556d7253bac4c90")
EXPECTED_REVISION = (
    "mrv_1fc769567e792989d47054c65608407c2d7c36ae05a06a924a801c39700ac7fd")


def _queries(reproduction, membership="final"):
    return kernel.ModelQueries(reproduction.store.replay(
        reproduction.memberships[membership]))


def _group_for_pin(result, record_id):
    return next(group for group in result.effective_body_groups
                if group.from_endpoint.declaration.record_id == record_id)


def test_disposable_positive_worlds_reproduce_byte_identically(tmp_path):
    forward = reproduce(tmp_path / "forward", reverse_independent=False)
    reverse = reproduce(tmp_path / "reverse", reverse_independent=True)

    assert forward.artifact_bytes == reverse.artifact_bytes
    assert forward.query_bytes == reverse.query_bytes
    assert forward.stored_bytes == reverse.stored_bytes
    assert forward.memberships == reverse.memberships
    assert forward.loaded.revision == reverse.loaded.revision
    for name in (
        "transition_registrations",
        "transition_registrations_by_anchor",
        "transition_anchor_ids_by_subject_entity",
        "transition_registration_id_by_ordered_subject_endpoints",
        "transition_declarations",
        "transition_declaration_ids_by_key",
        "transition_declaration_parent_ids",
        "transition_declaration_successor_ids",
        "transition_declaration_root_by_id",
        "transition_declaration_ancestry_by_id",
        "current_transition_declaration_tips_by_root",
        "transition_declaration_withdrawals",
        "transition_declaration_withdrawn_by",
        "transition_declaration_withdrawals_by_target",
    ):
        assert getattr(forward.loaded, name) == getattr(reverse.loaded, name)
    assert forward.loaded.revision.record_count == 29
    assert forward.loaded.revision.revision_id == EXPECTED_REVISION
    assert forward.stored_aggregate_sha256 == \
        reverse.stored_aggregate_sha256 == EXPECTED_STORED_AGGREGATE_SHA256
    assert forward.artifact_sha256 == \
        reverse.artifact_sha256 == EXPECTED_ARTIFACT_SHA256
    assert len(forward.artifact_bytes) == len(reverse.artifact_bytes) == 109906


def test_disposable_reproduction_is_identical_under_multiple_hash_seeds():
    script = r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.model_kernel.st002_slice_c_reproduction import reproduce
with TemporaryDirectory(dir="/tmp") as temporary:
    result = reproduce(Path(temporary), reverse_independent=True)
    print(result.artifact_sha256)
    print(result.stored_aggregate_sha256)
    print(result.loaded.revision.revision_id)
'''
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ, PYTHONHASHSEED=seed,
                           PYTHONDONTWRITEBYTECODE="1")
        outputs.append(subprocess.check_output(
            [sys.executable, "-c", script], text=True,
            cwd=Path.cwd(), env=environment))
    assert len(set(outputs)) == 1
    assert outputs[0].splitlines() == [
        EXPECTED_ARTIFACT_SHA256,
        EXPECTED_STORED_AGGREGATE_SHA256,
        EXPECTED_REVISION,
    ]


def test_disposable_artifact_uses_normative_canonical_records_only(tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    artifact = json.loads(reproduced.artifact_bytes)
    assert artifact["disclaimer"] == FIXTURE_DISCLAIMER == (
        "This is an illustrative synthetic ST-002 transition declaration "
        "fixture. A `declared` result means only that the selected model "
        "revision contains an admitted declaration connecting the exact "
        "pinned from-state and to-state declarations in the stated context. "
        "It does not claim that a real system is in either state, that either "
        "state is exclusive or complete, that the transition is enabled, "
        "executable, occurring, observed, or completed, or that temporal "
        "order establishes cause, control, safety, health, diagnosis, "
        "correctness, or recommended action.")
    assert artifact["nonclaims"] == (
        "Names, ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM, BH "
        "declarations, semantic compatibility, CN satisfaction, ST matches, "
        "temporal correlation, and observation changes did not create this "
        "transition. Displaying endpoint observations beside a transition "
        "does not persist an occurrence.")
    disclosed = {
        row["record_id"]: row
        for row in artifact["canonical_transition_records"]
    }
    transition_records = {
        record.record_id: record for record in reproduced.records.values()
        if record.record_kind.startswith("transition_")
    }
    assert set(disclosed) == set(transition_records)
    for record_id, record in transition_records.items():
        normative = canonical_bytes(record)
        row = disclosed[record_id]
        assert bytes.fromhex(row["canonical_hex"]) == normative
        assert row["canonical_bytes"] == len(normative)
        assert row["canonical_sha256"] == hashlib.sha256(normative).hexdigest()
        assert row["canonical_sha256"] == record_id.split("_", 1)[1]
        assert verify_record_id(record) is True
        assert b"+00:00" in normative
        assert b'"recorded_at"' in normative
        assert b"Z" not in normative


def test_compound_world_integrates_stale_pins_contexts_lifecycle_and_direction(
        tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    queries = kernel.ModelQueries(reproduced.loaded)

    forward = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    independent = queries.transition_declaration(
        TRANSITION_A, context=VIEW_INDEPENDENT)
    reverse = queries.transition_declaration(
        TRANSITION_B, context=AS_OPERATED)
    assert (forward.conclusion, forward.lineage_summary,
            forward.agreement_findings) == (
                "conflicted", "conflicted",
                ("corroborating_healthy_roots",
                 "cross_root_effective_body_disagreement",
                 "inactive_roots_present"))
    assert len(forward.roots) == 5
    assert len(forward.effective_body_groups) == 2
    assert (independent.conclusion, independent.lineage_summary,
            independent.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert (reverse.conclusion, reverse.lineage_summary,
            reverse.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))

    stale = _group_for_pin(forward, reproduced.records["from_root"].record_id)
    assert (stale.from_endpoint.state_declaration_conclusion,
            stale.from_endpoint.pinned_declaration_activity,
            stale.from_endpoint.alignment) == (
                "declared", "superseded",
                "pinned_declaration_superseded")
    assert (stale.to_endpoint.state_declaration_conclusion,
            stale.to_endpoint.pinned_declaration_activity,
            stale.to_endpoint.alignment) == (
                "declared", "withdrawn", "pinned_declaration_withdrawn")
    assert stale.from_endpoint.declaration == reproduced.records["from_root"]
    assert stale.to_endpoint.declaration == reproduced.records["to_root"]
    assert reproduced.records["from_successor"] not in (
        stale.from_endpoint.declaration, stale.to_endpoint.declaration)
    assert reproduced.records["to_peer"] not in (
        stale.from_endpoint.declaration, stale.to_endpoint.declaration)
    for endpoint in (stale.from_endpoint, stale.to_endpoint):
        state = queries.state_declaration(
            endpoint.state_anchor_id, context=AS_OPERATED)
        assertion = queries.state_assertion(endpoint.declaration.record_id)
        assert endpoint.state_declaration_conclusion == state.conclusion
        assert endpoint.pinned_declaration_activity == assertion.activity

    exact = _group_for_pin(
        forward, reproduced.records["from_successor"].record_id)
    assert (exact.from_endpoint.alignment, exact.to_endpoint.alignment) == (
        "exact_current", "exact_current")
    assert queries.transition(TRANSITION_A).status == "registered"
    assert queries.transition(TRANSITION_B).status == "registered"
    assert reproduced.records["forward_registration"].anchor.display_name == \
        reproduced.records["reverse_registration"].anchor.display_name
    assert reproduced.records["forward_registration"].from_state_anchor_id == \
        reproduced.records["reverse_registration"].to_state_anchor_id
    assert reproduced.records["forward_registration"].to_state_anchor_id == \
        reproduced.records["reverse_registration"].from_state_anchor_id
    assert reproduced.records["forward_registration"].record_id != \
        reproduced.records["reverse_registration"].record_id


def test_entity_collection_and_direct_queries_are_exactly_equivalent(tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=True)
    queries = kernel.ModelQueries(reproduced.loaded)
    collection = queries.transitions_of_entity(ENT_A, context=AS_OPERATED)
    assert tuple(entry.transition_anchor_id for entry in collection.entries) == (
        TRANSITION_A, TRANSITION_B)
    for entry in collection.entries:
        direct = queries.transition_declaration(
            entry.transition_anchor_id, context=AS_OPERATED)
        assert entry.model_dump(mode="python", exclude={
            "entry_index", "transition_registration_index",
        }) == direct.model_dump(mode="python", exclude={
            "material", "context", "registration_index",
        })


def test_historical_replay_revives_fork_withdrawal_and_endpoint_pins(tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    records = reproduced.records
    final = _queries(reproduced)
    before_merge = _queries(reproduced, "before_fork_merge")
    before_withdrawal = _queries(reproduced, "before_transition_withdrawal")
    before_from_successor = _queries(
        reproduced, "before_from_state_successor")
    before_to_withdrawal = _queries(
        reproduced, "before_to_state_withdrawal")

    assert (before_merge.transition_assertion(
        records["fork_left"].record_id).activity,
            before_merge.transition_assertion(
                records["fork_right"].record_id).activity) == (
                    "current", "current")
    assert before_merge.transition_assertion(
        records["fork_root"].record_id).containing_lineage_health == \
        "conflicted"
    assert (final.transition_assertion(records["fork_left"].record_id).activity,
            final.transition_assertion(
                records["fork_right"].record_id).activity,
            final.transition_assertion(
                records["fork_merge"].record_id).activity) == (
                    "superseded", "superseded", "current")
    assert final.transition_assertion(
        records["fork_merge"].record_id).containing_lineage_health == "healthy"

    assert before_withdrawal.transition_assertion(
        records["inactive_root"].record_id).activity == "current"
    assert final.transition_assertion(
        records["inactive_root"].record_id).activity == "withdrawn"

    from_revival = before_from_successor.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    from_group = _group_for_pin(
        from_revival, records["from_root"].record_id)
    assert (from_group.from_endpoint.pinned_declaration_activity,
            from_group.from_endpoint.alignment) == (
                "current", "exact_current")
    to_revival = before_to_withdrawal.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    to_group = _group_for_pin(to_revival, records["from_root"].record_id)
    assert (to_group.to_endpoint.pinned_declaration_activity,
            to_group.to_endpoint.alignment) == ("current", "exact_current")


def test_cross_context_and_cross_direction_lineage_attacks_reject(tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    records = reproduced.records
    mixed_context = transition_declaration(
        records["forward_registration"],
        from_registration=records["from_registration"],
        to_registration=records["to_registration"],
        from_declaration=records["from_view_independent"],
        to_declaration=records["to_root"],
        context=AS_OPERATED,
        note="hostile mixed endpoint context")
    with pytest.raises(kernel.ModelIntegrityError) as mixed_error:
        reproduced.store.append(mixed_context)
    assert mixed_error.value.error_code == \
        "MODEL_TRANSITION_DECLARATION_INVALID"

    cross_direction = transition_declaration(
        records["reverse_registration"],
        from_registration=records["to_registration"],
        to_registration=records["from_registration"],
        from_declaration=records["to_peer"],
        to_declaration=records["from_successor"],
        context=AS_OPERATED,
        supersedes=(records["stale_root_one"].record_id,),
        note="hostile cross-direction parent")
    with pytest.raises(kernel.ModelIntegrityError) as parent_error:
        reproduced.store.append(cross_direction)
    assert parent_error.value.error_code == "MODEL_TRANSITION_LINEAGE_INVALID"


def test_compound_world_evidence_closure_and_arms_are_integrated(tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    records = reproduced.records
    registration = records["forward_registration"]
    root = records["stale_root_one"]

    registration_refs = tuple(
        item.record_id for item in registration.evidence
        if item.kind == "model_record")
    assert len(registration_refs) == 3
    assert {records["from_registration"].record_id,
            records["to_registration"].record_id}.issubset(registration_refs)
    assert len(tuple(item for item in registration.evidence
                     if item.kind != "model_record")) == 1

    declaration_refs = tuple(
        item.record_id for item in root.evidence if item.kind == "model_record")
    assert set(declaration_refs) == {
        registration.record_id,
        records["from_registration"].record_id,
        records["to_registration"].record_id,
        records["from_root"].record_id,
        records["to_root"].record_id,
    }
    template = transition_declaration(
        registration,
        from_registration=records["from_registration"],
        to_registration=records["to_registration"],
        from_declaration=records["from_root"],
        to_declaration=records["to_root"],
        note="evidence closure template")
    support = kernel.ModelRecordEvidence(
        kind="model_record", record_id=root.record_id)
    dependent = transition_declaration(
        registration,
        from_registration=records["from_registration"],
        to_registration=records["to_registration"],
        from_declaration=records["from_root"],
        to_declaration=records["to_root"],
        evidence=(*template.evidence, support),
        note="depends on another transition declaration")
    reproduced.store.append(dependent)
    assert support in reproduced.store.load().transition_declarations[
        dependent.record_id].evidence
    without_support = tuple(
        record_id for record_id in reproduced.store.load().revision.record_ids
        if record_id != root.record_id)
    with pytest.raises(kernel.ModelIntegrityError) as replay_error:
        reproduced.store.replay(without_support)
    assert replay_error.value.error_code == "MODEL_REFERENCE_INVALID"

    before = {
        path.name: path.read_bytes()
        for path in sorted(reproduced.store.records_dir.iterdir())
    }
    missing = kernel.ModelRecordEvidence(
        kind="model_record", record_id="trd_" + "f" * 64)
    missing_support = transition_declaration(
        registration,
        from_registration=records["from_registration"],
        to_registration=records["to_registration"],
        from_declaration=records["from_root"],
        to_declaration=records["to_root"],
        evidence=(*template.evidence, missing),
        note="missing transition evidence")
    with pytest.raises(kernel.ModelIntegrityError) as missing_error:
        reproduced.store.append(missing_support)
    assert missing_error.value.error_code == "MODEL_REFERENCE_INVALID"
    assert {path.name: path.read_bytes()
            for path in sorted(reproduced.store.records_dir.iterdir())} == before
    with pytest.raises(ValidationError):
        kernel.ModelRecordEvidence(
            kind="model_record",
            record_id=records["inactive_withdrawal"].record_id)


def test_compound_outer_results_round_trip_and_reject_representative_forgery(
        tmp_path):
    reproduced = reproduce(tmp_path, reverse_independent=False)
    queries = kernel.ModelQueries(reproduced.loaded)
    values = (
        queries.transition(TRANSITION_A),
        queries.transition_declaration(TRANSITION_A, context=AS_OPERATED),
        queries.transitions_of_entity(ENT_A, context=AS_OPERATED),
        queries.transition_assertion(
            reproduced.records["fork_merge"].record_id),
    )
    for value in values:
        rebuilt = type(value).model_validate(value.model_dump(mode="python"))
        assert rebuilt.model_dump_json() == value.model_dump_json()

    lookup, declaration, entity, assertion = values
    attacks = []
    payload = lookup.model_dump(mode="python")
    payload["status"] = "not_registered"
    attacks.append((type(lookup), payload))
    payload = declaration.model_dump(mode="python")
    group_index = next(
        index for index, group in enumerate(payload["effective_body_groups"])
        if group["from_endpoint"]["alignment"] != "exact_current")
    payload["effective_body_groups"][group_index]["from_endpoint"][
        "alignment"] = "exact_current"
    attacks.append((type(declaration), payload))
    payload = entity.model_dump(mode="python")
    payload["entries"][0]["conclusion"] = "declared"
    attacks.append((type(entity), payload))
    payload = assertion.model_dump(mode="python")
    payload["activity"] = "withdrawn"
    attacks.append((type(assertion), payload))
    for contract, payload in attacks:
        with pytest.raises(ValidationError):
            contract.model_validate(payload)


def test_slice_c_reproduction_helper_has_exact_hard_boundary():
    source = Path(
        "tests/model_kernel/st002_slice_c_reproduction.py").read_text(
            encoding="utf-8")
    for forbidden in (
        "mint_transition_anchor", "uuid4", "models/demo-printer",
        "backend.transition_assessment", "backend.transition_occurrence",
        "backend.state_classification", "SourceSelector", "as_of",
        "cutoff", "change_class", "next_state",
    ):
        assert forbidden not in source
    assert "kernel.ModelStore" in source
    assert "kernel.ModelQueries" in source
    assert "transition_registration(" in source
    assert "transition_declaration(" in source
    assert "transition_withdrawal(" in source
