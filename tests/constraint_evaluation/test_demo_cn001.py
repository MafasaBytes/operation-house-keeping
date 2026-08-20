"""CN-001 Slice C: bounded committed fixture and full recomputable demo."""

import hashlib
import json
from pathlib import Path

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.model_kernel import ModelQueries, ModelStore
from backend.semantic_compatibility import SemanticCompatibilityQueries
from tests.constraint_evaluation.helpers import (
    AS_OF, CON_B, EXTRUDER, HOTEND, LATE, cn_stack, constraint_registration,
    craft_value)
from tests.model_kernel.test_demo_model import (
    CN001_MEMBERSHIP, CN001_MODEL_RECORDS, CURRENT_REVISION,
    FROZEN_ES001_MODEL_RECORDS, FROZEN_MK001_RECORDS,
    FROZEN_SN001_MODEL_RECORDS, FROZEN_VM001_RECORD,
    FROZEN_VS001_RECORD, PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION, PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION, VS001_MEMBERSHIP, GOLDEN_REVISION)
from tests.observation_compatibility.test_demo_compatibility import (
    LATEST_ATTEMPT_ID, LATEST_CHECKSUM,
    LATEST_OCCURRENCE_ID, LATEST_RAW_RECORD_ID, committed)
from tests.model_state.test_demo_join import LATEST_OBSERVATION_ID
from tests.semantic_compatibility.test_demo_semantics import stack as es_stack

DEMO_MODEL = Path("models/demo-printer")
CONSTRAINT = "con_4b768cf843f5474cb5e564e31d239a59"
REGISTRATION_ID, DECLARATION_ID = CN001_MODEL_RECORDS
REGISTRATION_SHA256 = "4eb7f531e9932a60cd73573f66323b543235bc98ac8663d4e158ef3c732e5abd"
DECLARATION_SHA256 = "ee99560f5272e324c13bbc8beef2a3fb28a45ba92c1aaec9ae62d0d0cbb860d1"
DISCLAIMER = (
    "This declaration is an illustrative synthetic test fixture used only "
    "to demonstrate CN-001 evaluation mechanics. It makes no claim about a "
    "real printer, safe operating limit, manufacturer specification, alarm "
    "threshold, recommended setting, or required action."
)
REGISTRATION_EVIDENCE = (
    "Synthetic CN-001 demonstration-only association between the minted "
    "constraint identity and the demo hotend variable; it describes neither "
    "real equipment nor a real engineering limit."
)
WARNING = (
    "Constraint verdicts are exact predicate outcomes only; they express no "
    "safety, alarm, severity, diagnosis, control, or recommended action."
)
ARTIFACT_BYTES = 37886
ARTIFACT_SHA256 = "0061dd735a241168fa0eb7e15fb92a35743c35357bf5d701c5220f31ec0a786c"


def _loaded_declaration():
    result = ModelQueries(ModelStore(DEMO_MODEL).load()).constraint_declaration(
        CONSTRAINT)
    assert result.status == "declared"
    return result


def _evaluation(tmp_path):
    cn, _, _, temporal = cn_stack(tmp_path, include_committed_constraints=True)
    result = cn.constraint_evaluation(
        CONSTRAINT, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    return result, temporal


def _artifact_bytes(tmp_path):
    result, temporal = _evaluation(tmp_path)
    candidate = result.semantic_compatibility.candidates[0]
    occurrence = candidate.value_candidate.state_candidate.bound.observed.occurrence
    assessment = result.candidates[0].boundary_assessments[0]
    resolution = candidate.value_candidate.state_candidate.bound.resolution
    payload = {
        "artifact": "CN-001 demo-printer constraint evaluation",
        "source": {"raw_record_id": occurrence.raw_record_id,
                   "payload_checksum": occurrence.payload_checksum,
                   "extraction_route": {
                       "source_id": occurrence.subject.source_id,
                       "adapter_id": occurrence.subject.adapter_id,
                       "subject_identifier": occurrence.subject.subject_identifier,
                       "route": occurrence.property.extraction_route,
                       "item_key": occurrence.property.item_key,
                       "json_pointer": occurrence.property.json_pointer}},
        "temporal": {"occurrence_id": occurrence.occurrence_id,
                     "attempt_id": occurrence.attempt_id,
                     "observation_id": occurrence.observation_id},
        "binding": {"revision": result.semantic_compatibility.value_compatibility.state.binding_revision.model_dump(mode="json"),
                    "via_assertions": [item.record_id for item in resolution.via_assertions]},
        "anchors": {"entity": EXTRUDER, "variable": HOTEND,
                    "constraint": CONSTRAINT},
        "model_revision": result.constraint.revision.model_dump(mode="json"),
        "variable_membership_and_state": result.semantic_compatibility.value_compatibility.state.model_dump(mode="json"),
        "variable_specification": result.semantic_compatibility.value_compatibility.specification_result.specification.model_dump(mode="json"),
        "observation_compatibility": result.semantic_compatibility.value_compatibility.model_dump(mode="json"),
        "interpretation_revision": result.semantic_compatibility.interpretation_revision.model_dump(mode="json"),
        "source_interpretation": candidate.interpretation.model_dump(mode="json"),
        "semantic_compatibility": {
            "quantity_kind": candidate.quantity_kind_compatibility,
            "observation_role": candidate.observation_role_compatibility,
            "unit_identity": candidate.unit_identity_compatibility,
            "findings": list(candidate.semantic_findings)},
        "constraint_records": {"registration": REGISTRATION_ID,
                               "declaration": DECLARATION_ID},
        "predicate": result.constraint.declaration.predicate.model_dump(mode="json"),
        "evaluation": {"candidate_index": 0,
                       "canonical_observed_decimal": result.candidates[0].observed_decimal,
                       "boundary_assessment": assessment.model_dump(mode="json"),
                       "verdict": result.candidates[0].verdict},
        "evidence_disclaimer": DISCLAIMER,
        "semantic_warning": WARNING,
    }
    # The provenance query must resolve the same immutable source chain.
    chain = temporal.provenance(occurrence.occurrence_id)
    assert chain.raw_record_id == payload["source"]["raw_record_id"]
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


class TestCommittedLedger:
    def test_exact_two_record_append_identity_authority_and_content(self):
        loaded = ModelStore(DEMO_MODEL).load()
        assert loaded.revision.revision_id == CURRENT_REVISION
        assert loaded.revision.record_count == 18
        assert len(loaded.constraint_registrations_by_anchor) == 1
        assert len(loaded.constraint_declarations) == 1
        result = _loaded_declaration()
        assert result.constraint_anchor_id == CONSTRAINT
        assert result.registration.variable_anchor_id == HOTEND
        assert result.registration.anchor.anchor_id == CONSTRAINT
        assert result.declaration.constraint_anchor_id == result.registration.anchor.anchor_id
        assert result.registration.note == REGISTRATION_EVIDENCE
        assert result.registration.evidence[0].statement == REGISTRATION_EVIDENCE
        assert result.registration.authority.model_dump() == {
            "kind": "test_fixture", "agent": "cn001_demo_fixture",
            "method": "manual_declaration"}
        assert result.declaration.authority == result.registration.authority
        assert result.declaration.record_id == DECLARATION_ID
        assert result.registration.record_id == REGISTRATION_ID
        assert result.declaration.note == DISCLAIMER
        assert result.declaration.evidence[0].statement == DISCLAIMER
        predicate = result.declaration.predicate
        assert predicate.kind == "upper_bound"
        assert predicate.upper.value == "80"
        assert predicate.upper.inclusion == "inclusive"
        assert (predicate.model_dump() ==
                {"kind": "upper_bound", "upper": {
                    "value": "80", "inclusion": "inclusive"}})
        assert result.declaration.expected_semantics.model_dump() == {
            "quantity_kind": {"system_id": "project_local",
                              "system_edition": "ohk-quantities-1",
                              "code": "temperature"},
            "observation_role": {"system_id": "project_local",
                                 "system_edition": "ohk-observation-roles-1",
                                 "code": "measured_actual"},
            "unit": {"system_id": "project_local",
                     "system_edition": "ohk-units-1",
                     "code": "degree_celsius"},
        }

    def test_old_sixteen_are_byte_frozen_and_only_two_cn_files_follow(self):
        frozen = {**FROZEN_MK001_RECORDS, **FROZEN_VM001_RECORD,
                  **FROZEN_VS001_RECORD, **FROZEN_SN001_MODEL_RECORDS,
                  **FROZEN_ES001_MODEL_RECORDS}
        assert len(frozen) == 16
        for name, digest in frozen.items():
            assert hashlib.sha256((DEMO_MODEL / "records" / name).read_bytes()).hexdigest() == digest
        assert hashlib.sha256((DEMO_MODEL / "records" / f"{REGISTRATION_ID}.json").read_bytes()).hexdigest() == REGISTRATION_SHA256
        assert hashlib.sha256((DEMO_MODEL / "records" / f"{DECLARATION_ID}.json").read_bytes()).hexdigest() == DECLARATION_SHA256
        assert CN001_MEMBERSHIP == (*PRE_CN001_MEMBERSHIP,
                                    REGISTRATION_ID, DECLARATION_ID)

    def test_explicit_historical_and_current_memberships_replay(self):
        store = ModelStore(DEMO_MODEL)
        historical = store.replay(PRE_CN001_MEMBERSHIP)
        assert historical.revision.revision_id == PRE_CN001_REVISION
        assert historical.revision.record_count == 16
        absent = ModelQueries(historical).constraint_declaration(CONSTRAINT)
        assert absent.status == "not_registered"
        assert not historical.constraint_registrations_by_anchor
        assert not historical.constraint_declarations
        assert store.replay(CN001_MEMBERSHIP).revision.revision_id == CURRENT_REVISION

    def test_every_explicit_pre_cn_membership_has_no_constraint_artifact(self):
        store = ModelStore(DEMO_MODEL)
        histories = (
            (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION),
            (VS001_MEMBERSHIP, GOLDEN_REVISION),
            (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION),
            (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION),
            (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION),
        )
        for membership, revision in histories:
            loaded = store.replay(membership)
            assert loaded.revision.revision_id == revision
            result = ModelQueries(loaded).constraint_declaration(CONSTRAINT)
            assert result.status == "not_registered"
            assert not loaded.constraint_registrations_by_anchor
            assert not loaded.constraint_declarations

    def test_upstream_ledger_counts_and_no_committed_synthetic_observation(self):
        assert len(list(Path("interpretations/demo-printer/records").glob("*.json"))) == 3
        assert len(list(Path("bindings/demo-printer/records").glob("*.json"))) == 6
        assert len(list(Path("bindings/demo-printer-model/records").glob("*.json"))) == 5
        assert not list(Path(".").rglob("spj_*.json"))


class TestEvaluationDemonstration:
    def test_frozen_60_4_chain_is_satisfied_with_complete_provenance(self,
                                                                    tmp_path):
        result, temporal = _evaluation(tmp_path)
        row = result.candidates[0]
        [assessment] = row.boundary_assessments
        es_candidate = result.semantic_compatibility.candidates[0]
        occurrence = es_candidate.value_candidate.state_candidate.bound.observed.occurrence
        assert (occurrence.raw_record_id, occurrence.payload_checksum,
                occurrence.attempt_id, occurrence.observation_id,
                occurrence.occurrence_id) == (
                    LATEST_RAW_RECORD_ID, LATEST_CHECKSUM, LATEST_ATTEMPT_ID,
                    LATEST_OBSERVATION_ID, LATEST_OCCURRENCE_ID)
        assert temporal.provenance(occurrence.occurrence_id).raw_record_id == LATEST_RAW_RECORD_ID
        assert result.constraint.revision.revision_id == CURRENT_REVISION
        assert row.semantic_candidate_index == 0
        assert row.observed_decimal == "60.4"
        assert assessment.side == "upper"
        assert assessment.boundary == result.constraint.declaration.predicate.upper
        assert assessment.boundary.inclusion == "inclusive"
        assert assessment.relation == "below"
        assert assessment.satisfied is True
        assert row.verdict == "satisfied"
        assert "declared_semantics_compatible" in es_candidate.semantic_findings
        assert es_candidate.quantity_kind_compatibility == "token_identical"
        assert es_candidate.observation_role_compatibility == "token_identical"
        assert es_candidate.unit_identity_compatibility == "unit_identity_exact"
        assert {item.record_id for dimension in (
            es_candidate.interpretation.quantity_kind,
            es_candidate.interpretation.observation_role,
            es_candidate.interpretation.unit)
                for item in dimension.via_assertions} == {
            "spi_07548575f798119990ac283484f81f183208223abc31f314ae042242b72848cc",
            "spi_2fef48f888b20a82a9c6f535262112527b194de31f07e02e36a7954a78433b92",
            "spi_5a4eca7a600e2f682514e574d443b22dd0110337c5097902a0920fb6a930682a",
        }

    def test_synthetic_noncommitted_85_is_violated_only_by_predicate(self,
                                                                    tmp_path):
        before = {path: path.read_bytes() for root in (
            Path("evidence"), DEMO_MODEL) for path in root.rglob("*") if path.is_file()}
        cn, _, _, temporal = cn_stack(
            tmp_path, include_committed_constraints=True)
        craft_value(temporal, value_json="85", json_type="number")
        result = cn.constraint_evaluation(CONSTRAINT, as_of=LATE,
                                          entity_anchor_id=EXTRUDER)
        [row] = result.candidates
        [assessment] = row.boundary_assessments
        assert row.observed_decimal == "85"
        assert assessment.relation == "above"
        assert assessment.satisfied is False
        assert row.verdict == "violated"
        dumped = row.model_dump(mode="json")
        for forbidden in ("safety", "alarm", "severity", "diagnostic",
                          "control", "recommended_action"):
            assert forbidden not in dumped
        assert {path: path.read_bytes() for path in before} == before
        assert not list(DEMO_MODEL.rglob("spj_*.json"))

    def test_lookup_and_discovery_agree_without_duplicate_carriage(self,
                                                                  tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, include_committed_constraints=True)
        exact = cn.constraint_evaluation(CONSTRAINT, as_of=AS_OF,
                                         entity_anchor_id=EXTRUDER)
        discovery = cn.variable_constraint_evaluations(
            HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)
        assert len(discovery.constraint_collection.constraints) == 1
        assert len(discovery.evaluations) == 1
        entry = discovery.evaluations[0]
        assert entry.constraint_index == 0
        assert entry.constraint_anchor_id == CONSTRAINT
        assert entry.candidates == exact.candidates
        assert discovery.semantic_compatibility == exact.semantic_compatibility
        serialized = discovery.model_dump(mode="json")
        assert set(serialized["evaluations"][0]) == {
            "constraint_index", "constraint_anchor_id", "candidates"}
        assert serialized["semantic_compatibility"]["ruleset_version"] == "es001.1"
        entry_text = json.dumps(serialized["evaluations"])
        assert REGISTRATION_ID not in entry_text
        assert DECLARATION_ID not in entry_text
        assert "semantic_compatibility" not in entry_text
        assert "constraint_collection" not in entry_text

    def test_unknown_remains_distinct_from_registered_without_declaration(self,
                                                                          tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, include_committed_constraints=True)
        unknown = cn.constraint_evaluation("con_" + "f" * 32, as_of=AS_OF)
        assert unknown.constraint.status == "not_registered"
        assert unknown.candidates == ()
        registered, _, _, _ = cn_stack(
            tmp_path / "registered", constraint_records=(
                constraint_registration(constraint_anchor_id=CON_B),))
        not_declared = registered.constraint_evaluation(CON_B, as_of=AS_OF)
        assert not_declared.constraint.status == "not_declared"
        assert not_declared.candidates[0].not_evaluated_reason == (
            "constraint_not_declared")
        assert all(row.verdict != "violated" for row in not_declared.candidates)

    def test_deterministic_artifact_two_clean_columns(self, tmp_path):
        left = _artifact_bytes(tmp_path / "left")
        right = _artifact_bytes(tmp_path / "right")
        assert left == right
        assert len(left) == ARTIFACT_BYTES
        assert hashlib.sha256(left).hexdigest() == ARTIFACT_SHA256
        assert hashlib.sha256(right).hexdigest() == ARTIFACT_SHA256
        assert DISCLAIMER.encode() in left
        assert WARNING.encode() in left


def test_pre_cn_model_fabricates_no_cn_result_over_same_evidence(tmp_path):
    historical = ModelStore(DEMO_MODEL).replay(PRE_CN001_MEMBERSHIP)
    semantic, _, _, _ = es_stack(tmp_path, model=historical)
    result = ConstraintEvaluationQueries(semantic).constraint_evaluation(
        CONSTRAINT, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    assert result.constraint.status == "not_registered"
    assert result.semantic_compatibility is None
    assert result.candidates == ()
