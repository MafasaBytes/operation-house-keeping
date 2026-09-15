"""Real module-command S6 checks; S7 clean-build release is not asserted."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    PACKAGE_PATH, BASE_REQUEST, BASE_SNAPSHOT, object_bytes,
)

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
