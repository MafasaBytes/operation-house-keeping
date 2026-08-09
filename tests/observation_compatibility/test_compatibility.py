"""VS-001 compatibility behaviour: composition, evidence consistency,
value shape, and the independent unit dimensions."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.model_kernel import ModelQueries, ModelStore
from backend.model_state import ModelStateQueries, SourceSelector
from backend.model_state.contracts import ModelStateError
from backend.observation_compatibility import (
    ObservationCompatibilityConfigurationError,
    ObservationCompatibilityError,
    ObservationCompatibilityQueries,
    VariableValueCompatibilityResult,
)

from tests.observation_compatibility.helpers import (
    AS_OF,
    E1,
    NO_UNIT,
    PROP_TARGET,
    PROP_TEMP,
    SUBJECT,
    V1,
    compatibility,
    craft_occurrence,
    entity_declaration,
    model_with,
    observed_stack,
    observed_value,
    resolver_with,
    unit,
    var_declaration,
)

BEFORE = datetime(2026, 8, 7, 19, 0, 0, tzinfo=UTC)


def only(result):
    assert len(result.candidates) == 1
    return result.candidates[0]


class TestComposition:
    def test_lower_layer_results_are_carried_whole_object_equal(self, tmp_path):
        queries, state, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)

        assert result.state == state.variable_state(V1, as_of=AS_OF)
        assert result.specification_result == ModelQueries(
            state.model).variable_value_specification(V1)
        assert result.ruleset_version == "vs001.1"
        assert only(result).state_candidate == result.state.candidates[0]

    def test_one_revision_governs_membership_and_specification(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert (result.specification_result.revision
                == result.state.model_revision)

    def test_no_second_status_vocabulary_is_serialized(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        for banned in ("specification_availability", "conflicting_specifications",
                       "superseded_specification_ids", "specification"):
            assert banned not in VariableValueCompatibilityResult.model_fields

    def test_no_aggregate_or_selected_value_fields_exist(self, tmp_path):
        from backend.observation_compatibility import (
            CandidateValueCompatibility)

        for model in (VariableValueCompatibilityResult,
                      CandidateValueCompatibility):
            for banned in ("value", "current_value", "normalized_value",
                           "unit_filled_value", "winner", "current", "usable"):
                assert banned not in model.model_fields

    def test_candidates_are_index_parallel(self, tmp_path):
        records = (entity_declaration(), var_declaration(),
                   prop_two := __import__(
                       "tests.model_state.helpers", fromlist=["x"]
                   ).prop_assertion())
        queries, state, _ = compatibility(tmp_path,
                                          binding_records=records)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert [c.state_candidate for c in result.candidates] == list(
            result.state.candidates)


class TestSpecificationAvailability:
    def test_specified_number_satisfied(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.specification_result.status == "specified"
        assert candidate.value_presence == "value_present"
        assert candidate.evidence_consistency == "consistent"
        assert candidate.observed_shape == "number"
        assert candidate.value_shape_compatibility == "satisfies_value_shape"
        assert candidate.value_shape_finding == "shape_matches"
        assert candidate.value_shape_not_evaluated_reason is None

    def test_not_specified(self, tmp_path):
        store = model_with(tmp_path, specifications=())
        queries, _, _ = compatibility(tmp_path, model_store=store)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.specification_result.status == "not_specified"
        assert result.model_unit_specification == "not_evaluated"
        assert candidate.value_shape_compatibility == "not_evaluated"
        assert candidate.value_shape_not_evaluated_reason == (
            "specification_not_available")
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "specification_not_available")
        # the evidence itself is still fully present
        assert candidate.state_candidate.bound is not None
        assert candidate.value_presence == "value_present"

    def test_not_registered_variable(self, tmp_path):
        store = model_with(tmp_path, specifications=(), variables=())
        queries, _, _ = compatibility(tmp_path, model_store=store)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert result.specification_result.status == "not_registered"
        assert result.state.model_membership == "not_registered"
        # attachment is refused first, and that clause precedes the
        # specification clause by the approved precedence
        assert only(result).state_candidate.attachment == (
            "not_attachable_variable_unregistered")
        assert only(result).value_shape_not_evaluated_reason == (
            "observation_not_attached")


class TestConflictDoesNotOverridePrecedence:
    """Final condition 1: a conflicted specification suppresses verdicts,
    but the reason is still the first applicable clause."""

    def conflicted_model(self, tmp_path):
        return model_with(tmp_path, specifications=(
            ("number", False, None), ("string", False, NO_UNIT)))

    def test_conflicted_with_attached_observation(self, tmp_path):
        queries, _, _ = compatibility(
            tmp_path, model_store=self.conflicted_model(tmp_path))
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.specification_result.status == "conflicted"
        assert len(result.specification_result.conflicting_specifications) == 2
        assert result.model_unit_specification == "not_evaluated"
        assert candidate.state_candidate.attachment == "attached"
        assert candidate.value_shape_compatibility == "not_evaluated"
        assert candidate.declared_unit_lexeme_relation == "not_evaluated"
        assert candidate.value_shape_not_evaluated_reason == (
            "specification_conflicted")
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "specification_conflicted")
        # evidence untouched
        assert candidate.state_candidate.bound.observed.occurrence.value_json

    def test_conflicted_with_no_observation(self, tmp_path):
        queries, _, _ = compatibility(
            tmp_path, model_store=self.conflicted_model(tmp_path))
        result = queries.variable_value_compatibility(V1, as_of=BEFORE)
        candidate = only(result)
        assert result.specification_result.status == "conflicted"
        assert candidate.state_candidate.bound is None
        assert candidate.value_shape_not_evaluated_reason == "no_observation"
        assert candidate.unit_lexeme_not_evaluated_reason == "no_observation"
        assert candidate.value_presence == "no_observation"

    def test_conflicted_with_unattached_observation(self, tmp_path):
        """A binding that resolves to a different variable leaves the
        observation unattached; that clause precedes the conflict."""
        from tests.model_state.helpers import prop_assertion

        V2 = "var_" + "4" * 32
        # both assertions sit on the SAME locator, so discovery finds it for
        # V1 while resolution is conflicted and attachment is refused
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2), prop_assertion(target=V1),
                   prop_assertion(target=V2, note="competing"))
        queries, _, _ = compatibility(
            tmp_path, model_store=self.conflicted_model(tmp_path),
            binding_records=records)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.specification_result.status == "conflicted"
        assert candidate.state_candidate.attachment != "attached"
        assert candidate.value_shape_not_evaluated_reason == (
            "observation_not_attached")
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "observation_not_attached")

    def test_every_tip_is_carried_verbatim_while_conflicted(self, tmp_path):
        store = self.conflicted_model(tmp_path)
        queries, _, _ = compatibility(tmp_path, model_store=store)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        loaded = store.load()
        assert set(result.specification_result.conflicting_specifications) == (
            set(loaded.current_specification_tips_by_variable[V1]))


class TestValueShape:
    @pytest.mark.parametrize("literal,shape,expected,finding", [
        pytest.param("60.4", "number", "satisfies_value_shape",
                     "shape_matches", id="number_ok"),
        pytest.param("60", "number", "satisfies_value_shape",
                     "shape_matches", id="integer_lexeme_is_a_number"),
        pytest.param("0", "number", "satisfies_value_shape",
                     "shape_matches", id="zero"),
        pytest.param("6e2", "number", "satisfies_value_shape",
                     "shape_matches", id="exponent_is_a_number"),
        pytest.param('"60.4"', "number", "does_not_satisfy_value_shape",
                     "shape_differs", id="numeric_string_never_coerced"),
        pytest.param("true", "number", "does_not_satisfy_value_shape",
                     "shape_differs", id="boolean_never_satisfies_number"),
        pytest.param("false", "boolean", "satisfies_value_shape",
                     "shape_matches", id="false_is_a_boolean"),
        pytest.param('""', "string", "satisfies_value_shape",
                     "shape_matches", id="empty_string"),
        pytest.param("[1,2]", "number", "does_not_satisfy_value_shape",
                     "unsupported_observed_structure", id="array"),
        pytest.param('{"a":1}', "number", "does_not_satisfy_value_shape",
                     "unsupported_observed_structure", id="object"),
    ])
    def test_shape_matrix(self, tmp_path, literal, shape, expected, finding):
        temporal = observed_value(tmp_path, literal)
        store = model_with(tmp_path, specifications=((shape, False, None),))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      model_store=store)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.value_presence == "value_present"
        assert candidate.evidence_consistency == "consistent"
        assert candidate.value_shape_compatibility == expected
        assert candidate.value_shape_finding == finding

    @pytest.mark.parametrize("nullable,expected,finding", [
        pytest.param(True, "satisfies_value_shape", "explicit_null_allowed",
                     id="nullable"),
        pytest.param(False, "does_not_satisfy_value_shape",
                     "explicit_null_not_allowed", id="not_nullable"),
    ])
    def test_explicit_null_follows_nullable(self, tmp_path, nullable,
                                            expected, finding):
        temporal = observed_value(tmp_path, "null")
        store = model_with(tmp_path,
                           specifications=(("number", nullable, None),))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      model_store=store)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.value_presence == "explicit_null"
        assert candidate.observed_shape == "null"
        assert candidate.value_shape_compatibility == expected
        assert candidate.value_shape_finding == finding

    def test_no_observation_is_distinct_from_null_and_absence(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        candidate = only(queries.variable_value_compatibility(V1, as_of=BEFORE))
        assert candidate.value_presence == "no_observation"
        assert candidate.observed_shape is None
        assert candidate.evidence_consistency == "not_evaluated"
        assert candidate.value_shape_not_evaluated_reason == "no_observation"

    def test_large_magnitudes_never_become_infinity(self, tmp_path):
        temporal = observed_value(tmp_path, "1e999")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.observed_shape == "number"
        assert candidate.value_shape_compatibility == "satisfies_value_shape"

    def test_very_long_integer_never_overflows(self, tmp_path):
        temporal = observed_value(tmp_path, "9" * 400)
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.observed_shape == "number"


class TestEvidenceIntegrity:
    """Contradictory evidence is NOT ordinary incompatibility."""

    def test_json_type_disagrees_with_the_lexeme(self, tmp_path):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json='"60.4"', json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "shape_disagreement"
        assert candidate.value_presence == "indeterminate"
        assert candidate.observed_shape is None
        assert candidate.value_shape_compatibility == "not_evaluated"
        assert candidate.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")

    def test_unrecognized_json_type(self, tmp_path):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="60.4", json_type="integer")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "json_type_unrecognized"
        assert candidate.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")

    @pytest.mark.parametrize("lexeme", [
        pytest.param("NaN", id="nan"),
        pytest.param("Infinity", id="infinity"),
        pytest.param("-Infinity", id="negative_infinity"),
        pytest.param("", id="empty"),
        pytest.param("007", id="leading_zeros"),
        pytest.param("+5", id="leading_plus"),
        pytest.param("1.", id="trailing_point"),
    ])
    def test_malformed_value_json(self, tmp_path, lexeme):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json=lexeme, json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_json_malformed"
        assert candidate.value_presence == "indeterminate"
        assert candidate.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")

    def test_contradictory_evidence_is_not_reported_as_incompatible(
            self, tmp_path):
        """The contrast that matters: an honest mismatch says
        does_not_satisfy; contradictory evidence says not_evaluated."""
        mismatch = observed_value(tmp_path / "a", '"60.4"')
        store = model_with(tmp_path, specifications=(("number", False, None),))
        queries, _, _ = compatibility(tmp_path / "a", temporal=mismatch,
                                      model_store=store)
        honest = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert honest.value_shape_compatibility == (
            "does_not_satisfy_value_shape")

        contradictory = observed_stack(tmp_path / "b")
        craft_occurrence(contradictory, value_json='"60.4"',
                         json_type="number")
        queries_b, _, _ = compatibility(tmp_path / "b",
                                        temporal=contradictory,
                                        model_store=store)
        confused = only(queries_b.variable_value_compatibility(V1, as_of=AS_OF))
        assert confused.value_shape_compatibility == "not_evaluated"
        assert confused.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")

    def test_evidence_is_never_repaired(self, tmp_path):
        temporal = observed_stack(tmp_path)
        crafted = craft_occurrence(temporal, value_json='"60.4"',
                                   json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        occurrence = only(queries.variable_value_compatibility(
            V1, as_of=AS_OF)).state_candidate.bound.observed.occurrence
        assert occurrence.value_json == crafted.value_json
        assert occurrence.json_type == crafted.json_type


class TestUnitDimensions:
    def test_model_declared_source_absent(self, tmp_path):
        """The real shape of the accepted evidence path."""
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.model_unit_specification == "declared"
        assert candidate.source_unit_evidence == "absent"
        assert candidate.declared_unit_lexeme_relation == "not_evaluated"
        assert candidate.unit_lexeme_not_evaluated_reason == "source_unit_absent"

    def test_identical_lexeme(self, tmp_path):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="60.4", json_type="number",
                         declared_unit="degree_celsius")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.source_unit_evidence == "present"
        assert candidate.declared_unit_lexeme_relation == (
            "declared_lexeme_identical")
        assert candidate.unit_lexeme_not_evaluated_reason is None

    @pytest.mark.parametrize("supplied", [
        pytest.param("kelvin", id="different_unit"),
        pytest.param("Degree_Celsius", id="case_lookalike"),
        pytest.param("DEGREE_CELSIUS", id="upper_lookalike"),
        pytest.param(" degree_celsius", id="leading_space"),
        pytest.param("degree_celsius ", id="trailing_space"),
        pytest.param("°C", id="display_symbol"),
        pytest.param("project_local", id="system_id_is_not_the_code"),
        pytest.param("ohk-units-1", id="edition_is_not_the_code"),
    ])
    def test_differing_lexemes(self, tmp_path, supplied):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="60.4", json_type="number",
                         declared_unit=supplied)
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.declared_unit_lexeme_relation == (
            "declared_lexeme_differs")

    def test_model_not_declared(self, tmp_path):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="60.4", json_type="number",
                         declared_unit="degree_celsius")
        store = model_with(tmp_path,
                           specifications=(("number", False, NO_UNIT),))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      model_store=store)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert result.model_unit_specification == "not_declared"
        assert candidate.source_unit_evidence == "present"
        assert candidate.declared_unit_lexeme_relation == "not_evaluated"
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "model_unit_not_declared")

    def test_model_side_absence_governs_when_neither_supplies_a_unit(
            self, tmp_path):
        store = model_with(tmp_path,
                           specifications=(("number", False, NO_UNIT),))
        queries, _, _ = compatibility(tmp_path, model_store=store)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.source_unit_evidence == "absent"
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "model_unit_not_declared")

    def test_unit_survives_malformed_value_evidence(self, tmp_path):
        """Final condition 2's independence rule: a malformed value_json
        does not erase an explicitly supplied source unit, and the lexical
        comparison still runs."""
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="NaN", json_type="number",
                         declared_unit="degree_celsius")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_json_malformed"
        assert candidate.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")
        assert candidate.source_unit_evidence == "present"
        assert candidate.declared_unit_lexeme_relation == (
            "declared_lexeme_identical")
        assert candidate.unit_lexeme_not_evaluated_reason is None

    def test_unattached_observation_still_discloses_its_unit(self, tmp_path):
        from tests.model_state.helpers import prop_assertion

        V2 = "var_" + "4" * 32
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="60.4", json_type="number",
                         declared_unit="degree_celsius")
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2), prop_assertion(target=V1),
                   prop_assertion(target=V2, note="competing"))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      binding_records=records)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.state_candidate.attachment != "attached"
        assert candidate.source_unit_evidence == "present"      # disclosed
        assert candidate.declared_unit_lexeme_relation == "not_evaluated"
        assert candidate.unit_lexeme_not_evaluated_reason == (
            "observation_not_attached")

    def test_the_model_unit_never_enters_the_evidence(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        evidence = only(result).state_candidate.model_dump_json()
        assert "degree_celsius" not in evidence
        assert "ohk-units-1" not in evidence
        assert "project_local" not in evidence
        occurrence = only(result).state_candidate.bound.observed.occurrence
        assert occurrence.declared_unit is None

    def test_no_unit_is_inferred_from_names_or_pointers(self, tmp_path):
        """The variable is named hotend-temperature and the pointer says
        temperature; neither is a unit."""
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        candidate = only(result)
        assert "temperature" in candidate.state_candidate.property.json_pointer
        assert candidate.source_unit_evidence == "absent"


class TestErrorSurface:
    @pytest.mark.parametrize("bad", [
        pytest.param(None, id="none"), pytest.param("state", id="str"),
        pytest.param(object(), id="object"),
    ])
    def test_constructor_type_is_validated(self, bad):
        with pytest.raises(ObservationCompatibilityError) as excinfo:
            ObservationCompatibilityQueries(bad)
        assert isinstance(excinfo.value,
                          ObservationCompatibilityConfigurationError)
        assert excinfo.value.error_code == (
            "OBSERVATION_COMPATIBILITY_INPUT_INVALID")

    def test_naive_cutoff_propagates_the_accepted_typed_error(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_value_compatibility(
                V1, as_of=datetime(2026, 8, 7, 23, 0))
        assert excinfo.value.error_code == "MODEL_STATE_NAIVE_AS_OF"

    def test_forged_selector_never_leaks_a_raw_validation_error(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        forged = SourceSelector.model_construct(subject="nope", property="x")
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_value_compatibility(V1, as_of=AS_OF,
                                                 source=forged)
        assert excinfo.value.error_code == "MODEL_STATE_INPUT_INVALID"

    @pytest.mark.parametrize("bad", [
        pytest.param(E1, id="entity_id"), pytest.param(None, id="none"),
        pytest.param(123, id="int"),
    ])
    def test_malformed_variable_id_propagates_typed(self, tmp_path, bad):
        queries, _, _ = compatibility(tmp_path)
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_value_compatibility(bad, as_of=AS_OF)
        assert excinfo.value.error_code == "MODEL_STATE_INPUT_INVALID"

    def test_malformed_evidence_is_an_outcome_not_an_exception(self, tmp_path):
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="not json at all",
                         json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_json_malformed"


class TestResultInvariants:
    def test_valid_result_revalidates(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert VariableValueCompatibilityResult(**result.model_dump()) == result

    def test_a_verdict_without_a_specification_is_unconstructible(self,
                                                                  tmp_path):
        store = model_with(tmp_path, specifications=())
        queries, _, _ = compatibility(tmp_path, model_store=store)
        dumped = queries.variable_value_compatibility(
            V1, as_of=AS_OF).model_dump()
        dumped["candidates"][0].update(
            value_shape_compatibility="satisfies_value_shape",
            value_shape_finding="shape_matches",
            value_shape_not_evaluated_reason=None)
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(**dumped)

    def test_a_reason_is_required_when_a_dimension_is_not_evaluated(
            self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        dumped = queries.variable_value_compatibility(
            V1, as_of=AS_OF).model_dump()
        dumped["candidates"][0]["unit_lexeme_not_evaluated_reason"] = None
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(**dumped)

    def test_candidate_reordering_is_rejected(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        dumped = queries.variable_value_compatibility(
            V1, as_of=AS_OF).model_dump()
        dumped["candidates"] = ()
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(**dumped)

    def test_source_unit_evidence_must_match_the_occurrence(self, tmp_path):
        queries, _, _ = compatibility(tmp_path)
        dumped = queries.variable_value_compatibility(
            V1, as_of=AS_OF).model_dump()
        dumped["candidates"][0]["source_unit_evidence"] = "present"
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(**dumped)


class TestGateRepairs:
    """Findings accepted from the acceptance audit and the adversarial
    review."""

    def test_deep_nesting_is_an_outcome_not_a_recursion_error(self, tmp_path):
        """Reviewer F1: json's scanner raises RecursionError, which is not a
        ValueError and escaped the typed contract."""
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="[" * 20000 + "]" * 20000,
                         json_type="array")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_not_representable"
        assert candidate.value_presence == "indeterminate"
        assert candidate.value_shape_not_evaluated_reason == (
            "evidence_not_assessable")

    @pytest.mark.parametrize("lexeme", [
        pytest.param("9" * 5000, id="beyond_int_max_str_digits"),
        pytest.param("1E+" + "9" * 400, id="exponent_decimal_rejects"),
    ])
    def test_well_formed_but_unrepresentable_is_not_called_malformed(
            self, tmp_path, lexeme):
        """Reviewer F2: the evidence is valid JSON; this interpreter cannot
        represent it. Calling that 'malformed' states a false fact about
        the stored bytes."""
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json=lexeme, json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_not_representable"

    def test_non_finite_constants_remain_malformed(self, tmp_path):
        """NaN is not JSON at all — that IS malformed, and must stay
        distinguishable from the unrepresentable case."""
        temporal = observed_stack(tmp_path)
        craft_occurrence(temporal, value_json="NaN", json_type="number")
        queries, _, _ = compatibility(tmp_path, temporal=temporal)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.evidence_consistency == "value_json_malformed"

    def test_mutating_the_injected_model_cannot_desynchronize_the_result(
            self, tmp_path):
        """Reviewer F3: the kernel query is now built per call from the
        state facade's current model, so the two halves cannot disagree."""
        queries, state, _ = compatibility(tmp_path)
        other = model_with(tmp_path, specifications=(), name="other").load()
        state.model = other
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert result.specification_result.revision == result.state.model_revision
        assert result.specification_result.status == "not_specified"

    def test_this_modules_own_contracts_reject_forged_instances(self,
                                                                tmp_path):
        """Reviewer F5, honestly scoped: revalidate_instances hardens the
        contracts THIS module owns."""
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        forged = result.candidates[0].model_copy(
            update={"value_presence": "totally_made_up"})
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(
                **{**result.model_dump(), "candidates": (forged,)})

    def test_carried_lower_layer_objects_are_trusted_by_their_producer(
            self, tmp_path):
        """The honest boundary: `revalidate_instances` is read from the
        model being validated, so it cannot reach model_state's own types
        (which this milestone must leave byte-unchanged). Those objects are
        trusted because the accepted facades produce them — a caller never
        supplies one. Pinned so the trust is explicit rather than assumed."""
        from backend.observation_compatibility import (
            CandidateValueCompatibility)

        queries, _, _ = compatibility(tmp_path)
        real = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        forged = real.state_candidate.model_copy(
            update={"attachment": "totally_made_up"})
        carried = CandidateValueCompatibility(
            **{**real.model_dump(), "state_candidate": forged})
        assert carried.state_candidate.attachment == "totally_made_up"

    def test_the_result_is_not_hashable_and_that_is_documented(self, tmp_path):
        """frozen=True synthesizes __hash__, but the carried temporal
        occurrence holds a list. Pinned so a consumer learns it here."""
        queries, _, _ = compatibility(tmp_path)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        with pytest.raises(TypeError):
            hash(result)


class TestMultipleCandidates:
    """Both gates flagged that no test ever produced more than one
    candidate, leaving the index-parallel invariant unexercised."""

    def two_locator_bindings(self):
        from tests.model_state.helpers import PROP_TARGET, prop_assertion

        return (entity_declaration(), var_declaration(),
                prop_assertion(prop=PROP_TEMP),
                prop_assertion(prop=PROP_TARGET)), PROP_TARGET

    def test_candidates_stay_separate_and_ordered(self, tmp_path):
        records, _ = self.two_locator_bindings()
        queries, state, _ = compatibility(tmp_path, binding_records=records)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        assert len(result.candidates) == 2
        assert result.state.selection == "multiple"
        assert [c.state_candidate for c in result.candidates] == list(
            result.state.candidates)
        pointers = [c.state_candidate.property.json_pointer
                    for c in result.candidates]
        assert pointers == sorted(pointers)          # never reordered
        for candidate in result.candidates:
            assert candidate.value_shape_compatibility == (
                "satisfies_value_shape")

    def test_verdicts_are_independent_per_candidate(self, tmp_path):
        """One locator carries a malformed value; the other is unaffected."""
        records, prop_target = self.two_locator_bindings()
        temporal = observed_stack(tmp_path)
        existing = temporal.history(SUBJECT, prop_target)[-1]
        from datetime import timedelta

        from backend.temporal_state.contracts import TemporalOccurrence

        crafted = TemporalOccurrence(
            **{**existing.model_dump(), "occurrence_id": "e" * 32,
               "observation_id": "f" * 32,
               "received_at": existing.received_at + timedelta(seconds=30),
               "finished_at": existing.finished_at + timedelta(seconds=30),
               "value_json": "NaN", "json_type": "number",
               "previous_occurrence_id": existing.occurrence_id,
               "change_class": "changed"})
        with temporal.store.writer() as conn:
            temporal.store.insert_occurrence(conn, crafted)

        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      binding_records=records)
        result = queries.variable_value_compatibility(V1, as_of=AS_OF)
        by_pointer = {c.state_candidate.property.json_pointer: c
                      for c in result.candidates}
        broken = by_pointer[prop_target.json_pointer]
        intact = by_pointer[PROP_TEMP.json_pointer]
        assert broken.evidence_consistency == "value_json_malformed"
        assert broken.value_shape_compatibility == "not_evaluated"
        assert intact.evidence_consistency == "consistent"
        assert intact.value_shape_compatibility == "satisfies_value_shape"

    def test_reordering_candidates_is_rejected(self, tmp_path):
        records, _ = self.two_locator_bindings()
        queries, _, _ = compatibility(tmp_path, binding_records=records)
        dumped = queries.variable_value_compatibility(
            V1, as_of=AS_OF).model_dump()
        dumped["candidates"] = tuple(reversed(dumped["candidates"]))
        with pytest.raises(ValidationError):
            VariableValueCompatibilityResult(**dumped)


class TestFullShapeMatrix:
    """The audit found only 9 of 21 shape-table cells exercised."""

    @pytest.mark.parametrize("spec_shape", ["boolean", "number", "string"])
    @pytest.mark.parametrize("literal,observed", [
        pytest.param("true", "boolean", id="boolean"),
        pytest.param("60.4", "number", id="number"),
        pytest.param('"text"', "string", id="string"),
        pytest.param("[1,2]", "array", id="array"),
        pytest.param('{"a":1}', "object", id="object"),
    ])
    def test_every_cell(self, tmp_path, spec_shape, literal, observed):
        temporal = observed_value(tmp_path, literal)
        store = model_with(tmp_path,
                           specifications=((spec_shape, False, None),))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      model_store=store)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.observed_shape == observed
        if observed in ("array", "object"):
            expected, finding = ("does_not_satisfy_value_shape",
                                 "unsupported_observed_structure")
        elif observed == spec_shape:
            expected, finding = "satisfies_value_shape", "shape_matches"
        else:
            expected, finding = "does_not_satisfy_value_shape", "shape_differs"
        assert candidate.value_shape_compatibility == expected
        assert candidate.value_shape_finding == finding

    @pytest.mark.parametrize("spec_shape", ["boolean", "number", "string"])
    def test_explicit_null_against_every_shape(self, tmp_path, spec_shape):
        temporal = observed_value(tmp_path, "null")
        store = model_with(tmp_path,
                           specifications=((spec_shape, True, None),))
        queries, _, _ = compatibility(tmp_path, temporal=temporal,
                                      model_store=store)
        candidate = only(queries.variable_value_compatibility(V1, as_of=AS_OF))
        assert candidate.value_shape_finding == "explicit_null_allowed"
