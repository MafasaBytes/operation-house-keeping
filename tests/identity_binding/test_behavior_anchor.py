"""BH-001 Slice A red-first tests for stable, meaning-free behavior identity."""

from uuid import RFC_4122, UUID

import pytest
from pydantic import ValidationError

import backend.system_identity as identity


BHV = "bhv_" + "a" * 32


def anchor(**overrides):
    fields = dict(
        anchor_id=BHV,
        namespace="demo-printer",
        display_name="Synthetic equality behavior",
        role_name="synthetic-equality",
    )
    fields.update(overrides)
    return identity.BehaviorAnchor(**fields)


def test_behavior_anchor_has_exact_opaque_contract_and_public_grammar():
    value = anchor()
    assert tuple(type(value).model_fields) == (
        "anchor_id", "namespace", "display_name", "role_name")
    assert identity.BEHAVIOR_ANCHOR_ID_PATTERN == r"^bhv_[0-9a-f]{32}$"
    assert value.anchor_id == BHV


@pytest.mark.parametrize("bad_id", [
    "bhv-" + "a" * 32,
    "bhv_" + "A" * 32,
    "bhv_" + "a" * 31,
    "bhv_" + "a" * 33,
    "beh_" + "a" * 32,
    "con_" + "a" * 32,
    "var_" + "a" * 32,
])
def test_behavior_anchor_rejects_every_noncanonical_identity_shape(bad_id):
    with pytest.raises(ValidationError):
        anchor(anchor_id=bad_id)


def test_behavior_anchor_is_frozen_extra_forbidden_and_meaning_free():
    value = anchor()
    with pytest.raises(ValidationError):
        value.display_name = "mutated"
    for forbidden in (
        {"owner_entity_anchor_id": "ent_" + "a" * 32},
        {"participant_variable_anchor_ids": ("var_" + "a" * 32,)},
        {"context": {"kind": "view_independent"}},
        {"rule": "exact_numeric_equality"},
        {"direction": "input_to_output"},
        {"port_anchor_id": "prt_" + "a" * 32},
        {"evidence": ()},
    ):
        with pytest.raises(ValidationError):
            anchor(**forbidden)


def test_behavior_anchor_names_are_human_context_not_identity():
    renamed = anchor(display_name="Renamed behavior", role_name=None)
    assert renamed.anchor_id == anchor().anchor_id


def test_behavior_anchor_revalidates_model_construct_and_model_copy():
    forged = identity.BehaviorAnchor.model_construct(
        anchor_id="bhv_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    with pytest.raises(ValidationError):
        identity.BehaviorAnchor.model_validate(forged)

    copied = anchor().model_copy(update={"namespace": "bad namespace"})
    with pytest.raises(ValidationError):
        identity.BehaviorAnchor.model_validate(copied)


def test_behavior_anchor_minter_emits_unique_real_uuid4_values():
    values = tuple(identity.mint_behavior_anchor(
        namespace="demo-printer", display_name="Synthetic equality behavior",
        role_name=None) for _ in range(16))
    assert len({value.anchor_id for value in values}) == 16
    for value in values:
        parsed = UUID(hex=value.anchor_id.removeprefix("bhv_"))
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_system_identity_public_surface_is_exact_after_slice_a():
    expected = {
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
    }
    assert len(identity.__all__) == len(expected)
    assert set(identity.__all__) == expected
