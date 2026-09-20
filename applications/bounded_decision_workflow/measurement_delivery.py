"""Slice 5 measurement bundle publication, verification, and replay binding."""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path


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


def publish_measurement_bundle(output_dir, payloads):
    """Publish exactly seven files, with manifest last and no overwrite."""
    if set(payloads) != set(PAYLOAD_FILES):
        raise MeasurementDeliveryError("PAYLOAD_SET_INVALID", "bundle")
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
    if not path.is_dir():
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
