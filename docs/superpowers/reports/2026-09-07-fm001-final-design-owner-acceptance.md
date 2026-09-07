# FM-001 Final Design Owner Acceptance

Date: 2026-09-07

The owner accepts the corrected FM-001 synthesis at
`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`,
SHA-256 `4179a46a9413ad7a666171572db058a7b71f8d8734af39ae3650e6bf100238e2`.

The accepted architecture remains refined Alternative A in the existing
`backend.model_kernel` ledger. It adds no association anchor or new ledger.
V1 is direct-measurement relevance only, participant-port only, exact-context,
and measured-actual supported by same-revision FRG/VRG/PRG/FLD/VPA/VSM pins.
Source/sink is derived from FRG. Orientation is immutable and one of
`aligned`, `opposite`, `unsigned_magnitude`, or `not_applicable`.

The generic `build_record(record_cls, **fields)` surface is preserved. Positive
and uncitable withdrawal records use `fma_` and `fmw_`. The exact future five
queries and result contracts are frozen but remain unauthorized. Slice A is
authorized only for record/canonical/store/evidence/DAG/withdrawal/replay/
index integrity and tests. Slice B, fixtures, authoritative append/demo, and
FA-001 remain unauthorized.

The six bounded corrections C1–C6 are accepted. B1–B5, RC1–RC10, and NB1–NB5
are mapped in the correction report. There are zero unresolved owner questions.
ADR-0021 is allocated for this accepted architecture; no later ADR is reserved.

The corrected design does not claim an observation, sensor placement, value,
rate, amount, current or occurred flow, continuity, conservation, balance,
causality, correctness, safety, diagnosis, recommendation, or physical
occurrence.

END OF FM-001 FINAL DESIGN OWNER ACCEPTANCE
