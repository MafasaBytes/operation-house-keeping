"""ES-001 completion demonstration over committed, offline fixtures.

The chain is model declaration -> identity attachment -> frozen occurrence ->
authority interpretation -> three independent token comparisons.  Every
lower-layer result and every evidence byte remains owned by its producer.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from backend.model_kernel import ModelQueries, ModelStore
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.source_interpretation import InterpretationResolver, InterpretationStore
from tests.model_kernel.test_demo_model import (
    ES001_MODEL_RECORDS, PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION)
from tests.model_state.helpers import PROP_TEMP, SUBJECT
from tests.observation_compatibility.test_demo_compatibility import (
    AS_OF, EXTRUDER, HOTEND, LATEST_CHECKSUM, LATEST_OCCURRENCE_ID,
    LATEST_RAW_RECORD_ID, SPECIFICATION_ID, committed)
from tests.source_interpretation.test_demo_interpretations import RECORD_IDS

DEMO_INTERPRETATIONS = Path("interpretations/demo-printer")
EARLY = datetime(2026, 8, 7, 19, 0, tzinfo=UTC)


def tree_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


def stack(tmp_path, *, model=None, interpretations=None):
    values, state, temporal = committed(tmp_path, model=model)
    loaded = (interpretations if interpretations is not None else
              InterpretationStore(DEMO_INTERPRETATIONS).load())
    facade = SemanticCompatibilityQueries(values, InterpretationResolver(loaded))
    return facade, values, state, temporal


def test_complete_committed_es001_chain_and_upstream_immutability(tmp_path):
    facade, values, state, temporal = stack(tmp_path)
    evidence_root = temporal.store.evidence_root
    before_temporal = temporal.store.ordered_logical_dump()
    before_evidence = tree_bytes(evidence_root)
    ledger_roots = tuple(Path(path) for path in (
        "models/demo-printer", "bindings/demo-printer",
        "bindings/demo-printer-model", "interpretations/demo-printer"))
    before_ledgers = {root: tree_bytes(root) for root in ledger_roots}

    result = facade.variable_semantic_compatibility(
        HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    [candidate] = result.candidates
    occurrence = candidate.value_candidate.state_candidate.bound.observed.occurrence

    # Every accepted lower-layer result is carried verbatim.
    direct_value = values.variable_value_compatibility(
        HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    assert result.value_compatibility == direct_value
    assert result.value_compatibility.state == state.variable_state(
        HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    assert result.value_compatibility.specification_result == ModelQueries(
        state.model).variable_value_specification(HOTEND)
    assert result.semantics_result == ModelQueries(
        state.model).variable_semantics(HOTEND)
    assert candidate.interpretation == InterpretationResolver(
        InterpretationStore(DEMO_INTERPRETATIONS).load()
    ).resolve_property_interpretations(
        SUBJECT, PROP_TEMP, at=occurrence.received_at)

    # Every authority-declaration arrow in the accepted diagram is named.
    assert result.value_compatibility.state.variable_registration.record_id == (
        "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7")
    assert result.value_compatibility.specification_result.specification\
        .record_id == SPECIFICATION_ID
    assert tuple(summary.record_id for summary in
                 candidate.value_candidate.state_candidate.bound.resolution
                 .via_assertions) == (
        "iba_b1b86a4fd0c56f36aafb4574176429c0edab530dbbd5d1da954a54f2533fd90c",
    )
    assert {
        result.semantics_result.quantity_kind.declaration.record_id,
        result.semantics_result.observation_role.declaration.record_id,
    } == set(ES001_MODEL_RECORDS)
    interpretation_ids = {
        summary.record_id
        for dimension in (candidate.interpretation.quantity_kind,
                          candidate.interpretation.observation_role,
                          candidate.interpretation.unit)
        for summary in dimension.via_assertions
    }
    assert interpretation_ids == set(RECORD_IDS)

    # Frozen evidence and provenance remain the accepted 60.4 chain.
    assert occurrence.value_json == "60.4"
    assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
    assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
    assert occurrence.payload_checksum == LATEST_CHECKSUM
    assert occurrence.declared_unit is None

    # Model and authority agree on all three identity-token dimensions while
    # the source-unit fact remains independently absent.
    assert candidate.quantity_kind_compatibility == "token_identical"
    assert candidate.observation_role_compatibility == "token_identical"
    assert candidate.unit_identity_compatibility == "unit_identity_exact"
    assert candidate.value_candidate.source_unit_evidence == "absent"
    assert candidate.semantic_findings == (
        "declared_semantics_compatible",
        "source_unit_absent_but_interpreted",
        "unit_identity_exact",
    )
    assert result.ruleset_version == "es001.1"

    # Read-only means both the projection and preserved evidence are exactly
    # byte/logically unchanged after the complete query.
    assert temporal.store.ordered_logical_dump() == before_temporal
    assert tree_bytes(evidence_root) == before_evidence
    assert {root: tree_bytes(root) for root in ledger_roots} == before_ledgers


def test_semantic_tokens_never_enter_committed_source_evidence_subtree(tmp_path):
    facade, _, _, temporal = stack(tmp_path)
    candidate = facade.variable_semantic_compatibility(
        HOTEND, as_of=AS_OF).candidates[0]
    source_tree = candidate.value_candidate.state_candidate.model_dump(
        mode="json")
    text = json.dumps(source_tree, sort_keys=True)
    semantic_needles = (
        "degree_celsius", "ohk-units-1", "project_local", "measured_actual",
        "ohk-observation-roles-1", "celsius", "Celsius", "kelvin",
        "fahrenheit", "temperature_unit", *ES001_MODEL_RECORDS, *RECORD_IDS)
    for token in semantic_needles:
        assert token not in text
        assert token.encode() not in b"".join(
            tree_bytes(temporal.store.evidence_root).values())
    assert '"declared_unit": null' in text
    assert candidate.interpretation.unit.interpretation.unit.code == (
        "degree_celsius")
    assert candidate.value_candidate.state_candidate.bound.observed.occurrence == (
        temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF).occurrence)


def test_pre_es001_model_replay_reports_meaning_absence_over_same_evidence(
        tmp_path):
    model_store = ModelStore(Path("models/demo-printer"))
    replayed = model_store.replay(PRE_ES001_MEMBERSHIP)
    assert replayed.revision.revision_id == PRE_ES001_REVISION
    assert replayed.revision.record_count == 14
    facade, values, _, _ = stack(tmp_path, model=replayed)
    result = facade.variable_semantic_compatibility(HOTEND, as_of=AS_OF)
    [candidate] = result.candidates
    assert result.semantics_result.quantity_kind.status == "not_declared"
    assert result.semantics_result.observation_role.status == "not_declared"
    assert candidate.quantity_kind_not_evaluated_reason == (
        "model_meaning_not_declared")
    assert candidate.observation_role_not_evaluated_reason == (
        "model_meaning_not_declared")
    assert candidate.value_candidate.state_candidate.bound.observed.occurrence\
        .value_json == "60.4"
    assert result.value_compatibility == values.variable_value_compatibility(
        HOTEND, as_of=AS_OF)


def test_empty_interpretation_revision_reports_honest_absence(tmp_path):
    empty = InterpretationStore(tmp_path / "empty" / "demo-printer").load()
    facade, _, _, _ = stack(tmp_path, interpretations=empty)
    result = facade.variable_semantic_compatibility(HOTEND, as_of=AS_OF)
    [candidate] = result.candidates
    assert result.interpretation_revision.record_count == 0
    assert candidate.interpretation.quantity_kind.status == "not_declared"
    assert candidate.interpretation.observation_role.status == "not_declared"
    assert candidate.interpretation.unit.status == "not_declared"
    assert candidate.quantity_kind_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert candidate.observation_role_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert candidate.unit_identity_not_evaluated_reason == (
        "source_interpretation_not_declared")
    assert candidate.semantic_findings == (
        "source_interpretation_not_declared",)


def test_early_cutoff_has_no_observation_and_no_semantic_verdict(tmp_path):
    facade, values, _, _ = stack(tmp_path)
    result = facade.variable_semantic_compatibility(HOTEND, as_of=EARLY)
    [candidate] = result.candidates
    assert candidate.value_candidate.state_candidate.bound is None
    assert candidate.interpretation is None
    assert candidate.quantity_kind_not_evaluated_reason == "no_observation"
    assert candidate.observation_role_not_evaluated_reason == "no_observation"
    assert candidate.unit_identity_not_evaluated_reason == "no_observation"
    assert candidate.semantic_findings == ("observation_absent",)
    assert result.value_compatibility == values.variable_value_compatibility(
        HOTEND, as_of=EARLY)


def test_demo_is_offline_and_uses_only_frozen_fixture_stack():
    import ast

    source = Path(__file__).read_text()
    tree = ast.parse(source)
    forbidden = {"socket", "requests", "httpx", "urllib"}
    imports = {alias.name.split(".")[0]
               for node in ast.walk(tree)
               if isinstance(node, (ast.Import, ast.ImportFrom))
               for alias in node.names}
    assert imports.isdisjoint(forbidden)
