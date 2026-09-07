"""Direct TA-001 Slice B lifecycle, gate, and issue witnesses."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from backend.evidence_alignment import (
    OperationalEvidenceAlignmentRequest,
    align_operational_evidence_with_value_compatibility,
)
from backend.evidence_assurance import (
    EvidenceAssuranceQueries,
    OperationalEvidenceIssue,
    OperationalEvidenceSelectionResult,
)
from backend.model_kernel import ModelQueries
from backend.transition_assessment import (
    DeclaredTransitionAssessmentRequest,
    assess_declared_transition_endpoints,
)

from tests.data_sources.test_ea001_operational_evidence_reader import _scope
from tests.evidence_assurance.test_selection import (
    HORIZON,
    _request as evidence_request,
)
from tests.model_kernel.builders import ENT_C, registration as entity_registration
from tests.model_kernel.st001_slice_a_helpers import (
    AS_DESIGNED,
    STATE_A,
    state_declaration,
    state_withdrawal,
)
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    T1,
    TRANSITION_A,
    TRANSITION_B,
    transition_declaration,
    transition_withdrawal,
)
from tests.transition_assessment.helpers import build_world


def _request(request, **updates):
    raw = request.model_dump(mode="python", warnings=False)
    raw.update(updates)
    return DeclaredTransitionAssessmentRequest.model_validate(raw)


def _records(store, kind):
    return tuple(
        record for record in store.load().records.values()
        if record.record_kind == kind
    )


def _transition_parts(store):
    root = _records(store, "transition_declaration")[0]
    registration = _records(store, "transition_registration")[0]
    states = {
        item.anchor.anchor_id: item
        for item in _records(store, "state_registration")
    }
    declarations = {
        item.record_id: item
        for item in _records(store, "state_declaration")
    }
    return (
        root,
        registration,
        states[root.from_endpoint.state_anchor_id],
        states[root.to_endpoint.state_anchor_id],
        declarations[root.from_endpoint.declaration_record_id],
        declarations[root.to_endpoint.declaration_record_id],
    )


def _same_root_fork(store):
    root, registration, from_reg, to_reg, from_dec, to_dec = (
        _transition_parts(store)
    )
    for offset, note in ((0, "left"), (1, "right")):
        store.append(transition_declaration(
            registration,
            from_registration=from_reg,
            to_registration=to_reg,
            from_declaration=from_dec,
            to_declaration=to_dec,
            supersedes=(root.record_id,),
            recorded_at=T1 + timedelta(seconds=offset),
            note=note,
        ))


def _cross_root_disagreement(store):
    _, registration, from_reg, to_reg, from_dec, to_dec = (
        _transition_parts(store)
    )
    successor = state_declaration(
        from_reg,
        state_anchor_id=from_reg.anchor.anchor_id,
        supersedes=(from_dec.record_id,),
        recorded_at=T1,
        note="new exact from pin",
    )
    store.append(successor)
    store.append(transition_declaration(
        registration,
        from_registration=from_reg,
        to_registration=to_reg,
        from_declaration=successor,
        to_declaration=to_dec,
        recorded_at=T1 + timedelta(seconds=1),
        note="different independent body",
    ))


def _inactive_transition(store):
    root = _records(store, "transition_declaration")[0]
    store.append(transition_withdrawal(root))


def _superseded_from_pin(store):
    _, _, from_reg, _, from_dec, _ = _transition_parts(store)
    store.append(state_declaration(
        from_reg,
        state_anchor_id=from_reg.anchor.anchor_id,
        supersedes=(from_dec.record_id,),
        recorded_at=T1,
        note="supersede pinned from declaration",
    ))


def _withdrawn_from_pin_with_peer(store):
    _, _, from_reg, _, from_dec, _ = _transition_parts(store)
    store.append(state_declaration(
        from_reg,
        state_anchor_id=from_reg.anchor.anchor_id,
        recorded_at=T1,
        note="surviving peer root",
    ))
    store.append(state_withdrawal(
        from_dec,
        recorded_at=T1 + timedelta(seconds=1),
        note="withdraw pinned from declaration",
    ))


def _inactive_from_state(store):
    _, _, _, _, from_dec, _ = _transition_parts(store)
    store.append(state_withdrawal(from_dec, recorded_at=T1))


@pytest.mark.parametrize(
    "from_upper,to_upper,expected",
    [
        ("80", "80", ("matches", "matches")),
        ("50", "80", ("does_not_match", "matches")),
        ("80", "50", ("matches", "does_not_match")),
        ("50", "50", ("does_not_match", "does_not_match")),
    ],
)
def test_t01_t03_all_endpoint_conclusion_quadrants(
    tmp_path, from_upper, to_upper, expected,
):
    world = build_world(
        tmp_path, from_upper=from_upper, to_upper=to_upper,
    )
    result = assess_declared_transition_endpoints(world.request)
    assert (
        result.from_endpoint.computed_match,
        result.to_endpoint.computed_match,
    ) == expected
    assert result.execution == "executed"
    assert result.conclusion == (
        "bounded_evidence_supports_declared_endpoint_pattern"
        if expected == ("matches", "matches")
        else "bounded_evidence_does_not_support_declared_endpoint_pattern"
    )


def test_t04_unregistered_transition_maps_to_structured_issue(tmp_path):
    world = build_world(tmp_path)
    transition = ModelQueries(world.model.load()).transition_declaration(
        TRANSITION_B, context=AS_OPERATED,
    )
    result = assess_declared_transition_endpoints(_request(
        world.request,
        transition_anchor_id=TRANSITION_B,
        transition=transition,
    ))
    assert result.declaration_admission == "not_admitted"
    assert result.execution == "not_executed"
    assert "transition_not_registered" in tuple(
        issue.code for issue in result.issues
    )


@pytest.mark.parametrize(
    "declare_transition,mutator,expected_code",
    [
        (False, None, "transition_not_declared"),
        (True, _same_root_fork, "transition_conflicted"),
        (True, _cross_root_disagreement, "transition_conflicted"),
        (True, _inactive_transition, "transition_inactive"),
        (True, _superseded_from_pin, "endpoint_pin_not_exact_current"),
        (True, _withdrawn_from_pin_with_peer, "endpoint_pin_not_exact_current"),
        (True, _inactive_from_state, "endpoint_pin_not_exact_current"),
    ],
)
def test_t05_t11_lifecycle_and_pin_cells_map_directly(
    tmp_path, declare_transition, mutator, expected_code,
):
    world = build_world(
        tmp_path,
        declare_transition=declare_transition,
        model_mutator=mutator,
    )
    result = assess_declared_transition_endpoints(world.request)
    assert result.execution == "not_executed"
    assert result.conclusion is None
    assert expected_code in tuple(issue.code for issue in result.issues)
    if mutator is _inactive_from_state:
        assert result.from_endpoint.pin_alignment == "endpoint_state_inactive"
        assert {
            "endpoint_classification_not_executed",
            "endpoint_classification_incomplete",
        } <= {issue.code for issue in result.issues}


def test_t12_t18_anchor_context_and_valid_substitution_are_structured(tmp_path):
    world = build_world(tmp_path)
    anchor = assess_declared_transition_endpoints(_request(
        world.request, transition_anchor_id=TRANSITION_B,
    ))
    assert tuple(issue.code for issue in anchor.issues)[0] == (
        "transition_anchor_mismatch"
    )

    context = assess_declared_transition_endpoints(_request(
        world.request, context=AS_DESIGNED,
    ))
    assert context.context_relation == "different"
    assert "context_mismatch" in tuple(issue.code for issue in context.issues)

    foreign = ModelQueries(world.model.load()).transition_declaration(
        TRANSITION_B, context=AS_OPERATED,
    )
    substituted = assess_declared_transition_endpoints(_request(
        world.request, transition=foreign,
    ))
    assert tuple(issue.code for issue in substituted.issues)[:2] == (
        "transition_anchor_mismatch", "transition_not_registered",
    )


def test_t13_t14_wrong_endpoint_states_are_role_specific(tmp_path):
    world = build_world(tmp_path)
    from_wrong = assess_declared_transition_endpoints(_request(
        world.request, from_classification=world.request.to_classification,
        from_as_of=world.request.to_as_of,
        to_as_of=world.request.to_as_of + timedelta(minutes=1),
        evidence_alignments=(world.request.evidence_alignments[1],),
    ))
    assert any(
        issue.code == "from_state_anchor_mismatch"
        and issue.endpoint_role == "from"
        for issue in from_wrong.issues
    )

    to_wrong = assess_declared_transition_endpoints(_request(
        world.request, to_classification=world.request.from_classification,
        to_as_of=world.request.from_as_of,
        evidence_alignments=(world.request.evidence_alignments[0],),
    ))
    assert any(
        issue.code == "to_state_anchor_mismatch"
        and issue.endpoint_role == "to"
        for issue in to_wrong.issues
    )


def test_t19_t20_cutoff_relations_do_not_rewrite_admission(tmp_path):
    world = build_world(tmp_path)
    for to_as_of, relation, code in (
        (world.request.from_as_of, "equal", "cutoffs_equal"),
        (
            world.request.from_as_of - timedelta(seconds=1),
            "reversed",
            "cutoffs_reversed",
        ),
    ):
        result = assess_declared_transition_endpoints(_request(
            world.request, to_as_of=to_as_of,
        ))
        assert result.declaration_admission == "not_admitted"
        assert result.cutoff_relation == relation
        assert code in tuple(issue.code for issue in result.issues)
        assert result.execution == "not_executed"


def test_t23_endpoint_cutoff_mismatch_is_role_specific(tmp_path):
    world = build_world(tmp_path)
    result = assess_declared_transition_endpoints(_request(
        world.request,
        from_as_of=world.request.from_as_of + timedelta(seconds=1),
    ))
    assert any(
        issue.code == "endpoint_classification_cutoff_mismatch"
        and issue.endpoint_role == "from"
        for issue in result.issues
    )


def test_t24_complete_model_revision_difference_is_structured(tmp_path):
    world = build_world(tmp_path)
    world.model.append(entity_registration(ENT_C))
    later_transition = ModelQueries(world.model.load()).transition_declaration(
        TRANSITION_A, context=AS_OPERATED,
    )
    result = assess_declared_transition_endpoints(_request(
        world.request, transition=later_transition,
    ))
    assert result.model_revision_relation == "different"
    assert "model_revision_mismatch" in tuple(
        issue.code for issue in result.issues
    )
    assert result.execution == "not_executed"


def test_t25_t28_incomplete_classification_maps_both_endpoint_roles(tmp_path):
    from tests.model_state.helpers import BEFORE_RECEIPT

    world = build_world(
        tmp_path,
        from_as_of=BEFORE_RECEIPT,
        to_as_of=BEFORE_RECEIPT + timedelta(minutes=1),
    )
    result = assess_declared_transition_endpoints(world.request)
    pairs = {(issue.code, issue.endpoint_role) for issue in result.issues}
    for role in ("from", "to"):
        assert ("endpoint_classification_not_executed", role) in pairs
        assert ("endpoint_classification_incomplete", role) in pairs
    assert result.evidence_completeness == (
        "incomplete_within_one_or_more_declared_horizons"
    )
    assert result.conclusion is None


def _alignment_with(selection, compatibility, expected):
    return align_operational_evidence_with_value_compatibility(
        OperationalEvidenceAlignmentRequest(
            schema_version="1",
            selection=selection,
            compatibility=compatibility,
            expected_snapshot_fingerprint=expected,
        )
    )


def _replace_first_alignment(world, alignment):
    return _request(
        world.request,
        evidence_alignments=(alignment, *world.request.evidence_alignments[1:]),
    )


def test_t35_t37_refusal_and_fingerprint_issues_are_both_retained(tmp_path):
    world = build_world(tmp_path)
    original = world.request.evidence_alignments[0]
    refused = OperationalEvidenceSelectionResult(
        status="refused",
        request=original.request.selection.request,
        snapshot=None,
        issues=(OperationalEvidenceIssue(
            code="invalid_bounded_material",
            detail_code="test_refusal",
            route_index=None,
            detail="test refusal is structured",
        ),),
    )
    alignment = _alignment_with(
        refused,
        original.request.compatibility,
        original.request.selection.snapshot.content_fingerprint,
    )
    result = assess_declared_transition_endpoints(
        _replace_first_alignment(world, alignment),
    )
    codes = tuple(issue.code for issue in result.issues)
    assert codes.index("governing_selection_refused") < codes.index(
        "governing_expected_fingerprint_not_evaluated"
    )
    assert result.evidence_completeness == "not_evaluated"
    assert result.execution == "not_executed"


def test_t38_mismatched_fingerprint_preserves_complete_evidence(tmp_path):
    world = build_world(tmp_path)
    original = world.request.evidence_alignments[0]
    mismatch = _alignment_with(
        original.request.selection,
        original.request.compatibility,
        "sha256:" + "0" * 64,
    )
    result = assess_declared_transition_endpoints(
        _replace_first_alignment(world, mismatch),
    )
    assert result.condition_traces[0].expected_fingerprint_relation == (
        "mismatched"
    )
    assert result.evidence_completeness == (
        "complete_within_all_declared_horizons"
    )
    assert "governing_expected_fingerprint_mismatched" in tuple(
        issue.code for issue in result.issues
    )
    assert result.execution == "not_executed"


def test_t41_incomplete_seed_alignment_remains_incomplete(tmp_path):
    world = build_world(tmp_path)
    original = world.request.evidence_alignments[0]
    snapshot = original.request.selection.snapshot
    selected = snapshot.temporal_material.occurrence_membership[
        snapshot.selected.temporal_occurrence_index
    ]
    selection = EvidenceAssuranceQueries(
        source=world.source, temporal=world.temporal,
    ).select_operational_evidence(evidence_request(
        start=selected.received_at + timedelta(minutes=1),
        end=original.request.compatibility.as_of,
    ))
    assert selection.snapshot is not None
    incomplete = _alignment_with(
        selection,
        original.request.compatibility,
        selection.snapshot.content_fingerprint,
    )
    result = assess_declared_transition_endpoints(
        _replace_first_alignment(world, incomplete),
    )
    assert result.condition_traces[0].alignment_relation == (
        "aligned_with_incomplete_evidence"
    )
    assert result.condition_traces[0].selected_occurrence_role == (
        "pre_horizon_seed"
    )
    assert result.evidence_completeness == (
        "incomplete_within_one_or_more_declared_horizons"
    )
    assert "governing_evidence_incomplete" in tuple(
        issue.code for issue in result.issues
    )


def test_t42_valid_not_aligned_lower_result_maps_without_reselection(tmp_path):
    world = build_world(tmp_path)
    original = world.request.evidence_alignments[0]
    selection = EvidenceAssuranceQueries(
        source=world.source, temporal=world.temporal,
    ).select_operational_evidence(evidence_request(
        scope=_scope(json_pointer="/result/status/extruder/not_present"),
        start=HORIZON,
        end=original.request.compatibility.as_of,
    ))
    assert selection.snapshot is not None
    not_aligned = _alignment_with(
        selection,
        original.request.compatibility,
        selection.snapshot.content_fingerprint,
    )
    assert not_aligned.status == "not_aligned"
    result = assess_declared_transition_endpoints(
        _replace_first_alignment(world, not_aligned),
    )
    assert result.condition_traces[0].alignment_relation == "not_aligned"
    assert "governing_occurrence_not_aligned" in tuple(
        issue.code for issue in result.issues
    )
    assert result.execution == "not_executed"


def test_t61_t62_public_results_use_only_bounded_pattern_language(tmp_path):
    positive = assess_declared_transition_endpoints(
        build_world(tmp_path / "positive").request,
    )
    negative = assess_declared_transition_endpoints(
        build_world(
            tmp_path / "negative", from_upper="50", to_upper="80",
        ).request,
    )
    text = "\n".join((
        positive.model_dump_json(),
        negative.model_dump_json(),
        Path("backend/transition_assessment/README.md").read_text(
            encoding="utf-8",
        ),
    )).lower()
    assert "bounded_evidence_supports_declared_endpoint_pattern" in text
    assert "bounded_evidence_does_not_support_declared_endpoint_pattern" in text
    for forbidden in (
        "transition_occurred",
        "transition_did_not_occur",
        "transition occurrence established",
        "transition non-occurrence established",
        "causal conclusion",
        "safety conclusion",
        "confidence score",
        "probability score",
    ):
        assert forbidden not in text
