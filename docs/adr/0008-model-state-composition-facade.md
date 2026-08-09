# ADR-0008 — Variable membership in the kernel; bound model-state as a composition facade

Status: accepted (owner, 2026-08-09). Spec:
`docs/superpowers/specs/2026-08-09-vm001-model-state-design.md`.

## Context

The product question turned model-variable-first: given a model revision
and a canonical variable, what source observations are bound to it as of a
cutoff, and what can honestly be said about them. The accepted stack was
source-locator-first (`BoundTemporalQueries.latest_observed(subject, prop,
as_of)`), and the model kernel had no variable membership (MK-001
explicitly excluded "variables-in-kernel").

## Decisions

1. **Variable membership is a fifth kernel record kind**,
   `VariableRegistration` (prefix `vrg`), embedding the accepted
   `system_identity.VariableAnchor` verbatim — no kernel copy, no units or
   meaning, no lifecycle, no evidence field. This supersedes exactly the
   membership slice of MK-001's variables exclusion; everything else in
   that exclusion stands. Ownership stays identity
   (`anchor.entity_anchor_id`): **no `variable_of` relationship**, and
   relationship endpoints remain entity anchors only. The owner entity
   must be registered in the same revision (`MODEL_REFERENCE_INVALID`;
   reference closure extends to replay subsets). Variables never enter
   hierarchy views.
2. **The bound model-state query is a new read-only sibling package
   `backend/model_state/`**, never inside `model_kernel`. It composes
   injected accepted query objects — `ModelStateQueries(model: LoadedModel,
   resolver: BindingResolver, temporal: TemporalQueries)`, constructing
   one `BoundTemporalQueries` from the exact injected objects — public
   APIs only, no store construction, no private-field access, one resolver
   governing both discovery and every candidate resolution.
3. **Model-first discovery is a read-only reverse lookup inside
   `identity_binding`** (`BindingResolver.declared_property_locators`):
   one authoritative home for binding declaration and lifecycle
   semantics. Rejected alternatives: (a) caller-supplied locators only —
   cannot answer the product question (kept as a labeled explicit-selector
   *mode*, never called complete discovery); (b) enumerating
   `LoadedBindingSet` mappings inside `model_state` — implementable today
   (all needed mappings are public), rejected because the declarative
   summary shape would fork from `AssertionSummary` and silently go stale
   as the IB ledger grows; (c) storing source locators in the model
   registration — rejected: binding knowledge has lifecycle the immutable
   kernel structurally lacks; it would be a second, worse binding ledger.
4. **Latest-per-locator only** (owner decision): candidates report each
   locator's most recent observation at or before the cutoff,
   forward-resolved at its own `received_at`. No historical fallback
   search in this slice; the limitation is stated verbatim in contracts,
   README, and demo ("no latest candidate observation attachable to the
   requested variable" — never "no observation ever").
5. **Evidence is never hidden**: an unregistered model variable still gets
   full discovery, querying, and resolution; per-candidate `attachment`
   (deterministic precedence: no-observation → resolution-nonpositive →
   resolution-mismatch → variable-unregistered → anchor-divergent →
   attached) separates observation existence from model attachment.
   `observation_availability=observed` asserts evidence existence only.
6. **Reverse-discovery context travels with the answer** (final amendment
   1): each candidate carries its exact `DeclaredLocatorEntry` verbatim,
   with `declared_via_assertion_ids` a derived convenience validated
   against it.
7. **Time-free lifecycle vocabulary** (final amendment 2):
   `DeclaredBindingSummary.lifecycle_flags` is a sorted tuple drawn from
   {closed, retracted, superseded}, derived one-to-one from the lifecycle
   record-id tuples; empty means "no lifecycle event recorded in this
   revision", never "currently applicable". No `active`/`current`/`valid`
   without a time argument; selector labels say `ever_declared_*`.
8. **Temporal storage failures are typed at their source** (prerequisite
   repair): the seven public `TemporalQueries` read methods wrap
   `sqlite3.Error` into the existing `TemporalStoreError`
   (`TEMPORAL_STORE_UNAVAILABLE`, path-free, cause chained).
   `model_state` never imports `sqlite3`.

## Consequences

- The kernel's import boundary is unchanged (`system_identity` + stdlib +
  pydantic); `model_state` adds a one-way dependency on the three lower
  layers' public contracts and forbids `data_sources` imports.
- The demo model grows by exactly one appended record; the old nine-record
  revision remains pinned and replayable, proving append-only history.
- Unavailable temporal storage is now distinguishable from "no observation
  before the cutoff" everywhere.
- A per-variable observation *history* query, persisted cross-set
  divergence diagnostics, and any ranking/aggregation remain explicitly
  out of scope for this slice.
