# system_identity

The canonical identity namespace shared between `identity_binding` and
the model kernel: pure anchor value contracts (`EntityAnchor`,
`VariableAnchor`, `ConstraintAnchor`) plus the pure public constraint-anchor
UUID4 minter — no storage, no I/O, no authority,
and no dependency on any other backend module (enforced by test).

Anchor IDs are opaque (`ent_`/`var_`/`con_` + uuid4 hex) by accepted decision
(ADR-0006): identity survives renames and role reassignment, and a
replacement physical component always receives a new anchor even when
its display name and source address are unchanged. `namespace`,
`display_name`, and `role_name` are human context and are never used for
matching. `referent_kind` (physical_instance | logical_instance |
type_definition | unknown) classifies only what kind of referent an ID
names — a CAD definition and its installed instance are always distinct
anchors, and the relation between them belongs to the future kernel.
`ConstraintAnchor` names one stable constraint identity and contains no target,
predicate, unit, severity, or lifecycle. `mint_constraint_anchor()` creates the
opaque value; its first persistence is an evidence-bearing model-kernel
`ConstraintRegistration`. CN-001 adds no identity-binding declaration.
