"""CN-001 Slice B parser tests: bounded exact JSON-number parsing, parity
with VS, preflight expansion, mathematical-zero normalization, and the
typed parity-breach integrity error."""

from decimal import Context, Decimal, getcontext, localcontext

import pytest

from backend.constraint_evaluation import (
    CanonicalObservedDecimal, NumericParityBreachError,
    ObservedDecimalResolution, parse_observed_decimal)
from backend.constraint_evaluation.errors import ConstraintEvaluationInputError


class TestAdmission:
    def test_plain_integer_admitted(self):
        r = parse_observed_decimal("80")
        assert r.status == "admitted"
        assert r.decimal.canonical == "80"
        assert r.decimal.lexeme == "80"

    def test_plain_decimal_admitted(self):
        r = parse_observed_decimal("60.4")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60.4"

    def test_negative_value_admitted(self):
        r = parse_observed_decimal("-25.5")
        assert r.status == "admitted"
        assert r.decimal.canonical == "-25.5"

    def test_negative_zero_normalized_to_zero(self):
        r = parse_observed_decimal("-0")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0"

    def test_zero_with_exponent_normalized_to_zero(self):
        r = parse_observed_decimal("0E+99")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0"

    def test_negative_zero_decimal_normalized(self):
        r = parse_observed_decimal("-0.0")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0"

    def test_trailing_zeros_stripped(self):
        r = parse_observed_decimal("60.40")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60.4"

    def test_exponent_notation_admitted(self):
        r = parse_observed_decimal("1E+3")
        assert r.status == "admitted"
        assert r.decimal.canonical == "1000"

    def test_negative_exponent_admitted(self):
        r = parse_observed_decimal("1E-3")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0.001"

    def test_lowercase_exponent_admitted(self):
        r = parse_observed_decimal("6e1")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60"

    def test_plus_sign_exponent_admitted(self):
        r = parse_observed_decimal("1E+2")
        assert r.status == "admitted"
        assert r.decimal.canonical == "100"


class TestWhitespace:
    def test_leading_space_admitted(self):
        r = parse_observed_decimal("  60.4")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60.4"
        assert r.decimal.lexeme == "  60.4"

    def test_trailing_space_admitted(self):
        r = parse_observed_decimal("60.4  ")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60.4"

    @pytest.mark.parametrize("ws", [" ", "\t", "\n", "\r", " \t\n\r"])
    def test_all_legal_json_whitespace_admitted(self, ws):
        r = parse_observed_decimal(f"{ws}60{ws}")
        assert r.status == "admitted"
        assert r.decimal.canonical == "60"


class TestParityBreach:
    def test_quoted_string_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal('"60.4"')

    def test_boolean_true_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("true")

    def test_boolean_false_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("false")

    def test_null_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("null")

    def test_array_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("[60.4]")

    def test_object_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal('{"v": 60.4}')

    def test_nan_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("NaN")

    def test_infinity_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("Infinity")

    def test_trailing_value_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("60.4 50")

    def test_empty_string_is_input_error(self):
        with pytest.raises(ConstraintEvaluationInputError):
            parse_observed_decimal("")

    def test_non_string_is_input_error(self):
        with pytest.raises(ConstraintEvaluationInputError):
            parse_observed_decimal(60.4)  # type: ignore[arg-type]


class TestOutOfBounds:
    def test_huge_exponent_integer_out_of_bounds(self):
        r = parse_observed_decimal("1E+999")
        assert r.status == "out_of_bounds"
        assert r.decimal is None

    def test_huge_negative_exponent_out_of_bounds(self):
        r = parse_observed_decimal("1E-999")
        assert r.status == "out_of_bounds"

    def test_integer_over_256_digits_out_of_bounds(self):
        r = parse_observed_decimal("1" * 300)
        assert r.status == "out_of_bounds"

    def test_lexeme_over_byte_limit_out_of_bounds(self):
        # 387-byte lexeme (one byte over the 386 limit)
        r = parse_observed_decimal(" " * 386 + "1")
        assert r.status == "out_of_bounds"

    def test_lexeme_at_byte_limit_admitted(self):
        # 386 bytes total: 385 spaces + "1" = 386 bytes
        r = parse_observed_decimal(" " * 385 + "1")
        assert r.status == "admitted"
        assert r.decimal.canonical == "1"


class TestPreflightExpansion:
    def test_preflight_does_not_allocate_huge_string(self):
        # If preflight failed, format(Decimal("1E+9999"), "f") would
        # allocate a 10000-char string. Preflight must reject first.
        r = parse_observed_decimal("1E+9999")
        assert r.status == "out_of_bounds"

    def test_preflight_large_negative_exponent(self):
        r = parse_observed_decimal("1E-9999")
        assert r.status == "out_of_bounds"


class TestPrecisionAndContext:
    def test_large_integer_admitted_exactly(self):
        # 200-digit integer: within the 256-integer-digit limit
        r = parse_observed_decimal("1" * 200)
        assert r.status == "admitted"
        assert r.decimal.canonical == "1" * 200

    def test_precision_sensitive_fraction_admitted(self):
        # 100-digit fraction: within the 128-fraction-digit limit
        r = parse_observed_decimal("0." + "0" * 99 + "1")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0." + "0" * 99 + "1"

    def test_altered_ambient_decimal_context_does_not_change_parsing(self):
        # Parsing must not consult the ambient Decimal context for rounding.
        with localcontext(Context(prec=5)):
            r = parse_observed_decimal("123456789.123456789")
        assert r.status == "admitted"
        assert r.decimal.canonical == "123456789.123456789"

    def test_no_float_rounding(self):
        r = parse_observed_decimal("0.1")
        assert r.status == "admitted"
        assert r.decimal.canonical == "0.1"  # not 0.10000000149...

    def test_negative_zero_under_high_precision_context(self):
        with localcontext(Context(prec=2)):
            r = parse_observed_decimal("-0.0001")
        assert r.status == "admitted"
        assert r.decimal.canonical == "-0.0001"


class TestContractForgery:
    def test_forged_canonical_rejected(self):
        # lexeme "60.4" canonicalizes to "60.4"; a forged "99" is rejected
        with pytest.raises(Exception):
            CanonicalObservedDecimal(lexeme="60.4", canonical="99")

    def test_forged_lexeme_canonical_mismatch_rejected(self):
        with pytest.raises(Exception):
            CanonicalObservedDecimal(lexeme="60.4", canonical="60.5")

    def test_canonical_must_be_rederivation_of_lexeme(self):
        with pytest.raises(Exception):
            CanonicalObservedDecimal(lexeme="1E+3", canonical="3")

    def test_empty_lexeme_rejected(self):
        with pytest.raises(Exception):
            CanonicalObservedDecimal(lexeme="", canonical="0")

    def test_lexeme_over_byte_limit_rejected(self):
        with pytest.raises(Exception):
            CanonicalObservedDecimal(lexeme=" " * 387, canonical="0")
        # " " * 387 isn't a number anyway; the byte limit guard fires first

    def test_resolution_contract_decimal_present_iff_admitted(self):
        with pytest.raises(Exception):
            ObservedDecimalResolution(status="admitted", decimal=None)
        with pytest.raises(Exception):
            r = parse_observed_decimal("1")
            ObservedDecimalResolution(status="out_of_bounds", decimal=r.decimal)

    def test_non_number_lexeme_raises_validation_error_not_parity_breach(self):
        # Direct construction with a non-number lexeme must raise a
        # pydantic ValidationError (wrapped ValueError), not a raw
        # NumericParityBreachError. The _locked validator catches the
        # parity-breach integrity error and re-raises as ValueError so
        # pydantic's normal contract applies.
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            CanonicalObservedDecimal(lexeme="abc", canonical="0")
        # verify the integrity error does not leak through directly
        from backend.constraint_evaluation import NumericParityBreachError
        try:
            CanonicalObservedDecimal(lexeme="abc", canonical="0")
        except NumericParityBreachError:
            pytest.fail("NumericParityBreachError must not leak through "
                         "direct construction")
        except pydantic.ValidationError:
            pass  # expected


class TestVsParity:
    """The CN parser must agree with the accepted VS classification on what
    is a JSON number. These cases would be reported by VS as ``consistent``
    and ``observed_shape == "number"`` and the CN parser must admit them."""

    @pytest.mark.parametrize("lexeme,canonical", [
        ("60.4", "60.4"),
        ("60.40", "60.4"),
        ("60", "60"),
        ("-0.25", "-0.25"),
        ("1e2", "100"),
        ("  60.4  ", "60.4"),
        ("0.001", "0.001"),
    ])
    def test_vs_consistent_number_cases_admitted(self, lexeme, canonical):
        r = parse_observed_decimal(lexeme)
        assert r.status == "admitted"
        assert r.decimal.canonical == canonical


class TestAdversarialLimitClassification:
    """Limits never turn malformed evidence into an honest refusal."""

    @pytest.mark.parametrize("lexeme", [
        "x" * 387,
        '"' + "1" * 387 + '"',
        "[" + "1" * 387 + "]",
        "1" * 386 + "x",
    ])
    def test_over_limit_non_numbers_are_parity_breaches(self, lexeme):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal(lexeme)

    def test_zero_cannot_bypass_coefficient_limit(self):
        assert parse_observed_decimal(
            "0." + "0" * 256).status == "out_of_bounds"

    def test_trailing_zero_is_trimmed_before_expansion_limit(self):
        lexeme = "1." + "1" * 128 + "0"
        result = parse_observed_decimal(lexeme)
        assert result.status == "admitted"
        assert result.decimal.canonical == "1." + "1" * 128

    @pytest.mark.parametrize("lexeme", ["0E+256", "0E-256"])
    def test_zero_at_explicit_exponent_limit_is_admitted(self, lexeme):
        assert parse_observed_decimal(lexeme).status == "admitted"

    @pytest.mark.parametrize("lexeme", ["0E+257", "0E-257"])
    def test_zero_beyond_explicit_exponent_limit_is_out_of_bounds(self, lexeme):
        assert parse_observed_decimal(lexeme).status == "out_of_bounds"
