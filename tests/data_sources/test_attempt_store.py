"""Store tests for DS-004: acquisition attempts and the uncommitted-API-
artifact integrity audit."""

from datetime import UTC, datetime

import pytest

from backend.data_sources.contracts import (
    AcquisitionAttempt,
    ApiSourceLocator,
    RawRecord,
    StoreIntegrityError,
)
from backend.data_sources.provenance import derive_keyed_record_id, payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore

UTC_NOW = datetime(2026, 8, 7, 18, 0, 0, tzinfo=UTC)
FPRINT = "sha256:" + "ab" * 32
PAYLOAD = b'{"result": {"eventtime": 1.5, "status": {}}}'


@pytest.fixture
def store(tmp_path):
    return FilesystemRawStore(tmp_path / "raw_store")


def make_locator() -> ApiSourceLocator:
    return ApiSourceLocator(
        adapter_id="moonraker", endpoint_id="printer_objects_query",
        item_key="printer_objects", request_fingerprint=FPRINT,
        request_canonical="GET /printer/objects/query?extruder=target,temperature",
        source_content_type="application/json",
        extraction_route="api:moonraker:v1",
    )


def make_envelope(payload: bytes = PAYLOAD, run_id: str = "run-1") -> RawRecord:
    checksum = payload_checksum(payload)
    return RawRecord(
        record_id=derive_keyed_record_id("printer-1", "printer_objects", checksum),
        source_id="printer-1",
        source_native_id=None,
        ingestion_run_id=run_id,
        captured_at=UTC_NOW,
        source_observed_at=None,
        content_type="application/json",
        payload_checksum=checksum,
        immutable_payload_reference=checksum,
        provenance={"acquisition_mode": "poll"},
        quality_flags=[],
        api_locator=make_locator(),
    )


def make_attempt(raw_record_id: str, attempt_id: str = "b" * 32,
                 outcome: str = "succeeded", started=UTC_NOW) -> AcquisitionAttempt:
    success = outcome == "succeeded"
    return AcquisitionAttempt(
        attempt_id=attempt_id, ingestion_run_id="run-1", source_id="printer-1",
        item_key="printer_objects", adapter_id="moonraker",
        endpoint_id="printer_objects_query", sweep_position=1,
        started_at=started, finished_at=started,
        received_at=started if success else None,
        outcome=outcome, request_fingerprint=FPRINT,
        request_canonical="GET /printer/objects/query?extruder=target,temperature",
        target_origin="http://127.0.0.1:7125", status_code=200 if success else None,
        allowlisted_headers={}, transport_security="plaintext_http_explicit",
        response_size_bytes=len(PAYLOAD) if success else None, retries_used=0,
        payload_checksum=payload_checksum(PAYLOAD) if success else None,
        raw_record_id=raw_record_id if success else None,
        payload_reused=False,
        failure=None if success else {"error_code": "ACQUIRE_TIMEOUT",
                                      "redacted_message": "deadline exceeded"},
    )


class TestAttemptPersistence:
    def test_round_trip_and_write_once(self, store):
        envelope = make_envelope()
        attempt = make_attempt(envelope.record_id)
        assert store.put_attempt(attempt) is True
        assert store.get_attempt(attempt.attempt_id) == attempt
        assert store.put_attempt(attempt) is False  # identical re-put
        with pytest.raises(StoreIntegrityError):
            store.put_attempt(attempt.model_copy(update={"retries_used": 3}))

    def test_iter_attempts_filters_and_orders(self, store):
        envelope = make_envelope()
        later = UTC_NOW.replace(minute=5)
        store.put_attempt(make_attempt(envelope.record_id, attempt_id="e" * 32,
                                       started=later))
        store.put_attempt(make_attempt(envelope.record_id, attempt_id="b" * 32))
        store.put_attempt(make_attempt(None, attempt_id="c" * 32, outcome="failed"))
        found = list(store.iter_attempts("printer-1"))
        assert [a.attempt_id for a in found] == ["b" * 32, "c" * 32, "e" * 32]
        assert list(store.iter_attempts("other-source")) == []


class TestUncommittedApiArtifactAudit:
    def test_committed_acquisition_is_clean(self, store):
        envelope = make_envelope()
        store.put_payload(PAYLOAD)
        store.put_envelope(envelope)
        store.put_attempt(make_attempt(envelope.record_id))
        audit = store.find_uncommitted_api_artifacts()
        assert audit == {"uncommitted_api_envelopes": [], "unreferenced_payloads": []}

    def test_api_envelope_without_attempt_detected(self, store):
        # crash between envelope write and attempt commit
        envelope = make_envelope()
        store.put_payload(PAYLOAD)
        store.put_envelope(envelope)
        audit = store.find_uncommitted_api_artifacts()
        assert audit["uncommitted_api_envelopes"] == [envelope.record_id]

    def test_payload_without_envelope_detected(self, store):
        # crash between payload write and envelope write
        reference = store.put_payload(b'{"orphan": true}')
        audit = store.find_uncommitted_api_artifacts()
        assert audit["unreferenced_payloads"] == [reference]

    def test_non_api_envelopes_are_not_flagged(self, store):
        # DS-001-003 records have no api_locator and no attempt requirement
        legacy = make_envelope().model_copy(update={"api_locator": None})
        store.put_payload(PAYLOAD)
        store.put_envelope(legacy)
        audit = store.find_uncommitted_api_artifacts()
        assert audit["uncommitted_api_envelopes"] == []
