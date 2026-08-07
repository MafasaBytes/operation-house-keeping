"""DS-004 contract tests: source-time markers, acquisition attempts,
locators, observations, health evidence, run accounting, canonical JSON
serialization, and RFC 6901 escaping."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    AcquisitionAttempt,
    ApiExtractionManifest,
    ApiHealthEvidence,
    ApiObservationsResult,
    ApiSourceLocator,
    ExtractionResult,
    ExtractorIdentity,
    IngestionRun,
    OperationalObservation,
    SourceHealth,
    resolve_completed_run_status,
)
from backend.data_sources.extractors.operational import (
    canonical_json,
    escape_pointer_token,
    json_pointer_of,
    json_type_of,
)
from backend.data_sources.provenance import derive_keyed_record_id

UTC_NOW = datetime(2026, 8, 7, 18, 0, 0, tzinfo=UTC)
RID = "a" * 32
FPRINT = "sha256:" + "ab" * 32

IDENTITY = ExtractorIdentity(
    name="moonraker_extractor", version="1.0.0",
    toolchain="python-stdlib-json", config_fingerprint="cafe" * 4,
)

MONO = {
    "kind": "monotonic", "value": "3721.845", "unit": "seconds",
    "clock_id": "klipper_host_monotonic", "origin": "unknown",
    "pointer": "/result/eventtime",
}


def make_attempt(**overrides) -> AcquisitionAttempt:
    base = dict(
        attempt_id="b" * 32,
        ingestion_run_id="run-1",
        source_id="printer-1",
        item_key="printer_objects",
        adapter_id="moonraker",
        endpoint_id="printer_objects_query",
        sweep_position=1,
        started_at=UTC_NOW,
        finished_at=UTC_NOW,
        received_at=UTC_NOW,
        outcome="succeeded",
        request_fingerprint=FPRINT,
        request_canonical="GET /printer/objects/query?extruder=target,temperature",
        target_origin="http://127.0.0.1:7125",
        status_code=200,
        allowlisted_headers={"Content-Type": "application/json"},
        transport_security="plaintext_http_explicit",
        response_size_bytes=512,
        retries_used=0,
        payload_checksum="sha256:" + "cd" * 32,
        raw_record_id=RID,
        payload_reused=False,
        failure=None,
    )
    base.update(overrides)
    return AcquisitionAttempt(**base)


def make_observation(**overrides) -> OperationalObservation:
    base = dict(
        observation_id="c" * 32,
        raw_record_id=RID,
        json_pointer="/result/status/extruder/temperature",
        subject_identifier="extruder",
        value_json="60.1",
        json_type="number",
        declared_unit=None,
        semantics="snapshot",
        source_time=MONO,
        quality_flags=["unit_not_declared"],
    )
    base.update(overrides)
    return OperationalObservation(**base)


class TestSourceTimeMarker:
    def test_monotonic_keeps_exact_lexeme(self):
        obs = make_observation()
        assert obs.source_time.kind == "monotonic"
        assert obs.source_time.value == "3721.845"  # verbatim, no epoch fabrication
        assert obs.source_time.clock_id == "klipper_host_monotonic"

    def test_wall_clock_requires_aware_datetime(self):
        with pytest.raises(ValidationError):
            make_observation(source_time={
                "kind": "wall_clock",
                "value": "2026-08-07T18:00:00",  # naive
                "basis": "source_declared_epoch",
            })
        ok = make_observation(source_time={
            "kind": "wall_clock",
            "value": "2026-08-07T18:00:00Z",
            "basis": "source_declared_epoch",
        })
        assert ok.source_time.kind == "wall_clock"

    def test_unavailable_needs_reason(self):
        ok = make_observation(source_time={
            "kind": "unavailable", "reason": "endpoint provides no source time"
        })
        assert ok.source_time.reason


class TestAcquisitionAttempt:
    def test_succeeded_requires_payload_reference_and_received_at(self):
        with pytest.raises(ValidationError):
            make_attempt(payload_checksum=None, raw_record_id=None)
        with pytest.raises(ValidationError):
            make_attempt(received_at=None)

    def test_failed_requires_failure_and_forbids_payload(self):
        failed = make_attempt(
            outcome="failed", payload_checksum=None, raw_record_id=None,
            received_at=UTC_NOW, status_code=401,
            failure={"error_code": "ACQUIRE_AUTH_FAILED",
                     "redacted_message": "authentication rejected (401)"},
        )
        assert failed.failure.error_code == "ACQUIRE_AUTH_FAILED"
        with pytest.raises(ValidationError):
            make_attempt(outcome="failed", failure=None,
                         payload_checksum=None, raw_record_id=None)
        with pytest.raises(ValidationError):  # failed may not carry a payload
            make_attempt(outcome="failed",
                         failure={"error_code": "X", "redacted_message": "y"})

    def test_timeout_does_not_fabricate_received_at(self):
        timeout = make_attempt(
            outcome="failed", payload_checksum=None, raw_record_id=None,
            received_at=None, status_code=None, response_size_bytes=None,
            failure={"error_code": "ACQUIRE_TIMEOUT",
                     "redacted_message": "request deadline exceeded"},
        )
        assert timeout.received_at is None

    def test_fingerprint_must_be_full_tagged_sha256(self):
        with pytest.raises(ValidationError):
            make_attempt(request_fingerprint="sha256:" + "ab" * 8)  # truncated

    def test_byte_identical_reuse_flag(self):
        reused = make_attempt(payload_reused=True)
        assert reused.payload_reused is True


class TestApiSourceLocator:
    def test_optional_content_type_and_route(self):
        locator = ApiSourceLocator(
            adapter_id="moonraker", endpoint_id="printer_objects_query",
            item_key="printer_objects", request_fingerprint=FPRINT,
            request_canonical="GET /printer/objects/query?x=y",
            source_content_type=None,  # responses may omit it
            extraction_route="api:moonraker:v1",
        )
        assert locator.source_content_type is None
        assert locator.extraction_route == "api:moonraker:v1"


class TestHealthEvidence:
    def test_typed_fields_not_strings(self):
        evidence = ApiHealthEvidence(
            consecutive_attempt_failures=2,
            last_attempt_error_code="ACQUIRE_RATE_LIMITED",
            last_status_code=429,
            last_retry_after_seconds=30.0,
            clock_skew_seconds=-1.5,
            plaintext_http_explicit=True,
            last_successful_attempt_at=UTC_NOW,
        )
        health = SourceHealth(
            source_id="printer-1", status="degraded", checked_at=UTC_NOW,
            last_success_at=None, last_record_at=None,
            diagnostic_code="ACQUIRE_RATE_LIMITED", api_evidence=evidence,
        )
        assert health.api_evidence.last_retry_after_seconds == 30.0
        with pytest.raises(ValidationError):
            ApiHealthEvidence(
                consecutive_attempt_failures="two",  # numbers stay numbers
                last_attempt_error_code=None, last_status_code=None,
                last_retry_after_seconds=None, clock_skew_seconds=None,
                plaintext_http_explicit=False, last_successful_attempt_at=None,
            )

    def test_health_without_api_evidence_still_valid(self):
        legacy = SourceHealth(
            source_id="s", status="ok", checked_at=UTC_NOW,
            last_success_at=None, last_record_at=None, diagnostic_code=None,
        )
        assert legacy.api_evidence is None


class TestRunAccounting:
    def test_attempt_counters_default_and_old_json_valid(self):
        run = IngestionRun(
            run_id="r", source_id="s", started_at=UTC_NOW, finished_at=UTC_NOW,
            status="succeeded", records_seen=1, records_accepted=1,
            records_duplicate=0, records_quarantined=0, error_summary=None,
        )
        assert (run.attempts_planned, run.attempts_succeeded,
                run.attempts_failed) == (0, 0, 0)
        legacy = run.model_dump_json(
            exclude={"attempts_planned", "attempts_succeeded", "attempts_failed",
                     "records_partial"}
        )
        assert IngestionRun.model_validate_json(legacy).attempts_failed == 0

    def test_new_status_literal(self):
        run = IngestionRun(
            run_id="r", source_id="s", started_at=UTC_NOW, finished_at=UTC_NOW,
            status="completed_with_acquisition_failures",
            records_seen=1, records_accepted=1, records_duplicate=0,
            records_quarantined=0, attempts_planned=2, attempts_succeeded=1,
            attempts_failed=1, error_summary="ACQUIRE_TIMEOUT: 1 attempt",
        )
        assert run.attempts_failed == 1

    def test_status_precedence(self):
        # quarantine outranks acquisition failure; both outrank succeeded
        assert resolve_completed_run_status(
            records_quarantined=1, attempts_failed=1
        ) == "completed_with_quarantine"
        assert resolve_completed_run_status(
            records_quarantined=0, attempts_failed=1
        ) == "completed_with_acquisition_failures"
        assert resolve_completed_run_status(
            records_quarantined=1, attempts_failed=0
        ) == "completed_with_quarantine"
        assert resolve_completed_run_status(
            records_quarantined=0, attempts_failed=0
        ) == "succeeded"


class TestManifestUnion:
    def test_api_observations_result_round_trips(self):
        manifest = ApiExtractionManifest(
            raw_record_id=RID, extractor=IDENTITY,
            item_key="printer_objects", adapter_id="moonraker",
            observations=[make_observation()],
            levels_supported=[0, 1, 2], levels_achieved=[0, 1, 2],
            unsupported_features=[], warnings=[],
        )
        result = ExtractionResult(
            raw_record_id=RID, extractor=IDENTITY, outcome="succeeded",
            warnings=[], result=ApiObservationsResult(manifest=manifest),
        )
        restored = ExtractionResult.model_validate_json(result.model_dump_json())
        assert restored == result
        assert restored.result.kind == "api_observations"
        assert restored.manifest_view().observations[0].value_json == "60.1"


class TestCanonicalJson:
    def test_number_vs_string_distinguishable(self):
        assert canonical_json([Decimal("1.0"), Decimal("2.0")]) == "[1.0,2.0]"
        assert canonical_json(["1.0", "2.0"]) == '["1.0","2.0"]'

    def test_int_vs_non_int_preserved(self):
        assert canonical_json(7) == "7"
        assert canonical_json(Decimal("7.0")) == "7.0"

    def test_exponent_notation_stays_a_number(self):
        assert canonical_json(Decimal("1E+3")) == "1E+3"

    def test_nested_types_preserved_and_keys_sorted(self):
        value = {"b": [Decimal("0.3"), 4, "5"], "a": {"x": True, "y": None}}
        assert canonical_json(value) == '{"a":{"x":true,"y":null},"b":[0.3,4,"5"]}'

    def test_toolhead_position_survives(self):
        position = [Decimal("1.0"), Decimal("2.0"), Decimal("0.3"), Decimal("0.0")]
        assert canonical_json(position) == "[1.0,2.0,0.3,0.0]"
        assert json_type_of(position) == "array"

    def test_deterministic_across_repeat(self):
        value = {"k": [Decimal("60.1"), "60.1", 60]}
        assert canonical_json(value) == canonical_json(value)

    def test_json_type_of(self):
        assert json_type_of("x") == "string"
        assert json_type_of(Decimal("1.5")) == "number"
        assert json_type_of(3) == "number"
        assert json_type_of(True) == "boolean"
        assert json_type_of(None) == "null"
        assert json_type_of({}) == "object"


class TestPointerEscaping:
    def test_rfc6901_escapes(self):
        assert escape_pointer_token("fan~1") == "fan~01"
        assert escape_pointer_token("probe/z") == "probe~1z"
        assert escape_pointer_token("a~/b") == "a~0~1b"
        assert escape_pointer_token("plain name") == "plain name"

    def test_pointer_of(self):
        assert json_pointer_of("result", "status", "probe/z", "value~") == (
            "/result/status/probe~1z/value~0"
        )


class TestKeyedRecordId:
    def test_deterministic_and_sensitive(self):
        checksum = "sha256:" + "cd" * 32
        a = derive_keyed_record_id("printer-1", "printer_objects", checksum)
        assert a == derive_keyed_record_id("printer-1", "printer_objects", checksum)
        assert len(a) == 32 and all(c in "0123456789abcdef" for c in a)
        assert a != derive_keyed_record_id("printer-2", "printer_objects", checksum)
        assert a != derive_keyed_record_id("printer-1", "server_info", checksum)
        assert a != derive_keyed_record_id(
            "printer-1", "printer_objects", "sha256:" + "ef" * 32
        )
