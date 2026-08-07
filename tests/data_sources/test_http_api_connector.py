"""HTTP API connector tests: network policy, event stream, evidence,
secret hygiene, bounds — using a deterministic transport stub, plus a
small real-loopback transport test (stdlib only, no markers needed)."""

import http.server
import json
import threading
from datetime import UTC, datetime

import pytest

from backend.data_sources.connectors.events import (
    AcquisitionFailed,
    AcquisitionSucceeded,
)
from backend.data_sources.connectors.http_api import (
    HttpApiConnector,
    StaticCredentialResolver,
    TransportError,
    TransportRequest,
    TransportResponse,
    UrllibTransport,
    validate_target_address,
)
from backend.data_sources.contracts import AcquisitionError, SourceDefinition


class PlanItem:
    def __init__(self, item_key, endpoint_id, path_and_query):
        self.item_key = item_key
        self.endpoint_id = endpoint_id
        self.path_and_query = path_and_query


class FakeAdapter:
    adapter_id = "moonraker"
    extraction_route = "api:moonraker:v1"

    def plan(self):
        return [
            PlanItem("server_info", "server_info", "/server/info"),
            PlanItem(
                "printer_objects", "printer_objects_query",
                "/printer/objects/query?extruder=target,temperature",
            ),
        ]

    def auth_headers(self, resolver, credential_reference):
        if credential_reference is None:
            return {}
        return {"X-Api-Key": resolver.resolve(credential_reference)}


def make_source(base_url="http://127.0.0.1:7125", credential=None,
                allow_http="true", scope="loopback_only") -> SourceDefinition:
    return SourceDefinition(
        source_id="printer-1", display_name="printer", source_kind="operational_api",
        connector_type="http_api",
        configuration={
            "base_url": base_url, "adapter": "moonraker",
            "allow_plaintext_http": allow_http, "plaintext_scope": scope,
        },
        credential_reference=credential,
        declared_content_types=["application/json"], enabled=True,
    )


class ScriptedTransport:
    """Deterministic transport stub: item path -> response or exception."""

    def __init__(self, script):
        self.script = script
        self.requests = []

    def __call__(self, request: TransportRequest) -> TransportResponse:
        self.requests.append(request)
        for needle, outcome in self.script.items():
            if needle in request.url:
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise AssertionError(f"unscripted url {request.url}")


def ok_json(body: dict, headers=None) -> TransportResponse:
    data = json.dumps(body).encode()
    return TransportResponse(
        status=200,
        headers={"Content-Type": "application/json", **(headers or {})},
        body=data,
    )


def make_connector(transport, resolver=None, **kwargs):
    return HttpApiConnector(
        adapters={"moonraker": FakeAdapter()},
        transport=transport,
        credential_resolver=resolver or StaticCredentialResolver({}),
        clock=lambda: datetime(2026, 8, 7, 19, 0, 0, tzinfo=UTC),
        **kwargs,
    )


class TestNetworkPolicy:
    def test_always_rejected_destinations(self):
        for ip in ("169.254.169.254", "224.0.0.1", "0.0.0.0", "fe80::1"):
            with pytest.raises(AcquisitionError) as excinfo:
                validate_target_address(ip, scheme="https", allow_plaintext=False,
                                        plaintext_scope="loopback_only")
            assert excinfo.value.error_code == "ACQUIRE_DESTINATION_FORBIDDEN"

    def test_plaintext_http_scope(self):
        # loopback ok under loopback_only
        validate_target_address("127.0.0.1", scheme="http", allow_plaintext=True,
                                plaintext_scope="loopback_only")
        # private LAN denied under loopback_only, allowed under private_lan
        with pytest.raises(AcquisitionError):
            validate_target_address("192.168.1.50", scheme="http",
                                    allow_plaintext=True,
                                    plaintext_scope="loopback_only")
        validate_target_address("192.168.1.50", scheme="http", allow_plaintext=True,
                                plaintext_scope="private_lan")
        # IPv6 unique-local handled explicitly: private_lan only
        validate_target_address("fd12:3456::1", scheme="http", allow_plaintext=True,
                                plaintext_scope="private_lan")
        with pytest.raises(AcquisitionError):
            validate_target_address("fd12:3456::1", scheme="http",
                                    allow_plaintext=True,
                                    plaintext_scope="loopback_only")
        # public plaintext never allowed
        with pytest.raises(AcquisitionError):
            validate_target_address("8.8.8.8", scheme="http", allow_plaintext=True,
                                    plaintext_scope="private_lan")

    def test_plaintext_requires_explicit_configuration(self):
        with pytest.raises(AcquisitionError) as excinfo:
            validate_target_address("127.0.0.1", scheme="http",
                                    allow_plaintext=False,
                                    plaintext_scope="loopback_only")
        assert "plaintext" in str(excinfo.value).lower()

    def test_https_to_public_is_permitted(self):
        validate_target_address("203.0.113.7", scheme="https",
                                allow_plaintext=False,
                                plaintext_scope="loopback_only")


class TestEventStream:
    def test_two_successes_in_plan_order_with_evidence(self):
        transport = ScriptedTransport({
            "/server/info": ok_json({"result": {"klippy_state": "ready"}},
                                    headers={"Date": "Fri, 07 Aug 2026 19:00:01 GMT"}),
            "/printer/objects/query": ok_json({"result": {"eventtime": 1.5}}),
        })
        connector = make_connector(transport)
        events = list(connector.acquire_events(make_source()))
        assert [type(e) for e in events] == [AcquisitionSucceeded] * 2
        assert [e.item_key for e in events] == ["server_info", "printer_objects"]
        first = events[0]
        assert first.identity_mode == "keyed"
        assert first.api.request_fingerprint.startswith("sha256:")
        assert len(first.api.request_fingerprint) == len("sha256:") + 64
        assert first.api.request_canonical == "GET /server/info"
        assert first.api.target_origin == "http://127.0.0.1:7125"
        assert first.api.transport_security == "plaintext_http_explicit"
        assert first.api.allowlisted_headers.get("Date")
        assert first.api.received_at is not None
        assert connector.planned_items(make_source()) == 2

    def test_failure_at_item_two_still_yields_item_one(self):
        transport = ScriptedTransport({
            "/server/info": ok_json({"result": {}}),
            "/printer/objects/query": TransportError("timeout", "deadline exceeded"),
        })
        events = list(make_connector(transport).acquire_events(make_source()))
        assert isinstance(events[0], AcquisitionSucceeded)
        assert isinstance(events[1], AcquisitionFailed)
        assert events[1].error_code == "ACQUIRE_TIMEOUT"
        assert events[1].api.received_at is None  # never fabricated

    def test_http_error_statuses_map_to_typed_failures(self):
        transport = ScriptedTransport({
            "/server/info": TransportResponse(
                status=429, headers={"Retry-After": "30"}, body=b""),
            "/printer/objects/query": TransportResponse(
                status=401, headers={}, body=b"unauthorized"),
        })
        events = list(make_connector(transport).acquire_events(make_source()))
        assert events[0].error_code == "ACQUIRE_RATE_LIMITED"
        assert events[0].api.allowlisted_headers["Retry-After"] == "30"
        assert events[1].error_code == "ACQUIRE_AUTH_FAILED"
        assert events[1].api.received_at is not None  # a response WAS received

    def test_redirect_refused(self):
        transport = ScriptedTransport({
            "/server/info": TransportError("redirect", "redirect refused"),
            "/printer/objects/query": ok_json({"result": {}}),
        })
        events = list(make_connector(transport).acquire_events(make_source()))
        assert events[0].error_code == "ACQUIRE_REDIRECT_REFUSED"

    def test_oversized_response_refused(self):
        big = TransportResponse(status=200, headers={}, body=b"x" * 2048)
        transport = ScriptedTransport({
            "/server/info": big, "/printer/objects/query": ok_json({"result": {}}),
        })
        connector = make_connector(transport, max_response_bytes=1024)
        events = list(connector.acquire_events(make_source()))
        assert events[0].error_code == "ACQUIRE_RESPONSE_TOO_LARGE"

    def test_secret_resolved_in_memory_only(self):
        transport = ScriptedTransport({
            "/server/info": ok_json({"result": {}}),
            "/printer/objects/query": ok_json({"result": {}}),
        })
        resolver = StaticCredentialResolver({"moonraker-key": "hunter2-token"})
        connector = make_connector(transport, resolver=resolver)
        events = list(connector.acquire_events(
            make_source(credential="moonraker-key")))
        # the header reached the transport...
        assert transport.requests[0].headers["X-Api-Key"] == "hunter2-token"
        # ...but appears in no event evidence
        for event in events:
            dumped = repr(event.__dict__) + repr(event.api.__dict__)
            assert "hunter2-token" not in dumped

    def test_unresolvable_credential_is_source_level_failure(self):
        transport = ScriptedTransport({})
        connector = make_connector(transport)
        with pytest.raises(AcquisitionError) as excinfo:
            list(connector.acquire_events(make_source(credential="missing-ref")))
        assert excinfo.value.error_code == "ACQUIRE_CREDENTIAL_UNRESOLVED"
        assert "missing-ref" in str(excinfo.value)  # name ok, no value to leak

    def test_plaintext_not_configured_is_source_level_failure(self):
        connector = make_connector(ScriptedTransport({}))
        with pytest.raises(AcquisitionError):
            list(connector.acquire_events(make_source(allow_http="false")))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/redirect"):
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1:1/evil")
            self.end_headers()
            return
        body = json.dumps({"result": {"ok": True}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestRealLoopbackTransport:
    @pytest.fixture
    def server(self):
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        yield srv
        srv.shutdown()

    def test_get_redirect_refusal_and_proxy_isolation(self, server, monkeypatch):
        monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
        monkeypatch.setenv("http_proxy", "http://127.0.0.1:1")
        port = server.server_address[1]
        transport = UrllibTransport()
        response = transport(TransportRequest(
            url=f"http://127.0.0.1:{port}/server/info", headers={}, timeout=5.0,
            max_response_bytes=1_000_000,
        ))
        assert response.status == 200
        assert json.loads(response.body)["result"]["ok"] is True
        with pytest.raises(TransportError) as excinfo:
            transport(TransportRequest(
                url=f"http://127.0.0.1:{port}/redirect", headers={}, timeout=5.0,
                max_response_bytes=1_000_000,
            ))
        assert excinfo.value.kind == "redirect"


class FakeMonotonic:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class ClockedTransport:
    """Advances an injected monotonic clock per call and records the
    timeout each request was given."""

    def __init__(self, clock: FakeMonotonic, outcomes):
        self.clock = clock
        self.outcomes = list(outcomes)  # (advance_seconds, response-or-exc)
        self.timeouts: list[float] = []

    def __call__(self, request: TransportRequest) -> TransportResponse:
        self.timeouts.append(request.timeout)
        advance, outcome = self.outcomes.pop(0)
        self.clock.now += advance
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class TestSweepDeadlineAcrossRetries:
    """Repair: the total sweep budget is recomputed before every transport
    call, before every retry, and after every return."""

    def _connector(self, transport, clock):
        return HttpApiConnector(
            adapters={"moonraker": FakeAdapter()},
            transport=transport,
            credential_resolver=StaticCredentialResolver({}),
            monotonic=clock,
            request_timeout_seconds=10.0,
            sweep_deadline_seconds=5.0,
            max_retries=1,
        )

    def test_retry_timeout_capped_by_remaining_budget(self):
        clock = FakeMonotonic()
        transport = ClockedTransport(clock, [
            (4.9, TransportError("timeout", "slow")),   # first call eats 4.9s
            (0.2, TransportError("timeout", "slow")),   # retry crosses deadline
        ])
        events = list(self._connector(transport, clock).acquire_events(make_source()))
        # first call got (close to) the full budget; the retry got <= 0.1s
        assert transport.timeouts[0] == pytest.approx(5.0, abs=0.01)
        assert transport.timeouts[1] <= 0.1 + 1e-6
        assert isinstance(events[0], AcquisitionFailed)
        assert events[0].error_code == "ACQUIRE_SWEEP_DEADLINE"
        assert events[0].api.retries_used == 1
        assert events[0].api.received_at is None
        # the second planned item is represented honestly, never attempted
        assert events[1].error_code == "ACQUIRE_SWEEP_DEADLINE"
        assert events[1].api.request_canonical.startswith("GET /printer/objects")
        assert len(transport.timeouts) == 2  # no transport call for item two

    def test_exhausted_budget_prevents_retry_entirely(self):
        clock = FakeMonotonic()
        transport = ClockedTransport(clock, [
            (5.1, TransportError("timeout", "slow")),   # eats the whole budget
        ])
        events = list(self._connector(transport, clock).acquire_events(make_source()))
        assert events[0].error_code == "ACQUIRE_SWEEP_DEADLINE"
        assert events[0].api.retries_used == 0  # no retry once exhausted
        assert len(transport.timeouts) == 1

    def test_late_response_after_deadline_is_not_accepted(self):
        clock = FakeMonotonic()
        late = TransportResponse(
            status=200, headers={"Content-Type": "application/json"},
            body=b'{"result": {}}',
        )
        transport = ClockedTransport(clock, [(6.0, late)])
        events = list(self._connector(transport, clock).acquire_events(make_source()))
        first = events[0]
        assert isinstance(first, AcquisitionFailed)
        assert first.error_code == "ACQUIRE_SWEEP_DEADLINE"
        assert first.api.received_at is not None  # a response DID arrive...
        assert first.api.status_code == 200       # ...and is recorded honestly
        assert not any(isinstance(e, AcquisitionSucceeded) for e in events)
