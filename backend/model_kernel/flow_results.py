"""FL-001 read-only logical-flow declaration result contracts.

One complete :class:`ModelQueryMaterial` is carried by each outer result.
Nested rows contain strict indices and derived model facts only. Nothing in
this module assesses physical flow, observations, quantities, paths, causes,
control, safety, health, diagnosis, correctness, or recommended action.
"""

from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, StrictInt, field_validator,
    model_validator,
)

from backend.model_kernel.canonical import _flow_effective_body_bytes
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.port_results import (
    AssertionActivity, ContainingLineageHealth, ModelQueryMaterial,
    TopologyConclusion, _exact_connections_payload, _port_assertion_payload,
    _port_interface_payload,
)
from backend.model_kernel.result_revalidation import (
    inspect_supplied_graph as _inspect_supplied_graph,
    material_indices as _indices,
    rebuild_context as _rebuild_context,
    rebuild_material as _rebuild_material,
    rebuild_row as _rebuild_row,
    rebuild_rows as _rebuild_rows,
)
from backend.system_identity import FLOW_ANCHOR_ID_PATTERN, PORT_ANCHOR_ID_PATTERN


FlowLookupStatus = Literal["not_registered", "registered"]
FlowDeclarationConclusion = Literal[
    "not_registered", "not_declared", "declared", "conflicted", "inactive",
]
FlowDeclarationLineageSummary = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
FlowAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]
FlowPortRole = Literal["source", "sink"]
PortFlowsStatus = Literal["port_not_registered", "registered"]
FlowAssertionLookupStatus = Literal["not_found", "found"]

FlowConnectionAlignment = Literal[
    "exact_current", "pinned_connection_superseded",
    "pinned_connection_withdrawn", "connection_lineage_conflicted",
    "connection_lineage_inactive",
]
FlowDirectionAlignment = Literal[
    "exact_current", "pinned_direction_superseded",
    "pinned_direction_withdrawn", "direction_lineage_conflicted",
    "direction_lineage_inactive",
]
FlowCurrentDirectionRelation = Literal[
    "consistent", "inconsistent", "indeterminate", "not_evaluated",
]
FlowSupportAlignmentSummary = Literal[
    "aligned", "stale", "conflicted", "inactive",
]
InterfaceDimensionStatus = Literal[
    "port_not_registered", "not_declared", "declared", "conflicted",
    "inactive",
]

_FlowIndex = Annotated[StrictInt, Field(ge=0)]


class _FlowResult(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="wrap")
    @classmethod
    def _reject_hostile_supplied_graph(cls, value, handler):
        _inspect_supplied_graph(value)
        return handler(value)


def _connection_alignment(health, activity) -> str:
    if health == "conflicted":
        if activity in ("current", "superseded", "withdrawn"):
            return "connection_lineage_conflicted"
    elif health == "inactive":
        if activity in ("superseded", "withdrawn"):
            return "connection_lineage_inactive"
    elif health == "healthy":
        value = {
            "current": "exact_current",
            "superseded": "pinned_connection_superseded",
            "withdrawn": "pinned_connection_withdrawn",
        }.get(activity)
        if value is not None:
            return value
    raise ValueError("unreachable connection activity/lineage combination")


def _direction_alignment(health, activity) -> str:
    if health == "conflicted":
        if activity in ("current", "superseded", "withdrawn"):
            return "direction_lineage_conflicted"
    elif health == "inactive":
        if activity in ("superseded", "withdrawn"):
            return "direction_lineage_inactive"
    elif health == "healthy":
        value = {
            "current": "exact_current",
            "superseded": "pinned_direction_superseded",
            "withdrawn": "pinned_direction_withdrawn",
        }.get(activity)
        if value is not None:
            return value
    raise ValueError("unreachable direction activity/lineage combination")


def _current_direction_relation(loaded, material, row, role) -> str:
    if row["status"] != "declared":
        return "not_evaluated"
    declaration = loaded.records[
        material.revision.record_ids[row["declaration_index"]]]
    value = declaration.declaration.value
    if value == "non_directional":
        return "indeterminate"
    if role == "source":
        return "consistent" if value in {"output", "bidirectional"} \
            else "inconsistent"
    return "consistent" if value in {"input", "bidirectional"} \
        else "inconsistent"


def _connection_support_payload(material, loaded, declaration, indices) -> dict:
    record_id = declaration.connection_assertion_record_id
    assertion = _port_assertion_payload(
        material, loaded, record_id, record_indices=indices)
    if (assertion["status"] != "found"
            or assertion["activity"] is None
            or assertion["lineage_health"] is None):
        raise ValueError("admitted flow has invalid PCN support")
    participants = tuple(sorted((
        *(pin.port_anchor_id for pin in declaration.source_direction_pins),
        *(pin.port_anchor_id for pin in declaration.sink_direction_pins),
    )))
    topology = _exact_connections_payload(
        material, loaded, participants, declaration.context,
        record_indices=indices)
    return {
        "connection_assertion_index": indices[record_id],
        "exact_topology_conclusion": topology["conclusion"],
        "pinned_assertion_activity": assertion["activity"],
        "pinned_lineage_health": assertion["lineage_health"],
        "alignment": _connection_alignment(
            assertion["lineage_health"], assertion["activity"]),
    }


def _direction_support_payload(material, loaded, declaration, pin, role,
                               indices) -> dict:
    assertion = _port_assertion_payload(
        material, loaded, pin.declaration_record_id,
        record_indices=indices)
    if (assertion["status"] != "found"
            or assertion["activity"] is None
            or assertion["lineage_health"] is None):
        raise ValueError("admitted flow has invalid PIF support")
    interface = _port_interface_payload(
        material, loaded, pin.port_anchor_id, declaration.context,
        record_indices=indices)
    direction = interface["dimensions"][1]
    registration = loaded.port_registrations_by_anchor[pin.port_anchor_id]
    return {
        "role": role,
        "port_anchor_id": pin.port_anchor_id,
        "port_registration_index": indices[registration.record_id],
        "direction_declaration_index": indices[pin.declaration_record_id],
        "direction_dimension_status": direction["status"],
        "pinned_assertion_activity": assertion["activity"],
        "pinned_lineage_health": assertion["lineage_health"],
        "current_direction_relation": _current_direction_relation(
            loaded, material, direction, role),
        "alignment": _direction_alignment(
            assertion["lineage_health"], assertion["activity"]),
    }


def _support_summary(connection, sources, sinks) -> str:
    alignments = tuple(row["alignment"]
                       for row in (connection, *sources, *sinks))
    if any(value.endswith("_conflicted") for value in alignments):
        return "conflicted"
    if any(value.endswith("_inactive") for value in alignments):
        return "inactive"
    if any(value != "exact_current" for value in alignments):
        return "stale"
    return "aligned"


def _flow_lookup_payload(material: ModelQueryMaterial, loaded,
                         flow_anchor_id: str, *, record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.flow_registrations_by_anchor.get(flow_anchor_id)
    if registration is None:
        return {
            "flow_anchor_id": flow_anchor_id,
            "status": "not_registered",
            "registration_index": None,
            "source_port_registration_indices": (),
            "sink_port_registration_indices": (),
        }
    return {
        "flow_anchor_id": flow_anchor_id,
        "status": "registered",
        "registration_index": indices[registration.record_id],
        "source_port_registration_indices": tuple(
            indices[loaded.port_registrations_by_anchor[port].record_id]
            for port in registration.source_port_anchor_ids),
        "sink_port_registration_indices": tuple(
            indices[loaded.port_registrations_by_anchor[port].record_id]
            for port in registration.sink_port_anchor_ids),
    }


def _flow_declaration_payload(material: ModelQueryMaterial, loaded,
                              flow_anchor_id: str,
                              context: AssertionContext, *,
                              record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.flow_registrations_by_anchor.get(flow_anchor_id)
    base = {
        "flow_anchor_id": flow_anchor_id,
        "context": context.model_dump(mode="python"),
    }
    if registration is None:
        return {
            **base,
            "conclusion": "not_registered",
            "lineage_summary": "not_applicable",
            "agreement_findings": (),
            "registration_index": None,
            "roots": (),
            "effective_body_groups": (),
            "current_declaration_indices": (),
        }
    declaration_ids = loaded.flow_declaration_ids_by_key.get(
        (flow_anchor_id, context), ())
    root_ids = tuple(sorted({
        loaded.flow_declaration_root_by_id[record_id]
        for record_id in declaration_ids
    }))
    if not root_ids:
        return {
            **base,
            "conclusion": "not_declared",
            "lineage_summary": "not_applicable",
            "agreement_findings": (),
            "registration_index": indices[registration.record_id],
            "roots": (),
            "effective_body_groups": (),
            "current_declaration_indices": (),
        }

    lineage_ids_by_root = {root_id: [] for root_id in root_ids}
    for record_id in declaration_ids:
        root_id = loaded.flow_declaration_root_by_id[record_id]
        lineage_ids_by_root[root_id].append(record_id)

    root_work = []
    body_by_tip: dict[str, bytes] = {}
    root_by_tip: dict[str, str] = {}
    for root_id in root_ids:
        lineage_ids = tuple(sorted(lineage_ids_by_root[root_id]))
        tips = tuple(sorted(
            loaded.current_flow_declaration_tips_by_root[root_id],
            key=lambda record: record.record_id))
        tip_ids = tuple(record.record_id for record in tips)
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in loaded.flow_declaration_withdrawn_by[
                record_id]))
        health = (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else "healthy")
        for tip in tips:
            body_by_tip[tip.record_id] = _flow_effective_body_bytes(tip)
            root_by_tip[tip.record_id] = root_id
        root_work.append({
            "root_id": root_id,
            "lineage_ids": lineage_ids,
            "tip_ids": tip_ids,
            "withdrawal_ids": withdrawal_ids,
            "lineage_health": health,
        })

    tip_ids_by_body: dict[bytes, list[str]] = {}
    for tip_id in sorted(body_by_tip):
        tip_ids_by_body.setdefault(body_by_tip[tip_id], []).append(tip_id)
    ordered_bodies = tuple(sorted(tip_ids_by_body))
    body_to_group_index = {
        body: group_index for group_index, body in enumerate(ordered_bodies)
    }
    group_payloads = []
    current_declaration_indices = []
    for body in ordered_bodies:
        tip_ids = tuple(sorted(tip_ids_by_body[body]))
        current_declaration_indices.extend(indices[item] for item in tip_ids)
        representative_id = min(tip_ids)
        representative = loaded.flow_declarations[representative_id]
        root_record_ids = tuple(sorted({root_by_tip[item] for item in tip_ids}))
        connection = _connection_support_payload(
            material, loaded, representative, indices)
        sources = tuple(_direction_support_payload(
            material, loaded, representative, pin, "source", indices)
            for pin in representative.source_direction_pins)
        sinks = tuple(_direction_support_payload(
            material, loaded, representative, pin, "sink", indices)
            for pin in representative.sink_direction_pins)
        group_payloads.append({
            "group_index": body_to_group_index[body],
            "representative_declaration_index": indices[representative_id],
            "current_tip_indices": tuple(indices[item] for item in tip_ids),
            "root_record_indices": tuple(
                indices[item] for item in root_record_ids),
            "connection_support": connection,
            "source_direction_supports": sources,
            "sink_direction_supports": sinks,
            "support_alignment_summary": _support_summary(
                connection, sources, sinks),
        })

    root_payloads = []
    for row in root_work:
        group_indices = tuple(sorted({
            body_to_group_index[body_by_tip[tip_id]]
            for tip_id in row["tip_ids"]
        }))
        root_payloads.append({
            "root_record_index": indices[row["root_id"]],
            "lineage_record_indices": tuple(
                indices[item] for item in row["lineage_ids"]),
            "current_tip_indices": tuple(
                indices[item] for item in row["tip_ids"]),
            "withdrawal_indices": tuple(
                indices[item] for item in row["withdrawal_ids"]),
            "lineage_health": row["lineage_health"],
            "effective_body_group_indices": group_indices,
        })

    healthy = tuple(row for row in root_work
                    if row["lineage_health"] == "healthy")
    conflicted = tuple(row for row in root_work
                       if row["lineage_health"] == "conflicted")
    inactive = tuple(row for row in root_work
                     if row["lineage_health"] == "inactive")
    healthy_bodies = tuple(
        body_by_tip[row["tip_ids"][0]] for row in healthy)
    healthy_roots_by_body: dict[bytes, list[str]] = {}
    for row, body in zip(healthy, healthy_bodies):
        healthy_roots_by_body.setdefault(body, []).append(row["root_id"])
    findings = []
    if len(healthy) == 1:
        findings.append("one_healthy_root")
    if any(len(roots) >= 2 for roots in healthy_roots_by_body.values()):
        findings.append("corroborating_healthy_roots")
    if conflicted:
        findings.append("same_root_conflict")
    if len(set(healthy_bodies)) > 1:
        findings.append("cross_root_effective_body_disagreement")
    if inactive:
        findings.append("inactive_roots_present")

    if not body_by_tip:
        conclusion, summary = "inactive", "inactive"
    elif conflicted or len(set(healthy_bodies)) > 1:
        conclusion, summary = "conflicted", "conflicted"
    else:
        conclusion, summary = "declared", "healthy"
    return {
        **base,
        "conclusion": conclusion,
        "lineage_summary": summary,
        "agreement_findings": tuple(findings),
        "registration_index": indices[registration.record_id],
        "roots": tuple(root_payloads),
        "effective_body_groups": tuple(group_payloads),
        "current_declaration_indices": tuple(current_declaration_indices),
    }


def _port_flows_payload(material: ModelQueryMaterial, loaded,
                        port_anchor_id: str, context: AssertionContext) -> dict:
    indices = _indices(material)
    registration = loaded.port_registrations_by_anchor.get(port_anchor_id)
    base = {
        "port_anchor_id": port_anchor_id,
        "context": context.model_dump(mode="python"),
    }
    if registration is None:
        return {
            **base,
            "status": "port_not_registered",
            "port_registration_index": None,
            "entries": (),
        }
    pending = []
    for flow_anchor_id in loaded.flow_anchor_ids_by_port.get(port_anchor_id, ()):
        if not loaded.flow_declaration_ids_by_key.get(
                (flow_anchor_id, context), ()):
            continue
        flow_registration = loaded.flow_registrations_by_anchor[flow_anchor_id]
        declaration = _flow_declaration_payload(
            material, loaded, flow_anchor_id, context,
            record_indices=indices)
        role = loaded.flow_role_by_anchor_and_port[
            (flow_anchor_id, port_anchor_id)]
        pending.append((flow_anchor_id, flow_registration.record_id, {
            "flow_anchor_id": flow_anchor_id,
            "flow_registration_index": indices[flow_registration.record_id],
            "role": role,
            "conclusion": declaration["conclusion"],
            "lineage_summary": declaration["lineage_summary"],
            "agreement_findings": declaration["agreement_findings"],
            "roots": declaration["roots"],
            "effective_body_groups": declaration["effective_body_groups"],
            "current_declaration_indices": declaration[
                "current_declaration_indices"],
        }))
    entries = tuple({"entry_index": entry_index, **payload}
                    for entry_index, (_, _, payload) in enumerate(
                        sorted(pending, key=lambda item: (item[0], item[1]))))
    return {
        **base,
        "status": "registered",
        "port_registration_index": indices[registration.record_id],
        "entries": entries,
    }


def _flow_assertion_payload(material: ModelQueryMaterial, loaded,
                            record_id: str) -> dict:
    indices = _indices(material)
    record = loaded.records.get(record_id)
    found = record is not None and record.record_kind in {
        "flow_registration", "flow_declaration",
        "flow_declaration_withdrawal",
    }
    base = {
        "record_id": record_id,
        "lookup_status": "found" if found else "not_found",
    }
    empty = {
        "activity": None,
        "containing_lineage_health": None,
        "containing_flow_conclusion": None,
        "containing_agreement_findings": None,
        "root_record_index": None,
        "successor_indices": (),
        "withdrawal_indices": (),
    }
    if not found:
        return {**base, "record_index": None, **empty}
    if record.record_kind != "flow_declaration":
        return {**base, "record_index": indices[record_id], **empty}
    root_id = loaded.flow_declaration_root_by_id[record_id]
    tips = loaded.current_flow_declaration_tips_by_root[root_id]
    successors = loaded.flow_declaration_successor_ids[record_id]
    withdrawals = loaded.flow_declaration_withdrawn_by[record_id]
    declaration = _flow_declaration_payload(
        material, loaded, record.flow_anchor_id, record.context,
        record_indices=indices)
    return {
        **base,
        "record_index": indices[record_id],
        "activity": (
            "superseded" if successors else
            "withdrawn" if withdrawals else "current"),
        "containing_lineage_health": (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else "healthy"),
        "containing_flow_conclusion": declaration["conclusion"],
        "containing_agreement_findings": declaration["agreement_findings"],
        "root_record_index": indices[root_id],
        "successor_indices": tuple(
            indices[item] for item in sorted(successors)),
        "withdrawal_indices": tuple(
            indices[item] for item in sorted(withdrawals)),
    }


class FlowConnectionSupportResult(_FlowResult):
    _material: ModelQueryMaterial = PrivateAttr()
    connection_assertion_index: _FlowIndex
    exact_topology_conclusion: TopologyConclusion
    pinned_assertion_activity: AssertionActivity
    pinned_lineage_health: ContainingLineageHealth
    alignment: FlowConnectionAlignment

    @property
    def connection_assertion(self):
        return self._material.record_at(self.connection_assertion_index)


class FlowDirectionSupportResult(_FlowResult):
    _material: ModelQueryMaterial = PrivateAttr()
    role: FlowPortRole
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    port_registration_index: _FlowIndex
    direction_declaration_index: _FlowIndex
    direction_dimension_status: InterfaceDimensionStatus
    pinned_assertion_activity: AssertionActivity
    pinned_lineage_health: ContainingLineageHealth
    current_direction_relation: FlowCurrentDirectionRelation
    alignment: FlowDirectionAlignment

    @property
    def port_registration(self):
        return self._material.record_at(self.port_registration_index)

    @property
    def direction_declaration(self):
        return self._material.record_at(self.direction_declaration_index)


class FlowEffectiveBodyGroupResult(_FlowResult):
    _material: ModelQueryMaterial = PrivateAttr()
    group_index: _FlowIndex
    representative_declaration_index: _FlowIndex
    current_tip_indices: tuple[_FlowIndex, ...]
    root_record_indices: tuple[_FlowIndex, ...]
    connection_support: FlowConnectionSupportResult
    source_direction_supports: tuple[FlowDirectionSupportResult, ...]
    sink_direction_supports: tuple[FlowDirectionSupportResult, ...]
    support_alignment_summary: FlowSupportAlignmentSummary

    _connection_before = field_validator("connection_support", mode="before")(
        lambda value: _rebuild_row(value, FlowConnectionSupportResult))

    @field_validator("source_direction_supports", mode="before")
    @classmethod
    def _sources_before(cls, value):
        return _rebuild_rows(
            value, FlowDirectionSupportResult, "source direction supports")

    @field_validator("sink_direction_supports", mode="before")
    @classmethod
    def _sinks_before(cls, value):
        return _rebuild_rows(
            value, FlowDirectionSupportResult, "sink direction supports")

    @property
    def representative_declaration(self):
        return self._material.record_at(self.representative_declaration_index)

    @property
    def current_tips(self):
        return tuple(self._material.record_at(index)
                     for index in self.current_tip_indices)

    @property
    def root_records(self):
        return tuple(self._material.record_at(index)
                     for index in self.root_record_indices)


class FlowDeclarationRootResult(_FlowResult):
    _material: ModelQueryMaterial = PrivateAttr()
    root_record_index: _FlowIndex
    lineage_record_indices: tuple[_FlowIndex, ...]
    current_tip_indices: tuple[_FlowIndex, ...]
    withdrawal_indices: tuple[_FlowIndex, ...]
    lineage_health: ContainingLineageHealth
    effective_body_group_indices: tuple[_FlowIndex, ...]

    @property
    def root_record(self):
        return self._material.record_at(self.root_record_index)

    @property
    def lineage_records(self):
        return tuple(self._material.record_at(index)
                     for index in self.lineage_record_indices)

    @property
    def current_tips(self):
        return tuple(self._material.record_at(index)
                     for index in self.current_tip_indices)

    @property
    def withdrawals(self):
        return tuple(self._material.record_at(index)
                     for index in self.withdrawal_indices)


def _bind_declaration_rows(roots, groups, material: ModelQueryMaterial) -> None:
    for root in roots:
        root._material = material
    for group in groups:
        group._material = material
        group.connection_support._material = material
        for row in (*group.source_direction_supports,
                    *group.sink_direction_supports):
            row._material = material


class FlowLookupResult(_FlowResult):
    material: ModelQueryMaterial
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    status: FlowLookupStatus
    registration_index: _FlowIndex | None = None
    source_port_registration_indices: tuple[_FlowIndex, ...] = ()
    sink_port_registration_indices: tuple[_FlowIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _flow_lookup_payload(
            self.material, self.material.loaded(), self.flow_anchor_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("flow lookup disclosure is forged")
        return self

    @property
    def registration(self):
        return (None if self.registration_index is None else
                self.material.record_at(self.registration_index))

    @property
    def source_port_registrations(self):
        return tuple(self.material.record_at(index)
                     for index in self.source_port_registration_indices)

    @property
    def sink_port_registrations(self):
        return tuple(self.material.record_at(index)
                     for index in self.sink_port_registration_indices)


class FlowDeclarationResult(_FlowResult):
    material: ModelQueryMaterial
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    context: AssertionContext
    conclusion: FlowDeclarationConclusion
    lineage_summary: FlowDeclarationLineageSummary
    agreement_findings: tuple[FlowAgreementFinding, ...] = ()
    registration_index: _FlowIndex | None = None
    roots: tuple[FlowDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[FlowEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_FlowIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, FlowDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, FlowEffectiveBodyGroupResult, "effective body groups")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _flow_declaration_payload(
            self.material, self.material.loaded(), self.flow_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("flow declaration disclosure is forged")
        _bind_declaration_rows(
            self.roots, self.effective_body_groups, self.material)
        return self


class PortFlowEntry(_FlowResult):
    _material: ModelQueryMaterial = PrivateAttr()
    entry_index: _FlowIndex
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    flow_registration_index: _FlowIndex
    role: FlowPortRole
    conclusion: FlowDeclarationConclusion
    lineage_summary: FlowDeclarationLineageSummary
    agreement_findings: tuple[FlowAgreementFinding, ...] = ()
    roots: tuple[FlowDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[FlowEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_FlowIndex, ...] = ()

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, FlowDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, FlowEffectiveBodyGroupResult, "effective body groups")

    @property
    def flow_registration(self):
        return self._material.record_at(self.flow_registration_index)


class PortFlowsResult(_FlowResult):
    material: ModelQueryMaterial
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: PortFlowsStatus
    port_registration_index: _FlowIndex | None = None
    entries: tuple[PortFlowEntry, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("entries", mode="before")
    @classmethod
    def _entries_before(cls, value):
        return _rebuild_rows(value, PortFlowEntry, "entries")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _port_flows_payload(
            self.material, self.material.loaded(), self.port_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("port flows disclosure is forged")
        for entry in self.entries:
            entry._material = self.material
            _bind_declaration_rows(
                entry.roots, entry.effective_body_groups, self.material)
        return self

    @property
    def port_registration(self):
        return (None if self.port_registration_index is None else
                self.material.record_at(self.port_registration_index))


class FlowAssertionDisclosureResult(_FlowResult):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:frg|fld|flw)_[0-9a-f]{64}$")
    lookup_status: FlowAssertionLookupStatus
    record_index: _FlowIndex | None = None
    activity: AssertionActivity | None = None
    containing_lineage_health: ContainingLineageHealth | None = None
    containing_flow_conclusion: FlowDeclarationConclusion | None = None
    containing_agreement_findings: tuple[FlowAgreementFinding, ...] | None = None
    root_record_index: _FlowIndex | None = None
    successor_indices: tuple[_FlowIndex, ...] = ()
    withdrawal_indices: tuple[_FlowIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _flow_assertion_payload(
            self.material, self.material.loaded(), self.record_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("flow assertion disclosure is forged")
        return self

    @property
    def record(self):
        return (None if self.record_index is None else
                self.material.record_at(self.record_index))

    @property
    def root_record(self):
        return (None if self.root_record_index is None else
                self.material.record_at(self.root_record_index))

    @property
    def successors(self):
        return tuple(self.material.record_at(index)
                     for index in self.successor_indices)

    @property
    def withdrawals(self):
        return tuple(self.material.record_at(index)
                     for index in self.withdrawal_indices)
