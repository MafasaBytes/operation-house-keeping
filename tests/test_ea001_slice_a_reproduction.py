"""Cross-seam parity and deterministic Slice A material reproduction."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import UTC, datetime

from backend.data_sources.contracts import Ds004OperationalEvidenceScope
from backend.data_sources.evidence import FilesystemDs004OperationalEvidenceReader
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import (
    fixture_response,
    happy_script,
    make_runner,
)


def _scope():
    return Ds004OperationalEvidenceScope(
        source_id="printer-1", adapter_id="moonraker",
        endpoint_id="printer_objects_query", item_key="printer_objects",
        subject_identifier="extruder", extraction_route="api:moonraker:v1",
        json_pointer="/result/status/extruder/temperature")


def _captured_lower_material(tmp_path):
    runner, raw, transport = make_runner(tmp_path / "raw", happy_script())
    runner.run("printer-1")
    transport.script["/printer/objects/query"] = fixture_response(
        "moonraker_printer_objects_changed.json")
    runner.run("printer-1")
    temporal = TemporalStore(tmp_path / "temporal.db", evidence_root=raw.base_dir)
    TemporalProjector(raw, temporal).project("printer-1")
    horizon = datetime(2026, 8, 7, 19, 0, tzinfo=UTC)
    as_of = datetime(2026, 8, 7, 21, 0, tzinfo=UTC)
    temporal_material = TemporalQueries(temporal).selection_material(
        _scope(), horizon_started_at=horizon, as_of=as_of)
    seed = None
    if temporal_material.selected_occurrence_is_pre_horizon_seed:
        seed = temporal_material.occurrence_membership[
            temporal_material.selected_occurrence_index].attempt_id
    source_material = FilesystemDs004OperationalEvidenceReader(raw).read_material(
        _scope(), horizon_started_at=horizon, as_of=as_of,
        selected_seed_attempt_id=seed)
    return source_material, temporal_material


def test_source_and_temporal_lower_material_have_exact_parity(tmp_path):
    source, temporal = _captured_lower_material(tmp_path)
    assert tuple(row.attempt_id for row in source.attempts) == tuple(
        row.attempt_id for row in temporal.attempt_coverage_membership)
    source_observations = {row.observation_id: row for row in source.observations}
    for occurrence in temporal.occurrence_membership:
        observation = source_observations[occurrence.observation_id]
        assert (
            observation.raw_record_id,
            observation.value_json,
            observation.json_type,
            observation.source_time,
        ) == (
            occurrence.raw_record_id,
            occurrence.value_json,
            occurrence.json_type,
            occurrence.source_time,
        )


def test_serialized_lower_material_is_hash_seed_independent(tmp_path):
    source, temporal = _captured_lower_material(tmp_path)
    source_path = tmp_path / "source.json"
    temporal_path = tmp_path / "temporal.json"
    source_path.write_text(source.model_dump_json(), "utf-8")
    temporal_path.write_text(temporal.model_dump_json(), "utf-8")
    script = """
import hashlib
import sys
from backend.data_sources.contracts import Ds004OperationalEvidenceMaterial
from backend.temporal_state.contracts import TemporalSelectionMaterial
s = Ds004OperationalEvidenceMaterial.model_validate_json(open(sys.argv[1], encoding='utf-8').read())
t = TemporalSelectionMaterial.model_validate_json(open(sys.argv[2], encoding='utf-8').read())
data = (s.model_dump_json() + '\\n' + t.model_dump_json()).encode()
print(hashlib.sha256(data).hexdigest())
"""
    digests = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = seed
        digests.append(subprocess.check_output(
            [sys.executable, "-c", script, str(source_path), str(temporal_path)],
            cwd=os.getcwd(), env=environment, text=True).strip())
    expected = hashlib.sha256((
        source.model_dump_json() + "\n" + temporal.model_dump_json()
    ).encode()).hexdigest()
    assert digests == [expected, expected, expected]
