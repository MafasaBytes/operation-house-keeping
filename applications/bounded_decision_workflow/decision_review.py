"""S4: pure bounded decision review. Captured bytes, no filesystem or CLI.

Prior inputs are not trusted outputs: every retained world is reconstructed and
recomputed. The integrating application supplies its build commitment; deriving
that commitment and verifying on-disk manifests remain S5/S6 responsibilities.
"""
from dataclasses import dataclass
import hashlib
import json
import re

from applications.bounded_decision_workflow.admission import _admit_parsed
from applications.bounded_decision_workflow.errors import WorkflowInputError, refusal
from applications.bounded_decision_workflow.input import (
    canonical_json_bytes, effective_limits, parse_request_wire, parse_snapshot_wire,
    _enforce_effective, _premise_declarations, _snapshot_collection, enforce_snapshot_limits,
)
from applications.bounded_decision_workflow.policy import PolicyReview, _assess_admitted
from applications.bounded_decision_workflow.projection import _prepare_projection, _serialize, _output_refusal
from applications.bounded_decision_workflow.projection_profile import (
    ACTIONS, projection_supports, validate_profile_structure,
)
from applications.bounded_decision_workflow.policy_profile import validate_policy_structure, policy_values


@dataclass(frozen=True, slots=True)
class PriorDecisionInput:
    request_wire: bytes
    snapshot_wire: bytes
    review_wire: bytes
    trace_wire: bytes
    build_identity: str
    prior: "PriorDecisionInput | None" = None


@dataclass(frozen=True, slots=True)
class DecisionReview:
    policy: PolicyReview
    review_bytes: bytes
    trace_bytes: bytes
    resource_counts_bytes: bytes
    # S6 can check retained complete ancestor outputs without recomputing them
    # a second time or hiding that extra work from the approved charge budget.
    prior_reviews: tuple = ()

    @property
    def reevaluation(self):
        return json.loads(self.review_bytes)

    @property
    def trace(self):
        return json.loads(self.trace_bytes)

    @property
    def resource_counts(self):
        return json.loads(self.resource_counts_bytes)


def _prior_refusal(cause=None):
    e = refusal("PRIOR_INCOMPATIBLE", stage="commitment_public_reconstruction",
                target="prior_bundle", retry="use_matching_build")
    return type(e)(e.diagnostic, cause=cause) if cause is not None else e


def _resource(target):
    if target == "resolved_input_bytes":
        return refusal("RESOLVED_INPUT_LIMIT_EXCEEDED", stage="wire_resource",
                       target=target, retry="reduce_input", exit_code=4)
    return refusal("INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
                   target=target, retry="reduce_input", exit_code=4)


def _bounded(value, limit, target):
    if value > limit:
        raise _resource(target)


def _changed_paths(before, proposed, limit):
    """Request leaf/frontier differences; public snapshot is an opaque input.

    This application's snapshot dependency is the whole public serialization,
    not each nested backend record. All its bytes still count and reconstruct.
    """
    paths = []
    pending = [(before, proposed, "")]
    while pending:
        a, b, path = pending.pop()
        if type(a) is type(b) and a == b:
            continue
        if path == "/snapshot":
            paths.append(path)
        elif type(a) is type(b) is dict:
            for k in sorted(set(a) | set(b), reverse=True):
                child = path + "/" + k.replace("~", "~0").replace("/", "~1")
                if k not in a or k not in b:
                    paths.append(child)
                else:
                    pending.append((a[k], b[k], child))
        elif type(a) is type(b) is list and len(a) == len(b):
            pending.extend((a[i], b[i], path + "/" + str(i)) for i in reversed(range(len(a))))
        else:
            paths.append(path)
        _bounded(len(paths), limit, "changed_paths")
    return sorted(paths)


def _support_and_decisions(result):
    admission = result.projection.admission
    r = admission.request.model_dump(mode="json")
    p = r["premises"]
    supports = {"snapshot": admission.snapshot_input.raw,
                "question": r["current_condition_question"],
                "observed:T0": {"snapshot": admission.snapshot_input.sha256,
                                "binding": r["observed_input_binding"]}}
    def register(value):
        if isinstance(value, dict):
            if "premise_id" in value:
                supports["premise:" + value["premise_id"]] = value
            else:
                for child in value.values(): register(child)
    register(p)
    register(r["target_policy"])
    cost = r["target_policy"]["costs"]
    supports["cost_policy"] = {k: v for k, v in cost.items() if k not in ("value", "canonical_commitment")}
    supports["cost_policy"]["cost_token"] = cost["value"]["cost_token"] if cost["value"] is not None else None
    entries = cost["value"]["entries"] if cost["value"] is not None else []
    for a in ACTIONS:
        supports["cost:" + a["action_id"]] = next((e for e in entries if e["action_id"] == a["action_id"]), None)

    dependencies = {"current_condition": ["snapshot", "question"]}
    # Match value remains null when no public match was calculated. The separate
    # admitted disposition/coverage explains unavailability; don't replace null
    # with a newly invented classification value.
    values = {"current_condition": admission.current_condition.computed_match}
    # S2's actual declared support trace supplies complete raw dependencies.
    for raw, trace in zip(result.projection.raw_projections, result.projection.raw_trace["projection_rows"]):
        key = f"raw:{raw['hypothesis_id']}:{raw['action_id']}"
        dependencies[key] = sorted(["observed:T0"] + ["premise:" + v for v in trace["premise_ids"]])
        values[key] = {k: raw[k] for k in ("raw_status", "raw_interval")}
    for row in result.target_relations:
        key = f"target:{row['hypothesis_id']}:{row['action_id']}"
        dependencies[key] = sorted([f"raw:{row['hypothesis_id']}:{row['action_id']}", "premise:P-target"])
        values[key] = row["target_relation"]
    retained = r["target_policy"]["retained_hypotheses"]
    ids = retained["value"]["hypothesis_ids"] if retained["availability"] == "present" else ["H_F", "H_H"]
    for row, action in zip(result.feasibility, ACTIONS):
        a = row["action_id"]
        gate_ids = action["precondition_ids"] + action["timing_ids"] + action["invariance_ids"]
        dependencies["feasibility:" + a] = sorted(
            [f"target:{h}:{a}" for h in ids] + ["premise:" + k for k in gate_ids]
            + ["premise:P-retained", "premise:P-feasibility", "premise:P-applicability"])
        values["feasibility:" + a] = row["feasibility"]
    relevant = [r["action_id"] for r in result.feasibility if r["feasibility"] in ("guaranteed", "unknown")]
    dependencies["selection"] = sorted(["feasibility:" + a["action_id"] for a in ACTIONS]
        + ["premise:P-actions", "premise:P-applicability", "premise:P-selection"]
        + (["cost_policy"] + ["cost:" + a for a in relevant] if relevant else []))
    values["selection"] = result.selection
    return supports, dependencies, values


def _review_rows(current, previous):
    supports, deps, values = current
    old_supports, old_deps, old_values = previous if previous is not None else current
    rows, required = [], set()
    for key in deps:
        inputs = sorted(set(deps[key]) | set(old_deps[key]))
        need = previous is not None and (deps[key] != old_deps[key] or any(
            dep in required if dep in deps else supports[dep] != old_supports[dep] for dep in inputs))
        if need:
            required.add(key)
        changed = values[key] != old_values[key] if previous is not None else None
        # An incomplete dependency map is an internal correctness failure, not a
        # reason to infer dependencies from the very output it missed.
        if changed and not need:
            raise RuntimeError("decision changed without a governing dependency")
        rows.append({"decision_id": key, "depends_on": inputs, "value": values[key],
                     "reevaluation": "not_applicable_no_prior" if previous is None else "required" if need else "not_required",
                     "equal_after_reevaluation": not changed if need else None,
                     "value_changed": changed})
    return rows


def _validator_rows(snapshot):
    """Rows presented at the public admission boundary; nested nodes charge too."""
    return (1 + len(_snapshot_collection(snapshot, "state", "material", "records"))
            + len(_snapshot_collection(snapshot, "conditions"))
            + len(_snapshot_collection(snapshot, "constraint_evaluations"))
            + sum(len(_snapshot_collection(e, "candidates"))
                  for e in _snapshot_collection(snapshot, "constraint_evaluations")))


def _admission_lookup_plan(request, snapshot):
    """Four selection lookups, plus semantic candidate when observation exists.

    Count the admitted S1 path before reconstruction; malformed paths reserve the
    longer path and are still rejected by S1, never admitted by this counter.
    Iteration here does not resolve or authenticate public evidence.
    """
    binding = request.observed_input_binding
    for i, evaluation in enumerate(_snapshot_collection(snapshot, "constraint_evaluations")):
        if i != binding.constraint_evaluation_index:
            continue
        for j, candidate in enumerate(_snapshot_collection(evaluation, "candidates")):
            if j == binding.semantic_candidate_index and isinstance(candidate, dict):
                return 4 if candidate.get("verdict") == "not_evaluated" else 5
    return 5


def review_request_and_snapshot(request_wire: bytes, snapshot_wire: bytes, *,
                                build_identity: str, prior: PriorDecisionInput | None = None) -> DecisionReview:
    """Recompute complete captured worlds; never trust a 'verified' success flag.

build_identity is the integrating application's expected build commitment, not
input JSON authority or executable authentication. S5/S6 must verify the retained
manifest and derive this value from the actual maintained build.
"""
    if type(build_identity) is not str or re.fullmatch(r"[0-9a-f]{64}", build_identity) is None:
        raise _prior_refusal()
    request, request_input = parse_request_wire(request_wire)
    snapshot_input = parse_snapshot_wire(snapshot_wire)
    limits = effective_limits(request)
    _bounded(22, limits["decision_rows"], "decision_rows")
    # Charge a world before retaining another parsed ancestor. Duplicated worlds
    # still cost their full reconstruction; references cannot hide work.
    resolved = refs = charges = lookups = 0
    def charge(q, qi, si):
        nonlocal resolved, refs, charges, lookups
        _enforce_effective(qi.counts, "request", limits)
        enforce_snapshot_limits(si, limits)
        _bounded(_premise_declarations(qi.raw), limits["application_premise_declarations"],
                 "application_premise_declarations")
        resolved += qi.counts.canonical_bytes + si.counts.canonical_bytes
        refs += qi.counts.reference_occurrences + si.counts.reference_occurrences
        indexes = _admission_lookup_plan(q, si.raw)
        lookups += indexes
        charges += (qi.counts.nodes + si.counts.nodes + qi.counts.reference_occurrences
                    + si.counts.reference_occurrences + indexes + _validator_rows(si.raw))
        _bounded(resolved, limits["resolved_input_bytes"], "resolved_input_bytes")
        _bounded(refs, limits["input_reference_occurrences"], "input_reference_occurrences")
        _bounded(charges, limits["input_resolution_charges"], "input_resolution_charges")
    charge(request, request_input, snapshot_input)
    chain, seen, prior_bytes = [], set(), 0
    node = prior
    while node is not None:
        if type(node) is not PriorDecisionInput or id(node) in seen:
            raise _prior_refusal()
        seen.add(id(node))
        if node.build_identity != build_identity:
            raise _prior_refusal()
        for b, cap in ((node.request_wire, "request_wire_bytes"), (node.snapshot_wire, "snapshot_wire_bytes"),
                       (node.review_wire, "output_result_bytes"), (node.trace_wire, "output_trace_bytes")):
            if type(b) is not bytes:
                raise _prior_refusal()
            _bounded(len(b), limits[cap], cap)
            prior_bytes += len(b)
            _bounded(prior_bytes, limits["aggregate_prior_bundle_bytes"], "aggregate_prior_bundle_bytes")
        try:
            q, qi = parse_request_wire(node.request_wire)
            si = parse_snapshot_wire(node.snapshot_wire)
        except WorkflowInputError as e:
            if e.diagnostic.exit_code == 4: raise
            raise _prior_refusal(e) from e
        charge(q, qi, si)
        chain.append((q, qi, si, node))
        node = node.prior
    parsed = list(reversed(chain))
    parsed.append((request, request_input, snapshot_input, None))
    admitted, corner_total = [], 0
    for q, qi, si, node in parsed:
        try:
            a = _admit_parsed(q, qi, si)
            local = {k: min(v, limits[k]) for k, v in effective_limits(q).items()}
            validate_profile_structure(q); validate_policy_structure(q)
            supports = projection_supports(q, local); policy_values(q, local)
            corner_total += _prepare_projection(a, local, supports)[3]
            _bounded(corner_total, limits["corner_evaluations"], "corner_evaluations")
        except WorkflowInputError as e:
            if node is None or e.diagnostic.exit_code == 4: raise
            raise _prior_refusal(e) from e
        admitted.append((a, node, local))
    previous, before_world = None, None
    completed = []
    prefix_resolved = prefix_refs = prefix_charges = prefix_lookups = prefix_corners = prefix_prior_bytes = 0
    for a, node, local in admitted:
        world = {"request": a.request_input.raw, "snapshot": a.snapshot_input.raw}
        paths = [] if before_world is None else _changed_paths(before_world, world, limits["changed_paths"])
        try:
            result = _assess_admitted(a, limits=local)
        except WorkflowInputError as e:
            if node is None or e.diagnostic.exit_code == 4: raise
            raise _prior_refusal(e) from e
        current = _support_and_decisions(result)
        rows = _review_rows(current, previous)
        review = {"disposition": "not_applicable_no_prior" if previous is None else "compared",
                  "decision_rows": rows, "changed_paths": paths}
        trace = {"trace_version": "bdw001.review.v1", "build_identity": build_identity,
                 "request_commitment": a.request_input.sha256, "snapshot_commitment": a.snapshot_input.sha256,
                 "prior_request_commitment": None if before_world is None else hashlib.sha256(canonical_json_bytes(before_world["request"])).hexdigest(),
                 "decision_rows": rows, "projection": result.projection.raw_trace}
        if len(rows) + 8 > min(local["output_trace_rows"], limits["output_trace_rows"]):
            raise _output_refusal()
        combined = dict(json.loads(result.policy_bytes), raw_projections=result.projection.raw_projections, reevaluation=review)
        _serialize(combined, min(local["output_result_bytes"], limits["output_result_bytes"]),
                   min(local["output_result_nodes"], limits["output_result_nodes"]))
        review_wire = _serialize(review, local["output_result_bytes"], local["output_result_nodes"])
        trace_wire = _serialize(trace, min(local["output_trace_bytes"], limits["output_trace_bytes"]))
        if node is not None and (review_wire != node.review_wire or trace_wire != node.trace_wire):
            raise _prior_refusal()
        qi, si = a.request_input, a.snapshot_input
        indexes = _admission_lookup_plan(a.request, si.raw)
        prefix_resolved += len(qi.canonical_bytes) + len(si.canonical_bytes)
        prefix_refs += qi.counts.reference_occurrences + si.counts.reference_occurrences
        prefix_lookups += indexes
        prefix_charges += qi.counts.nodes + si.counts.nodes + qi.counts.reference_occurrences + si.counts.reference_occurrences + indexes + _validator_rows(si.raw)
        prefix_corners += result.projection.corner_evaluations
        prefix_counts = {"worlds_reconstructed": len(completed) + 1, "prior_wire_bytes": prefix_prior_bytes,
            "resolved_input_bytes": prefix_resolved, "input_reference_occurrences": prefix_refs,
            "input_resolution_charges": prefix_charges, "admission_index_lookups": prefix_lookups,
            "corner_evaluations": prefix_corners, "decision_rows": 22, "trace_rows": 30, "changed_paths": len(paths)}
        completed.append(DecisionReview(result, review_wire, trace_wire, canonical_json_bytes(prefix_counts), tuple(completed)))
        prefix_prior_bytes += len(qi.canonical_bytes) + len(si.canonical_bytes) + len(review_wire) + len(trace_wire)
        previous, before_world = current, world
    counts = {"worlds_reconstructed": len(parsed), "prior_wire_bytes": prior_bytes,
              "resolved_input_bytes": resolved, "input_reference_occurrences": refs,
              "input_resolution_charges": charges, "admission_index_lookups": lookups,
              "corner_evaluations": corner_total,
              "decision_rows": 22, "trace_rows": 30, "changed_paths": len(paths)}
    return DecisionReview(result, review_wire, trace_wire, canonical_json_bytes(counts), tuple(completed[:-1]))
