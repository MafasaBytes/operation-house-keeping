# BH-001 Slice B Postimplementation Architecture Review

Status: independent software-architecture review of the implemented Slice B
at `ec50f7040f1a6fc703acfbe2cb599604ce431f76`.

Verdict: **accepted from an architecture and import-isolation perspective**.
No blocking, major, or minor architecture finding was reproduced. Slice B is
bounded to the four accepted read-only model-kernel queries and their
carry-once result contracts. It does not change the accepted Slice A identity,
record, canonicalization, store-validation, or index foundation, and it does
not begin Slice C or Slice D.

This review is advisory evidence for the owner gate. It does not declare owner
acceptance and does not authorize implementation of a later slice.

## 1. Review authority and exact inputs

The review used the corrected, accepted design rather than the superseded
initial proposal:

- implementation HEAD:
  `ec50f7040f1a6fc703acfbe2cb599604ce431f76`;
- accepted Slice A implementation boundary:
  `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`;
- Slice A owner-acceptance administrative boundary and Slice B starting HEAD:
  `c39c674a95ad04c68250e23e86b169399a9547dd`;
- authoritative corrected design:
  `docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`,
  SHA-256
  `3d1267ecb01e199479e9b4d0e09b39a72e7156b68b2d098754b54ef863f87fd8`;
- Slice B implementation plan, SHA-256
  `d7698986a24169d1b2184bb59c9cd391c98564a8fb610376404927678e0279d8`;
- Slice B adversarial acceptance matrix, SHA-256
  `40d4d931bd440c3742314dd5a1dfe469e9949afa3c875f061fe76e8be31afe4e`.

The normative design sections inspected for this review were the exact kernel
API and vocabulary, authoritative reconstruction, store/index impact,
dependency direction, historical replay, threat model, adversarial matrix,
and Slice B gate in Sections 17, 19 through 24, and 26.2.

The reviewed production files and their current hashes were:

| File | SHA-256 |
|---|---|
| `backend/model_kernel/behavior_results.py` | `55572417a517b9d69448809e8ecbb9565285b0c53ef39a7a7d8c577c708b675c` |
| `backend/model_kernel/queries.py` | `13001961807026dad31bcf5e17f5ebd2e520893c760f8ddb11857d527508ee10` |
| `backend/model_kernel/__init__.py` | `45988c9a22d876388d363a2d572277447cbc4f2b6515a7e53b414bd028063ad1` |

## 2. Change-boundary audit

The production delta from the Slice B starting boundary is exactly:

- one new kernel-local result module,
  `backend/model_kernel/behavior_results.py`;
- additive query boundary validation and exactly four methods in
  `backend/model_kernel/queries.py`;
- exact new public imports and exports in
  `backend/model_kernel/__init__.py`.

The diff contains no change to:

- `backend/system_identity`;
- `backend/model_kernel/contracts.py`;
- `backend/model_kernel/canonical.py`;
- `backend/model_kernel/store.py`;
- Slice A behavior contracts or IDs;
- model, binding, interpretation, source, structural, or temporal ledgers;
- model-state, temporal-state, identity-binding, semantic-compatibility, or
  observation-compatibility production behavior;
- canonical record serialization, model revision computation, or historical
  membership constants.

No `backend/behavior_evaluation` directory exists. No committed BRG, BHD, or
BHW record exists in the demo ledger. Thus neither evaluator work nor the
Slice D demonstration has started.

## 3. Exact query and public-contract review

The existing `ModelQueries` facade now exposes exactly the accepted methods:

```python
behavior(behavior_anchor_id) -> BehaviorLookupResult
behavior_declaration(behavior_anchor_id, *, context) -> BehaviorRuleResult
behaviors_involving_variable(variable_anchor_id, *, context) \
    -> VariableBehaviorsResult
behavior_assertion(record_id) -> BehaviorAssertionDisclosureResult
```

The context parameters are keyword-only. The boundary validates canonical
`bhv_` anchors and `brg_`/`bhd_`/`bhw_` identities before material or index
access. Malformed and non-BH identities produce the existing typed
`ModelQueryError`; valid-shaped absence is represented in results.

The package adds exactly the six BH-specific literal aliases and seven result
models prescribed by Section 17. It reuses `AssertionActivity` and
`ContainingLineageHealth`. Exact field order, literal order, signatures,
export cardinality, and the absence of aliases, port queries, evaluator types,
or behavioral-outcome vocabulary are pinned by
`test_behavior_query_contracts.py`.

All result indices use `Annotated[StrictInt, Field(ge=0)]`, including optional
outer indices, row indices, material-record indices, and group indices.
Boolean, string, and floating coercions therefore fail before derived-field
comparison.

## 4. Carry-once material and authoritative reconstruction

The implementation reuses the accepted public `ModelQueryMaterial` rather
than moving or duplicating it. Each top-level result carries the selected
model revision and its complete records once. Nested root, group, and reverse
entry rows contain only identifiers, statuses, findings, and strict indices;
they do not duplicate complete records, evidence, authority, or material.

Read-only convenience properties resolve indices through a private material
binding applied only after outer validation. They do not create a second
authoritative representation.

Outer validation performs the required hostile-instance boundary work:

1. serialize a supplied nested Pydantic instance to field content;
2. reconstruct `ModelQueryMaterial`, `AssertionContext`, and each nested row;
3. use the accepted in-memory `ModelQueryMaterial.loaded()` path to rebuild a
   `LoadedModel` and verify content-derived IDs, exact membership, revision,
   ordering, and store admission without constructing or reading a store;
4. recompute the full expected result payload from the rebuilt model;
5. compare all supplied serialized fields to that payload;
6. bind carried material to nested rows only after equality succeeds.

The facade and outer validators share pure private payload-derivation helpers.
This avoids recursive construction of the same public result while still
recomputing from independently reconstructed serialized material. It does not
use `model_construct`, `model_copy`, trusted nested object identity, a file,
or a store.

The adversarial tests reproduce rejection of stale content IDs, revision and
material substitution, missing/reordered/duplicated rows, forged root and
group membership, representatives, tips, withdrawals, health, findings,
conclusions, activities, wrong indices, and nested/outer construct and copy
forgeries.

## 5. Lifecycle and effective-body architecture

The derivation starts only from the accepted immutable Slice A indexes:

- `behavior_registrations_by_anchor`;
- `behavior_anchor_ids_by_variable`;
- `behavior_rule_ids_by_key`;
- `behavior_rule_root_by_id`;
- `behavior_rule_superseded_by`;
- `current_behavior_rule_tips_by_root`;
- `behavior_rule_withdrawn_by`.

There is no second graph, persistent effective-body index, winner function,
projection store, or revision.

For an exact `(behavior_anchor_id, AssertionContext)` key, roots are ordered by
root record ID. Each root's complete lineage, current tips, and withdrawals
are independently ordered by record ID. Health is derived solely from current
tip count: zero is inactive, one is healthy, and more than one is conflicted.

The accepted private five-field `_behavior_effective_body_bytes()` projection
is applied to every current tip. Group order is exact projected-byte order.
Within each group, tips and the unique contributing roots are ordered by
record ID. The lowest record ID is used only for the required deterministic
representative field; it never selects an engineering winner.

### 5.1 Corrected disclosure-versus-voting rule

The implementation correctly applies the owner-corrected interpretation:

- **disclosure groups contain every active tip**, including every tip of a
  same-root fork;
- an inactive root has no tips and therefore no effective-body group index;
- a healthy root points to exactly one group;
- a conflicted root points to every distinct group occupied by its current
  tips, including one group when its fork bodies are identical;
- **only healthy roots vote** for independent-root corroboration and
  cross-root effective-body disagreement;
- a conflicted root always contributes `same_root_conflict` and makes the
  aggregate conflicted, regardless of whether its tips have identical bodies;
- inactive roots remain disclosed and contribute
  `inactive_roots_present`, but do not vote.

This separation matters. An identical-body same-root fork is not mislabeled
as corroboration: the group shows both tips while `same_root_conflict`
preserves the unresolved correction lineage. Conversely, independent healthy
A/A/B roots can disclose both corroboration for the A roots and cross-root
disagreement between A and B. The focused tests cover identical and differing
fork bodies, partial/full convergence, corroboration, disagreement, mixed
active/inactive roots, and selective withdrawal.

## 6. Query-specific semantic review

### 6.1 Permanent behavior registration

`behavior()` discloses the permanent BRG, the two variable registrations in
the BRG's canonical unordered pair, and their owner registrations. Repeated
owner indices are allowed when both variables share an owner; the entity
record itself remains carried once. A valid absent behavior has a `None`
registration index and canonical empty participant/owner tuples.

### 6.2 Exact-context declaration

`behavior_declaration()` never unions assertion contexts. It independently
discloses registration absence, registered-but-undeclared state, inactive
roots, same-root conflict, independent-root body disagreement, one healthy
root, or corroborating healthy roots. Timestamps, authority, notes, evidence,
filenames, append order, and whole-record identity do not select a winner or
split an engineering body.

### 6.3 Reverse variable discovery

`behaviors_involving_variable()` starts only from
`behavior_anchor_ids_by_variable`. A registered variable returns every
permanent BRG involving it in behavior-anchor order, including exact-context
`not_declared` and inactive entries; a registered variable with no BRG returns
an empty collection. Entry indices are contiguous. The other variable and its
owner are resolved from the permanent BRG pair. The implementation performs
no name, owner, topology, VPA, port, semantic, constraint, or observation
inference.

Each reverse entry's lifecycle payload is obtained through the same exact
context/root derivation as the direct declaration query. Tests compare roots,
groups, findings, conclusion, summary, and current declarations between the
direct and reverse paths.

### 6.4 Individual record disclosure

`behavior_assertion()` accepts exactly the three BH record prefixes. BRG is
permanent and BHW is an event, so each has `None` lifecycle/root/subject
fields and empty successor/withdrawal tuples. A BHD reports direct successors
and withdrawals, membership-relative activity, containing-root health, and
the aggregate exact-subject conclusion/findings independently. A healthy
containing root can therefore coexist with a conflicted subject, and an
inactive containing root can coexist with another active root that keeps the
subject declared.

## 7. Dependency and isolation review

The effective production dependency is:

```text
backend.system_identity
          ↑
backend.model_kernel.contracts / canonical / immutable LoadedModel
          ↑
backend.model_kernel.behavior_results
          ↑
backend.model_kernel.queries
```

`behavior_results.py` imports the private Slice A canonical projection, the
public model contracts, and the accepted `ModelQueryMaterial` plus lifecycle
aliases. `queries.py` imports the public result classes and private pure
payload helpers. No dependency points upward from the kernel.

AST and text inspection found no import of:

- `backend.model_state`;
- `backend.temporal_state`;
- `backend.identity_binding`;
- `backend.semantic_compatibility`;
- `backend.constraint_evaluation`;
- `backend.source_interpretation`;
- `backend.data_sources`;
- `backend.behavior_evaluation`.

Neither reviewed module imports or constructs `ModelStore`; accesses a path;
opens a file; imports `sqlite3`; owns a cache, projection, repository, or
database; or performs a write. The existing `LoadedModel` type import and the
in-memory `validate_record_collection` used by `ModelQueryMaterial` are the
accepted query-material reconstruction boundary, not runtime store ownership
or filesystem access.

No port or VPA field, query, admission requirement, or inference was added.
The only word `healthy` in the new public vocabulary is the already accepted
declaration-DAG lineage health; it is not an evaluation or machine-health
finding.

## 8. Historical replay and preservation evidence

The focused historical test explicitly replays the existing 9-, 10-, 11-,
14-, 16-, 18-, 28-, and 29-record memberships. It does not enumerate a
directory to reconstruct history. Every pre-BH membership returns:

- behavior lookup `not_registered`;
- exact-context declaration `not_registered` with no roots or body groups;
- valid-shaped BH assertion lookup `not_found`;
- each registered variable's behavior collection as registered-empty.

Synthetic explicit memberships prove membership-relative revival when a
later successor or withdrawal is omitted.

Direct preservation checks at the reviewed HEAD showed:

```text
demo model record files: 29
committed brg_/bhd_/bhw_ files: 0
loaded record count: 29
loaded revision:
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

The focused PT/VP preservation suite also regenerated and checked the
accepted artifact hashes through its existing deterministic tests. The
accepted 29-record model boundary and prior artifacts remain unchanged.

## 9. Reproductions and exact results

All successful commands below were run from the repository root at the
reviewed HEAD with bytecode and repository pytest plugins disabled where
shown.

### 9.1 Focused Slice B query, public-contract, and hostile-revalidation tests

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result: `43 passed in 12.20s`.

### 9.2 Complete BH Slice A+B focused regression

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_revalidation.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Result: `140 passed in 25.29s`.

### 9.3 PT/VP demo, artifact, and authoritative-material preservation

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_demo_model.py \
  tests/model_kernel/test_demo_pt001.py \
  tests/model_kernel/test_demo_vp001.py \
  tests/model_kernel/test_variable_port_revalidation.py -q
```

Result: `42 passed in 37.88s`.

### 9.4 Complete model-kernel suite

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/model_kernel/ -q
```

Result: `1095 passed in 91.18s`.

### 9.5 Direct boundary inspection

```bash
git diff --name-only \
  c39c674a95ad04c68250e23e86b169399a9547dd..ec50f7040f1a6fc703acfbe2cb599604ce431f76 \
  -- backend/model_kernel/contracts.py backend/model_kernel/canonical.py \
  backend/model_kernel/store.py backend/system_identity models bindings \
  interpretations backend/model_state backend/temporal_state \
  backend/identity_binding backend/behavior_evaluation
```

Result: empty; none of those Slice A, ledger, upper-layer, or evaluator paths
changed.

## 10. Findings and residual risks

### 10.1 Findings

No blocking, major, minor, or advisory implementation defect was found.

The preimplementation ambiguity over body groups was resolved before this
review and is implemented correctly: all active tips are grouped for
disclosure, while only healthy roots participate in independent-root voting.
This is explicitly pinned in production derivation, focused tests, the Slice B
plan, and acceptance rows B30a and B30b.

### 10.2 Residual limitations, not Slice B defects

- Result validation necessarily repeats deterministic derivation work over
  the complete carried membership. This is the accepted integrity tradeoff;
  Slice B introduces no cache or persisted projection.
- `ModelQueryMaterial` remains defined in the pre-existing port result module.
  Reusing it avoids a risky cross-cutting relocation during Slice B. A future
  module-layout refactor would require its own owner gate and must preserve all
  public identities and bytes.
- Slice B discloses declared behavior knowledge only. It selects no source,
  reads no temporal evidence, compares no numbers, and produces no truth about
  operation, causality, flow, control, correctness, safety, or health.
- There are no committed BH records yet, so repository demonstrations of
  declared/inactive/conflicted behavior remain disposable test fixtures. This
  is intentional until the separately owner-gated Slice D.

## 11. Final architecture verdict

BH-001 Slice B at
`ec50f7040f1a6fc703acfbe2cb599604ce431f76` conforms to the corrected accepted
architecture:

- exact four-method read-only kernel surface;
- exact public results and literal vocabulary;
- complete authoritative model material carried once;
- nested rows represented by strict indices;
- store-independent reconstruction and hostile-forgery rejection;
- exact-context lifecycle disclosure;
- all-current-tip effective-body disclosure;
- healthy-root-only corroboration/disagreement voting;
- no winner selection;
- downward-only kernel dependencies;
- no Slice A mutation;
- no Slice C evaluator or Slice D fixture;
- explicit historical replay and preserved 29-record demo boundary.

Architecture verdict: **PASS; no repair required before the Slice B owner
validation gate.**

END OF BH-001 SLICE B ARCHITECTURE REVIEW
