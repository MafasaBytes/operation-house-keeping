"""CN-001 Slice A constraint discovery query contracts (Group E)."""

from dataclasses import replace

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    ConstraintDeclarationResult,
    ModelQueries,
    ModelQueryError,
    ModelRevision,
    VariableConstraintCollectionResult,
)
from backend.model_kernel.canonical import compute_revision_id
from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    ENT_A,
    VAR_A,
    VAR_B,
    constraint_declaration,
    constraint_registration,
    registration,
    store_with,
    variable_registration,
)


UNKNOWN_CONSTRAINT = "con_" + "9" * 32
UNKNOWN_VARIABLE = "var_" + "9" * 32


def world(tmp_path, *records, second_variable=False):
    base = [registration(ENT_A), variable_registration(VAR_A, owner=ENT_A)]
    if second_variable:
        base.append(variable_registration(VAR_B, owner=ENT_A))
    return store_with(tmp_path, *base, *records)


def empty_revision():
    return ModelRevision(
        revision_id=compute_revision_id("demo-printer", ()),
        record_ids=(), record_count=0, model_id="demo-printer")


class ExplodingMapping(dict):
    """Proves malformed ids are rejected before any index access."""

    def get(self, *args, **kwargs):
        raise AssertionError("query touched an index before validating the id")

    def __contains__(self, key):
        raise AssertionError("query touched an index before validating the id")


class TestExactConstraintDeclaration:
    def test_valid_unknown_constraint_is_structured_not_registered(self,
                                                                   tmp_path):
        result = ModelQueries(world(tmp_path).load()).constraint_declaration(
            UNKNOWN_CONSTRAINT)
        assert result == ConstraintDeclarationResult(
            constraint_anchor_id=UNKNOWN_CONSTRAINT,
            registration=None, status="not_registered", declaration=None,
            conflicting_declarations=(), superseded_declaration_ids=(),
            revision=result.revision)

    def test_registered_without_declaration_is_structured_not_declared(
            self, tmp_path):
        loaded = world(tmp_path, constraint_registration()).load()
        result = ModelQueries(loaded).constraint_declaration(CON_A)
        assert result.status == "not_declared"
        assert result.registration == loaded.constraint_registrations_by_anchor[
            CON_A]
        assert result.declaration is None
        assert result.conflicting_declarations == ()
        assert result.superseded_declaration_ids == ()
        assert result.revision == loaded.revision

    def test_one_tip_is_declared_and_carries_complete_revision(self, tmp_path):
        declaration = constraint_declaration()
        loaded = world(
            tmp_path, constraint_registration(), declaration).load()
        result = ModelQueries(loaded).constraint_declaration(CON_A)
        assert result.status == "declared"
        assert result.declaration == declaration
        assert result.conflicting_declarations == ()
        assert result.revision is loaded.revision
        assert result.revision.record_ids == tuple(sorted(loaded.records))
        assert result.revision.record_count == len(loaded.records)
        assert result.registration.record_id in result.revision.record_ids
        assert result.declaration.record_id in result.revision.record_ids

    def test_competing_tips_are_conflicted_in_record_id_order(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        result = ModelQueries(world(
            tmp_path, constraint_registration(), second, first
        ).load()).constraint_declaration(CON_A)
        assert result.status == "conflicted"
        assert result.declaration is None
        assert result.conflicting_declarations == tuple(
            sorted((first, second), key=lambda item: item.record_id))

    def test_superseded_history_is_disclosed_after_convergence(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        merged = constraint_declaration(
            supersedes=(second.record_id, first.record_id), note="merged")
        result = ModelQueries(world(
            tmp_path, constraint_registration(), first, second, merged
        ).load()).constraint_declaration(CON_A)
        assert result.status == "declared"
        assert result.declaration == merged
        assert result.superseded_declaration_ids == tuple(sorted(
            (first.record_id, second.record_id)))
        assert set(result.superseded_declaration_ids) <= set(
            result.revision.record_ids)

    @pytest.mark.parametrize("bad", [
        "con-" + "a" * 32, "con_" + "A" * 32, "con_" + "a" * 31,
        "var_" + "a" * 32, None, [],
    ])
    def test_malformed_constraint_id_fails_before_lookup(self, tmp_path, bad):
        loaded = replace(
            world(tmp_path).load(),
            constraint_registrations_by_anchor=ExplodingMapping())
        with pytest.raises(ModelQueryError) as error:
            ModelQueries(loaded).constraint_declaration(bad)
        assert error.value.error_code == "MODEL_ANCHOR_ID_INVALID"


class TestConstraintsOfVariable:
    def test_unregistered_variable_is_distinct_from_registered_empty(
            self, tmp_path):
        queries = ModelQueries(world(tmp_path).load())
        absent = queries.constraints_of_variable(UNKNOWN_VARIABLE)
        present = queries.constraints_of_variable(VAR_A)
        assert absent.status == "not_registered"
        assert absent.constraints == ()
        assert present.status == "registered"
        assert present.constraints == ()
        assert absent.revision == present.revision

    def test_constraints_are_ordered_by_constraint_anchor_id(self, tmp_path):
        loaded = world(
            tmp_path,
            constraint_registration(CON_B, VAR_A),
            constraint_declaration(CON_B),
            constraint_registration(CON_A, VAR_A),
            constraint_declaration(CON_A),
        ).load()
        result = ModelQueries(loaded).constraints_of_variable(VAR_A)
        assert result.status == "registered"
        assert tuple(item.constraint_anchor_id for item in result.constraints) == (
            CON_A, CON_B)
        assert all(item.revision == result.revision
                   for item in result.constraints)
        assert result.revision == loaded.revision

    @pytest.mark.parametrize("bad", [
        "var-" + "a" * 32, "var_" + "A" * 32, "var_" + "a" * 31,
        "con_" + "a" * 32, None, {},
    ])
    def test_malformed_variable_id_fails_before_lookup(self, tmp_path, bad):
        loaded = replace(
            world(tmp_path).load(),
            variable_registrations_by_anchor=ExplodingMapping())
        with pytest.raises(ModelQueryError) as error:
            ModelQueries(loaded).constraints_of_variable(bad)
        assert error.value.error_code == "MODEL_ANCHOR_ID_INVALID"


class TestResultContractHardening:
    def test_constraint_result_rejects_carried_ids_absent_from_revision(self):
        registration_record = constraint_registration()
        declaration = constraint_declaration()
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                constraint_anchor_id=CON_A,
                registration=registration_record, status="declared",
                declaration=declaration, revision=empty_revision())

    def test_constraint_result_rejects_wrong_anchor_and_impossible_statuses(self,
                                                                            tmp_path):
        loaded = world(tmp_path, constraint_registration()).load()
        registration_record = loaded.constraint_registrations_by_anchor[CON_A]
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                constraint_anchor_id=CON_B,
                registration=registration_record, status="not_declared",
                revision=loaded.revision)
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                constraint_anchor_id=CON_A,
                registration=registration_record, status="declared",
                declaration=None, revision=loaded.revision)
        with pytest.raises(ValidationError):
            ConstraintDeclarationResult(
                constraint_anchor_id=CON_A,
                registration=None, status="not_registered",
                superseded_declaration_ids=("vcn_" + "f" * 64,),
                revision=loaded.revision)

    def test_collection_rejects_reordering_revision_mismatch_and_wrong_target(
            self, tmp_path):
        loaded = world(
            tmp_path,
            constraint_registration(CON_B, VAR_A),
            constraint_declaration(CON_B),
            constraint_registration(CON_A, VAR_A),
            constraint_declaration(CON_A),
        ).load()
        queries = ModelQueries(loaded)
        first = queries.constraint_declaration(CON_A)
        second = queries.constraint_declaration(CON_B)
        with pytest.raises(ValidationError):
            VariableConstraintCollectionResult(
                variable_anchor_id=VAR_A, status="registered",
                constraints=(second, first), revision=loaded.revision)
        forged = first.model_copy(update={"revision": empty_revision()})
        with pytest.raises(ValidationError):
            VariableConstraintCollectionResult(
                variable_anchor_id=VAR_A, status="registered",
                constraints=(forged,), revision=loaded.revision)
        with pytest.raises(ValidationError):
            VariableConstraintCollectionResult(
                variable_anchor_id=VAR_B, status="registered",
                constraints=(first,), revision=loaded.revision)

    def test_not_registered_collection_carries_no_constraints(self, tmp_path):
        loaded = world(
            tmp_path, constraint_registration(), constraint_declaration()
        ).load()
        entry = ModelQueries(loaded).constraint_declaration(CON_A)
        with pytest.raises(ValidationError):
            VariableConstraintCollectionResult(
                variable_anchor_id=UNKNOWN_VARIABLE,
                status="not_registered", constraints=(entry,),
                revision=loaded.revision)
