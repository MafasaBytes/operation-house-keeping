# FC-001 final design owner approval

## 1. Accepted inputs and baseline

The owner approves the corrected final synthesis and authorizes documentation
reconciliation and Slice A only, on `fc001` from local `main` at
`c0e1c8fe930e10243fec16a4950a3d34d4c85df4`. Local `origin/main` remains
`d888ba6fbfb313cf2f85ce5cb07168fb528ec059`; the difference is the accepted
documentation-only FA feasibility closeout.

Frozen inputs remain byte-identical:

| Artifact | SHA-256 |
| --- | --- |
| [Lead proposal](../proposals/2026-09-09-fc001-codex-lead-proposal.md) | `8a65e3a4721fc0ba3dc28b0772e920f2dcc3008a9e1411ce07c9a8d1b204749e` |
| [Challenger audit](2026-09-09-fc001-codex-lead-proposal-challenger-audit.md) | `35d8537e2b1dc17775e2e96b0c021c4387ee1b6cd02265d861d17974b6e3d94f` |
| [Final synthesis](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md) | `7aa5007058c1733720fc624839c19efd98258c800c67461d1afc5ade674a3453` |

All 27 owner decisions, C1, and N1–N5 are normative. Approval does not edit
historical design-only wording in those frozen artifacts. This record is the
subsequent execution authority, including allocation of
[ADR-0022](../../adr/0022-explicit-flow-operating-criterion.md).

## 2. Exact authorized capability

An authority designates one exact CRG/VCN edition for one exact FM effective
body through a mandatory retained FMA witness. The witness is never silently
substituted. Its own current endorsement is not required when another healthy
active FMA supplies the identical body, as evaluated only in Slice B.

Use immutable FM subject S as the correction key and one governing slot per S.
Same-root forks conflict even for equal bodies; independent equal bodies
corroborate; active different bodies disagree; inactive roots do not veto.
Several legitimate mandatory criteria for S remain unsupported, not false,
and must not be encoded through artificial contexts or orientations.

Exactly `FlowOperatingCriterionDeclaration` (`fcd_`) and
`FlowOperatingCriterionWithdrawal` (`fcw_`) extend the existing kernel ledger.
Positive evidence/authority are mandatory; withdrawal has no evidence and is
uncitable. No anchor, minter, registration, sibling store, evaluator, upper
dependency, authoritative append or Slice B public contract is authorized.

## 3. Execution clarification, not a design amendment

The owner explicitly resolves the execution prompt's stale-support wording:

> rejection of stale content-derived IDs, support substitution, missing support, and invalid structural closure, while preserving valid historical support for Slice B applicability evaluation.

Mutated content under an unchanged canonical ID rejects. Missing, forged,
wrong-kind, cross-subject, mixed-membership or closure-invalid support rejects.
Structurally valid retained support loads and replays after correction,
supersession or withdrawal. Support currentness is not an admission/store
requirement except where the frozen synthesis expressly requires it at that
boundary. No Slice A applicability/currentness status or conclusion is added.
VSM remains context-independent. The post-green adversarial review must prove
all three sides: invalid closure rejects, retained history survives, and Slice B
conclusions remain absent. No additional design challenger pass is required.

## 4. Consumer, truth boundary and FA gate

The initial consumer is commissioning/operations verification, one criterion
and one nominated candidate. Slice A supplies durable governing designation,
not the complete consumer answer. Evaluation remains CN's responsibility.
FC never establishes satisfaction, violation, state, physical flow, activity,
occurrence, continuity, conservation, causality, correctness, safety, diagnosis,
recommendation, planning or permission to act.

FA remains deferred during FC. Cancel FA after the separately accepted direct
join proof if an FC query, existing CN result and existing evidence disclosures
answer the approved question. Reconsideration requires a new owner-approved
proposal demonstrating a concrete integrity/substitution attack unpreventable
through explicit checks over existing public results, identifying the missing
property and why checks fail. No currently identified attack justifies FA.
Combined-validator absence, convenience, aggregate status, reduced size or
deduplicated carriage cannot justify it.

## 5. Preservation and acceptance gate

Preserve 36 authoritative records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
inventory digest `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`,
FRG/FLD/FLW 1/1/0, TRG/TRD/TRW 0/0/0, FMA/FMW 0/0, and FCD/FCW 0/0.
Preserve all accepted identities, bytes, revisions, ledgers and artifacts.
Local settings remain unchanged and uncommitted at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

The [Slice A plan](../plans/2026-09-09-fc001-slice-a-implementation-plan.md)
and [matrix](../plans/2026-09-09-fc001-slice-a-adversarial-acceptance-matrix.md)
govern red-first implementation, post-green specialized review, full and both
clean-checkout columns. Commit the completion report only after verification.
Stop for owner acceptance; Slice B is unstarted and unauthorized. No push or
merge is authorized.

END OF FC-001 FINAL DESIGN OWNER APPROVAL
