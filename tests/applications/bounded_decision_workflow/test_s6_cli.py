"""Real module-command S6 checks; S7 clean-build release is not asserted."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    PACKAGE_PATH, BASE_REQUEST, BASE_SNAPSHOT, object_bytes,
)
from tests.applications.bounded_decision_workflow.test_s4_fixture_correction import variant
from applications.bounded_decision_workflow.input import canonical_json_bytes
from applications.bounded_decision_workflow import BUILD_LIMITS

ROOT = Path(__file__).parents[3]


def run(*args):
    return subprocess.run([sys.executable, "-m", "applications.bounded_decision_workflow", *map(str, args)],
                          cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                          capture_output=True, timeout=30)


@pytest.fixture
def inputs(tmp_path):
    p = json.loads(PACKAGE_PATH.read_bytes())
    request, snapshot = tmp_path / "request.json", tmp_path / "snapshot.json"
    request.write_bytes(object_bytes(p, BASE_REQUEST))
    snapshot.write_bytes(object_bytes(p, BASE_SNAPSHOT))
    return request, snapshot


def success(process):
    assert process.returncode == 0, process.stderr
    assert process.stderr == b""
    assert len(process.stdout) <= 512 and process.stdout.count(b"\n") == 1
    return json.loads(process.stdout)


def failure(process, code, status):
    assert process.returncode == status, process.stderr
    assert process.stdout == b""
    assert len(process.stderr) <= 512 and process.stderr.count(b"\n") == 1
    value = json.loads(process.stderr)
    assert value["code"] == code
    return value


def test_usage_is_one_bounded_diagnostic():
    failure(run("evaluate"), "CLI_USAGE", 2)


def test_baseline_command_and_exact_replay(tmp_path, inputs):
    request, snapshot = inputs
    dest = tmp_path / "baseline"
    receipt = success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest))
    assert receipt["semantic_disposition"] == "selected_from_supplied_set"
    result = json.loads((dest / "result.json").read_bytes())
    assert result["selection"]["selected_action_ids"] == ["aH"]
    assert result["selection"]["minimum_cost"] == {"numerator": 2, "denominator": 1}
    assert result["observed_value_admission"]["admitted_T0"] == {"numerator": 40, "denominator": 1}
    assert [r["raw_interval"]["lower"]["numerator"] for r in result["raw_projections"]] == [36,32,36,32,42,42,32,32]
    assert len(result["reevaluation"]["decision_rows"]) == 22
    assert success(run("verify", "--bundle", dest))["integrity_state"] == "complete_bundle"
    replay = tmp_path / "replayed"
    success(run("replay", "--bundle", dest, "--output-dir", replay))
    for name in ("result.json", "trace.json"):
        assert (replay / name).read_bytes() == (dest / name).read_bytes()


@pytest.mark.parametrize("name", ["CMD-2-unavailable", "CMD-2-no-feasible", "POL-5-tie", "POL-5-missing-cost", "UNC-1", "UNC-2-missing"])
def test_prepared_semantic_branches_are_command_success(tmp_path, inputs, name):
    package = json.loads(PACKAGE_PATH.read_bytes())
    v = variant(package, name)
    request, snapshot = inputs
    request.write_bytes(object_bytes(package, v["input"]["request_ref"]))
    snapshot.write_bytes(object_bytes(package, v["input"].get("snapshot_ref", BASE_SNAPSHOT)))
    dest = tmp_path / "result"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest))
    expected = json.loads(object_bytes(package, v["expected"]["result_ref"]))
    actual = json.loads((dest / "result.json").read_bytes())
    for section in ("raw_projections", "target_relations", "feasibility", "selection"):
        assert actual[section] == expected[section]


@pytest.mark.parametrize("name,required,changed", [("POL-3", 1, 1), ("POL-4", 13, 7)])
def test_prior_reconstruction_target_cost_and_replay(tmp_path, inputs, name, required, changed):
    request, snapshot = inputs
    baseline = tmp_path / "baseline"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", baseline))
    package = json.loads(PACKAGE_PATH.read_bytes()); v = variant(package, name)
    request.write_bytes(object_bytes(package, v["input"]["request_ref"]))
    dest = tmp_path / "changed"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest, "--compare-to", baseline))
    actual = json.loads((dest / "result.json").read_bytes())
    old = json.loads((baseline / "result.json").read_bytes())
    assert actual["raw_projections"] == old["raw_projections"]
    rows = actual["reevaluation"]["decision_rows"]
    assert sum(r["reevaluation"] == "required" for r in rows) == required
    assert sum(r["value_changed"] for r in rows) == changed
    replay = tmp_path / "replay"
    success(run("replay", "--bundle", dest, "--output-dir", replay))
    assert (replay / "result.json").read_bytes() == (dest / "result.json").read_bytes()


@pytest.mark.parametrize("mutation,code,status", [
    ("stale", "SNAPSHOT_COMMITMENT_MISMATCH", 3),
    ("duplicate", "JSON_DUPLICATE_KEY", 3), ("syntax", "JSON_SYNTAX_INVALID", 3),
    ("oversize", "INPUT_WIRE_LIMIT_EXCEEDED", 4), ("symlink", "PATH_FINAL_SYMLINK", 5),
])
def test_input_failures_and_valid_twin(tmp_path, inputs, mutation, code, status):
    request, snapshot = inputs; good = request.read_bytes()
    if mutation == "stale":
        value = json.loads(good); value["snapshot_commitment"] = "0" * 64; request.write_bytes(canonical_json_bytes(value))
    elif mutation == "duplicate": request.write_bytes(b'{"x":0,"x":1}')
    elif mutation == "syntax": request.write_bytes(b'{')
    elif mutation == "oversize": request.write_bytes(b'x' * 32769)
    else:
        link = tmp_path / "link"; link.symlink_to(request); request = link
    dest = tmp_path / "bad"
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest), code, status)
    assert not dest.exists()  # Optional refusal retention is not promised.
    if mutation == "symlink": request = inputs[0]
    request.write_bytes(good)
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "twin"))


def rehash(bundle, filename):
    path = bundle / "manifest.json"
    manifest = json.loads(path.read_bytes()); data = (bundle / filename).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    manifest["files"][filename] = {"bytes": len(data), "sha256": digest}
    if filename in manifest["semantic_commitments"]: manifest["semantic_commitments"][filename] = digest
    if filename == "build.json": manifest["build_identity"] = digest
    path.write_bytes(canonical_json_bytes(manifest))


@pytest.mark.parametrize("attack", ["result", "source-build", "lock-build", "python-build"])
def test_hash_consistent_replay_attacks_refuse(tmp_path, inputs, attack):
    request, snapshot = inputs; dest = tmp_path / "source"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest))
    name = "result.json" if attack == "result" else "build.json"
    value = json.loads((dest / name).read_bytes())
    if attack == "result": value["selection"]["selected_action_ids"] = ["a0"]
    elif attack == "source-build": value["application_source_sha256"]["applications/bounded_decision_workflow/cli.py"] = "0" * 64
    elif attack == "lock-build": value["dependency_lock_sha256"] = "0" * 64
    else: value["python"]["version"] = "3.14.0"
    (dest / name).write_bytes(canonical_json_bytes(value)); rehash(dest, name)
    success(run("verify", "--bundle", dest))
    code = "REPLAY_SEMANTIC_MISMATCH" if attack == "result" else "REPLAY_BUILD_UNAVAILABLE"
    failure(run("replay", "--bundle", dest, "--output-dir", tmp_path / "replay"), code, 3)
    assert not (tmp_path / "replay").exists()


def test_actual_collision_storage_failure_and_incomplete_verification(tmp_path, inputs):
    request, snapshot = inputs
    dest = tmp_path / "exists"; dest.mkdir(); (dest / "owner").write_bytes(b"preserve")
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest), "OUTPUT_COLLISION", 5)
    assert (dest / "owner").read_bytes() == b"preserve"
    failure(run("verify", "--bundle", dest), "BUNDLE_INCOMPLETE", 3)
    parent = tmp_path / "unwritable"; parent.mkdir(); parent.chmod(0o500)
    try:
        failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", parent / "fail"), "RETENTION_CREATE_FAILED", 6)
    finally: parent.chmod(0o700)


def test_tighter_presentation_limit_refuses_before_publication(tmp_path, inputs):
    request, snapshot = inputs
    value = json.loads(request.read_bytes())
    value["requested_limits"] = dict(BUILD_LIMITS, output_stdout_stderr_bytes=1)
    request.write_bytes(canonical_json_bytes(value))
    dest = tmp_path / "too-small"
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest), "OUTPUT_LIMIT_EXCEEDED", 4)
    assert not dest.exists()


def test_malformed_but_hash_consistent_prior_is_not_internal_error(tmp_path, inputs):
    request, snapshot = inputs; prior = tmp_path / "prior"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", prior))
    value = json.loads((prior / "result.json").read_bytes())
    del value["observed_value_admission"]["admitted_T0"]
    (prior / "result.json").write_bytes(canonical_json_bytes(value)); rehash(prior, "result.json")
    success(run("verify", "--bundle", prior))
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "bad", "--compare-to", prior), "PRIOR_INCOMPATIBLE", 3)
