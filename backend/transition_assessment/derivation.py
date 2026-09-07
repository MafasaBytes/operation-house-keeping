"""Pure TA-001 endpoint-pattern derivation."""

from __future__ import annotations

from .contracts import (
    DeclaredTransitionAssessmentRequest,
    DeclaredTransitionAssessmentResult,
    _fixed_limits,
    TransitionAssessmentConditionTrace,
    TransitionAssessmentEndpointDisclosure,
    TransitionAssessmentInputError,
    TransitionAssessmentIssue,
    TransitionAssessmentIssueCode,
)


_ISSUE_ORDER = {
    code: index
    for index, code in enumerate((
        "transition_anchor_mismatch",
        "transition_not_registered",
        "transition_not_declared",
        "transition_conflicted",
        "transition_inactive",
        "context_mismatch",
        "model_revision_mismatch",
        "from_state_anchor_mismatch",
        "to_state_anchor_mismatch",
        "endpoint_subject_mismatch",
        "endpoint_pin_not_exact_current",
        "endpoint_classification_cutoff_mismatch",
        "cutoffs_equal",
        "cutoffs_reversed",
        "endpoint_classification_not_executed",
        "endpoint_classification_incomplete",
        "governing_selection_refused",
        "governing_expected_fingerprint_not_supplied",
        "governing_expected_fingerprint_not_evaluated",
        "governing_expected_fingerprint_mismatched",
        "governing_occurrence_not_aligned",
        "governing_evidence_incomplete",
    ))
}


def _issue(
    code: TransitionAssessmentIssueCode,
    role=None,
    condition_index=None,
    alignment_index=None,
) -> TransitionAssessmentIssue:
    return TransitionAssessmentIssue(
        code=code,
        endpoint_role=role,
        condition_index=condition_index,
        evidence_alignment_index=alignment_index,
    )


def _issue_sort_key(issue: TransitionAssessmentIssue):
    role = {None: -1, "from": 0, "to": 1}[issue.endpoint_role]
    return (
        _ISSUE_ORDER[issue.code],
        role,
        -1 if issue.condition_index is None else issue.condition_index,
        -1 if issue.evidence_alignment_index is None
        else issue.evidence_alignment_index,
    )


def _record_at(material, index):
    if type(index) is not int or not 0 <= index < len(material.records):
        raise ValueError("carried model index is invalid")
    return material.records[index]


def _transition_subject(transition):
    if transition.registration_index is None:
        return None
    registration = _record_at(
        transition.material, transition.registration_index,
    )
    return registration.subject_entity_anchor_id


def _classification_subject(classification):
    if classification.state.registration_index is None:
        return None
    registration = _record_at(
        classification.state.material,
        classification.state.registration_index,
    )
    return registration.subject_entity_anchor_id


def _endpoint_facts(request, role, group, transition_subject):
    classification = (
        request.from_classification if role == "from"
        else request.to_classification
    )
    cutoff = request.from_as_of if role == "from" else request.to_as_of
    endpoint = None if group is None else getattr(group, f"{role}_endpoint")
    declared_anchor = None if endpoint is None else endpoint.state_anchor_id
    anchor_relation = (
        "not_evaluated" if declared_anchor is None
        else "exact" if declared_anchor == classification.state_anchor_id
        else "different"
    )
    classified_subject = _classification_subject(classification)
    subject_relation = (
        "not_evaluated"
        if group is None
        or transition_subject is None
        or classified_subject is None
        else "exact" if transition_subject == classified_subject
        else "different"
    )
    return {
        "classification": classification,
        "cutoff": cutoff,
        "endpoint": endpoint,
        "declared_anchor": declared_anchor,
        "anchor_relation": anchor_relation,
        "subject_relation": subject_relation,
        "context_relation": (
            "exact" if classification.context == request.context
            else "different"
        ),
        "cutoff_relation": (
            "exact" if classification.as_of == cutoff else "different"
        ),
    }


def _candidate_path(classification, condition):
    evaluation_index = condition.constraint_evaluation_index
    evaluation = classification.constraint_evaluations[evaluation_index]
    if condition.candidate_index is None:
        return evaluation, None, None, None, None
    candidate_index = condition.candidate_index
    if not 0 <= candidate_index < len(evaluation.candidates):
        raise ValueError("constraint candidate index is invalid")
    candidate = evaluation.candidates[candidate_index]
    semantic_index = candidate.semantic_candidate_index
    semantic = evaluation.semantic_compatibility
    if semantic is None or not 0 <= semantic_index < len(semantic.candidates):
        raise ValueError("semantic candidate index is invalid")
    semantic_candidate = semantic.candidates[semantic_index]
    compatibility = semantic.value_compatibility
    value_matches = tuple(
        index for index, value_candidate in enumerate(compatibility.candidates)
        if value_candidate == semantic_candidate.value_candidate
    )
    if len(value_matches) != 1:
        raise ValueError("value candidate correspondence is not exact")
    value_index = value_matches[0]
    if value_index != semantic_index:
        raise ValueError("semantic and value candidate coordinates diverge")
    value_candidate = compatibility.candidates[value_index]
    return evaluation, semantic_index, value_index, compatibility, value_candidate


def _trace_work(request):
    pending = []
    distinct = []
    for role, classification in (
        ("from", request.from_classification),
        ("to", request.to_classification),
    ):
        for expected_index, condition in enumerate(classification.conditions):
            if condition.condition_index != expected_index:
                raise ValueError("condition indices are not canonical")
            evaluation, semantic_index, value_index, compatibility, candidate = (
                _candidate_path(classification, condition)
            )
            bound = None if candidate is None else candidate.state_candidate.bound
            alignment_index = None
            if bound is not None:
                matches = tuple(
                    index for index, item in enumerate(distinct)
                    if item == compatibility
                )
                if len(matches) > 1:
                    raise ValueError("duplicate compatibility join")
                if matches:
                    alignment_index = matches[0]
                else:
                    alignment_index = len(distinct)
                    distinct.append(compatibility)
            pending.append({
                "role": role,
                "condition": condition,
                "evaluation": evaluation,
                "semantic_index": semantic_index,
                "value_index": value_index,
                "candidate": candidate,
                "bound": bound,
                "alignment_index": alignment_index,
            })

    alignments = request.evidence_alignments
    if len(alignments) != len(distinct):
        raise ValueError("evidence alignment collection is not exact")
    for index, compatibility in enumerate(distinct):
        if alignments[index].request.compatibility != compatibility:
            raise ValueError("evidence alignment order or content is invalid")
    return pending


def _traces_and_issues(request):
    work = _trace_work(request)
    traces = []
    issues = []
    for trace_index, item in enumerate(work):
        role = item["role"]
        condition = item["condition"]
        alignment_index = item["alignment_index"]
        if item["bound"] is None:
            trace = TransitionAssessmentConditionTrace(
                trace_index=trace_index,
                endpoint_role=role,
                condition_index=condition.condition_index,
                constraint_evaluation_index=condition.constraint_evaluation_index,
                semantic_candidate_index=item["semantic_index"],
                value_candidate_index=item["value_index"],
                observation_presence="absent",
                evidence_alignment_index=None,
                alignment_relation="not_applicable",
                evidence_selection_status="not_applicable",
                evidence_completeness="not_applicable",
                expected_fingerprint_relation="not_applicable",
                selected_occurrence_role="not_applicable",
                source_time_use="not_applicable",
            )
        else:
            alignment = request.evidence_alignments[alignment_index]
            if alignment.aligned_candidate_index is not None and (
                alignment.aligned_candidate_index != item["value_index"]
            ):
                raise ValueError("alignment candidate coordinate is invalid")
            trace = TransitionAssessmentConditionTrace(
                trace_index=trace_index,
                endpoint_role=role,
                condition_index=condition.condition_index,
                constraint_evaluation_index=condition.constraint_evaluation_index,
                semantic_candidate_index=item["semantic_index"],
                value_candidate_index=item["value_index"],
                observation_presence="present",
                evidence_alignment_index=alignment_index,
                alignment_relation=alignment.status,
                evidence_selection_status=alignment.evidence_selection_status,
                evidence_completeness=alignment.evidence_coverage_completeness,
                expected_fingerprint_relation=(
                    alignment.expected_fingerprint_relation
                ),
                selected_occurrence_role=alignment.selected_occurrence_role,
                source_time_use="disclosure_only",
            )
            if alignment.evidence_selection_status == "refused":
                issues.append(_issue(
                    "governing_selection_refused", role,
                    condition.condition_index, alignment_index,
                ))
            fingerprint_code = {
                "not_supplied": "governing_expected_fingerprint_not_supplied",
                "not_evaluated": "governing_expected_fingerprint_not_evaluated",
                "mismatched": "governing_expected_fingerprint_mismatched",
            }.get(alignment.expected_fingerprint_relation)
            if fingerprint_code is not None:
                issues.append(_issue(
                    fingerprint_code, role, condition.condition_index,
                    alignment_index,
                ))
            if alignment.status == "not_aligned":
                issues.append(_issue(
                    "governing_occurrence_not_aligned", role,
                    condition.condition_index, alignment_index,
                ))
            if (
                alignment.status == "aligned_with_incomplete_evidence"
                or alignment.evidence_coverage_completeness
                == "incomplete_within_declared_horizon"
            ):
                issues.append(_issue(
                    "governing_evidence_incomplete", role,
                    condition.condition_index, alignment_index,
                ))
        traces.append(trace)
    return tuple(traces), issues


def _evidence_completeness(request, traces):
    classifications = (
        request.from_classification, request.to_classification,
    )
    if any(
        item.condition_coverage == "not_evaluated"
        for item in classifications
    ) or any(trace.evidence_selection_status == "refused" for trace in traces):
        return "not_evaluated"
    if any(item.condition_coverage == "incomplete" for item in classifications) or any(
        trace.alignment_relation == "aligned_with_incomplete_evidence"
        or trace.evidence_completeness
        == "incomplete_within_declared_horizon"
        for trace in traces
    ):
        return "incomplete_within_one_or_more_declared_horizons"
    return "complete_within_all_declared_horizons"


def _derive_result_fields(request: DeclaredTransitionAssessmentRequest) -> dict:
    transition = request.transition
    group = (
        transition.effective_body_groups[0]
        if len(transition.effective_body_groups) == 1 else None
    )
    transition_subject = _transition_subject(transition)
    endpoint_facts = {
        role: _endpoint_facts(request, role, group, transition_subject)
        for role in ("from", "to")
    }
    context_relation = (
        "exact"
        if transition.context == request.context
        and all(item["context_relation"] == "exact"
                for item in endpoint_facts.values())
        else "different"
    )
    revisions = (
        transition.material.revision,
        request.from_classification.state.material.revision,
        request.to_classification.state.material.revision,
    )
    model_revision_relation = (
        "exact" if revisions[0] == revisions[1] == revisions[2]
        else "different"
    )
    cutoff_relation = (
        "ordered_earlier_to_later"
        if request.from_as_of < request.to_as_of
        else "equal" if request.from_as_of == request.to_as_of
        else "reversed"
    )

    traces, issues = _traces_and_issues(request)
    if transition.transition_anchor_id != request.transition_anchor_id:
        issues.append(_issue("transition_anchor_mismatch"))
    lifecycle_code = {
        "not_registered": "transition_not_registered",
        "not_declared": "transition_not_declared",
        "conflicted": "transition_conflicted",
        "inactive": "transition_inactive",
    }.get(transition.conclusion)
    if lifecycle_code is not None:
        issues.append(_issue(lifecycle_code))
    if context_relation == "different":
        issues.append(_issue("context_mismatch"))
    if model_revision_relation == "different":
        issues.append(_issue("model_revision_mismatch"))

    disclosures = {}
    for role in ("from", "to"):
        facts = endpoint_facts[role]
        classification = facts["classification"]
        endpoint = facts["endpoint"]
        if facts["anchor_relation"] == "different":
            issues.append(_issue(f"{role}_state_anchor_mismatch", role))
        if facts["subject_relation"] == "different":
            issues.append(_issue("endpoint_subject_mismatch", role))
        pin_alignment = None if endpoint is None else endpoint.alignment
        if pin_alignment is not None and pin_alignment != "exact_current":
            issues.append(_issue("endpoint_pin_not_exact_current", role))
        if facts["cutoff_relation"] == "different":
            issues.append(_issue(
                "endpoint_classification_cutoff_mismatch", role,
            ))
        if classification.execution != "executed":
            issues.append(_issue(
                "endpoint_classification_not_executed", role,
            ))
        if classification.condition_coverage != "complete":
            issues.append(_issue(
                "endpoint_classification_incomplete", role,
            ))
        trace_indices = tuple(
            trace.trace_index for trace in traces if trace.endpoint_role == role
        )
        disclosures[role] = TransitionAssessmentEndpointDisclosure(
            role=role,
            declared_state_anchor_id=facts["declared_anchor"],
            classified_state_anchor_id=classification.state_anchor_id,
            state_anchor_relation=facts["anchor_relation"],
            subject_relation=facts["subject_relation"],
            pin_alignment=pin_alignment,
            classification_context_relation=facts["context_relation"],
            classification_cutoff_relation=facts["cutoff_relation"],
            state_declaration_conclusion=classification.state.conclusion,
            condition_coverage=classification.condition_coverage,
            classification_execution=classification.execution,
            computed_match=classification.computed_match,
            condition_trace_indices=trace_indices,
        )

    if cutoff_relation == "equal":
        issues.append(_issue("cutoffs_equal"))
    elif cutoff_relation == "reversed":
        issues.append(_issue("cutoffs_reversed"))

    declaration_admission = (
        "admitted"
        if transition.transition_anchor_id == request.transition_anchor_id
        and transition.conclusion == "declared"
        and transition.lineage_summary == "healthy"
        and group is not None
        and context_relation == "exact"
        and model_revision_relation == "exact"
        and all(
            facts["anchor_relation"] == "exact"
            and facts["subject_relation"] == "exact"
            and facts["cutoff_relation"] == "exact"
            and facts["endpoint"] is not None
            and facts["endpoint"].alignment == "exact_current"
            for facts in endpoint_facts.values()
        )
        else "not_admitted"
    )
    evidence_completeness = _evidence_completeness(request, traces)
    evidence_gate = all(
        trace.observation_presence == "present"
        and trace.alignment_relation == "aligned_with_complete_evidence"
        and trace.evidence_selection_status == "complete_within_declared_horizon"
        and trace.evidence_completeness == "complete_within_declared_horizon"
        and trace.expected_fingerprint_relation == "matched"
        for trace in traces
    )
    classification_gate = all(
        facts["classification"].execution == "executed"
        and facts["classification"].condition_coverage == "complete"
        for facts in endpoint_facts.values()
    )
    execution = (
        "executed"
        if declaration_admission == "admitted"
        and cutoff_relation == "ordered_earlier_to_later"
        and classification_gate
        and evidence_completeness == "complete_within_all_declared_horizons"
        and evidence_gate
        else "not_executed"
    )
    conclusion = None
    if execution == "executed":
        conclusion = (
            "bounded_evidence_supports_declared_endpoint_pattern"
            if request.from_classification.computed_match == "matches"
            and request.to_classification.computed_match == "matches"
            else "bounded_evidence_does_not_support_declared_endpoint_pattern"
        )

    return {
        "ruleset_version": "ta001.1",
        "fixed_limits": _fixed_limits(),
        "declaration_admission": declaration_admission,
        "context_relation": context_relation,
        "model_revision_relation": model_revision_relation,
        "cutoff_relation": cutoff_relation,
        "from_endpoint": disclosures["from"],
        "to_endpoint": disclosures["to"],
        "condition_traces": traces,
        "evidence_completeness": evidence_completeness,
        "source_time_use": "disclosure_only_not_compared",
        "temporal_cohort": (
            "independent_latest_per_condition_not_a_temporal_cohort"
        ),
        "continuity": "not_assessed",
        "execution": execution,
        "issues": tuple(sorted(issues, key=_issue_sort_key)),
        "conclusion": conclusion,
    }


def assess_declared_transition_endpoints(
    request: DeclaredTransitionAssessmentRequest,
) -> DeclaredTransitionAssessmentResult:
    failure = None
    try:
        rebuilt = DeclaredTransitionAssessmentRequest.model_validate(request)
        fields = _derive_result_fields(rebuilt)
        return DeclaredTransitionAssessmentResult.model_construct(
            schema_version="1", request=rebuilt, **fields,
        )
    except TransitionAssessmentInputError:
        raise
    except Exception:
        failure = TransitionAssessmentInputError(
            "TRANSITION_ASSESSMENT_INPUT_INVALID",
            "transition assessment request is invalid",
        )
    raise failure
