# models/

Committed model-kernel ledgers (see `backend/model_kernel/` and
`docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`). One
model set per directory; one write-once JSON record per file under
`records/`, named by its content-derived SHA-256 `record_id`. Records are
never edited in place — corrections and withdrawals are new records, and
`append` validates the complete set before every write.

`demo-printer/` is the accepted validation model, currently 29 synthetic
records under `test_fixture` authorities. Its explicit historical memberships
preserve the 9-record MK-001 model, VM-001, VS-001, SN-001, ES-001, CN-001, and
the 28-record PT-001 fixture. VP-001 adds exactly one parentless, role-free,
same-owner variable-to-port association and no withdrawal or correction. Its
anchors remain declared in `bindings/demo-printer/` and
`bindings/demo-printer-model/`; those binding ledgers are not modified by the
VP append. The fixture makes no claim about a real printer. Historical
revisions remain provable by `replay()` from explicit record-ID lists; a
directory enumeration or prefix filter is never an acceptable membership
selector.

The bounded VP-001 disclosure is documented in `demo-printer/README.md`,
including the exact synthetic-fixture disclaimer and the warning that showing
variable state beside an associated port does not make the observation a port
fact.
