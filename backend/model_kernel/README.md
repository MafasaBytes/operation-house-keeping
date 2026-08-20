# model_kernel

The MK-001 typed entity/relationship kernel: an append-only ledger of
explicit model knowledge over canonical `system_identity` anchors, with a
containment-derived hierarchy view. The bridge target of:

```text
data_sources → temporal_state → identity_binding → model_kernel
                        system_identity ────────→ model_kernel
```

Spec: `docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`;
decisions: `docs/adr/0007-model-kernel-typed-graph-ledger.md`.

## Boundary

Runtime code imports only `system_identity`, the standard library, and
pydantic (AST-enforced by test); it never reads or writes any binding,
temporal, or evidence store and operates identically when those stores do
not exist. The kernel provides no anchor-creation API: demo anchor IDs are
externally allocated fixture constants declared through `AnchorDeclaration`
records in an identity-binding ledger, and registrations embed those
`EntityAnchor` values verbatim. The kernel cannot prove at runtime that an
embedded anchor was declared — committed fixtures are seam-verified in CI;
runtime model sets use the documented external verification procedure.

## Semantics worth knowing

- **Ports are explicit model identities and claims** (PT-001 Slice A): a pure
  `PortAnchor` is permanently registered to one entity by an evidence-bearing
  `PortRegistration`; three independent interface dimensions, positive
  unordered 2–64-port topology hyperedges, and explicit compatibility claims
  use membership-relative correction DAGs and the generic PT withdrawal.
  Duplicate endpoints are rejected, connection roots may corroborate, and PCM
  citation validity is structural rather than chronological. Domain and
  interface-type tokens carry bounded qualified system, edition, and code
  identifiers plus their serialized dimension discriminator. Comparison is
  exact over all four fields; the kernel performs no vocabulary inference,
  equivalence, or conversion. Slice A adds only
  contracts, canonicalization, validating storage, and immutable indexes: PT
  queries, compatibility assessment, traversal, and committed fixture records
  remain owner-gated.
- **Variable meaning is explicit and per dimension** (ES-001):
  `VariableSemanticDeclaration` records quantity-kind and observation-role
  identity tokens independently. Each `(variable, dimension)` lineage is a
  multi-parent correction DAG; conflicts remain queryable, full-tip
  supersession converges them, and replay is membership-relative. Tokens assert
  identity only—no ontology, dimensional algebra, convertibility, behavior, or
  source meaning. Evidence-reference closure now applies uniformly to every
  evidence-bearing `rel_`, `vsp_`, and `vsm_` claim.
- **Variable constraints are explicit model claims** (CN-001 Slice A): an
  evidence-bearing permanent `ConstraintRegistration` binds one stable `con_`
  anchor to one registered variable. Evidence-bearing
  `VariableConstraintDeclaration` records carry exact quantity-kind, role, and
  unit token locks plus a lower, upper, or interval decimal predicate. Their
  multi-parent correction DAG is keyed only by constraint anchor; conflicts,
  convergence, superseded history, and replay are membership-relative and
  never ranked. Both `crg_` and `vcn_` model-record evidence is uniformly
  reference-closed. Evaluation belongs to the read-only
  `backend.constraint_evaluation` composition layer.
- **Variables are membership, not structure or state** (VM-001): a
  `VariableRegistration` embeds one canonical `VariableAnchor` verbatim.
  Ownership is identity (`anchor.entity_anchor_id` — no `variable_of`
  edge); the owner entity must be registered in the same revision
  (reference-closed, including replay subsets); one registration per
  variable anchor (duplicates rejected whether embedded fields agree or
  conflict — never tie-broken); variables never appear in hierarchy views;
  `variable()` / `variables_of()` answer membership with structured
  absence. Like entity registrations: no lifecycle, no correction path,
  no units, no datatype, no meaning, no state.
- **Registrations have no lifecycle**: no supersession, no withdrawal, no
  path that alters an embedded anchor field. Two distinct registrations for
  one anchor invalidate the revision.
- **All relationship types are data** (`contains` and `instance_of`
  included). Type identity is a lineage named by `type_name`; supersession
  preserves `{type_name, directionality, hierarchy_semantics,
  context_requirement}`; exactly one current definition per name.
  Assertions are judged by the exact definition they cite and stale-marked
  when it is superseded — never retro-invalidated.
- **Validating append**: every supplied record is structurally revalidated
  from serialized field data at the public boundary (a record class alone
  proves nothing — `model_copy`/`model_construct`/stale instances bypass
  validation and can be rehashed), then `append` fully validates the
  current set and the prospective set before an atomic staged promote —
  absent filesystem tampering, the on-disk ledger is a valid revision after
  every successful append. Identical re-append is a validated no-op that
  still fails if any sibling is corrupted. Single-writer, honestly stated.
- **Public inputs are validated at every entry point**: query arguments
  (anchor id, type name, direction, lifecycle view →
  `MODEL_VIEW_INVALID`, assertion context → normalized mappings or
  `MODEL_CONTEXT_INVALID`) and store arguments (set directory, record
  collection, model id, replay membership) alike. Malformed input is never
  a silently empty answer, and **every operational public entry point of
  the kernel — queries, `ModelStore` construction, `append`, `load`,
  `replay`, `validate_record_collection`, `build_record`, and
  `ModelQueries` construction — fails through the `ModelKernelError`
  tree**: no `ValidationError`, `AttributeError`, `TypeError`, `KeyError`,
  `UnicodeError`, `OSError`, serializer error, or warning escapes as the
  public outcome. Direct construction of the pydantic contract models
  (`EntityRegistration(...)` and friends) is the one deliberate carve-out:
  it follows pydantic's normal `ValidationError` contract.
- **Absence is structured**: `RelationshipsResult.status` distinguishes a
  registered entity with no matching edge from an anchor unknown to the
  revision.
- **Supported surface**: import from `backend.model_kernel` (see
  `__all__`); canonicalization internals, collection validation, and the
  hierarchy projection are private implementation details.
- **Contention is surfaced, malformation invalidates**: distinct-parent/
  same-child conflicts and cycles are structured query results with full
  candidate/assertion disclosure, never resolved by recency or authority;
  dangling references, tampering, duplicate registrations/current names,
  endpoint-kind and context violations invalidate the complete revision.
- **Traversal is deliberately asymmetric**: parent conflicts block upward
  queries (`conflicted`/`partial`) but annotate — not block — downward
  traversal (`multiple_parents`); cycles block both directions.
- **Strict context equality**: every assertion carries a required
  lifecycle-view or view-independent context matching its type; queries
  match one context exactly, never a union; mismatches are typed errors.
- **Evidence explains every edge**: discriminated typed references,
  canonicalized (order- and duplication-insensitive); `model_record`
  references are verified in-revision, all foreign kinds are labeled
  `declared_reference` and never dereferenced.
- **Revisions replay**: `mrv_` revisions are computed-only (never stored);
  `replay(record_ids)` validates pattern-checked, reference-closed subsets
  against the still-present files, with membership-relative currentness.
  Membership input is validated before any member path is constructed;
  then store availability is probed before member reads. Empty membership
  is a valid revision only over an available model store; it is not
  evidence that a missing store is empty (`MODEL_STORAGE_FAILURE` when the
  records directory is gone, replaced, or unreadable). Exact-subset replay
  never requires unrelated ledger members to validate.
- **Cleanup is best-effort**: if promoting a staged record fails and
  removing the staging temp then fails too, harmless staging residue may
  remain — it never masks the typed `MODEL_STORAGE_FAILURE` and never
  corrupts a later `load`.

## Verification

```bash
.venv/bin/python -m pytest tests/model_kernel/   # focused suite
.venv/bin/python -m pytest                       # full repository suite
```

## Known limitations

No kernel correction path for registrations; registrations and type
definitions are irrevocable (no withdrawal); a lineage may end with no
active assertion; disagreement detection exists only for hierarchy types;
no time-varying structure (`rwd_` never means "stopped being true at T");
runtime registration↔declaration consistency is procedural; no global
cross-set anchor uniqueness at runtime; no knowledge-time revision queries;
single-writer stores; no fsync-grade durability claim. Validating append
is O(N²) to build an N-record ledger — accepted for MK-001 scale. The
typed-failure translation catches an enumerated exception set: a hostile
in-process class whose metaclass raises outside it can still surface that
exception, and exception `__cause__` chains can carry raw payloads into
full tracebacks (public messages stay clean). PT-001 Slice A is implemented
and awaiting owner acceptance; port queries and the bounded synthetic fixture
remain separately gated. Richer predicates beyond CN-001's exact numeric bounds
also remain future work.
