"""VM-001 model_state facade: model-variable-first bound state over the
real accepted Moonraker evidence path. Matrix sections E (bound-state
behavior) and F (cross-time). Nothing here converts, aggregates, ranks,
or manufactures a value — every claim is per-candidate and composed
verbatim from accepted lower-layer results."""

from datetime import UTC, datetime

import pytest

from backend.identity_binding.facade import BoundTemporalQueries
from backend.model_state import (
    ModelStateError,
    ModelStateQueries,
    SourceSelector,
    VariableStateResult,
)
from backend.temporal_state.contracts import TemporalStoreError

from tests.model_state.helpers import (
    AS_OF,
    BEFORE_RECEIPT,
    E1,
    E2,
    PROP_TARGET,
    PROP_TEMP,
    SUBJECT,
    V1,
    V2,
    UNKNOWN_START,
    entity_declaration,
    hour,
    model_with,
    observed_stack,
    prop_assertion,
    resolver_with,
    retraction,
    standard_bindings,
    state_queries,
    var_declaration,
)


class TestHappyPath:
    def test_registered_bound_observation_end_to_end(self, tmp_path):
        queries, resolver, temporal = state_queries(tmp_path)
        result = queries.variable_state(V1, as_of=AS_OF)

        assert result.model_membership == "registered"
        assert result.binding_discovery == "declared_candidates"
        assert result.observation_availability == "observed"
        assert result.selection == "single"
        assert result.selector_declaration == "not_applicable"
        assert result.requested_entity_membership == "not_supplied"
        assert result.anchor_agreement == "exact"
        assert result.divergent_anchor_fields == ()
        assert result.declared_locator_count == 1
        assert result.binding_revision == resolver.loaded.revision

        [candidate] = result.candidates
        assert candidate.origin == "declared_binding"
        assert (candidate.subject, candidate.property) == (SUBJECT, PROP_TEMP)
        # amendment 1: the exact reverse-discovery entry, verbatim
        assert candidate.declaration == resolver.declared_property_locators(
            V1).locators[0]
        assert candidate.declared_via_assertion_ids == tuple(
            s.record_id for s in candidate.declaration.assertion_summaries
            if s.target_anchor_id == V1)
        # the bound temporal object is the IB facade result, whole-object
        direct = BoundTemporalQueries(resolver, temporal).latest_observed(
            SUBJECT, PROP_TEMP, AS_OF)
        assert candidate.bound == direct
        assert candidate.attachment == "attached"

        # verbatim model composition
        assert result.variable_registration.anchor.anchor_id == V1
        assert result.owner_registration.anchor.anchor_id == E1
        assert result.model_revision.record_count == 2

        # provenance end to end: occurrence -> raw record -> checksum
        occurrence = candidate.bound.observed.occurrence
        chain = temporal.provenance(occurrence.occurrence_id)
        assert chain.raw_record_id == occurrence.raw_record_id
        assert chain.payload_checksum == occurrence.payload_checksum
        assert occurrence.payload_checksum.startswith("sha256:")

    def test_resolution_at_received_at_not_as_of(self, tmp_path):
        """F2 + E10: a far-future cutoff yields an older, staler bound
        observation — never outside_applicability, because resolution runs
        at the occurrence's in-window received_at. The latest-per-locator
        limitation in action, stated honestly."""
        queries, resolver, temporal = state_queries(tmp_path)
        late = datetime(2026, 9, 15, 12, 0, 0, tzinfo=UTC)
        result = queries.variable_state(V1, as_of=late)
        [candidate] = result.candidates
        assert candidate.bound.resolution.status == "bound"
        assert candidate.attachment == "attached"
        assert candidate.bound.observed.staleness_seconds > 30 * 24 * 3600
        earlier = queries.variable_state(V1, as_of=AS_OF).candidates[0]
        assert (candidate.bound.resolution.status
                == earlier.bound.resolution.status)


class TestHonestAbsence:
    def test_registered_but_unbound(self, tmp_path):
        queries, _, _ = state_queries(
            tmp_path,
            binding_records=(entity_declaration(), var_declaration()))
        result = queries.variable_state(V1, as_of=AS_OF)
        assert result.model_membership == "registered"
        assert result.binding_discovery == "no_declared_candidates"
        assert result.observation_availability == "not_evaluated"
        assert result.selection == "none"
        assert result.candidates == ()
        assert result.declared_locator_count == 0

    def test_binding_but_nothing_before_cutoff(self, tmp_path):
        queries, _, _ = state_queries(tmp_path)
        result = queries.variable_state(V1, as_of=BEFORE_RECEIPT)
        assert result.binding_discovery == "declared_candidates"
        assert result.observation_availability == "none_before_cutoff"
        assert result.selection == "single"
        [candidate] = result.candidates
        assert candidate.bound is None
        assert candidate.attachment == "not_evaluated"

    def test_anchor_unknown_to_binding_set(self, tmp_path):
        queries, _, _ = state_queries(
            tmp_path, binding_records=(entity_declaration(),))
        result = queries.variable_state(V1, as_of=AS_OF)
        assert result.model_membership == "registered"
        assert result.binding_discovery == "anchor_unknown_to_binding_set"
        assert result.anchor_agreement == "binding_declaration_absent"
        assert result.binding_declared_anchor is None
        assert result.candidates == ()


class TestEvidenceInLimbo:
    def test_unregistered_variable_with_real_evidence_first_class(
            self, tmp_path):
        """Mandatory correction 1: the model does not contain the variable,
        yet discovery, querying, and resolution all still run; the
        observation is returned in identity/model limbo with an honest
        attachment status — never suppressed, never fabricated into
        membership, never described as model state."""
        store = model_with(tmp_path, variables=())  # entity only, no vrg
        queries, resolver, temporal = state_queries(
            tmp_path, model_store=store)
        result = queries.variable_state(V1, as_of=AS_OF)

        assert result.model_membership == "not_registered"
        assert result.variable_registration is None
        assert result.owner_registration is None
        assert result.anchor_agreement == "model_registration_absent"
        assert result.binding_declared_anchor is not None  # still inspectable
        assert result.binding_discovery == "declared_candidates"
        assert result.observation_availability == "observed"
        [candidate] = result.candidates
        direct = BoundTemporalQueries(resolver, temporal).latest_observed(
            SUBJECT, PROP_TEMP, AS_OF)
        assert candidate.bound == direct  # evidence carried verbatim
        assert candidate.bound.resolution.status == "bound"
        assert candidate.attachment == "not_attachable_variable_unregistered"

    def test_latest_occurrence_resolving_elsewhere_disclosed(self, tmp_path):
        """A shared locator whose only ACTIVE assertion targets V2: the
        latest observation resolves to V2, and V1's answer says exactly
        that — a resolution mismatch, not 'no observation ever'."""
        mine = prop_assertion(target=V1)
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2), mine, retraction(mine),
                   prop_assertion(target=V2, note="rebound"))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        result = queries.variable_state(V1, as_of=AS_OF)
        assert result.observation_availability == "observed"
        [candidate] = result.candidates
        assert candidate.bound.resolution.status == "bound"
        assert candidate.bound.resolution.resolved_target.anchor_id == V2
        assert candidate.attachment == "not_attachable_resolution_mismatch"

    def test_conflicted_binding_not_suppressed(self, tmp_path):
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2), prop_assertion(target=V1),
                   prop_assertion(target=V2, note="competing"))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        [candidate] = queries.variable_state(V1, as_of=AS_OF).candidates
        assert candidate.bound.resolution.status == "conflicted"
        assert candidate.attachment == (
            "not_attachable_resolution_nonpositive")

    def test_outside_applicability_not_suppressed(self, tmp_path):
        records = (entity_declaration(), var_declaration(),
                   prop_assertion(applies=hour(0, 23, day=1)))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        [candidate] = queries.variable_state(V1, as_of=AS_OF).candidates
        assert candidate.bound is not None  # evidence intact
        assert candidate.bound.resolution.status == "outside_applicability"
        assert candidate.attachment == (
            "not_attachable_resolution_nonpositive")

    def test_applicability_unknown_carried(self, tmp_path):
        records = (entity_declaration(), var_declaration(),
                   prop_assertion(applies=UNKNOWN_START))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        [candidate] = queries.variable_state(V1, as_of=AS_OF).candidates
        assert candidate.bound.resolution.status == "applicability_unknown"
        assert candidate.attachment == (
            "not_attachable_resolution_nonpositive")

    def test_anchor_divergence_inspectable_and_blocking(self, tmp_path):
        """Correction 6: the binding set declares a DIFFERENT display name.
        Both anchors inspectable verbatim, differing fields named, nothing
        reconciled — and attachment is refused as unsafe."""
        records = (entity_declaration(),
                   var_declaration(name="Hotend temp (renamed)"),
                   prop_assertion())
        queries, resolver, _ = state_queries(
            tmp_path, binding_records=records)
        result = queries.variable_state(V1, as_of=AS_OF)
        assert result.anchor_agreement == "divergent"
        assert result.divergent_anchor_fields == ("display_name",)
        assert result.binding_declared_anchor.display_name == (
            "Hotend temp (renamed)")
        assert result.variable_registration.anchor.display_name == (
            "Hotend temperature")
        [candidate] = result.candidates
        assert candidate.bound.resolution.status == "bound"
        assert candidate.attachment == "not_attachable_anchor_divergent"


class TestMultiplicityAndSelectors:
    def test_multiple_candidates_all_surfaced_never_ranked(self, tmp_path):
        records = (entity_declaration(), var_declaration(),
                   prop_assertion(prop=PROP_TARGET),
                   prop_assertion(prop=PROP_TEMP))
        queries, resolver, _ = state_queries(
            tmp_path, binding_records=records)
        result = queries.variable_state(V1, as_of=AS_OF)
        assert result.selection == "multiple"
        assert result.declared_locator_count == 2
        assert len(result.candidates) == 2
        # order is the locator sort of the discovery result — never recency
        discovery = resolver.declared_property_locators(V1)
        assert [(c.subject, c.property) for c in result.candidates] == [
            (e.subject, e.property) for e in discovery.locators]
        assert result.observation_availability == "observed"

    def test_explicit_selector_declared_for_requested(self, tmp_path):
        queries, resolver, _ = state_queries(tmp_path)
        result = queries.variable_state(
            V1, as_of=AS_OF,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP))
        assert result.binding_discovery == "explicit_selector"
        assert result.selection == "explicit"
        assert result.selector_declaration == (
            "ever_declared_for_requested_variable")
        assert result.declared_locator_count == 1  # multiplicity not hidden
        [candidate] = result.candidates
        assert candidate.origin == "explicit_selector"
        assert candidate.declaration is not None
        assert candidate.declared_via_assertion_ids
        assert candidate.attachment == "attached"

    def test_explicit_selector_declared_for_other_variable(self, tmp_path):
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2), prop_assertion(target=V2))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        result = queries.variable_state(
            V1, as_of=AS_OF,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP))
        assert result.selector_declaration == (
            "ever_declared_for_other_variable")
        [candidate] = result.candidates
        assert candidate.declaration is not None  # the OTHER declaration
        assert candidate.declared_via_assertion_ids == ()
        assert candidate.bound.resolution.resolved_target.anchor_id == V2
        assert candidate.attachment == "not_attachable_resolution_mismatch"

    def test_explicit_undeclared_selector_executed_and_disclosed(
            self, tmp_path):
        """Owner decision 4 + correction 5: an undeclared locator is
        inspected diagnostically; nothing manufactures a binding."""
        queries, _, _ = state_queries(
            tmp_path,
            binding_records=(entity_declaration(), var_declaration()))
        result = queries.variable_state(
            V1, as_of=AS_OF,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP))
        assert result.selector_declaration == "undeclared"
        [candidate] = result.candidates
        assert candidate.declaration is None
        assert candidate.declared_via_assertion_ids == ()
        assert candidate.bound is not None  # the evidence itself is real
        assert candidate.bound.resolution.status == "unbound"
        assert candidate.attachment == (
            "not_attachable_resolution_nonpositive")


class TestRequestedEntity:
    def test_matching_owner(self, tmp_path):
        queries, _, _ = state_queries(tmp_path)
        result = queries.variable_state(V1, as_of=AS_OF,
                                        entity_anchor_id=E1)
        assert result.requested_entity_membership == "registered"
        assert result.requested_entity_agreement == "matches_owner"
        assert result.requested_entity_registration.anchor.anchor_id == E1

    def test_registered_non_owner_never_stops_the_evidence(self, tmp_path):
        store = model_with(tmp_path, entities=((E1, "Extruder unit"),
                                               (E2, "Other unit")))
        queries, _, _ = state_queries(tmp_path, model_store=store)
        result = queries.variable_state(V1, as_of=AS_OF,
                                        entity_anchor_id=E2)
        assert result.requested_entity_membership == "registered"
        assert result.requested_entity_agreement == "differs_from_owner"
        assert result.requested_entity_registration.anchor.anchor_id == E2
        assert result.observation_availability == "observed"  # continued
        assert result.candidates[0].attachment == "attached"

    def test_unregistered_supplied_entity(self, tmp_path):
        queries, _, _ = state_queries(tmp_path)
        result = queries.variable_state(V1, as_of=AS_OF,
                                        entity_anchor_id=E2)
        assert result.requested_entity_membership == "not_registered"
        assert result.requested_entity_agreement == "differs_from_owner"
        assert result.requested_entity_registration is None
        assert result.observation_availability == "observed"

    def test_owner_unavailable_when_variable_unregistered(self, tmp_path):
        store = model_with(tmp_path, variables=())
        queries, _, _ = state_queries(tmp_path, model_store=store)
        result = queries.variable_state(V1, as_of=AS_OF,
                                        entity_anchor_id=E1)
        assert result.model_membership == "not_registered"
        assert result.requested_entity_membership == "registered"
        assert result.requested_entity_agreement == "owner_unavailable"


class TestCrossTime:
    def test_replacement_interval_split_honestly(self, tmp_path):
        """F1: one locator, receipt-split intervals V1 then V2. At a late
        cutoff the LATEST occurrence resolves to V2: V2 attaches, V1
        reports a mismatch — 'no latest candidate observation attachable',
        never 'no observation ever'."""
        temporal = observed_stack(tmp_path, runs=2)
        occurrences = temporal.history(SUBJECT, PROP_TEMP)
        assert len(occurrences) == 2
        boundary = occurrences[1].received_at
        first_scope = hour()
        first_scope = first_scope.model_copy(update={
            "end_boundary": first_scope.end_boundary.model_copy(
                update={"at": boundary})})
        second_scope = hour().model_copy(update={
            "start_boundary": hour().start_boundary.model_copy(
                update={"at": boundary})})
        records = (entity_declaration(), var_declaration(V1),
                   var_declaration(V2),
                   prop_assertion(target=V1, applies=first_scope),
                   prop_assertion(target=V2, applies=second_scope))
        store = model_with(
            tmp_path, variables=((V1, E1, "Hotend temperature"),
                                 (V2, E1, "Hotend temperature")))
        queries, _, _ = state_queries(tmp_path, temporal=temporal,
                                      binding_records=records,
                                      model_store=store)
        for_v2 = queries.variable_state(V2, as_of=AS_OF)
        assert for_v2.candidates[0].attachment == "attached"
        for_v1 = queries.variable_state(V1, as_of=AS_OF)
        assert for_v1.observation_availability == "observed"
        assert for_v1.candidates[0].attachment == (
            "not_attachable_resolution_mismatch")

    def test_later_ingestion_cannot_rewrite_an_earlier_cutoff(self, tmp_path):
        from tests.identity_binding.test_facade import temporal_stack

        runner, projector, temporal = temporal_stack(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        cutoff = temporal.history(SUBJECT, PROP_TEMP)[0].received_at
        queries, _, _ = state_queries(tmp_path, temporal=temporal)
        before = queries.variable_state(V1, as_of=cutoff).model_dump()
        runner.run("printer-1")
        projector.project("printer-1")
        assert len(temporal.history(SUBJECT, PROP_TEMP)) == 2  # not vacuous
        after = queries.variable_state(V1, as_of=cutoff).model_dump()
        assert after == before

    def test_model_revision_is_not_a_temporal_cutoff(self, tmp_path):
        """F4: replaying the pre-variable model revision changes membership
        knowledge only — full evidence exists, the answer is honest
        not_registered limbo, and no cutoff is silently selected."""
        store = model_with(tmp_path)
        loaded = store.load()
        old_ids = [record_id for record_id in loaded.revision.record_ids
                   if record_id.startswith("reg_")]
        replayed = store.replay(old_ids)
        temporal = observed_stack(tmp_path)
        resolver = resolver_with(tmp_path, *standard_bindings())
        from backend.model_state import ModelStateQueries

        old_view = ModelStateQueries(replayed, resolver, temporal)
        result = old_view.variable_state(V1, as_of=AS_OF)
        assert result.model_membership == "not_registered"
        assert result.model_revision == replayed.revision
        assert result.observation_availability == "observed"  # limbo
        new_view = ModelStateQueries(loaded, resolver, temporal)
        assert new_view.variable_state(
            V1, as_of=AS_OF).model_membership == "registered"


class TestTypedFailures:
    def test_temporal_store_unavailable_propagates_unchanged(self, tmp_path):
        temporal = observed_stack(tmp_path)
        queries, _, _ = state_queries(tmp_path, temporal=temporal)
        db = temporal.store.db_path
        db.unlink()
        for suffix in ("-wal", "-shm"):
            side = db.with_name(db.name + suffix)
            if side.exists():
                side.unlink()
        with pytest.raises(TemporalStoreError) as excinfo:
            queries.variable_state(V1, as_of=AS_OF)
        assert excinfo.value.error_code == "TEMPORAL_STORE_UNAVAILABLE"
        assert not isinstance(excinfo.value, ModelStateError)

    def test_naive_as_of_typed_before_any_store_access(self, tmp_path):
        temporal = observed_stack(tmp_path)
        queries, _, _ = state_queries(tmp_path, temporal=temporal)
        temporal.store.db_path.unlink()
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_state(V1, as_of=datetime(2026, 8, 7, 23, 0))
        assert excinfo.value.error_code == "MODEL_STATE_NAIVE_AS_OF"

    @pytest.mark.parametrize("kwargs", [
        pytest.param({"variable_anchor_id": E1}, id="entity_id"),
        pytest.param({"variable_anchor_id": None}, id="none_id"),
        pytest.param({"variable_anchor_id": 3}, id="int_id"),
        pytest.param({"entity_anchor_id": V1}, id="var_as_entity"),
        pytest.param({"entity_anchor_id": 3}, id="int_entity"),
        pytest.param({"source": "printer-1"}, id="str_selector"),
        pytest.param({"source": {"subject": None}}, id="dict_selector"),
        pytest.param({"as_of": "2026-08-07"}, id="str_as_of"),
    ])
    def test_malformed_inputs_typed(self, tmp_path, kwargs):
        queries, _, _ = state_queries(tmp_path)
        call = {"variable_anchor_id": V1, "as_of": AS_OF, **kwargs}
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_state(call.pop("variable_anchor_id"), **call)
        assert excinfo.value.error_code == "MODEL_STATE_INPUT_INVALID"

    @pytest.mark.parametrize("bad", [
        pytest.param(("model",), id="model"),
        pytest.param(("resolver",), id="resolver"),
        pytest.param(("temporal",), id="temporal"),
    ])
    def test_constructor_type_validated(self, tmp_path, bad):
        from backend.model_state import ModelStateQueries

        temporal = observed_stack(tmp_path)
        resolver = resolver_with(tmp_path, *standard_bindings())
        loaded = model_with(tmp_path).load()
        args = {"model": loaded, "resolver": resolver, "temporal": temporal}
        args[bad[0]] = object()
        with pytest.raises(ModelStateError) as excinfo:
            ModelStateQueries(**args)
        assert excinfo.value.error_code == "MODEL_STATE_INPUT_INVALID"


class TestGateRepairs:
    def test_forged_selector_rejected_at_entry(self, tmp_path):
        """R3: a model_construct selector forgery fails as INPUT_INVALID —
        never a downstream binding/temporal error code."""
        queries, _, _ = state_queries(tmp_path)
        forged = SourceSelector.model_construct(subject="nope",
                                                property="nope")
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_state(V1, as_of=AS_OF, source=forged)
        assert excinfo.value.error_code == "MODEL_STATE_INPUT_INVALID"

    def test_naive_as_of_utcoffset_none_clause(self, tmp_path):
        from datetime import tzinfo as tzinfo_cls

        class _NoOffset(tzinfo_cls):
            def utcoffset(self, dt):
                return None

            def dst(self, dt):
                return None

        queries, _, _ = state_queries(tmp_path)
        hostile = datetime(2026, 8, 7, 23, 0, tzinfo=_NoOffset())
        with pytest.raises(ModelStateError) as excinfo:
            queries.variable_state(V1, as_of=hostile)
        assert excinfo.value.error_code == "MODEL_STATE_NAIVE_AS_OF"

    def test_explicit_selector_discloses_declared_multiplicity(
            self, tmp_path):
        """Selector mode with TWO declared locators: the count says so."""
        from tests.model_state.helpers import (entity_declaration,
                                               prop_assertion,
                                               var_declaration)

        records = (entity_declaration(), var_declaration(),
                   prop_assertion(prop=PROP_TEMP),
                   prop_assertion(prop=PROP_TARGET))
        queries, _, _ = state_queries(tmp_path, binding_records=records)
        result = queries.variable_state(
            V1, as_of=AS_OF,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP))
        assert result.selection == "explicit"
        assert len(result.candidates) == 1
        assert result.declared_locator_count == 2  # multiplicity disclosed
