# BRC-EXP-001 Slice A owner acceptance

## 1. Owner decision and administrative checkpoint

On 2026-09-12 the owner accepts Slice A experimental execution at branch
`brc-exp001`, starting HEAD `33cb997f2eaee1301801c9b4c165abb7e32a7416`.
This documentation closeout records acceptance; it does not rerun the experiment.
Slice A is complete and owner accepted. The overall BRC-EXP-001 experiment remains
incomplete. Slice B/Mode B remains unauthorized. No successor milestone, IN-001,
CI-001, production implementation or ADR is authorized.

## 2. Exact accepted evidence

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Final execution report](2026-09-12-brc-exp001-slice-a-final-execution-report.md) | 5,715,759 | `5a101e9815d4561d1b2fad6a678eb93c3250d395385efe044d270c85840ea5b2` |
| [Hostile-target correction report](2026-09-12-brc-exp001-slice-a-hostile-target-correction-report.md) | 49,463 | `7fa1c6db658fb2c9d6c12aedb0bdb4138322dd468188e1ef1bfbe3869cfffc0c` |

Both report bytes and ending markers were verified and preserved. Their historical
pending-acceptance wording describes the execution checkpoint; this separate
record supplies owner acceptance without modifying the accepted reports.

Strict base64 decoding, zlib recovery and canonical JSON verification recover the
44,144,528-byte self-contained archive, SHA-256
`4f5d5c7a3730b22ec6236e027175504e6fac155ca0372345475dd131079e6838`.
All 292 canonical objects rehash and reserialize exactly; all role references
resolve internally. The archive retains exact request/result and mutation bytes,
oracle comparisons, 13 source artifacts with commitments, policy/templates,
resource telemetry and full-execution determinism evidence. No standalone
candidate file or external store is necessary to recover this accepted evidence.
This closeout verifies retained evidence, not a new semantic re-execution.

## 3. Verified execution evidence and accepted conclusion

Recovered records confirm seven cohort requests, 40 registered controls and the
approved supplemental cases: 61 roles covering 59 distinct outputs. The two
overlaps are primary/producer-unique-match and BH-equal/natural-under-limit.
All 210 recorded checks pass, including targeted dynamic semantic-read mutations
and valid twins. All 12 combinations of seeds 1/7/313, two temporary roots and
normal/reversed permissible construction order report identical complete
canonical execution objects and commitments. These are recovered execution
checks, not newly rerun tests or 210 independent domain cases.

Within the explicit synthetic hypotheses, measurement candidates and compatibility
premises, `finite_compatibility_minimax/v1` correctly filters candidates and
performs bounded minimax ranking. The primary actual result has T1 worst-case
survivors 1 versus T2 worst-case survivors 2. T1 is preferred within the explicitly
supplied candidate set under that algorithm.

Acceptance does not establish premise accuracy, premise derivability, real fault
identification, causal truth, global hypothesis completeness or globally optimal
test selection. Hypotheses/predictions remain assumed; computed scores and bounded
inference do not become observations or authoritative engineering truth. Objective
3 receives bounded supplied-candidate filtering evidence, objective 4 receives
within-set worst-case discrimination evidence, and objective 7 receives epistemic
classification preservation evidence. Objectives 5 and 6 remain open.

The hostile-target correction is accepted exactly, not as an oracle wildcard.
Both carried parents pass public reconstruction; subsequent duplicate-locator
coherence rejects the hostile input and admits the unique-match twin. The exact
public target remains mandatory. The eleven designated execution-disclosure
differences remain confined to their approved field; unrelated comparisons are
not weakened. Earlier failed executions retain their historical failures.

## 4. Resources, preservation and verification scope

Accounting remains canonical wire nodes plus deterministic resolution charges.
Recounting all recovered role objects confirms input maximum 11,567 and result
maximum 13,453. Input operational limit remains 12,000; result limit remains
13,453; safety ceiling remains 16,384. M_A_support remains 7,680. The natural
12,355-node input guard is recorded refused before owning reconstruction, with
zero owning and algorithm calls. All byte, depth, cardinality and reference
limits remain unchanged. Incremental output enforcement and bounded nonrecursive
refusal-template evidence remain part of the accepted archive.

Fresh read-only preservation checks confirm 36 authoritative records, revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
236 model-kernel exports and FMA/FMW/FCD/FCW 0/0/0/0. ADR-0023 remains absent,
unallocated and unreserved. No production source/test, fixture, ledger, identity,
canonical artifact, cap or historical report is changed by this closeout.

Focused digest, archive recovery, documentation/status, local-link, marker,
preservation and whitespace checks apply before and after the documentation
commit, including recovery from committed report bytes. The recorded execution
and production verification are reused with attribution; neither minimax nor the
full production suite is rerun. The disposable driver and tests were already
deleted; their deletion was confirmed. This is accepted experimental execution,
not retained or promoted production code.

## 5. Retention and remaining question

The scoped documentation commit retains only the two accepted reports, this
acceptance record and necessary approved synthesis/plan amendments. Exact
canonical evidence is recoverable from the committed report/archive. Standalone
candidate JSON, backups and other historical owner-gate files remain untracked,
unchanged and intentionally unstaged; a clean worktree is not manufactured by
staging or deleting them. No push, merge or history rewrite is authorized.

The remaining Mode B question is whether existing public model contracts can
derive the hypothesis, measurement-procedure and conditional-prediction premises,
while separating absent semantics from sparse population through independently
approved controls. Slice A does not answer that question or establish prediction
accuracy. Any Mode B work needs separate owner authorization and separately
approved premises. No further execution is authorized by this acceptance.

END OF BRC-EXP-001 SLICE A OWNER ACCEPTANCE
