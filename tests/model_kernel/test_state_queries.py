"""ST-001 Slice B read-only lookup, lifecycle, collection, and assertion queries."""

from datetime import timedelta
from pathlib import Path

import pytest

import backend.model_kernel as kernel
from tests.model_kernel.builders import (
    CON_A, CON_B, ENT_A, ENT_B, VAR_A, VAR_B, constraint_declaration,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_DESIGNED, AS_OPERATED, STATE_A, STATE_B, T0, T1,
    condition_world_records, pins, state_declaration, state_registration,
    state_withdrawal, world,
)
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP, CN001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
    PRE_ES001_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
    PRE_VARIABLE_MEMBERSHIP, PT001_MEMBERSHIP, VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")


def record_ids(material, indices):
    return tuple(material.record_at(index).record_id for index in indices)


def alternate_declaration(registration, *, supersedes=(), note="alternate"):
    alternative_vcn = constraint_declaration(
        CON_A, predicate=upper_bound("90"), recorded_at=T1,
        note="alternate state pin")
    condition_pins = tuple(
        pin.model_copy(update={
            "constraint_declaration_record_id": alternative_vcn.record_id})
        if pin.constraint_anchor_id == CON_A else pin
        for pin in pins())
    declaration = state_declaration(
        registration, condition_pins=condition_pins,
        supersedes=supersedes, recorded_at=T1, note=note)
    return alternative_vcn, declaration


def test_state_lookup_absent_and_registered_with_canonical_condition_alignment(
        tmp_path):
    absent = kernel.ModelQueries(world(
        tmp_path / "absent", include_registration=False).load()).state(STATE_A)
    assert (absent.status, absent.registration_index,
            absent.subject_entity_registration_index,
            absent.condition_constraint_registration_indices,
            absent.condition_variable_registration_indices,
            absent.condition_owner_registration_indices) == (
                "not_registered", None, None, (), (), ())

    loaded = world(tmp_path / "registered").load()
    result = kernel.ModelQueries(loaded).state(STATE_A)
    assert result.status == "registered"
    assert result.registration == loaded.state_registrations_by_anchor[STATE_A]
    assert result.subject_entity_registration.anchor.anchor_id == ENT_A
    assert tuple(result.material.record_at(index).anchor.anchor_id
                 for index in result.condition_constraint_registration_indices
                 ) == (CON_A, CON_B)
    assert tuple(result.material.record_at(index).anchor.anchor_id
                 for index in result.condition_variable_registration_indices
                 ) == (VAR_A, VAR_B)
    assert tuple(result.material.record_at(index).anchor.anchor_id
                 for index in result.condition_owner_registration_indices
                 ) == (ENT_A, ENT_A)
    assert result.condition_owner_registration_indices[0] == \
        result.condition_owner_registration_indices[1]


def test_declaration_absence_and_exact_context_isolation(tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration, context=AS_OPERATED)
    queries = kernel.ModelQueries(world(tmp_path, declaration).load())
    operated = queries.state_declaration(STATE_A, context=AS_OPERATED)
    designed = queries.state_declaration(STATE_A, context=AS_DESIGNED)
    assert (operated.conclusion, operated.lineage_summary,
            operated.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert (designed.conclusion, designed.lineage_summary,
            designed.agreement_findings, designed.roots,
            designed.effective_body_groups,
            designed.current_declaration_indices) == (
                "not_declared", "not_applicable", (), (), (), ())


def test_declaration_not_registered_and_registered_without_root(tmp_path):
    absent = kernel.ModelQueries(world(
        tmp_path / "absent", include_registration=False).load()
                                 ).state_declaration(
                                     STATE_A, context=AS_OPERATED)
    assert (absent.conclusion, absent.lineage_summary,
            absent.registration_index, absent.roots,
            absent.effective_body_groups, absent.current_declaration_indices,
            absent.agreement_findings) == (
                "not_registered", "not_applicable", None, (), (), (), ())
    registered = kernel.ModelQueries(world(tmp_path / "registered").load()
                                     ).state_declaration(
                                         STATE_A, context=AS_OPERATED)
    assert (registered.conclusion, registered.lineage_summary,
            registered.roots, registered.effective_body_groups,
            registered.current_declaration_indices,
            registered.agreement_findings) == (
                "not_declared", "not_applicable", (), (), (), ())


def test_one_healthy_root_discloses_lineage_group_and_condition_material(
        tmp_path):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    child = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="child")
    result = kernel.ModelQueries(world(tmp_path, root, child).load()
                                 ).state_declaration(
                                     STATE_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert len(result.roots) == len(result.effective_body_groups) == 1
    root_row = result.roots[0]
    assert root_row.root_record == root
    assert record_ids(result.material, root_row.lineage_record_indices) == \
        tuple(sorted((root.record_id, child.record_id)))
    assert record_ids(result.material, root_row.current_tip_indices) == (
        child.record_id,)
    assert record_ids(result.material,
                      result.current_declaration_indices) == (child.record_id,)
    group = result.effective_body_groups[0]
    assert group.representative_declaration == child
    assert tuple(row.condition_index for row in group.conditions) == (0, 1)
    assert tuple(row.constraint_anchor_id for row in group.conditions) == (
        CON_A, CON_B)
    assert tuple(row.constraint_registration.anchor.anchor_id
                 for row in group.conditions) == (CON_A, CON_B)
    assert tuple(row.target_variable_registration.anchor.anchor_id
                 for row in group.conditions) == (VAR_A, VAR_B)
    assert tuple(row.target_owner_registration.anchor.anchor_id
                 for row in group.conditions) == (ENT_A, ENT_A)


def test_identical_independent_roots_corroborate_without_merging(tmp_path):
    registration = state_registration()
    first = state_declaration(registration, note="authority one")
    second = state_declaration(
        registration, recorded_at=T1, note="authority two")
    result = kernel.ModelQueries(world(tmp_path, first, second).load()
                                 ).state_declaration(
                                     STATE_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("corroborating_healthy_roots",))
    assert len(result.roots) == 2
    assert len(result.effective_body_groups) == 1
    group = result.effective_body_groups[0]
    assert record_ids(result.material, group.current_tip_indices) == tuple(
        sorted((first.record_id, second.record_id)))
    assert record_ids(result.material, group.root_record_indices) == tuple(
        sorted((first.record_id, second.record_id)))
    assert group.representative_declaration.record_id == min(
        first.record_id, second.record_id)


def test_independent_different_effective_bodies_conflict_without_winner(
        tmp_path):
    registration = state_registration()
    first = state_declaration(registration, note="first")
    alternative_vcn, second = alternate_declaration(registration)
    result = kernel.ModelQueries(world(
        tmp_path, alternative_vcn, first, second).load()
                                 ).state_declaration(
                                     STATE_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "conflicted", "conflicted",
                ("cross_root_effective_body_disagreement",))
    assert len(result.roots) == len(result.effective_body_groups) == 2
    assert record_ids(result.material,
                      result.current_declaration_indices) == tuple(sorted(
                          (first.record_id, second.record_id)))


@pytest.mark.parametrize("different_body,expected_groups", [(False, 1),
                                                               (True, 2)])
def test_same_root_fork_conflicts_even_when_bodies_match(
        tmp_path, different_body, expected_groups):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    left = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="left")
    extras = []
    if different_body:
        alternative_vcn, right = alternate_declaration(
            registration, supersedes=(root.record_id,), note="right")
        extras.append(alternative_vcn)
    else:
        right = state_declaration(
            registration, supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=1), note="right")
    result = kernel.ModelQueries(world(
        tmp_path, *extras, root, left, right).load()).state_declaration(
            STATE_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "conflicted", "conflicted", ("same_root_conflict",))
    assert result.roots[0].lineage_health == "conflicted"
    assert len(result.effective_body_groups) == expected_groups


def test_partial_and_complete_same_root_convergence(tmp_path):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    left = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="left")
    right = state_declaration(
        registration, supersedes=(root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="right")
    partial = state_declaration(
        registration, supersedes=(left.record_id,),
        recorded_at=T1 + timedelta(seconds=2), note="partial")
    partial_result = kernel.ModelQueries(world(
        tmp_path / "partial", root, left, right, partial).load()
                                         ).state_declaration(
                                             STATE_A, context=AS_OPERATED)
    assert partial_result.conclusion == "conflicted"
    assert partial_result.agreement_findings == ("same_root_conflict",)
    assert record_ids(
        partial_result.material,
        partial_result.current_declaration_indices) == tuple(sorted(
            (right.record_id, partial.record_id)))

    merged = state_declaration(
        registration, supersedes=(left.record_id, right.record_id),
        recorded_at=T1 + timedelta(seconds=3), note="merged")
    full_result = kernel.ModelQueries(world(
        tmp_path / "full", root, left, right, merged).load()
                                      ).state_declaration(
                                          STATE_A, context=AS_OPERATED)
    assert (full_result.conclusion, full_result.lineage_summary,
            full_result.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert record_ids(full_result.material,
                      full_result.current_declaration_indices) == (
                          merged.record_id,)


def test_inactive_roots_and_surviving_identical_root_are_disclosed(tmp_path):
    registration = state_registration()
    first = state_declaration(registration, note="withdrawn root")
    event = state_withdrawal(first)
    inactive = kernel.ModelQueries(world(
        tmp_path / "inactive", first, event).load()).state_declaration(
            STATE_A, context=AS_OPERATED)
    assert (inactive.conclusion, inactive.lineage_summary,
            inactive.agreement_findings) == (
                "inactive", "inactive", ("inactive_roots_present",))
    assert inactive.roots[0].lineage_health == "inactive"
    assert inactive.effective_body_groups == ()

    second = state_declaration(
        registration, recorded_at=T1 + timedelta(seconds=1),
        note="surviving root")
    mixed = kernel.ModelQueries(world(
        tmp_path / "mixed", first, event, second).load()).state_declaration(
            STATE_A, context=AS_OPERATED)
    assert (mixed.conclusion, mixed.lineage_summary,
            mixed.agreement_findings) == (
                "declared", "healthy",
                ("one_healthy_root", "inactive_roots_present"))
    assert sorted(row.lineage_health for row in mixed.roots) == [
        "healthy", "inactive"]


def test_selective_fork_withdrawal_restores_one_healthy_tip(tmp_path):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    left = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="left")
    right = state_declaration(
        registration, supersedes=(root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="right")
    event = state_withdrawal(left, recorded_at=T1 + timedelta(seconds=2))
    result = kernel.ModelQueries(world(
        tmp_path, root, left, right, event).load()).state_declaration(
            STATE_A, context=AS_OPERATED)
    assert (result.conclusion, result.lineage_summary,
            result.agreement_findings) == (
                "declared", "healthy", ("one_healthy_root",))
    assert record_ids(result.material,
                      result.roots[0].current_tip_indices) == (right.record_id,)
    assert record_ids(result.material,
                      result.roots[0].withdrawal_indices) == (event.record_id,)


def test_entity_reverse_discovery_includes_lifecycle_and_registered_empty(
        tmp_path):
    registration_a = state_registration()
    declaration_a = state_declaration(registration_a)
    registration_b = state_registration(state_anchor_id=STATE_B)
    store = world(tmp_path, declaration_a, registration_b)
    result = kernel.ModelQueries(store.load()).states_of_entity(
        ENT_A, context=AS_OPERATED)
    assert result.status == "registered"
    assert tuple(entry.entry_index for entry in result.entries) == (0, 1)
    assert tuple(entry.state_anchor_id for entry in result.entries) == (
        STATE_A, STATE_B)
    assert tuple(entry.conclusion for entry in result.entries) == (
        "declared", "not_declared")

    empty = kernel.ModelQueries(world(
        tmp_path / "empty", include_registration=False).load()
                                ).states_of_entity(
                                    ENT_A, context=AS_OPERATED)
    assert (empty.status, empty.entries) == ("registered", ())
    absent = kernel.ModelQueries(store.load()).states_of_entity(
        ENT_B, context=AS_OPERATED)
    assert (absent.status, absent.entity_registration_index,
            absent.entries) == ("entity_not_registered", None, ())


def test_constraint_existence_and_ownership_do_not_infer_state(tmp_path):
    loaded = world(tmp_path, include_registration=False).load()
    result = kernel.ModelQueries(loaded).states_of_entity(
        ENT_A, context=AS_OPERATED)
    assert loaded.constraint_registrations_by_anchor
    assert loaded.variable_registrations_by_anchor
    assert result.status == "registered"
    assert result.entries == ()


def test_assertion_discloses_events_activity_and_subject_health(tmp_path):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    child = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="child")
    queries = kernel.ModelQueries(world(tmp_path, root, child).load())

    permanent = queries.state_assertion(registration.record_id)
    assert permanent.lookup_status == "found"
    assert permanent.record == registration
    assert permanent.activity is None
    assert permanent.root_record_index is None

    superseded = queries.state_assertion(root.record_id)
    assert superseded.activity == "superseded"
    assert superseded.containing_lineage_health == "healthy"
    assert superseded.containing_subject_conclusion == "declared"
    assert record_ids(superseded.material,
                      superseded.successor_indices) == (child.record_id,)

    current = queries.state_assertion(child.record_id)
    assert current.activity == "current"
    assert current.root_record == root

    withdrawal = state_withdrawal(child)
    withdrawn_queries = kernel.ModelQueries(world(
        tmp_path / "withdrawn", root, child, withdrawal).load())
    withdrawn = withdrawn_queries.state_assertion(child.record_id)
    assert withdrawn.activity == "withdrawn"
    assert withdrawn.containing_lineage_health == "inactive"
    assert withdrawn.containing_subject_conclusion == "inactive"
    event = withdrawn_queries.state_assertion(withdrawal.record_id)
    assert event.lookup_status == "found"
    assert event.activity is None
    assert event.root_record_index is None


def test_valid_shaped_absent_assertions_are_structured_not_found(tmp_path):
    queries = kernel.ModelQueries(world(tmp_path).load())
    for record_id in ("srg_" + "f" * 64, "std_" + "f" * 64,
                      "stw_" + "f" * 64):
        result = queries.state_assertion(record_id)
        assert (result.lookup_status, result.record_index, result.activity,
                result.containing_lineage_health,
                result.containing_subject_conclusion,
                result.containing_agreement_findings,
                result.root_record_index, result.successor_indices,
                result.withdrawal_indices) == (
                    "not_found", None, None, None, None, None, None, (), ())


def test_every_explicit_pre_st_membership_returns_structured_absence():
    store = kernel.ModelStore(DEMO_MODEL)
    histories = (
        PRE_VARIABLE_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
        VS001_MEMBERSHIP, PRE_ES001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
        CN001_MEMBERSHIP, PT001_MEMBERSHIP, VP001_MEMBERSHIP,
        BH001_MEMBERSHIP,
    )
    for membership in histories:
        loaded = store.replay(membership)
        queries = kernel.ModelQueries(loaded)
        assert queries.state(STATE_A).status == "not_registered"
        declaration = queries.state_declaration(
            STATE_A, context=AS_OPERATED)
        assert declaration.conclusion == "not_registered"
        assert declaration.roots == ()
        assert queries.state_assertion(
            "std_" + "f" * 64).lookup_status == "not_found"
    current = kernel.ModelQueries(store.replay(BH001_MEMBERSHIP))
    assert current.states_of_entity(
        "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50",
        context=AS_OPERATED).entries == ()


def test_historical_membership_omitting_successor_or_withdrawal_revives_tip(
        tmp_path):
    registration = state_registration()
    root = state_declaration(registration, note="root")
    child = state_declaration(
        registration, supersedes=(root.record_id,), recorded_at=T1,
        note="child")
    withdrawal = state_withdrawal(child)
    store = world(tmp_path, root, child, withdrawal)
    full = kernel.ModelQueries(store.load()).state_declaration(
        STATE_A, context=AS_OPERATED)
    assert full.conclusion == "inactive"

    without_withdrawal = tuple(
        record_id for record_id in store.load().revision.record_ids
        if record_id != withdrawal.record_id)
    revived_child = kernel.ModelQueries(store.replay(without_withdrawal)
                                        ).state_assertion(child.record_id)
    assert revived_child.activity == "current"

    without_child_or_withdrawal = tuple(
        record_id for record_id in without_withdrawal
        if record_id != child.record_id)
    revived_root = kernel.ModelQueries(store.replay(
        without_child_or_withdrawal)).state_assertion(root.record_id)
    assert revived_root.activity == "current"
