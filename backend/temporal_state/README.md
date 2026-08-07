# temporal_state

A rebuildable, source-native **temporal evidence projection** over the
immutable `data_sources` store — what was observed when, how observations
changed, and what proves it. It is never a claim about actual system
state: the strongest wording any query uses is *latest observed*.

Design: `docs/superpowers/specs/2026-08-08-ts001-temporal-projection-design.md`;
store/boundary decisions: `docs/adr/0005-temporal-state-sqlite-projection.md`.

## Boundary

`temporal_state` reads `data_sources` (contracts + store) read-only;
nothing imports back. Attempt-bearing operational evidence only. No
hierarchy, identity binding, domain labels, validity intervals, or unit
inference — those are future sibling layers. `SourceSubjectRef` +
`SourcePropertyRef` (six identity dimensions, used in every occurrence
chain, uniqueness constraint, and property query) stay explicitly
unresolved source identity. Attempt-level coverage is honestly coarser:
failed attempts expose no extraction route, subject, or property
identity, so it scopes by `(source_id, adapter_id, item_key)` only.

## Semantics worth knowing

- **Occurrence vs content**: one `TemporalOccurrence` per successful
  attempt × observation, never deduplicated by checksum, record reuse,
  or unchanged value; the attempt **ledger** (`TemporalAttemptEvent`) is
  the coverage backbone and proof of processing — including successful
  snapshots with zero observations.
- **Change detection** is exact `(json_type, value_json)` equality →
  `first_seen | unchanged | changed`. No tolerances, no domain labels.
- **Clocks**: segment openings are immutable evidence derived only from
  observation markers; a monotonic decrease opens
  `monotonic_decrease_observed` and flags carriers
  `possible_source_clock_reset` — an observation about processing order,
  not a restart assertion. Unavailable source time ⇒ no segment +
  `ordered_by_acquisition_time_only`. Nothing is converted between time
  bases.
- **Gaps are outcomes, not values**: failures/quarantines are ledger
  rows; an absent observation is "not observed in that snapshot", never
  deletion, null, or unchanged. Extraction incompleteness halts the
  source and persists nothing.
- **Checkpoints are optimizations**: the ledger is ground truth;
  inconsistency, version mismatch, or a late attempt behind the
  watermark yields `TEMPORAL_REBUILD_REQUIRED` — never silent repair.
  Checkpoint and ledger maximum are re-read and re-validated inside
  every write transaction, and the checkpoint never moves backward: an
  attempt already present in the ledger leaves a consistent checkpoint
  unchanged (a missing one reconciles only to the verified ledger
  maximum), so interleaved projectors cannot regress it.
- **Queries** take caller-supplied timezone-aware cutoffs (a naive
  cutoff is rejected at the public boundary with
  `TemporalQueryError("TEMPORAL_NAIVE_CUTOFF")`) and are historically
  closed at them; `latest_observed` distinguishes intervening failures,
  quarantines, later snapshots without the property, and later empty
  snapshots — all attempt-level components scoped by
  `(source_id, adapter_id, item_key)`, so another adapter's attempts
  are never evidence about this one.
- **Rebuildable**: `rebuild(source_id)` is one transaction (readers see
  old or complete); it repairs source-local checkpoint/ledger
  inconsistency but refuses under a global schema/projector version
  mismatch (offline `rebuild_all` is that repair, and a rebuilt-all
  database's metadata always matches the projector that produced its
  rows). Rebuild over incomplete extraction evidence rolls the whole
  transaction back, preserves the previous projection exactly, and
  returns a public report (`halted.reason="extraction_incomplete"`,
  zero committed counters). `rebuild_all` is documented offline
  maintenance over the exact database + `-wal`/`-shm` files. Logical
  dumps are deterministic; SQLite file bytes are not claimed. The
  database path is rejected at or inside the evidence-store root.

## Verification

```bash
.venv/bin/python -m pytest tests/temporal_state/   # scenario suite
.venv/bin/python -m pytest                         # full repository suite
```

## Known limitations / next open question

Wall-clock source-time resets are not detected (initial segment only);
as-of cutoffs are ingestion-receipt-axis only; file-based (CSV/STEP/PDF)
evidence has no timeline until identity binding exists. Next milestone
decision: the identity-binding layer mapping `SourceSubjectRef` to
system-model entities.
