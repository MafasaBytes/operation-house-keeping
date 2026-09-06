"""C1 contract, reconstruction, and result-invariant acceptance tests."""

from __future__ import annotations

from typing import get_args

import pytest
from pydantic import ValidationError

from tests.evidence_alignment.helpers import alignment_api, align, build_world


COVERED_ROWS = {
    "C01", "C02", "C03", "C04", "C05", "C16", "C18", "C19", "C20",
    "C21", "C22", "C30", "C31", "C32", "C33", "C38",
}


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    return build_world(tmp_path_factory.mktemp("alignment-contracts"))


def test_c1_matrix_mapping_is_complete_with_other_modules():
    from tests.evidence_alignment.test_derivation import COVERED_ROWS as derivation
    from tests.evidence_alignment.test_isolation import COVERED_ROWS as isolation
    assert COVERED_ROWS | derivation | isolation == {
        f"C{index:02d}" for index in range(1, 39)
    }


def test_c01_exact_field_and_literal_order():
    api = alignment_api()
    assert tuple(api["OperationalEvidenceAlignmentRequest"].model_fields) == (
        "schema_version", "selection", "compatibility",
        "expected_snapshot_fingerprint",
    )
    assert tuple(api["OperationalEvidenceAlignmentResult"].model_fields) == (
        "schema_version", "request", "status", "reason",
        "snapshot_validation", "evidence_selection_status",
        "evidence_coverage_completeness", "expected_fingerprint_relation",
        "cutoff_relation", "scope_relation", "endpoint_closure",
        "selected_occurrence_role", "occurrence_relation",
        "mismatched_occurrence_fields", "aligned_candidate_index",
        "candidate_attachment", "variable_anchor_id", "model_revision_id",
        "binding_revision_id",
    )
    assert get_args(api["OperationalEvidenceAlignmentStatus"]) == (
        "aligned_with_complete_evidence",
        "aligned_with_incomplete_evidence",
        "not_aligned",
        "not_evaluated",
    )
    assert get_args(api["OperationalEvidenceAlignmentReason"]) == (
        "selection_refused",
        "snapshot_fingerprint_mismatched",
        "no_selected_observation",
        "cutoff_differs",
        "scope_differs",
        "consumer_observation_absent",
        "occurrence_content_mismatch",
        "occurrence_absent_from_consumer_result",
        "multiple_matching_candidates",
    )
    assert get_args(api["EvidenceAlignmentQueryErrorCode"]) == (
        "ALIGNMENT_REQUEST_INVALID",
    )
    for name in (
        "OperationalEvidenceAlignmentRequest",
        "OperationalEvidenceAlignmentResult",
    ):
        config = api[name].model_config
        assert config["frozen"] is True
        assert config["extra"] == "forbid"
        assert config["revalidate_instances"] == "always"


def test_c30_c31_hostile_and_forged_request_content_is_typed(world):
    api = alignment_api()
    valid = api["OperationalEvidenceAlignmentRequest"](
        schema_version="1", selection=world.selection,
        compatibility=world.compatibility,
        expected_snapshot_fingerprint=None,
    )
    hostile = valid.model_dump(mode="python", warnings=False)
    hostile["unexpected"] = "extra"
    with pytest.raises(api["EvidenceAlignmentQueryError"]) as error:
        api["align"](hostile)
    assert error.value.error_code == "ALIGNMENT_REQUEST_INVALID"

    forged = valid.model_copy(update={"selection": object()})
    with pytest.raises(api["EvidenceAlignmentQueryError"]):
        api["align"](forged)

    cycle = valid.model_dump(mode="python", warnings=False)
    cycle["selection"] = cycle
    with pytest.raises(api["EvidenceAlignmentQueryError"]):
        api["align"](cycle)


def test_c32_hostile_expected_fingerprint_cannot_manufacture_match(world):
    api = alignment_api()

    class ForgedFingerprint(str):
        def __eq__(self, other):
            return True

        __hash__ = str.__hash__

    wrong = ForgedFingerprint("sha256:" + "0" * 64)
    request = {
        "schema_version": "1",
        "selection": world.selection,
        "compatibility": world.compatibility,
        "expected_snapshot_fingerprint": wrong,
    }
    with pytest.raises(api["EvidenceAlignmentQueryError"]) as error:
        api["align"](request)
    assert error.value.error_code == "ALIGNMENT_REQUEST_INVALID"


def test_adversarial_boolean_nested_sweep_position_rejects(world):
    api = alignment_api()
    payload = {
        "schema_version": "1",
        "selection": world.selection.model_dump(mode="python", warnings=False),
        "compatibility": world.compatibility.model_dump(
            mode="python", warnings=False),
        "expected_snapshot_fingerprint": None,
    }
    payload["compatibility"]["state"]["candidates"][0]["bound"][
        "observed"]["occurrence"]["sweep_position"] = True
    payload["compatibility"]["candidates"][0]["state_candidate"]["bound"][
        "observed"]["occurrence"]["sweep_position"] = True
    with pytest.raises(api["EvidenceAlignmentQueryError"]) as error:
        api["align"](payload)
    assert error.value.error_code == "ALIGNMENT_REQUEST_INVALID"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aligned_candidate_index", True),
        ("aligned_candidate_index", -1),
        ("model_revision_id", "stale"),
        ("candidate_attachment", "not_applicable"),
        ("mismatched_occurrence_fields", ("z", "a")),
        ("mismatched_occurrence_fields", tuple(f"f{i}" for i in range(21))),
    ],
)
def test_c31_c33_stale_or_non_strict_result_claims_reject(world, field, value):
    api = alignment_api()
    result = align(world)
    payload = result.model_dump(mode="python", warnings=False)
    payload[field] = value
    with pytest.raises(ValidationError):
        api["OperationalEvidenceAlignmentResult"].model_validate(payload)


def test_c22_validation_is_carried_once_and_not_in_request(world):
    result = align(world)
    payload = result.model_dump(mode="python", warnings=False)
    assert "snapshot_validation" not in payload["request"]
    assert "store_revalidation" not in payload["request"]
    assert "store_revalidation_status" not in payload
    assert "store_revalidation_relation" not in payload
    assert payload["snapshot_validation"]["source_bytes"] == "not_rechecked"
    assert payload["snapshot_validation"]["temporal_store_membership"] == (
        "not_rechecked")


def test_c38_exact_error_surface_and_safe_message():
    api = alignment_api()
    error = api["EvidenceAlignmentQueryError"](
        "ALIGNMENT_REQUEST_INVALID", "alignment request is invalid")
    assert type(error).__mro__[:3] == (
        api["EvidenceAlignmentQueryError"], api["EvidenceAlignmentError"],
        Exception,
    )
    assert vars(error) == {
        "error_code": "ALIGNMENT_REQUEST_INVALID",
        "message": "alignment request is invalid",
    }
    assert str(error) == (
        "ALIGNMENT_REQUEST_INVALID: alignment request is invalid")
    for message in ("", "/private/location", "password=secret", "x" * 301):
        with pytest.raises(ValueError):
            api["EvidenceAlignmentQueryError"](
                "ALIGNMENT_REQUEST_INVALID", message)
    with pytest.raises(ValueError):
        api["EvidenceAlignmentQueryError"]("WRONG", "invalid code")
