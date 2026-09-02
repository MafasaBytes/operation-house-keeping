# ST-002 Slice B Completion Report

Date: 2026-09-02
Status: implementation complete; awaiting Slice B owner validation
Milestone: ST-002 — Explicit State Transition Identity and Declaration
Authorized slice: Slice B only

## 1. Outcome

ST-002 Slice B is complete at:

`9c2f3a8499dea3c1b98ec51e528ab748b95463d1`

The slice adds exactly four read-only transition query methods and their exact
public result contracts:

1. `transition()`
2. `transition_declaration()`
3. `transitions_of_entity()`
4. `transition_assertion()`

The implementation discloses registered transition identity, exact-context
transition-declaration lifecycle, effective-body agreement, endpoint pin
alignment, exact-subject transition collections, and transition assertion
activity. It does not assess, infer, detect, select, execute, or assert a
transition occurrence.

No transition assessment or occurrence package, result, method, record, or
fixture was added. The authoritative demo ledger remains the accepted
34-record ST-001 revision and contains zero TRG, TRD, or TRW records.

## 2. Accepted inputs and gates

The implementation used these accepted inputs exactly:

- accepted Slice A implementation:
  `012eecec26573904aa030975a2303122ed39fc78`;
- accepted Slice A completion-report SHA-256:
  `21a336252eb7437ec8104604cacca8e0b48c698da0726ef3af4c5017682aeb69`;
- corrected final ST-002 design SHA-256:
  `fd66bcb47a627c88875bcc26586844141e86e4ab227ad08d248549313fb7f9d4`;
- untouched authoritative revision:
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`.

The working tree was clean before the administrative acceptance work began.
No pre-existing user change was overwritten or absorbed into Slice B.

## 3. Slice A administrative acceptance commit

The required documentation-only acceptance commit is:

`7d22242fb5eb7a579c3dff667b353e0e1be3c8ef`

Parent:

`012eecec26573904aa030975a2303122ed39fc78`

Subject:

`docs: record ST-002 Slice A acceptance`

It adds only:

- the previously owner-gated Slice A completion report; and
- `docs/superpowers/reports/2026-09-02-st002-slice-a-owner-acceptance.md`.

The committed Slice A completion report retains its accepted SHA-256 exactly.
The acceptance commit changes no runtime contract, canonical vector, model
record, index, test behavior, ledger membership, or accepted artifact.

## 4. Slice B implementation commit

The local implementation commit is:

`9c2f3a8499dea3c1b98ec51e528ab748b95463d1`

Parent:

`7d22242fb5eb7a579c3dff667b353e0e1be3c8ef`

Subject:

`feat: add ST-002 transition declaration queries`

It contains 19 files, 2,799 insertions, and 37 deletions. Its production
surface is limited to:

- `backend/model_kernel/transition_results.py`;
- the four methods and typed input boundaries in
  `backend/model_kernel/queries.py`;
- exact public exports in `backend/model_kernel/__init__.py`; and
- status and non-inference documentation in
  `backend/model_kernel/README.md`.

All other changes are tests or exact pre-existing export-count assertions.
No file under `models/`, `bindings/`, `interpretations/`, temporal/source
fixture roots, structural fixture roots, or accepted-artifact locations is in
the implementation commit.

## 5. Exact public contracts

### 5.1 Method surface

The public method signatures are exactly:

```python
transition(transition_anchor_id) -> TransitionLookupResult

transition_declaration(
    transition_anchor_id,
    *,
    context,
) -> TransitionDeclarationResult

transitions_of_entity(
    entity_anchor_id,
    *,
    context,
) -> EntityTransitionsResult

transition_assertion(record_id) -> TransitionAssertionDisclosureResult
```

The context arguments are mandatory keyword-only arguments. Typed validation
of the transition anchor, entity anchor, context, and transition record ID
occurs before model material is accessed.

There is no alias or public method for current transition, detection,
assessment, enabled transitions, possible transitions, next-state selection,
traversal, path finding, or transition history.

### 5.2 Result and literal surface

Slice B exports the exact eight result contracts:

- `TransitionEndpointResult`;
- `TransitionEffectiveBodyGroupResult`;
- `TransitionDeclarationRootResult`;
- `TransitionLookupResult`;
- `TransitionDeclarationResult`;
- `EntityTransitionEntry`;
- `EntityTransitionsResult`; and
- `TransitionAssertionDisclosureResult`.

It exports the exact eight associated literal contracts:

- `TransitionLookupStatus`;
- `TransitionDeclarationConclusion`;
- `TransitionDeclarationLineageSummary`;
- `TransitionAgreementFinding`;
- `TransitionEndpointRole`;
- `TransitionEndpointPinAlignment`;
- `EntityTransitionsStatus`; and
- `TransitionAssertionLookupStatus`.

Field order, literal order, return annotations, exports, and the total unique
kernel export count of 182 are pinned executable contracts.

Every public outer result carries one complete `ModelQueryMaterial` exactly
once. Nested root, group, endpoint, and entity-entry rows carry strict,
non-boolean indices only. Convenience properties receive private access to the
one outer material snapshot only after complete authoritative equality has
succeeded.

## 6. Lifecycle and deterministic disclosure

`transition()` reports permanent registration only. A registered transition
remains `registered` with no declaration, conflict, or wholly inactive roots.

`transition_declaration()` derives the exact-context conclusion:

| Structural state | Conclusion | Summary |
|---|---|---|
| no TRG | `not_registered` | `not_applicable` |
| TRG, no exact-context roots | `not_declared` | `not_applicable` |
| one or more active roots, one effective body, no fork | `declared` | `healthy` |
| same-root fork or healthy-body disagreement | `conflicted` | `conflicted` |
| roots exist but no active tip remains | `inactive` | `inactive` |

Agreement findings are derived independently and emitted only in this order:

1. `one_healthy_root`;
2. `corroborating_healthy_roots`;
3. `same_root_conflict`;
4. `cross_root_effective_body_disagreement`;
5. `inactive_roots_present`.

Independent roots with byte-identical effective bodies corroborate one
transition meaning. Different active bodies conflict. A same-root fork is
conflicted even when its bodies are equal. A legal same-root two-parent merge
resolves a fork structurally. Withdrawals deactivate only their exact current
tips and do not delete history.

`transition_assertion()` uses successors-first defensive activity precedence:

1. any successor means `superseded`;
2. otherwise an exact withdrawal means `withdrawn`;
3. otherwise the TRD is `current`.

Full-set admission rejects successor-plus-withdrawal, while result derivation
retains the accepted defensive precedence. Found TRGs and TRWs have null
declaration-lifecycle fields. Found TRDs disclose exact activity, containing
root health, containing transition/context conclusion and findings, root,
successors, and withdrawals.

All roots, tips, groups, records, findings, entity entries, successors, and
withdrawals have explicit deterministic order. A dedicated inverse
time-versus-ID fixture proves `recorded_at` does not select a representative or
winner. A five-root, two-body-group world with corroboration, divergence, a
fork, inactivity, and withdrawal produces byte-identical disclosures under
two different legal append orders and under three hash seeds.

## 7. Endpoint state derivation and RC2

Endpoint state conclusion and pinned-STD activity are not reimplemented in the
transition layer. `transition_results.py` calls the accepted shared kernel ST
payload derivations for both endpoint roles:

- `_state_declaration_payload()` for the exact state/context conclusion; and
- `_state_assertion_payload()` for the exact pinned STD activity.

The public transition endpoint result is required to equal the corresponding
public `state_declaration()` and `state_assertion()` disclosures on identical
material.

Executable parity covers both `from` and `to` roles for every reachable cell:

| State conclusion | Pin activity | Alignment |
|---|---|---|
| `declared` | `current` | `exact_current` |
| `declared` | `superseded` | `pinned_declaration_superseded` |
| `declared` | `withdrawn` | `pinned_declaration_withdrawn` |
| `conflicted` | `current` | `endpoint_state_conflicted` |
| `conflicted` | `superseded` | `endpoint_state_conflicted` |
| `conflicted` | `withdrawn` | `endpoint_state_conflicted` |
| `inactive` | `superseded` | `endpoint_state_inactive` |
| `inactive` | `withdrawn` | `endpoint_state_inactive` |

Structural rejection covers all three `not_registered` activity combinations,
all three `not_declared` activity combinations, and `inactive/current`.
Runtime spies and AST checks require the shared ST helpers and forbid parallel
ST index/lifecycle derivation. Endpoint alignment remains orthogonal to the
transition-declaration lifecycle conclusion; an admitted stale or withdrawn
pin does not retarget automatically.

## 8. Authoritative outer-result reconstruction

Every public transition result rebuilds authority solely from its carried
material. Validation:

1. inspects the caller-owned object graph before normalization;
2. rejects hidden Pydantic extras and all undeclared private/cache fields;
3. bounds graph depth and node count and rejects cycles iteratively;
4. reconstructs the revision, records, contexts, and nested rows from plain
   serialized field content;
5. verifies strict record count, unique lexicographic membership, canonical
   record identities, full-set admission, and recomputed revision equality;
6. derives every expected field from the rebuilt `LoadedModel`;
7. compares the complete outer payload and all ordering exactly; and
8. binds nested rows to the single outer material only after equality.

The result module owns no `ModelStore` and performs no filesystem, network,
environment, clock, cache, or write access. It imports the same-layer accepted
ST derivation only and does not import state classification or another upper
layer.

Hostile tests reject missing, duplicate, reordered, stale-ID/content,
wrong-count, unique-extra, mixed-revision, foreign, wrong-union-arm, and
record-ID/content-substituted material. They also reject revision
substitution, context substitution, invalid or boolean indices, out-of-range
indices, wrong records, forged roles, anchors, pins, roots, tips, bodies,
groups, findings, conclusions, activity, alignment, precedence, nested rows
from another snapshot, implication-bearing fields, cycles, excessive depth,
and private cache injection at the outer result, nested endpoint, and material
levels.

Plain serialized and instance round trips reconstruct byte-identically from
the complete carried authority.

## 9. RC5 exact authoritative absence

All four query families execute against the untouched authoritative 34-record
ledger.

For `trn_00000000000000000000000000000000`, `transition()` returns:

- `status = not_registered`;
- `registration_index = None`;
- `subject_entity_registration_index = None`;
- `from_state_registration_index = None`; and
- `to_state_registration_index = None`.

For the same anchor and exact `lifecycle_view/as_operated` context,
`transition_declaration()` returns:

- `conclusion = not_registered`;
- `lineage_summary = not_applicable`;
- no findings, registration, roots, groups, or current declarations.

For entity `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` and the same context,
`transitions_of_entity()` returns:

- `status = registered`;
- `entity_registration_index = 14`; and
- empty entries.

For the valid all-zero `trg_`, `trd_`, and `trw_` record IDs,
`transition_assertion()` returns `not_found`, no record index, null activity
and containing fields, and empty successor and withdrawal indices.

Each result carries the exact 34-record revision once. Malformed identifiers
and wrong record families reject typed before material access.

## 10. Temporal and capability boundary

Named executable non-inference tests prove that transition queries reject or
cannot accept:

- classification pairs or changed outcomes;
- cutoffs;
- `change_class`;
- previous occurrence;
- receipt or source order;
- temporal proximity; and
- observation or source selection.

Two simultaneously declared endpoint states do not create a transition
declaration. No public transition result has classification, change-class,
cohort, persistence, continuity, causality, control, safety, diagnosis,
recommendation, confidence, occurrence, or occurred fields.

The implementation therefore discloses declared model meaning only. It does
not claim that a transition is possible now, enabled, executed, detected, or
occurred.

## 11. Red-first development evidence

The first focused contract run was intentionally red: 10 tests failed because
the four methods, result models, literals, fields, and exports did not yet
exist. No production placeholder was added before that failure was observed.

The first implementation pass made those 10 contract rows green. Lifecycle,
RC2, RC5, hostile reconstruction, deterministic ordering, import isolation,
and preservation tests were then added incrementally.

During integrated review, the affected kernel/identity run initially reported
1 documentation failure among 1,727 collected tests because the README had
changed an accepted exact phrase. The phrase was restored without weakening
the added transition documentation.

Adversarial review also found that caller-supplied undeclared private Pydantic
cache fields could be normalized away before a `before` validator inspected
them. A wrap validator now inspects the raw caller-owned instance, permits only
the declared nested `_material` binding, requires exact outer-material
identity when present, and rejects every other private field. Dedicated outer,
nested, and material attacks prove the correction.

The final transition-focused gate reports:

`151 passed in 66.62s`

## 12. Specialist reviews

Codex retained synthesis responsibility and reconciled four independent
specialist roles.

### Architecture and shared-ST review

Result: no blocker.

The review confirmed exact shared ST helper reuse, both endpoint roles across
the complete reachable matrix, full structural unreachability, no parallel ST
derivation, no result-module store dependency, and no scope leak into
assessment or occurrence.

### Backend-contract review

Result: no blocker.

The review confirmed all 16 new public names, 182 unique exports, exact field
and literal order, four method signatures, deterministic lifecycle/grouping,
carry-once material, strict indices, complete authoritative reconstruction,
and no filesystem or `ModelStore` ownership in the result layer. Its broad
transition run reported 132 passed.

### Adversarial review

Initial result: one blocker and one coverage gap.

- undeclared private/cache state survived supplied-instance revalidation; and
- entity entries did not directly exercise `conflicted` and `inactive`.

Both were corrected. Re-review reproduced rejection of outer, nested, and
material private attacks and verified all four entity lifecycle conclusions
against their direct declaration disclosures. Final result: no blocker; 65
focused hostile/query/parity/contract tests passed.

### Test-specialist review

Initial result: four coverage blockers.

- incomplete H02 unique-extra/mixed/wrong-arm material attacks;
- missing public assertion rows for conflicted and inactive containing
  lineages;
- incomplete H07 clock/cache isolation evidence; and
- insufficiently adversarial time/order and complex hash-seed coverage.

The corrections also made T03–T05 and T07 explicit named executable rows.
Re-review ran the seven repaired targets and the complete transition-focused
suite. Final result: no blocker; 7 repaired targets passed and 151 focused
tests passed.

## 13. Verification results

### 13.1 Working column

- final complete repository suite: `3,234 passed in 1,276.18s`;
- earlier complete integration checkpoint: `3,229 passed` before the final
  five test-strengthening rows;
- transition-focused final gate: `151 passed`;
- targeted review corrections: `7 passed`;
- backend no-write compilation: 108 Python files compiled;
- working-tree `git diff --check`: pass;
- full `e44a186..HEAD` milestone-range `git diff --check`: pass.

### 13.2 Fresh base-only clean checkout

Resolved checkout before cleanup:

`/tmp/st002-slice-b-base-clean-BgAigq/checkout`

- exact detached HEAD:
  `9c2f3a8499dea3c1b98ec51e528ab748b95463d1`;
- installed only `requirements.txt` and `requirements-dev.txt`;
- sandboxed suite: 3,198 passed, 35 optional-dependency skips, and one
  localhost-bind setup error;
- the exact loopback test rerun outside the sandbox: 1 passed;
- effective result: 3,199 passed and 35 skipped, with zero test failure;
- working-tree and milestone-range whitespace checks: pass;
- Git status: clean;
- authoritative ledger: 34 records, accepted revision, accepted aggregate,
  zero transition records.

### 13.3 Fresh all-extras clean checkout

Resolved checkout before cleanup:

`/tmp/st002-slice-b-extras-clean-1o4VKV/checkout`

- exact detached HEAD:
  `9c2f3a8499dea3c1b98ec51e528ab748b95463d1`;
- installed base/dev plus the hash-pinned CAD and PDF requirement sets;
- sandboxed suite: 3,233 passed and one localhost-bind setup error;
- the exact loopback test rerun outside the sandbox: 1 passed;
- effective result: 3,234 passed with zero skip or failure;
- focused OCP/STEP and PDF paths therefore executed in the full all-extras
  suite;
- working-tree and milestone-range whitespace checks: pass;
- Git status: clean;
- authoritative ledger: 34 records, accepted revision, accepted aggregate,
  zero transition records.

The sole error in each sandboxed clean column was
`PermissionError: [Errno 1] Operation not permitted` while binding
`127.0.0.1`. Both exact isolated loopback reruns passed once local socket
binding was authorized.

Both disposable checkout roots and their virtual environments were removed
only after their resolved paths, exact HEADs, clean statuses, ledger hashes,
and suite results were recorded. No repository file was removed.

## 14. Historical and artifact preservation

The authoritative model remains:

- record count: 34;
- revision:
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
- 34-record stored-file aggregate:
  `cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd`;
- `trg_` files: 0;
- `trd_` files: 0;
- `trw_` files: 0.

The accepted 32-record predecessor aggregate remains:

`eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58`

Explicit replay produced the accepted revisions for every membership:

| Records | Revision |
|---:|---|
| 9 | `mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d023e3da83227f` |
| 10 | `mrv_105658072294bad92f83e3d536863cb46d6d7ae83f271fb59d5026839d002686` |
| 11 | `mrv_25afc0ebf17ed12bd6ef0a95795798a53ef2731983410136d3da15c4d0f98093` |
| 14 | `mrv_702c840f7da00617feb1be252838105d8b001b2e19978842bdcbec56996c99ff` |
| 16 | `mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a40099e8032ca8135b` |
| 18 | `mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51` |
| 28 | `mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2` |
| 29 | `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652` |
| 32 | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |
| 34 | `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41` |

Every replay returned structured transition absence and empty immutable
transition indexes.

Accepted artifact checks remain:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| PT disclosure | 33,855 | `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8` |
| VP disclosure | 17,824 | `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3` |
| BH disclosure | 122,406 | `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |
| ST candidate manifest | 31,834 | `990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7` |
| ST candidate disclosure | 510,943 | `23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9` |
| ST completion report | 11,028 | `2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3` |

The PT/VP/BH reproductions and hashes are pinned by their existing accepted
tests. The ST files were also hashed directly after the final run.

## 15. Git topology and final status

Final implementation HEAD:

`9c2f3a8499dea3c1b98ec51e528ab748b95463d1`

Local `main` equals that HEAD. `origin/main` remains:

`e44a18641ba6b440adcf9c10cd86d28376886942`

The local branch is four commits ahead of `origin/main`:

1. `612ea10` — accepted ST-002 design;
2. `012eece` — accepted Slice A implementation;
3. `7d22242` — Slice A administrative owner acceptance; and
4. `9c2f3a8` — Slice B implementation.

There is no merge commit in `e44a186..HEAD`. Nothing was pushed, merged,
rebased, reset, cherry-picked, amended, or history-rewritten during Slice B.

Before this report was written, the primary working tree was clean. At the
owner gate, the only expected working-tree entry is this untracked completion
report:

`docs/superpowers/reports/2026-09-02-st002-slice-b-completion-report.md`

The report is intentionally not included in the implementation commit and
remains a filesystem owner-gate artifact.

## 16. Scope confirmation

Slice B did not:

- add `backend.transition_assessment` or any transition occurrence package;
- add assessment, occurrence, detection, history, state-machine execution,
  automatic next-state selection, or graph traversal;
- accept observations, classifications, sources, selectors, or cutoffs;
- add or mint a transition fixture identity;
- add TRG, TRD, TRW, or any other record to the authoritative ledger;
- alter Slice A transition identities, record contracts, canonical vectors,
  lifecycle indexes, or admission behavior;
- change any ST-001 record or state-classification contract;
- begin Slice C or Slice D; or
- push or merge.

Positive transition behavior exists only in disposable test fixtures built
through the accepted Slice A public builders and store contracts.

## 17. Owner gate

Owner question:

Do you accept ST-002 Slice B at
`9c2f3a8499dea3c1b98ec51e528ab748b95463d1`, including the exact four-query
contract, authoritative carry-once reconstruction, RC2 shared-ST parity, RC5
34-record absence behavior, hostile revalidation, deterministic ordering, and
the verification and preservation evidence in this report, while leaving
Slices C and D separately unauthorized?
