"""VM-001: read-only reverse binding discovery — every property locator
EVER declared for a variable anchor in one binding revision. Deliberately
time-free (revision-relative lifecycle flags, never a time-specific
"active" claim): applicability at an observation is decided solely by
forward resolution at that occurrence's own received_at."""

import inspect
from datetime import UTC, datetime

import pytest

from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    ApplicabilityClosure,
    AuthorityRef,
    BindingAssertion,
    BindingResolutionError,
    BindingRetraction,
    DeclaredBoundary,
    DeclaredBindingSummary,
    DeclaredLocatorEntry,
    DeclaredPropertyLocatorsResult,
    IdentityBindingError,
    UnboundedBoundary,
)
from backend.identity_binding.canonical import build_record
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

E1 = "ent_" + "1" * 32
V1 = "var_" + "3" * 32
V2 = "var_" + "4" * 32
V3 = "var_" + "5" * 32
RECORDED = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP_TEMP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                              item_key="printer_objects",
                              json_pointer="/result/status/extruder/temperature")
PROP_TARGET = SourcePropertyRef(extraction_route="api:moonraker:v1",
                                item_key="printer_objects",
                                json_pointer="/result/status/extruder/target")


def interval(start_h, end_h):
    day = datetime(2026, 8, 7, tzinfo=UTC)
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=DeclaredBoundary(
            kind="declared", at=day.replace(hour=start_h)),
        end_boundary=DeclaredBoundary(
            kind="declared", at=day.replace(hour=end_h)),
        interval_semantics="half_open")


UNBOUNDED = AppliesScope(
    axis="ingestion_received_at",
    start_boundary=DeclaredBoundary(kind="declared",
                                    at=datetime(2026, 8, 7, 20, tzinfo=UTC)),
    end_boundary=UnboundedBoundary(kind="unbounded"),
    interval_semantics="half_open")


def declaration(variable=V1, owner=E1):
    return build_record(
        AnchorDeclaration, anchor_kind="variable",
        anchor=VariableAnchor(anchor_id=variable, entity_anchor_id=owner,
                              namespace="demo-printer",
                              display_name="Demo variable"),
        recorded_at=RECORDED, authority=AUTHORITY)


def entity_declaration(entity=E1):
    return build_record(
        AnchorDeclaration, anchor_kind="entity",
        anchor=EntityAnchor(anchor_id=entity, namespace="demo-printer",
                            display_name="Demo entity",
                            referent_kind="physical_instance"),
        recorded_at=RECORDED, authority=AUTHORITY)


def prop_assertion(target=V1, prop=PROP_TEMP, applies=None, supersedes=None,
                   recorded_at=RECORDED, note=""):
    return build_record(
        BindingAssertion, binding_kind="property", subject=SUBJECT,
        property=prop, target_anchor_id=target,
        applies=applies or interval(20, 21), recorded_at=recorded_at,
        authority=AUTHORITY, supersedes=supersedes, note=note)


def resolver_with(tmp_path, *records):
    store = BindingStore(tmp_path / "demo-printer")
    for record in records:
        store.append(record)
    return BindingResolver(store.load())


class TestReverseDiscovery:
    def test_single_declared_locator(self, tmp_path):
        asserted = prop_assertion()
        resolver = resolver_with(tmp_path, entity_declaration(),
                                 declaration(), asserted)
        result = resolver.declared_property_locators(V1)
        assert result.status == "declared"
        assert result.target_anchor_id == V1
        assert len(result.locators) == 1
        entry = result.locators[0]
        assert (entry.subject, entry.property) == (SUBJECT, PROP_TEMP)
        summary = entry.assertion_summaries[0]
        assert summary.record_id == asserted.record_id
        assert summary.target_anchor_id == V1
        assert summary.lifecycle_flags == ()
        assert summary.declared_applies == summary.effective_applies
        assert summary.supersedes is None
        assert result.revision == resolver.loaded.revision

    def test_none_declared(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_declaration(), declaration())
        result = resolver.declared_property_locators(V1)
        assert result.status == "none_declared"
        assert result.locators == ()

    def test_anchor_not_declared(self, tmp_path):
        resolver = resolver_with(tmp_path, entity_declaration(), declaration())
        result = resolver.declared_property_locators(V2)
        assert result.status == "anchor_not_declared"
        assert result.locators == ()

    def test_lifecycle_history_fully_auditable(self, tmp_path):
        """Superseded, retracted, and closed declarations all stay listed
        with time-free flags and the exact lifecycle record ids — a
        historical declaration never looks like an unexplained live one."""
        original = prop_assertion(note="original")
        corrected = prop_assertion(note="corrected",
                                   supersedes=original.record_id)
        retracted_one = prop_assertion(prop=PROP_TARGET, note="mistake")
        retraction = build_record(
            BindingRetraction, retracts=retracted_one.record_id,
            recorded_at=RECORDED, authority=AUTHORITY)
        open_ended = prop_assertion(
            prop=SourcePropertyRef(extraction_route="api:moonraker:v1",
                                   item_key="printer_objects",
                                   json_pointer="/result/status/extruder/power"),
            applies=UNBOUNDED)
        closure = build_record(
            ApplicabilityClosure, closes=open_ended.record_id,
            end=datetime(2026, 8, 7, 22, tzinfo=UTC),
            recorded_at=RECORDED, authority=AUTHORITY)
        resolver = resolver_with(
            tmp_path, entity_declaration(), declaration(), original,
            corrected, retracted_one, retraction, open_ended, closure)

        result = resolver.declared_property_locators(V1)
        assert result.status == "declared"
        by_id = {s.record_id: s
                 for entry in result.locators
                 for s in entry.assertion_summaries}
        assert by_id[original.record_id].lifecycle_flags == ("superseded",)
        assert by_id[original.record_id].superseded_by == (
            corrected.record_id,)
        assert by_id[corrected.record_id].lifecycle_flags == ()
        assert by_id[corrected.record_id].supersedes == original.record_id
        assert by_id[retracted_one.record_id].lifecycle_flags == (
            "retracted",)
        assert by_id[retracted_one.record_id].retracted_by == (
            retraction.record_id,)
        closed = by_id[open_ended.record_id]
        assert closed.lifecycle_flags == ("closed",)
        assert closed.closure_records == (closure.record_id,)
        assert closed.declared_applies.end_boundary.kind == "unbounded"
        assert closed.effective_applies.end_boundary.kind == "declared"

    def test_multiple_locators_deterministically_sorted(self, tmp_path):
        second = prop_assertion(prop=PROP_TARGET)
        first = prop_assertion(prop=PROP_TEMP)
        resolver = resolver_with(tmp_path, entity_declaration(),
                                 declaration(), second, first)
        result = resolver.declared_property_locators(V1)
        pointers = [entry.property.json_pointer for entry in result.locators]
        assert pointers == sorted(pointers)
        again = resolver.declared_property_locators(V1)
        assert again == result

    def test_shared_locator_discloses_all_targets(self, tmp_path):
        """One locator asserted for V1 AND V2: discovery for V1 carries
        BOTH summaries so the conflict is explicable standalone."""
        mine = prop_assertion(target=V1)
        other = prop_assertion(target=V2)
        resolver = resolver_with(tmp_path, entity_declaration(),
                                 declaration(V1), declaration(V2), mine,
                                 other)
        result = resolver.declared_property_locators(V1)
        assert len(result.locators) == 1
        targets = {s.target_anchor_id
                   for s in result.locators[0].assertion_summaries}
        assert targets == {V1, V2}
        # and V3, never targeted by this locator, does not inherit it
        resolver_with(tmp_path / "other", entity_declaration(),
                      declaration(V3))

    def test_result_is_time_free(self, tmp_path):
        assert "at" not in inspect.signature(
            BindingResolver.declared_property_locators).parameters
        fields = DeclaredBindingSummary.model_fields
        assert "membership_at" not in fields
        assert "active" not in fields  # amendment 2: no time-ambiguous flag

    @pytest.mark.parametrize("bad", [
        pytest.param(E1, id="entity_id"), pytest.param(None, id="none"),
        pytest.param("", id="empty"), pytest.param(3, id="int"),
        pytest.param([], id="unhashable"),
        pytest.param("var_" + "z" * 32, id="nonhex"),
    ])
    def test_invalid_input_typed(self, tmp_path, bad):
        resolver = resolver_with(tmp_path, entity_declaration(), declaration())
        with pytest.raises(IdentityBindingError) as excinfo:
            resolver.declared_property_locators(bad)
        assert isinstance(excinfo.value, BindingResolutionError)
        assert excinfo.value.error_code == "BINDING_ANCHOR_ID_INVALID"
        assert str(tmp_path) not in str(excinfo.value)

    def test_never_a_winner(self, tmp_path):
        """No resolved/winner/basis field exists, and permuting recorded_at
        across competing assertions changes nothing."""
        for field in ("resolved", "winner", "resolved_target",
                      "applicability_basis"):
            assert field not in DeclaredPropertyLocatorsResult.model_fields
            assert field not in DeclaredLocatorEntry.model_fields
        early = prop_assertion(target=V1, recorded_at=RECORDED)
        late = prop_assertion(
            target=V2, recorded_at=RECORDED.replace(hour=1), note="later")
        resolver = resolver_with(tmp_path, entity_declaration(),
                                 declaration(V1), declaration(V2), early,
                                 late)
        result = resolver.declared_property_locators(V1)
        targets = [s.target_anchor_id
                   for s in result.locators[0].assertion_summaries]
        assert sorted(targets) == [V1, V2]

    def test_snapshot_consistency(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        for record in (entity_declaration(), declaration(), prop_assertion()):
            store.append(record)
        resolver = BindingResolver(store.load())
        before = resolver.declared_property_locators(V1)
        store.append(prop_assertion(prop=PROP_TARGET))
        after = resolver.declared_property_locators(V1)
        assert after == before
        assert after.revision == resolver.loaded.revision

    def test_demo_binding_set_discovery(self):
        from pathlib import Path

        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        result = resolver.declared_property_locators(
            "var_b7e2d3c4f5a6172839405a6b7c8d9e0f")
        assert result.status == "declared"
        assert len(result.locators) == 1
        entry = result.locators[0]
        assert entry.property.json_pointer == (
            "/result/status/extruder/temperature")
        assert entry.assertion_summaries[0].lifecycle_flags == ()
