"""Bounded, read-only filesystem reader for DS-004 operational API evidence."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ValidationError

from backend.data_sources.contracts import (
    AcquisitionAttempt,
    ApiObservationsResult,
    Ds004OperationalEvidenceMaterial,
    Ds004OperationalEvidenceScope,
    ExtractionResult,
    IngestionRun,
    OperationalApiArtifactDescriptor,
    OperationalApiInventoryToken,
    OperationalEvidenceReadError,
    OperationalObservation,
    QuarantineRecord,
    RawRecord,
)
from backend.data_sources.extractors.operational import (
    JsonLimits,
    canonical_json,
    json_type_of,
    parse_bounded_json,
)
from backend.data_sources.provenance import derive_keyed_record_id, payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore


MAX_IN_HORIZON_ATTEMPTS = 4_096
MAX_RETAINED_OBSERVATIONS = 16_384
MAX_RETAINED_ARTIFACTS = 16_384
MAX_RETAINED_METADATA_BYTES = 64 * 1024 * 1024
SUPPORTED_EXTRACTION_ROUTES = ("api:moonraker:v1",)

_HEX_ID = re.compile(r"^[0-9a-f]{32}$")
_SAFE_LOGICAL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,511}$")
_METADATA_SUFFIX = ".json"


class Ds004OperationalEvidenceReader(Protocol):
    def inventory_token(
        self,
        scope: Ds004OperationalEvidenceScope,
        *,
        horizon_started_at: datetime,
        as_of: datetime,
    ) -> OperationalApiInventoryToken: ...

    def read_material(
        self,
        scope: Ds004OperationalEvidenceScope,
        *,
        horizon_started_at: datetime,
        as_of: datetime,
        selected_seed_attempt_id: str | None,
    ) -> Ds004OperationalEvidenceMaterial: ...


def _fail(code: str, detail: str) -> OperationalEvidenceReadError:
    return OperationalEvidenceReadError(code, detail[:300])


def _aware_interval(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    for value, name in ((start, "horizon_started_at"), (end, "as_of")):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise _fail("OPERATIONAL_EVIDENCE_INVALID_HORIZON",
                        f"{name} must be timezone-aware")
    start, end = start.astimezone(UTC), end.astimezone(UTC)
    if start > end:
        raise _fail("OPERATIONAL_EVIDENCE_INVALID_HORIZON",
                    "horizon_started_at must be at or before as_of")
    return start, end


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _canonical_membership(keys: tuple[str, ...]) -> str:
    encoded = ("[" + ",".join(
        __import__("json").dumps(k, ensure_ascii=False) for k in keys) + "]").encode()
    return _sha(encoded)


def _safe_component(value: str, description: str, *, hex_only: bool = False) -> str:
    pattern = _HEX_ID if hex_only else _SAFE_LOGICAL_ID
    if not pattern.fullmatch(value) or value in {".", ".."}:
        raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_REFERENCE",
                    f"{description} is not a safe logical identifier")
    return value


def _decode_pointer(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                    "JSON pointer is not an RFC 6901 absolute pointer")
    decoded: list[str] = []
    for raw in pointer[1:].split("/"):
        token = ""
        index = 0
        while index < len(raw):
            if raw[index] != "~":
                token += raw[index]
                index += 1
                continue
            if index + 1 >= len(raw) or raw[index + 1] not in "01":
                raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                            "JSON pointer contains an invalid escape")
            token += "~" if raw[index + 1] == "0" else "/"
            index += 2
        decoded.append(token)
    return decoded


def _resolve_pointer(document, pointer: str):
    value = document
    for token in _decode_pointer(pointer):
        if isinstance(value, dict):
            if token not in value:
                raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                            "JSON pointer does not resolve")
            value = value[token]
        elif isinstance(value, list):
            if token == "-" or not token.isdigit() or (
                    len(token) > 1 and token.startswith("0")):
                raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                            "JSON pointer contains an invalid array index")
            position = int(token)
            if position >= len(value):
                raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                            "JSON pointer array index is out of range")
            value = value[position]
        else:
            raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                        "JSON pointer traverses a scalar")
    return value


class FilesystemDs004OperationalEvidenceReader:
    """Read a bounded DS-004 view without invoking acquisition or extraction."""

    def __init__(self, store: FilesystemRawStore) -> None:
        if type(store) is not FilesystemRawStore:
            raise TypeError("store must be exactly FilesystemRawStore")
        self._store = store
        self._root = store.base_dir

    def inventory_token(self, scope, *, horizon_started_at, as_of):
        start, end = _aware_interval(horizon_started_at, as_of)
        scope = self._scope(scope)
        material = self.read_material(
            scope, horizon_started_at=start, as_of=end,
            selected_seed_attempt_id=None)
        keys = tuple(sorted(
            f"{item.kind}:{item.logical_id}:{item.byte_count}"
            for item in material.artifacts))
        return OperationalApiInventoryToken(
            schema_version="1", scope=scope, horizon_started_at=start, as_of=end,
            ordered_member_keys=keys,
            canonical_membership_sha256=_canonical_membership(keys),
        )

    def read_material(
        self, scope, *, horizon_started_at, as_of, selected_seed_attempt_id
    ):
        start, end = _aware_interval(horizon_started_at, as_of)
        scope = self._scope(scope)
        if selected_seed_attempt_id is not None:
            _safe_component(selected_seed_attempt_id, "seed attempt", hex_only=True)

        descriptors: dict[tuple[str, str], OperationalApiArtifactDescriptor] = {}
        selected_attempts: list[AcquisitionAttempt] = []
        selected_attempt_bytes: dict[str, bytes] = {}
        for path in self._ordered_entries("attempts", hex_names=True):
            attempt, data = self._read_model(
                path, AcquisitionAttempt, "acquisition attempt")
            if path.stem != attempt.attempt_id:
                raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                            "attempt filename and logical identifier differ")
            if not self._attempt_scope_matches(attempt, scope):
                continue
            effective = (attempt.received_at or attempt.finished_at).astimezone(UTC)
            in_horizon = start <= effective <= end
            is_seed = attempt.attempt_id == selected_seed_attempt_id
            if is_seed and effective >= start:
                raise _fail("OPERATIONAL_EVIDENCE_SEED_INVALID",
                            "selected seed must predate the declared horizon")
            if not in_horizon and not is_seed:
                continue
            selected_attempts.append(attempt)
            selected_attempt_bytes[attempt.attempt_id] = data
            if len([a for a in selected_attempts
                    if (a.received_at or a.finished_at).astimezone(UTC) >= start]
                   ) > MAX_IN_HORIZON_ATTEMPTS:
                raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                            "in-horizon attempt count exceeds 4096")

        if selected_seed_attempt_id is not None and not any(
                a.attempt_id == selected_seed_attempt_id for a in selected_attempts):
            raise _fail("OPERATIONAL_EVIDENCE_SEED_INVALID",
                        "selected seed attempt is absent from the exact source scope")

        selected_attempts.sort(key=self._attempt_order)
        runs: dict[str, IngestionRun] = {}
        envelopes: dict[str, RawRecord] = {}
        extractions: dict[str, ExtractionResult] = {}
        quarantines: dict[str, QuarantineRecord] = {}
        observations: dict[str, OperationalObservation] = {}
        payload_documents: dict[str, object] = {}
        metadata_total = 0

        for attempt in selected_attempts:
            metadata_total += self._descriptor(
                descriptors, "acquisition_attempt", attempt.attempt_id,
                selected_attempt_bytes[attempt.attempt_id]).byte_count
            if attempt.ingestion_run_id not in runs:
                run, data = self._read_named_model(
                    "runs", attempt.ingestion_run_id, IngestionRun, "ingestion run")
                if run.run_id != attempt.ingestion_run_id or run.source_id != scope.source_id:
                    raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                                "attempt and ingestion run do not close")
                runs[run.run_id] = run
                metadata_total += self._descriptor(
                    descriptors, "ingestion_run", run.run_id, data).byte_count

            if attempt.outcome == "failed":
                continue
            record_id = attempt.raw_record_id
            if record_id not in envelopes:
                envelope, data = self._read_named_model(
                    "envelopes", record_id, RawRecord, "raw envelope", hex_only=True)
                self._validate_envelope(attempt, envelope, scope)
                envelopes[record_id] = envelope
                metadata_total += self._descriptor(
                    descriptors, "raw_envelope", record_id, data).byte_count

                payload_data = self._read_payload(envelope.immutable_payload_reference)
                observed_checksum = payload_checksum(payload_data)
                if observed_checksum != envelope.payload_checksum:
                    raise _fail("OPERATIONAL_EVIDENCE_CHECKSUM_MISMATCH",
                                "raw payload bytes do not match stored checksum")
                self._descriptor(
                    descriptors, "raw_payload", envelope.payload_checksum,
                    payload_data, payload_checksum_value=envelope.payload_checksum)
                try:
                    payload_documents[record_id] = parse_bounded_json(
                        payload_data, JsonLimits())
                except Exception as error:
                    raise _fail("OPERATIONAL_EVIDENCE_PAYLOAD_INVALID",
                                "raw operational payload is not acceptable JSON") from error

                extraction_path = self._named_path("extracted", record_id, hex_only=True)
                quarantine_path = self._named_path("quarantine", record_id, hex_only=True)
                extraction_exists = self._safe_is_file(extraction_path)
                quarantine_exists = self._safe_is_file(quarantine_path)
                if extraction_exists == quarantine_exists:
                    code = ("OPERATIONAL_EVIDENCE_EXTRACTION_INCOMPLETE"
                            if not extraction_exists else
                            "OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH")
                    raise _fail(code,
                                "successful attempt requires exactly one extraction or quarantine")
                if quarantine_exists:
                    quarantine, q_data = self._read_model(
                        quarantine_path, QuarantineRecord, "quarantine record")
                    if quarantine.record_id != record_id:
                        raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                                    "quarantine record does not match raw record")
                    quarantines[record_id] = quarantine
                    metadata_total += self._descriptor(
                        descriptors, "quarantine_record", record_id, q_data).byte_count
                else:
                    extraction, e_data = self._read_model(
                        extraction_path, ExtractionResult, "extraction result")
                    self._validate_extraction(
                        extraction, envelope, scope, payload_documents[record_id],
                        observations)
                    extractions[record_id] = extraction
                    metadata_total += self._descriptor(
                        descriptors, "extraction_result", record_id, e_data).byte_count

        if metadata_total > MAX_RETAINED_METADATA_BYTES:
            raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                        "retained metadata exceeds 64 MiB")
        if len(descriptors) > MAX_RETAINED_ARTIFACTS:
            raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                        "retained artifact count exceeds 16384")
        if len(observations) > MAX_RETAINED_OBSERVATIONS:
            raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                        "retained observation count exceeds 16384")

        return Ds004OperationalEvidenceMaterial(
            schema_version="1", scope=scope,
            artifacts=tuple(sorted(
                descriptors.values(), key=lambda d: (
                    ("ingestion_run", "acquisition_attempt", "raw_envelope",
                     "raw_payload", "extraction_result", "quarantine_record").index(
                         d.kind), d.logical_id))),
            runs=tuple(sorted(runs.values(), key=lambda r: r.run_id)),
            attempts=tuple(selected_attempts),
            envelopes=tuple(sorted(envelopes.values(), key=lambda r: r.record_id)),
            extractions=tuple(sorted(extractions.values(), key=lambda r: r.raw_record_id)),
            quarantines=tuple(sorted(quarantines.values(), key=lambda r: r.record_id)),
            observations=tuple(sorted(
                observations.values(), key=lambda o: (
                    o.raw_record_id, o.json_pointer, o.subject_identifier,
                    o.observation_id))),
        )

    @staticmethod
    def _scope(value) -> Ds004OperationalEvidenceScope:
        try:
            payload = value.model_dump(mode="python") if isinstance(
                value, BaseModel) else value
            scope = Ds004OperationalEvidenceScope.model_validate(payload)
        except ValidationError as error:
            raise _fail("OPERATIONAL_EVIDENCE_SCOPE_INVALID",
                        "operational evidence scope is invalid") from error
        if scope.extraction_route not in SUPPORTED_EXTRACTION_ROUTES:
            raise _fail("OPERATIONAL_EVIDENCE_UNSUPPORTED_ROUTE",
                        "extraction route is not supported by the DS-004 reader")
        return scope

    def _ordered_entries(self, directory: str, *, hex_names: bool) -> list[Path]:
        root = self._root / directory
        try:
            entries = list(root.iterdir())
        except OSError as error:
            raise _fail("OPERATIONAL_EVIDENCE_UNAVAILABLE",
                        "required evidence namespace is unavailable") from error
        accepted = []
        for path in entries:
            if not path.name.endswith(_METADATA_SUFFIX):
                raise _fail("OPERATIONAL_EVIDENCE_UNEXPECTED_ENTRY",
                            "evidence namespace contains an unexpected entry")
            stem = path.name.removesuffix(_METADATA_SUFFIX)
            _safe_component(stem, "stored logical identifier", hex_only=hex_names)
            if path.is_symlink():
                raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_ENTRY",
                            "evidence namespace contains an unsafe entry")
            try:
                mode = path.stat(follow_symlinks=False).st_mode
            except OSError as error:
                raise _fail("OPERATIONAL_EVIDENCE_UNAVAILABLE",
                            "required evidence entry is unavailable") from error
            if not stat.S_ISREG(mode):
                raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_ENTRY",
                            "evidence namespace contains a non-regular entry")
            accepted.append(path)
        return sorted(accepted, key=lambda p: p.name)

    def _named_path(self, directory: str, logical_id: str, *, hex_only=False) -> Path:
        _safe_component(logical_id, "stored logical identifier", hex_only=hex_only)
        return self._root / directory / f"{logical_id}.json"

    @staticmethod
    def _safe_is_file(path: Path) -> bool:
        try:
            mode = path.stat(follow_symlinks=False).st_mode
        except FileNotFoundError:
            return False
        except OSError as error:
            raise _fail("OPERATIONAL_EVIDENCE_UNAVAILABLE",
                        "required evidence entry is unavailable") from error
        if path.is_symlink() or not stat.S_ISREG(mode):
            raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_ENTRY",
                        "evidence entry is not a regular file")
        return True

    def _read_named_model(self, directory, logical_id, model, description,
                          *, hex_only=False):
        path = self._named_path(directory, logical_id, hex_only=hex_only)
        return self._read_model(path, model, description)

    @staticmethod
    def _read_bytes_once(path: Path, *, max_bytes: int | None = None) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path, flags)
        except OSError as error:
            raise _fail("OPERATIONAL_EVIDENCE_UNAVAILABLE",
                        "required evidence artifact is unavailable") from error
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode):
                raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_ENTRY",
                            "evidence artifact is not a regular file")
            if max_bytes is not None and info.st_size > max_bytes:
                raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                            "evidence artifact exceeds the byte limit")
            chunks = []
            observed = 0
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                observed += len(chunk)
                if max_bytes is not None and observed > max_bytes:
                    raise _fail("OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                                "evidence artifact exceeds the byte limit")
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)

    def _read_model(self, path: Path, model, description):
        data = self._read_bytes_once(path, max_bytes=MAX_RETAINED_METADATA_BYTES)
        try:
            parsed = parse_bounded_json(data, JsonLimits())
            rebuilt = model.model_validate(parsed)
        except Exception as error:
            raise _fail("OPERATIONAL_EVIDENCE_METADATA_INVALID",
                        f"stored {description} is malformed") from error
        return rebuilt, data

    def _read_payload(self, reference: str) -> bytes:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", reference):
            raise _fail("OPERATIONAL_EVIDENCE_UNSAFE_REFERENCE",
                        "payload reference is malformed")
        path = self._root / "payloads" / reference.removeprefix("sha256:")
        return self._read_bytes_once(path, max_bytes=MAX_RETAINED_METADATA_BYTES)

    @staticmethod
    def _attempt_scope_matches(attempt, scope) -> bool:
        return (
            attempt.source_id == scope.source_id
            and attempt.adapter_id == scope.adapter_id
            and attempt.endpoint_id == scope.endpoint_id
            and attempt.item_key == scope.item_key
        )

    @staticmethod
    def _attempt_order(attempt):
        return (
            attempt.started_at.astimezone(UTC).isoformat(),
            attempt.ingestion_run_id, attempt.sweep_position, attempt.attempt_id)

    @staticmethod
    def _descriptor(target, kind, logical_id, data, *, payload_checksum_value=None):
        key = (kind, logical_id)
        descriptor = OperationalApiArtifactDescriptor(
            kind=kind, logical_id=logical_id, byte_count=len(data),
            captured_file_sha256=_sha(data),
            payload_checksum=payload_checksum_value)
        existing = target.get(key)
        if existing is not None and existing != descriptor:
            raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                        "one logical artifact has contradictory captured bytes")
        target[key] = descriptor
        return descriptor

    @staticmethod
    def _validate_envelope(attempt, envelope, scope):
        locator = envelope.api_locator
        if locator is None or locator.extraction_route not in SUPPORTED_EXTRACTION_ROUTES:
            raise _fail("OPERATIONAL_EVIDENCE_UNSUPPORTED_ROUTE",
                        "raw record is not supported DS-004 API evidence")
        if (
            envelope.record_id != attempt.raw_record_id
            or envelope.source_id != attempt.source_id
            or envelope.ingestion_run_id != attempt.ingestion_run_id
            or envelope.payload_checksum != attempt.payload_checksum
            or envelope.immutable_payload_reference != attempt.payload_checksum
            or envelope.record_id != derive_keyed_record_id(
                attempt.source_id, attempt.item_key, attempt.payload_checksum)
            or locator.adapter_id != scope.adapter_id
            or locator.endpoint_id != scope.endpoint_id
            or locator.item_key != scope.item_key
            or locator.extraction_route != scope.extraction_route
            or locator.request_fingerprint != attempt.request_fingerprint
            or locator.request_canonical != attempt.request_canonical
        ):
            raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                        "attempt, raw record, and API locator do not close")

    @staticmethod
    def _validate_extraction(extraction, envelope, scope, document,
                             observations):
        if extraction.raw_record_id != envelope.record_id:
            raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                        "extraction and raw record do not close")
        if not isinstance(extraction.result, ApiObservationsResult):
            raise _fail("OPERATIONAL_EVIDENCE_UNSUPPORTED_ROUTE",
                        "extraction is not a DS-004 API observations result")
        manifest = extraction.result.manifest
        if (
            manifest.raw_record_id != extraction.raw_record_id
            or manifest.extractor != extraction.extractor
            or manifest.adapter_id != scope.adapter_id
            or manifest.item_key != scope.item_key
        ):
            raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                        "extraction wrapper and API manifest do not close")
        seen_pointer_subject = set()
        for observation in manifest.observations:
            if observation.raw_record_id != envelope.record_id:
                raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                            "observation and raw record do not close")
            key = (observation.subject_identifier, observation.json_pointer)
            if key in seen_pointer_subject or observation.observation_id in observations:
                raise _fail("OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH",
                            "operational observations are duplicated")
            seen_pointer_subject.add(key)
            value = _resolve_pointer(document, observation.json_pointer)
            if (canonical_json(value) != observation.value_json
                    or json_type_of(value) != observation.json_type):
                raise _fail("OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
                            "operational observation differs from raw JSON")
            if (observation.subject_identifier == scope.subject_identifier
                    and observation.json_pointer == scope.json_pointer):
                observations[observation.observation_id] = observation


__all__ = [
    "Ds004OperationalEvidenceReader",
    "FilesystemDs004OperationalEvidenceReader",
    "MAX_IN_HORIZON_ATTEMPTS",
    "MAX_RETAINED_ARTIFACTS",
    "MAX_RETAINED_METADATA_BYTES",
    "MAX_RETAINED_OBSERVATIONS",
    "SUPPORTED_EXTRACTION_ROUTES",
]
