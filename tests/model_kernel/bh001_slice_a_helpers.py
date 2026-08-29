"""Synthetic BH-001 Slice A records; never imported by committed fixtures."""

from datetime import UTC, datetime

import backend.model_kernel as kernel
import backend.system_identity as identity

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    VAR_A,
    VAR_B,
    constraint_signature,
    observation_role,
    registration as entity_registration,
    variable_registration,
)


T0 = datetime(2026, 8, 29, 12, 0, tzinfo=UTC)
T1 = datetime(2026, 8, 29, 13, 0, tzinfo=UTC)
BEHAVIOR_A = "bhv_" + "a" * 32
BEHAVIOR_B = "bhv_" + "b" * 32
AS_DESIGNED = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
AS_BUILT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_built")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="bh001_test_fixture",
    method="manual_declaration")
REGISTRATION_DECLARATION = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly registers this BH relation.")
RULE_DECLARATION = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly declares exact numeric equality.")


def behavior_anchor(anchor_id=BEHAVIOR_A, name="Synthetic equality behavior",
                    role=None):
    return identity.BehaviorAnchor(
        anchor_id=anchor_id, namespace="demo-printer", display_name=name,
        role_name=role)


def variable_records(*, owners=(ENT_A, ENT_A)):
    entities = tuple(entity_registration(owner)
                     for owner in dict.fromkeys(owners))
    first = variable_registration(VAR_A, owner=owners[0], name="Variable A")
    second = variable_registration(VAR_B, owner=owners[1], name="Variable B")
    return (*entities, first, second)


def variable_record_map(*, owners=(ENT_A, ENT_A)):
    records = variable_records(owners=owners)
    return {record.anchor.anchor_id: record for record in records
            if record.record_kind == "variable_registration"}


def registration_evidence(*, owners=(ENT_A, ENT_A), extra=()):
    variables = variable_record_map(owners=owners)
    citations = tuple(kernel.ModelRecordEvidence(
        kind="model_record", record_id=variables[variable_id].record_id)
        for variable_id in sorted((VAR_A, VAR_B)))
    return (*citations, REGISTRATION_DECLARATION, *extra)


def behavior_registration(*, behavior_anchor_id=BEHAVIOR_A,
                          participants=(VAR_A, VAR_B), owners=(ENT_A, ENT_A),
                          evidence=None, recorded_at=T0, note="", **overrides):
    fields = dict(
        anchor=behavior_anchor(behavior_anchor_id),
        participant_variable_anchor_ids=participants,
        rule_family="exact_numeric_equality",
        evidence=(registration_evidence(owners=owners)
                  if evidence is None else evidence),
        recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return kernel.build_record(kernel.BehaviorRegistration, **fields)


def semantic_lock(variable_anchor_id=VAR_A, *, role="measured",
                  quantity="temperature", unit="degree_celsius"):
    signature = constraint_signature().model_copy(update={
        "quantity_kind": constraint_signature().quantity_kind.model_copy(
            update={"code": quantity}),
        "observation_role": observation_role(role),
        "unit": constraint_signature().unit.model_copy(update={"code": unit}),
    })
    return kernel.BehaviorVariableSemanticLock(
        variable_anchor_id=variable_anchor_id, signature=signature)


def declaration_evidence(registration, *, statement=RULE_DECLARATION,
                         extra=()):
    return (
        kernel.ModelRecordEvidence(
            kind="model_record", record_id=registration.record_id),
        statement,
        *extra,
    )


def behavior_declaration(registration=None, *, behavior_anchor_id=BEHAVIOR_A,
                         context=AS_DESIGNED, locks=None, rule=None,
                         evidence=None, supersedes=(), recorded_at=T0,
                         note="", **overrides):
    registration = registration or behavior_registration(
        behavior_anchor_id=behavior_anchor_id)
    fields = dict(
        behavior_anchor_id=behavior_anchor_id,
        context=context,
        participant_semantics=(
            (semantic_lock(VAR_A), semantic_lock(VAR_B, role="reported"))
            if locks is None else locks),
        rule=(kernel.ExactNumericEqualityRule(kind="exact_numeric_equality")
              if rule is None else rule),
        evaluation_basis="same_acquisition_cohort",
        evidence=(declaration_evidence(registration)
                  if evidence is None else evidence),
        supersedes=supersedes, recorded_at=recorded_at,
        authority=AUTHORITY, note=note)
    fields.update(overrides)
    return kernel.build_record(kernel.BehaviorRuleDeclaration, **fields)


def behavior_withdrawal(target, *, recorded_at=T1, note=""):
    return kernel.build_record(
        kernel.BehaviorRuleWithdrawal, withdraws=target.record_id,
        recorded_at=recorded_at, authority=AUTHORITY, note=note)


def world(tmp_path, *extra, behavior_anchor_id=BEHAVIOR_A,
          owners=(ENT_A, ENT_A), include_registration=True):
    store = kernel.ModelStore(tmp_path / "demo-printer")
    for record in variable_records(owners=owners):
        store.append(record)
    registration = behavior_registration(
        behavior_anchor_id=behavior_anchor_id, owners=owners)
    if include_registration:
        store.append(registration)
    for record in extra:
        store.append(record)
    return store


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}
