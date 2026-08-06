"""Public contract surface of the data_sources module."""

from backend.data_sources.contracts.errors import (
    AcquisitionError,
    DataSourceError,
    ExtractionError,
    StoreIntegrityError,
)
from backend.data_sources.contracts.models import (
    AcquisitionMode,
    ConnectorManifest,
    ConnectorStatusReport,
    ExtractedCell,
    ExtractedRow,
    ExtractedTable,
    HealthStatus,
    IngestionRun,
    Maturity,
    QuarantineRecord,
    RawRecord,
    RunStatus,
    SourceDefinition,
    SourceHealth,
    StatusCheck,
)

__all__ = [
    "AcquisitionError",
    "AcquisitionMode",
    "ConnectorManifest",
    "ConnectorStatusReport",
    "DataSourceError",
    "ExtractedCell",
    "ExtractedRow",
    "ExtractedTable",
    "ExtractionError",
    "HealthStatus",
    "IngestionRun",
    "Maturity",
    "QuarantineRecord",
    "RawRecord",
    "RunStatus",
    "SourceDefinition",
    "SourceHealth",
    "StatusCheck",
    "StoreIntegrityError",
]
