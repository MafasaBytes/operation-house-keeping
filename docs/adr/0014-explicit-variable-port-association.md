# ADR-0014 — Explicit variable-to-port association

Status: VP-001 Slice A is owner accepted at
`60b739182e423a05eac7f3c531145d90c65fe9bc`. Slice B is implemented and
adversarially reviewed; awaiting owner acceptance. Slices C and D remain
separately owner-gated. No state composition or VP fixture record has been
added.

## Context

PT-001 introduced stable entity-owned ports while preserving existing
entity-owned variable identity. The model cannot yet explicitly state that one
registered variable and one registered port are associated. Ownership, names,
interface declarations, topology, compatibility, CAD, telemetry, and observation
availability are insufficient and must not infer that claim.

VP-001 must satisfy the future behavior prerequisite by making this association
explicit and evidence-backed without implementing behavior evaluation or
claiming that a value occurred at, travelled through, or was produced by a port.

## Decisions

1. Add `VariablePortAssociation` (`vpa_`) and
   `VariablePortAssociationWithdrawal` (`vpw_`) to the existing model ledger and
   existing model revision. Add no anchor, new ledger, store, generic
   relationship endpoint, role, negative assertion, or Slice A composition
   module.
2. A VPA means only that, in its exact `AssertionContext`, an accountable
   authority explicitly associates the registered variable and port with cited
   evidence. It carries endpoint IDs, exact context, nonempty canonical evidence,
   correction parents, recorded time, authority, and conventional note.
3. VPW targets one VPA and carries recorded time, authority, and note. It has no
   evidence, context, parents, outcome, or negative meaning. It means only that
   the target is no longer asserted in the selected revision.
4. Admission requires the variable registration, port registration, both owner
   entity registrations, exact owner equality, and complete model-record
   evidence closure. Shared ownership constrains an explicit VPA but never
   creates one. Entity referent kinds receive no inferred equivalence or
   propagation.
5. The exact subject is `(variable_anchor_id, port_anchor_id, exact context)`.
   Parentless records create independent corroborating roots. Corrections remain
   within one root and preserve the subject. Same-root forks and complete
   convergence are permitted; cross-root convergence and cycles are invalid.
6. Root health is inactive, healthy, or conflicted according to active current
   tips. No subject root means not declared; any active tip means asserted;
   roots without an active tip mean inactive. No timestamp, authority, ID, file,
   or append ordering selects a winner.
7. VPW may target any unsuperseded, unwithdrawn current VPA tip, including one
   tip of a fork. Sibling tips do not block withdrawal, and withdrawing one fork
   tip may resolve its root from conflicted to healthy. One membership cannot
   both supersede and withdraw a target. Historical replay that omits a later
   withdrawal revives the target relative to that membership.
8. One variable may associate with multiple same-owner ports; one port may
   associate with multiple same-owner variables; independent roots may
   corroborate. No uniqueness, exclusivity, or cardinality is inferred.
9. `vpa_` is citable model-record evidence and `vpw_` is not. Evidence supports
   an authority's declaration but never automatically materializes model truth.
10. Slice A adds only canonical contracts, validation, store indexes, builders,
    exports, replay, and tests. Slice B adds exactly four read-only kernel query
    methods and six carry-once result contracts with seven nominal status
    vocabularies. Slice C, required for VP-001 completion, adds a separately
    gated read-only model-state composition. Slice D may append one synthetic
    VPA to evolve the demo from 28 to 29 records.

## Consequences

The model can represent explicit, revision-bound variable-to-port knowledge
without changing either identity or ownership. Cross-owner and role-specific
meanings remain unsupported. Missing declarations remain unknown/not declared,
never evidence-backed negatives. Existing relationship, PT, variable, state,
temporal, evidence, and canonical contracts retain their meanings and bytes.

The kernel remains dependent only on `system_identity`, standard library, and
Pydantic. State composition, when separately authorized, remains in the
read-only `model_state` layer.
