"""Owner-resolved public VariableAnchor minter contract and purity gates."""

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


OWNER = "ent_" + "a" * 32


def mint(**overrides):
    fields = dict(
        entity_anchor_id=OWNER,
        namespace="demo-printer",
        display_name="Synthetic comparison variable",
        role_name=None,
    )
    fields.update(overrides)
    return identity.mint_variable_anchor(**fields)


def test_exact_keyword_only_signature_and_return_contract():
    signature = inspect.signature(identity.mint_variable_anchor)
    assert tuple(signature.parameters) == (
        "entity_anchor_id", "namespace", "display_name", "role_name")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert signature.parameters["entity_anchor_id"].annotation is str
    assert signature.parameters["namespace"].annotation is str
    assert signature.parameters["display_name"].annotation is str
    assert signature.parameters["role_name"].annotation == str | None
    assert signature.parameters["role_name"].default is None
    assert signature.return_annotation is identity.VariableAnchor

    value = mint()
    assert type(value) is identity.VariableAnchor
    assert tuple(type(value).model_fields) == (
        "anchor_id", "entity_anchor_id", "namespace", "display_name",
        "role_name")


def test_real_calls_emit_distinct_rfc4122_uuid4_lowercase_ids():
    values = tuple(mint() for _ in range(16))
    assert len({value.anchor_id for value in values}) == 16
    for value in values:
        assert value.anchor_id.startswith("var_")
        suffix = value.anchor_id.removeprefix("var_")
        assert len(suffix) == 32
        assert suffix == suffix.lower()
        assert set(suffix) <= set("0123456789abcdef")
        parsed = UUID(hex=suffix)
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_exactly_one_uuid_hex_is_used_and_fields_are_preserved(monkeypatch):
    class FrozenUuid:
        hex = "1234567890abcdef1234567890abcdef"

    calls = []

    def fake_uuid4():
        calls.append(None)
        return FrozenUuid()

    monkeypatch.setattr(minting, "uuid4", fake_uuid4)
    value = identity.mint_variable_anchor(
        entity_anchor_id=OWNER,
        namespace="demo-printer",
        display_name="Synthetic comparison variable",
        role_name="comparison-variable",
    )
    assert calls == [None]
    assert value.model_dump(mode="json") == {
        "anchor_id": "var_1234567890abcdef1234567890abcdef",
        "entity_anchor_id": OWNER,
        "namespace": "demo-printer",
        "display_name": "Synthetic comparison variable",
        "role_name": "comparison-variable",
    }


@pytest.mark.parametrize(("field", "value"), [
    ("entity_anchor_id", "var_" + "a" * 32),
    ("entity_anchor_id", "ent_" + "A" * 32),
    ("entity_anchor_id", True),
    ("entity_anchor_id", 1),
    ("namespace", "Demo Printer"),
    ("namespace", "demo_printer"),
    ("namespace", ""),
    ("namespace", True),
    ("display_name", ""),
    ("display_name", None),
    ("display_name", True),
    ("role_name", "Comparison Variable"),
    ("role_name", "comparison_variable"),
    ("role_name", True),
])
def test_invalid_and_coercive_fields_reject_through_existing_contract(field, value):
    with pytest.raises(ValidationError):
        mint(**{field: value})


def test_positional_and_extra_arguments_are_rejected():
    with pytest.raises(TypeError):
        identity.mint_variable_anchor(
            OWNER, "demo-printer", "Synthetic comparison variable")
    with pytest.raises(TypeError):
        mint(unit="degree_celsius")


def test_minter_has_no_io_store_network_environment_or_backend_dependency(monkeypatch):
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
        "ModelStore", "BindingStore", "TemporalStore", "sqlite3", "socket",
        "subprocess", "requests", "urllib", "environ", "getenv", "open(",
        "write_text", "write_bytes", "mkdir", "replace(",
    ):
        assert forbidden not in source

    def forbidden(*args, **kwargs):
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(os, "getenv", forbidden)
    value = mint()
    assert isinstance(value, identity.VariableAnchor)


def test_public_surface_grows_by_exactly_one_ordered_name():
    assert identity.__all__ == [
        "BEHAVIOR_ANCHOR_ID_PATTERN",
        "CONSTRAINT_ANCHOR_ID_PATTERN",
        "ENTITY_ANCHOR_ID_PATTERN",
        "PORT_ANCHOR_ID_PATTERN",
        "STATE_ANCHOR_ID_PATTERN",
        "VARIABLE_ANCHOR_ID_PATTERN",
        "BehaviorAnchor",
        "ConstraintAnchor",
        "EntityAnchor",
        "PortAnchor",
        "StateAnchor",
        "VariableAnchor",
        "mint_behavior_anchor",
        "mint_constraint_anchor",
        "mint_port_anchor",
        "mint_state_anchor",
        "mint_variable_anchor",
    ]
