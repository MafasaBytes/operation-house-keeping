"""Read-only DS-004 operational evidence material contracts for EA-001."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from backend.data_sources.contracts.api import (
    AcquisitionAttempt,
    FullTaggedSha256,
    OperationalObservation,
)
from backend.data_sources.contracts.errors import DataSourceError
from backend.data_sources.contracts.extraction import ExtractionResult
from backend.data_sources.contracts.models import IngestionRun, QuarantineRecord, RawRecord


SafeScopeText = Annotated[
    StrictStr, StringConstraints(min_length=1, max_length=512)
]

OperationalApiArtifactKind = Literal[
    "ingestion_run",
    "acquisition_attempt",
    "raw_envelope",
    "raw_payload",
    "extraction_result",
    "quarantine_record",
]

_ARTIFACT_RANK = {
    "ingestion_run": 0,
    "acquisition_attempt": 1,
    "raw_envelope": 2,
    "raw_payload": 3,
    "extraction_result": 4,
    "quarantine_record": 5,
}


class _StrictFrozen(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        revalidate_instances="always",
    )


class OperationalEvidenceReadError(DataSourceError):
    """A typed, redacted refusal from the bounded DS-004 read seam."""


class Ds004OperationalEvidenceScope(_StrictFrozen):
    """One exact source-native operational API property scope."""

    source_id: SafeScopeText
    adapter_id: SafeScopeText
    endpoint_id: SafeScopeText
    item_key: SafeScopeText
    subject_identifier: SafeScopeText
    extraction_route: SafeScopeText
    json_pointer: SafeScopeText


class OperationalApiArtifactDescriptor(_StrictFrozen):
    kind: OperationalApiArtifactKind
    logical_id: SafeScopeText
    byte_count: StrictInt = Field(ge=0)
    captured_file_sha256: FullTaggedSha256
    payload_checksum: FullTaggedSha256 | None

    @model_validator(mode="after")
    def _payload_fields(self):
        if self.kind == "raw_payload":
            if self.payload_checksum is None:
                raise ValueError("raw payload descriptor requires payload_checksum")
        elif self.payload_checksum is not None:
            raise ValueError("metadata descriptor cannot carry payload_checksum")
        return self


class OperationalApiInventoryToken(_StrictFrozen):
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: AwareDatetime
    as_of: AwareDatetime
    ordered_member_keys: tuple[SafeScopeText, ...]
    canonical_membership_sha256: FullTaggedSha256

    @field_validator("horizon_started_at", "as_of")
    @classmethod
    def _utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _interval_and_order(self):
        if self.horizon_started_at > self.as_of:
            raise ValueError("horizon_started_at must be at or before as_of")
        if tuple(sorted(set(self.ordered_member_keys))) != self.ordered_member_keys:
            raise ValueError("inventory member keys must be unique and ordered")
        return self


def _attempt_order(attempt: AcquisitionAttempt) -> tuple[str, str, int, str]:
    return (
        attempt.started_at.astimezone(UTC).isoformat(),
        attempt.ingestion_run_id,
        attempt.sweep_position,
        attempt.attempt_id,
    )


class Ds004OperationalEvidenceMaterial(_StrictFrozen):
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    artifacts: tuple[OperationalApiArtifactDescriptor, ...]
    runs: tuple[IngestionRun, ...]
    attempts: tuple[AcquisitionAttempt, ...]
    envelopes: tuple[RawRecord, ...]
    extractions: tuple[ExtractionResult, ...]
    quarantines: tuple[QuarantineRecord, ...]
    observations: tuple[OperationalObservation, ...]

    @model_validator(mode="after")
    def _ordered_unique(self):
        artifact_keys = tuple((_ARTIFACT_RANK[d.kind], d.logical_id)
                              for d in self.artifacts)
        if artifact_keys != tuple(sorted(set(artifact_keys))):
            raise ValueError("artifacts must be unique and canonically ordered")
        if tuple(r.run_id for r in self.runs) != tuple(
                sorted({r.run_id for r in self.runs})):
            raise ValueError("runs must be unique and ordered")
        if tuple(_attempt_order(a) for a in self.attempts) != tuple(
                sorted({_attempt_order(a) for a in self.attempts})):
            raise ValueError("attempts must be unique and canonically ordered")
        if tuple(r.record_id for r in self.envelopes) != tuple(
                sorted({r.record_id for r in self.envelopes})):
            raise ValueError("envelopes must be unique and ordered")
        if tuple(r.raw_record_id for r in self.extractions) != tuple(
                sorted({r.raw_record_id for r in self.extractions})):
            raise ValueError("extractions must be unique and ordered")
        if tuple(r.record_id for r in self.quarantines) != tuple(
                sorted({r.record_id for r in self.quarantines})):
            raise ValueError("quarantines must be unique and ordered")
        observation_keys = tuple(
            (o.raw_record_id, o.json_pointer, o.subject_identifier, o.observation_id)
            for o in self.observations)
        if observation_keys != tuple(sorted(set(observation_keys))):
            raise ValueError("observations must be unique and canonically ordered")
        return self


__all__ = [
    "Ds004OperationalEvidenceMaterial",
    "Ds004OperationalEvidenceScope",
    "OperationalApiArtifactDescriptor",
    "OperationalApiArtifactKind",
    "OperationalApiInventoryToken",
    "OperationalEvidenceReadError",
]
