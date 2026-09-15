"""Red-first S4 service tests. No command or filesystem acceptance is claimed."""
import copy
from dataclasses import replace
import hashlib
import inspect
import json

import pytest

import applications.bounded_decision_workflow as workflow
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    PACKAGE_PATH, BASE_REQUEST, BASE_SNAPSHOT, UNAVAILABLE_REQUEST, UNAVAILABLE_SNAPSHOT,
    object_bytes, object_value,
)
from tests.applications.bounded_decision_workflow.test_s2_raw_projection import (
    canonical, recommit, rational, expect_diagnostic,
)
from tests.applications.bounded_decision_workflow.test_s4_fixture_correction import variant
from tests.applications.bounded_decision_workflow.s4_expected_reasoning import inventory
from applications.bounded_decision_workflow import decision_review

BUILD = "1" * 64  # Explicit synthetic test build assertion, not executable authentication.


@pytest.fixture(scope="module")
def package():
    return json.loads(PACKAGE_PATH.read_bytes())


def call(p, request=BASE_REQUEST, snapshot=BASE_SNAPSHOT, prior=None):
    return workflow.review_request_and_snapshot(object_bytes(p, request), object_bytes(p, snapshot),
                                                build_identity=BUILD, prior=prior)


def capture(p, request=BASE_REQUEST, snapshot=BASE_SNAPSHOT, ancestor=None):
    r = call(p, request, snapshot, ancestor)
    return workflow.PriorDecisionInput(object_bytes(p, request), object_bytes(p, snapshot),
                                       r.review_bytes, r.trace_bytes, BUILD, ancestor)


@pytest.mark.parametrize("name", ["POL-3", "POL-4", "REV-1-target", "REV-1-omitted-prior"])
def test_frozen_review_rows_and_genuine_prior_branch(package, name):
    v = variant(package, name)
    prior = capture(package) if "--compare-to" in v["input"]["argv"] else None
    r = call(package, v["input"]["request_ref"], prior=prior)
    expected = object_value(package, v["expected"]["result_ref"])["reevaluation"]
    assert r.reevaluation["decision_rows"] == expected["decision_rows"]
    assert r.reevaluation["disposition"] == expected["disposition"]


def test_target_change_requires_equal_decisions_not_changed_raw(package):
    prior = capture(package)
    v = variant(package, "POL-4")
    r = call(package, v["input"]["request_ref"], prior=prior)
    rows = r.reevaluation["decision_rows"]
    assert sum(x["reevaluation"] == "required" for x in rows) == 13
    assert sum(x["value_changed"] for x in rows) == 7
    assert sum(x["equal_after_reevaluation"] is True for x in rows) == 6


def test_prior_result_is_recomputed_even_when_digest_would_match(package):
    prior = capture(package)
    forged = json.loads(prior.review_wire)
    forged["decision_rows"][0]["value"] = "does_not_match"
    bad = replace(prior, review_wire=json.dumps(forged,sort_keys=True,separators=(",", ":")).encode())
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call(package, prior=bad)
    assert exc.value.diagnostic.code == "PRIOR_INCOMPATIBLE"


def run(world, package, prior):
    return workflow.review_request_and_snapshot(recommit(world), object_bytes(package, BASE_SNAPSHOT),
                                                build_identity=BUILD, prior=prior)


def required(result):
    return {r["decision_id"] for r in result.reevaluation["decision_rows"] if r["reevaluation"] == "required"}


def action_decisions(actions):
    return {f"{layer}:{h}:{a}" for layer in ("raw", "target") for h in ("H_F", "H_H") for a in actions} | {
        "feasibility:" + a for a in actions} | {"selection"}


@pytest.mark.parametrize("group,key,actions", [
    ("global_applicability", None, ("a0", "aF", "aH", "aHF")),
    ("support_semantics", None, ("a0", "aF", "aH", "aHF")),
    ("effects", "E-aH", ("aH", "aHF")),
    ("preconditions", "PC-isolation", ("aH", "aHF")),
    ("timing", "T-aH", ("aH", "aHF")),
    ("invariances", "I-aH", ("aH", "aHF")),
])
def test_six_missing_dependency_witnesses_and_unaffected_twins(package, group, key, actions):
    world = object_value(package, BASE_REQUEST)
    prior = capture(package)
    premise = world["premises"][group]
    if key is not None: premise = premise[key]
    premise.update(availability="unknown", value=None)
    actual = run(world, package, prior)
    # Explicit affected-action table, not runtime dependency closure or equality.
    expected = action_decisions(actions)
    assert required(actual) == expected
    assert {r["decision_id"] for r in actual.reevaluation["decision_rows"] if r["value_changed"]} == expected
    assert required(call(package, prior=prior)) == set()
    assert actual.policy.projection.admission.observed_value.status == "admitted"


def test_all_22_direct_dependency_sets_match_independent_manual_inventory(package):
    v = variant(package, "REV-1-omitted-prior")
    expected_result = object_value(package, v["expected"]["result_ref"])
    expected = inventory(object_value(package, BASE_REQUEST), expected_result)
    actual = {r["decision_id"]: r["depends_on"] for r in call(package).reevaluation["decision_rows"]}
    assert actual == {k: sorted(v) for k, v in expected.items()}
    # A deleted support and a spurious whole-result cost edge must both fail this
    # equality; checking subset coverage alone would miss the latter.
    for mutate in ("missing", "extra"):
        wrong = copy.deepcopy(actual)
        if mutate == "missing": wrong["raw:H_F:aH"].remove("premise:E-aH")
        else: wrong["raw:H_F:aH"].append("cost:aH")
        assert wrong != actual


@pytest.mark.parametrize("mutation", ["actor", "receipt", "noneligible_cost"])
def test_irrelevant_changes_preserve_all_decisions_but_retain_provenance(package, mutation):
    world = object_value(package, BASE_REQUEST)
    if mutation == "actor": world["actor_assertion"]["actor_label"] += "-review"
    elif mutation == "receipt": world["request_id"] += "-review"
    else: world["target_policy"]["costs"]["value"]["entries"][0]["cost"] = rational(19)
    prior = capture(package)
    actual = run(world, package, prior)
    assert required(actual) == set()
    assert not any(r["value_changed"] for r in actual.reevaluation["decision_rows"])
    assert actual.reevaluation["changed_paths"]
    assert actual.trace["request_commitment"] != hashlib.sha256(prior.request_wire).hexdigest()
    assert actual.trace["request_commitment"] == hashlib.sha256(recommit(world)).hexdigest()


def test_parameter_sensitivity_and_equal_output_reevaluation(package):
    world = object_value(package, BASE_REQUEST)
    alpha = world["premises"]["coordinates"]["alpha"]["value"]
    alpha.update(lower=rational(11), upper=rational(11))
    result = run(world, package, capture(package))
    assert required(result) == action_decisions(("a0", "aF", "aH", "aHF"))
    rows = {r["decision_id"]: r for r in result.reevaluation["decision_rows"]}
    # alpha multiplies the heater state; isolated rows retain equal numeric
    # values, yet the explicitly required S2 support envelope changed.
    assert rows["raw:H_F:aH"]["equal_after_reevaluation"] is True
    assert rows["raw:H_H:a0"]["value_changed"] is True


def test_target_change_with_all_values_equal_still_propagates(package):
    world = object_value(package, BASE_REQUEST)
    world["target_policy"]["target"]["value"].update(lower=rational(30), upper=rational(34))
    result = run(world, package, capture(package))
    assert len(required(result)) == 13
    assert all(not r["value_changed"] for r in result.reevaluation["decision_rows"])
    assert sum(r["equal_after_reevaluation"] is True for r in result.reevaluation["decision_rows"]) == 13


def test_cost_change_preserves_physics_and_can_retain_same_selection(package):
    world = object_value(package, BASE_REQUEST)
    world["target_policy"]["costs"]["value"]["entries"][3]["cost"] = rational(7)
    result = run(world, package, capture(package))
    assert required(result) == {"selection"}
    assert result.reevaluation["decision_rows"][-1]["equal_after_reevaluation"] is True
    assert result.policy.projection.raw_projection_bytes == call(package).policy.projection.raw_projection_bytes


@pytest.mark.parametrize("field", ["target", "costs", "retained_hypotheses", "feasibility_rule", "selection_rule"])
def test_missing_policy_support_and_valid_twins(package, field):
    world = object_value(package, BASE_REQUEST)
    world["target_policy"][field].update(availability="unknown", value=None)
    result = run(world, package, capture(package))
    expected = ({"selection"} if field in ("costs", "selection_rule") else
                {"feasibility:" + a for a in ("a0", "aF", "aH", "aHF")} | {"selection"})
    if field == "target": expected |= {f"target:{h}:{a}" for h in ("H_F", "H_H") for a in ("a0", "aF", "aH", "aHF")}
    assert required(result) == expected
    assert result.policy.selection["disposition"] == "unknown"
    assert call(package).policy.selection["disposition"] == "selected_from_supplied_set"


def test_unavailable_public_twin_requires_full_snapshot_dependency(package):
    baseline = object_value(package, BASE_SNAPSHOT)
    unavailable = object_value(package, UNAVAILABLE_SNAPSHOT)
    assert baseline["state"] == unavailable["state"]
    # The complete public twin changes more than 64 leaf paths: end-to-end
    # comparison must refuse, not silently discard changes or raise the cap.
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call(package, UNAVAILABLE_REQUEST, UNAVAILABLE_SNAPSHOT, capture(package))
    assert exc.value.diagnostic.target == "changed_paths"
    result = call(package, UNAVAILABLE_REQUEST, UNAVAILABLE_SNAPSHOT)
    # Isolate the dependency kernel only after both public inputs were admitted.
    rows = decision_review._review_rows(decision_review._support_and_decisions(result.policy),
        decision_review._support_and_decisions(call(package).policy))
    assert all(r["reevaluation"] == "required" for r in rows)
    assert rows[0]["value"] is None
    assert result.policy.projection.admission.current_condition.disposition == "unavailable"
    assert all(r["raw_status"] == "unknown" for r in result.policy.projection.raw_projections)


@pytest.mark.parametrize("mutation", ["build", "profile", "trace", "schema", "stale", "forged", "wrong_type"])
def test_prior_integrity_refusals_exact_diagnostic_and_valid_twin(package, mutation):
    prior = capture(package)
    if mutation == "build": bad = replace(prior, build_identity="2" * 64)
    elif mutation == "trace": bad = replace(prior, trace_wire=b"{}")
    elif mutation == "wrong_type": bad = {"verified": True}
    elif mutation in ("stale", "forged"):
        # Retained original OBS-3 pair and corrected matching hostile pair.
        v = variant(package, "OBS-3-decimal-reconstruction" if mutation == "forged" else "OBS-3-decimal-stale-commitment")
        bad = replace(prior, request_wire=object_bytes(package, v["input"]["request_ref"]),
                      snapshot_wire=object_bytes(package, v["input"]["snapshot_ref"]))
    else:
        q = json.loads(prior.request_wire)
        if mutation == "profile": q["workflow_profile"] = "unsupported"
        else: q["extra"] = True
        bad = replace(prior, request_wire=canonical(q))
    expect_diagnostic(lambda: call(package, prior=bad), package, "PRIOR_INCOMPATIBLE")
    assert required(call(package, prior=prior)) == set()


def test_current_admission_precedence_is_not_reordered(package):
    for name, code in (("OBS-3-decimal-reconstruction", "PUBLIC_RECONSTRUCTION_REFUSED"),
                       ("OBS-3-decimal-stale-commitment", "SNAPSHOT_COMMITMENT_MISMATCH")):
        v = variant(package, name)
        expect_diagnostic(lambda: call(package, v["input"]["request_ref"], v["input"]["snapshot_ref"]), package, code)


def test_no_runtime_import_of_oracle_private_backend_or_io():
    source = inspect.getsource(decision_review)
    for text in ("tests.", "candidate-package", "object_value", "pathlib", "subprocess", "open(", "model_kernel._"):
        assert text not in source


def test_canonical_determinism_and_detached_outputs(package):
    prior = capture(package)
    first = call(package, prior=prior)
    world = json.loads(object_bytes(package, BASE_REQUEST))
    reversed_world = dict(reversed(list(world.items())))
    second = run(reversed_world, package, prior)
    assert (first.review_bytes, first.trace_bytes, first.resource_counts_bytes) == (
        second.review_bytes, second.trace_bytes, second.resource_counts_bytes)
    first.reevaluation["decision_rows"].clear()
    assert len(first.reevaluation["decision_rows"]) == 22


def nodes(value):
    children = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
    return 1 + sum(nodes(v) for v in children)


def test_counts_independent_and_no_reference_deduplication(package):
    prior = capture(package)
    result = call(package, prior=prior)
    q, s = json.loads(prior.request_wire), json.loads(prior.snapshot_wire)
    def references(v):
        if isinstance(v, list): return sum(references(x) for x in v)
        if not isinstance(v, dict): return 0
        total = 0
        for key, value in v.items():
            if key.endswith(("_id", "_ids", "_reference", "_commitment")) or key in ("supersedes", "via_assertion_ids"):
                total += len(value) if isinstance(value, list) else 0 if isinstance(value, dict) else 1
            total += references(value)
        return total
    refs = references(q) + references(s)
    validators = 1 + len(s["state"]["material"]["records"]) + len(s["conditions"]) + len(s["constraint_evaluations"])
    validators += sum(len(v["candidates"]) for v in s["constraint_evaluations"])
    c = result.resource_counts
    assert c["resolved_input_bytes"] == 2 * (len(prior.request_wire) + len(prior.snapshot_wire))
    assert c["input_reference_occurrences"] == 2 * refs
    assert c["input_resolution_charges"] == 2 * (nodes(q) + nodes(s) + refs + 3 + validators)
    assert c["prior_wire_bytes"] == sum(map(len, (prior.request_wire, prior.snapshot_wire, prior.review_wire, prior.trace_wire)))
    assert c["corner_evaluations"] == 16 and c["trace_rows"] == 30


@pytest.mark.parametrize("limit,cap", [
    ("decision_rows", 22), ("output_trace_rows", 30), ("corner_evaluations", 16),
    ("input_reference_occurrences", 1382), ("input_resolution_charges", 7920),
])
def test_exact_aggregate_boundary_and_one_under_refusal(package, limit, cap):
    world = object_value(package, BASE_REQUEST)
    prior = capture(package)
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, **{limit: cap})
    # Replacing baseline null limits with the complete 26-entry map adds 26
    # nodes to 7,894 charges. Resource metadata isn't a decision dependency.
    result = run(world, package, prior)
    assert required(result) == set()
    world["requested_limits"][limit] = cap - 1
    with pytest.raises(workflow.WorkflowInputError) as exc:
        run(world, package, prior)
    assert exc.value.diagnostic.exit_code == 4
    assert not hasattr(exc.value, "policy")
    assert exc.value.diagnostic.code == ("OUTPUT_LIMIT_EXCEEDED" if limit.startswith("output") else "INPUT_RESOURCE_LIMIT_EXCEEDED")


@pytest.mark.parametrize("limit", ["output_result_bytes", "output_result_nodes", "output_trace_bytes"])
def test_complete_s4_output_boundary_includes_dependencies(package, limit):
    world = object_value(package, BASE_REQUEST)
    result = run(world, package, None)
    combined = dict(json.loads(result.policy.policy_bytes), raw_projections=result.policy.projection.raw_projections,
                    reevaluation=result.reevaluation)
    cap = {"output_result_bytes": len(canonical(combined)), "output_result_nodes": nodes(combined),
           "output_trace_bytes": len(result.trace_bytes)}[limit]
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, **{limit: cap})
    assert len(run(world, package, None).reevaluation["decision_rows"]) == 22
    world["requested_limits"][limit] -= 1
    expect_diagnostic(lambda: run(world, package, None), package, "OUTPUT_LIMIT_EXCEEDED")


def test_aggregate_limits_refuse_before_public_reconstruction(package, monkeypatch):
    prior = capture(package)
    chained = replace(prior, prior=prior)
    monkeypatch.setattr(decision_review, "_admit_parsed", lambda *a: pytest.fail("reconstruction before aggregate check"))
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call(package, prior=chained)
    assert exc.value.diagnostic.target == "resolved_input_bytes"
    assert exc.value.diagnostic.exit_code == 4


def test_corner_limit_is_aggregate_and_checked_before_arithmetic(package, monkeypatch):
    prior = capture(package)
    world = object_value(package, BASE_REQUEST)
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, corner_evaluations=15)
    monkeypatch.setattr(decision_review, "_assess_admitted", lambda *a, **k: pytest.fail("arithmetic before aggregate corner bound"))
    with pytest.raises(workflow.WorkflowInputError) as exc:
        run(world, package, prior)
    assert exc.value.diagnostic.target == "corner_evaluations"


@pytest.mark.parametrize("field,cap", [("request_wire", "request_wire_bytes"), ("snapshot_wire", "snapshot_wire_bytes"),
                                      ("review_wire", "output_result_bytes"), ("trace_wire", "output_trace_bytes")])
def test_oversized_prior_refuses_before_parse(package, monkeypatch, field, cap):
    prior = replace(capture(package), **{field: b"x" * (workflow.BUILD_LIMITS[cap] + 1)})
    original = decision_review.parse_request_wire
    calls = []
    def parse(wire):
        calls.append(wire)
        assert len(calls) == 1, "oversized prior was parsed"
        return original(wire)
    monkeypatch.setattr(decision_review, "parse_request_wire", parse)
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call(package, prior=prior)
    assert exc.value.diagnostic.target == cap
    assert exc.value.diagnostic.exit_code == 4


def test_changed_path_bound_and_escaping():
    before = {"a/b~c": 0}
    assert decision_review._changed_paths(before, {"a/b~c": 1}, 1) == ["/a~1b~0c"]
    assert len(decision_review._changed_paths({}, {str(i): i for i in range(64)}, 64)) == 64
    with pytest.raises(workflow.WorkflowInputError) as exc:
        decision_review._changed_paths({}, {str(i): i for i in range(65)}, 64)
    assert exc.value.diagnostic.target == "changed_paths"


def test_retained_set_membership_and_removed_cost_support_union(package):
    world = object_value(package, BASE_REQUEST)
    world["target_policy"]["retained_hypotheses"]["value"]["hypothesis_ids"] = ["H_F"]
    result = run(world, package, capture(package))
    assert required(result) == {"feasibility:" + a for a in ("a0", "aF", "aH", "aHF")} | {"selection"}
    # Union retains the old H_H support in the comparison receipt.
    row = next(r for r in result.reevaluation["decision_rows"] if r["decision_id"] == "feasibility:aH")
    assert "target:H_H:aH" in row["depends_on"]
    assert result.policy.selection["selected_action_ids"] == ["aF"]


def test_unknown_cost_preserves_plural_or_unknown_policy_without_physics_change(package):
    for name, disposition in (("POL-5-tie", "selected_from_supplied_set"), ("POL-5-missing-cost", "unknown")):
        v = variant(package, name)
        result = call(package, v["input"]["request_ref"], prior=capture(package))
        assert required(result) == {"selection"}
        assert result.policy.selection["disposition"] == disposition
        if name.endswith("tie"): assert result.policy.selection["selected_action_ids"] == ["aH", "aHF"]


@pytest.mark.parametrize("field,value", [("state", None), ("conditions", 1), ("constraint_evaluations", [None])])
def test_malformed_public_collections_still_reach_authoritative_refusal(package, field, value):
    snapshot = object_value(package, BASE_SNAPSHOT)
    snapshot[field] = value
    wire = canonical(snapshot)
    request = object_value(package, BASE_REQUEST)
    request["snapshot_commitment"] = hashlib.sha256(wire).hexdigest()
    rq = recommit(request)
    expect_diagnostic(lambda: workflow.review_request_and_snapshot(rq, wire, build_identity=BUILD),
                      package, "PUBLIC_RECONSTRUCTION_REFUSED")
    bad = replace(capture(package), request_wire=rq, snapshot_wire=wire)
    expect_diagnostic(lambda: call(package, prior=bad), package, "PRIOR_INCOMPATIBLE")


@pytest.mark.parametrize("name", [
    "CMD-2-unavailable", "CMD-2-no-feasible", "OBS-2-absent", "OBS-4-interpreted-unit",
    "NUM-1-endpoint", "UNC-1", "UNC-2-missing", "POL-1-false", "POL-1-mixed",
    "POL-2-unknown-precondition", "POL-5-tie", "POL-5-missing-cost", "RES-2-tighter",
])
def test_remaining_frozen_service_results_without_claiming_command_execution(package, name):
    v = variant(package, name)
    result = call(package, v["input"]["request_ref"], v["input"]["snapshot_ref"])
    expected = object_value(package, v["expected"]["result_ref"])
    assert result.reevaluation["decision_rows"] == expected["reevaluation"]["decision_rows"]
    assert result.policy.projection.raw_projections == expected["raw_projections"]
    assert result.policy.selection == expected["selection"]
