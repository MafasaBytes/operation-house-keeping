"""IB-001 binding-ledger contracts.

Append-only records of explicit identity decisions, resolution results
that disclose everything (targets, candidates, assertions, authorities,
lifecycle links, revision membership), and typed errors. Locator types
are reused from ``temporal_state`` — subject identity is the
three-dimension ``SourceSubjectRef``; property identity is the
six-dimension subject+property pair. ``recorded_at`` is audit information
everywhere: it never picks winners.
"""

import re
from datetime import UTC
from typing import Annotated, Literal, Union

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from backend.identity_binding.canonical import compute_revision_id
from backend.system_identity import (
    ENTITY_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
    EntityAnchor,
    VariableAnchor,
)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]

BINDING_SET_ID_PATTERN = r"^[a-z0-9-]+$"
LEDGER_RECORD_ID_PATTERN = r"^(anc|iba|ibr|ibc|ibj)_[0-9a-f]{64}$"


def _sorted_unique(values) -> bool:
    return list(values) == sorted(set(values))


# -- errors
class IdentityBindingError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class BindingConfigurationError(IdentityBindingError):
    """Invalid binding-set root, id, or record location."""


class BindingIntegrityError(IdentityBindingError):
    """The binding set violates an integrity invariant. Validation is
    all-or-nothing: an invalid set resolves nothing."""


class BindingResolutionError(IdentityBindingError):
    """Invalid input to a resolution (e.g. a naive `at`)."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# -- authority
class AuthorityRef(_Frozen):
    """A recorded CLAIM of authorship. Nothing is authenticated or signed
    in IB-001; `agent` is a claimed name and never a credential."""

    kind: Literal["human_owner", "test_fixture"]
    agent: str = Field(min_length=1)
    method: Literal["manual_declaration"]


# -- applicability scope
class DeclaredBoundary(_Frozen):
    kind: Literal["declared"]
    at: UtcDatetime


class UnboundedBoundary(_Frozen):
    """An explicit authority claim — not the absence of knowledge."""

    kind: Literal["unbounded"]


class UnknownBoundary(_Frozen):
    """Absence of knowledge — never equivalent to unbounded."""

    kind: Literal["unknown"]


Boundary = Annotated[
    Union[DeclaredBoundary, UnboundedBoundary, UnknownBoundary],
    Field(discriminator="kind"),
]


class AppliesScope(_Frozen):
    """Half-open [start, end) applicability on the ingestion-receipt axis
    — the axis TS-001 queries are historically closed over. The boundary
    instant belongs to the successor."""

    axis: Literal["ingestion_received_at"]
    start_boundary: Boundary
    end_boundary: Boundary
    interval_semantics: Literal["half_open"]

    @model_validator(mode="after")
    def _declared_interval_ordered(self):
        start, end = self.start_boundary, self.end_boundary
        if (start.kind == "declared" and end.kind == "declared"
                and start.at >= end.at):
            raise ValueError("declared interval requires start < end")
        return self


# -- ledger records
class AnchorDeclaration(_Frozen):
    record_kind: Literal["anchor_declaration"] = "anchor_declaration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^anc_[0-9a-f]{64}$")
    anchor_kind: Literal["entity", "variable"]
    anchor: EntityAnchor | VariableAnchor
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _kind_matches_payload(self):
        expected = EntityAnchor if self.anchor_kind == "entity" else VariableAnchor
        if not isinstance(self.anchor, expected):
            raise ValueError("anchor_kind does not match the anchor payload")
        return self


class BindingAssertion(_Frozen):
    record_kind: Literal["binding_assertion"] = "binding_assertion"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^iba_[0-9a-f]{64}$")
    binding_kind: Literal["subject", "property"]
    subject: SourceSubjectRef
    property: SourcePropertyRef | None = None
    target_anchor_id: str
    applies: AppliesScope
    recorded_at: UtcDatetime
    authority: AuthorityRef
    # CORRECTION only ("the old decision was wrong") — never real-world
    # replacement, which is applicability closure plus a NEW anchor.
    supersedes: str | None = Field(default=None, pattern=r"^iba_[0-9a-f]{64}$")
    note: str = ""

    @model_validator(mode="after")
    def _shape_matches_kind(self):
        if self.binding_kind == "subject":
            if self.property is not None:
                raise ValueError("a subject binding carries no property locator")
            if not re.fullmatch(ENTITY_ANCHOR_ID_PATTERN, self.target_anchor_id):
                raise ValueError("a subject binding targets an entity anchor")
        else:
            if self.property is None:
                raise ValueError("a property binding requires the full locator")
            if not re.fullmatch(VARIABLE_ANCHOR_ID_PATTERN, self.target_anchor_id):
                raise ValueError("a property binding targets a variable anchor")
        return self


class BindingRetraction(_Frozen):
    record_kind: Literal["binding_retraction"] = "binding_retraction"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^ibr_[0-9a-f]{64}$")
    retracts: str = Field(pattern=r"^iba_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class ApplicabilityClosure(_Frozen):
    """The only amendment: convert an unknown/unbounded effective end to a
    declared one (narrowing). Changing a declared end is a correction and
    requires supersession."""

    record_kind: Literal["applicability_closure"] = "applicability_closure"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^ibc_[0-9a-f]{64}$")
    closes: str = Field(pattern=r"^iba_[0-9a-f]{64}$")
    end: UtcDatetime
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class BindingRejection(_Frozen):
    """A considered-and-refused candidate. Diagnostics only — never an
    input to resolution."""

    record_kind: Literal["binding_rejection"] = "binding_rejection"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^ibj_[0-9a-f]{64}$")
    subject: SourceSubjectRef
    property: SourcePropertyRef | None = None
    rejected_anchor_id: str = Field(
        pattern=r"^(ent|var)_[0-9a-f]{32}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _target_matches_level(self):
        # subject/property decisions stay coherent: a subject-level
        # rejection refuses an entity, a property-level one a variable
        expected = (ENTITY_ANCHOR_ID_PATTERN if self.property is None
                    else VARIABLE_ANCHOR_ID_PATTERN)
        if not re.fullmatch(expected, self.rejected_anchor_id):
            raise ValueError(
                "rejected_anchor_id kind does not match the rejection level")
        return self


LedgerRecord = Union[
    AnchorDeclaration, BindingAssertion, BindingRetraction,
    ApplicabilityClosure, BindingRejection,
]


# -- revision
class BindingRevision(_Frozen):
    """Exact, reconstructable membership. `revision_id` names both the
    authoritative set and its membership; canonical order is the sorted
    record ids — never filesystem enumeration or recorded_at order."""

    revision_id: str = Field(pattern=r"^rev_[0-9a-f]{64}$")
    record_ids: tuple[str, ...]
    record_count: int = Field(ge=0)
    binding_set_id: str = Field(pattern=BINDING_SET_ID_PATTERN)

    @model_validator(mode="after")
    def _membership_consistent(self):
        ids = self.record_ids
        for record_id in ids:
            if not re.fullmatch(LEDGER_RECORD_ID_PATTERN, record_id):
                raise ValueError(f"{record_id!r} is not a ledger record id")
        if list(ids) != sorted(set(ids)):
            raise ValueError("record_ids must be unique and sorted")
        if self.record_count != len(ids):
            raise ValueError("record_count must equal len(record_ids)")
        if self.revision_id != compute_revision_id(self.binding_set_id, ids):
            raise ValueError("revision_id does not match the membership")
        return self


# -- resolution
ResolutionStatus = Literal[
    "bound", "applicability_unknown", "outside_applicability", "unbound",
    "ambiguous", "conflicted", "superseded", "retracted", "inactive",
]

Membership = Literal["in", "out", "unknown"]


class AssertionSummary(_Frozen):
    """Structured evidence: enough to explain a resolution — including the
    exact closure, supersession, and retraction records — without
    searching the revision."""

    record_id: str
    target_anchor_id: str
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
    def _lifecycle_consistent(self):
        if self.active != (not self.superseded_by and not self.retracted_by):
            raise ValueError(
                "active is equivalent to having no supersession or "
                "retraction links")
        if len(self.closure_records) > 1:
            raise ValueError("a valid result carries at most one closure")
        for values, prefix in ((self.superseded_by, "iba"),
                               (self.retracted_by, "ibr"),
                               (self.closure_records, "ibc")):
            if not _sorted_unique(values):
                raise ValueError("lifecycle record ids must be unique/sorted")
            for record_id in values:
                if not re.fullmatch(rf"^{prefix}_[0-9a-f]{{64}}$", record_id):
                    raise ValueError(f"{record_id!r} is not a {prefix} id")
        return self


class SubjectResolutionContext(_Frozen):
    """Non-recursive subject context on property results: statuses,
    anchors, and assertion ids only — never a nested ResolutionResult."""

    status: ResolutionStatus
    resolved_entity: EntityAnchor | None = None
    candidate_entities: tuple[EntityAnchor, ...] = ()
    via_assertion_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _context_consistent(self):
        if (self.status == "bound") != (self.resolved_entity is not None):
            raise ValueError("resolved_entity is set exactly when bound")
        if self.status == "bound" and self.candidate_entities:
            raise ValueError("a bound context carries no candidates")
        if not _sorted_unique([a.anchor_id for a in self.candidate_entities]):
            raise ValueError("candidate entities must be unique/ordered")
        if not _sorted_unique(self.via_assertion_ids):
            raise ValueError("assertion ids must be unique/ordered")
        for record_id in self.via_assertion_ids:
            if not re.fullmatch(r"^iba_[0-9a-f]{64}$", record_id):
                raise ValueError(f"{record_id!r} is not an assertion id")
        return self


class ResolutionResult(_Frozen):
    status: ResolutionStatus
    locator_subject: SourceSubjectRef
    locator_property: SourcePropertyRef | None = None
    resolved_target: EntityAnchor | VariableAnchor | None = None
    candidate_targets: tuple[EntityAnchor | VariableAnchor, ...] = ()
    via_assertions: tuple[AssertionSummary, ...] = ()
    applicability_basis: Literal[
        "declared_interval", "includes_unbounded_claim"] | None = None
    revision: BindingRevision
    subject_context: SubjectResolutionContext | None = None
    detail: str = ""

    @model_validator(mode="after")
    def _result_consistent(self):
        bound = self.status == "bound"
        if bound != (self.resolved_target is not None):
            raise ValueError("resolved_target is set exactly when bound")
        if bound != (self.applicability_basis is not None):
            raise ValueError("applicability_basis exists exactly when bound")
        if bound and self.candidate_targets:
            raise ValueError("a bound result carries no candidates")
        if (self.status not in ("applicability_unknown", "ambiguous",
                                "conflicted") and self.candidate_targets):
            raise ValueError(f"{self.status} results cannot carry candidates")
        if (self.locator_property is not None) != (
                self.subject_context is not None):
            raise ValueError(
                "subject_context exists exactly for property resolution")
        expected = (VariableAnchor if self.locator_property is not None
                    else EntityAnchor)
        for anchor in (self.resolved_target, *self.candidate_targets):
            if anchor is not None and not isinstance(anchor, expected):
                raise ValueError(
                    "subject results carry entity anchors; property results "
                    "carry variable anchors")
        if not _sorted_unique([a.anchor_id for a in self.candidate_targets]):
            raise ValueError("candidates must be unique/canonically ordered")
        return self
