"""Frozen public contracts for ST-001 evidence-gated classification."""

from collections.abc import Mapping
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

from backend.constraint_evaluation import ConstraintEvaluationResult
from backend.model_kernel import AssertionContext, StateDeclarationResult
from backend.model_state import SourceSelector
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN,
    STATE_ANCHOR_ID_PATTERN,
)


UtcDatetime = Annotated[
    AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]
_Index = Annotated[StrictInt, Field(ge=0)]

StateConditionDeclarationAlignment = Literal[
    "not_evaluated", "not_registered", "not_declared", "conflicted",
    "superseded", "exact_current",
]
StateConditionOutcome = Literal["satisfied", "violated", "not_evaluated"]
StateConditionCoverage = Literal["not_evaluated", "complete", "incomplete"]
StateTemporalAlignment = Literal["not_evaluated", "not_asserted"]
StateClassificationExecution = Literal["not_executed", "executed"]
StateComputedMatch = Literal["matches", "does_not_match"]
StateClassificationRefusalReason = Literal[
    "state_not_registered",
    "state_not_declared",
    "state_inactive",
    "state_conflicted",
    "condition_not_registered",
    "condition_declaration_not_declared",
    "condition_declaration_conflicted",
    "condition_declaration_superseded",
    "condition_evaluation_not_evaluated",
]


class _Frozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="before")
    @classmethod
    def _reject_hidden_instance_fields(cls, value):
        """Reject fields hidden in forged nested Pydantic instances."""
        pending = [value]
        seen: set[int] = set()
        while pending:
            item = pending.pop()
            identity = id(item)
            if identity in seen:
                continue
            seen.add(identity)
            if isinstance(item, BaseModel):
                fields = type(item).model_fields
                private = set(getattr(
                    type(item), "__private_attributes__", {}))
                stored = vars(item)
                extras = getattr(item, "__pydantic_extra__", None)
                if set(stored).difference(fields).difference(private) or extras:
                    raise ValueError(
                        "pydantic result instance contains extra fields")
                pending.extend(stored[name] for name in fields if name in stored)
            elif isinstance(item, Mapping):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, (tuple, list, set, frozenset)):
                pending.extend(item)
        return value


def _dump(value):
    return (value.model_dump(mode="python", warnings=False)
            if isinstance(value, BaseModel) else value)


def _rebuild_tuple(value, contract, label):
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{label} must be a tuple")
    # Return serialized content. The annotated field contract performs the
    # actual reconstruction after the base hidden-instance guard has seen a
    # content-only graph. This avoids handing accepted lower result models
    # back to validators that intentionally reject their private row bindings.
    return tuple(_dump(item) for item in value)


class StateConditionSource(_Frozen):
    constraint_anchor_id: StrictStr = Field(
        pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    source: SourceSelector

    @field_validator("source", mode="before")
    @classmethod
    def _source_from_content(cls, value):
        return _dump(value)


class StateClassificationRefusal(_Frozen):
    reason: StateClassificationRefusalReason
    condition_index: _Index | None = None


class StateClassificationConditionResult(_Frozen):
    condition_index: _Index
    constraint_anchor_id: StrictStr = Field(
        pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    source_index: _Index
    constraint_evaluation_index: _Index
    candidate_index: _Index | None = None
    declaration_alignment: StateConditionDeclarationAlignment
    outcome: StateConditionOutcome


_CONTEXT = TypeAdapter(AssertionContext)


class StateClassificationResult(_Frozen):
    state: StateDeclarationResult
    state_anchor_id: StrictStr = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    as_of: UtcDatetime
    ruleset_version: Literal["st001.1"]
    condition_sources: tuple[StateConditionSource, ...]
    constraint_evaluations: tuple[ConstraintEvaluationResult, ...]
    conditions: tuple[StateClassificationConditionResult, ...]
    condition_coverage: StateConditionCoverage
    temporal_alignment: StateTemporalAlignment
    execution: StateClassificationExecution
    refusals: tuple[StateClassificationRefusal, ...]
    computed_match: StateComputedMatch | None = None

    @model_validator(mode="before")
    @classmethod
    def _reconstruct_all_inputs(cls, value):
        payload = dict(_dump(value)) if isinstance(_dump(value), Mapping) else value
        if not isinstance(payload, dict):
            return payload
        if "state" in payload:
            payload["state"] = _dump(payload["state"])
        if "context" in payload:
            payload["context"] = _dump(payload["context"])
        for field, contract, label in (
            ("condition_sources", StateConditionSource, "condition sources"),
            ("constraint_evaluations", ConstraintEvaluationResult,
             "constraint evaluations"),
            ("conditions", StateClassificationConditionResult,
             "condition rows"),
            ("refusals", StateClassificationRefusal, "refusals"),
        ):
            if field in payload:
                payload[field] = _rebuild_tuple(
                    payload[field], contract, label)
        return payload

    @model_validator(mode="after")
    def _authoritative(self):
        from backend.state_classification.derivation import derive_classification

        expected = derive_classification(
            state=self.state,
            state_anchor_id=self.state_anchor_id,
            context=self.context,
            as_of=self.as_of,
            condition_sources=self.condition_sources,
            constraint_evaluations=self.constraint_evaluations,
        )
        supplied = self.model_dump(
            mode="python",
            exclude={
                "state", "state_anchor_id", "context", "as_of",
                "condition_sources", "constraint_evaluations",
            },
            warnings=False,
        )
        if supplied != expected:
            raise ValueError("state classification disclosure is forged")
        return self
