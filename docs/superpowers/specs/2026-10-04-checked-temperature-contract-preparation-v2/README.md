# Checked-temperature contract preparation package v2 (successor)

**Date:** 2026-10-04.

**Status:** documentation-only preparation for owner evaluation. This package
authorizes no implementation, test, qualification or execution. It is **not**
evidence of executable readiness: none of its schemas, witnesses or limits has
been exercised by code.

**Predecessor:** `../2026-10-04-checked-temperature-contract-preparation/`,
`MANIFEST.json` SHA-256
`c3de4cb9d5868454e8d666267d9dd9cf58f33d69500065c1f648005bf3da48c2`. It is
preserved byte-for-byte, and this package supersedes it only as a proposal.

**Governing commitments (unchanged):**

- corrected design v2 `68da70f2…`;
- focused confirmation v2 `f0259702…`.

## Members

| Member | Purpose |
|---|---|
| [CONTRACT.md](CONTRACT.md) | Readable specification: identity and provenance, typed references, validation stages, claims and coverage, captured policy, changed-plan admission, bundle and closure carriage, build and replay |
| [schemas.json](schemas.json) | 21 closed record schemas, 23 typed-reference kinds, limit definitions |
| [policy.json](policy.json) | Editions, catalogue `ct.conditions.v2` (5 conditions), 7 local roles, 38 limits with basis, refusal codes, allowlist examples |
| [WITNESSES.md](WITNESSES.md) / [witnesses.json](witnesses.json) | 17 witnesses, 82 cases, 154 invocations; hand-derived, not executed |
| [RESOURCES.md](RESOURCES.md) | Measured sizes, estimates, engineering ceilings, and Gate 1/2 allowances |
| [PLAN.md](PLAN.md) | Gates 0–2, test authority per gate, stop rules |
| [CORRECTIONS.md](CORRECTIONS.md) | Old-to-new correction map |
| MANIFEST.json | Binds every other member by SHA-256 and bytes |

## The four corrections

The full map is in [CORRECTIONS.md](CORRECTIONS.md).

1. **Complete contracts and schemas.** Every output and carriage record is
   closed. Identity and provenance are defined per record class. Every
   reference names its target kinds. Validation responsibilities are staged.
   Missing policy refuses with `REFERENCE_MISSING`; an empty allowlist is only a
   recorded choice.
2. **Bind reviews to the exact claim.** Claims bind model revision, anchors,
   instrument and parameters or plan. Time scope is a separate `covers` window.
   Witnesses:
   - CB1–CB3: the `b_ref`-change twin;
   - OB2–OB4: `observation_error_bound`, with `b_ref` and `w` each applied once.

   Precedence is unchanged.
3. **Reconcile changed-plan requests.** One admission table governs the request
   and authority fields (CONTRACT §6.3), checked by witnesses PS1–PS5 and PB1.
   Unauthorized substitution refuses. A newly scoped successor records the former
   selection as historical reference and `ranking=not_reassessed`. There is no
   rerank or adoption.
4. **Verification and resource plan.**
   - Witnesses, cases, invocations and launches are counted separately.
   - Five legacy files are named.
   - Prior-bundle closure is counted in object and byte limits.
   - Estimates are no longer called maxima.
   - Accounting is separate for decoded and encoded data, all nine files,
     retained failures and physical allocation.
   - Test authority is set per gate, with no full suite.

## Conflicts with accepted semantics

None found (CONTRACT §11). No accepted design or confirmation commitment was
changed.

## Genuine owner choices

| ID | Choice | Recommendation |
|---|---|---|
| D1–D6 | H1 offset, H2 domain, `b_ref` bound, numeric admission, T1 decoder edition, hard-interval plan | as in the predecessor (unchanged) |
| D7 | Condition catalogue and exclusion predicate | **revised:** 5 conditions (`ct.conditions.v2`, adds `observation_error_bound`). Conclusive exclusion is unchanged. |
| D8 | Roles and unresolved policy | **revised:** 7 local unauthenticated roles (adds `local_policy_owner`). There is no default: missing policy refuses. |
| D9 | Build re-baseline | unchanged |
| D10 | Limits | **revised:** the 38 `policy.json` limits, with separate selection and reassessment caps. The predecessor's 128 MiB launch is superseded by G2. |
| O3 | Does `observation_error_bound` gate selection as well as reassessment? | yes, both phases |
| O5 | Claim binds the whole model revision, or only the governing parameters? | whole revision, as the design wording says |
| A1 | Synthetic allowlist content | calibration, mapping and hold only; `observation_error_bound` excluded |
| G1 | Gate 1 TDD allowance | 40 launches; 512 MiB / 20,000 files / 5,000 dirs; scoped selection |
| G2 | Gate 2 verification allowance | L1 288/320 MiB, 4,500 files, 900 dirs; L2 16/20 MiB, 600 files, 300 dirs |

**Disclosed discrepancy (unchanged).** The D5 decoder comes from the 2026-10-01
experiment model, not the committed P case (two regions split at 50).

## Static checks actually performed

Only static file parsing, hashing and standalone arithmetic were used. No
repository or application code was imported or executed.

The results are recorded in the delivery receipt and reproduced below:

- [x] JSON parse of `schemas.json`, `policy.json` and `witnesses.json`.
- [x] Schema consistency:
  - no dangling `$ref`;
  - no unknown `x-target`;
  - no required field missing from `properties`;
  - no open object.

  Only `ct.evidence-content` and `nm.evidence.v1` have no record schema, by
  design (opaque or legacy-validated).
- [x] Every refusal code used in `witnesses.json` is defined in
  `policy.json#/refusal_codes`.
- [x] Witness totals are recounted from the case list: 17 witnesses, 82 cases
  (31 positive, 51 adverse), 154 invocations by command. These agree with the
  `summary` block and with PLAN.
- [x] Limits:
  - The key set of `schemas.json#/definitions/limits` equals the 38 keys of
    `policy.json#/limits`, and all of them are required.
  - The nine closure, object and bundle ceilings in RESOURCES §3 are the
    `policy.json` values.
  - Embedded schema maxima equal policy values, except structural constants:
    - 6 claim rows;
    - 7 block reasons;
    - 9 bundle files;
    - 5 withholding reasons;
    - 1 observation-uncertainty entry;
    - name length 128.
  - The RESOURCES arithmetic was recomputed standalone and agrees.
- [x] Relative links resolve.
- [x] No trailing whitespace or tabs.
  - `git diff --check` does not apply to untracked files, so no
    `git diff --check` result is claimed.
- [x] Manifest digests recomputed after writing.
- [x] The predecessor manifest and all eight members re-verified unchanged.

## Preservation record

| Item | Value |
|---|---|
| HEAD | `2f0afbd368105b99f0b8548ffece107918386e3d` (unchanged) |
| `.git/index` SHA-256 | `09ae83d4c39ead36e682600c851b5d355246c84708f8791080cc97b3183ff476` (unchanged) |
| Tracked modifications | `.gitignore`, `tests/reassessment_profile/bounded_pytest_runner.py` (unchanged; file SHA-256 `010b1010…`, `97999fad…`) |

Nothing was staged, committed, cleaned, published, or written to runtime or a
ledger. No dependency was added.

IN-001 and CI-001 remain open and unselected. Slice 5 and final acceptance
remain owner gates.

END OF PACKAGE README V2
