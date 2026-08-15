# identity_binding

An append-only ledger of **explicit identity decisions** — which canonical
entity a source-native subject represents, and which canonical variable a
source-native field refers to — plus a deterministic resolver and a
read-only bound temporal facade. The bridge:

```text
data_sources → temporal_state → identity_binding → future model kernel
```

Spec: `docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md`;
decisions: `docs/adr/0006-identity-binding-ledger.md`. Anchor value
contracts live in `backend/system_identity/` (shared with the future
kernel).

## Boundary

Reads `temporal_state` read-only (locators, queries); imports nothing from
`data_sources`; nothing imports back. Resolution is a join over existing
evidence — temporal occurrences and raw/extracted evidence are never
copied, mutated, or rewritten. No hierarchy, graph edges, fuzzy matching,
automatic discovery, unit semantics, state inference, or interpretation
mode.

ES-001 preserves this boundary: `source_interpretation` is a separate
authoritative ledger keyed by the same exact locators, but it never mints an
anchor or maps a property to one. Identity binding remains the exclusive
property-to-variable authority; interpretation only reuses the public pure
`membership()` helper.

## Semantics worth knowing

- **Ledger, not database**: one write-once JSON file per record
  (`records/<record_id>.json`), staged outside the scanned directory and
  promoted by one atomic rename, honest single-writer assumption,
  all-or-nothing set validation. `record_id` is the full SHA-256 of the
  validated record's canonical UTC-normalized serialization —
  tamper-evident and idempotent; an existing file is validated on
  re-append and never silently overwritten. Loaded revisions are
  immutable read-only views, collection keys are bound to record
  identity, and revision members are pattern-validated before any path
  is touched.
- **Correction vs replacement**: superseding an assertion means *the old
  decision was wrong*; hardware replacement is an applicability closure
  plus a **new** anchor. Retraction withdraws; rejection documents a
  refused candidate (diagnostics only). Nothing is ever edited or
  deleted, and `recorded_at` never picks winners.
- **Applicability is three-valued**: declared/unbounded/unknown boundaries
  on half-open `[start, end)` ingestion-receipt intervals. `bound`
  requires positive establishment; unknown applicability yields the
  structurally distinct `applicability_unknown` (candidates never occupy
  `resolved_target`); a differing-target UNKNOWN prevents `bound`; OUT
  assertions never compete or block; conflicts are surfaced, never
  resolved by recency or authority rank.
- **Supported membership helper**: `identity_binding.membership(scope, at)`
  is the public pure implementation of three-valued half-open applicability.
  Consumers reuse it rather than copying the boundary algorithm; it performs
  no ledger access and has no implicit clock.
- **Subject ≠ property**: the 3-dimension subject and 6-dimension
  property locators bind independently; property results carry a
  non-recursive subject context, and a positively inconsistent
  variable/entity ownership is `conflicted`.
- **Revisions replay**: every result carries the exact sorted membership;
  `load_revision(record_ids)` re-validates and resolves over an earlier
  membership from the still-present files. Knowledge-time queries are
  explicitly not provided.
- **Facade honesty**: `BoundTemporalQueries` resolves each observation at
  its own `received_at` — never `as_of`, never the query clock — and
  returns the TS-001 object verbatim under every status.

## Verification

```bash
.venv/bin/python -m pytest tests/identity_binding/   # focused suite
.venv/bin/python -m pytest                           # full repository suite
```

## Known limitations

Anchors are immutable (no label correction until a future alias record);
no interpretation convenience for unknown applicability; explicit aware
`at` required everywhere; revision replay requires the caller to retain
membership; a mistaken closure is repaired by superseding its assertion;
configuration-aware rebinding beyond declared intervals is future work.
Next milestone question: the MK-001 typed entity/relationship kernel over
these anchors.
