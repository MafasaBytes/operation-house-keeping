"""FM-001 Slice A declaration, closure, lifecycle, index, and replay gates."""

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch

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


def variable_port_withdrawal(target, *, note=""):
    return kernel.build_record(
        kernel.VariablePortAssociationWithdrawal,
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
    predecessor_digest = hashlib.sha256(json.dumps(
        kernel.__all__[:-2], separators=(",", ":")).encode()).hexdigest()
    assert predecessor_digest == \
        "7821c7582f1332addca8fd467004c477262ea4e679c33f6bbe0a22831db83ce1"
    assert kernel.__all__[-2:] == [
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


@pytest.mark.parametrize("support_position", [3, 4])
def test_fld_and_vpa_context_substitution_rejects(support_position):
    first_records, support = foundation()
    other_records, other_support = foundation(VIEW_INDEPENDENT)
    substituted = list(support)
    substituted[support_position] = other_support[support_position]
    attack = association(tuple(substituted))
    records = {r.record_id: r for r in (
        *first_records, *other_records, attack)}
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", records)
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_SUPPORT_INVALID"


def test_wrong_variable_vsm_and_quantity_kind_refuse():
    wrong_variable = "var_" + "f" * 32
    wrong_vsm = semantic(variable=wrong_variable)
    records, support = foundation(vsm=wrong_vsm)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", {
            r.record_id: r for r in (*records, association(support))})
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    quantity = kernel.build_record(
        kernel.VariableSemanticDeclaration,
        variable_anchor_id=VAR_A,
        declaration=kernel.QuantityKindDeclaration(
            dimension="quantity_kind",
            quantity_kind=kernel.QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="temperature")),
        evidence=(CLAIM,), supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note="")
    records, support = foundation(vsm=quantity)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", {
            r.record_id: r for r in (*records, association(support))})
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_SEMANTIC_INVALID"


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


def test_partial_same_root_repair_remains_conflicted_until_full_convergence(
        tmp_path):
    store, support = store_with(tmp_path)
    root = association(support, note="root")
    left = association(support, supersedes=(root.record_id,), note="left")
    right = association(support, supersedes=(root.record_id,), note="right")
    partial = association(
        support, supersedes=(left.record_id,), note="partial repair")
    for record in (root, left, right, partial):
        store.append(record)
    loaded = store.load()
    assert loaded.current_flow_measurement_tips_by_root[root.record_id] == \
        tuple(sorted((right, partial), key=lambda item: item.record_id))
    complete = association(
        support, supersedes=(right.record_id, partial.record_id),
        note="complete convergence")
    store.append(complete)
    assert store.load().current_flow_measurement_tips_by_root[
        root.record_id] == (complete,)


def test_nonparticipant_port_rejects_before_write(tmp_path):
    other_port = "prt_" + "9" * 32
    store, support = store_with(tmp_path)
    original = support[2]
    registration = kernel.build_record(
        kernel.PortRegistration,
        anchor=original.anchor.model_copy(update={
            "anchor_id": other_port, "display_name": "Other port"}),
        owner_entity_anchor_id=original.owner_entity_anchor_id,
        evidence=original.evidence, recorded_at=original.recorded_at,
        authority=original.authority, note="")
    vpa = variable_port(port=other_port)
    store.append(registration)
    store.append(vpa)
    substituted = list(support)
    substituted[2] = registration
    substituted[4] = vpa
    attack = association(
        tuple(substituted), participant_port_anchor_id=other_port)
    before = snapshot(store)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(attack)
    assert error.value.error_code == \
        "MODEL_FLOW_MEASUREMENT_PARTICIPANT_INVALID"
    assert snapshot(store) == before


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


def test_fma_is_citable_but_positive_requires_evidence(tmp_path):
    store, support = store_with(tmp_path)
    first = association(support, note="basis")
    store.append(first)
    cited = association(
        support, note="cites FMA",
        evidence=(kernel.ModelRecordEvidence(
            kind="model_record", record_id=first.record_id),))
    store.append(cited)
    assert cited.record_id in store.load().flow_measurement_associations
    with pytest.raises(kernel.ModelIntegrityError) as error:
        association(support, evidence=())
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_selective_fork_tip_withdrawal_and_invalid_targets(tmp_path):
    store, support = store_with(tmp_path)
    root = association(support, note="root")
    left = association(support, supersedes=(root.record_id,), note="left")
    right = association(support, supersedes=(root.record_id,), note="right")
    for record in (root, left, right):
        store.append(record)
    event = withdrawal(left)
    store.append(event)
    loaded = store.load()
    assert loaded.flow_measurement_withdrawn_by[left.record_id] == (
        event.record_id,)
    assert loaded.current_flow_measurement_tips_by_root[root.record_id] == (
        right,)
    for attack in (
        withdrawal(left, note="duplicate"),
        withdrawal(root, note="superseded"),
    ):
        before = snapshot(store)
        with pytest.raises(kernel.ModelIntegrityError) as error:
            store.append(attack)
        assert error.value.error_code == \
            "MODEL_FLOW_MEASUREMENT_WITHDRAWAL_INVALID"
        assert snapshot(store) == before


def test_hostile_nested_instances_orientation_subclass_and_stale_id_refuse():
    records, support = foundation()
    class HostileString(str):
        pass

    with pytest.raises(kernel.ModelIntegrityError):
        association(support, orientation=HostileString("aligned"))

    valid = association(support)
    forged_context = valid.context.model_copy(update={"secret": "hidden"})
    with pytest.raises(kernel.ModelIntegrityError):
        association(support, context=forged_context)

    stale = valid.model_copy(update={"orientation": "opposite"})
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", {
            r.record_id: r for r in (*records, stale)})
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


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


def test_support_pins_remain_historical_when_vpa_is_noncurrent():
    for later_records in ("superseded", "withdrawn", "conflicted"):
        records, support = foundation()
        pinned = support[4]
        if later_records == "superseded":
            additions = (
                variable_port(supersedes=(pinned.record_id,), note="later"),
            )
        elif later_records == "withdrawn":
            additions = (variable_port_withdrawal(pinned),)
        else:
            additions = (
                variable_port(supersedes=(pinned.record_id,), note="left"),
                variable_port(supersedes=(pinned.record_id,), note="right"),
            )
        claim = association(support, note=later_records)
        loaded = validate_record_collection(
            "test-model",
            {row.record_id: row for row in (*records, *additions, claim)},
        )
        assert loaded.flow_measurement_associations[claim.record_id] == claim
        assert claim.variable_port_association_record_id == pinned.record_id


def test_effective_body_corroboration_and_disagreement_are_exact():
    records, support = foundation()
    first = association(support, note="first corroborating root")
    second = association(support, note="second corroborating root")
    alternate_vsm = semantic(note="alternate exact support record")
    alternate_support = (*support[:-1], alternate_vsm)
    disagreeing = association(alternate_support, note="different six-pin body")
    loaded = validate_record_collection(
        "test-model",
        {row.record_id: row for row in (
            *records, alternate_vsm, first, second, disagreeing)},
    )
    subject = (FLOW_A, VAR_A, PORT_A, AS_DESIGNED,
               "direct_measurement_relevance", "aligned")
    first_body = loaded.flow_measurement_effective_body_by_id[first.record_id]
    assert first_body == loaded.flow_measurement_effective_body_by_id[
        second.record_id]
    assert first_body != loaded.flow_measurement_effective_body_by_id[
        disagreeing.record_id]
    assert loaded.flow_measurement_root_ids_by_effective_body[first_body] == \
        tuple(sorted((first.record_id, second.record_id)))
    assert loaded.flow_measurement_root_ids_by_subject[subject] == tuple(
        sorted((first.record_id, second.record_id, disagreeing.record_id)))
    assert loaded.flow_measurement_disagreeing_root_ids_by_subject[subject] == \
        loaded.flow_measurement_root_ids_by_subject[subject]


def test_missing_duplicate_self_and_cyclic_parents_refuse():
    records, support = foundation()
    root = association(support, note="root")
    missing = association(
        support,
        supersedes=("fma_" + "f" * 64,),
        note="missing",
    )
    with pytest.raises(kernel.ModelIntegrityError):
        validate_record_collection(
            "test-model", {row.record_id: row for row in (*records, missing)})

    duplicate = root.model_copy(update={
        "supersedes": (root.record_id, root.record_id),
    })
    self_parent = root.model_copy(update={"supersedes": (root.record_id,)})
    for forged in (duplicate, self_parent):
        with pytest.raises(kernel.ModelIntegrityError):
            validate_record_collection(
                "test-model",
                {row.record_id: row for row in (*records, forged)},
                verify_hashes=False,
            )

    first = association(support, note="cycle one")
    second = association(support, note="cycle two")
    first = first.model_copy(update={"supersedes": (second.record_id,)})
    second = second.model_copy(update={"supersedes": (first.record_id,)})
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection(
            "test-model",
            {row.record_id: row for row in (*records, first, second)},
            verify_hashes=False,
        )
    assert error.value.error_code == "MODEL_FLOW_MEASUREMENT_LINEAGE_INVALID"


def test_unknown_and_foreign_withdrawal_targets_refuse():
    records, support = foundation()
    claim = association(support)
    unknown = kernel.build_record(
        kernel.FlowMeasurementAssociationWithdrawal,
        withdraws="fma_" + "f" * 64,
        recorded_at=T0,
        authority=AUTHORITY,
        note="unknown",
    )
    for event in (unknown,):
        with pytest.raises(kernel.ModelIntegrityError) as error:
            validate_record_collection(
                "test-model",
                {row.record_id: row for row in (*records, claim, event)},
            )
        assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    foreign = unknown.model_copy(update={
        "withdraws": support[4].record_id,
    })
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementAssociationWithdrawal.model_validate(
            foreign.model_dump(mode="python", warnings=False),
        )


@pytest.mark.parametrize("value", [
    None,
    True,
    "aggregate",
    "whole_flow",
    "storage",
    "boundary",
    "control_volume",
    FLOW_A,
])
def test_non_port_locus_forms_refuse_before_store_access(value):
    _, support = foundation()
    with pytest.raises(kernel.ModelIntegrityError):
        association(support, participant_port_anchor_id=value)
    assert association(support).participant_port_anchor_id == PORT_A


@pytest.mark.parametrize("value", [None, True, "unknown", "Aligned"])
def test_orientation_admission_is_exact(value):
    _, support = foundation()
    with pytest.raises(kernel.ModelIntegrityError):
        association(support, orientation=value)
    assert association(support).orientation == "aligned"


def test_flow_variable_port_and_context_parent_drift_refuse():
    records, support = foundation()
    root = association(support, note="root")
    foreign_records, foreign_support = foundation(VIEW_INDEPENDENT)
    attacks = (
        association(
            foreign_support,
            context=VIEW_INDEPENDENT,
            supersedes=(root.record_id,),
            note="context drift",
        ),
        root.model_copy(update={
            "flow_anchor_id": "flw_" + "f" * 32,
            "supersedes": (root.record_id,),
        }),
        root.model_copy(update={
            "variable_anchor_id": "var_" + "f" * 32,
            "supersedes": (root.record_id,),
        }),
        root.model_copy(update={
            "participant_port_anchor_id": "prt_" + "f" * 32,
            "supersedes": (root.record_id,),
        }),
    )
    all_records = (*records, *foreign_records, root)
    for attack in attacks:
        with pytest.raises(kernel.ModelIntegrityError):
            validate_record_collection(
                "test-model",
                {row.record_id: row for row in (*all_records, attack)},
                verify_hashes=False,
            )


def test_model_construct_hidden_state_and_wrong_nested_union_refuse():
    records, support = foundation()
    valid = association(support)
    plain = valid.model_dump(mode="python", warnings=False)
    forged = kernel.FlowMeasurementAssociation.model_construct(**plain)
    forged.__dict__["hidden_state"] = "forged"
    with pytest.raises(kernel.ModelIntegrityError):
        validate_record_collection(
            "test-model",
            {row.record_id: row for row in (*records, forged)},
            verify_hashes=False,
        )

    wrong_union = dict(plain)
    wrong_union["context"] = {
        "kind": "forged_context",
        "view": "as_designed",
    }
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementAssociation.model_validate(wrong_union)


def test_pure_fm_contract_canonical_and_collection_validation_do_no_io():
    records, support = foundation()
    claim = association(support)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("pure FM validation attempted I/O")

    with (
        patch("builtins.open", forbidden),
        patch.object(Path, "open", forbidden),
        patch.object(Path, "read_bytes", forbidden),
        patch.object(Path, "write_bytes", forbidden),
        patch("socket.socket", forbidden),
    ):
        rebuilt = kernel.FlowMeasurementAssociation.model_validate(
            claim.model_dump(mode="python", warnings=False))
        loaded = validate_record_collection(
            "test-model", {row.record_id: row for row in (*records, rebuilt)})
    assert loaded.flow_measurement_associations[claim.record_id] == claim
