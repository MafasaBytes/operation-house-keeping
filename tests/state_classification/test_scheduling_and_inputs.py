"""Deterministic branch scheduling and typed structural-input rejection."""

from datetime import datetime

import pytest

from backend.model_state import SourceSelector
from backend.state_classification import (
    StateClassificationInputError,
    StateConditionSource,
)
from tests.state_classification.helpers import (
    AS_OF,
    AS_OPERATED,
    CON_A,
    CON_B,
    STATE_A,
    condition_sources,
    facade,
    state_model,
)


@pytest.mark.parametrize("case", [
    "malformed_state", "malformed_context", "naive_cutoff",
    "non_tuple_sources", "malformed_source", "hidden_extra",
])
def test_invalid_requests_fail_before_kernel_or_cn_branch_access(
        tmp_path, monkeypatch, case):
    model, _, _ = state_model(tmp_path)
    queries = facade(tmp_path, model=model)
    calls = []
    monkeypatch.setattr(
        queries.constraints, "constraint_evaluation",
        lambda *args, **kwargs: calls.append((args, kwargs)))
    state = STATE_A
    context = AS_OPERATED
    as_of = AS_OF
    sources = condition_sources()
    if case == "malformed_state":
        state = True
    elif case == "malformed_context":
        context = {"kind": "invented"}
    elif case == "naive_cutoff":
        as_of = datetime(2026, 8, 7, 20, 30)
    elif case == "non_tuple_sources":
        sources = object()
    elif case == "malformed_source":
        sources = ({"constraint_anchor_id": CON_A, "source": {}}, sources[1])
    else:
        sources = (sources[0].model_copy(update={"implicit": True}), sources[1])
    with pytest.raises(StateClassificationInputError) as error:
        queries.state_classification(
            state, context=context, as_of=as_of, condition_sources=sources)
    assert error.value.error_code == "STATE_CLASSIFICATION_INPUT_INVALID"
    assert calls == []


def test_every_branch_runs_once_in_canonical_order_with_fixed_forwarding(
        tmp_path, monkeypatch):
    model, registration, _ = state_model(tmp_path)
    queries = facade(tmp_path, model=model)
    original = queries.constraints.constraint_evaluation
    calls = []

    def observed(constraint_anchor_id, **kwargs):
        calls.append((constraint_anchor_id, kwargs))
        return original(constraint_anchor_id, **kwargs)

    monkeypatch.setattr(queries.constraints, "constraint_evaluation", observed)
    result = queries.state_classification(
        STATE_A, context=AS_OPERATED, as_of=AS_OF,
        condition_sources=condition_sources(reverse=True))
    assert [item[0] for item in calls] == [CON_A, CON_B]
    assert all(item[1]["as_of"] == AS_OF for item in calls)
    assert all(item[1]["entity_anchor_id"]
               == registration.subject_entity_anchor_id for item in calls)
    assert tuple(item[1]["source"] for item in calls) == tuple(
        row.source for row in result.condition_sources)


def test_all_branches_are_attempted_and_first_canonical_lower_error_propagates(
        tmp_path, monkeypatch):
    model, _, _ = state_model(tmp_path)
    queries = facade(tmp_path, model=model)
    calls = []
    first = RuntimeError("first canonical lower failure")
    second = LookupError("second canonical lower failure")

    def failing(constraint_anchor_id, **kwargs):
        calls.append(constraint_anchor_id)
        raise first if constraint_anchor_id == CON_A else second

    monkeypatch.setattr(queries.constraints, "constraint_evaluation", failing)
    with pytest.raises(RuntimeError) as caught:
        queries.state_classification(
            STATE_A, context=AS_OPERATED, as_of=AS_OF,
            condition_sources=condition_sources(reverse=True))
    assert caught.value is first
    assert calls == [CON_A, CON_B]


def test_substituted_source_target_is_structural_input_misuse(tmp_path):
    model, _, _ = state_model(tmp_path)
    first, second = condition_sources()
    retargeted = StateConditionSource(
        constraint_anchor_id=first.constraint_anchor_id,
        source=SourceSelector(
            subject=first.source.subject, property=second.source.property))
    # The source set is structurally exact, so CN is invoked. The public CN
    # result then remains authoritative for the explicitly requested locator;
    # ST never substitutes or discovers a different source.
    result = facade(tmp_path, model=model).state_classification(
        STATE_A, context=AS_OPERATED, as_of=AS_OF,
        condition_sources=(retargeted, second))
    assert result.condition_sources[0] == retargeted
    assert result.constraint_evaluations[0].semantic_compatibility \
        .value_compatibility.state.candidates[0].property == second.source.property
