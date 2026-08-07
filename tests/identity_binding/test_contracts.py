"""IB-001 ledger contracts and canonical hashing: schema-versioned
records, UTC-normalized deterministic serialization, full-SHA-256
content-derived record ids."""

import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from backend.identity_binding.canonical import (
    canonical_bytes,
    build_record,
    compute_record_id,
    compute_revision_id,
    verify_record_id,
)
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    BindingRejection,
    BindingRetraction,
    ApplicabilityClosure,
    BindingRevision,
    DeclaredBoundary,
    ResolutionResult,
    UnboundedBoundary,
    UnknownBoundary,
)
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

ENT = "ent_" + "a" * 32
VAR = "var_" + "b" * 32
T0 = datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC)
T1 = datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)

AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")


def declared_scope(start=T0, end=T1):
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=DeclaredBoundary(kind="declared", at=start),
        end_boundary=DeclaredBoundary(kind="declared", at=end),
        interval_semantics="half_open",
    )


def entity_anchor():
    return EntityAnchor(anchor_id=ENT, namespace="demo-printer",
                        display_name="Extruder unit", role_name="extruder-unit",
                        referent_kind="physical_instance")


def declaration(**overrides):
    fields = dict(anchor_kind="entity", anchor=entity_anchor(),
                  recorded_at=T1, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(AnchorDeclaration, **fields)


def assertion(**overrides):
    fields = dict(binding_kind="subject", subject=SUBJECT, property=None,
                  target_anchor_id=ENT, applies=declared_scope(),
                  recorded_at=T1, authority=AUTHORITY, supersedes=None, note="")
    fields.update(overrides)
    return build_record(BindingAssertion, **fields)


class TestBoundariesAndScope:
    def test_declared_boundary_requires_aware_datetime(self):
        with pytest.raises(ValidationError):
            DeclaredBoundary(kind="declared", at=datetime(2026, 8, 7, 20, 0, 0))

    def test_non_utc_aware_datetime_normalized_to_utc(self):
        plus2 = timezone(timedelta(hours=2))
        boundary = DeclaredBoundary(
            kind="declared", at=datetime(2026, 8, 7, 22, 0, 0, tzinfo=plus2))
        assert boundary.at == T0
        assert boundary.at.utcoffset() == timedelta(0)

    def test_unknown_is_not_unbounded(self):
        assert UnknownBoundary(kind="unknown") != UnboundedBoundary(kind="unbounded")

    def test_declared_interval_must_be_ordered(self):
        with pytest.raises(ValidationError):
            declared_scope(start=T1, end=T0)
        with pytest.raises(ValidationError):
            declared_scope(start=T0, end=T0)

    def test_axis_and_semantics_are_fixed(self):
        with pytest.raises(ValidationError):
            AppliesScope(axis="wall_clock",
                         start_boundary=UnknownBoundary(kind="unknown"),
                         end_boundary=UnknownBoundary(kind="unknown"),
                         interval_semantics="half_open")


class TestRecordShapes:
    def test_declaration_anchor_kind_must_match_payload(self):
        with pytest.raises(ValidationError):
            declaration(anchor_kind="variable")  # entity payload

    def test_subject_assertion_forbids_property(self):
        with pytest.raises(ValidationError):
            assertion(binding_kind="subject", property=PROP)

    def test_property_assertion_requires_property(self):
        with pytest.raises(ValidationError):
            assertion(binding_kind="property", property=None)

    def test_target_prefix_must_match_binding_kind(self):
        with pytest.raises(ValidationError):
            assertion(target_anchor_id=VAR)  # subject binding → ent_ only
        with pytest.raises(ValidationError):
            assertion(binding_kind="property", property=PROP,
                      target_anchor_id=ENT)

    def test_property_assertion_constructs(self):
        record = assertion(binding_kind="property", property=PROP,
                           target_anchor_id=VAR)
        assert record.record_id.startswith("iba_")

    def test_recorded_at_rejects_naive(self):
        with pytest.raises(ValidationError):
            assertion(recorded_at=datetime(2026, 8, 7, 21, 0, 0))

    def test_authority_is_a_claim_with_fixed_vocabulary(self):
        with pytest.raises(ValidationError):
            AuthorityRef(kind="verified_admin", agent="x",
                         method="manual_declaration")

    def test_retraction_closure_rejection_construct(self):
        iba = assertion()
        ibr = build_record(BindingRetraction, retracts=iba.record_id,
                           recorded_at=T1, authority=AUTHORITY, note="")
        ibc = build_record(ApplicabilityClosure, closes=iba.record_id, end=T1,
                           recorded_at=T1, authority=AUTHORITY, note="")
        ibj = build_record(BindingRejection, subject=SUBJECT, property=None,
                           rejected_anchor_id=ENT, recorded_at=T1,
                           authority=AUTHORITY, note="")
        assert ibr.record_id.startswith("ibr_")
        assert ibc.record_id.startswith("ibc_")
        assert ibj.record_id.startswith("ibj_")


class TestCanonicalHashing:
    def test_record_id_is_prefixed_full_sha256(self):
        record = declaration()
        prefix, digest = record.record_id.split("_", 1)
        assert prefix == "anc"
        assert len(digest) == 64
        assert set(digest) <= set("0123456789abcdef")
        assert verify_record_id(record)

    def test_record_id_excluded_from_its_own_hash(self):
        record = declaration()
        assert compute_record_id(record) == record.record_id

    def test_content_changes_change_the_id(self):
        assert declaration(note="a").record_id != declaration(note="b").record_id

    def test_equal_instants_with_different_offsets_hash_identically(self):
        """Mandatory regression: semantically equal timestamps expressed
        with different offsets produce the same record id."""
        plus2 = timezone(timedelta(hours=2))
        as_utc = assertion(recorded_at=datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC))
        as_plus2 = assertion(recorded_at=datetime(2026, 8, 7, 23, 0, 0, tzinfo=plus2))
        assert as_utc.record_id == as_plus2.record_id

    def test_canonical_bytes_are_sorted_compact_utc(self):
        payload = canonical_bytes(declaration()).decode()
        parsed = json.loads(payload)
        assert "record_id" not in parsed
        assert ": " not in payload and ", " not in payload
        assert list(parsed) == sorted(parsed)
        assert "+00:00" in payload and "Z\"" not in payload

    def test_schema_version_is_part_of_identity(self):
        record = declaration()
        tampered = record.model_copy(update={"schema_version": "2"})
        assert compute_record_id(tampered) != record.record_id


class TestBindingRevision:
    def test_valid_revision_constructs(self):
        ids = tuple(sorted([declaration().record_id, assertion().record_id]))
        revision = BindingRevision(
            revision_id=compute_revision_id("demo-printer", ids),
            record_ids=ids, record_count=2, binding_set_id="demo-printer")
        assert revision.revision_id.startswith("rev_")
        assert len(revision.revision_id) == 4 + 64

    def test_membership_must_be_sorted_and_unique(self):
        a, b = sorted([declaration().record_id, assertion().record_id])
        with pytest.raises(ValidationError):
            BindingRevision(revision_id=compute_revision_id("s", (b, a)),
                            record_ids=(b, a), record_count=2, binding_set_id="s")
        with pytest.raises(ValidationError):
            BindingRevision(revision_id=compute_revision_id("s", (a, a)),
                            record_ids=(a, a), record_count=2, binding_set_id="s")

    def test_count_and_hash_must_match(self):
        ids = (declaration().record_id,)
        with pytest.raises(ValidationError):
            BindingRevision(revision_id=compute_revision_id("s", ids),
                            record_ids=ids, record_count=2, binding_set_id="s")
        with pytest.raises(ValidationError):
            BindingRevision(revision_id="rev_" + "0" * 64, record_ids=ids,
                            record_count=1, binding_set_id="s")

    def test_revision_identity_covers_set_id_and_membership(self):
        """Mandatory regression: revision identity changes when either the
        membership or the binding_set_id changes."""
        ids = tuple(sorted([declaration().record_id, assertion().record_id]))
        base = compute_revision_id("demo-printer", ids)
        assert compute_revision_id("other-set", ids) != base
        assert compute_revision_id("demo-printer", ids[:1]) != base


class TestResolutionResultInvariants:
    def test_resolved_target_only_when_bound(self):
        revision = BindingRevision(
            revision_id=compute_revision_id("s", ()), record_ids=(),
            record_count=0, binding_set_id="s")
        with pytest.raises(ValidationError):
            ResolutionResult(status="unbound", locator_subject=SUBJECT,
                             locator_property=None,
                             resolved_target=entity_anchor(),
                             candidate_targets=(), via_assertions=(),
                             applicability_basis=None, revision=revision,
                             subject_context=None)
        with pytest.raises(ValidationError):
            ResolutionResult(status="bound", locator_subject=SUBJECT,
                             locator_property=None, resolved_target=None,
                             candidate_targets=(), via_assertions=(),
                             applicability_basis="declared_interval",
                             revision=revision, subject_context=None)
