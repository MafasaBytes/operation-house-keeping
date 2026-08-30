"""Authoritative ST result reconstruction and hostile carried material."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from backend.constraint_evaluation import ConstraintEvaluationResult
from backend.state_classification import StateClassificationResult
from tests.model_kernel.builders import (
    CON_A, CON_B, constraint_declaration, registration, upper_bound)
from tests.model_kernel.st001_slice_a_helpers import T0
from tests.state_classification.helpers import (
    AS_DESIGNED,
    classify,
    condition_sources,
    custom_state_model,
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
    ("condition_index", -1),
    ("condition_index", 2),
    ("source_index", "0"),
    ("source_index", -1),
    ("source_index", 1),
    ("source_index", 2),
    ("constraint_evaluation_index", 1.0),
    ("constraint_evaluation_index", -1),
    ("constraint_evaluation_index", 1),
    ("constraint_evaluation_index", 2),
    ("candidate_index", False),
    ("candidate_index", -1),
    ("candidate_index", 2),
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
@pytest.mark.parametrize(
    "mutation", ["missing", "duplicate", "reordered", "extra"])
def test_carried_collections_are_complete_unique_and_canonical(
        tmp_path, field, mutation):
    payload = _payload(classify(tmp_path))
    rows = list(payload[field])
    if mutation == "missing":
        rows = rows[:1]
    elif mutation == "duplicate":
        rows[1] = rows[0]
    elif mutation == "reordered":
        rows.reverse()
    elif field == "condition_sources":
        extra = dict(rows[-1])
        extra["constraint_anchor_id"] = "con_" + "c" * 32
        rows.append(extra)
    elif field == "constraint_evaluations":
        rows.append(rows[-1])
    else:
        extra = dict(rows[-1])
        extra["condition_index"] = 2
        rows.append(extra)
    payload[field] = rows
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "extra"])
def test_refusal_collection_is_complete_unique_and_authoritative(
        tmp_path, mutation):
    model, _, _ = state_model(tmp_path, declaration_records=())
    payload = _payload(classify(tmp_path, model=model))
    rows = list(payload["refusals"])
    if mutation == "missing":
        rows = []
    elif mutation == "duplicate":
        rows.append(dict(rows[0]))
    else:
        rows.append({
            "reason": "condition_evaluation_not_evaluated",
            "condition_index": 0,
        })
    payload["refusals"] = rows
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_multiple_refusals_are_owned_ordered_and_cannot_be_reordered(tmp_path):
    original = constraint_declaration(CON_A, predicate=upper_bound("80"))
    correction = constraint_declaration(
        CON_A, predicate=upper_bound("90"),
        supersedes=(original.record_id,),
        recorded_at=T0 + timedelta(hours=1))
    unknown = constraint_declaration(CON_B, predicate=upper_bound("80"))
    model, _ = custom_state_model(
        tmp_path, declarations_a=(original, correction),
        declarations_b=(unknown,), pinned_a=original, pinned_b=unknown)
    result = classify(tmp_path, model=model)
    assert [(item.reason, item.condition_index) for item in result.refusals] == [
        ("condition_declaration_superseded", 0),
        ("condition_evaluation_not_evaluated", 1),
    ]
    assert result.constraint_evaluations[1].candidates[0].not_evaluated_reason == (
        "constraint_observation_role_mismatch")
    assert "constraint_observation_role_mismatch" not in {
        item.reason for item in result.refusals}
    payload = _payload(result)
    payload["refusals"] = tuple(reversed(payload["refusals"]))
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


@pytest.mark.parametrize("kind", ["semantic", "specification"])
def test_stale_lower_model_projection_ids_are_rejected(tmp_path, kind):
    payload = _payload(classify(tmp_path))
    semantic = payload["constraint_evaluations"][0]["semantic_compatibility"]
    if kind == "semantic":
        record = semantic["semantics_result"]["quantity_kind"]["declaration"]
    else:
        record = semantic["value_compatibility"]["specification_result"][
            "specification"]
    record["note"] = "mutated content with stale model record id"
    with pytest.raises(ValidationError, match="model facts"):
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


@pytest.mark.parametrize("target", ["observed", "evidence_quality"])
def test_raw_nested_lower_mapping_extras_cannot_be_laundered(tmp_path, target):
    payload = _payload(classify(tmp_path))
    candidate = payload["constraint_evaluations"][0][
        "semantic_compatibility"]["value_compatibility"]["candidates"][0]
    if target == "observed":
        mapping = candidate["state_candidate"]["bound"]["observed"]
    else:
        mapping = candidate["state_candidate"]["bound"]["observed"][
            "evidence_quality"]
    mapping["transition"] = "forged"
    with pytest.raises(ValidationError, match="serialized shape"):
        StateClassificationResult.model_validate(payload)


@pytest.mark.parametrize("attack", ["cycle", "deep"])
def test_hostile_raw_extra_shape_fails_closed_without_python_recursion(
        tmp_path, attack):
    payload = _payload(classify(tmp_path))
    observed = payload["constraint_evaluations"][0][
        "semantic_compatibility"]["value_compatibility"]["candidates"][0][
            "state_candidate"]["bound"]["observed"]
    if attack == "cycle":
        observed["hostile"] = observed
    else:
        cursor = observed
        for index in range(300):
            nested = {"depth": index}
            cursor["hostile"] = nested
            cursor = nested
    with pytest.raises(ValidationError):
        StateClassificationResult.model_validate(payload)


def test_store_and_filesystem_capabilities_are_not_used_for_revalidation(
        tmp_path, monkeypatch):
    import builtins
    import socket

    payload = _payload(classify(tmp_path))

    def forbidden(*args, **kwargs):
        raise AssertionError("result validation must not access a store")

    from backend.model_kernel import ModelStore
    for method in ("load", "replay", "append"):
        monkeypatch.setattr(ModelStore, method, forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
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
