"""CN-001 Slice B: read-only, composition-only constraint evaluation.

The supported import surface: the typed error tree, the observed-decimal
contract and its bounded parser, the result contracts with their
authoritative validators, and the read-only facade. Derivation helpers are
re-exported so callers and tests can reference the single authoritative
per-candidate derivation.
"""

from backend.constraint_evaluation.contracts import (
    BoundaryAssessment,
    CandidateConstraintEvaluation,
    ConstraintEvaluationResult,
    NotEvaluatedReason,
    VariableConstraintEvaluationCollectionResult,
    Verdict,
    derive_candidate_evaluation)
from backend.constraint_evaluation.decimal import (
    CanonicalObservedDecimal, ObservedDecimalResolution, parse_observed_decimal)
from backend.constraint_evaluation.errors import (
    ConstraintEvaluationConfigurationError,
    ConstraintEvaluationError,
    ConstraintEvaluationInputError,
    NumericParityBreachError)
from backend.constraint_evaluation.facade import ConstraintEvaluationQueries

__all__ = [
    # errors
    "ConstraintEvaluationError",
    "ConstraintEvaluationConfigurationError",
    "ConstraintEvaluationInputError",
    "NumericParityBreachError",
    # decimal
    "CanonicalObservedDecimal",
    "ObservedDecimalResolution",
    "parse_observed_decimal",
    # vocabularies
    "Verdict",
    "NotEvaluatedReason",
    # results
    "BoundaryAssessment",
    "CandidateConstraintEvaluation",
    "ConstraintEvaluationResult",
    "VariableConstraintEvaluationCollectionResult",
    "derive_candidate_evaluation",
    # facade
    "ConstraintEvaluationQueries",
]