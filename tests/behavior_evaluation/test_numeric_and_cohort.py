"""Exact public CN-parser parity and five-field cohort scheduling."""

from datetime import timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, getcontext

import pytest

from backend.behavior_evaluation import BehaviorEvaluationResult
from backend.behavior_evaluation.derivation import derive_evaluation
from backend.behavior_evaluation.derivation import _cohort_key
from backend.constraint_evaluation import NumericParityBreachError
from backend.semantic_compatibility import VariableSemanticCompatibilityResult

from tests.behavior_evaluation.helpers import evaluate
from tests.behavior_evaluation.helpers import (
    E1, PROP_TARGET, PROP_TEMP, VAR_A, VAR_B, interpretation_resolver,
    model_store, semantic_queries,
)
from tests.model_kernel.bh001_slice_a_helpers import (
    behavior_declaration, behavior_registration, semantic_lock,
)
from tests.model_state.helpers import (
    entity_declaration, prop_assertion, var_declaration,
)


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


def test_each_included_cohort_field_is_identity_bearing(tmp_path):
    result = evaluate(tmp_path)
    occurrence = (result.participant_semantic_results[0].candidates[0]
                  .value_candidate.state_candidate.bound.observed.occurrence)
    different_subject_source = occurrence.subject.model_copy(
        update={"source_id": "other-source"})
    different_subject_adapter = occurrence.subject.model_copy(
        update={"adapter_id": "other-adapter"})
    mutations = (
        {"subject": different_subject_source},
        {"subject": different_subject_adapter},
        {"attempt_id": "f" * len(occurrence.attempt_id)},
        {"raw_record_id": "e" * len(occurrence.raw_record_id)},
        {"payload_checksum": "d" * len(occurrence.payload_checksum)},
    )
    for update in mutations:
        assert _cohort_key(occurrence.model_copy(update=update)) != (
            _cohort_key(occurrence))


def test_every_declared_noncohort_field_is_excluded(tmp_path):
    result = evaluate(tmp_path)
    occurrence = (result.participant_semantic_results[0].candidates[0]
                  .value_candidate.state_candidate.bound.observed.occurrence)
    subject = occurrence.subject.model_copy(
        update={"subject_identifier": "other-subject"})
    prop = occurrence.property.model_copy(
        update={"json_pointer": "/synthetic/other"})
    later = occurrence.received_at + timedelta(seconds=1)
    updates = (
        {"subject": subject}, {"property": prop},
        {"occurrence_id": "e" * len(occurrence.occurrence_id)},
        {"observation_id": "d" * len(occurrence.observation_id)},
        {"attempt_started_at": later}, {"received_at": later},
        {"finished_at": later}, {"source_time": None},
        {"clock_segment_id": None}, {"ingestion_run_id": "other-run"},
        {"sweep_position": occurrence.sweep_position + 1},
        {"value_json": "999"}, {"declared_unit": "other"},
        {"change_class": "changed"},
        {"quality_flags": ("synthetic_noncohort",)},
    )
    expected = _cohort_key(occurrence)
    for update in updates:
        assert _cohort_key(occurrence.model_copy(update=update)) == expected


def test_cutoff_changes_staleness_not_model_or_behavior(tmp_path):
    first = evaluate(tmp_path / "first")
    later = first.as_of + timedelta(hours=2)
    second = evaluate(tmp_path / "second", as_of=later)
    assert first.behavior == second.behavior
    assert (first.behavior.material.revision
            == second.behavior.material.revision)
    first_staleness = (first.participant_semantic_results[0]
                       .value_compatibility.state.candidates[0]
                       .bound.observed.staleness_seconds)
    second_staleness = (second.participant_semantic_results[0]
                        .value_compatibility.state.candidates[0]
                        .bound.observed.staleness_seconds)
    assert second_staleness > first_staleness
    assert first.computed_relation == second.computed_relation == "different"


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


@pytest.mark.parametrize("lexeme", ["true", '"text"', "[1]", '{"a":1}', "null"])
def test_known_nonnumeric_shapes_never_reach_parser(tmp_path, monkeypatch, lexeme):
    import backend.behavior_evaluation.derivation as derivation
    from tests.observation_compatibility.helpers import observed_value

    temporal = observed_value(tmp_path, lexeme)
    original = derivation.parse_observed_decimal
    calls = []

    def parser(value):
        calls.append(value)
        return original(value)

    monkeypatch.setattr(derivation, "parse_observed_decimal", parser)
    result = evaluate(tmp_path, temporal=temporal)
    # One authoritative derivation builds the payload and one reconstructs it
    # at the public result boundary. The nonnumeric participant is absent from
    # both schedules.
    assert calls == ["60.0", "60.0"]
    expected = ("numeric_value_absent" if lexeme == "null"
                else "numeric_value_shape_mismatch")
    assert expected in result.participants[0].refusal_reasons
    if lexeme != "null":
        assert "numeric_value_absent" not in (
            result.participants[0].refusal_reasons)
    assert result.participants[0].numeric_admission == "not_evaluated"
    assert result.computed_relation is None


@pytest.mark.parametrize("left,right", [
    ("60.4", "60.40"), ("60.4", "6.04e1"),
    ("-0", "-0.0"), ("0E+99", "0"),
])
def test_equivalent_spellings_and_negative_zero_are_exactly_equal(
        tmp_path, left, right):
    result = _rebuild_with_lexemes(evaluate(tmp_path), left, right)
    assert result.execution == "executed"
    assert result.computed_relation == "equal"


def test_first_out_of_bounds_cannot_hide_second_parity_failure(
        tmp_path, monkeypatch):
    import backend.behavior_evaluation.derivation as derivation

    baseline = evaluate(tmp_path)
    original = derivation.parse_observed_decimal
    calls = []

    def parser(value):
        calls.append(value)
        return original(value)

    monkeypatch.setattr(derivation, "parse_observed_decimal", parser)
    with pytest.raises(NumericParityBreachError):
        _rebuild_with_lexemes(baseline, "1" * 257, "NaN")
    assert calls == ["1" * 257, "NaN"]


def _parser_calls(monkeypatch):
    import backend.behavior_evaluation.derivation as derivation

    original = derivation.parse_observed_decimal
    calls = []

    def parser(value):
        calls.append(value)
        return original(value)

    monkeypatch.setattr(derivation, "parse_observed_decimal", parser)
    return calls


def test_model_unit_absence_excludes_only_that_participant_from_parser(
        tmp_path, monkeypatch):
    from backend.model_kernel import UnitNotDeclared

    model = model_store(tmp_path, specification_overrides={
        VAR_A: {"unit": UnitNotDeclared(kind="not_declared")}})
    calls = _parser_calls(monkeypatch)
    result = evaluate(tmp_path, model=model)
    assert calls == ["60.0", "60.0"]
    assert "model_unit_not_available" in (
        result.participants[0].refusal_reasons)
    assert result.cohort_admission == "same_acquisition_cohort"


def test_one_present_and_one_absent_occurrence_never_invents_a_cohort(tmp_path):
    from backend.behavior_evaluation import BehaviorParticipantSource
    from backend.model_state import SourceSelector

    first, second = __import__(
        "tests.behavior_evaluation.helpers",
        fromlist=["participant_sources"]).participant_sources()
    absent_property = second.source.property.model_copy(
        update={"json_pointer": "/synthetic/not-present"})
    absent = BehaviorParticipantSource(
        variable_anchor_id=second.variable_anchor_id,
        entity_anchor_id=second.entity_anchor_id,
        source=SourceSelector(
            subject=second.source.subject, property=absent_property))
    result = evaluate(tmp_path, participants=(first, absent))
    assert result.participants[0].observation_availability == "observed"
    assert result.participants[1].observation_availability == (
        "none_before_cutoff")
    assert result.cohort_admission == "not_evaluated"


def test_attachment_refusal_does_not_hide_numeric_parser(tmp_path, monkeypatch):
    bindings = (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_B, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    semantic = semantic_queries(tmp_path, binding_records=bindings)
    calls = _parser_calls(monkeypatch)
    result = evaluate(tmp_path, semantic=semantic)
    assert calls == ["60.1", "60.0", "60.1", "60.0"]
    assert "observation_not_attached" in (
        result.participants[0].refusal_reasons)


def test_source_semantic_refusal_does_not_hide_numeric_parser(
        tmp_path, monkeypatch):
    from tests.model_kernel.builders import quantity_kind

    resolver = interpretation_resolver(tmp_path, overrides={
        PROP_TEMP: {"quantity_kind": quantity_kind(code="other_quantity")}})
    semantic = semantic_queries(tmp_path, interpretations=resolver)
    calls = _parser_calls(monkeypatch)
    result = evaluate(tmp_path, semantic=semantic)
    assert calls == ["60.1", "60.0", "60.1", "60.0"]
    assert "source_semantics_not_admitted" in (
        result.participants[0].refusal_reasons)


def test_lock_refusal_does_not_hide_numeric_parser(tmp_path, monkeypatch):
    registration = behavior_registration(owners=(E1, E1))
    declaration = behavior_declaration(registration, locks=(
        semantic_lock(VAR_A, quantity="other_quantity"),
        semantic_lock(VAR_B, quantity="other_quantity", role="reported"),
    ))
    model = model_store(tmp_path, declaration_records=(declaration,))
    calls = _parser_calls(monkeypatch)
    result = evaluate(tmp_path, model=model)
    assert calls == ["60.1", "60.0", "60.1", "60.0"]
    assert "quantity_kind_lock_mismatch" in (
        result.participants[0].refusal_reasons)


def test_bh_uses_the_exact_public_cn_parser_object():
    import backend.behavior_evaluation.derivation as derivation
    from backend.constraint_evaluation import parse_observed_decimal

    assert derivation.parse_observed_decimal is parse_observed_decimal


def test_coherent_lower_content_mutation_is_inside_lower_boundary_not_raw_auth(
        tmp_path):
    baseline = evaluate(tmp_path)
    mutated = _rebuild_with_lexemes(baseline, "60", "60")
    assert mutated.execution == "executed"
    assert mutated.computed_relation == "equal"
    assert mutated.participant_semantic_results != (
        baseline.participant_semantic_results)
