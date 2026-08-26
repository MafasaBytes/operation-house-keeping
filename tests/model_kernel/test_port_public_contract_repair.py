"""Red baseline for the owner-adjudicated PT-001 Slice B public surface."""

from typing import get_args

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel import ModelQueries
from tests.model_kernel.builders import ENT_A
from tests.model_kernel.test_port_compatibility_queries import assessment
from tests.model_kernel.test_port_queries import UNKNOWN_PORT, world
from tests.model_kernel.test_port_records import CONTEXT, PORT_A, PORT_B, connection


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
