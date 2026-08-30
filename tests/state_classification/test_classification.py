"""ST-001 Slice C scheduling, lifecycle gates, and all-of truth."""

import pytest

from backend.state_classification import (
    StateClassificationInputError,
    StateConditionSource,
)
from tests.model_kernel.builders import CON_A, CON_B
from tests.model_kernel.st001_slice_a_helpers import AS_DESIGNED, STATE_B
from tests.state_classification.helpers import (
    AS_OF,
    AS_OPERATED,
    classify,
    condition_sources,
    conflicted_model,
    facade,
    inactive_model,
    state_model,
)


def test_all_satisfied_matches_and_reversed_sources_canonicalize(tmp_path):
    model, _, _ = state_model(tmp_path)
    direct = classify(tmp_path, model=model)
    reversed_result = classify(
        tmp_path, model=model, sources=condition_sources(reverse=True))
    assert direct == reversed_result
    assert direct.ruleset_version == "st001.1"
    assert tuple(row.constraint_anchor_id for row in direct.condition_sources) == (
        CON_A, CON_B)
    assert tuple(row.declaration_alignment for row in direct.conditions) == (
        "exact_current", "exact_current")
    assert tuple(row.outcome for row in direct.conditions) == (
        "satisfied", "satisfied")
    assert (direct.condition_coverage, direct.temporal_alignment,
            direct.execution, direct.refusals, direct.computed_match) == (
                "complete", "not_asserted", "executed", (), "matches")


def test_one_violation_does_not_match_without_claiming_another_state(tmp_path):
    model, _, _ = state_model(tmp_path, upper_a="50")
    result = classify(tmp_path, model=model)
    assert tuple(row.outcome for row in result.conditions) == (
        "violated", "satisfied")
    assert (result.condition_coverage, result.execution,
            result.computed_match) == (
                "complete", "executed", "does_not_match")
    assert not hasattr(result, "matched_state_anchor_ids")
    assert not hasattr(result, "current_state")


@pytest.mark.parametrize("world,conclusion,reason", [
    ("not_declared", "not_declared", "state_not_declared"),
    ("inactive", "inactive", "state_inactive"),
    ("conflicted", "conflicted", "state_conflicted"),
])
def test_registered_lifecycle_refusal_still_carries_every_cn_branch(
        tmp_path, world, conclusion, reason):
    if world == "not_declared":
        model, _, _ = state_model(tmp_path, declaration_records=())
    elif world == "inactive":
        model, _ = inactive_model(tmp_path)
    else:
        model, _ = conflicted_model(tmp_path)
    result = classify(tmp_path, model=model)
    assert result.state.conclusion == conclusion
    assert len(result.constraint_evaluations) == len(result.conditions) == 2
    assert tuple(row.declaration_alignment for row in result.conditions) == (
        "not_evaluated", "not_evaluated")
    assert tuple(row.outcome for row in result.conditions) == (
        "not_evaluated", "not_evaluated")
    assert (result.condition_coverage, result.temporal_alignment,
            result.execution, result.computed_match) == (
                "not_evaluated", "not_asserted", "not_executed", None)
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        (reason, None)]


def test_unregistered_state_requires_empty_sources_and_invokes_no_cn(
        tmp_path, monkeypatch):
    model, _, _ = state_model(tmp_path, include_registration=False,
                              declaration_records=())
    queries = facade(tmp_path, model=model)
    calls = []
    monkeypatch.setattr(
        queries.constraints, "constraint_evaluation",
        lambda *args, **kwargs: calls.append((args, kwargs)))
    result = queries.state_classification(
        STATE_B, context=AS_OPERATED, as_of=AS_OF, condition_sources=())
    assert result.state.conclusion == "not_registered"
    assert result.constraint_evaluations == result.conditions == ()
    assert (result.condition_coverage, result.temporal_alignment,
            result.execution, result.computed_match) == (
                "not_evaluated", "not_evaluated", "not_executed", None)
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        ("state_not_registered", None)]
    assert calls == []
    with pytest.raises(StateClassificationInputError):
        queries.state_classification(
            STATE_B, context=AS_OPERATED, as_of=AS_OF,
            condition_sources=condition_sources())


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate"])
def test_registered_state_requires_exact_condition_source_set(tmp_path, mutation):
    model, _, _ = state_model(tmp_path)
    rows = list(condition_sources())
    if mutation == "missing":
        rows.pop()
    elif mutation == "extra":
        rows.append(StateConditionSource(
            constraint_anchor_id="con_" + "c" * 32,
            source=rows[0].source))
    else:
        rows[1] = rows[0]
    with pytest.raises(StateClassificationInputError):
        classify(tmp_path, model=model, sources=tuple(rows))


def test_context_changes_state_lifecycle_without_selecting_model_or_cn(tmp_path):
    model, _, _ = state_model(tmp_path)
    operated = classify(tmp_path, model=model)
    designed = classify(tmp_path, model=model, context=AS_DESIGNED)
    assert operated.state.material.revision == designed.state.material.revision
    assert tuple(item.model_dump_json()
                 for item in operated.constraint_evaluations) == tuple(
                     item.model_dump_json()
                     for item in designed.constraint_evaluations)
    assert operated.computed_match == "matches"
    assert designed.computed_match is None
    assert designed.refusals[0].reason == "state_not_declared"
