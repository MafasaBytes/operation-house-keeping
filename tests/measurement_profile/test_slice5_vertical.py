import json
import hashlib
from pathlib import Path

import pytest

from applications.bounded_decision_workflow import build
from applications.bounded_decision_workflow.measurement_delivery import (
    replay_semantic_bundle, evaluate_semantic_bundle,
)
from tests.measurement_profile.test_contracts_and_closure import base_objects


def test_real_vertical_path_evaluates_publishes_and_replays(tmp_path):
    invocation, objects = base_objects()
    actual_wire, actual_id = build.identity()
    build_wire = json.dumps({"schema": "nm.build.v1", "profile": "bdw.measurement.supplied.v1",
                             "id": "B1", "revision": 1, "status": "executable",
                             "actual_build_sha256": actual_id,
                             "actual_build": actual_wire.decode()}, sort_keys=True,
                            separators=(",", ":")).encode()
    build_id = hashlib.sha256(build_wire).hexdigest()
    iv = json.loads(invocation)
    iv["build_identity"] = build_id
    invocation = json.dumps(iv, sort_keys=True, separators=(",", ":")).encode()
    old_build = next(key for key in objects if key[0] == "nm.build.v1")
    objects.pop(old_build)
    objects[("nm.build.v1", build_id)] = build_wire
    public_request = Path("applications/bounded_decision_workflow/examples/request.json").read_bytes()
    public_snapshot = Path("applications/bounded_decision_workflow/examples/snapshot.json").read_bytes()
    q = json.loads(objects[next(key for key in objects if key[0] == "nm.request.v1")])
    h = q["hypotheses"][0]
    p = q["measurements"][0]
    support = [{"id": "S1", "hypothesis": h, "procedure": p,
                "context": q["context"], "decoder": {"kind": "nm.decoder.v1", "sha256": "d" * 64},
                "evidence": {"kind": "nm.evidence.v1", "sha256": "e" * 64},
                "qualification": {"status": "qualified_conditional"},
                "coverage": "complete_envelope", "permits": ["high"],
                "excludes": [], "exclusion_basis": []}]
    candidates = [{"id": "T1", "status": "complete", "branches": [
        {"outcome": "high", "survivors": ["H1"]},
        {"outcome": "low", "survivors": []}]}]
    bundle = evaluate_semantic_bundle(
        tmp_path / "bundle", invocation, objects, public_request, public_snapshot,
        support_rows=support, candidates=candidates)
    replay_semantic_bundle(bundle.path)
    forged = json.loads((bundle.path / "result.json").read_bytes())
    forged["ranking"]["best"] = ["forged"]
    (bundle.path / "result.json").write_bytes(json.dumps(forged, sort_keys=True, separators=(",", ":")).encode())
    with pytest.raises(Exception):
        replay_semantic_bundle(bundle.path)
