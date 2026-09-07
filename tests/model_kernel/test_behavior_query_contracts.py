"""BH-001 Slice B exact public query and result contracts (red first)."""

import inspect
from pathlib import Path
from typing import get_args

import backend.model_kernel as kernel


ALIASES = {
    "BehaviorLookupStatus": ("not_registered", "registered"),
    "BehaviorDeclarationConclusion": (
        "not_registered", "not_declared", "declared", "conflicted",
        "inactive"),
    "BehaviorRuleLineageSummary": (
        "not_applicable", "healthy", "conflicted", "inactive"),
    "BehaviorAgreementFinding": (
        "one_healthy_root", "corroborating_healthy_roots",
        "same_root_conflict", "cross_root_effective_body_disagreement",
        "inactive_roots_present"),
    "VariableBehaviorsStatus": ("variable_not_registered", "registered"),
    "BehaviorAssertionLookupStatus": ("not_found", "found"),
}

RESULT_FIELDS = {
    "BehaviorEffectiveBodyGroupResult": (
        "group_index", "representative_declaration_index",
        "current_tip_indices", "root_record_indices"),
    "BehaviorRuleRootResult": (
        "root_record_index", "lineage_record_indices", "current_tip_indices",
        "withdrawal_indices", "lineage_health",
        "effective_body_group_indices"),
    "BehaviorLookupResult": (
        "material", "behavior_anchor_id", "status", "registration_index",
        "participant_variable_registration_indices",
        "participant_owner_registration_indices"),
    "BehaviorRuleResult": (
        "material", "behavior_anchor_id", "context", "conclusion",
        "lineage_summary", "agreement_findings", "registration_index",
        "roots", "effective_body_groups", "current_declaration_indices"),
    "VariableBehaviorEntry": (
        "entry_index", "behavior_anchor_id", "other_variable_anchor_id",
        "behavior_registration_index", "other_variable_registration_index",
        "other_owner_registration_index", "conclusion", "lineage_summary",
        "agreement_findings", "roots", "effective_body_groups",
        "current_declaration_indices"),
    "VariableBehaviorsResult": (
        "material", "variable_anchor_id", "context", "status",
        "variable_registration_index", "owner_registration_index", "entries"),
    "BehaviorAssertionDisclosureResult": (
        "material", "record_id", "lookup_status", "record_index", "activity",
        "containing_lineage_health", "containing_subject_conclusion",
        "containing_agreement_findings", "root_record_index",
        "successor_indices", "withdrawal_indices"),
}


def test_exact_public_aliases_and_literal_order():
    for name, values in ALIASES.items():
        alias = getattr(kernel, name)
        assert get_args(alias) == values
        assert name in kernel.__all__


def test_exact_public_result_names_ordered_fields_and_exports():
    for name, fields in RESULT_FIELDS.items():
        contract = getattr(kernel, name)
        assert tuple(contract.model_fields) == fields
        assert name in kernel.__all__
    assert len(kernel.__all__) == 205
    assert len(kernel.__all__) == len(set(kernel.__all__))
    assert {name for name in kernel.__all__
            if name.startswith("Behavior") or name.startswith("VariableBehavior")
            } == set(ALIASES) | set(RESULT_FIELDS) | {
                "BehaviorRegistration", "BehaviorRuleDeclaration",
                "BehaviorRuleWithdrawal", "BehaviorVariableSemanticLock"}


def test_exact_field_annotations_use_named_aliases():
    cases = (
        ("BehaviorLookupResult", "status", "BehaviorLookupStatus"),
        ("BehaviorRuleResult", "conclusion",
         "BehaviorDeclarationConclusion"),
        ("BehaviorRuleResult", "lineage_summary",
         "BehaviorRuleLineageSummary"),
        ("VariableBehaviorEntry", "conclusion",
         "BehaviorDeclarationConclusion"),
        ("VariableBehaviorEntry", "lineage_summary",
         "BehaviorRuleLineageSummary"),
        ("VariableBehaviorsResult", "status", "VariableBehaviorsStatus"),
        ("BehaviorAssertionDisclosureResult", "lookup_status",
         "BehaviorAssertionLookupStatus"),
    )
    for contract_name, field, alias_name in cases:
        assert getattr(kernel, contract_name).model_fields[field].annotation == \
            getattr(kernel, alias_name)


def test_exact_four_query_signatures_and_no_aliases():
    expected = {
        "behavior": (("self", "behavior_anchor_id"), "BehaviorLookupResult"),
        "behavior_declaration": (
            ("self", "behavior_anchor_id", "context"), "BehaviorRuleResult"),
        "behaviors_involving_variable": (
            ("self", "variable_anchor_id", "context"),
            "VariableBehaviorsResult"),
        "behavior_assertion": (
            ("self", "record_id"), "BehaviorAssertionDisclosureResult"),
    }
    public = {name for name, member in inspect.getmembers(
        kernel.ModelQueries, inspect.isfunction)
        if not name.startswith("_") and "behavior" in name}
    assert public == set(expected)
    for name, (parameters, return_name) in expected.items():
        signature = inspect.signature(getattr(kernel.ModelQueries, name))
        assert tuple(signature.parameters) == parameters
        if "context" in signature.parameters:
            assert signature.parameters["context"].kind is \
                inspect.Parameter.KEYWORD_ONLY
        assert signature.return_annotation in {
            getattr(kernel, return_name), return_name}


def test_slice_b_exports_no_evaluator_port_or_outcome_surface():
    forbidden = {
        "behavior_at_port", "behaviors_involving_port",
        "BehaviorEvaluationResult", "BehaviorEvaluationQueries",
        "BehaviorComputedRelation", "BehaviorParticipantSource",
        "BehaviorValidity", "BehaviorHealth", "BehaviorOutcome",
    }
    assert forbidden.isdisjoint(kernel.__all__)


def test_slice_b_and_c_acceptance_and_slice_d_gate_status_are_exact():
    final_status = (
        "BH-001 complete, owner accepted, adversarially reviewed, full-suite "
        "verified, and dual-clean-checkout verified."
    )
    living_paths = (
        Path("CLAUDE.md"),
        Path("backend/model_kernel/README.md"),
        Path("docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md"),
        Path("docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md"),
    )
    for path in living_paths:
        normalized = " ".join(path.read_text(encoding="utf-8").split())
        assert "05177f7306ce745d093bd5f11abafc13a6274d0f" in normalized
        assert "8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521" in normalized
        assert final_status in normalized
    historical_paths = (
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-b-implementation-plan.md"),
        Path("docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md"),
    )
    for path in historical_paths:
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "05177f7306ce745d093bd5f11abafc13a6274d0f" in normalized, path
        assert "8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521" in normalized, path
