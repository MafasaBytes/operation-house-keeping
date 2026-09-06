"""EA-001 Slice C1 pure evidence-alignment contracts.

The models carry one accepted EA selection and one accepted observation-
compatibility result.  They own no store and add no evidence, assessment,
freshness, currentness, or physical-occurrence claim.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)

from backend.evidence_assurance import (
    OperationalEvidenceSelectionResult,
    OperationalEvidenceSelectionStatus,
    OperationalEvidenceSnapshotValidationResult,
)
from backend.observation_compatibility import VariableValueCompatibilityResult
from backend.temporal_state.contracts import TaggedSha256


EvidenceAlignmentQueryErrorCode = Literal["ALIGNMENT_REQUEST_INVALID"]
OperationalEvidenceAlignmentStatus = Literal[
    "aligned_with_complete_evidence",
    "aligned_with_incomplete_evidence",
    "not_aligned",
    "not_evaluated",
]
OperationalEvidenceAlignmentReason = Literal[
    "selection_refused",
    "snapshot_fingerprint_mismatched",
    "no_selected_observation",
    "cutoff_differs",
    "scope_differs",
    "consumer_observation_absent",
    "occurrence_content_mismatch",
    "occurrence_absent_from_consumer_result",
    "multiple_matching_candidates",
]
OperationalEvidenceAlignmentExpectedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_supplied",
    "not_evaluated",
]


def _bounded_safe_text(value: object, *, description: str) -> str:
    if type(value) is not str or not value or len(value) > 300:
        raise ValueError(f"{description} must contain 1 through 300 characters")
    lowered = value.lower()
    tokens = value.split()
    if any(
        token.strip("'\"()[],;").startswith(("/", "\\\\"))
        or re.match(r"^[a-zA-Z]:[\\/]", token.strip("'\"()[],;"))
        for token in tokens
    ):
        raise ValueError(f"{description} must not contain an absolute path")
    if re.search(r"[a-z][a-z0-9+.-]*://[^\s/@]+:[^\s/@]+@", value, re.I):
        raise ValueError(f"{description} must not contain URI user information")
    if re.search(
        r"\b(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]",
        lowered,
    ):
        raise ValueError(f"{description} must not contain credentials")
    return value


def _deep_plain(value: object, active: set[int] | None = None):
    """Rebuild public content from exact ordinary scalars with cycle checks."""
    if active is None:
        active = set()
    if type(value) in (str, bytes, int, float, bool, type(None), datetime):
        return value
    identity = id(value)
    if identity in active:
        raise ValueError("cyclic nested content is invalid")
    active.add(identity)
    try:
        if isinstance(value, BaseModel):
            fields = tuple(value.__class__.model_fields)
            extras = getattr(value, "__pydantic_extra__", None) or {}
            hidden = set(value.__dict__) - set(fields)
            if hidden or extras:
                raise ValueError("nested model contains hidden extra content")
            return {
                name: _deep_plain(getattr(value, name), active)
                for name in fields
            }
        if type(value) is dict:
            plain = {}
            for key, item in value.items():
                if type(key) is not str:
                    raise ValueError("nested mapping keys must be ordinary strings")
                if (
                    (key == "sweep_position" or key.endswith("_index"))
                    and type(item) is bool
                ):
                    raise ValueError("boolean indices are invalid")
                if key.endswith("_indices") and type(item) in (tuple, list):
                    if any(type(index) is bool for index in item):
                        raise ValueError("boolean indices are invalid")
                plain[key] = _deep_plain(item, active)
            return plain
        if type(value) in (tuple, list):
            return [_deep_plain(item, active) for item in value]
        raise ValueError("nested content contains an unsupported value")
    finally:
        active.remove(identity)


class _StrictFrozen(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        revalidate_instances="always",
    )

    @model_validator(mode="before")
    @classmethod
    def _reconstruct_plain(cls, value):
        if isinstance(value, BaseModel) or type(value) in (dict, tuple, list):
            return _deep_plain(value)
        return value


class EvidenceAlignmentError(Exception):
    _allowed_codes: tuple[str, ...] = ()

    def __init__(self, error_code: str, message: str) -> None:
        if type(error_code) is not str or error_code not in self._allowed_codes:
            raise ValueError("error code is not valid for this exception type")
        safe_message = _bounded_safe_text(message, description="message")
        super().__init__(f"{error_code}: {safe_message}")
        self.error_code = error_code
        self.message = safe_message


class EvidenceAlignmentQueryError(EvidenceAlignmentError):
    _allowed_codes = ("ALIGNMENT_REQUEST_INVALID",)


class OperationalEvidenceAlignmentRequest(_StrictFrozen):
    schema_version: Literal["1"]
    selection: OperationalEvidenceSelectionResult
    compatibility: VariableValueCompatibilityResult
    expected_snapshot_fingerprint: TaggedSha256 | None = None

    @field_validator("selection", mode="before")
    @classmethod
    def _selection(cls, value):
        return OperationalEvidenceSelectionResult.model_validate(
            _deep_plain(value))

    @field_validator("compatibility", mode="before")
    @classmethod
    def _compatibility(cls, value):
        return VariableValueCompatibilityResult.model_validate(
            _deep_plain(value))

    @field_validator("expected_snapshot_fingerprint", mode="before")
    @classmethod
    def _expected_fingerprint(cls, value):
        if value is not None and type(value) is not str:
            raise ValueError("expected fingerprint must be an ordinary string")
        return value


_StrictIndex = Annotated[StrictInt, Field(ge=0)]
_MismatchFields = Annotated[
    tuple[StrictStr, ...],
    Field(max_length=20),
]


class OperationalEvidenceAlignmentResult(_StrictFrozen):
    schema_version: Literal["1"]
    request: OperationalEvidenceAlignmentRequest
    status: OperationalEvidenceAlignmentStatus
    reason: OperationalEvidenceAlignmentReason | None
    snapshot_validation: OperationalEvidenceSnapshotValidationResult | None
    evidence_selection_status: OperationalEvidenceSelectionStatus
    evidence_coverage_completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "not_applicable",
    ]
    expected_fingerprint_relation: (
        OperationalEvidenceAlignmentExpectedFingerprintRelation
    )
    cutoff_relation: Literal["equal", "different", "not_evaluated"]
    scope_relation: Literal[
        "six_field_locator_equal",
        "six_field_locator_different",
        "not_evaluated",
    ]
    endpoint_closure: Literal[
        "bound_by_snapshot_closure",
        "not_evaluated",
    ]
    selected_occurrence_role: Literal[
        "in_horizon_member",
        "pre_horizon_seed",
        "not_applicable",
    ]
    occurrence_relation: Literal[
        "content_equal",
        "absent_from_consumer_result",
        "content_mismatch",
        "multiple_matches",
        "not_applicable",
    ]
    mismatched_occurrence_fields: _MismatchFields
    aligned_candidate_index: _StrictIndex | None
    candidate_attachment: Literal[
        "attached",
        "not_attachable_variable_unregistered",
        "not_attachable_anchor_divergent",
        "not_attachable_resolution_mismatch",
        "not_attachable_resolution_nonpositive",
        "not_evaluated",
        "not_applicable",
    ]
    variable_anchor_id: StrictStr
    model_revision_id: StrictStr
    binding_revision_id: StrictStr

    @field_validator("request", mode="before")
    @classmethod
    def _request(cls, value):
        return OperationalEvidenceAlignmentRequest.model_validate(
            _deep_plain(value))

    @field_validator("snapshot_validation", mode="before")
    @classmethod
    def _snapshot_validation(cls, value):
        if value is None:
            return None
        return OperationalEvidenceSnapshotValidationResult.model_validate(
            _deep_plain(value))

    @model_validator(mode="after")
    def _derived_fields_are_current(self, info: ValidationInfo):
        if self.mismatched_occurrence_fields != tuple(
            sorted(set(self.mismatched_occurrence_fields))
        ):
            raise ValueError("mismatched occurrence fields must be unique and sorted")
        from backend.evidence_alignment.derivation import (
            _derive_alignment_fields,
        )

        expected = _derive_alignment_fields(self.request)
        for name, value in expected.items():
            if getattr(self, name) != value:
                raise ValueError(f"{name} is not justified by the carried request")
        return self
