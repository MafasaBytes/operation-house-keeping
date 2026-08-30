# ADR-0016 — Explicit state identity and evidence-gated classification

Status: ST-001 corrected final design owner accepted; Slice A authorized and in progress; Slices B-D not authorized

Date: 2026-08-30

Authoritative design:
`docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-and-evidence-gated-classification-design.md`
at SHA-256
`febe18fa291896021708d09c10d5cf4ef955201bcd3e59199e74c6c4e630cc95`.

## Context

The accepted model can register entities, variables, constraints, ports,
variable-port associations, and bounded behavior declarations. It can evaluate
numeric constraints and behavior through read-only evidence compositions. It
has no first-class state identity or state declaration.

ST-001 must add explicit entity-level state knowledge without treating an
observation as a state, a changed value as a transition, or classification as
persisted model or temporal truth. ST-002, not ST-001, owns any future
transition identity, direction, trigger, occurrence, action, causal meaning,
or state-machine execution.

## Decisions

1. Add opaque `StateAnchor` identity with prefix `sta_` and public UUID4 minter
   `mint_state_anchor()` in `backend.system_identity`.
2. Add permanent evidence-bearing `StateRegistration` (`srg_`) to the existing
   model ledger. It embeds the complete anchor and fixes one subject entity, a
   canonical set of 1–64 constraint anchors, and
   `condition_family="all_of_constraints"`.
3. Every registered condition must target a variable whose embedded owner is
   exactly the subject entity. No hierarchy, relationship, name, port, VPA,
   behavior, or evidence inference substitutes for exact identity equality.
4. Add correctable contextual `StateDeclaration` (`std_`) keyed by
   `(state_anchor_id, exact AssertionContext)`. It pins one exact `vcn_` for
   every permanent constraint and fixes
   `evaluation_basis="independent_latest_at_or_before_cutoff"`.
5. A later VCN correction never silently changes state meaning. Classification
   may use a condition only when the uniquely current VCN is the exact pin.
   Accepted CN conflict remains conflict even for engineering-identical tips.
6. Add minimal uncitable `StateDeclarationWithdrawal` (`stw_`) targeting one
   current STD tip. It has no evidence, context, parents, outcome, reason, or
   physical-state meaning.
7. Use BH-style STD lifecycle: same-root forks conflict; partial convergence
   remains conflicted; full same-root convergence is healthy; cross-root
   convergence rejects; independent healthy identical effective bodies
   corroborate; independent differing bodies conflict; inactive roots remain
   disclosed.
8. State DAG validation uses iterative explicit-stack three-colour traversal.
   Recursive traversal is forbidden.
9. Use only the existing model ledger, `ModelStore`, `LoadedModel`, and `mrv_`
   revision. Add no state ledger, store, database, projection, cache, or
   revision.
10. Slice B will later add exactly four read-only kernel methods, but they are
    not authorized in Slice A.
11. Slice C will later add read-only `backend.state_classification`, composing
    public `ConstraintEvaluationQueries`; it is not authorized in Slice A.
12. Slice D will later be separately rehearsed and owner-gated before a
    two-record 32-to-34 demonstration append; no fixture mutation is authorized
    in Slice A.
13. Multiple states may match. ST-001 defines no family, state space,
    exclusivity, completeness, winner, priority, current physical state,
    safety, health, fault, control, diagnosis, or recommendation.

## Slice A authorization

Slice A implements only:

- `StateAnchor` and its minter;
- SRG, STD, and STW contracts;
- canonical identity, serialization, builders, unions, and exports;
- evidence arms for SRG and STD only;
- store reference/evidence/ownership/pin/DAG/withdrawal validation;
- immutable loaded-model indexes;
- explicit historical replay and preservation tests;
- documentation and verification.

Slice A does not implement queries, classification, CN composition, temporal
selection, condition sources, fixture records, candidate demonstration
identities, state families, or transitions.

## Consequences

Positive consequences:

- state identity and state-region declarations become explicit model knowledge;
- permanent entity and constraint scope cannot drift under one state identity;
- exact VCN pins prevent silent meaning changes after CN correction;
- correction, corroboration, conflict, and withdrawal are membership-relative
  and winner-free;
- all existing model records and historical revisions remain unchanged.

Costs and limitations:

- the kernel gains three record kinds and additive indexes;
- changes to subject, permanent conditions, or family require a new state
  anchor;
- accepted CN conditions remain the only v1 predicate vocabulary;
- cross-entity conditions, any-of logic, state families, and transitions are
  unsupported;
- no classification capability exists until separately authorized Slice C.

## Rejected alternatives

- generic relationship or variable attribute as state identity;
- treating CN evaluation output itself as a named state;
- inline or privately evaluated predicates;
- automatic adoption of corrected VCNs;
- a state family/state space in v1;
- a separate state ledger/store/revision;
- persisted computed classification;
- transition or state-machine fields in ST-001.

## Verification obligations

Slice A must prove exact public contracts, canonical ordering, hostile nested
revalidation, exact same-entity admission, reference/evidence closure,
iterative DAG validation, lifecycle/corroboration/withdrawal integrity, atomic
failed append, deterministic indexes, explicit historical replay, unchanged
pre-ST bytes/revisions/artifacts, a 32-record authoritative demo ledger, full
suite success, and base-only/all-extras clean-checkout success.

END OF ADR-0016
