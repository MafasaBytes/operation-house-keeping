"""EA-001 store-independent reconstruction and fingerprint acceptance tests."""

from __future__ import annotations

import copy
import json
import socket

import pytest

from backend.evidence_assurance import (
    OperationalCoverageSummary,
    validate_operational_evidence_snapshot,
)
from backend.evidence_assurance.queries import (
    _canonical_snapshot_bytes,
    _fingerprint,
)

from tests.evidence_assurance.test_selection import (
    _captured_world,
    _request,
)


def _snapshot(tmp_path):
    from backend.evidence_assurance import EvidenceAssuranceQueries

    _, _, source, temporal = _captured_world(tmp_path)
    return EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request()).snapshot


def _plain_without_fingerprint(snapshot):
    return snapshot.model_dump(
        mode="python", exclude={"content_fingerprint"}, warnings=False)


def test_valid_snapshot_reconstructs_from_serialized_values_without_io(
    tmp_path, monkeypatch,
):
    snapshot = _snapshot(tmp_path)
    serialized = json.loads(snapshot.model_dump_json())

    def forbidden(*args, **kwargs):
        raise AssertionError("store or network I/O occurred")

    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    result = validate_operational_evidence_snapshot(serialized)
    assert result.status == "structurally_self_consistent"
    assert result.computed_fingerprint == snapshot.content_fingerprint
    assert result.embedded_fingerprint_relation == "matched"
    assert result.expected_fingerprint_relation == "not_supplied"
    assert result.source_bytes == "not_rechecked"
    assert result.temporal_store_membership == "not_rechecked"


def test_expected_fingerprint_is_an_independent_comparison(tmp_path):
    snapshot = _snapshot(tmp_path)
    matched = validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint=snapshot.content_fingerprint)
    mismatched = validate_operational_evidence_snapshot(
        snapshot, expected_fingerprint="sha256:" + "f" * 64)
    assert matched.status == "structurally_self_consistent"
    assert matched.expected_fingerprint_relation == "matched"
    assert mismatched.status == "fingerprint_mismatch"
    assert mismatched.embedded_fingerprint_relation == "matched"
    assert mismatched.expected_fingerprint_relation == "mismatched"


def test_embedded_fingerprint_mismatch_is_distinct_from_invalid_structure(tmp_path):
    snapshot = _snapshot(tmp_path)
    forged = snapshot.model_copy(update={
        "content_fingerprint": "sha256:" + "0" * 64})
    result = validate_operational_evidence_snapshot(forged)
    assert result.status == "fingerprint_mismatch"
    assert result.computed_fingerprint == snapshot.content_fingerprint
    assert result.embedded_fingerprint_relation == "mismatched"


def test_stale_derived_boolean_reordered_and_hidden_content_are_invalid(tmp_path):
    snapshot = _snapshot(tmp_path)

    stale = snapshot.model_copy(update={
        "coverage": snapshot.coverage.model_copy(update={
            "property_observed_route_indices": (),
        })})
    boolean_route = snapshot.model_copy(update={
        "provenance_routes": (
            snapshot.provenance_routes[0].model_copy(update={"attempt_index": True}),
        )})
    reordered = snapshot.model_copy(update={
        "source_material": snapshot.source_material.model_copy(update={
            "artifacts": tuple(reversed(snapshot.source_material.artifacts)),
        })})
    hidden = snapshot.model_dump(mode="python")
    hidden["request"]["scope"]["hidden"] = "extra"

    for candidate in (stale, boolean_route, reordered, hidden):
        result = validate_operational_evidence_snapshot(candidate)
        assert result.status == "invalid"
        assert result.computed_fingerprint is None
        assert result.embedded_fingerprint_relation == "not_computed"


def test_wrong_union_arm_cycle_and_substituted_result_are_invalid(tmp_path):
    snapshot = _snapshot(tmp_path)
    wrong_union = snapshot.model_dump(mode="python")
    marker = wrong_union["temporal_material"]["occurrence_membership"][0][
        "source_time"]
    marker.clear()
    marker.update({"kind": "monotonic", "reason": "wrong arm"})

    cycle = snapshot.model_dump(mode="python")
    cycle["request"]["policy"] = cycle

    from backend.evidence_assurance import EvidenceAssuranceQueries
    _, _, source, temporal = _captured_world(tmp_path / "other")
    substituted = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request())

    for candidate in (wrong_union, cycle, substituted):
        assert validate_operational_evidence_snapshot(candidate).status == "invalid"


def test_snapshot_and_fingerprint_replacement_can_remain_self_consistent(tmp_path):
    snapshot = _snapshot(tmp_path)
    payload = snapshot.model_dump(mode="python")
    payload["source_material"]["attempts"][0]["allowlisted_headers"]["Date"] = (
        "Fri, 07 Aug 2026 20:00:04 GMT")
    without = {key: value for key, value in payload.items()
               if key != "content_fingerprint"}
    payload["content_fingerprint"] = _fingerprint(without)
    result = validate_operational_evidence_snapshot(payload)
    assert result.status == "structurally_self_consistent"
    assert result.computed_fingerprint != snapshot.content_fingerprint

    independently_pinned = validate_operational_evidence_snapshot(
        payload, expected_fingerprint=snapshot.content_fingerprint)
    assert independently_pinned.status == "fingerprint_mismatch"
    assert independently_pinned.expected_fingerprint_relation == "mismatched"


def _leaf_paths(value, prefix=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _leaf_paths(item, (*prefix, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _leaf_paths(item, (*prefix, index))
    else:
        yield prefix


def _mutate_leaf(document, path):
    target = document
    for component in path[:-1]:
        target = target[component]
    key = path[-1]
    value = target[key]
    if value is None:
        target[key] = "changed"
    elif isinstance(value, bool):
        target[key] = not value
    elif isinstance(value, int):
        target[key] = value + 1
    elif isinstance(value, float):
        target[key] = value + 1.0
    else:
        target[key] = value + "#"


def test_every_bound_leaf_changes_canonical_bytes_and_fingerprint(tmp_path):
    snapshot = _snapshot(tmp_path)
    base = json.loads(json.dumps(
        _plain_without_fingerprint(snapshot), default=str))
    expected_bytes = _canonical_snapshot_bytes(base)
    expected_fingerprint = _fingerprint(base)
    paths = tuple(_leaf_paths(base))
    assert paths
    for path in paths:
        changed = copy.deepcopy(base)
        _mutate_leaf(changed, path)
        assert _canonical_snapshot_bytes(changed) != expected_bytes
        assert _fingerprint(changed) != expected_fingerprint


def test_canonical_serialization_ignores_mapping_insertion_order(tmp_path):
    snapshot = _snapshot(tmp_path)
    base = _plain_without_fingerprint(snapshot)

    def reverse_mappings(value):
        if isinstance(value, dict):
            return {key: reverse_mappings(value[key]) for key in reversed(value)}
        if isinstance(value, list):
            return [reverse_mappings(item) for item in value]
        if isinstance(value, tuple):
            return tuple(reverse_mappings(item) for item in value)
        return value

    reversed_value = reverse_mappings(base)
    assert _canonical_snapshot_bytes(base) == _canonical_snapshot_bytes(reversed_value)
    assert _fingerprint(base) == _fingerprint(reversed_value)
