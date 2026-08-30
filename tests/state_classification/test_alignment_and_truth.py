"""Exact VCN-pin alignment and bounded all-of truth-table coverage."""

from datetime import timedelta

from tests.model_kernel.builders import (
    CON_A,
    constraint_declaration,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import T0
from tests.state_classification.helpers import (
    classify,
    custom_state_model,
    reported_constraint_declaration,
)


def test_unique_current_vcn_different_from_pin_is_superseded(tmp_path):
    original = constraint_declaration(CON_A, predicate=upper_bound("80"))
    correction = constraint_declaration(
        CON_A, predicate=upper_bound("90"),
        supersedes=(original.record_id,), recorded_at=T0 + timedelta(hours=1))
    second = reported_constraint_declaration()
    model, _ = custom_state_model(
        tmp_path,
        declarations_a=(original, correction), declarations_b=(second,),
        pinned_a=original, pinned_b=second)
    result = classify(tmp_path, model=model)
    assert tuple(row.declaration_alignment for row in result.conditions) == (
        "superseded", "exact_current")
    assert tuple(row.outcome for row in result.conditions) == (
        "not_evaluated", "satisfied")
    assert (result.condition_coverage, result.execution,
            result.computed_match) == ("incomplete", "not_executed", None)
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        ("condition_declaration_superseded", 0)]


def test_identical_parentless_current_vcns_remain_strict_cn_conflict(tmp_path):
    first = constraint_declaration(
        CON_A, predicate=upper_bound("80"), note="first authority")
    second = constraint_declaration(
        CON_A, predicate=upper_bound("80"),
        recorded_at=T0 + timedelta(hours=1), note="second authority")
    other = reported_constraint_declaration()
    model, _ = custom_state_model(
        tmp_path,
        declarations_a=(first, second), declarations_b=(other,),
        pinned_a=first, pinned_b=other)
    result = classify(tmp_path, model=model)
    assert result.constraint_evaluations[0].constraint.status == "conflicted"
    assert len(result.constraint_evaluations[0].constraint.conflicting_declarations) == 2
    assert result.conditions[0].declaration_alignment == "conflicted"
    assert result.conditions[0].outcome == "not_evaluated"
    assert (result.condition_coverage, result.execution,
            result.computed_match) == ("incomplete", "not_executed", None)
    assert ("condition_declaration_conflicted", 0) in {
        (item.reason, item.condition_index) for item in result.refusals}


def test_no_violation_plus_unknown_is_incomplete_and_not_executed(tmp_path):
    first = constraint_declaration(CON_A, predicate=upper_bound("80"))
    # The model observation role for the second variable is ``reported``;
    # this default ``measured`` lock makes CN honestly not_evaluated.
    unknown = constraint_declaration(CON_A.replace("a", "b"),
                                     predicate=upper_bound("80"))
    model, _ = custom_state_model(
        tmp_path, declarations_a=(first,), declarations_b=(unknown,),
        pinned_a=first, pinned_b=unknown)
    result = classify(tmp_path, model=model)
    assert tuple(row.outcome for row in result.conditions) == (
        "satisfied", "not_evaluated")
    assert (result.condition_coverage, result.execution,
            result.computed_match) == ("incomplete", "not_executed", None)
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        ("condition_evaluation_not_evaluated", 1)]


def test_false_conjunct_determines_all_of_despite_unknown_sibling(tmp_path):
    violated = constraint_declaration(CON_A, predicate=upper_bound("50"))
    unknown = constraint_declaration(CON_A.replace("a", "b"),
                                     predicate=upper_bound("80"))
    model, _ = custom_state_model(
        tmp_path, declarations_a=(violated,), declarations_b=(unknown,),
        pinned_a=violated, pinned_b=unknown)
    result = classify(tmp_path, model=model)
    assert tuple(row.outcome for row in result.conditions) == (
        "violated", "not_evaluated")
    assert (result.condition_coverage, result.execution,
            result.computed_match) == (
                "incomplete", "executed", "does_not_match")
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        ("condition_evaluation_not_evaluated", 1)]
