# Resources v2: measured, analytical, engineering and estimated

Every number in this file is labelled with one of five classes:

- **Measured:** sizes of existing retained material, taken statically. No code
  was executed.
- **Analytical:** follows from fixed profile limits alone.
- **Engineering:** a proposed refusal ceiling.
- **Engineering-derived:** arithmetic over engineering ceilings.
- **Estimate:** an unmeasured expectation for the new route. It is never a
  maximum.

The predecessor package called several hand counts "analytical maxima";
`CORRECTIONS.md` records the relabelling.

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
| reassessment_unique_objects | 400 | engineering-derived | **includes the entire prior selection closure** (≤ 192) + prior computed records 6 + descriptor 1 + own objects 189 = 388 |
| selection_closure_decoded_bytes | 1,048,576 | engineering | about 7× the measured selection analogue |
| selection_closure_file_bytes | 1,474,560 | engineering-derived | ⌈1,048,576 × 4/3⌉ + 192 × 160 B = 1,428,822 |
| reassessment_closure_decoded_bytes | 2,621,440 | engineering-derived | prior closure 1,048,576 + prior computed records 344,064 + own 1,048,576 = 2,441,216 |
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
- **Reassessment:** about 300 KB decoded, about 410 KB encoded, plus about 70 KB.
  Total about 480 KB.

## 4. Gate 2 storage, derived from the witness matrix

**Bundle and log counts** (from `witnesses.json`):

| Item | Count |
|---|---:|
| Application invocations | 154 |
| Bundle-producing selection invocations (completing evaluate and replay) | 69 |
| Bundle-producing reassessment invocations | 17 |
| Refusing evaluate/replay invocations | 29 |
| Verify invocations (write no bundle) | 39 |
| Harness-mutated bundle copies | 3 |

Refusals are contractually pre-publication: stages 1–5 and 7 run before any
output directory exists, so they write nothing.

**Cap-based upper bound for the verification launch** (engineering-derived; a
true bound only if the caps hold):

| Component | Logical bytes | Derivation |
|---|---:|---|
| Selection bundles and harness copies | 150,994,944 | 72 × 2,097,152 |
| Reassessment bundles | 71,303,168 | 17 × 4,194,304 |
| Retained stdout/stderr | 40,370,176 | 154 × 262,144 joint stream cap |
| Workspace sparse checkout | 10,485,760 | measured analogue ≈ 10.3 MB |
| **Total** | **273,154,048** | |

- **Files:** about 4,109, made up of 89 bundles × 9 files, 154 × 2 logs and
  about 3,000 checkout files.
- **Directories:** about 778.
- **Physical:** logical + 4,096 per file + 8,192 per directory, about
  296,357,888.

**Estimate** (unmeasured): 72 × 235 KB + 17 × 480 KB ≈ 25 MB of bundles, plus
logs and checkout.

**Retained failures and coexistence:**

- Replays keep the source bundle and write a new one; both are already counted.
- Evaluate writes directly into `NEW` with the manifest written last, so there is
  no duplicate copy.
- Any unexpected partial output (exit 5 or 6) is bounded by a single bundle cap.
  The allowance headroom below covers at least two partial reassessment bundles.
- Nothing is deleted.

**Proposed Gate 2 allowance:**

| Launch | Logical | Physical | Files | Dirs |
|---|---:|---:|---:|---:|
| L1 witness driver | 301,989,888 (288 MiB) | 335,544,320 (320 MiB) | 4,500 | 900 |
| L2 legacy regression pytest (5 named files) | 16,777,216 | 20,971,520 | 600 | 300 |

L2's figures are an estimate: the five files have 64 test functions, and their
`tmp_path` usage has not been measured.

## 5. Gate 1 test allowance (TDD; proposed)

See `PLAN.md`:

- at most 40 pytest launches;
- 536,870,912 logical bytes in total;
- 20,000 files and 5,000 directories in total;
- every launch uses a fresh basetemp under a dedicated workspace;
- no cleanup.

These are engineering allowances with no measured basis yet. The new tests do
not exist.

END OF RESOURCES V2
