"""Bounded C1 expected-fingerprint relation integrity regression."""

from __future__ import annotations

from typing import get_args

import pytest
from pydantic import ValidationError

from backend.evidence_assurance import (
    OperationalEvidenceIssue,
    OperationalEvidenceSelectionResult,
)

from tests.evidence_alignment.helpers import align, alignment_api, build_world


PLANNED_C2_EXPORTS = [
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
    return build_world(tmp_path_factory.mktemp("alignment-fingerprint-repair"))


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


@pytest.mark.parametrize(
    ("refused", "expected_kind", "relation"),
    [
        (True, "exact", "not_evaluated"),
        (True, "absent", "not_supplied"),
        (False, "exact", "matched"),
        (False, "different", "mismatched"),
    ],
)
def test_expected_fingerprint_relation_is_exact_and_reconstructable(
    world, refused, expected_kind, relation,
):
    api = alignment_api()
    selection = _refused_selection(world) if refused else world.selection
    expected = {
        "absent": None,
        "exact": world.selection.snapshot.content_fingerprint,
        "different": "sha256:" + "0" * 64,
    }[expected_kind]

    result = align(world, selection=selection, expected=expected)
    assert result.expected_fingerprint_relation == relation

    plain = result.model_dump(mode="python", warnings=False)
    reconstructed = api["OperationalEvidenceAlignmentResult"].model_validate(plain)
    assert reconstructed == result
    forged = dict(plain)
    forged["expected_fingerprint_relation"] = (
        "matched" if relation != "matched" else "mismatched"
    )
    with pytest.raises(ValidationError):
        api["OperationalEvidenceAlignmentResult"].model_validate(forged)


def test_relation_literal_and_authorized_c2_surface_are_exact():
    import backend.evidence_alignment as package
    import backend.evidence_alignment.contracts as contracts

    relation = getattr(
        contracts,
        "OperationalEvidenceAlignmentExpectedFingerprintRelation",
        None,
    )
    assert get_args(relation) == (
        "matched",
        "mismatched",
        "not_supplied",
        "not_evaluated",
    )
    assert PLANNED_C2_EXPORTS == [
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
    assert package.__all__ == PLANNED_C2_EXPORTS
    assert all(hasattr(package, name) for name in PLANNED_C2_EXPORTS)


def test_snapshot_validator_call_count_remains_zero_or_one(world, monkeypatch):
    import backend.evidence_alignment.derivation as derivation

    calls = []
    wrapped = derivation.validate_operational_evidence_snapshot

    def counted(*args, **kwargs):
        calls.append((args, kwargs))
        return wrapped(*args, **kwargs)

    monkeypatch.setattr(
        derivation,
        "validate_operational_evidence_snapshot",
        counted,
    )
    refused = _refused_selection(world)
    assert align(world, selection=refused).reason == "selection_refused"
    assert calls == []

    assert align(world).status == "aligned_with_complete_evidence"
    assert len(calls) == 1
