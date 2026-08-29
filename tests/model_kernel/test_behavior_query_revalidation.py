"""BH-001 Slice B authoritative reconstruction and isolation attacks."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from tests.model_kernel.bh001_slice_a_helpers import (
    AS_DESIGNED,
    BEHAVIOR_A,
    T1,
    behavior_declaration,
    behavior_registration,
    semantic_lock,
    world,
)
from tests.model_kernel.builders import VAR_A, VAR_B


def reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def conflict_result(tmp_path):
    registration = behavior_registration()
    first = behavior_declaration(registration, note="first")
    second = behavior_declaration(
        registration, locks=(semantic_lock(VAR_A, role="estimated"),
                             semantic_lock(VAR_B, role="reported")),
        recorded_at=T1, note="second")
    queries = kernel.ModelQueries(world(tmp_path, first, second).load())
    return queries.behavior_declaration(
        BEHAVIOR_A, context=AS_DESIGNED), first, second


def test_rule_result_rejects_every_outer_root_group_and_material_forgery(
        tmp_path):
    result, first, second = conflict_result(tmp_path)
    attacks = (
        lambda p: p.update(conclusion="declared"),
        lambda p: p.update(lineage_summary="healthy"),
        lambda p: p.update(agreement_findings=()),
        lambda p: p.update(registration_index=0),
        lambda p: p.update(current_declaration_indices=()),
        lambda p: p.update(context={"kind": "lifecycle_view",
                                    "view": "as_built"}),
        lambda p: p.update(roots=list(reversed(p["roots"]))),
        lambda p: p.update(effective_body_groups=
                           list(reversed(p["effective_body_groups"]))),
        lambda p: p["roots"][0].update(lineage_record_indices=()),
        lambda p: p["roots"][0].update(current_tip_indices=()),
        lambda p: p["roots"][0].update(withdrawal_indices=(0,)),
        lambda p: p["roots"][0].update(lineage_health="inactive"),
        lambda p: p["roots"][0].update(effective_body_group_indices=(1,)),
        lambda p: p["effective_body_groups"][0].update(group_index=1),
        lambda p: p["effective_body_groups"][0].update(
            representative_declaration_index=999),
        lambda p: p["effective_body_groups"][0].update(current_tip_indices=()),
        lambda p: p["effective_body_groups"][0].update(root_record_indices=()),
        lambda p: p["material"].update(
            records=list(reversed(p["material"]["records"]))),
        lambda p: p["material"]["records"][0].update(note="stale id"),
        lambda p: p["material"]["revision"].update(
            record_count=p["material"]["revision"]["record_count"] + 1),
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            reconstruct(result, attack)


def test_lookup_reverse_and_assertion_reject_derived_forgery(tmp_path):
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    queries = kernel.ModelQueries(world(tmp_path, declaration).load())
    lookup = queries.behavior(BEHAVIOR_A)
    reverse = queries.behaviors_involving_variable(
        VAR_A, context=AS_DESIGNED)
    assertion = queries.behavior_assertion(declaration.record_id)

    lookup_attacks = (
        lambda p: p.update(status="not_registered"),
        lambda p: p.update(registration_index=None),
        lambda p: p.update(participant_variable_registration_indices=()),
        lambda p: p.update(participant_owner_registration_indices=()),
    )
    reverse_attacks = (
        lambda p: p.update(status="variable_not_registered"),
        lambda p: p.update(entries=()),
        lambda p: p.update(entries=p["entries"] + p["entries"]),
        lambda p: p["entries"][0].update(entry_index=1),
        lambda p: p["entries"][0].update(
            other_variable_anchor_id="var_" + "9" * 32),
        lambda p: p["entries"][0].update(conclusion="inactive"),
    )
    assertion_attacks = (
        lambda p: p.update(activity="withdrawn"),
        lambda p: p.update(containing_lineage_health="inactive"),
        lambda p: p.update(containing_subject_conclusion="inactive"),
        lambda p: p.update(containing_agreement_findings=()),
        lambda p: p.update(root_record_index=999),
        lambda p: p.update(successor_indices=(0,)),
        lambda p: p.update(withdrawal_indices=(0,)),
        lambda p: p.update(record_id="bhd_" + "9" * 64),
    )
    for result, attacks in (
            (lookup, lookup_attacks), (reverse, reverse_attacks),
            (assertion, assertion_attacks)):
        for attack in attacks:
            with pytest.raises(ValidationError):
                reconstruct(result, attack)


def test_nested_construct_and_copy_forgery_is_revalidated(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    hostile_root = result.roots[0].model_copy(
        update={"lineage_health": "inactive"})
    hostile_group = result.effective_body_groups[0].model_copy(
        update={"group_index": 99})
    hostiles = (
        result.model_copy(update={"conclusion": "declared"}),
        type(result).model_construct(**{
            **result.model_dump(), "agreement_findings": ()}),
        result.model_copy(update={"roots": (hostile_root, *result.roots[1:])}),
        result.model_copy(update={
            "effective_body_groups": (
                hostile_group, *result.effective_body_groups[1:])}),
    )
    for hostile in hostiles:
        with pytest.raises(ValidationError):
            type(result).model_validate(hostile)


def test_every_behavior_index_rejects_boolean_and_coercion(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    scalar_paths = (
        (result, "registration_index"),
        (result.roots[0], "root_record_index"),
        (result.effective_body_groups[0], "group_index"),
        (result.effective_body_groups[0], "representative_declaration_index"),
    )
    for value, field in scalar_paths:
        payload = value.model_dump(mode="python")
        payload[field] = True
        with pytest.raises(ValidationError):
            type(value).model_validate(payload)

    root = result.roots[0].model_dump(mode="python")
    for field in ("lineage_record_indices", "current_tip_indices",
                  "withdrawal_indices", "effective_body_group_indices"):
        payload = {**root, field: (True,)}
        with pytest.raises(ValidationError):
            kernel.BehaviorRuleRootResult.model_validate(payload)

    group = result.effective_body_groups[0].model_dump(mode="python")
    for field in ("current_tip_indices", "root_record_indices"):
        payload = {**group, field: (False,)}
        with pytest.raises(ValidationError):
            kernel.BehaviorEffectiveBodyGroupResult.model_validate(payload)


def test_complete_material_is_carried_once_and_rows_are_indices_only(tmp_path):
    result, _, _ = conflict_result(tmp_path)
    payload = result.model_dump_json()
    decoded = json.loads(payload)
    assert len(decoded["material"]["records"]) == \
        decoded["material"]["revision"]["record_count"]
    for record in decoded["material"]["records"]:
        assert payload.count(f'"record_id":"{record["record_id"]}"') == 1
    for row in (*decoded["roots"], *decoded["effective_body_groups"]):
        assert "material" not in row
        assert "evidence" not in row
        assert "authority" not in row


def test_query_and_result_modules_are_store_and_upper_layer_isolated():
    for filename in (
            "backend/model_kernel/queries.py",
            "backend/model_kernel/behavior_results.py"):
        path = Path(filename)
        assert path.exists()
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
        assert not any(name.startswith((
            "backend.model_state", "backend.temporal_state",
            "backend.identity_binding", "backend.semantic_compatibility",
            "backend.constraint_evaluation", "backend.source_interpretation",
            "backend.data_sources", "backend.behavior_evaluation",
        )) for name in imports)
        assert "ModelStore" not in imported_symbols
        assert not any(isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name)
                       and node.func.id == "ModelStore"
                       for node in ast.walk(tree))
        assert "sqlite3" not in source
        assert "Path(" not in source
        assert "open(" not in source
    assert not Path("backend/behavior_evaluation").exists()
