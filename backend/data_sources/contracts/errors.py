"""Typed errors for the data_sources boundary.

Messages must be redacted (no secrets, no absolute paths) at the point of
raising, because these errors may be persisted in run reports and
quarantine records.
"""


class DataSourceError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class AcquisitionError(DataSourceError):
    """The connector could not reach or read the source."""


class ExtractionError(DataSourceError):
    """The payload's format-level structure could not be decoded."""


class StoreIntegrityError(DataSourceError):
    """An attempt was made to overwrite immutable stored content."""
