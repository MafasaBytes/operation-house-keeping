"""Single store-independent authoritative BH-001 derivation."""

from backend.constraint_evaluation import (
    NumericParityBreachError,
    parse_observed_decimal,
)
from backend.model_kernel import BehaviorRuleDeclaration


_REFUSAL_ORDER = (
    "behavior_not_registered", "behavior_not_declared", "behavior_inactive",
    "behavior_conflicted", "participant_model_not_registered",
    "observation_absent", "observation_not_attached", "binding_not_positive",
    "evidence_not_assessable", "numeric_specification_not_available",
    "numeric_specification_conflicted", "model_quantity_kind_not_available",
    "model_observation_role_not_available", "model_unit_not_available",
    "source_semantics_not_admitted", "quantity_kind_lock_mismatch",
    "observation_role_lock_mismatch", "unit_lock_mismatch",
    "numeric_value_absent", "numeric_value_shape_mismatch",
    "numeric_value_out_of_bounds", "acquisition_cohort_mismatch",
)
_REFUSAL_RANK = {reason: index for index, reason in enumerate(_REFUSAL_ORDER)}


def _behavior_refusal(conclusion):
    return {
        "not_registered": "behavior_not_registered",
        "not_declared": "behavior_not_declared",
        "inactive": "behavior_inactive",
        "conflicted": "behavior_conflicted",
        "declared": None,
    }[conclusion]


def _current_locks(behavior):
    if behavior.conclusion != "declared":
        return None
    declarations = tuple(
        behavior.material.record_at(index)
        for index in behavior.current_declaration_indices)
    if not declarations or not all(
            isinstance(record, BehaviorRuleDeclaration)
            for record in declarations):
        raise ValueError("declared behavior must carry current declarations")
    first = declarations[0].participant_semantics
    if any(record.participant_semantics != first for record in declarations):
        raise ValueError("declared behavior has divergent effective bodies")
    return {lock.variable_anchor_id: lock.signature for lock in first}


def _cohort_key(occurrence):
    return (
        occurrence.subject.source_id,
        occurrence.subject.adapter_id,
        occurrence.attempt_id,
        occurrence.raw_record_id,
        occurrence.payload_checksum,
    )


def _participant_facts(source, semantic, lock):
    value = semantic.value_compatibility
    state = value.state
    if (
        semantic.variable_anchor_id != source.variable_anchor_id
        or value.variable_anchor_id != source.variable_anchor_id
        or state.variable_anchor_id != source.variable_anchor_id
        or state.requested_entity_anchor_id != source.entity_anchor_id
        or semantic.as_of != state.as_of
        or state.binding_discovery != "explicit_selector"
        or state.selection != "explicit"
        or len(state.candidates) != 1
        or len(value.candidates) != 1
        or len(semantic.candidates) != 1
    ):
        raise ValueError("explicit participant evidence is incoherent")

    state_candidate = state.candidates[0]
    value_candidate = value.candidates[0]
    semantic_candidate = semantic.candidates[0]
    if (
        state_candidate.origin != "explicit_selector"
        or state_candidate.subject != source.source.subject
        or state_candidate.property != source.source.property
        or value_candidate.state_candidate != state_candidate
        or semantic_candidate.value_candidate != value_candidate
    ):
        raise ValueError("selector does not identify the carried candidate")

    refusals = set()
    model_admission = (
        "admitted" if state.model_membership == "registered"
        else "not_admitted")
    if model_admission == "not_admitted":
        refusals.add("participant_model_not_registered")

    bound = state_candidate.bound
    occurrence = None if bound is None else bound.observed.occurrence
    if bound is None:
        observation_availability = "none_before_cutoff"
        attachment_admission = "not_evaluated"
        refusals.add("observation_absent")
    else:
        observation_availability = "observed"
        if state_candidate.attachment == "attached":
            attachment_admission = "attached"
        else:
            attachment_admission = "not_attached"
            refusals.add("observation_not_attached")
        if bound.resolution.status != "bound":
            refusals.add("binding_not_positive")

    evidence_assessable = (
        value_candidate.evidence_consistency in ("consistent", "not_evaluated"))
    if bound is not None and not evidence_assessable:
        refusals.add("evidence_not_assessable")

    specification = value.specification_result
    numeric_specification = None
    if specification.status == "conflicted":
        refusals.add("numeric_specification_conflicted")
    elif (specification.status == "specified"
          and specification.specification.value_shape == "number"):
        numeric_specification = specification.specification
    else:
        refusals.add("numeric_specification_not_available")

    qk_result = semantic.semantics_result.quantity_kind
    role_result = semantic.semantics_result.observation_role
    qk = None
    role = None
    if qk_result.status == "declared":
        qk = qk_result.declaration.declaration.quantity_kind
    else:
        refusals.add("model_quantity_kind_not_available")
    if role_result.status == "declared":
        role = role_result.declaration.declaration.observation_role
    else:
        refusals.add("model_observation_role_not_available")

    unit = None
    if numeric_specification is not None:
        if numeric_specification.unit.kind == "declared":
            unit = numeric_specification.unit.unit
        else:
            refusals.add("model_unit_not_available")

    semantic_admission = "not_evaluated"
    if (bound is not None and attachment_admission == "attached"
            and evidence_assessable and qk is not None and role is not None):
        compatible = (
            semantic_candidate.quantity_kind_compatibility == "token_identical"
            and semantic_candidate.observation_role_compatibility
            == "token_identical")
        semantic_admission = "admitted" if compatible else "not_admitted"
        if not compatible:
            refusals.add("source_semantics_not_admitted")

    unit_admission = "not_evaluated"
    if (bound is not None and attachment_admission == "attached"
            and evidence_assessable and unit is not None):
        if semantic_candidate.unit_identity_compatibility == "unit_identity_exact":
            unit_admission = "exact"
        elif semantic_candidate.unit_identity_compatibility == "unit_identity_mismatch":
            unit_admission = "mismatch"
            refusals.add("source_semantics_not_admitted")
        else:
            refusals.add("source_semantics_not_admitted")

    lock_admission = "not_evaluated"
    if lock is not None and qk is not None and role is not None and unit is not None:
        lock_refusals = []
        if qk != lock.quantity_kind:
            lock_refusals.append("quantity_kind_lock_mismatch")
        if role != lock.observation_role:
            lock_refusals.append("observation_role_lock_mismatch")
        if unit != lock.unit:
            lock_refusals.append("unit_lock_mismatch")
        if lock_refusals:
            lock_admission = "mismatched"
            refusals.update(lock_refusals)
        else:
            lock_admission = "matched"

    numeric_eligible = False
    if bound is not None and evidence_assessable and numeric_specification is not None:
        if value_candidate.value_presence == "explicit_null":
            refusals.add("numeric_value_absent")
        elif value_candidate.observed_shape != "number":
            refusals.add("numeric_value_shape_mismatch")
        elif unit is not None:
            numeric_eligible = True

    return {
        "model_admission": model_admission,
        "observation_availability": observation_availability,
        "attachment_admission": attachment_admission,
        "semantic_admission": semantic_admission,
        "unit_admission": unit_admission,
        "lock_admission": lock_admission,
        "numeric_admission": "not_evaluated",
        "canonical_decimal": None,
        "refusals": refusals,
        "occurrence": occurrence,
        "numeric_eligible": numeric_eligible,
    }


def derive_evaluation(*, behavior, behavior_anchor_id, context, as_of,
                      participant_sources, semantic_results):
    if (
        behavior.behavior_anchor_id != behavior_anchor_id
        or behavior.context != context
        or len(participant_sources) != 2
        or len(semantic_results) != 2
    ):
        raise ValueError("evaluation request echo is incoherent")
    variable_ids = tuple(source.variable_anchor_id
                         for source in participant_sources)
    if variable_ids != tuple(sorted(set(variable_ids))):
        raise ValueError("participant sources must be unique and canonical")

    revisions = tuple(
        result.value_compatibility.state.model_revision
        for result in semantic_results)
    if any(revision != behavior.material.revision for revision in revisions):
        raise ValueError("one explicit model revision must govern evaluation")
    if any(result.as_of != as_of for result in semantic_results):
        raise ValueError("one cutoff must govern evaluation")
    bindings = tuple(result.value_compatibility.state.binding_revision
                     for result in semantic_results)
    interpretations = tuple(result.interpretation_revision
                            for result in semantic_results)
    if bindings[0] != bindings[1]:
        raise ValueError("one binding revision must govern both participants")
    if interpretations[0] != interpretations[1]:
        raise ValueError(
            "one interpretation revision must govern both participants")

    registration = (None if behavior.registration_index is None else
                    behavior.material.record_at(behavior.registration_index))
    if registration is not None and (
            tuple(registration.participant_variable_anchor_ids) != variable_ids):
        raise ValueError("participant set differs from behavior registration")

    locks = _current_locks(behavior)
    facts = []
    for index, (source, semantic) in enumerate(
            zip(participant_sources, semantic_results, strict=True)):
        lock = None if locks is None else locks[source.variable_anchor_id]
        facts.append(_participant_facts(source, semantic, lock))

    occurrences = tuple(fact["occurrence"] for fact in facts)
    if any(occurrence is None for occurrence in occurrences):
        cohort = "not_evaluated"
    elif _cohort_key(occurrences[0]) == _cohort_key(occurrences[1]):
        cohort = "same_acquisition_cohort"
    else:
        cohort = "different_acquisition_cohort"

    parity_failures = []
    if cohort == "same_acquisition_cohort":
        for fact in facts:
            if not fact["numeric_eligible"]:
                continue
            try:
                resolution = parse_observed_decimal(
                    fact["occurrence"].value_json)
            except NumericParityBreachError as error:
                parity_failures.append(error)
                continue
            if resolution.status == "admitted":
                fact["numeric_admission"] = "admitted"
                fact["canonical_decimal"] = resolution.decimal
            else:
                fact["numeric_admission"] = "out_of_bounds"
                fact["refusals"].add("numeric_value_out_of_bounds")
    if parity_failures:
        raise parity_failures[0]

    participant_rows = []
    for index, (source, fact) in enumerate(
            zip(participant_sources, facts, strict=True)):
        admitted = (
            fact["model_admission"] == "admitted"
            and fact["observation_availability"] == "observed"
            and fact["attachment_admission"] == "attached"
            and fact["semantic_admission"] == "admitted"
            and fact["unit_admission"] == "exact"
            and fact["lock_admission"] == "matched"
            and fact["numeric_admission"] == "admitted")
        ordered_refusals = tuple(sorted(
            fact["refusals"], key=_REFUSAL_RANK.__getitem__))
        participant_rows.append({
            "participant_index": index,
            "variable_anchor_id": source.variable_anchor_id,
            "source_index": index,
            "semantic_result_index": index,
            "candidate_index": 0,
            "model_admission": fact["model_admission"],
            "observation_availability": fact["observation_availability"],
            "attachment_admission": fact["attachment_admission"],
            "semantic_admission": fact["semantic_admission"],
            "unit_admission": fact["unit_admission"],
            "lock_admission": fact["lock_admission"],
            "numeric_admission": fact["numeric_admission"],
            "admission": "admitted" if admitted else "not_admitted",
            "refusal_reasons": ordered_refusals,
            "canonical_decimal": fact["canonical_decimal"],
        })

    behavior_reason = _behavior_refusal(behavior.conclusion)
    executable = (
        behavior_reason is None
        and cohort == "same_acquisition_cohort"
        and all(row["admission"] == "admitted" for row in participant_rows))
    refusals = []
    if behavior_reason is not None:
        refusals.append({"reason": behavior_reason, "participant_index": None})
    for index, row in enumerate(participant_rows):
        refusals.extend({"reason": reason, "participant_index": index}
                        for reason in row["refusal_reasons"])
    if cohort == "different_acquisition_cohort":
        refusals.append({
            "reason": "acquisition_cohort_mismatch", "participant_index": None})

    relation = None
    if executable:
        relation = ("equal" if participant_rows[0]["canonical_decimal"]
                    == participant_rows[1]["canonical_decimal"] else "different")
    return {
        "ruleset_version": "bh001.1",
        "participants": tuple(participant_rows),
        "cohort_admission": cohort,
        "execution": "executed" if executable else "not_executed",
        "not_executed_reasons": tuple(refusals),
        "computed_relation": relation,
    }
