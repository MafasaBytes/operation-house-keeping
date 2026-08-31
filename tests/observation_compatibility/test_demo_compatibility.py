"""VS-001 completion demonstration over the COMMITTED model, the
COMMITTED binding set, and the complete accepted three-occurrence
Moonraker timeline (60.1 / 60.1 / 60.4).

The whole point of the milestone is visible here: the model declares a
unit, the source supplied none, and the system says exactly that instead
of manufacturing Celsius."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import ModelQueries, ModelStore
from backend.model_state import ModelStateQueries
from backend.observation_compatibility import ObservationCompatibilityQueries

from tests.model_state.helpers import PROP_TEMP, SUBJECT, full_timeline_stack

HOTEND = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
EXTRUDER = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
AS_OF = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)
SPECIFICATION_ID = ("vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c389"
                    "53f971ff62ba0")
LATEST_OCCURRENCE_ID = "cd2579c5bca1c1f71f0170eaa73c74fb"
LATEST_ATTEMPT_ID = "971cf9dd7a595e13c5a74ba505ad92be"
LATEST_RAW_RECORD_ID = "698aa72a05a317e62b62274ffcb3bbfb"
LATEST_CHECKSUM = ("sha256:6771710d0a97db795a53192e1c6d463937deaa8c11e6fce3"
                   "d35285d69114caf2")


def committed(tmp_path, *, model=None):
    temporal = full_timeline_stack(tmp_path)
    loaded = (model if model is not None
              else ModelStore(Path("models/demo-printer")).load())
    resolver = BindingResolver(
        BindingStore(Path("bindings/demo-printer")).load())
    state = ModelStateQueries(loaded, resolver, temporal)
    return ObservationCompatibilityQueries(state), state, temporal


class TestCommittedDemonstration:
    def test_the_complete_vs001_chain(self, tmp_path):
        queries, state, temporal = committed(tmp_path)
        result = queries.variable_value_compatibility(
            HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
        [candidate] = result.candidates
        occurrence = candidate.state_candidate.bound.observed.occurrence

        # registered model variable -> one governing specification
        assert result.state.model_membership == "registered"
        assert result.specification_result.status == "specified"
        assert result.specification_result.specification.record_id == (
            SPECIFICATION_ID)

        # -> attached latest observation 60.4
        assert candidate.state_candidate.attachment == "attached"
        assert occurrence.value_json == "60.4"
        assert occurrence.received_at == datetime(2026, 8, 7, 20, 0, 18,
                                                  tzinfo=UTC)

        # -> internally consistent JSON number -> satisfies the shape
        assert candidate.evidence_consistency == "consistent"
        assert candidate.value_presence == "value_present"
        assert candidate.observed_shape == "number"
        assert candidate.value_shape_compatibility == "satisfies_value_shape"
        assert candidate.value_shape_finding == "shape_matches"
        assert candidate.value_shape_not_evaluated_reason is None

        # -> model unit declared, source unit absent, no lexical relation
        assert result.model_unit_specification == "declared"
        assert candidate.source_unit_evidence == "absent"
        assert candidate.declared_unit_lexeme_relation == "not_evaluated"
        assert candidate.unit_lexeme_not_evaluated_reason == "source_unit_absent"

        # -> unchanged raw provenance
        assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
        assert occurrence.attempt_id == LATEST_ATTEMPT_ID
        assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
        assert occurrence.payload_checksum == LATEST_CHECKSUM
        chain = temporal.provenance(occurrence.occurrence_id)
        assert (chain.raw_record_id, chain.payload_checksum) == (
            LATEST_RAW_RECORD_ID, LATEST_CHECKSUM)

    def test_celsius_is_never_manufactured(self, tmp_path):
        """The model's unit identity appears nowhere in the evidence."""
        queries, _, _ = committed(tmp_path)
        result = queries.variable_value_compatibility(HOTEND, as_of=AS_OF)
        [candidate] = result.candidates
        evidence = candidate.state_candidate.model_dump_json()
        for token in ("degree_celsius", "ohk-units-1", "project_local",
                      "celsius", "Celsius"):
            assert token not in evidence
        assert candidate.state_candidate.bound.observed.occurrence.\
            declared_unit is None
        # and the specification still says what the MODEL requires
        assert (result.specification_result.specification.unit.unit.code
                == "degree_celsius")

    def test_lower_layer_results_are_whole_object_equal(self, tmp_path):
        queries, state, _ = committed(tmp_path)
        result = queries.variable_value_compatibility(HOTEND, as_of=AS_OF)
        assert result.state == state.variable_state(HOTEND, as_of=AS_OF)
        assert result.specification_result == ModelQueries(
            state.model).variable_value_specification(HOTEND)

    def test_nothing_is_normalized_converted_filled_or_selected(self, tmp_path):
        queries, _, temporal = committed(tmp_path)
        result = queries.variable_value_compatibility(HOTEND, as_of=AS_OF)
        occurrence = result.candidates[0].state_candidate.bound.observed\
            .occurrence
        direct = temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF)
        assert occurrence == direct.occurrence      # byte-identical evidence
        assert occurrence.value_json == "60.4"      # not 60.4 the float
        assert isinstance(occurrence.value_json, str)

    def test_pre_specification_replay_is_attached_but_unspecified(self,
                                                                  tmp_path):
        # RP2/HD1: explicit membership, never a prefix filter (a vsp_
        # filter would silently select 13 of 14 records post-SN-001)
        from tests.model_kernel.test_demo_model import (
            PRE_SPECIFICATION_MEMBERSHIP,
            PRE_SPECIFICATION_REVISION,
        )
        store = ModelStore(Path("models/demo-printer"))
        replayed = store.replay(PRE_SPECIFICATION_MEMBERSHIP)
        assert replayed.revision.revision_id == PRE_SPECIFICATION_REVISION
        assert replayed.revision.record_count == 10
        queries, _, _ = committed(tmp_path, model=replayed)
        result = queries.variable_value_compatibility(HOTEND, as_of=AS_OF)
        [candidate] = result.candidates
        assert result.specification_result.status == "not_specified"
        assert candidate.state_candidate.attachment == "attached"
        assert candidate.state_candidate.bound.observed.occurrence\
            .value_json == "60.4"
        assert candidate.value_shape_compatibility == "not_evaluated"
        assert candidate.value_shape_not_evaluated_reason == (
            "specification_not_available")

    def test_no_observation_before_the_first_receipt(self, tmp_path):
        queries, _, _ = committed(tmp_path)
        result = queries.variable_value_compatibility(
            HOTEND, as_of=datetime(2026, 8, 7, 19, 0, tzinfo=UTC))
        [candidate] = result.candidates
        assert result.specification_result.status == "specified"
        assert candidate.value_presence == "no_observation"
        assert candidate.value_shape_not_evaluated_reason == "no_observation"
        assert candidate.unit_lexeme_not_evaluated_reason == "no_observation"

    def test_no_accepted_record_hash_changed(self):
        """The specification is additive: every previously committed record
        still verifies against its content-derived id."""
        from backend.model_kernel.canonical import verify_record_id

        loaded = ModelStore(Path("models/demo-printer")).load()
        assert loaded.revision.record_count == 34
        for record in loaded.records.values():
            assert verify_record_id(record), record.record_id
