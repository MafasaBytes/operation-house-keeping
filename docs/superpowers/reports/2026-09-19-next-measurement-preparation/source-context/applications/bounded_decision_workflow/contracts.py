"""Strict application-owned request contracts for S1."""

from datetime import UTC
import hashlib
import json
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    model_validator,
)

from backend.model_kernel import (
    AssertionContext,
    ObservationRoleReference,
    QuantityKindReference,
    UnitReference,
)


UtcDatetime = Annotated[
    AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]
Sha256 = Annotated[StrictStr, Field(pattern=r"^[0-9a-f]{64}$")]
LocalId = Annotated[
    StrictStr, Field(min_length=1, max_length=128,
                     pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
Index = Annotated[StrictInt, Field(ge=0)]


class _Frozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


class ApplicationIdentity(_Frozen):
    semantic_version: Literal["0.1.0"]
    build_policy_id: Literal["bdw-build-policy.v1"]


class ActorAssertion(_Frozen):
    actor_label: Annotated[StrictStr, Field(min_length=1, max_length=128)]
    authenticated: Literal[False]
    purpose: Annotated[StrictStr, Field(min_length=1, max_length=256)]


class CurrentConditionQuestion(_Frozen):
    state_anchor_id: StrictStr
    assertion_context: AssertionContext
    as_of: UtcDatetime
    declared_state_label: Annotated[StrictStr, Field(min_length=1, max_length=128)]


class PremiseEnvelope(_Frozen):
    premise_id: LocalId
    edition: Annotated[StrictInt, Field(ge=1)]
    epistemic_kind: Literal["synthetic_assumption", "application_policy"]
    issuer_assertion: Annotated[StrictStr, Field(min_length=1, max_length=256)]
    basis: Annotated[StrictStr, Field(min_length=1, max_length=256)]
    applicability_scope: Literal["one_step_enclosure"]
    availability: Literal["present", "missing", "unknown", "stale_reference"]
    value: Any
    canonical_commitment: Sha256

    @model_validator(mode="after")
    def _commitment_matches_content(self):
        content = self.model_dump(
            mode="json", exclude={"canonical_commitment"}, warnings=False)
        encoded = json.dumps(
            content, ensure_ascii=False, separators=(",", ":"),
            sort_keys=True, allow_nan=False).encode("utf-8")
        if hashlib.sha256(encoded).hexdigest() != self.canonical_commitment:
            raise ValueError("premise commitment does not match its content")
        return self


class TokenRolePremise(PremiseEnvelope):
    epistemic_kind: Literal["synthetic_assumption"]


class ObservedInputBinding(_Frozen):
    role: Literal["T0"]
    condition_index: Index
    constraint_evaluation_index: Index
    semantic_candidate_index: Index
    constraint_anchor_id: StrictStr
    variable_anchor_id: StrictStr
    subject_entity_anchor_id: StrictStr
    expected_quantity_kind: QuantityKindReference
    expected_observation_role: ObservationRoleReference
    expected_unit: UnitReference
    token_role_premises: tuple[TokenRolePremise, ...]


class ApplicationPremises(_Frozen):
    actions: PremiseEnvelope
    commands: PremiseEnvelope
    coordinates: dict[StrictStr, PremiseEnvelope]
    effects: dict[StrictStr, PremiseEnvelope]
    global_applicability: PremiseEnvelope
    hypotheses: PremiseEnvelope
    invariances: dict[StrictStr, PremiseEnvelope]
    law: PremiseEnvelope
    preconditions: dict[StrictStr, PremiseEnvelope]
    support_semantics: PremiseEnvelope
    timing: dict[StrictStr, PremiseEnvelope]


class TargetPolicy(_Frozen):
    costs: PremiseEnvelope
    feasibility_rule: PremiseEnvelope
    retained_hypotheses: PremiseEnvelope
    selection_rule: PremiseEnvelope
    target: PremiseEnvelope


class RequestedLimits(_Frozen):
    aggregate_prior_bundle_bytes: Annotated[StrictInt, Field(ge=1)]
    application_premise_declarations: Annotated[StrictInt, Field(ge=1)]
    candidates_per_evaluation: Annotated[StrictInt, Field(ge=1)]
    changed_paths: Annotated[StrictInt, Field(ge=1)]
    conditions_per_snapshot: Annotated[StrictInt, Field(ge=1)]
    constraint_evaluations_per_snapshot: Annotated[StrictInt, Field(ge=1)]
    corner_evaluations: Annotated[StrictInt, Field(ge=1)]
    decision_rows: Annotated[StrictInt, Field(ge=1)]
    exact_rational_digits_per_integer: Annotated[StrictInt, Field(ge=1)]
    input_json_depth: Annotated[StrictInt, Field(ge=1)]
    input_json_nodes_per_file: Annotated[StrictInt, Field(ge=1)]
    input_max_string_bytes: Annotated[StrictInt, Field(ge=1)]
    input_reference_occurrences: Annotated[StrictInt, Field(ge=1)]
    input_resolution_charges: Annotated[StrictInt, Field(ge=1)]
    model_records_per_snapshot: Annotated[StrictInt, Field(ge=1)]
    output_diagnostic_bytes: Annotated[StrictInt, Field(ge=1)]
    output_result_bytes: Annotated[StrictInt, Field(ge=1)]
    output_result_nodes: Annotated[StrictInt, Field(ge=1)]
    output_stdout_stderr_bytes: Annotated[StrictInt, Field(ge=1)]
    output_trace_bytes: Annotated[StrictInt, Field(ge=1)]
    output_trace_rows: Annotated[StrictInt, Field(ge=1)]
    prior_bundle_files: Annotated[StrictInt, Field(ge=1)]
    request_wire_bytes: Annotated[StrictInt, Field(ge=1)]
    resolved_input_bytes: Annotated[StrictInt, Field(ge=1)]
    retention_bundle_bytes: Annotated[StrictInt, Field(ge=1)]
    snapshot_wire_bytes: Annotated[StrictInt, Field(ge=1)]


class WorkflowRequest(_Frozen):
    actor_assertion: ActorAssertion
    application_identity: ApplicationIdentity
    current_condition_question: CurrentConditionQuestion
    observed_input_binding: ObservedInputBinding
    premises: ApplicationPremises
    request_id: LocalId
    requested_limits: RequestedLimits | None
    schema_version: Literal["bdw001.1"]
    snapshot_commitment: Sha256
    target_policy: TargetPolicy
    workflow_profile: Literal["hypothetical_enclosure_one_step.v1"]

    @model_validator(mode="after")
    def _closed_profile_cardinalities(self):
        if len(self.observed_input_binding.token_role_premises) != 3:
            raise ValueError("exactly three token-role premises are required")
        if set(self.premises.coordinates) != {"A", "alpha", "beta", "gamma"}:
            raise ValueError("coordinate premise IDs differ from the profile")
        if set(self.premises.effects) != {"E-a0", "E-aF", "E-aH"}:
            raise ValueError("effect premise IDs differ from the profile")
        if set(self.premises.invariances) != {"I-a0", "I-aF", "I-aH"}:
            raise ValueError("invariance premise IDs differ from the profile")
        if set(self.premises.preconditions) != {
                "PC-isolation", "PC-permission", "PC-restoration"}:
            raise ValueError("precondition premise IDs differ from the profile")
        if set(self.premises.timing) != {"T-aF", "T-aH"}:
            raise ValueError("timing premise IDs differ from the profile")
        return self
