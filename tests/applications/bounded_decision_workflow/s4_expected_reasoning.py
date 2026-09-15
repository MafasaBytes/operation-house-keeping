"""Independent S4 fixture specification; never imported by application code.

Shares approved semantics, IDs and encoding with runtime, not its dependency
builder or review helpers. Explicit action tables are intentional oracle data.
"""
import json

ACTION_SUPPORT = {
    "a0": ["E-a0", "I-a0"],
    "aF": ["E-aF", "I-aF", "PC-restoration", "PC-permission", "T-aF"],
    "aH": ["E-aH", "I-aH", "PC-isolation", "PC-permission", "T-aH"],
    "aHF": ["E-aH", "E-aF", "I-aH", "I-aF", "PC-isolation", "PC-restoration", "PC-permission", "T-aH", "T-aF"],
}
COMMON = ["P-actions", "P-commands", "P-applicability", "P-hypotheses", "P-law", "P-support",
          "P-A", "P-alpha", "P-beta", "P-gamma"]


def inventory(request, result):
    """Dependencies are admitted support identities, not causal effect sources."""
    d = {"current_condition": ["snapshot", "question"]}
    p = request["target_policy"]
    retained = p["retained_hypotheses"]
    hypotheses = retained["value"]["hypothesis_ids"] if retained["availability"] == "present" else ["H_F", "H_H"]
    for h in ("H_F", "H_H"):
        for a, support in ACTION_SUPPORT.items():
            d[f"raw:{h}:{a}"] = sorted(["observed:T0"] + ["premise:" + k for k in COMMON + support])
    for h in ("H_F", "H_H"):
        for a in ACTION_SUPPORT:
            d[f"target:{h}:{a}"] = sorted([f"raw:{h}:{a}", "premise:P-target"])
    for a, support in ACTION_SUPPORT.items():
        d[f"feasibility:{a}"] = sorted(
            [f"target:{h}:{a}" for h in hypotheses]
            + ["premise:P-retained", "premise:P-feasibility", "premise:P-applicability"]
            + ["premise:" + k for k in support if not k.startswith("E-")])
    relevant = [r["action_id"] for r in result["feasibility"] if r["feasibility"] in ("guaranteed", "unknown")]
    d["selection"] = sorted(["feasibility:" + a for a in ACTION_SUPPORT]
        + ["premise:P-actions", "premise:P-applicability", "premise:P-selection"]
        + (["cost_policy"] + ["cost:" + a for a in relevant] if relevant else []))
    return d


def values(result):
    d = {"current_condition": result["current_condition"]["computed_match"]}
    for r in result["raw_projections"]:
        d[f"raw:{r['hypothesis_id']}:{r['action_id']}"] = {k: r[k] for k in ("raw_status", "raw_interval")}
    for r in result["target_relations"]:
        d[f"target:{r['hypothesis_id']}:{r['action_id']}"] = r["target_relation"]
    for r in result["feasibility"]:
        d["feasibility:" + r["action_id"]] = r["feasibility"]
    d["selection"] = result["selection"]
    return d


def corrected_rows(request, result, *, prior_request=None, prior_result=None, change=None):
    deps = inventory(request, result)
    vals = values(result)
    oldvals = values(prior_result) if prior_result is not None else None
    olddeps = inventory(prior_request, prior_result) if prior_result is not None else deps
    # Only existing frozen comparison recipes: explicit policy-root propagation,
    # independently specified, not inferred by comparing output equality.
    required = ({"selection"} if change == "cost" else
                {k for k in deps if k.startswith(("target:", "feasibility:"))} | {"selection"}
                if change == "target" else set())
    rows = []
    for key in deps:
        need = key in required
        rows.append({"decision_id": key, "depends_on": sorted(set(deps[key]) | set(olddeps[key])),
                     "reevaluation": "not_applicable_no_prior" if oldvals is None else "required" if need else "not_required",
                     "equal_after_reevaluation": vals[key] == oldvals[key] if need else None,
                     "value_changed": vals[key] != oldvals[key] if oldvals is not None else None,
                     "value": vals[key]})
    return rows
