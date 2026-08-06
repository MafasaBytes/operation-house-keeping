"""Ingestion orchestration for snapshot sources.

The runner is the only place where acquisition, enveloping, persistence,
format detection, extraction, staged publication, quarantine, run
reporting, and health derivation meet. Failures are isolated per source and
per record; raw payloads are always persisted before extraction is
attempted; derivatives are published before the extraction envelope, which
is written last as the commit record.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from backend.data_sources.catalog import InMemorySourceCatalog
from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import (
    AcquisitionError,
    CsvTableResult,
    DataSourceError,
    ExtractionError,
    ExtractionResult,
    IngestionRun,
    QuarantineRecord,
    RawRecord,
    SourceDefinition,
    SourceHealth,
    SourceProfile,
)
from backend.data_sources.extractors import (
    CsvExtractionConfig,
    csv_extractor_identity,
    detect_format,
    extract_csv,
)
from backend.data_sources.extractors.step import (
    StepExtractionConfig,
    extract_step,
)
from backend.data_sources.extractors.worker_harness import WorkerLimits
from backend.data_sources.provenance import (
    derive_record_id,
    payload_checksum,
    redact_text,
)
from backend.data_sources.raw_store import FilesystemRawStore

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass
class ExtractionProduct:
    result: ExtractionResult
    derivative_payloads: dict[str, bytes] = field(default_factory=dict)


Extractor = Callable[[bytes, RawRecord], ExtractionProduct]

# Which application-profile source family a declared content type belongs to.
FAMILY_BY_CONTENT_TYPE = {
    "text/csv": "csv_bom",
    "model/step": "step_assembly",
}

_FORMAT_DETECTION_CODES = frozenset(
    {"EXTRACT_UNSUPPORTED_NATIVE_CAD_FORMAT", "EXTRACT_UNSUPPORTED_OR_UNKNOWN_FORMAT"}
)


class IngestionRunner:
    def __init__(
        self,
        catalog: InMemorySourceCatalog,
        store: FilesystemRawStore,
        connectors: dict[str, LocalFileConnector],
        clock: Clock = _utc_now,
        extractors: dict[str, Extractor] | None = None,
        profile: SourceProfile | None = None,
        step_config: StepExtractionConfig | None = None,
        worker_limits: WorkerLimits | None = None,
        scratch_root: Path | None = None,
    ) -> None:
        self.catalog = catalog
        self.store = store
        self.connectors = connectors
        self.clock = clock
        self.profile = profile
        self.step_config = step_config or StepExtractionConfig()
        self.worker_limits = worker_limits or WorkerLimits()
        self.scratch_root = scratch_root
        self.extractors: dict[str, Extractor] = (
            extractors if extractors is not None else self._default_extractors()
        )

    def _default_extractors(self) -> dict[str, Extractor]:
        return {"text/csv": self._extract_csv, "model/step": self._extract_step}

    # -- public API -------------------------------------------------------

    def run(self, source_id: str) -> IngestionRun:
        source = self.catalog.get(source_id)  # unknown source raises here
        run_id = self._next_run_id(source_id)
        started_at = self.clock()

        seen = accepted = duplicate = quarantined = partial = 0
        errors: list[str] = []

        try:
            connector = self._connector_for(source)
            if not source.enabled:
                raise AcquisitionError(
                    "ACQUIRE_SOURCE_DISABLED",
                    f"source {source_id!r} is disabled in the catalog",
                )
            self._check_profile(source)
            acquisition = connector.acquire(source)
            seen = 1

            checksum = payload_checksum(acquisition.payload)
            record_id = derive_record_id(source_id, checksum, 0)

            if self.store.has_envelope(record_id):
                duplicate = 1
            else:
                reference = self.store.put_payload(acquisition.payload)
                envelope = RawRecord(
                    record_id=record_id,
                    source_id=source_id,
                    source_native_id=acquisition.source_native_id,
                    ingestion_run_id=run_id,
                    captured_at=self.clock(),
                    source_observed_at=acquisition.source_observed_at,
                    content_type=self._content_type(source),
                    payload_checksum=checksum,
                    immutable_payload_reference=reference,
                    provenance=acquisition.provenance,
                    quality_flags=[],
                )
                self.store.put_envelope(envelope)
                accepted = 1
                try:
                    product = self._extract_product(envelope, acquisition.payload)
                    # Staged publication: derivatives first, envelope last as
                    # the commit record.
                    for data in product.derivative_payloads.values():
                        self.store.put_derivative_payload(data)
                    self.store.put_extraction(product.result)
                    if product.result.outcome == "partial":
                        partial = 1
                except DataSourceError as error:
                    quarantined = 1
                    errors.append(f"{error.error_code}: 1 record")
                    self.store.put_quarantine(
                        QuarantineRecord(
                            record_id=record_id,
                            stage=(
                                "format_detection"
                                if error.error_code in _FORMAT_DETECTION_CODES
                                else "extraction"
                            ),
                            error_code=error.error_code,
                            redacted_message=self._redact(error.message),
                            quarantined_at=self.clock(),
                        )
                    )
        except DataSourceError as error:
            errors.append(f"{error.error_code}: {self._redact(error.message)}")
            run = IngestionRun(
                run_id=run_id,
                source_id=source_id,
                started_at=started_at,
                finished_at=self.clock(),
                status="failed",
                records_seen=seen,
                records_accepted=accepted,
                records_duplicate=duplicate,
                records_quarantined=quarantined,
                records_partial=partial,
                error_summary="; ".join(errors),
            )
            self.store.put_run(run)
            return run

        run = IngestionRun(
            run_id=run_id,
            source_id=source_id,
            started_at=started_at,
            finished_at=self.clock(),
            status="completed_with_quarantine" if quarantined else "succeeded",
            records_seen=seen,
            records_accepted=accepted,
            records_duplicate=duplicate,
            records_quarantined=quarantined,
            records_partial=partial,
            error_summary="; ".join(errors) or None,
        )
        self.store.put_run(run)
        return run

    def replay(self, source_id: str) -> list[ExtractionProduct]:
        """Re-extract accepted raw records from the store, without touching
        the external source."""
        products: list[ExtractionProduct] = []
        for envelope in self.store.iter_accepted_envelopes(source_id):
            payload = self.store.get_payload(envelope.immutable_payload_reference)
            products.append(self._extract_product(envelope, payload))
        return products

    def health(self, source_id: str) -> SourceHealth:
        runs = sorted(self.store.iter_runs(source_id), key=lambda r: r.finished_at)
        checked_at = self.clock()
        if not runs:
            return SourceHealth(
                source_id=source_id,
                status="unknown",
                checked_at=checked_at,
                last_success_at=None,
                last_record_at=None,
                diagnostic_code=None,
            )
        latest = runs[-1]
        status = {
            "succeeded": "ok",
            "completed_with_quarantine": "degraded",
            "failed": "failed",
        }[latest.status]
        successes = [r for r in runs if r.status == "succeeded"]
        accepting = [r for r in runs if r.records_accepted > 0]
        diagnostic = None
        if latest.error_summary:
            diagnostic = latest.error_summary.split(":", 1)[0]
        return SourceHealth(
            source_id=source_id,
            status=status,
            checked_at=checked_at,
            last_success_at=successes[-1].finished_at if successes else None,
            last_record_at=accepting[-1].finished_at if accepting else None,
            diagnostic_code=diagnostic,
        )

    # -- extraction dispatch ---------------------------------------------

    def _extract_product(self, envelope: RawRecord, payload: bytes) -> ExtractionProduct:
        extractor = self.extractors.get(envelope.content_type)
        if extractor is None:
            raise ExtractionError(
                "EXTRACT_UNSUPPORTED_FORMAT",
                f"no extractor available for content type {envelope.content_type!r}",
            )
        return extractor(payload, envelope)

    def _extract_csv(self, payload: bytes, envelope: RawRecord) -> ExtractionProduct:
        config = CsvExtractionConfig()
        table = extract_csv(payload, envelope.record_id, config)
        result = ExtractionResult(
            schema_version=1,
            raw_record_id=envelope.record_id,
            extractor=csv_extractor_identity(config),
            outcome="succeeded",
            warnings=[],
            result=CsvTableResult(table=table),
        )
        return ExtractionProduct(result=result)

    def _extract_step(self, payload: bytes, envelope: RawRecord) -> ExtractionProduct:
        detection = detect_format(payload, declared_content_type=envelope.content_type)
        if detection.status == "unsupported_native_cad":
            raise ExtractionError(
                "EXTRACT_UNSUPPORTED_NATIVE_CAD_FORMAT",
                f"payload is an {detection.detected_container}, not STEP; "
                "native CAD formats require a vendor extraction pipeline",
            )
        if detection.status != "confirmed_step":
            raise ExtractionError(
                "EXTRACT_UNSUPPORTED_OR_UNKNOWN_FORMAT", detection.evidence
            )
        product = extract_step(
            payload=payload,
            raw_record_id=envelope.record_id,
            config=self.step_config,
            limits=self.worker_limits,
            scratch_root=self.scratch_root,
        )
        return ExtractionProduct(
            result=product.result, derivative_payloads=product.derivative_payloads
        )

    # -- internals --------------------------------------------------------

    def _check_profile(self, source: SourceDefinition) -> None:
        if self.profile is None:
            return
        content_type = self._content_type(source)
        family = FAMILY_BY_CONTENT_TYPE.get(content_type)
        entry = next(
            (e for e in self.profile.entries if e.source_family == family), None
        )
        if entry is None or not entry.enabled_for_profile:
            raise AcquisitionError(
                "ACQUIRE_NOT_IN_PROFILE",
                f"content type {content_type!r} (family {family!r}) is not "
                f"enabled in profile {self.profile.profile_id!r}",
            )

    def _connector_for(self, source: SourceDefinition) -> LocalFileConnector:
        try:
            return self.connectors[source.connector_type]
        except KeyError:
            raise AcquisitionError(
                "ACQUIRE_CONNECTOR_UNAVAILABLE",
                f"no active connector of type {source.connector_type!r}; the "
                "catalog declares it but this runtime does not provide it",
            ) from None

    @staticmethod
    def _content_type(source: SourceDefinition) -> str:
        if source.declared_content_types:
            return source.declared_content_types[0]
        return "application/octet-stream"

    def _next_run_id(self, source_id: str) -> str:
        count = sum(1 for _ in self.store.iter_runs(source_id))
        return f"run-{source_id}-{count + 1:04d}"

    def _redact(self, text: str) -> str:
        return redact_text(text, base_dir=str(self.store.base_dir))
