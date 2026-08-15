"""CN-001 Group 2 red baseline for scalar numeric predicates."""

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from backend.model_kernel import (
    CanonicalDecimal,
    DeclaredUnit,
    ScalarComparisonPredicate,
    UnitNotDeclared,
    UnitReference,
)


VAR = "var_" + "b" * 32


class DecimalBox(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: CanonicalDecimal


@pytest.mark.parametrize("value", [
    "0", "1", "-1", "0.5", "-0.5", "10.01", "-10.01",
    "9" * 128,
    "0." + "0" * 127 + "1",
])
def test_canonical_decimal_accepts_exact_canonical_strings(value):
    assert DecimalBox(value=value).value == value


@pytest.mark.parametrize("value", [
    "-0", "+1", "01", "-01", ".5", "1.", "1.0", "0.0", "1.230",
    "1e3", "1E3", "NaN", "Infinity", "-Infinity", " 1", "1 ", "1\n",
    "9" * 129,
    "0." + "0" * 128 + "1",
    1, 1.0, None,
])
def test_canonical_decimal_rejects_aliases_hostile_values_and_oversize(value):
    with pytest.raises(ValidationError):
        DecimalBox(value=value)


def declared_unit():
    return DeclaredUnit(
        kind="declared",
        unit=UnitReference(
            system_id="project_local",
            system_edition="cn001-test",
            code="cel",
        ),
    )


@pytest.mark.parametrize("operator", [
    "less_than", "less_than_or_equal", "equal",
    "greater_than_or_equal", "greater_than", "not_equal",
])
@pytest.mark.parametrize("unit", [
    pytest.param(declared_unit(), id="declared-unit"),
    pytest.param(UnitNotDeclared(kind="not_declared"), id="explicit-unitless"),
])
def test_scalar_comparison_predicate_accepts_every_operator(operator, unit):
    predicate = ScalarComparisonPredicate(
        kind="scalar_comparison",
        variable_anchor_id=VAR,
        operator=operator,
        threshold="60.4",
        unit=unit,
    )
    assert predicate.operator == operator
    assert predicate.threshold == "60.4"
    assert predicate.unit == unit


@pytest.mark.parametrize("overrides", [
    {"kind": "interval"},
    {"variable_anchor_id": "ent_" + "b" * 32},
    {"operator": "between"},
    {"threshold": "60.40"},
    {"unit": None},
    {"tolerance": "0.1"},
    {"lower": "0"},
    {"other_variable_anchor_id": "var_" + "c" * 32},
    {"severity": "warning"},
])
def test_scalar_predicate_rejects_non_v1_or_implicit_fields(overrides):
    fields = dict(
        kind="scalar_comparison",
        variable_anchor_id=VAR,
        operator="less_than_or_equal",
        threshold="60.4",
        unit=declared_unit(),
    )
    fields.update(overrides)
    with pytest.raises(ValidationError):
        ScalarComparisonPredicate(**fields)


def test_scalar_predicate_is_frozen_and_forgery_is_revalidated():
    predicate = ScalarComparisonPredicate(
        kind="scalar_comparison",
        variable_anchor_id=VAR,
        operator="equal",
        threshold="0",
        unit=UnitNotDeclared(kind="not_declared"),
    )
    with pytest.raises(ValidationError):
        predicate.threshold = "1"

    forged = ScalarComparisonPredicate.model_construct(
        kind="scalar_comparison",
        variable_anchor_id="var_NOT_HEX",
        operator="equal",
        threshold="1.0",
        unit=UnitNotDeclared(kind="not_declared"),
    )
    with pytest.raises(ValidationError):
        ScalarComparisonPredicate.model_validate(forged)
