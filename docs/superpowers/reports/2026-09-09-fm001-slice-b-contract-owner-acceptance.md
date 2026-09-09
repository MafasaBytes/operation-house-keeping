# FM-001 Slice B Contract Owner Acceptance

Date: 2026-09-09

Status: corrected Slice B public contract owner accepted; Slice B
implementation only authorized; FM-001 not yet complete

## 1. Accepted checkpoint

The owner accepts the corrected FM-001 Slice B public contract exactly as
recorded on branch `fm001` at
`7bb7db8ec27af74bdd887d763222757c1f1fc821`.

Repaired Slice A remains accepted at exact tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`; its administrative acceptance
commit is `6625fb89b49235444887b285f98eb7bc6a2ab7f0`.

## 2. Accepted authorities

The accepted corrected authorities are:

- synthesis
  `docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`,
  SHA-256
  `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7`;
- implementation plan
  `docs/superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md`,
  SHA-256
  `1bf6c8835d799186795478c337e12df9446e0b16d494d412604d07d6717922f2`;
- adversarial matrix
  `docs/superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md`,
  SHA-256
  `6f4d6927b41bb97089c4b4277c064b9cc6371ffa68375b36af36954d617c8200`;
- contract-correction report
  `docs/superpowers/reports/2026-09-09-fm001-slice-b-contract-correction-report.md`,
  SHA-256
  `7597a31c4e2dc240296350f4e21b24425bad3a971c3fd91ecc397920db1b3f4a`;
- ADR-0021
  `docs/adr/0021-explicit-flow-to-measurement-association.md`, SHA-256
  `71bb00e57132e982fb4243968c24f8b5b24072da03c879bb3d61ac5b1d56d671`.

Those accepted bytes freeze the five read-only methods, 11 aliases, four
nested rows, five outer results, exact 20-name append to the 205-name Slice A
export prefix, 225 total exports, carry-once material, support reachability,
mixed-root disclosure, authoritative reconstruction, purity, and FM-A01–FM-A58.

## 3. Authorized implementation scope

Authorization is limited to the accepted Slice B query/result implementation,
focused tests, bounded independent reviews, verification, and an uncommitted
completion report. The implementation may add only the five `ModelQueries`
methods and the exact accepted result surface inside `backend.model_kernel`.

It may not change Slice A records, canonicalization, IDs, store validation,
ledger membership, fixtures, existing artifacts, lower or upper packages. It
may not append FMA/FMW records, create a facade, store, identity, second
consumer, fixture, demonstration, occurrence claim, or FA-001 behavior.

## 4. Verified starting state

Before this administrative commit, the branch was clean at the accepted
checkpoint. The applicable documentation/status and flow-architecture gate
passed 32 tests in 11.77 seconds. The synthesis, plan, matrix, correction
report, and ADR digests matched Section 2, and working whitespace checks
passed.

The authoritative ledger remained exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
with FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, FMA/FMW `0/0`, and aggregate
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The 660,516-byte FL disclosure remained SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
Accepted lower, TA, VSM, model, identity, historical, report, fixture,
artifact, and settings digests remained unchanged.

## 5. Owner gate

This document accepts the corrected Slice B contract and authorizes only its
implementation. It does not claim Slice B or FM-001 is implemented, verified,
complete, or finally accepted.

There is no Slice C or demonstration. Final FM-001 acceptance requires a
separate owner decision after review of the exact tested implementation and
uncommitted completion report.

END OF FM-001 SLICE B CONTRACT OWNER ACCEPTANCE
