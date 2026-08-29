# BH-001 Slice B backend implementation review

Date: 2026-08-29
Branch: `bh001`
Accepted Slice A boundary: `c39c674`
Reviewed Slice B HEAD: `ec50f70`
Verdict: green for backend implementation integrity

## 1. Review authority and boundary

This review evaluates BH-001 Slice B against the owner-accepted corrected
design, especially Sections 17, 19 through 24, and 26.2; the Slice B
implementation plan; and the Slice B adversarial acceptance matrix.

The reviewed production scope is exactly:

```text
backend/model_kernel/behavior_results.py
backend/model_kernel/queries.py
backend/model_kernel/__init__.py
```

Slice B adds read-only kernel query contracts and derivation only. It does not
change Slice A identity or record contracts, canonicalization, the effective
body definition, store admission, indexes, model ledgers, explicit historical
memberships, fixtures, state composition, temporal selection, or numeric
evaluation.

This backend review made no production-code, test, fixture, ledger, or
existing-documentation change. Only this report was added.

## 2. Exact public contracts

The implementation exposes exactly the four accepted methods on
`ModelQueries`:

```text
behavior(behavior_anchor_id)
behavior_declaration(behavior_anchor_id, *, context)
behaviors_involving_variable(variable_anchor_id, *, context)
behavior_assertion(record_id)
```

Both context-bearing methods keep `context` keyword-only. There is no alias,
port query, evaluator method, overload, or alternate name.

The six new literal aliases preserve their specified order:

```text
BehaviorLookupStatus
BehaviorDeclarationConclusion
BehaviorRuleLineageSummary
BehaviorAgreementFinding
VariableBehaviorsStatus
BehaviorAssertionLookupStatus
```

The seven result contracts preserve their exact ordered field sets:

```text
BehaviorEffectiveBodyGroupResult
BehaviorRuleRootResult
BehaviorLookupResult
BehaviorRuleResult
VariableBehaviorEntry
VariableBehaviorsResult
BehaviorAssertionDisclosureResult
```

The implementation reuses the accepted `AssertionActivity`,
`ContainingLineageHealth`, and `ModelQueryMaterial` contracts. All record and
row indices use `StrictInt` with a nonnegative bound, including tuple members;
booleans, strings, and floats are not accepted as indices.

The kernel package exports exactly the six aliases and seven result names in
addition to the accepted Slice A surface. Private payload helpers and the
effective-body byte helper do not leak through `backend.model_kernel.__all__`.

## 3. Shared authoritative derivation

The implementation correctly centralizes behavior truth in four private pure
payload functions:

```text
_behavior_lookup_payload
_behavior_rule_payload
_variable_behaviors_payload
_behavior_assertion_payload
```

The query facade and the public result validators call the same helpers. This
avoids two independently evolving implementations of registration lookup,
lineage, effective-body grouping, findings, conclusions, assertion activity,
indices, or ordering. Validators do not recursively instantiate or rerun the
public query methods.

The helpers receive only carried `ModelQueryMaterial`, an already validated
in-memory `LoadedModel`, normalized identifiers/context, and an optional
precomputed record-index map. They perform no I/O and mutate no loaded model.

## 4. Root and effective-body reconstruction

For one exact `(behavior_anchor_id, AssertionContext)` key, derivation:

1. starts only from `behavior_rule_ids_by_key`;
2. resolves roots through `behavior_rule_root_by_id`;
3. groups exact-key declaration IDs by root in one pass;
4. orders roots, complete lineage members, current tips, and withdrawals by
   record ID;
5. derives root health strictly from current-tip count;
6. projects every active tip through the accepted private
   `_behavior_effective_body_bytes()` helper;
7. groups by exact canonical projected bytes;
8. orders groups by those bytes;
9. chooses the minimum current-tip record ID only as the deterministic
   disclosed representative;
10. links every root to the global group indices containing its active tips.

No timestamp, authority, evidence, note, filename, append order, or record ID
selects an engineering winner. Record IDs are used only for deterministic row
and representative disclosure after effective-body equality is established.

Inactive roots remain present with empty tip and group-index tuples. Every
active tip remains disclosed even when its root is conflicted. A same-root
fork may therefore map to one or several body groups without losing the
same-root conflict.

## 5. Lifecycle, corroboration, and findings

The aggregate implementation matches the accepted independent dimensions:

| Membership condition | Conclusion | Lineage summary |
|---|---|---|
| behavior unregistered | `not_registered` | `not_applicable` |
| BRG present, no exact-context root | `not_declared` | `not_applicable` |
| roots present, no active tips | `inactive` | `inactive` |
| any active same-root fork | `conflicted` | `conflicted` |
| healthy roots, one effective body | `declared` | `healthy` |
| healthy roots, multiple effective bodies | `conflicted` | `conflicted` |

Agreement findings occur in the public literal order and remain independent:

- `one_healthy_root` when exactly one active root is healthy;
- `corroborating_healthy_roots` when a body group contains at least two
  distinct healthy roots;
- `same_root_conflict` when any root has multiple current tips;
- `cross_root_effective_body_disagreement` when healthy roots span more than
  one effective body;
- `inactive_roots_present` when any root has no current tip.

Only healthy roots vote for cross-root corroboration or disagreement. A lone
same-root fork with different tip bodies does not fabricate a cross-root
finding. Mixed cases correctly retain several findings, including partial
corroboration plus disagreement and healthy plus conflicted plus inactive
roots.

Selective fork-tip withdrawal can restore one healthy current tip. Full and
partial convergence preserve complete lineage while deriving current tips
membership-relatively. Explicit replay without a later successor or
withdrawal revives the earlier member.

## 6. Query-specific semantics

### 6.1 Permanent registration lookup

`behavior()` returns structured absence for a valid unregistered `bhv_` and
discloses the exact BRG, both aligned participant VRGs, and both aligned owner
entity registrations when registered. A same-owner pair may repeat an owner
index while the owner record remains carried once. Cross-owner registrations
retain two distinct aligned owner indices.

### 6.2 Exact-context declaration lookup

`behavior_declaration()` normalizes and queries only the requested exact
context. Registration absence, declaration absence, inactivity,
same-root conflict, cross-root disagreement, one healthy root, and independent
corroboration are structured results. Contexts do not leak into or vote in one
another.

### 6.3 Reverse variable discovery

`behaviors_involving_variable()` begins only from the accepted permanent BRG
reverse index. It returns every registered behavior containing the variable
in behavior-anchor order, including exact-context `not_declared` and inactive
entries. It does not infer behavior from common ownership, names, hierarchy,
ports, VPA, topology, semantics, compatibility, constraints, or observations.

Each entry discloses the other variable and its exact registration/owner
indices without assigning an operand, input, output, source, result, role, or
direction. Entry indices are contiguous from zero. Each entry's lifecycle,
roots, groups, findings, and current declarations are byte-equivalent to the
direct exact-context behavior query.

### 6.4 Individual assertion disclosure

`behavior_assertion()` validates `brg_`, `bhd_`, or `bhw_` shape before
membership access. Valid-shaped absence is `not_found`.

A found BRG and BHW are events with a record index but no declaration
lifecycle or root fields. A found BHD discloses direct successors,
withdrawals, activity, containing-root health, and aggregate exact-subject
conclusion/findings separately. Consequently a current BHD can be in a
healthy root while another independent root makes the subject conflicted, or
a withdrawn BHD can be in an inactive root while another root leaves the
aggregate subject declared.

## 7. Authoritative Pydantic reconstruction

Every new public result is frozen, extra-forbidden, and configured with
`revalidate_instances="always"`.

Before derived checks:

- carried `ModelQueryMaterial` is serialized and reconstructed;
- assertion context is serialized and reconstructed through the accepted
  discriminated union;
- roots, effective-body groups, and reverse entries are each serialized and
  reconstructed as their exact contracts;
- malformed noncollection row payloads raise a typed Pydantic validation
  failure rather than leaking `TypeError`;
- generic duck-typed `model_dump` callbacks are not invoked—only actual
  Pydantic `BaseModel` instances are dumped.

The outer validator then rebuilds the loaded model entirely in memory, invokes
the shared pure derivation, and compares every supplied content-derived field
with the authoritative payload. Only after that comparison are private
material references bound for read-only convenience properties.

The hardened tests reject:

- outer and nested `model_construct` forgeries;
- outer and nested `model_copy` mutations;
- stale record IDs;
- reordered, missing, duplicated, extra, or substituted material;
- revision/count substitution;
- behavior, variable, context, or assertion substitution;
- forged root, lineage, tip, withdrawal, body group, representative,
  finding, conclusion, summary, activity, or index;
- wrong union-arm indices;
- malformed nested collections;
- boolean and coercible indices;
- implication-bearing extra fields.

Result validation uses no filesystem or store object. Its only model rebuild
is the accepted store-independent in-memory collection validator reached via
`ModelQueryMaterial`.

## 8. Efficiency and denial-of-service posture

The initial review identified an avoidable repeated global lineage scan. The
final implementation repairs it by grouping the exact-key declaration IDs by
root in one pass. Reverse discovery computes the record-index map once and
passes it into each per-behavior rule derivation. Effective-body bytes are
computed once per active tip for that derivation.

Work remains bounded by the explicitly selected membership, exact behavior
key, number of registered behaviors involving the requested variable, and
their active tips. The implementation adds no recursive behavior traversal,
expression evaluation, candidate cross-product, external model execution,
dynamic import, or persisted projection.

## 9. Import and isolation boundary

AST and source review confirms:

- no import of model state, temporal state, identity binding, semantic
  compatibility, constraint evaluation, source interpretation, data sources,
  or behavior evaluation;
- no `ModelStore` import or construction;
- no filesystem path, `open`, SQLite, cache, repository, or database;
- no write operation;
- no upward dependency from lower layers;
- no `backend/behavior_evaluation` package or Slice C result;
- no Slice D fixture or record.

`queries.py` mentions `ModelStore` only in the pre-existing user-facing
description of the accepted `LoadedModel` injection boundary; it neither
imports nor constructs one.

## 10. Determinism and preservation

The final adversarial tests demonstrate identical serialized output for all
four methods under:

- forward and reversed validated record mappings;
- Python hash seeds `1`, `17`, and `31337`;
- repeated material reconstruction.

All material records are carried exactly once, in exact revision order. Rows
contain indices rather than duplicated records, evidence, or authority.

The production diff does not touch:

```text
backend/model_kernel/contracts.py
backend/model_kernel/canonical.py
backend/model_kernel/store.py
models/
bindings/
interpretations/
backend/model_state/
backend/temporal_state/
```

The existing explicit 9/10/11/14/16/18/28/29 memberships remain selected by
their accepted constants. Pre-BH histories return structured behavior absence
without migration or enumeration. Slice B appends no BRG, BHD, BHW, fixture,
binding, or temporal evidence.

## 11. Review reproductions and test evidence

### 11.1 Focused Slice B

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result:

```text
43 passed in 11.48s
```

### 11.2 Complete BH Slice A+B

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result:

```text
153 passed in 32.34s
```

### 11.3 Complete model-kernel suite

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/model_kernel/ -q
```

Result:

```text
1095 passed in 85.96s
```

### 11.4 Static checks

```text
git diff --check c39c674..ec50f70
```

Result: passed with no output.

The reviewed commit set changes only the planned Slice B query/result code,
tests, plans, matrix, and additive public exports. The working tree was clean
before this report was added.

## 12. Findings and verdict

The preimplementation and first implementation passes found three concrete
risks:

1. a stale documented Slice B base;
2. raw `TypeError` leakage from malformed nested collection payloads;
3. avoidable repeated global lineage/index derivation and incomplete
   determinism/coercion coverage.

All three were repaired without broadening Slice B:

- the plan now records `c39c674` as the accepted Slice A boundary;
- nested rows fail through typed Pydantic validation;
- exact-key lineage and shared indices avoid the repeated scan;
- tests now cover strict coercion, implication-bearing extras, convergence,
  selective withdrawal, replay revival, mixed findings, reversed mappings,
  and multiple hash seeds.

No remaining backend defect was reproduced at `ec50f70`. The implementation
is ready for the independent final code-integrity review and the complete
Slice B verification matrix. This verdict does not authorize Slice C or Slice
D.

END OF BH-001 SLICE B BACKEND REVIEW
