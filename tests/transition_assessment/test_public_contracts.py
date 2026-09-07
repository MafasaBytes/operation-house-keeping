"""Exact TA-001 Slice A public-contract gates."""

from __future__ import annotations

import importlib
import inspect
from typing import get_args

import pytest


EXPECTED_EXPORTS = [
    "TransitionAssessmentError",
    "TransitionAssessmentInputError",
    "TransitionAssessmentInputErrorCode",
    "TransitionAssessmentEndpointRole",
    "TransitionAssessmentDeclarationAdmission",
    "TransitionAssessmentContextRelation",
    "TransitionAssessmentModelRevisionRelation",
    "TransitionAssessmentCutoffRelation",
    "TransitionAssessmentEndpointRelation",
    "TransitionAssessmentSubjectRelation",
    "TransitionAssessmentObservationPresence",
    "TransitionAssessmentAlignmentRelation",
    "TransitionAssessmentExpectedFingerprintRelation",
    "TransitionAssessmentEvidenceCompleteness",
    "TransitionAssessmentSourceTimeUse",
    "TransitionAssessmentTemporalCohort",
    "TransitionAssessmentContinuity",
    "TransitionAssessmentExecution",
    "TransitionAssessmentConclusion",
    "TransitionAssessmentIssueCode",
    "TransitionAssessmentPolicy",
    "TransitionAssessmentLimits",
    "DeclaredTransitionAssessmentRequest",
    "TransitionAssessmentIssue",
    "TransitionAssessmentConditionTrace",
    "TransitionAssessmentEndpointDisclosure",
    "DeclaredTransitionAssessmentResult",
    "assess_declared_transition_endpoints",
]


def _ta():
    return importlib.import_module("backend.transition_assessment")


def test_exact_ordered_unique_public_surface_and_no_alternate_names():
    module = _ta()
    assert module.__all__ == EXPECTED_EXPORTS
    assert len(module.__all__) == len(set(module.__all__)) == 28
    assert not hasattr(module, "TransitionAssessmentQueries")
    assert not hasattr(module, "assess_transition")


def test_exact_literal_order_including_all_twenty_two_issue_codes():
    module = _ta()
    expected = {
        "TransitionAssessmentInputErrorCode": (
            "TRANSITION_ASSESSMENT_INPUT_INVALID",
        ),
        "TransitionAssessmentEndpointRole": ("from", "to"),
        "TransitionAssessmentDeclarationAdmission": (
            "not_admitted", "admitted",
        ),
        "TransitionAssessmentContextRelation": ("exact", "different"),
        "TransitionAssessmentModelRevisionRelation": ("exact", "different"),
        "TransitionAssessmentCutoffRelation": (
            "ordered_earlier_to_later", "equal", "reversed",
        ),
        "TransitionAssessmentEndpointRelation": (
            "exact", "different", "not_evaluated",
        ),
        "TransitionAssessmentSubjectRelation": (
            "exact", "different", "not_evaluated",
        ),
        "TransitionAssessmentObservationPresence": ("present", "absent"),
        "TransitionAssessmentAlignmentRelation": (
            "aligned_with_complete_evidence",
            "aligned_with_incomplete_evidence",
            "not_aligned", "not_evaluated", "not_applicable",
        ),
        "TransitionAssessmentExpectedFingerprintRelation": (
            "matched", "mismatched", "not_supplied", "not_evaluated",
            "not_applicable",
        ),
        "TransitionAssessmentEvidenceCompleteness": (
            "not_evaluated", "complete_within_all_declared_horizons",
            "incomplete_within_one_or_more_declared_horizons",
        ),
        "TransitionAssessmentSourceTimeUse": (
            "disclosure_only_not_compared",
        ),
        "TransitionAssessmentTemporalCohort": (
            "independent_latest_per_condition_not_a_temporal_cohort",
        ),
        "TransitionAssessmentContinuity": ("not_assessed",),
        "TransitionAssessmentExecution": ("not_executed", "executed"),
        "TransitionAssessmentConclusion": (
            "bounded_evidence_supports_declared_endpoint_pattern",
            "bounded_evidence_does_not_support_declared_endpoint_pattern",
        ),
    }
    for name, values in expected.items():
        assert get_args(getattr(module, name)) == values
    assert get_args(module.TransitionAssessmentIssueCode) == (
        "transition_anchor_mismatch",
        "transition_not_registered",
        "transition_not_declared",
        "transition_conflicted",
        "transition_inactive",
        "context_mismatch",
        "model_revision_mismatch",
        "from_state_anchor_mismatch",
        "to_state_anchor_mismatch",
        "endpoint_subject_mismatch",
        "endpoint_pin_not_exact_current",
        "endpoint_classification_cutoff_mismatch",
        "cutoffs_equal",
        "cutoffs_reversed",
        "endpoint_classification_not_executed",
        "endpoint_classification_incomplete",
        "governing_selection_refused",
        "governing_expected_fingerprint_not_supplied",
        "governing_expected_fingerprint_not_evaluated",
        "governing_expected_fingerprint_mismatched",
        "governing_occurrence_not_aligned",
        "governing_evidence_incomplete",
    )


def test_exact_model_field_order():
    module = _ta()
    expected = {
        "TransitionAssessmentPolicy": (
            "kind", "version", "endpoint_selection", "evidence_requirement",
            "source_time_use", "temporal_cohort", "continuity",
        ),
        "TransitionAssessmentLimits": (
            "schema_version", "maximum_endpoint_conditions",
            "maximum_condition_traces", "maximum_distinct_alignments",
            "maximum_canonical_request_bytes", "maximum_reconstructed_nodes",
            "maximum_nesting_depth",
        ),
        "DeclaredTransitionAssessmentRequest": (
            "schema_version", "transition_anchor_id", "context", "from_as_of",
            "to_as_of", "policy", "transition", "from_classification",
            "to_classification", "evidence_alignments",
        ),
        "TransitionAssessmentIssue": (
            "code", "endpoint_role", "condition_index",
            "evidence_alignment_index",
        ),
        "TransitionAssessmentConditionTrace": (
            "trace_index", "endpoint_role", "condition_index",
            "constraint_evaluation_index", "semantic_candidate_index",
            "value_candidate_index", "observation_presence",
            "evidence_alignment_index", "alignment_relation",
            "evidence_selection_status", "evidence_completeness",
            "expected_fingerprint_relation", "selected_occurrence_role",
            "source_time_use",
        ),
        "TransitionAssessmentEndpointDisclosure": (
            "role", "declared_state_anchor_id", "classified_state_anchor_id",
            "state_anchor_relation", "subject_relation", "pin_alignment",
            "classification_context_relation", "classification_cutoff_relation",
            "state_declaration_conclusion", "condition_coverage",
            "classification_execution", "computed_match",
            "condition_trace_indices",
        ),
        "DeclaredTransitionAssessmentResult": (
            "schema_version", "request", "ruleset_version", "fixed_limits",
            "declaration_admission", "context_relation",
            "model_revision_relation", "cutoff_relation", "from_endpoint",
            "to_endpoint", "condition_traces", "evidence_completeness",
            "source_time_use", "temporal_cohort", "continuity", "execution",
            "issues", "conclusion",
        ),
    }
    for name, fields in expected.items():
        assert tuple(getattr(module, name).model_fields) == fields


def test_models_are_frozen_extra_forbidden_and_always_revalidated():
    module = _ta()
    for name in EXPECTED_EXPORTS[20:27]:
        config = getattr(module, name).model_config
        assert config["frozen"] is True
        assert config["extra"] == "forbid"
        assert config["revalidate_instances"] == "always"


def test_fixed_policy_limits_and_strict_issue_indices():
    module = _ta()
    limits = module.TransitionAssessmentLimits(
        schema_version="1",
        maximum_endpoint_conditions=64,
        maximum_condition_traces=128,
        maximum_distinct_alignments=128,
        maximum_canonical_request_bytes=134_217_728,
        maximum_reconstructed_nodes=200_000,
        maximum_nesting_depth=128,
    )
    assert limits.maximum_canonical_request_bytes == 134_217_728
    with pytest.raises(Exception):
        module.TransitionAssessmentIssue(
            code="cutoffs_equal", endpoint_role=None, condition_index=True,
            evidence_alignment_index=None,
        )


def test_input_error_tree_and_operation_signature_are_exact():
    module = _ta()
    assert module.TransitionAssessmentInputError.__bases__ == (
        module.TransitionAssessmentError,
    )
    error = module.TransitionAssessmentInputError(
        "TRANSITION_ASSESSMENT_INPUT_INVALID", "request is invalid",
    )
    assert vars(error) == {
        "error_code": "TRANSITION_ASSESSMENT_INPUT_INVALID",
        "message": "request is invalid",
    }
    with pytest.raises(ValueError):
        module.TransitionAssessmentInputError("WRONG", "request is invalid")
    with pytest.raises(ValueError):
        module.TransitionAssessmentInputError(
            "TRANSITION_ASSESSMENT_INPUT_INVALID", "password=secret",
        )
    signature = inspect.signature(module.assess_declared_transition_endpoints)
    assert tuple(signature.parameters) == ("request",)
    assert signature.return_annotation in (
        "DeclaredTransitionAssessmentResult",
        module.DeclaredTransitionAssessmentResult,
    )
