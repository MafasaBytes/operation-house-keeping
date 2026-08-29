"""VP-001 Slice C red baseline: composition and provenance separation."""

from datetime import UTC, datetime

import pytest

from backend.model_kernel import (
    ModelQueries, VariablePortAssociationWithdrawal, build_record,
)
from backend.model_state import ModelStateQueries, SourceSelector
from backend.temporal_state.contracts import TemporalStoreError
from tests.model_state.helpers import (
    AS_OF, BEFORE_RECEIPT, E1, PROP_TARGET, PROP_TEMP, SUBJECT,
)
from tests.model_state.vp001_slice_c_helpers import (
    CONTEXT, OTHER_CONTEXT, P_ASSOCIATED, P_CONFLICTED, P_DIFFERENT_OWNER,
    P_INACTIVE, P_NOT_DECLARED, P_UNKNOWN, V_UNKNOWN, _association,
    slice_c_world,
)
from tests.model_state.helpers import MODEL_AUTHORITY, RECORDED, V1


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
        assert result.association == ModelQueries(
            world.store.load()).variable_port_association(
                V1, port_id, context=CONTEXT)
        assert result.variable_state == direct
        assert result.variable_state.model_dump() == direct.model_dump()
        assert result.variable_state.observation_availability == "observed"
        assert result.variable_state.candidates[0].attachment == "attached"
        state_dumps.append(result.variable_state.model_dump_json())
    assert len(set(state_dumps)) == 1


def test_corroborating_root_precedence_is_complete_and_state_independent(
        tmp_path):
    world = slice_c_world(tmp_path)

    # A healthy independent root cannot hide a conflicted active root.
    healthy = _association(
        world.store, P_CONFLICTED, note="healthy corroborating root")
    world.store.append(healthy)

    # An inactive independent root cannot suppress a healthy active root.
    inactive = _association(
        world.store, P_ASSOCIATED, note="inactive corroborating root")
    world.store.append(inactive)
    withdrawn = build_record(
        VariablePortAssociationWithdrawal,
        withdraws=inactive.record_id,
        recorded_at=RECORDED,
        authority=MODEL_AUTHORITY,
        note="",
    )
    world.store.append(withdrawn)

    queries = ModelStateQueries(
        world.store.load(), world.resolver, world.temporal)
    conflict = _call(queries, P_CONFLICTED)
    associated = _call(queries, P_ASSOCIATED)
    assert conflict.status == "association_conflicted"
    assert {row.lineage_health for row in conflict.association.roots} == {
        "conflicted", "healthy",
    }
    assert associated.status == "associated"
    assert {row.lineage_health for row in associated.association.roots} == {
        "healthy", "inactive",
    }
    for result in (conflict, associated):
        assert result.variable_state == queries.variable_state(
            V1, as_of=AS_OF, entity_anchor_id=E1)


def test_every_status_executes_both_public_branches_and_propagates_state_error(
        tmp_path, monkeypatch):
    import backend.model_state.facade as facade

    world = slice_c_world(tmp_path)
    association_calls = []
    state_calls = []
    association_method = facade.ModelQueries.variable_port_association
    state_method = world.queries.variable_state

    def association_spy(instance, variable, port, *, context):
        association_calls.append((variable, port, context))
        return association_method(
            instance, variable, port, context=context)

    def state_spy(variable, *, as_of, entity_anchor_id=None, source=None):
        state_calls.append((variable, as_of, entity_anchor_id, source))
        return state_method(
            variable, as_of=as_of, entity_anchor_id=entity_anchor_id,
            source=source)

    monkeypatch.setattr(
        facade.ModelQueries, "variable_port_association", association_spy)
    monkeypatch.setattr(world.queries, "variable_state", state_spy)
    for port in (
            P_UNKNOWN, P_NOT_DECLARED, P_CONFLICTED, P_INACTIVE,
            P_ASSOCIATED):
        _call(world.queries, port)
    assert [row[1] for row in association_calls] == [
        P_UNKNOWN, P_NOT_DECLARED, P_CONFLICTED, P_INACTIVE, P_ASSOCIATED,
    ]
    assert len(state_calls) == 5

    failure = TemporalStoreError("TEMPORAL_STORE_UNAVAILABLE", "fixed")

    def state_failure(*args, **kwargs):
        raise failure

    monkeypatch.setattr(world.queries, "variable_state", state_failure)
    before = len(association_calls)
    with pytest.raises(TemporalStoreError) as raised:
        _call(world.queries, P_UNKNOWN)
    assert raised.value is failure
    assert len(association_calls) == before + 1


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

    # An unregistered requested variable still runs the explicit accepted
    # evidence path; the evidence remains visible in model/identity limbo.
    selector = SourceSelector(subject=SUBJECT, property=PROP_TEMP)
    limbo = _call(
        world.queries, P_ASSOCIATED, variable=V_UNKNOWN,
        entity_anchor_id=None, source=selector)
    assert limbo.status == "endpoint_not_admitted"
    assert limbo.association.endpoint_status == "variable_not_registered"
    assert limbo.variable_state.model_membership == "not_registered"
    assert limbo.variable_state.observation_availability == "observed"
    assert limbo.variable_state.candidates[0].attachment == \
        "not_attachable_resolution_mismatch"
    assert limbo.variable_state == world.queries.variable_state(
        V_UNKNOWN, as_of=AS_OF, entity_anchor_id=None, source=selector)


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
    assert current.variable_state == world.queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=E1)
    other_context = _call(
        world.queries, P_ASSOCIATED, context=OTHER_CONTEXT)
    assert current.status == "associated"
    assert other_context.status == "association_not_declared"
    assert other_context.variable_state == current.variable_state

    before = _call(world.queries, P_ASSOCIATED, as_of=BEFORE_RECEIPT)
    assert before.status == "associated"
    assert before.variable_state.observation_availability == \
        "none_before_cutoff"
    assert before.variable_state == world.queries.variable_state(
        V1, as_of=BEFORE_RECEIPT, entity_anchor_id=E1)
    late = _call(
        world.queries, P_ASSOCIATED,
        as_of=datetime(2026, 9, 15, 12, tzinfo=UTC))
    assert late.status == "associated"
    assert late.association == current.association
    assert late.variable_state == world.queries.variable_state(
        V1, as_of=datetime(2026, 9, 15, 12, tzinfo=UTC),
        entity_anchor_id=E1)

    selector = SourceSelector(subject=SUBJECT, property=PROP_TEMP)
    selected = _call(world.queries, P_ASSOCIATED, source=selector,
                     entity_anchor_id=None)
    assert selected.status == "associated"
    assert selected.variable_state.selection == "explicit"
    assert selected.variable_state.requested_entity_membership == \
        "not_supplied"
    assert selected.variable_state == world.queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=None, source=selector)

    undeclared_selector = SourceSelector(subject=SUBJECT, property=PROP_TARGET)
    undeclared = _call(
        world.queries, P_ASSOCIATED, source=undeclared_selector)
    assert undeclared.status == "associated"
    assert undeclared.association == current.association
    assert undeclared.variable_state == world.queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=E1,
        source=undeclared_selector)

    other_entity = _call(
        world.queries, P_ASSOCIATED, entity_anchor_id=("ent_" + "2" * 32))
    assert other_entity.status == "associated"
    assert other_entity.association == current.association
    assert other_entity.variable_state == world.queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=("ent_" + "2" * 32))


def test_non_utc_cutoff_is_normalized_once_for_both_disclosures(tmp_path):
    from datetime import timedelta, timezone

    world = slice_c_world(tmp_path)
    local_cutoff = AS_OF.astimezone(timezone(timedelta(hours=5, minutes=30)))
    result = _call(world.queries, P_ASSOCIATED, as_of=local_cutoff)
    assert result.as_of == AS_OF
    assert result.variable_state.as_of == AS_OF
    assert result.variable_state == world.queries.variable_state(
        V1, as_of=local_cutoff, entity_anchor_id=E1)


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
    assert old.variable_state == old_queries.variable_state(
        V1, as_of=AS_OF, entity_anchor_id=E1)
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
