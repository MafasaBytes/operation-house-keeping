# system_identity

The canonical identity namespace shared between `identity_binding` and
the model kernel: pure anchor value contracts (`EntityAnchor`,
`VariableAnchor`, `ConstraintAnchor`, `PortAnchor`, and `BehaviorAnchor`) plus
pure public UUID4 minters for constraint, port, behavior, and variable
identities — no
storage, no I/O, no authority,
and no dependency on any other backend module (enforced by test).

Anchor IDs are opaque (`ent_`/`var_`/`con_`/`prt_`/`bhv_` + uuid4 hex) by accepted decision
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
`PortAnchor` likewise contains no owner or interface claim; its permanent,
evidence-bearing owner association begins at model-kernel `PortRegistration`.
`BehaviorAnchor` contains no participants, owner, context, rule, lifecycle,
evidence, direction, state, or causal meaning. Its permanent unordered
two-variable membership and fixed BH-001 rule family begin only at an explicit,
evidence-bearing model-kernel `BehaviorRegistration`; names and shared
ownership never create behavior. `mint_behavior_anchor()` creates only the
opaque identity.

`mint_variable_anchor()` creates one fresh opaque `var_` UUID4 identity and
returns the unchanged `VariableAnchor` contract containing the explicitly
supplied entity identity and human-facing names. The helper performs no lookup,
registration, binding, authority assertion, storage, or persistence; its output
becomes model knowledge only through an independently admitted
`VariableRegistration`.

The BH-001 Slice D minter repair is committed at
`2bee0f3808335d57d5d835f66892d1c21004d519`. Its one-time candidate output
`var_ab2d312466054c20b0ac764e9bc0114e` and the independently allocated behavior
anchor `bhv_80e21f1682e449ca9c65a5e2ee051ea0` are now owner approved through the
frozen pre-append contract at `0905de0`; they must never be reminted or
replaced. The authorized exact model revision is
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
That approval changes no identity or minter semantics.
The approved anchors are now embedded unchanged in the authoritative Slice D
VRG and BRG; the allocation manifest remains unchanged as historical evidence.
BH-001 complete, owner accepted, adversarially reviewed, full-suite verified,
and dual-clean-checkout verified. Acceptance changes no identity or minter
semantics and does not turn the `not_executed` demonstration into observed
equality or real-machine truth.
