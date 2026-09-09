"""FL-001 Slice A scope, import, preservation, and replay gates."""

import ast
import hashlib
from pathlib import Path

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.canonical import verify_record_id
from tests.model_kernel.st001_slice_d_rehearsal import inventory_digest
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CN001_MEMBERSHIP,
    GOLDEN_REVISION,
    PRE_BH001_REVISION,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_FL001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION,
    PRE_ST001_REVISION,
    PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    ST001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")
FLOW_INDEX_NAMES = (
    "flow_registrations",
    "flow_registrations_by_anchor",
    "flow_anchor_id_by_semantic_signature",
    "flow_anchor_ids_by_port",
    "flow_role_by_anchor_and_port",
    "flow_declarations",
    "flow_declaration_ids_by_key",
    "flow_declaration_parent_ids",
    "flow_declaration_successor_ids",
    "flow_declaration_root_by_id",
    "flow_declaration_ancestry_by_id",
    "current_flow_declaration_tips_by_root",
    "flow_declaration_effective_body_by_id",
    "flow_declaration_ids_by_effective_body",
    "flow_declaration_withdrawals",
    "flow_declaration_withdrawn_by",
    "flow_declaration_withdrawals_by_target",
)


def test_slice_b_preserves_foundation_and_adds_exact_flow_query_surface():
    assert len(kernel.__all__) == 225
    assert {name for name in kernel.__all__ if name.startswith("Flow")} == {
        "FlowKindToken", "FlowDirectionDeclarationPin",
        "FlowRegistration", "FlowDeclaration",
        "FlowDeclarationWithdrawal", "FlowMeasurementAssociation",
        "FlowMeasurementAssociationWithdrawal", "FlowLookupStatus",
        "FlowDeclarationConclusion", "FlowDeclarationLineageSummary",
        "FlowAgreementFinding", "FlowPortRole",
        "FlowAssertionLookupStatus", "FlowLookupResult",
        "FlowConnectionSupportResult", "FlowDirectionSupportResult",
        "FlowEffectiveBodyGroupResult", "FlowDeclarationRootResult",
        "FlowDeclarationResult", "FlowAssertionDisclosureResult",
        "FlowMeasurementEndpointRegistration",
        "FlowMeasurementReverseRegistration",
        "FlowMeasurementDeclarationPresence",
        "FlowMeasurementDeclarationConclusion",
        "FlowMeasurementSupportKind", "FlowMeasurementSupportActivity",
        "FlowMeasurementSupportLineageHealth",
        "FlowMeasurementSupportAlignment", "FlowMeasurementOrientation",
        "FlowMeasurementAgreementFinding",
        "FlowMeasurementAssertionLookupStatus",
        "FlowMeasurementSupportRow", "FlowMeasurementEffectiveBodyGroupRow",
        "FlowMeasurementRootRow", "FlowMeasurementEntryRow",
        "FlowMeasurementAssociationResult",
        "FlowMeasurementAssociationsForFlowResult",
        "FlowMeasurementAssociationsForVariableResult",
        "FlowMeasurementAssociationsAtPortResult",
        "FlowMeasurementAssertionResult",
    }
    public_methods = {
        name for name, value in vars(kernel.ModelQueries).items()
        if not name.startswith("_") and callable(value)}
    assert public_methods & {
        "flow", "flow_declaration", "flows_involving_port", "flow_assertion",
    } == {"flow", "flow_declaration", "flows_involving_port", "flow_assertion"}
    assert not public_methods & {"assess_flow", "detect_flow", "flow_history"}
    for forbidden in (
        "FlowAssessment", "FlowOccurrence", "ConnectionAnchor",
    ):
        assert not hasattr(kernel, forbidden)


def test_import_direction_and_no_flow_assessment_occurrence_package():
    forbidden_imports = (
        "backend.state_classification", "backend.behavior_evaluation",
        "backend.constraint_evaluation", "backend.semantic_compatibility",
        "backend.observation_compatibility", "backend.model_state",
        "backend.temporal_state", "backend.identity_binding",
        "backend.source_interpretation", "backend.data_sources",
        "backend.structural_evidence",
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
    assert not Path("backend/flow_assessment").exists()
    assert not Path("backend/flow_occurrence").exists()
    assert Path("backend/model_kernel/flow_results.py").is_file()
    helper = Path(
        "tests/model_kernel/fl001_slice_a_helpers.py").read_text(
            encoding="utf-8")
    assert "mint_flow_anchor" not in helper
    assert "uuid4" not in helper


def test_historical_34_record_ledger_is_byte_frozen_and_flow_empty():
    paths = [DEMO_MODEL / "records" / f"{record_id}.json"
             for record_id in ST001_MEMBERSHIP]
    inventory = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths}
    loaded = kernel.ModelStore(DEMO_MODEL).replay(ST001_MEMBERSHIP)
    assert len(paths) == loaded.revision.record_count == 34
    assert loaded.revision.record_ids == ST001_MEMBERSHIP
    assert loaded.revision.revision_id == PRE_FL001_REVISION == (
        "mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41")
    assert inventory_digest(inventory) == (
        "cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd")
    assert not any(path.name.startswith(("trg_", "trd_", "trw_",
                                         "frg_", "fld_", "flw_"))
               for path in paths)


def test_historical_cross_layer_material_did_not_create_flow():
    loaded = kernel.ModelStore(DEMO_MODEL).replay(ST001_MEMBERSHIP)
    assert loaded.port_connections
    assert loaded.port_interface_declarations
    assert loaded.port_compatibility_declarations
    assert loaded.variable_port_associations
    assert loaded.behavior_rule_declarations
    assert loaded.state_declarations
    assert not loaded.transition_declarations
    assert not loaded.flow_registrations
    assert not loaded.flow_declarations
    queries = kernel.ModelQueries(loaded)
    absent = "flo_" + "0" * 32
    context = kernel.LifecycleViewContext(
        kind="lifecycle_view", view="as_operated")
    assert queries.flow(absent).status == "not_registered"
    assert queries.flow_declaration(
        absent, context=context).conclusion == "not_registered"
    for port_anchor_id in loaded.port_registrations_by_anchor:
        assert queries.flows_involving_port(
            port_anchor_id, context=context).entries == ()
    for forbidden in (
        "observed_flow", "commanded_flow", "assess_flow", "detect_flow",
        "flow_occurrence", "flow_rate", "balance", "conservation",
        "upstream", "downstream", "flow_path",
    ):
        assert not hasattr(queries, forbidden)
    assert all(verify_record_id(record) for record in loaded.records.values())
    for name in FLOW_INDEX_NAMES:
        assert getattr(loaded, name) == {}


def test_explicit_historical_memberships_replay_with_empty_flow_indexes():
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
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        for name in FLOW_INDEX_NAMES:
            mapping = getattr(loaded, name)
            assert mapping == {}
            with pytest.raises(TypeError):
                mapping["forged"] = ()


def test_accepted_fl_design_inputs_remain_byte_exact():
    expected = {
        Path("docs/superpowers/proposals/"
             "2026-09-02-fl001-codex-lead-proposal.md"):
            "4ab663af9e5766bb088353c95878b9115fb96973939778fc0fb42ac195dac092",
        Path("docs/superpowers/reports/"
             "2026-09-02-fl001-codex-lead-proposal-challenger-audit.md"):
            "449243118c95eb1296d8d0ffa1373daaa19261d629f8bf16b2383366ba822d3e",
        Path("docs/superpowers/specs/"
             "2026-09-02-fl001-explicit-flow-identity-and-evidence-gated-"
             "flow-declaration-design.md"):
            "4d6ea16b6f2c0f563934212f12dc15d130e39047341ee002e8dd759a8481856a",
    }
    for path, digest in expected.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
