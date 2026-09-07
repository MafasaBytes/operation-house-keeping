"""FM-001 Slice A declaration, closure, lifecycle, index, and replay gates."""

from datetime import UTC, datetime
from types import MappingProxyType

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import VAR_A, variable_registration
from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, AUTHORITY, FLOW_A, PORT_A, VIEW_INDEPENDENT,
    flow_declaration, flow_fixture,
)


T0 = datetime(2026, 9, 8, 9, 0, tzinfo=UTC)
CLAIM = kernel.OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="Synthetic authority declares direct-measurement relevance.")


def variable_port(*, context=AS_DESIGNED, variable=VAR_A, port=PORT_A,
                  supersedes=(), note=""):
    return kernel.build_record(
        kernel.VariablePortAssociation,
        variable_anchor_id=variable,
        port_anchor_id=port,
        context=context,
        evidence=(CLAIM,),
        supersedes=supersedes,
        recorded_at=T0,
        authority=AUTHORITY,
        note=note,
    )


def semantic(*, variable=VAR_A, edition="ohk-observation-roles-1",
             code="measured_actual", note=""):
    return kernel.build_record(
        kernel.VariableSemanticDeclaration,
        variable_anchor_id=variable,
        declaration=kernel.ObservationRoleDeclaration(
            dimension="observation_role",
            observation_role=kernel.ObservationRoleReference(
                system_id="project_local", system_edition=edition,
                code=code)),
        evidence=(CLAIM,), supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note=note,
    )


def association(support, *, context=AS_DESIGNED, orientation="aligned",
                supersedes=(), note="", **overrides):
    frg, vrg, prg, fld, vpa, vsm = support
    fields = dict(
        flow_anchor_id=FLOW_A,
        variable_anchor_id=VAR_A,
        participant_port_anchor_id=PORT_A,
        context=context,
        orientation=orientation,
        flow_registration_record_id=frg.record_id,
        variable_registration_record_id=vrg.record_id,
        port_registration_record_id=prg.record_id,
        flow_declaration_record_id=fld.record_id,
        variable_port_association_record_id=vpa.record_id,
        variable_semantic_declaration_record_id=vsm.record_id,
        evidence=(CLAIM,), supersedes=supersedes, recorded_at=T0,
        authority=AUTHORITY, note=note,
    )
    fields.update(overrides)
    return kernel.build_record(kernel.FlowMeasurementAssociation, **fields)


def withdrawal(target, *, note=""):
    return kernel.build_record(
        kernel.FlowMeasurementAssociationWithdrawal,
        withdraws=target.record_id,
        recorded_at=T0,
        authority=AUTHORITY,
        note=note,
    )


def foundation(context=AS_DESIGNED, *, vsm=None, vpa=None):
    base, frg, ports, pcn, source_pifs, sink_pifs = flow_fixture(
        context=context)
    fld = flow_declaration(
        frg, port_records=ports, pcn=pcn, source_pifs=source_pifs,
        sink_pifs=sink_pifs, context=context)
    vrg = variable_registration()
    vpa = variable_port(context=context) if vpa is None else vpa
    vsm = semantic() if vsm is None else vsm
    records = (*base, frg, fld, vrg, vpa, vsm)
    prg = next(item for item in ports if item.anchor.anchor_id == PORT_A)
    return records, (frg, vrg, prg, fld, vpa, vsm)


def store_with(tmp_path, *claims, context=AS_DESIGNED, vsm=None, vpa=None):
    records, support = foundation(context, vsm=vsm, vpa=vpa)
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, *claims):
        store.append(record)
    return store, support


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def test_exact_contract_fields_exports_builder_and_no_slice_b_surface():
    records, support = foundation()
    fma = association(support)
    fmw = withdrawal(fma)
    assert tuple(kernel.FlowMeasurementAssociation.model_fields) == (
        "record_kind", "schema_version", "record_id", "flow_anchor_id",
        "variable_anchor_id", "participant_port_anchor_id", "context",
        "orientation", "flow_registration_record_id",
        "variable_registration_record_id", "port_registration_record_id",
        "flow_declaration_record_id",
        "variable_port_association_record_id",
        "variable_semantic_declaration_record_id", "evidence", "supersedes",
        "recorded_at", "authority", "note")
    assert tuple(kernel.FlowMeasurementAssociationWithdrawal.model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert fma.record_id.startswith("fma_")
    assert fmw.record_id.startswith("fmw_")
    assert len(kernel.__all__) == 205 == len(set(kernel.__all__))
    flow_index = kernel.__all__.index("FlowDeclarationWithdrawal")
    assert kernel.__all__[flow_index + 1:flow_index + 3] == [
        "FlowMeasurementAssociation", "FlowMeasurementAssociationWithdrawal"]
    assert not any(name.startswith("FlowMeasurement") for name in
                   kernel.__all__ if name not in {
                       "FlowMeasurementAssociation",
                       "FlowMeasurementAssociationWithdrawal"})
    assert not any(hasattr(kernel.ModelQueries, name) for name in (
        "flow_measurement_association",
        "flow_measurement_associations_for_flow",
        "flow_measurement_associations_for_variable",
        "flow_measurement_associations_at_port",
        "flow_measurement_assertion"))
    assert records


def test_exact_support_admits_and_builds_immutable_indexes(tmp_path):
    records, support = foundation()
    fma = association(support)
    loaded = validate_record_collection(
        "test-model", {item.record_id: item for item in (*records, fma)})
    subject = (FLOW_A, VAR_A, PORT_A, AS_DESIGNED,
               "direct_measurement_relevance", "aligned")
    assert loaded.flow_measurement_associations[fma.record_id] == fma
    assert loaded.flow_measurement_ids_by_subject[subject] == (fma.record_id,)
    assert loaded.flow_measurement_ids_by_flow_context[
        (FLOW_A, AS_DESIGNED)] == (fma.record_id,)
    assert loaded.flow_measurement_ids_by_variable_context[
        (VAR_A, AS_DESIGNED)] == (fma.record_id,)
    assert loaded.flow_measurement_ids_by_port_context[
        (PORT_A, AS_DESIGNED)] == (fma.record_id,)
    assert loaded.flow_measurement_participant_role_by_id[fma.record_id] == \
        "source"
    assert loaded.flow_measurement_root_by_id[fma.record_id] == fma.record_id
    assert loaded.current_flow_measurement_tips_by_root[fma.record_id] == (fma,)
    for value in vars(loaded).values():
        if isinstance(value, MappingProxyType):
            with pytest.raises(TypeError):
                value["forged"] = ()


@pytest.mark.parametrize("field,prefix", [
    ("flow_registration_record_id", "frg"),
    ("variable_registration_record_id", "vrg"),
    ("port_registration_record_id", "prg"),
    ("flow_declaration_record_id", "fld"),
    ("variable_port_association_record_id", "vpa"),
    ("variable_semantic_declaration_record_id", "vsm"),
])
def test_every_missing_support_pin_rejects_before_write(tmp_path, field, prefix):
    store, support = store_with(tmp_path)
    attack = association(support, **{field: prefix + "_" + "f" * 64})
    before = snapshot(store)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(attack)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"
    assert snapshot(store) == before


@pytest.mark.parametrize("edition,code", [
    ("wrong-edition", "measured_actual"),
    ("ohk-observation-roles-1", "command_target"),
])
def test_context_independent_vsm_token_is_exact(tmp_path, edition, code):
    bad = semantic(edition=edition, code=code)
    records, support = foundation(vsm=bad)
    attack = association(support)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection(
            "test-model", {r.record_id: r for r in (*records, attack)})
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_SEMANTIC_INVALID"


def test_same_vsm_supports_distinct_contexts_with_matching_fld_vpa():
    vsm = semantic()
    first_records, first_support = foundation(vsm=vsm)
    second_records, second_support = foundation(VIEW_INDEPENDENT, vsm=vsm)
    first = association(first_support, note="designed")
    second = association(second_support, context=VIEW_INDEPENDENT,
                         note="independent")
    records = {r.record_id: r for r in (
        *first_records, *second_records, first, second)}
    loaded = validate_record_collection("test-model", records)
    assert loaded.flow_measurement_ids_by_variable_context[
        (VAR_A, AS_DESIGNED)] == (first.record_id,)
    assert loaded.flow_measurement_ids_by_variable_context[
        (VAR_A, VIEW_INDEPENDENT)] == (second.record_id,)


def test_forged_vsm_context_and_derived_role_fields_reject():
    vsm = semantic()
    forged = vsm.model_copy(update={"context": AS_DESIGNED})
    records, support = foundation(vsm=forged)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", {
            r.record_id: r for r in (*records, association(support))},
            verify_hashes=False)
    assert error.value.error_code == "MODEL_RECORD_INVALID"
    with pytest.raises(kernel.ModelIntegrityError):
        association(support, participant_role="source")


def test_subject_dag_independent_roots_fork_merge_and_withdrawal(tmp_path):
    store, support = store_with(tmp_path)
    independent = association(support, note="independent")
    root = association(support, note="root")
    left = association(support, supersedes=(root.record_id,), note="left")
    right = association(support, supersedes=(root.record_id,), note="right")
    merged = association(
        support, supersedes=(left.record_id, right.record_id), note="merged")
    event = withdrawal(independent)
    for record in (independent, root, left, right, merged, event):
        store.append(record)
    loaded = store.load()
    assert loaded.flow_measurement_root_by_id[merged.record_id] == root.record_id
    assert loaded.flow_measurement_ancestry_by_id[merged.record_id] == tuple(
        sorted((root.record_id, left.record_id, right.record_id)))
    assert loaded.current_flow_measurement_tips_by_root[root.record_id] == (
        merged,)
    assert loaded.current_flow_measurement_tips_by_root[independent.record_id] \
        == ()
    assert loaded.flow_measurement_withdrawn_by[independent.record_id] == (
        event.record_id,)


def test_cross_root_changed_subject_and_successor_of_withdrawn_reject(tmp_path):
    store, support = store_with(tmp_path)
    first = association(support, note="one")
    second = association(support, note="two")
    store.append(first)
    store.append(second)
    for attack in (
        association(support, supersedes=(first.record_id, second.record_id),
                    note="cross"),
        association(support, orientation="opposite",
                    supersedes=(first.record_id,), note="drift"),
    ):
        before = snapshot(store)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.append(attack)
        assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_LINEAGE_INVALID"
        assert snapshot(store) == before

    withdrawn_store, support = store_with(tmp_path / "withdrawn")
    root = association(support, note="root")
    withdrawn_store.append(root)
    withdrawn_store.append(withdrawal(root))
    with pytest.raises(kernel.ModelIntegrityError) as error:
        withdrawn_store.append(association(
            support, supersedes=(root.record_id,), note="late successor"))
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_WITHDRAWAL_INVALID"


def test_replay_is_membership_relative_and_fmw_is_uncitable(tmp_path):
    store, support = store_with(tmp_path)
    root = association(support, note="root")
    child = association(support, supersedes=(root.record_id,), note="child")
    event = withdrawal(child)
    for record in (root, child, event):
        store.append(record)
    membership = tuple(i for i in store.load().revision.record_ids
                       if i not in {child.record_id, event.record_id})
    replayed = store.replay(reversed(membership))
    assert replayed.current_flow_measurement_tips_by_root[root.record_id] == (
        root,)
    with pytest.raises(ValidationError):
        kernel.ModelRecordEvidence(
            kind="model_record", record_id=event.record_id)


def test_effective_body_and_indexes_are_order_deterministic():
    records, support = foundation()
    first = association(support, note="one")
    second = association(support, note="two")
    forward = validate_record_collection(
        "test-model", {r.record_id: r for r in (*records, first, second)})
    reverse = validate_record_collection(
        "test-model", {r.record_id: r for r in reversed(
            (*records, first, second))})
    names = (
        "flow_measurement_ids_by_subject",
        "flow_measurement_ids_by_flow_context",
        "flow_measurement_ids_by_variable_context",
        "flow_measurement_ids_by_port_context",
        "flow_measurement_root_by_id",
        "flow_measurement_ids_by_effective_body",
        "flow_measurement_root_ids_by_subject",
        "flow_measurement_root_ids_by_effective_body",
    )
    for name in names:
        assert dict(getattr(forward, name)) == dict(getattr(reverse, name))
    assert forward.revision == reverse.revision
