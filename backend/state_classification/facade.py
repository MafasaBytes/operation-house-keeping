"""Read-only ST-001 state-classification facade."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from pydantic import BaseModel, TypeAdapter, ValidationError

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.model_kernel import AssertionContext, ModelQueries
from backend.state_classification.contracts import (
    StateClassificationResult,
    StateConditionSource,
    _assert_no_hidden_instance_fields,
)
from backend.state_classification.derivation import derive_classification
from backend.state_classification.errors import (
    StateClassificationConfigurationError,
    StateClassificationInputError,
)
from backend.system_identity import STATE_ANCHOR_ID_PATTERN


_CONTEXT = TypeAdapter(AssertionContext)


def _input_error(message):
    return StateClassificationInputError(
        "STATE_CLASSIFICATION_INPUT_INVALID", message)


def _dump(value):
    return (value.model_dump(mode="python", warnings=False)
            if isinstance(value, BaseModel) else value)


class StateClassificationQueries:
    """Compose one exact-context state declaration with explicit CN paths."""

    def __init__(self, constraints: ConstraintEvaluationQueries) -> None:
        if not isinstance(constraints, ConstraintEvaluationQueries):
            raise StateClassificationConfigurationError(
                "STATE_CLASSIFICATION_CONFIGURATION_INVALID",
                "composition requires constraint evaluation queries",
            )
        self.constraints = constraints

    def state_classification(
        self,
        state_anchor_id,
        *,
        context,
        as_of,
        condition_sources,
    ) -> StateClassificationResult:
        state_anchor_id, context, as_of, sources = self._validate_request(
            state_anchor_id, context, as_of, condition_sources)
        model = self.constraints.semantic.compatibility.state.model
        queries = ModelQueries(model)
        lookup = queries.state(state_anchor_id)
        state = queries.state_declaration(state_anchor_id, context=context)

        if lookup.registration_index is None:
            if sources:
                raise _input_error(
                    "an unregistered state admits only empty condition sources")
            evaluations = ()
        else:
            registration = lookup.registration
            requested = tuple(item.constraint_anchor_id for item in sources)
            if requested != registration.condition_constraint_anchor_ids:
                raise _input_error(
                    "condition sources must equal the permanent constraint set")
            results = [None] * len(sources)
            failures = [None] * len(sources)
            for index, source in enumerate(sources):
                try:
                    results[index] = self.constraints.constraint_evaluation(
                        source.constraint_anchor_id,
                        as_of=as_of,
                        entity_anchor_id=registration.subject_entity_anchor_id,
                        source=source.source,
                    )
                except Exception as error:  # lower typed failures propagate below
                    failures[index] = error
            for failure in failures:
                if failure is not None:
                    raise failure
            evaluations = tuple(results)

        derived = derive_classification(
            state=state,
            state_anchor_id=state_anchor_id,
            context=context,
            as_of=as_of,
            condition_sources=sources,
            constraint_evaluations=evaluations,
        )
        return StateClassificationResult(
            state=state,
            state_anchor_id=state_anchor_id,
            context=context,
            as_of=as_of,
            condition_sources=sources,
            constraint_evaluations=evaluations,
            **derived,
        )

    @staticmethod
    def _validate_request(state_anchor_id, context, as_of, condition_sources):
        if (
            not isinstance(state_anchor_id, str)
            or re.fullmatch(STATE_ANCHOR_ID_PATTERN, state_anchor_id) is None
        ):
            raise _input_error("state_anchor_id is malformed")
        try:
            _assert_no_hidden_instance_fields((context, condition_sources))
            context = _CONTEXT.validate_python(_dump(context))
            if (not isinstance(as_of, datetime)
                    or as_of.tzinfo is None
                    or as_of.tzinfo.utcoffset(as_of) is None):
                raise ValueError("as_of must be a timezone-aware datetime")
            as_of = as_of.astimezone(UTC)
            if not isinstance(condition_sources, (tuple, list)):
                raise ValueError("condition_sources must be a tuple")
            if len(condition_sources) > 64:
                raise ValueError("at most 64 condition sources are permitted")
            sources = tuple(
                StateConditionSource.model_validate(item)
                for item in condition_sources)
        except (ValidationError, ValueError, TypeError, AttributeError) as error:
            raise _input_error(
                "classification request is structurally invalid") from error
        ids = tuple(item.constraint_anchor_id for item in sources)
        if len(set(ids)) != len(ids):
            raise _input_error("condition sources must be unique")
        return state_anchor_id, context, as_of, tuple(
            sorted(sources, key=lambda item: item.constraint_anchor_id))
