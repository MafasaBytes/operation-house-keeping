# Contract amendment C1: T1 acquisition-time binding

**Date:** 2026-10-05. **Status:** owner-approved amendment (the acquisition-time
closure sequence). It is recorded separately from the v4 package.

**It amends:**

- `docs/superpowers/specs/2026-10-04-checked-temperature-contract-preparation-v4/`,
  `MANIFEST.json`
  `9e0afa328c3281fd468be21911f7840a74a35cdafd616b3f79605eaebd5df529`
  (preserved byte-for-byte);
- specifically v4 CONTRACT §12.3, the paragraph "Pending owner choice C1". That
  paragraph is superseded by §C1.1–C1.4 below.

**Unchanged:**

- v4 `schemas.json` (`43c2af0b…`) and `policy.json` (`46df039b…`, edition
  `ct.policy-edition.v4`);
- the record shapes;
- the refusal codes;
- every other v4 clause.

## C1.1 Rules (T1 reassessment only)

1. **Occurrence window.** Admit the T1 result evidence through the owning legacy
   validator. Its observed occurrence `finished_at` is located through the
   evidence binding's `constraint_evaluation_index` and
   `semantic_candidate_index`, at
   `…candidates[i].value_candidate.state_candidate.bound.observed.occurrence`. It
   must lie within the closed `[acquisition.started, acquisition.ended]` window.
   That occurrence's `occurrence_id` must equal the admitted occurrence.
   Otherwise the refusal is `RESULT_EVIDENCE_MISMATCH`
   (`/result/acquisition/public_evidence/acquisition_window`).
2. **Not before the baseline.** `result.acquisition.started` ≥
   `model.context.as_of`. Otherwise the refusal is `SCHEMA_INVALID` at stage 4
   (`/result/acquisition/started_before_baseline`).
3. **Upstream consistency.** The evidence snapshot must satisfy the existing
   owning validator, unmodified:
   - `StateClassificationResult` reconstruction;
   - the current-condition assessment;
   - observed-value admission.

   It must also join under the evidence's own question `as_of` and the model's
   assertion context. An inconsistent substitution refuses with `SCHEMA_INVALID`
   (`/nm.evidence.v1`) through that validator. If a substitution passes the
   validator, rule 1 still applies.
4. **Check order (stage 5, inside the result-evidence step):**
   - kind;
   - instrument;
   - baseline-evidence reuse;
   - anchors;
   - legacy validation;
   - value;
   - distinct occurrence;
   - occurrence window.

## C1.2 Meaning

These are **declared-time consistency checks** over recorded instants. They do
not authenticate chronology, prove physical acquisition, or certify that a clock
was correct.

## C1.3 Evidence construction (tests)

The later synthetic evidence chain is rebuilt through the existing public
functions: no backend contract is altered and no validation is weakened.

The rebuilt elements are:

- the data_sources ingestion (scripted Moonraker transport, injected clock and
  HTTP `Date` header);
- temporal projection;
- identity-binding assertions, with applicability windows covering the new
  receipt;
- source-property interpretations, with applicability windows covering the new
  receipt;
- semantic compatibility, constraint evaluation and state classification, at the
  new `as_of`.

The model records are the baseline model revision, unchanged.

## C1.4 Witness cases

The cases are in `witnesses-c1.json`, status `new`. The original and v4
expectations are unchanged, except that every T1 reassessment fixture now
supplies later-chain evidence.

## C1.5 Unresolved: finished_at-only substitution

**Observed (TC5b).** Every copy of the occurrence `finished_at` in
retained-instant evidence was substituted with an in-window instant, and
nothing else was rebuilt. The owning validators accept that chain. They bind
`finished_at` only by equality between the occurrence and its attempt-event
copy. Rule 1 then sees an in-window instant, so the forged evidence is accepted.

**Exact constraint.** `finished_at` is not part of the governed temporal chain.
The backend's governed instant is `received_at` (`effective_wall_time`, the
`ingestion_received_at` applicability axis). Substituting `received_at` as well
is rejected by the owning validator (TC5c probe, `SCHEMA_INVALID`). No backend
contract was changed.

**Smallest owner choice (not implemented).** Also require that the admitted
occurrence's `received_at` lies in the same closed acquisition window. A
`finished_at`-only substitution then keeps an out-of-window `received_at` and
refuses (`RESULT_EVIDENCE_MISMATCH`), and a `received_at` substitution is
refused by the owning validator.

TC5b is retained as a strict expected failure until the owner decides.

END OF AMENDMENT C1
