"""MK-001 closure series: the last three owner-mandated repairs, encoded
red-first as observable behavior at public boundaries.

C1  ``build_record`` leaks raw pydantic ValidationError on bad field
    values and raw AttributeError/KeyError while identifying the record
    kind — every constructive failure must surface as a typed, path-free
    ``MODEL_RECORD_INVALID`` that does not echo hostile input. (Direct
    construction of the contract models keeps ordinary pydantic behavior;
    the guarantee is for the operational API.)
C2  ``replay([])`` answers with a valid empty revision even when the
    records directory has been destroyed — empty membership is valid ONLY
    against an existing, readable store, and a destroyed store must never
    be misreported as a merely-missing member. Input validation still
    precedes the availability check.
C3  ``ModelStore.append`` cleanup after a failed promotion is not
    best-effort: if unlinking the staging temp also fails, the raw
    OSError replaces the intended typed ``MODEL_STORAGE_FAILURE``.
"""

import json
import shutil
from pathlib import Path
from typing import Literal

import pytest
from pydantic import BaseModel

from backend.model_kernel import (
    EntityRegistration,
    ModelIntegrityError,
    ModelKernelError,
    RelationshipAssertion,
    build_record,
)
from backend.model_kernel.canonical import compute_revision_id, verify_record_id

from tests.model_kernel.builders import (
    AS_BUILT,
    AUTHORITY,
    ENT_A,
    ENT_B,
    ENT_C,
    EVIDENCE,
    T0,
    anchor as anchor_value,
    assertion,
    contains_type,
    containment_world,
    registration,
)


class _UnknownKindRecord(BaseModel):
    """Looks like a record class, but its kind is not in the prefix map."""

    record_kind: Literal["mystery_kind"] = "mystery_kind"
    record_id: str = ""
    note: str = ""


class _NoKindRecord(BaseModel):
    """A model class that declares no record_kind field at all."""

    record_id: str = ""


WELL_FORMED_TYPE_ID = "rtd_" + "0" * 64

INVALID_BUILDS = [
    pytest.param(lambda: build_record(EntityRegistration),
                 id="missing_required_fields"),
    pytest.param(lambda: build_record(
        EntityRegistration, anchor="bad", recorded_at=T0,
        authority=AUTHORITY, note=""),
        id="malformed_anchor"),
    pytest.param(lambda: build_record(
        RelationshipAssertion, type_id=WELL_FORMED_TYPE_ID,
        source_anchor_id=ENT_A, target_anchor_id=ENT_B,
        context={"kind": "lifecycle_view"}, evidence=EVIDENCE,
        supersedes=None, recorded_at=T0, authority=AUTHORITY, note=""),
        id="malformed_context"),
    pytest.param(lambda: build_record(
        RelationshipAssertion, type_id=WELL_FORMED_TYPE_ID,
        source_anchor_id=ENT_A, target_anchor_id=ENT_B,
        context=AS_BUILT, evidence=("garbage",),
        supersedes=None, recorded_at=T0, authority=AUTHORITY, note=""),
        id="malformed_evidence"),
    pytest.param(lambda: build_record(dict), id="non_record_class_dict"),
    pytest.param(lambda: build_record(None), id="non_record_class_none"),
    pytest.param(lambda: build_record(object), id="non_record_class_object"),
    pytest.param(lambda: build_record(_UnknownKindRecord, note="x"),
                 id="unknown_record_kind"),
    pytest.param(lambda: build_record(_NoKindRecord),
                 id="missing_record_kind_field"),
]


# --------------------------------------------------------------- closure 1
class TestBuildRecordFailsThroughTheKernelErrorTree:
    @pytest.mark.parametrize("call", INVALID_BUILDS)
    def test_invalid_build_is_a_typed_record_error(self, call):
        """Every constructive failure — bad field values, a non-record
        class, an unknown or absent record kind — surfaces as the kernel's
        own MODEL_RECORD_INVALID, never a raw pydantic/attribute error."""
        with pytest.raises(ModelKernelError) as excinfo:
            call()
        assert isinstance(excinfo.value, ModelIntegrityError)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_error_message_does_not_echo_hostile_input(self):
        """The typed message names the failure, not the payload: an
        attacker-controlled field value must not be reflected back."""
        with pytest.raises(ModelKernelError) as excinfo:
            build_record(EntityRegistration, anchor="HOSTILE_PAYLOAD_XYZ",
                         recorded_at=T0, authority=AUTHORITY, note="")
        assert isinstance(excinfo.value, ModelIntegrityError)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        assert "HOSTILE_PAYLOAD_XYZ" not in str(excinfo.value)

    def test_unencodable_content_stays_typed_and_unechoed(self):
        """Closure variant of the already-pinned surrogate case: typed,
        and the hostile content is not echoed."""
        hostile = json.loads('"\\ud800"')
        with pytest.raises(ModelKernelError) as excinfo:
            build_record(EntityRegistration, anchor=anchor_value(ENT_C),
                         recorded_at=T0, authority=AUTHORITY, note=hostile)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        assert hostile not in str(excinfo.value)

    def test_valid_build_still_returns_a_verifying_record(self):
        """Positive control: the typed-failure gate is a gate, not a wall."""
        record = build_record(EntityRegistration, anchor=anchor_value(ENT_C),
                              recorded_at=T0, authority=AUTHORITY, note="")
        assert record.record_kind == "entity_registration"
        assert verify_record_id(record)


# --------------------------------------------------------------- closure 2
class TestReplayDistinguishesEmptyFromUnavailable:
    def test_empty_membership_on_live_store_is_the_empty_revision(self,
                                                                  tmp_path):
        """Non-regression pin: replay([]) against an existing readable
        store is valid and answers the computed empty revision."""
        store = containment_world(tmp_path)
        loaded = store.replay([])
        assert loaded.revision.record_count == 0
        assert loaded.revision.record_ids == ()
        assert loaded.revision.revision_id == compute_revision_id(
            store.model_id, ())

    def test_empty_membership_on_deleted_store_is_a_storage_failure(
            self, tmp_path):
        """An empty revision can only be attested by a store that exists:
        a destroyed records directory is unavailable storage, not a valid
        empty answer."""
        store = containment_world(tmp_path)
        shutil.rmtree(store.records_dir)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([])
        assert excinfo.value.error_code == "MODEL_STORAGE_FAILURE"
        assert str(tmp_path) not in str(excinfo.value)

    def test_records_dir_replaced_by_file_is_a_storage_failure(self,
                                                               tmp_path):
        store = containment_world(tmp_path)
        shutil.rmtree(store.records_dir)
        store.records_dir.write_text("not a directory", encoding="utf-8")
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([])
        assert excinfo.value.error_code == "MODEL_STORAGE_FAILURE"
        assert str(tmp_path) not in str(excinfo.value)

    def test_malformed_member_precedes_the_availability_check(self,
                                                              tmp_path):
        """Order pin: input validation still comes first — a malformed
        member id is rejected as revision input even when the store is
        also destroyed."""
        store = containment_world(tmp_path)
        shutil.rmtree(store.records_dir)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay(["not-an-id"])
        assert excinfo.value.error_code == "MODEL_REVISION_INVALID"

    def test_duplicate_members_precede_the_availability_check(self,
                                                              tmp_path):
        """Order pin: duplicates are revision-input defects even when the
        store is destroyed."""
        store = containment_world(tmp_path)
        member = next(iter(store.load().records))
        shutil.rmtree(store.records_dir)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([member, member])
        assert excinfo.value.error_code == "MODEL_REVISION_INVALID"

    def test_destroyed_store_is_not_misreported_as_a_missing_member(
            self, tmp_path):
        """A well-formed member id against a destroyed store must fail as
        MODEL_STORAGE_FAILURE — the store's unavailability, not a merely
        absent member, is the fact being reported."""
        store = containment_world(tmp_path)
        member = next(iter(store.load().records))
        shutil.rmtree(store.records_dir)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([member])
        assert excinfo.value.error_code == "MODEL_STORAGE_FAILURE"
        assert str(tmp_path) not in str(excinfo.value)

    def test_subset_replay_does_not_require_excluded_members_to_validate(
            self, tmp_path):
        """Non-regression pin: exact-subset replay reads only the supplied
        membership — a corrupted ledger member OUTSIDE the reference-closed
        subset does not poison the answer."""
        kind = contains_type()
        edge = assertion(kind, source=ENT_A, target=ENT_B)
        store = containment_world(tmp_path, edge)
        corrupted = store.records_dir / f"{edge.record_id}.json"
        assert corrupted.exists()
        corrupted.write_text("{ this is not a record", encoding="utf-8")

        subset = [kind.record_id, registration(ENT_A).record_id,
                  registration(ENT_B).record_id]
        loaded = store.replay(subset)
        assert set(loaded.revision.record_ids) == set(subset)
        assert edge.record_id not in loaded.records


# --------------------------------------------------------------- closure 3
class TestAppendCleanupIsBestEffort:
    def test_failed_cleanup_never_replaces_the_typed_outcome(self, tmp_path,
                                                             monkeypatch):
        """When promotion fails AND unlinking the staging temp also fails,
        the cleanup failure is swallowed (staging residue is acceptable)
        and the public outcome stays MODEL_STORAGE_FAILURE, path-free; the
        committed ledger is untouched."""
        store = containment_world(tmp_path)
        before = store.load()
        prior_membership = set(before.records)
        new_record = registration(ENT_C)

        def deny_replace(src, dst, *args, **kwargs):
            raise OSError(13, "replace denied")

        def deny_unlink(self, missing_ok=False):
            raise OSError(13, "unlink denied")

        with monkeypatch.context() as patched:
            patched.setattr("backend.model_kernel.store.os.replace",
                            deny_replace)
            patched.setattr(Path, "unlink", deny_unlink)
            with pytest.raises(ModelKernelError) as excinfo:
                store.append(new_record)

        assert isinstance(excinfo.value, ModelIntegrityError)
        assert excinfo.value.error_code == "MODEL_STORAGE_FAILURE"
        assert str(tmp_path) not in str(excinfo.value)

        after = store.load()  # patches undone: ledger unchanged and loadable
        assert set(after.records) == prior_membership
        assert after.revision == before.revision


class TestReviewerClosureFindings:
    """The two CONFIRMED must-fix leaks plus the message-hygiene finding
    from the final targeted audit, encoded red-first."""

    @pytest.mark.parametrize("bomb", [
        pytest.param(RuntimeError("membership bomb"), id="runtime_error"),
        pytest.param(OSError(5, "io bomb"), id="os_error"),
    ])
    def test_raising_membership_iterable_stays_typed(self, tmp_path, bomb):
        """A membership generator that raises mid-iteration (a file-backed
        id source hitting I/O trouble, say) must fail typed — never leak
        the raw exception from `list(record_ids)`."""
        store = containment_world(tmp_path)

        def membership():
            yield "reg_" + "a" * 64
            raise bomb

        with pytest.raises(ModelKernelError) as excinfo:
            store.replay(membership())
        assert excinfo.value.error_code == "MODEL_REVISION_INVALID"
        assert str(tmp_path) not in str(excinfo.value)

    def test_duck_class_lacking_model_copy_stays_typed(self):
        """`draft.model_copy` is looked up during finalization; a
        duck-typed class that survives construction but lacks it must
        fail typed, not with a raw AttributeError."""

        class _Field:
            default = "entity_registration"

        class _Duck:
            model_fields = {"record_kind": _Field()}

            def __init__(self, **fields):
                pass

        with pytest.raises(ModelKernelError) as excinfo:
            build_record(_Duck)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_hostile_class_name_never_reaches_the_message(self):
        """The class-name interpolation must not let an attacker-shaped
        __name__ smuggle a path or payload into the path-free message."""
        hostile = type("record from /etc/secret HOSTILE_NAME_XYZ", (), {})
        with pytest.raises(ModelKernelError) as excinfo:
            build_record(hostile)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        assert "/etc" not in str(excinfo.value)
        assert "HOSTILE_NAME_XYZ" not in str(excinfo.value)
