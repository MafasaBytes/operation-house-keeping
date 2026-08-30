"""Exact documentation gate for the owner-resolved BH-001 Slice D rehearsal."""

import hashlib

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
SPEC_SHA256 = "520bf74823ab5e206bef8a56de9ba872ef8f3167451ad9c57e02a364532cd873"
SIGNATURE = """def mint_variable_anchor(
    *,
    entity_anchor_id: str,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> VariableAnchor:
    ..."""
PUBLIC_SURFACE = """BEHAVIOR_ANCHOR_ID_PATTERN
CONSTRAINT_ANCHOR_ID_PATTERN
ENTITY_ANCHOR_ID_PATTERN
PORT_ANCHOR_ID_PATTERN
VARIABLE_ANCHOR_ID_PATTERN
BehaviorAnchor
ConstraintAnchor
EntityAnchor
PortAnchor
VariableAnchor
mint_behavior_anchor
mint_constraint_anchor
mint_port_anchor
mint_variable_anchor"""


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
    assert "Historical stop status: blocked" in report
    assert "Current status: owner-resolved" in report


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


def test_specification_pins_exact_signature_surface_and_accepted_bytes():
    content = SPEC.read_bytes()
    text = content.decode("utf-8")
    assert SIGNATURE in text
    assert PUBLIC_SURFACE in text
    assert hashlib.sha256(content).hexdigest() == SPEC_SHA256
