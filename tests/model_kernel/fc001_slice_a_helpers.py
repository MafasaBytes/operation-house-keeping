"""Disposable FC-001 worlds; no authoritative model or evidence is changed."""

import backend.model_kernel as kernel
from tests.model_kernel.builders import (
    constraint_declaration, constraint_registration, constraint_signature,
)
from tests.model_kernel.test_flow_measurement_slice_a import (
    AUTHORITY, CLAIM, T0, association, foundation,
)


INDEX_NAMES = (
    "declarations", "withdrawals", "subject_by_id", "ids_by_subject",
    "parent_ids", "successor_ids", "root_by_id", "ancestry_by_id",
    "current_tips_by_root", "withdrawn_by", "effective_body_by_id",
    "ids_by_effective_body",
)


def world(*, orientation="aligned", context=None, participant="source"):
    records, support = foundation() if context is None else foundation(context)
    context = support[3].context
    participant_id = support[0].source_port_anchor_ids[0]
    if participant == "sink":
        participant_id = support[0].sink_port_anchor_ids[0]
        port = next(r for r in records if r.record_kind == "port_registration"
                    and r.anchor.anchor_id == participant_id)
        vpa = replace(support[4], port_anchor_id=participant_id)
        records = (*records, vpa)
        support = (*support[:2], port, support[3], vpa, support[5])
    witness = association(support, context=context, orientation=orientation,
                          participant_port_anchor_id=participant_id)
    crg = constraint_registration()
    signature = constraint_signature().model_dump()
    signature["observation_role"] = support[-1].declaration.observation_role
    vcn = constraint_declaration(expected_semantics=signature)
    return (*records, witness, crg, vcn), witness, crg, vcn


def declaration(witness, crg, vcn, **overrides):
    fields = dict(
        flow_measurement_association_record_id=witness.record_id,
        constraint_registration_record_id=crg.record_id,
        constraint_declaration_record_id=vcn.record_id,
        evidence=(CLAIM,), recorded_at=T0, authority=AUTHORITY,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.FlowOperatingCriterionDeclaration, **fields)


def withdrawal(target, **overrides):
    fields = dict(withdraws=target.record_id, recorded_at=T0, authority=AUTHORITY)
    fields.update(overrides)
    return kernel.build_record(kernel.FlowOperatingCriterionWithdrawal, **fields)


def replace(record, **updates):
    fields = record.model_dump()
    fields.pop("record_id")
    fields.update(updates)
    return kernel.build_record(type(record), **fields)


def membership(*records):
    return {record.record_id: record for record in records}
