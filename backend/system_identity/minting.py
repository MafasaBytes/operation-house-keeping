"""Public identity minting helpers for system_identity anchors.

Pure functions over the standard library only — no storage, no I/O, no
authority, and no dependency on any other backend module. A minter generates
a fresh opaque id and returns a frozen anchor value; it asserts nothing
about the referent beyond the id's uniqueness. ``EntityAnchor`` remains without
a public minter. CN-001 introduces the first public minter for
``ConstraintAnchor``; BH-001's Slice D rehearsal gate adds the narrowly scoped
public ``VariableAnchor`` minter without changing the anchor contract.
"""

from uuid import uuid4

from backend.system_identity.anchors import (
    BEHAVIOR_ANCHOR_ID_PATTERN,
    CONSTRAINT_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    _NAME_PATTERN,
    BehaviorAnchor,
    ConstraintAnchor,
    PortAnchor,
    StateAnchor,
    VariableAnchor,
)

_NAME_FIELD = dict(pattern=_NAME_PATTERN)


def mint_behavior_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> BehaviorAnchor:
    """Mint one fresh opaque UUID4-backed ``BehaviorAnchor``."""
    return BehaviorAnchor(
        anchor_id=f"bhv_{uuid4().hex}",
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )


def mint_constraint_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> ConstraintAnchor:
    """Mint one fresh ``ConstraintAnchor`` with a random RFC-4122 UUID4 id.

    Field validation is delegated to the frozen model (``namespace`` /
    ``role_name`` grammar, ``display_name`` nonempty); a malformed argument
    raises pydantic ``ValidationError`` before any id is emitted. The id is
    opaque and carries no meaning; the caller is responsible for persisting
    the anchor (first via a ``ConstraintRegistration`` record)."""
    return ConstraintAnchor(
        anchor_id=f"con_{uuid4().hex}",
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )


def mint_port_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> PortAnchor:
    """Mint one fresh opaque UUID4-backed ``PortAnchor``."""
    return PortAnchor(
        anchor_id=f"prt_{uuid4().hex}",
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )


def mint_state_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> StateAnchor:
    """Mint one fresh opaque UUID4-backed ``StateAnchor``."""
    return StateAnchor(
        anchor_id=f"sta_{uuid4().hex}",
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )


def mint_variable_anchor(
    *,
    entity_anchor_id: str,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> VariableAnchor:
    """Mint one fresh opaque UUID4-backed ``VariableAnchor``."""
    return VariableAnchor(
        anchor_id=f"var_{uuid4().hex}",
        entity_anchor_id=entity_anchor_id,
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )
