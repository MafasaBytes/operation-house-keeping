"""Adversarial EA-001 Slice B contract and isolation regressions."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.evidence_assurance as ea
from backend.evidence_assurance import (
    CapturedOperationalEvidenceSnapshot,
    EvidenceAssuranceQueries,
    OperationalEvidenceSelectionResult,
)
from backend.data_sources.contracts.operational_evidence import (
    OperationalApiInventoryToken,
)

from tests.evidence_assurance.test_selection import _captured_world, _request


EA_ROOT = Path("backend/evidence_assurance")
ALIGNMENT_ROOT = Path("backend/evidence_alignment")


def _snapshot(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    return EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request()).snapshot


def test_dependency_imports_are_only_exact_approved_public_modules():
    allowed = {
        "backend.data_sources.contracts.operational_evidence",
        "backend.data_sources.evidence",
        "backend.temporal_state.contracts",
        "backend.temporal_state.queries",
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


def test_no_unauthorized_backend_consumer_imports_evidence_assurance():
    offenders = []
    for path in Path("backend").rglob("*.py"):
        if EA_ROOT in path.parents or ALIGNMENT_ROOT in path.parents:
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


def test_forged_lower_inventory_tokens_are_reconstructed_before_use(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)

    class ForgedSourceToken:
        def inventory_token(self, *args, **kwargs):
            token = source.inventory_token(*args, **kwargs)
            return OperationalApiInventoryToken.model_construct(
                **token.model_dump(
                    mode="python",
                    exclude={"ordered_member_keys"},
                    warnings=False),
                ordered_member_keys=tuple(reversed(token.ordered_member_keys)))
        def read_material(self, *args, **kwargs):
            return source.read_material(*args, **kwargs)
        def reread_named_material(self, expected_material):
            return source.reread_named_material(expected_material)

    result = EvidenceAssuranceQueries(
        source=ForgedSourceToken(), temporal=temporal,
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert tuple(issue.code for issue in result.issues) == (
        "invalid_bounded_material",)


def test_every_public_model_rejects_hidden_extra_content(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    facade = EvidenceAssuranceQueries(source=source, temporal=temporal)
    selection = facade.select_operational_evidence(_request())
    snapshot = selection.snapshot
    store_result = facade.revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    validation = ea.validate_operational_evidence_snapshot(snapshot)
    issue = ea.OperationalEvidenceIssue(
        code="invalid_bounded_material", detail_code="invalid_material",
        route_index=None, detail="bounded material is invalid")
    instances = (
        snapshot.request.policy,
        snapshot.request,
        snapshot.fixed_limits,
        issue,
        snapshot.provenance_routes[0],
        snapshot.coverage,
        snapshot.selected,
        snapshot.capture_fence,
        snapshot.assurance,
        snapshot,
        store_result.named_artifact_results[0],
        selection,
        store_result,
        validation,
    )
    assert {type(value).__name__ for value in instances} == {
        "OperationalEvidenceSelectionPolicy",
        "OperationalEvidenceSelectionRequest",
        "OperationalEvidenceMaterialLimits",
        "OperationalEvidenceIssue",
        "OperationalProvenanceRoute",
        "OperationalCoverageSummary",
        "SelectedSourceObservation",
        "CapturedViewFence",
        "OperationalEvidenceAssurance",
        "CapturedOperationalEvidenceSnapshot",
        "OperationalNamedArtifactRevalidation",
        "OperationalEvidenceSelectionResult",
        "OperationalEvidenceStoreRevalidationResult",
        "OperationalEvidenceSnapshotValidationResult",
    }
    for value in instances:
        plain = value.model_dump(mode="python", warnings=False)
        plain["hidden_extra"] = "forged"
        with pytest.raises(ValidationError):
            type(value).model_validate(plain)


def test_runtime_has_no_forbidden_io_or_upper_layer_dependencies():
    forbidden_modules = {
        "os", "pathlib", "socket", "subprocess", "requests", "urllib",
        "backend.data_sources.connectors", "backend.data_sources.extractors",
        "backend.data_sources.raw_store", "backend.temporal_state.store",
        "backend.identity_binding", "backend.source_interpretation",
        "backend.model_kernel", "backend.model_state",
        "backend.observation_compatibility", "backend.semantic_compatibility",
        "backend.constraint_evaluation", "backend.behavior_evaluation",
        "backend.state_classification",
    }
    forbidden_calls = {"open", "getenv", "putenv", "write", "connect"}
    observed_modules = set()
    observed_calls = set()
    for path in EA_ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                observed_modules.add(node.module)
            elif isinstance(node, ast.Import):
                observed_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    observed_calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    observed_calls.add(node.func.attr)
    assert not any(
        module == forbidden or module.startswith(forbidden + ".")
        for module in observed_modules for forbidden in forbidden_modules)
    assert observed_calls.isdisjoint(forbidden_calls)
    assert "now" not in observed_calls
    assert "utcnow" not in observed_calls


ACCEPTANCE_MATRIX = {
    f"A{index:02d}": evidence for index, evidence in enumerate((
        "source closure and deterministic selection",
        "same-read checksum matching",
        "payload replacement and named reread",
        "metadata and seed fence binding",
        "provenance closure",
        "extraction wrapper validation",
        "incomplete extraction refusal",
        "same-read metadata hashing",
        "RFC 6901 pointer handling",
        "exact pointer value and type",
        "malformed JSON refusal",
        "six distinct coverage dispositions",
        "source attempt absent from temporal",
        "temporal attempt substitution",
        "attempt and observation parity sets",
        "inclusive cutoff",
        "complete AttemptOrderKey",
        "receipt and effective axes separated",
        "finished_at no-response coverage",
        "source time disclosure only",
        "no cross-clock API and fixed policy",
        "reused payload distinct occurrences",
        "one pre-horizon seed",
        "seed excluded from attempt coverage",
        "exact no-observation result",
        "bounded horizon beyond lifetime 4096",
        "in-horizon limit refusal",
        "bounds before retained allocation",
        "unsafe entry and redaction refusal",
        "pre-initial captured view",
        "source mutation after initial fence",
        "source mutation during named read",
        "source mutation before final fence",
        "temporal mutation during transaction",
        "temporal mutation before final fence",
        "crossed source and temporal mutation",
        "post-final limitation",
        "unsupported file evidence",
        "import isolation",
        "exact contracts exports and fields",
        "age disclosure without judgment",
        "incomplete horizon coverage",
        "source versus temporal unavailability",
        "separate occurrence and coverage axes",
        "hostile reconstruction",
        "snapshot and fingerprint replacement",
        "independent expected fingerprint",
        "store-independent no-I/O validation",
        "deterministic serialization",
        "no network write clock or environment discovery",
    ), start=1)
}


def test_a01_a50_acceptance_matrix_has_no_missing_or_extra_rows():
    assert tuple(ACCEPTANCE_MATRIX) == tuple(
        f"A{index:02d}" for index in range(1, 51))
    assert all(ACCEPTANCE_MATRIX.values())


def test_direct_result_models_reject_impossible_status_relation_combinations(
    tmp_path,
):
    _, _, source, temporal = _captured_world(tmp_path)
    facade = EvidenceAssuranceQueries(source=source, temporal=temporal)
    snapshot = facade.select_operational_evidence(_request()).snapshot
    store_result = facade.revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    forged_store = store_result.model_dump(mode="python")
    forged_store["named_source_material_relation"] = "not_evaluated"
    forged_store["named_artifact_results"] = []
    with pytest.raises(ValidationError):
        ea.OperationalEvidenceStoreRevalidationResult.model_validate(forged_store)

    validation = ea.validate_operational_evidence_snapshot(snapshot)
    forged_validation = validation.model_dump(mode="python")
    forged_validation["embedded_fingerprint_relation"] = "mismatched"
    with pytest.raises(ValidationError):
        ea.OperationalEvidenceSnapshotValidationResult.model_validate(
            forged_validation)
