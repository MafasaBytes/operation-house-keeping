"""ES-001 Group 7 adversarial resolver matrix and contract hardening."""

from datetime import UTC, datetime, timedelta, tzinfo
from itertools import permutations

import pytest
from pydantic import ValidationError

from backend.identity_binding import membership
from backend.identity_binding.contracts import (
    AppliesScope, AuthorityRef, DeclaredBoundary, UnboundedBoundary,
    UnknownBoundary)
from backend.model_kernel import QuantityKindReference
from backend.source_interpretation import (
    DimensionInterpretationResolution, InterpretationAssertionSummary,
    InterpretationRejection, InterpretationResolver, InterpretationRetraction,
    QuantityKindInterpretation, SourcePropertyInterpretation, build_record)
from backend.source_interpretation.canonical import canonical_sort_key
from backend.source_interpretation.errors import InterpretationResolutionError
from backend.source_interpretation.store import InterpretationStore
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef
from tests.source_interpretation.test_resolver import (
    AUTH, PRESSURE, PROP, SUBJECT, T0, T1, TEMP, TIN, resolver, scope, spi)


def resolve(tmp_path, *records, at=TIN, subject=SUBJECT, prop=PROP):
    return resolver(tmp_path, *records).resolve_property_interpretations(
        subject, prop, at=at).quantity_kind


def out_record(note="out"):
    return spi(applies=AppliesScope(
        axis="ingestion_received_at",
        start_boundary=DeclaredBoundary(kind="declared", at=T0 - timedelta(hours=2)),
        end_boundary=DeclaredBoundary(kind="declared", at=T0 - timedelta(hours=1)),
        interval_semantics="half_open"), note=note)


def unknown_record(*, token=TEMP, note="unknown"):
    return spi(body=QuantityKindInterpretation(
        dimension="quantity_kind", quantity_kind=token),
        applies=scope("unknown", "unknown"), note=note)


@pytest.mark.parametrize("case,records,status,candidate_count,positive", [
    ("one_in", lambda: (spi(),), "interpreted", 0, True),
    ("same_in_corroboration", lambda: (spi(note="a"), spi(note="b")),
     "interpreted", 0, True),
    ("different_in", lambda: (spi(), spi(body=QuantityKindInterpretation(
        dimension="quantity_kind", quantity_kind=PRESSURE))),
     "conflicted", 2, False),
    ("one_unknown", lambda: (unknown_record(),),
     "applicability_unknown", 1, False),
    ("different_unknowns", lambda: (unknown_record(), unknown_record(
        token=PRESSURE, note="other")), "ambiguous", 2, False),
    ("in_plus_same_unknown", lambda: (spi(), unknown_record()),
     "interpreted", 0, True),
    ("in_plus_different_unknown", lambda: (spi(), unknown_record(
        token=PRESSURE)), "ambiguous", 2, False),
    ("all_out", lambda: (out_record(), out_record("other")),
     "outside_applicability", 0, False),
    ("out_plus_unknown", lambda: (out_record(), unknown_record()),
     "applicability_unknown", 1, False),
    ("out_plus_in", lambda: (out_record(), spi()), "interpreted", 0, True),
])
def test_complete_classification_vectors(
        tmp_path, case, records, status, candidate_count, positive):
    result = resolve(tmp_path / case, *records())
    assert result.status == status
    assert len(result.candidate_interpretations) == candidate_count
    assert (result.interpretation is not None) is positive
    assert (result.applicability_basis is not None) is positive
    assert tuple(canonical_sort_key(body)
                 for body in result.candidate_interpretations) == tuple(sorted(
                     canonical_sort_key(body)
                     for body in result.candidate_interpretations))


@pytest.mark.parametrize("at,expected", [
    (T0 - timedelta(microseconds=1), "outside_applicability"),
    (T0, "interpreted"),
    (T1 - timedelta(microseconds=1), "interpreted"),
    (T1, "outside_applicability"),
])
def test_half_open_boundaries_are_exact(tmp_path, at, expected):
    assert resolve(tmp_path, spi(), at=at).status == expected


@pytest.mark.parametrize("start,end,expected", [
    ("declared", "declared", "interpreted"),
    ("declared", "unbounded", "interpreted"),
    ("declared", "unknown", "applicability_unknown"),
    ("unbounded", "declared", "interpreted"),
    ("unbounded", "unbounded", "interpreted"),
    ("unbounded", "unknown", "applicability_unknown"),
    ("unknown", "declared", "applicability_unknown"),
    ("unknown", "unbounded", "applicability_unknown"),
    ("unknown", "unknown", "applicability_unknown"),
])
def test_resolver_matches_public_membership_for_all_boundary_pairs(
        tmp_path, start, end, expected):
    declared = spi(applies=scope(start, end))
    assert membership(declared.applies, TIN) == (
        "in" if expected == "interpreted" else "unknown")
    assert resolve(tmp_path, declared).status == expected


def test_unbounded_positive_discloses_its_basis(tmp_path):
    result = resolve(tmp_path, spi(applies=scope("declared", "unbounded")))
    assert result.status == "interpreted"
    assert result.applicability_basis == "includes_unbounded_claim"


def test_rejection_alone_remains_not_declared(tmp_path):
    rejection = build_record(
        InterpretationRejection, subject=SUBJECT, property=PROP,
        rejected_interpretation=QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=TEMP),
        proposed_applies=scope(), recorded_at=T0, authority=AUTH, note="")
    result = resolver(tmp_path, rejection).resolve_property_interpretations(
        SUBJECT, PROP, at=TIN)
    assert result.quantity_kind.status == "not_declared"
    assert result.quantity_kind.via_assertions == ()
    assert result.revision.record_ids == (rejection.record_id,)


def test_one_assertion_both_superseded_and_retracted_is_disclosed_inactive(
        tmp_path):
    root = spi(note="root")
    successor = spi(parents=(root.record_id,), note="successor")
    retract_root = build_record(
        InterpretationRetraction, retracts=root.record_id,
        recorded_at=T0, authority=AUTH, note="")
    retract_successor = build_record(
        InterpretationRetraction, retracts=successor.record_id,
        recorded_at=T0, authority=AUTH, note="")
    result = resolve(tmp_path, root, successor, retract_root, retract_successor)
    assert result.status == "inactive"
    summaries = {summary.record_id: summary for summary in result.via_assertions}
    assert summaries[root.record_id].superseded_by == (successor.record_id,)
    assert summaries[root.record_id].retracted_by == (retract_root.record_id,)
    assert summaries[successor.record_id].retracted_by == (
        retract_successor.record_id,)


def variant(*, token, recorded_at, authority, note):
    return build_record(
        SourcePropertyInterpretation, subject=SUBJECT, property=PROP,
        interpretation=QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=token),
        applies=scope(), supersedes=(), recorded_at=recorded_at,
        authority=authority, note=note)


def test_conflict_candidates_ignore_append_time_and_authority_permutations(
        tmp_path):
    human = AuthorityRef(kind="human_owner", agent="z-owner",
                         method="manual_declaration")
    fixture = AuthorityRef(kind="test_fixture", agent="a-fixture",
                           method="manual_declaration")
    records = (
        variant(token=TEMP, recorded_at=T0 + timedelta(days=2),
                authority=human, note="late-human"),
        variant(token=PRESSURE, recorded_at=T0 - timedelta(days=2),
                authority=fixture, note="early-fixture"),
    )
    expected = tuple(sorted((record.interpretation for record in records),
                            key=canonical_sort_key))
    revisions = set()
    for index, order in enumerate(permutations(records)):
        ledger = InterpretationStore(tmp_path / f"order-{index}" / "demo-printer")
        for record in order:
            ledger.append(record)
        whole = InterpretationResolver(ledger.load(
        )).resolve_property_interpretations(SUBJECT, PROP, at=TIN)
        revisions.add(whole.revision.revision_id)
        assert whole.quantity_kind.status == "conflicted"
        assert whole.quantity_kind.candidate_interpretations == expected
    assert len(revisions) == 1


@pytest.mark.parametrize("where,field,value", [
    ("subject", "subject_identifier", "Extruder"),
    ("subject", "subject_identifier", "extruder "),
    ("subject", "source_id", "Printer-1"),
    ("property", "json_pointer", "/result/status/extruder/temperature "),
    ("property", "item_key", "Printer_Objects"),
])
def test_case_and_whitespace_are_locator_identity(
        tmp_path, where, field, value):
    subject, prop = SUBJECT, PROP
    if where == "subject":
        subject = subject.model_copy(update={field: value})
    else:
        prop = prop.model_copy(update={field: value})
    assert resolve(tmp_path, spi(), subject=subject, prop=prop).status == (
        "not_declared")


def test_same_pointer_different_source_and_adapter_never_cross_contaminate(
        tmp_path):
    other_source = SUBJECT.model_copy(update={"source_id": "bench-2"})
    other_adapter = SUBJECT.model_copy(update={"adapter_id": "other_adapter"})
    records = (spi(), spi(subject=other_source, note="source"),
               spi(subject=other_adapter, note="adapter"))
    for index, subject in enumerate((SUBJECT, other_source, other_adapter)):
        result = resolve(tmp_path / str(index), *records, subject=subject)
        assert result.status == "interpreted"
        assert len(result.via_assertions) == 1
        assert result.via_assertions[0].record_id == records[index].record_id


def test_same_subject_changed_pointer_inherits_nothing(tmp_path):
    target = PROP.model_copy(update={
        "json_pointer": "/result/status/extruder/target"})
    assert resolve(tmp_path, spi(), prop=target).status == "not_declared"


def summary(record, **updates):
    fields = dict(
        record_id=record.record_id, dimension="quantity_kind",
        interpretation=record.interpretation, authority=record.authority,
        declared_applies=record.applies, effective_applies=record.applies,
        closure_records=(), superseded_by=(), retracted_by=(), active=True,
        membership_at="in", recorded_at=record.recorded_at)
    fields.update(updates)
    return InterpretationAssertionSummary(**fields)


def test_summary_contract_rejects_lifecycle_and_dimension_inconsistency():
    record = spi()
    with pytest.raises(ValidationError):
        summary(record, dimension="unit")
    with pytest.raises(ValidationError):
        summary(record, active=True, superseded_by=("spi_" + "a" * 64,))
    with pytest.raises(ValidationError):
        summary(record, closure_records=("spc_" + "a" * 64,
                                         "spc_" + "b" * 64))
    with pytest.raises(ValidationError):
        summary(record, retracted_by=("spi_" + "a" * 64,))


def test_dimension_contract_rejects_duplicate_wrong_and_impossible_payloads():
    first = spi().interpretation
    wrong = SourcePropertyInterpretation.model_validate(
        spi(body=QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=PRESSURE)).model_dump(
        )).interpretation
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status="conflicted",
            candidate_interpretations=(first, first))
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status="outside_applicability",
            candidate_interpretations=(first,))
    ordered = tuple(sorted((first, wrong), key=canonical_sort_key))
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status="conflicted",
            candidate_interpretations=ordered[::-1])


@pytest.mark.parametrize("status,candidates", [
    ("conflicted", lambda first, second: (first,)),
    ("ambiguous", lambda first, second: (first,)),
    ("applicability_unknown", lambda first, second: (first, second)),
])
def test_candidate_statuses_enforce_their_cardinality(status, candidates):
    first = spi().interpretation
    second = spi(body=QuantityKindInterpretation(
        dimension="quantity_kind", quantity_kind=PRESSURE)).interpretation
    values = tuple(sorted(candidates(first, second), key=canonical_sort_key))
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status=status,
            candidate_interpretations=values)


@pytest.mark.parametrize("status,kwargs", [
    ("interpreted", lambda body: dict(
        interpretation=body, applicability_basis="declared_interval")),
    ("outside_applicability", lambda body: {}),
    ("applicability_unknown", lambda body: dict(
        candidate_interpretations=(body,))),
    ("conflicted", lambda body: dict(candidate_interpretations=(
        body, QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=PRESSURE)))),
])
def test_every_declared_status_requires_explanatory_assertions(status, kwargs):
    body = spi().interpretation
    fields = kwargs(body)
    if "candidate_interpretations" in fields:
        fields["candidate_interpretations"] = tuple(sorted(
            fields["candidate_interpretations"], key=canonical_sort_key))
    with pytest.raises(ValidationError):
        DimensionInterpretationResolution(
            dimension="quantity_kind", status=status,
            via_assertions=(), **fields)


class NoneOffset(tzinfo):
    def utcoffset(self, dt):
        return None


def test_utcoffset_none_time_is_typed(tmp_path):
    bad = datetime(2026, 8, 13, 12, tzinfo=NoneOffset())
    with pytest.raises(InterpretationResolutionError) as error:
        resolver(tmp_path).resolve_property_interpretations(
            SUBJECT, PROP, at=bad)
    assert error.value.error_code == "INTERPRETATION_NAIVE_AT"


def test_resolver_constructor_rejects_wrong_type():
    with pytest.raises(InterpretationResolutionError) as error:
        InterpretationResolver(object())
    assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"
