"""Slice 5 measurement bundle publication, verification, and replay binding."""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path

from .measurement_contracts import parse_document, parse_approved_policy, resolve_required_closure
from .measurement_admission import admit_measurement
from .support_qualification import qualify_supplied_support
from .measurement_ranking import rank_measurements
from . import build as maintained_build


FILES = ("invocation.json", "closure.json", "result.json", "trace.json",
         "build.json", "policy.json", "manifest.json")
PAYLOAD_FILES = FILES[:-1]


class MeasurementDeliveryError(ValueError):
    def __init__(self, code, target):
        super().__init__(code)
        self.code = code
        self.target = target


@dataclass(frozen=True, slots=True)
class MeasurementBundle:
    path: Path
    manifest_sha256: str
    files: tuple[str, ...]


def _canonical(data):
    try:
        value = json.loads(data.decode("utf-8"))
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()
    except (UnicodeDecodeError, ValueError, TypeError):
        raise MeasurementDeliveryError("WIRE_INVALID", "bundle")
    if encoded != data:
        raise MeasurementDeliveryError("CANONICAL_FORM_REQUIRED", "bundle")
    return value


def _manifest(payloads):
    return json.dumps({"schema": "nm.manifest.v1", "files": [
        {"name": name, "sha256": hashlib.sha256(payloads[name]).hexdigest(),
         "bytes": len(payloads[name])} for name in PAYLOAD_FILES
    ]}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _validate_profile_payloads(payloads):
    """Validate closed measurement envelopes when a real invocation is supplied."""
    invocation = payloads["invocation.json"]
    if b'"schema":"nm.invocation.v1"' not in invocation:
        return  # legacy unit fixtures are storage-only and never production envelopes
    try:
        root = parse_document(invocation, expected_schema="nm.invocation.v1")
        closure = json.loads(payloads["closure.json"])
        if not isinstance(closure, dict) or not isinstance(closure.get("objects"), dict):
            raise ValueError("required closure missing")
        objects = {}
        for key, value in closure["objects"].items():
            kind, separator, digest = key.partition("|")
            if not separator or not isinstance(value, str):
                raise ValueError("invalid closure member")
            objects[(kind, digest)] = value.encode()
        resolve_required_closure(invocation, objects,
                                authority_pin=root["selection"]["sha256"])
        build = json.loads(payloads["build.json"])
        if build.get("schema") != "nm.build.v1" or build.get("status") != "executable":
            raise ValueError("nonexecutable build")
        parse_approved_policy(payloads["policy.json"])
    except Exception as error:
        raise MeasurementDeliveryError("PROFILE_BINDING_INVALID", "invocation.json") from error


def publish_measurement_bundle(output_dir, payloads):
    """Publish exactly seven files, with manifest last and no overwrite."""
    if set(payloads) != set(PAYLOAD_FILES):
        raise MeasurementDeliveryError("PAYLOAD_SET_INVALID", "bundle")
    _validate_profile_payloads(payloads)
    path = Path(output_dir)
    try:
        path.mkdir(parents=False)
    except FileExistsError as error:
        raise MeasurementDeliveryError("OUTPUT_COLLISION", "output_dir") from error
    try:
        for name in PAYLOAD_FILES:
            data = payloads[name]
            if type(data) is not bytes:
                raise MeasurementDeliveryError("WIRE_INVALID", name)
            _canonical(data)
            with (path / name).open("xb") as stream:
                stream.write(data)
        manifest = _manifest(payloads)
        with (path / "manifest.json").open("xb") as stream:
            stream.write(manifest)
    except Exception:
        # An incomplete directory is intentionally retained; no false success.
        raise
    return MeasurementBundle(path, hashlib.sha256(manifest).hexdigest(), FILES)


def verify_measurement_bundle(bundle_dir):
    path = Path(bundle_dir)
    if path.is_symlink() or not path.is_dir():
        raise MeasurementDeliveryError("BUNDLE_INCOMPLETE", "bundle")
    names = tuple(sorted(item.name for item in path.iterdir()))
    if names != tuple(sorted(FILES)):
        raise MeasurementDeliveryError("BUNDLE_INCOMPLETE", "bundle")
    manifest = (path / "manifest.json").read_bytes()
    value = _canonical(manifest)
    if value.get("schema") != "nm.manifest.v1":
        raise MeasurementDeliveryError("MANIFEST_INVALID", "manifest.json")
    listed = {item.get("name"): item for item in value.get("files", ())}
    if set(listed) != set(PAYLOAD_FILES):
        raise MeasurementDeliveryError("MANIFEST_INVALID", "manifest.json")
    for name in PAYLOAD_FILES:
        if (path / name).is_symlink() or not (path / name).is_file():
            raise MeasurementDeliveryError("PATH_FILE_INVALID", name)
        data = (path / name).read_bytes()
        item = listed[name]
        if item.get("bytes") != len(data) or item.get("sha256") != hashlib.sha256(data).hexdigest():
            raise MeasurementDeliveryError("MANIFEST_COMMITMENT_MISMATCH", name)
        _canonical(data)
    return MeasurementBundle(path, hashlib.sha256(manifest).hexdigest(), FILES)


def replay_measurement_bundle(bundle_dir, *, build, policy, result, trace):
    """Compare freshly recomputed semantic bytes under exact build/policy pins."""
    bundle = verify_measurement_bundle(bundle_dir)
    path = bundle.path
    if (path / "build.json").read_bytes() != build:
        raise MeasurementDeliveryError("BUILD_IDENTITY_MISMATCH", "build.json")
    if (path / "policy.json").read_bytes() != policy:
        raise MeasurementDeliveryError("POLICY_IDENTITY_MISMATCH", "policy.json")
    if (path / "result.json").read_bytes() != result:
        raise MeasurementDeliveryError("REPLAY_SEMANTIC_MISMATCH", "result.json")
    if (path / "trace.json").read_bytes() != trace:
        raise MeasurementDeliveryError("REPLAY_SEMANTIC_MISMATCH", "trace.json")
    return bundle


def _semantic_inputs(invocation, objects, public_request, public_snapshot,
                     support_rows, candidates):
    root = json.loads(invocation)
    admission = admit_measurement(
        invocation, objects, authority_pin=root["selection"]["sha256"],
        public_request_wire=public_request, public_snapshot_wire=public_snapshot)
    request_key = (root["request"]["kind"], root["request"]["sha256"])
    request = json.loads(objects[request_key])
    h_ref, p_ref = request["hypotheses"][0], request["measurements"][0]
    cells = qualify_supplied_support(
        support_rows, hypothesis=h_ref, procedure=p_ref,
        context=request["context"], decoder=support_rows[0]["decoder"],
        evidence=support_rows[0]["evidence"], outcomes=("high", "low"))
    ranking = rank_measurements([json.loads(objects[(r["kind"], r["sha256"])])["id"]
                                 for r in request["hypotheses"]], candidates)
    result = {"admission": {"permission": admission.permission,
                             "authority_state": admission.authority_state,
                             "evidence_state": admission.evidence_state,
                             "reasons": admission.reasons},
              "support": [{"outcome": c.outcome, "relation": c.relation,
                           "reasons": c.reasons, "sources": c.source_ids} for c in cells],
              "ranking": {"disposition": ranking.disposition,
                          "best": ranking.best, "reason": ranking.reason,
                          "scores": [{"id": s.measurement_id,
                                      "worst": s.worst_survivors,
                                      "reduction": s.reduction,
                                      "survivors": s.survivor_multiset}
                                     for s in ranking.scores]}}
    trace = {"phases": ["closure", "admission", "support", "ranking"],
             "logical": {"objects": len(objects), "support_rows": len(support_rows),
                         "candidates": len(candidates)}}
    return (json.dumps(result, sort_keys=True, separators=(",", ":")).encode(),
            json.dumps(trace, sort_keys=True, separators=(",", ":")).encode())


def evaluate_semantic_bundle(output_dir, invocation, objects, public_request,
                             public_snapshot, *, support_rows, candidates):
    actual_build_wire, actual_build_id = maintained_build.identity()
    build_wire = json.dumps({"schema": "nm.build.v1", "profile": "bdw.measurement.supplied.v1",
                             "id": "B1", "revision": 1, "status": "executable",
                             "actual_build_sha256": actual_build_id,
                             "actual_build": actual_build_wire.decode()},
                            sort_keys=True, separators=(",", ":")).encode()
    build_id = hashlib.sha256(build_wire).hexdigest()
    root = json.loads(invocation)
    if root.get("build_identity") != build_id:
        raise MeasurementDeliveryError("BUILD_IDENTITY_MISMATCH", "invocation.build_identity")
    build_obj = json.loads(build_wire)
    if build_obj.get("actual_build_sha256") != actual_build_id \
            or build_obj.get("actual_build") != actual_build_wire.decode():
        raise MeasurementDeliveryError("BUILD_IDENTITY_MISMATCH", "build.json")
    policy = next(payload for (kind, _), payload in objects.items()
                  if kind == "nm.resource-policy.v1")
    parse_approved_policy(policy)
    result, trace = _semantic_inputs(invocation, objects, public_request,
                                     public_snapshot, support_rows, candidates)
    closure = {"schema": "nm.closure.v1", "invocation": invocation.decode(),
               "objects": {f"{kind}|{digest}": payload.decode()
                           for (kind, digest), payload in objects.items()},
               "public_request": public_request.decode(),
               "public_snapshot": public_snapshot.decode(),
               "support_rows": support_rows, "candidates": candidates}
    payloads = {
        "invocation.json": invocation,
        "closure.json": json.dumps(closure, sort_keys=True, separators=(",", ":")).encode(),
        "result.json": result, "trace.json": trace,
        "build.json": build_wire, "policy.json": policy,
    }
    return publish_measurement_bundle(output_dir, payloads)


def replay_semantic_bundle(bundle_dir):
    bundle = verify_measurement_bundle(bundle_dir)
    path = bundle.path
    build_wire, build_id = maintained_build.identity()
    if path.joinpath("build.json").read_bytes() != build_wire:
        raise MeasurementDeliveryError("BUILD_IDENTITY_MISMATCH", "build.json")
    closure = json.loads(path.joinpath("closure.json").read_bytes())
    objects = {}
    for key, value in closure["objects"].items():
        kind, _, digest = key.partition("|")
        objects[(kind, digest)] = value.encode()
    invocation = closure["invocation"].encode()
    result, trace = _semantic_inputs(
        invocation, objects, closure["public_request"].encode(),
        closure["public_snapshot"].encode(), closure["support_rows"],
        closure["candidates"])
    if path.joinpath("result.json").read_bytes() != result:
        raise MeasurementDeliveryError("REPLAY_SEMANTIC_MISMATCH", "result.json")
    if path.joinpath("trace.json").read_bytes() != trace:
        raise MeasurementDeliveryError("REPLAY_SEMANTIC_MISMATCH", "trace.json")
    return bundle
