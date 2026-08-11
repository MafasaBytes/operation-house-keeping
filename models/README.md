# models/

Committed model-kernel ledgers (see `backend/model_kernel/` and
`docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`). One
model set per directory; one write-once JSON record per file under
`records/`, named by its content-derived SHA-256 `record_id`. Records are
never edited in place — corrections and withdrawals are new records, and
`append` validates the complete set before every write.

`demo-printer/` is the accepted validation model, currently 14 synthetic
records (`test_fixture` authority): the 9 MK-001 records proving root →
subsystem → extruder containment in the `as_built` view plus one
view-independent `instance_of` edge; the VM-001 variable registration
(hotend temperature); the VS-001 variable value specification; and the 3
SN-001 records (`sn001_showcase_fixture` agent) — the
`assembly_definition_contains` type (a second, non-merging,
DEFINITION-level containment lineage, never "the hierarchy"), the
printer-assembly-type registration, and the definition-level assertion
citing the structural-source-locator evidence arm. Its anchors are
declared in `bindings/demo-printer/` (the extruder and hotend variable)
and `bindings/demo-printer-model/` (four synthetic declarations — a
declaration fixture, not an anchor-generation service). It makes no
claim about a real printer. Historical revisions remain provable by
`replay()` from explicit record-id lists; a prefix filter is never an
acceptable membership selector.
