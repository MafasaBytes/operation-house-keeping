"""TA-001 leaf dependency and no-I/O proofs."""

from __future__ import annotations

import ast
import builtins
import socket
import sqlite3
import time
from pathlib import Path

from backend.transition_assessment import (
    DeclaredTransitionAssessmentResult,
    assess_declared_transition_endpoints,
)

from tests.transition_assessment.helpers import build_world


ROOT = Path("backend/transition_assessment")


def test_package_imports_only_exact_public_lower_roots():
    allowed = {
        "backend.model_kernel",
        "backend.state_classification",
        "backend.evidence_alignment",
    }
    for path in ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("backend.")
        }
        imported.update(
            alias.name for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name.startswith("backend.")
        )
        assert imported <= allowed, (path, imported - allowed)


def test_no_existing_backend_package_imports_transition_assessment():
    offenders = []
    for path in Path("backend").glob("**/*.py"):
        if ROOT in path.parents:
            continue
        if "backend.transition_assessment" in path.read_text(encoding="utf-8"):
            offenders.append(path)
    assert offenders == []


def test_assessment_and_result_validation_perform_no_io_or_orchestration(
    tmp_path, monkeypatch,
):
    world = build_world(tmp_path)
    request = world.request.model_dump(mode="python", warnings=False)
    expected = assess_declared_transition_endpoints(world.request)
    raw_result = expected.model_dump(mode="python", warnings=False)

    for owner, name in (
        (builtins, "open"),
        (Path, "open"),
        (Path, "read_bytes"),
        (Path, "read_text"),
        (Path, "write_bytes"),
        (Path, "write_text"),
        (time, "time"),
        (time, "monotonic"),
        (socket, "socket"),
        (socket, "create_connection"),
        (sqlite3, "connect"),
    ):
        def forbidden(*args, _name=name, **kwargs):
            raise AssertionError(f"forbidden side effect: {_name}")

        monkeypatch.setattr(owner, name, forbidden)

    for dependency in (world.source, world.temporal, world.model):
        for name in (
            "inventory_token", "read_material", "reread_named_material",
            "captured_material", "transaction", "load", "append",
        ):
            if hasattr(dependency, name):
                monkeypatch.setattr(dependency, name, forbidden)

    result = assess_declared_transition_endpoints(request)
    rebuilt = DeclaredTransitionAssessmentResult.model_validate(raw_result)
    assert result == rebuilt == expected


def test_package_owns_no_facade_store_identity_demo_or_artifact_path():
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in ROOT.glob("*.py")
    ).lower()
    for forbidden in (
        "class transitionassessmentqueries",
        "class transitionassessmentfacade",
        "sqlite3",
        "socket",
        "modelstore",
        "temporalstore",
        "evidenceassurancequeries",
        "os.getenv",
        "time.time",
        "time.sleep",
        "fixtures/",
        "artifacts/",
    ):
        assert forbidden not in text
