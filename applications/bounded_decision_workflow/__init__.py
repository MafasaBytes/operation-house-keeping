"""Bounded supplied-alternative decision workflow.

Slice S1 exposes strict request/snapshot decoding and public observation
admission only. Projection, policy, retention, replay, and CLI delivery are not
part of this surface yet.
"""

from applications.bounded_decision_workflow.admission import (
    AdmissionReview,
    CurrentConditionAssessment,
    ObservedValueAdmission,
    admit_request_and_snapshot,
    canonical_example_pair,
)
from applications.bounded_decision_workflow.contracts import WorkflowRequest
from applications.bounded_decision_workflow.errors import (
    WorkflowDiagnostic,
    WorkflowInputError,
)
from applications.bounded_decision_workflow.input import (
    BUILD_LIMITS,
    ParsedInput,
    ResourceCounts,
    parse_request_wire,
    parse_snapshot_wire,
)

__all__ = [
    "AdmissionReview",
    "BUILD_LIMITS",
    "CurrentConditionAssessment",
    "ObservedValueAdmission",
    "ParsedInput",
    "ResourceCounts",
    "WorkflowDiagnostic",
    "WorkflowInputError",
    "WorkflowRequest",
    "admit_request_and_snapshot",
    "canonical_example_pair",
    "parse_request_wire",
    "parse_snapshot_wire",
]
