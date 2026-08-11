"""Inert proposals (P1-P8, commit 14).

A proposal carries no constructed record and no kernel record id;
acceptance requires the values SN-001 structurally cannot know
(authority, context, recorded_at, type_id), supplied by a person in a
separate, committed act. SN-001's public API contains no function that
writes to any store.
"""

import re

import pytest
from pydantic import ValidationError

from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.proposals import (
    REQUIRED_BY_PROPOSAL_KIND,
    EntityRegistrationProposal,
    ModelProposalResult,
    RelationshipAssertionProposal,
)
from backend.structural_evidence.reconcile import StructuralReconciler
from backend.structural_evidence.rules import SUBJECT_RULES

from tests.model_kernel.builders import registration, store_with
from tests.structural_evidence.helpers import (
    ENT_X,
    ENT_Y,
    RESOLUTION_AT,
    anchor_declaration,
    bom_claim,
    bom_claim_set,
    bom_source,
    declared_context,
    resolver_with,
    step_claim_set,
    subject_assertion,
    subject_for,
)

RULES = tuple(SUBJECT_RULES.values())
KERNEL_RECORD_ID = re.compile(r"^(reg|rtd|rel|rwd|vrg|vsp)_[0-9a-f]{64}$")


def model_with(tmp_path, *anchor_ids):
    return store_with(tmp_path,
                      *(registration(a) for a in anchor_ids)).load()


def run(tmp_path, claim_sets, resolvers, model):
    reconciler = StructuralReconciler(resolvers=resolvers, rules=RULES,
                                      model=model)
    reconciliation = reconciler.reconcile(claim_sets,
                                          resolution_at=RESOLUTION_AT)
    return reconciler, reconciler.propose(reconciliation)


class TestP1P2RegistrationProposals:
    def arrange(self, tmp_path, register=False):
        """BOM and STEP subjects both mapped to a DECLARED anchor; the
        anchor is registered in the model only when asked."""
        bom_set = bom_claim_set()
        step_set = step_claim_set()
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(subject_for(bom_set.subject_claims[0],
                                          "bom-item-no-v1"), ENT_X),
            subject_assertion(subject_for(step_set.subject_claims[0],
                                          "step-ocaf-entry-v1"), ENT_X))
        model = (model_with(tmp_path, ENT_X) if register
                 else model_with(tmp_path, ENT_Y))
        return [bom_set, step_set], [resolver], model

    def test_p2_one_declared_unregistered_anchor_one_proposal(
            self, tmp_path):
        claim_sets, resolvers, model = self.arrange(tmp_path)
        _, result = run(tmp_path, claim_sets, resolvers, model)
        proposals = [p for p in result.proposals
                     if p.proposal_kind == "entity_registration"]
        assert len(proposals) == 1
        [proposal] = proposals
        assert proposal.anchor_id == ENT_X
        assert result.status == "proposable"
        subjects = {f.subject.subject_identifier
                    for f in proposal.supporting if f.subject}
        assert len(proposal.supporting) >= 1

    def test_p1_conflicting_mappings_propose_nothing(self, tmp_path):
        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject, ENT_X),
            subject_assertion(subject, ENT_Y))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        _, result = run(tmp_path, [bom_set], [resolver], model)
        assert result.proposals == ()
        assert result.status == "not_proposable"

    def test_registered_anchor_needs_no_registration_proposal(
            self, tmp_path):
        claim_sets, resolvers, model = self.arrange(tmp_path, register=True)
        _, result = run(tmp_path, claim_sets, resolvers, model)
        assert [p for p in result.proposals
                if p.proposal_kind == "entity_registration"] == []


class TestP3NoPhysicalityClaim:
    def test_a_proposal_carries_no_referent_kind_and_no_record(
            self, tmp_path):
        claim_sets, resolvers, model = \
            TestP1P2RegistrationProposals().arrange(tmp_path)
        _, result = run(tmp_path, claim_sets, resolvers, model)
        [proposal] = result.proposals
        # The proposal's OWN contract carries no referent kind and no
        # physicality claim; the anchor's declared kind appears only
        # inside the carried-verbatim binding evidence, which is honest
        # disclosure of the AUTHORITY's earlier declaration.
        own_fields = set(type(proposal).model_fields)
        assert "referent_kind" not in own_fields
        assert not any("physical" in name for name in own_fields)
        assert not hasattr(proposal, "record")


class TestP7Inertness:
    def test_no_attribute_is_a_kernel_record_id(self, tmp_path):
        claim_sets, resolvers, model = \
            TestP1P2RegistrationProposals().arrange(tmp_path)
        _, result = run(tmp_path, claim_sets, resolvers, model)
        [proposal] = result.proposals

        def walk(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for v in value.values():
                    yield from walk(v)
            elif isinstance(value, (list, tuple)):
                for v in value:
                    yield from walk(v)

        for text in walk(proposal.model_dump(mode="json")):
            assert not KERNEL_RECORD_ID.fullmatch(text), text
        assert proposal.proposal_id.startswith("sxp_")

    def test_caller_must_supply_is_the_exact_frozen_tuple(self):
        assert REQUIRED_BY_PROPOSAL_KIND == {
            "entity_registration": ("authority", "recorded_at"),
            "relationship_assertion": ("authority", "context",
                                       "recorded_at", "type_id")}
        with pytest.raises(ValidationError):
            EntityRegistrationProposal.model_validate({
                "proposal_kind": "entity_registration",
                "proposal_id": "sxp_" + "0" * 64,
                "anchor_id": ENT_X,
                "supporting": (),
                "caller_must_supply": ("authority",)})  # wrong tuple


class TestP8UnknownContextNeverMaterializes:
    def test_containment_from_an_unknown_context_is_not_proposable(
            self, tmp_path):
        """Child and parent both joined and registered, but the claim
        set's context is unknown: no relationship proposal exists."""
        source = bom_source()
        child = bom_claim(source, 2, "EXT-100")
        parent = bom_claim(source, 1, "PRN-000")
        from backend.structural_evidence.contracts import (
            SourceContainmentClaim,
        )
        containment = SourceContainmentClaim(
            claim_kind="bom_parent_column", child=child.address,
            parent=parent.address)
        bom_set = bom_claim_set(claims=(parent, child),
                                containment=(containment,))
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject_for(child, "bom-item-no-v1"), ENT_X),
            subject_assertion(subject_for(parent, "bom-item-no-v1"), ENT_Y))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        _, unknown_result = run(tmp_path, [bom_set], [resolver], model)
        assert [p for p in unknown_result.proposals
                if p.proposal_kind == "relationship_assertion"] == []
        assert any(f.finding == "context_unknown"
                   for f in unknown_result.blocking_findings)
        # positive twin: a declared context makes the edge proposable
        declared_set = bom_claim_set(claims=(parent, child),
                                     containment=(containment,),
                                     context=declared_context("as_designed"))
        _, declared_result = run(tmp_path, [declared_set], [resolver],
                                 model)
        edges = [p for p in declared_result.proposals
                 if p.proposal_kind == "relationship_assertion"]
        assert len(edges) == 1
        [edge] = edges
        assert (edge.source_anchor_id, edge.target_anchor_id) == \
            (ENT_Y, ENT_X)  # parent contains child, source vocabulary
        assert edge.source_containment_kind == "bom_parent_column"
        assert len(edge.evidence_inputs) >= 2
        assert edge.caller_must_supply == ("authority", "context",
                                           "recorded_at", "type_id")


class TestP4UnregisteredEndpointBlocksEdges:
    def test_edge_with_unregistered_endpoint_is_blocked_not_proposed(
            self, tmp_path):
        source = bom_source()
        child = bom_claim(source, 2, "EXT-100")
        parent = bom_claim(source, 1, "PRN-000")
        from backend.structural_evidence.contracts import (
            SourceContainmentClaim,
        )
        bom_set = bom_claim_set(
            claims=(parent, child),
            containment=(SourceContainmentClaim(
                claim_kind="bom_parent_column", child=child.address,
                parent=parent.address),),
            context=declared_context("as_designed"))
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject_for(child, "bom-item-no-v1"), ENT_X),
            subject_assertion(subject_for(parent, "bom-item-no-v1"), ENT_Y))
        model = model_with(tmp_path, ENT_X)  # parent anchor unregistered
        before = model.revision.revision_id
        _, result = run(tmp_path, [bom_set], [resolver], model)
        assert [p for p in result.proposals
                if p.proposal_kind == "relationship_assertion"] == []
        assert any(f.finding == "anchor_not_registered"
                   for f in result.blocking_findings)
        assert model.revision.revision_id == before  # nothing written


class TestP5RevisionMismatch:
    def test_a_stale_reconciliation_is_refused_never_refreshed(
            self, tmp_path):
        claim_sets, resolvers, model = \
            TestP1P2RegistrationProposals().arrange(tmp_path)
        reconciler = StructuralReconciler(resolvers=resolvers, rules=RULES,
                                          model=model)
        reconciliation = reconciler.reconcile(claim_sets,
                                              resolution_at=RESOLUTION_AT)
        richer = resolver_with(
            tmp_path, "set-a2", anchor_declaration(ENT_X))
        other = StructuralReconciler(resolvers=[richer], rules=RULES,
                                     model=model)
        with pytest.raises(StructuralEvidenceError) as err:
            other.propose(reconciliation)
        assert err.value.error_code == "SN_REVISION_MISMATCH"


class TestP6AppendFailureHonesty:
    def test_partial_append_state_is_visible_in_counts_not_faked(
            self, tmp_path):
        """The kernel has no bulk append and SN-001 must not create one:
        a failed second append leaves the first record committed, and
        the honest observation is the count and revision, never a
        pretended rollback."""
        from backend.model_kernel import (
            ModelIntegrityError,
            ModelStore,
            build_record,
        )
        from backend.model_kernel.contracts import RelationshipAssertion
        from tests.model_kernel.builders import AS_BUILT, AUTHORITY
        from tests.model_kernel.builders import EVIDENCE, contains_type

        store = ModelStore(tmp_path / "acceptance-model")
        first = registration(ENT_X)
        store.append(first)
        assert store.load().revision.record_count == 1
        rtd = contains_type()
        store.append(rtd)
        bad_edge = build_record(
            RelationshipAssertion, type_id=rtd.record_id,
            source_anchor_id=ENT_X, target_anchor_id=ENT_Y,  # unregistered
            context=AS_BUILT, evidence=EVIDENCE,
            recorded_at="2026-08-11T12:00:00Z", authority=AUTHORITY)
        with pytest.raises(ModelIntegrityError):
            store.append(bad_edge)
        loaded = store.load()
        assert loaded.revision.record_count == 2  # partial state, visible
        assert first.record_id in loaded.revision.record_ids


class TestProposalResultShape:
    def test_status_is_consistent_with_proposals(self, tmp_path):
        claim_sets, resolvers, model = \
            TestP1P2RegistrationProposals().arrange(tmp_path)
        _, result = run(tmp_path, claim_sets, resolvers, model)
        assert (result.status == "proposable") == bool(result.proposals)
        with pytest.raises(ValidationError):
            ModelProposalResult(status="not_proposable",
                                proposals=result.proposals,
                                blocking_findings=(),
                                reconciliation=result.reconciliation)
