"""Canonical identity namespace shared with the future model kernel.

Pure anchor value contracts only — no storage, no I/O, no authority, and
no dependency on any other backend module. See
docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md and
ADR-0006.
"""

from backend.system_identity.anchors import (
    ENTITY_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
    EntityAnchor,
    VariableAnchor,
)

__all__ = [
    "ENTITY_ANCHOR_ID_PATTERN",
    "VARIABLE_ANCHOR_ID_PATTERN",
    "EntityAnchor",
    "VariableAnchor",
]
