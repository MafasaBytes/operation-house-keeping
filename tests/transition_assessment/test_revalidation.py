"""Authoritative, store-independent TA result reconstruction tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.transition_assessment import (
    DeclaredTransitionAssessmentResult,
    TransitionAssessmentInputError,
    assess_declared_transition_endpoints,
)

from tests.transition_assessment.helpers import build_world


def test_plain_request_and_result_round_trip_authoritatively(tmp_path):
    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    raw = result.model_dump(mode="python", warnings=False)
    rebuilt = DeclaredTransitionAssessmentResult.model_validate(raw)
    assert rebuilt == result
    assert rebuilt.request is not result.request


@pytest.mark.parametrize(
    "field,value",
    [
        ("declaration_admission", "not_admitted"),
        ("context_relation", "different"),
        ("model_revision_relation", "different"),
        ("cutoff_relation", "equal"),
        ("evidence_completeness", "not_evaluated"),
        ("execution", "not_executed"),
        ("conclusion", None),
    ],
)
def test_every_top_level_derived_partition_is_authoritative(
    tmp_path, field, value,
):
    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    raw = result.model_dump(mode="python", warnings=False)
    raw[field] = value
    with pytest.raises(ValidationError):
        DeclaredTransitionAssessmentResult.model_validate(raw)


def test_trace_endpoint_issue_and_boolean_forgeries_reject(tmp_path):
    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    base = result.model_dump(mode="python", warnings=False)
    mutations = []
    trace = result.model_dump(mode="python", warnings=False)
    trace["condition_traces"][0]["semantic_candidate_index"] = 1
    mutations.append(trace)
    endpoint = result.model_dump(mode="python", warnings=False)
    endpoint["from_endpoint"]["subject_relation"] = "different"
    mutations.append(endpoint)
    boolean = result.model_dump(mode="python", warnings=False)
    boolean["condition_traces"][0]["trace_index"] = True
    mutations.append(boolean)
    issues = result.model_dump(mode="python", warnings=False)
    issues["issues"] = [{
        "code": "cutoffs_equal", "endpoint_role": None,
        "condition_index": None, "evidence_alignment_index": None,
    }]
    mutations.append(issues)
    for raw in mutations:
        with pytest.raises((ValidationError, ValueError)):
            DeclaredTransitionAssessmentResult.model_validate(raw)
    assert base["execution"] == "executed"


def test_constructed_hidden_and_wrong_union_content_rejects_before_derivation(
    tmp_path,
):
    world = build_world(tmp_path)
    forged = world.request.model_copy()
    forged.__dict__["hidden_cache"] = "hostile"
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(forged)

    raw = world.request.model_dump(mode="python", warnings=False)
    raw["context"] = {"kind": "unknown_context"}
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)


def test_substituted_lower_private_material_binding_rejects(tmp_path):
    world = build_world(tmp_path)
    endpoint = (
        world.request.transition.effective_body_groups[0].from_endpoint
    )
    endpoint.__dict__["_material"] = object()
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(world.request)


def test_missing_duplicate_and_reordered_result_rows_reject(tmp_path):
    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    missing = result.model_dump(mode="python", warnings=False)
    missing["condition_traces"] = missing["condition_traces"][:-1]
    duplicate = result.model_dump(mode="python", warnings=False)
    duplicate["condition_traces"] = (
        *duplicate["condition_traces"], duplicate["condition_traces"][0],
    )
    reordered = result.model_dump(mode="python", warnings=False)
    reordered["condition_traces"] = tuple(
        reversed(reordered["condition_traces"]),
    )
    for raw in (missing, duplicate, reordered):
        with pytest.raises((ValidationError, ValueError)):
            DeclaredTransitionAssessmentResult.model_validate(raw)


def test_result_reconstruction_budgets_carried_request_once(
    tmp_path, monkeypatch,
):
    import backend.transition_assessment.contracts as contracts

    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    raw = result.model_dump(mode="python", warnings=False)
    original = contracts._preflight_graph
    traversed = []

    def recording(value, *args, **kwargs):
        if type(value) is dict:
            traversed.append(frozenset(value))
        return original(value, *args, **kwargs)

    monkeypatch.setattr(contracts, "_preflight_graph", recording)
    rebuilt = DeclaredTransitionAssessmentResult.model_validate(raw)
    assert rebuilt == result
    assert not any("request" in keys and "fixed_limits" in keys
                   for keys in traversed)
    assert sum("transition" in keys and "evidence_alignments" in keys
               for keys in traversed) == 1


def test_spoofed_backend_model_subclass_rejects_without_dispatch(
    tmp_path,
):
    world = build_world(tmp_path)
    calls = []
    policy_type = type(world.request.policy)

    class HostilePolicy(policy_type):
        __module__ = "backend.hostile"

        def __getattribute__(self, name):
            if name == "kind":
                calls.append(name)
            return super().__getattribute__(name)

    hostile = HostilePolicy.model_construct(
        **world.request.policy.model_dump(mode="python"),
    )
    calls.clear()
    raw = world.request.model_dump(mode="python", warnings=False)
    raw["policy"] = hostile
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)
    assert calls == []


def test_alignment_cardinality_rejects_before_lower_reconstruction(
    tmp_path, monkeypatch,
):
    import backend.transition_assessment.contracts as contracts

    raw = build_world(tmp_path).request.model_dump(mode="python", warnings=False)
    raw["evidence_alignments"] = [{} for _ in range(129)]
    calls = []

    def forbidden(*args, **kwargs):
        calls.append("lower validation")
        raise AssertionError("lower validation must not run")

    monkeypatch.setattr(
        contracts.OperationalEvidenceAlignmentResult,
        "model_validate",
        forbidden,
    )
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)
    assert calls == []


def test_request_runs_one_full_plain_copy_and_canonical_agreement_pass(
    tmp_path, monkeypatch,
):
    import backend.transition_assessment.contracts as contracts

    raw = build_world(tmp_path).request.model_dump(mode="python", warnings=False)
    plain_graph = contracts._plain_graph
    verify = contracts._verify_canonical_plain
    full_copies = []
    canonical_checks = []

    def recording_plain(value):
        if type(value) is dict and {
            "transition", "from_classification", "to_classification",
            "evidence_alignments",
        } <= set(value):
            full_copies.append(value)
        return plain_graph(value)

    def recording_verify(value, expected_size):
        canonical_checks.append((value, expected_size))
        return verify(value, expected_size)

    monkeypatch.setattr(contracts, "_plain_graph", recording_plain)
    monkeypatch.setattr(contracts, "_verify_canonical_plain", recording_verify)
    assert assess_declared_transition_endpoints(raw).execution == "executed"
    assert len(full_copies) == 1
    assert len(canonical_checks) == 1
