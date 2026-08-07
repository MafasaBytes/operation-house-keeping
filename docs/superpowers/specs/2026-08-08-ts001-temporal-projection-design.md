# TS-001 Temporal Evidence Projection — Design

Date: 2026-08-08
Status: Approved for implementation (two amendment rounds + final owner
constraints, all incorporated). TS-001 is a **rebuildable source-native
temporal evidence projection — never a claim about actual system state**.

## Boundary

```
backend/temporal_state/     new sibling module
  contracts.py  store.py  projector.py  queries.py

temporal_state ──reads──▶ data_sources     (contracts + store, read-only)
data_sources   ──never──▶ temporal_state   (no data_sources changes)
```

Scope: attempt-bearing operational evidence only. Excluded: system
hierarchy/tree, identity binding, domain state labels, validity
intervals, unit inference, polling/commands, Excel, `data_sources`
changes of any kind. Evidence-store immutability is proven by test
(file hashes before/after projection).

## Contracts (final)

```
SourceSubjectRef   { source_id, adapter_id, subject_identifier }
SourcePropertyRef  { extraction_route, item_key, json_pointer }
```

The temporal property key is the **complete six-dimension pair**; every
previous-occurrence lookup, change chain, uniqueness rule, query, and
index uses all six dimensions — two adapters or routes with identical
subject names and pointers can never contaminate each other.

```
AttemptOrderKey = (attempt_started_at, ingestion_run_id,
                   sweep_position, attempt_id)
```

The single deterministic processing order, used everywhere (checkpoints
persist all four fields; as-of queries tie-break by the same components
after effective_wall_time).

**TemporalAttemptEvent** (immutable ledger row, PK = attempt_id): source/
adapter/endpoint/item identifiers, sweep_position, ingestion_run_id, the
three ingestion timestamps, `effective_wall_time` +
`effective_time_basis (received_at | finished_at_no_response)`,
`outcome (observations_projected | acquisition_failed | quarantined)`,
raw_record_id/payload_checksum (successes), `observation_count` (zero is
a real result), failure_or_quarantine_code, source_warning_count,
projector_version. **No source-clock marker columns**: a zero-observation
extraction exposes no `SourceTimeMarker` through DS-004 contracts and the
temporal layer never parses raw payloads or reproduces adapter semantics.
Zero-observation snapshots are fully represented by their ledger row,
ordered on the acquisition/receipt axis only; a later observation may
reveal a monotonic decrease and open a segment then. The ledger is the
processed-attempt proof, the atomic parent of occurrences, and the
coverage backbone (there is **no separate gap table** — outcome carries
it).

**TemporalOccurrence** (immutable, PK = derive(attempt_id,
observation_id)): the six key dimensions, provenance ids (attempt,
observation, raw record, checksum), the order-key fields, **`received_at`
non-nullable** (successful attempts always have it; effective wall time
of an occurrence IS its received_at), verbatim `SourceTimeMarker` fields,
`clock_segment_id | None`, value_json/json_type/declared_unit,
`change_class (first_seen | unchanged | changed)`,
previous_occurrence_id, quality_flags (may include
`possible_source_clock_reset`, `ordered_by_acquisition_time_only`,
`mixed_source_time_snapshot`).

**ClockSegmentOpening** (immutable opening evidence, never updated —
no closing or last-value field): segment_id = derive(source_id,
adapter_id, clock_id, opening attempt_id), the clock-domain key,
`boundary_reason (initial | monotonic_decrease_observed)`,
opened_by_attempt_id, opened_at_effective_wall_time.

**ProjectionCheckpoint** (mutable optimization only): source_id + all
four AttemptOrderKey fields + projector/schema versions.

**ProjectionReport** (returned, never persisted): counts by outcome,
`deferred_incomplete`, `halted {source_id, reason
(extraction_incomplete | TEMPORAL_REBUILD_REQUIRED), at_attempt_id}`.

Typed errors: `TemporalConfigurationError`, `TemporalStoreBusyError`,
`TemporalStoreError`.

## Source-time domains and segmentation

Clock information derives **only from `OperationalObservation.source_time`**:

- monotonic → domain `(source_id, adapter_id, clock_id)`; a decrease
  versus the domain's last observed marker (derived from occurrences,
  never from checkpoints) opens `monotonic_decrease_observed` and flags
  the carrying observations `possible_source_clock_reset` — proving only
  that *a decrease was observed in acquisition processing order*, never
  that the source restarted. Equal/increasing markers stay in the
  segment.
- wall_clock → domain `(source_id, adapter_id, "wall_clock:"+basis)`;
  initial segment only, no wall-clock reset inference in TS-001.
- unavailable → `clock_segment_id = None` +
  `ordered_by_acquisition_time_only`.
- No source time is ever converted to another basis; monotonic values
  are never compared across segments as a shared origin.

Segments are resolved **once per distinct (domain, marker) represented
by an attempt's observations** — the core does not assume one uniform
marker per attempt. If one attempt carries different markers for the
same domain, they are processed deterministically (observation order:
sorted json_pointer) and every observation in that domain for that
attempt gains `mixed_source_time_snapshot`; the discrepancy is never
hidden.

## Projection algorithm

```
project(source_id):
  path guard: canonical temporal DB path is rejected at or inside the
              evidence-store root (TemporalConfigurationError)
  version check: meta/checkpoint projector+schema versions must match the
              running projector, else halt TEMPORAL_REBUILD_REQUIRED —
              never silently repaired
  checkpoint = load(source_id)                    # optimization only
  ledger_max = max AttemptOrderKey in temporal_attempts for source
  if checkpoint is None and ledger_max exists:    # reconstruct safely —
      checkpoint = ledger_max                     # no segment state lives
                                                  # outside the ledger/
                                                  # occurrence rows
  elif checkpoint set and checkpoint != ledger_max (ahead, behind, or
      ledger empty): halt TEMPORAL_REBUILD_REQUIRED

  for attempt in evidence attempts sorted by FULL AttemptOrderKey:
      if key(attempt) <= checkpoint:
          if attempt_id not in ledger:            # ground truth, never the
              halt TEMPORAL_REBUILD_REQUIRED      # watermark: late attempts
          continue                                # are never skipped or
                                                  # inserted behind chains
      BEGIN IMMEDIATE                             # one txn per attempt
        re-read ledger membership + checkpoint under the txn
        outcome failed      -> ledger row (acquisition_failed)
        quarantined         -> ledger row (quarantined)
        extraction missing  -> ROLLBACK; deferred_incomplete; HALT source
                               (nothing persisted, checkpoint unchanged —
                                incompleteness is a projection condition,
                                not source evidence; after upstream
                                reconstruction the attempt projects
                                normally with no residue)
        else:
            pre-scan observations -> domains, distinct markers, mixed set
            ledger row (observations_projected, observation_count)
            per observation (sorted json_pointer):
                resolve/cache segment for (domain, marker)
                previous = latest occurrence for the FULL 6-dim key by
                           AttemptOrderKey order
                change_class by exact (json_type, value_json)
                insert occurrence
        advance checkpoint to key(attempt)
      COMMIT
```

## SQLite store

Derived, rebuildable; single file (configurable path, guarded), WAL,
`foreign_keys=ON`, parameterized statements only, deterministic primary
keys, schema/projector version metadata. **Writer model (honest)**: one
active write transaction at a time via `BEGIN IMMEDIATE` per attempt with
`busy_timeout=0`; actual write contention raises typed
`TemporalStoreBusyError` — no lifetime lease, no pretend `writer_token`;
concurrent projector calls interleave safely only at transaction
boundaries because deterministic ids and under-transaction rechecks
preserve correctness; readers operate concurrently under WAL.
**Logical rows are deterministic; SQLite/WAL/SHM bytes are explicitly
not** — determinism is asserted on ordered logical dumps.

## Rebuild

- `rebuild(source_id)`: **one SQLite write transaction** covering removal
  (that source's occurrences, segment openings, ledger rows, checkpoint)
  and full deterministic replay — readers see the old projection or the
  complete rebuilt one, never a committed empty/partial source. Other
  sources untouched.
- `rebuild_all(source_ids)`: explicit **offline** maintenance requiring
  closed readers/writers; deletes exactly the configured database file
  and its exact `-wal`/`-shm` sidecars — never a directory or computed
  broad path — then recreates and replays. No whole-file byte-determinism
  or online-replacement claims.

## Queries (all take an explicit caller-supplied cutoff where time-relative)

1. `history(subject, property)`; 2. `latest_observed(subject, property,
as_of)` — single query, required cutoff, **historically closed**: every
component (occurrence choice, staleness = as_of − received_at,
intervening failed/quarantined attempt counts for the item,
`later_snapshots_without_property` (observations present, this property
absent), `later_empty_snapshots` (observation_count == 0), latest
applicable attempt outcome, source-time basis + segment flags) computed
solely from rows with effective_wall_time ≤ as_of, tie-broken by the
AttemptOrderKey components. The five later-coverage cases (no later
attempt / failed / quarantined / non-observing snapshot / empty
snapshot) are all distinguishable and none is ever called deletion,
null, or unchanged; 3. `change_history`; 4. `attempt_coverage` (ledger);
5. `freshness(source_id, as_of)`; 6. `provenance(occurrence_id)` — full
chain to attempt, observation, raw record, checksum;
7. `clock_segments(source_id)`.

## Task 0 spike (hard gate)

WAL behavior; per-attempt rollback; `BEGIN IMMEDIATE` contention
(typed busy on actual write contention only; concurrent reader
unaffected); foreign-key enforcement; logical-dump determinism (bytes
may differ); per-source transactional rebuild reader visibility; exact
sidecar handling; path-containment rejection.

### Task 0 spike results (2026-08-08 — gate PASSED, 16/16)

WSL2 Ubuntu x86_64, CPython 3.13.11, stdlib sqlite3 (SQLite bundled with
CPython): WAL active; mid-attempt rollback leaves zero rows across both
tables; second `BEGIN IMMEDIATE` writer receives the lock error mapped to
the typed busy error while a concurrent WAL reader is unaffected and sees
commits afterwards; foreign keys reject orphan occurrences; two databases
loaded in different insert orders produce identical ordered logical dumps
with differing file bytes (logical-only determinism confirmed);
delete+replay of one source inside a single transaction shows a
snapshot reader the OLD rows mid-rebuild, a fresh reader the COMPLETE
rebuilt rows, and the other source untouched; the exact db/-wal/-shm
sidecars are individually removable; canonical path-containment logic
rejects the evidence root and children while accepting siblings and
dot-dot paths that resolve outside.

## Acceptance scenarios

First sweep (`first_seen`); byte-identical re-poll (new occurrences, all
`unchanged`); changed payload (`changed` only for affected pointers);
reused server_info content with new occurrences; failure between sweeps
surfaced via ledger coverage in `evidence_quality`; quarantine with zero
fabricated values; omitted fields age without deletion; monotonic
increase (one segment); monotonic decrease (new opening,
`possible_source_clock_reset`); unavailable source time (basis flags,
segment None); offline projection; idempotent re-projection (ordered
logical dumps); crash mid-attempt rollback + identical resume;
zero-observation snapshot (ledger row, count 0, later-empty-snapshot
reporting, no clock participation); late attempt behind watermark →
TEMPORAL_REBUILD_REQUIRED, never skipped; checkpoint loss → safe
reconstruction, no fabricated segments; checkpoint ahead/behind/version
mismatch → rebuild required; as-of closure before/between/after and
under later ingestion; mixed-marker snapshot flagging; per-source
rebuild preserving the other source; full rebuild; two-source isolation;
busy-writer typed error; path rejection; evidence-store immutability
(hash sweep); DS-001–004 suites (338) preserved; dual clean-checkout.
