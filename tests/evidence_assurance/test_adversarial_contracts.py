"""Adversarial EA-001 Slice B contract and isolation regressions."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.evidence_assurance import (
    CapturedOperationalEvidenceSnapshot,
    EvidenceAssuranceQueries,
    OperationalEvidenceSelectionResult,
)

from tests.evidence_assurance.test_selection import _captured_world, _request


EA_ROOT = Path("backend/evidence_assurance")


def _snapshot(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    return EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request()).snapshot


def test_dependency_imports_are_only_exact_approved_public_modules():
    allowed = {
        "backend.data_sources.contracts.operational_evidence",
        "backend.temporal_state.contracts",
        "backend.evidence_assurance.contracts",
        "backend.evidence_assurance.queries",
    }
    observed = set()
    for path in EA_ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module.startswith("backend."):
                observed.add(node.module)
            elif isinstance(node, ast.Import):
                observed.update(
                    alias.name for alias in node.names
                    if alias.name.startswith("backend."))
    assert observed <= allowed
    assert "backend.data_sources.contracts" not in observed


def test_no_existing_backend_consumer_imports_evidence_assurance():
    offenders = []
    for path in Path("backend").rglob("*.py"):
        if EA_ROOT in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        if "backend.evidence_assurance" in text:
            offenders.append(path.as_posix())
    assert offenders == []


def test_exact_facade_method_parameter_names_and_annotations():
    init = inspect.signature(EvidenceAssuranceQueries.__init__)
    assert tuple(init.parameters) == ("self", "source", "temporal")
    assert init.parameters["source"].kind is inspect.Parameter.KEYWORD_ONLY
    assert init.parameters["temporal"].kind is inspect.Parameter.KEYWORD_ONLY
    assert init.parameters["source"].annotation is not inspect.Parameter.empty
    assert init.parameters["temporal"].annotation is not inspect.Parameter.empty
    assert init.return_annotation is not inspect.Signature.empty

    select = inspect.signature(EvidenceAssuranceQueries.select_operational_evidence)
    assert tuple(select.parameters) == ("self", "request")
    assert select.parameters["request"].annotation is not inspect.Parameter.empty
    assert select.return_annotation is not inspect.Signature.empty

    revalidate = inspect.signature(
        EvidenceAssuranceQueries.revalidate_operational_evidence)
    assert tuple(revalidate.parameters) == ("self", "snapshot", "membership_mode")
    assert revalidate.parameters["membership_mode"].kind is (
        inspect.Parameter.KEYWORD_ONLY)
    assert all(parameter.annotation is not inspect.Parameter.empty
               for parameter in tuple(revalidate.parameters.values())[1:])
    assert revalidate.return_annotation is not inspect.Signature.empty


def test_direct_snapshot_reconstruction_rejects_stale_derivation_and_digest(
    tmp_path,
):
    snapshot = _snapshot(tmp_path)
    stale = snapshot.model_dump(mode="python")
    stale["coverage"]["property_observed_route_indices"] = []
    with pytest.raises(ValidationError):
        CapturedOperationalEvidenceSnapshot.model_validate(stale)

    wrong_digest = snapshot.model_dump(mode="python")
    wrong_digest["content_fingerprint"] = "sha256:" + "0" * 64
    with pytest.raises(ValidationError):
        CapturedOperationalEvidenceSnapshot.model_validate(wrong_digest)


def test_direct_result_reconstruction_rejects_substituted_nested_snapshot(tmp_path):
    snapshot = _snapshot(tmp_path)
    result = OperationalEvidenceSelectionResult(
        status="complete_within_declared_horizon", request=snapshot.request,
        snapshot=snapshot, issues=())
    hostile = result.model_dump(mode="python")
    hostile["snapshot"]["selected"]["observation_age_seconds"] = "0"
    with pytest.raises(ValidationError):
        OperationalEvidenceSelectionResult.model_validate(hostile)
