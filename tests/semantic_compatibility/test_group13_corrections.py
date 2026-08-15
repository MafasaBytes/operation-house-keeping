"""ES-001 Group 13 mandatory adversarial corrections.

``superseded`` remains lifecycle history on assertion summaries, but cannot be
an aggregate resolver or semantic-facade status for any valid finite DAG.
"""

from typing import get_args

import pytest
from pydantic import ValidationError

from backend.semantic_compatibility import (
    CandidateSemanticCompatibility, derive_semantic_findings)
from backend.source_interpretation import (
    DimensionInterpretationResolution, InterpretationAssertionSummary,
    InterpretationResolver, InterpretationStore,
    ObservationRoleInterpretation, QuantityKindInterpretation,
    SourcePropertyInterpretation, UnitInterpretation, build_record)
from backend.source_interpretation.contracts import InterpretationStatus
from tests.model_state.helpers import (
    AS_OF, PROP_TARGET, PROP_TEMP, SUBJECT, V1, hour, prop_assertion,
    standard_bindings)
from tests.observation_compatibility.helpers import model_with
from tests.semantic_compatibility.test_contract_hardening import candidate_fields
from tests.semantic_compatibility.test_facade import (
    INTERP_AUTH, QUANTITY, ROLE, T0, UNIT, queries)
from tests.semantic_compatibility.test_remaining_matrix import facade_with
from tests.source_interpretation.test_resolver import TIN, resolver, spi


def superseded_summary():
    record = spi(note="historical")
    successor_id = "spi_" + "f" * 64
    return InterpretationAssertionSummary(
        record_id=record.record_id, dimension="quantity_kind",
        interpretation=record.interpretation, authority=record.authority,
        declared_applies=record.applies, effective_applies=record.applies,
        closure_records=(), superseded_by=(successor_id,), retracted_by=(),
        active=False, membership_at="in", recorded_at=record.recorded_at)


def test_public_aggregate_status_vocabulary_has_no_dead_superseded_literal():
    assert "superseded" not in get_args(InterpretationStatus)


def test_forged_aggregate_superseded_resolution_is_rejected():
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status="superseded",
            via_assertions=(superseded_summary(),))


def test_forged_semantic_candidate_cannot_surface_superseded_aggregate(
        tmp_path):
    facade, _ = queries(tmp_path)
    candidate = facade.variable_semantic_compatibility(
        V1, as_of=AS_OF).candidates[0]
    aggregate = DimensionInterpretationResolution.model_construct(
        dimension="quantity_kind", status="superseded",
        interpretation=None, candidate_interpretations=(),
        via_assertions=(superseded_summary(),))
    interpretation = candidate.interpretation.model_copy(
        update={"quantity_kind": aggregate})
    fields = candidate_fields(
        candidate, interpretation=interpretation,
        quantity_kind_compatibility="not_evaluated",
        quantity_kind_not_evaluated_reason="source_interpretation_superseded")
    draft = CandidateSemanticCompatibility.model_construct(
        **fields, semantic_findings=())
    with pytest.raises(ValidationError):
        CandidateSemanticCompatibility(
            **fields, semantic_findings=derive_semantic_findings(draft))


def test_supersession_remains_disclosed_as_history_not_aggregate_status(
        tmp_path):
    root = spi(note="root")
    successor = spi(parents=(root.record_id,), note="successor")
    result = resolver(tmp_path, root, successor).resolve_property_interpretations(
        SUBJECT, PROP_TEMP, at=TIN).quantity_kind
    assert result.status == "interpreted"
    summaries = {summary.record_id: summary for summary in result.via_assertions}
    assert summaries[root.record_id].active is False
    assert summaries[root.record_id].superseded_by == (successor.record_id,)
    assert summaries[successor.record_id].active is True
    assert result.interpretation == successor.interpretation


def test_synthetic_target_role_counterexample_keeps_quantity_and_unit_equal(
        tmp_path):
    """DM2: no committed PROP_TARGET assertion/interpretation is required."""
    target_role = ROLE.model_copy(update={"code": "commanded_target"})
    ledger = InterpretationStore(tmp_path / "synthetic" / "demo-printer")
    for prop, role in ((PROP_TEMP, ROLE), (PROP_TARGET, target_role)):
        for body in (
            QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=QUANTITY),
            ObservationRoleInterpretation(
                dimension="observation_role", observation_role=role),
            UnitInterpretation(dimension="unit", unit=UNIT),
        ):
            ledger.append(build_record(
                SourcePropertyInterpretation, subject=SUBJECT, property=prop,
                interpretation=body, applies=hour(), supersedes=(),
                recorded_at=T0, authority=INTERP_AUTH, note="synthetic DM2"))
    bindings = (*standard_bindings(), prop_assertion(
        prop=PROP_TARGET, note="synthetic target counterexample"))
    from tests.semantic_compatibility.test_facade import model_semantics

    model = model_semantics(model_with(tmp_path))
    facade = facade_with(
        tmp_path, model, InterpretationResolver(ledger.load()),
        binding_records=bindings)
    result = facade.variable_semantic_compatibility(V1, as_of=AS_OF)
    by_property = {item.value_candidate.state_candidate.property: item
                   for item in result.candidates}
    measured, target = by_property[PROP_TEMP], by_property[PROP_TARGET]
    assert measured.quantity_kind_compatibility == "token_identical"
    assert target.quantity_kind_compatibility == "token_identical"
    assert measured.unit_identity_compatibility == "unit_identity_exact"
    assert target.unit_identity_compatibility == "unit_identity_exact"
    assert measured.observation_role_compatibility == "token_identical"
    assert target.observation_role_compatibility == "token_differs"
    assert "observation_role_mismatch" in target.semantic_findings
    assert "declared_semantics_compatible" not in target.semantic_findings
