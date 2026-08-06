"""Contract tests for the data_sources Pydantic models and typed errors."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    ConnectorManifest,
    ConnectorStatusReport,
    DataSourceError,
    ExtractedCell,
    ExtractedRow,
    ExtractedTable,
    IngestionRun,
    QuarantineRecord,
    RawRecord,
    SourceDefinition,
    SourceHealth,
    StatusCheck,
)

UTC_NOW = datetime(2026, 8, 6, 12, 0, 0, tzinfo=UTC)
CHECKSUM = "sha256:" + "ab" * 32


def make_source(**overrides) -> SourceDefinition:
    base = dict(
        source_id="bom-local",
        display_name="Local BOM CSV",
        source_kind="tabular_file",
        connector_type="local_file",
        configuration={"path": "backend/data_sources/testing/fixtures/bom_valid.csv"},
        credential_reference=None,
        declared_content_types=["text/csv"],
        enabled=True,
    )
    base.update(overrides)
    return SourceDefinition(**base)


def make_raw_record(**overrides) -> RawRecord:
    base = dict(
        record_id="a" * 32,
        source_id="bom-local",
        source_native_id="fixtures/bom_valid.csv",
        ingestion_run_id="run-1",
        captured_at=UTC_NOW,
        source_observed_at=UTC_NOW,
        content_type="text/csv",
        payload_checksum=CHECKSUM,
        immutable_payload_reference=CHECKSUM,
        provenance={"acquisition_mode": "snapshot", "observed_at_meaning": "file_mtime"},
        quality_flags=[],
    )
    base.update(overrides)
    return RawRecord(**base)


class TestSourceDefinition:
    def test_valid_definition_round_trips_json(self):
        source = make_source()
        restored = SourceDefinition.model_validate_json(source.model_dump_json())
        assert restored == source

    def test_secret_looking_configuration_keys_are_rejected(self):
        for key in ("password", "token", "secret", "api_key", "DB_PASSWORD"):
            with pytest.raises(ValidationError):
                make_source(configuration={"path": "x.csv", key: "hunter2"})

    def test_credential_reference_is_a_name_not_a_mapping(self):
        source = make_source(credential_reference="vault:bom-reader")
        assert source.credential_reference == "vault:bom-reader"
        with pytest.raises(ValidationError):
            make_source(credential_reference={"user": "u", "password": "p"})


class TestConnectorManifest:
    def make(self, **overrides) -> ConnectorManifest:
        base = dict(
            connector_type="local_file",
            source_families=["tabular_file"],
            supported_formats_or_protocols=["text/csv"],
            acquisition_modes=["snapshot"],
            supported_extraction_levels=[0, 1],
            read_only=True,
            incremental_read_support=False,
            required_dependencies=[],
            maturity="experimental",
            known_limitations=["single local file per source"],
        )
        base.update(overrides)
        return ConnectorManifest(**base)

    def test_maturity_literals_enforced(self):
        assert self.make(maturity="planned").maturity == "planned"
        with pytest.raises(ValidationError):
            self.make(maturity="production_ready")

    def test_acquisition_mode_literals_enforced(self):
        with pytest.raises(ValidationError):
            self.make(acquisition_modes=["telepathy"])


class TestConnectorStatusReport:
    def test_validated_requires_evidence(self):
        ok = StatusCheck(passed=True, evidence="probe read 120 bytes")
        with pytest.raises(ValidationError):
            ConnectorStatusReport(
                connector_type="local_file",
                source_id="bom-local",
                declared=ok,
                available=ok,
                configured=ok,
                connected=ok,
                validated=StatusCheck(passed=True, evidence=""),
            )

    def test_failed_check_needs_no_evidence(self):
        report = ConnectorStatusReport(
            connector_type="local_file",
            source_id="bom-local",
            declared=StatusCheck(passed=True, evidence="in catalog"),
            available=StatusCheck(passed=True, evidence="importable"),
            configured=StatusCheck(passed=True, evidence="path set"),
            connected=StatusCheck(passed=False, evidence=""),
            validated=StatusCheck(passed=False, evidence=""),
        )
        assert report.connected.passed is False


class TestRawRecord:
    def test_frozen(self):
        record = make_raw_record()
        with pytest.raises(ValidationError):
            record.payload_checksum = "sha256:" + "00" * 32

    def test_checksum_format_enforced(self):
        with pytest.raises(ValidationError):
            make_raw_record(payload_checksum="md5:abc")
        with pytest.raises(ValidationError):
            make_raw_record(payload_checksum="sha256:zz")

    def test_timestamps_must_be_timezone_aware(self):
        with pytest.raises(ValidationError):
            make_raw_record(captured_at=datetime(2026, 8, 6, 12, 0, 0))

    def test_json_round_trip(self):
        record = make_raw_record()
        assert RawRecord.model_validate_json(record.model_dump_json()) == record


class TestIngestionRun:
    def test_status_literals(self):
        run = IngestionRun(
            run_id="run-1",
            source_id="bom-local",
            started_at=UTC_NOW,
            finished_at=UTC_NOW,
            status="completed_with_quarantine",
            records_seen=1,
            records_accepted=0,
            records_duplicate=0,
            records_quarantined=1,
            error_summary="EXTRACT_UNDECODABLE: 1 record",
        )
        assert run.records_quarantined == 1
        with pytest.raises(ValidationError):
            IngestionRun(
                run_id="run-2",
                source_id="bom-local",
                started_at=UTC_NOW,
                finished_at=UTC_NOW,
                status="partially_ok",
                records_seen=0,
                records_accepted=0,
                records_duplicate=0,
                records_quarantined=0,
                error_summary=None,
            )

    def test_counts_may_not_be_negative(self):
        with pytest.raises(ValidationError):
            IngestionRun(
                run_id="run-3",
                source_id="bom-local",
                started_at=UTC_NOW,
                finished_at=UTC_NOW,
                status="succeeded",
                records_seen=-1,
                records_accepted=0,
                records_duplicate=0,
                records_quarantined=0,
                error_summary=None,
            )


class TestSourceHealth:
    def test_unknown_health_allows_missing_timestamps(self):
        health = SourceHealth(
            source_id="bom-local",
            status="unknown",
            checked_at=UTC_NOW,
            last_success_at=None,
            last_record_at=None,
            diagnostic_code=None,
        )
        assert health.status == "unknown"


class TestQuarantineRecord:
    def test_absolute_paths_rejected_in_message(self):
        with pytest.raises(ValidationError):
            QuarantineRecord(
                record_id="a" * 32,
                stage="extraction",
                error_code="EXTRACT_UNDECODABLE",
                redacted_message="failed reading /mnt/d/secret/place.csv",
                quarantined_at=UTC_NOW,
            )

    def test_valid_quarantine(self):
        q = QuarantineRecord(
            record_id="a" * 32,
            stage="extraction",
            error_code="EXTRACT_UNDECODABLE",
            redacted_message="payload of source bom-local is not decodable as utf-8",
            quarantined_at=UTC_NOW,
        )
        assert q.stage == "extraction"


class TestExtractedTable:
    def test_cells_carry_full_provenance_and_string_values(self):
        cell = ExtractedCell(
            raw_record_id="a" * 32,
            physical_row_index=1,
            column_index=0,
            column_name="item_no",
            value="100-001",
        )
        row = ExtractedRow(physical_row_index=1, cells=[cell])
        table = ExtractedTable(
            raw_record_id="a" * 32,
            header_row_index=0,
            columns=["item_no"],
            rows=[row],
            warnings=[],
        )
        assert table.rows[0].cells[0].value == "100-001"
        with pytest.raises(ValidationError):
            ExtractedCell(
                raw_record_id="a" * 32,
                physical_row_index=1,
                column_index=0,
                column_name="qty",
                value=4,  # ints must not sneak in: extraction does not coerce types
            )

    def test_json_round_trip(self):
        table = ExtractedTable(
            raw_record_id="a" * 32,
            header_row_index=0,
            columns=["item_no"],
            rows=[],
            warnings=["ragged row at physical row 3: expected 5 fields, found 4"],
        )
        assert ExtractedTable.model_validate_json(table.model_dump_json()) == table


class TestErrors:
    def test_typed_errors_carry_codes(self):
        from backend.data_sources.contracts import (
            AcquisitionError,
            ExtractionError,
            StoreIntegrityError,
        )

        for cls, code in (
            (AcquisitionError, "ACQUIRE_FAILED"),
            (ExtractionError, "EXTRACT_UNDECODABLE"),
            (StoreIntegrityError, "STORE_CONFLICT"),
        ):
            err = cls(code, "redacted detail")
            assert isinstance(err, DataSourceError)
            assert err.error_code == code
            assert "redacted detail" in str(err)
