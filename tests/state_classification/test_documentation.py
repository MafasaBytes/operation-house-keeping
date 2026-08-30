"""ST-001 Slice C documentation and owner-gate assertions."""

from pathlib import Path


STATUS = (
    "Slices A, B, and C are owner accepted. Slice D pre-append rehearsal is "
    "authorized; authoritative append remains prohibited.")

SLICE_C_HEAD = "f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_slice_c_status_and_slice_d_gate_are_exactly_documented():
    paths = (
        "CLAUDE.md",
        "backend/model_kernel/README.md",
        "backend/state_classification/README.md",
        "docs/adr/0016-explicit-state-identity-and-evidence-gated-"
        "classification.md",
        "docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-"
        "and-evidence-gated-classification-design.md",
        "docs/superpowers/plans/2026-08-31-st001-slice-c-implementation-"
        "plan.md",
        "docs/superpowers/plans/2026-08-31-st001-slice-c-adversarial-"
        "acceptance-matrix.md",
    )
    for path in paths:
        normalized = " ".join(read(path).split())
        assert STATUS in normalized, path
        assert SLICE_C_HEAD in normalized, path


def test_classifier_documentation_preserves_nonclaims_and_boundary():
    text = read("backend/state_classification/README.md")
    for phrase in (
        "owns no store",
        "independently selected latest evidence",
        "simultaneity and synchronization are not asserted",
        "does not independently authenticate uncaptured raw payload bytes",
        "defensive-unreachable",
        "ST-002",
    ):
        assert phrase in text


def test_authoritative_documents_retain_ending_markers():
    cases = (
        (
            "docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-"
            "and-evidence-gated-classification-design.md",
            "END OF ST-001 CORRECTED FINAL SYNTHESIS\n",
        ),
        (
            "docs/superpowers/plans/2026-08-31-st001-slice-c-implementation-"
            "plan.md",
            "END OF ST-001 SLICE C IMPLEMENTATION PLAN\n",
        ),
        (
            "docs/superpowers/plans/2026-08-31-st001-slice-c-adversarial-"
            "acceptance-matrix.md",
            "END OF ST-001 SLICE C ADVERSARIAL ACCEPTANCE MATRIX\n",
        ),
    )
    for path, marker in cases:
        assert read(path).endswith(marker), path
