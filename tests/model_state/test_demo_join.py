"""VM-001 committed-demo end-to-end join: the COMMITTED model (10
records) + the COMMITTED bindings/demo-printer set + accepted Moonraker
evidence, answering the milestone's product question for the real
hotend-temperature variable.

The completion demonstration uses the COMPLETE accepted three-occurrence
timeline (60.1 / 60.1 / 60.4). The single-sweep variants below are
deliberately smaller fixtures and are labelled as such — a one-sweep
projection is never presented as the full timeline."""

from datetime import UTC, datetime
from pathlib import Path

from backend.identity_binding.facade import BoundTemporalQueries
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import ModelStore
from backend.model_state import ModelStateQueries

from tests.model_state.helpers import (
    PROP_TEMP,
    SUBJECT,
    full_timeline_stack,
    observed_stack,
)

HOTEND = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
EXTRUDER = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
AS_OF = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)  # inside [20:00, 21:00)

# the accepted timeline's LATEST occurrence at any cutoff >= 20:00:18 —
# every id below is content-derived and deterministic
LATEST_VALUE = "60.4"
LATEST_RECEIVED_AT = datetime(2026, 8, 7, 20, 0, 18, tzinfo=UTC)
LATEST_OCCURRENCE_ID = "cd2579c5bca1c1f71f0170eaa73c74fb"
LATEST_ATTEMPT_ID = "971cf9dd7a595e13c5a74ba505ad92be"
LATEST_OBSERVATION_ID = "297be88ea705222d9b03b97733276774"
LATEST_RAW_RECORD_ID = "698aa72a05a317e62b62274ffcb3bbfb"
LATEST_CHECKSUM = ("sha256:6771710d0a97db795a53192e1c6d463937deaa8c11e6fce3"
                   "d35285d69114caf2")


class TestCompleteTimelineJoin:
    """The VM-001 completion demonstration: the full accepted timeline."""

    def test_full_timeline_selects_the_latest_occurrence_through_both_layers(
            self, tmp_path):
        temporal = full_timeline_stack(tmp_path)

        # the projection really is the complete accepted timeline
        history = temporal.history(SUBJECT, PROP_TEMP)
        assert [(o.received_at.isoformat(), o.value_json, o.change_class)
                for o in history] == [
            ("2026-08-07T20:00:06+00:00", "60.1", "first_seen"),
            ("2026-08-07T20:00:12+00:00", "60.1", "unchanged"),
            ("2026-08-07T20:00:18+00:00", "60.4", "changed"),
        ]

        # 1) direct temporal lookup selects the 20:00:18 occurrence
        direct = temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF)
        assert direct.occurrence.value_json == LATEST_VALUE
        assert direct.occurrence.received_at == LATEST_RECEIVED_AT

        # 2) model-state selects the SAME occurrence, and carries the
        #    bound temporal object verbatim
        model = ModelStore(Path("models/demo-printer")).load()
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        bound_direct = BoundTemporalQueries(resolver, temporal).latest_observed(
            SUBJECT, PROP_TEMP, AS_OF)
        result = ModelStateQueries(model, resolver, temporal).variable_state(
            HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
        [candidate] = result.candidates
        assert candidate.bound == bound_direct          # whole-object
        assert candidate.bound.observed == direct       # whole-object
        occurrence = candidate.bound.observed.occurrence
        assert occurrence == direct.occurrence

        # 3) the exact occurrence, attempt, observation, raw record, checksum
        assert occurrence.value_json == LATEST_VALUE
        assert occurrence.received_at == LATEST_RECEIVED_AT
        assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
        assert occurrence.attempt_id == LATEST_ATTEMPT_ID
        assert occurrence.observation_id == LATEST_OBSERVATION_ID
        assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
        assert occurrence.payload_checksum == LATEST_CHECKSUM
        chain = temporal.provenance(occurrence.occurrence_id)
        assert (chain.attempt_id, chain.observation_id, chain.raw_record_id,
                chain.payload_checksum) == (
            LATEST_ATTEMPT_ID, LATEST_OBSERVATION_ID, LATEST_RAW_RECORD_ID,
            LATEST_CHECKSUM)

        # 4) attached to the requested REGISTERED variable
        assert result.model_membership == "registered"
        assert result.requested_entity_agreement == "matches_owner"
        assert result.anchor_agreement == "exact"
        assert result.observation_availability == "observed"
        assert candidate.bound.resolution.status == "bound"
        assert candidate.bound.resolution.resolved_target.anchor_id == HOTEND
        assert candidate.attachment == "attached"

    def test_no_recency_selection_happens_above_the_temporal_layer(
            self, tmp_path):
        """model_state adds no ordering of its own: at three cutoffs the
        model-state occurrence is byte-equal to the direct temporal one."""
        temporal = full_timeline_stack(tmp_path)
        model = ModelStore(Path("models/demo-printer")).load()
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        queries = ModelStateQueries(model, resolver, temporal)
        for cutoff, expected in (
                (datetime(2026, 8, 7, 20, 0, 9, tzinfo=UTC), "60.1"),
                (datetime(2026, 8, 7, 20, 0, 15, tzinfo=UTC), "60.1"),
                (AS_OF, "60.4")):
            direct = temporal.latest_observed(SUBJECT, PROP_TEMP, cutoff)
            [candidate] = queries.variable_state(
                HOTEND, as_of=cutoff).candidates
            assert candidate.bound.observed == direct
            assert candidate.bound.observed.occurrence.value_json == expected


class TestCommittedDemoJoin:
    def test_single_sweep_projection_joins_end_to_end(self, tmp_path):
        """Smaller fixture: ONE sweep, therefore one occurrence (60.1 at
        20:00:06) — a single-sweep projection, not the full timeline."""
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
        assert candidate.bound.observed.occurrence.value_json == "60.1"
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
        """Replaying the committed pre-variable revision against the full
        accepted timeline: knowledge context changes, evidence stays,
        attachment is refused honestly."""
        # HD1 (SN-001): explicit membership, never a prefix filter — a
        # vrg_/vsp_ filter would silently select 12 of 14 records while
        # this docstring claims the 9-record pre-variable revision
        from tests.model_kernel.test_demo_model import (
            FROZEN_MK001_RECORDS,
            PRE_VARIABLE_REVISION,
        )
        store = ModelStore(Path("models/demo-printer"))
        old_ids = tuple(name[:-5] for name in FROZEN_MK001_RECORDS)
        replayed = store.replay(old_ids)
        assert replayed.revision.revision_id == PRE_VARIABLE_REVISION
        assert replayed.revision.record_count == 9
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        temporal = full_timeline_stack(tmp_path)
        queries = ModelStateQueries(replayed, resolver, temporal)

        result = queries.variable_state(HOTEND, as_of=AS_OF)
        assert result.model_membership == "not_registered"
        assert result.observation_availability == "observed"
        assert result.candidates[0].bound.observed.occurrence.value_json == (
            LATEST_VALUE)  # the real latest evidence, in limbo
        assert result.candidates[0].attachment == (
            "not_attachable_variable_unregistered")
