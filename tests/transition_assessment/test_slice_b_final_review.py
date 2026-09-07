"""Permanent failing-before regressions from the final Slice B review."""

from __future__ import annotations

import traceback

import pytest

from backend.transition_assessment import (
    TransitionAssessmentInputError,
    assess_declared_transition_endpoints,
)

from tests.transition_assessment.helpers import build_world


def test_private_preflight_flag_cannot_admit_hidden_nested_state(tmp_path):
    import backend.transition_assessment.contracts as contracts

    request = build_world(tmp_path).request.model_copy(deep=True)
    request.policy.__dict__["hidden_cache"] = "forged"
    ambient = getattr(contracts, "_REQUEST_ALREADY_PREFLIGHTED", None)
    token = None if ambient is None else ambient.set(True)
    try:
        with pytest.raises(TransitionAssessmentInputError):
            assess_declared_transition_endpoints(request)
    finally:
        if ambient is not None:
            ambient.reset(token)


def test_typed_input_error_retains_no_raw_exception_or_secret(tmp_path):
    request = build_world(tmp_path).request.model_dump(
        mode="python", warnings=False,
    )
    secret = "password=TOPSECRET"
    request["transition_anchor_id"] = secret
    with pytest.raises(TransitionAssessmentInputError) as captured:
        assess_declared_transition_endpoints(request)
    error = captured.value
    assert error.__cause__ is None
    assert error.__context__ is None
    assert secret not in "".join(traceback.format_exception(error))


def test_each_result_owns_fresh_fixed_limits(tmp_path):
    first = assess_declared_transition_endpoints(
        build_world(tmp_path / "first").request,
    )
    first.fixed_limits.__dict__["maximum_nesting_depth"] = 1
    second = assess_declared_transition_endpoints(
        build_world(tmp_path / "second").request,
    )
    assert second.fixed_limits.maximum_nesting_depth == 128
    assert second.fixed_limits is not first.fixed_limits


def test_wrong_lower_union_arm_rejects_before_lower_validation(
    tmp_path,
):
    import backend.transition_assessment.preflight as preflight

    request = build_world(tmp_path).request.model_dump(
        mode="python", warnings=False,
    )
    predicates = []

    def visit(value):
        if type(value) is dict:
            if "predicate" in value and type(value["predicate"]) is dict:
                predicates.append(value["predicate"])
            for item in value.values():
                visit(item)
        elif type(value) in (list, tuple):
            for item in value:
                visit(item)

    visit(request)
    assert predicates
    assert preflight._preflight_graph(request).nodes > 0
    predicates[0]["kind"] = "unexpected_predicate"
    with pytest.raises(ValueError, match="union arm"):
        preflight._preflight_graph(request)
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(request)


def test_floats_in_every_fixed_integer_field_reject_without_coercion(tmp_path):
    from backend.transition_assessment import TransitionAssessmentLimits

    fields = (
        "maximum_endpoint_conditions",
        "maximum_condition_traces",
        "maximum_distinct_alignments",
        "maximum_canonical_request_bytes",
        "maximum_reconstructed_nodes",
        "maximum_nesting_depth",
    )
    valid = {
        "schema_version": "1",
        "maximum_endpoint_conditions": 64,
        "maximum_condition_traces": 128,
        "maximum_distinct_alignments": 128,
        "maximum_canonical_request_bytes": 134_217_728,
        "maximum_reconstructed_nodes": 200_000,
        "maximum_nesting_depth": 128,
    }
    for field in fields:
        forged = dict(valid)
        forged[field] = float(forged[field])
        with pytest.raises(Exception):
            TransitionAssessmentLimits.model_validate(forged)

    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    for field in fields:
        forged = result.model_dump(mode="python", warnings=False)
        forged["fixed_limits"][field] = float(forged["fixed_limits"][field])
        with pytest.raises(Exception):
            type(result).model_validate(forged)
