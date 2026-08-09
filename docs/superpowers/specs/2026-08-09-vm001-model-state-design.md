# VM-001 — Variable Membership and Bound Model-State Query

Status: owner-approved for implementation (2026-08-09), including two final
contract amendments (declaration context carried per candidate; time-free
lifecycle vocabulary). Base commit: `682fa53` on `main`, implemented on the
isolated `vm001` branch in a linked worktree.

This specification is self-contained: it supersedes design chat and carries
every decision needed to implement, review, and validate the slice.

## Supersession of an accepted exclusion

MK-001's accepted design explicitly excluded "variables-in-kernel". VM-001
**lifts exactly the membership slice of that exclusion and nothing else**:
the kernel gains a record kind that registers an existing canonical
`VariableAnchor` as model membership. Variables still carry no units, no
datatype, no meaning, no state, no lifecycle, and no hierarchy role. All
other MK-001 exclusions stand.

## Capability

Given a model revision and a canonical variable of a modeled entity: what
source observations are bound to that variable as of a required cutoff, and
what can honestly be said about their value, freshness, quality, identity
resolution, and provenance. Unknown, unbound, ambiguous, stale, and absent
are valid outcomes. No single current value is ever manufactured.

## Architecture

Milestone VM-001, two seams plus one prerequisite:

- **Task 0 (prerequisite repair)**: type temporal storage failures at the
  `temporal_state` public query boundary (own commit, red-first).
- **Part A**: fifth model-kernel record kind `VariableRegistration`
  (prefix `vrg`) + kernel queries, inside `backend/model_kernel/`.
- **Part B**: new read-only package `backend/model_state/` joining model
  membership to bound temporal evidence, plus one read-only reverse-lookup
  query added to `backend/identity_binding/`.

### Dependency diagram and import rules

```text
data_sources → temporal_state ─┐
        system_identity ─→ identity_binding ─→ ┌──────────────┐
        system_identity ─→ model_kernel ─────→ │ model_state  │
                           temporal_state ───→ └──────────────┘
                           (contract types)      read-only facade
```

- `model_kernel` allowed roots unchanged: `backend.system_identity`,
  stdlib, pydantic. Its AST isolation test additionally forbids
  `backend.model_state` (no upward import).
- `model_state` allowed roots: `backend.system_identity`,
  `backend.model_kernel`, `backend.identity_binding`,
  `backend.temporal_state`, pydantic, stdlib. Forbidden:
  `backend.data_sources` (import-level rule; `data_sources` contract
  *types* legitimately appear inside verbatim temporal objects — the same
  accepted precedent as identity_binding), `sqlite3`, any store
  construction (`ModelStore`, `BindingStore`, `TemporalStore`), any path
  literal, `importlib`/`__import__`.
- The direct `temporal_state` import is deliberate: `SourceSubjectRef`,
  `SourcePropertyRef`, and the bound result types are not re-exported
  anywhere, and `identity_binding` itself imports them directly.

## Task 0 — temporal storage failures typed at source

The seven public read methods of `TemporalQueries` (`history`,
`change_history`, `latest_observed`, `attempt_coverage`, `freshness`,
`provenance`, `clock_segments`) wrap their store access so that any
`sqlite3.Error` raises the **existing accepted class**:

```text
TemporalStoreError("TEMPORAL_STORE_UNAVAILABLE",
                   "temporal store for this query is unavailable or unreadable")
```

path-free (no database path, no implementation detail), with the original
exception chained as the cause. `TEMPORAL_NAIVE_CUTOFF` behavior is
unchanged; no schema or logical-row change; projector and store write
paths untouched. Unavailable/corrupted storage is thereby distinguishable
from `none_before_cutoff` everywhere downstream. `model_state` propagates
this error unchanged and never imports `sqlite3`.

## Part A — `VariableRegistration`

```python
class VariableRegistration(_Frozen):
    record_kind: Literal["variable_registration"] = "variable_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vrg_[0-9a-f]{64}$")
    anchor: VariableAnchor          # system_identity contract, embedded verbatim
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

No evidence field (registrations claim membership on authority, exactly
like `EntityRegistration`); no lifecycle (no correction path — accepted
asymmetry); no `variable_of` relationship (ownership is identity via
`anchor.entity_anchor_id`; relationship endpoints remain entity anchors
only by pattern). A variable registration is membership — not state, not
semantic enrichment, not an edge.

### Hashing and patterns

- `_PREFIX_BY_KIND += {"variable_registration": "vrg"}`; canonical rules
  inherited; no existing record hash and no revision function changes.
- `MODEL_RECORD_ID_PATTERN` → `^(reg|rtd|rel|rwd|vrg)_[0-9a-f]{64}$`;
  store `_FILENAME` likewise.
- `ModelRecord` union += `VariableRegistration` (revalidation and file
  reads follow via the shared TypeAdapter).
- `ModelRecordEvidence.record_id` pattern → `^(reg|rtd|rel|vrg)_…$`
  (owner decision: variable membership citable symmetrically with entity
  membership; `rwd` stays excluded).
- `LoadedModel` gains `variable_registrations_by_anchor` — a **separate**
  defaulted read-only mapping, never merged into `registrations_by_anchor`
  (endpoint-kind validation reads `.referent_kind`, which `VariableAnchor`
  does not have).
- Kernel/IB canonical-parity suite gains a `vrg` golden vector; existing
  vectors frozen.

### Validation (in `validate_record_collection` — identical at load,
### prospective append, and replay-subset)

1. The record-kind bucket dispatch gains the new kind (its omission would
   leak a raw `KeyError`).
2. **Duplicate and idempotency behavior — three pinned cases**:
   1. Re-appending the byte-identical record: accepted idempotent no-op —
      same id returned, nothing written, revision unchanged.
   2. A second distinct record claiming the same `anchor.anchor_id` with
      agreeing anchor fields: `MODEL_DUPLICATE_REGISTRATION`. Never chosen
      by `recorded_at`, authority, or record id.
   3. Same `anchor.anchor_id` with divergent anchor fields: structurally
      rejected with `MODEL_DUPLICATE_REGISTRATION`, the message naming
      **both conflicting record ids** (ids only — never paths).
3. **Owner-entity rule**: `anchor.entity_anchor_id` must key
   `registrations_by_anchor` in the same collection, else
   `ModelIntegrityError("MODEL_REFERENCE_INVALID", "variable registration
   {vrg_id} references unregistered owner entity {ent_id}")`. Append of an
   orphan vrg fails before any write (owner-first ordering, like
   rtd-before-rel). A replay subset containing a vrg must contain the
   owner's registration (reference closure); pre-variable subsets stay
   valid untouched.
4. No kernel-side 32-hex-tail cross-kind check: declaration-layer
   knowledge. The cross-layer seam test is **widened** (its
   `isinstance(anchor, EntityAnchor)` filter currently skips variable
   anchors) so every kernel-embedded `VariableAnchor` is compared
   field-for-field against its committed binding-set declaration in CI.

### Hierarchy non-impact

The hierarchy projection is built from relationship assertions only.
Variable registrations add zero edges; parents/children/ancestors/
descendants/health are bit-for-bit unaffected, and a probe test proves no
`var_` id ever appears in any hierarchy result.

### Kernel queries

```python
class VariableRegistrationSummary(_Frozen):
    record_id: str = Field(pattern=r"^vrg_[0-9a-f]{64}$")
    anchor: VariableAnchor
    authority: AuthorityRef
    recorded_at: UtcDatetime

class VariableResult(_Frozen):
    status: Literal["registered", "not_registered"]
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    registration: VariableRegistrationSummary | None = None   # iff registered
    revision: ModelRevision

class EntityVariablesResult(_Frozen):
    status: Literal["registered", "not_registered"]           # OF THE ENTITY
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    entries: tuple[VariableRegistrationSummary, ...] = ()     # asc anchor_id
    revision: ModelRevision                                   # not_registered ⇒ ()
```

- `ModelQueries.variable(anchor_id)`: input validated against
  `VARIABLE_ANCHOR_ID_PATTERN` (`MODEL_ANCHOR_ID_INVALID`, message
  parameterized "not a canonical variable anchor id"); an `ent_` id is
  typed misuse, never `not_registered`.
- `ModelQueries.variables_of(entity_anchor_id)`: three distinct outcomes —
  registered-with-variables / registered-zero-variables / unregistered.
- Every result echoes the revision. Public surface `__all__` 43 → 47
  (`VariableRegistration`, `VariableRegistrationSummary`, `VariableResult`,
  `EntityVariablesResult`).

## Reverse lookup — `identity_binding` (owner-approved additive extension)

One authoritative home for binding declaration and lifecycle semantics.

```python
class DeclaredBindingSummary(_Frozen):        # identity_binding/contracts.py
    record_id: str        # iba_…                 the asserted binding
    target_anchor_id: str                       # exact target — even when ≠ requested
    authority: AuthorityRef                     # verbatim from the record
    recorded_at: UtcDatetime
    declared_applies: AppliesScope              # as asserted
    effective_applies: AppliesScope             # after closures, this revision
    supersedes: str | None                      # backward audit link (iba_)
    superseded_by: tuple[str, ...] = ()         # iba_, sorted unique
    retracted_by: tuple[str, ...] = ()          # ibr_, sorted unique
    closure_records: tuple[str, ...] = ()       # ibc_, at most one
    lifecycle_flags: tuple[Literal["closed", "retracted", "superseded"], ...]
    # sorted unique; derived one-to-one from the three id tuples; () means
    # "no supersession, retraction, or closure recorded in this binding
    # revision" — NEVER "currently applicable". Deliberately time-free:
    # applicability at an observation is decided solely by forward
    # resolution at that occurrence's received_at.

class DeclaredLocatorEntry(_Frozen):
    subject: SourceSubjectRef
    property: SourcePropertyRef
    assertion_summaries: tuple[DeclaredBindingSummary, ...]   # ALL property
    # assertions on this locator, ANY target, sorted by record_id — a shared
    # locator explains its own conflicts standalone.

class DeclaredPropertyLocatorsResult(_Frozen):
    status: Literal["declared", "none_declared", "anchor_not_declared"]
    target_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    locators: tuple[DeclaredLocatorEntry, ...]  # sorted by the 6-tuple
    # (source_id, adapter_id, subject_identifier, extraction_route,
    #  item_key, json_pointer)
    revision: BindingRevision
```

`BindingResolver.declared_property_locators(target_anchor_id)` — plus a
small companion required by amendment 1's selector classification:
`BindingResolver.declared_locator(subject, property) ->
DeclaredLocatorEntry | None`, the time-free declarative entry for ONE
locator (all property assertions on it, any target) or None when never
declared; invalid subject/property inputs →
`BindingResolutionError("BINDING_LOCATOR_INVALID", …)`. Without it,
classifying a selector declared only for another variable would force
`model_state` to re-implement locator matching over binding internals —
exactly what the one-authoritative-home decision forbids.

Semantics of the discovery query:

- **No `at` parameter** — revision-relative and time-free. Lists every
  locator ever declared for the variable in this revision, including
  superseded, retracted, and closed assertions (include-with-disclosure;
  a historical declaration never looks like an unexplained current
  candidate because its lifecycle flags, lifecycle record ids, and
  effective scope are all present).
- An entry enters the result when at least one of its assertions targets
  the requested variable; the entry carries all assertions on the locator.
- Zero property assertions for a declared variable → `none_declared`
  (unbound at discovery level — a valid answer, not missing data).
  Anchor id absent from the revision's declarations →
  `anchor_not_declared` (the cross-set gap).
- Never a winner; no recency/authority ordering anywhere.
- Input domain: `var_` ids only. Anything else (including `ent_` ids) →
  `BindingResolutionError("BINDING_ANCHOR_ID_INVALID", …)` (new code, no
  new class). Store, canonical, and facade modules are untouched.

## Part B — `backend/model_state/`

Files: `__init__.py` (docstring: read-only projection facade, **holds no
state of its own**; `__all__`), `contracts.py` (result contracts + error
tree), `facade.py` (`ModelStateQueries`).

### Constructor seam (public composition only)

```python
class ModelStateQueries:
    def __init__(self, model: LoadedModel,
                 resolver: BindingResolver,
                 temporal: TemporalQueries) -> None:
        # each argument type-validated →
        #   ModelStateConfigurationError("MODEL_STATE_INPUT_INVALID")
        self.model = model
        self.resolver = resolver
        self.bound = BoundTemporalQueries(resolver, temporal)
```

One resolver by construction: reverse discovery and every forward
resolution share the same object, so a discovery/resolution
binding-revision mismatch is unconstructible. Public APIs only; no store
construction; no underscore-attribute access on any injected object
(AST-enforced).

### Request

```python
def variable_state(self, variable_anchor_id: str, *,
                   as_of: datetime,                       # required, aware
                   entity_anchor_id: str | None = None,
                   source: SourceSelector | None = None) -> VariableStateResult
```

`SourceSelector` is a frozen `{subject: SourceSubjectRef, property:
SourcePropertyRef}` pair. Naive `as_of` (two-clause check: `tzinfo is
None or utcoffset(as_of) is None`) → `ModelStateQueryError(
"MODEL_STATE_NAIVE_AS_OF")` before any store access. Malformed
`variable_anchor_id`/`entity_anchor_id`/`source` →
`ModelStateQueryError("MODEL_STATE_INPUT_INVALID")`.

### Pipeline (always runs for valid input — no membership short-circuit)

1. Model membership: `variable_registration`, `owner_registration` from
   the loaded model (never fabricated; both None when unregistered).
2. Requested-entity dimensions (when supplied).
3. Reverse discovery via `resolver.declared_property_locators(...)` — or
   selector classification in selector mode.
4. Each queried locator → `bound.latest_observed(subject, property,
   as_of)` (verbatim result or None).
5. Per-candidate attachment classification.

**Evidence for an unregistered variable is a first-class outcome**: the
pipeline still discovers, queries, and resolves; the result reports
`model_membership="not_registered"` and per-candidate
`attachment="not_attachable_variable_unregistered"`. The evidence is
returned in identity/model limbo — never suppressed, never described as
model state.

### Response contract

```python
class VariableStateResult(_Frozen):
    variable_anchor_id: str
    as_of: UtcDatetime
    requested_entity_anchor_id: str | None

    model_membership: Literal["registered", "not_registered"]
    requested_entity_membership: Literal["registered", "not_registered",
                                         "not_supplied"]
    requested_entity_agreement: Literal["matches_owner", "differs_from_owner",
                                        "owner_unavailable", "not_supplied"]
    binding_discovery: Literal["declared_candidates", "no_declared_candidates",
                               "anchor_unknown_to_binding_set",
                               "explicit_selector"]
    selector_declaration: Literal["ever_declared_for_requested_variable",
                                  "ever_declared_for_other_variable",
                                  "undeclared", "not_applicable"]
    observation_availability: Literal["observed", "none_before_cutoff",
                                      "not_evaluated"]
    selection: Literal["none", "single", "multiple", "explicit"]

    variable_registration: VariableRegistration | None
    owner_registration: EntityRegistration | None
    requested_entity_registration: EntityRegistration | None
    model_revision: ModelRevision
    binding_revision: BindingRevision
    binding_declared_anchor: VariableAnchor | None       # binding set's, verbatim
    anchor_agreement: Literal["exact", "divergent", "binding_declaration_absent",
                              "model_registration_absent"]
    divergent_anchor_fields: tuple[str, ...]             # sorted; iff divergent
    declared_locator_count: int                          # both modes — explicit
                                                         # mode cannot hide multiplicity
    candidates: tuple[CandidateObservation, ...]

class CandidateObservation(_Frozen):
    subject: SourceSubjectRef
    property: SourcePropertyRef
    origin: Literal["declared_binding", "explicit_selector"]
    declaration: DeclaredLocatorEntry | None    # AMENDMENT 1: the exact
    # reverse-discovery entry used to discover or classify this locator,
    # carried verbatim from identity_binding — never copied, truncated,
    # reinterpreted, or reconstructed in model_state. Discovery candidates
    # always carry it; an explicit selector matching a declared locator
    # carries the corresponding entry; a completely undeclared selector
    # carries None.
    declared_via_assertion_ids: tuple[str, ...]  # deterministic convenience —
    # derivable from declaration.assertion_summaries (see invariants)
    bound: BoundLatestObserved | None            # IB facade result VERBATIM
    attachment: Literal["attached",
                        "not_attachable_variable_unregistered",
                        "not_attachable_anchor_divergent",
                        "not_attachable_resolution_mismatch",
                        "not_attachable_resolution_nonpositive",
                        "not_evaluated"]
```

There is **no aggregate value field and no attachment rollup** anywhere.

### Dimension semantics

- `model_membership`: variable in this model revision?
- `requested_entity_membership`: the supplied entity's own registration in
  this revision, independent of everything else.
- `requested_entity_agreement`: comparison to the variable's actual owner.
  `owner_unavailable` = entity supplied but variable unregistered, so no
  owner exists in this revision to compare (claiming matches/differs there
  would be unfounded). A wrong or unknown supplied entity **never** stops
  the evidence query.
- `binding_discovery`: locators ever declared for the variable in this
  binding revision (`declared_candidates` includes lifecycle-closed
  history, disclosed per candidate); `anchor_unknown_to_binding_set` =
  cross-set gap; `explicit_selector` = discovery bypassed for candidate
  construction (a selector-mode result is never complete discovery).
- `selector_declaration` (selector mode only, else `not_applicable`) —
  **"ever declared" means declared somewhere in this binding revision, not
  necessarily applicable or lifecycle-open at the observation time**:
  `ever_declared_for_requested_variable` when the selector's locator has
  ≥1 assertion targeting the requested variable (other targets stay
  visible in the entry); `ever_declared_for_other_variable` when it has
  property assertions targeting only other variables; `undeclared`
  otherwise. Explicit selection never creates or implies a binding — it
  only asks the accepted forward-resolution pipeline to inspect a locator.
- `observation_availability`: **asserts only that source evidence
  exists** — `observed` ⇔ some candidate has `bound is not None`;
  `none_before_cutoff` ⇔ candidates were queried and none had evidence at
  or before the cutoff; `not_evaluated` ⇔ zero locators queried. It never
  implies attachment to the requested model variable.
- `selection`: queried candidate locators — `none`=0, `single`=1,
  `multiple`≥2 (all surfaced, never ranked, identical values never
  collapse it), `explicit`=selector mode.
- `attachment` (per candidate, deterministic precedence, evaluated in
  order): `not_evaluated` (bound is None) → `not_attachable_resolution_nonpositive`
  (resolution did not positively bind any target) →
  `not_attachable_resolution_mismatch` (positively bound to a different
  variable) → `not_attachable_variable_unregistered` (bound to the
  requested variable, but it is not in this model revision) →
  `not_attachable_anchor_divergent` (registered and bound, but model and
  binding anchors diverge — attachment unsafe) → `attached`. Identity
  questions outrank model-membership questions; every underlying fact
  stays independently inspectable.
- `anchor_agreement` + `binding_declared_anchor` + `divergent_anchor_fields`:
  when the binding set declares the anchor, the declared `VariableAnchor`
  is carried verbatim; divergence lists the sorted names of every
  differing field. No reconciliation, no preferred version, no copied
  fields. Four outcomes: `exact`; `divergent` (both inputs inspectable);
  `binding_declaration_absent`; `model_registration_absent`.

### Cross-field invariants (pydantic-enforced)

1. `model_membership="not_registered"` ⇔ `variable_registration is None`
   ⇔ `owner_registration is None` ⇔
   `anchor_agreement="model_registration_absent"`. Candidates are NOT
   constrained by membership — evidence flows regardless.
2. Registered ⇒ `owner_registration.anchor.anchor_id ==
   variable_registration.anchor.entity_anchor_id`.
3. `requested_entity_anchor_id is None` ⇔ membership and agreement both
   `not_supplied`; `requested_entity_registration` present iff supplied
   and registered; agreement `owner_unavailable` ⇔ supplied ∧ variable
   unregistered; `matches_owner`/`differs_from_owner` require the variable
   registered (the owner exists to compare).
4. Selector mode ⇔ `binding_discovery="explicit_selector"` ⇔
   `selection="explicit"` ⇔ `selector_declaration != "not_applicable"` ⇔
   exactly one candidate with `origin="explicit_selector"`. Discovery mode
   ⇔ `selector_declaration="not_applicable"` ∧ all candidates
   `origin="declared_binding"` ∧ `declared_locator_count == len(candidates)`.
5. `binding_discovery="anchor_unknown_to_binding_set"` ⇔ (discovery mode ∧
   `binding_declared_anchor is None`); `anchor_agreement=
   "binding_declaration_absent"` ⇔ variable registered ∧
   `binding_declared_anchor is None`; `divergent_anchor_fields != ()` ⇔
   `anchor_agreement="divergent"`.
6. `observed` ⇔ some candidate `bound is not None`; `none_before_cutoff` ⇔
   candidates ≠ () ∧ all `bound is None`; `not_evaluated` ⇔ candidates == ().
7. `selection` counts: `none` ⇔ 0 candidates ∧ discovery mode; `single`/
   `multiple` ⇔ 1 / ≥2 discovery candidates; `explicit` ⇔ selector mode.
8. `binding_revision == candidate.bound.resolution.revision` for every
   bound candidate.
9. `attachment="not_evaluated"` ⇔ `bound is None`; `attachment="attached"`
   ⇒ registered ∧ `anchor_agreement="exact"` ∧ resolution bound to the
   requested variable.
10. **Amendment-1 validators**: per candidate, `declaration is None` ⇒
    `declared_via_assertion_ids == ()` ∧ `origin="explicit_selector"`;
    `declaration` present ⇒ `declared_via_assertion_ids` ⊆ its summaries'
    record ids (candidate-level) and — result-level, where the requested
    variable is known — `declared_via_assertion_ids == tuple(sorted(
    s.record_id for s in declaration.assertion_summaries if
    s.target_anchor_id == variable_anchor_id))`. Discovery candidates
    carry `declaration` always; selector candidates carry it iff
    `selector_declaration != "undeclared"`.

### Errors

`ModelStateError` base (code + path-free message, kernel convention) →
`ModelStateConfigurationError` (`MODEL_STATE_INPUT_INVALID`),
`ModelStateQueryError` (`MODEL_STATE_NAIVE_AS_OF`,
`MODEL_STATE_INPUT_INVALID` for malformed query arguments). Upstream typed
errors — `ModelKernelError`, `IdentityBindingError`, `TemporalError`
(including Task 0's `TemporalStoreError`) — propagate unchanged. No
`sqlite3` import, no storage-class recognition, no translation.

## Time-axis and revision semantics

- **Model revision is a knowledge context, not a time axis.** Selecting a
  revision selects membership, never a temporal cutoff.
- **`as_of` is on the accepted ingestion/receipt axis**, historically
  closed (what had been received by this instant — never what was true at
  the source).
- **Binding resolution is evaluated at each occurrence's own
  `received_at`** — never at `as_of`, never at the execution clock. A
  later binding revision does not rewrite an older occurrence's identity
  within a fixed revision; re-querying against a newer revision is a new
  knowledge context, disclosed via `binding_revision`.
- **Source-native time is retained evidence only** (`source_time`,
  `clock_segment_id`, clock-reset flags); it never enters cutoff
  comparison, staleness, or resolution.
- **Reproducibility** is scoped: same model revision + binding revision +
  `as_of` + an identical temporal projection (same schema and projector
  versions) reproduce a result exactly. The temporal projection has no
  revision concept of its own.

## Latest-per-locator limitation (stated prominently, verbatim in
## contracts, README, and demo)

> Per-locator latest only: each candidate reports the locator's most
> recent observation at or before the cutoff, forward-resolved at its own
> `received_at`. When that occurrence resolves elsewhere, the result means
> **no latest candidate observation attachable to the requested
> variable** — never "no observation ever." The historical last
> observation that once resolved to this variable belongs to a later,
> explicitly named history query.

## Demo fixture strategy

- Byte-hash pin the nine existing `models/demo-printer` records FIRST.
- Append exactly one `vrg_` record for the already-declared
  hotend-temperature variable `var_b7e2d3c4f5a6172839405a6b7c8d9e0f`
  (owner extruder `ent_a3f1c2d4…` already registered), authority
  `test_fixture` / `mk001_demo_fixture`, embedded anchor byte-equal to its
  committed declaration in `bindings/demo-printer`.
- Preserve the old nine-record revision
  `mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d023e3da83227f`
  as a pinned constant: replay reproduces it and `variable()` against it
  answers `not_registered`.
- Pin the new deterministic ten-record revision; prove it registers the
  exact declared `VariableAnchor`.
- Prove the happy-path Moonraker observation joins end-to-end: model
  registration → reverse binding → temporal observation → identity
  resolution at `received_at` → attachment → raw-record/checksum
  provenance.
- **After-window interpretation (accepted)**: a later query cutoff does
  not push an occurrence outside the binding interval — resolution runs at
  the occurrence's earlier in-window `received_at`, yielding an
  older/staler bound observation. The demo pins and explains this.
- The committed demo proves only the real happy path, append-only history,
  and revision replay. Conflict, lifecycle, selector, divergence, failure,
  and multiplicity cases use synthetic fixtures.
- No edits to existing model records, binding sets, raw evidence, or
  temporal fixtures.

## Threat, integrity, and failure model

Forged `vrg` files → content-hash mismatch; rehashed in-memory forgeries →
structural revalidation at every public boundary (inherited); authority
remains an unauthenticated claim (stated honestly). Cross-set anchor
divergence: commit-time honesty via the widened seam test; query-time
honesty via `anchor_agreement` (disclosed, never reconciled; persisted
divergence diagnostics deferred by owner decision). Temporal store
missing/corrupted/unreadable → `TemporalStoreError`
(`TEMPORAL_STORE_UNAVAILABLE`), never a false absence. Destroyed binding
store → IB's all-or-nothing load fails upstream. Silently-empty stores
(both `TemporalStore` and `BindingStore` mkdir on construction) stay out
of `model_state` by injection-only composition. Naive datetimes typed
before I/O. Path-free messages. Contradictory dimension combinations
unconstructible.

## Acceptance criteria

The adversarial matrix (~106 new test functions): kernel record/identity
integrity incl. forgery-matrix and golden-vector rows; revision/replay
incl. old-golden and byte-freeze pins; kernel queries incl. three-way
`variables_of` and hierarchy-absence; IB reverse lookup incl. time-free
probes, lifecycle disclosure, never-a-winner; model_state behavior incl.
the unregistered-variable-evidence-in-limbo first-class test,
whole-object-equality of carried `declaration` and `bound` against direct
IB calls, attachment-precedence boundaries, selector-declaration four-way,
divergence inspectability, falsy-values-vs-absence, temporal-unavailable
propagation; cross-time rows (resolution at `received_at`, later ingestion
cannot rewrite, revision ≠ cutoff, no cross-adapter ranking);
architectural boundaries (AST both directions, no locator/value/device
vocabulary in ledgers and contracts, no `sqlite3`, no private access, no
store construction); Task 0 red-first rows for missing/corrupted/
unreadable temporal storage. Expected suite shape: temporal_state 51 →
~57; model_kernel 213 → ~259; identity_binding 155 → ~169; model_state
0 → ~44; full clean-worktree suite ≈ 860–870, zero failures.

Verification commands (all with `-o addopts=""`):

```bash
.venv/bin/python -m pytest tests/model_state tests/model_kernel tests/identity_binding tests/temporal_state
.venv/bin/python -m pytest tests/
# plus base-only and all-extras clean-checkout runs from fresh clones/venvs
```

## Explicit exclusions

No units or datatype inference; no canonical unit conversion; no
equations, behavior, constraints, limits, or alarms; no calculated or
inferred state; no aggregation or sensor fusion; no source-authority
ranking; no automatic conflict resolution; no port modelling; no causal
reasoning; no commands or device control; no cached "authoritative current
state"; no API/UI work; no automatic variable creation from telemetry; no
automatic model mutation from bindings; no bulk fixture migration; no
Excel or other unrelated source-family work; no history fallback search
(later, explicitly named history query); no persisted divergence
diagnostics (deferred).
