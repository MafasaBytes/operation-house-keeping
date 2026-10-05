# Focused independent confirmation v2: checked derivation and applicability

Date: 2026-10-04, Europe/Amsterdam.

## Provenance, frozen inputs and method

Reviewer: Codex sub-agent `/root/checked_corrections_focused_confirmation`, with no authorship or editing role in either corrected candidate. The exact runtime model identifier was not exposed to this agent; no Claude provenance is claimed. This report continues the authorized focused independent design confirmation after the author made a separate second correction. It is not an implementation review, experiment, executable contract freeze or owner approval.

Independently verified repository HEAD: `2f0afbd368105b99f0b8548ffece107918386e3d`.

| Frozen document | Independently verified SHA-256 |
|---|---|
| [Complete corrected design v2](../proposals/2026-10-04-checked-derivation-and-applicability-corrected-design-v2.md) | `68da70f2cc64d837e45e8534da0eba7d95d94686ab40806099c5f06a0e4a02da` |
| [Preserved first corrected candidate](../proposals/2026-10-04-checked-derivation-and-applicability-corrected-design.md) | `d1609c607ecfd342be1a752c33ce8766920e83dc1b63e945639cbccb3e55e936` |
| [Frozen predecessor](../proposals/2026-10-01-checked-derivation-and-applicability-successor-design.md) | `27e2a5a2e527cc6763fa4479ed6b83b3736d9faedfce48e9db3096dbf20fdd23` |
| [Original independent adversarial review](2026-10-04-checked-derivation-and-applicability-independent-adversarial-review.md) | `ed14313f66746b57856ef7dcef02015ccd81e0ca137f951bfd483d4ea08505a5` |
| [Preserved initial focused confirmation](2026-10-04-checked-derivation-and-applicability-focused-confirmation.md) | `64dcab4c3ecca32a242ec320fe75996d744d5a6016eb3aa706240af8da1fca53` |

Read the entire first corrected candidate, frozen predecessor and original independent review during the initial confirmation, then the entire complete v2 after the author supplied it. Independently verified that the repository copy of the initial focused report matches its unchanged staged bytes. Below, **V2** denotes the complete v2 at the digest above and its one-based lines; **First** denotes the preserved first candidate. The original predecessor/review hashes and checkpoint were checked again after the initial source inspection, and all listed hashes/checkpoint were checked at final handoff.

No repository AGENTS.md was found in a search including hidden files; none was present at the checked repository root, immediate drive ancestor or staging-workspace root. Relevant read-only source inspection covered ideal-branch construction and minimax ranking, interval intersections and all-intersecting-branches reassessment, hard-interval grammar/containment, and legacy verify/replay. No new checked-profile implementation was observed in the inspected application source. This review neither imports nor executes that source.

Git inspection used per-command `safe.directory=D:/operation-house-keeping` and `--no-optional-locks`, without configuration edits. The reviewer did not alter pre-existing working-tree/index changes, including the modified test runner and untracked materials. There was no delegation, test execution, application call, repository import, experiment, clone, dependency change, runtime/ledger write, cleanup, commit, Git configuration change, remote operation or edit of a pre-existing file. The reviewer created only the initial staged report and, under the subsequent explicit instruction, this new staged v2 report. The parent retained the initial report in the repository; the reviewer did not copy either report into the protected repository. No full historical runtime preservation inventory was repeated.

At final preservation inspection, the parent reported a concurrent unexplained tracked `.gitignore` change. The reviewer independently confirmed that its read-only diff adds `/_to_delete/` and a newline after `/venv/`; the earlier tracked-diff inspection had listed only the modified test runner. The reviewer did not make, restore or edit this change. Accordingly, no claim that all repository content remained unchanged is made. The exact frozen-document digests and HEAD still match, so this unrelated concurrent change does not alter the reviewed bytes or semantic dispositions; its cause remains unestablished here.

## Final verdict and severity counts

F1 is resolved. F2 is resolved by v2, including the consequential same-item relevance ambiguity independently found and reopened in the initial focused confirmation. No additional consequential defect was found in the corrections.

Current open severity counts: P0 0; P1 0; P2 0; P3 0. Historical initial-confirmation count: P2 1, now closed by the separately preserved v2 correction. Observed new-implementation defects: 0. These are design dispositions, not passing test results or proof of a deployed implementation.

The complete v2 is endorsed for owner consideration of this semantic correction only. This endorsement does not approve deployment policy, freeze delivery schemas/resource limits, authorize implementation or replace the separately gated preparation work listed below.

## F1 — resolved: ideal-measurand branches, not operational elimination

**Locations.** V2:53–59 fixes `ideal_measurand_decoder_branches`, defines the maximum ideal-branch survivor cardinality, requires `post_measurement_elimination_guaranteed = false`, captures but does not rank the observation interpretation plan, and prohibits operational/probabilistic labels. V2:61–71 defines conservative reassessment and changed-plan inheritance. V2:134–139 distinguishes mandatory metadata verification from downstream replay.

The conditional ideal sets remain H1/T1 `{60.1}` and H2/T1 `[45.1,55.1]`. With low ≤56, gap `(56,59]`, high >59, T1 has survivor sets `{H2}`, `{}`, `{H1}` and score 1; T2's common heater-off branch has score 2. This is the exact named score domain. The [retained pure ranker](../../../applications/bounded_decision_workflow/measurement_ranking.py), lines 30–33 and 68–75, preserves empty/repeated branches and takes this maximum. It may be reused with new application-owned checked cells without inheriting legacy supplied-support qualification as the new trust decision.

**Analytical, unexecuted twins.** At half-width 2.5, H1's measurand 60.1 with error −2.5 and H2's measurand 55.1 with error +2.5 both produce scalar 57.6. Interpreting it once gives `[55.1,60.1]`, reaching low `[55.1,56]`, gap `(56,59]`, and high `(59,60.1]`. Both hypotheses have mixed permits/exclusions and remain unresolved. The ideal score is still 1; v2 expressly promises neither one operational survivor nor a settled compatibility result. Admission of that half-width by a future new parser remains conditional on the exact numeric contract, not a reported passing test.

At half-width 0.5, reading 60.0 gives `[59.5,60.5]`, only high: H1 is conditionally compatible and H2 conditionally incompatible. Measurand 55.1 plus legal error +0.5 gives reading 55.6 and `[55.1,56.1]`, low plus gap: H2 is unresolved, while H1 is excluded in both branches. One non-excluded account is not necessarily a settled compatible account. Parameter uncertainty enters the ideal predictions once; observation error is applied once to the observation. This preserves the [retained reassessment rule](../../../applications/bounded_decision_workflow/reassessment_compute.py), lines 122–128 and 145–171, without claiming that legacy derivation is checked.

A missing required scalar interpretation plan withholds selection rather than supplying a default. Unknown/confidence-only uncertainty cannot become an invented hard bound. Changed rules, bounds, units or editions require an explicit immutable successor, disclosed plan change and newly scoped authority under V2:63. The former selection is historical, not execution of an unchanged plan. New observation/acquisition evidence still must pass exact current applicability and authority gates; no result-time review upgrades selection-time applicability or automatically reranks/adopts anything.

Mandatory misleading score-domain/uncertainty-plan metadata refuses verify. A correctly rehashed changed numerical downstream score may survive verify only because the operation explicitly reports `downstream_result_not_replayed`; replay must independently recompute and detect it. That weaker downstream check cannot excuse operational or guaranteed score labels. F1 remains closed in v2.

## F2 history — initial P2 reopening was warranted

**Initial locations.** First:76–78 retained competing reviews, marked unresolved relevance/relation pending, and allowed a completed irrelevant review to exclude an item from all contributions. First:82–93 supplied exact condition-level axes/precedence but no item-level order for competing relevance judgments.

The initial same-graph witness had item A with applicable completed calibration support, plus item B with both a completed irrelevant review and a completed unresolved-relevance review. Both B reviews had valid exact bindings; no conclusively disjoint typed scope excluded B. The policy forbade unresolved calibration and all other gates passed.

Exclusion-first could yield `support_only / complete / supported` and use; pending-first could yield `support_only / pending / unresolved` and block. Retaining both reviews and rejecting a newest-timestamp winner did not choose the completeness input. This was the one historical P2 finding in the preserved initial focused report, not an observed software defect. The author accepted it and created a new complete v2, leaving the inspected first candidate and initial report unchanged. The reviewer did not edit either candidate.

## F2 — resolved in v2: exact item order and condition precedence

**Locations.** V2:79–86 gives the explicit item-level order, before V2:90–101 computes condition-level relation/completeness/state. V2:103–107 protects opposition/conflict and separates declaration/authority gates; V2:120–125 supplies same-item twins and changed-graph behavior.

The item order is now unique:

1. A conclusive profile-defined typed scope/context/validity exclusion takes priority, retains every review and contributes neither relation nor pending status for this assessment. Raw publication/acquisition/attachment time alone cannot serve as that validity basis.
2. For remaining items, applicable completed relevant reviews contribute support/opposition. Missing/incomplete required reviews or unresolved relation/relevance make the item pending. Unknown or partial scope overlap that does not establish exclusion remains pending.
3. Irrelevant plus still-potentially-applicable unresolved relevance is pending. Relevant plus irrelevant is also pending due to disputed relevance, while completed relevant support/opposition stays in the relation axis. Relevance disagreement does not invent empirical opposition; known support and opposition still conflict independently of completeness.
4. Human-reviewed exclusion is allowed only after these checks, when all potentially applicable supplied relevance judgments are completed and agree on irrelevance/out-of-scope, with no relevant/unresolved judgment or missing required review. One unopposed completed irrelevant review suffices only if the captured profile requires no other review.

Thus the initial witness now has exactly `support_only / pending / unresolved`: it blocks if unresolved calibration is forbidden, and is visibly conditional only if the owner explicitly allowlists that condition. No exclusion-first interpretation remains permitted. A conclusive typed exclusion is different from a disputed human relevance judgment; the former's exact predicate/catalogue remains contract preparation, but its priority and the unknown/overlap fallback are not left to implementer choice.

**Additional analytical aggregation challenges, not passing tests:**

| Captured graph / challenge | Unique axes and state | Policy consequence |
|---|---|---|
| Completed support plus unreviewed potentially relevant attachment | `support_only / pending / unresolved` | Explicit unresolved-condition policy, never a pending badge beside `supported`. |
| Completed opposition plus pending | `opposition_only / pending / contradicted` | Always block. |
| Completed support and opposition plus pending | `support_and_opposition / pending / conflicting` | Always block. |
| One relevant support review plus an irrelevant review of that same item | `support_only / pending / unresolved` | Disputed relevance stays pending; support is retained. |
| One relevant opposition review plus an irrelevant review of that same item | `opposition_only / pending / contradicted` | Opposition cannot be erased. |
| Same-item support and opposition plus irrelevant or unresolved review | `support_and_opposition / pending / conflicting` | Both relations remain; pending cannot weaken conflict. |
| Sole completed unresolved relation/relevance on a potentially applicable item | `none / pending / unresolved` | Same explicit unresolved policy; no positive support is invented. |
| Support A; B has only unopposed completed irrelevant judgments and no missing required review | `support_only / complete / supported` | May proceed subject to independent gates; retain B and exclusion basis. |
| Sole expired support with conclusive typed non-overlap | `none / complete / unresolved` | Historical support cannot settle this assessment. |
| Support A; B conclusively outside typed scope, unresolved review retained historically | `support_only / complete / supported` | Mechanical exclusion is explicit; not a hidden relevance override. |

An applicable unresolved judgment cannot be suppressed by an irrelevant judgment, reviewer preference or timestamp. Conversely, a review whose exact scope/time does not apply is not an applicable opposing review for this assessment. That distinction does not authorize hiding in-scope opposition: exact conclusive exclusion bases are retained, unresolved overlap remains pending, and changes create a different graph/request subject to new scope and authority.

Changed attachments, reviews, declarations, policy or assessment context require successor applicability/request identity and fresh recomputation under V2:125. Newly completed opposition can block a successor without retroactively changing the old captured assessment. Removing an item is a changed graph, not reuse of the same assessment. Neither old supported labels nor request-specific permission carry over silently. Missing required bytes/malformed identities structurally refuse before aggregation rather than becoming policy-tolerable pending evidence.

Conflicting applicable declarations and false/unknown/missing/out-of-scope required declarations independently block. An unresolved empirical-support allowlist cannot repair them, and cannot permit contradicted/conflicting states. Any governing selection block withholds ranking over the whole nominated set; reassessment retains affected accounts as not assessed instead of pruning or resurrecting them. F2, including the initial residual finding, is now closed.

## Consequences, preservation and remaining gates

The semantic changes are bounded: the score is explicitly ideal-measurand discrimination, while raw pending attachments and same-item relevance disputes affect governing use policy conservatively. A3/A4 post-result attachments do not become reviewed opposition automatically; they can make completeness pending, and completed applicable opposition subsequently blocks. Historical conditional results and exposure labels remain preserved. No uncertainty-aware branch optimizer, extra causal kind, backend extension, empirical validation claim or upgrade of legacy NM/NR verify/replay follows.

The reviewer checked the frozen documents and relevant source, not physical evidence or the reported 1,756-file runtime inventory. The semantic-candidate recovery disclosure, absent distinct pre-fix builder for failed attempt 006, producer/test-builder dependence, unresolved mapping and clock relationship remain as disclosed in the frozen sources. Both corrected candidates, the predecessor, original independent review and initial focused report remain distinct historical artifacts at their listed digests.

All six V2:177–182 prerequisites remain expressly unfinished before executable contract freeze:

1. Exact H1/H2 meanings and parameter/kind constraints, positive-offset/low domains, reference-bias intervals, baseline eligibility, endpoints and units.
2. Exact decoder partitions and literal procedure/interpretation editions, held-suspect T2 threshold/equality behavior, scalar containment and numeric admission bounds. Half-width 2.5 is not deemed admitted by this review.
3. Finite typed condition catalogue, proposition/subject/phase identity and contradictory declaration detection. The same-item and condition aggregation precedence is now normative; concrete catalogue/schema preparation is not a reopened aggregation policy choice.
4. Externally expected-pin carriage and precise evaluate/verify/replay interfaces; owner-selected reviewers/issuers and explicit unresolved-condition allowlist. Local pins remain declarations, not authentication.
5. Exact source/module/build capture and preserved historical executable/replay environments; unchanged old schema text alone is insufficient in a changed build.
6. Finite byte/object/review/history/rational/work/trace/retention limits, delivery schemas and a bounded separately authorized preparation/verification plan, charged before the work they bound. Old-profile ceilings are not new capacity evidence.

These are explicit preparation obligations, not additional findings, passing capacity proofs or demonstrated admission failures. No new implementation, tests, fixture execution, resource qualification, independent physical validation or completed end-to-end producer was established. Owner consideration and separately scoped contract/fixture/resource preparation remain the next gates. Reviewer endorsement is not owner approval and does not authorize implementation or a new qualification campaign.

END OF CHECKED-DERIVATION AND APPLICABILITY FOCUSED CONFIRMATION V2
