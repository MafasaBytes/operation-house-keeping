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


_LOCATOR_KIND_BY_CLAIM_KIND = {
    "bom_row": "csv_row",
    "step_part_definition": "step_part_definition",
    "step_nauo_usage": "step_nauo_usage",
}


class SourceStructuralClaim(_Frozen):
    """What the source reported. Carries no anchor, no engineering
    vocabulary, no derived count, no name-derived key. Provenance is
    coherent by construction (owner audit 2026-08-12): the claim kind
    fixes the locator scheme, and every field is pinned to the claim's
    exact source — a bom_row field is a csv_cell on the claim's physical
    row whose disclosed name agrees with its locator, and a STEP field
    addresses the same structural object as its claim."""

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

    @model_validator(mode="after")
    def _kind_and_fields_cohere(self):
        locator = self.address.locator
        expected = _LOCATOR_KIND_BY_CLAIM_KIND[self.claim_kind]
        if locator.kind != expected:
            raise ValueError(
                f"a {self.claim_kind} claim is addressed by a {expected} "
                f"locator, not {locator.kind}")
        for field in self.fields:
            if field.address.source != self.address.source:
                raise ValueError(
                    "a field belongs to its claim's exact source")
            if self.claim_kind == "bom_row":
                cell = field.address.locator
                if cell.kind != "csv_cell":
                    raise ValueError(
                        "a bom_row field is addressed by a csv_cell "
                        "locator")
                if cell.physical_row_index != locator.physical_row_index:
                    raise ValueError(
                        "a bom_row field lives on its claim's physical "
                        "row")
                if field.field_name_as_extracted != \
                        cell.column_name_as_extracted:
                    raise ValueError(
                        "the field name disclosure must agree with its "
                        "cell locator's extracted column name")
            elif field.address != self.address:
                raise ValueError(
                    "a STEP field addresses the same structural object "
                    "as its claim")
        return self


class SourceContainmentClaim(_Frozen):
    """Containment IN THE SOURCE'S OWN VOCABULARY. Never an MK-001 edge,
    never functional/causal/electrical/fluid/physical containment.

    Endpoint grammar (adjudicated against D6, owner audit 2026-08-12):

    - `bom_parent_column`: child and parent are both csv_row addresses
      from one source.
    - `step_nauo_usage_edge`: the parent is the RELATING definition's
      step_part_definition address; the child is the NAUO usage
      occurrence's step_nauo_usage address, whose `definition_path_id`
      names the RELATED definition and whose `parent_definition_path_id`
      must equal the parent endpoint's `extractor_path_id`. Both
      definitions therefore stay named, and repeated same-pair usages
      stay distinct. This is a source claim about STEP product
      structure, never the model's hand-authored definition-level
      relationship (D6), whose definition-to-definition endpoints and
      type name live only in the accepted model ledger."""

    claim_kind: Literal["bom_parent_column", "step_nauo_usage_edge"]
    child: StructuralAddress
    parent: StructuralAddress

    @model_validator(mode="after")
    def _endpoint_grammar(self):
        if self.child.source != self.parent.source:
            raise ValueError(
                "containment endpoints come from one exact source")
        if self.claim_kind == "bom_parent_column":
            if self.child.locator.kind != "csv_row" or \
                    self.parent.locator.kind != "csv_row":
                raise ValueError(
                    "bom_parent_column endpoints are csv_row addresses")
        else:
            if self.child.locator.kind != "step_nauo_usage":
                raise ValueError(
                    "the step_nauo_usage_edge child is the NAUO usage "
                    "occurrence address")
            if self.parent.locator.kind != "step_part_definition":
                raise ValueError(
                    "the step_nauo_usage_edge parent is the relating "
                    "definition address")
            if self.child.locator.parent_definition_path_id != \
                    self.parent.locator.extractor_path_id:
                raise ValueError(
                    "the usage's parent_definition_path_id must equal "
                    "the parent endpoint's extractor_path_id")
        return self


class DerivedUsagePath(_Frozen):
    """SN-001's OWN derivation, explicitly labelled; never what the
    source reported. When the parent definition is used more than once,
    SN-001 reports rather than picks. `for_usage` names the usage the
    path was derived FOR, so an ambiguous path (steps=()) still
    identifies its subject."""

    derivation: Literal["nauo_parent_definition_chain_v1"]
    for_usage: StepUsageLocator
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


class LabelFieldRef(_Frozen):
    """The DECLARED display-label column, identified by column index. A
    label is disclosure: duplicate labels are reported, never merged,
    and a label is never identity and never a join key. STEP claim sets
    carry no label declaration — their single `name` field is the label
    by construction, and step_structural_claims documents that."""

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
    label_field: LabelFieldRef | None = None
    unresolved_parent_references: tuple[UnresolvedParentReference, ...] = ()
    extraction_outcome: ExtractionOutcome
    extraction_warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _provenance_coherent(self):
        """Owner audit 2026-08-12: every address in a claim set belongs
        to the set's exact `source_ref`, containment endpoints refer to
        disclosed subject claims (complete addresses, never bare
        locators), and a derived path is derived FOR a disclosed usage
        claim."""
        def own(address, what):
            if address.source != self.source_ref:
                raise ValueError(f"{what} must belong to the claim set's "
                                 "exact source_ref")
        claim_addresses = set()
        usage_locators = set()
        for claim in self.subject_claims:
            own(claim.address, "a subject claim")
            claim_addresses.add(claim.address)
            if claim.claim_kind == "step_nauo_usage":
                usage_locators.add(claim.address.locator)
        for containment in self.containment_claims:
            own(containment.child, "a containment endpoint")
            if containment.child not in claim_addresses or \
                    containment.parent not in claim_addresses:
                raise ValueError(
                    "containment endpoints must refer to disclosed "
                    "subject claims")
        for reference in self.unresolved_parent_references:
            own(reference.child, "an unresolved parent child")
        for path in self.derived_paths:
            if path.for_usage not in usage_locators:
                raise ValueError(
                    "a derived path must be derived for a disclosed "
                    "usage claim")
            # Owner follow-up (2026-08-12): every STEP of a unique
            # chain — not merely its for_usage — is evidence-backed and
            # coherent. Ambiguous/unresolved paths carry no steps (the
            # DerivedUsagePath contract enforces that), so this loop is
            # the unique-path discipline.
            if len(set(path.steps)) != len(path.steps):
                raise ValueError(
                    "derived-path steps must not repeat")
            for step in path.steps:
                if step not in usage_locators:
                    raise ValueError(
                        "every derived-path step must be a disclosed "
                        "usage claim")
            if path.steps and path.steps[-1] != path.for_usage:
                raise ValueError(
                    "a unique derived path ends at its for_usage")
            for parent_step, child_step in zip(path.steps,
                                               path.steps[1:]):
                if child_step.parent_definition_path_id != \
                        parent_step.definition_path_id:
                    raise ValueError(
                        "adjacent derived-path steps must chain the "
                        "parent usage's definition to the child's "
                        "parent definition")
        return self
