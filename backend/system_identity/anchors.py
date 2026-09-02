"""IB-001 canonical anchors: opaque identity values.

An anchor claims exactly one thing — this ID names one particular
referent — and nothing else. No hierarchy, connectivity, units, state, or
meaning. IDs are opaque (uuid4 hex) by accepted decision: identity must
survive renames and role reassignment, and a replacement physical
component always receives a new anchor even when its display name and
source address are unchanged. `namespace`, `display_name`, and
`role_name` are human context and are never used for matching.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ENTITY_ANCHOR_ID_PATTERN = r"^ent_[0-9a-f]{32}$"
VARIABLE_ANCHOR_ID_PATTERN = r"^var_[0-9a-f]{32}$"
CONSTRAINT_ANCHOR_ID_PATTERN = r"^con_[0-9a-f]{32}$"
PORT_ANCHOR_ID_PATTERN = r"^prt_[0-9a-f]{32}$"
BEHAVIOR_ANCHOR_ID_PATTERN = r"^bhv_[0-9a-f]{32}$"
STATE_ANCHOR_ID_PATTERN = r"^sta_[0-9a-f]{32}$"
TRANSITION_ANCHOR_ID_PATTERN = r"^trn_[0-9a-f]{32}$"
_NAME_PATTERN = r"^[a-z0-9-]+$"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class EntityAnchor(_Frozen):
    """One canonical entity identity. `referent_kind` classifies only what
    kind of referent the ID names — an installed unit is never the same
    anchor as its CAD/type definition; the relation between them belongs
    to the future kernel."""

    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)
    referent_kind: Literal[
        "physical_instance", "logical_instance", "type_definition", "unknown"
    ]


class VariableAnchor(_Frozen):
    """One canonical variable of one entity. Ownership is identity, not
    hierarchy; the anchor never carries units, datatypes, or meaning the
    source did not supply."""

    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)


class ConstraintAnchor(BaseModel):
    """One canonical constraint identity. A constraint claims exactly one
    thing — this ID names one particular constraint — and nothing else: no
    target variable, no unit, no predicate, no severity. The target-variable
    association is a permanent membership claim carried by a
    ``ConstraintRegistration`` record, never by the anchor, so it cannot
    become an unsupported model fact when the declaration is superseded. IDs
    are opaque (uuid4 hex); ``namespace``, ``display_name``, and
    ``role_name`` are human context and are never used for matching.

    Unlike the older ``EntityAnchor``/``VariableAnchor`` (whose behaviour is
    unchanged), the constraint anchor re-validates any instance handed back
    through ``model_validate``, so a ``model_construct`` forgery (a bad id,
    namespace, or empty display name) is caught here rather than silently
    accepted — the accepted construction-forgery discipline (acceptance row
    A6). This applies only to this anchor; it carries no storage, I/O, or
    authority."""

    model_config = ConfigDict(frozen=True, extra="forbid", revalidate_instances="always")

    anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)


class PortAnchor(BaseModel):
    """One stable port identity and no interface or topology claim."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)


class BehaviorAnchor(BaseModel):
    """One stable behavior identity and no behavioral claim.

    Participants, rule family, context, lifecycle, evidence, direction, and
    every operational meaning belong to model-ledger records, never to this
    opaque identity. Human-facing names may change without changing the
    referent named by ``anchor_id``.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    anchor_id: str = Field(pattern=BEHAVIOR_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)


class StateAnchor(BaseModel):
    """One stable state identity and no state-region or runtime claim.

    Subject entity, permanent constraints, context, evidence, lifecycle, and
    every classification or transition meaning belong to separately admitted
    model records. Names are human context and never identity material.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)


class TransitionAnchor(BaseModel):
    """One stable transition identity and no transition meaning.

    Subject entity, ordered endpoint states, exact endpoint declarations,
    context, evidence, and lifecycle belong to separately admitted model-ledger
    records. Assessment and occurrence are deferred and absent. Names are
    human context and never identity material.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")

    anchor_id: str = Field(pattern=TRANSITION_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)
