# ADR-0021 — Explicit flow-to-measurement association

Date: 2026-09-07

Status: FM-001 corrected final design and repaired Slice A owner accepted;
corrected Slice B contract pending owner approval; Slice B implementation and
demonstration unauthorized

Authoritative design:
[`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`](../superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md),
SHA-256 `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7`.

Correction record:
[`docs/superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md`](../superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md).

Accepted Slice A evidence and decision:

- [`docs/superpowers/reports/2026-09-07-fm001-slice-a-completion-report.md`](../superpowers/reports/2026-09-07-fm001-slice-a-completion-report.md);
- [`docs/superpowers/reports/2026-09-09-fm001-slice-a-owner-acceptance.md`](../superpowers/reports/2026-09-09-fm001-slice-a-owner-acceptance.md).

Corrected future Slice B contract records:

- [`docs/superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md`](../superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md);
- [`docs/superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md`](../superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md);
- [`docs/superpowers/reports/2026-09-09-fm001-slice-b-contract-correction-report.md`](../superpowers/reports/2026-09-09-fm001-slice-b-contract-correction-report.md).

## Decision

FM-001 belongs in the existing `backend.model_kernel` ledger. It adds one
atomic positive declaration, `FlowMeasurementAssociation`, and one uncitable
withdrawal, `FlowMeasurementAssociationWithdrawal`, over existing
FlowAnchor, VariableAnchor, and participant PortAnchor identities. It adds no
durable association anchor and no new ledger.

The v1 claim is direct-measurement relevance only. The locus is exactly one
registered participant port from the flow's FRG signature. Source/sink is
derived from FRG membership and never stored as caller data. Exact same-
revision FRG/VRG/PRG/FLD/VPA/measured-actual-VSM support is mandatory. VSM
support is context-independent and proves the exact variable plus the
measured-actual observation-role token; only FLD and VPA must match the exact
FMA assertion context.

The positive record uses the existing generic `build_record` surface and the
`fma_` prefix. The withdrawal uses `fmw_`, has no evidence field, and is not
accepted by ModelRecordEvidence. Immutable subject dimensions are flow,
variable, participant port, exact context, implicit direct-measurement
relevance, and explicit orientation.

Correction DAGs, independent-root corroboration/disagreement, same-root
conflict, membership-relative replay, and selective uncitable withdrawal
follow accepted model-kernel precedent. Repaired Slice A is owner accepted at
exact tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`.

The corrected future Slice B surface retains exactly five read-only query
methods. It adds exactly 11 aliases, four nested rows, and five outer results:
20 ordered additions after the accepted 205-name Slice A export prefix, for
225 total `backend.model_kernel.__all__` names. The five methods are methods
only; there is no public FM builder, free-function alias, facade, store, or
second consumer.

Each positive effective-body group and found positive assertion has exactly
six ordered FRG/VRG/PRG/FLD/VPA/VSM support rows. Pinned activity, containing-
lineage health, and current alignment are separate. Permanent registrations
cannot acquire assertion lifecycle states, and context-independent VSM cannot
acquire context, withdrawal, withdrawn activity, or inactive health.

Root rows disclose lineages only. Effective-body group rows disclose current
bodies and their six support rows. A conflicted root may participate in
several groups and selects none; mixed healthy, conflicted, inactive,
corroborating, and cross-root disagreeing states remain simultaneous ordered
findings under one explicit aggregate-conclusion precedence. One reverse
entry represents one complete immutable subject in the requested context.
Every outer result carries one complete `ModelQueryMaterial` once, and nested
rows use strict indices only. These corrected Slice B contracts are not yet
owner accepted or authorized for implementation.

## Truth boundary

An FM declaration does not establish an observation, sensor placement, value,
rate, amount, unit compatibility, active or occurred flow, continuity,
conservation, balance, causality, correctness, safety, diagnosis,
recommendation, or physical occurrence. FM does not read evidence or temporal
stores, select observations, calculate signs, convert units, or assess flow.

Accepted Slice A is limited to records, canonical/store/replay/DAG/withdrawal
integrity, and immutable indexes. A future authorized Slice B is limited to
the five read-only queries and authoritatively reconstructed results. There is
no Slice C or demonstration slice.

END OF ADR-0021
