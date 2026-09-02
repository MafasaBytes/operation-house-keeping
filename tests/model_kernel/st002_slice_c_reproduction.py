"""Deterministic disposable ST-002 Slice C positive-world reproduction.

The harness independently constructs every record through accepted public
identity/record builders and appends through ``ModelStore``. It never calls a
minter, copies a record file, or touches the authoritative demo ledger.
"""

from dataclasses import dataclass
from datetime import timedelta
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_bytes, verify_record_id
from tests.model_kernel.builders import ENT_A
from tests.model_kernel.st001_slice_a_helpers import (
    state_declaration,
    state_withdrawal,
)
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    STATE_B,
    T1,
    TRANSITION_A,
    TRANSITION_B,
    VIEW_INDEPENDENT,
    transition_declaration,
    transition_fixture,
    transition_registration,
    transition_withdrawal,
)


TRANSITION_INDEX_NAMES = (
    "transition_registrations",
    "transition_registrations_by_anchor",
    "transition_anchor_ids_by_subject_entity",
    "transition_registration_id_by_ordered_subject_endpoints",
    "transition_declarations",
    "transition_declaration_ids_by_key",
    "transition_declaration_parent_ids",
    "transition_declaration_successor_ids",
    "transition_declaration_root_by_id",
    "transition_declaration_ancestry_by_id",
    "current_transition_declaration_tips_by_root",
    "transition_declaration_withdrawals",
    "transition_declaration_withdrawn_by",
    "transition_declaration_withdrawals_by_target",
)

FIXTURE_DISCLAIMER = (
    "This is an illustrative synthetic ST-002 transition declaration "
    "fixture. A `declared` result means only that the selected model revision "
    "contains an admitted declaration connecting the exact "
    "pinned from-state and to-state declarations in the stated context. It "
    "does not claim that a real system is in either state, that either state "
    "is exclusive or complete, that the transition is enabled, executable, "
    "occurring, observed, or completed, or that temporal order establishes "
    "cause, control, safety, health, diagnosis, correctness, or recommended "
    "action."
)


@dataclass(frozen=True)
class SliceCReproduction:
    store: kernel.ModelStore
    loaded: object
    records: dict[str, kernel.ModelRecord]
    memberships: dict[str, tuple[str, ...]]
    query_bytes: dict[str, bytes]
    stored_bytes: dict[str, bytes]
    artifact_bytes: bytes
    artifact_sha256: str
    stored_aggregate_sha256: str


def _json_bytes(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False).encode("utf-8")


def _plain(value):
    if isinstance(value, BaseModel):
        record_id = getattr(value, "record_id", None)
        if isinstance(record_id, str):
            return {"record_id": record_id}
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        rows = [(_plain(key), _plain(item)) for key, item in value.items()]
        return sorted(rows, key=lambda row: _json_bytes(row[0]))
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    if isinstance(value, (set, frozenset)):
        rows = [_plain(item) for item in value]
        return sorted(rows, key=_json_bytes)
    return value


def _compact(result) -> dict:
    return result.model_dump(mode="json", exclude={"material"})


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _build_semantic_graph():
    base, forward_registration, from_registration, to_registration, \
        from_root, to_root = transition_fixture()

    # The two state histories create exact membership-relative RC1 pins:
    # from_root is superseded; to_root is withdrawn while an independent peer
    # keeps STATE_B declared.
    from_successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_root.record_id,), recorded_at=T1,
        note="slice-c from-state successor")
    to_peer = state_declaration(
        to_registration, state_anchor_id=STATE_B,
        recorded_at=T1 + timedelta(seconds=1),
        note="slice-c to-state independent peer")
    to_root_withdrawal = state_withdrawal(
        to_root, recorded_at=T1 + timedelta(seconds=2),
        note="slice-c withdraw pinned to-state root")
    from_view_independent = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        context=VIEW_INDEPENDENT,
        recorded_at=T1 + timedelta(seconds=3),
        note="slice-c view-independent from-state")
    to_view_independent = state_declaration(
        to_registration, state_anchor_id=STATE_B,
        context=VIEW_INDEPENDENT,
        recorded_at=T1 + timedelta(seconds=4),
        note="slice-c view-independent to-state")

    reverse_registration = transition_registration(
        transition_anchor_id=TRANSITION_B,
        from_registration=to_registration,
        to_registration=from_registration,
        from_state=STATE_B,
        to_state=STATE_A,
        recorded_at=T1,
        note="slice-c reverse registration with shared human name")

    def claim(note, *, from_declaration=from_root,
              to_declaration=to_root, supersedes=(), seconds,
              registration=forward_registration,
              from_state_registration=from_registration,
              to_state_registration=to_registration,
              context=AS_OPERATED):
        return transition_declaration(
            registration,
            from_registration=from_state_registration,
            to_registration=to_state_registration,
            from_declaration=from_declaration,
            to_declaration=to_declaration,
            context=context,
            supersedes=supersedes,
            recorded_at=T1 + timedelta(seconds=seconds),
            note=note)

    stale_root_one = claim(
        "slice-c stale root one", seconds=10)
    stale_root_two = claim(
        "slice-c stale root two", seconds=11)
    exact_root = claim(
        "slice-c exact-current divergent root",
        from_declaration=from_successor,
        to_declaration=to_peer,
        seconds=12)
    fork_root = claim("slice-c fork root", seconds=13)
    fork_left = claim(
        "slice-c fork left", supersedes=(fork_root.record_id,), seconds=14)
    fork_right = claim(
        "slice-c fork right", supersedes=(fork_root.record_id,), seconds=15)
    fork_merge = claim(
        "slice-c fork merge",
        supersedes=(fork_left.record_id, fork_right.record_id), seconds=16)
    inactive_root = claim(
        "slice-c inactive root",
        from_declaration=from_successor,
        to_declaration=to_peer,
        seconds=17)
    inactive_withdrawal = transition_withdrawal(
        inactive_root, recorded_at=T1 + timedelta(seconds=18),
        note="slice-c withdraw independent transition root")
    view_independent_root = claim(
        "slice-c view-independent transition",
        from_declaration=from_view_independent,
        to_declaration=to_view_independent,
        context=VIEW_INDEPENDENT,
        seconds=19)
    reverse_root = claim(
        "slice-c reverse declaration",
        from_declaration=to_peer,
        to_declaration=from_successor,
        registration=reverse_registration,
        from_state_registration=to_registration,
        to_state_registration=from_registration,
        seconds=20)

    generated = {
        "from_registration": from_registration,
        "to_registration": to_registration,
        "from_root": from_root,
        "to_root": to_root,
        "from_successor": from_successor,
        "to_peer": to_peer,
        "to_root_withdrawal": to_root_withdrawal,
        "from_view_independent": from_view_independent,
        "to_view_independent": to_view_independent,
        "forward_registration": forward_registration,
        "reverse_registration": reverse_registration,
        "stale_root_one": stale_root_one,
        "stale_root_two": stale_root_two,
        "exact_root": exact_root,
        "fork_root": fork_root,
        "fork_left": fork_left,
        "fork_right": fork_right,
        "fork_merge": fork_merge,
        "inactive_root": inactive_root,
        "inactive_withdrawal": inactive_withdrawal,
        "view_independent_root": view_independent_root,
        "reverse_root": reverse_root,
    }
    for record in base:
        generated[f"base_{record.record_id}"] = record

    def of_kind(kind):
        return tuple(record for record in base if record.record_kind == kind)

    stages = (
        of_kind("entity_registration"),
        of_kind("variable_registration"),
        of_kind("constraint_registration"),
        of_kind("variable_constraint_declaration"),
        of_kind("state_registration"),
        of_kind("state_declaration"),
        (from_successor, to_peer,
         from_view_independent, to_view_independent),
        (to_root_withdrawal,),
        (forward_registration, reverse_registration),
        (stale_root_one, stale_root_two, exact_root, fork_root,
         inactive_root, view_independent_root, reverse_root),
        (fork_left, fork_right),
        (fork_merge, inactive_withdrawal),
    )
    return generated, stages


def _query_serializations(store, loaded, records):
    queries = kernel.ModelQueries(loaded)
    results = {
        "transition_forward": queries.transition(TRANSITION_A),
        "transition_reverse": queries.transition(TRANSITION_B),
        "declaration_forward_as_operated": queries.transition_declaration(
            TRANSITION_A, context=AS_OPERATED),
        "declaration_forward_view_independent":
            queries.transition_declaration(
                TRANSITION_A, context=VIEW_INDEPENDENT),
        "declaration_reverse_as_operated": queries.transition_declaration(
            TRANSITION_B, context=AS_OPERATED),
        "entity_as_operated": queries.transitions_of_entity(
            ENT_A, context=AS_OPERATED),
    }
    transition_records = sorted(
        (record for record in records.values()
         if record.record_kind.startswith("transition_")),
        key=lambda record: record.record_id)
    for record in transition_records:
        results[f"assertion_{record.record_id}"] = \
            queries.transition_assertion(record.record_id)
    return results, {
        name: result.model_dump_json().encode("utf-8")
        for name, result in sorted(results.items())
    }


def reproduce(root: Path, *, reverse_independent: bool) -> SliceCReproduction:
    records, stages = _build_semantic_graph()
    store = kernel.ModelStore(root / "test-model")
    for stage in stages:
        ordered = tuple(sorted(stage, key=lambda record: record.record_id))
        if reverse_independent:
            ordered = tuple(reversed(ordered))
        for record in ordered:
            store.append(record)

    loaded = store.load()
    final_membership = loaded.revision.record_ids
    memberships = {
        "final": final_membership,
        "before_fork_merge": tuple(
            record_id for record_id in final_membership
            if record_id != records["fork_merge"].record_id),
        "before_transition_withdrawal": tuple(
            record_id for record_id in final_membership
            if record_id != records["inactive_withdrawal"].record_id),
        "before_from_state_successor": tuple(
            record_id for record_id in final_membership
            if record_id not in {
                records["from_successor"].record_id,
                records["exact_root"].record_id,
                records["inactive_root"].record_id,
                records["inactive_withdrawal"].record_id,
                records["reverse_root"].record_id,
            }),
        "before_to_state_withdrawal": tuple(
            record_id for record_id in final_membership
            if record_id != records["to_root_withdrawal"].record_id),
    }

    results, query_bytes = _query_serializations(store, loaded, records)
    replay_payloads = {}
    for label, membership in memberships.items():
        selected = store.replay(membership)
        selected_queries = kernel.ModelQueries(selected)
        declaration = selected_queries.transition_declaration(
            TRANSITION_A, context=AS_OPERATED)
        replay_payloads[label] = {
            "membership": list(membership),
            "revision": selected.revision.model_dump(mode="json"),
            "declaration": _compact(declaration),
            "fork_left_assertion": _compact(
                selected_queries.transition_assertion(
                    records["fork_left"].record_id)),
            "fork_right_assertion": _compact(
                selected_queries.transition_assertion(
                    records["fork_right"].record_id)),
            "inactive_root_assertion": _compact(
                selected_queries.transition_assertion(
                    records["inactive_root"].record_id)),
        }

    stored_bytes = {
        record_id: (store.records_dir / f"{record_id}.json").read_bytes()
        for record_id in loaded.revision.record_ids
    }
    stored_inventory = {
        f"{record_id}.json": _sha256(value)
        for record_id, value in stored_bytes.items()
    }
    stored_aggregate = _sha256(_json_bytes(stored_inventory))

    transition_records = sorted(
        (record for record in records.values()
         if record.record_kind.startswith("transition_")),
        key=lambda record: record.record_id)
    canonical_records = []
    for record in transition_records:
        normative = canonical_bytes(record)
        assert verify_record_id(record)
        assert _sha256(normative) == record.record_id.split("_", 1)[1]
        canonical_records.append({
            "record_id": record.record_id,
            "record_kind": record.record_kind,
            "canonical_bytes": len(normative),
            "canonical_sha256": _sha256(normative),
            "canonical_hex": normative.hex(),
            "stored_bytes": len(stored_bytes[record.record_id]),
            "stored_sha256": _sha256(stored_bytes[record.record_id]),
        })

    index_payload = {
        name: _plain(getattr(loaded, name))
        for name in TRANSITION_INDEX_NAMES
    }
    artifact = {
        "schema": "st002_slice_c_disposable_reproduction/v1",
        "scope": "disposable_test_fixture_only",
        "disclaimer": FIXTURE_DISCLAIMER,
        "model": {
            "model_id": loaded.revision.model_id,
            "record_count": loaded.revision.record_count,
            "revision_id": loaded.revision.revision_id,
            "membership": list(loaded.revision.record_ids),
            "stored_aggregate_sha256": stored_aggregate,
        },
        "identities": {
            "entity_anchor_id": ENT_A,
            "from_state_anchor_id": STATE_A,
            "to_state_anchor_id": STATE_B,
            "forward_transition_anchor_id": TRANSITION_A,
            "reverse_transition_anchor_id": TRANSITION_B,
        },
        "records": {
            label: record.record_id
            for label, record in sorted(records.items())
            if not label.startswith("base_")
        },
        "canonical_transition_records": canonical_records,
        "transition_indexes": index_payload,
        "queries": {
            name: {
                "bytes": len(value),
                "sha256": _sha256(value),
                "payload_without_material": _compact(results[name]),
            }
            for name, value in sorted(query_bytes.items())
        },
        "replay": replay_payloads,
        "nonclaims": (
            "Names, ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM, "
            "BH declarations, semantic compatibility, CN satisfaction, ST "
            "matches, temporal correlation, and observation changes did not "
            "create this transition. Displaying endpoint observations beside "
            "a transition does not persist an occurrence."
        ),
    }
    artifact_bytes = _json_bytes(artifact)
    return SliceCReproduction(
        store=store,
        loaded=loaded,
        records=records,
        memberships=memberships,
        query_bytes=query_bytes,
        stored_bytes=stored_bytes,
        artifact_bytes=artifact_bytes,
        artifact_sha256=_sha256(artifact_bytes),
        stored_aggregate_sha256=stored_aggregate,
    )
