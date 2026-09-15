"""S3 only: exact target assessment and conservative nominated-action selection.

No prior-world dependency review, filesystem, CLI or backend store ownership.
"""
from dataclasses import dataclass
from fractions import Fraction
import json

from applications.bounded_decision_workflow.admission import admit_request_and_snapshot
from applications.bounded_decision_workflow.input import effective_limits
from applications.bounded_decision_workflow.policy_profile import (
    ACTION_IDS, policy_values, validate_policy_structure,
)
from applications.bounded_decision_workflow.projection import (
    RawProjectionReview, _gate, _number, _output_refusal, _project_admitted, _serialize,
)
from applications.bounded_decision_workflow.projection_profile import (
    projection_supports, validate_profile_structure,
)


@dataclass(frozen=True, slots=True)
class PolicyReview:
    """Immutable slice result, not the S5/S6 retained result.json/trace.json.

The admitted request retains every policy premise's identity and provenance.
Accessors return detached values. Raw and current-condition answers stay separate.
"""
    projection: RawProjectionReview
    policy_bytes: bytes
    policy_trace_bytes: bytes

    @property
    def target_relations(self):
        return json.loads(self.policy_bytes)["target_relations"]

    @property
    def feasibility(self):
        return json.loads(self.policy_bytes)["feasibility"]

    @property
    def selection(self):
        return json.loads(self.policy_bytes)["selection"]

    @property
    def policy_trace(self):
        return json.loads(self.policy_trace_bytes)


def _target_relation(status, interval, target):
    if status == "inapplicable":
        return "inapplicable"
    if status == "unknown" or target is None:
        return "unknown"
    lo, hi = interval
    lower, upper = target
    if lower <= lo and hi <= upper:
        return "guaranteed"
    if hi < lower or upper < lo:
        return "incompatible"
    return "possible_not_guaranteed"


def _feasibility(relations, *, false_gate=False, supported=True):
    # Nonempty retained rows are validated before this internal total function.
    if false_gate:
        return "inapplicable"
    if not supported or "unknown" in relations:
        return "unknown"
    if all(r == "guaranteed" for r in relations):
        return "guaranteed"
    if "incompatible" in relations:
        return "incompatible"
    return "possible_not_guaranteed"


def _selection(feasibility, costs, *, global_false=False, supported=True):
    result = {"disposition": "unknown", "minimum_cost": None, "selected_action_ids": []}
    eligible = [a for a in ACTION_IDS if feasibility[a] == "guaranteed"]
    unknown = [a for a in ACTION_IDS if feasibility[a] == "unknown"]
    if global_false:
        result["disposition"] = "inapplicable_for_declared_model"
    elif not supported:
        pass
    elif not eligible:
        if not unknown:
            result["disposition"] = "no_feasible_action_in_supplied_set"
    elif all(costs[a] is not None for a in eligible):
        minimum = min(costs[a] for a in eligible)
        if all(costs[a] is not None and costs[a] > minimum for a in unknown):
            result.update(disposition="selected_from_supplied_set", minimum_cost=_number(minimum),
                          selected_action_ids=[a for a in eligible if costs[a] == minimum])
    return result


def assess_request_and_snapshot(request_wire: bytes, snapshot_wire: bytes) -> PolicyReview:
    """Admit public evidence, project assumed effects, then assess supplied policy.

No caller-created admission/result object is accepted; no expected result is read.
All premise structure is checked before any projection arithmetic.
"""
    admission = admit_request_and_snapshot(request_wire, snapshot_wire)
    request = admission.request
    limits = effective_limits(request)
    validate_profile_structure(request)
    validate_policy_structure(request)
    supports = projection_supports(request, limits)
    target, costs, retained = policy_values(request, limits)
    raw = _project_admitted(admission, limits, supports)
    p = request.target_policy
    rows = raw.raw_projections
    targets, traces = [], []
    for row in rows:
        interval = row["raw_interval"]
        bounds = None if interval is None else tuple(
            Fraction(interval[k]["numerator"], interval[k]["denominator"]) for k in ("lower", "upper"))
        relation = _target_relation(row["raw_status"], bounds, target)
        targets.append({"action_id": row["action_id"], "hypothesis_id": row["hypothesis_id"],
                        "target_relation": relation})
        traces.append({"layer": "target", "action_id": row["action_id"],
                       "hypothesis_id": row["hypothesis_id"], "result": relation,
                       "premise_ids": [p.target.premise_id]})
    feasible = {}
    for action in ACTION_IDS:
        selected_rows = [r["target_relation"] for r in targets
                         if r["action_id"] == action and retained is not None and r["hypothesis_id"] in retained]
        false = any(r["raw_status"] == "inapplicable" for r in rows if r["action_id"] == action)
        feasible[action] = _feasibility(selected_rows, false_gate=false,
                                       supported=retained is not None and p.feasibility_rule.availability == "present")
        traces.append({"layer": "feasibility", "action_id": action, "result": feasible[action],
                       "premise_ids": [p.retained_hypotheses.premise_id, p.feasibility_rule.premise_id]})
    selection = _selection(feasible, costs,
                           global_false=_gate(request.premises.global_applicability) is False,
                           supported=p.selection_rule.availability == "present")
    traces.append({"layer": "selection", "result": selection["disposition"],
                   "premise_ids": [p.costs.premise_id, p.selection_rule.premise_id]})
    result = {"target_relations": targets,
              "feasibility": [{"action_id": a, "feasibility": feasible[a]} for a in ACTION_IDS],
              "selection": selection}
    trace = {"trace_version": "bdw001.policy.v1", "request_commitment": admission.request_input.sha256,
             "snapshot_commitment": admission.snapshot_input.sha256,
             "meaning": "computed_under_supplied_policy_not_global_optimality",
             "rows": traces,
             "unavailable_policy_ids": sorted(v.premise_id for v in (
                 p.target, p.costs, p.retained_hypotheses, p.feasibility_rule, p.selection_rule)
                 if v.availability != "present"),
             "unavailable_cost_action_ids": [a for a in ACTION_IDS if costs[a] is None]}
    # Charge combined S2/S3 results and traces, not each layer its own full budget.
    if len(traces) + len(rows) > limits["output_trace_rows"]:
        raise _output_refusal()
    _serialize(dict(result, raw_projections=rows), limits["output_result_bytes"], limits["output_result_nodes"])
    _serialize({"raw": raw.raw_trace, "policy": trace}, limits["output_trace_bytes"])
    return PolicyReview(raw, _serialize(result, limits["output_result_bytes"], limits["output_result_nodes"]),
                        _serialize(trace, limits["output_trace_bytes"]))
