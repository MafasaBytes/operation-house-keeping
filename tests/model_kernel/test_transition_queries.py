"""ST-002 Slice B transition lifecycle, collection, and assertion queries."""

from datetime import timedelta

import pytest

import backend.model_kernel as kernel
from tests.model_kernel.builders import ENT_A, ENT_B
from tests.model_kernel.st001_slice_a_helpers import state_declaration
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    STATE_B,
    T0,
    T1,
    TRANSITION_A,
    TRANSITION_B,
    VIEW_INDEPENDENT,
    transition_declaration,
    transition_fixture,
    transition_registration,
    transition_withdrawal,
    world,
)


def record_ids(material, indices):
    return tuple(material.record_at(index).record_id for index in indices)


def declaration_for_fixture(*, context=AS_OPERATED, supersedes=(),
                            recorded_at=T0, note=""):
    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture(context=context)
    return transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration, context=context,
        supersedes=supersedes, recorded_at=recorded_at, note=note)


def test_transition_lookup_is_permanent_and_resolves_exact_registrations(
        tmp_path):
    store, registration, from_registration, to_registration, *_ = world(
        tmp_path)
    result = kernel.ModelQueries(store.load()).transition(TRANSITION_A)
    assert result.status == "registered"
    assert result.registration == registration
    assert result.subject_entity_registration.anchor.anchor_id == ENT_A
    assert result.from_state_registration == from_registration
    assert result.to_state_registration == to_registration
    assert result.from_state_registration.anchor.anchor_id == STATE_A
    assert result.to_state_registration.anchor.anchor_id == STATE_B


def test_declaration_not_declared_and_exact_context_isolation(tmp_path):
    store, *_ = world(tmp_path)
    queries = kernel.ModelQueries(store.load())
    for context in (
            AS_OPERATED,
            kernel.LifecycleViewContext(
                kind="lifecycle_view", view="as_designed")):
        result = queries.transition_declaration(
            TRANSITION_A, context=context)
        assert (result.conclusion, result.lineage_summary,
                result.agreement_findings, result.roots,
                result.effective_body_groups,
                result.current_declaration_indices) == (
                    "not_declared", "not_applicable", (), (), (), ())
        assert result.registration_index is not None


def test_temporal_noninference_rows_t03_t04_t05_and_t07_are_executable(
        tmp_path):
    store, *_ = world(tmp_path)
    queries = kernel.ModelQueries(store.load())
    for forbidden_kwargs in (
        {"classifications": ("matches", "does_not_match")},
        {"cutoffs": ("earlier", "later")},
        {"change_class": "step"},
        {"previous_occurrence": "event"},
        {"receipt_order": (1, 2)},
        {"source_order": (1, 2)},
        {"proximity": 0},
    ):
        with pytest.raises(TypeError):
            queries.transition_declaration(
                TRANSITION_A, context=AS_OPERATED, **forbidden_kwargs)

    states = queries.states_of_entity(ENT_A, context=AS_OPERATED)
    assert {entry.state_anchor_id for entry in states.entries} == {
        STATE_A, STATE_B}
    declaration = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert declaration.conclusion == "not_declared"
    assert declaration.effective_body_groups == ()

    transition_contract_words = {
        field
        for contract in (
            kernel.TransitionLookupResult,
            kernel.TransitionDeclarationResult,
            kernel.EntityTransitionEntry,
            kernel.EntityTransitionsResult,
            kernel.TransitionAssertionDisclosureResult,
        )
        for field in contract.model_fields
    }
    assert transition_contract_words.isdisjoint({
        "classification", "change_class", "cohort", "persistence",
        "continuity", "causality", "control", "safety", "diagnosis",
        "recommendation", "occurred", "occurrence", "confidence",
    })


def test_one_healthy_root_discloses_exact_endpoints_and_shared_st_parity(
        tmp_path):
    declaration = declaration_for_fixture(note="root")
    store, registration, from_registration, to_registration, \
        from_declaration, to_declaration = world(tmp_path, declaration)
    queries = kernel.ModelQueries(store.load())
    result = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert record_ids(result.material,
                      result.current_declaration_indices) == (
                          declaration.record_id,)
    assert len(result.roots) == len(result.effective_body_groups) == 1
    root = result.roots[0]
    assert root.root_record == declaration
    assert root.lineage_records == (declaration,)
    assert root.current_tips == (declaration,)
    assert root.lineage_health == "healthy"
    group = result.effective_body_groups[0]
    assert group.representative_declaration == declaration
    assert group.current_tips == (declaration,)
    assert group.root_records == (declaration,)
    for role, endpoint, state_registration, state_declaration_record in (
        ("from", group.from_endpoint, from_registration, from_declaration),
        ("to", group.to_endpoint, to_registration, to_declaration),
    ):
        assert endpoint.role == role
        assert endpoint.state_registration == state_registration
        assert endpoint.declaration == state_declaration_record
        state_result = queries.state_declaration(
            state_registration.anchor.anchor_id, context=AS_OPERATED)
        assertion_result = queries.state_assertion(
            state_declaration_record.record_id)
        assert endpoint.state_declaration_conclusion == \
            state_result.conclusion == "declared"
        assert endpoint.pinned_declaration_activity == \
            assertion_result.activity == "current"
        assert endpoint.alignment == "exact_current"
    assert result.registration_index == result.material.revision.record_ids.index(
        registration.record_id)


def test_same_root_fork_partial_and_complete_merge_are_structural(tmp_path):
    root = declaration_for_fixture(note="root")
    left = declaration_for_fixture(
        supersedes=(root.record_id,), recorded_at=T1, note="left")
    right = declaration_for_fixture(
        supersedes=(root.record_id,), recorded_at=T1 + timedelta(seconds=1),
        note="right")
    fork = kernel.ModelQueries(world(
        tmp_path / "fork", root, left, right)[0].load()
                               ).transition_declaration(
                                   TRANSITION_A, context=AS_OPERATED)
    assert (fork.conclusion, fork.lineage_summary,
            fork.agreement_findings) == (
                "conflicted", "conflicted", ("same_root_conflict",))
    assert fork.roots[0].lineage_health == "conflicted"
    assert len(fork.effective_body_groups) == 1
    assert record_ids(fork.material, fork.current_declaration_indices) == \
        tuple(sorted((left.record_id, right.record_id)))

    partial = declaration_for_fixture(
        supersedes=(left.record_id,), recorded_at=T1 + timedelta(seconds=2),
        note="partial")
    partial_result = kernel.ModelQueries(world(
        tmp_path / "partial", root, left, right, partial)[0].load()
                                         ).transition_declaration(
                                             TRANSITION_A,
                                             context=AS_OPERATED)
    assert partial_result.conclusion == "conflicted"
    assert record_ids(
        partial_result.material,
        partial_result.current_declaration_indices) == tuple(sorted(
            (right.record_id, partial.record_id)))

    merge = declaration_for_fixture(
        supersedes=(left.record_id, right.record_id),
        recorded_at=T1 + timedelta(seconds=3), note="merge")
    merged = kernel.ModelQueries(world(
        tmp_path / "merged", root, left, right, merge)[0].load()
                                 ).transition_declaration(
                                     TRANSITION_A, context=AS_OPERATED)
    assert (merged.conclusion, merged.lineage_summary,
            merged.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert record_ids(merged.material,
                      merged.current_declaration_indices) == (
                          merge.record_id,)
    assert kernel.ModelQueries(world(
        tmp_path / "assertions", root, left, right, merge)[0].load()
                               ).transition_assertion(left.record_id).activity \
        == "superseded"


def test_independent_roots_corroborate_or_disagree_by_exact_pins(tmp_path):
    first = declaration_for_fixture(note="authority one")
    second = declaration_for_fixture(
        recorded_at=T1, note="authority two")
    corroborating = kernel.ModelQueries(world(
        tmp_path / "same", first, second)[0].load()
                                        ).transition_declaration(
                                            TRANSITION_A,
                                            context=AS_OPERATED)
    assert (corroborating.conclusion, corroborating.lineage_summary,
            corroborating.agreement_findings) == (
                "declared", "healthy",
                ("corroborating_healthy_roots",))
    assert len(corroborating.roots) == 2
    assert len(corroborating.effective_body_groups) == 1
    assert corroborating.effective_body_groups[
        0].representative_declaration.record_id == min(
            first.record_id, second.record_id)

    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_declaration.record_id,), recorded_at=T1,
        note="new exact endpoint declaration")
    different = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=successor,
        to_declaration=to_declaration, recorded_at=T1,
        note="different exact pin")
    disagreement = kernel.ModelQueries(world(
        tmp_path / "different", successor, first, different)[0].load()
                                       ).transition_declaration(
                                           TRANSITION_A,
                                           context=AS_OPERATED)
    assert (disagreement.conclusion, disagreement.lineage_summary,
            disagreement.agreement_findings) == (
                "conflicted", "conflicted",
                ("cross_root_effective_body_disagreement",))
    assert len(disagreement.effective_body_groups) == 2


def test_inactive_roots_remain_visible_and_registration_stays_registered(
        tmp_path):
    inactive_root = declaration_for_fixture(note="inactive")
    withdrawal = transition_withdrawal(inactive_root)
    inactive_store, *_ = world(
        tmp_path / "inactive", inactive_root, withdrawal)
    queries = kernel.ModelQueries(inactive_store.load())
    result = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "inactive", "inactive", ("inactive_roots_present",))
    assert result.roots[0].lineage_health == "inactive"
    assert result.roots[0].withdrawals == (withdrawal,)
    assert result.effective_body_groups == ()
    assert result.current_declaration_indices == ()
    assert queries.transition(TRANSITION_A).status == "registered"

    healthy = declaration_for_fixture(
        recorded_at=T1 + timedelta(seconds=1), note="healthy")
    mixed = kernel.ModelQueries(world(
        tmp_path / "mixed", inactive_root, withdrawal, healthy)[0].load()
                                ).transition_declaration(
                                    TRANSITION_A, context=AS_OPERATED)
    assert (mixed.conclusion, mixed.lineage_summary,
            mixed.agreement_findings) == (
                "declared", "healthy",
                ("one_healthy_root", "inactive_roots_present"))
    assert len(mixed.roots) == 2
    assert len(mixed.effective_body_groups) == 1


def test_selective_withdrawal_recomputes_fork_and_assertion_disclosure(
        tmp_path):
    root = declaration_for_fixture(note="root")
    left = declaration_for_fixture(
        supersedes=(root.record_id,), recorded_at=T1, note="left")
    right = declaration_for_fixture(
        supersedes=(root.record_id,), recorded_at=T1 + timedelta(seconds=1),
        note="right")
    withdrawal = transition_withdrawal(right)
    store, registration, *_ = world(
        tmp_path, root, left, right, withdrawal)
    queries = kernel.ModelQueries(store.load())
    declaration = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert declaration.conclusion == "declared"
    assert declaration.roots[0].lineage_health == "healthy"
    assert record_ids(declaration.material,
                      declaration.current_declaration_indices) == (
                          left.record_id,)

    registered = queries.transition_assertion(registration.record_id)
    superseded = queries.transition_assertion(root.record_id)
    current = queries.transition_assertion(left.record_id)
    withdrawn = queries.transition_assertion(right.record_id)
    withdrawal_result = queries.transition_assertion(withdrawal.record_id)
    assert registered.record == registration
    assert registered.activity is None
    assert registered.containing_lineage_health is None
    assert (superseded.activity, current.activity, withdrawn.activity) == (
        "superseded", "current", "withdrawn")
    assert record_ids(superseded.material,
                      superseded.successor_indices) == tuple(sorted(
                          (left.record_id, right.record_id)))
    assert withdrawn.withdrawals == (withdrawal,)
    assert current.containing_lineage_health == "healthy"
    assert current.containing_subject_conclusion == "declared"
    assert withdrawal_result.record == withdrawal
    assert withdrawal_result.activity is None
    assert withdrawal_result.containing_subject_conclusion is None


def test_entity_collection_is_exact_subject_ordered_and_reuses_direct_payload(
        tmp_path):
    declaration = declaration_for_fixture(note="forward")
    store, _, from_registration, to_registration, *_ = world(
        tmp_path, declaration)
    reverse = transition_registration(
        transition_anchor_id=TRANSITION_B,
        from_registration=to_registration,
        to_registration=from_registration,
        from_state=STATE_B, to_state=STATE_A)
    store.append(reverse)
    queries = kernel.ModelQueries(store.load())
    unknown = queries.transitions_of_entity(ENT_B, context=AS_OPERATED)
    assert (unknown.status, unknown.entity_registration_index,
            unknown.entries) == ("entity_not_registered", None, ())

    result = queries.transitions_of_entity(ENT_A, context=AS_OPERATED)
    assert result.status == "registered"
    assert result.entity_registration.anchor.anchor_id == ENT_A
    assert tuple(entry.entry_index for entry in result.entries) == (0, 1)
    assert tuple(entry.transition_anchor_id for entry in result.entries) == (
        TRANSITION_A, TRANSITION_B)
    assert tuple(entry.conclusion for entry in result.entries) == (
        "declared", "not_declared")
    for entry in result.entries:
        direct = queries.transition_declaration(
            entry.transition_anchor_id, context=AS_OPERATED)
        assert entry.model_dump(mode="python", exclude={
            "entry_index", "transition_registration_index",
        }) == direct.model_dump(mode="python", exclude={
            "material", "context", "registration_index",
        })
        assert entry.transition_registration.anchor.anchor_id == \
            entry.transition_anchor_id


def test_entity_collection_discloses_every_declaration_lifecycle_conclusion(
        tmp_path):
    healthy = declaration_for_fixture(note="healthy")
    fork_root = declaration_for_fixture(note="fork root")
    fork_left = declaration_for_fixture(
        supersedes=(fork_root.record_id,), recorded_at=T1, note="fork left")
    fork_right = declaration_for_fixture(
        supersedes=(fork_root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="fork right")
    inactive = declaration_for_fixture(note="inactive")
    cases = (
        ("not_declared", ()),
        ("declared", (healthy,)),
        ("conflicted", (fork_root, fork_left, fork_right)),
        ("inactive", (inactive, transition_withdrawal(inactive))),
    )
    for expected, records in cases:
        store, *_ = world(tmp_path / expected, *records)
        queries = kernel.ModelQueries(store.load())
        collection = queries.transitions_of_entity(
            ENT_A, context=AS_OPERATED)
        entry = next(item for item in collection.entries
                     if item.transition_anchor_id == TRANSITION_A)
        direct = queries.transition_declaration(
            TRANSITION_A, context=AS_OPERATED)
        assert entry.conclusion == direct.conclusion == expected
        assert entry.model_dump(mode="python", exclude={
            "entry_index", "transition_registration_index",
        }) == direct.model_dump(mode="python", exclude={
            "material", "context", "registration_index",
        })


def test_view_independent_transition_query_is_exactly_isolated(tmp_path):
    declaration = declaration_for_fixture(
        context=VIEW_INDEPENDENT, note="view independent")
    store, *_ = world(
        tmp_path, declaration, context=VIEW_INDEPENDENT)
    queries = kernel.ModelQueries(store.load())
    independent = queries.transition_declaration(
        TRANSITION_A, context=VIEW_INDEPENDENT)
    operated = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert independent.conclusion == "declared"
    assert operated.conclusion == "not_declared"


def test_compound_findings_keep_exact_normative_order(tmp_path):
    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_declaration.record_id,), recorded_at=T1,
        note="alternate exact endpoint pin")

    def claim(*, from_pin=from_declaration, supersedes=(), seconds=0,
              note):
        return transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=from_pin,
            to_declaration=to_declaration, supersedes=supersedes,
            recorded_at=T1 + timedelta(seconds=seconds), note=note)

    corroborating_one = claim(note="corroborating one")
    corroborating_two = claim(seconds=1, note="corroborating two")
    divergent = claim(
        from_pin=successor, seconds=2, note="divergent healthy root")
    fork_root = claim(seconds=3, note="fork root")
    fork_left = claim(
        supersedes=(fork_root.record_id,), seconds=4, note="fork left")
    fork_right = claim(
        supersedes=(fork_root.record_id,), seconds=5, note="fork right")
    inactive_root = claim(seconds=6, note="inactive root")
    withdrawal = transition_withdrawal(
        inactive_root, recorded_at=T1 + timedelta(seconds=7))
    result = kernel.ModelQueries(world(
        tmp_path, successor, corroborating_one, corroborating_two, divergent,
        fork_root, fork_left, fork_right, inactive_root, withdrawal)[0].load()
                                 ).transition_declaration(
                                     TRANSITION_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary) == (
        "conflicted", "conflicted")
    assert result.agreement_findings == (
        "corroborating_healthy_roots",
        "same_root_conflict",
        "cross_root_effective_body_disagreement",
        "inactive_roots_present",
    )


def test_assertion_separates_healthy_root_from_conflicted_subject(tmp_path):
    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_declaration.record_id,), recorded_at=T1,
        note="alternate endpoint")
    first = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration, note="first root")
    second = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=successor,
        to_declaration=to_declaration, recorded_at=T1, note="second root")
    queries = kernel.ModelQueries(world(
        tmp_path, successor, first, second)[0].load())
    assertion = queries.transition_assertion(first.record_id)
    assert assertion.activity == "current"
    assert assertion.containing_lineage_health == "healthy"
    assert assertion.containing_subject_conclusion == "conflicted"
    assert assertion.containing_agreement_findings == (
        "cross_root_effective_body_disagreement",)


def test_assertion_discloses_conflicted_and_inactive_containing_lineages(
        tmp_path):
    fork_root = declaration_for_fixture(note="fork assertion root")
    fork_left = declaration_for_fixture(
        supersedes=(fork_root.record_id,), recorded_at=T1,
        note="fork assertion left")
    fork_right = declaration_for_fixture(
        supersedes=(fork_root.record_id,),
        recorded_at=T1 + timedelta(seconds=1),
        note="fork assertion right")
    fork_queries = kernel.ModelQueries(world(
        tmp_path / "fork", fork_root, fork_left, fork_right)[0].load())
    conflicted = fork_queries.transition_assertion(fork_root.record_id)
    assert conflicted.activity == "superseded"
    assert conflicted.containing_lineage_health == "conflicted"
    assert conflicted.containing_subject_conclusion == "conflicted"
    assert conflicted.containing_agreement_findings == (
        "same_root_conflict",)

    inactive_root = declaration_for_fixture(note="inactive assertion root")
    withdrawal = transition_withdrawal(inactive_root)
    inactive_queries = kernel.ModelQueries(world(
        tmp_path / "inactive", inactive_root, withdrawal)[0].load())
    inactive = inactive_queries.transition_assertion(inactive_root.record_id)
    assert inactive.activity == "withdrawn"
    assert inactive.containing_lineage_health == "inactive"
    assert inactive.containing_subject_conclusion == "inactive"
    assert inactive.containing_agreement_findings == (
        "inactive_roots_present",)


def test_recorded_at_never_selects_effective_body_representative(tmp_path):
    earlier_high_id = declaration_for_fixture(
        recorded_at=T0, note="earlier-0")
    later_low_id = declaration_for_fixture(
        recorded_at=T1, note="later-0")
    assert earlier_high_id.recorded_at < later_low_id.recorded_at
    assert earlier_high_id.record_id > later_low_id.record_id
    result = kernel.ModelQueries(world(
        tmp_path, earlier_high_id, later_low_id)[0].load()
                                 ).transition_declaration(
                                     TRANSITION_A, context=AS_OPERATED)
    assert result.conclusion == "declared"
    assert result.agreement_findings == (
        "corroborating_healthy_roots",)
    assert result.effective_body_groups[0].representative_declaration == \
        later_low_id


def test_query_bytes_ignore_legal_independent_append_order(tmp_path):
    first = declaration_for_fixture(note="first")
    second = declaration_for_fixture(recorded_at=T1, note="second")
    forward = kernel.ModelQueries(world(
        tmp_path / "forward", first, second)[0].load())
    reverse = kernel.ModelQueries(world(
        tmp_path / "reverse", second, first)[0].load())

    def disclosures(queries):
        return tuple(result.model_dump_json() for result in (
            queries.transition(TRANSITION_A),
            queries.transition_declaration(
                TRANSITION_A, context=AS_OPERATED),
            queries.transitions_of_entity(ENT_A, context=AS_OPERATED),
            queries.transition_assertion(first.record_id),
        ))

    assert forward.loaded.revision == reverse.loaded.revision
    assert disclosures(forward) == disclosures(reverse)


def test_complex_query_bytes_ignore_reversed_legal_append_order(tmp_path):
    _, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_declaration.record_id,), recorded_at=T1,
        note="complex endpoint successor")

    def claim(*, from_pin=from_declaration, supersedes=(), seconds=0,
              note):
        return transition_declaration(
            registration, from_registration=from_registration,
            to_registration=to_registration, from_declaration=from_pin,
            to_declaration=to_declaration, supersedes=supersedes,
            recorded_at=T1 + timedelta(seconds=seconds), note=note)

    first = claim(note="complex corroborating first")
    second = claim(seconds=1, note="complex corroborating second")
    divergent = claim(
        from_pin=successor, seconds=2, note="complex divergent")
    fork_root = claim(seconds=3, note="complex fork root")
    fork_left = claim(
        supersedes=(fork_root.record_id,), seconds=4,
        note="complex fork left")
    fork_right = claim(
        supersedes=(fork_root.record_id,), seconds=5,
        note="complex fork right")
    inactive_root = claim(seconds=6, note="complex inactive root")
    withdrawal = transition_withdrawal(
        inactive_root, recorded_at=T1 + timedelta(seconds=7))
    forward_order = (
        successor, first, second, divergent, fork_root, fork_left,
        fork_right, inactive_root, withdrawal)
    reversed_legal_order = (
        successor, inactive_root, withdrawal, fork_root, fork_right,
        fork_left, divergent, second, first)
    forward = kernel.ModelQueries(world(
        tmp_path / "forward-complex", *forward_order)[0].load())
    reverse = kernel.ModelQueries(world(
        tmp_path / "reverse-complex", *reversed_legal_order)[0].load())

    transition_record_ids = tuple(sorted(
        record.record_id for record in forward_order
        if record.record_kind.startswith("transition_")))

    def disclosures(queries):
        return tuple(result.model_dump_json() for result in (
            queries.transition(TRANSITION_A),
            queries.transition_declaration(
                TRANSITION_A, context=AS_OPERATED),
            queries.transitions_of_entity(ENT_A, context=AS_OPERATED),
            *(queries.transition_assertion(record_id)
              for record_id in transition_record_ids),
        ))

    declaration = forward.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert len(declaration.roots) == 5
    assert len(declaration.effective_body_groups) == 2
    assert declaration.agreement_findings == (
        "corroborating_healthy_roots",
        "same_root_conflict",
        "cross_root_effective_body_disagreement",
        "inactive_roots_present",
    )
    assert forward.loaded.revision == reverse.loaded.revision
    assert disclosures(forward) == disclosures(reverse)


def test_explicit_positive_membership_replay_rederives_lifecycle(tmp_path):
    records, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture()
    root = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration, note="root")
    left = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration, supersedes=(root.record_id,),
        recorded_at=T1, note="left")
    right = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration, supersedes=(root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="right")
    withdrawal = transition_withdrawal(
        left, recorded_at=T1 + timedelta(seconds=2))
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, registration):
        store.append(record)
    registration_membership = store.load().revision.record_ids
    store.append(root)
    root_membership = store.load().revision.record_ids
    store.append(left)
    store.append(right)
    fork_membership = store.load().revision.record_ids
    store.append(withdrawal)
    withdrawn_membership = store.load().revision.record_ids

    expectations = (
        (registration_membership, "not_declared", None),
        (root_membership, "declared", "current"),
        (fork_membership, "conflicted", "superseded"),
        (withdrawn_membership, "declared", "superseded"),
    )
    for membership, conclusion, root_activity in expectations:
        queries = kernel.ModelQueries(store.replay(membership))
        result = queries.transition_declaration(
            TRANSITION_A, context=AS_OPERATED)
        assert result.conclusion == conclusion
        if root_activity is not None:
            assert queries.transition_assertion(
                root.record_id).activity == root_activity
    revived = kernel.ModelQueries(store.replay(fork_membership))
    assert revived.transition_assertion(left.record_id).activity == "current"
    assert revived.transition_declaration(
        TRANSITION_A, context=AS_OPERATED).conclusion == "conflicted"
