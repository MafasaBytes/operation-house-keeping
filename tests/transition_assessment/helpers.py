"""Disposable integrated public lower-result worlds for TA-001 tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.evidence_alignment import (
    OperationalEvidenceAlignmentRequest,
    align_operational_evidence_with_value_compatibility,
)
from backend.evidence_assurance import EvidenceAssuranceQueries
from backend.model_kernel import ModelQueries
from backend.model_state import SourceSelector
from backend.state_classification import (
    StateClassificationQueries,
    StateConditionSource,
)
from backend.transition_assessment import (
    DeclaredTransitionAssessmentRequest,
    TransitionAssessmentPolicy,
)

from tests.behavior_evaluation.helpers import E1, model_store, semantic_queries
from tests.evidence_assurance.test_selection import (
    AS_OF,
    HORIZON,
    _captured_world,
    _request as evidence_request,
)
from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    VAR_A,
    constraint_declaration,
    constraint_registration,
    registration as entity_registration,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
    REGISTRATION_DECLARATION,
    STATE_DECLARATION,
    STATE_A,
    STATE_B,
    pins,
    state_declaration,
    state_registration,
)
from tests.model_kernel.st002_slice_a_helpers import (
    TRANSITION_A,
    transition_declaration,
    transition_registration,
)
from tests.model_state.helpers import PROP_TEMP, SUBJECT


POLICY = TransitionAssessmentPolicy(
    kind="declared_endpoint_pattern_at_ordered_cutoffs",
    version="ta001.endpoint_pattern.v1",
    endpoint_selection="independent_latest_per_condition_at_or_before_cutoff",
    evidence_requirement="complete_alignment_with_matched_expected_fingerprint",
    source_time_use="disclosure_only",
    temporal_cohort="not_asserted",
    continuity="not_assessed",
)


@dataclass(frozen=True)
class AssessmentWorld:
    request: DeclaredTransitionAssessmentRequest
    model: object
    source: object
    temporal: object


def _model(root, *, upper="80", declare_transition=True):
    constraint_registration_record = constraint_registration(
        CON_A, variable_anchor_id=VAR_A,
    )
    constraint_declaration_record = constraint_declaration(
        CON_A, predicate=upper_bound(upper),
    )
    declarations = {CON_A: constraint_declaration_record}
    from_registration = state_registration(
        state_anchor_id=STATE_A,
        subject=E1,
        constraints=(CON_A,),
    )
    to_registration = state_registration(
        state_anchor_id=STATE_B,
        subject=E1,
        constraints=(CON_A,),
    )
    from_declaration = state_declaration(
        from_registration,
        state_anchor_id=STATE_A,
        context=AS_OPERATED,
        condition_pins=pins(constraints=(CON_A,), declarations=declarations),
    )
    to_declaration = state_declaration(
        to_registration,
        state_anchor_id=STATE_B,
        context=AS_OPERATED,
        condition_pins=pins(constraints=(CON_A,), declarations=declarations),
    )
    registration = transition_registration(
        transition_anchor_id=TRANSITION_A,
        subject=E1,
        from_registration=from_registration,
        to_registration=to_registration,
        from_state=STATE_A,
        to_state=STATE_B,
    )
    declaration = transition_declaration(
        registration,
        from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration,
        context=AS_OPERATED,
    )
    transition_records = (
        (registration, declaration) if declare_transition else (registration,)
    )
    return model_store(
        root,
        include_behavior=False,
        extra_records=(
            constraint_registration_record,
            constraint_declaration_record,
            from_registration,
            to_registration,
            from_declaration,
            to_declaration,
            *transition_records,
        ),
    )


def _split_endpoint_model(root, *, from_upper: str, to_upper: str):
    registrations = (
        constraint_registration(CON_A, variable_anchor_id=VAR_A),
        constraint_registration(CON_B, variable_anchor_id=VAR_A),
    )
    declarations = (
        constraint_declaration(CON_A, predicate=upper_bound(from_upper)),
        constraint_declaration(CON_B, predicate=upper_bound(to_upper)),
    )
    by_anchor = dict(zip((CON_A, CON_B), declarations, strict=True))
    kernel = __import__("backend.model_kernel", fromlist=["ModelRecordEvidence"])
    entity = entity_registration(E1)

    def state_evidence(constraint_record):
        return (
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=entity.record_id,
            ),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=constraint_record.record_id,
            ),
            REGISTRATION_DECLARATION,
        )

    def declaration_evidence(
        state_registration_record, constraint_record, declaration_record,
    ):
        return (
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=state_registration_record.record_id,
            ),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=constraint_record.record_id,
            ),
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=declaration_record.record_id,
            ),
            STATE_DECLARATION,
        )

    from_registration = state_registration(
        state_anchor_id=STATE_A,
        subject=E1,
        constraints=(CON_A,),
        evidence=state_evidence(registrations[0]),
    )
    to_registration = state_registration(
        state_anchor_id=STATE_B,
        subject=E1,
        constraints=(CON_B,),
        evidence=state_evidence(registrations[1]),
    )
    from_declaration = state_declaration(
        from_registration,
        state_anchor_id=STATE_A,
        context=AS_OPERATED,
        condition_pins=pins(
            constraints=(CON_A,), declarations=by_anchor,
        ),
        evidence=declaration_evidence(
            from_registration, registrations[0], declarations[0],
        ),
    )
    to_declaration = state_declaration(
        to_registration,
        state_anchor_id=STATE_B,
        context=AS_OPERATED,
        condition_pins=pins(
            constraints=(CON_B,), declarations=by_anchor,
        ),
        evidence=declaration_evidence(
            to_registration, registrations[1], declarations[1],
        ),
    )
    transition_registration_record = transition_registration(
        transition_anchor_id=TRANSITION_A,
        subject=E1,
        from_registration=from_registration,
        to_registration=to_registration,
        from_state=STATE_A,
        to_state=STATE_B,
    )
    transition_declaration_record = transition_declaration(
        transition_registration_record,
        from_registration=from_registration,
        to_registration=to_registration,
        from_declaration=from_declaration,
        to_declaration=to_declaration,
        context=AS_OPERATED,
    )
    return model_store(
        root,
        include_behavior=False,
        extra_records=(
            *registrations,
            *declarations,
            from_registration,
            to_registration,
            from_declaration,
            to_declaration,
            transition_registration_record,
            transition_declaration_record,
        ),
    )


def build_world(
    tmp_path,
    *,
    upper="80",
    declare_transition=True,
    from_as_of: datetime | None = None,
    to_as_of: datetime | None = None,
    from_upper: str | None = None,
    to_upper: str | None = None,
    model_mutator=None,
) -> AssessmentWorld:
    split = from_upper is not None or to_upper is not None
    if split:
        model = _split_endpoint_model(
            tmp_path / "model-world",
            from_upper=from_upper or upper,
            to_upper=to_upper or upper,
        )
    else:
        model = _model(
            tmp_path / "model-world",
            upper=upper,
            declare_transition=declare_transition,
        )
    if model_mutator is not None:
        model_mutator(model)
    _, _, source, temporal = _captured_world(tmp_path / "evidence-world")
    semantic = semantic_queries(
        tmp_path / "semantic-world", model=model, temporal=temporal,
    )
    classifications = StateClassificationQueries(
        ConstraintEvaluationQueries(semantic),
    )
    from_condition_sources = (
        StateConditionSource(
            constraint_anchor_id=CON_A,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP),
        ),
    )
    to_constraint = CON_B if split else CON_A
    to_condition_sources = (
        StateConditionSource(
            constraint_anchor_id=to_constraint,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP),
        ),
    )
    from_as_of = AS_OF if from_as_of is None else from_as_of
    to_as_of = (
        from_as_of + timedelta(minutes=1) if to_as_of is None else to_as_of
    )
    from_classification = classifications.state_classification(
        STATE_A,
        context=AS_OPERATED,
        as_of=from_as_of,
        condition_sources=from_condition_sources,
    )
    to_classification = classifications.state_classification(
        STATE_B,
        context=AS_OPERATED,
        as_of=to_as_of,
        condition_sources=to_condition_sources,
    )
    compatibilities = tuple(
        classification.constraint_evaluations[0]
        .semantic_compatibility.value_compatibility
        for classification in (from_classification, to_classification)
    )
    alignments = []
    for cutoff, compatibility in zip(
        (from_as_of, to_as_of), compatibilities,
    ):
        if (
            not compatibility.candidates
            or compatibility.candidates[0].state_candidate.bound is None
        ):
            continue
        selection = (
            EvidenceAssuranceQueries(source=source, temporal=temporal)
            .select_operational_evidence(
                evidence_request(start=HORIZON, end=cutoff),
            )
        )
        assert selection.snapshot is not None
        alignment_request = OperationalEvidenceAlignmentRequest(
            schema_version="1",
            selection=selection,
            compatibility=compatibility,
            expected_snapshot_fingerprint=selection.snapshot.content_fingerprint,
        )
        alignments.append(
            align_operational_evidence_with_value_compatibility(
                alignment_request,
            )
        )
    transition = ModelQueries(model.load()).transition_declaration(
        TRANSITION_A, context=AS_OPERATED,
    )
    request = DeclaredTransitionAssessmentRequest(
        schema_version="1",
        transition_anchor_id=TRANSITION_A,
        context=AS_OPERATED,
        from_as_of=from_as_of,
        to_as_of=to_as_of,
        policy=POLICY,
        transition=transition,
        from_classification=from_classification,
        to_classification=to_classification,
        evidence_alignments=tuple(alignments),
    )
    return AssessmentWorld(
        request=request, model=model, source=source, temporal=temporal,
    )
