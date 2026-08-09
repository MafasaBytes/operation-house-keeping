"""Fixture tiers for the VS-001 compatibility suite.

Tier R — real committed data.
Tier P — a synthetic payload through the REAL accepted ingestion path at
         the real committed binding target: no forgery, genuine
         `attached` status, any JSON value.
Tier C — a crafted store row through the public writer, required only for
         what no adapter can produce: a non-None declared_unit (so EVERY
         lexical-relation case is synthetic), non-finite constants, an
         unrecognized json_type, and json_type/shape disagreements.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import (
    AuthorityRef,
    DeclaredUnit,
    EntityRegistration,
    ModelStore,
    OwnerDeclarationEvidence,
    UnitNotDeclared,
    UnitReference,
    VariableRegistration,
    VariableValueSpecification,
    build_record,
)
from backend.model_state import ModelStateQueries
from backend.observation_compatibility import ObservationCompatibilityQueries
from tests.model_state.helpers import entity_anchor, var_anchor
from backend.temporal_state.contracts import TemporalOccurrence

from tests.model_state.helpers import (  # noqa: F401  (re-exported)
    AS_OF,
    E1,
    PROP_TARGET,
    PROP_TEMP,
    SUBJECT,
    V1,
    entity_declaration,
    full_timeline_stack,
    observed_stack,
    prop_assertion,
    resolver_with,
    standard_bindings,
    var_declaration,
)

RECORDED = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="vs001_fixture",
                         method="manual_declaration")
EVIDENCE = (OwnerDeclarationEvidence(
    kind="owner_declaration", statement="synthetic value specification"),)


def unit(code="degree_celsius", system_edition="ohk-units-1"):
    return DeclaredUnit(kind="declared", unit=UnitReference(
        system_id="project_local", system_edition=system_edition, code=code))


NO_UNIT = UnitNotDeclared(kind="not_declared")


def model_with(tmp_path, *, specifications=(("number", False, None),),
               variables=((V1, E1),), name="model"):
    """A registered entity, its variables, and zero or more specifications
    given as (value_shape, nullable, unit) triples for V1."""
    store = ModelStore(tmp_path / name / "demo-printer")
    store.append(build_record(
        EntityRegistration, anchor=entity_anchor(E1),
        recorded_at=RECORDED, authority=AUTHORITY))
    for anchor_id, owner in variables:
        # the anchor must match the binding declaration exactly, or
        # VM-001 correctly refuses attachment on anchor divergence
        store.append(build_record(
            VariableRegistration, anchor=var_anchor(anchor_id, owner),
            recorded_at=RECORDED, authority=AUTHORITY))
    for index, (shape, nullable, declared) in enumerate(specifications):
        store.append(build_record(
            VariableValueSpecification, variable_anchor_id=V1,
            value_shape=shape, nullable=nullable,
            unit=declared if declared is not None else unit(),
            evidence=EVIDENCE, recorded_at=RECORDED, authority=AUTHORITY,
            note=f"spec-{index}"))
    return store


def compatibility(tmp_path, *, temporal=None, model_store=None,
                  binding_records=None):
    if temporal is None:
        temporal = observed_stack(tmp_path)
    resolver = resolver_with(
        tmp_path, *(standard_bindings() if binding_records is None
                    else binding_records))
    store = model_store if model_store is not None else model_with(tmp_path)
    state = ModelStateQueries(store.load(), resolver, temporal)
    return ObservationCompatibilityQueries(state), state, temporal


def payload(temperature_json: str) -> bytes:
    """Tier P: a real Moonraker-shaped body carrying any JSON value at the
    committed binding target."""
    return ('{"result":{"eventtime":3721.845,"status":{"extruder":'
            f'{{"temperature":{temperature_json},"target":60.0}},'
            '"heater_bed":{"temperature":45.2,"target":45.0},'
            '"toolhead":{"homed_axes":"xyz"},'
            '"print_stats":{"state":"printing","print_duration":512.4,'
            '"total_duration":640.9},'
            '"virtual_sdcard":{"progress":0.42,"is_active":true}}}}'
            ).encode("utf-8")


def observed_value(tmp_path, temperature_json: str):
    """Tier P: project one sweep whose extruder temperature is exactly the
    supplied JSON text, through the real adapter and projector."""
    from backend.temporal_state.projector import TemporalProjector
    from backend.temporal_state.queries import TemporalQueries
    from backend.temporal_state.store import TemporalStore
    from backend.data_sources.connectors.http_api import TransportResponse
    from tests.data_sources.test_ingestion_runner_api import (happy_script,
                                                              make_runner)

    runner, ds_store, transport = make_runner(tmp_path / "ds", happy_script())
    store = TemporalStore(tmp_path / "temporal.db",
                          evidence_root=ds_store.base_dir)
    projector = TemporalProjector(ds_store, store)
    transport.script["/printer/objects/query"] = TransportResponse(
        status=200, headers={"Content-Type": "application/json"},
        body=payload(temperature_json))
    runner.run("printer-1")
    projector.project("printer-1")
    return TemporalQueries(store)


def craft_occurrence(temporal, *, value_json, json_type,
                     declared_unit=None):
    """Tier C: insert one occurrence carrying content no adapter emits,
    reusing a real attempt row so the foreign key holds. Built from a REAL
    occurrence via validated construction, so only the intended fields are
    hostile."""
    from datetime import timedelta

    existing = temporal.history(SUBJECT, PROP_TEMP)[-1]
    crafted = TemporalOccurrence(
        **{**existing.model_dump(),
           "occurrence_id": "c" * 32,
           "observation_id": "d" * 32,
           "received_at": existing.received_at + timedelta(seconds=30),
           "finished_at": existing.finished_at + timedelta(seconds=30),
           "value_json": value_json,
           "json_type": json_type,
           "declared_unit": declared_unit,
           "previous_occurrence_id": existing.occurrence_id,
           "change_class": "changed"})
    with temporal.store.writer() as conn:
        temporal.store.insert_occurrence(conn, crafted)
    return crafted
