"""BH-001 Slice C status and limitation documentation is exact."""

from pathlib import Path


STATUS = (
    "BH-001 Slices A and B are owner accepted. Slice C is implemented and "
    "adversarially reviewed; awaiting owner acceptance. Slice D has not "
    "started."
)
LIMITATION = (
    "BH authoritative result validation proves the internal coherence of the "
    "carried lower public results and every BH-derived field. It inherits, "
    "and does not independently re-prove, raw-source authenticity. A fully "
    "coherent lower-evidence content mutation accepted by the lower public "
    "contracts is outside BH's store-independent detection boundary."
)
FILES = (
    Path("CLAUDE.md"),
    Path("backend/model_kernel/README.md"),
    Path("backend/behavior_evaluation/README.md"),
    Path("docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"),
    Path("docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"),
    Path("docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md"),
    Path("docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md"),
)


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_exact_slice_status_is_recorded_everywhere():
    for path in FILES:
        assert STATUS in _normalized(path), path


def test_authority_limitation_is_normative_in_spec_and_evaluator_docs():
    for path in (FILES[2], FILES[4]):
        assert LIMITATION in _normalized(path), path


def test_no_operational_implication_and_slice_d_remains_unstarted():
    evaluator = _normalized(FILES[2])
    assert "not claims about validity, correctness, causality, flow, control, safety, health, simultaneity, or continuing real-machine behavior" in evaluator
    assert "no committed behavior fixture or demonstration artifact exists" in evaluator.lower()
