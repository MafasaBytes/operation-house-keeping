"""STEP extractor tests.

Golden tests (marker: cad) run the real OCP worker against the frozen
fixture and compare with the hand-authored oracle in
golden_step_assembly.py. Parent-logic tests (no marker) stub the worker
harness and need no CAD toolchain.
"""

import json
import math
from pathlib import Path

import pytest

from backend.data_sources.contracts import ExtractionError
from backend.data_sources.extractors.step import (
    STEP_EXTRACTOR_VERSION,
    StepExtractionConfig,
    extract_step,
)
from backend.data_sources.extractors.worker_harness import WorkerLimits, WorkerOutcome
from backend.data_sources.provenance import payload_checksum

from tests.data_sources import golden_step_assembly as golden

FIXTURES = Path("backend/data_sources/testing/fixtures")
RID = "a" * 32

LIMITS = WorkerLimits(timeout_seconds=120.0, max_payload_bytes=50_000_000)


def run_fixture(name: str, tmp_path, record_id: str = RID):
    payload = (FIXTURES / name).read_bytes()
    return extract_step(
        payload=payload,
        raw_record_id=record_id,
        config=StepExtractionConfig(),
        limits=LIMITS,
        scratch_root=tmp_path / "scratch",
    )


def by_name(items):
    return {item.name if hasattr(item, "name") else item.occurrence_name: item for item in items}


@pytest.mark.cad
class TestGoldenAssembly:
    def test_structure_matches_hand_authored_oracle(self, tmp_path):
        product = run_fixture("step_assembly.step", tmp_path)
        manifest = product.result.manifest_view()

        assert manifest.declared_schemas == golden.EXPECTED_SCHEMAS

        defs = by_name(manifest.definitions)
        assert set(defs) == set(golden.EXPECTED_DEFINITIONS)
        for name, is_assembly in golden.EXPECTED_DEFINITIONS.items():
            assert defs[name].is_assembly == is_assembly, name
            assert defs[name].source_native_id is None  # never overclaimed

        assert len(manifest.instances) == golden.EXPECTED_INSTANCE_COUNT
        def_by_id = {d.definition_id: d for d in manifest.definitions}
        occurrences = {
            i.occurrence_name: i for i in manifest.instances
            if i.parent_definition_ref is not None
        }
        assert set(occurrences) == set(golden.EXPECTED_OCCURRENCES)
        for occ_name, (def_name, parent_name, translation) in (
            golden.EXPECTED_OCCURRENCES.items()
        ):
            instance = occurrences[occ_name]
            assert def_by_id[instance.definition_ref].name == def_name, occ_name
            assert def_by_id[instance.parent_definition_ref].name == parent_name
            matrix = instance.transform.matrix
            assert matrix[3] == pytest.approx(translation[0], abs=1e-9)
            assert matrix[7] == pytest.approx(translation[1], abs=1e-9)
            assert matrix[11] == pytest.approx(translation[2], abs=1e-9)

        bracket = occurrences["bracket-A"].transform.matrix
        for (row, col), expected in golden.EXPECTED_BRACKET_A_ROTATION.items():
            assert bracket[row * 4 + col] == pytest.approx(expected, abs=1e-9)

        [root_instance] = [
            i for i in manifest.instances if i.parent_definition_ref is None
        ]
        assert def_by_id[root_instance.definition_ref].name == golden.EXPECTED_ROOT_DEFINITION
        assert root_instance.instance_id in manifest.root_instance_ids

    def test_units_declared_not_defaulted(self, tmp_path):
        manifest = run_fixture("step_assembly.step", tmp_path).result.manifest_view()
        declared = [c for c in manifest.unit_contexts if c.provenance == "explicitly_declared"]
        assert len(declared) == 1
        assert declared[0].length_unit == golden.EXPECTED_LENGTH_UNIT
        assert declared[0].source_representation  # carries the source line
        config_ctx = [c for c in manifest.unit_contexts if c.provenance == "configuration_supplied"]
        assert len(config_ctx) == 1
        for instance in manifest.instances:
            assert instance.transform.length_unit_ref == config_ctx[0].context_id

    def test_derivative_traceable_and_levels_full(self, tmp_path):
        product = run_fixture("step_assembly.step", tmp_path)
        result = product.result
        assert result.outcome == "succeeded"
        manifest = result.manifest_view()
        assert manifest.levels_achieved == [0, 1, 2, 3]

        [derivative] = manifest.derivatives
        glb = product.derivative_payloads[derivative.payload_reference]
        assert payload_checksum(glb) == derivative.checksum
        assert glb[:4] == b"glTF"

        instance_ids = {i.instance_id for i in manifest.instances}
        assert derivative.node_map  # index-keyed sidecar exists
        for node_index, instance_id in derivative.node_map.items():
            assert node_index.isdigit()
            assert instance_id in instance_ids
        # every occurrence with geometry is reachable from the node map
        mapped = set(derivative.node_map.values())
        mesh_count = sum(
            1 for i in manifest.instances if i.instance_id in mapped
        )
        assert mesh_count >= golden.EXPECTED_MESH_NODE_COUNT
        assert derivative.environment.component_versions["occt"]
        assert derivative.tessellation.linear_deflection == 0.1
        # renaming for traceability is declared as a lossy conversion
        assert any("node name" in note.lower() for note in manifest.lossy_conversions)

    def test_semantic_determinism_and_same_platform_glb_stability(self, tmp_path):
        first = run_fixture("step_assembly.step", tmp_path)
        second = run_fixture("step_assembly.step", tmp_path / "second")
        assert (
            first.result.model_dump_json() == second.result.model_dump_json()
        )  # canonical byte-stable manifest JSON
        assert set(first.derivative_payloads) == set(second.derivative_payloads)
        for reference, data in first.derivative_payloads.items():
            assert second.derivative_payloads[reference] == data

    def test_part_only_has_definition_and_root_but_no_occurrences(self, tmp_path):
        manifest = run_fixture("step_part_only.step", tmp_path).result.manifest_view()
        assert [d.name for d in manifest.definitions] == ["lone-cube"]
        assert len(manifest.instances) == 1  # synthesized root only
        assert manifest.instances[0].parent_definition_ref is None

    def test_corrupted_step_raises_parse_failed(self, tmp_path):
        with pytest.raises(ExtractionError) as excinfo:
            run_fixture("step_corrupted.step", tmp_path)
        assert excinfo.value.error_code == "EXTRACT_STEP_PARSE_FAILED"


def fake_worker_result(gltf_ok: bool):
    return {
        "status": "ok",
        "error": None,
        "toolchain": "cadquery-ocp 7.9.3.1.1",
        "occt_version": "7.9.3",
        "free_roots": [{"path": "0:1:1:1", "name": "demo-unit"}],
        "definitions": [
            {"path": "0:1:1:1", "name": "demo-unit", "is_assembly": True},
            {"path": "0:1:1:2", "name": "base-plate", "is_assembly": False},
        ],
        "occurrences": [
            {
                "path": "0:1:1:1:1",
                "name": "base-1",
                "ref_path": "0:1:1:2",
                "parent_def_path": "0:1:1:1",
                "matrix12": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            }
        ],
        "gltf": (
            {"ok": True, "file": "scene.glb", "error": None}
            if gltf_ok
            else {"ok": False, "file": None, "error": "tessellation exploded"}
        ),
        "coordinate_conversion": {
            "source_frame": "step_model_space_mm_z_up",
            "target_frame": "gltf_y_up_right_handed",
            "target_length_unit": "metre",
            "converter": "RWGltf_CafWriter (explicit mm->m, Z-up->Y-up)",
        },
        "warnings": [],
    }


class TestParentLogicWithStubbedWorker:
    STEP_PAYLOAD = (
        b"ISO-10303-21;\nHEADER;\n"
        b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"
        b"#24 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );\n"
        b"ENDSEC;\nEND-ISO-10303-21;\n"
    )

    def _patch(self, monkeypatch, outcome: WorkerOutcome):
        monkeypatch.setattr(
            "backend.data_sources.extractors.step.step_extractor.invoke_worker",
            lambda *args, **kwargs: outcome,
        )

    def test_gltf_failure_yields_partial_levels_0_2(self, monkeypatch, tmp_path):
        outcome = WorkerOutcome(
            status="ok", returncode=0, stdout_tail="", stderr_tail="",
            outputs={"worker_result.json": json.dumps(fake_worker_result(False)).encode()},
        )
        self._patch(monkeypatch, outcome)
        product = extract_step(
            payload=self.STEP_PAYLOAD, raw_record_id=RID,
            config=StepExtractionConfig(), limits=LIMITS,
        )
        result = product.result
        assert result.outcome == "partial"
        manifest = result.manifest_view()
        assert manifest.levels_achieved == [0, 1, 2]
        assert manifest.derivatives == []
        assert product.derivative_payloads == {}
        assert any("tessellation exploded" in w for w in result.warnings)

    def test_worker_crash_raises_worker_crashed(self, monkeypatch):
        outcome = WorkerOutcome(
            status="crashed", returncode=-11, stdout_tail="",
            stderr_tail="Segmentation fault", outputs={},
        )
        self._patch(monkeypatch, outcome)
        with pytest.raises(ExtractionError) as excinfo:
            extract_step(
                payload=self.STEP_PAYLOAD, raw_record_id=RID,
                config=StepExtractionConfig(), limits=LIMITS,
            )
        assert excinfo.value.error_code == "EXTRACT_WORKER_CRASHED"

    def test_worker_timeout_raises_worker_timeout(self, monkeypatch):
        outcome = WorkerOutcome(
            status="timeout", returncode=None, stdout_tail="", stderr_tail="",
            outputs={},
        )
        self._patch(monkeypatch, outcome)
        with pytest.raises(ExtractionError) as excinfo:
            extract_step(
                payload=self.STEP_PAYLOAD, raw_record_id=RID,
                config=StepExtractionConfig(), limits=LIMITS,
            )
        assert excinfo.value.error_code == "EXTRACT_WORKER_TIMEOUT"

    def test_ids_are_deterministic_and_distinct_per_role(self, monkeypatch):
        outcome = WorkerOutcome(
            status="ok", returncode=0, stdout_tail="", stderr_tail="",
            outputs={"worker_result.json": json.dumps(fake_worker_result(False)).encode()},
        )
        self._patch(monkeypatch, outcome)
        kwargs = dict(
            payload=self.STEP_PAYLOAD, raw_record_id=RID,
            config=StepExtractionConfig(), limits=LIMITS,
        )
        first = extract_step(**kwargs).result.manifest_view()
        second = extract_step(**kwargs).result.manifest_view()
        assert first == second
        root_def = [d for d in first.definitions if d.name == "demo-unit"][0]
        root_inst = [i for i in first.instances if i.parent_definition_ref is None][0]
        # a root instance id never collides with its definition id
        assert root_def.definition_id != root_inst.instance_id
