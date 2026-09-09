# ADR-0021 — Explicit flow-to-measurement association

Date: 2026-09-07

Status: FM-001 complete and owner accepted at exact tested implementation
`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`; no Slice C or demonstration

The authoritative design blob at the exact tested implementation is:
[`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`](../superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md),
SHA-256 `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7`.
Its current path now contains only the final status reconciliation after that
tested implementation.

Correction record:
[`docs/superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md`](../superpowers/reports/2026-09-07-fm001-final-contract-correction-report.md).

Accepted Slice A evidence and decision:

- [`docs/superpowers/reports/2026-09-07-fm001-slice-a-completion-report.md`](../superpowers/reports/2026-09-07-fm001-slice-a-completion-report.md);
- [`docs/superpowers/reports/2026-09-09-fm001-slice-a-owner-acceptance.md`](../superpowers/reports/2026-09-09-fm001-slice-a-owner-acceptance.md).

Accepted Slice B contract records:

- [`docs/superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md`](../superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md);
- [`docs/superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md`](../superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md);
- [`docs/superpowers/reports/2026-09-09-fm001-slice-b-contract-correction-report.md`](../superpowers/reports/2026-09-09-fm001-slice-b-contract-correction-report.md).

Owner acceptance and implementation authorization:
[`docs/superpowers/reports/2026-09-09-fm001-slice-b-contract-owner-acceptance.md`](../superpowers/reports/2026-09-09-fm001-slice-b-contract-owner-acceptance.md).

Accepted Slice B completion and final owner decision:

- [`docs/superpowers/reports/2026-09-09-fm001-slice-b-completion-report.md`](../superpowers/reports/2026-09-09-fm001-slice-b-completion-report.md), SHA-256 `f7ce3280a6d1af1682b6ef1139fc8d8d2166c26e56525c703029f03586d8c290`;
- [`docs/superpowers/reports/2026-09-09-fm001-final-owner-acceptance.md`](../superpowers/reports/2026-09-09-fm001-final-owner-acceptance.md).

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

The accepted Slice B surface contains exactly five read-only query
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
rows use strict indices only. The owner accepted these exact contracts at
`7bb7db8ec27af74bdd887d763222757c1f1fc821` and accepts their implementation
at `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`. FM-001 is complete.

## Truth boundary

An FM declaration does not establish an observation, sensor placement, value,
rate, amount, unit compatibility, active or occurred flow, continuity,
conservation, balance, causality, correctness, safety, diagnosis,
recommendation, or physical occurrence. FM does not read evidence or temporal
stores, select observations, calculate signs, convert units, or assess flow.

Accepted Slice A is limited to records, canonical/store/replay/DAG/withdrawal
integrity, and immutable indexes. Accepted Slice B is limited to the five
read-only queries and authoritatively reconstructed results. There is no Slice
C or demonstration slice. FA-001 remains separate and unauthorized.

END OF ADR-0021
