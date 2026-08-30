"""BH-001 Slice C owner-resolution documentation gate.

These assertions must pass before evaluator production code begins.
"""

from pathlib import Path


SPEC = Path(
    "docs/superpowers/specs/"
    "2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"
)
PLAN = Path(
    "docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md"
)
MATRIX = Path(
    "docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md"
)
DISCREPANCY = Path(
    "docs/superpowers/reports/"
    "2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md"
)

REFUSALS = (
    "behavior_not_registered",
    "behavior_not_declared",
    "behavior_inactive",
    "behavior_conflicted",
    "participant_model_not_registered",
    "observation_absent",
    "observation_not_attached",
    "binding_not_positive",
    "evidence_not_assessable",
    "numeric_specification_not_available",
    "numeric_specification_conflicted",
    "model_quantity_kind_not_available",
    "model_observation_role_not_available",
    "model_unit_not_available",
    "source_semantics_not_admitted",
    "quantity_kind_lock_mismatch",
    "observation_role_lock_mismatch",
    "unit_lock_mismatch",
    "numeric_value_absent",
    "numeric_value_shape_mismatch",
    "numeric_value_out_of_bounds",
    "acquisition_cohort_mismatch",
)

EXPORTS = (
    "BehaviorEvaluationError",
    "BehaviorEvaluationConfigurationError",
    "BehaviorEvaluationInputError",
    "NumericParityBreachError",
    "BehaviorParticipantSource",
    "BehaviorEvaluationExecution",
    "BehaviorComputedRelation",
    "BehaviorParticipantAdmission",
    "BehaviorParticipantModelAdmission",
    "BehaviorParticipantObservationAvailability",
    "BehaviorParticipantAttachmentAdmission",
    "BehaviorParticipantSemanticAdmission",
    "BehaviorParticipantUnitAdmission",
    "BehaviorParticipantLockAdmission",
    "BehaviorParticipantNumericAdmission",
    "BehaviorAcquisitionCohortAdmission",
    "BehaviorEvaluationRefusalReason",
    "BehaviorEvaluationRefusal",
    "BehaviorEvaluationParticipantResult",
    "BehaviorEvaluationResult",
    "BehaviorEvaluationQueries",
)


def _block_after(text: str, marker: str) -> str:
    rest = text.split(marker, 1)[1]
    return rest.split("```", 1)[0].strip()


def test_exact_refusal_vocabulary_and_public_exports_are_pinned():
    spec = SPEC.read_text(encoding="utf-8")
    refusal_block = _block_after(
        spec, "ordered vocabulary is:\n\n```text\n")
    assert tuple(refusal_block.splitlines()) == REFUSALS

    export_block = _block_after(
        spec,
        "`backend.behavior_evaluation.__all__` is exactly this ordered list:\n\n"
        "```python\n",
    )
    parsed = tuple(
        line.strip().strip(',').strip('"')
        for line in export_block.splitlines()
        if line.strip().startswith('"')
    )
    assert parsed == EXPORTS


def test_error_tree_codes_and_cn_class_identity_are_normative():
    spec = SPEC.read_text(encoding="utf-8")
    assert "class BehaviorEvaluationError(Exception)" in spec
    assert (
        "class BehaviorEvaluationConfigurationError(BehaviorEvaluationError)"
        in spec
    )
    assert "class BehaviorEvaluationInputError(BehaviorEvaluationError)" in spec
    assert "BEHAVIOR_EVALUATION_CONFIGURATION_INVALID" in spec
    assert "BEHAVIOR_EVALUATION_INPUT_INVALID" in spec
    assert "re-exports the exact public CN `NumericParityBreachError` class" in spec
    assert "does not re-export the CN parser" in spec


def test_refusal_mapping_and_null_precedence_are_normative_everywhere():
    spec = SPEC.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    for token in (
        "numeric_specification_not_available",
        "model_unit_not_available",
        "numeric_value_absent",
        "numeric_value_shape_mismatch",
        'numeric_admission="not_evaluated"',
        'unit_admission="not_evaluated"',
    ):
        assert token in spec
        assert token in plan
    assert "Explicit null has precedence" in spec
    assert "Explicit null takes precedence" in plan
    assert "`numeric_value_absent` only" in matrix
    assert "no parser call" in matrix


def test_cohort_and_parser_scheduling_are_exact_and_staleness_is_disclosure():
    spec = SPEC.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    for text in (spec, plan):
        normalized = " ".join(text.split())
        assert "whenever both selected occurrences exist" in normalized
        assert "If either occurrence is absent" in normalized
        assert "canonical participant order" in normalized
        assert "model-unit" in normalized
        assert "typed parity failure" in normalized
    assert "Staleness is" in spec or "Staleness remains" in spec
    assert "does not hide" in spec
    assert "does not suppress" in plan


def test_carried_material_integrity_boundary_is_exact_and_testable():
    exact = (
        "BH authoritative result validation proves the internal coherence of "
        "the carried lower public results and every BH-derived field. It "
        "inherits, and does not independently re-prove, raw-source "
        "authenticity. A fully coherent lower-evidence content mutation "
        "accepted by the lower public contracts is outside BH's "
        "store-independent detection boundary."
    )
    spec = SPEC.read_text(encoding="utf-8")
    discrepancy = DISCREPANCY.read_text(encoding="utf-8")
    assert exact in " ".join(spec.split())
    assert "The owner accepted option 1" in discrepancy
    assert "executable limitation test" in spec
    assert "does not claim that `payload_checksum` authenticates" in spec
    assert "Content-bound lower occurrence authentication" in spec


def test_discrepancy_is_resolved_and_slice_d_remains_unstarted():
    spec = SPEC.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    discrepancy = DISCREPANCY.read_text(encoding="utf-8")
    claude = Path("CLAUDE.md").read_text(encoding="utf-8")
    adr = Path(
        "docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-"
        "evaluation.md"
    ).read_text(encoding="utf-8")

    assert (
        "all four contract questions are resolved"
        in " ".join(spec.lower().split())
    )
    assert "owner accepted and resolved" in plan
    assert "every blocker row below are owner resolved" in " ".join(
        matrix.split())
    assert "ALL FOUR QUESTIONS RESOLVED" in discrepancy
    assert "eedae19a9b2542958f44e66af7117a981c7faeef" in claude
    assert "all four contract\nquestions are resolved" in adr
    for text in (spec, plan, matrix):
        normalized = " ".join(text.split())
        assert "8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521" in normalized
    for text in (plan, matrix):
        normalized = " ".join(text.split())
        assert "Only the Slice D pre-append rehearsal gate is owner authorized" in normalized
        assert "the authoritative append has not started" in normalized
    assert "Slice D is implemented and adversarially reviewed" in " ".join(
        spec.split())
    assert "Slice D remains\nunstarted" in discrepancy
