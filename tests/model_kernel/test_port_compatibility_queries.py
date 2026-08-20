"""PT-001 Slice B red baseline for deterministic interface compatibility."""

import itertools
import json

import pytest

from backend.model_kernel import ModelQueries
from tests.model_kernel.test_port_queries import world
from tests.model_kernel.test_port_records import (
    CONTEXT,
    PORT_A,
    PORT_B,
    declaration_body,
    interface,
)
from tests.model_kernel.test_port_store import pcm_from


def pif(port, dimension, value=None, **overrides):
    return interface(
        port, dimension, declaration=declaration_body(dimension, value),
        **overrides)


def assessment(tmp_path, *claims, left=PORT_A, right=PORT_B):
    loaded = world(tmp_path, *claims).load()
    return ModelQueries(loaded).interface_compatibility(
        left, right, context=CONTEXT)


def test_compatibility_preserves_requested_roles_and_canonicalizes_pair(tmp_path):
    result = assessment(tmp_path, left=PORT_B, right=PORT_A)
    assert result.requested_left_port_anchor_id == PORT_B
    assert result.requested_right_port_anchor_id == PORT_A
    assert result.endpoint_port_anchor_ids == (PORT_A, PORT_B)
    assert result.material.revision.record_count == 3
    assert result.context == CONTEXT


@pytest.mark.parametrize("dimension,field", [
    ("interface_domain", "domain_relation"),
    ("interface_type", "interface_type_relation"),
])
def test_token_comparison_exact_vocabularies(tmp_path, dimension, field):
    missing = assessment(tmp_path / "missing")
    assert getattr(missing, field) == "not_declared"

    equal = assessment(
        tmp_path / "equal", pif(PORT_A, dimension), pif(PORT_B, dimension))
    assert getattr(equal, field) == "token_identical"

    different = assessment(
        tmp_path / "different", pif(PORT_A, dimension),
        pif(PORT_B, dimension, declaration_body(dimension).value.model_copy(
            update={"code": "different"})))
    assert getattr(different, field) == "token_different"


@pytest.mark.parametrize("left,right,expected", [
    ("input", "input", "inadmissible"),
    ("input", "output", "admissible"),
    ("input", "bidirectional", "admissible"),
    ("input", "non_directional", "indeterminate"),
    ("output", "input", "admissible"),
    ("output", "output", "inadmissible"),
    ("output", "bidirectional", "admissible"),
    ("output", "non_directional", "indeterminate"),
    ("bidirectional", "input", "admissible"),
    ("bidirectional", "output", "admissible"),
    ("bidirectional", "bidirectional", "admissible"),
    ("bidirectional", "non_directional", "indeterminate"),
    ("non_directional", "input", "indeterminate"),
    ("non_directional", "output", "indeterminate"),
    ("non_directional", "bidirectional", "indeterminate"),
    ("non_directional", "non_directional", "not_applicable"),
])
def test_complete_symmetric_direction_table(tmp_path, left, right, expected):
    claims = (pif(PORT_A, "direction_role", left),
              pif(PORT_B, "direction_role", right))
    result = assessment(tmp_path, *claims)
    assert result.direction_relation == expected
    reversed_result = assessment(
        tmp_path / "reversed", *claims, left=PORT_B, right=PORT_A)
    assert reversed_result.direction_relation == expected


def test_missing_conflicted_and_inactive_direction_are_indeterminate(tmp_path):
    assert assessment(tmp_path / "missing").direction_relation == "indeterminate"
    root = pif(PORT_A, "direction_role", "input")
    left = pif(PORT_A, "direction_role", "output",
               supersedes=(root.record_id,), note="left")
    right = pif(PORT_A, "direction_role", "bidirectional",
                supersedes=(root.record_id,), note="right")
    conflict = assessment(tmp_path / "conflict", root, left, right,
                          pif(PORT_B, "direction_role", "input"))
    assert conflict.direction_relation == "indeterminate"
    assert conflict.left_interface.dimensions[1].status == "conflicted"


def test_explicit_status_not_declared_unique_conflicted_inactive_and_stale(
        tmp_path):
    pifs = (pif(PORT_A, "interface_domain"),
            pif(PORT_B, "interface_domain"))
    assert assessment(tmp_path / "none", *pifs).explicit_status == "not_declared"
    pcm = pcm_from(pifs)
    unique = assessment(tmp_path / "unique", *pifs, pcm)
    assert unique.explicit_status == "declared_compatible"
    assert unique.material.records[unique.explicit_declaration_index] == pcm

    child_left = pcm_from(pifs, supersedes=(pcm.record_id,),
                          outcome="declared_compatible", statement="left")
    child_right = pcm_from(pifs, supersedes=(pcm.record_id,),
                           outcome="declared_incompatible", statement="right")
    conflicted = assessment(tmp_path / "conflict", *pifs, pcm,
                            child_left, child_right)
    assert conflicted.explicit_status == "conflicted"
    assert tuple(conflicted.material.records[index]
                 for index in conflicted.conflicting_explicit_declaration_indices
                 ) == tuple(sorted(
                     (child_left, child_right), key=lambda record: record.record_id))

    successor = pif(PORT_A, "interface_domain", supersedes=(pifs[0].record_id,),
                    note="citation becomes stale")
    stale = assessment(tmp_path / "stale", *pifs, pcm, successor)
    assert stale.explicit_status == "stale"
    assert stale.material.records[stale.explicit_declaration_index] == pcm
    assert tuple(stale.material.records[index].record_id
                 for index in stale.stale_citation_indices) == (
                     pifs[0].record_id,)


@pytest.mark.parametrize("outcome,direction,expected", [
    ("declared_compatible", ("output", "output"), "inconsistent"),
    ("declared_compatible", ("output", "input"), "consistent"),
    ("declared_incompatible", ("output", "output"), "consistent"),
    ("declared_incompatible", ("output", "input"), "inconsistent"),
])
def test_cross_finding_consistency_table(tmp_path, outcome, direction, expected):
    pifs = (pif(PORT_A, "direction_role", direction[0]),
            pif(PORT_B, "direction_role", direction[1]))
    pcm = pcm_from(pifs, outcome=outcome)
    assert assessment(tmp_path, *pifs, pcm).consistency == expected


def test_cross_finding_is_indeterminate_without_unique_applicable_outcome(
        tmp_path):
    assert assessment(tmp_path).consistency == "indeterminate"
    non_directional = (
        pif(PORT_A, "direction_role", "non_directional"),
        pif(PORT_B, "direction_role", "non_directional"))
    pcm = pcm_from(non_directional)
    assert assessment(tmp_path / "na", *non_directional, pcm).consistency == (
        "indeterminate")


def test_compatibility_discloses_declarations_and_evidence_once(tmp_path):
    pifs = tuple(pif(port, dimension) for port, dimension in itertools.product(
        (PORT_A, PORT_B),
        ("interface_domain", "direction_role", "interface_type")))
    pcm = pcm_from(pifs)
    result = assessment(tmp_path, *pifs, pcm)
    payload = json.loads(result.model_dump_json())
    def objects(value):
        if isinstance(value, dict):
            yield value
            for item in value.values():
                yield from objects(item)
        elif isinstance(value, list):
            for item in value:
                yield from objects(item)
    dictionaries = tuple(objects(payload))
    for record in (*pifs, pcm):
        assert sum(item.get("record_id") == record.record_id
                   for item in dictionaries) == 1
    assert len(result.material.records) == \
        result.material.revision.record_count
    assert result.material.revision.record_ids == tuple(
        sorted(result.material.revision.record_ids))
