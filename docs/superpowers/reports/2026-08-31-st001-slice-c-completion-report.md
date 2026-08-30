# ST-001 Slice C Completion Report

Date: 2026-08-31

Status: implemented and adversarially reviewed; awaiting owner acceptance

## 1. Outcome

ST-001 Slice C implements the separately authorized, read-only
`backend/state_classification` composition. It adds exactly one facade method:

```python
StateClassificationQueries.state_classification(
    state_anchor_id,
    *,
    context,
    as_of,
    condition_sources,
) -> StateClassificationResult
```

The facade composes an injected public `ConstraintEvaluationQueries`, reaches
the same loaded model through the public
`constraints.semantic.compatibility.state.model` chain, and constructs public
`ModelQueries` over that exact membership. It owns no store, filesystem,
database, cache, projection, repository, socket, network client, or write
capability.

The implementation preserves state-declaration lifecycle, CN evaluation,
temporal evidence, source selection, coverage, execution, and computed match
as distinct disclosures. It adds no fixture, candidate identity, ledger
record, persisted result, current-state assertion, or transition capability.
Slice D remains unstarted and unauthorized.

## 2. Repository boundary

- branch: `st001`
- accepted original milestone base:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`
- accepted Slice B base:
  `23eca10a52c0124d22b4e90d80bef952ef5f9381`
- implementation and verification HEAD before this report commit:
  `1d16acdf843d2e46699680c4b18bf345f16f8cab`
- `main`:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`
- `origin/main`:
  `0ed77df7ea4870faec1eae9b89668add97aa855d`

The completion-report commit is intentionally not self-referential. Its final
administrative HEAD is supplied in the file-delivery receipt after commit.

No push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
performed.

## 3. Administrative acceptance commit

Commit `5c389f839fae4ae806fe0bf757a1d32faa0e1bdd` separately records:

- Slice B owner acceptance at
  `23eca10a52c0124d22b4e90d80bef952ef5f9381`;
- Slice C authorization for only the read-only classifier;
- continued Slice D prohibition;
- no change to Slice A or B runtime behavior.

Both working-tree and complete milestone-range whitespace checks passed at
that gate. The accepted demo remained the 32-record BH-001 membership.

## 4. Commit list

Commits after the accepted Slice B HEAD and before this completion-report
commit:

| Commit | Subject |
|---|---|
| `5c389f839fae4ae806fe0bf757a1d32faa0e1bdd` | `docs: record ST-001 Slice B acceptance` |
| `8b7a375991480fd8d46f86506ce06d128741691f` | `docs: plan ST-001 Slice C classification` |
| `57b62ae` | `test: pin ST-001 classification surface red` |
| `dfd3221` | `feat: add ST-001 state classification facade` |
| `c905f87` | `test: harden ST-001 classification integrity` |
| `153c7a0` | `test: close ST-001 classifier adversarial gaps` |
| `e10861f` | `docs: record ST-001 Slice C implementation status` |
| `1d16acd` | `docs: preserve state-query non-inference assertion` |

The abbreviated hashes identify the exact commits in this branch and are
unambiguous. The final report commit is reported in the delivery receipt.

## 5. Changed files

### 5.1 Production package

- `backend/state_classification/__init__.py`
- `backend/state_classification/contracts.py`
- `backend/state_classification/derivation.py`
- `backend/state_classification/errors.py`
- `backend/state_classification/facade.py`
- `backend/state_classification/README.md`

### 5.2 Slice C tests

- `tests/state_classification/__init__.py`
- `tests/state_classification/helpers.py`
- `tests/state_classification/test_public_contract.py`
- `tests/state_classification/test_classification.py`
- `tests/state_classification/test_alignment_and_truth.py`
- `tests/state_classification/test_scheduling_and_inputs.py`
- `tests/state_classification/test_revalidation.py`
- `tests/state_classification/test_architecture.py`
- `tests/state_classification/test_cross_layer_and_temporal.py`
- `tests/state_classification/test_determinism_and_preservation.py`
- `tests/state_classification/test_historical_replay.py`
- `tests/state_classification/test_documentation.py`

### 5.3 Focused lower-boundary regression updates

- `tests/model_kernel/test_state_query_revalidation.py`
- `tests/model_kernel/test_state_revalidation.py`
- `tests/model_kernel/test_state_slice_b_documentation.py`

The first two preserve the accepted kernel import boundary while replacing an
obsolete pre-Slice-C assertion that the authorized upper package must not
exist. The documentation test retains the exact Slice B non-inference text.
No Slice A record or Slice B query contract changed.

### 5.4 Documentation and owner-gate material

- `CLAUDE.md`
- `backend/model_kernel/README.md`
- `docs/adr/0016-explicit-state-identity-and-evidence-gated-classification.md`
- `docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-and-evidence-gated-classification-design.md`
- `docs/superpowers/plans/2026-08-30-st001-slice-b-implementation-plan.md`
- `docs/superpowers/plans/2026-08-30-st001-slice-b-adversarial-acceptance-matrix.md`
- `docs/superpowers/plans/2026-08-31-st001-slice-c-implementation-plan.md`
- `docs/superpowers/plans/2026-08-31-st001-slice-c-adversarial-acceptance-matrix.md`
- this completion report

## 6. Exact public contracts

The package exports exactly these names in this order:

1. `StateClassificationError`
2. `StateClassificationConfigurationError`
3. `StateClassificationInputError`
4. `StateConditionSource`
5. `StateConditionDeclarationAlignment`
6. `StateConditionOutcome`
7. `StateConditionCoverage`
8. `StateTemporalAlignment`
9. `StateClassificationExecution`
10. `StateComputedMatch`
11. `StateClassificationRefusalReason`
12. `StateClassificationRefusal`
13. `StateClassificationConditionResult`
14. `StateClassificationResult`
15. `StateClassificationQueries`

Facade construction misuse reports
`STATE_CLASSIFICATION_CONFIGURATION_INVALID`. Structurally invalid requests
and source-set misuse report `STATE_CLASSIFICATION_INPUT_INVALID`. Typed CN and
other lower failures propagate unchanged and are neither wrapped nor
re-exported.

The exact frozen, extra-forbidden result fields are:

```text
state
state_anchor_id
context
as_of
ruleset_version
condition_sources
constraint_evaluations
conditions
condition_coverage
temporal_alignment
execution
refusals
computed_match
```

`ruleset_version` is exactly `st001.1`. One complete
`StateDeclarationResult` carries model material once. Each complete public CN
result is carried once. Condition rows contain only strict indices, condition
identity, pin alignment, and outcome.

## 7. Red-before and fixed-after evidence

The first public-contract run failed during collection with:

```text
ModuleNotFoundError: No module named 'backend.state_classification'
```

After the minimal public surface was added, those initial five contract tests
passed. The focused suite then grew through implementation and adversarial
review to its final `109 passed` result.

Confirmed specialist findings were each reproduced before repair:

1. stale retained IDs inside carried VSP/VSM model projections could remain
   internally accepted by lower objects;
2. nested raw mapping extras could be discarded by permissive legacy lower
   models during reconstruction;
3. a forged context instance could carry a hidden extra;
4. booleans, integers, floats, and strings could be coerced into cutoffs;
5. cyclic or deeply nested hostile mappings could reach Python recursion;
6. pre-Slice-C architecture tests incorrectly required the authorized package
   to remain absent.

Repairs bind lower model facts to the carried state membership through public
kernel queries, compare raw and reconstructed serialized shapes, reject hidden
Pydantic extras, require an actual aware `datetime`, and use an iterative
active-stack shape walk with depth 128 and node 200,000 bounds. Updated kernel
tests continue to forbid upward imports while recognizing the authorized
upper package.

One documentation edit initially split the exact Slice B phrase
`No query infers state`; the complete kernel suite exposed that regression.
The phrase was restored in the separate `1d16acd` commit, the focused
documentation reproduction passed, and the complete kernel suite then passed
all 1,266 tests.

## 8. Source validation and deterministic scheduling

Before lower access, the facade validates:

- one valid `sta_` identity;
- one exact `AssertionContext`;
- one actual aware cutoff, normalized to UTC;
- a tuple/list of at most 64 source rows;
- exact `StateConditionSource` reconstruction with no hidden extras;
- unique constraint identities and canonical constraint ordering.

An unregistered state accepts only an empty source tuple and schedules no CN
branch. A registered state requires exactly one source for every permanent
constraint and no other source.

Every registered condition branch is attempted once in canonical constraint
order, even when the state declaration is absent, inactive, or conflicted.
Every branch receives the same normalized cutoff and the permanent SRG subject
entity. If lower branches raise typed errors, the bounded schedule completes
and the first error in canonical constraint order is re-raised as the same
object. No source discovery, fallback, ranking, permutation, or cross-product
exists.

Direct-equivalence tests prove each carried CN result equals the corresponding
public direct `ConstraintEvaluationQueries.constraint_evaluation()` result.

## 9. Lifecycle, pin alignment, and truth-table demonstrations

Only a declared state with one admitted effective-body group can contribute a
computed match. One healthy root and multiple independent corroborating roots
with the same effective body can execute without selecting a declaration
winner. A withdrawn corroborating root remains disclosed while the surviving
healthy root may execute.

Exact VCN alignment is derived as follows:

| CN declaration | Alignment | Contribution | ST refusal |
|---|---|---|---|
| not registered | `not_registered` | none | `condition_not_registered` |
| not declared | `not_declared` | none | `condition_declaration_not_declared` |
| multiple current tips | `conflicted` | none | `condition_declaration_conflicted` |
| unique current ID differs from pin | `superseded` | none | `condition_declaration_superseded` |
| unique current ID equals pin | `exact_current` | CN verdict | CN not-evaluated maps to `condition_evaluation_not_evaluated` |

The first two condition-level mappings are defensive-unreachable through a
valid public SRG/STD membership because accepted reference and pin closure
require the constraint and pinned declaration. They remain fail-closed in the
derivation; tests prove the closure rather than manufacture an invalid private
model.

CN conflict remains strict. A disposable world with two parentless, current,
engineering-identical VCN records, a state pin naming one of them, and
satisfying evidence produces:

```text
CN declaration status: conflicted
ST pin alignment: conflicted
condition outcome: not_evaluated
coverage: incomplete
execution: not_executed
computed_match: None
refusal: condition_declaration_conflicted
```

ST does not compare, merge, or reinterpret VCN bodies.

The implemented all-of truth table is:

| Admitted condition outcomes | Coverage | Execution | Computed match |
|---|---|---|---|
| all satisfied | complete | executed | matches |
| violation, all siblings evaluated | complete | executed | does_not_match |
| violation plus unknown sibling | incomplete | executed | does_not_match |
| no violation plus unknown | incomplete | not_executed | None |

For unregistered, not-declared, inactive, or conflicted state lifecycle,
coverage is `not_evaluated`, execution is `not_executed`, and computed match is
`None`; independently scheduled CN results remain carried for registered
states. A nonmatch does not establish another state.

## 10. Temporal policy and non-claims

Every CN branch independently selects its accepted latest evidence at or
before one shared cutoff. Registered classifications disclose
`temporal_alignment="not_asserted"`. Receipt times, source-native times,
clock-domain data, staleness, and provenance remain in the lower result and
are not rewritten.

Tests use different receipt times while preserving successful classification
to prove that ST does not invent co-temporality. There is no acquisition
cohort, simultaneity, synchronization, skew, freshness class, interpolation,
resampling, lag compensation, persistence, range search, or source-clock
equivalence. `as_of` never selects model membership.

`matches` and `does_not_match` are evidence-relative all-of results. Neither
asserts a current physical state, exclusivity, completeness, transition,
causality, control, safety, health, correctness, fault, diagnosis, or action.

## 11. Authoritative reconstruction and authenticity boundary

`StateClassificationResult` reconstructs all nested public models from
serialized content and then recomputes every ST-derived field without a facade,
store, filesystem, or network. It:

- revalidates `StateDeclarationResult` and rebuilds its exact membership;
- reruns public kernel declaration queries;
- reconstructs every public CN result;
- binds lower registrations, specifications, and semantics back to that model;
- enforces common model, binding, interpretation, and cutoff axes;
- validates exact state, context, entity, constraint, selector, candidate, and
  pin coherence;
- recomputes alignments, outcomes, coverage, temporal disclosure, ordered
  refusals, execution, and computed match;
- rejects missing, duplicated, extra, reordered, substituted, wrong-arm,
  stale-ID, boolean-index, mixed-revision, mixed-cutoff, hidden-extra,
  `model_construct`, and `model_copy` attacks.

The iterative serialized-shape guard rejects cycles, excessive depth, and
excessive node counts without recursive traversal.

The new ST-specific executable limitation test coherently changes a carried
lower occurrence quality flag in every copy accepted by the lower public
contracts. The reconstructed ST result honestly accepts that coherent change.
This proves the exact boundary: ST establishes internal coherence of carried
public material but does not independently authenticate uncaptured raw payload
bytes. The validator never accesses a store or filesystem to overclaim a
stronger guarantee.

## 12. Specialist review and repairs

Three bounded internal specialists reviewed the first green implementation:

### 12.1 Architecture and backend review

The backend reviewer confirmed the exact public facade chain, deterministic
branch scheduling, CN-owned evaluation semantics, unchanged lower contracts,
and absence of Slice D work. Its final review found no blocker.

### 12.2 Canonical and adversarial integrity review

The integrity reviewer independently reproduced the five hostile-validation
defects listed in Section 7. Each received a focused failing regression before
repair. Its final review found no remaining blocker after stale lower model
facts, raw nested extras, hidden context extras, coercible cutoffs, and
deep/cyclic payloads were closed.

### 12.3 Test-coverage review

The test reviewer identified obsolete import-presence assertions and missing
coverage for corroborating roots, inactive roots beside a survivor, direct CN
equivalence, 64-row preflight, historical replay, determinism, multi-refusal
ordering, strict indices, different receipt times, and artifact preservation.
Those cases are now regressions. The reviewer also confirmed that the two
closure-protected condition mappings are defensive-unreachable through valid
public material; this is documented rather than bypassing the public store.

No review broadened Slice C. No external Kimi audit was requested.

## 13. Verification matrix

All pytest commands used `-o addopts='' -p no:cacheprovider` and
`PYTHONDONTWRITEBYTECODE=1`.

| Verification column | Result |
|---|---:|
| focused final Slice C classifier | 109 passed |
| complete ST Slice A-C plus state identity | 270 passed |
| complete model-kernel | 1266 passed |
| complete constraint-evaluation | 183 passed |
| affected binding, temporal, model-state, observation, source-interpretation, semantic, and behavior suites | 941 passed |
| architecture/capability plus hostile reconstruction | 77 passed |
| explicit replay plus PT/VP/BH artifact preservation | 49 passed |
| focused STEP/OCP and PDF paths | 120 passed |
| state identity minter/contract | 30 passed |
| focused Slice C documentation/status | 3 passed |
| backend compilation | passed |
| complete implementation-worktree repository suite | 3064 passed |
| fresh base-only aggregate | 3028 passed, 35 skipped, 1 sandbox-denied setup |
| fresh base-only permitted loopback rerun | 1 passed |
| fresh base-only distinct verified total | 3029 passed, 35 expected optional skips |
| fresh all-extras aggregate | 3063 passed, 1 sandbox-denied setup |
| fresh all-extras permitted loopback rerun | 1 passed |
| fresh all-extras distinct verified total | 3064 passed |

The only clean-checkout aggregate error in either environment was the known
localhost sandbox boundary:

```text
PermissionError: [Errno 1] Operation not permitted
ThreadingHTTPServer(("127.0.0.1", 0), Handler)
```

It occurred only in
`TestRealLoopbackTransport.test_get_redirect_refusal_and_proxy_isolation`.
The exact test was rerun separately through the accepted permission mechanism
and passed once in each checkout. A denied setup is not counted as a pass.

Base-only skipped 35 tests requiring separately pinned CAD/PDF dependencies.
The all-extras environment installed base/dev requirements followed by the
hash-pinned CAD and PDF requirement files and ran every test.

## 14. Reproducible verification commands

Representative implementation-worktree commands:

```text
.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/state_classification -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_state_anchor.py \
  tests/model_kernel/test_state_*.py tests/state_classification -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/constraint_evaluation -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/identity_binding tests/temporal_state tests/model_state \
  tests/observation_compatibility tests/source_interpretation \
  tests/semantic_compatibility tests/behavior_evaluation -q

.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend

git diff --check
git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD
```

Fresh detached worktrees were created at exact HEAD `1d16acd`. Independent
Python 3.13 virtual environments were populated as follows:

```text
base-only: requirements.txt plus pytest
all-extras: requirements.txt, requirements-dev.txt,
            --require-hashes -r requirements-cad.txt,
            --require-hashes -r requirements-pdf.txt
```

Each checkout ran the full suite from its own root. Both detached checkout
statuses remained clean.

## 15. Historical, ledger, and artifact preservation

Every accepted explicit model membership replays unchanged:

```text
9 / 10 / 11 / 14 / 16 / 18 / 28 / 29 / 32 records
```

The authoritative demo remains exactly 32 records at:

```text
mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
```

It contains zero committed `srg_`, `std_`, or `stw_` records. Every pre-Slice-C
record byte and membership constant is unchanged. No binding, interpretation,
temporal, source, structural, PT, VP, BH, or model fixture changed.

Accepted deterministic artifact hashes remain:

| Artifact | SHA-256 |
|---|---|
| PT-001 | `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8` |
| VP-001 | `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3` |
| BH-001 | `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |

The preservation tests regenerated and verified those accepted bytes. Slice C
does not generate an ST artifact.

## 16. Administrative and topology checks

Before this report was added:

```text
branch: st001
working tree: clean
HEAD: 1d16acdf843d2e46699680c4b18bf345f16f8cab
main: 0ed77df7ea4870faec1eae9b89668add97aa855d
origin/main: 0ed77df7ea4870faec1eae9b89668add97aa855d
git diff --check: passed
git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD: passed
```

Both required diff checks are rerun after the report commit. Final HEAD,
report hash, exact status, and those final results are supplied in the concise
delivery receipt.

Nothing was pushed or merged.

## 17. Known limitations and exclusions

State classification inherits accepted lower-result semantics and the
carried-material authenticity boundary described in Section 11. It does not
authenticate absent raw bytes, change CN lifecycle, or invent unavailable
condition worlds.

Slice C deliberately adds no:

- demo state anchor or candidate identity;
- rehearsal or authoritative ledger append;
- deterministic ST artifact;
- state family, exclusivity, completeness, priority, or winner;
- aggregate current-state selection;
- transition identity, from/to direction, trigger, guard, action, event,
  history, persistence, execution engine, control, or recommendation;
- new ingestion, source discovery, store, ledger, database, cache, projection,
  or revision.

Slice D remains unstarted and unauthorized. ST-002 remains wholly excluded.

## 18. Owner gate

Owner question: accept ST-001 Slice C and separately authorize Slice D
pre-append rehearsal only?

END OF ST-001 SLICE C COMPLETION REPORT
