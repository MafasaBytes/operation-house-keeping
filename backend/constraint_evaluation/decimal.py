"""Bounded exact JSON-number parsing for CN-001 observed values."""

import re
from typing import Annotated, Literal

from pydantic import (
    AfterValidator, BaseModel, ConfigDict, StrictStr, model_validator)

from backend.constraint_evaluation.errors import (
    ConstraintEvaluationInputError, NumericParityBreachError)

_SOURCE_BYTE_LIMIT = 512
_MANTISSA_COEFFICIENT_DIGIT_LIMIT = 256
_MANTISSA_FRACTION_DIGIT_LIMIT = 128
_SIGNIFICANT_DIGIT_LIMIT = 256
_EXPONENT_DIGIT_LIMIT = 4
_ABSOLUTE_EXPONENT_LIMIT = 1024
_EXPANDED_DIGIT_LIMIT = 384
_EXPANDED_FRACTION_DIGIT_LIMIT = 384
_EXPANDED_BYTE_LIMIT = 386

_PARITY_MESSAGE = (
    "observed value disagrees with accepted VS numeric classification")

# Applied only after the complete source has passed the 512-byte gate.
_JSON_NUMBER = re.compile(
    r"[ \t\r\n]*(?P<sign>-?)(?P<integer>0|[1-9][0-9]*)"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?:[eE](?P<exponent_sign>[+-]?)(?P<exponent>[0-9]+))?"
    r"[ \t\r\n]*\Z")
_CANONICAL = re.compile(
    r"(?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))\Z")


def _parity_breach() -> NumericParityBreachError:
    return NumericParityBreachError("NUMERIC_PARITY_BREACH", _PARITY_MESSAGE)


def _looks_numeric_at_bounded_prefix(lexeme: str) -> bool:
    """Classify an already oversized source without scanning it fully."""
    prefix = lexeme[:_SOURCE_BYTE_LIMIT + 1]
    for character in prefix:
        if character in " \t\r\n":
            continue
        return character in "-0123456789"
    # An oversized whitespace prefix may precede a number beyond the gate;
    # treating it as a resource refusal avoids unbounded scanning.
    return True


def _expanded_plain(sign: str, digits: str, exponent: int) -> str | None:
    """Preflight canonical fixed-point expansion before allocating it."""
    # Remove coefficient trailing zeros without Decimal/context operations.
    trailing = len(digits) - len(digits.rstrip("0"))
    if trailing:
        digits = digits[:-trailing]
        exponent += trailing

    point = len(digits) + exponent
    if point <= 0:
        fractional_digits = -point + len(digits)
        expanded_digits = fractional_digits
        byte_count = len(sign) + 2 + fractional_digits  # ``-?0.`` + fraction
        if (fractional_digits > _EXPANDED_FRACTION_DIGIT_LIMIT
                or expanded_digits > _EXPANDED_DIGIT_LIMIT
                or byte_count > _EXPANDED_BYTE_LIMIT):
            return None
        return sign + "0." + "0" * (-point) + digits

    if point >= len(digits):
        integer_digits = point
        expanded_digits = integer_digits
        byte_count = len(sign) + integer_digits
        if (expanded_digits > _EXPANDED_DIGIT_LIMIT
                or byte_count > _EXPANDED_BYTE_LIMIT):
            return None
        return sign + digits + "0" * (point - len(digits))

    fractional_digits = len(digits) - point
    expanded_digits = len(digits)
    byte_count = len(sign) + len(digits) + 1
    if (fractional_digits > _EXPANDED_FRACTION_DIGIT_LIMIT
            or expanded_digits > _EXPANDED_DIGIT_LIMIT
            or byte_count > _EXPANDED_BYTE_LIMIT):
        return None
    return sign + digits[:point] + "." + digits[point:]


def _parse_only(lexeme: str) -> str | None:
    if not isinstance(lexeme, str) or not lexeme:
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "observed value_json must be a non-empty string")
    # ``len`` is the minimum constant-work hostile-input gate.  No regex,
    # encoding, integer conversion, or expansion occurs for a longer source.
    if len(lexeme) > _SOURCE_BYTE_LIMIT:
        if _looks_numeric_at_bounded_prefix(lexeme):
            return None
        raise _parity_breach()
    # Encoding at most 512 characters is bounded. A valid JSON number and
    # its legal whitespace are ASCII, so a larger UTF-8 byte count here is
    # necessarily a parity breach rather than a numeric resource refusal.
    if len(lexeme.encode("utf-8")) > _SOURCE_BYTE_LIMIT:
        raise _parity_breach()

    match = _JSON_NUMBER.fullmatch(lexeme)
    if match is None:
        raise _parity_breach()

    integer = match.group("integer")
    fraction = match.group("fraction") or ""
    coefficient = integer + fraction
    if (len(coefficient) > _MANTISSA_COEFFICIENT_DIGIT_LIMIT
            or len(fraction) > _MANTISSA_FRACTION_DIGIT_LIMIT):
        return None

    exponent_text = match.group("exponent")
    if exponent_text is not None and len(exponent_text) > _EXPONENT_DIGIT_LIMIT:
        return None
    exponent_magnitude = 0 if exponent_text is None else int(exponent_text)
    if exponent_magnitude > _ABSOLUTE_EXPONENT_LIMIT:
        return None
    exponent = (-exponent_magnitude
                if match.group("exponent_sign") == "-"
                else exponent_magnitude)

    nonzero = coefficient.lstrip("0")
    if not nonzero:
        return "0"
    if len(nonzero) > _SIGNIFICANT_DIGIT_LIMIT:
        return None

    # Removing lexical leading zeros shifts no mathematical exponent because
    # they occur only in the fraction after JSON's single integer zero.
    mathematical_exponent = exponent - len(fraction)
    sign = "-" if match.group("sign") else ""
    return _expanded_plain(sign, nonzero, mathematical_exponent)


def _validate_canonical(value: str) -> str:
    if not _CANONICAL.fullmatch(value):
        raise ValueError("observed decimal must be canonical plain decimal")
    raw = value.lstrip("-")
    numeric_digits = len(raw.replace(".", "")) - (1 if raw.startswith("0.") else 0)
    fractional_digits = len(raw.split(".", 1)[1]) if "." in raw else 0
    if (numeric_digits > _EXPANDED_DIGIT_LIMIT
            or fractional_digits > _EXPANDED_FRACTION_DIGIT_LIMIT
            or len(value.encode("utf-8")) > _EXPANDED_BYTE_LIMIT):
        raise ValueError("observed decimal exceeds canonical output limits")
    return value


CanonicalObservedDecimal = Annotated[StrictStr, AfterValidator(_validate_canonical)]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


class ObservedDecimalResolution(_Frozen):
    status: Literal["admitted", "out_of_bounds"]
    decimal: CanonicalObservedDecimal | None = None

    @model_validator(mode="after")
    def _locked(self):
        if (self.decimal is None) != (self.status != "admitted"):
            raise ValueError("a decimal is carried exactly when admitted")
        return self


def parse_observed_decimal(lexeme: str) -> ObservedDecimalResolution:
    canonical = _parse_only(lexeme)
    if canonical is None:
        return ObservedDecimalResolution(status="out_of_bounds")
    return ObservedDecimalResolution(status="admitted", decimal=canonical)
