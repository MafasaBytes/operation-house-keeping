"""BH-001 Slice A validating-store, lifecycle, withdrawal, and index tests."""

from datetime import timedelta

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    VAR_A,
    VAR_B,
    VAR_C,
    registration as entity_registration,
    specification,
    variable_registration,
)
from tests.model_kernel.bh001_slice_a_helpers import (
    AS_BUILT,
    AS_DESIGNED,
    BEHAVIOR_A,
    BEHAVIOR_B,
    REGISTRATION_DECLARATION,
    RULE_DECLARATION,
    T0,
    T1,
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
    semantic_lock,
    snapshot,
    variable_records,
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


def registration_citation(record_id):
    return kernel.ModelRecordEvidence(kind="model_record", record_id=record_id)


class TestBehaviorRegistrationAdmission:
    def test_all_pre_bh_validation_precedes_behavior_admission(self):
        behavior = behavior_registration()
        citations_only = tuple(
            reference for reference in behavior.evidence
            if reference.kind == "model_record")
        behavior = behavior_registration(evidence=citations_only)
        pre_bh_invalid = specification(variable_anchor_id=VAR_C)
        records = (*variable_records(), behavior, pre_bh_invalid)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "demo-printer",
                {record.record_id: record for record in records})
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_registration_requires_both_exact_variable_registrations(self,
                                                                     tmp_path):
        variables = variable_records()
        behavior = behavior_registration()
        for index, omitted in enumerate((VAR_A, VAR_B)):
            store = kernel.ModelStore(tmp_path / f"omitted-{index}")
            for record in variables:
                if (record.record_kind != "variable_registration"
                        or record.anchor.anchor_id != omitted):
                    store.append(record)
            assert_atomic_rejection(
                store, behavior, "MODEL_REFERENCE_INVALID")

    def test_registration_requires_variable_owner_entity_closure_on_collection(
            self):
        first = variable_registration(VAR_A, owner=ENT_A)
        second = variable_registration(VAR_B, owner=ENT_B)
        behavior = behavior_registration(owners=(ENT_A, ENT_B))
        records = {
            first.record_id: first,
            second.record_id: second,
            entity_registration(ENT_A).record_id: entity_registration(ENT_A),
            behavior.record_id: behavior,
        }
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("demo-printer", records)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_cross_owner_and_same_owner_pairs_are_both_explicitly_admitted(
            self, tmp_path):
        same = world(tmp_path / "same").load()
        cross = world(tmp_path / "cross", owners=(ENT_A, ENT_B)).load()
        assert same.behavior_registrations_by_anchor[BEHAVIOR_A].record_id
        assert cross.behavior_registrations_by_anchor[BEHAVIOR_A].record_id
        assert (same.behavior_registrations_by_anchor[BEHAVIOR_A]
                .participant_variable_anchor_ids) == (VAR_A, VAR_B)
        assert (cross.behavior_registrations_by_anchor[BEHAVIOR_A]
                .participant_variable_anchor_ids) == (VAR_A, VAR_B)

    def test_registration_requires_both_vrg_citations_and_owner_declaration(
            self, tmp_path):
        variables = {record.anchor.anchor_id: record
                     for record in variable_records()
                     if record.record_kind == "variable_registration"}
        complete = tuple(registration_citation(
            variables[var].record_id) for var in (VAR_A, VAR_B))
        attacks = (
            (REGISTRATION_DECLARATION,),
            (complete[0], REGISTRATION_DECLARATION),
            complete,
            (registration_citation(entity_registration(ENT_A).record_id),
             REGISTRATION_DECLARATION),
        )
        for index, evidence in enumerate(attacks):
            store = kernel.ModelStore(tmp_path / f"missing-{index}")
            for record in variable_records():
                store.append(record)
            assert_atomic_rejection(
                store, behavior_registration(evidence=evidence),
                "MODEL_BEHAVIOR_REGISTRATION_INVALID",
                "MODEL_REFERENCE_INVALID")

    def test_additional_model_record_evidence_must_close_on_append_and_replay(
            self, tmp_path):
        unknown = registration_citation("reg_" + "f" * 64)
        bad = behavior_registration(evidence=(
            *behavior_registration().evidence, unknown))
        store = kernel.ModelStore(tmp_path / "append")
        for record in variable_records():
            store.append(record)
        assert_atomic_rejection(store, bad, "MODEL_REFERENCE_INVALID")

        support = entity_registration(ENT_B)
        good = behavior_registration(evidence=(
            *behavior_registration().evidence,
            registration_citation(support.record_id)))
        complete = kernel.ModelStore(tmp_path / "replay")
        for record in (*variable_records(), support, good):
            complete.append(record)
        subset = tuple(record_id for record_id in
                       complete.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_behavior_anchor_registration_is_permanently_unique(self, tmp_path):
        store = world(tmp_path)
        duplicate = behavior_registration(note="alternate registration")
        assert_atomic_rejection(
            store, duplicate, "MODEL_DUPLICATE_REGISTRATION",
            "MODEL_BEHAVIOR_REGISTRATION_INVALID")


class TestDeclarationAdmission:
    def test_declaration_requires_exact_behavior_registration(self, tmp_path):
        registration = behavior_registration()
        declaration = behavior_declaration(registration)
        store = kernel.ModelStore(tmp_path / "missing")
        for record in variable_records():
            store.append(record)
        assert_atomic_rejection(store, declaration, "MODEL_REFERENCE_INVALID")

    def test_declaration_locks_must_equal_registered_variable_pair(self,
                                                                   tmp_path):
        registration = behavior_registration()
        attacks = (
            (semantic_lock(VAR_A), semantic_lock(VAR_C)),
            (semantic_lock(VAR_B), semantic_lock(VAR_C)),
        )
        store = world(tmp_path)
        for index, locks in enumerate(attacks):
            declaration = behavior_declaration(
                registration, locks=locks, note=f"attack-{index}")
            assert_atomic_rejection(
                store, declaration, "MODEL_BEHAVIOR_DECLARATION_INVALID")

    @pytest.mark.parametrize("dimension,left,right", [
        ("quantity", "temperature", "pressure"),
        ("unit", "degree_celsius", "kelvin"),
    ])
    def test_declaration_rejects_cross_participant_quantity_or_unit_mismatch(
            self, dimension, left, right):
        first_options = {dimension: left}
        second_options = {dimension: right}
        locks = (semantic_lock(VAR_A, **first_options),
                 semantic_lock(VAR_B, **second_options))
        with pytest.raises(kernel.ModelIntegrityError) as error:
            behavior_declaration(locks=locks)
        assert error.value.error_code == "MODEL_RECORD_INVALID"

    def test_different_observation_roles_are_valid_and_variable_keyed(
            self, tmp_path):
        registration = behavior_registration()
        declaration = behavior_declaration(registration, locks=(
            semantic_lock(VAR_A, role="measured"),
            semantic_lock(VAR_B, role="reported")))
        loaded = world(tmp_path, declaration).load()
        assert loaded.behavior_rule_declarations[declaration.record_id] == \
            declaration

    def test_declaration_requires_exact_brg_citation_and_owner_declaration(
            self, tmp_path):
        registration = behavior_registration()
        brg = registration_citation(registration.record_id)
        attacks = (
            (RULE_DECLARATION,),
            (brg,),
            (registration_citation("brg_" + "f" * 64), RULE_DECLARATION),
        )
        store = world(tmp_path)
        for index, evidence in enumerate(attacks):
            declaration = behavior_declaration(
                registration, evidence=evidence, note=f"attack-{index}")
            assert_atomic_rejection(
                store, declaration, "MODEL_BEHAVIOR_DECLARATION_INVALID",
                "MODEL_REFERENCE_INVALID")

    def test_contexts_are_independent_lineage_keys(self, tmp_path):
        registration = behavior_registration()
        designed = behavior_declaration(registration, context=AS_DESIGNED)
        built = behavior_declaration(registration, context=AS_BUILT)
        view_free_context = kernel.ViewIndependentContext(
            kind="view_independent")
        view_free = behavior_declaration(
            registration, context=view_free_context)
        loaded = world(tmp_path, designed, built, view_free).load()
        assert loaded.behavior_rule_ids_by_key[(BEHAVIOR_A, AS_DESIGNED)] == (
            designed.record_id,)
        assert loaded.behavior_rule_ids_by_key[(BEHAVIOR_A, AS_BUILT)] == (
            built.record_id,)
        assert loaded.behavior_rule_ids_by_key[
            (BEHAVIOR_A, view_free_context)] == (view_free.record_id,)


class TestBehaviorCorrectionDag:
    def test_chain_fork_partial_and_full_same_root_convergence(self, tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        left = behavior_declaration(
            registration, supersedes=(root.record_id,), note="left")
        right = behavior_declaration(
            registration, supersedes=(root.record_id,), note="right")
        partial = behavior_declaration(
            registration, supersedes=(left.record_id,), note="partial")
        partial_model = world(
            tmp_path / "partial", root, left, right, partial).load()
        assert partial_model.behavior_rule_root_by_id[partial.record_id] == \
            root.record_id
        assert partial_model.behavior_rule_ancestry_by_id[
            partial.record_id] == tuple(sorted((root.record_id, left.record_id)))
        assert tuple(record.record_id for record in
                     partial_model.current_behavior_rule_tips_by_root[
                         root.record_id]) == tuple(sorted(
                             (partial.record_id, right.record_id)))

        merged = behavior_declaration(
            registration, supersedes=(left.record_id, right.record_id),
            note="merged")
        full = world(tmp_path / "full", root, left, right, merged).load()
        assert tuple(record.record_id for record in
                     full.current_behavior_rule_tips_by_root[root.record_id]) == (
                         merged.record_id,)
        assert full.behavior_rule_ancestry_by_id[merged.record_id] == tuple(
            sorted((root.record_id, left.record_id, right.record_id)))

    def test_identical_body_same_root_fork_is_preserved_as_two_tips(self,
                                                                   tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        left = behavior_declaration(
            registration, supersedes=(root.record_id,), note="audit-left")
        right = behavior_declaration(
            registration, supersedes=(root.record_id,), note="audit-right")
        loaded = world(tmp_path, root, left, right).load()
        assert tuple(record.record_id for record in
                     loaded.current_behavior_rule_tips_by_root[root.record_id]
                     ) == tuple(sorted((left.record_id, right.record_id)))

    def test_independent_identical_and_different_body_roots_remain_separate(
            self, tmp_path):
        registration = behavior_registration()
        one = behavior_declaration(registration, note="authority one")
        two = behavior_declaration(
            registration, recorded_at=T1, note="authority two")
        different = behavior_declaration(registration, locks=(
            semantic_lock(VAR_A, role="estimated"),
            semantic_lock(VAR_B, role="reported")), note="different body")
        loaded = world(tmp_path, one, two, different).load()
        for root in (one, two, different):
            assert loaded.behavior_rule_root_by_id[root.record_id] == \
                root.record_id
            assert loaded.current_behavior_rule_tips_by_root[root.record_id] == (
                root,)

    def test_cross_root_convergence_is_rejected_atomically(self, tmp_path):
        registration = behavior_registration()
        one = behavior_declaration(registration, note="one")
        two = behavior_declaration(registration, note="two")
        store = world(tmp_path, one, two)
        cross = behavior_declaration(
            registration, supersedes=(one.record_id, two.record_id),
            note="cross-root")
        assert_atomic_rejection(
            store, cross, "MODEL_BEHAVIOR_LINEAGE_INVALID")

    def test_parent_must_match_behavior_anchor_and_exact_context(self,
                                                                 tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration)
        store = world(tmp_path, root)
        second_registration = behavior_registration(
            behavior_anchor_id=BEHAVIOR_B, note="second behavior")
        store.append(second_registration)
        attacks = (
            behavior_declaration(
                second_registration, behavior_anchor_id=BEHAVIOR_B,
                supersedes=(root.record_id,), note="anchor"),
            behavior_declaration(
                registration, context=AS_BUILT,
                supersedes=(root.record_id,), note="context"),
        )
        for attack in attacks:
            assert_atomic_rejection(
                store, attack, "MODEL_BEHAVIOR_LINEAGE_INVALID")

    def test_crafted_cycle_is_rejected_without_hash_verification(self):
        registration = behavior_registration()
        one = behavior_declaration(registration, note="one")
        two = behavior_declaration(registration, note="two")
        first_id = "bhd_" + "1" * 64
        second_id = "bhd_" + "2" * 64
        one = one.model_copy(update={
            "record_id": first_id, "supersedes": (second_id,)})
        two = two.model_copy(update={
            "record_id": second_id, "supersedes": (first_id,)})
        records = {record.record_id: record for record in (
            *variable_records(), registration, one, two)}
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "demo-printer", records, verify_hashes=False)
        assert error.value.error_code == "MODEL_BEHAVIOR_LINEAGE_INVALID"


class TestBehaviorWithdrawals:
    def test_selective_fork_tip_withdrawal_keeps_sibling_current(self, tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        left = behavior_declaration(
            registration, supersedes=(root.record_id,), note="left")
        right = behavior_declaration(
            registration, supersedes=(root.record_id,), note="right")
        event = behavior_withdrawal(left)
        loaded = world(tmp_path, root, left, right, event).load()
        assert loaded.behavior_rule_withdrawals[event.record_id] == event
        assert loaded.behavior_rule_withdrawn_by[left.record_id] == (
            event.record_id,)
        assert loaded.behavior_rule_withdrawals_by_target[left.record_id] == (
            event.record_id,)
        assert loaded.current_behavior_rule_tips_by_root[root.record_id] == (
            right,)

    def test_unknown_superseded_and_duplicate_withdrawals_are_rejected(
            self, tmp_path):
        unknown = kernel.build_record(
            kernel.BehaviorRuleWithdrawal,
            withdraws="bhd_" + "f" * 64, recorded_at=T1,
            authority=behavior_declaration().authority, note="unknown")
        empty = world(tmp_path / "unknown")
        assert_atomic_rejection(empty, unknown, "MODEL_REFERENCE_INVALID")

        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        child = behavior_declaration(
            registration, supersedes=(root.record_id,), note="child")
        superseded = world(tmp_path / "superseded", root, child)
        assert_atomic_rejection(
            superseded, behavior_withdrawal(root),
            "MODEL_BEHAVIOR_WITHDRAWAL_INVALID")

        event = behavior_withdrawal(root)
        withdrawn = world(tmp_path / "duplicate", root, event)
        assert_atomic_rejection(
            withdrawn, behavior_withdrawal(root, note="again"),
            "MODEL_BEHAVIOR_WITHDRAWAL_INVALID")
        assert_atomic_rejection(
            withdrawn, child, "MODEL_BEHAVIOR_WITHDRAWAL_INVALID")

    def test_replay_without_withdrawal_or_successor_revives_prior_tip(self,
                                                                     tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        child = behavior_declaration(
            registration, supersedes=(root.record_id,), note="child")
        event = behavior_withdrawal(child)
        store = world(tmp_path, root, child, event)
        no_event = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id != event.record_id))
        assert no_event.current_behavior_rule_tips_by_root[root.record_id] == (
            child,)
        no_child_or_event = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id not in (child.record_id, event.record_id)))
        assert no_child_or_event.current_behavior_rule_tips_by_root[
            root.record_id] == (root,)

    def test_withdrawing_every_active_fork_tip_leaves_inactive_root(self,
                                                                    tmp_path):
        registration = behavior_registration()
        root = behavior_declaration(registration, note="root")
        left = behavior_declaration(
            registration, supersedes=(root.record_id,), note="left")
        right = behavior_declaration(
            registration, supersedes=(root.record_id,), note="right")
        left_event = behavior_withdrawal(left, note="withdraw left")
        right_event = behavior_withdrawal(right, note="withdraw right")
        loaded = world(
            tmp_path, root, left, right, left_event, right_event).load()
        assert loaded.current_behavior_rule_tips_by_root[root.record_id] == ()
        assert loaded.behavior_rule_withdrawn_by[left.record_id] == (
            left_event.record_id,)
        assert loaded.behavior_rule_withdrawn_by[right.record_id] == (
            right_event.record_id,)

    def test_recorded_time_never_selects_a_tip_or_blocks_withdrawal(self,
                                                                   tmp_path):
        registration = behavior_registration()
        later_root = behavior_declaration(
            registration, recorded_at=T0 + timedelta(days=5), note="root")
        earlier_child = behavior_declaration(
            registration, supersedes=(later_root.record_id,),
            recorded_at=T0, note="child")
        earlier_event = behavior_withdrawal(
            earlier_child, recorded_at=T0 - timedelta(days=5))
        loaded = world(
            tmp_path, later_root, earlier_child, earlier_event).load()
        assert loaded.current_behavior_rule_tips_by_root[
            later_root.record_id] == ()


def test_all_behavior_indexes_are_complete_immutable_and_deterministic(tmp_path):
    registration = behavior_registration()
    root = behavior_declaration(registration, note="root")
    child = behavior_declaration(
        registration, supersedes=(root.record_id,), note="child")
    loaded = world(tmp_path, root, child).load()
    reloaded = kernel.ModelStore(tmp_path / "demo-printer").load()
    names = (
        "behavior_registrations",
        "behavior_registrations_by_anchor",
        "behavior_anchor_ids_by_variable",
        "behavior_rule_declarations",
        "behavior_rule_ids_by_key",
        "behavior_rule_root_by_id",
        "behavior_rule_ancestry_by_id",
        "behavior_rule_superseded_by",
        "current_behavior_rule_tips_by_root",
        "behavior_rule_withdrawals",
        "behavior_rule_withdrawn_by",
        "behavior_rule_withdrawals_by_target",
    )
    assert loaded.behavior_registrations[registration.record_id] == registration
    assert loaded.behavior_registrations_by_anchor[BEHAVIOR_A] == registration
    assert loaded.behavior_anchor_ids_by_variable[VAR_A] == (BEHAVIOR_A,)
    assert loaded.behavior_anchor_ids_by_variable[VAR_B] == (BEHAVIOR_A,)
    assert loaded.behavior_rule_ids_by_key[(BEHAVIOR_A, AS_DESIGNED)] == tuple(
        sorted((root.record_id, child.record_id)))
    assert loaded.behavior_rule_superseded_by[root.record_id] == (
        child.record_id,)
    assert loaded.behavior_rule_superseded_by[child.record_id] == ()
    assert loaded.behavior_rule_withdrawn_by[root.record_id] == ()
    assert loaded.behavior_rule_withdrawn_by[child.record_id] == ()
    assert loaded.behavior_rule_withdrawals_by_target == {}
    for name in names:
        mapping = getattr(loaded, name)
        assert tuple(mapping) == tuple(getattr(reloaded, name))
        with pytest.raises(TypeError):
            mapping[next(iter(mapping), "forged")] = ()
