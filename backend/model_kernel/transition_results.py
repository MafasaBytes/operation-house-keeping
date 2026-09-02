"""ST-002 read-only transition declaration result contracts.

Complete model authority is carried once in :class:`ModelQueryMaterial`.
Nested rows contain strict indices only. Transition endpoint disclosure reuses
the accepted state payload derivations; it does not evaluate observations,
classifications, transition assessment, or occurrence.
"""

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, StrictInt, field_validator,
    model_validator, TypeAdapter,
)

from backend.model_kernel.canonical import _transition_effective_body_bytes
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.port_results import (
    AssertionActivity, ContainingLineageHealth, ModelQueryMaterial,
)
from backend.model_kernel.state_results import (
    StateDeclarationConclusion,
    _state_assertion_payload,
    _state_declaration_payload,
)
from backend.system_identity import (
    ENTITY_ANCHOR_ID_PATTERN, STATE_ANCHOR_ID_PATTERN,
    TRANSITION_ANCHOR_ID_PATTERN,
)


TransitionLookupStatus = Literal["not_registered", "registered"]
TransitionDeclarationConclusion = Literal[
    "not_registered", "not_declared", "declared", "conflicted", "inactive",
]
TransitionDeclarationLineageSummary = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
TransitionAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]
TransitionEndpointRole = Literal["from", "to"]
TransitionEndpointPinAlignment = Literal[
    "exact_current",
    "pinned_declaration_superseded",
    "pinned_declaration_withdrawn",
    "endpoint_state_conflicted",
    "endpoint_state_inactive",
]
EntityTransitionsStatus = Literal["entity_not_registered", "registered"]
TransitionAssertionLookupStatus = Literal["not_found", "found"]

_TransitionIndex = Annotated[StrictInt, Field(ge=0)]
_MAX_RESULT_GRAPH_DEPTH = 128
_MAX_RESULT_GRAPH_NODES = 100_000
_CONTEXT_ADAPTER = TypeAdapter(AssertionContext)


def _field(container, name, missing):
    if isinstance(container, BaseModel):
        return vars(container).get(name, missing)
    if isinstance(container, Mapping):
        return container.get(name, missing)
    return missing


def _graph_children(item, outer_material):
    if isinstance(item, BaseModel):
        fields = type(item).model_fields
        stored = vars(item)
        extras = getattr(item, "__pydantic_extra__", None)
        if set(stored).difference(fields) or extras:
            raise ValueError("pydantic result instance contains extra fields")
        private = getattr(item, "__pydantic_private__", None) or {}
        permitted_private = (
            {"_material"}
            if "_material" in getattr(type(item),
                                      "__private_attributes__", {})
            else set())
        if set(private).difference(permitted_private):
            raise ValueError("pydantic result instance contains private cache")
        if "_material" in private:
            bound_material = private["_material"]
            if (not isinstance(outer_material, ModelQueryMaterial)
                    or bound_material is not outer_material):
                raise ValueError(
                    "nested result is bound to another material snapshot")
        return tuple(stored[name] for name in fields if name in stored)
    if isinstance(item, Mapping):
        return tuple(item.keys()) + tuple(item.values())
    if isinstance(item, (tuple, list, set, frozenset)):
        return tuple(item)
    return None


def _inspect_supplied_graph(value) -> None:
    """Reject hidden extras, cycles, excessive depth, and coercive counts.

    The traversal is iterative so a hostile caller cannot make validation rely
    on Python recursion. Shared acyclic objects are allowed, but no supplied
    private/cached value is trusted or copied into the reconstructed result.
    """
    missing = object()
    material = _field(value, "material", missing)
    revision = _field(material, "revision", missing)
    record_count = _field(revision, "record_count", missing)
    if record_count is not missing and type(record_count) is not int:
        raise ValueError("material revision record_count must be strict int")

    stack = [(False, value, 0)]
    active: set[int] = set()
    complete: set[int] = set()
    visited = 0
    while stack:
        exiting, item, depth = stack.pop()
        children = _graph_children(item, material)
        if children is None:
            continue
        identity = id(item)
        if exiting:
            active.remove(identity)
            complete.add(identity)
            continue
        if identity in active:
            raise ValueError("result object graph contains a cycle")
        if identity in complete:
            continue
        if depth > _MAX_RESULT_GRAPH_DEPTH:
            raise ValueError("result object graph exceeds maximum depth")
        visited += 1
        if visited > _MAX_RESULT_GRAPH_NODES:
            raise ValueError("result object graph exceeds maximum size")
        active.add(identity)
        stack.append((True, item, depth))
        stack.extend((False, child, depth + 1)
                     for child in reversed(children))


class _TransitionResult(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="wrap")
    @classmethod
    def _reject_hostile_supplied_graph(cls, value, handler):
        # A wrap validator sees caller-owned model instances before Pydantic
        # normalizes them to field dictionaries. This closes private/cache
        # laundering while keeping rejection inside the typed validation path.
        _inspect_supplied_graph(value)
        return handler(value)


def _dump_nested(value):
    return (value.model_dump(mode="python")
            if isinstance(value, BaseModel) else value)


def _rebuild_material(value) -> ModelQueryMaterial:
    return ModelQueryMaterial.model_validate(_dump_nested(value))


def _rebuild_context(value) -> AssertionContext:
    return _CONTEXT_ADAPTER.validate_python(_dump_nested(value))


def _rebuild_rows(value, contract, label: str):
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{label} must be a tuple of result rows")
    return tuple(contract.model_validate(_dump_nested(row)) for row in value)


def _rebuild_row(value, contract):
    return contract.model_validate(_dump_nested(value))


def _indices(material: ModelQueryMaterial) -> dict[str, int]:
    return {record_id: index for index, record_id
            in enumerate(material.revision.record_ids)}


def _transition_lookup_payload(material: ModelQueryMaterial, loaded,
                               transition_anchor_id: str, *,
                               record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.transition_registrations_by_anchor.get(
        transition_anchor_id)
    if registration is None:
        return {
            "transition_anchor_id": transition_anchor_id,
            "status": "not_registered",
            "registration_index": None,
            "subject_entity_registration_index": None,
            "from_state_registration_index": None,
            "to_state_registration_index": None,
        }
    subject = loaded.registrations_by_anchor[
        registration.subject_entity_anchor_id]
    from_state = loaded.state_registrations_by_anchor[
        registration.from_state_anchor_id]
    to_state = loaded.state_registrations_by_anchor[
        registration.to_state_anchor_id]
    return {
        "transition_anchor_id": transition_anchor_id,
        "status": "registered",
        "registration_index": indices[registration.record_id],
        "subject_entity_registration_index": indices[subject.record_id],
        "from_state_registration_index": indices[from_state.record_id],
        "to_state_registration_index": indices[to_state.record_id],
    }


def _endpoint_alignment(state_conclusion, pin_activity):
    if state_conclusion == "conflicted":
        if pin_activity in ("current", "superseded", "withdrawn"):
            return "endpoint_state_conflicted"
    elif state_conclusion == "inactive":
        if pin_activity in ("superseded", "withdrawn"):
            return "endpoint_state_inactive"
    elif state_conclusion == "declared":
        alignment = {
            "current": "exact_current",
            "superseded": "pinned_declaration_superseded",
            "withdrawn": "pinned_declaration_withdrawn",
        }.get(pin_activity)
        if alignment is not None:
            return alignment
    raise ValueError(
        "admitted active transition has unreachable endpoint state/activity")


def _endpoint_payload(material, loaded, declaration, role, indices) -> dict:
    pin = (declaration.from_endpoint if role == "from"
           else declaration.to_endpoint)
    state = _state_declaration_payload(
        material, loaded, pin.state_anchor_id, declaration.context,
        record_indices=indices)
    assertion = _state_assertion_payload(
        material, loaded, pin.declaration_record_id)
    expected_index = indices[pin.declaration_record_id]
    if (assertion["lookup_status"] != "found"
            or assertion["record_index"] != expected_index
            or assertion["activity"] is None
            or assertion["containing_subject_conclusion"]
            != state["conclusion"]):
        raise ValueError("admitted transition endpoint ST derivation disagrees")
    activity = assertion["activity"]
    return {
        "role": role,
        "state_anchor_id": pin.state_anchor_id,
        "state_registration_index": state["registration_index"],
        "declaration_index": expected_index,
        "state_declaration_conclusion": state["conclusion"],
        "pinned_declaration_activity": activity,
        "alignment": _endpoint_alignment(state["conclusion"], activity),
    }


def _transition_declaration_payload(
        material: ModelQueryMaterial, loaded, transition_anchor_id: str,
        context: AssertionContext, *, record_indices=None) -> dict:
    indices = _indices(material) if record_indices is None else record_indices
    registration = loaded.transition_registrations_by_anchor.get(
        transition_anchor_id)
    base = {
        "transition_anchor_id": transition_anchor_id,
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

    declaration_ids = loaded.transition_declaration_ids_by_key.get(
        (transition_anchor_id, context), ())
    root_ids = tuple(sorted({
        loaded.transition_declaration_root_by_id[record_id]
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
            loaded.transition_declaration_root_by_id[record_id]].append(
                record_id)

    root_work = []
    body_by_tip: dict[str, bytes] = {}
    root_by_tip: dict[str, str] = {}
    for root_id in root_ids:
        lineage_ids = tuple(sorted(lineage_ids_by_root[root_id]))
        tips = tuple(sorted(
            loaded.current_transition_declaration_tips_by_root[root_id],
            key=lambda record: record.record_id))
        tip_ids = tuple(record.record_id for record in tips)
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in loaded.transition_declaration_withdrawn_by[
                record_id]))
        health = (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else
            "healthy")
        for tip in tips:
            body_by_tip[tip.record_id] = _transition_effective_body_bytes(tip)
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
        representative = loaded.transition_declarations[representative_id]
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
            "from_endpoint": _endpoint_payload(
                material, loaded, representative, "from", indices),
            "to_endpoint": _endpoint_payload(
                material, loaded, representative, "to", indices),
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


def _entity_transitions_payload(material: ModelQueryMaterial, loaded,
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
    for transition_anchor_id in \
            loaded.transition_anchor_ids_by_subject_entity.get(
                entity_anchor_id, ()):
        registration = loaded.transition_registrations_by_anchor[
            transition_anchor_id]
        declaration = _transition_declaration_payload(
            material, loaded, transition_anchor_id, context,
            record_indices=indices)
        first_root_id = (
            material.revision.record_ids[
                declaration["roots"][0]["root_record_index"]]
            if declaration["roots"] else "")
        pending.append((transition_anchor_id, first_root_id, {
            "transition_anchor_id": transition_anchor_id,
            "transition_registration_index": indices[registration.record_id],
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


def _transition_assertion_payload(material: ModelQueryMaterial, loaded,
                                  record_id: str) -> dict:
    indices = _indices(material)
    record = loaded.records.get(record_id)
    found = record is not None and record.record_kind in {
        "transition_registration", "transition_declaration",
        "transition_declaration_withdrawal",
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
    if record.record_kind != "transition_declaration":
        return {**base, "record_index": indices[record_id], **empty}

    root_id = loaded.transition_declaration_root_by_id[record_id]
    tips = loaded.current_transition_declaration_tips_by_root[root_id]
    successors = loaded.transition_declaration_successor_ids[record_id]
    withdrawals = loaded.transition_declaration_withdrawn_by[record_id]
    subject = _transition_declaration_payload(
        material, loaded, record.transition_anchor_id, record.context,
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


class TransitionEndpointResult(_TransitionResult):
    _material: ModelQueryMaterial = PrivateAttr()
    role: TransitionEndpointRole
    state_anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    state_registration_index: _TransitionIndex
    declaration_index: _TransitionIndex
    state_declaration_conclusion: StateDeclarationConclusion
    pinned_declaration_activity: AssertionActivity
    alignment: TransitionEndpointPinAlignment

    @property
    def state_registration(self):
        return self._material.record_at(self.state_registration_index)

    @property
    def declaration(self):
        return self._material.record_at(self.declaration_index)


class TransitionEffectiveBodyGroupResult(_TransitionResult):
    _material: ModelQueryMaterial = PrivateAttr()
    group_index: _TransitionIndex
    representative_declaration_index: _TransitionIndex
    current_tip_indices: tuple[_TransitionIndex, ...]
    root_record_indices: tuple[_TransitionIndex, ...]
    from_endpoint: TransitionEndpointResult
    to_endpoint: TransitionEndpointResult

    _from_before = field_validator("from_endpoint", mode="before")(
        lambda value: _rebuild_row(value, TransitionEndpointResult))
    _to_before = field_validator("to_endpoint", mode="before")(
        lambda value: _rebuild_row(value, TransitionEndpointResult))

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


class TransitionDeclarationRootResult(_TransitionResult):
    _material: ModelQueryMaterial = PrivateAttr()
    root_record_index: _TransitionIndex
    lineage_record_indices: tuple[_TransitionIndex, ...]
    current_tip_indices: tuple[_TransitionIndex, ...]
    withdrawal_indices: tuple[_TransitionIndex, ...]
    lineage_health: ContainingLineageHealth
    effective_body_group_indices: tuple[_TransitionIndex, ...]

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
        root._material = material
    for group in groups:
        group._material = material
        group.from_endpoint._material = material
        group.to_endpoint._material = material


class TransitionLookupResult(_TransitionResult):
    material: ModelQueryMaterial
    transition_anchor_id: str = Field(pattern=TRANSITION_ANCHOR_ID_PATTERN)
    status: TransitionLookupStatus
    registration_index: _TransitionIndex | None = None
    subject_entity_registration_index: _TransitionIndex | None = None
    from_state_registration_index: _TransitionIndex | None = None
    to_state_registration_index: _TransitionIndex | None = None

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _transition_lookup_payload(
            self.material, self.material.loaded(), self.transition_anchor_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("transition lookup disclosure is forged")
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

    @property
    def from_state_registration(self):
        return (None if self.from_state_registration_index is None else
                self.material.record_at(self.from_state_registration_index))

    @property
    def to_state_registration(self):
        return (None if self.to_state_registration_index is None else
                self.material.record_at(self.to_state_registration_index))


class TransitionDeclarationResult(_TransitionResult):
    material: ModelQueryMaterial
    transition_anchor_id: str = Field(pattern=TRANSITION_ANCHOR_ID_PATTERN)
    context: AssertionContext
    conclusion: TransitionDeclarationConclusion
    lineage_summary: TransitionDeclarationLineageSummary
    agreement_findings: tuple[TransitionAgreementFinding, ...] = ()
    registration_index: _TransitionIndex | None = None
    roots: tuple[TransitionDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[TransitionEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_TransitionIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(
            value, TransitionDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, TransitionEffectiveBodyGroupResult,
            "effective body groups")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _transition_declaration_payload(
            self.material, self.material.loaded(), self.transition_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("transition declaration disclosure is forged")
        _bind_declaration_rows(
            self.roots, self.effective_body_groups, self.material)
        return self


class EntityTransitionEntry(_TransitionResult):
    _material: ModelQueryMaterial = PrivateAttr()
    entry_index: _TransitionIndex
    transition_anchor_id: str = Field(pattern=TRANSITION_ANCHOR_ID_PATTERN)
    transition_registration_index: _TransitionIndex
    conclusion: TransitionDeclarationConclusion
    lineage_summary: TransitionDeclarationLineageSummary
    agreement_findings: tuple[TransitionAgreementFinding, ...] = ()
    roots: tuple[TransitionDeclarationRootResult, ...] = ()
    effective_body_groups: tuple[TransitionEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_TransitionIndex, ...] = ()

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(
            value, TransitionDeclarationRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, TransitionEffectiveBodyGroupResult,
            "effective body groups")

    @property
    def transition_registration(self):
        return self._material.record_at(
            self.transition_registration_index)


class EntityTransitionsResult(_TransitionResult):
    material: ModelQueryMaterial
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: EntityTransitionsStatus
    entity_registration_index: _TransitionIndex | None = None
    entries: tuple[EntityTransitionEntry, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("entries", mode="before")
    @classmethod
    def _entries_before(cls, value):
        return _rebuild_rows(value, EntityTransitionEntry, "entries")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _entity_transitions_payload(
            self.material, self.material.loaded(), self.entity_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("entity transitions disclosure is forged")
        for entry in self.entries:
            entry._material = self.material
            _bind_declaration_rows(
                entry.roots, entry.effective_body_groups, self.material)
        return self

    @property
    def entity_registration(self):
        return (None if self.entity_registration_index is None else
                self.material.record_at(self.entity_registration_index))


class TransitionAssertionDisclosureResult(_TransitionResult):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:trg|trd|trw)_[0-9a-f]{64}$")
    lookup_status: TransitionAssertionLookupStatus
    record_index: _TransitionIndex | None = None
    activity: AssertionActivity | None = None
    containing_lineage_health: ContainingLineageHealth | None = None
    containing_subject_conclusion: TransitionDeclarationConclusion | None = None
    containing_agreement_findings: tuple[
        TransitionAgreementFinding, ...] | None = None
    root_record_index: _TransitionIndex | None = None
    successor_indices: tuple[_TransitionIndex, ...] = ()
    withdrawal_indices: tuple[_TransitionIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _transition_assertion_payload(
            self.material, self.material.loaded(), self.record_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("transition assertion disclosure is forged")
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
