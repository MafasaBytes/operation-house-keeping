# CV-001 Proposal Correction Report

Documentation-only closeout — 2026-09-10.

## 1. Frozen inputs and verified baseline

All requested checkpoints matched before editing. Branch `main` and
`HEAD = origin/main = 1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675`;
latest subject: `docs: close DI-001 as application composition`.
Initially there were no tracked changes; the frozen proposal and audit were
the only two untracked files. Both are included in this closeout commit.

| Input | SHA-256 |
| --- | --- |
| [Proposal before correction](../proposals/2026-09-10-cv001-codex-lead-proposal.md), 661 lines / 69,441 bytes | `7d1714076204bdff1169c6215370ae7207ed80beeb6b0aeb1ff8ba8993cbc6a2` |
| Corrected proposal, same path | `1646fc662ae2ae0bc15e2b50173efad88e73d6728036bbf54ed56429393fd99e` |
| [Unchanged challenger audit](2026-09-10-cv001-codex-lead-proposal-challenger-audit.md) | `7cafecf638ee3024282b58369bebaae78cb293262aee0ceceff54bcf74f13580` |

The old proposal digest identifies the frozen reviewed bytes, not the corrected
file now at that path. The original bytes were captured in memory before editing
for exact preservation comparisons; no additional repository artifact was created.
The audit remains byte-for-byte unchanged and still addresses that old digest.

## 2. RC-1 mapping and exact correction

The owner accepts `approve_with_corrections`: zero blocking findings, one required
correction, and three non-blocking observations. The
[owner decision](2026-09-10-cv001-deferral-owner-decision.md) closes the investigation.

| Location | Previous problem | Correction |
| --- | --- | --- |
| Proposal title/status and section 1 | Unconditional CV-001 cancellation blurred backend sufficiency and absent application delivery. | Backend additions cancelled; application delivery deferred pending the eleven concrete consumer requirements. Proposal retained as guidance, not implementation approval. |
| Sections 1 and 3 | Public composability could be credited as an exposed complete answer. | Existing public APIs suffice for correct in-process composition; no stable application entry point exposes the complete answer. CS policy remains guidance, not an implemented workflow evaluator. |
| Section 4 | Documentation alternative still referenced the old unconditional outcome choice. | Retained guidance is for deferred application design; no new documentation milestone or delivered workflow is implied. |
| Section 9 introduction | Backend spill prevention could imply application guards were already solved. | Authentication/authorization, policy authority, retention, error translation, confidentiality, resource ownership, deployment, and scope completeness remain application prerequisites. No generic wrapper may hide them. |
| Section 13 | Objectives 2/7 and the user-visible sentence could be interpreted as delivered product capability. | Architecture/test support only. FC proves the lower join; the original satisfied-A twin was CN-only; separately acquired W40 closes full-path test coverage, not a new architectural or user-facing capability. Objective 4 still lacks next-best-measurement/test selection. |
| Section 14 | Old owner/audit gate and authoring-only stopping language were stale for closeout. | Record accepted deferral, all consumer gates and unauthorized scope; distinguish historical authoring checks from current documentation closeout. |

No lower API, policy gate, request/result semantics, canonicalization algorithm,
or implementation recommendation was added. The backend must not be credited
with a user-facing workflow that has not been built.

## 3. Preserved design and spill material

All 26 spill-register rows SP01–SP26 are byte-identical to the frozen proposal.
Sections 2, 5–8 and 10–12 are unchanged, preserving baseline evidence, all
fourteen public join steps, policy details, refusal axes, integrity analysis,
fifteen worked cases, twenty-four attack/twin entries, and the zero-append decision.
Only disposition, capability, application-prerequisite and closeout wording changed.

The accepted CS distinctions remain: receipt-side age only;
`evidence_not_usable_under_policy` / `receipt_age_exceeded`; exact EA
`complete_within_declared_horizon`; honest multiple matches remain
`criterion_evaluation_unavailable`, not input incoherence. Receipt-age denial
does not establish physical-measurement staleness or require a new physical
measurement. Public composition is not truth, physical occurrence, health or safety.

NBO-1's CN-only/W40 distinction, NBO-2's application responsibility for complete
joins and refusal preservation, and NBO-3's security/retention/presentation
prerequisites are retained as limitations. No further challenger was run.

## 4. Changed-document allowlist and corrected frontier

Exactly these seven documents form the closeout:

1. [Corrected proposal](../proposals/2026-09-10-cv001-codex-lead-proposal.md).
2. [Frozen audit](2026-09-10-cv001-codex-lead-proposal-challenger-audit.md), added unchanged.
3. This correction report.
4. [Owner decision](2026-09-10-cv001-deferral-owner-decision.md).
5. [Root README](../../../README.md), current frontier only.
6. [Repository status guidance](../../../CLAUDE.md), current frontier only.
7. [Model-kernel README](../../../backend/model_kernel/README.md), current frontier only.

CS-001 remains application policy; DI-001 remains bounded application composition.
CV-001 backend additions are cancelled; CV-001 application delivery is deferred
pending concrete application requirements. No successor milestone is approved.
Causal diagnosis, next-test ranking, impact prediction, and planning remain
unauthorized. Further backend abstraction requires a demonstrated integrity gap;
further application work requires all eleven consumer requirements in the owner
decision. No earlier accepted report or ADR was rewritten.

## 5. Preservation evidence

| Protected checkpoint | Preserved value |
| --- | --- |
| Authoritative model and exact replay | 36 records; `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FMA/FMW; FCD/FCW | `0/0`; `0/0` |
| Model-kernel exports | 236 unique ordered names; `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |
| FC witness | 14,677 bytes; `a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca` |
| Integrated witness | 174,490 bytes; `1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e` |
| ADRs | Unique contiguous accepted ADR-0001 through ADR-0022; ADR-0023 absent, unallocated and unreserved |
| Historical full verification | 4,074 passes; not rerun or replaced by this closeout |

The eight protected document hashes and six tree inventory hashes in unchanged
proposal section 2 were freshly recomputed. Inventories cover model, both binding
trees, interpretations, showcases, and ignored raw-store artifacts; the ignored
local settings digest was also preserved. Inventory encoding remains sorted
repository-relative pathname to file SHA-256, compact sorted-key JSON plus newline.
Export encoding is the ordered compact JSON public-name list without newline.

Both accepted witnesses were reproduced using the existing disposable checker.
The protected six-result integrated payload still contains a CN-only satisfied-A
twin: its digest is not replaced by W40. W40's separate full-path evidence remains
the previously executed proposal/audit result, not a newly run closeout experiment.

## 6. Verification and commit boundary

Checks use read-only inline documentation/preservation assertions and existing
witness tooling; no production code, test file, authoritative append or generated
artifact is introduced. Relevant reproduction commands include:

```text
sha256sum docs/superpowers/proposals/2026-09-10-cv001-codex-lead-proposal.md docs/superpowers/reports/2026-09-10-cv001-codex-lead-proposal-challenger-audit.md
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python /tmp/post_fc001_witness_checks.py
git diff --check
git diff --cached --check
git diff --check 7693f1acf763f652947dff28b5dbb8a8dfee2505
git diff --cached --check 7693f1acf763f652947dff28b5dbb8a8dfee2505
git status --short
```

The existing temporary checker is a disposable reproducibility aid, not a new
committed dependency; its producer digest is pinned in unchanged proposal
section 3. Inline assertions additionally compare exact spill rows and unchanged
sections against the captured old proposal, check document headings/markers,
resolve changed-document links, verify current status and the seven-file allowlist,
load/replay the model, check ADRs, and recompute all protected hashes.

Fresh closeout results: frozen audit and corrected proposal hashes matched;
all 26 spill rows and the protected proposal sections were unchanged; document
structure, ending markers and status assertions passed; all 73 local links
resolved; model/replay, export, ADR, protected inventories and both witness
checks passed. The exact seven-file working/staged allowlist and working-tree,
staged, and full post-FC-range whitespace checks passed. These checks are rerun
on the final staged payload and after the authorized commit.

A full repository or clean-checkout matrix is unnecessary and was not run for
this documentation-only closeout. The proposal's 71-test authoring run and the
audit's separate 71-test run remain historical evidence, not fresh closeout tests.

The owner authorizes one commit: `docs: defer CV-001 pending application requirements`.
No implementation, successor proposal, ADR allocation, fixture/ledger mutation,
push, merge or history rewrite is authorized. Repository receiving-code-review
guided RC-1 verification; verification-before-completion guided fresh preservation
and commit checks. Neither skill expanded the owner's documentation-only scope.

END OF CV-001 PROPOSAL CORRECTION REPORT
