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


def test_rejected_hidden_model_key_never_invokes_caller_representation(tmp_path):
    world = build_world(tmp_path)
    raw = world.request.model_dump(mode="python", warnings=False)
    policy = world.request.policy.model_copy()
    calls = []

    class HiddenKey:
        def __hash__(self):
            return 7

        def __repr__(self):
            calls.append("repr")
            raise AssertionError("caller representation was invoked")

    policy.__dict__[HiddenKey()] = "hidden"
    raw["policy"] = policy
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)
    assert calls == []

    ordinary = world.request.policy.model_copy()
    ordinary.__dict__["hidden_cache"] = "hidden"
    raw["policy"] = ordinary
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)


@pytest.mark.parametrize("attribute", ["__pydantic_extra__", "__pydantic_private__"])
def test_rejected_model_metadata_never_invokes_caller_truthiness(
    tmp_path, attribute,
):
    world = build_world(tmp_path)
    raw = world.request.model_dump(mode="python", warnings=False)
    policy = world.request.policy.model_copy()
    calls = []

    class HostileMetadata:
        def __bool__(self):
            calls.append("bool")
            raise AssertionError("caller truthiness was invoked")

    object.__setattr__(policy, attribute, HostileMetadata())
    raw["policy"] = policy
    with pytest.raises(TransitionAssessmentInputError):
        assess_declared_transition_endpoints(raw)
    assert calls == []


def test_request_reconstructs_each_expensive_lower_result_once(
    tmp_path, monkeypatch,
):
    import backend.evidence_alignment.derivation as alignment_derivation
    import backend.state_classification.derivation as state_derivation

    raw = build_world(tmp_path).request.model_dump(mode="python", warnings=False)
    state_original = state_derivation.derive_classification
    alignment_original = alignment_derivation._derive_alignment_fields
    state_calls = []
    alignment_calls = []

    def state_counted(*args, **kwargs):
        state_calls.append(1)
        return state_original(*args, **kwargs)

    def alignment_counted(*args, **kwargs):
        alignment_calls.append(1)
        return alignment_original(*args, **kwargs)

    monkeypatch.setattr(state_derivation, "derive_classification", state_counted)
    monkeypatch.setattr(
        alignment_derivation, "_derive_alignment_fields", alignment_counted,
    )
    assert assess_declared_transition_endpoints(raw).execution == "executed"
    assert len(state_calls) == 2
    assert len(alignment_calls) == 2


def test_compact_result_cycle_rejects_before_carried_request_reconstruction(
    tmp_path, monkeypatch,
):
    import backend.state_classification.derivation as state_derivation

    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    raw = result.model_dump(mode="python", warnings=False)
    cycle = []
    cycle.append(cycle)
    raw["issues"] = cycle
    calls = []
    original = state_derivation.derive_classification

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(state_derivation, "derive_classification", counted)
    with pytest.raises((ValidationError, ValueError)):
        DeclaredTransitionAssessmentResult.model_validate(raw)
    assert calls == []


def test_t50_every_public_model_level_rejects_hidden_missing_and_private_state(
    tmp_path,
):
    world = build_world(tmp_path)
    result = assess_declared_transition_endpoints(world.request)
    issue_result = assess_declared_transition_endpoints(
        type(world.request).model_validate({
            **world.request.model_dump(mode="python", warnings=False),
            "to_as_of": world.request.from_as_of,
        }),
    )
    instances = (
        world.request.policy,
        result.fixed_limits,
        world.request,
        issue_result.issues[0],
        result.condition_traces[0],
        result.from_endpoint,
        result,
    )
    for instance in instances:
        contract = type(instance)

        hidden = instance.model_copy()
        hidden.__dict__["hidden_cache"] = "forged"
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(hidden)

        extra = instance.model_copy()
        object.__setattr__(extra, "__pydantic_extra__", {"forged": True})
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(extra)

        private = instance.model_copy()
        object.__setattr__(private, "__pydantic_private__", {"forged": True})
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(private)

        plain = instance.model_dump(mode="python", warnings=False)
        plain.pop(next(iter(contract.model_fields)))
        missing = contract.model_construct(**plain)
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(missing)


def test_t53_t54_every_compact_result_partition_is_authoritative(tmp_path):
    result = assess_declared_transition_endpoints(build_world(tmp_path).request)

    def rejected(update):
        raw = result.model_dump(mode="python", warnings=False)
        update(raw)
        with pytest.raises((ValidationError, ValueError)):
            DeclaredTransitionAssessmentResult.model_validate(raw)

    top_level_updates = (
        lambda raw: raw.__setitem__("ruleset_version", "ta001.2"),
        lambda raw: raw["fixed_limits"].__setitem__(
            "maximum_nesting_depth", 127,
        ),
        lambda raw: raw.__setitem__("source_time_use", "not_evaluated"),
        lambda raw: raw.__setitem__("temporal_cohort", "asserted"),
        lambda raw: raw.__setitem__("continuity", "continuous"),
        lambda raw: raw["from_endpoint"].__setitem__("role", "to"),
        lambda raw: raw["to_endpoint"].__setitem__("role", "from"),
        lambda raw: raw["condition_traces"][0].__setitem__(
            "observation_presence", "absent",
        ),
        lambda raw: raw.__setitem__("issues", ({
            "code": "cutoffs_equal",
            "endpoint_role": None,
            "condition_index": None,
            "evidence_alignment_index": None,
        },)),
    )
    for update in top_level_updates:
        rejected(update)

    endpoint_values = {
        "declared_state_anchor_id": result.to_endpoint.declared_state_anchor_id,
        "classified_state_anchor_id": result.to_endpoint.classified_state_anchor_id,
        "state_anchor_relation": "different",
        "subject_relation": "different",
        "pin_alignment": "not_current",
        "classification_context_relation": "different",
        "classification_cutoff_relation": "different",
        "state_declaration_conclusion": "inactive",
        "condition_coverage": "incomplete",
        "classification_execution": "not_executed",
        "computed_match": "does_not_match",
        "condition_trace_indices": (),
    }
    for field, value in endpoint_values.items():
        rejected(lambda raw, field=field, value=value: raw[
            "from_endpoint"
        ].__setitem__(field, value))

    trace_values = {
        "trace_index": 1,
        "endpoint_role": "to",
        "condition_index": 1,
        "constraint_evaluation_index": 1,
        "semantic_candidate_index": None,
        "value_candidate_index": None,
        "observation_presence": "absent",
        "evidence_alignment_index": None,
        "alignment_relation": "not_aligned",
        "evidence_selection_status": "refused",
        "evidence_completeness": "incomplete_within_declared_horizon",
        "expected_fingerprint_relation": "mismatched",
        "selected_occurrence_role": "pre_horizon_seed",
        "source_time_use": "not_applicable",
    }
    for field, value in trace_values.items():
        rejected(lambda raw, field=field, value=value: raw[
            "condition_traces"
        ][0].__setitem__(field, value))
