"""Explicit-membership replay separates model revision from temporal cutoff."""

from datetime import timedelta

from tests.model_kernel.builders import CON_A, constraint_declaration, upper_bound
from tests.model_kernel.st001_slice_a_helpers import T0
from tests.state_classification.helpers import (
    AS_OF,
    classify,
    custom_state_model,
    inactive_model,
    reported_constraint_declaration,
)


class _SelectedModel:
    """Test-only provider for one explicitly replayed LoadedModel."""

    def __init__(self, loaded):
        self._loaded = loaded

    def load(self):
        return self._loaded


def test_explicit_membership_not_as_of_selects_pinned_vcn_currentness(tmp_path):
    original = constraint_declaration(CON_A, predicate=upper_bound("80"))
    correction = constraint_declaration(
        CON_A, predicate=upper_bound("90"),
        supersedes=(original.record_id,), recorded_at=T0 + timedelta(hours=1))
    second = reported_constraint_declaration()
    store, _ = custom_state_model(
        tmp_path / "ledger",
        declarations_a=(original, correction), declarations_b=(second,),
        pinned_a=original, pinned_b=second)
    current_membership = store.load().revision.record_ids
    earlier_membership = tuple(
        record_id for record_id in current_membership
        if record_id != correction.record_id)
    earlier_loaded = store.replay(earlier_membership)

    earlier = classify(
        tmp_path / "earlier-evidence",
        model=_SelectedModel(earlier_loaded), as_of=AS_OF)
    later = classify(tmp_path / "later-evidence", model=store, as_of=AS_OF)
    assert earlier.as_of == later.as_of == AS_OF
    assert earlier.state.material.revision != later.state.material.revision
    assert earlier.conditions[0].declaration_alignment == "exact_current"
    assert earlier.computed_match == "matches"
    assert later.conditions[0].declaration_alignment == "superseded"
    assert later.computed_match is None


def test_explicit_membership_omitting_later_stw_revives_declaration(tmp_path):
    store, _ = inactive_model(tmp_path / "ledger")
    current = store.load()
    withdrawal_id = next(
        record_id for record_id in current.revision.record_ids
        if record_id.startswith("stw_"))
    earlier_membership = tuple(
        record_id for record_id in current.revision.record_ids
        if record_id != withdrawal_id)
    earlier = classify(
        tmp_path / "earlier-evidence",
        model=_SelectedModel(store.replay(earlier_membership)))
    later = classify(tmp_path / "later-evidence", model=store)
    assert earlier.state.conclusion == "declared"
    assert earlier.computed_match == "matches"
    assert later.state.conclusion == "inactive"
    assert later.computed_match is None
