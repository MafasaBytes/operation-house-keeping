"""Pure TA-001 endpoint-pattern derivation."""

from __future__ import annotations

from .contracts import (
    DeclaredTransitionAssessmentRequest,
    DeclaredTransitionAssessmentResult,
    TransitionAssessmentInputError,
)


def _derive_result_fields(request: DeclaredTransitionAssessmentRequest) -> dict:
    raise ValueError("transition assessment derivation is not implemented")


def assess_declared_transition_endpoints(
    request: DeclaredTransitionAssessmentRequest,
) -> DeclaredTransitionAssessmentResult:
    try:
        rebuilt = DeclaredTransitionAssessmentRequest.model_validate(request)
        fields = _derive_result_fields(rebuilt)
        return DeclaredTransitionAssessmentResult.model_construct(
            schema_version="1", request=rebuilt, **fields,
        )
    except TransitionAssessmentInputError:
        raise
    except Exception as error:
        raise TransitionAssessmentInputError(
            "TRANSITION_ASSESSMENT_INPUT_INVALID",
            "transition assessment request is invalid",
        ) from error
