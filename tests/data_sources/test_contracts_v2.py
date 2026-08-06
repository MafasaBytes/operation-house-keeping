"""Contract tests for DS-002 amendments: extraction envelope, CAD models,
source profile, and the identity/unit/transform honesty rules."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    ComponentInstance,
    CoordinateConversion,
    DerivativeRecord,
    ExtractedTable,
    ExtractionEnvironment,
    ExtractionResult,
    ExtractorIdentity,
    IngestionRun,
    PartDefinition,
    PropertyValue,
    QuarantineRecord,
    SourceProfile,
    SourceProfileEntry,
    StepExtractionManifest,
    TessellationParameters,
    TransformSpec,
    UnitContext,
)

UTC_NOW = datetime(2026, 8, 6, 12, 0, 0, tzinfo=UTC)
RID = "a" * 32

IDENTITY = ExtractorIdentity(
    name="step_extractor",
    version="1.0.0",
    toolchain="cadquery-ocp 7.9.3.1.1",
    config_fingerprint="ab" * 8,
)

UNIT_MM = UnitContext(
    context_id="uc-declared",
    length_unit="millimetre",
    angle_unit=None,
    provenance="explicitly_declared",
    source_representation="SI_UNIT(.MILLI.,.METRE.)",
)

TRANSFORM = TransformSpec(
    matrix=[1.0, 0, 0, 20.0, 0, 1.0, 0, 15.0, 0, 0, 1.0, 6.0, 0, 0, 0, 1.0],
    layout="row_major_4x4",
    source_frame="step_model_space",
    destination_frame="assembly_root",
    handedness="right_handed",
    length_unit_ref="uc-config",
)


def make_definition(**overrides) -> PartDefinition:
    base = dict(
        definition_id="d" * 32,
        extractor_path_id="0:1:1:5",
        source_native_id=None,
        source_native_id_basis=None,
        raw_locator=None,
        name="bolt-m6",
        properties=[],
        unit_context_ref="uc-config",
    )
    base.update(overrides)
    return PartDefinition(**base)


def make_instance(**overrides) -> ComponentInstance:
    base = dict(
        instance_id="e" * 32,
        definition_ref="d" * 32,
        parent_instance_ref=None,
        occurrence_name="bolt-front",
        extractor_path_id="0:1:1:3:2",
        source_native_id=None,
        source_native_id_basis=None,
        raw_locator=None,
        transform=TRANSFORM,
    )
    base.update(overrides)
    return ComponentInstance(**base)


def make_manifest(**overrides) -> StepExtractionManifest:
    base = dict(
        raw_record_id=RID,
        extractor=IDENTITY,
        declared_schemas=["AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }"],
        unit_contexts=[UNIT_MM],
        definitions=[make_definition()],
        instances=[make_instance()],
        root_instance_ids=["e" * 32],
        derivatives=[],
        levels_supported=[0, 1, 2, 3],
        levels_achieved=[0, 1, 2],
        unsupported_features=[],
        lossy_conversions=[],
        warnings=[],
    )
    base.update(overrides)
    return StepExtractionManifest(**base)


class TestExtractorIdentity:
    def test_all_fields_required_and_nonempty(self):
        with pytest.raises(ValidationError):
            ExtractorIdentity(name="", version="1", toolchain="t", config_fingerprint="f")


class TestExtractionResult:
    def test_csv_result_round_trips(self):
        table = ExtractedTable(
            raw_record_id=RID, header_row_index=0, columns=["a"], rows=[], warnings=[]
        )
        result = ExtractionResult(
            schema_version=1,
            raw_record_id=RID,
            extractor=IDENTITY,
            outcome="succeeded",
            warnings=[],
            result={"kind": "csv_table", "table": table},
        )
        restored = ExtractionResult.model_validate_json(result.model_dump_json())
        assert restored == result
        assert restored.result.kind == "csv_table"

    def test_step_result_discriminates(self):
        result = ExtractionResult(
            schema_version=1,
            raw_record_id=RID,
            extractor=IDENTITY,
            outcome="partial",
            warnings=["derivative generation failed: EXTRACT_GLTF_WRITE_FAILED"],
            result={"kind": "step_manifest", "manifest": make_manifest()},
        )
        assert result.result.kind == "step_manifest"
        assert result.outcome == "partial"

    def test_outcome_literals_enforced(self):
        table = ExtractedTable(
            raw_record_id=RID, header_row_index=0, columns=[], rows=[], warnings=[]
        )
        with pytest.raises(ValidationError):
            ExtractionResult(
                schema_version=1,
                raw_record_id=RID,
                extractor=IDENTITY,
                outcome="quarantined",  # quarantine is a QuarantineRecord, not a result
                warnings=[],
                result={"kind": "csv_table", "table": table},
            )


class TestIdentityHonesty:
    def test_source_native_id_requires_a_basis(self):
        with pytest.raises(ValidationError):
            make_definition(source_native_id="#123", source_native_id_basis=None)
        ok = make_definition(
            source_native_id="#123",
            source_native_id_basis="verified via transfer-map replay of entity #123",
        )
        assert ok.source_native_id == "#123"

    def test_basis_without_id_is_rejected(self):
        with pytest.raises(ValidationError):
            make_instance(source_native_id=None, source_native_id_basis="stray basis")


class TestPropertyValue:
    def test_value_type_literals(self):
        prop = PropertyValue(
            name="mass",
            value="0.012",
            value_type="real",
            unit="kilogram",
            raw_representation="0.012 kg",
            locator=None,
        )
        assert prop.unit == "kilogram"
        with pytest.raises(ValidationError):
            PropertyValue(
                name="x", value="1", value_type="float64",
                unit=None, raw_representation="1", locator=None,
            )


class TestUnitContext:
    def test_provenance_literals(self):
        with pytest.raises(ValidationError):
            UnitContext(
                context_id="u1", length_unit="millimetre", angle_unit=None,
                provenance="assumed", source_representation=None,
            )

    def test_unavailable_unit_stays_none_not_millimetre(self):
        ctx = UnitContext(
            context_id="u1", length_unit=None, angle_unit=None,
            provenance="unavailable", source_representation=None,
        )
        assert ctx.length_unit is None  # never silently defaulted

    def test_declared_provenance_requires_source_representation(self):
        with pytest.raises(ValidationError):
            UnitContext(
                context_id="u1", length_unit="millimetre", angle_unit=None,
                provenance="explicitly_declared", source_representation=None,
            )


class TestTransformSpec:
    def test_matrix_must_have_16_entries(self):
        with pytest.raises(ValidationError):
            TransformSpec(
                matrix=[1.0] * 12, layout="row_major_4x4",
                source_frame="a", destination_frame="b",
                handedness="right_handed", length_unit_ref="uc",
            )

    def test_layout_and_handedness_literals(self):
        with pytest.raises(ValidationError):
            TransformSpec(
                matrix=[1.0] * 16, layout="column_major_4x4",
                source_frame="a", destination_frame="b",
                handedness="right_handed", length_unit_ref="uc",
            )


class TestManifest:
    def test_levels_achieved_must_be_subset_of_supported(self):
        with pytest.raises(ValidationError):
            make_manifest(levels_achieved=[0, 1, 4])

    def test_json_round_trip(self):
        manifest = make_manifest()
        restored = StepExtractionManifest.model_validate_json(manifest.model_dump_json())
        assert restored == manifest


class TestDerivativeRecord:
    def make(self, **overrides) -> DerivativeRecord:
        base = dict(
            derivative_id="f" * 32,
            raw_record_id=RID,
            kind="visualization_gltf",
            media_type="model/gltf-binary",
            payload_reference="sha256:" + "cd" * 32,
            checksum="sha256:" + "cd" * 32,
            generator=IDENTITY,
            tessellation=TessellationParameters(
                linear_deflection=0.1, angular_deflection=0.5, relative=False
            ),
            coordinate_conversion=CoordinateConversion(
                source_frame="step_model_space_mm_z_up",
                target_frame="gltf_y_up_right_handed",
                target_length_unit="metre",
                converter="RWGltf_CafWriter default (mm->m, Z-up->Y-up)",
            ),
            node_map={"1": "e" * 32, "3": "b" * 32},
            environment=ExtractionEnvironment(
                platform="linux", architecture="x86_64", occt_version="7.9.3"
            ),
        )
        base.update(overrides)
        return DerivativeRecord(**base)

    def test_node_map_keys_must_be_integer_strings(self):
        with pytest.raises(ValidationError):
            self.make(node_map={"node-one": "e" * 32})

    def test_round_trip(self):
        record = self.make()
        assert DerivativeRecord.model_validate_json(record.model_dump_json()) == record


class TestSourceProfile:
    def test_planning_fields_only(self):
        entry = SourceProfileEntry(
            source_family="step_assembly",
            requirement="required",
            roadmap_stage="next",
            enabled_for_profile=True,
            justification="DS-002 slice",
        )
        assert entry.roadmap_stage == "next"
        with pytest.raises(ValidationError):
            SourceProfileEntry(
                source_family="x", requirement="required",
                roadmap_stage="connected",  # runtime state does not belong here
                enabled_for_profile=True, justification="",
            )

    def test_profile_rejects_duplicate_families(self):
        entry = SourceProfileEntry(
            source_family="csv_bom", requirement="required",
            roadmap_stage="validated", enabled_for_profile=True, justification="",
        )
        with pytest.raises(ValidationError):
            SourceProfile(profile_id="v0", entries=[entry, entry])


class TestRunAndQuarantineAmendments:
    def test_records_partial_defaults_and_old_json_still_valid(self):
        legacy_json = IngestionRun(
            run_id="r", source_id="s", started_at=UTC_NOW, finished_at=UTC_NOW,
            status="succeeded", records_seen=1, records_accepted=1,
            records_duplicate=0, records_quarantined=0, error_summary=None,
        ).model_dump_json(exclude={"records_partial"})
        assert '"records_partial"' not in legacy_json
        restored = IngestionRun.model_validate_json(legacy_json)
        assert restored.records_partial == 0

    def test_quarantine_stage_format_detection_allowed(self):
        q = QuarantineRecord(
            record_id=RID, stage="format_detection",
            error_code="EXTRACT_UNSUPPORTED_NATIVE_CAD_FORMAT",
            redacted_message="payload is an ole_compound_container, not STEP",
            quarantined_at=UTC_NOW,
        )
        assert q.stage == "format_detection"


class TestDeterministicEntityIds:
    def test_derive_entity_id_is_deterministic_and_sensitive(self):
        from backend.data_sources.provenance import derive_entity_id

        a = derive_entity_id(RID, "1.0.0", "0:1:1:3:2")
        assert a == derive_entity_id(RID, "1.0.0", "0:1:1:3:2")
        assert len(a) == 32 and all(c in "0123456789abcdef" for c in a)
        assert a != derive_entity_id(RID, "1.0.1", "0:1:1:3:2")
        assert a != derive_entity_id(RID, "1.0.0", "0:1:1:3:1")
        assert a != derive_entity_id("b" * 32, "1.0.0", "0:1:1:3:2")
