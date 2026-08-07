"""DS-003 contract refactor tests: derivative union, environment
generalization, schema versioning, and read compatibility with DS-002-era
artifacts (which must never be rewritten or reinterpreted)."""

import json

from backend.data_sources.contracts import (
    DerivativeCore,
    ExtractionEnvironment,
    ExtractionResult,
    GltfDerivativeRecord,
    PageRenderDerivativeRecord,
)

RID = "a" * 32
CHECKSUM = "sha256:" + "cd" * 32

IDENTITY_JSON = {
    "name": "step_extractor",
    "version": "1.0.0",
    "toolchain": "cadquery-ocp 7.9.3.1.1",
    "config_fingerprint": "ab" * 8,
}

# Verbatim shape written by DS-002 (environment carries occt_version).
LEGACY_GLTF_DERIVATIVE_JSON = {
    "derivative_id": "f" * 32,
    "raw_record_id": RID,
    "kind": "visualization_gltf",
    "media_type": "model/gltf-binary",
    "payload_reference": CHECKSUM,
    "checksum": CHECKSUM,
    "generator": IDENTITY_JSON,
    "tessellation": {
        "linear_deflection": 0.1,
        "angular_deflection": 0.5,
        "relative": False,
    },
    "coordinate_conversion": {
        "source_frame": "step_model_space_mm_z_up",
        "target_frame": "gltf_y_up_right_handed",
        "target_length_unit": "metre",
        "converter": "RWGltf_CafWriter with explicit mm->m scale and Z-up input",
    },
    "node_map": {"1": "e" * 32},
    "environment": {
        "platform": "linux",
        "architecture": "x86_64",
        "occt_version": "7.9.3",
    },
}


class TestEnvironmentGeneralization:
    def test_new_shape_uses_component_versions(self):
        env = ExtractionEnvironment(
            platform="linux",
            architecture="x86_64",
            component_versions={"pdfium": "5.12.1", "pillow": "12.3.0"},
        )
        assert env.component_versions["pdfium"] == "5.12.1"

    def test_legacy_occt_version_json_converts_on_read(self):
        env = ExtractionEnvironment.model_validate(
            {"platform": "linux", "architecture": "x86_64", "occt_version": "7.9.3"}
        )
        assert env.component_versions == {"occt": "7.9.3"}


class TestDerivativeUnion:
    def test_legacy_gltf_derivative_json_still_validates(self):
        record = GltfDerivativeRecord.model_validate(LEGACY_GLTF_DERIVATIVE_JSON)
        assert record.kind == "visualization_gltf"
        assert record.environment.component_versions == {"occt": "7.9.3"}
        assert isinstance(record, DerivativeCore)

    def test_page_render_derivative(self):
        record = PageRenderDerivativeRecord(
            derivative_id="b" * 32,
            raw_record_id=RID,
            media_type="image/png",
            payload_reference=CHECKSUM,
            checksum=CHECKSUM,
            generator=IDENTITY_JSON,
            environment={
                "platform": "linux",
                "architecture": "x86_64",
                "component_versions": {"pdfium": "5.12.1", "pillow": "12.3.0"},
            },
            page_index=2,
            dpi=150,
            colorspace="RGB",
            pixel_width=1275,
            pixel_height=1651,
        )
        assert record.kind == "page_render_png"
        assert isinstance(record, DerivativeCore)
        restored = PageRenderDerivativeRecord.model_validate_json(
            record.model_dump_json()
        )
        assert restored == record


class TestSchemaVersioning:
    def _step_result_v1_json(self) -> str:
        return json.dumps(
            {
                "schema_version": 1,
                "raw_record_id": RID,
                "extractor": IDENTITY_JSON,
                "outcome": "succeeded",
                "warnings": [],
                "result": {
                    "kind": "step_manifest",
                    "manifest": {
                        "raw_record_id": RID,
                        "extractor": IDENTITY_JSON,
                        "declared_schemas": [],
                        "unit_contexts": [],
                        "definitions": [],
                        "instances": [],
                        "root_instance_ids": [],
                        "derivatives": [LEGACY_GLTF_DERIVATIVE_JSON],
                        "levels_supported": [0, 1, 2, 3],
                        "levels_achieved": [0, 1, 2, 3],
                        "unsupported_features": [],
                        "lossy_conversions": [],
                        "warnings": [],
                    },
                },
            }
        )

    def test_ds002_era_v1_artifact_reads_without_reinterpretation(self):
        result = ExtractionResult.model_validate_json(self._step_result_v1_json())
        assert result.schema_version == 1  # kept as-is, not rewritten
        derivative = result.manifest_view().derivatives[0]
        assert derivative.environment.component_versions == {"occt": "7.9.3"}

    def test_new_results_default_to_schema_version_2(self):
        from backend.data_sources.contracts import CsvTableResult, ExtractedTable

        result = ExtractionResult(
            raw_record_id=RID,
            extractor=IDENTITY_JSON,
            outcome="succeeded",
            warnings=[],
            result=CsvTableResult(
                table=ExtractedTable(
                    raw_record_id=RID, header_row_index=0,
                    columns=[], rows=[], warnings=[],
                )
            ),
        )
        assert result.schema_version == 2
