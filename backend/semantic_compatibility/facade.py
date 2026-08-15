"""Read-only ES-001 composition facade."""

from datetime import datetime

from backend.model_kernel import ModelQueries
from backend.model_state import SourceSelector
from backend.observation_compatibility import ObservationCompatibilityQueries
from backend.semantic_compatibility.contracts import (
    CandidateSemanticCompatibility, SemanticCompatibilityConfigurationError,
    VariableSemanticCompatibilityResult, authoritative_assessment,
    derive_semantic_findings)
from backend.source_interpretation import InterpretationResolver

class SemanticCompatibilityQueries:
    def __init__(self, compatibility: ObservationCompatibilityQueries,
                 interpretations: InterpretationResolver) -> None:
        if (not isinstance(compatibility, ObservationCompatibilityQueries)
                or not isinstance(interpretations, InterpretationResolver)):
            raise SemanticCompatibilityConfigurationError(
                "SEMANTIC_COMPATIBILITY_INPUT_INVALID",
                "composition requires compatibility and interpretation queries")
        self.compatibility = compatibility
        self.interpretations = interpretations

    def variable_semantic_compatibility(
            self, variable_anchor_id: str, *, as_of: datetime,
            entity_anchor_id: str | None = None,
            source: SourceSelector | None = None,
    ) -> VariableSemanticCompatibilityResult:
        value = self.compatibility.variable_value_compatibility(
            variable_anchor_id, as_of=as_of, entity_anchor_id=entity_anchor_id,
            source=source)
        semantics = ModelQueries(
            self.compatibility.state.model).variable_semantics(variable_anchor_id)
        candidates = tuple(self._candidate(candidate, semantics, value)
                           for candidate in value.candidates)
        return VariableSemanticCompatibilityResult(
            variable_anchor_id=value.variable_anchor_id, as_of=value.as_of,
            ruleset_version="es001.1", value_compatibility=value,
            semantics_result=semantics,
            interpretation_revision=self.interpretations.loaded.revision,
            candidates=candidates)

    def _candidate(self, value_candidate, semantics, value_result):
        state = value_candidate.state_candidate
        observed = state.bound is not None
        interpretation = None
        if observed:
            occurrence = state.bound.observed.occurrence
            interpretation = self.interpretations.resolve_property_interpretations(
                state.subject, state.property, at=occurrence.received_at)
        fields = dict(value_candidate=value_candidate,
                      interpretation=interpretation)
        fields.update(authoritative_assessment(
            value_candidate, semantics, value_result.specification_result,
            interpretation))
        draft = CandidateSemanticCompatibility.model_construct(
            **fields, semantic_findings=())
        return CandidateSemanticCompatibility(
            **fields, semantic_findings=derive_semantic_findings(draft))
