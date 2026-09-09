# FC-001 Codex Lead Proposal Challenger Audit

Date: 2026-09-09. Scope: one adversarial, audit-only review of the frozen lead proposal. This report evaluates the recommendation afresh against repository contracts; it does not treat the author's recommendation or the absence of G1 as sufficient justification. Scenario worlds below are reasoning examples, not created fixtures, minted identities, appended records or executed FC tests.

## 1. Frozen-input and baseline verification

| Item | Independently checked result |
| --- | --- |
| [Frozen FC proposal](../proposals/2026-09-09-fc001-codex-lead-proposal.md) SHA-256 | `8a65e3a4721fc0ba3dc28b0772e920f2dcc3008a9e1411ce07c9a8d1b204749e` |
| Size | 312 lines; 47,882 bytes |
| Structure | 20 contiguous numbered sections |
| Final marker | `END OF FC-001 CODEX LEAD PROPOSAL` |
| Branch / HEAD | `main` / `c0e1c8fe930e10243fec16a4950a3d34d4c85df4` |
| Local `origin/main` | `d888ba6fbfb313cf2f85ce5cb07168fb528ec059` |
| Difference | Exactly one commit; five documentation files in the accepted FA closeout. Expected, not a discrepancy |
| Authoritative model | 36 records; `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Ledger inventory aggregate | `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a` |
| FRG/FLD/FLW; TRG/TRD/TRW; FMA/FMW | `1/1/0`; `0/0/0`; `0/0` |
| Kernel exports | 225 distinct names |
| ADRs | Contiguous ADR-0001–ADR-0021; ADR-0022 absent |
| Initial worktree | Frozen FC proposal untracked; no tracked changes |

The model was loaded read-only and its revision/counts checked, not inferred solely from documentation. Source inspection covered [canonical FM body projection](../../../backend/model_kernel/canonical.py), [record contracts](../../../backend/model_kernel/contracts.py), [collection validation and lifecycle indexes](../../../backend/model_kernel/store.py), [public queries](../../../backend/model_kernel/queries.py), [FM result derivation](../../../backend/model_kernel/flow_measurement_results.py), [FL support derivation](../../../backend/model_kernel/flow_results.py), [CN reconstruction](../../../backend/constraint_evaluation/contracts.py), and [alignment's public contract](../../../backend/evidence_alignment/README.md).

Preserved artifact digests were independently recomputed: FA owner decision `a65761f26d1c646a41a5af10fb8b4af10aa04d72ef5263f7fe04d4fa16f6290a`; FA proposal `c818e4e342bd9450c5e1d19513bae336097f7601648ef1a8f73232e490d37c17`; FA audit `65114fcc03cbe07a90cfceb349bea1ea7dba2c3f21f67f835cb100c76b062980`; local settings `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`. The committed audit's original CRLF bytes remain untouched. FA runtime remains deferred.

## 2. Executive verdict

**Verdict: `approve_with_corrections`.** The core FC semantic recommendation is defensible and useful for the named single-criterion workflow. No blocking defect in FC's governing object, ownership or truth boundary was found. One required correction tightens the future FA gate: absence of a single combined validator is not evidence that existing public-result join checks are insufficient.

Counts: **0 blocking findings; 1 required correction (C1); 5 non-blocking observations (N1–N5).** Open owner policy approvals are adjudicated separately and are not counted as defects or silently granted by this audit.

Proceed to semantic synthesis with the four policy decisions made explicit and C1 incorporated in the future synthesis/decision record; do not edit the frozen proposal. No API names, record prefixes, ADR or implementation are ready to be allocated merely because this audit is favorable.

## 3. Architectural-integrity verdict

**PASS for the FC semantic architecture; a future-authorization correction is required.** The fact is applicability, not evaluated state. It belongs beside the existing model declarations and can be validated from same-ledger material without CN, EA, temporal or source imports. Existing identities, predicate machinery, FM meaning and record bytes need not change.

The strongest honest interpretation is: an authority has designated an exact constraint edition for an exact FM body; the query additionally reports whether the proposed selected-membership currentness policy admits its present use. Record presence, agreement, applicability and numeric evaluation stay separate. Reject any implementation that substitutes one generic green status for those axes.

Canonical body equality is available, but adopting it as the object of a new governing declaration is a **new FC policy**, not an inference already authorized by FM. The proposal openly asks the owner to accept that policy. Full carried model material provides reconstruction, not authentication, authority ranking or proof that the chosen membership is the latest one.

## 4. Baseline-goal-contribution verdict

**PASS, narrowly.** Absence of a governing relation alone does not justify a record. The decisive additional facts are the owner's approved commissioning/operations consumer, the need to distinguish two existing predicates on the same variable, and the requirement that the designation be explicit, queryable and replayable model meaning.

Today an external procedure can tell a human which constraint to use; a human can also manually select a CN result. Those are legitimate alternatives, not unsafe by definition. However, neither is a typed governing relation available through the accepted model queries. Encoding it in free text or names would require a new interpretation convention and would not inherit FC's closure, lifecycle or conflict checks. For the approved model-centric question, FC supplies a real missing fact rather than a new name for admission.

FC alone identifies the governing edition without observing anything. Existing CN plus evidence then answers selected-sample conformance. FC does not answer physical state, diagnosis, next-best-test optimization, impact propagation, planning or control. A deployment that only needs an external human procedure may reasonably decline FC; the present owner has selected the model-declared workflow instead.

## 5. Governing-object audit

The accepted canonical projection in `canonical.py` includes flow, variable, participant port, exact context, orientation and all six FRG/VRG/PRG/FLD/VPA/VSM IDs. It excludes assertion ID, authority, evidence, timestamps, note and ancestry. Direct-measurement relevance is fixed by the accepted FMA kind and measured-actual support. Canonical JSON serialization and the loaded effective-body indexes make this reconstructible without minting a new identity.

Two FMA assertions with the same projection assert the same **typed relevance proposition**, not the same authorship, evidence strength or endorsement history. Since the consumer asks which meaning the FC authority designates, not which engineer's continuing certification it requires, this equivalence is adequate. A note cannot contain a hidden exception that changes body meaning; a required authority qualification would need an explicit separate contract or exact-record policy.

The nominated witness is sufficient to fix exact immutable contents and dependencies. It must be explicitly supplied, never auto-selected as the lowest ID or the “best” authority. FC may derive body equivalence from another current assertion, but may not discard the nominated witness from its provenance or silently replace its ID. An opaque body hash alone would be insufficient: it neither closes the underlying references nor proves which fields were hashed and would act like a second identity mechanism.

The following explicit worlds use symbolic names only. Let W1 and W2 be independent FMA roots asserting body B for subject S; W3 asserts B2, differing in one support ID. Let D designate constraint edition A for B using witness W1. Other typed support and constraint gates are admitted unless the row says otherwise.

| World | Audit expectation |
| --- | --- |
| W1 alone is current and healthy | D can be presently applicable |
| W1 and W2 are current/healthy with identical B, different authority/evidence | Corroboration; both provenance chains remain visible |
| W1 is superseded by W1a with only evidence/authority/note changes and the same B | D can remain applicable through W1a; original W1 must remain membership-present |
| W1 is corrected to B2 and no active B remains | D cannot follow B2; the authority must explicitly renew FC for B2 |
| W1/W2 assert B while healthy W3 asserts B2 for S | Active body disagreement blocks the single governed selection |
| W1 is withdrawn; W2 remains healthy with B | D can remain applicable under the proposed body policy |
| Both W1 and W2 are withdrawn | D remains a historical designation; no presently supported B |
| Selected replay omits W1 but retains D and W2 | Invalid closure, even though W2 has the same body; D's witness is mandatory |
| Replay omits W1's withdrawal, retains D/W1 and required closure | Earlier activity can reappear; this is membership-relative, not physical history |
| Replay retains a successor but omits its required parent | Invalid membership; not a permissible historical simplification |

**Governing-object verdict: approve effective-body pinning for this consumer, subject to explicit owner acceptance of its endorsement semantics.** Exact-record dependence is more honest only when that particular assertion's continued endorsement is part of the intended proposition. It is not universally more honest and would add churn without answering the approved question better under the stated policy.

## 6. Authority and withdrawal semantics

Distinguish the authority of the FMA witness from the authority of the FC designation. The first asserts measurement relevance; the second chooses the governing criterion. Retraction of the first claim is not automatically retraction of the second authority's decision. The accepted withdrawal contract says “no longer asserted,” not “false,” “unsafe,” or “all other authorities revoked.”

Consequently W1's withdrawal does not revoke D when another eligible assertion still supplies B. This remains honest even if the same human authored both records: record kinds and targets define what was withdrawn. If that human intends to retract D too, the corresponding FC withdrawal is needed. A cross-family cascade inferred from matching authority names would invent authorization semantics and break deterministic explicit closure.

Likewise withdrawal of one corroborating FC root is not universal revocation when another active FC root designates the same B/CRG/VCN. AuthorityRef is only a recorded claim of authorship; it is not a role-based permission system. A new lower-ranked or hostile claimed authority can create disagreement under the proposed policy. That availability cost follows from the accepted no-ranking trust boundary and must not be concealed as authenticated consensus.

Evidence/endorsement distinctions are preserved in full material, not used as body equality dimensions. The consumer must not describe a surviving body-based designation as still endorsed by a withdrawn witness authority. A workflow requiring a named engineer's continuing approval is out of scope for this body-based contract, not a case for guessing that requirement from prose.

## 7. Correction/agreement audit

S is a defensible correction key for **one designated criterion slot per exact FM subject**. The governing VCN/CRG is what that slot asserts, so explicit correction may change it. The new CRG must still target S's variable; changing flow, variable, participant, context or orientation is not an in-lineage correction. Parent closure and same-root derivation prevent a correction from becoming an implicit global replacement.

Let D0 be an FC root; D1/D2 supersede it. All examples retain required model dependencies.

| Scenario | Correct outcome |
| --- | --- |
| D1/D2 have identical governing bodies | Same-root conflict persists; equality does not resolve ancestry |
| D1/D2 select different constraints | Same-root conflict; neither is usable as the unique criterion |
| Two independent healthy FC roots agree on B and exact CRG/VCN | Corroboration, not a duplicate-identity error |
| Independent roots use W1/W2 as different same-body witnesses | Same governing meaning, distinct record identities/provenance |
| Independent roots select different VCNs, even on the same variable | Cross-root disagreement; no latest/easiest/strictest winner |
| Inactive disagreeing root beside healthy agreement | Historical disclosure only; no active veto |
| Withdraw D2, leaving D1 as the only current fork tip | Root becomes healthy under selected-membership rules |
| Withdraw one of two corroborating roots | Other root can keep designation applicable |
| New correction cites every current same-root fork tip | Explicit convergence can resolve that root |
| Correction omits a current sibling tip | Uncited branch survives; not global convergence |
| Correction cites parents from two independent roots | Reject cross-root convergence |
| Replay omits a withdrawal and retains required parents | Earlier tip or conflict may revive; never silently select by time |

Real commissioning can have several mandatory criteria. The proposed conflict rule must not be generalized to mean those criteria are logically contradictory. They are **incompatible selections for the single supported slot**, not evidence that one requirement is false. The owner explicitly chose one criterion; this is a sound bounded version provided it is not described as a complete commissioning checklist.

Several participants and relevant variables create different S values and therefore separate lookups, not an implicit all-of result. If a consumer needs two mandatory criteria for the same S, decline that request or seek a separate multi-criterion contract. Do not abuse different orientations, artificial contexts or extra roots as checklist item identities. No need to introduce an anchor now merely to anticipate that excluded use case.

## 8. Constraint edition/currentness audit

CRG fixes the ConstraintAnchor-to-variable association permanently within a valid membership. VCN fixes the particular numeric predicate and expected semantics. FC appropriately governs **both the existing constraint identity and one exact assertion edition**, through CRG/VCN pins; it does not create or replace either identity.

An exact CRG pin also makes registration provenance explicit across differently selected memberships. It is somewhat redundant with VCN-to-anchor lookup inside one validated membership, but serves an exact support-commitment purpose rather than introducing a new anchor. Another CRG targeting the same variable is not a substitute.

The repository does not define a public VCN effective-body/predicate-equivalence contract. A correction with numerically equal bounds may differ in semantic signature, authority or evidence. Exact-edition renewal is a conservative authority-control choice: no predicate comparison, equivalence algorithm or floating lookup is needed. It incurs real administrative churn, but is coherent with the user's one exact existing criterion and CN's existing current-declaration behavior.

| Constraint situation | Required distinction |
| --- | --- |
| Pinned VCN is the sole current declaration | Potential FC applicability; sample still unevaluated |
| Same ConstraintAnchor now has a different sole current VCN | Historical designation remains; exact edition is stale and present applicability is withheld |
| A VCN correction changes metadata only | Same policy: renewal needed; no invented semantic equivalence |
| Several active VCN tips | Constraint conflict, not mere staleness and not predicate falsity |
| Nomination references absent/wrong-kind VCN or wrong target CRG | Structural invalidity, not a valid negative applicability result |
| Constraint lookup has a registered anchor but no VCN | Existing lower absence disclosure; cannot coexist with a valid FC that pins a membership-present VCN for that anchor |
| A same-variable different constraint's satisfied CN row is supplied | Join mismatch; never substitute it for the governing edition |

For a valid finite VCN DAG containing the pinned VCN, at least one current tip exists; VCN has no accepted withdrawal kind. A “valid FC with no current VCN at all” is therefore not a reachable current-contract test world. Historical CN evaluation is possible only using a selected closed membership in which that exact VCN is current, with matching FC/model material; not by asking current CN to evaluate an arbitrary stale declaration.

**Verdict: accept exact-edition pinning and renewal as the first-scope policy.** This preserves CN rather than redesigning it. Calling stale FC merely “declared” is appropriate for historical inspection, but admitting it as presently applicable while CN evaluates another VCN would be misleading.

## 9. Direct and transitive support audit

The proposed support policy is stricter than the bare proposition “authority designated criterion A for historical body B.” It is an eligibility policy for present use in the selected model membership. This extra policy is explicitly proposed, not a necessary engineering truth deduced from FM. I accept it for the initial known-edition commissioning workflow, provided the owner approves it as such and historical designation stays inspectable.

| Support | Audit of proposed gate |
| --- | --- |
| FRG/VRG/PRG/CRG | Permanent membership/identity checks; no lifecycle ranking or timestamp currentness exists |
| Active FM roots for S | Require healthy roots agreeing on B; appropriate to an unambiguous single slot, not unanimous authenticated endorsement |
| Exact FLD/VPA/VSM | Require actual current activity and healthy lineage separately from alignment |
| FLD's exact PCN/PIF support | Conservative no-silent-edition-change gate; adds no physical connectivity proof |
| Exact VCN | Current identity/edition gate already justified by the CN join |
| Historical EvidenceRef citations | Membership closure only for model references; never require every cited claim to remain current |

This distinction is confirmed in FM derivation: `_claim_support_state` can return alignment `exact` for a superseded pin or conflicted active root. `_semantic_support_state` can return `exact` when several tips all declare measured-actual. Therefore “aligned” alone is not sufficient. The proposal correctly requires separate activity and health checks. FL's PCN/PIF alignment similarly derives from pinned activity and containing lineage; it is not an observation of connectivity.

Transitive PCN/PIF admission closure is necessary to reconstruct the selected FLD. Requiring those exact records to remain current is **not logically necessary** to retain an authority's designation of that historical body. It is also not numerically necessary to evaluate the variable predicate. Its defensible benefit is refusing silent use of a commissioning designation after the selected declared topology/direction edition changes. It reuses FL disclosures rather than reimplementing their meaning.

Metadata-only PIF or PCN correction consequently blocks present applicability until the explicit support chain is renewed: new FLD pins, new FM body, then explicit FC renewal as necessary. This can involve considerable documentation churn. The proposal accurately discloses the same strictness for FLD/VPA/VSM and VCN, while deliberately allowing same-body FMA metadata changes. No inconsistency follows: FMA assertion metadata is outside B; its support-record identities are inside B.

Withdrawal or conflict in typed support blocks eligibility; inactive unrelated historical roots do not globally veto it. Crucially, the rule is not “all lower logical-flow declarations agree.” A separate healthy FL root can disagree while the exact pinned FLD's own lineage is healthy; the proposed FC gate does not explicitly require global FL-root agreement. That is a scope limit, not proof that the selected FLD is globally uncontested. See N2. No physical flow, whole-flow validity or actual wiring conclusion can follow from these checks.

## 10. Representation/package/import audit

| Alternative | Independent assessment |
| --- | --- |
| Existing generic relationship | Entity-anchor endpoints cannot directly encode FMA-body/VCN support. A new label or owner statement can describe a procedure but is not a typed governing relation; parsing it would introduce new semantics implicitly |
| Extend VCN | Couples an existing variable predicate to independently correctable flow/context meaning; changes accepted grammar and makes reuse across loci awkward |
| Extend FMA | Makes measurement relevance optionally carry a governing criterion, coupling unrelated lifecycle facts and changing accepted FMA meaning/bytes. An additive declaration is cleaner |
| Separate sibling ledger | Adds cross-ledger closure, revision coordination and another store without independent ownership need; loses same-membership proof simplicity |
| Pure presentation selection | Safe when labelled as a caller's choice; not an authority-declared model fact and lacks durable correction/withdrawal semantics |
| External commissioning procedure | Can safely direct a human and should be preferred if that suffices. It does not already furnish the accepted model-query/replay contract sought here |
| Existing ST/BH/TA | ST is an entity-scoped declared conjunction, BH a behavior relation, TA a transition assessment; none declares that this exact constraint governs this FM body |
| Do nothing | Reasonable if the owner relinquishes model-declared designation; does not answer the approved software question |

Two conceptual record kinds—positive designation and retraction—are the smallest **precedent-consistent** durable representation with explicit correction and withdrawal. They are not the only theoretically possible encoding: a tagged single schema could encode both, but would still represent two different semantics and must not make a withdrawal a positive citable claim. No separate registration or durable anchor is justified for a relation among already identified objects.

Positive evidence is necessary to record the authority's declared basis; it cannot be fabricated by the presence of support pins alone. Existing nonempty EvidenceRef and AuthorityRef contracts suffice. An uncitable withdrawal without an evidence field is consistent with FM/FL/VP's non-claim retraction; its note/authority/time can record administrative explanation without becoming evidence that the original was false.

All hard pins and model-evidence closure can be validated in `backend.model_kernel`. Kernel access to VCN contracts/query data is not an import of CN evaluation. No CN, EA, alignment, semantic-compatibility or temporal import is needed. The prospective explicit model-store write boundary is distinct from pure loaded-model queries and carried-material reconstruction. No upper result or observed value is stored in FC, and no circular ownership is required.

## 11. Named-consumer decision-usefulness test

For the **commissioning/operations verification workflow**, take one FM subject and two existing constraints on its variable: A is inclusive interval `2`–`4`; B is upper boundary `10`. FC explicitly designates A. A fully admitted nominated `4.7` sample violates A and satisfies B under CN.

FC creates a legitimate new decision: the reviewer must reject B's satisfied verdict as evidence of meeting the **declared** check. The exact governing edition and model relation identify A independently of which result is favorable. Without FC, B is not a wrong target under the existing type contracts merely because a human intended A; that intent has no typed governing representation. This is operationally useful model meaning, not decorative metadata.

| Consumer situation | Legitimate use of FC |
| --- | --- |
| No observation | Identify the applicable declared criterion; do not mark it satisfied |
| Criterion exists but CN cannot evaluate | Keep the check unevaluated with CN/evidence reasons; no false violation |
| Observation changes from `4.7` to `3.2` | FC remains unchanged; A's CN verdict can change to satisfied |
| Governing criterion changes with observation fixed | New FC correction/revision changes which exact result is admissible, or creates conflict; no use of an old revision's CN result |
| Consumer asks whether physical flow occurred | Refuse that stronger reading, even with applicable FC and satisfied CN |
| Several mandatory criteria for the same subject | Out of this single-slot scope; not a full checklist and not a reason to pick one favorable requirement |
| Several flow participants or relevant variables | Separate exact subjects; no participant-to-whole-flow or arbitrary-variable generalization |

The authorized action is to record a specific selected sample's predicate outcome against a specific declared check, or leave that check open. It is not permission to energize equipment, certify commissioning complete, recommend a change or claim safety. This bounded distinction passes the consumer usefulness test.

## 12. Contract-theatre test

**PASS: the FC fact survives removal of all observation-admission statuses.** With no sample at all, FC still identifies the criterion authority selected. Changing the FC declaration while keeping FM and CN inputs fixed changes which existing predicate result belongs to the check. Neither FM relevance nor numeric evaluation already provides that governing selection.

Conversely changing only the observation must not change FC's query. A value-dependent applicability status would move assessment into the declaration layer. Requiring every candidate, adding a confidence score or combining compatible/aligned/admitted flags would not strengthen the missing relation and should be rejected.

The check is not “a record exists.” It is that the named consumer can reject substitution of satisfied B for violated governing A through an exact reconstructible relation. A human procedure can already do that for a human; FC is justified here by making that authority choice a typed model fact with the requested replay/provenance boundary. If the consumer stops needing that boundary, abandon FC rather than justify it by the vacant milestone name.

## 13. Original-objective contribution matrix

The original questions are reproduced from [CLAUDE.md](../../../CLAUDE.md). This matrix does not credit a disclosed missing prerequisite as an optimized next action.

| Original question | FC alone | FC with CN and evidence | Still absent |
| --- | --- | --- | --- |
| What exists in this system, and how is it connected? | Explicit governing relation and its typed dependencies | Same relation attached to an evaluated sample | As-built/physical connectivity truth |
| What is the current state of this particular system? | No physical or measured state | Bounded selected-sample conformance at a receipt cutoff | Freshness, actual flow/activity, continuous state |
| Why might the system be behaving this way? | None | Computational trace, not causal explanation | Diagnosis, causal models and alternative explanations |
| What is the next best measurement or test? | No progress on “best” | No progress on “best”; an unevaluated check is not an optimized next test | Information gain, uncertainty, cost and experiment selection |
| What would be affected if this component, parameter, or software version changed? | Inspectable declaration dependencies only | Stale edition can be identified | Impact propagation and counterfactual inference |
| What is the smallest valid set of changes needed to reach a desired state? | None | None | Goals, action effects, planning and control |
| Which conclusions are observed, calculated, inferred, assumed, or unknown? | Authority-declared applicability separated from observation | Declaration, calculated predicate result and selected evidence distinguished | Authentication, uncertainty and complete epistemic coverage |

Net: FC directly advances 1 and 7, provides dependency discoverability relevant to 5 without answering impact, and enables only a narrow contribution to 2 through existing evaluation. There is no claimed contribution to causality, next-best-test optimization or planning.

## 14. FA cancellation test

**Recommendation: cancel FA after FC acceptance/implementation demonstrates the direct answer.** The required answer can be assembled from one FC query, one nominated row of an existing CN result, and existing evidence/provenance disclosures. “One CN result” need not contain only one candidate; nomination identifies one exact row. No new flow proposition remains to evaluate.

Explicit checks available from public material defeat the contemplated substitutions:

| Attack | Existing-data check |
| --- | --- |
| Supply satisfied B instead of governing A | Compare exact FC CRG/VCN and variable to CN's carried constraint registration/declaration, not just variable identity |
| Supply CN from another membership | Compare exact model revision and the reconstructed governing records; reject revision/content mismatch |
| Supply an old VCN with the same ConstraintAnchor | Check exact edition and current applicability, not numeric equality |
| Pick a more favorable candidate or occurrence | Check independently nominated strict candidate path, six-field locator and full occurrence |
| Pair CN with another snapshot/alignment | Compare CN's carried VS material with alignment's consumer; validate full occurrence/cutoff identity and independent expected fingerprint |
| Hide additional FC roots | Reconstruct FC query from complete carried selected membership |
| Replace every model/evidence object and their self-reported hashes coherently | Requires independent expected commitments under accepted boundaries; a new FA wrapper cannot manufacture authenticity |

FC and CN individually do not validate their mutual join. That does **not** show the join cannot be checked using their existing public fields and validators. None of the listed attacks survives the explicit checks above. Convenience, a single result object, lower object size, or moving those checks into a named package does not satisfy the requested justification for FA.

The proposal's Section 15 leaves a broader opening: a consumer request for a single independently reconstructible boundary plus a substitution attack “otherwise” crossing the boundary. **C1:** narrow that gate to an attack that cannot be prevented by explicit join checks using existing public results. Require a demonstrated missing property, not merely absence of a combined validator. No such attack or missing property has been demonstrated here.

This is an audit recommendation for the later owner gate, not an administrative change to FA's current deferred status. Do not implement or allocate FA while investigating it.

## 15. Zero-FMA/disposable-demonstration audit

Confirmed: the authoritative model has 36 records and zero FMA/FMW. It has no witness for an FC positive assertion. Even after a future FC grammar exists, a positive FC append over that unchanged membership would fail support closure. The current implementation also has no FC kind. Do not conflate those two independent reasons with a demand to populate the ledger now.

A labelled disposable world is sufficient to prove the software's governing selection, refusal of constraint substitution, same-body witness replacement, loss of all supporting bodies, both satisfied and violated CN outcomes, and full carried provenance. Require public construction/query/evaluation paths in a later authorized implementation test, including EA/alignment for snapshot-backed claims; not fabricated already-green result objects.

The worked example proves a model/software capability, not real sensor calibration, physical occurrence or successful commissioning of the authoritative system. An authoritative append would add no necessary evidence of the declaration semantics and is not required. This audit created no worlds or fixtures and ran no FC tests; its worlds are design counterexamples and obligations.

## 16. Threat-model and acceptance-matrix critique

The proposal covers the main threats: governing-criterion substitution, concealed roots, stale-pin reuse, authority laundering, body drift, hidden state, index forgery, graph amplification, lower import inversion and truth inflation. Full material plus exact nominal joins is the appropriate integrity boundary; no new authoritative store or remote dependency is needed.

Strengthen future acceptance evidence with these explicit pairs, some covered only generally in the current matrix:

- **Same authority versus different authority:** withdraw W1 while W2 remains, then separately withdraw D; prove no inferred cross-family revocation in either case.
- **Omitted witness versus withdrawn witness:** one is invalid closure, the other can support historical body selection. Equal replacement bodies do not repair missing references.
- **Equal-body fork versus independent corroboration:** equal fields do not erase different ancestry semantics.
- **Exact VCN absence reachability:** missing referenced VCN is invalid, while no declaration for an otherwise registered nominated constraint is lower absence. Do not manufacture a valid FC with an impossible empty VCN tip set.
- **Historical evidence versus typed support:** supersede a cited evidence record without changing a typed pin; applicability must not be blocked merely by evidence age/activity. Then change a typed pin and verify the separate policy.
- **Lower local health versus global agreement:** introduce another FL root while leaving the pinned FLD lineage healthy; verify only the explicitly selected FC gate, not an invented global topology guarantee.
- **Same S with two legitimate procedure requirements:** disclose unsupported single-slot scope, never “requirement B is false” or a complete-checklist conclusion.
- **End-to-end substitution:** A violated/B satisfied, matched versus mismatched revisions, candidate paths and snapshots, with explicit join checks shown to defeat each attack before proposing FA.

The inherited depth/node limits are not a complete expanded-byte budget; the proposal acknowledges that. Exact canonical grammar, aggregate limits, hostile subclass rejection, repeated-DAG accounting and exact-bound witnesses must be specified before implementation. Their deliberate deferral does not stop evaluation of body pinning or package ownership. Consumer usefulness and every-field justification remain review judgements, not executable test counts.

## 17. Owner-question adjudication

| Owner decision | Independent adjudication | Consequence to approve explicitly |
| --- | --- | --- |
| 1. Effective body versus exact record | **Recommend effective body via exact witness** | Witness must remain in membership, but its own current endorsement is not mandatory if another healthy same-body assertion remains. Choose exact-record dependence instead only for an endorsement-specific consumer |
| 2. S correction subject and active-root agreement | **Recommend S and agreement for one criterion slot** | Same-root forks block even when bodies match; independent equal bodies corroborate; inactive roots do not veto; multiple requirements for the same S are unsupported, not false |
| 3. Exact VCN and support-edition currentness | **Recommend exact VCN and the disclosed conservative support policy** | Metadata-only support correction can require renewal. Transitive PCN/PIF currentness is selected-model eligibility, not necessary truth of a historical designation or physical connectivity |
| 4. Two additive kernel records, positive evidence, uncitable withdrawal, no anchor | **Recommend** | Positive applicability/retraction semantics fit existing ledger/replay boundaries; no new identity or upper imports are warranted |

These are independently evaluated recommendations, not owner acceptance. If the owner changes any of these semantics, the synthesis must restate the object, body equality and lifecycle consequences before API design. The already approved consumer, one candidate/criterion, excluded physical/temporal policies, public proof boundary and disposable demonstration sufficiency need not be re-opened.

Semantic synthesis can proceed now with those decisions and C1 on its agenda. Names, prefixes, field order, statuses, numeric budgets, public query grammar and implementation slices remain deliberately unfrozen. None should be allocated in this audit. Final synthesis must also retain the distinction between local pinned-support health and any broader agreement claim.

## 18. Blocking findings

**None: 0.** No counterexample establishes that the chosen typed body is unreconstructible, that a new anchor is necessary, that kernel ownership is circular, that an accepted existing query already provides the governing fact, or that FC must evaluate an observation to be useful.

The open owner choices are real authorization gates, but not defects hidden by missing API grammar. C1 constrains a future FA authorization argument; it does not invalidate FC's core meaning or prevent starting semantic synthesis.

## 19. Required corrections

**C1 — tighten the FA reconsideration gate (one required correction).** Proposal Section 15 and its acceptance-matrix motivation permit too much weight on a consumer's desire for one combined validator. The concrete revision/constraint/candidate/snapshot substitutions can all be prevented using existing public results and explicit join checks. They do not justify FA under this audit's required cancellation standard.

In the later synthesis/owner decision, require: after FC implementation, cancel FA if FC, CN and existing evidence disclosures answer the approved question; reconsider only on a demonstrated integrity/substitution attack that cannot be prevented by explicit join checks using existing public results. State the missing property and why existing checks fail. No such property is established by this proposal or audit.

Acceptance evidence for C1 is a corrected future gate and an explicit direct-join counterexample review, not a new implementation, new fixture or edit to the frozen proposal. One combined return object, convenience presentation, size reduction or aggregate status is insufficient.

## 20. Non-blocking observations

- **N1 — edition-renewal cost:** exact VCN and support pinning can require several declarative renewals after metadata-only corrections. This is honest but operationally significant. The owner should accept the cost explicitly; do not silently implement predicate/support equivalence to reduce it.
- **N2 — support policy scope:** current/healthy/aligned typed pins are not global FL-root consensus and are not physical connectivity. Preserve that wording in synthesis and test the separate healthy conflicting-FL-root world. The current proposal does not claim global agreement, so this is a clarification obligation, not a discovered false claim.
- **N3 — reachable absence cases:** a valid FC pinning a membership-present VCN cannot have zero VCN tips in the accepted finite DAG. Keep valid lower absence, invalid closure, stale edition and conflict distinct in future tests and vocabulary.
- **N4 — single-slot scope:** several real commissioning requirements for the same S are legitimate but unsupported. Avoid calling their coexistence an engineering contradiction or using artificial contexts/orientations to encode a checklist. No checklist anchor is justified in this first version.
- **N5 — synthesis versus implementation readiness:** unfrozen API names, prefixes, field order and resource budgets are intentional and appropriate now. A later specification must close those details and measure bounded reconstruction before implementation; a favorable semantic audit is not that verification evidence.

## 21. Final recommendation

**`approve_with_corrections`: 0 blocking findings, 1 required correction, 5 non-blocking observations.** Architectural/semantic integrity passes for the FC core. Contribution to the original objectives and the named commissioning/operations consumer is useful but narrow. Effective-body pinning, exact VCN editions and two additive kernel records without a new anchor are defensible subject to the four explicit owner decisions.

Proceed to synthesis, incorporating C1's stricter FA cancellation gate and preserving the distinction between declared designation, current applicability policy and evaluation. Recommend cancellation of FA after the implemented FC query plus existing CN/evidence results demonstrates the complete approved answer. No extra evaluator is justified by the attacks examined here.

The audit wrote only this new report. The frozen proposal, all existing documentation, code, tests, fixtures, ledgers, identities, canonical artifacts and local settings remain unchanged. Branch and refs remain at the verified baseline. ADR-0022 remains absent and unallocated. No branch, commit, push, merge, rebase, reset, cherry-pick, amend, history rewrite, authoritative append or implementation was performed.

END OF FC-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
