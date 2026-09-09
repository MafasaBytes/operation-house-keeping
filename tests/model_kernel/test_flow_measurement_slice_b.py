"""FM-001 Slice B exact public contracts and structured-absence gate."""

from pathlib import Path
import inspect
import typing

import backend.model_kernel as kernel
from tests.model_kernel.fl001_slice_a_helpers import AS_DESIGNED, FLOW_A, PORT_A
from tests.model_kernel.builders import VAR_A


PUBLIC_ADDITIONS = [
    "FlowMeasurementEndpointRegistration",
    "FlowMeasurementReverseRegistration",
    "FlowMeasurementDeclarationPresence",
    "FlowMeasurementDeclarationConclusion",
    "FlowMeasurementSupportKind",
    "FlowMeasurementSupportActivity",
    "FlowMeasurementSupportLineageHealth",
    "FlowMeasurementSupportAlignment",
    "FlowMeasurementOrientation",
    "FlowMeasurementAgreementFinding",
    "FlowMeasurementAssertionLookupStatus",
    "FlowMeasurementSupportRow",
    "FlowMeasurementEffectiveBodyGroupRow",
    "FlowMeasurementRootRow",
    "FlowMeasurementEntryRow",
    "FlowMeasurementAssociationResult",
    "FlowMeasurementAssociationsForFlowResult",
    "FlowMeasurementAssociationsForVariableResult",
    "FlowMeasurementAssociationsAtPortResult",
    "FlowMeasurementAssertionResult",
]


def _literal(name):
    return typing.get_args(getattr(kernel, name))


def test_exact_public_additions_literals_fields_and_signatures():
    assert len(kernel.__all__) == len(set(kernel.__all__)) == 225
    assert kernel.__all__[-20:] == PUBLIC_ADDITIONS
    assert _literal("FlowMeasurementEndpointRegistration") == (
        "all_registered", "flow_not_registered", "variable_not_registered",
        "port_not_registered", "multiple_not_registered")
    assert _literal("FlowMeasurementReverseRegistration") == (
        "not_registered", "registered")
    assert _literal("FlowMeasurementDeclarationPresence") == (
        "not_declared", "declared")
    assert _literal("FlowMeasurementDeclarationConclusion") == (
        "not_evaluated", "declared_direct_measurement_relevance",
        "conflicted", "inactive")
    assert _literal("FlowMeasurementSupportKind") == (
        "frg", "vrg", "prg", "fld", "vpa", "vsm")
    assert _literal("FlowMeasurementSupportActivity") == (
        "permanent", "current", "superseded", "withdrawn")
    assert _literal("FlowMeasurementSupportLineageHealth") == (
        "not_applicable", "healthy", "conflicted", "inactive")
    assert _literal("FlowMeasurementSupportAlignment") == (
        "exact", "unaligned")
    assert _literal("FlowMeasurementOrientation") == (
        "aligned", "opposite", "unsigned_magnitude", "not_applicable")
    assert _literal("FlowMeasurementAgreementFinding") == (
        "one_healthy_root", "corroborating_healthy_roots",
        "same_root_conflict", "inactive_roots_present",
        "cross_root_effective_body_disagreement")
    assert _literal("FlowMeasurementAssertionLookupStatus") == (
        "not_found", "found")

    expected_fields = {
        "FlowMeasurementSupportRow": (
            "support_kind", "record_index", "activity",
            "containing_lineage_health", "current_alignment"),
        "FlowMeasurementEffectiveBodyGroupRow": (
            "group_index", "representative_current_tip_index",
            "current_tip_indices", "participating_root_indices",
            "participant_role", "orientation", "support_rows"),
        "FlowMeasurementRootRow": (
            "root_index", "root_record_index", "lineage_record_indices",
            "current_tip_indices", "withdrawal_indices", "lineage_health",
            "effective_body_group_indices"),
        "FlowMeasurementEntryRow": (
            "entry_index", "flow_anchor_id", "variable_anchor_id",
            "participant_port_anchor_id", "orientation",
            "declaration_conclusion", "agreement_findings",
            "participant_role", "roots", "effective_body_groups",
            "current_assertion_indices"),
        "FlowMeasurementAssociationResult": (
            "material", "flow_anchor_id", "variable_anchor_id",
            "participant_port_anchor_id", "context", "orientation",
            "endpoint_registration", "declaration_presence",
            "declaration_conclusion", "agreement_findings",
            "participant_role", "roots", "effective_body_groups",
            "current_assertion_indices"),
        "FlowMeasurementAssociationsForFlowResult": (
            "material", "flow_anchor_id", "context",
            "registration_status", "declaration_presence", "entries"),
        "FlowMeasurementAssociationsForVariableResult": (
            "material", "variable_anchor_id", "context",
            "registration_status", "declaration_presence", "entries"),
        "FlowMeasurementAssociationsAtPortResult": (
            "material", "participant_port_anchor_id", "context",
            "registration_status", "declaration_presence", "entries"),
        "FlowMeasurementAssertionResult": (
            "material", "record_id", "lookup_status", "record_index",
            "assertion_activity", "containing_root_health",
            "containing_subject_conclusion",
            "containing_agreement_findings", "root_record_index",
            "successor_indices", "withdrawal_indices", "participant_role",
            "orientation", "support_rows"),
    }
    for name, fields in expected_fields.items():
        contract = getattr(kernel, name)
        assert tuple(contract.model_fields) == fields
        assert all(field.is_required() for field in contract.model_fields.values())

    methods = kernel.ModelQueries
    assert tuple(inspect.signature(methods.flow_measurement_association).parameters) == (
        "self", "flow_anchor_id", "variable_anchor_id",
        "participant_port_anchor_id", "context", "orientation")
    for name, endpoint in (
        ("flow_measurement_associations_for_flow", "flow_anchor_id"),
        ("flow_measurement_associations_for_variable", "variable_anchor_id"),
        ("flow_measurement_associations_at_port", "participant_port_anchor_id"),
    ):
        parameters = inspect.signature(getattr(methods, name)).parameters
        assert tuple(parameters) == ("self", endpoint, "context")
        assert parameters["context"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(inspect.signature(methods.flow_measurement_assertion).parameters) == (
        "self", "record_id")


def test_accepted_36_record_revision_returns_exact_structured_absence():
    loaded = kernel.ModelStore(Path("models/demo-printer")).load()
    assert loaded.revision.record_count == 36
    queries = kernel.ModelQueries(loaded)

    exact = queries.flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert exact.endpoint_registration == "all_registered"
    assert exact.declaration_presence == "not_declared"
    assert exact.declaration_conclusion == "not_evaluated"
    assert exact.agreement_findings == exact.roots == ()
    assert exact.effective_body_groups == exact.current_assertion_indices == ()
    assert exact.participant_role is None
    assert exact.material.revision == loaded.revision

    for result in (
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    ):
        assert result.registration_status == "registered"
        assert result.declaration_presence == "not_declared"
        assert result.entries == ()
        assert result.material.revision == loaded.revision

    missing = queries.flow_measurement_assertion("fma_" + "0" * 64)
    assert missing.lookup_status == "not_found"
    assert missing.record_index is None
    assert missing.assertion_activity is None
    assert missing.containing_root_health is None
    assert missing.containing_subject_conclusion is None
    assert missing.containing_agreement_findings is None
    assert missing.root_record_index is None
    assert missing.successor_indices == missing.withdrawal_indices == ()
    assert missing.participant_role is missing.orientation is None
    assert missing.support_rows == ()
