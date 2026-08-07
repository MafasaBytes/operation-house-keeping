# bindings/

Committed identity binding sets: append-only ledgers of explicit identity
decisions (see `backend/identity_binding/` and
`docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md`).
One set per directory; one write-once JSON record per file under
`records/`, named by its content-derived SHA-256 `record_id`. Records are
never edited in place — corrections, closures, and retractions are new
records.

`demo-printer/` is the IB-001 validation set: synthetic anchors and
bindings with `test_fixture` authority (`ib001_demo_fixture`) and a
declared applicability interval
`[2026-08-07T20:00:00Z, 2026-08-07T21:00:00Z)` covering only the
committed deterministic fixture observations. It makes no claim about a
real printer. A real deployment records its own binding set (same
format) outside the repository, with `human_owner` authority and
genuinely known intervals.
