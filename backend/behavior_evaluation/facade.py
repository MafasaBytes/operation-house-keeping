"""Read-only BH-001 evidence-gated evaluation facade."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import TypeAdapter, ValidationError

from backend.behavior_evaluation.contracts import (
    BehaviorEvaluationResult,
    BehaviorParticipantSource,
    UtcDatetime,
)
from backend.behavior_evaluation.derivation import derive_evaluation
from backend.behavior_evaluation.errors import (
    BehaviorEvaluationConfigurationError,
    BehaviorEvaluationInputError,
)
from backend.model_kernel import AssertionContext, ModelQueries
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.system_identity import BEHAVIOR_ANCHOR_ID_PATTERN


_CONTEXT = TypeAdapter(AssertionContext)


def _input_error(message):
    return BehaviorEvaluationInputError(
        "BEHAVIOR_EVALUATION_INPUT_INVALID", message)


class BehaviorEvaluationQueries:
    """Compose explicit BH declarations with two explicit ES paths.

    The facade owns no store and persists no result. It intentionally exposes
    no source discovery or candidate-selection API.
    """

    def __init__(self, semantic: SemanticCompatibilityQueries) -> None:
        if not isinstance(semantic, SemanticCompatibilityQueries):
            raise BehaviorEvaluationConfigurationError(
                "BEHAVIOR_EVALUATION_CONFIGURATION_INVALID",
                "composition requires semantic compatibility queries",
            )
        self.semantic = semantic

    def behavior_evaluation(
        self,
        behavior_anchor_id,
        *,
        context,
        as_of,
        participants,
    ) -> BehaviorEvaluationResult:
        behavior_anchor_id, context, as_of, participants = (
            self._validate_request(
                behavior_anchor_id, context, as_of, participants))
        model = self.semantic.compatibility.state.model
        behavior = ModelQueries(model).behavior_declaration(
            behavior_anchor_id, context=context)

        if behavior.registration_index is not None:
            registration = behavior.material.record_at(
                behavior.registration_index)
            requested = tuple(source.variable_anchor_id
                              for source in participants)
            if requested != registration.participant_variable_anchor_ids:
                raise _input_error(
                    "participant variables must equal the registered pair")

        results = [None, None]
        failures = [None, None]
        for index, source in enumerate(participants):
            try:
                results[index] = self.semantic.variable_semantic_compatibility(
                    source.variable_anchor_id,
                    as_of=as_of,
                    entity_anchor_id=source.entity_anchor_id,
                    source=source.source,
                )
            except Exception as error:  # typed lower failures propagate below
                failures[index] = error
        for failure in failures:
            if failure is not None:
                raise failure

        semantic_results = tuple(results)
        derived = derive_evaluation(
            behavior=behavior,
            behavior_anchor_id=behavior_anchor_id,
            context=context,
            as_of=as_of,
            participant_sources=participants,
            semantic_results=semantic_results,
        )
        return BehaviorEvaluationResult(
            behavior=behavior,
            behavior_anchor_id=behavior_anchor_id,
            context=context,
            as_of=as_of,
            participant_sources=participants,
            participant_semantic_results=semantic_results,
            **derived,
        )

    @staticmethod
    def _validate_request(behavior_anchor_id, context, as_of, participants):
        if (not isinstance(behavior_anchor_id, str)
                or re.fullmatch(BEHAVIOR_ANCHOR_ID_PATTERN,
                                 behavior_anchor_id) is None):
            raise _input_error("behavior_anchor_id is malformed")
        try:
            context = _CONTEXT.validate_python(
                context.model_dump(mode="python", warnings=False)
                if hasattr(context, "model_dump") else context)
            as_of = TypeAdapter(UtcDatetime).validate_python(as_of)
            if not isinstance(participants, (tuple, list)):
                raise ValueError("participants must be a tuple")
            rebuilt = tuple(BehaviorParticipantSource.model_validate(
                participant.model_dump(mode="python", warnings=False)
                if hasattr(participant, "model_dump") else participant)
                for participant in participants)
        except (ValidationError, ValueError, TypeError) as error:
            raise _input_error("evaluation request is structurally invalid") from error
        if len(rebuilt) != 2:
            raise _input_error("exactly two participant sources are required")
        variable_ids = tuple(item.variable_anchor_id for item in rebuilt)
        if len(set(variable_ids)) != 2:
            raise _input_error("participant variables must be distinct")
        return behavior_anchor_id, context, as_of, tuple(
            sorted(rebuilt, key=lambda item: item.variable_anchor_id))
