# ADR-0021 — Explicit flow-to-measurement association

Date: 2026-09-07

Status: FM-001 corrected final design accepted; Slice A authorized; Slice B
and demonstration remain unauthorized

Authoritative design:
[`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`](../superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md),
SHA-256 `4179a46a9413ad7a666171572db058a7b71f8d8734af39ae3650e6bf100238e2`.

Correction record:
[`docs/superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md`](../superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md).

## Decision

FM-001 belongs in the existing `backend.model_kernel` ledger. It adds one
atomic positive declaration, `FlowMeasurementAssociation`, and one uncitable
withdrawal, `FlowMeasurementAssociationWithdrawal`, over existing
FlowAnchor, VariableAnchor, and participant PortAnchor identities. It adds no
durable association anchor and no new ledger.

The v1 claim is direct-measurement relevance only. The locus is exactly one
registered participant port from the flow's FRG signature. Source/sink is
derived from FRG membership and never stored as caller data. Exact same-
revision FRG/VRG/PRG/FLD/VPA/measured-actual-VSM support is mandatory.

The positive record uses the existing generic `build_record` surface and the
`fma_` prefix. The withdrawal uses `fmw_`, has no evidence field, and is not
accepted by ModelRecordEvidence. Immutable subject dimensions are flow,
variable, participant port, exact context, implicit direct-measurement
relevance, and explicit orientation.

Correction DAGs, independent-root corroboration/disagreement, same-root
conflict, membership-relative replay, and selective uncitable withdrawal
follow accepted model-kernel precedent. Five exact read-only queries and
authoritative carry-once results are frozen for Slice B but are not
implemented by Slice A.

## Truth boundary

An FM declaration does not establish an observation, sensor placement, value,
rate, amount, unit compatibility, active or occurred flow, continuity,
conservation, balance, causality, correctness, safety, diagnosis,
recommendation, or physical occurrence. FM does not read evidence or temporal
stores, select observations, calculate signs, convert units, or assess flow.

Slice A is limited to records, canonical/store/replay/DAG/withdrawal
integrity, and immutable indexes. Slice B is limited to the five read-only
queries and reconstructed results. There is no Slice C or demonstration slice.

END OF ADR-0021
