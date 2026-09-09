"""FC-001 Slice B authoritative read-only result contracts."""

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.flow_measurement_results import FlowMeasurementOrientation
from backend.model_kernel.port_results import ModelQueryMaterial

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

class FlowOperatingCriterionLineageRow(_FC):
    root_index: _I
    root_record_index: _I
    lineage_record_indices: tuple[_I, ...]
    current_tip_indices: tuple[_I, ...]
    withdrawal_indices: tuple[_I, ...]
    lineage_health: Literal["healthy", "conflicted", "inactive"]

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

class FlowOperatingCriterionSubjectResult(_FC):
    flow_anchor_id: str
    variable_anchor_id: str
    participant_port_anchor_id: str
    context: AssertionContext
    orientation: FlowMeasurementOrientation
    conclusion: FlowOperatingCriterionConclusion
    reasons: tuple[FlowOperatingCriterionReason, ...]
    roots: tuple[FlowOperatingCriterionLineageRow, ...]
    fm_roots: tuple[FlowOperatingCriterionLineageRow, ...]
    body_groups: tuple[FlowOperatingCriterionBodyRow, ...]
    governing_body_group_index: _I | None

class FlowOperatingCriterionResult(_FC):
    material: ModelQueryMaterial
    subject: FlowOperatingCriterionSubjectResult


class FlowOperatingCriterionAssertionResult(_FC):
    material: ModelQueryMaterial
    record_id: str
    lookup_status: FlowOperatingCriterionLookupStatus
    record_index: _I | None
    positive_record_index: _I | None
    positive_activity: Literal["current", "superseded", "withdrawn"] | None
    body_group_index: _I | None
    subject: FlowOperatingCriterionSubjectResult | None
