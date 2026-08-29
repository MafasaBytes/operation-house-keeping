"""BH-001 lifecycle, evidence, cohort, and exact-comparison behavior."""

from backend.model_kernel import ModelQueries
from backend.semantic_compatibility import SemanticCompatibilityConfigurationError

from tests.behavior_evaluation.helpers import (
    AS_BUILT,
    AS_DESIGNED,
    AS_OF,
    BEHAVIOR_A,
    VAR_A,
    VAR_B,
    evaluate,
    model_store,
    participant_sources,
    semantic_queries,
)


def test_exact_equal_world_executes_and_carries_direct_results_once(tmp_path):
    semantic = semantic_queries(tmp_path)
    from backend.behavior_evaluation import BehaviorEvaluationQueries

    result = BehaviorEvaluationQueries(semantic).behavior_evaluation(
        BEHAVIOR_A, context=AS_DESIGNED, as_of=AS_OF,
        participants=participant_sources(reverse=True))
    direct_behavior = ModelQueries(
        semantic.compatibility.state.model).behavior_declaration(
            BEHAVIOR_A, context=AS_DESIGNED)
    direct_semantics = tuple(
        semantic.variable_semantic_compatibility(
            source.variable_anchor_id, as_of=AS_OF,
            entity_anchor_id=source.entity_anchor_id, source=source.source)
        for source in result.participant_sources)
    assert result.behavior == direct_behavior
    assert result.participant_semantic_results == direct_semantics
    assert tuple(row.variable_anchor_id for row in result.participants) == (
        VAR_A, VAR_B)
    assert result.cohort_admission == "same_acquisition_cohort"
    assert result.execution == "executed"
    assert result.computed_relation == "different"
    assert result.not_executed_reasons == ()
    assert tuple(row.admission for row in result.participants) == (
        "admitted", "admitted")
    assert tuple(row.canonical_decimal for row in result.participants) == (
        "60.1", "60")


def test_real_disposable_ingestion_path_can_execute_exact_equal(tmp_path):
    from tests.observation_compatibility.helpers import observed_value

    result = evaluate(tmp_path, temporal=observed_value(tmp_path, "60.0"))
    assert result.execution == "executed"
    assert result.computed_relation == "equal"
    assert tuple(row.canonical_decimal for row in result.participants) == (
        "60", "60")


def test_context_absence_never_suppresses_participant_evidence(tmp_path):
    result = evaluate(tmp_path, context=AS_BUILT)
    assert result.behavior.conclusion == "not_declared"
    assert result.execution == "not_executed"
    assert result.not_executed_reasons[0].reason == "behavior_not_declared"
    assert all(row.observation_availability == "observed"
               for row in result.participants)
    assert all(row.canonical_decimal is not None for row in result.participants)


def test_unregistered_behavior_still_runs_both_explicit_evidence_paths(tmp_path):
    model = model_store(tmp_path, include_behavior=False)
    result = evaluate(tmp_path, model=model)
    assert result.behavior.conclusion == "not_registered"
    assert result.not_executed_reasons[0].reason == "behavior_not_registered"
    assert len(result.participant_semantic_results) == 2
    assert all(row.observation_availability == "observed"
               for row in result.participants)


def test_reversed_selector_input_is_canonical_and_byte_deterministic(tmp_path):
    first = evaluate(tmp_path / "first", participants=participant_sources())
    second = evaluate(tmp_path / "second", participants=participant_sources(reverse=True))
    assert first.model_dump_json() == second.model_dump_json()


def test_cohort_key_is_exact_and_not_timestamp_proximity(tmp_path):
    result = evaluate(tmp_path)
    first, second = result.participant_semantic_results
    first_occurrence = (
        first.candidates[0].value_candidate.state_candidate.bound.observed.occurrence)
    second_occurrence = (
        second.candidates[0].value_candidate.state_candidate.bound.observed.occurrence)
    assert (
        first_occurrence.subject.source_id,
        first_occurrence.subject.adapter_id,
        first_occurrence.attempt_id,
        first_occurrence.raw_record_id,
        first_occurrence.payload_checksum,
    ) == (
        second_occurrence.subject.source_id,
        second_occurrence.subject.adapter_id,
        second_occurrence.attempt_id,
        second_occurrence.raw_record_id,
        second_occurrence.payload_checksum,
    )


def test_exact_result_has_no_implication_bearing_fields():
    from backend.behavior_evaluation import BehaviorEvaluationResult

    forbidden = {
        "valid", "healthy", "safe", "flow", "direction", "causes",
        "controls", "influences", "port", "consistent", "passed",
    }
    assert forbidden.isdisjoint(BehaviorEvaluationResult.model_fields)


def test_both_lower_branches_run_once_before_first_typed_failure_propagates(
        tmp_path, monkeypatch):
    from backend.behavior_evaluation import BehaviorEvaluationQueries

    semantic = semantic_queries(tmp_path)
    original = semantic.variable_semantic_compatibility
    calls = []
    sentinel = SemanticCompatibilityConfigurationError(
        "SYNTHETIC_LOWER_FAILURE", "first canonical participant failed")

    def branch(variable_anchor_id, **kwargs):
        calls.append(variable_anchor_id)
        if variable_anchor_id == VAR_A:
            raise sentinel
        return original(variable_anchor_id, **kwargs)

    monkeypatch.setattr(semantic, "variable_semantic_compatibility", branch)
    facade = BehaviorEvaluationQueries(semantic)
    try:
        facade.behavior_evaluation(
            BEHAVIOR_A, context=AS_DESIGNED, as_of=AS_OF,
            participants=participant_sources())
    except SemanticCompatibilityConfigurationError as error:
        assert error is sentinel
    else:
        raise AssertionError("the exact lower exception must propagate")
    assert calls == [VAR_A, VAR_B]


def test_second_lower_failure_propagates_after_both_branches(tmp_path, monkeypatch):
    from backend.behavior_evaluation import BehaviorEvaluationQueries

    semantic = semantic_queries(tmp_path)
    original = semantic.variable_semantic_compatibility
    calls = []
    sentinel = SemanticCompatibilityConfigurationError(
        "SYNTHETIC_SECOND_FAILURE", "second participant failed")

    def branch(variable_anchor_id, **kwargs):
        calls.append(variable_anchor_id)
        if variable_anchor_id == VAR_B:
            raise sentinel
        return original(variable_anchor_id, **kwargs)

    monkeypatch.setattr(semantic, "variable_semantic_compatibility", branch)
    with __import__("pytest").raises(
            SemanticCompatibilityConfigurationError) as error:
        BehaviorEvaluationQueries(semantic).behavior_evaluation(
            BEHAVIOR_A, context=AS_DESIGNED, as_of=AS_OF,
            participants=participant_sources())
    assert error.value is sentinel
    assert calls == [VAR_A, VAR_B]


def test_two_lower_failures_propagate_first_canonical_object(tmp_path, monkeypatch):
    from backend.behavior_evaluation import BehaviorEvaluationQueries

    semantic = semantic_queries(tmp_path)
    calls = []
    first = SemanticCompatibilityConfigurationError(
        "FIRST_CANONICAL_FAILURE", "first")
    second = SemanticCompatibilityConfigurationError(
        "SECOND_CANONICAL_FAILURE", "second")

    def branch(variable_anchor_id, **kwargs):
        calls.append(variable_anchor_id)
        raise first if variable_anchor_id == VAR_A else second

    monkeypatch.setattr(semantic, "variable_semantic_compatibility", branch)
    with __import__("pytest").raises(
            SemanticCompatibilityConfigurationError) as error:
        BehaviorEvaluationQueries(semantic).behavior_evaluation(
            BEHAVIOR_A, context=AS_DESIGNED, as_of=AS_OF,
            participants=participant_sources())
    assert error.value is first
    assert calls == [VAR_A, VAR_B]


def test_known_behavior_participant_substitution_fails_before_lower_access(
        tmp_path, monkeypatch):
    from backend.behavior_evaluation import (
        BehaviorEvaluationInputError,
        BehaviorEvaluationQueries,
        BehaviorParticipantSource,
    )
    from backend.model_state import SourceSelector

    semantic = semantic_queries(tmp_path)
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("lower evidence must not be accessed")

    monkeypatch.setattr(
        semantic, "variable_semantic_compatibility", forbidden)
    first, second = participant_sources()
    substituted = BehaviorParticipantSource(
        variable_anchor_id="var_" + "8" * 32,
        entity_anchor_id=second.entity_anchor_id,
        source=SourceSelector(
            subject=second.source.subject, property=second.source.property))
    with __import__("pytest").raises(BehaviorEvaluationInputError) as error:
        BehaviorEvaluationQueries(semantic).behavior_evaluation(
            BEHAVIOR_A, context=AS_DESIGNED, as_of=AS_OF,
            participants=(first, substituted))
    assert error.value.error_code == "BEHAVIOR_EVALUATION_INPUT_INVALID"
    assert calls == []
