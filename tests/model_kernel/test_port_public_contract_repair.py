"""Red baseline for the owner-adjudicated PT-001 Slice B public surface."""

from typing import get_args, get_type_hints

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel import ModelQueries
from tests.model_kernel.builders import ENT_A
from tests.model_kernel.test_port_compatibility_queries import assessment
from tests.model_kernel.test_port_queries import UNKNOWN_PORT, world
from tests.model_kernel.test_port_records import (
    CONTEXT, PORT_A, PORT_B, connection, interface, withdrawal,
)


NEW_RESULT_NAMES = {
    "PortLookupResult",
    "ExactConnectionSetResult",
    "PortConnectionsResult",
    "SharedConnectionsResult",
    "PortAssertionDisclosureResult",
}
SUPERSEDED_RESULT_NAMES = {
    "PortResult",
    "ExactConnectionsResult",
    "IncidentConnectionsResult",
    "ContainingConnectionsResult",
    "PortAssertionResult",
}


def reconstruct(result, **changes):
    payload = result.model_dump(mode="python")
    payload.update(changes)
    return type(result).model_validate(payload)


def test_exact_public_result_names_replace_superseded_names():
    assert NEW_RESULT_NAMES <= set(kernel.__all__)
    assert NEW_RESULT_NAMES <= set(vars(kernel))
    assert SUPERSEDED_RESULT_NAMES.isdisjoint(kernel.__all__)
    assert SUPERSEDED_RESULT_NAMES.isdisjoint(vars(kernel))


@pytest.mark.parametrize("name,values", [
    ("PortLookupStatus", ("not_registered", "registered")),
    ("EntityPortsStatus", ("owner_not_registered", "registered")),
    ("TopologyAdmissionStatus", ("endpoint_not_registered", "admitted")),
    ("TopologyConclusion", ("unknown", "asserted", "inactive")),
    ("PortConnectionsStatus", ("port_not_registered", "registered")),
    ("PortAssertionLookupStatus", ("not_found", "found")),
    ("AssertionActivity", ("current", "superseded", "withdrawn")),
    ("ContainingLineageHealth", ("healthy", "conflicted", "inactive")),
    ("CompatibilityEndpointStatus", (
        "both_registered", "left_not_registered",
        "right_not_registered", "both_not_registered")),
    ("ExplicitCompatibilityStatus", (
        "not_declared", "declared_compatible", "declared_incompatible",
        "conflicted", "inactive", "stale")),
    ("CrossFindingConsistency", (
        "consistent", "inconsistent", "indeterminate")),
])
def test_named_status_aliases_are_public_and_exact(name, values):
    assert name in kernel.__all__
    assert get_args(getattr(kernel, name)) == values


def test_repaired_result_field_sets_are_exact():
    expected = {
        "PortLookupResult": {
            "material", "port_anchor_id", "status", "registration_index",
            "owner_registration_index"},
        "ExactConnectionSetResult": {
            "material", "context", "admission_status", "conclusion",
            "roots", "subjects", "requested_port_anchor_ids",
            "unregistered_port_anchor_ids"},
        "PortConnectionsResult": {
            "material", "context", "status", "conclusion", "roots",
            "subjects", "port_anchor_id"},
        "SharedConnectionsResult": {
            "material", "context", "admission_status", "conclusion",
            "roots", "subjects", "requested_port_anchor_ids",
            "unregistered_port_anchor_ids"},
        "PortAssertionDisclosureResult": {
            "material", "record_id", "status", "record_index", "activity",
            "lineage_health", "root_record_index", "successor_indices",
            "withdrawal_indices"},
    }
    for name, fields in expected.items():
        assert set(getattr(kernel, name).model_fields) == fields


def test_entity_ports_distinguishes_unknown_owner_from_registered_empty(tmp_path):
    queries = ModelQueries(world(tmp_path, ports=()).load())
    assert queries.ports_of_entity("ent_" + "9" * 32).status == \
        "owner_not_registered"
    registered = queries.ports_of_entity(ENT_A)
    assert registered.status == "registered"
    assert registered.port_registration_indices == ()


def test_exact_admission_is_separate_from_topology_conclusion(tmp_path):
    queries = ModelQueries(world(tmp_path, ports=(PORT_A,)).load())
    rejected = queries.connections_exact((PORT_A, PORT_B), context=CONTEXT)
    assert rejected.admission_status == "endpoint_not_registered"
    assert rejected.conclusion == "unknown"
    assert rejected.roots == rejected.subjects == ()

    admitted = ModelQueries(world(tmp_path / "admitted").load()).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    assert admitted.admission_status == "admitted"
    assert admitted.conclusion == "unknown"


def test_incident_status_is_not_a_topology_conclusion(tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    unknown = queries.connections_of_port(UNKNOWN_PORT, context=CONTEXT)
    assert unknown.status == "port_not_registered"
    assert unknown.conclusion == "unknown"
    registered = queries.connections_of_port(PORT_A, context=CONTEXT)
    assert registered.status == "registered"
    assert registered.conclusion == "unknown"


def test_shared_query_uses_the_accepted_public_name(tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    assert hasattr(queries, "connections_containing")
    result = queries.connections_containing((PORT_A, PORT_B), context=CONTEXT)
    assert isinstance(result, kernel.SharedConnectionsResult)
    assert result.admission_status == "admitted"
    assert result.conclusion == "unknown"


@pytest.mark.parametrize("ports,left,right,expected", [
    ((PORT_A, PORT_B), PORT_A, PORT_B, "both_registered"),
    ((PORT_B,), PORT_A, PORT_B, "left_not_registered"),
    ((PORT_A,), PORT_A, PORT_B, "right_not_registered"),
    ((), PORT_A, PORT_B, "both_not_registered"),
])
def test_compatibility_has_one_aggregate_endpoint_status(
        tmp_path, ports, left, right, expected):
    result = assessment(tmp_path, left=left, right=right) if ports == (
        PORT_A, PORT_B) else ModelQueries(world(tmp_path, ports=ports).load(
        )).interface_compatibility(left, right, context=CONTEXT)
    assert result.endpoint_registration_status == expected


def test_assertion_disclosure_separates_lookup_status_from_activity(tmp_path):
    claim = connection()
    queries = ModelQueries(world(tmp_path, claim).load())
    found = queries.port_assertion(claim.record_id)
    assert isinstance(found, kernel.PortAssertionDisclosureResult)
    assert found.status == "found"
    assert found.activity == "current"
    missing = queries.port_assertion("pcn_" + "9" * 64)
    assert missing.status == "not_found"
    assert missing.activity is None


def test_authoritative_results_reject_forged_admission_conclusion_and_aggregate(
        tmp_path):
    exact = ModelQueries(world(tmp_path).load()).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    with pytest.raises(ValidationError):
        reconstruct(exact, admission_status="endpoint_not_registered")
    with pytest.raises(ValidationError):
        reconstruct(exact, conclusion="asserted")

    compatibility = assessment(tmp_path / "compatibility")
    with pytest.raises(ValidationError):
        reconstruct(compatibility, endpoint_registration_status="both_not_registered")


def test_every_query_has_the_exact_public_return_annotation():
    expected = {
        "port": kernel.PortLookupResult,
        "ports_of_entity": kernel.EntityPortsResult,
        "port_interface": kernel.PortInterfaceResult,
        "port_assertion": kernel.PortAssertionDisclosureResult,
        "connections_exact": kernel.ExactConnectionSetResult,
        "connections_of_port": kernel.PortConnectionsResult,
        "connections_containing": kernel.SharedConnectionsResult,
        "interface_compatibility": kernel.InterfaceCompatibilityResult,
    }
    for method, contract in expected.items():
        assert get_type_hints(getattr(ModelQueries, method))["return"] is contract


def test_exact_admission_crosses_every_reachable_conclusion(tmp_path):
    unknown = ModelQueries(world(tmp_path / "unknown").load()).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    active_claim = connection(note="active")
    asserted = ModelQueries(world(tmp_path / "asserted", active_claim).load(
        )).connections_exact((PORT_A, PORT_B), context=CONTEXT)
    inactive_claim = connection(note="inactive")
    event = withdrawal(inactive_claim.record_id)
    inactive = ModelQueries(world(
        tmp_path / "inactive", inactive_claim, event).load()
        ).connections_exact((PORT_A, PORT_B), context=CONTEXT)
    rejected = ModelQueries(world(tmp_path / "rejected").load(
        )).connections_exact((PORT_A, UNKNOWN_PORT), context=CONTEXT)

    assert [(item.admission_status, item.conclusion) for item in (
        unknown, asserted, inactive, rejected)] == [
            ("admitted", "unknown"),
            ("admitted", "asserted"),
            ("admitted", "inactive"),
            ("endpoint_not_registered", "unknown"),
        ]
    for conclusion in ("asserted", "inactive"):
        with pytest.raises(ValidationError):
            reconstruct(rejected, conclusion=conclusion)


@pytest.mark.parametrize("ports,left,right,expected", [
    ((PORT_B,), PORT_A, PORT_B, "left_not_registered"),
    ((PORT_B,), PORT_B, PORT_A, "right_not_registered"),
    ((PORT_A,), PORT_A, PORT_B, "right_not_registered"),
    ((PORT_A,), PORT_B, PORT_A, "left_not_registered"),
])
def test_compatibility_endpoint_aggregate_is_positional_in_requested_order(
        tmp_path, ports, left, right, expected):
    result = ModelQueries(world(tmp_path, ports=ports).load(
        )).interface_compatibility(left, right, context=CONTEXT)
    assert result.endpoint_registration_status == expected
    assert result.requested_left_port_anchor_id == left
    assert result.requested_right_port_anchor_id == right


def test_assertion_activity_and_containing_health_are_independent(tmp_path):
    single_root = connection(note="single root")
    single_child = connection(
        supersedes=(single_root.record_id,), note="single child")
    healthy = ModelQueries(world(
        tmp_path / "healthy", single_root, single_child).load())
    assert (healthy.port_assertion(single_root.record_id).activity,
            healthy.port_assertion(single_root.record_id).lineage_health) == (
                "superseded", "healthy")
    assert (healthy.port_assertion(single_child.record_id).activity,
            healthy.port_assertion(single_child.record_id).lineage_health) == (
                "current", "healthy")

    fork_root = connection(note="fork root")
    left = connection(supersedes=(fork_root.record_id,), note="left")
    right = connection(supersedes=(fork_root.record_id,), note="right")
    conflicted = ModelQueries(world(
        tmp_path / "conflicted", fork_root, left, right).load())
    assert (conflicted.port_assertion(fork_root.record_id).activity,
            conflicted.port_assertion(fork_root.record_id).lineage_health) == (
                "superseded", "conflicted")
    assert (conflicted.port_assertion(left.record_id).activity,
            conflicted.port_assertion(left.record_id).lineage_health) == (
                "current", "conflicted")

    event = withdrawal(left.record_id)
    withdrawn = ModelQueries(world(
        tmp_path / "withdrawn", fork_root, left, right, event).load())
    assert (withdrawn.port_assertion(left.record_id).activity,
            withdrawn.port_assertion(left.record_id).lineage_health) == (
                "withdrawn", "healthy")

    only = connection(note="only")
    only_event = withdrawal(only.record_id)
    inactive = ModelQueries(world(
        tmp_path / "fully-inactive", only, only_event).load())
    assert (inactive.port_assertion(only.record_id).activity,
            inactive.port_assertion(only.record_id).lineage_health) == (
                "withdrawn", "inactive")


def test_nested_aggregate_and_subject_forgeries_are_rejected(tmp_path):
    claim = connection()
    result = ModelQueries(world(tmp_path, claim).load()).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    payload = result.model_dump(mode="python")
    payload["subjects"][0]["conclusion"] = "inactive"
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)

    payload = result.model_dump(mode="python")
    payload["subjects"][0]["root_indices"] = ()
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)


def test_repaired_results_preserve_deterministic_root_and_subject_order(tmp_path):
    first = connection(note="first root")
    second = connection(note="second root")
    forward = ModelQueries(world(
        tmp_path / "forward", first, second).load()).connections_exact(
            (PORT_A, PORT_B), context=CONTEXT)
    reverse = ModelQueries(world(
        tmp_path / "reverse", second, first).load()).connections_exact(
            (PORT_B, PORT_A), context=CONTEXT)
    assert isinstance(forward, kernel.ExactConnectionSetResult)
    assert forward.model_dump() == reverse.model_dump()
