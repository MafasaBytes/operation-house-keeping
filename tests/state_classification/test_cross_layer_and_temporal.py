"""Cross-layer revision coherence and independent temporal policy."""

import json
from datetime import timedelta, timezone
from decimal import ROUND_DOWN, localcontext

import pytest
from pydantic import ValidationError

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.state_classification import (
    StateClassificationQueries,
    StateClassificationResult,
)
from tests.behavior_evaluation.helpers import (
    E1,
    PROP_TARGET,
    PROP_TEMP,
    interpretation_resolver,
    semantic_queries,
)
from tests.model_kernel.builders import VAR_A, VAR_B
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    STATE_B,
    pins,
    state_declaration,
    state_registration,
)
from tests.model_state.helpers import (
    entity_declaration,
    prop_assertion,
    var_declaration,
)
from tests.state_classification.helpers import (
    AS_OF,
    classify,
    condition_records,
    condition_sources,
    state_model,
)


def _classify_with_semantic(semantic, state_anchor_id=STATE_A):
    return StateClassificationQueries(
        ConstraintEvaluationQueries(semantic)).state_classification(
            state_anchor_id, context=AS_OPERATED, as_of=AS_OF,
            condition_sources=condition_sources())


def test_mixed_binding_revisions_are_rejected(tmp_path):
    model, _, _ = state_model(tmp_path / "model")
    baseline = classify(tmp_path / "baseline", model=model)
    bindings = (
        entity_declaration(E1, "Demo entity"),
        entity_declaration("ent_" + "7" * 32, "Irrelevant entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_A, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    other = _classify_with_semantic(semantic_queries(
        tmp_path / "other", model=model, binding_records=bindings))
    payload = baseline.model_dump(mode="python")
    payload["constraint_evaluations"] = (
        payload["constraint_evaluations"][0],
        other.constraint_evaluations[1].model_dump(mode="python"),
    )
    with pytest.raises(ValidationError, match="binding revision"):
        StateClassificationResult.model_validate(payload)


def test_mixed_interpretation_revisions_are_rejected(tmp_path):
    from backend.source_interpretation import QuantityKindInterpretation
    from tests.behavior_evaluation.helpers import _interpretation_record
    from tests.model_kernel.builders import quantity_kind

    model, _, _ = state_model(tmp_path / "model")
    baseline = classify(tmp_path / "baseline", model=model)
    extra = _interpretation_record(
        PROP_TEMP,
        QuantityKindInterpretation(
            dimension="quantity_kind",
            quantity_kind=quantity_kind(code="other_quantity")),
    )
    resolver = interpretation_resolver(
        tmp_path / "other", extra_records=(extra,))
    other = _classify_with_semantic(semantic_queries(
        tmp_path / "other", model=model, interpretations=resolver))
    payload = baseline.model_dump(mode="python")
    payload["constraint_evaluations"] = (
        payload["constraint_evaluations"][0],
        other.constraint_evaluations[1].model_dump(mode="python"),
    )
    with pytest.raises(ValidationError, match="interpretation revision"):
        StateClassificationResult.model_validate(payload)


def test_aware_offset_normalizes_once_and_as_of_never_selects_model(tmp_path):
    model, _, _ = state_model(tmp_path)
    offset_cutoff = AS_OF.astimezone(timezone(timedelta(hours=2)))
    result = classify(tmp_path, model=model, as_of=offset_cutoff)
    assert result.as_of == AS_OF
    assert all(item.as_of == AS_OF for item in result.constraint_evaluations)

    earlier = classify(tmp_path, model=model, as_of=AS_OF - timedelta(hours=2))
    assert earlier.state == result.state
    assert earlier.state.material.revision == result.state.material.revision
    assert earlier.as_of != result.as_of
    assert earlier.temporal_alignment == result.temporal_alignment == "not_asserted"


def test_far_later_cutoff_discloses_staleness_without_freshness_veto(tmp_path):
    model, _, _ = state_model(tmp_path)
    later = classify(tmp_path, model=model, as_of=AS_OF + timedelta(days=30))
    observed = tuple(
        item.semantic_compatibility.value_compatibility.state.candidates[0]
        .bound.observed
        for item in later.constraint_evaluations)
    assert all(item.staleness_seconds >= 30 * 24 * 60 * 60 for item in observed)
    assert later.temporal_alignment == "not_asserted"
    assert later.execution == "executed"
    assert later.computed_match == "matches"
    assert not hasattr(later, "freshness")
    assert not hasattr(later, "acquisition_cohort")


def test_independent_latest_observations_may_have_different_receipt_times(
        tmp_path):
    from backend.data_sources.connectors.http_api import TransportResponse
    from backend.temporal_state.projector import TemporalProjector
    from backend.temporal_state.queries import TemporalQueries
    from backend.temporal_state.store import TemporalStore
    from tests.data_sources.test_ingestion_runner_api import (
        FIXTURES, happy_script, make_runner)

    runner, evidence, transport = make_runner(
        tmp_path / "temporal" / "ds", happy_script())
    temporal_store = TemporalStore(
        tmp_path / "temporal" / "temporal.db",
        evidence_root=evidence.base_dir)
    projector = TemporalProjector(evidence, temporal_store)
    runner.run("printer-1")

    changed = json.loads((FIXTURES / "moonraker_printer_objects_changed.json")
                         .read_text(encoding="utf-8"))
    del changed["result"]["status"]["extruder"]["target"]
    transport.script["/printer/objects/query"] = TransportResponse(
        status=200,
        headers={"Content-Type": "application/json",
                 "Date": "Fri, 07 Aug 2026 20:00:11 GMT"},
        body=json.dumps(changed, sort_keys=True).encode("utf-8"))
    runner.run("printer-1")
    projector.project("printer-1")
    temporal = TemporalQueries(temporal_store)

    model, _, _ = state_model(tmp_path / "model")
    result = _classify_with_semantic(semantic_queries(
        tmp_path / "evidence", model=model, temporal=temporal))
    receipts = tuple(
        item.semantic_compatibility.value_compatibility.state.candidates[0]
        .bound.observed.occurrence.received_at
        for item in result.constraint_evaluations)
    assert receipts[0] != receipts[1]
    assert result.temporal_alignment == "not_asserted"
    assert result.execution == "executed"
    assert result.computed_match == "matches"


def test_ambient_decimal_context_cannot_change_cn_owned_outcomes(tmp_path):
    model, _, _ = state_model(tmp_path)
    baseline = classify(tmp_path, model=model)
    with localcontext() as context:
        context.prec = 2
        context.rounding = ROUND_DOWN
        constrained = classify(tmp_path, model=model)
    assert constrained == baseline


def test_two_state_calls_may_match_without_aggregate_rollup(tmp_path):
    _, declarations = condition_records()
    registration_b = state_registration(
        state_anchor_id=STATE_B, subject=E1,
        constraints=tuple(row.constraint_anchor_id
                          for row in condition_sources()),
        second_owner=E1)
    declaration_b = state_declaration(
        registration_b, state_anchor_id=STATE_B,
        context=AS_OPERATED, condition_pins=pins(declarations=declarations))
    model, _, _ = state_model(
        tmp_path, extra_records=(registration_b, declaration_b))
    semantic = semantic_queries(tmp_path / "queries", model=model)
    queries = StateClassificationQueries(ConstraintEvaluationQueries(semantic))
    first = queries.state_classification(
        STATE_A, context=AS_OPERATED, as_of=AS_OF,
        condition_sources=condition_sources())
    second = queries.state_classification(
        STATE_B, context=AS_OPERATED, as_of=AS_OF,
        condition_sources=condition_sources())
    assert first.computed_match == second.computed_match == "matches"
    assert first.state_anchor_id != second.state_anchor_id
    assert not hasattr(queries, "classify_all_states")
