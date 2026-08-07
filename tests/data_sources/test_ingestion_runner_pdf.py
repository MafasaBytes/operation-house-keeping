"""End-to-end DS-003 runtime tests: PDF through the full source boundary."""

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from backend.data_sources.catalog import (
    APPLICATION_PROFILE_V1,
    InMemorySourceCatalog,
)
from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import SourceDefinition
from backend.data_sources.raw_store import FilesystemRawStore
from backend.data_sources.runtime import IngestionRunner

FIXTURES = Path("backend/data_sources/testing/fixtures")


class FakeClock:
    def __init__(self) -> None:
        self._now = datetime(2026, 8, 7, 15, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self._now += timedelta(seconds=1)
        return self._now


def make_source(source_id: str, path: Path, content_type: str = "application/pdf"):
    return SourceDefinition(
        source_id=source_id,
        display_name=source_id,
        source_kind="document",
        connector_type="local_file",
        configuration={"path": str(path)},
        credential_reference=None,
        declared_content_types=[content_type],
        enabled=True,
    )


@pytest.fixture
def env(tmp_path):
    for name in ("manual_multipage.pdf", "scanned_only.pdf", "encrypted.pdf",
                 "malformed.pdf"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    (tmp_path / "not_a_pdf.pdf").write_bytes(b"item_no,name\n1,Frame\n")

    catalog = InMemorySourceCatalog()
    catalog.register(make_source("pdf-manual", tmp_path / "manual_multipage.pdf"))
    catalog.register(make_source("pdf-scanned", tmp_path / "scanned_only.pdf"))
    catalog.register(make_source("pdf-encrypted", tmp_path / "encrypted.pdf"))
    catalog.register(make_source("pdf-malformed", tmp_path / "malformed.pdf"))
    catalog.register(make_source("pdf-masquerade", tmp_path / "not_a_pdf.pdf"))

    store = FilesystemRawStore(tmp_path / "raw_store")
    runner = IngestionRunner(
        catalog=catalog,
        store=store,
        connectors={"local_file": LocalFileConnector()},
        clock=FakeClock(),
        scratch_root=tmp_path / "scratch",
        profile=APPLICATION_PROFILE_V1,
    )
    return runner, store, tmp_path


@pytest.mark.pdf
class TestPdfEndToEnd:
    def test_ingest_persists_manifest_and_page_renders(self, env):
        runner, store, _ = env
        run = runner.run("pdf-manual")
        assert run.status == "succeeded"
        assert (run.records_seen, run.records_accepted) == (1, 1)
        assert (run.records_partial, run.records_quarantined) == (0, 0)

        [envelope] = store.iter_accepted_envelopes("pdf-manual")
        result = store.get_extraction(envelope.record_id)
        manifest = result.manifest_view()
        assert manifest.levels_achieved == [0, 1, 2, 3]
        assert len(manifest.derivatives) == 3
        for derivative in manifest.derivatives:
            png = store.get_derivative_payload(derivative.payload_reference)
            assert png[:8] == b"\x89PNG\r\n\x1a\n"
        assert store.find_orphan_derivatives() == []

    def test_scanned_pdf_is_partial(self, env):
        runner, store, _ = env
        run = runner.run("pdf-scanned")
        assert run.status == "succeeded"
        assert run.records_partial == 1
        [envelope] = store.iter_accepted_envelopes("pdf-scanned")
        result = store.get_extraction(envelope.record_id)
        assert result.outcome == "partial"
        [outcome] = result.manifest_view().page_outcomes
        assert outcome.ocr_required is True

    def test_encrypted_and_malformed_quarantine(self, env):
        runner, store, _ = env
        run_enc = runner.run("pdf-encrypted")
        assert run_enc.status == "completed_with_quarantine"
        run_mal = runner.run("pdf-malformed")
        assert run_mal.status == "completed_with_quarantine"
        codes = sorted(
            store.get_quarantine(p.stem).error_code
            for p in (store.base_dir / "quarantine").glob("*.json")
        )
        assert codes == [
            "EXTRACT_PDF_PARSE_FAILED",
            "EXTRACT_PDF_PASSWORD_REQUIRED",
        ]

    def test_rerun_duplicate_and_replay_after_delete(self, env):
        runner, store, tmp_path = env
        runner.run("pdf-manual")
        second = runner.run("pdf-manual")
        assert second.records_duplicate == 1

        [envelope] = store.iter_accepted_envelopes("pdf-manual")
        stored = store.get_extraction(envelope.record_id)
        (tmp_path / "manual_multipage.pdf").unlink()
        [replayed] = runner.replay("pdf-manual")
        assert replayed.result == stored


class TestDetectionWithoutWorker:
    def test_non_pdf_bytes_quarantined_at_format_detection(self, env):
        runner, store, _ = env
        run = runner.run("pdf-masquerade")
        assert run.status == "completed_with_quarantine"
        [q_path] = (store.base_dir / "quarantine").glob("*.json")
        quarantine = store.get_quarantine(q_path.stem)
        assert quarantine.stage == "format_detection"
        assert quarantine.error_code == "EXTRACT_UNSUPPORTED_OR_UNKNOWN_FORMAT"


class TestProfileV1:
    def test_v1_contents(self):
        entries = {e.source_family: e for e in APPLICATION_PROFILE_V1.entries}
        assert entries["csv_bom"].roadmap_stage == "validated"
        assert entries["step_assembly"].roadmap_stage == "validated"
        assert entries["pdf_drawing_manual"].roadmap_stage == "validated"
        assert entries["pdf_drawing_manual"].enabled_for_profile is True
        assert entries["operational_api_or_telemetry"].roadmap_stage == "later"

    def test_disabled_family_still_rejected(self, env, tmp_path):
        runner, _, _ = env
        db_path = tmp_path / "dump.sql"
        db_path.write_bytes(b"SELECT 1;")
        runner.catalog.register(
            make_source("sql-early", db_path, content_type="application/sql")
        )
        run = runner.run("sql-early")
        assert run.status == "failed"
        assert "ACQUIRE_NOT_IN_PROFILE" in (run.error_summary or "")


class TestCheckpointQuarantineThroughRunner:
    def test_invalid_phase_a_manifest_is_quarantined(self, env, monkeypatch):
        from backend.data_sources.extractors.worker_harness import WorkerOutcome
        import hashlib as _hashlib
        import json as _json
        from backend.data_sources.extractors.pdf.pdf_extractor import (
            PdfExtractionConfig as _Cfg, pdf_extractor_identity,
        )

        runner, store, _ = env
        manifest_bytes = b'{"totally": "wrong shape"}'
        checkpoint = {
            "checkpoint_schema_version": 1,
            # matched dynamically below via a record-id-agnostic stub: the
            # parent checks the checkpoint rid first, so mirror it lazily.
        }

        def stub(build_argv, payload, expected_checksum, limits, **kwargs):
            # Recover the raw_record_id the parent passed to the worker via
            # the argv context (last argument).
            argv = build_argv(__import__("pathlib").Path("in"),
                              __import__("pathlib").Path("out"))
            context = _json.loads(argv[-1])
            cp = {
                "checkpoint_schema_version": 1,
                "raw_record_id": context["raw_record_id"],
                "extractor": pdf_extractor_identity(_Cfg(), {}).model_dump(),
                "manifest_sha256": _hashlib.sha256(manifest_bytes).hexdigest(),
                "state": "phase_a_complete",
            }
            return WorkerOutcome(
                status="ok", returncode=0, stdout_tail="", stderr_tail="",
                outputs={
                    "phase_a_status.json": _json.dumps(
                        {"status": "ok", "error": None}).encode(),
                    "manifest_a.json": manifest_bytes,
                    "checkpoint.json": _json.dumps(cp).encode(),
                },
            )

        monkeypatch.setattr(
            "backend.data_sources.extractors.pdf.pdf_extractor.invoke_worker", stub
        )
        run = runner.run("pdf-manual")
        assert run.status == "completed_with_quarantine"
        assert run.records_accepted == 1  # raw payload preserved
        [q_path] = (store.base_dir / "quarantine").glob("*.json")
        quarantine = store.get_quarantine(q_path.stem)
        assert quarantine.error_code == "EXTRACT_PDF_CHECKPOINT_INVALID"
        assert quarantine.stage == "extraction"
