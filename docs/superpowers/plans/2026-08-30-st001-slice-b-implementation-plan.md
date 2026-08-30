# ST-001 Slice B — Read-Only Kernel Queries Implementation Plan

Status: Slices A-B owner accepted; Slice C separately authorized; Slice D unauthorized and unstarted

Slice B is owner accepted at `23eca10a52c0124d22b4e90d80bef952ef5f9381`.

Date: 2026-08-30

## 1. Objective and boundary

Implement only the four accepted read-only `ModelQueries` methods and their
authoritatively reconstructed carry-once result contracts:

1. `state(state_anchor_id) -> StateLookupResult`
2. `state_declaration(state_anchor_id, *, context) -> StateDeclarationResult`
3. `states_of_entity(entity_anchor_id, *, context) -> EntityStatesResult`
4. `state_assertion(record_id) -> StateAssertionDisclosureResult`

All production work remains in `backend/model_kernel`. No store, record,
canonical, identity, ledger, fixture, membership, temporal, CN, or
classification behavior changes are authorized.

## 2. Administrative gate

The first Slice B commit must precede implementation and must:

- remove the two committed Markdown trailing-space sequences from the Slice A
  completion report;
- record Slice A owner acceptance and Slice B authorization;
- record honestly that the earlier clean-tree `git diff --check` did not inspect
  the committed milestone range;
- pass both `git diff --check` and
  `git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD`.

This gate was completed at
`dbc09283e26345192e096236680e455ce72c1c1e` before this plan.

## 3. Production contract layout

Add a dedicated `backend/model_kernel/state_results.py` following the accepted
BH carry-once pattern while deriving state-specific truth from accepted Slice A
indexes and the exact `_state_effective_body_bytes` projection.

The module will define and export only:

- six named state-specific literal aliases;
- `StateConditionReferenceResult`;
- `StateEffectiveBodyGroupResult`;
- `StateDeclarationRootResult`;
- `StateLookupResult`;
- `StateDeclarationResult`;
- `EntityStateEntry`;
- `EntityStatesResult`;
- `StateAssertionDisclosureResult`.

It will reuse `AssertionActivity`, `ContainingLineageHealth`,
`ModelQueryMaterial`, and the existing `ModelQueryError` boundary. Nested rows
carry strict non-boolean indices only. Complete model authority appears only in
the outer result's `material` field.

## 4. Red-first implementation groups

### 4.1 Public surface red group

Add failing tests that pin:

- exact aliases and literal order;
- exact model field order;
- exact method signatures and return annotations;
- exact additive package `__all__` order;
- absence of alternate names;
- typed malformed state/record input failures.

Commit these failing tests before adding production symbols.

### 4.2 Lookup and structured-absence red group

Add failing tests for:

- absent/present `state()`;
- canonical condition-aligned constraint, variable, and owner indices;
- repeated owner indices;
- every explicit pre-ST membership;
- absent/present entity and registered-empty `states_of_entity()`;
- valid-shaped absent assertions.

Then implement the smallest query/result support to make this group green.

### 4.3 Lifecycle/corroboration red group

Add failing disposable-world tests for:

- not-declared, declared, inactive, and conflicted conclusions;
- one healthy root;
- same-root fork and partial/full convergence;
- identical independent healthy roots as corroboration;
- cross-root effective-body disagreement;
- inactive root beside a surviving corroborating root;
- selective and complete withdrawal;
- historical revival;
- deterministic roots, lineages, tips, withdrawals, groups, and condition rows.

Then implement one private deterministic payload derivation shared by query
construction and public result validators. Do not select a winner record.

### 4.4 Assertion and hostile-revalidation red group

Add failing tests for:

- SRG/STD/STW assertion shapes;
- STD current/superseded/withdrawn activity independently of root and subject
  health;
- strict non-boolean/out-of-range/wrong-arm indices;
- missing, duplicate, extra, reordered, mixed-revision, mixed-context, and
  substituted material/rows;
- forged root health, effective-body equality, corroboration, findings,
  conclusion, ordering, and activity;
- nested `model_construct`, `model_copy`, and stale-ID attacks;
- validation with store/filesystem APIs monkeypatched to fail.

Then harden only the public query-result boundary. Store-independent validation
may call the pure collection validator but may not construct or access
`ModelStore` or the filesystem.

## 5. Exact derivation rules

For one exact `(state_anchor_id, AssertionContext)` lineage key:

1. order root IDs lexicographically;
2. recompute complete lineage, current tips, withdrawals, and root health;
3. project every active tip using `_state_effective_body_bytes`;
4. order groups by those canonical bytes;
5. carry every tip and root in its group without merging records or identity;
6. mark any same-root active fork as aggregate conflict;
7. mark multiple active body groups as cross-root disagreement;
8. retain inactive roots and emit `inactive_roots_present`;
9. use exactly one active body group across one or more healthy roots as
   `declared / healthy`;
10. use no ID, timestamp, authority, filename, or append order as truth.

Conditions inside a body group are ordered by constraint anchor ID and resolve
the exact pinned VCN, CRG, target VRG, and owner ERG through strict indices.

## 6. Authoritative validation

Every outer result validator will:

- reconstruct `ModelQueryMaterial` from serialized content;
- invoke its pure in-memory `loaded()` reconstruction;
- recompute exact revision membership and all Slice A closure/lifecycle facts;
- recompute query-specific payload and compare every supplied field exactly;
- rebuild every nested row from serialized field content before comparison;
- bind read-only convenience properties only after successful validation.

No validator may enumerate a directory, instantiate a store, read a file,
perform network access, mutate the model, or trust an existing nested instance.

## 7. Documentation and review

Update only model-kernel/ST status documentation needed to describe the exact
Slice B read-only surface and preserve its non-claims.

After the first green implementation, request bounded independent reviews for:

1. architecture/import and Slice B scope;
2. model-kernel payload/canonical/lifecycle integrity;
3. adversarial coverage and hostile reconstruction.

Every confirmed finding must first receive a failing reproduction, then the
smallest in-scope repair, with the reproduction retained.

## 8. Verification matrix

Run and record exact counts for:

1. focused Slice B query tests;
2. complete ST Slice A+B tests;
3. complete model-kernel suite;
4. system identity and affected CN/PT/VP/BH/model-state suites;
5. architecture/import-isolation;
6. explicit replay and artifact preservation;
7. backend compilation;
8. complete repository suite;
9. fresh base-only checkout;
10. fresh all-extras checkout;
11. focused OCP/STEP/PDF paths;
12. permitted standalone loopback rerun if aggregate setup is denied;
13. clean-tree and full-milestone-range `git diff --check`;
14. branch, status, and topology checks.

## 9. Commit plan

Use small reviewable groups:

1. administrative acceptance/whitespace repair — already committed;
2. Slice B plan and adversarial matrix;
3. red public-contract tests;
4. result contracts and query surface;
5. red lifecycle and collection tests;
6. lifecycle/corroboration derivation;
7. red hostile-revalidation tests;
8. authoritative revalidation hardening;
9. specialist reproductions and repairs, if any;
10. documentation/status update;
11. completion report.

## 10. Stop gate

Slice B completes only after every applicable matrix row is green, all
verification columns are recorded, both diff checks pass over the resulting
committed range, the tree is clean, the demo remains 32 records with zero ST
records, and the completion report is committed separately.

Stop for owner acceptance. Slices C and D remain unstarted and unauthorized.

END OF ST-001 SLICE B IMPLEMENTATION PLAN
