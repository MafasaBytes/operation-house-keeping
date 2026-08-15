"""Read-only composition of declared model and source-property semantics."""

from backend.semantic_compatibility.contracts import (
    CandidateSemanticCompatibility, SemanticCompatibilityConfigurationError,
    SemanticCompatibilityError, VariableSemanticCompatibilityResult,
    derive_semantic_findings)
from backend.semantic_compatibility.facade import SemanticCompatibilityQueries

__all__ = [
    "CandidateSemanticCompatibility", "SemanticCompatibilityConfigurationError",
    "SemanticCompatibilityError", "SemanticCompatibilityQueries",
    "VariableSemanticCompatibilityResult", "derive_semantic_findings"]

