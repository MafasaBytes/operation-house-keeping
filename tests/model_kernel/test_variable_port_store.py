"""VP-001 Slice A validating-store, lifecycle, and index red baseline."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.model_kernel import (
    ModelIntegrityError, ModelRecordEvidence, ModelStore,
)
from tests.model_kernel.builders import (
    ENT_A, ENT_B, registration as entity_registration,
    variable_registration,
)
from tests.model_kernel.test_port_records import registration as port_registration
from tests.model_kernel.test_variable_port_records import (
    CONTEXT, EVIDENCE, PORT, VARIABLE, association, withdrawal,
)


PORT_B = "prt_" + "2" * 32
VARIABLE_B = "var_" + "c" * 32
OTHER_CONTEXT = {"kind": "lifecycle_view", "view": "as_built"}


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def append_all(store, *records):
    for record in records:
        store.append(record)
    return store


def port_record(port=PORT, owner=ENT_A):
    template = port_registration()
    return port_registration(
        anchor=template.anchor.model_copy(update={
            "anchor_id": port, "display_name": f"Port {port[-1]}"}),
        owner_entity_anchor_id=owner)


def base(tmp_path, *, variable=VARIABLE, port=PORT, owner=ENT_A,
         variable_owner=None, port_owner=None):
    variable_owner = owner if variable_owner is None else variable_owner
    port_owner = owner if port_owner is None else port_owner
    store = ModelStore(tmp_path / "demo-printer")
    for entity in tuple(dict.fromkeys((variable_owner, port_owner))):
        store.append(entity_registration(entity))
    store.append(variable_registration(variable, owner=variable_owner))
    store.append(port_record(port, owner=port_owner))
    return store


def assert_atomic_rejection(store, record, code):
    before = snapshot(store)
    with pytest.raises(ModelIntegrityError) as error:
        store.append(record)
    assert error.value.error_code == code
    assert snapshot(store) == before


@pytest.mark.parametrize("missing", ["variable", "port"])
def test_both_registered_endpoints_are_required_atomically(tmp_path, missing):
    store = ModelStore(tmp_path / "demo-printer")
    store.append(entity_registration(ENT_A))
    if missing != "variable":
        store.append(variable_registration(VARIABLE, owner=ENT_A))
    if missing != "port":
        store.append(port_record())
    assert_atomic_rejection(store, association(), "MODEL_REFERENCE_INVALID")


def test_exact_same_owner_is_required_and_never_propagated(tmp_path):
    store = base(tmp_path, variable_owner=ENT_A, port_owner=ENT_B)
    assert_atomic_rejection(store, association(), "MODEL_REFERENCE_INVALID")
    admitted = append_all(base(tmp_path / "same"), association()).load()
    assert association().record_id in admitted.variable_port_associations


def test_model_record_evidence_closes_on_append_and_replay(tmp_path):
    missing = "reg_" + "f" * 64
    claim = association(evidence=(ModelRecordEvidence(
        kind="model_record", record_id=missing),))
    assert_atomic_rejection(base(tmp_path / "append"), claim,
                            "MODEL_REFERENCE_INVALID")
    support = entity_registration(ENT_B)
    claim = association(evidence=(ModelRecordEvidence(
        kind="model_record", record_id=support.record_id),))
    store = append_all(base(tmp_path / "replay"), support, claim)
    subset = tuple(i for i in store.load().revision.record_ids
                   if i != support.record_id)
    with pytest.raises(ModelIntegrityError) as error:
        store.replay(subset)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_all_required_indexes_are_immutable_complete_and_canonical(tmp_path):
    root = association(note="root")
    child = association(supersedes=(root.record_id,), note="child")
    loaded = append_all(base(tmp_path), root, child).load()
    subject = (VARIABLE, PORT, CONTEXT)
    assert tuple(loaded.variable_port_associations) == tuple(sorted(
        (root.record_id, child.record_id)))
    assert loaded.variable_port_association_ids_by_subject[subject] == tuple(
        sorted((root.record_id, child.record_id)))
    assert loaded.variable_port_association_ids_by_variable_context[
        (VARIABLE, CONTEXT)] == tuple(sorted((root.record_id, child.record_id)))
    assert loaded.variable_port_association_ids_by_port_context[
        (PORT, CONTEXT)] == tuple(sorted((root.record_id, child.record_id)))
    assert loaded.variable_port_association_root_by_id[child.record_id] == \
        root.record_id
    assert loaded.variable_port_association_ancestry_by_id[child.record_id] == (
        root.record_id,)
    assert loaded.variable_port_association_superseded_by[root.record_id] == (
        child.record_id,)
    assert tuple(item.record_id for item in
                 loaded.current_variable_port_association_tips_by_root[
                     root.record_id]) == (child.record_id,)
    assert loaded.variable_port_association_withdrawn_by[child.record_id] == ()
    assert loaded.variable_port_association_withdrawals_by_target == {}
    for mapping in (
        loaded.variable_port_associations,
        loaded.variable_port_association_ids_by_subject,
        loaded.variable_port_association_root_by_id,
        loaded.variable_port_association_ancestry_by_id,
        loaded.current_variable_port_association_tips_by_root,
    ):
        with pytest.raises(TypeError):
            mapping["forged"] = ()


def test_independent_roots_fork_partial_and_full_convergence(tmp_path):
    independent = association(note="independent")
    root = association(note="root")
    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")
    partial = association(supersedes=(left.record_id,), note="partial")
    loaded = append_all(base(tmp_path / "partial"), independent, root,
                        left, right, partial).load()
    assert loaded.variable_port_association_root_by_id[independent.record_id] \
        == independent.record_id
    assert tuple(item.record_id for item in
                 loaded.current_variable_port_association_tips_by_root[
                     root.record_id]) == tuple(sorted(
                         (right.record_id, partial.record_id)))
    merge = association(supersedes=(left.record_id, right.record_id),
                        note="merge")
    converged = append_all(base(tmp_path / "full"), root, left, right,
                           merge).load()
    assert tuple(item.record_id for item in
                 converged.current_variable_port_association_tips_by_root[
                     root.record_id]) == (merge.record_id,)
    assert converged.variable_port_association_ancestry_by_id[merge.record_id] \
        == tuple(sorted((root.record_id, left.record_id, right.record_id)))


def test_cross_root_and_changed_subject_or_context_are_rejected(tmp_path):
    one = association(note="one")
    two = association(note="two")
    cross = association(supersedes=(one.record_id, two.record_id), note="bad")
    store = append_all(base(tmp_path / "roots"), one, two)
    # Close both alternate endpoints so these attacks reach lineage-subject
    # validation rather than failing earlier at ordinary reference closure.
    store.append(variable_registration(VARIABLE_B, owner=ENT_A))
    store.append(port_record(PORT_B, owner=ENT_A))
    assert_atomic_rejection(store, cross,
                            "MODEL_VARIABLE_PORT_LINEAGE_INVALID")
    for changed in (
        association(variable_anchor_id=VARIABLE_B,
                    supersedes=(one.record_id,), note="variable"),
        association(port_anchor_id=PORT_B,
                    supersedes=(one.record_id,), note="port"),
        association(context=OTHER_CONTEXT,
                    supersedes=(one.record_id,), note="context"),
    ):
        assert_atomic_rejection(store, changed,
                                "MODEL_VARIABLE_PORT_LINEAGE_INVALID")


def test_selective_fork_tip_withdrawal_is_valid_and_sibling_remains(tmp_path):
    root = association(note="root")
    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")
    event = withdrawal(left.record_id)
    loaded = append_all(base(tmp_path), root, left, right, event).load()
    assert loaded.variable_port_association_withdrawals[event.record_id] == event
    assert loaded.variable_port_association_withdrawn_by[left.record_id] == (
        event.record_id,)
    assert loaded.variable_port_association_withdrawals_by_target[
        left.record_id] == (event.record_id,)
    assert tuple(item.record_id for item in
                 loaded.current_variable_port_association_tips_by_root[
                     root.record_id]) == (right.record_id,)


def test_invalid_withdrawal_targets_successor_interaction_and_revival(tmp_path):
    root = association(note="root")
    child = association(supersedes=(root.record_id,), note="child")
    store = append_all(base(tmp_path / "superseded"), root, child)
    assert_atomic_rejection(store, withdrawal(root.record_id),
                            "MODEL_VARIABLE_PORT_WITHDRAWAL_INVALID")
    assert_atomic_rejection(base(tmp_path / "unknown"), withdrawal(),
                            "MODEL_REFERENCE_INVALID")

    event = withdrawal(root.record_id)
    withdrawn = append_all(base(tmp_path / "withdrawn"), root, event)
    assert_atomic_rejection(withdrawn, withdrawal(root.record_id, note="again"),
                            "MODEL_VARIABLE_PORT_WITHDRAWAL_INVALID")
    assert_atomic_rejection(withdrawn, child,
                            "MODEL_VARIABLE_PORT_WITHDRAWAL_INVALID")
    revived_ids = tuple(i for i in withdrawn.load().revision.record_ids
                        if i != event.record_id)
    revived = withdrawn.replay(revived_ids)
    assert tuple(item.record_id for item in
                 revived.current_variable_port_association_tips_by_root[
                     root.record_id]) == (root.record_id,)


def test_replay_omitting_successor_revives_parent_and_contexts_are_separate(
        tmp_path):
    root = association(note="root")
    child = association(supersedes=(root.record_id,), note="child")
    other = association(context=OTHER_CONTEXT, note="other context")
    store = append_all(base(tmp_path), root, child, other)
    historical = store.replay(tuple(i for i in store.load().revision.record_ids
                                    if i != child.record_id))
    assert tuple(item.record_id for item in
                 historical.current_variable_port_association_tips_by_root[
                     root.record_id]) == (root.record_id,)
    assert historical.variable_port_association_ids_by_subject[
        (VARIABLE, PORT, CONTEXT)] == (root.record_id,)
    assert historical.variable_port_association_ids_by_subject[
        (VARIABLE, PORT, type(CONTEXT).model_validate(OTHER_CONTEXT))] == (
            other.record_id,)
