# Bounded next-measurement selection — focused identity/closure confirmation

2026-09-19. Independent documentation confirmation of FR-M1/FR-M2 and their consequential interactions only. No contract freeze, fixture/resource preparation execution, implementation, tests, application/proof execution, experiments, dependency changes, ledger/ADR changes, commits or remote operations.

## Provenance and verdict

I am the returning `measurement_focused_reviewer`, author of the frozen focused re-review and not author of this candidate. I read the complete frozen design, complete frozen review and complete candidate, and compared the changes. This is independent reviewer staffing within the same agent environment, not independent empirical evidence. I performed substantive specification reasoning; no predicted outcome below was executed.

Local HEAD verified: `6351750b3cacad288cb99d9d11a8b61b6fe85b71`. No remote publication check.

| Object read completely and hash-verified | SHA-256 |
| --- | --- |
| [Frozen corrected design](../specs/2026-09-19-maintained-bounded-next-measurement-selection-corrected-proof-design.md) | `4a703558f0974a77e710ca66ea1df5854f86c683cc1d3b599b485b03f9c221bb` |
| [Frozen focused re-review](2026-09-19-maintained-bounded-next-measurement-selection-focused-rereview.md) | `66203085f45533c2e96e368cc3abed33d2cf73df891f92cb2c8692f73ce0e3c3` |
| [Identity/closure candidate reviewed](../specs/2026-09-19-maintained-bounded-next-measurement-selection-identity-closure-candidate.md) | `8726f35dac9997ee82c0764c95f749cb462e796c6d04794758a90775d0671305` |

**Verdict: `confirmed_for_owner_decision`. FR-M1 and FR-M2 are closed in this candidate at documentation-design level. Remaining findings in this focused scope: 0 Critical, 0 High, 0 Medium, 0 Low.** No additional required correction was identified. This does not retroactively change either frozen source, establish passing proof evidence, approve the candidate on the owner's behalf, or authorize preparation/implementation.

## FR-M1 — confirmed closed

Section 2A requires unique `(kind,id)` within each Q's H and P nomination arrays, independently of revision/digest. It applies separately to historical and current Qs, so historical versions can coexist without being co-nominated. The explicit identity maps make every current result label resolve to exactly one versioned content reference. Separate H/P namespaces and decoder-scoped outcome IDs prevent cross-kind or cross-procedure label confusion.

The original counterexample now refuses: H1@1 and H1@2 representing different account kinds within one Q receive `DUPLICATE_NOMINATION_ID` before alias/mapping work. Distinct logical H1/H2 under T2 produce `["H1","H2"]`, cardinality 2; the two repeated T2 branches cannot collapse into T1's singleton split. Different Q revisions may respectively nominate H1@1 and H1@2, but old support never transfers by logical ID alone. Correctly rehashed stale procedure/decoder support still fails its exact join.

Consequential checks are coherent:

- Exact duplicate references, same-ID/different-version nominations, and same-ID/same-version/conflicting bytes have distinct prescribed refusals. Closure integrity precedes nomination subchecks; resource guards precede work.
- Canonical nomination order is checked, not repaired after hashing. Canonical construction from different insertion orders is distinct from accepting reordered wire arrays.
- Logical uniqueness is not a replacement for semantic-alias rejection: different-ID copies of the same meaning still refuse; genuinely distinct methods may tie.
- Survivor members are unique, but the multiset of branches is not deduplicated. Repeated empty or repeated nonempty branches remain. Cross-request equivalence requires exact identity maps/viable references, not shared spelling.

The additional same-ID, repeated-reference, collision, revised-request, permutation and multiplicity obligations in §7A are sufficient to expose the original defect and its nearest valid twins without adding another ranking criterion.

## FR-M2 — confirmed closed

Sections 3/4/4A/8/9 consistently choose **bounded transitive required-reference closure**, as directed. The former immediate-only inspection promise is removed; no terminal predecessor alternative remains. Every declared Q ancestor and its required dependencies must be captured through the explicit revision-1 root. Every D member Q is required, not just the selected member. Thus Q3→Q2→Q1 with Q1 absent refuses `REQUIRED_REFERENCE_MISSING` when reached within budget; a checksum-only Q1 does not satisfy it. The complete twin may proceed to current semantic eligibility.

Required versus optional boundaries are explicit. Typed application edges, basis bytes and fixed-role build/resource witnesses are required. Unreferenced prior results/adoptions/dossiers are optional context, not hidden authority or recoverability claims. Opaque basis text does not create executable edges. Embedded public-result material is validated by its owning contract; raw custody checksums do not authorize fetching arbitrary source files. These boundaries narrow traversal by role without exempting a required ancestor.

Historical scope is appropriately limited: ancestor/other-member schemas, lineage, nomination rules, intrinsic decoder constraints, exact joins and public reconstruction must be valid. Their missing scientific support or inapplicable conditions do not propagate a current withholding conclusion. Historical H consistency, support mapping, all-excluded mapped rows, scores, recommendations and working adoption are not evaluated/imported. A malformed historical dependency can nevertheless refuse current evaluation because required integrity is not optional. Current phases 5–8 use the current Q and its selected authority/support/policy only.

Sharing/cycle/resource interactions are specified without a loophole. Deterministic incremental traversal returns the first reached failure, after applicable guards; it does not promise global error sorting at unbounded cost. An active target is a cycle, whereas a completed matching-scope target can be shared. Every occurrence still incurs its edge/context/effective-limit obligations; completed byte validation cannot cache eligibility. Missing deeper content can be preceded by a legitimate resource refusal. Over-budget complete closure cannot be truncated into success. The isolated future traversal-checker obligation does not pretend a hash-consistent cyclic file graph is easy to construct and adds no product bypass.

Standalone replay retains/revalidates the full required closure under the captured build/policy, then recomputes only the selected current request. It does not need old result bundles or remote history, and cannot use a prior verify flag to bless missing content. The new future demand dimensions cover ancestor expansion, public reconstruction, contextual repetition, retained bytes and replay rather than assuming a one-predecessor allowance.

## Preserved semantics, obligations and owner gate

The correction does not change supplied-prediction qualification, independent exclusion justification, prior-free minimax/no costs, whole-nominated-set withholding, zero/one H/M dispositions, ties, branch multiplicity, isolated unsupported-exclusion bypass, semantic-substitution twins or unresolved manual C. The existing P/T/U-B-V/A/G/X/S/J/E/N/R expectations remain; §7A adds only identity and closure witnesses. No broader architecture or backend requirement is introduced. Existing thermal contracts/commands/replay remain outside the change.

There are no remaining defect findings in this confirmation. The following remain explicit future obligations, not passing evidence or newly authorized work: freeze exact diagnostic/wire/build/retention layouts; construct valid public fixtures; independently specify expected graph/set results; calculate complete demand/headroom and approve immutable limits; later measure physical work/time/memory and standalone replay under separate execution authorization. Functional matrix cardinalities do not prove closure capacity, and no numeric ceiling is supplied or increased here.

Approval-ready semantic rules are per-Q logical nomination uniqueness with exact version joins, and complete bounded required closure with integrity-only historical scope, deterministic refusal precedence and no partial success. The owner has directed these corrective approaches; terminal ancestry is no longer a pending alternative. Final approval of this exact candidate remains the owner's decision, together with the still-pending supplied/conditional scope, minimax/withholding/cardinality policy, local authority roles/manual C and standalone replay scope. Exact future preparation packages and resource amendments require their own disposition. Reviewer confirmation supplies none of those approvals.

**Recommended next gate:** owner disposition of this candidate and confirmation. A favorable owner decision may be accompanied by a separately bounded preparation authorization, but this report grants neither preparation execution nor contract freeze, proof execution or implementation. No additional reviewer or broad investigation is required by this confirmation. IN-001 and CI-001 remain open and unselected.

This reviewer created only this report; all existing artifacts were preserved. The lead retains responsibility for the whole-task inventory receipt.

END OF FOCUSED IDENTITY/CLOSURE CONFIRMATION
