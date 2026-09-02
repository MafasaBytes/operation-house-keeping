"""ST-002 Slice B RC2 shared state-derivation parity and reachability."""

import ast
from datetime import timedelta
from pathlib import Path

import pytest

import backend.model_kernel as kernel
import backend.model_kernel.transition_results as transition_results
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.st001_slice_a_helpers import (
    AS_DESIGNED,
    state_declaration,
    state_withdrawal,
)
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    STATE_A,
    STATE_B,
    T0,
    T1,
    TRANSITION_A,
    transition_declaration,
    transition_fixture,
)


REACHABLE = (
    ("declared", "current", "exact_current"),
    ("declared", "superseded", "pinned_declaration_superseded"),
    ("declared", "withdrawn", "pinned_declaration_withdrawn"),
    ("conflicted", "current", "endpoint_state_conflicted"),
    ("conflicted", "superseded", "endpoint_state_conflicted"),
    ("conflicted", "withdrawn", "endpoint_state_conflicted"),
    ("inactive", "superseded", "endpoint_state_inactive"),
    ("inactive", "withdrawn", "endpoint_state_inactive"),
)


def target_fixture(role):
    records, registration, from_registration, to_registration, \
        from_root, to_root = transition_fixture()
    if role == "from":
        return (records, registration, from_registration, to_registration,
                from_root, to_root, from_registration, from_root)
    return (records, registration, from_registration, to_registration,
            from_root, to_root, to_registration, to_root)


def state_shape(registration, root, conclusion, activity):
    state_anchor_id = registration.anchor.anchor_id
    additions = []
    pin = root
    if (conclusion, activity) == ("declared", "current"):
        pass
    elif (conclusion, activity) == ("declared", "superseded"):
        additions.append(state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(root.record_id,), recorded_at=T1,
            note="declared successor"))
    elif (conclusion, activity) == ("declared", "withdrawn"):
        additions.extend((
            state_withdrawal(root, recorded_at=T1,
                             note="withdraw pinned root"),
            state_declaration(
                registration, state_anchor_id=state_anchor_id,
                recorded_at=T1 + timedelta(seconds=1),
                note="surviving healthy peer"),
        ))
    elif (conclusion, activity) in {
            ("conflicted", "current"),
            ("conflicted", "superseded")}:
        left = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(root.record_id,), recorded_at=T1,
            note="fork left")
        right = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=1), note="fork right")
        additions.extend((left, right))
        if activity == "current":
            pin = left
    elif (conclusion, activity) == ("conflicted", "withdrawn"):
        peer = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            recorded_at=T1 + timedelta(seconds=1), note="fork peer root")
        left = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(peer.record_id,),
            recorded_at=T1 + timedelta(seconds=2), note="peer fork left")
        right = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(peer.record_id,),
            recorded_at=T1 + timedelta(seconds=3), note="peer fork right")
        additions.extend((
            state_withdrawal(root, recorded_at=T1,
                             note="withdraw pinned root"),
            peer, left, right,
        ))
    elif (conclusion, activity) == ("inactive", "superseded"):
        successor = state_declaration(
            registration, state_anchor_id=state_anchor_id,
            supersedes=(root.record_id,), recorded_at=T1,
            note="terminal successor")
        additions.extend((
            successor,
            state_withdrawal(
                successor, recorded_at=T1 + timedelta(seconds=1),
                note="withdraw terminal successor"),
        ))
    elif (conclusion, activity) == ("inactive", "withdrawn"):
        additions.append(state_withdrawal(
            root, recorded_at=T1, note="withdraw sole root"))
    else:
        raise AssertionError("unsupported parity fixture")
    return tuple(additions), pin


def parity_world(tmp_path, role, conclusion, activity):
    (records, transition_registration, from_registration, to_registration,
     from_root, to_root, target_registration, target_root) = target_fixture(
         role)
    additions, pin = state_shape(
        target_registration, target_root, conclusion, activity)
    from_pin = pin if role == "from" else from_root
    to_pin = pin if role == "to" else to_root
    declaration = transition_declaration(
        transition_registration,
        from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_pin,
        to_declaration=to_pin,
        recorded_at=T1 + timedelta(minutes=1),
        note=f"{role}-{conclusion}-{activity}")
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, *additions, transition_registration, declaration):
        store.append(record)
    return store.load(), declaration, target_registration, pin


@pytest.mark.parametrize("role", ("from", "to"))
@pytest.mark.parametrize("conclusion,activity,alignment", REACHABLE)
def test_rc2_every_reachable_cell_matches_public_state_derivations(
        tmp_path, role, conclusion, activity, alignment):
    loaded, declaration, state_registration, pinned = parity_world(
        tmp_path, role, conclusion, activity)
    queries = kernel.ModelQueries(loaded)
    transition = queries.transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert transition.conclusion == "declared"
    group = transition.effective_body_groups[0]
    endpoint = group.from_endpoint if role == "from" else group.to_endpoint
    public_state = queries.state_declaration(
        state_registration.anchor.anchor_id, context=AS_OPERATED)
    public_assertion = queries.state_assertion(pinned.record_id)
    assert endpoint.role == role
    assert endpoint.state_anchor_id == state_registration.anchor.anchor_id
    assert endpoint.declaration == pinned
    assert endpoint.state_declaration_conclusion == \
        public_state.conclusion == conclusion
    assert endpoint.pinned_declaration_activity == \
        public_assertion.activity == activity
    assert public_assertion.containing_subject_conclusion == conclusion
    assert endpoint.alignment == alignment
    assert group.representative_declaration == declaration


def test_transition_endpoint_adapter_runtime_calls_both_shared_st_helpers(
        tmp_path, monkeypatch):
    declaration_calls = []
    assertion_calls = []
    original_declaration = transition_results._state_declaration_payload
    original_assertion = transition_results._state_assertion_payload

    def declaration_spy(*args, **kwargs):
        declaration_calls.append((args[2], args[3]))
        return original_declaration(*args, **kwargs)

    def assertion_spy(*args, **kwargs):
        assertion_calls.append(args[2])
        return original_assertion(*args, **kwargs)

    monkeypatch.setattr(
        transition_results, "_state_declaration_payload", declaration_spy)
    monkeypatch.setattr(
        transition_results, "_state_assertion_payload", assertion_spy)
    loaded, _, _, _ = parity_world(
        tmp_path, "from", "declared", "current")
    result = kernel.ModelQueries(loaded).transition_declaration(
        TRANSITION_A, context=AS_OPERATED)
    assert result.conclusion == "declared"
    assert {anchor_id for anchor_id, _ in declaration_calls} == {
        STATE_A, STATE_B}
    assert set(assertion_calls) == {
        result.effective_body_groups[0].from_endpoint.declaration.record_id,
        result.effective_body_groups[0].to_endpoint.declaration.record_id,
    }


def test_transition_results_import_and_source_enforce_one_st_derivation():
    path = Path("backend/model_kernel/transition_results.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "backend.model_kernel.state_results"
        for alias in node.names
    }
    assert {"_state_declaration_payload", "_state_assertion_payload"} <= imports
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert "backend.model_kernel.queries" not in imported_modules
    assert "backend.model_kernel.store" not in imported_modules
    assert "ModelStore" not in source
    for forbidden in (
        "current_state_declaration_tips_by_root",
        "state_declaration_ids_by_key",
        "state_declaration_root_by_id",
        "_state_effective_body_bytes",
        "backend.state_classification",
    ):
        assert forbidden not in source


@pytest.mark.parametrize("activity", ("current", "superseded", "withdrawn"))
def test_not_registered_endpoint_cells_reject_by_full_set_closure(activity):
    records, transition_registration, from_registration, to_registration, \
        from_root, to_root = transition_fixture()
    additions, pin = state_shape(
        from_registration, from_root,
        "declared" if activity != "withdrawn" else "inactive", activity)
    declaration = transition_declaration(
        transition_registration,
        from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=pin, to_declaration=to_root)
    collection = {
        record.record_id: record
        for record in (*records, *additions,
                       transition_registration, declaration)
        if record.record_id != from_registration.record_id
    }
    with pytest.raises(kernel.ModelIntegrityError):
        validate_record_collection("test-model", collection)


@pytest.mark.parametrize("activity", ("current", "superseded", "withdrawn"))
def test_not_declared_endpoint_cells_reject_exact_context_mismatch(activity):
    records, transition_registration, from_registration, to_registration, \
        from_root, to_root = transition_fixture()
    additions = []
    pin = from_root
    if activity == "superseded":
        additions.append(state_declaration(
            from_registration, state_anchor_id=STATE_A,
            supersedes=(from_root.record_id,), recorded_at=T1,
            note="other-context successor"))
    elif activity == "withdrawn":
        additions.append(state_withdrawal(
            from_root, recorded_at=T1, note="other-context withdrawal"))
    declaration = transition_declaration(
        transition_registration,
        from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=pin, to_declaration=to_root,
        context=AS_DESIGNED,
        note=f"context mismatch {activity}")
    collection = {record.record_id: record for record in (
        *records, *additions, transition_registration, declaration)}
    with pytest.raises(kernel.ModelIntegrityError) as error:
        validate_record_collection("test-model", collection)
    assert error.value.error_code == "MODEL_TRANSITION_DECLARATION_INVALID"


def test_inactive_current_is_structurally_unreachable(tmp_path):
    loaded, _, registration, current_pin = parity_world(
        tmp_path / "current", "from", "declared", "current")
    queries = kernel.ModelQueries(loaded)
    assert queries.state_assertion(current_pin.record_id).activity == "current"
    assert queries.state_declaration(
        registration.anchor.anchor_id,
        context=AS_OPERATED).conclusion == "declared"

    with pytest.raises(ValueError):
        transition_results._endpoint_alignment("inactive", "current")

    records, _, from_registration, _, from_root, _ = transition_fixture()
    successor = state_declaration(
        from_registration, state_anchor_id=STATE_A,
        supersedes=(from_root.record_id,), recorded_at=T1,
        note="successor")
    bad_withdrawal = state_withdrawal(
        from_root, recorded_at=T1 + timedelta(seconds=1),
        note="successor plus withdrawal")
    collection = {record.record_id: record
                  for record in (*records, successor, bad_withdrawal)}
    with pytest.raises(kernel.ModelIntegrityError):
        validate_record_collection("test-model", collection)
