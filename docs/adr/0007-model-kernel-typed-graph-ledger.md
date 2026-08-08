# ADR-0007: model_kernel as a typed-graph ledger over system_identity anchors

Date: 2026-08-08
Status: Accepted (project owner; candidate design + specialist reviews + one
correction pass + six final normative amendments)

## Context

`data_sources` (immutable evidence), `temporal_state` (rebuildable
timeline), and `identity_binding` (append-only identity-decision ledger with
`system_identity` anchor values) are accepted. MK-001 must represent
canonical entities, typed directional evidence-backed relationships,
type-vs-instance, a containment-derived hierarchy view, and exact replayable
model revisions — without hierarchy inference, identity matching, evidence
mutation, or a graph database.

## Decisions

1. **Sibling module, `system_identity`-only runtime dependency.**
   `backend/model_kernel/` imports only `system_identity`, stdlib, and
   pydantic (AST-enforced); nothing lower imports upward. Test-only pinning
   seams may import `identity_binding`, `data_sources.contracts`, and
   `temporal_state` contracts. Rejected: kernel reading the binding ledger
   (dependency reversal ADR-0006 built `system_identity` to avoid); bare
   anchor-ID references (loses `referent_kind` needed for endpoint
   validation and makes seam checks vacuous).

2. **Registration embeds the anchor; the kernel consumes identity, never
   allocates it.** `EntityRegistration` embeds the full `EntityAnchor`
   value as an immutable membership claim with **no lifecycle** (no
   supersession, no withdrawal): the kernel can never alter an embedded
   anchor field. Synthetic demo anchor IDs are externally allocated fixture
   constants declared via `AnchorDeclaration` records in a new committed
   binding set `bindings/demo-printer-model/` (a declaration fixture, not an
   anchor-generation service); existing `bindings/demo-printer/` records are
   untouched. Trust boundary disclosed: structural validation at runtime,
   field-for-field seam/CI verification for committed fixtures, documented
   external procedure for runtime sets. Rejected: kernel-side registration
   supersession (invited anchor mutation); kernel-embedded anchors declared
   nowhere (second identity authority).

3. **All relationship types are data; the kernel ships none.** `contains`
   and `instance_of` are committed `rtd_` records; kernel code interprets
   only declared flags. Type identity is a **lineage** named by `type_name`:
   supersession preserves `{type_name, directionality, hierarchy_semantics,
   context_requirement}`; exactly one current definition per name (branched
   chains invalid); assertions are judged by the exact definition they cite
   and stale-marked when it is superseded — never retro-invalidated or
   silently reinterpreted. Transitivity is a property of the containment
   projection only, never a per-type flag. `unknown` referent kind is an
   explicit opt-in endpoint member, never a wildcard. Rejected: hard-coded
   types (ontology slide); per-type transitivity (semantic smuggling);
   the earlier active-assertions-must-cite-current-types cascade (deadlocked
   correction and broke single-append validity).

4. **Contention is surfaced; malformation invalidates.** Distinct-parent/
   same-child conflicts (independent lineages, same type lineage and view)
   and containment cycles are structured query results with full candidate
   and assertion disclosure — never resolved by recency, authority rank, or
   timestamps, and never revision-invalidating. Same-edge multiples are
   corroboration with every supporting assertion preserved; intra-lineage
   competing successors are reported exclusively via `lineage_conflicts`.
   Dangling references, tampering, duplicate registrations/current names,
   endpoint-kind and context violations invalidate the complete revision.
   Traversal is deliberately asymmetric: parent conflicts block upward
   queries but annotate (not block) downward traversal; cycles block both.

5. **Append-only JSON ledger with VALIDATING append and computed
   revisions.** One record per file, content-derived full-SHA-256 ids over
   UTC-normalized canonical serialization (byte-parity with
   `identity_binding.canonical` held by shared golden vectors, not shared
   code), staging outside the scanned directory, atomic promote.
   `append` diverges deliberately from IB-001's record-local append: it
   fully validates the current set, then the prospective set, before
   promoting — owner-approved despite O(set) cost, because kernel records
   form a referential graph and the divergence buys "the on-disk ledger is a
   valid revision after every successful append" (absent tampering).
   Identical re-append is a validated idempotent no-op that still fails if
   any other member is corrupted. `ModelRevision` (`mrv_`) is computed-only,
   never stored, structurally excluded from membership. Evidence tuples are
   canonicalized (sorted by canonical bytes, duplicates normalized away)
   so permuted or repeated evidence cannot produce distinct record ids.
   Rejected: authoritative SQLite graph (binary authority in git; nothing
   gained at this scale); ledger + rebuildable SQLite projection (correct
   future shape, premature now — queries sit behind `ModelQueries` so a
   projection can be slotted later); extracting a shared ledger utility
   (modifies accepted frozen code to save ~200 lines; recorded as a possible
   future owner-approved consolidation slice).

6. **Views without a configuration timeline.** Every assertion carries a
   required discriminated context (five lifecycle views or view-independent)
   matching its type's declared requirement; queries use strict context
   equality with typed mismatch errors and no union form. Validity
   intervals, configuration generations, and time-varying structure are
   explicitly deferred; `rwd_` means "no longer asserted," never "was wrong"
   and never "stopped being true at time T."

## Consequences

- Hierarchy is one projection per (containment lineage × view) over an
  auditable typed graph; every edge explains itself down to checksummed
  evidence references.
- Model corrections are single-record appends with structured staleness
  disclosure — no cascades, no unloadable intermediate states.
- Error results and messages carry ids and names, never absolute paths.
- The full spec is
  `docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`.
