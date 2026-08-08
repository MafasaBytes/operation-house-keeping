"""MK-001 all-or-nothing set validation: every integrity invariant rejects
the complete set, at validating append and at load (crafted files bypass
append)."""

import json

import pytest

from backend.model_kernel.contracts import ModelIntegrityError
from backend.model_kernel.store import ModelStore, validate_record_collection

from tests.model_kernel.builders import (
    AS_BUILT,
    AS_DESIGNED,
    ENT_A,
    ENT_B,
    ENT_C,
    VIEW_FREE,
    assertion,
    contains_type,
    containment_world,
    instance_of_type,
    registration,
    store_with,
    withdrawal,
)


def expect_invalid(code, records, model_id="demo-printer"):
    collection = {record.record_id: record for record in records}
    with pytest.raises(ModelIntegrityError) as excinfo:
        validate_record_collection(model_id, collection, verify_hashes=False)
    assert excinfo.value.error_code == code
    return excinfo.value


class TestCollectionIdentity:
    def test_mapping_key_must_equal_record_id(self):
        record = registration()
        with pytest.raises(ModelIntegrityError) as excinfo:
            validate_record_collection("demo-printer",
                                       {"not-a-record-id": record})
        assert excinfo.value.error_code == "MODEL_RECORD_KEY_MISMATCH"

    def test_registration_duplicates_are_semantic_not_shape(self):
        """The registration-lifecycle guard: (a) `supersedes` fails as an
        unknown field (shape), and — independently — (b) two distinct
        registrations for one anchor fail with the semantic duplicate
        error."""
        from pydantic import ValidationError

        from backend.model_kernel.canonical import build_record
        from backend.model_kernel.contracts import EntityRegistration

        from tests.model_kernel.builders import AUTHORITY, T0, anchor

        with pytest.raises(ValidationError):
            build_record(EntityRegistration, anchor=anchor(), recorded_at=T0,
                         authority=AUTHORITY, supersedes=None)
        expect_invalid("MODEL_DUPLICATE_REGISTRATION",
                       [registration(note="one"), registration(note="two")])


class TestTypeLineage:
    def test_duplicate_current_type_name_invalid(self):
        expect_invalid("MODEL_DUPLICATE_TYPE_NAME",
                       [contains_type(note="one"), contains_type(note="two")])

    def test_lineage_supersession_valid_and_currentness_shifts(self):
        original = contains_type()
        corrected = contains_type(forward_label="physically contains",
                                  supersedes=original.record_id)
        collection = {r.record_id: r for r in (original, corrected)}
        loaded = validate_record_collection("demo-printer", collection,
                                            verify_hashes=False)
        assert loaded.current_type_by_name["contains"] == corrected.record_id

    def test_branched_lineage_two_current_tips_invalid(self):
        original = contains_type()
        branch_a = contains_type(note="a", supersedes=original.record_id)
        branch_b = contains_type(note="b", supersedes=original.record_id)
        expect_invalid("MODEL_DUPLICATE_TYPE_NAME",
                       [original, branch_a, branch_b])

    def test_branched_lineage_via_crafted_files_at_load(self, tmp_path):
        """Crafted files bypass validating append; load() must still refuse
        a branched lineage."""
        from backend.model_kernel.canonical import canonical_payload
        from backend.model_kernel.store import ModelStore

        original = contains_type()
        branch_a = contains_type(note="a", supersedes=original.record_id)
        branch_b = contains_type(note="b", supersedes=original.record_id)
        store = ModelStore(tmp_path / "demo-printer")
        for record in (original, branch_a, branch_b):
            text = json.dumps({**canonical_payload(record),
                               "record_id": record.record_id},
                              sort_keys=True, indent=2)
            (store.records_dir / f"{record.record_id}.json").write_text(text)
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_DUPLICATE_TYPE_NAME"

    @pytest.mark.parametrize("mutation", [
        dict(type_name="holds"),
        dict(hierarchy_semantics="none"),
        dict(context_requirement="view_independent"),
    ])
    def test_lineage_invariant_fields_must_be_preserved(self, mutation):
        original = contains_type()
        overrides = dict(supersedes=original.record_id)
        overrides.update(mutation)
        successor = contains_type(**overrides)
        expect_invalid("MODEL_SUPERSEDES_INVALID", [original, successor])

    def test_type_supersession_of_missing_target_invalid(self):
        expect_invalid("MODEL_SUPERSEDES_INVALID",
                       [contains_type(supersedes="rtd_" + "9" * 64)])


class TestAssertionReferences:
    def test_dangling_type_and_endpoints_invalid(self):
        kind = contains_type()
        reg_a, reg_b = registration(ENT_A), registration(ENT_B)
        good = assertion(kind)
        expect_invalid("MODEL_REFERENCE_INVALID",
                       [reg_a, reg_b, good])                    # type missing
        expect_invalid("MODEL_REFERENCE_INVALID",
                       [kind, reg_b, good])                     # source missing
        expect_invalid("MODEL_REFERENCE_INVALID",
                       [kind, reg_a, good])                     # target missing

    def test_context_arm_must_match_type_requirement(self):
        kind = contains_type()
        expect_invalid("MODEL_CONTEXT_INVALID",
                       [kind, registration(ENT_A), registration(ENT_B),
                        assertion(kind, context=VIEW_FREE)])
        io_kind = instance_of_type()
        expect_invalid("MODEL_CONTEXT_INVALID",
                       [io_kind, registration(ENT_A),
                        registration(ENT_B, kind="type_definition"),
                        assertion(io_kind, context=AS_BUILT)])

    def test_endpoint_kinds_checked_against_cited_definition(self):
        kind = contains_type()  # physical/logical only
        expect_invalid("MODEL_ENDPOINT_KIND_INVALID",
                       [kind, registration(ENT_A, kind="type_definition"),
                        registration(ENT_B), assertion(kind)])

    def test_unknown_fails_closed_but_optin_type_accepts(self):
        strict = contains_type()
        expect_invalid("MODEL_ENDPOINT_KIND_INVALID",
                       [strict, registration(ENT_A, kind="unknown"),
                        registration(ENT_B), assertion(strict)])
        permissive = contains_type(
            type_name="observed_with", hierarchy_semantics="none",
            source_referent_kinds=("physical_instance", "unknown"),
            target_referent_kinds=("physical_instance",))
        collection = {r.record_id: r for r in (
            permissive, registration(ENT_A, kind="unknown"),
            registration(ENT_B), assertion(permissive))}
        loaded = validate_record_collection("demo-printer", collection,
                                            verify_hashes=False)
        assert len(loaded.assertions) == 1  # unknown accepted when explicit

    def test_self_relation_governed_by_cited_definition(self):
        strict = contains_type(type_name="holds", hierarchy_semantics="none")
        expect_invalid("MODEL_SELF_RELATION_INVALID",
                       [strict, registration(ENT_A),
                        assertion(strict, source=ENT_A, target=ENT_A)])
        loop_ok = contains_type(
            type_name="mirrors", hierarchy_semantics="none",
            self_relation_allowed=True)
        collection = {r.record_id: r for r in (
            loop_ok, registration(ENT_A),
            assertion(loop_ok, source=ENT_A, target=ENT_A))}
        validate_record_collection("demo-printer", collection,
                                   verify_hashes=False)

    def test_model_record_evidence_must_exist_in_collection(self):
        from backend.model_kernel.contracts import ModelRecordEvidence

        kind = contains_type()
        ghost = ModelRecordEvidence(kind="model_record",
                                    record_id="reg_" + "9" * 64)
        expect_invalid("MODEL_REFERENCE_INVALID",
                       [kind, registration(ENT_A), registration(ENT_B),
                        assertion(kind, evidence=(ghost,))])

    def test_foreign_evidence_never_dereferenced(self):
        from backend.model_kernel.contracts import IdentityBindingRecordEvidence

        kind = contains_type()
        foreign = IdentityBindingRecordEvidence(
            kind="identity_binding_record", binding_set_id="no-such-set",
            record_id="anc_" + "f" * 64)
        collection = {r.record_id: r for r in (
            kind, registration(ENT_A), registration(ENT_B),
            assertion(kind, evidence=(foreign,)))}
        validate_record_collection("demo-printer", collection,
                                   verify_hashes=False)  # loads fine


class TestAssertionLineage:
    def test_supersession_same_lineage_source_target_context(self):
        kind = contains_type()
        original = assertion(kind)
        cases = [
            assertion(kind, source=ENT_C, supersedes=original.record_id),
            assertion(kind, target=ENT_C, supersedes=original.record_id),
            assertion(kind, context=AS_DESIGNED,
                      supersedes=original.record_id),
        ]
        for successor in cases:
            expect_invalid("MODEL_SUPERSEDES_INVALID",
                           [kind, registration(ENT_A), registration(ENT_B),
                            registration(ENT_C), original, successor])

    def test_successor_may_cite_corrected_definition_in_same_lineage(self):
        original_type = contains_type()
        corrected_type = contains_type(forward_label="physically contains",
                                       supersedes=original_type.record_id)
        original = assertion(original_type)
        successor = assertion(
            corrected_type, supersedes=original.record_id, note="re-affirmed")
        collection = {r.record_id: r for r in (
            original_type, corrected_type, registration(ENT_A),
            registration(ENT_B), original, successor)}
        loaded = validate_record_collection("demo-printer", collection,
                                            verify_hashes=False)
        assert loaded.superseded_by[original.record_id] == (
            successor.record_id,)

    def test_cross_lineage_supersession_invalid(self):
        containment = contains_type()
        other = contains_type(type_name="feeds", hierarchy_semantics="none")
        original = assertion(containment)
        wrong = assertion(other, supersedes=original.record_id)
        expect_invalid("MODEL_SUPERSEDES_INVALID",
                       [containment, other, registration(ENT_A),
                        registration(ENT_B), original, wrong])

    def test_withdrawal_of_missing_assertion_invalid(self):
        kind = contains_type()
        ghost = assertion(kind)  # never added
        expect_invalid("MODEL_WITHDRAWAL_INVALID",
                       [kind, registration(ENT_A), registration(ENT_B),
                        withdrawal(ghost)])


class TestLoadFromDisk:
    def test_tampered_content_invalidates_load(self, tmp_path):
        store = containment_world(tmp_path)
        record_file = sorted(store.records_dir.iterdir())[0]
        data = json.loads(record_file.read_text())
        data["note"] = "edited in place"
        record_file.write_text(json.dumps(data))
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_RECORD_HASH_MISMATCH"

    def test_unexpected_files_invalidate_load(self, tmp_path):
        store = containment_world(tmp_path)
        (store.records_dir / "notes.txt").write_text("junk")
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_foreign_record_kind_rejected(self, tmp_path):
        store = containment_world(tmp_path)
        alien = store.records_dir / ("anc_" + "0" * 64 + ".json")
        alien.write_text("{}")
        with pytest.raises(ModelIntegrityError):
            store.load()

    def test_empty_model_set_is_a_valid_empty_revision(self, tmp_path):
        store = ModelStore(tmp_path / "empty-model")
        loaded = store.load()
        assert loaded.revision.record_count == 0

    def test_one_bad_record_poisons_the_whole_set(self, tmp_path):
        kind = contains_type()
        store = store_with(tmp_path, kind, registration(ENT_A),
                           registration(ENT_B))
        orphan = assertion(kind, source=ENT_A, target=ENT_C)  # ENT_C absent
        # a crafted file bypasses validating append
        from backend.model_kernel.canonical import canonical_payload

        text = json.dumps({**canonical_payload(orphan),
                           "record_id": orphan.record_id}, sort_keys=True,
                          indent=2)
        (store.records_dir / f"{orphan.record_id}.json").write_text(text)
        with pytest.raises(ModelIntegrityError):
            store.load()
