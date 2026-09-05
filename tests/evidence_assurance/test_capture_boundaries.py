"""EA-001 A30-A37 captured-boundary mutation acceptance tests."""

from __future__ import annotations

from backend.evidence_assurance import EvidenceAssuranceQueries

from tests.evidence_assurance.test_selection import (
    _SourceProbe,
    _TemporalProbe,
    _captured_world,
    _request,
)


def _mutate_attempt_same_length(raw):
    attempt = next(row for row in raw.iter_attempts("printer-1")
                   if row.item_key == "printer_objects")
    path = raw.base_dir / "attempts" / f"{attempt.attempt_id}.json"
    before = path.read_bytes()
    assert b"20:00:05 GMT" in before
    after = before.replace(b"20:00:05 GMT", b"20:00:04 GMT")
    assert len(after) == len(before)
    path.chmod(0o644)
    path.write_bytes(after)


class _HookedSource:
    def __init__(self, wrapped, *, before_read=None, after_read=None):
        self.wrapped = wrapped
        self.before_read = before_read
        self.after_read = after_read

    def inventory_token(self, *args, **kwargs):
        return self.wrapped.inventory_token(*args, **kwargs)

    def read_material(self, *args, **kwargs):
        if self.before_read:
            self.before_read()
            self.before_read = None
        material = self.wrapped.read_material(*args, **kwargs)
        if self.after_read:
            self.after_read()
            self.after_read = None
        return material

    def reread_named_material(self, expected_material):
        return self.wrapped.reread_named_material(expected_material)


class _HookedTemporal:
    def __init__(self, wrapped, *, after_initial=None, after_material=None,
                 after_final=None):
        self.wrapped = wrapped
        self.after_initial = after_initial
        self.after_material = after_material
        self.after_final = after_final
        self.inventory_calls = 0

    def selection_inventory_token(self, *args, **kwargs):
        self.inventory_calls += 1
        token = self.wrapped.selection_inventory_token(*args, **kwargs)
        if self.inventory_calls == 1 and self.after_initial:
            self.after_initial()
            self.after_initial = None
        elif self.inventory_calls == 2 and self.after_final:
            callback = self.after_final
            self.after_final = None
            callback()
        return token

    def selection_material(self, *args, **kwargs):
        material = self.wrapped.selection_material(*args, **kwargs)
        if self.after_material:
            self.after_material()
            self.after_material = None
        return material


def _codes(result):
    return tuple(issue.code for issue in result.issues)


def test_a30_change_completed_before_initial_fences_is_the_captured_view(tmp_path):
    raw, _, source, temporal = _captured_world(tmp_path)
    _mutate_attempt_same_length(raw)
    result = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request())
    assert result.status == "complete_within_declared_horizon"
    assert result.issues == ()
    # A same-length source disclosure mutation that completed before both
    # initial fences is part of the captured view. EA makes no earlier-state
    # claim and the temporal projection does not duplicate that source header.


def test_a31_source_change_after_initial_before_material_is_detected(tmp_path):
    raw, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=source,
        temporal=_HookedTemporal(
            temporal, after_initial=lambda: _mutate_attempt_same_length(raw)),
    ).select_operational_evidence(_request())
    assert "source_store_changed_during_capture" in _codes(result)


def test_a32_source_change_during_named_material_read_is_detected(tmp_path):
    raw, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_HookedSource(
            source, before_read=lambda: _mutate_attempt_same_length(raw)),
        temporal=temporal,
    ).select_operational_evidence(_request())
    assert "source_store_changed_during_capture" in _codes(result)


def test_a33_source_change_after_material_before_final_fence_is_detected(tmp_path):
    raw, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_HookedSource(
            source, after_read=lambda: _mutate_attempt_same_length(raw)),
        temporal=temporal,
    ).select_operational_evidence(_request())
    assert _codes(result) == ("source_store_changed_during_capture",)


def test_a34_a35_temporal_change_during_or_after_transaction_is_detected(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)

    class TemporalPhaseChange:
        def __init__(self, wrapped, phase):
            self.wrapped = wrapped
            self.phase = phase
            self.changed = False
            self.inventory_calls = 0
        def selection_inventory_token(self, *args, **kwargs):
            self.inventory_calls += 1
            token = self.wrapped.selection_inventory_token(*args, **kwargs)
            if self.inventory_calls == 1 and self.phase == "after_initial":
                self.changed = True
            if self.inventory_calls == 2 and self.changed:
                return token.model_copy(update={
                    "clock_opening_membership_sha256": "sha256:" + "d" * 64})
            return token
        def selection_material(self, *args, **kwargs):
            material = self.wrapped.selection_material(*args, **kwargs)
            if self.phase == "after_material":
                self.changed = True
            return material

    for phase in ("after_initial", "after_material"):
        result = EvidenceAssuranceQueries(
            source=source, temporal=TemporalPhaseChange(temporal, phase),
        ).select_operational_evidence(_request())
        assert _codes(result) == ("temporal_store_changed_during_capture",)


def test_a36_crossed_source_and_temporal_changes_retain_both(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, [], mutate_final=True),
        temporal=_TemporalProbe(temporal, [], mutate_final=True),
    ).select_operational_evidence(_request())
    assert _codes(result) == (
        "source_store_changed_during_capture",
        "temporal_store_changed_during_capture",
    )


def test_a37_change_immediately_after_both_final_fences_is_not_claimed_detected(
    tmp_path,
):
    raw, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=source,
        temporal=_HookedTemporal(
            temporal, after_final=lambda: _mutate_attempt_same_length(raw)),
    ).select_operational_evidence(_request())
    assert result.status == "complete_within_declared_horizon"
    assert result.issues == ()
    assert result.snapshot.capture_fence.relation == "equal_at_observed_fences"
