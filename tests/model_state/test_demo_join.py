"""VM-001 committed-demo end-to-end join: the COMMITTED model (10
records) + the COMMITTED bindings/demo-printer set + the accepted
Moonraker fixture evidence, answering the milestone's product question
for the real hotend-temperature variable."""

from datetime import UTC, datetime
from pathlib import Path

from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import ModelStore
from backend.model_state import ModelStateQueries

from tests.model_state.helpers import observed_stack

HOTEND = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
EXTRUDER = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
AS_OF = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)  # inside [20:00, 21:00)


class TestCommittedDemoJoin:
    def test_committed_demo_hotend_variable_end_to_end(self, tmp_path):
        model = ModelStore(Path("models/demo-printer")).load()
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        temporal = observed_stack(tmp_path)
        queries = ModelStateQueries(model, resolver, temporal)

        result = queries.variable_state(HOTEND, as_of=AS_OF,
                                        entity_anchor_id=EXTRUDER)
        assert result.model_membership == "registered"
        assert result.requested_entity_agreement == "matches_owner"
        assert result.anchor_agreement == "exact"
        assert result.binding_discovery == "declared_candidates"
        assert result.observation_availability == "observed"
        assert result.selection == "single"
        [candidate] = result.candidates
        assert candidate.property.json_pointer == (
            "/result/status/extruder/temperature")
        assert candidate.bound.resolution.status == "bound"
        assert candidate.bound.resolution.resolved_target.anchor_id == HOTEND
        assert candidate.attachment == "attached"
        # provenance to the raw evidence
        occurrence = candidate.bound.observed.occurrence
        assert occurrence.payload_checksum.startswith("sha256:")
        assert temporal.provenance(
            occurrence.occurrence_id).raw_record_id == (
            occurrence.raw_record_id)
        # the observed value is real evidence, carried verbatim — never
        # converted or interpreted
        assert occurrence.value_json  # a JSON number string from the source

    def test_committed_demo_old_revision_is_honest_limbo(self, tmp_path):
        """Replaying the committed pre-variable revision against the SAME
        evidence: knowledge context changes, evidence stays, attachment is
        refused honestly."""
        store = ModelStore(Path("models/demo-printer"))
        old_ids = [record_id for record_id
                   in store.load().revision.record_ids
                   if not record_id.startswith("vrg_")]
        replayed = store.replay(old_ids)
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        temporal = observed_stack(tmp_path)
        queries = ModelStateQueries(replayed, resolver, temporal)

        result = queries.variable_state(HOTEND, as_of=AS_OF)
        assert result.model_membership == "not_registered"
        assert result.observation_availability == "observed"
        assert result.candidates[0].attachment == (
            "not_attachable_variable_unregistered")
