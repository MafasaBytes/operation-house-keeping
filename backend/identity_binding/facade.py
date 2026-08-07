"""IB-001 bound temporal facade.

A read-only join: it calls the accepted `TemporalQueries` unchanged and
attaches a resolution to each returned object. The TS-001 result is
carried VERBATIM — never copied field-by-field, never mutated — and every
resolution status still returns the underlying observation: identity
limbo never hides evidence. Resolutions are computed at each
observation's own `received_at`, never at `as_of` and never at the query
execution clock, so one history honestly spans a replacement boundary.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.identity_binding.contracts import ResolutionResult
from backend.identity_binding.resolver import BindingResolver
from backend.temporal_state.contracts import (
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalOccurrence,
)
from backend.temporal_state.queries import LatestObservedState, TemporalQueries


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class BoundLatestObserved(_Frozen):
    observed: LatestObservedState
    resolution: ResolutionResult


class BoundOccurrence(_Frozen):
    occurrence: TemporalOccurrence
    resolution: ResolutionResult


class BoundTemporalQueries:
    def __init__(self, resolver: BindingResolver,
                 temporal: TemporalQueries) -> None:
        self.resolver = resolver
        self.temporal = temporal

    def latest_observed(self, subject: SourceSubjectRef,
                        prop: SourcePropertyRef,
                        as_of: datetime) -> BoundLatestObserved | None:
        observed = self.temporal.latest_observed(subject, prop, as_of)
        if observed is None:
            return None
        resolution = self.resolver.resolve_property(
            subject, prop, at=observed.occurrence.received_at)
        return BoundLatestObserved(observed=observed, resolution=resolution)

    def history(self, subject: SourceSubjectRef,
                prop: SourcePropertyRef) -> list[BoundOccurrence]:
        return [
            BoundOccurrence(
                occurrence=occurrence,
                resolution=self.resolver.resolve_property(
                    subject, prop, at=occurrence.received_at))
            for occurrence in self.temporal.history(subject, prop)
        ]
