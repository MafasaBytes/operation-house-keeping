"""VS-001 observation-compatibility facade.

Read-only, composition-only: one injected accepted query object, from
whose exact public loaded model the kernel query is constructed — so a
membership/specification revision mismatch is unconstructible. Lower-layer
results are carried verbatim; no tips, conflicts, superseded sets, or
registration statuses are recomputed here.

Evidence is parsed with the accepted ingestion policy (lossless numbers,
non-finite constants rejected) and NEVER converted with ``float``: a
`1E+999` lexeme would become infinity and a 400-digit integer raises
``OverflowError``, which is not a ``ValueError`` and would escape the
typed contract. Contradictory evidence is an outcome, never an exception,
and never an ordinary specification incompatibility.
"""

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from backend.model_kernel import ModelQueries
from backend.model_state import ModelStateQueries, SourceSelector
from backend.observation_compatibility.contracts import (
    CandidateValueCompatibility,
    ObservationCompatibilityConfigurationError,
    VariableValueCompatibilityResult,
)

_RULESET_VERSION = "vs001.1"
_JSON_TYPES = frozenset(
    {"object", "array", "string", "number", "boolean", "null"})


def _reject_constant(name: str):
    raise ValueError(f"non-finite JSON constant {name!r} rejected")


def _parse_shape(value_json: str):
    """Return the JSON shape the stored lexeme actually preserves, or None
    when it cannot be parsed. ``bool`` is tested before ``int`` so a Python
    boolean never enters number handling."""
    try:
        value = json.loads(value_json, parse_float=Decimal, parse_int=int,
                           parse_constant=_reject_constant)
    except (json.JSONDecodeError, ValueError, InvalidOperation):
        return None
    if isinstance(value, bool):
        return "boolean"
    if value is None:
        return "null"
    if isinstance(value, (int, Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


class ObservationCompatibilityQueries:
    def __init__(self, state: ModelStateQueries) -> None:
        if not isinstance(state, ModelStateQueries):
            raise ObservationCompatibilityConfigurationError(
                "OBSERVATION_COMPATIBILITY_INPUT_INVALID",
                "composition requires a ModelStateQueries instance")
        self.state = state
        # the EXACT public loaded model the state facade uses
        self.model_queries = ModelQueries(state.model)

    def variable_value_compatibility(
        self, variable_anchor_id: str, *, as_of: datetime,
        entity_anchor_id: str | None = None,
        source: SourceSelector | None = None,
    ) -> VariableValueCompatibilityResult:
        """Assess a model variable's declared value representation against
        the evidence attached to it. Request validation, including naive
        cutoffs and forged selectors, belongs to the accepted VM-001
        boundary and its typed errors propagate unchanged."""
        state = self.state.variable_state(
            variable_anchor_id, as_of=as_of, entity_anchor_id=entity_anchor_id,
            source=source)
        specification_result = self.model_queries.variable_value_specification(
            variable_anchor_id)

        specified = specification_result.status == "specified"
        specification = specification_result.specification
        model_unit = ("not_evaluated" if not specified
                      else "declared" if specification.unit.kind == "declared"
                      else "not_declared")

        candidates = tuple(
            self._assess(candidate, specification_result, specification,
                         model_unit)
            for candidate in state.candidates)

        return VariableValueCompatibilityResult(
            variable_anchor_id=state.variable_anchor_id, as_of=state.as_of,
            ruleset_version=_RULESET_VERSION, state=state,
            specification_result=specification_result,
            model_unit_specification=model_unit, candidates=candidates)

    def _assess(self, candidate, specification_result, specification,
                model_unit) -> CandidateValueCompatibility:
        observed = candidate.bound is not None
        occurrence = candidate.bound.observed.occurrence if observed else None
        attached = candidate.attachment == "attached"
        status = specification_result.status

        # -- evidence consistency and presence (observation-only facts)
        if not observed:
            consistency, presence, shape = "not_evaluated", "no_observation", None
        elif occurrence.json_type not in _JSON_TYPES:
            consistency, presence, shape = ("json_type_unrecognized",
                                            "indeterminate", None)
        else:
            parsed = _parse_shape(occurrence.value_json)
            if parsed is None:
                consistency, presence, shape = ("value_json_malformed",
                                                "indeterminate", None)
            elif parsed != occurrence.json_type:
                # neither field is repaired and neither is preferred
                consistency, presence, shape = ("shape_disagreement",
                                                "indeterminate", None)
            else:
                consistency, shape = "consistent", parsed
                presence = ("explicit_null" if parsed == "null"
                            else "value_present")

        # -- source-unit disclosure: independent of attachment
        if not observed:
            source_unit = "not_evaluated"
        else:
            source_unit = ("present" if occurrence.declared_unit is not None
                           else "absent")

        # -- shape verdict, gated on evidence consistency
        shape_reason = self._shape_reason(observed, attached, status,
                                          consistency)
        if shape_reason is not None:
            shape_verdict, finding = "not_evaluated", None
        else:
            satisfies, finding = self._shape_verdict(shape, specification)
            shape_verdict = ("satisfies_specification" if satisfies
                             else "does_not_satisfy_specification")

        # -- lexical relation, NOT gated on evidence consistency
        unit_reason = self._unit_reason(observed, attached, status, model_unit,
                                        source_unit)
        if unit_reason is not None:
            relation = "not_evaluated"
        else:
            relation = ("declared_lexeme_identical"
                        if occurrence.declared_unit == specification.unit.unit.code
                        else "declared_lexeme_differs")

        return CandidateValueCompatibility(
            state_candidate=candidate, value_presence=presence,
            evidence_consistency=consistency, observed_shape=shape,
            value_shape_compatibility=shape_verdict,
            value_shape_finding=finding,
            value_shape_not_evaluated_reason=shape_reason,
            source_unit_evidence=source_unit,
            declared_unit_lexeme_relation=relation,
            unit_lexeme_not_evaluated_reason=unit_reason)

    @staticmethod
    def _shape_reason(observed, attached, status, consistency):
        """Independent precedence: a conflicted specification suppresses the
        verdict but never overrides an earlier clause."""
        if not observed:
            return "no_observation"
        if not attached:
            return "observation_not_attached"
        if status == "conflicted":
            return "specification_conflicted"
        if status in ("not_specified", "not_registered"):
            return "specification_not_available"
        if consistency != "consistent":
            return "evidence_not_assessable"
        return None

    @staticmethod
    def _unit_reason(observed, attached, status, model_unit, source_unit):
        if not observed:
            return "no_observation"
        if not attached:
            return "observation_not_attached"
        if status == "conflicted":
            return "specification_conflicted"
        if status in ("not_specified", "not_registered"):
            return "specification_not_available"
        if model_unit != "declared":
            # the model-side absence governs: no comparison could exist
            return "model_unit_not_declared"
        if source_unit != "present":
            return "source_unit_absent"
        return None

    @staticmethod
    def _shape_verdict(shape, specification):
        if shape == "null":
            return (specification.nullable,
                    "explicit_null_allowed" if specification.nullable
                    else "explicit_null_not_allowed")
        if shape in ("array", "object"):
            return False, "unsupported_observed_structure"
        if shape == specification.value_shape:
            return True, "shape_matches"
        return False, "shape_differs"
