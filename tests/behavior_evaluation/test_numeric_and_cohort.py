"""Exact public CN-parser parity and five-field cohort scheduling."""

from decimal import ROUND_CEILING, ROUND_FLOOR, getcontext

import pytest

from backend.behavior_evaluation import BehaviorEvaluationResult
from backend.behavior_evaluation.derivation import derive_evaluation
from backend.constraint_evaluation import NumericParityBreachError
from backend.semantic_compatibility import VariableSemanticCompatibilityResult

from tests.behavior_evaluation.helpers import evaluate


def _replace_all(value, key, replacement):
    if isinstance(value, dict):
        return {name: (replacement if name == key else
                       _replace_all(item, key, replacement))
                for name, item in value.items()}
    if isinstance(value, list):
        return [_replace_all(item, key, replacement) for item in value]
    if isinstance(value, tuple):
        return tuple(_replace_all(item, key, replacement) for item in value)
    return value


def _rebuild_with_lexemes(result, left, right):
    semantics = []
    for semantic, lexeme in zip(
            result.participant_semantic_results, (left, right), strict=True):
        payload = _replace_all(
            semantic.model_dump(mode="python"), "value_json", lexeme)
        semantics.append(VariableSemanticCompatibilityResult.model_validate(payload))
    semantics = tuple(semantics)
    derived = derive_evaluation(
        behavior=result.behavior,
        behavior_anchor_id=result.behavior_anchor_id,
        context=result.context,
        as_of=result.as_of,
        participant_sources=result.participant_sources,
        semantic_results=semantics,
    )
    return BehaviorEvaluationResult(
        behavior=result.behavior,
        behavior_anchor_id=result.behavior_anchor_id,
        context=result.context,
        as_of=result.as_of,
        participant_sources=result.participant_sources,
        participant_semantic_results=semantics,
        **derived,
    )


BOUNDARY_TWINS = (
    ("1" + " " * 511, "1" + " " * 512),
    ("1" * 256, "1" * 257),
    ("0." + "1" * 128, "0." + "1" * 129),
    ("1e0000", "1e00000"),
    ("0e1024", "0e1025"),
    ("1e383", "1e384"),
    ("1e-384", "1e-385"),
    ("-1e-383", "-1e-384"),
)


@pytest.mark.parametrize("admitted,over", BOUNDARY_TWINS)
def test_every_inherited_cn_boundary_has_admitted_and_one_over_twin(
        tmp_path, admitted, over):
    baseline = evaluate(tmp_path)
    accepted = _rebuild_with_lexemes(baseline, admitted, admitted)
    assert accepted.execution == "executed"
    assert accepted.computed_relation == "equal"
    refused = _rebuild_with_lexemes(baseline, over, "0")
    assert refused.participants[0].numeric_admission == "out_of_bounds"
    assert "numeric_value_out_of_bounds" in (
        refused.participants[0].refusal_reasons)
    assert refused.computed_relation is None


@pytest.mark.parametrize("rounding", [ROUND_CEILING, ROUND_FLOOR])
def test_ambient_decimal_context_cannot_change_equality(tmp_path, rounding):
    baseline = evaluate(tmp_path)
    original = getcontext().copy()
    try:
        getcontext().prec = 1
        getcontext().rounding = rounding
        result = _rebuild_with_lexemes(baseline, "1.00", "1e0")
    finally:
        getcontext().prec = original.prec
        getcontext().rounding = original.rounding
    assert result.execution == "executed"
    assert result.computed_relation == "equal"
    assert tuple(row.canonical_decimal for row in result.participants) == (
        "1", "1")


def test_exact_five_field_cohort_mismatch_is_not_mathematical_difference(tmp_path):
    result = evaluate(tmp_path)
    semantics = list(result.participant_semantic_results)
    payload = _replace_all(
        semantics[1].model_dump(mode="python"), "attempt_id", "f" * 32)
    semantics[1] = VariableSemanticCompatibilityResult.model_validate(payload)
    semantics = tuple(semantics)
    derived = derive_evaluation(
        behavior=result.behavior, behavior_anchor_id=result.behavior_anchor_id,
        context=result.context, as_of=result.as_of,
        participant_sources=result.participant_sources,
        semantic_results=semantics)
    rebuilt = BehaviorEvaluationResult(
        behavior=result.behavior, behavior_anchor_id=result.behavior_anchor_id,
        context=result.context, as_of=result.as_of,
        participant_sources=result.participant_sources,
        participant_semantic_results=semantics, **derived)
    assert rebuilt.cohort_admission == "different_acquisition_cohort"
    assert rebuilt.execution == "not_executed"
    assert rebuilt.computed_relation is None
    assert rebuilt.not_executed_reasons[-1].reason == (
        "acquisition_cohort_mismatch")
    assert all(row.numeric_admission == "not_evaluated"
               for row in rebuilt.participants)


def test_parser_parity_breach_propagates_and_never_becomes_different(tmp_path):
    baseline = evaluate(tmp_path)
    with pytest.raises(NumericParityBreachError) as error:
        _rebuild_with_lexemes(baseline, "NaN", "60")
    assert error.value.error_code == "NUMERIC_PARITY_BREACH"


def test_parser_runs_for_both_numeric_eligible_participants_before_parity_raise(
        tmp_path, monkeypatch):
    import backend.behavior_evaluation.derivation as derivation

    baseline = evaluate(tmp_path)
    original = derivation.parse_observed_decimal
    calls = []
    sentinel = NumericParityBreachError(
        "NUMERIC_PARITY_BREACH", "synthetic scheduled parity breach")

    def parser(lexeme):
        calls.append(lexeme)
        if len(calls) == 1:
            raise sentinel
        return original(lexeme)

    monkeypatch.setattr(derivation, "parse_observed_decimal", parser)
    with pytest.raises(NumericParityBreachError) as error:
        derive_evaluation(
            behavior=baseline.behavior,
            behavior_anchor_id=baseline.behavior_anchor_id,
            context=baseline.context,
            as_of=baseline.as_of,
            participant_sources=baseline.participant_sources,
            semantic_results=baseline.participant_semantic_results)
    assert error.value is sentinel
    assert calls == ["60.1", "60.0"]


def test_cohort_mismatch_suppresses_every_parser_call(tmp_path, monkeypatch):
    import backend.behavior_evaluation.derivation as derivation

    baseline = evaluate(tmp_path)
    semantics = list(baseline.participant_semantic_results)
    payload = _replace_all(
        semantics[1].model_dump(mode="python"), "raw_record_id", "e" * 32)
    semantics[1] = VariableSemanticCompatibilityResult.model_validate(payload)
    calls = []

    def forbidden(lexeme):
        calls.append(lexeme)
        raise AssertionError("cohort refusal must precede numeric parsing")

    monkeypatch.setattr(derivation, "parse_observed_decimal", forbidden)
    derived = derive_evaluation(
        behavior=baseline.behavior,
        behavior_anchor_id=baseline.behavior_anchor_id,
        context=baseline.context,
        as_of=baseline.as_of,
        participant_sources=baseline.participant_sources,
        semantic_results=tuple(semantics))
    assert derived["cohort_admission"] == "different_acquisition_cohort"
    assert calls == []


def test_coherent_lower_content_mutation_is_inside_lower_boundary_not_raw_auth(
        tmp_path):
    baseline = evaluate(tmp_path)
    mutated = _rebuild_with_lexemes(baseline, "60", "60")
    assert mutated.execution == "executed"
    assert mutated.computed_relation == "equal"
    assert mutated.participant_semantic_results != (
        baseline.participant_semantic_results)
