"""PT-001 and VP-001 read-only query result contracts.

All authority is carried once in ``ModelQueryMaterial``.  Result rows contain
only indices into that immutable, fully revalidated collection.
"""

import re
from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, StrictInt, TypeAdapter,
    ValidationError,
    model_validator,
)

from backend.model_kernel.contracts import (
    AssertionContext, ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN, ModelIntegrityError,
    ModelQueryError, ModelRecord, ModelRevision,
)

_CONTEXT_ADAPTER = TypeAdapter(AssertionContext)

PortLookupStatus = Literal["not_registered", "registered"]
EntityPortsStatus = Literal["owner_not_registered", "registered"]
TopologyAdmissionStatus = Literal["endpoint_not_registered", "admitted"]
TopologyConclusion = Literal["unknown", "asserted", "inactive"]
PortConnectionsStatus = Literal["port_not_registered", "registered"]
PortAssertionLookupStatus = Literal["not_found", "found"]
AssertionActivity = Literal["current", "superseded", "withdrawn"]
ContainingLineageHealth = Literal["healthy", "conflicted", "inactive"]
CompatibilityEndpointStatus = Literal[
    "both_registered", "left_not_registered", "right_not_registered",
    "both_not_registered",
]
ExplicitCompatibilityStatus = Literal[
    "not_declared", "declared_compatible", "declared_incompatible",
    "conflicted", "inactive", "stale",
]
CrossFindingConsistency = Literal[
    "consistent", "inconsistent", "indeterminate",
]
VariablePortEndpointStatus = Literal[
    "both_registered", "variable_not_registered", "port_not_registered",
    "both_not_registered",
]
VariablePortOwnerAlignment = Literal[
    "not_evaluated", "same_owner", "different_owners",
]
VariablePortAssociationConclusion = Literal[
    "not_evaluated", "not_declared", "asserted", "inactive",
]
VariablePortLineageSummary = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
VariablePortsStatus = Literal["variable_not_registered", "registered"]
PortVariablesStatus = Literal["port_not_registered", "registered"]
VariablePortAssertionLookupStatus = Literal["not_found", "found"]

_VariablePortIndex = Annotated[StrictInt, Field(ge=0)]


def _validated_context(value) -> AssertionContext:
    try:
        payload = value.model_dump(mode="python") if hasattr(
            value, "model_dump") else value
        return _CONTEXT_ADAPTER.validate_python(payload)
    except (ValidationError, ValueError, TypeError, AttributeError) as error:
        raise ValueError("carried assertion context is invalid") from error


class _Result(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


class ModelQueryMaterial(_Result):
    revision: ModelRevision
    records: tuple[ModelRecord, ...]

    @model_validator(mode="after")
    def _authoritative(self):
        # Reconstruct every nested object from serialized content; never trust
        # an already-created pydantic instance at this public boundary.
        from backend.model_kernel.store import validate_record_collection
        revision = ModelRevision.model_validate(self.revision.model_dump())
        rebuilt = tuple(type(record).model_validate(record.model_dump())
                        for record in self.records)
        ids = tuple(record.record_id for record in rebuilt)
        if ids != tuple(sorted(set(ids))):
            raise ValueError("material records must be unique and ordered")
        if ids != revision.record_ids:
            raise ValueError("material records must exactly equal revision membership")
        try:
            loaded = validate_record_collection(
                revision.model_id,
                {record.record_id: record for record in rebuilt})
        except ModelIntegrityError as error:
            raise ValueError(
                "material records are not a valid selected revision") from error
        if loaded.revision != revision:
            raise ValueError("material revision is not the selected membership")
        return self

    def record_at(self, index: int):
        if (not isinstance(index, int) or isinstance(index, bool)
                or not 0 <= index < len(self.records)):
            raise ModelQueryError(
                "MODEL_RECORD_INDEX_INVALID",
                "record index must identify one carried model record")
        return self.records[index]

    def loaded(self):
        from backend.model_kernel.store import validate_record_collection
        validated = ModelQueryMaterial.model_validate(self.model_dump())
        return validate_record_collection(
            validated.revision.model_id,
            {record.record_id: record for record in validated.records})


def _material_indices(material: ModelQueryMaterial) -> dict[str, int]:
    return {record_id: index for index, record_id
            in enumerate(material.revision.record_ids)}


def _port_interface_payload(material: ModelQueryMaterial, loaded,
                            port_anchor_id: str, context: AssertionContext,
                            *, record_indices=None) -> dict:
    """One authoritative PT interface payload derivation."""
    indices = (_material_indices(material) if record_indices is None
               else record_indices)
    registered = port_anchor_id in loaded.port_registrations_by_anchor
    rows = []
    for dimension in ("interface_domain", "direction_role", "interface_type"):
        key = (port_anchor_id, context, dimension)
        ids = (loaded.port_interface_ids_by_key.get(key, ())
               if registered else ())
        tips = (loaded.current_port_interface_tips_by_key.get(key, ())
                if ids else ())
        withdrawals = tuple(sorted(
            withdrawal_id for record_id in ids
            for withdrawal_id in loaded.port_interface_withdrawn_by[record_id]))
        status = (
            "port_not_registered" if not registered else
            "not_declared" if not ids else
            "declared" if len(tips) == 1 else
            "conflicted" if tips else "inactive")
        rows.append({
            "dimension": dimension,
            "status": status,
            "lineage_health": (
                "healthy" if status == "declared" else
                "conflicted" if status == "conflicted" else
                "inactive" if status == "inactive" else
                "not_applicable"),
            "lineage_record_indices": tuple(indices[item] for item in ids),
            "current_tip_indices": tuple(
                indices[record.record_id] for record in tips),
            "withdrawal_indices": tuple(
                indices[item] for item in withdrawals),
            "declaration_index": (
                indices[tips[0].record_id] if status == "declared" else None),
            "conflicting_declaration_indices": (
                tuple(indices[record.record_id] for record in tips)
                if status == "conflicted" else ()),
            "superseded_declaration_indices": (
                tuple(indices[item] for item in ids
                      if loaded.port_interface_superseded_by[item])
                if registered else ()),
            "inactive_declaration_indices": tuple(
                indices[item] for item in ids
                if loaded.port_interface_withdrawn_by[item]),
        })
    return {
        "port_anchor_id": port_anchor_id,
        "status": "registered" if registered else "not_registered",
        "context": context.model_dump(mode="python"),
        "dimensions": tuple(rows),
    }


def _port_assertion_payload(material: ModelQueryMaterial, loaded,
                            record_id: str, *, record_indices=None) -> dict:
    """One authoritative PT assertion lifecycle payload derivation."""
    indices = (_material_indices(material) if record_indices is None
               else record_indices)
    record = loaded.records.get(record_id)
    pt_kinds = {
        "port_registration", "port_interface_declaration",
        "port_connection_assertion", "port_compatibility_declaration",
        "port_claim_withdrawal",
    }
    found = record is not None and record.record_kind in pt_kinds
    base = {"record_id": record_id,
            "status": "found" if found else "not_found"}
    empty = {
        "record_index": None,
        "activity": None,
        "lineage_health": None,
        "root_record_index": None,
        "successor_indices": (),
        "withdrawal_indices": (),
    }
    if not found:
        return {**base, **empty}
    if record.record_kind in {"port_registration", "port_claim_withdrawal"}:
        return {**base, **empty, "record_index": indices[record_id]}
    if record.record_kind == "port_interface_declaration":
        roots = loaded.port_interface_root_by_id
        successors = loaded.port_interface_superseded_by
        withdrawn = loaded.port_interface_withdrawn_by
    elif record.record_kind == "port_connection_assertion":
        roots = loaded.port_connection_root_by_id
        successors = loaded.port_connection_superseded_by
        withdrawn = loaded.port_connection_withdrawn_by
    else:
        roots = loaded.port_compatibility_root_by_id
        successors = loaded.port_compatibility_superseded_by
        withdrawn = loaded.port_compatibility_withdrawn_by
    root = roots[record_id]
    lineage_ids = tuple(item for item, candidate_root in roots.items()
                        if candidate_root == root)
    tips = tuple(item for item in lineage_ids
                 if not successors[item] and not withdrawn[item])
    return {
        **base,
        "record_index": indices[record_id],
        "activity": (
            "superseded" if successors[record_id] else
            "withdrawn" if withdrawn[record_id] else "current"),
        "lineage_health": (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else "healthy"),
        "root_record_index": indices[root],
        "successor_indices": tuple(indices[item]
                                   for item in successors[record_id]),
        "withdrawal_indices": tuple(indices[item]
                                    for item in withdrawn[record_id]),
    }


def _connection_parts_payload(material: ModelQueryMaterial, loaded,
                              selected_record_ids, requested,
                              *, record_indices=None) -> dict:
    """One authoritative PT connection-root and conclusion derivation."""
    indices = (_material_indices(material) if record_indices is None
               else record_indices)
    root_ids = tuple(sorted({
        loaded.port_connection_root_by_id[item]
        for item in selected_record_ids
    }))
    roots = []
    for position, root_id in enumerate(root_ids):
        lineage = tuple(sorted(
            item for item, candidate_root
            in loaded.port_connection_root_by_id.items()
            if candidate_root == root_id))
        tips = loaded.current_port_connection_tips_by_root[root_id]
        withdrawals = tuple(sorted(
            withdrawal_id for item in lineage
            for withdrawal_id in loaded.port_connection_withdrawn_by[item]))
        roots.append({
            "root_index": position,
            "root_record_index": indices[root_id],
            "lineage_record_indices": tuple(indices[item] for item in lineage),
            "current_tip_indices": tuple(
                indices[record.record_id] for record in tips),
            "withdrawal_indices": tuple(
                indices[item] for item in withdrawals),
            "lineage_health": (
                "inactive" if not tips else
                "conflicted" if len(tips) > 1 else "healthy"),
            "exact_endpoint_set": (
                loaded.port_connections[root_id].endpoint_port_anchor_ids
                == requested),
        })
    conclusion = (
        "unknown" if not roots else
        "asserted" if any(row["current_tip_indices"] for row in roots)
        else "inactive")
    roots_by_subject = {}
    for root_position, root_id in enumerate(root_ids):
        subject = loaded.port_connections[root_id].endpoint_port_anchor_ids
        roots_by_subject.setdefault(subject, []).append(root_position)
    subjects = tuple({
        "subject_index": position,
        "endpoint_port_anchor_ids": subject,
        "conclusion": (
            "asserted" if any(roots[root_index]["current_tip_indices"]
                              for root_index in root_indices)
            else "inactive"),
        "root_indices": tuple(root_indices),
    } for position, (subject, root_indices) in enumerate(
        sorted(roots_by_subject.items())))
    return {"conclusion": conclusion, "roots": tuple(roots),
            "subjects": subjects}


def _exact_connections_payload(material: ModelQueryMaterial, loaded,
                               endpoint_port_anchor_ids,
                               context: AssertionContext,
                               *, record_indices=None) -> dict:
    selected = loaded.port_connection_ids_by_subject.get(
        (endpoint_port_anchor_ids, context), ())
    parts = _connection_parts_payload(
        material, loaded, selected, endpoint_port_anchor_ids,
        record_indices=record_indices)
    missing = tuple(
        port_id for port_id in endpoint_port_anchor_ids
        if port_id not in loaded.port_registrations_by_anchor)
    return {
        "context": context.model_dump(mode="python"),
        **parts,
        "admission_status": (
            "endpoint_not_registered" if missing else "admitted"),
        "requested_port_anchor_ids": endpoint_port_anchor_ids,
        "unregistered_port_anchor_ids": missing,
    }


class _WithMaterial(_Result):
    material: ModelQueryMaterial

    @property
    def revision(self):
        return self.material.revision


def _validate_endpoint_subject(values: tuple[str, ...]) -> None:
    if not 2 <= len(values) <= 64:
        raise ValueError("endpoint subject requires two through 64 ports")
    if tuple(values) != tuple(sorted(set(values))):
        raise ValueError("endpoint subject must be unique and canonical")
    if any(not isinstance(value, str)
           or not re.fullmatch(PORT_ANCHOR_ID_PATTERN, value)
           for value in values):
        raise ValueError("endpoint subject contains an invalid port id")


class PortLookupResult(_WithMaterial):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    status: PortLookupStatus
    registration_index: int | None = Field(default=None, ge=0)
    owner_registration_index: int | None = Field(default=None, ge=0)

    @property
    def registration(self):
        return (None if self.registration_index is None
                else self.material.record_at(self.registration_index))

    @property
    def owner_registration(self):
        return (None if self.owner_registration_index is None
                else self.material.record_at(self.owner_registration_index))

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        registration = loaded.port_registrations_by_anchor.get(self.port_anchor_id)
        expected = (None if registration is None else
                    self.material.revision.record_ids.index(registration.record_id))
        owner = (None if registration is None else
                 self.material.revision.record_ids.index(
                     loaded.registrations_by_anchor[
                         registration.owner_entity_anchor_id].record_id))
        if (self.registration_index != expected
                or self.owner_registration_index != owner
                or self.status != (
                    "registered" if registration else "not_registered")):
            raise ValueError("port result does not follow authoritative material")
        return self


class EntityPortsResult(_WithMaterial):
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    status: EntityPortsStatus
    entity_registration_index: int | None = Field(default=None, ge=0)
    port_registration_indices: tuple[int, ...] = ()

    @property
    def ports(self):
        return tuple(self.material.record_at(i)
                     for i in self.port_registration_indices)

    @property
    def entity_registration(self):
        return (None if self.entity_registration_index is None
                else self.material.record_at(self.entity_registration_index))

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        registered = self.entity_anchor_id in loaded.registrations_by_anchor
        expected = tuple(self.material.revision.record_ids.index(
            loaded.port_registrations_by_anchor[a].record_id)
            for a in loaded.port_anchor_ids_by_owner.get(self.entity_anchor_id, ()))
        entity_index = (self.material.revision.record_ids.index(
            loaded.registrations_by_anchor[self.entity_anchor_id].record_id)
            if registered else None)
        if self.status != ("registered" if registered else
                           "owner_not_registered"):
            raise ValueError("entity ownership status is forged")
        if self.entity_registration_index != entity_index:
            raise ValueError("entity registration index is forged")
        if self.port_registration_indices != (expected if registered else ()):
            raise ValueError("entity port registrations are forged")
        return self


class InterfaceDimensionResult(_Result):
    _material: ModelQueryMaterial = PrivateAttr()
    dimension: Literal["interface_domain", "direction_role", "interface_type"]
    status: Literal["port_not_registered", "not_declared", "declared",
                    "conflicted", "inactive"]
    lineage_health: Literal[
        "not_applicable", "healthy", "conflicted", "inactive"]
    lineage_record_indices: tuple[int, ...] = ()
    current_tip_indices: tuple[int, ...] = ()
    withdrawal_indices: tuple[int, ...] = ()
    declaration_index: int | None = Field(default=None, ge=0)
    conflicting_declaration_indices: tuple[int, ...] = ()
    superseded_declaration_indices: tuple[int, ...] = ()
    inactive_declaration_indices: tuple[int, ...] = ()

    @property
    def declaration(self):
        return (self._material.record_at(self.current_tip_indices[0])
                if self.status == "declared" else None)

    @property
    def conflicting_declarations(self):
        return (tuple(self._material.record_at(i) for i in self.current_tip_indices)
                if self.status == "conflicted" else ())

    @property
    def superseded_declaration_ids(self):
        return tuple(self._material.record_at(i).record_id
                     for i in self.superseded_declaration_indices)

    @property
    def inactive_declaration_ids(self):
        return tuple(self._material.record_at(i).record_id
                     for i in self.inactive_declaration_indices)

    @property
    def withdrawal_ids(self):
        return tuple(self._material.record_at(i).record_id
                     for i in self.withdrawal_indices)


class PortInterfaceResult(_WithMaterial):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    status: Literal["registered", "not_registered"]
    context: AssertionContext
    dimensions: tuple[InterfaceDimensionResult, InterfaceDimensionResult,
                      InterfaceDimensionResult]

    @model_validator(mode="after")
    def _bind(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        expected = _port_interface_payload(
            self.material, loaded, self.port_anchor_id, context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("interface dimension disclosure is forged")
        for row in self.dimensions:
            object.__setattr__(row, "_material", self.material)
        return self


class EndpointInterfaceResult(_Result):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    status: Literal["registered", "not_registered"]
    port_registration_index: int | None = Field(default=None, ge=0)
    owner_registration_index: int | None = Field(default=None, ge=0)
    dimensions: tuple[InterfaceDimensionResult, InterfaceDimensionResult,
                      InterfaceDimensionResult]


class PortAssertionDisclosureResult(_WithMaterial):
    record_id: str = Field(
        pattern=r"^(prg|pif|pcn|pcm|ptw)_[0-9a-f]{64}$")
    status: PortAssertionLookupStatus
    record_index: int | None = Field(default=None, ge=0)
    activity: AssertionActivity | None = None
    lineage_health: ContainingLineageHealth | None = None
    root_record_index: int | None = Field(default=None, ge=0)
    successor_indices: tuple[int, ...] = ()
    withdrawal_indices: tuple[int, ...] = ()

    @property
    def record(self):
        return None if self.record_index is None else self.material.record_at(self.record_index)

    @property
    def successor_ids(self):
        return tuple(self.material.record_at(i).record_id for i in self.successor_indices)

    @property
    def withdrawal_ids(self):
        return tuple(self.material.record_at(i).record_id for i in self.withdrawal_indices)

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        expected = _port_assertion_payload(
            self.material, loaded, self.record_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("assertion lifecycle disclosure is forged")
        return self


class VariablePortAssociationRootResult(_Result):
    """One correction root, carrying indices into the outer material only."""

    _material: ModelQueryMaterial = PrivateAttr()
    root_record_index: _VariablePortIndex
    lineage_record_indices: tuple[_VariablePortIndex, ...]
    current_tip_indices: tuple[_VariablePortIndex, ...]
    withdrawal_indices: tuple[_VariablePortIndex, ...]
    lineage_health: ContainingLineageHealth

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


def _variable_port_root_payloads(material: ModelQueryMaterial, loaded,
                                 root_ids) -> tuple[dict, ...]:
    """Recompute complete VP lineage rows from one selected membership."""
    indices = {record_id: index for index, record_id
               in enumerate(material.revision.record_ids)}
    payloads = []
    for root_id in sorted(set(root_ids)):
        lineage_ids = tuple(sorted(
            record_id for record_id, candidate_root
            in loaded.variable_port_association_root_by_id.items()
            if candidate_root == root_id))
        tips = tuple(sorted(
            loaded.current_variable_port_association_tips_by_root[root_id],
            key=lambda record: record.record_id))
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in
            loaded.variable_port_association_withdrawn_by[record_id]))
        payloads.append({
            "root_record_index": indices[root_id],
            "lineage_record_indices": tuple(indices[record_id]
                                             for record_id in lineage_ids),
            "current_tip_indices": tuple(indices[record.record_id]
                                         for record in tips),
            "withdrawal_indices": tuple(indices[record_id]
                                        for record_id in withdrawal_ids),
            "lineage_health": (
                "inactive" if not tips else
                "conflicted" if len(tips) > 1 else
                "healthy"),
        })
    return tuple(payloads)


def _variable_port_conclusion(root_payloads: tuple[dict, ...]):
    if not root_payloads:
        return "not_declared", "not_applicable"
    active = tuple(row for row in root_payloads
                   if row["current_tip_indices"])
    if not active:
        return "inactive", "inactive"
    return (
        "asserted",
        "conflicted" if any(row["lineage_health"] == "conflicted"
                            for row in active) else "healthy",
    )


def _bind_variable_port_roots(rows, material: ModelQueryMaterial) -> None:
    for row in rows:
        object.__setattr__(row, "_material", material)


class VariablePortAssociationResult(_WithMaterial):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    endpoint_status: VariablePortEndpointStatus
    owner_alignment: VariablePortOwnerAlignment
    variable_registration_index: _VariablePortIndex | None = None
    variable_owner_registration_index: _VariablePortIndex | None = None
    port_registration_index: _VariablePortIndex | None = None
    port_owner_registration_index: _VariablePortIndex | None = None
    conclusion: VariablePortAssociationConclusion
    lineage_summary: VariablePortLineageSummary
    roots: tuple[VariablePortAssociationRootResult, ...] = ()

    @property
    def variable_registration(self):
        return (None if self.variable_registration_index is None else
                self.material.record_at(self.variable_registration_index))

    @property
    def variable_owner_registration(self):
        return (None if self.variable_owner_registration_index is None else
                self.material.record_at(
                    self.variable_owner_registration_index))

    @property
    def port_registration(self):
        return (None if self.port_registration_index is None else
                self.material.record_at(self.port_registration_index))

    @property
    def port_owner_registration(self):
        return (None if self.port_owner_registration_index is None else
                self.material.record_at(self.port_owner_registration_index))

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        indices = {record_id: index for index, record_id
                   in enumerate(self.material.revision.record_ids)}
        variable = loaded.variable_registrations_by_anchor.get(
            self.variable_anchor_id)
        port = loaded.port_registrations_by_anchor.get(self.port_anchor_id)
        expected_endpoint = (
            "both_registered" if variable is not None and port is not None else
            "variable_not_registered" if variable is None and port is not None else
            "port_not_registered" if variable is not None and port is None else
            "both_not_registered")
        variable_owner_id = (None if variable is None else
                             variable.anchor.entity_anchor_id)
        port_owner_id = (None if port is None else
                         port.owner_entity_anchor_id)
        variable_index = (None if variable is None else
                          indices[variable.record_id])
        variable_owner_index = (None if variable_owner_id is None else
            indices[loaded.registrations_by_anchor[variable_owner_id].record_id])
        port_index = None if port is None else indices[port.record_id]
        port_owner_index = (None if port_owner_id is None else
            indices[loaded.registrations_by_anchor[port_owner_id].record_id])
        if variable is None or port is None:
            alignment = "not_evaluated"
            conclusion, summary = "not_evaluated", "not_applicable"
            payloads = ()
        elif variable_owner_id != port_owner_id:
            alignment = "different_owners"
            conclusion, summary = "not_evaluated", "not_applicable"
            payloads = ()
        else:
            alignment = "same_owner"
            association_ids = loaded.variable_port_association_ids_by_subject.get(
                (self.variable_anchor_id, self.port_anchor_id, context), ())
            root_ids = tuple(
                loaded.variable_port_association_root_by_id[record_id]
                for record_id in association_ids)
            payloads = _variable_port_root_payloads(
                self.material, loaded, root_ids)
            conclusion, summary = _variable_port_conclusion(payloads)
        expected = (
            expected_endpoint, alignment, variable_index, variable_owner_index,
            port_index, port_owner_index, conclusion, summary,
            tuple(payloads),
        )
        supplied = (
            self.endpoint_status, self.owner_alignment,
            self.variable_registration_index,
            self.variable_owner_registration_index,
            self.port_registration_index, self.port_owner_registration_index,
            self.conclusion, self.lineage_summary,
            tuple(row.model_dump() for row in self.roots),
        )
        if supplied != expected:
            raise ValueError(
                "variable-port association disclosure is forged")
        _bind_variable_port_roots(self.roots, self.material)
        return self


class VariablePortAssociationEntry(_Result):
    _material: ModelQueryMaterial = PrivateAttr()
    entry_index: _VariablePortIndex
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    variable_registration_index: _VariablePortIndex
    variable_owner_registration_index: _VariablePortIndex
    port_registration_index: _VariablePortIndex
    port_owner_registration_index: _VariablePortIndex
    conclusion: VariablePortAssociationConclusion
    lineage_summary: VariablePortLineageSummary
    roots: tuple[VariablePortAssociationRootResult, ...]

    @property
    def variable_registration(self):
        return self._material.record_at(self.variable_registration_index)

    @property
    def variable_owner_registration(self):
        return self._material.record_at(
            self.variable_owner_registration_index)

    @property
    def port_registration(self):
        return self._material.record_at(self.port_registration_index)

    @property
    def port_owner_registration(self):
        return self._material.record_at(self.port_owner_registration_index)


def _variable_port_entry_payloads(material: ModelQueryMaterial, loaded,
                                  association_ids, *, order_by: str):
    """Return canonical collection entries for association subjects."""
    indices = {record_id: index for index, record_id
               in enumerate(material.revision.record_ids)}
    subjects = {}
    for record_id in association_ids:
        record = loaded.variable_port_associations[record_id]
        subject = (record.variable_anchor_id, record.port_anchor_id,
                   record.context)
        subjects.setdefault(subject, set()).add(
            loaded.variable_port_association_root_by_id[record_id])
    pending = []
    for (variable_anchor_id, port_anchor_id, _), roots in subjects.items():
        variable = loaded.variable_registrations_by_anchor[variable_anchor_id]
        port = loaded.port_registrations_by_anchor[port_anchor_id]
        variable_owner = loaded.registrations_by_anchor[
            variable.anchor.entity_anchor_id]
        port_owner = loaded.registrations_by_anchor[port.owner_entity_anchor_id]
        root_payloads = _variable_port_root_payloads(
            material, loaded, tuple(roots))
        conclusion, summary = _variable_port_conclusion(root_payloads)
        # A stored subject necessarily has at least one root, so collection
        # conclusions can only be asserted or inactive.
        first_root_id = min(roots)
        sort_anchor = (port_anchor_id if order_by == "port" else
                       variable_anchor_id)
        pending.append(((sort_anchor, first_root_id), {
            "variable_anchor_id": variable_anchor_id,
            "port_anchor_id": port_anchor_id,
            "variable_registration_index": indices[variable.record_id],
            "variable_owner_registration_index": indices[
                variable_owner.record_id],
            "port_registration_index": indices[port.record_id],
            "port_owner_registration_index": indices[port_owner.record_id],
            "conclusion": conclusion,
            "lineage_summary": summary,
            "roots": tuple(root_payloads),
        }))
    return tuple({"entry_index": entry_index, **payload}
                 for entry_index, (_, payload) in enumerate(sorted(pending)))


class VariablePortsResult(_WithMaterial):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: VariablePortsStatus
    variable_registration_index: _VariablePortIndex | None = None
    owner_registration_index: _VariablePortIndex | None = None
    entries: tuple[VariablePortAssociationEntry, ...] = ()

    @property
    def variable_registration(self):
        return (None if self.variable_registration_index is None else
                self.material.record_at(self.variable_registration_index))

    @property
    def owner_registration(self):
        return (None if self.owner_registration_index is None else
                self.material.record_at(self.owner_registration_index))

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        indices = {record_id: index for index, record_id
                   in enumerate(self.material.revision.record_ids)}
        variable = loaded.variable_registrations_by_anchor.get(
            self.variable_anchor_id)
        if variable is None:
            expected_status = "variable_not_registered"
            variable_index = owner_index = None
            payloads = ()
        else:
            expected_status = "registered"
            variable_index = indices[variable.record_id]
            owner_index = indices[loaded.registrations_by_anchor[
                variable.anchor.entity_anchor_id].record_id]
            association_ids = (
                loaded.variable_port_association_ids_by_variable_context.get(
                    (self.variable_anchor_id, context), ()))
            payloads = _variable_port_entry_payloads(
                self.material, loaded, association_ids, order_by="port")
        supplied = (
            self.status, self.variable_registration_index,
            self.owner_registration_index,
            tuple(row.model_dump() for row in self.entries),
        )
        expected = (expected_status, variable_index, owner_index,
                    tuple(payloads))
        if supplied != expected:
            raise ValueError("variable-to-ports disclosure is forged")
        for entry in self.entries:
            object.__setattr__(entry, "_material", self.material)
            _bind_variable_port_roots(entry.roots, self.material)
        return self


class PortVariablesResult(_WithMaterial):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: PortVariablesStatus
    port_registration_index: _VariablePortIndex | None = None
    owner_registration_index: _VariablePortIndex | None = None
    entries: tuple[VariablePortAssociationEntry, ...] = ()

    @property
    def port_registration(self):
        return (None if self.port_registration_index is None else
                self.material.record_at(self.port_registration_index))

    @property
    def owner_registration(self):
        return (None if self.owner_registration_index is None else
                self.material.record_at(self.owner_registration_index))

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        indices = {record_id: index for index, record_id
                   in enumerate(self.material.revision.record_ids)}
        port = loaded.port_registrations_by_anchor.get(self.port_anchor_id)
        if port is None:
            expected_status = "port_not_registered"
            port_index = owner_index = None
            payloads = ()
        else:
            expected_status = "registered"
            port_index = indices[port.record_id]
            owner_index = indices[loaded.registrations_by_anchor[
                port.owner_entity_anchor_id].record_id]
            association_ids = (
                loaded.variable_port_association_ids_by_port_context.get(
                    (self.port_anchor_id, context), ()))
            payloads = _variable_port_entry_payloads(
                self.material, loaded, association_ids, order_by="variable")
        supplied = (
            self.status, self.port_registration_index,
            self.owner_registration_index,
            tuple(row.model_dump() for row in self.entries),
        )
        expected = (expected_status, port_index, owner_index, tuple(payloads))
        if supplied != expected:
            raise ValueError("port-to-variables disclosure is forged")
        for entry in self.entries:
            object.__setattr__(entry, "_material", self.material)
            _bind_variable_port_roots(entry.roots, self.material)
        return self


class VariablePortAssertionDisclosureResult(_WithMaterial):
    record_id: str = Field(pattern=r"^(?:vpa|vpw)_[0-9a-f]{64}$")
    lookup_status: VariablePortAssertionLookupStatus
    record_index: _VariablePortIndex | None = None
    activity: AssertionActivity | None = None
    containing_lineage_health: ContainingLineageHealth | None = None
    root_record_index: _VariablePortIndex | None = None
    successor_indices: tuple[_VariablePortIndex, ...] = ()
    withdrawal_indices: tuple[_VariablePortIndex, ...] = ()

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

    @model_validator(mode="after")
    def _coherent(self):
        loaded = self.material.loaded()
        indices = {record_id: index for index, record_id
                   in enumerate(self.material.revision.record_ids)}
        record = loaded.records.get(self.record_id)
        found = (record is not None and record.record_kind in {
            "variable_port_association",
            "variable_port_association_withdrawal",
        })
        expected_lookup = "found" if found else "not_found"
        if not found:
            expected = (expected_lookup, None, None, None, None, (), ())
        elif record.record_kind == "variable_port_association_withdrawal":
            expected = (
                expected_lookup, indices[self.record_id], None, None, None,
                (), (),
            )
        else:
            root_id = loaded.variable_port_association_root_by_id[
                self.record_id]
            tips = loaded.current_variable_port_association_tips_by_root[
                root_id]
            successors = loaded.variable_port_association_superseded_by[
                self.record_id]
            withdrawals = loaded.variable_port_association_withdrawn_by[
                self.record_id]
            activity = (
                "superseded" if successors else
                "withdrawn" if withdrawals else
                "current")
            health = (
                "inactive" if not tips else
                "conflicted" if len(tips) > 1 else
                "healthy")
            expected = (
                expected_lookup, indices[self.record_id], activity, health,
                indices[root_id],
                tuple(indices[record_id] for record_id in sorted(successors)),
                tuple(indices[record_id] for record_id in sorted(withdrawals)),
            )
        supplied = (
            self.lookup_status, self.record_index, self.activity,
            self.containing_lineage_health, self.root_record_index,
            self.successor_indices, self.withdrawal_indices,
        )
        if supplied != expected:
            raise ValueError("variable-port assertion disclosure is forged")
        return self


class ConnectionRootResult(_Result):
    _material: ModelQueryMaterial = PrivateAttr()
    root_index: int = Field(ge=0)
    root_record_index: int = Field(ge=0)
    lineage_record_indices: tuple[int, ...]
    current_tip_indices: tuple[int, ...]
    withdrawal_indices: tuple[int, ...]
    lineage_health: ContainingLineageHealth
    exact_endpoint_set: bool

    @property
    def root(self):
        return self._material.record_at(self.root_record_index)

    @property
    def lineage_records(self):
        return tuple(self._material.record_at(i) for i in self.lineage_record_indices)

    @property
    def current_tips(self):
        return tuple(self._material.record_at(i) for i in self.current_tip_indices)

    @property
    def withdrawals(self):
        return tuple(self._material.record_at(i) for i in self.withdrawal_indices)


class ConnectionSubjectResult(_Result):
    subject_index: int = Field(ge=0)
    endpoint_port_anchor_ids: tuple[str, ...]
    conclusion: Literal["asserted", "inactive"]
    root_indices: tuple[int, ...]


class _ConnectionsResult(_WithMaterial):
    context: AssertionContext
    conclusion: TopologyConclusion
    roots: tuple[ConnectionRootResult, ...] = ()
    subjects: tuple[ConnectionSubjectResult, ...] = ()

    @model_validator(mode="after")
    def _bind(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        ids_to_index = {value: index for index, value
                        in enumerate(self.material.revision.record_ids)}
        if isinstance(self, ExactConnectionSetResult):
            _validate_endpoint_subject(self.requested_port_anchor_ids)
            selected = loaded.port_connection_ids_by_subject.get(
                (self.requested_port_anchor_ids, context), ())
            requested = self.requested_port_anchor_ids
            expected_missing = tuple(
                port_id for port_id in requested
                if port_id not in loaded.port_registrations_by_anchor)
            if self.unregistered_port_anchor_ids != expected_missing:
                raise ValueError("exact endpoint registration status is forged")
            expected_admission = (
                "endpoint_not_registered" if expected_missing else "admitted")
            if self.admission_status != expected_admission:
                raise ValueError("exact topology admission status is forged")
        elif isinstance(self, PortConnectionsResult):
            selected = tuple(i for i in loaded.port_connection_ids_by_port.get(
                self.port_anchor_id, ()) if loaded.port_connections[i].context == context)
            requested = (self.port_anchor_id,)
            expected_port = ("registered" if self.port_anchor_id
                             in loaded.port_registrations_by_anchor else
                             "port_not_registered")
            if self.status != expected_port:
                raise ValueError("incident port status is forged")
        elif isinstance(self, SharedConnectionsResult):
            _validate_endpoint_subject(self.requested_port_anchor_ids)
            requested = self.requested_port_anchor_ids
            wanted = set(requested)
            selected = tuple(i for i, record in loaded.port_connections.items()
                             if record.context == context
                             and wanted.issubset(record.endpoint_port_anchor_ids))
            expected_missing = tuple(p for p in requested
                                     if p not in loaded.port_registrations_by_anchor)
            if self.unregistered_port_anchor_ids != expected_missing:
                raise ValueError("shared endpoint registration status is forged")
            expected_admission = (
                "endpoint_not_registered" if expected_missing else "admitted")
            if self.admission_status != expected_admission:
                raise ValueError("shared topology admission status is forged")
        else:
            raise ValueError("unsupported connection result contract")
        expected = _connection_parts_payload(
            self.material, loaded, selected, requested,
            record_indices=ids_to_index)
        if (self.conclusion != expected["conclusion"]
                or tuple(row.model_dump() for row in self.roots)
                != expected["roots"]
                or tuple(row.model_dump() for row in self.subjects)
                != expected["subjects"]):
            raise ValueError("connection disclosure is forged")
        for row in self.roots:
            object.__setattr__(row, "_material", self.material)
        return self


class ExactConnectionSetResult(_ConnectionsResult):
    admission_status: TopologyAdmissionStatus
    requested_port_anchor_ids: tuple[str, ...]
    unregistered_port_anchor_ids: tuple[str, ...] = ()


class PortConnectionsResult(_ConnectionsResult):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    status: PortConnectionsStatus


class SharedConnectionsResult(_ConnectionsResult):
    admission_status: TopologyAdmissionStatus
    requested_port_anchor_ids: tuple[str, ...]
    unregistered_port_anchor_ids: tuple[str, ...] = ()


class InterfaceCompatibilityResult(_WithMaterial):
    requested_left_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    requested_right_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    endpoint_port_anchor_ids: tuple[str, str]
    context: AssertionContext
    endpoint_registration_status: CompatibilityEndpointStatus
    left_interface: EndpointInterfaceResult
    right_interface: EndpointInterfaceResult
    domain_relation: Literal["token_identical", "token_different",
                             "not_declared", "conflicted", "inactive"]
    interface_type_relation: Literal["token_identical", "token_different",
                                    "not_declared", "conflicted", "inactive"]
    direction_relation: Literal["admissible", "inadmissible",
                                "not_applicable", "indeterminate"]
    explicit_status: ExplicitCompatibilityStatus
    explicit_declaration_index: int | None = Field(default=None, ge=0)
    conflicting_explicit_declaration_indices: tuple[int, ...] = ()
    pcm_lineage_record_indices: tuple[int, ...] = ()
    current_pcm_tip_indices: tuple[int, ...] = ()
    stale_citation_indices: tuple[int, ...] = ()
    consistency: CrossFindingConsistency

    @model_validator(mode="after")
    def _bind(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        from backend.model_kernel.queries import ModelQueries
        queries = ModelQueries(loaded)
        expected_left = queries.port_interface(
            self.requested_left_port_anchor_id, context=context)
        expected_right = queries.port_interface(
            self.requested_right_port_anchor_id, context=context)
        if self.endpoint_port_anchor_ids != tuple(sorted((
                self.requested_left_port_anchor_id,
                self.requested_right_port_anchor_id))):
            raise ValueError("compatibility endpoint pair is forged")
        if self.requested_left_port_anchor_id == self.requested_right_port_anchor_id:
            raise ValueError("compatibility endpoints must be distinct")
        left_registered = expected_left.status == "registered"
        right_registered = expected_right.status == "registered"
        expected_endpoint_status = (
            "both_registered" if left_registered and right_registered else
            "left_not_registered" if not left_registered and right_registered else
            "right_not_registered" if left_registered and not right_registered else
            "both_not_registered")
        if self.endpoint_registration_status != expected_endpoint_status:
            raise ValueError("compatibility registration status is forged")
        for supplied, expected in ((self.left_interface, expected_left),
                                   (self.right_interface, expected_right)):
            registration = loaded.port_registrations_by_anchor.get(
                supplied.port_anchor_id)
            expected_port_index = (None if registration is None else
                self.material.revision.record_ids.index(registration.record_id))
            expected_owner_index = (None if registration is None else
                self.material.revision.record_ids.index(
                    loaded.registrations_by_anchor[
                        registration.owner_entity_anchor_id].record_id))
            if (supplied.port_anchor_id != expected.port_anchor_id
                    or supplied.status != expected.status
                    or supplied.port_registration_index != expected_port_index
                    or supplied.owner_registration_index != expected_owner_index
                    or tuple(row.model_dump() for row in supplied.dimensions)
                    != tuple(row.model_dump() for row in expected.dimensions)):
                raise ValueError("compatibility interface disclosure is forged")

        def relation(position):
            left, right = self.left_interface.dimensions[position], self.right_interface.dimensions[position]
            statuses = {left.status, right.status}
            if "port_not_registered" in statuses:
                return "not_declared"
            if "conflicted" in statuses:
                return "conflicted"
            if "inactive" in statuses:
                return "inactive"
            if statuses != {"declared"}:
                return "not_declared"
            lv = self.material.records[left.declaration_index].declaration.value
            rv = self.material.records[right.declaration_index].declaration.value
            return "token_identical" if lv == rv else "token_different"
        if self.domain_relation != relation(0) or self.interface_type_relation != relation(2):
            raise ValueError("compatibility token relation is forged")
        ld, rd = self.left_interface.dimensions[1], self.right_interface.dimensions[1]
        if ld.status != "declared" or rd.status != "declared":
            direction = "indeterminate"
        else:
            lv = self.material.records[ld.declaration_index].declaration.value
            rv = self.material.records[rd.declaration_index].declaration.value
            direction = ("not_applicable" if lv == rv == "non_directional" else
                         "indeterminate" if "non_directional" in (lv, rv) else
                         "inadmissible" if lv == rv and lv in ("input", "output") else
                         "admissible")
        if self.direction_relation != direction:
            raise ValueError("compatibility direction relation is forged")
        indices = {value: index for index, value
                   in enumerate(self.material.revision.record_ids)}
        pcm_ids = loaded.port_compatibility_ids_by_key.get(
            (self.endpoint_port_anchor_ids, context), ())
        tips = loaded.current_port_compatibility_tips_by_key.get(
            (self.endpoint_port_anchor_ids, context), ())
        stale_ids = []
        for tip in tips:
            for citation_id in loaded.port_compatibility_citations[tip.record_id]:
                citation = loaded.port_interface_declarations[citation_id]
                current = loaded.current_port_interface_tips_by_key.get((
                    citation.port_anchor_id, context,
                    citation.declaration.dimension), ())
                if (len(current) != 1
                        or current[0].record_id != citation_id):
                    stale_ids.append(citation_id)
        stale_ids = tuple(sorted(set(stale_ids)))
        if not pcm_ids:
            explicit, declaration_index, conflicts = "not_declared", None, ()
        elif not tips:
            explicit, declaration_index, conflicts = "inactive", None, ()
        elif len(tips) > 1:
            explicit, declaration_index = "conflicted", None
            conflicts = tuple(indices[item.record_id] for item in tips)
        else:
            explicit = "stale" if stale_ids else tips[0].outcome
            declaration_index, conflicts = indices[tips[0].record_id], ()
        if (self.explicit_status != explicit
                or self.explicit_declaration_index != declaration_index
                or self.conflicting_explicit_declaration_indices != conflicts
                or self.pcm_lineage_record_indices != tuple(indices[i] for i in pcm_ids)
                or self.current_pcm_tip_indices != tuple(indices[i.record_id] for i in tips)
                or self.stale_citation_indices != tuple(indices[i] for i in stale_ids)):
            raise ValueError("explicit compatibility disclosure is forged")
        if self.explicit_status in ("declared_compatible", "declared_incompatible") \
                and direction in ("admissible", "inadmissible"):
            expected_consistency = ("consistent" if
                (self.explicit_status == "declared_compatible") ==
                (direction == "admissible") else "inconsistent")
        else:
            expected_consistency = "indeterminate"
        if self.consistency != expected_consistency:
            raise ValueError("compatibility consistency is forged")
        for endpoint in (self.left_interface, self.right_interface):
            for row in endpoint.dimensions:
                object.__setattr__(row, "_material", self.material)
        return self
