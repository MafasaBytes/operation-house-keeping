"""FM-001 Slice A owner-review integrity repairs R1 and R2."""

from typing import get_args

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.test_flow_measurement_slice_a import (
    AS_DESIGNED,
    FLOW_A,
    PORT_A,
    VAR_A,
    association,
    foundation,
    semantic,
    snapshot,
    store_with,
    withdrawal,
)


def _two_bodies():
    records, support = foundation()
    alternate_vsm = semantic(note="alternate exact measured-actual support")
    alternate_support = (*support[:-1], alternate_vsm)
    return (*records, alternate_vsm), support, alternate_support


def _subject(orientation="aligned"):
    return (
        FLOW_A,
        VAR_A,
        PORT_A,
        AS_DESIGNED,
        "direct_measurement_relevance",
        orientation,
    )


def test_r1_one_conflicted_root_is_not_cross_root_disagreement():
    records, support, alternate_support = _two_bodies()
    root = association(support, note="one root")
    left = association(
        support, supersedes=(root.record_id,), note="body one")
    right = association(
        alternate_support, supersedes=(root.record_id,), note="body two")
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (*records, root, left, right)},
    )
    assert len(loaded.current_flow_measurement_tips_by_root[root.record_id]) == 2
    assert len({
        loaded.flow_measurement_effective_body_by_id[row.record_id]
        for row in loaded.current_flow_measurement_tips_by_root[root.record_id]
    }) == 2
    assert _subject() not in \
        loaded.flow_measurement_disagreeing_root_ids_by_subject


def test_r1_one_active_and_one_inactive_root_do_not_disagree():
    records, support, alternate_support = _two_bodies()
    active = association(support, note="active")
    inactive = association(alternate_support, note="inactive")
    event = withdrawal(inactive)
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (
            *records, active, inactive, event)},
    )
    assert loaded.current_flow_measurement_tips_by_root[active.record_id] == (
        active,)
    assert loaded.current_flow_measurement_tips_by_root[inactive.record_id] == ()
    assert _subject() not in \
        loaded.flow_measurement_disagreeing_root_ids_by_subject


def test_r1_two_active_singleton_roots_with_different_bodies_disagree():
    records, support, alternate_support = _two_bodies()
    first = association(support, note="first active root")
    second = association(alternate_support, note="second active root")
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (*records, first, second)},
    )
    assert loaded.flow_measurement_disagreeing_root_ids_by_subject[
        _subject()] == tuple(sorted((first.record_id, second.record_id)))


def test_r1_equal_body_sets_do_not_disagree_despite_internal_conflict():
    records, support, alternate_support = _two_bodies()
    first = association(support, note="first root")
    first_a = association(
        support, supersedes=(first.record_id,), note="first A")
    first_b = association(
        alternate_support, supersedes=(first.record_id,), note="first B")
    second = association(support, note="second root")
    second_a = association(
        support, supersedes=(second.record_id,), note="second A")
    second_b = association(
        alternate_support, supersedes=(second.record_id,), note="second B")
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (
            *records, first, first_a, first_b, second, second_a, second_b)},
    )
    body_sets = {
        root: frozenset(
            loaded.flow_measurement_effective_body_by_id[tip.record_id]
            for tip in loaded.current_flow_measurement_tips_by_root[root]
        )
        for root in (first.record_id, second.record_id)
    }
    assert body_sets[first.record_id] == body_sets[second.record_id]
    assert _subject() not in \
        loaded.flow_measurement_disagreeing_root_ids_by_subject


def test_r1_mixed_roots_index_only_active_unequal_participants():
    records, support, alternate_support = _two_bodies()
    first = association(support, note="active body A")
    second = association(alternate_support, note="active body B")
    inactive = association(support, note="inactive third root")
    event = withdrawal(inactive)
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (
            *records, first, second, inactive, event)},
    )
    assert loaded.flow_measurement_disagreeing_root_ids_by_subject[
        _subject()] == tuple(sorted((first.record_id, second.record_id)))


ORIENTATIONS = (
    "aligned",
    "opposite",
    "unsigned_magnitude",
    "not_applicable",
)


def test_r2_all_four_orientations_build_store_index_reconstruct_and_replay(
        tmp_path):
    store, support = store_with(tmp_path)
    claims = tuple(
        association(support, orientation=value, note="orientation witness")
        for value in ORIENTATIONS
    )
    assert get_args(
        kernel.FlowMeasurementAssociation.model_fields[
            "orientation"].annotation) == ORIENTATIONS
    assert len({claim.record_id for claim in claims}) == 4

    for expected, claim in zip(ORIENTATIONS, claims, strict=True):
        rebuilt = kernel.FlowMeasurementAssociation.model_validate(
            claim.model_dump(mode="python", warnings=False))
        assert rebuilt == claim
        assert rebuilt.orientation == expected
        store.append(claim)

    loaded = store.load()
    replayed = store.replay(reversed(loaded.revision.record_ids))
    for expected, claim in zip(ORIENTATIONS, claims, strict=True):
        assert loaded.flow_measurement_ids_by_subject[_subject(expected)] == (
            claim.record_id,)
        assert replayed.flow_measurement_ids_by_subject[
            _subject(expected)] == (claim.record_id,)


@pytest.mark.parametrize("orientation", ORIENTATIONS[1:])
def test_r2_cross_orientation_supersession_refuses_before_write(
        tmp_path, orientation):
    store, support = store_with(tmp_path)
    root = association(support, orientation="aligned", note="root")
    store.append(root)
    before = snapshot(store)
    attack = association(
        support,
        orientation=orientation,
        supersedes=(root.record_id,),
        note="orientation drift",
    )
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(attack)
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_LINEAGE_INVALID"
    assert snapshot(store) == before


def test_r2_invalid_orientation_forms_still_refuse_with_valid_twin():
    _, support = foundation()

    class OrientationSubclass(str):
        pass

    for invalid in (
        None,
        True,
        False,
        "",
        "unknown",
        "Aligned",
        "UNSIGNED_MAGNITUDE",
        "not-applicable",
        OrientationSubclass("aligned"),
    ):
        with pytest.raises(kernel.ModelIntegrityError):
            association(support, orientation=invalid)
    assert association(support, orientation="not_applicable").orientation == \
        "not_applicable"
