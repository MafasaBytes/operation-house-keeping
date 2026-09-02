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
    PORT_D,
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

    def test_rc3_registration_ignores_conflicted_and_inactive_pt_support(
            self, tmp_path):
        records, registration, ports, *_ = flow_fixture(
            include_support=False)
        pcn_root = connection(note="PCN root")
        pcn_left = connection(
            supersedes=(pcn_root.record_id,), note="PCN left")
        pcn_right = connection(
            supersedes=(pcn_root.record_id,), note="PCN right")
        source_root = direction_interface(PORT_A, "output", note="PIF root")
        source_left = direction_interface(
            PORT_A, "output", supersedes=(source_root.record_id,),
            note="PIF left")
        source_right = direction_interface(
            PORT_A, "bidirectional", supersedes=(source_root.record_id,),
            note="PIF right")
        sink_root = direction_interface(PORT_B, "input", note="sink root")
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (
                *records, pcn_root, pcn_left, pcn_right,
                source_root, source_left, source_right, sink_root,
                pt_withdrawal(sink_root), registration):
            store.append(record)
        loaded = store.load()
        assert loaded.flow_registrations_by_anchor[FLOW_A] == registration
        assert loaded.flow_declarations == {}
        assert tuple(record.record_id for record in
                     loaded.current_port_connection_tips_by_root[
                         pcn_root.record_id]) == tuple(sorted((
                             pcn_left.record_id, pcn_right.record_id)))
        assert loaded.port_interface_superseded_by[source_root.record_id] == \
            tuple(sorted((source_left.record_id, source_right.record_id)))
        assert loaded.port_interface_withdrawn_by[sink_root.record_id]
        assert not hasattr(loaded, "flow_occurrences")
        assert len(ports) == 2

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

        token_variant = flow_registration(
            flow_anchor_id="flo_" + "c" * 32,
            port_records=ports, kind=flow_kind(code="another_kind"))
        store.append(token_variant)
        third_port = port_registration(PORT_C)
        store.append(third_port)
        partition_variant = flow_registration(
            flow_anchor_id="flo_" + "d" * 32,
            source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B,),
            port_records=(*ports, third_port))
        store.append(partition_variant)
        loaded = store.load()
        assert loaded.flow_registrations_by_anchor[
            token_variant.anchor.anchor_id] == token_variant
        assert loaded.flow_registrations_by_anchor[
            partition_variant.anchor.anchor_id] == partition_variant
        assert len(loaded.flow_registrations) == 4

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
        attacks = (
            refs,
            (FLOW_REGISTRATION_CLAIM,),
            *(tuple(ref for position, ref in enumerate(refs)
                    if position != omitted) + (FLOW_REGISTRATION_CLAIM,)
              for omitted in range(len(refs))),
        )
        for index, evidence in enumerate(attacks):
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

    @pytest.mark.parametrize("context", [
        *(kernel.LifecycleViewContext(kind="lifecycle_view", view=view)
          for view in ("as_designed", "as_built", "as_configured",
                       "as_operated", "as_maintained")),
        VIEW_INDEPENDENT,
    ])
    def test_every_exact_context_arm_admits_independently(
            self, tmp_path, context):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture(context=context)
        declaration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            context=context)
        store = kernel.ModelStore(tmp_path / "test-model")
        for record in (*records, registration, declaration):
            store.append(record)
        loaded = store.load()
        assert loaded.flow_declaration_ids_by_key[
            (FLOW_A, context)] == (declaration.record_id,)

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
            loaded = validate_record_collection("test-model", records)
            assert loaded.flow_declarations[declaration.record_id] == \
                declaration
            assert tuple(loaded.flow_registrations_by_anchor) == (FLOW_A,)
            assert loaded.flow_role_by_anchor_and_port == {
                (FLOW_A, PORT_A): "source", (FLOW_A, PORT_B): "sink"}
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

    def test_missing_frg_and_individual_pif_reject_reference_typed(self):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture()
        missing_registration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            flow_anchor_id=FLOW_B, note="missing FRG")
        missing_pif = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            source_direction_pins=(direction_pin(
                PORT_A, "pif_" + "f" * 64),), note="missing PIF")
        for candidate in (missing_registration, missing_pif):
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", {
                    record.record_id: record
                    for record in (*records, registration, candidate)})
            assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_every_nonexact_connection_union_rejects(self):
        records, registration, ports, _, source_pifs, sink_pifs = \
            flow_fixture(source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B,))
        fourth = port_registration(PORT_D)
        attacks = (
            connection((PORT_A, PORT_B), note="proper subset"),
            connection((PORT_A, PORT_B, PORT_D),
                       note="same-cardinality different union"),
            connection((PORT_A, PORT_D), note="overlap only"),
            connection((PORT_A, PORT_B, PORT_C, PORT_D),
                       note="proper superset"),
        )
        for index, candidate_pcn in enumerate(attacks):
            declaration = flow_declaration(
                registration, port_records=ports, pcn=candidate_pcn,
                source_pifs=source_pifs, sink_pifs=sink_pifs,
                note=f"nonexact-union-{index}")
            collection = {record.record_id: record for record in (
                *records, fourth, candidate_pcn, registration, declaration)}
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", collection)
            assert error.value.error_code == "MODEL_FLOW_DECLARATION_INVALID"

    def test_missing_extra_wrong_dimension_and_wrong_context_pins_reject(self):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture(source_ports=(PORT_A, PORT_C), sink_ports=(PORT_B,))
        wrong_dimension = kernel.build_record(
            kernel.PortInterfaceDeclaration,
            port_anchor_id=PORT_A,
            context=AS_DESIGNED,
            declaration=kernel.InterfaceDomainDeclaration(
                dimension="interface_domain",
                value=kernel.InterfaceDomainToken(
                    token_kind="interface_domain", system_id="project_local",
                    system_edition="1", code="synthetic")),
            evidence=source_pifs[0].evidence,
            supersedes=(),
            recorded_at=source_pifs[0].recorded_at,
            authority=AUTHORITY,
            note="wrong dimension",
        )
        wrong_context = direction_interface(
            PORT_A, "output", context=VIEW_INDEPENDENT,
            note="wrong context")
        attacks = (
            {"source_direction_pins": (direction_pin(
                PORT_A, source_pifs[0].record_id),)},
            {"source_direction_pins": (
                *(direction_pin(item.port_anchor_id, item.record_id)
                  for item in source_pifs),
                direction_pin(PORT_D, "pif_" + "d" * 64))},
            {"source_direction_pins": (direction_pin(
                PORT_A, wrong_dimension.record_id),
                direction_pin(PORT_C, source_pifs[1].record_id))},
            {"source_direction_pins": (direction_pin(
                PORT_A, wrong_context.record_id),
                direction_pin(PORT_C, source_pifs[1].record_id))},
        )
        extras = (wrong_dimension, wrong_context)
        for index, overrides in enumerate(attacks):
            declaration = flow_declaration(
                registration, port_records=ports, pcn=pcn,
                source_pifs=source_pifs, sink_pifs=sink_pifs,
                note=f"pin-shape-{index}", **overrides)
            collection = {record.record_id: record for record in (
                *records, *extras, registration, declaration)}
            with pytest.raises(kernel.ModelIntegrityError) as error:
                validate_record_collection("test-model", collection)
            assert error.value.error_code in {
                "MODEL_FLOW_DECLARATION_INVALID", "MODEL_REFERENCE_INVALID"}

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
        attacks = (
            refs,
            (FLOW_DECLARATION_CLAIM,),
            *(tuple(ref for position, ref in enumerate(refs)
                    if position != omitted) + (FLOW_DECLARATION_CLAIM,)
              for omitted in range(len(refs))),
        )
        for index, evidence in enumerate(attacks):
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

    def test_valid_current_pif_cannot_repair_invalid_exact_stale_pin(self):
        records, registration, ports, pcn, _, sink_pifs = flow_fixture()
        records = tuple(
            record for record in records
            if not (record.record_kind == "port_interface_declaration"
                    and record.port_anchor_id == PORT_A))
        invalid_root = direction_interface(
            PORT_A, "input", note="invalid source-role root")
        valid_current = direction_interface(
            PORT_A, "output", supersedes=(invalid_root.record_id,),
            note="valid current replacement")
        declaration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=(invalid_root,), sink_pifs=sink_pifs,
            note="must not retarget")
        collection = {record.record_id: record for record in (
            *records, invalid_root, valid_current, registration, declaration)}
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection("test-model", collection)
        assert error.value.error_code == "MODEL_FLOW_DECLARATION_INVALID"

    def test_exact_pins_admit_inside_conflicted_support_lineages(self):
        records, registration, ports, pcn, source_pifs, sink_pifs = \
            flow_fixture()
        pcn_left = connection(
            supersedes=(pcn.record_id,), note="PCN left fork")
        pcn_right = connection(
            supersedes=(pcn.record_id,), note="PCN right fork")
        source_left = direction_interface(
            PORT_A, "output", supersedes=(source_pifs[0].record_id,),
            note="PIF left fork")
        source_right = direction_interface(
            PORT_A, "bidirectional", supersedes=(source_pifs[0].record_id,),
            note="PIF right fork")
        declaration = flow_declaration(
            registration, port_records=ports, pcn=pcn,
            source_pifs=source_pifs, sink_pifs=sink_pifs,
            note="pins structurally valid conflicted roots")
        loaded = validate_record_collection("test-model", {
            record.record_id: record for record in (
                *records, pcn_left, pcn_right, source_left, source_right,
                registration, declaration)})
        assert loaded.flow_declarations[declaration.record_id] == declaration
        assert tuple(record.record_id for record in
                     loaded.current_port_connection_tips_by_root[
                         pcn.record_id]) == tuple(sorted((
                             pcn_left.record_id, pcn_right.record_id)))
        assert loaded.port_interface_superseded_by[
            source_pifs[0].record_id] == tuple(sorted((
                source_left.record_id, source_right.record_id)))

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
    left = forward.load()
    right = reverse.load()
    assert left.revision == right.revision
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
    for name in names:
        assert dict(getattr(left, name)) == dict(getattr(right, name))
