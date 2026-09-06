"""Pure EA-to-observation-compatibility occurrence alignment."""

from __future__ import annotations

from backend.evidence_assurance import validate_operational_evidence_snapshot

from backend.evidence_alignment.contracts import (
    EvidenceAlignmentQueryError,
    OperationalEvidenceAlignmentRequest,
    OperationalEvidenceAlignmentResult,
    _deep_plain,
)


_OCCURRENCE_FIELDS = (
    "occurrence_id",
    "attempt_id",
    "subject",
    "property",
    "observation_id",
    "raw_record_id",
    "payload_checksum",
    "attempt_started_at",
    "ingestion_run_id",
    "sweep_position",
    "received_at",
    "finished_at",
    "source_time",
    "clock_segment_id",
    "value_json",
    "json_type",
    "declared_unit",
    "change_class",
    "previous_occurrence_id",
    "quality_flags",
)


def _strict_request(value) -> OperationalEvidenceAlignmentRequest:
    try:
        return OperationalEvidenceAlignmentRequest.model_validate(
            _deep_plain(value))
    except Exception as error:
        raise EvidenceAlignmentQueryError(
            "ALIGNMENT_REQUEST_INVALID",
            "alignment request is invalid",
        ) from error


def _locator_equal(candidate, scope) -> bool:
    return (
        candidate.subject.source_id == scope.source_id
        and candidate.subject.adapter_id == scope.adapter_id
        and candidate.subject.subject_identifier == scope.subject_identifier
        and candidate.property.extraction_route == scope.extraction_route
        and candidate.property.item_key == scope.item_key
        and candidate.property.json_pointer == scope.json_pointer
    )


def _selected_occurrence(snapshot):
    selected_index = snapshot.selected.temporal_occurrence_index
    if selected_index is None:
        return None
    return snapshot.temporal_material.occurrence_membership[selected_index]


def _assert_endpoint_closure(snapshot, occurrence) -> None:
    attempts = tuple(
        attempt for attempt in snapshot.source_material.attempts
        if attempt.attempt_id == occurrence.attempt_id
    )
    if (
        len(attempts) != 1
        or attempts[0].endpoint_id != snapshot.request.scope.endpoint_id
    ):
        raise ValueError("selected occurrence endpoint closure is invalid")


def _occurrence_differences(expected, observed) -> tuple[str, ...]:
    return tuple(sorted(
        name for name in _OCCURRENCE_FIELDS
        if getattr(expected, name) != getattr(observed, name)
    ))


def _base_disclosures(request):
    compatibility = request.compatibility
    selection = request.selection
    return {
        "snapshot_validation": None,
        "evidence_selection_status": selection.status,
        "evidence_coverage_completeness": (
            "not_applicable" if selection.status == "refused"
            else selection.status
        ),
        "expected_fingerprint_relation": (
            "not_supplied"
            if request.expected_snapshot_fingerprint is None
            else "mismatched"
        ),
        "cutoff_relation": "not_evaluated",
        "scope_relation": "not_evaluated",
        "endpoint_closure": "not_evaluated",
        "selected_occurrence_role": "not_applicable",
        "occurrence_relation": "not_applicable",
        "mismatched_occurrence_fields": (),
        "aligned_candidate_index": None,
        "candidate_attachment": "not_applicable",
        "variable_anchor_id": compatibility.variable_anchor_id,
        "model_revision_id": compatibility.state.model_revision.revision_id,
        "binding_revision_id": compatibility.state.binding_revision.revision_id,
    }


def _derive_alignment_fields(
    request: OperationalEvidenceAlignmentRequest,
) -> dict[str, object]:
    """Derive every compact result field from reconstructed carried content."""
    selection = request.selection
    compatibility = request.compatibility
    fields = _base_disclosures(request)

    if selection.status == "refused":
        fields.update(status="not_evaluated", reason="selection_refused")
        return fields

    snapshot = selection.snapshot
    if snapshot is None:
        raise ValueError("non-refused selection has no snapshot")
    validation = validate_operational_evidence_snapshot(
        snapshot,
        expected_fingerprint=request.expected_snapshot_fingerprint,
    )
    fields["snapshot_validation"] = validation
    fields["expected_fingerprint_relation"] = (
        validation.expected_fingerprint_relation)
    if (
        validation.status == "invalid"
        or validation.embedded_fingerprint_relation != "matched"
    ):
        raise ValueError("carried snapshot is not structurally self-consistent")
    if validation.expected_fingerprint_relation == "mismatched":
        fields.update(
            status="not_evaluated",
            reason="snapshot_fingerprint_mismatched",
            candidate_attachment="not_evaluated",
        )
        return fields
    if validation.status != "structurally_self_consistent":
        raise ValueError("snapshot validation status is invalid")

    scope = snapshot.request.scope
    occurrence = _selected_occurrence(snapshot)
    cutoff_equal = snapshot.request.as_of == compatibility.as_of
    fields["cutoff_relation"] = "equal" if cutoff_equal else "different"
    locator_candidates = tuple(
        (index, candidate)
        for index, candidate in enumerate(compatibility.candidates)
        if _locator_equal(candidate.state_candidate, scope)
    )
    fields["scope_relation"] = (
        "six_field_locator_equal"
        if locator_candidates
        else "six_field_locator_different"
    )

    if occurrence is None:
        fields.update(status="not_aligned", reason="no_selected_observation")
        return fields

    _assert_endpoint_closure(snapshot, occurrence)
    fields["endpoint_closure"] = "bound_by_snapshot_closure"
    fields["selected_occurrence_role"] = (
        "pre_horizon_seed"
        if snapshot.selected.pre_horizon_seed
        else "in_horizon_member"
    )

    observed_candidates = tuple(
        (index, candidate, candidate.state_candidate.bound.observed.occurrence)
        for index, candidate in locator_candidates
        if candidate.state_candidate.bound is not None
    )
    exact_matches = tuple(
        row for row in observed_candidates if row[2] == occurrence)

    if not cutoff_equal:
        if len(exact_matches) == 1:
            fields["occurrence_relation"] = "content_equal"
            fields["candidate_attachment"] = (
                exact_matches[0][1].state_candidate.attachment)
        fields.update(status="not_aligned", reason="cutoff_differs")
        return fields

    if not locator_candidates:
        fields.update(status="not_aligned", reason="scope_differs")
        return fields

    if not observed_candidates:
        fields.update(
            status="not_aligned",
            reason="consumer_observation_absent",
            candidate_attachment="not_evaluated",
        )
        return fields

    if len(exact_matches) > 1:
        fields.update(
            status="not_aligned",
            reason="multiple_matching_candidates",
            occurrence_relation="multiple_matches",
        )
        return fields

    if len(exact_matches) == 1:
        index, candidate, _ = exact_matches[0]
        fields.update(
            status=(
                "aligned_with_complete_evidence"
                if selection.status == "complete_within_declared_horizon"
                else "aligned_with_incomplete_evidence"
            ),
            reason=None,
            occurrence_relation="content_equal",
            aligned_candidate_index=index,
            candidate_attachment=candidate.state_candidate.attachment,
        )
        return fields

    same_identity = tuple(
        row for row in observed_candidates
        if row[2].occurrence_id == occurrence.occurrence_id
    )
    if same_identity:
        mismatches = tuple(sorted(set().union(*(
            _occurrence_differences(occurrence, row[2])
            for row in same_identity
        ))))
        fields.update(
            status="not_aligned",
            reason="occurrence_content_mismatch",
            occurrence_relation="content_mismatch",
            mismatched_occurrence_fields=mismatches,
            candidate_attachment=(
                same_identity[0][1].state_candidate.attachment),
        )
        return fields

    fields.update(
        status="not_aligned",
        reason="occurrence_absent_from_consumer_result",
        occurrence_relation="absent_from_consumer_result",
    )
    return fields


def align_operational_evidence_with_value_compatibility(
    request: OperationalEvidenceAlignmentRequest,
) -> OperationalEvidenceAlignmentResult:
    """Purely align one carried EA selection with one carried VS result."""
    request = _strict_request(request)
    try:
        derived = _derive_alignment_fields(request)
        return OperationalEvidenceAlignmentResult.model_construct(
            schema_version="1",
            request=request,
            **derived,
        )
    except EvidenceAlignmentQueryError:
        raise
    except Exception as error:
        raise EvidenceAlignmentQueryError(
            "ALIGNMENT_REQUEST_INVALID",
            "alignment request is invalid",
        ) from error
