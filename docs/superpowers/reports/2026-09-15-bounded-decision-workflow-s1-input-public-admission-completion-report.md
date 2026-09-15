# Bounded decision-workflow S1 input/public-admission completion report

Date: 2026-09-15

Status: S1 implemented and verified; owner acceptance required; S2-S7 not started

## 1. Authority and administrative sequence

The resumed work started on branch `brc-exp001` at
`a9473d5d4ffaa4276b29374466f6d1079cd0397f`. Existing authorization commit
`44600982e6ec0e2e2dd4759d0d24510f8c81da37` authorizes S1 only. The frozen
[blocker report](2026-09-15-bounded-decision-workflow-s1-input-public-admission-blocker-report.md)
remains byte-identical at
`d7255969245010f4f41b922558e4a741993169bd13687110c52e67c559b0652c`.

The work produced these small commits:

| Commit | Scope |
| --- | --- |
| `1555cc8` | Preserve the original package/manifest and split/fix the OBS-3 fixture commitments. |
| `feb7227` | Add maintained S1 input, request-contract and public-admission code. |
| `79b3ea6` | Add the initial focused S1 test suite. |
| `0485b3d` | Make the OBS-2 null producer's nullable numeric specification explicit. |
| `160bfc5` | Exercise all five public unavailable admission paths. |

`feb7227` is the implementation-source HEAD; `160bfc5` is the exact tested
implementation/test HEAD before this administrative report. No backend file was
changed.

## 2. Fixture contradiction resolution

The [correction report](2026-09-15-bounded-decision-workflow-obs3-decimal-fixture-correction.md)
records the field-level changes and independently reproduced precedence. Its
current corrected package has SHA-256
`199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4` and its
manifest has SHA-256
`5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.
All 38 content-addressed objects recovered with their declared byte counts and
digests; the corpus has 69 variants.

The old package/oracle bytes remain at the clearly named
`pre-obs3-decimal-correction` paths with their original commitments
`0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`
and `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`.
The accepted baseline request/snapshot also remain unchanged.

Actual diagnostic precedence is:

1. bounded canonical request/snapshot decoding;
2. snapshot commitment comparison;
3. authoritative public `StateClassificationResult.model_validate`;
4. application binding and admission predicates; and
5. public decimal reparse/equality defense.

Accordingly, the original stale pair returns
`SNAPSHOT_COMMITMENT_MISMATCH`; the matching-enclosure hostile decimal returns
`PUBLIC_RECONSTRUCTION_REFUSED`. The wrong-revision and forged-result fixtures
also carry matching enclosing commitments before reaching public reconstruction.
Request-only substitutions reach `OBSERVATION_BINDING_MISMATCH`. A serialized
public result cannot reach the decimal mismatch branch under the current public
equality invariants. The direct defense test remains scoped to the already
reconstructed internal admission seam.

The fixture sweep also identified that JSON null against the baseline
non-nullable specification stops at `value_shape_not_satisfied`. The corrected
OBS-2 producer recipe now explicitly uses a nullable numeric public
specification, and independently produced results reach
`numeric_value_absent`. No remaining S1 semantic contradiction was found.

## 3. Maintained S1 capability

Maintained source now exists only in
`applications/bounded_decision_workflow/`. It provides:

- one explicit 11-field `WorkflowRequest` and closed nested S1 contracts;
- canonical compact UTF-8 JSON admission with duplicate-key, non-finite,
  noncanonical and extra-field refusal;
- immutable build-owned wire/node/depth/string/reference/cardinality limits,
  exact prepared counting semantics, and caller limits that may only tighten;
- SHA-256 snapshot commitment comparison before public reconstruction;
- reconstruction solely through the public `StateClassificationResult` export;
- exact question, condition, evaluation, candidate, identity, context, cutoff,
  semantic token, revision, source locator, subject and staleness joins;
- decimal admission solely through public `parse_observed_decimal`;
- distinct typed current-condition and `admitted|unavailable` observed-value
  results, without a caller numeric fallback; and
- canonical reserialization of a complete admitted request/snapshot pair without
  importing preparation artifacts.

Premise envelopes retain their application authority and validate their own
canonical commitments. They are not backend records. The application imports
only supported exports from `backend.state_classification`,
`backend.constraint_evaluation` and `backend.model_kernel`; it opens no private
store and bypasses no lower validation.

This slice deliberately has no `__main__.py`. It does not implement or claim raw
projection, target/policy calculation, decision review, retention, verify,
replay, CLI behavior, command-level acceptance or release readiness.

## 4. Verification and red/fixed evidence

The approved isolated CPython 3.13.11 environment at
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001`
was used without installing or changing dependencies. Before filesystem-dependent
test setup, `findmnt` reconfirmed the persistent workspace is ext4 on `/dev/sdc`.
Only dedicated paths beneath `test-workspaces/` were used; runtime `inputs/`,
`results/`, dependency artifacts and provisioning evidence were not changed.

Final focused result at `160bfc5`:

    20 passed in 10.63s

That suite covers OBS-1, all five OBS-2 public-producer paths, all nine corrected
OBS-3 variants, OBS-4 conversion refusal and interpreted-unit success, exact
diagnostic fields/order, valid twins, request/premise integrity, canonical example
round-trip, build and caller-tightened S1 limits, public import isolation, and
recovery of all current and historical fixture objects.

The affected existing public-contract regression selection collected 213 tests
and completed successfully. It covered state-classification public and
preservation contracts, constraint decimal/integrity contracts, semantic remaining
matrix and observation compatibility. Its first attempt recorded 97 passes and
116 setup errors because pytest's base parent did not exist; no assertion failed.
After exclusively recreating the dedicated `test-workspaces` parent, the unchanged
selection exited successfully with all 213 tests passing.

Two ordinary red/fixed events were retained in the execution record:

- the first focused run had 16 passes and one test-only import-isolation assertion
  that also matched the application's own module path; narrowing it to backend
  private import strings produced 17 passes; and
- the expanded producer run exposed the incomplete nullable-null fixture premise;
  after the correction described above, the final 20-test suite passed.

`git diff --check`, exact staged-scope inspection, canonical-JSON/no-trailing-newline
checks, frozen/historical digests and public fixture recovery passed. Disposable
scripts in `/tmp` are not retained as application code and are removed after this
report's recovery checks.

## 5. Preservation, limitations and acceptance gate

The original blocker report, corrected and historical package evidence, accepted
design/review material, authoritative ledgers and fixtures, and unrelated untracked
artifacts were preserved. The checkout remains on `/mnt/d`; the approved ext4
workspace remains provisioned. No physical operation, dependency change, backend
extension, ADR, push, merge or history rewrite occurred.

S1 establishes maintained strict input/public observation admission within the
approved synthetic application profile. It does not establish empirical accuracy,
source authentication, projection correctness, policy correctness, retained bundle
durability or a usable command. Owner acceptance of this S1 scope is the next gate.
Authorization of S2, S3, S4, S5, S6 or S7 must be separate.

END OF BOUNDED DECISION WORKFLOW S1 INPUT/PUBLIC-ADMISSION COMPLETION REPORT
