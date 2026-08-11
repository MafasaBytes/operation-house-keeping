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

## SN-001 structural subject namespace (`sx1:`)

Structural mappings are ordinary `binding_assertion` records whose
subject `adapter_id` is the eight-component `sx1` namespace —
`sx1:family:extractor-name:extractor-version:config-fp:toolchain-fp:
rule-id:rule-fp` — binding the identity to the exact interpretation
mechanism that produced it. Set selection is forced by anchor ownership
(same-set validation is all-or-nothing): mappings targeting the extruder
live in `demo-printer/`; the assembly-type mapping lives in
`demo-printer-model/` beside its declaration. Applicability is asserted
on the ingestion-receipt axis only and carries no lifecycle-view
validity.
