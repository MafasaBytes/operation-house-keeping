"""Detector PDF branch + dependency-aware connector availability."""

import pytest

from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import SourceDefinition
from backend.data_sources.extractors import detect_format
from backend.data_sources.extractors.dependencies import (
    check_extraction_dependencies,
)
from backend.data_sources.raw_store import FilesystemRawStore

PDF_HEAD = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"


class TestPdfDetection:
    def test_pdf_confirmed(self):
        result = detect_format(PDF_HEAD, declared_content_type="application/pdf")
        assert result.status == "confirmed_pdf"

    def test_signature_may_follow_a_preamble_within_1024_bytes(self):
        payload = b"\xef\xbb\xbf junk preamble " + b"x" * 100 + b"%PDF-1.7\n..."
        result = detect_format(payload, declared_content_type="application/pdf")
        assert result.status == "confirmed_pdf"

    def test_signature_beyond_1024_bytes_is_not_confirmed(self):
        payload = b"x" * 1030 + b"%PDF-1.7\n"
        result = detect_format(payload, declared_content_type="application/pdf")
        assert result.status == "unsupported_or_unknown_format"

    def test_csv_bytes_declared_as_pdf_are_unknown(self):
        result = detect_format(b"a,b\n1,2\n", declared_content_type="application/pdf")
        assert result.status == "unsupported_or_unknown_format"

    def test_step_detection_unaffected(self):
        result = detect_format(
            b"ISO-10303-21;\nHEADER;", declared_content_type="model/step"
        )
        assert result.status == "confirmed_step"


class TestDependencyAwareAvailability:
    def make_source(self, content_type: str, path) -> SourceDefinition:
        return SourceDefinition(
            source_id="s1",
            display_name="s1",
            source_kind="document",
            connector_type="local_file",
            configuration={"path": str(path)},
            credential_reference=None,
            declared_content_types=[content_type],
            enabled=True,
        )

    @pytest.mark.pdf
    def test_pdf_dependencies_checked_and_reported(self, tmp_path):
        passed, evidence = check_extraction_dependencies("application/pdf")
        assert passed is True  # the pdf marker guarantees the closure
        assert "pdfplumber" in evidence

    def test_missing_dependency_fails_available_rung(self, tmp_path, monkeypatch):
        monkeypatch.setitem(
            __import__(
                "backend.data_sources.extractors.dependencies",
                fromlist=["EXTRACTION_DEPENDENCIES"],
            ).EXTRACTION_DEPENDENCIES,
            "application/x-fake",
            ("definitely_not_installed_module",),
        )
        passed, evidence = check_extraction_dependencies("application/x-fake")
        assert passed is False
        assert "definitely_not_installed_module" in evidence

        source_path = tmp_path / "f.bin"
        source_path.write_bytes(b"data")
        source = self.make_source("application/x-fake", source_path)
        store = FilesystemRawStore(tmp_path / "raw_store")
        report = LocalFileConnector().status_report(source, store)
        assert report.available.passed is False

    def test_content_type_without_extraction_deps_is_available(self, tmp_path):
        source_path = tmp_path / "f.csv"
        source_path.write_bytes(b"a,b\n")
        source = self.make_source("text/csv", source_path)
        store = FilesystemRawStore(tmp_path / "raw_store")
        report = LocalFileConnector().status_report(source, store)
        assert report.available.passed is True
