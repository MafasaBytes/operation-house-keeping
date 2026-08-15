"""ES-001 promotion of the accepted membership helper, behavior unchanged."""

from datetime import UTC, datetime

import pytest

from backend.identity_binding import membership
from backend.identity_binding.contracts import (
    AppliesScope, DeclaredBoundary, UnboundedBoundary, UnknownBoundary)

START = datetime(2026, 8, 13, 12, tzinfo=UTC)
END = datetime(2026, 8, 13, 13, tzinfo=UTC)
IN = datetime(2026, 8, 13, 12, 30, tzinfo=UTC)


def boundary(kind, end=False):
    if kind == "declared":
        return DeclaredBoundary(kind="declared", at=END if end else START)
    if kind == "unbounded":
        return UnboundedBoundary(kind="unbounded")
    return UnknownBoundary(kind="unknown")


@pytest.mark.parametrize("start,end,expected", [
    ("declared", "declared", "in"),
    ("declared", "unbounded", "in"),
    ("declared", "unknown", "unknown"),
    ("unbounded", "declared", "in"),
    ("unbounded", "unbounded", "in"),
    ("unbounded", "unknown", "unknown"),
    ("unknown", "declared", "unknown"),
    ("unknown", "unbounded", "unknown"),
    ("unknown", "unknown", "unknown"),
])
def test_all_nine_boundary_kind_pairs_are_public_pure_and_pinned(
        start, end, expected):
    scope = AppliesScope(
        axis="ingestion_received_at", start_boundary=boundary(start),
        end_boundary=boundary(end, end=True), interval_semantics="half_open")
    before = scope.model_dump_json()
    assert membership(scope, IN) == expected
    assert scope.model_dump_json() == before
