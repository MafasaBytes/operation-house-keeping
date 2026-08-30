# BH-001 Slice D Pre-Append Rehearsal Gate Report

Date: 2026-08-30

Historical stop status: blocked before candidate generation by a public-identity-minter discrepancy

Current status: owner-resolved; minter implementation and disposable rehearsal
resumption authorized, authoritative append prohibited

Branch: `bh001`

Accepted Slice C HEAD: `8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`

Administrative acceptance HEAD: `a619ed14d36aeb508e4db8602adbbdce4b1b4e2d`

## 1. Outcome

The Slice D pre-append gate cannot be completed under the presently authorized
procedure. The repository exposes `mint_behavior_anchor()` but has no public
`mint_variable_anchor()`. Slice D requires one new `VariableRegistration`, and
the owner-fixed candidate procedure requires the proposed opaque anchor
identities to be produced by public identity minters.

No candidate identity was minted. No candidate record was built. No disposable
or authoritative `ModelStore` was opened for append. No disclosure artifact
was generated. This is a fail-closed stop before the first irreversible
candidate choice and before any ledger write.

The blocker is confined to the Slice D candidate-identity gate. It does not
invalidate accepted Slices A, B, or C.

## 2. Authoritative inputs and read verification

The three owner-supplied artifacts were read completely before the
administrative step or rehearsal analysis. Their content at the accepted Slice
C commit was verified directly from Git:

| Artifact | Verified SHA-256 |
|---|---|
| `CLAUDE.md` | `51c4712ec708ca9310727b06436aad497e821ebd2d4bc14e47ad9263607410be` |
| `docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md` | `a5e0c8abb0cb96f432f5ad5b69298f12c3ea718a71b57f6872e22179dba70310` |
| `docs/superpowers/reports/2026-08-30-bh001-slice-c-completion-report.md` | `f7bdc664e4d9c50a7ba331e1e71cf986da096af05baa458fd2723b7540d8eaf0` |

The accepted commit resolved exactly to:

```text
8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521
```

Verification used the accepted commit objects rather than the subsequently
amended working copies:

```text
git show 8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521:CLAUDE.md | sha256sum
git show 8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521:docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md | sha256sum
git show 8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521:docs/superpowers/reports/2026-08-30-bh001-slice-c-completion-report.md | sha256sum
```

## 3. Slice C owner-acceptance administration

Slice C owner acceptance was recorded in a separate documentation commit as
required:

```text
a619ed14d36aeb508e4db8602adbbdce4b1b4e2d
docs: record owner acceptance of BH-001 Slice C
```

The commit changes only status documentation and exact documentation/status
assertions. It contains 72 insertions and 54 deletions across these 13 files:

```text
CLAUDE.md
backend/behavior_evaluation/README.md
backend/model_kernel/README.md
docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md
docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md
docs/superpowers/plans/2026-08-29-bh001-slice-b-implementation-plan.md
docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md
docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md
docs/superpowers/reports/2026-08-30-bh001-slice-c-completion-report.md
docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
tests/behavior_evaluation/test_documentation.py
tests/model_kernel/test_behavior_query_contracts.py
tests/model_kernel/test_behavior_slice_c_resolution_documentation.py
```

The focused documentation/status assertions passed:

```text
10 passed in 2.03s
```

The status now records Slices A, B, and C as owner accepted at the exact
accepted Slice C HEAD, authorizes only the Slice D pre-append rehearsal gate,
and states that the authoritative append has not started.

## 4. Authorized candidate procedure

The owner clarified UUID4 identity handling precisely:

1. invoke the public minters once in a disposable candidate-generation step;
2. record the resulting anchors as non-authoritative candidates;
3. freeze those exact serialized anchors;
4. reconstruct them through public contracts in two independent disposable
   rehearsal roots;
5. use only public builders, canonical serialization, `ModelStore`, replay,
   and query APIs thereafter; and
6. judge determinism from identical frozen inputs, not from repeated UUID4
   minting.

That clarification completely resolves UUID4 nondeterminism for the existing
behavior minter. The present blocker is narrower: there is no public minter to
perform the required one-time allocation of the new variable identity.

## 5. Exact repository discrepancy

`backend/system_identity/minting.py` declares only:

```text
mint_behavior_anchor
mint_constraint_anchor
mint_port_anchor
```

Its module documentation states that existing `EntityAnchor` and
`VariableAnchor` values have no minter there. The behavior minter creates a
`bhv_` identity from `uuid4().hex`, exactly as expected by the owner-fixed
freeze-and-replay procedure.

`backend/system_identity/__init__.py` imports and publicly exports the same
three minters and does not export `mint_variable_anchor`. A repository-wide
search found no function or public symbol named `mint_variable_anchor`.

The public `VariableAnchor` contract accepts an already chosen `var_` identity,
owner identity, namespace, display name, and optional role name. Contract
construction validates a supplied identity; it does not allocate one.

The public model-record builder likewise accepts already selected anchor
content. It derives the content-addressed `vrg_` record identity, but it does
not mint the opaque `var_` identity. Therefore neither public contract
construction nor `build_record()` satisfies the explicit public-minter step.

## 6. Why no workaround was used

The following technically possible actions were rejected because each would
silently reinterpret or broaden the authorization:

- constructing `VariableAnchor(anchor_id="var_" + uuid4().hex, ...)` directly;
- calling `uuid4()` privately in rehearsal code;
- transforming a `bhv_`, `con_`, or `prt_` identity into a `var_` identity;
- importing or copying a test helper;
- monkeypatching a public minter;
- hand-writing a fixed `var_` identity;
- adding `mint_variable_anchor()` to production code; or
- treating `build_record()` as an identity minter.

The first six bypass the required public-minter path. Adding a production
minter changes the accepted public identity surface and exceeds the present
rehearsal-only authorization. The final alternative confuses opaque anchor
identity with content-addressed ledger-record identity.

No alternative candidate was minted, so the owner's prohibition on reminting
after the first candidate remains fully preserved.

## 7. Candidate and artifact fields

No candidate exists, so none of the following values can honestly be reported:

| Required gate value | Status |
|---|---|
| New variable anchor and semantic name | not generated |
| Behavior anchor and semantic name | not generated |
| Canonical VRG content and `vrg_` identity | not generated |
| Canonical BRG content and `brg_` identity | not generated |
| Canonical BHD content and `bhd_` identity | not generated |
| Three stored-file SHA-256 values | not generated |
| Explicit 32-record membership | not generated |
| Prospective 32-record model revision | not generated |
| Behavior-query disclosure | not executed |
| Evaluator disclosure | not executed |
| Artifact byte count and SHA-256 | not generated |
| Two-run byte comparison | not executed |

Inventing placeholders would defeat the purpose of the owner gate. The exact
values must be derived after a compliant one-time candidate allocation, then
held fixed across both rehearsals.

## 8. Binding-seam status

The existing cross-layer binding seam remains green. A focused read-only audit
covered the complete existing seam and confirmed the accepted model remains a
29-record membership. Because no new variable was minted or registered, there
is not yet an owner-pinned exception to test.

The required future checks remain unchanged after the identity issue is
resolved:

- the proposed new variable must be the sole exact `(variable_anchor_id,
  variable_registration_record_id)` exception;
- every pre-existing registered anchor must continue to match the accepted
  binding declarations exactly;
- a second undeclared variable must fail;
- a substituted or divergent candidate anchor or registration must fail;
- binding files, memberships, revisions, and hashes must remain unchanged; and
- direct model-state disclosure must report `binding_declaration_absent` for
  the candidate variable.

No binding file, membership, revision, or record was changed during this gate.

## 9. Baseline preservation evidence

The authoritative demo ledger still contains exactly 29 JSON records. Its
accepted revision remains:

```text
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

The sorted aggregate over the 29 predecessor file-hash lines is:

```text
3a9e9ff0f6988dc1a19fddee97715d19e8d09dac15fa3a79d858f0e428e5ebb7
```

This aggregate is computed as:

```text
sha256sum models/demo-printer/records/*.json | LC_ALL=C sort | sha256sum
```

The accepted VPA file remains:

```text
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49
SHA-256 95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e
```

Focused replay, seam, and artifact-preservation verification ran:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/model_kernel/test_cross_layer_seam.py \
  tests/model_kernel/test_demo_model.py::TestCommittedLedger::test_golden_revision_and_membership \
  tests/model_kernel/test_demo_vp001.py::test_fixture_scope_and_accepted_pt_artifact_are_unchanged \
  tests/model_state/test_demo_vp001.py::test_disclosure_artifact_is_deterministic_complete_and_path_free \
  -q
```

Result:

```text
9 passed in 15.60s
```

This pins the existing cross-layer seam, accepted model membership and
revision, PT preservation, and deterministic VP artifact. The accepted
artifact identities remain:

```text
PT artifact SHA-256 53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8
VP artifact SHA-256 a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3
```

The audit used `PYTHONDONTWRITEBYTECODE=1`, disabled the pytest cache provider,
and wrote test temporaries only outside the repository.

## 10. Historical replay and evaluator status

The existing explicit 9-, 10-, 11-, 14-, 16-, 18-, 28-, and 29-record
memberships were not edited. No directory-derived historical membership was
introduced. The focused historical model test remains green at the accepted
29-record revision.

No proposed 32-record history exists yet, so no behavior query or evaluator
result was fabricated. In particular, this report does not claim a
`not_executed` result without the candidate model membership and two explicit
selectors. After resolution, the evaluator must still disclose both
participant results, exact refusal rows, cohort admission, execution
`not_executed`, and `computed_relation=None`. It must preserve independently
available evidence for the existing variable and honestly disclose missing
binding, specification, semantic, interpretation, and temporal evidence for
the synthetic participant.

`equal` and `different` remain confined to the already accepted disposable
Slice C test worlds.

## 11. Specialist findings

The repository's backend, test, and adversarial reviewers inspected the
corrected gate independently and agreed on the blocker:

- Backend review confirmed no compliant alternate public API exists. It also
  verified that, once identities are legitimately fixed, public
  `build_record()`, `ModelStore.append()`, explicit replay, Slice B queries,
  and Slice C evaluation can support the bounded rehearsal without requiring
  VSP, VSM, port, VPA, binding, interpretation, or temporal fixture writes.
- Test review confirmed the missing minter by public-export and repository-wide
  search, ran the nine-test preservation audit, and defined the required
  negative binding-seam controls and two-run comparisons for the resumed gate.
- Integrity review confirmed that direct construction, private UUID allocation,
  prefix substitution, or a newly implemented minter would exceed the current
  authorization. It recommended keeping run-comparison evidence outside the
  canonical artifact and excluding temporary paths, mtimes, directory order,
  runtime clocks, object representations, and reminted UUIDs from artifact
  content.

All specialists were read-only. None edited files, minted candidates, built
records, opened a store for append, or generated an artifact.

## 12. Mandatory demonstration disclaimer

The candidate artifact was not generated. When the gate resumes, it must carry
this exact accepted disclaimer:

> This is an illustrative synthetic BH-001 exact-numeric-equality declaration.
> It does not describe or claim any real printer physics, target, command,
> response, control loop, wiring, signal path, flow, causality, simultaneity,
> correctness, safety, health, real-machine behavior, or operating condition.
> Shared ownership, names, topology, VPA associations, semantic compatibility,
> constraints, and observed correlation did not create this declaration.

It must additionally state that `not_executed` is an honest admission result,
not evidence that the declared relation is false.

## 13. Exact owner resolution required

One identity-allocation decision is required before work can resume. The lead
recommendation is a separately owner-gated, narrowly scoped addition of a
public `mint_variable_anchor()` that returns the existing `VariableAnchor`
contract with an opaque UUID4-backed `var_` identity. The API, tests, exports,
and architecture impact should be owner-approved before implementation. After
that addition, the minter would be invoked once, and its serialized result
would be frozen across both disposable rehearsals exactly as already directed.

Alternatively, the owner may explicitly amend this one gate to authorize a
single external UUID4 allocation followed by direct public `VariableAnchor`
construction and full public-contract reconstruction. That option avoids a
production change but is not compliant with the currently accepted
public-minter-only wording.

No decision is needed about behavior-anchor UUID4 reproducibility: the current
owner instruction already correctly defines determinism as identical output
from identical frozen candidate inputs, not identical output from repeated
minter calls.

Until one variable-identity path is authorized, no candidate anchor, record,
membership, revision, query disclosure, evaluator disclosure, or artifact hash
can be produced honestly.

## 14. Scope and Git status

At the stop point:

- branch: `bh001`;
- HEAD: `a619ed14d36aeb508e4db8602adbbdce4b1b4e2d`;
- one authorized administrative acceptance commit exists after Slice C;
- this report is the only post-commit working-tree file;
- no implementation or test code was added;
- no fixture, ledger, binding, interpretation, temporal, source, structural,
  PT, VP, or BH artifact path was mutated;
- no candidate identities or records exist;
- no authoritative or disposable append occurred; and
- no push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
  performed.

The working tree was intentionally stopped with this report uncommitted,
pending owner review of the discrepancy and identity-allocation choice.

## 15. Owner resolution

Status: resolved by owner decision; rehearsal resumption authorized

The original finding remains preserved above: the repository had no public `mint_variable_anchor()` and a compliant candidate could not be allocated under the then-authorized procedure.

Owner resolution: add the narrowly scoped public `mint_variable_anchor()` API, commit it green before candidate allocation, then resume only the disposable pre-append rehearsal.

The approved function is keyword-only, calls standard-library `uuid4()` once,
uses `uuid4().hex` with the `var_` prefix, and returns the unchanged public
`VariableAnchor`. Add `mint_variable_anchor` after `mint_port_anchor` in the
existing minter export sequence. It adds no entity minter, storage, I/O,
authority, registration, binding, persistence, deterministic seed, injected
randomness, or identity meaning.

No candidate may be minted before the minter commit is green. After that
separate commit, invoke each public minter exactly once, serialize both anchors
immediately as non-authoritative candidates, and never invoke either minter
again. Reuse the frozen public-contract inputs in both independent disposable
ledger roots; each ledger has exactly one behavior lineage root. The authoritative
append remains prohibited until the exact rehearsal outputs receive owner
approval.

END OF BH-001 SLICE D PRE-APPEND REHEARSAL DISCREPANCY REPORT
