# BRC-EXP-001 final owner acceptance

## 1. Owner decision and administrative boundary

On 2026-09-12 the owner accepts Mode B execution and closes BRC-EXP-001 as a
bounded experiment. Slice A remains owner accepted. Starting branch is
`brc-exp001`; administrative starting HEAD is
`f89bf9a37faa4b23106a149aa8bd827931324c1b`. The closeout commit is identified by
Git metadata and subject `docs: accept and close BRC-EXP-001`.

This is documentation acceptance, not a new experiment run, production delivery
or successor decision. No production capability was added. The disposable drivers
and tests were deleted; their source is not promoted or committed. ADR-0023 remains
absent, unallocated and unreserved. No successor proposal, package, record type,
milestone, architecture or ADR is authorized by this acceptance.

## 2. Exact accepted commitments

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Slice A final execution report](2026-09-12-brc-exp001-slice-a-final-execution-report.md) | 5,715,759 | `5a101e9815d4561d1b2fad6a678eb93c3250d395385efe044d270c85840ea5b2` |
| [Slice A owner acceptance](2026-09-12-brc-exp001-slice-a-owner-acceptance.md) | 6,515 | `dad65d192fc92b3f50554c4fcb8a43afd3216f46ac3167ebb3cb9875fb82bdac` |
| [Mode B final execution report](2026-09-12-brc-exp001-mode-b-final-execution-report.md) | 4,965,514 | `39afa882cd41bd01b1c39047ff651732770c326b62c03a56c8ab9925d4a495ca` |
| [Mode B output-resource amendment witness](2026-09-12-brc-exp001-mode-b-output-resource-amendment-report.md) | 1,073,123 | `b37b999f98ff64e2586d908516dcdd06e11087a4fe2a1b8ba10880c5611cecec` |

All report bytes and markers are verified and preserved exactly. Pending owner
gates in frozen execution reports and historical failed reports describe their
own checkpoints; this separate acceptance supersedes their current-status role,
not their bytes or historical meaning. Slice A's acceptance record remains frozen,
including its then-current Mode B non-authorization.

The approved Mode B package and manifest commitments remain
`fa1f3b3cbd9e9586a063ae7df10fc75a22298fa80d1971ef363ddf702bbe957e` and
`3be37d8858b50cba4d02bf9731c0d4eb0da85c35cd3fc0b79193afc7a505f970`.
Policy `ca302217d59d6ae80645f22db1a7121c2e70b686190daa73c82ab7270af3ca98`
and template bundle
`5b21b7cffe4aec2c4ef130f0e8c2e7681cb2bfbb57e2f80893df638ff8135a52`
are recovered from the retained evidence, not regenerated or reinterpreted.

## 3. Recovered evidence and verification scope

Strict base64 decoding, bounded zlib recovery, duplicate-key rejection, exact
canonical reserialization and SHA-256 checks recover both self-contained archives:

| Slice | Decoded bytes | Archive SHA-256 | Canonical objects |
| --- | ---: | --- | ---: |
| A | 44,144,528 | `4f5d5c7a3730b22ec6236e027175504e6fac155ca0372345475dd131079e6838` | 292 |
| B | 41,332,253 | `f05da5a10fe5d20f4771aed70175c280aba041017397cd4bf8c12ed7c8ddfa50` | 327 |

Every canonical object rehashes and reserializes exactly. Active role and replay
references resolve inside retained evidence. The original frozen package,
manifest, requests, premises, oracle forms, actual outputs, traces, mutation/twin
objects, comparison results and resource/reproduction evidence are recoverable
without standalone candidate JSON or external stores. This closeout verifies
retained evidence; it does not rerun derivation, minimax or dynamic tests.

Slice A records confirm seven cohort requests, 40 registered controls and approved
supplemental cases; 61 roles cover 59 distinct outputs, with the two disclosed
overlaps. All 210 recorded checks and twelve full-execution reproduction
combinations passed. Accepted primary scores remain T1=1 and T2=2.

Mode B records confirm:

- 27 active roles executed; all 28 expected outputs and nine refusal templates
  accounted for. The directed-premise role is inactive, not an executed success.
- All 238 focused checks passed, including dynamic semantic-read mutations and
  valid twins. Seven Mode B obligations E18–E21/E23–E25 and cross-slice E22 are
  linked to concrete executed cases.
- All 324 executions agree across twelve combinations of seeds 1/7/313, two
  disposable roots and forward/reverse permissible construction order. Per-role
  request/result and telemetry commitments are identical; comparisons include
  diagnostics, targets, ordering, provenance and traces without oracle exceptions.
- Actual input maximum is 11,410 and result maximum is 13,735 charged nodes.
  The 12,488-node hostile input was refused before owning reconstruction, with
  zero owning calls. Incremental result enforcement and bounded, nonrecursive
  refusal templates retain no partial success.
- B0 isolation, external A mutation/inversion, helper renaming and irrelevant
  input invariance are recorded. No Mode A prediction or expected answer was
  delivered to the B0 worker.

Recorded check/replay counts are assertions and reproductions, not inflated
numbers of independent operational worlds. Recorded preservation/isolation and
existing production verification are reused with attribution; no full production
or experiment suite is rerun for this administrative closeout.

## 4. Accepted bounded conclusions

1. Slice A demonstrated bounded filtering and minimax ranking over supplied
   synthetic premises under `finite_compatibility_minimax/v1`.
2. B0 recovered governing, observational and declaration material but did not
   derive hypothesis-conditioned predictions from the examined public surface.
3. Existing-contract population changed registration/declaration availability
   without closing that prediction gap. Population absence and contract
   expressibility are different questions; the positive population twin does not
   justify treating them as the same gap.
4. An explicitly supplied conditional rule enabled the expected ranking. This
   establishes sufficiency of that supplied premise within the experiment, not
   native derivation or prediction accuracy. T1 is preferred only within the
   explicitly supplied measurement set, with worst-case survivors 1 versus 2.
5. Directed influence was not tested. The experiment neither establishes its
   necessity nor rules it out. It does not establish that IN-001 is necessary.
6. The result supports a bounded next investigation into the representation,
   provenance and evaluation of hypothesis-conditioned predictions. Such an
   investigation needs a separate owner decision; this closeout does not start it.
7. No particular new package, record type, milestone or ADR is justified by
   acceptance alone. No successor is selected or authorized.
8. Objectives 3/4/7 receive experimental evidence about a missing capability;
   real diagnosis and next-best-test delivery remain incomplete. Objectives 5/6
   remain open. Closing the bounded experiment is not closing those capabilities.

## 5. Limits and remaining architecture questions

The findings are limited to the supplied finite candidates, synthetic premises,
selected population and examined typed public contracts. B0's selected world had
17 records; B2's positive population world had 23. These are not the authoritative
36-record ledger or a claim of exhaustive global model inspection. Native
contract conclusions rely on contract/API evidence as well as actual query paths;
an empty query alone cannot prove inexpressibility.

No real fault, physical cause, causal influence, prediction accuracy, global
hypothesis completeness, globally optimal test selection, general diagnosis,
production capacity, change-impact reasoning, planning or control is established.
Hypotheses and conditional predictions remain supplied assumptions; calculations
and bounded inferences do not become observations or engineering truth. The
assumption ladder and provenance boundaries remain unchanged.

Remaining questions include how an explicit prediction premise should be
represented; what evidence and provenance justify it; how its applicability and
predictive validity should be evaluated; which missing meanings can be supplied
through existing contracts versus separately approved extensions; and whether
directed influence is relevant to a concrete future use case. Several alternatives
remain possible. No future experiment, production design or successor proposal is
authorized by listing these questions.

Input operational limit stays 12,000 charged nodes; Slice A result limit stays
13,453; Mode B result limit stays 13,735; safety ceiling stays 16,384. Certified
admitted-input maxima are 11,567 for A and 11,410 for B; M_A_support remains 7,680.
Accounting remains canonical wire nodes plus per-occurrence typed StatementSlot
resolution charges, not recursive expansion of ordinary provenance/scalar refs.
All byte, depth, cardinality, reference and other bounds remain unchanged.

## 6. Documentation lineage, retention and commit scope

Only current status/retention navigation is amended in the existing synthesis,
Slice A plan and Mode B plan. Historical procedures and approved resource
contracts remain intact. The administrative commit also records the already
owner-approved, previously uncommitted Mode B resource amendment; it does not
change a limit today.

| Status surface | Before this closeout SHA-256 | After this closeout SHA-256 |
| --- | --- | --- |
| docs/superpowers/specs/2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md | `681e052c0bfc7af10fbbd6a8851ed70930e5f0d3dfc9d9243e142a74ae3eea04` | `03d17caac8daaa4953e4698ec81add76495dffd58b3428d75f9affee17930b23` |
| docs/superpowers/plans/2026-09-11-brc-exp001-slice-a-execution-plan.md | `f1524dd4eee3462ae0e487cff84a296c050a0ca46fe68941aeff5801f7dfa054` | `b90744258eaee2434fbd4c5b7c3c96a7fb0a98e92f85fa524de2c5658aa9c021` |
| docs/superpowers/plans/2026-09-12-brc-exp001-mode-b-execution-plan.md | `5ba74126969364a055bcb15594587e7b40c2a4ae93a8b818768ef00892af03ce` | `87b030cd984a45e345db55549493604085604c7bac34482c1a4f7292ec62bfa3` |

The exact documentation-only commit scope is:

- `docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-final-execution-report.md`
- `docs/superpowers/reports/2026-09-12-brc-exp001-final-owner-acceptance.md`
- `docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-output-resource-amendment-report.md`
- `docs/superpowers/specs/2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md`
- `docs/superpowers/plans/2026-09-11-brc-exp001-slice-a-execution-plan.md`
- `docs/superpowers/plans/2026-09-12-brc-exp001-mode-b-execution-plan.md`

The single additional supporting report is the unchanged Mode B output-resource
amendment witness. Its full canonical report bytes are not recoverable from the
final execution archive: that archive retains its digest and policy/template
bytes, but not the complete authoritative amendment/verification report. The
immutable execution report and retained plan also link to that witness. Retaining
it closes this amendment dependency without changing those frozen reports or
depending on an untracked authority document. Its own verified 8,715,588-byte
archive has SHA-256
`4b9ebefc9820789af3639cfef680ab1be2bf452971de2fe62fc908b4fed47eea`.

No other historical report, candidate package, manifest, JSON backup or unrelated
artifact is staged to manufacture a clean worktree. The historical Slice A review
keeps its exact local bytes and digest; its untracked navigation link is replaced
by the committed Slice A execution evidence link, while the complete operative
amendment remains in synthesis section 19. Mode B preparation data is recovered
from the execution archive rather than requiring its untracked rehearsal file.
The already committed Slice A reports and acceptance remain unchanged.

## 7. Preservation and closeout checks

Read-only public baseline verification confirms 36 authoritative records at
revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
236 model-kernel exports and FMA/FMW/FCD/FCW 0/0/0/0. ADR-0001–0022 remain
contiguous and unique; ADR-0023 is absent, unallocated and unreserved.

All pre-existing files other than the three explicitly authorized status surfaces
are hash-preserved, including both execution reports, Slice A acceptance,
historical failures, protected records/reports/witnesses and all standalone
owner-gate artifacts. Focused checks cover status assertions, full report and
canonical-object commitments, archive recovery, per-role resource recounting,
local links, markers, preservation and whitespace. The exact staged paths and
blobs are inspected before commit; recovery and preservation are repeated against
committed report bytes afterward. No clean-worktree fiction is asserted.

No production source/test, fixture, ledger, identity, membership, canonical
artifact or cap changes. No new ADR, successor proposal, push, merge or history
rewrite. Only the authorized documentation commit is created. Temporary recovery
tooling is removed after verification; disposable experiment tooling remains
deleted. BRC-EXP-001 is owner accepted and closed as a bounded experiment.

END OF BRC-EXP-001 FINAL OWNER ACCEPTANCE
