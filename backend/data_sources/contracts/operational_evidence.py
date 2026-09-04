"""Read-only DS-004 operational evidence material contracts for EA-001."""

from __future__ import annotations

import hashlib
import json
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
from backend.data_sources.contracts.extraction import (
    ApiObservationsResult,
    ExtractionResult,
)
from backend.data_sources.contracts.models import IngestionRun, QuarantineRecord, RawRecord
from backend.data_sources.provenance.core import (
    derive_entity_id,
    derive_keyed_record_id,
)


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


def operational_inventory_digest(keys: tuple[str, ...]) -> str:
    payload = json.dumps(
        list(keys), ensure_ascii=False, separators=(",", ":"),
        allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


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
            if self.captured_file_sha256 != self.payload_checksum:
                raise ValueError(
                    "raw payload file digest must equal its stored checksum")
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
        if operational_inventory_digest(self.ordered_member_keys) != (
                self.canonical_membership_sha256):
            raise ValueError("inventory membership digest is stale")
        return self


def _attempt_order(attempt: AcquisitionAttempt) -> tuple[str, str, int, str]:
    return (
        attempt.started_at.astimezone(UTC).isoformat(),
        attempt.ingestion_run_id,
        attempt.sweep_position,
        attempt.attempt_id,
    )


def _attempt_disclosure_is_sanitized(attempt: AcquisitionAttempt) -> bool:
    origin = attempt.target_origin
    if not origin.startswith(("http://", "https://")):
        return False
    authority = origin.split("://", 1)[1]
    if (not authority or any(character.isspace() for character in authority)
            or any(token in authority for token in ("@", "/", "?", "#", "\\"))):
        return False
    if (not attempt.request_canonical.startswith("GET /")
            or len(attempt.request_canonical) > 4_096
            or any(token in attempt.request_canonical for token in ("\r", "\n"))):
        return False
    allowed_headers = {"Content-Type", "Date", "Retry-After", "X-Request-Id"}
    return set(attempt.allowlisted_headers) <= allowed_headers and all(
        isinstance(value, str) and len(value) <= 1_024
        and "\r" not in value and "\n" not in value
        for value in attempt.allowlisted_headers.values())


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

        runs = {row.run_id: row for row in self.runs}
        envelopes = {row.record_id: row for row in self.envelopes}
        extractions = {row.raw_record_id: row for row in self.extractions}
        quarantines = {row.record_id: row for row in self.quarantines}
        descriptors = {(row.kind, row.logical_id): row for row in self.artifacts}
        referenced_runs: set[str] = set()
        referenced_records: set[str] = set()

        for attempt in self.attempts:
            if (
                attempt.source_id != self.scope.source_id
                or attempt.adapter_id != self.scope.adapter_id
                or attempt.endpoint_id != self.scope.endpoint_id
                or attempt.item_key != self.scope.item_key
            ):
                raise ValueError("attempt lies outside exact source scope")
            if not _attempt_disclosure_is_sanitized(attempt):
                raise ValueError("attempt disclosure is not sanitized")
            run = runs.get(attempt.ingestion_run_id)
            if run is None or run.source_id != self.scope.source_id:
                raise ValueError("attempt and ingestion run do not close")
            referenced_runs.add(attempt.ingestion_run_id)
            if ("acquisition_attempt", attempt.attempt_id) not in descriptors:
                raise ValueError("attempt artifact descriptor is absent")
            if attempt.outcome == "failed":
                continue
            record_id = attempt.raw_record_id
            envelope = envelopes.get(record_id)
            if envelope is None:
                raise ValueError("successful attempt envelope is absent")
            if (
                envelope.source_id != self.scope.source_id
                or envelope.ingestion_run_id not in runs
                or envelope.payload_checksum != attempt.payload_checksum
                or envelope.immutable_payload_reference != attempt.payload_checksum
                or envelope.record_id != derive_keyed_record_id(
                    attempt.source_id, attempt.item_key, attempt.payload_checksum)
            ):
                raise ValueError("attempt and raw envelope do not close")
            referenced_runs.add(envelope.ingestion_run_id)
            locator = envelope.api_locator
            if locator is None or (
                locator.adapter_id != self.scope.adapter_id
                or locator.endpoint_id != self.scope.endpoint_id
                or locator.item_key != self.scope.item_key
                or locator.extraction_route != self.scope.extraction_route
                or locator.request_fingerprint != attempt.request_fingerprint
                or locator.request_canonical != attempt.request_canonical
                or attempt.request_fingerprint != "sha256:" + hashlib.sha256(
                    f"{attempt.target_origin} {attempt.request_canonical}".encode(
                        "utf-8")).hexdigest()
            ):
                raise ValueError("API locator does not close the exact scope")
            referenced_records.add(record_id)

        if set(runs) != referenced_runs or set(envelopes) != referenced_records:
            raise ValueError("source material contains unreferenced closure rows")
        expected_descriptors = {
            *(('ingestion_run', key) for key in runs),
            *(('acquisition_attempt', row.attempt_id) for row in self.attempts),
            *(('raw_envelope', key) for key in envelopes),
            *(('raw_payload', row.payload_checksum) for row in envelopes.values()),
            *(('extraction_result', key) for key in extractions),
            *(('quarantine_record', key) for key in quarantines),
        }
        if set(descriptors) != expected_descriptors:
            raise ValueError("artifact descriptors do not match carried source rows")

        expected_observations = {}
        for record_id in referenced_records:
            extraction = extractions.get(record_id)
            quarantine = quarantines.get(record_id)
            if (extraction is None) == (quarantine is None):
                raise ValueError(
                    "raw envelope requires exactly one extraction or quarantine")
            if quarantine is not None:
                continue
            if not isinstance(extraction.result, ApiObservationsResult):
                raise ValueError("non-operational extraction is not supported")
            manifest = extraction.result.manifest
            if (
                manifest.raw_record_id != record_id
                or manifest.extractor != extraction.extractor
                or manifest.adapter_id != self.scope.adapter_id
                or manifest.item_key != self.scope.item_key
            ):
                raise ValueError("extraction wrapper and manifest do not close")
            seen_claims = set()
            for observation in manifest.observations:
                claim = (observation.subject_identifier, observation.json_pointer)
                if claim in seen_claims or observation.raw_record_id != record_id:
                    raise ValueError("extraction observations do not close")
                seen_claims.add(claim)
                expected_id = derive_entity_id(
                    record_id, extraction.extractor.version,
                    f"obs:{observation.json_pointer}")
                if observation.observation_id != expected_id:
                    raise ValueError("observation identity is stale")
                if (
                    observation.subject_identifier
                    == self.scope.subject_identifier
                    and observation.json_pointer == self.scope.json_pointer
                ):
                    expected_observations[observation.observation_id] = observation
        if {row.observation_id: row for row in self.observations} != (
                expected_observations):
            raise ValueError("carried observations do not match exact-scope manifests")
        return self


__all__ = [
    "Ds004OperationalEvidenceMaterial",
    "Ds004OperationalEvidenceScope",
    "OperationalApiArtifactDescriptor",
    "OperationalApiArtifactKind",
    "OperationalApiInventoryToken",
    "OperationalEvidenceReadError",
]
