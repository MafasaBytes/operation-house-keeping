"""Frozen, authoritative BH-001 evidence-gated evaluation results."""

from datetime import UTC
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    TypeAdapter,
    field_validator,
    model_validator,
)

from backend.constraint_evaluation import CanonicalObservedDecimal
from backend.model_kernel import AssertionContext, BehaviorRuleResult
from backend.model_state import SourceSelector
from backend.semantic_compatibility import VariableSemanticCompatibilityResult
from backend.system_identity import (
    BEHAVIOR_ANCHOR_ID_PATTERN,
    ENTITY_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
)


UtcDatetime = Annotated[
    AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]
_Index = Annotated[StrictInt, Field(ge=0)]

BehaviorEvaluationExecution = Literal["not_executed", "executed"]
BehaviorComputedRelation = Literal["equal", "different"]
BehaviorParticipantAdmission = Literal["admitted", "not_admitted"]
BehaviorParticipantModelAdmission = Literal["admitted", "not_admitted"]
BehaviorParticipantObservationAvailability = Literal[
    "observed", "none_before_cutoff", "not_evaluated"]
BehaviorParticipantAttachmentAdmission = Literal[
    "not_evaluated", "attached", "not_attached"]
BehaviorParticipantSemanticAdmission = Literal[
    "not_evaluated", "admitted", "not_admitted"]
BehaviorParticipantUnitAdmission = Literal[
    "not_evaluated", "exact", "mismatch"]
BehaviorParticipantLockAdmission = Literal[
    "not_evaluated", "matched", "mismatched"]
BehaviorParticipantNumericAdmission = Literal[
    "not_evaluated", "admitted", "out_of_bounds"]
BehaviorAcquisitionCohortAdmission = Literal[
    "not_evaluated", "same_acquisition_cohort",
    "different_acquisition_cohort"]
BehaviorEvaluationRefusalReason = Literal[
    "behavior_not_registered",
    "behavior_not_declared",
    "behavior_inactive",
    "behavior_conflicted",
    "participant_model_not_registered",
    "observation_absent",
    "observation_not_attached",
    "binding_not_positive",
    "evidence_not_assessable",
    "numeric_specification_not_available",
    "numeric_specification_conflicted",
    "model_quantity_kind_not_available",
    "model_observation_role_not_available",
    "model_unit_not_available",
    "source_semantics_not_admitted",
    "quantity_kind_lock_mismatch",
    "observation_role_lock_mismatch",
    "unit_lock_mismatch",
    "numeric_value_absent",
    "numeric_value_shape_mismatch",
    "numeric_value_out_of_bounds",
    "acquisition_cohort_mismatch",
]


class _Frozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


class BehaviorParticipantSource(_Frozen):
    variable_anchor_id: StrictStr = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    entity_anchor_id: StrictStr | None = Field(
        default=None, pattern=ENTITY_ANCHOR_ID_PATTERN)
    source: SourceSelector

    @field_validator("source", mode="before")
    @classmethod
    def _source_from_content(cls, value):
        return _dump(value)


class BehaviorEvaluationRefusal(_Frozen):
    reason: BehaviorEvaluationRefusalReason
    participant_index: _Index | None = None


class BehaviorEvaluationParticipantResult(_Frozen):
    participant_index: _Index
    variable_anchor_id: StrictStr = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    source_index: _Index
    semantic_result_index: _Index
    candidate_index: _Index
    model_admission: BehaviorParticipantModelAdmission
    observation_availability: BehaviorParticipantObservationAvailability
    attachment_admission: BehaviorParticipantAttachmentAdmission
    semantic_admission: BehaviorParticipantSemanticAdmission
    unit_admission: BehaviorParticipantUnitAdmission
    lock_admission: BehaviorParticipantLockAdmission
    numeric_admission: BehaviorParticipantNumericAdmission
    admission: BehaviorParticipantAdmission
    refusal_reasons: tuple[BehaviorEvaluationRefusalReason, ...] = ()
    canonical_decimal: CanonicalObservedDecimal | None = None


_CONTEXT = TypeAdapter(AssertionContext)


def _dump(value):
    return (value.model_dump(mode="python", warnings=False)
            if isinstance(value, BaseModel) else value)


def _rebuild_tuple(value, contract, label):
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{label} must be a tuple")
    return tuple(contract.model_validate(_dump(item)) for item in value)


class BehaviorEvaluationResult(_Frozen):
    behavior: BehaviorRuleResult
    behavior_anchor_id: StrictStr = Field(pattern=BEHAVIOR_ANCHOR_ID_PATTERN)
    context: AssertionContext
    as_of: UtcDatetime
    ruleset_version: Literal["bh001.1"]
    participant_sources: tuple[BehaviorParticipantSource, ...]
    participant_semantic_results: tuple[
        VariableSemanticCompatibilityResult, ...]
    participants: tuple[BehaviorEvaluationParticipantResult, ...]
    cohort_admission: BehaviorAcquisitionCohortAdmission
    execution: BehaviorEvaluationExecution
    not_executed_reasons: tuple[BehaviorEvaluationRefusal, ...] = ()
    computed_relation: BehaviorComputedRelation | None = None

    @model_validator(mode="before")
    @classmethod
    def _reconstruct_all_inputs(cls, value):
        payload = dict(_dump(value)) if isinstance(_dump(value), dict) else value
        if not isinstance(payload, dict):
            return payload
        if "behavior" in payload:
            payload["behavior"] = BehaviorRuleResult.model_validate(
                _dump(payload["behavior"]))
        if "context" in payload:
            payload["context"] = _CONTEXT.validate_python(
                _dump(payload["context"]))
        for field, contract, label in (
            ("participant_sources", BehaviorParticipantSource, "sources"),
            ("participant_semantic_results", VariableSemanticCompatibilityResult,
             "semantic results"),
            ("participants", BehaviorEvaluationParticipantResult,
             "participant rows"),
            ("not_executed_reasons", BehaviorEvaluationRefusal, "refusals"),
        ):
            if field in payload:
                payload[field] = _rebuild_tuple(
                    payload[field], contract, label)
        return payload

    @model_validator(mode="after")
    def _authoritative(self):
        from backend.behavior_evaluation.derivation import derive_evaluation

        expected = derive_evaluation(
            behavior=self.behavior,
            behavior_anchor_id=self.behavior_anchor_id,
            context=self.context,
            as_of=self.as_of,
            participant_sources=self.participant_sources,
            semantic_results=self.participant_semantic_results,
        )
        supplied = self.model_dump(
            mode="python",
            exclude={"behavior", "behavior_anchor_id", "context", "as_of",
                     "participant_sources", "participant_semantic_results"},
            warnings=False,
        )
        if supplied != expected:
            raise ValueError("behavior evaluation disclosure is forged")
        return self
