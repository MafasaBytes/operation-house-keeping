"""ST-002 Slice A red-first contracts for opaque transition identity."""

import inspect
from uuid import RFC_4122, UUID

import pytest
from pydantic import ValidationError

import backend.system_identity as identity
import backend.system_identity.minting as minting


TRANSITION = "trn_" + "a" * 32


def anchor(**overrides):
    fields = dict(
        anchor_id=TRANSITION, namespace="test-model",
        display_name="Synthetic transition", role_name="synthetic-transition")
    fields.update(overrides)
    return identity.TransitionAnchor(**fields)


def test_transition_anchor_exact_contract_grammar_and_revalidation():
    value = anchor()
    assert identity.TRANSITION_ANCHOR_ID_PATTERN == r"^trn_[0-9a-f]{32}$"
    assert tuple(type(value).model_fields) == (
        "anchor_id", "namespace", "display_name", "role_name")
    forged = identity.TransitionAnchor.model_construct(
        anchor_id="trn_NOT_HEX", namespace="bad namespace",
        display_name="", role_name=None)
    with pytest.raises(ValidationError):
        identity.TransitionAnchor.model_validate(forged)


@pytest.mark.parametrize("bad_id", [
    "trn_" + "A" * 32, "trn_" + "a" * 31, "trn_" + "a" * 33,
    "sta_" + "a" * 32, "trn_" + "g" * 32, True, 1,
])
def test_transition_anchor_rejects_noncanonical_and_coercive_ids(bad_id):
    with pytest.raises(ValidationError):
        anchor(anchor_id=bad_id)


def test_transition_anchor_is_frozen_extra_forbidden_and_meaning_free():
    value = anchor()
    with pytest.raises(ValidationError):
        value.display_name = "mutated"
    for forbidden in (
        {"subject_entity_anchor_id": "ent_" + "a" * 32},
        {"from_state_anchor_id": "sta_" + "a" * 32},
        {"to_state_anchor_id": "sta_" + "b" * 32},
        {"trigger": "change"}, {"occurrence": True}, {"outcome": "matches"},
    ):
        with pytest.raises(ValidationError):
            anchor(**forbidden)


def test_minter_is_keyword_only_calls_uuid4_once_and_preserves_fields(
        monkeypatch):
    signature = inspect.signature(identity.mint_transition_anchor)
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
    value = identity.mint_transition_anchor(
        namespace="test-model", display_name="Synthetic transition",
        role_name="synthetic-transition")
    assert calls == [None]
    assert value.model_dump(mode="json") == {
        "anchor_id": "trn_1234567890abcdef1234567890abcdef",
        "namespace": "test-model", "display_name": "Synthetic transition",
        "role_name": "synthetic-transition",
    }


def test_minter_emits_distinct_rfc4122_uuid4_lowercase_ids():
    values = tuple(identity.mint_transition_anchor(
        namespace="test-model", display_name="Synthetic transition")
        for _ in range(12))
    assert len({value.anchor_id for value in values}) == len(values)
    for value in values:
        suffix = value.anchor_id.removeprefix("trn_")
        parsed = UUID(hex=suffix)
        assert suffix == suffix.lower()
        assert parsed.version == 4
        assert parsed.variant == RFC_4122


def test_transition_names_are_exported_without_query_or_occurrence_symbols():
    for required in (
        "TRANSITION_ANCHOR_ID_PATTERN", "TransitionAnchor",
        "mint_transition_anchor"):
        assert required in identity.__all__
    for forbidden in ("TransitionOccurrence", "TransitionAssessment"):
        assert forbidden not in identity.__all__
        assert not hasattr(identity, forbidden)
