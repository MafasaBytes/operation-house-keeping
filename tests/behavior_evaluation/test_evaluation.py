"""BH-001 lifecycle, evidence, cohort, and exact-comparison behavior."""

from backend.model_kernel import ModelQueries

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
