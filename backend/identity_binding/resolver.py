"""IB-001 deterministic resolver.

A total function of (revision, locator, at): three-valued applicability
membership feeding the accepted eight-case algorithm. `bound` requires
positive establishment by declared or explicitly unbounded boundaries; an
OUT assertion is proven not applicable and never competes or blocks; a
differing-target UNKNOWN prevents `bound`; conflicts and ambiguity are
never resolved by recency, `recorded_at`, or authority rank. There is no
implicit clock and no interpretation mode.
"""

import re
from datetime import UTC, datetime

from backend.identity_binding.contracts import (
    AppliesScope,
    DeclaredBindingSummary,
    DeclaredLocatorEntry,
    DeclaredPropertyLocatorsResult,
    AssertionSummary,
    BindingAssertion,
    BindingResolutionError,
    BindingRevision,
    Membership,
    ResolutionResult,
    SubjectResolutionContext,
)
from backend.identity_binding.store import LoadedBindingSet
from backend.system_identity import (
    VARIABLE_ANCHOR_ID_PATTERN,
    EntityAnchor,
    VariableAnchor,
)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef


def membership(scope: AppliesScope, at: datetime) -> Membership:
    """Three-valued membership of `at` in a half-open effective scope."""
    start, end = scope.start_boundary, scope.end_boundary

    if start.kind == "declared":
        started = "yes" if at >= start.at else "no"
    elif start.kind == "unbounded":
        started = "yes"
    else:
        started = "unknown"

    if end.kind == "declared":
        not_ended = "yes" if at < end.at else "no"  # boundary → successor
    elif end.kind == "unbounded":
        not_ended = "yes"
    else:
        not_ended = "unknown"

    if started == "no" or not_ended == "no":
        return "out"  # one declared side suffices to exclude
    if started == "yes" and not_ended == "yes":
        return "in"
    return "unknown"


def _require_aware(at: datetime | None) -> datetime:
    """Missing, None, non-datetime, and naive resolution times all fail
    through the same typed contract — never TypeError/AttributeError."""
    if (not isinstance(at, datetime) or at.tzinfo is None
            or at.tzinfo.utcoffset(at) is None):
        raise BindingResolutionError(
            "BINDING_NAIVE_AT",
            "resolution time must be a timezone-aware datetime")
    return at.astimezone(UTC)


class _Assessment:
    """One locator's assertions assessed at one instant."""

    def __init__(self, loaded: LoadedBindingSet,
                 matching: list[BindingAssertion], at: datetime) -> None:
        self.summaries: list[AssertionSummary] = []
        self.status = "unbound"
        self.in_targets: dict[str, list[str]] = {}
        self.unknown_targets: dict[str, list[str]] = {}

        for assertion in sorted(matching, key=lambda a: a.record_id):
            record_id = assertion.record_id
            superseded_by = loaded.superseded_by[record_id]
            retracted_by = loaded.retracted_by[record_id]
            active = not superseded_by and not retracted_by
            effective = loaded.effective_applies[record_id]
            member = membership(effective, at)
            self.summaries.append(AssertionSummary(
                record_id=record_id,
                target_anchor_id=assertion.target_anchor_id,
                authority=assertion.authority,
                declared_applies=assertion.applies,
                effective_applies=effective,
                closure_records=loaded.closure_records[record_id],
                superseded_by=superseded_by, retracted_by=retracted_by,
                active=active, membership_at=member,
                recorded_at=assertion.recorded_at))
            if active and member == "in":
                self.in_targets.setdefault(
                    assertion.target_anchor_id, []).append(record_id)
            elif active and member == "unknown":
                self.unknown_targets.setdefault(
                    assertion.target_anchor_id, []).append(record_id)

        if not matching:
            self.status = "unbound"
            return
        actives = [s for s in self.summaries if s.active]
        if not actives:
            self.status = self._inactive_status()
            return
        in_targets = set(self.in_targets)
        unknown_targets = set(self.unknown_targets)
        if not in_targets and not unknown_targets:
            self.status = "outside_applicability"
        elif len(in_targets) >= 2:
            self.status = "conflicted"
        elif len(in_targets) == 1:
            self.status = ("bound" if unknown_targets <= in_targets
                           else "ambiguous")
        elif len(unknown_targets) == 1:
            self.status = "applicability_unknown"
        else:
            self.status = "ambiguous"

    def _inactive_status(self) -> str:
        # Independent lifecycle facts, no invented precedence. (A pure
        # "superseded" set is structurally rare: a finite same-locator
        # supersession chain ends in an active or retracted assertion —
        # the rule is still honored as specified.)
        kinds = set()
        for summary in self.summaries:
            superseded = bool(summary.superseded_by)
            retracted = bool(summary.retracted_by)
            if superseded and retracted:
                return "inactive"
            kinds.add("superseded" if superseded else "retracted")
        return kinds.pop() if len(kinds) == 1 else "inactive"

    def positive_target_id(self) -> str | None:
        return next(iter(self.in_targets)) if len(self.in_targets) == 1 else None

    def candidate_ids(self) -> tuple[str, ...]:
        if self.status in ("applicability_unknown", "ambiguous"):
            return tuple(sorted({*self.in_targets, *self.unknown_targets}))
        if self.status == "conflicted":
            return tuple(sorted(self.in_targets))
        return ()

    def cited_ids(self) -> tuple[str, ...]:
        return tuple(s.record_id for s in self.summaries)

    def basis(self) -> str | None:
        if self.status != "bound":
            return None
        target = self.positive_target_id()
        declared_only = all(
            s.effective_applies.start_boundary.kind == "declared"
            and s.effective_applies.end_boundary.kind == "declared"
            for s in self.summaries
            if s.record_id in self.in_targets[target])
        return "declared_interval" if declared_only else "includes_unbounded_claim"


class BindingResolver:
    def __init__(self, loaded: LoadedBindingSet) -> None:
        self.loaded = loaded

    # -- public ------------------------------------------------------------

    def resolve_subject(self, subject: SourceSubjectRef,
                        at: datetime | None = None) -> ResolutionResult:
        # `at` defaults to None solely so missing input is rejected
        # through the typed contract; there is no implicit clock.
        at = _require_aware(at)
        assessment = self._assess("subject", subject, None, at)
        return self._result(assessment, subject, None, subject_context=None)

    def resolve_property(self, subject: SourceSubjectRef,
                         prop: SourcePropertyRef,
                         at: datetime | None = None) -> ResolutionResult:
        at = _require_aware(at)
        assessment = self._assess("property", subject, prop, at)
        subject_assessment = self._assess("subject", subject, None, at)
        context = SubjectResolutionContext(
            status=subject_assessment.status,
            resolved_entity=(
                self._anchor(subject_assessment.positive_target_id())
                if subject_assessment.status == "bound" else None),
            candidate_entities=tuple(
                self._anchor(anchor_id)
                for anchor_id in subject_assessment.candidate_ids()),
            via_assertion_ids=subject_assessment.cited_ids())

        # Cross-level consistency fires only when BOTH sides are
        # positively established; an unbound/unknown/ambiguous subject
        # cannot prove an inconsistency.
        if assessment.status == "bound" and context.status == "bound":
            variable = self._anchor(assessment.positive_target_id())
            if variable.entity_anchor_id != context.resolved_entity.anchor_id:
                return ResolutionResult(
                    status="conflicted", locator_subject=subject,
                    locator_property=prop, resolved_target=None,
                    candidate_targets=(variable,),
                    via_assertions=tuple(assessment.summaries),
                    applicability_basis=None,
                    revision=self._revision(), subject_context=context,
                    detail="the bound variable belongs to "
                    f"{variable.entity_anchor_id}, but the subject is bound "
                    f"to {context.resolved_entity.anchor_id}")
        return self._result(assessment, subject, prop, subject_context=context)

    def declared_property_locators(
            self, target_anchor_id: str) -> DeclaredPropertyLocatorsResult:
        """Reverse discovery: every locator EVER declared for this variable
        anchor in the loaded revision. Time-free by design — no `at`
        parameter exists; lifecycle is disclosed per assertion and
        applicability is decided only by forward resolution at each
        occurrence's received_at."""
        if not isinstance(target_anchor_id, str) or not re.fullmatch(
                VARIABLE_ANCHOR_ID_PATTERN, target_anchor_id):
            raise BindingResolutionError(
                "BINDING_ANCHOR_ID_INVALID",
                f"{target_anchor_id!r} is not a canonical variable anchor id")
        by_locator: dict[tuple, list[BindingAssertion]] = {}
        for candidate in self.loaded.assertions.values():
            if candidate.binding_kind != "property":
                continue
            key = (candidate.subject.source_id, candidate.subject.adapter_id,
                   candidate.subject.subject_identifier,
                   candidate.property.extraction_route,
                   candidate.property.item_key,
                   candidate.property.json_pointer)
            by_locator.setdefault(key, []).append(candidate)
        entries = []
        for key in sorted(by_locator):
            group = by_locator[key]
            if not any(candidate.target_anchor_id == target_anchor_id
                       for candidate in group):
                continue
            entries.append(DeclaredLocatorEntry(
                subject=group[0].subject, property=group[0].property,
                assertion_summaries=tuple(
                    self._declared_summary(candidate) for candidate in
                    sorted(group, key=lambda a: a.record_id))))
        if entries:
            status = "declared"
        elif target_anchor_id in self.loaded.anchors_by_id:
            status = "none_declared"
        else:
            status = "anchor_not_declared"
        return DeclaredPropertyLocatorsResult(
            status=status, target_anchor_id=target_anchor_id,
            locators=tuple(entries), revision=self.loaded.revision)

    def _declared_summary(self, candidate) -> DeclaredBindingSummary:
        record_id = candidate.record_id
        superseded_by = self.loaded.superseded_by[record_id]
        retracted_by = self.loaded.retracted_by[record_id]
        closures = self.loaded.closure_records[record_id]
        return DeclaredBindingSummary(
            record_id=record_id,
            target_anchor_id=candidate.target_anchor_id,
            authority=candidate.authority, recorded_at=candidate.recorded_at,
            declared_applies=candidate.applies,
            effective_applies=self.loaded.effective_applies[record_id],
            supersedes=candidate.supersedes, superseded_by=superseded_by,
            retracted_by=retracted_by, closure_records=closures,
            lifecycle_flags=tuple(sorted(
                flag for flag, links in (("closed", closures),
                                         ("retracted", retracted_by),
                                         ("superseded", superseded_by))
                if links)))

    # -- internals ----------------------------------------------------------

    def _assess(self, binding_kind, subject, prop, at) -> _Assessment:
        matching = [
            a for a in self.loaded.assertions.values()
            if a.binding_kind == binding_kind and a.subject == subject
            and a.property == prop
        ]
        return _Assessment(self.loaded, matching, at)

    def _anchor(self, anchor_id) -> EntityAnchor | VariableAnchor:
        return self.loaded.anchors_by_id[anchor_id]

    def _revision(self) -> BindingRevision:
        return self.loaded.revision

    def _result(self, assessment, subject, prop,
                subject_context) -> ResolutionResult:
        resolved = (self._anchor(assessment.positive_target_id())
                    if assessment.status == "bound" else None)
        return ResolutionResult(
            status=assessment.status, locator_subject=subject,
            locator_property=prop, resolved_target=resolved,
            candidate_targets=tuple(self._anchor(anchor_id)
                                    for anchor_id in assessment.candidate_ids()),
            via_assertions=tuple(assessment.summaries),
            applicability_basis=assessment.basis(),
            revision=self._revision(), subject_context=subject_context)
