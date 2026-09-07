"""Strict public contracts for TA-001 declared endpoint assessment."""

from __future__ import annotations

import re
from contextvars import ContextVar
from datetime import UTC
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
    TypeAdapter,
    field_validator,
    model_validator,
)

from backend.evidence_alignment import OperationalEvidenceAlignmentResult
from backend.model_kernel import (
    AssertionContext,
    StateDeclarationConclusion,
    TransitionDeclarationResult,
    TransitionEndpointPinAlignment,
)
from backend.state_classification import (
    StateClassificationExecution,
    StateClassificationResult,
    StateComputedMatch,
    StateConditionCoverage,
)

from .preflight import _plain_graph, _preflight_graph


TransitionAssessmentInputErrorCode = Literal[
    "TRANSITION_ASSESSMENT_INPUT_INVALID",
]
TransitionAssessmentEndpointRole = Literal["from", "to"]
TransitionAssessmentDeclarationAdmission = Literal["not_admitted", "admitted"]
TransitionAssessmentContextRelation = Literal["exact", "different"]
TransitionAssessmentModelRevisionRelation = Literal["exact", "different"]
TransitionAssessmentCutoffRelation = Literal[
    "ordered_earlier_to_later", "equal", "reversed",
]
TransitionAssessmentEndpointRelation = Literal[
    "exact", "different", "not_evaluated",
]
TransitionAssessmentSubjectRelation = Literal[
    "exact", "different", "not_evaluated",
]
TransitionAssessmentObservationPresence = Literal["present", "absent"]
TransitionAssessmentAlignmentRelation = Literal[
    "aligned_with_complete_evidence",
    "aligned_with_incomplete_evidence",
    "not_aligned",
    "not_evaluated",
    "not_applicable",
]
TransitionAssessmentExpectedFingerprintRelation = Literal[
    "matched", "mismatched", "not_supplied", "not_evaluated",
    "not_applicable",
]
TransitionAssessmentEvidenceCompleteness = Literal[
    "not_evaluated",
    "complete_within_all_declared_horizons",
    "incomplete_within_one_or_more_declared_horizons",
]
TransitionAssessmentSourceTimeUse = Literal["disclosure_only_not_compared"]
TransitionAssessmentTemporalCohort = Literal[
    "independent_latest_per_condition_not_a_temporal_cohort",
]
TransitionAssessmentContinuity = Literal["not_assessed"]
TransitionAssessmentExecution = Literal["not_executed", "executed"]
TransitionAssessmentConclusion = Literal[
    "bounded_evidence_supports_declared_endpoint_pattern",
    "bounded_evidence_does_not_support_declared_endpoint_pattern",
]
TransitionAssessmentIssueCode = Literal[
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
]


def _bounded_safe_text(value: object) -> str:
    if type(value) is not str or not value or len(value) > 300:
        raise ValueError("message must contain 1 through 300 characters")
    lowered = value.lower()
    tokens = value.split()
    if any(
        token.strip("'\"()[],;").startswith(("/", "\\\\"))
        or re.match(r"^[a-zA-Z]:[\\/]", token.strip("'\"()[],;"))
        for token in tokens
    ):
        raise ValueError("message must not contain an absolute path")
    if re.search(r"[a-z][a-z0-9+.-]*://[^\s/@]+:[^\s/@]+@", value, re.I):
        raise ValueError("message must not contain URI user information")
    if re.search(
        r"\b(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]",
        lowered,
    ):
        raise ValueError("message must not contain credentials")
    return value


class TransitionAssessmentError(Exception):
    _allowed_codes: tuple[str, ...] = ()

    def __init__(self, error_code: str, message: StrictStr) -> None:
        if type(error_code) is not str or error_code not in self._allowed_codes:
            raise ValueError("error code is invalid")
        safe = _bounded_safe_text(message)
        super().__init__(f"{error_code}: {safe}")
        self.error_code = error_code
        self.message = safe


class TransitionAssessmentInputError(TransitionAssessmentError):
    _allowed_codes = ("TRANSITION_ASSESSMENT_INPUT_INVALID",)


class _Frozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always",
    )


class TransitionAssessmentPolicy(_Frozen):
    kind: Literal["declared_endpoint_pattern_at_ordered_cutoffs"]
    version: Literal["ta001.endpoint_pattern.v1"]
    endpoint_selection: Literal[
        "independent_latest_per_condition_at_or_before_cutoff"
    ]
    evidence_requirement: Literal[
        "complete_alignment_with_matched_expected_fingerprint"
    ]
    source_time_use: Literal["disclosure_only"]
    temporal_cohort: Literal["not_asserted"]
    continuity: Literal["not_assessed"]


class TransitionAssessmentLimits(_Frozen):
    schema_version: Literal["1"]
    maximum_endpoint_conditions: Literal[64]
    maximum_condition_traces: Literal[128]
    maximum_distinct_alignments: Literal[128]
    maximum_canonical_request_bytes: Literal[134217728]
    maximum_reconstructed_nodes: Literal[200000]
    maximum_nesting_depth: Literal[128]


_UtcDatetime = Annotated[
    AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC)),
]
_StrictNonnegativeInt = Annotated[StrictInt, Field(ge=0)]
_TransitionAnchorId = Annotated[
    StrictStr, StringConstraints(pattern=r"^trn_[0-9a-f]{32}$"),
]
_CONTEXT = TypeAdapter(AssertionContext)
_REQUEST_ALREADY_PREFLIGHTED: ContextVar[bool] = ContextVar(
    "ta_request_already_preflighted", default=False,
)


class DeclaredTransitionAssessmentRequest(_Frozen):
    schema_version: Literal["1"]
    transition_anchor_id: _TransitionAnchorId
    context: AssertionContext
    from_as_of: _UtcDatetime
    to_as_of: _UtcDatetime
    policy: TransitionAssessmentPolicy
    transition: TransitionDeclarationResult
    from_classification: StateClassificationResult
    to_classification: StateClassificationResult
    evidence_alignments: tuple[OperationalEvidenceAlignmentResult, ...]

    @model_validator(mode="wrap")
    @classmethod
    def _bounded_reconstruction(cls, value, handler):
        if not _REQUEST_ALREADY_PREFLIGHTED.get():
            _preflight_graph(value)
        plain = _plain_graph(value)
        rebuilt = handler(plain)
        if len(rebuilt.evidence_alignments) > 128:
            raise ValueError("alignment cardinality exceeds the fixed limit")
        if any(len(item.conditions) > 64 for item in (
            rebuilt.from_classification, rebuilt.to_classification,
        )):
            raise ValueError("endpoint condition cardinality exceeds the fixed limit")
        return rebuilt

    @field_validator("context", mode="before")
    @classmethod
    def _context(cls, value):
        return _CONTEXT.validate_python(_plain_graph(value))

    @field_validator("policy", mode="before")
    @classmethod
    def _policy(cls, value):
        return TransitionAssessmentPolicy.model_validate(_plain_graph(value))

    @field_validator("transition", mode="before")
    @classmethod
    def _transition(cls, value):
        return TransitionDeclarationResult.model_validate(_plain_graph(value))

    @field_validator("from_classification", "to_classification", mode="before")
    @classmethod
    def _classification(cls, value):
        return StateClassificationResult.model_validate(_plain_graph(value))

    @field_validator("evidence_alignments", mode="before")
    @classmethod
    def _alignments(cls, value):
        if type(value) not in (tuple, list):
            raise ValueError("evidence alignments must be a sequence")
        return tuple(
            OperationalEvidenceAlignmentResult.model_validate(_plain_graph(item))
            for item in value
        )


class TransitionAssessmentIssue(_Frozen):
    code: TransitionAssessmentIssueCode
    endpoint_role: TransitionAssessmentEndpointRole | None
    condition_index: _StrictNonnegativeInt | None
    evidence_alignment_index: _StrictNonnegativeInt | None


class TransitionAssessmentConditionTrace(_Frozen):
    trace_index: _StrictNonnegativeInt
    endpoint_role: TransitionAssessmentEndpointRole
    condition_index: _StrictNonnegativeInt
    constraint_evaluation_index: _StrictNonnegativeInt
    semantic_candidate_index: _StrictNonnegativeInt | None
    value_candidate_index: _StrictNonnegativeInt | None
    observation_presence: TransitionAssessmentObservationPresence
    evidence_alignment_index: _StrictNonnegativeInt | None
    alignment_relation: TransitionAssessmentAlignmentRelation
    evidence_selection_status: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "refused",
        "not_applicable",
    ]
    evidence_completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "not_applicable",
    ]
    expected_fingerprint_relation: TransitionAssessmentExpectedFingerprintRelation
    selected_occurrence_role: Literal[
        "in_horizon_member", "pre_horizon_seed", "not_applicable",
    ]
    source_time_use: Literal["disclosure_only", "not_applicable"]


class TransitionAssessmentEndpointDisclosure(_Frozen):
    role: TransitionAssessmentEndpointRole
    declared_state_anchor_id: StrictStr | None
    classified_state_anchor_id: StrictStr
    state_anchor_relation: TransitionAssessmentEndpointRelation
    subject_relation: TransitionAssessmentSubjectRelation
    pin_alignment: TransitionEndpointPinAlignment | None
    classification_context_relation: TransitionAssessmentContextRelation
    classification_cutoff_relation: TransitionAssessmentEndpointRelation
    state_declaration_conclusion: StateDeclarationConclusion
    condition_coverage: StateConditionCoverage
    classification_execution: StateClassificationExecution
    computed_match: StateComputedMatch | None
    condition_trace_indices: tuple[_StrictNonnegativeInt, ...]


class DeclaredTransitionAssessmentResult(_Frozen):
    schema_version: Literal["1"]
    request: DeclaredTransitionAssessmentRequest
    ruleset_version: Literal["ta001.1"]
    fixed_limits: TransitionAssessmentLimits
    declaration_admission: TransitionAssessmentDeclarationAdmission
    context_relation: TransitionAssessmentContextRelation
    model_revision_relation: TransitionAssessmentModelRevisionRelation
    cutoff_relation: TransitionAssessmentCutoffRelation
    from_endpoint: TransitionAssessmentEndpointDisclosure
    to_endpoint: TransitionAssessmentEndpointDisclosure
    condition_traces: tuple[TransitionAssessmentConditionTrace, ...]
    evidence_completeness: TransitionAssessmentEvidenceCompleteness
    source_time_use: TransitionAssessmentSourceTimeUse
    temporal_cohort: TransitionAssessmentTemporalCohort
    continuity: TransitionAssessmentContinuity
    execution: TransitionAssessmentExecution
    issues: tuple[TransitionAssessmentIssue, ...]
    conclusion: TransitionAssessmentConclusion | None

    @model_validator(mode="wrap")
    @classmethod
    def _bounded_reconstruction(cls, value, handler):
        _preflight_graph(value)
        plain = _plain_graph(value)
        token = _REQUEST_ALREADY_PREFLIGHTED.set(True)
        try:
            return handler(plain)
        finally:
            _REQUEST_ALREADY_PREFLIGHTED.reset(token)

    @model_validator(mode="after")
    def _authoritative(self):
        from .derivation import _derive_result_fields

        expected = _derive_result_fields(self.request)
        for name, value in expected.items():
            if getattr(self, name) != value:
                raise ValueError("assessment result contains stale derived content")
        return self


FIXED_POLICY = TransitionAssessmentPolicy(
    kind="declared_endpoint_pattern_at_ordered_cutoffs",
    version="ta001.endpoint_pattern.v1",
    endpoint_selection="independent_latest_per_condition_at_or_before_cutoff",
    evidence_requirement="complete_alignment_with_matched_expected_fingerprint",
    source_time_use="disclosure_only",
    temporal_cohort="not_asserted",
    continuity="not_assessed",
)
FIXED_LIMITS = TransitionAssessmentLimits(
    schema_version="1",
    maximum_endpoint_conditions=64,
    maximum_condition_traces=128,
    maximum_distinct_alignments=128,
    maximum_canonical_request_bytes=134_217_728,
    maximum_reconstructed_nodes=200_000,
    maximum_nesting_depth=128,
)
