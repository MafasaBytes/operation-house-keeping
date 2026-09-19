"""Closed measurement-profile contracts and bounded required-closure resolver.

This is the first measurement slice only.  It does not admit public evidence,
qualify predictions, rank procedures, publish results, or dispatch commands.
"""

from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType

PROFILE = "bdw.measurement.supplied.v1"
APPROVED_POLICY_SHA = "a4a4c8016b35ab78a2b98797234a9a014f46a9bd891e45977477efd3be4ae22c"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")

APPROVED_LIMITS = MappingProxyType({
    "active_depth": 32, "build_bytes": 65536, "bundle_bytes": 1048576,
    "capture_bytes": 1048576, "closure_bytes": 524288,
    "context_scan_bytes": 16777216, "diagnostic_bytes": 2048,
    "edge_visits": 4096, "integer_digits": 128,
    "invocation_bytes": 16384, "json_depth": 40, "json_nodes": 65536,
    "manifest_bytes": 16384, "object_bytes": 262144,
    "public_reconstruction_nodes": 131072, "receipt_bytes": 1024,
    "reference_occurrences": 4096, "request_chain": 4,
    "request_contexts": 8, "result_bytes": 65536,
    "scoped_expansions": 1024, "string_bytes": 4096,
    "trace_bytes": 131072, "unique_objects": 128,
})


class MeasurementContractError(ValueError):
    def __init__(self, code, *, stage="phase_1", target="input", details=None):
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.target = target
        self.details = details or {}


def canonical_json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise MeasurementContractError("DUPLICATE_JSON_KEY", target=key)
        out[key] = value
    return out


def parse_document(wire, *, expected_schema=None, allow_opaque=False):
    if type(wire) is not bytes:
        raise MeasurementContractError("WIRE_TYPE_INVALID")
    try:
        value = json.loads(wire, object_pairs_hook=_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(
                               ValueError(token)))
    except MeasurementContractError:
        raise
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise MeasurementContractError("JSON_INVALID") from error
    if canonical_json_bytes(value) != wire:
        raise MeasurementContractError("CANONICAL_FORM_REQUIRED")
    if not isinstance(value, dict):
        raise MeasurementContractError("SCHEMA_INVALID")
    if allow_opaque:
        return value
    _validate_header(value, expected_schema=expected_schema)
    return value


def _validate_header(value, *, expected_schema=None):
    required = {"schema", "profile", "id", "revision"}
    if not required <= set(value) or not isinstance(value["schema"], str):
        raise MeasurementContractError("SCHEMA_INVALID", stage="phase_1")
    if expected_schema is not None and value["schema"] != expected_schema:
        raise MeasurementContractError("REFERENCE_ROLE_MISMATCH", target="schema")
    if value["profile"] != PROFILE:
        raise MeasurementContractError("PROFILE_MISMATCH", target="profile")
    if type(value["id"]) is not str or not _ID.fullmatch(value["id"]):
        raise MeasurementContractError("IDENTITY_INVALID", target="id")
    if type(value["revision"]) is not int or isinstance(value["revision"], bool) \
            or value["revision"] < 1:
        raise MeasurementContractError("REVISION_INVALID", target="revision")


def _ref(value, *, expected_kind=None):
    if type(value) is not dict or set(value) != {"kind", "sha256"} \
            or type(value["kind"]) is not str or not _SHA.fullmatch(value["sha256"]):
        raise MeasurementContractError("REFERENCE_SHAPE_INVALID", target="reference")
    if expected_kind is not None and value["kind"] != expected_kind:
        raise MeasurementContractError("REFERENCE_ROLE_MISMATCH", target=expected_kind)
    return value["kind"], value["sha256"]


def parse_policy(wire, *, limits=None):
    value = parse_document(wire, expected_schema="nm.resource-policy.v1")
    if value.get("status") not in {"approved", "proposed_not_approved"}:
        raise MeasurementContractError("RESOURCE_POLICY_STATUS_INVALID")
    supplied = value.get("limits")
    if type(supplied) is not dict or not supplied:
        raise MeasurementContractError("RESOURCE_POLICY_INVALID", target="limits")
    effective = dict(APPROVED_LIMITS)
    for name, number in supplied.items():
        if name not in APPROVED_LIMITS or type(number) is not int \
                or isinstance(number, bool) or number < 1:
            raise MeasurementContractError("RESOURCE_POLICY_INVALID", target=name)
        if number > APPROVED_LIMITS[name]:
            raise MeasurementContractError("RESOURCE_POLICY_EXCEEDS_APPROVED", target=name)
        effective[name] = number
    if limits is not None:
        if type(limits) is not dict:
            raise MeasurementContractError("RESOURCE_LIMIT_REQUEST_INVALID")
        for name, number in limits.items():
            if name not in effective or type(number) is not int or isinstance(number, bool) \
                    or number < 1 or number > effective[name]:
                raise MeasurementContractError("RESOURCE_LIMIT_REQUEST_INVALID", target=name)
            effective[name] = number
    return MeasurementPolicy(value["id"], value["revision"],
                             MappingProxyType(effective), value["status"])


def parse_approved_policy(wire, *, limits=None):
    """Validate the exact owner-approved manifest-bound policy bytes."""
    if hashlib.sha256(wire).hexdigest() != APPROVED_POLICY_SHA:
        raise MeasurementContractError("RESOURCE_POLICY_IDENTITY_MISMATCH")
    return parse_policy(wire, limits=limits)


@dataclass(frozen=True)
class MeasurementPolicy:
    id: str
    revision: int
    limits: MappingProxyType
    status: str


@dataclass(frozen=True)
class ClosureResult:
    objects: dict
    order: tuple
    reference_occurrences: int
    edge_visits: int
    active_depth: int
    request_contexts: int
    request_chain: int
    unique_bytes: int


def _typed_edges(value, path=""):
    """Enumerate typed refs, excluding public snapshots and opaque basis content."""
    found = []
    if isinstance(value, dict):
        if set(value) == {"kind", "sha256"}:
            found.append((path, value))
            return found
        for key in sorted(value):
            if key == "snapshot":
                continue
            found.extend(_typed_edges(value[key], f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_typed_edges(item, f"{path}/{index}"))
    return found


def _nomination_checks(value):
    if value.get("schema") != "nm.request.v1":
        return
    for field, kind in (("hypotheses", "nm.hypothesis.v1"),
                        ("measurements", "nm.procedure.v1")):
        entries = value.get(field)
        if not isinstance(entries, list) or not 1 <= len(entries) <= 2:
            raise MeasurementContractError("NOMINATION_CARDINALITY_INVALID", target=field)
        ids = []
        refs = []
        for entry in entries:
            refs.append(_ref(entry, expected_kind=kind))
        if len(set(refs)) != len(refs):
            raise MeasurementContractError("DUPLICATE_NOMINATION_REFERENCE", target=field)
        # IDs are checked after resolution by the caller; retaining the exact
        # refs here ensures a duplicate cannot be repaired by deduplication.
        value.setdefault("_nomination_refs", {})[field] = refs


def _validate_nominations(value, resolve):
    if value.get("schema") != "nm.request.v1":
        return
    for field, kind in (("hypotheses", "nm.hypothesis.v1"),
                        ("measurements", "nm.procedure.v1")):
        entries = value[field]
        ids = []
        for entry in entries:
            key = _ref(entry, expected_kind=kind)
            target = resolve(key, field)
            ids.append(target["id"])
        if ids != sorted(ids):
            raise MeasurementContractError("NOMINATION_ORDER_INVALID", target=field)
        if len(set(ids)) != len(ids):
            raise MeasurementContractError("DUPLICATE_NOMINATION_ID", target=field)


def _special_edges(value):
    schema = value.get("schema")
    if schema == "nm.invocation.v1":
        required = {"request": "nm.request.v1", "selection": "nm.selection.v1"}
        if value.get("adoption") is not None:
            required["adoption"] = "nm.adoption.v1"
        for field, kind in required.items():
            yield "/" + field, _ref(value.get(field), expected_kind=kind)
        yield "/build_identity", ("__build_digest__", value.get("build_identity"))
        yield "/resource_policy", ("nm.resource-policy.v1", value.get("resource_policy"))
    elif schema == "nm.request.v1":
        for field, kind in (("evidence", "nm.evidence.v1"),
                            ("policy", "nm.policy.v1"),
                            ("predecessor", "nm.request.v1")):
            if value.get(field) is not None:
                yield "/" + field, _ref(value[field], expected_kind=kind)
        for field in ("hypotheses", "measurements", "support"):
            for i, entry in enumerate(value.get(field, [])):
                kind = {"hypotheses": "nm.hypothesis.v1", "measurements": "nm.procedure.v1",
                        "support": "nm.support.v1"}[field]
                yield f"/{field}/{i}", _ref(entry, expected_kind=kind)
    elif schema == "nm.declaration.v1":
        for i, entry in enumerate(value.get("requests", [])):
            yield f"/requests/{i}", _ref(entry, expected_kind="nm.request.v1")
    elif schema == "nm.selection.v1":
        yield "/declaration", _ref(value.get("declaration"), expected_kind="nm.declaration.v1")
        yield "/request", _ref(value.get("request"), expected_kind="nm.request.v1")
    elif schema == "nm.adoption.v1":
        for field, kind in (("declaration", "nm.declaration.v1"),
                            ("request", "nm.request.v1"),
                            ("selection", "nm.selection.v1")):
            yield "/" + field, _ref(value.get(field), expected_kind=kind)
    else:
        # Typed refs in H/P/S/E/K and future closed members are still followed;
        # public snapshots and opaque basis bytes were excluded by the walker.
        for path, entry in _typed_edges(value):
            yield path, _ref(entry)


def _join_checks(value, objects):
    """Check exact authority/request joins without later semantic admission."""
    schema = value.get("schema")
    if schema == "nm.selection.v1":
        declaration = value["declaration"]
        request = value["request"]
        payload = objects.get(_ref(declaration, expected_kind="nm.declaration.v1"))
        if payload is not None:
            declared = parse_document(payload, expected_schema="nm.declaration.v1")
            if request not in declared.get("requests", []):
                raise MeasurementContractError("AUTHORITY_REFERENCE_MISMATCH", stage="phase_2", target="selection.request")
    elif schema == "nm.adoption.v1":
        payload = objects.get(_ref(value["selection"], expected_kind="nm.selection.v1"))
        if payload is not None:
            selected = parse_document(payload, expected_schema="nm.selection.v1")
            if value["request"] != selected["request"] or value["declaration"] != selected["declaration"]:
                raise MeasurementContractError("AUTHORITY_REFERENCE_MISMATCH", stage="phase_2", target="adoption")
    elif schema == "nm.invocation.v1":
        payload = objects.get(_ref(value["selection"], expected_kind="nm.selection.v1"))
        if payload is not None:
            selected = parse_document(payload, expected_schema="nm.selection.v1")
            if value["request"] != selected["request"]:
                raise MeasurementContractError("AUTHORITY_REFERENCE_MISMATCH", stage="phase_2", target="invocation.request")
        if value.get("adoption") is not None:
            payload = objects.get(_ref(value["adoption"], expected_kind="nm.adoption.v1"))
            if payload is not None:
                adopted = parse_document(payload, expected_schema="nm.adoption.v1")
                if adopted["request"] != value["request"] or adopted["selection"] != value["selection"]:
                    raise MeasurementContractError("AUTHORITY_REFERENCE_MISMATCH", stage="phase_2", target="invocation.adoption")


def resolve_required_closure(invocation_wire, objects, *, authority_pin=None,
                             policy=None, limits=None):
    if policy is None:
        effective = dict(APPROVED_LIMITS)
        if limits is not None:
            for name, number in limits.items():
                if name not in effective or type(number) is not int or isinstance(number, bool) \
                        or number < 1 or number > effective[name]:
                    raise MeasurementContractError("RESOURCE_LIMIT_REQUEST_INVALID", target=name)
                effective[name] = number
        policy = MeasurementPolicy("approved-inline", 1, MappingProxyType(effective), "approved")
    if not isinstance(objects, dict):
        raise MeasurementContractError("CAPTURE_INVALID")
    root_value = parse_document(invocation_wire, expected_schema="nm.invocation.v1")
    root_ref = (root_value["schema"], hashlib.sha256(invocation_wire).hexdigest())
    objects = dict(objects)
    objects[root_ref] = invocation_wire
    if authority_pin is not None and root_value.get("selection", {}).get("sha256") != authority_pin:
        raise MeasurementContractError("AUTHORITY_PIN_REQUIRED", target="authority_pin")
    active = []
    complete = {}
    identity = {}
    order = []
    refs_count = edges_count = max_depth = contexts = chain = unique_bytes = 0

    def locate(key, path):
        nonlocal refs_count
        refs_count += 1
        if refs_count > policy.limits["reference_occurrences"]:
            raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="reference_occurrences")
        if key[0] == "__build_digest__":
            candidates = [(kind, digest, payload) for (kind, digest), payload in objects.items()
                          if digest == key[1] and kind in {"nm.build.v1", "nm.prepared-build.v1"}]
            if not candidates:
                raise MeasurementContractError("REQUIRED_REFERENCE_MISSING", stage="phase_2", target=path)
            return (candidates[0][0], candidates[0][1]), candidates[0][2]
        if not _SHA.fullmatch(key[1]):
            raise MeasurementContractError("REFERENCE_SHAPE_INVALID", stage="phase_2", target=path)
        payload = objects.get(key)
        if payload is None:
            raise MeasurementContractError("REQUIRED_REFERENCE_MISSING", stage="phase_2", target=path)
        return key, payload

    def walk(key, depth, path):
        nonlocal edges_count, max_depth, contexts, chain, unique_bytes
        if depth > policy.limits["active_depth"]:
            raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="active_depth")
        max_depth = max(max_depth, depth)
        if key in active:
            raise MeasurementContractError("REFERENCE_CYCLE", stage="phase_2", target=path)
        if key in complete:
            return complete[key]
        located, payload = locate(key, path)
        if hashlib.sha256(payload).hexdigest() != located[1]:
            raise MeasurementContractError("REFERENCE_DIGEST_MISMATCH", stage="phase_2", target=path)
        if located[0] == "nm.basis":
            complete[key] = payload
            return payload
        value = parse_document(payload)
        if value["schema"] != located[0]:
            raise MeasurementContractError("REFERENCE_KIND_MISMATCH", stage="phase_2", target=path)
        if value["schema"] == "nm.resource-policy.v1":
            parse_approved_policy(payload)
        ident = (value["schema"], value["id"], value["revision"])
        prior = identity.get(ident)
        if prior is not None and prior != located[1]:
            raise MeasurementContractError("IDENTITY_VERSION_COLLISION", stage="phase_2", target=path)
        identity[ident] = located[1]
        if len(complete) >= policy.limits["unique_objects"]:
            raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="unique_objects")
        if len(payload) > policy.limits["object_bytes"]:
            raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="object_bytes")
        unique_bytes += len(payload)
        if unique_bytes > policy.limits["capture_bytes"]:
            raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="capture_bytes")
        if value["schema"] == "nm.prepared-build.v1" or value.get("status") == "prepared_not_executable":
            raise MeasurementContractError("NONEXECUTABLE_BUILD_WITNESS", stage="phase_2", target=path)
        _nomination_checks(value)
        active.append(key)
        try:
            for edge_path, edge in _special_edges(value):
                edges_count += 1
                if edges_count > policy.limits["edge_visits"]:
                    raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="edge_visits")
                child = walk(edge, depth + 1, edge_path)
                if value["schema"] == "nm.request.v1" and edge_path.startswith("/predecessor"):
                    predecessor = json.loads(child)
                    if predecessor["id"] != value["id"] or predecessor["profile"] != value["profile"] \
                            or predecessor["revision"] != value["revision"] - 1:
                        raise MeasurementContractError("PREDECESSOR_VERSION_MISMATCH", stage="phase_2", target=edge_path)
            if value["schema"] == "nm.request.v1":
                _validate_nominations(value, lambda ref, field: json.loads(walk(ref, depth + 1, field)))
                contexts += 1
                chain = max(chain, value["revision"])
                if contexts > policy.limits["request_contexts"] or chain > policy.limits["request_chain"]:
                    raise MeasurementContractError("RESOURCE_LIMIT_EXCEEDED", stage="phase_2", target="request_chain" if chain > policy.limits["request_chain"] else "request_contexts")
            _join_checks(value, objects)
            complete[key] = payload
            order.append(key)
            return payload
        finally:
            active.pop()

    root_payload = walk(root_ref, 1, "/invocation")
    return ClosureResult(dict(complete), tuple(order), refs_count, edges_count,
                          max_depth, contexts, chain, unique_bytes)
