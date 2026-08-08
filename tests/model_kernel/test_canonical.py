"""MK-001 canonical identity: full-SHA-256 content-derived ids, UTC
normalization, evidence canonicalization, and byte-parity with the
identity_binding canonicalizer (test-only seam import)."""

import json
from datetime import UTC, datetime, timedelta, timezone

from backend.identity_binding import canonical as ib_canonical
from backend.model_kernel import canonical as mk_canonical
from backend.model_kernel.canonical import (
    build_record,
    canonical_bytes,
    compute_record_id,
    compute_revision_id,
    verify_record_id,
)
from backend.model_kernel.contracts import (
    AuthorityRef,
    EntityRegistration,
    IdentityBindingRecordEvidence,
    LifecycleViewContext,
    OwnerDeclarationEvidence,
    RelationshipAssertion,
)
from backend.system_identity import EntityAnchor

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
PLUS2 = timezone(timedelta(hours=2))
AUTHORITY = AuthorityRef(kind="test_fixture", agent="mk001_demo_fixture",
                         method="manual_declaration")
OWNER_EV = OwnerDeclarationEvidence(kind="owner_declaration",
                                    statement="synthetic demo structure")
BINDING_EV = IdentityBindingRecordEvidence(
    kind="identity_binding_record", binding_set_id="demo-printer",
    record_id="anc_" + "e" * 64)


def registration(recorded_at=T0, note=""):
    return build_record(
        EntityRegistration,
        anchor=EntityAnchor(anchor_id="ent_" + "a" * 32,
                            namespace="demo-printer",
                            display_name="Demo entity",
                            referent_kind="physical_instance"),
        recorded_at=recorded_at, authority=AUTHORITY, note=note)


def assertion(evidence):
    return build_record(
        RelationshipAssertion, type_id="rtd_" + "0" * 64,
        source_anchor_id="ent_" + "a" * 32, target_anchor_id="ent_" + "b" * 32,
        context=LifecycleViewContext(kind="lifecycle_view", view="as_built"),
        evidence=evidence, supersedes=None, recorded_at=T0,
        authority=AUTHORITY, note="")


class TestRecordIdentity:
    def test_full_sha256_prefixed_and_verifiable(self):
        record = registration()
        prefix, digest = record.record_id.split("_", 1)
        assert prefix == "reg" and len(digest) == 64
        assert set(digest) <= set("0123456789abcdef")
        assert verify_record_id(record)
        assert compute_record_id(record) == record.record_id

    def test_content_changes_change_the_id(self):
        assert registration(note="a").record_id != registration(note="b").record_id

    def test_equal_instants_different_offsets_hash_identically(self):
        utc = registration(recorded_at=datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC))
        offset = registration(
            recorded_at=datetime(2026, 8, 8, 14, 0, 0, tzinfo=PLUS2))
        assert utc.record_id == offset.record_id

    def test_canonical_bytes_sorted_compact_utc_and_id_excluded(self):
        payload = canonical_bytes(registration()).decode()
        parsed = json.loads(payload)
        assert "record_id" not in parsed
        assert ": " not in payload and ", " not in payload
        assert "+00:00" in payload
        assert list(parsed) == sorted(parsed)

    def test_schema_version_is_part_of_identity(self):
        record = registration()
        tampered = record.model_copy(update={"schema_version": "2"})
        assert compute_record_id(tampered) != record.record_id


class TestEvidenceCanonicalization:
    def test_permuted_and_duplicated_evidence_same_record_id(self):
        """Golden amendment-6 test: evidence order carries no meaning and
        repeating identical evidence adds no support."""
        forward = assertion((OWNER_EV, BINDING_EV))
        permuted = assertion((BINDING_EV, OWNER_EV))
        duplicated = assertion((BINDING_EV, OWNER_EV, BINDING_EV, OWNER_EV))
        assert forward.record_id == permuted.record_id == duplicated.record_id
        assert len(duplicated.evidence) == 2  # duplicates normalized away

    def test_evidence_stored_in_canonical_order(self):
        record = assertion((OWNER_EV, BINDING_EV))
        keys = [mk_canonical.canonical_bytes(ref) for ref in record.evidence]
        assert keys == sorted(keys)

    def test_min_one_applies_after_normalization(self):
        record = assertion((OWNER_EV, OWNER_EV))
        assert len(record.evidence) == 1


class TestRevisionIdentity:
    def test_revision_formula_and_sensitivity(self):
        ids = tuple(sorted([registration(note="1").record_id,
                            registration(note="2").record_id]))
        base = compute_revision_id("demo-printer", ids)
        assert base.startswith("mrv_") and len(base) == 4 + 64
        assert compute_revision_id("other-model", ids) != base
        assert compute_revision_id("demo-printer", ids[:1]) != base
        assert compute_revision_id("demo-printer", ids[::-1]) == base  # sorted


class TestCanonicalParity:
    """Byte-parity with identity_binding's canonicalizer, enforced by shared
    vectors — never by shared code and never by modifying accepted IB code."""

    def test_shared_vectors_produce_identical_bytes(self):
        vectors = [
            AUTHORITY,
            OWNER_EV,
            BINDING_EV,
            registration(),
            assertion((OWNER_EV, BINDING_EV)),
        ]
        for model in vectors:
            assert (ib_canonical.canonical_bytes(model)
                    == mk_canonical.canonical_bytes(model))

    def test_offset_normalization_parity(self):
        record = registration(
            recorded_at=datetime(2026, 8, 8, 14, 0, 0, tzinfo=PLUS2))
        ib_payload = ib_canonical.canonical_bytes(record).decode()
        assert "+00:00" in ib_payload and "14:00" not in ib_payload
