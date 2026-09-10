# CS-001 Proposal Correction Report

2026-09-10 — bounded documentation corrections accepted by the owner.

## 1. Frozen inputs and scope

Before editing, branch `main` and baseline HEAD
`4ad1a5812e01490bf40aaa8079936f038488e6f9` were verified. The only initial
working-tree entries were the untracked proposal and challenger audit. Both
frozen SHA-256 checkpoints matched exactly. No discrepancy was found.

| Artifact | SHA-256 |
| --- | --- |
| [Proposal before correction](../proposals/2026-09-10-cs001-codex-lead-proposal.md), frozen 728 lines / 64,913 bytes | `691f3ab913995100d7beb81a2327ac21f4ea42a1fe2c95e8ac68cf6128446550` |
| Same proposal after RC-1/RC-2 correction | `ab816af9a96aa0578b29cd8209e3e0f1530ac8a02dac455a5538b58d460372c1` |
| [Frozen challenger audit](2026-09-10-cs001-codex-lead-proposal-challenger-audit.md), unchanged | `ebbe452695019d6f83a3a775149c8370125110c58461380f38a39e1092f37859` |

The owner accepts the audit verdict `approve_with_corrections` and both required
corrections. Only RC-1 and RC-2 alter the proposal; no policy profile, numerical
bound, coverage semantics, architecture alternative or lower contract changes.
The proposal's original unapproved/review-pending and task-scope statements
remain historical drafting context. The separate
[application-policy owner decision](2026-09-10-cs001-application-policy-owner-decision.md)
records their final disposition; they are not rewritten as part of these two
corrections. The audit is preserved byte-for-byte, including historical wording.

## 2. RC-1 — receipt evidence, not physical measurement freshness

| Location in corrected proposal | Precise correction |
| --- | --- |
| Section 1 question/outcome; section 3 necessity example and classification | Replace an implied physical-measurement refresh requirement with receipt-age-conditioned evidence usability. |
| Section 7 outcome table | Remove normative `fresh_measurement_required`; use disposition `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`. Acquisition/evidence refresh is an optional workflow response, not the policy's physical claim. |
| Section 8 examples 2, 5, 7, 8 and arithmetic commentary | Apply the same disposition/reason to age failure, source-time non-rescue, threshold twins and policy replay; arithmetic and thresholds remain unchanged. Example labels explicitly refer to receipt-age admissibility. |
| Section 8 valid reused-payload/rereceipt twin | A distinct valid receipt at 21:00:05 evaluated at 21:00:06 has receipt age 1 second; unchanged payload/observation/source time may pass the explicit P2 age bound when exact coverage and all joins pass. Independently bind the new occurrence, cutoff and snapshot; retain every origin/run/seed dependency. |
| Sections 9–11 alternative wording, objective 4 and CS-A22/CS-A24 | Propagate use/not-usable semantics; refreshing one nominated evidence path remains an application choice, not a mandated new physical measurement. |

The reused-payload twin is a design counterexample, not a newly appended
fixture or newly captured observation. Its arithmetic and lower reuse semantics
are sufficient to disprove the old label: a later valid receipt of byte-identical
evidence can meet the rule without establishing a new physical measurement.
Editing the old receipt while retaining its expected fingerprint remains an
inconsistency, not the valid twin.

Receipt-age failure does not establish that the physical measurement is stale,
that a new physical measurement is necessarily required, that byte-identical
rereceipt is insufficient, or that the observation is false. The existing CN
verdict remains retained as its historical evaluation, separately from policy
usability. Source-observed/effective time cannot rescue receipt-age failure.

## 3. RC-2 — honest multiple exact matches

| Location in corrected proposal | Precise correction |
| --- | --- |
| Section 5, join step 5 | Honest `multiple_matching_candidates` with otherwise valid inputs maps to `criterion_evaluation_unavailable`; retain the lower reason and `multiple_matches` relation. Never pick first. |
| Section 7 incoherence trigger | Remove multiple exact candidate matches as an intrinsic inconsistency. Actual identity/revision/cutoff/candidate/carried-result inconsistencies, failed reconstruction and mismatched independent commitments still reject. |
| Section 7 unavailability trigger | Explicitly include honest lower multiple-match ambiguity without rewriting it into a CN reason or claiming malformed input. |
| Section 8 valid ambiguity twin | Two legitimate paths to the same full occurrence yield lower `not_aligned` / `multiple_matching_candidates` / `multiple_matches` and application `criterion_evaluation_unavailable`. The unique-match twin proceeds through the remaining gates. Forged candidate duplication remains incoherent. |

No candidate-selection algorithm, tie breaker, validation relaxation or new
result contract is introduced. The exact lower reason stays authoritative.

## 4. Documentation and authority disposition

The [owner decision](2026-09-10-cs001-application-policy-owner-decision.md)
accepts the post-FC reconciliation and closes CS-001 without implementation as
commissioning application policy, not deferred architecture. Root README,
CLAUDE status guidance and the model-kernel README's stale investigation-status
sentence now point to that decision. No successor milestone is approved;
ADR-0023 remains absent and unallocated.

The closeout commit contains only seven Markdown paths: the corrected proposal,
the unchanged audit, this report, the owner decision, `README.md`, `CLAUDE.md`
and `backend/model_kernel/README.md`. The audit/proposal were untracked inputs
at the verified baseline; recording the unchanged audit is not an audit rewrite.
No accepted reconciliation, ADR, FC acceptance, source/test implementation,
fixture, canonical record, membership or generated artifact is edited.

## 5. Verification and preservation

Verification is bounded to documentation/status assertions, corrected-proposal
structure/marker and RC assertions, changed-document links, ADR numbering and
absence checks, accepted ledger/revision/exports and witness preservation,
frozen audit/reconciliation digests, and working/staged/full post-FC range
whitespace checks. Exact command outcomes and artifact receipts are supplied
after execution in the terminal receipt.

Executed closeout checks passed: 31 existing documentation/status/export
assertions; 62 local links across the seven closeout documents; corrected
proposal sections 1–13, 25 attack/twin rows, arithmetic, RC-1/RC-2 and ending
marker; correction sections 1–5 and decision sections 1–6 with exact markers;
22 contiguous unique accepted ADRs; exact frozen audit/reconciliation digests;
all protected inventories, ledger/replay/revision and ordered exports; and both
accepted witness byte lengths/digests below. Working, staged, full post-FC
range and new-file whitespace checks passed before commit; final post-commit
checks and the clean-tree result are reported in the terminal receipt.

The existing focused documentation/status/export assertion selection is the
31-check command recorded in section 12 of the
[accepted reconciliation](2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md).
The accepted FC/integrated witness reproducer is reused unchanged with
`PYTHONPATH=.` and `PYTHONDONTWRITEBYTECODE=1`, using fresh temporary material
only; no existing witness, fixture or ledger is overwritten. It verifies:

| Preservation checkpoint | Required value |
| --- | --- |
| Authoritative model load/replay | 36 records; `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FCD/FCW and FMA/FMW | `0/0` and `0/0` |
| Model-kernel exports | Exactly 236; ordered digest `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |
| FC witness | 14,677 bytes; `a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca` |
| Integrated witness | 174,490 bytes; `1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e` |
| Protected inventories | Six trees / 65 files, accepted digests unchanged; ignored local settings also unchanged |
| ADRs | Unique, contiguous accepted ADR-0001 through ADR-0022; no ADR-0023 |

Whitespace ranges include the working tree, staged closeout, and the complete
post-FC reconciliation range from `7693f1acf763f652947dff28b5dbb8a8dfee2505`
through the final closeout HEAD, not merely the immediate parent commit.
A complete repository or clean-checkout matrix is unnecessary and was not run
for this documentation-only closeout. Historical coverage of 4,074 passing
tests remains historical; it is not a fresh full-suite claim.

The repository verification-before-completion skill informs fresh evidence and
these limited claims. No implementation, new runtime/test contract, successor
proposal, branch, ADR allocation, push, merge or history rewrite is authorized
or performed. The only forward commit requested is
`docs: close CS-001 as application policy`.

END OF CS-001 PROPOSAL CORRECTION REPORT
