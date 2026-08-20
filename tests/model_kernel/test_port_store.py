"""PT-001 Slice A red baseline for validating storage and derived indexes."""

from dataclasses import FrozenInstanceError
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
from types import MappingProxyType

import pytest

from backend.model_kernel import (
    CompatibilityDimensionBasis,
    ModelIntegrityError,
    ModelRecordEvidence,
    ModelStore,
    PortCompatibilityBasis,
    PortCompatibilityDeclaration,
    PortInterfaceCitation,
    build_record,
)
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import ENT_A, registration as entity_registration
from tests.model_kernel.test_port_records import (
    AUTHORITY,
    CONTEXT,
    EVIDENCE,
    PORT_A,
    PORT_B,
    PORT_C,
    T0,
    compatibility,
    connection,
    declaration_body,
    interface,
    registration,
    withdrawal,
)


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def append_all(store, *records):
    for record in records:
        store.append(record)
    return store


def base(tmp_path, *ports):
    store = ModelStore(tmp_path / "demo-printer")
    store.append(entity_registration(ENT_A))
    for port in ports or (PORT_A,):
        store.append(registration(
            anchor=registration().anchor.model_copy(update={
                "anchor_id": port, "display_name": f"Port {port[-1]}"})))
    return store


def pcm_from(pifs, *, outcome="declared_compatible", supersedes=(),
             context=CONTEXT, endpoints=(PORT_A, PORT_B), statement="basis"):
    by_key = {(record.port_anchor_id, record.declaration.dimension): record
              for record in pifs}
    dimensions = []
    for dimension in ("interface_domain", "direction_role", "interface_type"):
        if (PORT_A, dimension) not in by_key:
            continue
        dimensions.append(CompatibilityDimensionBasis(
            dimension=dimension,
            citations=tuple(PortInterfaceCitation(
                port_anchor_id=port,
                declaration_record_id=by_key[(port, dimension)].record_id)
                for port in endpoints)))
    return build_record(
        PortCompatibilityDeclaration,
        endpoint_port_anchor_ids=endpoints, context=context, outcome=outcome,
        basis=PortCompatibilityBasis(statement=statement,
                                     dimensions=tuple(dimensions)),
        evidence=EVIDENCE, supersedes=supersedes, recorded_at=T0,
        authority=AUTHORITY, note="")


def assert_atomic_rejection(store, record, code):
    before = snapshot(store)
    with pytest.raises(ModelIntegrityError) as error:
        store.append(record)
    assert error.value.error_code == code
    assert snapshot(store) == before


class TestPortRegistrationValidation:
    def test_owner_must_be_registered_and_failure_is_atomic(self, tmp_path):
        store = ModelStore(tmp_path / "demo-printer")
        assert_atomic_rejection(store, registration(), "MODEL_REFERENCE_INVALID")

    def test_one_registration_per_port_even_when_owner_agrees(self, tmp_path):
        store = base(tmp_path)
        duplicate = registration(note="second registration")
        assert_atomic_rejection(store, duplicate, "MODEL_DUPLICATE_REGISTRATION")

    def test_model_record_evidence_closes_on_append_and_replay(self, tmp_path):
        missing = "reg_" + "f" * 64
        cited = (ModelRecordEvidence(kind="model_record", record_id=missing),)
        store = append_all(ModelStore(tmp_path / "append"),
                           entity_registration(ENT_A))
        assert_atomic_rejection(
            store, registration(evidence=cited), "MODEL_REFERENCE_INVALID")

        support = entity_registration("ent_" + "b" * 32)
        good = registration(evidence=(ModelRecordEvidence(
            kind="model_record", record_id=support.record_id),))
        complete = append_all(ModelStore(tmp_path / "replay"),
                              entity_registration(ENT_A), support, good)
        subset = tuple(record_id for record_id in complete.load().revision.record_ids
                       if record_id != support.record_id)
        with pytest.raises(ModelIntegrityError) as error:
            complete.replay(subset)
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"


class TestPortInterfaceLifecycle:
    def test_registration_closure_and_one_root_per_key(self, tmp_path):
        ghost = interface(PORT_B)
        assert_atomic_rejection(base(tmp_path / "ghost"), ghost,
                                "MODEL_REFERENCE_INVALID")
        store = base(tmp_path / "root")
        first = interface(note="first root")
        store.append(first)
        assert_atomic_rejection(store, interface(note="second root"),
                                "MODEL_PORT_INTERFACE_LINEAGE_INVALID")

    def test_fork_partial_and_all_tip_convergence_are_membership_relative(
            self, tmp_path):
        root = interface()
        left = interface(supersedes=(root.record_id,), note="left")
        right = interface(
            declaration=declaration_body("interface_domain",
                                         value=declaration_body().value.model_copy(
                                             update={"code": "data"})),
            supersedes=(root.record_id,), note="right")
        merge = interface(supersedes=(left.record_id, right.record_id),
                          note="merge")
        store = append_all(base(tmp_path), root, left, right, merge)
        loaded = store.load()
        key = (PORT_A, CONTEXT, "interface_domain")
        assert loaded.current_port_interface_tips_by_key[key] == (merge,)
        replay = store.replay(tuple(
            record_id for record_id in loaded.revision.record_ids
            if record_id != merge.record_id))
        assert replay.current_port_interface_tips_by_key[key] == tuple(
            sorted((left, right), key=lambda record: record.record_id))

    def test_cross_key_parent_and_crafted_cycle_are_rejected(self, tmp_path):
        root = interface()
        cross = interface(dimension="direction_role",
                          supersedes=(root.record_id,))
        store = append_all(base(tmp_path / "cross"), root)
        assert_atomic_rejection(store, cross,
                                "MODEL_PORT_INTERFACE_LINEAGE_INVALID")

        child = interface(supersedes=(root.record_id,), note="child")
        cyclic = root.model_copy(update={"supersedes": (child.record_id,)})
        records = {record.record_id: record for record in (
            entity_registration(ENT_A), registration(), cyclic, child)}
        with pytest.raises(ModelIntegrityError) as error:
            validate_record_collection("demo-printer", records,
                                       verify_hashes=False)
        assert error.value.error_code == "MODEL_PORT_INTERFACE_LINEAGE_INVALID"

    def test_wrong_context_parent_and_partial_convergence_are_honest(
            self, tmp_path):
        root = interface()
        other_context = CONTEXT.model_copy(update={"view": "as_built"})
        wrong_context = interface(
            context=other_context, supersedes=(root.record_id,))
        store = append_all(base(tmp_path / "context"), root)
        assert_atomic_rejection(store, wrong_context,
                                "MODEL_PORT_INTERFACE_LINEAGE_INVALID")

        left = interface(supersedes=(root.record_id,), note="left")
        right = interface(
            supersedes=(root.record_id,), note="right",
            declaration=declaration_body().model_copy(update={
                "value": declaration_body().value.model_copy(
                    update={"code": "other"})}))
        partial = interface(supersedes=(left.record_id,), note="partial")
        loaded = append_all(base(tmp_path / "partial"), root, left, right,
                            partial).load()
        key = (PORT_A, CONTEXT, "interface_domain")
        assert loaded.current_port_interface_tips_by_key[key] == tuple(
            sorted((right, partial), key=lambda record: record.record_id))


class TestPortConnectionLifecycle:
    def test_every_endpoint_must_be_registered(self, tmp_path):
        assert_atomic_rejection(base(tmp_path, PORT_A), connection(),
                                "MODEL_REFERENCE_INVALID")

    def test_multiple_roots_corroborate_and_keep_distinct_derived_roots(
            self, tmp_path):
        first = connection(note="first root")
        second = connection(note="second root")
        loaded = append_all(base(tmp_path, PORT_A, PORT_B),
                            second, first).load()
        assert loaded.port_connection_root_by_id[first.record_id] == first.record_id
        assert loaded.port_connection_root_by_id[second.record_id] == second.record_id
        subject = ((PORT_A, PORT_B), CONTEXT)
        assert loaded.port_connection_ids_by_subject[subject] == tuple(
            sorted((first.record_id, second.record_id)))

    def test_same_root_fork_converges_but_cross_root_or_subject_does_not(
            self, tmp_path):
        root = connection()
        left = connection(supersedes=(root.record_id,), note="left")
        right = connection(supersedes=(root.record_id,), note="right")
        merge = connection(supersedes=(left.record_id, right.record_id),
                           note="merge")
        store = append_all(base(tmp_path / "same", PORT_A, PORT_B),
                           root, left, right, merge)
        assert store.load().current_port_connection_tips_by_root[
            root.record_id] == (merge,)

        other = connection(note="other root")
        cross_root = connection(supersedes=(merge.record_id, other.record_id),
                                note="illegal merge")
        store.append(other)
        assert_atomic_rejection(store, cross_root,
                                "MODEL_PORT_CONNECTION_LINEAGE_INVALID")

        changed = connection((PORT_A, PORT_C),
                             supersedes=(merge.record_id,))
        other_store = append_all(base(tmp_path / "subject", PORT_A, PORT_B,
                                      PORT_C), root, left, right, merge)
        assert_atomic_rejection(other_store, changed,
                                "MODEL_PORT_CONNECTION_LINEAGE_INVALID")

    def test_ancestry_is_complete_and_immutable(self, tmp_path):
        root_z = connection(note="z root")
        root_a = connection(note="a root")
        child = connection(supersedes=(root_z.record_id,), note="child")
        merge = connection(supersedes=(child.record_id,), note="grandchild")
        loaded = append_all(base(tmp_path, PORT_A, PORT_B),
                            root_z, child, merge, root_a).load()
        assert loaded.port_connection_ancestry_by_id[root_z.record_id] == ()
        assert loaded.port_connection_ancestry_by_id[child.record_id] == (
            root_z.record_id,)
        assert loaded.port_connection_ancestry_by_id[merge.record_id] == tuple(
            sorted((root_z.record_id, child.record_id)))
        with pytest.raises(TypeError):
            loaded.port_connection_ancestry_by_id[merge.record_id] = ()

    def test_current_tip_root_key_iteration_is_canonical(self, tmp_path):
        roots = tuple(connection(note=note) for note in (
            "z root", "a root", "middle root", "another root"))
        # Deliberately append in noncanonical order. The result's mapping
        # iteration is public serialized order and must not inherit insertion
        # or hash-table order.
        loaded = append_all(base(tmp_path, PORT_A, PORT_B), *roots).load()
        keys = tuple(loaded.current_port_connection_tips_by_root)
        assert keys == tuple(sorted(keys))


class TestPortCompatibilityValidation:
    def declared_pair(self, tmp_path):
        pifs = (interface(PORT_A), interface(PORT_B))
        return base(tmp_path, PORT_A, PORT_B), pifs

    def test_citations_require_membership_endpoint_dimension_and_context(
            self, tmp_path):
        store, pifs = self.declared_pair(tmp_path)
        pcm = pcm_from(pifs)
        assert_atomic_rejection(store, pcm, "MODEL_REFERENCE_INVALID")
        append_all(store, *pifs)
        store.append(pcm)

        wrong_endpoint = interface(PORT_C)
        wrong_store = append_all(base(tmp_path / "endpoint", PORT_A, PORT_B,
                                      PORT_C), *pifs, wrong_endpoint)
        basis = CompatibilityDimensionBasis(
            dimension="interface_domain", citations=(
                PortInterfaceCitation(port_anchor_id=PORT_A,
                    declaration_record_id=pifs[0].record_id),
                PortInterfaceCitation(port_anchor_id=PORT_B,
                    declaration_record_id=wrong_endpoint.record_id)))
        bad = compatibility(basis=PortCompatibilityBasis(
            statement="bad endpoint", dimensions=(basis,)))
        assert_atomic_rejection(wrong_store, bad,
                                "MODEL_PORT_COMPATIBILITY_CITATION_INVALID")

        wrong_dimension = interface(PORT_B, "direction_role")
        dimension_store = append_all(base(tmp_path / "dimension", PORT_A,
                                          PORT_B), pifs[0], wrong_dimension)
        basis = CompatibilityDimensionBasis(
            dimension="interface_domain", citations=(
                PortInterfaceCitation(port_anchor_id=PORT_A,
                    declaration_record_id=pifs[0].record_id),
                PortInterfaceCitation(port_anchor_id=PORT_B,
                    declaration_record_id=wrong_dimension.record_id)))
        bad = compatibility(basis=PortCompatibilityBasis(
            statement="bad dimension", dimensions=(basis,)))
        assert_atomic_rejection(dimension_store, bad,
                                "MODEL_PORT_COMPATIBILITY_CITATION_INVALID")

    def test_missing_and_duplicate_citation_record_attacks_are_rejected(
            self, tmp_path):
        store, pifs = self.declared_pair(tmp_path)
        append_all(store, *pifs)
        missing = pifs[1].record_id.replace("pif_", "pif_f")[-68:]
        # Preserve the exact prefix/64-hex grammar while naming no member.
        missing = "pif_" + "f" * 64
        item = CompatibilityDimensionBasis(
            dimension="interface_domain", citations=(
                PortInterfaceCitation(port_anchor_id=PORT_A,
                    declaration_record_id=pifs[0].record_id),
                PortInterfaceCitation(port_anchor_id=PORT_B,
                    declaration_record_id=missing)))
        absent = compatibility(basis=PortCompatibilityBasis(
            statement="missing citation", dimensions=(item,)))
        assert_atomic_rejection(store, absent, "MODEL_REFERENCE_INVALID")

        duplicate = CompatibilityDimensionBasis(
            dimension="interface_domain", citations=(
                PortInterfaceCitation(port_anchor_id=PORT_A,
                    declaration_record_id=pifs[0].record_id),
                PortInterfaceCitation(port_anchor_id=PORT_B,
                    declaration_record_id=pifs[0].record_id)))
        forged = compatibility(basis=PortCompatibilityBasis(
            statement="same PIF cited twice", dimensions=(duplicate,)))
        assert_atomic_rejection(
            store, forged, "MODEL_PORT_COMPATIBILITY_CITATION_INVALID")

    def test_one_root_per_pair_context_and_stale_citations_remain_loadable(
            self, tmp_path):
        store, pifs = self.declared_pair(tmp_path)
        first = pcm_from(pifs)
        append_all(store, *pifs, first)
        assert_atomic_rejection(store, pcm_from(pifs, outcome="declared_incompatible"),
                                "MODEL_PORT_COMPATIBILITY_LINEAGE_INVALID")

        successor = interface(PORT_A, supersedes=(pifs[0].record_id,),
                              note="new current declaration")
        store.append(successor)
        loaded = store.load()
        assert first.record_id in loaded.port_compatibility_declarations
        assert loaded.port_compatibility_citations[first.record_id] == tuple(
            citation.declaration_record_id
            for item in first.basis.dimensions for citation in item.citations)

    @pytest.mark.parametrize("offset", [-1, 1])
    def test_stale_pcm_validity_ignores_successor_time_file_order_and_replays(
            self, tmp_path, offset):
        store, pifs = self.declared_pair(tmp_path / "store")
        pcm = pcm_from(pifs)
        successor = interface(
            PORT_A, supersedes=(pifs[0].record_id,),
            recorded_at=T0 + timedelta(days=offset), note="successor")
        append_all(store, *pifs, pcm, successor)
        loaded = store.load()
        assert pcm.record_id in loaded.port_compatibility_declarations

        # Complete collection validity is independent of mapping/file order.
        records = list(loaded.records.values())
        forward = validate_record_collection(
            "demo-printer", {r.record_id: r for r in records})
        reverse = validate_record_collection(
            "demo-printer", {r.record_id: r for r in reversed(records)})
        assert forward.revision == reverse.revision == loaded.revision
        assert forward.port_compatibility_citations == \
            reverse.port_compatibility_citations

        # Explicit membership without the successor makes citations current;
        # including it makes them stale, but both revisions remain valid.
        before_ids = tuple(record_id for record_id in loaded.revision.record_ids
                           if record_id != successor.record_id)
        before = store.replay(before_ids)
        after = store.replay(loaded.revision.record_ids)
        assert pcm.record_id in before.port_compatibility_declarations
        assert pcm.record_id in after.port_compatibility_declarations


class TestPortWithdrawalDiscipline:
    def test_only_unique_unsuperseded_current_tip_may_be_withdrawn(self, tmp_path):
        root = interface()
        child = interface(supersedes=(root.record_id,), note="child")
        store = append_all(base(tmp_path), root, child)
        assert_atomic_rejection(store, withdrawal(root.record_id),
                                "MODEL_PORT_WITHDRAWAL_INVALID")
        event = withdrawal(child.record_id)
        store.append(event)
        assert_atomic_rejection(store, withdrawal(child.record_id, note="again"),
                                "MODEL_PORT_WITHDRAWAL_INVALID")

    def test_target_cannot_be_both_withdrawn_and_superseded_or_resurrected(
            self, tmp_path):
        root = interface()
        store = append_all(base(tmp_path), root, withdrawal(root.record_id))
        successor = interface(supersedes=(root.record_id,), note="resurrection")
        assert_atomic_rejection(store, successor,
                                "MODEL_PORT_WITHDRAWAL_INVALID")

    def test_replay_omitting_withdrawal_revives_tip(self, tmp_path):
        root = interface()
        event = withdrawal(root.record_id)
        store = append_all(base(tmp_path), root, event)
        loaded = store.load()
        key = (PORT_A, CONTEXT, "interface_domain")
        assert loaded.current_port_interface_tips_by_key[key] == ()
        replay = store.replay(tuple(record_id for record_id
                                    in loaded.revision.record_ids
                                    if record_id != event.record_id))
        assert replay.current_port_interface_tips_by_key[key] == (root,)


def test_indexes_are_immutable_and_deterministic_across_append_order(tmp_path):
    root = connection()
    pif = interface()
    forward = append_all(base(tmp_path / "forward", PORT_A, PORT_B), pif, root)
    backward = append_all(base(tmp_path / "backward", PORT_A, PORT_B), root, pif)
    left, right = forward.load(), backward.load()
    assert left.revision == right.revision
    assert left.port_anchor_ids_by_owner == right.port_anchor_ids_by_owner
    assert left.port_connection_ids_by_port == right.port_connection_ids_by_port
    assert isinstance(left.port_registrations_by_anchor, MappingProxyType)
    with pytest.raises(TypeError):
        left.port_registrations_by_anchor[PORT_C] = registration()
    with pytest.raises(FrozenInstanceError):
        left.revision = right.revision


@pytest.mark.parametrize("factory,ports", [
    (interface, (PORT_A,)),
    (connection, (PORT_A, PORT_B)),
    (compatibility, (PORT_A, PORT_B)),
])
def test_model_record_evidence_closure_is_independent_for_each_pt_claim(
        tmp_path, factory, ports):
    missing = ModelRecordEvidence(kind="model_record",
                                  record_id="reg_" + "f" * 64)
    record = factory(evidence=(missing,))
    assert_atomic_rejection(base(tmp_path, *ports), record,
                            "MODEL_REFERENCE_INVALID")


def test_ptw_cannot_gain_a_citable_evidence_arm_at_store_boundary(tmp_path):
    root = interface()
    store = append_all(base(tmp_path), root)
    event = withdrawal(root.record_id)
    from backend.model_kernel.canonical import canonical_payload
    payload = {**canonical_payload(event), "record_id": event.record_id,
               "evidence": [item.model_dump(mode="json") for item in EVIDENCE]}
    (store.records_dir / f"{event.record_id}.json").write_text(
        json.dumps(payload, sort_keys=True), encoding="utf-8")
    with pytest.raises(ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_public_pt_index_order_is_identical_across_python_hash_seeds():
    script = r'''
import json, tempfile
from pathlib import Path
from backend.model_kernel import ModelStore
from tests.model_kernel.builders import ENT_A, registration as entity_registration
from tests.model_kernel.test_port_records import PORT_A, PORT_B, connection, registration

root = Path(tempfile.mkdtemp()) / "demo-printer"
store = ModelStore(root)
store.append(entity_registration(ENT_A))
for port in (PORT_A, PORT_B):
    base = registration()
    store.append(registration(anchor=base.anchor.model_copy(update={
        "anchor_id": port, "display_name": port})))
records = {connection(note=note) for note in ("z", "a", "m", "b")}
for record in records:
    store.append(record)
loaded = store.load()
print(json.dumps({
    "roots": list(loaded.current_port_connection_tips_by_root),
    "subjects": [repr(key) for key in loaded.port_connection_ids_by_subject],
    "incident": list(loaded.port_connection_ids_by_port),
}, separators=(",", ":")))
'''
    outputs = []
    for seed in ("1", "2", "8675309"):
        environment = os.environ.copy()
        environment.update(PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(), env=environment,
            text=True, capture_output=True, check=True)
        outputs.append(completed.stdout.strip())
    assert outputs[0] == outputs[1] == outputs[2]
    decoded = json.loads(outputs[0])
    assert decoded["roots"] == sorted(decoded["roots"])
    assert decoded["subjects"] == sorted(decoded["subjects"])
    assert decoded["incident"] == sorted(decoded["incident"])
