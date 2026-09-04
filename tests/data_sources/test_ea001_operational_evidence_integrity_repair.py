"""EA-001 Slice A integrity-repair regressions.

These tests preserve the exact preimplementation discrepancy: a pre-horizon
source seed and its closure were absent from both source fence tokens.
"""

from __future__ import annotations

import json
import socket
from collections import Counter
from datetime import timedelta
from unittest.mock import patch

import pytest

from backend.data_sources.contracts import OperationalEvidenceReadError
from backend.data_sources.evidence import FilesystemDs004OperationalEvidenceReader
import backend.data_sources.evidence.operational_api as operational_api

from tests.data_sources.test_ea001_operational_evidence_reader import _scope
from tests.data_sources.test_http_api_connector import ok_json
from tests.data_sources.test_ingestion_runner_api import (
    fixture_response,
    happy_script,
    make_runner,
)


def _seed_world(tmp_path, *, reuse: bool = False):
    runner, store, transport = make_runner(tmp_path, happy_script())
    runner.run("printer-1")
    if reuse:
        runner.run("printer-1")
    attempts = [
        row for row in store.iter_attempts("printer-1")
        if row.item_key == "printer_objects"
    ]
    seed = attempts[-1]
    horizon = seed.received_at + timedelta(hours=1)
    as_of = horizon + timedelta(hours=1)
    return runner, store, transport, seed, horizon, as_of


def _token(reader, horizon, as_of):
    return reader.inventory_token(
        _scope(), horizon_started_at=horizon, as_of=as_of)


def _append_json_whitespace(path):
    original = path.read_bytes()
    path.chmod(0o644)
    path.write_bytes(original + b" ")


def _seed_and_empty_horizon_world(tmp_path):
    runner, store, transport, seed, _, _ = _seed_world(tmp_path)
    transport.script["/printer/objects/query"] = ok_json({
        "result": {"status": {}, "eventtime": 4000.0},
    })
    runner.run("printer-1")
    attempts = sorted(
        (
            row for row in store.iter_attempts("printer-1")
            if row.item_key == "printer_objects"
        ),
        key=lambda row: row.received_at,
    )
    horizon = attempts[-1].received_at
    return store, seed, horizon, horizon + timedelta(seconds=1)


def _capture(reader, seed, horizon, as_of):
    return reader.read_material(
        _scope(), horizon_started_at=horizon, as_of=as_of,
        selected_seed_attempt_id=seed.attempt_id)


def test_exact_discrepancy_seed_attempt_same_length_mutation_changes_fence(
    tmp_path,
):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    initial = _token(reader, horizon, as_of)
    attempt_path = store.base_dir / "attempts" / f"{seed.attempt_id}.json"
    original = attempt_path.read_bytes()
    assert b"20:00:05 GMT" in original
    mutated = original.replace(b"20:00:05 GMT", b"20:00:04 GMT")
    assert len(mutated) == len(original)
    attempt_path.chmod(0o644)
    attempt_path.write_bytes(mutated)

    final = _token(reader, horizon, as_of)

    assert initial.ordered_member_keys
    assert final.ordered_member_keys
    assert initial != final


@pytest.mark.parametrize(
    "dependency",
    [
        "attempt",
        "attempt_run",
        "raw_origin_run",
        "envelope",
        "payload",
        "extraction",
        "observation_content",
    ],
)
def test_every_seed_dependency_changes_token_or_refuses_typed(
    tmp_path, dependency,
):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path, reuse=True)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    initial = _token(reader, horizon, as_of)
    envelope = store.get_envelope(seed.raw_record_id)

    paths = {
        "attempt": store.base_dir / "attempts" / f"{seed.attempt_id}.json",
        "attempt_run": store.base_dir / "runs" / f"{seed.ingestion_run_id}.json",
        "raw_origin_run": (
            store.base_dir / "runs" / f"{envelope.ingestion_run_id}.json"
        ),
        "envelope": store.base_dir / "envelopes" / f"{seed.raw_record_id}.json",
        "payload": (
            store.base_dir / "payloads"
            / envelope.payload_checksum.removeprefix("sha256:")
        ),
        "extraction": store.base_dir / "extracted" / f"{seed.raw_record_id}.json",
        "observation_content": (
            store.base_dir / "extracted" / f"{seed.raw_record_id}.json"
        ),
    }
    target = paths[dependency]
    if dependency == "observation_content":
        document = json.loads(target.read_text("utf-8"))
        observations = document["result"]["manifest"]["observations"]
        observation = next(
            row for row in observations
            if row["json_pointer"] == _scope().json_pointer
        )
        observation["value_json"] = "60.2"
        target.chmod(0o644)
        target.write_text(json.dumps(document), "utf-8")
    elif dependency == "payload":
        target.chmod(0o644)
        target.write_bytes(target.read_bytes() + b" ")
    else:
        _append_json_whitespace(target)

    try:
        final = _token(reader, horizon, as_of)
    except OperationalEvidenceReadError:
        return
    assert final != initial


def test_source_seed_candidate_replacement_changes_inventory_token(tmp_path):
    runner, store, transport, _, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    initial = _token(reader, horizon, as_of)
    transport.script["/printer/objects/query"] = fixture_response(
        "moonraker_printer_objects_changed.json")
    runner.run("printer-1")

    final = _token(reader, horizon, as_of)

    assert final != initial


def test_source_selected_seed_must_equal_temporal_supplied_seed(tmp_path):
    runner, store, transport, old_seed, horizon, as_of = _seed_world(tmp_path)
    transport.script["/printer/objects/query"] = fixture_response(
        "moonraker_printer_objects_changed.json")
    runner.run("printer-1")
    reader = FilesystemDs004OperationalEvidenceReader(store)

    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.read_material(
            _scope(), horizon_started_at=horizon, as_of=as_of,
            selected_seed_attempt_id=old_seed.attempt_id)

    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH"
    assert str(tmp_path) not in str(exc.value)


def test_missing_temporal_seed_refuses_when_source_requires_seed(tmp_path):
    _, store, _, _, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)

    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.read_material(
            _scope(), horizon_started_at=horizon, as_of=as_of,
            selected_seed_attempt_id=None)

    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH"


def test_named_material_unavailable_uses_accepted_reader_seam(tmp_path):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    material = reader.read_material(
        _scope(), horizon_started_at=horizon, as_of=as_of,
        selected_seed_attempt_id=seed.attempt_id)
    path = store.base_dir / "attempts" / f"{seed.attempt_id}.json"
    path.unlink()

    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.reread_named_material(material)

    assert exc.value.error_code == (
        "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE")
    assert str(tmp_path) not in str(exc.value)


@pytest.mark.parametrize("public_path", ["material", "inventory"])
@pytest.mark.parametrize("budget", ["artifacts", "metadata_bytes"])
def test_seed_and_horizon_closure_enforces_one_aggregate_budget(
    tmp_path, public_path, budget,
):
    store, seed, horizon, as_of = _seed_and_empty_horizon_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    ordinary = _capture(reader, seed, horizon, as_of)
    actual = (
        len(ordinary.artifacts)
        if budget == "artifacts"
        else sum(
            row.byte_count for row in ordinary.artifacts
            if row.kind != "raw_payload"
        )
    )
    constant = (
        "MAX_RETAINED_ARTIFACTS"
        if budget == "artifacts"
        else "MAX_RETAINED_METADATA_BYTES"
    )

    def invoke():
        if public_path == "material":
            return _capture(reader, seed, horizon, as_of)
        return reader.inventory_token(
            _scope(), horizon_started_at=horizon, as_of=as_of)

    with patch.object(operational_api, constant, actual):
        admitted = invoke()
        if public_path == "material":
            assert reader.reread_named_material(admitted) == admitted

    with patch.object(operational_api, constant, actual - 1):
        with pytest.raises(OperationalEvidenceReadError) as exc:
            invoke()
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED"
    assert str(tmp_path) not in str(exc.value)


def test_named_reread_equal_and_reads_each_named_artifact_once(
    tmp_path, monkeypatch,
):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path, reuse=True)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    material = _capture(reader, seed, horizon, as_of)
    observed_paths = []
    original = reader._read_bytes_once

    def recording_read(path, *, max_bytes=None):
        observed_paths.append(path)
        return original(path, max_bytes=max_bytes)

    monkeypatch.setattr(reader, "_read_bytes_once", recording_read)
    reread = reader.reread_named_material(material)

    assert reread == material
    assert len(observed_paths) == len(material.artifacts)
    assert set(Counter(observed_paths).values()) == {1}
    assert len(material.runs) == 2
    assert len(material.envelopes) == 1


@pytest.mark.parametrize("condition", ["changed", "substituted", "unsafe"])
def test_named_reread_refuses_changed_substituted_or_unsafe_material(
    tmp_path, condition,
):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path, reuse=True)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    material = _capture(reader, seed, horizon, as_of)
    target = store.base_dir / "attempts" / f"{seed.attempt_id}.json"
    target.chmod(0o644)
    if condition == "changed":
        target.write_bytes(target.read_bytes() + b" ")
    elif condition == "substituted":
        substitute = next(
            row for row in store.iter_attempts("printer-1")
            if row.item_key == "printer_objects"
            and row.attempt_id != seed.attempt_id
        )
        substitute_path = (
            store.base_dir / "attempts" / f"{substitute.attempt_id}.json"
        )
        target.write_bytes(substitute_path.read_bytes())
    else:
        original = target.with_suffix(".original")
        target.rename(original)
        target.symlink_to(original)

    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.reread_named_material(material)

    expected = (
        "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE"
        if condition == "unsafe"
        else "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH"
    )
    assert exc.value.error_code == expected
    assert str(tmp_path) not in str(exc.value)


def test_named_reread_ignores_unrelated_additions_and_current_capture_limit(
    tmp_path,
):
    runner, store, _, seed, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    frozen = _capture(reader, seed, horizon, as_of)
    runner.run("printer-1")
    runner.run("printer-1")

    with patch.object(operational_api, "MAX_IN_HORIZON_ATTEMPTS", 1):
        assert reader.reread_named_material(frozen) == frozen
        with pytest.raises(OperationalEvidenceReadError) as exc:
            reader.inventory_token(
                _scope(), horizon_started_at=frozen.attempts[-1].received_at,
                as_of=as_of + timedelta(days=1))
    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED"


def test_named_reread_rejects_forged_nested_material_before_io(
    tmp_path, monkeypatch,
):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    material = _capture(reader, seed, horizon, as_of)
    forged_descriptor = material.artifacts[0].model_copy(
        update={"byte_count": True})
    forged = material.model_copy(
        update={"artifacts": (forged_descriptor, *material.artifacts[1:])})
    reads = 0

    def forbidden_read(*args, **kwargs):
        nonlocal reads
        reads += 1
        raise AssertionError("filesystem access preceded reconstruction")

    monkeypatch.setattr(reader, "_read_bytes_once", forbidden_read)
    with pytest.raises(OperationalEvidenceReadError) as exc:
        reader.reread_named_material(forged)

    assert exc.value.error_code == "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH"
    assert reads == 0


def test_named_reread_has_no_write_or_network_effect(tmp_path, monkeypatch):
    _, store, _, seed, horizon, as_of = _seed_world(tmp_path)
    reader = FilesystemDs004OperationalEvidenceReader(store)
    material = _capture(reader, seed, horizon, as_of)
    before = {
        path.relative_to(store.base_dir): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in store.base_dir.rglob("*") if path.is_file()
    }

    def forbidden_socket(*args, **kwargs):
        raise AssertionError("named reread attempted network access")

    monkeypatch.setattr(socket, "socket", forbidden_socket)
    assert reader.reread_named_material(material) == material
    after = {
        path.relative_to(store.base_dir): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in store.base_dir.rglob("*") if path.is_file()
    }
    assert after == before
