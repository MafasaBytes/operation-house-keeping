"""Recover original evidence and distinguish schema controls from policy inputs."""
import hashlib
import json

import pytest

import applications.bounded_decision_workflow as workflow
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    BASE_REQUEST, BASE_SNAPSHOT, PACKAGE_PATH, object_bytes, object_value,
)
from tests.applications.bounded_decision_workflow.test_s2_raw_projection import canonical


@pytest.fixture(scope="module")
def package():
    return json.loads(PACKAGE_PATH.read_bytes())


def test_originals_and_all_objects_recover(package):
    for kind, digest in (
        ("package", "199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4"),
        ("manifest", "5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a"),
    ):
        path = PACKAGE_PATH.with_name(f"2026-09-15-bounded-decision-workflow-candidate-{kind}-pre-s3-policy-correction.json")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        if kind == "package":
            original = json.loads(path.read_bytes())
            assert all(package["objects"][k] == v for k, v in original["objects"].items())
    for key in package["objects"]:
        assert canonical(object_value(package, key)) == object_bytes(package, key)
    manifest = json.loads(PACKAGE_PATH.with_name(PACKAGE_PATH.name.replace("package", "manifest")).read_bytes())
    assert manifest["candidate_package_sha256"] == hashlib.sha256(PACKAGE_PATH.read_bytes()).hexdigest()
    assert manifest["candidate_package_bytes"] == len(PACKAGE_PATH.read_bytes())


@pytest.mark.parametrize("index", range(3))
def test_only_cost_commitment_changed_and_twins_reach_raw_stage(package, index):
    correction = package["s3_fixture_correction"]["premise_corrections"][index]
    old = object_value(package, correction["old_request"])
    new = object_value(package, correction["new_request"])
    old["target_policy"]["costs"]["canonical_commitment"] = correction["new_premise"]
    assert old == new
    with pytest.raises(workflow.WorkflowInputError) as caught:
        workflow.project_request_and_snapshot(object_bytes(package, correction["old_request"]),
                                              object_bytes(package, BASE_SNAPSHOT))
    assert caught.value.diagnostic.code == "REQUEST_SCHEMA_INVALID"
    assert caught.value.diagnostic.stage == "lexical_schema"
    for reference in (correction["new_request"], BASE_REQUEST):
        actual = workflow.project_request_and_snapshot(object_bytes(package, reference),
                                                       object_bytes(package, BASE_SNAPSHOT))
        assert actual.admission.observed_value.status == "admitted"
        assert all(row["raw_status"] == "ready" for row in actual.raw_projections)


def test_active_request_commitment_sweep_and_missing_effect_diagnostic(package):
    refs = {v["input"]["request_ref"] for c in package["acceptance_cases"]
            for v in c["variants"] if "request_ref" in v["input"]}
    def walk(value):
        if isinstance(value, dict):
            if "canonical_commitment" in value:
                assert value["canonical_commitment"] == hashlib.sha256(canonical(
                    {k: v for k, v in value.items() if k != "canonical_commitment"})).hexdigest()
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)
    for ref in refs:
        walk(object_value(package, ref))
    baseline = object_value(package, BASE_REQUEST)
    del baseline["premises"]["effects"]["E-aH"]
    with pytest.raises(workflow.WorkflowInputError) as caught:
        workflow.project_request_and_snapshot(canonical(baseline), object_bytes(package, BASE_SNAPSHOT))
    variant = next(v for c in package["acceptance_cases"] for v in c["variants"]
                   if v["variant_id"] == "POL-2-missing-effect")
    assert caught.value.diagnostic.code == variant["expected"]["stderr_line"]["code"] == "REQUEST_SCHEMA_INVALID"
