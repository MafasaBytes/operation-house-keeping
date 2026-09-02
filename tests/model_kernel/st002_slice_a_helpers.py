"""Synthetic ST-002 Slice A records; never imported by demo fixtures."""

from datetime import UTC, datetime

import backend.model_kernel as kernel
import backend.system_identity as identity

from tests.model_kernel.builders import ENT_A
from tests.model_kernel.st001_slice_a_helpers import (
    STATE_A,
    STATE_B,
    condition_world_records,
    state_declaration,
    state_registration,
)


T0 = datetime(2026, 9, 2, 9, 0, tzinfo=UTC)
T1 = datetime(2026, 9, 2, 10, 0, tzinfo=UTC)
TRANSITION_A = "trn_" + "a" * 32
TRANSITION_B = "trn_" + "b" * 32
AS_OPERATED = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_operated")
VIEW_INDEPENDENT = kernel.ViewIndependentContext(kind="view_independent")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="st002_test_fixture",
    method="manual_declaration")
TRANSITION_REGISTRATION_CLAIM = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly registers this transition identity.")
TRANSITION_DECLARATION_CLAIM = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority explicitly declares this exact transition meaning.")


def transition_anchor(anchor_id=TRANSITION_A, name="Synthetic transition",
                      role=None):
    return identity.TransitionAnchor(
        anchor_id=anchor_id, namespace="test-model", display_name=name,
        role_name=role)


def citation(record_id):
    return kernel.ModelRecordEvidence(kind="model_record", record_id=record_id)


def state_world_records(*, subject=ENT_A, context=AS_OPERATED):
    records = list(condition_world_records(owner=subject, second_owner=subject))
    from_registration = state_registration(
        state_anchor_id=STATE_A, subject=subject, note="from state")
    to_registration = state_registration(
        state_anchor_id=STATE_B, subject=subject, note="to state")
    from_declaration = state_declaration(
        from_registration, state_anchor_id=STATE_A, context=context,
        note="from declaration")
    to_declaration = state_declaration(
        to_registration, state_anchor_id=STATE_B, context=context,
        note="to declaration")
    records.extend((from_registration, to_registration,
                    from_declaration, to_declaration))
    return tuple(records), from_registration, to_registration, \
        from_declaration, to_declaration


def registration_evidence(from_registration, to_registration, *,
                          subject=ENT_A, extra=()):
    records, *_ = state_world_records(subject=subject)
    subject_registration = next(
        record for record in records
        if record.record_kind == "entity_registration"
        and record.anchor.anchor_id == subject)
    return (
        citation(subject_registration.record_id),
        citation(from_registration.record_id),
        citation(to_registration.record_id),
        TRANSITION_REGISTRATION_CLAIM,
        *extra,
    )


def transition_registration(*, transition_anchor_id=TRANSITION_A,
                            subject=ENT_A, from_registration=None,
                            to_registration=None, from_state=STATE_A,
                            to_state=STATE_B, evidence=None,
                            recorded_at=T0, note="", **overrides):
    if from_registration is None or to_registration is None:
        _, default_from, default_to, _, _ = state_world_records(
            subject=subject)
        from_registration = from_registration or default_from
        to_registration = to_registration or default_to
    fields = dict(
        anchor=transition_anchor(transition_anchor_id),
        subject_entity_anchor_id=subject,
        from_state_anchor_id=from_state,
        to_state_anchor_id=to_state,
        evidence=(registration_evidence(
            from_registration, to_registration, subject=subject)
                  if evidence is None else evidence),
        recorded_at=recorded_at, authority=AUTHORITY, note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.TransitionRegistration, **fields)


def declaration_evidence(registration, from_registration, to_registration,
                         from_declaration, to_declaration, *, extra=()):
    return (
        citation(registration.record_id),
        citation(from_registration.record_id),
        citation(to_registration.record_id),
        citation(from_declaration.record_id),
        citation(to_declaration.record_id),
        TRANSITION_DECLARATION_CLAIM,
        *extra,
    )


def endpoint(state_anchor_id, declaration_record_id):
    return kernel.TransitionStateDeclarationPin(
        state_anchor_id=state_anchor_id,
        declaration_record_id=declaration_record_id)


def transition_declaration(registration=None, *, from_registration=None,
                           to_registration=None, from_declaration=None,
                           to_declaration=None, context=AS_OPERATED,
                           evidence=None, supersedes=(), recorded_at=T0,
                           note="", **overrides):
    if any(item is None for item in (
            from_registration, to_registration,
            from_declaration, to_declaration)):
        _, default_from_registration, default_to_registration, \
            default_from_declaration, default_to_declaration = \
            state_world_records(context=context)
        from_registration = from_registration or default_from_registration
        to_registration = to_registration or default_to_registration
        from_declaration = from_declaration or default_from_declaration
        to_declaration = to_declaration or default_to_declaration
    registration = registration or transition_registration(
        from_registration=from_registration,
        to_registration=to_registration)
    fields = dict(
        transition_anchor_id=registration.anchor.anchor_id,
        context=context,
        from_endpoint=endpoint(
            from_registration.anchor.anchor_id, from_declaration.record_id),
        to_endpoint=endpoint(
            to_registration.anchor.anchor_id, to_declaration.record_id),
        evidence=(declaration_evidence(
            registration, from_registration, to_registration,
            from_declaration, to_declaration)
                  if evidence is None else evidence),
        supersedes=supersedes, recorded_at=recorded_at,
        authority=AUTHORITY, note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.TransitionDeclaration, **fields)


def transition_withdrawal(target, *, recorded_at=T1, note="", **overrides):
    fields = dict(withdraws=target.record_id, recorded_at=recorded_at,
                  authority=AUTHORITY, note=note)
    fields.update(overrides)
    return kernel.build_record(
        kernel.TransitionDeclarationWithdrawal, **fields)


def transition_fixture(*, context=AS_OPERATED, subject=ENT_A):
    records, from_registration, to_registration, from_declaration, \
        to_declaration = state_world_records(subject=subject, context=context)
    registration = transition_registration(
        subject=subject, from_registration=from_registration,
        to_registration=to_registration)
    return (records, registration, from_registration, to_registration,
            from_declaration, to_declaration)


def world(tmp_path, *extra, context=AS_OPERATED):
    store = kernel.ModelStore(tmp_path / "test-model")
    records, registration, from_registration, to_registration, \
        from_declaration, to_declaration = transition_fixture(context=context)
    for record in records:
        store.append(record)
    store.append(registration)
    for record in extra:
        store.append(record)
    return (store, registration, from_registration, to_registration,
            from_declaration, to_declaration)


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}
