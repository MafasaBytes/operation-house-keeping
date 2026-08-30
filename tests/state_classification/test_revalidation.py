"""Authoritative ST result reconstruction and hostile carried material."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from backend.constraint_evaluation import ConstraintEvaluationResult
from backend.state_classification import StateClassificationResult
from tests.model_kernel.builders import registration
from tests.state_classification.helpers import (
    AS_DESIGNED,
    classify,
    condition_sources,
    state_model,
)


def _payload(result):
    return result.model_dump(mode="python")


@pytest.mark.parametrize("field,value", [
    ("condition_coverage", "not_evaluated"),
    ("temporal_alignment", "not_evaluated"),
    ("execution", "not_executed"),
    ("computed_match", "does_not_match"),
    ("ruleset_version", "st001.2"),
])
def test_every_outer_derived_field_is_authoritative(tmp_path, field, value):
    payload = _payload(classify(tmp_path))
    payload[field] = value
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("field,value", [
    ("condition_index", True),
    ("source_index", "0"),
    ("constraint_evaluation_index", 1.0),
    ("candidate_index", False),
])
def test_every_lightweight_index_is_strict_and_authoritative(
        tmp_path, field, value):
    payload = _payload(classify(tmp_path))
    payload["conditions"][0][field] = value
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_boolean_lower_candidate_and_revision_indices_are_rejected(tmp_path):
    payload = _payload(classify(tmp_path))
    payload["constraint_evaluations"][0]["candidates"][0][
        "semantic_candidate_index"] = True
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)
    payload = _payload(classify(tmp_path / "revision"))
    payload["constraint_evaluations"][0]["constraint"]["revision"][
        "record_count"] = True
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("field", [
    "declaration_alignment", "outcome", "constraint_anchor_id",
])
def test_every_condition_derived_field_is_recomputed(tmp_path, field):
    payload = _payload(classify(tmp_path))
    replacements = {
        "declaration_alignment": "superseded",
        "outcome": "violated",
        "constraint_anchor_id": "con_" + "c" * 32,
    }
    payload["conditions"][0][field] = replacements[field]
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("field", ["reason", "condition_index"])
def test_forged_refusal_is_rejected(tmp_path, field):
    model, _, _ = state_model(tmp_path, declaration_records=())
    payload = _payload(classify(tmp_path, model=model))
    payload["refusals"][0][field] = (
        "state_conflicted" if field == "reason" else 0)
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("field", [
    "condition_sources", "constraint_evaluations", "conditions",
])
@pytest.mark.parametrize("mutation", ["missing", "duplicate", "reordered"])
def test_carried_collections_are_complete_unique_and_canonical(
        tmp_path, field, mutation):
    payload = _payload(classify(tmp_path))
    rows = list(payload[field])
    if mutation == "missing":
        rows = rows[:1]
    elif mutation == "duplicate":
        rows[1] = rows[0]
    else:
        rows.reverse()
    payload[field] = rows
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_mixed_model_revisions_and_stale_model_ids_are_rejected(tmp_path):
    baseline = classify(tmp_path / "baseline")
    other_model, _, _ = state_model(
        tmp_path / "other", extra_records=(registration("ent_" + "7" * 32),))
    other = classify(tmp_path / "other", model=other_model)
    payload = _payload(baseline)
    payload["constraint_evaluations"] = (
        payload["constraint_evaluations"][0],
        _payload(other)["constraint_evaluations"][1],
    )
    with pytest.raises(ValidationError, match="model revision"):
        StateClassificationResult.model_validate(payload)

    payload = _payload(baseline)
    declaration = next(
        record for record in payload["state"]["material"]["records"]
        if record["record_kind"] == "state_declaration")
    declaration["note"] = "stale content-derived id"
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_context_cutoff_selector_and_candidate_substitution_are_rejected(tmp_path):
    result = classify(tmp_path)
    payload = _payload(result)
    payload["context"] = AS_DESIGNED.model_dump(mode="python")
    with pytest.raises(ValidationError, match="request echo"):
        StateClassificationResult.model_validate(payload)

    payload = _payload(result)
    payload["as_of"] = result.as_of + timedelta(seconds=1)
    with pytest.raises(ValidationError, match="cutoff"):
        StateClassificationResult.model_validate(payload)

    payload = _payload(result)
    payload["condition_sources"][0]["source"] = payload[
        "condition_sources"][1]["source"]
    with pytest.raises(ValidationError, match="selector"):
        StateClassificationResult.model_validate(payload)

    payload = _payload(result)
    payload["conditions"][0]["candidate_index"] = None
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_nested_model_copy_construct_and_hidden_extra_forgeries_reject(tmp_path):
    result = classify(tmp_path)
    row = result.conditions[0].model_copy(update={"condition_index": True})
    forged = result.model_construct(
        **{**result.model_dump(mode="python"),
           "conditions": (row, result.conditions[1])})
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(forged)

    hidden = result.model_copy(update={"state_valid": True})
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(hidden)


def test_store_and_filesystem_capabilities_are_not_used_for_revalidation(
        tmp_path, monkeypatch):
    payload = _payload(classify(tmp_path))

    def forbidden(*args, **kwargs):
        raise AssertionError("result validation must not access a store")

    from backend.model_kernel import ModelStore
    for method in ("load", "replay", "append"):
        monkeypatch.setattr(ModelStore, method, forbidden)
    rebuilt = StateClassificationResult.model_validate(payload)
    assert rebuilt.model_dump(mode="python") == payload


def _replace_all_key(value, key, replacement):
    if isinstance(value, dict):
        return {
            item_key: (replacement if item_key == key else
                       _replace_all_key(item_value, key, replacement))
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_replace_all_key(item, key, replacement) for item in value]
    if isinstance(value, tuple):
        return tuple(_replace_all_key(item, key, replacement) for item in value)
    return value


def test_st_specific_coherent_lower_mutation_limitation_is_executable(tmp_path):
    """ST proves carried coherence, not uncaptured raw-payload authenticity."""
    result = classify(tmp_path)
    payload = _payload(result)
    lower = _replace_all_key(
        payload["constraint_evaluations"][0],
        "quality_flags", ["coherent_untrusted_lower_mutation"])
    # The public lower contract accepts this coherent occurrence-content
    # mutation because the raw payload authenticated by its checksum is not
    # carried. ST must not access a store to overclaim a stronger boundary.
    coherent = ConstraintEvaluationResult.model_validate(lower)
    payload["constraint_evaluations"] = (
        coherent.model_dump(mode="python"),
        payload["constraint_evaluations"][1],
    )
    rebuilt = StateClassificationResult.model_validate(payload)
    assert (rebuilt.constraint_evaluations[0].semantic_compatibility
            .value_compatibility.state.candidates[0].bound.observed.occurrence
            .quality_flags) == ["coherent_untrusted_lower_mutation"]
