"""Release-one application premises, not backend declarations or an expression DSL.

Literal forms implement corrected design section 6 and the approved wire examples.
Values are checked by structure and type, never by fixture identity or commitment.
"""

from fractions import Fraction
from math import gcd

from applications.bounded_decision_workflow.errors import refusal


LAW = {
    "equation": "T1=T0+alpha*h-gamma*f-beta*(T0-A)",
    "evaluation": "all_distinct_cartesian_endpoint_corners",
    "law_id": "thermal-affine.v1",
    "operations": ["addition", "subtraction", "multiplication"], "steps": 1,
}
SUPPORT = {
    "basis": "cartesian_hard_support.v1", "confidence_interpretation": False,
    "endpoints": "closed", "shared_named_coordinates": True,
}
HYPOTHESES = [
    {"hypothesis_id": "H_F", "mapping": {"f": 0, "h": "u_h"},
     "meaning": "fan_failed_off", "not_causally_exhaustive": True},
    {"hypothesis_id": "H_H", "mapping": {"f": "u_f", "h": 1},
     "meaning": "heater_stuck_on", "not_causally_exhaustive": True},
]
ACTIONS = [
    {"action_id": "a0", "effect_ids": ["E-a0"], "invariance_ids": ["I-a0"],
     "precondition_ids": [], "timing_ids": []},
    {"action_id": "aF", "effect_ids": ["E-aF"], "invariance_ids": ["I-aF"],
     "precondition_ids": ["PC-restoration", "PC-permission"], "timing_ids": ["T-aF"]},
    {"action_id": "aH", "effect_ids": ["E-aH"], "invariance_ids": ["I-aH"],
     "precondition_ids": ["PC-isolation", "PC-permission"], "timing_ids": ["T-aH"]},
    {"action_id": "aHF", "effect_ids": ["E-aH", "E-aF"],
     "invariance_ids": ["I-aH", "I-aF"],
     "precondition_ids": ["PC-isolation", "PC-restoration", "PC-permission"],
     "timing_ids": ["T-aH", "T-aF"]},
]
UNITS = {"A": "degree_celsius", "alpha": "degree_celsius_per_step",
         "gamma": "degree_celsius_per_step", "beta": "per_step"}


def reject_profile():
    return refusal("PROFILE_UNSUPPORTED", stage="profile_cardinality_edition",
                   target="workflow_profile", retry="use_supported_profile")


def _schema():
    return refusal("REQUEST_SCHEMA_INVALID", stage="lexical_schema",
                   target="request", retry="correct_input")


def _malformed():
    return refusal("SUPPORT_MALFORMED", stage="profile_cardinality_edition",
                   target="coordinate_support", retry="correct_input")


def numeric_limit():
    return refusal("NUMERIC_LIMIT_EXCEEDED", stage="semantic_calculation",
                   target="rational", retry="reduce_numeric_size", exit_code=4)


def _rational_shape(value):
    if (type(value) is not dict or set(value) != {"numerator", "denominator"}
            or any(type(v) is not int for v in value.values())):
        raise _schema()


def validate_projection_lexical(request):
    """Check numeric JSON shapes before public reconstruction, not numeric meaning."""
    for premise in request.premises.coordinates.values():
        value = premise.value
        if value is None and premise.availability != "present":
            continue
        if type(value) is not dict or set(value) != {
                "lower", "upper", "endpoint_semantics", "unit_role"}:
            raise _schema()
        _rational_shape(value["lower"])
        _rational_shape(value["upper"])


def bounded_fraction(value, digits):
    """Bound operands before gcd/arithmetic; booleans are not integers."""
    _rational_shape(value)
    n, d = value["numerator"], value["denominator"]
    if any(abs(v) >= 10 ** digits for v in (n, d)):
        raise numeric_limit()
    if d <= 0 or gcd(n, d) != 1:
        raise _malformed()
    return Fraction(n, d)


def check_number(number, digits):
    if (abs(number.numerator) >= 10 ** digits
            or number.denominator >= 10 ** digits):
        raise numeric_limit()
    return number


def _same(actual, expected):
    # Python equality alone would accept True as 1, or 1.0 as 1.
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            _same(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _same(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _body(premise, expected, *, gate=False):
    if premise.value is None and premise.availability != "present":
        return
    if gate:
        if type(premise.value) is not dict or type(premise.value.get("status")) is not bool:
            raise reject_profile()
        expected = dict(expected, status=premise.value["status"])
    if not _same(premise.value, expected):
        raise reject_profile()


def validate_profile(request, limits):
    """Validate S2 premises only. Policy semantics belong to S3.

    Exact application edition 1 is implicit in this fixed profile. Unknown bodies
    may be null, or carried in their valid shape; they are never used as support.
    """
    p = request.premises
    inventory = [(p.actions, "P-actions"), (p.commands, "P-commands"),
                 (p.global_applicability, "P-applicability"),
                 (p.hypotheses, "P-hypotheses"), (p.law, "P-law"),
                 (p.support_semantics, "P-support")]
    inventory += [(v, "P-" + k) for k, v in sorted(p.coordinates.items())]
    for group in (p.effects, p.invariances, p.preconditions, p.timing):
        inventory += [(v, k) for k, v in sorted(group.items())]
    for premise, expected_id in inventory:
        if premise.premise_id != expected_id or premise.epistemic_kind != "synthetic_assumption":
            raise reject_profile()
        if premise.edition != 1:
            raise refusal("EDITION_MISMATCH", stage="profile_cardinality_edition",
                          target="premise_edition", retry="update_complete_world")
        if premise.availability == "stale_reference":
            raise refusal("STALE_REFERENCE", stage="profile_cardinality_edition",
                          target="premise_reference", retry="update_complete_world")

    for premise, field, ids in ((p.actions, "action_id", ["a0", "aF", "aH", "aHF"]),
                                (p.hypotheses, "hypothesis_id", ["H_F", "H_H"])):
        if premise.value is None and premise.availability != "present":
            continue
        if (type(premise.value) is not list
                or any(type(v) is not dict for v in premise.value)
                or [v.get(field) for v in premise.value] != ids):
            raise refusal("CARDINALITY_INVALID", stage="profile_cardinality_edition",
                          target="premise_inventory", retry="correct_input")
    _body(p.actions, ACTIONS)
    _body(p.hypotheses, HYPOTHESES)
    _body(p.law, LAW)
    _body(p.support_semantics, SUPPORT)
    if p.commands.value is not None or p.commands.availability == "present":
        v = p.commands.value
        if (type(v) is not dict or set(v) != {"meaning", "u_h", "u_f"}
                or v["meaning"] != "assumed_command_state_not_execution"
                or any(type(v[k]) is not int or v[k] not in (0, 1) for k in ("u_h", "u_f"))):
            raise reject_profile()
    _body(p.global_applicability,
          {"configuration": "hypothetical_enclosure", "law_edition": 1,
           "one_step": True, "status": True}, gate=True)
    for key, assignments in (("E-a0", {}), ("E-aF", {"f": 1}), ("E-aH", {"h": 0})):
        _body(p.effects[key], {"assignments": assignments,
              "kind": "assignment" if assignments else "identity", "timing": "before_step"})
    for key, unchanged in (
        ("I-a0", ["T0", "A", "alpha", "beta", "gamma", "h", "f", "law_form"]),
        ("I-aF", ["T0", "A", "alpha", "beta", "gamma", "h", "law_form"]),
        ("I-aH", ["T0", "A", "beta", "gamma", "f", "law_form"]),
    ):
        _body(p.invariances[key], {"status": True, "unchanged": unchanged}, gate=True)
    for key, premise in p.preconditions.items():
        expected = {"status": True}
        if key == "PC-permission":
            expected["meaning"] = "synthetic_permission_only"
        _body(premise, expected, gate=True)
    for premise in p.timing.values():
        _body(premise, {"status": True, "when": "before_step"}, gate=True)

    supports = {}
    for key, premise in sorted(p.coordinates.items()):
        if premise.value is None:
            supports[key] = None
            continue
        value = premise.value
        if value["endpoint_semantics"] != "closed" or value["unit_role"] != UNITS[key]:
            raise reject_profile()
        lo, hi = (bounded_fraction(value[k], limits["exact_rational_digits_per_integer"])
                  for k in ("lower", "upper"))
        if lo > hi:
            raise _malformed()
        supports[key] = (lo, hi) if premise.availability == "present" else None
    return supports
