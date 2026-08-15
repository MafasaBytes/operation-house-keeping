"""CN-001 Group 2 red baseline for exact numeric-bound predicates."""

from decimal import Decimal
import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

from backend.model_kernel import (
    CanonicalDecimal,
    ConstraintPredicate,
    ExactNumericInterval,
    ExactNumericLowerBound,
    ExactNumericUpperBound,
    NumericBoundary,
    canonical_constraint_decimal,
)


class DecimalBox(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: CanonicalDecimal


@pytest.mark.parametrize("value", [
    "0", "1", "-1", "0.5", "-0.5", "10.01", "-10.01",
    "9" * 256,
    "0." + "0" * 127 + "1",
    "9" * 128 + "." + "0" * 126 + "1",
])
def test_canonical_decimal_accepts_exact_canonical_strings(value):
    assert DecimalBox(value=value).value == value


@pytest.mark.parametrize("value", [
    "-0", "+1", "01", "-01", ".5", "1.", "1.0", "0.0", "1.230",
    "1e3", "1E3", "NaN", "Infinity", "-Infinity", " 1", "1 ", "1\n",
    1, 1.0, Decimal("1"), None,
])
def test_canonical_decimal_rejects_aliases_and_non_strings(value):
    with pytest.raises(ValidationError):
        DecimalBox(value=value)


@pytest.mark.parametrize("value", [
    "9" * 257,                              # integer digits > 256
    "0." + "0" * 128 + "1",              # fraction digits > 128
    "9" * 129 + "." + "0" * 127 + "1", # coefficient digits > 256
    "-" + "9" * 257 + "." + "0" * 127 + "1",  # UTF-8 bytes > 386
])
def test_canonical_decimal_enforces_every_declaration_resource_limit(value):
    with pytest.raises(ValidationError):
        DecimalBox(value=value)


@pytest.mark.parametrize(("value", "expected"), [
    ("0", "0"),
    ("-0", "0"),
    ("1.2300", "1.23"),
    ("1E+3", "1000"),
    ("-5e-3", "-0.005"),
    ("1e255", "1" + "0" * 255),
    ("1e-128", "0." + "0" * 127 + "1"),
])
def test_public_decimal_helper_produces_plain_canonical_strings(value, expected):
    assert canonical_constraint_decimal(value) == expected


@pytest.mark.parametrize("value", [
    "NaN", "Infinity", "-Infinity", "9" * 257, "1e256", "1e-129",
    "1." + "0" * 256,
    7, 7.0, Decimal("7"), None,
])
def test_public_decimal_helper_refuses_nonfinite_or_oversize_values(value):
    with pytest.raises(ValueError):
        canonical_constraint_decimal(value)


@pytest.mark.parametrize("inclusion", ["inclusive", "exclusive"])
def test_numeric_boundary_is_exact_and_explicit(inclusion):
    boundary = NumericBoundary(value="60.4", inclusion=inclusion)
    assert boundary.value == "60.4"
    assert boundary.inclusion == inclusion


@pytest.mark.parametrize("overrides", [
    {"value": "60.40"}, {"inclusion": "closed"},
    {"inclusion": True}, {"tolerance": "0.1"},
])
def test_numeric_boundary_rejects_aliases_and_extra_semantics(overrides):
    fields = {"value": "60.4", "inclusion": "inclusive"}
    fields.update(overrides)
    with pytest.raises(ValidationError):
        NumericBoundary(**fields)


def lower(value="0", inclusion="inclusive"):
    return NumericBoundary(value=value, inclusion=inclusion)


def upper(value="100", inclusion="inclusive"):
    return NumericBoundary(value=value, inclusion=inclusion)


def test_all_three_predicate_arms_are_public_and_exact():
    lo = ExactNumericLowerBound(lower=lower("0", "exclusive"))
    hi = ExactNumericUpperBound(upper=upper("100", "inclusive"))
    interval = ExactNumericInterval(lower=lower(), upper=upper())
    assert lo.kind == "lower_bound" and lo.lower.value == "0"
    assert hi.kind == "upper_bound" and hi.upper.value == "100"
    assert interval.kind == "interval"


def test_inclusive_singleton_interval_is_valid():
    predicate = ExactNumericInterval(
        lower=lower("60.4", "inclusive"),
        upper=upper("60.4", "inclusive"),
    )
    assert predicate.lower.value == predicate.upper.value == "60.4"


@pytest.mark.parametrize(("lower_inclusion", "upper_inclusion"), [
    ("exclusive", "inclusive"),
    ("inclusive", "exclusive"),
    ("exclusive", "exclusive"),
])
def test_equal_endpoint_interval_is_empty_if_either_endpoint_is_exclusive(
        lower_inclusion, upper_inclusion):
    with pytest.raises(ValidationError):
        ExactNumericInterval(
            lower=lower("60.4", lower_inclusion),
            upper=upper("60.4", upper_inclusion),
        )


def test_reversed_interval_is_rejected_by_exact_decimal_comparison():
    with pytest.raises(ValidationError):
        ExactNumericInterval(lower=lower("10.01"), upper=upper("10"))


@pytest.mark.parametrize("predicate", [
    ExactNumericLowerBound(lower=lower()),
    ExactNumericUpperBound(upper=upper()),
    ExactNumericInterval(lower=lower(), upper=upper()),
])
def test_constraint_predicate_union_accepts_and_round_trips_every_arm(predicate):
    adapter = TypeAdapter(ConstraintPredicate)
    assert adapter.validate_python(predicate.model_dump()) == predicate


@pytest.mark.parametrize("payload", [
    {"kind": "between", "lower": {"value": "0", "inclusion": "inclusive"}},
    {"kind": "lower_bound", "upper": {"value": "1", "inclusion": "inclusive"}},
    {"kind": "upper_bound", "upper": {"value": "1", "inclusion": "inclusive"},
     "severity": "warning"},
])
def test_constraint_predicate_union_rejects_unknown_wrong_and_extra_shapes(payload):
    with pytest.raises(ValidationError):
        TypeAdapter(ConstraintPredicate).validate_python(payload)


@pytest.mark.parametrize(("cls", "fields"), [
    (ExactNumericLowerBound, {"kind": "lower_bound", "lower": lower()}),
    (ExactNumericUpperBound, {"kind": "upper_bound", "upper": upper()}),
    (ExactNumericInterval,
     {"kind": "interval", "lower": lower(), "upper": upper()}),
])
def test_predicate_arms_are_frozen_and_forged_instances_are_revalidated(cls, fields):
    predicate = cls(**fields)
    with pytest.raises(ValidationError):
        predicate.kind = "forged"
    forged = cls.model_construct(**{**fields, "kind": "forged"})
    with pytest.raises(ValidationError):
        cls.model_validate(forged)
