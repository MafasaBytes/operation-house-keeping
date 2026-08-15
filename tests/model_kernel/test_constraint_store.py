"""CN-001 Slice A store acceptance: registration closure and vcn DAGs."""

import json

import pytest

from backend.model_kernel import ModelKernelError, ModelRecordEvidence, ModelStore
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.contracts import VariableConstraintDeclaration
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    ENT_A,
    VAR_A,
    VAR_B,
    constraint_declaration,
    constraint_registration,
    constraint_signature,
    quantity_kind,
    registration,
    store_with,
    upper_bound,
    variable_registration,
)


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def base_records(*, second_variable=False):
    records = [registration(ENT_A), variable_registration(VAR_A, owner=ENT_A)]
    if second_variable:
        records.append(variable_registration(VAR_B, owner=ENT_A))
    return records


def world(tmp_path, *extra, constraint=CON_A, variable=VAR_A):
    return store_with(
        tmp_path, *base_records(second_variable=variable == VAR_B),
        constraint_registration(constraint, variable), *extra)


def tips(loaded, anchor=CON_A):
    return loaded.current_constraint_tips_by_anchor.get(anchor, ())


def cited(record_id):
    return (ModelRecordEvidence(kind="model_record", record_id=record_id),)


def write_crafted(store, record):
    payload = {**canonical_payload(record), "record_id": record.record_id}
    (store.records_dir / f"{record.record_id}.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


class TestConstraintRegistrationClosure:
    def test_constraint_anchor_registration_is_unique(self, tmp_path):
        store = world(tmp_path)
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as error:
            store.append(constraint_registration(CON_A, VAR_A, note="duplicate"))
        assert error.value.error_code == "MODEL_DUPLICATE_REGISTRATION"
        assert snapshot(store) == before

    def test_duplicate_registration_is_rejected_on_crafted_load_and_replay(
            self, tmp_path):
        store = world(tmp_path)
        duplicate = constraint_registration(CON_A, VAR_A, note="duplicate")
        write_crafted(store, duplicate)
        with pytest.raises(ModelKernelError) as error:
            store.load()
        assert error.value.error_code == "MODEL_DUPLICATE_REGISTRATION"
        with pytest.raises(ModelKernelError) as error:
            store.replay(tuple(path.stem for path in store.records_dir.iterdir()))
        assert error.value.error_code == "MODEL_DUPLICATE_REGISTRATION"

    def test_registration_requires_its_target_variable_at_append(self, tmp_path):
        store = store_with(tmp_path, registration(ENT_A))
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as error:
            store.append(constraint_registration())
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"
        assert snapshot(store) == before

    def test_registration_target_closure_is_enforced_on_load_and_replay(self, tmp_path):
        crg = constraint_registration()
        store = store_with(tmp_path, *base_records(), crg)
        variable_path = store.records_dir / f"{variable_registration().record_id}.json"
        variable_path.unlink()
        with pytest.raises(ModelKernelError) as error:
            store.load()
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        complete = store_with(tmp_path / "replay", *base_records(), crg)
        with pytest.raises(ModelKernelError) as error:
            complete.replay((registration(ENT_A).record_id, crg.record_id))
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_registration_model_evidence_closes_append_load_and_replay(self, tmp_path):
        missing = "reg_" + "f" * 64
        bad = constraint_registration(evidence=cited(missing))
        store = store_with(tmp_path / "append", *base_records())
        with pytest.raises(ModelKernelError) as error:
            store.append(bad)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        crafted = store_with(tmp_path / "load", *base_records())
        write_crafted(crafted, bad)
        with pytest.raises(ModelKernelError) as error:
            crafted.load()
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        support = registration("ent_" + "b" * 32)
        good = constraint_registration(evidence=cited(support.record_id))
        complete = store_with(tmp_path / "replay", *base_records(), support, good)
        full = complete.load()
        assert complete.replay(full.revision.record_ids).revision == full.revision
        subset = tuple(record_id for record_id in complete.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(ModelKernelError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"


class TestDeclarationReferenceAndLineage:
    def test_declaration_requires_constraint_registration(self, tmp_path):
        store = store_with(tmp_path, *base_records())
        with pytest.raises(ModelKernelError) as error:
            store.append(constraint_declaration())
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_declaration_registration_closure_is_enforced_on_load_and_replay(
            self, tmp_path):
        declaration = constraint_declaration()
        crafted = store_with(tmp_path / "load", *base_records())
        write_crafted(crafted, declaration)
        with pytest.raises(ModelKernelError) as error:
            crafted.load()
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        complete = world(tmp_path / "replay", declaration)
        subset = tuple(
            record_id for record_id in complete.load().revision.record_ids
            if record_id != constraint_registration().record_id)
        with pytest.raises(ModelKernelError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_missing_parent_is_rejected(self, tmp_path):
        orphan = constraint_declaration(
            supersedes=("vcn_" + "f" * 64,), note="orphan")
        with pytest.raises(ModelKernelError) as error:
            world(tmp_path, orphan)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_cross_constraint_parent_is_rejected(self, tmp_path):
        first = constraint_declaration(CON_A)
        alien = constraint_declaration(
            CON_B, supersedes=(first.record_id,), note="alien")
        store = store_with(
            tmp_path, *base_records(),
            constraint_registration(CON_A, VAR_A),
            constraint_registration(CON_B, VAR_A), first)
        with pytest.raises(ModelKernelError) as error:
            store.append(alien)
        assert error.value.error_code == "MODEL_CONSTRAINT_LINEAGE_INVALID"

    def test_crafted_cycle_is_rejected(self):
        first = constraint_declaration(note="first")
        second = constraint_declaration(
            supersedes=(first.record_id,), note="second")
        cyclic_first = VariableConstraintDeclaration.model_construct(
            **{**first.model_dump(), "supersedes": (second.record_id,)})
        records = {
            record.record_id: record for record in (
                *base_records(), constraint_registration(), second)
        }
        records[first.record_id] = cyclic_first
        with pytest.raises(ModelKernelError) as error:
            validate_record_collection("demo-printer", records,
                                       verify_hashes=False)
        assert error.value.error_code == "MODEL_CONSTRAINT_LINEAGE_INVALID"
        assert "cycle" in str(error.value)

    def test_corrections_may_change_tokens_and_predicate_shape(self, tmp_path):
        first = constraint_declaration(predicate=upper_bound("80"))
        changed_signature = constraint_signature().model_copy(update={
            "quantity_kind": quantity_kind("pressure")})
        from backend.model_kernel import ExactNumericLowerBound, NumericBoundary
        second = constraint_declaration(
            expected_semantics=changed_signature,
            predicate=ExactNumericLowerBound(lower=NumericBoundary(
                value="10", inclusion="exclusive")),
            supersedes=(first.record_id,), note="corrected claim")
        loaded = world(tmp_path, first, second).load()
        assert tips(loaded) == (second,)


class TestDeclarationTipsAndConvergence:
    def test_one_root_is_current_and_indexes_history(self, tmp_path):
        root = constraint_declaration()
        loaded = world(tmp_path, root).load()
        assert tips(loaded) == (root,)
        assert loaded.constraint_declarations == {root.record_id: root}
        assert loaded.constraint_superseded_by == {root.record_id: ()}

    def test_competing_roots_are_canonically_ordered_tips(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        loaded = world(tmp_path, second, first).load()
        assert tips(loaded) == tuple(sorted((first, second),
                                           key=lambda item: item.record_id))

    def test_partial_then_full_convergence(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        partial = constraint_declaration(
            supersedes=(first.record_id,), note="partial")
        partially = world(tmp_path / "partial", first, second, partial).load()
        assert {item.record_id for item in tips(partially)} == {
            second.record_id, partial.record_id}

        merged = constraint_declaration(
            supersedes=(first.record_id, second.record_id), note="merged")
        fully = world(tmp_path / "full", first, second, merged).load()
        assert tips(fully) == (merged,)
        assert fully.constraint_superseded_by[first.record_id] == (
            merged.record_id,)

    def test_repeated_convergence_can_be_converged_again(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        merge_a = constraint_declaration(
            supersedes=(first.record_id, second.record_id), note="merge-a")
        merge_b = constraint_declaration(
            supersedes=(first.record_id, second.record_id), note="merge-b")
        store = world(tmp_path, first, second, merge_a, merge_b)
        assert {item.record_id for item in tips(store.load())} == {
            merge_a.record_id, merge_b.record_id}
        final = constraint_declaration(
            supersedes=(merge_a.record_id, merge_b.record_id), note="final")
        store.append(final)
        assert tips(store.load()) == (final,)

    def test_replay_before_conflict_and_after_convergence(self, tmp_path):
        first = constraint_declaration(note="first")
        second = constraint_declaration(note="second")
        merged = constraint_declaration(
            supersedes=(first.record_id, second.record_id), note="merged")
        store = world(tmp_path, first, second, merged)
        base = [record.record_id for record in
                (*base_records(), constraint_registration())]
        assert tips(store.replay((*base, first.record_id))) == (first,)
        assert len(tips(store.replay((*base, first.record_id,
                                      second.record_id)))) == 2
        assert tips(store.replay((*base, first.record_id, second.record_id,
                                  merged.record_id))) == (merged,)


class TestDeclarationEvidenceAndIndexes:
    def test_declaration_model_evidence_closes_append_load_and_replay(self, tmp_path):
        missing = "reg_" + "e" * 64
        bad = constraint_declaration(evidence=cited(missing))
        store = world(tmp_path / "append")
        with pytest.raises(ModelKernelError) as error:
            store.append(bad)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        crafted = world(tmp_path / "load")
        write_crafted(crafted, bad)
        with pytest.raises(ModelKernelError) as error:
            crafted.load()
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        support = registration("ent_" + "b" * 32)
        good = constraint_declaration(evidence=cited(support.record_id))
        complete = world(tmp_path / "replay", support, good)
        full = complete.load()
        assert complete.replay(full.revision.record_ids).revision == full.revision
        subset = tuple(record_id for record_id in complete.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(ModelKernelError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_all_constraint_indexes_are_immutable_and_variable_ordered(self, tmp_path):
        first = constraint_declaration(CON_A)
        second = constraint_declaration(CON_B)
        loaded = store_with(
            tmp_path, *base_records(),
            constraint_registration(CON_B, VAR_A),
            constraint_registration(CON_A, VAR_A), first, second).load()
        assert loaded.constraint_anchor_ids_by_variable[VAR_A] == tuple(
            sorted((CON_A, CON_B)))
        indexes = (
            loaded.constraint_registrations_by_anchor,
            loaded.constraint_anchor_ids_by_variable,
            loaded.constraint_declarations,
            loaded.current_constraint_tips_by_anchor,
            loaded.constraint_superseded_by,
        )
        for index in indexes:
            with pytest.raises(TypeError):
                index["forged"] = None

    def test_validated_indexes_are_copied_from_the_input_collection(self):
        declaration = constraint_declaration()
        members = {
            record.record_id: record for record in (
                *base_records(), constraint_registration(), declaration)
        }
        loaded = validate_record_collection("demo-printer", members)
        members.clear()
        assert loaded.constraint_registrations_by_anchor[CON_A].anchor.anchor_id == CON_A
        assert loaded.current_constraint_tips_by_anchor[CON_A] == (declaration,)
        assert loaded.revision.record_count == 4
