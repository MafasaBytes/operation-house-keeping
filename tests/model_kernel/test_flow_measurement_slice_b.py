"""FM-001 Slice B exact public contracts and structured-absence gate."""

from pathlib import Path
import inspect
import typing
from unittest.mock import patch

import backend.model_kernel as kernel
import pytest
from pydantic import ValidationError
from backend.model_kernel.canonical import _flow_measurement_effective_body_bytes
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, FLOW_B, PORT_A, PORT_B, VIEW_INDEPENDENT,
    flow_declaration, flow_kind, flow_registration, flow_withdrawal,
)
from tests.model_kernel.builders import VAR_A, VAR_B, variable_registration
from tests.model_kernel.test_flow_measurement_slice_a import (
    CLAIM, T0, association, foundation, semantic, variable_port,
    variable_port_withdrawal, withdrawal,
)


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
    assert len(kernel.__all__) == len(set(kernel.__all__)) == 236
    assert kernel.__all__[205:225] == PUBLIC_ADDITIONS
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
    for forbidden in (
        "flow_measurement_associations", "query_flow_measurement",
        "build_flow_measurement_association", "FlowMeasurementQueries",
        "FlowMeasurementStore", "FlowMeasurementFacade",
    ):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)


def test_accepted_36_record_revision_returns_exact_structured_absence():
    loaded = kernel.ModelStore(Path("models/demo-printer")).load()
    assert loaded.revision.record_count == 36
    queries = kernel.ModelQueries(loaded)

    exact = queries.flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert exact.endpoint_registration == "multiple_not_registered"
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
        assert result.registration_status == "not_registered"
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
    missing_withdrawal = queries.flow_measurement_assertion("fmw_" + "0" * 64)
    assert missing_withdrawal.lookup_status == "not_found"
    assert missing_withdrawal.record_index is None
    assert missing_withdrawal.support_rows == ()


def _queries(*claims, extra=()):
    records, support = foundation()
    all_records = (*records, *extra, *claims)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in all_records})
    return kernel.ModelQueries(loaded), support


def _successor(record, *, supersedes, note, **changes):
    values = record.model_dump(mode="python", exclude={
        "record_kind", "schema_version", "record_id"})
    values.update(supersedes=supersedes, note=note, **changes)
    return kernel.build_record(type(record), **values)


def test_one_healthy_root_six_support_rows_reverse_and_assertion_agree():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    queries = kernel.ModelQueries(loaded)
    exact = queries.flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")

    assert exact.endpoint_registration == "all_registered"
    assert exact.declaration_presence == "declared"
    assert exact.declaration_conclusion == \
        "declared_direct_measurement_relevance"
    assert exact.agreement_findings == ("one_healthy_root",)
    assert exact.participant_role == "source"
    assert len(exact.roots) == len(exact.effective_body_groups) == 1
    assert exact.roots[0].root_index == 0
    assert exact.roots[0].lineage_health == "healthy"
    assert exact.roots[0].effective_body_group_indices == (0,)
    group = exact.effective_body_groups[0]
    assert group.group_index == 0
    assert group.participating_root_indices == (0,)
    assert group.participant_role == "source"
    assert group.orientation == "aligned"
    assert tuple(row.support_kind for row in group.support_rows) == (
        "frg", "vrg", "prg", "fld", "vpa", "vsm")
    assert tuple(row.activity for row in group.support_rows) == (
        "permanent", "permanent", "permanent", "current", "current",
        "current")
    assert tuple(row.containing_lineage_health for row in group.support_rows) == (
        "not_applicable", "not_applicable", "not_applicable", "healthy",
        "healthy", "healthy")
    assert all(row.current_alignment == "exact" for row in group.support_rows)

    reverse_results = (
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    )
    exact_subject = exact.model_dump(mode="python", exclude={
        "material", "endpoint_registration", "declaration_presence",
        "flow_anchor_id", "variable_anchor_id", "participant_port_anchor_id",
        "context", "orientation",
    })
    for reverse in reverse_results:
        assert reverse.registration_status == "registered"
        assert reverse.declaration_presence == "declared"
        assert len(reverse.entries) == 1
        entry = reverse.entries[0]
        assert entry.entry_index == 0
        assert entry.flow_anchor_id == FLOW_A
        assert entry.variable_anchor_id == VAR_A
        assert entry.participant_port_anchor_id == PORT_A
        assert entry.orientation == "aligned"
        assert entry.model_dump(mode="python", exclude={
            "entry_index", "flow_anchor_id", "variable_anchor_id",
            "participant_port_anchor_id", "orientation",
        }) == exact_subject

    assertion_result = queries.flow_measurement_assertion(claim.record_id)
    assert assertion_result.lookup_status == "found"
    assert assertion_result.assertion_activity == "current"
    assert assertion_result.containing_root_health == "healthy"
    assert assertion_result.containing_subject_conclusion == \
        exact.declaration_conclusion
    assert assertion_result.containing_agreement_findings == \
        exact.agreement_findings
    assert assertion_result.participant_role == "source"
    assert assertion_result.orientation == "aligned"
    assert assertion_result.support_rows == group.support_rows
    result_index = loaded.revision.record_ids.index(claim.record_id)
    assert assertion_result.record_index == result_index
    assert assertion_result.root_record_index == result_index
    assert assertion_result.successor_indices == ()
    assert assertion_result.withdrawal_indices == ()

    for result in (exact, *reverse_results, assertion_result):
        rebuilt = type(result).model_validate(result.model_dump(mode="python"))
        assert rebuilt == result
        dumped = result.model_dump(mode="python")
        assert "material" in dumped
        assert str(dumped).count("'material':") == 1


def test_withdrawal_assertion_has_exact_null_and_empty_shape():
    records, support = foundation()
    claim = association(support)
    event = withdrawal(claim)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, claim, event)})
    queries = kernel.ModelQueries(loaded)
    exact = queries.flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert exact.declaration_presence == "declared"
    assert exact.declaration_conclusion == "inactive"
    assert exact.agreement_findings == ("inactive_roots_present",)
    assert exact.roots[0].lineage_health == "inactive"
    assert exact.effective_body_groups == exact.current_assertion_indices == ()

    result = queries.flow_measurement_assertion(event.record_id)
    assert result.lookup_status == "found"
    assert result.record_index is not None
    assert result.material.records[result.record_index].withdraws == claim.record_id
    assert result.assertion_activity is None
    assert result.containing_root_health is None
    assert result.containing_subject_conclusion is None
    assert result.containing_agreement_findings is None
    assert result.root_record_index is None
    assert result.successor_indices == result.withdrawal_indices == ()
    assert result.participant_role is result.orientation is None
    assert result.support_rows == ()


def test_corroboration_disagreement_and_mixed_root_findings_are_exact():
    records, support = foundation()
    first = association(support, note="first independent root")
    second = association(support, note="second independent root")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, first, second)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.declaration_conclusion == \
        "declared_direct_measurement_relevance"
    assert result.agreement_findings == ("corroborating_healthy_roots",)
    assert len(result.roots) == 2
    assert len(result.effective_body_groups) == 1
    assert result.effective_body_groups[0].participating_root_indices == (0, 1)

    alternate_vsm = semantic(note="different exact support pin")
    alternate = association((*support[:-1], alternate_vsm), note="different body")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, alternate_vsm, first, alternate)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.declaration_conclusion == "conflicted"
    assert result.agreement_findings == (
        "cross_root_effective_body_disagreement",)
    assert len(result.roots) == len(result.effective_body_groups) == 2

    inactive = association(support, note="inactive independent root")
    event = withdrawal(inactive)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, first, inactive, event)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.declaration_conclusion == \
        "declared_direct_measurement_relevance"
    assert result.agreement_findings == (
        "one_healthy_root", "inactive_roots_present")
    assert tuple(root.lineage_health for root in result.roots) == tuple(
        "healthy" if root.root_record_index == result.material.revision.record_ids.index(
            first.record_id) else "inactive" for root in result.roots)


def test_same_root_conflict_retains_all_groups_without_selecting_a_body():
    records, support = foundation()
    root = association(support, note="root")
    left = association(
        support, supersedes=(root.record_id,), note="same body left")
    alternate_vsm = semantic(note="alternate support")
    right = association(
        (*support[:-1], alternate_vsm), supersedes=(root.record_id,),
        note="different body right")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, alternate_vsm, root, left, right)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.declaration_conclusion == "conflicted"
    assert result.agreement_findings == ("same_root_conflict",)
    assert len(result.roots) == 1
    assert result.roots[0].lineage_health == "conflicted"
    assert result.roots[0].effective_body_group_indices == (0, 1)
    assert len(result.effective_body_groups) == 2
    assert {group.representative_current_tip_index for group in
            result.effective_body_groups} == {
                result.material.revision.record_ids.index(left.record_id),
                result.material.revision.record_ids.index(right.record_id),
            }


def test_same_body_conflicts_and_mixed_root_precedence_are_exact():
    records, support = foundation()
    root = association(support, note="conflict root")
    left = association(support, supersedes=(root.record_id,), note="left")
    right = association(support, supersedes=(root.record_id,), note="right")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, root, left, right)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.agreement_findings == ("same_root_conflict",)
    assert result.declaration_conclusion == "conflicted"
    assert len(result.roots) == len(result.effective_body_groups) == 1
    assert result.roots[0].effective_body_group_indices == (0,)

    healthy = association(support, note="healthy root")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, healthy, root, left, right)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.agreement_findings == (
        "one_healthy_root", "same_root_conflict")
    assert result.declaration_conclusion == "conflicted"
    reverse = kernel.ModelQueries(loaded).flow_measurement_associations_for_flow(
        FLOW_A, context=AS_DESIGNED)
    assert len(reverse.entries) == 1
    assert len(reverse.entries[0].roots) == 2


def test_equal_and_unequal_conflicted_root_body_sets_and_ordering():
    records, support = foundation()
    first_root = association(support, note="first root")
    first_tips = (
        association(support, supersedes=(first_root.record_id,), note="first left"),
        association(support, supersedes=(first_root.record_id,), note="first right"),
    )
    second_root = association(support, note="second root")
    second_tips = (
        association(support, supersedes=(second_root.record_id,), note="second left"),
        association(support, supersedes=(second_root.record_id,), note="second right"),
    )
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, first_root, *first_tips, second_root, *second_tips)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.agreement_findings == ("same_root_conflict",)
    assert len(result.roots) == 2
    assert len(result.effective_body_groups) == 1

    alternate_vsm = semantic(note="alternate exact body support")
    alternate_support = (*support[:-1], alternate_vsm)
    second_root = association(alternate_support, note="alternate root")
    second_tips = (
        association(alternate_support, supersedes=(second_root.record_id,),
                    note="alternate left"),
        association(alternate_support, supersedes=(second_root.record_id,),
                    note="alternate right"),
    )
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, alternate_vsm, first_root, *first_tips,
            second_root, *second_tips)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert result.agreement_findings == (
        "same_root_conflict", "cross_root_effective_body_disagreement")
    root_ids = tuple(result.material.revision.record_ids[row.root_record_index]
                     for row in result.roots)
    assert root_ids == tuple(sorted(root_ids))
    group_bodies = tuple(_flow_measurement_effective_body_bytes(
        result.material.records[group.representative_current_tip_index])
        for group in result.effective_body_groups)
    assert group_bodies == tuple(sorted(group_bodies))
    for group in result.effective_body_groups:
        assert group.representative_current_tip_index == min(
            group.current_tip_indices)
    for root_row in result.roots:
        for group_index in root_row.effective_body_group_indices:
            assert root_row.root_index in result.effective_body_groups[
                group_index].participating_root_indices


def test_support_rows_disclose_historical_lower_lifecycle_without_retargeting():
    records, support = foundation()
    pinned_fld = support[3]
    pinned_vpa = support[4]
    pinned_vsm = support[5]
    newer_fld = _successor(
        pinned_fld, supersedes=(pinned_fld.record_id,), note="later FLD")
    newer_vpa = variable_port(
        supersedes=(pinned_vpa.record_id,), note="later VPA")
    newer_vsm = _successor(
        pinned_vsm, supersedes=(pinned_vsm.record_id,), note="later VSM")
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, newer_fld, newer_vpa, newer_vsm, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    by_kind = {row.support_kind: row for row in result.support_rows}
    for kind in ("fld", "vpa", "vsm"):
        assert by_kind[kind].activity == "superseded"
        assert by_kind[kind].containing_lineage_health == "healthy"
        assert by_kind[kind].current_alignment == "exact"

    wrong_role = kernel.ObservationRoleDeclaration(
        dimension="observation_role",
        observation_role=kernel.ObservationRoleReference(
            system_id="project_local", system_edition="ohk-observation-roles-1",
            code="command_target"))
    unaligned_vsm = _successor(
        pinned_vsm, supersedes=(pinned_vsm.record_id,),
        note="current command role", declaration=wrong_role)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, unaligned_vsm, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    vsm_row = result.support_rows[-1]
    assert (vsm_row.activity, vsm_row.containing_lineage_health,
            vsm_row.current_alignment) == (
                "superseded", "healthy", "unaligned")

    fld_event = flow_withdrawal(pinned_fld)
    vpa_event = variable_port_withdrawal(pinned_vpa)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, fld_event, vpa_event, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    by_kind = {row.support_kind: row for row in result.support_rows}
    for kind in ("fld", "vpa"):
        assert (by_kind[kind].activity,
                by_kind[kind].containing_lineage_health,
                by_kind[kind].current_alignment) == (
                    "withdrawn", "inactive", "unaligned")


@pytest.mark.parametrize("flow,variable,port,expected", [
    ("flow", VAR_A, PORT_A, "flow_not_registered"),
    (FLOW_A, "variable", PORT_A, "variable_not_registered"),
    (FLOW_A, VAR_A, "port", "port_not_registered"),
    ("flow", "variable", PORT_A, "multiple_not_registered"),
    ("flow", VAR_A, "port", "multiple_not_registered"),
    (FLOW_A, "variable", "port", "multiple_not_registered"),
    ("flow", "variable", "port", "multiple_not_registered"),
])
def test_endpoint_registration_axes_are_exact(flow, variable, port, expected):
    records, _ = foundation()
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in records})
    query = kernel.ModelQueries(loaded)
    values = {
        "flow": "flo_" + "f" * 32,
        "variable": "var_" + "f" * 32,
        "port": "prt_" + "f" * 32,
    }
    result = query.flow_measurement_association(
        values.get(flow, flow), values.get(variable, variable),
        values.get(port, port), AS_DESIGNED, "aligned")
    assert result.endpoint_registration == expected
    assert result.declaration_presence == "not_declared"
    assert result.declaration_conclusion == "not_evaluated"
    assert result.participant_role is None
    assert result.agreement_findings == result.roots == ()
    assert result.effective_body_groups == result.current_assertion_indices == ()


def test_registered_nonparticipant_and_cross_context_do_not_create_relevance():
    first_records, support = foundation()
    second_records, second_support = foundation(VIEW_INDEPENDENT)
    claim = association(second_support, context=VIEW_INDEPENDENT)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *first_records, *second_records, claim)})
    queries = kernel.ModelQueries(loaded)
    nonparticipant = queries.flow_measurement_association(
        FLOW_A, VAR_A, PORT_B, AS_DESIGNED, "aligned")
    assert nonparticipant.endpoint_registration == "all_registered"
    assert nonparticipant.declaration_presence == "not_declared"
    assert nonparticipant.declaration_conclusion == "not_evaluated"
    assert nonparticipant.participant_role is None
    assert nonparticipant.agreement_findings == nonparticipant.roots == ()
    assert nonparticipant.effective_body_groups == \
        nonparticipant.current_assertion_indices == ()
    for result in (
        queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned"),
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    ):
        assert result.declaration_presence == "not_declared"
        assert getattr(result, "entries", ()) == ()

    for reverse in (
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    ):
        assert reverse.registration_status == "registered"
        assert reverse.declaration_presence == "not_declared"
        assert reverse.entries == ()


def test_orientation_subjects_remain_distinct_and_reverse_order_is_normative():
    records, support = foundation()
    orientations = (
        "aligned", "opposite", "unsigned_magnitude", "not_applicable")
    claims = tuple(association(support, orientation=value, note=value)
                   for value in reversed(orientations))
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *reversed(records), *claims)})
    queries = kernel.ModelQueries(loaded)
    for value in orientations:
        result = queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, AS_DESIGNED, value)
        assert result.orientation == value
        assert result.declaration_presence == "declared"
        assert result.effective_body_groups[0].orientation == value
    for result in (
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    ):
        assert tuple(entry.orientation for entry in result.entries) == orientations
        assert tuple(entry.entry_index for entry in result.entries) == (0, 1, 2, 3)


def test_multi_identifier_reverse_axes_sort_semantically_and_share_payloads():
    records, support = foundation()
    ports = tuple(record for record in records
                  if record.record_kind == "port_registration")
    connection = next(record for record in records
                      if record.record_kind == "port_connection_assertion")
    interfaces = tuple(record for record in records
                       if record.record_kind == "port_interface_declaration")
    source_interfaces = tuple(
        record for record in interfaces if record.declaration.value == "output")
    sink_interfaces = tuple(
        record for record in interfaces if record.declaration.value == "input")

    alternate_vrg = variable_registration(VAR_B)
    alternate_vpa = variable_port(variable=VAR_B)
    alternate_vsm = semantic(variable=VAR_B)
    alternate_variable_claim = association(
        (support[0], alternate_vrg, support[2], support[3],
         alternate_vpa, alternate_vsm),
        variable_anchor_id=VAR_B,
    )
    alternate_frg = flow_registration(
        flow_anchor_id=FLOW_B, port_records=ports,
        kind=flow_kind(code="secondary_transfer"))
    alternate_fld = flow_declaration(
        alternate_frg, port_records=ports, pcn=connection,
        source_pifs=source_interfaces, sink_pifs=sink_interfaces)
    alternate_flow_claim = association(
        (alternate_frg, support[1], support[2], alternate_fld,
         support[4], support[5]),
        flow_anchor_id=FLOW_B,
    )
    base_claim = association(support)
    members = (
        *records, alternate_vrg, alternate_vpa, alternate_vsm,
        alternate_frg, alternate_fld, alternate_variable_claim,
        alternate_flow_claim, base_claim,
    )
    loaded = validate_record_collection(
        "test-model", {record.record_id: record
                       for record in reversed(members)})
    queries = kernel.ModelQueries(loaded)
    reverse_results = (
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
    )
    expected_subjects = (
        ((FLOW_A, VAR_A, PORT_A, "aligned"),
         (FLOW_A, VAR_B, PORT_A, "aligned")),
        ((FLOW_A, VAR_A, PORT_A, "aligned"),
         (FLOW_B, VAR_A, PORT_A, "aligned")),
        ((FLOW_A, VAR_A, PORT_A, "aligned"),
         (FLOW_A, VAR_B, PORT_A, "aligned"),
         (FLOW_B, VAR_A, PORT_A, "aligned")),
    )
    for reverse, expected in zip(reverse_results, expected_subjects):
        actual = tuple((
            entry.flow_anchor_id, entry.variable_anchor_id,
            entry.participant_port_anchor_id, entry.orientation,
        ) for entry in reverse.entries)
        assert actual == expected
        assert tuple(entry.entry_index for entry in reverse.entries) == \
            tuple(range(len(expected)))
        for entry in reverse.entries:
            exact = queries.flow_measurement_association(
                entry.flow_anchor_id, entry.variable_anchor_id,
                entry.participant_port_anchor_id, AS_DESIGNED,
                entry.orientation)
            assert entry.model_dump(mode="json", exclude={
                "entry_index", "flow_anchor_id", "variable_anchor_id",
                "participant_port_anchor_id", "orientation",
            }) == exact.model_dump(mode="json", exclude={
                "material", "flow_anchor_id", "variable_anchor_id",
                "participant_port_anchor_id", "context", "orientation",
                "endpoint_registration", "declaration_presence",
            })


def test_authoritative_result_reconstruction_rejects_hostile_values():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    contract = kernel.FlowMeasurementAssociationResult

    valid = result.model_dump(mode="python")
    for field, replacement in (
        ("declaration_conclusion", "inactive"),
        ("participant_role", None),
        ("current_assertion_indices", (True,)),
        ("agreement_findings", ()),
    ):
        attack = {**valid, field: replacement}
        with pytest.raises(ValidationError):
            contract.model_validate(attack)
    missing = dict(valid)
    del missing["agreement_findings"]
    with pytest.raises(ValidationError):
        contract.model_validate(missing)
    for unordered in (set(result.agreement_findings),
                      frozenset(result.agreement_findings)):
        with pytest.raises(ValidationError):
            contract.model_validate({**valid, "agreement_findings": unordered})

    forged_group = dict(valid)
    forged_group["effective_body_groups"] = tuple(
        {**row, "participating_root_indices": (True,)}
        for row in forged_group["effective_body_groups"])
    with pytest.raises(ValidationError):
        contract.model_validate(forged_group)

    class HostileString(str):
        pass

    hostile = dict(valid)
    hostile["flow_anchor_id"] = HostileString(FLOW_A)
    with pytest.raises(ValidationError):
        contract.model_validate(hostile)
    with pytest.raises(kernel.ModelQueryError):
        kernel.ModelQueries(loaded).flow_measurement_association(
            HostileString(FLOW_A), VAR_A, PORT_A, AS_DESIGNED, "aligned")

    forged = result.model_copy(update={"declaration_conclusion": "inactive"})
    with pytest.raises(ValidationError):
        contract.model_validate(forged)
    vars(result)["hidden"] = "state"
    with pytest.raises(ValidationError):
        contract.model_validate(result)


def test_result_revalidation_and_queries_perform_no_io_or_ambient_discovery():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    queries = kernel.ModelQueries(loaded)
    baselines = (
        queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned"),
        queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED),
        queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED),
        queries.flow_measurement_assertion(claim.record_id),
    )
    payloads = tuple(result.model_dump(mode="python") for result in baselines)

    def forbidden(*args, **kwargs):
        raise AssertionError("ambient operation attempted")

    with patch("builtins.open", forbidden), \
            patch("pathlib.Path.open", forbidden), \
            patch("pathlib.Path.read_bytes", forbidden), \
            patch("pathlib.Path.read_text", forbidden), \
            patch("pathlib.Path.write_bytes", forbidden), \
            patch("pathlib.Path.write_text", forbidden), \
            patch("pathlib.Path.mkdir", forbidden), \
            patch("pathlib.Path.touch", forbidden), \
            patch("socket.socket", forbidden), \
            patch("socket.create_connection", forbidden), \
            patch("sqlite3.connect", forbidden), \
            patch("os.getenv", forbidden), \
            patch("time.time", forbidden):
        rebuilt = tuple(type(result).model_validate(payload)
                        for result, payload in zip(baselines, payloads))
        queried = (
            queries.flow_measurement_association(
                FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned"),
            queries.flow_measurement_associations_for_flow(
                FLOW_A, context=AS_DESIGNED),
            queries.flow_measurement_associations_for_variable(
                VAR_A, context=AS_DESIGNED),
            queries.flow_measurement_associations_at_port(
                PORT_A, context=AS_DESIGNED),
            queries.flow_measurement_assertion(claim.record_id),
        )
    assert rebuilt == baselines
    assert queried == baselines
