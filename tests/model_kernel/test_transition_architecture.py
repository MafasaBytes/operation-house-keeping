"""ST-002 Slice A scope, preservation, and historical-replay gates."""

import ast
import hashlib
import json
from pathlib import Path

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import verify_record_id
from tests.model_kernel.st001_slice_d_rehearsal import inventory_digest
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CN001_MEMBERSHIP,
    CURRENT_REVISION,
    FL001_MEMBERSHIP,
    GOLDEN_REVISION,
    PRE_BH001_REVISION,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION,
    PRE_ST001_REVISION,
    PRE_FL001_REVISION,
    PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    ST001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")
TRANSITION_INDEX_NAMES = (
    "transition_registrations",
    "transition_registrations_by_anchor",
    "transition_anchor_ids_by_subject_entity",
    "transition_registration_id_by_ordered_subject_endpoints",
    "transition_declarations",
    "transition_declaration_ids_by_key",
    "transition_declaration_parent_ids",
    "transition_declaration_successor_ids",
    "transition_declaration_root_by_id",
    "transition_declaration_ancestry_by_id",
    "current_transition_declaration_tips_by_root",
    "transition_declaration_withdrawals",
    "transition_declaration_withdrawn_by",
    "transition_declaration_withdrawals_by_target",
)


def test_slice_b_public_query_surface_adds_exactly_four_transition_queries():
    public_methods = {
        name for name, value in vars(kernel.ModelQueries).items()
        if not name.startswith("_") and callable(value)
    }
    assert public_methods == {
        "ancestors", "behavior", "behavior_assertion",
        "behavior_declaration", "behaviors_involving_variable", "children",
        "connections_containing", "connections_exact", "connections_of_port",
        "constraint_declaration", "constraints_of_variable", "descendants",
        "entity", "hierarchy_health", "interface_compatibility", "parents",
        "port", "port_assertion", "port_interface",
        "ports_associated_with_variable", "ports_of_entity", "relationships",
        "state", "state_assertion", "state_declaration", "states_of_entity",
        "transition", "transition_assertion", "transition_declaration",
        "transitions_of_entity", "flow", "flow_assertion",
        "flow_declaration", "flows_involving_port",
        "variable", "variable_port_assertion", "variable_port_association",
        "variable_semantics", "variable_value_specification",
        "variables_associated_with_port", "variables_of",
    }
    for forbidden in (
        "assess_transition", "detect_transition",
        "transition_assessment", "transition_occurrence", "transition_history",
        "current_transition", "possible_transitions", "enabled_transitions",
        "next_state", "transition_path",
    ):
        assert forbidden not in public_methods


def test_slice_b_kernel_exports_exact_transition_contract_and_result_surface():
    assert len(kernel.__all__) == 203
    assert {name for name in kernel.__all__
            if name.startswith("Transition")} == {
        "TransitionRegistration", "TransitionStateDeclarationPin",
        "TransitionDeclaration", "TransitionDeclarationWithdrawal",
        "TransitionLookupStatus", "TransitionDeclarationConclusion",
        "TransitionDeclarationLineageSummary", "TransitionAgreementFinding",
        "TransitionEndpointRole", "TransitionEndpointPinAlignment",
        "TransitionAssertionLookupStatus", "TransitionEndpointResult",
        "TransitionEffectiveBodyGroupResult",
        "TransitionDeclarationRootResult", "TransitionLookupResult",
        "TransitionDeclarationResult", "TransitionAssertionDisclosureResult",
    }
    for forbidden in (
        "TransitionAssessment", "TransitionOccurrence",
    ):
        assert not hasattr(kernel, forbidden)


def test_import_direction_and_assessment_remains_an_upper_sibling():
    forbidden_imports = (
        "backend.state_classification", "backend.behavior_evaluation",
        "backend.constraint_evaluation", "backend.semantic_compatibility",
        "backend.observation_compatibility", "backend.model_state",
        "backend.temporal_state", "backend.identity_binding",
        "backend.source_interpretation", "backend.data_sources",
        "backend.structural_evidence", "backend.transition_assessment",
    )
    imports = []
    for path in Path("backend/model_kernel").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
    assert not any(name.startswith(forbidden_imports) for name in imports)
    assert Path("backend/transition_assessment").is_dir()
    assert not Path("backend/transition_occurrence").exists()
    assert Path("backend/model_kernel/transition_results.py").is_file()
    helper = Path(
        "tests/model_kernel/st002_slice_a_helpers.py").read_text(encoding="utf-8")
    assert "mint_transition_anchor" not in helper
    assert "uuid4" not in helper


def test_authoritative_36_record_ledger_is_byte_frozen_and_transition_empty():
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    inventory = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }
    loaded = kernel.ModelStore(DEMO_MODEL).load()
    assert len(paths) == loaded.revision.record_count == 36
    assert loaded.revision.record_ids == FL001_MEMBERSHIP
    assert loaded.revision.revision_id == CURRENT_REVISION == (
        "mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee")
    assert inventory_digest(inventory) == (
        "bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a")
    assert sum(path.name.startswith("srg_") for path in paths) == 1
    assert sum(path.name.startswith("std_") for path in paths) == 1
    assert not any(path.name.startswith(("stw_", "trg_", "trd_", "trw_"))
                   for path in paths)
    assert all(verify_record_id(record) for record in loaded.records.values())
    for name in TRANSITION_INDEX_NAMES:
        assert getattr(loaded, name) == {}


def test_explicit_historical_memberships_replay_with_empty_immutable_indexes():
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
        (FL001_MEMBERSHIP, CURRENT_REVISION, 36),
    )
    store = kernel.ModelStore(DEMO_MODEL)
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        for name in TRANSITION_INDEX_NAMES:
            mapping = getattr(loaded, name)
            assert mapping == {}
            with pytest.raises(TypeError):
                mapping["forged"] = ()


def test_accepted_st_owner_gate_artifacts_and_completion_report_are_frozen():
    paths = {
        Path("docs/superpowers/reports/"
             "2026-08-31-st001-slice-d-candidate-identities.json"):
            "990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7",
        Path("docs/superpowers/reports/"
             "2026-08-31-st001-slice-d-candidate-disclosure.json"):
            "23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9",
        Path("docs/superpowers/reports/"
             "2026-08-31-st001-slice-d-completion-report.md"):
            "2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3",
    }
    for path, digest in paths.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    manifest = json.loads(next(iter(paths)).read_bytes())
    assert manifest["content"]["candidate_contract"]["revision"][
        "revision_id"] == PRE_FL001_REVISION
