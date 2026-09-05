"""EA-001 Slice B store-bound revalidation acceptance tests."""

from __future__ import annotations

import pytest

from backend.data_sources.contracts import OperationalEvidenceReadError
from backend.evidence_assurance import (
    EvidenceAssuranceQueries,
    EvidenceAssuranceQueryError,
)

from tests.evidence_assurance.test_selection import (
    _SourceProbe,
    _TemporalProbe,
    _captured_world,
    _request,
)


def _captured_snapshot(tmp_path):
    raw, transport, source, temporal = _captured_world(tmp_path)
    queries = EvidenceAssuranceQueries(source=source, temporal=temporal)
    snapshot = queries.select_operational_evidence(_request()).snapshot
    return raw, transport, source, temporal, snapshot


def test_equal_membership_mode_matches_named_and_current_material(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)
    result = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).revalidate_operational_evidence(
        snapshot, membership_mode="require_equal_final_observed_membership")
    assert result.status == "matches_final_observed_membership"
    assert result.snapshot_validation_status == "structurally_self_consistent"
    assert result.snapshot_content_fingerprint == snapshot.content_fingerprint
    assert result.expected_artifact_count == len(snapshot.source_material.artifacts)
    assert result.expected_provenance_route_count == len(snapshot.provenance_routes)
    assert result.named_source_material_relation == "matched"
    assert result.captured_temporal_material_relation == "matched"
    assert result.source_membership_relation == "equal_to_snapshot_final"
    assert result.temporal_membership_relation == "equal_to_snapshot_final"
    assert tuple(row.artifact_descriptor_index
                 for row in result.named_artifact_results) == tuple(
        range(len(snapshot.source_material.artifacts)))
    for row, descriptor in zip(
        result.named_artifact_results, snapshot.source_material.artifacts,
        strict=True,
    ):
        assert row.observed_byte_count == descriptor.byte_count
        assert row.observed_captured_file_sha256 == descriptor.captured_file_sha256
    assert result.issues == ()


def test_named_mode_discloses_growth_without_reselection(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)

    class GrowingSource:
        def __init__(self, wrapped):
            self.wrapped = wrapped
        def reread_named_material(self, expected_material):
            return self.wrapped.reread_named_material(expected_material)
        def read_material(self, *args, **kwargs):
            raise AssertionError("revalidation must not reselect source material")
        def inventory_token(self, *args, **kwargs):
            token = self.wrapped.inventory_token(*args, **kwargs)
            from tests.evidence_assurance.test_selection import _changed_source_token
            return _changed_source_token(token)

    class GrowingTemporal:
        def __init__(self, wrapped):
            self.wrapped = wrapped
        def selection_inventory_token(self, *args, **kwargs):
            token = self.wrapped.selection_inventory_token(*args, **kwargs)
            return token.model_copy(update={
                "attempt_coverage_membership_sha256": "sha256:" + "e" * 64})
        def selection_material(self, *args, **kwargs):
            return self.wrapped.selection_material(*args, **kwargs)

    result = EvidenceAssuranceQueries(
        source=GrowingSource(source), temporal=GrowingTemporal(temporal),
    ).revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    assert result.status == "valid_for_named_captured_artifacts"
    assert result.named_source_material_relation == "matched"
    assert result.captured_temporal_material_relation == "matched"
    assert result.source_membership_relation == "different_from_snapshot_final"
    assert result.temporal_membership_relation == "different_from_snapshot_final"
    assert result.issues == ()


def test_equal_mode_reports_stable_membership_difference(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)

    class DifferentSource(_SourceProbe):
        def __init__(self, wrapped):
            super().__init__(wrapped, [], fake_all=True)

    class DifferentTemporal(_TemporalProbe):
        def selection_inventory_token(self, *args, **kwargs):
            token = self.wrapped.selection_inventory_token(*args, **kwargs)
            return token.model_copy(update={
                "attempt_coverage_membership_sha256": "sha256:" + "e" * 64})

    result = EvidenceAssuranceQueries(
        source=DifferentSource(source),
        temporal=DifferentTemporal(temporal, []),
    ).revalidate_operational_evidence(
        snapshot, membership_mode="require_equal_final_observed_membership")
    assert result.status == "observed_membership_changed"
    assert result.source_membership_relation == "different_from_snapshot_final"
    assert result.temporal_membership_relation == "different_from_snapshot_final"


def test_named_mode_survives_unobservable_current_source_membership(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)

    class OverBoundSource:
        def reread_named_material(self, expected_material):
            return source.reread_named_material(expected_material)
        def read_material(self, *args, **kwargs):
            raise AssertionError("source material must not be reselected")
        def inventory_token(self, *args, **kwargs):
            raise OperationalEvidenceReadError(
                "OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED",
                "in-horizon attempt count exceeds 4096")

    named = EvidenceAssuranceQueries(
        source=OverBoundSource(), temporal=temporal,
    ).revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    assert named.status == "valid_for_named_captured_artifacts"
    assert named.named_source_material_relation == "matched"
    assert named.source_membership_relation == "not_fully_observed"
    assert tuple(issue.code for issue in named.issues) == (
        "excessive_bounded_material",)

    equal = EvidenceAssuranceQueries(
        source=OverBoundSource(), temporal=temporal,
    ).revalidate_operational_evidence(
        snapshot, membership_mode="require_equal_final_observed_membership")
    assert equal.status == "refused"
    assert equal.source_membership_relation == "not_fully_observed"


def test_named_material_changed_or_unavailable_stops_before_membership_io(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)

    class NamedFailure:
        def __init__(self, code):
            self.code = code
            self.inventory_calls = 0
        def reread_named_material(self, expected_material):
            raise OperationalEvidenceReadError(self.code, "named material failed")
        def read_material(self, *args, **kwargs):
            raise AssertionError("source material must not be reselected")
        def inventory_token(self, *args, **kwargs):
            self.inventory_calls += 1
            raise AssertionError("membership I/O must not follow named failure")

    class NoTemporalIo:
        def selection_inventory_token(self, *args, **kwargs):
            raise AssertionError("temporal I/O must not follow named failure")
        def selection_material(self, *args, **kwargs):
            raise AssertionError("temporal I/O must not follow named failure")

    for code, relation, issue_code in (
        ("OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH", "changed",
         "invalid_bounded_material"),
        ("OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE", "unavailable",
         "source_evidence_unavailable"),
    ):
        result = EvidenceAssuranceQueries(
            source=NamedFailure(code), temporal=NoTemporalIo(),
        ).revalidate_operational_evidence(
            snapshot, membership_mode="named_captured_artifacts")
        assert result.status == "refused"
        assert result.named_source_material_relation == relation
        assert result.named_artifact_results == ()
        assert tuple(issue.code for issue in result.issues) == (issue_code,)


def test_invalid_snapshot_and_invalid_mode_perform_no_io(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)

    class NeverIo:
        def reread_named_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def read_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def inventory_token(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def selection_inventory_token(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def selection_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")

    facade = EvidenceAssuranceQueries(source=NeverIo(), temporal=NeverIo())
    invalid = snapshot.model_copy(update={
        "content_fingerprint": "sha256:" + "0" * 64})
    result = facade.revalidate_operational_evidence(
        invalid, membership_mode="named_captured_artifacts")
    assert result.status == "refused"
    assert result.snapshot_content_fingerprint is None
    assert result.expected_artifact_count == 0
    assert result.expected_provenance_route_count == 0
    assert result.named_source_material_relation == "not_evaluated"
    assert result.source_membership_relation == "not_evaluated"
    assert tuple(issue.code for issue in result.issues) == (
        "invalid_bounded_material",)

    with pytest.raises(EvidenceAssuranceQueryError) as error:
        facade.revalidate_operational_evidence(snapshot, membership_mode="latest")
    assert error.value.error_code == "EA_REQUEST_INVALID"


def test_crossed_revalidation_fence_changes_retain_both_issues(tmp_path):
    _, _, source, temporal, snapshot = _captured_snapshot(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, [], mutate_final=True),
        temporal=_TemporalProbe(temporal, [], mutate_final=True),
    ).revalidate_operational_evidence(
        snapshot, membership_mode="named_captured_artifacts")
    assert result.status == "valid_for_named_captured_artifacts"
    assert result.source_membership_relation == "not_fully_observed"
    assert result.temporal_membership_relation == "not_fully_observed"
    assert tuple(issue.code for issue in result.issues) == (
        "source_store_changed_during_capture",
        "temporal_store_changed_during_capture",
    )
