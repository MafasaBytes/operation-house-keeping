"""Operational API contracts (DS-004).

Central distinctions enforced here:

- an **AcquisitionAttempt** is occurrence evidence — persisted for every
  attempted item including byte-identical repeats and failures; a
  **RawRecord** is content-addressed payload evidence. A repeated response
  references an existing raw record from a new attempt.
- source time is a discriminated marker (wall-clock | monotonic |
  unavailable) — a monotonic source clock is never converted into a
  fabricated wall-clock datetime.
- an observation's ``value_json`` is an extractor-produced canonical JSON
  representation (numbers stay JSON numbers); the immutable payload plus
  JSON Pointer remain the source truth.
"""

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from backend.data_sources.contracts.cad import EntityId
from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.data_sources.contracts.models import (
    RecordId,
    Sha256Checksum,
    _FrozenModel,
)

FullTaggedSha256 = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]


# ---------------------------------------------------------------- time
class WallClockTimeMarker(_FrozenModel):
    kind: Literal["wall_clock"] = "wall_clock"
    value: AwareDatetime
    basis: str = Field(min_length=1)


class MonotonicTimeMarker(_FrozenModel):
    """A source-native monotonic clock reading, kept as the exact number
    lexeme — explicitly NOT a wall-clock time and never converted."""

    kind: Literal["monotonic"] = "monotonic"
    value: str = Field(pattern=r"^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?$")
    unit: Literal["seconds"]
    clock_id: str = Field(min_length=1)
    origin: Literal["unknown"]
    pointer: str


class UnavailableTimeMarker(_FrozenModel):
    kind: Literal["unavailable"] = "unavailable"
    reason: str = Field(min_length=1)


SourceTimeMarker = Annotated[
    Union[WallClockTimeMarker, MonotonicTimeMarker, UnavailableTimeMarker],
    Field(discriminator="kind"),
]


# ---------------------------------------------------------- acquisition
class AttemptFailure(_FrozenModel):
    error_code: str = Field(min_length=1)
    redacted_message: str


class AcquisitionAttempt(_FrozenModel):
    """One polling occurrence — always persisted, whatever the outcome."""

    attempt_id: EntityId
    ingestion_run_id: str
    source_id: str
    item_key: str = Field(min_length=1)
    adapter_id: str
    endpoint_id: str
    sweep_position: int = Field(ge=0)  # ordering evidence only, never identity
    started_at: AwareDatetime
    finished_at: AwareDatetime
    received_at: AwareDatetime | None = None  # only when a response arrived
    outcome: Literal["succeeded", "failed"]
    request_fingerprint: FullTaggedSha256
    request_canonical: str = Field(min_length=1)
    target_origin: str = Field(min_length=1)  # scheme://host:port, sanitized
    status_code: int | None = None
    allowlisted_headers: dict[str, str] = Field(default_factory=dict)
    transport_security: Literal["tls_verified", "plaintext_http_explicit"]
    response_size_bytes: int | None = Field(default=None, ge=0)
    retries_used: int = Field(ge=0)
    payload_checksum: Sha256Checksum | None = None
    raw_record_id: RecordId | None = None
    payload_reused: bool = False
    failure: AttemptFailure | None = None

    @model_validator(mode="after")
    def _outcome_coherence(self) -> "AcquisitionAttempt":
        if self.outcome == "succeeded":
            if self.payload_checksum is None or self.raw_record_id is None:
                raise ValueError(
                    "a succeeded attempt must reference its payload checksum "
                    "and raw record"
                )
            if self.received_at is None:
                raise ValueError("a succeeded attempt must record received_at")
            if self.failure is not None:
                raise ValueError("a succeeded attempt carries no failure")
        else:
            if self.failure is None:
                raise ValueError(
                    "a failed attempt must carry typed, sanitized failure evidence"
                )
            if self.payload_checksum is not None or self.raw_record_id is not None:
                raise ValueError("a failed attempt may not reference a payload")
        return self


class ApiSourceLocator(_FrozenModel):
    """Stable per-item facts attached to a raw record. Attempt-specific
    data (timestamps, status codes, retries, headers, transport evidence)
    lives ONLY on AcquisitionAttempt so the first occurrence's metadata is
    never mistaken for later duplicates."""

    adapter_id: str
    endpoint_id: str
    item_key: str
    request_fingerprint: FullTaggedSha256
    request_canonical: str
    source_content_type: str | None = None  # responses may omit it
    extraction_route: str = Field(min_length=1)  # e.g. "api:moonraker:v1"


# ---------------------------------------------------------- observation
JsonType = Literal["object", "array", "string", "number", "boolean", "null"]


class OperationalObservation(_FrozenModel):
    observation_id: EntityId
    raw_record_id: RecordId
    json_pointer: str = Field(min_length=1)
    subject_identifier: str = Field(min_length=1)  # source-native, pre-semantic
    value_json: str  # canonical JSON text; numbers are JSON numbers
    json_type: JsonType
    declared_unit: str | None = None  # only when the source supplies one
    semantics: Literal["snapshot"]
    source_time: SourceTimeMarker
    quality_flags: list[str] = Field(default_factory=list)


class ApiItemSummary(_FrozenModel):
    item_key: str
    endpoint_id: str
    observation_count: int = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)


class ApiExtractionManifest(_FrozenModel):
    raw_record_id: RecordId
    extractor: ExtractorIdentity
    adapter_id: str
    item_key: str
    observations: list[OperationalObservation] = Field(default_factory=list)
    levels_supported: list[int]
    levels_achieved: list[int]
    unsupported_features: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _levels_honest(self) -> "ApiExtractionManifest":
        extra = set(self.levels_achieved) - set(self.levels_supported)
        if extra:
            raise ValueError(f"levels_achieved {sorted(extra)} exceed supported")
        return self


# --------------------------------------------------------------- health
class ApiHealthEvidence(_FrozenModel):
    """Typed API health evidence — booleans, numbers, and timestamps are
    never encoded as strings."""

    consecutive_attempt_failures: int = Field(ge=0)
    last_attempt_error_code: str | None
    last_status_code: int | None
    last_retry_after_seconds: float | None
    clock_skew_seconds: float | None
    plaintext_http_explicit: bool
    last_successful_attempt_at: datetime | None


# -------------------------------------------------------- run precedence
def resolve_completed_run_status(
    records_quarantined: int, attempts_failed: int
) -> Literal["succeeded", "completed_with_quarantine",
             "completed_with_acquisition_failures"]:
    """Status precedence for runs that made acquisition progress.

    (1) `failed` is decided by the existing no-meaningful-progress rule
    before this helper is consulted. Then:
    (2) quarantine outranks acquisition failure — a quarantined retrieved
    record is reported even when other attempts also failed;
    (3) acquisition failures without quarantine;
    (4) succeeded. Attempt counters always expose combined cases.
    """
    if records_quarantined > 0:
        return "completed_with_quarantine"
    if attempts_failed > 0:
        return "completed_with_acquisition_failures"
    return "succeeded"
