"""FL-001 Slice A flow admission, lifecycle, index, and replay tests."""

from types import MappingProxyType

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED,
    AUTHORITY,
    FLOW_A,
    FLOW_B,
    FLOW_DECLARATION_CLAIM,
    FLOW_REGISTRATION_CLAIM,
    PORT_A,
    PORT_B,
    PORT_C,
    T1,
    VIEW_INDEPENDENT,
    citation,
    complete_records,
    connection,
    declaration_evidence,
    direction_interface,
    direction_pin,
    flow_declaration,
    flow_fixture,
    flow_kind,
    flow_registration,
    flow_withdrawal,
    port_registration,
    snapshot,
    world,
)


def assert_atomic_rejection(store, record, *codes):
    before = snapshot(store)
    revision = store.load().revision
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(record)
    assert error.value.error_code in codes
    assert snapshot(store) == before
    assert store.load().revision == revision


def pt_withdrawal(target, *, note=""):
    return kernel.build_record(
        kernel.PortClaimWithdrawal,
        withdraws=target.record_id,
        recorded_at=T1,
        authority=AUTHORITY,
        note=note,
    )


def fixture_claim(**kwargs):
    _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    return flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs, **kwargs)


class TestFlowRegistrationAdmission:
    def test_rc3_registration_without_contextual_support_admits_and_indexes(
            self, tmp_path):
        store, registration, ports, pcn, source_pifs, sink_pifs = world(
            tmp_path, include_support=False)
        loaded = store.load()
        token = registration.flow_kind
        signature = (
            registration.source_port_anchor_ids,
            registration.sink_port_anchor_ids,
            token.token_kind,
            token.system_id,
            token.system_edition,
            token.code,
        )
        assert pcn is None and source_pifs == sink_pifs == ()
        assert loaded.flow_registrations == {
            registration.record_id: registration}
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration
        assert loaded.flow_anchor_id_by_semantic_signature[signature] == FLOW_A
        assert loaded.flow_anchor_ids_by_port == {
            PORT_A: (FLOW_A,), PORT_B: (FLOW_A,)}
        assert loaded.flow_role_by_anchor_and_port == {
            (FLOW_A, PORT_A): "source", (FLOW_A, PORT_B): "sink"}
        assert loaded.flow_declarations == {}
        assert loaded.current_flow_declaration_tips_by_root == {}
        assert loaded.port_connections == {}
        assert loaded.port_interface_declarations == {}
        assert len(ports) == 2
        for name in (
            "flow_registrations", "flow_registrations_by_anchor",
            "flow_anchor_id_by_semantic_signature",
            "flow_anchor_ids_by_port", "flow_role_by_anchor_and_port",
        ):
            assert isinstance(getattr(loaded, name), MappingProxyType)
            with pytest.raises(TypeError):
                getattr(loaded, name)["forged"] = ()

    def test_duplicate_anchor_and_exact_signature_reject_atomically(
            self, tmp_path):
        store, registration, ports, *_ = world(tmp_path)
        duplicate_anchor = flow_registration(
            port_records=ports, note="duplicate anchor")
        duplicate_signature = flow_registration(
            flow_anchor_id=FLOW_B, port_records=ports,
            note="indistinguishable parallel mechanism")
        assert_atomic_rejection(
            store, duplicate_anchor, "MODEL_DUPLICATE_REGISTRATION")
        assert_atomic_rejection(
            store, duplicate_signature, "MODEL_FLOW_REGISTRATION_INVALID")
        assert registration.anchor.anchor_id == FLOW_A

    def test_reversed_roles_partition_and_token_difference_can_coexist(
            self, tmp_path):
        store, registration, ports, *_ = world(tmp_path)
        reverse = flow_registration(
            flow_anchor_id=FLOW_B,
            source_ports=(PORT_B,), sink_ports=(PORT_A,),
            port_records=ports)
        store.append(reverse)
        loaded = store.load()
        assert loaded.flow_registrations_by_anchor[FLOW_B] == reverse
        assert loaded.flow_anchor_ids_by_port[PORT_A] == (FLOW_A, FLOW_B)
        assert loaded.flow_role_by_anchor_and_port[(FLOW_B, PORT_A)] == "sink"
        assert loaded.flow_role_by_anchor_and_port[(FLOW_B, PORT_B)] == \
            "source"

        records, _, third_ports, *_ = flow_fixture(
            source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B,))
        third_registration = flow_registration(
            flow_anchor_id=FLOW_B,
            source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B,),
            port_records=third_ports, kind=flow_kind(code="another_kind"))
        assert records and third_registration.record_id != \
            registration.record_id

    def test_cross_entity_many_to_many_signature_is_one_flow_not_pairs(
            self, tmp_path):
        source_ports = (PORT_A, PORT_C)
        sink_ports = ("prt_" + "4" * 32, "prt_" + "5" * 32)
        store, registration, ports, *_ = world(
            tmp_path, source_ports=source_ports, sink_ports=sink_ports,
            cross_entity=True, include_support=False)
        loaded = store.load()
        assert registration.source_port_anchor_ids == tuple(
            sorted(source_ports))
        assert registration.sink_port_anchor_ids == tuple(sorted(sink_ports))
        assert len(ports) == 4
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration
        assert set(loaded.flow_anchor_ids_by_port) == set(
            (*source_ports, *sink_ports))
        assert all(value == (FLOW_A,)
                   for value in loaded.flow_anchor_ids_by_port.values())
        assert not hasattr(loaded, "flow_pair_ids")
        assert not hasattr(loaded, "flow_graph")

    def test_missing_port_uniform_closure_and_mandatory_basis_reject(self):
        records, registration, ports, *_ = flow_fixture(
            include_support=False)
        unregistered = flow_registration(
            flow_anchor_id=FLOW_B,
            source_ports=(PORT_A,), sink_ports=(PORT_C,),
            port_records=ports, evidence=registration.evidence)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", {
                record.record_id: record for record in (*records, unregistered)
            })
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        dangling = flow_registration(
            flow_anchor_id=FLOW_B, port_records=ports,
            evidence=(citation("frg_" + "f" * 64),
                      FLOW_REGISTRATION_CLAIM))
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", {
                record.record_id: record for record in (*records, dangling)
            })
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        refs = tuple(item for item in registration.evidence
                     if item.kind == "model_record")
        for index, evidence in enumerate((refs, (FLOW_REGISTRATION_CLAIM,),
                                          refs[:-1] + (
                                              FLOW_REGISTRATION_CLAIM,))):
            candidate = flow_registration(
                flow_anchor_id=FLOW_B, port_records=ports,
                evidence=evidence, note=f"missing-basis-{index}")
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", {
                    record.record_id: record
                    for record in (*records, candidate)})
            assert error.value.error_code == \
                "MODEL_FLOW_REGISTRATION_INVALID"


class TestFlowDeclarationAdmission:
    def test_exact_support_admits_and_builds_all_foundational_indexes(
            self, tmp_path):
        declaration = fixture_claim()
        store, registration, *_ = world(tmp_path, declaration)
        loaded = store.load()
        key = (FLOW_A, AS_DESIGNED)
        assert loaded.flow_declarations[declaration.record_id] == declaration
        assert loaded.flow_declaration_ids_by_key[key] == (
            declaration.record_id,)
        assert loaded.flow_declaration_parent_ids[declaration.record_id] == ()
        assert loaded.flow_declaration_successor_ids[
            declaration.record_id] == ()
        assert loaded.flow_declaration_root_by_id[
            declaration.record_id] == declaration.record_id
        assert loaded.flow_declaration_ancestry_by_id[
            declaration.record_id] == ()
        assert loaded.current_flow_declaration_tips_by_root[
            declaration.record_id] == (declaration,)
        body = loaded.flow_declaration_effective_body_by_id[
            declaration.record_id]
        assert loaded.flow_declaration_ids_by_effective_body[body] == (
            declaration.record_id,)
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration

    def test_view_independent_exact_context_admits(self, tmp_path):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture(context=VIEW_INDEPENDENT)
        declaration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            context=VIEW_INDEPENDENT)
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (*records, registration, declaration):
            store.append(record)
        loaded = store.load()
        assert loaded.flow_declaration_ids_by_key[
            (FLOW_A, VIEW_INDEPENDENT)] == (declaration.record_id,)

    @pytest.mark.parametrize("source_value,sink_value,accepted", [
        (source, sink, source in {"output", "bidirectional"}
         and sink in {"input", "bidirectional"})
        for source in ("input", "output", "bidirectional", "non_directional")
        for sink in ("input", "output", "bidirectional", "non_directional")
    ])
    def test_exact_direction_role_table(self, source_value, sink_value,
                                        accepted):
        base, registration, ports, pcn, _, _ = flow_fixture()
        source_pif = direction_interface(PORT_A, source_value)
        sink_pif = direction_interface(PORT_B, sink_value)
        declaration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=(source_pif,), sink_pifs=(sink_pif,))
        records = {record.record_id: record for record in (
            *(record for record in base
              if record.record_kind != "port_interface_declaration"),
            source_pif, sink_pif, registration, declaration)}
        if accepted:
            assert validate_record_collection(
                "test-model", records).flow_declarations[
                    declaration.record_id] == declaration
        else:
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", records)
            assert error.value.error_code == "MODEL_FLOW_DECLARATION_INVALID"

    def test_wrong_context_union_port_and_role_substitutions_reject(
            self, tmp_path):
        _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
        store, *_ = world(tmp_path)
        other_context_pcn = connection(context=VIEW_INDEPENDENT)
        store.append(other_context_pcn)
        superset_port = port_registration(PORT_C)
        store.append(superset_port)
        superset_pcn = connection((PORT_A, PORT_B, PORT_C))
        store.append(superset_pcn)
        source_input = direction_interface(
            PORT_A, "input", supersedes=(source_pifs[0].record_id,),
            note="wrong")
        store.append(source_input)
        attacks = (
            {"connection_assertion_record_id": other_context_pcn.record_id},
            {"connection_assertion_record_id": superset_pcn.record_id},
            {"source_direction_pins": (
                direction_pin(PORT_A, source_input.record_id),)},
            {"source_direction_pins": (
                direction_pin(PORT_B, source_pifs[0].record_id),),
             "sink_direction_pins": (
                 direction_pin(PORT_A, sink_pifs[0].record_id),)},
            {"context": VIEW_INDEPENDENT},
        )
        for index, overrides in enumerate(attacks):
            candidate = flow_declaration(
                registration, port_records=ports, pcn=pcn,
                source_pifs=source_pifs, sink_pifs=sink_pifs,
                note=f"attack-{index}", **overrides)
            assert_atomic_rejection(
                store, candidate, "MODEL_FLOW_DECLARATION_INVALID")

    def test_missing_support_and_evidence_closure_precede_claim_basis(
            self, tmp_path):
        _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
        store, *_ = world(tmp_path)
        missing = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            connection_assertion_record_id="pcn_" + "f" * 64)
        assert_atomic_rejection(store, missing, "MODEL_REFERENCE_INVALID")

        dangling = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            evidence=(citation("fld_" + "f" * 64),
                      FLOW_DECLARATION_CLAIM))
        assert_atomic_rejection(store, dangling, "MODEL_REFERENCE_INVALID")

        complete = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs)
        refs = tuple(item for item in complete.evidence
                     if item.kind == "model_record")
        for index, evidence in enumerate((refs, (FLOW_DECLARATION_CLAIM,),
                                          refs[:-1] + (
                                              FLOW_DECLARATION_CLAIM,))):
            candidate = flow_declaration(
                registration, port_records=ports, pcn=pcn,
                source_pifs=source_pifs, sink_pifs=sink_pifs,
                evidence=evidence, note=f"missing-evidence-{index}")
            assert_atomic_rejection(
                store, candidate, "MODEL_FLOW_DECLARATION_INVALID")


class TestFlowLifecycleAndReplay:
    def test_same_root_fork_merge_and_cross_root_merge(self, tmp_path):
        root = fixture_claim(note="root")
        left = fixture_claim(supersedes=(root.record_id,), note="left")
        right = fixture_claim(supersedes=(root.record_id,), note="right")
        merged = fixture_claim(
            supersedes=(right.record_id, left.record_id), note="merged")
        store, *_ = world(tmp_path, root, left, right, merged)
        loaded = store.load()
        assert loaded.current_flow_declaration_tips_by_root[
            root.record_id] == (merged,)
        assert loaded.flow_declaration_ancestry_by_id[merged.record_id] == \
            tuple(sorted((root.record_id, left.record_id, right.record_id)))

        first = fixture_claim(note="first independent root")
        second = fixture_claim(note="second independent root")
        independent, *_ = world(tmp_path / "independent", first, second)
        cross = fixture_claim(
            supersedes=(first.record_id, second.record_id), note="cross")
        assert_atomic_rejection(
            independent, cross, "MODEL_FLOW_LINEAGE_INVALID")

    def test_fork_partial_convergence_and_identical_independent_roots(
            self, tmp_path):
        root = fixture_claim(note="root")
        left = fixture_claim(supersedes=(root.record_id,), note="left")
        middle = fixture_claim(supersedes=(root.record_id,), note="middle")
        right = fixture_claim(supersedes=(root.record_id,), note="right")
        forked, *_ = world(tmp_path / "forked", root, left, middle, right)
        assert tuple(record.record_id for record in
                     forked.load().current_flow_declaration_tips_by_root[
                         root.record_id]) == tuple(sorted((
                             left.record_id, middle.record_id,
                             right.record_id)))
        partial = fixture_claim(
            supersedes=(left.record_id, middle.record_id), note="partial")
        partial_store, *_ = world(
            tmp_path / "partial", root, left, middle, right, partial)
        assert tuple(record.record_id for record in
                     partial_store.load().current_flow_declaration_tips_by_root[
                         root.record_id]) == tuple(sorted((
                             partial.record_id, right.record_id)))

        first = fixture_claim(note="first independent root")
        second = fixture_claim(note="second independent root")
        roots, *_ = world(tmp_path / "roots", first, second)
        loaded = roots.load()
        first_body = loaded.flow_declaration_effective_body_by_id[
            first.record_id]
        second_body = loaded.flow_declaration_effective_body_by_id[
            second.record_id]
        assert first_body == second_body
        assert loaded.flow_declaration_ids_by_effective_body[first_body] == \
            tuple(sorted((first.record_id, second.record_id)))
        assert loaded.flow_declaration_root_by_id[first.record_id] == \
            first.record_id
        assert loaded.flow_declaration_root_by_id[second.record_id] == \
            second.record_id

    def test_cross_context_missing_and_cross_flow_parent_reject(self):
        root = fixture_claim(note="root")
        missing = fixture_claim(
            supersedes=("fld_" + "f" * 64,), note="missing")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "test-model", complete_records(missing))
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture()
        other_pcn = connection(context=VIEW_INDEPENDENT)
        other_source = direction_interface(
            PORT_A, "output", context=VIEW_INDEPENDENT)
        other_sink = direction_interface(
            PORT_B, "input", context=VIEW_INDEPENDENT)
        other_context = flow_declaration(
            registration, port_records=ports, pcn=other_pcn,
            source_pifs=(other_source,), sink_pifs=(other_sink,),
            context=VIEW_INDEPENDENT, supersedes=(root.record_id,),
            note="cross context")
        collection = {record.record_id: record for record in (
            *records, other_pcn, other_source, other_sink,
            registration, root, other_context)}
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", collection)
        assert error.value.error_code == "MODEL_FLOW_LINEAGE_INVALID"

        other_flow = flow_registration(
            flow_anchor_id=FLOW_B, port_records=ports,
            kind=flow_kind(code="other_logical_flow"))
        other_root = flow_declaration(
            other_flow, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            note="other flow root")
        cross_flow = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            supersedes=(other_root.record_id,), note="cross flow")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", {
                record.record_id: record for record in (
                    *records, registration, other_flow, other_root,
                    cross_flow)})
        assert error.value.error_code == "MODEL_FLOW_LINEAGE_INVALID"

    def test_selective_withdrawal_replay_revives_tip_and_registration(
            self, tmp_path):
        first = fixture_claim(note="first")
        second = fixture_claim(note="second")
        event = flow_withdrawal(first)
        store, registration, *_ = world(tmp_path, first, second, event)
        loaded = store.load()
        assert loaded.flow_declaration_withdrawn_by[first.record_id] == (
            event.record_id,)
        assert loaded.current_flow_declaration_tips_by_root[
            first.record_id] == ()
        assert loaded.current_flow_declaration_tips_by_root[
            second.record_id] == (second,)
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration
        replay = store.replay(tuple(
            record_id for record_id in loaded.revision.record_ids
            if record_id != event.record_id))
        assert replay.current_flow_declaration_tips_by_root[
            first.record_id] == (first,)

    def test_selective_fork_withdrawal_and_all_inactive_roots(self, tmp_path):
        root = fixture_claim(note="root")
        left = fixture_claim(supersedes=(root.record_id,), note="left")
        right = fixture_claim(supersedes=(root.record_id,), note="right")
        selective, registration, *_ = world(
            tmp_path / "selective", root, left, right,
            flow_withdrawal(left))
        loaded = selective.load()
        assert loaded.current_flow_declaration_tips_by_root[
            root.record_id] == (right,)
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration

        first = fixture_claim(note="first root")
        second = fixture_claim(note="second root")
        inactive, registration, *_ = world(
            tmp_path / "inactive", first, second,
            flow_withdrawal(first),
            flow_withdrawal(second, note="second withdrawal"))
        assert inactive.load().current_flow_declaration_tips_by_root == {
            first.record_id: (), second.record_id: ()}
        assert inactive.load().flow_registrations_by_anchor[FLOW_A] == \
            registration

    def test_unknown_superseded_duplicate_and_successor_race_reject(
            self, tmp_path):
        root = fixture_claim(note="root")
        child = fixture_claim(
            supersedes=(root.record_id,), note="child")
        unknown = kernel.build_record(
            kernel.FlowDeclarationWithdrawal,
            withdraws="fld_" + "f" * 64,
            recorded_at=T1,
            authority=AUTHORITY,
            note="unknown",
        )
        store, *_ = world(tmp_path / "unknown")
        assert_atomic_rejection(store, unknown, "MODEL_REFERENCE_INVALID")
        superseded, *_ = world(tmp_path / "superseded", root, child)
        assert_atomic_rejection(
            superseded, flow_withdrawal(root),
            "MODEL_FLOW_WITHDRAWAL_INVALID")
        withdrawn, *_ = world(
            tmp_path / "withdrawn", root, flow_withdrawal(root))
        assert_atomic_rejection(
            withdrawn, flow_withdrawal(root, note="again"),
            "MODEL_FLOW_WITHDRAWAL_INVALID")
        assert_atomic_rejection(
            withdrawn, child, "MODEL_FLOW_WITHDRAWAL_INVALID")

    def test_stale_pcn_and_pif_pins_admit_without_retargeting(self, tmp_path):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture()
        pcn_successor = connection(
            supersedes=(pcn.record_id,), note="connection successor")
        source_successor = direction_interface(
            PORT_A, "output", supersedes=(source_pifs[0].record_id,),
            note="interface successor")
        stale = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            note="pins superseded PT support")
        store = kernel.ModelStore(tmp_path / "superseded")
        for record in (*records, pcn_successor, source_successor,
                       registration, stale):
            store.append(record)
        loaded = store.load()
        disclosed = loaded.flow_declarations[stale.record_id]
        assert disclosed.connection_assertion_record_id == pcn.record_id
        assert disclosed.source_direction_pins[0].declaration_record_id == \
            source_pifs[0].record_id
        assert loaded.port_connection_superseded_by[pcn.record_id] == (
            pcn_successor.record_id,)
        assert loaded.port_interface_superseded_by[source_pifs[0].record_id] \
            == (source_successor.record_id,)

        withdrawn = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            note="pins withdrawn PT support")
        withdrawn_store = kernel.ModelStore(tmp_path / "withdrawn")
        for record in (*records, pt_withdrawal(pcn),
                       pt_withdrawal(source_pifs[0], note="withdraw PIF"),
                       registration, withdrawn):
            withdrawn_store.append(record)
        inactive = withdrawn_store.load()
        assert inactive.flow_declarations[withdrawn.record_id] == withdrawn
        assert inactive.port_connection_withdrawn_by[pcn.record_id]
        assert inactive.port_interface_withdrawn_by[source_pifs[0].record_id]

    def test_replay_omitting_successor_revives_predecessor_tip(self, tmp_path):
        root = fixture_claim(note="root")
        child = fixture_claim(supersedes=(root.record_id,), note="child")
        store, *_ = world(tmp_path, root, child)
        replay = store.replay(tuple(
            record_id for record_id in store.load().revision.record_ids
            if record_id != child.record_id))
        assert replay.current_flow_declaration_tips_by_root[
            root.record_id] == (root,)

    def test_changed_exact_support_pin_changes_effective_body(self):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture()
        source_successor = direction_interface(
            PORT_A, "bidirectional",
            supersedes=(source_pifs[0].record_id,), note="new exact pin")
        first = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs, note="first")
        second = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=(source_successor,), sink_pifs=sink_pifs,
            note="second")
        loaded = validate_record_collection("test-model", {
            record.record_id: record for record in (
                *records, source_successor, registration, first, second)})
        assert loaded.flow_declaration_effective_body_by_id[
            first.record_id] != loaded.flow_declaration_effective_body_by_id[
                second.record_id]

    def test_deep_legal_dag_is_iterative(self):
        chain = []
        parent = None
        for index in range(1100):
            item = fixture_claim(
                supersedes=(() if parent is None else (parent.record_id,)),
                note=f"depth-{index}")
            chain.append(item)
            parent = item
        loaded = validate_record_collection(
            "test-model", complete_records(*chain))
        assert loaded.current_flow_declaration_tips_by_root[
            chain[0].record_id] == (chain[-1],)


def test_flow_indexes_and_revision_are_deterministic_under_reversed_input():
    root = fixture_claim(note="root")
    child = fixture_claim(supersedes=(root.record_id,), note="child")
    values = tuple(complete_records(root, child).values())
    forward = validate_record_collection(
        "test-model", {record.record_id: record for record in values})
    reverse = validate_record_collection(
        "test-model", {record.record_id: record for record in reversed(values)})
    names = (
        "flow_registrations", "flow_registrations_by_anchor",
        "flow_anchor_id_by_semantic_signature", "flow_anchor_ids_by_port",
        "flow_role_by_anchor_and_port", "flow_declarations",
        "flow_declaration_ids_by_key", "flow_declaration_parent_ids",
        "flow_declaration_successor_ids", "flow_declaration_root_by_id",
        "flow_declaration_ancestry_by_id",
        "current_flow_declaration_tips_by_root",
        "flow_declaration_effective_body_by_id",
        "flow_declaration_ids_by_effective_body",
        "flow_declaration_withdrawals", "flow_declaration_withdrawn_by",
        "flow_declaration_withdrawals_by_target",
    )
    assert forward.revision == reverse.revision
    for name in names:
        assert dict(getattr(forward, name)) == dict(getattr(reverse, name))


def test_valid_independent_append_order_produces_identical_files_and_indexes(
        tmp_path):
    records, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    entity_records = tuple(
        record for record in records if record.record_kind ==
        "entity_registration")
    support_records = tuple(
        record for record in records if record.record_kind in {
            "port_connection_assertion", "port_interface_declaration"})
    first = fixture_claim(note="first root")
    second = fixture_claim(note="second root")

    def build(path, reverse):
        store = kernel.ModelStore(path / "test-model")
        for level in (
                entity_records,
                tuple(reversed(ports)) if reverse else ports,
                tuple(reversed(support_records)) if reverse
                else support_records,
                (registration,),
                (second, first) if reverse else (first, second)):
            for record in level:
                store.append(record)
        return store

    forward = build(tmp_path / "forward", False)
    reverse = build(tmp_path / "reverse", True)
    assert snapshot(forward) == snapshot(reverse)
    assert forward.load().revision == reverse.load().revision
    assert dict(forward.load().flow_declaration_root_by_id) == dict(
        reverse.load().flow_declaration_root_by_id)
