"""PT-001 Slice B authoritative material/result and isolation attacks."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.model_kernel import ModelQueries
from tests.model_kernel.test_port_compatibility_queries import assessment, pif
from tests.model_kernel.test_port_queries import world
from tests.model_kernel.test_port_records import CONTEXT, PORT_A, PORT_B, connection


def reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def test_port_result_rejects_wrong_index_omitted_material_and_revision(tmp_path):
    result = ModelQueries(world(tmp_path).load()).port(PORT_A)
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p.update(registration_index=999))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["material"].update(records=()))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["material"]["revision"].update(
            record_count=p["material"]["revision"]["record_count"] + 1))


def test_interface_result_rejects_missing_reordered_duplicate_and_forged_rows(
        tmp_path):
    claims = (pif(PORT_A, "interface_domain"),
              pif(PORT_A, "direction_role", "output"),
              pif(PORT_A, "interface_type"))
    result = ModelQueries(world(tmp_path, *claims).load()).port_interface(
        PORT_A, context=CONTEXT)
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p.update(dimensions=p["dimensions"][:2]))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p.update(
            dimensions=list(reversed(p["dimensions"]))))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["dimensions"][0].update(
            status="conflicted"))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["dimensions"][0].update(
            declaration_index=p["dimensions"][1]["declaration_index"]))


def test_connectivity_result_rejects_root_substitution_and_omitted_competitor(
        tmp_path):
    root = connection()
    left = connection(supersedes=(root.record_id,), note="left")
    right = connection(supersedes=(root.record_id,), note="right")
    result = ModelQueries(world(tmp_path, root, left, right).load()
                          ).connections_exact((PORT_A, PORT_B), context=CONTEXT)
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["roots"][0].update(root_index=2))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["roots"][0].update(
            current_tip_indices=p["roots"][0]["current_tip_indices"][:1]))
    with pytest.raises(ValidationError):
        reconstruct(result, lambda p: p["roots"][0].update(
            lineage_health="healthy"))


def test_compatibility_rejects_forged_relations_status_consistency_and_citation(
        tmp_path):
    claims = (pif(PORT_A, "direction_role", "output"),
              pif(PORT_B, "direction_role", "output"))
    result = assessment(tmp_path, *claims)
    for field, value in (
        ("direction_relation", "admissible"),
        ("domain_relation", "token_identical"),
        ("explicit_status", "declared_compatible"),
        ("consistency", "consistent"),
    ):
        with pytest.raises(ValidationError):
            reconstruct(result, lambda p, f=field, v=value: p.update({f: v}))


def test_model_construct_and_model_copy_results_do_not_bypass_revalidation(
        tmp_path):
    result = ModelQueries(world(tmp_path).load()).port(PORT_A)
    forged = type(result).model_construct(
        **{**result.model_dump(), "registration_index": 999})
    copied = result.model_copy(update={"registration_index": 999})
    for hostile in (forged, copied):
        with pytest.raises(ValidationError):
            type(result).model_validate(hostile)


def test_material_serializes_every_complete_record_object_exactly_once(tmp_path):
    claim = connection()
    result = ModelQueries(world(tmp_path, claim).load()).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    payload = json.loads(result.model_dump_json())
    def dictionaries(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from dictionaries(child)
        elif isinstance(value, list):
            for child in value:
                yield from dictionaries(child)
    objects = tuple(dictionaries(payload))
    for record in result.material.records:
        assert sum(item.get("record_id") == record.record_id
                   for item in objects) == 1


def test_slice_b_adds_queries_only_no_store_module_traversal_or_upper_import():
    assert not any(path.name.startswith(("port_", "connectivity"))
                   for path in Path("backend").iterdir())
    for forbidden in ("neighbors", "paths", "reachable", "traverse_ports"):
        assert not hasattr(ModelQueries, forbidden)
    query_source = Path("backend/model_kernel/queries.py")
    tree = ast.parse(query_source.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    for name in imports:
        assert not name.startswith((
            "backend.data_sources", "backend.temporal_state",
            "backend.structural_evidence", "backend.model_state",
            "backend.constraint_evaluation"))
    text = query_source.read_text(encoding="utf-8")
    assert "ModelStore(" not in text
