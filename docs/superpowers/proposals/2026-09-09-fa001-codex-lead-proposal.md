# FA-001 Codex Lead Proposal

## 1. What useful question would this add?

The useful candidate question is:

> At this explicit cutoff, does the selected measurement satisfy the explicitly declared operating criterion for this logical flow at this participant port, and which exact evidence and declaration justify that answer?

**There is no new flow-assessment question answerable from the accepted baseline alone.** The repository has the measurement, relevance, compatibility, predicate-evaluation, and evidence-integrity machinery, but no approved declaration that makes a particular measurement criterion govern a particular flow claim. A result saying only that all of those inputs were admitted would not answer the question above.

Lead recommendation: **defer FA-001 implementation; first seek a separately owner-gated design for an explicit flow operating-criterion declaration, then reassess whether a new evaluator is needed.** Do not allocate a name, record prefix, identity, ADR, or implementation for that prerequisite here. If the eventual output is only a CN verdict displayed beside an FM association, use existing results and decline the new milestone.

The proposed future question is deliberately about a declared criterion at one measurement selection, not whether fluid, energy, material, or information physically flowed. Even its bounded answer is conditional on a missing premise. This document stops at that prerequisite boundary; it is a complete feasibility proposal, not an executable FA contract or authorization to fill the gap in code.

## 2. Baseline and scope of investigation

Read-only inspection confirmed:

| Item | Observed baseline |
| --- | --- |
| Branch | `main` |
| HEAD and locally stored `origin/main` | `d888ba6fbfb313cf2f85ce5cb07168fb528ec059` |
| Accepted FM runtime implementation | `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f` |
| Model membership | 36 records |
| Model revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Ledger inventory aggregate | `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a` |
| FRG/FLD/FLW | `1/1/0` |
| TRG/TRD/TRW | `0/0/0` |
| FMA/FMW | `0/0` |
| Model-kernel exports | 225 |
| ADR inventory | Contiguous ADR-0001 through ADR-0021; ADR-0022 absent |
| Initial ordinary worktree status | Clean |

No fetch or other history operation was performed; the remote-tracking reference was inspected locally. FM-001 is complete and owner accepted. Its acceptance record has SHA-256 `c3f4418c767a4df388de5e9a1124cecdb1a0c9b95d58da3a42688f15ccb49fe4`; its completion report has SHA-256 `f7ce3280a6d1af1682b6ef1139fc8d8d2166c26e56525c703029f03586d8c290`. Local settings have SHA-256 `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

There is a documentation discrepancy in the baseline: the FM synthesis's closing paragraph still describes approval of the Slice B correction as the sole pending owner gate, although its opening status and the later final acceptance record establish completion. This proposal treats the explicit final owner decision as controlling, leaves the historical document unchanged, and does not mistake that stale paragraph for authorization or for an unresolved FM semantic decision.

The only authorized output of this work is this proposal. No existing file, runtime, test, fixture, identity, record, model membership, artifact logic, or Git history is changed. ADR-0022 remains unallocated.

## 3. Original product objective: all seven questions

The mission in [CLAUDE.md](../../../CLAUDE.md) asks:

1. What exists in this system, and how is it connected?
2. What is the current state of this particular system?
3. Why might the system be behaving this way?
4. What is the next best measurement or test?
5. What would be affected if this component, parameter, or software version changed?
6. What is the smallest valid set of changes needed to reach a desired state?
7. Which conclusions are observed, calculated, inferred, assumed, or unknown?

The candidate advances question 2 only narrowly: a selected measurement's conformance to an authority-declared flow operating criterion at an explicit cutoff. It does not establish the actual current physical state. It advances question 7 by separating the captured observation, declared relevance, declared criterion, calculated predicate result, and remaining unknowns.

A missing criterion or evidence path can tell a human what prerequisite is absent, but it cannot answer question 4's word **best**. No information-gain model, uncertainty model, test costs, controllability, or optimization exists for that decision. FA must not claim progress on causality, impact prediction, planning, or control by relabelling an input refusal.

## 4. Evidence base and accepted responsibilities

This proposal is grounded in the following repository contracts, not in the suggestiveness of milestone names:

| Source | Finding used here |
| --- | --- |
| [FM final acceptance](../reports/2026-09-09-fm001-final-owner-acceptance.md), [FM synthesis](../specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md), Sections 8, 12, 13, 17, 18 | Relevance, orientation, six historical pins, indexed query disclosure, and explicit numeric/physical non-claims |
| [Kernel contracts](../../../backend/model_kernel/contracts.py): `ConstraintRegistration`, `VariableConstraintDeclaration`, `StateRegistration`, `StateDeclaration`, `FlowRegistration`, `FlowDeclaration` | Existing predicates target variables; state regions target entities; logical-flow declarations contain no measurement criterion |
| [EA README](../../../backend/evidence_assurance/README.md) | Captured scope, receipt-axis selection, seed closure, attempt coverage, observed fences, fingerprint boundaries |
| [Alignment contracts](../../../backend/evidence_alignment/contracts.py), [alignment README](../../../backend/evidence_alignment/README.md) | Whole-occurrence alignment to one public value-compatibility result; expected-fingerprint relation independent of completeness |
| [Model-state contracts](../../../backend/model_state/contracts.py), [README](../../../backend/model_state/README.md) | Latest per locator, occurrence-time identity resolution, no winning current value |
| [Observation-compatibility contracts](../../../backend/observation_compatibility/contracts.py), [README](../../../backend/observation_compatibility/README.md) | Shape, null, evidence consistency, lexical units; no engineering range assessment |
| [Semantic-compatibility contracts](../../../backend/semantic_compatibility/contracts.py), [README](../../../backend/semantic_compatibility/README.md) | Exact declared quantity/role/unit relations; unauthenticated interpretation claims and no conversion |
| [CN contracts](../../../backend/constraint_evaluation/contracts.py), [README](../../../backend/constraint_evaluation/README.md) | Exact numeric boundary evaluation already exists; `satisfied` and `violated` are predicate outcomes |
| [ST README](../../../backend/state_classification/README.md), [TA README](../../../backend/transition_assessment/README.md), [TA derivation](../../../backend/transition_assessment/derivation.py) | Explicit state conjunction and transition endpoint premises precede bounded assessment |
| [Binding contracts](../../../backend/identity_binding/contracts.py), [interpretation contracts](../../../backend/source_interpretation/contracts.py) | Carried assertion summaries and independent revisions do not amount to full source-ledger replay or authentication |

FM does not require a VSP, quantity-kind declaration, or unit as one of its six pins. Its `measured_actual` role is not a threshold or a sensor guarantee. A legal positive FM declaration may consequently be unsuitable for any numeric assessment even before the missing flow criterion is considered.

## 5. Architectural integrity versus product contribution

| Proposal | Architectural integrity | Contribution to original objective |
| --- | --- | --- |
| Pure FA wrapper over admitted FL/FM/EA/compatibility results | Can preserve dependency direction and immutable carriage | Fails: produces no new engineering answer |
| FA interprets positive numbers, sign, or zero as flow | Fails: code invents engineering meaning | Apparent progress on question 2 is misleading |
| Existing CN evaluation shown beside FM | Honest if displayed as independent results | Useful navigation, but not a new flow assessment; CN already supplies the measurement verdict |
| Explicit flow criterion prerequisite, followed by a narrowly justified composition | Potentially sound after separate approval and proof | Conditional progress on questions 2 and 7 |
| Defer while retaining current lower disclosures | Sound | No immediate new capability; avoids asserting progress that does not exist |

Architectural purity is necessary but insufficient. A no-I/O function with perfectly reconstructed inputs can still calculate an undefined proposition. The absent engineering premise cannot be replaced by more statuses, tighter fingerprints, or more exhaustive hostile-input tests.

## 6. Before and after: what actually changes?

| User question | Accepted repository today | FA using only today's meanings | After a separately accepted criterion prerequisite, if warranted |
| --- | --- | --- | --- |
| Which logical flow and participant are declared? | FL answers | No new answer | Unchanged |
| Which variable is declared relevant at the participant? | FM answers for a membership containing FMA | No new answer | Unchanged |
| Which source observation attaches to the variable at cutoff? | Model state and binding answer per candidate | No new answer | Unchanged |
| Are captured evidence and occurrence alignment admissible? | EA and alignment answer | No new answer | Unchanged |
| Does the numeric observation satisfy this declared variable predicate? | CN answers | No new answer | Reuse CN |
| Which criterion is declared to govern this flow/participant/context, and does its selected measurement satisfy it? | No explicit governing relation exists | Must withhold | Conditional new flow-scoped criterion answer |
| Did physical flow occur or persist? | Not established by these layers | Must withhold | Still withheld |

The proposed new information is the result of applying an explicit **flow-scoped governing criterion**, with a trace identifying why that criterion and evidence apply. It is not merely a renamed CN verdict. If the owner only wants a convenience join without additional governing meaning, the correct outcome is a display of existing results, not FA-001 as an engineering milestone.

## 7. Central missing premise and non-identifiability proof

Let the complete accepted input bundle be E. It contains a healthy FM association, healthy FL declaration, aligned measured-actual semantics, an attached numeric observation of `3.2`, complete EA evidence, a matched expected fingerprint, and, even if desired, a CN interval predicate satisfied by `3.2`.

Consider two engineering interpretations compatible with exactly E:

- Under one interpretation, that reading meets a process operating criterion at this participant.
- Under another, the variable is only relevant diagnostic context and cannot decide any operating criterion. For example, a pressure reading may be compatible with a blocked path as well as a flowing path.

The accepted contracts choose neither interpretation. Even an existing VCN targeting that variable says nothing about whether its satisfaction governs this flow. Thus a deterministic function of E cannot select a flow conclusion without introducing an additional premise. Distinguishing the two cases requires a declared relation, not an algorithmic guess.

The same issue applies to nonnumeric values. Boolean `true`, string `running`, or a valid nullable specification has no accepted mapping to a flow proposition. Names, notes, display labels, adapter routes, apparent unit spelling, and physical intuition cannot supply that mapping.

## 8. Missing-contract discrepancy register and stopping point

These labels identify design discrepancies, not proposed public error codes.

| Gap | Existing evidence | Missing decision or contract | Consequence |
| --- | --- | --- | --- |
| G1: governing relation | FM relates variable to flow; CRG relates constraint to variable | Which exact criterion governs which flow, participant, context, and FM subject, and what satisfaction means | Blocks any new flow-assessment contract |
| G2: measurement interpretation | VSM measured-actual and orientation token | Threshold/deadband/zero/sign/nonnumeric mapping when needed; no implicit active-flow interpretation | Blocks direction/activity/flow-occurrence conclusions |
| G3: temporal sufficiency | EA horizon and latest selection; VM receipt age | Whether a selected sample is adequate for the specific claim; freshness, cadence, continuity, or uncertainty rule if claimed | Blocks current physical state and interval claims |
| G4: evidence choice and disagreement | Independent locator candidates and multiple FM roots | Whether one nominated candidate, all candidates, or a declared combination governs; disagreement policy | Blocks implicit winning-source or whole-flow aggregate |
| G5: proof strength | Public reconstructed results, EA fingerprint, carried binding/interpretation summaries | Whether structural carried-result trust suffices or full declaration-ledger closure/authentication is required | Additional lower contract only if stronger proof is demanded |
| G6: global carry-once interpretation | CN and alignment embed overlapping VS results | Whole public objects with equality checks versus a new shared-material representation | Prevents a false promise of globally deduplicated carriage |

G1 is a hard prerequisite even for the narrow question in Section 1. G2–G4 can be reduced by choosing a single numeric sample and a literal criterion-conformance claim, but they cannot be silently decided in an evaluator. G5 and G6 are integrity design choices, not ways to manufacture engineering meaning.

**Stop here for runtime design.** No FA request/result classes, public statuses, reason literals, exception vocabulary, record kinds, minters, or runtime package are allocated by this proposal. Exact API and numeric admission budgets are intentionally not frozen because no viable baseline-only assessment has been demonstrated. This is the nonviable branch of the requested feasibility analysis, not an incomplete implementation specification.

The remaining sections provide the complete rationale, conditional usefulness witness, constraints on reconsideration, and owner decisions. They do not fill G1 on the owner's behalf.

## 9. What an explicit prerequisite would have to declare

The smallest candidate premise is an authority-declared operating criterion governing one exact flow/participant/context and one FM association subject, tied to one existing variable constraint. Reuse the accepted numeric predicate machinery rather than inventing another decimal evaluator.

The prerequisite design must settle the following semantic content before choosing fields or record grammar:

- Exact governed locus and context, including whether it selects one assertion, root, or effective body; broad variable or flow ID matching is insufficient.
- Exact governing constraint declaration and semantic signature; selecting any VCN that happens to target the variable is not permitted.
- The meaning of a positive and negative answer: only criterion conformance unless separately justified, never an automatic active/no-flow assertion.
- Whether the criterion is applied to the original measured value, a transformed value, or a code. Recommend original numeric value only in a first slice; transformations and codebooks need additional contracts.
- Evidence-selection basis, treatment of age and coverage, and whether a single nominated locator is the entire claim's scope.
- Lifecycle, correction, withdrawal, evidence citation, and what stale pins mean. Historical evaluation and present-applicability evaluation must not be conflated.

These are premise requirements, not proposed public fields. Each either determines the new engineering question or provides the integrity needed to trust its answer. An `all_inputs_ok`, confidence number, generic health field, or redundant copy of every lower status has neither justification.

Recommendation for the prerequisite's eventual owner is the existing model-kernel declaration boundary, because this is model meaning. That would require separately approved lower contract work and preservation design. It must not be smuggled into an FA request as a free-form instruction or hidden configuration. A caller-supplied policy could support a hypothetical-policy calculator, but that would be a different product claim needing explicit approval.

## 10. Trace from a possible future conclusion to its premises

The following trace describes the conditional criterion-conformance answer. Every edge is mandatory; G1 is visibly missing at baseline.

| Step | Required trace | Accepted owner and limitation |
| --- | --- | --- |
| 1 | Exact source/property/endpoint scope, captured source and temporal material, retained expected snapshot fingerprint | EA; captured fences are not a distributed transaction or authentication |
| 2 | Complete selected `TemporalOccurrence`, attempt membership and coverage, receipt cutoff and horizon | Temporal/EA; seed does not prove earlier continuity and absence is not zero |
| 3 | Whole selected occurrence matches exactly one compatibility candidate, at the same normalized cutoff and six-field locator | Evidence alignment; equal value or occurrence ID alone is insufficient |
| 4 | That candidate's binding resolution targets the exact variable with attachment admitted at its own `received_at` | Identity binding/model state; revisions and embedded anchors must agree |
| 5 | Value is present and consistent, shape is appropriate, VSP and requested variable belong to the selected model revision | Observation compatibility; null may be shape-compatible without supplying a number |
| 6 | Model and source quantity, measured-actual role, and unit identities match under the carried interpretation revision | Semantic compatibility; exact tokens are declarations, not calibration or SI traceability |
| 7 | Exact pinned VCN's predicate is evaluated for that same candidate, numeric value and expected semantic signature | CN; `satisfied` is already a lower conclusion, not flow support |
| 8 | Selected logical flow, exact-context FLD and its structural pins, and participant role are admitted | FL; port groups and declared direction are logical model facts |
| 9 | Exact FM subject and chosen body connect that variable, flow, port, context and orientation; six pins close in the same material | FM; present activity/health/alignment must be disclosed, not retargeted |
| 10 | Authority declares that this exact criterion governs this exact flow-scoped question | G1: no accepted representation or public query exists |
| 11 | Derive criterion conformance and its precise trace under the declared evaluation basis | Only reconsider after Step 10 exists; no physical-occurrence inference |

FM pin closure must independently establish:

| Pin | Required identity/relation |
| --- | --- |
| FRG | Selected flow registration and participant membership; derived source/sink role |
| VRG | Exact measured variable registration |
| PRG | Exact participant port registration |
| FLD | Same flow and context, correct participant direction support, and its accepted PCN/PIF closure |
| VPA | Same variable, port, and context |
| VSM | Same variable and exact context-independent `measured_actual` role token |

A CN semantic result must match the selected FM variable and the governing role; a merely equal value from another candidate is insufficient. Same model revision must be proven across kernel-dependent results. Binding and source-interpretation revisions remain distinct provenance domains, not equalized to a model revision or to one another.

## 11. Nine meanings that must remain distinct

| Meaning | What establishes it today | Permitted treatment by baseline-only FA | Conditional criterion slice |
| --- | --- | --- | --- |
| Evidence availability | Captured occurrence and lower availability results | Carry existing disclosure | Necessary evidence fact |
| Measurement relevance | FM declaration and its lifecycle | Carry existing disclosure | Necessary model premise |
| Semantic compatibility | ES exact declared token relations | Carry existing disclosure | Necessary meaning relation |
| Measurement assessment | CN numeric predicate evaluation | Already available from CN | Reuse exactly |
| Declared-flow support | No accepted measurement-to-flow criterion implication | Withhold | Only conformance to a separately declared criterion; label accordingly |
| Physical flow occurrence | No approved rule in these contracts | Prohibited | Prohibited |
| Continuity | No time-window/cadence/interpolation rule | Prohibited | Prohibited |
| Conservation | No physical boundary, accumulation, synchronization or dimensional algebra contract | Prohibited | Prohibited |
| Causality | No causal model or intervention contract | Prohibited | Prohibited |

No proposed FA can currently promote the first four rows into the fifth. A criterion-conformance result would not license promotion into the final four. Correctness and safety remain outside all positive conclusions here.

## 12. Alternatives and recommendation

| Alternative | Benefit | Cost or failure | Decision |
| --- | --- | --- | --- |
| A. Do nothing/defer FA | Preserves honest boundaries; current CN/FM remain usable | No new flow criterion answer | Recommended immediate action |
| B. Read-only joined measurement-relevance disclosure, possibly renamed | Makes existing facts easier to navigate | Fails the requested new-engineering-question test; baseline zero-FMA means no positive authoritative view | Consider only as a separately requested presentation task |
| C. Pure FA using sign, nonzero, or any nearby satisfied constraint | Superficially simple | Invents meaning; ambiguous sources and stale supports become hidden policy | Reject |
| D. Explicit governing criterion prerequisite, then narrow composition | Supplies the missing premise and may advance objectives 2 and 7 | Requires a new approved lower declaration contract and another usefulness review | Recommended direction for an owner decision |
| E. Generic caller-supplied policy calculator | Could answer hypothetical numeric policies without a durable model record | Duplicates CN unless it adds a real governing relation; assumption becomes caller policy, not accepted model knowledge | Not the default; requires renamed claim and separate approval |
| F. Full physical-flow assessment with rate integration, continuity and conservation | Potentially much larger engineering value | Missing temporal, physical-boundary, uncertainty and unit contracts; no smallest slice | Defer |

Option D is not permission to launch another milestone automatically. First decide whether its declared operating-criterion question matters enough to justify new model meaning. If direct CN evaluation with explicit human interpretation already satisfies the intended workflow, stop at A or B.

## 13. Smallest potentially useful vertical slice

The candidate for reconsideration is one explicitly selected flow participant, one exact FM subject/body, one numeric measured-actual variable, one exact governing VCN, one nominated source/property candidate, and one receipt-axis cutoff. All declared identities must match exactly. No source ranking, aggregation, sign transform, unit conversion, automatic source/sink balancing, or physical-event inference is needed.

Its only potential answer is conformance/nonconformance to that exact declared criterion, or inability to evaluate with a precise missing premise. Do not label the answer `flowing`, `not_flowing`, `flow_ok`, `safe`, or even generic `flow_supported`.

Initially restrict the candidate to a raw-value numeric criterion and a declared evaluation basis that does not claim physical freshness. Whether a stricter age bound is needed is an owner decision; no numeric age limit is selected here. If the intended user question requires present physical state, this slice is insufficient and should be rejected rather than oversold.

The benefit must survive removing the name FA-001 from the interface. A user must be able to identify which declared criterion was evaluated for which flow locus and what changed in the evidence, not merely see a collection of green lower statuses.

## 14. Decision-usefulness test and its present impossibility

There is **no valid baseline-only positive FA witness** for Section 1: the required governing declaration is absent from the accepted contract, not merely absent from today's ledger. That is the reason to stop. It would be dishonest to present the following thought experiment as an executable accepted-world test.

Conditional example after separate premise approval: an authority explicitly declares that a measured pressure variable at a nominated logical-flow participant must satisfy an inclusive interval `2` to `4` in one exact declared unit identity for a named commissioning criterion. This is a fictional process criterion, not a claim that pressure implies transport. Use the existing measured-actual role and CN interval machinery; no new rate or cumulative role is implied.

At cutoff T, one nominated sample is `3.2`, its EA expected fingerprint matches, coverage satisfies the separately approved rule, attachment and semantic identity agree, the exact CN predicate is satisfied, and all governing model pins are admitted. The conditional output says this **declared flow operating criterion is met by this selected sample**. A comparable sample of `4.7` yields not met. Neither answer says flow occurred.

This changes what a human may legitimately do: record that this specific evidence satisfies that specific commissioning criterion, or leave that criterion open with the boundary violation identified. A later bounded conjunction could count that criterion as satisfied only if its own approved rule permits it. Neither result authorizes machine operation, declares commissioning complete, or recommends an intervention.

Without G1, CN already says `3.2` satisfies an interval. A human can interpret that independently, but software cannot assert which flow criterion was discharged. The new information therefore depends on the explicit governing premise. If the owner finds this distinction too small to justify another contract, defer FA rather than inventing a stronger conclusion.

## 15. Contract-theatre test

Implementing `admitted`, `aligned`, `relevant`, `complete`, and `supported` would fail this test if `supported` is merely their conjunction. For every proposed result, remove the echoed lower statuses and ask what new engineering proposition remains. At the baseline, none remains.

Three rejection probes are mandatory before any implementation approval:

1. **Criterion-removal probe:** delete the governing flow criterion while keeping all lower admissions positive. The new engineering conclusion must disappear. If it does not, the implementation invented the premise.
2. **Value-change probe:** hold identity, meaning, relevance, and evidence admission fixed; replace one fully valid captured world with another on the opposite side of the declared predicate. The criterion outcome must change. This tests a fresh valid world, not a forged fingerprint mutation.
3. **Lower-equivalence probe:** if the complete user answer is already a CN result plus an FM label and no approved new relation is needed, do not claim an FA capability gain.

The second probe alone is insufficient: CN already passes it. Both the new declared flow-scoped premise and a useful downstream interpretation must be demonstrated.

## 16. Misleading-success tests

Each example permits lower results to be structurally valid. Where described as fully admitted, it also permits every relevant positive lower admission. The flow conclusion must still be withheld.

| Case | Why lower success is possible | Why flow conclusion is unavailable |
| --- | --- | --- |
| Healthy FM, compatible attached measurement, complete fingerprint-matched EA, but no flow criterion | All existing contracts can be satisfied without G1 | Relevance supplies no assessment rule |
| Same bundle plus a satisfied VCN on the FM variable | CN does not require a flow relation | Arbitrary variable predicate is not a flow criterion |
| Numeric zero with satisfied `0 <= x <= 4` | Zero is an ordinary admitted numeric value | Zero may be within deadband, offset, absence of signal, or a valid operating reading; no approved no-flow rule |
| Negative value with FM `opposite` | FM records orientation without evaluating a sign | Neither multiplication by minus one nor reverse physical flow is licensed |
| Old but latest eligible occurrence under complete declared evidence | Complete EA evidence is not a freshness judgement | Current physical flow cannot be inferred from selection alone |
| Two independently complete scopes with equal cutoffs | Both snapshots can align successfully | Equal cutoffs do not establish simultaneous acquisition or conservation |
| Pressure above a hypothetical limit while the path is blocked | Measurement, tokens and relevance may all be admitted | Such a value is not proof of physical movement |
| All-source semantic declarations agree but the sensor is biased | ES agrees declared identities, not calibration | No uncertainty, correctness or safety guarantee follows |

Additional valid-but-nonpositive lower worlds include explicit null, missing numeric semantics, conflicted FM roots, withdrawn pins and incomplete evidence. They must remain unevaluated for a criterion claim, not be turned into failed physical flow.

## 17. Multiplicity, lifecycle and difficult observations

These are conservative constraints on a future first slice, not approved defaults or new runtime reason literals.

| Situation | Required disposition or owner decision |
| --- | --- |
| Several FM subjects for one flow | Select the exact governing locus/subject explicitly; no whole-flow summary from an arbitrary member |
| Independent healthy roots with identical body | Preserve corroboration; whether a governing declaration pins a record or body must be explicit |
| Conflicting roots or cross-root body disagreement | No winning authority or minimum-ID choice; withhold the single-criterion evaluation unless a later declared policy resolves scope |
| Inactive association | Keep historical disclosure; no present governing relevance; historical assessment requires its own selected revision and explicit claim |
| Superseded/withdrawn FLD or VPA pin, or changed VSM support | FM can validly disclose stale/unaligned support; current alignment is not exact-pin currentness; do not silently repin |
| Several observations/locators | No latest across unrelated sources, averaging, or matching-by-value; nominate an exact candidate under the criterion's approved scope |
| Source disagreement | A per-source answer must disclose its limited scope; no consensus or authoritative winner; if agreement is required, the current slice cannot decide |
| Missing attempt coverage or refused EA selection | Preserve absence/integrity distinction; never convert missing evidence into numeric zero or predicate falsity |
| Pre-horizon seed | Full mechanical closure is possible but does not supply within-window continuity or a fresh physical measurement |
| Mixed acquisition cohorts | Single-sample scope avoids an aggregate; any multisample relation requires declared cohort/independence semantics |
| Clock domains | Normalize receipt cutoffs as accepted; do not compare uptime/source clocks as physical time or assume synchronization |
| Different cutoffs or model revisions | Do not merge; an explicit model revision is knowledge selection, not selected automatically by `as_of` |
| Unit differences | Exact unit identity only for the narrow candidate; no equivalence, scaling, dimensional inference or conversion |
| `aligned` or `opposite` orientation | Trace the declared token; no numeric transform without its own approved meaning |
| `unsigned_magnitude` | Could govern a raw magnitude criterion after explicit approval; provides no sign or direction conclusion |
| `not_applicable` | No directional interpretation; may be relevant to a separately defined non-directional criterion |
| Sign and zero | Apply only the explicitly declared numeric predicate; no positive-means-flow convention or inferred deadband |
| Explicit null | Even if nullable VSP admits it, CN supplies no numeric value; withhold numeric criterion evaluation |
| Boolean, string, array or object | Shape admission is not a numeric criterion; require a separately declared nonnumeric predicate/codebook, outside the first slice |
| Numeric overflow, hostile lexical value, inconsistent JSON type | Reuse lower bounded numeric refusal and integrity distinctions; do not round, coerce or repair |
| Sensor uncertainty or disagreement with physical expectations | No inferred confidence margin; owner must add an explicit uncertainty premise before uncertainty-aware judgement |

## 18. Consumption, ownership and proof boundaries

A future evaluator, if approved, should be a pure upper leaf consuming public carried model-kernel FM/FL results, CN results, and evidence-alignment results. The candidate responsibility could live in a flow-assessment package, but no package name is allocated as a public contract in this stopped proposal. Dependencies would point downward; no lower package imports FA and no FA code reads stores, connectors, source readers, clocks, configuration, or environment.

FA should consume public CN evaluation rather than importing its private decimal helper or reimplementing predicate evaluation. It should compare alignment's carried `VariableValueCompatibilityResult` with the CN/ES embedded value-compatibility material, including the full selected occurrence and index path. A matched fingerprint must have been independently retained by the caller; copying the snapshot's own fingerprint into a request proves no independent commitment.

Existing public carried results are sufficient for many relational checks but do not solve G1. A new lower declaration contract is necessary for the recommended direction. Stronger source/binding/interpretation authentication is not automatically necessary for an explicitly limited structural result; if the owner demands authoritative replay of every binding or interpretation decision, the existing carried summaries are not complete ledgers. That requirement would need another public material contract, never private store access.

Reconstructing Pydantic objects must not be described as authenticating the source or proving that carried declarations are true. FM material supports full model-ledger reconstruction; EA supports canonical snapshot verification without raw-payload reread; binding and interpretation carry their own limited evidence. The future result must preserve these unequal proof strengths.

## 19. Carry-once, cutoffs, reconstruction and bounds

These are feasibility constraints for a later design, not an exact proposed FA schema.

**Carry-once:** carry the future request once in its result; derived trace rows use indices into request-owned inputs. Do not add separate copies of records, units, values, or lower statuses for symmetry. However, intact CN and alignment results each already embed a value-compatibility result. Logical input ownership once is feasible; global physical deduplication of all nested lower material is not feasible through those intact public contracts. Compare overlapping content authoritatively; do not strip fields or substitute a private reference envelope. A requirement for global deduplication would trigger a separately approved lower public contract.

**Cutoff:** use an explicit aware normalized UTC receipt cutoff; all governing lower results must agree. Horizons remain explicit and independent of the selected model revision. Source time is disclosure only. Missing, incomplete and pre-horizon evidence retain accepted distinctions. A proposed complete-evidence gate is conservative eligibility, not cadence, freshness or occurrence proof; the owner must approve its adequacy for the chosen criterion.

**Reconstruction:** preflight the entire supplied graph before nested validation or callbacks; rebuild plain content through public lower validators; require exact subjects, model membership, cutoffs, candidate paths and expected-fingerprint relations; derive only the new declared relation and criterion conclusion. No filesystem, store validation, reselection, ambient clock or result persistence is allowed. Forged conclusions and row indices must fail reconstruction.

**Ordering:** one criterion/candidate requires no ranking. Any permitted diagnostic rows need declared literal order and semantic keys, with contiguous strict nonboolean indices after ordering. Input order, dict order, filenames, timestamps and hash seed cannot select a winner.

**Bounds:** no numeric FA limit is justified until the premise and carriage shape are settled. The existing TA ceiling of 134,217,728 canonical bytes, 200,000 expanded nodes and depth 128 is precedent, not a free FA default. A later contract must specify aggregate byte/node/depth/cardinality limits before expansion, handling of shared DAGs and cycles, per-string limits, exact finite-float handling inherited from lower models, and predictable overflow errors. It must measure a smallest valid witness and reject just-over-bound inputs without allocating them fully. Guessing a copied budget now would conceal an unresolved contract.

## 20. Conditional decision table and refusal semantics

This table defines reasoning obligations, not public status/reason vocabulary. No runtime result is proposed while G1 remains missing.

| Inputs | Honest outcome |
| --- | --- |
| Malformed/forged supplied content, invalid indices, cycles, over-budget representation | Typed malformed-input failure under a future approved error contract; no engineering negative |
| Well-formed lower results, missing governing flow criterion | Assessment undefined; prerequisite must be declared |
| Governing criterion exists but applicability/identity/evidence/semantic gate is not established | Cannot evaluate the declared criterion; disclose exact gate without calling the criterion false |
| Exact criterion and all approved gates, CN numeric predicate satisfied for the nominated candidate | That declared criterion is met by that selected sample |
| Exact criterion and all approved gates, CN numeric predicate violated | That declared criterion is not met by that selected sample |
| Any row above followed by a question about occurrence, continuity, conservation or causality | Withhold that stronger conclusion |

Negative-result semantics must be predicate falsity only. Source refusal, incomplete evidence, absent association, null value, conflict and uncertain applicability must never become negative flow evidence. A public vocabulary, field order, null cardinality, reason precedence, and exception type must be specified only after the owner accepts an actual criterion contract.

## 21. Threat model and adversarial acceptance obligations

The most dangerous attack is semantic: valid lower facts are presented as proof of an undeclared flow proposition. Other threats include cherry-picking sources, stale-pin laundering, replacing snapshot plus fingerprint coherently, cross-revision or cross-context substitution, concealing duplicate associations, hostile model subclasses/callbacks, cyclic or exponentially expanded graphs, and using source clock values as common wall time.

The following is a **design acceptance matrix**. It allocates no test file or runtime code. The baseline fails the positive-premise gate intentionally.

| ID | Required challenge | Acceptance evidence |
| --- | --- | --- |
| FA-D01 | All lower gates positive with G1 absent | No flow criterion conclusion; implementation proposal stops |
| FA-D02 | Satisfied VCN on the same variable but no governing relation | CN result retained; no invented flow relevance of that predicate |
| FA-D03 | Conditional valid worlds `3.2` and `4.7` under an approved interval criterion | New flow-scoped criterion outcome changes, with identical admission meaning |
| FA-D04 | Same measurement with different or absent governing declaration | Correct scoped outcome or withholding; no hidden global rule |
| FA-D05 | Substituted flow/port/variable/context/orientation | Exact mismatch detected before conclusion |
| FA-D06 | Each of the six FM pins substituted, stale, inactive or conflicted | Exact lifecycle/applicability policy followed; no silent retargeting |
| FA-D07 | Same-body corroboration, same-root fork, cross-root disagreement | Complete disclosure, no ID/authority winner |
| FA-D08 | Multiple candidates, duplicate subjects, disagreeing sources | No implicit ranking, voting, averaging or match-by-value |
| FA-D09 | Missing coverage, pre-horizon seed, selection refused | No fabricated negative, zero, continuity or freshness |
| FA-D10 | Equal values but different occurrence content or scope | Alignment relation withheld; complete occurrence identity required |
| FA-D11 | Missing or mismatched independent fingerprint | No trusted assessment admission; self-supplied embedded hash is insufficient |
| FA-D12 | Equal cutoff but different cohorts/source clocks | No simultaneity, interval or conservation claim |
| FA-D13 | Null, nonnumeric, signed zero, negative value, differing units | Accepted predicate semantics only; no coercion, sign transformation or conversion |
| FA-D14 | Forged model instances, private state, scalars, booleans as indices | Typed refusal before arbitrary callbacks or derivation |
| FA-D15 | Cycles, shared-DAG amplification, exact-bound and over-bound requests | Bounded deterministic admission measured against valid witnesses |
| FA-D16 | Reordered input and at least five hash seeds | Canonically equal results and complete ordered traces |
| FA-D17 | Filesystem/network/store/clock/environment spies | Zero access during pure assessment and reconstruction |
| FA-D18 | Coherently replaced binding/interpretation summaries | No claim stronger than their actual carried-material proof boundary |
| FA-D19 | Existing 36-record membership with FMA/FMW zero | Structured absence only; no authoritative append or inferred FMA |
| FA-D20 | All statuses implemented but no useful new proposition | Reject milestone as contract theatre |
| FA-D21 | Proposal or demo claims physical flow from predicate success | Reject as misleading success |
| FA-D22 | Every proposed public field audited | Each justified by new criterion disclosure or necessary integrity; redundant fields removed |

## 22. Zero-FMA model, demonstration and verification strategy

Today's authoritative model cannot produce a positive FM-based assessment because it has zero FMA records. More fundamentally, adding a disposable FMA alone would not close G1. Do not transform a positive test-world association into a claim about the committed printer model.

Disposable worlds are sufficient to prove contract behavior and the bounded computational contribution, provided a separately approved prerequisite exists and the two-sided criterion example is reproducible through public APIs. They are not sufficient evidence of real-machine benefit, calibration or physical flow.

Recommendation: require a clearly labelled, disposable worked example as part of a later implementation acceptance test, but **do not require an authoritative synthetic demonstration or ledger append**. If the owner wants a shipped demonstration over the authoritative model, it needs a separate proposal, identities/records approval and preservation gate. No such demonstration is created or authorized here.

A future verified slice would require focused predicate/relation tests, affected lower consumers, no-I/O/import checks, full repository and fresh base/extras runs, deterministic order/seed evidence, canonical reconstruction and protected-artifact checks. This proposal did not repeat runtime suites because it changes no runtime or tests. Its verification is baseline inspection, source-contract analysis, proposal link/marker/section checks, and proof that this is the only new file.

## 23. Separately owner-gated path and unresolved decisions

No implementation slice is authorized by this proposal. The recommended sequence is:

1. **Product decision gate:** accept or reject the exact Section 1 question and its limited contribution. If the desired outcome is physical flow/activity, stop and scope the missing physical/temporal contracts instead.
2. **Prerequisite design gate:** define the governing criterion declaration, exact subject/pins, lifecycle, evidence basis and strongest meaning. Allocate no ADR or identity in this proposal.
3. **Prerequisite implementation gate, only after separate approval:** add only the approved lower declaration/read contract, with its own review and verification. Whether it needs records is decided in that contract, not pre-authorized here.
4. **FA viability gate:** repeat the contract-theatre and decision-usefulness tests against the new accepted baseline. Decide whether existing CN plus a direct declared-relation query suffices; cancel FA if it does.
5. **Narrow evaluator gate, only if justified:** write the exact public API, field justifications, input ownership, decision/error tables and numeric limits before implementation. Then implement the smallest pure carried-result slice and its disposable worked example under separate authorization.
6. **Optional demonstration gate:** only if independently requested; never automatic after evaluator acceptance.

Owner decisions still open:

- O1: Is selected-sample conformance to a declared flow operating criterion valuable enough, or is the target actual physical flow?
- O2: Authorize a separate prerequisite design, use a presentation-only join, or defer without further work?
- O3: If pursuing the prerequisite, is one governing constraint tied to an exact FM record/body the right model meaning, and how is lifecycle applicability defined?
- O4: Is one nominated source/candidate sufficient, or is source agreement/temporal coverage/freshness/uncertainty part of the desired claim? Stronger requirements expand prerequisites.
- O5: Accept the existing public carried-result proof boundary and repeated nested lower material, or require stronger replay/deduplication contracts?
- O6: Is a disposable worked example sufficient for software acceptance, or is a separately gated authoritative/real-system demonstration required?

Defaults recommended for reconsideration are one numeric criterion and candidate, public carried results only, no evaluator identity or store, and disposable verification. These recommendations are explicitly not frozen engineering premises.

## 24. Gap-closure matrix and remaining product gaps

| Original question | Proposed baseline-only FA | Conditional criterion contribution | Gap still open afterward |
| --- | --- | --- | --- |
| 1. What exists and how is it connected? | No new model fact | Makes an explicitly declared flow criterion discoverable if the prerequisite adds it | Physical topology validation and as-built truth |
| 2. What is the current state? | No justified new flow state | Selected measurement meets/does not meet a declared flow criterion at a cutoff | Actual current physical flow, freshness, configuration and continuous state |
| 3. Why is it behaving this way? | None | No causal explanation; trace explains the computation only | Causal model, diagnosis and competing explanations |
| 4. Next best measurement/test? | None | Human sees a missing premise or unmet criterion; no optimal recommendation | Uncertainty, discriminating tests, costs, information gain |
| 5. What would be affected by change? | None | Explicit criterion dependencies become inspectable | Propagation semantics, counterfactuals and impact assessment |
| 6. Smallest valid change set? | None | None; predicate evaluation does not select actions | Goals, action effects, constraints across plans, optimization and control |
| 7. Observed/calculated/inferred/assumed/unknown? | Lower provenance already exists | New criterion claim has an explicit chain from observation through declared premises to calculated conformance | Authentication, calibrated uncertainty, comprehensive epistemic model and physical validation |

Even after the conditional slice, open gaps include flow occurrence/non-occurrence, continuity, rates/integration, accumulation and conservation, physical boundaries, unit conversion and dimensional algebra, sensor uncertainty, source authenticity, clock synchronization, source disagreement policies, causal explanation, impact propagation, planning, safety and correctness. The named `measured_actual` role remains a declaration; it does not certify any of those properties.

Final lead decision: the current baseline can support excellent lower-layer disclosures and numeric predicate assessments, but cannot support a genuinely new bounded flow conclusion. Defer FA-001 runtime work, leave ADR-0022 absent, and present the missing governing declaration and the product-value decision to the owner. No successor work follows automatically from this proposal.

END OF FA-001 CODEX LEAD PROPOSAL
