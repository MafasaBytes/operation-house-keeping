"""ST-001 read-only kernel result contracts and authoritative derivation.

Complete model authority is carried once in :class:`ModelQueryMaterial`.
Nested rows contain strict indices only. Query construction and public result
validation share the deterministic private payload derivations below.
"""

from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, StrictInt, field_validator,
    model_validator,
)

from backend.model_kernel.canonical import _state_effective_body_bytes
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.port_results import (
    AssertionActivity, ContainingLineageHealth, ModelQueryMaterial,
)
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN, ENTITY_ANCHOR_ID_PATTERN,
    STATE_ANCHOR_ID_PATTERN,
)


StateLookupStatus = Literal["not_registered", "registered"]
StateDeclarationConclusion = Literal[
    "not_registered", "not_declared", "declared", "conflicted", "inactive",
]
StateDeclarationLineageSummary = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
StateAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]
EntityStatesStatus = Literal["entity_not_registered", "registered"]
StateAssertionLookupStatus = Literal["not_found", "found"]

_StateIndex = Annotated[StrictInt, Field(ge=0)]


class _StateResult(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="before")
    @classmethod
    def _reject_hidden_instance_fields(cls, value):
        """Reject extras that ``model_copy`` can hide from serialization."""
        pending = [value]
        seen: set[int] = set()
        while pending:
            item = pending.pop()
            identity = id(item)
            if identity in seen:
                continue
            seen.add(identity)
            if isinstance(item, BaseModel):
                fields = type(item).model_fields
                stored = vars(item)
                extras = getattr(item, "__pydantic_extra__", None)
                if set(stored).difference(fields) or extras:
                    raise ValueError(
                        "pydantic result instance contains extra fields")
                pending.extend(stored[field] for field in fields
                               if field in stored)
            elif isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, (tuple, list, set, frozenset)):
                pending.extend(item)
        return value


def _dump_nested(value):
    return (value.model_dump(mode="python")
            if isinstance(value, BaseModel) else value)


def _rebuild_material(value) -> ModelQueryMaterial:
    return ModelQueryMaterial.model_validate(_dump_nested(value))


def _rebuild_context(value) -> AssertionContext:
    from pydantic import TypeAdapter
    return TypeAdapter(AssertionContext).validate_python(_dump_nested(value))


def _rebuild_rows(value, contract, label: str):
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{label} must be a tuple of result rows")
    return tuple(contract.model_validate(_dump_nested(row)) for row in value)


def _indices(material: ModelQueryMaterial) -> dict[str, int]:
    return {record_id: index for index, record_id
            in enumerate(material.revision.record_ids)}


def _condition_payloads(loaded, declaration, indices) -> tuple[dict, ...]:
    rows = []
    for condition_index, pin in enumerate(declaration.conditions):
        constraint = loaded.constraint_registrations_by_anchor[
            pin.constraint_anchor_id]
        variable = loaded.variable_registrations_by_anchor[
            constraint.variable_anchor_id]
        owner = loaded.registrations_by_anchor[
            variable.anchor.entity_anchor_id]
        rows.append({
            "condition_index": condition_index,
            "constraint_anchor_id": pin.constraint_anchor_id,
            "constraint_registration_index": indices[constraint.record_id],
            "pinned_declaration_index": indices[
                pin.constraint_declaration_record_id],
            "target_variable_registration_index": indices[variable.record_id],
            "target_owner_registration_index": indices[owner.record_id],
        })
    return tuple(rows)


def _state_lookup_payload(material: ModelQueryMaterial, loaded,
                          state_anchor_id: str, *,
                          record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.state_registrations_by_anchor.get(state_anchor_id)
    if registration is None:
        return {
            "state_anchor_id": state_anchor_id,
            "status": "not_registered",
            "registration_index": None,
            "subject_entity_registration_index": None,
            "condition_constraint_registration_indices": (),
            "condition_variable_registration_indices": (),
            "condition_owner_registration_indices": (),
        }
    subject = loaded.registrations_by_anchor[
        registration.subject_entity_anchor_id]
    constraint_indices = []
    variable_indices = []
    owner_indices = []
    for constraint_id in registration.condition_constraint_anchor_ids:
        constraint = loaded.constraint_registrations_by_anchor[constraint_id]
        variable = loaded.variable_registrations_by_anchor[
            constraint.variable_anchor_id]
        owner = loaded.registrations_by_anchor[
            variable.anchor.entity_anchor_id]
        constraint_indices.append(indices[constraint.record_id])
        variable_indices.append(indices[variable.record_id])
        owner_indices.append(indices[owner.record_id])
    return {
        "state_anchor_id": state_anchor_id,
        "status": "registered",
        "registration_index": indices[registration.record_id],
        "subject_entity_registration_index": indices[subject.record_id],
        "condition_constraint_registration_indices": tuple(
            constraint_indices),
        "condition_variable_registration_indices": tuple(variable_indices),
        "condition_owner_registration_indices": tuple(owner_indices),
    }


def _state_declaration_payload(material: ModelQueryMaterial, loaded,
                               state_anchor_id: str,
                               context: AssertionContext, *,
                               record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.state_registrations_by_anchor.get(state_anchor_id)
    base = {
        "state_anchor_id": state_anchor_id,
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

    declaration_ids = loaded.state_declaration_ids_by_key.get(
        (state_anchor_id, context), ())
    root_ids = tuple(sorted({
        loaded.state_declaration_root_by_id[record_id]
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
        lineage_ids_by_root[
            loaded.state_declaration_root_by_id[record_id]].append(record_id)

    root_work = []
    body_by_tip: dict[str, bytes] = {}
    root_by_tip: dict[str, str] = {}
    for root_id in root_ids:
        lineage_ids = tuple(sorted(lineage_ids_by_root[root_id]))
        tips = tuple(sorted(
            loaded.current_state_declaration_tips_by_root[root_id],
            key=lambda record: record.record_id))
        tip_ids = tuple(record.record_id for record in tips)
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in loaded.state_declaration_withdrawn_by[
                record_id]))
        health = (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else
            "healthy")
        for tip in tips:
            body_by_tip[tip.record_id] = _state_effective_body_bytes(tip)
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
    body_to_group_index = {
        body: group_index
        for group_index, body in enumerate(sorted(tip_ids_by_body))
    }
    group_payloads = []
    for body in sorted(tip_ids_by_body):
        tip_ids = tuple(sorted(tip_ids_by_body[body]))
        representative_id = min(tip_ids)
        representative = loaded.state_declarations[representative_id]
        root_record_ids = tuple(sorted({
            root_by_tip[tip_id] for tip_id in tip_ids
        }))
        group_payloads.append({
            "group_index": body_to_group_index[body],
            "representative_declaration_index": indices[representative_id],
            "current_tip_indices": tuple(indices[tip_id]
                                         for tip_id in tip_ids),
            "root_record_indices": tuple(indices[root_id]
                                         for root_id in root_record_ids),
            "conditions": _condition_payloads(
                loaded, representative, indices),
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
                indices[record_id] for record_id in row["lineage_ids"]),
            "current_tip_indices": tuple(
                indices[record_id] for record_id in row["tip_ids"]),
            "withdrawal_indices": tuple(
                indices[record_id] for record_id in row["withdrawal_ids"]),
            "lineage_health": row["lineage_health"],
            "effective_body_group_indices": group_indices,
        })

    healthy = tuple(row for row in root_work
                    if row["lineage_health"] == "healthy")
    conflicted = tuple(row for row in root_work
                       if row["lineage_health"] == "conflicted")
    inactive = tuple(row for row in root_work
                     if row["lineage_health"] == "inactive")
    healthy_bodies = tuple(body_by_tip[row["tip_ids"][0]] for row in healthy)
    healthy_roots_by_body: dict[bytes, list[str]] = {}
    for row, body in zip(healthy, healthy_bodies):
        healthy_roots_by_body.setdefault(body, []).append(row["root_id"])

    findings = []
    if len(healthy) == 1:
        findings.append("one_healthy_root")
    if any(len(roots) >= 2
           for roots in healthy_roots_by_body.values()):
        findings.append("corroborating_healthy_roots")
    if conflicted:
        findings.append("same_root_conflict")
    if len(set(healthy_bodies)) > 1:
        findings.append("cross_root_effective_body_disagreement")
    if inactive:
        findings.append("inactive_roots_present")

    active_tip_ids = tuple(sorted(body_by_tip))
    if not active_tip_ids:
        conclusion = "inactive"
        summary = "inactive"
    elif conflicted or len(set(healthy_bodies)) > 1:
        conclusion = "conflicted"
        summary = "conflicted"
    else:
        conclusion = "declared"
        summary = "healthy"
    return {
        **base,
        "conclusion": conclusion,
        "lineage_summary": summary,
        "agreement_findings": tuple(findings),
        "registration_index": indices[registration.record_id],
        "roots": tuple(root_payloads),
        "effective_body_groups": tuple(group_payloads),
        "current_declaration_indices": tuple(
            indices[record_id] for record_id in active_tip_ids),
    }


def _entity_states_payload(material: ModelQueryMaterial, loaded,
                           entity_anchor_id: str,
                           context: AssertionContext) -> dict:
    indices = _indices(material)
    entity = loaded.registrations_by_anchor.get(entity_anchor_id)
    base = {
        "entity_anchor_id": entity_anchor_id,
        "context": context.model_dump(mode="python"),
    }
    if entity is None:
        return {
            **base,
            "status": "entity_not_registered",
            "entity_registration_index": None,
            "entries": (),
        }

    pending = []
    for state_anchor_id in loaded.state_anchor_ids_by_subject_entity.get(
            entity_anchor_id, ()):
        registration = loaded.state_registrations_by_anchor[state_anchor_id]
        declaration = _state_declaration_payload(
            material, loaded, state_anchor_id, context,
            record_indices=indices)
        first_root_id = (
            material.revision.record_ids[
                declaration["roots"][0]["root_record_index"]]
            if declaration["roots"] else "")
        pending.append((state_anchor_id, first_root_id, {
            "state_anchor_id": state_anchor_id,
            "state_registration_index": indices[registration.record_id],
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
        "entity_registration_index": indices[entity.record_id],
        "entries": entries,
    }


def _state_assertion_payload(material: ModelQueryMaterial, loaded,
                             record_id: str) -> dict:
    indices = _indices(material)
    record = loaded.records.get(record_id)
    found = record is not None and record.record_kind in {
        "state_registration", "state_declaration",
        "state_declaration_withdrawal",
    }
    base = {
        "record_id": record_id,
        "lookup_status": "found" if found else "not_found",
    }
    empty = {
        "activity": None,
        "containing_lineage_health": None,
        "containing_subject_conclusion": None,
        "containing_agreement_findings": None,
        "root_record_index": None,
        "successor_indices": (),
        "withdrawal_indices": (),
    }
    if not found:
        return {**base, "record_index": None, **empty}
    if record.record_kind != "state_declaration":
        return {**base, "record_index": indices[record_id], **empty}

    root_id = loaded.state_declaration_root_by_id[record_id]
    tips = loaded.current_state_declaration_tips_by_root[root_id]
    successors = loaded.state_declaration_successor_ids[record_id]
    withdrawals = loaded.state_declaration_withdrawn_by[record_id]
    subject = _state_declaration_payload(
        material, loaded, record.state_anchor_id, record.context,
        record_indices=indices)
    return {
        **base,
        "record_index": indices[record_id],
        "activity": (
            "superseded" if successors else
            "withdrawn" if withdrawals else
            "current"),
        "containing_lineage_health": (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else
            "healthy"),
        "containing_subject_conclusion": subject["conclusion"],
        "containing_agreement_findings": subject["agreement_findings"],
        "root_record_index": indices[root_id],
        "successor_indices": tuple(indices[item]
                                   for item in sorted(successors)),
        "withdrawal_indices": tuple(indices[item]
                                    for item in sorted(withdrawals)),
    }


class StateConditionReferenceResult(_StateResult):
    _material: ModelQueryMaterial = PrivateAttr()
    condition_index: _StateIndex
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    constraint_registration_index: _StateIndex
    pinned_declaration_index: _StateIndex
    target_variable_registration_index: _StateIndex
    target_owner_registration_index: _StateIndex

    @property
    def constraint_registration(self):
        return self._material.record_at(self.constraint_registration_index)

    @property
    def pinned_declaration(self):
        return self._material.record_at(self.pinned_declaration_index)

    @property
    def target_variable_registration(self):
        return self._material.record_at(
            self.target_variable_registration_index)

    @property
    def target_owner_registration(self):
        return self._material.record_at(self.target_owner_registration_index)


class StateEffectiveBodyGroupResult(_StateResult):
    _material: ModelQueryMaterial = PrivateAttr()
    group_index: _StateIndex
    representative_declaration_index: _StateIndex
    current_tip_indices: tuple[_StateIndex, ...]
    root_record_indices: tuple[_StateIndex, ...]
    conditions: tuple[StateConditionReferenceResult, ...]

    @field_validator("conditions", mode="before")
    @classmethod
    def _conditions_before(cls, value):
        return _rebuild_rows(
            value, StateConditionReferenceResult, "conditions")

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


class StateDeclarationRootResult(_StateResult):
    _material: ModelQueryMaterial = PrivateAttr()
    root_record_index: _StateIndex
    lineage_record_indices: tuple[_StateIndex, ...]
    current_tip_indices: tuple[_StateIndex, ...]
    withdrawal_indices: tuple[_StateIndex, ...]
    lineage_health: ContainingLineageHealth
    effective_body_group_indices: tuple[_StateIndex, ...]

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


def _bind_declaration_rows(roots, groups,
                           material: ModelQueryMaterial) -> None:
    for root in roots:
        object.__setattr__(root, "_material", material)
    for group in groups:
        object.__setattr__(group, "_material", material)
        for condition in group.conditions:
            object.__setattr__(condition, "_material", material)


class StateLookupResult(_StateResult):
    material: ModelQueryMaterial
    state_anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    status: StateLookupStatus
    registration_index: _StateIndex | None = None
    subject_entity_registration_index: _StateIndex | None = None
    condition_constraint_registration_indices: tuple[_StateIndex, ...] = ()
    condition_variable_registration_indices: tuple[_StateIndex, ...] = ()
    condition_owner_registration_indices: tuple[_StateIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _state_lookup_payload(
            self.material, self.material.loaded(), self.state_anchor_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("state lookup disclosure is forged")
        return self

    @property
    def registration(self):
        return (None if self.registration_index is None else
                self.material.record_at(self.registration_index))

    @property
    def subject_entity_registration(self):
        return (None if self.subject_entity_registration_index is None else
                self.material.record_at(
                    self.subject_entity_registration_index))


class StateDeclarationResult(_StateResult):
    material: ModelQueryMaterial
    state_anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    conclusion: StateDeclarationConclusion
    lineage_summary: StateDeclarationLineageSummary
    agreement_findings: tuple[StateAgreementFinding, ...] = ()
    registration_index: _StateIndex | None = None
    roots: tuple[StateDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[StateEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_StateIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, StateDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, StateEffectiveBodyGroupResult, "effective body groups")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _state_declaration_payload(
            self.material, self.material.loaded(), self.state_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("state declaration disclosure is forged")
        _bind_declaration_rows(
            self.roots, self.effective_body_groups, self.material)
        return self


class EntityStateEntry(_StateResult):
    _material: ModelQueryMaterial = PrivateAttr()
    entry_index: _StateIndex
    state_anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    state_registration_index: _StateIndex
    conclusion: StateDeclarationConclusion
    lineage_summary: StateDeclarationLineageSummary
    agreement_findings: tuple[StateAgreementFinding, ...] = ()
    roots: tuple[StateDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[StateEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_StateIndex, ...] = ()

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, StateDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, StateEffectiveBodyGroupResult, "effective body groups")

    @property
    def state_registration(self):
        return self._material.record_at(self.state_registration_index)


class EntityStatesResult(_StateResult):
    material: ModelQueryMaterial
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: EntityStatesStatus
    entity_registration_index: _StateIndex | None = None
    entries: tuple[EntityStateEntry, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("entries", mode="before")
    @classmethod
    def _entries_before(cls, value):
        return _rebuild_rows(value, EntityStateEntry, "entries")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _entity_states_payload(
            self.material, self.material.loaded(), self.entity_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("entity states disclosure is forged")
        for entry in self.entries:
            object.__setattr__(entry, "_material", self.material)
            _bind_declaration_rows(
                entry.roots, entry.effective_body_groups, self.material)
        return self


class StateAssertionDisclosureResult(_StateResult):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:srg|std|stw)_[0-9a-f]{64}$")
    lookup_status: StateAssertionLookupStatus
    record_index: _StateIndex | None = None
    activity: AssertionActivity | None = None
    containing_lineage_health: ContainingLineageHealth | None = None
    containing_subject_conclusion: StateDeclarationConclusion | None = None
    containing_agreement_findings: tuple[StateAgreementFinding, ...] | None = None
    root_record_index: _StateIndex | None = None
    successor_indices: tuple[_StateIndex, ...] = ()
    withdrawal_indices: tuple[_StateIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _state_assertion_payload(
            self.material, self.material.loaded(), self.record_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("state assertion disclosure is forged")
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
