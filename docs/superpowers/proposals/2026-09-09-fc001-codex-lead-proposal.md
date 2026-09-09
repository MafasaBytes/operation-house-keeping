# FC-001 — Explicit Flow Operating Criterion Declaration: Codex Lead Proposal

## 1. Answer and lead recommendation

An authority can declare: **one exact existing variable-constraint declaration governs the original measured value for one exact logical-flow measurement meaning, at its exact participant port and context**. This establishes declared applicability, not a predicate verdict or an observation about the system.

Recommend an additive, evidence-bearing declaration and an uncitable withdrawal in `backend.model_kernel`, with no new durable anchor. Govern an **exact FM effective body**, not an arbitrary assertion's lineage and not the FM subject across all future support changes. Identify that body through an explicitly nominated, membership-present FMA witness; pin the exact CRG and VCN separately. The witness is immutable provenance and a body selector, not a privileged FM authority or a requirement that its particular lineage remain active.

The first consumer is the owner-approved **commissioning/operations verification workflow**. FC alone answers a genuinely new question: “Which exact criterion is authority-declared to govern this exact flow-measurement meaning in this selected model membership?” Evaluation stays in CN. Prefer no subsequent FA evaluator if the FC query and existing CN/evidence disclosures supply the complete answer; reassess only after FC acceptance and implementation.

This is a proposed semantic design, not an accepted contract or implementation authorization. No record prefixes, public class/function names, serialized field order, identities, ADR number, or implementation slices are allocated. Necessity and package ownership are established below; owner review of the consequential lifecycle choices still precedes API freezing.

## 2. Baseline, accepted decisions, and investigation method

Starting branch `main`, HEAD and locally stored `origin/main` were `d888ba6fbfb313cf2f85ce5cb07168fb528ec059`. Phase 1 created exactly one documentation-only commit, `c0e1c8fe930e10243fec16a4950a3d34d4c85df4`, accepting the FA investigation and authorizing this design. This commit is the FC proposal's administrative baseline; `origin/main` remains unchanged. No fetch was performed.

The [FA owner decision](../reports/2026-09-09-fa001-feasibility-owner-decision.md) has SHA-256 `a65761f26d1c646a41a5af10fb8b4af10aa04d72ef5263f7fe04d4fa16f6290a`. The frozen [FA proposal](2026-09-09-fa001-codex-lead-proposal.md) remains `c818e4e342bd9450c5e1d19513bae336097f7601648ef1a8f73232e490d37c17`; the frozen [challenger audit](../reports/2026-09-09-fa001-codex-lead-proposal-challenger-audit.md) remains `65114fcc03cbe07a90cfceb349bea1ea7dba2c3f21f67f835cb100c76b062980`, including its CRLF bytes. The closeout record documents the resulting default staged-whitespace exception; this proposal uses LF.

FM-001 remains complete and accepted at tested implementation `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`. The authoritative model remains 36 records at `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`, inventory aggregate `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`. FRG/FLD/FLW are `1/1/0`, TRG/TRD/TRW `0/0/0`, FMA/FMW `0/0`. The kernel surface remains 225 names. ADRs remain contiguous through ADR-0021; ADR-0022 is absent and unallocated.

Inspection used actual contracts, reducers, query construction and carried-result validators, not merely the G1 label. The repository brainstorming skill informed alternatives and self-review; the owner's specific artifact, commit and design-only instructions control the workflow. No code, tests or example worlds were created for this investigation.

## 3. Approved question and initial consumer

The owner has approved this question and its value:

> At this explicit receipt cutoff, does one nominated measured-actual sample satisfy the authority-declared operating criterion governing one exact logical-flow participant and context, and what evidence and declarations justify the result?

For commissioning/operations verification, a human needs to know which declared check is applicable before recording a sample's predicate outcome against that check. A constraint on a relevant variable is not automatically the commissioned criterion. FC supplies that missing normative association; CN supplies numeric evaluation, and the accepted evidence layers supply provenance and alignment.

The first scope is one criterion and one nominated candidate. Source agreement, freshness policy, uncertainty, continuity, aggregation and physical-flow occurrence are explicitly excluded, not unresolved defaults. Keep the existing public carried-result proof boundary. Disposable worked examples suffice for software verification. These owner decisions are settled and are not re-opened as questions below.

FC has no receipt cutoff, sample, source ranking or observation input. Its selected model membership is explicit knowledge selection, not a model state inferred from the measurement's receipt time. The receipt cutoff belongs to independently supplied CN and evidence results.

## 4. Repository findings: what is and is not already declared

| Inspected source | Relevant accepted contract |
| --- | --- |
| [Kernel contracts](../../../backend/model_kernel/contracts.py): `ConstraintRegistration`, `VariableConstraintDeclaration` | CRG permanently assigns a ConstraintAnchor to one VariableAnchor. VCN corrects the numeric predicate and expected quantity/role/unit signature; its lineage key is the constraint anchor. Neither identifies a flow locus or context. |
| Same file: `RelationshipTypeDefinition`, `RelationshipAssertion` | Generic directed relationship assertions have entity-anchor endpoints; no typed FMA/VCN record endpoints or governing-criterion support closure. A type label cannot add those semantics. |
| Same file: `FlowMeasurementAssociation`; [FM design Sections 10–15](../specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md) | FM freezes flow, variable, participant, context, direct-measurement relevance and orientation as its subject. Effective body adds six exact support IDs. Evidence/authority/time/ancestry do not define body equality. |
| [Kernel store](../../../backend/model_kernel/store.py): `validate_record_collection`, `_pt_dag_indexes` | Selected-membership validation, same-root correction, immutable indexes, evidence closure, and membership-relative withdrawals are established patterns. Private helpers are evidence for design, not upper-layer import APIs. |
| [FM result contracts](../../../backend/model_kernel/flow_measurement_results.py), [query facade](../../../backend/model_kernel/queries.py) | Exact/reverse/assertion lookup already separates root health, current activity, body agreement and support alignment. A representative row index is not a winning authority. |
| [CN contracts](../../../backend/constraint_evaluation/contracts.py), [CN README](../../../backend/constraint_evaluation/README.md) | CN carries the exact constraint result and ES, evaluates candidate rows, and reconstructs them. It does not select which predicate governs a flow. It evaluates the current VCN of the selected membership, not an arbitrary historical VCN within it. |
| [Model material](../../../backend/model_kernel/port_results.py): `ModelQueryMaterial`; [result reconstruction](../../../backend/model_kernel/result_revalidation.py) | One carried full selected membership supports pure reconstruction without store access; indexes are derived, not authority. |
| [Alignment contracts](../../../backend/evidence_alignment/contracts.py), [EA README](../../../backend/evidence_assurance/README.md) | Whole-occurrence alignment and snapshot fingerprint/coverage are separate from CN predicate evaluation. CN is not itself an EA snapshot or expected-fingerprint proof. |

FM's six pins are FRG, VRG, PRG, FLD, VPA and observation-role VSM. FM does not pin a VSP, quantity kind or unit. `measured_actual` is an exact declared role, not calibrated truth. Orientation does not transform a number. FC must not accidentally import any of these absent interpretations.

An arbitrary VCN on the same variable cannot govern automatically: several constraints can address different purposes, and the same variable can be associated with several flows/participants. Neither shared variable identity, similar names, authority metadata, an evidence citation nor a satisfied CN verdict supplies an authority's governing choice.

## 5. Original objectives and before/after contribution

These are the seven original questions in [CLAUDE.md](../../../CLAUDE.md), with FC separated from evaluation:

| Original product question | FC by itself | With existing evaluation and evidence | Remaining gap |
| --- | --- | --- | --- |
| What exists in this system, and how is it connected? | New explicit criterion-to-flow-measurement relation and its dependencies | Same relation, now alongside a sample verdict | As-built and physical topology truth |
| What is the current state of this particular system? | No observed state; declares which criterion applies in a selected membership | Narrow selected-sample conformance, not current physical state | Freshness, actual activity, continuous state |
| Why might the system be behaving this way? | None; declaration rationale is not diagnosis | None; trace explains computation only | Causal models and competing explanations |
| What is the next best measurement or test? | Identifies the declared variable/criterion, not a recommended measurement | Human can identify an unevaluated declared check | Optimization, uncertainty, information gain and costs |
| What would be affected if this component, parameter, or software version changed? | Makes a declared dependency inspectable | Pin changes can disclose loss of applicability | Impact propagation and counterfactual semantics |
| What is the smallest valid set of changes needed to reach a desired state? | None | None | Goals, actions, effects and planning |
| Which conclusions are observed, calculated, inferred, assumed, or unknown? | Separates authority-declared applicability from all sample outcomes | Explicit declaration plus calculated CN verdict and observation trace | Authentication, uncertainty and broader epistemic model |

Before FC, a consumer can find relevant measurements and independently evaluate constraints, but cannot identify the model-declared governing connection. After FC alone, it can inspect that connection, its exact predicate edition, and applicability limitations without obtaining a value. Thus FC directly advances questions 1 and 7, supports dependency discoverability under 5, and enables a bounded contribution to 2 only with existing evaluation. None of this requires a new evaluator by definition.

## 6. Alternatives: pinning and representation

| Alternative | Benefit | Problem or cost | Decision |
| --- | --- | --- | --- |
| Exact FMA assertion-record as governed object | Simplest record reference and individual activity test | Metadata correction or withdrawal of this root removes applicability even if identical meaning is independently asserted; makes a provenance lineage govern the check | Reject as default; viable only if owner wants a named assertion's authority to be essential |
| Effective FM body, selected by an exact FMA witness | Stable under same-body corroboration and metadata correction; all six historical support pins remain exact | Requires explicit body equality and subject-wide conflict rules; witness activity differs from body applicability | Recommend |
| FM semantic subject alone | Small key, stable across support refresh | Automatically governs future FLD/VPA/VSM support editions that authority never selected | Reject |
| Pin all corroborating same-body assertions | Captures a complete endorsement set at one membership | Adds churn on any endorsement change; “all” is membership-relative; unanimity/authority-set policy is outside approved scope | Reject |
| Follow one FMA assertion lineage's latest tip | Allows metadata corrections without restating FC | Can silently follow changed support pins and makes one root privileged despite disagreement | Reject |
| Existing generic relationship | Reuses ledger machinery | Entity endpoints cannot express this n-ary typed relation or exact record closure; changing generic semantics would itself be a new contract | Reject |
| Extend CRG or VCN | Convenient route from CN | CRG's permanent target identity must not change; VCN is context-independent variable predicate meaning. Adding flow semantics changes accepted records and couples independent lifecycles | Reject |
| Additive typed model-kernel declaration | Owns the missing model premise, preserves lower/upper direction and existing bytes | Two new eventual record kinds and focused lifecycle/query surface | Recommend after owner review |
| Do nothing or display a human's unrecorded selection | Zero schema cost; CN remains useful | Does not provide the approved authority-declared relation or replayable provenance | Does not meet the approved consumer need |

No generic “association anchor” is independently needed. The objects already have identities; the new fact needs content-addressed assertion records and derived roots, not another enduring referent. This is why new declaration machinery is justified, but a new identity family is not.

## 7. Exact proposed meaning and governed object

Let S be the accepted immutable FM subject: flow, variable, participant port, exact context, fixed direct-measurement relevance and orientation. Let B be its accepted effective body: S plus the exact FRG/VRG/PRG/FLD/VPA/VSM support IDs. These symbols are explanatory notation, not proposed field names or new IDs.

A positive FC fact says: **the authority designates the exact VCN belonging to the exact CRG as the operating criterion governing the original measured value associated by B.** The registered constraint must target S's variable. Its expected observation role must equal B's pinned measured-actual role exactly. Governing does not mean the criterion is good engineering, sufficient for commissioning, or satisfied.

The governed object is B, not S forever, not one assertion lineage, not a source, not a whole flow, and not the set of endorsing authorities. A membership-present FMA witness determines B unambiguously; no opaque body hash is sufficient on its own. An FC record's content identity includes that exact witness reference. **FC effective-body equality**, however, compares B plus exact CRG and VCN IDs, excluding which same-body witness was nominated. Thus distinct FC records can corroborate the same governing meaning without pretending their provenance is identical.

The FC correction subject is S alone. The governing constraint and exact FM support edition are correctable body choices. Switching variable, port, flow, context or orientation requires a new parentless subject. Choosing a different constraint on the same variable within S requires an explicit FC correction, not automatic discovery. Several active different criterion bodies for S are disagreement, not several independently usable “first-scope” criteria.

VCN pinning remains **exact assertion-record pinning**. CN's accepted query selects one current VCN per ConstraintAnchor; FC must not float to later predicates. Even a semantically identical VCN correction requires FC renewal for present applicability. The deliberate asymmetry is justified: FM already defines cross-root body equivalence; CN does not offer an equivalent governed-body contract. FC does not redesign CN.

## 8. Minimal durable content and field-necessity test

Propose one positive declaration kind and one withdrawal kind in the existing model ledger, not a registration plus declaration plus withdrawal and not a new store. The following specifies semantic content, deliberately not API names, field order or prefix allocations:

| Content | Why necessary |
| --- | --- |
| Exact positive FMA witness reference | Identifies the governed body and all subject dimensions without copying six pins or inventing a new body identity |
| Exact CRG and exact VCN references | Proves target-variable identity and fixes the predicate/semantic-signature edition; no constraint discovery policy |
| Nonempty canonical existing EvidenceRef collection on the positive declaration | Makes the governing choice evidence-bearing rather than inferred from code |
| Existing AuthorityRef and recorded time | Claimed authorship and administrative provenance; not authentication, precedence or effective time |
| Canonical same-root correction-parent set | Explicit correction history and fork/convergence semantics |
| Standard content-derived record identity, version and kind | Integrity and future grammar discrimination, not a new durable anchor |
| Optional ordinary note | Human explanation only; never a parsed rule or hidden applicability qualifier |
| Withdrawal's exact positive target, authority and recorded time | Membership-relative retraction with attributable provenance; no predicate or evidence-bearing negative claim |

Exact context and orientation are mandatory **through the witness**, not optional or ambient. Query requests must state all S dimensions explicitly; no “current context” default. ConstraintAnchor, VCN, FlowAnchor, VariableAnchor, PortAnchor and all FMA identities remain unchanged. Derived source/sink role is not serialized as another authority claim.

No threshold, value, cutoff, source locator, candidate index, freshness duration, uncertainty, confidence, score, satisfaction status, numeric transform, effective-date range, or physical-flow flag belongs in an FC record. The predicate and expected unit/quantity remain in the pinned VCN. Extra provenance should not be copied merely for symmetry.

Positive FC declarations should become citable model claims after separate contract approval; withdrawals remain uncitable and have no evidence field, following FM/FL/VP. Foreign EvidenceRef arms remain declared references, never triggers to read sibling stores. Evidence supports why the authority made the designation; it is not a substitute for mandatory support pins.

## 9. Admission and dependency closure

Prospective append and replay must use the same invariants and validate the complete prospective selected membership before publishing anything:

1. Revalidate all record shapes and canonical content IDs without coercion or hidden state; preserve all pre-existing record bytes and rules.
2. Resolve the exact positive FMA witness, CRG and VCN as members of this same model membership. Wrong kinds, missing members and fabricated IDs reject.
3. Reconstruct the witness's S and B from the accepted FM contract. Prove its six pins and transitive typed dependencies under existing kernel validation: registrations/owners, participant membership, exact-context FLD and VPA, FLD's PCN/PIF direction closure, exact measured-actual VSM.
4. Prove CRG's variable equals S's variable, VCN belongs to that CRG's ConstraintAnchor, and VCN's expected role equals the pinned measured-actual role. Do not require quantity/unit/VSP agreement at FC append: those are evaluation prerequisites owned by existing semantics/CN, not invented FM admission.
5. Validate nonempty evidence and same-membership closure for every model-record evidence reference. Foreign references remain opaque claims. Withdrawal references are never citable evidence.
6. Validate FC parent/withdrawal rules, derive roots/tips/ancestry and bodies, then build immutable indexes and revision material. Recompute from all records, not append chronology.

Historical support may be superseded, withdrawn, inactive or conflicted; that does not make a structurally valid positive FC record impossible to retain. Admission proves an immutable assertion is well formed, **not present applicability**. This separation permits replay and honest stale disclosures. A forged wrong-variable or wrong-context support is a structural error, not a stale record.

No new dependency may point into CN, EA, evidence alignment, source interpretation, observation stores or temporal projections. FK and model-evidence dependency closure must be satisfied by the selected model records alone. Model evidence cycles, if accepted by the existing uniform membership rule, do not authorize recursive proof walks; use visited-set closure rather than inventing a new evidence theorem.

## 10. Correction, withdrawal and replay semantics

The proposed FC lifecycle follows the accepted FM correction-DAG family, with S as the invariant key:

- A parentless positive record starts an independent root, derived from its record identity. Authority/time are not root selectors.
- Every parent must be a membership-present positive FC record of the same S and derived root. Parents are unique and canonical. Self-parenting, missing/foreign parents, cycles and cross-root convergence reject.
- A same-root fork remains a conflict even if its tips have equal bodies. A correction explicitly citing the complete current fork-tip set may converge it. A one-parent correction does not erase an uncited sibling branch. No authority or minimum-ID heuristic repairs a fork.
- Correction can change witness, CRG/VCN and evidence within S. Referencing a same-body witness changes provenance but not governing body. Changing a support pin changes body and must be explicit. No successor of a withdrawn parent is valid.
- Withdrawal retracts exactly one eligible positive tip: unknown, wrong-kind, superseded, non-tip or already-withdrawn targets reject. Selective withdrawal of one fork tip is allowed. A withdrawal is not a correction parent, a claim of original falsity, or a physical cessation event.
- A wholly withdrawn root is inactive. It can be disclosed but cannot vote against an active root; a new assertion after withdrawal starts a new root. Several healthy roots with the same body corroborate; several active different bodies disagree.

These rules are selected-membership-relative. Replay omitting a withdrawal may expose the former tip again. Replay with a retained child but missing parent, witness, CRG, VCN or required model evidence is invalid. A withdrawn target and a successor of that target cannot coexist in a valid replay membership; append order cannot make the combination valid.

Replay does not perform “as of recorded_at” filtering. The caller selects an explicit dependency-closed membership; its revision is computed from that membership. The same material must yield identical roots, applicability and ordering under shuffled input and different hash seeds. A later result about an older membership is historical knowledge disclosure, not a claim about what was physically true then.

## 11. Applicability: exact decision rule, not evaluation

Keep three disclosures separate: **record presence**, **governing agreement**, and **present applicability within the selected membership**. The terms below specify semantics, not allocated status literals.

For requested S, present applicability is established only when:

1. At least one active FC root exists; every active FC root has exactly one tip; all those tips have equal FC effective bodies (B plus CRG/VCN). Inactive roots are disclosed but ignored for agreement.
2. At least one active FM root exists for S; every active FM root has exactly one tip; all those tips have exactly B. Same-root conflicts and cross-root disagreement block applicability even if the nominated witness itself looks healthy. Inactive roots do not veto active corroboration.
3. The selected B's permanent pins are present. Each exact mutable direct FM support pin (FLD, VPA, VSM) is current, has healthy containing lineage, and is exactly aligned under the accepted lower disclosure. Equality to a successor's meaning does not make a superseded pin current.
4. The exact FLD's typed PCN/PIF support pins are also current, healthy and aligned as disclosed by FL. This additional declared-support gate is a conservative FC applicability requirement, not an assertion that the connection physically exists. Do not recursively demand that historical evidence citations remain current: typed support and evidence are different edges.
5. CN's existing kernel constraint lookup for the selected ConstraintAnchor is unconflicted and its sole current declaration is the exact pinned VCN. There is no accepted VCN withdrawal kind to invent; supersession and conflict are its relevant lifecycle changes.

If any condition fails, the FC designation still exists as a historical model claim, but present applicability is not established. Disclose every blocking relation and its exact record/root indices; do not collapse all failures into “criterion false.” Quantity/unit/VSP compatibility, value presence and all sample gates remain unevaluated by FC even when applicability is established.

This definition is intentionally conservative about **exact mutable support editions**, while tolerant of changes in **FM endorsing assertion identity** that preserve B. These are different changes. No lower FM conclusion or alignment flag is redefined; FC derives a stricter applicability relation from accepted disclosures.

## 12. Lifecycle scenario table: consequences of the body choice

| Change in a disposable selected membership | Proposed FC applicability consequence |
| --- | --- |
| Two healthy FM roots assert identical B | Both corroborate; no representative becomes the authority |
| Witness root gets an evidence-only same-body correction | Applicability may persist through the current same-body tip; old witness remains provenance |
| Witness is withdrawn, another healthy root still asserts B | Applicability may persist. This is deliberate effective-body pinning, not record pinning |
| All roots asserting B become inactive | No present applicability, even though witness and FC records remain |
| A previously inactive same-body root is omitted by historical replay | No special effect if all required records remain and another eligible root supports B |
| A same-root FM fork has two equal-body tips | Block: equal meaning does not repair unresolved lineage conflict |
| Two active FM roots disagree on one support pin | Block: exact body disagreement, even if both sets of pins are individually admissible |
| One FM root corrects to B2 with new FLD/VPA/VSM pins | Old FC does not float to B2. It needs explicit FC correction after the authority selects B2 |
| An inactive root historically asserted a different body | Disclose it; no active disagreement solely from this historical fact |
| Two FC roots pin same B and exact CRG/VCN using different same-body witnesses | Corroborating FC meanings, distinct evidence and authorities retained |
| Two FC roots select different VCNs or constraints for S | Block even if both CN predicates happen to be satisfied; no strongest/easiest/latest criterion selection |
| VCN is superseded by an identical numeric predicate | Old FC is no longer presently applicable; exact VCN renewal is required |
| FC root is withdrawn while another same-body FC root stays healthy | Active governing applicability may remain; retraction of one authority is not universal revocation |
| Underlying PIF/PCN becomes stale while direct FMA pins remain unchanged | Typed FL support gate blocks applicability; FM relevance alone is insufficient for this FC gate |
| Observation changes, is null, old, absent, nonnumeric or disputed | FC applicability is unchanged; only separate evaluation/evidence disclosures may change |

A witness's authority is therefore not an enduring mandatory endorsement. If the owner requires that specific authority's continued assertion, this body design is the wrong contract and exact-record pinning should replace it. Do not silently hybridize the two policies.

## 13. Read-only queries, indexes and carriage

The smallest useful query responsibility is exact governing lookup by all S dimensions, returning every FC root and body group, the agreed exact criterion when one exists, applicability blockers, and complete model provenance. One separate assertion lookup supports audit of a named positive record and its activity. Do not automatically copy FM's five-query surface or allocate reverse facades merely for symmetry. An existing FM lookup can supply the locus to a consumer before FC exact lookup.

Immutable derived indexes are needed for record lookup, FC subject membership, parent/successor/root/ancestry relations, withdrawal targets, current tips and effective-body grouping. Build them in validated loaded-model state, never as authoritative files. Full subject-wide enumeration is essential: a caller must not provide a truncated set of corroborating roots that hides disagreement. Optional reverse indexes must have a concrete consumer before entering a later API specification.

Each result carries the full `ModelQueryMaterial` once. Lightweight rows index the carried records and other derived rows; they do not embed duplicate FMA/VCN/support/evidence objects. Root/body agreement, direct and FL-transitive typed-support checks, and exact CN constraint lookup must be reconstructible from that same material. Derive S and B from witness contents; never trust a caller-supplied equality flag, body digest, cached index or scalar summary.

Material includes the complete selected membership, not just positive dependency closure. This proves the absence of additional **members of that selected set**, not that the caller selected the only authoritative or newest model in the world. Expected model revision is a caller commitment; a coherently replaced membership cannot be authenticated by rehashing itself.

For each eventual public field, require either the new designation/applicability disclosure or its necessary provenance: query subject, material, assertion/root/body indices, current criterion reference, activity/health and blocking relations qualify. A sample verdict, duplicated threshold, generic score, copied lower-result trees or a redundant “all inputs admitted” field does not. Names, exact field order, cardinalities and error literals belong in a separately reviewed API contract after this semantic choice is accepted.

## 14. Import direction, reconstruction, limits and no-I/O boundary

Ownership is `backend.model_kernel`: record validation/canonical dispatch, existing model-store integration, immutable loaded indexes, and `ModelQueries` read-only disclosure. Identity definitions remain in `backend.system_identity`; no FC identity is added there. Kernel code must not import `constraint_evaluation`, `semantic_compatibility`, EA, alignment or any observation consumer. Reading an exact VCN is a kernel responsibility; evaluating it is not.

Pure record-collection validation and carried-result reconstruction perform no filesystem, network, clock, environment, connector, sibling-ledger or raw-payload access. Existing explicit model-store load/append operations are the sole relevant disk boundary in a future implementation. A query operates on an already validated loaded membership and owns no store or persistent cache. This proposal performs no future append.

Reconstruction must inspect hostile supplied graphs before serialization/callbacks, rebuild plain records through trusted public validation, recompute membership and all derived rows, and compare complete authoritative payloads. Reject extra/private state, `model_construct`/`model_copy` forgeries, substituted body/support IDs, nonboolean-index violations, reordered/omitted rows, cycles and resource amplification. An upper consumer uses public carried-result validators, not private reducer helpers.

Ordering is canonical record-ID order for material and ancestry sets, exact context/orientation order already used by FM for subject enumeration, and deterministic tuple/body order for group disclosures. Ordering has presentation meaning only; never select a criterion by minimum index, ID, authority, timestamp, filename or input order. A representative may assist display but all agreeing assertions remain visible.

Use the existing kernel result preflight's depth-128 and 100,000-container-node ceilings as a minimum inherited restriction, not a claim that they bound every expanded serialization. Before an API is frozen, specify aggregate serialized-byte, expanded-DAG-node, cardinality and per-string limits for the chosen result grammar and measure a smallest full-maturity witness. Shared DAGs must not bypass expanded-size limits; cycles reject before dump; no new higher limit or borrowed TA-sized allowance is authorized here. Missing numeric budgets block implementation readiness, not the identified model meaning.

## 15. FC plus CN: direct answer and FA cancellation test

An FC query can expose the exact governing VCN and its applicability without any observation. CN already carries its selected VCN, model revision, receipt cutoff, exact semantic/value candidate path and predicate verdict. A human can directly combine them for the approved workflow when the following joins are explicit:

1. FC applicability is established under one selected model revision; CN carries that same revision and the exact governing CRG/VCN and variable, not merely an equal predicate or ConstraintAnchor.
2. The nominated strict candidate index identifies one CN/ES/VS occurrence and exact locator. Receipt cutoff is the explicitly requested normalized cutoff; no most-favorable candidate selection occurs.
3. Existing evidence alignment matches that full occurrence and the same cutoff/locator; the accepted EA evidence selection, coverage disclosures and independently retained expected fingerprint are checked under their own contract. CN alone does not carry those proofs.
4. CN's existing verdict is reported literally: `satisfied`, `violated`, or `not_evaluated`, with its exact declared predicate and lower reasons. FC neither computes nor copies the verdict into a model fact.

Thus **FC plus CN supplies the new model-meaning-and-verdict answer**, while existing EA/alignment disclosures remain necessary to substantiate a snapshot-backed evidence claim. “Plus CN” must not be misread as a proof that exactly two serialized objects contain all EA material. No new flow engineering conclusion is missing after these existing relations are established.

Cancellation test: after FC is accepted and implemented, show a commissioning reviewer the FC applicability query, nominated CN row and already accepted evidence trace. If that supplies the complete approved answer, recommend **no FA milestone**. Convenience formatting or repeating the same statuses is not a separately justified assessment.

Reconsider FA only if a consumer explicitly requires a single independently reconstructible cross-result integrity boundary that these existing contracts do not provide. Neither FC nor CN presently validates their join to one another, and CN does not perform EA alignment. A pure composition might be justified by making those joins authoritative, but it must demonstrate a concrete substitution attack that would otherwise cross the consumer boundary, preserve all lower results, and add no new engineering semantics. That is a later owner decision, not authorization here. Until then FA remains deferred, not completed or cancelled by this proposal itself.

## 16. Disposable decision-usefulness and contract-theatre tests

All examples below are labelled **disposable design worlds**, not fabricated identities, committed fixtures or authoritative model claims.

Imagine one exact FM body for a measured-actual pressure variable at a participant. Existing constraint A is an inclusive `2`–`4` interval; existing constraint B is an upper boundary `10`, both in the same exact declared unit. The authority designates A through FC for the commissioning/operations verification check. With no observation at all, the reviewer can now legitimately identify A as the declared check and reject B as an ungoverned substitute. That decision could not be derived from FM or CN alone.

With a separately admitted nominated sample `4.7`, CN says A is `violated` and B is `satisfied`. FC prevents the consumer from discharging the declared check using B's easier verdict. With `3.2`, CN says A is `satisfied`, permitting the reviewer to record only that this selected evidence meets this declared check. Neither case says pressure proves transport, commissioning is complete, operation is authorized, or equipment is safe.

This is FC's decision-usefulness test: its declaration changes which existing result the named consumer may use, even though FC calculates no numeric result. The evidence-free applicability example proves FC is more than a wrapper around admission of observations.

Contract-theatre rejection probes:

- Remove FC while leaving all FM, CN, EA and alignment results unchanged: a governing designation must no longer be derivable.
- Change only the declared governing constraint: the discovered criterion must change or become conflicted, not be chosen by whichever CN result looks favorable.
- Change only the sample: FC must remain identical; CN may change. A value-sensitive FC query has crossed the boundary.
- Add another healthy same-body FM root: applicability must not change solely because the endorsement set grew. Replace one support pin: exact-body applicability must not silently persist.
- If the initial consumer can already get the authority-declared governing relation from an accepted existing contract, reject the new declaration. Inspection in Section 4 found no such contract.

The consumer-value and no-duplication probes are review judgements. Do not report them as executable test counts.

## 17. Threat model and misleading-success boundary

Principal threats are laundering measurement relevance into criterion authority; presenting a convenient CN result as governing; concealing conflicting roots; changing meaning through support refresh; and treating applicability as satisfaction or physical truth. Integrity threats include coherently rehashed wrong-target records, cross-context/revision substitution, historical witness loss, hidden mutable caches, hostile subclasses, row omission, evidence dereferencing and resource exhaustion.

Every lower admission may succeed while no FC applicability exists: two authorities designate different VCNs; a healthy nominated FMA coexists with an active disagreeing root; an arbitrary satisfied VCN has never been designated; or an old FC points to a superseded VCN. Conversely, every FC applicability gate may succeed while the sample is missing, null, incompatible, nonnumeric or violates the predicate. These are not contradictory outcomes because the layers answer different questions.

Even applicability plus CN satisfaction and complete aligned evidence cannot establish physical flow. Zero may satisfy the predicate without meaning no-flow; a negative number with `opposite` orientation is not reversed transport; a pressure reading may describe a blocked path; complete receipt evidence need not be fresh; matching semantic declarations do not establish calibration. No threshold interpretation, unit conversion, sign transform or uncertainty margin is introduced here.

AuthorityRef is a claimed author and method, not authenticated authorization or an authority ranking. Evidence references are declared provenance, not automatic truth. A hash protects content consistency, not source honesty, complete real-world evidence or the latest authoritative membership.

## 18. Adversarial acceptance matrix

This matrix specifies future obligations only. No implementation or test artifact is created, and no row is claimed to have been executed as an FC test.

| Case | Required result or review evidence |
| --- | --- |
| Valid designation with no observation anywhere | Applicability lookup works; no sample, cutoff or verdict field required |
| CRG targets another variable; VCN belongs to another CRG | Structural admission rejection before publication |
| VCN expects a non-measured-actual role | Structural relation mismatch; no implicit role conversion |
| Wrong flow, participant, context or orientation in witness/correction | Exact subject/closure rejection; no approximate match |
| Missing or wrong-kind witness, six pins, typed FL closure, or model evidence | Dependency-closure rejection; foreign ledgers never read |
| Same-body FM corroboration and evidence-only correction | Applicability persists with complete provenance |
| Withdraw nominated witness but retain other healthy same-body root | Body applicability can persist; explicit regression test distinguishing record pinning |
| Withdraw every same-body root | Historical declaration retained; no present applicability |
| Same-root equal-body fork or active cross-root disagreement | No winner; block even if one nominated assertion is healthy |
| Inactive disagreeing roots beside active agreement | Disclose history; do not manufacture an active conflict |
| Stale FLD/VPA/VSM or typed PCN/PIF support | Applicability blocked independently of declaration presence |
| Two FC roots nominate different same-body witnesses and same exact VCN | Corroboration, not conflict; distinct assertion content identities |
| Different governing constraints, changed predicate or equal-predicate VCN correction | Disagreement or stale pin; never float to the new VCN |
| Same-root convergence, partial fork correction, cross-root merge | Complete convergence resolves; uncited fork remains; cross-root merge rejects |
| Withdrawal of foreign/superseded/already withdrawn target; successor of withdrawn parent | Membership validation rejects, regardless of append order |
| Closed historical subset omits withdrawal versus omits required parent | Earlier activity restored in first; invalid membership in second |
| Timestamps/authority/file names/hash seeds/input order permuted | Same derived semantic result; canonical presentation order only |
| Forged rows, omitted roots, private state, caches, booleans as indices | Authoritative reconstruction rejects before trusted derivation |
| Cycles, shared DAG amplification, exact and over-bound graphs | Deterministic bounded failure before unsafe expansion; budgets frozen before implementation |
| Query/reconstruction spies on disk/network/clock/environment/sibling stores | Zero calls; explicit store boundary tested separately |
| Zero-FMA authoritative membership | No FC positive append proposed or inferred; structured absence |
| Sample null/zero/sign/unit/cohort/source disagreement variations | FC unchanged; lower numeric/evidence behavior remains owned below the consumer |
| FC/CN different revision, variable, VCN or nominated occurrence | Direct workflow rejects the join; motivates FA only if a new integrity boundary is genuinely required |
| Commissioning reviewer chooses B instead of designated A | Named consumer can detect and reject substitution using FC; review plus disposable demonstration |
| All statuses green but wording says flow occurred or safe | Reject design/result presentation as misleading success |
| Seven-objective and every-field audit | New applicability meaning or necessary provenance only; no decorative vocabulary |

## 19. Authoritative zero-FMA state and verification strategy

The committed model has no FMA support. FC cannot validly append over nonexistent FM records, and no new FMA is implied by the owner decision. Preserve 36 records, the accepted revision, all identities, canonical bytes, artifact logic and protected digests. Keep the model-kernel export count at 225 throughout this investigation; a future approved additive surface would require its own explicit contract and preservation evidence.

A labelled disposable world is sufficient to prove software behavior and demonstrate the named workflow's bounded benefit. It should exercise one valid FC designation, both numeric outcomes through existing CN, a competing ungoverned constraint, same-body root replacement and loss of all support. Its evidence must traverse public APIs and existing EA/alignment when claiming snapshot-backed verification. It is not a claim about the authoritative printer model or a real physical system. No shipped demonstration or ledger append is required.

After separate implementation authorization, verification should cover additive canonical dispatch, full collection replay, exact lifecycle/query reconstruction, import/no-I/O boundaries, lower-consumer regressions, disposable workflow examples, at least five deterministic hash seeds, and preservation of accepted artifacts. Full and clean-checkout suites belong to that future change, not to this design-only investigation. Numeric resource ceilings and exact API grammar must be frozen and tested before that work is ready.

For this proposal, verification is read-only source inspection, baseline and frozen-digest checks, preservation/status checks, local links, contiguous sections, exact ending marker and whitespace checks. The only Phase 2 output is this uncommitted file. `.claude/settings.local.json` remains unchanged and uncommitted at SHA-256 `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 20. Owner decisions, remaining gates and final boundary

The owner has already settled the consumer, question, single-criterion/candidate scope, excluded freshness/agreement/uncertainty concerns, carried-proof boundary, disposable verification sufficiency and FA reconsideration requirement. Genuine design decisions still requiring acceptance are:

1. **Governed object:** accept effective-body pinning through an exact historical witness, including continued applicability after that witness is withdrawn when another healthy same-body root remains; or choose exact-record dependence if continued endorsement by that lineage is essential. Lead choice: body pinning.
2. **Correction and agreement:** accept S as FC correction subject, allowing explicit replacement of the chosen constraint, with all active roots required to agree and inactive roots non-vetoing. Lead choice: yes; no parallel criterion aggregation in this scope.
3. **Edition/currentness policy:** accept exact VCN renewal and conservative current/healthy direct and typed FL support gates, rather than a floating-equivalence policy. Lead choice: exact editions; historical designations remain inspectable.
4. **Durable representation:** accept two additive kernel record kinds, nonempty evidence on positives, uncitable withdrawal, and no new anchor. Lead choice: yes. Public names, grammar, budgets and any implementation plan require later reviewed specification; this proposal allocates none.

A later consumer gate, not a prerequisite to recording FC meaning, is whether a separately reconstructible FC/CN/EA join is actually needed. Prefer cancellation of FA if direct existing results suffice. Reassess only after FC is accepted and implemented; do not start an evaluator because the roadmap has a vacant milestone label.

The strongest defensible FC statement is authority-declared applicability of one exact variable criterion to one exact FM body in one selected model membership. FC must never conclude satisfaction, violation, flow state, activity, occurrence, continuity, conservation, causality, correctness, safety, diagnosis or recommendation. It stores neither an evaluated outcome nor a permission to act.

Lead recommendation: proceed to owner review of this additive, body-governed declaration design, not implementation. FA stays deferred. ADR-0022 stays absent and unallocated. No FC branch, production code, tests, fixtures, identities, records, authoritative append, push, merge or history rewrite is part of this proposal.

END OF FC-001 CODEX LEAD PROPOSAL
