"""FC-001 Slice B authoritative read-only result contracts."""

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.flow_measurement_results import FlowMeasurementOrientation
from backend.model_kernel.port_results import ModelQueryMaterial
from backend.model_kernel.result_revalidation import (
    inspect_supplied_graph as _inspect_supplied_graph,
    rebuild_material as _rebuild_material,
    rebuild_row as _rebuild_row,
    rebuild_rows as _rebuild_rows,
)
from backend.system_identity import FLOW_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN, PORT_ANCHOR_ID_PATTERN

_I = Annotated[StrictInt, Field(ge=0)]

FlowOperatingCriterionConclusion = Literal[
    "not_declared", "inactive", "conflicted", "disagreed", "inapplicable", "applicable"]
FlowOperatingCriterionReason = Literal[
    "fc_not_declared", "fc_inactive", "fc_same_root_conflict", "fc_cross_root_disagreement",
    "fm_inactive", "fm_same_root_conflict", "fm_cross_root_disagreement", "fm_body_not_current",
    "vcn_conflicted", "vcn_not_current", "typed_support_not_current", "typed_support_conflicted",
    "typed_support_inactive", "typed_support_unaligned"]
FlowOperatingCriterionLookupStatus = Literal["not_found", "found"]

class _FC(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", revalidate_instances="always")

    @model_validator(mode="wrap")
    @classmethod
    def _bounded_graph(cls, value, handler):
        _inspect_supplied_graph(value)
        return handler(value)

class FlowOperatingCriterionLineageRow(_FC):
    root_index: _I
    root_record_index: _I
    lineage_record_indices: tuple[_I, ...]
    current_tip_indices: tuple[_I, ...]
    withdrawal_indices: tuple[_I, ...]
    lineage_health: Literal["healthy", "conflicted", "inactive"]

    @model_validator(mode="after")
    def _coherent(self):
        for values in (self.lineage_record_indices, self.current_tip_indices, self.withdrawal_indices):
            if tuple(values) != tuple(sorted(set(values))): raise ValueError("lineage indices must be unique and increasing")
        if not self.lineage_record_indices or self.root_record_index not in self.lineage_record_indices: raise ValueError("lineage root is missing")
        expected="inactive" if not self.current_tip_indices else "conflicted" if len(self.current_tip_indices)>1 else "healthy"
        if self.lineage_health != expected: raise ValueError("lineage health is forged")
        return self

class FlowOperatingCriterionSupportRow(_FC):
    support_kind: Literal["frg", "vrg", "prg", "fld", "vpa", "vsm", "crg", "vcn", "pcn", "pif"]
    record_index: _I
    activity: Literal["permanent", "current", "superseded", "withdrawn"]
    lineage_health: Literal["not_applicable", "healthy", "conflicted", "inactive"]
    alignment: Literal["exact", "unaligned"]

class FlowOperatingCriterionBodyRow(_FC):
    group_index: _I
    declaration_indices: tuple[_I, ...]
    current_declaration_indices: tuple[_I, ...]
    witness_record_indices: tuple[_I, ...]
    matching_fm_current_indices: tuple[_I, ...]
    support_rows: tuple[FlowOperatingCriterionSupportRow, ...]
    reasons: tuple[FlowOperatingCriterionReason, ...]

    _supports = field_validator("support_rows", mode="before")(
        lambda value: _rebuild_rows(value, FlowOperatingCriterionSupportRow, "FC support rows"))

class FlowOperatingCriterionSubjectResult(_FC):
    flow_anchor_id: str = Field(pattern=FLOW_ANCHOR_ID_PATTERN)
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    participant_port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    orientation: FlowMeasurementOrientation
    conclusion: FlowOperatingCriterionConclusion
    reasons: tuple[FlowOperatingCriterionReason, ...]
    roots: tuple[FlowOperatingCriterionLineageRow, ...]
    fm_roots: tuple[FlowOperatingCriterionLineageRow, ...]
    body_groups: tuple[FlowOperatingCriterionBodyRow, ...]
    governing_body_group_index: _I | None

    _roots = field_validator("roots", "fm_roots", mode="before")(
        lambda value: _rebuild_rows(value, FlowOperatingCriterionLineageRow, "FC lineage rows"))
    _groups = field_validator("body_groups", mode="before")(
        lambda value: _rebuild_rows(value, FlowOperatingCriterionBodyRow, "FC body rows"))

class FlowOperatingCriterionResult(_FC):
    material: ModelQueryMaterial
    subject: FlowOperatingCriterionSubjectResult

    _material = field_validator("material", mode="before")(_rebuild_material)
    _subject = field_validator("subject", mode="before")(
        lambda value: _rebuild_row(value, FlowOperatingCriterionSubjectResult))

    @model_validator(mode="after")
    def _authoritative(self):
        from backend.model_kernel.queries import ModelQueries
        _, expected=ModelQueries(self.material.loaded())._flow_operating_criterion_subject(
            self.subject.flow_anchor_id,self.subject.variable_anchor_id,
            self.subject.participant_port_anchor_id,self.subject.context,self.subject.orientation)
        if self.subject.model_dump(mode="python") != expected.model_dump(mode="python"):
            raise ValueError("flow operating criterion result is forged")
        return self


class FlowOperatingCriterionAssertionResult(_FC):
    material: ModelQueryMaterial
    record_id: str = Field(pattern=r"^(?:fcd|fcw)_[0-9a-f]{64}$")
    lookup_status: FlowOperatingCriterionLookupStatus
    record_index: _I | None
    positive_record_index: _I | None
    positive_activity: Literal["current", "superseded", "withdrawn"] | None
    body_group_index: _I | None
    subject: FlowOperatingCriterionSubjectResult | None

    _material = field_validator("material", mode="before")(_rebuild_material)
    _subject = field_validator("subject", mode="before")(
        lambda value: None if value is None else _rebuild_row(value, FlowOperatingCriterionSubjectResult))

    @model_validator(mode="after")
    def _authoritative(self):
        loaded=self.material.loaded(); indices={x:i for i,x in enumerate(loaded.revision.record_ids)}
        record=loaded.records.get(self.record_id)
        found=record is not None and record.record_kind in {"flow_operating_criterion_declaration","flow_operating_criterion_withdrawal"}
        if not found:
            expected=("not_found",None,None,None,None,None)
        else:
            target=self.record_id if record.record_kind=="flow_operating_criterion_declaration" else record.withdraws
            s=loaded.flow_operating_criterion_subject_by_id[target]
            from backend.model_kernel.queries import ModelQueries
            _,subject=ModelQueries(loaded)._flow_operating_criterion_subject(s[0],s[1],s[2],s[3],s[5])
            activity="current" if not loaded.flow_operating_criterion_successor_ids[target] and not loaded.flow_operating_criterion_withdrawn_by[target] else "withdrawn" if loaded.flow_operating_criterion_withdrawn_by[target] else "superseded"
            gi=next(i for i,g in enumerate(subject.body_groups) if indices[target] in g.declaration_indices)
            expected=("found",indices[self.record_id],indices[target],activity,gi,subject)
        actual=(self.lookup_status,self.record_index,self.positive_record_index,self.positive_activity,self.body_group_index,self.subject)
        if actual != expected: raise ValueError("flow operating criterion assertion is forged")
        return self
