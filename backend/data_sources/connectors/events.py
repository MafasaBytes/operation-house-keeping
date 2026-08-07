"""Typed acquisition events for the incremental connector boundary.

The runtime pulls events one at a time and persists each successful
payload plus its acquisition attempt BEFORE requesting the next event, so
a failure at a later item can never discard an earlier one.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class ApiAttemptEvidence:
    """Attempt-occurrence facts gathered by the connector for one item.

    Lives only on events/attempts — never on raw records — so a first
    occurrence's timestamps can't masquerade as a later duplicate's.
    """

    adapter_id: str
    endpoint_id: str
    request_fingerprint: str
    request_canonical: str
    target_origin: str
    transport_security: Literal["tls_verified", "plaintext_http_explicit"]
    started_at: datetime
    finished_at: datetime
    received_at: datetime | None
    status_code: int | None
    allowlisted_headers: dict[str, str] = field(default_factory=dict)
    response_size_bytes: int | None = None
    retries_used: int = 0
    source_content_type: str | None = None
    extraction_route: str | None = None


@dataclass
class AcquisitionSucceeded:
    item_key: str
    payload: bytes
    identity_mode: Literal["positional", "keyed"]
    content_type: str | None = None
    source_native_id: str | None = None
    source_observed_at: datetime | None = None
    provenance: dict[str, str] = field(default_factory=dict)
    api: ApiAttemptEvidence | None = None


@dataclass
class AcquisitionFailed:
    item_key: str
    error_code: str
    redacted_message: str
    api: ApiAttemptEvidence | None = None
