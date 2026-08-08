"""MK-001 hierarchy projection: distinct-parent/same-child conflicts,
corroboration, cycles, traversal asymmetry, lineage scoping."""

import pytest

from backend.model_kernel.contracts import ModelQueryError
from backend.model_kernel.queries import ModelQueries

from tests.model_kernel.builders import (
    AS_BUILT,
    AS_DESIGNED,
    ENT_A,
    ENT_B,
    ENT_C,
    ENT_D,
    VIEW_FREE,
    assertion,
    contains_type,
    containment_world,
    instance_of_type,
    registration,
    store_with,
)


class TestParents:
    def test_resolved_with_supporting_assertion(self, tmp_path):
        kind = contains_type()
        edge = assertion(kind, source=ENT_A, target=ENT_B)
        store = containment_world(tmp_path, edge)
        result = ModelQueries(store.load()).parents(ENT_B, "contains",
                                                    view="as_built")
        assert result.status == "resolved"
        assert result.parent.anchor_id == ENT_A
        assert [s.record_id for s in result.supporting] == [edge.record_id]
        assert result.revision.record_count == 4

    def test_absence_statuses_are_distinct(self, tmp_path):
        store = containment_world(tmp_path)
        queries = ModelQueries(store.load())
        assert queries.parents(ENT_A, "contains", view="as_built").status == (
            "no_declared_parent")  # never called "root"
        assert queries.parents(ENT_D, "contains", view="as_built").status == (
            "not_registered")
        with pytest.raises(ModelQueryError):
            queries.parents("bogus", "contains", view="as_built")

    def test_distinct_parent_same_child_conflict(self, tmp_path):
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C),
            assertion(kind, source=ENT_A, target=ENT_C),
            assertion(kind, source=ENT_B, target=ENT_C))
        result = ModelQueries(store.load()).parents(ENT_C, "contains",
                                                    view="as_built")
        assert result.status == "conflicted"
        assert [a.anchor_id for a in result.candidate_parents] == sorted(
            [ENT_A, ENT_B])
        assert len(result.supporting) == 2  # every claim disclosed

    def test_same_edge_multiples_are_corroboration(self, tmp_path):
        from backend.model_kernel.contracts import OwnerDeclarationEvidence

        kind = contains_type()
        other_evidence = (OwnerDeclarationEvidence(
            kind="owner_declaration", statement="independent confirmation"),)
        store = containment_world(
            tmp_path,
            assertion(kind, source=ENT_A, target=ENT_B),
            assertion(kind, source=ENT_A, target=ENT_B,
                      evidence=other_evidence))
        result = ModelQueries(store.load()).parents(ENT_B, "contains",
                                                    view="as_built")
        assert result.status == "resolved"        # NOT conflicted
        assert len(result.supporting) == 2        # provenance never merged

    def test_views_are_independent_hierarchies(self, tmp_path):
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C),
            assertion(kind, source=ENT_A, target=ENT_C, context=AS_DESIGNED),
            assertion(kind, source=ENT_B, target=ENT_C, context=AS_BUILT))
        queries = ModelQueries(store.load())
        designed = queries.parents(ENT_C, "contains", view="as_designed")
        built = queries.parents(ENT_C, "contains", view="as_built")
        assert designed.status == built.status == "resolved"
        assert designed.parent.anchor_id == ENT_A
        assert built.parent.anchor_id == ENT_B


class TestCycles:
    def _cycle_world(self, tmp_path, *extra_edges):
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C), registration(ENT_D),
            assertion(kind, source=ENT_A, target=ENT_B),
            assertion(kind, source=ENT_B, target=ENT_A),
            *[assertion(kind, source=s, target=t) for s, t in extra_edges])
        return ModelQueries(store.load())

    def test_direct_cycle_reported_on_members(self, tmp_path):
        queries = self._cycle_world(tmp_path)
        for member in (ENT_A, ENT_B):
            result = queries.parents(member, "contains", view="as_built")
            assert result.status == "cyclic"
            assert result.cycle_members == tuple(sorted([ENT_A, ENT_B]))

    def test_three_node_cycle(self, tmp_path):
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C),
            assertion(kind, source=ENT_A, target=ENT_B),
            assertion(kind, source=ENT_B, target=ENT_C),
            assertion(kind, source=ENT_C, target=ENT_A))
        result = ModelQueries(store.load()).parents(ENT_B, "contains",
                                                    view="as_built")
        assert result.status == "cyclic"
        assert result.cycle_members == tuple(sorted([ENT_A, ENT_B, ENT_C]))

    def test_unaffected_subtree_still_answers(self, tmp_path):
        queries = self._cycle_world(tmp_path, (ENT_C, ENT_D))
        clean = queries.parents(ENT_D, "contains", view="as_built")
        assert clean.status == "resolved"
        assert clean.parent.anchor_id == ENT_C
        ancestors = queries.ancestors(ENT_D, "contains", view="as_built")
        assert ancestors.status == "complete"
        assert [s.anchor.anchor_id for s in ancestors.steps] == [ENT_C]

    def test_cycles_block_both_directions(self, tmp_path):
        queries = self._cycle_world(tmp_path)
        up = queries.ancestors(ENT_A, "contains", view="as_built")
        down = queries.descendants(ENT_A, "contains", view="as_built")
        assert up.status == down.status == "partial"
        assert up.blocked[0].reason == down.blocked[0].reason == "cyclic"
        children = queries.children(ENT_A, "contains", view="as_built")
        assert children.status == "cyclic"


class TestTraversalAsymmetry:
    def _conflict_world(self, tmp_path):
        """A→B, D→B (conflict at B), B→C."""
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C), registration(ENT_D),
            assertion(kind, source=ENT_A, target=ENT_B),
            assertion(kind, source=ENT_D, target=ENT_B),
            assertion(kind, source=ENT_B, target=ENT_C))
        return ModelQueries(store.load())

    def test_ancestors_block_at_the_conflicted_node(self, tmp_path):
        queries = self._conflict_world(tmp_path)
        result = queries.ancestors(ENT_C, "contains", view="as_built")
        assert result.status == "partial"
        assert [s.anchor.anchor_id for s in result.steps] == [ENT_B]
        assert result.blocked == (result.blocked[0],)
        assert result.blocked[0].anchor_id == ENT_B
        assert result.blocked[0].reason == "conflicted"

    def test_descendants_proceed_through_with_annotation(self, tmp_path):
        """Downward traversal is NOT blocked by an incoming-parent conflict;
        each affected step carries a multiple_parents annotation."""
        queries = self._conflict_world(tmp_path)
        result = queries.descendants(ENT_A, "contains", view="as_built")
        assert result.status == "complete"
        step_ids = [s.anchor.anchor_id for s in result.steps]
        assert step_ids == [ENT_B, ENT_C]
        annotated = result.steps[0]
        assert annotated.annotations[0].kind == "multiple_parents"
        assert annotated.annotations[0].candidate_parent_anchor_ids == tuple(
            sorted([ENT_A, ENT_D]))
        assert result.steps[1].annotations == ()

    def test_children_list_annotated_not_blocked(self, tmp_path):
        queries = self._conflict_world(tmp_path)
        result = queries.children(ENT_A, "contains", view="as_built")
        assert result.status == "listed"
        assert result.entries[0].anchor.anchor_id == ENT_B
        assert result.entries[0].annotations[0].kind == "multiple_parents"


class TestHierarchyQueryDiscipline:
    def test_view_required_and_forbidden(self, tmp_path):
        store = containment_world(tmp_path, instance_of_type(),
                                  registration(ENT_C, kind="type_definition"))
        queries = ModelQueries(store.load())
        with pytest.raises(ModelQueryError) as excinfo:
            queries.parents(ENT_B, "contains")
        assert excinfo.value.error_code == "MODEL_VIEW_REQUIRED"
        with pytest.raises(ModelQueryError) as excinfo:
            queries.parents(ENT_B, "instance_of")
        assert excinfo.value.error_code == "MODEL_NOT_A_HIERARCHY"
        with pytest.raises(ModelQueryError) as excinfo:
            queries.parents(ENT_B, "no_such_type", view="as_built")
        assert excinfo.value.error_code == "MODEL_UNKNOWN_TYPE"

    def test_instance_of_never_contributes_ancestry(self, tmp_path):
        contains = contains_type()
        instance_of = instance_of_type()
        store = store_with(
            tmp_path, contains, instance_of, registration(ENT_A),
            registration(ENT_B),
            registration(ENT_C, kind="type_definition"),
            assertion(contains, source=ENT_A, target=ENT_B),
            assertion(instance_of, source=ENT_B, target=ENT_C,
                      context=VIEW_FREE))
        result = ModelQueries(store.load()).ancestors(ENT_B, "contains",
                                                      view="as_built")
        assert [s.anchor.anchor_id for s in result.steps] == [ENT_A]  # no ENT_C


class TestLineageScopedHierarchy:
    def test_stale_assertions_still_project_and_are_flagged(self, tmp_path):
        original = contains_type()
        edge = assertion(original, source=ENT_A, target=ENT_B)
        corrected = contains_type(forward_label="physically contains",
                                  supersedes=original.record_id)
        store = store_with(tmp_path, original, registration(ENT_A),
                           registration(ENT_B), edge, corrected)
        queries = ModelQueries(store.load())
        result = queries.parents(ENT_B, "contains", view="as_built")
        assert result.status == "resolved"                 # still projects
        assert result.supporting[0].cited_type_current is False
        health = queries.hierarchy_health("contains", view="as_built")
        assert health.stale_type_assertions == (edge.record_id,)

    def test_health_reports_cycles_and_conflicts(self, tmp_path):
        kind = contains_type()
        store = store_with(
            tmp_path, kind, registration(ENT_A), registration(ENT_B),
            registration(ENT_C), registration(ENT_D),
            assertion(kind, source=ENT_A, target=ENT_B),
            assertion(kind, source=ENT_B, target=ENT_A),
            assertion(kind, source=ENT_C, target=ENT_D),
            assertion(kind, source=ENT_A, target=ENT_D))
        health = ModelQueries(store.load()).hierarchy_health(
            "contains", view="as_built")
        assert health.cycles[0].members == tuple(sorted([ENT_A, ENT_B]))
        assert health.parent_conflicts[0].child_anchor_id == ENT_D
        assert health.parent_conflicts[0].candidate_parent_anchor_ids == tuple(
            sorted([ENT_A, ENT_C]))
