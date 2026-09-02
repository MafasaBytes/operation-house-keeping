"""ST-002 Slice B authoritative reconstruction and hostile-result attacks."""

import ast
import builtins
import json
import os
from pathlib import Path
import socket
import sqlite3
from types import MappingProxyType

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import ENT_A, ENT_B, registration
from tests.model_kernel.st001_slice_a_helpers import state_declaration
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    T1,
    TRANSITION_A,
    transition_declaration,
    transition_fixture,
    transition_withdrawal,
    world,
)


def reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def complex_result(tmp_path):
    _, registration, from_registration, to_registration, \
        from_root, to_root = transition_fixture()
    from_successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_root.record_id,), recorded_at=T1,
        note="new endpoint pin")
    first = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_root,
        to_declaration=to_root, note="first root")
    second = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_successor,
        to_declaration=to_root, recorded_at=T1, note="second root")
    store, *_ = world(tmp_path, from_successor, first, second)
    queries = kernel.ModelQueries(store.load())
    return (queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED), queries,
        registration, first, second)


def test_declaration_rejects_every_outer_root_group_and_endpoint_forgery(
        tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)
    attacks = (
        ("anchor", lambda p: p.update(
            transition_anchor_id="trn_" + "9" * 32)),
        ("context", lambda p: p.update(context={
            "kind": "lifecycle_view", "view": "as_designed"})),
        ("conclusion", lambda p: p.update(conclusion="declared")),
        ("summary", lambda p: p.update(lineage_summary="healthy")),
        ("findings", lambda p: p.update(agreement_findings=())),
        ("registration", lambda p: p.update(registration_index=0)),
        ("current", lambda p: p.update(current_declaration_indices=())),
        ("roots-order", lambda p: p.update(
            roots=tuple(reversed(p["roots"])))),
        ("groups-order", lambda p: p.update(
            effective_body_groups=tuple(reversed(
                p["effective_body_groups"])))),
        ("lineage", lambda p: p["roots"][0].update(
            lineage_record_indices=())),
        ("tips", lambda p: p["roots"][0].update(
            current_tip_indices=())),
        ("withdrawals", lambda p: p["roots"][0].update(
            withdrawal_indices=(0,))),
        ("health", lambda p: p["roots"][0].update(
            lineage_health="inactive")),
        ("root-groups", lambda p: p["roots"][0].update(
            effective_body_group_indices=(99,))),
        ("group-index", lambda p: p["effective_body_groups"][0].update(
            group_index=99)),
        ("representative", lambda p: p[
            "effective_body_groups"][0].update(
                representative_declaration_index=999)),
        ("group-tips", lambda p: p["effective_body_groups"][0].update(
            current_tip_indices=())),
        ("group-roots", lambda p: p["effective_body_groups"][0].update(
            root_record_indices=())),
        ("from-role", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(role="to")),
        ("to-role", lambda p: p["effective_body_groups"][0][
            "to_endpoint"].update(role="from")),
        ("endpoint-anchor", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(state_anchor_id="sta_" + "9" * 32)),
        ("state-registration", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(state_registration_index=0)),
        ("pin", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(declaration_index=0)),
        ("state-conclusion", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(
                state_declaration_conclusion="inactive")),
        ("activity", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(
                pinned_declaration_activity="withdrawn")),
        ("alignment", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(alignment="endpoint_state_conflicted")),
        ("precedence-swap", lambda p: p["effective_body_groups"][0][
            "from_endpoint"].update(
                state_declaration_conclusion="conflicted",
                alignment="pinned_declaration_superseded")),
    )
    for label, attack in attacks:
        try:
            reconstruct(result, attack)
        except ValidationError:
            continue
        pytest.fail(f"transition disclosure forgery was accepted: {label}")


def test_lookup_entity_and_assertion_reject_derived_forgery(tmp_path):
    result, queries, registration, first, _ = complex_result(tmp_path)
    lookup = queries.transition(TRANSITION_A)
    collection = queries.transitions_of_entity(ENT_A, context=AS_OPERATED)
    assertion = queries.transition_assertion(first.record_id)
    cases = (
        (lookup, (
            lambda p: p.update(status="not_registered"),
            lambda p: p.update(registration_index=None),
            lambda p: p.update(subject_entity_registration_index=None),
            lambda p: p.update(from_state_registration_index=None),
            lambda p: p.update(to_state_registration_index=None),
        )),
        (collection, (
            lambda p: p.update(status="entity_not_registered"),
            lambda p: p.update(entity_registration_index=None),
            lambda p: p.update(entries=()),
            lambda p: p.update(entries=p["entries"] + p["entries"]),
            lambda p: p["entries"][0].update(entry_index=1),
            lambda p: p["entries"][0].update(conclusion="inactive"),
            lambda p: p["entries"][0].update(roots=()),
        )),
        (assertion, (
            lambda p: p.update(record_id=registration.record_id),
            lambda p: p.update(activity="withdrawn"),
            lambda p: p.update(containing_lineage_health="inactive"),
            lambda p: p.update(containing_subject_conclusion="declared"),
            lambda p: p.update(containing_agreement_findings=()),
            lambda p: p.update(root_record_index=999),
            lambda p: p.update(successor_indices=(0,)),
            lambda p: p.update(withdrawal_indices=(0,)),
        )),
    )
    assert result.conclusion == "conflicted"
    for value, attacks in cases:
        for attack in attacks:
            with pytest.raises(ValidationError):
                reconstruct(value, attack)


def test_every_transition_result_index_is_strict_non_boolean(tmp_path):
    result, queries, _, first, _ = complex_result(tmp_path)
    entry = queries.transitions_of_entity(
        ENT_A, context=AS_OPERATED).entries[0]
    assertion = queries.transition_assertion(first.record_id)
    scalar_rows = (
        (result, "registration_index"),
        (result.roots[0], "root_record_index"),
        (result.effective_body_groups[0], "group_index"),
        (result.effective_body_groups[0],
         "representative_declaration_index"),
        (result.effective_body_groups[0].from_endpoint,
         "state_registration_index"),
        (result.effective_body_groups[0].from_endpoint,
         "declaration_index"),
        (entry, "entry_index"),
        (entry, "transition_registration_index"),
        (assertion, "record_index"),
        (assertion, "root_record_index"),
    )
    for value, field in scalar_rows:
        for hostile in (True, False, "0", 0.0, -1):
            payload = value.model_dump(mode="python")
            payload[field] = hostile
            with pytest.raises(ValidationError):
                type(value).model_validate(payload)
    tuple_rows = (
        (result, "current_declaration_indices"),
        (result.roots[0], "lineage_record_indices"),
        (result.roots[0], "current_tip_indices"),
        (result.roots[0], "withdrawal_indices"),
        (result.roots[0], "effective_body_group_indices"),
        (result.effective_body_groups[0], "current_tip_indices"),
        (result.effective_body_groups[0], "root_record_indices"),
        (assertion, "successor_indices"),
        (assertion, "withdrawal_indices"),
    )
    for value, field in tuple_rows:
        for hostile in (True, "0", 0.0, -1):
            payload = value.model_dump(mode="python")
            payload[field] = (hostile,)
            with pytest.raises(ValidationError):
                type(value).model_validate(payload)


def test_all_four_families_reject_h02_material_attack_matrix(
        tmp_path):
    _, queries, _, first, _ = complex_result(tmp_path / "first")
    results = (
        queries.transition(TRANSITION_A),
        queries.transition_declaration(TRANSITION_A, context=AS_OPERATED),
        queries.transitions_of_entity(ENT_A, context=AS_OPERATED),
        queries.transition_assertion(first.record_id),
    )
    other_store, *_ = world(tmp_path / "other")
    other_material = kernel.ModelQueries(other_store.load()).transition(
        TRANSITION_A).material.model_dump(mode="python")
    added = registration(ENT_B, note="unique valid extra record")
    extra_loaded = validate_record_collection(
        "test-model", {**queries.loaded.records, added.record_id: added})
    extra_material = kernel.ModelQueries(extra_loaded).transition(
        TRANSITION_A).material.model_dump(mode="python")
    mixed_material = {
        **extra_material,
        "revision": results[0].material.revision.model_dump(mode="python"),
    }
    for result in results:
        attacks = (
            lambda p: p["material"].update(
                records=p["material"]["records"][:-1]),
            lambda p: p["material"].update(records=(
                *p["material"]["records"], p["material"]["records"][0])),
            lambda p: p["material"].update(
                records=tuple(reversed(p["material"]["records"]))),
            lambda p: p["material"]["records"][0].update(
                note="mutated under stale id"),
            lambda p: p["material"]["revision"].update(
                record_count=p["material"]["revision"]["record_count"] + 1),
            lambda p: p.update(material=extra_material),
            lambda p: p.update(material=mixed_material),
            lambda p: p.update(material=other_material),
            lambda p: p["material"]["records"][0].update(
                record_kind="transition_registration"),
            lambda p: p["material"]["records"][0].update(
                record_id=p["material"]["records"][1]["record_id"]),
        )
        for attack in attacks:
            with pytest.raises(ValidationError):
                reconstruct(result, attack)


def test_revision_count_and_optional_indices_reject_coercible_twins(tmp_path):
    result, queries, _, first, _ = complex_result(tmp_path)
    for hostile in (True, False, "1", 1.0):
        payload = result.model_dump(mode="python")
        payload["material"]["revision"]["record_count"] = hostile
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)
    cases = (
        (queries.transition(TRANSITION_A), "registration_index"),
        (queries.transition(TRANSITION_A),
         "subject_entity_registration_index"),
        (queries.transitions_of_entity(
            ENT_A, context=AS_OPERATED), "entity_registration_index"),
        (queries.transition_assertion(first.record_id), "record_index"),
        (queries.transition_assertion(first.record_id), "root_record_index"),
    )
    for value, field in cases:
        for hostile in (True, "0", 0.0):
            payload = value.model_dump(mode="python")
            payload[field] = hostile
            with pytest.raises(ValidationError):
                type(value).model_validate(payload)


def test_hidden_nested_instances_and_implication_fields_reject(tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)
    root = result.roots[0].model_copy(update={"priority": "winner"})
    endpoint = result.effective_body_groups[0].from_endpoint.model_copy(
        update={"occurred": True})
    group = result.effective_body_groups[0].model_copy(update={
        "from_endpoint": endpoint})
    material = result.material.model_copy(update={
        "recommended_action": "select"})
    hostiles = (
        result.model_copy(update={"confidence": 1}),
        result.model_copy(update={"roots": (
            root, *result.roots[1:])}),
        result.model_copy(update={"effective_body_groups": (
            group, *result.effective_body_groups[1:])}),
        result.model_copy(update={"material": material}),
    )
    for hostile in hostiles:
        with pytest.raises(ValidationError):
            type(result).model_validate(hostile)
    for field in (
            "occurred", "triggered_by", "confidence", "recommended_action",
            "cutoff", "source_selector", "observation", "classification"):
        payload = result.model_dump(mode="python")
        payload[field] = "forged"
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)


def test_outer_nested_and_material_private_cache_injection_rejects(tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)

    outer = type(result).model_validate(result.model_dump(mode="python"))
    object.__setattr__(outer, "__pydantic_private__", {
        "_occurred": True,
        "_winner_cache": outer.roots[0],
    })
    with pytest.raises(ValidationError, match="private cache"):
        type(outer).model_validate(outer)

    nested = type(result).model_validate(result.model_dump(mode="python"))
    endpoint = nested.effective_body_groups[0].from_endpoint
    endpoint.__pydantic_private__["_winner"] = "forged-private-cache"
    with pytest.raises(ValidationError, match="private cache"):
        type(nested).model_validate(nested)

    material = type(result).model_validate(
        result.model_dump(mode="python"))
    object.__setattr__(material.material, "__pydantic_private__", {
        "_assessment": "forged-private-cache",
    })
    with pytest.raises(ValidationError, match="private cache"):
        type(material).model_validate(material)


def test_mapping_wrapper_cannot_launder_hidden_material_extra(tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)
    hostile_material = result.material.model_copy(update={"winner": "forged"})
    payload = {**result.model_dump(mode="python"),
               "material": hostile_material}
    with pytest.raises(ValidationError):
        type(result).model_validate(MappingProxyType(payload))


def test_nested_row_bound_to_another_snapshot_rejects_before_dump(tmp_path):
    first, _, _, _, _ = complex_result(tmp_path / "first")
    second, _, _, _, _ = complex_result(tmp_path / "second")
    assert first.model_dump(mode="python") == second.model_dump(mode="python")
    foreign_endpoint = second.effective_body_groups[0].from_endpoint
    hostile_group = first.effective_body_groups[0].model_copy(update={
        "from_endpoint": foreign_endpoint})
    hostile = first.model_copy(update={"effective_body_groups": (
        hostile_group, *first.effective_body_groups[1:])})
    with pytest.raises(ValidationError, match="another material snapshot"):
        type(first).model_validate(hostile)


def test_cycles_and_excessive_depth_reject_deterministically(tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)
    cycle = []
    cycle.append(cycle)
    payload = result.model_dump(mode="python")
    payload["roots"] = cycle
    with pytest.raises(ValidationError, match="cycle"):
        type(result).model_validate(payload)

    nested = "leaf"
    for _ in range(130):
        nested = [nested]
    payload = result.model_dump(mode="python")
    payload["occurred"] = nested
    with pytest.raises(ValidationError, match="maximum depth"):
        type(result).model_validate(payload)


def test_plain_round_trip_binds_one_material_and_no_nested_snapshot(tmp_path):
    result, queries, _, first, _ = complex_result(tmp_path)
    values = (
        queries.transition(TRANSITION_A), result,
        queries.transitions_of_entity(ENT_A, context=AS_OPERATED),
        queries.transition_assertion(first.record_id),
    )
    for value in values:
        rebuilt = type(value).model_validate(value.model_dump(mode="python"))
        assert rebuilt.model_dump_json() == value.model_dump_json()
        rebuilt_instance = type(value).model_validate(value)
        assert rebuilt_instance.model_dump_json() == value.model_dump_json()
        decoded = json.loads(value.model_dump_json())
        assert list(decoded).count("material") == 1
        assert len(decoded["material"]["records"]) == \
            decoded["material"]["revision"]["record_count"]
    group = type(result).model_validate(
        result.model_dump(mode="python")).effective_body_groups[0]
    assert group.representative_declaration.record_kind == \
        "transition_declaration"
    assert group.from_endpoint.declaration.record_kind == "state_declaration"


def test_revalidation_has_no_store_filesystem_network_environment_or_clock(
        tmp_path, monkeypatch):
    result, _, _, _, _ = complex_result(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("external capability access is forbidden")

    for name in ("__init__", "append", "load", "replay"):
        monkeypatch.setattr(kernel.ModelStore, name, forbidden)
    for name in ("open", "read_text", "read_bytes", "write_text",
                 "write_bytes"):
        monkeypatch.setattr(Path, name, forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(sqlite3, "connect", forbidden)
    monkeypatch.setattr(os, "getenv", forbidden)
    rebuilt = type(result).model_validate(result.model_dump(mode="python"))
    assert rebuilt.model_dump_json() == result.model_dump_json()


def test_revalidation_source_has_no_clock_or_cache_capability():
    path = Path("backend/model_kernel/transition_results.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported_modules = set()
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)
    assert not imported_modules.intersection({
        "time", "datetime", "functools", "cachetools"})
    assert not called_names.intersection({
        "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
        "now", "utcnow", "today", "cache", "lru_cache",
        "cached_property"})


def test_invalid_inputs_reject_before_loaded_records_are_accessed(tmp_path):
    store, *_ = world(tmp_path)
    loaded = store.load()

    class ExplodingRecords(dict):
        def __iter__(self):
            raise AssertionError("model records were accessed")

        def __getitem__(self, key):
            raise AssertionError("model records were accessed")

    object.__setattr__(loaded, "records", ExplodingRecords())
    queries = kernel.ModelQueries(loaded)
    calls = (
        lambda: queries.transition(False),
        lambda: queries.transition("trn_bad"),
        lambda: queries.transition_declaration(TRANSITION_A, context=None),
        lambda: queries.transitions_of_entity({}, context=AS_OPERATED),
        lambda: queries.transition_assertion("trd_bad"),
        lambda: queries.transition_assertion("std_" + "a" * 64),
        lambda: queries.transition_assertion([]),
    )
    for call in calls:
        with pytest.raises(kernel.ModelQueryError):
            call()


def test_forged_context_rejects_before_loaded_records_are_accessed(tmp_path):
    store, *_ = world(tmp_path)
    loaded = store.load()

    class ExplodingRecords(dict):
        def __iter__(self):
            raise AssertionError("model records were accessed")

        def __getitem__(self, key):
            raise AssertionError("model records were accessed")

    object.__setattr__(loaded, "records", ExplodingRecords())
    forged = AS_OPERATED.model_copy(update={"transition": "forged"})
    with pytest.raises(kernel.ModelQueryError) as error:
        kernel.ModelQueries(loaded).transition_declaration(
            TRANSITION_A, context=forged)
    assert error.value.error_code == "MODEL_CONTEXT_INVALID"


def test_every_transition_result_contract_is_frozen(tmp_path):
    result, queries, _, first, _ = complex_result(tmp_path)
    collection = queries.transitions_of_entity(ENT_A, context=AS_OPERATED)
    instances = (
        queries.transition(TRANSITION_A), result, result.roots[0],
        result.effective_body_groups[0],
        result.effective_body_groups[0].from_endpoint,
        collection, collection.entries[0],
        queries.transition_assertion(first.record_id),
    )
    assert {type(item).__name__ for item in instances} == {
        "TransitionEndpointResult", "TransitionEffectiveBodyGroupResult",
        "TransitionDeclarationRootResult", "TransitionLookupResult",
        "TransitionDeclarationResult", "EntityTransitionEntry",
        "EntityTransitionsResult", "TransitionAssertionDisclosureResult",
    }
    for item in instances:
        field = next(iter(type(item).model_fields))
        with pytest.raises(ValidationError):
            setattr(item, field, getattr(item, field))


def test_successors_first_assertion_activity_precedence_is_defensive(tmp_path):
    root = transition_declaration(note="root")
    child = transition_declaration(
        supersedes=(root.record_id,), recorded_at=T1, note="child")
    other = transition_declaration(
        recorded_at=T1, note="independent withdrawn root")
    withdrawal = transition_withdrawal(other)
    store, *_ = world(tmp_path, root, child, other, withdrawal)
    loaded = store.load()
    object.__setattr__(loaded, "transition_declaration_withdrawn_by", {
        **loaded.transition_declaration_withdrawn_by,
        root.record_id: (withdrawal.record_id,),
    })
    material = kernel.ModelQueries(loaded)._material()
    from backend.model_kernel.transition_results import \
        _transition_assertion_payload
    payload = _transition_assertion_payload(material, loaded, root.record_id)
    assert payload["activity"] == "superseded"
