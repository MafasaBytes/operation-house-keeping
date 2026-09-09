"""FM-001 read-only explicit flow-to-measurement association results.

Each outer result carries one complete :class:`ModelQueryMaterial`. Nested
rows carry indices and derived disclosure only.  The derivation makes no
claim about observation, occurrence, freshness, physical flow, correctness,
or safety.
"""

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, StrictInt, field_validator,
    model_validator,
)

from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.flow_results import FlowPortRole
from backend.model_kernel.port_results import (
    AssertionActivity, ContainingLineageHealth, ModelQueryMaterial,
)
from backend.model_kernel.result_revalidation import (
    inspect_supplied_graph as _inspect_supplied_graph,
    material_indices as _indices,
    rebuild_context as _rebuild_context,
    rebuild_material as _rebuild_material,
    rebuild_rows as _rebuild_rows,
)
from backend.system_identity import (
    FLOW_ANCHOR_ID_PATTERN, PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
)


FlowMeasurementEndpointRegistration = Literal[
    "all_registered", "flow_not_registered", "variable_not_registered",
    "port_not_registered", "multiple_not_registered",
]
FlowMeasurementReverseRegistration = Literal[
    "not_registered", "registered",
]
FlowMeasurementDeclarationPresence = Literal["not_declared", "declared"]
FlowMeasurementDeclarationConclusion = Literal[
    "not_evaluated", "declared_direct_measurement_relevance", "conflicted",
    "inactive",
]
FlowMeasurementSupportKind = Literal["frg", "vrg", "prg", "fld", "vpa", "vsm"]
FlowMeasurementSupportActivity = Literal[
    "permanent", "current", "superseded", "withdrawn",
]
FlowMeasurementSupportLineageHealth = Literal[
    "not_applicable", "healthy", "conflicted", "inactive",
]
FlowMeasurementSupportAlignment = Literal["exact", "unaligned"]
FlowMeasurementOrientation = Literal[
    "aligned", "opposite", "unsigned_magnitude", "not_applicable",
]
FlowMeasurementAgreementFinding = Literal[
    "one_healthy_root", "corroborating_healthy_roots",
    "same_root_conflict", "inactive_roots_present",
    "cross_root_effective_body_disagreement",
]
FlowMeasurementAssertionLookupStatus = Literal["not_found", "found"]

_Index = Annotated[StrictInt, Field(ge=0)]
_ORIENTATION_RANK = {
    "aligned": 0,
    "opposite": 1,
    "unsigned_magnitude": 2,
    "not_applicable": 3,
}
_SUPPORT_KINDS = ("frg", "vrg", "prg", "fld", "vpa", "vsm")


def _strictly_increasing(values, label: str, *, allow_empty: bool = True) -> None:
    if not allow_empty and not values:
        raise ValueError(f"{label} must not be empty")
    if tuple(values) != tuple(sorted(set(values))):
        raise ValueError(f"{label} must be unique and strictly increasing")


def _reject_scalar_subclasses(value) -> None:
    """Reject coercive caller scalars before Pydantic or derived access."""
    stack = [value]
    seen = set()
    while stack:
        item = stack.pop()
        if isinstance(item, str) and type(item) is not str:
            raise ValueError("result strings must be exact built-in strings")
        if isinstance(item, bool) and type(item) is not bool:
            raise ValueError("result booleans must be exact built-in booleans")
        if (isinstance(item, int) and not isinstance(item, bool)
                and type(item) is not int):
            raise ValueError("result integers must be exact built-in integers")
        if isinstance(item, float) and type(item) is not float:
            raise ValueError("result floats must be exact built-in floats")
        if isinstance(item, BaseModel):
            nested = tuple(vars(item).values())
        elif isinstance(item, Mapping):
            nested = tuple(item.keys()) + tuple(item.values())
        elif isinstance(item, (tuple, list, set, frozenset)):
            nested = tuple(item)
        else:
            continue
        identity = id(item)
        if identity in seen:
            continue
        seen.add(identity)
        stack.extend(nested)


class _FlowMeasurementResult(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="wrap")
    @classmethod
    def _reject_hostile_supplied_graph(cls, value, handler):
        _inspect_supplied_graph(value)
        _reject_scalar_subclasses(value)
        return handler(value)


class FlowMeasurementSupportRow(_FlowMeasurementResult):
    support_kind: FlowMeasurementSupportKind
    record_index: _Index
    activity: FlowMeasurementSupportActivity
    containing_lineage_health: FlowMeasurementSupportLineageHealth
    current_alignment: FlowMeasurementSupportAlignment

    @model_validator(mode="after")
    def _reachable(self):
        values = (
            self.activity, self.containing_lineage_health,
            self.current_alignment,
        )
        if self.support_kind in {"frg", "vrg", "prg"}:
            if values != ("permanent", "not_applicable", "exact"):
                raise ValueError("registration support state is unreachable")
            return self
        if self.support_kind in {"fld", "vpa"}:
            if self.activity == "permanent" \
                    or self.containing_lineage_health == "not_applicable":
                raise ValueError("claim support state is unreachable")
            if self.activity == "current" and \
                    self.containing_lineage_health == "inactive":
                raise ValueError("current claim support cannot be inactive")
            expected = (
                "unaligned" if self.containing_lineage_health == "inactive"
                else "exact")
            if self.current_alignment != expected:
                raise ValueError("claim support alignment is unreachable")
            return self
        if (self.activity not in {"current", "superseded"}
                or self.containing_lineage_health not in {
                    "healthy", "conflicted"}):
            raise ValueError("semantic support state is unreachable")
        return self


class FlowMeasurementEffectiveBodyGroupRow(_FlowMeasurementResult):
    group_index: _Index
    representative_current_tip_index: _Index
    current_tip_indices: tuple[_Index, ...]
    participating_root_indices: tuple[_Index, ...]
    participant_role: FlowPortRole
    orientation: FlowMeasurementOrientation
    support_rows: tuple[FlowMeasurementSupportRow, ...]

    @field_validator("support_rows", mode="before")
    @classmethod
    def _support_before(cls, value):
        return _rebuild_rows(value, FlowMeasurementSupportRow, "support rows")

    @model_validator(mode="after")
    def _local_invariants(self):
        _strictly_increasing(
            self.current_tip_indices, "group current-tip indices",
            allow_empty=False)
        _strictly_increasing(
            self.participating_root_indices,
            "group participating-root indices", allow_empty=False)
        if self.representative_current_tip_index != min(
                self.current_tip_indices):
            raise ValueError(
                "group representative must be its lowest current tip")
        if tuple(row.support_kind for row in self.support_rows) != \
                _SUPPORT_KINDS:
            raise ValueError("group must carry the exact six support rows")
        if len({row.record_index for row in self.support_rows}) != 6:
            raise ValueError("group support record indices must be unique")
        return self


class FlowMeasurementRootRow(_FlowMeasurementResult):
    root_index: _Index
    root_record_index: _Index
    lineage_record_indices: tuple[_Index, ...]
    current_tip_indices: tuple[_Index, ...]
    withdrawal_indices: tuple[_Index, ...]
    lineage_health: ContainingLineageHealth
    effective_body_group_indices: tuple[_Index, ...]

    @model_validator(mode="after")
    def _local_invariants(self):
        _strictly_increasing(
            self.lineage_record_indices, "root lineage indices",
            allow_empty=False)
        _strictly_increasing(self.current_tip_indices, "root current-tip indices")
        _strictly_increasing(self.withdrawal_indices, "root withdrawal indices")
        _strictly_increasing(
            self.effective_body_group_indices, "root body-group indices")
        if self.root_record_index not in self.lineage_record_indices:
            raise ValueError("root record must belong to its lineage")
        if not set(self.current_tip_indices).issubset(
                self.lineage_record_indices):
            raise ValueError("root current tips must belong to its lineage")
        expected = (
            "inactive" if not self.current_tip_indices else
            "conflicted" if len(self.current_tip_indices) > 1 else
            "healthy")
        if self.lineage_health != expected:
            raise ValueError("root health disagrees with current-tip cardinality")
        if ((self.lineage_health == "inactive")
                != (not self.effective_body_group_indices)):
            raise ValueError("root body groups disagree with root activity")
        return self


class FlowMeasurementEntryRow(_FlowMeasurementResult):
    entry_index: _Index
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    participant_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    orientation: FlowMeasurementOrientation
    declaration_conclusion: FlowMeasurementDeclarationConclusion
    agreement_findings: tuple[FlowMeasurementAgreementFinding, ...]
    participant_role: FlowPortRole
    roots: tuple[FlowMeasurementRootRow, ...]
    effective_body_groups: tuple[FlowMeasurementEffectiveBodyGroupRow, ...]
    current_assertion_indices: tuple[_Index, ...]

    @field_validator("roots", mode="before")
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, FlowMeasurementRootRow, "roots")

    @field_validator("effective_body_groups", mode="before")
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, FlowMeasurementEffectiveBodyGroupRow,
            "effective body groups")

    @model_validator(mode="after")
    def _local_invariants(self):
        if tuple(row.root_index for row in self.roots) != tuple(
                range(len(self.roots))):
            raise ValueError("entry root indices must be contiguous")
        if tuple(row.group_index for row in self.effective_body_groups) != tuple(
                range(len(self.effective_body_groups))):
            raise ValueError("entry body-group indices must be contiguous")
        _strictly_increasing(
            self.current_assertion_indices, "entry current assertion indices")
        current = tuple(sorted(
            index for group in self.effective_body_groups
            for index in group.current_tip_indices))
        if current != self.current_assertion_indices:
            raise ValueError("entry current assertions disagree with body groups")
        for group in self.effective_body_groups:
            if (group.participant_role != self.participant_role
                    or group.orientation != self.orientation):
                raise ValueError("entry body group changes immutable subject")
            if any(index >= len(self.roots)
                   for index in group.participating_root_indices):
                raise ValueError("entry body group references an absent root")
        for root in self.roots:
            if any(index >= len(self.effective_body_groups)
                   for index in root.effective_body_group_indices):
                raise ValueError("entry root references an absent body group")
            reciprocal = tuple(
                group.group_index for group in self.effective_body_groups
                if root.root_index in group.participating_root_indices)
            if reciprocal != root.effective_body_group_indices:
                raise ValueError("entry root/body-group links are not reciprocal")
        healthy = tuple(root for root in self.roots
                        if root.lineage_health == "healthy")
        conflicted = tuple(root for root in self.roots
                           if root.lineage_health == "conflicted")
        inactive = tuple(root for root in self.roots
                         if root.lineage_health == "inactive")
        corroborating = any(
            len(tuple(index for index in group.participating_root_indices
                      if self.roots[index].lineage_health == "healthy")) >= 2
            for group in self.effective_body_groups)
        active_sets = tuple(
            frozenset(root.effective_body_group_indices)
            for root in self.roots if root.current_tip_indices)
        disagreement = len(set(active_sets)) > 1
        findings = []
        if len(healthy) == 1:
            findings.append("one_healthy_root")
        if corroborating:
            findings.append("corroborating_healthy_roots")
        if conflicted:
            findings.append("same_root_conflict")
        if inactive:
            findings.append("inactive_roots_present")
        if disagreement:
            findings.append("cross_root_effective_body_disagreement")
        if self.agreement_findings != tuple(findings):
            raise ValueError("entry agreement findings are stale")
        expected = (
            "conflicted" if conflicted or disagreement else
            "declared_direct_measurement_relevance" if healthy else
            "inactive")
        if not self.roots or self.declaration_conclusion != expected:
            raise ValueError("entry declaration conclusion is stale")
        return self


def _subject(record) -> tuple:
    return (
        record.flow_anchor_id,
        record.variable_anchor_id,
        record.participant_port_anchor_id,
        record.context,
        "direct_measurement_relevance",
        record.orientation,
    )


def _semantic_exact_measured_actual(record) -> bool:
    declaration = record.declaration
    return (
        declaration.dimension == "observation_role"
        and declaration.observation_role.system_id == "project_local"
        and declaration.observation_role.system_edition
        == "ohk-observation-roles-1"
        and declaration.observation_role.code == "measured_actual"
    )


def _claim_support_state(loaded, record_id, *, family: str) -> tuple[str, str, str]:
    if family == "fld":
        successors = loaded.flow_declaration_successor_ids[record_id]
        withdrawals = loaded.flow_declaration_withdrawn_by[record_id]
        root_id = loaded.flow_declaration_root_by_id[record_id]
        tips = loaded.current_flow_declaration_tips_by_root[root_id]
    else:
        successors = loaded.variable_port_association_superseded_by[record_id]
        withdrawals = loaded.variable_port_association_withdrawn_by[record_id]
        root_id = loaded.variable_port_association_root_by_id[record_id]
        tips = loaded.current_variable_port_association_tips_by_root[root_id]
    activity = (
        "superseded" if successors else
        "withdrawn" if withdrawals else "current")
    health = "inactive" if not tips else "conflicted" if len(tips) > 1 else "healthy"
    alignment = "unaligned" if health == "inactive" else "exact"
    return activity, health, alignment


def _semantic_support_state(loaded, record_id) -> tuple[str, str, str]:
    record = loaded.semantic_declarations[record_id]
    tips = loaded.current_semantic_tips_by_variable_dimension[
        (record.variable_anchor_id, "observation_role")]
    activity = "superseded" if loaded.semantic_superseded_by[record_id] else "current"
    health = "conflicted" if len(tips) > 1 else "healthy"
    alignment = (
        "exact" if all(_semantic_exact_measured_actual(tip) for tip in tips)
        else "unaligned")
    return activity, health, alignment


def _support_payloads(material, loaded, association, indices=None) -> tuple[dict, ...]:
    indices = _indices(material) if indices is None else indices
    pins = (
        ("frg", association.flow_registration_record_id),
        ("vrg", association.variable_registration_record_id),
        ("prg", association.port_registration_record_id),
        ("fld", association.flow_declaration_record_id),
        ("vpa", association.variable_port_association_record_id),
        ("vsm", association.variable_semantic_declaration_record_id),
    )
    rows = []
    for kind, record_id in pins:
        if kind in {"frg", "vrg", "prg"}:
            state = ("permanent", "not_applicable", "exact")
        elif kind in {"fld", "vpa"}:
            state = _claim_support_state(loaded, record_id, family=kind)
        else:
            state = _semantic_support_state(loaded, record_id)
        rows.append({
            "support_kind": kind,
            "record_index": indices[record_id],
            "activity": state[0],
            "containing_lineage_health": state[1],
            "current_alignment": state[2],
        })
    return tuple(rows)


def _endpoint_registration(loaded, flow_anchor_id, variable_anchor_id,
                           participant_port_anchor_id) -> str:
    missing = (
        flow_anchor_id not in loaded.flow_registrations_by_anchor,
        variable_anchor_id not in loaded.variable_registrations_by_anchor,
        participant_port_anchor_id not in loaded.port_registrations_by_anchor,
    )
    if not any(missing):
        return "all_registered"
    if sum(missing) != 1:
        return "multiple_not_registered"
    return (
        "flow_not_registered" if missing[0] else
        "variable_not_registered" if missing[1] else
        "port_not_registered")


def _empty_subject_payload() -> dict:
    return {
        "declaration_presence": "not_declared",
        "declaration_conclusion": "not_evaluated",
        "agreement_findings": (),
        "participant_role": None,
        "roots": (),
        "effective_body_groups": (),
        "current_assertion_indices": (),
    }


def _subject_payload(material, loaded, subject, indices=None) -> dict:
    indices = _indices(material) if indices is None else indices
    declaration_ids = loaded.flow_measurement_ids_by_subject.get(subject, ())
    if not declaration_ids:
        return _empty_subject_payload()

    root_ids = tuple(sorted({
        loaded.flow_measurement_root_by_id[record_id]
        for record_id in declaration_ids
    }))
    root_position = {root_id: position for position, root_id in enumerate(root_ids)}
    root_work = []
    body_by_tip = {}
    root_by_tip = {}
    for root_id in root_ids:
        lineage_ids = tuple(sorted(
            record_id for record_id in declaration_ids
            if loaded.flow_measurement_root_by_id[record_id] == root_id))
        tip_ids = tuple(sorted(
            record.record_id
            for record in loaded.current_flow_measurement_tips_by_root[root_id]))
        withdrawal_ids = tuple(sorted(
            withdrawal_id
            for record_id in lineage_ids
            for withdrawal_id in loaded.flow_measurement_withdrawn_by[record_id]))
        health = (
            "inactive" if not tip_ids else
            "conflicted" if len(tip_ids) > 1 else "healthy")
        for tip_id in tip_ids:
            body_by_tip[tip_id] = loaded.flow_measurement_effective_body_by_id[tip_id]
            root_by_tip[tip_id] = root_id
        root_work.append({
            "root_id": root_id,
            "lineage_ids": lineage_ids,
            "tip_ids": tip_ids,
            "withdrawal_ids": withdrawal_ids,
            "lineage_health": health,
        })

    tip_ids_by_body = {}
    for tip_id in sorted(body_by_tip):
        tip_ids_by_body.setdefault(body_by_tip[tip_id], []).append(tip_id)
    ordered_bodies = tuple(sorted(tip_ids_by_body))
    body_position = {body: position for position, body in enumerate(ordered_bodies)}
    groups = []
    for body in ordered_bodies:
        tip_ids = tuple(sorted(tip_ids_by_body[body]))
        representative_id = min(tip_ids)
        representative = loaded.flow_measurement_associations[representative_id]
        participating_roots = tuple(sorted({root_by_tip[tip_id] for tip_id in tip_ids}))
        groups.append({
            "group_index": body_position[body],
            "representative_current_tip_index": indices[representative_id],
            "current_tip_indices": tuple(indices[tip_id] for tip_id in tip_ids),
            "participating_root_indices": tuple(
                root_position[root_id] for root_id in participating_roots),
            "participant_role": loaded.flow_measurement_participant_role_by_id[
                representative_id],
            "orientation": representative.orientation,
            "support_rows": _support_payloads(
                material, loaded, representative, indices),
        })

    roots = []
    for row in root_work:
        group_indices = tuple(sorted({
            body_position[body_by_tip[tip_id]] for tip_id in row["tip_ids"]
        }))
        roots.append({
            "root_index": root_position[row["root_id"]],
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
    active_body_sets = tuple(
        frozenset(body_by_tip[tip_id] for tip_id in row["tip_ids"])
        for row in root_work if row["tip_ids"])
    corroborating = any(
        len({root_by_tip[tip_id] for tip_id in tip_ids
             if root_work[root_position[root_by_tip[tip_id]]]["lineage_health"]
             == "healthy"}) >= 2
        for tip_ids in tip_ids_by_body.values())
    disagreement = len(set(active_body_sets)) > 1
    findings = []
    if len(healthy) == 1:
        findings.append("one_healthy_root")
    if corroborating:
        findings.append("corroborating_healthy_roots")
    if conflicted:
        findings.append("same_root_conflict")
    if inactive:
        findings.append("inactive_roots_present")
    if disagreement:
        findings.append("cross_root_effective_body_disagreement")

    conclusion = (
        "conflicted" if conflicted or disagreement else
        "declared_direct_measurement_relevance" if healthy else
        "inactive")
    first = loaded.flow_measurement_associations[declaration_ids[0]]
    return {
        "declaration_presence": "declared",
        "declaration_conclusion": conclusion,
        "agreement_findings": tuple(findings),
        "participant_role": loaded.flow_measurement_participant_role_by_id[
            first.record_id],
        "roots": tuple(roots),
        "effective_body_groups": tuple(groups),
        "current_assertion_indices": tuple(sorted(
            indices[tip_id] for tip_id in body_by_tip)),
    }


def _exact_payload(material, loaded, flow_anchor_id, variable_anchor_id,
                   participant_port_anchor_id, context, orientation) -> dict:
    subject = (
        flow_anchor_id, variable_anchor_id, participant_port_anchor_id,
        context, "direct_measurement_relevance", orientation,
    )
    return {
        "flow_anchor_id": flow_anchor_id,
        "variable_anchor_id": variable_anchor_id,
        "participant_port_anchor_id": participant_port_anchor_id,
        "context": context.model_dump(mode="python"),
        "orientation": orientation,
        "endpoint_registration": _endpoint_registration(
            loaded, flow_anchor_id, variable_anchor_id,
            participant_port_anchor_id),
        **_subject_payload(material, loaded, subject),
    }


def _entry_payload(material, loaded, subject, entry_index, indices) -> dict:
    payload = _subject_payload(material, loaded, subject, indices)
    if payload["declaration_presence"] != "declared" \
            or payload["participant_role"] is None:
        raise ValueError("reverse index selected an absent FM subject")
    return {
        "entry_index": entry_index,
        "flow_anchor_id": subject[0],
        "variable_anchor_id": subject[1],
        "participant_port_anchor_id": subject[2],
        "orientation": subject[5],
        "declaration_conclusion": payload["declaration_conclusion"],
        "agreement_findings": payload["agreement_findings"],
        "participant_role": payload["participant_role"],
        "roots": payload["roots"],
        "effective_body_groups": payload["effective_body_groups"],
        "current_assertion_indices": payload["current_assertion_indices"],
    }


def _reverse_payload(material, loaded, endpoint_id, context, *, axis: str) -> dict:
    indices = _indices(material)
    if axis == "flow":
        registered = endpoint_id in loaded.flow_registrations_by_anchor
        selected_ids = loaded.flow_measurement_ids_by_flow_context.get(
            (endpoint_id, context), ()) if registered else ()
        endpoint_field = "flow_anchor_id"
        order = lambda subject: (subject[1], subject[2], _ORIENTATION_RANK[subject[5]])
    elif axis == "variable":
        registered = endpoint_id in loaded.variable_registrations_by_anchor
        selected_ids = loaded.flow_measurement_ids_by_variable_context.get(
            (endpoint_id, context), ()) if registered else ()
        endpoint_field = "variable_anchor_id"
        order = lambda subject: (subject[0], subject[2], _ORIENTATION_RANK[subject[5]])
    else:
        registered = endpoint_id in loaded.port_registrations_by_anchor
        selected_ids = loaded.flow_measurement_ids_by_port_context.get(
            (endpoint_id, context), ()) if registered else ()
        endpoint_field = "participant_port_anchor_id"
        order = lambda subject: (subject[0], subject[1], _ORIENTATION_RANK[subject[5]])
    subjects = tuple(sorted({
        _subject(loaded.flow_measurement_associations[record_id])
        for record_id in selected_ids
    }, key=order))
    entries = tuple(
        _entry_payload(material, loaded, subject, entry_index, indices)
        for entry_index, subject in enumerate(subjects))
    return {
        endpoint_field: endpoint_id,
        "context": context.model_dump(mode="python"),
        "registration_status": "registered" if registered else "not_registered",
        "declaration_presence": "declared" if entries else "not_declared",
        "entries": entries,
    }


def _assertion_payload(material, loaded, record_id) -> dict:
    indices = _indices(material)
    record = loaded.records.get(record_id)
    found = record is not None and record.record_kind in {
        "flow_measurement_association",
        "flow_measurement_association_withdrawal",
    }
    base = {
        "record_id": record_id,
        "lookup_status": "found" if found else "not_found",
    }
    empty = {
        "assertion_activity": None,
        "containing_root_health": None,
        "containing_subject_conclusion": None,
        "containing_agreement_findings": None,
        "root_record_index": None,
        "successor_indices": (),
        "withdrawal_indices": (),
        "participant_role": None,
        "orientation": None,
        "support_rows": (),
    }
    if not found:
        return {**base, "record_index": None, **empty}
    if record.record_kind == "flow_measurement_association_withdrawal":
        return {**base, "record_index": indices[record_id], **empty}
    root_id = loaded.flow_measurement_root_by_id[record_id]
    tips = loaded.current_flow_measurement_tips_by_root[root_id]
    successors = loaded.flow_measurement_successor_ids[record_id]
    withdrawals = loaded.flow_measurement_withdrawn_by[record_id]
    subject_payload = _subject_payload(material, loaded, _subject(record), indices)
    return {
        **base,
        "record_index": indices[record_id],
        "assertion_activity": (
            "superseded" if successors else
            "withdrawn" if withdrawals else "current"),
        "containing_root_health": (
            "inactive" if not tips else
            "conflicted" if len(tips) > 1 else "healthy"),
        "containing_subject_conclusion": subject_payload[
            "declaration_conclusion"],
        "containing_agreement_findings": subject_payload[
            "agreement_findings"],
        "root_record_index": indices[root_id],
        "successor_indices": tuple(indices[item] for item in sorted(successors)),
        "withdrawal_indices": tuple(indices[item] for item in sorted(withdrawals)),
        "participant_role": loaded.flow_measurement_participant_role_by_id[record_id],
        "orientation": record.orientation,
        "support_rows": _support_payloads(material, loaded, record, indices),
    }


class _WithSubjectRows(_FlowMeasurementResult):
    @field_validator("roots", mode="before", check_fields=False)
    @classmethod
    def _roots_before(cls, value):
        return _rebuild_rows(value, FlowMeasurementRootRow, "roots")

    @field_validator("effective_body_groups", mode="before", check_fields=False)
    @classmethod
    def _groups_before(cls, value):
        return _rebuild_rows(
            value, FlowMeasurementEffectiveBodyGroupRow,
            "effective body groups")


class FlowMeasurementAssociationResult(_WithSubjectRows):
    material: ModelQueryMaterial
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    participant_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    orientation: FlowMeasurementOrientation
    endpoint_registration: FlowMeasurementEndpointRegistration
    declaration_presence: FlowMeasurementDeclarationPresence
    declaration_conclusion: FlowMeasurementDeclarationConclusion
    agreement_findings: tuple[FlowMeasurementAgreementFinding, ...]
    participant_role: FlowPortRole | None
    roots: tuple[FlowMeasurementRootRow, ...]
    effective_body_groups: tuple[FlowMeasurementEffectiveBodyGroupRow, ...]
    current_assertion_indices: tuple[_Index, ...]

    _material_before = field_validator("material", mode="before")(_rebuild_material)
    _context_before = field_validator("context", mode="before")(_rebuild_context)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _exact_payload(
            self.material, self.material.loaded(), self.flow_anchor_id,
            self.variable_anchor_id, self.participant_port_anchor_id,
            self.context, self.orientation)
        supplied = self.model_dump(mode="python", exclude={"material"})
        if supplied != expected:
            raise ValueError("flow-measurement association disclosure is forged")
        return self


class _ReverseResult(_FlowMeasurementResult):
    @field_validator("entries", mode="before", check_fields=False)
    @classmethod
    def _entries_before(cls, value):
        return _rebuild_rows(value, FlowMeasurementEntryRow, "entries")


class FlowMeasurementAssociationsForFlowResult(_ReverseResult):
    material: ModelQueryMaterial
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    context: AssertionContext
    registration_status: FlowMeasurementReverseRegistration
    declaration_presence: FlowMeasurementDeclarationPresence
    entries: tuple[FlowMeasurementEntryRow, ...]

    _material_before = field_validator("material", mode="before")(_rebuild_material)
    _context_before = field_validator("context", mode="before")(_rebuild_context)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _reverse_payload(
            self.material, self.material.loaded(), self.flow_anchor_id,
            self.context, axis="flow")
        if self.model_dump(mode="python", exclude={"material"}) != expected:
            raise ValueError("flow reverse FM disclosure is forged")
        return self


class FlowMeasurementAssociationsForVariableResult(_ReverseResult):
    material: ModelQueryMaterial
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    registration_status: FlowMeasurementReverseRegistration
    declaration_presence: FlowMeasurementDeclarationPresence
    entries: tuple[FlowMeasurementEntryRow, ...]

    _material_before = field_validator("material", mode="before")(_rebuild_material)
    _context_before = field_validator("context", mode="before")(_rebuild_context)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _reverse_payload(
            self.material, self.material.loaded(), self.variable_anchor_id,
            self.context, axis="variable")
        if self.model_dump(mode="python", exclude={"material"}) != expected:
            raise ValueError("variable reverse FM disclosure is forged")
        return self


class FlowMeasurementAssociationsAtPortResult(_ReverseResult):
    material: ModelQueryMaterial
    participant_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    registration_status: FlowMeasurementReverseRegistration
    declaration_presence: FlowMeasurementDeclarationPresence
    entries: tuple[FlowMeasurementEntryRow, ...]

    _material_before = field_validator("material", mode="before")(_rebuild_material)
    _context_before = field_validator("context", mode="before")(_rebuild_context)

    @model_validator(mode="after")
    def _coherent(self):
        expected = _reverse_payload(
            self.material, self.material.loaded(),
            self.participant_port_anchor_id, self.context, axis="port")
        if self.model_dump(mode="python", exclude={"material"}) != expected:
            raise ValueError("port reverse FM disclosure is forged")
        return self


class FlowMeasurementAssertionResult(_FlowMeasurementResult):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:fma|fmw)_[0-9a-f]{64}$")
    lookup_status: FlowMeasurementAssertionLookupStatus
    record_index: _Index | None
    assertion_activity: AssertionActivity | None
    containing_root_health: ContainingLineageHealth | None
    containing_subject_conclusion: FlowMeasurementDeclarationConclusion | None
    containing_agreement_findings: tuple[FlowMeasurementAgreementFinding, ...] | None
    root_record_index: _Index | None
    successor_indices: tuple[_Index, ...]
    withdrawal_indices: tuple[_Index, ...]
    participant_role: FlowPortRole | None
    orientation: FlowMeasurementOrientation | None
    support_rows: tuple[FlowMeasurementSupportRow, ...]

    _material_before = field_validator("material", mode="before")(_rebuild_material)

    @field_validator("support_rows", mode="before")
    @classmethod
    def _support_before(cls, value):
        return _rebuild_rows(value, FlowMeasurementSupportRow, "support rows")

    @model_validator(mode="after")
    def _coherent(self):
        expected = _assertion_payload(
            self.material, self.material.loaded(), self.record_id)
        if self.model_dump(mode="python", exclude={"material"}) != expected:
            raise ValueError("flow-measurement assertion disclosure is forged")
        return self
