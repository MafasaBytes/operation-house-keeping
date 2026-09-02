"""VP-001 Slice B public query/result contract red baseline."""

import inspect
from typing import get_args

import backend.model_kernel as kernel


RESULT_FIELDS = {
    "VariablePortAssociationRootResult": {
        "root_record_index", "lineage_record_indices", "current_tip_indices",
        "withdrawal_indices", "lineage_health"},
    "VariablePortAssociationResult": {
        "material", "variable_anchor_id", "port_anchor_id", "context",
        "endpoint_status", "owner_alignment", "variable_registration_index",
        "variable_owner_registration_index", "port_registration_index",
        "port_owner_registration_index", "conclusion", "lineage_summary",
        "roots"},
    "VariablePortAssociationEntry": {
        "entry_index", "variable_anchor_id", "port_anchor_id",
        "variable_registration_index", "variable_owner_registration_index",
        "port_registration_index", "port_owner_registration_index",
        "conclusion", "lineage_summary", "roots"},
    "VariablePortsResult": {
        "material", "variable_anchor_id", "context", "status",
        "variable_registration_index", "owner_registration_index", "entries"},
    "PortVariablesResult": {
        "material", "port_anchor_id", "context", "status",
        "port_registration_index", "owner_registration_index", "entries"},
    "VariablePortAssertionDisclosureResult": {
        "material", "record_id", "lookup_status", "record_index", "activity",
        "containing_lineage_health", "root_record_index", "successor_indices",
        "withdrawal_indices"},
}


ALIASES = {
    "VariablePortEndpointStatus": (
        "both_registered", "variable_not_registered", "port_not_registered",
        "both_not_registered"),
    "VariablePortOwnerAlignment": (
        "not_evaluated", "same_owner", "different_owners"),
    "VariablePortAssociationConclusion": (
        "not_evaluated", "not_declared", "asserted", "inactive"),
    "VariablePortLineageSummary": (
        "not_applicable", "healthy", "conflicted", "inactive"),
    "VariablePortsStatus": ("variable_not_registered", "registered"),
    "PortVariablesStatus": ("port_not_registered", "registered"),
    "VariablePortAssertionLookupStatus": ("not_found", "found"),
}


def test_exact_public_result_names_fields_and_exports():
    for name, fields in RESULT_FIELDS.items():
        contract = getattr(kernel, name)
        assert set(contract.model_fields) == fields
        assert name in kernel.__all__
    assert {name for name in kernel.__all__ if name.startswith("VariablePort")
            or name.startswith("PortVariables")} == (
                set(RESULT_FIELDS) | set(ALIASES) | {
                    "VariablePortAssociation",
                    "VariablePortAssociationWithdrawal"})
    assert len(kernel.__all__) == 187
    assert len(kernel.__all__) == len(set(kernel.__all__))


def test_exact_named_literal_vocabularies_are_public():
    for name, values in ALIASES.items():
        assert get_args(getattr(kernel, name)) == values
        assert name in kernel.__all__

    annotated_fields = (
        (kernel.VariablePortAssociationResult, "endpoint_status",
         kernel.VariablePortEndpointStatus),
        (kernel.VariablePortAssociationResult, "owner_alignment",
         kernel.VariablePortOwnerAlignment),
        (kernel.VariablePortAssociationResult, "conclusion",
         kernel.VariablePortAssociationConclusion),
        (kernel.VariablePortAssociationResult, "lineage_summary",
         kernel.VariablePortLineageSummary),
        (kernel.VariablePortAssociationEntry, "conclusion",
         kernel.VariablePortAssociationConclusion),
        (kernel.VariablePortAssociationEntry, "lineage_summary",
         kernel.VariablePortLineageSummary),
        (kernel.VariablePortsResult, "status", kernel.VariablePortsStatus),
        (kernel.PortVariablesResult, "status", kernel.PortVariablesStatus),
        (kernel.VariablePortAssertionDisclosureResult, "lookup_status",
         kernel.VariablePortAssertionLookupStatus),
    )
    for contract, field, alias in annotated_fields:
        assert contract.model_fields[field].annotation == alias


def test_exact_query_signatures_and_return_annotations():
    expected = {
        "variable_port_association": (
            ("self", "variable_anchor_id", "port_anchor_id", "context"),
            "VariablePortAssociationResult"),
        "ports_associated_with_variable": (
            ("self", "variable_anchor_id", "context"), "VariablePortsResult"),
        "variables_associated_with_port": (
            ("self", "port_anchor_id", "context"), "PortVariablesResult"),
        "variable_port_assertion": (
            ("self", "record_id"), "VariablePortAssertionDisclosureResult"),
    }
    for name, (parameters, return_name) in expected.items():
        signature = inspect.signature(getattr(kernel.ModelQueries, name))
        assert tuple(signature.parameters) == parameters
        if "context" in signature.parameters:
            assert signature.parameters["context"].kind is \
                inspect.Parameter.KEYWORD_ONLY
        assert signature.return_annotation in {
            getattr(kernel, return_name), return_name}


def test_slice_b_adds_no_state_composition_or_fixture_surface():
    forbidden = {
        "AssociatedPortVariableStateResult", "AssociatedPortVariableStateStatus",
        "associated_port_variable_state", "port_observation", "observed_at_port",
    }
    assert forbidden.isdisjoint(kernel.__all__)
    assert not hasattr(kernel.ModelQueries, "associated_port_variable_state")
