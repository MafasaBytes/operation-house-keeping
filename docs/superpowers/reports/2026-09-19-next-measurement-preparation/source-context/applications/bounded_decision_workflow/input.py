"""Canonical wire decoding and immutable S1 resource enforcement."""

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Literal
from types import MappingProxyType

from pydantic import ValidationError

from applications.bounded_decision_workflow.contracts import WorkflowRequest
from applications.bounded_decision_workflow.errors import refusal
from applications.bounded_decision_workflow.projection_profile import validate_projection_lexical
from applications.bounded_decision_workflow.policy_profile import validate_policy_lexical


BUILD_LIMITS = MappingProxyType({
    "aggregate_prior_bundle_bytes": 262144,
    "application_premise_declarations": 32,
    "candidates_per_evaluation": 4,
    "changed_paths": 64,
    "conditions_per_snapshot": 8,
    "constraint_evaluations_per_snapshot": 8,
    "corner_evaluations": 128,
    "decision_rows": 22,
    "exact_rational_digits_per_integer": 128,
    "input_json_depth": 32,
    "input_json_nodes_per_file": 8192,
    "input_max_string_bytes": 256,
    "input_reference_occurrences": 2048,
    "input_resolution_charges": 8192,
    "model_records_per_snapshot": 32,
    "output_diagnostic_bytes": 1024,
    "output_result_bytes": 16384,
    "output_result_nodes": 1024,
    "output_stdout_stderr_bytes": 512,
    "output_trace_bytes": 16384,
    "output_trace_rows": 64,
    "prior_bundle_files": 7,
    "request_wire_bytes": 32768,
    "resolved_input_bytes": 262144,
    "retention_bundle_bytes": 393216,
    "snapshot_wire_bytes": 131072,
})

_REFERENCE_FIELDS = {
    "record_ids", "supersedes", "via_assertion_ids",
}


@dataclass(frozen=True, slots=True)
class ResourceCounts:
    wire_bytes: int
    canonical_bytes: int
    nodes: int
    depth: int
    reference_occurrences: int
    max_string_bytes: int


@dataclass(frozen=True, slots=True)
class ParsedInput:
    kind: Literal["request", "snapshot"]
    raw: dict[str, Any]
    canonical_bytes: bytes
    sha256: str
    counts: ResourceCounts


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
        allow_nan=False).encode("utf-8")


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _parse(wire: bytes, kind: Literal["request", "snapshot"]):
    wire_limit = BUILD_LIMITS[f"{kind}_wire_bytes"]
    if len(wire) > wire_limit:
        raise refusal(
            f"{kind.upper()}_WIRE_LIMIT_EXCEEDED", stage="wire_resource",
            target=kind, retry="reduce_input", exit_code=4)
    try:
        text = wire.decode("utf-8")
        value = json.loads(
            text, object_pairs_hook=_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON token {token}")))
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise refusal(
            f"{kind.upper()}_JSON_INVALID", stage="lexical_schema",
            target=kind, retry="correct_input") from error
    if not isinstance(value, dict):
        raise refusal(
            f"{kind.upper()}_SCHEMA_INVALID", stage="lexical_schema",
            target=kind, retry="correct_input")
    canonical = canonical_json_bytes(value)
    if canonical != wire:
        raise refusal(
            f"{kind.upper()}_CANONICAL_FORM_REQUIRED", stage="lexical_schema",
            target=kind, retry="canonicalize_input")
    counts = _count(value, wire_bytes=len(wire), canonical_bytes=len(canonical))
    _enforce_structural_counts(counts, kind)
    return value, canonical, counts


def _count(value: Any, *, wire_bytes: int, canonical_bytes: int) -> ResourceCounts:
    nodes = 0
    max_depth = 0
    references = 0
    max_string = 0
    pending = [(value, 1, None)]
    while pending:
        item, depth, field = pending.pop()
        nodes += 1
        max_depth = max(max_depth, depth)
        if isinstance(item, str):
            max_string = max(max_string, len(item.encode("utf-8")))
        if field is not None and _is_reference_field(field):
            references += _scalar_occurrences(item)
        if isinstance(item, dict):
            for key, child in item.items():
                max_string = max(max_string, len(key.encode("utf-8")))
                pending.append((child, depth + 1, key))
        elif isinstance(item, list):
            child_field = None if field is not None and _is_reference_field(field) else field
            for child in item:
                pending.append((child, depth + 1, child_field))
    return ResourceCounts(
        wire_bytes=wire_bytes, canonical_bytes=canonical_bytes, nodes=nodes,
        depth=max_depth, reference_occurrences=references,
        max_string_bytes=max_string)


def _is_reference_field(name: str) -> bool:
    return (name.endswith("_id") or name.endswith("_ids")
            or name.endswith("_reference") or name.endswith("_commitment")
            or name in _REFERENCE_FIELDS)


def _scalar_occurrences(value: Any) -> int:
    if isinstance(value, list):
        return sum(_scalar_occurrences(item) for item in value)
    return 0 if isinstance(value, (dict, list)) else 1


def _enforce_structural_counts(counts: ResourceCounts, kind: str):
    checks = (
        (counts.nodes, "input_json_nodes_per_file"),
        (counts.depth, "input_json_depth"),
        (counts.reference_occurrences, "input_reference_occurrences"),
        (counts.max_string_bytes, "input_max_string_bytes"),
    )
    for actual, dimension in checks:
        if actual > BUILD_LIMITS[dimension]:
            raise refusal(
                "INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
                target=dimension, retry="reduce_input", exit_code=4)


def _reject_known_unsupported_profile_fields(value: dict[str, Any]):
    binding = value.get("observed_input_binding")
    if isinstance(binding, dict) and "conversion" in binding:
        raise refusal(
            "PROFILE_UNSUPPORTED", stage="profile_cardinality_edition",
            target="workflow_profile", retry="use_supported_profile")


def _validate_requested_limits(request: WorkflowRequest):
    if request.requested_limits is None:
        return
    requested = request.requested_limits.model_dump()
    for name, value in requested.items():
        if value > BUILD_LIMITS[name]:
            raise refusal(
                "REQUESTED_LIMIT_RELAXATION", stage="profile_cardinality_edition",
                target=name, retry="use_build_limits")


def effective_limits(request: WorkflowRequest) -> dict[str, int]:
    if request.requested_limits is None:
        return dict(BUILD_LIMITS)
    return request.requested_limits.model_dump()


def enforce_request_limits(
        request: WorkflowRequest, parsed: ParsedInput) -> dict[str, int]:
    limits = effective_limits(request)
    _enforce_effective(parsed.counts, "request", limits)
    declarations = _premise_declarations(parsed.raw)
    if declarations > limits["application_premise_declarations"]:
        raise refusal(
            "INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
            target="application_premise_declarations", retry="reduce_input",
            exit_code=4)
    return limits


def enforce_snapshot_limits(parsed: ParsedInput, limits: dict[str, int]):
    _enforce_effective(parsed.counts, "snapshot", limits)
    snapshot = parsed.raw
    cardinalities = (
        (len(_snapshot_collection(snapshot, "conditions")), "conditions_per_snapshot"),
        (len(_snapshot_collection(snapshot, "constraint_evaluations")),
         "constraint_evaluations_per_snapshot"),
        (len(_snapshot_collection(snapshot, "state", "material", "records")),
         "model_records_per_snapshot"),
    )
    for evaluation in _snapshot_collection(snapshot, "constraint_evaluations"):
        cardinalities += ((len(_snapshot_collection(evaluation, "candidates")),
                           "candidates_per_evaluation"),)
    for actual, dimension in cardinalities:
        if actual > limits[dimension]:
            raise refusal(
                "INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
                target=dimension, retry="reduce_input", exit_code=4)


def _snapshot_collection(value, *path):
    """Count actual rows without repairing material before public validation.

    Malformed shapes remain untouched in parsed.raw. Their nodes have already
    been charged by the generic JSON counter; only public reconstruction admits.
    """
    for key in path:
        if not isinstance(value, dict):
            return ()
        value = value.get(key)
    return value if isinstance(value, list) else ()


def _enforce_effective(
        counts: ResourceCounts, kind: str, limits: dict[str, int]):
    checks = (
        (counts.wire_bytes, f"{kind}_wire_bytes"),
        (counts.nodes, "input_json_nodes_per_file"),
        (counts.depth, "input_json_depth"),
        (counts.reference_occurrences, "input_reference_occurrences"),
        (counts.max_string_bytes, "input_max_string_bytes"),
    )
    for actual, dimension in checks:
        if actual > limits[dimension]:
            raise refusal(
                "INPUT_RESOURCE_LIMIT_EXCEEDED", stage="wire_resource",
                target=dimension, retry="reduce_input", exit_code=4)


def _premise_declarations(value: Any) -> int:
    count = 0
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if "premise_id" in item and "canonical_commitment" in item:
                count += 1
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return count


def parse_request_wire(wire: bytes) -> tuple[WorkflowRequest, ParsedInput]:
    value, canonical, counts = _parse(wire, "request")
    _reject_known_unsupported_profile_fields(value)
    try:
        request = WorkflowRequest.model_validate(value)
    except ValidationError as error:
        raise refusal(
            "REQUEST_SCHEMA_INVALID", stage="lexical_schema",
            target="request", retry="correct_input") from error
    validate_projection_lexical(request)
    validate_policy_lexical(request)
    _validate_requested_limits(request)
    parsed = ParsedInput(
        kind="request", raw=value, canonical_bytes=canonical,
        sha256=hashlib.sha256(canonical).hexdigest(), counts=counts)
    enforce_request_limits(request, parsed)
    return request, parsed


def parse_snapshot_wire(wire: bytes) -> ParsedInput:
    value, canonical, counts = _parse(wire, "snapshot")
    return ParsedInput(
        kind="snapshot", raw=value, canonical_bytes=canonical,
        sha256=hashlib.sha256(canonical).hexdigest(), counts=counts)
