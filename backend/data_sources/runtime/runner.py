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
from backend.data_sources.adapters.moonraker import MoonrakerAdapter
from backend.data_sources.contracts import (
    AcquisitionAttempt,
    AcquisitionError,
    ApiHealthEvidence,
    ApiObservationsResult,
    ApiSourceLocator,
    AttemptFailure,
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
    resolve_completed_run_status,
)
from backend.data_sources.connectors.events import AcquisitionFailed
from backend.data_sources.extractors import (
    CsvExtractionConfig,
    csv_extractor_identity,
    detect_format,
    extract_csv,
)
from backend.data_sources.extractors.pdf import (
    PdfExtractionConfig,
    extract_pdf,
)
from backend.data_sources.extractors.step import (
    StepExtractionConfig,
    extract_step,
)
from backend.data_sources.extractors.worker_harness import WorkerLimits
from backend.data_sources.provenance import (
    derive_entity_id,
    derive_keyed_record_id,
    derive_record_id,
    payload_checksum,
    redact_text,
    scrub_secrets,
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
    "application/pdf": "pdf_drawing_manual",
    "application/json": "operational_api_or_telemetry",
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
        pdf_config: PdfExtractionConfig | None = None,
        worker_limits: WorkerLimits | None = None,
        scratch_root: Path | None = None,
    ) -> None:
        self.catalog = catalog
        self.store = store
        self.connectors = connectors
        self.clock = clock
        self.profile = profile
        self.step_config = step_config or StepExtractionConfig()
        self.pdf_config = pdf_config or PdfExtractionConfig()
        self.worker_limits = worker_limits or WorkerLimits()
        self.scratch_root = scratch_root
        self.extractors: dict[str, Extractor] = (
            extractors if extractors is not None else self._default_extractors()
        )

    def _default_extractors(self) -> dict[str, Extractor]:
        return {
            "text/csv": self._extract_csv,
            "model/step": self._extract_step,
            "application/pdf": self._extract_pdf,
            "api:moonraker:v1": self._extract_moonraker,
        }

    def _extract_moonraker(self, payload: bytes, envelope: RawRecord) -> ExtractionProduct:
        adapter = MoonrakerAdapter()
        manifest = adapter.extract(
            payload, envelope.record_id, envelope.api_locator.item_key
        )
        result = ExtractionResult(
            raw_record_id=envelope.record_id,
            extractor=manifest.extractor,
            outcome="succeeded",
            warnings=[],
            result=ApiObservationsResult(manifest=manifest),
        )
        return ExtractionProduct(result=result)

    # -- public API -------------------------------------------------------

    def run(self, source_id: str) -> IngestionRun:
        source = self.catalog.get(source_id)  # unknown source raises here
        run_id = self._next_run_id(source_id)
        started_at = self.clock()

        seen = accepted = duplicate = quarantined = partial = 0
        attempts_planned = attempts_succeeded = attempts_failed = 0
        item_ordinals: dict[str, int] = {}
        errors: list[str] = []

        def next_attempt_id(item_key: str) -> str:
            ordinal = item_ordinals.get(item_key, 0)
            item_ordinals[item_key] = ordinal + 1
            return derive_entity_id(run_id, "attempt", f"{item_key}:{ordinal}")

        try:
            connector = self._connector_for(source)
            if not source.enabled:
                raise AcquisitionError(
                    "ACQUIRE_SOURCE_DISABLED",
                    f"source {source_id!r} is disabled in the catalog",
                )
            self._check_profile(source)
            if source.connector_type == "http_api":
                attempts_planned = connector.planned_items(source)

            # Incremental pull loop: each successful payload plus its
            # acquisition attempt is persisted BEFORE the next event is
            # requested — a later failure never discards earlier evidence.
            for position, event in enumerate(connector.acquire_events(source)):
                if isinstance(event, AcquisitionFailed):
                    attempts_failed += 1
                    errors.append(f"{event.error_code}: item {event.item_key}")
                    if event.api is not None:
                        self.store.put_attempt(self._attempt_from_event(
                            event, next_attempt_id(event.item_key), run_id,
                            source_id, position, raw_record_id=None,
                            checksum=None, payload_reused=False,
                        ))
                    continue

                seen += 1
                checksum = payload_checksum(event.payload)
                if event.identity_mode == "keyed":
                    record_id = derive_keyed_record_id(
                        source_id, event.item_key, checksum
                    )
                else:
                    record_id = derive_record_id(source_id, checksum, 0)

                reused = self.store.has_envelope(record_id)
                envelope = None
                if reused:
                    duplicate += 1
                else:
                    # commit order: payload -> envelope -> attempt -> extraction
                    reference = self.store.put_payload(event.payload)
                    envelope = RawRecord(
                        record_id=record_id,
                        source_id=source_id,
                        source_native_id=event.source_native_id,
                        ingestion_run_id=run_id,
                        captured_at=self.clock(),
                        source_observed_at=event.source_observed_at,
                        content_type=event.content_type
                        or self._content_type(source),
                        payload_checksum=checksum,
                        immutable_payload_reference=reference,
                        provenance=event.provenance,
                        quality_flags=[],
                        api_locator=self._locator_from_event(event),
                    )
                    self.store.put_envelope(envelope)
                    accepted += 1

                if event.api is not None:
                    attempts_succeeded += 1
                    self.store.put_attempt(self._attempt_from_event(
                        event, next_attempt_id(event.item_key), run_id,
                        source_id, position, raw_record_id=record_id,
                        checksum=checksum, payload_reused=reused,
                    ))

                if reused or envelope is None:
                    continue
                try:
                    product = self._extract_product(envelope, event.payload)
                    # Staged publication: derivatives first, envelope last as
                    # the commit record.
                    for data in product.derivative_payloads.values():
                        self.store.put_derivative_payload(data)
                    self.store.put_extraction(product.result)
                    if product.result.outcome == "partial":
                        partial += 1
                except DataSourceError as error:
                    quarantined += 1
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
                attempts_planned=attempts_planned,
                attempts_succeeded=attempts_succeeded,
                attempts_failed=attempts_failed,
                error_summary="; ".join(errors),
            )
            self.store.put_run(run)
            return run

        # Precedence rule 1: a run with attempted acquisition and ZERO
        # progress (nothing retrieved, not even a reused payload) is
        # `failed` — counters and per-attempt evidence are preserved.
        if seen == 0 and attempts_failed > 0:
            status = "failed"
        else:
            status = resolve_completed_run_status(
                records_quarantined=quarantined, attempts_failed=attempts_failed
            )
        run = IngestionRun(
            run_id=run_id,
            source_id=source_id,
            started_at=started_at,
            finished_at=self.clock(),
            status=status,
            records_seen=seen,
            records_accepted=accepted,
            records_duplicate=duplicate,
            records_quarantined=quarantined,
            records_partial=partial,
            attempts_planned=attempts_planned,
            attempts_succeeded=attempts_succeeded,
            attempts_failed=attempts_failed,
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
            "completed_with_acquisition_failures": "degraded",
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
            api_evidence=self._api_health_evidence(source_id),
        )

    # -- acquisition helpers (DS-004) -------------------------------------

    @staticmethod
    def _locator_from_event(event) -> "ApiSourceLocator | None":
        if event.api is None:
            return None
        return ApiSourceLocator(
            adapter_id=event.api.adapter_id,
            endpoint_id=event.api.endpoint_id,
            item_key=event.item_key,
            request_fingerprint=event.api.request_fingerprint,
            request_canonical=event.api.request_canonical,
            source_content_type=event.api.source_content_type,
            extraction_route=event.api.extraction_route,
        )

    def _attempt_from_event(
        self, event, attempt_id, run_id, source_id, position,
        raw_record_id, checksum, payload_reused,
    ) -> AcquisitionAttempt:
        evidence = event.api
        succeeded = raw_record_id is not None
        return AcquisitionAttempt(
            attempt_id=attempt_id,
            ingestion_run_id=run_id,
            source_id=source_id,
            item_key=event.item_key,
            adapter_id=evidence.adapter_id,
            endpoint_id=evidence.endpoint_id,
            sweep_position=position,
            started_at=evidence.started_at,
            finished_at=evidence.finished_at,
            received_at=evidence.received_at,
            outcome="succeeded" if succeeded else "failed",
            request_fingerprint=evidence.request_fingerprint,
            request_canonical=evidence.request_canonical,
            target_origin=evidence.target_origin,
            status_code=evidence.status_code,
            allowlisted_headers=evidence.allowlisted_headers,
            transport_security=evidence.transport_security,
            response_size_bytes=evidence.response_size_bytes,
            retries_used=evidence.retries_used,
            payload_checksum=checksum,
            raw_record_id=raw_record_id,
            payload_reused=payload_reused,
            failure=None if succeeded else AttemptFailure(
                error_code=event.error_code,
                redacted_message=self._redact(event.redacted_message),
            ),
        )

    def _api_health_evidence(self, source_id: str) -> "ApiHealthEvidence | None":
        attempts = list(self.store.iter_attempts(source_id))
        if not attempts:
            return None
        consecutive = 0
        for attempt in reversed(attempts):
            if attempt.outcome == "failed":
                consecutive += 1
            else:
                break
        last = attempts[-1]
        last_success = next(
            (a for a in reversed(attempts) if a.outcome == "succeeded"), None
        )
        retry_after = None
        raw_retry = last.allowlisted_headers.get("Retry-After")
        if raw_retry is not None:
            try:
                retry_after = float(raw_retry)
            except ValueError:
                retry_after = None
        skew = None
        date_header = last.allowlisted_headers.get("Date")
        if date_header and last.received_at is not None:
            try:
                from email.utils import parsedate_to_datetime

                server_time = parsedate_to_datetime(date_header)
                skew = (server_time - last.received_at).total_seconds()
            except (ValueError, TypeError):
                skew = None
        return ApiHealthEvidence(
            consecutive_attempt_failures=consecutive,
            last_attempt_error_code=(
                last.failure.error_code if last.failure else None
            ),
            last_status_code=last.status_code,
            last_retry_after_seconds=retry_after,
            clock_skew_seconds=skew,
            plaintext_http_explicit=(
                last.transport_security == "plaintext_http_explicit"
            ),
            last_successful_attempt_at=(
                last_success.received_at if last_success else None
            ),
        )

    # -- extraction dispatch ---------------------------------------------

    def _extract_product(self, envelope: RawRecord, payload: bytes) -> ExtractionProduct:
        # Vendor-aware routing: an explicit extraction route stored with the
        # raw record wins; the source-reported media type is never enough to
        # give arbitrary JSON vendor semantics.
        if envelope.api_locator is not None:
            extractor = self.extractors.get(envelope.api_locator.extraction_route)
            if extractor is None:
                raise ExtractionError(
                    "EXTRACT_UNSUPPORTED_FORMAT",
                    f"no extractor registered for route "
                    f"{envelope.api_locator.extraction_route!r}",
                )
            return extractor(payload, envelope)
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

    def _extract_pdf(self, payload: bytes, envelope: RawRecord) -> ExtractionProduct:
        detection = detect_format(payload, declared_content_type=envelope.content_type)
        if detection.status != "confirmed_pdf":
            raise ExtractionError(
                "EXTRACT_UNSUPPORTED_OR_UNKNOWN_FORMAT", detection.evidence
            )
        product = extract_pdf(
            payload=payload,
            raw_record_id=envelope.record_id,
            config=self.pdf_config,
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
        return redact_text(scrub_secrets(text), base_dir=str(self.store.base_dir))
