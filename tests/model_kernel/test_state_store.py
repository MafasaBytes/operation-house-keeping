"""ST-001 Slice A validating store, lifecycle, withdrawal, and index tests."""

from datetime import timedelta

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import _state_effective_body_bytes
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    ENT_A,
    ENT_B,
    VAR_A,
    VAR_B,
    constraint_declaration,
    registration as entity_registration,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_DESIGNED,
    AS_OPERATED,
    REGISTRATION_DECLARATION,
    STATE_A,
    STATE_B,
    STATE_DECLARATION,
    T0,
    T1,
    condition_world_records,
    declaration_evidence,
    pins,
    snapshot,
    state_declaration,
    state_registration,
    state_withdrawal,
    world,
)


def assert_atomic_rejection(store, record, *codes):
    before = snapshot(store)
    revision = store.load().revision
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(record)
    assert error.value.error_code in codes
    assert snapshot(store) == before
    assert store.load().revision == revision


def citation(record_id):
    return kernel.ModelRecordEvidence(kind="model_record", record_id=record_id)


def complete_records(*extra):
    registration = state_registration()
    values = (*condition_world_records(), registration, *extra)
    return {record.record_id: record for record in values}


class TestStateRegistrationAdmission:
    def test_registration_builds_exact_immutable_owner_and_condition_indexes(
            self, tmp_path):
        registration = state_registration(constraints=(CON_B, CON_A))
        loaded = world(tmp_path).load()
        assert loaded.state_registrations[registration.record_id] == registration
        assert loaded.state_registrations_by_anchor[STATE_A] == registration
        assert loaded.state_anchor_ids_by_subject_entity[ENT_A] == (STATE_A,)
        assert loaded.state_condition_constraint_ids_by_anchor[STATE_A] == (
            CON_A, CON_B)
        for name in (
            "state_registrations", "state_registrations_by_anchor",
            "state_anchor_ids_by_subject_entity",
            "state_condition_constraint_ids_by_anchor",
        ):
            with pytest.raises(TypeError):
                getattr(loaded, name)["forged"] = ()

    def test_registration_requires_registered_subject(self):
        records = tuple(
            record for record in condition_world_records()
            if not (record.record_kind == "entity_registration"
                    and record.anchor.anchor_id == ENT_A))
        registration = state_registration()
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("demo-printer", {
                record.record_id: record for record in (*records, registration)})
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_registration_requires_every_constraint_and_variable_owner_closure(
            self):
        complete = condition_world_records()
        registration = state_registration()
        omissions = (
            lambda record: (record.record_kind == "constraint_registration"
                            and record.anchor.anchor_id == CON_B),
            lambda record: (record.record_kind == "variable_registration"
                            and record.anchor.anchor_id == VAR_B),
            lambda record: (record.record_kind == "entity_registration"
                            and record.anchor.anchor_id == ENT_A),
        )
        for omitted in omissions:
            records = tuple(record for record in complete if not omitted(record))
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("demo-printer", {
                    record.record_id: record
                    for record in (*records, registration)})
            assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_cross_entity_constraint_target_is_rejected_atomically(self,
                                                                    tmp_path):
        store = kernel.ModelStore(tmp_path / "demo-printer")
        records = condition_world_records(second_owner=ENT_B)
        for record in records:
            store.append(record)
        registration = state_registration(
            second_owner=ENT_B,
            evidence=(
                citation(next(record.record_id for record in records
                              if record.record_kind == "entity_registration"
                              and record.anchor.anchor_id == ENT_A)),
                *(citation(record.record_id) for record in records
                  if record.record_kind == "constraint_registration"),
                REGISTRATION_DECLARATION,
            ))
        assert_atomic_rejection(
            store, registration, "MODEL_STATE_REGISTRATION_INVALID")

    def test_same_state_anchor_cannot_be_registered_twice(self, tmp_path):
        store = world(tmp_path)
        for duplicate in (
            state_registration(),
            state_registration(note="divergent audit registration"),
        ):
            assert_atomic_rejection(
                store, duplicate, "MODEL_DUPLICATE_REGISTRATION")

    def test_registration_requires_exact_subject_and_crg_citations_and_claim(
            self, tmp_path):
        complete = state_registration()
        model_refs = tuple(ref for ref in complete.evidence
                           if ref.kind == "model_record")
        attacks = (
            (REGISTRATION_DECLARATION,),
            (*model_refs[:-1], REGISTRATION_DECLARATION),
            model_refs,
            (citation(entity_registration(ENT_B).record_id),
             REGISTRATION_DECLARATION),
        )
        for index, evidence in enumerate(attacks):
            store = kernel.ModelStore(tmp_path / f"missing-{index}")
            for record in condition_world_records():
                store.append(record)
            assert_atomic_rejection(
                store, state_registration(evidence=evidence),
                "MODEL_STATE_REGISTRATION_INVALID", "MODEL_REFERENCE_INVALID")

    def test_additional_model_evidence_must_close_on_append_and_replay(
            self, tmp_path):
        unknown = citation("reg_" + "f" * 64)
        bad = state_registration(evidence=(
            *state_registration().evidence, unknown))
        store = kernel.ModelStore(tmp_path / "append")
        for record in condition_world_records():
            store.append(record)
        assert_atomic_rejection(store, bad, "MODEL_REFERENCE_INVALID")

        support = entity_registration(ENT_B)
        good = state_registration(evidence=(
            *state_registration().evidence, citation(support.record_id)))
        complete = kernel.ModelStore(tmp_path / "replay")
        for record in (*condition_world_records(), support, good):
            complete.append(record)
        subset = tuple(record_id for record_id in
                       complete.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"


class TestStateDeclarationAdmission:
    def test_declaration_requires_registration_and_exact_pin_coverage(
            self, tmp_path):
        registration = state_registration()
        valid_pins = pins()
        no_registration = kernel.ModelStore(tmp_path / "no-registration")
        for record in condition_world_records():
            no_registration.append(record)
        assert_atomic_rejection(
            no_registration, state_declaration(registration),
            "MODEL_REFERENCE_INVALID")

        store = world(tmp_path / "coverage")
        extra_pin = kernel.StateConstraintDeclarationPin(
            constraint_anchor_id="con_" + "c" * 32,
            constraint_declaration_record_id="vcn_" + "c" * 64)
        substitution = valid_pins[0].model_copy(update={
            "constraint_declaration_record_id": valid_pins[1]
            .constraint_declaration_record_id})
        attacks = (
            valid_pins[:1],
            (*valid_pins, extra_pin),
            (substitution, valid_pins[1]),
        )
        for index, attack in enumerate(attacks):
            declaration = state_declaration(
                registration, condition_pins=attack,
                evidence=(citation(registration.record_id),
                          STATE_DECLARATION), note=f"attack-{index}")
            assert_atomic_rejection(
                store, declaration, "MODEL_STATE_DECLARATION_INVALID",
                "MODEL_REFERENCE_INVALID")

    def test_missing_or_cross_constraint_vcn_pin_rejects(self, tmp_path):
        registration = state_registration()
        valid_pins = pins()
        store = world(tmp_path)
        missing = valid_pins[0].model_copy(update={
            "constraint_declaration_record_id": "vcn_" + "f" * 64})
        cross = valid_pins[0].model_copy(update={
            "constraint_declaration_record_id": valid_pins[1]
            .constraint_declaration_record_id})
        for attack in (missing, cross):
            candidate = state_declaration(
                registration, condition_pins=(attack, valid_pins[1]),
                evidence=(citation(registration.record_id),
                          STATE_DECLARATION))
            assert_atomic_rejection(
                store, candidate, "MODEL_STATE_DECLARATION_INVALID",
                "MODEL_REFERENCE_INVALID")

    def test_declaration_requires_srg_crg_vcn_citations_and_claim_basis(
            self, tmp_path):
        registration = state_registration()
        complete = state_declaration(registration)
        model_refs = tuple(ref for ref in complete.evidence
                           if ref.kind == "model_record")
        attacks = (
            (STATE_DECLARATION,),
            (*model_refs[:-1], STATE_DECLARATION),
            model_refs,
            (citation(registration.record_id), STATE_DECLARATION),
        )
        store = world(tmp_path)
        for index, evidence in enumerate(attacks):
            assert_atomic_rejection(
                store, state_declaration(
                    registration, evidence=evidence, note=f"attack-{index}"),
                "MODEL_STATE_DECLARATION_INVALID",
                "MODEL_REFERENCE_INVALID")

    def test_exact_contexts_are_independent_lineage_keys(self, tmp_path):
        registration = state_registration()
        operated = state_declaration(registration, context=AS_OPERATED)
        designed = state_declaration(registration, context=AS_DESIGNED)
        loaded = world(tmp_path, operated, designed).load()
        assert loaded.state_declaration_ids_by_key[(STATE_A, AS_OPERATED)] == (
            operated.record_id,)
        assert loaded.state_declaration_ids_by_key[(STATE_A, AS_DESIGNED)] == (
            designed.record_id,)


class TestStateCorrectionDag:
    def test_chain_fork_partial_and_full_same_root_convergence(self, tmp_path):
        registration = state_registration()
        root = state_declaration(registration, note="root")
        left = state_declaration(
            registration, supersedes=(root.record_id,), note="left")
        right = state_declaration(
            registration, supersedes=(root.record_id,), note="right")
        partial = state_declaration(
            registration, supersedes=(left.record_id,), note="partial")
        partial_model = world(
            tmp_path / "partial", root, left, right, partial).load()
        assert partial_model.state_declaration_root_by_id[partial.record_id] == \
            root.record_id
        assert partial_model.state_declaration_ancestry_by_id[
            partial.record_id] == tuple(sorted((root.record_id, left.record_id)))
        assert tuple(record.record_id for record in
                     partial_model.current_state_declaration_tips_by_root[
                         root.record_id]) == tuple(sorted(
                             (partial.record_id, right.record_id)))

        merged = state_declaration(
            registration, supersedes=(left.record_id, right.record_id),
            note="merged")
        full = world(tmp_path / "full", root, left, right, merged).load()
        assert full.current_state_declaration_tips_by_root[root.record_id] == (
            merged,)

    def test_independent_identical_and_different_effective_bodies_stay_roots(
            self, tmp_path):
        registration = state_registration()
        one = state_declaration(registration, note="authority one")
        two = state_declaration(
            registration, recorded_at=T1, note="authority two")
        base_declarations = {
            pin.constraint_anchor_id: next(
                record for record in condition_world_records()
                if record.record_kind == "variable_constraint_declaration"
                and record.record_id == pin.constraint_declaration_record_id)
            for pin in one.conditions
        }
        correction = constraint_declaration(
            CON_A, predicate=upper_bound("90"),
            supersedes=(base_declarations[CON_A].record_id,),
            recorded_at=T1)
        changed_pins = tuple(
            pin.model_copy(update={
                "constraint_declaration_record_id": correction.record_id})
            if pin.constraint_anchor_id == CON_A else pin
            for pin in one.conditions)
        different = state_declaration(
            registration, condition_pins=changed_pins,
            evidence=declaration_evidence(registration, changed_pins),
            note="different body")
        loaded = world(tmp_path, correction, one, two, different).load()
        assert _state_effective_body_bytes(one) == _state_effective_body_bytes(two)
        assert _state_effective_body_bytes(one) != \
            _state_effective_body_bytes(different)
        for root in (one, two, different):
            assert loaded.state_declaration_root_by_id[root.record_id] == \
                root.record_id
            assert loaded.current_state_declaration_tips_by_root[
                root.record_id] == (root,)

    def test_cross_root_convergence_rejects_atomically(self, tmp_path):
        registration = state_registration()
        one = state_declaration(registration, note="one")
        two = state_declaration(registration, note="two")
        store = world(tmp_path, one, two)
        cross = state_declaration(
            registration, supersedes=(one.record_id, two.record_id),
            note="cross-root")
        assert_atomic_rejection(
            store, cross, "MODEL_STATE_LINEAGE_INVALID")

    def test_parent_must_match_state_anchor_and_exact_context(self, tmp_path):
        registration = state_registration()
        root = state_declaration(registration)
        store = world(tmp_path, root)
        second_registration = state_registration(
            state_anchor_id=STATE_B, note="second state")
        store.append(second_registration)
        attacks = (
            state_declaration(
                second_registration, state_anchor_id=STATE_B,
                supersedes=(root.record_id,), note="state"),
            state_declaration(
                registration, context=AS_DESIGNED,
                supersedes=(root.record_id,), note="context"),
        )
        for attack in attacks:
            assert_atomic_rejection(
                store, attack, "MODEL_STATE_LINEAGE_INVALID")

    def test_crafted_cycle_rejects_without_hash_verification(self):
        registration = state_registration()
        one = state_declaration(registration, note="one")
        two = state_declaration(registration, note="two")
        first_id = "std_" + "1" * 64
        second_id = "std_" + "2" * 64
        one = one.model_copy(update={
            "record_id": first_id, "supersedes": (second_id,)})
        two = two.model_copy(update={
            "record_id": second_id, "supersedes": (first_id,)})
        records = complete_records(one, two)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "demo-printer", records, verify_hashes=False)
        assert error.value.error_code == "MODEL_STATE_LINEAGE_INVALID"

    def test_deep_dag_uses_iterative_traversal_without_python_recursion(self):
        registration = state_registration()
        chain = []
        parent = None
        for index in range(1100):
            item = state_declaration(
                registration,
                supersedes=(() if parent is None else (parent.record_id,)),
                note=f"depth-{index}")
            chain.append(item)
            parent = item
        loaded = validate_record_collection(
            "demo-printer", complete_records(*chain))
        assert loaded.current_state_declaration_tips_by_root[
            chain[0].record_id] == (chain[-1],)


class TestStateWithdrawals:
    def test_selective_and_complete_tip_withdrawal(self, tmp_path):
        registration = state_registration()
        root = state_declaration(registration, note="root")
        left = state_declaration(
            registration, supersedes=(root.record_id,), note="left")
        right = state_declaration(
            registration, supersedes=(root.record_id,), note="right")
        left_event = state_withdrawal(left)
        selective = world(
            tmp_path / "selective", root, left, right, left_event).load()
        assert selective.state_declaration_withdrawn_by[left.record_id] == (
            left_event.record_id,)
        assert selective.current_state_declaration_tips_by_root[
            root.record_id] == (right,)

        right_event = state_withdrawal(right, note="right")
        inactive = world(
            tmp_path / "inactive", root, left, right,
            left_event, right_event).load()
        assert inactive.current_state_declaration_tips_by_root[
            root.record_id] == ()

    def test_unknown_superseded_duplicate_and_successor_race_reject(self,
                                                                    tmp_path):
        unknown = kernel.build_record(
            kernel.StateDeclarationWithdrawal,
            withdraws="std_" + "f" * 64, recorded_at=T1,
            authority=state_declaration().authority, note="unknown")
        assert_atomic_rejection(
            world(tmp_path / "unknown"), unknown, "MODEL_REFERENCE_INVALID")

        registration = state_registration()
        root = state_declaration(registration, note="root")
        child = state_declaration(
            registration, supersedes=(root.record_id,), note="child")
        assert_atomic_rejection(
            world(tmp_path / "superseded", root, child),
            state_withdrawal(root), "MODEL_STATE_WITHDRAWAL_INVALID")

        event = state_withdrawal(root)
        withdrawn = world(tmp_path / "duplicate", root, event)
        assert_atomic_rejection(
            withdrawn, state_withdrawal(root, note="again"),
            "MODEL_STATE_WITHDRAWAL_INVALID")
        assert_atomic_rejection(
            withdrawn, child, "MODEL_STATE_WITHDRAWAL_INVALID")

    def test_replay_without_successor_or_withdrawal_revives_tip(self, tmp_path):
        registration = state_registration()
        root = state_declaration(registration, note="root")
        child = state_declaration(
            registration, supersedes=(root.record_id,), note="child")
        event = state_withdrawal(child)
        store = world(tmp_path, root, child, event)
        no_event = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id != event.record_id))
        assert no_event.current_state_declaration_tips_by_root[
            root.record_id] == (child,)
        root_only = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id not in (child.record_id, event.record_id)))
        assert root_only.current_state_declaration_tips_by_root[
            root.record_id] == (root,)


def test_indexes_are_deterministic_under_reversed_collection_input():
    registration = state_registration()
    root = state_declaration(registration, note="root")
    left = state_declaration(
        registration, supersedes=(root.record_id,), note="left")
    right = state_declaration(
        registration, supersedes=(root.record_id,), note="right")
    values = tuple(complete_records(root, left, right).values())
    forward = validate_record_collection(
        "demo-printer", {record.record_id: record for record in values})
    reverse = validate_record_collection(
        "demo-printer", {record.record_id: record
                         for record in reversed(values)})
    names = (
        "state_declaration_ids_by_key", "state_declaration_parent_ids",
        "state_declaration_successor_ids", "state_declaration_root_by_id",
        "state_declaration_ancestry_by_id",
        "current_state_declaration_tips_by_root",
    )
    assert forward.revision == reverse.revision
    for name in names:
        assert dict(getattr(forward, name)) == dict(getattr(reverse, name))
