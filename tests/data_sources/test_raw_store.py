"""Tests for the write-once filesystem raw store."""

from datetime import UTC, datetime

import pytest

from backend.data_sources.contracts import (
    ExtractedTable,
    IngestionRun,
    QuarantineRecord,
    RawRecord,
    StoreIntegrityError,
)
from backend.data_sources.provenance import derive_record_id, payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore

UTC_NOW = datetime(2026, 8, 6, 12, 0, 0, tzinfo=UTC)
PAYLOAD = b"item_no,name\n100-001,Frame\n"


@pytest.fixture
def store(tmp_path):
    return FilesystemRawStore(tmp_path / "raw_store")


def make_record(payload: bytes = PAYLOAD, source_id: str = "bom-local", **overrides):
    checksum = payload_checksum(payload)
    base = dict(
        record_id=derive_record_id(source_id, checksum, 0),
        source_id=source_id,
        source_native_id="fixtures/bom_valid.csv",
        ingestion_run_id="run-1",
        captured_at=UTC_NOW,
        source_observed_at=UTC_NOW,
        content_type="text/csv",
        payload_checksum=checksum,
        immutable_payload_reference=checksum,
        provenance={"acquisition_mode": "snapshot"},
        quality_flags=[],
    )
    base.update(overrides)
    return RawRecord(**base)


class TestPayloads:
    def test_put_and_get_round_trip(self, store):
        reference = store.put_payload(PAYLOAD)
        assert reference == payload_checksum(PAYLOAD)
        assert store.get_payload(reference) == PAYLOAD

    def test_identical_payload_is_idempotent(self, store):
        assert store.put_payload(PAYLOAD) == store.put_payload(PAYLOAD)

    def test_get_verifies_checksum_on_read(self, store, tmp_path):
        reference = store.put_payload(PAYLOAD)
        payload_file = next((tmp_path / "raw_store" / "payloads").iterdir())
        payload_file.chmod(0o644)
        payload_file.write_bytes(b"tampered")
        with pytest.raises(StoreIntegrityError):
            store.get_payload(reference)

    def test_unknown_reference_raises(self, store):
        with pytest.raises(StoreIntegrityError):
            store.get_payload(payload_checksum(b"never stored"))


class TestEnvelopes:
    def test_put_envelope_returns_true_then_detects_duplicate(self, store):
        record = make_record()
        assert store.put_envelope(record) is True
        assert store.put_envelope(record) is False  # identical re-put = duplicate

    def test_conflicting_envelope_same_id_raises(self, store):
        record = make_record()
        store.put_envelope(record)
        conflicting = make_record(ingestion_run_id="run-2")
        with pytest.raises(StoreIntegrityError):
            store.put_envelope(conflicting)

    def test_iter_accepted_envelopes_filters_by_source(self, store):
        first = make_record()
        other_payload = b"item_no,name\n200-002,Bolt\n"
        other = make_record(payload=other_payload, source_id="other-source")
        store.put_envelope(first)
        store.put_envelope(other)
        found = list(store.iter_accepted_envelopes("bom-local"))
        assert found == [first]


class TestRunsQuarantineExtracted:
    def test_run_report_round_trip(self, store):
        run = IngestionRun(
            run_id="run-1",
            source_id="bom-local",
            started_at=UTC_NOW,
            finished_at=UTC_NOW,
            status="succeeded",
            records_seen=1,
            records_accepted=1,
            records_duplicate=0,
            records_quarantined=0,
            error_summary=None,
        )
        store.put_run(run)
        assert store.get_run("run-1") == run
        with pytest.raises(StoreIntegrityError):
            store.put_run(run.model_copy(update={"records_seen": 2}))

    def test_quarantine_round_trip(self, store):
        record = make_record()
        q = QuarantineRecord(
            record_id=record.record_id,
            stage="extraction",
            error_code="EXTRACT_UNDECODABLE",
            redacted_message="payload is not decodable as utf-8",
            quarantined_at=UTC_NOW,
        )
        store.put_quarantine(q)
        assert store.get_quarantine(record.record_id) == q

    def test_extraction_envelope_round_trip(self, store):
        from backend.data_sources.contracts import ExtractionResult, ExtractorIdentity

        record = make_record()
        table = ExtractedTable(
            raw_record_id=record.record_id,
            header_row_index=0,
            columns=["item_no", "name"],
            rows=[],
            warnings=[],
        )
        result = ExtractionResult(
            schema_version=1,
            raw_record_id=record.record_id,
            extractor=ExtractorIdentity(
                name="csv_extractor", version="1.1.0",
                toolchain="python-stdlib-csv", config_fingerprint="test",
            ),
            outcome="succeeded",
            warnings=[],
            result={"kind": "csv_table", "table": table},
        )
        store.put_extraction(result)
        assert store.get_extraction(record.record_id) == result

    def test_quarantined_records_are_excluded_from_accepted(self, store):
        record = make_record()
        store.put_envelope(record)
        store.put_quarantine(
            QuarantineRecord(
                record_id=record.record_id,
                stage="extraction",
                error_code="EXTRACT_UNDECODABLE",
                redacted_message="payload is not decodable as utf-8",
                quarantined_at=UTC_NOW,
            )
        )
        assert list(store.iter_accepted_envelopes("bom-local")) == []
