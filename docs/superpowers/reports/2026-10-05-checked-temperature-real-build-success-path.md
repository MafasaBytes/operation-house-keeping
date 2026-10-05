# Checked-temperature Gate 1 real-build success path

Date: 2026-10-05. Status: **Gate 1 integration evidence**. This is the remaining
Gate 1 integration check. It is not Gate 2 and not acceptance.

No production code, backend, dependency or contract was changed. Nothing was
staged or committed, and there was no push, publication, history operation or
full suite. Work stops for test-only commit review and the separate Gate 1
acceptance decision.

## 1. Checkpoint

| Item | Value |
|---|---|
| Source checkpoint (HEAD) | `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8` (verified) |
| Scoped-commit report | `docs/superpowers/reports/2026-10-05-checked-temperature-scoped-commit-and-clean-build.md` `60e47562…34bb` |
| Committed manifests (from `HEAD:`; identical to the worktree) | original `c3de4cb9`, v2 `e7dbccec`, v3 `1a9eccbd`, v4 `9e0afa32`, C1 `791b4035`, C2 `6252a2da` |
| Unchanged | `.gitignore`, `bounded_pytest_runner.py`, all earlier bundles, pins and reports |

## 2. Build handling

The maintained identity's cleanliness rule (`measurement_build.identity`) is:

`git status --porcelain --untracked-files=all -- applications backend` must be
empty, plus CPython 3.13, the exact lock and exact installed distributions. Its
source manifest covers only the tracked `.py` files under `applications/` and
`backend/`, plus the lock.

**Test-file state, recorded honestly:**

- The new test file `tests/checked_temperature/test_real_build_success.py` is
  **untracked** and lies outside both inputs.
- `applications/` and `backend/` were clean before and after the launch, with
  zero status entries.
- The identity was therefore legitimately generated. Nothing was bypassed.

## 3. Real executable identity (approved environment)

Recorded by the test at
`<ws>/launch-19/tmp/real-build0/real-build-identity.json`, where
`<ws>` = `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd`.

| Field | Value |
|---|---|
| `ct.build.v1` SHA-256 | `d81acac6f40f97670c23d08df15b3d1f568df5433bdb8ac3b55961f33d27f23c` (28,604 B) |
| checkpoint | `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8` (asserted equal to HEAD) |
| interpreter | `cp313-bdw001/bin/python`, CPython 3.13.11; executable SHA-256 `47f615b1…0264` (32,003,680 B) |
| dependency lock | `7c87f0d7…0817` |
| source manifest | 179 entries |
| contract editions | schemas `43c2af0b…`, policy edition `46df039b…`, catalogue `ct.conditions.v2`, calculator `ct.calculator.v1` |

`TestDoubleBuild` was **not** used in this module. The test policy, a test-only
fixture, permits exactly `[d81acac6…]`. Each command subprocess recomputes the
identity itself, and every bundle's `build.json` equals the recorded identity
byte-for-byte.

## 4. Commands and outcomes (launch 19: 6 passed)

Every command is
`<cp313-bdw001 python> -m applications.bounded_decision_workflow <command> --expected-request-pin <R> --expected-authority-pin <A> …`,
run from the repository root with `PYTHONDONTWRITEBYTECODE=1`.

| # | Command | Outcome asserted |
|---|---|---|
| 1 | `checked-selection-evaluate --request … --objects-dir … --output-dir SEL` | Exit 0, stderr empty, exact receipt. Ranked: T1 `low{H2} gap{} high{H1}`, `best = [T1]`, `post_measurement_elimination_guaranteed = false`. 9 files; build is the real identity; policy permits only it. |
| 2 | `checked-selection-verify --bundle SEL` | Exit 0, stderr empty, exact report (`derivation_checked`, `applicability_policy_checked`, `downstream_result_not_replayed`) |
| 3 | `checked-selection-replay --bundle SEL --output-dir SEL-REPLAY` | Exit 0. Closure, derivation, applicability, result, trace, build and policy are byte-identical. `replay_of` names the SEL manifest. |
| 4 | `checked-reassessment-evaluate … --prior-bundle SEL --output-dir REA` | Exit 0. CO1 construction with the **coherent later synthetic evidence chain** (amendments C1/C2). Interval `[119/2, 121/2]`, branch `high`; H1 `compatible_under_declared_model`, H2 `conditionally_incompatible`; `one_compatible`. |
| 5 | `checked-reassessment-verify --bundle REA` | Exit 0, exact report including `prior_material_checked` |
| 6 | `checked-reassessment-replay --bundle REA --output-dir REA-REPLAY` | Exit 0, byte-identical records, `replay_of` |
| 7 | `checked-selection-evaluate` (unpermitted twin: otherwise valid, but the policy permits a different 64-hex digest) | Exit 3, stdout empty. stderr exactly `{"code":"BUILD_NOT_PERMITTED","exit_class":3,"schema":"ct.diagnostic.v1","stage":5,"target":"/build"}`. No output directory. |

**No new claims.** Each check below is asserted:

- `ranking = not_reassessed`;
- `adoption = derived_not_adopted`;
- the presentation states that the actual cause is not established;
- no `ct.adoption.v1`, `ct.reassessment.v1` or `ct.closure.v1` closure member;
- the result evidence is not the baseline evidence.

The later chain is a declared-time synthetic chain, not a physical acquisition.

## 5. Retained evidence (`<ws>/launch-19/`)

| Item | Path under `tmp/` | Manifest SHA-256 |
|---|---|---|
| Selection bundle | `real-selection0/SEL` (201,455 B) | `230faf8f203d8ed5407a5b4e3c5b4abd19b53e9d75ea1777e1b41bba3bf3409b` |
| Selection replay | `test_selection_verify_and_repl0/SEL-REPLAY` | `9f9928e2c791cc75924849913f0bb97f04d41ec3cf414516844af112ce72bc0a` |
| Reassessment bundle | `real-reassessment0/REA` (409,107 B) | `42c834d590de52afa38ad0c332bf5721e6524cd6ffc0d37bcb895cdcd9344610` |
| Reassessment replay | `test_reassessment_verify_and_r0/REA-REPLAY` | `18651c972b1573454a8fc27b0e6ab89fa4d4e59bf0ccbcc42e4e9b9d27ea0a81` |
| Inputs | `real-selection0/in`, `real-reassessment0/in`, `test_unpermitted_build_twin_th0/in` | — |
| Later-chain stores | `later-chains0/chain-60-2026-10-05T090100Z` | — |

Also retained: the launch log (`<ws>/launch-log.jsonl`) and `launch-19/stdout.txt`.

## 6. Evidence attribution (kept separate)

| Class | Scope |
|---|---|
| **Real-build evidence (this report)** | Launch 19, identity `d81acac6…` |
| **Clean-build evidence** | Launches 17–18 at `8414f4d`: 221 legacy tests and 198 checked tests passed |
| **Test-double evidence** | Every in-process bundle in launches 01–16 and 18 (labelled `TestDoubleBuild`) |
| **Historical failures** | Launches 01, 02, 05, 11 and 13: application, fixture and harness defects, each fixed and documented. Launch 07: 9 identity-dependent legacy failures in the then-uncommitted tree, superseded by launch 17. All retained. |

No production defect was found in this step.

## 7. Cumulative accounting (not reset)

**Before launch 19:** 3,724 files and 719 counted directories (21,549,055 logical
bytes).

**Launch 19 delta:** +1,816,167 logical bytes, +218 files.

**Launches: 19 of 40 used, 21 remain.**

| Measure | Used now | Allowance |
|---|---:|---:|
| Logical bytes | 23,375,300 | 536,870,912 |
| Physical bytes | 39,288,832 | — |
| Files | 3,942 | 20,000 |
| Directories | 700 real | 5,000 |

Nothing was deleted.

## 8. Proposed test-only commit scope (for review; not staged)

| Path | Bytes | SHA-256 | State |
|---|---:|---|---|
| `tests/checked_temperature/test_real_build_success.py` | 10,862 | `439fab0a5827691fe1b8b0daf4fe563eefa5b61996423cf46d4bea7b55ca2bab` | new, untracked |

No other file changed: `fixtures.py`, `conftest.py` and every other test are
identical to `8414f4d`. Optionally, this report can be added as documentation.

The commit would be test-only and outside `applications/`/`backend/`, so the
source manifest, environment and contract editions inside the identity are
unchanged. The identity's `checkpoint` field is the HEAD at generation time,
however. After any new commit, the next generated identity therefore has a new
checkpoint and a new digest, and `d81acac6…` remains the record for `8414f4d`.

The test computes the identity at run time and pins the policy to it, so it stays
valid after such a commit. Historical bundles keep their recorded `d81acac6…`
build.

END OF REAL-BUILD SUCCESS-PATH REPORT
