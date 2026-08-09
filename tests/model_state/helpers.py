"""Shared builders for the VM-001 model_state suite: a real Moonraker
temporal stack (accepted test fixtures), synthetic binding sets, and
synthetic model ledgers whose anchors match the binding declarations."""

from datetime import UTC, datetime
from pathlib import Path

from backend.identity_binding.canonical import build_record as ib_build
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    AuthorityRef as IbAuthorityRef,
    BindingAssertion,
    BindingRetraction,
    DeclaredBoundary,
    UnknownBoundary,
)
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import (
    AuthorityRef,
    EntityRegistration,
    ModelStore,
    VariableRegistration,
    build_record,
)
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

from tests.identity_binding.test_facade import temporal_stack

E1 = "ent_" + "1" * 32
E2 = "ent_" + "2" * 32
V1 = "var_" + "3" * 32
V2 = "var_" + "4" * 32
RECORDED = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
AS_OF = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
BEFORE_RECEIPT = datetime(2026, 8, 7, 19, 0, 0, tzinfo=UTC)
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP_TEMP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                              item_key="printer_objects",
                              json_pointer="/result/status/extruder/temperature")
PROP_TARGET = SourcePropertyRef(extraction_route="api:moonraker:v1",
                                item_key="printer_objects",
                                json_pointer="/result/status/extruder/target")
MODEL_AUTHORITY = AuthorityRef(kind="test_fixture", agent="vm001_demo_fixture",
                               method="manual_declaration")
IB_AUTHORITY = IbAuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                              method="manual_declaration")


def entity_anchor(anchor_id=E1, name="Extruder unit"):
    return EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                        display_name=name, referent_kind="physical_instance")


def var_anchor(anchor_id=V1, owner=E1, name="Hotend temperature"):
    return VariableAnchor(anchor_id=anchor_id, entity_anchor_id=owner,
                          namespace="demo-printer", display_name=name)


def hour(start_h=20, end_h=21, day=7):
    base = datetime(2026, 8, day, tzinfo=UTC)
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=DeclaredBoundary(kind="declared",
                                        at=base.replace(hour=start_h)),
        end_boundary=DeclaredBoundary(kind="declared",
                                      at=base.replace(hour=end_h)),
        interval_semantics="half_open")


UNKNOWN_START = AppliesScope(
    axis="ingestion_received_at",
    start_boundary=UnknownBoundary(kind="unknown"),
    end_boundary=DeclaredBoundary(kind="declared",
                                  at=datetime(2026, 8, 7, 21, tzinfo=UTC)),
    interval_semantics="half_open")


def model_with(tmp_path, *, entities=((E1, "Extruder unit"),),
               variables=((V1, E1, "Hotend temperature"),)):
    store = ModelStore(tmp_path / "model" / "demo-printer")
    for anchor_id, name in entities:
        store.append(build_record(
            EntityRegistration, anchor=entity_anchor(anchor_id, name),
            recorded_at=RECORDED, authority=MODEL_AUTHORITY))
    for anchor_id, owner, name in variables:
        store.append(build_record(
            VariableRegistration, anchor=var_anchor(anchor_id, owner, name),
            recorded_at=RECORDED, authority=MODEL_AUTHORITY))
    return store


def entity_declaration(anchor_id=E1, name="Extruder unit"):
    return ib_build(AnchorDeclaration, anchor_kind="entity",
                    anchor=entity_anchor(anchor_id, name),
                    recorded_at=RECORDED, authority=IB_AUTHORITY)


def var_declaration(anchor_id=V1, owner=E1, name="Hotend temperature"):
    return ib_build(AnchorDeclaration, anchor_kind="variable",
                    anchor=var_anchor(anchor_id, owner, name),
                    recorded_at=RECORDED, authority=IB_AUTHORITY)


def prop_assertion(target=V1, prop=PROP_TEMP, applies=None, note=""):
    return ib_build(BindingAssertion, binding_kind="property",
                    subject=SUBJECT, property=prop,
                    target_anchor_id=target, applies=applies or hour(),
                    recorded_at=RECORDED, authority=IB_AUTHORITY, note=note)


def retraction(target_assertion):
    return ib_build(BindingRetraction, retracts=target_assertion.record_id,
                    recorded_at=RECORDED, authority=IB_AUTHORITY)


def resolver_with(tmp_path, *records):
    store = BindingStore(tmp_path / "bindings" / "demo-printer")
    for record in records:
        store.append(record)
    return BindingResolver(store.load())


STANDARD_BINDINGS = None  # computed lazily per tmp_path


def standard_bindings():
    return (entity_declaration(), var_declaration(), prop_assertion())


def observed_stack(tmp_path, runs=1):
    runner, projector, temporal = temporal_stack(tmp_path)
    for _ in range(runs):
        runner.run("printer-1")
    projector.project("printer-1")
    return temporal


def state_queries(tmp_path, *, temporal=None, binding_records=None,
                  model_store=None):
    from backend.model_state import ModelStateQueries

    if temporal is None:
        temporal = observed_stack(tmp_path)
    resolver = resolver_with(
        tmp_path, *(standard_bindings() if binding_records is None
                    else binding_records))
    store = model_store if model_store is not None else model_with(tmp_path)
    return ModelStateQueries(store.load(), resolver, temporal), resolver, temporal
