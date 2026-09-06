"""C01-C29 exact pure occurrence-alignment derivation tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from backend.evidence_assurance import (
    OperationalEvidenceIssue,
    OperationalEvidenceSelectionResult,
)
from backend.temporal_state.contracts import TemporalOccurrence

from tests.evidence_alignment.helpers import (
    AS_OF,
    align,
    alternate_model_consumer,
    build_world,
    consumer_without_observation,
    differing_scope_consumer,
    duplicate_consumer,
    explicit_consumer,
    mutate_consumer_occurrence,
    no_candidates_consumer,
    no_observation_selection,
    pre_horizon_pair,
    selected_occurrence,
)


COVERED_ROWS = {
    "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09",
    "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18",
    "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27",
    "C28", "C29",
}


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    return build_world(tmp_path_factory.mktemp("alignment-derivation"))


def test_c01_c05_complete_and_seed_success_twins(world):
    complete = align(world)
    assert complete.status == "aligned_with_complete_evidence"
    assert complete.reason is None
    assert complete.aligned_candidate_index == 0
    assert complete.occurrence_relation == "content_equal"
    assert complete.endpoint_closure == "bound_by_snapshot_closure"
    assert complete.selected_occurrence_role == "in_horizon_member"
    assert complete.candidate_attachment == "attached"

    selection, consumer = pre_horizon_pair(world)
    incomplete = align(world, selection=selection, consumer=consumer)
    assert incomplete.status == "aligned_with_incomplete_evidence"
    assert incomplete.reason is None
    assert incomplete.evidence_coverage_completeness == (
        "incomplete_within_declared_horizon")
    assert incomplete.selected_occurrence_role == "pre_horizon_seed"
    assert incomplete.occurrence_relation == "content_equal"


def test_c03_no_selected_observation_precedes_other_relations(world):
    result = align(world, selection=no_observation_selection(world))
    assert result.status == "not_aligned"
    assert result.reason == "no_selected_observation"
    assert result.occurrence_relation == "not_applicable"
    assert result.aligned_candidate_index is None


def test_c19_refused_selection_is_not_evaluated(world):
    refused = OperationalEvidenceSelectionResult(
        status="refused", request=world.selection.request, snapshot=None,
        issues=(OperationalEvidenceIssue(
            code="invalid_bounded_material", detail_code="test_refusal",
            route_index=None, detail="test refusal is structured"),),
    )
    result = align(world, selection=refused)
    assert result.status == "not_evaluated"
    assert result.reason == "selection_refused"
    assert result.snapshot_validation is None
    assert result.evidence_coverage_completeness == "not_applicable"


def test_c21_c22_independent_expected_fingerprint_twins(world):
    fingerprint = world.selection.snapshot.content_fingerprint
    matched = align(world, expected=fingerprint)
    mismatched = align(world, expected="sha256:" + "0" * 64)
    absent = align(world)
    assert matched.status == "aligned_with_complete_evidence"
    assert matched.expected_fingerprint_relation == "matched"
    assert absent.expected_fingerprint_relation == "not_supplied"
    assert mismatched.status == "not_evaluated"
    assert mismatched.reason == "snapshot_fingerprint_mismatched"
    assert mismatched.expected_fingerprint_relation == "mismatched"
    assert mismatched.cutoff_relation == "not_evaluated"


@pytest.mark.parametrize(
    ("updates", "candidate_updates", "expected_fields"),
    [
        ({"attempt_id": "different-attempt"}, None, ("attempt_id",)),
        ({"raw_record_id": "different-raw"}, None, ("raw_record_id",)),
        ({"payload_checksum": "sha256:" + "1" * 64}, None,
         ("payload_checksum",)),
        ({"value_json": "61.0"}, None, ("value_json",)),
        ({"json_type": "string"}, None, ("json_type",)),
        ({"declared_unit": "different-unit"}, {
            "source_unit_evidence": "present",
            "declared_unit_lexeme_relation": "declared_lexeme_differs",
            "unit_lexeme_not_evaluated_reason": None,
        }, ("declared_unit",)),
        ({"attempt_started_at": datetime(2026, 8, 7, 19, 59, tzinfo=UTC)},
         None, ("attempt_started_at",)),
        ({"ingestion_run_id": "different-run"}, None, ("ingestion_run_id",)),
        ({"sweep_position": 99}, None, ("sweep_position",)),
        ({"change_class": "changed"}, None, ("change_class",)),
        ({"previous_occurrence_id": "different-previous"}, None,
         ("previous_occurrence_id",)),
        ({"quality_flags": ["different"]}, None, ("quality_flags",)),
    ],
)
def test_c07_c14_same_id_content_mutations_are_exactly_named(
    world, updates, candidate_updates, expected_fields,
):
    consumer = mutate_consumer_occurrence(
        world.compatibility, updates, candidate_updates=candidate_updates)
    result = align(world, consumer=consumer)
    assert result.status == "not_aligned"
    assert result.reason == "occurrence_content_mismatch"
    assert result.mismatched_occurrence_fields == expected_fields
    assert result.aligned_candidate_index is None


def test_c12_received_time_and_c14_source_clock_mutations(world):
    occurrence = selected_occurrence(world.selection)
    received = mutate_consumer_occurrence(
        world.compatibility,
        {"received_at": occurrence.received_at + timedelta(seconds=1)},
    )
    received_result = align(world, consumer=received)
    assert received_result.reason == "occurrence_content_mismatch"
    assert received_result.mismatched_occurrence_fields == ("received_at",)

    marker = occurrence.source_time.model_dump(mode="python")
    marker["value"] = str(float(marker["value"]) + 1)
    source_time = mutate_consumer_occurrence(
        world.compatibility, {"source_time": marker})
    assert align(world, consumer=source_time).mismatched_occurrence_fields == (
        "source_time",)

    segment = mutate_consumer_occurrence(
        world.compatibility, {"clock_segment_id": "different-segment"})
    assert align(world, consumer=segment).mismatched_occurrence_fields == (
        "clock_segment_id",)


def test_c06_equal_value_from_other_occurrence_never_aligns(world):
    consumer = mutate_consumer_occurrence(
        world.compatibility, {"occurrence_id": "different-occurrence"})
    result = align(world, consumer=consumer)
    assert result.status == "not_aligned"
    assert result.reason == "occurrence_absent_from_consumer_result"
    assert result.mismatched_occurrence_fields == ()


@pytest.mark.parametrize(
    "field",
    [
        "source_id", "adapter_id", "subject_identifier",
        "extraction_route", "item_key", "json_pointer",
    ],
)
def test_c15_each_shared_locator_field_is_required(world, field):
    result = align(world, consumer=differing_scope_consumer(world, field))
    assert result.status == "not_aligned"
    assert result.reason == "scope_differs"
    assert result.scope_relation == "six_field_locator_different"


def test_c17_cutoff_difference_and_equal_instant_normalization(world):
    different = world.consumer_queries.variable_value_compatibility(
        world.compatibility.variable_anchor_id,
        as_of=AS_OF + timedelta(seconds=1),
    )
    result = align(world, consumer=different)
    assert result.reason == "cutoff_differs"
    assert result.cutoff_relation == "different"

    same_instant = world.consumer_queries.variable_value_compatibility(
        world.compatibility.variable_anchor_id,
        as_of=AS_OF.astimezone(timezone(timedelta(hours=2))),
    )
    assert align(world, consumer=same_instant).cutoff_relation == "equal"


def test_c23_c24_no_candidates_and_no_observation_are_distinct(world):
    no_candidates = no_candidates_consumer(world)
    no_candidates_result = align(world, consumer=no_candidates)
    assert no_candidates_result.reason == "scope_differs"
    assert no_candidates_result.candidate_attachment == "not_applicable"

    absent = consumer_without_observation(world.compatibility)
    absent_result = align(world, consumer=absent)
    assert absent_result.reason == "consumer_observation_absent"
    assert absent_result.candidate_attachment == "not_evaluated"


def test_c25_c26_attachment_and_specification_do_not_gate_alignment(world):
    unattached = alternate_model_consumer(world, registered=False)
    # Reuse the exact candidate while retaining a genuinely unregistered model
    # result from the accepted consumer facade.
    assert unattached.candidates[0].state_candidate.bound is not None
    unattached_result = align(world, consumer=unattached)
    assert unattached_result.status == "aligned_with_complete_evidence"
    assert unattached_result.candidate_attachment == (
        "not_attachable_variable_unregistered")

    conflicted = alternate_model_consumer(world, conflicted=True)
    assert conflicted.specification_result.status == "conflicted"
    conflicted_result = align(world, consumer=conflicted)
    assert conflicted_result.status == "aligned_with_complete_evidence"


def test_c27_c28_c29_candidate_cardinality_cases(world):
    duplicate = duplicate_consumer(world.compatibility)
    multiple = align(world, consumer=duplicate)
    assert multiple.status == "not_aligned"
    assert multiple.reason == "multiple_matching_candidates"
    assert multiple.occurrence_relation == "multiple_matches"
    assert multiple.aligned_candidate_index is None

    explicit = align(world, consumer=explicit_consumer(world))
    assert explicit.status == "aligned_with_complete_evidence"
    assert explicit.aligned_candidate_index == 0


def test_c16_c20_broken_endpoint_closure_and_snapshot_are_typed(world):
    api = __import__(
        "tests.evidence_alignment.helpers", fromlist=["alignment_api"]
    ).alignment_api()
    request = {
        "schema_version": "1",
        "selection": world.selection.model_copy(update={
            "snapshot": world.selection.snapshot.model_copy(update={
                "source_material": world.selection.snapshot.source_material.model_copy(
                    update={"attempts": (None,)})
            })
        }),
        "compatibility": world.compatibility,
        "expected_snapshot_fingerprint": None,
    }
    with pytest.raises(api["EvidenceAlignmentQueryError"]) as error:
        api["align"](request)
    assert error.value.error_code == "ALIGNMENT_REQUEST_INVALID"
