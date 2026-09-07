"""Disposable integrated public lower-result worlds for TA-001 tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

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
    VAR_A,
    constraint_declaration,
    constraint_registration,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_OPERATED,
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


def _model(root, *, upper="80"):
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
            registration,
            declaration,
        ),
    )


def build_world(tmp_path, *, upper="80") -> AssessmentWorld:
    model = _model(tmp_path / "model-world", upper=upper)
    _, _, source, temporal = _captured_world(tmp_path / "evidence-world")
    semantic = semantic_queries(
        tmp_path / "semantic-world", model=model, temporal=temporal,
    )
    classifications = StateClassificationQueries(
        ConstraintEvaluationQueries(semantic),
    )
    condition_sources = (
        StateConditionSource(
            constraint_anchor_id=CON_A,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP),
        ),
    )
    from_as_of = AS_OF
    to_as_of = AS_OF + timedelta(minutes=1)
    from_classification = classifications.state_classification(
        STATE_A,
        context=AS_OPERATED,
        as_of=from_as_of,
        condition_sources=condition_sources,
    )
    to_classification = classifications.state_classification(
        STATE_B,
        context=AS_OPERATED,
        as_of=to_as_of,
        condition_sources=condition_sources,
    )
    selections = tuple(
        EvidenceAssuranceQueries(source=source, temporal=temporal)
        .select_operational_evidence(
            evidence_request(start=HORIZON, end=cutoff),
        )
        for cutoff in (from_as_of, to_as_of)
    )
    compatibilities = tuple(
        classification.constraint_evaluations[0]
        .semantic_compatibility.value_compatibility
        for classification in (from_classification, to_classification)
    )
    alignments = []
    for selection, compatibility in zip(selections, compatibilities):
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
