"""ES-001 Group 6 validating store and lifecycle graph."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from backend.identity_binding.contracts import (
    AppliesScope, AuthorityRef, DeclaredBoundary, UnboundedBoundary,
    UnknownBoundary)
from backend.model_kernel import QuantityKindReference, UnitReference
from backend.source_interpretation import (
    InterpretationClosure, InterpretationIntegrityError,
    InterpretationRetraction, InterpretationRejection,
    InterpretationStore, QuantityKindInterpretation,
    SourcePropertyInterpretation, UnitInterpretation, build_record,
    canonical_payload, validate_record_collection)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

T0 = datetime(2026, 8, 13, 12, tzinfo=UTC)
AUTH = AuthorityRef(kind="test_fixture", agent="es001_store_fixture",
                    method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")
Q_TEMP = QuantityKindReference(system_id="project_local",
                               system_edition="ohk-quantities-1",
                               code="temperature")
Q_PRESSURE = QuantityKindReference(system_id="project_local",
                                   system_edition="ohk-quantities-1",
                                   code="pressure")
UNIT = UnitReference(system_id="project_local", system_edition="ohk-units-1",
                     code="degree_celsius")


def scope(end="unbounded"):
    boundary = {
        "unbounded": UnboundedBoundary(kind="unbounded"),
        "unknown": UnknownBoundary(kind="unknown"),
        "declared": DeclaredBoundary(kind="declared", at=T0 + timedelta(hours=1)),
    }[end]
    return AppliesScope(axis="ingestion_received_at",
                        start_boundary=DeclaredBoundary(kind="declared", at=T0),
                        end_boundary=boundary, interval_semantics="half_open")


def spi(*, body=None, subject=SUBJECT, prop=PROP, parents=(), applies=None,
        note=""):
    return build_record(
        SourcePropertyInterpretation, subject=subject, property=prop,
        interpretation=body or QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=Q_TEMP),
        applies=applies or scope(), supersedes=parents, recorded_at=T0,
        authority=AUTH, note=note)


def retract(target):
    return build_record(InterpretationRetraction, retracts=target.record_id,
                        recorded_at=T0, authority=AUTH, note="")


def close(target, end=None):
    return build_record(InterpretationClosure, closes=target.record_id,
                        end=end or T0 + timedelta(minutes=30), recorded_at=T0,
                        authority=AUTH, note="")


def store(tmp_path):
    return InterpretationStore(tmp_path / "demo-printer")


class TestValidatingAppend:
    def test_append_round_trip_idempotence_and_immutable_indexes(self, tmp_path):
        ledger = store(tmp_path)
        record = spi()
        assert ledger.append(record) == record.record_id
        assert ledger.append(record) == record.record_id
        loaded = ledger.load()
        assert loaded.revision.record_count == 1
        assert loaded.records[record.record_id] == record
        key = (SUBJECT, PROP, "quantity_kind")
        assert loaded.current_interpretation_tips_by_property_dimension[key] == (
            record,)
        with pytest.raises(TypeError):
            loaded.records[record.record_id] = record

    @pytest.mark.parametrize("bad", [
        lambda: retract(spi(note="missing")),
        lambda: close(spi(note="missing")),
    ])
    def test_dangling_lifecycle_is_refused_before_write(self, tmp_path, bad):
        ledger = store(tmp_path)
        with pytest.raises(InterpretationIntegrityError):
            ledger.append(bad())
        assert ledger.load().revision.record_count == 0

    def test_second_closure_is_refused_before_write(self, tmp_path):
        ledger = store(tmp_path)
        root = spi()
        first, second = close(root), close(root, T0 + timedelta(minutes=40))
        ledger.append(root)
        ledger.append(first)
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.append(second)
        assert error.value.error_code == "INTERPRETATION_MULTIPLE_CLOSURES"
        assert ledger.load().revision.record_count == 2

    def test_forged_record_is_revalidated_before_hashing_or_write(self, tmp_path):
        ledger = store(tmp_path)
        forged = SourcePropertyInterpretation.model_construct(
            **{**spi().model_dump(), "property": {"json_pointer": "bad"}})
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.append(forged)
        assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"
        assert ledger.load().revision.record_count == 0


class TestLineage:
    def test_partial_and_full_multi_parent_convergence_compute_honest_tips(
            self, tmp_path):
        ledger = store(tmp_path)
        roots = (spi(note="a"), spi(note="b"), spi(note="c"))
        for record in roots:
            ledger.append(record)
        partial = spi(parents=(roots[0].record_id,), note="partial")
        ledger.append(partial)
        key = (SUBJECT, PROP, "quantity_kind")
        assert {r.record_id for r in ledger.load(
        ).current_interpretation_tips_by_property_dimension[key]} == {
            roots[1].record_id, roots[2].record_id, partial.record_id}
        converge = spi(parents=tuple(r.record_id for r in ledger.load(
        ).current_interpretation_tips_by_property_dimension[key]), note="all")
        ledger.append(converge)
        assert ledger.load().current_interpretation_tips_by_property_dimension[
            key] == (converge,)

    @pytest.mark.parametrize("change", ["property", "subject", "dimension"])
    def test_parent_must_share_exact_pair_and_dimension(self, tmp_path, change):
        ledger = store(tmp_path)
        root = spi()
        ledger.append(root)
        kwargs = {"parents": (root.record_id,)}
        if change == "property":
            kwargs["prop"] = PROP.model_copy(update={"item_key": "other"})
        elif change == "subject":
            kwargs["subject"] = SUBJECT.model_copy(update={"source_id": "other"})
        else:
            kwargs["body"] = UnitInterpretation(dimension="unit", unit=UNIT)
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.append(spi(**kwargs))
        assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"
        assert ledger.load().revision.record_count == 1

    def test_dangling_parent_refused_at_append(self, tmp_path):
        ledger = store(tmp_path)
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.append(spi(parents=("spi_" + "f" * 64,)))
        assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"

    def test_cycle_refused_by_collection_validation(self):
        first, second = spi(note="first"), spi(note="second")
        first = first.model_copy(update={"supersedes": (second.record_id,)})
        second = second.model_copy(update={"supersedes": (first.record_id,)})
        with pytest.raises(InterpretationIntegrityError) as error:
            validate_record_collection(
                "demo-printer", {first.record_id: first, second.record_id: second},
                verify_hashes=False)
        assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"


class TestClosuresAndLifecycleIndexes:
    def test_closure_narrows_unknown_or_unbounded_and_preserves_declared_scope(
            self, tmp_path):
        for end_kind in ("unknown", "unbounded"):
            ledger = InterpretationStore(tmp_path / end_kind)
            root = spi(applies=scope(end_kind))
            amendment = close(root)
            ledger.append(root)
            ledger.append(amendment)
            loaded = ledger.load()
            assert loaded.closure_records[root.record_id] == (
                amendment.record_id,)
            assert loaded.effective_applies[root.record_id].end_boundary.kind == (
                "declared")
            assert root.applies.end_boundary.kind == end_kind

    def test_declared_end_and_end_not_after_start_are_refused(self, tmp_path):
        for index, (root, end) in enumerate((
            (spi(applies=scope("declared")), T0 + timedelta(minutes=30)),
            (spi(applies=scope()), T0),
        )):
            ledger = InterpretationStore(tmp_path / f"case-{index}")
            ledger.append(root)
            with pytest.raises(InterpretationIntegrityError) as error:
                ledger.append(close(root, end))
            assert error.value.error_code == "INTERPRETATION_CLOSURE_INVALID"

    def test_supersession_and_retraction_links_are_both_preserved(self, tmp_path):
        ledger = store(tmp_path)
        root = spi()
        successor = spi(parents=(root.record_id,), note="successor")
        withdrawal = retract(root)
        for record in (root, successor, withdrawal):
            ledger.append(record)
        loaded = ledger.load()
        assert loaded.interpretation_superseded_by[root.record_id] == (
            successor.record_id,)
        assert loaded.retracted_by[root.record_id] == (withdrawal.record_id,)


class TestAllOrNothingLoadAndReplay:
    def test_crafted_dangling_record_invalidates_whole_load(self, tmp_path):
        ledger = store(tmp_path)
        ledger.append(spi())
        bad = retract(spi(note="absent"))
        payload = {**canonical_payload(bad), "record_id": bad.record_id}
        (ledger.records_dir / f"{bad.record_id}.json").write_text(
            json.dumps(payload), encoding="utf-8")
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.load()
        assert error.value.error_code == "INTERPRETATION_RETRACTS_INVALID"

    def test_ancestor_replay_revives_tip_and_successor_requires_ancestry(
            self, tmp_path):
        ledger = store(tmp_path)
        root = spi()
        successor = spi(parents=(root.record_id,), note="successor")
        ledger.append(root)
        ledger.append(successor)
        key = (SUBJECT, PROP, "quantity_kind")
        replayed = ledger.load_revision((root.record_id,))
        assert replayed.current_interpretation_tips_by_property_dimension[key] == (
            root,)
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.load_revision((successor.record_id,))
        assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"

    @pytest.mark.parametrize("membership", [
        ("not-an-id",), ("spi_" + "a" * 64,) * 2,
    ])
    def test_replay_refuses_invalid_or_duplicate_membership(self, tmp_path,
                                                            membership):
        ledger = store(tmp_path)
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.load_revision(membership)
        assert error.value.error_code == "INTERPRETATION_REVISION_INVALID"

    def test_empty_replay_does_not_hide_a_destroyed_store(self, tmp_path):
        ledger = store(tmp_path)
        ledger.records_dir.rmdir()
        with pytest.raises(InterpretationIntegrityError) as error:
            ledger.load_revision(())
        assert error.value.error_code == "INTERPRETATION_STORAGE_FAILURE"

    def test_rejection_is_standalone_and_indexed_without_references(self,
                                                                    tmp_path):
        ledger = store(tmp_path)
        rejection = build_record(
            InterpretationRejection, subject=SUBJECT, property=PROP,
            rejected_interpretation=QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=Q_TEMP),
            proposed_applies=scope(), recorded_at=T0, authority=AUTH, note="")
        ledger.append(rejection)
        loaded = ledger.load()
        assert loaded.rejections == {rejection.record_id: rejection}
        assert loaded.interpretations == {}
