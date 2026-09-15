"""Independent graph census versus S6 preallocation lexical scan."""
import json
import pytest

from applications.bounded_decision_workflow.preflight import scan
from applications.bounded_decision_workflow import BUILD_LIMITS, WorkflowInputError
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import PACKAGE_PATH, object_bytes


def census(value, depth=1):
    children = list(value.values()) if isinstance(value, dict) else value if isinstance(value, list) else []
    parts = [census(v, depth + 1) for v in children]
    strings = ([value] if isinstance(value, str) else []) + (list(value) if isinstance(value, dict) else [])
    return {"nodes": 1 + sum(p["nodes"] for p in parts),
            "keys": (len(value) if isinstance(value, dict) else 0) + sum(p["keys"] for p in parts),
            "scalars": (not isinstance(value, (dict, list))) + sum(p["scalars"] for p in parts),
            "depth": max([depth] + [p["depth"] for p in parts]),
            "max_string_bytes": max([0] + [len(v.encode()) for v in strings] + [p["max_string_bytes"] for p in parts])}


def test_all_68_recovered_objects_agree_with_independent_census():
    p = json.loads(PACKAGE_PATH.read_bytes())
    for key in p["objects"]:
        wire = object_bytes(p, key)
        assert scan(wire) == census(json.loads(wire))


@pytest.mark.parametrize("wire,code", [
    (b'{"x":1,"x":2}', "JSON_DUPLICATE_KEY"),
    (b'{"x":1,"\\u0078":2}', "JSON_DUPLICATE_KEY"),
    (b'{"v":"\xff"}', "JSON_UTF8_INVALID"),
    (b'{"v":"\\ud800"}', "JSON_UTF8_INVALID"),
    (b'{"v":NaN}', "JSON_SYNTAX_INVALID"),
    (b'{"v":01}', "JSON_SYNTAX_INVALID"),
    (b'{"v":1,}', "JSON_SYNTAX_INVALID"),
    (b'{"v":[1,]}', "JSON_SYNTAX_INVALID"),
    (b'{}{}', "JSON_SYNTAX_INVALID"),
])
def test_hostile_lexical_forms(wire, code):
    with pytest.raises(WorkflowInputError) as e: scan(wire)
    assert e.value.diagnostic.code == code
    assert scan(b'{"v":[1]}') == census({"v": [1]})


@pytest.mark.parametrize("dimension,good,bad,code", [
    ("input_json_nodes_per_file", b'[0,0]', b'[0,0,0]', "JSON_NODE_LIMIT_EXCEEDED"),
    ("input_json_depth", b'[[0]]', b'[[[0]]]', "JSON_DEPTH_LIMIT_EXCEEDED"),
    ("input_max_string_bytes", b'"abc"', b'"abcd"', "JSON_STRING_LIMIT_EXCEEDED"),
])
def test_exact_incremental_limits(dimension, good, bad, code):
    limits = dict(BUILD_LIMITS, **{dimension: 3})
    assert scan(good, limits) == census(json.loads(good))
    with pytest.raises(WorkflowInputError) as e: scan(bad, limits)
    assert e.value.diagnostic.code == code and e.value.diagnostic.exit_code == 4


def test_long_escape_and_unicode_strings():
    for text in ['a' * 256, 'é' * 128, '\\"\n', '😀' * 64]:
        for escaped in (True, False):
            wire = json.dumps({"v": text}, ensure_ascii=escaped).encode()
            assert scan(wire) == census({"v": text})
