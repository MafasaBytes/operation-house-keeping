"""FC-001 Slice B governing query and authoritative reconstruction gates."""

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fc001_slice_a_helpers import (
    declaration, membership, replace, world,
)


def result():
    records, witness, crg, vcn = world()
    positive = declaration(witness, crg, vcn)
    loaded = validate_record_collection("fc001-slice-b", membership(*records, positive))
    query = kernel.ModelQueries(loaded)
    return query.flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context, witness.orientation), positive


def test_exact_public_contract_and_complete_support_disclosure():
    disclosed, _ = result()
    assert disclosed.subject.conclusion == "applicable"
    group = disclosed.subject.body_groups[0]
    assert tuple(row.support_kind for row in group.support_rows) == (
        "frg", "vrg", "prg", "fld", "vpa", "vsm", "crg", "vcn",
        "pcn", "pif", "pif")
    assert group.matching_fm_current_indices
    assert group.reasons == ()


@pytest.mark.parametrize("field,value", [
    ("conclusion", "inapplicable"),
    ("reasons", ("fm_body_not_current",)),
    ("governing_body_group_index", None),
])
def test_outer_result_rejects_forged_conclusions(field, value):
    disclosed, _ = result()
    payload = disclosed.model_dump(mode="python")
    payload["subject"][field] = value
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate(payload)


def test_assertion_result_rejects_forged_lookup_and_indices():
    disclosed, positive = result()
    query = kernel.ModelQueries(disclosed.material.loaded())
    assertion = query.flow_operating_criterion_assertion(positive.record_id)
    payload = assertion.model_dump(mode="python")
    payload["positive_record_index"] += 1
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionAssertionResult.model_validate(payload)


def test_complete_historical_absence_is_structured():
    records, witness, _, _ = world()
    loaded = validate_record_collection("fc001-absence", membership(*records))
    disclosed = kernel.ModelQueries(loaded).flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context, witness.orientation)
    assert disclosed.subject.conclusion == "not_declared"
    assert disclosed.subject.reasons == ("fc_not_declared",)
    assert disclosed.subject.roots == disclosed.subject.body_groups == ()


def test_selector_and_assertion_id_fail_with_fc_query_code():
    disclosed, _ = result()
    query = kernel.ModelQueries(disclosed.material.loaded())
    for call in (
        lambda: query.flow_operating_criterion(1, "var_" + "1" * 32,
                                               "prt_" + "1" * 32,
                                               {"kind": "view_independent"}, "aligned"),
        lambda: query.flow_operating_criterion_assertion("fcd_bad"),
    ):
        with pytest.raises(kernel.ModelQueryError) as error:
            call()
        assert error.value.error_code == "MODEL_FLOW_CRITERION_QUERY_INVALID"


def test_same_root_different_body_fork_is_not_cross_root_disagreement():
    records, witness, crg, old_vcn = world()
    root = declaration(witness, crg, old_vcn, note="root")
    renewed_vcn = replace(old_vcn, supersedes=(old_vcn.record_id,))
    left = declaration(
        witness, crg, old_vcn, supersedes=(root.record_id,), note="left")
    right = declaration(
        witness, crg, renewed_vcn, supersedes=(root.record_id,), note="right")
    loaded = validate_record_collection(
        "fc001-same-root-fork",
        membership(*records, renewed_vcn, root, left, right))
    disclosed = kernel.ModelQueries(loaded).flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context,
        witness.orientation)
    assert disclosed.subject.conclusion == "conflicted"
    assert disclosed.subject.reasons == ("fc_same_root_conflict",)


def test_independent_equal_bodies_corroborate_and_different_bodies_disagree():
    records, witness, crg, old_vcn = world()
    first = declaration(witness, crg, old_vcn, note="first root")
    corroborating = declaration(
        witness, crg, old_vcn, note="corroborating root")
    equal = validate_record_collection(
        "fc001-corroboration",
        membership(*records, first, corroborating))
    query = lambda loaded: kernel.ModelQueries(loaded).flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context,
        witness.orientation)
    disclosed = query(equal)
    assert disclosed.subject.conclusion == "applicable"
    assert disclosed.subject.reasons == ()
    assert len(disclosed.subject.roots) == 2
    assert len(disclosed.subject.body_groups) == 1

    renewed_vcn = replace(old_vcn, supersedes=(old_vcn.record_id,))
    different = declaration(
        witness, crg, renewed_vcn, note="different-body root")
    disagreed = validate_record_collection(
        "fc001-disagreement",
        membership(*records, renewed_vcn, first, different))
    disclosed = query(disagreed)
    assert disclosed.subject.conclusion == "disagreed"
    assert disclosed.subject.reasons == ("fc_cross_root_disagreement",)
    assert disclosed.subject.governing_body_group_index is None


def test_same_root_conflict_and_independent_disagreement_can_coexist():
    records, witness, crg, old_vcn = world()
    root = declaration(witness, crg, old_vcn, note="fork root")
    renewed_vcn = replace(old_vcn, supersedes=(old_vcn.record_id,))
    old_tip = declaration(
        witness, crg, old_vcn, supersedes=(root.record_id,), note="old tip")
    new_tip = declaration(
        witness, crg, renewed_vcn, supersedes=(root.record_id,),
        note="new tip")
    independent = declaration(
        witness, crg, old_vcn, note="independent old-body root")
    loaded = validate_record_collection(
        "fc001-conflict-and-disagreement",
        membership(
            *records, renewed_vcn, root, old_tip, new_tip, independent))
    disclosed = kernel.ModelQueries(loaded).flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context,
        witness.orientation)
    assert disclosed.subject.conclusion == "conflicted"
    assert disclosed.subject.reasons == (
        "fc_same_root_conflict", "fc_cross_root_disagreement")


def test_outer_result_rejects_hostile_model_before_serializer_callback():
    disclosed, _ = result()
    calls = []

    class HostileSubject(kernel.FlowOperatingCriterionSubjectResult):
        def model_dump(self, *args, **kwargs):
            calls.append("model_dump")
            raise AssertionError("hostile serializer called")

    hostile = HostileSubject.model_construct(**vars(disclosed.subject))
    payload = disclosed.model_dump(mode="python")
    payload["subject"] = hostile
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate(payload)
    assert calls == []

    class HostileObject:
        def __getattribute__(self, name):
            calls.append(name)
            raise AssertionError("hostile attribute callback called")

    payload = disclosed.model_dump(mode="python")
    payload["subject"] = HostileObject()
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate(payload)
    assert calls == []


def test_outer_result_json_rejects_duplicates_and_raw_limit_before_validation():
    disclosed, _ = result()
    material = disclosed.material.model_dump_json()
    subject = disclosed.subject.model_dump_json()
    duplicate = (
        '{"material":' + material + ',"subject":' + subject
        + ',"subject":' + subject + "}")
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate_json(duplicate)
    oversized = disclosed.model_dump_json() + " " * (
        4_194_305 - len(disclosed.model_dump_json()))
    with pytest.raises(ValidationError, match="FC_RESULT_LIMIT_EXCEEDED"):
        kernel.FlowOperatingCriterionResult.model_validate_json(oversized)


def test_outer_result_errors_are_fixed_and_value_free():
    disclosed, _ = result()
    assert kernel.FlowOperatingCriterionResult.model_validate_json(
        disclosed.model_dump_json()) == disclosed
    payload = disclosed.model_dump(mode="python")
    payload["subject"]["conclusion"] = "SENSITIVE_PROBE"
    with pytest.raises(ValidationError) as caught:
        kernel.FlowOperatingCriterionResult.model_validate(payload)
    rendered = str(caught.value)
    assert "FC_RESULT_INVALID" in rendered
    assert "SENSITIVE_PROBE" not in rendered
    forged = disclosed.model_copy(update={
        "subject": disclosed.subject.model_copy(update={
            "conclusion": "inapplicable",
            "reasons": ("fm_body_not_current",),
        }),
    })
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate(forged)
    with pytest.raises(ValidationError, match="FC_RESULT_INVALID"):
        kernel.FlowOperatingCriterionResult.model_validate_strings(payload)
