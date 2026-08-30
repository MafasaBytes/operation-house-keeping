"""Synthetic ST-001 Slice A records; never imported by committed fixtures."""

from datetime import UTC, datetime

import backend.model_kernel as kernel
import backend.system_identity as identity

from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    ENT_A,
    ENT_B,
    T0 as BASE_T0,
    VAR_A,
    VAR_B,
    constraint_declaration,
    constraint_registration,
    registration as entity_registration,
    variable_registration,
)


T0 = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
T1 = datetime(2026, 8, 30, 13, 0, tzinfo=UTC)
STATE_A = "sta_" + "a" * 32
STATE_B = "sta_" + "b" * 32
AS_OPERATED = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_operated")
AS_DESIGNED = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="st001_test_fixture",
    method="manual_declaration")
REGISTRATION_DECLARATION = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly registers this state region.")
STATE_DECLARATION = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly declares this contextual state region.")


def state_anchor(anchor_id=STATE_A, name="Synthetic state", role=None):
    return identity.StateAnchor(
        anchor_id=anchor_id, namespace="demo-printer", display_name=name,
        role_name=role)


def condition_world_records(*, owner=ENT_A, second_owner=ENT_A,
                            include_second=True):
    entities = tuple(entity_registration(item)
                     for item in dict.fromkeys((owner, second_owner)))
    variable_a = variable_registration(VAR_A, owner=owner, name="Variable A")
    constraint_a = constraint_registration(
        CON_A, variable_anchor_id=VAR_A, recorded_at=BASE_T0)
    declaration_a = constraint_declaration(CON_A, recorded_at=BASE_T0)
    records = [*entities, variable_a, constraint_a, declaration_a]
    if include_second:
        variable_b = variable_registration(
            VAR_B, owner=second_owner, name="Variable B")
        constraint_b = constraint_registration(
            CON_B, variable_anchor_id=VAR_B, recorded_at=BASE_T0)
        declaration_b = constraint_declaration(CON_B, recorded_at=BASE_T0)
        records.extend((variable_b, constraint_b, declaration_b))
    return tuple(records)


def records_by_kind(*, owner=ENT_A, second_owner=ENT_A,
                    include_second=True):
    records = condition_world_records(
        owner=owner, second_owner=second_owner,
        include_second=include_second)
    return {
        kind: {record.record_id: record for record in records
               if record.record_kind == kind}
        for kind in {
            "entity_registration", "variable_registration",
            "constraint_registration", "variable_constraint_declaration",
        }
    }


def registration_evidence(*, constraints=(CON_A, CON_B), owner=ENT_A,
                          second_owner=ENT_A, extra=()):
    by_kind = records_by_kind(
        owner=owner, second_owner=second_owner,
        include_second=CON_B in constraints)
    subject = next(record for record in by_kind["entity_registration"].values()
                   if record.anchor.anchor_id == owner)
    constraint_records = {
        record.anchor.anchor_id: record
        for record in by_kind["constraint_registration"].values()
    }
    citations = (
        kernel.ModelRecordEvidence(
            kind="model_record", record_id=subject.record_id),
        *(kernel.ModelRecordEvidence(
            kind="model_record",
            record_id=constraint_records[constraint_id].record_id)
          for constraint_id in sorted(constraints)),
    )
    return (*citations, REGISTRATION_DECLARATION, *extra)


def state_registration(*, state_anchor_id=STATE_A, subject=ENT_A,
                       constraints=(CON_A, CON_B), evidence=None,
                       recorded_at=T0, note="", **overrides):
    fields = dict(
        anchor=state_anchor(state_anchor_id),
        subject_entity_anchor_id=subject,
        condition_constraint_anchor_ids=constraints,
        condition_family="all_of_constraints",
        evidence=(registration_evidence(constraints=constraints, owner=subject)
                  if evidence is None else evidence),
        recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return kernel.build_record(kernel.StateRegistration, **fields)


def pins(*, constraints=(CON_A, CON_B), declarations=None):
    if declarations is None:
        by_kind = records_by_kind(
            include_second=CON_B in constraints)[
                "variable_constraint_declaration"]
        declarations = {
            record.constraint_anchor_id: record for record in by_kind.values()
        }
    return tuple(kernel.StateConstraintDeclarationPin(
        constraint_anchor_id=constraint_id,
        constraint_declaration_record_id=declarations[
            constraint_id].record_id)
        for constraint_id in constraints)


def declaration_evidence(registration, condition_pins, *, extra=()):
    by_kind = records_by_kind(
        include_second=any(pin.constraint_anchor_id == CON_B
                           for pin in condition_pins))
    constraints = {
        record.anchor.anchor_id: record
        for record in by_kind["constraint_registration"].values()
    }
    citations = [kernel.ModelRecordEvidence(
        kind="model_record", record_id=registration.record_id)]
    for pin in condition_pins:
        citations.extend((
            kernel.ModelRecordEvidence(
                kind="model_record",
                record_id=constraints[pin.constraint_anchor_id].record_id),
            kernel.ModelRecordEvidence(
                kind="model_record",
                record_id=pin.constraint_declaration_record_id),
        ))
    return (*citations, STATE_DECLARATION, *extra)


def state_declaration(registration=None, *, state_anchor_id=STATE_A,
                      context=AS_OPERATED, condition_pins=None,
                      evidence=None, supersedes=(), recorded_at=T0,
                      note="", **overrides):
    registration = registration or state_registration(
        state_anchor_id=state_anchor_id)
    condition_pins = condition_pins or pins(
        constraints=registration.condition_constraint_anchor_ids)
    fields = dict(
        state_anchor_id=state_anchor_id, context=context,
        conditions=condition_pins,
        evaluation_basis="independent_latest_at_or_before_cutoff",
        evidence=(declaration_evidence(registration, condition_pins)
                  if evidence is None else evidence),
        supersedes=supersedes, recorded_at=recorded_at,
        authority=AUTHORITY, note=note)
    fields.update(overrides)
    return kernel.build_record(kernel.StateDeclaration, **fields)


def state_withdrawal(target, *, recorded_at=T1, note=""):
    return kernel.build_record(
        kernel.StateDeclarationWithdrawal, withdraws=target.record_id,
        recorded_at=recorded_at, authority=AUTHORITY, note=note)


def world(tmp_path, *extra, state_anchor_id=STATE_A, subject=ENT_A,
          constraints=(CON_A, CON_B), second_owner=ENT_A,
          include_registration=True):
    store = kernel.ModelStore(tmp_path / "demo-printer")
    for record in condition_world_records(
            owner=subject, second_owner=second_owner,
            include_second=CON_B in constraints):
        store.append(record)
    registration = state_registration(
        state_anchor_id=state_anchor_id, subject=subject,
        constraints=constraints)
    if include_registration:
        store.append(registration)
    for record in extra:
        store.append(record)
    return store


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}
