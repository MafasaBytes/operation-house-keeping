"""TA-001 Slice A pure join, gate, and conclusion tests."""

from __future__ import annotations

import pytest

from backend.evidence_alignment import (
    OperationalEvidenceAlignmentRequest,
    align_operational_evidence_with_value_compatibility,
)
from backend.transition_assessment import (
    DeclaredTransitionAssessmentRequest,
    TransitionAssessmentInputError,
    assess_declared_transition_endpoints,
)

from tests.transition_assessment.helpers import build_world
from tests.model_state.helpers import BEFORE_RECEIPT


def _request(request, **updates):
    raw = request.model_dump(mode="python", warnings=False)
    raw.update(updates)
    return DeclaredTransitionAssessmentRequest.model_validate(raw)


def test_complete_matched_endpoints_execute_bounded_support(tmp_path):
    world = build_world(tmp_path)
    result = assess_declared_transition_endpoints(world.request)
    assert result.declaration_admission == "admitted"
    assert result.execution == "executed"
    assert result.conclusion == (
        "bounded_evidence_supports_declared_endpoint_pattern"
    )
    assert result.evidence_completeness == (
        "complete_within_all_declared_horizons"
    )
    assert result.issues == ()
    assert tuple(trace.endpoint_role for trace in result.condition_traces) == (
        "from", "to",
    )
    assert all(trace.expected_fingerprint_relation == "matched"
               for trace in result.condition_traces)


def test_complete_endpoint_nonmatch_executes_bounded_non_support(tmp_path):
    world = build_world(tmp_path, upper="50")
    result = assess_declared_transition_endpoints(world.request)
    assert result.execution == "executed"
    assert result.conclusion == (
        "bounded_evidence_does_not_support_declared_endpoint_pattern"
    )
    assert result.issues == ()


def test_equal_cutoffs_are_structured_nonexecution(tmp_path):
    world = build_world(tmp_path)
    request = _request(world.request, to_as_of=world.request.from_as_of)
    result = assess_declared_transition_endpoints(request)
    assert result.cutoff_relation == "equal"
    assert result.execution == "not_executed"
    assert result.conclusion is None
    assert tuple(issue.code for issue in result.issues) == (
        "endpoint_classification_cutoff_mismatch", "cutoffs_equal",
    )


def test_missing_expected_fingerprint_blocks_without_changing_completeness(
    tmp_path,
):
    world = build_world(tmp_path)
    alignments = tuple(
        align_operational_evidence_with_value_compatibility(
            OperationalEvidenceAlignmentRequest(
                schema_version="1",
                selection=alignment.request.selection,
                compatibility=alignment.request.compatibility,
                expected_snapshot_fingerprint=None,
            )
        )
        for alignment in world.request.evidence_alignments
    )
    result = assess_declared_transition_endpoints(
        _request(world.request, evidence_alignments=alignments),
    )
    assert result.evidence_completeness == (
        "complete_within_all_declared_horizons"
    )
    assert result.execution == "not_executed"
    assert tuple(issue.code for issue in result.issues) == (
        "governing_expected_fingerprint_not_supplied",
        "governing_expected_fingerprint_not_supplied",
    )


def test_missing_or_reordered_exact_alignment_collection_is_malformed(tmp_path):
    world = build_world(tmp_path)
    for alignments in (
        world.request.evidence_alignments[:1],
        tuple(reversed(world.request.evidence_alignments)),
    ):
        with pytest.raises(TransitionAssessmentInputError) as captured:
            assess_declared_transition_endpoints(
                _request(world.request, evidence_alignments=alignments),
            )
        assert captured.value.error_code == "TRANSITION_ASSESSMENT_INPUT_INVALID"


def test_corrected_t43_candidate_zero_twin_and_candidate_one_attack(
    tmp_path, monkeypatch,
):
    import backend.transition_assessment.derivation as derivation

    world = build_world(tmp_path)
    assert tuple(
        alignment.aligned_candidate_index
        for alignment in world.request.evidence_alignments
    ) == (0, 0)
    assert assess_declared_transition_endpoints(world.request).execution == "executed"

    raw = world.request.model_dump(mode="python", warnings=False)
    raw["evidence_alignments"][0]["aligned_candidate_index"] = 1
    original = derivation._derive_result_fields
    calls = []

    def recording(request):
        calls.append(request)
        return original(request)

    monkeypatch.setattr(derivation, "_derive_result_fields", recording)
    with pytest.raises(TransitionAssessmentInputError) as captured:
        assess_declared_transition_endpoints(raw)
    assert captured.value.error_code == "TRANSITION_ASSESSMENT_INPUT_INVALID"
    assert calls == []


def test_finite_float_in_nonfloat_field_remains_malformed(tmp_path):
    world = build_world(tmp_path)
    raw = world.request.model_dump(mode="python", warnings=False)
    raw["transition_anchor_id"] = 1.0
    with pytest.raises(TransitionAssessmentInputError) as captured:
        assess_declared_transition_endpoints(raw)
    assert captured.value.error_code == "TRANSITION_ASSESSMENT_INPUT_INVALID"


def test_integral_float_in_carried_integer_field_is_not_coerced(tmp_path):
    world = build_world(tmp_path)
    raw = world.request.model_dump(mode="python", warnings=False)

    def replace(value):
        if type(value) is dict:
            return {
                key: (
                    float(item)
                    if key == "observation_count" and type(item) is int
                    else replace(item)
                )
                for key, item in value.items()
            }
        if type(value) in (tuple, list):
            return type(value)(replace(item) for item in value)
        return value

    with pytest.raises(TransitionAssessmentInputError) as captured:
        assess_declared_transition_endpoints(replace(raw))
    assert captured.value.error_code == "TRANSITION_ASSESSMENT_INPUT_INVALID"


def test_incomplete_classification_is_incomplete_not_not_evaluated(tmp_path):
    world = build_world(
        tmp_path,
        from_as_of=BEFORE_RECEIPT,
        to_as_of=BEFORE_RECEIPT.replace(minute=1),
    )
    result = assess_declared_transition_endpoints(world.request)
    assert world.request.from_classification.condition_coverage == "incomplete"
    assert result.evidence_completeness == (
        "incomplete_within_one_or_more_declared_horizons"
    )
    assert result.execution == "not_executed"


def test_subject_relation_is_not_evaluated_without_effective_body(tmp_path):
    world = build_world(tmp_path, declare_transition=False)
    result = assess_declared_transition_endpoints(world.request)
    assert world.request.transition.effective_body_groups == ()
    assert result.from_endpoint.subject_relation == "not_evaluated"
    assert result.to_endpoint.subject_relation == "not_evaluated"
