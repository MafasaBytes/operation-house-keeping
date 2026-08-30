"""Single store-independent authoritative ST-001 classification derivation."""

from backend.model_kernel import ModelQueries, StateDeclaration


_REFUSAL_ORDER = (
    "state_not_registered",
    "state_not_declared",
    "state_inactive",
    "state_conflicted",
    "condition_not_registered",
    "condition_declaration_not_declared",
    "condition_declaration_conflicted",
    "condition_declaration_superseded",
    "condition_evaluation_not_evaluated",
)
_REFUSAL_RANK = {reason: index for index, reason in enumerate(_REFUSAL_ORDER)}


def _state_refusal(conclusion):
    return {
        "not_registered": "state_not_registered",
        "not_declared": "state_not_declared",
        "inactive": "state_inactive",
        "conflicted": "state_conflicted",
        "declared": None,
    }[conclusion]


def _active_pin_ids(state):
    """Return the unique admitted effective body's exact VCN pins."""
    if state.conclusion != "declared":
        return None
    if len(state.effective_body_groups) != 1:
        raise ValueError("declared state must carry one effective-body group")
    group = state.effective_body_groups[0]
    declaration = group.representative_declaration
    if not isinstance(declaration, StateDeclaration):
        raise ValueError("effective-body representative is not an STD record")
    return {
        condition.constraint_anchor_id:
            condition.constraint_declaration_record_id
        for condition in declaration.conditions
    }


def _condition_facts(evaluation, pinned_id, state_admitted):
    declaration = evaluation.constraint
    candidate_index = None
    if declaration.status != "not_registered":
        if len(evaluation.candidates) != 1:
            raise ValueError(
                "an explicit registered condition must carry one candidate")
        candidate_index = 0

    if not state_admitted:
        return candidate_index, "not_evaluated", "not_evaluated", None
    if declaration.status == "not_registered":
        return candidate_index, "not_registered", "not_evaluated", (
            "condition_not_registered")
    if declaration.status == "not_declared":
        return candidate_index, "not_declared", "not_evaluated", (
            "condition_declaration_not_declared")
    if declaration.status == "conflicted":
        # CN-001 defines every multiple-current-tip world as conflict. ST does
        # not compare or merge current VCN engineering bodies.
        return candidate_index, "conflicted", "not_evaluated", (
            "condition_declaration_conflicted")
    if declaration.declaration.record_id != pinned_id:
        return candidate_index, "superseded", "not_evaluated", (
            "condition_declaration_superseded")

    verdict = evaluation.candidates[candidate_index].verdict
    if verdict == "not_evaluated":
        return candidate_index, "exact_current", "not_evaluated", (
            "condition_evaluation_not_evaluated")
    return candidate_index, "exact_current", verdict, None


def derive_classification(*, state, state_anchor_id, context, as_of,
                          condition_sources, constraint_evaluations):
    """Recompute every ST-derived field from carried public lower results."""
    if state.state_anchor_id != state_anchor_id or state.context != context:
        raise ValueError("classification request echo is incoherent")
    source_ids = tuple(item.constraint_anchor_id for item in condition_sources)
    if source_ids != tuple(sorted(set(source_ids))):
        raise ValueError("condition sources must be unique and canonical")
    if len(condition_sources) != len(constraint_evaluations):
        raise ValueError("one CN result must exist per condition source")

    loaded = state.material.loaded()
    expected_state = ModelQueries(loaded).state_declaration(
        state_anchor_id, context=context)
    if expected_state != state:
        raise ValueError("carried state differs from authoritative model material")
    if any(evaluation.as_of != as_of
           for evaluation in constraint_evaluations):
        raise ValueError("one cutoff must govern classification")

    registration = (None if state.registration_index is None else
                    state.material.record_at(state.registration_index))
    if registration is None:
        if condition_sources or constraint_evaluations:
            raise ValueError("an unregistered state carries no condition evidence")
        condition_ids = ()
    else:
        condition_ids = registration.condition_constraint_anchor_ids
        if source_ids != condition_ids:
            raise ValueError("condition sources differ from the permanent set")

    binding_revision = None
    interpretation_revision = None
    for source, evaluation in zip(
            condition_sources, constraint_evaluations, strict=True):
        declaration = evaluation.constraint
        if declaration.constraint_anchor_id != source.constraint_anchor_id:
            raise ValueError("CN result is retargeted from its condition source")
        if declaration.revision != state.material.revision:
            raise ValueError("one model revision must govern classification")
        expected_constraint = ModelQueries(loaded).constraint_declaration(
            source.constraint_anchor_id)
        if declaration != expected_constraint:
            raise ValueError("carried CN declaration differs from model material")
        if declaration.status == "not_registered":
            continue
        semantic = evaluation.semantic_compatibility
        evidence_state = semantic.value_compatibility.state
        if (
            evidence_state.requested_entity_anchor_id
            != registration.subject_entity_anchor_id
            or evidence_state.binding_discovery != "explicit_selector"
            or evidence_state.selection != "explicit"
            or len(evidence_state.candidates) != 1
            or len(semantic.candidates) != 1
        ):
            raise ValueError("explicit condition evidence is incoherent")
        candidate = evidence_state.candidates[0]
        if (
            candidate.origin != "explicit_selector"
            or candidate.subject != source.source.subject
            or candidate.property != source.source.property
        ):
            raise ValueError("condition selector does not identify the candidate")
        current_binding = evidence_state.binding_revision
        current_interpretation = semantic.interpretation_revision
        if binding_revision is None:
            binding_revision = current_binding
        elif binding_revision != current_binding:
            raise ValueError("one binding revision must govern classification")
        if interpretation_revision is None:
            interpretation_revision = current_interpretation
        elif interpretation_revision != current_interpretation:
            raise ValueError(
                "one interpretation revision must govern classification")

    state_reason = _state_refusal(state.conclusion)
    pins = _active_pin_ids(state)
    state_admitted = pins is not None
    rows = []
    refusals = []
    if state_reason is not None:
        refusals.append({"reason": state_reason, "condition_index": None})
    outcomes = []
    for index, (source, evaluation) in enumerate(zip(
            condition_sources, constraint_evaluations, strict=True)):
        pinned_id = None if pins is None else pins[source.constraint_anchor_id]
        candidate_index, alignment, outcome, reason = _condition_facts(
            evaluation, pinned_id, state_admitted)
        rows.append({
            "condition_index": index,
            "constraint_anchor_id": source.constraint_anchor_id,
            "source_index": index,
            "constraint_evaluation_index": index,
            "candidate_index": candidate_index,
            "declaration_alignment": alignment,
            "outcome": outcome,
        })
        outcomes.append(outcome)
        if reason is not None:
            refusals.append({"reason": reason, "condition_index": index})

    if not state_admitted:
        coverage = "not_evaluated"
        execution = "not_executed"
        computed = None
    else:
        unknown = any(outcome == "not_evaluated" for outcome in outcomes)
        violated = any(outcome == "violated" for outcome in outcomes)
        coverage = "incomplete" if unknown else "complete"
        if violated:
            execution = "executed"
            computed = "does_not_match"
        elif unknown:
            execution = "not_executed"
            computed = None
        else:
            execution = "executed"
            computed = "matches"

    refusals.sort(key=lambda row: (
        _REFUSAL_RANK[row["reason"]],
        -1 if row["condition_index"] is None else row["condition_index"],
    ))
    return {
        "ruleset_version": "st001.1",
        "conditions": tuple(rows),
        "condition_coverage": coverage,
        "temporal_alignment": (
            "not_evaluated" if registration is None else "not_asserted"),
        "execution": execution,
        "refusals": tuple(refusals),
        "computed_match": computed,
    }
