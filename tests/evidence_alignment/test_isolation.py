"""C30-C38 reconstruction, no-I/O, import, and determinism guards."""

from __future__ import annotations

import ast
import builtins
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from tests.evidence_alignment.helpers import align, alignment_api, build_world


COVERED_ROWS = {
    "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38",
}


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    return build_world(tmp_path_factory.mktemp("alignment-isolation"))


def test_c34_c36_derivation_performs_no_io_or_reselection(world, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("I/O or reselection occurred")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(
        "backend.evidence_assurance.EvidenceAssuranceQueries.select_operational_evidence",
        forbidden,
    )
    monkeypatch.setattr(
        "backend.evidence_assurance.EvidenceAssuranceQueries.revalidate_operational_evidence",
        forbidden,
    )
    result = align(world)
    assert result.status == "aligned_with_complete_evidence"


def test_c35_import_direction_and_authorized_c2_exports():
    package_root = Path("backend/evidence_alignment")
    existing_roots = [
        path for path in Path("backend").glob("*/**/*.py")
        if package_root not in path.parents
    ]
    assert all(
        "backend.evidence_alignment" not in path.read_text(encoding="utf-8")
        for path in existing_roots
    )

    forbidden = {
        "backend.data_sources.evidence",
        "backend.temporal_state.queries",
        "backend.evidence_assurance.queries",
        "backend.observation_compatibility.facade",
    }
    for path in package_root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not imports & forbidden

    import backend.evidence_alignment as package
    assert package.__all__ == [
        "EvidenceAlignmentError",
        "EvidenceAlignmentQueryError",
        "EvidenceAlignmentQueryErrorCode",
        "OperationalEvidenceAlignmentStatus",
        "OperationalEvidenceAlignmentReason",
        "OperationalEvidenceAlignmentExpectedFingerprintRelation",
        "OperationalEvidenceAlignmentRequest",
        "OperationalEvidenceAlignmentResult",
        "align_operational_evidence_with_value_compatibility",
    ]


def test_c37_serialized_construction_order_is_deterministic(world):
    api = alignment_api()
    plain = {
        "schema_version": "1",
        "selection": world.selection.model_dump(mode="python", warnings=False),
        "compatibility": world.compatibility.model_dump(
            mode="python", warnings=False),
        "expected_snapshot_fingerprint": None,
    }

    def reverse(value):
        if isinstance(value, dict):
            return {key: reverse(value[key]) for key in reversed(value)}
        if isinstance(value, list):
            return [reverse(item) for item in value]
        return value

    first = api["align"](plain)
    second = api["align"](reverse(plain))
    assert first == second
    assert json.loads(first.model_dump_json()) == json.loads(
        second.model_dump_json())


def test_c37_hash_seed_processes_are_deterministic():
    script = """
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.evidence_alignment.helpers import align, build_world
with TemporaryDirectory(prefix='ea001-c1-seed-') as temporary:
    result = align(build_world(Path(temporary)))
print(result.model_dump_json())
"""
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ)
        environment.update({
            "PYTHONHASHSEED": seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(), env=environment,
            check=True, capture_output=True, text=True,
        )
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1] == outputs[2]


def test_c22_validator_is_called_once_for_non_refused_selection(
    world, monkeypatch,
):
    import backend.evidence_alignment.derivation as derivation

    calls = []
    wrapped = derivation.validate_operational_evidence_snapshot

    def counted(*args, **kwargs):
        calls.append((args, kwargs))
        return wrapped(*args, **kwargs)

    monkeypatch.setattr(
        derivation, "validate_operational_evidence_snapshot", counted)
    assert align(world).status == "aligned_with_complete_evidence"
    assert len(calls) == 1
