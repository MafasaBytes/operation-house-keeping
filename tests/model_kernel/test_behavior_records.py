"""BH-001 Slice A red-first tests for exact role-free record contracts."""

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel

from tests.model_kernel.bh001_slice_a_helpers import (
    AS_DESIGNED,
    AUTHORITY,
    BEHAVIOR_A,
    REGISTRATION_DECLARATION,
    RULE_DECLARATION,
    T0,
    VAR_A,
    VAR_B,
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
    semantic_lock,
)


def test_behavior_registration_exact_contract_and_defaults():
    value = behavior_registration()
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "anchor",
        "participant_variable_anchor_ids", "rule_family", "evidence",
        "recorded_at", "authority", "note")
    assert (value.record_kind, value.schema_version) == (
        "behavior_registration", "1")
    assert value.record_id.startswith("brg_") and len(value.record_id) == 68
    assert value.participant_variable_anchor_ids == tuple(sorted((VAR_A, VAR_B)))
    assert value.rule_family == "exact_numeric_equality"


def test_behavior_declaration_exact_contract_and_defaults():
    value = behavior_declaration()
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "behavior_anchor_id",
        "context", "participant_semantics", "rule", "evaluation_basis",
        "evidence", "supersedes", "recorded_at", "authority", "note")
    assert (value.record_kind, value.schema_version) == (
        "behavior_rule_declaration", "1")
    assert value.record_id.startswith("bhd_") and len(value.record_id) == 68
    assert value.evaluation_basis == "same_acquisition_cohort"
    assert value.rule.kind == "exact_numeric_equality"
    assert tuple(lock.variable_anchor_id
                 for lock in value.participant_semantics) == (VAR_A, VAR_B)


def test_behavior_lock_and_rule_have_exact_minimal_contracts():
    lock = semantic_lock()
    rule = kernel.ExactNumericEqualityRule(kind="exact_numeric_equality")
    assert tuple(type(lock).model_fields) == ("variable_anchor_id", "signature")
    assert tuple(type(rule).model_fields) == ("kind",)
    for attack in (
        {"kind": "exact_numeric_equality", "tolerance": "0.1"},
        {"kind": "exact_numeric_equality", "operator": "=="},
        {"kind": "affine"},
    ):
        with pytest.raises(ValidationError):
            kernel.ExactNumericEqualityRule(**attack)


def test_behavior_withdrawal_exact_minimal_contract():
    target = behavior_declaration()
    value = behavior_withdrawal(target)
    assert tuple(type(value).model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert (value.record_kind, value.schema_version) == (
        "behavior_rule_withdrawal", "1")
    assert value.record_id.startswith("bhw_") and len(value.record_id) == 68


@pytest.mark.parametrize("field,value", [
    ("context", AS_DESIGNED),
    ("supersedes", ("brg_" + "a" * 64,)),
    ("withdraws", "brg_" + "a" * 64),
    ("owner_entity_anchor_id", "ent_" + "a" * 32),
    ("participant_roles", ("input", "output")),
    ("port_anchor_id", "prt_" + "a" * 32),
    ("direction", "left_to_right"),
    ("state", "active"),
])
def test_registration_forbids_context_lifecycle_owner_role_and_port_fields(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        behavior_registration(**{field: value})
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("field,value", [
    ("coefficient", "1"),
    ("offset", "0"),
    ("tolerance", "0.01"),
    ("expression", "a == b"),
    ("direction", "input_to_output"),
    ("participant_role", "input"),
    ("port_anchor_id", "prt_" + "a" * 32),
    ("variable_port_association_id", "vpa_" + "a" * 64),
    ("value", "1"),
    ("outcome", "equal"),
    ("safe", True),
])
def test_declaration_forbids_expression_direction_port_value_and_verdict_fields(
        field, value):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        behavior_declaration(**{field: value})
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("field,value", [
    ("evidence", (RULE_DECLARATION,)),
    ("context", AS_DESIGNED),
    ("supersedes", ("bhd_" + "a" * 64,)),
    ("outcome", "different"),
    ("replacement", "bhd_" + "a" * 64),
    ("reason_code", "false"),
    ("negative_behavior", True),
])
def test_withdrawal_forbids_claim_context_parent_and_negative_fields(field,
                                                                      value):
    target = behavior_declaration()
    with pytest.raises(kernel.ModelIntegrityError) as error:
        kernel.build_record(
            kernel.BehaviorRuleWithdrawal, withdraws=target.record_id,
            recorded_at=T0, authority=AUTHORITY, note="", **{field: value})
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("target", [
    "brg_" + "a" * 64,
    "bhw_" + "a" * 64,
    "vpa_" + "a" * 64,
    "bhd_NOT_HEX",
])
def test_withdrawal_target_contract_accepts_only_bhd_identity(target):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        kernel.build_record(
            kernel.BehaviorRuleWithdrawal, withdraws=target,
            recorded_at=T0, authority=AUTHORITY, note="")
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("participants", [
    (),
    (VAR_A,),
    (VAR_A, VAR_A),
    (VAR_A, VAR_B, "var_" + "c" * 32),
    (VAR_A, "prt_" + "b" * 32),
])
def test_registration_requires_exactly_two_distinct_variable_ids(participants):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        behavior_registration(participants=participants)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_registration_pair_and_declaration_locks_are_canonical_not_directional():
    forward = behavior_registration(participants=(VAR_A, VAR_B))
    reverse = behavior_registration(participants=(VAR_B, VAR_A))
    assert forward == reverse
    assert forward.record_id == reverse.record_id

    locks = (semantic_lock(VAR_A), semantic_lock(VAR_B, role="reported"))
    one = behavior_declaration(participant_semantics=locks)
    two = behavior_declaration(participant_semantics=tuple(reversed(locks)))
    assert one == two
    assert one.record_id == two.record_id


@pytest.mark.parametrize("parents", [
    ("bhd_" + "a" * 64, "bhd_" + "a" * 64),
    ("brg_" + "a" * 64,),
    ("vpa_" + "a" * 64,),
    ("bhd_NOT_HEX",),
])
def test_declaration_rejects_duplicate_or_non_bhd_parent_input(parents):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        behavior_declaration(supersedes=parents)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_declaration_rejects_self_supersession_at_direct_boundary():
    value = behavior_declaration()
    payload = value.model_dump()
    payload["supersedes"] = (value.record_id,)
    with pytest.raises(ValidationError):
        kernel.BehaviorRuleDeclaration(**payload)


def test_brgs_and_bhds_are_citable_bhw_is_not():
    for record_id in ("brg_" + "a" * 64, "bhd_" + "b" * 64):
        assert kernel.ModelRecordEvidence(
            kind="model_record", record_id=record_id).record_id == record_id
    with pytest.raises(ValidationError):
        kernel.ModelRecordEvidence(
            kind="model_record", record_id="bhw_" + "a" * 64)


def test_model_record_union_accepts_exact_three_behavior_arms():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    withdrawal = behavior_withdrawal(declaration)
    adapter = TypeAdapter(kernel.ModelRecord)
    for record in (registration, declaration, withdrawal):
        rebuilt = adapter.validate_python(record.model_dump())
        assert type(rebuilt) is type(record)


def test_kernel_public_surface_adds_only_slice_a_contracts():
    expected_new = {
        "BehaviorRegistration", "BehaviorRuleDeclaration",
        "BehaviorRuleWithdrawal", "BehaviorVariableSemanticLock",
        "ExactNumericEqualityRule",
    }
    assert len(kernel.__all__) == 131
    assert expected_new <= set(kernel.__all__)
    for forbidden in (
        "BehaviorLookupResult", "BehaviorRuleResult",
        "VariableBehaviorsResult", "BehaviorAssertionDisclosureResult",
        "BehaviorEvaluationQueries", "BehaviorEvaluationResult",
        "BehaviorParticipantSource", "BehaviorComputedRelation",
    ):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)


def test_fixed_literal_vocabularies_reject_all_future_rule_and_basis_values():
    registration = behavior_registration()
    with pytest.raises(kernel.ModelIntegrityError):
        behavior_registration(rule_family="affine")
    with pytest.raises(kernel.ModelIntegrityError):
        behavior_declaration(registration, evaluation_basis="receipt_tolerance")
    with pytest.raises(ValidationError):
        kernel.ExactNumericEqualityRule(kind="tolerant_equality")


def test_owner_evidence_contract_is_claim_bearing_not_a_role_or_direction():
    registration = behavior_registration()
    assert REGISTRATION_DECLARATION in registration.evidence
    declaration = behavior_declaration(registration)
    assert RULE_DECLARATION in declaration.evidence
    assert not hasattr(registration, "input_variable_anchor_id")
    assert not hasattr(declaration, "output_variable_anchor_id")
