"""Generic read-only HTTP API connector (DS-004).

GET-only, bounded, vendor-blind. Adapters supply the endpoint plan and
auth headers; an injectable transport performs the actual I/O (production:
stdlib urllib with no proxy inheritance, no redirects, verified TLS).
Security posture per the DS-004 spec: HTTPS always verified (unverified
HTTPS unsupported), plaintext HTTP only by explicit configuration to
loopback/approved-private-LAN targets, per-request address screening, and
credentials resolved in memory only via an injected CredentialResolver.
"""

import gzip
import hashlib
import io
import ipaddress
import socket
import time as _time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Callable, Iterator, Protocol
from urllib.parse import urlsplit

from backend.data_sources.connectors.events import (
    AcquisitionFailed,
    AcquisitionSucceeded,
    ApiAttemptEvidence,
)
from backend.data_sources.contracts import (
    AcquisitionError,
    ConnectorManifest,
    SourceDefinition,
    StatusCheck,
)

_HEADER_ALLOWLIST = ("Content-Type", "Date", "Retry-After", "X-Request-Id")
_HEADER_VALUE_BOUND = 200


# transport
@dataclass
class TransportRequest:
    url: str
    headers: dict[str, str]
    timeout: float
    max_response_bytes: int


@dataclass
class TransportResponse:
    status: int
    headers: dict[str, str]
    body: bytes


class TransportError(Exception):
    """kind: timeout | connection | tls | redirect | oversize"""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


Transport = Callable[[TransportRequest], TransportResponse]


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise TransportError("redirect", f"redirect refused (HTTP {code})")


class UrllibTransport:
    """Stdlib transport: explicit handler list (proxy environment is never
    consulted), redirects refused, TLS verified by the default context."""

    def __init__(self) -> None:
        self._opener = urllib.request.OpenerDirector()
        for handler in (
            urllib.request.HTTPHandler(),
            urllib.request.HTTPSHandler(),  # default verified SSL context
            _RefuseRedirects(),
            urllib.request.HTTPDefaultErrorHandler(),
            urllib.request.HTTPErrorProcessor(),
        ):
            self._opener.add_handler(handler)

    def __call__(self, request: TransportRequest) -> TransportResponse:
        req = urllib.request.Request(request.url, headers=request.headers,
                                     method="GET")
        try:
            response = self._opener.open(req, timeout=request.timeout)
        except TransportError:
            raise
        except urllib.error.HTTPError as error:
            body = error.read(request.max_response_bytes + 1) or b""
            return TransportResponse(
                status=error.code, headers=dict(error.headers or {}), body=body
            )
        except TimeoutError as error:
            raise TransportError("timeout", "request timed out") from error
        except urllib.error.URLError as error:
            reason = str(getattr(error, "reason", error))
            kind = "timeout" if "timed out" in reason.lower() else (
                "tls" if "certificate" in reason.lower() else "connection")
            raise TransportError(kind, f"transport failure ({kind})") from error
        except OSError as error:
            raise TransportError("connection", type(error).__name__) from error

        with response:
            raw = response.read(request.max_response_bytes + 1)
            if len(raw) > request.max_response_bytes:
                raise TransportError("oversize", "response exceeds size limit")
            headers = dict(response.headers)
            if headers.get("Content-Encoding", "").lower() == "gzip":
                stream = gzip.GzipFile(fileobj=io.BytesIO(raw))
                raw = stream.read(request.max_response_bytes + 1)
                if len(raw) > request.max_response_bytes:
                    raise TransportError(
                        "oversize", "decompressed response exceeds size limit"
                    )
            return TransportResponse(status=response.status, headers=headers,
                                     body=raw)


# credentials
class CredentialResolver(Protocol):
    def resolve(self, reference: str) -> str: ...


class StaticCredentialResolver:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = dict(values)

    def resolve(self, reference: str) -> str:
        try:
            return self._values[reference]
        except KeyError:
            raise AcquisitionError(
                "ACQUIRE_CREDENTIAL_UNRESOLVED",
                f"credential reference {reference!r} cannot be resolved",
            ) from None


class EnvironmentCredentialResolver:
    """Resolves a credential_reference as an environment variable name."""

    def resolve(self, reference: str) -> str:
        import os

        value = os.environ.get(reference)
        if value is None:
            raise AcquisitionError(
                "ACQUIRE_CREDENTIAL_UNRESOLVED",
                f"credential reference {reference!r} cannot be resolved",
            )
        return value


# network policy
def _classify(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str:
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link_local"
    if ip.is_multicast:
        return "multicast"
    if ip.is_unspecified:
        return "unspecified"
    if isinstance(ip, ipaddress.IPv6Address) and ip in ipaddress.ip_network("fc00::/7"):
        return "unique_local"  # IPv6 ULA: handled explicitly, never by accident
    if ip.is_private:
        return "private"
    return "public"


def validate_target_address(
    ip_text: str, scheme: str, allow_plaintext: bool, plaintext_scope: str
) -> str:
    """Validate one resolved destination address against the network policy.

    Link-local (incl. cloud metadata), multicast, and unspecified are always
    rejected. Plaintext HTTP requires explicit configuration and is limited
    to loopback (or, under the private_lan scope, RFC-1918/ULA). Verified
    HTTPS may reach any not-always-rejected destination.
    """
    kind = _classify(ipaddress.ip_address(ip_text.split("%")[0]))
    if kind in ("link_local", "multicast", "unspecified"):
        raise AcquisitionError(
            "ACQUIRE_DESTINATION_FORBIDDEN",
            f"destination address class {kind!r} is never permitted",
        )
    if scheme == "http":
        if not allow_plaintext:
            raise AcquisitionError(
                "ACQUIRE_DESTINATION_FORBIDDEN",
                "plaintext HTTP requires explicit configuration",
            )
        allowed = {"loopback"} if plaintext_scope == "loopback_only" else {
            "loopback", "private", "unique_local"}
        if kind not in allowed:
            raise AcquisitionError(
                "ACQUIRE_DESTINATION_FORBIDDEN",
                f"plaintext HTTP to a {kind!r} destination is not permitted "
                f"under the {plaintext_scope!r} policy",
            )
    return kind


# connector
class HttpApiConnector:
    MANIFEST = ConnectorManifest(
        connector_type="http_api",
        source_families=["operational_api"],
        supported_formats_or_protocols=["http", "https"],
        acquisition_modes=["poll"],
        supported_extraction_levels=[0, 1, 2],
        read_only=True,
        incremental_read_support=False,
        required_dependencies=[],
        maturity="experimental",
        known_limitations=[
            "bounded snapshot sweeps only; no streaming",
            "stdlib transport leaves a documented DNS-rebinding window "
            "between address validation and connection",
        ],
    )

    def __init__(
        self,
        adapters: dict[str, object],
        transport: Transport | None = None,
        credential_resolver: CredentialResolver | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(tz=UTC),
        monotonic: Callable[[], float] = _time.monotonic,
        request_timeout_seconds: float = 10.0,
        sweep_deadline_seconds: float = 30.0,
        max_response_bytes: int = 4 * 1024 * 1024,
        max_retries: int = 1,
        resolve_addresses: Callable[[str], list[str]] | None = None,
    ) -> None:
        self.adapters = adapters
        self.transport = transport or UrllibTransport()
        self.credential_resolver = credential_resolver or EnvironmentCredentialResolver()
        self.clock = clock
        self.monotonic = monotonic
        self.request_timeout_seconds = request_timeout_seconds
        self.sweep_deadline_seconds = sweep_deadline_seconds
        self.max_response_bytes = max_response_bytes
        self.max_retries = max_retries
        self.resolve_addresses = resolve_addresses or self._getaddrinfo

    @staticmethod
    def _getaddrinfo(host: str) -> list[str]:
        try:
            infos = socket.getaddrinfo(host, None)
        except OSError as error:
            raise AcquisitionError(
                "ACQUIRE_DNS_FAILED", f"cannot resolve configured host "
                f"({type(error).__name__})",
            ) from error
        return sorted({info[4][0] for info in infos})

    def _config(self, source: SourceDefinition):
        base_url = source.configuration.get("base_url", "").strip()
        parts = urlsplit(base_url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise AcquisitionError(
                "ACQUIRE_NOT_CONFIGURED",
                f"source {source.source_id!r} has no valid base_url",
            )
        adapter_name = source.configuration.get("adapter", "")
        try:
            adapter = self.adapters[adapter_name]
        except KeyError:
            raise AcquisitionError(
                "ACQUIRE_CONNECTOR_UNAVAILABLE",
                f"no adapter {adapter_name!r} is registered",
            ) from None
        allow_plaintext = source.configuration.get(
            "allow_plaintext_http", "false").lower() == "true"
        scope = source.configuration.get("plaintext_scope", "loopback_only")
        port = parts.port or (443 if parts.scheme == "https" else 80)
        origin = f"{parts.scheme}://{parts.hostname}:{port}" if parts.port else (
            f"{parts.scheme}://{parts.hostname}")
        return adapter, parts.scheme, parts.hostname, origin, allow_plaintext, scope

    def planned_items(self, source: SourceDefinition) -> int:
        adapter, *_ = self._config(source)
        return len(adapter.plan())

    def probe(self, source: SourceDefinition) -> StatusCheck:
        try:
            adapter, scheme, host, origin, allow_plaintext, scope = self._config(source)
            for address in self.resolve_addresses(host):
                validate_target_address(address, scheme, allow_plaintext, scope)
        except AcquisitionError as error:
            return StatusCheck(passed=False, evidence=error.message)
        return StatusCheck(
            passed=True,
            evidence=f"origin {origin} passes the configured network policy",
        )

    def acquire_events(
        self, source: SourceDefinition
    ) -> Iterator[AcquisitionSucceeded | AcquisitionFailed]:
        adapter, scheme, host, origin, allow_plaintext, scope = self._config(source)
        # source-level guards: credentials + destination policy for the
        # pinned origin. Failures here mean no meaningful progress.
        auth_headers = adapter.auth_headers(
            self.credential_resolver, source.credential_reference
        )
        for address in self.resolve_addresses(host):
            validate_target_address(address, scheme, allow_plaintext, scope)
        transport_security = (
            "tls_verified" if scheme == "https" else "plaintext_http_explicit"
        )
        deadline = self.monotonic() + self.sweep_deadline_seconds

        for item in adapter.plan():
            canonical = f"GET {item.path_and_query}"
            fingerprint = "sha256:" + hashlib.sha256(
                f"{origin} {canonical}".encode()
            ).hexdigest()
            evidence = ApiAttemptEvidence(
                adapter_id=adapter.adapter_id,
                endpoint_id=item.endpoint_id,
                request_fingerprint=fingerprint,
                request_canonical=canonical,
                target_origin=origin,
                transport_security=transport_security,
                started_at=self.clock(),
                finished_at=self.clock(),
                received_at=None,
                status_code=None,
                extraction_route=adapter.extraction_route,
            )
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                evidence.finished_at = self.clock()
                yield AcquisitionFailed(
                    item_key=item.item_key,
                    error_code="ACQUIRE_SWEEP_DEADLINE",
                    redacted_message="total sweep deadline exceeded before "
                    "this item was attempted",
                    api=evidence,
                )
                continue
            # re-validate destinations immediately before each connection
            for address in self.resolve_addresses(host):
                validate_target_address(address, scheme, allow_plaintext, scope)

            response = None
            failure: tuple[str, str] | None = None
            retries = 0
            while True:
                try:
                    response = self.transport(TransportRequest(
                        url=origin + item.path_and_query,
                        headers=dict(auth_headers),
                        timeout=min(self.request_timeout_seconds, max(remaining, 0.1)),
                        max_response_bytes=self.max_response_bytes,
                    ))
                    break
                except TransportError as error:
                    code = {
                        "timeout": "ACQUIRE_TIMEOUT",
                        "redirect": "ACQUIRE_REDIRECT_REFUSED",
                        "tls": "ACQUIRE_TLS_FAILED",
                        "oversize": "ACQUIRE_RESPONSE_TOO_LARGE",
                        "connection": "ACQUIRE_SOURCE_UNREACHABLE",
                    }.get(error.kind, "ACQUIRE_SOURCE_UNREACHABLE")
                    if error.kind in ("timeout", "connection") and retries < self.max_retries:
                        retries += 1
                        continue
                    failure = (code, str(error))
                    break
            evidence.retries_used = retries
            evidence.finished_at = self.clock()

            if failure is not None:
                yield AcquisitionFailed(
                    item_key=item.item_key, error_code=failure[0],
                    redacted_message=failure[1], api=evidence,
                )
                continue

            evidence.received_at = evidence.finished_at
            evidence.status_code = response.status
            evidence.allowlisted_headers = {
                name: str(response.headers[name])[:_HEADER_VALUE_BOUND]
                for name in _HEADER_ALLOWLIST if name in response.headers
            }
            evidence.response_size_bytes = len(response.body)
            evidence.source_content_type = response.headers.get("Content-Type")

            if response.status == 200:
                if len(response.body) > self.max_response_bytes:
                    yield AcquisitionFailed(
                        item_key=item.item_key,
                        error_code="ACQUIRE_RESPONSE_TOO_LARGE",
                        redacted_message="response exceeds the configured size limit",
                        api=evidence,
                    )
                    continue
                yield AcquisitionSucceeded(
                    item_key=item.item_key,
                    payload=response.body,
                    identity_mode="keyed",
                    content_type="application/json",
                    provenance={"acquisition_mode": "poll",
                                "connector_type": "http_api"},
                    api=evidence,
                )
            else:
                code = {
                    401: "ACQUIRE_AUTH_FAILED", 403: "ACQUIRE_AUTH_FAILED",
                    429: "ACQUIRE_RATE_LIMITED",
                }.get(response.status, "ACQUIRE_HTTP_ERROR")
                yield AcquisitionFailed(
                    item_key=item.item_key, error_code=code,
                    redacted_message=f"HTTP {response.status} from the source",
                    api=evidence,
                )
