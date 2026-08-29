# BH-001 Slice B completion report

Status: implemented and adversarially reviewed; awaiting owner acceptance.

Date: 2026-08-29

Authoritative design:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`

## 1. Outcome and stop gate

BH-001 Slice B is implemented on branch `bh001`. It adds exactly four
read-only model-kernel queries and their frozen, extra-forbidden,
authoritatively revalidated result contracts:

- `behavior(...)`;
- `behavior_declaration(..., context=...)`;
- `behaviors_involving_variable(..., context=...)`;
- `behavior_assertion(...)`.

The queries disclose permanent behavior registration, exact-context
declaration lifecycle, roots, ancestry, active tips, withdrawals,
effective-engineering-body agreement, independent corroboration, conflict,
inactivity, and membership-relative historical revival. They infer no
behavior and choose no winner.

The verified implementation-and-review HEAD before this completion report was
persisted is:

```text
66c3b54d1861687d45e3147ef871b14948d7fd70
```

The commit containing this report necessarily receives its content-addressed
identity only after the report is written. That terminal administrative HEAD
is recorded in the concise delivery receipt instead of being falsely
self-referenced here.

Slice C evaluation and Slice D demonstration remain unstarted. No evaluator,
numeric parser use, observation selection, state composition, fixture record,
or ledger append was introduced.

## 2. Authority and repository boundary

The accepted Slice A implementation boundary was:

```text
branch: bh001
accepted Slice A HEAD: 57edec37b40c5da0c300cc1333fbb3cf5d7bb41a
accepted main baseline: 46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
```

The owner-supplied authoritative inputs were read before implementation:

```text
corrected final BH-001 design SHA-256:
2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978

Slice A completion report SHA-256:
e5ee01aa267f3e446e09d56ecce0d7555b53ba9c7cedd2b9af813f5a3206a0af
```

The design hash above identifies the accepted engineering content before the
subsequent Slice A acceptance and Slice B status-only amendments. The current
status-amended design file is:

```text
SHA-256: 2b2f21335e4deff8989efc47498659bc990321566f972bfc0abb69130d49a8ba
```

No normative engineering definition was silently reinterpreted. The Slice A
private effective-engineering-body projection remains unchanged.

## 3. Administrative acceptance commit

Slice A owner acceptance was recorded before Slice B planning or code:

```text
c39c674a95ad04c68250e23e86b169399a9547dd
docs: record owner acceptance of BH-001 Slice A
```

That status retained the accepted scope: permanent role-free registration,
exact-context declaration lifecycle, evidence-backed records, no query facade,
no evaluator, and no fixture.

## 4. Slice B commits

The reviewable commit sequence after the accepted Slice A HEAD is:

```text
c39c674a95ad04c68250e23e86b169399a9547dd docs: record owner acceptance of BH-001 Slice A
c2a28c789f4e9a52976e8f9476503fee50c6f4c0 docs: plan BH-001 Slice B
54b9017c79a3315a78a42e09bbe145ac8e87af87 docs: correct BH-001 Slice B starting boundary
5d3e4fbbe57189fa1bf8960b9eb2150c5b6ab133 test: define BH-001 Slice B query contracts
a6fb5c2f09c19a89dabdb67a6a22227aa1471a31 feat: add BH-001 read-only kernel queries
ec50f7040f1a6fc703acfbe2cb599604ce431f76 fix: harden BH-001 query reconstruction
96048b004bea584b4758bf00dbf06c94c6606499 docs: record BH-001 Slice B reviews
66c3b54d1861687d45e3147ef871b14948d7fd70 docs: record BH-001 Slice B status
```

No commit was amended or rewritten. Nothing was pushed, merged, rebased,
reset, or cherry-picked.

## 5. Changed files

Slice B production code changes are limited to:

```text
backend/model_kernel/behavior_results.py       new authoritative results
backend/model_kernel/queries.py                four facade methods
backend/model_kernel/__init__.py               exact public exports
```

Red-first and regression tests are:

```text
tests/model_kernel/test_behavior_query_contracts.py
tests/model_kernel/test_behavior_queries.py
tests/model_kernel/test_behavior_query_revalidation.py
tests/model_kernel/test_behavior_records.py
tests/model_kernel/test_behavior_revalidation.py
tests/model_kernel/test_port_records.py
tests/model_kernel/test_structural_evidence_arm.py
tests/model_kernel/test_variable_port_query_contracts.py
tests/model_kernel/test_variable_port_records.py
tests/model_kernel/test_variable_registration.py
```

Documentation and review artifacts are:

```text
CLAUDE.md
backend/model_kernel/README.md
docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md
docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md
docs/superpowers/plans/2026-08-29-bh001-slice-a-implementation-plan.md
docs/superpowers/plans/2026-08-29-bh001-slice-b-implementation-plan.md
docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-completion-report.md
docs/superpowers/reports/2026-08-29-bh001-slice-b-architecture-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-b-backend-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-b-test-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-b-final-integrity-review.md
```

No model, binding, interpretation, source, temporal, structural, showcase, or
artifact file changed.

## 6. Exact public query API

The only new public `ModelQueries` methods are:

```python
def behavior(
    self,
    behavior_anchor_id,
) -> BehaviorLookupResult: ...

def behavior_declaration(
    self,
    behavior_anchor_id,
    *,
    context,
) -> BehaviorRuleResult: ...

def behaviors_involving_variable(
    self,
    variable_anchor_id,
    *,
    context,
) -> VariableBehaviorsResult: ...

def behavior_assertion(
    self,
    record_id,
) -> BehaviorAssertionDisclosureResult: ...
```

There is no alias, port query, evaluator method, overload, graph traversal, or
inference entry point. All four methods are read-only over the injected
`LoadedModel` and construct no store.

## 7. Exact public literal vocabularies

Slice B exports exactly six BH-specific aliases in this literal order:

```python
BehaviorLookupStatus = Literal[
    "not_registered",
    "registered",
]

BehaviorDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]

BehaviorRuleLineageSummary = Literal[
    "not_applicable",
    "healthy",
    "conflicted",
    "inactive",
]

BehaviorAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]

VariableBehaviorsStatus = Literal[
    "variable_not_registered",
    "registered",
]

BehaviorAssertionLookupStatus = Literal[
    "not_found",
    "found",
]
```

The accepted shared `AssertionActivity` and `ContainingLineageHealth` aliases
are reused. No behavioral validity, health, safety, diagnosis, pass/fail,
equal/different, causality, control, flow, or port vocabulary was introduced.

## 8. Exact result contracts

The seven public result field sets, in order, are:

```text
BehaviorEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices

BehaviorRuleRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices

BehaviorLookupResult
  material
  behavior_anchor_id
  status
  registration_index
  participant_variable_registration_indices
  participant_owner_registration_indices

BehaviorRuleResult
  material
  behavior_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices

VariableBehaviorEntry
  entry_index
  behavior_anchor_id
  other_variable_anchor_id
  behavior_registration_index
  other_variable_registration_index
  other_owner_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

VariableBehaviorsResult
  material
  variable_anchor_id
  context
  status
  variable_registration_index
  owner_registration_index
  entries

BehaviorAssertionDisclosureResult
  material
  record_id
  lookup_status
  record_index
  activity
  containing_lineage_health
  containing_subject_conclusion
  containing_agreement_findings
  root_record_index
  successor_indices
  withdrawal_indices
```

Complete authoritative records and evidence occur once in
`ModelQueryMaterial`. Nested rows carry strict non-negative indices and expose
only read-only convenience properties that resolve those indices through the
carried material. `backend.model_kernel.__all__` contains exactly 144 unique
names after the accepted 13 additions: six aliases and seven results.

## 9. Registration and exact-context semantics

`behavior()` discloses permanent registration independently of declaration
lifecycle. An absent anchor returns `not_registered`, no registration index,
and canonical empty participant tuples. A present registration returns its
record, both participant variable registrations, and both owner registrations
by authoritative indices.

`behavior_declaration()` evaluates only the exact
`(behavior_anchor_id, AssertionContext)` key:

| Registration | Exact-context roots | Active condition | Conclusion | Summary |
|---|---:|---|---|---|
| absent | none | not applicable | `not_registered` | `not_applicable` |
| present | none | none declared | `not_declared` | `not_applicable` |
| present | one or more | no active tips | `inactive` | `inactive` |
| present | active | conflict rule applies | `conflicted` | `conflicted` |
| present | active | no conflict | `declared` | `healthy` |

Claims in another assertion context are neither substituted nor combined.
Registration remains disclosed even when the requested context has no
declaration.

## 10. Lifecycle, corroboration, and conflict evidence

A parentless `bhd_` begins an independent root. Within each root:

- zero active tips is `inactive`;
- one active tip is `healthy`;
- multiple active tips is `conflicted`, including byte-identical effective
  bodies;
- corrections and multi-parent convergence remain within the root;
- cross-root convergence remains invalid under the accepted Slice A store.

Across independent healthy roots:

- exactly identical effective engineering bodies corroborate;
- different effective engineering bodies conflict;
- inactive roots remain disclosed but do not vote;
- a conflicted root remains a conflict even beside healthy or corroborating
  roots.

The effective body is the accepted Slice A projection only: behavior anchor,
exact context, two semantic locks, exact rule, and evaluation basis. Evidence,
authority, recorded time, note, record ID, filename, and append order remain
fully disclosed but never distinguish an engineering body or select a winner.

The result carries every root, lineage member, active tip, withdrawal, and
effective-body group in deterministic order. Independent corroborating roots
remain separate roots; corroboration never collapses their evidence or
authority.

## 11. Reverse discovery and assertion disclosure

`behaviors_involving_variable()` returns structured absence for an
unregistered variable. For a registered variable it discloses that variable
and its owner, then one row for every permanently registered behavior that
contains it. Shared ownership, matching names, topology, ports, VPA, semantics,
constraints, or observations never synthesize a row.

Rows are ordered by `behavior_anchor_id`, use contiguous zero-based strict
`entry_index` values, identify the other registered variable and owner, and
embed the exact-context lifecycle disclosure by indices. Registered-empty is
a valid result. Direct declaration and reverse-entry lifecycle material are
byte-equal after canonical serialization.

`behavior_assertion()` accepts only well-shaped `brg_`, `bhd_`, and `bhw_`
identities. Malformed or non-BH IDs fail through the typed input boundary
before loaded-model index access. For a well-shaped absent ID it returns
`not_found` with explicit `None` scalar lifecycle fields and canonical empty
successor and withdrawal tuples.

A found registration or withdrawal is disclosed as an event with no invented
declaration lifecycle. A found declaration reports:

- `current` when it has no successor or withdrawal;
- `superseded` when a direct successor exists;
- `withdrawn` when a withdrawal exists;
- its containing root and root health;
- the exact containing-subject conclusion and agreement findings;
- direct successors and withdrawals in record-ID order.

Conflict belongs to the containing root or subject, never to an individual
assertion. Omitting a later correction or withdrawal from an earlier explicit
membership revives the earlier assertion membership-relatively.

## 12. Authoritative store-independent revalidation

Every public outer result reconstructs nested content rather than trusting an
existing Pydantic instance. Validation:

1. reconstructs `ModelQueryMaterial` from serialized content;
2. validates each record union arm and every content-derived record ID;
3. verifies exact revision membership and canonical record ordering;
4. rebuilds the `LoadedModel` using the accepted in-memory validation path;
5. recomputes registration and owner closure;
6. recomputes the exact context key, roots, ancestry, successors,
   withdrawals, and current tips;
7. recomputes effective-body bytes using the accepted private kernel
   projection;
8. recomputes body groups, corroboration, conflict, inactivity, conclusions,
   and findings;
9. recomputes every record index, row index, and deterministic order;
10. compares the supplied public disclosure with that authoritative payload.

Validation owns no store, accesses no filesystem, and performs no write. It
uses shared private pure payload helpers from the same kernel result module so
the public facade and public-boundary reconstruction cannot drift.

All result models are frozen, extra-forbidden, and revalidate full instances.
Every index uses `StrictInt`, rejecting booleans, floats, strings, negative
values, and coercible alternatives. Invalid collection shapes become typed
Pydantic validation failures rather than leaking raw callbacks or trusting
duck-typed `model_dump` methods.

## 13. Red-before and fixed-after evidence

The public-contract, semantic, lifecycle, and hostile tests were committed
before production code. Against the unimplemented Slice A surface, the exact
focused reproduction was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

Red result:

```text
28 failed, 1 passed in 9.22s
```

The one pass was the negative scope guard; all missing public contracts and
queries failed as intended. There were no collection errors masking the red
state.

After implementation and hardening, the same focused surface plus the final
documentation-status pin produced:

```text
44 passed in 11.77s
```

The initial production pass reached 29/29 green. Adversarial extensions then
raised the focused total to 43, and the exact documentation-status assertion
raised the final total to 44.

## 14. Adversarial acceptance evidence

All B01-B60 controls in
`docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md`
are green. The test suite independently attacks:

- nested `model_construct` and `model_copy` forgeries;
- stale content-derived IDs after record mutation;
- missing, duplicated, substituted, or reordered membership;
- revision substitution and mixed-revision material;
- behavior, variable, owner, context, and record substitution;
- wrong union-arm indices;
- boolean, string, float, negative, and noncontiguous indices;
- missing, duplicated, substituted, and reordered reverse rows;
- forged roots, lineage members, tips, withdrawals, and ancestry;
- forged effective-body representatives and group membership;
- forged corroboration, same-root conflict, cross-root disagreement,
  inactivity, activity, conclusion, summary, and findings;
- hostile collection shapes and duck-typed nested objects;
- extra fields carrying port, flow, direction, causality, control, safety,
  diagnosis, evaluation, or recommendation implications;
- hash-seed and input-order nondeterminism.

Deterministic serialization was reproduced with hash seeds `1`, `17`, and
`31337` for all four queries. Reverse-map insertion order and explicit
membership order attacks did not change authoritative output.

Reviewer-added executable attacks were also green:

```text
software-test-engineer external attacks: 9/9 rejected as required
code-reviewer additional hostile attacks: 5/5 rejected as required
```

Two defense-in-depth issues found during review were repaired before the final
verification:

1. hostile `None` or non-sequence nested row collections now produce typed
   validation failures instead of raw iteration `TypeError`;
2. exact-key declaration lineage is grouped once and shares the material index
   map, avoiding avoidable repeated scans without changing semantics.

Nested dumping was additionally restricted to actual Pydantic `BaseModel`
instances, so an untrusted object cannot gain execution through a lookalike
`model_dump` callback.

## 15. Specialist reviews and reconciliation

The owner-required specialists reviewed the corrected Slice B implementation,
not the preimplementation design alone:

| Specialist | Artifact | Result |
|---|---|---|
| software-architect | `docs/superpowers/reports/2026-08-29-bh001-slice-b-architecture-review.md` | PASS |
| backend-engineer | `docs/superpowers/reports/2026-08-29-bh001-slice-b-backend-review.md` | GREEN |
| software-test-engineer | `docs/superpowers/reports/2026-08-29-bh001-slice-b-test-review.md` | GREEN |
| code-reviewer | `docs/superpowers/reports/2026-08-29-bh001-slice-b-final-integrity-review.md` | GREEN |

Their frozen review artifact identities are:

```text
architecture review
lines: 429
bytes: 18478
SHA-256: 7b98a560927ae0e7d79b015733231852a465dfc008369b07e1395b762c0b7c4a

backend review
lines: 398
bytes: 14875
SHA-256: de76fd7771aa506134623a4b49eb338ba5dfb81679bee8bd4d504d01fa3c5377

test review
lines: 349
bytes: 13303
SHA-256: eaf776169b2e643c9d2ed87e53438045ab920929ca8b1509566dff88ffd59b68

final integrity review
lines: 777
bytes: 27792
SHA-256: cba2aa67b8c8b32c807ae841231e8f8479b892a4b3d26e6b6544cf346b16c949
```

The lead reconciled every finding. No reviewer requested broader scope, a
Slice A contract change, Slice C evaluation, or Slice D fixture work. No
unresolved correctness finding remains.

## 16. Focused and affected verification

Final focused results are:

```text
Slice B public/lifecycle/revalidation: 44 passed in 11.77s
complete BH Slice A+B:                154 passed in 25.78s
complete model-kernel:                1096 passed in 84.52s
```

The complete BH command was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_revalidation.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q
```

The affected lower- and upper-layer regressions produced:

```text
system identity, model state, observation compatibility,
semantic compatibility, and constraint evaluation: 712 passed in 169.44s

architecture and import isolation: 94 passed in 39.08s

PT, VP, demo, historical replay, and artifact preservation:
40 passed in 36.09s
```

Focused optional-dependency verification produced:

```text
OCP/STEP: 31 passed in 207.15s
PDF:      89 passed in 141.43s
```

Backend compilation passed with:

```bash
PYTHONPYCACHEPREFIX=/tmp/bh001-slice-b-pyc \
  .venv/bin/python -m compileall -q backend
```

The implementation worktree full repository suite before the final single
documentation-status test was added produced:

```text
2597 passed in 620.73s
```

The final 2598-test surface is reproduced by the all-extras clean-checkout
column in Section 17.

## 17. Dual clean-checkout verification

Two fresh detached worktrees were created at the exact verified HEAD
`66c3b54d1861687d45e3147ef871b14948d7fd70`:

```text
/tmp/bh001-slice-b-base-clean-uw6ac5
/tmp/bh001-slice-b-extras-clean-6uP81L
```

Both installed base and development dependencies from the committed files.
The extras checkout then installed CAD and PDF dependencies with hash checking:

```bash
venv/bin/pip install -r requirements.txt -r requirements-dev.txt

venv/bin/pip install --require-hashes \
  -r requirements-cad.txt -r requirements-pdf.txt
```

Each checkout ran:

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q
```

Results before the separately authorized loopback rerun were:

```text
base-only:  2562 passed, 35 skipped, 1 sandbox-denied error in 288.08s
all-extras: 2597 passed, 1 sandbox-denied error in 329.78s
```

In both columns the sole error was exactly:

```text
tests/data_sources/test_http_api_connector.py::
TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation

PermissionError: [Errno 1] Operation not permitted
```

The test was rerun with the required permission in each checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation \
  -q
```

Authorized results:

```text
base-only loopback:  1 passed in 0.73s
all-extras loopback: 1 passed in 0.75s
```

Therefore the final clean-checkout columns are:

```text
base-only:  2563 passed, 35 skipped
all-extras: 2598 passed
```

Both detached worktrees remained clean and resolved to the exact verified
commit. No clean-checkout test depended on the implementation worktree,
uncommitted content, directory enumeration, or local optional packages.

## 18. Historical replay and byte preservation

Every accepted explicit model membership remains unchanged:

```text
9 records
mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d023e3da83227f

10 records
mrv_105658072294bad92f83e3d536863cb46d6d7ae83f271fb59d5026839d002686

11 records
mrv_25afc0ebf17ed12bd6ef0a95795798a53ef2731983410136d3da15c4d0f98093

14 records
mrv_702c840f7da00617feb1be252838105d8b001b2e19978842bdcbec56996c99ff

16 records
mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a40099e8032ca8135b

18 records
mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51

28 records
mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2

29 records
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

Each pre-BH membership returns structured absence:

- behavior lookup `not_registered`;
- exact-context declaration `not_registered` with no roots or groups;
- assertion lookup `not_found`;
- registered variables with empty behavior collections.

The demo ledger remains:

```text
record count: 29
BRG count: 0
BHD count: 0
BHW count: 0
revision: mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

The accepted VPA remains byte-identical:

```text
record ID:
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49

stored-file SHA-256:
95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e
```

The deterministic artifacts remain:

```text
PT artifact SHA-256:
53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8

VP artifact SHA-256:
a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3
```

No canonical byte, content-derived ID, Slice A golden, record contract, store
admission rule, index, membership constant, model revision, fixture, binding,
temporal occurrence, interpretation, source evidence, structural evidence, or
artifact changed.

## 19. Architecture and isolation evidence

Slice B preserves this dependency direction:

```text
backend.system_identity
          ↑
backend.model_kernel
```

The model kernel imports no model state, temporal state, identity binding,
semantic compatibility, observation compatibility, constraint evaluation,
source interpretation, data source, structural evidence, CAD, PDF, or future
behavior evaluation module.

The query facade:

- receives a `LoadedModel`;
- owns no `ModelStore`;
- constructs no store or repository;
- reads and writes no file;
- opens no database or socket;
- persists no result;
- mutates neither membership nor indexes;
- performs no graph traversal or behavior inference;
- uses record IDs for display ordering only, never truth selection.

No upward import from the kernel and no lower-layer import of behavior result
contracts was introduced. No new store, ledger, revision, cache, projection,
database, or runtime composition module exists.

## 20. Exact reproduction commands

The principal verification commands are:

```bash
# Focused Slice B
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_behavior_query_contracts.py \
  tests/model_kernel/test_behavior_queries.py \
  tests/model_kernel/test_behavior_query_revalidation.py -q

# Complete model kernel
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/model_kernel/ -q

# Complete repository
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q

# OCP/STEP
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/data_sources/test_step_extractor.py \
  tests/data_sources/test_ingestion_runner_step.py \
  tests/structural_evidence/test_step_claims.py -q

# PDF
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/data_sources/test_pdf_contracts.py \
  tests/data_sources/test_pdf_coordinates.py \
  tests/data_sources/test_pdf_detection_availability.py \
  tests/data_sources/test_pdf_extractor.py \
  tests/data_sources/test_ingestion_runner_pdf.py -q

# Compilation and diff hygiene
PYTHONPYCACHEPREFIX=/tmp/bh001-slice-b-pyc \
  .venv/bin/python -m compileall -q backend
git diff --check
git status --short
```

Historical replay is explicitly membership-driven in the committed tests. No
reproduction command derives an old membership from directory enumeration,
filename prefix, timestamp, append order, or current ledger contents.

## 21. Limitations and explicit exclusions

Slice B discloses only explicit, revision-relative model knowledge. It does
not establish, evaluate, or imply:

- exact numeric equality of any observations;
- source selection or observation availability;
- acquisition-cohort alignment or simultaneity;
- semantic or unit admission;
- constraint satisfaction;
- behavior validity, correctness, health, safety, diagnosis, or operation;
- input/output direction, dependency, cause/effect, command/response, flow,
  influence, control, or state transition;
- a relationship at a port or through a VPA;
- real-machine truth.

An inactive declaration is only inactive in the selected model membership. A
conflict is disclosed and never resolved. Corroboration is independent
agreement on an identical effective engineering body, not proof of physical
truth. `as_of`, source selection, temporal evidence, numeric parsing, and
evaluation do not exist in Slice B.

## 22. Remaining owner-gated slices

Slice C remains separately owner-gated and unstarted. It may add only the
accepted read-only `backend/behavior_evaluation` layer after Slice B owner
acceptance, including explicit source selectors, exact same-acquisition-envelope
admission, inherited public CN exact-number parsing, and independent result
dimensions.

Slice D remains separately owner-gated and unstarted. It may add only the
accepted bounded declaration-only synthetic demonstration after disposable
rehearsal and owner approval of the exact derived identities and artifact
contract.

No implementation work, tests, fixture preparation, identity minting, or
artifact generation for either later slice was begun.

## 23. Repository and remote status

At the verified implementation-and-review boundary:

```text
branch: bh001
HEAD: 66c3b54d1861687d45e3147ef871b14948d7fd70
worktree: clean
git diff --check: passed
remote: origin unchanged
push: none
merge: none
rebase: none
reset: none
cherry-pick: none
history rewrite: none
```

The only post-verification change is this completion report. It will be
committed as the terminal documentation delivery and its resulting HEAD will
be recorded in the concise receipt.

## 24. Final stop gate

BH-001 Slice B satisfies its authorized scope:

- exact four-query public facade;
- exact literal vocabularies, field sets, signatures, and exports;
- permanent registration and exact-context declaration disclosure;
- same-root conflict, independent corroboration, cross-root disagreement, and
  inactive-root disclosure;
- current, superseded, withdrawn, and historical-revival assertion evidence;
- carry-once authoritative material and strict index-only rows;
- store-independent full reconstruction and hostile rejection;
- deterministic ordering and serialization;
- green focused, kernel, affected, architecture, optional, full-repository,
  and dual-clean-checkout verification;
- unchanged historical identities, model ledger, demo count, VPA, and PT/VP
  artifacts;
- independent specialist architecture, backend, testing, and integrity
  reviews;
- no Slice C or Slice D work.

There is no unresolved implementation discrepancy. The only open question is
the intended owner gate: whether to accept BH-001 Slice B and separately
authorize Slice C.

BH-001 Slice B implemented and adversarially reviewed; awaiting owner acceptance.

END OF BH-001 SLICE B COMPLETION REPORT
