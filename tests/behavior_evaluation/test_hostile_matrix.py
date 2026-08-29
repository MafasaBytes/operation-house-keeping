"""BH-001 authoritative outer reconstruction adversarial matrix."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from backend.behavior_evaluation import BehaviorEvaluationResult
from backend.model_state import SourceSelector

from tests.behavior_evaluation.helpers import (
    AS_BUILT,
    E1,
    PROP_TARGET,
    VAR_A,
    VAR_B,
    evaluate,
    model_store,
    participant_sources,
    semantic_queries,
)
from tests.model_kernel.builders import registration
from tests.model_state.helpers import entity_declaration


def _payload(result):
    return result.model_dump(mode="python")


@pytest.mark.parametrize("field,value", [
    ("participant_index", True), ("participant_index", -1),
    ("source_index", "0"), ("semantic_result_index", 1),
    ("candidate_index", False),
])
def test_every_index_is_strict_and_authoritative(tmp_path, field, value):
    payload = _payload(evaluate(tmp_path))
    payload["participants"][0][field] = value
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


@pytest.mark.parametrize("mutation", ["missing", "extra", "reordered", "duplicate"])
def test_participant_rows_are_complete_unique_and_ordered(tmp_path, mutation):
    payload = _payload(evaluate(tmp_path))
    rows = list(payload["participants"])
    if mutation == "missing":
        rows = rows[:1]
    elif mutation == "extra":
        rows.append(dict(rows[1]))
    elif mutation == "reordered":
        rows.reverse()
    else:
        rows[1] = dict(rows[0])
    payload["participants"] = rows
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


@pytest.mark.parametrize("field", [
    "model_admission", "observation_availability", "attachment_admission",
    "semantic_admission", "unit_admission", "lock_admission",
    "numeric_admission", "admission", "refusal_reasons", "canonical_decimal",
])
def test_every_participant_derived_field_is_recomputed(tmp_path, field):
    payload = _payload(evaluate(tmp_path))
    replacements = {
        "model_admission": "not_admitted",
        "observation_availability": "not_evaluated",
        "attachment_admission": "not_attached",
        "semantic_admission": "not_admitted",
        "unit_admission": "mismatch",
        "lock_admission": "mismatched",
        "numeric_admission": "out_of_bounds",
        "admission": "not_admitted",
        "refusal_reasons": ("numeric_value_out_of_bounds",),
        "canonical_decimal": "999",
    }
    payload["participants"][0][field] = replacements[field]
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


def test_swapped_or_duplicated_semantic_results_are_rejected(tmp_path):
    result = evaluate(tmp_path)
    for semantics in (
        tuple(reversed(result.participant_semantic_results)),
        (result.participant_semantic_results[0],) * 2,
    ):
        payload = _payload(result)
        payload["participant_semantic_results"] = tuple(
            item.model_dump(mode="python") for item in semantics)
        with pytest.raises(ValidationError):
            BehaviorEvaluationResult.model_validate(payload)


def test_duplicate_or_retargeted_sources_are_rejected(tmp_path):
    result = evaluate(tmp_path)
    first, second = result.participant_sources
    retargeted_entity = first.model_copy(
        update={"entity_anchor_id": "ent_" + "7" * 32})
    retargeted_property = first.model_copy(update={
        "source": SourceSelector(
            subject=first.source.subject, property=PROP_TARGET)})
    for sources in ((first, first), (retargeted_entity, second),
                    (retargeted_property, second)):
        payload = _payload(result)
        payload["participant_sources"] = tuple(
            item.model_dump(mode="python") for item in sources)
        with pytest.raises(ValidationError):
            BehaviorEvaluationResult.model_validate(payload)


def test_mixed_model_revisions_are_rejected(tmp_path):
    baseline = evaluate(tmp_path / "baseline")
    other_root = tmp_path / "other"
    other_model = model_store(
        other_root, extra_records=(registration("ent_" + "7" * 32),))
    other = evaluate(other_root, model=other_model)
    payload = _payload(baseline)
    payload["participant_semantic_results"] = (
        payload["participant_semantic_results"][0],
        other.participant_semantic_results[1].model_dump(mode="python"))
    with pytest.raises(ValidationError, match="model revision"):
        BehaviorEvaluationResult.model_validate(payload)


def test_mixed_binding_revisions_are_rejected(tmp_path):
    baseline = evaluate(tmp_path / "baseline")
    other_root = tmp_path / "other"
    from tests.behavior_evaluation.helpers import semantic_queries as make_semantic
    from tests.model_state.helpers import (
        PROP_TEMP, entity_declaration as entity_decl, prop_assertion,
        var_declaration,
    )
    bindings = (
        entity_decl(E1, "Demo entity"),
        entity_decl("ent_" + "7" * 32, "Irrelevant entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_A, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    other = evaluate(
        other_root,
        semantic=make_semantic(other_root, binding_records=bindings))
    payload = _payload(baseline)
    payload["participant_semantic_results"] = (
        payload["participant_semantic_results"][0],
        other.participant_semantic_results[1].model_dump(mode="python"))
    with pytest.raises(ValidationError, match="binding revision"):
        BehaviorEvaluationResult.model_validate(payload)


def test_mixed_interpretation_revisions_are_rejected(tmp_path):
    from backend.source_interpretation import QuantityKindInterpretation
    from tests.behavior_evaluation.helpers import (
        _interpretation_record, interpretation_resolver)
    from tests.model_kernel.builders import quantity_kind
    from tests.model_state.helpers import PROP_TEMP

    baseline = evaluate(tmp_path / "baseline")
    other_root = tmp_path / "other"
    extra = _interpretation_record(
        PROP_TEMP, QuantityKindInterpretation(
            dimension="quantity_kind",
            quantity_kind=quantity_kind(code="other_quantity")))
    resolver = interpretation_resolver(other_root, extra_records=(extra,))
    other = evaluate(
        other_root,
        semantic=semantic_queries(other_root, interpretations=resolver))
    payload = _payload(baseline)
    payload["participant_semantic_results"] = (
        payload["participant_semantic_results"][0],
        other.participant_semantic_results[1].model_dump(mode="python"))
    with pytest.raises(ValidationError, match="interpretation revision"):
        BehaviorEvaluationResult.model_validate(payload)


def test_mixed_cutoff_and_context_are_rejected(tmp_path):
    result = evaluate(tmp_path)
    payload = _payload(result)
    payload["as_of"] = result.as_of + timedelta(seconds=1)
    with pytest.raises(ValidationError, match="cutoff"):
        BehaviorEvaluationResult.model_validate(payload)
    payload = _payload(result)
    payload["context"] = AS_BUILT.model_dump(mode="python")
    with pytest.raises(ValidationError, match="request echo"):
        BehaviorEvaluationResult.model_validate(payload)


def test_single_duplicate_occurrence_mutation_is_detected(tmp_path):
    payload = _payload(evaluate(tmp_path))
    occurrence = (payload["participant_semantic_results"][0]["candidates"][0]
                  ["value_candidate"]["state_candidate"]["bound"]["observed"]
                  ["occurrence"])
    occurrence["value_json"] = "999"
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)


def test_stale_model_record_content_and_wrong_material_index_are_rejected(tmp_path):
    result = evaluate(tmp_path)
    payload = _payload(result)
    records = payload["behavior"]["material"]["records"]
    declaration = next(
        record for record in records
        if record["record_kind"] == "behavior_rule_declaration")
    declaration["note"] = "stale content-derived identity"
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)

    payload = _payload(result)
    payload["behavior"]["registration_index"] = 0
    with pytest.raises(ValidationError):
        BehaviorEvaluationResult.model_validate(payload)
