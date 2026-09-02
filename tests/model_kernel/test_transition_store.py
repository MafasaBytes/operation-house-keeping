"""ST-002 Slice A validating transition store, lifecycle, and replay tests."""

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    CON_A, CON_B, ENT_A, ENT_B, ENT_C,
    assertion, contains_type,
)
from tests.model_kernel.st001_slice_a_helpers import (
    condition_world_records,
    state_declaration,
    state_registration,
    state_withdrawal,
)
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    STATE_B,
    TRANSITION_A,
    TRANSITION_B,
    TRANSITION_DECLARATION_CLAIM,
    TRANSITION_REGISTRATION_CLAIM,
    VIEW_INDEPENDENT,
    citation,
    declaration_evidence,
    endpoint,
    registration_evidence,
    snapshot,
    transition_declaration,
    transition_fixture,
    transition_registration,
    transition_withdrawal,
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


def complete_records(*claims, context=AS_OPERATED):
    records, registration, *_ = transition_fixture(context=context)
    values = (*records, registration, *claims)
    return {record.record_id: record for record in values}


class TestTransitionRegistrationAdmission:
    def test_registration_builds_exact_immutable_indexes(self, tmp_path):
        store, registration, *_ = world(tmp_path)
        loaded = store.load()
        key = (registration.subject_entity_anchor_id,
               registration.from_state_anchor_id,
               registration.to_state_anchor_id)
        assert loaded.transition_registrations == {
            registration.record_id: registration}
        assert loaded.transition_registrations_by_anchor[TRANSITION_A] == \
            registration
        assert loaded.transition_anchor_ids_by_subject_entity[ENT_A] == (
            TRANSITION_A,)
        assert loaded.transition_registration_id_by_ordered_subject_endpoints[
            key] == registration.record_id
        for name in (
            "transition_registrations", "transition_registrations_by_anchor",
            "transition_anchor_ids_by_subject_entity",
            "transition_registration_id_by_ordered_subject_endpoints",
        ):
            with pytest.raises(TypeError):
                getattr(loaded, name)["forged"] = ()

    def test_duplicate_anchor_tuple_and_self_transition_reject_atomically(
            self, tmp_path):
        store, registration, from_registration, to_registration, *_ = \
            world(tmp_path)
        duplicate_anchor = transition_registration(
            from_registration=from_registration,
            to_registration=to_registration, note="second TRG")
        duplicate_tuple = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=from_registration,
            to_registration=to_registration, note="parallel identity")
        self_transition = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=from_registration,
            to_registration=to_registration,
            from_state=STATE_A, to_state=STATE_A,
            evidence=registration.evidence)
        assert_atomic_rejection(
            store, duplicate_anchor, "MODEL_DUPLICATE_REGISTRATION")
        assert_atomic_rejection(
            store, duplicate_tuple, "MODEL_TRANSITION_REGISTRATION_INVALID")
        assert_atomic_rejection(
            store, self_transition, "MODEL_TRANSITION_REGISTRATION_INVALID")

    def test_reversed_ordered_pair_coexists_as_distinct_transition(self,
                                                                  tmp_path):
        store, _, from_registration, to_registration, *_ = world(tmp_path)
        reverse = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=to_registration,
            to_registration=from_registration,
            from_state=STATE_B, to_state=STATE_A)
        store.append(reverse)
        loaded = store.load()
        assert loaded.transition_registrations_by_anchor[TRANSITION_B] == \
            reverse
        assert loaded.transition_anchor_ids_by_subject_entity[ENT_A] == (
            TRANSITION_A, TRANSITION_B)
        forward_key = (ENT_A, STATE_A, STATE_B)
        reverse_key = (ENT_A, STATE_B, STATE_A)
        index = loaded.transition_registration_id_by_ordered_subject_endpoints
        assert index[forward_key] != index[reverse_key]
        assert index[reverse_key] == reverse.record_id

    def test_missing_subject_and_endpoint_reference_precedence_is_exact(self):
        records, registration, from_registration, to_registration, *_ = \
            transition_fixture()
        missing_subject = transition_registration(
            transition_anchor_id=TRANSITION_B, subject=ENT_C,
            from_registration=from_registration,
            to_registration=to_registration, evidence=registration.evidence)
        missing_endpoint = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=from_registration,
            to_registration=to_registration, to_state="sta_" + "c" * 32,
            evidence=registration.evidence)
        missing_self_endpoint = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=from_registration,
            to_registration=to_registration,
            from_state="sta_" + "c" * 32,
            to_state="sta_" + "c" * 32,
            evidence=registration.evidence)
        for candidate in (
                missing_subject, missing_endpoint, missing_self_endpoint):
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", {
                    record.record_id: record
                    for record in (*records, candidate)})
            assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_cross_subject_endpoint_rejects_even_with_complete_evidence(self):
        records = condition_world_records(owner=ENT_A, second_owner=ENT_B)
        relation_type = contains_type()
        hierarchy = assertion(relation_type, source=ENT_A, target=ENT_B)
        from_registration = state_registration(
            state_anchor_id=STATE_A, subject=ENT_A, constraints=(CON_A,),
            note="from")
        to_registration = state_registration(
            state_anchor_id=STATE_B, subject=ENT_B, constraints=(CON_B,),
            second_owner=ENT_B, note="to")
        registration = transition_registration(
            subject=ENT_A, from_registration=from_registration,
            to_registration=to_registration,
            evidence=registration_evidence(
                from_registration, to_registration, subject=ENT_A))
        collection = {record.record_id: record for record in (
            *records, relation_type, hierarchy,
            from_registration, to_registration, registration)}
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", collection)
        assert error.value.error_code == \
            "MODEL_TRANSITION_REGISTRATION_INVALID"

    def test_uniform_closure_precedes_required_citations_and_claim_basis(
            self, tmp_path):
        store, _, from_registration, to_registration, *_ = world(tmp_path)
        unknown = citation("trg_" + "f" * 64)
        bad = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=from_registration,
            to_registration=to_registration,
            evidence=(unknown, TRANSITION_REGISTRATION_CLAIM))
        assert_atomic_rejection(store, bad, "MODEL_REFERENCE_INVALID")

    def test_registration_requires_exact_three_citations_and_claim(self,
                                                                    tmp_path):
        _, complete, from_registration, to_registration, *_ = \
            transition_fixture()
        refs = tuple(item for item in complete.evidence
                     if item.kind == "model_record")
        store, *_ = world(tmp_path)
        attacks = (
            (TRANSITION_REGISTRATION_CLAIM,), refs,
            *(tuple(ref for position, ref in enumerate(refs)
                    if position != omitted) + (TRANSITION_REGISTRATION_CLAIM,)
              for omitted in range(len(refs))),
        )
        for index, evidence in enumerate(attacks):
            candidate = transition_registration(
                transition_anchor_id=TRANSITION_B,
                from_registration=from_registration,
                to_registration=to_registration,
                evidence=evidence, note=f"attack-{index}")
            assert_atomic_rejection(
                store, candidate, "MODEL_TRANSITION_REGISTRATION_INVALID")


class TestTransitionDeclarationAdmission:
    def test_declaration_admits_exact_pins_and_indexes(self, tmp_path):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        declaration = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration)
        store, *_ = world(tmp_path, declaration)
        loaded = store.load()
        key = (TRANSITION_A, AS_OPERATED)
        assert loaded.transition_declarations[declaration.record_id] == \
            declaration
        assert loaded.transition_declaration_ids_by_key[key] == (
            declaration.record_id,)
        assert loaded.transition_declaration_parent_ids[
            declaration.record_id] == ()
        assert loaded.transition_declaration_root_by_id[
            declaration.record_id] == declaration.record_id
        assert loaded.current_transition_declaration_tips_by_root[
            declaration.record_id] == (declaration,)

    def test_view_independent_exact_context_admits(self, tmp_path):
        records, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture(
                context=VIEW_INDEPENDENT)
        declaration = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration, context=VIEW_INDEPENDENT)
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (*records, registration, declaration):
            store.append(record)
        assert store.load().transition_declarations[declaration.record_id] == \
            declaration

    def test_missing_wrong_role_anchor_and_context_substitutions_reject(
            self, tmp_path):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        store, *_ = world(tmp_path)
        missing = endpoint(STATE_A, "std_" + "f" * 64)
        swapped = endpoint(STATE_B, from_declaration.record_id)
        wrong_std = endpoint(STATE_A, to_declaration.record_id)
        designed = state_declaration(
            from_registration, state_anchor_id=STATE_A,
            context={"kind": "lifecycle_view", "view": "as_designed"},
            note="designed")
        store.append(designed)
        attacks = (
            {"from_endpoint": missing},
            {"from_endpoint": swapped},
            {"from_endpoint": wrong_std},
            {"from_endpoint": endpoint(STATE_A, designed.record_id)},
            {"context": VIEW_INDEPENDENT},
        )
        for index, overrides in enumerate(attacks):
            candidate = transition_declaration(
                registration, from_registration=from_registration,
                to_registration=to_registration,
                from_declaration=from_declaration,
                to_declaration=to_declaration,
                note=f"attack-{index}", **overrides)
            assert_atomic_rejection(
                store, candidate, "MODEL_REFERENCE_INVALID",
                "MODEL_TRANSITION_DECLARATION_INVALID")

    def test_uniform_closure_precedes_required_citations_and_claim_basis(
            self, tmp_path):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        store, *_ = world(tmp_path)
        bad = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration,
            evidence=(citation("trd_" + "f" * 64),
                      TRANSITION_DECLARATION_CLAIM))
        assert_atomic_rejection(store, bad, "MODEL_REFERENCE_INVALID")

    def test_missing_transition_registration_rejects_reference_typed(self):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        declaration = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration,
            transition_anchor_id=TRANSITION_B)
        records, *_ = transition_fixture()
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", {
                record.record_id: record for record in (*records, declaration)})
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_additional_transition_citation_closes_on_append_and_replay(
            self, tmp_path):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        support = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration, note="support root")
        dependent = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration,
            evidence=(*transition_declaration(
                registration, from_registration=from_registration,
                to_registration=to_registration,
                from_declaration=from_declaration,
                to_declaration=to_declaration).evidence,
                      citation(support.record_id)),
            note="dependent root")
        store, *_ = world(tmp_path, support, dependent)
        subset = tuple(record_id for record_id in store.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_declaration_requires_exact_five_citations_and_claim(self,
                                                                 tmp_path):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        complete = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration)
        refs = tuple(item for item in complete.evidence
                     if item.kind == "model_record")
        store, *_ = world(tmp_path)
        attacks = (
            (TRANSITION_DECLARATION_CLAIM,), refs,
            *(tuple(ref for position, ref in enumerate(refs)
                    if position != omitted) + (TRANSITION_DECLARATION_CLAIM,)
              for omitted in range(len(refs))),
        )
        for index, evidence in enumerate(attacks):
            candidate = transition_declaration(
                registration, from_registration=from_registration,
                to_registration=to_registration,
                from_declaration=from_declaration,
                to_declaration=to_declaration,
                evidence=evidence, note=f"attack-{index}")
            assert_atomic_rejection(
                store, candidate, "MODEL_TRANSITION_DECLARATION_INVALID")


class TestTransitionLifecycle:
    def _claims(self):
        _, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()

        def claim(**kwargs):
            return transition_declaration(
                registration, from_registration=from_registration,
                to_registration=to_registration,
                from_declaration=from_declaration,
                to_declaration=to_declaration, **kwargs)

        return claim

    def test_rc3_same_root_two_parent_merge_restores_one_tip(self, tmp_path):
        claim = self._claims()
        root = claim(note="root")
        left = claim(supersedes=(root.record_id,), note="left")
        right = claim(supersedes=(root.record_id,), note="right")
        merged = claim(
            supersedes=(right.record_id, left.record_id), note="merged")
        store, *_ = world(tmp_path, root, left, right, merged)
        loaded = store.load()
        assert loaded.transition_declaration_successor_ids[left.record_id] == (
            merged.record_id,)
        assert loaded.transition_declaration_successor_ids[right.record_id] == (
            merged.record_id,)
        assert loaded.current_transition_declaration_tips_by_root[
            root.record_id] == (merged,)
        assert loaded.transition_declaration_ancestry_by_id[
            merged.record_id] == tuple(sorted(
                (root.record_id, left.record_id, right.record_id)))

    def test_rc3_divergent_pin_branches_merge_within_one_root(self, tmp_path):
        records, registration, from_registration, to_registration, \
            from_root, to_root = transition_fixture()
        from_left = state_declaration(
            from_registration, state_anchor_id=STATE_A, note="left STD root")
        from_right = state_declaration(
            from_registration, state_anchor_id=STATE_A, note="right STD root")

        def claim(from_pin, **kwargs):
            return transition_declaration(
                registration, from_registration=from_registration,
                to_registration=to_registration, from_declaration=from_pin,
                to_declaration=to_root, **kwargs)

        root = claim(from_root, note="transition root")
        left = claim(
            from_left, supersedes=(root.record_id,), note="left branch")
        right = claim(
            from_right, supersedes=(root.record_id,), note="right branch")
        merged = claim(
            from_right, supersedes=(right.record_id, left.record_id),
            note="explicit merge")
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (
                *records, from_left, from_right, registration,
                root, left, right, merged):
            store.append(record)
        loaded = store.load()
        assert left.from_endpoint != right.from_endpoint
        assert {loaded.transition_declaration_root_by_id[item.record_id]
                for item in (root, left, right, merged)} == {root.record_id}
        assert loaded.transition_declaration_successor_ids[left.record_id] == (
            merged.record_id,)
        assert loaded.transition_declaration_successor_ids[right.record_id] == (
            merged.record_id,)
        assert loaded.current_transition_declaration_tips_by_root[
            root.record_id] == (merged,)

    def test_partial_convergence_leaves_two_deterministic_tips(self, tmp_path):
        claim = self._claims()
        root = claim(note="root")
        left = claim(supersedes=(root.record_id,), note="left")
        middle = claim(supersedes=(root.record_id,), note="middle")
        right = claim(supersedes=(root.record_id,), note="right")
        partial = claim(
            supersedes=(left.record_id, middle.record_id),
            note="partial two-parent merge")
        store, *_ = world(tmp_path, root, left, middle, right, partial)
        assert tuple(record.record_id for record in
                     store.load().current_transition_declaration_tips_by_root[
                         root.record_id]) == tuple(sorted(
                             (partial.record_id, right.record_id)))

    def test_rc3_cross_root_parent_tuple_rejects_typed(self, tmp_path):
        claim = self._claims()
        first = claim(note="first root")
        second = claim(note="second root")
        store, *_ = world(tmp_path, first, second)
        cross = claim(
            supersedes=(first.record_id, second.record_id), note="cross")
        assert_atomic_rejection(
            store, cross, "MODEL_TRANSITION_LINEAGE_INVALID")

    def test_missing_and_cross_transition_parents_reject_typed(self):
        claim = self._claims()
        missing = claim(supersedes=("trd_" + "f" * 64,), note="missing")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", complete_records(missing))
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        records, forward, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        reverse = transition_registration(
            transition_anchor_id=TRANSITION_B,
            from_registration=to_registration,
            to_registration=from_registration,
            from_state=STATE_B, to_state=STATE_A)
        reverse_root = transition_declaration(
            reverse, from_registration=to_registration,
            to_registration=from_registration,
            from_declaration=to_declaration,
            to_declaration=from_declaration, note="reverse root")
        cross = transition_declaration(
            forward, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration,
            supersedes=(reverse_root.record_id,), note="cross transition")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", {
                record.record_id: record for record in (
                    *records, forward, reverse, reverse_root, cross)})
        assert error.value.error_code == "MODEL_TRANSITION_LINEAGE_INVALID"

    def test_parent_key_mismatch_cycle_and_deep_dag_reject_or_derive(self):
        records, registration, from_registration, to_registration, \
            from_declaration, to_declaration = transition_fixture()
        root = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration, note="root")
        designed = kernel.LifecycleViewContext(
            kind="lifecycle_view", view="as_designed")
        from_designed = state_declaration(
            from_registration, state_anchor_id=STATE_A, context=designed,
            note="from designed")
        to_designed = state_declaration(
            to_registration, state_anchor_id=STATE_B, context=designed,
            note="to designed")
        changed_context = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration,
            from_declaration=from_designed, to_declaration=to_designed,
            context=designed, supersedes=(root.record_id,),
            note="wrong context")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "test-model", {record.record_id: record for record in (
                    *records, registration, from_designed, to_designed,
                    root, changed_context)})
        assert error.value.error_code == "MODEL_TRANSITION_LINEAGE_INVALID"

        claim = self._claims()
        chain = []
        parent = None
        for index in range(1100):
            item = claim(
                supersedes=(() if parent is None else (parent.record_id,)),
                note=f"depth-{index}")
            chain.append(item)
            parent = item
        loaded = validate_record_collection(
            "test-model", complete_records(*chain))
        assert loaded.current_transition_declaration_tips_by_root[
            chain[0].record_id] == (chain[-1],)

    def test_selective_withdrawal_and_historical_replay_revive_tips(
            self, tmp_path):
        claim = self._claims()
        root = claim(note="root")
        left = claim(supersedes=(root.record_id,), note="left")
        right = claim(supersedes=(root.record_id,), note="right")
        event = transition_withdrawal(left)
        store, *_ = world(tmp_path, root, left, right, event)
        loaded = store.load()
        assert loaded.transition_declaration_withdrawn_by[left.record_id] == (
            event.record_id,)
        assert loaded.current_transition_declaration_tips_by_root[
            root.record_id] == (right,)
        replay = store.replay(tuple(
            record_id for record_id in loaded.revision.record_ids
            if record_id != event.record_id))
        assert tuple(record.record_id for record in
                     replay.current_transition_declaration_tips_by_root[
                         root.record_id]) == tuple(sorted(
                             (left.record_id, right.record_id)))

    def test_independent_roots_and_active_inactive_shapes_remain_explicit(
            self, tmp_path):
        claim = self._claims()
        first = claim(note="first independent root")
        second = claim(note="second independent root")
        healthy_store, *_ = world(tmp_path / "healthy", first, second)
        healthy = healthy_store.load()
        assert healthy.current_transition_declaration_tips_by_root[
            first.record_id] == (first,)
        assert healthy.current_transition_declaration_tips_by_root[
            second.record_id] == (second,)
        active_store, *_ = world(
            tmp_path / "active", first, second,
            transition_withdrawal(first))
        active = active_store.load()
        assert active.transition_declaration_root_by_id == {
            first.record_id: first.record_id,
            second.record_id: second.record_id,
        }
        assert active.current_transition_declaration_tips_by_root[
            first.record_id] == ()
        assert active.current_transition_declaration_tips_by_root[
            second.record_id] == (second,)
        assert active.transition_registrations_by_anchor[TRANSITION_A]

        inactive_store, *_ = world(
            tmp_path / "inactive", first, second,
            transition_withdrawal(first),
            transition_withdrawal(second, note="second withdrawal"))
        inactive = inactive_store.load()
        assert inactive.current_transition_declaration_tips_by_root == {
            first.record_id: (), second.record_id: ()}
        assert inactive.transition_registrations_by_anchor[TRANSITION_A]

    def test_independent_different_pin_bodies_remain_separate_roots(
            self, tmp_path):
        records, registration, from_registration, to_registration, \
            from_root, to_root = transition_fixture()
        alternate = state_declaration(
            from_registration, state_anchor_id=STATE_A,
            note="alternate exact STD")
        first = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=from_root,
            to_declaration=to_root, note="first transition root")
        second = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=alternate,
            to_declaration=to_root, note="different transition root")
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (*records, alternate, registration, first, second):
            store.append(record)
        loaded = store.load()
        assert first.from_endpoint != second.from_endpoint
        assert loaded.transition_declaration_root_by_id[first.record_id] == \
            first.record_id
        assert loaded.transition_declaration_root_by_id[second.record_id] == \
            second.record_id
        assert loaded.current_transition_declaration_tips_by_root[
            first.record_id] == (first,)
        assert loaded.current_transition_declaration_tips_by_root[
            second.record_id] == (second,)

    def test_unknown_superseded_duplicate_and_successor_race_reject(
            self, tmp_path):
        claim = self._claims()
        unknown = kernel.build_record(
            kernel.TransitionDeclarationWithdrawal,
            withdraws="trd_" + "f" * 64,
            recorded_at=transition_withdrawal(claim()).recorded_at,
            authority=claim().authority, note="unknown")
        store, *_ = world(tmp_path / "unknown")
        assert_atomic_rejection(store, unknown, "MODEL_REFERENCE_INVALID")

        root = claim(note="root")
        child = claim(supersedes=(root.record_id,), note="child")
        store, *_ = world(tmp_path / "superseded", root, child)
        assert_atomic_rejection(
            store, transition_withdrawal(root),
            "MODEL_TRANSITION_WITHDRAWAL_INVALID")
        withdrawn, *_ = world(
            tmp_path / "withdrawn", root, transition_withdrawal(root))
        assert_atomic_rejection(
            withdrawn, transition_withdrawal(root, note="again"),
            "MODEL_TRANSITION_WITHDRAWAL_INVALID")
        assert_atomic_rejection(
            withdrawn, child, "MODEL_TRANSITION_WITHDRAWAL_INVALID")

    def test_replay_omitting_successor_revives_predecessor_tip(self, tmp_path):
        claim = self._claims()
        root = claim(note="root")
        child = claim(supersedes=(root.record_id,), note="child")
        store, *_ = world(tmp_path, root, child)
        replay = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id != child.record_id))
        assert replay.current_transition_declaration_tips_by_root[
            root.record_id] == (root,)

    def test_rc1_superseded_and_withdrawn_state_pins_admit_without_retarget(
            self, tmp_path):
        records, registration, from_registration, to_registration, \
            from_root, to_root = transition_fixture()
        from_successor = state_declaration(
            from_registration, state_anchor_id=STATE_A,
            supersedes=(from_root.record_id,), note="state successor")
        superseded_pin = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=from_root,
            to_declaration=to_root, note="pins superseded STD")
        store = kernel.ModelStore(tmp_path / "superseded-pin")
        for record in (*records, registration, from_successor, superseded_pin):
            store.append(record)
        loaded = store.load()
        assert loaded.transition_declarations[
            superseded_pin.record_id].from_endpoint.declaration_record_id == \
            from_root.record_id
        assert loaded.state_declaration_successor_ids[from_root.record_id] == (
            from_successor.record_id,)

        peer = state_declaration(
            from_registration, state_anchor_id=STATE_A,
            note="surviving healthy state root")
        withdrawn_pin = transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=from_root,
            to_declaration=to_root, note="pins withdrawn STD")
        withdrawn_store = kernel.ModelStore(tmp_path / "withdrawn-pin")
        for record in (*records, peer, registration,
                       state_withdrawal(from_root), withdrawn_pin):
            withdrawn_store.append(record)
        withdrawn_loaded = withdrawn_store.load()
        assert withdrawn_loaded.transition_declarations[
            withdrawn_pin.record_id].from_endpoint.declaration_record_id == \
            from_root.record_id
        assert withdrawn_loaded.state_declaration_withdrawn_by[
            from_root.record_id]
        assert withdrawn_loaded.current_state_declaration_tips_by_root[
            peer.record_id] == (peer,)


def test_transition_indexes_are_deterministic_under_reversed_input():
    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    root = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration, note="root")
    child = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration, supersedes=(root.record_id,),
        note="child")
    values = tuple(complete_records(root, child).values())
    forward = validate_record_collection(
        "test-model", {record.record_id: record for record in values})
    reverse = validate_record_collection(
        "test-model", {record.record_id: record for record in reversed(values)})
    names = (
        "transition_registrations", "transition_registrations_by_anchor",
        "transition_anchor_ids_by_subject_entity",
        "transition_registration_id_by_ordered_subject_endpoints",
        "transition_declarations", "transition_declaration_ids_by_key",
        "transition_declaration_parent_ids",
        "transition_declaration_successor_ids",
        "transition_declaration_root_by_id",
        "transition_declaration_ancestry_by_id",
        "current_transition_declaration_tips_by_root",
        "transition_declaration_withdrawals",
        "transition_declaration_withdrawn_by",
        "transition_declaration_withdrawals_by_target",
    )
    assert forward.revision == reverse.revision
    for name in names:
        assert dict(getattr(forward, name)) == dict(getattr(reverse, name))
