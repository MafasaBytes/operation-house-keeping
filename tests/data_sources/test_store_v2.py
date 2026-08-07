"""Store tests for DS-002: extraction envelopes, legacy reading,
derivative payloads, staged publication, and orphan handling."""

import json

import pytest

from backend.data_sources.contracts import (
    CoordinateConversion,
    DerivativeRecord,
    ExtractedTable,
    ExtractionEnvironment,
    ExtractionResult,
    ExtractorIdentity,
    StepExtractionManifest,
    StoreIntegrityError,
    TessellationParameters,
)
from backend.data_sources.provenance import payload_checksum
from backend.data_sources.raw_store import FilesystemRawStore

RID = "a" * 32

IDENTITY = ExtractorIdentity(
    name="csv_extractor",
    version="1.1.0",
    toolchain="python-stdlib-csv",
    config_fingerprint="cafe" * 4,
)


def make_csv_result(record_id: str = RID) -> ExtractionResult:
    table = ExtractedTable(
        raw_record_id=record_id, header_row_index=0,
        columns=["item_no"], rows=[], warnings=[],
    )
    return ExtractionResult(
        schema_version=1,
        raw_record_id=record_id,
        extractor=IDENTITY,
        outcome="succeeded",
        warnings=[],
        result={"kind": "csv_table", "table": table},
    )


def make_step_result(store, glb: bytes, record_id: str = RID) -> ExtractionResult:
    reference = store.put_derivative_payload(glb)
    derivative = DerivativeRecord(
        derivative_id="b" * 32,
        raw_record_id=record_id,
        kind="visualization_gltf",
        media_type="model/gltf-binary",
        payload_reference=reference,
        checksum=reference,
        generator=IDENTITY,
        tessellation=TessellationParameters(
            linear_deflection=0.1, angular_deflection=0.5, relative=False
        ),
        coordinate_conversion=CoordinateConversion(
            source_frame="step", target_frame="gltf",
            target_length_unit="metre", converter="test",
        ),
        node_map={},
        environment=ExtractionEnvironment(
            platform="linux", architecture="x86_64", component_versions={"occt": "7.9.3"}
        ),
    )
    manifest = StepExtractionManifest(
        raw_record_id=record_id, extractor=IDENTITY, declared_schemas=[],
        unit_contexts=[], definitions=[], instances=[], root_instance_ids=[],
        derivatives=[derivative], levels_supported=[0, 1, 2, 3],
        levels_achieved=[0, 1], unsupported_features=[], lossy_conversions=[],
        warnings=[],
    )
    return ExtractionResult(
        schema_version=1, raw_record_id=record_id, extractor=IDENTITY,
        outcome="succeeded", warnings=[],
        result={"kind": "step_manifest", "manifest": manifest},
    )


@pytest.fixture
def store(tmp_path):
    return FilesystemRawStore(tmp_path / "raw_store")


class TestExtractionEnvelope:
    def test_round_trip(self, store):
        result = make_csv_result()
        assert store.put_extraction(result) is True
        assert store.get_extraction(RID) == result

    def test_write_once_conflict(self, store):
        store.put_extraction(make_csv_result())
        conflicting = make_csv_result().model_copy(update={"outcome": "partial"})
        with pytest.raises(StoreIntegrityError):
            store.put_extraction(conflicting)

    def test_legacy_bare_table_json_is_wrapped_on_read(self, store):
        # Simulate a DS-001-era file: a bare ExtractedTable, no envelope.
        table = ExtractedTable(
            raw_record_id=RID, header_row_index=0,
            columns=["item_no"], rows=[], warnings=[],
        )
        legacy_path = store.base_dir / "extracted" / f"{RID}.json"
        legacy_path.write_text(table.model_dump_json(indent=2), "utf-8")

        wrapped = store.get_extraction(RID)
        assert wrapped.schema_version == 1
        assert wrapped.outcome == "succeeded"
        assert wrapped.extractor.version == "legacy"
        assert wrapped.result.kind == "csv_table"
        assert wrapped.result.table == table


class TestDerivativePayloads:
    def test_put_get_round_trip_with_checksum_verify(self, store):
        data = b"glTF-binary-bytes"
        reference = store.put_derivative_payload(data)
        assert reference == payload_checksum(data)
        assert store.get_derivative_payload(reference) == data

    def test_tampered_derivative_detected_on_read(self, store, tmp_path):
        reference = store.put_derivative_payload(b"glTF-binary-bytes")
        [path] = (store.base_dir / "derivatives").iterdir()
        path.chmod(0o644)
        path.write_bytes(b"tampered")
        with pytest.raises(StoreIntegrityError):
            store.get_derivative_payload(reference)


class TestOrphanDerivatives:
    def test_referenced_derivative_is_not_an_orphan(self, store):
        result = make_step_result(store, b"referenced-glb")
        store.put_extraction(result)
        assert store.find_orphan_derivatives() == []

    def test_unreferenced_derivative_is_detected_and_purgeable(self, store):
        # Simulates a failure between derivative publication and the
        # envelope write: the derivative exists, no manifest references it.
        store.put_extraction(make_step_result(store, b"referenced-glb"))
        orphan_ref = store.put_derivative_payload(b"orphaned-glb")

        assert store.find_orphan_derivatives() == [orphan_ref]
        purged = store.purge_orphan_derivatives()
        assert purged == [orphan_ref]
        assert store.find_orphan_derivatives() == []
        with pytest.raises(StoreIntegrityError):
            store.get_derivative_payload(orphan_ref)

    def test_purge_never_touches_payloads_envelopes_or_referenced(self, store):
        payload_ref = store.put_payload(b"raw payload bytes")
        store.put_extraction(make_step_result(store, b"referenced-glb"))
        store.put_derivative_payload(b"orphaned-glb")
        store.purge_orphan_derivatives()
        assert store.get_payload(payload_ref) == b"raw payload bytes"
        kept = store.get_extraction(RID).result.manifest.derivatives[0]
        assert store.get_derivative_payload(kept.payload_reference) == b"referenced-glb"
