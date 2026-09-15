import hashlib
import json

import pytest

from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    PACKAGE_PATH, object_value, object_bytes,
)


def packages():
    old = PACKAGE_PATH.with_name(PACKAGE_PATH.stem + "-pre-s4-review-correction.json")
    return json.loads(old.read_bytes()), json.loads(PACKAGE_PATH.read_bytes())


def variant(p, name):
    return next(v for c in p["acceptance_cases"] for v in c["variants"] if v["variant_id"] == name)


RED_CASES = ["POL-3", "POL-4", "REV-1-target", "current_condition",
             "P-applicability", "P-support", "E-aH", "PC-isolation", "T-aH", "I-aH", "prior_argument"]


@pytest.mark.parametrize("case", RED_CASES)
def test_original_eleven_red_assertions_have_corrected_twins(case):
    old, new = packages()
    def passes(p):
        v = variant(p, case if case in RED_CASES[:3] else "NUM-1-endpoint")
        r = object_value(p, v["expected"]["result_ref"])["reevaluation"]
        if case in RED_CASES[:3]:
            return r["disposition"] != "not_applicable_no_prior"
        if case == "current_condition":
            return "snapshot" in r["decision_rows"][0]["depends_on"]
        if case == "prior_argument":
            return "--compare-to" in variant(p, "REV-1-incompatible")["input"]["argv"]
        row = next(x for x in r["decision_rows"] if x["decision_id"] == "raw:H_H:aH")
        return "premise:" + case in row["depends_on"]
    assert not passes(old), "historical red evidence lost"
    assert passes(new)


def test_exact_authorized_differences_and_complete_recovery():
    old, new = packages()
    for key, entry in old["objects"].items():
        assert new["objects"][key] == entry
    for key in new["objects"]:
        object_bytes(new, key)
    for c in new["s4_fixture_correction"]["object_changes"]:
        a, b = object_value(old, c["old_result"]), object_value(new, c["new_result"])
        del a["reevaluation"]; del b["reevaluation"]
        assert a == b
        a, b = object_value(old, c["old_trace"]), object_value(new, c["new_trace"])
        del a["decision_rows"]; del b["decision_rows"]
        assert a == b
    for kind, sha in [("package", "df9766b51dea3339b9b2096ab3a96ea75ff01b130b6eb913da86d337c5d7cb1e"),
                       ("manifest", "9b9effe6809bb49ad2f0a7cd1096eeef688ef17dee1a87f44b0832af1e478de9")]:
        path = PACKAGE_PATH.with_name(f"2026-09-15-bounded-decision-workflow-candidate-{kind}-pre-s4-review-correction.json")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
    assert len(new["acceptance_cases"]) == 27
    assert sum(len(c["variants"]) for c in new["acceptance_cases"]) == 72


@pytest.mark.parametrize("name,required,changed,equal", [("POL-3", 1, 1, 0), ("POL-4", 13, 7, 6), ("REV-1-target", 13, 7, 6)])
def test_independent_review_counts_and_no_prior_control(name, required, changed, equal):
    _, p = packages()
    v = variant(p, name)
    rows = object_value(p, v["expected"]["result_ref"])["reevaluation"]["decision_rows"]
    assert len(rows) == 22
    assert sum(r["reevaluation"] == "required" for r in rows) == required
    assert sum(r["value_changed"] for r in rows) == changed
    assert sum(r["equal_after_reevaluation"] is True for r in rows) == equal
    assert all(not r["value_changed"] for r in rows if r["decision_id"].startswith("raw:"))
    no = variant(p, "REV-1-omitted-prior")
    assert "--compare-to" not in no["input"]["argv"]
    assert object_value(p, no["expected"]["result_ref"])["reevaluation"]["disposition"] == "not_applicable_no_prior"


def test_every_supplied_prior_has_comparison_expectations_and_preserved_sweep_history():
    _, p = packages()
    historical = PACKAGE_PATH.with_name("2026-09-15-bounded-decision-workflow-candidate-package-pre-s4-complete-sweep.json")
    raw = historical.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "6af90f315b7f1c407a30e57d526d609c650dfbd10bb2489c87087a6f596a8a63"
    old = json.loads(raw)
    for k, entry in old["objects"].items(): assert p["objects"][k] == entry
    for c in p["s4_complete_sweep_correction"]["object_changes"]:
        before, after = object_value(old, c["old_result"]), object_value(p, c["new_result"])
        assert before["reevaluation"]["disposition"] == "not_applicable_no_prior"
        assert all(r["reevaluation"] == "required" and r["value_changed"] for r in after["reevaluation"]["decision_rows"])
        del before["reevaluation"]; del after["reevaluation"]
        assert before == after
        before, after = object_value(old, c["old_trace"]), object_value(p, c["new_trace"])
        del before["decision_rows"]; del after["decision_rows"]
        assert before == after
    for case in p["acceptance_cases"]:
        for v in case["variants"]:
            if "result_ref" in v["expected"] and "request_ref" in v["input"]:
                expected = "compared" if "--compare-to" in v["input"]["argv"] else "not_applicable_no_prior"
                assert object_value(p, v["expected"]["result_ref"])["reevaluation"]["disposition"] == expected
