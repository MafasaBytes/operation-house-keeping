"""FL-001 Slice B positive lifecycle, support, and context disclosures."""

from datetime import timedelta

import backend.model_kernel as kernel
import pytest

from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, PORT_A, PORT_B, T0, T1, VIEW_INDEPENDENT,
    connection, direction_interface, flow_declaration, flow_fixture,
    flow_registration, flow_withdrawal,
)


def build_world(tmp_path, *, context=AS_DESIGNED, claims=(), extra=()):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture(context=context)
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, registration, *claims, *extra):
        store.append(record)
    return (store, registration, port_records, pcn, source_pifs, sink_pifs)


def basic_claim(port_records, registration, pcn, source_pifs, sink_pifs,
                **overrides):
    return flow_declaration(
        registration, port_records=port_records, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs, **overrides)


def material_index(result, record):
    return result.material.revision.record_ids.index(record.record_id)


def test_registration_lookup_is_permanent_and_role_ordered(tmp_path):
    records, registration, port_records, *_ = flow_fixture()
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration):
        store.append(record)
    result = kernel.ModelQueries(store.load()).flow(FLOW_A)
    assert result.status == "registered"
    assert result.registration == registration
    assert result.source_port_registrations == (port_records[0],)
    assert result.sink_port_registrations == (port_records[1],)
    declaration = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert declaration.conclusion == "not_declared"
    assert declaration.lineage_summary == "not_applicable"


def test_one_root_declares_exact_support_without_occurrence_claim(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    declaration = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, declaration):
        store.append(record)
    result = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert result.conclusion == "declared"
    assert result.lineage_summary == "healthy"
    assert result.agreement_findings == ("one_healthy_root",)
    assert result.current_declaration_indices == (
        material_index(result, declaration),)
    assert len(result.roots) == len(result.effective_body_groups) == 1
    group = result.effective_body_groups[0]
    assert group.connection_support.model_dump() == {
        "connection_assertion_index": material_index(result, pcn),
        "exact_topology_conclusion": "asserted",
        "pinned_assertion_activity": "current",
        "pinned_lineage_health": "healthy",
        "alignment": "exact_current",
    }
    assert tuple(row.role for row in group.source_direction_supports) == (
        "source",)
    assert tuple(row.role for row in group.sink_direction_supports) == (
        "sink",)
    assert group.source_direction_supports[0].current_direction_relation == \
        "consistent"
    assert group.sink_direction_supports[0].current_direction_relation == \
        "consistent"
    assert group.support_alignment_summary == "aligned"
    dumped = result.model_dump(mode="python")
    for forbidden in (
        "occurred", "flowing", "observed", "rate", "quantity", "cause",
        "safe", "healthy_asset", "recommended_action",
    ):
        assert forbidden not in dumped


def test_corroboration_disagreement_fork_and_inactive_conclusions(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    root_a = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs, note="a")
    root_b = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs, note="b",
        recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "corroborating")
    for record in (*records, registration, root_a, root_b):
        store.append(record)
    corroborating = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert corroborating.conclusion == "declared"
    assert corroborating.agreement_findings == (
        "corroborating_healthy_roots",)
    assert len(corroborating.roots) == 2
    assert len(corroborating.effective_body_groups) == 1

    fork_a = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs,
        supersedes=(root_a.record_id,), note="fork-a", recorded_at=T1)
    fork_b = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs,
        supersedes=(root_a.record_id,), note="fork-b",
        recorded_at=T1 + timedelta(minutes=1))
    fork_store = kernel.ModelStore(tmp_path / "fork")
    for record in (*records, registration, root_a, fork_a, fork_b):
        fork_store.append(record)
    forked = kernel.ModelQueries(fork_store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert forked.conclusion == "conflicted"
    assert forked.lineage_summary == "conflicted"
    assert forked.agreement_findings == ("same_root_conflict",)
    assert forked.roots[0].lineage_health == "conflicted"

    withdrawal = flow_withdrawal(root_a)
    inactive_store = kernel.ModelStore(tmp_path / "inactive")
    for record in (*records, registration, root_a, withdrawal):
        inactive_store.append(record)
    inactive = kernel.ModelQueries(inactive_store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert inactive.conclusion == "inactive"
    assert inactive.lineage_summary == "inactive"
    assert inactive.agreement_findings == ("inactive_roots_present",)
    assert inactive.effective_body_groups == ()
    assert inactive.current_declaration_indices == ()
    inactive_queries = kernel.ModelQueries(inactive_store.load())
    assert inactive_queries.flow(FLOW_A).status == "registered"
    event = inactive_queries.flow_assertion(withdrawal.record_id)
    assert event.lookup_status == "found"
    assert event.record == withdrawal
    assert event.activity is None
    assert event.containing_lineage_health is None
    assert event.containing_flow_conclusion is None
    assert event.containing_agreement_findings is None
    assert event.root_record is None
    assert event.successors == event.withdrawals == ()


def test_cross_root_body_disagreement_and_finding_order(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    alternate_pcn = connection(note="independent exact-subject claim",
                               recorded_at=T1)
    root_a = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs, note="a")
    root_b = basic_claim(
        port_records, registration, alternate_pcn, source_pifs, sink_pifs,
        note="b", recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, alternate_pcn, root_a, root_b):
        store.append(record)
    result = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert result.conclusion == "conflicted"
    assert result.agreement_findings == (
        "cross_root_effective_body_disagreement",)
    assert len(result.effective_body_groups) == 2


def test_stale_pins_are_not_retargeted_and_do_not_change_conclusion(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    declaration = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs)
    pcn_successor = connection(
        supersedes=(pcn.record_id,), recorded_at=T1, note="later PCN")
    source_successor = direction_interface(
        PORT_A, "input", supersedes=(source_pifs[0].record_id,),
        recorded_at=T1, note="later incompatible source direction")
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, declaration, pcn_successor,
                   source_successor):
        store.append(record)
    result = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    group = result.effective_body_groups[0]
    assert result.conclusion == "declared"
    assert group.connection_support.connection_assertion == pcn
    assert group.connection_support.pinned_assertion_activity == "superseded"
    assert group.connection_support.alignment == \
        "pinned_connection_superseded"
    source = group.source_direction_supports[0]
    assert source.direction_declaration == source_pifs[0]
    assert source.pinned_assertion_activity == "superseded"
    assert source.alignment == "pinned_direction_superseded"
    assert source.direction_dimension_status == "declared"
    assert source.current_direction_relation == "inconsistent"
    assert group.support_alignment_summary == "stale"


def test_exact_context_port_collection_and_direct_parity(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    designed = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs)
    other_pcn = connection(context=VIEW_INDEPENDENT, recorded_at=T1)
    other_sources = (direction_interface(
        PORT_A, "output", context=VIEW_INDEPENDENT, recorded_at=T1),)
    other_sinks = (direction_interface(
        PORT_B, "input", context=VIEW_INDEPENDENT, recorded_at=T1),)
    independent = basic_claim(
        port_records, registration, other_pcn, other_sources, other_sinks,
        context=VIEW_INDEPENDENT, recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, designed, other_pcn,
                   *other_sources, *other_sinks, independent):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    direct = queries.flow_declaration(FLOW_A, context=AS_DESIGNED)
    collection = queries.flows_involving_port(PORT_A, context=AS_DESIGNED)
    assert collection.status == "registered"
    assert len(collection.entries) == 1
    entry = collection.entries[0]
    assert entry.role == "source"
    direct_payload = direct.model_dump(mode="python", exclude={
        "material", "flow_anchor_id", "context", "registration_index"})
    entry_payload = entry.model_dump(mode="python", exclude={
        "entry_index", "flow_anchor_id", "flow_registration_index", "role"})
    assert entry_payload == direct_payload
    independent_collection = queries.flows_involving_port(
        PORT_A, context=VIEW_INDEPENDENT)
    assert len(independent_collection.entries) == 1
    absent_context = kernel.LifecycleViewContext(
        kind="lifecycle_view", view="as_operated")
    empty = queries.flows_involving_port(PORT_A, context=absent_context)
    assert empty.status == "registered"
    assert empty.entries == ()


def test_assertion_disclosure_separates_activity_and_containing_health(tmp_path):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture()
    root = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs)
    successor = basic_claim(
        port_records, registration, pcn, source_pifs, sink_pifs,
        supersedes=(root.record_id,), recorded_at=T1)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, root, successor):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    registration_result = queries.flow_assertion(registration.record_id)
    assert registration_result.lookup_status == "found"
    assert registration_result.activity is None
    root_result = queries.flow_assertion(root.record_id)
    assert root_result.activity == "superseded"
    assert root_result.containing_lineage_health == "healthy"
    assert root_result.containing_flow_conclusion == "declared"
    assert root_result.successors == (successor,)
    current_result = queries.flow_assertion(successor.record_id)
    assert current_result.activity == "current"
    assert current_result.containing_lineage_health == "healthy"


def test_same_root_merge_and_selective_withdrawal_restore_health(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    root = basic_claim(ports, registration, pcn, sources, sinks, note="root")
    left = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(root.record_id,), recorded_at=T1, note="left")
    right = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="right")
    merge = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(left.record_id, right.record_id),
        recorded_at=T1 + timedelta(seconds=2), note="merge")
    merged_store = kernel.ModelStore(tmp_path / "merged")
    for record in (*records, registration, root, left, right, merge):
        merged_store.append(record)
    merged = kernel.ModelQueries(merged_store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert merged.conclusion == "declared"
    assert merged.roots[0].lineage_health == "healthy"
    assert merged.current_declaration_indices == (
        material_index(merged, merge),)

    withdrawal = flow_withdrawal(left)
    selective_store = kernel.ModelStore(tmp_path / "selective")
    for record in (*records, registration, root, left, right, withdrawal):
        selective_store.append(record)
    queries = kernel.ModelQueries(selective_store.load())
    selective = queries.flow_declaration(FLOW_A, context=AS_DESIGNED)
    assert selective.conclusion == "declared"
    assert selective.roots[0].lineage_health == "healthy"
    assert selective.current_declaration_indices == (
        material_index(selective, right),)
    withdrawn = queries.flow_assertion(left.record_id)
    assert withdrawn.activity == "withdrawn"
    assert withdrawn.containing_lineage_health == "healthy"


def test_historical_replay_revives_omitted_merge_and_withdrawal(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    root = basic_claim(ports, registration, pcn, sources, sinks, note="root")
    left = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(root.record_id,), recorded_at=T1, note="left")
    right = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(root.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="right")
    merge = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(left.record_id, right.record_id),
        recorded_at=T1 + timedelta(seconds=2), note="merge")
    isolated = basic_claim(
        ports, registration, pcn, sources, sinks,
        recorded_at=T1 + timedelta(seconds=3), note="isolated")
    withdrawal = flow_withdrawal(
        isolated, recorded_at=T1 + timedelta(seconds=4))
    store = kernel.ModelStore(tmp_path / "history")
    for record in (*records, registration, root, left, right, merge,
                   isolated, withdrawal):
        store.append(record)
    membership = store.load().revision.record_ids
    before_merge = store.replay(tuple(
        item for item in membership
        if item not in {merge.record_id, withdrawal.record_id,
                        isolated.record_id}))
    forked = kernel.ModelQueries(before_merge).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert forked.conclusion == "conflicted"
    assert forked.roots[0].lineage_health == "conflicted"
    before_withdrawal = store.replay(tuple(
        item for item in membership if item != withdrawal.record_id))
    revived = kernel.ModelQueries(before_withdrawal).flow_assertion(
        isolated.record_id)
    assert revived.activity == "current"
    assert revived.containing_flow_conclusion == "declared"


def test_compound_findings_keep_exact_normative_order(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    healthy_a = basic_claim(
        ports, registration, pcn, sources, sinks, note="healthy a")
    healthy_b = basic_claim(
        ports, registration, pcn, sources, sinks,
        recorded_at=T1, note="healthy b")
    alternate_pcn = connection(
        recorded_at=T1 + timedelta(seconds=1), note="alternate body")
    different = basic_claim(
        ports, registration, alternate_pcn, sources, sinks,
        recorded_at=T1 + timedelta(seconds=2), note="different healthy")
    fork_root = basic_claim(
        ports, registration, pcn, sources, sinks,
        recorded_at=T1 + timedelta(seconds=3), note="fork root")
    fork_left = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(fork_root.record_id,),
        recorded_at=T1 + timedelta(seconds=4), note="fork left")
    fork_right = basic_claim(
        ports, registration, pcn, sources, sinks,
        supersedes=(fork_root.record_id,),
        recorded_at=T1 + timedelta(seconds=5), note="fork right")
    inactive_root = basic_claim(
        ports, registration, pcn, sources, sinks,
        recorded_at=T1 + timedelta(seconds=6), note="inactive root")
    withdrawal = flow_withdrawal(
        inactive_root, recorded_at=T1 + timedelta(seconds=7))
    store = kernel.ModelStore(tmp_path / "compound")
    for record in (
            *records, registration, alternate_pcn, healthy_a, healthy_b,
            different, fork_root, fork_left, fork_right, inactive_root,
            withdrawal):
        store.append(record)
    result = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED)
    assert result.conclusion == "conflicted"
    assert result.agreement_findings == (
        "corroborating_healthy_roots",
        "same_root_conflict",
        "cross_root_effective_body_disagreement",
        "inactive_roots_present",
    )


@pytest.mark.parametrize("shape", ("declared", "conflicted", "inactive"))
def test_port_collection_has_direct_parity_for_every_reachable_entry_shape(
        tmp_path, shape):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    root = basic_claim(ports, registration, pcn, sources, sinks, note="root")
    claims = [root]
    if shape == "conflicted":
        claims.extend((
            basic_claim(
                ports, registration, pcn, sources, sinks,
                supersedes=(root.record_id,), recorded_at=T1, note="left"),
            basic_claim(
                ports, registration, pcn, sources, sinks,
                supersedes=(root.record_id,),
                recorded_at=T1 + timedelta(seconds=1), note="right"),
        ))
    elif shape == "inactive":
        claims.append(flow_withdrawal(root))
    store = kernel.ModelStore(tmp_path / shape)
    for record in (*records, registration, *claims):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    direct = queries.flow_declaration(FLOW_A, context=AS_DESIGNED)
    entry = queries.flows_involving_port(
        PORT_A, context=AS_DESIGNED).entries[0]
    assert entry.conclusion == shape
    assert entry.model_dump(mode="python", exclude={
        "entry_index", "flow_anchor_id", "flow_registration_index", "role",
    }) == direct.model_dump(mode="python", exclude={
        "material", "flow_anchor_id", "context", "registration_index",
    })
