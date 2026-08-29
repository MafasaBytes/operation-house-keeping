"""PT-001 Slice A red baseline for pure, stable port identity."""

import ast
from pathlib import Path
from uuid import RFC_4122, UUID

import pytest
from pydantic import ValidationError

import backend.system_identity as identity


PORT = "prt_" + "a" * 32


def port(**overrides):
    fields = dict(
        anchor_id=PORT,
        namespace="demo-printer",
        display_name="Synthetic controller interface",
        role_name="controller-interface",
    )
    fields.update(overrides)
    return identity.PortAnchor(**fields)


def test_port_anchor_is_public_and_has_its_own_opaque_grammar():
    anchor = port()
    assert anchor.anchor_id == PORT
    assert identity.PORT_ANCHOR_ID_PATTERN == r"^prt_[0-9a-f]{32}$"


@pytest.mark.parametrize("bad_id", [
    "prt-" + "a" * 32,
    "prt_" + "A" * 32,
    "prt_" + "g" * 32,
    "prt_" + "a" * 31,
    "prt_" + "a" * 33,
    "ent_" + "a" * 32,
    "var_" + "a" * 32,
    "con_" + "a" * 32,
    "a" * 36,
])
def test_port_anchor_rejects_noncanonical_ids(bad_id):
    with pytest.raises(ValidationError):
        port(anchor_id=bad_id)


@pytest.mark.parametrize("field,value", [
    ("namespace", "Demo Printer"),
    ("namespace", "demo_printer"),
    ("namespace", ""),
    ("role_name", "Controller Interface"),
    ("display_name", ""),
])
def test_port_context_fields_use_the_existing_anchor_grammar(field, value):
    with pytest.raises(ValidationError):
        port(**{field: value})


def test_role_name_is_optional_and_names_are_not_identity():
    original = port()
    renamed = port(display_name="Renamed interface", role_name=None)
    assert renamed.anchor_id == original.anchor_id
    assert renamed.role_name is None


def test_port_anchor_is_frozen_and_has_exactly_the_accepted_fields():
    anchor = port()
    assert tuple(type(anchor).model_fields) == (
        "anchor_id", "namespace", "display_name", "role_name")
    with pytest.raises(ValidationError):
        anchor.display_name = "mutated"


@pytest.mark.parametrize("forbidden", [
    {"entity_anchor_id": "ent_" + "b" * 32},
    {"referent_kind": "physical_instance"},
    {"context": {"kind": "lifecycle_view", "view": "as_built"}},
    {"domain": "electrical"},
    {"direction": "output"},
    {"interface_type": "gpio"},
    {"unit": "volt"},
    {"compatible": True},
    {"flow": "active"},
    {"authority": "owner"},
])
def test_port_anchor_contains_no_owner_semantics_state_or_authority(forbidden):
    with pytest.raises(ValidationError):
        port(**forbidden)


def test_public_minter_emits_real_unique_uuid4_ids():
    anchors = tuple(
        identity.mint_port_anchor(
            namespace="demo-printer",
            display_name="Synthetic controller interface",
            role_name="controller-interface",
        )
        for _ in range(16)
    )
    assert len({anchor.anchor_id for anchor in anchors}) == len(anchors)
    for anchor in anchors:
        assert isinstance(anchor, identity.PortAnchor)
        parsed = UUID(hex=anchor.anchor_id.removeprefix("prt_"))
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_minter_delegates_context_validation_to_the_anchor_contract():
    with pytest.raises(ValidationError):
        identity.mint_port_anchor(
            namespace="bad namespace", display_name="", role_name="Bad Role")


def test_forged_port_anchor_is_fully_revalidated():
    forged = identity.PortAnchor.model_construct(
        anchor_id="prt_NOT_HEX",
        namespace="bad namespace",
        display_name="",
        role_name=None,
    )
    with pytest.raises(ValidationError):
        identity.PortAnchor.model_validate(forged)


def test_system_identity_exports_are_exact_after_pt001_identity_extension():
    assert identity.__all__ == [
        "BEHAVIOR_ANCHOR_ID_PATTERN",
        "CONSTRAINT_ANCHOR_ID_PATTERN",
        "ENTITY_ANCHOR_ID_PATTERN",
        "PORT_ANCHOR_ID_PATTERN",
        "VARIABLE_ANCHOR_ID_PATTERN",
        "BehaviorAnchor",
        "ConstraintAnchor",
        "EntityAnchor",
        "PortAnchor",
        "VariableAnchor",
        "mint_behavior_anchor",
        "mint_constraint_anchor",
        "mint_port_anchor",
    ]


def test_system_identity_remains_a_pure_value_namespace():
    package = Path(identity.__file__).parent
    sources = sorted(package.glob("*.py"))
    assert sources, "system_identity source scan must not be vacuous"
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported = [node.module or ""]
            else:
                continue
            for name in imported:
                assert not (
                    name.startswith("backend.")
                    and not name.startswith("backend.system_identity")
                ), f"{source.name} imports {name}"
        text = source.read_text(encoding="utf-8")
        for forbidden in (
            "Path(", "open(", "sqlite", "ModelStore", "BindingStore",
            "TemporalStore",
        ):
            assert forbidden not in text, f"{forbidden!r} in {source.name}"
