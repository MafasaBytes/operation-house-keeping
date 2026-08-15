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


__all__ = [
    "AppliesScope", "AuthorityRef", "CanonicalParents",
    "INTERPRETATION_RECORD_ID_PATTERN", "INTERPRETATION_SET_ID_PATTERN",
    "InterpretationBody", "InterpretationClosure", "InterpretationRecord",
    "InterpretationRejection", "InterpretationRetraction",
    "InterpretationRevision", "Membership",
    "ObservationRoleInterpretation", "QuantityKindInterpretation",
    "SourcePropertyInterpretation", "UnitInterpretation", "UtcDatetime",
]

