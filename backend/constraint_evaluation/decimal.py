"""CN-001 Slice B observed-decimal parsing.

A narrow, bounded, exact JSON-number parser owned by the constraint
evaluator. It is NOT the accepted VS-001 ``_parse_shape`` and it imports
nothing private from VS: the strict ``json.loads(parse_float=Decimal,
parse_int=int, parse_constant=reject)`` call shape is the standard
library's accepted ingestion policy, reimplemented here so the evaluator
never reaches into VS internals. Parity with VS is achieved by using the
same standard-library call, never by sharing code.

The parser accepts exactly one standard JSON number. Legal JSON whitespace
(space, tab, CR, LF) around it is permitted, matching VS and standard JSON.
Quoted numbers, booleans, ``null``, arrays, objects, trailing values,
``NaN``, and ``Infinity`` are rejected. The byte limit applies to the
complete stored lexeme (including whitespace). The original evidence
lexeme is preserved unchanged on the returned ``CanonicalObservedDecimal``.

``Decimal`` is used throughout; ``float`` is never used and the ambient
``Decimal`` context is never consulted for rounding (``format(d, "f")`` is
fixed-point and context-free). A valid admitted number that exceeds the CN
resource limits (lexeme bytes, coefficient digits, or expanded integer/
fraction digits) returns ``numeric_value_out_of_bounds`` — an honest
candidate refusal, never a typed error. A disagreement with the accepted VS
numeric classification (VS reported a consistent number but the CN narrow
parser could not reproduce it) is a typed parity-breach integrity error,
never an honest candidate verdict. Preflight expansion is checked before
any allocation, so ``1E+999`` never materializes a thousand-character
string. Mathematical zero (``-0``, ``0.0``, ``0E+99``, ``-0E-99`` …) is
normalized to ``"0"``.
"""

import json
import re
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.constraint_evaluation.errors import (
    ConstraintEvaluationInputError, NumericParityBreachError)

# Resource limits. The canonical plain-number grammar is the accepted
# CanonicalDecimal declaration grammar; the lexeme byte limit applies to
# the complete stored lexeme (including legal JSON whitespace); the
# coefficient/integer/fraction limits apply to the expanded canonical
# output. These are narrower than the VS parser, which inherits the
# standard library's defaults; they bound the evaluator's resource use
# without relying on ambient limits.
_LEXEME_BYTE_LIMIT = 386
_COEFFICIENT_DIGIT_LIMIT = 256
_EXPONENT_MAGNITUDE_LIMIT = 256
_INTEGER_DIGIT_LIMIT = 256
_FRACTION_DIGIT_LIMIT = 128

_JSON_NUMBER = re.compile(
    r"[ \t\r\n]*(?P<number>-?(?P<integer>0|[1-9][0-9]*)"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?:[eE](?P<exponent_sign>[+-]?)(?P<exponent>[0-9]+))?)"
    r"[ \t\r\n]*\Z")

# The canonical plain-number grammar (the accepted CanonicalDecimal
# declaration grammar, compiled locally so this module never reaches into
# model_kernel or VS internals during parsing).
_CANONICAL_DECIMAL = re.compile(
    r"(?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))")


class _NonFiniteConstant(ValueError):
    """NaN/Infinity are not JSON: malformed text, not an unrepresentable
    value. Mirrors the accepted VS rejection locally; not imported."""


def _reject_constant(name: str):
    raise _NonFiniteConstant(f"non-finite JSON constant {name!r} rejected")


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


class CanonicalObservedDecimal(_Frozen):
    """One admitted observed numeric value: the original source lexeme,
    preserved unchanged, and the canonical plain-number form derived from
    it. The canonical form follows the accepted CanonicalDecimal
    declaration grammar (no exponent, no leading zeros, no trailing zeros,
    mathematical zero normalized to ``"0"``)."""

    lexeme: str = Field(min_length=1)
    canonical: str = Field(min_length=1)

    @model_validator(mode="after")
    def _locked(self):
        if len(self.lexeme.encode("utf-8")) > _LEXEME_BYTE_LIMIT:
            raise ValueError("lexeme exceeds the CN observed byte limit")
        if not _CANONICAL_DECIMAL.fullmatch(self.canonical):
            raise ValueError("canonical is not a canonical plain-number")
        # defense-in-depth: re-derive the canonical from the lexeme and
        # confirm it matches, so a forged canonical/lexeme pair is rejected
        # at the contract boundary
        try:
            reparsed = _parse_only(self.lexeme)
        except NumericParityBreachError:
            raise ValueError("lexeme is not a valid JSON number")
        if reparsed is None or reparsed != self.canonical:
            raise ValueError("canonical must be the exact re-derivation "
                             "of the preserved lexeme")
        return self


class ObservedDecimalResolution(_Frozen):
    """The outcome of parsing one observed numeric lexeme: ``admitted``
    (carry the ``CanonicalObservedDecimal``) or ``out_of_bounds`` (the
    value is a valid JSON number but exceeds a CN resource limit). A
    disagreement with VS raises ``NumericParityBreachError`` and never
    reaches this type."""

    status: Literal["admitted", "out_of_bounds"]
    decimal: CanonicalObservedDecimal | None = None

    @model_validator(mode="after")
    def _locked(self):
        if (self.decimal is None) != (self.status != "admitted"):
            raise ValueError("a decimal is carried exactly when admitted")
        return self


def _parse_only(lexeme: str) -> str | None:
    """Re-derive the canonical plain-number form from one lexeme without
    constructing the public contract. Returns ``None`` if the lexeme is a
    valid JSON number that exceeds a CN resource limit (out_of_bounds).
    Raises ``NumericParityBreachError`` if the lexeme is not parseable as
    exactly one JSON number (the caller must have already established that
    VS reported it as a consistent number)."""

    if not isinstance(lexeme, str) or not lexeme:
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "observed lexeme must be a non-empty string")
    # Establish JSON-number syntax before applying resource refusals.  A
    # malformed/non-number lexeme is a parity breach even when oversized;
    # only a valid number may honestly be reported out of bounds.  This
    # lexical preflight allocates no expanded decimal representation.
    match = _JSON_NUMBER.fullmatch(lexeme)
    if match is None:
        raise NumericParityBreachError(
            "NUMERIC_PARITY_BREACH",
            f"CN narrow parser rejects lexeme VS reported as a number: "
            f"{lexeme!r}")
    if len(lexeme.encode("utf-8")) > _LEXEME_BYTE_LIMIT:
        return None
    coefficient_digits = len(match.group("integer")) + len(
        match.group("fraction") or "")
    if coefficient_digits > _COEFFICIENT_DIGIT_LIMIT:
        return None
    exponent_text = match.group("exponent")
    if (exponent_text is not None
            and int(exponent_text) > _EXPONENT_MAGNITUDE_LIMIT):
        return None
    try:
        value = json.loads(lexeme, parse_float=Decimal, parse_int=int,
                           parse_constant=_reject_constant)
    except (json.JSONDecodeError, _NonFiniteConstant):
        raise NumericParityBreachError(
            "NUMERIC_PARITY_BREACH",
            f"CN narrow parser rejects lexeme VS reported as a number: "
            f"{lexeme!r}")
    except (ValueError, InvalidOperation, RecursionError):
        raise NumericParityBreachError(
            "NUMERIC_PARITY_BREACH",
            f"CN narrow parser could not represent lexeme VS reported as "
            f"a number: {lexeme!r}")
    if isinstance(value, bool) or value is None or isinstance(
            value, (str, list, dict)):
        raise NumericParityBreachError(
            "NUMERIC_PARITY_BREACH",
            f"CN narrow parser parsed a non-number where VS reported a "
            f"number: {lexeme!r}")
    decimal = value if isinstance(value, Decimal) else Decimal(value)
    if not decimal.is_finite():
        raise NumericParityBreachError(
            "NUMERIC_PARITY_BREACH",
            f"CN narrow parser produced a non-finite value where VS "
            f"reported a number: {lexeme!r}")
    return _normalize(decimal)


def _normalize(d: Decimal) -> str | None:
    """Return the canonical plain-number form of one finite ``Decimal``,
    or ``None`` if its expanded form exceeds a CN resource limit.
    Mathematical zero is normalized to ``"0"`` (both signs, any exponent).
    ``format(d, "f")`` is fixed-point and context-free; the ambient Decimal
    context is never consulted for rounding."""

    if d.is_zero():
        return "0"
    sign, digits_tuple, exponent = d.as_tuple()
    digits = list(digits_tuple)
    # Expanded-output limits apply to the canonical value.  Trailing
    # coefficient zeros disappear from that value and therefore must be
    # trimmed before the fractional preflight.
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
        exponent += 1
    if exponent >= 0:
        int_digits = len(digits) + exponent
        frac_digits = 0
    else:
        int_digits = max(len(digits) + exponent, 0)
        frac_digits = -exponent
    if int_digits < 1:
        int_digits = 1
    if int_digits > _INTEGER_DIGIT_LIMIT or frac_digits > _FRACTION_DIGIT_LIMIT:
        return None
    rendered = format(d, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if rendered in ("", "-", "-0"):
        return "0"
    return rendered


def parse_observed_decimal(lexeme: str) -> ObservedDecimalResolution:
    """Parse one observed numeric lexeme. Returns ``admitted`` (carrying a
    ``CanonicalObservedDecimal`` whose canonical form follows the accepted
    declaration grammar) or ``out_of_bounds`` (the value is a valid JSON
    number but exceeds a CN resource limit). Raises
    ``NumericParityBreachError`` if the lexeme is not parseable as exactly
    one JSON number — this is the typed integrity failure that surfaces
    when the CN narrow parser disagrees with the accepted VS numeric
    classification, and it is never an honest candidate verdict."""

    canonical = _parse_only(lexeme)
    if canonical is None:
        return ObservedDecimalResolution(status="out_of_bounds")
    return ObservedDecimalResolution(
        status="admitted",
        decimal=CanonicalObservedDecimal(lexeme=lexeme, canonical=canonical))
