"""IB-001 bound temporal facade: verbatim TS-001 objects joined with
resolutions computed at each observation's own receipt time."""

from datetime import UTC, datetime

import pytest

from backend.identity_binding.canonical import build_record
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    DeclaredBoundary,
)
from backend.identity_binding.facade import BoundTemporalQueries
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import (
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalQueryError,
)
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import happy_script, make_runner

E1 = "ent_" + "1" * 32
E2 = "ent_" + "2" * 32
V1 = "var_" + "3" * 32
V2 = "var_" + "4" * 32
RECORDED = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
AS_OF = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")


def temporal_stack(tmp_path):
    runner, ds_store, transport = make_runner(tmp_path / "ds", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db",
                             evidence_root=ds_store.base_dir)
    projector = TemporalProjector(ds_store, temporal)
    return runner, projector, TemporalQueries(temporal)


def interval(start, end):
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=DeclaredBoundary(kind="declared", at=start),
        end_boundary=DeclaredBoundary(kind="declared", at=end),
        interval_semantics="half_open")


def declarations(entity=E1, variable=V1):
    return [
        build_record(AnchorDeclaration, anchor_kind="entity",
                     anchor=EntityAnchor(anchor_id=entity,
                                         namespace="demo-printer",
                                         display_name="Extruder unit",
                                         referent_kind="physical_instance"),
                     recorded_at=RECORDED, authority=AUTHORITY),
        build_record(AnchorDeclaration, anchor_kind="variable",
                     anchor=VariableAnchor(anchor_id=variable,
                                           entity_anchor_id=entity,
                                           namespace="demo-printer",
                                           display_name="Hotend temperature"),
                     recorded_at=RECORDED, authority=AUTHORITY),
    ]


def property_assertion(applies, target=V1):
    return build_record(BindingAssertion, binding_kind="property",
                        subject=SUBJECT, property=PROP,
                        target_anchor_id=target, applies=applies,
                        recorded_at=RECORDED, authority=AUTHORITY)


def facade_with(tmp_path, queries, *records):
    store = BindingStore(tmp_path / "demo-printer")
    for record in records:
        store.append(record)
    return BoundTemporalQueries(BindingResolver(store.load()), queries)


class TestLatestObserved:
    def test_verbatim_observation_with_bound_resolution(self, tmp_path):
        runner, projector, queries = temporal_stack(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        direct = queries.latest_observed(SUBJECT, PROP, AS_OF)
        hour = interval(datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC),
                        datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC))
        facade = facade_with(tmp_path, queries, *declarations(),
                             property_assertion(hour))
        bound = facade.latest_observed(SUBJECT, PROP, AS_OF)
        assert bound.observed == direct  # the TS-001 object, verbatim
        assert bound.resolution.status == "bound"
        assert bound.resolution.resolved_target.anchor_id == V1
        assert bound.resolution.applicability_basis == "declared_interval"
        assert bound.resolution.revision.record_count == 3

    def test_resolution_time_is_receipt_time_not_as_of(self, tmp_path):
        """The binding hour contains the observation's received_at but not
        as_of: still bound. An interval containing as_of but not the
        receipt: not bound. Resolution never uses the query clock."""
        runner, projector, queries = temporal_stack(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        late_as_of = datetime(2026, 9, 15, 12, 0, 0, tzinfo=UTC)
        hour = interval(datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC),
                        datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC))
        facade = facade_with(tmp_path, queries, *declarations(),
                             property_assertion(hour))
        assert facade.latest_observed(
            SUBJECT, PROP, late_as_of).resolution.status == "bound"

        wrong_hour = interval(datetime(2026, 9, 15, 0, 0, 0, tzinfo=UTC),
                              datetime(2026, 9, 16, 0, 0, 0, tzinfo=UTC))
        facade2 = facade_with(
            tmp_path.joinpath("second"), queries, *declarations(),
            property_assertion(wrong_hour))
        result = facade2.latest_observed(SUBJECT, PROP, late_as_of)
        assert result.resolution.status == "outside_applicability"
        assert result.observed == queries.latest_observed(
            SUBJECT, PROP, late_as_of)  # limbo never hides the observation

    def test_unbound_still_returns_observation(self, tmp_path):
        runner, projector, queries = temporal_stack(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        facade = facade_with(tmp_path, queries)  # empty binding set
        result = facade.latest_observed(SUBJECT, PROP, AS_OF)
        assert result.resolution.status == "unbound"
        assert result.observed.occurrence.value_json  # evidence intact

    def test_none_when_nothing_observed(self, tmp_path):
        _, _, queries = temporal_stack(tmp_path)
        facade = facade_with(tmp_path, queries)
        assert facade.latest_observed(SUBJECT, PROP, AS_OF) is None

    def test_naive_as_of_still_rejected_by_temporal_layer(self, tmp_path):
        runner, projector, queries = temporal_stack(tmp_path)
        runner.run("printer-1")
        projector.project("printer-1")
        facade = facade_with(tmp_path, queries)
        with pytest.raises(TemporalQueryError):
            facade.latest_observed(SUBJECT, PROP, datetime(2026, 8, 7, 23, 0))


class TestHistory:
    def test_per_occurrence_resolution_spans_a_replacement(self, tmp_path):
        runner, projector, queries = temporal_stack(tmp_path)
        runner.run("printer-1")
        runner.run("printer-1")
        projector.project("printer-1")
        occurrences = queries.history(SUBJECT, PROP)
        assert len(occurrences) == 2
        boundary = occurrences[1].received_at  # half-open: 2nd → new anchor
        first_scope = interval(
            datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC), boundary)
        second_scope = interval(
            boundary, datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC))
        records = [
            *declarations(entity=E1, variable=V1),
            *declarations(entity=E2, variable=V2),
            property_assertion(first_scope, target=V1),
            property_assertion(second_scope, target=V2),
        ]
        facade = facade_with(tmp_path, queries, *records)
        bound_history = facade.history(SUBJECT, PROP)
        assert [b.occurrence for b in bound_history] == occurrences  # verbatim
        assert bound_history[0].resolution.resolved_target.anchor_id == V1
        assert bound_history[1].resolution.resolved_target.anchor_id == V2
        # one history, honestly split at the declared boundary
        assert all(b.resolution.status == "bound" for b in bound_history)
