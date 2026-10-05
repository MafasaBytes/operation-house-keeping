# Resource measurements, analytical bounds and engineering allowances

This file keeps three kinds of number separate, and every limit in
`policy.json#/limits` carries one of them as its basis:

- **Measured:** sizes of existing retained material, measured statically
  (`stat`, plus base64 decoding of closure members). No code was executed.
- **Analytical:** maxima that follow from the proposed profile structure.
- **Engineering allowance:** a proposed ceiling with a margin over the measured
  value. It is a spending and refusal limit, not proof that the work fits.

Old-profile ceilings (`measurement_contracts.APPROVED_LIMITS`) are listed only
for comparison. They are not capacity evidence for the new route.

## 1. Measured (existing material, 2026-10-04)

Source: the 2026-10-01 experiment workspace
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/sim-investigation-2026-10-01/outputs/`.
It was read only; no file there was written.

| Artifact | Bytes |
|---|---:|
| NM bundle files (6 runs) | invocation 511–520 · closure 192,430–201,218 · result 5,890–15,967 · trace 22,688–31,134 · build 27,479 · policy 876 · manifest 971–972 |
| NR bundle files (3 runs) | invocation 580–583 · closure 418,747–419,391 · result 5,047–5,884 · trace 6,298–6,475 · build 27,632 · policy 876 · manifest 970 |
| NM baseline closure, decoded | 24 members, 144,491 B; largest member 86,310 B (`nm.evidence.v1`) |
| NR baseline closure, decoded | 43 members, 309,593 B; largest member 86,313 B (`nm.evidence.v1`) |
| Public evidence object | 86,310–86,313 B. It dominates closure size; a reassessment carries two. |
| Build record | 27,479 B (NM), 27,632 B (NR) |

These are the nearest analogues, not measurements of the new route. The new
records (derivation, applicability, reviews) do not exist yet.

## 2. Analytical bounds of the proposed profile

### Structural maxima

- 2 hypotheses (one per kind) × procedures T1 (3 outcomes) and T2 (2 outcomes),
  giving **10 derivation cells**.
- Required condition keys: T1 has 3 conditions and T2 has 2, so 5 per phase and
  **10** across both phases.

### Rational operations

| Stage | Operations |
|---|---|
| Derivation, per hypothesis | 2 additions and 2 subtractions for the T1 interval endpoints, plus 3 regions × up to 4 endpoint comparisons, so ≤ 16 |
| Derivation, two hypotheses | ≤ 32 |
| Baseline checks | 2 equality comparisons per hypothesis, so ≤ 4 |
| T2 | 1 comparison |
| Reassessment | 2 operations (`r ± w`), plus 3 regions × 4 comparisons, plus ≤ 4 containment and domain checks, plus 2 × 3 cell lookups, so ≤ 30 |
| Admission of all model, plan, scalar and bound rationals | ≤ 40 parses |
| **Total** | **< 200** |

The proposed allowance is 1,024.

### Unique objects (sum of per-kind maxima)

| Object | Maximum |
|---|---:|
| Explanations | 2 |
| Model | 1 |
| Interpretation plan | 1 |
| Policy | 1 |
| Request | 1 |
| Authorities | 2 |
| Declarations | 32 |
| Evidence items | 32 |
| Evidence contents | 32 |
| Reviews | 64 |
| Public evidence (baseline, result) | 2 |
| Prior-selection bundle references | ≤ 8 |
| Build | 1 |
| Policy proposal | 1 |
| **Total** | **≤ 180** |

The proposed limit is 192.

### Aggregation and trace

- Aggregation: at most 64 reviews, each evaluated against at most 4 condition
  keys of its item, so ≤ 256 review evaluations.
- Trace entries: 10 cells + 10 condition keys + 32 items + 64 reviews + gates
  (< 20), so ≤ 136. The proposed limit is 512.

### Closure bytes

There is no useful analytical bound: 192 objects × 196,608 B is about 37.7 MB,
which is not a credible target. The ceiling is therefore an engineering
allowance with a refusal before aggregation.

## 3. Engineering allowances (proposed)

| Limit | Value | Basis |
|---|---:|---|
| object_bytes | 196,608 | about 2.3× the largest measured object (86,313) |
| closure_bytes (decoded) | 1,048,576 | about 3.4× the measured reassessment-analogue closure (309,593) |
| result_bytes | 65,536 | about 4× the largest measured result (15,967) |
| trace_bytes | 131,072 | about 4× the largest measured trace (31,134) |
| build_bytes | 65,536 | about 2.4× measured (27,632) |
| invocation / manifest | 16,384 each | measured below 1 KiB |
| bundle_bytes | 2,097,152 | sum of file caps, rounded |
| integer_digits | 32 | new; legacy 128 is not inherited |
| evidence items / per key / reviews / per item | 32 / 8 / 64 / 4 | engineering; boundary witnesses F10–F12 |

For comparison only, the legacy old-profile values are: `object_bytes` 262,144;
`closure_bytes` 524,288; `trace_bytes` 131,072; `integer_digits` 128;
`unique_objects` 128. The proposal does not inherit them.

## 4. Proposed storage for the next verification step

These figures are estimates and are not yet reserved.

A witness run of about 52 evaluate/verify/replay calls produces small bundles:
about 0.8 MB each at most (closure plus files), and most refusals write nothing.

- **Estimate:** 52 × 0.8 MB, about 42 MB, plus about 10 MB for a sparse
  checkout and about 2 MB of logs.
- **Proposed allowance:** 128 MiB logical, 4,000 files, 800 directories, in a
  new workspace with one launch and no contingency.
- **Stop rules:** see `PLAN.md`. Exceeding the allowance stops the run; it does
  not raise the ceiling.

END OF RESOURCES
