# BH-001 Slice A completion report

Status: implemented and adversarially reviewed; awaiting owner acceptance.

Date: 2026-08-29

Authoritative design:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`

## 1. Outcome and stop gate

BH-001 Slice A is implemented on branch `bh001`. The implementation adds only
the accepted stable behavior identity and model-kernel record foundation:

- `BehaviorAnchor` and its public UUID4 minter;
- permanent, evidence-bearing `BehaviorRegistration` records;
- exact-context `BehaviorRuleDeclaration` correction DAGs;
- dedicated current-tip `BehaviorRuleWithdrawal` events;
- canonical identity support, validating-store admission, immutable indexes,
  historical replay, hostile reconstruction, public exports, tests, and
  documentation.

No Slice B query or result contract, Slice C evaluator or numeric comparison,
or Slice D fixture/model append was started. The demo remains the accepted
29-record VP-001 revision and contains no BH record.

The verified implementation-and-review HEAD before this completion report was
persisted is:

```text
191f706a9e0d5be35d1401e70fbede7a1a5adc0e
```

The commit containing this report necessarily receives its content-addressed
identity only after the report is written. That terminal administrative HEAD
is therefore recorded in the concise delivery receipt rather than falsely
self-referenced inside its own content.

## 2. Repository boundary and branch topology

Accepted base:

```text
branch: main
main: 46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
origin/main: 46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
```

Implementation branch:

```text
branch: bh001
ahead of origin/main: 6 commits before this report commit
behind origin/main: 0 commits
```

The accepted starting worktree contained only the owner-accepted modified
`CLAUDE.md` and untracked BH-001 specification. Their owner-supplied hashes
were verified before branching:

```text
CLAUDE.md
95b674d24e99f8a757eb1c99a470e6ffedc303b514acf207f409cdd83f8c4226

BH-001 corrected final synthesis
2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978
```

No push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
performed.

## 3. Reviewable commits

The Slice A history through the reviewed implementation HEAD is:

```text
703564fc19a834e9ee9a38f336eeec6e7642b0c1
docs: accept BH-001 design and file-first protocol

d780ed765534fa4426965cd315e0e5afff345abb
docs: plan BH-001 Slice A

19fdca6f476245a2b79d24ef0266182d0da77ba8
test: define BH-001 Slice A contracts

20bd22411a07c9fc2820b5cc15a1ce63df80fd7d
feat: add BH-001 identity and record foundation

1fb10097c2d0a97ecc007cef4034028c9a5668a2
fix: repair BH-001 adversarial findings

191f706a9e0d5be35d1401e70fbede7a1a5adc0e
docs: record BH-001 Slice A review
```

## 4. Changed-file inventory

Production and module documentation:

```text
CLAUDE.md
backend/system_identity/anchors.py
backend/system_identity/minting.py
backend/system_identity/__init__.py
backend/system_identity/README.md
backend/model_kernel/contracts.py
backend/model_kernel/canonical.py
backend/model_kernel/store.py
backend/model_kernel/__init__.py
backend/model_kernel/README.md
```

Design controls and reviews:

```text
docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md
docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
docs/superpowers/plans/2026-08-29-bh001-slice-a-implementation-plan.md
docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-preimplementation-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-architecture-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-backend-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-test-review.md
docs/superpowers/reports/2026-08-29-bh001-slice-a-final-integrity-review.md
```

Tests and synthetic test-only builders:

```text
tests/identity_binding/test_behavior_anchor.py
tests/identity_binding/test_port_anchor.py
tests/model_kernel/bh001_slice_a_helpers.py
tests/model_kernel/test_behavior_records.py
tests/model_kernel/test_behavior_canonical.py
tests/model_kernel/test_behavior_store.py
tests/model_kernel/test_behavior_revalidation.py
tests/model_kernel/test_demo_pt001.py
tests/model_kernel/test_port_records.py
tests/model_kernel/test_structural_evidence_arm.py
tests/model_kernel/test_variable_port_query_contracts.py
tests/model_kernel/test_variable_port_records.py
tests/model_kernel/test_variable_registration.py
tests/model_kernel/test_variable_value_specification.py
```

The existing exact-surface tests were updated only for the five new public
kernel contracts, the three new model-record union arms/prefixes, the three new
system-identity names, and a later-project status boundary. No fixture, ledger,
binding, interpretation, temporal, source, structural-evidence, or artifact
file changed.

## 5. Public identity contract

`BehaviorAnchor` is frozen, extra-forbidden, and revalidates complete instances.
Its exact fields are:

```text
anchor_id: ^bhv_[0-9a-f]{32}$
namespace
display_name
role_name
```

It contains no owner, participant, context, rule, evidence, lifecycle, role,
direction, state, port, VPA, flow, control, causality, or safety meaning.
`mint_behavior_anchor()` emits a fresh RFC-4122 UUID4-backed opaque ID and
returns only the validated anchor value.

The exact three system-identity additions are:

```text
BEHAVIOR_ANCHOR_ID_PATTERN
BehaviorAnchor
mint_behavior_anchor
```

## 6. Public model-record contracts

The exact `BehaviorRegistration` fields are:

```text
record_kind = behavior_registration
schema_version = 1
record_id = brg_<64 lowercase hex>
anchor
participant_variable_anchor_ids
rule_family = exact_numeric_equality
evidence
recorded_at
authority
note
```

The participant pair is exactly two distinct variable anchor IDs, unordered,
unique, and canonically sorted. Registration is permanent and has no context,
parents, withdrawal, owner field, or lifecycle.

The exact nested declaration contracts are:

```text
BehaviorVariableSemanticLock
  variable_anchor_id
  signature: ConstraintSemanticSignature

ExactNumericEqualityRule
  kind = exact_numeric_equality
```

The exact `BehaviorRuleDeclaration` fields are:

```text
record_kind = behavior_rule_declaration
schema_version = 1
record_id = bhd_<64 lowercase hex>
behavior_anchor_id
context: AssertionContext
participant_semantics
rule: ExactNumericEqualityRule
evaluation_basis = same_acquisition_cohort
evidence
supersedes
recorded_at
authority
note
```

The two locks are distinct and canonically variable-sorted, equal the permanent
registration pair at store admission, and require exact equality of
quantity-kind and unit identities. Observation-role identities may differ.
There is no expression, operator field, coefficient, offset, tolerance,
direction, participant role, value, result, or verdict.

The exact `BehaviorRuleWithdrawal` fields are:

```text
record_kind = behavior_rule_withdrawal
schema_version = 1
record_id = bhw_<64 lowercase hex>
withdraws: bhd_<64 lowercase hex>
recorded_at
authority
note
```

It contains no evidence, context, parents, outcome, replacement, reason code,
or negative-behavior claim.

The only five new public `backend.model_kernel.__all__` names are:

```text
BehaviorRegistration
BehaviorRuleDeclaration
BehaviorRuleWithdrawal
BehaviorVariableSemanticLock
ExactNumericEqualityRule
```

No BH-specific builder was added. All three records use the existing public
`build_record()` API.

## 7. Canonical identity and golden vectors

Canonical support adds exact mappings:

```text
behavior_registration -> brg_
behavior_rule_declaration -> bhd_
behavior_rule_withdrawal -> bhw_
```

All three prefixes are admitted by model-record and filename grammars. `brg_`
and `bhd_` are citable `ModelRecordEvidence`; `bhw_` is deliberately uncitable.

The frozen synthetic public-builder vectors are:

```text
BRG
record ID: brg_ecd5a9b669f91dca639fde20202ce4f3c4ff17006d7f0ffd23f09ed44f1f9e3e
canonical bytes: 840

BHD
record ID: bhd_9e3af9219521d1b3c5dfd5d41ae359dc8d3fb4c5db4b002586998e52f0a823eb
canonical bytes: 1427

BHW
record ID: bhw_4c2456b2a6473f6a37c47b9aadedc10b1a8610c80e6650ba70cdbd7b2dd938f6
canonical bytes: 293
```

`tests/model_kernel/test_behavior_canonical.py` pins every canonical byte, not
only the IDs and lengths. Reversed participants, semantic locks, evidence, and
valid parents produce identical bytes and IDs. Duplicate participants and
parents are rejected. Stale IDs, prefix substitution, hostile nested copies,
and hostile constructed instances fail at authoritative boundaries.

Slice A also supplies a private, non-persisted canonical effective-engineering-
body projection of exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

It excludes evidence, authority, time, note, record identity, parents, and
append order. Public body grouping and corroboration conclusions remain Slice B.

## 8. Store admission and ownership boundary

BRG admission requires:

1. both exact variable registrations in the selected membership;
2. both variables' owner entity registrations through the unchanged variable
   closure path;
3. exact model-record citations to both variable registrations;
4. at least one claim-bearing `OwnerDeclarationEvidence`;
5. closure of every additional model-record evidence reference;
6. exactly one permanent registration for each behavior anchor.

Same-owner and cross-owner pairs are both admitted when explicitly registered
with the required evidence. This is intentional. Shared ownership neither
creates nor strengthens a behavior claim.

BHD admission requires the exact behavior registration, the exact registered
pair in its locks, exact quantity-kind/unit agreement, the exact BRG citation,
claim-bearing owner-declaration evidence, and closure of all cited model
records.

The BH validation phase runs only after all unchanged pre-BH validation paths.
A mixed-invalid regression pins this failure precedence. Failed append remains
atomic: no record file is promoted and the prior revision and bytes remain
unchanged.

## 9. Lifecycle, roots, withdrawals, and corroboration material

The BHD lineage key is:

```text
(behavior_anchor_id, exact AssertionContext)
```

A parentless BHD starts an independent root. Same-root chains, forks, partial
convergence, and complete multi-parent convergence are admitted. Cross-root
convergence, cross-anchor parents, cross-context parents, unknown parents,
duplicate parents, self-parents, and cycles are rejected. No timestamp,
authority, filename, append order, or record ID selects a winner.

Independent roots remain separate. Identical effective bodies provide the
material needed for later corroboration disclosure; different effective bodies
provide the material needed for later conflict disclosure. Slice A does not add
the Slice B public conclusion vocabulary.

A BHW may target one current, unsuperseded, unwithdrawn BHD tip. Selective
fork-tip withdrawal leaves siblings current. Withdrawing every current fork tip
leaves the root present with an empty current-tip tuple. Unknown, wrong-kind,
superseded, duplicate, already-withdrawn, and successor-plus-withdrawal targets
are rejected. Replay without a later successor or withdrawal revives the
earlier tip membership-relatively.

## 10. Immutable indexes

`LoadedModel` adds exactly these copied, read-only mappings:

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

All mapping-key and tuple iteration is deterministic under reversed input maps
and `PYTHONHASHSEED=1`, `17`, and `31337`. Every mapping rejects mutation. Every
pre-BH membership exposes all twelve as immutable empty mappings.

## 11. Red-before and fixed-after evidence

The initial public contract run against the unmodified accepted documentation
HEAD was:

```text
66 failed in 8.10s
0 collection errors
```

The frozen complete Slice A red suite, before production changes, was:

```text
103 failed, 4 passed in 25.07s
0 collection errors
```

The four passes were preservation and Slice-isolation gates; every intended BH
capability was red.

The first production pass was:

```text
103 passed, 4 failed
```

It exposed four bounded issues: handwritten canonical placeholders used VRG
citations different from the frozen helper output; one test used an invalid
underscore-bearing model directory; one ancestry assertion used semantic
rather than canonical ID order; and declaration mapping iteration retained
caller insertion order. The tests and deterministic declaration map were
repaired without changing the accepted architecture.

The first affected legacy-kernel run found seven exact-surface guard failures
after the intentional five exports/three union arms were added. The identity
suite found one corresponding exact `system_identity.__all__` guard. Those
guards now pin the additive Slice A surface and nothing more.

Postimplementation specialists then independently found and reproduced:

1. four remaining input-order-dependent BH mapping iterations;
2. the missing required private effective-body projection;
3. BH validation executing before unchanged later pre-BH validation paths;
4. a PT acceptance-status test scanning into later BH status wording;
5. stale handwritten placeholder golden IDs in the acceptance matrix.

Repairs added direct red reproductions, sorted all affected mappings, added and
pinned the private projection, moved BH validation after every pre-BH path,
pinned mixed-invalid precedence, bounded the PT project-status scan, and
reconciled the matrix to measured public-builder vectors. No existing record
identity changed.

The repaired focused result is:

```text
110 passed in 14.91s
```

## 12. Independent specialist reviews

The lead reconciled all four required specialist perspectives.

```text
Preimplementation code/adversarial review
docs/superpowers/reports/2026-08-29-bh001-slice-a-preimplementation-review.md
SHA-256: 73675e1d2d77deee556747e1cc5c95d7de1524c80acc66284c29ed46904f2af9

Software-architect postimplementation review
docs/superpowers/reports/2026-08-29-bh001-slice-a-architecture-review.md
SHA-256: c7a106dba2e4576c44f2e98d744fc401a1918456f6cc20b0e370de98fddf355c

Backend-engineer implementation review
docs/superpowers/reports/2026-08-29-bh001-slice-a-backend-review.md
SHA-256: b222fdf59c4909566429ff33d8265bae8bf4779849763bf36ff7d2dd5f7afc95

Software-test-engineer adversarial review
docs/superpowers/reports/2026-08-29-bh001-slice-a-test-review.md
SHA-256: a9ee0900330fecaddbe9a01bf908eb405cc5287a839052968c7e2fb4741fc28a

Final code-reviewer integrity review
docs/superpowers/reports/2026-08-29-bh001-slice-a-final-integrity-review.md
SHA-256: 113530d8dfccd119f59472ae353952fe61a66495aaba4bae3953bf8e5ce504b5
```

The final verdict is green with no open Slice A blocker. Nonblocking future
failure-localization suggestions do not alter the accepted contracts and were
not used to broaden this slice.

## 13. Verification commands and exact results

Focused BH Slice A:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py -q
```

```text
110 passed in 14.91s
```

Complete model kernel:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/model_kernel/ -q
```

```text
1052 passed in 73.57s
```

Complete identity-binding/system-identity affected suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/identity_binding/ -q
```

```text
249 passed in 4.71s
```

Architecture/import-isolation column:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/model_kernel/test_isolation.py \
  tests/model_kernel/test_behavior_revalidation.py \
  tests/model_state/test_isolation.py \
  tests/model_state/test_vp001_slice_c_revalidation.py \
  tests/observation_compatibility/test_isolation.py \
  tests/semantic_compatibility/test_isolation.py \
  tests/structural_evidence/test_isolation.py -q
```

```text
83 passed in 28.25s
```

Historical replay, PT, VP, artifacts, and accepted state demonstration:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/model_kernel/test_isolation.py \
  tests/model_kernel/test_demo_model.py \
  tests/model_kernel/test_demo_pt001.py \
  tests/model_kernel/test_demo_vp001.py \
  tests/model_state/test_demo_vp001.py -q
```

Independent specialist result:

```text
40 passed
```

Focused OCP/STEP:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/data_sources/test_step_extractor.py \
  tests/data_sources/test_ingestion_runner_step.py \
  tests/structural_evidence/test_step_claims.py -q
```

```text
31 passed in 195.60s
```

Focused PDF:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/data_sources/test_pdf_contracts.py \
  tests/data_sources/test_pdf_coordinates.py \
  tests/data_sources/test_pdf_detection_availability.py \
  tests/data_sources/test_pdf_extractor.py \
  tests/data_sources/test_ingestion_runner_pdf.py -q
```

```text
89 passed in 128.62s
```

Backend compilation:

```bash
.venv/bin/python -m compileall -q backend
```

```text
passed; no diagnostics
```

Complete repository suite, all extras, with local loopback permission:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/ -q
```

```text
2554 passed in 542.31s
```

The first sandboxed complete run produced `2549 passed, 1 failed, 1 error`:
the failure was the already-repaired in-flight PT status-boundary test, and the
error was `PermissionError` when the real loopback fixture attempted to open
`127.0.0.1`. The loopback test was immediately rerun with required permission:

```text
1 passed in 1.85s
```

The final full run included that loopback test and passed all 2554 tests.

## 14. Dual clean-checkout verification

Both worktrees were detached, clean checkouts at:

```text
191f706a9e0d5be35d1401e70fbede7a1a5adc0e
```

Base-only dependencies were installed from `requirements.txt` and
`requirements-dev.txt`. The complete base-only suite result was:

```text
2519 passed, 35 skipped in 255.71s
```

The skips are the expected unavailable CAD/PDF optional-toolchain cases.

All-extras dependencies were installed in the documented two stages: base/dev,
then `pip install --require-hashes -r requirements-cad.txt -r
requirements-pdf.txt`. Combining unpinned base requirements with hash-pinned
extra files in one pip invocation correctly failed because pip enables hash
mode globally; no dependency contract was changed to conceal that behavior.

The complete all-extras suite result was:

```text
2554 passed in 281.75s
```

After the suites, both worktrees reported empty `git status --short`, passed
`git diff --check`, and resolved to the exact reviewed HEAD above.

## 15. Historical replay and byte preservation

Every accepted explicit pre-BH membership replayed with its exact unchanged
revision and all twelve BH indexes empty:

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

The current demo ledger verification is:

```text
record count: 29
BRG count: 0
BHD count: 0
BHW count: 0
revision: mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

All 29 existing model-record files remain byte-identical to their frozen
hashes. The accepted VPA remains:

```text
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49
stored-file SHA-256:
95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e
```

Artifacts regenerated without mutation at:

```text
PT artifact bytes: 33855
PT artifact SHA-256:
53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8

VP artifact bytes: 17824
VP artifact SHA-256:
a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3
```

No canonical bytes, record ID, schema, revision, membership constant, binding
revision, temporal occurrence, source evidence, structural evidence, PT
identity, or VP identity changed.

## 16. Architecture and exclusions

The kernel continues to import only `backend.system_identity`, Pydantic, and
the standard library. It imports no behavior evaluator, model state, temporal
state, identity binding, semantic compatibility, constraint evaluation,
source interpretation, data source, CAD, PDF, or structural-evidence module.

Slice A added no:

- `ModelQueries` behavior method;
- query or authoritative result contract;
- `backend/behavior_evaluation` package;
- numeric parsing or comparison;
- source selection or observation discovery;
- model-state composition;
- behavior ledger, store, revision, projection, cache, or database;
- committed BRG, BHD, BHW, variable, VSP, VSM, binding, or temporal record;
- port, VPA, input/output, signal, topology, flow, influence, causality,
  control, compatibility, safety, diagnosis, or recommendation meaning.

## 17. Known limitations and remaining slices

BH-001 v1 remains deliberately narrower than general engineering behavior. It
registers and declares only an exact numeric-equality relation between two
role-free variables. Slice A does not say whether a declaration is currently
corroborated or conflicted at a public query boundary, and it does not evaluate
any observation.

Remaining owner-gated work is unchanged:

```text
Slice B: four read-only kernel queries and authoritative result contracts
Slice C: separate evidence-gated read-only evaluator
Slice D: separately approved bounded synthetic declaration-only demonstration
```

Registration is permanent; changing the pair or rule family requires a new
behavior identity. Store validation retains the accepted whole-revision cost
and single-writer assumptions. No behavior truth is inferred from common
ownership, names, hierarchy, ports, VPA, topology, semantics, constraints, or
observations.

Genuine unresolved owner questions for Slice A: none. Owner acceptance is the
only remaining Slice A gate.

## 18. Final repository state

Immediately before adding this report, the reviewed worktree was clean on
branch `bh001`; `git diff --check` passed; `main` and `origin/main` remained at
the accepted base; and `bh001` was six commits ahead and zero behind. The
completion-report commit adds documentation only. Nothing was pushed or
merged.

BH-001 Slice A implemented and adversarially reviewed; awaiting owner acceptance.
