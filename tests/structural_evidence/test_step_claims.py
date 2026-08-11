"""STEP structural claims and derived usage paths (SC1-SC5, M2a, FX6, A11).

Definitions and usages never collapse; parenthood comes ONLY from the
explicit `parent_definition_ref`; when a parent definition is used more
than once, the derived usage path is reported ambiguous — never picked.
Everything here runs base-only from the frozen extraction; FX6 (cad) is
the drift guard proving the live extractor still produces it.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from backend.data_sources.contracts import ExtractionResult
from backend.structural_evidence.claims import step_structural_claims
from backend.structural_evidence.contracts import UnknownEngineeringContext
from backend.structural_evidence.errors import StructuralEvidenceError

from tests.structural_evidence.golden_showcase import (
    EXPECTED_AMBIGUOUS_PATH_COUNT,
    EXPECTED_AMBIGUOUS_PATH_USAGES,
    EXPECTED_STEP_DEFINITION_COUNT,
    EXPECTED_STEP_USAGE_COUNT,
    EXPECTED_TWICE_USED_DEFINITION,
    STEP_RAW_RECORD_ID,
    STEP_SOURCE_ID,
    UPSTREAM_DEFINITION_IDS,
    UPSTREAM_USAGE_IDS,
)

SHOWCASE = Path("showcases/demo-printer")
MANIFEST = json.loads((SHOWCASE / "MANIFEST.json").read_text("utf-8"))
STEP_ENTRY = MANIFEST["sources"]["showcase-printer-cad"]
UNKNOWN = UnknownEngineeringContext(kind="unknown",
                                    reason="source_declares_no_view")


def frozen_extraction() -> ExtractionResult:
    return ExtractionResult.model_validate_json(
        (SHOWCASE / STEP_ENTRY["frozen_extraction_file"]).read_text("utf-8"))


def derive(extraction=None):
    return step_structural_claims(
        extraction or frozen_extraction(), source_id=STEP_SOURCE_ID,
        payload_checksum=STEP_ENTRY["pinned_payload_checksum"],
        engineering_context=UNKNOWN)


class TestSC1DefinitionUsageDiscipline:
    def test_per_kind_counts_never_a_total(self):
        claims = derive()
        by_kind = {}
        for claim in claims.subject_claims:
            by_kind[claim.claim_kind] = by_kind.get(claim.claim_kind, 0) + 1
        assert by_kind == {
            "step_part_definition": EXPECTED_STEP_DEFINITION_COUNT,
            "step_nauo_usage": EXPECTED_STEP_USAGE_COUNT}

    def test_one_definition_two_usages_never_collapse(self):
        claims = derive()
        twice_used_path = next(
            path for path, _ in UPSTREAM_DEFINITION_IDS.items()
            if path == "0:1:1:3")  # gantry-sub per SOURCES.md
        usages = [c for c in claims.subject_claims
                  if c.claim_kind == "step_nauo_usage"
                  and c.address.locator.definition_path_id == twice_used_path]
        assert len(usages) == 2
        assert len({c.address.locator.extractor_path_id for c in usages}) == 2

    def test_the_synthesized_root_is_not_a_usage_claim(self):
        claims = derive()
        for claim in claims.subject_claims:
            if claim.claim_kind == "step_nauo_usage":
                assert claim.address.locator.extractor_path_id != "0:1:1:1"


class TestSC4UpstreamIdCrossChecks:
    def test_upstream_ids_carried_and_verified(self):
        claims = derive()
        definitions = {c.address.locator.extractor_path_id:
                       c.address.locator.upstream_definition_id
                       for c in claims.subject_claims
                       if c.claim_kind == "step_part_definition"}
        assert definitions == UPSTREAM_DEFINITION_IDS
        usages = {c.address.locator.extractor_path_id:
                  c.address.locator.upstream_instance_id
                  for c in claims.subject_claims
                  if c.claim_kind == "step_nauo_usage"}
        assert usages == UPSTREAM_USAGE_IDS

    def test_checksum_mismatch_is_typed(self):
        with pytest.raises(StructuralEvidenceError) as err:
            step_structural_claims(
                frozen_extraction(), source_id=STEP_SOURCE_ID,
                payload_checksum="sha256:" + "00" * 32,
                engineering_context=UNKNOWN)
        assert err.value.error_code == "SN_EXTRACTION_MISMATCH"


class TestSC5ParenthoodDiscipline:
    def test_containment_edges_come_only_from_parent_definition_ref(self):
        claims = derive()
        # every containment edge child is a usage, parent is a definition
        assert len(claims.containment_claims) == EXPECTED_STEP_USAGE_COUNT
        for edge in claims.containment_claims:
            assert edge.claim_kind == "step_nauo_usage_edge"
            assert edge.child.locator.kind == "step_nauo_usage"
            assert edge.parent.locator.kind == "step_part_definition"

    def test_root_usage_with_none_parent_produces_no_edge(self):
        claims = derive()
        children = {e.child.locator.extractor_path_id
                    for e in claims.containment_claims}
        assert "0:1:1:1" not in children  # the synthesized root


class TestSC3DerivedPathAmbiguity:
    def test_twice_used_subassembly_children_are_ambiguous(self):
        claims = derive()
        ambiguous = [p for p in claims.derived_paths
                     if p.ambiguity == "multiple_parent_uses"]
        assert len(ambiguous) == EXPECTED_AMBIGUOUS_PATH_COUNT
        for path in ambiguous:
            assert path.steps == ()

    def test_unique_paths_are_root_first(self):
        claims = derive()
        unique = [p for p in claims.derived_paths if p.ambiguity == "unique"]
        # extruder-1, gantry-left, gantry-right, fan-1 all hang directly
        # off the once-used root definition
        assert len(unique) == 4
        for path in unique:
            assert len(path.steps) == 1


class TestSC2Quarantine:
    @pytest.mark.cad
    def test_corrupted_step_quarantines_and_yields_no_claims(self, tmp_path):
        import shutil
        from datetime import UTC, datetime

        from backend.data_sources.catalog import InMemorySourceCatalog
        from backend.data_sources.connectors import LocalFileConnector
        from backend.data_sources.contracts import SourceDefinition
        from backend.data_sources.raw_store import FilesystemRawStore
        from backend.data_sources.runtime import IngestionRunner

        path = tmp_path / "broken.step"
        shutil.copy(Path("backend/data_sources/testing/fixtures/"
                         "step_corrupted.step"), path)
        catalog = InMemorySourceCatalog()
        catalog.register(SourceDefinition(
            source_id="cad-broken", display_name="b", source_kind="cad_file",
            connector_type="local_file", configuration={"path": str(path)},
            credential_reference=None, declared_content_types=["model/step"],
            enabled=True))
        store = FilesystemRawStore(tmp_path / "raw_store")
        runner = IngestionRunner(
            catalog=catalog, store=store,
            connectors={"local_file": LocalFileConnector()},
            clock=lambda: datetime(2026, 8, 11, 12, 0, tzinfo=UTC))
        run = runner.run("cad-broken")
        assert run.records_quarantined == 1
        # quarantined records are EXCLUDED from the accepted iterator, so
        # there is no envelope to read and no extraction to derive claims
        # from — a QuarantineRecord is never read as a partial result
        assert list(store.iter_accepted_envelopes("cad-broken")) == []
        from backend.data_sources.provenance import (
            derive_record_id,
            payload_checksum,
        )
        record_id = derive_record_id(
            "cad-broken", payload_checksum(path.read_bytes()), 0)
        assert store.has_quarantine(record_id)
        assert not store.has_extraction(record_id)
        quarantine = store.get_quarantine(record_id)
        assert quarantine.error_code == "EXTRACT_STEP_PARSE_FAILED"


class TestM2aClaimSetDeterminism:
    def test_byte_identical_across_hash_seeds(self):
        """Two subprocesses with different PYTHONHASHSEED values must
        produce byte-identical claim-set JSON — the only observation that
        kills a set()/hash-order leak."""
        program = (
            "import json;"
            "from pathlib import Path;"
            "from backend.data_sources.contracts import ExtractionResult;"
            "from backend.structural_evidence.claims import "
            "step_structural_claims;"
            "from backend.structural_evidence.contracts import "
            "UnknownEngineeringContext;"
            "m = json.loads(Path('showcases/demo-printer/MANIFEST.json')"
            ".read_text());"
            "e = m['sources']['showcase-printer-cad'];"
            "x = ExtractionResult.model_validate_json("
            "(Path('showcases/demo-printer')/e['frozen_extraction_file'])"
            ".read_text());"
            "c = step_structural_claims(x, source_id='showcase-printer-cad',"
            "payload_checksum=e['pinned_payload_checksum'],"
            "engineering_context=UnknownEngineeringContext(kind='unknown',"
            "reason='source_declares_no_view'));"
            "print(c.model_dump_json())")
        outputs = set()
        for seed in ("1", "2"):
            result = subprocess.run(
                [sys.executable, "-c", program], capture_output=True,
                text=True, env={"PYTHONHASHSEED": seed,
                                "PYTHONPATH": ".",
                                "PATH": "/usr/bin:/bin"}, check=True)
            outputs.add(result.stdout)
        assert len(outputs) == 1


@pytest.mark.cad
class TestFX6LiveStepEqualsFrozen:
    def test_live_extractor_reproduces_the_frozen_result_exactly(
            self, tmp_path):
        """The ONLY thing stopping the frozen STEP manifest drifting into
        fiction — full-object equality including every literal upstream
        id, so an OCCT shift fails loudly (A11's cad half)."""
        from backend.data_sources.extractors.step.step_extractor import (
            StepExtractionConfig,
            extract_step,
        )
        from backend.data_sources.extractors.worker_harness import (
            WorkerLimits,
        )

        payload = (SHOWCASE / STEP_ENTRY["source_file"]).read_bytes()
        product = extract_step(
            payload=payload,
            raw_record_id=STEP_ENTRY["pinned_raw_record_id"],
            config=StepExtractionConfig(),
            limits=WorkerLimits(timeout_seconds=120.0,
                                max_payload_bytes=50_000_000),
            scratch_root=tmp_path / "scratch")
        frozen = frozen_extraction()
        assert product.result.manifest_view() == frozen.manifest_view()
        assert product.result.extractor == frozen.extractor
