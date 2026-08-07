"""IB-001 repair slice: loaded-revision immutability, collection-key
identity binding, and append/staging integrity."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.identity_binding.canonical import (
    build_record,
    compute_revision_id,
)
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AuthorityRef,
    BindingIntegrityError,
    BindingRevision,
)
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore, validate_record_collection
from backend.system_identity import EntityAnchor
from backend.temporal_state.contracts import SourceSubjectRef

DEMO_SET = Path("bindings/demo-printer")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
IN_HOUR = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)
T1 = datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")

MAPPING_FIELDS = (
    "records", "anchors_by_id", "declarations", "assertions", "retractions",
    "closures", "rejections", "superseded_by", "retracted_by",
    "closure_records", "effective_applies",
)


def entity_declaration(note=""):
    return build_record(
        AnchorDeclaration, anchor_kind="entity",
        anchor=EntityAnchor(anchor_id="ent_" + "a" * 32,
                            namespace="demo-printer",
                            display_name="Extruder unit",
                            referent_kind="physical_instance"),
        recorded_at=T1, authority=AUTHORITY, note=note)


class TestLoadedRevisionImmutability:
    def test_every_exposed_mapping_rejects_mutation(self):
        loaded = BindingStore(DEMO_SET).load()
        for name in MAPPING_FIELDS:
            mapping = getattr(loaded, name)
            with pytest.raises((TypeError, AttributeError)):
                mapping["forged"] = None
            with pytest.raises((TypeError, AttributeError)):
                mapping.clear()
            with pytest.raises((TypeError, AttributeError)):
                mapping.pop("anything", None)

    def test_owner_reproduction_mutation_cannot_unbind(self):
        """Owner reproduction: clearing loaded.assertions used to flip a
        bound resolution to unbound under the same revision_id."""
        loaded = BindingStore(DEMO_SET).load()
        resolver = BindingResolver(loaded)
        before = resolver.resolve_subject(SUBJECT, at=IN_HOUR)
        assert before.status == "bound"
        with pytest.raises((TypeError, AttributeError)):
            loaded.assertions.clear()
        after = resolver.resolve_subject(SUBJECT, at=IN_HOUR)
        assert after.status == "bound"
        assert after == before  # same revision, locator, time → same result

    def test_input_mapping_mutation_cannot_affect_loaded_set(self):
        declaration = entity_declaration()
        source = {declaration.record_id: declaration}
        loaded = validate_record_collection("demo-printer", source)
        source.clear()
        assert declaration.record_id in loaded.records
        assert declaration.anchor.anchor_id in loaded.anchors_by_id
        assert loaded.revision.record_count == 1


class TestCollectionKeyIdentity:
    def test_mismatched_mapping_key_rejected(self):
        """Owner reproduction: a mapping keyed 'not-a-record-id' used to be
        accepted and the forged key became revision membership."""
        declaration = entity_declaration()
        with pytest.raises(BindingIntegrityError) as excinfo:
            validate_record_collection("demo-printer",
                                       {"not-a-record-id": declaration})
        assert excinfo.value.error_code == "BINDING_RECORD_KEY_MISMATCH"

    def test_revision_contract_rejects_malformed_member(self):
        with pytest.raises(ValidationError):
            BindingRevision(
                revision_id=compute_revision_id("s", ("not-a-record-id",)),
                record_ids=("not-a-record-id",), record_count=1,
                binding_set_id="s")

    def test_load_revision_rejects_malformed_member(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        store.append(entity_declaration())
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load_revision(("not-a-record-id",))
        assert excinfo.value.error_code == "BINDING_REVISION_INVALID"

    def test_load_revision_rejects_traversal_member_before_reading(
        self, tmp_path
    ):
        """A traversal-shaped member must be rejected by pattern, with the
        typed revision error — never used to construct a path."""
        store = BindingStore(tmp_path / "demo-printer")
        store.append(entity_declaration())
        outside = tmp_path / "outside.json"
        outside.write_text("{}")
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load_revision(("../../outside",))
        assert excinfo.value.error_code == "BINDING_REVISION_INVALID"

    def test_load_revision_rejects_duplicate_membership(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        record_id = store.append(entity_declaration())
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load_revision((record_id, record_id))
        assert excinfo.value.error_code == "BINDING_REVISION_INVALID"

    def test_valid_exact_membership_still_replays_identically(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        store.append(entity_declaration())
        earlier = store.load().revision
        store.append(entity_declaration(note="later"))
        replayed = store.load_revision(earlier.record_ids)
        assert replayed.revision == earlier


class TestAppendIntegrity:
    def test_identical_reappend_remains_noop(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        record = entity_declaration()
        store.append(record)
        store.append(record)
        files = list(store.records_dir.iterdir())
        assert [p.name for p in files] == [f"{record.record_id}.json"]

    def test_reappend_over_tampered_file_detected_not_silent(self, tmp_path):
        """Owner reproduction: appending the original record over a
        tampered stored file used to report success."""
        store = BindingStore(tmp_path / "demo-printer")
        record = entity_declaration()
        store.append(record)
        path = store.records_dir / f"{record.record_id}.json"
        tampered = json.loads(path.read_text())
        tampered["note"] = "tampered in place"
        path.write_text(json.dumps(tampered))
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.append(record)
        assert excinfo.value.error_code == "BINDING_RECORD_HASH_MISMATCH"
        # the invalid existing authority is surfaced, never overwritten
        assert json.loads(path.read_text())["note"] == "tampered in place"

    def test_staging_residue_cannot_invalidate_load(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        store.append(entity_declaration())
        store.staging_dir.mkdir(exist_ok=True)
        (store.staging_dir / "crashed-append.tmp").write_text("partial")
        loaded = store.load()  # residue lives outside the scanned ledger
        assert loaded.revision.record_count == 1

    def test_failed_promotion_leaves_ledger_clean(self, tmp_path, monkeypatch):
        import backend.identity_binding.store as store_module

        store = BindingStore(tmp_path / "demo-printer")
        store.append(entity_declaration())

        def broken_replace(src, dst):
            raise OSError("promotion failed")

        monkeypatch.setattr(store_module.os, "replace", broken_replace)
        with pytest.raises(OSError):
            store.append(entity_declaration(note="second"))
        monkeypatch.undo()
        # the ledger holds only complete final records — no partial member,
        # no staging residue promoted, and the set still loads
        assert all(p.suffix == ".json" and not p.name.endswith(".tmp")
                   for p in store.records_dir.iterdir())
        assert list(store.staging_dir.glob("*")) == []
        assert store.load().revision.record_count == 1
