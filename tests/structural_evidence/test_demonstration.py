"""SN-001 completion demonstration (DM1, DM2) — base-only.

One coherent chain over the COMMITTED artifacts: showcase source bytes ->
raw identity/checksum -> frozen extraction -> structural claims -> subject
rules -> SourceSubjectRefs -> the committed BindingAssertions and exact
binding revisions -> canonical anchors -> the accepted model records and
model revision -> the definition-level hierarchy and the extruder's
variable -> the existing Moonraker observation, unchanged. Every arrow
states its disclosure kind; every count is pinned against the
hand-authored golden multiset in SOURCES.md.
"""

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from backend.data_sources.contracts import ExtractionResult
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import ModelQueries, ModelStore
from backend.structural_evidence.claims import (
    CsvStructuralReading,
    csv_structural_claims,
    step_structural_claims,
)
from backend.structural_evidence.contracts import UnknownEngineeringContext
from backend.structural_evidence.reconcile import StructuralReconciler
from backend.structural_evidence.rules import SUBJECT_RULES

from tests.model_kernel.test_demo_model import (
    ASSEMBLY_TYPE,
    CURRENT_REVISION,
    EXTRUDER,
    UNIT_TYPE,
)

SHOWCASE = Path("showcases/demo-printer")
MANIFEST = json.loads((SHOWCASE / "MANIFEST.json").read_text("utf-8"))
RESOLUTION_AT = datetime(2026, 8, 11, 13, 0, 0, tzinfo=UTC)
UNKNOWN = UnknownEngineeringContext(kind="unknown",
                                    reason="source_declares_no_view")
HOTEND = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"

# hand-authored from SOURCES.md — never from the reconciler
GOLDEN_FINDING_COUNTS = Counter({
    "corroborated_by_all_mapped_sources": 1,
    "supported_by_step_only": 1,
    "quantity_not_reconcilable_with_registered_instances": 1,
    "claims_not_comparable": 1,
    "context_unknown": 3,
    "duplicate_source_label_not_identity": 1,
    "derived_usage_path_ambiguous": 2,
    "absence_is_not_evidence_of_absence": 3,
    "source_subject_unmapped": 20,
})

BINDING_REVISIONS = {
    "demo-printer": ("rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e2"
                     "6759b745240e60b93"),
    "demo-printer-model": ("rev_bf16a154f7ab89a0e820f5d2917bf1e7361d24381"
                           "d10c9c208e6092846532d99"),
}
REL_S7 = ("rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c"
          "78fcf0d5")


def showcase_claims():
    """[verified_in_supplied_context] source bytes match the manifest;
    [computed_result] claims derive from the FROZEN extractions."""
    claim_sets = {}
    for source_id, entry in MANIFEST["sources"].items():
        payload = (SHOWCASE / entry["source_file"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == entry["source_sha256"]
        extraction = ExtractionResult.model_validate_json(
            (SHOWCASE / entry["frozen_extraction_file"]).read_text("utf-8"))
        assert extraction.raw_record_id == entry["pinned_raw_record_id"]
        if source_id == "showcase-printer-bom":
            claim_sets[source_id] = csv_structural_claims(
                extraction, source_id=source_id,
                payload_checksum=entry["pinned_payload_checksum"],
                engineering_context=UNKNOWN,
                reading=CsvStructuralReading(
                    quantity_column_index=2, parent_column_index=4,
                    parent_matches_column_index=0))
        else:
            claim_sets[source_id] = step_structural_claims(
                extraction, source_id=source_id,
                payload_checksum=entry["pinned_payload_checksum"],
                engineering_context=UNKNOWN)
    # the declared label column (index 1) is part of the reading
    from backend.structural_evidence.contracts import LabelFieldRef
    claim_sets["showcase-printer-bom"] = claim_sets[
        "showcase-printer-bom"].model_copy(update={
            "label_field": LabelFieldRef(column_index=1,
                                         column_name_as_extracted="name")})
    return claim_sets


def committed_reconciler():
    """[authority_declaration] the committed BindingAssertions;
    [verified_in_supplied_context] the committed 14-record model."""
    resolvers = [
        BindingResolver(BindingStore(Path("bindings/demo-printer")).load()),
        BindingResolver(BindingStore(
            Path("bindings/demo-printer-model")).load())]
    model = ModelStore(Path("models/demo-printer")).load()
    assert model.revision.revision_id == CURRENT_REVISION
    return StructuralReconciler(
        resolvers=resolvers, rules=tuple(SUBJECT_RULES.values()),
        model=model,
        required_binding_set_ids=frozenset(BINDING_REVISIONS)), model


class TestDM1TheCompleteChain:
    def test_the_golden_finding_multiset_and_every_arrow(self):
        claim_sets = showcase_claims()
        reconciler, model = committed_reconciler()
        result = reconciler.reconcile(list(claim_sets.values()),
                                      resolution_at=RESOLUTION_AT)

        # [computed_result] the finding multiset, pinned to the oracle
        assert Counter(f.finding for f in result.findings) == \
            GOLDEN_FINDING_COUNTS

        # [computed_result] every participating revision carried VERBATIM
        assert {p.binding_set_id: p.revision.revision_id
                for p in result.participations} == BINDING_REVISIONS
        assert result.model_revision.revision_id == CURRENT_REVISION

        # [computed_result] the join: BOM row and STEP definition bind the
        # SAME canonical extruder anchor
        joined = {rs.join_anchor_id
                  for d in result.claim_sets
                  for rs in d.resolved_subjects if rs.join_anchor_id}
        assert joined == {EXTRUDER, ASSEMBLY_TYPE}
        [corroborated] = [f for f in result.findings
                          if f.finding == "corroborated_by_all_mapped_sources"]
        assert corroborated.anchor_id == EXTRUDER
        assert corroborated.model_disclosures[0].verified == \
            "verified_in_supplied_revision"
        kinds = {c.claim_kind for c in corroborated.supporting_claims}
        assert kinds == {"bom_row", "step_part_definition"}

        # [computed_result] proposals: honestly nothing to propose
        proposal_result = reconciler.propose(result)
        assert proposal_result.status == "not_proposable"
        assert proposal_result.proposals == ()

        # [computed_result] the definition-level hierarchy, queried by its
        # EXPLICIT type name, reaches the extruder-unit type
        queries = ModelQueries(model)
        definition_tree = queries.descendants(
            ASSEMBLY_TYPE, "assembly_definition_contains",
            view="as_designed")
        assert [s.anchor.anchor_id for s in definition_tree.steps] == \
            [UNIT_TYPE]
        [supporting] = definition_tree.steps[0].supporting
        assert supporting.record_id == REL_S7
        # [declared_reference_only] the structural citation on that record
        arm_refs = [d for d in supporting.evidence
                    if d.ref.kind == "structural_source_locator"]
        assert len(arm_refs) == 1
        assert arm_refs[0].verification == "declared_reference"
        assert arm_refs[0].ref.raw_record_id == \
            MANIFEST["sources"]["showcase-printer-cad"][
                "pinned_raw_record_id"]

        # [computed_result] the structurally identified extruder owns the
        # already-bound temperature variable
        owned = queries.variables_of(EXTRUDER)
        assert [e.anchor.anchor_id for e in owned.entries] == [HOTEND]

    def test_every_subject_is_accounted_for(self):
        claim_sets = showcase_claims()
        reconciler, _ = committed_reconciler()
        result = reconciler.reconcile(list(claim_sets.values()),
                                      resolution_at=RESOLUTION_AT)
        # 12 BOM subjects + 11 STEP subjects, none silently dropped
        subject_bearing = [rs for d in result.claim_sets
                           for rs in d.resolved_subjects
                           if rs.subject is not None]
        assert len(subject_bearing) == 23


class TestDM2TheMoonrakerLegIsUntouched:
    def test_variable_value_compatibility_is_identical_under_14_records(
            self, tmp_path):
        """The VS-001 demonstration result — the model requires
        degree_celsius, the source supplied no unit, the value is 60.4 —
        is byte-identical under the enlarged model."""
        from backend.model_state import ModelStateQueries
        from backend.observation_compatibility import (
            ObservationCompatibilityQueries,
        )
        from tests.model_state.helpers import full_timeline_stack

        temporal = full_timeline_stack(tmp_path)
        model = ModelStore(Path("models/demo-printer")).load()
        resolver = BindingResolver(
            BindingStore(Path("bindings/demo-printer")).load())
        state = ModelStateQueries(model, resolver, temporal)
        result = ObservationCompatibilityQueries(
            state).variable_value_compatibility(
            HOTEND, as_of=datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC),
            entity_anchor_id=EXTRUDER)
        assert result.state.model_membership == "registered"
        assert result.specification_result.status == "specified"
        [candidate] = result.candidates
        occurrence = candidate.state_candidate.bound.observed.occurrence
        assert occurrence.value_json == "60.4"
        assert occurrence.declared_unit is None
        assert candidate.value_shape_compatibility == "satisfies_value_shape"
        assert candidate.unit_lexeme_not_evaluated_reason == \
            "source_unit_absent"
        assert (result.specification_result.specification.unit.unit.code
                == "degree_celsius")
