"""End-to-end DS-004 runtime tests: Moonraker snapshots through the full
source boundary using the deterministic transport stub (stdlib only)."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from backend.data_sources.adapters.moonraker import MoonrakerAdapter
from backend.data_sources.catalog import InMemorySourceCatalog
from backend.data_sources.connectors import (
    HttpApiConnector,
    LocalFileConnector,
    StaticCredentialResolver,
)
from backend.data_sources.contracts import SourceDefinition
from backend.data_sources.raw_store import FilesystemRawStore
from backend.data_sources.runtime import IngestionRunner

from tests.data_sources.test_http_api_connector import (
    ScriptedTransport,
    ok_json,
)
from tests.data_sources import golden_moonraker as golden

FIXTURES = Path("backend/data_sources/testing/fixtures/api")


class FakeClock:
    def __init__(self) -> None:
        self._now = datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self._now += timedelta(seconds=1)
        return self._now


def fixture_response(name: str):
    from backend.data_sources.connectors.http_api import TransportResponse

    return TransportResponse(
        status=200,
        headers={"Content-Type": "application/json",
                 "Date": "Fri, 07 Aug 2026 20:00:05 GMT"},
        body=(FIXTURES / name).read_bytes(),
    )


def happy_script() -> dict:
    return {
        "/server/info": fixture_response("moonraker_server_info.json"),
        "/printer/objects/query": fixture_response("moonraker_printer_objects.json"),
    }


def make_source(credential=None) -> SourceDefinition:
    return SourceDefinition(
        source_id="printer-1", display_name="voron-1", source_kind="operational_api",
        connector_type="http_api",
        configuration={
            "base_url": "http://127.0.0.1:7125", "adapter": "moonraker",
            "allow_plaintext_http": "true", "plaintext_scope": "loopback_only",
        },
        credential_reference=credential,
        declared_content_types=["application/json"], enabled=True,
    )


def make_runner(tmp_path, script, credential_values=None, credential=None):
    transport = ScriptedTransport(script)
    connector = HttpApiConnector(
        adapters={"moonraker": MoonrakerAdapter()},
        transport=transport,
        credential_resolver=StaticCredentialResolver(credential_values or {}),
        clock=FakeClock(),
    )
    catalog = InMemorySourceCatalog()
    catalog.register(make_source(credential=credential))
    store = FilesystemRawStore(tmp_path / "raw_store")
    runner = IngestionRunner(
        catalog=catalog, store=store,
        connectors={"local_file": LocalFileConnector(), "http_api": connector},
        clock=FakeClock(),
    )
    return runner, store, transport


class TestSuccessfulSweep:
    def test_full_sweep_with_field_level_provenance(self, tmp_path):
        runner, store, _ = make_runner(tmp_path, happy_script())
        run = runner.run("printer-1")
        assert run.status == "succeeded"
        assert (run.attempts_planned, run.attempts_succeeded,
                run.attempts_failed) == (2, 2, 0)
        assert (run.records_seen, run.records_accepted) == (2, 2)

        attempts = list(store.iter_attempts("printer-1"))
        assert len(attempts) == 2
        assert all(a.outcome == "succeeded" for a in attempts)
        assert {a.item_key for a in attempts} == {"server_info", "printer_objects"}

        envelopes = {e.api_locator.item_key: e
                     for e in store.iter_accepted_envelopes("printer-1")}
        assert envelopes["printer_objects"].api_locator.extraction_route == (
            "api:moonraker:v1"
        )
        assert envelopes["printer_objects"].api_locator.request_canonical == (
            "GET " + golden.CANONICAL_QUERY
        )

        # field-level provenance: pointer resolves inside the stored bytes
        record = envelopes["printer_objects"]
        result = store.get_extraction(record.record_id)
        obs = next(o for o in result.manifest_view().observations
                   if o.json_pointer == "/result/status/extruder/temperature")
        payload = store.get_payload(record.immutable_payload_reference)
        parsed = json.loads(payload.decode())
        assert parsed["result"]["status"]["extruder"]["temperature"] == 60.1
        assert obs.value_json == "60.1"
        assert obs.source_time.kind == "monotonic"
        assert obs.source_time.value == golden.EVENTTIME_LEXEME
        assert store.find_uncommitted_api_artifacts() == {
            "uncommitted_api_envelopes": [], "unreferenced_payloads": []}

    def test_health_evidence_after_success(self, tmp_path):
        runner, store, _ = make_runner(tmp_path, happy_script())
        runner.run("printer-1")
        health = runner.health("printer-1")
        assert health.status == "ok"
        evidence = health.api_evidence
        assert evidence.consecutive_attempt_failures == 0
        assert evidence.plaintext_http_explicit is True
        assert evidence.last_successful_attempt_at is not None
        assert evidence.clock_skew_seconds is not None  # Date header present


class TestOccurrenceVsPayload:
    def test_byte_identical_repoll_reuses_payload_records_new_attempts(self, tmp_path):
        runner, store, _ = make_runner(tmp_path, happy_script())
        first = runner.run("printer-1")
        second = runner.run("printer-1")
        assert first.records_accepted == 2
        assert second.records_accepted == 0
        assert second.records_duplicate == 2
        assert second.status == "succeeded"
        assert second.attempts_succeeded == 2

        attempts = list(store.iter_attempts("printer-1"))
        assert len(attempts) == 4  # every occurrence recorded
        reused = [a for a in attempts if a.payload_reused]
        assert len(reused) == 2
        first_records = {a.raw_record_id for a in attempts[:2]}
        second_records = {a.raw_record_id for a in attempts[2:]}
        assert first_records == second_records  # same content-addressed records
        # payload/envelope counts did not grow
        assert len(list((store.base_dir / "envelopes").glob("*.json"))) == 2

    def test_changed_measurement_is_a_new_record(self, tmp_path):
        runner, store, transport = make_runner(tmp_path, happy_script())
        runner.run("printer-1")
        transport.script["/printer/objects/query"] = fixture_response(
            "moonraker_printer_objects_changed.json"
        )
        run = runner.run("printer-1")
        assert run.records_accepted == 1  # printer_objects changed
        assert run.records_duplicate == 1  # server_info reused
        temps = set()
        for envelope in store.iter_accepted_envelopes("printer-1"):
            if envelope.api_locator.item_key != "printer_objects":
                continue
            result = store.get_extraction(envelope.record_id)
            for obs in result.manifest_view().observations:
                if obs.json_pointer.endswith("extruder/temperature"):
                    temps.add(obs.value_json)
        assert temps == {"60.1", "60.4"}


class TestPartialAndPrecedence:
    def test_endpoint_two_failure_is_acquisition_failure_status(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportError

        script = happy_script()
        script["/printer/objects/query"] = TransportError("timeout", "deadline")
        runner, store, _ = make_runner(tmp_path, script)
        run = runner.run("printer-1")
        assert run.status == "completed_with_acquisition_failures"
        assert (run.attempts_succeeded, run.attempts_failed) == (1, 1)
        assert run.records_accepted == 1  # endpoint one persisted + extracted
        assert run.records_quarantined == 0
        failed = [a for a in store.iter_attempts("printer-1")
                  if a.outcome == "failed"]
        assert failed[0].received_at is None  # never fabricated
        assert failed[0].failure.error_code == "ACQUIRE_TIMEOUT"
        assert runner.health("printer-1").status == "degraded"

    def test_quarantine_outranks_acquisition_failure(self, tmp_path):
        from backend.data_sources.connectors.http_api import (
            TransportError, TransportResponse,
        )

        script = {
            "/server/info": TransportError("connection", "unreachable"),
            "/printer/objects/query": TransportResponse(
                status=200, headers={"Content-Type": "application/json"},
                body=(FIXTURES / "moonraker_dup_key.json").read_bytes(),
            ),
        }
        runner, store, _ = make_runner(tmp_path, script)
        run = runner.run("printer-1")
        assert run.status == "completed_with_quarantine"  # precedence rule 2
        assert run.attempts_failed == 1  # still exposed by the counters
        assert run.records_quarantined == 1
        [q_path] = (store.base_dir / "quarantine").glob("*.json")
        assert store.get_quarantine(q_path.stem).error_code == (
            "EXTRACT_API_MALFORMED_JSON"
        )

    def test_rate_limit_evidence_reaches_health(self, tmp_path):
        from backend.data_sources.connectors.http_api import TransportResponse

        script = happy_script()
        script["/server/info"] = TransportResponse(
            status=429, headers={"Retry-After": "30"}, body=b"")
        runner, store, _ = make_runner(tmp_path, script)
        run = runner.run("printer-1")
        assert run.status == "completed_with_acquisition_failures"
        # order attempts by sweep to find the last one deterministically
        evidence = runner.health("printer-1").api_evidence
        assert evidence.last_status_code in (200, 429)
        rate_limited = [a for a in store.iter_attempts("printer-1")
                        if a.failure and a.failure.error_code == "ACQUIRE_RATE_LIMITED"]
        assert rate_limited[0].allowlisted_headers["Retry-After"] == "30"


class TestSecretsAndReplay:
    def test_auth_token_never_persisted(self, tmp_path):
        script = happy_script()
        runner, store, transport = make_runner(
            tmp_path, script,
            credential_values={"moonraker-key": "hunter2-api-token"},
            credential="moonraker-key",
        )
        runner.run("printer-1")
        assert transport.requests[0].headers["X-Api-Key"] == "hunter2-api-token"
        for path in store.base_dir.rglob("*"):
            if path.is_file():
                assert b"hunter2-api-token" not in path.read_bytes(), path

    def test_replay_offline_after_service_shutdown(self, tmp_path):
        runner, store, transport = make_runner(tmp_path, happy_script())
        runner.run("printer-1")
        stored = {
            e.record_id: store.get_extraction(e.record_id)
            for e in store.iter_accepted_envelopes("printer-1")
        }
        transport.script.clear()  # the service is gone
        replayed = runner.replay("printer-1")
        assert len(replayed) == 2
        for product in replayed:
            assert product.result == stored[product.result.raw_record_id]


class TestCommitOrderRecovery:
    def test_crash_before_attempt_commit_is_detectable_and_recoverable(
        self, tmp_path, monkeypatch
    ):
        runner, store, _ = make_runner(tmp_path, happy_script())
        original = store.put_attempt
        monkeypatch.setattr(
            store, "put_attempt",
            lambda attempt: (_ for _ in ()).throw(RuntimeError("simulated crash")),
        )
        with pytest.raises(RuntimeError):
            runner.run("printer-1")
        audit = store.find_uncommitted_api_artifacts()
        assert audit["uncommitted_api_envelopes"]  # detectable, not evidence

        monkeypatch.setattr(store, "put_attempt", original)
        run = runner.run("printer-1")
        assert run.status == "succeeded"
        assert run.records_duplicate >= 1  # crashed envelope resolved by reuse
        assert store.find_uncommitted_api_artifacts() == {
            "uncommitted_api_envelopes": [], "unreferenced_payloads": []}

    def test_record_and_observation_ids_deterministic_across_stores(self, tmp_path):
        runner_a, store_a, _ = make_runner(tmp_path / "a", happy_script())
        runner_b, store_b, _ = make_runner(tmp_path / "b", happy_script())
        runner_a.run("printer-1")
        runner_b.run("printer-1")
        ids_a = sorted(e.record_id for e in store_a.iter_accepted_envelopes("printer-1"))
        ids_b = sorted(e.record_id for e in store_b.iter_accepted_envelopes("printer-1"))
        assert ids_a == ids_b
        for record_id in ids_a:
            assert (store_a.get_extraction(record_id).model_dump_json()
                    == store_b.get_extraction(record_id).model_dump_json())


class TestProfileV2:
    def test_v2_all_required_families_validated(self):
        from backend.data_sources.catalog import APPLICATION_PROFILE_V2

        entries = {e.source_family: e for e in APPLICATION_PROFILE_V2.entries}
        for family in ("csv_bom", "step_assembly", "pdf_drawing_manual",
                       "operational_api_or_telemetry"):
            assert entries[family].requirement == "required"
            assert entries[family].roadmap_stage == "validated"
            assert entries[family].enabled_for_profile is True

    def test_v2_admits_api_sources(self, tmp_path):
        from backend.data_sources.catalog import APPLICATION_PROFILE_V2

        runner, store, _ = make_runner(tmp_path, happy_script())
        runner.profile = APPLICATION_PROFILE_V2
        assert runner.run("printer-1").status == "succeeded"
