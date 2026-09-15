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
from tests.applications.bounded_decision_workflow.test_s2_raw_projection import recommit

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


@pytest.mark.parametrize("name", ["OBS-3-decimal-reconstruction", "OBS-3-decimal-stale-commitment", "OBS-3-wrong-context", "NUM-1-oversized"])
def test_command_retains_accepted_admission_precedence(tmp_path, inputs, name):
    package = json.loads(PACKAGE_PATH.read_bytes()); v = variant(package, name)
    request, snapshot = inputs
    request.write_bytes(object_bytes(package, v["input"]["request_ref"]))
    snapshot.write_bytes(object_bytes(package, v["input"].get("snapshot_ref", BASE_SNAPSHOT)))
    if name == "OBS-3-wrong-context":
        value = json.loads(request.read_bytes())
        value["current_condition_question"]["assertion_context"]["view"] = "as_designed"
        request.write_bytes(canonical_json_bytes(value))
    if name == "NUM-1-oversized":
        value = json.loads(request.read_bytes())
        support = value["premises"]["coordinates"]["alpha"]["value"]
        for endpoint in ("lower", "upper"):
            support[endpoint] = {"numerator": 10 ** 128, "denominator": 1}
        request.write_bytes(recommit(value))
    d = v["expected"]["stderr_line"]
    actual = failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "bad"), d["code"], d["exit_code"])
    assert actual == d


@pytest.mark.parametrize("dimension,value,code", [
    ("corner_evaluations", 7, "INPUT_RESOURCE_LIMIT_EXCEEDED"),
    ("decision_rows", 21, "INPUT_RESOURCE_LIMIT_EXCEEDED"),
    ("output_trace_rows", 29, "OUTPUT_LIMIT_EXCEEDED"),
    ("output_result_bytes", 1024, "OUTPUT_LIMIT_EXCEEDED"),
    ("output_trace_bytes", 1024, "OUTPUT_LIMIT_EXCEEDED"),
    ("retention_bundle_bytes", 1024, "OUTPUT_LIMIT_EXCEEDED"),
    ("resolved_input_bytes", 100000, "RESOLVED_INPUT_LIMIT_EXCEEDED"),
])
def test_command_incremental_limits_and_no_partial_result(tmp_path, inputs, dimension, value, code):
    request, snapshot = inputs
    data = json.loads(request.read_bytes()); data["requested_limits"] = dict(BUILD_LIMITS, **{dimension: value})
    request.write_bytes(canonical_json_bytes(data))
    dest = tmp_path / "limited"
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", dest), code, 4)
    assert not dest.exists()


def test_equal_tighter_and_relaxed_requested_limits(tmp_path, inputs):
    request, snapshot = inputs; data = json.loads(request.read_bytes())
    for label, limits in [("equal", dict(BUILD_LIMITS)), ("tighter", dict(BUILD_LIMITS, corner_evaluations=8, output_trace_rows=30))]:
        data["requested_limits"] = limits; request.write_bytes(canonical_json_bytes(data))
        success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / label))
    data["requested_limits"]["corner_evaluations"] = 129
    request.write_bytes(canonical_json_bytes(data))
    # Accepted S1 service diagnostic, not the stale preparation alias.
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "relaxed"), "REQUESTED_LIMIT_RELAXATION", 3)


@pytest.mark.parametrize("stage,code,status", [("internal", "INTERNAL_ERROR", 7),
    ("directory_fsync", "RETENTION_DIR_FSYNC_FAILED", 6), ("parent_fsync", "RETENTION_PARENT_FSYNC_FAILED", 6)])
def test_real_entrypoint_with_trusted_fault_bootstrap(tmp_path, inputs, stage, code, status):
    request, snapshot = inputs; output = tmp_path / "fault"
    # No production CLI flag or environment hook. Test-only bootstrap runs the
    # real module entry point in a fresh process with a trusted callable seam.
    bootstrap = '''import runpy,sys
from applications.bounded_decision_workflow import cli
original=cli.execute
def fault(event,name):
    if event == sys.argv[1]: raise OSError("injected")
def execute(args, **kwargs):
    if sys.argv[1] == "internal": raise RuntimeError("private detail must not leak")
    return original(args,fault=fault)
cli.execute=execute
sys.argv=["applications.bounded_decision_workflow"]+sys.argv[2:]
runpy.run_module("applications.bounded_decision_workflow",run_name="__main__")
'''
    # Keep the chosen stage outside argv after the bootstrap resets it.
    bootstrap = bootstrap.replace('original=cli.execute', 'original=cli.execute\nstage=sys.argv[1]').replace('sys.argv[1] ==', 'stage ==').replace('event == sys.argv[1]', 'event == stage')
    process = subprocess.run([sys.executable, "-c", bootstrap, stage, "evaluate", "--request", str(request),
        "--snapshot", str(snapshot), "--output-dir", str(output)], cwd=ROOT,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, timeout=30)
    actual = failure(process, code, status)
    assert b"private detail" not in process.stderr
    if stage != "internal":
        assert actual["bundle_state"] == "complete_visible_durability_unknown"
        success(run("verify", "--bundle", output))


def test_command_concurrent_creators_preserve_one_winner(tmp_path, inputs):
    request, snapshot = inputs; dest = tmp_path / "race"
    argv = [sys.executable, "-m", "applications.bounded_decision_workflow", "evaluate", "--request", str(request),
            "--snapshot", str(snapshot), "--output-dir", str(dest)]
    children = [subprocess.Popen(argv, cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
    results = []
    try:
        for child in children:
            stdout, stderr = child.communicate(timeout=30)
            results.append(subprocess.CompletedProcess(argv, child.returncode, stdout, stderr))
    finally:
        for child in children:
            if child.poll() is None: child.kill(); child.communicate()
    assert sorted(r.returncode for r in results) == [0, 5]
    for result in results:
        if result.returncode: failure(result, "OUTPUT_COLLISION", 5)
        else: success(result)
    success(run("verify", "--bundle", dest))


@pytest.mark.parametrize("dimension,limit,code", [("prior_bundle_files", 6, "INPUT_RESOURCE_LIMIT_EXCEEDED"),
    ("aggregate_prior_bundle_bytes", 1024, "INPUT_WIRE_LIMIT_EXCEEDED")])
def test_prior_corpus_limit_refuses_before_reconstruction(tmp_path, inputs, dimension, limit, code):
    request, snapshot = inputs; prior = tmp_path / "prior"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", prior))
    value = json.loads(request.read_bytes()); value["requested_limits"] = dict(BUILD_LIMITS, **{dimension: limit})
    request.write_bytes(canonical_json_bytes(value))
    failure(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "bad", "--compare-to", prior), code, 4)
    assert not (tmp_path / "bad").exists()
