# models/

Committed model-kernel ledgers (see `backend/model_kernel/` and
`docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`). One
model set per directory; one write-once JSON record per file under
`records/`, named by its content-derived SHA-256 `record_id`. Records are
never edited in place — corrections and withdrawals are new records, and
`append` validates the complete set before every write.

VP-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. The final implementation HEAD before the
administrative acceptance commit is
`82fcb93b233db180d5d2d6c54d465dad390f08a5`. The accepted VPA is
`vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`;
its file SHA-256 is
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`.
The pre-VP revision is
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`;
the final revision is
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
The VP artifact SHA-256 is
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
the PT artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
Displaying variable state beside a port does not mean the observation occurred
at, originated at, travelled through, or describes the port.

`demo-printer/` is the accepted validation model, currently 36 synthetic
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

BH-001 Slice D is implemented and adversarially reviewed from the owner-
approved pre-append contract at `0905de0`. It appends exactly
one neutral VRG, one BRG, and one parentless BHD to the explicit 29-record VP
membership. The resulting explicit 32-record revision is
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
The owner-approved pre-append candidate disclosure artifact is 122406 bytes
with SHA-256
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
It reports `not_executed`; no binding or missing semantic/state evidence was
fabricated. Its candidate/proposed fields record the frozen rehearsal scope;
the byte-identical reproduction does not relabel them as current state.
BH-001 complete, owner accepted, adversarially reviewed, full-suite verified,
and dual-clean-checkout verified. Acceptance does not convert `not_executed`
into observed equality or real-machine truth.

ST-001 is complete and owner accepted at implementation HEAD
`0f05903af4f11fd94d6e6987247ceb9795faebd6`. It adds exactly the frozen SRG
followed by the frozen parentless STD to the unchanged 32-record predecessor,
yielding the exact 34-record revision
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`.
There is no STW or additional record. The accepted completion-report SHA-256 is
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
Acceptance does not make `matches` a claim of current physical state,
exclusivity, completeness, transition, cause, control, safety, health,
diagnosis, correctness, or recommended action.

FL-001 Slice D adds only the owner-approved frozen FRG followed by its
parentless FLD. The resulting explicit 36-record revision is
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
the 34-record ST-001 membership remains the exact historical predecessor.
There is one FRG, one FLD, and zero FLW. The fixture declares one synthetic
logical directed flow in exact `as_designed` context; it does not establish
physical flow, activity, occurrence, observation, command, quantity,
conservation, behavior, cause, safety, health, correctness, diagnosis, or
recommended action. FL-001 Slices A, B, and D are owner accepted, Slice C is
absent from v1, and FL-001 is complete, adversarially reviewed, full-suite
verified, and dual-clean-checkout verified at implementation HEAD
`fe3b15a3caf77974a795dad5b04c0a35abee37b4`.
