"""MK-001 contract shapes: record kinds, contexts, evidence, revision, and
result invariants — impossible states unrepresentable."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.model_kernel.canonical import build_record, compute_revision_id
from backend.model_kernel.contracts import (
    AuthorityRef,
    EntityRegistration,
    IdentityBindingRecordEvidence,
    LifecycleViewContext,
    LineageConflict,
    ModelIntegrityError,
    ModelRevision,
    OwnerDeclarationEvidence,
    ParentResult,
    RelationshipAssertion,
    RelationshipsResult,
    RelationshipSummary,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
    TraversalResult,
    ViewIndependentContext,
)
from backend.system_identity import EntityAnchor

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="mk001_demo_fixture",
                         method="manual_declaration")
ENT_A = "ent_" + "a" * 32
ENT_B = "ent_" + "b" * 32
RTD = "rtd_" + "0" * 64
REL = "rel_" + "1" * 64
AS_BUILT = LifecycleViewContext(kind="lifecycle_view", view="as_built")
VIEW_FREE = ViewIndependentContext(kind="view_independent")
EVIDENCE = (OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic demo structure"),)


def anchor(anchor_id=ENT_A, kind="physical_instance"):
    return EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                        display_name="Demo entity", referent_kind=kind)


def registration(**overrides):
    fields = dict(anchor=anchor(), recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(EntityRegistration, **fields)


def type_definition(**overrides):
    fields = dict(
        type_name="contains", forward_label="contains",
        inverse_label="is contained in", directionality="directed",
        source_referent_kinds=("logical_instance", "physical_instance"),
        target_referent_kinds=("logical_instance", "physical_instance"),
        self_relation_allowed=False, hierarchy_semantics="containment",
        context_requirement="lifecycle_view", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


def assertion(**overrides):
    fields = dict(type_id=RTD, source_anchor_id=ENT_A, target_anchor_id=ENT_B,
                  context=AS_BUILT, evidence=EVIDENCE, supersedes=None,
                  recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipAssertion, **fields)


class TestRecordShapes:
    def test_registration_has_no_lifecycle(self):
        """Registrations are lifecycle-free: no supersedes field exists, and
        a mistaken registration has no kernel correction path. Through the
        operational `build_record` API the rejection is typed."""
        with pytest.raises(ModelIntegrityError):
            registration(supersedes=None)

    def test_registration_embeds_full_anchor_verbatim(self):
        record = registration()
        assert record.anchor.referent_kind == "physical_instance"
        assert record.record_id.startswith("reg_")
        with pytest.raises(ValidationError):
            record.anchor.display_name = "renamed"  # frozen all the way down

    def test_frozen_and_extra_forbid_on_every_kind(self):
        for record in (registration(), type_definition(), assertion()):
            with pytest.raises(ValidationError):
                record.note = "edited"
        with pytest.raises(ModelIntegrityError):
            registration(unexpected_field="x")

    def test_type_definition_lineage_fields(self):
        record = type_definition()
        assert record.record_id.startswith("rtd_")
        assert record.hierarchy_semantics == "containment"
        with pytest.raises(ModelIntegrityError):
            type_definition(directionality="symmetric")  # MK-001: directed only
        with pytest.raises(ModelIntegrityError):
            type_definition(type_name="Contains")  # lowercase machine names

    def test_containment_with_self_relation_rejected_at_construction(self):
        with pytest.raises(ModelIntegrityError):
            type_definition(self_relation_allowed=True)

    def test_endpoint_kind_tuples_normalized_sorted_unique(self):
        record = type_definition(source_referent_kinds=(
            "physical_instance", "logical_instance", "physical_instance"))
        assert record.source_referent_kinds == ("logical_instance",
                                                "physical_instance")

    def test_unknown_is_an_explicit_optin_member_never_default(self):
        permissive = type_definition(
            type_name="observed_near", hierarchy_semantics="none",
            source_referent_kinds=("unknown", "physical_instance"),
            target_referent_kinds=("physical_instance",))
        assert "unknown" in permissive.source_referent_kinds
        with pytest.raises(ModelIntegrityError):
            type_definition(source_referent_kinds=())  # min 1
        with pytest.raises(ModelIntegrityError):
            type_definition(source_referent_kinds=("widget",))

    def test_assertion_shape_and_patterns(self):
        record = assertion()
        assert record.record_id.startswith("rel_")
        with pytest.raises(ModelIntegrityError):
            assertion(source_anchor_id="extruder")   # names are not identity
        with pytest.raises(ModelIntegrityError):
            assertion(type_id=REL)                   # must cite an rtd_
        with pytest.raises(ModelIntegrityError):
            assertion(evidence=())                   # evidence-free claims

    def test_context_arms_are_discriminated(self):
        with pytest.raises(ValidationError):
            LifecycleViewContext(kind="lifecycle_view", view="as_imagined")
        with pytest.raises(ValidationError):
            ViewIndependentContext(kind="view_independent", view="as_built")
        assert assertion(context=VIEW_FREE).context.kind == "view_independent"

    def test_withdrawal_targets_assertions_only(self):
        record = build_record(RelationshipWithdrawal, withdraws=REL,
                              recorded_at=T0, authority=AUTHORITY)
        assert record.record_id.startswith("rwd_")
        with pytest.raises(ModelIntegrityError):
            build_record(RelationshipWithdrawal, withdraws=RTD,
                         recorded_at=T0, authority=AUTHORITY)

    def test_authority_is_a_claim_with_fixed_vocabulary(self):
        with pytest.raises(ValidationError):
            AuthorityRef(kind="verified_admin", agent="x",
                         method="manual_declaration")


class TestEvidence:
    def test_evidence_reference_patterns(self):
        with pytest.raises(ValidationError):
            IdentityBindingRecordEvidence(
                kind="identity_binding_record", binding_set_id="demo-printer",
                record_id="xyz_" + "0" * 64)
        with pytest.raises(ValidationError):
            OwnerDeclarationEvidence(kind="owner_declaration", statement="")

    def test_evidence_discriminator_rejects_unknown_kind(self):
        with pytest.raises(ModelIntegrityError):
            assertion(evidence=({"kind": "blog_post", "url": "x"},))


class TestModelRevision:
    def test_valid_revision_constructs_and_forgeries_rejected(self):
        ids = tuple(sorted([registration().record_id, assertion().record_id]))
        revision = ModelRevision(
            revision_id=compute_revision_id("demo-printer", ids),
            record_ids=ids, record_count=2, model_id="demo-printer")
        assert revision.revision_id.startswith("mrv_")
        assert len(revision.revision_id) == 4 + 64
        cases = [
            dict(record_ids=ids[::-1], record_count=2),      # unsorted
            dict(record_ids=(ids[0], ids[0]), record_count=2),  # duplicate
            dict(record_ids=ids, record_count=3),            # wrong count
        ]
        for case in cases:
            with pytest.raises(ValidationError):
                ModelRevision(revision_id=compute_revision_id(
                    "demo-printer", case["record_ids"]),
                    model_id="demo-printer", **case)
        with pytest.raises(ValidationError):  # wrong hash
            ModelRevision(revision_id="mrv_" + "0" * 64, record_ids=ids,
                          record_count=2, model_id="demo-printer")

    def test_membership_pattern_excludes_mrv_and_garbage(self):
        for bad in ("mrv_" + "0" * 64, "not-a-record-id", "anc_" + "0" * 64):
            with pytest.raises(ValidationError):
                ModelRevision(revision_id=compute_revision_id("m", (bad,)),
                              record_ids=(bad,), record_count=1, model_id="m")


def summary(**overrides):
    fields = dict(
        record_id=REL, type_id=RTD, type_name="contains",
        forward_label="contains", inverse_label="is contained in",
        cited_type_current=True, source_anchor_id=ENT_A,
        target_anchor_id=ENT_B, context=AS_BUILT, authority=AUTHORITY,
        evidence=(), supersedes=None, superseded_by=(), withdrawn_by=(),
        active=True, recorded_at=T0)
    fields.update(overrides)
    return RelationshipSummary(**fields)


def revision0():
    return ModelRevision(revision_id=compute_revision_id("m", ()),
                         record_ids=(), record_count=0, model_id="m")


class TestResultInvariants:
    def test_summary_active_iff_no_lifecycle_links(self):
        with pytest.raises(ValidationError):
            summary(active=True, withdrawn_by=("rwd_" + "2" * 64,))
        with pytest.raises(ValidationError):
            summary(active=False)  # inactive requires a cited cause
        with pytest.raises(ValidationError):
            summary(active=False,
                    superseded_by=("rel_" + "3" * 64, "rel_" + "2" * 64))

    def test_lineage_conflict_needs_two_competitors(self):
        with pytest.raises(ValidationError):
            LineageConflict(predecessor_id=REL,
                            competing_successor_ids=("rel_" + "2" * 64,))

    def test_relationships_result_tuple_placement_validated(self):
        with pytest.raises(ValidationError):
            RelationshipsResult(
                status="registered",
                anchor_id=ENT_A, direction="outgoing", type_name=None,
                context=AS_BUILT, active=(),
                inactive=(summary(),),  # an ACTIVE summary in inactive
                lineage_conflicts=(), revision=revision0())

    def test_not_registered_relationships_result_carries_nothing(self):
        """MK repair F3: absence gained a status, so "never registered" must
        not be able to claim edges. Registered-and-empty stays legitimate."""
        def result(**overrides):
            fields = dict(status="registered", anchor_id=ENT_A,
                          direction="outgoing", type_name=None,
                          context=AS_BUILT, active=(), inactive=(),
                          lineage_conflicts=(), revision=revision0())
            fields.update(overrides)
            return RelationshipsResult(**fields)

        assert result(active=(summary(),)).status == "registered"
        assert result(status="not_registered").active == ()  # legitimate
        assert result().status == "registered"  # registered may be empty
        withdrawn = summary(active=False, withdrawn_by=("rwd_" + "2" * 64,))
        conflict = LineageConflict(
            predecessor_id=REL,
            competing_successor_ids=("rel_" + "2" * 64, "rel_" + "3" * 64))
        for populated in (dict(active=(summary(),)),
                          dict(inactive=(withdrawn,)),
                          dict(lineage_conflicts=(conflict,))):
            with pytest.raises(ValidationError):
                result(status="not_registered", **populated)

    def test_parent_result_field_coherence(self):
        with pytest.raises(ValidationError):
            ParentResult(status="no_declared_parent", child_anchor_id=ENT_B,
                         parent=anchor(), supporting=(), candidate_parents=(),
                         cycle_members=(), type_name="contains",
                         view="as_built", revision=revision0())
        with pytest.raises(ValidationError):
            ParentResult(status="resolved", child_anchor_id=ENT_B, parent=None,
                         supporting=(), candidate_parents=(), cycle_members=(),
                         type_name="contains", view="as_built",
                         revision=revision0())

    def test_traversal_partial_iff_blocked(self):
        with pytest.raises(ValidationError):
            TraversalResult(status="partial", origin_anchor_id=ENT_A,
                            steps=(), blocked=(), type_name="contains",
                            view="as_built", revision=revision0())
