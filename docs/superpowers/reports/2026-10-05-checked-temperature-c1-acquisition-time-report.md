# Checked-temperature amendment C1 — acquisition-time closure report

Date: 2026-10-05. Status: **Gate 1 unit-test evidence for the owner-approved C1
step only**.

Not included: commit authorization, Gate 1 acceptance and Gate 2, which remain
separate. No staging, commits, full suite, physical acquisition, adoption,
reranking, dependency change, cleanup or remote operation was performed.

## 1. Commitments

| Item | SHA-256 |
|---|---|
| C1 amendment record `docs/superpowers/specs/2026-10-05-checked-temperature-contract-amendment-c1/MANIFEST.json` | `791b4035807ce032f7852447df0e0b7d9324c8cb90d52bc8a1b6ebac42ab9d1a` (821 B) |
| `AMENDMENT.md` | `465da554e518181fe7fedc1ed01aed7e8184d3ac525c8b9a7b0fb2a59b6cc4e1` |
| `witnesses-c1.json` (9 cases: TC1–TC6, TC5c probe) | `2da80db0203ab212c24b5e733f381cd223bad952c32863c6f24da18a171c19f1` |
| Amends v4 (`MANIFEST.json` verified before work, unchanged) | `9e0afa328c3281fd468be21911f7840a74a35cdafd616b3f79605eaebd5df529` |
| v4 `schemas.json` / `policy.json` (unchanged; no new fields or codes) | `43c2af0b…` / `46df039b…` |

**Preserved unchanged:**

- the v3, v2 and original packages;
- the Gate 1 TDD report (`02e3b29f…`), the Gate 1 repair report (`57756c0d…`)
  and the approval record (`de67a27c…`);
- HEAD `2f0afbd`, the git index `09ae83d4…`, and the pre-existing changes
  (`010b1010…`, `97999fad…`).

## 2. Implemented rules (amendment C1.1)

1. **Occurrence window.** The admitted T1 occurrence's `finished_at` (located via
   the evidence binding indices; its `occurrence_id` must equal the admitted one)
   lies in the closed `[acquisition.started, acquisition.ended]`. Otherwise
   `RESULT_EVIDENCE_MISMATCH` `/acquisition_window`.
2. **Not before the baseline.** `acquisition.started` ≥ `model.context.as_of`.
   Otherwise `SCHEMA_INVALID` (stage 4)
   `/result/acquisition/started_before_baseline`.
3. **Upstream consistency.** The unmodified owning validator, plus the model's
   assertion context and the evidence's own `as_of`.

These are declared-time consistency checks. They do not authenticate chronology
or prove physical acquisition.

## 3. Coherent later evidence chain (C1.3)

`tests/checked_temperature/later_chain.py` rebuilds every layer through existing
public functions. No backend contract was altered and no validation was relaxed.

**Rebuilt layers:**

- data_sources ingestion: scripted Moonraker transport, an injected clock from
  `2026-10-05T09:01:00Z`, and an HTTP `Date` header at the later time;
- temporal projection;
- new identity-binding assertions and source-property interpretations, with new
  record hashes, whose applicability windows cover the later receipt;
- semantic compatibility, constraint evaluation and state classification at
  `as_of 2026-10-05T09:05:00Z`, over the **unchanged baseline model revision**
  (asserted equal).

**Result:** a later occurrence (`finished_at 2026-10-05T09:01:…`) carrying the
requested value. A test asserts the chain's new record hashes and the unchanged
model revision. The chain's stores live inside each launch's basetemp (counted
storage).

The fixed timestamp in the earlier fixtures was not a backend limitation: the
chain is fully parameterizable through the public API.

**Fixtures:** every T1 reassessment fixture (`co1`) now uses later-chain
evidence. The value-variant retained-instant builder remains only for the
adverse twins.

## 4. Results (launch 15: 191 passed, 1 strict-xfail)

| Required check | Test (`test_c1_acquisition_time.py`) | Result |
|---|---|---|
| 1 Positive later result completes; standalone verify and replay | `test_tc1_*`, `test_later_chain_is_coherent_and_later` | pass |
| 2 Closed boundaries accepted | `test_tc2_closed_window_boundaries[TC2a-start, TC2b-end]`; one second outside refuses (`test_tc2_one_second_outside_refuses`) | pass |
| 3 Out-of-window occurrence refuses | `test_tc3_*` (retained-instant evidence, October window) → `RESULT_EVIDENCE_MISMATCH` `/acquisition_window` | pass |
| 4 Acquisition before the model baseline refuses | `test_tc4_*` → `SCHEMA_INVALID` stage 4 `/result/acquisition/started_before_baseline` | pass |
| 5 Inconsistent upstream timestamp substitution refuses | TC5a (naive shift of every timestamp) → the owning validator rejects it, `SCHEMA_INVALID` `/nm.evidence.v1`: **pass**. TC5c (`received_at` and `finished_at` substituted) → owning validator rejects: **pass**. **TC5b (only `finished_at` substituted, every copy) → ACCEPTED: strict xfail, unresolved (§6)** | partial |
| 6 Baseline-evidence and baseline-occurrence reuse remain refused | `test_tc6_*` → `/baseline_reuse`, `/occurrence` | pass |
| 7 Existing value, instrument, authority and uncertainty checks intact | Full `tests/checked_temperature` (191 tests). It includes the v4 RE, AV, OB, PS, EO, UN and F4 cases, now on later-chain evidence. | pass |

**Evidence classes:**

- **Test-double:** every bundle here uses the labelled `TestDoubleBuild` and
  proves nothing about a clean build.
- **Original and v4:** the original-matrix and v4 expectations are unchanged.
  Only the T1 fixture evidence source changed.
- **Legacy failures:** the 9 legacy identity-dependent failures (launch 07) remain
  unresolved until clean-build verification. They were not re-run or
  reinterpreted.

## 5. Implementation diff

Retained in `<ws>/review/`, where
`<ws>` = `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd`.

| Artifact | Lines | SHA-256 |
|---|---:|---|
| `c1-delta.diff`: exact delta from the post-repair implementation (reconstructed from `gate1-code-r4.diff`) | 389 | `999e8d6774b4dcb03db418e66ebf986304d597bb8b9a1ec40b9b69b239be6d77` |

**Files in the delta:**

- `checked_runtime.py`: C1 rules 1–2 and the docstring;
- `tests/checked_temperature/fixtures.py`: T1 `co1` evidence switched to the
  later chain;
- new: `later_chain.py`, `conftest.py` (session base directory inside basetemp),
  `test_c1_acquisition_time.py`.

Unchanged: the other application modules, the vendored schema, legacy modules,
backend, dependencies and historical evidence.

## 6. Unresolved obligation (stopped portion)

**TC5b, `finished_at`-only substitution.**

- The owning validators bind `finished_at` only by equality between the
  occurrence and its attempt-event copy (`backend/temporal_state/contracts.py`,
  in-horizon closure check). A consistent substitution of every copy passes them.
- The governed instant is `received_at` (`effective_wall_time`, the
  `ingestion_received_at` applicability axis). Substituting it is rejected by the
  validator (TC5c).

**Smallest owner choice (not implemented):** additionally require the admitted
occurrence's `received_at` to lie in the same closed acquisition window.

TC5b is kept as a **strict** xfail that documents the gap. It will fail loudly if
the behaviour changes.

## 7. Cumulative accounting (not reset)

| Launch | Selection | Exit | Outcome | Cumulative after (logical B / files / dirs counted) |
|---|---|---|---|---|
| 13 | C1 module | 1 | **2 failed**, 8 passed (preserved): a record-id regex test bug; TC5b accepted (the gap) | 11,233,123 / 1,901 / 203 |
| 14 | C1 module | 0 | 10 passed, 1 xfailed | 11,393,264 / 1,943 / 229 |
| 15 | `tests/checked_temperature` | 0 | **191 passed, 1 xfailed** | 13,864,163 / 2,438 / 385 |

**Launches: 15 of 40 used, 25 remain.**

| Measure | Used now | Allowance |
|---|---:|---:|
| Logical bytes | 13,892,133 | 536,870,912 |
| Physical bytes | 23,482,368 | — |
| Files | 2,439 | 20,000 |
| Directories | 339 real | 5,000 |

Nothing was deleted.

END OF C1 ACQUISITION-TIME REPORT
