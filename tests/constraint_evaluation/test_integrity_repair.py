"""Owner-specified CN-001 Slice B integrity-repair regressions."""

from decimal import Context, ROUND_CEILING, ROUND_FLOOR, localcontext
import json

import pytest

import backend.constraint_evaluation as public
from backend.constraint_evaluation import (
    ConstraintEvaluationQueries, NumericParityBreachError,
    parse_observed_decimal)
from backend.model_kernel import NumericBoundary
from tests.constraint_evaluation.helpers import (
    AS_OF, CON_A, CON_B, HOTEND, cn_stack, constraint_declaration,
    constraint_registration)


def admitted(lexeme):
    result = parse_observed_decimal(lexeme)
    assert result.status == "admitted"
    return result.decimal


class TestApprovedDecimalLimits:
    def test_canonical_observed_decimal_is_plain_string(self):
        value = admitted(" 60.40 ")
        assert value == "60.4"
        assert isinstance(value, str)
        assert not hasattr(value, "lexeme")

    @pytest.mark.parametrize("sign", ["", "-"])
    def test_padded_512_byte_lexeme_admitted_and_513_refused(self, sign):
        number = sign + "1"
        padded = number + " " * (512 - len(number))
        assert len(padded.encode()) == 512
        assert admitted(padded) == number
        assert parse_observed_decimal(padded + " ").status == "out_of_bounds"

    @pytest.mark.parametrize("sign", ["", "-"])
    @pytest.mark.parametrize("exponent,expected", [
        ("300", lambda sign: sign + "1" + "0" * 300),
        ("-300", lambda sign: sign + "0." + "0" * 299 + "1"),
    ])
    def test_expansion_300_admitted(self, sign, exponent, expected):
        assert admitted(f"{sign}1e{exponent}") == expected(sign)

    @pytest.mark.parametrize("sign", ["", "-"])
    def test_zero_exponent_magnitude_1024_boundary(self, sign):
        assert admitted(f"{sign}0e1024") == "0"
        assert parse_observed_decimal(f"{sign}0e1025").status == "out_of_bounds"

    def test_exponent_digit_count_includes_leading_zeroes(self):
        assert admitted("1e0001") == "10"
        assert parse_observed_decimal("1e00001").status == "out_of_bounds"

    @pytest.mark.parametrize("sign", ["", "-"])
    def test_expanded_digit_and_byte_boundaries(self, sign):
        exact_digits = f"{sign}1e383"
        assert len(admitted(exact_digits).lstrip("-")) == 384
        assert parse_observed_decimal(f"{sign}1e384").status == "out_of_bounds"
        # Negative output is 386 bytes at 384 digits; one more digit is both
        # 385 expanded digits and 387 bytes.
        rendered = admitted(f"{sign}1e383")
        assert len(rendered.encode()) in (384, 385)

    @pytest.mark.parametrize("sign", ["", "-"])
    def test_expanded_fraction_boundary(self, sign):
        exponent = 384 if not sign else 383
        exact = admitted(f"{sign}1e-{exponent}")
        assert len(exact.encode()) == 386
        assert len(exact.split(".")[1]) == exponent
        assert parse_observed_decimal(
            f"{sign}1e-{exponent + 1}").status == "out_of_bounds"

    def test_mantissa_limits_and_valid_twins(self):
        assert parse_observed_decimal("1" * 256).status == "admitted"
        assert parse_observed_decimal("1" * 257).status == "out_of_bounds"
        assert parse_observed_decimal("0." + "1" * 128).status == "admitted"
        assert parse_observed_decimal("0." + "1" * 129).status == "out_of_bounds"

    @pytest.mark.parametrize("rounding", [ROUND_CEILING, ROUND_FLOOR])
    def test_ambient_decimal_context_cannot_change_result(self, rounding):
        with localcontext(Context(prec=2, rounding=rounding)):
            assert admitted("-1.23456789e2") == "-123.456789"


class TestBoundedPreflightAndMessages:
    def test_hostile_oversize_has_fixed_value_free_error(self):
        hostile = "x" * 100_000
        with pytest.raises(NumericParityBreachError) as caught:
            parse_observed_decimal(hostile)
        assert caught.value.message == (
            "observed value disagrees with accepted VS numeric classification")
        assert "x" not in caught.value.message

    def test_oversized_valid_number_is_refusal_not_parity_breach(self):
        assert parse_observed_decimal("1" + " " * 512).status == "out_of_bounds"

    def test_bounded_non_ascii_oversize_is_parity_breach(self):
        with pytest.raises(NumericParityBreachError):
            parse_observed_decimal("1" + "é" * 300)


def test_exact_public_exports_and_normative_names():
    assert public.ConstraintEvaluationVerdict.__args__ == (
        "satisfied", "violated", "not_evaluated")
    assert set(public.ConstraintNotEvaluatedReason.__args__) == {
        "constraint_not_declared", "constraint_conflicted",
        "observation_absent", "observation_not_attached",
        "evidence_not_assessable", "value_shape_not_evaluated",
        "model_value_shape_not_numeric", "value_shape_not_satisfied",
        "numeric_value_absent", "declared_semantics_not_compatible",
        "constraint_quantity_kind_mismatch",
        "constraint_observation_role_mismatch",
        "constraint_unit_identity_mismatch", "numeric_value_out_of_bounds",
    }
    assert "constraint" in public.ConstraintEvaluationResult.model_fields
    assert "revision" not in public.ConstraintEvaluationResult.model_fields
    assert "semantic_candidate_index" in public.CandidateConstraintEvaluation.model_fields
    assert set(public.BoundaryAssessment.model_fields) == {
        "side", "boundary", "relation", "satisfied"}
    assert public.BoundaryAssessment.model_fields["boundary"].annotation is NumericBoundary
    assert hasattr(ConstraintEvaluationQueries, "constraint_evaluation")
    assert hasattr(ConstraintEvaluationQueries, "variable_constraint_evaluations")
    assert "Verdict" not in public.__all__
    assert "NotEvaluatedReason" not in public.__all__
    assert public.__all__ == [
        "ConstraintEvaluationError",
        "ConstraintEvaluationConfigurationError",
        "ConstraintEvaluationInputError",
        "NumericParityBreachError",
        "CanonicalObservedDecimal",
        "ObservedDecimalResolution",
        "parse_observed_decimal",
        "ConstraintEvaluationVerdict",
        "ConstraintNotEvaluatedReason",
        "BoundaryAssessment",
        "CandidateConstraintEvaluation",
        "ConstraintEvaluationResult",
        "VariableConstraintEvaluationEntry",
        "VariableConstraintEvaluationCollectionResult",
        "derive_candidate_evaluation",
        "ConstraintEvaluationQueries",
    ]


def test_source_lexeme_remains_only_in_carried_occurrence(tmp_path):
    from tests.constraint_evaluation.helpers import (
        LATE, craft_value, default_constraint_records)
    cn, _, _, temporal = cn_stack(
        tmp_path, constraint_records=default_constraint_records())
    lexeme = " \t6.040e1\r\n"
    craft_value(temporal, value_json=lexeme, json_type="number")
    result = cn.constraint_evaluation(CON_A, as_of=LATE)
    assert result.candidates[0].observed_decimal == "60.4"
    occurrence = (result.semantic_compatibility.candidates[0].value_candidate
                  .state_candidate.bound.observed.occurrence)
    assert occurrence.value_json == lexeme
    assert "lexeme" not in result.candidates[0].model_dump()


def test_discovery_serializes_es_and_declarations_once(tmp_path):
    records = (
        constraint_registration(constraint_anchor_id=CON_A),
        constraint_declaration(constraint_anchor_id=CON_A),
        constraint_registration(constraint_anchor_id=CON_B),
        constraint_declaration(constraint_anchor_id=CON_B),
    )
    cn, _, _, _ = cn_stack(tmp_path, constraint_records=records)
    result = cn.variable_constraint_evaluations(HOTEND, as_of=AS_OF)
    payload = json.loads(result.model_dump_json())
    assert payload["semantic_compatibility"] is not None
    assert len(payload["evaluations"]) == 2
    assert all("semantic_compatibility" not in row for row in payload["evaluations"])
    assert all("constraint" not in row for row in payload["evaluations"])
    assert [row["constraint_index"] for row in payload["evaluations"]] == [0, 1]
    text = result.model_dump_json()
    assert text.count('"ruleset_version":"es001.1"') == 1
    assert text.count('"record_kind":"variable_constraint_declaration"') == 2


class TestDiscoveryAuthority:
    def _result(self, tmp_path):
        records = (
            constraint_registration(constraint_anchor_id=CON_A),
            constraint_declaration(constraint_anchor_id=CON_A),
            constraint_registration(constraint_anchor_id=CON_B),
            constraint_declaration(constraint_anchor_id=CON_B),
        )
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=records)
        return cn.variable_constraint_evaluations(HOTEND, as_of=AS_OF)

    @pytest.mark.parametrize("mutation", ["missing", "duplicate", "reordered"])
    def test_entry_count_order_and_indices_are_authoritative(
            self, tmp_path, mutation):
        result = self._result(tmp_path)
        entries = result.evaluations
        if mutation == "missing":
            forged = entries[:1]
        elif mutation == "duplicate":
            forged = (entries[0], entries[0])
        else:
            forged = tuple(reversed(entries))
        with pytest.raises(Exception):
            type(result)(**{
                **result.model_dump(mode="python"), "evaluations": forged})

    def test_anchor_substitution_and_candidate_forgery_rejected(self, tmp_path):
        result = self._result(tmp_path)
        first = result.evaluations[0]
        wrong_anchor = first.model_copy(update={"constraint_anchor_id": CON_B})
        with pytest.raises(Exception):
            type(result)(**{
                **result.model_dump(mode="python"),
                "evaluations": (wrong_anchor, result.evaluations[1])})
        wrong_row = first.candidates[0].model_copy(update={"verdict": "violated"})
        forged = first.model_copy(update={"candidates": (wrong_row,)})
        with pytest.raises(Exception):
            type(result)(**{
                **result.model_dump(mode="python"),
                "evaluations": (forged, result.evaluations[1])})

    def test_mixed_cutoff_variable_and_revision_rejected(self, tmp_path):
        from datetime import timedelta
        from tests.model_kernel.test_demo_model import PRE_ES001_MEMBERSHIP
        from backend.model_kernel import ModelStore
        from pathlib import Path
        result = self._result(tmp_path)
        for update in (
            {"as_of": result.as_of + timedelta(seconds=1)},
            {"variable_anchor_id": "var_" + "f" * 32},
            {"constraint_collection": result.constraint_collection.model_copy(
                update={"revision": ModelStore(Path("models/demo-printer")).replay(
                    PRE_ES001_MEMBERSHIP).revision})},
        ):
            with pytest.raises(Exception):
                type(result)(**{**result.model_dump(mode="python"), **update})
