"""Permanent regressions for the 2026-09-05 Slice B owner review."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts.operational_evidence import (
    Ds004OperationalEvidenceMaterial,
    OperationalEvidenceReadError,
)
from backend.evidence_assurance import (
    CapturedOperationalEvidenceSnapshot,
    EvidenceAssuranceQueries,
    EvidenceAssuranceQueryError,
    OperationalEvidenceStoreRevalidationResult,
    validate_operational_evidence_snapshot,
)

from tests.evidence_assurance.test_selection import (
    _SourceProbe,
    _TemporalProbe,
    _captured_world,
    _request,
)


class _ForgedFingerprint(str):
    def __eq__(self, other):
        return True

    __hash__ = str.__hash__


class _EqualMode:
    def __eq__(self, other):
        return True


def _snapshot(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    queries = EvidenceAssuranceQueries(source=source, temporal=temporal)
    snapshot = queries.select_operational_evidence(_request()).snapshot
    assert snapshot is not None
    return source, temporal, snapshot


def test_review_valid_capture_validation_and_revalidation_twins(tmp_path):
    source, temporal, snapshot = _snapshot(tmp_path)
    queries = EvidenceAssuranceQueries(source=source, temporal=temporal)

    capture = queries.select_operational_evidence(_request())
    assert capture.status == "complete_within_declared_horizon"
    assert capture.issues == ()
    assert validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint=snapshot.content_fingerprint,
    ).status == "structurally_self_consistent"
    assert queries.revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts",
    ).status == "valid_for_named_captured_artifacts"
    assert queries.revalidate_operational_evidence(
        snapshot,
        membership_mode="require_equal_final_observed_membership",
    ).status == "matches_final_observed_membership"


def test_r1_rejected_temporal_capture_never_supports_indexing_or_source_read(
    tmp_path,
):
    _, _, source, temporal = _captured_world(tmp_path)
    log = []

    class RejectedTemporal(_TemporalProbe):
        def selection_material(self, *args, **kwargs):
            material = super().selection_material(*args, **kwargs)
            return material.model_copy(update={
                "selected_occurrence_is_pre_horizon_seed": True,
                "selected_occurrence_index": 999,
            })

    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, log),
        temporal=RejectedTemporal(temporal, log),
    ).select_operational_evidence(_request())

    assert result.status == "refused"
    assert result.snapshot is None
    assert tuple(issue.code for issue in result.issues) == (
        "invalid_bounded_material",
    )
    assert "source_material" not in log
    assert log == [
        "source_inventory",
        "temporal_inventory",
        "temporal_material",
        "source_inventory",
        "temporal_inventory",
    ]


def test_r1_rejected_source_capture_never_supports_token_derivation(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)

    class RejectedSource(_SourceProbe):
        def read_material(self, *args, **kwargs):
            material = super().read_material(*args, **kwargs)
            return material.model_copy(update={"artifacts": (None,)})

    result = EvidenceAssuranceQueries(
        source=RejectedSource(source, []), temporal=temporal,
    ).select_operational_evidence(_request())

    assert result.status == "refused"
    assert result.snapshot is None
    assert tuple(issue.code for issue in result.issues) == (
        "invalid_bounded_material",
    )


@pytest.mark.parametrize(
    ("mode", "expected_status"),
    [
        ("named_captured_artifacts", "valid_for_named_captured_artifacts"),
        ("require_equal_final_observed_membership", "refused"),
    ],
)
def test_r1_rejected_current_temporal_material_cannot_claim_match_or_membership(
    tmp_path, mode, expected_status,
):
    source, temporal, snapshot = _snapshot(tmp_path)

    class RejectedTemporal(_TemporalProbe):
        def selection_material(self, *args, **kwargs):
            material = super().selection_material(*args, **kwargs)
            return material.model_copy(update={"hidden_extra": "forged"})

    result = EvidenceAssuranceQueries(
        source=source, temporal=RejectedTemporal(temporal, []),
    ).revalidate_operational_evidence(snapshot, membership_mode=mode)

    assert result.status == expected_status
    assert result.named_source_material_relation == "matched"
    assert result.captured_temporal_material_relation == "not_fully_observed"
    assert result.source_membership_relation == "equal_to_snapshot_final"
    assert result.temporal_membership_relation == "not_fully_observed"
    assert tuple(issue.code for issue in result.issues) == (
        "invalid_bounded_material",
    )


def test_r2_expected_fingerprint_is_strictly_reconstructed_before_comparison(
    tmp_path,
):
    _, _, snapshot = _snapshot(tmp_path)
    wrong = "sha256:" + "0" * 64
    assert wrong != snapshot.content_fingerprint

    valid_match = validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint=snapshot.content_fingerprint,
    )
    ordinary_mismatch = validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint=wrong,
    )
    hostile_mismatch = validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint=_ForgedFingerprint(wrong),
    )

    assert valid_match.expected_fingerprint_relation == "matched"
    assert ordinary_mismatch.status == hostile_mismatch.status == (
        "fingerprint_mismatch"
    )
    assert ordinary_mismatch.expected_fingerprint_relation == (
        hostile_mismatch.expected_fingerprint_relation
    ) == "mismatched"

    with pytest.raises(EvidenceAssuranceQueryError) as error:
        validate_operational_evidence_snapshot(
            snapshot, expected_fingerprint=object())
    assert error.value.error_code == "EA_REQUEST_INVALID"


def test_r2_membership_mode_is_admitted_before_any_dependency_access(tmp_path):
    source, temporal, snapshot = _snapshot(tmp_path)
    calls = []

    class LoggedSource(_SourceProbe):
        def reread_named_material(self, expected_material):
            self.log.append("source_named_reread")
            return self.wrapped.reread_named_material(expected_material)

    queries = EvidenceAssuranceQueries(
        source=LoggedSource(source, calls),
        temporal=_TemporalProbe(temporal, calls),
    )
    with pytest.raises(EvidenceAssuranceQueryError) as error:
        queries.revalidate_operational_evidence(
            snapshot, membership_mode=_EqualMode())
    assert error.value.error_code == "EA_REQUEST_INVALID"
    assert calls == []

    valid = queries.revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    assert valid.status == "valid_for_named_captured_artifacts"
    assert calls[0] == "source_named_reread"


def test_r4_compact_store_result_valid_twins_reconstruct(tmp_path):
    source, temporal, snapshot = _snapshot(tmp_path)
    queries = EvidenceAssuranceQueries(source=source, temporal=temporal)
    results = (
        queries.revalidate_operational_evidence(
            snapshot, membership_mode="named_captured_artifacts"),
        queries.revalidate_operational_evidence(
            snapshot,
            membership_mode="require_equal_final_observed_membership"),
        queries.revalidate_operational_evidence(
            snapshot.model_copy(update={
                "content_fingerprint": "sha256:" + "0" * 64,
            }),
            membership_mode="named_captured_artifacts",
        ),
    )
    for result in results:
        rebuilt = OperationalEvidenceStoreRevalidationResult.model_validate(
            result.model_dump(mode="python", warnings=False))
        assert rebuilt == result


def test_r4_compact_store_result_rejects_impossible_local_shapes(tmp_path):
    source, temporal, snapshot = _snapshot(tmp_path)
    queries = EvidenceAssuranceQueries(source=source, temporal=temporal)
    equal = queries.revalidate_operational_evidence(
        snapshot, membership_mode="require_equal_final_observed_membership")

    missing_fingerprint = equal.model_dump(mode="python", warnings=False)
    missing_fingerprint["snapshot_content_fingerprint"] = None
    unjustified_refusal = equal.model_dump(mode="python", warnings=False)
    unjustified_refusal["status"] = "refused"

    invalid_snapshot = queries.revalidate_operational_evidence(
        snapshot.model_copy(update={
            "content_fingerprint": "sha256:" + "0" * 64,
        }),
        membership_mode="named_captured_artifacts",
    )
    invalid_without_issue = invalid_snapshot.model_dump(
        mode="python", warnings=False)
    invalid_without_issue["issues"] = []

    class NamedFailure:
        def inventory_token(self, *args, **kwargs):
            raise AssertionError("membership access is not expected")

        def read_material(self, *args, **kwargs):
            raise AssertionError("selection is not expected")

        def reread_named_material(self, expected_material):
            raise OperationalEvidenceReadError(
                "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH",
                "named material changed",
            )

    refused = EvidenceAssuranceQueries(
        source=NamedFailure(), temporal=temporal,
    ).revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    unjustified_success = refused.model_dump(mode="python", warnings=False)
    unjustified_success["status"] = "valid_for_named_captured_artifacts"

    for candidate in (
        missing_fingerprint,
        unjustified_refusal,
        invalid_without_issue,
        unjustified_success,
    ):
        with pytest.raises(ValidationError):
            OperationalEvidenceStoreRevalidationResult.model_validate(candidate)
