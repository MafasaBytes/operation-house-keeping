"""VM-001 result-contract invariants: contradictory dimension
combinations are unconstructible, and the amendment-1 declaration
validators bind declared_via_assertion_ids to the carried entry."""

import pytest
from pydantic import ValidationError

from backend.model_state import VariableStateResult

from tests.model_state.helpers import AS_OF, V1, state_queries


@pytest.fixture()
def happy(tmp_path):
    queries, _, _ = state_queries(tmp_path)
    return queries.variable_state(V1, as_of=AS_OF)


def rebuild(result, **updates):
    return VariableStateResult(**{**result.model_dump(), **updates})


class TestCrossFieldInvariants:
    def test_valid_result_revalidates(self, happy):
        assert rebuild(happy) == happy

    def test_not_registered_requires_absent_registrations(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, model_membership="not_registered")

    def test_registration_never_fabricated_for_not_registered(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, model_membership="not_registered",
                    owner_registration=None,
                    anchor_agreement="model_registration_absent")

    def test_observed_requires_a_bound_candidate(self, happy):
        dumped = happy.model_dump()
        for candidate in dumped["candidates"]:
            candidate["bound"] = None
            candidate["attachment"] = "not_evaluated"
        with pytest.raises(ValidationError):
            VariableStateResult(**dumped)  # still claims "observed"

    def test_selection_counts_candidates(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, selection="multiple")  # one candidate
        with pytest.raises(ValidationError):
            rebuild(happy, selection="none")

    def test_explicit_mode_is_all_or_nothing(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, selection="explicit")  # discovery-origin candidate
        with pytest.raises(ValidationError):
            rebuild(happy, binding_discovery="explicit_selector")

    def test_divergence_names_fields_exactly_when_divergent(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, divergent_anchor_fields=("display_name",))
        with pytest.raises(ValidationError):
            rebuild(happy, anchor_agreement="divergent")

    def test_binding_revision_must_match_candidate_resolutions(self, happy):
        dumped = happy.model_dump()
        dumped["binding_revision"]["record_ids"] = ()
        dumped["binding_revision"]["record_count"] = 0
        with pytest.raises(ValidationError):
            VariableStateResult(**dumped)

    def test_attached_requires_exact_agreement(self, happy):
        dumped = happy.model_dump()
        dumped["anchor_agreement"] = "binding_declaration_absent"
        dumped["binding_declared_anchor"] = None
        with pytest.raises(ValidationError):
            VariableStateResult(**dumped)  # candidate still says attached

    def test_declared_via_ids_bound_to_the_carried_declaration(self, happy):
        dumped = happy.model_dump()
        dumped["candidates"][0]["declared_via_assertion_ids"] = (
            "iba_" + "0" * 64,)
        with pytest.raises(ValidationError):
            VariableStateResult(**dumped)
        dumped = happy.model_dump()
        dumped["candidates"][0]["declaration"] = None
        with pytest.raises(ValidationError):
            VariableStateResult(**dumped)  # discovery candidate needs it

    def test_requested_entity_trio_consistent(self, happy):
        with pytest.raises(ValidationError):
            rebuild(happy, requested_entity_membership="registered")
        with pytest.raises(ValidationError):
            rebuild(happy, requested_entity_agreement="matches_owner")

    def test_no_aggregate_value_field_exists(self, happy):
        assert "value" not in VariableStateResult.model_fields
        assert "current_value" not in VariableStateResult.model_fields
        assert not any("value" == name
                       for name in VariableStateResult.model_fields)
