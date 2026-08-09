"""VS-001 observation compatibility: does this observation match what the
model says the variable's value should be?

A read-only assessment layer above VM-001. It holds no state, composes
accepted lower-layer results verbatim, and never converts, normalizes,
fills, ranks, or selects a value. Compatibility is per candidate; there is
no aggregate, current, or usable value anywhere. See README.md.
"""

from backend.observation_compatibility.contracts import (
    CandidateValueCompatibility,
    ObservationCompatibilityConfigurationError,
    ObservationCompatibilityError,
    VariableValueCompatibilityResult,
)
from backend.observation_compatibility.facade import (
    ObservationCompatibilityQueries,
)

__all__ = [
    "CandidateValueCompatibility",
    "ObservationCompatibilityConfigurationError",
    "ObservationCompatibilityError",
    "ObservationCompatibilityQueries",
    "VariableValueCompatibilityResult",
]
