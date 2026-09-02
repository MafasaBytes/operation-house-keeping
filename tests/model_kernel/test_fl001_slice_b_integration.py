"""FL-001 Slice B deterministic disposable-world integration gates."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import backend.model_kernel as kernel

from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, FLOW_B, PORT_A, PORT_B, PORT_C, PORT_D, T1,
    VIEW_INDEPENDENT, flow_declaration, flow_fixture, flow_kind,
    flow_registration,
)


EXPECTED_QUERY_DIGEST = (
    "6866cf1f06b7a83ae1a8b803506cf1a4c69459ff06c3a113e9d7b5384f6d619b")
EXPECTED_STORED_DIGEST = (
    "5e964d30e0c0e2f159ae6b6adac6672476e9f28996b5ed9732180bba6e566e16")
EXPECTED_REVISION = (
    "mrv_6d4c0a4b53eb9badb170d050267b46372e6cb96c815363fa02c5f187c322332a")


def reproduce(root: Path, *, reverse_roots: bool):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    first = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks, note="independent one")
    second = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks, recorded_at=T1,
        note="independent two")
    roots = (second, first) if reverse_roots else (first, second)
    store = kernel.ModelStore(root / "test-model")
    for record in (*records, registration, *roots):
        store.append(record)
    loaded = store.load()
    queries = kernel.ModelQueries(loaded)
    results = (
        queries.flow(FLOW_A),
        queries.flow_declaration(FLOW_A, context=AS_DESIGNED),
        queries.flows_involving_port(PORT_A, context=AS_DESIGNED),
        *(queries.flow_assertion(record.record_id)
          for record in sorted((first, second), key=lambda row: row.record_id)),
    )
    query_bytes = json.dumps(
        [result.model_dump(mode="json") for result in results],
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    stored = {
        path.name: path.read_bytes()
        for path in sorted(store.records_dir.glob("*.json"))
    }
    stored_digest = hashlib.sha256(b"".join(
        name.encode("utf-8") + b"\0" + value
        for name, value in stored.items())).hexdigest()
    return {
        "query_bytes": query_bytes,
        "query_digest": hashlib.sha256(query_bytes).hexdigest(),
        "stored": stored,
        "stored_digest": stored_digest,
        "revision": loaded.revision,
    }


def test_independent_disposable_roots_reproduce_exact_query_and_record_bytes(
        tmp_path):
    forward = reproduce(tmp_path / "forward", reverse_roots=False)
    reverse = reproduce(tmp_path / "reverse", reverse_roots=True)
    assert forward == reverse
    assert len(forward["query_bytes"]) == 47_433
    assert forward["query_digest"] == EXPECTED_QUERY_DIGEST
    assert forward["stored_digest"] == EXPECTED_STORED_DIGEST
    assert len(forward["stored"]) == forward["revision"].record_count == 9
    assert forward["revision"].revision_id == EXPECTED_REVISION


def test_disposable_reproduction_is_hash_seed_independent():
    script = r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.model_kernel.test_fl001_slice_b_integration import reproduce
with TemporaryDirectory(dir="/tmp") as temporary:
    result = reproduce(Path(temporary), reverse_roots=True)
    print(result["query_digest"])
    print(result["stored_digest"])
    print(result["revision"].revision_id)
'''
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(
            os.environ, PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE="1")
        outputs.append(subprocess.check_output(
            [sys.executable, "-c", script], text=True,
            cwd=Path.cwd(), env=environment))
    assert len(set(outputs)) == 1
    assert outputs[0].splitlines() == [
        EXPECTED_QUERY_DIGEST, EXPECTED_STORED_DIGEST, EXPECTED_REVISION]


def test_hyperedge_is_one_incident_flow_without_pairwise_expansion(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture(
        source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B, PORT_D))
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks)
    store = kernel.ModelStore(tmp_path / "hyperedge")
    for record in (*records, registration, declaration):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    for port, role in (
        (PORT_A, "source"), (PORT_C, "source"),
        (PORT_B, "sink"), (PORT_D, "sink"),
    ):
        result = queries.flows_involving_port(port, context=AS_DESIGNED)
        assert tuple((entry.flow_anchor_id, entry.role)
                     for entry in result.entries) == ((FLOW_A, role),)
        serialized = result.model_dump_json()
        assert "adjacent" not in serialized
        assert "pairwise" not in serialized


def test_pcn_membership_never_discovers_an_unregistered_flow(tmp_path):
    records, *_ = flow_fixture()
    store = kernel.ModelStore(tmp_path / "topology-only")
    for record in records:
        store.append(record)
    result = kernel.ModelQueries(store.load()).flows_involving_port(
        PORT_A, context=AS_DESIGNED)
    assert result.status == "registered"
    assert result.entries == ()


@pytest.mark.parametrize(
    "target_context",
    tuple(kernel.LifecycleViewContext(kind="lifecycle_view", view=view)
          for view in (
              "as_designed", "as_built", "as_configured", "as_operated",
              "as_maintained")) + (VIEW_INDEPENDENT,),
)
def test_every_context_arm_is_exact_and_view_independent_is_not_wildcard(
        tmp_path, target_context):
    records, registration, ports, pcn, sources, sinks = flow_fixture(
        context=target_context)
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks, context=target_context)
    store = kernel.ModelStore(tmp_path / "context")
    for record in (*records, registration, declaration):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    assert len(queries.flows_involving_port(
        PORT_A, context=target_context).entries) == 1
    other = (VIEW_INDEPENDENT if target_context != VIEW_INDEPENDENT
             else AS_DESIGNED)
    assert queries.flows_involving_port(PORT_A, context=other).entries == ()


def test_multiple_incident_flows_use_exact_anchor_then_frg_order(tmp_path):
    records, first_registration, ports, pcn, sources, sinks = flow_fixture()
    second_registration = flow_registration(
        flow_anchor_id=FLOW_B, port_records=ports,
        kind=flow_kind(code="distinct_logical_flow"))
    first = flow_declaration(
        first_registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks)
    second = flow_declaration(
        second_registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks, recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "ordered")
    for record in (*records, second_registration, first_registration,
                   second, first):
        store.append(record)
    entries = kernel.ModelQueries(store.load()).flows_involving_port(
        PORT_A, context=AS_DESIGNED).entries
    assert tuple(entry.flow_anchor_id for entry in entries) == (
        FLOW_A, FLOW_B)
    assert tuple(entry.entry_index for entry in entries) == (0, 1)
