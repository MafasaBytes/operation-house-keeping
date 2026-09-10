# CS-001 Application Policy Owner Decision

2026-09-10 — owner-accepted documentation-only closeout.

## 1. Accepted inputs and owner authority

The owner accepts the [post-FC architecture/objective/ADR reconciliation](2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md)
at SHA-256 `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5`
and baseline HEAD `4ad1a5812e01490bf40aaa8079936f038488e6f9` on `main`.
The reconciliation's recommended design investigation has now been completed;
it is not an inherited implementation slot or a deferred backend milestone.

The [independent challenger audit](2026-09-10-cs001-codex-lead-proposal-challenger-audit.md)
is accepted unchanged at SHA-256
`ebbe452695019d6f83a3a775149c8370125110c58461380f38a39e1092f37859`.
Its verdict is `approve_with_corrections`, with zero blockers and two required
corrections. Both are accepted and applied as mapped by the
[proposal correction report](2026-09-10-cs001-proposal-correction-report.md).

The [corrected proposal](../proposals/2026-09-10-cs001-codex-lead-proposal.md)
is accepted as the design record for the bounded consumer protocol, at SHA-256
`ab816af9a96aa0578b29cd8209e3e0f1530ac8a02dac455a5538b58d460372c1`.
Its frozen pre-correction SHA-256 was
`691f3ab913995100d7beb81a2327ac21f4ea42a1fe2c95e8ac68cf6128446550`.
This owner decision supersedes the proposal's historical unapproved/review-gate
language without rewriting that history beyond RC-1 and RC-2.

## 2. Final disposition — application policy, not architecture

CS-001 is investigated and closed without implementation. It is reclassified
as commissioning application policy, not deferred architecture. The named
consumer remains the commissioning/operations verification workflow.

Existing FC, FM, CN, EA, VS and evidence-alignment public results carry and
authoritatively validate all information required by the bounded question.
No missing public field, lower-layer prerequisite, integrity boundary or durable
engineering fact was demonstrated. No new backend package, shared runtime
function, durable identity, record, ledger or ADR is justified. This closeout
does not authorize even an application implementation.

The application decision is whether one exact governing criterion's nominated
evidence at an explicit receipt cutoff may be used under its explicit policy.
The result is not a new fact about the physical system. An existing applicable
governing A which is violated remains the governing check; satisfied ungoverned
B cannot replace it. Policy permission and CN satisfaction remain distinct.

## 3. Accepted corrections and semantic limits

RC-1: receipt-age failure has disposition `evidence_not_usable_under_policy`
and reason `receipt_age_exceeded`. The commissioning workflow may respond by
requesting a new acquisition or evidence refresh. The policy does not establish
that the physical measurement itself is stale, that a new physical measurement
is necessarily required, that byte-identical rereceipt is insufficient, or that
the existing observation is false.

The corrected proposal's valid rereceipt twin retains unchanged payload and
observation content with a distinct valid later receipt, complete origin/run/
seed closure, independently committed inputs and sufficient exact EA coverage.
One-second receipt age satisfies its illustrative explicit threshold without
establishing a new physical measurement. Those numbers demonstrate the label
distinction; they are not operational configuration chosen by this decision.

RC-2: an honest lower `multiple_matching_candidates` result with otherwise
valid inputs maps to `criterion_evaluation_unavailable`, retaining the exact
lower reason and `multiple_matches` relation. It is not input or revision
incoherence. Actual identity, revision, cutoff, candidate or carried-result
inconsistency still maps to `input_or_revision_incoherent`. No automatic tie
breaking, selection or weakened reconstruction is permitted.

The accepted coverage basis is exactly EA's
`complete_within_declared_horizon`, not a generic Boolean: in the exact required
scope and inclusive interval, captured routes are nonempty, a selected
observation exists and every captured attempt observed the property. Preserve
all failure/omission/quarantine, seed, reuse, membership and refusal disclosures.
This is not cadence, physical continuity, cross-source coverage or a guarantee
about all instants. Empty or incomplete coverage does not pass.

Age is receipt-side only. Source-observed/effective time cannot rescue
receipt-age failure. No cross-clock ordering or physical-time authentication
is inferred. Permission under policy establishes neither observation truth,
criterion satisfaction, physical occurrence, safety nor health. Absence,
selection refusal, coverage insufficiency, unavailability and actual
incoherence retain their separate meanings rather than becoming a generic
refresh command.

## 4. Mandatory caller configuration and retention

The commissioning application must explicitly supply and retain its policy
schema/version, authority, age threshold, inclusive/exclusive boundary
semantics, coverage requirement, exact inputs/independent commitments and
resulting disposition. Full retained policy values, not labels alone, govern
historical replay. Arbitrary hidden defaults, automatic latest-policy lookup,
implicit threshold choices or silent criterion/candidate substitution are
forbidden. Retain lower results as required for authoritative reconstruction;
do not replace them with an unsupported green summary.

Concrete thresholds, window values, policy authority, retention arrangements
and any acquisition/evidence-refresh response remain commissioning-application
configuration. They are not foundational architecture decisions or unresolved
backend prerequisites for this bounded profile. No values, physical acceptance
limits, device commands or new workflow implementation are approved here.

## 5. Original-objective contribution and explicit non-recommendations

| Original objective | Accepted contribution |
| --- | --- |
| 1. Existence and connectivity | No new capability beyond the accepted declarations and exact governing relation. |
| 2. Current state | Partial: distinguish evidence usable at C under P from receipt-age or coverage failure; not present physical state. |
| 3. Why the system behaves this way | No causal or diagnostic contribution; only an explanation of workflow withholding. |
| 4. Next best measurement or test | Supports refreshing one nominated evidence path as an application response; does not select the next best measurement or test, rank alternatives, or optimize information gain, cost, risk, accessibility or diagnostic value. |
| 5. Change impact | No traversal or propagation added; existing exact-dependency/revision checks remain unchanged. |
| 6. Smallest valid desired-state changes | No planning, goals, action effects, optimization or control. |
| 7. Observed/calculated/inferred/assumed/unknown | Partial: preserve observations and calculated age/CN results separately from explicit policy and unknown/refused/unavailable outcomes. |

This is an application-policy decision supported by existing capabilities,
not implementation progress toward general recommendation, causal reasoning,
impact analysis, physical occurrence history, desired-state planning or safety.
FA-001 remains cancelled under its accepted rule: reconsideration requires a
new owner-approved proposal demonstrating a concrete integrity attack that
existing public-result validation cannot prevent. Convenience or aggregation
preference is insufficient; CS-001 has demonstrated no such attack.

## 6. Status, preservation and bounded authorization

No successor milestone is approved. ADRs remain contiguous and unique through
the latest accepted ADR-0022; ADR-0023 remains absent and unallocated. The
accepted objective-gap reconciliation, followed by this closed application
investigation, defines status without selecting the next unused roadmap noun.

Only the corrected proposal, unchanged audit, correction/owner reports and
minimum root/status documentation enter the bounded closeout commit:
`docs: close CS-001 as application policy`. Baseline ledger membership remains
36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
model-kernel exports remain exactly 236; FCD/FCW and FMA/FMW remain `0/0`.
Protected inventories, accepted FC/integrated witness digests and the frozen
audit are checked as recorded in the correction report and terminal receipt.

A complete repository or clean-checkout matrix is unnecessary and was not run
for this documentation-only closeout. Focused documentation/status,
structure/link/ADR, preservation and whitespace assertions are the relevant
verification. Historical 4,074-pass coverage is not represented as a new run.
No implementation, production/test change beyond documentation assertions,
authoritative fixture or ledger mutation, branch, ADR allocation, push, merge
or history rewrite occurs. No additional challenger audit is run.

END OF CS-001 APPLICATION POLICY OWNER DECISION
