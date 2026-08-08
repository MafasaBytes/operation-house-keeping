"""MK-001 assertion-lineage lifecycle: the five disclosure states,
competing successors, withdrawal semantics, and both-facts disclosure."""

from datetime import UTC, datetime

from backend.model_kernel.queries import ModelQueries

from tests.model_kernel.builders import (
    AS_BUILT,
    ENT_A,
    ENT_B,
    assertion,
    contains_type,
    containment_world,
    withdrawal,
)


def build(tmp_path, kind, *records):
    store = containment_world(tmp_path)
    for record in records:
        store.append(record)
    return ModelQueries(store.load())


def relationships(queries):
    return queries.relationships(ENT_B, direction="incoming",
                                 context=AS_BUILT)


class TestSupersession:
    def test_successor_resolves_predecessor_disclosed(self, tmp_path):
        kind = contains_type()
        v1 = assertion(kind, note="v1")
        v2 = assertion(kind, note="v2 corrected", supersedes=v1.record_id)
        queries = build(tmp_path, kind, v1, v2)
        result = relationships(queries)
        assert [s.record_id for s in result.active] == [v2.record_id]
        assert [s.record_id for s in result.inactive] == [v1.record_id]
        assert result.inactive[0].superseded_by == (v2.record_id,)
        assert result.inactive[0].supersedes is None
        assert result.active[0].supersedes == v1.record_id
        parents = queries.parents(ENT_B, "contains", view="as_built")
        assert parents.supporting[0].record_id == v2.record_id

    def test_competing_successors_disclosed_never_timestamp_resolved(
        self, tmp_path
    ):
        kind = contains_type()
        v1 = assertion(kind, note="v1")
        v2a = assertion(kind, note="fix a", supersedes=v1.record_id)
        v2b_late = assertion(kind, note="fix b", supersedes=v1.record_id)
        queries = build(tmp_path, kind, v1, v2a, v2b_late)
        result = relationships(queries)
        assert {s.record_id for s in result.active} == {
            v2a.record_id, v2b_late.record_id}
        assert len(result.lineage_conflicts) == 1
        conflict = result.lineage_conflicts[0]
        assert conflict.predecessor_id == v1.record_id
        assert conflict.competing_successor_ids == tuple(sorted(
            [v2a.record_id, v2b_late.record_id]))
        # same parent asserted by both successors: hierarchy is CORROBORATED,
        # not conflicted — lineage dispute and hierarchy conflict are
        # independent facts
        parents = queries.parents(ENT_B, "contains", view="as_built")
        assert parents.status == "resolved"
        assert len(parents.supporting) == 2


class TestWithdrawal:
    def test_withdrawn_is_disclosed_not_erased(self, tmp_path):
        kind = contains_type()
        edge = assertion(kind)
        gone = withdrawal(edge)
        queries = build(tmp_path, kind, edge, gone)
        result = relationships(queries)
        assert result.active == ()
        assert result.inactive[0].withdrawn_by == (gone.record_id,)
        # withdrawn ≠ never-asserted, observable from the result alone
        assert queries.parents(ENT_B, "contains", view="as_built").status == (
            "no_declared_parent")

    def test_withdrawing_superseded_predecessor_changes_nothing(self, tmp_path):
        kind = contains_type()
        v1 = assertion(kind, note="v1")
        v2 = assertion(kind, note="v2", supersedes=v1.record_id)
        queries = build(tmp_path, kind, v1, v2, withdrawal(v1))
        result = relationships(queries)
        assert [s.record_id for s in result.active] == [v2.record_id]
        both = result.inactive[0]
        assert both.superseded_by == (v2.record_id,)   # both facts disclosed
        assert both.withdrawn_by != ()

    def test_withdrawing_active_successor_never_reactivates(self, tmp_path):
        kind = contains_type()
        v1 = assertion(kind, note="v1")
        v2 = assertion(kind, note="v2", supersedes=v1.record_id)
        queries = build(tmp_path, kind, v1, v2, withdrawal(v2))
        result = relationships(queries)
        assert result.active == ()  # the lineage ends with no active claim
        assert {s.record_id for s in result.inactive} == {
            v1.record_id, v2.record_id}
        assert queries.parents(ENT_B, "contains", view="as_built").status == (
            "no_declared_parent")

    def test_multiple_withdrawals_all_disclosed_sorted(self, tmp_path):
        kind = contains_type()
        edge = assertion(kind)
        first = withdrawal(edge, note="first")
        second = withdrawal(edge, note="second")
        queries = build(tmp_path, kind, edge, first, second)
        result = relationships(queries)
        assert result.inactive[0].withdrawn_by == tuple(sorted(
            [first.record_id, second.record_id]))
