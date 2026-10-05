# Checked-temperature Gate 1 — TDD implementation report

Date: 2026-10-04. Status: **Gate 1 unit-test evidence**. This report is not
executable-build qualification and not final acceptance. Gate 2, the full suite
and release qualification were not launched.

- Approval record: `docs/superpowers/reports/2026-10-04-checked-temperature-gate1-owner-approval.md`.
- Approved baseline: v3 package, `MANIFEST.json` `1a9eccbd…5572`, verified before any edit.

## 1. Baseline and adverse-twin results (reported first)

All results below come from in-process unit tests in launch 09, which had 140
passed and 0 failed. They use the labelled `TestDoubleBuild` (see §5).

### Baseline vertical path (`tests/checked_temperature/test_baseline_vertical.py`)

**FX1 selection fixture.** The fixture is a complete, hash-consistent graph with
no placeholders. It uses the genuine committed public evidence object
(`nm.evidence.v1`, 86,310 B, from the 2026-09-19 preparation capture), which
gives baseline 60.1 and verdict `violated`. It has 6 required claims, each
declared, evidenced and reviewed.

**FX1 selection results:**

- Derivation:
  - H1 T1 `[601/10, 601/10]`;
  - H2 T1 `[451/10, 551/10]`;
  - T2 `heater_off` for both hypotheses.
- Selection:
  - T1 branches `low{H2} gap{} high{H1}`, worst 1, reduction 1;
  - T2 `heater_off{H1,H2}`, worst 2;
  - `best = [T1]`;
  - `score_domain = ideal_measurand_decoder_branches`;
  - `post_measurement_elimination_guaranteed = false`;
  - plan w = 1/2 captured, not scored.
- Applicability: 6 of 6 claims `supported`; use permitted; nothing unbound.
- Closure roots are exactly `{request, evaluation_authority, null}`, and the
  member set equals the reachable set.
- Verify reports `derivation_checked`, `applicability_policy_checked` and
  `downstream_result_not_replayed`.
- Replay reproduces the closure, derivation, applicability, result and trace
  byte-for-byte. The replay invocation records `replay_of`.

**UN1 reassessment, constructed in CO1 order (X → E → O → R → A):**

- Interval `[119/2, 121/2]`, branch `high`.
- H1 `compatible_under_declared_model`, H2 `conditionally_incompatible`;
  disposition `one_compatible`.
- `ranking = not_reassessed`, `adoption = derived_not_adopted`.
- Inherited plan executed. `former_plan` is null and `executed_plan` is P0.

**Prior carriage for UN1:**

- Closure roots are `{R, A, D}`.
- The descriptor lists exactly the prior closure members.
- The prior manifest, invocation, selection, derivation, applicability, trace,
  build and policy records are carried. The prior `closure.json` is rebuilt, not
  carried.
- No adoption, reassessment or closure record is a member.
- Verify with `--bundle` only reports `prior_material_checked`. Replay
  reproduces the result.

### Adverse twins

Each twin is schema-valid. Every affected digest and pin was recomputed, and
each refusal is the intended semantic code.

| Twin | Construction | Result |
|---|---|---|
| EO4 wrong execution-authority target | E authorizes X2 (X with a different instrument). R keeps X. X2 is reachable via E, so the refusal is not `REFERENCE_MISSING`. | `AUTHORITY_TARGET_MISMATCH`, stage 5, `/execution_authority/target`. The untouched control completes (EO1). |
| CL8 unrelated closure object at evaluate | A second, valid but unpinned evaluation authority for R is in `--objects-dir` | `UNREFERENCED_MEMBER` naming that digest (only the pinned authority is a root) |
| IN11 unrelated object at selection | A valid declaration bound to nothing | `UNREFERENCED_MEMBER` |
| CL2 unrelated member in a retained bundle | A valid opposing review is added to `closure.json`; the manifest is rehashed; the pins are unchanged | Verify refuses `UNREFERENCED_MEMBER`. The untouched bundle verifies. |
| CL3 the same object laundered through the descriptor | The review digest is also inserted into `D.prior_closure.members`; D, closure and manifest are rehashed | `PRIOR_BUNDLE_MISMATCH`, `/retained_selection/prior_closure/rebuild` |

### Kind and issuer-role enforcement (`test_kind_and_role.py`)

- **Schema annotations alone do not enforce.** A schema-valid execution
  authority whose `target` is a model reference, or whose role is
  `local_evaluation_issuer`, passes structural validation. The `x-target` and
  `x-allowed-roles` annotations are only collected there.
- **Enforcement is at stage 3:**
  - EO2: an execution authority targeting a request kind → `REFERENCE_KIND_MISMATCH`.
  - EO3: an evaluation authority targeting an execution target → `REFERENCE_KIND_MISMATCH`.
  - An execution authority issued by the evaluation role → `ROLE_MISMATCH`.
  - An evaluation authority issued by the execution role → `ROLE_MISMATCH`.
  - A declaration issued by the reviewer role → `ROLE_MISMATCH`.
  - A reassessment-only kind inside a selection closure → `REFERENCE_KIND_MISMATCH`.

## 2. Code-review-ready diff

| Item | Value |
|---|---|
| Edited (dispatch only) | `applications/bounded_decision_workflow/cli.py`: +3 lines (`checked-` → `checked_cli.main`) |
| New application modules | `checked_contracts.py`, `checked_derivation.py`, `checked_applicability.py`, `checked_selection.py`, `checked_reassessment.py`, `checked_runtime.py`, `checked_cli.py` |
| New data file | `checked_temperature_schemas.json`, byte-identical to the v3 `schemas.json` (SHA-256 `e1cafb83…9910`, pinned and checked at import) |
| New tests | `tests/checked_temperature/`: `__init__.py`, `fixtures.py` and 8 test modules (122 test functions; 140 collected cases) |
| Patch (outside the repository) | `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd/review/gate1-code-r2.diff` (4,157 lines; SHA-256 `7ad6ffa57962ee6f544170106cf6c72adeabad1fb6c56b6f5e57706b5f8f22af`). The earlier `gate1-code.diff` is superseded but retained. |
| Reproduce | `git diff -- applications/bounded_decision_workflow/cli.py` plus `git diff --no-index /dev/null <file>` for each new file |

**Unchanged:**

- legacy modules;
- backend;
- existing tests and assertions;
- dependencies;
- the lock;
- historical evidence;
- every preparation package;
- the pre-existing changes to `.gitignore` and `bounded_pytest_runner.py`.

## 3. Launch log (G1 allowance: 40 launches; 9 used)

**Setup:**

- Interpreter: `cp313-bdw001` (CPython 3.13.11, lock-exact).
- Flags: `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`, and a fresh
  `--basetemp=<ws>/launch-NN/tmp` per launch.
- Workspace: `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd/` (ext4).
- The full log is `launch-log.jsonl` in that workspace (argv, exit, elapsed time,
  usage before and after).

| # | Selection | Exit | Outcome | Cumulative usage after (logical B / files / dirs*) |
|---|---|---|---|---|
| 01 | baseline, twins, kind/role | 1 | 19 setup errors: application defect (blanket rejection of finite floats; the legacy public evidence carries `1794.0`) | 27,427 / 2 / 1 |
| 02 | same | 1 | 3 failures: test-fixture defect (`co1` mutated a shared world, leaking objects between twins; the application correctly refused them as unrelated) | 32,140 / 5 / 2 |
| 03 | same | 0 | 20 passed | 32,991 / 7 / 3 |
| 04 | `tests/checked_temperature` | 0 | 123 passed (double `-q` suppressed the summary line; counted from the progress output) | 1,071,188 / 213 / 21 |
| 05 | `tests/checked_temperature` | 1 | 7 failed, 121 passed: harness defects (rehashed twins did not carry new digests into `trace.json`/`result.json`, which the new trace-annotation check correctly caught; F13 padding contents were identical and deduplicated) | 2,113,549 / 419 / 39 |
| 06 | `tests/checked_temperature` | 0 | 128 passed | 3,151,599 / 625 / 57 |
| 07 | the 5 named legacy files | 1 | **9 failed, 212 passed** (§6) | 3,161,286 / 627 / 70 |
| 08 | `tests/checked_temperature` | 0 | 130 passed | 4,199,593 / 833 / 88 |
| 09 | `tests/checked_temperature` (after the review fixes, §9) | 0 | **140 passed** | 5,723,843 / 1,088 / 111 |

\* The launcher counts directory entries including pytest's `*-current` symlinks.
`find -type d` reports 71 real directories.

**Measured usage after launch 09 plus the review artifacts:**

| Measure | Used | Allowance |
|---|---:|---:|
| Logical bytes | 5,953,048 | 536,870,912 |
| Physical bytes | 10,039,296 | — |
| Files | 1,090 | 20,000 |
| Directories | 88 real (111 counted) | 5,000 |

Nothing was deleted. Every failed launch's stdout, stderr and tmp tree is
retained.

## 4. Obligation-to-test mapping (v3 witness matrix)

| Witness | Cases | Tests (`tests/checked_temperature/…`) |
|---|---|---|
| W01, W02 | FX1, SC1 | `test_baseline_vertical`: fx1 bundle, derivation, scores, applicability, closure, verify/replay |
| W03 | UN1, UN3, UN4 | `test_baseline_vertical::test_un1_*`; `test_reassessment_witnesses::test_un3_*`, `test_un4_*` |
| W04, W05 | LB1, PM1 | `test_selection_witnesses::test_lb1_*`, `test_pm1_*` |
| W06, W07 | PS1–PS5, PB1 | `test_reassessment_witnesses::test_ps1_*`, `test_ps2_*`, `test_changed_plan_refusals[PS3,PS4,PS5]`, `test_pb1_*` |
| W08 | HW0, HW5, HW5p | `test_selection_witnesses::test_hw0_hw5p_*`, `test_hw5_*` |
| W09 | OB2, OB3, OB4 | `test_reassessment_witnesses::test_ob2_*`, `test_ob3_*`, `test_ob4_*`; `test_selection_witnesses::test_ob4_*` |
| W10 | CB1–CB3 | `test_selection_witnesses::test_cb1_*`, `test_cb2_*`, `test_cb3_*` |
| W11 | AG1–AG14 | `test_aggregation::test_ag1_*` … `test_ag14_*`, plus disjoint review covers, missing required review, and partial declaration cover |
| W12 | DC1–DC3 | `test_aggregation::test_dc1_*`, `test_dc2_*`, `test_dc3_*` |
| W13 | PO1–PO5, A1 | `test_selection_witnesses::test_po1_*` … `test_po5_*`, `test_a1_allowlist_*` |
| W14 | IN2–IN11 | `test_closure_and_verify::test_in2_*` … `test_in5_*`; `test_selection_witnesses::test_in6_*`, `test_in7_*`, `test_in8_*`; `test_reassessment_witnesses::test_in9_*`, `test_in10_*`; `test_adverse_twins::test_in11_*` |
| W15 | BE1 | `test_selection_witnesses::test_be1_*` |
| W16 | F1b, F2b, F4, F5b, F6, F8–F13 | `test_selection_witnesses::test_f*`; `test_reassessment_witnesses::test_f4_*` |
| W17 | T2a, T2b | `test_selection_witnesses::test_t2a_t2b_*` |
| W18 | EO1–EO13 | `test_adverse_twins::test_eo1_*`, `test_eo4_*`; `test_kind_and_role::test_eo2_*`, `test_eo3_*`; `test_reassessment_witnesses::test_eo5_*`, `test_execution_target_and_scope_substitutions[EO6,EO8,EO10]`, `test_eo7_*`, `test_eo9_*`, `test_changed_plan_refusals[EO11,EO12]`, `test_eo13_*` |
| W19 | CL1–CL9 | `test_baseline_vertical::test_un1_closure_*`, `test_un1_verify_standalone_*`; `test_adverse_twins::test_cl2_*`, `test_cl8_*`; `test_closure_and_verify::test_cl3_*` … `test_cl7_*`, `test_cl9_*` |

**Further obligations covered:**

- issuer roles;
- annotation versus enforcement;
- build not permitted, and replay requiring the exact recorded build
  (`HISTORICAL_BUILD_UNAVAILABLE`);
- trace annotation targets;
- `APPLICABILITY_MISMATCH`;
- invocation-kind consistency;
- the captured policy tightening the unique-object cap;
- CLI:
  - the real process entry point refuses;
  - usage errors;
  - path publishing with the manifest last;
  - `OUTPUT_COLLISION`;
  - objects-dir naming;
  - reassessment through paths.

**Not covered in Gate 1:**

- **IN1** (submitted cached-derivation comparison): not implemented, because
  CONTRACT §7.1 defines no argument for it.
- **F3** (caller-supplied decoder content): not representable. The schema has no
  decoder field; editions are fixed in code.
- **Reassessment boundaries:** the 400-object and 2,621,440-byte reassessment
  limits are enforced but not boundary-tested.
- **Per-case invocation matrix:** Gate 1 checks each case's semantic outcome in
  process. The 179-invocation CLI matrix belongs to Gate 2, which is deferred.

## 5. Test doubles and executable identity

- **`TestDoubleBuild`** (`tests/checked_temperature/fixtures.py`) is labelled in
  code as **not an executable identity**. Its identity fields are all-zero or
  `TEST_DOUBLE` markers. The schema's `clean_application_backend` constant forces
  it to read `true`; that field is therefore meaningless for the double and proves
  nothing about a clean build.
- **The double is never reachable from the process entry point.**
  `checked_cli.main` always uses `ExecutableBuild`, the maintained clean-tree,
  exact-lock identity.
- **Real entry point refuses.** In this uncommitted tree the real command refuses
  with `BUILD_NOT_PERMITTED` at target `/build/current_build_identity_unavailable`
  (`test_cli::test_process_entry_point_refuses_without_a_clean_executable_identity`).
  The check was not weakened.

## 6. Preserved failures

| Launch | Cause | Classification |
|---|---|---|
| 01 | `parse_canonical` rejected all finite floats. That rule is not in the contract, and it rejected the genuine legacy evidence. | Application defect, fixed (finite floats allowed; NaN and Infinity still refused; closed `ct.*` schemas admit integers only). |
| 02 | Shared fixture world leaked objects between twins | Test defect, fixed (`World.clone`) |
| 05 | Twin harness left stale digests in `trace.json`/`result.json`; F13 padding deduplicated | Test-harness defects, fixed (digest propagation; distinct padding) |
| 07 | 9 legacy tests (`test_assessment.py::test_real_captured_semantic_path` × 5 and `test_admission.py::test_production_capture_then_admit` × 4) raise `REPLAY_BUILD_UNAVAILABLE`. They compute the maintained executable identity, which requires clean, committed `applications/` and `backend/`. The new uncommitted checked modules make the tree dirty. | **Not a code regression.** This is the clean-build/commit requirement, reported separately in §7. The other 212 legacy tests pass. The v3 PLAN static screening did not catch this dependency. |

## 7. Clean-build and commit requirement (reported separately)

The following can only pass once the checked modules and `cli.py` are committed,
which is not authorized here:

- the 9 legacy identity-dependent tests;
- every real-entry-point success path;
- Gate 2.

After an authorized commit the maintained identity would be recomputed (a
re-baseline, owner decision D9). The vendored schema file is a data file; it is
outside the build source manifest, which covers `.py` files and the lock. It is
bound instead through `contract_editions.schemas_sha256` and the import-time pin.

## 8. Unresolved findings (owner decisions; not silently resolved)

| ID | Finding | Implementation choice |
|---|---|---|
| F1 | The v3 `schemas.json` fixes the captured-policy `edition` at `ct.policy-edition.v2`, while v3 CONTRACT §5 requires v3. No schema-valid record can carry v3. | Accept the schema label `v2` (any other label refuses `POLICY_EDITION_MISMATCH`). Enforce the v3 edition content (39 limits). A schema correction needs a successor package. |
| F2 | The refusal catalogue has no code for "current executable identity unavailable" and none for CLI usage | `BUILD_NOT_PERMITTED` with target `/build/current_build_identity_unavailable`; `CLI_USAGE` (exit 2) is outside `policy.json` |
| F3 | No contract join between `result.observation` and the result public evidence | Legacy reconstruction under the evidence's own question time, plus a subject/variable anchor join; no value join |
| F4 | Reassessment requires claims only for the executed procedure (contract: "nominated procedure × condition for the request's phase") | Executed procedure only |
| F5 | Base64 closure data necessarily exceeds `string_bytes` (4,096) | `closure.json` parsing exempts member data from `string_bytes`. File and decoded caps still apply. |
| F6 | Carried prior computed records can reference unsupplied required claim cores (a blocked prior) | Such a prior refuses `PRIOR_BUNDLE_MISMATCH` (`carried_reference_unresolvable`); no silent `REFERENCE_MISSING` |
| F7 | Witness F12b expects `RESOURCE_LIMIT_EXCEEDED` for 65 reviews, but schema `request.reviews` maxItems 64 refuses first at stage 2 | The test asserts `SCHEMA_INVALID` and is labelled with this finding |
| F8 | The evaluation authority's `valid` window has no enforcement rule in the contract | Not enforced. The execution authority's window must contain the acquisition (c2). |
| F9 | v3 PLAN's legacy-file screening missed the clean-tree identity dependency | Reported (§6, §7) |

Independent read-only review: see §9.

## 9. Independent review and fixes

A read-only `code-reviewer` subagent reviewed the work. It ran no tests,
imported no code and edited no files. Its report is retained at
`<workspace>/review/gate1-review.md`, SHA-256
`7e99c25591b3685bb3dcb25d6c95259e162741089cda8bc195809b207a75852a`. It is model
output, not owner approval.

The review confirmed several things:

- the schema is byte-identical to the approved copy;
- the `cli.py` change is exactly the 3-line dispatch;
- design §4 and §5 hold for well-formed graphs;
- pins, roots, reachability and the descriptor binding resist rehash attacks.

I verified every finding below against the code before fixing it. Each fix has
a schema-valid twin test that reaches the intended code and target in
launch 09.

| Review item | Defect | Fix | Twin |
|---|---|---|---|
| **C1 (critical)** | A supplied opposing review bound to a required claim could fall out of aggregation as "unbound". This happened when its item was reachable only through the review, or when its claim was not among the item's claims. The claim then read `supported`, violating fixed design §5. | Stage 4 now refuses such a review (`SCHEMA_INVALID`, `/reviews/<d>/item_claim_binding`). | `test_c1_review_cannot_drop_out_of_aggregation` (2 variants) |
| I1 | Verify did not require `closure.json` to be the canonical closure record, so member kind labels went unchecked | Verify rebuilds the record and requires equality (`REFERENCE_KIND_MISMATCH`) | `test_i1_mislabelled_closure_member_is_refused` |
| I2 | A missing descriptor member raised `KeyError` (internal error) | Refuses `REFERENCE_MISSING` | `test_i2_missing_descriptor_member` |
| I3 | Malformed legacy `nm.evidence.v1` raised `KeyError` | Refuses `SCHEMA_INVALID` (`/nm.evidence.v1`); result evidence is shape-guarded | `test_i3_malformed_legacy_evidence_*` |
| I4 | Deep nesting raised `RecursionError` before the depth limit applied | Refuses `RESOURCE_LIMIT_EXCEEDED` | `test_i4_deep_nesting_*` |
| I5 | P0 and the carried prior selection were trusted without recomputation | The prior derivation, applicability and selection are recomputed from the carried prior closure under the carried prior build and compared (`PRIOR_BUNDLE_MISMATCH`, `/…_recomputed`) | `test_i5_carried_prior_selection_is_recomputed` |
| I6 | Verify ignored the plan-change disclosures and `use_disposition` | Added to the mandatory-metadata comparison (`SCORE_METADATA_INVALID`) | `test_i6_*` (2 tests) |
| I7 | The CLI test target held only in a dirty tree | Accepts either target (dirty: identity unavailable; clean: `/build` is not in the fixture policy) | (test corrected) |
| I8 | Objects and bundle directories were read without count or total caps | Objects-dir: at most 400 entries and at most 2,621,440 total bytes; bundle directory: exactly 9 entries checked before reading | `test_bundle_directory_must_hold_exactly_nine_files` |
| M2/M3 | Manifest roles were unchecked; a malformed prior manifest could raise `KeyError` | Each (name, role) pair must match its bundle kind, for own and prior manifests | (existing tests) |
| M6 | Subprocess or OS failures while computing identity became internal errors | Mapped to `BUILD_NOT_PERMITTED` (identity unavailable) | — |
| M8 | Test names overclaimed | A1 test renamed to what it shows; CL9 now asserts the stray digest | — |

**Residual minor items, not changed (owner visibility):**

- **M1:** a few stage-4 checks run inside the stage-5 routine. This affects only
  multi-defect precedence; every single-defect witness is unaffected.
- **M4:** captured-policy tightening of `object_bytes`, `string_bytes`,
  `json_depth`, `json_nodes`, `integer_digits`, `trace_entries` and
  `rational_operations` is recorded but not applied. Those limits act at edition
  level, before the policy is known.
- **M5:** `contained` is necessarily true when `w > 0`; it is reported as
  computed.
- **M7:** an internal error maps to exit 7. The contract has no internal-error
  exit class.
- **M9:** a pinned evaluation authority with purpose `execution` refuses
  `AUTHORITY_SCOPE_MISMATCH`. The contract names no code for this case.
- **M6 remainder:** a schema-pin mismatch at import surfaces as a traceback, not a
  diagnostic.
- **CONTRACT §1.1 wording:** the claim "validated by the existing
  public-evidence validator semantics" holds for snapshot reconstruction and
  joins. The `nm.basis` references inside `token_roles` are neither carried nor
  checked.

END OF GATE 1 TDD REPORT
