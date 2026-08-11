"""Showcase fixture integrity (FX1-FX5, FX7, FX8, A5a) — all base-only.

The frozen extraction derivatives are what let the whole SN-001 suite run
without the CAD extra; these tests are what keep them honest. FX6 (the
cad-marked drift guard proving the live STEP extractor still produces the
frozen result) lives in test_step_claims.py.
"""

import hashlib
import json
from pathlib import Path

from backend.data_sources.contracts import ExtractionResult
from backend.data_sources.extractors.csv_extractor import (
    CsvExtractionConfig,
    csv_extractor_identity,
    extract_csv,
)
from backend.data_sources.provenance import derive_record_id, payload_checksum

SHOWCASE = Path("showcases/demo-printer")
MANIFEST = json.loads((SHOWCASE / "MANIFEST.json").read_text("utf-8"))
FIXTURES = Path("backend/data_sources/testing/fixtures")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    entries = list(MANIFEST["sources"].items())
    assert len(entries) >= 2, "vacuous manifest"
    return entries


class TestFX1SourceChecksums:
    def test_every_committed_source_matches_the_manifest(self):
        for source_id, entry in sources():
            path = SHOWCASE / entry["source_file"]
            assert path.is_file(), path
            assert sha256(path) == entry["source_sha256"], source_id


class TestFX2FrozenExtractionChecksums:
    def test_every_frozen_extraction_matches_and_parses(self):
        for source_id, entry in sources():
            frozen = SHOWCASE / entry["frozen_extraction_file"]
            assert sha256(frozen) == entry["frozen_extraction_sha256"]
            extraction = ExtractionResult.model_validate_json(
                frozen.read_text("utf-8"))
            assert extraction.raw_record_id == entry["pinned_raw_record_id"]

    def test_no_stray_extraction_files(self):
        frozen = {e["frozen_extraction_file"] for _, e in sources()}
        on_disk = {f"extractions/{p.name}"
                   for p in (SHOWCASE / "extractions").glob("*.json")}
        assert on_disk == frozen


class TestFX3PinnedIngestionIdentity:
    def test_committed_bytes_derive_the_pinned_ids(self):
        """raw_record_id = derive_record_id(source_id, checksum, 0) for
        file sources; both extractors' identities re-verify from the
        committed bytes without any extraction run (base-only for STEP)."""
        for source_id, entry in sources():
            payload = (SHOWCASE / entry["source_file"]).read_bytes()
            checksum = payload_checksum(payload)
            assert checksum == entry["pinned_payload_checksum"], source_id
            assert derive_record_id(source_id, checksum, 0) == \
                entry["pinned_raw_record_id"], source_id


class TestFX4FrozenExtractorIdentity:
    def test_frozen_extractor_equals_the_manifest_field_for_field(self):
        for source_id, entry in sources():
            extraction = ExtractionResult.model_validate_json(
                (SHOWCASE / entry["frozen_extraction_file"]).read_text(
                    "utf-8"))
            assert extraction.extractor.model_dump() == entry["extractor"]
            assert hashlib.sha256(
                extraction.extractor.toolchain.encode()).hexdigest()[:16] \
                == entry["extractor_toolchain_fingerprint"]


class TestFX5LiveCsvEqualsFrozen:
    def test_live_extraction_over_committed_bytes_equals_frozen(self):
        entry = MANIFEST["sources"]["showcase-printer-bom"]
        payload = (SHOWCASE / entry["source_file"]).read_bytes()
        config = CsvExtractionConfig()
        assert csv_extractor_identity(config).model_dump() == \
            entry["extractor"]
        live = extract_csv(payload, entry["pinned_raw_record_id"], config)
        frozen = ExtractionResult.model_validate_json(
            (SHOWCASE / entry["frozen_extraction_file"]).read_text("utf-8"))
        assert live == frozen.table_view()


class TestFX7ManifestHonesty:
    def test_regeneration_command_and_honesty_sentence_verbatim(self):
        assert "regeneration_command" in MANIFEST
        assert "tools/generate.py" in MANIFEST["regeneration_command"]
        assert ("Synthetic showcase evidence; represents no real machine."
                in MANIFEST["honesty"])
        assert "NOT an authoritative ledger record" in MANIFEST["honesty"]


class TestFX8NoNameJoinWithTheNegativeCorpus:
    def test_showcase_and_fixture_filenames_are_disjoint(self):
        fixture_names = {p.name for p in FIXTURES.rglob("*")
                         if p.is_file() and "__pycache__" not in p.parts}
        showcase_names = {p.name for p in SHOWCASE.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts}
        assert len(fixture_names) >= 20, "vacuous fixture corpus"
        assert len(showcase_names) >= 5, "vacuous showcase corpus"
        assert fixture_names & showcase_names == set()


class TestA5aShowcaseHonestyLabel:
    def test_every_prose_artifact_carries_the_label(self):
        labelled = [SHOWCASE / "README.md", SHOWCASE / "SOURCES.md",
                    SHOWCASE / "tools" / "generate.py"]
        for path in labelled:
            text = path.read_text("utf-8").lower()
            assert "synthetic showcase evidence" in text, path
            assert "represents no real machine" in text, path
        first_line = (SHOWCASE / "README.md").read_text("utf-8").splitlines()[0]
        assert "synthetic showcase evidence" in first_line
        assert "represents no real machine" in first_line
