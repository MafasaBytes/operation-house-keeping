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


class _NonFiniteConstant(ValueError):
    """NaN/Infinity are not JSON: malformed text, not an unrepresentable
    value."""


def _reject_constant(name: str):
    raise _NonFiniteConstant(f"non-finite JSON constant {name!r} rejected")


def _parse_shape(value_json: str):
    """Return (shape, failure) for the stored lexeme. ``bool`` is tested
    before ``int`` so a Python boolean never enters number handling.

    Two failures are distinguished honestly: text that is not JSON is
    `malformed`, while well-formed JSON this interpreter cannot represent
    (a digit string beyond ``int_max_str_digits``, an exponent Decimal
    rejects, nesting past the recursion limit) is `not_representable` — the
    evidence is not at fault and must not be called malformed."""
    try:
        value = json.loads(value_json, parse_float=Decimal, parse_int=int,
                           parse_constant=_reject_constant)
    except (json.JSONDecodeError, _NonFiniteConstant):
        return None, "value_json_malformed"
    except (ValueError, InvalidOperation, RecursionError):
        return None, "value_not_representable"
    if isinstance(value, bool):
        return "boolean", None
    if value is None:
        return "null", None
    if isinstance(value, (int, Decimal)):
        return "number", None
    if isinstance(value, str):
        return "string", None
    if isinstance(value, list):
        return "array", None
    return "object", None


class ObservationCompatibilityQueries:
    def __init__(self, state: ModelStateQueries) -> None:
        if not isinstance(state, ModelStateQueries):
            raise ObservationCompatibilityConfigurationError(
                "OBSERVATION_COMPATIBILITY_INPUT_INVALID",
                "composition requires a ModelStateQueries instance")
        self.state = state

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
        # built per call from the EXACT public loaded model the state
        # facade just used, so a membership/specification revision
        # mismatch is structurally impossible rather than merely detected
        specification_result = ModelQueries(
            self.state.model).variable_value_specification(variable_anchor_id)

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
            parsed, failure = _parse_shape(occurrence.value_json)
            if parsed is None:
                consistency, presence, shape = (failure, "indeterminate",
                                                None)
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
            shape_verdict = ("satisfies_value_shape" if satisfies
                             else "does_not_satisfy_value_shape")

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
