"""Read-only snapshot connector for a single local file.

The connector only acquires bytes and file-level metadata. It knows nothing
about CSV or any other format; extraction is a separate concern.
"""

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from backend.data_sources.contracts import (
    AcquisitionError,
    ConnectorManifest,
    ConnectorStatusReport,
    SourceDefinition,
    StatusCheck,
)
from backend.data_sources.extractors.dependencies import (
    check_extraction_dependencies,
)
from backend.data_sources.raw_store import FilesystemRawStore


class Acquisition(BaseModel):
    """Result of one snapshot acquisition, before enveloping."""

    model_config = ConfigDict(frozen=True)

    payload: bytes
    source_native_id: str
    source_observed_at: datetime
    provenance: dict[str, str]


class LocalFileConnector:
    MANIFEST = ConnectorManifest(
        connector_type="local_file",
        source_families=["tabular_file"],
        supported_formats_or_protocols=["text/csv"],
        acquisition_modes=["snapshot"],
        supported_extraction_levels=[0, 1],
        read_only=True,
        incremental_read_support=False,
        required_dependencies=[],
        maturity="experimental",
        known_limitations=[
            "single local file per source",
            "source_observed_at is the file modification time, not a true "
            "source-side observation timestamp",
        ],
    )

    def _configured_path(self, source: SourceDefinition) -> Path:
        raw_path = source.configuration.get("path", "").strip()
        if not raw_path:
            raise AcquisitionError(
                "ACQUIRE_NOT_CONFIGURED",
                f"source {source.source_id!r} has no 'path' configured",
            )
        return Path(raw_path)

    def probe(self, source: SourceDefinition) -> StatusCheck:
        try:
            path = self._configured_path(source)
        except AcquisitionError as error:
            return StatusCheck(passed=False, evidence=error.message)
        if not path.is_file():
            return StatusCheck(
                passed=False,
                evidence=f"configured file for source {source.source_id!r} "
                "does not exist or is not a regular file",
            )
        try:
            with path.open("rb") as handle:
                handle.read(1)
        except OSError:
            return StatusCheck(
                passed=False,
                evidence=f"configured file for source {source.source_id!r} "
                "exists but is not readable",
            )
        return StatusCheck(
            passed=True,
            evidence=f"opened and read configured file for source "
            f"{source.source_id!r} ({path.stat().st_size} bytes)",
        )

    def acquire(self, source: SourceDefinition) -> Acquisition:
        path = self._configured_path(source)
        try:
            payload = path.read_bytes()
            mtime = path.stat().st_mtime
        except OSError as error:
            raise AcquisitionError(
                "ACQUIRE_SOURCE_UNREADABLE",
                f"cannot read configured file for source {source.source_id!r} "
                f"({error.__class__.__name__})",
            ) from error
        return Acquisition(
            payload=payload,
            source_native_id=path.name,
            source_observed_at=datetime.fromtimestamp(mtime, tz=UTC),
            provenance={
                "acquisition_mode": "snapshot",
                "connector_type": "local_file",
                "observed_at_meaning": "file_mtime",
            },
        )

    def status_report(
        self, source: SourceDefinition, store: FilesystemRawStore
    ) -> ConnectorStatusReport:
        declared = StatusCheck(
            passed=True,
            evidence="local_file is declared in the connector manifest",
        )
        content_type = (
            source.declared_content_types[0]
            if source.declared_content_types
            else "application/octet-stream"
        )
        deps_ok, deps_evidence = check_extraction_dependencies(content_type)
        available = StatusCheck(passed=deps_ok, evidence=deps_evidence)
        try:
            self._configured_path(source)
            configured = StatusCheck(
                passed=True,
                evidence=f"source {source.source_id!r} declares a file path",
            )
        except AcquisitionError as error:
            configured = StatusCheck(passed=False, evidence=error.message)
        connected = (
            self.probe(source)
            if configured.passed
            else StatusCheck(passed=False, evidence="not configured")
        )
        validated = self._validation_status(source, store)
        return ConnectorStatusReport(
            connector_type="local_file",
            source_id=source.source_id,
            declared=declared,
            available=available,
            configured=configured,
            connected=connected,
            validated=validated,
        )

    @staticmethod
    def _validation_status(
        source: SourceDefinition, store: FilesystemRawStore
    ) -> StatusCheck:
        successful = [
            run
            for run in store.iter_runs(source.source_id)
            if run.status == "succeeded" and run.records_accepted > 0
        ]
        if not successful:
            return StatusCheck(passed=False, evidence="")
        latest = max(successful, key=lambda run: run.finished_at)
        return StatusCheck(
            passed=True,
            evidence=f"run {latest.run_id} accepted "
            f"{latest.records_accepted} record(s) at {latest.finished_at.isoformat()}",
        )
