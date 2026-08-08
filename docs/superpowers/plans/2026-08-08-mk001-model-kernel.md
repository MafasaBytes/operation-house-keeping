# MK-001 Model Kernel Implementation Plan

**Spec:** `docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`
(self-contained, authoritative). **ADR:** `docs/adr/0007-model-kernel-typed-graph-ledger.md`.

**Hard boundaries (checked at every slice):** the enforceable upstream
boundary — (a) no changes to accepted code under
`backend/{data_sources,temporal_state,identity_binding,system_identity}`;
(b) no edits/deletions to existing `bindings/demo-printer/` records; (c) the
new synthetic declaration fixture `bindings/demo-printer-model/` is the only
upstream-layer data addition; (d) no `model_kernel` runtime code reads or
writes any binding set. Preserve all pre-existing working-tree changes
(`.gitignore`, four `temporal_state` comment edits) — never commit them.
Runtime imports: `system_identity` + stdlib + pydantic only. Strict TDD:
write the failing tests, run and CAPTURE the red output (evidence for the
test-engineer audit), implement minimally, re-run green, commit. Small local
commits; no push.

**Verification commands:**

```bash
.venv/bin/python -m pytest tests/model_kernel/ -q     # focused
.venv/bin/python -m pytest tests/ -q                  # full repository
```

Baseline to preserve: 544 all-extras / 511 + 33-skip base-only.

## Task 1 — Contracts and canonical identity

Files: `backend/model_kernel/{__init__,contracts,canonical}.py`,
`tests/model_kernel/{__init__,test_contracts,test_canonical}.py`.

1. Failing tests — contracts: frozen/extra-forbid on every record kind and
   result type; per-kind record-id patterns; registration has NO
   `supersedes` field (semantic guard: unknown-field rejection AND, later in
   store tests, the semantic duplicate error); rtd_ lineage fields +
   containment⇒no-self validator + four-literal sorted-unique endpoint
   tuples (unknown as opt-in member); rel_ context arms, evidence min-1,
   supersedes pattern; rwd_ shape; ModelRevision self-validation (sorted/
   unique/count/hash/member-pattern incl. mrv_ exclusion); result-contract
   invariants (active ⇔ empty links; bound-style status/field coherence on
   Parent/Traversal/Relationships results; sorted-unique collections;
   LineageConflict min 2).
2. Failing tests — canonical: prefix map for the four kinds; full-64-hex
   ids; record_id excluded from its own hash; offset-normalized timestamps
   hash identically; schema_version covered; **evidence canonicalization
   golden test** (permuted + duplicated evidence inputs → identical
   record_id; duplicates normalized away; min-1 after normalization);
   canonical-parity vectors: `identity_binding.canonical.canonical_bytes`
   and the kernel's produce identical bytes for shared duck-typed inputs.
3. Run, capture red. Implement `canonical.py` (duck-typed; imports no
   contracts) and `contracts.py`. Green. Commit
   `feat: model_kernel contracts and canonical identity`.

## Task 2 — Store: validating append, load, replay, LoadedModel

Files: `backend/model_kernel/store.py`,
`tests/model_kernel/{test_store,test_validation}.py`.

1. Failing tests — validating append order per spec: current-set validation
   precedes every result (tamper another member, then identical re-append →
   typed error, nothing written — the amendment-4 case); idempotent
   identical no-op; tampered-existing detection; five adversarial append
   rejections (dangling rel, duplicate registration, incompatible endpoint,
   context mismatch, duplicate current type name) each leaving the prior
   revision byte-identical and loadable; staging outside `records/`;
   failed-promotion cleanup; construction-order documentation behavior.
2. Failing tests — load/validation: every integrity invariant from the spec
   numbered list (parametrized crafted files: hash/key/filename mismatch,
   unknown kind/version, duplicate registration, lineage violations incl.
   branched chains, endpoint kinds incl. unknown fail-closed and opt-in
   positive, self-relation, context arm, supersession identity incl.
   cross-lineage, dangling everything, withdrawal targets); empty set valid;
   one bad record poisons the set; input-mapping mutation isolation; deep
   immutability (dataclass-introspected mapping enumeration; no
   list/set/dict fields anywhere — annotation audit).
3. Failing tests — replay: pattern-check before path construction
   (traversal member + planted decoy), duplicates rejected, missing member,
   reference-closed subsets (parametrized exclusions), earlier-membership
   replay after later appends, membership-relative currentness.
4. Failing tests — path leakage: parametrized representative errors
   (configuration, malformed file, hash mismatch, replay, append validation)
   assert no absolute tmp/store paths in messages.
5. Red → implement `store.py` → green. Commit
   `feat: model_kernel validating-append ledger store`.

## Task 3 — Hierarchy projection, queries, lineage lifecycle

Files: `backend/model_kernel/{hierarchy,queries}.py`,
`tests/model_kernel/{test_hierarchy,test_queries,test_lifecycle}.py`.

1. Failing tests — hierarchy: parents precedence (not_registered / cyclic /
   conflicted / resolved / no_declared_parent); distinct-parent/same-child
   conflict vs same-edge corroboration (all supporting ids preserved);
   cross-view non-conflict; direct + 3-node cycles, per-(lineage,view)
   scoping, subtree isolation; children/descendants proceed through
   multi-parent children with `multiple_parents` annotations; ancestors
   partial + blocking node (conflicted vs cyclic distinguished); cycles
   block both directions; deterministic DFS-preorder canonical ordering;
   hierarchy_health (cycles, parent conflicts, stale-type assertions);
   lineage-scoped hierarchy spans corrected definitions.
2. Failing tests — queries: strict context equality (no unions; both arms);
   MODEL_VIEW_REQUIRED/FORBIDDEN/CONTEXT_MISMATCH/UNKNOWN_TYPE/
   NOT_A_HIERARCHY typed errors; entity registered/not_registered;
   direction filters + inverse labels; insertion-order independence
   (shuffled appends → identical revision + results); results embed the
   revision.
3. Failing tests — lifecycle: five disclosure states; competing successors
   in `active` + `lineage_conflicts`, never timestamp-resolved; withdrawal
   preserves records; non-reactivation; empty-lineage consequence; both-facts
   disclosure; stale `cited_type_current` marking; same-parent competing
   successors = corroboration + lineage conflict (independent facts).
4. Red → implement `hierarchy.py`, `queries.py` → green. Commit
   `feat: model_kernel hierarchy projection and queries`.

## Task 4 — Demo fixtures, seam, isolation, end-to-end

Files: `bindings/demo-printer-model/records/*.json` (3 declarations,
generated through `identity_binding`'s own store code as fixture tooling),
`models/demo-printer/records/*.json` (9 records via `ModelStore`),
`backend/model_kernel/README.md`, `backend/system_identity` untouched,
`models/README.md`,
`tests/model_kernel/{test_isolation,test_cross_layer_seam,test_demo_model}.py`.

1. Failing tests — isolation: AST import inspection (only system_identity/
   stdlib/pydantic; reject the three lower modules); no path-based store
   access in runtime source; kernel operates identically with no
   `bindings/`, temporal, or evidence store roots present; byte-for-byte
   sweeps over accepted stores + existing
   `bindings/demo-printer/` across all kernel ops including failures.
2. Failing tests — seam: embedded anchors field-for-field vs declarations
   (both binding sets); negative controls (diverged value, never-declared
   anchor) proving teeth; cross-set duplicate anchor sweep; restated
   evidence patterns pinned to upstream constants
   (`identity_binding.contracts.LEDGER_RECORD_ID_PATTERN`,
   `system_identity` patterns, `data_sources.contracts` RecordId/
   FullTaggedSha256); canonical parity re-run on committed records.
3. Failing tests — demo: committed sets load valid (golden revision id,
   exact membership); authority test_fixture everywhere, never human_owner;
   no secrets/absolute paths committed; parents/ancestors/children/
   instance_of/no_declared_parent expected shapes; full provenance chain
   through evidence references.
4. Generate fixtures; green. Commit
   `feat: committed MK-001 demo model and declaration fixture`.

## Task 5 — Gates and final verification

1. software-test-engineer audit: red-first evidence per slice (captured
   outputs), amended-matrix coverage sweep.
2. code-reviewer adversarial review; findings repaired in separate tested
   commits.
3. Focused suite; full suite; base-only and all-extras clean checkouts;
   upstream-boundary proof; memory checkpoint; final report; stop for owner
   validation.
