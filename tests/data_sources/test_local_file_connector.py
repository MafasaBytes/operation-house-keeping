"""Tests for the read-only local file connector and its honest status ladder."""

from datetime import UTC, datetime

import pytest

from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import AcquisitionError, SourceDefinition
from backend.data_sources.raw_store import FilesystemRawStore


@pytest.fixture
def source_file(tmp_path):
    path = tmp_path / "data" / "bom.csv"
    path.parent.mkdir()
    path.write_bytes(b"item_no,name\n100-001,Frame\n")
    return path


def make_source(path, source_id="bom-local") -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        display_name="Local BOM CSV",
        source_kind="tabular_file",
        connector_type="local_file",
        configuration={"path": str(path)},
        credential_reference=None,
        declared_content_types=["text/csv"],
        enabled=True,
    )


class TestManifest:
    def test_manifest_is_honest_about_maturity_and_mode(self):
        manifest = LocalFileConnector.MANIFEST
        assert manifest.connector_type == "local_file"
        assert manifest.maturity == "experimental"  # nothing claims validated yet
        assert manifest.acquisition_modes == ["snapshot"]
        assert manifest.read_only is True
        assert manifest.incremental_read_support is False
        assert manifest.known_limitations  # must declare at least one


class TestProbe:
    def test_probe_passes_for_readable_file(self, source_file):
        check = LocalFileConnector().probe(make_source(source_file))
        assert check.passed is True
        assert check.evidence  # says what it verified

    def test_probe_fails_for_missing_file_without_leaking_path(self, tmp_path):
        source = make_source(tmp_path / "nope.csv")
        check = LocalFileConnector().probe(source)
        assert check.passed is False
        assert str(tmp_path) not in check.evidence


class TestAcquire:
    def test_acquire_returns_payload_and_mtime_as_observed_at(self, source_file):
        acquisition = LocalFileConnector().acquire(make_source(source_file))
        assert acquisition.payload == source_file.read_bytes()
        assert acquisition.source_native_id == "bom.csv"
        expected_mtime = datetime.fromtimestamp(source_file.stat().st_mtime, tz=UTC)
        assert acquisition.source_observed_at == expected_mtime
        assert acquisition.provenance["observed_at_meaning"] == "file_mtime"

    def test_acquire_missing_file_raises_redacted_acquisition_error(self, tmp_path):
        source = make_source(tmp_path / "nope.csv")
        with pytest.raises(AcquisitionError) as excinfo:
            LocalFileConnector().acquire(source)
        assert excinfo.value.error_code == "ACQUIRE_SOURCE_UNREADABLE"
        assert str(tmp_path) not in str(excinfo.value)

    def test_unconfigured_source_raises(self, source_file):
        source = SourceDefinition(
            source_id="bom-local",
            display_name="Local BOM CSV",
            source_kind="tabular_file",
            connector_type="local_file",
            configuration={},  # no path
            credential_reference=None,
            declared_content_types=["text/csv"],
            enabled=True,
        )
        with pytest.raises(AcquisitionError) as excinfo:
            LocalFileConnector().acquire(source)
        assert excinfo.value.error_code == "ACQUIRE_NOT_CONFIGURED"


class TestStatusReport:
    def test_ladder_before_any_run(self, source_file, tmp_path):
        store = FilesystemRawStore(tmp_path / "raw_store")
        report = LocalFileConnector().status_report(make_source(source_file), store)
        assert report.declared.passed is True
        assert report.available.passed is True
        assert report.configured.passed is True
        assert report.connected.passed is True
        assert report.validated.passed is False  # no successful run recorded yet

    def test_ladder_unconfigured_and_unconnected(self, tmp_path):
        store = FilesystemRawStore(tmp_path / "raw_store")
        source = make_source(tmp_path / "nope.csv")
        report = LocalFileConnector().status_report(source, store)
        assert report.configured.passed is True  # a path is set...
        assert report.connected.passed is False  # ...but unreachable
        assert report.validated.passed is False
