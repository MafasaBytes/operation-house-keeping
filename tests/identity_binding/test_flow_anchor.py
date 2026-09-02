"""FL-001 Slice A red-first contracts for opaque logical flow identity."""

import ast
import builtins
import inspect
import os
from pathlib import Path
import socket
from uuid import RFC_4122, UUID

import pytest
from pydantic import ValidationError

import backend.system_identity as identity
import backend.system_identity.minting as minting


FLOW = "flo_" + "a" * 32


def anchor(**overrides):
    fields = dict(
        anchor_id=FLOW,
        namespace="test-model",
        display_name="Synthetic logical flow",
        role_name="synthetic-flow",
    )
    fields.update(overrides)
    return identity.FlowAnchor(**fields)


def test_flow_anchor_exact_contract_grammar_and_revalidation():
    value = anchor()
    assert identity.FLOW_ANCHOR_ID_PATTERN == r"^flo_[0-9a-f]{32}$"
    assert tuple(type(value).model_fields) == (
        "anchor_id", "namespace", "display_name", "role_name")
    forged = identity.FlowAnchor.model_construct(
        anchor_id="flo_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    with pytest.raises(ValidationError):
        identity.FlowAnchor.model_validate(forged)


@pytest.mark.parametrize("bad_id", [
    "flo_" + "A" * 32,
    "flo_" + "a" * 31,
    "flo_" + "a" * 33,
    "trn_" + "a" * 32,
    "flo_" + "g" * 32,
    True,
    1,
])
def test_flow_anchor_rejects_noncanonical_and_coercive_ids(bad_id):
    with pytest.raises(ValidationError):
        anchor(anchor_id=bad_id)


def test_flow_anchor_is_frozen_extra_forbidden_and_meaning_free():
    value = anchor()
    with pytest.raises(ValidationError):
        value.display_name = "mutated"
    for forbidden in (
        {"source_port_anchor_ids": ("prt_" + "a" * 32,)},
        {"sink_port_anchor_ids": ("prt_" + "b" * 32,)},
        {"flow_kind": "material"},
        {"connection_anchor_id": "cnn_" + "a" * 32},
        {"mechanism": "pipe"},
        {"occurrence": True},
        {"active": True},
        {"rate": "1"},
    ):
        with pytest.raises(ValidationError):
            anchor(**forbidden)


def test_nested_flow_anchor_forgery_is_rejected():
    forged = anchor().model_copy(update={"physical_mechanism": "forged"})
    with pytest.raises(ValidationError):
        identity.FlowAnchor.model_validate(forged)


def test_names_neither_merge_distinct_ids_nor_split_one_opaque_id():
    first = anchor(display_name="same", role_name="same")
    distinct = anchor(
        anchor_id="flo_" + "b" * 32,
        display_name="same", role_name="same")
    renamed = anchor(display_name="different", role_name="different")
    assert first.anchor_id != distinct.anchor_id
    assert first.anchor_id == renamed.anchor_id
    assert first != renamed


def test_minter_is_keyword_only_calls_uuid4_once_and_preserves_fields(
        monkeypatch):
    signature = inspect.signature(identity.mint_flow_anchor)
    assert tuple(signature.parameters) == (
        "namespace", "display_name", "role_name")
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY
               for parameter in signature.parameters.values())

    class FrozenUuid:
        hex = "1234567890abcdef1234567890abcdef"

    calls = []

    def fake_uuid4():
        calls.append(None)
        return FrozenUuid()

    monkeypatch.setattr(minting, "uuid4", fake_uuid4)
    value = identity.mint_flow_anchor(
        namespace="test-model", display_name="Synthetic logical flow",
        role_name="synthetic-flow")
    assert calls == [None]
    assert value.model_dump(mode="json") == {
        "anchor_id": "flo_1234567890abcdef1234567890abcdef",
        "namespace": "test-model",
        "display_name": "Synthetic logical flow",
        "role_name": "synthetic-flow",
    }


def test_minter_has_no_io_store_network_environment_or_backend_dependency(
        monkeypatch):
    source = Path(minting.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert imported == ["uuid", "backend.system_identity.anchors"]
    for forbidden in (
        "ModelStore", "FlowRegistration", "sqlite3", "subprocess",
        "requests", "urllib", "environ", "getenv", "open(",
        "write_text", "write_bytes", "mkdir", "replace(",
    ):
        assert forbidden not in source

    def forbidden(*args, **kwargs):
        raise AssertionError("flow minter performed a forbidden side effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(os, "getenv", forbidden)
    value = identity.mint_flow_anchor(
        namespace="test-model", display_name="Synthetic logical flow")
    assert isinstance(value, identity.FlowAnchor)


def test_minter_emits_distinct_rfc4122_uuid4_lowercase_ids():
    values = tuple(identity.mint_flow_anchor(
        namespace="test-model", display_name="Synthetic logical flow")
        for _ in range(12))
    assert len({value.anchor_id for value in values}) == len(values)
    for value in values:
        suffix = value.anchor_id.removeprefix("flo_")
        parsed = UUID(hex=suffix)
        assert suffix == suffix.lower()
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_flow_identity_public_surface_is_exact_and_has_no_connection_anchor():
    assert identity.__all__ == [
        "BEHAVIOR_ANCHOR_ID_PATTERN",
        "CONSTRAINT_ANCHOR_ID_PATTERN",
        "ENTITY_ANCHOR_ID_PATTERN",
        "FLOW_ANCHOR_ID_PATTERN",
        "PORT_ANCHOR_ID_PATTERN",
        "STATE_ANCHOR_ID_PATTERN",
        "TRANSITION_ANCHOR_ID_PATTERN",
        "VARIABLE_ANCHOR_ID_PATTERN",
        "BehaviorAnchor",
        "ConstraintAnchor",
        "EntityAnchor",
        "FlowAnchor",
        "PortAnchor",
        "StateAnchor",
        "TransitionAnchor",
        "VariableAnchor",
        "mint_behavior_anchor",
        "mint_constraint_anchor",
        "mint_flow_anchor",
        "mint_port_anchor",
        "mint_state_anchor",
        "mint_transition_anchor",
        "mint_variable_anchor",
    ]
    for forbidden in (
        "ConnectionAnchor", "mint_connection_anchor", "FlowOccurrence",
        "FlowAssessment",
    ):
        assert forbidden not in identity.__all__
        assert not hasattr(identity, forbidden)
