"""Contracts for authority interpretation of exact source properties."""

import re
from datetime import UTC
from typing import Annotated, Literal, Union

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    model_validator,
)

from backend.identity_binding.contracts import AppliesScope, AuthorityRef, Membership
from backend.model_kernel import (
    ObservationRoleReference,
    QuantityKindReference,
    UnitReference,
)
from backend.source_interpretation.canonical import compute_revision_id
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]
INTERPRETATION_SET_ID_PATTERN = r"^[a-z0-9-]+$"
INTERPRETATION_RECORD_ID_PATTERN = r"^(spi|spr|spc|spj)_[0-9a-f]{64}$"


class _Frozen(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


class QuantityKindInterpretation(_Frozen):
    dimension: Literal["quantity_kind"]
    quantity_kind: QuantityKindReference


class ObservationRoleInterpretation(_Frozen):
    dimension: Literal["observation_role"]
    observation_role: ObservationRoleReference


class UnitInterpretation(_Frozen):
    dimension: Literal["unit"]
    unit: UnitReference


InterpretationBody = Annotated[
    Union[QuantityKindInterpretation, ObservationRoleInterpretation,
          UnitInterpretation],
    Field(discriminator="dimension"),
]


def _canonical_parents(value) -> tuple:
    values = tuple(value)
    if len(values) != len(set(values)):
        raise ValueError("superseded interpretation ids must be unique")
    return tuple(sorted(values))


InterpretationParentId = Annotated[str, Field(pattern=r"^spi_[0-9a-f]{64}$")]
CanonicalParents = Annotated[
    tuple[InterpretationParentId, ...], BeforeValidator(_canonical_parents)]


class SourcePropertyInterpretation(_Frozen):
    """One authority's interpretation of one exact source property."""

    record_kind: Literal["source_property_interpretation"] = (
        "source_property_interpretation")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^spi_[0-9a-f]{64}$")
    subject: SourceSubjectRef
    property: SourcePropertyRef
    interpretation: InterpretationBody
    applies: AppliesScope
    supersedes: CanonicalParents = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _does_not_supersede_self(self):
        if self.record_id in self.supersedes:
            raise ValueError("an interpretation cannot supersede itself")
        return self


class InterpretationRetraction(_Frozen):
    record_kind: Literal["interpretation_retraction"] = "interpretation_retraction"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^spr_[0-9a-f]{64}$")
    retracts: str = Field(pattern=r"^spi_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class InterpretationClosure(_Frozen):
    record_kind: Literal["interpretation_closure"] = "interpretation_closure"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^spc_[0-9a-f]{64}$")
    closes: str = Field(pattern=r"^spi_[0-9a-f]{64}$")
    end: UtcDatetime
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class InterpretationRejection(_Frozen):
    """A fully identified refused candidate; diagnostics only."""

    record_kind: Literal["interpretation_rejection"] = "interpretation_rejection"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^spj_[0-9a-f]{64}$")
    subject: SourceSubjectRef
    property: SourcePropertyRef
    rejected_interpretation: InterpretationBody
    proposed_applies: AppliesScope
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


InterpretationRecord = Annotated[
    Union[SourcePropertyInterpretation, InterpretationRetraction,
          InterpretationClosure, InterpretationRejection],
    Field(discriminator="record_kind"),
]


class InterpretationRevision(_Frozen):
    """Exact set identity and sorted, reconstructable record membership."""

    revision_id: str = Field(pattern=r"^irv_[0-9a-f]{64}$")
    record_ids: tuple[str, ...]
    record_count: int = Field(ge=0)
    interpretation_set_id: str = Field(pattern=INTERPRETATION_SET_ID_PATTERN)

    @model_validator(mode="after")
    def _membership_consistent(self):
        if not isinstance(self.interpretation_set_id, str) or not re.fullmatch(
                INTERPRETATION_SET_ID_PATTERN, self.interpretation_set_id):
            raise ValueError("interpretation_set_id is invalid")
        if any(not re.fullmatch(INTERPRETATION_RECORD_ID_PATTERN, record_id)
               for record_id in self.record_ids):
            raise ValueError("record_ids contain an invalid record id")
        if list(self.record_ids) != sorted(set(self.record_ids)):
            raise ValueError("record_ids must be unique and sorted")
        if self.record_count != len(self.record_ids):
            raise ValueError("record_count must equal len(record_ids)")
        expected = compute_revision_id(
            self.interpretation_set_id, self.record_ids)
        if self.revision_id != expected:
            raise ValueError("revision_id does not match the membership")
        return self


InterpretationStatus = Literal[
    "interpreted", "applicability_unknown", "outside_applicability",
    "not_declared", "ambiguous", "conflicted", "superseded", "retracted",
    "inactive"]
InterpretationDimension = Literal["quantity_kind", "observation_role", "unit"]


class InterpretationAssertionSummary(_Frozen):
    record_id: str = Field(pattern=r"^spi_[0-9a-f]{64}$")
    dimension: InterpretationDimension
    interpretation: InterpretationBody
    authority: AuthorityRef
    declared_applies: AppliesScope
    effective_applies: AppliesScope
    closure_records: tuple[str, ...] = ()
    superseded_by: tuple[str, ...] = ()
    retracted_by: tuple[str, ...] = ()
    active: bool
    membership_at: Membership
    recorded_at: UtcDatetime

    @model_validator(mode="after")
    def _consistent(self):
        if self.dimension != self.interpretation.dimension:
            raise ValueError("summary dimension must match its interpretation")
        if self.active != (not self.superseded_by and not self.retracted_by):
            raise ValueError("active is derived from lifecycle links")
        if len(self.closure_records) > 1:
            raise ValueError("at most one closure may be disclosed")
        for values, prefix in ((self.closure_records, "spc"),
                               (self.superseded_by, "spi"),
                               (self.retracted_by, "spr")):
            if list(values) != sorted(set(values)):
                raise ValueError("lifecycle ids must be unique and sorted")
            if any(not re.fullmatch(rf"^{prefix}_[0-9a-f]{{64}}$", item)
                   for item in values):
                raise ValueError("lifecycle id has the wrong record kind")
        return self


class DimensionInterpretationResolution(_Frozen):
    dimension: InterpretationDimension
    status: InterpretationStatus
    interpretation: InterpretationBody | None = None
    candidate_interpretations: tuple[InterpretationBody, ...] = ()
    via_assertions: tuple[InterpretationAssertionSummary, ...] = ()
    applicability_basis: Literal[
        "declared_interval", "includes_unbounded_claim"] | None = None

    @model_validator(mode="after")
    def _consistent(self):
        positive = self.status == "interpreted"
        if positive != (self.interpretation is not None):
            raise ValueError("interpretation exists exactly when interpreted")
        if positive != (self.applicability_basis is not None):
            raise ValueError("basis exists exactly when interpreted")
        candidate_status = self.status in (
            "applicability_unknown", "ambiguous", "conflicted")
        if bool(self.candidate_interpretations) != candidate_status:
            raise ValueError("candidate interpretations must match status")
        candidate_count = len(self.candidate_interpretations)
        if self.status == "applicability_unknown" and candidate_count != 1:
            raise ValueError(
                "applicability_unknown carries exactly one candidate body")
        if self.status in ("ambiguous", "conflicted") and candidate_count < 2:
            raise ValueError(
                "ambiguity or conflict carries at least two candidate bodies")
        if self.status != "not_declared" and not self.via_assertions:
            raise ValueError(
                "a declared resolution outcome requires explanatory assertions")
        bodies = (() if self.interpretation is None
                  else (self.interpretation,)) + self.candidate_interpretations
        if any(body.dimension != self.dimension for body in bodies):
            raise ValueError("result carries a wrong-dimension body")
        if any(summary.dimension != self.dimension
               for summary in self.via_assertions):
            raise ValueError("result carries a wrong-dimension summary")
        from backend.source_interpretation.canonical import canonical_sort_key
        keys = tuple(canonical_sort_key(body)
                     for body in self.candidate_interpretations)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("candidate bodies must be unique and sorted")
        ids = tuple(summary.record_id for summary in self.via_assertions)
        if ids != tuple(sorted(set(ids))):
            raise ValueError("summaries must be unique and sorted")
        return self


class PropertyInterpretationResult(_Frozen):
    subject: SourceSubjectRef
    property: SourcePropertyRef
    at: UtcDatetime
    quantity_kind: DimensionInterpretationResolution
    observation_role: DimensionInterpretationResolution
    unit: DimensionInterpretationResolution
    revision: InterpretationRevision

    @model_validator(mode="after")
    def _dimensions_locked(self):
        if (self.quantity_kind.dimension != "quantity_kind"
                or self.observation_role.dimension != "observation_role"
                or self.unit.dimension != "unit"):
            raise ValueError("result arms must carry their named dimensions")
        return self


__all__ = [
    "AppliesScope", "AuthorityRef", "CanonicalParents",
    "INTERPRETATION_RECORD_ID_PATTERN", "INTERPRETATION_SET_ID_PATTERN",
    "DimensionInterpretationResolution", "InterpretationAssertionSummary",
    "InterpretationBody", "InterpretationClosure", "InterpretationDimension",
    "InterpretationRecord", "InterpretationStatus",
    "InterpretationRejection", "InterpretationRetraction",
    "InterpretationRevision", "Membership",
    "ObservationRoleInterpretation", "PropertyInterpretationResult",
    "QuantityKindInterpretation", "SourcePropertyInterpretation",
    "UnitInterpretation", "UtcDatetime",
]
