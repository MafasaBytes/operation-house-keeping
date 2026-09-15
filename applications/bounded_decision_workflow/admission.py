"""Public-result reconstruction and exact observed-value admission."""

from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal

from pydantic import ValidationError

from backend.constraint_evaluation import parse_observed_decimal
from backend.state_classification import StateClassificationResult

from applications.bounded_decision_workflow.contracts import WorkflowRequest
from applications.bounded_decision_workflow.errors import refusal
from applications.bounded_decision_workflow.input import (
    ParsedInput,
    canonical_json_bytes,
    effective_limits,
    enforce_snapshot_limits,
    parse_request_wire,
    parse_snapshot_wire,
)


@dataclass(frozen=True, slots=True)
class CurrentConditionAssessment:
    disposition: str
    computed_match: str | None
    condition_coverage: str
    refusals: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ObservedValueAdmission:
    status: str
    canonical_decimal: str | None
    unavailable_reason: str | None
    occurrence_id: str | None
    raw_record_id: str | None
    payload_checksum: str | None
    source_unit_lexeme: str | None


@dataclass(frozen=True, slots=True)
class AdmissionReview:
    request: WorkflowRequest
    snapshot: StateClassificationResult
    request_input: ParsedInput
    snapshot_input: ParsedInput
    current_condition: CurrentConditionAssessment
    observed_value: ObservedValueAdmission


def canonical_example_pair(review: AdmissionReview) -> tuple[bytes, bytes]:
    """Serialize a fully admitted pair without importing preparation artifacts."""
    request = canonical_json_bytes(review.request.model_dump(mode="json"))
    snapshot = canonical_json_bytes(review.snapshot.model_dump(mode="json"))
    if request != review.request_input.canonical_bytes:
        raise ValueError("request changed during typed reconstruction")
    if snapshot != review.snapshot_input.canonical_bytes:
        raise ValueError("snapshot changed during public reconstruction")
    return request, snapshot


def admit_request_and_snapshot(
        request_wire: bytes, snapshot_wire: bytes) -> AdmissionReview:
    request, request_input = parse_request_wire(request_wire)
    snapshot_input = parse_snapshot_wire(snapshot_wire)
    limits = effective_limits(request)
    enforce_snapshot_limits(snapshot_input, limits)

    if (request_input.counts.reference_occurrences
            + snapshot_input.counts.reference_occurrences
            > limits["input_reference_occurrences"]):
        raise refusal(
            "INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
            target="input_reference_occurrences", retry="reduce_input",
            exit_code=4)

    if request.snapshot_commitment != snapshot_input.sha256:
        raise refusal(
            "SNAPSHOT_COMMITMENT_MISMATCH",
            stage="commitment_public_reconstruction",
            target="snapshot_commitment", retry="supply_matching_snapshot")

    if request_input.counts.canonical_bytes + snapshot_input.counts.canonical_bytes \
            > limits["resolved_input_bytes"]:
        raise refusal(
            "RESOLVED_INPUT_LIMIT_EXCEEDED", stage="wire_resource",
            target="resolved_input_bytes", retry="reduce_input", exit_code=4)

    try:
        snapshot = StateClassificationResult.model_validate(snapshot_input.raw)
    except (ValidationError, ValueError, TypeError, AttributeError, KeyError) as error:
        problem = refusal(
            "PUBLIC_RECONSTRUCTION_REFUSED",
            stage="commitment_public_reconstruction", target="snapshot",
            retry="regenerate_public_result")
        raise type(problem)(problem.diagnostic, cause=error)

    current = _assess_current_condition(request, snapshot)
    observed = _admit_observed_value(request, snapshot)
    return AdmissionReview(
        request=request, snapshot=snapshot, request_input=request_input,
        snapshot_input=snapshot_input, current_condition=current,
        observed_value=observed)


def _mismatch():
    return refusal(
        "OBSERVATION_BINDING_MISMATCH",
        stage="commitment_public_reconstruction",
        target="observed_input_binding", retry="correct_binding")


def _assess_current_condition(
        request: WorkflowRequest,
        snapshot: StateClassificationResult) -> CurrentConditionAssessment:
    question = request.current_condition_question
    if (question.state_anchor_id != snapshot.state_anchor_id
            or question.assertion_context != snapshot.context
            or question.as_of != snapshot.as_of.astimezone(UTC)):
        raise _mismatch()
    disposition = (snapshot.computed_match
                   if snapshot.execution == "executed" else "unavailable")
    return CurrentConditionAssessment(
        disposition=disposition,
        computed_match=snapshot.computed_match,
        condition_coverage=snapshot.condition_coverage,
        refusals=tuple(item.reason for item in snapshot.refusals),
    )


def _at(items, index: int):
    try:
        return items[index]
    except IndexError as error:
        raise _mismatch() from error


def _admit_observed_value(
        request: WorkflowRequest,
        snapshot: StateClassificationResult) -> ObservedValueAdmission:
    binding = request.observed_input_binding
    condition = _at(snapshot.conditions, binding.condition_index)
    if (condition.condition_index != binding.condition_index
            or condition.constraint_anchor_id != binding.constraint_anchor_id
            or condition.constraint_evaluation_index
            != binding.constraint_evaluation_index
            or condition.candidate_index != binding.semantic_candidate_index
            or condition.declaration_alignment != "exact_current"):
        raise _mismatch()

    evaluation = _at(
        snapshot.constraint_evaluations,
        binding.constraint_evaluation_index)
    condition_source = _at(snapshot.condition_sources, condition.source_index)
    candidate = _at(evaluation.candidates, binding.semantic_candidate_index)
    if (evaluation.constraint.constraint_anchor_id
            != binding.constraint_anchor_id
            or evaluation.as_of != snapshot.as_of
            or evaluation.constraint.registration is None
            or evaluation.constraint.registration.variable_anchor_id
            != binding.variable_anchor_id
            or condition_source.constraint_anchor_id
            != binding.constraint_anchor_id
            or candidate.semantic_candidate_index
            != binding.semantic_candidate_index):
        raise _mismatch()

    constraint_semantics = evaluation.constraint.declaration.expected_semantics
    if (constraint_semantics.quantity_kind != binding.expected_quantity_kind
            or constraint_semantics.observation_role
            != binding.expected_observation_role
            or constraint_semantics.unit != binding.expected_unit):
        raise _mismatch()

    state_registrations = [
        record for record in snapshot.state.material.records
        if getattr(record, "record_kind", None) == "state_registration"
        and record.anchor.anchor_id == snapshot.state_anchor_id]
    if (len(state_registrations) != 1
            or state_registrations[0].subject_entity_anchor_id
            != binding.subject_entity_anchor_id):
        raise _mismatch()

    if candidate.verdict == "not_evaluated":
        return ObservedValueAdmission(
            status="unavailable", canonical_decimal=None,
            unavailable_reason=candidate.not_evaluated_reason,
            occurrence_id=None, raw_record_id=None, payload_checksum=None,
            source_unit_lexeme=None)
    if (candidate.verdict not in {"satisfied", "violated"}
            or candidate.not_evaluated_reason is not None
            or candidate.observed_decimal is None):
        raise _mismatch()

    semantic = evaluation.semantic_compatibility
    if semantic is None or semantic.variable_anchor_id != binding.variable_anchor_id:
        raise _mismatch()
    semantic_candidate = _at(
        semantic.candidates, binding.semantic_candidate_index)
    value_candidate = semantic_candidate.value_candidate
    state_candidate = value_candidate.state_candidate
    if (state_candidate.bound is None
            or state_candidate.attachment != "attached"
            or value_candidate.evidence_consistency != "consistent"
            or value_candidate.observed_shape != "number"
            or value_candidate.value_shape_compatibility
            != "satisfies_value_shape"
            or "declared_semantics_compatible"
            not in semantic_candidate.semantic_findings):
        raise _mismatch()

    bound = state_candidate.bound
    occurrence = bound.observed.occurrence
    resolution = bound.resolution
    expected_quantity = binding.expected_quantity_kind
    expected_role = binding.expected_observation_role
    expected_unit = binding.expected_unit
    model_semantics = semantic.semantics_result
    specification = semantic.value_compatibility.specification_result
    interpretation = semantic_candidate.interpretation
    model_revision = snapshot.state.material.revision
    if (constraint_semantics.quantity_kind != expected_quantity
            or constraint_semantics.observation_role != expected_role
            or constraint_semantics.unit != expected_unit
            or model_semantics.quantity_kind.declaration.declaration.quantity_kind
            != expected_quantity
            or model_semantics.observation_role.declaration.declaration.observation_role
            != expected_role
            or specification.specification.unit.unit != expected_unit
            or semantic_candidate.quantity_kind_compatibility != "token_identical"
            or semantic_candidate.observation_role_compatibility != "token_identical"
            or semantic_candidate.unit_identity_compatibility != "unit_identity_exact"
            or interpretation.quantity_kind.interpretation.quantity_kind
            != expected_quantity
            or interpretation.observation_role.interpretation.observation_role
            != expected_role
            or interpretation.unit.interpretation.unit != expected_unit):
        raise _mismatch()

    role_values = {
        premise.premise_id: premise.value
        for premise in binding.token_role_premises}
    expected_role_values = {
        "ROLE-temperature": {
            "profile_role": "temperature",
            "public_token": expected_quantity.model_dump(mode="json")},
        "ROLE-measured": {
            "profile_role": "measured_actual",
            "public_token": expected_role.model_dump(mode="json")},
        "ROLE-unit": {
            "profile_role": "degree_celsius",
            "public_token": expected_unit.model_dump(mode="json")},
    }
    if (role_values != expected_role_values
            or any(premise.availability != "present"
                   for premise in binding.token_role_premises)
            or evaluation.constraint.revision != model_revision
            or model_semantics.revision != model_revision
            or specification.revision != model_revision
            or semantic.interpretation_revision != interpretation.revision):
        raise _mismatch()

    if (resolution.status != "bound"
            or resolution.resolved_target is None
            or resolution.resolved_target.anchor_id != binding.variable_anchor_id
            or resolution.resolved_target.entity_anchor_id
            != binding.subject_entity_anchor_id
            or state_candidate.subject != occurrence.subject
            or state_candidate.property != occurrence.property
            or condition_source.source.subject != occurrence.subject
            or condition_source.source.property != occurrence.property
            or resolution.locator_subject != occurrence.subject
            or resolution.locator_property != occurrence.property):
        raise _mismatch()

    if (bound.observed.as_of != snapshot.as_of
            or occurrence.received_at > snapshot.as_of
            or bound.observed.staleness_seconds
            != (snapshot.as_of - occurrence.received_at).total_seconds()):
        raise _mismatch()

    canonical = _defensive_decimal_check(
        occurrence.value_json, str(candidate.observed_decimal))
    return ObservedValueAdmission(
        status="admitted", canonical_decimal=canonical,
        unavailable_reason=None, occurrence_id=occurrence.occurrence_id,
        raw_record_id=occurrence.raw_record_id,
        payload_checksum=occurrence.payload_checksum,
        source_unit_lexeme=occurrence.declared_unit)


def _defensive_decimal_check(lexeme: str, carried: str) -> str:
    resolution = parse_observed_decimal(lexeme)
    if resolution.status != "admitted" or resolution.decimal is None:
        raise _mismatch()
    if Decimal(resolution.decimal) != Decimal(carried):
        raise refusal(
            "OBSERVATION_DECIMAL_MISMATCH",
            stage="commitment_public_reconstruction",
            target="observed_candidate", retry="regenerate_public_result")
    return resolution.decimal
