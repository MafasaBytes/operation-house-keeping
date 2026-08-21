"""PT-001 Slice B red baseline for bounded hyperedge connectivity disclosure."""

import pytest

from backend.model_kernel import ModelQueries, ModelQueryError
from tests.model_kernel.test_port_queries import UNKNOWN_PORT, world
from tests.model_kernel.test_port_records import (
    CONTEXT, PORT_A, PORT_B, PORT_C, connection, withdrawal,
)


def root_ids(result):
    return tuple(result.material.records[entry.root_record_index].record_id
                 for entry in result.roots)


def test_connections_exact_matches_only_identical_canonical_hyperedge(tmp_path):
    pair = connection((PORT_A, PORT_B), note="pair")
    triple = connection((PORT_A, PORT_B, PORT_C), note="triple")
    queries = ModelQueries(world(
        tmp_path, pair, triple, ports=(PORT_A, PORT_B, PORT_C)).load())
    result = queries.connections_exact((PORT_B, PORT_A), context=CONTEXT)
    assert result.status == "asserted"
    assert result.requested_port_anchor_ids == (PORT_A, PORT_B)
    assert root_ids(result) == (pair.record_id,)
    assert triple.record_id not in result.revision.record_ids or \
        triple.record_id not in root_ids(result)


def test_connections_of_port_returns_every_incident_hyperedge_once(tmp_path):
    ab = connection((PORT_A, PORT_B), note="ab")
    abc = connection((PORT_A, PORT_B, PORT_C), note="abc")
    bc = connection((PORT_B, PORT_C), note="bc")
    result = ModelQueries(world(
        tmp_path, ab, abc, bc, ports=(PORT_A, PORT_B, PORT_C)).load()
    ).connections_of_port(PORT_A, context=CONTEXT)
    assert result.status == "asserted"
    assert result.port_anchor_id == PORT_A
    assert root_ids(result) == tuple(sorted(
        (ab.record_id, abc.record_id)))
    assert all(len(result.material.records[
        entry.root_record_index].endpoint_port_anchor_ids) in (2, 3)
               for entry in result.roots)


def test_connections_containing_requires_complete_requested_set(tmp_path):
    ab = connection((PORT_A, PORT_B), note="ab")
    abc = connection((PORT_A, PORT_B, PORT_C), note="abc")
    ac = connection((PORT_A, PORT_C), note="ac")
    result = ModelQueries(world(
        tmp_path, ab, abc, ac, ports=(PORT_A, PORT_B, PORT_C)).load()
    ).connections_containing((PORT_B, PORT_A), context=CONTEXT)
    assert result.status == "asserted"
    assert result.requested_port_anchor_ids == (PORT_A, PORT_B)
    assert root_ids(result) == tuple(sorted(
        (ab.record_id, abc.record_id)))
    assert ac.record_id not in root_ids(result)


@pytest.mark.parametrize("method,args", [
    ("connections_exact", ((PORT_A, PORT_B),)),
    ("connections_of_port", (PORT_A,)),
    ("connections_containing", ((PORT_A, PORT_B),)),
])
def test_no_lineage_is_unknown_not_absent_or_disconnected(
        tmp_path, method, args):
    result = getattr(ModelQueries(world(tmp_path).load()), method)(
        *args, context=CONTEXT)
    assert result.status == "unknown"
    assert result.roots == ()
    assert not hasattr(result, "disconnected")


def test_registered_empty_is_distinct_from_unknown_port_input(tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    registered = queries.connections_of_port(PORT_A, context=CONTEXT)
    unknown = queries.connections_of_port(UNKNOWN_PORT, context=CONTEXT)
    assert registered.port_status == "registered"
    assert unknown.port_status == "not_registered"
    assert registered.status == unknown.status == "unknown"


def test_exact_discloses_unregistered_endpoints_separately_from_unknown_claim(
        tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    registered = queries.connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    missing = queries.connections_exact(
        (PORT_A, UNKNOWN_PORT), context=CONTEXT)
    assert registered.status == missing.status == "unknown"
    assert registered.unregistered_port_anchor_ids == ()
    assert missing.unregistered_port_anchor_ids == (UNKNOWN_PORT,)


def test_root_entries_separate_corroboration_conflict_and_activity(tmp_path):
    corroborating = connection(note="other root")
    root = connection(note="forked root")
    left = connection(supersedes=(root.record_id,), note="left")
    right = connection(supersedes=(root.record_id,), note="right")
    loaded = world(tmp_path / "active", corroborating, root, left, right).load()
    result = ModelQueries(loaded).connections_exact(
        (PORT_A, PORT_B), context=CONTEXT)
    assert result.status == "asserted"
    assert tuple(entry.root_index for entry in result.roots) == tuple(
        range(len(result.roots)))
    assert root_ids(result) == tuple(sorted(
        (corroborating.record_id, root.record_id)))
    assert len(result.subjects) == 1
    assert result.subjects[0].endpoint_port_anchor_ids == (PORT_A, PORT_B)
    assert result.subjects[0].conclusion == "asserted"
    assert result.subjects[0].root_indices == (0, 1)
    fork = next(item for item in result.roots
                if result.material.records[
                    item.root_record_index].record_id == root.record_id)
    assert fork.lineage_health == "conflicted"
    assert tuple(result.material.records[index]
                 for index in fork.current_tip_indices) == tuple(sorted(
                     (left, right), key=lambda record: record.record_id))
    assert tuple(result.material.records[index]
                 for index in fork.lineage_record_indices) == tuple(sorted(
                     (root, left, right), key=lambda record: record.record_id))

    inactive_root = connection(note="inactive")
    event = withdrawal(inactive_root.record_id)
    inactive = ModelQueries(world(
        tmp_path / "inactive", inactive_root, event).load()
    ).connections_exact((PORT_A, PORT_B), context=CONTEXT)
    assert inactive.status == "inactive"
    assert inactive.roots[0].lineage_health == "inactive"
    assert inactive.roots[0].current_tip_indices == ()
    assert tuple(inactive.material.records[index]
                 for index in inactive.roots[0].withdrawal_indices) == (event,)


def test_root_and_lineage_order_ignore_append_time_file_and_authority(tmp_path):
    first = connection(note="z")
    second = connection(note="a")
    forward = ModelQueries(world(tmp_path / "forward", first, second).load()
                           ).connections_exact(
                               (PORT_A, PORT_B), context=CONTEXT)
    reverse = ModelQueries(world(tmp_path / "reverse", second, first).load()
                           ).connections_exact(
                               (PORT_B, PORT_A), context=CONTEXT)
    assert forward.model_dump() == reverse.model_dump()


@pytest.mark.parametrize("method,args", [
    ("connections_exact", ((PORT_A,),)),
    ("connections_exact", ((PORT_A, PORT_A),)),
    ("connections_of_port", ("prt_NOT_HEX",)),
    ("connections_containing", ((PORT_A, PORT_A),)),
    ("connections_containing", (tuple(
        f"prt_{index:032x}" for index in range(65)),)),
])
def test_topology_inputs_are_bounded_and_typed(tmp_path, method, args):
    with pytest.raises(ModelQueryError):
        getattr(ModelQueries(world(tmp_path).load()), method)(
            *args, context=CONTEXT)


def test_endpoint_count_is_preflighted_before_identifier_scanning(
        tmp_path, monkeypatch):
    queries = ModelQueries(world(tmp_path).load())
    calls = 0
    original = queries._require_port_anchor_id

    def counted(value):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(queries, "_require_port_anchor_id", counted)
    valid = tuple(f"prt_{index:032x}" for index in range(64))
    queries.connections_containing(valid, context=CONTEXT)
    assert calls == 64

    calls = 0
    with pytest.raises(ModelQueryError) as error:
        queries.connections_exact(valid + ("not-even-scanned",), context=CONTEXT)
    assert "MODEL_PORT_ENDPOINTS_INVALID" in str(error.value)
    assert calls == 0


def test_context_is_exact_and_never_unioned(tmp_path):
    claim = connection()
    queries = ModelQueries(world(tmp_path, claim).load())
    assert queries.connections_exact(
        (PORT_A, PORT_B), context=CONTEXT).status == "asserted"
    other = CONTEXT.model_copy(update={"view": "as_built"})
    assert queries.connections_exact(
        (PORT_A, PORT_B), context=other).status == "unknown"
