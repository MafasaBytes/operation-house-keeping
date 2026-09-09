# FA-001 Feasibility Owner Decision

## 1. Accepted investigation and frozen artifacts

On 2026-09-09 the owner accepted the [FA feasibility proposal](../proposals/2026-09-09-fa001-codex-lead-proposal.md) and [independent challenger audit](2026-09-09-fa001-codex-lead-proposal-challenger-audit.md). Approval is for correctly rejecting baseline-only FA implementation: the accepted lower layers do not declare that a variable criterion governs a flow-measurement meaning. Approval does not establish FA runtime viability.

The artifacts are committed byte-identically, including their original line endings:

| Artifact | SHA-256 |
| --- | --- |
| FA proposal | `c818e4e342bd9450c5e1d19513bae336097f7601648ef1a8f73232e490d37c17` |
| Challenger audit | `65114fcc03cbe07a90cfceb349bea1ea7dba2c3f21f67f835cb100c76b062980` |

Starting branch is `main`; starting HEAD and locally inspected `origin/main` are `d888ba6fbfb313cf2f85ce5cb07168fb528ec059`. No fetch is needed. FM-001 remains complete and owner accepted at exact tested implementation `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`.

## 2. Deferral and authorized product question

FA-001 is **deferred, not completed or implemented**. All FA runtime, API, package, identity, record, test, fixture, demonstration, and ADR work is deferred. ADR-0022 is absent, remains unallocated, and is not assigned to FA.

The owner approves this narrowly bounded future question as valuable for a **commissioning/operations verification workflow**:

> At this explicit receipt cutoff, does one nominated measured-actual sample satisfy the authority-declared operating criterion governing one exact logical-flow participant and context, and what evidence and declarations justify the result?

An answer does not establish physical flow, activity, occurrence, continuity, conservation, correctness, or safety. It does not authorize operation or certify commissioning completion.

## 3. FC design authorization and scope

The missing G1 governing relation is authorized for **design-only investigation**, provisionally named **FC-001 — Explicit Flow Operating Criterion Declaration**. The relation is not already designed or approved for implementation.

The first scope uses one governing criterion and one nominated candidate. Source agreement, freshness policy, uncertainty, continuity, aggregation, and physical-flow occurrence are outside that scope. Retain the accepted public carried-result proof boundary. A labelled disposable worked example is sufficient for software verification; no authoritative demonstration or ledger append is required.

The FC design must explicitly compare and decide assertion-record versus effective-body pinning, including corroborating roots and lifecycle effects. No choice is implied by this authorization. Existing anchor and FM identities remain unchanged. No ADR number is allocated.

## 4. Reconsideration and cancellation gate

After FC is separately accepted and implemented, FA viability must be reassessed. Cancel FA if an FC query plus the existing CN result already answers the approved question without a new evaluator. A later FA composition requires a separately justified conclusion or integrity boundary and explicit owner authorization; it does not follow automatically from FC.

The audit's missing-consumer concern is resolved by the named commissioning/operations workflow. Its remaining pinning/design concerns belong to FC investigation. Non-blocking observations do not authorize editing the frozen artifacts.

## 5. Administrative preservation and scope

The authoritative model stays at 36 records, revision `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`: FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, FMA/FMW `0/0`. The exact 225-name kernel surface remains unchanged. Zero FMA precludes an authoritative FC declaration with valid existing FM support.

This closeout changes only necessary frontier wording in root README and CLAUDE, adds this decision, and commits the two frozen artifacts in one documentation-only commit. FC's subsequent proposal is not part of that commit. Runtime code, tests, fixtures, identities, records, canonical bytes, ledger membership and artifact logic remain untouched. `.claude/settings.local.json` remains unchanged and uncommitted; its SHA-256 is `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

Verification consists of frozen-byte and staged-blob digest checks, status/frontier review, local links, ending marker, ADR absence, documentation-only diff and whitespace checks. No runtime suite rerun is claimed or needed for this administrative change. No push, merge, rebase, reset, cherry-pick, amend, or history rewrite is authorized.

The frozen audit contains 498 CRLF-terminated lines. Repository Markdown attributes normally normalize these to LF, so its exact blob is staged without clean filters to preserve the accepted digest. Default staged `git diff --check` reports those CR bytes as trailing whitespace; this is a disclosed frozen-artifact exception, not permission to normalize it. The CRLF-aware check (`git -c core.whitespace=cr-at-eol diff --cached --check`) and ordinary checks on newly authored documentation must pass. No attributes or Git configuration are changed.

END OF FA-001 FEASIBILITY OWNER DECISION
