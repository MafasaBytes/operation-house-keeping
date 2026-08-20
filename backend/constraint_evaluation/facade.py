"""CN-001 Slice B read-only constraint-evaluation facade.

Composition-only: one injected accepted ES-001 ``SemanticCompatibilityQueries``
instance, from whose exact public loaded model the Slice A
``ModelQueries`` is constructed — so a constraint-declaration /
membership / specification / semantics revision mismatch is
structurally impossible rather than merely detected. The facade owns no
store, performs no writes, selects no model revision by ``as_of``, and
propagates lower-layer typed errors unchanged.

The evaluator emits exactly three verdicts (``satisfied``, ``violated``,
``not_evaluated``) and refuses for exactly the reasons enumerated in
``NotEvaluatedReason``. It emits no severity, grade, normality, alarm,
recommendation, cause, diagnosis, or safety field, ever. ``violated``
asserts only that the admitted observed value does not satisfy the
declared numeric predicate.
"""

from datetime import UTC, datetime

from backend.constraint_evaluation.contracts import (
    ConstraintEvaluationResult, VariableConstraintEvaluationCollectionResult,
    derive_candidate_evaluation)
from backend.constraint_evaluation.errors import (
    ConstraintEvaluationConfigurationError, ConstraintEvaluationInputError)
from backend.model_kernel import ModelQueries
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN, VARIABLE_ANCHOR_ID_PATTERN)

_RULESET_VERSION = "cn001.1"


def _require_constraint_anchor_id(anchor_id: str) -> None:
    if not isinstance(anchor_id, str):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "constraint anchor id must be a string")
    import re as _re
    if not _re.fullmatch(CONSTRAINT_ANCHOR_ID_PATTERN, anchor_id):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "constraint anchor id must match the con_ pattern")


def _require_variable_anchor_id(anchor_id: str) -> None:
    if not isinstance(anchor_id, str):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "variable anchor id must be a string")
    import re as _re
    if not _re.fullmatch(VARIABLE_ANCHOR_ID_PATTERN, anchor_id):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "variable anchor id must match the var_ pattern")


def _normalize_early_as_of(as_of: datetime) -> datetime:
    """Validate cutoffs on paths that legitimately do not call ES."""
    if not isinstance(as_of, datetime):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "as_of must be a timezone-aware datetime")
    if as_of.tzinfo is None or as_of.tzinfo.utcoffset(as_of) is None:
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_NAIVE_AS_OF",
            "the query cutoff must be a timezone-aware datetime")
    return as_of.astimezone(UTC)


def _validate_early_selectors(entity_anchor_id, source) -> None:
    """Reject selectors that an early no-evidence return cannot delegate."""
    from backend.model_state import SourceSelector
    from backend.system_identity import ENTITY_ANCHOR_ID_PATTERN
    import re as _re
    if entity_anchor_id is not None and (
            not isinstance(entity_anchor_id, str)
            or not _re.fullmatch(ENTITY_ANCHOR_ID_PATTERN, entity_anchor_id)):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "entity anchor id must match the ent_ pattern")
    if source is not None and not isinstance(source, SourceSelector):
        raise ConstraintEvaluationInputError(
            "CONSTRAINT_EVALUATION_INPUT_INVALID",
            "an explicit source selector must be a SourceSelector")


class ConstraintEvaluationQueries:
    """Read-only evaluation of declared numeric constraints against the
    evidence attached to their target variable. Composition-only:
    constructed over one injected accepted ES-001 facade and the Slice A
    model query built over its exact loaded model."""

    def __init__(self, semantic: SemanticCompatibilityQueries) -> None:
        if not isinstance(semantic, SemanticCompatibilityQueries):
            raise ConstraintEvaluationConfigurationError(
                "CONSTRAINT_EVALUATION_INPUT_INVALID",
                "composition requires a SemanticCompatibilityQueries instance")
        self.semantic = semantic
        # Construct the Slice A ModelQueries over the SAME public loaded
        # model the injected ES facade uses, so a declaration / membership /
        # specification / semantics revision mismatch is unconstructible.
        self._model = ModelQueries(semantic.compatibility.state.model)

    # ----------------------------------------------------------- exact lookup

    def evaluate_constraint(
            self, constraint_anchor_id: str, *, as_of: datetime,
            entity_anchor_id: str | None = None,
            source: object | None = None,
    ) -> ConstraintEvaluationResult:
        """Evaluate one constraint against the evidence attached to its
        target variable. Request validation, including naive cutoffs and
        forged selectors, belongs to the accepted VS/VM/ES boundaries and
        their typed errors propagate unchanged. Absence, disagreement, and
        out-of-bounds are verdicts or statuses, never exceptions; the only
        exception that can surface is the numeric parity-breach integrity
        error."""
        _require_constraint_anchor_id(constraint_anchor_id)
        declaration = self._model.constraint_declaration(constraint_anchor_id)
        if declaration.status == "not_registered":
            as_of = _normalize_early_as_of(as_of)
            _validate_early_selectors(entity_anchor_id, source)
            return ConstraintEvaluationResult(
                constraint_anchor_id=constraint_anchor_id,
                declaration=declaration, as_of=as_of,
                ruleset_version=_RULESET_VERSION,
                semantic_compatibility=None, candidates=(),
                revision=declaration.revision)
        es = self.semantic.variable_semantic_compatibility(
            declaration.registration.variable_anchor_id, as_of=as_of,
            entity_anchor_id=entity_anchor_id, source=source)
        candidates = tuple(
            derive_candidate_evaluation(declaration, es, index)
            for index in range(len(es.candidates)))
        return ConstraintEvaluationResult(
            constraint_anchor_id=constraint_anchor_id,
            declaration=declaration, as_of=es.as_of,
            ruleset_version=_RULESET_VERSION,
            semantic_compatibility=es, candidates=candidates,
            revision=declaration.revision)

    # --------------------------------------------------- variable-scoped discovery

    def constraints_of_variable_evaluation(
            self, variable_anchor_id: str, *, as_of: datetime,
            entity_anchor_id: str | None = None,
            source: object | None = None,
    ) -> VariableConstraintEvaluationCollectionResult:
        """Discover and evaluate every constraint targeting one variable.
        The registered / not_registered distinction is preserved so an
        empty ``evaluations`` tuple is never ambiguous. The complete ES
        result for the variable is carried once and shared by every
        evaluation."""
        _require_variable_anchor_id(variable_anchor_id)
        collection = self._model.constraints_of_variable(variable_anchor_id)
        if collection.status == "not_registered":
            as_of = _normalize_early_as_of(as_of)
            _validate_early_selectors(entity_anchor_id, source)
            return VariableConstraintEvaluationCollectionResult(
                variable_anchor_id=variable_anchor_id, as_of=as_of,
                ruleset_version=_RULESET_VERSION, status="not_registered",
                constraint_collection=collection,
                semantic_compatibility=None, evaluations=(),
                revision=collection.revision)
        constraints = collection.constraints
        if not constraints:
            as_of = _normalize_early_as_of(as_of)
            _validate_early_selectors(entity_anchor_id, source)
            return VariableConstraintEvaluationCollectionResult(
                variable_anchor_id=variable_anchor_id, as_of=as_of,
                ruleset_version=_RULESET_VERSION, status="registered",
                constraint_collection=collection,
                semantic_compatibility=None, evaluations=(),
                revision=collection.revision)
        es = self.semantic.variable_semantic_compatibility(
            variable_anchor_id, as_of=as_of, entity_anchor_id=entity_anchor_id,
            source=source)
        evaluations = tuple(
            self._evaluation_for(declaration, es)
            for declaration in constraints)
        return VariableConstraintEvaluationCollectionResult(
            variable_anchor_id=variable_anchor_id, as_of=es.as_of,
            ruleset_version=_RULESET_VERSION, status="registered",
            constraint_collection=collection,
            semantic_compatibility=es, evaluations=evaluations,
            revision=collection.revision)

    def _evaluation_for(self, declaration, es) -> ConstraintEvaluationResult:
        """Build one evaluation over a pre-queried ES result. The ES result
        is shared (carried once) across every evaluation in a collection."""
        if declaration.status == "not_registered":
            # constraints_of_variable only returns registered constraints,
            # so this branch is unreachable in practice; keep it honest.
            return ConstraintEvaluationResult(
                constraint_anchor_id=declaration.constraint_anchor_id,
                declaration=declaration, as_of=es.as_of,
                ruleset_version=_RULESET_VERSION,
                semantic_compatibility=None, candidates=(),
                revision=declaration.revision)
        candidates = tuple(
            derive_candidate_evaluation(declaration, es, index)
            for index in range(len(es.candidates)))
        return ConstraintEvaluationResult(
            constraint_anchor_id=declaration.constraint_anchor_id,
            declaration=declaration, as_of=es.as_of,
            ruleset_version=_RULESET_VERSION,
            semantic_compatibility=es, candidates=candidates,
            revision=declaration.revision)
