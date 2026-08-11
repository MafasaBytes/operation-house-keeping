"""MK-001 cross-layer seam (test-only imports of identity_binding,
data_sources.contracts, and temporal_state contracts — for pinning and
verification only; runtime kernel code never imports them).

Verifies: embedded anchors equal their committed AnchorDeclarations
field-for-field; the seam has teeth (negative controls); no anchor id is
declared in two committed sets; restated evidence patterns equal the
upstream constants."""

from pathlib import Path

from backend.identity_binding.store import BindingStore
from backend.model_kernel.store import ModelStore
from backend.system_identity import EntityAnchor

DEMO_MODEL = Path("models/demo-printer")
BINDING_SETS = (Path("bindings/demo-printer"),
                Path("bindings/demo-printer-model"))


def committed_declarations():
    """ALL committed declarations — entity AND variable anchors alike, so
    every kernel-embedded anchor (VM-001 included) faces the seam."""
    declared = {}
    for set_dir in BINDING_SETS:
        loaded = BindingStore(set_dir).load()
        for anchor_id, anchor in loaded.anchors_by_id.items():
            assert anchor_id not in declared, (
                f"{anchor_id} declared in more than one committed set")
            declared[anchor_id] = anchor
    return declared


class TestEmbeddedAnchorEquality:
    def test_every_registration_matches_its_declaration_exactly(self):
        declared = committed_declarations()
        loaded = ModelStore(DEMO_MODEL).load()
        assert len(loaded.registrations_by_anchor) == 4
        for anchor_id, registration in loaded.registrations_by_anchor.items():
            assert anchor_id in declared, (
                f"{anchor_id} is registered but declared in no committed "
                "binding set")
            assert registration.anchor == declared[anchor_id], (
                f"{anchor_id}: embedded anchor diverges from its declaration")
        assert len(loaded.variable_registrations_by_anchor) >= 1
        for anchor_id, registration in (
                loaded.variable_registrations_by_anchor.items()):
            assert anchor_id in declared, (
                f"variable {anchor_id} is registered but declared in no "
                "committed binding set")
            assert registration.anchor == declared[anchor_id], (
                f"{anchor_id}: embedded variable anchor diverges from its "
                "declaration (including entity_anchor_id ownership)")

    def test_seam_has_teeth_diverged_value_detected(self, tmp_path):
        """Negative control: a re-hashed registration embedding a diverged
        display_name is perfectly valid to the kernel — only this seam
        comparison can catch it."""
        from backend.model_kernel.canonical import build_record
        from backend.model_kernel.contracts import EntityRegistration

        declared = committed_declarations()
        loaded = ModelStore(DEMO_MODEL).load()
        victim = next(iter(loaded.registrations_by_anchor.values()))
        diverged_anchor = victim.anchor.model_copy(
            update={"display_name": "Quietly renamed"})
        diverged = build_record(
            EntityRegistration, anchor=diverged_anchor,
            recorded_at=victim.recorded_at, authority=victim.authority,
            note=victim.note)
        # the kernel accepts it (structurally valid, correct hash) ...
        assert diverged.record_id.startswith("reg_")
        # ... and the seam comparison refuses it
        assert diverged.anchor != declared[diverged.anchor.anchor_id]

    def test_seam_has_teeth_never_declared_anchor_detected(self):
        """Negative control: a registration embedding a never-declared
        anchor is fully acceptable to the kernel — only the seam sweep can
        flag it. Build one, confirm the kernel accepts it, and confirm the
        sweep's membership check rejects it."""
        from datetime import UTC, datetime

        from backend.model_kernel.canonical import build_record
        from backend.model_kernel.contracts import (
            AuthorityRef,
            EntityRegistration,
        )

        ghost_anchor = EntityAnchor(
            anchor_id="ent_" + "9" * 32, namespace="demo-printer",
            display_name="Declared nowhere", referent_kind="unknown")
        ghost_registration = build_record(
            EntityRegistration, anchor=ghost_anchor,
            recorded_at=datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC),
            authority=AuthorityRef(kind="test_fixture", agent="seam-probe",
                                   method="manual_declaration"))
        assert ghost_registration.record_id.startswith("reg_")  # kernel-valid
        declared = committed_declarations()
        assert ghost_anchor.anchor_id not in declared  # the sweep flags it

    def test_cross_set_duplicate_sweep_covers_hex_tails(self):
        tails: dict[str, str] = {}
        for set_dir in BINDING_SETS:
            loaded = BindingStore(set_dir).load()
            for anchor_id in loaded.anchors_by_id:
                tail = anchor_id.split("_", 1)[1]
                assert tail not in tails, (
                    f"identifier {tail} used by {tails[tail]} and {anchor_id}")
                tails[tail] = anchor_id


class TestPatternPinning:
    def test_restated_constants_equal_upstream(self):
        """Staleness must be loud: the kernel restates upstream id shapes as
        literal regex constants; these pins fail if upstream vocabulary
        changes through an owner-approved slice."""
        import backend.model_kernel.contracts as mk

        from backend.identity_binding.contracts import (
            BINDING_SET_ID_PATTERN,
            LEDGER_RECORD_ID_PATTERN,
        )
        from backend.system_identity import (
            ENTITY_ANCHOR_ID_PATTERN,
            VARIABLE_ANCHOR_ID_PATTERN,
        )

        binding_ev = mk.IdentityBindingRecordEvidence.model_fields
        assert (binding_ev["record_id"].metadata[0].pattern
                == LEDGER_RECORD_ID_PATTERN)
        assert (binding_ev["binding_set_id"].metadata[0].pattern
                == BINDING_SET_ID_PATTERN)

        from backend.data_sources.contracts.models import RawRecord

        raw_pattern = RawRecord.model_fields["record_id"].metadata[0].pattern
        source_ev = mk.SourceRawRecordEvidence.model_fields
        assert source_ev["raw_record_id"].metadata[0].pattern == raw_pattern
        assert (mk.TemporalOccurrenceEvidence.model_fields[
            "occurrence_id"].metadata[0].pattern == raw_pattern)

        checksum_pattern = RawRecord.model_fields[
            "payload_checksum"].metadata[0].pattern
        assert (source_ev["payload_checksum"].metadata[0].pattern
                == checksum_pattern)

        assert ENTITY_ANCHOR_ID_PATTERN == r"^ent_[0-9a-f]{32}$"
        assert VARIABLE_ANCHOR_ID_PATTERN == r"^var_[0-9a-f]{32}$"

        # SN-001 (KR4): the structural arm restates the raw-record and
        # checksum shapes; staleness must be loud here too
        structural_ev = mk.StructuralSourceLocatorEvidence.model_fields
        assert (structural_ev["raw_record_id"].metadata[0].pattern
                == raw_pattern)
        assert (structural_ev["payload_checksum"].metadata[0].pattern
                == checksum_pattern)

    def test_committed_records_parity_across_canonicalizers(self):
        from backend.identity_binding import canonical as ib_canonical
        from backend.model_kernel import canonical as mk_canonical

        loaded = ModelStore(DEMO_MODEL).load()
        for record in loaded.records.values():
            assert (ib_canonical.canonical_bytes(record)
                    == mk_canonical.canonical_bytes(record))
