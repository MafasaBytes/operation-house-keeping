"""D6: `assembly_definition_contains` is a second, non-merging containment
lineage (D6-1..D6-6, I1c).

The kernel enforces the separation structurally: endpoint kinds are
load-bearing in both directions, and every hierarchy query is per
(type_name x view), so the definition-level lineage cannot merge into the
physical/logical `contains` hierarchy and is never presented as it.
"""

import json
from pathlib import Path

import pytest

from backend.model_kernel import ModelIntegrityError, ModelQueries, ModelStore

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    assertion,
    contains_type,
    registration,
    store_with,
)
from tests.model_kernel.test_demo_model import (
    ASSEMBLY_TYPE,
    DEMO_MODEL,
    ROOT,
    UNIT_TYPE,
    eleven_ids,
)


def definition_contains_type(**overrides):
    from backend.model_kernel import build_record
    from backend.model_kernel.contracts import RelationshipTypeDefinition
    from tests.model_kernel.builders import AUTHORITY, T0

    fields = dict(
        type_name="assembly_definition_contains",
        forward_label="assembly definition contains",
        inverse_label="assembly definition is contained in",
        directionality="directed",
        source_referent_kinds=("type_definition",),
        target_referent_kinds=("type_definition",),
        self_relation_allowed=False, hierarchy_semantics="containment",
        context_requirement="lifecycle_view", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


class TestD6Separation:
    def test_d6_1_the_contains_projection_is_semantically_unchanged(self):
        """K8/1: compare the REPLAYED pre-SN-001 projection with the
        current one on semantic content — the embedded revision
        necessarily differs and is excluded."""
        store = ModelStore(DEMO_MODEL)
        current = ModelQueries(store.load())
        replayed = ModelQueries(store.replay(eleven_ids(store.load())))
        before = replayed.descendants(ROOT, "contains", view="as_built")
        after = current.descendants(ROOT, "contains", view="as_built")
        assert before.model_dump(exclude={"revision"}) == \
            after.model_dump(exclude={"revision"})
        assert before.revision != after.revision  # 11 vs 14

    def test_d6_2_the_definition_lineage_is_anchor_disjoint(self):
        queries = ModelQueries(ModelStore(DEMO_MODEL).load())
        definition = queries.descendants(
            ASSEMBLY_TYPE, "assembly_definition_contains",
            view="as_designed")
        assert definition.status == "complete"
        definition_anchors = {step.anchor.anchor_id
                              for step in definition.steps}
        assert definition_anchors == {UNIT_TYPE}
        physical = queries.descendants(ROOT, "contains", view="as_built")
        physical_anchors = {step.anchor.anchor_id for step in physical.steps}
        assert definition_anchors.isdisjoint(physical_anchors | {ROOT})

    def test_d6_3_type_anchors_have_no_contains_parent(self):
        queries = ModelQueries(ModelStore(DEMO_MODEL).load())
        for anchor in (UNIT_TYPE, ASSEMBLY_TYPE):
            result = queries.parents(anchor, "contains", view="as_built")
            assert result.status == "no_declared_parent"
            assert result.supporting == ()

    def test_d6_4_definition_type_rejects_physical_endpoints(self, tmp_path):
        rtd = definition_contains_type()
        edge = assertion(rtd)  # ENT_A/ENT_B are physical_instance anchors
        with pytest.raises(ModelIntegrityError) as err:
            store_with(tmp_path, registration(ENT_A), registration(ENT_B),
                       rtd, edge)
        assert "MODEL_ENDPOINT_KIND" in str(err.value)

    def test_d6_5_contains_rejects_type_definition_endpoints(self, tmp_path):
        rtd = contains_type()
        edge = assertion(rtd)
        with pytest.raises(ModelIntegrityError) as err:
            store_with(tmp_path,
                       registration(ENT_A, kind="type_definition"),
                       registration(ENT_B, kind="type_definition"),
                       rtd, edge)
        assert "MODEL_ENDPOINT_KIND" in str(err.value)

    def test_d6_6_never_presented_as_the_hierarchy(self):
        """The committed type record's note states the separation; no
        SN-001 prose calls the definition lineage 'the hierarchy'."""
        [rtd_path] = [p for p in (DEMO_MODEL / "records").glob("rtd_*.json")
                      if json.loads(p.read_text()).get("type_name")
                      == "assembly_definition_contains"]
        note = json.loads(rtd_path.read_text())["note"].lower()
        assert "second" in note and "non-merging" in note
        assert "never" in note and "the hierarchy" in note
        readme = Path("backend/structural_evidence/README.md").read_text(
            "utf-8")
        assert "assembly_definition_contains is the hierarchy" not in readme

    def test_i1c_the_type_name_literal_appears_exactly_once_in_the_ledger(
            self):
        occurrences = 0
        records = sorted((DEMO_MODEL / "records").glob("*.json"))
        assert len(records) == 34
        for path in records:
            occurrences += path.read_text("utf-8").count(
                "assembly_definition_contains")
        assert occurrences == 1  # the rtd type_name field, nowhere else
