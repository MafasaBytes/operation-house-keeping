"""ST-001 Slice A red-first contracts for opaque state identity."""

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


STATE = "sta_" + "a" * 32


def anchor(**overrides):
    fields = dict(
        anchor_id=STATE,
        namespace="demo-printer",
        display_name="Synthetic constraint-match state",
        role_name="synthetic-state",
    )
    fields.update(overrides)
    return identity.StateAnchor(**fields)


def mint(**overrides):
    fields = dict(
        namespace="demo-printer",
        display_name="Synthetic constraint-match state",
        role_name=None,
    )
    fields.update(overrides)
    return identity.mint_state_anchor(**fields)


def test_state_anchor_exact_contract_and_grammar():
    value = anchor()
    assert identity.STATE_ANCHOR_ID_PATTERN == r"^sta_[0-9a-f]{32}$"
    assert tuple(type(value).model_fields) == (
        "anchor_id", "namespace", "display_name", "role_name")
    assert value.anchor_id == STATE


@pytest.mark.parametrize("bad_id", [
    "sta-" + "a" * 32,
    "sta_" + "A" * 32,
    "sta_" + "a" * 31,
    "sta_" + "a" * 33,
    "st_" + "a" * 32,
    "bhv_" + "a" * 32,
    "con_" + "a" * 32,
    "sta_" + "g" * 32,
    True,
    1,
])
def test_state_anchor_rejects_noncanonical_and_coercive_ids(bad_id):
    with pytest.raises(ValidationError):
        anchor(anchor_id=bad_id)


def test_state_anchor_is_frozen_extra_forbidden_and_meaning_free():
    value = anchor()
    with pytest.raises(ValidationError):
        value.display_name = "mutated"
    for forbidden in (
        {"subject_entity_anchor_id": "ent_" + "a" * 32},
        {"condition_constraint_anchor_ids": ("con_" + "a" * 32,)},
        {"context": {"kind": "view_independent"}},
        {"lifecycle": "declared"},
        {"state_result": "matches"},
        {"transition": "next"},
        {"evidence": ()},
        {"authority": "owner"},
    ):
        with pytest.raises(ValidationError):
            anchor(**forbidden)


def test_state_anchor_names_never_participate_in_identity():
    renamed = anchor(display_name="Renamed synthetic state", role_name=None)
    assert renamed.anchor_id == anchor().anchor_id


def test_state_anchor_revalidates_model_construct_and_model_copy():
    forged = identity.StateAnchor.model_construct(
        anchor_id="sta_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    with pytest.raises(ValidationError):
        identity.StateAnchor.model_validate(forged)

    copied = anchor().model_copy(update={"namespace": "bad namespace"})
    with pytest.raises(ValidationError):
        identity.StateAnchor.model_validate(copied)


def test_mint_state_anchor_has_exact_keyword_only_signature():
    signature = inspect.signature(identity.mint_state_anchor)
    assert tuple(signature.parameters) == (
        "namespace", "display_name", "role_name")
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY
               for parameter in signature.parameters.values())
    assert signature.parameters["namespace"].annotation is str
    assert signature.parameters["display_name"].annotation is str
    assert signature.parameters["role_name"].annotation == str | None
    assert signature.parameters["role_name"].default is None
    assert signature.return_annotation is identity.StateAnchor


def test_mint_state_anchor_emits_distinct_rfc4122_uuid4_lowercase_ids():
    values = tuple(mint() for _ in range(16))
    assert len({value.anchor_id for value in values}) == 16
    for value in values:
        suffix = value.anchor_id.removeprefix("sta_")
        assert len(suffix) == 32
        assert suffix == suffix.lower()
        assert set(suffix) <= set("0123456789abcdef")
        parsed = UUID(hex=suffix)
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_minter_calls_uuid4_once_and_preserves_fields(monkeypatch):
    class FrozenUuid:
        hex = "1234567890abcdef1234567890abcdef"

    calls = []

    def fake_uuid4():
        calls.append(None)
        return FrozenUuid()

    monkeypatch.setattr(minting, "uuid4", fake_uuid4)
    value = identity.mint_state_anchor(
        namespace="demo-printer",
        display_name="Synthetic constraint-match state",
        role_name="synthetic-state",
    )
    assert calls == [None]
    assert value.model_dump(mode="json") == {
        "anchor_id": "sta_1234567890abcdef1234567890abcdef",
        "namespace": "demo-printer",
        "display_name": "Synthetic constraint-match state",
        "role_name": "synthetic-state",
    }


@pytest.mark.parametrize(("field", "value"), [
    ("namespace", "Demo Printer"),
    ("namespace", "demo_printer"),
    ("namespace", ""),
    ("namespace", True),
    ("display_name", ""),
    ("display_name", None),
    ("display_name", True),
    ("role_name", "Synthetic State"),
    ("role_name", "synthetic_state"),
    ("role_name", True),
])
def test_minter_rejects_invalid_and_coercive_fields(field, value):
    with pytest.raises(ValidationError):
        mint(**{field: value})


def test_minter_rejects_positional_and_extra_arguments():
    with pytest.raises(TypeError):
        identity.mint_state_anchor("demo-printer", "Synthetic state")
    with pytest.raises(TypeError):
        mint(subject_entity_anchor_id="ent_" + "a" * 32)


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
    assert isinstance(mint(), identity.StateAnchor)


def test_system_identity_public_surface_adds_exact_state_names_in_order():
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
