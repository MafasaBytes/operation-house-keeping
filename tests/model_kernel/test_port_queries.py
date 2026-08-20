"""PT-001 Slice B red baseline: exact port, interface, and claim disclosure."""

from dataclasses import replace

import pytest

from backend.model_kernel import ModelQueries, ModelQueryError, ModelStore
from tests.model_kernel.builders import ENT_A, registration as entity_registration
from tests.model_kernel.test_port_records import (
    CONTEXT,
    PORT_A,
    PORT_B,
    compatibility,
    connection,
    interface,
    registration,
    withdrawal,
)


UNKNOWN_PORT = "prt_" + "9" * 32
UNKNOWN_RECORD = "pif_" + "9" * 64


def world(tmp_path, *claims, ports=(PORT_A, PORT_B)):
    store = ModelStore(tmp_path / "demo-printer")
    store.append(entity_registration(ENT_A))
    for port in ports:
        template = registration()
        store.append(registration(anchor=template.anchor.model_copy(update={
            "anchor_id": port, "display_name": f"Port {port[-1]}"})))
    for claim in claims:
        store.append(claim)
    return store


class ExplodingMapping(dict):
    def get(self, *args, **kwargs):
        raise AssertionError("query touched an index before validating input")

    def __contains__(self, key):
        raise AssertionError("query touched an index before validating input")


def test_port_distinguishes_unknown_from_registered_and_carries_revision(tmp_path):
    loaded = world(tmp_path).load()
    queries = ModelQueries(loaded)
    unknown = queries.port(UNKNOWN_PORT)
    assert unknown.status == "not_registered"
    assert unknown.port_anchor_id == UNKNOWN_PORT
    assert unknown.registration_index is None
    assert unknown.material.revision == loaded.revision

    present = queries.port(PORT_A)
    assert present.status == "registered"
    assert present.material.records[present.registration_index] == \
        loaded.port_registrations_by_anchor[PORT_A]
    assert present.material.revision is loaded.revision


def test_ports_of_entity_distinguishes_unknown_owner_from_registered_empty(
        tmp_path):
    loaded = world(tmp_path, ports=()).load()
    queries = ModelQueries(loaded)
    registered = queries.ports_of_entity(ENT_A)
    unknown = queries.ports_of_entity("ent_" + "9" * 32)
    assert registered.status == "registered" and \
        registered.port_registration_indices == ()
    assert unknown.status == "not_registered" and \
        unknown.port_registration_indices == ()
    assert registered.material.revision == unknown.material.revision == loaded.revision


def test_ports_of_entity_returns_complete_registrations_in_anchor_order(tmp_path):
    loaded = world(tmp_path, ports=(PORT_B, PORT_A)).load()
    result = ModelQueries(loaded).ports_of_entity(ENT_A)
    assert tuple(result.material.records[index].anchor.anchor_id
                 for index in result.port_registration_indices) == (
        PORT_A, PORT_B)
    assert all(result.material.records[index].record_id
               in result.material.revision.record_ids
               for index in result.port_registration_indices)


def test_port_interface_returns_all_dimensions_and_distinguishes_absence(
        tmp_path):
    loaded = world(tmp_path).load()
    queries = ModelQueries(loaded)
    absent = queries.port_interface(UNKNOWN_PORT, context=CONTEXT)
    empty = queries.port_interface(PORT_A, context=CONTEXT)
    assert absent.status == "not_registered"
    assert empty.status == "registered"
    assert tuple(item.dimension for item in absent.dimensions) == (
        "interface_domain", "direction_role", "interface_type")
    assert tuple(item.dimension for item in empty.dimensions) == (
        "interface_domain", "direction_role", "interface_type")
    assert all(item.status == "not_registered" for item in absent.dimensions)
    assert all(item.status == "not_declared" for item in empty.dimensions)
    assert all(item.declaration_index is None for item in (*absent.dimensions,
                                                            *empty.dimensions))
    assert absent.material.revision == empty.material.revision == loaded.revision


def test_port_interface_discloses_unique_conflicted_and_inactive_lifecycle(
        tmp_path):
    root = interface()
    left = interface(supersedes=(root.record_id,), note="left")
    right = interface(supersedes=(root.record_id,), note="right")
    conflicted = world(tmp_path / "conflict", root, left, right).load()
    outer = ModelQueries(conflicted).port_interface(PORT_A, context=CONTEXT)
    result = outer.dimensions[0]
    assert outer.status == "registered" and result.status == "conflicted"
    assert result.declaration_index is None
    assert tuple(outer.material.records[index]
                 for index in result.conflicting_declaration_indices) == tuple(
                     sorted((left, right), key=lambda record: record.record_id))
    assert tuple(outer.material.records[index].record_id
                 for index in result.superseded_declaration_indices) == (
                     root.record_id,)

    event = withdrawal(root.record_id)
    inactive = world(tmp_path / "inactive", root, event).load()
    outer = ModelQueries(inactive).port_interface(PORT_A, context=CONTEXT)
    result = outer.dimensions[0]
    assert result.status == "inactive"
    assert result.declaration_index is None
    assert tuple(outer.material.records[index].record_id
                 for index in result.inactive_declaration_indices) == (
                     root.record_id,)
    assert tuple(outer.material.records[index].record_id
                 for index in result.withdrawal_indices) == (event.record_id,)


@pytest.mark.parametrize("factory,kind", [
    (registration, "port_registration"),
    (interface, "port_interface_declaration"),
    (connection, "port_connection_assertion"),
])
def test_port_assertion_finds_each_pt_claim_and_discloses_exact_record(
        tmp_path, factory, kind):
    claim = factory()
    claims = () if kind == "port_registration" else (claim,)
    loaded = world(tmp_path, *claims).load()
    record_id = (loaded.port_registrations_by_anchor[PORT_A].record_id
                 if kind == "port_registration" else claim.record_id)
    result = ModelQueries(loaded).port_assertion(record_id)
    assert result.status == "found"
    assert result.material.records[result.record_index].record_id == record_id
    assert result.material.records[result.record_index].record_kind == kind
    assert result.material.revision == loaded.revision
    if kind == "port_registration":
        assert result.activity is None and result.lineage_health is None
    else:
        assert result.activity == "current"
        assert result.lineage_health == "healthy"


def test_port_assertion_not_found_is_structured(tmp_path):
    loaded = world(tmp_path).load()
    result = ModelQueries(loaded).port_assertion(UNKNOWN_RECORD)
    assert result.status == "not_found"
    assert result.record_id == UNKNOWN_RECORD
    assert result.record_index is None
    assert result.material.revision == loaded.revision


def test_port_assertion_reports_superseded_withdrawn_and_conflicted_root(
        tmp_path):
    root = connection()
    left = connection(supersedes=(root.record_id,), note="left")
    right = connection(supersedes=(root.record_id,), note="right")
    loaded = world(tmp_path / "conflict", root, left, right).load()
    root_result = ModelQueries(loaded).port_assertion(root.record_id)
    assert root_result.activity == "superseded"
    assert root_result.lineage_health == "conflicted"
    assert tuple(root_result.material.records[index].record_id
                 for index in root_result.successor_indices) == tuple(sorted(
                     (left.record_id, right.record_id)))

    current = connection(note="withdraw me")
    event = withdrawal(current.record_id)
    withdrawn = world(tmp_path / "withdrawn", current, event).load()
    result = ModelQueries(withdrawn).port_assertion(current.record_id)
    assert result.activity == "withdrawn"
    assert result.lineage_health == "inactive"
    assert tuple(result.material.records[index].record_id
                 for index in result.withdrawal_indices) == (event.record_id,)


@pytest.mark.parametrize("method,bad", [
    ("port", "prt_NOT_HEX"),
    ("ports_of_entity", "ent_NOT_HEX"),
    ("port_assertion", "pif_NOT_HEX"),
])
def test_malformed_ids_are_typed_before_index_access(tmp_path, method, bad):
    loaded = world(tmp_path).load()
    poisoned = replace(
        loaded,
        port_registrations_by_anchor=ExplodingMapping(),
        port_interface_declarations=ExplodingMapping(),
        port_connections=ExplodingMapping(),
        port_compatibility_declarations=ExplodingMapping())
    with pytest.raises(ModelQueryError):
        getattr(ModelQueries(poisoned), method)(bad)


def test_port_interface_has_exact_no_dimension_signature_and_typed_context(
        tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    with pytest.raises(TypeError):
        queries.port_interface(PORT_A, dimension="interface_domain",
                               context=CONTEXT)
    with pytest.raises(ModelQueryError):
        queries.port_interface(PORT_A, context={"kind": "bad"})
