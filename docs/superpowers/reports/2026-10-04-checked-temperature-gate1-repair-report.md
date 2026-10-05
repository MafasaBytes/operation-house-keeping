# Checked-temperature Gate 1 — consolidated correction and scoped repair report

Date: 2026-10-04. Status: **Gate 1 repair evidence**. It is not Gate 1
acceptance and not executable-build qualification. Gate 2, the full suite,
qualification, commits and publication were not performed. Gate 1 acceptance and
the commit/build-binding step remain owner-gated.

## 0. Checkpoints verified before work

| Item | Value |
|---|---|
| Gate 1 report | `docs/superpowers/reports/2026-10-04-checked-temperature-gate1-tdd-report.md` `02e3b29f866fa8ab7af1ada3c9bab2eaa52434cd72e01e3b46ce51220354e6a1` (unchanged) |
| v3 manifest | `1a9eccbd8b0191eac08b4677a087f7503ee934845425985b05686c179e1e5572` (unchanged; v2 `e7dbccec…`, original `c3de4cb9…` unchanged) |
| HEAD and index | `2f0afbd…`; `09ae83d4…` (unchanged) |
| Pre-existing changes | `.gitignore` `010b1010…`, `bounded_pytest_runner.py` `97999fad…` (unchanged) |

## 1. Successor commitments

| Item | SHA-256 |
|---|---|
| v4 package `docs/superpowers/specs/2026-10-04-checked-temperature-contract-preparation-v4/MANIFEST.json` | `9e0afa328c3281fd468be21911f7840a74a35cdafd616b3f79605eaebd5df529` (1,973 B; 6 members) |
| v4 `schemas.json` (vendored byte-identically as `checked_temperature_schemas.json`) | `43c2af0b7bc3be137a0576e51b281be1ea53854c5e13d5d0a2c807f7611ac570` |
| v4 `policy.json` (`ct.policy-edition.v4`) | `46df039bff18ab0ccb8a31262e42f1f0d40a828ede6e797953b769ecb49e8c15` |

**Package content:**

- `CONTRACT.md` is the v3 text verbatim (checked) plus §12 amendments.
- `AMENDMENTS.md` is the explicit old/new contract, schema, policy and witness
  map.
- `witnesses.json` has 135 cases: 103 original, 1 amended (F12b, original
  expectation retained), 31 new.

## 2. Results first

Launch 12 ran `tests/checked_temperature`: **181 passed, 0 failed**. All results
in this report are in-process unit tests using the labelled `TestDoubleBuild`
(§6).

**Baseline selection (FX1):** unchanged from Gate 1.

- T1 branches `low{H2} gap{} high{H1}`, worst 1; T2 worst 2; `best = [T1]`.
- Verify and replay complete.

**Baseline reassessment (UN1 / RE1):** now uses **value-distinct,
occurrence-distinct T1 result evidence**, admitted value 60. It is not the
baseline evidence.

- Interval `[59.5, 60.5]`; H1 compatible, H2 incompatible; `one_compatible`.
- Verify and replay complete standalone.
- The applicability rows are only the 4 executed-procedure (T1) claims.

**Adverse twins.** Every twin is a legal object with recomputed hashes and pins
(the owner's legal-form requirement). Each refusal is asserted with its exact
code and target.

| Correction | Twins (code) |
|---|---|
| 1 Policy identity | v3 label and v2 label → `POLICY_EDITION_MISMATCH` (workaround removed) |
| 2 Diagnostics | Real entry point in the uncommitted tree → exit 3 `BUILD_IDENTITY_UNAVAILABLE`, target `/build/current` (DG1, amended expectation); usage → exit 2 `CLI_USAGE`; F12b (65 reviews) → `SCHEMA_INVALID` (amended); F12c (captured `reviews` 10, 11 supplied) → `RESOURCE_LIMIT_EXCEEDED` stage 4 |
| 3 Result evidence | T1 value 60.2 versus evidence 60 → `/value`; baseline evidence reused → `/baseline_reuse`; different digest but the baseline occurrence reused → `/occurrence`; foreign anchors → `/anchors`; consistently substituted instrument → `/instrument`; code evidence for T1 → `/kind`. T2: code mismatch `/value`, instrument `/instrument`, `observed_at` outside the window `/acquisition`, temperature evidence for T2 `/kind`. All are `RESULT_EVIDENCE_MISMATCH`. A non-model assertion context fails the legacy join (`SCHEMA_INVALID`). The T2 positive completes, verifies and replays. |
| 4 Applicability scope | Reassessment rows = executed procedure only (4); selection still requires all 6 |
| 5 Encoded carriage | Authored 2,000-character rationale under captured `string_bytes` 1,500 → refused; the same limit still carries base64 payloads over 100 KB and verifies; a long non-`data` string in `closure.json` → `RESOURCE_LIMIT_EXCEEDED` |
| 6 Withheld priors | Selection with an unsupplied, undeclared required claim core: withheld, verify and replay complete, and the core is not a closure member. A reassessment over it completes and verifies (carried prior recomputes equal). |
| 7 Evaluation authority validity | Selection window excluding `request.as_of` → `AUTHORITY_SCOPE_MISMATCH` `/evaluation_authority/valid`; reassessment window ending before `acquisition.ended` → same; a closed boundary is admitted |
| 8 Cached derivation | Equal cache completes (CD1); altered cache → `CACHED_DERIVATION_MISMATCH` (CD2 / IN1, selection and reassessment); non-canonical or non-object cache → `SCHEMA_INVALID` |
| 9 Captured limits | Each of these refuses `RESOURCE_LIMIT_EXCEEDED`: `object_bytes`, `string_bytes`, `json_depth`, `json_nodes`, `integer_digits`, `hypotheses`, `procedures`, `outcomes_per_procedure`, `fractional_digits` (edition-valid 1/100 under captured 1), `successor_chain`, `retained_selection_bytes`, `derivation_cells`, `trace_entries` (7 < 8) and `rational_operations` (33 < 34). The exact boundaries 8 and 34 are admitted. |

## 3. Evidence classes (kept separate)

| Class | Meaning | Where |
|---|---|---|
| **Original-matrix evidence** | v3 witness cases with v3 expectations, unchanged | `test_baseline_vertical`, `test_adverse_twins`, `test_kind_and_role`, `test_aggregation`, `test_selection_witnesses`, `test_reassessment_witnesses`, `test_closure_and_verify`, `test_cli` (except DG1). These now run under the v4 contract: v4 policy label, genuine-derivation result evidence, enforced validity windows. No original expectation changed except F12b. |
| **Amended-contract evidence** | Cases whose expectation changed (F12b, DG1) or that are new under §12 | `test_v4_amendments.py`; `test_selection_witnesses::test_f12b_*` (amended); `test_cli::test_process_entry_point_*` (DG1 amended) |
| **Test-double evidence** | Every in-process bundle in this report | `TestDoubleBuild` (all-zero / `TEST_DOUBLE` markers). Proves nothing about a clean build. The only real-identity observation is the DG1 refusal. |

**Result-evidence fixture.**
`tests/checked_temperature/result_evidence.py` derives value-variant T1 public
evidence through the backend's public derivations. It mirrors the committed
generator `prepare_public_evidence.py`, with distinct payload, raw-record and
occurrence identities. The backend is used, not extended. The fixture keeps the
retained synthetic instant, so **it is not a temporally subsequent acquisition**
(§8, C1).

## 4. Obligation-to-test map (v4 obligations)

| Obligation | Tests (`tests/checked_temperature/…`) |
|---|---|
| 1 Policy identity | `test_v4_amendments::test_policy_identity_v4_label_only`; `test_selection_witnesses::test_po5_*` |
| 2 Diagnostics and precedence | `test_cli::test_process_entry_point_*` (DG1), `test_process_usage_error` (DG2), `test_duplicate_flag_*`; `test_selection_witnesses::test_f12b_*` (amended); `test_v4_amendments::test_f12c_*` |
| 3 Result evidence | `test_v4_amendments::test_re1_*`, `test_t1_result_evidence_twins[RE2,RE3,RE5]`, `test_re4_*`, `test_re6_*`, `test_t2_result_evidence_twins[RE7–RE10]`, `test_result_evidence_reusing_the_baseline_occurrence`, `test_result_evidence_with_other_anchors`, `test_result_evidence_assertion_context_is_the_models`; every UN/PS/OB/EO test now uses genuine-derivation evidence |
| 4 Applicability scope | `test_v4_amendments::test_ap1_*` |
| 5 Encoded carriage | `test_v4_amendments::test_ec1_*`, `test_ec2_*` |
| 6 Withheld priors | `test_v4_amendments::test_wd1_*`, `test_wd2_*` |
| 7 Evaluation authority validity | `test_v4_amendments::test_av1_*`, `test_av2_*`, `test_av3_*` |
| 8 Cached derivation | `test_v4_amendments::test_cd1_cd2_cd3_*`, `test_cached_derivation_on_reassessment`, `test_cached_derivation_must_be_an_object` |
| 9 Captured limits | `test_v4_amendments::test_captured_limits_are_enforced[LM1–LM7]`, `test_lm6_lm7_exact_accounting_boundaries`, `test_captured_count_and_format_limits[…]`, `test_captured_derivation_cells_limit`, `test_captured_successor_chain_limit`, `test_captured_retained_selection_bytes_limit`, `test_f12c_*` |

## 5. Launch and storage accounting (cumulative; not reset)

Allowance: 40 launches, 536,870,912 logical bytes, 20,000 files and 5,000
directories. **Launches 01–09 were consumed before this repair; launches 10–12
are this repair. 12 have been used and 28 remain.**

| # | Selection | Exit | Outcome | Cumulative after (logical B / files / dirs counted) |
|---|---|---|---|---|
| 10 | `tests/checked_temperature` | 0 | 170 passed | 7,473,781 / 1,345 / 133 |
| 11 | `tests/checked_temperature` | 1 | **2 failed**, 179 passed (preserved) | 9,288,890 / 1,602 / 155 |
| 12 | `tests/checked_temperature` | 0 | **181 passed** | 10,813,500 / 1,857 / 177 |

**Workspace now, including the review artifacts:**

| Measure | Used | Allowance |
|---|---:|---:|
| Logical bytes | 11,079,480 | 536,870,912 |
| Physical bytes | 17,989,632 | — |
| Files | 1,859 | 20,000 |
| Directories | 139 real | 5,000 |

The launch log is `<ws>/launch-log.jsonl`. Nothing was deleted.

**Preserved failure, launch 11:**

- **F5b:** the new captured `fractional_digits` check preempted the original
  edition-level `RATIONAL_INVALID`. Fixed: the captured check applies only to
  edition-valid rationals, so the original expectation holds.
- **Test defect:** a case set `fractional_digits` 0, below the schema minimum of 1.

The 9 legacy identity-dependent failures from launch 07 were **not re-run and
are not reinterpreted**. They still require a clean committed tree (§7).

## 6. Code-review-ready diff

| Artifact (`<ws>` = `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd`) | Lines | SHA-256 |
|---|---:|---|
| `<ws>/review/gate1-repair-delta.diff`: exact delta from the Gate 1 implementation (reconstructed from the retained r2 patch) to the repaired files | 1,186 | `0b638c0d07fde44e09a49683379afab9b9cc8500d6fc3946411139df0c0ba28c` |
| `<ws>/review/gate1-code-r4.diff`: full current implementation (cli.py dispatch plus every new file) | 4,738 | `d7178b818bf6b0f8fff67b6b4ad4965112d310801b9c4ffeac95844e4534d566` |

**Files changed by the repair:**

- `checked_contracts.py`, `checked_runtime.py`, `checked_cli.py`,
  `checked_derivation.py`, `checked_reassessment.py`;
- the vendored schema (v3 → v4);
- `tests/checked_temperature/fixtures.py`, `test_cli.py`,
  `test_selection_witnesses.py` (F12b docstring);
- new: `result_evidence.py`, `test_v4_amendments.py`.

**Unchanged:**

- `checked_applicability.py`, `checked_selection.py`;
- legacy modules, backend, dependencies and the lock;
- historical evidence;
- every preparation package (v4 is a new directory).

## 7. Independent review of the repair

A read-only `code-reviewer` subagent ran no tests and executed no code. Its report
is `<ws>/review/v4-review.md`, SHA-256
`8c989f7069f193c1091d4fe78e5daba08fb8075d6b68db8fc58366a7adf08b43`. It is model
output, not approval.

It found no critical issues. It confirmed:

- the vendored schema and policy pins;
- the label check is free of any workaround;
- exactly three derived non-edges;
- the authority windows;
- the base64 exemption;
- the rational accounting (FX1 = 34);
- honest disclosure of C1 and of the test double.

The four important findings were verified against the code and fixed, each with a
twin test (launch 12):

| Finding | Fix |
|---|---|
| I-1 Captured `hypotheses`, `procedures`, `outcomes_per_procedure`, `derivation_cells`, `successor_chain`, `fractional_digits` and `retained_selection_bytes` retained but not checked | Enforced (`_captured_counts`, `_cell_limit`); contract §12.9 text updated |
| I-2 Output-directory creation failure exited 5 | Exit 6, per §12.2 |
| I-3 A non-object cached derivation gave an internal error | `SCHEMA_INVALID` |
| I-4 T1 result evidence borrowed its own assertion context | The model's assertion context is enforced; only the evidence `as_of` remains, pending C1; contract §12.3 updated |

Minor items also fixed: occurrence and anchor twins added;
`PackageNotFoundError` / `ImportError` mapped to `BUILD_IDENTITY_UNAVAILABLE`;
the stale F12b docstring.

**Residual minor items, not changed (owner visibility):**

- **Legacy reconstruction failure code:** a result-evidence legacy reconstruction
  failure reports `SCHEMA_INVALID`, not `RESULT_EVIDENCE_MISMATCH`.
- **DG1 on a clean tree:** DG1 asserts `BUILD_NOT_PERMITTED` there, so the
  `BUILD_IDENTITY_UNAVAILABLE` observation exists only in an uncommitted tree.
- **LM2 trigger:** LM2 is triggered by 64-character digests as well as authored
  text.
- **Unbound clause:** AP1 does not exercise the "unbound" clause for other
  procedures.
- **Forged `plan_claim`:** it refuses `SCORE_METADATA_INVALID` rather than the
  §12.6 recomputation code.
- **Uncounted comparisons:** some comparisons outside the §12.9 enumerated items
  are not counted.
- **Receipt overflow exit:** receipt overflow maps to exit 7.

Still open from Gate 1 review: M1 stage-4/5 ordering for multi-defect inputs; M5
`contained` tautology; M9 code for a pinned evaluation authority with purpose
`execution`.

## 8. Unresolved decisions and owner gates

1. **C1, T1 acquisition-time binding** (§12.3; this portion stopped).
   - Which T1 evidence instant must lie within the acquisition window (snapshot
     `as_of`, question `as_of`, or occurrence `finished_at`)? Must it follow
     `model.context.as_of`?
   - Every committed or reproducibly derivable `nm.evidence.v1` carries the
     retained instant `2026-08-07T20:30:00Z`, so no genuine temporally subsequent
     evidence exists for a positive witness.
   - Smallest exact proposal: occurrence `finished_at` ∈ `[acquisition.started,
     acquisition.ended]` and `acquisition.started` ≥ `model.context.as_of`. A
     positive fixture would need authorized generation of new synthetic upstream
     evidence (the source-interpretation and assertion chain).
   - Not implemented.
2. **Commit and build binding** (owner-gated). The following need an authorized
   commit and a re-baselined build identity (D9):
   - the 9 legacy identity-dependent tests;
   - DG1's clean-tree branch;
   - every real-entry-point success path;
   - Gate 2.
3. **G2:** still deferred. The v4 matrix has 217 invocations versus 179, so the
   v3 Gate 2 sizing needs re-derivation before any G2 request.
4. **Gate 1 acceptance:** owner decision.

END OF GATE 1 REPAIR REPORT
