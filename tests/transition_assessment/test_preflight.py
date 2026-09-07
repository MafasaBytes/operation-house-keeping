"""Bounded TA-001 structural and finite-float admission tests."""

from __future__ import annotations

import importlib
import gc
import math
import sys
from datetime import UTC, datetime

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


def test_t64_t69_exact_production_byte_node_and_depth_boundaries():
    module = _preflight()
    byte_limit = module.MAXIMUM_CANONICAL_REQUEST_BYTES
    exact = "a" * (byte_limit - 2)
    admitted = module._preflight_graph(exact)
    assert admitted.canonical_bytes == byte_limit
    del exact
    gc.collect()

    plus_one = "a" * (byte_limit - 1)
    with pytest.raises(ValueError, match="byte limit"):
        module._preflight_graph(plus_one)
    del plus_one
    gc.collect()

    node_limit = module.MAXIMUM_RECONSTRUCTED_NODES
    assert module._preflight_graph([None] * (node_limit - 1)).nodes == node_limit
    with pytest.raises(ValueError, match="node limit"):
        module._preflight_graph([None] * node_limit)

    depth_limit = module.MAXIMUM_NESTING_DEPTH
    exact_depth = None
    for _ in range(depth_limit):
        exact_depth = [exact_depth]
    assert module._preflight_graph(exact_depth).maximum_depth == depth_limit
    too_deep = [exact_depth]
    with pytest.raises(ValueError, match="depth limit"):
        module._preflight_graph(too_deep)


def test_t70_t72_iterative_active_path_and_container_admission():
    module = _preflight()
    shared = [None]
    assert module._preflight_graph(
        [shared, shared], max_nodes=5,
    ).nodes == 5
    with pytest.raises(ValueError, match="node limit"):
        module._preflight_graph([shared, shared], max_nodes=4)

    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError, match="cyclic"):
        module._preflight_graph(cycle)

    previous = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(96)
        deep = None
        for _ in range(90):
            deep = [deep]
        assert module._preflight_graph(deep, max_depth=90).maximum_depth == 90
    finally:
        sys.setrecursionlimit(previous)

    class HostileList(list):
        def __iter__(self):
            raise AssertionError("hostile sequence iteration")

        def __len__(self):
            raise AssertionError("hostile sequence length")

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(HostileList([None]))

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(b"not admitted")


def test_t71_one_aggregate_budget_does_not_reset_between_siblings():
    module = _preflight()
    distributed = {"from": "a" * 8, "to": "b" * 8}
    exact = len(module._canonical_json_bytes(distributed))
    assert module._preflight_graph(
        distributed, max_bytes=exact,
    ).canonical_bytes == exact
    with pytest.raises(ValueError, match="byte limit"):
        module._preflight_graph(distributed, max_bytes=exact - 1)


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
        module._preflight_graph(2**34, max_bytes=10)
    assert calls == []


@pytest.mark.parametrize(
    "field",
    [
        "attempts_failed",
        "records_seen",
        "records_accepted",
        "retries_used",
        "intervening_failed_attempts",
        "later_empty_snapshots",
    ],
)
def test_unsuffixed_carried_count_booleans_reject_structurally(field):
    module = _preflight()
    assert module._preflight_graph({field: 0}).nodes == 2
    with pytest.raises(ValueError, match="boolean index"):
        module._preflight_graph({field: True})


def test_carried_integer_collection_booleans_reject_structurally():
    module = _preflight()
    module._preflight_graph({"levels_achieved": [0, 1]})
    with pytest.raises(ValueError, match="boolean index"):
        module._preflight_graph({"levels_achieved": [0, True]})


def test_unrecognized_context_union_arm_rejects_structurally():
    module = _preflight()
    module._preflight_graph({"context": {"kind": "view_independent"}})
    with pytest.raises(ValueError, match="union arm"):
        module._preflight_graph({"context": {"kind": "unknown_context"}})


def test_t22_t51_all_strict_integer_names_and_datetime_subclasses_fail_early():
    module = _preflight()
    assert module._STRICT_INTEGER_NAMES
    for name in module._STRICT_INTEGER_NAMES:
        assert module._preflight_graph({name: 0}).nodes == 2
        with pytest.raises(ValueError, match="boolean index"):
            module._preflight_graph({name: True})
    for name in module._STRICT_INTEGER_COLLECTION_NAMES:
        assert module._preflight_graph({name: [0]}).nodes == 3
        with pytest.raises(ValueError, match="boolean index"):
            module._preflight_graph({name: [True]})

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(datetime(2026, 9, 7, 12, 0))

    calls = []

    class HostileDatetime(datetime):
        def __getattribute__(self, name):
            calls.append(name)
            raise AssertionError("datetime subclass accessed")

    hostile = HostileDatetime(2026, 9, 7, 12, 0, tzinfo=UTC)
    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(hostile)
    assert calls == []


def test_t52_scalar_subclasses_reject_without_caller_protocols():
    module = _preflight()
    calls = []

    class HostileString(str):
        def _called(self, name):
            calls.append(name)
            raise AssertionError(name)

        def __eq__(self, other):
            return self._called("eq")

        def __hash__(self):
            return self._called("hash")

        def __iter__(self):
            return self._called("iter")

        def __len__(self):
            return self._called("len")

        def __repr__(self):
            return self._called("repr")

        def encode(self, *args, **kwargs):
            return self._called("encode")

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(HostileString("ordinary-looking"))
    assert calls == []

    class HostileInt(int):
        def bit_length(self):
            calls.append("bit_length")
            raise AssertionError("bit length")

        def __str__(self):
            calls.append("str")
            raise AssertionError("string conversion")

    with pytest.raises(ValueError, match="invalid scalar"):
        module._preflight_graph(HostileInt(1))
    assert calls == []
