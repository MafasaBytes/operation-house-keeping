"""Shared fixture builders for the MK-001 test suite."""

from datetime import UTC, datetime

from backend.model_kernel.canonical import build_record
from backend.model_kernel.contracts import (
    AuthorityRef,
    EntityRegistration,
    LifecycleViewContext,
    OwnerDeclarationEvidence,
    RelationshipAssertion,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
    ViewIndependentContext,
)
from backend.model_kernel.store import ModelStore
from backend.system_identity import EntityAnchor

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="mk001_demo_fixture",
                         method="manual_declaration")
AS_BUILT = LifecycleViewContext(kind="lifecycle_view", view="as_built")
AS_DESIGNED = LifecycleViewContext(kind="lifecycle_view", view="as_designed")
VIEW_FREE = ViewIndependentContext(kind="view_independent")
EVIDENCE = (OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic test structure"),)

ENT_A = "ent_" + "a" * 32
ENT_B = "ent_" + "b" * 32
ENT_C = "ent_" + "c" * 32
ENT_D = "ent_" + "d" * 32
ENT_TYPE = "ent_" + "e" * 32


def anchor(anchor_id=ENT_A, kind="physical_instance", name="Demo entity"):
    return EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                        display_name=name, referent_kind=kind)


def registration(anchor_id=ENT_A, kind="physical_instance", note=""):
    return build_record(EntityRegistration,
                        anchor=anchor(anchor_id, kind=kind),
                        recorded_at=T0, authority=AUTHORITY, note=note)


def contains_type(**overrides):
    fields = dict(
        type_name="contains", forward_label="contains",
        inverse_label="is contained in", directionality="directed",
        source_referent_kinds=("logical_instance", "physical_instance"),
        target_referent_kinds=("logical_instance", "physical_instance"),
        self_relation_allowed=False, hierarchy_semantics="containment",
        context_requirement="lifecycle_view", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


def instance_of_type(**overrides):
    fields = dict(
        type_name="instance_of", forward_label="is an instance of",
        inverse_label="has instance", directionality="directed",
        source_referent_kinds=("logical_instance", "physical_instance"),
        target_referent_kinds=("type_definition",),
        self_relation_allowed=False, hierarchy_semantics="none",
        context_requirement="view_independent", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


def assertion(type_record, source=ENT_A, target=ENT_B, context=AS_BUILT,
              supersedes=None, note="", evidence=EVIDENCE, recorded_at=T0):
    return build_record(RelationshipAssertion, type_id=type_record.record_id,
                        source_anchor_id=source, target_anchor_id=target,
                        context=context, evidence=evidence,
                        supersedes=supersedes, recorded_at=recorded_at,
                        authority=AUTHORITY, note=note)


def withdrawal(target_assertion, note=""):
    return build_record(RelationshipWithdrawal,
                        withdraws=target_assertion.record_id,
                        recorded_at=T0, authority=AUTHORITY, note=note)


def store_with(tmp_path, *records, model_id="demo-printer"):
    store = ModelStore(tmp_path / model_id)
    for record in records:
        store.append(record)
    return store


def containment_world(tmp_path, *extra):
    """A minimal valid world: contains type + registrations A, B."""
    return store_with(tmp_path, contains_type(), registration(ENT_A),
                      registration(ENT_B), *extra)
