"""PT-001 read-only query result contracts.

All authority is carried once in ``ModelQueryMaterial``.  Result rows contain
only indices into that immutable, fully revalidated collection.
"""

import re
from typing import Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, TypeAdapter, ValidationError,
    model_validator,
)

from backend.model_kernel.contracts import (
    AssertionContext, ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN, ModelIntegrityError, ModelQueryError, ModelRecord,
    ModelRevision,
)

_CONTEXT_ADAPTER = TypeAdapter(AssertionContext)


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


class PortResult(_WithMaterial):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    status: Literal["registered", "not_registered"]
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
    status: Literal["registered", "not_registered"]
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
        if self.status != ("registered" if registered else "not_registered"):
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
        registered = self.port_anchor_id in loaded.port_registrations_by_anchor
        ids_to_index = {value: index for index, value
                        in enumerate(self.material.revision.record_ids)}
        expected = []
        for dimension in ("interface_domain", "direction_role", "interface_type"):
            key = (self.port_anchor_id, context, dimension)
            ids = loaded.port_interface_ids_by_key.get(key, ()) if registered else ()
            tips = loaded.current_port_interface_tips_by_key.get(key, ()) if ids else ()
            withdrawals = tuple(sorted(w for record_id in ids
                                       for w in loaded.port_interface_withdrawn_by[record_id]))
            status = ("port_not_registered" if not registered else
                      "not_declared" if not ids else
                      "declared" if len(tips) == 1 else
                      "conflicted" if tips else "inactive")
            expected.append(dict(
                dimension=dimension, status=status,
                lineage_health=(
                    "healthy" if status == "declared" else
                    "conflicted" if status == "conflicted" else
                    "inactive" if status == "inactive" else
                    "not_applicable"),
                lineage_record_indices=tuple(ids_to_index[i] for i in ids),
                current_tip_indices=tuple(ids_to_index[r.record_id] for r in tips),
                withdrawal_indices=tuple(ids_to_index[i] for i in withdrawals),
                declaration_index=(ids_to_index[tips[0].record_id]
                                   if status == "declared" else None),
                conflicting_declaration_indices=(tuple(
                    ids_to_index[r.record_id] for r in tips)
                    if status == "conflicted" else ()),
                superseded_declaration_indices=(tuple(
                    ids_to_index[i] for i in ids
                    if loaded.port_interface_superseded_by[i]) if registered else ()),
                inactive_declaration_indices=tuple(
                    ids_to_index[i] for i in ids
                    if loaded.port_interface_withdrawn_by[i])))
        if self.status != ("registered" if registered else "not_registered"):
            raise ValueError("interface port status is forged")
        if tuple(row.model_dump() for row in self.dimensions) != tuple(expected):
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


class PortAssertionResult(_WithMaterial):
    record_id: str = Field(
        pattern=r"^(prg|pif|pcn|pcm|ptw)_[0-9a-f]{64}$")
    status: Literal["found", "not_found"]
    record_index: int | None = Field(default=None, ge=0)
    activity: Literal["current", "superseded", "withdrawn"] | None = None
    lineage_health: Literal["healthy", "conflicted", "inactive"] | None = None
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
        indices = {value: index for index, value
                   in enumerate(self.material.revision.record_ids)}
        record = loaded.records.get(self.record_id)
        pt_kinds = {"port_registration", "port_interface_declaration",
                    "port_connection_assertion", "port_compatibility_declaration",
                    "port_claim_withdrawal"}
        found = record is not None and record.record_kind in pt_kinds
        if self.status != ("found" if found else "not_found"):
            raise ValueError("assertion membership status is forged")
        if not found:
            if any((self.record_index is not None, self.activity is not None,
                    self.lineage_health is not None, self.root_record_index is not None,
                    self.successor_indices, self.withdrawal_indices)):
                raise ValueError("missing assertion carries no lifecycle")
            return self
        if self.record_index != indices[self.record_id]:
            raise ValueError("assertion record index is forged")
        if record.record_kind in {"port_registration", "port_claim_withdrawal"}:
            if any((self.activity is not None, self.lineage_health is not None,
                    self.root_record_index is not None, self.successor_indices,
                    self.withdrawal_indices)):
                raise ValueError("permanent/event disclosure has no claim lifecycle")
            return self
        if record.record_kind == "port_interface_declaration":
            roots, successors, withdrawn = (
                loaded.port_interface_root_by_id,
                loaded.port_interface_superseded_by,
                loaded.port_interface_withdrawn_by)
        elif record.record_kind == "port_connection_assertion":
            roots, successors, withdrawn = (
                loaded.port_connection_root_by_id,
                loaded.port_connection_superseded_by,
                loaded.port_connection_withdrawn_by)
        else:
            roots, successors, withdrawn = (
                loaded.port_compatibility_root_by_id,
                loaded.port_compatibility_superseded_by,
                loaded.port_compatibility_withdrawn_by)
        root = roots[self.record_id]
        lineage_ids = tuple(i for i, value in roots.items() if value == root)
        tips = tuple(i for i in lineage_ids if not successors[i] and not withdrawn[i])
        expected_activity = ("superseded" if successors[self.record_id] else
                             "withdrawn" if withdrawn[self.record_id] else "current")
        expected_health = ("inactive" if not tips else
                           "conflicted" if len(tips) > 1 else "healthy")
        if (self.activity != expected_activity
                or self.lineage_health != expected_health
                or self.root_record_index != indices[root]
                or self.successor_indices != tuple(indices[i] for i in successors[self.record_id])
                or self.withdrawal_indices != tuple(indices[i] for i in withdrawn[self.record_id])):
            raise ValueError("assertion lifecycle disclosure is forged")
        return self


class ConnectionRootResult(_Result):
    _material: ModelQueryMaterial = PrivateAttr()
    root_index: int = Field(ge=0)
    root_record_index: int = Field(ge=0)
    lineage_record_indices: tuple[int, ...]
    current_tip_indices: tuple[int, ...]
    withdrawal_indices: tuple[int, ...]
    lineage_health: Literal["healthy", "conflicted", "inactive"]
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
    status: Literal["unknown", "asserted", "inactive"]
    roots: tuple[ConnectionRootResult, ...] = ()
    subjects: tuple[ConnectionSubjectResult, ...] = ()

    @model_validator(mode="after")
    def _bind(self):
        loaded = self.material.loaded()
        context = _validated_context(self.context)
        ids_to_index = {value: index for index, value
                        in enumerate(self.material.revision.record_ids)}
        if isinstance(self, ExactConnectionsResult):
            _validate_endpoint_subject(self.requested_port_anchor_ids)
            selected = loaded.port_connection_ids_by_subject.get(
                (self.requested_port_anchor_ids, context), ())
            requested = self.requested_port_anchor_ids
            expected_missing = tuple(
                port_id for port_id in requested
                if port_id not in loaded.port_registrations_by_anchor)
            if self.unregistered_port_anchor_ids != expected_missing:
                raise ValueError("exact endpoint registration status is forged")
        elif isinstance(self, IncidentConnectionsResult):
            selected = tuple(i for i in loaded.port_connection_ids_by_port.get(
                self.port_anchor_id, ()) if loaded.port_connections[i].context == context)
            requested = (self.port_anchor_id,)
            expected_port = ("registered" if self.port_anchor_id
                             in loaded.port_registrations_by_anchor else "not_registered")
            if self.port_status != expected_port:
                raise ValueError("incident port status is forged")
        else:
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
        root_ids = sorted({loaded.port_connection_root_by_id[i] for i in selected})
        expected_rows = []
        for position, root_id in enumerate(root_ids):
            lineage = tuple(sorted(i for i, root in loaded.port_connection_root_by_id.items()
                                   if root == root_id))
            tips = loaded.current_port_connection_tips_by_root[root_id]
            withdrawals = tuple(sorted(w for i in lineage
                                       for w in loaded.port_connection_withdrawn_by[i]))
            expected_rows.append(dict(
                root_index=position, root_record_index=ids_to_index[root_id],
                lineage_record_indices=tuple(ids_to_index[i] for i in lineage),
                current_tip_indices=tuple(ids_to_index[i.record_id] for i in tips),
                withdrawal_indices=tuple(ids_to_index[i] for i in withdrawals),
                lineage_health=("inactive" if not tips else
                                "conflicted" if len(tips) > 1 else "healthy"),
                exact_endpoint_set=(loaded.port_connections[root_id].endpoint_port_anchor_ids
                                    == requested)))
        expected_status = ("unknown" if not expected_rows else "asserted"
                           if any(row["current_tip_indices"] for row in expected_rows)
                           else "inactive")
        roots_by_subject = {}
        for root_position, root_id in enumerate(root_ids):
            subject = loaded.port_connections[root_id].endpoint_port_anchor_ids
            roots_by_subject.setdefault(subject, []).append(root_position)
        expected_subjects = tuple(
            dict(
                subject_index=position,
                endpoint_port_anchor_ids=subject,
                conclusion=("asserted" if any(
                    expected_rows[root_index]["current_tip_indices"]
                    for root_index in root_indices) else "inactive"),
                root_indices=tuple(root_indices),
            )
            for position, (subject, root_indices) in enumerate(
                sorted(roots_by_subject.items()))
        )
        if self.status != expected_status or tuple(
                row.model_dump() for row in self.roots) != tuple(expected_rows) \
                or tuple(row.model_dump() for row in self.subjects) != \
                expected_subjects:
            raise ValueError("connection disclosure is forged")
        for row in self.roots:
            object.__setattr__(row, "_material", self.material)
        return self


class ExactConnectionsResult(_ConnectionsResult):
    requested_port_anchor_ids: tuple[str, ...]
    unregistered_port_anchor_ids: tuple[str, ...] = ()


class IncidentConnectionsResult(_ConnectionsResult):
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    port_status: Literal["registered", "not_registered"]


class ContainingConnectionsResult(_ConnectionsResult):
    requested_port_anchor_ids: tuple[str, ...]
    unregistered_port_anchor_ids: tuple[str, ...] = ()


class InterfaceCompatibilityResult(_WithMaterial):
    requested_left_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    requested_right_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    endpoint_port_anchor_ids: tuple[str, str]
    context: AssertionContext
    endpoint_registration_status: tuple[
        Literal["registered", "not_registered"],
        Literal["registered", "not_registered"]]
    left_interface: EndpointInterfaceResult
    right_interface: EndpointInterfaceResult
    domain_relation: Literal["token_identical", "token_different",
                             "not_declared", "conflicted", "inactive"]
    interface_type_relation: Literal["token_identical", "token_different",
                                    "not_declared", "conflicted", "inactive"]
    direction_relation: Literal["admissible", "inadmissible",
                                "not_applicable", "indeterminate"]
    explicit_status: Literal["not_declared", "declared_compatible",
                             "declared_incompatible", "conflicted",
                             "inactive", "stale"]
    explicit_declaration_index: int | None = Field(default=None, ge=0)
    conflicting_explicit_declaration_indices: tuple[int, ...] = ()
    pcm_lineage_record_indices: tuple[int, ...] = ()
    current_pcm_tip_indices: tuple[int, ...] = ()
    stale_citation_indices: tuple[int, ...] = ()
    consistency: Literal["consistent", "inconsistent", "indeterminate"]

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
        if self.endpoint_registration_status != (
                expected_left.status, expected_right.status):
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
