"""TS-001 temporal evidence contracts.

Everything here is *temporal evidence* — a rebuildable projection of what
sources reported and when it was acquired — never a claim about actual
system state. Subject/property references are explicitly unresolved
source-native identity; a future identity-binding layer maps them to
system entities without rewriting this history.
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from backend.data_sources.contracts import SourceTimeMarker


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
