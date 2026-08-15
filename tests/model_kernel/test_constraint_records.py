"""CN-001 Group C/D envelope-level contracts for the two new record kinds.

Store-level behaviour (dangling identity/target, cross-lineage supersession,
cycles, competing tips, convergence, replay, evidence membership closure) is
covered in the Slice A store tests; this module pins the record envelope
itself — content-derived ids, evidence canonicalisation, the absence of any
lifecycle field on a registration, and the declaration's self-consistency
validators (predicate↔variable, self-supersede, well-formed parents)."""

import re

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    ConstraintRegistration,
    ModelRecord,
    ModelRecordEvidence,
    OwnerDeclarationEvidence,
    SourceRawRecordEvidence,
    VariableConstraintDeclaration,
)
from backend.model_kernel.contracts import (
    MODEL_RECORD_ID_PATTERN,
    ObservationRoleReference,
    QuantityKindReference,
)
from tests.model_kernel.builders import (
    AUTHORITY,
    CON_A,
    CONSTRAINT_EVIDENCE,
    T0,
    VAR_A,
    VAR_B,
    constraint_declaration,
    constraint_registration,
    scalar_predicate,
)

CRG = "crg_" + "1" * 64
VCN = "vcn_" + "1" * 64


def _registration(**overrides):
    fields = dict(
        record_id=CRG,
        constraint_anchor_id=CON_A,
        variable_anchor_id=VAR_A,
        evidence=CONSTRAINT_EVIDENCE,
        recorded_at=T0,
        authority=AUTHORITY,
        note="",
    )
    fields.update(overrides)
    return ConstraintRegistration(**fields)


def _declaration(**overrides):
    fields = dict(
        record_id=VCN,
        constraint_anchor_id=CON_A,
        variable_anchor_id=VAR_A,
        lock_quantity_kind=None,
        lock_observation_role=None,
        predicate=scalar_predicate(variable_anchor_id=VAR_A),
        evidence=CONSTRAINT_EVIDENCE,
        supersedes=(),
        recorded_at=T0,
        authority=AUTHORITY,
        note="",
    )
    fields.update(overrides)
    return VariableConstraintDeclaration(**fields)


# --------------------------------------------------------------- Group C
def test_registration_builds_with_a_content_derived_crg_id():
    record = constraint_registration()
    assert record.record_id.startswith("crg_")
    assert record.record_kind == "constraint_registration"
    # idempotent: identical content -> identical id
    assert constraint_registration().record_id == record.record_id


def test_registration_id_is_excluded_from_its_own_hash():
    a = constraint_registration(note="first")
    b = constraint_registration(note="second")
    assert a.record_id != b.record_id
    assert constraint_registration(note="first").record_id == a.record_id


def test_registration_rejects_empty_evidence():
    with pytest.raises(ValidationError):
        _registration(evidence=())


def test_registration_canonicalizes_evidence_order_and_duplicates():
    dup = (CONSTRAINT_EVIDENCE[0], CONSTRAINT_EVIDENCE[0])
    record = constraint_registration(evidence=dup)
    assert len(record.evidence) == 1
    other = OwnerDeclarationEvidence(
        kind="owner_declaration", statement="another synthetic reason")
    first = constraint_registration(evidence=(CONSTRAINT_EVIDENCE[0], other))
    second = constraint_registration(evidence=(other, CONSTRAINT_EVIDENCE[0]))
    assert first.evidence == second.evidence


def test_registration_accepts_every_evidence_arm_of_the_union():
    arms = (
        OwnerDeclarationEvidence(
            kind="owner_declaration",
            statement="synthetic owner constraint disclaimer"),
        ModelRecordEvidence(kind="model_record",
                            record_id="reg_" + "0" * 64),
        SourceRawRecordEvidence(
            kind="source_raw_record", raw_record_id="0" * 32,
            payload_checksum="sha256:" + "0" * 64),
    )
    record = constraint_registration(evidence=arms)
    assert len(record.evidence) == len(arms)
    shuffled = constraint_registration(evidence=tuple(reversed(arms)))
    assert record.evidence == shuffled.evidence


def test_registration_carries_the_synthetic_disclaimer_in_its_evidence():
    record = constraint_registration()
    assert any(
        getattr(ref, "statement", None)
        == "synthetic test constraint registration"
        for ref in record.evidence)


def test_registration_has_no_lifecycle_field():
    record = constraint_registration()
    for forbidden in ("supersedes", "superseded_by", "withdrawn_by",
                      "status", "lifecycle", "withdrawal"):
        assert not hasattr(record, forbidden), forbidden
    with pytest.raises(ValidationError):
        _registration(supersedes=("vcn_" + "0" * 64,))
    with pytest.raises(ValidationError):
        _registration(withdrawn_by=())


def test_registration_id_matches_the_record_id_grammar():
    assert re.fullmatch(MODEL_RECORD_ID_PATTERN, "crg_" + "0" * 64)


# --------------------------------------------------------------- Group D
def test_declaration_builds_with_a_content_derived_vcn_id():
    record = constraint_declaration()
    assert record.record_id.startswith("vcn_")
    assert record.record_kind == "variable_constraint_declaration"
    assert constraint_declaration().record_id == record.record_id


def test_declaration_threshold_change_yields_a_new_id():
    a = constraint_declaration(predicate=scalar_predicate(threshold="60"))
    b = constraint_declaration(predicate=scalar_predicate(threshold="61"))
    assert a.record_id != b.record_id
    assert (constraint_declaration(predicate=scalar_predicate(threshold="60"))
            .record_id == a.record_id)


def test_declaration_rejects_empty_evidence():
    with pytest.raises(ValidationError):
        _declaration(evidence=())


def test_declaration_predicate_must_target_the_declared_variable():
    mismatched = scalar_predicate(variable_anchor_id=VAR_B)
    with pytest.raises(ValidationError):
        _declaration(variable_anchor_id=VAR_A, predicate=mismatched)


def test_declaration_rejects_a_self_supersede():
    with pytest.raises(ValidationError):
        _declaration(supersedes=(VCN,))


def test_declaration_rejects_a_non_vcn_parent_id():
    with pytest.raises(ValidationError):
        _declaration(supersedes=("vsp_" + "0" * 64,))


def test_declaration_rejects_forbidden_extra_fields():
    record = constraint_declaration()
    for forbidden in ("severity", "grade", "alarm", "recommendation",
                      "cause", "lower", "upper", "tolerance",
                      "other_variable_anchor_id"):
        assert not hasattr(record, forbidden), forbidden
    with pytest.raises(ValidationError):
        _declaration(severity="warning")
    with pytest.raises(ValidationError):
        _declaration(tolerance="0.1")


def test_declaration_lock_fields_are_optional_and_carried():
    bare = constraint_declaration()
    assert bare.lock_quantity_kind is None
    assert bare.lock_observation_role is None
    locked = constraint_declaration(
        lock_quantity_kind=QuantityKindReference(
            system_id="project_local", system_edition="ohk-semantics-1",
            code="temperature"),
        lock_observation_role=ObservationRoleReference(
            system_id="project_local", system_edition="ohk-semantics-1",
            code="measured"),
    )
    assert locked.lock_quantity_kind is not None
    assert locked.lock_observation_role is not None


def test_both_records_are_members_of_the_model_record_union():
    assert isinstance(constraint_registration(), ModelRecord)
    assert isinstance(constraint_declaration(), ModelRecord)


def test_model_record_evidence_cites_the_new_record_kinds():
    assert ModelRecordEvidence(
        kind="model_record", record_id="crg_" + "0" * 64)
    assert ModelRecordEvidence(
        kind="model_record", record_id="vcn_" + "0" * 64)