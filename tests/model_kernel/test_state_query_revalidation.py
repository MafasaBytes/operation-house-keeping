"""ST-001 Slice B authoritative reconstruction and isolation attacks."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from types import MappingProxyType

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import (
    CON_A, ENT_A, constraint_declaration, registration, upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED, STATE_A, T1, condition_world_records, pins,
    state_declaration, state_registration, state_withdrawal, world,
)


def reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def conflict_result(tmp_path):
    registration = state_registration()
    first = state_declaration(registration, note="first")
    alternative_vcn = constraint_declaration(
        CON_A, predicate=upper_bound("90"), recorded_at=T1,
        note="alternate pin")
    alternate_pins = tuple(
        pin.model_copy(update={
            "constraint_declaration_record_id": alternative_vcn.record_id})
        if pin.constraint_anchor_id == CON_A else pin
        for pin in pins())
    second = state_declaration(
        registration, condition_pins=alternate_pins, recorded_at=T1,
        note="second")
    queries = kernel.ModelQueries(world(
        tmp_path, alternative_vcn, first, second).load())
    return queries.state_declaration(
        STATE_A, context=AS_OPERATED), first, second


def test_declaration_rejects_outer_root_group_condition_and_material_forgery(
        tmp_path):
    result, _, _ = conflict_result(tmp_path)
    attacks = (
        ("conclusion", lambda p: p.update(conclusion="declared")),
        ("summary", lambda p: p.update(lineage_summary="healthy")),
        ("findings", lambda p: p.update(agreement_findings=())),
        ("registration", lambda p: p.update(registration_index=0)),
        ("current", lambda p: p.update(current_declaration_indices=())),
        ("context", lambda p: p.update(context={"kind": "lifecycle_view",
                                                "view": "as_designed"})),
        ("roots-order", lambda p: p.update(roots=list(reversed(p["roots"])))),
        ("groups-order", lambda p: p.update(effective_body_groups=
                                             list(reversed(p["effective_body_groups"])))),
        ("lineage", lambda p: p["roots"][0].update(lineage_record_indices=())),
        ("tips", lambda p: p["roots"][0].update(current_tip_indices=())),
        ("withdrawals", lambda p: p["roots"][0].update(withdrawal_indices=(0,))),
        ("health", lambda p: p["roots"][0].update(lineage_health="inactive")),
        ("root-groups", lambda p: p["roots"][0].update(
            effective_body_group_indices=(99,))),
        ("group-index", lambda p: p["effective_body_groups"][0].update(group_index=99)),
        ("representative", lambda p: p["effective_body_groups"][0].update(
            representative_declaration_index=999),
         ),
        ("group-tips", lambda p: p["effective_body_groups"][0].update(
            current_tip_indices=())),
        ("group-roots", lambda p: p["effective_body_groups"][0].update(
            root_record_indices=())),
        ("conditions", lambda p: p["effective_body_groups"][0].update(conditions=())),
        ("condition-index", lambda p: p["effective_body_groups"][0]["conditions"][0].update(
            condition_index=99)),
        ("constraint", lambda p: p["effective_body_groups"][0]["conditions"][0].update(
            constraint_anchor_id="con_" + "f" * 32)),
        ("pin", lambda p: p["effective_body_groups"][0]["conditions"][0].update(
            pinned_declaration_index=0)),
        ("material-order", lambda p: p["material"].update(
            records=list(reversed(p["material"]["records"])))),
        ("stale-id", lambda p: p["material"]["records"][0].update(note="stale id")),
        ("revision", lambda p: p["material"]["revision"].update(
            record_count=p["material"]["revision"]["record_count"] + 1)),
    )
    for label, attack in attacks:
        try:
            reconstruct(result, attack)
        except ValidationError:
            continue
        pytest.fail(f"forgery was accepted: {label}")


def test_lookup_entity_collection_and_assertion_reject_derived_forgery(
        tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration)
    queries = kernel.ModelQueries(world(tmp_path, declaration).load())
    lookup = queries.state(STATE_A)
    collection = queries.states_of_entity(ENT_A, context=AS_OPERATED)
    assertion = queries.state_assertion(declaration.record_id)

    lookup_attacks = (
        lambda p: p.update(status="not_registered"),
        lambda p: p.update(registration_index=None),
        lambda p: p.update(subject_entity_registration_index=None),
        lambda p: p.update(condition_constraint_registration_indices=()),
        lambda p: p.update(condition_variable_registration_indices=()),
        lambda p: p.update(condition_owner_registration_indices=()),
    )
    collection_attacks = (
        lambda p: p.update(status="entity_not_registered"),
        lambda p: p.update(entity_registration_index=None),
        lambda p: p.update(entries=()),
        lambda p: p.update(entries=p["entries"] + p["entries"]),
        lambda p: p["entries"][0].update(entry_index=1),
        lambda p: p["entries"][0].update(
            state_anchor_id="sta_" + "9" * 32),
        lambda p: p["entries"][0].update(conclusion="inactive"),
        lambda p: p["entries"][0].update(roots=()),
    )
    assertion_attacks = (
        lambda p: p.update(activity="withdrawn"),
        lambda p: p.update(containing_lineage_health="inactive"),
        lambda p: p.update(containing_subject_conclusion="inactive"),
        lambda p: p.update(containing_agreement_findings=()),
        lambda p: p.update(root_record_index=999),
        lambda p: p.update(successor_indices=(0,)),
        lambda p: p.update(withdrawal_indices=(0,)),
        lambda p: p.update(record_id="std_" + "9" * 64),
    )
    for value, attacks in (
            (lookup, lookup_attacks), (collection, collection_attacks),
            (assertion, assertion_attacks)):
        for attack in attacks:
            with pytest.raises(ValidationError):
                reconstruct(value, attack)


def test_every_state_query_index_rejects_boolean_float_string_and_negative(
        tmp_path):
    result, _, _ = conflict_result(tmp_path)
    scalar_rows = (
        (result, "registration_index"),
        (result.roots[0], "root_record_index"),
        (result.effective_body_groups[0], "group_index"),
        (result.effective_body_groups[0],
         "representative_declaration_index"),
        (result.effective_body_groups[0].conditions[0], "condition_index"),
        (result.effective_body_groups[0].conditions[0],
         "constraint_registration_index"),
        (result.effective_body_groups[0].conditions[0],
         "pinned_declaration_index"),
        (result.effective_body_groups[0].conditions[0],
         "target_variable_registration_index"),
        (result.effective_body_groups[0].conditions[0],
         "target_owner_registration_index"),
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
    )
    for value, field in tuple_rows:
        for hostile in (True, "0", 0.0, -1):
            payload = value.model_dump(mode="python")
            payload[field] = (hostile,)
            with pytest.raises(ValidationError):
                type(value).model_validate(payload)


def test_optional_outer_indices_reject_boolean_and_coercion(tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration)
    queries = kernel.ModelQueries(world(tmp_path, declaration).load())
    cases = (
        (queries.state(STATE_A), "registration_index"),
        (queries.state(STATE_A), "subject_entity_registration_index"),
        (queries.states_of_entity(
            ENT_A, context=AS_OPERATED), "entity_registration_index"),
        (queries.state_assertion(declaration.record_id), "record_index"),
        (queries.state_assertion(declaration.record_id), "root_record_index"),
    )
    for result, field in cases:
        for hostile in (True, "0", 0.0):
            payload = result.model_dump(mode="python")
            payload[field] = hostile
            with pytest.raises(ValidationError):
                type(result).model_validate(payload)


def test_wrong_union_arm_indices_reject(tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration)
    result = kernel.ModelQueries(world(tmp_path, declaration).load()).state(
        STATE_A)
    payload = result.model_dump(mode="python")
    constraint_index = payload["condition_constraint_registration_indices"][0]
    payload["registration_index"] = constraint_index
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)

    declaration_result = kernel.ModelQueries(world(
        tmp_path / "declaration", declaration).load()).state_declaration(
            STATE_A, context=AS_OPERATED)
    payload = declaration_result.model_dump(mode="python")
    condition = payload["effective_body_groups"][0]["conditions"][0]
    condition["target_variable_registration_index"] = condition[
        "constraint_registration_index"]
    with pytest.raises(ValidationError):
        type(declaration_result).model_validate(payload)


def test_nested_construct_copy_and_hidden_extra_forgery_is_revalidated(
        tmp_path):
    result, _, _ = conflict_result(tmp_path)
    hostile_root = result.roots[0].model_copy(
        update={"lineage_health": "inactive"})
    hostile_condition = result.effective_body_groups[0].conditions[0].model_copy(
        update={"condition_index": 99})
    hostile_group = result.effective_body_groups[0].model_copy(
        update={"conditions": (
            hostile_condition,
            *result.effective_body_groups[0].conditions[1:])})
    extra_root = result.roots[0].model_copy(update={"priority": "winner"})
    hostiles = (
        result.model_copy(update={"conclusion": "declared"}),
        type(result).model_construct(**{
            **result.model_dump(), "agreement_findings": ()}),
        result.model_copy(update={"roots": (
            hostile_root, *result.roots[1:])}),
        result.model_copy(update={"effective_body_groups": (
            hostile_group, *result.effective_body_groups[1:])}),
        result.model_copy(update={"roots": (
            extra_root, *result.roots[1:])}),
    )
    for index, hostile in enumerate(hostiles):
        try:
            type(result).model_validate(hostile)
        except ValidationError:
            continue
        pytest.fail(f"nested hostile instance was accepted: {index}")


def test_mapping_wrapper_cannot_launder_hidden_nested_result_extra(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    hostile_material = result.material.model_copy(
        update={"winner": "forged"})
    payload = {
        **result.model_dump(mode="python"),
        "material": hostile_material,
    }
    with pytest.raises(ValidationError):
        type(result).model_validate(MappingProxyType(payload))


def test_carried_revision_count_rejects_boolean_and_coercible_twins(tmp_path):
    entity = registration(ENT_A)
    loaded = validate_record_collection(
        "demo-printer", {entity.record_id: entity})
    result = kernel.ModelQueries(loaded).state(STATE_A)
    for hostile in (True, False, "1", 1.0):
        payload = result.model_dump(mode="python")
        payload["material"]["revision"]["record_count"] = hostile
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)


def test_malformed_nested_collections_and_implication_fields_reject(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    for field in ("roots", "effective_body_groups"):
        payload = result.model_dump(mode="python")
        payload[field] = None
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)
    payload = result.model_dump(mode="python")
    payload["effective_body_groups"][0]["conditions"] = None
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)

    for field in (
            "current_state", "winner", "priority", "exclusive", "complete",
            "transition", "from_state", "to_state", "trigger", "action",
            "flow", "causes", "controls", "safe", "healthy"):
        payload = result.model_dump(mode="python")
        payload[field] = "forged"
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)


def test_invalid_query_input_rejects_before_any_model_index_access(tmp_path):
    loaded = world(tmp_path).load()

    class ExplodingRecords(dict):
        def __iter__(self):
            raise AssertionError("model records were accessed")

        def __getitem__(self, key):
            raise AssertionError("model records were accessed")

    object.__setattr__(loaded, "records", ExplodingRecords())
    queries = kernel.ModelQueries(loaded)
    calls = (
        lambda: queries.state(False),
        lambda: queries.state("sta_bad"),
        lambda: queries.state_declaration(STATE_A, context=None),
        lambda: queries.states_of_entity({}, context=AS_OPERATED),
        lambda: queries.state_assertion("std_bad"),
        lambda: queries.state_assertion("bhd_" + "a" * 64),
        lambda: queries.state_assertion([]),
    )
    for call in calls:
        with pytest.raises(kernel.ModelQueryError):
            call()


def test_forged_context_instance_rejects_before_any_model_index_access(
        tmp_path):
    loaded = world(tmp_path).load()

    class ExplodingRecords(dict):
        def __iter__(self):
            raise AssertionError("model records were accessed")

        def __getitem__(self, key):
            raise AssertionError("model records were accessed")

    object.__setattr__(loaded, "records", ExplodingRecords())
    forged = AS_OPERATED.model_copy(update={"transition": "forged"})
    with pytest.raises(kernel.ModelQueryError) as error:
        kernel.ModelQueries(loaded).state_declaration(STATE_A, context=forged)
    assert error.value.error_code == "MODEL_CONTEXT_INVALID"


def test_result_revalidation_is_store_and_filesystem_independent(
        tmp_path, monkeypatch):
    result, _, _ = conflict_result(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("store or filesystem access is forbidden")

    for name in ("__init__", "append", "load", "replay"):
        monkeypatch.setattr(kernel.ModelStore, name, forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    rebuilt = type(result).model_validate(result.model_dump(mode="python"))
    assert rebuilt.model_dump_json() == result.model_dump_json()


def test_complete_material_is_carried_once_and_rows_are_indices_only(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    decoded = json.loads(result.model_dump_json())
    assert len(decoded["material"]["records"]) == \
        decoded["material"]["revision"]["record_count"]
    assert len({record["record_id"]
                for record in decoded["material"]["records"]}) == len(
                    decoded["material"]["records"])
    for root in decoded["roots"]:
        assert "material" not in root
        assert "evidence" not in root
        assert "authority" not in root
    for group in decoded["effective_body_groups"]:
        assert "material" not in group
        assert "evidence" not in group
        assert "authority" not in group
        for condition in group["conditions"]:
            assert "material" not in condition
            assert "record" not in condition


def test_state_query_result_is_deterministic_across_record_order_and_hash_seed(
        tmp_path):
    registration = state_registration()
    declaration = state_declaration(registration)
    records = (*condition_world_records(), registration, declaration)
    forward = validate_record_collection(
        "demo-printer", {record.record_id: record for record in records})
    reverse = validate_record_collection(
        "demo-printer", {record.record_id: record for record in reversed(records)})
    first = kernel.ModelQueries(forward).state_declaration(
        STATE_A, context=AS_OPERATED).model_dump_json()
    second = kernel.ModelQueries(reverse).state_declaration(
        STATE_A, context=AS_OPERATED).model_dump_json()
    assert first == second

    script = """
from backend.model_kernel import ModelQueries
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.st001_slice_a_helpers import (AS_OPERATED, STATE_A, condition_world_records, state_declaration, state_registration)
r = state_registration()
d = state_declaration(r)
records = (*condition_world_records(), r, d)
loaded = validate_record_collection('demo-printer', {x.record_id: x for x in set(records)})
print(ModelQueries(loaded).state_declaration(STATE_A, context=AS_OPERATED).model_dump_json())
"""
    outputs = []
    for seed in ("1", "29", "101"):
        env = {**os.environ, "PYTHONHASHSEED": seed,
               "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(), env=env,
            check=True, capture_output=True, text=True)
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1] == outputs[2]


def test_query_and_state_result_modules_are_store_and_upper_layer_isolated():
    forbidden = (
        "backend.state_classification", "backend.model_state",
        "backend.temporal_state", "backend.identity_binding",
        "backend.observation_compatibility", "backend.semantic_compatibility",
        "backend.constraint_evaluation", "backend.source_interpretation",
        "backend.data_sources", "backend.behavior_evaluation",
        "backend.structural_evidence",
    )
    for filename in (
            "backend/model_kernel/queries.py",
            "backend/model_kernel/state_results.py"):
        path = Path(filename)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = []
        imported_symbols = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
                imported_symbols.extend(alias.asname or alias.name
                                        for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
                imported_symbols.extend(alias.asname or alias.name
                                        for alias in node.names)
        assert not any(name.startswith(forbidden) for name in imports)
        assert "ModelStore" not in imported_symbols
        assert not any(isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name)
                       and node.func.id == "ModelStore"
                       for node in ast.walk(tree))
        assert "sqlite3" not in source
        assert "Path(" not in source
        assert "open(" not in source
    assert not Path("backend/state_classification").exists()
