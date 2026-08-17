"""Typed error tree for CN-001 Slice B constraint evaluation.

The evaluator is read-only and composes accepted lower layers. Every
operational public entry point (the facade constructor and the two query
methods) fails through this tree: raw ``ValidationError``, ``KeyError``,
``AttributeError``, ``TypeError``, ``OSError``, ``UnicodeError``, parser
errors, and warnings never escape as the public outcome. Direct
construction of the pydantic contract models is the deliberate carve-out
and follows pydantic's normal ``ValidationError`` contract.

Absence, disagreement, and out-of-bounds are verdicts or statuses, never
exceptions. The single exception that CAN surface at query time is the
numeric parity-breach integrity error: VS reported a consistent number-
shaped JSON value but the CN narrow parser disagreed. That is a typed
internal integrity failure, never an honest candidate verdict.
"""


class ConstraintEvaluationError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class ConstraintEvaluationConfigurationError(ConstraintEvaluationError):
    """Invalid composition input (wrong object kinds injected)."""


class ConstraintEvaluationInputError(ConstraintEvaluationError):
    """Contract misuse at the query boundary. Absence, disagreement, and
    out-of-bounds are statuses, never exceptions."""


class NumericParityBreachError(ConstraintEvaluationError):
    """VS reported ``evidence_consistency == "consistent"`` and
    ``observed_shape == "number"`` but the CN narrow parser disagreed.

    This is a typed internal integrity/configuration failure, never an
    honest candidate verdict: the accepted VS boundary and the CN narrow
    parser must agree on what is a JSON number. ``numeric_value_malformed``
    is removed from the candidate vocabulary precisely because a
    disagreement here is an integrity fault, not an observation outcome."""