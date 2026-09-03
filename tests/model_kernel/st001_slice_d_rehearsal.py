"""Disposable-only ST-001 Slice D candidate rehearsal helpers.

The helper intentionally cannot mint identity. It reconstructs one frozen
``StateAnchor`` from caller-supplied manifest content and directs every copy,
append, temporal projection, and generated artifact to caller-supplied
disposable roots.
"""

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import shutil

import backend.model_kernel as kernel
from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.model_kernel.canonical import (
    canonical_bytes as kernel_canonical_bytes,
    canonical_payload as kernel_canonical_payload,
    compute_record_id,
    verify_record_id,
)
from backend.model_state import SourceSelector
from backend.state_classification import (
    StateClassificationQueries,
    StateConditionSource,
)
from backend.system_identity import StateAnchor
from tests.model_kernel.bh001_slice_d_rehearsal import (
    authoritative_reproduction as bh_authoritative_reproduction,
)
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CN001_MEMBERSHIP,
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
    FL001_MEMBERSHIP,
    ST001_MEMBERSHIP,
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
from tests.semantic_compatibility.test_demo_semantics import (
    stack as semantic_stack,
)


MANIFEST_PATH = Path(
    "docs/superpowers/reports/"
    "2026-08-31-st001-slice-d-candidate-identities.json")
DISCLOSURE_PATH = Path(
    "docs/superpowers/reports/"
    "2026-08-31-st001-slice-d-candidate-disclosure.json")
ACCEPTED_SLICE_C_HEAD = "f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6"
DEMO_MODEL = Path("models/demo-printer")
BASE_REVISION = (
    "mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b")
SUBJECT_ENTITY = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
SUBJECT_ENTITY_REGISTRATION = (
    "reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451")
CONSTRAINT = "con_4b768cf843f5474cb5e564e31d239a59"
CONSTRAINT_REGISTRATION = (
    "crg_870fe60d91056b6b1da9e3f734e5156cbb52722f6a0fc5f366f66cd40102a3df")
CONSTRAINT_DECLARATION = (
    "vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="st001_demo_fixture",
    method="manual_declaration")
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_operated")
REGISTRATION_RECORDED_AT = datetime(2026, 8, 31, 12, 0, tzinfo=UTC)
DECLARATION_RECORDED_AT = datetime(2026, 8, 31, 12, 1, tzinfo=UTC)
ANCHOR_NAMESPACE = "demo-printer"
ANCHOR_DISPLAY_NAME = "Synthetic Region Alpha"
ANCHOR_ROLE_NAME = None
REGISTRATION_NOTE = "ST-001 bounded synthetic state registration."
DECLARATION_NOTE = "ST-001 bounded synthetic state declaration."
REGISTRATION_STATEMENT = (
    "ST-001 fixture authority explicitly registers this opaque synthetic "
    "state identity for the cited entity and permanent singleton constraint; "
    "illustrative fixture only."
)
DECLARATION_STATEMENT = (
    "ST-001 fixture authority explicitly declares the exact pinned all-of "
    "constraint region under the stated lifecycle context and evaluation "
    "basis; illustrative fixture only."
)
DISCLAIMER = (
    "This is an illustrative synthetic ST-001 state declaration and evidence "
    "classification fixture. `matches` means only that the explicitly "
    "selected admitted observation satisfied the referenced synthetic "
    "constraint under the stated context, cutoff, and revisions. It does not "
    "claim that a real printer is currently in this state, that the state is "
    "exclusive or complete, that any transition occurred, or that temporal "
    "order establishes cause, control, safety, health, diagnosis, correctness, "
    "or recommended action."
)
WARNINGS = (
    "Names, shared ownership, hierarchy, CAD, ports, VPA, PIF, PCN, PCM, BH "
    "declarations, semantic compatibility, CN satisfaction alone, temporal "
    "correlation, and observation changes did not create the state.",
    "Displaying an observation beside a state does not persist it as state "
    "truth.",
    "The declaration is applied relative to evidence at the cutoff; this does "
    "not claim that the declaration existed at the cutoff or that the "
    "observation persisted.",
)
RAW_AUTHENTICITY_LIMITATION = (
    "ST proves the internal coherence of carried public results and does not "
    "independently authenticate uncaptured raw payload bytes."
)


def canonical_json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tree_inventory(*roots: Path) -> dict[str, str]:
    result = {}
    for root in roots:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            key = f"{root.as_posix()}/{path.relative_to(root).as_posix()}"
            result[key] = sha256_bytes(path.read_bytes())
    return result


def record_inventory(root: Path, record_ids) -> dict[str, str]:
    return {
        f"{record_id}.json": sha256_bytes(
            (root / "records" / f"{record_id}.json").read_bytes())
        for record_id in record_ids
    }


def inventory_digest(inventory: dict[str, str]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(sorted(inventory.items()))))


def compact_record_payload(record) -> tuple[dict, bytes]:
    return kernel_canonical_payload(record), kernel_canonical_bytes(record)


def source_selector() -> SourceSelector:
    return SourceSelector(subject=SUBJECT, property=PROP_TEMP)


def candidate_records(anchor: StateAnchor):
    anchor = StateAnchor.model_validate(anchor.model_dump(mode="python"))
    registration = kernel.build_record(
        kernel.StateRegistration,
        anchor=anchor,
        subject_entity_anchor_id=SUBJECT_ENTITY,
        condition_constraint_anchor_ids=(CONSTRAINT,),
        condition_family="all_of_constraints",
        evidence=(
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=SUBJECT_ENTITY_REGISTRATION),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=CONSTRAINT_REGISTRATION),
            kernel.OwnerDeclarationEvidence(
                kind="owner_declaration", statement=REGISTRATION_STATEMENT),
        ),
        recorded_at=REGISTRATION_RECORDED_AT,
        authority=AUTHORITY,
        note=REGISTRATION_NOTE,
    )
    declaration = kernel.build_record(
        kernel.StateDeclaration,
        state_anchor_id=anchor.anchor_id,
        context=CONTEXT,
        conditions=(kernel.StateConstraintDeclarationPin(
            constraint_anchor_id=CONSTRAINT,
            constraint_declaration_record_id=CONSTRAINT_DECLARATION,
        ),),
        evaluation_basis="independent_latest_at_or_before_cutoff",
        evidence=(
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=registration.record_id),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=CONSTRAINT_REGISTRATION),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=CONSTRAINT_DECLARATION),
            kernel.OwnerDeclarationEvidence(
                kind="owner_declaration", statement=DECLARATION_STATEMENT),
        ),
        supersedes=(),
        recorded_at=DECLARATION_RECORDED_AT,
        authority=AUTHORITY,
        note=DECLARATION_NOTE,
    )
    return registration, declaration


def manifest_content(path: Path = MANIFEST_PATH):
    raw = path.read_bytes()
    payload = json.loads(raw)
    assert raw == canonical_json_bytes(payload)
    checksum = payload["manifest_checksum"]
    assert checksum == {
        "algorithm": "sha256",
        "scope": "content",
        "value": sha256_bytes(canonical_json_bytes(payload["content"])),
    }
    content = payload["content"]
    assert payload["schema_version"] == "1"
    assert payload["status"] == "non_authoritative_candidate"
    assert content["accepted_source_head"] == ACCEPTED_SLICE_C_HEAD
    assert content["base_model_revision"] == BASE_REVISION
    anchor = StateAnchor.model_validate(content["state_anchor"])
    assert anchor.model_dump(mode="json") == content["state_anchor"]
    return payload, content, anchor, raw


def prepare_disposable_store(root: Path, *, predecessor_copy_order=None):
    root = root.resolve()
    authoritative = DEMO_MODEL.resolve()
    if root == authoritative or authoritative.is_relative_to(root):
        raise AssertionError("rehearsal root must not contain the ledger")
    source_ids = (tuple(BH001_MEMBERSHIP)
                  if predecessor_copy_order is None
                  else tuple(predecessor_copy_order))
    assert len(source_ids) == 32
    assert set(source_ids) == set(BH001_MEMBERSHIP)
    source_names = {
        path.stem for path in (DEMO_MODEL / "records").glob("*.json")}
    assert source_names == set(FL001_MEMBERSHIP)
    source_before = record_inventory(DEMO_MODEL, BH001_MEMBERSHIP)
    store = kernel.ModelStore(root / "demo-printer")
    for record_id in source_ids:
        source = DEMO_MODEL / "records" / f"{record_id}.json"
        target = store.records_dir / source.name
        shutil.copyfile(source, target)
    assert record_inventory(
        store.records_dir.parent, BH001_MEMBERSHIP) == source_before
    base = store.replay(BH001_MEMBERSHIP)
    assert base.revision.revision_id == BASE_REVISION
    assert base.revision.record_count == 32
    return store, source_before, base


def historical_revisions(state_anchor_id: str):
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
        (BH001_MEMBERSHIP, BASE_REVISION, 32),
    )
    rows = []
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        queries = kernel.ModelQueries(loaded)
        assert queries.state(state_anchor_id).status == "not_registered"
        assert queries.state_declaration(
            state_anchor_id, context=CONTEXT).conclusion == "not_registered"
        assert queries.states_of_entity(
            SUBJECT_ENTITY, context=CONTEXT).entries == ()
        rows.append({
            "record_count": count,
            "revision_id": revision,
            "record_ids": list(loaded.revision.record_ids),
            "candidate_state_status": "not_registered",
        })
    return rows


def query_disclosure(base, final, anchor, records):
    registration_record, declaration_record = records
    current = kernel.ModelQueries(final)
    historical = kernel.ModelQueries(base)
    lookup = current.state(anchor.anchor_id)
    declaration = current.state_declaration(
        anchor.anchor_id, context=CONTEXT)
    entity_states = current.states_of_entity(
        SUBJECT_ENTITY, context=CONTEXT)
    registration_assertion = current.state_assertion(
        registration_record.record_id)
    declaration_assertion = current.state_assertion(
        declaration_record.record_id)

    assert lookup.status == "registered"
    assert lookup.registration == registration_record
    assert declaration.conclusion == "declared"
    assert declaration.lineage_summary == "healthy"
    assert declaration.agreement_findings == ("one_healthy_root",)
    assert len(declaration.roots) == 1
    assert declaration.roots[0].root_record == declaration_record
    assert declaration.roots[0].current_tips == (declaration_record,)
    assert declaration.roots[0].lineage_health == "healthy"
    assert declaration.roots[0].withdrawals == ()
    assert len(declaration.effective_body_groups) == 1
    assert len(entity_states.entries) == 1
    assert entity_states.entries[0].state_anchor_id == anchor.anchor_id
    assert entity_states.entries[0].conclusion == "declared"
    assert registration_assertion.lookup_status == "found"
    assert registration_assertion.activity is None
    assert registration_assertion.root_record_index is None
    assert declaration_assertion.lookup_status == "found"
    assert declaration_assertion.activity == "current"
    assert declaration_assertion.containing_lineage_health == "healthy"
    assert declaration_assertion.root_record == declaration_record
    assert declaration_assertion.successors == ()
    assert declaration_assertion.withdrawals == ()

    historical_lookup = historical.state(anchor.anchor_id)
    historical_declaration = historical.state_declaration(
        anchor.anchor_id, context=CONTEXT)
    historical_entity = historical.states_of_entity(
        SUBJECT_ENTITY, context=CONTEXT)
    historical_srg = historical.state_assertion(registration_record.record_id)
    historical_std = historical.state_assertion(declaration_record.record_id)
    assert historical_lookup.status == "not_registered"
    assert historical_declaration.conclusion == "not_registered"
    assert historical_entity.status == "registered"
    assert historical_entity.entries == ()
    assert historical_srg.lookup_status == "not_found"
    assert historical_std.lookup_status == "not_found"

    return {
        "state": lookup.model_dump(mode="json"),
        "state_declaration": declaration.model_dump(mode="json"),
        "states_of_entity": entity_states.model_dump(mode="json"),
        "state_assertion_registration": (
            registration_assertion.model_dump(mode="json")),
        "state_assertion_declaration": (
            declaration_assertion.model_dump(mode="json")),
        "historical_32": {
            "state": historical_lookup.model_dump(mode="json"),
            "state_declaration": historical_declaration.model_dump(
                mode="json"),
            "states_of_entity": historical_entity.model_dump(mode="json"),
            "registration_assertion": historical_srg.model_dump(mode="json"),
            "declaration_assertion": historical_std.model_dump(mode="json"),
        },
        "summary": {
            "lookup_status": lookup.status,
            "declaration_conclusion": declaration.conclusion,
            "lineage_summary": declaration.lineage_summary,
            "agreement_findings": list(declaration.agreement_findings),
            "root_count": len(declaration.roots),
            "entity_entry_count": len(entity_states.entries),
            "registration_assertion_lookup": (
                registration_assertion.lookup_status),
            "declaration_assertion_activity": declaration_assertion.activity,
            "declaration_assertion_lineage_health": (
                declaration_assertion.containing_lineage_health),
        },
    }


def evaluation_disclosure(work_root: Path, final, anchor):
    semantic, _, _, temporal = semantic_stack(work_root, model=final)
    constraints = ConstraintEvaluationQueries(semantic)
    selector = source_selector()
    direct = constraints.constraint_evaluation(
        CONSTRAINT,
        as_of=AS_OF,
        entity_anchor_id=SUBJECT_ENTITY,
        source=selector,
    )
    classification = StateClassificationQueries(
        constraints).state_classification(
            anchor.anchor_id,
            context=CONTEXT,
            as_of=AS_OF,
            condition_sources=(StateConditionSource(
                constraint_anchor_id=CONSTRAINT, source=selector),),
        )
    assert classification.constraint_evaluations == (direct,)
    assert classification.state == kernel.ModelQueries(
        final).state_declaration(anchor.anchor_id, context=CONTEXT)
    assert direct.constraint.status == "declared"
    assert direct.constraint.declaration.record_id == CONSTRAINT_DECLARATION
    assert len(direct.candidates) == 1
    assert direct.candidates[0].observed_decimal == "60.4"
    assert direct.candidates[0].verdict == "satisfied"
    [assessment] = direct.candidates[0].boundary_assessments
    assert assessment.side == "upper"
    assert assessment.boundary.value == "80"
    assert assessment.boundary.inclusion == "inclusive"
    assert assessment.satisfied is True
    assert len(classification.conditions) == 1
    condition = classification.conditions[0]
    assert condition.declaration_alignment == "exact_current"
    assert condition.outcome == "satisfied"
    assert classification.condition_coverage == "complete"
    assert classification.temporal_alignment == "not_asserted"
    assert classification.execution == "executed"
    assert classification.computed_match == "matches"
    assert classification.refusals == ()

    semantic_candidate = direct.semantic_compatibility.candidates[0]
    occurrence = (semantic_candidate.value_candidate.state_candidate.bound
                  .observed.occurrence)
    provenance = temporal.provenance(occurrence.occurrence_id)
    assert occurrence.value_json == LATEST_VALUE
    assert occurrence.received_at == LATEST_RECEIVED_AT
    assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
    assert occurrence.attempt_id == LATEST_ATTEMPT_ID
    assert occurrence.observation_id == LATEST_OBSERVATION_ID
    assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
    assert occurrence.payload_checksum == LATEST_CHECKSUM
    assert provenance.raw_record_id == LATEST_RAW_RECORD_ID
    assert provenance.payload_checksum == LATEST_CHECKSUM

    state_result = (direct.semantic_compatibility.value_compatibility.state)
    return {
        "source_selector": selector.model_dump(mode="json"),
        "cutoff": AS_OF.isoformat(),
        "direct_constraint_evaluation": direct.model_dump(mode="json"),
        "state_classification": classification.model_dump(mode="json"),
        "summary": {
            "constraint_status": direct.constraint.status,
            "current_constraint_declaration_id": (
                direct.constraint.declaration.record_id),
            "observed_decimal": direct.candidates[0].observed_decimal,
            "predicate": direct.constraint.declaration.predicate.model_dump(
                mode="json"),
            "constraint_verdict": direct.candidates[0].verdict,
            "state_conclusion": classification.state.conclusion,
            "state_lineage_summary": classification.state.lineage_summary,
            "declaration_alignment": condition.declaration_alignment,
            "condition_outcome": condition.outcome,
            "condition_coverage": classification.condition_coverage,
            "temporal_alignment": classification.temporal_alignment,
            "execution": classification.execution,
            "refusals": [],
            "computed_match": classification.computed_match,
        },
        "occurrence": occurrence.model_dump(mode="json"),
        "provenance": provenance.model_dump(mode="json"),
        "provenance_axes": {
            "model_revision": final.revision.revision_id,
            "binding_revision": state_result.binding_revision.revision_id,
            "interpretation_revision": (
                direct.semantic_compatibility.interpretation_revision
                .revision_id),
            "temporal_cutoff": AS_OF.isoformat(),
            "declaration_recorded_at": (
                DECLARATION_RECORDED_AT.isoformat()),
            "statement": (
                "Model, binding, interpretation, and temporal cutoff remain "
                "separate. The later model declaration is applied relative "
                "to evidence at the cutoff; neither declaration existence at "
                "the cutoff nor observation persistence is claimed."
            ),
        },
    }


def accepted_artifacts(work_root: Path):
    pt = pt_artifact_bytes()
    vp = vp_artifact_bytes(work_root / "vp")
    bh = bh_authoritative_reproduction(work_root / "bh")
    assert len(pt) == PT_ARTIFACT_BYTES
    assert sha256_bytes(pt) == PT_ARTIFACT_SHA256
    assert len(vp) == VP_ARTIFACT_BYTES
    assert sha256_bytes(vp) == VP_ARTIFACT_SHA256
    assert bh["artifact_bytes"] == 122406
    assert bh["artifact_sha256"] == (
        "4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3")
    return {
        "pt": {"bytes": len(pt), "sha256": sha256_bytes(pt)},
        "vp": {"bytes": len(vp), "sha256": sha256_bytes(vp)},
        "bh": {
            "bytes": bh["artifact_bytes"],
            "sha256": bh["artifact_sha256"],
        },
    }


def artifact_bytes(*, anchor, records, final, candidate_files,
                   predecessor_hashes, queries, evaluation, artifacts,
                   histories, protected_hashes):
    registration, declaration = records
    candidate_record_disclosures = []
    for record in records:
        payload, raw = compact_record_payload(record)
        candidate_record_disclosures.append({
            "record": record.model_dump(mode="json"),
            "canonical_payload": payload,
            "canonical_bytes": raw.decode("utf-8"),
            "canonical_payload_bytes": len(raw),
            "canonical_payload_sha256": sha256_bytes(raw),
            "record_id_verification": {
                "computed_record_id": compute_record_id(record),
                "verified": verify_record_id(record),
            },
            "stored_file": candidate_files[f"{record.record_id}.json"],
        })
    content = {
        "scope": {
            "authoritative_append_performed": False,
            "candidate_records": {
                "state_registration": 1,
                "state_declaration": 1,
                "state_declaration_withdrawal": 0,
                "correction": 0,
                "second_root": 0,
                "other": 0,
            },
            "statement": (
                "This owner-gate artifact is generated only from disposable "
                "ledgers. No authoritative fixture is mutated."
            ),
        },
        "state_anchor": anchor.model_dump(mode="json"),
        "authority": AUTHORITY.model_dump(mode="json"),
        "context": CONTEXT.model_dump(mode="json"),
        "model": {
            "predecessor_revision": BASE_REVISION,
            "predecessor_membership": list(BH001_MEMBERSHIP),
            "candidate_append_order": [
                registration.record_id, declaration.record_id],
            "candidate_membership": list(final.revision.record_ids),
            "candidate_revision": final.revision.model_dump(mode="json"),
            "predecessor_file_sha256": dict(
                sorted(predecessor_hashes.items())),
            "predecessor_aggregate_sha256": inventory_digest(
                predecessor_hashes),
            "candidate_records": candidate_record_disclosures,
        },
        "kernel_queries": queries,
        "constraint_evaluation": {
            "full_result": evaluation["direct_constraint_evaluation"],
            "summary": evaluation["summary"],
        },
        "state_classification": {
            "full_result": evaluation["state_classification"],
            "summary": evaluation["summary"],
        },
        "temporal_evidence": {
            "cutoff": evaluation["cutoff"],
            "source_selector": evaluation["source_selector"],
            "occurrence": evaluation["occurrence"],
            "provenance": evaluation["provenance"],
        },
        "provenance_axes": evaluation["provenance_axes"],
        "historical_replay": histories,
        "preservation": {
            "accepted_artifacts": artifacts,
            "protected_tree_aggregate_sha256": protected_hashes,
        },
        "raw_authenticity_limitation": RAW_AUTHENTICITY_LIMITATION,
    }
    content_raw = canonical_json_bytes(content)
    return canonical_json_bytes({
        "artifact": "ST-001 demo-printer state disclosure candidate",
        "schema_version": "1",
        "disclaimer": DISCLAIMER,
        "warnings": list(WARNINGS),
        "artifact_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": sha256_bytes(content_raw),
        },
        "content": content,
    })


def run_rehearsal(root: Path, *, manifest=None,
                  predecessor_copy_order=None, enforce_manifest=True):
    root = root.resolve()
    if manifest is None:
        manifest, content, anchor, _ = manifest_content()
    else:
        content = manifest["content"]
        anchor = StateAnchor.model_validate(content["state_anchor"])
    records = candidate_records(anchor)
    store, source_before, base = prepare_disposable_store(
        root / "ledger", predecessor_copy_order=predecessor_copy_order)
    protected_roots = (
        DEMO_MODEL,
        Path("bindings/demo-printer"),
        Path("bindings/demo-printer-model"),
        Path("interpretations/demo-printer"),
        Path("showcases/demo-printer"),
    )
    protected_before = tree_inventory(*protected_roots)
    runtime_evidence_before = tree_inventory(Path("var/raw_store"))
    candidate_raw = {}
    for expected_count, record in zip((33, 34), records, strict=True):
        assert store.append(record) == record.record_id
        path = store.records_dir / f"{record.record_id}.json"
        raw = path.read_bytes()
        candidate_raw[f"{record.record_id}.json"] = raw
        loaded_step = store.load()
        assert loaded_step.revision.record_count == expected_count
        assert loaded_step.records[record.record_id] == record

    candidate_ids = tuple(record.record_id for record in records)
    membership = tuple(sorted((*BH001_MEMBERSHIP, *candidate_ids)))
    final = store.replay(membership)
    assert final.revision.record_count == 34
    assert final.revision.record_ids == membership
    assert store.load().revision == final.revision
    assert set(membership) - set(BH001_MEMBERSHIP) == set(candidate_ids)
    assert len(final.state_registrations) == 1
    assert len(final.state_declarations) == 1
    assert len(final.state_declaration_withdrawals) == 0
    assert records[1].supersedes == ()

    source_after = record_inventory(
        store.records_dir.parent, BH001_MEMBERSHIP)
    assert source_after == source_before
    candidate_files = {
        filename: {
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
            "stored_json": raw.decode("utf-8"),
        }
        for filename, raw in candidate_raw.items()
    }
    record_contracts = []
    for record in records:
        payload, compact = compact_record_payload(record)
        assert compact == kernel_canonical_bytes(record)
        assert payload == kernel_canonical_payload(record)
        assert sha256_bytes(compact) == record.record_id.split("_", 1)[1]
        assert compute_record_id(record) == record.record_id
        assert verify_record_id(record) is True
        filename = f"{record.record_id}.json"
        record_contracts.append({
            "record_id": record.record_id,
            "canonical_payload": payload,
            "canonical_bytes": compact.decode("utf-8"),
            "canonical_payload_bytes": len(compact),
            "canonical_payload_sha256": sha256_bytes(compact),
            **candidate_files[filename],
        })

    queries = query_disclosure(base, final, anchor, records)
    evaluation = evaluation_disclosure(root / "evaluation", final, anchor)
    histories = historical_revisions(anchor.anchor_id)
    artifacts = accepted_artifacts(root / "accepted-artifacts")
    protected_after = tree_inventory(*protected_roots)
    assert protected_after == protected_before
    runtime_evidence_after = tree_inventory(Path("var/raw_store"))
    assert runtime_evidence_after == runtime_evidence_before
    protected_digest = content["predecessor"][
        "protected_tree_aggregate_sha256"]
    artifact = artifact_bytes(
        anchor=anchor,
        records=records,
        final=final,
        candidate_files=candidate_files,
        predecessor_hashes=source_before,
        queries=queries,
        evaluation=evaluation,
        artifacts=artifacts,
        histories=histories,
        protected_hashes={"aggregate_sha256": protected_digest},
    )
    result = {
        "resolved_root": root.as_posix(),
        "state_anchor": anchor.model_dump(mode="json"),
        "records": [record.model_dump(mode="json") for record in records],
        "record_ids": list(candidate_ids),
        "record_contracts": record_contracts,
        "candidate_record_bytes": candidate_raw,
        "append_order": list(candidate_ids),
        "membership": list(membership),
        "revision": final.revision.model_dump(mode="json"),
        "queries": queries,
        "evaluation": evaluation,
        "predecessor_sha256": source_before,
        "predecessor_aggregate_sha256": inventory_digest(source_before),
        "protected_aggregate_sha256": protected_digest,
        "authoritative_tree_aggregate_sha256": inventory_digest(
            protected_before),
        "runtime_evidence_unchanged": True,
        "accepted_artifacts": artifacts,
        "artifact": artifact,
        "artifact_bytes": len(artifact),
        "artifact_sha256": sha256_bytes(artifact),
    }
    if enforce_manifest:
        expected = content["candidate_contract"]
        assert result["state_anchor"] == content["state_anchor"]
        assert result["records"] == expected["records"]
        assert result["record_ids"] == expected["record_ids"]
        assert result["record_contracts"] == expected["record_contracts"]
        assert result["append_order"] == expected["append_order"]
        assert result["membership"] == expected["membership"]
        assert result["revision"] == expected["revision"]
        assert result["predecessor_aggregate_sha256"] == content[
            "predecessor"]["aggregate_sha256"]
        assert result["artifact_bytes"] == content["artifact"]["bytes"]
        assert result["artifact_sha256"] == content["artifact"]["sha256"]
    return result


def build_manifest(anchor: StateAnchor, result) -> dict:
    registration, declaration = candidate_records(anchor)
    semantic_inputs = {
        "anchor_allocation": {
            "api": "backend.system_identity.mint_state_anchor",
            "arguments": {
                "namespace": ANCHOR_NAMESPACE,
                "display_name": ANCHOR_DISPLAY_NAME,
                "role_name": ANCHOR_ROLE_NAME,
            },
            "statement": (
                "The public UUID4 minter was invoked exactly once. UUID4 "
                "allocation is intentionally nondeterministic; this manifest "
                "freezes the returned opaque identity for all reproductions."
            ),
        },
        "state_registration": {
            "subject_entity_anchor_id": SUBJECT_ENTITY,
            "condition_constraint_anchor_ids": [CONSTRAINT],
            "condition_family": "all_of_constraints",
            "evidence": [item.model_dump(mode="json")
                         for item in registration.evidence],
            "recorded_at": REGISTRATION_RECORDED_AT.isoformat(),
            "authority": AUTHORITY.model_dump(mode="json"),
            "note": REGISTRATION_NOTE,
        },
        "state_declaration": {
            "state_anchor_id": anchor.anchor_id,
            "context": CONTEXT.model_dump(mode="json"),
            "conditions": [item.model_dump(mode="json")
                           for item in declaration.conditions],
            "evaluation_basis": (
                "independent_latest_at_or_before_cutoff"),
            "evidence": [item.model_dump(mode="json")
                         for item in declaration.evidence],
            "supersedes": [],
            "recorded_at": DECLARATION_RECORDED_AT.isoformat(),
            "authority": AUTHORITY.model_dump(mode="json"),
            "note": DECLARATION_NOTE,
        },
    }
    content = {
        "accepted_source_head": ACCEPTED_SLICE_C_HEAD,
        "base_model_revision": BASE_REVISION,
        "canonicalization": {
            "module": "backend.model_kernel.canonical",
            "payload_function": "canonical_payload",
            "bytes_function": "canonical_bytes",
            "record_id_function": "compute_record_id",
            "verification_function": "verify_record_id",
            "utc_representation": "+00:00",
            "statement": (
                "Every field named canonical is derived directly from the "
                "model kernel's normative canonical_payload(record) or "
                "canonical_bytes(record) result."
            ),
        },
        "state_anchor": anchor.model_dump(mode="json"),
        "semantic_inputs": semantic_inputs,
        "candidate_contract": {
            "records": result["records"],
            "record_ids": result["record_ids"],
            "record_contracts": result["record_contracts"],
            "append_order": result["append_order"],
            "predecessor_membership": list(BH001_MEMBERSHIP),
            "membership": result["membership"],
            "revision": result["revision"],
        },
        "expected_public_results": {
            "kernel": result["queries"]["summary"],
            "classification": result["evaluation"]["summary"],
        },
        "classification_request": {
            "state_anchor_id": anchor.anchor_id,
            "context": CONTEXT.model_dump(mode="json"),
            "as_of": AS_OF.isoformat(),
            "condition_sources": [{
                "constraint_anchor_id": CONSTRAINT,
                "source": source_selector().model_dump(mode="json"),
            }],
        },
        "artifact": {
            "path": DISCLOSURE_PATH.as_posix(),
            "bytes": result["artifact_bytes"],
            "sha256": result["artifact_sha256"],
            "schema_version": "1",
        },
        "predecessor": {
            "record_count": 32,
            "revision": BASE_REVISION,
            "membership": list(BH001_MEMBERSHIP),
            "record_file_sha256": result["predecessor_sha256"],
            "aggregate_sha256": result["predecessor_aggregate_sha256"],
            "protected_tree_aggregate_sha256": (
                result["protected_aggregate_sha256"]),
            "accepted_artifacts": result["accepted_artifacts"],
        },
        "disclaimer": DISCLAIMER,
        "warnings": list(WARNINGS),
        "raw_authenticity_limitation": RAW_AUTHENTICITY_LIMITATION,
    }
    return {
        "schema_version": "1",
        "status": "non_authoritative_candidate",
        "manifest_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": sha256_bytes(canonical_json_bytes(content)),
        },
        "content": content,
    }


def allocation_outputs(anchor: StateAnchor, root: Path):
    seed = {
        "schema_version": "1",
        "status": "allocation_in_progress",
        "content": {
            "state_anchor": anchor.model_dump(mode="json"),
        },
    }
    result = run_rehearsal(
        root, manifest=seed, enforce_manifest=False)
    manifest = build_manifest(anchor, result)
    return canonical_json_bytes(manifest), result["artifact"], result


def reproduction_summary(result):
    return {
        "state_anchor": result["state_anchor"],
        "record_ids": result["record_ids"],
        "record_contracts": result["record_contracts"],
        "append_order": result["append_order"],
        "membership": result["membership"],
        "revision": result["revision"],
        "queries": result["queries"],
        "evaluation": result["evaluation"],
        "predecessor_aggregate_sha256": (
            result["predecessor_aggregate_sha256"]),
        "accepted_artifacts": result["accepted_artifacts"],
        "artifact_bytes": result["artifact_bytes"],
        "artifact_sha256": result["artifact_sha256"],
    }
