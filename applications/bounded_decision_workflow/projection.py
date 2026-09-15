"""Bounded raw projection only; no policy, execution, observation writes or I/O."""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from itertools import product
import json
from math import prod

from applications.bounded_decision_workflow.admission import (
    AdmissionReview, admit_request_and_snapshot,
)
from applications.bounded_decision_workflow.errors import refusal
from applications.bounded_decision_workflow.input import _count, effective_limits
from applications.bounded_decision_workflow.projection_profile import (
    ACTIONS, check_number, numeric_limit, validate_profile,
)


@dataclass(frozen=True, slots=True)
class RawProjectionReview:
    """Immutable S2 result bytes; admission retains the complete premise provenance.

    This is not the final result.json/trace.json or a retained workflow bundle.
    Accessors return detached JSON values; mutating them cannot change evidence.
    """

    admission: AdmissionReview
    raw_projection_bytes: bytes
    raw_trace_bytes: bytes
    corner_evaluations: int

    @property
    def raw_projections(self):
        return json.loads(self.raw_projection_bytes)

    @property
    def raw_trace(self):
        return json.loads(self.raw_trace_bytes)


def _number(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def _interval(lower, upper):
    return {"endpoint_semantics": "closed", "lower": _number(lower),
            "upper": _number(upper), "unit_role": "degree_celsius"}


def _observed_fraction(text, digits):
    # Bound decimal scaling BEFORE constructing powers of ten or a Fraction.
    decimal = Decimal(text)
    _, coefficient, exponent = decimal.as_tuple()
    if (len(coefficient) + max(0, exponent) > digits
            or max(0, -exponent) + 1 > digits):
        raise numeric_limit()
    return check_number(Fraction(decimal), digits)


def _output_refusal():
    return refusal("OUTPUT_LIMIT_EXCEEDED", stage="output_resource",
                   target="result_or_trace", retry="reduce_input", exit_code=4)


def _serialize(value, ceiling, node_ceiling=None):
    # Bounded incrementally: never allocate an over-ceiling encoded result.
    if node_ceiling is not None and _count(
            value, wire_bytes=0, canonical_bytes=0).nodes > node_ceiling:
        raise _output_refusal()
    result = bytearray()
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False,
                               sort_keys=True, separators=(",", ":"))
    for chunk in encoder.iterencode(value):
        wire = chunk.encode("utf-8")
        if len(result) + len(wire) > ceiling:
            raise _output_refusal()
        result.extend(wire)
    return bytes(result)


def _gate(premise):
    return premise.value["status"] if premise.availability == "present" else None


def project_request_and_snapshot(request_wire: bytes, snapshot_wire: bytes) -> RawProjectionReview:
    """Reenter S1 admission, then derive eight raw rows under declared assumptions.

    Accepts bytes, not caller-created admission objects or caller numbers. All
    profile/edition failures precede arithmetic. Target/cost content is carried by
    S1 but is neither interpreted nor used here. No expected-output file is read.
    """
    admission = admit_request_and_snapshot(request_wire, snapshot_wire)
    request = admission.request
    limits = effective_limits(request)
    supports = validate_profile(request, limits)
    p = request.premises
    digits = limits["exact_rational_digits_per_integer"]
    observed = admission.observed_value
    t0 = (_observed_fraction(observed.canonical_decimal, digits)
          if observed.status == "admitted" else None)
    supports["T0"] = None if t0 is None else (t0, t0)
    names = ("T0", "A", "alpha", "gamma", "beta")
    common = [p.actions, p.commands, p.global_applicability, p.hypotheses,
              p.law, p.support_semantics, *p.coordinates.values()]

    # Establish every gate/frontier and total work before computing any corners.
    plans = []
    for hypothesis_id in ("H_F", "H_H"):
        for action in ACTIONS:
            gates = [p.global_applicability]
            for field, group in (("precondition_ids", p.preconditions),
                                 ("timing_ids", p.timing), ("invariance_ids", p.invariances)):
                gates.extend(group[key] for key in action[field])
            required = common + gates + [p.effects[key] for key in action["effect_ids"]]
            false = sorted({v.premise_id for v in gates if _gate(v) is False})
            unknown = sorted({v.premise_id for v in required if v.availability != "present"})
            if t0 is None:
                unknown.append("observed:T0")
            status = "inapplicable" if false else "unknown" if unknown else "ready"
            plans.append((hypothesis_id, action, status, false or unknown,
                          sorted({v.premise_id for v in required})))
    endpoints = [tuple(dict.fromkeys(supports[k])) if supports[k] is not None else ()
                 for k in names]
    corners_per_row = prod(map(len, endpoints))
    total = sum(status == "ready" for _, _, status, _, _ in plans) * corners_per_row
    if total > limits["corner_evaluations"]:
        raise refusal("INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
                      target="corner_evaluations", retry="reduce_input", exit_code=4)
    if len(plans) > limits["output_trace_rows"]:
        raise _output_refusal()

    rows, traces = [], []
    for hypothesis_id, action, status, frontier, premise_ids in plans:
        raw = None
        corners = []
        before = after = None
        if status == "ready":
            hypothesis = next(v for v in p.hypotheses.value if v["hypothesis_id"] == hypothesis_id)
            before = {k: (p.commands.value[v] if isinstance(v, str) else v)
                      for k, v in hypothesis["mapping"].items()}
            after = dict(before)
            for effect_id in action["effect_ids"]:
                # Effect values come only from the admitted application body.
                after.update(p.effects[effect_id].value["assignments"])
            values = []
            for indices in product(*(range(len(v)) for v in endpoints)):
                T0, A, alpha, gamma, beta = (
                    points[index] for points, index in zip(endpoints, indices))
                heating = check_number(alpha * after["h"], digits)
                cooling = check_number(gamma * after["f"], digits)
                difference = check_number(T0 - A, digits)
                loss = check_number(beta * difference, digits)
                value = check_number(check_number(check_number(T0 + heating, digits)
                                                 - cooling, digits) - loss, digits)
                values.append(value)
                corners.append({"endpoint_indices": list(indices), "value": _number(value)})
            raw = _interval(min(values), max(values))
        rows.append({"action_id": action["action_id"], "hypothesis_id": hypothesis_id,
                     "raw_status": status, "raw_interval": raw})
        traces.append({"action_id": action["action_id"], "hypothesis_id": hypothesis_id,
                       "raw_status": status, "effect_ids": action["effect_ids"],
                       "premise_ids": premise_ids, "frontier_ids": frontier,
                       "before_effect": before, "after_effect": after, "corners": corners})
    trace = {
        "trace_version": "bdw001.raw.v1",
        "request_commitment": admission.request_input.sha256,
        "snapshot_commitment": admission.snapshot_input.sha256,
        "meaning": "computed_under_supplied_synthetic_assumptions_not_execution",
        "coordinate_order": list(names),
        "coordinate_endpoints": {k: [_number(v) for v in points]
                                 for k, points in zip(names, endpoints)},
        "corner_evaluations": total, "projection_rows": traces,
    }
    return RawProjectionReview(
        admission=admission,
        raw_projection_bytes=_serialize(rows, limits["output_result_bytes"], limits["output_result_nodes"]),
        raw_trace_bytes=_serialize(trace, limits["output_trace_bytes"]),
        corner_evaluations=total,
    )
