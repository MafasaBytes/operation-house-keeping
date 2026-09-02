"""FL-001 Slice B authoritative reconstruction and forgery rejection."""

import copy
import os
from pathlib import Path
import socket
import time

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
import backend.model_kernel.flow_results as flow_results
import backend.model_kernel.result_revalidation as result_revalidation

from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, PORT_A, PORT_B, T1, VIEW_INDEPENDENT, connection,
    direction_interface, flow_declaration, flow_fixture,
)
from tests.model_kernel.builders import ENT_B, registration as entity_registration


def results(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, declaration):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    return (
        queries.flow(FLOW_A),
        queries.flow_declaration(FLOW_A, context=AS_DESIGNED),
        queries.flows_involving_port(PORT_A, context=AS_DESIGNED),
        queries.flow_assertion(declaration.record_id),
    )


def assert_rejects(contract, payload):
    with pytest.raises(ValidationError):
        contract.model_validate(payload)


@pytest.mark.parametrize("result_position", range(4))
def test_all_outer_results_reject_reordered_or_substituted_material(
        tmp_path, result_position):
    result = results(tmp_path)[result_position]
    payload = result.model_dump(mode="python")
    reordered = copy.deepcopy(payload)
    reordered["material"]["records"] = tuple(reversed(
        reordered["material"]["records"]))
    assert_rejects(type(result), reordered)
    revision = copy.deepcopy(payload)
    revision["material"]["revision"]["revision_id"] = "mrv_" + "0" * 64
    assert_rejects(type(result), revision)


def test_complete_material_attack_matrix_rejects_before_derivation(tmp_path):
    _, declaration, *_ = results(tmp_path)
    contract = kernel.FlowDeclarationResult
    base = declaration.model_dump(mode="python")
    attacks = []

    missing = copy.deepcopy(base)
    missing["material"]["records"] = missing["material"]["records"][:-1]
    attacks.append(missing)

    duplicate = copy.deepcopy(base)
    duplicate["material"]["records"] = (
        *duplicate["material"]["records"],
        duplicate["material"]["records"][-1])
    attacks.append(duplicate)

    extra = copy.deepcopy(base)
    extra_record = entity_registration(ENT_B).model_dump(mode="python")
    extra["material"]["records"] = (
        *extra["material"]["records"], extra_record)
    attacks.append(extra)

    mixed = copy.deepcopy(base)
    mixed["material"]["revision"] = kernel.ModelStore(
        "models/demo-printer").load().revision.model_dump(mode="python")
    attacks.append(mixed)

    stale = copy.deepcopy(base)
    target = next(record for record in stale["material"]["records"]
                  if record["record_kind"] == "flow_declaration")
    target["note"] = "content changed without recomputing record id"
    attacks.append(stale)

    wrong_union = copy.deepcopy(base)
    wrong_union["material"]["records"][0]["record_kind"] = \
        "flow_registration"
    attacks.append(wrong_union)

    for attack in attacks:
        assert_rejects(contract, attack)


def test_strict_indices_reject_boolean_wrong_kind_and_out_of_range(tmp_path):
    lookup, declaration, collection, assertion = results(tmp_path)
    cases = []
    lookup_payload = lookup.model_dump(mode="python")
    lookup_payload["registration_index"] = True
    cases.append((kernel.FlowLookupResult, lookup_payload))
    root_payload = declaration.model_dump(mode="python")
    root_payload["roots"][0]["lineage_record_indices"] = (True,)
    cases.append((kernel.FlowDeclarationResult, root_payload))
    support_payload = declaration.model_dump(mode="python")
    support_payload["effective_body_groups"][0]["connection_support"][
        "connection_assertion_index"] = 10_000
    cases.append((kernel.FlowDeclarationResult, support_payload))
    direction_payload = declaration.model_dump(mode="python")
    direction_payload["effective_body_groups"][0][
        "source_direction_supports"][0]["direction_declaration_index"] = 0
    cases.append((kernel.FlowDeclarationResult, direction_payload))
    entry_payload = collection.model_dump(mode="python")
    entry_payload["entries"][0]["entry_index"] = False
    cases.append((kernel.PortFlowsResult, entry_payload))
    assertion_payload = assertion.model_dump(mode="python")
    assertion_payload["root_record_index"] = -1
    cases.append((kernel.FlowAssertionDisclosureResult, assertion_payload))
    float_payload = declaration.model_dump(mode="python")
    float_payload["effective_body_groups"][0]["current_tip_indices"] = (1.0,)
    cases.append((kernel.FlowDeclarationResult, float_payload))
    string_payload = declaration.model_dump(mode="python")
    string_payload["effective_body_groups"][0][
        "source_direction_supports"][0]["port_registration_index"] = "1"
    cases.append((kernel.FlowDeclarationResult, string_payload))
    wrong_group = declaration.model_dump(mode="python")
    wrong_group["roots"][0]["effective_body_group_indices"] = (
        wrong_group["effective_body_groups"][0]["connection_support"][
            "connection_assertion_index"],)
    cases.append((kernel.FlowDeclarationResult, wrong_group))
    for contract, payload in cases:
        assert_rejects(contract, payload)


def test_every_derived_layer_rejects_substitution(tmp_path):
    _, declaration, collection, assertion = results(tmp_path)
    mutations = (
        ("conclusion", "conflicted"),
        ("lineage_summary", "inactive"),
        ("agreement_findings", ("inactive_roots_present",)),
    )
    for field, value in mutations:
        payload = declaration.model_dump(mode="python")
        payload[field] = value
        assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    payload["roots"][0]["lineage_health"] = "inactive"
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    payload["roots"][0]["connection_support"] = payload[
        "effective_body_groups"][0]["connection_support"]
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    payload["effective_body_groups"][0]["root_record_indices"] = ()
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    payload["effective_body_groups"][0]["support_alignment_summary"] = "stale"
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    support = payload["effective_body_groups"][0]["connection_support"]
    support.update({
        "pinned_assertion_activity": "current",
        "pinned_lineage_health": "inactive",
        "alignment": "connection_lineage_inactive",
    })
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = declaration.model_dump(mode="python")
    direction = payload["effective_body_groups"][0][
        "source_direction_supports"][0]
    direction["current_direction_relation"] = "inconsistent"
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = collection.model_dump(mode="python")
    payload["entries"][0]["role"] = "sink"
    assert_rejects(kernel.PortFlowsResult, payload)
    payload = assertion.model_dump(mode="python")
    payload["activity"] = "withdrawn"
    assert_rejects(kernel.FlowAssertionDisclosureResult, payload)


def test_other_context_and_private_state_laundering_reject(tmp_path):
    _, declaration, collection, _ = results(tmp_path)
    other = {"kind": "view_independent"}
    payload = declaration.model_dump(mode="python")
    payload["context"] = other
    assert_rejects(kernel.FlowDeclarationResult, payload)
    payload = collection.model_dump(mode="python")
    payload["context"] = other
    assert_rejects(kernel.PortFlowsResult, payload)

    forged = declaration.model_copy()
    object.__setattr__(forged, "conclusion", "conflicted")
    assert_rejects(kernel.FlowDeclarationResult, forged)

    class FalseyExtras(dict):
        def __bool__(self):
            return False

    hidden = declaration.model_copy()
    object.__setattr__(hidden, "__pydantic_extra__", FalseyExtras(
        {"occurred": True}))
    assert_rejects(kernel.FlowDeclarationResult, hidden)

    constructed_payload = declaration.model_dump(mode="python")
    constructed_payload["conclusion"] = "conflicted"
    constructed = kernel.FlowDeclarationResult.model_construct(
        **constructed_payload)
    assert_rejects(kernel.FlowDeclarationResult, constructed)


def test_other_context_nested_rows_and_cross_material_instances_reject(
        tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    designed = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks)
    other_pcn = connection(context=VIEW_INDEPENDENT, recorded_at=T1)
    other_sources = (direction_interface(
        PORT_A, "output", context=VIEW_INDEPENDENT, recorded_at=T1),)
    other_sinks = (direction_interface(
        PORT_B, "input", context=VIEW_INDEPENDENT, recorded_at=T1),)
    independent = flow_declaration(
        registration, port_records=ports, pcn=other_pcn,
        source_pifs=other_sources, sink_pifs=other_sinks,
        context=VIEW_INDEPENDENT, recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "contexts")
    for record in (*records, registration, designed, other_pcn,
                   *other_sources, *other_sinks, independent):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    designed_result = queries.flows_involving_port(
        PORT_A, context=AS_DESIGNED)
    independent_result = queries.flows_involving_port(
        PORT_A, context=VIEW_INDEPENDENT)

    plain = designed_result.model_dump(mode="python")
    plain["entries"] = independent_result.model_dump(
        mode="python")["entries"]
    assert_rejects(kernel.PortFlowsResult, plain)

    instance = designed_result.model_dump(mode="python")
    instance["entries"] = (independent_result.entries[0],)
    assert_rejects(kernel.PortFlowsResult, instance)


def test_context_falsey_extra_is_rejected_at_query_boundary(tmp_path):
    lookup, *_ = results(tmp_path)
    queries = kernel.ModelQueries(lookup.material.loaded())

    class FalseyExtras(dict):
        def __bool__(self):
            return False

    context = AS_DESIGNED.model_copy()
    object.__setattr__(context, "__pydantic_extra__", FalseyExtras(
        {"fallback": "view_independent"}))
    with pytest.raises(kernel.ModelQueryError) as error:
        queries.flow_declaration(FLOW_A, context=context)
    assert error.value.error_code == "MODEL_CONTEXT_INVALID"


def test_hostile_cycle_rejects_before_nested_normalization(tmp_path):
    _, declaration, *_ = results(tmp_path)
    payload = declaration.model_dump(mode="python")
    cycle = []
    cycle.append(cycle)
    payload["roots"] = cycle
    assert_rejects(kernel.FlowDeclarationResult, payload)


def test_shared_graph_bounds_reject_excessive_depth_and_node_count():
    deeply_nested = []
    cursor = deeply_nested
    for _ in range(130):
        child = []
        cursor.append(child)
        cursor = child
    with pytest.raises(ValueError, match="maximum depth"):
        result_revalidation.inspect_supplied_graph(deeply_nested)
    many_nodes = [[] for _ in range(100_001)]
    with pytest.raises(ValueError, match="maximum size"):
        result_revalidation.inspect_supplied_graph(many_nodes)


def test_result_validation_is_store_independent(tmp_path, monkeypatch):
    values = results(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("result reconstruction touched ModelStore")

    monkeypatch.setattr(kernel.ModelStore, "load", forbidden)
    monkeypatch.setattr(kernel.ModelStore, "append", forbidden)
    for result in values:
        rebuilt = type(result).model_validate(result.model_dump(mode="python"))
        assert rebuilt.model_dump(mode="python") == result.model_dump(
            mode="python")


def test_result_validation_uses_no_ambient_io_clock_or_environment(
        tmp_path, monkeypatch):
    result = results(tmp_path)[1]
    payload = result.model_dump(mode="python")

    def forbidden(*args, **kwargs):
        raise AssertionError("result reconstruction used an ambient capability")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(os, "getenv", forbidden)
    monkeypatch.setattr(time, "time", forbidden)
    rebuilt = kernel.FlowDeclarationResult.model_validate(payload)
    assert rebuilt.model_dump(mode="python") == payload


def test_alignment_tables_reject_only_unreachable_current_inactive_pair():
    connection_expected = {
        ("healthy", "current"): "exact_current",
        ("healthy", "superseded"): "pinned_connection_superseded",
        ("healthy", "withdrawn"): "pinned_connection_withdrawn",
        ("conflicted", "current"): "connection_lineage_conflicted",
        ("conflicted", "superseded"): "connection_lineage_conflicted",
        ("conflicted", "withdrawn"): "connection_lineage_conflicted",
        ("inactive", "superseded"): "connection_lineage_inactive",
        ("inactive", "withdrawn"): "connection_lineage_inactive",
    }
    direction_expected = {
        (health, activity): value.replace("connection", "direction")
        for (health, activity), value in connection_expected.items()
    }
    for pair, expected in connection_expected.items():
        assert flow_results._connection_alignment(*pair) == expected
    for pair, expected in direction_expected.items():
        assert flow_results._direction_alignment(*pair) == expected
    with pytest.raises(ValueError):
        flow_results._connection_alignment("inactive", "current")
    with pytest.raises(ValueError):
        flow_results._direction_alignment("inactive", "current")
