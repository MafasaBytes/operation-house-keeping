"""Disposable-only BH-001 Slice D candidate rehearsal helpers.

This module never invokes an identity minter. Candidate anchors are reconstructed
from the owner-gate manifest and every ledger append targets a caller-supplied
temporary root.
"""

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import shutil

import backend.model_kernel as kernel
from backend.behavior_evaluation import (
    BehaviorEvaluationQueries,
    BehaviorParticipantSource,
)
from backend.identity_binding.store import BindingStore
from backend.model_state import SourceSelector
from backend.system_identity import BehaviorAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef
from tests.model_kernel.test_cross_layer_seam import committed_declarations
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    BH001_MODEL_RECORDS,
    CN001_MEMBERSHIP,
    DEMO_MODEL,
    GOLDEN_REVISION,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_BH001_REVISION,
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
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES as PT_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as PT_ARTIFACT_SHA256,
    _artifact_bytes as pt_artifact_bytes,
)
from tests.model_state.helpers import PROP_TEMP, SUBJECT
from tests.model_state.test_demo_join import (
    AS_OF,
    EXTRUDER,
    LATEST_ATTEMPT_ID,
    LATEST_CHECKSUM,
    LATEST_OBSERVATION_ID,
    LATEST_OCCURRENCE_ID,
    LATEST_RAW_RECORD_ID,
    LATEST_RECEIVED_AT,
    LATEST_VALUE,
)
from tests.model_state.test_demo_vp001 import (
    ARTIFACT_BYTES as VP_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as VP_ARTIFACT_SHA256,
    _artifact_bytes as vp_artifact_bytes,
)
from tests.semantic_compatibility.test_demo_semantics import stack as semantic_stack


MANIFEST_PATH = Path(
    "docs/superpowers/reports/"
    "2026-08-30-bh001-slice-d-candidate-identities.json")
BASE_REVISION = PRE_BH001_REVISION
EXISTING_VARIABLE = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
EXISTING_VARIABLE_REGISTRATION = (
    "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7"
)
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture",
    agent="bh001_demo_fixture",
    method="manual_declaration",
)
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
RECORDED_AT = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
NEUTRAL_PROPERTY = SourcePropertyRef(
    extraction_route="synthetic:bh001:v1",
    item_key="bh001_candidate",
    json_pointer="/synthetic/comparison-variable",
)
REGISTRATION_STATEMENT = (
    "BH-001 fixture authority explicitly registers this unordered pair of "
    "synthetic variables for the exact-numeric-equality rule family; shared "
    "ownership, names, topology, VPA associations, semantics, constraints, "
    "and observations did not create or corroborate this behavior registration."
)
DECLARATION_STATEMENT = (
    "BH-001 fixture authority explicitly declares this exact-numeric-equality "
    "relationship under the same-acquisition-cohort evaluation basis in the "
    "as-designed lifecycle view; illustrative declaration only, not an "
    "observed equality or real-machine behavior claim."
)
DISCLAIMER = (
    "This is an illustrative synthetic BH-001 exact-numeric-equality "
    "declaration. It does not describe or claim any real printer physics, "
    "target, command, response, control loop, wiring, signal path, flow, "
    "causality, simultaneity, correctness, safety, health, real-machine "
    "behavior, or operating condition. Shared ownership, names, topology, "
    "VPA associations, semantic compatibility, constraints, and observed "
    "correlation did not create this declaration."
)
WARNINGS = (
    "The not_executed result is an honest admission result, not evidence that "
    "the declared relation is false.",
    "Shared ownership did not create or corroborate the behavior.",
    "Names, topology, VPA associations, semantic compatibility, constraints, "
    "and observed correlation did not create or corroborate the behavior.",
    "No result describes a port, flow, direction, influence, causality, "
    "control, safety, diagnosis, recommendation, or real-machine operation.",
)


def canonical_json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def candidate_manifest():
    raw = MANIFEST_PATH.read_bytes()
    payload = json.loads(raw)
    assert raw == canonical_json_bytes(payload)
    assert payload["status"] == "non_authoritative_candidate"
    assert payload["accepted_base_model_revision"] == BASE_REVISION
    variable = VariableAnchor.model_validate(payload["variable_anchor"])
    behavior = BehaviorAnchor.model_validate(payload["behavior_anchor"])
    assert variable.model_dump(mode="json") == payload["variable_anchor"]
    assert behavior.model_dump(mode="json") == payload["behavior_anchor"]
    return payload, variable, behavior, raw


def _signature(*, role_code: str) -> kernel.ConstraintSemanticSignature:
    return kernel.ConstraintSemanticSignature(
        quantity_kind=kernel.QuantityKindReference(
            system_id="project_local",
            system_edition="ohk-quantities-1",
            code="temperature",
        ),
        observation_role=kernel.ObservationRoleReference(
            system_id="project_local",
            system_edition="ohk-observation-roles-1",
            code=role_code,
        ),
        unit=kernel.UnitReference(
            system_id="project_local",
            system_edition="ohk-units-1",
            code="degree_celsius",
        ),
    )


def candidate_records():
    manifest, variable, behavior, _ = candidate_manifest()
    vrg = kernel.build_record(
        kernel.VariableRegistration,
        anchor=variable,
        recorded_at=RECORDED_AT,
        authority=AUTHORITY,
        note="BH-001 bounded neutral synthetic participant.",
    )
    brg = kernel.build_record(
        kernel.BehaviorRegistration,
        anchor=behavior,
        participant_variable_anchor_ids=(
            EXISTING_VARIABLE, variable.anchor_id),
        rule_family="exact_numeric_equality",
        evidence=(
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=EXISTING_VARIABLE_REGISTRATION),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=vrg.record_id),
            kernel.OwnerDeclarationEvidence(
                kind="owner_declaration", statement=REGISTRATION_STATEMENT),
        ),
        recorded_at=RECORDED_AT,
        authority=AUTHORITY,
        note="BH-001 bounded synthetic registration.",
    )
    bhd = kernel.build_record(
        kernel.BehaviorRuleDeclaration,
        behavior_anchor_id=behavior.anchor_id,
        context=CONTEXT,
        participant_semantics=(
            kernel.BehaviorVariableSemanticLock(
                variable_anchor_id=EXISTING_VARIABLE,
                signature=_signature(role_code="measured_actual"),
            ),
            kernel.BehaviorVariableSemanticLock(
                variable_anchor_id=variable.anchor_id,
                signature=_signature(role_code="synthetic_comparison"),
            ),
        ),
        rule=kernel.ExactNumericEqualityRule(kind="exact_numeric_equality"),
        evaluation_basis="same_acquisition_cohort",
        evidence=(
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=brg.record_id),
            kernel.OwnerDeclarationEvidence(
                kind="owner_declaration", statement=DECLARATION_STATEMENT),
        ),
        supersedes=(),
        recorded_at=RECORDED_AT,
        authority=AUTHORITY,
        note="BH-001 bounded synthetic declaration.",
    )
    return manifest, variable, behavior, (vrg, brg, bhd)


def record_inventory(root: Path, record_ids) -> dict[str, str]:
    return {
        f"{record_id}.json": sha256_bytes(
            (root / "records" / f"{record_id}.json").read_bytes())
        for record_id in record_ids
    }


def inventory_digest(inventory: dict[str, str]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(sorted(inventory.items()))))


def tree_inventory(*roots: Path) -> dict[str, str]:
    inventory = {}
    for root in roots:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = f"{root.as_posix()}/{path.relative_to(root).as_posix()}"
            inventory[relative] = sha256_bytes(path.read_bytes())
    return inventory


def prepare_disposable_store(root: Path, *, predecessor_copy_order=None):
    source_ids = (tuple(VP001_MEMBERSHIP)
                  if predecessor_copy_order is None
                  else tuple(predecessor_copy_order))
    assert len(source_ids) == len(VP001_MEMBERSHIP)
    assert set(source_ids) == set(VP001_MEMBERSHIP)
    source_paths = {
        path.stem for path in (DEMO_MODEL / "records").glob("*.json")}
    assert source_paths == set(BH001_MEMBERSHIP)
    source_before = record_inventory(DEMO_MODEL, source_ids)
    store = kernel.ModelStore(root / "demo-printer")
    for record_id in source_ids:
        source = DEMO_MODEL / "records" / f"{record_id}.json"
        target = store.records_dir / source.name
        shutil.copyfile(source, target)
    assert record_inventory(store.records_dir.parent, source_ids) == source_before
    loaded = store.replay(source_ids)
    assert loaded.revision.revision_id == BASE_REVISION
    assert loaded.revision.record_count == 29
    return store, source_before


def _record_ids(material, indices) -> list[str]:
    return [material.record_at(index).record_id for index in indices]


def query_disclosure(base, final, behavior_id, records):
    vrg, brg, bhd = records
    current = kernel.ModelQueries(final)
    historical = kernel.ModelQueries(base)
    registration = current.behavior(behavior_id)
    declaration = current.behavior_declaration(behavior_id, context=CONTEXT)
    existing_reverse = current.behaviors_involving_variable(
        EXISTING_VARIABLE, context=CONTEXT)
    new_reverse = current.behaviors_involving_variable(
        vrg.anchor.anchor_id, context=CONTEXT)
    brg_assertion = current.behavior_assertion(brg.record_id)
    bhd_assertion = current.behavior_assertion(bhd.record_id)
    historical_registration = historical.behavior(behavior_id)
    historical_declaration = historical.behavior_declaration(
        behavior_id, context=CONTEXT)
    historical_reverse = historical.behaviors_involving_variable(
        EXISTING_VARIABLE, context=CONTEXT)
    historical_brg = historical.behavior_assertion(brg.record_id)
    historical_bhd = historical.behavior_assertion(bhd.record_id)

    roots = [{
        "root_record_id": declaration.material.record_at(
            row.root_record_index).record_id,
        "lineage_record_ids": _record_ids(
            declaration.material, row.lineage_record_indices),
        "current_tip_ids": _record_ids(
            declaration.material, row.current_tip_indices),
        "withdrawal_ids": _record_ids(
            declaration.material, row.withdrawal_indices),
        "lineage_health": row.lineage_health,
        "effective_body_group_indices": list(
            row.effective_body_group_indices),
    } for row in declaration.roots]

    def reverse_summary(result):
        return {
            "status": result.status,
            "entries": [{
                "entry_index": row.entry_index,
                "behavior_anchor_id": row.behavior_anchor_id,
                "other_variable_anchor_id": row.other_variable_anchor_id,
                "conclusion": row.conclusion,
                "lineage_summary": row.lineage_summary,
                "agreement_findings": list(row.agreement_findings),
            } for row in result.entries],
        }

    def assertion_summary(result):
        return {
            "record_id": result.record_id,
            "lookup_status": result.lookup_status,
            "activity": result.activity,
            "containing_lineage_health": result.containing_lineage_health,
            "containing_subject_conclusion": (
                result.containing_subject_conclusion),
            "containing_agreement_findings": (
                list(result.containing_agreement_findings)
                if result.containing_agreement_findings is not None else None),
            "root_record_id": (
                result.material.record_at(result.root_record_index).record_id
                if result.root_record_index is not None else None),
            "successor_ids": _record_ids(
                result.material, result.successor_indices),
            "withdrawal_ids": _record_ids(
                result.material, result.withdrawal_indices),
        }

    return {
        "registration": {
            "status": registration.status,
            "record_id": registration.material.record_at(
                registration.registration_index).record_id,
            "participant_variable_anchor_ids": list(
                registration.material.record_at(
                    registration.registration_index
                ).participant_variable_anchor_ids),
        },
        "declaration": {
            "conclusion": declaration.conclusion,
            "lineage_summary": declaration.lineage_summary,
            "agreement_findings": list(declaration.agreement_findings),
            "current_declaration_ids": _record_ids(
                declaration.material,
                declaration.current_declaration_indices),
            "root_count": len(declaration.roots),
            "roots": roots,
        },
        "behaviors_involving_existing_variable": reverse_summary(
            existing_reverse),
        "behaviors_involving_candidate_variable": reverse_summary(new_reverse),
        "registration_assertion": assertion_summary(brg_assertion),
        "declaration_assertion": assertion_summary(bhd_assertion),
        "historical_29": {
            "registration_status": historical_registration.status,
            "declaration_conclusion": historical_declaration.conclusion,
            "existing_variable_status": historical_reverse.status,
            "existing_variable_entry_count": len(historical_reverse.entries),
            "registration_assertion_lookup": historical_brg.lookup_status,
            "declaration_assertion_lookup": historical_bhd.lookup_status,
        },
    }


def participant_sources(variable_id: str):
    return (
        BehaviorParticipantSource(
            variable_anchor_id=variable_id,
            entity_anchor_id=EXTRUDER,
            source=SourceSelector(
                subject=SUBJECT, property=NEUTRAL_PROPERTY),
        ),
        BehaviorParticipantSource(
            variable_anchor_id=EXISTING_VARIABLE,
            entity_anchor_id=EXTRUDER,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP),
        ),
    )


def _assert_binding_seam(*, entity_registrations, variable_registrations,
                         candidate_vrg):
    candidate_variable_id = candidate_vrg.anchor.anchor_id
    declared = committed_declarations()
    observed_preexisting = (
        set(entity_registrations)
        | (set(variable_registrations) - {candidate_variable_id}))
    assert observed_preexisting == set(declared)
    for anchor_id, registration in entity_registrations.items():
        assert anchor_id in declared
        assert registration.anchor == declared[anchor_id]
    exceptions = []
    for anchor_id, registration in variable_registrations.items():
        if anchor_id in declared:
            assert registration.anchor == declared[anchor_id]
        else:
            exceptions.append((anchor_id, registration))
    assert exceptions == [(candidate_variable_id, candidate_vrg)]


def binding_seam_disclosure(final, records, state_result):
    vrg, _, _ = records
    candidate_id = vrg.anchor.anchor_id
    _assert_binding_seam(
        entity_registrations=final.registrations_by_anchor,
        variable_registrations=final.variable_registrations_by_anchor,
        candidate_vrg=vrg,
    )
    declared = committed_declarations()
    assert candidate_id not in declared
    assert state_result.anchor_agreement == "binding_declaration_absent"

    second = kernel.build_record(
        kernel.VariableRegistration,
        anchor=VariableAnchor(
            anchor_id="var_ffffffffffffffffffffffffffffffff",
            entity_anchor_id=EXTRUDER,
            namespace="demo-printer",
            display_name="Second undeclared seam probe",
            role_name=None,
        ),
        recorded_at=RECORDED_AT,
        authority=AUTHORITY,
        note="Disposable seam rejection probe.",
    )
    variable_map = dict(final.variable_registrations_by_anchor)
    variable_map[second.anchor.anchor_id] = second
    second_failed = False
    try:
        _assert_binding_seam(
            entity_registrations=final.registrations_by_anchor,
            variable_registrations=variable_map,
            candidate_vrg=vrg,
        )
    except AssertionError:
        second_failed = True
    assert second_failed

    divergent = kernel.build_record(
        kernel.VariableRegistration,
        anchor=VariableAnchor(
            anchor_id=candidate_id,
            entity_anchor_id=EXTRUDER,
            namespace="demo-printer",
            display_name="Divergent candidate seam probe",
            role_name=None,
        ),
        recorded_at=RECORDED_AT,
        authority=AUTHORITY,
        note="Disposable divergent seam rejection probe.",
    )
    divergent_map = dict(final.variable_registrations_by_anchor)
    divergent_map[candidate_id] = divergent
    divergent_failed = False
    try:
        _assert_binding_seam(
            entity_registrations=final.registrations_by_anchor,
            variable_registrations=divergent_map,
            candidate_vrg=vrg,
        )
    except AssertionError:
        divergent_failed = True
    assert divergent_failed

    return {
        "candidate_exception": {
            "variable_anchor_id": candidate_id,
            "variable_registration_id": vrg.record_id,
        },
        "candidate_binding_declaration_present": False,
        "preexisting_anchor_count": len(declared),
        "preexisting_anchors_exact": True,
        "second_undeclared_variable_gate_failed": second_failed,
        "divergent_candidate_gate_failed": divergent_failed,
        "candidate_model_state_anchor_agreement": state_result.anchor_agreement,
    }


def evaluator_disclosure(work_root: Path, final, behavior_id: str, records):
    vrg, _, _ = records
    semantic, _, state, temporal = semantic_stack(work_root, model=final)
    sources = participant_sources(vrg.anchor.anchor_id)
    evaluation = BehaviorEvaluationQueries(semantic).behavior_evaluation(
        behavior_id,
        context=CONTEXT,
        as_of=AS_OF,
        participants=sources,
    )
    direct_semantic = tuple(
        semantic.variable_semantic_compatibility(
            source.variable_anchor_id,
            as_of=AS_OF,
            entity_anchor_id=source.entity_anchor_id,
            source=source.source,
        )
        for source in evaluation.participant_sources
    )
    assert evaluation.participant_semantic_results == direct_semantic

    direct_states = tuple(
        state.variable_state(
            source.variable_anchor_id,
            as_of=AS_OF,
            entity_anchor_id=source.entity_anchor_id,
            source=source.source,
        )
        for source in evaluation.participant_sources
    )
    for semantic_result, direct_state in zip(
            evaluation.participant_semantic_results, direct_states):
        assert semantic_result.value_compatibility.state == direct_state

    by_variable = {
        result.variable_anchor_id: result
        for result in evaluation.participant_semantic_results
    }
    existing_semantic = by_variable[EXISTING_VARIABLE]
    candidate_semantic = by_variable[vrg.anchor.anchor_id]
    existing_state = existing_semantic.value_compatibility.state
    candidate_state = candidate_semantic.value_compatibility.state
    [existing_candidate] = existing_state.candidates
    occurrence = existing_candidate.bound.observed.occurrence
    direct_temporal = temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF)
    assert occurrence == direct_temporal.occurrence
    provenance = temporal.provenance(occurrence.occurrence_id)

    assert evaluation.execution == "not_executed"
    assert evaluation.computed_relation is None
    assert evaluation.cohort_admission == "not_evaluated"
    assert candidate_state.anchor_agreement == "binding_declaration_absent"
    assert candidate_state.observation_availability == "none_before_cutoff"
    assert existing_state.observation_availability == "observed"
    assert occurrence.value_json == LATEST_VALUE
    assert occurrence.received_at == LATEST_RECEIVED_AT
    assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
    assert occurrence.attempt_id == LATEST_ATTEMPT_ID
    assert occurrence.observation_id == LATEST_OBSERVATION_ID
    assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
    assert occurrence.payload_checksum == LATEST_CHECKSUM
    assert provenance.raw_record_id == LATEST_RAW_RECORD_ID
    assert provenance.payload_checksum == LATEST_CHECKSUM

    seam = binding_seam_disclosure(final, records, candidate_state)
    participants = [{
        "participant_index": row.participant_index,
        "variable_anchor_id": row.variable_anchor_id,
        "model_admission": row.model_admission,
        "observation_availability": row.observation_availability,
        "attachment_admission": row.attachment_admission,
        "semantic_admission": row.semantic_admission,
        "unit_admission": row.unit_admission,
        "lock_admission": row.lock_admission,
        "numeric_admission": row.numeric_admission,
        "admission": row.admission,
        "refusal_reasons": list(row.refusal_reasons),
        "canonical_decimal": (
            row.canonical_decimal.model_dump(mode="json")
            if row.canonical_decimal is not None else None),
    } for row in evaluation.participants]

    return {
        "full_result": evaluation.model_dump(mode="json"),
        "direct_participant_semantic_results_equal": True,
        "direct_participant_state_results_equal": True,
        "direct_temporal_occurrence_equal": True,
        "execution": evaluation.execution,
        "computed_relation": evaluation.computed_relation,
        "cohort_admission": evaluation.cohort_admission,
        "not_executed_reasons": [
            row.model_dump(mode="json")
            for row in evaluation.not_executed_reasons
        ],
        "participants": participants,
        "existing_participant_occurrence": {
            "value_json": occurrence.value_json,
            "received_at": occurrence.received_at.isoformat(),
            "occurrence_id": occurrence.occurrence_id,
            "attempt_id": occurrence.attempt_id,
            "observation_id": occurrence.observation_id,
            "raw_record_id": occurrence.raw_record_id,
            "payload_checksum": occurrence.payload_checksum,
        },
        "existing_participant_provenance": {
            "attempt_id": provenance.attempt_id,
            "observation_id": provenance.observation_id,
            "raw_record_id": provenance.raw_record_id,
            "payload_checksum": provenance.payload_checksum,
        },
        "provenance_axes": {
            "model_revision": existing_state.model_revision.revision_id,
            "binding_revision": existing_state.binding_revision.revision_id,
            "interpretation_revision": (
                existing_semantic.interpretation_revision.revision_id),
            "temporal_cutoff": AS_OF.isoformat(),
            "statement": (
                "Model, binding, interpretation, and temporal-cutoff axes "
                "remain separate; no clock synchronization or shared validity "
                "interval is claimed."
            ),
        },
        "binding_seam": seam,
    }


def historical_revisions():
    store = kernel.ModelStore(DEMO_MODEL)
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
    result = []
    for membership, expected_revision, count in cases:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == expected_revision
        assert loaded.revision.record_count == count
        result.append({
            "record_count": count,
            "revision_id": loaded.revision.revision_id,
            "record_ids": list(loaded.revision.record_ids),
        })
    return result


def artifact_bytes(*, manifest, records, source_before, candidate_files,
                   final, queries, evaluator, binding_hashes,
                   interpretation_hashes, accepted_artifacts):
    vrg, brg, bhd = records
    content = {
        "candidate_manifest": {
            "path": MANIFEST_PATH.as_posix(),
            "bytes": len(MANIFEST_PATH.read_bytes()),
            "sha256": sha256_bytes(MANIFEST_PATH.read_bytes()),
            "content": manifest,
        },
        "model": {
            "base_revision": BASE_REVISION,
            "base_membership": list(VP001_MEMBERSHIP),
            "candidate_append_sequence": [
                vrg.record_id, brg.record_id, bhd.record_id],
            "candidate_model_records": [
                vrg.record_id, brg.record_id, bhd.record_id],
            "final_revision": final.revision.model_dump(mode="json"),
            "explicit_membership": list(final.revision.record_ids),
            "predecessor_sha256": dict(sorted(source_before.items())),
            "predecessor_aggregate_sha256": inventory_digest(source_before),
            "candidate_records": [{
                "record": record.model_dump(mode="json"),
                "stored_file": candidate_files[f"{record.record_id}.json"],
            } for record in records],
        },
        "authority": AUTHORITY.model_dump(mode="json"),
        "context": CONTEXT.model_dump(mode="json"),
        "queries": queries,
        "evaluation": evaluator,
        "binding": {
            "committed_file_sha256": dict(sorted(binding_hashes.items())),
            "files_unchanged": True,
        },
        "interpretation": {
            "committed_file_sha256": dict(
                sorted(interpretation_hashes.items())),
            "files_unchanged": True,
        },
        "preservation": {
            "historical_revisions": historical_revisions(),
            "pt_artifact": accepted_artifacts["pt"],
            "vp_artifact": accepted_artifacts["vp"],
        },
        "scope": {
            "authoritative_append_performed": False,
            "records_proposed": {
                "variable_registration": 1,
                "behavior_registration": 1,
                "behavior_rule_declaration": 1,
                "behavior_rule_withdrawal": 0,
                "other": 0,
            },
            "statement": (
                "The committed demonstration remains declaration-only. No "
                "binding, VSP, VSM, port, VPA, constraint, interpretation, "
                "temporal, source, correction, withdrawal, or second behavior "
                "root is proposed."
            ),
        },
    }
    content_bytes = canonical_json_bytes(content)
    return canonical_json_bytes({
        "artifact": "BH-001 demo-printer behavior disclosure candidate",
        "schema_version": "1",
        "disclaimer": DISCLAIMER,
        "warnings": list(WARNINGS),
        "artifact_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": sha256_bytes(content_bytes),
        },
        "content": content,
    })


def run_rehearsal(root: Path, *, predecessor_copy_order=None):
    manifest, variable, behavior, records = candidate_records()
    store, source_before = prepare_disposable_store(
        root / "ledger", predecessor_copy_order=predecessor_copy_order)
    base = store.replay(VP001_MEMBERSHIP)
    for record in records:
        store.append(record)
    candidate_ids = tuple(record.record_id for record in records)
    assert candidate_ids == BH001_MODEL_RECORDS
    membership = tuple(sorted((*VP001_MEMBERSHIP, *candidate_ids)))
    assert membership == BH001_MEMBERSHIP
    final = store.replay(membership)
    loaded = store.load()
    assert final.revision == loaded.revision
    assert final.revision.record_count == 32
    assert tuple(final.revision.record_ids) == membership
    assert set(membership) - set(VP001_MEMBERSHIP) == set(candidate_ids)
    assert len(final.behavior_registrations_by_anchor) == 1
    assert len(final.behavior_rule_declarations) == 1
    assert len(final.behavior_rule_withdrawals) == 0
    assert not records[2].supersedes
    assert len(final.current_behavior_rule_tips_by_root) == 1

    source_after = record_inventory(store.records_dir.parent, VP001_MEMBERSHIP)
    assert source_after == source_before
    candidate_record_bytes = {
        f"{record.record_id}.json": (
            store.records_dir / f"{record.record_id}.json").read_bytes()
        for record in records
    }
    candidate_files = {
        filename: {
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        }
        for filename, raw in candidate_record_bytes.items()
    }
    for record in records:
        assert final.records[record.record_id] == record

    binding_hashes_before = tree_inventory(
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
    )
    interpretation_hashes_before = tree_inventory(
        Path("interpretations/demo-printer"))
    queries = query_disclosure(base, final, behavior.anchor_id, records)
    evaluator = evaluator_disclosure(
        root / "evaluation", final, behavior.anchor_id, records)
    binding_hashes = tree_inventory(
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
    )
    interpretation_hashes = tree_inventory(Path("interpretations/demo-printer"))
    assert binding_hashes == binding_hashes_before
    assert interpretation_hashes == interpretation_hashes_before
    accepted_artifacts = verify_accepted_artifacts(root / "accepted-artifacts")
    artifact = artifact_bytes(
        manifest=manifest,
        records=records,
        source_before=source_before,
        candidate_files=candidate_files,
        final=final,
        queries=queries,
        evaluator=evaluator,
        binding_hashes=binding_hashes,
        interpretation_hashes=interpretation_hashes,
        accepted_artifacts=accepted_artifacts,
    )
    return {
        "manifest": manifest,
        "variable_anchor": variable.model_dump(mode="json"),
        "behavior_anchor": behavior.model_dump(mode="json"),
        "records": [record.model_dump(mode="json") for record in records],
        "record_ids": list(candidate_ids),
        "candidate_files": candidate_files,
        "candidate_record_bytes": candidate_record_bytes,
        "membership": list(membership),
        "revision": final.revision.model_dump(mode="json"),
        "queries": queries,
        "evaluator": evaluator,
        "predecessor_sha256": source_before,
        "predecessor_aggregate_sha256": inventory_digest(source_before),
        "binding_sha256": binding_hashes,
        "interpretation_sha256": interpretation_hashes,
        "artifact": artifact,
        "artifact_bytes": len(artifact),
        "artifact_sha256": sha256_bytes(artifact),
    }


def authoritative_reproduction(work_root: Path):
    """Reproduce the approved artifact from the committed 32-record ledger."""
    manifest, variable, behavior, records = candidate_records()
    store = kernel.ModelStore(DEMO_MODEL)
    base = store.replay(VP001_MEMBERSHIP)
    final = store.replay(BH001_MEMBERSHIP)
    loaded = store.load()
    assert final.revision == loaded.revision
    assert final.revision.revision_id == (
        "mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b")
    assert final.revision.record_count == 32
    assert tuple(final.revision.record_ids) == BH001_MEMBERSHIP
    assert tuple(record.record_id for record in records) == BH001_MODEL_RECORDS
    for record in records:
        assert final.records[record.record_id] == record

    source_before = record_inventory(DEMO_MODEL, VP001_MEMBERSHIP)
    assert inventory_digest(source_before) == (
        "962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf")
    candidate_record_bytes = {
        f"{record.record_id}.json": (
            store.records_dir / f"{record.record_id}.json").read_bytes()
        for record in records
    }
    candidate_files = {
        filename: {"bytes": len(raw), "sha256": sha256_bytes(raw)}
        for filename, raw in candidate_record_bytes.items()
    }

    protected_before = tree_inventory(
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
        Path("interpretations/demo-printer"),
        Path("var/raw_store"),
        Path("showcases/demo-printer"),
    )
    queries = query_disclosure(base, final, behavior.anchor_id, records)
    evaluator = evaluator_disclosure(
        work_root / "evaluation", final, behavior.anchor_id, records)
    binding_hashes = tree_inventory(
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
    )
    interpretation_hashes = tree_inventory(Path("interpretations/demo-printer"))
    accepted_artifacts = verify_accepted_artifacts(
        work_root / "accepted-artifacts")
    protected_after = tree_inventory(
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
        Path("interpretations/demo-printer"),
        Path("var/raw_store"),
        Path("showcases/demo-printer"),
    )
    assert protected_before == protected_after
    artifact = artifact_bytes(
        manifest=manifest,
        records=records,
        source_before=source_before,
        candidate_files=candidate_files,
        final=final,
        queries=queries,
        evaluator=evaluator,
        binding_hashes=binding_hashes,
        interpretation_hashes=interpretation_hashes,
        accepted_artifacts=accepted_artifacts,
    )
    return {
        "manifest": manifest,
        "variable_anchor": variable.model_dump(mode="json"),
        "behavior_anchor": behavior.model_dump(mode="json"),
        "records": [record.model_dump(mode="json") for record in records],
        "record_ids": list(BH001_MODEL_RECORDS),
        "candidate_files": candidate_files,
        "candidate_record_bytes": candidate_record_bytes,
        "membership": list(BH001_MEMBERSHIP),
        "revision": final.revision.model_dump(mode="json"),
        "queries": queries,
        "evaluator": evaluator,
        "predecessor_sha256": source_before,
        "predecessor_aggregate_sha256": inventory_digest(source_before),
        "binding_sha256": binding_hashes,
        "interpretation_sha256": interpretation_hashes,
        "artifact": artifact,
        "artifact_bytes": len(artifact),
        "artifact_sha256": sha256_bytes(artifact),
    }


def verify_accepted_artifacts(tmp_path: Path):
    pt = pt_artifact_bytes()
    vp = vp_artifact_bytes(tmp_path)
    assert len(pt) == PT_ARTIFACT_BYTES
    assert sha256_bytes(pt) == PT_ARTIFACT_SHA256
    assert len(vp) == VP_ARTIFACT_BYTES
    assert sha256_bytes(vp) == VP_ARTIFACT_SHA256
    return {
        "pt": {"bytes": len(pt), "sha256": sha256_bytes(pt)},
        "vp": {"bytes": len(vp), "sha256": sha256_bytes(vp)},
    }
