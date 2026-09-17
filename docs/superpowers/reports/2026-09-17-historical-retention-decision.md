# Historical-retention decision pass

2026-09-17. This is an approval-ready decision record only. No historical file
was added, removed, renamed, staged or published.

Verified main is `d229c540f5aa1ec318df9d03fd4a93ff906a2d67`; the governing
[reconciliation](2026-09-17-post-admissibility-reconciliation.md) has SHA-256
`5f0ce7756b755f62ae1f745055a14062ad1bb1dcbe04dac754d790ce3156cfb9`.
The existing [inventory](2026-09-17-post-admissibility-inventory.json) remains
the source for all 242 paths, hashes, references and recovery locators. No
isolated application checks were repeated.

## Decision

Required exact additions to the published repository: **none**. The accepted
authority/reproduction chain is already recoverable from committed material:
the 105-file authority index, embedded design/schema/policy/build inputs and the
467-file governed evidence archive. The unresolved files below are not required
to execute, verify or historically replay the accepted capability.

Optional historical additions: **none recommended at this gate**. All 16 files
are present locally, but exact committed recovery is not located. They remain
preserved untracked. Adding any would require a separate owner decision after
disclosure review; this pass does not infer that superseded history must be
published.

The phrase “recovery not located” is intentional: these bytes exist locally and
are not established as lost. The consequence of leaving them outside publication
is limited to unresolved historical navigation links and loss of self-contained
access to those discarded-stage narratives; it does not impair accepted runtime,
authority, reproduction or release evidence.

## The 16 linked targets

Every row has exact local bytes, no exact committed recovery locator, and the
listed referencing documents. “Binding” means required for the accepted chain;
none is binding. “History” means explanatory or superseded decision evidence.

| Path | SHA-256 | Bytes | Role / references | Local and committed state; consequence |
|---|---|---:|---|---|
| `docs/superpowers/proposals/2026-09-12-conditional-prediction-codex-lead-investigation.md` | `a43f843d93729881e9254d0ddb060444e06f95e1ad29a6aef1c288234e24e97c` | 49,518 | History; referenced by conditional-prediction comparative design | Local only; leaving out leaves an obsolete experiment link unresolved. |
| `docs/superpowers/proposals/2026-09-15-bounded-decision-workflow-delivery-proposal.md` | `f48065f53f35a302d9cd1c4f3d66872bf367f0625da44bc499b3be97381b808f` | 32,252 | Superseded proposal/history; referenced by delivery review and corrected design | Local only; accepted S1–S7 records remain recoverable. |
| `docs/superpowers/proposals/2026-09-15-one-step-intervention-projection-proof-design.md` | `1857703f8c76fbbcdb99b5dca2b62a7e49237ca64ee8807aff496effcdd78599` | 33,415 | Historical proof proposal; referenced by owner acceptance/corrected design | Local only; proof history is not needed for maintained replay. |
| `docs/superpowers/proposals/2026-09-16-maintained-admissibility-enforcement-lead-proposal.md` | `5a5b26fca9043bb14df44e9f963e880446813a5fcf0d7a9017a41c9f7c43e038` | 30,850 | Superseded lead proposal; referenced by corrected admissibility design | Local only; accepted corrected design and final acceptance supersede it. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-preexecution-rehearsal-report.md` | `8e34bbc84ae404c0789e62801abe025c6a6820f33747b3c5a38dfbc56cf193f1` | 17,708 | Historical rehearsal; referenced by completion/challenger/resource reports | Local only; no accepted authority or input depends on it. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-redesigned-preexecution-rehearsal-report.md` | `7cec799a730584d315242db964c669629b1914826dcba36f88746267da02ad45` | 28,764 | Historical corrected rehearsal; referenced by discrepancy report | Local only; omits one obsolete rehearsal link. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-request-carriage-redesign-investigation-report.md` | `393fcc985173f55794bda9808e01b9691c9c4b45c5a37fd02584c57309e76403` | 251,720 | Historical experiment investigation; referenced by redesign proposal/correction/audit | Local only; largest unresolved historical file, not runtime input. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-resource-calibration-continuation-report.md` | `2f1b0b24f6a6929c80b0566bef7232ebed1fc2fa786f2990264ba9478273cfc0` | 152,923 | Historical resource calibration; referenced by redesign proposal/correction/audit | Local only; no current resource ceiling derives from it. |
| `docs/superpowers/reports/2026-09-12-conditional-prediction-codex-lead-investigation-challenger-audit.md` | `5b9517f17ee03c748a455d4c93b1d251ef21b0fa60756e6ea90d0c96f4741399` | 12,270 | Historical adversarial review; referenced by comparative design | Local only; no accepted implementation dependency. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-independent-review.md` | `41c6ece7848bb9ee59a2cc62eff21c234c1b2d2e9c472ab57b213a6d1c0390b3` | 29,260 | Historical independent review; referenced by owner acceptance/corrected design | Local only; accepted implementation evidence is elsewhere. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-preexecution-report.md` | `0df39edb1033ac0a3389864a69a582ca49748c326cf9cff2b6e5bac4dac0d56b` | 15,907 | Historical preparation; referenced by final execution report | Local only; no reproduction input. |
| `docs/superpowers/reports/2026-09-15-post-experiment-objective-and-architecture-consolidation.md` | `08bdd577755c5e1e8b04a2780c137ae31de8a742dcdc8020f2c2097a534f9574` | 30,224 | Historical objective/architecture analysis; referenced by delivery review/corrected design | Local only; current reconciliation supersedes status claims. |
| `docs/superpowers/reports/2026-09-15-source-agnostic-backend-gap-assessment.md` | `121f832852c5e2162882a2bdc1ecd3e0249f1e3d6afd8cd7da23b3f5ab7e63a9` | 29,772 | Historical backend-gap analysis; referenced by one-step acceptance/corrected design | Local only; no backend contract or authority depends on it. |
| `docs/superpowers/reports/2026-09-16-maintained-admissibility-enforcement-focused-rereview.md` | `9631c4d333272a2379128e0cc438764490de0d32931d0b3528a3d6e9f681457b` | 15,445 | Historical focused review; referenced by accepted corrected design | Local only; final confirmation and acceptance remain recoverable. |
| `docs/superpowers/reports/2026-09-16-maintained-admissibility-enforcement-independent-adversarial-review.md` | `7c58332df841d526dc73bbaf430ce11acae61985d585dfcd339c358128b57dad` | 23,092 | Historical independent review; referenced by accepted corrected design | Local only; no executable authority dependency. |
| `docs/superpowers/specs/2026-09-16-maintained-admissibility-enforcement-corrected-final-design.md` | `e6e9938aac5387c6719c678a2392c48b9539e4f3d7840ea6ab1d5cfaacfbd472` | 35,511 | Superseded design; referenced by shared-reference-corrected design | Local only; current approved design is tracked and bound by digest. |

The 16 files total **788,631 bytes**. Their local contents were hash-checked
against the inventory. The accepted chain has no dependency on any one of them.

## Navigation, disclosure and owner gates

Do not silently rewrite frozen historical links. The smallest navigation remedy
is an explicit publication note (or future index entry) saying that these 16
historical targets remain locally preserved but are not committed and are not
required for accepted authority/reproduction. Such a correction itself requires
separate authorization; this report does not alter frozen links.

The inventory’s screening found no private-key, GitHub-token or AWS-key pattern
in the proposed files. They do contain historical experiment details, synthetic
assumptions, review commentary and environment/path metadata. That is a disclosure
category requiring owner publication review; it is not a claim of exhaustive
privacy certification. Prior metadata approval does not cover these 16 files.

No exact additions are therefore proposed. Remaining publication blockers are:
owner choice on whether to retain any optional historical file, owner disclosure
approval, and a fresh authenticated remote-tip comparison. Remote authentication
remains owner-operated. IN-001 and CI-001 remain open and unselected.

END OF HISTORICAL-RETENTION DECISION
