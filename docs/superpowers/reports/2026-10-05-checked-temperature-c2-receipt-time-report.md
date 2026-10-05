# Checked-temperature amendment C2 — receipt-time closure and commit-scope review

Date: 2026-10-05. Status: **Gate 1 unit-test evidence for the owner-approved C2
step only**. Work stops here for exact commit-scope review. Gate 1 acceptance and
commit authorization remain owner decisions.

No backend change, staging, commit, Gate 2, full suite, dependency change,
physical acquisition, adoption, reranking or remote operation was performed.

## 1. Amendment commitments

| Item | SHA-256 |
|---|---|
| C2 record `docs/superpowers/specs/2026-10-05-checked-temperature-contract-amendment-c2/MANIFEST.json` | `6252a2da6058b443db070954e7bf2a2ae075aba652ce6b09cabc0eb1b323bec6` (901 B) |
| `AMENDMENT.md` | `98253c479b5a04242a2c9ffc327193b2bfc1d851fe786baaf9ac04180ddb2ad1` |
| `witnesses-c2.json` (8 cases: TC5b amended; RC1–RC4 new; TC1 and TC2a retained from C1) | `2a5a91c45e606ee49984547a07635f9e3fb62eff94cb2d9fa93d4afa9570ca4a` |
| Amends C1 (verified before work; frozen and unedited) | `791b4035807ce032f7852447df0e0b7d9324c8cb90d52bc8a1b6ebac42ab9d1a` |
| Base v4 / schemas / policy (unchanged) | `9e0afa32…` / `43c2af0b…` / `46df039b…` |

**Preserved unchanged:**

- the v3, v2 and original packages;
- every earlier report;
- HEAD `2f0afbd`, the git index `09ae83d4…`, and the pre-existing changes
  (`010b1010…`, `97999fad…`).

## 2. Rule (C2.1, supersedes C1.1 rule 1)

Read from the **same** admitted occurrence, located through the binding indices,
whose `occurrence_id` must equal the admission's: `received_at` **and**
`finished_at` both lie within the closed `[acquisition.started,
acquisition.ended]`. Otherwise the refusal is `RESULT_EVIDENCE_MISMATCH`
`/acquisition_window`.

**Retained:**

- `acquisition.started` ≥ `model.context.as_of`;
- the upstream validation, unchanged.

This closes the demonstrated retained-evidence substitution. It does not
authenticate chronology, and it does not promise rejection of coherently
reconstructed synthetic evidence.

## 3. Results (launch 16: `tests/checked_temperature`, 198 passed, 0 failed, 0 xfail)

| Required check | Test | Result |
|---|---|---|
| 1 TC5b is now an explicit refusal, with no expected-failure marker | `test_c1_acquisition_time::test_tc5b_*` → `RESULT_EVIDENCE_MISMATCH` `/acquisition_window` | pass. Historical outcome retained: the forged chain was **accepted** under C1 alone (strict xfail in launches 13–15; C1 `witnesses-c1.json` `observed`) |
| 2 `received_at` outside the window, `finished_at` inside → refuse | `test_c2_receipt_time::test_rc1_*` | pass |
| 3 `finished_at` outside, `received_at` inside → refuse | `test_c2_receipt_time::test_rc2_*` (later chain, `finished_at` moved after `ended`) | pass |
| 4 Closed boundaries accepted (receipt at the start, completion at the end) | `test_rc3a_*` (genuine chain, receipt = completion = `09:01:06`); `test_rc3b_*` (distinct instants) | pass |
| 5 The old start-at-`finished_at` case refuses when receipt precedes it | `test_rc4_*` refuses. C1 `test_tc2_closed_window_boundaries[TC2a-start]` stays accepted on unaltered genuine evidence, because there receipt equals completion and does not precede the start. No evidence was altered to preserve an old expectation. | pass |
| 6 Coherent later evidence completes reassessment, standalone verify and replay | `test_c1_acquisition_time::test_tc1_*`; `test_genuine_chain_receipt_equals_completion` | pass |
| 7 Baseline reuse, value, instrument, authority and uncertainty checks intact | Full module set (198), including TC6, the v4 RE/AV/OB/PS/EO/UN cases and F4 | pass |

**Labelling:**

- RC3b and RC4 use validator-accepted evidence in which only `finished_at` was
  moved, 20 s after receipt. It is labelled in the test module and is not a
  coherently rebuilt chain.
- **Test-double evidence:** every bundle uses the labelled `TestDoubleBuild` and
  proves nothing about a clean build.
- **Legacy failures:** the 9 legacy identity-dependent failures (launch 07) remain
  unresolved until authorized clean-build verification.

## 4. Exact diff

Retained under `<ws>/review/`, where
`<ws>` = `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd`.

| Artifact | Lines | SHA-256 |
|---|---:|---|
| `c2-delta.diff`: post-C1 → now. The post-C1 tree was reconstructed by applying the retained `c1-delta.diff` to the r4 reconstruction; every other file was checked byte-equal. | 180 | `c2534739f1742b8ec5e83e9756d5338cabcf8791e0fd105b251d292235601bc1` |
| `gate1-code-r5.diff`: full current implementation and tests | 5,204 | `d55837960f5624416194f84f06417997691f1b584c1d8b4ba9370c42ef4b7200` |

**Files in the C2 delta:**

- `checked_runtime.py`: the C2.1 rule and the docstring;
- `tests/checked_temperature/later_chain.py`: helpers `occurrence_received_at`
  and `with_finished_at`;
- `test_c1_acquisition_time.py`: TC5b marker removed, explicit refusal;
- new: `test_c2_receipt_time.py`.

## 5. Cumulative accounting (not reset)

| Launch | Selection | Exit | Outcome | Cumulative after (logical B / files / dirs counted) |
|---|---|---|---|---|
| 16 | `tests/checked_temperature` | 0 | 198 passed | 16,355,860 / 2,934 / 541 |

**Launches: 16 of 40 used, 24 remain.**

| Measure | Used now | Allowance |
|---|---:|---:|
| Logical bytes | 16,637,378 | 536,870,912 |
| Physical bytes | 28,446,720 | — |
| Files | 2,936 | 20,000 |
| Directories | 489 real | 5,000 |

Nothing was deleted, and earlier failed launches (01, 02, 05, 07, 11, 13) remain
retained.

## 6. Exact commit-scope review (for owner decision; nothing staged)

### A. Implementation (inside `applications/`; part of the maintained build identity)

| Path | Bytes | SHA-256 (prefix) | State |
|---|---:|---|---|
| `applications/bounded_decision_workflow/cli.py` | 15,781 | `ed4e7ffdd41a748e` | tracked, modified: exactly the 3-line `checked-` dispatch |
| `applications/bounded_decision_workflow/checked_applicability.py` | 13,034 | `cd7f22ec5a47aa74` | new |
| `applications/bounded_decision_workflow/checked_cli.py` | 8,772 | `888bbf0743969317` | new |
| `applications/bounded_decision_workflow/checked_contracts.py` | 12,812 | `c658bae8e6f94686` | new |
| `applications/bounded_decision_workflow/checked_derivation.py` | 6,308 | `a09ae6e076a7dc5e` | new |
| `applications/bounded_decision_workflow/checked_reassessment.py` | 4,538 | `671b68333f8f1654` | new |
| `applications/bounded_decision_workflow/checked_runtime.py` | 57,820 | `4aca566e271238ae` | new |
| `applications/bounded_decision_workflow/checked_selection.py` | 3,583 | `a203bb75589ef1a4` | new |
| `applications/bounded_decision_workflow/checked_temperature_schemas.json` | 92,493 | `43c2af0b7bc3be13` | new; byte-identical to the v4 `schemas.json` |

These are the only uncommitted paths under `applications/` and `backend/`.
Committing all of them is what makes the maintained executable identity
computable again, so the clean-build step can run.

Two consequences of committing them:

- **Re-baseline:** it changes the current build identity (owner decision D9).
  Earlier NM/NR bundles then replay only under their recorded historical builds.
- **Data file:** the schema JSON is outside the build source manifest, which
  covers `.py` files and the lock. It is bound through
  `contract_editions.schemas_sha256` and the import-time pin.

### B. Tests (`tests/checked_temperature/`, 16 files)

| Path | Bytes | SHA-256 (prefix) |
|---|---:|---|
| `__init__.py` | 0 | `e3b0c44298fc1c14` |
| `conftest.py` | 314 | `a09262949a6f7bae` |
| `fixtures.py` | 26,003 | `7e4cdab6f6ca585c` |
| `later_chain.py` | 9,607 | `539b73ba72b5fb2d` |
| `result_evidence.py` | 4,215 | `89d3a3e3f9c3f0d3` |
| `test_adverse_twins.py` | 3,634 | `5e32a82a569ad916` |
| `test_aggregation.py` | 11,098 | `fd86f1aea0d96510` |
| `test_baseline_vertical.py` | 7,523 | `a0265bb8ae4048bc` |
| `test_c1_acquisition_time.py` | 7,360 | `d88b38bcb57f56c2` |
| `test_c2_receipt_time.py` | 3,756 | `9e37f1816aaa74e9` |
| `test_cli.py` | 7,173 | `76f6b87a0ad1a168` |
| `test_closure_and_verify.py` | 11,608 | `04ac85959fac4044` |
| `test_kind_and_role.py` | 3,637 | `a6cf84ef2701273a` |
| `test_reassessment_witnesses.py` | 11,448 | `9e30b0ffa75dd574` |
| `test_selection_witnesses.py` | 22,976 | `e8262afa8cd376a7` |
| `test_v4_amendments.py` | 15,416 | `e99ec9378552ab60` |

The tests read committed historical evidence read-only:

- `docs/superpowers/reports/2026-09-19-next-measurement-preparation/inputs/A-restored/capture.json`;
- the Moonraker fixtures under `backend/data_sources/testing/fixtures/api/`;
- existing backend test helpers.

### C. Contract and evidence documentation (candidates; owner chooses)

**Packages:**

| Package | `MANIFEST.json` (prefix) |
|---|---|
| Original | `c3de4cb9` |
| v2 | `e7dbccec` |
| v3 | `1a9eccbd` |
| v4 | `9e0afa32` |
| C1 | `791b4035` |
| C2 | `6252a2da` |

**Reports:**

- `2026-10-04-checked-temperature-gate1-owner-approval.md` (`de67a27c`);
- `…-gate1-tdd-report.md` (`02e3b29f`);
- `…-gate1-repair-report.md` (`57756c0d`);
- `2026-10-05-checked-temperature-c1-acquisition-time-report.md` (`f975a387`);
- this report.

The governing design and confirmation v2 are already present in the repository
as untracked files.

### D. Excluded from any checked-temperature commit (unrelated; preserve)

- the pre-existing tracked modifications to `.gitignore` (`/_to_delete/`) and
  `tests/reassessment_profile/bounded_pytest_runner.py`;
- untracked material from earlier work (for example
  `tests/reassessment_profile/slice5_*`, `.agents/`, and the 2026-09/2026-10-01
  proposals and reports);
- the test workspace and review artifacts under
  `~/operation-house-keeping-runtime/…` (outside the repository).

### E. After an authorized commit (not performed)

1. Clean-build verification in the approved environment.
2. A re-run of the 9 legacy identity-dependent tests.
3. DG1's clean-tree branch (`BUILD_NOT_PERMITTED`).
4. Real-entry-point success paths, which need a policy permitting the real build
   identity.
5. Gate 2 sizing for the 217-invocation matrix.

Each step stays separately owner-gated.

END OF C2 RECEIPT-TIME REPORT
