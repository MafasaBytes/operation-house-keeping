"""Validator-locked ES-001 semantic compatibility results."""

from datetime import UTC
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from backend.model_kernel import VariableSemanticsResult
from backend.observation_compatibility import CandidateValueCompatibility, VariableValueCompatibilityResult
from backend.source_interpretation import InterpretationRevision, PropertyInterpretationResult
from backend.system_identity import VARIABLE_ANCHOR_ID_PATTERN

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]

MeaningReason = Literal[
    "no_observation", "observation_not_attached", "evidence_not_assessable",
    "model_meaning_not_declared", "model_meaning_conflicted",
    "source_interpretation_not_declared", "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous", "source_interpretation_conflicted",
    "source_interpretation_retracted", "source_interpretation_inactive"]
UnitReason = Literal[
    "no_observation", "observation_not_attached", "evidence_not_assessable",
    "model_specification_not_available", "model_specification_conflicted",
    "model_unit_not_declared", "source_interpretation_not_declared",
    "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous", "source_interpretation_conflicted",
    "source_interpretation_retracted", "source_interpretation_inactive"]
LexemeReason = Literal[
    "no_observation", "observation_not_attached", "source_unit_absent",
    "unit_interpretation_not_positive"]
SemanticFinding = Literal[
    "declared_semantics_compatible", "observation_absent",
    "observation_not_attached", "evidence_inconsistent",
    "model_meaning_not_declared", "model_meaning_conflicted",
    "model_specification_not_available", "model_specification_conflicted",
    "model_unit_not_declared", "source_interpretation_not_declared",
    "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous", "source_interpretation_conflicted",
    "source_interpretation_retracted", "source_interpretation_inactive",
    "quantity_kind_mismatch",
    "observation_role_mismatch", "unit_identity_exact",
    "unit_identity_mismatch", "unit_identities_differ_conversion_not_attempted",
    "source_unit_absent_but_interpreted",
    "interpreted_unit_lexeme_differs_from_source"]


class SemanticCompatibilityError(Exception):
    def __init__(self, error_code, message):
        super().__init__(f"{error_code}: {message}")
        self.error_code, self.message = error_code, message


class SemanticCompatibilityConfigurationError(SemanticCompatibilityError):
    pass


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", revalidate_instances="always")


_INTERP_FINDING = {
    "source_interpretation_not_declared",
    "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous",
    "source_interpretation_conflicted",
    "source_interpretation_retracted",
    "source_interpretation_inactive",
}

_INTERP_REASON = {
    "not_declared": "source_interpretation_not_declared",
    "outside_applicability": "source_interpretation_inapplicable",
    "applicability_unknown": "source_interpretation_applicability_unknown",
    "ambiguous": "source_interpretation_ambiguous",
    "conflicted": "source_interpretation_conflicted",
    "retracted": "source_interpretation_retracted",
    "inactive": "source_interpretation_inactive",
}


def _common_reason(value_candidate):
    state = value_candidate.state_candidate
    if state.bound is None:
        return "no_observation"
    if state.attachment != "attached":
        return "observation_not_attached"
    if value_candidate.evidence_consistency not in (
            "consistent", "not_evaluated"):
        return "evidence_not_assessable"
    return None


def _meaning_assessment(value_candidate, model, interpreted, dimension):
    reason = _common_reason(value_candidate)
    if reason is None and model.status in ("not_declared", "not_registered"):
        reason = "model_meaning_not_declared"
    if reason is None and model.status == "conflicted":
        reason = "model_meaning_conflicted"
    if reason is None and interpreted.status != "interpreted":
        reason = _INTERP_REASON[interpreted.status]
    if reason is not None:
        return "not_evaluated", reason
    model_token = (model.declaration.declaration.quantity_kind
                   if dimension == "quantity_kind" else
                   model.declaration.declaration.observation_role)
    source_token = (interpreted.interpretation.quantity_kind
                    if dimension == "quantity_kind" else
                    interpreted.interpretation.observation_role)
    return ("token_identical" if model_token == source_token
            else "token_differs"), None


def _unit_assessment(value_candidate, specification, interpreted):
    reason = _common_reason(value_candidate)
    if reason is None and specification.status in (
            "not_specified", "not_registered"):
        reason = "model_specification_not_available"
    if reason is None and specification.status == "conflicted":
        reason = "model_specification_conflicted"
    if (reason is None and specification.specification.unit.kind
            == "not_declared"):
        reason = "model_unit_not_declared"
    if reason is None and interpreted.status != "interpreted":
        reason = _INTERP_REASON[interpreted.status]
    if reason is not None:
        return "not_evaluated", reason
    exact = (specification.specification.unit.unit
             == interpreted.interpretation.unit)
    return ("unit_identity_exact" if exact
            else "unit_identity_mismatch"), None


def _lexeme_assessment(value_candidate, interpreted):
    state = value_candidate.state_candidate
    if state.bound is None:
        return "not_evaluated", "no_observation"
    if state.attachment != "attached":
        return "not_evaluated", "observation_not_attached"
    if value_candidate.source_unit_evidence != "present":
        return "not_evaluated", "source_unit_absent"
    if interpreted.status != "interpreted":
        return "not_evaluated", "unit_interpretation_not_positive"
    occurrence = state.bound.observed.occurrence
    return ("lexeme_identical" if occurrence.declared_unit
            == interpreted.interpretation.unit.code else "lexeme_differs"), None


def authoritative_assessment(value_candidate, semantics, specification,
                             interpretation):
    """Derive every authoritative verdict/reason from carried facts."""
    quantity = _meaning_assessment(
        value_candidate, semantics.quantity_kind,
        None if interpretation is None else interpretation.quantity_kind,
        "quantity_kind")
    role = _meaning_assessment(
        value_candidate, semantics.observation_role,
        None if interpretation is None else interpretation.observation_role,
        "observation_role")
    unit = _unit_assessment(
        value_candidate, specification,
        None if interpretation is None else interpretation.unit)
    lexeme = _lexeme_assessment(
        value_candidate,
        None if interpretation is None else interpretation.unit)
    return {
        "quantity_kind_compatibility": quantity[0],
        "quantity_kind_not_evaluated_reason": quantity[1],
        "observation_role_compatibility": role[0],
        "observation_role_not_evaluated_reason": role[1],
        "unit_identity_compatibility": unit[0],
        "unit_identity_not_evaluated_reason": unit[1],
        "interpreted_unit_source_lexeme_relation": lexeme[0],
        "interpreted_unit_source_lexeme_not_evaluated_reason": lexeme[1],
    }


class CandidateSemanticCompatibility(_Frozen):
    value_candidate: CandidateValueCompatibility
    interpretation: PropertyInterpretationResult | None = None
    quantity_kind_compatibility: Literal["token_identical", "token_differs", "not_evaluated"]
    quantity_kind_not_evaluated_reason: MeaningReason | None = None
    observation_role_compatibility: Literal["token_identical", "token_differs", "not_evaluated"]
    observation_role_not_evaluated_reason: MeaningReason | None = None
    unit_identity_compatibility: Literal["unit_identity_exact", "unit_identity_mismatch", "not_evaluated"]
    unit_identity_not_evaluated_reason: UnitReason | None = None
    interpreted_unit_source_lexeme_relation: Literal["lexeme_identical", "lexeme_differs", "not_evaluated"]
    interpreted_unit_source_lexeme_not_evaluated_reason: LexemeReason | None = None
    semantic_findings: tuple[SemanticFinding, ...] = ()

    @model_validator(mode="after")
    def _locked(self):
        observed = self.value_candidate.state_candidate.bound is not None
        if observed != (self.interpretation is not None):
            raise ValueError("interpretation exists exactly when an observation exists")
        if observed:
            occurrence = self.value_candidate.state_candidate.bound.observed.occurrence
            if (self.interpretation.subject != self.value_candidate.state_candidate.subject
                    or self.interpretation.property != self.value_candidate.state_candidate.property
                    or self.interpretation.at != occurrence.received_at):
                raise ValueError("interpretation must resolve the exact candidate at received_at")
        pairs = (
            (self.quantity_kind_compatibility, self.quantity_kind_not_evaluated_reason),
            (self.observation_role_compatibility, self.observation_role_not_evaluated_reason),
            (self.unit_identity_compatibility, self.unit_identity_not_evaluated_reason),
            (self.interpreted_unit_source_lexeme_relation,
             self.interpreted_unit_source_lexeme_not_evaluated_reason))
        for verdict, reason in pairs:
            if (verdict == "not_evaluated") != (reason is not None):
                raise ValueError("a reason exists exactly for a non-evaluated verdict")
        dimensional = (
            (self.quantity_kind_compatibility, "quantity_kind"),
            (self.observation_role_compatibility, "observation_role"),
            (self.unit_identity_compatibility, "unit"),
        )
        for verdict, dimension in dimensional:
            resolution = (None if self.interpretation is None
                          else getattr(self.interpretation, dimension))
            if verdict != "not_evaluated" and (
                    resolution is None or resolution.status != "interpreted"):
                raise ValueError(
                    "a dimensional verdict requires a positive source "
                    "interpretation for that dimension")
        if self.interpreted_unit_source_lexeme_relation != "not_evaluated":
            if (self.interpretation is None
                    or self.interpretation.unit.status != "interpreted"
                    or self.value_candidate.source_unit_evidence != "present"):
                raise ValueError(
                    "a source-unit lexical verdict requires both a supplied "
                    "lexeme and a positive unit interpretation")
        expected = derive_semantic_findings(self)
        if self.semantic_findings != expected:
            raise ValueError("semantic_findings must be the total deterministic derivation")
        return self


def derive_semantic_findings(candidate: CandidateSemanticCompatibility):
    findings = set()
    value = candidate.value_candidate
    observed = value.state_candidate.bound is not None
    if not observed:
        findings.add("observation_absent")
    elif value.state_candidate.attachment != "attached":
        findings.add("observation_not_attached")
    if value.evidence_consistency not in ("consistent", "not_evaluated"):
        findings.add("evidence_inconsistent")
    for verdict, reason, mismatch in (
        (candidate.quantity_kind_compatibility,
         candidate.quantity_kind_not_evaluated_reason, "quantity_kind_mismatch"),
        (candidate.observation_role_compatibility,
         candidate.observation_role_not_evaluated_reason, "observation_role_mismatch")):
        if verdict == "token_differs":
            findings.add(mismatch)
        elif reason not in (None, "no_observation", "observation_not_attached",
                            "evidence_not_assessable"):
            findings.add(reason)
    if candidate.unit_identity_compatibility == "unit_identity_exact":
        findings.add("unit_identity_exact")
    elif candidate.unit_identity_compatibility == "unit_identity_mismatch":
        findings.update(("unit_identity_mismatch",
                         "unit_identities_differ_conversion_not_attempted"))
    elif candidate.unit_identity_not_evaluated_reason not in (
            None, "no_observation", "observation_not_attached",
            "evidence_not_assessable"):
        findings.add(candidate.unit_identity_not_evaluated_reason)
    if (observed and value.source_unit_evidence == "absent"
            and candidate.interpretation.unit.status == "interpreted"):
        findings.add("source_unit_absent_but_interpreted")
    if candidate.interpreted_unit_source_lexeme_relation == "lexeme_differs":
        findings.add("interpreted_unit_lexeme_differs_from_source")
    compatible = (
        observed and value.state_candidate.attachment == "attached"
        and value.evidence_consistency == "consistent"
        and candidate.quantity_kind_compatibility == "token_identical"
        and candidate.observation_role_compatibility == "token_identical"
        and candidate.unit_identity_compatibility == "unit_identity_exact")
    if compatible:
        findings.add("declared_semantics_compatible")
    return tuple(sorted(findings))


class VariableSemanticCompatibilityResult(_Frozen):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    as_of: UtcDatetime
    ruleset_version: Literal["es001.1"]
    value_compatibility: VariableValueCompatibilityResult
    semantics_result: VariableSemanticsResult
    interpretation_revision: InterpretationRevision
    candidates: tuple[CandidateSemanticCompatibility, ...] = ()

    @model_validator(mode="after")
    def _locked(self):
        if (self.semantics_result.anchor_id != self.variable_anchor_id
                or self.value_compatibility.variable_anchor_id != self.variable_anchor_id):
            raise ValueError("all results must answer for the requested variable")
        if self.semantics_result.revision != self.value_compatibility.state.model_revision:
            raise ValueError("one model revision governs membership and meaning")
        if self.as_of != self.value_compatibility.as_of:
            raise ValueError("as_of must equal the carried value-query cutoff")
        if len(self.candidates) != len(self.value_compatibility.candidates):
            raise ValueError("candidates must remain index-parallel")
        for index, candidate in enumerate(self.candidates):
            if candidate.value_candidate != self.value_compatibility.candidates[index]:
                raise ValueError("value candidates must be carried verbatim")
            if (candidate.interpretation is not None
                    and candidate.interpretation.revision != self.interpretation_revision):
                raise ValueError("one interpretation revision governs every candidate")
            expected = authoritative_assessment(
                candidate.value_candidate, self.semantics_result,
                self.value_compatibility.specification_result,
                candidate.interpretation)
            for field, value in expected.items():
                if getattr(candidate, field) != value:
                    raise ValueError(
                        "authoritative dimensional verdicts must follow "
                        "the carried model, interpretation, and evidence facts")
        return self
