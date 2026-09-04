"""EA-001 Slice A: DS-004 operational evidence reader acceptance."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    Ds004OperationalEvidenceMaterial,
    Ds004OperationalEvidenceScope,
    OperationalApiArtifactDescriptor,
    OperationalApiInventoryToken,
    OperationalEvidenceReadError,
)
from backend.data_sources.evidence import FilesystemDs004OperationalEvidenceReader

from tests.data_sources.test_ingestion_runner_api import happy_script, make_runner


def _scope(**updates) -> Ds004OperationalEvidenceScope:
    values = {
        "source_id": "printer-1",
        "adapter_id": "moonraker",
        "endpoint_id": "printer_objects_query",
        "item_key": "printer_objects",
        "subject_identifier": "extruder",
        "extraction_route": "api:moonraker:v1",
        "json_pointer": "/result/status/extruder/temperature",
    }
    values.update(updates)
    return Ds004OperationalEvidenceScope(**values)


def _reader_world(tmp_path):
    runner, store, _ = make_runner(tmp_path, happy_script())
    runner.run("printer-1")
    reader = FilesystemDs004OperationalEvidenceReader(store)
    return store, reader


HORIZON = datetime(2026, 8, 7, 19, 0, tzinfo=UTC)
AS_OF = datetime(2026, 8, 7, 21, 0, tzinfo=UTC)


def test_exact_contract_field_order_and_strict_scope():
    assert tuple(Ds004OperationalEvidenceScope.model_fields) == (
        "source_id", "adapter_id", "endpoint_id", "item_key",
        "subject_identifier", "extraction_route", "json_pointer",
    )
    assert tuple(OperationalApiArtifactDescriptor.model_fields) == (
        "kind", "logical_id", "byte_count", "captured_file_sha256",
        "payload_checksum",
    )
    assert tuple(OperationalApiInventoryToken.model_fields) == (
        "schema_version", "scope", "horizon_started_at", "as_of",
        "ordered_member_keys", "canonical_membership_sha256",
    )
    with pytest.raises(ValidationError):
        Ds004OperationalEvidenceScope.model_validate({
            **_scope().model_dump(), "unexpected": "field"})
    with pytest.raises(ValidationError):
        Ds004OperationalEvidenceScope.model_validate({
            **_scope().model_dump(), "source_id": 7})


def test_happy_material_closes_api_chain_and_hashes_exact_bytes(tmp_path):
    store, reader = _reader_world(tmp_path)
    before = sorted(
        (p.relative_to(store.base_dir).as_posix(), p.read_bytes())
        for p in store.base_dir.rglob("*") if p.is_file())

    token = reader.inventory_token(
        _scope(), horizon_started_at=HORIZON, as_of=AS_OF)
    material = reader.read_material(
        _scope(), horizon_started_at=HORIZON, as_of=AS_OF,
        selected_seed_attempt_id=None)

    assert token.scope == _scope()
    assert token.canonical_membership_sha256.startswith("sha256:")
    assert len(material.attempts) == 1
    assert material.attempts[0].endpoint_id == "printer_objects_query"
    assert len(material.runs) == 1
    assert len(material.envelopes) == 1
    assert len(material.extractions) == 1
    assert material.extractions[0].result.kind == "api_observations"
    assert any(o.json_pointer == _scope().json_pointer
               for o in material.observations)
    assert {d.kind for d in material.artifacts} >= {
        "ingestion_run", "acquisition_attempt", "raw_envelope",
        "raw_payload", "extraction_result"}
    for descriptor in material.artifacts:
        assert descriptor.captured_file_sha256.startswith("sha256:")
        assert len(descriptor.captured_file_sha256) == 71
    payload_descriptor = next(d for d in material.artifacts
                              if d.kind == "raw_payload")
    assert payload_descriptor.captured_file_sha256 == (
        payload_descriptor.payload_checksum)

    after = sorted(
        (p.relative_to(store.base_dir).as_posix(), p.read_bytes())
        for p in store.base_dir.rglob("*") if p.is_file())
    assert after == before


def test_metadata_digest_matches_the_same_stored_bytes(tmp_path):
    store, reader = _reader_world(tmp_path)
    material = reader.read_material(
        _scope(), horizon_started_at=HORIZON, as_of=AS_OF,
        selected_seed_attempt_id=None)
    attempt = material.attempts[0]
    descriptor = next(d for d in material.artifacts
                      if d.kind == "acquisition_attempt")
    stored = (store.base_dir / "attempts" / f"{attempt.attempt_id}.json").read_bytes()
    assert descriptor.byte_count == len(stored)
    assert descriptor.captured_file_sha256 == (
        "sha256:" + hashlib.sha256(stored).hexdigest())


@pytest.mark.parametrize("route", [
    "csv:v1", "excel:v1", "pdf:v1", "step:v1", "cad:v1", "file:json:v1",
])
def test_non_ds004_routes_reject_without_path_leak(tmp_path, route):
    _, reader = _reader_world(tmp_path)
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.inventory_token(
            _scope(extraction_route=route),
            horizon_started_at=HORIZON, as_of=AS_OF)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_UNSUPPORTED_ROUTE"
    assert str(tmp_path) not in str(exc.value)


def test_payload_checksum_mutation_fails_closed(tmp_path):
    store, reader = _reader_world(tmp_path)
    [payload] = [p for p in (store.base_dir / "payloads").iterdir()
                 if b'"extruder"' in p.read_bytes()]
    payload.chmod(0o644)
    payload.write_bytes(payload.read_bytes() + b" ")
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.read_material(
            _scope(), horizon_started_at=HORIZON, as_of=AS_OF,
            selected_seed_attempt_id=None)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_CHECKSUM_MISMATCH"
    assert str(tmp_path) not in str(exc.value)


def test_nested_manifest_is_not_accepted_as_outer_extraction(tmp_path):
    store, reader = _reader_world(tmp_path)
    attempt = next(a for a in store.iter_attempts("printer-1")
                   if a.item_key == "printer_objects")
    path = store.base_dir / "extracted" / f"{attempt.raw_record_id}.json"
    outer = json.loads(path.read_text("utf-8"))
    path.chmod(0o644)
    path.write_text(json.dumps(outer["result"]["manifest"]), "utf-8")
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.read_material(
            _scope(), horizon_started_at=HORIZON, as_of=AS_OF,
            selected_seed_attempt_id=None)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_METADATA_INVALID"


def test_observation_value_substitution_fails_pointer_closure(tmp_path):
    store, reader = _reader_world(tmp_path)
    attempt = next(a for a in store.iter_attempts("printer-1")
                   if a.item_key == "printer_objects")
    path = store.base_dir / "extracted" / f"{attempt.raw_record_id}.json"
    outer = json.loads(path.read_text("utf-8"))
    observations = outer["result"]["manifest"]["observations"]
    target = next(o for o in observations if o["json_pointer"] == _scope().json_pointer)
    target["value_json"] = "999"
    path.chmod(0o644)
    path.write_text(json.dumps(outer), "utf-8")
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.read_material(
            _scope(), horizon_started_at=HORIZON, as_of=AS_OF,
            selected_seed_attempt_id=None)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH"


def test_unexpected_attempt_name_and_symlink_reject(tmp_path):
    store, reader = _reader_world(tmp_path)
    (store.base_dir / "attempts" / "unexpected.tmp").write_text("x", "utf-8")
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.inventory_token(
            _scope(), horizon_started_at=HORIZON, as_of=AS_OF)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_UNEXPECTED_ENTRY"

    (store.base_dir / "attempts" / "unexpected.tmp").unlink()
    target = next((store.base_dir / "attempts").glob("*.json"))
    link = store.base_dir / "attempts" / ("f" * 32 + ".json")
    link.symlink_to(target)
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.inventory_token(
            _scope(), horizon_started_at=HORIZON, as_of=AS_OF)
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_UNSAFE_ENTRY"


def test_hostile_nested_material_is_revalidated():
    forged = Ds004OperationalEvidenceMaterial.model_construct(
        schema_version="1", scope=_scope(), artifacts=(), runs=(), attempts=(
            {"not": "an attempt"},), envelopes=(), extractions=(),
        quarantines=(), observations=())
    with pytest.raises(ValidationError):
        Ds004OperationalEvidenceMaterial.model_validate(
            forged.model_dump(mode="python", warnings=False))
