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
