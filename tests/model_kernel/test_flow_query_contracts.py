"""FL-001 Slice B red-first public contract and structured-absence gates."""

import inspect
import json
from pathlib import Path
import typing

import backend.model_kernel as kernel
import pytest
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP, CN001_MEMBERSHIP, GOLDEN_REVISION,
    PRE_BH001_REVISION, PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, PRE_PT001_REVISION,
    PRE_FL001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION,
    PRE_ST001_REVISION, PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION, PT001_MEMBERSHIP, ST001_MEMBERSHIP,
    VP001_MEMBERSHIP, VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")
ABSENT_FLOW = "flo_" + "0" * 32
ABSENT_RECORDS = tuple(prefix + "_" + "0" * 64
                       for prefix in ("frg", "fld", "flw"))
REGISTERED_PORT = "prt_91a3d6db9df440e1a09dbdb185c7b182"
ABSENT_PORT = "prt_" + "0" * 32
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_operated")
def public_methods():
    return {
        name for name, value in vars(kernel.ModelQueries).items()
        if not name.startswith("_") and callable(value)
    }


def without_material(result):
    return result.model_dump(mode="python", exclude={"material"})


def test_exactly_four_flow_methods_and_signatures_are_public():
    before = {
        "ancestors", "behavior", "behavior_assertion", "behavior_declaration",
        "behaviors_involving_variable", "children", "connections_containing",
        "connections_exact", "connections_of_port", "constraint_declaration",
        "constraints_of_variable", "descendants", "entity", "hierarchy_health",
        "interface_compatibility", "parents", "port", "port_assertion",
        "port_interface", "ports_associated_with_variable", "ports_of_entity",
        "relationships", "state", "state_assertion", "state_declaration",
        "states_of_entity", "transition", "transition_assertion",
        "transition_declaration", "transitions_of_entity", "variable",
        "variable_port_assertion", "variable_port_association",
        "variable_semantics", "variable_value_specification",
        "variables_associated_with_port", "variables_of",
    }
    expected = {
        "flow": (("self", "flow_anchor_id"), kernel.FlowLookupResult),
        "flow_declaration": (
            ("self", "flow_anchor_id", "context"),
            kernel.FlowDeclarationResult),
        "flows_involving_port": (
            ("self", "port_anchor_id", "context"), kernel.PortFlowsResult),
        "flow_assertion": (
            ("self", "record_id"), kernel.FlowAssertionDisclosureResult),
    }
    assert public_methods() == before | set(expected)
    for name, (parameters, return_annotation) in expected.items():
        signature = inspect.signature(getattr(kernel.ModelQueries, name))
        assert tuple(signature.parameters) == parameters
        assert signature.return_annotation is return_annotation
        if "context" in parameters:
            assert signature.parameters["context"].kind is \
                inspect.Parameter.KEYWORD_ONLY
            assert signature.parameters["context"].default is \
                inspect.Parameter.empty
    for forbidden in (
        "current_flow", "observed_flow", "commanded_flow", "assess_flow",
        "detect_flow", "flow_history", "flow_occurrence", "upstream",
        "downstream", "flow_path", "flow_rate", "balance", "conservation",
    ):
        assert forbidden not in public_methods()


def test_exact_flow_literals_are_public_in_normative_order():
    expected = {
        "FlowLookupStatus": ("not_registered", "registered"),
        "FlowDeclarationConclusion": (
            "not_registered", "not_declared", "declared", "conflicted",
            "inactive"),
        "FlowDeclarationLineageSummary": (
            "not_applicable", "healthy", "conflicted", "inactive"),
        "FlowAgreementFinding": (
            "one_healthy_root", "corroborating_healthy_roots",
            "same_root_conflict", "cross_root_effective_body_disagreement",
            "inactive_roots_present"),
        "FlowPortRole": ("source", "sink"),
        "PortFlowsStatus": ("port_not_registered", "registered"),
        "FlowAssertionLookupStatus": ("not_found", "found"),
    }
    for name, literals in expected.items():
        value = getattr(kernel, name)
        assert typing.get_args(value) == literals
        assert name in kernel.__all__


def test_exact_flow_result_field_order_and_exports():
    assert len(kernel.__all__) == 203
    expected = {
        "FlowLookupResult": (
            "material", "flow_anchor_id", "status", "registration_index",
            "source_port_registration_indices",
            "sink_port_registration_indices"),
        "FlowConnectionSupportResult": (
            "connection_assertion_index", "exact_topology_conclusion",
            "pinned_assertion_activity", "pinned_lineage_health",
            "alignment"),
        "FlowDirectionSupportResult": (
            "role", "port_anchor_id", "port_registration_index",
            "direction_declaration_index", "direction_dimension_status",
            "pinned_assertion_activity", "pinned_lineage_health",
            "current_direction_relation", "alignment"),
        "FlowEffectiveBodyGroupResult": (
            "group_index", "representative_declaration_index",
            "current_tip_indices", "root_record_indices",
            "connection_support", "source_direction_supports",
            "sink_direction_supports", "support_alignment_summary"),
        "FlowDeclarationRootResult": (
            "root_record_index", "lineage_record_indices",
            "current_tip_indices", "withdrawal_indices", "lineage_health",
            "effective_body_group_indices"),
        "FlowDeclarationResult": (
            "material", "flow_anchor_id", "context", "conclusion",
            "lineage_summary", "agreement_findings", "registration_index",
            "roots", "effective_body_groups", "current_declaration_indices"),
        "PortFlowEntry": (
            "entry_index", "flow_anchor_id", "flow_registration_index",
            "role", "conclusion", "lineage_summary", "agreement_findings",
            "roots", "effective_body_groups", "current_declaration_indices"),
        "PortFlowsResult": (
            "material", "port_anchor_id", "context", "status",
            "port_registration_index", "entries"),
        "FlowAssertionDisclosureResult": (
            "material", "record_id", "lookup_status", "record_index",
            "activity", "containing_lineage_health",
            "containing_flow_conclusion", "containing_agreement_findings",
            "root_record_index", "successor_indices", "withdrawal_indices"),
    }
    for name, fields in expected.items():
        contract = getattr(kernel, name)
        assert tuple(contract.model_fields) == fields
        assert name in kernel.__all__


def test_all_four_queries_have_exact_historical_34_record_absence():
    loaded = kernel.ModelStore(DEMO_MODEL).replay(ST001_MEMBERSHIP)
    queries = kernel.ModelQueries(loaded)
    lookup = queries.flow(ABSENT_FLOW)
    assert without_material(lookup) == {
        "flow_anchor_id": ABSENT_FLOW,
        "status": "not_registered",
        "registration_index": None,
        "source_port_registration_indices": (),
        "sink_port_registration_indices": (),
    }
    declaration = queries.flow_declaration(ABSENT_FLOW, context=CONTEXT)
    assert without_material(declaration) == {
        "flow_anchor_id": ABSENT_FLOW,
        "context": CONTEXT.model_dump(mode="python"),
        "conclusion": "not_registered",
        "lineage_summary": "not_applicable",
        "agreement_findings": (),
        "registration_index": None,
        "roots": (),
        "effective_body_groups": (),
        "current_declaration_indices": (),
    }
    registered = queries.flows_involving_port(
        REGISTERED_PORT, context=CONTEXT)
    assert without_material(registered) == {
        "port_anchor_id": REGISTERED_PORT,
        "context": CONTEXT.model_dump(mode="python"),
        "status": "registered",
        "port_registration_index": 11,
        "entries": (),
    }
    absent = queries.flows_involving_port(ABSENT_PORT, context=CONTEXT)
    assert without_material(absent) == {
        "port_anchor_id": ABSENT_PORT,
        "context": CONTEXT.model_dump(mode="python"),
        "status": "port_not_registered",
        "port_registration_index": None,
        "entries": (),
    }
    for record_id in ABSENT_RECORDS:
        assertion = queries.flow_assertion(record_id)
        assert without_material(assertion) == {
            "record_id": record_id,
            "lookup_status": "not_found",
            "record_index": None,
            "activity": None,
            "containing_lineage_health": None,
            "containing_flow_conclusion": None,
            "containing_agreement_findings": None,
            "root_record_index": None,
            "successor_indices": (),
            "withdrawal_indices": (),
        }
    for result in (lookup, declaration, registered, absent):
        assert result.material.revision.revision_id == PRE_FL001_REVISION
        assert result.material.revision.record_count == 34
        assert len(result.material.records) == 34


def test_flow_results_carry_material_once():
    result = kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load()
                                 ).flow_declaration(
                                     ABSENT_FLOW, context=CONTEXT)
    decoded = json.loads(result.model_dump_json())
    assert list(decoded).count("material") == 1
    assert len(decoded["material"]["records"]) == 36
    assert "material" not in json.dumps({
        "roots": decoded["roots"],
        "groups": decoded["effective_body_groups"],
    })


def test_every_explicit_historical_membership_has_structured_flow_absence():
    cases = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION, 9),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION, 10),
        (VS001_MEMBERSHIP, GOLDEN_REVISION, 11),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, 14),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION, 16),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION, 18),
        (PT001_MEMBERSHIP, PRE_VP001_REVISION, 28),
        (VP001_MEMBERSHIP, PRE_BH001_REVISION, 29),
        (BH001_MEMBERSHIP, PRE_ST001_REVISION, 32),
        (ST001_MEMBERSHIP, PRE_FL001_REVISION, 34),
    )
    store = kernel.ModelStore(DEMO_MODEL)
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        queries = kernel.ModelQueries(loaded)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        assert queries.flow(ABSENT_FLOW).status == "not_registered"
        assert queries.flow_declaration(
            ABSENT_FLOW, context=CONTEXT).conclusion == "not_registered"
        port_result = queries.flows_involving_port(
            REGISTERED_PORT, context=CONTEXT)
        assert port_result.status == (
            "registered" if REGISTERED_PORT
            in loaded.port_registrations_by_anchor else
            "port_not_registered")
        assert port_result.entries == ()
        for record_id in ABSENT_RECORDS:
            assert queries.flow_assertion(record_id).lookup_status == \
                "not_found"


@pytest.mark.parametrize(
    "method,args,kwargs",
    (
        ("flow", ("flo_bad",), {}),
        ("flow", (True,), {}),
        ("flow_declaration", ("sta_" + "0" * 32,), {"context": CONTEXT}),
        ("flows_involving_port", ("flo_" + "0" * 32,), {"context": CONTEXT}),
        ("flow_assertion", ("pcn_" + "0" * 64,), {}),
        ("flow_assertion", ("fld_bad",), {}),
    ),
)
def test_flow_query_identifiers_are_typed_before_lookup(method, args, kwargs):
    queries = kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load())
    with pytest.raises(kernel.ModelQueryError) as error:
        getattr(queries, method)(*args, **kwargs)
    assert error.value.error_code in {
        "MODEL_ANCHOR_ID_INVALID", "MODEL_RECORD_ID_INVALID"}


@pytest.mark.parametrize("method", ("flow_declaration", "flows_involving_port"))
def test_flow_query_context_is_exact_and_typed(method):
    queries = kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load())
    anchor = ABSENT_FLOW if method == "flow_declaration" else REGISTERED_PORT
    with pytest.raises(kernel.ModelQueryError) as error:
        getattr(queries, method)(anchor, context={
            "kind": "view_independent", "fallback": "as_operated"})
    assert error.value.error_code == "MODEL_CONTEXT_INVALID"
