"""EA-001 source/temporal parity and issue-vocabulary regressions."""

from __future__ import annotations

from datetime import timedelta

import pytest

from backend.evidence_assurance import EvidenceAssuranceQueries
from backend.evidence_assurance.queries import _temporal_token_from_material
from backend.temporal_state.contracts import (
    TemporalSelectionMaterial,
    temporal_selection_digest,
)

from tests.evidence_assurance.test_selection import (
    _captured_world,
    _request,
)


def _rebuild(material, mutate):
    plain = material.model_dump(
        mode="python", exclude={"transaction_membership_sha256"},
        warnings=False)
    mutate(plain)
    plain["transaction_membership_sha256"] = temporal_selection_digest(plain)
    return TemporalSelectionMaterial.model_validate(plain)


class _FixedTemporalView:
    def __init__(self, material):
        self.material = material
        self.token = _temporal_token_from_material(material)

    def selection_inventory_token(self, *args, **kwargs):
        return self.token

    def selection_material(self, *args, **kwargs):
        return self.material


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        (
            lambda plain: plain["occurrence_membership"][0].__setitem__(
                "observation_id", "0" * 32),
            "temporal_occurrence_absent",
        ),
        (
            lambda plain: plain["occurrence_membership"][0].__setitem__(
                "value_json", "999"),
            "source_temporal_parity_failure",
        ),
        (
            lambda plain: plain.__setitem__(
                "as_of", plain["as_of"] + timedelta(seconds=1)),
            "temporal_occurrence_inconsistent",
        ),
    ],
)
def test_occurrence_absence_inconsistency_and_parity_are_distinct(
    tmp_path, mutation, expected_code,
):
    _, _, source, temporal = _captured_world(tmp_path)
    material = temporal.selection_material(
        _request().scope,
        horizon_started_at=_request().horizon_started_at,
        as_of=_request().as_of)
    changed = _rebuild(material, mutation)
    result = EvidenceAssuranceQueries(
        source=source, temporal=_FixedTemporalView(changed),
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert tuple(issue.code for issue in result.issues) == (expected_code,)


def test_source_attempt_missing_from_temporal_coverage_fails_parity(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    material = temporal.selection_material(
        _request().scope,
        horizon_started_at=_request().horizon_started_at,
        as_of=_request().as_of)

    def remove_memberships(plain):
        plain["selected_occurrence_index"] = None
        plain["selected_occurrence_is_pre_horizon_seed"] = False
        plain["occurrence_membership"] = []
        plain["attempt_coverage_membership"] = []
        plain["clock_segment_openings"] = []

    changed = _rebuild(material, remove_memberships)
    result = EvidenceAssuranceQueries(
        source=source, temporal=_FixedTemporalView(changed),
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert tuple(issue.code for issue in result.issues) == (
        "source_temporal_parity_failure",)
