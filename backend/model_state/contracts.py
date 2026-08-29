"""VM-001 model_state result contracts.

Multidimensional, never flattened: model membership, requested entity,
binding discovery, selector declaration, observation availability,
per-candidate identity resolution, per-candidate model attachment, and
selection cardinality are independent questions with independent answers.
``observation_availability == "observed"`` asserts ONLY that source
evidence exists — attachment to the requested model variable is claimed
exclusively by a candidate's ``attachment == "attached"``. There is no
aggregate value field and no rollup: values live only inside verbatim
per-candidate occurrences.

Latest-per-locator limitation (accepted): each candidate reports the
locator's most recent observation at or before the cutoff, forward-
resolved at its own ``received_at``. When that occurrence resolves
elsewhere, the result means "no latest candidate observation attachable
to the requested variable" — never "no observation ever". The historical
last observation that once resolved to this variable belongs to a later,
explicitly named history query.
"""

from datetime import UTC
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    TypeAdapter,
    model_validator,
)

from backend.identity_binding.contracts import (
    BindingRevision,
    DeclaredLocatorEntry,
)
from backend.identity_binding.facade import BoundLatestObserved
from backend.model_kernel import (
    AssertionContext,
    EntityRegistration,
    ModelRevision,
    VariablePortAssociationResult,
    VariableRegistration,
)
from backend.system_identity import (
    ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
    VariableAnchor,
)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]


# ---------------------------------------------------------------- errors
class ModelStateError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class ModelStateConfigurationError(ModelStateError):
    """Invalid composition input (wrong object kinds injected)."""


class ModelStateQueryError(ModelStateError):
    """Contract misuse at the query boundary. Absence, limbo, and
    disagreement are statuses, never exceptions."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceSelector(_Frozen):
    """An explicit locator to inspect through the accepted forward
    pipeline. Selecting never creates or implies a binding."""

    subject: SourceSubjectRef
    property: SourcePropertyRef


AttachmentStatus = Literal[
    "attached",
    "not_attachable_variable_unregistered",
    "not_attachable_anchor_divergent",
    "not_attachable_resolution_mismatch",
    "not_attachable_resolution_nonpositive",
    "not_evaluated",
]


class CandidateObservation(_Frozen):
    """One queried locator: its declarative discovery context (verbatim
    from identity_binding — never copied, truncated, reinterpreted, or
    reconstructed here), the bound temporal result (verbatim), and the
    per-candidate attachment verdict."""

    subject: SourceSubjectRef
    property: SourcePropertyRef
    origin: Literal["declared_binding", "explicit_selector"]
    declaration: DeclaredLocatorEntry | None = None
    declared_via_assertion_ids: tuple[str, ...] = ()
    bound: BoundLatestObserved | None = None
    attachment: AttachmentStatus

    @model_validator(mode="after")
    def _declaration_consistent(self):
        ids = self.declared_via_assertion_ids
        if list(ids) != sorted(set(ids)):
            raise ValueError("declared_via ids must be unique and sorted")
        if self.declaration is None:
            if ids:
                raise ValueError(
                    "declared_via ids require the carried declaration")
            if self.origin != "explicit_selector":
                raise ValueError(
                    "a discovery candidate always carries its declaration")
        else:
            known = {summary.record_id
                     for summary in self.declaration.assertion_summaries}
            if not set(ids) <= known:
                raise ValueError(
                    "declared_via ids must come from the carried declaration")
        if (self.attachment == "not_evaluated") != (self.bound is None):
            raise ValueError(
                "not_evaluated attachment exactly when nothing was observed")
        return self


class VariableStateResult(_Frozen):
    # request echo
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    as_of: UtcDatetime
    requested_entity_anchor_id: str | None = Field(
        default=None, pattern=ENTITY_ANCHOR_ID_PATTERN)

    # dimensions
    model_membership: Literal["registered", "not_registered"]
    requested_entity_membership: Literal["registered", "not_registered",
                                         "not_supplied"]
    requested_entity_agreement: Literal["matches_owner", "differs_from_owner",
                                        "owner_unavailable", "not_supplied"]
    binding_discovery: Literal["declared_candidates", "no_declared_candidates",
                               "anchor_unknown_to_binding_set",
                               "explicit_selector"]
    selector_declaration: Literal["ever_declared_for_requested_variable",
                                  "ever_declared_for_other_variable",
                                  "undeclared", "not_applicable"]
    observation_availability: Literal["observed", "none_before_cutoff",
                                      "not_evaluated"]
    selection: Literal["none", "single", "multiple", "explicit"]

    # verbatim composition
    variable_registration: VariableRegistration | None = None
    owner_registration: EntityRegistration | None = None
    requested_entity_registration: EntityRegistration | None = None
    model_revision: ModelRevision
    binding_revision: BindingRevision
    binding_declared_anchor: VariableAnchor | None = None
    anchor_agreement: Literal["exact", "divergent",
                              "binding_declaration_absent",
                              "model_registration_absent"]
    divergent_anchor_fields: tuple[str, ...] = ()
    declared_locator_count: Annotated[StrictInt, Field(ge=0)]
    candidates: tuple[CandidateObservation, ...] = ()

    @model_validator(mode="after")
    def _dimensions_consistent(self):
        def fail(message):
            raise ValueError(message)

        binding_record_ids = set(self.binding_revision.record_ids)
        registered = self.model_membership == "registered"
        # 1: membership <=> registrations <=> agreement basis
        if registered != (self.variable_registration is not None):
            fail("variable_registration present exactly when registered")
        if registered != (self.owner_registration is not None):
            fail("owner_registration present exactly when registered")
        if (not registered) != (
                self.anchor_agreement == "model_registration_absent"):
            fail("model_registration_absent exactly when not registered")
        # 2: ownership coherence + request echo
        if registered:
            anchor = self.variable_registration.anchor
            if anchor.anchor_id != self.variable_anchor_id:
                fail("the carried registration must be the requested one")
            if self.owner_registration.anchor.anchor_id != (
                    anchor.entity_anchor_id):
                fail("owner_registration must be the registration's owner")
        # 3: requested entity trio
        supplied = self.requested_entity_anchor_id is not None
        if supplied == (self.requested_entity_membership == "not_supplied"):
            fail("requested_entity_membership follows the supplied id")
        if supplied == (self.requested_entity_agreement == "not_supplied"):
            fail("requested_entity_agreement follows the supplied id")
        if (self.requested_entity_membership == "registered") != (
                self.requested_entity_registration is not None):
            fail("requested_entity_registration present exactly when the "
                 "supplied entity is registered")
        if (self.requested_entity_registration is not None
                and self.requested_entity_registration.anchor.anchor_id !=
                self.requested_entity_anchor_id):
            fail("requested_entity_registration must be the requested entity")
        if supplied:
            if (self.requested_entity_agreement == "owner_unavailable") != (
                    not registered):
                fail("owner_unavailable exactly when the variable is "
                     "unregistered")
            if registered:
                matches = (self.requested_entity_anchor_id
                           == self.variable_registration.anchor
                           .entity_anchor_id)
                expected = "matches_owner" if matches else "differs_from_owner"
                if self.requested_entity_agreement != expected:
                    fail("requested_entity_agreement must state the actual "
                         "ownership comparison")
        # 4: mode coherence
        explicit = self.binding_discovery == "explicit_selector"
        if explicit != (self.selection == "explicit"):
            fail("explicit selection exactly in selector mode")
        if explicit != (self.selector_declaration != "not_applicable"):
            fail("selector_declaration exactly in selector mode")
        if explicit:
            if len(self.candidates) != 1 or (
                    self.candidates[0].origin != "explicit_selector"):
                fail("selector mode carries exactly the selector candidate")
            declaration = self.candidates[0].declaration
            expected_selector = (
                "undeclared" if declaration is None else
                "ever_declared_for_requested_variable" if any(
                    summary.target_anchor_id == self.variable_anchor_id
                    for summary in declaration.assertion_summaries) else
                "ever_declared_for_other_variable")
            if self.selector_declaration != expected_selector:
                fail("selector_declaration must follow the carried "
                     "declaration targets")
        else:
            if any(candidate.origin != "declared_binding"
                   for candidate in self.candidates):
                fail("discovery candidates are declared bindings")
            if self.declared_locator_count != len(self.candidates):
                fail("discovery queries every declared locator")
            unknown = self.binding_discovery == "anchor_unknown_to_binding_set"
            if unknown != (self.binding_declared_anchor is None):
                fail("anchor_unknown exactly when no declaration exists")
            expected_discovery = (
                "anchor_unknown_to_binding_set"
                if self.binding_declared_anchor is None else
                "declared_candidates" if self.candidates else
                "no_declared_candidates")
            if self.binding_discovery != expected_discovery:
                fail("binding_discovery must follow anchor and candidate "
                     "disclosure")
            expected_selection = ("none" if not self.candidates else
                                  "single" if len(self.candidates) == 1
                                  else "multiple")
            if self.selection != expected_selection:
                fail("selection counts the queried candidate locators")
        # 5: anchor agreement coherence
        if self.anchor_agreement in ("exact", "divergent") and (
                self.binding_declared_anchor is None):
            fail("anchor comparison requires the declared anchor")
        if (self.binding_declared_anchor is not None
                and self.binding_declared_anchor.anchor_id !=
                self.variable_anchor_id):
            fail("binding_declared_anchor must be the requested variable")
        if self.anchor_agreement == "binding_declaration_absent" and (
                not registered or self.binding_declared_anchor is not None):
            fail("binding_declaration_absent: registered, no declaration")
        if (self.anchor_agreement == "divergent") != bool(
                self.divergent_anchor_fields):
            fail("divergent_anchor_fields exactly when divergent")
        if registered and self.binding_declared_anchor is not None:
            anchor = self.variable_registration.anchor
            diffs = tuple(sorted(
                name for name in type(anchor).model_fields
                if getattr(anchor, name) != getattr(
                    self.binding_declared_anchor, name)))
            expected = "exact" if not diffs else "divergent"
            if self.anchor_agreement != expected:
                fail("anchor_agreement must state the actual comparison")
            if self.divergent_anchor_fields != diffs:
                fail("divergent_anchor_fields must name the exact "
                     "differing fields")
        # 6: availability
        bound_any = any(candidate.bound is not None
                        for candidate in self.candidates)
        expected_availability = (
            "not_evaluated" if not self.candidates
            else "observed" if bound_any else "none_before_cutoff")
        if self.observation_availability != expected_availability:
            fail("observation_availability states evidence existence only")
        # 8-10: per-candidate coherence
        for candidate in self.candidates:
            if candidate.declaration is not None:
                if (candidate.declaration.subject != candidate.subject
                        or candidate.declaration.property !=
                        candidate.property):
                    fail("candidate locator must equal its declaration")
                for summary in candidate.declaration.assertion_summaries:
                    lifecycle_ids = (
                        *((summary.supersedes,) if summary.supersedes else ()),
                        *summary.superseded_by,
                        *summary.retracted_by,
                        *summary.closure_records,
                    )
                    if ({summary.record_id, *lifecycle_ids}
                            - binding_record_ids):
                        fail("candidate binding citations must belong to the "
                             "carried binding revision")
                expected_ids = tuple(sorted(
                    summary.record_id
                    for summary in candidate.declaration.assertion_summaries
                    if summary.target_anchor_id == self.variable_anchor_id))
                if candidate.declared_via_assertion_ids != expected_ids:
                    fail("declared_via ids must be exactly the carried "
                         "declaration's assertions targeting the requested "
                         "variable")
                if (candidate.origin == "declared_binding"
                        and not expected_ids):
                    fail("a discovery candidate must cite an assertion "
                         "targeting the requested variable")
            if candidate.bound is None:
                continue
            observed = candidate.bound.observed
            resolution = candidate.bound.resolution
            if observed.as_of != self.as_of:
                fail("candidate cutoff must equal the requested cutoff")
            if observed.occurrence.received_at > observed.as_of:
                fail("candidate occurrence must not postdate its cutoff")
            expected_staleness = (
                observed.as_of - observed.occurrence.received_at
            ).total_seconds()
            if observed.staleness_seconds != expected_staleness:
                fail("candidate staleness must derive from its cutoff")
            if (observed.occurrence.subject != candidate.subject
                    or observed.occurrence.property != candidate.property
                    or resolution.locator_subject != candidate.subject
                    or resolution.locator_property != candidate.property):
                fail("candidate locator must equal observation and resolution")
            if resolution.revision != self.binding_revision:
                fail("one binding revision governs discovery and every "
                     "candidate resolution")
            resolution_ids = set()
            for summary in resolution.via_assertions:
                resolution_ids.update((
                    summary.record_id,
                    *summary.superseded_by,
                    *summary.retracted_by,
                    *summary.closure_records,
                ))
            if resolution.subject_context is not None:
                resolution_ids.update(
                    resolution.subject_context.via_assertion_ids)
            if resolution_ids - binding_record_ids:
                fail("resolution citations must belong to the carried "
                     "binding revision")
            positive = resolution.status == "bound"
            target = (resolution.resolved_target.anchor_id
                      if positive else None)
            if (target == self.variable_anchor_id
                    and resolution.resolved_target !=
                    self.binding_declared_anchor):
                fail("resolved target must equal the carried binding anchor")
            if not positive:
                expected_attachment = "not_attachable_resolution_nonpositive"
            elif target != self.variable_anchor_id:
                expected_attachment = "not_attachable_resolution_mismatch"
            elif not registered:
                expected_attachment = "not_attachable_variable_unregistered"
            elif self.anchor_agreement == "divergent":
                expected_attachment = "not_attachable_anchor_divergent"
            elif self.anchor_agreement == "exact":
                expected_attachment = "attached"
            else:
                fail("a resolution bound to the requested variable cannot "
                     "exist without its binding declaration")
            if candidate.attachment != expected_attachment:
                fail("attachment must follow the deterministic precedence")
        return self


AssociatedPortVariableStateStatus = Literal[
    "endpoint_not_admitted",
    "association_not_declared",
    "association_conflicted",
    "association_inactive",
    "associated",
]

_ASSERTION_CONTEXT = TypeAdapter(AssertionContext)


def _rebuild_context(value) -> AssertionContext:
    payload = (value.model_dump(mode="python", warnings=False)
               if hasattr(value, "model_dump") else value)
    return _ASSERTION_CONTEXT.validate_python(payload)


def _status_from_association(
        association: VariablePortAssociationResult
) -> AssociatedPortVariableStateStatus:
    if (association.endpoint_status != "both_registered"
            or association.owner_alignment != "same_owner"):
        return "endpoint_not_admitted"
    if association.conclusion == "not_declared":
        return "association_not_declared"
    if association.conclusion == "inactive":
        return "association_inactive"
    if (association.conclusion == "asserted"
            and association.lineage_summary == "conflicted"):
        return "association_conflicted"
    if (association.conclusion == "asserted"
            and association.lineage_summary == "healthy"):
        return "associated"
    raise ValueError("association carries an impossible lifecycle result")


class AssociatedPortVariableStateResult(BaseModel):
    """A revision-relative association beside independently computed state.

    The temporal evidence remains attached only to the variable.  Carrying it
    beside a port association does not assert that an observation occurred at,
    originated from, passed through, or otherwise describes the port.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    as_of: UtcDatetime
    status: AssociatedPortVariableStateStatus
    association: VariablePortAssociationResult
    variable_state: VariableStateResult

    @model_validator(mode="before")
    @classmethod
    def _reconstruct_inputs(cls, value):
        # Nested kernel rows carry private dereference-only material handles.
        # Convert all supplied Pydantic instances to public serialized field
        # content before field validation so neither private state nor an
        # already-constructed instance can cross this trust boundary.
        if isinstance(value, BaseModel):
            payload = value.model_dump(mode="python", warnings=False)
        elif isinstance(value, dict):
            payload = dict(value)
        else:
            return value
        for name in ("context", "association", "variable_state"):
            nested = payload.get(name)
            if hasattr(nested, "model_dump"):
                payload[name] = nested.model_dump(
                    mode="python", warnings=False)
        return payload

    @model_validator(mode="after")
    def _authoritative(self):
        # Reconstruct both public nested results from their serialized field
        # content.  Existing Pydantic instances, including model_construct and
        # model_copy forgeries, are never trusted at this outer boundary.
        context = _rebuild_context(self.context)
        association = VariablePortAssociationResult.model_validate(
            self.association.model_dump(mode="python", warnings=False))
        variable_state = VariableStateResult.model_validate(
            self.variable_state.model_dump(mode="python", warnings=False))
        object.__setattr__(self, "context", context)
        object.__setattr__(self, "association", association)
        object.__setattr__(self, "variable_state", variable_state)

        if (association.variable_anchor_id != self.variable_anchor_id
                or association.port_anchor_id != self.port_anchor_id
                or association.context != context):
            raise ValueError(
                "association request echo does not match the composition")
        if (variable_state.variable_anchor_id != self.variable_anchor_id
                or variable_state.as_of != self.as_of):
            raise ValueError(
                "variable-state request echo does not match the composition")
        if association.material.revision != variable_state.model_revision:
            raise ValueError(
                "association and variable state use different model revisions")
        if association.variable_registration != (
                variable_state.variable_registration):
            raise ValueError(
                "association and state carry different variable registration")
        if association.variable_owner_registration != (
                variable_state.owner_registration):
            raise ValueError(
                "association and state carry different variable owner")
        if self.status != _status_from_association(association):
            raise ValueError("associated-port state status is forged")
        return self
