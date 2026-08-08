# models/

Committed model-kernel ledgers (see `backend/model_kernel/` and
`docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`). One
model set per directory; one write-once JSON record per file under
`records/`, named by its content-derived SHA-256 `record_id`. Records are
never edited in place — corrections and withdrawals are new records, and
`append` validates the complete set before every write.

`demo-printer/` is the MK-001 validation model: 9 synthetic records
(`test_fixture` authority) proving root → subsystem → extruder containment
in the `as_built` view plus one view-independent `instance_of` edge. Its
anchors are declared in `bindings/demo-printer/` (the existing extruder)
and `bindings/demo-printer-model/` (three synthetic additions — a
declaration fixture, not an anchor-generation service). It makes no claim
about a real printer.
