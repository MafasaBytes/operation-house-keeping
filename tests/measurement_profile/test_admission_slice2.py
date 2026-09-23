from datetime import UTC, datetime
from types import SimpleNamespace
import json

import pytest

from applications.bounded_decision_workflow import measurement_admission as admission
from applications.bounded_decision_workflow.measurement_admission import (
    MeasurementAdmissionError,
    assess_procedure,
    admit_measurement,
)
from applications.bounded_decision_workflow.measurement_contracts import PROFILE

from tests.measurement_profile.test_contracts_and_closure import base_objects


def test_slice2_marks_all_declared_procedure_conditions_inapplicable_without_pruning():
    procedure = {
        "id": "T1",
        "conditions": [
            {"id": "applicability", "state": "false"},
            {"id": "availability", "state": "true"},
            {"id": "calibration", "state": "true"},
            {"id": "fidelity", "state": "true"},
            {"id": "hold", "state": "true"},
        ],
    }
    result = assess_procedure(procedure)
    assert result.state == "inapplicable"
    assert result.reasons == ("applicability_false",)


def public_review(context, *, current="true", observed="admitted"):
    question = SimpleNamespace(
        as_of=datetime.fromisoformat(context["as_of"].replace("Z", "+00:00")),
        assertion_context=SimpleNamespace(model_dump=lambda mode: context["assertion_context"]),
    )
    return SimpleNamespace(
        request=SimpleNamespace(current_condition_question=question),
        current_condition=SimpleNamespace(disposition=current),
        observed_value=SimpleNamespace(status=observed),
    )


def test_slice2_reuses_public_reconstruction_and_retains_procedure_inapplicability(monkeypatch):
    invocation, objects = base_objects()
    request = json.loads(objects[next(k for k in objects if k[0] == "nm.request.v1")])
    monkeypatch.setattr(
        admission, "admit_request_and_snapshot",
        lambda *_: public_review(request["context"]),
    )
    result = admit_measurement(
        invocation, objects, authority_pin=json.loads(invocation)["selection"]["sha256"],
        public_request_wire=b"request", public_snapshot_wire=b"snapshot")
    assert result.permission is True
    assert result.authority_state == "permitted"
    assert result.procedures[0].state == "inapplicable"
    assert "applicability_missing" in result.procedures[0].reasons
    assert result.downstream_work is True


def test_slice2_withholds_all_downstream_work_when_public_baseline_unavailable(monkeypatch):
    invocation, objects = base_objects()
    request = json.loads(objects[next(k for k in objects if k[0] == "nm.request.v1")])
    monkeypatch.setattr(
        admission, "admit_request_and_snapshot",
        lambda *_: public_review(request["context"], current="unavailable", observed="unavailable"),
    )
    result = admit_measurement(
        invocation, objects, authority_pin=json.loads(invocation)["selection"]["sha256"],
        public_request_wire=b"request", public_snapshot_wire=b"snapshot")
    assert result.evidence_state == "baseline_unavailable"
    assert result.permission is False
    assert result.procedures == ()
    assert result.hypotheses == ()
    assert result.downstream_work is False


def test_slice2_rejects_context_join_before_procedure_or_hypothesis_work(monkeypatch):
    invocation, objects = base_objects()
    request = json.loads(objects[next(k for k in objects if k[0] == "nm.request.v1")])
    wrong = dict(request["context"])
    wrong["as_of"] = "2026-08-08T20:30:00Z"
    monkeypatch.setattr(admission, "admit_request_and_snapshot",
                        lambda *_: public_review(wrong))
    with pytest.raises(MeasurementAdmissionError) as error:
        admit_measurement(
            invocation, objects, authority_pin=json.loads(invocation)["selection"]["sha256"],
            public_request_wire=b"request", public_snapshot_wire=b"snapshot")
    assert error.value.code == "EVIDENCE_JOIN_MISMATCH"
    assert error.value.target == "context"
