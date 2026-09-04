"""TS-001 temporal evidence contracts.

Everything here is *temporal evidence* — a rebuildable projection of what
sources reported and when it was acquired — never a claim about actual
system state. Subject/property references are explicitly unresolved
source-native identity; a future identity-binding layer maps them to
system entities without rewriting this history.
"""

from datetime import UTC, datetime
import hashlib
import json
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StringConstraints,
    field_validator,
    model_validator,
)

from backend.data_sources.contracts import (
    Ds004OperationalEvidenceScope,
    SourceTimeMarker,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# errors
class TemporalError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class TemporalConfigurationError(TemporalError):
    """The temporal store is misconfigured (e.g. placed inside the
    immutable evidence-store root)."""


class TemporalStoreBusyError(TemporalError):
    """Actual write contention on the temporal database. Only the
    contended write is rejected — never a projector's whole lifetime."""


class TemporalStoreError(TemporalError):
    """Integrity or consistency failure in the temporal store."""


class TemporalQueryError(TemporalError):
    """Invalid input to a public temporal query (e.g. a naive cutoff)."""


# identity
class SourceSubjectRef(_Frozen):
    """Unresolved source-native subject identity — NOT a system entity."""

    source_id: str = Field(min_length=1)
    adapter_id: str = Field(min_length=1)
    subject_identifier: str = Field(min_length=1)


class SourcePropertyRef(_Frozen):
    extraction_route: str = Field(min_length=1)
    item_key: str = Field(min_length=1)
    json_pointer: str = Field(min_length=1)


# The temporal property key is the complete six-dimension pair; every
# chain lookup, uniqueness rule, and index uses all six.


class AttemptOrderKey(_Frozen):
    """The single deterministic processing order, used everywhere."""

    attempt_started_at: AwareDatetime
    ingestion_run_id: str
    sweep_position: int = Field(ge=0)
    attempt_id: str

    def sort_tuple(self) -> tuple[str, str, int, str]:
        return (
            self.attempt_started_at.astimezone(UTC).isoformat(),
            self.ingestion_run_id,
            self.sweep_position,
            self.attempt_id,
        )


# ledger
AttemptOutcome = Literal[
    "observations_projected", "acquisition_failed", "quarantined"
]
EffectiveTimeBasis = Literal["received_at", "finished_at_no_response"]


class TemporalAttemptEvent(_Frozen):
    """Immutable ledger row: proof that an acquisition attempt was fully
    processed, the atomic parent of its occurrences, and the coverage
    backbone. Carries no source-clock marker — clock evidence derives
    only from observations."""

    attempt_id: str
    source_id: str
    adapter_id: str
    endpoint_id: str
    item_key: str
    sweep_position: int = Field(ge=0)
    ingestion_run_id: str
    attempt_started_at: AwareDatetime
    received_at: AwareDatetime | None = None
    finished_at: AwareDatetime
    effective_wall_time: AwareDatetime
    effective_time_basis: EffectiveTimeBasis
    outcome: AttemptOutcome
    raw_record_id: str | None = None
    payload_checksum: str | None = None
    observation_count: int = Field(ge=0)  # zero is a real, honest result
    failure_or_quarantine_code: str | None = None
    source_warning_count: int = Field(ge=0)
    projector_version: str


ChangeClass = Literal["first_seen", "unchanged", "changed"]


class TemporalOccurrence(_Frozen):
    """Immutable point fact: this value was observed at this occurrence.
    Never proof the value stayed true until the next poll."""

    occurrence_id: str
    attempt_id: str
    subject: SourceSubjectRef
    property: SourcePropertyRef
    observation_id: str
    raw_record_id: str
    payload_checksum: str
    attempt_started_at: AwareDatetime
    ingestion_run_id: str
    sweep_position: int = Field(ge=0)
    received_at: AwareDatetime  # non-nullable: successes always have it
    finished_at: AwareDatetime
    source_time: SourceTimeMarker
    clock_segment_id: str | None = None  # None <=> unavailable source time
    value_json: str
    json_type: str
    declared_unit: str | None = None
    change_class: ChangeClass
    previous_occurrence_id: str | None = None
    quality_flags: list[str] = Field(default_factory=list)

    @property
    def effective_wall_time(self) -> datetime:
        return self.received_at


class ClockSegmentOpening(_Frozen):
    """Immutable opening evidence for a source-clock segment. There is no
    closing or last-value field; segment extent is derived from rows.
    ``monotonic_decrease_observed`` asserts only that a decrease was
    observed in acquisition processing order — never that the source
    restarted."""

    segment_id: str
    source_id: str
    adapter_id: str
    clock_id: str  # monotonic clock id, or "wall_clock:<basis>"
    boundary_reason: Literal["initial", "monotonic_decrease_observed"]
    opened_by_attempt_id: str
    opened_at_effective_wall_time: AwareDatetime


class ProjectionCheckpoint(_Frozen):
    """Mutable optimization only. Ground truth of processing is the
    ledger; a checkpoint inconsistent with the ledger requires rebuild."""

    source_id: str
    last_attempt_started_at: AwareDatetime
    last_ingestion_run_id: str
    last_sweep_position: int
    last_attempt_id: str
    projector_version: str
    schema_version: str

    def order_key(self) -> AttemptOrderKey:
        return AttemptOrderKey(
            attempt_started_at=self.last_attempt_started_at,
            ingestion_run_id=self.last_ingestion_run_id,
            sweep_position=self.last_sweep_position,
            attempt_id=self.last_attempt_id,
        )


class HaltInfo(_Frozen):
    source_id: str
    reason: Literal["extraction_incomplete", "TEMPORAL_REBUILD_REQUIRED"]
    at_attempt_id: str | None = None
    detail: str = ""


class ProjectionReport(BaseModel):
    """Returned, never persisted."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    attempts_processed: int = 0
    occurrences_created: int = 0
    attempts_by_outcome: dict[str, int] = Field(default_factory=dict)
    deferred_incomplete: list[str] = Field(default_factory=list)
    halted: HaltInfo | None = None


# EA-001 Slice A: bounded read material only. These contracts add no row,
# checkpoint, persistence, or assessment meaning to the temporal projection.
TaggedSha256 = Annotated[
    str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")
]


class _SelectionFrozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


def _canonical_value(value):
    if isinstance(value, BaseModel):
        return {name: _canonical_value(getattr(value, name))
                for name in value.__class__.model_fields}
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, tuple | list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _canonical_value(item) for key, item in value.items()}
    return value


def temporal_selection_digest(value) -> str:
    payload = json.dumps(
        _canonical_value(value), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _occurrence_order(occurrence: TemporalOccurrence):
    return (
        occurrence.received_at.astimezone(UTC),
        occurrence.attempt_started_at.astimezone(UTC),
        occurrence.ingestion_run_id,
        occurrence.sweep_position,
        occurrence.attempt_id,
        occurrence.occurrence_id,
    )


def _attempt_order(event: TemporalAttemptEvent):
    return (
        event.attempt_started_at.astimezone(UTC),
        event.ingestion_run_id,
        event.sweep_position,
        event.attempt_id,
    )


class TemporalSelectionInventoryToken(_SelectionFrozen):
    schema_version: str = Field(min_length=1)
    projector_version: str = Field(min_length=1)
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: AwareDatetime
    as_of: AwareDatetime
    occurrence_membership_sha256: TaggedSha256
    attempt_coverage_membership_sha256: TaggedSha256
    clock_opening_membership_sha256: TaggedSha256

    @field_validator("horizon_started_at", "as_of")
    @classmethod
    def _utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _interval(self):
        if self.horizon_started_at > self.as_of:
            raise ValueError("horizon_started_at must be at or before as_of")
        return self


class TemporalSelectionMaterial(_SelectionFrozen):
    schema_version: str = Field(min_length=1)
    projector_version: str = Field(min_length=1)
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: AwareDatetime
    as_of: AwareDatetime
    selected_occurrence_index: StrictInt | None
    selected_occurrence_is_pre_horizon_seed: StrictBool
    occurrence_membership: tuple[TemporalOccurrence, ...]
    attempt_coverage_membership: tuple[TemporalAttemptEvent, ...]
    clock_segment_openings: tuple[ClockSegmentOpening, ...]
    transaction_membership_sha256: TaggedSha256

    @field_validator("occurrence_membership", mode="before")
    @classmethod
    def _rebuild_occurrences(cls, value):
        return tuple(TemporalOccurrence.model_validate(
            item.model_dump(mode="python", warnings=False)
            if isinstance(item, BaseModel) else item) for item in value)

    @field_validator("attempt_coverage_membership", mode="before")
    @classmethod
    def _rebuild_attempts(cls, value):
        return tuple(TemporalAttemptEvent.model_validate(
            item.model_dump(mode="python", warnings=False)
            if isinstance(item, BaseModel) else item) for item in value)

    @field_validator("clock_segment_openings", mode="before")
    @classmethod
    def _rebuild_openings(cls, value):
        return tuple(ClockSegmentOpening.model_validate(
            item.model_dump(mode="python", warnings=False)
            if isinstance(item, BaseModel) else item) for item in value)

    @field_validator("horizon_started_at", "as_of")
    @classmethod
    def _utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _complete_revalidation(self):
        start, end = self.horizon_started_at, self.as_of
        if start > end:
            raise ValueError("horizon_started_at must be at or before as_of")
        if len(self.occurrence_membership) > 16_384:
            raise ValueError("occurrence membership exceeds 16384")
        if len(self.attempt_coverage_membership) > 4_096:
            raise ValueError("attempt coverage membership exceeds 4096")
        if tuple(sorted(self.occurrence_membership, key=_occurrence_order)) != (
                self.occurrence_membership):
            raise ValueError("occurrence membership is not canonically ordered")
        occurrence_ids = [row.occurrence_id for row in self.occurrence_membership]
        if len(occurrence_ids) != len(set(occurrence_ids)):
            raise ValueError("occurrence membership contains duplicates")
        if tuple(sorted(self.attempt_coverage_membership, key=_attempt_order)) != (
                self.attempt_coverage_membership):
            raise ValueError("attempt coverage membership is not canonically ordered")
        attempt_ids = [row.attempt_id for row in self.attempt_coverage_membership]
        if len(attempt_ids) != len(set(attempt_ids)):
            raise ValueError("attempt coverage membership contains duplicates")

        scope = self.scope
        for occurrence in self.occurrence_membership:
            if (
                occurrence.subject.source_id != scope.source_id
                or occurrence.subject.adapter_id != scope.adapter_id
                or occurrence.subject.subject_identifier != scope.subject_identifier
                or occurrence.property.extraction_route != scope.extraction_route
                or occurrence.property.item_key != scope.item_key
                or occurrence.property.json_pointer != scope.json_pointer
                or occurrence.received_at.astimezone(UTC) > end
            ):
                raise ValueError("occurrence lies outside the exact selection scope")
        for event in self.attempt_coverage_membership:
            effective = event.effective_wall_time.astimezone(UTC)
            if (
                event.source_id != scope.source_id
                or event.adapter_id != scope.adapter_id
                or event.endpoint_id != scope.endpoint_id
                or event.item_key != scope.item_key
                or not start <= effective <= end
                or event.projector_version != self.projector_version
            ):
                raise ValueError("attempt lies outside exact coverage membership")
            expected_effective = event.received_at or event.finished_at
            expected_basis = (
                "received_at" if event.received_at is not None
                else "finished_at_no_response")
            if (event.effective_wall_time != expected_effective
                    or event.effective_time_basis != expected_basis):
                raise ValueError("attempt effective-time contract is inconsistent")

        attempt_by_id = {
            row.attempt_id: row for row in self.attempt_coverage_membership}
        for occurrence in self.occurrence_membership:
            if occurrence.received_at.astimezone(UTC) < start:
                continue
            event = attempt_by_id.get(occurrence.attempt_id)
            if event is None or (
                event.outcome != "observations_projected"
                or event.observation_count < 1
                or event.raw_record_id != occurrence.raw_record_id
                or event.payload_checksum != occurrence.payload_checksum
                or event.attempt_started_at != occurrence.attempt_started_at
                or event.ingestion_run_id != occurrence.ingestion_run_id
                or event.sweep_position != occurrence.sweep_position
                or event.received_at != occurrence.received_at
                or event.finished_at != occurrence.finished_at
            ):
                raise ValueError(
                    "in-horizon occurrence and attempt coverage do not close")

        selected = self.selected_occurrence_index
        if selected is None:
            if self.selected_occurrence_is_pre_horizon_seed:
                raise ValueError("absent selection cannot be a pre-horizon seed")
            if self.occurrence_membership:
                raise ValueError("nonempty occurrence membership requires selection")
        else:
            if selected < 0 or selected >= len(self.occurrence_membership):
                raise ValueError("selected occurrence index is out of range")
            selected_row = self.occurrence_membership[selected]
            if selected_row != max(self.occurrence_membership, key=_occurrence_order):
                raise ValueError("selected occurrence is not latest at the cutoff")
            is_seed = selected_row.received_at.astimezone(UTC) < start
            if is_seed != self.selected_occurrence_is_pre_horizon_seed:
                raise ValueError("pre-horizon seed label is inconsistent")
        before_horizon = [row for row in self.occurrence_membership
                          if row.received_at.astimezone(UTC) < start]
        if len(before_horizon) > 1 or (
                before_horizon and not self.selected_occurrence_is_pre_horizon_seed):
            raise ValueError("only the selected pre-horizon seed may precede horizon")

        opening_ids = [row.segment_id for row in self.clock_segment_openings]
        opening_order = [(
            row.source_id, row.adapter_id, row.clock_id,
            row.opened_at_effective_wall_time.astimezone(UTC), row.segment_id)
            for row in self.clock_segment_openings]
        if (len(opening_ids) != len(set(opening_ids))
                or opening_order != sorted(opening_order)):
            raise ValueError("clock openings must be unique and ordered")
        required_openings = {row.clock_segment_id for row in self.occurrence_membership
                             if row.clock_segment_id is not None}
        if set(opening_ids) != required_openings:
            raise ValueError("clock opening membership does not close occurrences")
        if any(row.source_id != scope.source_id
               or row.adapter_id != scope.adapter_id
               for row in self.clock_segment_openings):
            raise ValueError("clock opening lies outside exact source scope")

        payload = self.model_dump(
            mode="python", exclude={"transaction_membership_sha256"})
        if temporal_selection_digest(payload) != self.transaction_membership_sha256:
            raise ValueError("transaction membership digest is stale")
        return self
