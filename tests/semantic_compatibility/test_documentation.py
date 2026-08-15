"""Group-12 documentation is pinned to the governing ES-001 wording."""

from pathlib import Path

SPEC = Path(
    "docs/superpowers/specs/2026-08-13-es001-engineering-semantics-design.md")


def governing_limitations():
    text = SPEC.read_text()
    section = text.split(
        "## Limitations (verbatim in the module READMEs, asserted by test)\n\n",
        1)[1].split("\n## §14 Adjudication record", 1)[0]
    assert section.startswith("1.")
    assert "\n15." in section
    return section.strip()


def test_both_new_module_readmes_carry_every_limitation_verbatim():
    limitations = governing_limitations()
    for path in (
        Path("backend/source_interpretation/README.md"),
        Path("backend/semantic_compatibility/README.md"),
    ):
        assert limitations in path.read_text(), path


def test_touched_accepted_module_notes_preserve_layer_ownership():
    kernel = Path("backend/model_kernel/README.md").read_text()
    compatibility = Path(
        "backend/observation_compatibility/README.md").read_text()
    binding = Path("backend/identity_binding/README.md").read_text()
    assert "VariableSemanticDeclaration" in kernel
    assert "`rel_`, `vsp_`, and `vsm_`" in kernel
    assert "ES-001 composes this complete result unchanged" in compatibility
    assert "none of its accepted contracts" in compatibility
    assert "Identity binding remains the exclusive" in binding
    assert "`membership()` helper" in binding


def test_claude_status_is_not_applied_by_group_12():
    # The exact proposed paragraph is an owner checkpoint deliverable, not a
    # repository mutation until approval.
    text = Path("CLAUDE.md").read_text()
    assert "The current milestone is SN-001" in text
    assert "The current milestone is ES-001" not in text
