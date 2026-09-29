"""Authoritative public contracts for CN-001 Slice B evaluation."""

from datetime import UTC
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field,
    model_validator)

from backend.constraint_evaluation.decimal import (
    CanonicalObservedDecimal, parse_observed_decimal)
from backend.model_kernel import (
    ConstraintDeclarationResult, ConstraintPredicate,
    ConstraintSemanticSignature, ExactNumericInterval,
    ExactNumericLowerBound, ExactNumericUpperBound, NumericBoundary,
    VariableConstraintCollectionResult)
from backend.observation_compatibility import CandidateValueCompatibility
from backend.semantic_compatibility import VariableSemanticCompatibilityResult
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN)

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]

ConstraintEvaluationVerdict = Literal[
    "satisfied", "violated", "not_evaluated"]
ConstraintNotEvaluatedReason = Literal[
    "constraint_not_declared",
    "constraint_conflicted",
    "observation_absent",
    "observation_not_attached",
    "evidence_not_assessable",
    "value_shape_not_evaluated",
    "model_value_shape_not_numeric",
    "value_shape_not_satisfied",
    "numeric_value_absent",
    "declared_semantics_not_compatible",
    "constraint_quantity_kind_mismatch",
    "constraint_observation_role_mismatch",
    "constraint_unit_identity_mismatch",
    "numeric_value_out_of_bounds",
]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


def _revalidate(instance, kind, label):
    try:
        rebuilt = kind.model_validate(
            instance.model_dump(mode="python", warnings=False))
    except (ValueError, TypeError, AttributeError, KeyError,
            UnicodeError, Warning) as error:
        raise ValueError(f"{label} must be structurally valid") from error
    if rebuilt != instance:
        raise ValueError(f"{label} must survive revalidation unchanged")
    return rebuilt


class BoundaryAssessment(_Frozen):
    side: Literal["lower", "upper"]
    boundary: NumericBoundary
    relation: Literal["below", "equal", "above"]
    satisfied: bool

    @model_validator(mode="after")
    def _authoritative(self):
        boundary = _revalidate(self.boundary, NumericBoundary, "boundary")
        if self.side == "lower":
            expected = (self.relation in ("equal", "above")
                        if boundary.inclusion == "inclusive"
                        else self.relation == "above")
        else:
            expected = (self.relation in ("equal", "below")
                        if boundary.inclusion == "inclusive"
                        else self.relation == "below")
        if self.satisfied != expected:
            raise ValueError("satisfaction must follow side, relation, and inclusion")
        return self


class CandidateConstraintEvaluation(_Frozen):
    semantic_candidate_index: int = Field(ge=0)
    verdict: ConstraintEvaluationVerdict
    not_evaluated_reason: ConstraintNotEvaluatedReason | None = None
    observed_decimal: CanonicalObservedDecimal | None = None
    boundary_assessments: tuple[BoundaryAssessment, ...] = ()

    @model_validator(mode="after")
    def _shape(self):
        refused = self.verdict == "not_evaluated"
        if refused != (self.not_evaluated_reason is not None):
            raise ValueError("a refusal reason exists exactly for not_evaluated")
        if refused != (self.observed_decimal is None):
            raise ValueError("an observed decimal exists exactly for a reached verdict")
        if refused != (not self.boundary_assessments):
            raise ValueError("boundary assessments exist exactly for a reached verdict")
        return self


def _assess_boundary(boundary: NumericBoundary, observed: Decimal,
                     side: Literal["lower", "upper"]) -> BoundaryAssessment:
    value = Decimal(boundary.value)
    relation = "below" if observed < value else "above" if observed > value else "equal"
    if side == "lower":
        satisfied = (relation in ("equal", "above")
                     if boundary.inclusion == "inclusive"
                     else relation == "above")
    else:
        satisfied = (relation in ("equal", "below")
                     if boundary.inclusion == "inclusive"
                     else relation == "below")
    return BoundaryAssessment(
        side=side, boundary=boundary, relation=relation, satisfied=satisfied)


def _assessments(predicate: ConstraintPredicate, observed: Decimal):
    if isinstance(predicate, ExactNumericLowerBound):
        return (_assess_boundary(predicate.lower, observed, "lower"),)
    if isinstance(predicate, ExactNumericUpperBound):
        return (_assess_boundary(predicate.upper, observed, "upper"),)
    if isinstance(predicate, ExactNumericInterval):
        return (_assess_boundary(predicate.lower, observed, "lower"),
                _assess_boundary(predicate.upper, observed, "upper"))
    raise ValueError("unknown constraint predicate")


def _refused(index: int, reason: ConstraintNotEvaluatedReason):
    return CandidateConstraintEvaluation(
        semantic_candidate_index=index, verdict="not_evaluated",
        not_evaluated_reason=reason)


def derive_candidate_evaluation(
        constraint: ConstraintDeclarationResult,
        semantic_compatibility: VariableSemanticCompatibilityResult,
        semantic_candidate_index: int) -> CandidateConstraintEvaluation:
    """Apply the accepted admission precedence and exact predicate."""
    if constraint.status == "not_declared":
        return _refused(semantic_candidate_index, "constraint_not_declared")
    if constraint.status == "conflicted":
        return _refused(semantic_candidate_index, "constraint_conflicted")
    if constraint.status != "declared":
        raise ValueError("candidate evaluation requires a registered constraint")

    semantic_candidate = semantic_compatibility.candidates[semantic_candidate_index]
    value_candidate: CandidateValueCompatibility = semantic_candidate.value_candidate
    state_candidate = value_candidate.state_candidate
    if state_candidate.bound is None:
        return _refused(semantic_candidate_index, "observation_absent")
    if state_candidate.attachment != "attached":
        return _refused(semantic_candidate_index, "observation_not_attached")
    if value_candidate.evidence_consistency != "consistent":
        return _refused(semantic_candidate_index, "evidence_not_assessable")
    if value_candidate.value_shape_compatibility == "not_evaluated":
        return _refused(semantic_candidate_index, "value_shape_not_evaluated")

    specification = semantic_compatibility.value_compatibility.specification_result
    if specification.status != "specified":
        return _refused(semantic_candidate_index, "value_shape_not_evaluated")
    if specification.specification.value_shape != "number":
        return _refused(semantic_candidate_index, "model_value_shape_not_numeric")
    if value_candidate.value_shape_compatibility == "does_not_satisfy_value_shape":
        return _refused(semantic_candidate_index, "value_shape_not_satisfied")
    if value_candidate.value_presence == "explicit_null":
        return _refused(semantic_candidate_index, "numeric_value_absent")
    if "declared_semantics_compatible" not in semantic_candidate.semantic_findings:
        return _refused(
            semantic_candidate_index, "declared_semantics_not_compatible")

    record = constraint.declaration
    expected: ConstraintSemanticSignature = record.expected_semantics
    semantics = semantic_compatibility.semantics_result
    model_quantity = semantics.quantity_kind.declaration.declaration.quantity_kind
    if expected.quantity_kind != model_quantity:
        return _refused(
            semantic_candidate_index, "constraint_quantity_kind_mismatch")
    model_role = semantics.observation_role.declaration.declaration.observation_role
    if expected.observation_role != model_role:
        return _refused(
            semantic_candidate_index, "constraint_observation_role_mismatch")
    model_unit = specification.specification.unit.unit
    if expected.unit != model_unit:
        return _refused(
            semantic_candidate_index, "constraint_unit_identity_mismatch")

    lexeme = state_candidate.bound.observed.occurrence.value_json
    resolution = parse_observed_decimal(lexeme)
    if resolution.status == "out_of_bounds":
        return _refused(semantic_candidate_index, "numeric_value_out_of_bounds")
    observed = resolution.decimal
    assessments = _assessments(record.predicate, Decimal(observed))
    verdict: ConstraintEvaluationVerdict = (
        "satisfied" if all(item.satisfied for item in assessments)
        else "violated")
    return CandidateConstraintEvaluation(
        semantic_candidate_index=semantic_candidate_index, verdict=verdict,
        observed_decimal=observed, boundary_assessments=assessments)


class ConstraintEvaluationResult(_Frozen):
    constraint: ConstraintDeclarationResult
    as_of: UtcDatetime
    ruleset_version: Literal["cn001.1"]
    semantic_compatibility: VariableSemanticCompatibilityResult | None = None
    candidates: tuple[CandidateConstraintEvaluation, ...] = ()

    @model_validator(mode="after")
    def _authoritative(self):
        constraint = _revalidate(
            self.constraint, ConstraintDeclarationResult, "constraint")
        if constraint.status == "not_registered":
            if self.semantic_compatibility is not None or self.candidates:
                raise ValueError("an unregistered constraint carries no ES or rows")
            return self
        if self.semantic_compatibility is None:
            raise ValueError("a registered constraint carries one ES result")
        es = _revalidate(
            self.semantic_compatibility, VariableSemanticCompatibilityResult,
            "semantic compatibility")
        if self.as_of != es.as_of:
            raise ValueError("one cutoff governs the result")
        if (es.semantics_result.revision != constraint.revision
                or es.value_compatibility.state.model_revision != constraint.revision):
            raise ValueError("one model revision governs constraint and ES")
        if es.variable_anchor_id != constraint.registration.variable_anchor_id:
            raise ValueError("ES must answer for the constraint target variable")
        if len(self.candidates) != len(es.candidates):
            raise ValueError("one row exists per semantic candidate")
        for index, row in enumerate(self.candidates):
            if row.semantic_candidate_index != index:
                raise ValueError("semantic candidate indices are contiguous")
            if row != derive_candidate_evaluation(constraint, es, index):
                raise ValueError("candidate row differs from authoritative derivation")
        return self


class VariableConstraintEvaluationEntry(_Frozen):
    constraint_index: int = Field(ge=0)
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    candidates: tuple[CandidateConstraintEvaluation, ...] = ()


class VariableConstraintEvaluationCollectionResult(_Frozen):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    as_of: UtcDatetime
    ruleset_version: Literal["cn001.1"]
    constraint_collection: VariableConstraintCollectionResult
    semantic_compatibility: VariableSemanticCompatibilityResult | None = None
    evaluations: tuple[VariableConstraintEvaluationEntry, ...] = ()

    @model_validator(mode="after")
    def _authoritative(self):
        collection = _revalidate(
            self.constraint_collection, VariableConstraintCollectionResult,
            "constraint collection")
        if collection.variable_anchor_id != self.variable_anchor_id:
            raise ValueError("collection must answer for the requested variable")
        constraints = collection.constraints
        if not constraints:
            if self.semantic_compatibility is not None or self.evaluations:
                raise ValueError("empty discovery carries no ES or entries")
            return self
        if self.semantic_compatibility is None:
            raise ValueError("nonempty discovery carries one ES result")
        es = _revalidate(
            self.semantic_compatibility, VariableSemanticCompatibilityResult,
            "semantic compatibility")
        if (self.as_of != es.as_of
                or es.variable_anchor_id != self.variable_anchor_id
                or es.semantics_result.revision != collection.revision
                or es.value_compatibility.state.model_revision != collection.revision):
            raise ValueError("variable, cutoff, and model revision must be coherent")
        if len(self.evaluations) != len(constraints):
            raise ValueError("one lightweight entry exists per constraint")
        for index, entry in enumerate(self.evaluations):
            constraint = constraints[index]
            if entry.constraint_index != index:
                raise ValueError("constraint indices are contiguous and ordered")
            if entry.constraint_anchor_id != constraint.constraint_anchor_id:
                raise ValueError("constraint index and anchor must agree")
            if len(entry.candidates) != len(es.candidates):
                raise ValueError("one row exists per semantic candidate")
            for candidate_index, row in enumerate(entry.candidates):
                if row.semantic_candidate_index != candidate_index:
                    raise ValueError("semantic candidate indices are contiguous")
                expected = derive_candidate_evaluation(
                    constraint, es, candidate_index)
                if row != expected:
                    raise ValueError("entry row differs from authoritative derivation")
        return self
