"""VP-001 Slice A red baseline for the two immutable record contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel


T0 = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)
VARIABLE = "var_" + "b" * 32
PORT = "prt_" + "1" * 32
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="vp001_test_fixture",
    method="manual_declaration")
EVIDENCE = (kernel.OwnerDeclarationEvidence(
    kind="owner_declaration", statement="synthetic VP-001 association"),)


def association(**overrides):
    fields = dict(
        variable_anchor_id=VARIABLE, port_anchor_id=PORT, context=CONTEXT,
        evidence=EVIDENCE, supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(kernel.VariablePortAssociation, **fields)


def withdrawal(withdraws="vpa_" + "a" * 64, **overrides):
    fields = dict(withdraws=withdraws, recorded_at=T0,
                  authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(
        kernel.VariablePortAssociationWithdrawal, **fields)


def test_exact_record_shapes_discriminators_and_prefixes():
    vpa = association()
    vpw = withdrawal()
    assert tuple(type(vpa).model_fields) == (
        "record_kind", "schema_version", "record_id",
        "variable_anchor_id", "port_anchor_id", "context", "evidence",
        "supersedes", "recorded_at", "authority", "note")
    assert tuple(type(vpw).model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert (vpa.record_kind, vpa.schema_version) == (
        "variable_port_association", "1")
    assert (vpw.record_kind, vpw.schema_version) == (
        "variable_port_association_withdrawal", "1")
    assert vpa.record_id.startswith("vpa_") and len(vpa.record_id) == 68
    assert vpw.record_id.startswith("vpw_") and len(vpw.record_id) == 68


@pytest.mark.parametrize("field,value", [
    ("owner_entity_anchor_id", "ent_" + "a" * 32),
    ("association_role", "measured_at"),
    ("unit", "degree_celsius"),
    ("value", "60.4"),
    ("compatible", True),
    ("active", True),
    ("flow", "present"),
    ("as_of", T0),
])
def test_association_forbids_identity_state_semantic_and_behavior_fields(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        association(**{field: value})
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("field,value", [
    ("evidence", EVIDENCE),
    ("context", CONTEXT),
    ("supersedes", ("vpa_" + "a" * 64,)),
    ("outcome", "false"),
    ("reason", "removed"),
    ("target", "vpa_" + "a" * 64),
])
def test_withdrawal_is_a_minimal_event_and_forbids_negative_claim_fields(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        withdrawal(**{field: value})
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_evidence_is_nonempty_canonical_and_parents_are_canonical():
    with pytest.raises(kernel.ModelIntegrityError):
        association(evidence=())
    extra = EVIDENCE[0].model_copy(update={"statement": "other evidence"})
    assert association(evidence=(extra, *EVIDENCE)).record_id == association(
        evidence=(*EVIDENCE, extra)).record_id

    first = association(note="first")
    second = association(note="second")
    forward = association(supersedes=(first.record_id, second.record_id),
                          note="merge")
    reverse = association(supersedes=(second.record_id, first.record_id),
                          note="merge")
    assert forward.supersedes == tuple(sorted((first.record_id,
                                               second.record_id)))
    assert forward.record_id == reverse.record_id


@pytest.mark.parametrize("parents", [
    ("vpa_" + "a" * 64, "vpa_" + "a" * 64),
    ("pif_" + "a" * 64,),
    ("vpa_NOT_HEX",),
])
def test_duplicate_and_non_vpa_parents_are_rejected(parents):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        association(supersedes=parents)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("target", [
    "vpw_" + "a" * 64,
    "pif_" + "a" * 64,
    "vpa_NOT_HEX",
])
def test_withdrawal_targets_only_a_vpa(target):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        withdrawal(withdraws=target)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_vpa_is_citable_and_vpw_is_uncitable():
    cited = kernel.ModelRecordEvidence(
        kind="model_record", record_id="vpa_" + "a" * 64)
    assert cited.record_id.startswith("vpa_")
    with pytest.raises(ValidationError):
        kernel.ModelRecordEvidence(
            kind="model_record", record_id="vpw_" + "a" * 64)


def test_model_record_union_revalidates_hostile_nested_context_and_evidence():
    valid = association()
    assert type(TypeAdapter(kernel.ModelRecord).validate_python(
        valid.model_dump())) is kernel.VariablePortAssociation

    hostile_context = CONTEXT.model_copy(update={"view": "future_view"})
    forged = valid.model_copy(update={"context": hostile_context})
    with pytest.raises(ValidationError):
        TypeAdapter(kernel.ModelRecord).validate_python(forged)

    hostile_evidence = EVIDENCE[0].model_copy(update={"statement": ""})
    forged = valid.model_copy(update={"evidence": (hostile_evidence,)})
    with pytest.raises(ValidationError):
        TypeAdapter(kernel.ModelRecord).validate_python(forged)


def test_slice_a_exports_exactly_two_vp_names_and_no_reserved_query_surface():
    assert len(kernel.__all__) == 113
    assert {name for name in kernel.__all__ if "VariablePort" in name} == {
        "VariablePortAssociation", "VariablePortAssociationWithdrawal"}
    assert kernel.VariablePortAssociation is not None
    assert kernel.VariablePortAssociationWithdrawal is not None
    for forbidden in (
        "VariablePortAssociationResult", "VariablePortsResult",
        "PortVariablesResult", "VariablePortAssertionDisclosureResult",
        "AssociatedPortVariableStateResult",
    ):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)
    for method in (
        "variable_port_association", "ports_associated_with_variable",
        "variables_associated_with_port", "variable_port_assertion",
    ):
        assert not hasattr(kernel.ModelQueries, method)
