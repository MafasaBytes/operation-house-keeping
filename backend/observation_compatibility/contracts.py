"""VS-001 compatibility result contracts.

A specification states what the MODEL requires; an observation states what
a source SUPPLIED; compatibility is the assessment of one against the
other. The two are never conflated and a model unit is never inherited
into source evidence.

Lower-layer results are COMPOSED, never re-expressed: the VM-001
`VariableStateResult`, its candidates, and the kernel's
`VariableSpecificationResult` are carried verbatim, and this module holds
no second vocabulary for a fact either of them already states.

Shape and unit are independently gated. Evidence consistency gates only
the shape verdict: a malformed or self-contradictory ``value_json`` never
erases an explicitly supplied source-unit string, and source-unit evidence
is disclosed whenever an observation exists, including for unattached
candidates.

There is no aggregate, normalized, filled, winning, current, or usable
value anywhere in this module.
"""

from datetime import UTC
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from backend.model_kernel import VariableSpecificationResult
from backend.model_state import CandidateObservation, VariableStateResult
from backend.system_identity import VARIABLE_ANCHOR_ID_PATTERN

UtcDatetime = Annotated[AwareDatetime,
                        AfterValidator(lambda v: v.astimezone(UTC))]


class ObservationCompatibilityError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class ObservationCompatibilityConfigurationError(
        ObservationCompatibilityError):
    """Invalid composition input. Request validation belongs to the
    accepted VM-001 boundary and its typed errors propagate unchanged;
    this module adds exactly one code of its own."""


class _Frozen(BaseModel):
    # `revalidate_instances` is read from the model being validated, so
    # this hardens THIS module's own nested contracts against forged
    # instances. It cannot reach the carried lower-layer types, whose
    # config belongs to their own accepted modules: those objects are
    # trusted because the accepted VM-001 and kernel facades produce them
    # — they are never supplied by a caller of this module.
    model_config = ConfigDict(frozen=True, extra="forbid",
                              revalidate_instances="always")


class CandidateValueCompatibility(_Frozen):
    state_candidate: CandidateObservation          # VM-001, VERBATIM

    value_presence: Literal["value_present", "explicit_null",
                            "no_observation", "indeterminate"]
    evidence_consistency: Literal["consistent", "json_type_unrecognized",
                                  "shape_disagreement", "value_json_malformed",
                                  "value_not_representable", "not_evaluated"]
    observed_shape: Literal["boolean", "number", "string",
                            "null", "array", "object"] | None = None

    # named for the dimension actually assessed: a specification also
    # declares a unit, and that half is reported separately
    value_shape_compatibility: Literal["satisfies_value_shape",
                                       "does_not_satisfy_value_shape",
                                       "not_evaluated"]
    value_shape_finding: Literal["shape_matches", "shape_differs",
                                 "explicit_null_allowed",
                                 "explicit_null_not_allowed",
                                 "unsupported_observed_structure"] | None = None
    value_shape_not_evaluated_reason: Literal[
        "no_observation", "observation_not_attached", "specification_conflicted",
        "specification_not_available", "evidence_not_assessable"] | None = None

    source_unit_evidence: Literal["present", "absent", "not_evaluated"]
    declared_unit_lexeme_relation: Literal["declared_lexeme_identical",
                                           "declared_lexeme_differs",
                                           "not_evaluated"]
    unit_lexeme_not_evaluated_reason: Literal[
        "no_observation", "observation_not_attached", "specification_conflicted",
        "specification_not_available", "model_unit_not_declared",
        "source_unit_absent"] | None = None

    @model_validator(mode="after")
    def _candidate_consistent(self):
        observed = self.state_candidate.bound is not None
        occurrence = (self.state_candidate.bound.observed.occurrence
                      if observed else None)

        if (self.value_shape_not_evaluated_reason is None) != (
                self.value_shape_compatibility != "not_evaluated"):
            raise ValueError("a shape reason is present exactly when the "
                             "shape verdict is not evaluated")
        if (self.unit_lexeme_not_evaluated_reason is None) != (
                self.declared_unit_lexeme_relation != "not_evaluated"):
            raise ValueError("a unit reason is present exactly when the "
                             "lexical relation is not evaluated")
        if (self.value_shape_finding is None) != (
                self.value_shape_compatibility == "not_evaluated"):
            raise ValueError("a finding is present exactly when a shape "
                             "verdict was computed")
        if self.value_shape_finding is not None:
            satisfies = self.value_shape_finding in (
                "shape_matches", "explicit_null_allowed")
            if satisfies != (self.value_shape_compatibility
                             == "satisfies_value_shape"):
                raise ValueError("the finding must agree with the verdict")

        # presence and evidence consistency are properties of the
        # observation alone
        if (self.evidence_consistency == "not_evaluated") != (not observed):
            raise ValueError("evidence consistency is evaluated exactly when "
                             "an observation exists")
        if (self.observed_shape is not None) != (
                self.evidence_consistency == "consistent"):
            raise ValueError("an observed shape exists exactly when the "
                             "evidence is internally consistent")
        if (self.value_presence == "no_observation") != (not observed):
            raise ValueError("no_observation exactly when nothing was "
                             "observed")
        if observed:
            indeterminate = self.evidence_consistency in (
                "json_type_unrecognized", "shape_disagreement",
                "value_json_malformed", "value_not_representable")
            if (self.value_presence == "indeterminate") != indeterminate:
                raise ValueError("indeterminate presence exactly when the "
                                 "evidence is not assessable")
            if not indeterminate and (
                    (self.value_presence == "explicit_null")
                    != (self.observed_shape == "null")):
                raise ValueError("explicit_null exactly for a null shape")

        # source-unit disclosure is independent of attachment
        if (self.source_unit_evidence == "not_evaluated") != (not observed):
            raise ValueError("source-unit evidence is disclosed exactly when "
                             "an observation exists")
        if observed:
            supplied = occurrence.declared_unit is not None
            if (self.source_unit_evidence == "present") != supplied:
                raise ValueError("source-unit evidence must state what the "
                                 "occurrence actually carried")
        return self


class VariableValueCompatibilityResult(_Frozen):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    as_of: UtcDatetime
    ruleset_version: Literal["vs001.1"]
    state: VariableStateResult                      # VM-001, VERBATIM
    specification_result: VariableSpecificationResult   # kernel, VERBATIM
    model_unit_specification: Literal["declared", "not_declared",
                                      "not_evaluated"]
    candidates: tuple[CandidateValueCompatibility, ...] = ()

    @model_validator(mode="after")
    def _result_consistent(self):
        specified = self.specification_result.status == "specified"
        if self.specification_result.anchor_id != self.variable_anchor_id:
            raise ValueError("the specification result must answer for the "
                             "requested variable")
        if self.specification_result.revision != self.state.model_revision:
            raise ValueError("one model revision governs membership and "
                             "specification")
        if (self.specification_result.status == "not_registered") != (
                self.state.model_membership == "not_registered"):
            raise ValueError("registration status must agree with model "
                             "membership")
        expected_unit = (
            "not_evaluated" if not specified else
            "declared" if self.specification_result.specification.unit.kind
            == "declared" else "not_declared")
        if self.model_unit_specification != expected_unit:
            raise ValueError("model_unit_specification must follow the "
                             "governing specification")

        if len(self.candidates) != len(self.state.candidates):
            raise ValueError("one compatibility entry per VM-001 candidate")
        conflicted = self.specification_result.status == "conflicted"
        for index, candidate in enumerate(self.candidates):
            if candidate.state_candidate != self.state.candidates[index]:
                raise ValueError("candidates must be carried verbatim and in "
                                 "the VM-001 order")
            if conflicted and (
                    candidate.value_shape_compatibility != "not_evaluated"
                    or candidate.declared_unit_lexeme_relation
                    != "not_evaluated"):
                raise ValueError("a conflicted specification produces no "
                                 "shape or unit verdict")
            if not specified and (
                    candidate.value_shape_compatibility != "not_evaluated"
                    or candidate.declared_unit_lexeme_relation
                    != "not_evaluated"):
                raise ValueError("no verdict without a governing "
                                 "specification")
            attached = candidate.state_candidate.attachment == "attached"
            if not attached and (
                    candidate.value_shape_compatibility != "not_evaluated"
                    or candidate.declared_unit_lexeme_relation
                    != "not_evaluated"):
                raise ValueError("no verdict for an unattached observation")
            if candidate.declared_unit_lexeme_relation != "not_evaluated" and (
                    self.model_unit_specification != "declared"
                    or candidate.source_unit_evidence != "present"):
                raise ValueError("a lexical relation needs a declared model "
                                 "unit and a supplied source unit")
            if candidate.value_shape_compatibility != "not_evaluated" and (
                    candidate.evidence_consistency != "consistent"):
                raise ValueError("a shape verdict needs internally "
                                 "consistent evidence")
        return self
