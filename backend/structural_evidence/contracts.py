"""SN-001 claim, field, and engineering-context contracts.

A claim records what the source reported, in the source's own vocabulary:
verbatim lexemes, no anchors, no engineering meaning, no derived counts,
no name-derived keys. The engineering context is SN-001-local with a
first-class `unknown` and NO DEFAULT anywhere — a defaulted unknown would
satisfy "never inferred" while destroying the unknown/absent distinction.
"""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.data_sources.contracts import ExtractionOutcome
from backend.identity_binding.contracts import AuthorityRef
from backend.model_kernel import LifecycleView
from backend.structural_evidence.locators import (
    StepUsageLocator,
    StructuralAddress,
    StructuralSourceRef,
    canonical_locator_value,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


StructuralClaimKind = Literal[
    "bom_row", "step_part_definition", "step_nauo_usage"]


class SourceNativeField(_Frozen):
    """One field EXACTLY as the extractor reported it. `lexeme` is never
    parsed, coerced, normalized, trimmed, or unit-interpreted. None means
    the extractor reported an absent/empty cell — never zero, never
    missing-by-accident."""

    field_name_as_extracted: str = Field(min_length=1)
    lexeme: str | None
    address: StructuralAddress


def _field_sort_key(field: SourceNativeField) -> tuple[str, str]:
    # name first; the canonical locator value totalizes the tie-break
    # (column_index for CSV cells) without reading any display name.
    return (field.field_name_as_extracted,
            canonical_locator_value(field.address.locator))


class SourceStructuralClaim(_Frozen):
    """What the source reported. Carries no anchor, no engineering
    vocabulary, no derived count, no name-derived key."""

    claim_kind: StructuralClaimKind
    address: StructuralAddress
    fields: tuple[SourceNativeField, ...] = ()

    @model_validator(mode="after")
    def _fields_canonically_ordered(self):
        keys = [_field_sort_key(field) for field in self.fields]
        if keys != sorted(keys):
            raise ValueError(
                "fields must be canonically ordered by "
                "(field_name_as_extracted, canonical locator value)")
        return self


class SourceContainmentClaim(_Frozen):
    """Containment IN THE SOURCE'S OWN VOCABULARY. Never an MK-001 edge,
    never functional/causal/electrical/fluid/physical containment. For
    STEP both endpoints are DEFINITIONS (NAUO semantics)."""

    claim_kind: Literal["bom_parent_column", "step_nauo_usage_edge"]
    child: StructuralAddress
    parent: StructuralAddress


class DerivedUsagePath(_Frozen):
    """SN-001's OWN derivation, explicitly labelled; never what the
    source reported. When the parent definition is used more than once,
    SN-001 reports rather than picks."""

    derivation: Literal["nauo_parent_definition_chain_v1"]
    steps: tuple[StepUsageLocator, ...] = ()  # root-first; () unless unique
    ambiguity: Literal["unique", "multiple_parent_uses", "unresolved"]

    @model_validator(mode="after")
    def _steps_iff_unique(self):
        if (self.ambiguity == "unique") != bool(self.steps):
            raise ValueError("steps are present exactly when the path is "
                             "unique")
        return self


class QuantityFieldRef(_Frozen):
    """The exact extracted column carrying the quantity lexeme,
    identified by column index — never by a display/header name."""

    column_index: int = Field(ge=0)
    column_name_as_extracted: str  # disclosure only


class UnresolvedParentReference(_Frozen):
    """A BOM `parent` lexeme whose within-source lookup did not resolve
    to exactly one row. Disclosed verbatim; no containment claim is
    emitted, and nothing is guessed."""

    child: StructuralAddress
    parent_lexeme: str
    reason: Literal["no_matching_row", "multiple_matching_rows"]


# ------------------------------------------------------ engineering context
class DeclaredEngineeringContext(_Frozen):
    """A positive authority claim that this source describes one
    lifecycle view."""

    kind: Literal["declared_lifecycle_view"]
    view: LifecycleView  # model_kernel Literal, reused verbatim
    declared_by: AuthorityRef
    statement: str = Field(min_length=1)


class ViewIndependentEngineeringContext(_Frozen):
    """A POSITIVE claim that the structure holds regardless of view —
    never the absence of knowledge."""

    kind: Literal["view_independent"]
    declared_by: AuthorityRef
    statement: str = Field(min_length=1)


class UnknownEngineeringContext(_Frozen):
    """Absence of knowledge. Never equivalent to view_independent, and
    never a default."""

    kind: Literal["unknown"]
    reason: Literal["source_declares_no_view", "authority_has_not_declared"]


EngineeringContext = Annotated[
    Union[DeclaredEngineeringContext, ViewIndependentEngineeringContext,
          UnknownEngineeringContext],
    Field(discriminator="kind"),
]


class SourceStructuralClaimSet(_Frozen):
    """Everything SN-001 read from one persisted extraction, verbatim.
    `engineering_context` has NO DEFAULT. `quantity_field=None` means
    this source declares no quantity column. A STEP usage count is
    derivable only by counting disclosed usage claims; no field carries a
    manufactured count."""

    source_ref: StructuralSourceRef
    engineering_context: EngineeringContext
    subject_claims: tuple[SourceStructuralClaim, ...]
    containment_claims: tuple[SourceContainmentClaim, ...] = ()
    derived_paths: tuple[DerivedUsagePath, ...] = ()
    quantity_field: QuantityFieldRef | None = None
    unresolved_parent_references: tuple[UnresolvedParentReference, ...] = ()
    extraction_outcome: ExtractionOutcome
    extraction_warnings: tuple[str, ...] = ()
