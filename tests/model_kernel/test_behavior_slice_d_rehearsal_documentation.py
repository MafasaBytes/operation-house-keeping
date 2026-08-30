"""Exact documentation gate for the owner-resolved BH-001 Slice D rehearsal."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SPEC = ROOT / "docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"
ADR = ROOT / "docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"
PLAN = ROOT / "docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md"
MATRIX = ROOT / "docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md"
DISCREPANCY = ROOT / "docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-report.md"

RESOLUTION = (
    "Owner resolution: add the narrowly scoped public "
    "`mint_variable_anchor()` API, commit it green before candidate allocation, "
    "then resume only the disposable pre-append rehearsal."
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_owner_resolution_is_pinned_in_every_authoritative_slice_d_document():
    for path in (SPEC, ADR, PLAN, MATRIX, DISCREPANCY):
        assert RESOLUTION in read(path), path


def test_discrepancy_history_is_preserved_and_marked_resolved():
    report = read(DISCREPANCY)
    assert "blocked before candidate generation" in report
    assert "no public `mint_variable_anchor()`" in report
    assert "## 15. Owner resolution" in report
    assert "Status: resolved by owner decision; rehearsal resumption authorized" in report


def test_minter_scope_and_candidate_freeze_order_are_exact():
    for path in (SPEC, PLAN, MATRIX):
        content = read(path)
        assert "`mint_variable_anchor` after `mint_port_anchor`" in content
        assert "one UUID4 using standard-library `uuid4().hex`" in content
        assert "No candidate may be minted before the minter commit is green." in content
        assert "invoke each public minter exactly once" in content
        assert "never invoke either minter again" in content
        assert "non_authoritative_candidate" in content


def test_authoritative_append_remains_prohibited():
    for path in (SPEC, ADR, PLAN, MATRIX, ROOT / "CLAUDE.md"):
        content = read(path)
        assert "The authoritative append remains prohibited" in content


def test_plan_and_matrix_have_exact_markers():
    assert read(PLAN).endswith("END OF BH-001 SLICE D PRE-APPEND REHEARSAL PLAN\n")
    assert read(MATRIX).endswith(
        "END OF BH-001 SLICE D PRE-APPEND ACCEPTANCE MATRIX\n")
