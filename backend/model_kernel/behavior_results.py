"""BH-001 read-only kernel result contracts and authoritative derivation.

Complete model authority is carried once in :class:`ModelQueryMaterial`.
Nested rows contain strict indices only.  The private payload helpers are used
both by ``ModelQueries`` and by outer result validators so lifecycle and
corroboration truth has one deterministic implementation without validator
recursion.
"""

from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, StrictInt, field_validator,
    model_validator,
)

from backend.model_kernel.canonical import _behavior_effective_body_bytes
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.port_results import (
    AssertionActivity, ContainingLineageHealth, ModelQueryMaterial,
)
from backend.system_identity import (
    BEHAVIOR_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN,
)


BehaviorLookupStatus = Literal["not_registered", "registered"]
BehaviorDeclarationConclusion = Literal[
    "not_registered", "not_declared", "declared", "conflicted", "inactive",
]
BehaviorRuleLineageSummary = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
BehaviorAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]
VariableBehaviorsStatus = Literal["variable_not_registered", "registered"]
BehaviorAssertionLookupStatus = Literal["not_found", "found"]

_BehaviorIndex = Annotated[StrictInt, Field(ge=0)]


class _BehaviorResult(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


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


def _behavior_lookup_payload(material: ModelQueryMaterial, loaded,
                             behavior_anchor_id: str, *,
                             record_indices=None) -> dict:
    indices = (_indices(material) if record_indices is None
               else record_indices)
    registration = loaded.behavior_registrations_by_anchor.get(
        behavior_anchor_id)
    if registration is None:
        return {
            "behavior_anchor_id": behavior_anchor_id,
            "status": "not_registered",
            "registration_index": None,
            "participant_variable_registration_indices": (),
            "participant_owner_registration_indices": (),
        }
    variable_indices = []
    owner_indices = []
    for variable_id in registration.participant_variable_anchor_ids:
        variable = loaded.variable_registrations_by_anchor[variable_id]
        owner = loaded.registrations_by_anchor[
            variable.anchor.entity_anchor_id]
        variable_indices.append(indices[variable.record_id])
        owner_indices.append(indices[owner.record_id])
    return {
        "behavior_anchor_id": behavior_anchor_id,
        "status": "registered",
        "registration_index": indices[registration.record_id],
        "participant_variable_registration_indices": tuple(variable_indices),
        "participant_owner_registration_indices": tuple(owner_indices),
    }


def _behavior_rule_payload(material: ModelQueryMaterial, loaded,
                           behavior_anchor_id: str,
                           context: AssertionContext, *,
                           record_indices=None) -> dict:
    indices = (_indices(material) if record_indices is None
               else record_indices)
    registration = loaded.behavior_registrations_by_anchor.get(
        behavior_anchor_id)
    base = {
        "behavior_anchor_id": behavior_anchor_id,
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

    declaration_ids = loaded.behavior_rule_ids_by_key.get(
        (behavior_anchor_id, context), ())
    root_ids = tuple(sorted({
        loaded.behavior_rule_root_by_id[record_id]
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
            loaded.behavior_rule_root_by_id[record_id]].append(record_id)

    root_work = []
    body_by_tip: dict[str, bytes] = {}
    root_by_tip: dict[str, str] = {}
    for root_id in root_ids:
        lineage_ids = tuple(sorted(lineage_ids_by_root[root_id]))
        tips = tuple(sorted(
            loaded.current_behavior_rule_tips_by_root[root_id],
            key=lambda record: record.record_id))
        tip_ids = tuple(record.record_id for record in tips)
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in loaded.behavior_rule_withdrawn_by[record_id]))
        health = (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else
            "healthy")
        for tip in tips:
            body_by_tip[tip.record_id] = _behavior_effective_body_bytes(tip)
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
        root_record_ids = tuple(sorted({root_by_tip[tip_id]
                                        for tip_id in tip_ids}))
        group_payloads.append({
            "group_index": body_to_group_index[body],
            "representative_declaration_index": indices[min(tip_ids)],
            "current_tip_indices": tuple(indices[tip_id]
                                         for tip_id in tip_ids),
            "root_record_indices": tuple(indices[root_id]
                                         for root_id in root_record_ids),
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
    if any(len(root_ids_for_body) >= 2
           for root_ids_for_body in healthy_roots_by_body.values()):
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


def _variable_behaviors_payload(material: ModelQueryMaterial, loaded,
                                variable_anchor_id: str,
                                context: AssertionContext) -> dict:
    indices = _indices(material)
    variable = loaded.variable_registrations_by_anchor.get(variable_anchor_id)
    base = {
        "variable_anchor_id": variable_anchor_id,
        "context": context.model_dump(mode="python"),
    }
    if variable is None:
        return {
            **base,
            "status": "variable_not_registered",
            "variable_registration_index": None,
            "owner_registration_index": None,
            "entries": (),
        }
    entries = []
    for entry_index, behavior_anchor_id in enumerate(sorted(
            loaded.behavior_anchor_ids_by_variable.get(variable_anchor_id, ()))):
        registration = loaded.behavior_registrations_by_anchor[
            behavior_anchor_id]
        other_variable_id = next(
            participant for participant
            in registration.participant_variable_anchor_ids
            if participant != variable_anchor_id)
        other_variable = loaded.variable_registrations_by_anchor[
            other_variable_id]
        other_owner = loaded.registrations_by_anchor[
            other_variable.anchor.entity_anchor_id]
        declaration = _behavior_rule_payload(
            material, loaded, behavior_anchor_id, context,
            record_indices=indices)
        entries.append({
            "entry_index": entry_index,
            "behavior_anchor_id": behavior_anchor_id,
            "other_variable_anchor_id": other_variable_id,
            "behavior_registration_index": indices[registration.record_id],
            "other_variable_registration_index": indices[
                other_variable.record_id],
            "other_owner_registration_index": indices[other_owner.record_id],
            "conclusion": declaration["conclusion"],
            "lineage_summary": declaration["lineage_summary"],
            "agreement_findings": declaration["agreement_findings"],
            "roots": declaration["roots"],
            "effective_body_groups": declaration["effective_body_groups"],
            "current_declaration_indices": declaration[
                "current_declaration_indices"],
        })
    owner = loaded.registrations_by_anchor[variable.anchor.entity_anchor_id]
    return {
        **base,
        "status": "registered",
        "variable_registration_index": indices[variable.record_id],
        "owner_registration_index": indices[owner.record_id],
        "entries": tuple(entries),
    }


def _behavior_assertion_payload(material: ModelQueryMaterial, loaded,
                                record_id: str) -> dict:
    indices = _indices(material)
    record = loaded.records.get(record_id)
    found = record is not None and record.record_kind in {
        "behavior_registration", "behavior_rule_declaration",
        "behavior_rule_withdrawal",
    }
    base = {"record_id": record_id, "lookup_status": (
        "found" if found else "not_found")}
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
    if record.record_kind != "behavior_rule_declaration":
        return {**base, "record_index": indices[record_id], **empty}

    root_id = loaded.behavior_rule_root_by_id[record_id]
    tips = loaded.current_behavior_rule_tips_by_root[root_id]
    successors = loaded.behavior_rule_superseded_by[record_id]
    withdrawals = loaded.behavior_rule_withdrawn_by[record_id]
    subject = _behavior_rule_payload(
        material, loaded, record.behavior_anchor_id, record.context,
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


class BehaviorEffectiveBodyGroupResult(_BehaviorResult):
    _material: ModelQueryMaterial = PrivateAttr()
    group_index: _BehaviorIndex
    representative_declaration_index: _BehaviorIndex
    current_tip_indices: tuple[_BehaviorIndex, ...]
    root_record_indices: tuple[_BehaviorIndex, ...]

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


class BehaviorRuleRootResult(_BehaviorResult):
    _material: ModelQueryMaterial = PrivateAttr()
    root_record_index: _BehaviorIndex
    lineage_record_indices: tuple[_BehaviorIndex, ...]
    current_tip_indices: tuple[_BehaviorIndex, ...]
    withdrawal_indices: tuple[_BehaviorIndex, ...]
    lineage_health: ContainingLineageHealth
    effective_body_group_indices: tuple[_BehaviorIndex, ...]

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


def _bind_rule_rows(roots, groups, material: ModelQueryMaterial) -> None:
    for row in (*roots, *groups):
        object.__setattr__(row, "_material", material)


class BehaviorLookupResult(_BehaviorResult):
    material: ModelQueryMaterial
    behavior_anchor_id: str = Field(pattern=BEHAVIOR_ANCHOR_ID_PATTERN)
    status: BehaviorLookupStatus
    registration_index: _BehaviorIndex | None = None
    participant_variable_registration_indices: tuple[_BehaviorIndex, ...] = ()
    participant_owner_registration_indices: tuple[_BehaviorIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _behavior_lookup_payload(
            self.material, self.material.loaded(), self.behavior_anchor_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("behavior lookup disclosure is forged")
        return self


class BehaviorRuleResult(_BehaviorResult):
    material: ModelQueryMaterial
    behavior_anchor_id: str = Field(pattern=BEHAVIOR_ANCHOR_ID_PATTERN)
    context: AssertionContext
    conclusion: BehaviorDeclarationConclusion
    lineage_summary: BehaviorRuleLineageSummary
    agreement_findings: tuple[BehaviorAgreementFinding, ...] = ()
    registration_index: _BehaviorIndex | None = None
    roots: tuple[BehaviorRuleRootResult, ...] = ()
    effective_body_groups: tuple[BehaviorEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_BehaviorIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, BehaviorRuleRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, BehaviorEffectiveBodyGroupResult,
            "effective body groups")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _behavior_rule_payload(
            self.material, self.material.loaded(), self.behavior_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("behavior declaration disclosure is forged")
        _bind_rule_rows(self.roots, self.effective_body_groups, self.material)
        return self


class VariableBehaviorEntry(_BehaviorResult):
    _material: ModelQueryMaterial = PrivateAttr()
    entry_index: _BehaviorIndex
    behavior_anchor_id: str = Field(pattern=BEHAVIOR_ANCHOR_ID_PATTERN)
    other_variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    behavior_registration_index: _BehaviorIndex
    other_variable_registration_index: _BehaviorIndex
    other_owner_registration_index: _BehaviorIndex
    conclusion: BehaviorDeclarationConclusion
    lineage_summary: BehaviorRuleLineageSummary
    agreement_findings: tuple[BehaviorAgreementFinding, ...] = ()
    roots: tuple[BehaviorRuleRootResult, ...] = ()
    effective_body_groups: tuple[BehaviorEffectiveBodyGroupResult, ...] = ()
    current_declaration_indices: tuple[_BehaviorIndex, ...] = ()

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, BehaviorRuleRootResult, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, BehaviorEffectiveBodyGroupResult,
            "effective body groups")

    @property
    def behavior_registration(self):
        return self._material.record_at(self.behavior_registration_index)

    @property
    def other_variable_registration(self):
        return self._material.record_at(self.other_variable_registration_index)

    @property
    def other_owner_registration(self):
        return self._material.record_at(self.other_owner_registration_index)


class VariableBehaviorsResult(_BehaviorResult):
    material: ModelQueryMaterial
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    status: VariableBehaviorsStatus
    variable_registration_index: _BehaviorIndex | None = None
    owner_registration_index: _BehaviorIndex | None = None
    entries: tuple[VariableBehaviorEntry, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)
    _context_before = field_validator("context", mode="before")(
        _rebuild_context)

    @field_validator("entries", mode="before")
    @classmethod
    def _entries_before(cls, value):
        return _rebuild_rows(value, VariableBehaviorEntry, "entries")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _variable_behaviors_payload(
            self.material, self.material.loaded(), self.variable_anchor_id,
            self.context)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("variable behaviors disclosure is forged")
        for entry in self.entries:
            object.__setattr__(entry, "_material", self.material)
            _bind_rule_rows(
                entry.roots, entry.effective_body_groups, self.material)
        return self


class BehaviorAssertionDisclosureResult(_BehaviorResult):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:brg|bhd|bhw)_[0-9a-f]{64}$")
    lookup_status: BehaviorAssertionLookupStatus
    record_index: _BehaviorIndex | None = None
    activity: AssertionActivity | None = None
    containing_lineage_health: ContainingLineageHealth | None = None
    containing_subject_conclusion: BehaviorDeclarationConclusion | None = None
    containing_agreement_findings: tuple[BehaviorAgreementFinding, ...] | None = None
    root_record_index: _BehaviorIndex | None = None
    successor_indices: tuple[_BehaviorIndex, ...] = ()
    withdrawal_indices: tuple[_BehaviorIndex, ...] = ()

    _material_before = field_validator("material", mode="before")(
        _rebuild_material)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _behavior_assertion_payload(
            self.material, self.material.loaded(), self.record_id)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("behavior assertion disclosure is forged")
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
