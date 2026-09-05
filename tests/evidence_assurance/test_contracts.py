"""EA-001 Slice B exact public-contract acceptance tests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import get_args

import pytest
from pydantic import ValidationError

import backend.evidence_assurance as ea
from backend.data_sources.contracts import Ds004OperationalEvidenceScope


EXPECTED_EXPORTS = [
    "EvidenceAssuranceError",
    "EvidenceAssuranceConfigurationError",
    "EvidenceAssuranceQueryError",
    "EvidenceAssuranceConfigurationErrorCode",
    "EvidenceAssuranceQueryErrorCode",
    "CanonicalNonnegativeDecimal",
    "CoverageDisposition",
    "OperationalEvidenceIssueCode",
    "OperationalEvidenceSelectionStatus",
    "StoreIndependentValidationStatus",
    "ExpectedFingerprintRelation",
    "EmbeddedFingerprintRelation",
    "StoreBoundMembershipMode",
    "StoreBoundRevalidationStatus",
    "NamedCapturedMaterialRelation",
    "CapturedTemporalMaterialRelation",
    "ObservedMembershipRelation",
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
    "EvidenceAssuranceQueries",
    "validate_operational_evidence_snapshot",
]


EXPECTED_FIELDS = {
    "OperationalEvidenceSelectionPolicy": (
        "kind", "version", "occurrence_axis", "attempt_coverage_axis",
        "source_time_use",
    ),
    "OperationalEvidenceSelectionRequest": (
        "schema_version", "scope", "horizon_started_at", "as_of", "policy",
    ),
    "OperationalEvidenceMaterialLimits": (
        "schema_version", "maximum_in_horizon_attempts",
        "maximum_occurrence_members", "maximum_retained_artifacts",
        "maximum_retained_metadata_bytes",
    ),
    "OperationalEvidenceIssue": (
        "code", "detail_code", "route_index", "detail",
    ),
    "OperationalProvenanceRoute": (
        "attempt_index", "run_index", "temporal_attempt_index",
        "envelope_index", "payload_artifact_index", "extraction_index",
        "quarantine_index", "observation_index", "temporal_occurrence_index",
        "artifact_descriptor_indices", "coverage_disposition",
    ),
    "OperationalCoverageSummary": (
        "attempt_route_indices", "property_observed_route_indices",
        "omitted_property_route_indices", "empty_snapshot_route_indices",
        "failed_route_indices", "quarantined_route_indices",
        "extraction_incomplete_route_indices", "completeness",
    ),
    "SelectedSourceObservation": (
        "outcome", "temporal_occurrence_index", "provenance_route_index",
        "pre_horizon_seed", "selected_received_at",
        "observation_age_seconds", "age_basis",
    ),
    "CapturedViewFence": (
        "initial_source_token", "initial_temporal_token", "final_source_token",
        "final_temporal_token", "relation",
    ),
    "OperationalEvidenceAssurance": (
        "payload_byte_check", "metadata_same_read_check", "provenance_closure",
        "observation_content_relation", "occurrence_membership_relation",
        "attempt_coverage_membership_relation", "captured_view_relation",
        "semantic_compatibility", "accountable_occurrence",
    ),
    "CapturedOperationalEvidenceSnapshot": (
        "schema_version", "request", "fixed_limits", "source_material",
        "temporal_material", "provenance_routes", "selected", "coverage",
        "capture_fence", "assurance", "issues", "content_fingerprint",
    ),
    "OperationalNamedArtifactRevalidation": (
        "artifact_descriptor_index", "relation", "observed_byte_count",
        "observed_captured_file_sha256",
    ),
    "OperationalEvidenceSelectionResult": (
        "status", "request", "snapshot", "issues",
    ),
    "OperationalEvidenceStoreRevalidationResult": (
        "status", "membership_mode", "snapshot_content_fingerprint",
        "snapshot_validation_status", "expected_artifact_count",
        "expected_provenance_route_count", "named_source_material_relation",
        "captured_temporal_material_relation", "source_membership_relation",
        "temporal_membership_relation", "named_artifact_results", "issues",
    ),
    "OperationalEvidenceSnapshotValidationResult": (
        "status", "computed_fingerprint", "embedded_fingerprint_relation",
        "expected_fingerprint_relation", "source_bytes",
        "temporal_store_membership", "detail_code", "detail",
    ),
}


def _scope():
    return Ds004OperationalEvidenceScope(
        source_id="printer-1", adapter_id="moonraker",
        endpoint_id="printer_objects_query", item_key="printer_objects",
        subject_identifier="extruder", extraction_route="api:moonraker:v1",
        json_pointer="/result/status/extruder/temperature",
    )


def _policy():
    return ea.OperationalEvidenceSelectionPolicy(
        kind="independent_latest_at_or_before_as_of",
        version="ea001.operational_selection.v1", occurrence_axis="received_at",
        attempt_coverage_axis="effective_wall_time",
        source_time_use="disclosure_only",
    )


def test_exact_ordered_exports_and_no_convenience_aliases():
    assert ea.__all__ == EXPECTED_EXPORTS
    assert len(ea.__all__) == 33
    for forbidden in (
        "authenticate_evidence", "verify_state", "assessment_evidence",
        "current_evidence", "fresh_evidence", "history", "occurrence",
        "transition", "flow",
    ):
        assert not hasattr(ea, forbidden)


def test_exact_model_field_order_and_frozen_strict_configuration():
    for name, fields in EXPECTED_FIELDS.items():
        model = getattr(ea, name)
        assert tuple(model.model_fields) == fields
        assert model.model_config["frozen"] is True
        assert model.model_config["extra"] == "forbid"
        assert model.model_config["revalidate_instances"] == "always"


def test_exact_literal_order():
    expected = {
        "CoverageDisposition": (
            "property_observed", "snapshot_without_property", "empty_snapshot",
            "acquisition_failed", "quarantined", "extraction_incomplete",
        ),
        "OperationalEvidenceIssueCode": (
            "unsupported_operational_evidence", "invalid_bounded_material",
            "excessive_bounded_material", "source_evidence_unavailable",
            "temporal_evidence_unavailable", "source_store_changed_during_capture",
            "temporal_store_changed_during_capture", "checksum_mismatch",
            "provenance_closure_failure", "observation_content_mismatch",
            "extraction_incomplete", "temporal_occurrence_absent",
            "temporal_occurrence_inconsistent", "source_temporal_parity_failure",
            "no_observation_at_or_before_as_of",
            "incomplete_coverage_within_declared_horizon",
        ),
        "OperationalEvidenceSelectionStatus": (
            "complete_within_declared_horizon",
            "incomplete_within_declared_horizon", "refused",
        ),
        "StoreIndependentValidationStatus": (
            "structurally_self_consistent", "fingerprint_mismatch", "invalid",
        ),
        "ExpectedFingerprintRelation": ("matched", "mismatched", "not_supplied"),
        "EmbeddedFingerprintRelation": ("matched", "mismatched", "not_computed"),
        "StoreBoundMembershipMode": (
            "require_equal_final_observed_membership", "named_captured_artifacts",
        ),
        "StoreBoundRevalidationStatus": (
            "matches_final_observed_membership",
            "valid_for_named_captured_artifacts", "observed_membership_changed",
            "refused",
        ),
        "NamedCapturedMaterialRelation": (
            "matched", "changed", "unavailable", "not_evaluated",
        ),
        "CapturedTemporalMaterialRelation": (
            "matched", "changed", "not_fully_observed", "not_evaluated",
        ),
        "ObservedMembershipRelation": (
            "equal_to_snapshot_final", "different_from_snapshot_final",
            "not_fully_observed", "not_evaluated",
        ),
        "EvidenceAssuranceConfigurationErrorCode": ("EA_DEPENDENCY_INVALID",),
        "EvidenceAssuranceQueryErrorCode": (
            "EA_REQUEST_INVALID", "EA_SELECTION_POLICY_INVALID",
        ),
    }
    for name, values in expected.items():
        assert get_args(getattr(ea, name)) == values
    assert "EA_TIME_COMPARISON_UNSUPPORTED" not in repr(ea.EvidenceAssuranceQueryErrorCode)


def test_request_and_supporting_scalar_contracts_are_strict():
    request = ea.OperationalEvidenceSelectionRequest(
        schema_version="1", scope=_scope(),
        horizon_started_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 2, tzinfo=UTC), policy=_policy(),
    )
    assert request.horizon_started_at.tzinfo is UTC
    with pytest.raises(ValidationError):
        ea.OperationalEvidenceSelectionRequest.model_validate({
            **request.model_dump(mode="python"), "as_of": datetime(2025, 1, 1, tzinfo=UTC),
        })
    with pytest.raises(ValidationError):
        ea.OperationalEvidenceIssue(
            code="invalid_bounded_material", detail_code="bad", route_index=True,
            detail="invalid material",
        )
    for invalid in ("-1", "00", "1.0", "1e2", "+1", " 1", "nan"):
        with pytest.raises(ValidationError):
            ea.SelectedSourceObservation(
                outcome="selected_source_observation", temporal_occurrence_index=0,
                provenance_route_index=0, pre_horizon_seed=False,
                selected_received_at=datetime(2026, 1, 1, tzinfo=UTC),
                observation_age_seconds=invalid, age_basis="received_at",
            )


def test_typed_error_tree_has_only_exact_public_fields():
    error = ea.EvidenceAssuranceConfigurationError(
        "EA_DEPENDENCY_INVALID", "dependencies are invalid")
    assert type(error).__mro__[:3] == (
        ea.EvidenceAssuranceConfigurationError, ea.EvidenceAssuranceError,
        Exception,
    )
    assert vars(error) == {
        "error_code": "EA_DEPENDENCY_INVALID", "message": "dependencies are invalid"}
    assert str(error) == "EA_DEPENDENCY_INVALID: dependencies are invalid"
    with pytest.raises((TypeError, ValueError)):
        ea.EvidenceAssuranceConfigurationError(
            "EA_REQUEST_INVALID", "wrong vocabulary")
    with pytest.raises((TypeError, ValueError)):
        ea.EvidenceAssuranceQueryError("EA_DEPENDENCY_INVALID", "wrong vocabulary")
