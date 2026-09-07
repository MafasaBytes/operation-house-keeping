# ADR-0019 — Content-bound operational evidence selection and assurance

Date: 2026-09-07

Status: EA-001 complete and owner accepted

Authoritative design:
[`docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`](../superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md),
SHA-256
`557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`.

Final owner acceptance:
[`docs/superpowers/reports/2026-09-07-ea001-final-owner-acceptance.md`](../superpowers/reports/2026-09-07-ea001-final-owner-acceptance.md).

## Context

The repository had immutable operational source evidence and a rebuildable
temporal projection, but no single read-only boundary that could capture a
bounded source/property view, reconcile source and temporal material, select
the accepted latest occurrence, and expose exactly what had and had not been
checked. Upper consumers also needed a pure way to align one selected
occurrence with one already-computed value-compatibility result without
reselecting evidence.

## Decisions

1. **EA is a read-only sibling composition.**
   `backend.evidence_assurance` composes only public DS-004 operational-reader
   and temporal-query seams. It owns no store, cache, database, ledger,
   revision, anchor, durable identity, writer, connector, or clock. Existing
   lower packages do not import it.

2. **Requests are exact and bounded.** One request names one seven-field
   DS-004 operational source/property scope, an inclusive aware-UTC horizon
   and cutoff, and the fixed receipt-time/effective-time policy. Selection is
   the latest occurrence at or before `as_of`, ordered by `received_at` and
   the complete `AttemptOrderKey`. Source time is disclosure only.

3. **Occurrence and coverage axes remain separate.** Receipt time governs
   occurrence membership and selection. Effective wall time governs attempt
   coverage, including `finished_at_no_response`. A single optional selected
   pre-horizon seed supports latest-at-or-before selection but never claims
   pre-horizon coverage or continuity.

4. **Source fences are seed aware.** Each source inventory-token call
   independently discovers the source-side latest eligible exact-property
   observation. When it is pre-horizon, the token binds exactly one seed and
   its complete mechanical closure. The temporal-selected seed ID must agree;
   neither source nor temporal evidence silently wins a disagreement.

5. **Captured-view consistency is qualified.** Selection captures initial
   source and temporal tokens, reads temporal material in one transaction,
   reads named source material once, verifies closure and parity, and captures
   final tokens. Observable change or material/fence disagreement refuses.
   This is consistency at observed fences, not a distributed transaction,
   global atomic snapshot, currentness claim, or detection after final fences.

6. **Mechanical assurance is explicit.** Store-bound capture checks same-read
   metadata digests, raw payload checksums, DS-004 provenance closure, RFC 6901
   observation content, source/temporal attempt and occurrence parity,
   deterministic selection, coverage dispositions, and fence equality. It
   makes no semantic, freshness, suitability, state, transition, flow,
   correctness, or physical-occurrence judgment.

7. **Snapshots are content bound, not authenticated identities.** A canonical
   captured snapshot carries complete source and temporal material once,
   derived routes, selected observation, horizon coverage, assurance
   disclosures, issues, fences, and a `sha256:` content fingerprint. Raw
   payload bytes are not embedded. The fingerprint is not a signature,
   identity, authority endorsement, trusted time, or truth claim; replacing a
   snapshot and its fingerprint together may remain self-consistent without
   an independently retained expected fingerprint.

8. **Validation and revalidation have different proof boundaries.** Pure
   `validate_operational_evidence_snapshot(...)` performs no I/O, fully
   reconstructs hostile nested input, recomputes all derived content and the
   fingerprint, and always reports source bytes and temporal membership as
   `not_rechecked`. Store-bound revalidation supports
   `require_equal_final_observed_membership` and
   `named_captured_artifacts`. Exact named reread is separate from current
   membership observation and never relabels frozen material as current or
   latest.

9. **Result states preserve all applicable conditions.** Selection is
   complete within the declared horizon, incomplete within that horizon, or
   refused. Integrity/parity issues refuse without a snapshot; absence and
   incomplete coverage produce a canonical incomplete snapshot. Issues retain
   normative order and carry-once rules rather than being hidden by outer
   status precedence.

10. **Alignment is one pure leaf consumer.**
    `backend.evidence_alignment` relates one already-computed EA selection to
    one already-computed `VariableValueCompatibilityResult` using complete
    occurrence equality and EA-internal endpoint closure. It performs no I/O,
    store revalidation, evidence reselection, semantic evaluation, or
    persistence. It remains the sole EA alignment consumer and is not a
    registry or generic adapter.

## Consequences

EA can reproduce and disclose a deterministic bounded captured-evidence view
and its exact proof boundary. Historical snapshots remain historical when
stores grow. Store-independent validation can prove structural and canonical
self-consistency but cannot authenticate absent source bytes. Store-bound
named reread can establish equality of captured named material without
claiming current membership.

EA-001 added no authoritative demonstration or committed alignment-result
artifact. The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
with FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`.

## Rejected alternatives and non-claims

- putting raw-file verification or cross-store orchestration inside the
  temporal projection;
- spreading evidence selection across upper semantic consumers;
- an unbounded lifetime query or silent truncation;
- a distributed-transaction or globally current snapshot claim;
- treating source time as a selection or cross-clock comparison axis;
- freshness or suitability admission;
- semantic, model, state, transition, flow, causal, or occurrence inference;
- a signature, trusted timestamp, persistent receipt, or durable snapshot
  identity; and
- a generic multi-consumer alignment framework.

END OF ADR-0019
