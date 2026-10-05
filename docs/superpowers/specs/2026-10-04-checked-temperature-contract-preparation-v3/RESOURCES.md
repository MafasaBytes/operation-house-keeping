# Resources v3: measured, analytical, engineering and estimated

Every number in this file is labelled with one of five classes:

- **Measured:** sizes of existing retained material, taken statically. No code
  was executed.
- **Analytical:** follows from fixed profile limits alone.
- **Engineering:** a proposed refusal ceiling.
- **Engineering-derived:** arithmetic over engineering ceilings.
- **Estimate:** an unmeasured expectation for the new route. It is never a
  maximum.

The original package called several hand counts "analytical maxima"; the v2 map
records the relabelling. v3 changes are listed in `CORRECTIONS.md`:

- §3 adds `retained_selection_bytes` and re-derives the reassessment rows;
- §4 is recomputed for the 179-invocation matrix.

## 1. Measured (unchanged from the predecessor; 2026-10-04)

Source: the 2026-10-01 experiment outputs, read only.

| Item | Bytes |
|---|---:|
| NM selection-analogue closure: 24 members decoded / file encoded | 144,491 / 196,480 |
| NR reassessment-analogue closure: 43 members decoded / file encoded | 309,593 / 419,391 |
| Largest object (public evidence, `nm.evidence.v1`) | 86,313 |
| Build record | 27,479–27,632 |
| Results / traces / manifests | 5,047–15,967 / 6,298–31,134 / 970–972 |
| Sparse experiment checkout (applications, backend, tests, docs/next-measurement) | ≈ 10.3 MB |

The measured encoded/decoded ratio is 1.36 for both closures. That is consistent
with base64 (4/3) plus per-member JSON overhead.

## 2. Analytical (fixed profile only)

| Quantity | Derivation | Value |
|---|---|---:|
| Derivation cells | 2 hypotheses × (3 + 2) outcomes | 10 |
| Required claims per request | T1: 4 conditions; T2: 2 conditions; one phase | 6 |
| Branches per score | T1: 3, T2: 2 | ≤ 3 |

**Hand-count estimates.** These are not analytical maxima and are unproved until
implementation.

| Quantity | Estimate | Engineering allowance |
|---|---:|---:|
| Rational operations | < 200 | 1,024 |
| Trace entries | ≈ 140 | 512 |

## 3. Engineering and engineering-derived ceilings

These match `policy.json#/limits`.

| Limit | Value | Class | Derivation |
|---|---:|---|---|
| object_bytes | 196,608 | engineering | measured 86,313 × ~2.3 |
| selection_unique_objects | 192 | engineering-derived | sum of per-kind caps (explanations 2, model 1, plan 1, policy 1, request 1, authority 1, claims 24, declarations 32, items 32, contents 32, reviews 64, baseline evidence 1) |
| reassessment_unique_objects | 400 | engineering-derived | **includes the entire prior selection closure** (≤ 192, including the prior evaluation authority) + carried prior computed records 7 (invocation, selection, derivation, applicability, trace, build, bundle manifest) + descriptor 1 + own objects 195 (execution target and both authorities included; no deduplication assumed) = 395. v2's stated sum was 388 (and its policy text said 389). |
| selection_closure_decoded_bytes | 1,048,576 | engineering | about 7× the measured selection analogue |
| selection_closure_file_bytes | 1,474,560 | engineering-derived | ⌈1,048,576 × 4/3⌉ + 192 × 160 B = 1,428,822 |
| reassessment_closure_decoded_bytes | 2,621,440 | engineering-derived | prior closure 1,048,576 + carried prior computed records at their file caps 491,520 + descriptor 32,768 + own 1,048,576 = 2,621,440. Only the total is enforced. |
| retained_selection_bytes | 32,768 | engineering | analytical schema bound 23,472 B (192 prior member references of the longest kind, 7-digit closure length) |
| reassessment_closure_file_bytes | 3,670,016 | engineering-derived | ⌈2,621,440 × 4/3⌉ + 400 × 160 B = 3,559,254 |
| Other files | invocation 16,384 · derivation 65,536 · applicability 131,072 · result 65,536 · trace 131,072 · build 65,536 · policy 16,384 · manifest 16,384 | engineering | measured analogues far below |
| bundle_bytes_selection | 2,097,152 | engineering-derived | 1,474,560 + 507,904 = 1,982,464 |
| bundle_bytes_reassessment | 4,194,304 | engineering-derived | 3,670,016 + 507,904 = 4,177,920 |

Each ceiling refuses before work proceeds. A ceiling is not a measured maximum of
real bundles. The legacy `APPROVED_LIMITS` are not inherited.

**New-route bundle estimates** (unmeasured; for context only):

- **Selection:** about 120 KB decoded closure (one public evidence object plus
  small authored records), about 165 KB encoded, plus about 70 KB of other files.
  Total about 235 KB.
- **Reassessment:** about 400 KB decoded (v2's 300 KB plus about 100 KB of
  carried prior computed records and the descriptor, scaled from the measured
  analogues in §1), about 545 KB encoded, plus about 70 KB. Total about 615 KB.

## 4. Gate 2 storage, derived from the witness matrix

**Bundle and log counts** (from `witnesses.json`). The counting rule reproduces
v2's figures (69 / 17 / 29 / 39) on the v2 matrix:

| Item | Count |
|---|---:|
| Application invocations | 179 |
| Bundle-producing selection invocations (completing evaluate and replay) | 69 |
| Bundle-producing reassessment invocations | 20 |
| Refusing evaluate/replay invocations | 43 |
| Verify invocations (write no bundle) | 47 |
| Harness-mutated copies: selection (IN2, IN3/IN4, IN5, CL9) | 4 |
| Harness-mutated copies: reassessment (CL2–CL7) | 6 |

Refusals are contractually pre-publication: stages 1–5 and 7 run before any
output directory exists, so they write nothing.

**Cap-based upper bound for the verification launch** (engineering-derived; a
true bound only if the caps hold):

| Component | Logical bytes | Derivation |
|---|---:|---|
| Selection bundles and copies | 153,092,096 | 73 × 2,097,152 |
| Reassessment bundles and copies | 109,051,904 | 26 × 4,194,304 |
| Retained stdout/stderr | 46,923,776 | 179 × 262,144 joint stream cap |
| Workspace sparse checkout | 10,485,760 | measured analogue ≈ 10.3 MB |
| **Total** | **319,553,536** | |

- **Files:** about 4,249, made up of 99 bundles × 9 files, 179 × 2 logs and
  about 3,000 checkout files.
- **Directories:** about 813. This is v2's 778 plus 10 bundle directories plus 25
  invocation directories.
- **Physical:** logical + 4,096 per file + 8,192 per directory, about
  343,617,536.

**Estimate** (unmeasured): 73 × 235 KB + 26 × 615 KB ≈ 33 MB of bundles, plus
logs and checkout.

**Retained failures and coexistence:**

- Replays keep the source bundle and write a new one; both are already counted.
- Evaluate writes directly into `NEW` with the manifest written last, so there is
  no duplicate copy.
- Any unexpected partial output (exit 5 or 6) is bounded by a single bundle cap.
  The allowance headroom covers at least two partial reassessment bundles.
- Nothing is deleted.

**The v2 L1 allowance (301,989,888 B logical) no longer covers the v3 cap-based
bound.** Re-proposed Gate 2 allowance (owner choice G2, pending):

| Launch | Logical | Physical | Files | Dirs |
|---|---:|---:|---:|---:|
| L1 witness driver | 369,098,752 (352 MiB; headroom 49,545,216) | 402,653,184 (384 MiB; headroom 59,035,648) | 4,500 | 900 |
| L2 legacy regression pytest (5 named files) | 16,777,216 | 20,971,520 | 600 | 300 |

L2's figures are an estimate: the five files have 64 test functions, and their
`tmp_path` usage has not been measured. L2 is unchanged from v2.

## 5. Gate 1 test allowance (TDD; proposed)

See `PLAN.md`:

- at most 40 pytest launches;
- 536,870,912 logical bytes in total;
- 20,000 files and 5,000 directories in total;
- every launch uses a fresh basetemp under a dedicated workspace;
- no cleanup.

These are engineering allowances with no measured basis yet. The new tests do
not exist.

END OF RESOURCES V3
