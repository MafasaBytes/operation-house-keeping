"""EA-001 Slice C2 exact root surface and final preservation gates."""

from __future__ import annotations

import ast
import builtins
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from types import ModuleType

import pytest
from pydantic import ValidationError

from backend.evidence_assurance import (
    OperationalEvidenceIssue,
    OperationalEvidenceSelectionResult,
)
from backend.model_kernel.store import ModelStore
from tests.evidence_alignment.helpers import (
    AS_OF,
    V1,
    build_world,
    consumer_without_observation,
    differing_scope_consumer,
    duplicate_consumer,
    mutate_consumer_occurrence,
    no_observation_selection,
    pre_horizon_pair,
)
from tests.model_kernel.st001_slice_d_rehearsal import inventory_digest


EXPECTED_EXPORTS = [
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


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    return build_world(tmp_path_factory.mktemp("alignment-c2-public"))


def _api():
    return importlib.import_module("backend.evidence_alignment")


def _align(world, *, selection=None, consumer=None, expected=None):
    api = _api()
    request = api.OperationalEvidenceAlignmentRequest(
        schema_version="1",
        selection=world.selection if selection is None else selection,
        compatibility=world.compatibility if consumer is None else consumer,
        expected_snapshot_fingerprint=expected,
    )
    return api.align_operational_evidence_with_value_compatibility(request)


def _refused_selection(world):
    return OperationalEvidenceSelectionResult(
        status="refused",
        request=world.selection.request,
        snapshot=None,
        issues=(
            OperationalEvidenceIssue(
                code="invalid_bounded_material",
                detail_code="test_refusal",
                route_index=None,
                detail="test refusal is structured",
            ),
        ),
    )


def test_c39_root_all_is_exact_ordered_unique_and_defining_objects():
    api = _api()
    contracts = importlib.import_module("backend.evidence_alignment.contracts")
    derivation = importlib.import_module("backend.evidence_alignment.derivation")

    assert api.__all__ == EXPECTED_EXPORTS
    assert len(api.__all__) == len(set(api.__all__)) == 9
    for name in EXPECTED_EXPORTS[:-1]:
        assert getattr(api, name) is getattr(contracts, name)
    assert getattr(api, EXPECTED_EXPORTS[-1]) is getattr(
        derivation, EXPECTED_EXPORTS[-1]
    )

    visible_nonmodules = {
        name
        for name, value in vars(api).items()
        if not name.startswith("_") and not isinstance(value, ModuleType)
    }
    assert visible_nonmodules == set(EXPECTED_EXPORTS)
    for forbidden in (
        "ExpectedFingerprintRelation",
        "OperationalEvidenceSelectionResult",
        "OperationalEvidenceSnapshotValidationResult",
        "VariableValueCompatibilityResult",
        "EvidenceAssuranceQueries",
        "TemporalOccurrence",
    ):
        assert not hasattr(api, forbidden)


def test_c39_root_import_is_pure_and_import_direction_stays_one_way(monkeypatch):
    source = Path("backend/evidence_alignment/__init__.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert modules == {
        "backend.evidence_alignment.contracts",
        "backend.evidence_alignment.derivation",
    }
    forbidden_text = (
        "EvidenceAssuranceQueries",
        "TemporalQueries",
        "FilesystemDs004OperationalEvidenceReader",
        "sqlite3",
        "connect(",
        "open(",
        "socket",
        "datetime.now",
        "datetime.utcnow",
    )
    assert all(token not in source for token in forbidden_text)

    import backend.evidence_alignment.contracts  # noqa: F401
    import backend.evidence_alignment.derivation  # noqa: F401

    sys.modules.pop("backend.evidence_alignment", None)

    def forbidden(*args, **kwargs):
        raise AssertionError("root import performed I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    reloaded = importlib.import_module("backend.evidence_alignment")
    assert reloaded.__all__ == EXPECTED_EXPORTS

    root = Path("backend/evidence_alignment")
    authorized_upper = Path("backend/transition_assessment")
    lower_files = [
        path for path in Path("backend").glob("*/**/*.py")
        if root not in path.parents and authorized_upper not in path.parents
    ]
    assert all(
        "backend.evidence_alignment" not in path.read_text(encoding="utf-8")
        for path in lower_files
    )


def test_c39_every_status_and_reason_round_trips_through_root(world):
    from datetime import timedelta

    refused = _refused_selection(world)
    incomplete_selection, incomplete_consumer = pre_horizon_pair(world)
    different_cutoff = world.consumer_queries.variable_value_compatibility(
        V1, as_of=AS_OF + timedelta(seconds=1)
    )
    results = (
        _align(world),
        _align(
            world,
            selection=incomplete_selection,
            consumer=incomplete_consumer,
        ),
        _align(world, selection=refused),
        _align(world, expected="sha256:" + "0" * 64),
        _align(world, selection=no_observation_selection(world)),
        _align(world, consumer=different_cutoff),
        _align(world, consumer=differing_scope_consumer(world, "source_id")),
        _align(world, consumer=consumer_without_observation(world.compatibility)),
        _align(
            world,
            consumer=mutate_consumer_occurrence(
                world.compatibility, {"value_json": "61.0"}
            ),
        ),
        _align(
            world,
            consumer=mutate_consumer_occurrence(
                world.compatibility, {"occurrence_id": "other-occurrence"}
            ),
        ),
        _align(world, consumer=duplicate_consumer(world.compatibility)),
    )
    assert {result.status for result in results} == {
        "aligned_with_complete_evidence",
        "aligned_with_incomplete_evidence",
        "not_aligned",
        "not_evaluated",
    }
    assert {result.reason for result in results} == {
        None,
        "selection_refused",
        "snapshot_fingerprint_mismatched",
        "no_selected_observation",
        "cutoff_differs",
        "scope_differs",
        "consumer_observation_absent",
        "occurrence_content_mismatch",
        "occurrence_absent_from_consumer_result",
        "multiple_matching_candidates",
    }
    api = _api()
    for result in results:
        plain = result.model_dump(mode="python", warnings=False)
        assert api.OperationalEvidenceAlignmentResult.model_validate(plain) == result


def test_c39_public_result_rejects_forged_derived_fields(world):
    api = _api()
    plain = _align(world).model_dump(mode="python", warnings=False)
    for field, forged in (
        ("status", "not_aligned"),
        ("aligned_candidate_index", 1),
        ("expected_fingerprint_relation", "mismatched"),
        ("model_revision_id", "mrv_" + "0" * 64),
    ):
        payload = dict(plain)
        payload[field] = forged
        with pytest.raises(ValidationError):
            api.OperationalEvidenceAlignmentResult.model_validate(payload)


def test_c39_refused_expected_fingerprint_relations_remain_truthful(world):
    refused = _refused_selection(world)
    supplied = _align(
        world,
        selection=refused,
        expected=world.selection.snapshot.content_fingerprint,
    )
    absent = _align(world, selection=refused)
    assert (
        supplied.status,
        supplied.reason,
        supplied.snapshot_validation,
        supplied.expected_fingerprint_relation,
    ) == ("not_evaluated", "selection_refused", None, "not_evaluated")
    assert absent.expected_fingerprint_relation == "not_supplied"


def test_c39_root_serialization_is_construction_order_independent(world):
    api = _api()
    result = _align(world)
    plain = result.request.model_dump(mode="python", warnings=False)

    def reverse(value):
        if type(value) is dict:
            return {key: reverse(value[key]) for key in reversed(value)}
        if type(value) is list:
            return [reverse(item) for item in value]
        return value

    rebuilt = api.OperationalEvidenceAlignmentRequest.model_validate(
        reverse(plain)
    )
    second = api.align_operational_evidence_with_value_compatibility(rebuilt)
    assert second.model_dump_json() == result.model_dump_json()


def test_c39_root_serialization_is_hash_seed_independent():
    script = """
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import backend.evidence_alignment as api
from tests.evidence_alignment.helpers import build_world, pre_horizon_pair
with TemporaryDirectory(prefix='ea001-c2-seed-') as temporary:
    world = build_world(Path(temporary))
    complete = api.align_operational_evidence_with_value_compatibility(
        api.OperationalEvidenceAlignmentRequest(
            schema_version='1', selection=world.selection,
            compatibility=world.compatibility,
            expected_snapshot_fingerprint=None))
    selection, consumer = pre_horizon_pair(world)
    incomplete = api.align_operational_evidence_with_value_compatibility(
        api.OperationalEvidenceAlignmentRequest(
            schema_version='1', selection=selection,
            compatibility=consumer,
            expected_snapshot_fingerprint=None))
    data = (complete.model_dump_json() + '\\n' +
            incomplete.model_dump_json()).encode()
    print(len(data), hashlib.sha256(data).hexdigest())
"""
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ)
        environment.update({
            "PYTHONHASHSEED": seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path.cwd(),
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        outputs.append(completed.stdout.strip())
    assert outputs[0] == outputs[1] == outputs[2]


def test_c40_frozen_model_artifacts_ea_and_c1_documents_are_preserved():
    expected_documents = {
        Path("docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md"):
            "557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e",
        Path("docs/superpowers/proposals/2026-09-06-ea001-slice-c-integration-proposal.md"):
            "829435ba1f6bff6a27daf1aeb6f1c654257fd20afc4e831c13a7f90478436812",
        Path("docs/superpowers/reports/2026-09-06-ea001-slice-c1-completion-report.md"):
            "cb32954e76e5b4fcdb718a20f1af2f072fd9a7743d7b577a09700db3edc8b031",
        Path("docs/superpowers/reports/2026-09-07-ea001-slice-c1-integrity-repair-report.md"):
            "bdb4ec72c00f2dde1578424c33aa22389d52cf7d90e788d5bb534ec8a07823c7",
        Path("docs/superpowers/reports/2026-09-07-ea001-slice-c2-preimplementation-discrepancy-report.md"):
            "0ce93f6951d89cc563b530d2683f8a7b743a6e144182684159801923bbdeeb29",
    }
    for path, digest in expected_documents.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    historical = subprocess.check_output(
        [
            "git",
            "show",
            "c94b5629bea928e976779be6cb4cf035264dc88d:docs/superpowers/reports/2026-09-06-ea001-slice-c1-completion-report.md",
        ],
        cwd=Path.cwd(),
    )
    assert len(historical) == 13898
    assert hashlib.sha256(historical).hexdigest() == (
        "5c728116fbc458352d9ce7967d3286ce96ce82991e678d1a3469306fb52310e6"
    )

    record_paths = sorted(Path("models/demo-printer/records").glob("*.json"))
    inventory = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in record_paths
    }
    loaded = ModelStore(Path("models/demo-printer")).load()
    assert len(record_paths) == loaded.revision.record_count == 36
    assert loaded.revision.revision_id == (
        "mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee"
    )
    assert inventory_digest(inventory) == (
        "bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a"
    )
    assert sum(path.name.startswith("frg_") for path in record_paths) == 1
    assert sum(path.name.startswith("fld_") for path in record_paths) == 1
    assert sum(path.name.startswith("flw_") for path in record_paths) == 0

    disclosure = Path(
        "docs/superpowers/reports/2026-09-03-fl001-slice-d-candidate-disclosure.json"
    ).read_bytes()
    assert len(disclosure) == 660516
    assert hashlib.sha256(disclosure).hexdigest() == (
        "096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b"
    )
