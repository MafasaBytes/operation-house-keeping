import pytest

from applications.bounded_decision_workflow.support_qualification import (
    SupportQualificationError,
    qualify_supplied_support,
)


H = {"kind": "nm.hypothesis.v1", "sha256": "h" * 64}
P = {"kind": "nm.procedure.v1", "sha256": "p" * 64}
D = {"kind": "nm.decoder.v1", "sha256": "d" * 64}
E = {"kind": "nm.evidence.v1", "sha256": "e" * 64}
C = {"scenario_label": "case", "as_of": "2026-01-01T00:00:00Z"}


def row(**changes):
    value = {
        "id": "S1", "hypothesis": H, "procedure": P, "context": C,
        "decoder": D, "evidence": E,
        "qualification": {"status": "qualified_conditional"},
        "coverage": "complete_envelope", "permits": [], "excludes": [],
        "exclusion_basis": [],
    }
    value.update(changes)
    return value


def qualify(rows, outcomes=("high", "low")):
    return qualify_supplied_support(
        rows, hypothesis=H, procedure=P, context=C, decoder=D, evidence=E,
        outcomes=outcomes)


def test_positive_support_does_not_infer_complement_exclusion():
    cells = qualify([row(permits=["high"])])
    assert [(c.outcome, c.relation) for c in cells] == [
        ("high", "supports"), ("low", "unavailable")]


def test_missing_and_conflicting_support_remain_unknown_without_pruning():
    missing = qualify([])
    assert all(cell.relation == "unavailable" for cell in missing)
    conflict = qualify([
        row(id="positive", permits=["high"]),
        row(id="gap", qualification={"status": "unavailable"}),
    ])
    assert conflict[0].relation == "unknown"
    assert conflict[1].relation == "unknown"


def test_unsupported_exclusion_is_not_a_valid_negative_cell():
    cells = qualify([row(excludes=["low"])])
    assert cells[1].relation == "unknown"
    assert cells[1].reasons == ("unsupported_exclusion",)
    valid = qualify([row(excludes=["low"], coverage="explicit_exclusions",
                          exclusion_basis=[{"kind": "nm.basis", "sha256": "b" * 64}])])
    assert valid[1].relation == "excludes"


def test_rehashed_semantic_substitution_fails_join_and_no_alias_is_made():
    substituted = {**P, "sha256": "q" * 64}
    with pytest.raises(SupportQualificationError) as error:
        qualify([row(procedure=substituted)])
    assert error.value.code == "SUPPORT_SUBJECT_MISMATCH"
    assert error.value.target == "procedure"
