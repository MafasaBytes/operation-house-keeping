"""Independent S2 expectations; the runtime never imports this oracle/package.

Frozen preparation expectations have same-author provenance. The extra arithmetic
oracle uses Decimal interval factoring, not the runtime's Fraction corner helper.
Shared inputs are the approved equation, Cartesian hard support and fixed profile.
"""

from dataclasses import asdict
from decimal import Decimal, localcontext
from itertools import product
import copy
import hashlib
import inspect
import json

import pytest

import applications.bounded_decision_workflow as workflow
from applications.bounded_decision_workflow import projection
from applications.bounded_decision_workflow import projection_profile
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    BASE_REQUEST, BASE_SNAPSHOT, UNAVAILABLE_REQUEST, UNAVAILABLE_SNAPSHOT,
    PACKAGE_PATH, object_bytes, object_value,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


@pytest.fixture(scope="module")
def package():
    return json.loads(PACKAGE_PATH.read_bytes())


@pytest.fixture
def world(package):
    return object_value(package, BASE_REQUEST)


def recommit(request):
    """Bookkeeping only; preserve all unmutated fixture bytes and valid twins."""
    def walk(v):
        if isinstance(v, dict):
            if "canonical_commitment" in v:
                v["canonical_commitment"] = hashlib.sha256(canonical(
                    {k: x for k, x in v.items() if k != "canonical_commitment"})).hexdigest()
            else:
                for x in v.values():
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(request)
    return canonical(request)


def run(world, package):
    return workflow.project_request_and_snapshot(recommit(world), object_bytes(package, BASE_SNAPSHOT))


def rational(n, d=1):
    return {"numerator": n, "denominator": d}


def set_bounds(world, key, lo, hi):
    value = world["premises"]["coordinates"][key]["value"]
    value.update(lower=rational(*lo), upper=rational(*hi))


def expect_diagnostic(call, package, code):
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call()
    expected = next(v for v in package["diagnostic_catalogue"] if v["code"] == code)
    assert asdict(exc.value.diagnostic) == expected
    assert not hasattr(exc.value, "raw_projections")


def numeric_values(result):
    return {(r["hypothesis_id"], r["action_id"]):
            None if r["raw_interval"] is None else
            tuple(r["raw_interval"][k] for k in ("lower", "upper"))
            for r in result.raw_projections}


@pytest.mark.parametrize("case_id", ["NUM-1", "UNC-1", "UNC-2"])
def test_frozen_complete_raw_examples_and_trace_summary(package, case_id):
    case = next(v for v in package["acceptance_cases"] if v["acceptance_id"] == case_id)
    variant = case["variants"][0]
    result = workflow.project_request_and_snapshot(
        object_bytes(package, variant["input"]["request_ref"]),
        object_bytes(package, variant["input"]["snapshot_ref"]))
    expected = object_value(package, variant["expected"]["result_ref"])
    assert result.raw_projections == expected["raw_projections"]
    frozen_trace = object_value(package, variant["expected"]["trace_ref"])
    assert result.raw_projections == [{k: v for k, v in row.items() if k != "target_relation"}
                                     for row in frozen_trace["projection_rows"]]
    assert result.admission.observed_value.canonical_decimal == "40"
    assert result.corner_evaluations == {"NUM-1": 8, "UNC-1": 16, "UNC-2": 0}[case_id]
    assert "selection" not in result.raw_trace


@pytest.mark.parametrize("mutation,code", [
    ("float", "REQUEST_SCHEMA_INVALID"), ("bool", "REQUEST_SCHEMA_INVALID"),
    ("reversed", "SUPPORT_MALFORMED"), ("unreduced", "SUPPORT_MALFORMED"),
    ("zero_denominator", "SUPPORT_MALFORMED"), ("negative_denominator", "SUPPORT_MALFORMED"),
    ("correlation", "PROFILE_UNSUPPORTED"), ("open", "PROFILE_UNSUPPORTED"),
    ("unit", "PROFILE_UNSUPPORTED"), ("oversized", "NUMERIC_LIMIT_EXCEEDED"),
    ("stale", "STALE_REFERENCE"), ("edition", "EDITION_MISMATCH"),
])
def test_numeric_hostile_cases_with_baseline_twin(world, package, mutation, code):
    beta = world["premises"]["coordinates"]["beta"]
    if mutation == "float": beta["value"]["lower"] = 0.2
    elif mutation == "bool": beta["value"]["lower"]["numerator"] = True
    elif mutation == "reversed": set_bounds(world, "beta", (3, 10), (1, 10))
    elif mutation == "unreduced": beta["value"]["lower"] = rational(2, 10)
    elif mutation == "zero_denominator": beta["value"]["lower"] = rational(1, 0)
    elif mutation == "negative_denominator": beta["value"]["lower"] = rational(-1, -5)
    elif mutation == "correlation": world["premises"]["support_semantics"]["value"]["basis"] = "correlated"
    elif mutation == "open": beta["value"]["endpoint_semantics"] = "open"
    elif mutation == "unit": beta["value"]["unit_role"] = "degree_celsius"
    elif mutation == "oversized": beta["value"]["upper"] = rational(10 ** 128)
    elif mutation == "stale": beta["availability"] = "stale_reference"
    elif mutation == "edition": beta["edition"] = 2
    expect_diagnostic(lambda: run(world, package), package, code)
    twin = object_value(package, BASE_REQUEST)
    assert run(twin, package).corner_evaluations == 8


@pytest.mark.parametrize("availability", ["missing", "unknown"])
@pytest.mark.parametrize("coordinate", ["A", "alpha", "beta", "gamma"])
def test_incomplete_support_never_uses_a_nominal_or_zero_multiplier(world, package, availability, coordinate):
    v = world["premises"]["coordinates"][coordinate]
    v.update(availability=availability, value=None)
    result = run(world, package)
    assert {v["raw_status"] for v in result.raw_projections} == {"unknown"}
    assert set(numeric_values(result).values()) == {None}
    assert result.corner_evaluations == 0
    assert all("P-" + coordinate in v["frontier_ids"] for v in result.raw_trace["projection_rows"])


@pytest.mark.parametrize("group,key,affected", [
    (None, "global_applicability", {"a0", "aF", "aH", "aHF"}),
    ("preconditions", "PC-isolation", {"aH", "aHF"}),
    ("preconditions", "PC-restoration", {"aF", "aHF"}),
    ("preconditions", "PC-permission", {"aF", "aH", "aHF"}),
    ("timing", "T-aH", {"aH", "aHF"}),
    ("timing", "T-aF", {"aF", "aHF"}),
    ("invariances", "I-a0", {"a0"}),
    ("invariances", "I-aH", {"aH", "aHF"}),
    ("invariances", "I-aF", {"aF", "aHF"}),
])
@pytest.mark.parametrize("state", [True, False, "missing", "unknown"])
def test_gate_states_and_nearest_true_twins(world, package, group, key, affected, state):
    v = world["premises"][key] if group is None else world["premises"][group][key]
    if isinstance(state, bool): v["value"]["status"] = state
    else: v.update(availability=state, value=None)
    result = run(world, package)
    for row in result.raw_projections:
        expected = "ready" if row["action_id"] not in affected or state is True else (
            "inapplicable" if state is False else "unknown")
        assert row["raw_status"] == expected
    assert run(object_value(package, BASE_REQUEST), package).corner_evaluations == 8


def test_false_gate_dominates_unknown_and_structural_refusal_dominates_both(world, package):
    world["premises"]["global_applicability"]["value"]["status"] = False
    world["premises"]["coordinates"]["beta"].update(availability="unknown", value=None)
    assert {r["raw_status"] for r in run(world, package).raw_projections} == {"inapplicable"}
    world["premises"]["effects"]["E-aH"]["edition"] = 2
    expect_diagnostic(lambda: run(world, package), package, "EDITION_MISMATCH")


@pytest.mark.parametrize("effect,affected", [("E-a0", {"a0"}), ("E-aF", {"aF", "aHF"}), ("E-aH", {"aH", "aHF"})])
def test_edges_do_not_supply_missing_effect_and_staleness_is_not_unknown(world, package, effect, affected):
    v = world["premises"]["effects"][effect]
    v.update(availability="missing", value=None)
    for r in run(world, package).raw_projections:
        assert r["raw_status"] == ("unknown" if r["action_id"] in affected else "ready")
    v["availability"] = "stale_reference"
    expect_diagnostic(lambda: run(world, package), package, "STALE_REFERENCE")
    assert run(object_value(package, BASE_REQUEST), package).corner_evaluations == 8


@pytest.mark.parametrize("field", ["law", "support_semantics", "commands", "hypotheses", "actions"])
def test_missing_shared_premise_does_not_receive_a_profile_default(world, package, field):
    world["premises"][field].update(availability="unknown", value=None)
    assert {r["raw_status"] for r in run(world, package).raw_projections} == {"unknown"}


@pytest.mark.parametrize("mutation,code", [
    ("effect_sign", "PROFILE_UNSUPPORTED"), ("command_bool", "PROFILE_UNSUPPORTED"),
    ("hypothesis_mapping", "PROFILE_UNSUPPORTED"), ("duplicate_action", "CARDINALITY_INVALID"),
    ("effect_reference", "PROFILE_UNSUPPORTED"), ("premise_identity", "PROFILE_UNSUPPORTED"),
    ("effect_timing", "PROFILE_UNSUPPORTED"), ("invariance", "PROFILE_UNSUPPORTED"),
    ("authority", "PROFILE_UNSUPPORTED"),
])
def test_profile_substitutions_are_refused(world, package, mutation, code):
    p = world["premises"]
    if mutation == "effect_sign": p["effects"]["E-aF"]["value"]["assignments"]["f"] = -1
    elif mutation == "command_bool": p["commands"]["value"]["u_f"] = True
    elif mutation == "hypothesis_mapping": p["hypotheses"]["value"][0]["mapping"]["f"] = 1
    elif mutation == "duplicate_action": p["actions"]["value"][1] = copy.deepcopy(p["actions"]["value"][0])
    elif mutation == "effect_reference": p["actions"]["value"][1]["effect_ids"] = ["E-aH"]
    elif mutation == "premise_identity": p["effects"]["E-aF"]["premise_id"] = "E-aH"
    elif mutation == "effect_timing": p["effects"]["E-aF"]["value"]["timing"] = "after_step"
    elif mutation == "invariance": p["invariances"]["I-aF"]["value"]["unchanged"].remove("gamma")
    elif mutation == "authority": p["law"]["epistemic_kind"] = "application_policy"
    expect_diagnostic(lambda: run(world, package), package, code)


def decimal_oracle(world):
    """Factored interval algebra: scalar T0, independent heat/cool and beta*(T0-A).

    Unlike runtime enumeration this finds additive extrema analytically. Decimal
    input fixtures here terminate exactly and use a precision comfortably above
    their maximum possible digit count (all coordinates <= four digits).
    """
    def dec(x): return Decimal(x["numerator"]) / Decimal(x["denominator"])
    p = world["premises"]
    bounds = {k: (dec(v["value"]["lower"]), dec(v["value"]["upper"]))
              for k, v in p["coordinates"].items()}
    lo_a, hi_a = bounds["A"]
    loss = [b * (Decimal(40) - a) for b in bounds["beta"] for a in (lo_a, hi_a)]
    out = {}
    for h_id in ("H_F", "H_H"):
        for a_id in ("a0", "aF", "aH", "aHF"):
            h = 1 if h_id == "H_H" else p["commands"]["value"]["u_h"]
            f = 0 if h_id == "H_F" else p["commands"]["value"]["u_f"]
            if a_id in ("aH", "aHF"): h = 0
            if a_id in ("aF", "aHF"): f = 1
            heat = [v * h for v in bounds["alpha"]]
            cool = [v * f for v in bounds["gamma"]]
            out[h_id, a_id] = (Decimal(40) + min(heat) - max(cool) - max(loss),
                               Decimal(40) + max(heat) - min(cool) - min(loss))
    return out


@pytest.mark.parametrize("bounds", [
    {"A": ((15, 1), (25, 1)), "alpha": ((8, 1), (12, 1)),
     "gamma": ((3, 1), (5, 1)), "beta": ((1, 10), (3, 10))},
    {"A": ((35, 1), (45, 1)), "alpha": ((-2, 1), (3, 1)),
     "gamma": ((-3, 1), (4, 1)), "beta": ((-1, 2), (1, 2))},
    {"A": ((20, 1), (20, 1)), "alpha": ((1, 3), (1, 3))},
])
def test_complete_cartesian_corners_and_shared_coordinate_semantics(world, package, bounds):
    for k, (lo, hi) in bounds.items(): set_bounds(world, k, lo, hi)
    result = run(world, package)
    # The nonterminating 1/3 twin is checked as exact integers below, not Decimal.
    if "alpha" in bounds and bounds["alpha"][0] == (1, 3):
        assert numeric_values(result)["H_H", "a0"] == (rational(97, 3), rational(97, 3))
        return
    with localcontext() as context:
        context.prec = 80
        expected = decimal_oracle(world)
        for key, actual in numeric_values(result).items():
            assert tuple(Decimal(v["numerator"]) / Decimal(v["denominator"]) for v in actual) == expected[key]
        trace = result.raw_trace
        def dec(v):
            return Decimal(v["numerator"]) / Decimal(v["denominator"])
        endpoint_lists = [trace["coordinate_endpoints"][k] for k in trace["coordinate_order"]]
        expected_indices = list(product(*(range(len(v)) for v in endpoint_lists)))
        for row in trace["projection_rows"]:
            assert [v["endpoint_indices"] for v in row["corners"]] == list(map(list, expected_indices))
            for corner in row["corners"]:
                T0, A, alpha, gamma, beta = [dec(v[i]) for v, i in
                                            zip(endpoint_lists, corner["endpoint_indices"])]
                h, f = row["after_effect"]["h"], row["after_effect"]["f"]
                assert dec(corner["value"]) == (1 - beta) * T0 + beta * A + alpha * h - gamma * f
    assert result.corner_evaluations == 128
    assert all(len(r["corners"]) == 16 for r in result.raw_trace["projection_rows"])


def test_target_cost_and_provenance_edits_do_not_contaminate_physics(world, package):
    baseline = run(copy.deepcopy(world), package)
    world["target_policy"]["target"]["value"]["lower"] = rational(25)
    world["target_policy"]["target"]["value"]["upper"] = rational(27)
    world["actor_assertion"]["purpose"] = "changed target and owner note"
    assert run(world, package).raw_projection_bytes == baseline.raw_projection_bytes
    # Cost contents are deliberately not interpreted by S2.
    world["target_policy"]["costs"]["basis"] = "cost-only provenance edit"
    world["target_policy"]["costs"]["value"]["entries"][2]["cost"] = rational(5)
    changed = run(world, package)
    assert changed.raw_projection_bytes == baseline.raw_projection_bytes
    assert changed.raw_trace["request_commitment"] != baseline.raw_trace["request_commitment"]
    assert changed.raw_trace["projection_rows"] == baseline.raw_trace["projection_rows"]


def test_commands_are_assumptions_and_trace_exposes_effect_sources(world, package):
    world["premises"]["commands"]["value"]["u_h"] = 1
    world["premises"]["commands"]["value"]["u_f"] = 0
    result = run(world, package)
    assert numeric_values(result)["H_F", "a0"] == (rational(46), rational(46))
    assert numeric_values(result)["H_H", "a0"] == (rational(46), rational(46))
    row = next(r for r in result.raw_trace["projection_rows"] if r["action_id"] == "aHF")
    assert row["effect_ids"] == ["E-aH", "E-aF"]
    assert row["before_effect"] == {"h": 1, "f": 0}
    assert row["after_effect"] == {"h": 0, "f": 1}
    assert "not_execution" in result.raw_trace["meaning"]


def test_unavailable_observation_and_hostile_snapshot_cannot_reach_projection(package, monkeypatch):
    result = workflow.project_request_and_snapshot(object_bytes(package, UNAVAILABLE_REQUEST),
                                                   object_bytes(package, UNAVAILABLE_SNAPSHOT))
    assert {r["raw_status"] for r in result.raw_projections} == {"unknown"}
    assert result.corner_evaluations == 0
    def forbidden(*args): raise AssertionError("projection reached before admission")
    monkeypatch.setattr(projection, "validate_profile", forbidden)
    correction = package["fixture_correction"]
    expect_diagnostic(lambda: workflow.project_request_and_snapshot(
        object_bytes(package, correction["hostile_request_sha256"]),
        object_bytes(package, correction["hostile_snapshot_sha256"])), package, "PUBLIC_RECONSTRUCTION_REFUSED")
    expect_diagnostic(lambda: workflow.project_request_and_snapshot(
        object_bytes(package, BASE_REQUEST), object_bytes(package, correction["hostile_snapshot_sha256"])),
        package, "SNAPSHOT_COMMITMENT_MISMATCH")


def test_float_schema_precedes_snapshot_commitment(world, package):
    world["premises"]["coordinates"]["beta"]["value"]["lower"] = 0.2
    world["snapshot_commitment"] = "0" * 64
    expect_diagnostic(lambda: run(world, package), package, "REQUEST_SCHEMA_INVALID")


def test_immutable_caps_and_corner_preflight_before_arithmetic(world, package, monkeypatch):
    with pytest.raises(TypeError): workflow.BUILD_LIMITS["corner_evaluations"] = 1000
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, corner_evaluations=7)
    def forbidden(*args): raise AssertionError("corner arithmetic ran before work refusal")
    monkeypatch.setattr(projection, "product", forbidden)
    with pytest.raises(workflow.WorkflowInputError) as exc: run(world, package)
    assert exc.value.diagnostic.target == "corner_evaluations"
    assert exc.value.diagnostic.exit_code == 4


@pytest.mark.parametrize("dimension", ["output_result_bytes", "output_result_nodes", "output_trace_bytes", "output_trace_rows"])
def test_output_refusals_are_bounded_and_have_valid_twins(world, package, dimension):
    valid = run(copy.deepcopy(world), package)
    actual = {"output_result_bytes": len(valid.raw_projection_bytes),
              "output_result_nodes": 121, "output_trace_bytes": len(valid.raw_trace_bytes),
              "output_trace_rows": 8}[dimension]
    if dimension == "output_result_nodes":
        def nodes(v):
            return 1 + (sum(map(nodes, v.values())) if isinstance(v, dict) else
                        sum(map(nodes, v)) if isinstance(v, list) else 0)
        actual = nodes(valid.raw_projections)
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, **{dimension: actual})
    assert run(world, package).raw_projection_bytes == valid.raw_projection_bytes
    world["requested_limits"][dimension] -= 1
    expect_diagnostic(lambda: run(world, package), package, "OUTPUT_LIMIT_EXCEEDED")


def test_numeric_limit_checks_intermediates_and_valid_twin(world, package):
    world["requested_limits"] = dict(workflow.BUILD_LIMITS, exact_rational_digits_per_integer=2)
    set_bounds(world, "alpha", (99, 1), (99, 1))
    expect_diagnostic(lambda: run(world, package), package, "NUMERIC_LIMIT_EXCEEDED")
    set_bounds(world, "alpha", (10, 1), (10, 1))
    assert run(world, package).corner_evaluations == 8


def test_build_digit_ceiling_and_negative_zero_wire(world, package):
    set_bounds(world, "alpha", (10 ** 127, 1), (10 ** 127, 1))
    assert run(world, package).corner_evaluations == 8
    set_bounds(world, "alpha", (10 ** 128, 1), (10 ** 128, 1))
    expect_diagnostic(lambda: run(world, package), package, "NUMERIC_LIMIT_EXCEEDED")
    # Lexical negative zero cannot be hidden by Python integer equality.
    wire = object_bytes(package, BASE_REQUEST).replace(b'"u_h":0', b'"u_h":-0')
    with pytest.raises(workflow.WorkflowInputError) as exc:
        workflow.project_request_and_snapshot(wire, object_bytes(package, BASE_SNAPSHOT))
    assert exc.value.diagnostic.code == "REQUEST_CANONICAL_FORM_REQUIRED"


def test_effect_observational_claim_and_omitted_premise_are_not_defaults(world, package):
    world["premises"]["effects"]["E-aH"]["value"]["execution_confirmed_by_observation"] = True
    expect_diagnostic(lambda: run(world, package), package, "PROFILE_UNSUPPORTED")
    world = object_value(package, BASE_REQUEST)
    del world["premises"]["effects"]["E-aH"]
    expect_diagnostic(lambda: run(world, package), package, "REQUEST_SCHEMA_INVALID")


def test_raw_bytes_are_deterministic_detached_and_application_isolated(world, package):
    first, second = run(copy.deepcopy(world), package), run(copy.deepcopy(world), package)
    assert first.raw_projection_bytes == second.raw_projection_bytes
    assert first.raw_trace_bytes == second.raw_trace_bytes
    first.raw_projections[0]["raw_status"] = "tampered"
    assert first.raw_projections[0]["raw_status"] == "ready"
    for module in (projection, projection_profile):
        source = inspect.getsource(module)
        assert "candidate-package" not in source
        assert "backend." not in source  # Public backend admission belongs to S1.
        assert "open(" not in source
    assert not hasattr(first, "selection")
