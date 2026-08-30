"""ST-001 Slice B exact documentation and owner-gate status."""

from pathlib import Path


STATUS = (
    "Slice B is owner accepted at "
    "`23eca10a52c0124d22b4e90d80bef952ef5f9381`.")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_slice_b_acceptance_and_slice_c_authorization_are_pinned():
    paths = (
        "CLAUDE.md",
        "backend/model_kernel/README.md",
        "docs/adr/0016-explicit-state-identity-and-evidence-gated-"
        "classification.md",
        "docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-"
        "and-evidence-gated-classification-design.md",
        "docs/superpowers/plans/2026-08-30-st001-slice-b-implementation-"
        "plan.md",
        "docs/superpowers/plans/2026-08-30-st001-slice-b-adversarial-"
        "acceptance-matrix.md",
    )
    for path in paths:
        normalized = " ".join(read(path).split())
        assert STATUS in normalized, path
        assert "Slice C" in normalized and "authorized" in normalized
        assert "Slice D" in normalized and "unauthorized" in normalized


def test_kernel_documentation_pins_exact_slice_b_surface_and_non_inference():
    documentation = read("backend/model_kernel/README.md")
    for method in (
            "`state()`", "`state_declaration()`", "`states_of_entity()`",
            "`state_assertion()`"):
        assert method in documentation
    assert "carry `ModelQueryMaterial` exactly once" in documentation
    assert "without a store or filesystem" in documentation
    assert "No query infers state" in documentation
    assert "zero SRG, STD, or STW records" in documentation


def test_slice_b_documents_retain_their_exact_ending_markers():
    cases = (
        (
            "docs/superpowers/plans/2026-08-30-st001-slice-b-"
            "implementation-plan.md",
            "END OF ST-001 SLICE B IMPLEMENTATION PLAN\n",
        ),
        (
            "docs/superpowers/plans/2026-08-30-st001-slice-b-adversarial-"
            "acceptance-matrix.md",
            "END OF ST-001 SLICE B ADVERSARIAL ACCEPTANCE MATRIX\n",
        ),
        (
            "docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-"
            "and-evidence-gated-classification-design.md",
            "END OF ST-001 CORRECTED FINAL SYNTHESIS\n",
        ),
    )
    for path, marker in cases:
        assert read(path).endswith(marker), path
