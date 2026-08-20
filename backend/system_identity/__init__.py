"""Canonical identity namespace shared with the future model kernel.

Pure anchor value contracts only — no storage, no I/O, no authority, and
no dependency on any other backend module. See
docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md and
ADR-0006.
"""

from backend.system_identity.anchors import (
    CONSTRAINT_ANCHOR_ID_PATTERN,
    ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
    ConstraintAnchor,
    EntityAnchor,
    PortAnchor,
    VariableAnchor,
)
from backend.system_identity.minting import mint_constraint_anchor, mint_port_anchor

__all__ = [
    "CONSTRAINT_ANCHOR_ID_PATTERN",
    "ENTITY_ANCHOR_ID_PATTERN",
    "PORT_ANCHOR_ID_PATTERN",
    "VARIABLE_ANCHOR_ID_PATTERN",
    "ConstraintAnchor",
    "EntityAnchor",
    "PortAnchor",
    "VariableAnchor",
    "mint_constraint_anchor",
    "mint_port_anchor",
]
