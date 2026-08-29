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
DEMO_VARIABLE = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
DEMO_PORT = "prt_91a3d6db9df440e1a09dbdb185c7b182"
DEMO_MODEL = Path("models/demo-printer")


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
        variable_present = status in {"both_registered", "port_not_registered"}
        port_present = status in {"both_registered", "variable_not_registered"}
        assert (result.variable_registration_index is not None) is variable_present
        assert (result.variable_owner_registration_index is not None) is \
            variable_present
        assert (result.port_registration_index is not None) is port_present
        assert (result.port_owner_registration_index is not None) is port_present
        if variable_present:
            assert result.material.record_at(
                result.variable_registration_index).record_kind == \
                "variable_registration"
            assert result.material.record_at(
                result.variable_owner_registration_index).record_kind == \
                "entity_registration"
        if port_present:
            assert result.material.record_at(
                result.port_registration_index).record_kind == \
                "port_registration"
            assert result.material.record_at(
                result.port_owner_registration_index).record_kind == \
                "entity_registration"
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


def test_aggregate_retains_active_inactive_and_conflicted_roots(tmp_path):
    fork = association(note="fork root")
    left = association(supersedes=(fork.record_id,), note="left")
    right = association(supersedes=(fork.record_id,), note="right")
    healthy = association(note="healthy corroboration")
    inactive = association(note="inactive corroboration")
    inactive_event = withdrawal(inactive.record_id, note="inactive event")

    conflicted = exact(append_all(
        base(tmp_path / "conflicted"), fork, left, right, healthy, inactive,
        inactive_event))
    by_root = {
        conflicted.material.record_at(row.root_record_index).record_id: row
        for row in conflicted.roots
    }
    assert (conflicted.conclusion, conflicted.lineage_summary) == (
        "asserted", "conflicted")
    assert set(by_root) == {fork.record_id, healthy.record_id,
                            inactive.record_id}
    assert by_root[fork.record_id].lineage_health == "conflicted"
    assert by_root[healthy.record_id].lineage_health == "healthy"
    assert by_root[inactive.record_id].lineage_health == "inactive"

    repaired = exact(append_all(
        base(tmp_path / "repaired"), fork, left, right, healthy, inactive,
        inactive_event, withdrawal(left.record_id, note="selective event")))
    assert (repaired.conclusion, repaired.lineage_summary) == (
        "asserted", "healthy")
    assert {row.lineage_health for row in repaired.roots} == {
        "healthy", "inactive"}

    all_inactive = exact(append_all(
        base(tmp_path / "all-inactive"), fork,
        withdrawal(fork.record_id, note="fork event"), inactive,
        inactive_event))
    assert (all_inactive.conclusion, all_inactive.lineage_summary) == (
        "inactive", "inactive")
    assert all(row.lineage_health == "inactive"
               for row in all_inactive.roots)


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


def test_reverse_collections_group_roots_and_include_inactive_subjects(tmp_path):
    store = base(tmp_path)
    store.append(port_record(PORT_B, owner=ENT_A))
    first_root = association(note="first root")
    corroborating = association(note="corroborating root")
    inactive = association(port_anchor_id=PORT_B, note="inactive subject")
    event = withdrawal(inactive.record_id)
    append_all(store, first_root, corroborating, inactive, event)
    queries = ModelQueries(store.load())

    forward = queries.ports_associated_with_variable(VARIABLE, context=CONTEXT)
    assert tuple(entry.port_anchor_id for entry in forward.entries) == (
        PORT, PORT_B)
    assert tuple(entry.entry_index for entry in forward.entries) == (0, 1)
    assert len(forward.entries[0].roots) == 2
    assert (forward.entries[0].conclusion,
            forward.entries[0].lineage_summary) == ("asserted", "healthy")
    assert (forward.entries[1].conclusion,
            forward.entries[1].lineage_summary) == ("inactive", "inactive")

    reverse = queries.variables_associated_with_port(PORT, context=CONTEXT)
    exact_result = queries.variable_port_association(
        VARIABLE, PORT, context=CONTEXT)
    assert len(reverse.entries) == 1
    assert reverse.entries[0].roots == exact_result.roots
    assert reverse.entries[0].conclusion == exact_result.conclusion
    assert reverse.entries[0].lineage_summary == exact_result.lineage_summary


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


def test_assertion_activity_is_independent_of_containing_root_health(tmp_path):
    root = association(note="root")
    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")

    conflict_queries = ModelQueries(append_all(
        base(tmp_path / "conflict"), root, left, right).load())
    ancestor = conflict_queries.variable_port_assertion(root.record_id)
    tip = conflict_queries.variable_port_assertion(left.record_id)
    assert (ancestor.activity, ancestor.containing_lineage_health) == (
        "superseded", "conflicted")
    assert (tip.activity, tip.containing_lineage_health) == (
        "current", "conflicted")

    event = withdrawal(left.record_id)
    repaired_queries = ModelQueries(append_all(
        base(tmp_path / "repaired"), root, left, right, event).load())
    withdrawn = repaired_queries.variable_port_assertion(left.record_id)
    survivor = repaired_queries.variable_port_assertion(right.record_id)
    event_disclosure = repaired_queries.variable_port_assertion(event.record_id)
    assert (withdrawn.activity, withdrawn.containing_lineage_health) == (
        "withdrawn", "healthy")
    assert (survivor.activity, survivor.containing_lineage_health) == (
        "current", "healthy")
    assert event_disclosure.activity is None
    assert event_disclosure.containing_lineage_health is None
    assert event_disclosure.root_record_index is None
    assert event_disclosure.successor_indices == ()
    assert event_disclosure.withdrawal_indices == ()


def test_demo_pt_semantics_and_shared_owner_do_not_infer_vp_association():
    loaded = ModelStore(DEMO_MODEL).load()
    queries = ModelQueries(loaded)
    exact_result = queries.variable_port_association(
        DEMO_VARIABLE, DEMO_PORT, context=CONTEXT)
    assert loaded.revision.record_count == 28
    assert loaded.revision.revision_id == (
        "mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2")
    assert len(loaded.variable_port_associations) == 0
    assert any(record.record_kind == "port_interface_declaration"
               for record in loaded.records.values())
    assert any(record.record_kind == "port_connection_assertion"
               for record in loaded.records.values())
    assert any(record.record_kind == "port_compatibility_declaration"
               for record in loaded.records.values())
    assert (exact_result.endpoint_status, exact_result.owner_alignment,
            exact_result.conclusion, exact_result.lineage_summary) == (
                "both_registered", "same_owner", "not_declared",
                "not_applicable")
    assert exact_result.roots == ()
    assert queries.ports_associated_with_variable(
        DEMO_VARIABLE, context=CONTEXT).entries == ()
    assert queries.variables_associated_with_port(
        DEMO_PORT, context=CONTEXT).entries == ()


def test_public_inputs_are_validated_before_querying_indexes(tmp_path):
    queries = ModelQueries(base(tmp_path).load())
    calls = (
        (lambda: queries.variable_port_association(
            "var_bad", PORT, context=CONTEXT), "MODEL_ANCHOR_ID_INVALID"),
        (lambda: queries.variable_port_association(
            VARIABLE, "prt_bad", context=CONTEXT),
         "MODEL_ANCHOR_ID_INVALID"),
        (lambda: queries.ports_associated_with_variable(
            "var_bad", context=CONTEXT), "MODEL_ANCHOR_ID_INVALID"),
        (lambda: queries.variables_associated_with_port(
            "prt_bad", context=CONTEXT), "MODEL_ANCHOR_ID_INVALID"),
        (lambda: queries.variable_port_assertion("vpa_bad"),
         "MODEL_RECORD_ID_INVALID"),
    )
    for call, expected_code in calls:
        with pytest.raises(ModelQueryError) as error:
            call()
        assert error.value.error_code == expected_code
