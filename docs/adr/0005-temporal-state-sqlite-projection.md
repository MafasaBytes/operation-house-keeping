# ADR-0005: temporal_state as a sibling module with a rebuildable SQLite projection

Date: 2026-08-08
Status: Accepted (project owner; two amendment rounds + final constraints)

## Context

The completed `data_sources` boundary persists immutable evidence:
content-addressed raw records, per-occurrence acquisition attempts,
canonical operational observations with discriminated source-time
markers, and honest failure/quarantine outcomes. The next layer must
answer temporal questions (latest observed value, history, change,
coverage, freshness, provenance) without touching that evidence and
without claiming actual system state.

## Decisions

1. **Sibling module, one-way dependency.** `backend/temporal_state/`
   reads `data_sources` contracts and store read-only; nothing in
   `data_sources` changes or may import back. Hierarchy, identity
   binding, and constraints remain future sibling modules; TS-001
   contracts are framed as temporal *evidence*.

2. **SQLite (stdlib) as the derived temporal store.** Compared against
   the write-once filesystem pattern: the projection is derived and
   rebuildable — not evidence — and its workload is indexed history/
   latest/as-of lookups with an atomic-per-attempt commit requirement.
   SQLite provides per-attempt `BEGIN IMMEDIATE` transactions, WAL crash
   safety, concurrent readers, and deterministic uniqueness constraints
   at zero dependency cost. The filesystem pattern stays authoritative
   for evidence; deriving queries from it would re-implement indexing
   and multi-file atomicity by hand.

3. **Determinism claim is logical, not physical.** Ordered logical dumps
   from the same evidence and projector version are byte-identical;
   SQLite/WAL/SHM file bytes are explicitly outside the claim.

4. **Attempt ledger as ground truth.** `TemporalAttemptEvent` rows prove
   processing; the checkpoint (full four-field AttemptOrderKey) is an
   optimization that must equal the ledger maximum — any inconsistency,
   or a projector/schema version mismatch, halts with
   TEMPORAL_REBUILD_REQUIRED rather than silent repair. Late attempts
   ordering at or before the watermark whose ids are absent from the
   ledger also require rebuild — history chains are never rewritten in
   place. Checkpoint loss reconstructs safely from the ledger because no
   segment or chain state lives anywhere except immutable rows.

5. **Clock evidence from observations only.** Segment resolution derives
   exclusively from `OperationalObservation.source_time` (per distinct
   domain and marker within an attempt; mixed markers flagged, never
   hidden). No raw-payload parsing, no adapter semantics in the temporal
   core, no ledger marker columns: zero-observation snapshots order on
   the acquisition axis only. A monotonic decrease is recorded as
   `monotonic_decrease_observed` / `possible_source_clock_reset` — an
   observation about ordering, not a restart assertion.

6. **Honest writer model.** One active write transaction at a time;
   `busy_timeout=0` turns actual write contention into a typed
   `TemporalStoreBusyError`; no lifetime lease is pretended. Per-source
   `rebuild` is a single transaction (readers see old or complete);
   `rebuild_all` is documented offline maintenance handling the exact
   database and sidecar paths only. The temporal database path is
   canonically resolved and rejected at or inside the evidence-store
   root.

## Consequences

- Every temporal fact traces attempt → observation → extraction → raw
  record → checksum, and the whole projection can be deleted and rebuilt
  from evidence alone.
- Query answers carry their time basis and evidence quality; "latest
  observed" is the strongest wording the layer ever uses.
- A future `identity_binding` module can map `SourceSubjectRef` (full
  six-dimension keys with `SourcePropertyRef`) to system entities by
  join, without rewriting temporal history.
