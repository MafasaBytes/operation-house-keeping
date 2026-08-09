"""VS-001 Part A: store validation, the multi-parent specification DAG,
tip computation, conflict surfacing, and convergence.

The governing rule: competing current tips are SURFACED, never fatal. A
conflicted lineage leaves the revision loadable, queryable, and
replayable, and a record superseding every current tip converges it —
including after repeated contention."""

import json

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    ModelKernelError,
    ModelQueries,
    ModelStore,
    VariableValueSpecification,
)
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    VAR_A,
    VAR_B,
    declared_unit,
    registration,
    specification,
    store_with,
    variable_registration,
)


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def world(tmp_path, *extra):
    """A registered variable A (owned by entity A) plus anything else."""
    return store_with(tmp_path, registration(ENT_A),
                      variable_registration(VAR_A, owner=ENT_A), *extra)


def tips(loaded, anchor_id=VAR_A):
    return loaded.current_specification_tips_by_variable.get(anchor_id, ())


class TestReferenceClosure:
    def test_specification_requires_its_variable_registration(self, tmp_path):
        store = store_with(tmp_path, registration(ENT_A))
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(specification())
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        assert str(tmp_path) not in str(excinfo.value)
        assert snapshot(store) == before

    def test_crafted_load_without_the_registration_fails(self, tmp_path):
        record = specification()
        store = world(tmp_path, record)
        registration_file = (store.records_dir
                             / f"{variable_registration(VAR_A).record_id}.json")
        registration_file.unlink()
        with pytest.raises(ModelKernelError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        assert record.record_id in str(excinfo.value)

    def test_replay_subset_must_include_the_registration(self, tmp_path):
        record = specification()
        store = world(tmp_path, record)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([record.record_id])
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        closed = store.replay([registration(ENT_A).record_id,
                               variable_registration(VAR_A).record_id,
                               record.record_id])
        assert tips(closed) == (record,)

    def test_a_valid_specification_never_leaks_an_untyped_error(self, tmp_path):
        """The record-kind bucket dispatch must know the new kind: a missing
        arm raises a raw KeyError straight through load/append/replay."""
        record = specification()
        loaded = world(tmp_path, record).load()
        assert loaded.specifications == {record.record_id: record}
        assert validate_record_collection(
            "demo-printer", dict(loaded.records)).revision == loaded.revision


class TestParentValidation:
    def test_missing_parent_is_typed(self, tmp_path):
        orphan = specification(supersedes=("vsp_" + "1" * 64,), note="orphan")
        with pytest.raises(ModelKernelError) as excinfo:
            world(tmp_path, orphan)
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_cross_variable_parent_rejected(self, tmp_path):
        first = specification(variable_anchor_id=VAR_A)
        alien = specification(variable_anchor_id=VAR_B,
                              supersedes=(first.record_id,))
        with pytest.raises(ModelKernelError) as excinfo:
            store_with(tmp_path, registration(ENT_A),
                       variable_registration(VAR_A, owner=ENT_A),
                       variable_registration(VAR_B, owner=ENT_A),
                       first, alien)
        assert excinfo.value.error_code == "MODEL_SPECIFICATION_LINEAGE_INVALID"
        assert "specifies a different variable" in str(excinfo.value)

    def test_self_reference_rejected(self, tmp_path):
        record = specification()
        forged = VariableValueSpecification.model_construct(
            **{**record.model_dump(), "supersedes": (record.record_id,)})
        with pytest.raises(ModelKernelError) as excinfo:
            world(tmp_path).append(forged)
        # the contract guard catches it during revalidation, before any
        # store-level lineage pass sees it
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        with pytest.raises(ValidationError):
            VariableValueSpecification(
                **{**record.model_dump(), "supersedes": (record.record_id,)})

    def test_cycle_rejected(self, tmp_path):
        """A crafted two-record cycle: each names the other as parent."""
        first = specification(note="first")
        second = specification(note="second", supersedes=(first.record_id,))
        cyclic_first = VariableValueSpecification.model_construct(
            **{**first.model_dump(), "supersedes": (second.record_id,)})
        collection = {registration(ENT_A).record_id: registration(ENT_A),
                      variable_registration(VAR_A).record_id:
                          variable_registration(VAR_A),
                      first.record_id: cyclic_first,
                      second.record_id: second}
        with pytest.raises(ModelKernelError) as excinfo:
            validate_record_collection("demo-printer", collection,
                                       verify_hashes=False)
        # pin the CYCLE guard specifically: without the message assertion
        # the zero-tip defence-in-depth branch satisfies this test with the
        # same error code, and a regression in the DAG walk would pass
        assert excinfo.value.error_code == "MODEL_SPECIFICATION_LINEAGE_INVALID"
        assert "supersession cycle" in str(excinfo.value)


class TestTipsAndConflict:
    def test_single_root_is_the_tip(self, tmp_path):
        record = specification()
        loaded = world(tmp_path, record).load()
        assert tips(loaded) == (record,)
        assert loaded.specification_superseded_by == {record.record_id: ()}

    def test_linked_chain_has_one_tip(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second", supersedes=(first.record_id,))
        loaded = world(tmp_path, first, second).load()
        assert tips(loaded) == (second,)
        assert loaded.specification_superseded_by[first.record_id] == (
            second.record_id,)

    def test_two_independent_tips_conflict_without_invalidating(self, tmp_path):
        """The central rule: a conflict is surfaced, never fatal."""
        first = specification(note="first")
        second = specification(note="second")
        store = world(tmp_path, first, second)
        loaded = store.load()                       # loads
        assert tips(loaded) == tuple(
            sorted([first, second], key=lambda r: r.record_id))
        replayed = store.replay(list(loaded.records))   # replays
        assert len(tips(replayed)) == 2
        queries = ModelQueries(loaded)                  # every query answers
        assert queries.variable(VAR_A).status == "registered"
        assert queries.entity(ENT_A).status == "registered"

    def test_tips_are_never_chosen_by_recency_or_authority(self, tmp_path):
        from datetime import UTC, datetime

        early = specification(note="early",
                              recorded_at=datetime(2026, 1, 1, tzinfo=UTC))
        late = specification(note="late",
                             recorded_at=datetime(2026, 12, 31, tzinfo=UTC))
        forward = world(tmp_path / "a", early, late).load()
        backward = world(tmp_path / "b", late, early).load()
        assert len(tips(forward)) == 2
        assert tips(forward) == tips(backward)       # append order irrelevant

    def test_partial_convergence_remains_conflicted(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second")
        partial = specification(note="partial", supersedes=(first.record_id,))
        loaded = world(tmp_path, first, second, partial).load()
        assert {record.record_id for record in tips(loaded)} == {
            second.record_id, partial.record_id}

    def test_full_convergence_restores_one_tip(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second")
        merged = specification(note="merged", supersedes=(
            first.record_id, second.record_id))
        loaded = world(tmp_path, first, second, merged).load()
        assert tips(loaded) == (merged,)
        assert sorted(loaded.specification_superseded_by[first.record_id]) == [
            merged.record_id]

    def test_repeated_contention_converges_again(self, tmp_path):
        """Two writers each converge the same tips; their convergence
        records then compete, and a third record converges those."""
        first = specification(note="first")
        second = specification(note="second")
        merge_a = specification(note="merge-a", supersedes=(
            first.record_id, second.record_id))
        merge_b = specification(note="merge-b", supersedes=(
            first.record_id, second.record_id))
        store = world(tmp_path, first, second, merge_a, merge_b)
        contended = store.load()
        assert {record.record_id for record in tips(contended)} == {
            merge_a.record_id, merge_b.record_id}
        final = specification(note="final", supersedes=(
            merge_a.record_id, merge_b.record_id))
        store.append(final)
        assert tips(store.load()) == (final,)

    def test_specification_for_another_variable_is_independent(self, tmp_path):
        mine = specification(variable_anchor_id=VAR_A)
        theirs = specification(variable_anchor_id=VAR_B)
        loaded = store_with(tmp_path, registration(ENT_A),
                            variable_registration(VAR_A, owner=ENT_A),
                            variable_registration(VAR_B, owner=ENT_A),
                            mine, theirs).load()
        assert tips(loaded, VAR_A) == (mine,)
        assert tips(loaded, VAR_B) == (theirs,)


class TestAppendAndReplay:
    def test_identical_reappend_is_a_validated_no_op(self, tmp_path):
        record = specification()
        store = world(tmp_path, record)
        before = snapshot(store)
        revision = store.load().revision
        assert store.append(record) == record.record_id
        assert snapshot(store) == before
        assert store.load().revision == revision

    def test_replay_before_during_and_after_convergence(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second")
        merged = specification(note="merged", supersedes=(
            first.record_id, second.record_id))
        store = world(tmp_path, first, second, merged)
        base = [registration(ENT_A).record_id,
                variable_registration(VAR_A).record_id]

        before = store.replay([*base, first.record_id])
        assert tips(before) == (first,)                      # ancestor governs
        during = store.replay([*base, first.record_id, second.record_id])
        assert len(tips(during)) == 2                        # conflicted
        after = store.replay([*base, first.record_id, second.record_id,
                              merged.record_id])
        assert tips(after) == (merged,)                      # converged
        assert len({before.revision.revision_id, during.revision.revision_id,
                    after.revision.revision_id}) == 3

    def test_successor_without_its_ancestry_is_rejected(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second", supersedes=(first.record_id,))
        store = world(tmp_path, first, second)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([registration(ENT_A).record_id,
                          variable_registration(VAR_A).record_id,
                          second.record_id])
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_unsorted_parents_on_disk_load_normalized(self, tmp_path):
        """Accepted precedent (evidence tuples): on-disk array order is not
        canonically enforced; post-normalization content is."""
        first = specification(note="first")
        second = specification(note="second")
        merged = specification(note="merged", supersedes=(
            first.record_id, second.record_id))
        store = world(tmp_path, first, second, merged)
        path = store.records_dir / f"{merged.record_id}.json"
        payload = json.loads(path.read_text())
        payload["supersedes"] = list(reversed(payload["supersedes"]))
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        loaded = store.load()
        assert tips(loaded) == (merged,)
        assert loaded.records[merged.record_id].supersedes == merged.supersedes

    def test_tampered_specification_detected(self, tmp_path):
        record = specification()
        store = world(tmp_path, record)
        path = store.records_dir / f"{record.record_id}.json"
        payload = json.loads(path.read_text())
        payload["unit"]["unit"]["code"] = "kelvin"
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        with pytest.raises(ModelKernelError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_RECORD_HASH_MISMATCH"

    def test_specifications_do_not_enter_other_buckets(self, tmp_path):
        record = specification()
        loaded = world(tmp_path, record).load()
        assert record.record_id not in loaded.registrations_by_anchor
        assert record.record_id not in loaded.variable_registrations_by_anchor
        assert len(loaded.variable_registrations_by_anchor) == 1
        assert loaded.types == {} and loaded.assertions == {}


class TestSpecificationQuery:
    """The kernel query is the SINGLE source of specification status."""

    def test_specified(self, tmp_path):
        record = specification()
        loaded = world(tmp_path, record).load()
        result = ModelQueries(loaded).variable_value_specification(VAR_A)
        assert result.status == "specified"
        assert result.specification == record          # verbatim
        assert result.conflicting_specifications == ()
        assert result.superseded_specification_ids == ()
        assert result.anchor_id == VAR_A
        assert result.revision == loaded.revision

    def test_not_specified_for_a_registered_variable(self, tmp_path):
        loaded = world(tmp_path).load()
        result = ModelQueries(loaded).variable_value_specification(VAR_A)
        assert result.status == "not_specified"
        assert result.specification is None

    def test_not_registered_variable(self, tmp_path):
        loaded = world(tmp_path).load()
        result = ModelQueries(loaded).variable_value_specification(VAR_B)
        assert result.status == "not_registered"
        assert result.specification is None
        assert result.superseded_specification_ids == ()

    def test_conflicted_carries_every_tip_verbatim(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second")
        loaded = world(tmp_path, first, second).load()
        result = ModelQueries(loaded).variable_value_specification(VAR_A)
        assert result.status == "conflicted"
        assert result.specification is None
        assert set(result.conflicting_specifications) == {first, second}
        ids = [record.record_id for record in result.conflicting_specifications]
        assert ids == sorted(ids)

    def test_superseded_history_disclosed(self, tmp_path):
        first = specification(note="first")
        second = specification(note="second", supersedes=(first.record_id,))
        loaded = world(tmp_path, first, second).load()
        result = ModelQueries(loaded).variable_value_specification(VAR_A)
        assert result.status == "specified"
        assert result.specification == second
        assert result.superseded_specification_ids == (first.record_id,)

    @pytest.mark.parametrize("bad", [
        pytest.param(ENT_A, id="entity_id"), pytest.param(None, id="none"),
        pytest.param(123, id="int"), pytest.param([], id="unhashable"),
        pytest.param("", id="empty"),
    ])
    def test_input_is_typed(self, tmp_path, bad):
        queries = ModelQueries(world(tmp_path).load())
        with pytest.raises(ModelKernelError) as excinfo:
            queries.variable_value_specification(bad)
        assert excinfo.value.error_code == "MODEL_ANCHOR_ID_INVALID"

    def test_replayed_revision_answers_for_that_membership(self, tmp_path):
        record = specification()
        store = world(tmp_path, record)
        old = store.replay([registration(ENT_A).record_id,
                            variable_registration(VAR_A).record_id])
        result = ModelQueries(old).variable_value_specification(VAR_A)
        assert result.status == "not_specified"
        assert result.revision == old.revision


class TestSupersededHistoryIsPerVariable:
    def test_history_never_leaks_another_variables_lineage(self, tmp_path):
        a_old = specification(variable_anchor_id=VAR_A, note="a-old")
        a_new = specification(variable_anchor_id=VAR_A, note="a-new",
                              supersedes=(a_old.record_id,))
        b_old = specification(variable_anchor_id=VAR_B, note="b-old")
        b_new = specification(variable_anchor_id=VAR_B, note="b-new",
                              supersedes=(b_old.record_id,))
        loaded = store_with(tmp_path, registration(ENT_A),
                            variable_registration(VAR_A, owner=ENT_A),
                            variable_registration(VAR_B, owner=ENT_A),
                            a_old, a_new, b_old, b_new).load()
        queries = ModelQueries(loaded)
        assert queries.variable_value_specification(
            VAR_A).superseded_specification_ids == (a_old.record_id,)
        assert queries.variable_value_specification(
            VAR_B).superseded_specification_ids == (b_old.record_id,)
