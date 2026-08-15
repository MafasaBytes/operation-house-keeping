"""Deterministic, exact-locator source-property interpretation."""

from datetime import UTC, datetime

from backend.identity_binding.resolver import membership
from backend.source_interpretation.canonical import canonical_sort_key
from backend.source_interpretation.contracts import (
    DimensionInterpretationResolution, InterpretationAssertionSummary,
    PropertyInterpretationResult)
from backend.source_interpretation.errors import InterpretationResolutionError
from backend.source_interpretation.store import LoadedInterpretationSet
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

_DIMENSIONS = ("quantity_kind", "observation_role", "unit")


def _require_aware(at):
    if (not isinstance(at, datetime) or at.tzinfo is None
            or at.tzinfo.utcoffset(at) is None):
        raise InterpretationResolutionError(
            "INTERPRETATION_NAIVE_AT",
            "interpretation time must be a timezone-aware datetime")
    return at.astimezone(UTC)


def _require_locators(subject, prop):
    try:
        if not isinstance(subject, SourceSubjectRef) or not isinstance(
                prop, SourcePropertyRef):
            raise TypeError
        subject = SourceSubjectRef.model_validate(
            subject.model_dump(mode="python", warnings=False))
        prop = SourcePropertyRef.model_validate(
            prop.model_dump(mode="python", warnings=False))
        return subject, prop
    except (AttributeError, TypeError, ValueError, Warning) as error:
        raise InterpretationResolutionError(
            "INTERPRETATION_LOCATOR_INVALID",
            "resolution requires valid source subject and property references"
        ) from error


class _Assessment:
    def __init__(self, loaded, matching, dimension, at):
        self.dimension = dimension
        self.summaries = []
        self.in_bodies = {}
        self.unknown_bodies = {}
        for assertion in sorted(matching, key=lambda item: item.record_id):
            record_id = assertion.record_id
            superseded_by = loaded.interpretation_superseded_by[record_id]
            retracted_by = loaded.retracted_by[record_id]
            active = not superseded_by and not retracted_by
            effective = loaded.effective_applies[record_id]
            member = membership(effective, at)
            self.summaries.append(InterpretationAssertionSummary(
                record_id=record_id, dimension=dimension,
                interpretation=assertion.interpretation,
                authority=assertion.authority,
                declared_applies=assertion.applies,
                effective_applies=effective,
                closure_records=loaded.closure_records[record_id],
                superseded_by=superseded_by, retracted_by=retracted_by,
                active=active, membership_at=member,
                recorded_at=assertion.recorded_at))
            key = canonical_sort_key(assertion.interpretation)
            if active and member == "in":
                self.in_bodies[key] = assertion.interpretation
            elif active and member == "unknown":
                self.unknown_bodies[key] = assertion.interpretation
        if not matching:
            self.status = "not_declared"
        elif not any(summary.active for summary in self.summaries):
            self.status = self._inactive_status()
        else:
            ins, unknowns = set(self.in_bodies), set(self.unknown_bodies)
            if not ins and not unknowns:
                self.status = "outside_applicability"
            elif len(ins) >= 2:
                self.status = "conflicted"
            elif len(ins) == 1:
                self.status = "interpreted" if unknowns <= ins else "ambiguous"
            elif len(unknowns) == 1:
                self.status = "applicability_unknown"
            else:
                self.status = "ambiguous"

    def _inactive_status(self):
        kinds = set()
        for summary in self.summaries:
            if summary.superseded_by and summary.retracted_by:
                return "inactive"
            kinds.add("superseded" if summary.superseded_by else "retracted")
        return kinds.pop() if len(kinds) == 1 else "inactive"

    def candidates(self):
        if self.status in ("applicability_unknown", "ambiguous"):
            values = {**self.in_bodies, **self.unknown_bodies}
        elif self.status == "conflicted":
            values = self.in_bodies
        else:
            return ()
        return tuple(values[key] for key in sorted(values))

    def basis(self):
        if self.status != "interpreted":
            return None
        positive_key = next(iter(self.in_bodies))
        declared = all(
            summary.effective_applies.start_boundary.kind == "declared"
            and summary.effective_applies.end_boundary.kind == "declared"
            for summary in self.summaries
            if summary.active and summary.membership_at == "in"
            and canonical_sort_key(summary.interpretation) == positive_key)
        return "declared_interval" if declared else "includes_unbounded_claim"

    def result(self):
        interpretation = (next(iter(self.in_bodies.values()))
                          if self.status == "interpreted" else None)
        return DimensionInterpretationResolution(
            dimension=self.dimension, status=self.status,
            interpretation=interpretation,
            candidate_interpretations=self.candidates(),
            via_assertions=tuple(self.summaries),
            applicability_basis=self.basis())


class InterpretationResolver:
    def __init__(self, loaded: LoadedInterpretationSet) -> None:
        if not isinstance(loaded, LoadedInterpretationSet):
            raise InterpretationResolutionError(
                "INTERPRETATION_RECORD_INVALID",
                "resolver requires a validated interpretation set")
        self.loaded = loaded

    def resolve_property_interpretations(
            self, subject: SourceSubjectRef, prop: SourcePropertyRef,
            at: datetime | None = None) -> PropertyInterpretationResult:
        at = _require_aware(at)
        subject, prop = _require_locators(subject, prop)
        results = {}
        for dimension in _DIMENSIONS:
            matching = [
                record for record in self.loaded.interpretations.values()
                if record.subject == subject and record.property == prop
                and record.interpretation.dimension == dimension]
            results[dimension] = _Assessment(
                self.loaded, matching, dimension, at).result()
        return PropertyInterpretationResult(
            subject=subject, property=prop, at=at,
            quantity_kind=results["quantity_kind"],
            observation_role=results["observation_role"],
            unit=results["unit"], revision=self.loaded.revision)
