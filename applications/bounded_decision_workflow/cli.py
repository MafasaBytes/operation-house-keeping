"""S6 local command composition; no device access, stores or planning policy."""
import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import sys

from applications.bounded_decision_workflow import (
    BUILD_LIMITS, PriorDecisionInput, WorkflowDiagnostic, WorkflowInputError,
    capture_file, publish_bundle, verify_bundle, review_request_and_snapshot,
)
from applications.bounded_decision_workflow import build, retention
from applications.bounded_decision_workflow.input import canonical_json_bytes, effective_limits, parse_request_wire
from applications.bounded_decision_workflow.preflight import scan
from applications.bounded_decision_workflow.projection import _serialize, _output_refusal
from applications.bounded_decision_workflow.errors import refusal
from applications.bounded_decision_workflow.terminal import emit_failure


def _problem(code):
    specs = {
        "CLI_USAGE": (2, "usage", "invocation", "correct_invocation", "absent"),
        "REPLAY_SEMANTIC_MISMATCH": (3, "commitment_public_reconstruction", "result_or_trace", "investigate_integrity", "absent"),
        "INTERNAL_ERROR": (7, "internal_failure", "application", "investigate", "incomplete_or_absent"),
        "PRIOR_INCOMPATIBLE": (3, "commitment_public_reconstruction", "prior_bundle", "use_matching_build", "optional_refusal"),
    }
    status, stage, target, retry, state = specs[code]
    return WorkflowInputError(WorkflowDiagnostic(code, stage, target, code.lower(), retry, status, state))


class _Parser(argparse.ArgumentParser):
    def error(self, message): raise _problem("CLI_USAGE")


def _arguments(argv):
    parser = _Parser(add_help=False, allow_abbrev=False)
    sub = parser.add_subparsers(dest="operation", required=True, parser_class=_Parser)
    for mode in ("evaluate", "verify", "replay"):
        p = sub.add_parser(mode, add_help=False, allow_abbrev=False)
        if mode == "evaluate":
            for arg in ("request", "snapshot", "output-dir"): p.add_argument("--" + arg, required=True)
            p.add_argument("--compare-to")
        else:
            p.add_argument("--bundle", required=True)
            if mode == "replay": p.add_argument("--output-dir", required=True)
    for mode in ('evaluate','verify','replay'):
        p=sub.add_parser('governed-'+mode,add_help=False,allow_abbrev=False)
        if mode=='evaluate':
            for arg in ('invocation','objects-dir','authority-pin','output-dir'):p.add_argument('--'+arg,required=True)
            p.add_argument('--compare-to')
        else:
            p.add_argument('--bundle',required=True)
            if mode=='replay':p.add_argument('--output-dir',required=True)
    # Repeated flags have no implicit last-writer authority.
    flags = [x for x in argv if x.startswith("--")]
    if len(flags) != len(set(flags)): raise _problem("CLI_USAGE")
    return parser.parse_args(argv)


def _hash(data): return hashlib.sha256(data).hexdigest()


def _json(wire, limits=BUILD_LIMITS):
    scan(wire, limits)
    return json.loads(wire)


def _resolved_bytes(value, limit):
    try:
        return _serialize(value, limit)
    except WorkflowInputError as e:
        raise refusal("RESOLVED_INPUT_LIMIT_EXCEEDED", stage="wire_resource",
                      target="resolved_input_bytes", retry="reduce_input", exit_code=4) from e


def _output(review, build_id):
    policy = review.policy
    a = policy.projection.admission
    obs = a.observed_value
    t0 = None if obs.canonical_decimal is None else Fraction(obs.canonical_decimal)
    result = {
        "current_condition": dict(asdict(a.current_condition), as_of=a.request.current_condition_question.as_of.isoformat(),
                                  declared_state_label=a.request.current_condition_question.declared_state_label,
                                  meaning="classification_at_exact_cutoff_not_projected_state"),
        "observed_value_admission": dict(asdict(obs), disposition=obs.status, source="public_candidate_only",
            admitted_T0=None if t0 is None else {"numerator": t0.numerator, "denominator": t0.denominator}),
        "raw_projections": policy.projection.raw_projections,
        "target_relations": policy.target_relations, "feasibility": policy.feasibility,
        "selection": policy.selection, "reevaluation": review.reevaluation,
        "epistemic_manifest": {"application_premises": "synthetic_assumption", "policy": "application_policy",
            "observed_material": "carried_public_result", "authentication": "not_established",
            "projection": "calculated_conditional_on_assumptions"},
        "commitments_and_limits": {"request_sha256": a.request_input.sha256, "snapshot_sha256": a.snapshot_input.sha256,
            "build_policy_id": "bdw-build-policy.v1", "build_identity": build_id,
            "counts": review.resource_counts, "limits": effective_limits(a.request)},
    }
    trace = {"trace_version": "bdw-trace.v1", "decision_rows": review.reevaluation["decision_rows"],
             "projection_rows": policy.projection.raw_trace["projection_rows"]}
    limits = effective_limits(a.request)
    return (_serialize(result, limits["output_result_bytes"], limits["output_result_nodes"]),
            _serialize(trace, limits["output_trace_bytes"]))


def _node(value, build_id):
    if value is None: return None
    if type(value) is not dict or set(value) != {"request", "snapshot", "review", "trace", "prior", "result_sha256", "trace_sha256"}:
        raise _problem("PRIOR_INCOMPATIBLE")
    return PriorDecisionInput(*(canonical_json_bytes(value[k]) for k in ("request", "snapshot", "review", "trace")),
                              build_id, _node(value["prior"], build_id))


def _retained_node(review, prior, result, trace):
    a = review.policy.projection.admission
    return {"request": a.request_input.raw, "snapshot": a.snapshot_input.raw,
            "review": review.reevaluation, "trace": review.trace, "prior": prior,
            "result_sha256": _hash(result), "trace_sha256": _hash(trace)}


def _checked_bundle(path, build_wire=None, prior_limits=None):
    inspection = (verify_bundle(path) if prior_limits is None else retention._verify_bundle(path,
        total_limit=prior_limits["aggregate_prior_bundle_bytes"], file_limit=prior_limits["prior_bundle_files"]))
    if inspection.diagnostic: raise WorkflowInputError(inspection.diagnostic)
    if build_wire is not None:
        if inspection.bundle_kind != "complete" or inspection.captured["build.json"] != build_wire:
            raise build.unavailable()
    return inspection


def _compute(request_wire, snapshot_wire, prior, build_id):
    scan(request_wire); scan(snapshot_wire)
    review = review_request_and_snapshot(request_wire, snapshot_wire, build_identity=build_id, prior=_node(prior, build_id))
    nodes = []
    current = prior
    while current is not None: nodes.append(current); current = current["prior"]
    for computed, expected in zip(review.prior_reviews, reversed(nodes)):
        result, trace = _output(computed, build_id)
        if _hash(result) != expected["result_sha256"] or _hash(trace) != expected["trace_sha256"]:
            raise _problem("PRIOR_INCOMPATIBLE")
    result, trace = _output(review, build_id)
    return review, result, trace


def _recover(inspection, build_id):
    try:
        return _recover_valid_shape(inspection, build_id)
    except WorkflowInputError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise _problem("REPLAY_SEMANTIC_MISMATCH") from e


def _recover_valid_shape(inspection, build_id):
    files = inspection.captured
    resolved = _json(files["resolved-input.json"])
    if type(resolved) is not dict or set(resolved) != {"request", "snapshot", "prior"}:
        raise _problem("REPLAY_SEMANTIC_MISMATCH")
    if canonical_json_bytes(resolved["request"]) != files["request.json"] or canonical_json_bytes(resolved["snapshot"]) != files["snapshot.json"]:
        raise _problem("REPLAY_SEMANTIC_MISMATCH")
    review, result, trace = _compute(files["request.json"], files["snapshot.json"], resolved["prior"], build_id)
    if result != files["result.json"] or trace != files["trace.json"]:
        raise _problem("REPLAY_SEMANTIC_MISMATCH")
    return review, resolved, result, trace


def execute(args, *, fault=None, observer=None):
    """Trusted in-process fault seam; CLI offers no hooks or policy overrides."""
    if args.operation.startswith('governed-'):
        from . import governed_cli
        return governed_cli.execute(args,fault=fault,observer=observer)
    if args.operation == "verify":
        checked = _checked_bundle(args.bundle)
        return {"operation": "verify", "bundle_commitment": checked.manifest_sha256, "integrity_state": checked.integrity_state}
    # Path preflight precedes interpretation; collision remains at publication.
    absolute, parts = retention._parts(args.output_dir)
    import re
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", parts[-1]) is None: raise retention._error("OUTPUT_BASENAME_INVALID")
    with retention._directory(absolute, parts[:-1]) as fd: retention._filesystem(fd)
    build_wire, build_id = build.identity()
    if args.operation == "replay":
        inspected = _checked_bundle(args.bundle, build_wire)
        review, resolved, result, trace = _recover(inspected, build_id)
        request_wire, snapshot_wire = inspected.captured["request.json"], inspected.captured["snapshot.json"]
    else:
        request_wire = capture_file(args.request, kind="request", fault=fault).data
        snapshot_wire = capture_file(args.snapshot, kind="snapshot", fault=fault).data
        scan(request_wire); scan(snapshot_wire)
        request, _ = parse_request_wire(request_wire)
        limits = effective_limits(request)
        scan(request_wire, limits); scan(snapshot_wire, limits)
        prior = None
        if args.compare_to:
            inspected = _checked_bundle(args.compare_to, prior_limits=limits)
            if inspected.bundle_kind != "complete" or inspected.captured["build.json"] != build_wire:
                raise _problem("PRIOR_INCOMPATIBLE")
            if sum(map(len, inspected.captured.values())) > limits["aggregate_prior_bundle_bytes"]:
                raise retention._error("INPUT_WIRE_LIMIT_EXCEEDED")
            # Do not run the prior separately: S4 recomputes the complete chain once.
            try:
                old = _json(inspected.captured["resolved-input.json"], limits)
                if set(old) != {"request", "snapshot", "prior"}: raise _problem("PRIOR_INCOMPATIBLE")
                if canonical_json_bytes(old["request"]) != inspected.captured["request.json"] or canonical_json_bytes(old["snapshot"]) != inspected.captured["snapshot.json"]:
                    raise _problem("PRIOR_INCOMPATIBLE")
                # Reconstruction is a decoding adapter, not an admitted prior.
                prior = _prior_from_final(inspected, old, build_id)
            except WorkflowInputError:
                raise
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise _problem("PRIOR_INCOMPATIBLE") from e
        resolved = {"request": _json(request_wire), "snapshot": _json(snapshot_wire), "prior": prior}
        resolved_wire = _resolved_bytes(resolved, limits["resolved_input_bytes"])
        scan(resolved_wire, limits)
        review, result, trace = _compute(request_wire, snapshot_wire, prior, build_id)
    limits = effective_limits(review.policy.projection.admission.request)
    payload = {"request.json": request_wire, "snapshot.json": snapshot_wire,
               "resolved-input.json": _resolved_bytes(resolved, limits["resolved_input_bytes"]),
               "result.json": result, "trace.json": trace, "build.json": build_wire}
    # S5 enforces immutable ceilings; optional tighter bundle budget is checked here.
    if sum(map(len, payload.values())) > limits["retention_bundle_bytes"]: raise _output_refusal()
    receipt = {"operation": args.operation, "bundle_commitment": "0" * 64,
               "result_commitment": _hash(result), "semantic_disposition": review.policy.selection["disposition"]}
    if len(canonical_json_bytes(receipt)) + 1 > limits["output_stdout_stderr_bytes"]: raise _output_refusal()
    published = retention._publish_bundle(args.output_dir, payload, operation=args.operation, fault=fault,
                                          bundle_limit=limits["retention_bundle_bytes"])
    receipt["bundle_commitment"] = published.manifest_sha256
    return receipt


def _prior_from_final(inspection, old, build_id):
    result = _json(inspection.captured["result.json"])
    trace = _json(inspection.captured["trace.json"])
    p = old["request"]["premises"]
    coords = {}
    for key in ("A", "alpha", "gamma", "beta"):
        support = p["coordinates"][key]
        bounds = support["value"] if support["availability"] == "present" else None
        coords[key] = [] if bounds is None else [bounds["lower"]] if bounds["lower"] == bounds["upper"] else [bounds["lower"], bounds["upper"]]
    t0 = result["observed_value_admission"]["admitted_T0"]
    coords["T0"] = [] if t0 is None else [t0]
    raw = {"trace_version": "bdw001.raw.v1", "request_commitment": _hash(inspection.captured["request.json"]),
        "snapshot_commitment": _hash(inspection.captured["snapshot.json"]),
        "meaning": "computed_under_supplied_synthetic_assumptions_not_execution",
        "coordinate_order": ["T0", "A", "alpha", "gamma", "beta"], "coordinate_endpoints": coords,
        "corner_evaluations": sum(len(r["corners"]) for r in trace["projection_rows"]), "projection_rows": trace["projection_rows"]}
    internal_trace = {"trace_version": "bdw001.review.v1", "build_identity": build_id,
        "request_commitment": raw["request_commitment"], "snapshot_commitment": raw["snapshot_commitment"],
        "prior_request_commitment": None if old["prior"] is None else _hash(canonical_json_bytes(old["prior"]["request"])),
        "decision_rows": result["reevaluation"]["decision_rows"], "projection": raw}
    return {"request": old["request"], "snapshot": old["snapshot"], "prior": old["prior"],
            "review": result["reevaluation"], "trace": internal_trace,
            "result_sha256": _hash(inspection.captured["result.json"]), "trace_sha256": _hash(inspection.captured["trace.json"])}


def main(argv=None, *, fault=None, observer=None):
    supplied = sys.argv[1:] if argv is None else argv
    if supplied and supplied[0].startswith('measurement-'):
        from .measurement_cli import main as measurement_main
        return measurement_main(supplied)
    try:
        args = _arguments(sys.argv[1:] if argv is None else argv)
        receipt = execute(args, fault=fault,observer=observer)
        wire = canonical_json_bytes(receipt) + b"\n"
        if len(wire) > BUILD_LIMITS["output_stdout_stderr_bytes"]: raise _output_refusal()
        sys.stdout.buffer.write(wire); sys.stdout.buffer.flush()
        return 0
    except WorkflowInputError as e:
        d = e.diagnostic
    except Exception:
        d = _problem("INTERNAL_ERROR").diagnostic
    # Write below BufferedWriter: after EPIPE its pending buffer would otherwise
    # be retried by CPython shutdown, replacing our exit 7 with exit 120.
    stream = sys.stderr.buffer
    return emit_failure(d, getattr(stream, 'raw', stream))
