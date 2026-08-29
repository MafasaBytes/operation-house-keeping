"""Disposable VP-001 Slice C composition worlds; never committed ledgers."""

from dataclasses import dataclass

from backend.model_kernel import (
    LifecycleViewContext,
    ModelRecordEvidence,
    OwnerDeclarationEvidence,
    PortRegistration,
    VariablePortAssociation,
    VariablePortAssociationWithdrawal,
    build_record,
)
from backend.system_identity import PortAnchor

from tests.model_state.helpers import (
    E1, E2, MODEL_AUTHORITY, RECORDED, V1, model_with, state_queries,
)


P_NOT_DECLARED = "prt_" + "1" * 32
P_CONFLICTED = "prt_" + "2" * 32
P_INACTIVE = "prt_" + "3" * 32
P_ASSOCIATED = "prt_" + "4" * 32
P_DIFFERENT_OWNER = "prt_" + "5" * 32
P_UNKNOWN = "prt_" + "9" * 32
V_UNKNOWN = "var_" + "9" * 32

CONTEXT = LifecycleViewContext(kind="lifecycle_view", view="as_designed")
OTHER_CONTEXT = LifecycleViewContext(kind="lifecycle_view", view="as_built")
EVIDENCE = (OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="synthetic VP-001 Slice C composition test claim",
),)


def _port(port_id, owner):
    return build_record(
        PortRegistration,
        anchor=PortAnchor(
            anchor_id=port_id,
            namespace="demo-printer",
            display_name=f"Synthetic port {port_id[-1]}",
            role_name=f"vp001-test-{port_id[-1]}",
        ),
        owner_entity_anchor_id=owner,
        evidence=EVIDENCE,
        recorded_at=RECORDED,
        authority=MODEL_AUTHORITY,
        note="",
    )


def _association(store, port_id, *, supersedes=(), note=""):
    loaded = store.load()
    variable = loaded.variable_registrations_by_anchor[V1]
    port = loaded.port_registrations_by_anchor[port_id]
    return build_record(
        VariablePortAssociation,
        variable_anchor_id=V1,
        port_anchor_id=port_id,
        context=CONTEXT,
        evidence=(
            ModelRecordEvidence(kind="model_record",
                                record_id=variable.record_id),
            ModelRecordEvidence(kind="model_record",
                                record_id=port.record_id),
            *EVIDENCE,
        ),
        supersedes=supersedes,
        recorded_at=RECORDED,
        authority=MODEL_AUTHORITY,
        note=note,
    )


@dataclass(frozen=True)
class SliceCWorld:
    queries: object
    resolver: object
    temporal: object
    store: object
    associated: object
    inactive: object
    inactive_withdrawal: object
    conflict_root: object
    conflict_left: object
    conflict_right: object
    pre_association_membership: tuple[str, ...]


def slice_c_world(tmp_path):
    store = model_with(
        tmp_path,
        entities=((E1, "Extruder unit"), (E2, "Other unit")),
    )
    for port_id, owner in (
        (P_NOT_DECLARED, E1),
        (P_CONFLICTED, E1),
        (P_INACTIVE, E1),
        (P_ASSOCIATED, E1),
        (P_DIFFERENT_OWNER, E2),
    ):
        store.append(_port(port_id, owner))
    pre_association_membership = store.load().revision.record_ids

    root = _association(store, P_CONFLICTED, note="conflict root")
    left = _association(
        store, P_CONFLICTED, supersedes=(root.record_id,), note="left")
    right = _association(
        store, P_CONFLICTED, supersedes=(root.record_id,), note="right")
    inactive = _association(store, P_INACTIVE, note="inactive")
    event = build_record(
        VariablePortAssociationWithdrawal,
        withdraws=inactive.record_id,
        recorded_at=RECORDED,
        authority=MODEL_AUTHORITY,
        note="",
    )
    associated = _association(store, P_ASSOCIATED, note="associated")
    for record in (root, left, right, inactive, event, associated):
        store.append(record)

    queries, resolver, temporal = state_queries(
        tmp_path, model_store=store)
    return SliceCWorld(
        queries=queries,
        resolver=resolver,
        temporal=temporal,
        store=store,
        associated=associated,
        inactive=inactive,
        inactive_withdrawal=event,
        conflict_root=root,
        conflict_left=left,
        conflict_right=right,
        pre_association_membership=pre_association_membership,
    )
