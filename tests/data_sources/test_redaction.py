"""Redaction policy tests: synthetic credentials, query tokens, and
absolute paths must never reach persisted artifacts, while non-sensitive
evidence (scheme, host, safe basename) is preserved."""

import json

import pytest

from backend.data_sources.provenance import (
    sanitize_source_text,
    sanitize_uri,
    scrub_secrets,
)

SECRETS = ("hunter2", "abc123token", "sekrit-fragment")


class TestSanitizeUri:
    def test_credentials_query_and_fragment_removed_host_kept(self):
        uri = "http://bob:hunter2@example.com:8443/private/specs/manual.pdf?token=abc123token#sekrit-fragment"
        cleaned = sanitize_uri(uri)
        for secret in ("hunter2", "abc123token", "sekrit-fragment", "bob:"):
            assert secret not in cleaned
        assert cleaned.startswith("http://example.com:8443")
        assert "manual.pdf" in cleaned  # safe basename preserved
        assert "<redacted-query>" in cleaned

    def test_plain_uri_keeps_scheme_host_basename(self):
        cleaned = sanitize_uri("https://docs.example.invalid/manuals/pump.pdf")
        assert cleaned == "https://docs.example.invalid/pump.pdf"

    def test_garbage_uri_does_not_crash(self):
        assert sanitize_uri("::::not a uri::::")  # returns something bounded


class TestScrubSecrets:
    def test_key_value_patterns(self):
        text = "failed with password=hunter2 and api_key: abc123token in config"
        cleaned = scrub_secrets(text)
        assert "hunter2" not in cleaned and "abc123token" not in cleaned
        assert "password=<redacted>" in cleaned

    def test_userinfo_in_embedded_url(self):
        cleaned = scrub_secrets("fetch ftp://svc:hunter2@files.local/x failed")
        assert "hunter2" not in cleaned


class TestSanitizeSourceText:
    def test_paths_and_secrets_removed(self):
        text = r"see C:\Users\bob\secret.docx or /home/bob/notes.txt token=abc123token"
        cleaned = sanitize_source_text(text)
        assert "C:\\Users" not in cleaned
        assert "/home/bob" not in cleaned
        assert "abc123token" not in cleaned

    def test_none_passthrough_and_bounding(self):
        assert sanitize_source_text(None) is None
        assert len(sanitize_source_text("x" * 10_000)) <= 500


class TestEnvelopeSanitization:
    """Hostile strings injected via a stubbed Phase A manifest must not
    appear anywhere in the serialized extraction envelope."""

    def test_hostile_metadata_annotations_and_names(self, monkeypatch):
        from backend.data_sources.extractors.pdf import (
            PdfExtractionConfig, extract_pdf,
        )
        from backend.data_sources.extractors.worker_harness import WorkerLimits
        from tests.data_sources.test_pdf_extractor import (
            RID, STUB_PDF, StubHarness, ok_outcome, phase_a_outputs,
            stub_manifest_a,
        )
        from backend.data_sources.extractors.pdf.pdf_extractor import (
            pdf_extractor_identity,
        )

        manifest = stub_manifest_a()
        manifest["metadata"]["declared_title"] = (
            r"Manual C:\Users\bob\secret.docx password=hunter2"
        )
        manifest["metadata"]["declared_producer"] = "/home/bob/toolchain/producer"
        manifest["catalog"]["embedded_file_names"] = [
            "/home/bob/attachments/secret-attachment.bin"
        ]
        manifest["pages"][0]["annotations"] = [{
            "subtype": "Link",
            "rect": [10.0, 10.0, 100.0, 30.0],
            "contents": "open /etc/passwd token=abc123token",
            "uri": "http://svc:hunter2@intranet.example/private/area/spec.pdf?sid=abc123token",
        }]
        identity = pdf_extractor_identity(PdfExtractionConfig(), {}).model_dump()
        outputs = phase_a_outputs(manifest, RID, identity)
        crash_b = None  # no rendering: phase B skipped for annotation-only page?
        harness = StubHarness([ok_outcome(outputs),
                               ok_outcome({"render_results.json": json.dumps(
                                   {"pages": [{"page_index": 0, "status": "render_failed",
                                               "error": "stub", "pixel_width": None,
                                               "pixel_height": None}],
                                    "component_versions": {}}).encode()})])
        monkeypatch.setattr(
            "backend.data_sources.extractors.pdf.pdf_extractor.invoke_worker",
            harness,
        )
        product = extract_pdf(
            payload=STUB_PDF, raw_record_id=RID,
            config=PdfExtractionConfig(),
            limits=WorkerLimits(timeout_seconds=10, max_payload_bytes=1_000_000),
        )
        serialized = product.result.model_dump_json()
        for forbidden in ("hunter2", "abc123token", "C:\\\\Users", "/home/bob",
                          "/etc/passwd", "svc:"):
            assert forbidden not in serialized, forbidden
        # non-sensitive evidence preserved
        assert "intranet.example" in serialized
        assert "spec.pdf" in serialized
        assert "secret-attachment.bin" in serialized

    def test_quarantine_and_run_report_scrubbed(self, tmp_path):
        from backend.data_sources.catalog import InMemorySourceCatalog
        from backend.data_sources.connectors import LocalFileConnector
        from backend.data_sources.contracts import ExtractionError, SourceDefinition
        from backend.data_sources.raw_store import FilesystemRawStore
        from backend.data_sources.runtime import IngestionRunner

        source_path = tmp_path / "data.csv"
        source_path.write_bytes(b"a,b\n1,2\n")
        catalog = InMemorySourceCatalog()
        catalog.register(SourceDefinition(
            source_id="s", display_name="s", source_kind="tabular_file",
            connector_type="local_file", configuration={"path": str(source_path)},
            declared_content_types=["text/csv"], enabled=True,
        ))
        store = FilesystemRawStore(tmp_path / "raw_store")
        runner = IngestionRunner(catalog, store, {"local_file": LocalFileConnector()})

        def hostile_extractor(payload, envelope):
            raise ExtractionError(
                "EXTRACT_PDF_PARSE_FAILED",
                "failed at /home/bob/work/x.pdf with password=hunter2 "
                "via http://svc:hunter2@files.local/y?token=abc123token",
            )

        runner.extractors["text/csv"] = hostile_extractor
        run = runner.run("s")
        [q_path] = (store.base_dir / "quarantine").glob("*.json")
        quarantine_json = q_path.read_text("utf-8")
        run_json = (store.base_dir / "runs" / f"{run.run_id}.json").read_text("utf-8")
        for forbidden in ("hunter2", "abc123token", "/home/bob"):
            assert forbidden not in quarantine_json
            assert forbidden not in run_json
