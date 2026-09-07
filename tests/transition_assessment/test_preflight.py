"""Bounded TA-001 structural and finite-float admission tests."""

from __future__ import annotations

import importlib
import math

import pytest


def _preflight():
    return importlib.import_module("backend.transition_assessment.preflight")


@pytest.mark.parametrize(
    "value,token",
    [
        (0.0, b"0.0"),
        (-0.0, b"-0.0"),
        (1794.0, b"1794.0"),
        (1.25, b"1.25"),
        (1e-20, b"1e-20"),
        (1e20, b"1e+20"),
    ],
)
def test_exact_builtin_finite_float_tokens(value, token):
    module = _preflight()
    module._preflight_graph(value)
    assert module._canonical_json_bytes(value) == token


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_float_rejects_before_encoding(value):
    module = _preflight()
    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(value)


def test_float_subclass_rejects():
    module = _preflight()

    class HostileFloat(float):
        pass

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(HostileFloat(1.0))


def test_exact_node_depth_and_shared_occurrence_boundaries():
    module = _preflight()
    assert module._preflight_graph(None, max_depth=0).maximum_depth == 0
    assert module._preflight_graph([None, None], max_nodes=3).nodes == 3
    with pytest.raises(ValueError, match="node limit"):
        module._preflight_graph([None, None], max_nodes=2)

    depth_two = [[None]]
    assert module._preflight_graph(depth_two, max_depth=2).maximum_depth == 2
    with pytest.raises(ValueError, match="depth limit"):
        module._preflight_graph(depth_two, max_depth=1)

    shared = [None]
    with pytest.raises(ValueError, match="node limit"):
        module._preflight_graph([shared, shared], max_nodes=4)


def test_cycle_nonstring_key_and_boolean_index_reject():
    module = _preflight()
    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError, match="cyclic"):
        module._preflight_graph(cycle)
    with pytest.raises(ValueError, match="mapping key"):
        module._preflight_graph({1: "bad"})
    with pytest.raises(ValueError, match="boolean index"):
        module._preflight_graph({"candidate_index": True})


def test_byte_counter_exact_limit_and_plus_one():
    module = _preflight()
    value = {"x": "é"}
    encoded = b'{"x":"\xc3\xa9"}'
    result = module._preflight_graph(value, max_bytes=len(encoded))
    assert result.canonical_bytes == len(encoded)
    with pytest.raises(ValueError, match="byte limit"):
        module._preflight_graph(value, max_bytes=len(encoded) - 1)


def test_huge_scalar_stops_at_byte_limit_before_scanning_invalid_suffix():
    module = _preflight()
    value = "a" * 10_000 + "\ud800"
    with pytest.raises(ValueError, match="byte limit"):
        module._preflight_graph(value, max_bytes=8)


def test_oversized_mapping_stops_at_node_lower_bound_before_key_scan():
    module = _preflight()

    class HostileString(str):
        pass

    value = {"first": None, HostileString("late"): None}
    with pytest.raises(ValueError, match="node limit"):
        module._preflight_graph(value, max_nodes=1)


def test_public_constants_are_exact():
    module = _preflight()
    assert module.MAXIMUM_CANONICAL_REQUEST_BYTES == 134_217_728
    assert module.MAXIMUM_RECONSTRUCTED_NODES == 200_000
    assert module.MAXIMUM_NESTING_DEPTH == 128


def test_compact_result_cardinalities_reject_during_preflight():
    module = _preflight()
    module._preflight_graph({"condition_traces": [None] * 128})
    module._preflight_graph({"condition_trace_indices": [None] * 64})
    with pytest.raises(ValueError, match="fixed container cardinality"):
        module._preflight_graph({"condition_traces": [None] * 129})
    with pytest.raises(ValueError, match="fixed container cardinality"):
        module._preflight_graph({"condition_trace_indices": [None] * 65})


def test_definitely_oversized_integer_rejects_before_decimal_conversion(
    monkeypatch,
):
    module = _preflight()
    calls = []

    def forbidden(value):
        calls.append(value)
        raise AssertionError("decimal conversion ran after inevitable refusal")

    monkeypatch.setattr(module, "str", forbidden, raising=False)
    with pytest.raises(ValueError, match="canonical byte limit exceeded"):
        module._preflight_graph(10**10, max_bytes=10)
    assert calls == []
