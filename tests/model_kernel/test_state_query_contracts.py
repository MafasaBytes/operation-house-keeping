"""ST-001 Slice B exact public query contracts (red first)."""

import inspect
from typing import get_args

import backend.model_kernel as kernel


ALIASES = {
    "StateLookupStatus": ("not_registered", "registered"),
    "StateDeclarationConclusion": (
        "not_registered", "not_declared", "declared", "conflicted",
        "inactive"),
    "StateDeclarationLineageSummary": (
        "not_applicable", "healthy", "conflicted", "inactive"),
    "StateAgreementFinding": (
        "one_healthy_root", "corroborating_healthy_roots",
        "same_root_conflict", "cross_root_effective_body_disagreement",
        "inactive_roots_present"),
    "EntityStatesStatus": ("entity_not_registered", "registered"),
    "StateAssertionLookupStatus": ("not_found", "found"),
}

RESULT_FIELDS = {
    "StateConditionReferenceResult": (
        "condition_index", "constraint_anchor_id",
        "constraint_registration_index", "pinned_declaration_index",
        "target_variable_registration_index",
        "target_owner_registration_index"),
    "StateEffectiveBodyGroupResult": (
        "group_index", "representative_declaration_index",
        "current_tip_indices", "root_record_indices", "conditions"),
    "StateDeclarationRootResult": (
        "root_record_index", "lineage_record_indices",
        "current_tip_indices", "withdrawal_indices", "lineage_health",
        "effective_body_group_indices"),
    "StateLookupResult": (
        "material", "state_anchor_id", "status", "registration_index",
        "subject_entity_registration_index",
        "condition_constraint_registration_indices",
        "condition_variable_registration_indices",
        "condition_owner_registration_indices"),
    "StateDeclarationResult": (
        "material", "state_anchor_id", "context", "conclusion",
        "lineage_summary", "agreement_findings", "registration_index",
        "roots", "effective_body_groups", "current_declaration_indices"),
    "EntityStateEntry": (
        "entry_index", "state_anchor_id", "state_registration_index",
        "conclusion", "lineage_summary", "agreement_findings", "roots",
        "effective_body_groups", "current_declaration_indices"),
    "EntityStatesResult": (
        "material", "entity_anchor_id", "context", "status",
        "entity_registration_index", "entries"),
    "StateAssertionDisclosureResult": (
        "material", "record_id", "lookup_status", "record_index",
        "activity", "containing_lineage_health",
        "containing_subject_conclusion", "containing_agreement_findings",
        "root_record_index", "successor_indices", "withdrawal_indices"),
}

SLICE_B_EXPORTS = (
    "StateLookupStatus",
    "StateDeclarationConclusion",
    "StateDeclarationLineageSummary",
    "StateAgreementFinding",
    "EntityStatesStatus",
    "StateAssertionLookupStatus",
    "StateConditionReferenceResult",
    "StateEffectiveBodyGroupResult",
    "StateDeclarationRootResult",
    "StateLookupResult",
    "StateDeclarationResult",
    "EntityStateEntry",
    "EntityStatesResult",
    "StateAssertionDisclosureResult",
)


def test_exact_state_query_aliases_and_literal_order():
    for name, values in ALIASES.items():
        alias = getattr(kernel, name)
        assert get_args(alias) == values
        assert name in kernel.__all__


def test_exact_state_query_result_names_fields_and_exports():
    for name, fields in RESULT_FIELDS.items():
        contract = getattr(kernel, name)
        assert tuple(contract.model_fields) == fields
        assert name in kernel.__all__
    assert len(kernel.__all__) == 203
    assert len(kernel.__all__) == len(set(kernel.__all__))
    start = kernel.__all__.index(SLICE_B_EXPORTS[0])
    assert tuple(kernel.__all__[start:start + len(SLICE_B_EXPORTS)]) == \
        SLICE_B_EXPORTS
    assert {name for name in kernel.__all__
            if name.startswith("State") or name.startswith("EntityState")} == (
        set(ALIASES) | set(RESULT_FIELDS) | {
            "StateRegistration", "StateConstraintDeclarationPin",
            "StateDeclaration", "StateDeclarationWithdrawal",
        })


def test_state_query_fields_use_named_public_aliases():
    cases = (
        ("StateLookupResult", "status", "StateLookupStatus"),
        ("StateDeclarationResult", "conclusion",
         "StateDeclarationConclusion"),
        ("StateDeclarationResult", "lineage_summary",
         "StateDeclarationLineageSummary"),
        ("EntityStateEntry", "conclusion", "StateDeclarationConclusion"),
        ("EntityStateEntry", "lineage_summary",
         "StateDeclarationLineageSummary"),
        ("EntityStatesResult", "status", "EntityStatesStatus"),
        ("StateAssertionDisclosureResult", "lookup_status",
         "StateAssertionLookupStatus"),
    )
    for contract_name, field, alias_name in cases:
        assert getattr(kernel, contract_name).model_fields[field].annotation == \
            getattr(kernel, alias_name)
    assert kernel.StateDeclarationRootResult.model_fields[
        "lineage_health"].annotation == kernel.ContainingLineageHealth
    assertion = kernel.StateAssertionDisclosureResult.model_fields
    assert assertion["activity"].annotation == kernel.AssertionActivity | None
    assert assertion["containing_lineage_health"].annotation == \
        kernel.ContainingLineageHealth | None


def test_every_state_query_result_has_exact_frozen_revalidation_config():
    for name in RESULT_FIELDS:
        config = getattr(kernel, name).model_config
        assert config["frozen"] is True
        assert config["extra"] == "forbid"
        assert config["revalidate_instances"] == "always"


def test_exact_four_state_query_signatures_and_no_aliases():
    expected = {
        "state": (("self", "state_anchor_id"), "StateLookupResult"),
        "state_declaration": (
            ("self", "state_anchor_id", "context"),
            "StateDeclarationResult"),
        "states_of_entity": (
            ("self", "entity_anchor_id", "context"),
            "EntityStatesResult"),
        "state_assertion": (
            ("self", "record_id"), "StateAssertionDisclosureResult"),
    }
    public = {name for name, member in inspect.getmembers(
        kernel.ModelQueries, inspect.isfunction)
        if not name.startswith("_") and "state" in name}
    assert public == set(expected)
    for name, (parameters, return_name) in expected.items():
        signature = inspect.signature(getattr(kernel.ModelQueries, name))
        assert tuple(signature.parameters) == parameters
        if "context" in signature.parameters:
            assert signature.parameters["context"].kind is \
                inspect.Parameter.KEYWORD_ONLY
        assert signature.return_annotation in {
            getattr(kernel, return_name), return_name}


def test_slice_b_exports_no_classification_transition_or_family_surface():
    forbidden = {
        "StateClassificationQueries", "StateClassificationResult",
        "StateConditionSource", "StateComputedMatch", "StateFamily",
        "StateSpace", "StateTransition", "states_of_variable",
        "states_of_port", "current_state", "classify_states",
    }
    assert forbidden.isdisjoint(kernel.__all__)
