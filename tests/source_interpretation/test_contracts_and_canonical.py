"""ES-001 Group 5: source-interpretation records and canonical identity."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from backend.identity_binding.contracts import (
    AppliesScope,
    AuthorityRef,
    DeclaredBoundary,
)
from backend.model_kernel import (
    ObservationRoleReference,
    QuantityKindReference,
    UnitReference,
)
from backend.source_interpretation import (
    InterpretationClosure,
    InterpretationRejection,
    InterpretationRetraction,
    InterpretationRevision,
    ObservationRoleInterpretation,
    QuantityKindInterpretation,
    SourcePropertyInterpretation,
    UnitInterpretation,
    build_record,
    canonical_bytes,
    compute_record_id,
    compute_revision_id,
    verify_record_id,
)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

T0 = datetime(2026, 8, 13, 12, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="es001_contract_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROPERTY = SourcePropertyRef(
    extraction_route="api:moonraker:v1", item_key="printer_objects",
    json_pointer="/result/status/extruder/temperature")
APPLIES = AppliesScope(
    axis="ingestion_received_at",
    start_boundary=DeclaredBoundary(kind="declared", at=T0),
    end_boundary=DeclaredBoundary(kind="declared", at=T0 + timedelta(hours=1)),
    interval_semantics="half_open")
QUANTITY = QuantityKindReference(system_id="project_local",
                                 system_edition="ohk-quantities-1",
                                 code="temperature")
ROLE = ObservationRoleReference(system_id="project_local",
                                system_edition="ohk-observation-roles-1",
                                code="measured_actual")
UNIT = UnitReference(system_id="project_local",
                     system_edition="ohk-units-1", code="degree_celsius")


def interpretation(body=None, supersedes=()):
    return build_record(
        SourcePropertyInterpretation, subject=SUBJECT, property=PROPERTY,
        interpretation=body or QuantityKindInterpretation(
            dimension="quantity_kind", quantity_kind=QUANTITY),
        applies=APPLIES, supersedes=supersedes, recorded_at=T0,
        authority=AUTHORITY, note="")


class TestRecordContracts:
    def test_each_interpretation_dimension_round_trips_verbatim(self):
        bodies = (
            QuantityKindInterpretation(dimension="quantity_kind",
                                       quantity_kind=QUANTITY),
            ObservationRoleInterpretation(dimension="observation_role",
                                          observation_role=ROLE),
            UnitInterpretation(dimension="unit", unit=UNIT),
        )
        records = tuple(interpretation(body) for body in bodies)
        assert tuple(record.interpretation for record in records) == bodies
        assert all(record.subject == SUBJECT and record.property == PROPERTY
                   for record in records)
        assert all(record.record_id.startswith("spi_") for record in records)

    def test_parent_set_is_canonical_identity_and_duplicates_are_refused(self):
        parents = ("spi_" + "b" * 64, "spi_" + "a" * 64)
        forward = interpretation(supersedes=parents)
        reversed_ = interpretation(supersedes=parents[::-1])
        assert forward.supersedes == tuple(sorted(parents))
        assert forward.record_id == reversed_.record_id
        from backend.source_interpretation import InterpretationIntegrityError
        with pytest.raises(InterpretationIntegrityError) as error:
            interpretation(supersedes=(parents[0], parents[0]))
        assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"

    def test_self_supersession_is_refused_even_for_forged_id(self):
        candidate = interpretation()
        with pytest.raises(ValidationError):
            SourcePropertyInterpretation(
                **{**candidate.model_dump(),
                   "supersedes": (candidate.record_id,)})

    def test_lifecycle_and_rejection_shapes_have_distinct_prefixes(self):
        assertion = interpretation()
        retraction = build_record(
            InterpretationRetraction, retracts=assertion.record_id,
            recorded_at=T0, authority=AUTHORITY, note="")
        closure = build_record(
            InterpretationClosure, closes=assertion.record_id,
            end=T0 + timedelta(minutes=30), recorded_at=T0,
            authority=AUTHORITY, note="")
        rejection = build_record(
            InterpretationRejection, subject=SUBJECT, property=PROPERTY,
            rejected_interpretation=UnitInterpretation(
                dimension="unit", unit=UNIT), proposed_applies=APPLIES,
            recorded_at=T0, authority=AUTHORITY, note="")
        assert retraction.record_id.startswith("spr_")
        assert closure.record_id.startswith("spc_")
        assert rejection.record_id.startswith("spj_")
        fields = type(rejection).model_fields
        assert "retracts" not in fields
        assert "anchor_id" not in " ".join(fields)

    def test_extra_source_evidence_and_anchor_fields_are_impossible(self):
        from backend.source_interpretation import InterpretationIntegrityError

        fields = dict(
            subject=SUBJECT, property=PROPERTY,
            interpretation=UnitInterpretation(dimension="unit", unit=UNIT),
            applies=APPLIES, supersedes=(), recorded_at=T0,
            authority=AUTHORITY, note="")
        with pytest.raises(InterpretationIntegrityError):
            build_record(SourcePropertyInterpretation, **fields,
                         target_anchor_id="var_" + "a" * 32)
        with pytest.raises(InterpretationIntegrityError):
            build_record(SourcePropertyInterpretation, **fields,
                         value_json="60.4")


class TestCanonicalIdentity:
    def test_full_sha256_identity_verifies_and_content_changes_it(self):
        record = interpretation()
        assert len(record.record_id) == 4 + 64
        assert verify_record_id(record)
        assert compute_record_id(record) == record.record_id
        changed = build_record(
            SourcePropertyInterpretation,
            **{**record.model_dump(exclude={"record_id"}), "note": "changed"})
        assert changed.record_id != record.record_id

    def test_canonical_bytes_are_compact_sorted_utc_and_id_free(self):
        record = interpretation()
        payload = canonical_bytes(record).decode()
        assert '"record_id"' not in payload
        assert ": " not in payload and ", " not in payload
        assert "+00:00" in payload

    def test_equal_instants_under_offsets_hash_identically(self):
        offset = timezone(timedelta(hours=2))
        shifted = build_record(
            SourcePropertyInterpretation, subject=SUBJECT, property=PROPERTY,
            interpretation=QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=QUANTITY),
            applies=APPLIES, supersedes=(),
            recorded_at=T0.astimezone(offset), authority=AUTHORITY, note="")
        assert shifted.record_id == interpretation().record_id

    def test_revision_material_is_domain_tagged_set_and_membership(self):
        import hashlib

        ids = tuple(sorted((interpretation().record_id,
                            interpretation(UnitInterpretation(
                                dimension="unit", unit=UNIT)).record_id)))
        revision_id = compute_revision_id("demo-printer", ids)
        material = "interpretations\ndemo-printer\n" + "\n".join(ids)
        assert revision_id == "irv_" + hashlib.sha256(
            material.encode()).hexdigest()
        assert revision_id.startswith("irv_")
        revision = InterpretationRevision(
            revision_id=revision_id, record_ids=ids, record_count=2,
            interpretation_set_id="demo-printer")
        assert revision.record_ids == ids
        assert compute_revision_id("other-set", ids) != revision_id
        assert compute_revision_id("demo-printer", ids[:1]) != revision_id
        assert compute_revision_id("demo-printer", ids[::-1]) == revision_id

    def test_shared_canonical_vectors_have_byte_parity_without_shared_code(self):
        from backend.identity_binding import canonical as binding_canonical

        for vector in (AUTHORITY, APPLIES, SUBJECT, PROPERTY, QUANTITY, UNIT):
            assert canonical_bytes(vector) == binding_canonical.canonical_bytes(
                vector)

    def test_canonical_module_has_no_contract_import(self):
        import ast
        from pathlib import Path

        source = Path("backend/source_interpretation/canonical.py").read_text()
        imports = {
            alias.name
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        assert not any(name.endswith("contracts") for name in imports)

    def test_revision_refuses_unsorted_duplicate_or_wrong_identity(self):
        first = interpretation().record_id
        second = interpretation(UnitInterpretation(
            dimension="unit", unit=UNIT)).record_id
        for ids, count, revision_id in (
            ((second, first), 2, compute_revision_id(
                "demo-printer", (second, first))),
            ((first, first), 2, compute_revision_id(
                "demo-printer", (first, first))),
            ((first,), 2, compute_revision_id("demo-printer", (first,))),
            ((first,), 1, "irv_" + "0" * 64),
        ):
            with pytest.raises(ValidationError):
                InterpretationRevision(
                    revision_id=revision_id, record_ids=ids,
                    record_count=count, interpretation_set_id="demo-printer")


class TestHardening:
    def test_build_record_wraps_invalid_inputs_in_typed_integrity_error(self):
        from backend.source_interpretation import InterpretationIntegrityError

        with pytest.raises(InterpretationIntegrityError) as error:
            build_record(SourcePropertyInterpretation, subject=SUBJECT)
        assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"
        assert str(T0) not in error.value.message

    def test_contracts_revalidate_forged_instances(self):
        forged = QuantityKindInterpretation.model_construct(
            dimension="unit", quantity_kind=QUANTITY)
        with pytest.raises(ValidationError):
            SourcePropertyInterpretation(
                record_id="spi_" + "0" * 64, subject=SUBJECT,
                property=PROPERTY, interpretation=forged, applies=APPLIES,
                recorded_at=T0, authority=AUTHORITY)
