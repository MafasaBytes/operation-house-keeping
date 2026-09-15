"""Fixed S3 policy premises; caller assertions never become backend records."""
from applications.bounded_decision_workflow.errors import refusal
from applications.bounded_decision_workflow.projection_profile import (
    _body, _malformed, _rational_shape, _schema, bounded_fraction, reject_profile,
)

ACTION_IDS = ("a0", "aF", "aH", "aHF")
FEASIBILITY = {"kind": "robust_over_retained_hypotheses.v1"}
SELECTION = {"global_minimality": False, "kind": "minimum_cost_among_guaranteed.v1",
             "ties": "retain_all_canonical_action_id_order"}


def _available_body(p):
    return p.value is not None or p.availability == "present"


def validate_policy_lexical(request):
    """Numeric shapes are admission schema, before reconstruction and arithmetic."""
    p = request.target_policy
    if _available_body(p.target):
        v = p.target.value
        if type(v) is not dict or set(v) != {"lower", "upper", "endpoint_semantics", "unit_role"}:
            raise _schema()
        for key in ("lower", "upper"):
            _rational_shape(v[key])
    if _available_body(p.costs):
        v = p.costs.value
        if type(v) is not dict or set(v) != {"cost_token", "entries"} or type(v["entries"]) is not list:
            raise _schema()
        for entry in v["entries"]:
            if (type(entry) is not dict or set(entry) != {"action_id", "availability", "cost"}
                    or entry["availability"] not in ("present", "missing", "unknown", "stale_reference")):
                raise _schema()
            if entry["cost"] is not None or entry["availability"] == "present":
                _rational_shape(entry["cost"])


def validate_policy_structure(request):
    p = request.target_policy
    for name, expected in (("target", "P-target"), ("costs", "P-cost"),
                           ("retained_hypotheses", "P-retained"),
                           ("feasibility_rule", "P-feasibility"), ("selection_rule", "P-selection")):
        premise = getattr(p, name)
        if premise.premise_id != expected or premise.epistemic_kind != "application_policy":
            raise reject_profile()
        if premise.edition != 1:
            raise refusal("EDITION_MISMATCH", stage="profile_cardinality_edition",
                          target="premise_edition", retry="update_complete_world")
        if premise.availability == "stale_reference":
            raise refusal("STALE_REFERENCE", stage="profile_cardinality_edition",
                          target="premise_reference", retry="update_complete_world")
    _body(p.feasibility_rule, FEASIBILITY)
    _body(p.selection_rule, SELECTION)
    if _available_body(p.retained_hypotheses):
        v = p.retained_hypotheses.value
        if (type(v) is not dict or set(v) != {"hypothesis_ids", "not_causal_selection"}
                or v["not_causal_selection"] is not True):
            raise reject_profile()
        ids = v["hypothesis_ids"]
        if ids not in (["H_F"], ["H_H"], ["H_F", "H_H"]):
            raise refusal("CARDINALITY_INVALID", stage="profile_cardinality_edition",
                          target="premise_inventory", retry="correct_input")
    if _available_body(p.target):
        if p.target.value["endpoint_semantics"] != "closed" or p.target.value["unit_role"] != "degree_celsius":
            raise reject_profile()
    if _available_body(p.costs):
        if p.costs.value["cost_token"] != "synthetic_scalar":
            raise reject_profile()
        entries = p.costs.value["entries"]
        if [e["action_id"] for e in entries] != list(ACTION_IDS):
            raise refusal("CARDINALITY_INVALID", stage="profile_cardinality_edition",
                          target="premise_inventory", retry="correct_input")
        if any(e["availability"] == "stale_reference" for e in entries):
            raise refusal("STALE_REFERENCE", stage="profile_cardinality_edition",
                          target="premise_reference", retry="update_complete_world")


def policy_values(request, limits):
    p = request.target_policy
    digits = limits["exact_rational_digits_per_integer"]
    target = None
    if _available_body(p.target):
        bounds = tuple(bounded_fraction(p.target.value[k], digits) for k in ("lower", "upper"))
        if bounds[0] > bounds[1]:
            raise _malformed()
        if p.target.availability == "present":
            target = bounds
    costs = dict.fromkeys(ACTION_IDS)
    if _available_body(p.costs):
        for entry in p.costs.value["entries"]:
            number = None if entry["cost"] is None else bounded_fraction(entry["cost"], digits)
            if number is not None and number < 0:
                raise _malformed()
            if p.costs.availability == entry["availability"] == "present":
                costs[entry["action_id"]] = number
    retained = (p.retained_hypotheses.value["hypothesis_ids"]
                if p.retained_hypotheses.availability == "present" else None)
    return target, costs, retained
