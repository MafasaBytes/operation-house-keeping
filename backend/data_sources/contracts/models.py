"""Contract models for the data_sources boundary.

These models are the module's public contract: everything acquired from an
external source is represented, persisted, and reported through them. They
deliberately carry no engineering semantics — that belongs to the later
normalization layer.
"""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Sha256Checksum = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]
RecordId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")]

# Configuration keys that suggest a secret is being smuggled into a source
# definition. Credentials may only be referenced by name, never embedded.
_SECRET_KEY_MARKERS = ("password", "token", "secret", "api_key", "apikey", "credential")

_AwareDatetime = Annotated[datetime, Field()]


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("timestamps must be timezone-aware")
    return value


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceDefinition(_FrozenModel):
    source_id: str = Field(min_length=1)
    display_name: str
    source_kind: str
    connector_type: str
    configuration: dict[str, str] = Field(default_factory=dict)
    credential_reference: str | None = None
    declared_content_types: list[str] = Field(default_factory=list)
    enabled: bool = True

    @field_validator("configuration")
    @classmethod
    def _no_embedded_secrets(cls, value: dict[str, str]) -> dict[str, str]:
        for key in value:
            lowered = key.lower()
            if any(marker in lowered for marker in _SECRET_KEY_MARKERS):
                raise ValueError(
                    f"configuration key {key!r} looks like a secret; use "
                    "credential_reference to name an external secret instead"
                )
        return value


Maturity = Literal["planned", "experimental", "validated"]
AcquisitionMode = Literal["snapshot", "poll", "stream"]


class ConnectorManifest(_FrozenModel):
    connector_type: str
    source_families: list[str]
    supported_formats_or_protocols: list[str]
    acquisition_modes: list[AcquisitionMode]
    supported_extraction_levels: list[int]
    read_only: bool
    incremental_read_support: bool
    required_dependencies: list[str]
    maturity: Maturity
    known_limitations: list[str]


class StatusCheck(_FrozenModel):
    passed: bool
    evidence: str

    @model_validator(mode="after")
    def _passed_needs_evidence(self) -> "StatusCheck":
        if self.passed and not self.evidence.strip():
            raise ValueError("a passing status check must state its evidence")
        return self


class ConnectorStatusReport(_FrozenModel):
    """The declared → available → configured → connected → validated ladder.

    Each rung is computed at runtime with its evidence; nothing here may be
    hard-coded true.
    """

    connector_type: str
    source_id: str
    declared: StatusCheck
    available: StatusCheck
    configured: StatusCheck
    connected: StatusCheck
    validated: StatusCheck


class RawRecord(_FrozenModel):
    record_id: RecordId
    source_id: str
    source_native_id: str | None = None
    ingestion_run_id: str
    captured_at: datetime
    source_observed_at: datetime | None = None
    content_type: str
    payload_checksum: Sha256Checksum
    immutable_payload_reference: str
    provenance: dict[str, str] = Field(default_factory=dict)
    quality_flags: list[str] = Field(default_factory=list)
    # stable API source-locator facts (DS-004); None for file sources
    api_locator: "ApiSourceLocator | None" = None

    @field_validator("captured_at", "source_observed_at")
    @classmethod
    def _aware(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _require_aware(value)


RunStatus = Literal[
    "succeeded",
    "completed_with_quarantine",
    "completed_with_acquisition_failures",
    "failed",
]


class IngestionRun(_FrozenModel):
    run_id: str
    source_id: str
    started_at: datetime
    finished_at: datetime
    status: RunStatus
    records_seen: int = Field(ge=0)
    records_accepted: int = Field(ge=0)
    records_duplicate: int = Field(ge=0)
    records_quarantined: int = Field(ge=0)
    records_partial: int = Field(default=0, ge=0)
    attempts_planned: int = Field(default=0, ge=0)
    attempts_succeeded: int = Field(default=0, ge=0)
    attempts_failed: int = Field(default=0, ge=0)
    error_summary: str | None = None

    @field_validator("started_at", "finished_at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        return _require_aware(value)


HealthStatus = Literal["ok", "degraded", "failed", "unknown"]


class SourceHealth(_FrozenModel):
    source_id: str
    status: HealthStatus
    checked_at: datetime
    last_success_at: datetime | None = None
    last_record_at: datetime | None = None
    diagnostic_code: str | None = None
    # typed API evidence (DS-004); None for non-API sources and old JSON
    api_evidence: "ApiHealthEvidence | None" = None

    @field_validator("checked_at", "last_success_at", "last_record_at")
    @classmethod
    def _aware(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _require_aware(value)


class QuarantineRecord(_FrozenModel):
    record_id: RecordId
    stage: Literal["format_detection", "extraction"]
    error_code: str
    redacted_message: str
    quarantined_at: datetime

    @field_validator("redacted_message")
    @classmethod
    def _no_absolute_paths(cls, value: str) -> str:
        for token in value.split():
            candidate = token.strip("'\"()[],;")
            if candidate.startswith("/") or (
                len(candidate) > 2 and candidate[1] == ":" and candidate[2] in "\\/"
            ):
                raise ValueError(
                    "quarantine messages must be redacted; absolute paths are not allowed"
                )
        return value

    @field_validator("quarantined_at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        return _require_aware(value)


class ExtractedCell(_FrozenModel):
    """One extracted field value, traceable to its exact raw location.

    Values are strings (or None for an empty field): extraction never
    coerces types, guesses units, or interprets meaning.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    raw_record_id: RecordId
    physical_row_index: int = Field(ge=0)
    column_index: int = Field(ge=0)
    column_name: str
    value: str | None


class ExtractedRow(_FrozenModel):
    physical_row_index: int = Field(ge=0)
    cells: list[ExtractedCell]


class ExtractedTable(_FrozenModel):
    raw_record_id: RecordId
    header_row_index: int = Field(ge=0)
    columns: list[str]
    rows: list[ExtractedRow]
    warnings: list[str] = Field(default_factory=list)
