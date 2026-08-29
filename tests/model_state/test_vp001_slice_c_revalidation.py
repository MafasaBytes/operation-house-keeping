"""VP-001 Slice C red baseline: authoritative boundary and preservation."""

import ast
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_state as model_state
from tests.model_kernel.test_demo_model import CURRENT_REVISION
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES, ARTIFACT_SHA256, _artifact_bytes,
)
from tests.model_state.helpers import AS_OF, E1, V1
from tests.model_state.vp001_slice_c_helpers import (
    CONTEXT, P_ASSOCIATED, slice_c_world,
)


DEMO = Path("models/demo-printer")


def _result(world):
    return world.queries.associated_port_variable_state(
        V1, P_ASSOCIATED, context=CONTEXT, as_of=AS_OF,
        entity_anchor_id=E1)


def _reconstruct(result, mutate):
    payload = result.model_dump(mode="python")
    mutate(payload)
    return type(result).model_validate(payload)


def test_outer_rejects_every_echo_status_revision_and_extra_forgery(tmp_path):
    result = _result(slice_c_world(tmp_path))
    attacks = (
        lambda p: p.update(variable_anchor_id="var_" + "8" * 32),
        lambda p: p.update(port_anchor_id="prt_" + "8" * 32),
        lambda p: p.update(context={"kind": "lifecycle_view",
                                    "view": "as_built"}),
        lambda p: p.update(as_of="2026-08-07T22:59:59+00:00"),
        lambda p: p.update(status="association_inactive"),
        lambda p: p.update(extra_field="forged"),
        lambda p: p["association"].update(conclusion="inactive"),
        lambda p: p["association"].update(lineage_summary="inactive"),
        lambda p: p["association"]["roots"][0].update(
            current_tip_indices=()),
        lambda p: p["association"]["material"]["records"][0].update(
            note="stale content id"),
        lambda p: p["variable_state"].update(
            variable_anchor_id="var_" + "8" * 32),
        lambda p: p["variable_state"].update(as_of="2026-08-07T22:00:00Z"),
        lambda p: p["variable_state"].update(model_membership="not_registered"),
        lambda p: p["variable_state"].update(model_revision={
            **p["variable_state"]["model_revision"],
            "revision_id": "mrv_" + "0" * 64,
        }),
    )
    for attack in attacks:
        with pytest.raises(ValidationError):
            _reconstruct(result, attack)


def test_model_copy_construct_and_nested_instance_forgeries_are_rejected(
        tmp_path):
    result = _result(slice_c_world(tmp_path))
    hostile_association = result.association.model_copy(
        update={"conclusion": "inactive"})
    hostile_state = result.variable_state.model_copy(
        update={"as_of": result.as_of.replace(hour=22)})
    hostiles = (
        result.model_copy(update={"status": "association_inactive"}),
        type(result).model_construct(**{
            **result.model_dump(), "port_anchor_id": "prt_" + "8" * 32}),
        result.model_copy(update={"association": hostile_association}),
        result.model_copy(update={"variable_state": hostile_state}),
    )
    for hostile in hostiles:
        with pytest.raises(ValidationError):
            type(result).model_validate(hostile)


def test_serialized_composition_carries_each_nested_result_once(tmp_path):
    payload = json.loads(_result(slice_c_world(tmp_path)).model_dump_json())
    assert set(payload) == {
        "variable_anchor_id", "port_anchor_id", "context", "as_of", "status",
        "association", "variable_state",
    }
    assert "association" not in payload["variable_state"]
    assert "variable_state" not in payload["association"]
    assert "material" not in payload["variable_state"]
    assert set(key for key in payload if key in (
        "association", "variable_state")) == {"association", "variable_state"}


def test_slice_c_import_direction_read_only_scope_and_non_inference_words():
    allowed = (
        "backend.model_state", "backend.model_kernel",
        "backend.system_identity", "backend.identity_binding",
        "backend.temporal_state",
    )
    for filename in (
        "backend/model_state/contracts.py", "backend/model_state/facade.py",
    ):
        source = Path(filename).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        backend_imports = [name for name in imports
                           if name.startswith("backend.")]
        assert all(name.startswith(allowed) for name in backend_imports)
        # Local list assembly is expected in the existing facade; forbid
        # repository/store construction and mutation specifically.
        assert "ModelStore" not in source
        assert ".model.append(" not in source
        assert ".store.append(" not in source
        assert ".replay(" not in source
        assert "write_text(" not in source
        assert "write_bytes(" not in source
        assert "sqlite3" not in source
    for path in Path("backend/model_kernel").glob("*.py"):
        assert "backend.model_state" not in path.read_text(encoding="utf-8")
    assert not Path("backend/associated_port_variable_state").exists()

    result = getattr(model_state, "AssociatedPortVariableStateResult")
    implication_terms = (
        "observed_at_port", "port_value", "signal", "flow", "causality",
        "influence", "control", "compatibility", "safety", "behavior",
    )
    assert not any(term in result.model_fields for term in implication_terms)


def test_committed_ledgers_and_accepted_pt_artifact_remain_unchanged():
    paths = sorted((DEMO / "records").glob("*.json"))
    assert len(paths) == 28
    assert not any(path.name.startswith(("vpa_", "vpw_")) for path in paths)
    from backend.model_kernel import ModelStore
    assert ModelStore(DEMO).load().revision.revision_id == CURRENT_REVISION
    artifact = _artifact_bytes()
    assert len(artifact) == ARTIFACT_BYTES
    assert hashlib.sha256(artifact).hexdigest() == ARTIFACT_SHA256
