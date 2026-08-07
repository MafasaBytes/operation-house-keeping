"""IB-001 repair slice: typed missing-time rejection at the resolver
boundary and result-contract invariants that reject impossible states."""

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.identity_binding.canonical import build_record, compute_revision_id
from backend.identity_binding.contracts import (
    AppliesScope,
    AssertionSummary,
    AuthorityRef,
    BindingRejection,
    BindingResolutionError,
    BindingRevision,
    DeclaredBoundary,
    ResolutionResult,
    SubjectResolutionContext,
)
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef
from backend.system_identity import EntityAnchor, VariableAnchor

DEMO_SET = Path("bindings/demo-printer")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")
IN_HOUR_UTC = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")

ENTITY = EntityAnchor(anchor_id="ent_" + "a" * 32, namespace="demo-printer",
                      display_name="Entity", referent_kind="physical_instance")
ENTITY_B = EntityAnchor(anchor_id="ent_" + "b" * 32, namespace="demo-printer",
                        display_name="Entity B",
                        referent_kind="physical_instance")
VARIABLE = VariableAnchor(anchor_id="var_" + "c" * 32,
                          entity_anchor_id=ENTITY.anchor_id,
                          namespace="demo-printer", display_name="Variable")
REVISION = BindingRevision(revision_id=compute_revision_id("s", ()),
                           record_ids=(), record_count=0, binding_set_id="s")
CONTEXT = SubjectResolutionContext(status="unbound")


def result(**overrides):
    fields = dict(status="unbound", locator_subject=SUBJECT,
                  locator_property=None, resolved_target=None,
                  candidate_targets=(), via_assertions=(),
                  applicability_basis=None, revision=REVISION,
                  subject_context=None)
    fields.update(overrides)
    return ResolutionResult(**fields)


class TestResolutionTimeBoundary:
    @pytest.fixture()
    def resolver(self):
        return BindingResolver(BindingStore(DEMO_SET).load())

    def test_omitted_at_raises_typed_error(self, resolver):
        for call in (lambda: resolver.resolve_subject(SUBJECT),
                     lambda: resolver.resolve_property(SUBJECT, PROP)):
            with pytest.raises(BindingResolutionError) as excinfo:
                call()
            assert excinfo.value.error_code == "BINDING_NAIVE_AT"

    def test_explicit_none_raises_typed_error(self, resolver):
        for call in (lambda: resolver.resolve_subject(SUBJECT, at=None),
                     lambda: resolver.resolve_property(SUBJECT, PROP, at=None)):
            with pytest.raises(BindingResolutionError) as excinfo:
                call()
            assert excinfo.value.error_code == "BINDING_NAIVE_AT"

    def test_naive_at_raises_typed_error(self, resolver):
        naive = datetime(2026, 8, 7, 20, 30, 0)
        for call in (lambda: resolver.resolve_subject(SUBJECT, at=naive),
                     lambda: resolver.resolve_property(SUBJECT, PROP, at=naive)):
            with pytest.raises(BindingResolutionError) as excinfo:
                call()
            assert excinfo.value.error_code == "BINDING_NAIVE_AT"

    def test_aware_non_utc_at_normalizes(self, resolver):
        plus2 = timezone(timedelta(hours=2))
        offset_at = datetime(2026, 8, 7, 22, 30, 0, tzinfo=plus2)  # == 20:30Z
        assert (resolver.resolve_subject(SUBJECT, at=offset_at)
                == resolver.resolve_subject(SUBJECT, at=IN_HOUR_UTC))
        assert (resolver.resolve_property(SUBJECT, PROP, at=offset_at)
                == resolver.resolve_property(SUBJECT, PROP, at=IN_HOUR_UTC))


class TestResolutionResultInvariants:
    def test_bound_requires_basis_and_no_candidates(self):
        with pytest.raises(ValidationError):
            result(status="bound", resolved_target=ENTITY,
                   applicability_basis=None)
        with pytest.raises(ValidationError):
            result(status="bound", resolved_target=ENTITY,
                   applicability_basis="declared_interval",
                   candidate_targets=(ENTITY_B,))

    def test_statuses_that_cannot_carry_candidates_reject_them(self):
        for status in ("unbound", "outside_applicability", "superseded",
                       "retracted", "inactive"):
            with pytest.raises(ValidationError):
                result(status=status, candidate_targets=(ENTITY,))

    def test_subject_context_exists_exactly_for_property_resolution(self):
        with pytest.raises(ValidationError):
            result(subject_context=CONTEXT)  # subject resolution
        with pytest.raises(ValidationError):
            result(locator_property=PROP, subject_context=None)
        assert result(locator_property=PROP,
                      subject_context=CONTEXT).subject_context is CONTEXT

    def test_subject_results_carry_entity_anchors_only(self):
        with pytest.raises(ValidationError):
            result(status="bound", resolved_target=VARIABLE,
                   applicability_basis="declared_interval")
        with pytest.raises(ValidationError):
            result(status="ambiguous", candidate_targets=(VARIABLE,))

    def test_property_results_carry_variable_anchors_only(self):
        with pytest.raises(ValidationError):
            result(status="bound", locator_property=PROP,
                   subject_context=CONTEXT, resolved_target=ENTITY,
                   applicability_basis="declared_interval")

    def test_candidates_unique_and_canonically_ordered(self):
        with pytest.raises(ValidationError):
            result(status="conflicted", candidate_targets=(ENTITY_B, ENTITY))
        with pytest.raises(ValidationError):
            result(status="conflicted", candidate_targets=(ENTITY, ENTITY))
        ordered = result(status="conflicted",
                         candidate_targets=(ENTITY, ENTITY_B))
        assert len(ordered.candidate_targets) == 2


class TestSubjectContextInvariants:
    def test_resolved_entity_exactly_when_bound(self):
        with pytest.raises(ValidationError):
            SubjectResolutionContext(status="bound", resolved_entity=None)
        with pytest.raises(ValidationError):
            SubjectResolutionContext(status="unbound", resolved_entity=ENTITY)

    def test_bound_context_has_no_candidates(self):
        with pytest.raises(ValidationError):
            SubjectResolutionContext(status="bound", resolved_entity=ENTITY,
                                     candidate_entities=(ENTITY_B,))

    def test_collections_unique_and_ordered(self):
        with pytest.raises(ValidationError):
            SubjectResolutionContext(status="ambiguous",
                                     candidate_entities=(ENTITY_B, ENTITY))
        with pytest.raises(ValidationError):
            SubjectResolutionContext(
                status="unbound",
                via_assertion_ids=("iba_" + "b" * 64, "iba_" + "a" * 64))


class TestAssertionSummaryInvariants:
    def _summary(self, **overrides):
        scope = AppliesScope(
            axis="ingestion_received_at",
            start_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 7, 20, 0, tzinfo=UTC)),
            end_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 7, 21, 0, tzinfo=UTC)),
            interval_semantics="half_open")
        fields = dict(record_id="iba_" + "a" * 64,
                      target_anchor_id=ENTITY.anchor_id, authority=AUTHORITY,
                      declared_applies=scope, effective_applies=scope,
                      closure_records=(), superseded_by=(), retracted_by=(),
                      active=True, membership_at="in",
                      recorded_at=datetime(2026, 8, 7, 23, 0, tzinfo=UTC))
        fields.update(overrides)
        return AssertionSummary(**fields)

    def test_active_equivalent_to_no_lifecycle_links(self):
        with pytest.raises(ValidationError):
            self._summary(active=True, superseded_by=("iba_" + "b" * 64,))
        with pytest.raises(ValidationError):
            self._summary(active=False)  # inactive requires a cited cause

    def test_at_most_one_closure_record(self):
        with pytest.raises(ValidationError):
            self._summary(closure_records=("ibc_" + "a" * 64,
                                           "ibc_" + "b" * 64))

    def test_lifecycle_ids_valid_unique_and_ordered(self):
        with pytest.raises(ValidationError):
            self._summary(active=False, retracted_by=("not-a-retraction",))
        with pytest.raises(ValidationError):
            self._summary(active=False,
                          superseded_by=("iba_" + "b" * 64, "iba_" + "a" * 64))


class TestRejectionCoherence:
    def _rejection(self, prop, target):
        return build_record(
            BindingRejection, subject=SUBJECT, property=prop,
            rejected_anchor_id=target,
            recorded_at=datetime(2026, 8, 7, 23, 0, tzinfo=UTC),
            authority=AUTHORITY)

    def test_subject_level_rejection_targets_entity(self):
        with pytest.raises(ValidationError):
            self._rejection(None, VARIABLE.anchor_id)
        assert self._rejection(None, ENTITY.anchor_id).record_id

    def test_property_level_rejection_targets_variable(self):
        with pytest.raises(ValidationError):
            self._rejection(PROP, ENTITY.anchor_id)
        assert self._rejection(PROP, VARIABLE.anchor_id).record_id
