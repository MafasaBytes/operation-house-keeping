"""IB-001 resolver: three-valued applicability, the eight-case
non-overlapping algorithm, structured lifecycle explanations, and
independent subject/property resolution."""

from datetime import UTC, datetime

import pytest

from backend.identity_binding.canonical import build_record
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    ApplicabilityClosure,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    BindingResolutionError,
    BindingRetraction,
    DeclaredBoundary,
    UnboundedBoundary,
    UnknownBoundary,
)
from backend.identity_binding.resolver import BindingResolver, membership
from backend.identity_binding.store import BindingStore
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

E1 = "ent_" + "1" * 32
E2 = "ent_" + "2" * 32
V1 = "var_" + "3" * 32
T_START = datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC)
T_IN = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)
T_END = datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)
T_BEFORE = datetime(2026, 8, 7, 19, 0, 0, tzinfo=UTC)
T_AFTER = datetime(2026, 8, 7, 22, 0, 0, tzinfo=UTC)
RECORDED = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)

AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")

_BOUNDARY = {
    "declared_start": DeclaredBoundary(kind="declared", at=T_START),
    "declared_end": DeclaredBoundary(kind="declared", at=T_END),
    "unbounded": UnboundedBoundary(kind="unbounded"),
    "unknown": UnknownBoundary(kind="unknown"),
}


def scope(start="declared", end="declared"):
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=_BOUNDARY["declared_start" if start == "declared" else start],
        end_boundary=_BOUNDARY["declared_end" if end == "declared" else end],
        interval_semantics="half_open")


def entity_decl(anchor_id, role=None):
    return build_record(
        AnchorDeclaration, anchor_kind="entity",
        anchor=EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                            display_name=f"Entity {anchor_id[:6]}",
                            role_name=role, referent_kind="physical_instance"),
        recorded_at=RECORDED, authority=AUTHORITY)


def variable_decl(anchor_id, owner):
    return build_record(
        AnchorDeclaration, anchor_kind="variable",
        anchor=VariableAnchor(anchor_id=anchor_id, entity_anchor_id=owner,
                              namespace="demo-printer",
                              display_name="Hotend temperature"),
        recorded_at=RECORDED, authority=AUTHORITY)


def subject_assertion(target, applies=None, supersedes=None,
                      recorded_at=RECORDED, note=""):
    return build_record(
        BindingAssertion, binding_kind="subject", subject=SUBJECT,
        property=None, target_anchor_id=target, applies=applies or scope(),
        recorded_at=recorded_at, authority=AUTHORITY, supersedes=supersedes,
        note=note)


def property_assertion(target=V1, applies=None, prop=PROP):
    return build_record(
        BindingAssertion, binding_kind="property", subject=SUBJECT,
        property=prop, target_anchor_id=target, applies=applies or scope(),
        recorded_at=RECORDED, authority=AUTHORITY)


def resolver_with(tmp_path, *records):
    store = BindingStore(tmp_path / "demo-printer")
    for record in records:
        store.append(record)
    return BindingResolver(store.load())


class TestMembership:
    @pytest.mark.parametrize("start,end,at,expected", [
        # declared start, declared end — half-open [start, end)
        ("declared", "declared", T_START, "in"),
        ("declared", "declared", T_IN, "in"),
        ("declared", "declared", T_END, "out"),      # boundary → successor
        ("declared", "declared", T_BEFORE, "out"),
        # declared start, unbounded / unknown end
        ("declared", "unbounded", T_AFTER, "in"),
        ("declared", "unbounded", T_BEFORE, "out"),
        ("declared", "unknown", T_BEFORE, "out"),    # declared side excludes
        ("declared", "unknown", T_IN, "unknown"),
        # unbounded start
        ("unbounded", "declared", T_BEFORE, "in"),
        ("unbounded", "declared", T_END, "out"),
        ("unbounded", "unbounded", T_AFTER, "in"),
        ("unbounded", "unknown", T_IN, "unknown"),
        # unknown start
        ("unknown", "declared", T_AFTER, "out"),     # declared side excludes
        ("unknown", "declared", T_IN, "unknown"),
        ("unknown", "unbounded", T_IN, "unknown"),
        ("unknown", "unknown", T_IN, "unknown"),
    ])
    def test_all_nine_boundary_combinations(self, start, end, at, expected):
        assert membership(scope(start, end), at) == expected


class TestResolutionAlgorithm:
    def test_unbound_when_no_assertion_matches(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_decl(E1))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "unbound"
        assert result.resolved_target is None
        assert result.via_assertions == ()

    def test_bound_within_declared_interval(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 subject_assertion(E1))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "bound"
        assert result.resolved_target.anchor_id == E1
        assert result.applicability_basis == "declared_interval"
        assert result.candidate_targets == ()
        assert result.revision.record_count == 2

    def test_outside_applicability_after_declared_end(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 subject_assertion(E1))
        for at in (T_END, T_AFTER, T_BEFORE):
            result = resolver.resolve_subject(SUBJECT, at=at)
            assert result.status == "outside_applicability"
            assert result.via_assertions[0].membership_at == "out"

    def test_different_target_out_never_blocks_bound(self, tmp_path):
        """Mandatory regression: a different-target OUT assertion never
        blocks a valid binding — replacement resolves per interval."""
        later = AppliesScope(
            axis="ingestion_received_at",
            start_boundary=DeclaredBoundary(kind="declared", at=T_END),
            end_boundary=DeclaredBoundary(kind="declared", at=T_AFTER),
            interval_semantics="half_open")
        resolver = resolver_with(
            tmp_path, entity_decl(E1, role="extruder-unit"),
            entity_decl(E2, role="extruder-unit"),  # same ROLE, new identity
            subject_assertion(E1), subject_assertion(E2, applies=later))
        in_first = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert in_first.status == "bound"
        assert in_first.resolved_target.anchor_id == E1
        memberships = {s.record_id: s.membership_at
                       for s in in_first.via_assertions}
        assert sorted(memberships.values()) == ["in", "out"]
        in_second = resolver.resolve_subject(SUBJECT, at=T_END)  # boundary
        assert in_second.status == "bound"
        assert in_second.resolved_target.anchor_id == E2

    def test_different_target_unknown_prevents_bound(self, tmp_path):
        """Mandatory regression: a differing-target UNKNOWN assertion
        prevents `bound` — the competitor cannot be ruled out."""
        resolver = resolver_with(
            tmp_path, entity_decl(E1), entity_decl(E2),
            subject_assertion(E1),
            subject_assertion(E2, applies=scope("unknown", "unknown")))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "ambiguous"
        assert result.resolved_target is None
        assert {a.anchor_id for a in result.candidate_targets} == {E1, E2}

    def test_same_target_unknown_corroborates_bound(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1), subject_assertion(E1),
            subject_assertion(E1, applies=scope("unknown", "unknown"),
                              note="corroborating"))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "bound"
        assert len(result.via_assertions) == 2  # no vote counting, all cited

    def test_conflicted_when_two_targets_positively_in(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1), entity_decl(E2),
            subject_assertion(E1), subject_assertion(E2, note="competing"))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "conflicted"
        assert result.resolved_target is None
        assert [a.anchor_id for a in result.candidate_targets] == sorted([E1, E2])

    def test_applicability_unknown_candidate_never_resolved(self, tmp_path):
        """Mandatory regression: an unknown-only candidate never occupies
        resolved_target."""
        resolver = resolver_with(
            tmp_path, entity_decl(E1),
            subject_assertion(E1, applies=scope("unknown", "unknown")))
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "applicability_unknown"
        assert result.resolved_target is None
        assert [a.anchor_id for a in result.candidate_targets] == [E1]

    def test_two_unknown_targets_are_ambiguous(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1), entity_decl(E2),
            subject_assertion(E1, applies=scope("unknown", "unknown")),
            subject_assertion(E2, applies=scope("unknown", "unknown")))
        assert resolver.resolve_subject(SUBJECT, at=T_IN).status == "ambiguous"

    def test_unbounded_claim_binds_with_disclosed_basis(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1),
            subject_assertion(E1, applies=scope("unbounded", "unbounded")))
        result = resolver.resolve_subject(SUBJECT, at=T_AFTER)
        assert result.status == "bound"
        assert result.applicability_basis == "includes_unbounded_claim"

    def test_competing_successors_never_resolved_by_recency(self, tmp_path):
        original = subject_assertion(E1, note="original")
        earlier = subject_assertion(E1, supersedes=original.record_id,
                                    recorded_at=RECORDED, note="fix-a")
        later = subject_assertion(
            E2, supersedes=original.record_id,
            recorded_at=datetime(2026, 8, 8, 1, 0, 0, tzinfo=UTC), note="fix-b")
        resolver = resolver_with(tmp_path, entity_decl(E1), entity_decl(E2),
                                 original, earlier, later)
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "conflicted"  # matrix, never the timestamp

    def test_naive_at_rejected(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 subject_assertion(E1))
        with pytest.raises(BindingResolutionError) as excinfo:
            resolver.resolve_subject(SUBJECT, at=datetime(2026, 8, 7, 20, 30))
        assert excinfo.value.error_code == "BINDING_NAIVE_AT"


class TestLifecycleStatuses:
    def test_retracted_only(self, tmp_path):
        assertion = subject_assertion(E1)
        retraction = build_record(BindingRetraction,
                                  retracts=assertion.record_id,
                                  recorded_at=RECORDED, authority=AUTHORITY)
        resolver = resolver_with(tmp_path, entity_decl(E1), assertion,
                                 retraction)
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "retracted"
        summary = result.via_assertions[0]
        assert summary.retracted_by == (retraction.record_id,)
        assert summary.active is False

    def test_mixture_is_inactive(self, tmp_path):
        original = subject_assertion(E1, note="original")
        successor = subject_assertion(E2, supersedes=original.record_id)
        retraction = build_record(BindingRetraction,
                                  retracts=successor.record_id,
                                  recorded_at=RECORDED, authority=AUTHORITY)
        resolver = resolver_with(tmp_path, entity_decl(E1), entity_decl(E2),
                                 original, successor, retraction)
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "inactive"  # superseded + retracted mixture

    def test_simultaneous_supersession_and_retraction_loses_neither(
        self, tmp_path
    ):
        """Mandatory regression: both lifecycle facts are disclosed."""
        original = subject_assertion(E1, note="original")
        successor = subject_assertion(E2, supersedes=original.record_id)
        retract_original = build_record(BindingRetraction,
                                        retracts=original.record_id,
                                        recorded_at=RECORDED,
                                        authority=AUTHORITY)
        retract_successor = build_record(BindingRetraction,
                                         retracts=successor.record_id,
                                         recorded_at=RECORDED,
                                         authority=AUTHORITY, note="b")
        resolver = resolver_with(tmp_path, entity_decl(E1), entity_decl(E2),
                                 original, successor, retract_original,
                                 retract_successor)
        result = resolver.resolve_subject(SUBJECT, at=T_IN)
        assert result.status == "inactive"
        by_id = {s.record_id: s for s in result.via_assertions}
        both = by_id[original.record_id]
        assert both.superseded_by == (successor.record_id,)
        assert both.retracted_by == (retract_original.record_id,)

    def test_summary_cites_exact_closure_record(self, tmp_path):
        """Mandatory regression: lifecycle summaries cite the exact
        closure record whose end was used for this resolution."""
        open_ended = subject_assertion(E1, applies=scope(end="unknown"))
        closure = build_record(ApplicabilityClosure,
                               closes=open_ended.record_id, end=T_END,
                               recorded_at=RECORDED, authority=AUTHORITY)
        resolver = resolver_with(tmp_path, entity_decl(E1), open_ended,
                                 closure)
        result = resolver.resolve_subject(SUBJECT, at=T_AFTER)
        assert result.status == "outside_applicability"
        summary = result.via_assertions[0]
        assert summary.declared_applies.end_boundary.kind == "unknown"
        assert summary.effective_applies.end_boundary.at == T_END
        assert summary.closure_records == (closure.record_id,)
        # before the closed end the assertion still binds
        assert resolver.resolve_subject(SUBJECT, at=T_IN).status == "bound"


class TestPropertyIndependence:
    def test_property_binds_while_subject_unbound(self, tmp_path):
        """Mandatory regressions: a property may bind while its subject
        remains unbound, and property binding never creates a general
        subject binding."""
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 variable_decl(V1, owner=E1),
                                 property_assertion(V1))
        result = resolver.resolve_property(SUBJECT, PROP, at=T_IN)
        assert result.status == "bound"
        assert result.resolved_target.anchor_id == V1
        assert result.subject_context.status == "unbound"
        assert resolver.resolve_subject(SUBJECT, at=T_IN).status == "unbound"

    def test_inconsistent_ownership_is_conflicted(self, tmp_path):
        """Mandatory regression: positively inconsistent subject/entity
        ownership produces conflicted."""
        resolver = resolver_with(
            tmp_path, entity_decl(E1), entity_decl(E2),
            variable_decl(V1, owner=E1),
            subject_assertion(E2),          # subject bound to E2 ...
            property_assertion(V1))         # ... but V1 belongs to E1
        result = resolver.resolve_property(SUBJECT, PROP, at=T_IN)
        assert result.status == "conflicted"
        assert result.resolved_target is None
        assert [a.anchor_id for a in result.candidate_targets] == [V1]
        assert result.subject_context.status == "bound"
        assert result.subject_context.resolved_entity.anchor_id == E2

    def test_consistent_ownership_binds(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1), variable_decl(V1, owner=E1),
            subject_assertion(E1), property_assertion(V1))
        result = resolver.resolve_property(SUBJECT, PROP, at=T_IN)
        assert result.status == "bound"
        assert result.subject_context.resolved_entity.anchor_id == E1

    def test_unknown_subject_visible_but_not_contradictory(self, tmp_path):
        resolver = resolver_with(
            tmp_path, entity_decl(E1), variable_decl(V1, owner=E1),
            subject_assertion(E1, applies=scope("unknown", "unknown")),
            property_assertion(V1))
        result = resolver.resolve_property(SUBJECT, PROP, at=T_IN)
        assert result.status == "bound"  # unknown subject proves nothing
        assert result.subject_context.status == "applicability_unknown"
        assert [a.anchor_id
                for a in result.subject_context.candidate_entities] == [E1]

    def test_context_is_non_recursive(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 variable_decl(V1, owner=E1),
                                 property_assertion(V1))
        context = resolver.resolve_property(SUBJECT, PROP, at=T_IN).subject_context
        assert all(isinstance(i, str) for i in context.via_assertion_ids)
        assert not hasattr(context, "subject_context")
        assert not hasattr(context, "via_assertions")

    def test_exact_six_dimension_locator_required(self, tmp_path):
        other_pointer = SourcePropertyRef(
            extraction_route="api:moonraker:v1", item_key="printer_objects",
            json_pointer="/result/status/extruder/target")
        resolver = resolver_with(tmp_path, entity_decl(E1),
                                 variable_decl(V1, owner=E1),
                                 property_assertion(V1))
        assert resolver.resolve_property(
            SUBJECT, other_pointer, at=T_IN).status == "unbound"
