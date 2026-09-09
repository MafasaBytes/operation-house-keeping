"""FC-001 Slice B governing query and authoritative reconstruction gates."""

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fc001_slice_a_helpers import declaration, membership, world


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
    with pytest.raises(ValidationError, match="result is forged"):
        kernel.FlowOperatingCriterionResult.model_validate(payload)


def test_assertion_result_rejects_forged_lookup_and_indices():
    disclosed, positive = result()
    query = kernel.ModelQueries(disclosed.material.loaded())
    assertion = query.flow_operating_criterion_assertion(positive.record_id)
    payload = assertion.model_dump(mode="python")
    payload["positive_record_index"] += 1
    with pytest.raises(ValidationError, match="assertion is forged"):
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
