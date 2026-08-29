# BH-001 Slice B independent test and adversarial review

Date: 2026-08-29
Branch: `bh001`
Reviewed HEAD: `ec50f7040f1a6fc703acfbe2cb599604ce431f76`
Accepted Slice A boundary: `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`
Review role: software test engineer
Scope: BH-001 Slice B read-only kernel queries only

## 1. Outcome

The postimplementation Slice B surface is consistent with the corrected,
owner-accepted BH-001 design and the B01-B60 adversarial matrix. Independent
focused execution found no failing production contract:

- the focused Slice B query suite reports `43 passed`;
- the complete BH Slice A+B focused regression surface reports `153 passed`;
- the explicit preservation boundary reports `6 passed`;
- nine additional mixed-material, row, index, context, and subject attacks
  were independently rejected;
- canonical effective-body group ordering, outer reconstruction of private
  convenience bindings, and rejection of an arbitrary duck-typed
  `model_dump` carrier were independently reproduced.

No blocking production or test defect remains. One narrow defense-in-depth
test opportunity remains: commit `ec50f70` correctly prevents arbitrary
non-Pydantic objects from having their `model_dump()` method invoked at the
public boundary, but no retained test attacks that exact duck-typed carrier.
The external reproduction in Section 7 proves the current behavior. This is
not an uncovered B01-B60 acceptance failure.

Slices C and D remain outside this review. No evaluator or demonstration
fixture exists.

## 2. Authority and reviewed material

The review compared current code and tests with:

- the corrected final BH-001 specification, especially Sections 17, 19, 22,
  24, and 26.2;
- the Slice B implementation plan;
- every row B01-B60 of the Slice B adversarial acceptance matrix;
- the owner-accepted Slice A records, canonical body projection, lifecycle,
  immutable indexes, and historical replay boundary;
- `backend/model_kernel/behavior_results.py`;
- the four BH methods in `backend/model_kernel/queries.py`;
- exact package exports in `backend/model_kernel/__init__.py`;
- all focused behavior identity, record, store, canonical, query, and hostile
  revalidation tests;
- existing demo revision, model-byte, PT-artifact, and VP-artifact tests.

The implementation diff from the accepted Slice A administrative boundary
changes production only in:

```text
backend/model_kernel/__init__.py
backend/model_kernel/behavior_results.py
backend/model_kernel/queries.py
```

There is no production diff to record contracts, the canonical projection,
store validation, immutable indexes, ledgers, fixtures, or artifacts.

## 3. Focused verification

### 3.1 Exact Slice B query suite

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result:

```text
43 passed in 12.14s
```

### 3.2 Complete BH Slice A+B focused regression

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result:

```text
153 passed in 26.21s
```

### 3.3 Historical, ledger, and artifact preservation

The targeted command selected:

- the committed-ledger golden revision and explicit membership test;
- all explicit pre-BH replay and empty-index tests;
- all current-demo record-byte freeze checks;
- PT and VP artifact byte/hash checks;
- the Slice B no-evaluator/no-fixture boundary;
- structured BH absence over every explicit historical membership.

Result:

```text
6 passed in 13.33s
```

This independently preserves the 9-, 10-, 11-, 14-, 16-, 18-, 28-, and
29-record histories; the 29-record current revision; zero committed BRG, BHD,
and BHW records; and the accepted PT and VP artifacts.

## 4. B01-B16 — public contract, lookup, and reverse discovery

Status: green.

The tests pin:

- exactly four public method names and signatures, with keyword-only context;
- exactly six new literal aliases in accepted order;
- exactly seven result contracts with ordered fields;
- reuse of `AssertionActivity` and `ContainingLineageHealth`;
- exact unique package export count `144` and no alias, port-query, evaluator,
  state, validity, health, or outcome export;
- typed malformed-input rejection before material or index access;
- absent and present behavior registration lookup;
- participant VRG and owner-index alignment;
- repeated same-owner indices while carrying the owner record once;
- distinct cross-owner indices;
- absent variable, registered-empty variable, multiple registered behaviors,
  exact-context `not_declared`, canonical anchor ordering, and contiguous
  entry indices.

The explicit 29-record replay contains the accepted common ownership, model
facts, port topology, VPA, semantics, and observations without a BRG. Its
behavior collection remains empty, demonstrating that those facts infer no
behavior.

## 5. B17-B30b — roots, bodies, conclusions, and findings

Status: green.

Independent inspection and retained tests cover:

- registered-without-root as `not_declared/not_applicable`;
- one healthy root and `one_healthy_root`;
- independent identical bodies as one group and corroboration;
- independent different bodies as cross-root disagreement without a winner;
- identical-body and different-body same-root forks as conflicts;
- partial convergence remaining conflicted and full convergence becoming one
  healthy current tip;
- all-inactive and active-plus-inactive disclosures;
- exact context isolation;
- exclusion of evidence, authority, time, note, ID, and parent history from
  effective-body equality;
- inclusion of changed variable-keyed locks in effective-body difference;
- canonical root, lineage, tip, withdrawal, group, and current-declaration
  ordering;
- conflicted-root tips grouped for disclosure but excluded from healthy-root
  agreement voting;
- A/A/B healthy roots disclosing both corroboration and cross-root body
  disagreement;
- independent coexistence of one-healthy-root, same-root-conflict, and
  inactive-root findings.

An independent two-body reproduction resolved each group representative back
to its authoritative BHD, projected it with the accepted private canonical
helper, and obtained:

```text
body_group_bytes_canonical=True
group_indices=(0, 1)
conclusion=conflicted
```

Record ID determines only deterministic representative and display ordering;
it does not select a declaration winner.

## 6. B31-B39 — assertion lifecycle and historical revival

Status: green.

The assertion tests distinguish:

- a permanent BRG with all lifecycle/root fields `None`;
- a BHW event with all lifecycle/root fields `None`;
- valid-shaped absent BRG, BHD, and BHW IDs with canonical null/empty fields;
- current, directly superseded, and withdrawn BHDs;
- direct successor and withdrawal indices;
- containing-root health from aggregate subject conclusion/findings;
- a healthy current root inside a cross-root-conflicted subject;
- an inactive withdrawn root inside an otherwise declared subject;
- selective fork-tip withdrawal restoring one healthy active tip.

Explicit synthetic replay omitting a later successor revives its predecessor
as `current`. Explicit replay omitting a later withdrawal revives its target
as `current`. Adding those records changes activity to `superseded` or
`withdrawn` membership-relatively. No authority, timestamp, filename, append
order, or temporal cutoff reconstructs history.

## 7. B40-B52 — authoritative reconstruction attacks

Status: green.

Retained hostile tests reject:

- outer and nested `model_construct` and `model_copy` mutations;
- stale content-derived IDs;
- missing, reordered, or inconsistent material and revisions;
- substituted behaviors, variables, contexts, and record identities;
- wrong or out-of-range record indices;
- forged root lineage, tips, withdrawals, group links, representatives,
  group members, root members, findings, health, conclusion, and activity;
- missing, duplicate, reordered, or noncontiguous reverse entries;
- boolean, string, and float coercions at every scalar and tuple index path;
- malformed nested collections and implication-bearing extra fields;
- store/filesystem access during result reconstruction.

### 7.1 Independent nine-attack reproduction

A result containing two independent different-body roots was serialized and
attacked outside the retained tests with:

1. a duplicate root;
2. a missing effective-body group;
3. a duplicate current-declaration index;
4. a root index redirected to the BRG union arm;
5. a valid-shaped behavior-anchor substitution;
6. a valid alternate-context substitution;
7. a missing material record;
8. a complete valid material from another selected membership;
9. mutated BHD content retaining its stale record ID.

Result:

```text
external_attacks_rejected=9/9
```

### 7.2 Nested construct and convenience binding reproduction

A `ModelQueryMaterial.model_construct()` carrying a copied revision with a
forged record count was inserted through an outer `model_copy()`. Full public
validation rejected it.

Canonical reconstruction also rebound private material for read-only index
conveniences:

```text
root_property_bound=True
group_property_bound=True
reverse_nested_property_bound=True
nested_material_construct_rejected=True
```

### 7.3 Duck-typed carrier hardening

Commit `ec50f70` changed the nested dump boundary to invoke `model_dump()` only
on actual Pydantic `BaseModel` instances. An arbitrary object whose method
would return an otherwise valid material payload was supplied externally.

Result:

```text
duck_typed_material_rejected=True
duck_model_dump_called=False
```

This prevents validation from invoking attacker-defined methods merely because
they share the `model_dump` name.

Complete records and evidence occur once in `ModelQueryMaterial`; nested roots,
groups, and entries serialize indices only. Repeated serialization, reversed
input maps, and subprocess runs under hash seeds `1`, `17`, and `31337` are
byte-identical.

## 8. B53-B60 — replay, preservation, and architecture

Status: green within the focused review boundary.

- All explicit 9/10/11/14/16/18/28/29 memberships replay without migration
  or inferred BH records.
- The current demo remains exactly 29 records at its accepted revision, with
  zero BRG, BHD, or BHW records.
- Existing model bytes and PT/VP artifacts remain frozen under accepted hash
  tests.
- `ModelQueries` owns one injected `LoadedModel`, not a store, path, cache,
  database, or projection.
- Result validation calls only the accepted in-memory collection validator;
  patched `ModelStore` and filesystem operations are not touched.
- AST checks reject upper-layer, evaluator, temporal, binding, semantic,
  constraint-evaluation, source, and data-source imports.
- BH methods derive only from Slice A behavior indexes. They do not traverse
  hierarchy, topology, VPA, state, or observation graphs.
- The diff contains no production store, index, canonical, record-contract,
  ledger, or fixture change.
- `backend/behavior_evaluation` and every Slice D record remain absent.

`git diff --check` passed before this report was added.

## 9. Finding BHT-B-01 — retain the duck-carrier hardening reproduction

Severity: low, defense in depth.
Production defect: none at reviewed HEAD.
Acceptance blocker: no.

The final hardening commit deliberately replaced a generic `hasattr(value,
"model_dump")` dispatch with an `isinstance(value, BaseModel)` boundary. The
current implementation rejects the hostile carrier without invoking its
method, as independently reproduced in Section 7.3.

The retained `model_construct` and `model_copy` cases protect all explicitly
required Pydantic-instance attacks, so B40 and B41 are green. A future focused
test should retain the exact non-Pydantic duck carrier as a regression for the
additional hardening guarantee. This recommendation does not broaden Slice B
or require production repair.

## 10. Final verdict

BH-001 Slice B implements the exact read-only kernel query surface, discloses
registration, lifecycle, roots, effective-body agreement, corroboration, and
conflict without inference or winner selection, and reconstructs every outer
result authoritatively from carry-once material.

Every B01-B60 row has supporting retained or existing regression evidence.
The independent external attacks found no remaining false disclosure or
validation bypass. The only review recommendation is the non-blocking retained
test strengthening in Section 9.

No production, test, fixture, ledger, artifact, or existing documentation file
was modified by this review. Only this report was added. Slices C and D remain
unstarted.

END OF BH-001 SLICE B TEST REVIEW
