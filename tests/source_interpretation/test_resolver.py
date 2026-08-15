"""ES-001 Group 7 deterministic source-property interpretation."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from backend.identity_binding.contracts import (
    AppliesScope, AuthorityRef, DeclaredBoundary, UnboundedBoundary,
    UnknownBoundary)
from backend.model_kernel import QuantityKindReference, UnitReference
from backend.source_interpretation import (
    DimensionInterpretationResolution, InterpretationClosure,
    InterpretationResolver, InterpretationRetraction,
    QuantityKindInterpretation, SourcePropertyInterpretation,
    UnitInterpretation, build_record)
from backend.source_interpretation.errors import InterpretationResolutionError
from backend.source_interpretation.store import InterpretationStore
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

T0 = datetime(2026, 8, 13, 12, tzinfo=UTC)
T1 = T0 + timedelta(hours=1)
TIN = T0 + timedelta(minutes=30)
AUTH = AuthorityRef(kind="test_fixture", agent="es001_resolver_fixture",
                    method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")
TEMP = QuantityKindReference(system_id="project_local",
                             system_edition="ohk-quantities-1",
                             code="temperature")
PRESSURE = QuantityKindReference(system_id="project_local",
                                 system_edition="ohk-quantities-1",
                                 code="pressure")
UNIT = UnitReference(system_id="project_local", system_edition="ohk-units-1",
                     code="degree_celsius")


def boundary(kind, *, end=False):
    if kind == "declared":
        return DeclaredBoundary(kind="declared", at=T1 if end else T0)
    if kind == "unbounded":
        return UnboundedBoundary(kind="unbounded")
    return UnknownBoundary(kind="unknown")


def scope(start="declared", end="declared"):
    return AppliesScope(axis="ingestion_received_at",
                        start_boundary=boundary(start),
                        end_boundary=boundary(end, end=True),
                        interval_semantics="half_open")


def spi(*, body=None, applies=None, parents=(), subject=SUBJECT, prop=PROP,
        note=""):
    return build_record(
        SourcePropertyInterpretation, subject=subject, property=prop,
        interpretation=body or QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=TEMP),
        applies=applies or scope(), supersedes=parents, recorded_at=T0,
        authority=AUTH, note=note)


def resolver(tmp_path, *records):
    store = InterpretationStore(tmp_path / "demo-printer")
    for record in records:
        store.append(record)
    return InterpretationResolver(store.load())


def quantity(result):
    return result.quantity_kind


class TestStatuses:
    def test_no_declaration_is_structured_and_revisioned(self, tmp_path):
        result = resolver(tmp_path).resolve_property_interpretations(
            SUBJECT, PROP, at=TIN)
        assert result.quantity_kind.status == "not_declared"
        assert result.observation_role.status == "not_declared"
        assert result.unit.status == "not_declared"
        assert result.revision.record_count == 0

    def test_one_in_scope_body_is_interpreted_verbatim(self, tmp_path):
        record = spi()
        result = resolver(tmp_path, record).resolve_property_interpretations(
            SUBJECT, PROP, at=TIN)
        dimension = quantity(result)
        assert dimension.status == "interpreted"
        assert dimension.interpretation == record.interpretation
        assert dimension.applicability_basis == "declared_interval"
        assert dimension.via_assertions[0].record_id == record.record_id

    def test_same_body_corroborates_but_different_positive_bodies_conflict(
            self, tmp_path):
        same = (spi(note="a"), spi(note="b"))
        corroborated = resolver(tmp_path / "same", *same
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert quantity(corroborated).status == "interpreted"
        differing = spi(body=QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=PRESSURE), note="other")
        conflicted = resolver(tmp_path / "different", same[0], differing
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert quantity(conflicted).status == "conflicted"
        assert set(quantity(conflicted).candidate_interpretations) == {
            same[0].interpretation, differing.interpretation}

    def test_unknown_different_body_blocks_positive_result(self, tmp_path):
        positive = spi()
        uncertain = spi(
            body=QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=PRESSURE),
            applies=scope("unknown", "unknown"), note="uncertain")
        result = resolver(tmp_path, positive, uncertain
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert quantity(result).status == "ambiguous"

    @pytest.mark.parametrize("records,status", [
        ((spi(applies=scope("unknown", "unknown")),),
         "applicability_unknown"),
        ((spi(applies=scope("declared", "unknown")),),
         "applicability_unknown"),
        ((spi(applies=scope(), note="outside"),), "outside_applicability"),
    ])
    def test_unknown_and_outside_classification(self, tmp_path, records, status):
        at = T1 + timedelta(hours=1) if status == "outside_applicability" else TIN
        result = resolver(tmp_path, *records).resolve_property_interpretations(
            SUBJECT, PROP, at=at)
        assert quantity(result).status == status

    def test_superseded_retracted_and_mixed_inactive_are_distinct(self, tmp_path):
        root = spi(note="root")
        successor = spi(parents=(root.record_id,), note="successor")
        retraction = build_record(
            InterpretationRetraction, retracts=successor.record_id,
            recorded_at=T0, authority=AUTH, note="")
        result = resolver(tmp_path, root, successor, retraction
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert quantity(result).status == "inactive"
        summaries = {s.record_id: s for s in quantity(result).via_assertions}
        assert not summaries[root.record_id].active
        assert summaries[root.record_id].superseded_by == (successor.record_id,)
        assert summaries[successor.record_id].retracted_by == (
            retraction.record_id,)

    def test_retracted_only_is_retracted(self, tmp_path):
        root = spi()
        retraction = build_record(InterpretationRetraction,
                                  retracts=root.record_id, recorded_at=T0,
                                  authority=AUTH, note="")
        result = resolver(tmp_path, root, retraction
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert quantity(result).status == "retracted"


class TestExactLocatorAndDimensions:
    @pytest.mark.parametrize("field", [
        "source_id", "adapter_id", "subject_identifier", "extraction_route",
        "item_key", "json_pointer"])
    def test_each_locator_dimension_is_identity_sensitive(self, tmp_path, field):
        declared = spi()
        subject, prop = SUBJECT, PROP
        if field in SourceSubjectRef.model_fields:
            subject = subject.model_copy(update={field: "different"})
        else:
            prop = prop.model_copy(update={field: (
                "/different" if field == "json_pointer" else "different")})
        result = resolver(tmp_path, declared).resolve_property_interpretations(
            subject, prop, at=TIN)
        assert quantity(result).status == "not_declared"

    def test_dimensions_resolve_independently(self, tmp_path):
        quantity_record = spi()
        unit_record = spi(body=UnitInterpretation(dimension="unit", unit=UNIT))
        result = resolver(tmp_path, quantity_record, unit_record
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert result.quantity_kind.status == "interpreted"
        assert result.unit.status == "interpreted"
        assert result.observation_role.status == "not_declared"


class TestTimeLifecycleAndContracts:
    def test_closure_effective_scope_is_used_and_disclosed(self, tmp_path):
        root = spi(applies=scope("declared", "unbounded"))
        closure = build_record(InterpretationClosure, closes=root.record_id,
                               end=T1, recorded_at=T0, authority=AUTH, note="")
        result = resolver(tmp_path, root, closure
        ).resolve_property_interpretations(SUBJECT, PROP, at=T1)
        summary = quantity(result).via_assertions[0]
        assert quantity(result).status == "outside_applicability"
        assert summary.declared_applies.end_boundary.kind == "unbounded"
        assert summary.effective_applies.end_boundary.kind == "declared"
        assert summary.closure_records == (closure.record_id,)

    @pytest.mark.parametrize("at", [None, datetime(2026, 8, 13, 12), "bad"])
    def test_missing_or_naive_at_is_typed(self, tmp_path, at):
        with pytest.raises(InterpretationResolutionError) as error:
            resolver(tmp_path).resolve_property_interpretations(
                SUBJECT, PROP, at=at)
        assert error.value.error_code == "INTERPRETATION_NAIVE_AT"

    def test_result_echoes_normalized_time_exact_locator_and_revision(self,
                                                                      tmp_path):
        result = resolver(tmp_path, spi()).resolve_property_interpretations(
            SUBJECT, PROP, at=TIN)
        assert result.subject == SUBJECT and result.property == PROP
        assert result.at == TIN
        assert result.quantity_kind.dimension == "quantity_kind"
        assert result.observation_role.dimension == "observation_role"
        assert result.unit.dimension == "unit"

    def test_forged_locator_is_refused_typed(self, tmp_path):
        forged = SourcePropertyRef.model_construct(
            extraction_route="bad route", item_key="", json_pointer="bad")
        with pytest.raises(InterpretationResolutionError) as error:
            resolver(tmp_path).resolve_property_interpretations(
                SUBJECT, forged, at=TIN)
        assert error.value.error_code == "INTERPRETATION_LOCATOR_INVALID"

    def test_dimension_contract_refuses_interpretation_under_nonpositive_status(
            self):
        with pytest.raises(ValidationError):
            DimensionInterpretationResolution(
                dimension="quantity_kind", status="not_declared",
                interpretation=QuantityKindInterpretation(
                    dimension="quantity_kind", quantity_kind=TEMP))


class TestDeterminismAndBoundaries:
    def test_append_order_never_changes_resolution(self, tmp_path):
        first = spi(note="first")
        second = spi(body=QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=PRESSURE), note="second")
        forward = resolver(tmp_path / "forward", first, second
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        backward = resolver(tmp_path / "backward", second, first
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert forward.quantity_kind == backward.quantity_kind

    def test_rejection_never_changes_any_dimensional_resolution(self, tmp_path):
        from backend.source_interpretation import InterpretationRejection

        accepted = spi()
        rejection = build_record(
            InterpretationRejection, subject=SUBJECT, property=PROP,
            rejected_interpretation=QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=PRESSURE),
            proposed_applies=scope(), recorded_at=T0, authority=AUTH, note="")
        without = resolver(tmp_path / "without", accepted
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        with_rejection = resolver(tmp_path / "with", accepted, rejection
        ).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        assert with_rejection.quantity_kind == without.quantity_kind
        assert with_rejection.observation_role == without.observation_role
        assert with_rejection.unit == without.unit
        assert with_rejection.revision != without.revision

    def test_resolver_imports_public_membership_without_copying_algorithm(self):
        import ast
        from pathlib import Path

        tree = ast.parse(Path(
            "backend/source_interpretation/resolver.py").read_text())
        functions = {node.name for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert "membership" not in functions
        assert any(
            isinstance(node, ast.ImportFrom)
            and node.module == "backend.identity_binding.resolver"
            and any(alias.name == "membership" for alias in node.names)
            for node in ast.walk(tree))
