"""End-to-end tests for the DS-001 ingestion runtime."""

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from backend.data_sources.catalog import InMemorySourceCatalog, UnknownSourceError
from backend.data_sources.connectors import LocalFileConnector
from backend.data_sources.contracts import SourceDefinition
from backend.data_sources.provenance import payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore
from backend.data_sources.runtime import IngestionRunner

FIXTURES = Path("backend/data_sources/testing/fixtures")


class FakeClock:
    """Deterministic clock: each call advances one second."""

    def __init__(self) -> None:
        self._now = datetime(2026, 8, 6, 12, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self._now += timedelta(seconds=1)
        return self._now


@pytest.fixture
def env(tmp_path):
    """A catalog + store + runner with both fixtures copied to tmp."""
    valid_path = tmp_path / "bom_valid.csv"
    malformed_path = tmp_path / "bom_malformed.bin"
    shutil.copy(FIXTURES / "bom_valid.csv", valid_path)
    shutil.copy(FIXTURES / "bom_malformed.bin", malformed_path)

    catalog = InMemorySourceCatalog()
    for source_id, path in (("bom-valid", valid_path), ("bom-malformed", malformed_path)):
        catalog.register(
            SourceDefinition(
                source_id=source_id,
                display_name=source_id,
                source_kind="tabular_file",
                connector_type="local_file",
                configuration={"path": str(path)},
                credential_reference=None,
                declared_content_types=["text/csv"],
                enabled=True,
            )
        )
    catalog.register(
        SourceDefinition(
            source_id="bom-disabled",
            display_name="disabled source",
            source_kind="tabular_file",
            connector_type="local_file",
            configuration={"path": str(valid_path)},
            credential_reference=None,
            declared_content_types=["text/csv"],
            enabled=False,
        )
    )

    store = FilesystemRawStore(tmp_path / "raw_store")
    runner = IngestionRunner(
        catalog=catalog,
        store=store,
        connectors={"local_file": LocalFileConnector()},
        clock=FakeClock(),
    )
    return runner, store, valid_path


class TestValidIngestion:
    def test_run_succeeds_and_preserves_everything(self, env):
        runner, store, valid_path = env
        run = runner.run("bom-valid")

        assert run.status == "succeeded"
        assert (run.records_seen, run.records_accepted) == (1, 1)
        assert (run.records_duplicate, run.records_quarantined) == (0, 0)

        [envelope] = store.iter_accepted_envelopes("bom-valid")
        original = valid_path.read_bytes()
        assert envelope.payload_checksum == payload_checksum(original)
        assert store.get_payload(envelope.immutable_payload_reference) == original
        assert envelope.source_observed_at is not None
        assert envelope.source_observed_at != envelope.captured_at
        assert envelope.provenance["observed_at_meaning"] == "file_mtime"

        extraction = store.get_extraction(envelope.record_id)
        assert extraction.outcome == "succeeded"
        assert extraction.extractor.name == "csv_extractor"
        table = extraction.result.table
        assert table.columns[0] == "item_no"
        first_cell = table.rows[0].cells[0]
        assert first_cell.raw_record_id == envelope.record_id
        assert first_cell.physical_row_index == 1
        assert first_cell.column_index == 0

        health = runner.health("bom-valid")
        assert health.status == "ok"
        assert health.last_success_at == run.finished_at

    def test_run_report_is_persisted(self, env):
        runner, store, _ = env
        run = runner.run("bom-valid")
        assert store.get_run(run.run_id) == run


class TestQuarantine:
    def test_malformed_payload_is_preserved_and_quarantined(self, env):
        runner, store, _ = env
        run = runner.run("bom-malformed")

        assert run.status == "completed_with_quarantine"
        assert (run.records_seen, run.records_accepted) == (1, 1)
        assert run.records_quarantined == 1
        assert "EXTRACT_UNDECODABLE" in (run.error_summary or "")

        # Raw payload is preserved even though extraction failed.
        assert list(store.iter_accepted_envelopes("bom-malformed")) == []
        envelopes_dir = store.base_dir / "envelopes"
        assert len(list(envelopes_dir.glob("*.json"))) == 1

        [q_path] = (store.base_dir / "quarantine").glob("*.json")
        quarantine = store.get_quarantine(q_path.stem)
        assert quarantine.error_code == "EXTRACT_UNDECODABLE"
        assert "/" not in quarantine.redacted_message or "<" in quarantine.redacted_message

        assert runner.health("bom-malformed").status == "degraded"

    def test_quarantine_does_not_touch_other_sources(self, env):
        runner, store, _ = env
        runner.run("bom-valid")
        runner.run("bom-malformed")
        assert len(list(store.iter_accepted_envelopes("bom-valid"))) == 1


class TestIdempotentRerun:
    def test_rerun_detects_duplicate_and_creates_nothing_new(self, env):
        runner, store, _ = env
        first = runner.run("bom-valid")
        assert first.records_accepted == 1

        files_before = sorted(p.name for p in store.base_dir.rglob("*.json"))
        second = runner.run("bom-valid")
        files_after = sorted(p.name for p in store.base_dir.rglob("*.json"))

        assert second.status == "succeeded"
        assert (second.records_seen, second.records_accepted) == (1, 0)
        assert second.records_duplicate == 1
        # Only the new run report was added; no new envelope/payload/extraction.
        new_files = set(files_after) - set(files_before)
        assert new_files == {f"{second.run_id}.json"}

    def test_changed_content_is_a_new_record_not_an_overwrite(self, env):
        runner, store, valid_path = env
        runner.run("bom-valid")
        valid_path.write_bytes(valid_path.read_bytes() + b"999-999,Extra,1,piece,\n")
        run = runner.run("bom-valid")
        assert run.records_accepted == 1
        assert run.records_duplicate == 0
        assert len(list(store.iter_accepted_envelopes("bom-valid"))) == 2


class TestReplay:
    def test_replay_matches_original_extraction_without_the_source(self, env):
        runner, store, valid_path = env
        runner.run("bom-valid")
        [envelope] = store.iter_accepted_envelopes("bom-valid")
        original = store.get_extraction(envelope.record_id)

        valid_path.unlink()  # the external source is gone; replay must not need it
        [replayed] = runner.replay("bom-valid")
        assert replayed == original


class TestFailureHonesty:
    def test_missing_file_records_failed_run_with_redacted_error(self, env, tmp_path):
        runner, store, valid_path = env
        valid_path.unlink()
        run = runner.run("bom-valid")
        assert run.status == "failed"
        assert run.records_seen == 0
        assert "ACQUIRE_SOURCE_UNREADABLE" in (run.error_summary or "")
        assert str(tmp_path) not in (run.error_summary or "")
        health = runner.health("bom-valid")
        assert health.status == "failed"
        assert health.diagnostic_code == "ACQUIRE_SOURCE_UNREADABLE"

    def test_unknown_source_raises(self, env):
        runner, _, _ = env
        with pytest.raises(UnknownSourceError):
            runner.run("no-such-source")

    def test_disabled_source_is_a_failed_run_not_an_acquisition(self, env):
        runner, store, _ = env
        run = runner.run("bom-disabled")
        assert run.status == "failed"
        assert "ACQUIRE_SOURCE_DISABLED" in (run.error_summary or "")
        assert list(store.iter_accepted_envelopes("bom-disabled")) == []

    def test_health_unknown_before_any_run(self, env):
        runner, _, _ = env
        assert runner.health("bom-valid").status == "unknown"


class TestValidationLadderIntegration:
    def test_successful_run_flips_validated_with_evidence(self, env):
        runner, store, valid_path = env
        connector = LocalFileConnector()
        source = runner.catalog.get("bom-valid")
        assert connector.status_report(source, store).validated.passed is False
        runner.run("bom-valid")
        report = connector.status_report(source, store)
        assert report.validated.passed is True
        assert "accepted 1 record" in report.validated.evidence
