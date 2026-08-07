# TS-001 Temporal Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Rebuildable SQLite projection of DS-004 acquisition/observation
evidence into an attempt ledger, temporal occurrences with six-dimension
keys and exact change classes, immutable clock-segment openings, and
historically-closed as-of queries — with zero changes to `data_sources`.

**Authority:** the spec
(`docs/superpowers/specs/2026-08-08-ts001-temporal-projection-design.md`)
for every contract field, ordering rule, halt policy, and query-closure
requirement; ADR-0005 for store/boundary decisions.

## Global Constraints

- `data_sources` untouched (proven by evidence-hash test); DS-001–004
  suites (338) stay green at every commit; no push.
- Zero new dependencies (stdlib sqlite3 + existing pydantic).
- Full six-dimension temporal keys and the four-field AttemptOrderKey in
  every lookup, constraint, and index; determinism asserted on ordered
  logical dumps only.
- Extraction incompleteness persists nothing; late/inconsistent state
  yields TEMPORAL_REBUILD_REQUIRED, never silent repair or skips.
- All time-relative queries take caller-supplied cutoffs; no wall-clock
  reads inside the module.

## Tasks

### Task 0: Spike (hard gate)
Prove: WAL journal behavior; per-attempt transaction rollback;
`BEGIN IMMEDIATE` contention -> typed busy on actual write contention
with an unaffected concurrent reader; foreign-key enforcement; ordered
logical-dump determinism across two databases (bytes differing);
per-source transactional rebuild reader visibility (old-or-complete);
exact db/-wal/-shm sidecar deletion; canonical path-containment
rejection. Stop and amend the design if any item fails. Record results
in the spec.

### Task 1: Contracts + store
Tests then code: refs, AttemptOrderKey, TemporalAttemptEvent,
TemporalOccurrence (received_at non-null), ClockSegmentOpening,
checkpoint, report, typed errors; SQLite schema with deterministic PKs,
six-dimension indexes, meta versions; txn helper (`BEGIN IMMEDIATE`,
busy_timeout=0); `ordered_logical_dump()`; path guard.

### Task 2: Projector
Tests then code: full-order-key sorting of evidence attempts; checkpoint
validation matrix (missing+ledger -> reconstruct; mismatch/ahead/behind/
version -> rebuild-required; never repair); per-attempt transactions with
under-txn rechecks; outcome classification; per-(domain, marker) segment
resolution from observations with mixed-marker flagging; exact change
chains keyed on all six dimensions; halts (incompleteness unpersisted;
late attempt -> rebuild required).

### Task 3: Queries + rebuild
Tests then code: `latest_observed` (single query, required as_of,
historically closed, five-way later-coverage distinction), history,
change_history, attempt_coverage, freshness, provenance chain,
clock_segments; `rebuild(source_id)` in one transaction;
`rebuild_all(source_ids)` offline with exact sidecar handling.

### Task 4: Scenario suite + verification
All spec acceptance scenarios against evidence stores built with the
existing DS-004 transport stub + frozen fixtures (including in-test
synthesized decreasing-eventtime and zero-observation payloads); crash
injection; evidence-immutability hash sweep; module README; full suite;
base-only and all-extras clean checkouts; evidence report. No push.
