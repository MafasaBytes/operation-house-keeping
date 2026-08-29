"""VP-001 Slice C red baseline: composition and provenance separation."""

from datetime import UTC, datetime

import pytest

from backend.model_state import ModelStateQueries, SourceSelector
from tests.model_state.helpers import (
    AS_OF, BEFORE_RECEIPT, E1, PROP_TEMP, SUBJECT,
)
from tests.model_state.vp001_slice_c_helpers import (
    CONTEXT, OTHER_CONTEXT, P_ASSOCIATED, P_CONFLICTED, P_DIFFERENT_OWNER,
    P_INACTIVE, P_NOT_DECLARED, P_UNKNOWN, V_UNKNOWN, slice_c_world,
)
from tests.model_state.helpers import V1


def _call(queries, port, *, context=CONTEXT, as_of=AS_OF,
          entity_anchor_id=E1, source=None, variable=V1):
    return queries.associated_port_variable_state(
        variable, port, context=context, as_of=as_of,
        entity_anchor_id=entity_anchor_id, source=source)


def test_all_five_statuses_carry_one_identical_direct_state_result(tmp_path):
    world = slice_c_world(tmp_path)
    selector = SourceSelector(subject=SUBJECT, property=PROP_TEMP)
    direct = world.queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=E1, source=selector)
    expected = {
        P_UNKNOWN: "endpoint_not_admitted",
        P_NOT_DECLARED: "association_not_declared",
        P_CONFLICTED: "association_conflicted",
        P_INACTIVE: "association_inactive",
        P_ASSOCIATED: "associated",
    }
    state_dumps = []
    for port_id, status in expected.items():
        result = _call(world.queries, port_id, source=selector)
        assert result.status == status
        assert result.variable_state == direct
        assert result.variable_state.model_dump() == direct.model_dump()
        assert result.variable_state.observation_availability == "observed"
        assert result.variable_state.candidates[0].attachment == "attached"
        state_dumps.append(result.variable_state.model_dump_json())
    assert len(set(state_dumps)) == 1


def test_every_endpoint_and_owner_admission_arm_still_returns_state(tmp_path):
    world = slice_c_world(tmp_path)
    cases = (
        (V1, P_UNKNOWN, "port_not_registered"),
        (V_UNKNOWN, P_ASSOCIATED, "variable_not_registered"),
        (V_UNKNOWN, P_UNKNOWN, "both_not_registered"),
        (V1, P_DIFFERENT_OWNER, "both_registered"),
    )
    for variable, port, endpoint_status in cases:
        result = _call(world.queries, port, variable=variable,
                       entity_anchor_id=None)
        assert result.status == "endpoint_not_admitted"
        assert result.association.endpoint_status == endpoint_status
        assert result.variable_state.variable_anchor_id == variable
    different = _call(world.queries, P_DIFFERENT_OWNER)
    assert different.association.owner_alignment == "different_owners"
    assert different.association.conclusion == "not_evaluated"


def test_conflict_precedence_and_selective_withdrawal_are_model_only(tmp_path):
    world = slice_c_world(tmp_path)
    conflicted = _call(world.queries, P_CONFLICTED)
    assert conflicted.association.conclusion == "asserted"
    assert conflicted.association.lineage_summary == "conflicted"
    assert conflicted.status == "association_conflicted"

    # Replay without one fork arm: model currentness changes, while the exact
    # resolver, temporal projection, cutoff, and requested variable do not.
    membership = tuple(
        record_id for record_id in world.store.load().revision.record_ids
        if record_id != world.conflict_left.record_id)
    historical_model = world.store.replay(membership)
    historical_queries = ModelStateQueries(
        historical_model, world.resolver, world.temporal)
    repaired = _call(historical_queries, P_CONFLICTED)
    assert repaired.status == "associated"
    assert repaired.variable_state.candidates == \
        conflicted.variable_state.candidates
    assert repaired.variable_state.binding_revision == \
        conflicted.variable_state.binding_revision
    assert repaired.variable_state.model_revision == historical_model.revision


def test_context_cutoff_selector_and_requested_entity_axes_are_independent(
        tmp_path):
    world = slice_c_world(tmp_path)
    current = _call(world.queries, P_ASSOCIATED)
    other_context = _call(
        world.queries, P_ASSOCIATED, context=OTHER_CONTEXT)
    assert current.status == "associated"
    assert other_context.status == "association_not_declared"
    assert other_context.variable_state == current.variable_state

    before = _call(world.queries, P_ASSOCIATED, as_of=BEFORE_RECEIPT)
    assert before.status == "associated"
    assert before.variable_state.observation_availability == \
        "none_before_cutoff"
    late = _call(
        world.queries, P_ASSOCIATED,
        as_of=datetime(2026, 9, 15, 12, tzinfo=UTC))
    assert late.status == "associated"
    assert late.association == current.association

    selector = SourceSelector(subject=SUBJECT, property=PROP_TEMP)
    selected = _call(world.queries, P_ASSOCIATED, source=selector,
                     entity_anchor_id=None)
    assert selected.status == "associated"
    assert selected.variable_state.selection == "explicit"
    assert selected.variable_state.requested_entity_membership == \
        "not_supplied"


def test_explicit_historical_model_membership_not_cutoff_selects_association(
        tmp_path):
    world = slice_c_world(tmp_path)
    historical = world.store.replay(world.pre_association_membership)
    old_queries = ModelStateQueries(historical, world.resolver, world.temporal)
    old = _call(old_queries, P_ASSOCIATED)
    current = _call(world.queries, P_ASSOCIATED)
    assert old.status == "association_not_declared"
    assert current.status == "associated"
    assert old.as_of == current.as_of == AS_OF
    assert old.association.material.revision == historical.revision
    assert old.variable_state.model_revision == historical.revision
    assert current.variable_state.model_revision == \
        world.store.load().revision


def test_typed_input_errors_remain_model_state_errors(tmp_path):
    from backend.model_state import ModelStateQueryError

    world = slice_c_world(tmp_path)
    calls = (
        lambda: _call(world.queries, "prt_bad"),
        lambda: _call(world.queries, P_ASSOCIATED,
                      context={"kind": "lifecycle_view", "view": "future"}),
        lambda: _call(world.queries, P_ASSOCIATED,
                      as_of=datetime(2026, 8, 7, 23)),
    )
    for call in calls:
        with pytest.raises(ModelStateQueryError):
            call()
