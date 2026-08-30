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
        _assert_no_hidden_instance_fields(value)
        return value


def _assert_no_hidden_instance_fields(value):
    """Walk arbitrary carried content without trusting model serialization."""
    strict_names = {"sweep_position"}

    def require_strict_named_ints(items):
        for name, field_value in items:
            if (isinstance(name, str)
                    and (name.endswith("_index")
                         or name.endswith("_count")
                         or name in strict_names)
                    and field_value is not None
                    and type(field_value) is not int):
                raise ValueError(f"{name} must be a strict integer")

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
            require_strict_named_ints(
                (name, stored[name]) for name in fields if name in stored)
            pending.extend(stored[name] for name in fields if name in stored)
        elif isinstance(item, Mapping):
            require_strict_named_ints(item.items())
            pending.extend(item.keys())
            pending.extend(item.values())
        elif isinstance(item, (tuple, list, set, frozenset)):
            pending.extend(item)


def _dump(value):
    return (value.model_dump(mode="python", warnings=False)
            if isinstance(value, BaseModel) else value)


def _serialized_shape(value):
    """Describe every mapping key and sequence position, but not leaf values."""
    signature = []
    pending = [("visit", (), value, 0)]
    active: set[int] = set()
    node_count = 0
    while pending:
        operation, path, item, depth = pending.pop()
        if operation == "exit":
            active.remove(item)
            continue
        node_count += 1
        if node_count > 200_000:
            raise ValueError("serialized model shape exceeds the node limit")
        if depth > 128:
            raise ValueError("serialized model shape exceeds the depth limit")
        item = _dump(item)
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in active:
                raise ValueError("serialized model shape is cyclic")
            active.add(identity)
            if any(not isinstance(key, str) for key in item):
                raise ValueError("serialized model mappings require string keys")
            keys = tuple(sorted(item))
            signature.append((path, "mapping", keys))
            pending.append(("exit", (), identity, 0))
            for key in reversed(keys):
                pending.append(("visit", (*path, key), item[key], depth + 1))
        elif isinstance(item, (tuple, list)):
            identity = id(item)
            if identity in active:
                raise ValueError("serialized model shape is cyclic")
            active.add(identity)
            signature.append((path, "sequence", len(item)))
            pending.append(("exit", (), identity, 0))
            for index in range(len(item) - 1, -1, -1):
                pending.append((
                    "visit", (*path, index), item[index], depth + 1))
        else:
            signature.append((path, "leaf", None))
    return tuple(signature)


def _rebuild_content(value, contract, label):
    raw = _dump(value)
    rebuilt = contract.model_validate(raw)
    content = rebuilt.model_dump(mode="python", warnings=False)
    if _serialized_shape(raw) != _serialized_shape(content):
        raise ValueError(f"{label} serialized shape changed during reconstruction")
    return content


def _rebuild_tuple(value, contract, label):
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{label} must be a tuple")
    # Return serialized content. The annotated field contract performs its
    # final reconstruction after the hidden-instance guard has seen a
    # content-only graph. Shape equality prevents permissive legacy lower
    # contracts from silently discarding raw nested mapping keys.
    return tuple(_rebuild_content(item, contract, label) for item in value)


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
        _assert_no_hidden_instance_fields(value)
        payload = dict(_dump(value)) if isinstance(_dump(value), Mapping) else value
        if not isinstance(payload, dict):
            return payload
        if "state" in payload:
            payload["state"] = _rebuild_content(
                payload["state"], StateDeclarationResult, "state result")
        if "context" in payload:
            raw_context = _dump(payload["context"])
            rebuilt_context = _CONTEXT.validate_python(raw_context)
            context_content = rebuilt_context.model_dump(
                mode="python", warnings=False)
            if _serialized_shape(raw_context) != _serialized_shape(
                    context_content):
                raise ValueError(
                    "context serialized shape changed during reconstruction")
            payload["context"] = context_content
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
