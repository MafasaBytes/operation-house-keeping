# ADR-0017 — Explicit state-transition identity and declaration

Date: 2026-09-02

Status: ST-002 v1 complete and owner accepted; declaration-only scope

Authoritative design:
`docs/superpowers/specs/2026-09-02-st002-explicit-state-transition-identity-and-declaration-design.md`.

Final owner acceptance:
`docs/superpowers/reports/2026-09-02-st002-final-owner-acceptance.md`.

## Context

ST-001 introduced explicit state identity, evidence-bearing declarations, and
read-only classification against selected observations. It deliberately did
not make a changed value, two classifications at different cutoffs, or
temporal order into a transition.

ST-002 needed the smallest replayable model vocabulary for declaring one
directed state-transition possibility while keeping a declaration separate
from evidence assessment and accountable physical occurrence.

## Decisions

1. **ST-002 is a declaration-only extension of `system_identity` and
   `model_kernel`.** `TransitionAnchor` is an opaque `trn_` identity.
   `mint_transition_anchor()` allocates identity only and performs no lookup,
   storage, inference, assessment, or occurrence creation. There is no
   transition-specific ledger or revision; records join the existing
   `ModelStore` and `mrv_` membership.

2. **A permanent registration fixes a directed, same-subject endpoint
   tuple.** `TransitionRegistration` (`trg_`) fixes exactly the subject entity,
   from-state anchor, and to-state anchor. Both state registrations must name
   that exact subject. Self-transitions and cross-entity endpoints reject.
   At most one transition identity may occupy an ordered same-subject
   `(from_state_anchor_id, to_state_anchor_id)` tuple in one membership.
   Reversing the endpoints creates a distinct directed transition.

3. **The permanent identity does not encode a mechanism or occurrence.**
   Independent declaration roots are multiple evidence claims about one
   transition, not multiple mechanisms or occurrence instances. A future
   need for distinct mechanisms sharing endpoints requires an additive,
   separately owner-gated discriminator or contract that cannot reinterpret
   existing `trn_` identities or historical revisions.

4. **Correctable declarations pin exact state-declaration meaning.**
   `TransitionDeclaration` (`trd_`) uses one exact `AssertionContext` and pins
   the exact from-state and to-state `std_` record IDs. The endpoint states and
   declarations must match the permanent anchors, common subject, and exact
   context. A later state correction never silently retargets an earlier TRD.
   A structurally valid TRD may deliberately pin an already superseded or
   withdrawn STD; admission and later pin activity/alignment are separate.

5. **Lifecycle follows the accepted correction-DAG model.** A parentless TRD
   is an independent evidence root. Same-root correction, multi-parent
   convergence, fork conflict, independent-root corroboration or disagreement,
   selective withdrawal, inactivity, and historical revival are derived only
   from the selected membership. A parent tuple crossing independent roots
   rejects. `TransitionDeclarationWithdrawal` (`trw_`) withdraws one current
   positive tip, carries no evidence, and is not citable.

6. **Evidence closure is explicit and uniform.** TRG and TRD are evidence
   bearing and citable model records. Their required entity, state,
   registration, exact declaration, and owner-declaration references are
   additive to the existing uniform model-record evidence-closure rule.
   `trw_` remains uncitable. Evidence supports the model claim; it does not
   authenticate uncaptured external bytes or prove that a transition occurred.

7. **Endpoint lifecycle and alignment are orthogonal.** Public transition
   disclosure reuses the accepted model-kernel state-declaration and
   state-assertion derivation. It does not implement a parallel ST lifecycle
   engine. Transition-declaration conclusion, containing-root health, pinned
   STD activity, endpoint state conclusion, and pin alignment remain separate
   fields. No timestamp, authority, filename, append order, or record ID picks
   a winner.

8. **The public surface is exactly four read-only queries.** `ModelQueries`
   exposes `transition()`, `transition_declaration()`,
   `transitions_of_entity()`, and `transition_assertion()`. Results carry one
   complete `ModelQueryMaterial`; nested rows use indices and derived scalars.
   Authoritative result reconstruction is store-independent, revalidates the
   entire material and result graph, recomputes revision and derivation, and
   rejects forged or impossible combinations.

9. **Context and replay are exact.** `view_independent` is an exact context,
   not a wildcard. Context mapping, fallback, state families, and family-based
   endpoint selection are absent. Canonical IDs, deterministic ordering,
   append validation, immutable indexes, and historical membership replay use
   the accepted model-kernel rules.

## Implemented and accepted capability

ST-002 Slices A through C are owner accepted. They implement identity,
TRG/TRD/TRW contracts, canonical/store/lifecycle integration, the four
read-only queries, authoritative result validation, adversarial hardening, and
deterministic disposable positive worlds. The authoritative demo ledger has
no TRG, TRD, or TRW record; positive coverage remains disposable.

## Deliberately deferred capability

ST-002 provides no transition assessment, occurrence identity or assertion,
detection, transition history, execution, enablement, trigger, guard, action,
effect, dwell, debounce, hysteresis, continuity, state-machine traversal,
next-state selection, causality, control, safety, diagnosis, correctness, or
recommendation.

The accepted ST-001 classification basis selects independent latest admitted
observations at or before a cutoff. It supplies no temporal cohort,
continuity, persistence, interval, ordering, or occurrence contract. A later
transition assessment therefore requires separately owner-accepted temporal
selection and evidence contracts; differing classifications do not suffice.

## Consequences

- A model can name and disclose a directed transition possibility without
  claiming that it is enabled, executable, observed, completed, or occurred.
- State correction changes pin activity/alignment disclosure but never changes
  the historical meaning of an existing TRD.
- Transition records remain ordinary model records under exact historical
  `mrv_` replay.
- Current authoritative transition absence is a structured result, not an
  inferred negative transition claim.

END OF ADR-0017
