"""BH-001 Slice B read-only registration, lineage, and assertion queries."""

from pathlib import Path

import pytest

import backend.model_kernel as kernel
from tests.model_kernel.bh001_slice_a_helpers import (
    AS_BUILT,
    AS_DESIGNED,
    BEHAVIOR_A,
    BEHAVIOR_B,
    T1,
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
    semantic_lock,
    variable_records,
    world,
)
from tests.model_kernel.builders import ENT_A, ENT_B, VAR_A, VAR_B, VAR_C
from tests.model_kernel.test_demo_model import (
    CN001_MEMBERSHIP,
    PRE_CN001_MEMBERSHIP,
    PRE_ES001_MEMBERSHIP,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_VARIABLE_MEMBERSHIP,
    PT001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")


def record_ids(material, indices):
    return tuple(material.record_at(index).record_id for index in indices)


def test_behavior_lookup_absent_and_registered_same_owner(tmp_path):
    empty = world(tmp_path / "empty", include_registration=False).load()
    absent = kernel.ModelQueries(empty).behavior(BEHAVIOR_A)
    assert absent.status == "not_registered"
    assert absent.registration_index is None
    assert absent.participant_variable_registration_indices == ()
    assert absent.participant_owner_registration_indices == ()

    loaded = world(tmp_path / "registered").load()
    result = kernel.ModelQueries(loaded).behavior(BEHAVIOR_A)
    registration = loaded.behavior_registrations_by_anchor[BEHAVIOR_A]
    assert result.status == "registered"
    assert result.material.record_at(result.registration_index) == registration
    assert tuple(result.material.record_at(index).anchor.anchor_id
                 for index in result.participant_variable_registration_indices
                 ) == registration.participant_variable_anchor_ids
    owner_ids = tuple(result.material.record_at(index).anchor.anchor_id
                      for index in result.participant_owner_registration_indices)
    assert owner_ids == (ENT_A, ENT_A)


def test_behavior_lookup_cross_owner_preserves_pair_alignment(tmp_path):
    loaded = world(tmp_path, owners=(ENT_A, ENT_B)).load()
    result = kernel.ModelQueries(loaded).behavior(BEHAVIOR_A)
    assert tuple(result.material.record_at(index).anchor.entity_anchor_id
                 for index in result.participant_variable_registration_indices
                 ) == (ENT_A, ENT_B)
    assert tuple(result.material.record_at(index).anchor.anchor_id
                 for index in result.participant_owner_registration_indices
                 ) == (ENT_A, ENT_B)


def test_declaration_absence_and_exact_context_isolation(tmp_path):
    registration = behavior_registration()
    declaration = behavior_declaration(registration, context=AS_DESIGNED)
    queries = kernel.ModelQueries(world(tmp_path, declaration).load())
    designed = queries.behavior_declaration(BEHAVIOR_A, context=AS_DESIGNED)
    built = queries.behavior_declaration(BEHAVIOR_A, context=AS_BUILT)
    assert (designed.conclusion, designed.lineage_summary,
            designed.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert (built.conclusion, built.lineage_summary, built.roots,
            built.effective_body_groups, built.current_declaration_indices,
            built.agreement_findings) == (
                "not_declared", "not_applicable", (), (), (), ())


def test_declaration_not_registered_and_registered_without_root(tmp_path):
    loaded = world(tmp_path / "empty", include_registration=False).load()
    absent = kernel.ModelQueries(loaded).behavior_declaration(
        BEHAVIOR_A, context=AS_DESIGNED)
    assert (absent.conclusion, absent.lineage_summary,
            absent.registration_index, absent.roots,
            absent.effective_body_groups, absent.current_declaration_indices,
            absent.agreement_findings) == (
                "not_registered", "not_applicable", None, (), (), (), ())

    registered = kernel.ModelQueries(world(tmp_path / "registered").load()
                                     ).behavior_declaration(
                                         BEHAVIOR_A, context=AS_DESIGNED)
    assert (registered.conclusion, registered.lineage_summary,
            registered.roots, registered.effective_body_groups,
            registered.current_declaration_indices,
            registered.agreement_findings) == (
                "not_declared", "not_applicable", (), (), (), ())


def test_one_healthy_root_discloses_complete_lineage(tmp_path):
    registration = behavior_registration()
    root = behavior_declaration(registration, note="root")
    child = behavior_declaration(
        registration, supersedes=(root.record_id,), note="child")
    result = kernel.ModelQueries(world(tmp_path, root, child).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert len(result.roots) == len(result.effective_body_groups) == 1
    row = result.roots[0]
    assert result.material.record_at(row.root_record_index) == root
    assert record_ids(result.material, row.lineage_record_indices) == tuple(
        sorted((root.record_id, child.record_id)))
    assert record_ids(result.material, row.current_tip_indices) == (
        child.record_id,)
    assert record_ids(result.material, result.current_declaration_indices) == (
        child.record_id,)
    assert row.lineage_health == "healthy"
    assert row.effective_body_group_indices == (0,)


def test_identical_independent_roots_corroborate_by_engineering_body(tmp_path):
    registration = behavior_registration()
    first = behavior_declaration(registration, note="authority one")
    second = behavior_declaration(
        registration, note="authority two", recorded_at=T1)
    result = kernel.ModelQueries(world(tmp_path, first, second).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("corroborating_healthy_roots",))
    assert len(result.roots) == 2
    assert len(result.effective_body_groups) == 1
    group = result.effective_body_groups[0]
    assert group.group_index == 0
    assert record_ids(result.material, group.current_tip_indices) == tuple(
        sorted((first.record_id, second.record_id)))
    assert record_ids(result.material, group.root_record_indices) == tuple(
        sorted((first.record_id, second.record_id)))
    assert result.material.record_at(
        group.representative_declaration_index).record_id == min(
            first.record_id, second.record_id)


def test_independent_different_bodies_conflict_without_winner(tmp_path):
    registration = behavior_registration()
    first = behavior_declaration(registration, note="measured")
    second = behavior_declaration(
        registration, locks=(semantic_lock(VAR_A, role="estimated"),
                             semantic_lock(VAR_B, role="reported")),
        note="estimated")
    result = kernel.ModelQueries(world(tmp_path, first, second).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "conflicted", "conflicted",
                ("cross_root_effective_body_disagreement",))
    assert len(result.roots) == len(result.effective_body_groups) == 2
    assert record_ids(result.material, result.current_declaration_indices) == \
        tuple(sorted((first.record_id, second.record_id)))


@pytest.mark.parametrize("different_body,expected_group_count", [
    (False, 1), (True, 2),
])
def test_same_root_fork_conflicts_even_when_bodies_match(
        tmp_path, different_body, expected_group_count):
    registration = behavior_registration()
    root = behavior_declaration(registration, note="root")
    left = behavior_declaration(
        registration, supersedes=(root.record_id,), note="left")
    locks = ((semantic_lock(VAR_A, role="estimated"),
              semantic_lock(VAR_B, role="reported"))
             if different_body else None)
    right = behavior_declaration(
        registration, supersedes=(root.record_id,), locks=locks, note="right")
    result = kernel.ModelQueries(world(tmp_path, root, left, right).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "conflicted", "conflicted", ("same_root_conflict",))
    assert result.roots[0].lineage_health == "conflicted"
    assert len(result.effective_body_groups) == expected_group_count
    assert len(result.roots[0].effective_body_group_indices) == \
        expected_group_count


def test_partial_corroboration_and_disagreement_findings_coexist(tmp_path):
    registration = behavior_registration()
    one = behavior_declaration(registration, note="A one")
    two = behavior_declaration(registration, note="A two", recorded_at=T1)
    three = behavior_declaration(
        registration, locks=(semantic_lock(VAR_A, role="estimated"),
                             semantic_lock(VAR_B, role="reported")), note="B")
    result = kernel.ModelQueries(world(tmp_path, one, two, three).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert result.conclusion == "conflicted"
    assert result.agreement_findings == (
        "corroborating_healthy_roots",
        "cross_root_effective_body_disagreement",
    )


def test_inactive_roots_and_active_plus_inactive_are_disclosed(tmp_path):
    registration = behavior_registration()
    inactive_root = behavior_declaration(registration, note="inactive")
    event = behavior_withdrawal(inactive_root)
    inactive = kernel.ModelQueries(world(
        tmp_path / "inactive", inactive_root, event).load()
                                    ).behavior_declaration(
                                        BEHAVIOR_A, context=AS_DESIGNED)
    assert (inactive.conclusion, inactive.lineage_summary,
            inactive.agreement_findings) == (
                "inactive", "inactive", ("inactive_roots_present",))
    assert inactive.roots[0].lineage_health == "inactive"
    assert inactive.roots[0].current_tip_indices == ()
    assert inactive.roots[0].effective_body_group_indices == ()
    assert inactive.effective_body_groups == ()

    active_root = behavior_declaration(registration, note="active")
    mixed = kernel.ModelQueries(world(
        tmp_path / "mixed", inactive_root, event, active_root).load()
                                 ).behavior_declaration(
                                     BEHAVIOR_A, context=AS_DESIGNED)
    assert (mixed.conclusion, mixed.lineage_summary,
            mixed.agreement_findings) == (
                "declared", "healthy",
                ("one_healthy_root", "inactive_roots_present"))
    assert tuple(row.lineage_health for row in mixed.roots) == tuple(
        "inactive" if mixed.material.record_at(row.root_record_index) ==
        inactive_root else "healthy" for row in mixed.roots)


def test_reverse_variable_discovery_includes_registered_empty_and_lifecycle(
        tmp_path):
    store = world(tmp_path)
    second_registration = behavior_registration(
        behavior_anchor_id=BEHAVIOR_B, note="second")
    store.append(second_registration)
    first_declaration = behavior_declaration(
        behavior_registration(), note="declared")
    store.append(first_declaration)
    queries = kernel.ModelQueries(store.load())
    result = queries.behaviors_involving_variable(VAR_A, context=AS_DESIGNED)
    assert result.status == "registered"
    assert tuple(entry.entry_index for entry in result.entries) == (0, 1)
    assert tuple(entry.behavior_anchor_id for entry in result.entries) == (
        BEHAVIOR_A, BEHAVIOR_B)
    assert tuple(entry.other_variable_anchor_id for entry in result.entries) == (
        VAR_B, VAR_B)
    assert tuple(entry.conclusion for entry in result.entries) == (
        "declared", "not_declared")

    absent = queries.behaviors_involving_variable(VAR_C, context=AS_DESIGNED)
    assert (absent.status, absent.variable_registration_index,
            absent.owner_registration_index, absent.entries) == (
                "variable_not_registered", None, None, ())


def test_registered_variable_without_behavior_is_registered_empty(tmp_path):
    loaded = world(tmp_path, include_registration=False).load()
    result = kernel.ModelQueries(loaded).behaviors_involving_variable(
        VAR_A, context=AS_DESIGNED)
    assert result.status == "registered"
    assert result.variable_registration_index is not None
    assert result.owner_registration_index is not None
    assert result.entries == ()


def test_assertion_discloses_permanent_event_and_membership_lifecycle(tmp_path):
    registration = behavior_registration()
    root = behavior_declaration(registration, note="root")
    child = behavior_declaration(
        registration, supersedes=(root.record_id,), note="child")
    queries = kernel.ModelQueries(world(tmp_path, root, child).load())

    permanent = queries.behavior_assertion(registration.record_id)
    assert (permanent.lookup_status, permanent.activity,
            permanent.containing_lineage_health,
            permanent.containing_subject_conclusion,
            permanent.containing_agreement_findings,
            permanent.root_record_index, permanent.successor_indices,
            permanent.withdrawal_indices) == (
                "found", None, None, None, None, None, (), ())

    superseded = queries.behavior_assertion(root.record_id)
    assert (superseded.activity, superseded.containing_lineage_health,
            superseded.containing_subject_conclusion,
            superseded.containing_agreement_findings) == (
                "superseded", "healthy", "declared",
                ("one_healthy_root",))
    assert record_ids(superseded.material, superseded.successor_indices) == (
        child.record_id,)

    current = queries.behavior_assertion(child.record_id)
    assert current.activity == "current"
    assert current.root_record_index == superseded.root_record_index


def test_assertion_withdrawal_event_and_valid_absence(tmp_path):
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    event = behavior_withdrawal(declaration)
    queries = kernel.ModelQueries(world(tmp_path, declaration, event).load())
    withdrawn = queries.behavior_assertion(declaration.record_id)
    assert (withdrawn.activity, withdrawn.containing_lineage_health,
            withdrawn.containing_subject_conclusion) == (
                "withdrawn", "inactive", "inactive")
    assert record_ids(withdrawn.material, withdrawn.withdrawal_indices) == (
        event.record_id,)
    disclosed_event = queries.behavior_assertion(event.record_id)
    assert (disclosed_event.lookup_status, disclosed_event.activity,
            disclosed_event.containing_agreement_findings,
            disclosed_event.successor_indices,
            disclosed_event.withdrawal_indices) == (
                "found", None, None, (), ())
    for record_id in ("brg_" + "9" * 64, "bhd_" + "9" * 64,
                      "bhw_" + "9" * 64):
        missing = queries.behavior_assertion(record_id)
        assert (missing.lookup_status, missing.record_index, missing.activity,
                missing.containing_lineage_health,
                missing.containing_subject_conclusion,
                missing.containing_agreement_findings,
                missing.root_record_index, missing.successor_indices,
                missing.withdrawal_indices) == (
                    "not_found", None, None, None, None, None, None, (), ())


def test_assertion_keeps_root_health_and_subject_conflict_independent(tmp_path):
    registration = behavior_registration()
    first = behavior_declaration(registration, note="first")
    second = behavior_declaration(
        registration, locks=(semantic_lock(VAR_A, role="estimated"),
                             semantic_lock(VAR_B, role="reported")),
        note="second")
    result = kernel.ModelQueries(world(tmp_path, first, second).load()
                                 ).behavior_assertion(first.record_id)
    assert (result.activity, result.containing_lineage_health,
            result.containing_subject_conclusion,
            result.containing_agreement_findings) == (
                "current", "healthy", "conflicted",
                ("cross_root_effective_body_disagreement",))


def test_malformed_query_inputs_raise_typed_errors(tmp_path):
    queries = kernel.ModelQueries(world(tmp_path).load())
    calls = (
        lambda: queries.behavior("bhv_bad"),
        lambda: queries.behavior(True),
        lambda: queries.behavior_declaration(BEHAVIOR_A, context=[]),
        lambda: queries.behaviors_involving_variable([], context=AS_DESIGNED),
        lambda: queries.behavior_assertion("vpa_" + "a" * 64),
        lambda: queries.behavior_assertion({}),
    )
    for call in calls:
        with pytest.raises(kernel.ModelQueryError):
            call()


def test_historical_explicit_memberships_return_structured_absence():
    store = kernel.ModelStore(DEMO_MODEL)
    histories = (
        PRE_VARIABLE_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
        VS001_MEMBERSHIP, PRE_ES001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
        CN001_MEMBERSHIP, PT001_MEMBERSHIP, VP001_MEMBERSHIP,
    )
    for membership in histories:
        loaded = store.replay(membership)
        queries = kernel.ModelQueries(loaded)
        result = queries.behavior_declaration(BEHAVIOR_A, context=AS_DESIGNED)
        assert (result.conclusion, result.roots,
                result.effective_body_groups) == (
                    "not_registered", (), ())
        assert queries.behavior(BEHAVIOR_A).status == "not_registered"
        assert queries.behavior_assertion(
            "bhd_" + "9" * 64).lookup_status == "not_found"
        for variable_id in loaded.variable_registrations_by_anchor:
            reverse = queries.behaviors_involving_variable(
                variable_id, context=AS_DESIGNED)
            assert reverse.status == "registered"
            assert reverse.entries == ()
