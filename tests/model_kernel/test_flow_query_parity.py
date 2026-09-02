"""FL-001 Slice B shared PT derivation and complete RC1 reachability."""

from datetime import timedelta

import pytest

import backend.model_kernel as kernel
import backend.model_kernel.flow_results as flow_results

from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, AUTHORITY, FLOW_A, PORT_A, PORT_B, T1, connection,
    direction_interface, flow_declaration, flow_fixture,
)


REACHABLE = (
    ("healthy", "current", "exact_current"),
    ("healthy", "superseded", "pinned_{kind}_superseded"),
    ("healthy", "withdrawn", "pinned_{kind}_withdrawn"),
    ("conflicted", "current", "{kind}_lineage_conflicted"),
    ("conflicted", "superseded", "{kind}_lineage_conflicted"),
    ("conflicted", "withdrawn", "{kind}_lineage_conflicted"),
    ("inactive", "superseded", "{kind}_lineage_inactive"),
    ("inactive", "withdrawn", "{kind}_lineage_inactive"),
)


def pt_withdrawal(target, *, seconds=10, note="withdraw support"):
    return kernel.build_record(
        kernel.PortClaimWithdrawal,
        withdraws=target.record_id,
        recorded_at=T1 + timedelta(seconds=seconds),
        authority=AUTHORITY,
        note=note,
    )


def support_shape(root, health, activity, make_child):
    additions = []
    pin = root
    if (health, activity) == ("healthy", "current"):
        pass
    elif (health, activity) == ("healthy", "superseded"):
        additions.append(make_child(
            supersedes=(root.record_id,), recorded_at=T1,
            note="healthy successor"))
    elif (health, activity) == ("healthy", "withdrawn"):
        left = make_child(
            supersedes=(root.record_id,), recorded_at=T1,
            note="withdrawn fork tip")
        right = make_child(
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=1),
            note="surviving fork tip")
        additions.extend((left, right, pt_withdrawal(left)))
        pin = left
    elif (health, activity) == ("conflicted", "current"):
        left = make_child(
            supersedes=(root.record_id,), recorded_at=T1,
            note="current fork pin")
        right = make_child(
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=1),
            note="current fork peer")
        additions.extend((left, right))
        pin = left
    elif (health, activity) == ("conflicted", "superseded"):
        additions.extend((
            make_child(
                supersedes=(root.record_id,), recorded_at=T1,
                note="fork left"),
            make_child(
                supersedes=(root.record_id,),
                recorded_at=T1 + timedelta(seconds=1), note="fork right"),
        ))
    elif (health, activity) == ("conflicted", "withdrawn"):
        left = make_child(
            supersedes=(root.record_id,), recorded_at=T1,
            note="withdrawn three-way tip")
        middle = make_child(
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=1), note="survivor one")
        right = make_child(
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=2), note="survivor two")
        additions.extend((left, middle, right, pt_withdrawal(left)))
        pin = left
    elif (health, activity) == ("inactive", "superseded"):
        successor = make_child(
            supersedes=(root.record_id,), recorded_at=T1,
            note="terminal successor")
        additions.extend((successor, pt_withdrawal(successor)))
    elif (health, activity) == ("inactive", "withdrawn"):
        additions.append(pt_withdrawal(root))
    else:
        raise AssertionError("unsupported RC1 shape")
    return tuple(additions), pin


def build_parity_world(tmp_path, support_kind, health, activity):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    if support_kind == "connection":
        additions, pin = support_shape(
            pcn, health, activity,
            lambda **kwargs: connection(**kwargs))
        declaration_pcn = pin
        declaration_sources = sources
    else:
        additions, pin = support_shape(
            sources[0], health, activity,
            lambda **kwargs: direction_interface(
                PORT_A, "output", **kwargs))
        declaration_pcn = pcn
        declaration_sources = (pin,)
    declaration = flow_declaration(
        registration, port_records=ports, pcn=declaration_pcn,
        source_pifs=declaration_sources, sink_pifs=sinks,
        recorded_at=T1 + timedelta(minutes=1),
        note=f"{support_kind}-{health}-{activity}")
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, *additions, registration, declaration):
        store.append(record)
    return store.load(), declaration, pin


@pytest.mark.parametrize("support_kind", ("connection", "direction"))
@pytest.mark.parametrize("health,activity,alignment_template", REACHABLE)
def test_rc1_all_reachable_support_cells_match_public_pt_derivation(
        tmp_path, support_kind, health, activity, alignment_template):
    loaded, declaration, pin = build_parity_world(
        tmp_path, support_kind, health, activity)
    queries = kernel.ModelQueries(loaded)
    result = queries.flow_declaration(FLOW_A, context=AS_DESIGNED)
    assert result.conclusion == "declared"
    group = result.effective_body_groups[0]
    support = (group.connection_support if support_kind == "connection"
               else group.source_direction_supports[0])
    assertion = queries.port_assertion(pin.record_id)
    assert support.pinned_assertion_activity == assertion.activity == activity
    assert support.pinned_lineage_health == assertion.lineage_health == health
    assert support.alignment == alignment_template.format(kind=support_kind)
    expected_summary = (
        "conflicted" if health == "conflicted" else
        "inactive" if health == "inactive" else
        "aligned" if activity == "current" else "stale")
    assert group.support_alignment_summary == expected_summary
    if support_kind == "connection":
        topology = queries.connections_exact(
            (PORT_A, PORT_B), context=AS_DESIGNED)
        assert support.exact_topology_conclusion == topology.conclusion
    else:
        direction = queries.port_interface(
            PORT_A, context=AS_DESIGNED).dimensions[1]
        assert support.direction_dimension_status == direction.status
        if health in {"conflicted", "inactive"}:
            assert support.current_direction_relation == "not_evaluated"


@pytest.mark.parametrize(
    "role,current_value,expected",
    (
        ("source", "output", "consistent"),
        ("source", "bidirectional", "consistent"),
        ("source", "input", "inconsistent"),
        ("source", "non_directional", "indeterminate"),
        ("sink", "input", "consistent"),
        ("sink", "bidirectional", "consistent"),
        ("sink", "output", "inconsistent"),
        ("sink", "non_directional", "indeterminate"),
    ),
)
def test_current_direction_relation_is_a_current_pif_comparison_only(
        tmp_path, role, current_value, expected):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    pinned = sources[0] if role == "source" else sinks[0]
    port = PORT_A if role == "source" else PORT_B
    successor = direction_interface(
        port, current_value, supersedes=(pinned.record_id,), recorded_at=T1)
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks)
    store = kernel.ModelStore(tmp_path / "model")
    for record in (*records, registration, declaration, successor):
        store.append(record)
    group = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED).effective_body_groups[0]
    row = (group.source_direction_supports[0] if role == "source"
           else group.sink_direction_supports[0])
    assert row.current_direction_relation == expected
    assert row.pinned_assertion_activity == "superseded"
    assert row.alignment == "pinned_direction_superseded"


def test_active_other_topology_cannot_mask_pin_and_summary_precedence(
        tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    pcn_left = connection(
        supersedes=(pcn.record_id,), recorded_at=T1, note="PCN fork left")
    pcn_right = connection(
        supersedes=(pcn.record_id,),
        recorded_at=T1 + timedelta(seconds=1), note="PCN fork right")
    alternate_root = connection(
        recorded_at=T1 + timedelta(seconds=2), note="active other PCN root")
    source_successor = direction_interface(
        PORT_A, "output", supersedes=(sources[0].record_id,),
        recorded_at=T1, note="terminal source PIF")
    source_withdrawal = pt_withdrawal(
        source_successor, seconds=3, note="inactive source PIF lineage")
    sink_successor = direction_interface(
        PORT_B, "input", supersedes=(sinks[0].record_id,),
        recorded_at=T1, note="current sink successor")
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn_left,
        source_pifs=sources, sink_pifs=sinks,
        recorded_at=T1 + timedelta(minutes=1), note="compound support")
    store = kernel.ModelStore(tmp_path / "compound")
    for record in (
            *records, pcn_left, pcn_right, alternate_root, source_successor,
            source_withdrawal, sink_successor, registration, declaration):
        store.append(record)
    queries = kernel.ModelQueries(store.load())
    group = queries.flow_declaration(
        FLOW_A, context=AS_DESIGNED).effective_body_groups[0]
    assert group.connection_support.exact_topology_conclusion == "asserted"
    assert group.connection_support.pinned_lineage_health == "conflicted"
    assert group.connection_support.alignment == \
        "connection_lineage_conflicted"
    assert group.source_direction_supports[0].alignment == \
        "direction_lineage_inactive"
    assert group.sink_direction_supports[0].alignment == \
        "pinned_direction_superseded"
    assert group.support_alignment_summary == "conflicted"


def test_active_other_pcn_root_does_not_hide_inactive_pinned_root(tmp_path):
    records, registration, ports, pcn, sources, sinks = flow_fixture()
    withdrawn = pt_withdrawal(pcn)
    other = connection(recorded_at=T1, note="active other root")
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=sources, sink_pifs=sinks,
        recorded_at=T1 + timedelta(minutes=1), note="inactive exact pin")
    store = kernel.ModelStore(tmp_path / "inactive-pin")
    for record in (*records, withdrawn, other, registration, declaration):
        store.append(record)
    support = kernel.ModelQueries(store.load()).flow_declaration(
        FLOW_A, context=AS_DESIGNED).effective_body_groups[
            0].connection_support
    assert support.exact_topology_conclusion == "asserted"
    assert support.pinned_assertion_activity == "withdrawn"
    assert support.pinned_lineage_health == "inactive"
    assert support.alignment == "connection_lineage_inactive"


def test_support_summary_function_has_exact_precedence():
    def row(alignment):
        return {"alignment": alignment}

    assert flow_results._support_summary(
        row("exact_current"), (), ()) == "aligned"
    assert flow_results._support_summary(
        row("pinned_connection_superseded"), (), ()) == "stale"
    assert flow_results._support_summary(
        row("pinned_connection_superseded"),
        (row("direction_lineage_inactive"),), ()) == "inactive"
    assert flow_results._support_summary(
        row("pinned_connection_superseded"),
        (row("direction_lineage_inactive"),),
        (row("direction_lineage_conflicted"),)) == "conflicted"
