"""Exact documentation gate for the owner-resolved BH-001 Slice D rehearsal."""

import hashlib

from pathlib import Path


ROOT = Path(__file__).parents[2]
SPEC = ROOT / "docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"
ADR = ROOT / "docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"
PLAN = ROOT / "docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md"
MATRIX = ROOT / "docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md"
DISCREPANCY = ROOT / "docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-report.md"
REHEARSAL_RESULTS = ROOT / "docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-results.md"
MANIFEST = ROOT / "docs/superpowers/reports/2026-08-30-bh001-slice-d-candidate-identities.json"
GLOBAL_MATRIX = ROOT / "docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md"

RESOLUTION = (
    "Owner resolution: add the narrowly scoped public "
    "`mint_variable_anchor()` API, commit it green before candidate allocation, "
    "then resume only the disposable pre-append rehearsal."
)
APPROVAL = (
    "Owner approval: the exact Slice D candidate identities, canonical records, "
    "32-record revision, and 122406-byte disclosure-artifact contract are approved; "
    "the bounded authoritative append and final verification are authorized."
)
REPORT_SHA256 = "0a559255359440f54f370eaf11645122089d4c0744e537c9446e20c12ffd4778"
MANIFEST_SHA256 = "8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07"
SPEC_SHA256 = "b6a8268780426aee7db6b0bce3d69ac092710bf41836d26d3606e9e4f9f4b652"
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


def test_exact_contract_is_owner_approved_before_authoritative_append():
    for path in (SPEC, ADR, PLAN, MATRIX):
        content = read(path)
        assert APPROVAL in " ".join(content.split()), path
    for path in (
        ROOT / "CLAUDE.md",
        ROOT / "backend/model_kernel/README.md",
        ROOT / "backend/behavior_evaluation/README.md",
        ROOT / "backend/system_identity/README.md",
        ROOT / "models/README.md",
        ROOT / "models/demo-printer/README.md",
        GLOBAL_MATRIX,
    ):
        content = read(path)
        assert "0905de0" in content, path
        assert "mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b" in content, path


def test_approved_gate_artifacts_and_fixed_outputs_are_exact():
    assert hashlib.sha256(REHEARSAL_RESULTS.read_bytes()).hexdigest() == REPORT_SHA256
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256
    manifest = read(MANIFEST)
    assert '"status":"non_authoritative_candidate"' in manifest
    assert "var_ab2d312466054c20b0ac764e9bc0114e" in manifest
    assert "bhv_80e21f1682e449ca9c65a5e2ee051ea0" in manifest
    for record_id in (
        "vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6",
        "brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e",
        "bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e",
    ):
        assert record_id in read(REHEARSAL_RESULTS)
    assert "4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3" in read(REHEARSAL_RESULTS)


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
