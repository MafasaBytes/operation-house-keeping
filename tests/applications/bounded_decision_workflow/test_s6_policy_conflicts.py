"""Conflict witnesses, NOT passing S6 policy acceptance tests.

Keep both sides of the approved contract visible until owner adjudication.
"""
import hashlib
import json

import pytest

from applications.bounded_decision_workflow import BUILD_LIMITS, parse_request_wire, verify_bundle
from applications.bounded_decision_workflow.input import canonical_json_bytes
from tests.applications.bounded_decision_workflow.test_s6_cli import inputs, run, success, failure


@pytest.mark.parametrize("dimension", ["output_stdout_stderr_bytes", "output_diagnostic_bytes"])
def test_admitted_one_byte_budget_cannot_hold_required_refusal(tmp_path, inputs, dimension):
    request, snapshot = inputs
    value = json.loads(request.read_bytes())
    value["requested_limits"] = dict(BUILD_LIMITS, **{dimension: 1})
    if dimension == "output_diagnostic_bytes": value["snapshot_commitment"] = "0" * 64
    wire = canonical_json_bytes(value)
    admitted, _ = parse_request_wire(wire)
    assert admitted.requested_limits.model_dump()[dimension] == 1
    request.write_bytes(wire)
    process = run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", tmp_path / "refused")
    assert process.returncode in (3, 4) and process.stdout == b""
    assert len(process.stderr) > 1
    assert set(json.loads(process.stderr)) == {"code", "stage", "target", "message_key", "retry_class", "exit_code", "bundle_state"}
    assert not (tmp_path / "refused").exists()


def test_fixed_failure_envelope_cannot_report_complete_incomplete_inventory(tmp_path, inputs):
    request, snapshot = inputs; bundle = tmp_path / "interrupted"
    success(run("evaluate", "--request", request, "--snapshot", snapshot, "--output-dir", bundle))
    (bundle / "manifest.json").unlink()  # Isolated corruption witness only.
    before = {p.name: p.read_bytes() for p in bundle.iterdir()}
    inspected = verify_bundle(bundle)
    assert len(inspected.captured) == 6
    process = run("verify", "--bundle", bundle)
    d = failure(process, "BUNDLE_INCOMPLETE", 3)
    assert "recognized_files" not in d
    full = dict(d, recognized_files={n: hashlib.sha256(b).hexdigest() for n,b in inspected.captured.items()})
    assert len(canonical_json_bytes(full)) + 1 > BUILD_LIMITS["output_stdout_stderr_bytes"]
    assert {p.name: p.read_bytes() for p in bundle.iterdir()} == before
