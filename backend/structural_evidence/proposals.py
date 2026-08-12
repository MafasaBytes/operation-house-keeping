"""SN-001 inert model proposals.

A proposal carries ONLY the inputs an authority must decide over — an
existing declared anchor id, source-vocabulary endpoints, cited evidence
— never a constructed record and never a kernel record id.
`caller_must_supply` names the values SN-001 structurally cannot know:
`authority` (who accepted), `context` (which lifecycle view),
`recorded_at` (when), `type_id` (which type-lineage tip is current in the
accepting revision). That asymmetry is the structural proof that
acceptance is a separate act. A proposal names NO model type: even the
containment kind stays in the source's vocabulary.

`sxp_` is structurally excluded from the kernel's record-id pattern, and
this module writes nothing anywhere.
"""

import hashlib
import json
from types import MappingProxyType
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.model_kernel import (
    EvidenceRef,
    SourceRawRecordEvidence,
)
from backend.structural_evidence.locators import to_kernel_evidence
from backend.structural_evidence.reconcile import (
    ReconciliationFinding,
    StructuralReconciliationResult,
    _canon,
)
from backend.system_identity import ENTITY_ANCHOR_ID_PATTERN


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


REQUIRED_BY_PROPOSAL_KIND: Mapping[str, tuple] = MappingProxyType({
    "entity_registration": ("authority", "recorded_at"),
    "relationship_assertion": ("authority", "context", "recorded_at",
                               "type_id"),
})


def _proposal_id(payload: dict) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False)
    return "sxp_" + hashlib.sha256(material.encode("utf-8")).hexdigest()


class EntityRegistrationProposal(_Frozen):
    """Propose registering an anchor that is DECLARED in a participating
    binding set and positively joined, but not yet registered in the
    supplied model revision. The anchor's referent kind lives in its
    declaration — this proposal claims nothing about physicality."""

    proposal_kind: Literal["entity_registration"]
    proposal_id: str = Field(pattern=r"^sxp_[0-9a-f]{64}$")
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    supporting: tuple[ReconciliationFinding, ...] = Field(min_length=1)
    caller_must_supply: tuple[Literal["authority", "recorded_at"], ...]

    @model_validator(mode="after")
    def _caller_tuple_is_frozen(self):
        if self.caller_must_supply != \
                REQUIRED_BY_PROPOSAL_KIND["entity_registration"]:
            raise ValueError("caller_must_supply must be exactly the "
                             "frozen table entry")
        return self


class RelationshipAssertionProposal(_Frozen):
    """Propose asserting an edge between two registered anchors, in the
    SOURCE'S vocabulary: `source_containment_kind` names what the source
    reported, never a model relationship type. The accepting authority
    supplies the type id (the current lineage tip in their revision), the
    context, the recorded_at, and their own authority."""

    proposal_kind: Literal["relationship_assertion"]
    proposal_id: str = Field(pattern=r"^sxp_[0-9a-f]{64}$")
    source_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    target_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    source_containment_kind: Literal["bom_parent_column",
                                     "step_nauo_usage_edge"]
    evidence_inputs: tuple[EvidenceRef, ...] = Field(min_length=1)
    supporting: tuple[ReconciliationFinding, ...] = Field(min_length=1)
    caller_must_supply: tuple[Literal["authority", "context",
                                      "recorded_at", "type_id"], ...]

    @model_validator(mode="after")
    def _caller_tuple_is_frozen(self):
        if self.caller_must_supply != \
                REQUIRED_BY_PROPOSAL_KIND["relationship_assertion"]:
            raise ValueError("caller_must_supply must be exactly the "
                             "frozen table entry")
        return self


class ModelProposalResult(_Frozen):
    """Computed and returned, never persisted. `blocking_findings` lists
    the findings that blocked a candidate proposal; they may coexist with
    proposals for other candidates."""

    status: Literal["proposable", "not_proposable"]
    proposals: tuple[EntityRegistrationProposal
                     | RelationshipAssertionProposal, ...] = ()
    blocking_findings: tuple[ReconciliationFinding, ...] = ()
    reconciliation: StructuralReconciliationResult

    @model_validator(mode="after")
    def _status_consistent(self):
        if (self.status == "proposable") != bool(self.proposals):
            raise ValueError("proposable exactly when proposals exist")
        return self


def _joined_members(reconciliation):
    for disclosure in reconciliation.claim_sets:
        for rs in disclosure.resolved_subjects:
            if rs.join_anchor_id is not None:
                yield disclosure, rs


def _declared_anywhere(reconciliation, findings_by_anchor, anchor_id):
    # a registration proposal needs a declared anchor: the join itself
    # proves declaration (a binding assertion can only target a declared
    # anchor in its own set), so a joined anchor is always declared
    return True


def build_proposals(
        reconciliation: StructuralReconciliationResult) -> ModelProposalResult:
    findings_by_anchor: dict = {}
    for finding in reconciliation.findings:
        if finding.anchor_id:
            findings_by_anchor[finding.anchor_id] = (
                *findings_by_anchor.get(finding.anchor_id, ()), finding)

    registered = {
        anchor_id for anchor_id, findings in findings_by_anchor.items()
        if not any(f.finding == "anchor_not_registered" for f in findings)}
    joined_anchors = sorted({rs.join_anchor_id for _, rs in
                             _joined_members(reconciliation)})
    conflicted = any(
        f.finding in ("mapping_conflicted", "mapping_ambiguous",
                      "mapping_conflicted_across_sets",
                      "mappings_jointly_incoherent")
        for f in reconciliation.findings)

    registration_proposals = ()
    if not conflicted:
        for anchor_id in joined_anchors:
            if anchor_id in registered:
                continue
            supporting = findings_by_anchor.get(anchor_id, ())
            payload = dict(proposal_kind="entity_registration",
                           anchor_id=anchor_id,
                           supporting=[_canon(f) for f in supporting])
            registration_proposals = (*registration_proposals,
                                      EntityRegistrationProposal(
                                          proposal_kind="entity_registration",
                                          proposal_id=_proposal_id(payload),
                                          anchor_id=anchor_id,
                                          supporting=supporting,
                                          caller_must_supply=(
                                              "authority", "recorded_at")))

    # Endpoint resolution is keyed by the COMPLETE StructuralAddress —
    # payload, source identity, extractor, and locator — never by the
    # locator value alone: two sources both contain an r=1, and a
    # locator-only key let source B's join re-point source A's
    # containment claim (owner audit 2026-08-12, defect 1). An address
    # whose rules join it to DIFFERENT anchors is excluded outright:
    # silent last-writer-wins is the same defect class.
    joined_by_address = {}
    context_ok_by_address = {}
    conflicted_addresses = set()
    for disclosure, rs in _joined_members(reconciliation):
        key = rs.claim_address
        if key in joined_by_address and \
                joined_by_address[key] != rs.join_anchor_id:
            conflicted_addresses.add(key)
        joined_by_address[key] = rs.join_anchor_id
        ok = disclosure.claim_set.engineering_context.kind != "unknown"
        context_ok_by_address[key] = \
            context_ok_by_address.get(key, True) and ok

    edge_proposals = ()
    blocking = ()
    if not conflicted:
        for disclosure in reconciliation.claim_sets:
            for containment in disclosure.claim_set.containment_claims:
                child_key = containment.child
                parent_key = containment.parent
                if child_key in conflicted_addresses or \
                        parent_key in conflicted_addresses:
                    continue  # no single join: nothing to propose
                child_anchor = joined_by_address.get(child_key)
                parent_anchor = joined_by_address.get(parent_key)
                if child_anchor is None or parent_anchor is None:
                    continue  # unmapped endpoints: nothing to propose
                if not (context_ok_by_address[child_key]
                        and context_ok_by_address[parent_key]):
                    blocking = (*blocking, *(
                        f for f in reconciliation.findings
                        if f.finding == "context_unknown"
                        and f.anchor_id in (child_anchor, parent_anchor)))
                    continue
                if child_anchor not in registered or \
                        parent_anchor not in registered:
                    blocking = (*blocking, *(
                        f for f in reconciliation.findings
                        if f.finding == "anchor_not_registered"
                        and f.anchor_id in (child_anchor, parent_anchor)))
                    continue
                source_ref = containment.child.source
                evidence_inputs = (
                    to_kernel_evidence(containment.child).evidence,
                    to_kernel_evidence(containment.parent).evidence,
                    SourceRawRecordEvidence(
                        kind="source_raw_record",
                        raw_record_id=source_ref.raw_record_id,
                        payload_checksum=source_ref.payload_checksum))
                supporting = findings_by_anchor.get(child_anchor, ()) or \
                    findings_by_anchor.get(parent_anchor, ())
                payload = dict(proposal_kind="relationship_assertion",
                               source=parent_anchor, target=child_anchor,
                               kind=containment.claim_kind,
                               evidence=[_canon(e)
                                         for e in evidence_inputs])
                edge_proposals = (*edge_proposals,
                                  RelationshipAssertionProposal(
                                      proposal_kind="relationship_assertion",
                                      proposal_id=_proposal_id(payload),
                                      source_anchor_id=parent_anchor,
                                      target_anchor_id=child_anchor,
                                      source_containment_kind=(
                                          containment.claim_kind),
                                      evidence_inputs=evidence_inputs,
                                      supporting=supporting,
                                      caller_must_supply=(
                                          "authority", "context",
                                          "recorded_at", "type_id")))
    else:
        blocking = tuple(
            f for f in reconciliation.findings
            if f.finding in ("mapping_conflicted", "mapping_ambiguous",
                             "mapping_conflicted_across_sets",
                             "mappings_jointly_incoherent"))

    proposals = (*registration_proposals, *edge_proposals)
    return ModelProposalResult(
        status="proposable" if proposals else "not_proposable",
        proposals=proposals, blocking_findings=blocking,
        reconciliation=reconciliation)
