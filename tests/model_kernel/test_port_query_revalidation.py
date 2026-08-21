"""PT-001 Slice B authoritative material/result and isolation attacks."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel import ModelQueries, ModelQueryError
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


def test_slice_b_public_result_field_sets_are_exact():
    expected = {
        kernel.ModelQueryMaterial: {"revision", "records"},
        kernel.PortResult: {"material", "port_anchor_id", "status",
                            "registration_index", "owner_registration_index"},
        kernel.EntityPortsResult: {"material", "entity_anchor_id", "status",
                                  "entity_registration_index",
                                  "port_registration_indices"},
        kernel.InterfaceDimensionResult: {
            "dimension", "status", "lineage_health",
            "lineage_record_indices", "current_tip_indices",
            "withdrawal_indices", "declaration_index",
            "conflicting_declaration_indices",
            "superseded_declaration_indices",
            "inactive_declaration_indices"},
        kernel.ConnectionRootResult: {
            "root_index", "root_record_index", "lineage_record_indices",
            "current_tip_indices", "withdrawal_indices", "lineage_health",
            "exact_endpoint_set"},
        kernel.ConnectionSubjectResult: {
            "subject_index", "endpoint_port_anchor_ids", "conclusion",
            "root_indices"},
        kernel.PortInterfaceResult: {
            "material", "port_anchor_id", "status", "context", "dimensions"},
        kernel.EndpointInterfaceResult: {
            "port_anchor_id", "status", "port_registration_index",
            "owner_registration_index", "dimensions"},
        kernel.PortAssertionResult: {
            "material", "record_id", "status", "record_index", "activity",
            "lineage_health", "root_record_index", "successor_indices",
            "withdrawal_indices"},
        kernel.ExactConnectionsResult: {
            "material", "context", "status", "roots", "subjects",
            "requested_port_anchor_ids", "unregistered_port_anchor_ids"},
        kernel.IncidentConnectionsResult: {
            "material", "context", "status", "roots", "subjects",
            "port_anchor_id", "port_status"},
        kernel.ContainingConnectionsResult: {
            "material", "context", "status", "roots", "subjects",
            "requested_port_anchor_ids", "unregistered_port_anchor_ids"},
        kernel.InterfaceCompatibilityResult: {
            "material", "requested_left_port_anchor_id",
            "requested_right_port_anchor_id", "endpoint_port_anchor_ids",
            "context", "endpoint_registration_status", "left_interface",
            "right_interface", "domain_relation", "interface_type_relation",
            "direction_relation", "explicit_status",
            "explicit_declaration_index",
            "conflicting_explicit_declaration_indices",
            "pcm_lineage_record_indices", "current_pcm_tip_indices",
            "stale_citation_indices", "consistency"},
    }
    for contract, fields in expected.items():
        assert set(contract.model_fields) == fields


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


def test_material_rejects_reordered_duplicate_and_stale_nested_records(tmp_path):
    result = ModelQueries(world(tmp_path).load()).port(PORT_A)
    mutations = (
        lambda p: p["material"].update(
            records=list(reversed(p["material"]["records"]))),
        lambda p: p["material"].update(
            records=p["material"]["records"] + p["material"]["records"][:1]),
        lambda p: p["material"]["records"][0].update(
            note="forged with stale content-derived id"),
    )
    for mutate in mutations:
        with pytest.raises(ValidationError):
            reconstruct(result, mutate)


def test_assertion_and_topology_reject_context_endpoint_and_status_forgery(
        tmp_path):
    claim = connection()
    queries = ModelQueries(world(tmp_path, claim).load())
    assertion = queries.port_assertion(claim.record_id)
    with pytest.raises(ValidationError):
        reconstruct(assertion, lambda p: p.update(activity="withdrawn"))
    topology = queries.connections_exact((PORT_A, PORT_B), context=CONTEXT)
    with pytest.raises(ValidationError):
        reconstruct(topology, lambda p: p.update(
            requested_port_anchor_ids=(PORT_A, "prt_" + "3" * 32)))
    with pytest.raises(ValidationError):
        reconstruct(topology, lambda p: p.update(context={
            "kind": "lifecycle_view", "view": "as_built"}))


def test_port_assertion_result_rejects_non_pt_record_identity(tmp_path):
    result = ModelQueries(world(tmp_path).load()).port_assertion(
        "pif_" + "9" * 64)
    payload = result.model_dump(mode="python")
    payload["record_id"] = "reg_" + "9" * 64
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)


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


@pytest.mark.parametrize("index", [-1, True, "0", 999999])
def test_material_record_lookup_rejects_invalid_indices_typed(tmp_path, index):
    material = ModelQueries(world(tmp_path).load()).port(PORT_A).material
    with pytest.raises(ModelQueryError):
        material.record_at(index)


def test_nested_context_copy_forgery_rejects_at_query_and_result_boundaries(
        tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    forged_context = CONTEXT.model_copy(update={"view": "bogus"})
    with pytest.raises(ModelQueryError):
        queries.port_interface(PORT_A, context=forged_context)
    result = queries.connections_exact((PORT_A, PORT_B), context=CONTEXT)
    hostile = result.model_copy(update={"context": forged_context})
    with pytest.raises(ValidationError):
        type(result).model_validate(hostile)


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


def test_malformed_topology_and_compatibility_inputs_precede_index_access(
        tmp_path):
    from dataclasses import replace
    from tests.model_kernel.test_port_queries import ExplodingMapping

    loaded = world(tmp_path).load()
    poisoned = replace(
        loaded,
        port_registrations_by_anchor=ExplodingMapping(),
        port_connection_ids_by_subject=ExplodingMapping(),
        port_compatibility_ids_by_key=ExplodingMapping())
    queries = ModelQueries(poisoned)
    with pytest.raises(ModelQueryError):
        queries.connections_exact((PORT_A, PORT_A), context=CONTEXT)
    with pytest.raises(ModelQueryError):
        queries.interface_compatibility(
            "prt_NOT_HEX", PORT_B, context=CONTEXT)
