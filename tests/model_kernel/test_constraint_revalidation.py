"""CN-001 Slice A adversarial trust-boundary and ledger-freeze tests."""

import hashlib
import json
from dataclasses import replace

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    ConstraintDeclarationResult,
    ExactNumericUpperBound,
    ModelKernelError,
    ModelQueries,
    ModelRevision,
    ModelStore,
    NumericBoundary,
    OwnerDeclarationEvidence,
    VariableConstraintCollectionResult,
)
from backend.model_kernel.store import validate_record_collection
from backend.system_identity import ConstraintAnchor
from tests.model_kernel.builders import (
    CON_A,
    ENT_A,
    VAR_A,
    constraint_declaration,
    constraint_registration,
    registration,
    store_with,
    variable_registration,
)
from tests.model_kernel.test_demo_model import (
    CURRENT_REVISION,
    DEMO_MODEL,
    FROZEN_ES001_MODEL_RECORDS,
    FROZEN_CN001_MODEL_RECORDS,
    FROZEN_MK001_RECORDS,
    FROZEN_PT001_MODEL_RECORDS, FROZEN_VP001_MODEL_RECORDS,
    FROZEN_SN001_MODEL_RECORDS,
    FROZEN_VM001_RECORD,
    FROZEN_VS001_RECORD,
)


def base_records():
    return (registration(ENT_A), variable_registration(VAR_A, owner=ENT_A))


def registration_store(tmp_path):
    return store_with(tmp_path, *base_records())


def declaration_store(tmp_path):
    return store_with(tmp_path, *base_records(), constraint_registration())


def collection_for(record):
    members = list(base_records())
    if record.record_kind == "variable_constraint_declaration":
        members.append(constraint_registration())
    members.append(record)
    return {item.record_id: item for item in members}


def assert_append_rejects(tmp_path, record):
    store = (declaration_store(tmp_path) if record.record_kind
             == "variable_constraint_declaration"
             else registration_store(tmp_path))
    before = store.load().revision
    with pytest.raises(ModelKernelError) as error:
        store.append(record)
    assert error.value.error_code == "MODEL_RECORD_INVALID"
    assert store.load().revision == before


def assert_collection_rejects(record):
    with pytest.raises(ModelKernelError) as error:
        validate_record_collection(
            "demo-printer", collection_for(record), verify_hashes=False)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


class TestTopLevelRecordRevalidation:
    @pytest.mark.parametrize("factory,update", [
        (constraint_registration, {"variable_anchor_id": "var_NOT_HEX"}),
        (constraint_declaration, {"constraint_anchor_id": "con_NOT_HEX"}),
    ])
    def test_model_construct_forgery_rejected_by_append_and_collection(
            self, tmp_path, factory, update):
        valid = factory()
        forged = type(valid).model_construct(**{**valid.model_dump(), **update})
        assert_append_rejects(tmp_path, forged)
        assert_collection_rejects(forged)

    @pytest.mark.parametrize("factory,update", [
        (constraint_registration, {"variable_anchor_id": "var_NOT_HEX"}),
        (constraint_declaration, {"constraint_anchor_id": "con_NOT_HEX"}),
    ])
    def test_model_copy_forgery_rejected_by_append_and_collection(
            self, tmp_path, factory, update):
        forged = factory().model_copy(update=update)
        assert_append_rejects(tmp_path, forged)
        assert_collection_rejects(forged)


class TestNestedRevalidation:
    def test_forged_constraint_anchor_is_rejected_at_both_boundaries(
            self, tmp_path):
        valid = constraint_registration()
        bad_anchor = ConstraintAnchor.model_construct(
            anchor_id="con_NOT_HEX", namespace="bad namespace",
            display_name="", role_name=None)
        forged = valid.model_copy(update={"anchor": bad_anchor})
        assert_append_rejects(tmp_path, forged)
        assert_collection_rejects(forged)

    def test_forged_boundary_and_predicate_are_rejected_at_both_boundaries(
            self, tmp_path):
        valid = constraint_declaration()
        boundary = NumericBoundary.model_construct(
            value="80.0", inclusion="sometimes")
        predicate = ExactNumericUpperBound.model_construct(
            kind="upper_bound", upper=boundary)
        forged = valid.model_copy(update={"predicate": predicate})
        assert_append_rejects(tmp_path, forged)
        assert_collection_rejects(forged)

    @pytest.mark.parametrize("factory", [
        constraint_registration, constraint_declaration,
    ])
    def test_forged_nested_evidence_is_rejected_at_both_boundaries(
            self, tmp_path, factory):
        valid = factory()
        evidence = OwnerDeclarationEvidence.model_construct(
            kind="owner_declaration", statement="")
        forged = valid.model_copy(update={"evidence": (evidence,)})
        assert_append_rejects(tmp_path, forged)
        assert_collection_rejects(forged)


class TestHashBindingAfterModelCopy:
    @pytest.mark.parametrize("factory", [
        constraint_registration, constraint_declaration,
    ])
    def test_valid_shape_with_stale_id_is_a_typed_hash_failure(
            self, tmp_path, factory):
        original = factory()
        changed = original.model_copy(update={"note": "changed after hashing"})
        store = (declaration_store(tmp_path) if changed.record_kind
                 == "variable_constraint_declaration"
                 else registration_store(tmp_path))
        with pytest.raises(ModelKernelError) as error:
            store.append(changed)
        assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
        with pytest.raises(ModelKernelError) as error:
            validate_record_collection(
                "demo-printer", collection_for(changed), verify_hashes=True)
        assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def forged_revision(valid):
    return ModelRevision.model_construct(
        revision_id=valid.revision_id,
        record_ids=valid.record_ids,
        record_count=valid.record_count + 1,
        model_id=valid.model_id,
    )


class TestQueryResultRevisionRevalidation:
    def test_result_translates_surrogate_in_stale_registration_to_validation_error(
            self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        hostile = result.registration.model_copy(update={"note": "\ud800"})
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"registration"}),
                   "registration": hostile})

    def test_result_translates_surrogate_in_stale_declaration_to_validation_error(
            self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        hostile = result.declaration.model_copy(update={"note": "\ud800"})
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"declaration"}),
                   "declaration": hostile})

    def test_result_translates_surrogate_in_stale_conflict_tip_to_validation_error(
            self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        store = declaration_store(tmp_path)
        store.append(first)
        store.append(second)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        hostile = result.conflicting_declarations[0].model_copy(
            update={"note": "\ud800"})
        conflicts = (hostile, *result.conflicting_declarations[1:])
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"conflicting_declarations"}),
                   "conflicting_declarations": conflicts})

    def test_constraint_result_rejects_stale_id_registration_model_copy(
            self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        forged_registration = result.registration.model_copy(update={
            "note": "changed without recomputing record id"})
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"registration"}),
                   "registration": forged_registration})

    def test_constraint_result_rejects_stale_id_declaration_model_copy(
            self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        forged_declaration = result.declaration.model_copy(update={
            "note": "changed without recomputing record id"})
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"declaration"}),
                   "declaration": forged_declaration})

    def test_declared_tip_cannot_also_be_disclosed_as_superseded(self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"superseded_declaration_ids"}),
                   "superseded_declaration_ids": (declaration.record_id,)})

    def test_conflict_tips_cannot_also_be_disclosed_as_superseded(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        store = declaration_store(tmp_path)
        store.append(first)
        store.append(second)
        result = ModelQueries(store.load()).constraint_declaration(CON_A)
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"superseded_declaration_ids"}),
                   "superseded_declaration_ids": (first.record_id,)})

    def test_constraint_result_rejects_model_construct_revision(self, tmp_path):
        loaded = declaration_store(tmp_path)
        declaration = constraint_declaration()
        loaded.append(declaration)
        result = ModelQueries(loaded.load()).constraint_declaration(CON_A)
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                **{**result.model_dump(exclude={"revision"}),
                   "revision": forged_revision(result.revision)})

    def test_collection_result_rejects_model_copy_revision(self, tmp_path):
        loaded = declaration_store(tmp_path).load()
        result = ModelQueries(loaded).constraints_of_variable(VAR_A)
        bad = result.revision.model_copy(update={
            "record_count": result.revision.record_count + 1})
        with pytest.raises(ValidationError):
            VariableConstraintCollectionResult(
                **{**result.model_dump(exclude={"revision"}),
                   "revision": bad})

    def test_public_query_rejects_a_forged_loaded_revision(self, tmp_path):
        loaded = declaration_store(tmp_path).load()
        forged_loaded = replace(loaded, revision=forged_revision(loaded.revision))
        with pytest.raises(ValidationError):
            ModelQueries(forged_loaded).constraint_declaration(CON_A)

    def test_public_query_revalidates_forged_index_records(self, tmp_path):
        store = declaration_store(tmp_path)
        declaration = constraint_declaration()
        store.append(declaration)
        loaded = store.load()
        registration_record = loaded.constraint_registrations_by_anchor[CON_A]
        forged_registration = registration_record.model_copy(update={
            "variable_anchor_id": "var_NOT_HEX"})
        with pytest.raises(ValidationError):
            ModelQueries(replace(
                loaded,
                constraint_registrations_by_anchor={
                    CON_A: forged_registration},
            )).constraint_declaration(CON_A)

        forged_declaration = declaration.model_copy(update={
            "constraint_anchor_id": "con_NOT_HEX"})
        with pytest.raises(ValidationError):
            ModelQueries(replace(
                loaded,
                current_constraint_tips_by_anchor={
                    CON_A: (forged_declaration,)},
            )).constraint_declaration(CON_A)


class TestAcceptedDemoLedgerFreeze:
    def test_every_existing_demo_record_byte_and_id_remains_frozen(self):
        expected = {
            **FROZEN_MK001_RECORDS,
            **FROZEN_VM001_RECORD,
            **FROZEN_VS001_RECORD,
            **FROZEN_SN001_MODEL_RECORDS,
            **FROZEN_ES001_MODEL_RECORDS,
            **FROZEN_CN001_MODEL_RECORDS,
            **FROZEN_PT001_MODEL_RECORDS,
            **FROZEN_VP001_MODEL_RECORDS,
        }
        paths = sorted((DEMO_MODEL / "records").glob("*.json"))
        assert {path.name for path in paths} == set(expected)
        assert sum(path.name.startswith("crg_") for path in paths) == 1
        assert sum(path.name.startswith("vcn_") for path in paths) == 1
        for path in paths:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[path.name]
            payload = json.loads(path.read_text(encoding="utf-8"))
            assert path.name == f"{payload['record_id']}.json"

    def test_revision_and_authorities_remain_exactly_accepted(self):
        model = ModelStore(DEMO_MODEL).load()
        assert model.revision.revision_id == CURRENT_REVISION
        assert model.revision.record_count == 29
        assert len(model.constraint_registrations_by_anchor) == 1
        assert len(model.constraint_declarations) == 1
        expected_agents = {
            "mk001_demo_fixture": 11,
            "sn001_showcase_fixture": 3,
            "es001_demo_fixture": 2,
            "cn001_demo_fixture": 2,
            "pt001_demo_fixture": 10,
            "vp001_demo_fixture": 1,
        }
        actual = {}
        for record in model.records.values():
            assert record.authority.kind == "test_fixture"
            actual[record.authority.agent] = actual.get(record.authority.agent, 0) + 1
        assert actual == expected_agents
