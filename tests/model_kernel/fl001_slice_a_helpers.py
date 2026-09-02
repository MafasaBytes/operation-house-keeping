"""Deterministic synthetic FL-001 Slice A records; never a demo fixture."""

from datetime import UTC, datetime

import backend.model_kernel as kernel
import backend.system_identity as identity

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    registration as entity_registration,
)


T0 = datetime(2026, 9, 2, 12, 0, tzinfo=UTC)
T1 = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)
FLOW_A = "flo_" + "a" * 32
FLOW_B = "flo_" + "b" * 32
PORT_A = "prt_" + "1" * 32
PORT_B = "prt_" + "2" * 32
PORT_C = "prt_" + "3" * 32
PORT_D = "prt_" + "4" * 32
AS_DESIGNED = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
VIEW_INDEPENDENT = kernel.ViewIndependentContext(kind="view_independent")
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="fl001_test_fixture",
    method="manual_declaration")
FLOW_REGISTRATION_CLAIM = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement=("Synthetic authority explicitly registers this exact logical "
               "directed flow signature."))
FLOW_DECLARATION_CLAIM = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement=("Synthetic authority explicitly declares this exact logical "
               "flow capability and support-pin set."))


def citation(record_id):
    return kernel.ModelRecordEvidence(kind="model_record", record_id=record_id)


def flow_anchor(anchor_id=FLOW_A, name="Synthetic logical flow", role=None):
    return identity.FlowAnchor(
        anchor_id=anchor_id, namespace="test-model", display_name=name,
        role_name=role)


def flow_kind(*, system_id="project_local",
              system_edition="ohk-flow-kinds-1", code="synthetic_transfer"):
    return kernel.FlowKindToken(
        token_kind="flow_kind", system_id=system_id,
        system_edition=system_edition, code=code)


def port_registration(port_id, *, owner=ENT_A):
    return kernel.build_record(
        kernel.PortRegistration,
        anchor=identity.PortAnchor(
            anchor_id=port_id, namespace="test-model",
            display_name=f"Synthetic port {port_id[-1]}"),
        owner_entity_anchor_id=owner,
        evidence=(kernel.OwnerDeclarationEvidence(
            kind="owner_declaration",
            statement="Synthetic authority explicitly registers this port."),),
        recorded_at=T0,
        authority=AUTHORITY,
        note="",
    )


def direction_interface(port_id, value, *, context=AS_DESIGNED,
                        supersedes=(), recorded_at=T0, note=""):
    return kernel.build_record(
        kernel.PortInterfaceDeclaration,
        port_anchor_id=port_id,
        context=context,
        declaration=kernel.DirectionRoleDeclaration(
            dimension="direction_role", value=value),
        evidence=(kernel.OwnerDeclarationEvidence(
            kind="owner_declaration",
            statement="Synthetic authority declares this direction role."),),
        supersedes=supersedes,
        recorded_at=recorded_at,
        authority=AUTHORITY,
        note=note,
    )


def connection(endpoints=(PORT_A, PORT_B), *, context=AS_DESIGNED,
               supersedes=(), recorded_at=T0, note=""):
    return kernel.build_record(
        kernel.PortConnectionAssertion,
        endpoint_port_anchor_ids=endpoints,
        context=context,
        evidence=(kernel.OwnerDeclarationEvidence(
            kind="owner_declaration",
            statement="Synthetic authority declares common membership."),),
        supersedes=supersedes,
        recorded_at=recorded_at,
        authority=AUTHORITY,
        note=note,
    )


def port_world_records(*, source_ports=(PORT_A,), sink_ports=(PORT_B,),
                       context=AS_DESIGNED, cross_entity=False,
                       include_support=True):
    participants = tuple(sorted((*source_ports, *sink_ports)))
    entity_records = [entity_registration(ENT_A)]
    owners = {port: ENT_A for port in participants}
    if cross_entity:
        entity_records.append(entity_registration(ENT_B))
        owners[sink_ports[-1]] = ENT_B
    port_records = tuple(
        port_registration(port, owner=owners[port]) for port in participants)
    if not include_support:
        return tuple((*entity_records, *port_records)), port_records, None, (), ()
    pcn = connection(participants, context=context)
    source_pifs = tuple(direction_interface(
        port, "output", context=context) for port in source_ports)
    sink_pifs = tuple(direction_interface(
        port, "input", context=context) for port in sink_ports)
    return tuple((*entity_records, *port_records, pcn,
                  *source_pifs, *sink_pifs)), port_records, pcn, \
        source_pifs, sink_pifs


def registration_evidence(port_records, *, extra=()):
    return tuple((*(citation(record.record_id) for record in port_records),
                  FLOW_REGISTRATION_CLAIM, *extra))


def flow_registration(*, flow_anchor_id=FLOW_A,
                      source_ports=(PORT_A,), sink_ports=(PORT_B,),
                      port_records=None, kind=None, evidence=None,
                      recorded_at=T0, note="", **overrides):
    if port_records is None:
        _, port_records, _, _, _ = port_world_records(
            source_ports=source_ports, sink_ports=sink_ports,
            include_support=False)
    fields = dict(
        anchor=flow_anchor(flow_anchor_id),
        source_port_anchor_ids=source_ports,
        sink_port_anchor_ids=sink_ports,
        flow_kind=flow_kind() if kind is None else kind,
        evidence=(registration_evidence(port_records)
                  if evidence is None else evidence),
        recorded_at=recorded_at,
        authority=AUTHORITY,
        note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.FlowRegistration, **fields)


def direction_pin(port_id, declaration_record_id):
    return kernel.FlowDirectionDeclarationPin(
        port_anchor_id=port_id,
        declaration_record_id=declaration_record_id)


def declaration_evidence(registration, port_records, pcn,
                         source_pifs, sink_pifs, *, extra=()):
    return tuple((citation(registration.record_id),
                  *(citation(record.record_id) for record in port_records),
                  citation(pcn.record_id),
                  *(citation(record.record_id)
                    for record in (*source_pifs, *sink_pifs)),
                  FLOW_DECLARATION_CLAIM,
                  *extra))


def flow_declaration(registration, *, port_records, pcn, source_pifs,
                     sink_pifs, context=AS_DESIGNED, evidence=None,
                     supersedes=(), recorded_at=T0, note="", **overrides):
    fields = dict(
        flow_anchor_id=registration.anchor.anchor_id,
        context=context,
        connection_assertion_record_id=pcn.record_id,
        source_direction_pins=tuple(direction_pin(
            record.port_anchor_id, record.record_id) for record in source_pifs),
        sink_direction_pins=tuple(direction_pin(
            record.port_anchor_id, record.record_id) for record in sink_pifs),
        evidence=(declaration_evidence(
            registration, port_records, pcn, source_pifs, sink_pifs)
                  if evidence is None else evidence),
        supersedes=supersedes,
        recorded_at=recorded_at,
        authority=AUTHORITY,
        note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.FlowDeclaration, **fields)


def flow_withdrawal(target, *, recorded_at=T1, note="", **overrides):
    fields = dict(
        withdraws=target.record_id,
        recorded_at=recorded_at,
        authority=AUTHORITY,
        note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.FlowDeclarationWithdrawal, **fields)


def flow_fixture(*, source_ports=(PORT_A,), sink_ports=(PORT_B,),
                 context=AS_DESIGNED, cross_entity=False,
                 include_support=True):
    records, port_records, pcn, source_pifs, sink_pifs = port_world_records(
        source_ports=source_ports, sink_ports=sink_ports, context=context,
        cross_entity=cross_entity, include_support=include_support)
    registration = flow_registration(
        source_ports=source_ports, sink_ports=sink_ports,
        port_records=port_records)
    return records, registration, port_records, pcn, source_pifs, sink_pifs


def world(tmp_path, *claims, source_ports=(PORT_A,), sink_ports=(PORT_B,),
          context=AS_DESIGNED, cross_entity=False, include_support=True):
    records, registration, port_records, pcn, source_pifs, sink_pifs = \
        flow_fixture(
            source_ports=source_ports, sink_ports=sink_ports, context=context,
            cross_entity=cross_entity, include_support=include_support)
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, registration, *claims):
        store.append(record)
    return store, registration, port_records, pcn, source_pifs, sink_pifs


def complete_records(*claims, source_ports=(PORT_A,), sink_ports=(PORT_B,),
                     context=AS_DESIGNED, cross_entity=False,
                     include_support=True):
    records, registration, *_ = flow_fixture(
        source_ports=source_ports, sink_ports=sink_ports, context=context,
        cross_entity=cross_entity, include_support=include_support)
    values = (*records, registration, *claims)
    return {record.record_id: record for record in values}


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}
