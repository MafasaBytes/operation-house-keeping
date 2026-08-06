"""End-to-end DS-002 runtime tests: STEP through the full source boundary.

cad-marked tests spawn the real OCP worker; the rest stub the extraction
layer and run without the CAD extra.
"""

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from backend.data_sources.catalog import (
    APPLICATION_PROFILE_V0,
    InMemorySourceCatalog,
)
from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import (
    SourceDefinition,
    StoreIntegrityError,
)
from backend.data_sources.provenance import payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore
from backend.data_sources.runtime import IngestionRunner

FIXTURES = Path("backend/data_sources/testing/fixtures")


class FakeClock:
    def __init__(self) -> None:
        self._now = datetime(2026, 8, 7, 9, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self._now += timedelta(seconds=1)
        return self._now


def make_source(source_id: str, path: Path, content_type: str) -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        display_name=source_id,
        source_kind="cad_file" if content_type == "model/step" else "tabular_file",
        connector_type="local_file",
        configuration={"path": str(path)},
        credential_reference=None,
        declared_content_types=[content_type],
        enabled=True,
    )


@pytest.fixture
def env(tmp_path):
    for name in ("step_assembly.step", "step_corrupted.step", "native_cad_masquerade.step"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    catalog = InMemorySourceCatalog()
    catalog.register(make_source("cad-main", tmp_path / "step_assembly.step", "model/step"))
    catalog.register(make_source("cad-corrupt", tmp_path / "step_corrupted.step", "model/step"))
    catalog.register(
        make_source("cad-masquerade", tmp_path / "native_cad_masquerade.step", "model/step")
    )
    store = FilesystemRawStore(tmp_path / "raw_store")
    runner = IngestionRunner(
        catalog=catalog,
        store=store,
        connectors={"local_file": LocalFileConnector()},
        clock=FakeClock(),
        scratch_root=tmp_path / "scratch",
    )
    return runner, store, tmp_path


@pytest.mark.cad
class TestStepEndToEnd:
    def test_ingest_persists_manifest_and_traceable_derivative(self, env):
        runner, store, _ = env
        run = runner.run("cad-main")
        assert run.status == "succeeded"
        assert (run.records_seen, run.records_accepted) == (1, 1)
        assert (run.records_partial, run.records_quarantined) == (0, 0)

        [envelope] = store.iter_accepted_envelopes("cad-main")
        result = store.get_extraction(envelope.record_id)
        assert result.outcome == "succeeded"
        manifest = result.manifest_view()
        assert manifest.levels_achieved == [0, 1, 2, 3]

        [derivative] = manifest.derivatives
        glb = store.get_derivative_payload(derivative.payload_reference)
        assert payload_checksum(glb) == derivative.checksum
        instance_ids = {i.instance_id for i in manifest.instances}
        assert derivative.node_map
        assert set(derivative.node_map.values()) <= instance_ids
        assert store.find_orphan_derivatives() == []

    def test_rerun_is_duplicate_and_writes_only_a_run_report(self, env):
        runner, store, _ = env
        runner.run("cad-main")
        before = sorted(p.name for p in store.base_dir.rglob("*") if p.is_file())
        second = runner.run("cad-main")
        after = sorted(p.name for p in store.base_dir.rglob("*") if p.is_file())
        assert second.records_duplicate == 1
        assert set(after) - set(before) == {f"{second.run_id}.json"}

    def test_replay_after_source_removed_matches_stored_extraction(self, env):
        runner, store, tmp_path = env
        runner.run("cad-main")
        [envelope] = store.iter_accepted_envelopes("cad-main")
        stored = store.get_extraction(envelope.record_id)
        (tmp_path / "step_assembly.step").unlink()
        [replayed] = runner.replay("cad-main")
        assert replayed.result == stored

    def test_corrupted_step_quarantined_at_extraction_stage(self, env):
        runner, store, _ = env
        run = runner.run("cad-corrupt")
        assert run.status == "completed_with_quarantine"
        assert run.records_quarantined == 1
        [envelope_path] = (store.base_dir / "envelopes").glob("*.json")
        quarantine = store.get_quarantine(envelope_path.stem)
        assert quarantine.stage == "extraction"
        assert quarantine.error_code == "EXTRACT_STEP_PARSE_FAILED"
        assert runner.health("cad-corrupt").status == "degraded"


class TestFormatDetectionQuarantine:
    def test_native_cad_masquerade_rejected_honestly_without_worker(self, env):
        runner, store, _ = env
        run = runner.run("cad-masquerade")
        assert run.status == "completed_with_quarantine"
        [envelope_path] = (store.base_dir / "envelopes").glob("*.json")
        quarantine = store.get_quarantine(envelope_path.stem)
        assert quarantine.stage == "format_detection"
        assert quarantine.error_code == "EXTRACT_UNSUPPORTED_NATIVE_CAD_FORMAT"
        assert "ole_compound_container" in quarantine.redacted_message
        # raw payload is preserved even though the format was rejected
        [envelope] = list(store.iter_accepted_envelopes("cad-masquerade")) or [None]
        assert envelope is None  # quarantined records are excluded from accepted
        assert (store.base_dir / "envelopes").exists()


class TestPartialOutcome:
    def test_derivative_failure_is_partial_not_quarantine(self, env, monkeypatch):
        from backend.data_sources.extractors.worker_harness import WorkerOutcome
        from tests.data_sources.test_step_extractor import fake_worker_result
        import json as _json

        outcome = WorkerOutcome(
            status="ok", returncode=0, stdout_tail="", stderr_tail="",
            outputs={
                "worker_result.json": _json.dumps(fake_worker_result(False)).encode()
            },
        )
        monkeypatch.setattr(
            "backend.data_sources.extractors.step.step_extractor.invoke_worker",
            lambda *args, **kwargs: outcome,
        )
        runner, store, _ = env
        run = runner.run("cad-main")
        assert run.status == "succeeded"
        assert run.records_partial == 1
        assert run.records_quarantined == 0
        [envelope] = store.iter_accepted_envelopes("cad-main")
        result = store.get_extraction(envelope.record_id)
        assert result.outcome == "partial"
        assert result.manifest_view().levels_achieved == [0, 1, 2]
        assert result.manifest_view().derivatives == []


class TestStagedPublication:
    def test_envelope_failure_leaves_detectable_purgeable_orphan(self, env, monkeypatch):
        from backend.data_sources.extractors.step import StepExtractionProduct
        from tests.data_sources.test_store_v2 import make_step_result

        runner, store, _ = env

        def fake_extract(payload, envelope):
            glb = b"fake-glb-bytes"
            result = make_step_result(store, glb, record_id=envelope.record_id)
            return StepExtractionProduct(
                result=result,
                derivative_payloads={payload_checksum(glb): glb},
            )

        runner.extractors["model/step"] = fake_extract
        original_put = store.put_extraction

        def failing_put(result):
            raise StoreIntegrityError("STORE_CONFLICT", "injected envelope failure")

        monkeypatch.setattr(store, "put_extraction", failing_put)
        run = runner.run("cad-main")
        assert run.status == "completed_with_quarantine"  # honest failure record

        orphans = store.find_orphan_derivatives()
        assert orphans == [payload_checksum(b"fake-glb-bytes")]
        monkeypatch.setattr(store, "put_extraction", original_put)
        assert store.purge_orphan_derivatives() == orphans


class TestProfileV0:
    def test_profile_contents(self):
        entries = {e.source_family: e for e in APPLICATION_PROFILE_V0.entries}
        assert entries["csv_bom"].roadmap_stage == "validated"
        assert entries["csv_bom"].requirement == "required"
        assert entries["step_assembly"].roadmap_stage == "next"
        assert entries["step_assembly"].enabled_for_profile is True
        assert entries["pdf_drawing_manual"].roadmap_stage == "later"
        assert entries["pdf_drawing_manual"].enabled_for_profile is False
        assert entries["operational_api_or_telemetry"].requirement == "required"
        assert entries["excel_workbook"].requirement == "optional"
        assert entries["native_cad"].roadmap_stage == "not_started"

    def test_runner_refuses_sources_outside_the_active_profile(self, env, tmp_path):
        runner, store, _ = env
        pdf_path = tmp_path / "manual.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake")
        runner.catalog.register(
            SourceDefinition(
                source_id="pdf-early",
                display_name="premature pdf",
                source_kind="document",
                connector_type="local_file",
                configuration={"path": str(pdf_path)},
                credential_reference=None,
                declared_content_types=["application/pdf"],
                enabled=True,
            )
        )
        runner.profile = APPLICATION_PROFILE_V0
        run = runner.run("pdf-early")
        assert run.status == "failed"
        assert "ACQUIRE_NOT_IN_PROFILE" in (run.error_summary or "")
