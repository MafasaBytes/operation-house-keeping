"""EA-001 Slice A integrity-repair regressions.

These tests preserve the exact preimplementation discrepancy: a pre-horizon
source seed and its closure were absent from both source fence tokens.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from backend.data_sources.contracts import OperationalEvidenceReadError
from backend.data_sources.evidence import FilesystemDs004OperationalEvidenceReader

from tests.data_sources.test_ea001_operational_evidence_reader import _scope
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
