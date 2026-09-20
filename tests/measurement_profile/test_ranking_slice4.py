import pytest

from applications.bounded_decision_workflow.measurement_ranking import (
    MeasurementRankingError,
    rank_measurements,
)


def candidate(identifier, branches, status="complete"):
    return {"id": identifier, "status": status, "branches": branches}


def test_one_measurement_discriminates_two_hypotheses_and_preserves_empty_branch():
    result = rank_measurements(("H1", "H2"), [candidate("T1", [
        {"outcome": "a", "survivors": ["H1"]},
        {"outcome": "b", "survivors": ["H2"]},
        {"outcome": "empty", "survivors": []},
    ])])
    assert result.disposition == "ranked"
    assert result.best == ("T1",)
    assert result.scores[0].worst_survivors == 1
    assert result.scores[0].reduction == 1
    assert () in result.scores[0].survivor_multiset


def test_ties_and_equal_scores_do_not_imply_multiset_equivalence():
    result = rank_measurements(("H1", "H2"), [
        candidate("T1", [{"outcome": "a", "survivors": ["H1"]},
                           {"outcome": "b", "survivors": ["H2"]}]),
        candidate("T2", [{"outcome": "a", "survivors": ["H2"]},
                           {"outcome": "b", "survivors": ["H1"]}]),
    ])
    assert result.best == ("T1", "T2")
    assert result.scores[0].worst_survivors == result.scores[1].worst_survivors
    assert result.scores[0].survivor_multiset == result.scores[1].survivor_multiset

    unequal = rank_measurements(("H1", "H2", "H3"), [
        candidate("T1", [{"outcome": "a", "survivors": ["H1", "H2"]},
                           {"outcome": "b", "survivors": ["H3"]}]),
        candidate("T2", [{"outcome": "a", "survivors": ["H1"]},
                           {"outcome": "b", "survivors": ["H2", "H3"]}]),
    ])
    assert unequal.scores[0].worst_survivors == unequal.scores[1].worst_survivors
    assert unequal.scores[0].survivor_multiset != unequal.scores[1].survivor_multiset


def test_withholding_is_whole_set_and_does_not_prune_incomplete_candidate():
    result = rank_measurements(("H1", "H2"), [
        candidate("T1", [{"outcome": "a", "survivors": ["H1"]}]),
        candidate("T2", [{"outcome": "a", "survivors": ["H1"]}], status="conflicting"),
    ])
    assert result.disposition == "withheld"
    assert result.best is None
    assert result.scores == ()
    assert result.reason.startswith("whole_nominated_set_withheld")


def test_zero_cardinality_and_permutation_invariance():
    assert rank_measurements((), []).reason == "zero_hypotheses"
    assert rank_measurements(("H1",), []).reason == "zero_measurements"
    left = rank_measurements(("H2", "H1"), [candidate("T2", [{"outcome": "b", "survivors": ["H2"]}]),
                                               candidate("T1", [{"outcome": "a", "survivors": ["H1"]}])])
    right = rank_measurements(("H1", "H2"), [candidate("T1", [{"outcome": "a", "survivors": ["H1"]}]),
                                                candidate("T2", [{"outcome": "b", "survivors": ["H2"]}])])
    assert left == right


def test_bypass_like_survivors_are_test_data_only_and_nonnominated_ids_reject():
    with pytest.raises(MeasurementRankingError) as error:
        rank_measurements(("H1", "H2"), [candidate("T1", [
            {"outcome": "a", "survivors": ["H1", "H3"]}])])
    assert error.value.code == "SURVIVOR_NOT_NOMINATED"
