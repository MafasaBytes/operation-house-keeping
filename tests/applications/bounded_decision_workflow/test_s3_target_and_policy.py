"""S3 expectations: frozen preparation oracle plus independent set reasoning.

Same-author provenance; shared synthetic premises, not runtime arithmetic helpers.
No test below claims S4 review or command/retention acceptance.
"""
from fractions import Fraction as F
from itertools import product
import inspect
import json

import pytest

import applications.bounded_decision_workflow as workflow
from applications.bounded_decision_workflow import policy
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    BASE_REQUEST, BASE_SNAPSHOT, UNAVAILABLE_REQUEST, UNAVAILABLE_SNAPSHOT,
    PACKAGE_PATH, object_bytes, object_value,
)
from tests.applications.bounded_decision_workflow.test_s2_raw_projection import (
    canonical, recommit, rational, set_bounds, expect_diagnostic,
)


@pytest.fixture(scope="module")
def package():
    return json.loads(PACKAGE_PATH.read_bytes())


@pytest.fixture
def world(package):
    return object_value(package, BASE_REQUEST)


def run(world, package):
    return workflow.assess_request_and_snapshot(recommit(world), object_bytes(package, BASE_SNAPSHOT))


@pytest.mark.parametrize("case_id", ["NUM-1", "UNC-1", "UNC-2", "POL-1", "POL-2", "POL-3", "POL-4", "POL-5"])
def test_frozen_semantic_layers_reach_intended_branches(package, case_id):
    case = next(c for c in package["acceptance_cases"] if c["acceptance_id"] == case_id)
    for v in case["variants"]:
        if "result_ref" not in v["expected"]:
            continue
        actual = workflow.assess_request_and_snapshot(object_bytes(package, v["input"]["request_ref"]),
                                                      object_bytes(package, v["input"]["snapshot_ref"]))
        expected = object_value(package, v["expected"]["result_ref"])
        assert actual.projection.raw_projections == expected["raw_projections"]
        for key in ("target_relations", "feasibility", "selection"):
            assert getattr(actual, key) == expected[key], v["variant_id"]
        assert len(actual.target_relations) == 8 and len(actual.feasibility) == 4
        assert actual.projection.admission.observed_value.status == "admitted"
        assert actual.policy_trace["request_commitment"] == v["input"]["request_ref"]
        assert len(actual.policy_trace["rows"]) == 13
        assert not hasattr(actual, "reevaluation")


@pytest.mark.parametrize("index", range(3))
def test_stale_controls_are_not_policy_coverage(package, index, monkeypatch):
    c = package["s3_fixture_correction"]["stale_admission_controls"][index]
    actual = workflow.assess_request_and_snapshot(object_bytes(package, c["valid_twin_request_ref"]),
                                                 object_bytes(package, BASE_SNAPSHOT))
    assert all(r["raw_status"] == "ready" for r in actual.projection.raw_projections)
    monkeypatch.setattr(policy, "_selection", lambda *a, **k: pytest.fail("policy reached by stale input"))
    expect_diagnostic(lambda: workflow.assess_request_and_snapshot(object_bytes(package, c["request_ref"]),
                      object_bytes(package, BASE_SNAPSHOT)), package, "REQUEST_SCHEMA_INVALID")


@pytest.mark.parametrize("lo,hi,glo,ghi", list(product(range(-1, 2), repeat=4)))
def test_target_relation_independent_finite_set_oracle(lo, hi, glo, ghi):
    # For integer interval endpoints a half-integer lattice distinguishes subset,
    # overlap and disjointness, including point contact, without copying inequalities.
    lo, hi = sorted((lo, hi)); glo, ghi = sorted((glo, ghi))
    raw = set(range(2 * lo, 2 * hi + 1)); target = set(range(2 * glo, 2 * ghi + 1))
    expected = "guaranteed" if raw <= target else "possible_not_guaranteed" if raw & target else "incompatible"
    assert policy._target_relation("ready", (F(lo), F(hi)), (F(glo), F(ghi))) == expected


@pytest.mark.parametrize("pair", list(product(
    ("guaranteed", "possible_not_guaranteed", "incompatible", "unknown"), repeat=2)))
def test_robust_feasibility_complete_table(pair):
    # Ordered table expressed as independently specified status sets.
    known = set(pair)
    table = {
        frozenset({"guaranteed"}): "guaranteed",
        frozenset({"possible_not_guaranteed"}): "possible_not_guaranteed",
        frozenset({"guaranteed", "possible_not_guaranteed"}): "possible_not_guaranteed",
        frozenset({"incompatible"}): "incompatible",
        frozenset({"incompatible", "guaranteed"}): "incompatible",
        frozenset({"incompatible", "possible_not_guaranteed"}): "incompatible",
    }
    expected = "unknown" if "unknown" in known else table[frozenset(known)]
    assert policy._feasibility(pair) == expected
    assert policy._feasibility(pair, false_gate=True) == "inapplicable"
    assert policy._feasibility(pair, supported=False) == "unknown"


@pytest.mark.parametrize("unknown_cost", [None, F(1), F(2), F(3)])
@pytest.mark.parametrize("eligible_cost", [None, F(2)])
def test_hidden_eligible_completion_oracle(unknown_cost, eligible_cost):
    states = dict(zip(policy.ACTION_IDS, ("incompatible", "unknown", "guaranteed", "guaranteed")))
    costs = dict(zip(policy.ACTION_IDS, (None, unknown_cost, eligible_cost, F(5))))
    # Enumerate possible completions: an unknown action may be eligible or not;
    # absent costs sample 0,2,6, sufficient to exhibit distinct minima in this case.
    answers = set()
    for include, uc, ec in product((False, True),
                                   [unknown_cost] if unknown_cost is not None else [F(0), F(2), F(6)],
                                   [eligible_cost] if eligible_cost is not None else [F(0), F(2), F(6)]):
        candidates = {"aH": ec, "aHF": F(5)}
        if include: candidates["aF"] = uc
        minimum = min(candidates.values())
        answers.add((minimum, tuple(sorted(a for a, cost in candidates.items() if cost == minimum))))
    actual = policy._selection(states, costs)
    if len(answers) > 1:
        assert actual == {"disposition": "unknown", "minimum_cost": None, "selected_action_ids": []}
    else:
        minimum, actions = answers.pop()
        assert actual == {"disposition": "selected_from_supplied_set",
                          "minimum_cost": rational(minimum.numerator, minimum.denominator),
                          "selected_action_ids": list(actions)}


@pytest.mark.parametrize("state,expected", [
    ("unknown", "unknown"), ("incompatible", "no_feasible_action_in_supplied_set"),
    ("inapplicable", "no_feasible_action_in_supplied_set"),
    ("possible_not_guaranteed", "no_feasible_action_in_supplied_set"),
])
def test_no_eligible_and_false_global(state, expected):
    states = dict.fromkeys(policy.ACTION_IDS, state)
    costs = dict.fromkeys(policy.ACTION_IDS)
    assert policy._selection(states, costs)["disposition"] == expected
    assert policy._selection(states, costs, global_false=True)["disposition"] == "inapplicable_for_declared_model"


def test_target_only_and_cost_only_layer_separation(world, package):
    baseline = run(world, package)
    world["target_policy"]["costs"]["value"]["entries"][2]["cost"] = rational(5)
    cost = run(world, package)
    assert cost.projection.raw_projection_bytes == baseline.projection.raw_projection_bytes
    assert cost.target_relations == baseline.target_relations
    assert cost.feasibility == baseline.feasibility
    assert cost.selection["selected_action_ids"] == ["aH", "aHF"]
    world["target_policy"]["target"]["value"].update(lower=rational(25), upper=rational(27))
    target = run(world, package)
    assert target.projection.raw_projection_bytes == baseline.projection.raw_projection_bytes
    assert all(r["target_relation"] == "incompatible" for r in target.target_relations)
    assert target.selection["disposition"] == "no_feasible_action_in_supplied_set"
    assert cost.policy_trace["request_commitment"] != baseline.policy_trace["request_commitment"]
    assert not hasattr(target, "reevaluation")  # S4, not inferred from equal values.


@pytest.mark.parametrize("availability", ["missing", "unknown"])
@pytest.mark.parametrize("name", ["target", "costs", "retained_hypotheses", "feasibility_rule", "selection_rule"])
def test_incomplete_policy_no_defaults(world, package, name, availability):
    baseline = run(world, package)
    world["target_policy"][name].update(availability=availability, value=None)
    result = run(world, package)
    assert result.projection.raw_projection_bytes == baseline.projection.raw_projection_bytes
    assert result.selection["disposition"] == "unknown"
    assert result.policy_trace["unavailable_policy_ids"]
    if name == "target":
        assert {r["target_relation"] for r in result.target_relations} == {"unknown"}


@pytest.mark.parametrize("group,key", [
    ("effects", "E-aH"), ("preconditions", "PC-isolation"),
    ("timing", "T-aH"), ("invariances", "I-aH"),
])
@pytest.mark.parametrize("availability", ["missing", "unknown"])
def test_action_support_frontiers_and_valid_twins(world, package, group, key, availability):
    assert run(world, package).selection["selected_action_ids"] == ["aH"]
    world["premises"][group][key].update(availability=availability, value=None)
    result = run(world, package)
    assert result.selection["disposition"] == "unknown"
    assert [r["feasibility"] for r in result.feasibility] == ["incompatible", "incompatible", "unknown", "unknown"]
    assert key in next(r for r in result.projection.raw_trace["projection_rows"] if r["action_id"] == "aH")["frontier_ids"]


@pytest.mark.parametrize("group,key", [("preconditions", "PC-isolation"), ("timing", "T-aH"), ("invariances", "I-aH")])
def test_false_gate_dominates_missing_target_and_effect(world, package, group, key):
    world["premises"][group][key]["value"]["status"] = False
    world["premises"]["effects"]["E-aH"].update(availability="missing", value=None)
    world["target_policy"]["target"].update(availability="missing", value=None)
    actual = run(world, package)
    assert [r["feasibility"] for r in actual.feasibility] == ["unknown", "unknown", "inapplicable", "inapplicable"]


@pytest.mark.parametrize("action,index,cost,expected", [
    ("aF", 1, 1, "unknown"), ("aF", 1, 2, "unknown"),
    ("aF", 1, 3, "selected_from_supplied_set"),
])
def test_unknown_action_cost_threshold_integration(world, package, action, index, cost, expected):
    # Unknown restoration leaves aH guaranteed and aF/aHF unknown.
    world["premises"]["preconditions"]["PC-restoration"].update(availability="unknown", value=None)
    world["target_policy"]["costs"]["value"]["entries"][index]["cost"] = rational(cost)
    assert run(world, package).selection["disposition"] == expected


def test_missing_noneligible_cost_and_exact_fractional_tie(world, package):
    entries = world["target_policy"]["costs"]["value"]["entries"]
    entries[0].update(availability="missing", cost=None)
    entries[2]["cost"] = entries[3]["cost"] = rational(1, 3)
    actual = run(world, package)
    assert actual.selection == {"disposition": "selected_from_supplied_set", "minimum_cost": rational(1, 3),
                                "selected_action_ids": ["aH", "aHF"]}
    assert actual.policy_trace["unavailable_cost_action_ids"] == ["a0"]


@pytest.mark.parametrize("mutation,code", [
    ("cost_float", "REQUEST_SCHEMA_INVALID"), ("cost_bool", "REQUEST_SCHEMA_INVALID"),
    ("target_bool", "REQUEST_SCHEMA_INVALID"), ("negative", "SUPPORT_MALFORMED"),
    ("unreduced", "SUPPORT_MALFORMED"), ("denominator", "SUPPORT_MALFORMED"),
    ("reverse", "SUPPORT_MALFORMED"), ("unit", "PROFILE_UNSUPPORTED"),
    ("open", "PROFILE_UNSUPPORTED"), ("token", "PROFILE_UNSUPPORTED"),
    ("duplicate", "CARDINALITY_INVALID"), ("empty_retained", "CARDINALITY_INVALID"),
    ("extra_retained", "CARDINALITY_INVALID"), ("stale_entry", "STALE_REFERENCE"),
    ("stale_target", "STALE_REFERENCE"), ("edition", "EDITION_MISMATCH"),
    ("unsupported_rule", "PROFILE_UNSUPPORTED"), ("unsupported_selection", "PROFILE_UNSUPPORTED"),
    ("identity", "PROFILE_UNSUPPORTED"), ("authority", "PROFILE_UNSUPPORTED"),
    ("oversized", "NUMERIC_LIMIT_EXCEEDED"), ("missing_effect", "REQUEST_SCHEMA_INVALID"),
    ("dependency_effect", "PROFILE_UNSUPPORTED"),
])
def test_hostile_policy_and_valid_twins(world, package, mutation, code):
    assert run(world, package).selection["selected_action_ids"] == ["aH"]
    p = world["target_policy"]; t = p["target"]["value"]; costs = p["costs"]["value"]
    entry = costs["entries"][0]
    if mutation == "cost_float": entry["cost"] = 1.0
    elif mutation == "cost_bool": entry["cost"] = rational(True)
    elif mutation == "target_bool": t["lower"] = rational(False)
    elif mutation == "negative": entry["cost"] = rational(-1)
    elif mutation == "unreduced": entry["cost"] = rational(2, 2)
    elif mutation == "denominator": entry["cost"] = rational(1, 0)
    elif mutation == "reverse": t.update(lower=rational(33), upper=rational(31))
    elif mutation == "unit": t["unit_role"] = "kelvin"
    elif mutation == "open": t["endpoint_semantics"] = "open"
    elif mutation == "token": costs["cost_token"] = "mixed_currency"
    elif mutation == "duplicate": costs["entries"][1]["action_id"] = "a0"
    elif mutation == "empty_retained": p["retained_hypotheses"]["value"]["hypothesis_ids"] = []
    elif mutation == "extra_retained": p["retained_hypotheses"]["value"]["hypothesis_ids"] = ["H_X"]
    elif mutation == "stale_entry": entry["availability"] = "stale_reference"
    elif mutation == "stale_target": p["target"]["availability"] = "stale_reference"
    elif mutation == "edition": p["costs"]["edition"] = 2
    elif mutation == "unsupported_rule": p["feasibility_rule"]["value"]["kind"] = "nominal"
    elif mutation == "unsupported_selection": p["selection_rule"]["value"]["ties"] = "first"
    elif mutation == "identity": p["costs"]["premise_id"] = "P-other"
    elif mutation == "authority": p["costs"]["epistemic_kind"] = "synthetic_assumption"
    elif mutation == "oversized": entry["cost"] = rational(10 ** 128)
    elif mutation == "missing_effect": del world["premises"]["effects"]["E-aH"]
    elif mutation == "dependency_effect": world["premises"]["effects"]["E-aH"]["value"] = {"kind": "dependency", "from": "heater", "to": "temperature"}
    expect_diagnostic(lambda: run(world, package), package, code)


def test_exact_endpoint_and_uncertainty_integration(world, package):
    # Independent arithmetic: 40 - 4 - beta*(40-20) = 36-20*beta.
    set_bounds(world, "beta", (1, 10), (3, 10))  # [30,34], not merely nominal 32.
    t = world["target_policy"]["target"]["value"]
    for lo, hi, expected in ((30, 34, "guaranteed"), (34, 35, "possible_not_guaranteed"),
                             (35, 36, "incompatible"), (31, 33, "possible_not_guaranteed")):
        t.update(lower=rational(lo), upper=rational(hi))
        result = run(world, package)
        row = next(r for r in result.target_relations if r["hypothesis_id"] == "H_H" and r["action_id"] == "aH")
        assert row["target_relation"] == expected


def test_unavailable_observation_no_policy_substitution(package):
    result = workflow.assess_request_and_snapshot(object_bytes(package, UNAVAILABLE_REQUEST),
                                                  object_bytes(package, UNAVAILABLE_SNAPSHOT))
    assert result.projection.admission.current_condition.disposition == "unavailable"
    assert {r["target_relation"] for r in result.target_relations} == {"unknown"}
    assert result.selection["disposition"] == "unknown"


def test_policy_numeric_schema_precedes_limit_and_reconstruction(world, package, monkeypatch):
    world["target_policy"]["costs"]["value"]["entries"][0]["cost"] = rational(True)
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, corner_evaluations=129)
    world["snapshot_commitment"] = "0" * 64
    expect_diagnostic(lambda: run(world, package), package, "REQUEST_SCHEMA_INVALID")


def test_profile_refusal_precedes_projection(world, package, monkeypatch):
    world["target_policy"]["costs"]["edition"] = 2
    monkeypatch.setattr(policy, "_project_admitted", lambda *a: pytest.fail("arithmetic before profile"))
    expect_diagnostic(lambda: run(world, package), package, "EDITION_MISMATCH")


@pytest.mark.parametrize("limit", ["output_result_bytes", "output_result_nodes", "output_trace_bytes", "output_trace_rows"])
def test_combined_output_limits_and_no_partial_result(world, package, limit):
    baseline = run(world, package)
    combined = dict(json.loads(baseline.policy_bytes), raw_projections=baseline.projection.raw_projections)
    def nodes(value):
        # Independent output counter, not the runtime resource helper.
        children = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
        return 1 + sum(nodes(v) for v in children)
    counts = {"output_result_bytes": len(canonical(combined)),
              "output_result_nodes": nodes(combined),
              "output_trace_bytes": len(canonical({"raw": baseline.projection.raw_trace, "policy": baseline.policy_trace})),
              "output_trace_rows": 21}
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, **{limit: counts[limit]})
    assert run(world, package).selection == baseline.selection
    world["requested_limits"][limit] -= 1
    expect_diagnostic(lambda: run(world, package), package, "OUTPUT_LIMIT_EXCEEDED")


def test_max_corner_trace_fits_and_policy_results_are_detached(world, package):
    for key, lo, hi in (("A", (19, 1), (21, 1)), ("alpha", (9, 1), (11, 1)),
                        ("gamma", (3, 1), (5, 1)), ("beta", (1, 10), (3, 10))):
        set_bounds(world, key, lo, hi)
    result = run(world, package)
    assert result.projection.corner_evaluations == 128
    assert len(canonical({"raw": result.projection.raw_trace, "policy": result.policy_trace})) <= 16384
    copy = result.selection; copy["disposition"] = "forged"
    assert result.selection["disposition"] != "forged"
    again = run(world, package)
    assert again.policy_bytes == result.policy_bytes and again.policy_trace_bytes == result.policy_trace_bytes


def test_no_source_or_fixture_io_in_policy_and_public_admission_reused(world, package, monkeypatch):
    source = inspect.getsource(policy)
    assert "backend." not in source and "open(" not in source and "Path(" not in source
    calls = []
    original = policy.admit_request_and_snapshot
    def spy(*args):
        calls.append(args)
        return original(*args)
    monkeypatch.setattr(policy, "admit_request_and_snapshot", spy)
    result = run(world, package)
    assert len(calls) == 1
    assert result.projection.admission.current_condition.disposition == "matches"
    assert result.projection.admission.request.target_policy.costs.epistemic_kind == "application_policy"
    assert "not_global_optimality" in result.policy_trace["meaning"]


@pytest.mark.parametrize("retained,selected", [(["H_F"], ["aF"]), (["H_H"], ["aH"]), (["H_F", "H_H"], ["aHF"])])
def test_exact_retained_set_not_automatic_hypothesis_selection(world, package, retained, selected):
    world["target_policy"]["retained_hypotheses"]["value"]["hypothesis_ids"] = retained
    result = run(world, package)
    assert result.selection["selected_action_ids"] == selected
    assert len(result.target_relations) == 8  # Unretained raw/target rows are not erased.


@pytest.mark.parametrize("name", ["target", "costs", "retained_hypotheses", "feasibility_rule", "selection_rule"])
def test_missing_envelope_is_not_missing_support(world, package, name):
    del world["target_policy"][name]
    expect_diagnostic(lambda: run(world, package), package, "REQUEST_SCHEMA_INVALID")


@pytest.mark.parametrize("name", ["target", "costs", "retained_hypotheses", "feasibility_rule", "selection_rule"])
def test_carried_unknown_policy_body_is_not_used(world, package, name):
    world["target_policy"][name]["availability"] = "unknown"
    assert run(world, package).selection["disposition"] == "unknown"


def test_irrelevant_provenance_changes_are_retained_not_semantic(world, package):
    before = run(world, package)
    world["actor_assertion"]["actor_label"] = "another_local_engineer"
    after = run(world, package)
    assert before.policy_bytes == after.policy_bytes
    assert before.projection.raw_projection_bytes == after.projection.raw_projection_bytes
    assert before.policy_trace["request_commitment"] != after.policy_trace["request_commitment"]


def test_exact_numeric_cap_valid_twin(world, package):
    entry = world["target_policy"]["costs"]["value"]["entries"][0]
    entry["cost"] = rational(10 ** 127)
    assert run(world, package).selection["selected_action_ids"] == ["aH"]
    entry["cost"] = rational(10 ** 128)
    expect_diagnostic(lambda: run(world, package), package, "NUMERIC_LIMIT_EXCEEDED")
