"""MK-001 model-ledger contracts.

Append-only records of explicit model knowledge over canonical
``system_identity`` anchors, plus result contracts that reject impossible
states. ``recorded_at`` is audit information everywhere — it never selects
winners. Assertions are ACTIVE/inactive; type-definition chain tips are
CURRENT. Registrations have no lifecycle at all: the kernel can never alter
an embedded anchor field, and a mistaken registration has no kernel
correction path.
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

from backend.model_kernel.canonical import canonical_bytes, compute_revision_id
from backend.system_identity import ENTITY_ANCHOR_ID_PATTERN, EntityAnchor

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]

MODEL_ID_PATTERN = r"^[a-z0-9-]+$"
MODEL_RECORD_ID_PATTERN = r"^(reg|rtd|rel|rwd)_[0-9a-f]{64}$"

ReferentKind = Literal[
    "logical_instance", "physical_instance", "type_definition", "unknown"
]
LifecycleView = Literal[
    "as_designed", "as_built", "as_configured", "as_operated", "as_maintained"
]


# ---------------------------------------------------------------- errors
class ModelKernelError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class ModelConfigurationError(ModelKernelError):
    """Invalid model-set root or model id."""


class ModelIntegrityError(ModelKernelError):
    """The model set violates an integrity invariant. Validation is
    all-or-nothing: an invalid set resolves nothing."""


class ModelQueryError(ModelKernelError):
    """Contract misuse at the query boundary. Absence and disagreement are
    statuses, never exceptions."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ------------------------------------------------------------- authority
class AuthorityRef(_Frozen):
    """A recorded CLAIM of authorship — nothing is authenticated or signed."""

    kind: Literal["human_owner", "test_fixture"]
    agent: str = Field(min_length=1)
    method: Literal["manual_declaration"]


# -------------------------------------------------------------- contexts
class LifecycleViewContext(_Frozen):
    kind: Literal["lifecycle_view"]
    view: LifecycleView


class ViewIndependentContext(_Frozen):
    kind: Literal["view_independent"]


AssertionContext = Annotated[
    Union[LifecycleViewContext, ViewIndependentContext],
    Field(discriminator="kind"),
]


# -------------------------------------------------------------- evidence
class OwnerDeclarationEvidence(_Frozen):
    """The claim's basis is a human decision, honestly labeled as such —
    the only prose-bearing evidence kind."""

    kind: Literal["owner_declaration"]
    statement: str = Field(min_length=1)


class ModelRecordEvidence(_Frozen):
    kind: Literal["model_record"]
    record_id: str = Field(pattern=r"^(reg|rtd|rel)_[0-9a-f]{64}$")


class IdentityBindingRecordEvidence(_Frozen):
    kind: Literal["identity_binding_record"]
    binding_set_id: str = Field(pattern=r"^[a-z0-9-]+$")
    record_id: str = Field(pattern=r"^(anc|iba|ibr|ibc|ibj)_[0-9a-f]{64}$")


class SourceRawRecordEvidence(_Frozen):
    kind: Literal["source_raw_record"]
    raw_record_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class TemporalOccurrenceEvidence(_Frozen):
    kind: Literal["temporal_occurrence"]
    occurrence_id: str = Field(pattern=r"^[0-9a-f]{32}$")


EvidenceRef = Annotated[
    Union[OwnerDeclarationEvidence, ModelRecordEvidence,
          IdentityBindingRecordEvidence, SourceRawRecordEvidence,
          TemporalOccurrenceEvidence],
    Field(discriminator="kind"),
]


def _normalized_kinds(value: tuple) -> tuple:
    normalized = tuple(sorted(set(value)))
    if not normalized:
        raise ValueError("at least one referent kind is required")
    return normalized


ReferentKindTuple = Annotated[
    tuple[ReferentKind, ...], AfterValidator(_normalized_kinds)
]


def _canonical_evidence(value: tuple) -> tuple:
    """Evidence order carries no engineering meaning and repeating identical
    evidence adds no support: sort by canonical serialized bytes, normalize
    duplicates away. Min-1 applies after normalization."""
    by_key = {canonical_bytes(ref): ref for ref in value}
    normalized = tuple(by_key[key] for key in sorted(by_key))
    if not normalized:
        raise ValueError("at least one evidence reference is required")
    return normalized


# --------------------------------------------------------- ledger records
class EntityRegistration(_Frozen):
    """Membership claim for one already-declared canonical identity. NO
    lifecycle: the kernel provides no supersession, no withdrawal, and no
    path that alters any embedded anchor field."""

    record_kind: Literal["entity_registration"] = "entity_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^reg_[0-9a-f]{64}$")
    anchor: EntityAnchor
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class RelationshipTypeDefinition(_Frozen):
    """One member of a type LINEAGE named by its invariant type_name.
    Supersession preserves {type_name, directionality, hierarchy_semantics,
    context_requirement}; changing any of these requires a new type name."""

    record_kind: Literal["relationship_type_definition"] = (
        "relationship_type_definition")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    type_name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    forward_label: str = Field(min_length=1)
    inverse_label: str = Field(min_length=1)
    directionality: Literal["directed"]
    source_referent_kinds: ReferentKindTuple
    target_referent_kinds: ReferentKindTuple
    self_relation_allowed: bool
    hierarchy_semantics: Literal["containment", "none"]
    context_requirement: Literal["lifecycle_view", "view_independent"]
    supersedes: str | None = Field(default=None,
                                   pattern=r"^rtd_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _containment_never_self_relating(self):
        if self.hierarchy_semantics == "containment" and self.self_relation_allowed:
            raise ValueError(
                "a containment type permitting self-relations is contradictory")
        return self


class RelationshipAssertion(_Frozen):
    """One directed, typed, evidence-backed edge claim, judged by the EXACT
    definition it cites."""

    record_kind: Literal["relationship_assertion"] = "relationship_assertion"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    type_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    source_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    target_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    evidence: Annotated[tuple[EvidenceRef, ...],
                        AfterValidator(_canonical_evidence)]
    # correction only: same LINEAGE + source + target + context
    supersedes: str | None = Field(default=None, pattern=r"^rel_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class RelationshipWithdrawal(_Frozen):
    """"No longer asserted" — never a claim the original was wrong, and
    never a claim about when it stopped being true."""

    record_kind: Literal["relationship_withdrawal"] = "relationship_withdrawal"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rwd_[0-9a-f]{64}$")
    withdraws: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


ModelRecord = Union[
    EntityRegistration, RelationshipTypeDefinition, RelationshipAssertion,
    RelationshipWithdrawal,
]


# ---------------------------------------------------------------- revision
class ModelRevision(_Frozen):
    """COMPUTED ONLY — never a file, never a ledger record; the membership
    pattern structurally excludes mrv_. Canonical order is the sorted
    record ids, never filesystem enumeration."""

    revision_id: str = Field(pattern=r"^mrv_[0-9a-f]{64}$")
    record_ids: tuple[str, ...]
    record_count: int = Field(ge=0)
    model_id: str = Field(pattern=MODEL_ID_PATTERN)

    @model_validator(mode="after")
    def _membership_consistent(self):
        ids = self.record_ids
        for record_id in ids:
            if not re.fullmatch(MODEL_RECORD_ID_PATTERN, record_id):
                raise ValueError(f"{record_id!r} is not a model record id")
        if list(ids) != sorted(set(ids)):
            raise ValueError("record_ids must be unique and sorted")
        if self.record_count != len(ids):
            raise ValueError("record_count must equal len(record_ids)")
        if self.revision_id != compute_revision_id(self.model_id, ids):
            raise ValueError("revision_id does not match the membership")
        return self


# --------------------------------------------------------------- results
def _sorted_unique(values) -> bool:
    return list(values) == sorted(set(values))


class EvidenceDisclosure(_Frozen):
    ref: EvidenceRef
    verification: Literal["verified_in_revision", "declared_reference"]


class RelationshipSummary(_Frozen):
    record_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    type_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    type_name: str
    forward_label: str
    inverse_label: str
    cited_type_current: bool
    source_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    target_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    authority: AuthorityRef
    evidence: tuple[EvidenceDisclosure, ...]
    supersedes: str | None = None
    superseded_by: tuple[str, ...] = ()
    withdrawn_by: tuple[str, ...] = ()
    active: bool
    recorded_at: UtcDatetime

    @model_validator(mode="after")
    def _lifecycle_consistent(self):
        if self.active != (not self.superseded_by and not self.withdrawn_by):
            raise ValueError(
                "active is equivalent to having no lifecycle links")
        for values, prefix in ((self.superseded_by, "rel"),
                               (self.withdrawn_by, "rwd")):
            if not _sorted_unique(values):
                raise ValueError("lifecycle links must be unique/sorted")
            for record_id in values:
                if not re.fullmatch(rf"^{prefix}_[0-9a-f]{{64}}$", record_id):
                    raise ValueError(f"{record_id!r} is not a {prefix} id")
        return self


class LineageConflict(_Frozen):
    """Competing ACTIVE successors of one predecessor — reported here
    exclusively; a second hierarchy parent candidate is never fabricated."""

    predecessor_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    competing_successor_ids: tuple[str, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def _competitors_canonical(self):
        if not _sorted_unique(self.competing_successor_ids):
            raise ValueError("competitors must be unique/sorted")
        return self


class RelationshipsResult(_Frozen):
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    direction: Literal["incoming", "outgoing", "both"]
    type_name: str | None
    context: AssertionContext
    active: tuple[RelationshipSummary, ...]
    inactive: tuple[RelationshipSummary, ...]
    lineage_conflicts: tuple[LineageConflict, ...]
    revision: ModelRevision

    @model_validator(mode="after")
    def _placement_matches_state(self):
        if any(not summary.active for summary in self.active):
            raise ValueError("inactive summary placed in the active tuple")
        if any(summary.active for summary in self.inactive):
            raise ValueError("active summary placed in the inactive tuple")
        return self


class RegistrationSummary(_Frozen):
    record_id: str = Field(pattern=r"^reg_[0-9a-f]{64}$")
    anchor: EntityAnchor
    authority: AuthorityRef
    recorded_at: UtcDatetime


class EntityResult(_Frozen):
    status: Literal["registered", "not_registered"]
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    registration: RegistrationSummary | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _registration_iff_registered(self):
        if (self.status == "registered") != (self.registration is not None):
            raise ValueError("registration is present exactly when registered")
        return self


ParentStatus = Literal[
    "resolved", "no_declared_parent", "conflicted", "cyclic", "not_registered"
]


class ParentResult(_Frozen):
    status: ParentStatus
    child_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    parent: EntityAnchor | None = None
    supporting: tuple[RelationshipSummary, ...] = ()
    candidate_parents: tuple[EntityAnchor, ...] = ()
    cycle_members: tuple[str, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _fields_match_status(self):
        if (self.status == "resolved") != (self.parent is not None):
            raise ValueError("parent is set exactly when resolved")
        if self.status == "resolved" and not self.supporting:
            raise ValueError("a resolved parent cites its supporting assertions")
        if (self.status == "conflicted") != (len(self.candidate_parents) >= 2):
            raise ValueError("candidates exist exactly when conflicted")
        if (self.status == "cyclic") != bool(self.cycle_members):
            raise ValueError("cycle members exist exactly when cyclic")
        if not _sorted_unique([a.anchor_id for a in self.candidate_parents]):
            raise ValueError("candidates must be unique/sorted")
        if not _sorted_unique(self.cycle_members):
            raise ValueError("cycle members must be unique/sorted")
        return self


class TraversalAnnotation(_Frozen):
    kind: Literal["multiple_parents"]
    candidate_parent_anchor_ids: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _canonical(self):
        if not _sorted_unique(self.candidate_parent_anchor_ids):
            raise ValueError("candidates must be unique/sorted")
        if not _sorted_unique(self.via_assertion_ids):
            raise ValueError("assertion ids must be unique/sorted")
        return self


class ChildEntry(_Frozen):
    anchor: EntityAnchor
    supporting: tuple[RelationshipSummary, ...] = Field(min_length=1)
    annotations: tuple[TraversalAnnotation, ...] = ()


class ChildrenResult(_Frozen):
    status: Literal["listed", "not_registered", "cyclic"]
    parent_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    entries: tuple[ChildEntry, ...] = ()
    cycle_members: tuple[str, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _fields_match_status(self):
        if self.status != "listed" and self.entries:
            raise ValueError("entries exist only when listed")
        if (self.status == "cyclic") != bool(self.cycle_members):
            raise ValueError("cycle members exist exactly when cyclic")
        return self


class TraversalStep(_Frozen):
    anchor: EntityAnchor
    supporting: tuple[RelationshipSummary, ...] = Field(min_length=1)
    annotations: tuple[TraversalAnnotation, ...] = ()


class TraversalBlock(_Frozen):
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    reason: Literal["conflicted", "cyclic"]


class TraversalResult(_Frozen):
    status: Literal["complete", "partial", "not_registered"]
    origin_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    steps: tuple[TraversalStep, ...] = ()
    blocked: tuple[TraversalBlock, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _partial_iff_blocked(self):
        if (self.status == "partial") != bool(self.blocked):
            raise ValueError("partial exactly when something blocked")
        if self.status == "not_registered" and (self.steps or self.blocked):
            raise ValueError("not_registered carries no steps or blocks")
        return self


class CycleReport(_Frozen):
    members: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=1)


class ParentConflictReport(_Frozen):
    child_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    candidate_parent_anchor_ids: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=2)


class HierarchyHealth(_Frozen):
    type_name: str
    view: LifecycleView | None = None
    cycles: tuple[CycleReport, ...] = ()
    parent_conflicts: tuple[ParentConflictReport, ...] = ()
    stale_type_assertions: tuple[str, ...] = ()
    revision: ModelRevision
