# Contract amendment C2: T1 receipt-time closure

**Date:** 2026-10-05. **Status:** owner-approved successor amendment (the narrow
receipt-time closure). It is recorded separately. Frozen C1 is not edited.

**It amends:**

- C1 `docs/superpowers/specs/2026-10-05-checked-temperature-contract-amendment-c1/`,
  `MANIFEST.json`
  `791b4035807ce032f7852447df0e0b7d9324c8cb90d52bc8a1b6ebac42ab9d1a` (verified;
  preserved byte-for-byte);
- specifically C1.1 rule 1 and C1.5. C1.1 rules 2–4, C1.2 and C1.3 remain in
  force.

**Base:** v4 (`9e0afa32…`). Its `schemas.json`, `policy.json`, record shapes and
refusal codes are unchanged.

## C2.1 Rule (supersedes C1.1 rule 1)

**Locate the occurrence.** Through the evidence binding's
`constraint_evaluation_index` and `semantic_candidate_index`, locate the single
observed occurrence:
`…candidates[i].value_candidate.state_candidate.bound.observed.occurrence`.

Its `occurrence_id` must equal the admitted occurrence.

**Both instants in the window.** From that same occurrence, **both**
`received_at` and `finished_at` must lie within the closed
`[acquisition.started, acquisition.ended]`.

Otherwise the refusal is `RESULT_EVIDENCE_MISMATCH`
(`/result/acquisition/public_evidence/acquisition_window`).

**Unchanged:**

- `acquisition.started` ≥ `model.context.as_of` (C1.1 rule 2);
- the owning upstream validation (C1.1 rule 3);
- the check order (C1.1 rule 4), with this rule in the final position.

## C2.2 Meaning

`received_at` is the backend's governed instant: `effective_wall_time` on the
`ingestion_received_at` applicability axis. Requiring it in the window closes
the demonstrated retained-evidence substitution (C1 TC5b, which substituted only
`finished_at`).

This is a declared-time consistency check. It does **not** authenticate
chronology, and it does **not** promise rejection of coherently reconstructed
synthetic evidence.

## C2.3 Supersession of C1.5

C1.5 ("Unresolved: `finished_at`-only substitution") is resolved by C2.1. The
historical observation that TC5b was **accepted** under C1.1 is retained, in
`witnesses-c1.json` (`observed`) and in launches 13–15. It is not rewritten.

## C2.4 Witness cases

The cases are in `witnesses-c2.json`.

END OF AMENDMENT C2
