"""Ingestion orchestration for snapshot sources.

The runner is the only place where acquisition, enveloping, persistence,
extraction, quarantine, run reporting, and health derivation meet. Failures
are isolated per source and per record; raw payloads are always persisted
before extraction is attempted.
"""

from collections.abc import Callable
from datetime import UTC, datetime

from backend.data_sources.catalog import InMemorySourceCatalog
from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import (
    AcquisitionError,
    DataSourceError,
    ExtractedTable,
    ExtractionError,
    IngestionRun,
    QuarantineRecord,
    RawRecord,
    SourceDefinition,
    SourceHealth,
)
from backend.data_sources.extractors import CsvExtractionConfig, extract_csv
from backend.data_sources.provenance import (
    derive_record_id,
    payload_checksum,
    redact_text,
)
from backend.data_sources.raw_store import FilesystemRawStore

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


class IngestionRunner:
    def __init__(
        self,
        catalog: InMemorySourceCatalog,
        store: FilesystemRawStore,
        connectors: dict[str, LocalFileConnector],
        clock: Clock = _utc_now,
    ) -> None:
        self.catalog = catalog
        self.store = store
        self.connectors = connectors
        self.clock = clock

    # -- public API -------------------------------------------------------

    def run(self, source_id: str) -> IngestionRun:
        source = self.catalog.get(source_id)  # unknown source raises here
        run_id = self._next_run_id(source_id)
        started_at = self.clock()

        seen = accepted = duplicate = quarantined = 0
        errors: list[str] = []

        try:
            connector = self._connector_for(source)
            if not source.enabled:
                raise AcquisitionError(
                    "ACQUIRE_SOURCE_DISABLED",
                    f"source {source_id!r} is disabled in the catalog",
                )
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
                    self.store.put_extracted(self._extract(envelope, acquisition.payload))
                except ExtractionError as error:
                    quarantined = 1
                    errors.append(f"{error.error_code}: 1 record")
                    self.store.put_quarantine(
                        QuarantineRecord(
                            record_id=record_id,
                            stage="extraction",
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
            error_summary="; ".join(errors) or None,
        )
        self.store.put_run(run)
        return run

    def replay(self, source_id: str) -> list[ExtractedTable]:
        """Re-extract accepted raw records from the store, without touching
        the external source."""
        tables: list[ExtractedTable] = []
        for envelope in self.store.iter_accepted_envelopes(source_id):
            payload = self.store.get_payload(envelope.immutable_payload_reference)
            tables.append(self._extract(envelope, payload))
        return tables

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

    # -- internals --------------------------------------------------------

    def _connector_for(self, source: SourceDefinition) -> LocalFileConnector:
        try:
            return self.connectors[source.connector_type]
        except KeyError:
            raise AcquisitionError(
                "ACQUIRE_CONNECTOR_UNAVAILABLE",
                f"no active connector of type {source.connector_type!r}; the "
                "catalog declares it but this runtime does not provide it",
            ) from None

    def _extract(self, envelope: RawRecord, payload: bytes) -> ExtractedTable:
        if envelope.content_type != "text/csv":
            raise ExtractionError(
                "EXTRACT_UNSUPPORTED_FORMAT",
                f"no extractor available for content type {envelope.content_type!r}",
            )
        return extract_csv(payload, envelope.record_id, CsvExtractionConfig())

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
