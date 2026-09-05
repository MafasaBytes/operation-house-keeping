"""Public EA-001 Slice B contracts.

These values describe a bounded captured view of lower operational evidence.
They do not authenticate a source, interpret observations, or assert physical
occurrence.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from backend.data_sources.contracts import (
    Ds004OperationalEvidenceMaterial,
    Ds004OperationalEvidenceScope,
    OperationalApiInventoryToken,
)
from backend.temporal_state.contracts import (
    TaggedSha256,
    TemporalSelectionInventoryToken,
    TemporalSelectionMaterial,
)


EvidenceAssuranceConfigurationErrorCode = Literal[
    "EA_DEPENDENCY_INVALID",
]
EvidenceAssuranceQueryErrorCode = Literal[
    "EA_REQUEST_INVALID",
    "EA_SELECTION_POLICY_INVALID",
]

CanonicalNonnegativeDecimal = Annotated[
    StrictStr,
    StringConstraints(pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$"),
]
CoverageDisposition = Literal[
    "property_observed",
    "snapshot_without_property",
    "empty_snapshot",
    "acquisition_failed",
    "quarantined",
    "extraction_incomplete",
]
OperationalEvidenceIssueCode = Literal[
    "unsupported_operational_evidence",
    "invalid_bounded_material",
    "excessive_bounded_material",
    "source_evidence_unavailable",
    "temporal_evidence_unavailable",
    "source_store_changed_during_capture",
    "temporal_store_changed_during_capture",
    "checksum_mismatch",
    "provenance_closure_failure",
    "observation_content_mismatch",
    "extraction_incomplete",
    "temporal_occurrence_absent",
    "temporal_occurrence_inconsistent",
    "source_temporal_parity_failure",
    "no_observation_at_or_before_as_of",
    "incomplete_coverage_within_declared_horizon",
]
OperationalEvidenceSelectionStatus = Literal[
    "complete_within_declared_horizon",
    "incomplete_within_declared_horizon",
    "refused",
]
StoreIndependentValidationStatus = Literal[
    "structurally_self_consistent",
    "fingerprint_mismatch",
    "invalid",
]
ExpectedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_supplied",
]
EmbeddedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_computed",
]
StoreBoundMembershipMode = Literal[
    "require_equal_final_observed_membership",
    "named_captured_artifacts",
]
StoreBoundRevalidationStatus = Literal[
    "matches_final_observed_membership",
    "valid_for_named_captured_artifacts",
    "observed_membership_changed",
    "refused",
]
NamedCapturedMaterialRelation = Literal[
    "matched",
    "changed",
    "unavailable",
    "not_evaluated",
]
CapturedTemporalMaterialRelation = Literal[
    "matched",
    "changed",
    "not_fully_observed",
    "not_evaluated",
]
ObservedMembershipRelation = Literal[
    "equal_to_snapshot_final",
    "different_from_snapshot_final",
    "not_fully_observed",
    "not_evaluated",
]


_ISSUE_RANK = {
    code: index for index, code in enumerate(
        (
            "unsupported_operational_evidence",
            "invalid_bounded_material",
            "excessive_bounded_material",
            "source_evidence_unavailable",
            "temporal_evidence_unavailable",
            "source_store_changed_during_capture",
            "temporal_store_changed_during_capture",
            "checksum_mismatch",
            "provenance_closure_failure",
            "observation_content_mismatch",
            "extraction_incomplete",
            "temporal_occurrence_absent",
            "temporal_occurrence_inconsistent",
            "source_temporal_parity_failure",
            "no_observation_at_or_before_as_of",
            "incomplete_coverage_within_declared_horizon",
        )
    )
}
_REFUSAL_CODES = frozenset(tuple(_ISSUE_RANK)[:14])
_INCOMPLETE_CODES = frozenset(tuple(_ISSUE_RANK)[14:])
_DETAIL_PATTERN = r"^[a-z][a-z0-9_]{0,63}$"
_TAGGED_SHA_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def _bounded_safe_text(value: object, *, description: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 300:
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
    if re.search(r"\b(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]", lowered):
        raise ValueError(f"{description} must not contain credentials")
    return value


def _deep_plain(value: object, active: set[int] | None = None):
    """Convert nested public content to ordinary Python values with cycles refused."""
    if active is None:
        active = set()
    if isinstance(value, (str, bytes, int, float, bool, type(None), datetime)):
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
        if isinstance(value, dict):
            return {
                _deep_plain(key, active): _deep_plain(item, active)
                for key, item in value.items()
            }
        if isinstance(value, (tuple, list)):
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
        if isinstance(value, BaseModel):
            return _deep_plain(value)
        return value


class EvidenceAssuranceError(Exception):
    _allowed_codes: tuple[str, ...] = ()

    def __init__(self, error_code: str, message: str) -> None:
        if error_code not in self._allowed_codes:
            raise ValueError("error code is not valid for this exception type")
        safe_message = _bounded_safe_text(message, description="message")
        super().__init__(f"{error_code}: {safe_message}")
        self.error_code = error_code
        self.message = safe_message


class EvidenceAssuranceConfigurationError(EvidenceAssuranceError):
    _allowed_codes = ("EA_DEPENDENCY_INVALID",)


class EvidenceAssuranceQueryError(EvidenceAssuranceError):
    _allowed_codes = ("EA_REQUEST_INVALID", "EA_SELECTION_POLICY_INVALID")


class OperationalEvidenceSelectionPolicy(_StrictFrozen):
    kind: Literal["independent_latest_at_or_before_as_of"]
    version: Literal["ea001.operational_selection.v1"]
    occurrence_axis: Literal["received_at"]
    attempt_coverage_axis: Literal["effective_wall_time"]
    source_time_use: Literal["disclosure_only"]


class OperationalEvidenceSelectionRequest(_StrictFrozen):
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: AwareDatetime
    as_of: AwareDatetime
    policy: OperationalEvidenceSelectionPolicy

    @field_validator("scope", mode="before")
    @classmethod
    def _scope(cls, value):
        return Ds004OperationalEvidenceScope.model_validate(_deep_plain(value))

    @field_validator("policy", mode="before")
    @classmethod
    def _policy(cls, value):
        return OperationalEvidenceSelectionPolicy.model_validate(_deep_plain(value))

    @field_validator("horizon_started_at", "as_of")
    @classmethod
    def _utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _ordered_interval(self):
        if self.horizon_started_at > self.as_of:
            raise ValueError("horizon_started_at must be at or before as_of")
        return self


class OperationalEvidenceMaterialLimits(_StrictFrozen):
    schema_version: Literal["1"]
    maximum_in_horizon_attempts: Literal[4096]
    maximum_occurrence_members: Literal[16384]
    maximum_retained_artifacts: Literal[16384]
    maximum_retained_metadata_bytes: Literal[67108864]


class OperationalEvidenceIssue(_StrictFrozen):
    code: OperationalEvidenceIssueCode
    detail_code: Annotated[StrictStr, StringConstraints(pattern=_DETAIL_PATTERN)]
    route_index: Annotated[StrictInt, Field(ge=0)] | None
    detail: Annotated[StrictStr, StringConstraints(min_length=1, max_length=300)]

    @field_validator("detail")
    @classmethod
    def _safe_detail(cls, value: str) -> str:
        return _bounded_safe_text(value, description="detail")


_StrictIndex = Annotated[StrictInt, Field(ge=0)]


class OperationalProvenanceRoute(_StrictFrozen):
    attempt_index: _StrictIndex
    run_index: _StrictIndex
    temporal_attempt_index: _StrictIndex
    envelope_index: _StrictIndex | None
    payload_artifact_index: _StrictIndex | None
    extraction_index: _StrictIndex | None
    quarantine_index: _StrictIndex | None
    observation_index: _StrictIndex | None
    temporal_occurrence_index: _StrictIndex | None
    artifact_descriptor_indices: tuple[_StrictIndex, ...]
    coverage_disposition: CoverageDisposition

    @model_validator(mode="after")
    def _unique_descriptor_indices(self):
        if len(self.artifact_descriptor_indices) != len(
            set(self.artifact_descriptor_indices)
        ):
            raise ValueError("artifact descriptor indices must be unique")
        if tuple(sorted(self.artifact_descriptor_indices)) != (
            self.artifact_descriptor_indices
        ):
            raise ValueError("artifact descriptor indices must be ordered")
        return self


class OperationalCoverageSummary(_StrictFrozen):
    attempt_route_indices: tuple[_StrictIndex, ...]
    property_observed_route_indices: tuple[_StrictIndex, ...]
    omitted_property_route_indices: tuple[_StrictIndex, ...]
    empty_snapshot_route_indices: tuple[_StrictIndex, ...]
    failed_route_indices: tuple[_StrictIndex, ...]
    quarantined_route_indices: tuple[_StrictIndex, ...]
    extraction_incomplete_route_indices: tuple[_StrictIndex, ...]
    completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
    ]

    @model_validator(mode="after")
    def _ordered_unique_indices(self):
        for name in self.__class__.model_fields:
            if name == "completeness":
                continue
            values = getattr(self, name)
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} must be unique and ordered")
        return self


class SelectedSourceObservation(_StrictFrozen):
    outcome: Literal[
        "selected_source_observation",
        "no_observation_at_or_before_as_of",
    ]
    temporal_occurrence_index: _StrictIndex | None
    provenance_route_index: _StrictIndex | None
    pre_horizon_seed: StrictBool
    selected_received_at: AwareDatetime | None
    observation_age_seconds: CanonicalNonnegativeDecimal | None
    age_basis: Literal["received_at", "not_applicable"]

    @field_validator("selected_received_at")
    @classmethod
    def _selected_utc(cls, value: datetime | None) -> datetime | None:
        return None if value is None else value.astimezone(UTC)

    @model_validator(mode="after")
    def _coherent_selection(self):
        fields = (
            self.temporal_occurrence_index,
            self.provenance_route_index,
            self.selected_received_at,
            self.observation_age_seconds,
        )
        if self.outcome == "no_observation_at_or_before_as_of":
            if any(value is not None for value in fields):
                raise ValueError("absent selection cannot carry selected values")
            if self.pre_horizon_seed or self.age_basis != "not_applicable":
                raise ValueError("absent selection has non-applicable age")
        else:
            if any(value is None for value in fields):
                raise ValueError("selected observation requires every selected value")
            if self.age_basis != "received_at":
                raise ValueError("selected observation age uses received_at")
        return self


class CapturedViewFence(_StrictFrozen):
    initial_source_token: OperationalApiInventoryToken
    initial_temporal_token: TemporalSelectionInventoryToken
    final_source_token: OperationalApiInventoryToken
    final_temporal_token: TemporalSelectionInventoryToken
    relation: Literal["equal_at_observed_fences"]

    @model_validator(mode="after")
    def _equal_fences(self):
        if self.initial_source_token != self.final_source_token:
            raise ValueError("source inventory changed between observed fences")
        if self.initial_temporal_token != self.final_temporal_token:
            raise ValueError("temporal inventory changed between observed fences")
        return self


class OperationalEvidenceAssurance(_StrictFrozen):
    payload_byte_check: Literal["matched", "not_applicable"]
    metadata_same_read_check: Literal["matched"]
    provenance_closure: Literal["closed"]
    observation_content_relation: Literal[
        "exact_value_and_type", "not_applicable"
    ]
    occurrence_membership_relation: Literal["reconciled"]
    attempt_coverage_membership_relation: Literal["reconciled"]
    captured_view_relation: Literal["equal_at_observed_fences"]
    semantic_compatibility: Literal["not_assessed"]
    accountable_occurrence: Literal["not_assessed"]


class CapturedOperationalEvidenceSnapshot(_StrictFrozen):
    schema_version: Literal["1"]
    request: OperationalEvidenceSelectionRequest
    fixed_limits: OperationalEvidenceMaterialLimits
    source_material: Ds004OperationalEvidenceMaterial
    temporal_material: TemporalSelectionMaterial
    provenance_routes: tuple[OperationalProvenanceRoute, ...]
    selected: SelectedSourceObservation
    coverage: OperationalCoverageSummary
    capture_fence: CapturedViewFence
    assurance: OperationalEvidenceAssurance
    issues: tuple[OperationalEvidenceIssue, ...]
    content_fingerprint: TaggedSha256

    @model_validator(mode="after")
    def _basic_snapshot_invariants(self):
        if any(issue.code not in _INCOMPLETE_CODES for issue in self.issues):
            raise ValueError("snapshot may carry only incomplete issues")
        if _ordered_issues(self.issues) != self.issues:
            raise ValueError("snapshot issues are not canonically ordered")
        return self


class OperationalNamedArtifactRevalidation(_StrictFrozen):
    artifact_descriptor_index: _StrictIndex
    relation: Literal["matched"]
    observed_byte_count: _StrictIndex
    observed_captured_file_sha256: TaggedSha256


class OperationalEvidenceSelectionResult(_StrictFrozen):
    status: OperationalEvidenceSelectionStatus
    request: OperationalEvidenceSelectionRequest
    snapshot: CapturedOperationalEvidenceSnapshot | None
    issues: tuple[OperationalEvidenceIssue, ...]

    @model_validator(mode="after")
    def _carry_once(self):
        if _ordered_issues(self.issues) != self.issues:
            raise ValueError("result issues are not canonically ordered")
        if self.status == "refused":
            if self.snapshot is not None or not self.issues:
                raise ValueError("refused selection carries issues and no snapshot")
            if any(issue.code not in _REFUSAL_CODES or issue.route_index is not None
                   for issue in self.issues):
                raise ValueError("refusal issues must be refusal codes without routes")
        else:
            if self.snapshot is None or self.issues:
                raise ValueError("successful selection carries one snapshot only")
            if self.snapshot.request != self.request:
                raise ValueError("selection request and snapshot request differ")
            if self.status == "complete_within_declared_horizon":
                if self.snapshot.issues or self.snapshot.coverage.completeness != self.status:
                    raise ValueError("complete selection has inconsistent snapshot")
            elif (not self.snapshot.issues
                  or self.snapshot.coverage.completeness != self.status):
                raise ValueError("incomplete selection has inconsistent snapshot")
        return self


class OperationalEvidenceStoreRevalidationResult(_StrictFrozen):
    status: StoreBoundRevalidationStatus
    membership_mode: StoreBoundMembershipMode
    snapshot_content_fingerprint: TaggedSha256 | None
    snapshot_validation_status: StoreIndependentValidationStatus
    expected_artifact_count: _StrictIndex
    expected_provenance_route_count: _StrictIndex
    named_source_material_relation: NamedCapturedMaterialRelation
    captured_temporal_material_relation: CapturedTemporalMaterialRelation
    source_membership_relation: ObservedMembershipRelation
    temporal_membership_relation: ObservedMembershipRelation
    named_artifact_results: tuple[OperationalNamedArtifactRevalidation, ...]
    issues: tuple[OperationalEvidenceIssue, ...]

    @model_validator(mode="after")
    def _result_shape(self):
        if _ordered_issues(self.issues) != self.issues:
            raise ValueError("revalidation issues are not canonically ordered")
        if any(
            issue.route_index is not None
            and issue.route_index >= self.expected_provenance_route_count
            for issue in self.issues
        ):
            raise ValueError("revalidation issue route index is out of range")
        indices = tuple(row.artifact_descriptor_index
                        for row in self.named_artifact_results)
        if self.named_source_material_relation == "matched":
            if indices != tuple(range(self.expected_artifact_count)):
                raise ValueError("matched named rows must cover every artifact")
        elif self.named_artifact_results:
            raise ValueError("unmatched named material carries no artifact rows")
        if self.snapshot_validation_status != "structurally_self_consistent":
            if (
                self.status != "refused"
                or self.snapshot_content_fingerprint is not None
                or self.expected_artifact_count != 0
                or self.expected_provenance_route_count != 0
                or self.named_source_material_relation != "not_evaluated"
                or self.captured_temporal_material_relation != "not_evaluated"
                or self.source_membership_relation != "not_evaluated"
                or self.temporal_membership_relation != "not_evaluated"
                or self.named_artifact_results
            ):
                raise ValueError("invalid snapshot revalidation shape is inconsistent")
        return self


class OperationalEvidenceSnapshotValidationResult(_StrictFrozen):
    status: StoreIndependentValidationStatus
    computed_fingerprint: TaggedSha256 | None
    embedded_fingerprint_relation: EmbeddedFingerprintRelation
    expected_fingerprint_relation: ExpectedFingerprintRelation
    source_bytes: Literal["not_rechecked"]
    temporal_store_membership: Literal["not_rechecked"]
    detail_code: Annotated[StrictStr, StringConstraints(pattern=_DETAIL_PATTERN)]
    detail: Annotated[StrictStr, StringConstraints(min_length=1, max_length=300)]

    @field_validator("detail")
    @classmethod
    def _safe_detail(cls, value: str) -> str:
        return _bounded_safe_text(value, description="detail")

    @model_validator(mode="after")
    def _validation_shape(self):
        if self.status == "invalid":
            if self.computed_fingerprint is not None or (
                self.embedded_fingerprint_relation != "not_computed"
            ):
                raise ValueError("invalid validation result cannot claim computation")
        elif self.computed_fingerprint is None:
            raise ValueError("derivable snapshot requires computed fingerprint")
        return self


def _ordered_issues(
    issues: tuple[OperationalEvidenceIssue, ...],
) -> tuple[OperationalEvidenceIssue, ...]:
    return tuple(sorted(
        issues,
        key=lambda issue: (
            _ISSUE_RANK[issue.code],
            -1 if issue.route_index is None else issue.route_index,
            issue.detail_code,
        ),
    ))


FIXED_LIMITS = OperationalEvidenceMaterialLimits(
    schema_version="1",
    maximum_in_horizon_attempts=4096,
    maximum_occurrence_members=16384,
    maximum_retained_artifacts=16384,
    maximum_retained_metadata_bytes=67108864,
)
