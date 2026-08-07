"""Connector implementations (acquisition only, no format extraction)."""

from backend.data_sources.connectors.events import (
    AcquisitionFailed,
    AcquisitionSucceeded,
    ApiAttemptEvidence,
)
from backend.data_sources.connectors.http_api import (
    CredentialResolver,
    EnvironmentCredentialResolver,
    HttpApiConnector,
    StaticCredentialResolver,
    UrllibTransport,
)
from backend.data_sources.connectors.local_file import Acquisition, LocalFileConnector

__all__ = [
    "Acquisition",
    "AcquisitionFailed",
    "AcquisitionSucceeded",
    "ApiAttemptEvidence",
    "CredentialResolver",
    "EnvironmentCredentialResolver",
    "HttpApiConnector",
    "LocalFileConnector",
    "StaticCredentialResolver",
    "UrllibTransport",
]
