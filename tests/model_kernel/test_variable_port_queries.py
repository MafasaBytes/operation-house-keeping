"""VP-001 Slice B exact, reverse-collection, and lifecycle query reds."""

from pathlib import Path

import pytest

from backend.model_kernel import ModelQueries, ModelQueryError, ModelStore
from tests.model_kernel.builders import ENT_A, ENT_B
from tests.model_kernel.test_variable_port_records import (
    CONTEXT, PORT, VARIABLE, association, withdrawal,
)
from tests.model_kernel.test_variable_port_store import (
    OTHER_CONTEXT, PORT_B, VARIABLE_B, append_all, base, port_record,
)
from tests.model_kernel.builders import variable_registration


UNKNOWN_VARIABLE = "var_" + "9" * 32
UNKNOWN_PORT = "prt_" + "9" * 32


def exact(store, variable=VARIABLE, port=PORT, context=CONTEXT):
    return ModelQueries(store.load()).variable_port_association(
        variable, port, context=context)


def test_exact_four_way_endpoint_admission_and_registration_indices(tmp_path):
    worlds = {
        "both_registered": base(tmp_path / "both"),
        "variable_not_registered": base(tmp_path / "no-variable"),
        "port_not_registered": base(tmp_path / "no-port"),
        "both_not_registered": base(tmp_path / "neither"),
    }
    arguments = {
        "both_registered": (VARIABLE, PORT),
        "variable_not_registered": (UNKNOWN_VARIABLE, PORT),
        "port_not_registered": (VARIABLE, UNKNOWN_PORT),
        "both_not_registered": (UNKNOWN_VARIABLE, UNKNOWN_PORT),
    }
    for status, store in worlds.items():
        result = exact(store, *arguments[status])
        assert result.endpoint_status == status
        assert result.material.revision == store.load().revision
        if status != "both_registered":
            assert result.owner_alignment == "not_evaluated"
            assert result.conclusion == "not_evaluated"
            assert result.lineage_summary == "not_applicable"
            assert result.roots == ()


def test_same_owner_empty_is_not_declared_and_different_owner_not_evaluated(
        tmp_path):
    same = exact(base(tmp_path / "same"))
    assert same.endpoint_status == "both_registered"
    assert same.owner_alignment == "same_owner"
    assert same.conclusion == "not_declared"
    assert same.lineage_summary == "not_applicable"
    assert same.roots == ()

    different = exact(base(
        tmp_path / "different", variable_owner=ENT_A, port_owner=ENT_B))
    assert different.endpoint_status == "both_registered"
    assert different.owner_alignment == "different_owners"
    assert different.conclusion == "not_evaluated"
    assert different.lineage_summary == "not_applicable"
    assert different.roots == ()


def test_healthy_conflicted_inactive_and_corroborating_roots(tmp_path):
    root = association(note="root")
    healthy = exact(append_all(base(tmp_path / "healthy"), root))
    assert (healthy.conclusion, healthy.lineage_summary) == (
        "asserted", "healthy")
    assert len(healthy.roots) == 1

    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")
    conflict = exact(append_all(
        base(tmp_path / "conflict"), root, left, right))
    assert (conflict.conclusion, conflict.lineage_summary) == (
        "asserted", "conflicted")
    assert len(conflict.roots[0].current_tip_indices) == 2

    event = withdrawal(root.record_id)
    inactive = exact(append_all(base(tmp_path / "inactive"), root, event))
    assert (inactive.conclusion, inactive.lineage_summary) == (
        "inactive", "inactive")
    assert inactive.roots[0].current_tip_indices == ()

    other = association(note="independent corroboration")
    corroborated = exact(append_all(base(tmp_path / "roots"), root, other))
    assert (corroborated.conclusion, corroborated.lineage_summary) == (
        "asserted", "healthy")
    assert len(corroborated.roots) == 2

    selective = exact(append_all(
        base(tmp_path / "selective"), root, left, right,
        withdrawal(left.record_id)))
    assert (selective.conclusion, selective.lineage_summary) == (
        "asserted", "healthy")
    assert len(selective.roots[0].current_tip_indices) == 1


def test_context_is_exact_and_replay_currentness_is_membership_relative(tmp_path):
    root = association(note="root")
    child = association(supersedes=(root.record_id,), note="child")
    other = association(context=OTHER_CONTEXT, note="other context")
    store = append_all(base(tmp_path), root, child, other)
    assert exact(store).material.records[
        exact(store).roots[0].current_tip_indices[0]].record_id == child.record_id
    historical_ids = tuple(record_id for record_id in store.load().revision.record_ids
                           if record_id != child.record_id)
    historical = ModelQueries(store.replay(historical_ids)
                              ).variable_port_association(
                                  VARIABLE, PORT, context=CONTEXT)
    assert historical.material.records[
        historical.roots[0].current_tip_indices[0]].record_id == root.record_id
    assert len(ModelQueries(store.load()).variable_port_association(
        VARIABLE, PORT, context=OTHER_CONTEXT).roots) == 1


def test_reverse_collections_distinguish_unknown_registered_empty_and_order(
        tmp_path):
    store = base(tmp_path)
    queries = ModelQueries(store.load())
    variable_empty = queries.ports_associated_with_variable(
        VARIABLE, context=CONTEXT)
    port_empty = queries.variables_associated_with_port(PORT, context=CONTEXT)
    assert variable_empty.status == "registered" and variable_empty.entries == ()
    assert port_empty.status == "registered" and port_empty.entries == ()
    assert queries.ports_associated_with_variable(
        UNKNOWN_VARIABLE, context=CONTEXT).status == "variable_not_registered"
    assert queries.variables_associated_with_port(
        UNKNOWN_PORT, context=CONTEXT).status == "port_not_registered"

    store.append(variable_registration(VARIABLE_B, owner=ENT_A))
    store.append(port_record(PORT_B, owner=ENT_A))
    first = association(port_anchor_id=PORT_B, note="second port")
    second = association(variable_anchor_id=VARIABLE_B, note="second variable")
    store.append(first)
    store.append(second)
    store.append(association(note="first pair"))
    variables = ModelQueries(store.load()).variables_associated_with_port(
        PORT, context=CONTEXT)
    ports = ModelQueries(store.load()).ports_associated_with_variable(
        VARIABLE, context=CONTEXT)
    assert tuple(entry.entry_index for entry in variables.entries) == (0, 1)
    assert tuple(entry.variable_anchor_id for entry in variables.entries) == (
        VARIABLE, VARIABLE_B)
    assert tuple(entry.port_anchor_id for entry in ports.entries) == (PORT, PORT_B)


def test_assertion_disclosure_separates_vpa_vpw_and_absence(tmp_path):
    root = association(note="root")
    child = association(supersedes=(root.record_id,), note="child")
    event = withdrawal(child.record_id)
    queries = ModelQueries(append_all(
        base(tmp_path), root, child, event).load())
    prior = queries.variable_port_assertion(root.record_id)
    withdrawn = queries.variable_port_assertion(child.record_id)
    withdrawal_event = queries.variable_port_assertion(event.record_id)
    missing = queries.variable_port_assertion("vpa_" + "9" * 64)
    assert prior.lookup_status == "found" and prior.activity == "superseded"
    assert withdrawn.lookup_status == "found" and withdrawn.activity == "withdrawn"
    assert withdrawal_event.lookup_status == "found"
    assert withdrawal_event.activity is None
    assert withdrawal_event.containing_lineage_health is None
    assert withdrawal_event.root_record_index is None
    assert missing.lookup_status == "not_found" and missing.record_index is None


def test_public_inputs_are_validated_before_querying_indexes(tmp_path):
    queries = ModelQueries(base(tmp_path).load())
    calls = (
        lambda: queries.variable_port_association(
            "var_bad", PORT, context=CONTEXT),
        lambda: queries.variable_port_association(
            VARIABLE, "prt_bad", context=CONTEXT),
        lambda: queries.ports_associated_with_variable(
            "var_bad", context=CONTEXT),
        lambda: queries.variables_associated_with_port(
            "prt_bad", context=CONTEXT),
        lambda: queries.variable_port_assertion("vpa_bad"),
    )
    for call in calls:
        with pytest.raises(ModelQueryError) as error:
            call()
        assert error.value.error_code == "MODEL_QUERY_INVALID"
