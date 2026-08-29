"""VP-001 Slice C red baseline: authoritative boundary and preservation."""

import ast
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_state as model_state
from tests.model_kernel.test_demo_model import (
    CURRENT_REVISION, PRE_VP001_REVISION, PT001_MEMBERSHIP,
    VP001_MEMBERSHIP, VP001_MODEL_RECORDS,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES, ARTIFACT_SHA256, _artifact_bytes,
)
from tests.model_state.helpers import AS_OF, E1, PROP_TEMP, SUBJECT, V1
from tests.model_state.vp001_slice_c_helpers import (
    CONTEXT, P_ASSOCIATED, V_UNKNOWN, slice_c_world,
)
from tests.model_state.helpers import E2


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


@pytest.mark.parametrize("attack", (
    "requested_entity_registration",
    "binding_declared_anchor",
    "candidate_locator",
    "candidate_declaration_locator",
    "resolution_locator",
    "occurrence_locator",
    "resolution_target",
    "citation_outside_revision",
    "resolution_citation_outside_revision",
    "discovery_target_substitution",
    "nested_cutoff",
    "observation_after_cutoff",
    "boolean_count",
))
def test_outer_rejects_nested_provenance_and_coercion_substitution(
        tmp_path, attack):
    result = _result(slice_c_world(tmp_path))
    payload = result.model_dump(mode="python")
    state = payload["variable_state"]
    if attack == "requested_entity_registration":
        state["requested_entity_registration"] = next(
            record for record in payload["association"]["material"]["records"]
            if record["record_kind"] == "entity_registration"
            and record["anchor"]["anchor_id"] == E2)
    elif attack == "binding_declared_anchor":
        state["binding_declared_anchor"]["anchor_id"] = V_UNKNOWN
        state["anchor_agreement"] = "divergent"
        state["divergent_anchor_fields"] = ("anchor_id",)
        state["candidates"][0]["attachment"] = \
            "not_attachable_anchor_divergent"
    elif attack == "candidate_locator":
        state["candidates"][0]["subject"]["subject_identifier"] = \
            "forged-other-subject"
    elif attack == "candidate_declaration_locator":
        state["candidates"][0]["declaration"]["subject"][
            "subject_identifier"] = "forged-declaration-subject"
    elif attack == "resolution_locator":
        state["candidates"][0]["bound"]["resolution"]["locator_subject"][
            "subject_identifier"] = "forged-resolution-subject"
    elif attack == "occurrence_locator":
        state["candidates"][0]["bound"]["observed"]["occurrence"][
            "subject"]["subject_identifier"] = "forged-occurrence-subject"
    elif attack == "resolution_target":
        state["candidates"][0]["bound"]["resolution"]["resolved_target"][
            "display_name"] = "Forged resolution target"
    elif attack == "citation_outside_revision":
        forged_id = "iba_" + "0" * 64
        state["candidates"][0]["declaration"]["assertion_summaries"][0][
            "record_id"] = forged_id
        state["candidates"][0]["declared_via_assertion_ids"] = (forged_id,)
    elif attack == "resolution_citation_outside_revision":
        state["candidates"][0]["bound"]["resolution"]["via_assertions"][0][
            "record_id"] = "iba_" + "0" * 64
    elif attack == "discovery_target_substitution":
        state["candidates"][0]["declaration"]["assertion_summaries"][0][
            "target_anchor_id"] = V_UNKNOWN
        state["candidates"][0]["declared_via_assertion_ids"] = ()
    elif attack == "nested_cutoff":
        state["candidates"][0]["bound"]["observed"]["as_of"] = \
            "2026-09-01T00:00:00Z"
    elif attack == "observation_after_cutoff":
        payload["as_of"] = "2026-08-07T19:00:00Z"
        state["as_of"] = "2026-08-07T19:00:00Z"
        state["candidates"][0]["bound"]["observed"]["as_of"] = \
            "2026-08-07T19:00:00Z"
    else:
        state["declared_locator_count"] = True
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)


def test_outer_rejects_forged_explicit_selector_declaration_classification(
        tmp_path):
    world = slice_c_world(tmp_path)
    result = world.queries.associated_port_variable_state(
        V1, P_ASSOCIATED, context=CONTEXT, as_of=AS_OF,
        entity_anchor_id=E1,
        source=model_state.SourceSelector(subject=SUBJECT, property=PROP_TEMP))
    payload = result.model_dump(mode="python")
    state = payload["variable_state"]
    state["candidates"][0]["declaration"]["assertion_summaries"][0][
        "target_anchor_id"] = V_UNKNOWN
    state["candidates"][0]["declared_via_assertion_ids"] = ()
    # This classification still claims the declaration targets V1.
    assert state["selector_declaration"] == \
        "ever_declared_for_requested_variable"
    with pytest.raises(ValidationError):
        type(result).model_validate(payload)


@pytest.mark.parametrize("attack", (
    lambda p: p.update(variable_anchor_id=True),
    lambda p: p.update(port_anchor_id=True),
    lambda p: p.update(as_of=True),
    lambda p: p.update(status=True),
    lambda p: p["association"].update(variable_registration_index=True),
    lambda p: p["association"]["roots"][0].update(
        current_tip_indices=(True,)),
))
def test_outer_rejects_boolean_and_scalar_coercions(tmp_path, attack):
    result = _result(slice_c_world(tmp_path))
    with pytest.raises(ValidationError):
        _reconstruct(result, attack)


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
    assert len(paths) == 29
    assert [path.stem for path in paths if path.name.startswith("vpa_")] == \
        list(VP001_MODEL_RECORDS)
    assert not any(path.name.startswith("vpw_") for path in paths)
    from backend.model_kernel import ModelStore
    store = ModelStore(DEMO)
    assert store.load().revision.revision_id == CURRENT_REVISION
    assert store.load().revision.record_ids == VP001_MEMBERSHIP
    historical = store.replay(PT001_MEMBERSHIP)
    assert historical.revision.revision_id == PRE_VP001_REVISION
    assert not historical.variable_port_associations
    artifact = _artifact_bytes()
    assert len(artifact) == ARTIFACT_BYTES
    assert hashlib.sha256(artifact).hexdigest() == ARTIFACT_SHA256
