"""ST-001 Slice D documentation and final owner-gate assertions."""

from pathlib import Path


STATUS = (
    "ST-001 Slices A-D are implemented and verified; Slice D final owner "
    "acceptance is pending.")

SLICE_C_HEAD = "f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6"
FINAL_REVISION = (
    "mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_slice_d_status_and_final_gate_are_exactly_documented():
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
        assert FINAL_REVISION in normalized, path


def test_demo_documentation_pins_the_exact_candidate_and_nonclaims():
    text = " ".join(read("models/demo-printer/README.md").split())
    for phrase in (
        FINAL_REVISION,
        "sta_ec739d80d5a843d28a91f4cf96de3883",
        "srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a",
        "std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0",
        "temporal alignment remains `not_asserted`",
        "does not persist it as state truth",
        "final owner acceptance remains pending",
    ):
        assert phrase in text


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
