"""FL-001 Slice D committed synthetic flow fixture and disclosure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import TypeAdapter

import backend.model_kernel as kernel
from tests.model_kernel.fl001_slice_d_reproduction import (
    APPEND_ORDER,
    DISCLOSURE_BYTES,
    DISCLOSURE_PATH,
    DISCLOSURE_SHA256,
    FLD_ID,
    FLOW_ANCHOR_ID,
    FRG_ID,
    PREDECESSOR_AGGREGATE,
    PREDECESSOR_REVISION,
    PROPOSED_REVISION,
    candidate_records,
    load_frozen_contract,
    sha256_bytes,
    verify_authoritative_ledger,
)
from tests.model_kernel.test_demo_model import (
    CURRENT_REVISION,
    FL001_MEMBERSHIP,
    FL001_MODEL_RECORDS,
    ST001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")


def compact(result):
    return result.model_dump(mode="json", exclude={"material"})


def test_exact_two_record_append_and_canonical_stored_contract():
    frozen = load_frozen_contract()
    candidate = frozen["content"]["candidate_contract"]
    loaded = verify_authoritative_ledger("proposed")
    registration, declaration = candidate_records(frozen)

    assert CURRENT_REVISION == PROPOSED_REVISION
    assert loaded.revision.record_count == 36
    assert loaded.revision.record_ids == FL001_MEMBERSHIP
    assert set(FL001_MEMBERSHIP) - set(ST001_MEMBERSHIP) == set(APPEND_ORDER)
    assert FL001_MODEL_RECORDS == APPEND_ORDER
    assert len(loaded.flow_registrations) == 1
    assert len(loaded.flow_declarations) == 1
    assert not loaded.flow_declaration_withdrawals
    assert declaration.supersedes == ()

    for record, contract in zip((registration, declaration),
                                candidate["record_contracts"], strict=True):
        path = DEMO_MODEL / "records" / contract["stored_file"]["filename"]
        raw = path.read_bytes()
        assert loaded.records[record.record_id] == record
        assert len(raw) == contract["stored_file"]["bytes"]
        assert hashlib.sha256(raw).hexdigest() == \
            contract["stored_file"]["sha256"]
        assert raw.decode("utf-8") == contract["stored_file"]["stored_json"]


def test_authoritative_public_queries_equal_frozen_disclosure_exactly():
    frozen = load_frozen_contract()
    disclosure = json.loads(DISCLOSURE_PATH.read_bytes())
    expected = disclosure["content"]["public_queries"]
    semantics = frozen["content"]["semantic_inputs"]
    context = TypeAdapter(kernel.AssertionContext).validate_python(
        semantics["declaration"]["context"])
    other = kernel.LifecycleViewContext(
        kind="lifecycle_view", view="as_operated")
    source = semantics["registration"]["source_port_anchor_ids"][0]
    sink = semantics["registration"]["sink_port_anchor_ids"][0]
    pcn = semantics["declaration"]["connection_assertion_record_id"]
    source_pif = semantics["declaration"]["source_direction_pins"][0][
        "declaration_record_id"]
    sink_pif = semantics["declaration"]["sink_direction_pins"][0][
        "declaration_record_id"]
    queries = kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load())

    actual_final = {
        "declaration_assertion": queries.flow_assertion(
            FLD_ID).model_dump(mode="json"),
        "flow": queries.flow(FLOW_ANCHOR_ID).model_dump(mode="json"),
        "flow_declaration": queries.flow_declaration(
            FLOW_ANCHOR_ID, context=context).model_dump(mode="json"),
        "other_context_declaration": queries.flow_declaration(
            FLOW_ANCHOR_ID, context=other).model_dump(mode="json"),
        "other_context_sink_port_flows": queries.flows_involving_port(
            sink, context=other).model_dump(mode="json"),
        "other_context_source_port_flows": queries.flows_involving_port(
            source, context=other).model_dump(mode="json"),
        "registration_assertion": queries.flow_assertion(
            FRG_ID).model_dump(mode="json"),
        "sink_port_flows": queries.flows_involving_port(
            sink, context=context).model_dump(mode="json"),
        "source_port_flows": queries.flows_involving_port(
            source, context=context).model_dump(mode="json"),
    }
    actual_pt = {
        "connection_assertion": queries.port_assertion(
            pcn).model_dump(mode="json"),
        "exact_connection": queries.connections_exact(
            (source, sink), context=context).model_dump(mode="json"),
        "sink_direction_assertion": queries.port_assertion(
            sink_pif).model_dump(mode="json"),
        "sink_interface": queries.port_interface(
            sink, context=context).model_dump(mode="json"),
        "source_direction_assertion": queries.port_assertion(
            source_pif).model_dump(mode="json"),
        "source_interface": queries.port_interface(
            source, context=context).model_dump(mode="json"),
    }
    assert actual_final == expected["final_36"]
    assert actual_pt == expected["pt_support_36"]

    declaration = queries.flow_declaration(FLOW_ANCHOR_ID, context=context)
    assert declaration.conclusion == "declared"
    assert declaration.lineage_summary == "healthy"
    assert declaration.agreement_findings == ("one_healthy_root",)
    group = declaration.effective_body_groups[0]
    assert group.support_alignment_summary == "aligned"
    assert group.connection_support.exact_topology_conclusion == "asserted"
    assert group.connection_support.pinned_assertion_activity == "current"
    assert group.connection_support.pinned_lineage_health == "healthy"
    assert group.connection_support.alignment == "exact_current"
    source_support = group.source_direction_supports[0]
    sink_support = group.sink_direction_supports[0]
    assert (source_support.direction_dimension_status,
            source_support.pinned_assertion_activity,
            source_support.pinned_lineage_health,
            source_support.current_direction_relation,
            source_support.alignment) == (
                "declared", "current", "healthy", "consistent",
                "exact_current")
    assert (sink_support.direction_dimension_status,
            sink_support.pinned_assertion_activity,
            sink_support.pinned_lineage_health,
            sink_support.current_direction_relation,
            sink_support.alignment) == (
                "declared", "current", "healthy", "consistent",
                "exact_current")


def test_predecessor_34_replays_with_structured_flow_absence():
    frozen = load_frozen_contract()
    expected = json.loads(DISCLOSURE_PATH.read_bytes())["content"][
        "public_queries"]["predecessor_34_structured_absence"]
    semantics = frozen["content"]["semantic_inputs"]
    context = TypeAdapter(kernel.AssertionContext).validate_python(
        semantics["declaration"]["context"])
    source = semantics["registration"]["source_port_anchor_ids"][0]
    sink = semantics["registration"]["sink_port_anchor_ids"][0]
    store = kernel.ModelStore(DEMO_MODEL)
    historical = store.replay(ST001_MEMBERSHIP)
    queries = kernel.ModelQueries(historical)
    actual = {
        "declaration_assertion": compact(queries.flow_assertion(FLD_ID)),
        "flow": compact(queries.flow(FLOW_ANCHOR_ID)),
        "flow_declaration": compact(queries.flow_declaration(
            FLOW_ANCHOR_ID, context=context)),
        "registration_assertion": compact(queries.flow_assertion(FRG_ID)),
        "sink_port_flows": compact(queries.flows_involving_port(
            sink, context=context)),
        "source_port_flows": compact(queries.flows_involving_port(
            source, context=context)),
    }
    assert historical.revision.record_count == 34
    assert historical.revision.revision_id == PREDECESSOR_REVISION
    assert actual == expected


def test_all_explicit_historical_memberships_and_final_replay():
    frozen = load_frozen_contract()
    store = kernel.ModelStore(DEMO_MODEL)
    counts = []
    for row in frozen["content"]["predecessor"]["historical_replay"]:
        replayed = store.replay(tuple(row["membership"]))
        assert replayed.revision.record_count == row["record_count"]
        assert replayed.revision.revision_id == row["revision_id"]
        counts.append(row["record_count"])
    final = store.replay(FL001_MEMBERSHIP)
    assert counts == [9, 10, 11, 14, 16, 18, 28, 29, 32, 34]
    assert final.revision.record_count == 36
    assert final.revision.revision_id == PROPOSED_REVISION
    assert frozen["content"]["predecessor"]["aggregate_sha256"] == \
        PREDECESSOR_AGGREGATE


def test_disclosure_is_frozen_and_preserves_the_complete_truth_boundary():
    raw = DISCLOSURE_PATH.read_bytes()
    assert len(raw) == DISCLOSURE_BYTES
    assert sha256_bytes(raw) == DISCLOSURE_SHA256
    disclosure = json.loads(raw)
    text = " ".join((disclosure["disclaimer"],
                     *disclosure["warnings"]))
    for phrase in (
        "does not claim that a real printer carries material, signal, energy, "
        "or data",
        "flow is active, observed, commanded, current, continuous, or occurred",
        "anything is conserved",
        "did not create the flow",
        "does not attach or persist it as flow truth",
    ):
        assert phrase in text
    assert disclosure["content"]["scope"][
        "authoritative_append_performed"] is False
    assert "flow_occurrence" not in disclosure["content"]
