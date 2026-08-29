"""VP-001 Slice B authoritative reconstruction, non-inference, isolation reds."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel import ModelQueries, ModelStore
from tests.model_kernel.test_demo_model import (
    CN001_MEMBERSHIP, PRE_CN001_MEMBERSHIP, PRE_ES001_MEMBERSHIP,
    PRE_SPECIFICATION_MEMBERSHIP, PRE_VARIABLE_MEMBERSHIP, PT001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)
from tests.model_kernel.test_variable_port_records import (
    CONTEXT, PORT, VARIABLE, association, withdrawal,
)
from tests.model_kernel.test_variable_port_store import append_all, base
from tests.model_kernel.test_variable_port_store import PORT_B, port_record


DEMO_MODEL = Path("models/demo-printer")


def reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def result_world(tmp_path):
    root = association(note="root")
    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")
    return append_all(base(tmp_path), root, left, right), root, left, right


def test_exact_result_rejects_every_derived_and_material_forgery(tmp_path):
    store, root, left, right = result_world(tmp_path)
    result = ModelQueries(store.load()).variable_port_association(
        VARIABLE, PORT, context=CONTEXT)
    attacks = (
        lambda p: p.update(endpoint_status="port_not_registered"),
        lambda p: p.update(owner_alignment="different_owners"),
        lambda p: p.update(conclusion="inactive"),
        lambda p: p.update(lineage_summary="healthy"),
        lambda p: p.update(variable_registration_index=999),
        lambda p: p.update(variable_owner_registration_index=999),
        lambda p: p.update(port_registration_index=999),
        lambda p: p.update(port_owner_registration_index=999),
        lambda p: p.update(context={"kind": "lifecycle_view", "view": "as_built"}),
        lambda p: p["roots"][0].update(lineage_record_indices=()),
        lambda p: p["roots"][0].update(current_tip_indices=
                                        p["roots"][0]["current_tip_indices"][:1]),
        lambda p: p["roots"][0].update(withdrawal_indices=(0,)),
        lambda p: p["roots"][0].update(lineage_health="healthy"),
        lambda p: p["roots"][0].update(root_record_index=999),
        lambda p: p["material"].update(records=
                                         list(reversed(p["material"]["records"]))),
        lambda p: p["material"]["records"][0].update(note="stale id forgery"),
        lambda p: p["material"]["revision"].update(record_count=
            p["material"]["revision"]["record_count"] + 1),
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            reconstruct(result, attack)


def test_collection_rejects_missing_duplicate_reordered_substituted_entries(
        tmp_path):
    store = base(tmp_path)
    store.append(port_record(PORT_B))
    store.append(association())
    store.append(association(port_anchor_id=PORT_B, note="other port"))
    result = ModelQueries(store.load()).ports_associated_with_variable(
        VARIABLE, context=CONTEXT)
    attacks = (
        lambda p: p.update(entries=()),
        lambda p: p.update(entries=p["entries"] + p["entries"]),
        lambda p: p.update(entries=list(reversed(p["entries"]))),
        lambda p: p["entries"][0].update(entry_index=1),
        lambda p: p["entries"][0].update(port_anchor_id="prt_" + "9" * 32),
        lambda p: p["entries"][0].update(conclusion="inactive"),
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            reconstruct(result, attack)

    reverse = ModelQueries(store.load()).variables_associated_with_port(
        PORT, context=CONTEXT)
    reverse_attacks = (
        lambda p: p.update(status="port_not_registered"),
        lambda p: p.update(port_registration_index=None),
        lambda p: p.update(owner_registration_index=None),
        lambda p: p.update(entries=()),
        lambda p: p["entries"][0].update(variable_anchor_id=
                                           "var_" + "9" * 32),
    )
    for attack in reverse_attacks:
        with pytest.raises(ValidationError):
            reconstruct(reverse, attack)


def test_assertion_result_rejects_activity_health_root_and_link_forgery(
        tmp_path):
    store, root, left, right = result_world(tmp_path)
    result = ModelQueries(store.load()).variable_port_assertion(root.record_id)
    attacks = (
        lambda p: p.update(activity="current"),
        lambda p: p.update(containing_lineage_health="healthy"),
        lambda p: p.update(root_record_index=999),
        lambda p: p.update(successor_indices=()),
        lambda p: p.update(withdrawal_indices=(0,)),
        lambda p: p.update(record_id="vpa_" + "9" * 64),
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            reconstruct(result, attack)


def test_model_construct_and_copy_nested_rows_are_revalidated(tmp_path):
    result = ModelQueries(append_all(base(tmp_path), association()).load()
                          ).variable_port_association(
                              VARIABLE, PORT, context=CONTEXT)
    hostile_root = result.roots[0].model_copy(update={"lineage_health": "inactive"})
    hostiles = (
        result.model_copy(update={"conclusion": "inactive"}),
        type(result).model_construct(**{
            **result.model_dump(), "owner_alignment": "different_owners"}),
        result.model_copy(update={"roots": (hostile_root,)}),
    )
    for hostile in hostiles:
        with pytest.raises(ValidationError):
            type(result).model_validate(hostile)


def test_every_vp_result_index_rejects_boolean_coercion(tmp_path):
    result = ModelQueries(append_all(base(tmp_path), association()).load()
                          ).variable_port_association(
                              VARIABLE, PORT, context=CONTEXT)
    for field in (
        "variable_registration_index", "variable_owner_registration_index",
        "port_registration_index", "port_owner_registration_index",
    ):
        value = getattr(result, field)
        payload = result.model_dump(mode="python")
        payload[field] = bool(value)
        with pytest.raises(ValidationError):
            type(result).model_validate(payload)

    root_payload = result.roots[0].model_dump(mode="python")
    root_attacks = (
        {**root_payload, "root_record_index": True},
        {**root_payload, "lineage_record_indices": (True,)},
        {**root_payload, "current_tip_indices": (False,)},
        {**root_payload, "withdrawal_indices": (True,)},
    )
    for payload in root_attacks:
        with pytest.raises(ValidationError):
            kernel.VariablePortAssociationRootResult.model_validate(payload)

    collection = ModelQueries(append_all(
        base(tmp_path / "collection"), association()).load()
                              ).ports_associated_with_variable(
                                  VARIABLE, context=CONTEXT)
    entry_payload = collection.entries[0].model_dump(mode="python")
    for field in (
        "entry_index", "variable_registration_index",
        "variable_owner_registration_index", "port_registration_index",
        "port_owner_registration_index",
    ):
        payload = {**entry_payload, field: bool(entry_payload[field])}
        with pytest.raises(ValidationError):
            kernel.VariablePortAssociationEntry.model_validate(payload)

    disclosure = ModelQueries(append_all(
        base(tmp_path / "assertion"), association()).load()
                              ).variable_port_assertion(association().record_id)
    payload = disclosure.model_dump(mode="python")
    payload["record_index"] = True
    with pytest.raises(ValidationError):
        type(disclosure).model_validate(payload)


def test_material_serializes_each_complete_selected_record_once(tmp_path):
    store = append_all(base(tmp_path), association())
    result = ModelQueries(store.load()).ports_associated_with_variable(
        VARIABLE, context=CONTEXT)
    payload = result.model_dump_json()
    decoded = json.loads(payload)
    assert len(decoded["material"]["records"]) == len(store.load().records)
    for record in decoded["material"]["records"]:
        assert payload.count(f'"record_id":"{record["record_id"]}"') == 1
    assert "material" not in decoded["entries"][0]


def test_every_pre_vp_revision_answers_absence_without_inference():
    store = ModelStore(DEMO_MODEL)
    histories = (
        PRE_VARIABLE_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
        VS001_MEMBERSHIP, PRE_ES001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
        CN001_MEMBERSHIP, PT001_MEMBERSHIP,
    )
    for membership in histories:
        queries = ModelQueries(store.replay(membership))
        exact = queries.variable_port_association(
            VARIABLE, PORT, context=CONTEXT)
        assert exact.conclusion in {"not_evaluated", "not_declared"}
        assert exact.roots == ()
        assert queries.variable_port_assertion(
            "vpa_" + "9" * 64).lookup_status == "not_found"


def test_query_layer_owns_no_store_and_imports_no_upper_layer():
    assert "store" not in kernel.ModelQueries.__dict__
    for filename in ("backend/model_kernel/queries.py",
                     "backend/model_kernel/query_results.py"):
        path = Path(filename)
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        assert not any(name.startswith((
            "backend.model_state", "backend.temporal_state",
            "backend.identity_binding", "backend.structural_evidence",
            "backend.data_sources")) for name in imports)
    assert not Path("backend/variable_port_association").exists()
