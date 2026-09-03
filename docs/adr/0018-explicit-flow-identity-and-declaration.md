# ADR-0018 — Explicit flow identity and declaration

Date: 2026-09-03

Status: FL-001 complete and owner accepted; declaration-only scope

Authoritative design:
`docs/superpowers/specs/2026-09-02-fl001-explicit-flow-identity-and-evidence-gated-flow-declaration-design.md`.

Final owner acceptance:
`docs/superpowers/reports/2026-09-03-fl001-final-owner-acceptance.md`.

## Context

PT-001 represents ports, common connection membership, and declared interface
roles without a stable connection identity. Those facts do not establish
adjacency or flow. FL-001 needed the smallest explicit vocabulary for a
replayable logical directed flow declaration without turning topology,
compatibility, observations, state, transition, or behavior into transfer or
physical occurrence.

## Decisions

1. **FL-001 adopts a durable logical directed `FlowAnchor` and no
   `ConnectionAnchor`.** The opaque `flo_` anchor names one logical,
   kind-qualified directed port-group relation. It does not name a physical
   connection, path, channel, carrier instance, mechanism, or occurrence.
   `mint_flow_anchor()` allocates identity only and performs no storage,
   authority claim, or inference.

2. **A permanent registration fixes the complete logical signature.**
   `FlowRegistration` (`frg_`) fixes canonical nonempty source and sink port
   sets plus one complete nominal `FlowKindToken`. The role sets are sorted,
   duplicate-free, disjoint, and together contain 2–64 ports. Moving a port,
   reversing roles, changing participation, or changing any token field
   requires a new anchor. One declaration may span several entities; hierarchy
   and ownership do not create the flow.

3. **One exact signature has at most one v1 identity.** Reversed direction or
   a different partition/token is distinct. FL-001 cannot distinguish
   physically parallel mechanisms with the same logical signature and does
   not assert that only one such mechanism exists. Minting indistinguishable
   anchors to suggest physical plurality is forbidden. A future requirement
   needs an evidence-backed, additive connection/path/mechanism identity under
   a separate owner gate and cannot reinterpret existing `flo_`, FRG, or
   historical `mrv_` meaning.

4. **Flow is a directed hyperedge, never inferred pairwise adjacency.** One
   FRG may represent one-to-one, fan-out, fan-in, or many-to-many logical
   participation. It creates no pairwise route, broadcast, split, merge,
   mixing, capacity, conservation, traversal, or reachability claim. Same-port
   role overlap and empty or over-limit role sets reject.

5. **Correctable declarations carry exact contextual support.**
   `FlowDeclaration` (`fld_`) has one exact `AssertionContext`, pins one
   exact-union PCN for all participants, and pins one exact same-context PIF
   direction declaration per port. Source pins accept `output` or
   `bidirectional`; sink pins accept `input` or `bidirectional`. These are
   support claims only. PCN means common membership, PIF means interface role,
   and neither means that anything flowed.

6. **Registration, declaration, support, alignment, and occurrence are
   separate.** An FRG can be admitted from exact PRGs, evidence closure, and
   owner declaration even when current PCN/PIF support is absent. An FLD may
   pin structurally valid support that is already superseded, withdrawn,
   conflicted, or inactive. Queries disclose exact pin activity and alignment
   without retargeting to a successor. `view_independent` and every lifecycle
   view are exact, isolated contexts with no wildcard, fallback, or mapping.

7. **Lifecycle follows the accepted correction-DAG model.** Parentless FLDs
   are independent evidence roots. Same-root correction and convergence,
   fork conflict, cross-root corroboration or effective-body disagreement,
   selective withdrawal, inactivity, and historical revival are derived from
   exact selected membership. `FlowDeclarationWithdrawal` (`flw_`) withdraws
   one current positive tip, has no evidence, and remains uncitable.

8. **Evidence closure is explicit and does not create flow.** FRG and FLD are
   evidence-bearing and citable. Required PRG, FRG, exact PCN/PIF, parent, and
   owner-declaration references supplement uniform model-record evidence
   closure. PCM compatibility, VPA, BH, ST, transition declarations,
   observations, temporal order, correlation, geometry, hierarchy, names, and
   token equality never create flow identity, declaration, assessment, or
   occurrence.

9. **The public surface is exactly four read-only queries.** `ModelQueries`
   exposes `flow()`, `flow_declaration()`, `flows_involving_port()`, and
   `flow_assertion()`. Port collection discovers only through the immutable
   participant index and includes only declarations in the requested exact
   context; it never traverses PCN or infers adjacency. Results carry one
   complete `ModelQueryMaterial` and are authoritatively reconstructed without
   store, filesystem, network, clock, cache, or write access.

10. **Flow records use the existing ledger and revision.** FRG/FLD/FLW join
    the existing `ModelStore`, canonical content-derived identity,
    deterministic immutable indexes, validated append, and historical `mrv_`
    replay. No flow ledger, database, projection, cache, persisted result, or
    second revision exists.

## Implemented and accepted capability

FL-001 Slices A, B, and D are owner accepted; Slice C is absent from v1. The
authoritative synthetic demo contains exactly one FRG followed by one
parentless FLD and zero FLW in the 36-record revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
It demonstrates stable logical identity, exact role partition, qualified kind,
exact contextual support, lifecycle, and read-only disclosure only.

## Deliberately deferred capability

FL-001 provides no observed, commanded, calculated, or inferred flow; no
measurement association, rate, quantity, amount, duration, persistence,
continuity, occurrence, or history; no conservation or balance; no traversal,
routing, reachability, arbitration, simulation, or optimization; and no
behavior, influence, causality, control, safety, health, diagnosis,
correctness, planning, or recommendation.

Any later flow assessment requires an explicit flow-to-measurement association,
quantity/unit/sign semantics, temporal selection and continuity rules,
immutable evidence selection, coverage/refusal vocabulary, and an upper-layer
composition contract. Occurrence and conservation require additional
accountable identity, boundary, provenance, lifecycle, and evaluation
contracts. None is approved by this ADR.

## Consequences

- A model can disclose an evidence-bearing logical flow capability/pathway
  without claiming physical transfer or activity.
- Correcting or withdrawing PCN/PIF support changes disclosure, never the
  durable flow identity or historical FLD pins.
- The accepted synthetic fixture retains the complete declaration-only
  disclaimer; `registered`, `declared`, `healthy`, `current`, `consistent`,
  and `aligned` are model/support terms, not physical truth.
- Future mechanism, measurement, assessment, occurrence, conservation, or
  causal planes must be additive and separately owner gated.

END OF ADR-0018
