# ST-001 Slice B Completion Report

Date: 2026-08-31

Status: implemented and adversarially reviewed; awaiting owner acceptance

## 1. Outcome

ST-001 Slice B implements exactly four read-only model-kernel queries and
their authoritative public result contracts:

1. `state(state_anchor_id) -> StateLookupResult`
2. `state_declaration(state_anchor_id, *, context) -> StateDeclarationResult`
3. `states_of_entity(entity_anchor_id, *, context) -> EntityStatesResult`
4. `state_assertion(record_id) -> StateAssertionDisclosureResult`

Slice B carries one complete `ModelQueryMaterial`, uses lightweight strict
indices in disclosure rows, and reconstructs all derived results without a
store or filesystem. It adds no state classification, condition-source,
temporal, fixture, transition, persistence, or state-inference capability.

Slices C and D remain unstarted and unauthorized.

## 2. Repository boundary

- branch: `st001`
- accepted original milestone base:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`
- accepted Slice A base:
  `9adcf4d9613ac96e5fb430a4b750f3053679b64d`
- implementation and verification HEAD before this report commit:
  `4a671870e2c24b33a18380604e4a3c68fcf34dc1`
- `main`:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`
- `origin/main`:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`

The completion-report commit is intentionally not self-referential. Its final
administrative HEAD is supplied in the file-delivery receipt after commit.

No push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
performed.

## 3. Mandatory administrative correction

Before Slice B production work, the accepted Slice A report was checked over
the complete milestone range, not merely the then-clean working tree:

```text
git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..9adcf4d9613ac96e5fb430a4b750f3053679b64d

docs/superpowers/reports/2026-08-30-st001-slice-a-completion-report.md:3: trailing whitespace.
+Date: 2026-08-30 [two trailing spaces]
docs/superpowers/reports/2026-08-30-st001-slice-a-completion-report.md:4: trailing whitespace.
+Status: implemented and adversarially reviewed; awaiting owner acceptance [two trailing spaces]
```

Commit `dbc09283e26345192e096236680e455ce72c1c1e` removed exactly those
two Markdown trailing-space sequences and recorded Slice A owner acceptance
and Slice B authorization. It changed no runtime, canonical, test, fixture, or
ledger behavior. Both working-tree and full-milestone diff checks pass after
the correction.

This corrects the prior administrative receipt: ordinary `git diff --check`
on an empty working tree could not inspect already committed report content.

## 4. Commit list

Commits after accepted Slice A HEAD and before the completion-report commit:

| Commit | Subject |
|---|---|
| `dbc09283e26345192e096236680e455ce72c1c1e` | `docs: record ST-001 Slice A acceptance` |
| `560fc7b61ded53a8f0506b345327e2834e279ca5` | `docs: plan ST-001 Slice B queries` |
| `289e8bb8681fb02163baf1a43fb5bb3f39b5b91b` | `test: define ST-001 state query contracts` |
| `259b8bbb838fee6a04b85d46b3255671fe624972` | `feat: add ST-001 state query contracts` |
| `f6ee0688af51358a3bca0766cd88b8754c80da23` | `test: cover ST-001 state query lifecycle` |
| `3f12c7f31dc52705f4127d416fc0cf18d908bfb2` | `test: attack ST-001 query revalidation` |
| `7f7d7a8c8c59292d2a37e81a58aa2f1ab7fdc939` | `fix: reject hidden ST query result extras` |
| `399b36f37821350800ea3ad502c082bfe4401710` | `test: pin additive ST query exports` |
| `c48f0f266e0acbf7b7cd11e50f1fbbbac914d366` | `test: harden ST-001 query lifecycle disclosure` |
| `f218e34644ecb5efe86e0a1763c84b8134d44320` | `test: reproduce ST query boundary forgeries` |
| `6ca09357c5f78559bdd421b20da84bc40d1eb29a` | `fix: harden ST query reconstruction boundaries` |
| `b70d06c0ca1786bd9a465699082c9e58671a0d57` | `test: close ST-001 Slice B review gaps` |
| `4a671870e2c24b33a18380604e4a3c68fcf34dc1` | `docs: document ST-001 Slice B query boundary` |

## 5. Changed files

Relative to accepted Slice A HEAD:

```text
M  CLAUDE.md
M  backend/model_kernel/README.md
M  backend/model_kernel/__init__.py
M  backend/model_kernel/queries.py
A  backend/model_kernel/state_results.py
M  docs/adr/0016-explicit-state-identity-and-evidence-gated-classification.md
M  docs/superpowers/plans/2026-08-30-st001-slice-a-adversarial-acceptance-matrix.md
M  docs/superpowers/plans/2026-08-30-st001-slice-a-implementation-plan.md
A  docs/superpowers/plans/2026-08-30-st001-slice-b-adversarial-acceptance-matrix.md
A  docs/superpowers/plans/2026-08-30-st001-slice-b-implementation-plan.md
M  docs/superpowers/reports/2026-08-30-st001-slice-a-completion-report.md
M  docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-and-evidence-gated-classification-design.md
M  tests/model_kernel/test_behavior_query_contracts.py
M  tests/model_kernel/test_behavior_records.py
M  tests/model_kernel/test_port_records.py
A  tests/model_kernel/test_state_queries.py
A  tests/model_kernel/test_state_query_contracts.py
A  tests/model_kernel/test_state_query_revalidation.py
M  tests/model_kernel/test_state_records.py
M  tests/model_kernel/test_state_revalidation.py
A  tests/model_kernel/test_state_slice_b_documentation.py
M  tests/model_kernel/test_structural_evidence_arm.py
M  tests/model_kernel/test_variable_port_query_contracts.py
M  tests/model_kernel/test_variable_port_records.py
M  tests/model_kernel/test_variable_registration.py
```

The existing contract tests changed only to pin the additive `__all__` growth
from 148 to 162 public model-kernel names. No accepted Slice A record contract,
canonical vector, store admission rule, index, membership, or ledger file was
changed.

## 6. Exact public surface

### 6.1 Named literal contracts

```text
StateLookupStatus
  not_registered | registered

StateDeclarationConclusion
  not_registered | not_declared | declared | conflicted | inactive

StateDeclarationLineageSummary
  not_applicable | healthy | conflicted | inactive

StateAgreementFinding
  one_healthy_root
  corroborating_healthy_roots
  same_root_conflict
  cross_root_effective_body_disagreement
  inactive_roots_present

EntityStatesStatus
  entity_not_registered | registered

StateAssertionLookupStatus
  not_found | found
```

The result contracts reuse the accepted named `AssertionActivity` and
`ContainingLineageHealth` aliases. No anonymous narrowed substitute or public
implementation alias was added.

### 6.2 Result field sets

```text
StateConditionReferenceResult
  condition_index
  constraint_anchor_id
  constraint_registration_index
  pinned_declaration_index
  target_variable_registration_index
  target_owner_registration_index

StateEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices
  conditions

StateDeclarationRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices

StateLookupResult
  material
  state_anchor_id
  status
  registration_index
  subject_entity_registration_index
  condition_constraint_registration_indices
  condition_variable_registration_indices
  condition_owner_registration_indices

StateDeclarationResult
  material
  state_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices

EntityStateEntry
  entry_index
  state_anchor_id
  state_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

EntityStatesResult
  material
  entity_anchor_id
  context
  status
  entity_registration_index
  entries

StateAssertionDisclosureResult
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

All eight contracts are frozen, extra-forbidden, and full-instance
revalidated. Every index is a nonnegative `StrictInt`; booleans, floats,
strings, negative values, coercible values, wrong union arms, and out-of-range
values reject.

The exact 14-name Slice B export sequence is pinned, public `__all__` has 162
unique entries, and later-slice state names are absent.

## 7. Query semantics demonstrated

### 7.1 Registration lookup

- valid-shaped absent state returns `not_registered` with canonical empty
  tuples and explicit `None` indices;
- a registered state discloses its exact SRG, subject entity, permanent
  constraints, target variable registrations, and repeated owner indices in
  permanent constraint order;
- no state is inferred from existing constraints or variable ownership.

### 7.2 Exact-context declaration lifecycle

The tests independently demonstrate:

- unregistered: `not_registered / not_applicable`;
- registered without an exact-context root: `not_declared / not_applicable`;
- one healthy root: `declared / healthy / one_healthy_root`;
- identical independent healthy roots: `declared / healthy /
  corroborating_healthy_roots`;
- differing independent healthy effective bodies: `conflicted / conflicted /
  cross_root_effective_body_disagreement`;
- same-root forks, including engineering-identical bodies: `conflicted /
  conflicted / same_root_conflict`;
- partial convergence remains conflicted;
- complete convergence becomes healthy;
- all tips withdrawn becomes inactive;
- an inactive root remains disclosed beside one healthy root;
- an inactive root remains disclosed beside two corroborating healthy roots;
- one healthy independent root cannot hide a separate same-root conflict;
- selective withdrawal can restore one healthy current tip;
- omission of a later successor or withdrawal from explicit historical
  membership revives the earlier membership-relative tip.

Full applicable findings remain visible. A separate healthy root plus a
conflicted root discloses both `one_healthy_root` and `same_root_conflict`,
while the aggregate conclusion remains `conflicted`. A pure same-root fork
discloses only `same_root_conflict`.

Roots, lineage members, tips, and withdrawals sort by record ID. Effective
body groups sort by exact canonical body bytes. Conditions sort by constraint
anchor. IDs order disclosure only and never select truth or a winner.

### 7.3 Entity reverse discovery

- absent entity: `entity_not_registered`, no registration index, no entries;
- registered entity with no direct SRG: `registered`, empty entries;
- exact SRG subjects produce one entry per state for the requested context;
- not-declared, declared, inactive, and conflicted entries coexist;
- entries sort by state anchor ID and the accepted first-root tie-break;
- constraints, hierarchy, names, ports, VPA, behavior, source data, and
  observations create no entry.

### 7.4 Assertion disclosure

- malformed and non-ST IDs raise typed `ModelQueryError` before model access;
- valid-shaped absent SRG/STD/STW IDs return `not_found`;
- SRG and STW disclose event/permanent shape with all lifecycle/root fields
  `None` and collection fields empty;
- direct STD successor means `superseded`;
- direct withdrawal means `withdrawn`;
- otherwise STD activity is `current`;
- two direct successors and withdrawal rows disclose exact ID-sorted indices;
- an individual current assertion remains `current` while its containing root
  and aggregate subject are conflicted.

## 8. Authoritative reconstruction

Every outer validator:

1. rejects hidden Pydantic instance fields before serialization;
2. rebuilds `ModelQueryMaterial` and every nested context/row;
3. validates all content-derived record IDs;
4. rebuilds the selected `LoadedModel` in memory;
5. recomputes exact revision membership, SRG closure, exact context, lineage,
   roots, ancestry, successors, current tips, withdrawals, effective bodies,
   agreement, conclusion, activity, indices, field presence, and ordering;
6. compares the complete public payload with the authoritative derivation.

Store, filesystem, database, environment, clock, network, and write
capabilities are absent from result validation. Runtime capability tripwires
and AST/import tests enforce the boundary.

Hostile regressions cover:

- missing, duplicate, extra, reordered, and substituted material;
- coherent material from another revision;
- stale content-derived IDs and forged revision counts;
- hidden extras through `model_construct`, `model_copy`, and arbitrary
  `Mapping` wrappers;
- forged query-context instances before model access;
- missing, duplicate, reordered, and substituted roots, groups, conditions,
  entity entries, tips, lineage members, successors, and withdrawals;
- wrong union arms, booleans, coercible values, negative and out-of-range
  indices;
- forged activity, health, effective-body equality, corroboration,
  conclusion, findings, context, state, entity, variable, owner, and ordering.

## 9. Red-before and fixed-after evidence

The first public contract run against Slice A produced:

```text
4 failed, 1 passed
```

After the result contracts and exact four-method facade were implemented:

```text
5 passed
```

The first combined Slice B run exposed three expected acceptance updates in
Slice A-only surface/status tests. After the additive contract expectations
were pinned, the initial ST set passed:

```text
132 passed
```

The first dedicated hostile reconstruction run produced:

```text
2 failed, 10 passed
```

One failure was a non-mutating test payload and was corrected. The genuine
failure showed that a nested `model_copy` hidden extra was silently omitted;
the validator was hardened and the retained suite passed:

```text
12 passed
```

The internal integrity review then produced three additional red
reproductions:

1. arbitrary `Mapping` wrappers could launder a hidden nested extra;
2. a forged `AssertionContext` could lose a hidden field before validation;
3. `material.revision.record_count` accepted booleans/coercible twins in a
   one-record world.

The focused reproductions failed before `6ca0935` and passed afterward:

```text
3 passed
```

The final focused public/lifecycle/revalidation query suite is:

```text
48 passed
```

Lifecycle tests were added after the initial production skeleton. This report
does not mischaracterize their commit ordering as preimplementation red-first;
their value is independent semantic and adversarial proof.

## 10. Specialist reviews and repairs

### 10.1 Backend/architecture reviewer

Confirmed no remaining blocker, high, or medium defect. Verified:

- exact four-method public facade;
- canonical root/group/condition ordering;
- BH-style lifecycle and agreement semantics;
- assertion activity separated from root and aggregate health;
- store-independent result reconstruction;
- downward-only imports and intact Slice C/D boundary.

Reviewer-focused result: `40 passed` at the reviewed commit.

### 10.2 Integrity reviewer

Confirmed the three boundary defects listed in Section 9. Each was reproduced
red-first, repaired, and retained. Final review found no additional defect in
material reconstruction, indices, record identity, lineage, body grouping,
withdrawals, activity, or store/filesystem isolation.

### 10.3 Test/adversarial reviewer

Identified proof gaps for mixed healthy/conflicted roots, historical reverse
queries, assertion event shapes, complex deterministic ordering, hostile
material/row matrices, frozen models, and capability isolation. Commit
`b70d06c` closes all six groups. The final reviewer audit reported no remaining
blocker-level coverage gap.

No reviewer edited the repository. No finding broadened Slice B.

## 11. Verification matrix

All commands used `-o addopts='' -p no:cacheprovider` and
`PYTHONDONTWRITEBYTECODE=1` where applicable.

| Column | Result |
|---|---:|
| focused final Slice B query contracts/lifecycle/revalidation | 48 passed |
| complete ST Slice A+B plus state identity | 161 passed |
| complete model-kernel | 1266 passed |
| identity-binding + CN + model-state + behavior-evaluation affected suites | 722 passed |
| architecture/import/capability isolation | 71 passed |
| explicit replay + PT/VP/BH artifact preservation | 80 passed |
| focused PDF + STEP/OCP paths | 120 passed |
| focused Slice B documentation/status | 3 passed |
| backend compilation | passed |
| complete implementation-worktree repository suite | 2955 passed |
| fresh base-only aggregate | 2919 passed, 35 skipped, 1 sandbox-denied setup |
| fresh base-only permitted loopback rerun | 1 passed |
| fresh base-only distinct verified total | 2920 passed, 35 expected optional skips |
| fresh all-extras aggregate | 2954 passed, 1 sandbox-denied setup |
| fresh all-extras permitted loopback rerun | 1 passed |
| fresh all-extras distinct verified total | 2955 passed |

The only clean-checkout aggregate error was:

```text
PermissionError: [Errno 1] Operation not permitted
ThreadingHTTPServer(("127.0.0.1", 0), Handler)
```

It occurred in both sandboxes at
`TestRealLoopbackTransport.test_get_redirect_refusal_and_proxy_isolation`.
The exact test was rerun separately with the accepted localhost permission and
passed in each checkout (`1 passed` each). The denied setup is not counted as
a pass.

Base-only legitimately skipped 35 tests requiring the separately declared CAD
or PDF extras. The all-extras checkout installed base/dev first, followed by
the repository's separately hash-pinned CAD and PDF requirement files, and
ran all 2955 tests.

## 12. Exact verification commands

Representative commands:

```text
.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_state_query_contracts.py \
  tests/model_kernel/test_state_queries.py \
  tests/model_kernel/test_state_query_revalidation.py -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_state_*.py \
  tests/identity_binding/test_state_anchor.py -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/identity_binding tests/constraint_evaluation tests/model_state \
  tests/behavior_evaluation -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q

PYTHONPYCACHEPREFIX=/tmp/st001-slice-b-pyc \
  .venv/bin/python -m compileall -q backend

git diff --check
git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD
```

Fresh detached worktrees were created at exact HEAD `4a67187`. New Python 3.13
virtual environments were populated independently. The base environment used
`requirements.txt` plus `pytest`; the all-extras environment used
`requirements.txt`, `requirements-dev.txt`, then separately
`--require-hashes -r requirements-cad.txt` and
`--require-hashes -r requirements-pdf.txt`.

## 13. Historical and ledger preservation

Every explicit historical membership remains replayable with its exact
accepted revision:

| Records | Revision role |
|---:|---|
| 9 | pre-variable |
| 10 | pre-specification |
| 11 | VS-001 |
| 14 | pre-ES-001 |
| 16 | pre-CN-001 |
| 18 | CN-001 / pre-PT-001 |
| 28 | PT-001 / pre-VP-001 |
| 29 | VP-001 / pre-BH-001 |
| 32 | BH-001 current |

For every membership, all four state queries return structured ST absence,
including both registered-empty and absent-entity reverse collections. Every
result carries the exact selected revision. No directory enumeration,
filename, timestamp, append order, or ambient current ledger reconstructs
historical membership.

Current authoritative ledger checks:

```text
record files: 32
revision: mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
srg_: 0
std_: 0
stw_: 0
```

The full milestone diff contains no change under `models/`, `bindings/`,
`interpretations/`, or `backend/data_sources/`. Every predecessor ledger byte
and identity remains unchanged.

Accepted deterministic artifact checks remain:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| PT-001 | 33855 | `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8` |
| VP-001 | 17824 | `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3` |
| BH-001 | 122406 | `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |

## 14. Architecture and non-claims

`backend.model_kernel` imports no state classification, model state, temporal
state, identity binding, observation compatibility, semantic compatibility,
constraint evaluation, source interpretation, data-source, behavior
evaluation, or structural-evidence module for Slice B.

Queries operate only on the injected immutable `LoadedModel`. Result
validation reconstructs that material in memory and constructs no store.

Slice B does not assert or infer:

- that an observation is a state;
- that a constraint's existence or satisfaction declares a state;
- current physical state;
- exclusivity, completeness, priority, or winner;
- a state family or state space;
- transition identity, from/to direction, trigger, event, guard, action,
  causal meaning, persistence, execution, control, or recommendation;
- any state from hierarchy, names, ports, VPA, behavior, ownership, topology,
  temporal evidence, or source data.

## 15. Diff, status, and topology gates

Before writing this report:

```text
git diff --check
  passed

git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD
  passed

git status --short
  clean

branch
  st001

main
  0ed77df7ea4870faec1eae9b89668add97aa855d

origin/main
  0ed77df7ea4870faec1eae9b89668add97aa855d
```

Both fresh detached checkout statuses were clean after verification. The two
required diff checks are rerun after the report commit and their final results
are delivered in the receipt.

Nothing was pushed or merged.

## 16. Known limitations and remaining slices

Slice B discloses explicit revision-relative state registration and
declaration lifecycle only. It does not evaluate constraints or classify a
state against evidence.

Slice C remains unstarted and unauthorized. It is the separately owner-gated
read-only `backend/state_classification` composition.

Slice D remains unstarted and unauthorized. No state identity candidate,
SRG, STD, STW, fixture, membership, artifact, or authoritative ledger append
was created.

ST-002 remains wholly excluded and owns every future transition capability.

## 17. Owner gate

Owner question: accept ST-001 Slice B and separately authorize Slice C?

END OF ST-001 SLICE B COMPLETION REPORT
