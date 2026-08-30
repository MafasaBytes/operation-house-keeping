"""Exact ST-001 Slice C public vocabulary and facade boundary."""

import inspect
from typing import get_args

import pytest

import backend.state_classification as classification


EXPECTED_EXPORTS = [
    "StateClassificationError",
    "StateClassificationConfigurationError",
    "StateClassificationInputError",
    "StateConditionSource",
    "StateConditionDeclarationAlignment",
    "StateConditionOutcome",
    "StateConditionCoverage",
    "StateTemporalAlignment",
    "StateClassificationExecution",
    "StateComputedMatch",
    "StateClassificationRefusalReason",
    "StateClassificationRefusal",
    "StateClassificationConditionResult",
    "StateClassificationResult",
    "StateClassificationQueries",
]

REFUSALS = (
    "state_not_registered",
    "state_not_declared",
    "state_inactive",
    "state_conflicted",
    "condition_not_registered",
    "condition_declaration_not_declared",
    "condition_declaration_conflicted",
    "condition_declaration_superseded",
    "condition_evaluation_not_evaluated",
)


def test_exact_public_exports_without_lower_contract_leaks():
    assert classification.__all__ == EXPECTED_EXPORTS
    assert not hasattr(classification, "ConstraintEvaluationQueries")
    assert not hasattr(classification, "ConstraintEvaluationResult")
    assert not hasattr(classification, "ModelQueries")
    assert not hasattr(classification, "SourceSelector")
    assert not hasattr(classification, "derive_classification")


def test_exact_status_literals_and_refusal_order():
    assert get_args(classification.StateConditionDeclarationAlignment) == (
        "not_evaluated", "not_registered", "not_declared", "conflicted",
        "superseded", "exact_current")
    assert get_args(classification.StateConditionOutcome) == (
        "satisfied", "violated", "not_evaluated")
    assert get_args(classification.StateConditionCoverage) == (
        "not_evaluated", "complete", "incomplete")
    assert get_args(classification.StateTemporalAlignment) == (
        "not_evaluated", "not_asserted")
    assert get_args(classification.StateClassificationExecution) == (
        "not_executed", "executed")
    assert get_args(classification.StateComputedMatch) == (
        "matches", "does_not_match")
    assert get_args(classification.StateClassificationRefusalReason) == REFUSALS


def test_exact_contract_fields_and_signature():
    assert tuple(classification.StateConditionSource.model_fields) == (
        "constraint_anchor_id", "source")
    assert tuple(classification.StateClassificationRefusal.model_fields) == (
        "reason", "condition_index")
    assert tuple(
        classification.StateClassificationConditionResult.model_fields) == (
            "condition_index", "constraint_anchor_id", "source_index",
            "constraint_evaluation_index", "candidate_index",
            "declaration_alignment", "outcome")
    assert tuple(classification.StateClassificationResult.model_fields) == (
        "state", "state_anchor_id", "context", "as_of", "ruleset_version",
        "condition_sources", "constraint_evaluations", "conditions",
        "condition_coverage", "temporal_alignment", "execution", "refusals",
        "computed_match")
    assert str(inspect.signature(
        classification.StateClassificationQueries.state_classification)) == (
            "(self, state_anchor_id, *, context, as_of, condition_sources) -> "
            "'StateClassificationResult'")


def test_public_error_tree_and_configuration_code():
    assert issubclass(
        classification.StateClassificationConfigurationError,
        classification.StateClassificationError)
    assert issubclass(
        classification.StateClassificationInputError,
        classification.StateClassificationError)
    with pytest.raises(
            classification.StateClassificationConfigurationError) as error:
        classification.StateClassificationQueries(object())
    assert error.value.error_code == "STATE_CLASSIFICATION_CONFIGURATION_INVALID"


def test_contract_models_are_frozen_extra_forbidden_and_revalidated():
    for contract in (
        classification.StateConditionSource,
        classification.StateClassificationRefusal,
        classification.StateClassificationConditionResult,
        classification.StateClassificationResult,
    ):
        assert contract.model_config["frozen"] is True
        assert contract.model_config["extra"] == "forbid"
        assert contract.model_config["revalidate_instances"] == "always"
