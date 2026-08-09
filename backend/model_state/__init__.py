"""VM-001 model_state: the read-only bound model-state query facade.

Holds NO state of its own — a projection facade joining a loaded model
revision (knowledge context) to identity-bound temporal evidence at a
required receipt-axis cutoff, by composition of injected accepted query
objects. See README.md for the dependency direction and the
latest-per-locator limitation, stated verbatim in `contracts`.
"""

from backend.model_state.contracts import (
    AttachmentStatus,
    CandidateObservation,
    ModelStateConfigurationError,
    ModelStateError,
    ModelStateQueryError,
    SourceSelector,
    VariableStateResult,
)
from backend.model_state.facade import ModelStateQueries

__all__ = [
    "AttachmentStatus",
    "CandidateObservation",
    "ModelStateConfigurationError",
    "ModelStateError",
    "ModelStateQueries",
    "ModelStateQueryError",
    "SourceSelector",
    "VariableStateResult",
]
