"""CN-001 Group 2 red baseline for stable constraint identity."""

from uuid import RFC_4122, UUID

import pytest
from pydantic import ValidationError

from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN,
    ConstraintAnchor,
    mint_constraint_anchor,
)


CON = "con_" + "a" * 32


def constraint(**overrides):
    fields = dict(
        anchor_id=CON,
        namespace="demo-printer",
        display_name="Safe hotend temperature",
        role_name="hotend-temperature-limit",
    )
    fields.update(overrides)
    return ConstraintAnchor(**fields)


def test_constraint_anchor_is_public_and_has_its_own_opaque_grammar():
    anchor = constraint()
    assert anchor.anchor_id == CON
    assert CONSTRAINT_ANCHOR_ID_PATTERN == r"^con_[0-9a-f]{32}$"


@pytest.mark.parametrize("bad_id", [
    "con-" + "a" * 32,
    "con_" + "A" * 32,
    "con_" + "a" * 31,
    "con_" + "a" * 33,
    "ent_" + "a" * 32,
    "var_" + "a" * 32,
    "a" * 36,
])
def test_constraint_anchor_rejects_noncanonical_ids(bad_id):
    with pytest.raises(ValidationError):
        constraint(anchor_id=bad_id)


def test_public_minter_emits_real_unique_uuid4_ids():
    anchors = tuple(
        mint_constraint_anchor(
            namespace="demo-printer",
            display_name="Safe hotend temperature",
            role_name="hotend-temperature-limit",
        )
        for _ in range(16)
    )
    assert len({anchor.anchor_id for anchor in anchors}) == len(anchors)
    for anchor in anchors:
        parsed = UUID(hex=anchor.anchor_id.removeprefix("con_"))
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


@pytest.mark.parametrize("field,value", [
    ("namespace", "Demo Printer"),
    ("namespace", "demo_printer"),
    ("namespace", ""),
    ("role_name", "Hotend Limit"),
    ("display_name", ""),
])
def test_constraint_context_fields_use_existing_anchor_grammar(field, value):
    with pytest.raises(ValidationError):
        constraint(**{field: value})


def test_constraint_anchor_is_frozen_minimal_and_names_are_not_identity():
    anchor = constraint()
    renamed = constraint(display_name="Renamed", role_name=None)
    assert renamed.anchor_id == anchor.anchor_id
    with pytest.raises(ValidationError):
        anchor.display_name = "mutated"
    for forbidden in (
        {"entity_anchor_id": "ent_" + "b" * 32},
        {"variable_anchor_id": "var_" + "b" * 32},
        {"unit": "Cel"},
        {"predicate": "less_than"},
        {"severity": "critical"},
    ):
        with pytest.raises(ValidationError):
            constraint(**forbidden)


def test_forged_constraint_anchor_is_revalidated():
    forged = ConstraintAnchor.model_construct(
        anchor_id="con_NOT_HEX",
        namespace="bad namespace",
        display_name="",
        role_name=None,
    )
    with pytest.raises(ValidationError):
        ConstraintAnchor.model_validate(forged)
