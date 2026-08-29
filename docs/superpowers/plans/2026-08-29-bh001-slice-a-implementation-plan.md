# BH-001 Slice A — identity and kernel record foundation implementation plan

Status: corrected final BH-001 design and Slice A owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. Slice B is
owner-authorized but not yet implemented. Slices C and D remain unstarted.

Accepted repository base: `main` at
`46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`.

Accepted documentation commit on branch `bh001`:
`703564fc19a834e9ee9a38f336eeec6e7642b0c1`.

Authoritative specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`
at SHA-256
`2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`.

ADR: `docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md`.

## 1. Slice boundary

Slice A implements only:

- `BehaviorAnchor`, `BEHAVIOR_ANCHOR_ID_PATTERN`, and
  `mint_behavior_anchor()`;
- `BehaviorRegistration`, `BehaviorVariableSemanticLock`,
  `ExactNumericEqualityRule`, `BehaviorRuleDeclaration`, and
  `BehaviorRuleWithdrawal`;
- the `bhv_`, `brg_`, `bhd_`, and `bhw_` canonical grammars and mappings;
- the accepted model-record and citable-evidence union changes;
- the existing public `build_record()` path for all three BH record kinds;
- validating append/load/replay admission;
- immutable registration, lineage, ancestry, successor, tip, and withdrawal
  indexes;
- the private canonical effective-engineering-body projection needed to pin
  future corroboration semantics;
- historical replay, byte preservation, forgery, import-isolation, and public
  contract tests;
- Slice A documentation and its file-first completion report.

Slice A does not implement:

- `ModelQueries.behavior()`;
- `ModelQueries.behavior_declaration()`;
- `ModelQueries.behaviors_involving_variable()`;
- `ModelQueries.behavior_assertion()`;
- any BH query/result/status contract or implementation alias;
- `backend.behavior_evaluation` or numeric comparison;
- source selectors, model-state composition, semantic evaluation, temporal
  cohort admission, or CN-parser integration;
- a new store, ledger, repository, revision, cache, projection, or database;
- demo, model, binding, interpretation, temporal, source, structural, or
  artifact mutation;
- a port/VPA field or query, participant role, direction, input/output, flow,
  influence, causality, control, compatibility, correctness, safety,
  diagnosis, or recommendation.

Every gate below stops for a discrepancy report if implementation would require
changing an accepted architectural decision.

## 2. Gate 0 — baseline and preservation capture

Before production changes:

1. Verify branch `bh001`, ancestor base `46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`,
   and accepted documentation commit
   `703564fc19a834e9ee9a38f336eeec6e7642b0c1`.
2. Verify `main` and `origin/main` remain at the accepted base and the only
   branch changes are the accepted/planned BH documentation.
3. Confirm the committed demo contains exactly 29 records and loads at
   `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
4. Capture SHA-256 and byte count for all 29 existing model-record files.
5. Pin the explicit 9-, 10-, 11-, 14-, 16-, 18-, 28-, and 29-record
   memberships and their accepted revision IDs from repository constants.
6. Pin the VP artifact SHA-256
   `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`
   and PT artifact SHA-256
   `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
7. Record hashes/status for prohibited paths, including
   `.claude/settings.local.json`, and never stage or modify them.
8. Record a clean pre-production `git diff --check` and complete accepted-suite
   result if it has not already been reproduced on the branch.

The preservation baseline belongs in the eventual completion report; do not
paste large hash or test transcripts into chat.

## 3. Gate 1 — persist Slice A design controls

Commit the accepted ADR, this plan, and the complete BH-001 adversarial
acceptance matrix before implementation. The design/specification and
file-first protocol are already accepted in the first administrative commit.

Documentation must state:

- exact Slice A contracts and exclusions;
- all four owner-gated slices;
- permanent registration versus contextual correctable declaration;
- same-root fork conflict and cross-root effective-body corroboration;
- evidence and authority disclosure without winner selection;
- BHW's evidence-free, uncitable, non-negative meaning;
- no port/VPA or evaluator semantics in Slice A;
- unchanged explicit historical memberships and 29-record demo.

Expected documentation commit:

```text
docs: add BH-001 Slice A architecture and plan
```

## 4. Gate 2 — red-first identity contracts

Add focused failing tests before editing `backend/system_identity`.

Pin:

1. `BEHAVIOR_ANCHOR_ID_PATTERN == r"^bhv_[0-9a-f]{32}$"`.
2. Exact `BehaviorAnchor` field order:

   ```text
   anchor_id
   namespace
   display_name
   role_name
   ```

3. Frozen, extra-forbidden, full-instance revalidation.
4. Rejection of wrong prefix, case, hexadecimal alphabet, and length.
5. Existing namespace, display-name, and role-name validation.
6. Absence of owner, participant, context, evidence, rule, lifecycle,
   direction, state, causality, port, and VPA fields.
7. `mint_behavior_anchor()` emits unique RFC-4122 UUID4 hex identities and
   delegates all human-field validation to the contract.
8. `system_identity.__all__` changes only by:

   ```text
   BEHAVIOR_ANCHOR_ID_PATTERN
   BehaviorAnchor
   mint_behavior_anchor
   ```

9. `backend.system_identity` remains a pure value namespace with no Pydantic
   internal imports, filesystem, store, model-kernel, or evaluator dependency.

Record the focused missing-symbol failure before production edits, then add the
smallest implementation in:

- `backend/system_identity/anchors.py`;
- `backend/system_identity/minting.py`;
- `backend/system_identity/__init__.py`.

Do not refactor `EntityAnchor`, `VariableAnchor`, `ConstraintAnchor`, or
`PortAnchor`.

## 5. Gate 3 — red-first record and canonical contracts

Write contract and canonical tests before editing `model_kernel`.

### 5.1 Exact public record fields

Pin `BehaviorRegistration`:

```text
record_kind
schema_version
record_id
anchor
participant_variable_anchor_ids
rule_family
evidence
recorded_at
authority
note
```

Pin `BehaviorVariableSemanticLock`:

```text
variable_anchor_id
signature
```

Pin `ExactNumericEqualityRule`:

```text
kind
```

Pin `BehaviorRuleDeclaration`:

```text
record_kind
schema_version
record_id
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
evidence
supersedes
recorded_at
authority
note
```

Pin `BehaviorRuleWithdrawal`:

```text
record_kind
schema_version
record_id
withdraws
recorded_at
authority
note
```

Every model is frozen and extra-forbidden. New record and nested contracts use
full-instance revalidation plus before-validators that dump/reconstruct nested
anchor, context, lock, signature/token, rule, evidence, and authority content.

### 5.2 Shape and meaning tests

Test red-first that:

- BRG accepts exactly two distinct unordered variables, normalizes them by
  variable ID, and fixes `rule_family` to `exact_numeric_equality`;
- reversing participant input produces identical validated content, canonical
  bytes, and record ID;
- BHD accepts exactly the BRG pair as variable-keyed locks, sorts by variable
  ID, requires exact quantity-kind and unit identity equality, and permits
  equal or different observation-role identities;
- swapped variable-to-signature association remains visible and cannot be
  erased by sorting signatures alone;
- `ExactNumericEqualityRule` contains no operator, coefficient, offset,
  constant, tolerance, expression, ordering, direction, or label;
- `evaluation_basis` accepts only `same_acquisition_cohort`;
- BHD parent tuples reject malformed IDs, duplicates, and self-supersession,
  and canonicalize valid caller order before hashing;
- BHW targets only a valid `bhd_` shape and forbids evidence, context, parents,
  outcome, replacement, and negative-behavior fields;
- boolean, port, VPA, participant-role, input/output, state, value, unit,
  temporal cutoff, flow, influence, causality, control, compatibility,
  correctness, safety, diagnosis, and recommendation fields are rejected.

### 5.3 Canonical ripple and golden tests

Red-first tests must pin:

- `brg_`, `bhd_`, and `bhw_` record-ID grammar;
- identical record identity under reversed BRG participants, BHD locks,
  evidence, and valid parents;
- exact canonical golden bytes and IDs for one valid BRG, BHD, and BHW;
- stale ID rejection after any content mutation;
- filename/content and mapping-key/content mismatch rejection;
- `brg_` and `bhd_` are citable `ModelRecordEvidence` arms;
- `bhw_` is not citable;
- all three are authoritative `ModelRecord` union arms;
- the existing `build_record()` API builds each kind; no BH-specific builder
  function is added;
- every existing record kind retains its exact golden canonical bytes and ID.

The only new public `backend.model_kernel.__all__` names in Slice A are:

```text
BehaviorRegistration
BehaviorVariableSemanticLock
ExactNumericEqualityRule
BehaviorRuleDeclaration
BehaviorRuleWithdrawal
```

Do not export private tuple normalizers, effective-body helpers, query names,
result contracts, evaluator types, or implementation aliases.

### 5.4 Production ripple sites

Apply only these additive changes:

| Site | File | Slice A change |
|---|---|---|
| Behavior identity import | `backend/model_kernel/contracts.py` | import `BehaviorAnchor` and behavior ID pattern |
| Model record grammar | `backend/model_kernel/contracts.py` | add `brg|bhd|bhw` |
| Citable evidence grammar | `backend/model_kernel/contracts.py` | add `brg|bhd`; exclude `bhw` |
| Record/nested contracts | `backend/model_kernel/contracts.py` | add the five accepted BH contracts |
| Record union | `backend/model_kernel/contracts.py` | add BRG/BHD/BHW |
| Canonical prefix map | `backend/model_kernel/canonical.py` | exact three kind-prefix entries |
| Filename grammar | `backend/model_kernel/store.py` | add `brg|bhd|bhw` |
| Store imports/buckets | `backend/model_kernel/store.py` | exact three record buckets |
| Loaded indexes | `backend/model_kernel/store.py` | accepted BH immutable indexes |
| Public exports | `backend/model_kernel/__init__.py` | only the five Slice A kernel names |

`_RECORD_ADAPTER`, `compute_record_id`, `compute_revision_id`, and the public
builder are already generic and should not be forked. Do not change canonical
serialization for an existing record family.

## 6. Gate 4 — red-first registration and evidence admission

Before store implementation, add failing append/load/replay tests for:

1. unknown first variable;
2. unknown second variable;
3. a variable whose owner registration is missing in an explicit replay;
4. duplicate BRGs for one `bhv_`, whether their embedded bodies agree or not;
5. missing exact first VRG citation;
6. missing exact second VRG citation;
7. a citation to a different VRG instead of the registered participant;
8. missing `OwnerDeclarationEvidence`;
9. empty evidence;
10. additional missing model-record evidence;
11. valid same-owner pair;
12. valid cross-owner pair with explicit evidence;
13. proof that shared ownership alone creates no BRG;
14. hostile embedded behavior anchor and evidence instances;
15. failed append leaves no JSON or staging residue and leaves revision
    unchanged.

Store admission must require the two exact VRG citations as a subset of the
canonical evidence tuple; additional supported evidence arms remain allowed and
uniform model-record closure applies to every citation.

## 7. Gate 5 — red-first declaration DAG and indexes

### 7.1 Declaration admission

Add failures for:

- absent behavior registration;
- semantic-lock IDs that are missing, duplicated, or differ from the BRG pair;
- unequal quantity-kind or unit identities;
- missing exact BRG evidence citation;
- missing `OwnerDeclarationEvidence`;
- missing additional model-record evidence;
- malformed, unknown, wrong-kind, self, cross-anchor, or cross-context parent;
- duplicate parents and caller-order instability;
- forged nested context, signature tokens, lock, rule, evidence, or authority;
- stale declaration ID after nested mutation.

Do not validate a lock against current VSP, VSM, source interpretation, or
observation evidence in Slice A.

### 7.2 Root and correction semantics

Use iterative, bounded-by-membership DAG validation. Test:

- one parentless root;
- a healthy correction chain;
- a valid fork with two active tips;
- identical-body same-root forks remaining structurally conflicted;
- partial convergence leaving another active tip;
- complete same-root multi-parent convergence;
- several independent roots for the same lineage key;
- independent identical engineering bodies admitted as corroborating material;
- independent different engineering bodies admitted as conflicting material;
- cross-root convergence rejection;
- cycle rejection, including crafted hash-skipping collections;
- exact context separation.

Slice A retains the roots and active tips without selecting a winner. Add one
private canonical effective-body projection helper, using the repository's
canonical JSON rules, and pin that it includes exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

and excludes record kind, schema, ID, evidence, parents, authority, recorded
time, note, filename, and append order. The helper is not persisted or publicly
exported. Public body groups, corroboration findings, and aggregate conclusions
remain Slice B.

### 7.3 Withdrawal semantics

Add failures for:

- missing or non-BHD target;
- BRG and BHW target;
- superseded target;
- already-withdrawn target;
- duplicate withdrawal;
- successor and withdrawal of the same target in one membership.

Add valid cases for:

- withdrawal of one healthy current tip;
- selective withdrawal of one fork tip;
- all current tips withdrawn;
- replay of earlier membership without successor;
- replay of earlier membership without withdrawal.

BHW has no citable evidence and carries no negative claim.

### 7.4 Exact LoadedModel indexes

Add the following copied, read-only, deterministic mappings:

```text
behavior_registrations
behavior_registrations_by_anchor
behavior_anchor_ids_by_variable

behavior_rule_declarations
behavior_rule_ids_by_key
behavior_rule_root_by_id
behavior_rule_ancestry_by_id
behavior_rule_superseded_by
current_behavior_rule_tips_by_root

behavior_rule_withdrawals
behavior_rule_withdrawn_by
behavior_rule_withdrawals_by_target
```

Keys use exact anchor IDs or `(behavior_anchor_id, AssertionContext)` as
specified. All record-ID tuples and record tuples are canonical by record ID;
behavior-anchor reverse tuples are canonical by anchor ID. Empty pre-BH models
carry immutable empty mappings. Mutation of the input mappings or returned
mapping proxies cannot alter a validated revision.

## 8. Gate 6 — hostile boundaries, replay, and non-inference

Run the same records through every public Slice A boundary:

- direct construction;
- `build_record()`;
- `TypeAdapter(ModelRecord)`;
- `validate_record_collection()`;
- prospective `ModelStore.append()`;
- on-disk `ModelStore.load()`;
- explicit `ModelStore.replay()`.

Attack each with `model_construct`, `model_copy`, stale IDs, malformed nested
instances, valid-looking substitutions, wrong union arms, filename mismatch,
external symlinks, duplicate parents, cycles, and reversed/hash-seed ordering.
Every failure must be typed and append failures must be atomic.

Non-inference fixtures may coexist with common owners, matching names,
hierarchy, CAD, PIF, PCN, PCM, VPA, semantics, constraints, and observations.
Without explicit BRG/BHD records all BH indexes remain empty. No existing fact
is interpreted as behavior.

Architecture tests must prove:

- `system_identity` imports no backend package;
- `model_kernel` imports no model-state, temporal, binding, semantic,
  constraint-evaluation, source-interpretation, data-source, structural, CAD,
  PDF, or behavior-evaluation module;
- Slice A creates no query method, evaluator package, store, path, database,
  cache, write projection, or fixture;
- no port/VPA dependency appears in a BH contract or validation key;
- no query/evaluator result name leaks through either package `__all__`.

## 9. Gate 7 — historical and byte preservation

For every explicit 9-, 10-, 11-, 14-, 16-, 18-, 28-, and 29-record membership:

1. replay the explicitly named tuple, never an enumerated directory subset;
2. assert its accepted revision ID and membership order are unchanged;
3. assert every BH mapping is present, empty, and immutable;
4. assert all existing query, model-state, semantic, constraint, PT, and VP
   behavior remains unchanged;
5. compare each member's committed bytes and SHA-256 with the Gate 0 capture.

For the current demo assert:

```text
record count: 29
brg_ count: 0
bhd_ count: 0
bhw_ count: 0
revision: mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

Also recheck the exact VP and PT artifact hashes. Slice A must not alter
bindings, interpretations, temporal/source evidence, structural showcase data,
or `.claude/settings.local.json`.

## 10. Gate 8 — independent adversarial review

After focused tests are green, obtain independent reviews from the repository's
software architect, backend engineer, software test engineer, and code
reviewer. Give every reviewer the accepted specification and this Slice A
boundary.

Require independent assessment of:

- canonical identity and exact public contracts;
- evidence and owner/participant closure;
- correction roots, context separation, ancestry, tips, and withdrawals;
- identical-body corroboration versus same-root and cross-root conflict;
- historical replay and immutable indexes;
- nested forgery and atomic-append defenses;
- import isolation and absence of Slice B-D work;
- test coverage and byte preservation.

Reviewers must add concrete reproductions for suspected defects and must not
broaden Slice A. Fix real implementation defects red-first. If a proposed fix
would alter the accepted design, write a bounded discrepancy report and stop
for owner direction.

## 11. Gate 9 — verification matrix

Run and record exact command outcomes and counts for:

1. focused BH identity and record-contract tests;
2. focused BH canonical, store, lifecycle, withdrawal, replay, and forgery
   tests;
3. all `tests/model_kernel/` tests;
4. all identity-binding tests affected by the public anchor surface;
5. VP, PT, CN, ES, VS, VM, and explicit historical replay regressions;
6. architecture and import-isolation tests;
7. the complete repository suite;
8. a fresh base-only clean checkout at final Slice A HEAD;
9. a fresh all-extras clean checkout at final Slice A HEAD;
10. focused OCP/STEP tests;
11. focused PDF tests;
12. the real loopback test separately if its sandbox gate requires permission;
13. backend compilation;
14. `git diff --check` and `git diff --cached --check` as applicable;
15. branch topology, remote status, and clean working-tree checks.

The clean-checkout columns must install only their documented dependency sets
and run from checked-out committed content. Temporary ledgers and caches remain
outside the repository and are removed or reported without destructive broad
commands.

## 12. Reviewable commit sequence

Preferred sequence after the accepted documentation commit:

1. `docs: add BH-001 Slice A architecture and plan`
2. `test: add BH-001 identity and record contract reds`
3. `feat: add behavior identity and record contracts`
4. `test: add BH-001 store and lifecycle reds`
5. `feat: validate behavior declaration lifecycle`
6. `test: harden BH-001 replay and forgery boundaries`
7. `fix: repair BH-001 adversarial findings` only when concrete defects exist
8. `docs: record BH-001 Slice A verification`

Tests and the smallest production change may share a reviewable green commit
when necessary, but the file-first completion report must preserve the exact
red command, failure count/reason, matching fix, and green command.

Do not amend, rebase, reset, cherry-pick, merge, push, or rewrite history.

## 13. File-first completion report

Write the substantial report to:

```text
docs/superpowers/reports/2026-08-29-bh001-slice-a-completion-report.md
```

It must include:

- branch, accepted base, accepted documentation commit, final HEAD, and commit
  list;
- changed-file inventory;
- exact public identity, record, builder, export, and immutable-index contracts;
- red-before/fixed-after evidence;
- canonical golden bytes/IDs and deterministic-order evidence;
- registration closure, cross-owner admission, lifecycle, withdrawal,
  corroboration-material, and replay demonstrations;
- adversarial findings, reproductions, and repairs;
- exact focused, affected, full-suite, clean-checkout, OCP/STEP, PDF, loopback,
  compilation, and diff-check outcomes;
- all historical revisions, existing record bytes, ledger counts, and artifact
  hashes preserved;
- confirmation that the demo remains 29 records with zero BH records;
- confirmation that Slices B-D remain unstarted;
- working-tree, branch-topology, and remote status;
- known limitations and genuine unresolved owner questions.

End the report with:

```text
BH-001 Slice A implemented, adversarially reviewed, and owner accepted.
```

The terminal response is only the concise delivery receipt required by
`CLAUDE.md`; the report file is authoritative.

## 14. Stop condition

Stop after Slice A is implemented, committed in reviewable groups,
independently reviewed, fully verified, and documented. Do not begin any
kernel query, evaluator, numeric comparison, state composition, committed
behavior fixture, or 29-to-32 ledger evolution without the next explicit owner
gate.

END OF BH-001 SLICE A IMPLEMENTATION PLAN
