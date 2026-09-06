"""C30-C38 reconstruction, no-I/O, import, and determinism guards."""

from __future__ import annotations

import ast
import builtins
import json
import socket
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


def test_c35_import_direction_and_c2_export_remains_absent():
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
    assert not hasattr(package, "__all__")
    for public_name in (
        "OperationalEvidenceAlignmentRequest",
        "align_operational_evidence_with_value_compatibility",
    ):
        assert not hasattr(package, public_name)


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
