"""CN-001 Slice B constraint-evaluation result contracts.

Read-only, composition-only: this module holds no second vocabulary for a
fact the accepted ES-001, VS-001, VM-001, or MK-001 layers already state.
Lower-layer results — ``ConstraintDeclarationResult`` (Slice A),
``VariableSemanticCompatibilityResult`` (ES-001), and the candidates it
carries — are composed verbatim, never re-expressed, never copied field by
field, and never mutated.

The evaluator emits exactly three verdicts (``satisfied``, ``violated``,
``not_evaluated``) and one refusal-reason vocabulary. It emits no
``severity``, ``grade``, ``normality``, ``alarm``, ``recommendation``,
``cause``, ``diagnosis``, or ``safety`` field, ever. ``violated`` asserts
ONLY that the admitted observed value does not satisfy the declared
numeric predicate; it connotes nothing about safety, normality, fault,
or any recommended action.

The authoritative validators re-derive every per-candidate evaluation from
the carried declaration, the carried ES result, and the CN narrow parser,
and reject any divergence — including objects forged through
``model_construct`` or ``model_copy`` or with stale content-derived ids.
The re-derivation is identical to the facade's original computation
because both call ``derive_candidate_evaluation``.
"""

from datetime import UTC
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field, model_validator)

from backend.constraint_evaluation.decimal import (
    CanonicalObservedDecimal, parse_observed_decimal)
from backend.model_kernel import (
    ConstraintDeclarationResult, ConstraintPredicate, ConstraintSemanticSignature,
    ExactNumericInterval, ExactNumericLowerBound, ExactNumericUpperBound,
    ModelRevision, NumericBoundary)
from backend.observation_compatibility import CandidateValueCompatibility
from backend.semantic_compatibility import (
    CandidateSemanticCompatibility, VariableSemanticCompatibilityResult)
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN)

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]


# ----------------------------------------------------------- vocabularies

Verdict = Literal["satisfied", "violated", "not_evaluated"]

#: The single refusal-reason vocabulary. Steps 5 and 6 carry the accepted
#: VS reason verbatim (the ``evidence_consistency`` value at step 5 and the
#: ``value_shape_not_evaluated_reason`` value at step 6); the precedence
#: ensures only one reason is reported per candidate. ``model_value_shape_not_numeric``
#: and ``declared_semantics_not_compatible`` are CN-only reasons. The
#: constraint-level reasons ``not_declared`` and ``conflicted`` come from
#: the carried Slice A ``ConstraintDeclarationResult.status``.
NotEvaluatedReason = Literal[
    # constraint-level (steps 1-2)
    "not_declared",
    "conflicted",
    # observation-level (steps 3-4)
    "no_observation",
    "observation_not_attached",
    # evidence not assessable (step 5, VS ``evidence_consistency`` verbatim)
    "json_type_unrecognized",
    "shape_disagreement",
    "value_json_malformed",
    "value_not_representable",
    # VS shape not evaluated (step 6, VS ``value_shape_not_evaluated_reason`` verbatim)
    "specification_conflicted",
    "specification_not_available",
    "evidence_not_assessable",
    # CN-only (step 7)
    "model_value_shape_not_numeric",
    # VS shape mismatch (step 8)
    "does_not_satisfy_value_shape",
    # numeric value absent (step 9)
    "numeric_value_absent",
    # ES gate (step 10)
    "declared_semantics_not_compatible",
    # constraint semantic locks (steps 11-13)
    "constraint_quantity_kind_lock_mismatch",
    "constraint_observation_role_lock_mismatch",
    "constraint_unit_identity_lock_mismatch",
    # CN resource limits (step 14)
    "numeric_value_out_of_bounds",
]


class _Frozen(BaseModel):
    # `revalidate_instances` is read from the model being validated, so
    # this hardens THIS module's own nested contracts against forged
    # instances. It cannot reach the carried lower-layer types, whose
    # config belongs to their own accepted modules: those objects are
    # trusted because the accepted ES/VS/MK facades produce them — they are
    # never supplied by a caller of this module.
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


# ----------------------------------------------------------- boundary assessment

class BoundaryAssessment(_Frozen):
    """The exact comparison of one predicate boundary against the admitted
    observed decimal. Carries the boundary's canonical value, its
    inclusion, the observed relation, and whether THIS boundary is
    satisfied. ``satisfied`` asserts only the boundary's predicate truth;
    it connotes nothing about safety, normality, or any recommended
    action."""

    role: Literal["lower", "upper"]
    boundary_value: str
    inclusion: Literal["inclusive", "exclusive"]
    relation: Literal["less", "equal", "greater"]
    satisfied: bool

    @model_validator(mode="after")
    def _locked(self):
        if self.role == "lower":
            expected = (self.relation in ("equal", "greater")
                        if self.inclusion == "inclusive"
                        else self.relation == "greater")
        else:
            expected = (self.relation in ("equal", "less")
                        if self.inclusion == "inclusive"
                        else self.relation == "less")
        if self.satisfied != expected:
            raise ValueError("satisfied must follow the boundary relation "
                             "and inclusion")
        return self


# ----------------------------------------------------------- candidate evaluation

class CandidateConstraintEvaluation(_Frozen):
    """One (constraint, candidate) evaluation. The candidate is referred to
    by contiguous index into the carried ES result's candidates; no second
    ``CandidateSemanticCompatibility`` or ``CandidateValueCompatibility``
    copy is held here. ``observed_decimal`` and ``boundary_assessments``
    are present exactly when the verdict is ``satisfied`` or ``violated``;
    ``not_evaluated_reason`` is present exactly when the verdict is
    ``not_evaluated``. No ``severity``, ``grade``, ``alarm``,
    ``recommendation``, ``cause``, ``diagnosis``, or ``safety`` field
    exists or can be added (``extra="forbid"``)."""

    candidate_index: int = Field(ge=0)
    verdict: Verdict
    not_evaluated_reason: NotEvaluatedReason | None = None
    observed_decimal: CanonicalObservedDecimal | None = None
    boundary_assessments: tuple[BoundaryAssessment, ...] = ()

    @model_validator(mode="after")
    def _locked(self):
        if (self.not_evaluated_reason is None) != (self.verdict != "not_evaluated"):
            raise ValueError("a not-evaluated reason is present exactly when "
                             "the verdict is not evaluated")
        if (self.observed_decimal is None) != (self.verdict == "not_evaluated"):
            raise ValueError("an observed decimal is present exactly when a "
                             "verdict was reached")
        if (bool(self.boundary_assessments) == (self.verdict == "not_evaluated")):
            raise ValueError("boundary assessments are present exactly when a "
                             "verdict was reached")
        if self.verdict != "not_evaluated":
            if self.observed_decimal is None or not self.boundary_assessments:
                raise ValueError("a reached verdict carries its decimal and "
                                 "its boundary assessments")
        return self


# ----------------------------------------------------------- derivation

def _assess_boundary(boundary: NumericBoundary, observed: Decimal,
                     role: str) -> BoundaryAssessment:
    boundary_value = Decimal(boundary.value)
    if observed < boundary_value:
        relation = "less"
    elif observed > boundary_value:
        relation = "greater"
    else:
        relation = "equal"
    if role == "lower":
        satisfied = (relation in ("equal", "greater")
                     if boundary.inclusion == "inclusive"
                     else relation == "greater")
    else:
        satisfied = (relation in ("equal", "less")
                     if boundary.inclusion == "inclusive"
                     else relation == "less")
    return BoundaryAssessment(
        role=role, boundary_value=boundary.value, inclusion=boundary.inclusion,
        relation=relation, satisfied=satisfied)


def _derive_boundary_assessments(predicate: ConstraintPredicate,
                                 observed: Decimal) -> tuple[BoundaryAssessment, ...]:
    if isinstance(predicate, ExactNumericLowerBound):
        return (_assess_boundary(predicate.lower, observed, "lower"),)
    if isinstance(predicate, ExactNumericUpperBound):
        return (_assess_boundary(predicate.upper, observed, "upper"),)
    if isinstance(predicate, ExactNumericInterval):
        return (
            _assess_boundary(predicate.lower, observed, "lower"),
            _assess_boundary(predicate.upper, observed, "upper"),
        )
    raise ValueError("unknown constraint predicate kind")


def derive_candidate_evaluation(
        declaration: ConstraintDeclarationResult,
        es_result: VariableSemanticCompatibilityResult,
        candidate_index: int) -> CandidateConstraintEvaluation:
    """The single authoritative per-candidate derivation. Pure: no I/O,
    no facade, no injected state. Both the facade and the result validators
    call this, so a forged or divergent candidate is always detected.

    The reachable precedence is fixed and total:
        1.  constraint not declared            -> ``not_declared``
        2.  constraint conflicted              -> ``conflicted``
        3.  observation absent                  -> ``no_observation``
        4.  observation not attached            -> ``observation_not_attached``
        5.  evidence not assessable             -> VS ``evidence_consistency`` verbatim
        6.  VS shape not evaluated              -> VS ``value_shape_not_evaluated_reason`` verbatim
        7.  governing VSP not numeric           -> ``model_value_shape_not_numeric``
        8.  VS shape evaluated mismatch         -> ``does_not_satisfy_value_shape``
        9.  numeric value absent (nullable null)-> ``numeric_value_absent``
        10. declared semantics not compatible   -> ``declared_semantics_not_compatible``
        11. quantity-kind lock mismatch         -> ``constraint_quantity_kind_lock_mismatch``
        12. observation-role lock mismatch       -> ``constraint_observation_role_lock_mismatch``
        13. unit-identity lock mismatch         -> ``constraint_unit_identity_lock_mismatch``
        14. numeric value outside CN bounds     -> ``numeric_value_out_of_bounds``
        15. otherwise exact predicate comparison -> ``satisfied`` | ``violated``

    Authoritative model semantic tokens (steps 11-13) are dereferenced only
    after the candidate-local ``declared_semantics_compatible`` finding has
    passed (step 10)."""

    status = declaration.status
    if status == "not_declared":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="not_declared")
    if status == "conflicted":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="conflicted")
    if status != "declared":
        # not_registered has no candidates and never reaches here; a future
        # unknown status is an honest non-evaluation rather than a guess.
        raise ValueError("declared candidate derivation requires a declared "
                         "constraint")

    es_candidate = es_result.candidates[candidate_index]
    value_candidate: CandidateValueCompatibility = es_candidate.value_candidate
    state_candidate = value_candidate.state_candidate

    # step 3: observation absent
    if state_candidate.bound is None:
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="no_observation")
    # step 4: observation not attached
    if state_candidate.attachment != "attached":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="observation_not_attached")
    # step 5: evidence not assessable (VS evidence_consistency verbatim)
    if value_candidate.evidence_consistency != "consistent":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason=value_candidate.evidence_consistency)
    # step 6: VS shape not evaluated (VS reason verbatim)
    if value_candidate.value_shape_compatibility == "not_evaluated":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason=value_candidate.value_shape_not_evaluated_reason)
    # step 7: governing VSP not numeric (CN-only)
    specification_result = es_result.value_compatibility.specification_result
    if specification_result.status != "specified":
        # By precedence step 6 should have caught a missing/conflicted VSP;
        # reaching here is a VS contract inconsistency. Report honestly.
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="specification_not_available")
    governing_shape = specification_result.specification.value_shape
    if governing_shape != "number":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="model_value_shape_not_numeric")
    # step 8: VS shape evaluated mismatch
    if value_candidate.value_shape_compatibility == "does_not_satisfy_value_shape":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="does_not_satisfy_value_shape")
    # step 9: numeric value absent, including an admitted nullable null
    if value_candidate.value_presence == "explicit_null":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="numeric_value_absent")
    # step 10: ES declared_semantics_compatible not present
    if "declared_semantics_compatible" not in es_candidate.semantic_findings:
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="declared_semantics_not_compatible")

    # steps 11-13: dereference authoritative model semantic tokens now that
    # the candidate-local declared_semantics_compatible finding has passed.
    declaration_record = declaration.declaration
    expected_semantics: ConstraintSemanticSignature = declaration_record.expected_semantics
    predicate = declaration_record.predicate

    semantics_result = es_result.semantics_result
    model_qk = semantics_result.quantity_kind.declaration.declaration.quantity_kind
    if expected_semantics.quantity_kind != model_qk:
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="constraint_quantity_kind_lock_mismatch")
    model_or = semantics_result.observation_role.declaration.declaration.observation_role
    if expected_semantics.observation_role != model_or:
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="constraint_observation_role_lock_mismatch")
    model_unit = specification_result.specification.unit.unit
    if expected_semantics.unit != model_unit:
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="constraint_unit_identity_lock_mismatch")

    # step 14: parse the observed numeric lexeme
    occurrence = state_candidate.bound.observed.occurrence
    parsed = parse_observed_decimal(occurrence.value_json)
    if parsed.status == "out_of_bounds":
        return CandidateConstraintEvaluation(
            candidate_index=candidate_index, verdict="not_evaluated",
            not_evaluated_reason="numeric_value_out_of_bounds")
    observed = parsed.decimal

    # step 15: exact predicate comparison
    observed_value = Decimal(observed.canonical)
    assessments = _derive_boundary_assessments(predicate, observed_value)
    verdict: Verdict = (
        "satisfied" if all(assessment.satisfied for assessment in assessments)
        else "violated")
    return CandidateConstraintEvaluation(
        candidate_index=candidate_index, verdict=verdict,
        not_evaluated_reason=None, observed_decimal=observed,
        boundary_assessments=assessments)


# ----------------------------------------------------------- exact-lookup result

class ConstraintEvaluationResult(_Frozen):
    """The evaluation of one constraint against the evidence attached to
    its target variable. The complete accepted ES result is carried once
    (``semantic_compatibility``); each candidate evaluation refers to the
    ES candidate by contiguous index and holds no second
    ``CandidateSemanticCompatibility`` or ``CandidateValueCompatibility``
    copy. For an unregistered constraint, ``semantic_compatibility`` is
    ``None`` and ``candidates`` is empty."""

    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    declaration: ConstraintDeclarationResult
    as_of: UtcDatetime
    ruleset_version: Literal["cn001.1"]
    semantic_compatibility: VariableSemanticCompatibilityResult | None = None
    candidates: tuple[CandidateConstraintEvaluation, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _authoritative(self):
        if self.declaration.constraint_anchor_id != self.constraint_anchor_id:
            raise ValueError("the declaration must answer for the requested "
                             "constraint anchor")
        if self.declaration.revision != self.revision:
            raise ValueError("revision must equal the carried declaration's "
                             "revision")
        if self.declaration.status == "not_registered":
            if self.semantic_compatibility is not None or self.candidates:
                raise ValueError("an unregistered constraint carries no ES "
                                 "result and no candidates")
            return self
        if self.semantic_compatibility is None:
            raise ValueError("a registered constraint must carry the ES "
                             "result")
        es = self.semantic_compatibility
        if self.as_of != es.as_of:
            raise ValueError("as_of must equal the carried ES result cutoff")
        if (es.semantics_result.revision != self.revision
                or es.value_compatibility.state.model_revision != self.revision):
            raise ValueError("one model revision governs the declaration, "
                             "semantics, and state")
        if es.variable_anchor_id != self.declaration.registration.variable_anchor_id:
            raise ValueError("the ES result must answer for the "
                             "registration's target variable")
        if len(self.candidates) != len(es.candidates):
            raise ValueError("one candidate evaluation per ES candidate")
        for index, candidate in enumerate(self.candidates):
            if candidate.candidate_index != index:
                raise ValueError("candidate indices must be contiguous and "
                                 "ordered")
            expected = derive_candidate_evaluation(
                self.declaration, es, index)
            if candidate != expected:
                raise ValueError("each candidate evaluation must equal the "
                                 "authoritative derivation")
        return self


# ----------------------------------------------------------- variable-scoped discovery

class VariableConstraintEvaluationCollectionResult(_Frozen):
    """Structured variable-scoped evaluation discovery: the evaluations of
    every constraint targeting one variable. The registered /
    not_registered distinction from Slice A is preserved so an empty
    ``evaluations`` tuple is never ambiguous. The complete accepted ES
    result for the variable is carried once (``semantic_compatibility``);
    each evaluation refers to it. For a not-registered variable, or a
    registered variable with no constraints, ``semantic_compatibility`` is
    ``None`` and ``evaluations`` is empty."""

    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    as_of: UtcDatetime
    ruleset_version: Literal["cn001.1"]
    status: Literal["registered", "not_registered"]
    semantic_compatibility: VariableSemanticCompatibilityResult | None = None
    evaluations: tuple[ConstraintEvaluationResult, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _authoritative(self):
        if self.status == "not_registered":
            if self.semantic_compatibility is not None or self.evaluations:
                raise ValueError("an unregistered variable carries no ES "
                                 "result and no evaluations")
            return self
        anchor_ids = tuple(ev.constraint_anchor_id for ev in self.evaluations)
        if len(set(anchor_ids)) != len(anchor_ids):
            raise ValueError("each constraint anchor appears at most once")
        if list(anchor_ids) != sorted(anchor_ids):
            raise ValueError("evaluations must be ordered by constraint "
                             "anchor id")
        if self.evaluations and self.semantic_compatibility is None:
            raise ValueError("a registered variable with constraints carries "
                             "the ES result")
        for ev in self.evaluations:
            if ev.declaration.registration is None:
                raise ValueError("every evaluation targets a registered "
                                 "constraint")
            if ev.declaration.registration.variable_anchor_id != self.variable_anchor_id:
                raise ValueError("every evaluation must target the requested "
                                 "variable")
            if ev.revision != self.revision:
                raise ValueError("one model revision governs the collection")
            if ev.as_of != self.as_of:
                raise ValueError("one cutoff governs the collection")
            if ev.semantic_compatibility != self.semantic_compatibility:
                raise ValueError("the ES result is carried once and shared "
                                 "by every evaluation")
        return self