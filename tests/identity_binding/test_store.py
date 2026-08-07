"""IB-001 write-once binding store: atomic append, all-or-nothing
validation, deterministic revisions, exact-membership replay."""

import json
from datetime import UTC, datetime

import pytest

from backend.identity_binding.canonical import build_record
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    ApplicabilityClosure,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    BindingConfigurationError,
    BindingIntegrityError,
    BindingRejection,
    BindingRetraction,
    DeclaredBoundary,
    UnknownBoundary,
)
from backend.identity_binding.store import BindingStore, validate_record_collection
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

ENT = "ent_" + "a" * 32
ENT2 = "ent_" + "c" * 32
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


def scope(start_kind="declared", end_kind="declared"):
    boundaries = {
        "declared_start": DeclaredBoundary(kind="declared", at=T0),
        "declared_end": DeclaredBoundary(kind="declared", at=T1),
        "unknown": UnknownBoundary(kind="unknown"),
    }
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=(boundaries["declared_start"]
                        if start_kind == "declared" else boundaries["unknown"]),
        end_boundary=(boundaries["declared_end"]
                      if end_kind == "declared" else boundaries["unknown"]),
        interval_semantics="half_open",
    )


def entity_declaration(anchor_id=ENT, note=""):
    return build_record(
        AnchorDeclaration, anchor_kind="entity",
        anchor=EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                            display_name="Extruder unit",
                            referent_kind="physical_instance"),
        recorded_at=T1, authority=AUTHORITY, note=note)


def variable_declaration(anchor_id=VAR, owner=ENT):
    return build_record(
        AnchorDeclaration, anchor_kind="variable",
        anchor=VariableAnchor(anchor_id=anchor_id, entity_anchor_id=owner,
                              namespace="demo-printer",
                              display_name="Hotend temperature"),
        recorded_at=T1, authority=AUTHORITY)


def subject_assertion(target=ENT, applies=None, supersedes=None,
                      subject=SUBJECT, note=""):
    return build_record(
        BindingAssertion, binding_kind="subject", subject=subject,
        property=None, target_anchor_id=target,
        applies=applies or scope(), recorded_at=T1, authority=AUTHORITY,
        supersedes=supersedes, note=note)


def property_assertion(target=VAR, note=""):
    return build_record(
        BindingAssertion, binding_kind="property", subject=SUBJECT,
        property=PROP, target_anchor_id=target, applies=scope(),
        recorded_at=T1, authority=AUTHORITY, note=note)


def store_with(tmp_path, *records, set_id="demo-printer"):
    store = BindingStore(tmp_path / set_id)
    for record in records:
        store.append(record)
    return store


class TestAppend:
    def test_append_writes_named_readable_json(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        record = entity_declaration()
        assert store.append(record) == record.record_id
        path = tmp_path / "demo-printer" / "records" / f"{record.record_id}.json"
        assert json.loads(path.read_text())["record_id"] == record.record_id

    def test_identical_reappend_is_a_noop(self, tmp_path):
        store = BindingStore(tmp_path / "demo-printer")
        record = entity_declaration()
        store.append(record)
        store.append(record)
        assert len(list((tmp_path / "demo-printer" / "records").iterdir())) == 1

    def test_set_id_pattern_enforced(self, tmp_path):
        with pytest.raises(BindingConfigurationError):
            BindingStore(tmp_path / "Demo Printer")


class TestLoadValidSet:
    def test_load_returns_sorted_deterministic_revision(self, tmp_path):
        records = [entity_declaration(), variable_declaration(),
                   subject_assertion(), property_assertion()]
        store = store_with(tmp_path, *records)
        loaded = store.load()
        assert loaded.revision.binding_set_id == "demo-printer"
        assert list(loaded.revision.record_ids) == sorted(
            r.record_id for r in records)
        assert store.load().revision == loaded.revision  # deterministic reload
        assert set(loaded.anchors_by_id) == {ENT, VAR}

    def test_lifecycle_links_computed(self, tmp_path):
        original = subject_assertion(note="first")
        successor = subject_assertion(target=ENT2, note="corrected",
                                      supersedes=original.record_id)
        retraction = build_record(BindingRetraction,
                                  retracts=original.record_id,
                                  recorded_at=T1, authority=AUTHORITY)
        store = store_with(tmp_path, entity_declaration(),
                           entity_declaration(anchor_id=ENT2, note="second"),
                           original, successor, retraction)
        loaded = store.load()
        assert loaded.superseded_by[original.record_id] == (successor.record_id,)
        assert loaded.retracted_by[original.record_id] == (retraction.record_id,)
        assert loaded.superseded_by[successor.record_id] == ()

    def test_closure_produces_effective_applies(self, tmp_path):
        open_ended = subject_assertion(applies=scope(end_kind="unknown"))
        closure = build_record(ApplicabilityClosure,
                               closes=open_ended.record_id, end=T1,
                               recorded_at=T1, authority=AUTHORITY)
        store = store_with(tmp_path, entity_declaration(), open_ended, closure)
        loaded = store.load()
        effective = loaded.effective_applies[open_ended.record_id]
        assert effective.end_boundary.kind == "declared"
        assert effective.end_boundary.at == T1
        assert loaded.closure_records[open_ended.record_id] == (closure.record_id,)
        # declared_applies stays untouched on the record itself
        assert loaded.assertions[open_ended.record_id].applies.end_boundary.kind == (
            "unknown")


class TestIntegrityFailures:
    def test_tampered_content_invalidates_set(self, tmp_path):
        store = store_with(tmp_path, entity_declaration())
        record_file = next((tmp_path / "demo-printer" / "records").iterdir())
        data = json.loads(record_file.read_text())
        data["note"] = "edited in place"
        record_file.write_text(json.dumps(data))
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_RECORD_HASH_MISMATCH"

    def test_duplicate_anchor_id_invalidates_set(self, tmp_path):
        """Mandatory regression: duplicate canonical anchor declarations
        invalidate the complete set, even under distinct record ids."""
        store = store_with(tmp_path, entity_declaration(note="one"),
                           entity_declaration(note="two"))
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_DUPLICATE_ANCHOR_ID"

    def test_cross_kind_identifier_invalidates_set(self, tmp_path):
        shared_hex = "d" * 32
        store = store_with(
            tmp_path, entity_declaration(anchor_id="ent_" + shared_hex),
            variable_declaration(anchor_id="var_" + shared_hex,
                                 owner="ent_" + shared_hex))
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_DUPLICATE_ANCHOR_ID"

    @pytest.mark.parametrize("records,code", [
        ((variable_declaration(),), "BINDING_ANCHOR_REFERENCE_INVALID"),
        ((subject_assertion(),), "BINDING_ANCHOR_REFERENCE_INVALID"),
        ((entity_declaration(),
          build_record(BindingRejection, subject=SUBJECT, property=None,
                       rejected_anchor_id=ENT2, recorded_at=T1,
                       authority=AUTHORITY)), "BINDING_ANCHOR_REFERENCE_INVALID"),
        ((entity_declaration(),
          subject_assertion(supersedes="iba_" + "0" * 64)),
         "BINDING_SUPERSEDES_INVALID"),
        ((entity_declaration(),
          build_record(BindingRetraction, retracts="iba_" + "0" * 64,
                       recorded_at=T1, authority=AUTHORITY)),
         "BINDING_RETRACTS_INVALID"),
        ((entity_declaration(),
          build_record(ApplicabilityClosure, closes="iba_" + "0" * 64,
                       end=T1, recorded_at=T1, authority=AUTHORITY)),
         "BINDING_CLOSURE_INVALID"),
    ])
    def test_dangling_references_invalidate_set(self, tmp_path, records, code):
        store = store_with(tmp_path, *records)
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == code

    def test_supersedes_must_match_kind_and_locator(self, tmp_path):
        subject_b = SourceSubjectRef(source_id="printer-1",
                                     adapter_id="moonraker",
                                     subject_identifier="heater_bed")
        original = subject_assertion(subject=subject_b)
        wrong_locator = subject_assertion(target=ENT2,
                                          supersedes=original.record_id)
        store = store_with(tmp_path, entity_declaration(),
                           entity_declaration(anchor_id=ENT2, note="second"),
                           original, wrong_locator)
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_SUPERSEDES_INVALID"

    def test_supersession_cycle_rejected(self):
        """Content-derived ids make real cycles cryptographically
        implausible; the validator still refuses forged ones."""
        first = subject_assertion(note="a")
        second = subject_assertion(target=ENT2, supersedes=first.record_id)
        forged = first.model_copy(update={"supersedes": second.record_id})
        records = {r.record_id: r for r in (
            entity_declaration(), entity_declaration(anchor_id=ENT2, note="x"),
            forged, second)}
        with pytest.raises(BindingIntegrityError) as excinfo:
            validate_record_collection("demo-printer", records,
                                       verify_hashes=False)
        assert excinfo.value.error_code == "BINDING_SUPERSEDES_INVALID"

    def test_closure_on_declared_end_rejected(self, tmp_path):
        closed = subject_assertion()  # declared end already
        closure = build_record(ApplicabilityClosure, closes=closed.record_id,
                               end=T1, recorded_at=T1, authority=AUTHORITY)
        store = store_with(tmp_path, entity_declaration(), closed, closure)
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_CLOSURE_INVALID"

    def test_closure_must_exceed_declared_start(self, tmp_path):
        open_ended = subject_assertion(applies=scope(end_kind="unknown"))
        closure = build_record(ApplicabilityClosure,
                               closes=open_ended.record_id, end=T0,
                               recorded_at=T1, authority=AUTHORITY)
        store = store_with(tmp_path, entity_declaration(), open_ended, closure)
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_CLOSURE_INVALID"

    def test_two_closures_for_one_assertion_rejected(self, tmp_path):
        open_ended = subject_assertion(applies=scope(end_kind="unknown"))
        first = build_record(ApplicabilityClosure, closes=open_ended.record_id,
                             end=T1, recorded_at=T1, authority=AUTHORITY)
        second = build_record(ApplicabilityClosure, closes=open_ended.record_id,
                              end=datetime(2026, 8, 7, 22, 0, 0, tzinfo=UTC),
                              recorded_at=T1, authority=AUTHORITY,
                              note="contradictory")
        store = store_with(tmp_path, entity_declaration(), open_ended,
                           first, second)
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "BINDING_MULTIPLE_CLOSURES"


class TestRevisionReplay:
    def test_explicit_membership_reloads_earlier_state(self, tmp_path):
        declaration = entity_declaration()
        original = subject_assertion()
        store = store_with(tmp_path, declaration, original)
        earlier = store.load().revision
        store.append(entity_declaration(anchor_id=ENT2, note="later"))
        store.append(subject_assertion(target=ENT2, note="later",
                                       supersedes=original.record_id))
        current = store.load()
        assert current.revision.record_count == 4
        replayed = store.load_revision(earlier.record_ids)
        assert replayed.revision == earlier
        assert set(replayed.records) == set(earlier.record_ids)

    def test_missing_member_rejected(self, tmp_path):
        store = store_with(tmp_path, entity_declaration())
        with pytest.raises(BindingIntegrityError) as excinfo:
            store.load_revision(("iba_" + "0" * 64,))
        assert excinfo.value.error_code == "BINDING_REVISION_INVALID"

    def test_non_reference_closed_subset_rejected(self, tmp_path):
        declaration = entity_declaration()
        assertion = subject_assertion()
        store = store_with(tmp_path, declaration, assertion)
        with pytest.raises(BindingIntegrityError):
            store.load_revision((assertion.record_id,))  # anchor missing
