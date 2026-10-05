# Checked derivation and applicability corrected design v2

Date: 2026-10-04, Europe/Amsterdam. Documentation-only second correction for focused independent confirmation. This complete successor preserves the first corrected draft and addresses the reviewer's consequential same-item review-precedence finding. It supersedes that draft's recommendation and the 2026-10-01 successor without changing either file, the independent review, accepted application profiles or experimental evidence. It does not freeze an executable contract or authorize implementation, fixture preparation, tests or a new qualification campaign.

## 1. Frozen inputs and correction scope

Repository checkpoint inspected for this correction: `2f0afbd368105b99f0b8548ffece107918386e3d`. The index and pre-existing changes are preserved. The earlier report's provenance and numerical witnesses remain historical design-review evidence, not newly executed application results.

| Frozen input | SHA-256 |
|---|---|
| [First corrected draft inspected by the focused reviewer](2026-10-04-checked-derivation-and-applicability-corrected-design.md) | `d1609c607ecfd342be1a752c33ce8766920e83dc1b63e945639cbccb3e55e936` |
| [Reviewed successor](2026-10-01-checked-derivation-and-applicability-successor-design.md) | `27e2a5a2e527cc6763fa4479ed6b83b3736d9faedfce48e9db3096dbf20fdd23` |
| [Independent adversarial review](../reports/2026-10-04-checked-derivation-and-applicability-independent-adversarial-review.md) | `ed14313f66746b57856ef7dcef02015ccd81e0ca137f951bfd483d4ea08505a5` |
| [Original intake proposal](2026-10-01-investigation-handoff-and-hypothesis-intake-design.md) | `48209b883ba1b47f32a6a4b2b701b70b4ee5d467e93a9e09709510974d68da7c` |
| [Simulated investigation report](../reports/2026-10-01-simulated-investigation-experiment.md) | `5f822e9afa089616e1266a1ccb43732715009cb19dd335108815b135012fb4e6` |

F1 is addressed by choosing the review's minimal, explicitly labelled ideal-measurand scoring contract. We do not introduce uncertainty-aware optimization, error distributions or a new attainable-assessment-branch engine. F2 is addressed by separate completed evidence relations and review completeness, exact same-item review/exclusion precedence, and exact governing-state precedence. The first corrected draft left irrelevant-plus-unresolved reviews of one item ambiguous; the focused reviewer identified it before implementation. Section 5 below corrects that boundary without changing the score contract. These are design recommendations under the owner's correction authorization, not deployed policies; closure remains subject to independent confirmation.

The original preservation index remains applicable. The semantic candidate is recoverable in tracked repository material at SHA-256 `8726f35dac9997ee82c0764c95f749cb462e796c6d04794758a90775d0671305`; only its experimental-workspace copy is absent. The missing distinct pre-fix builder for failed attempt 006 remains a gap. The historical 1,756-file experiment inventory is reported evidence; this correction does not repeat that runtime inventory, rerun the experiment or claim independent physical validation.

## 2. Application principle and unchanged scope

The application checks that predictions follow from a supported, versioned model and captured inputs. It separately assesses evidence for applicability and applies explicit use policy. Calculation correctness, applicability, conditional compatibility, evaluation permission, execution permission and human adoption are distinct.

The proposed sibling profile remains `bdw.checked-temperature.v1`, a fixed synthetic temperature template with the two existing account kinds, at most two nominated procedures and at most three outcome regions per procedure. A supported template is software-supported, not physically validated. Users supply bounded declarative model parameters and nominated accounts; they cannot upload executable equations, assert a checked output table or nominate arbitrary causal kinds.

The fixed relationships are `T_true = baseline - b_suspect` and T1 ideal measurand `T_true + b_ref`. H1 is `high_underlying_faithful_baseline`; H2 is `low_underlying_positive_offset`. T2 reports `heater_on` iff the held suspect baseline is less than the declared target, otherwise `heater_off`; equality is off. It does not compare the hidden true temperature with the target. Exact allowed parameters, the meaning of the account kinds and literal procedure/decoder editions remain contract-preparation obligations in section 10.

Human nomination does not assert truth or exhaustiveness. The profile does not discover hypotheses, acquire physical observations, establish causality, authenticate identity or automatically adopt results. No backend extension, IN-001 or CI-001 follows from this correction.

## 3. Captured records, joins and responsibilities

Every design record retains an ID, immutable revision, predecessor where applicable, provenance and canonical content digest. Required typed references resolve transitively to retained bytes. Names below are design identifiers, not implemented schemas.

| Record | Required information and boundary |
|---|---|
| Explanation | Human-proposed account kind, statement, proposer, rationale and exact subject. |
| Model/input graph | Maintained template/rule edition, predictive-model revision/digest, bounded parameter intervals and units, admitted baseline evidence/extraction, procedure/decoder references and governing conditions. |
| Observation interpretation plan | Per scalar procedure, the declared hard-error rule and bounds, quantity/unit and interpretation edition, including exact-point treatment. Unknown or confidence-only error is not silently converted to a hard bound. This is a declared, conditionally applicable plan, not an error estimate certified by the application. |
| Derivation | Exact inputs, allowlisted calculator/build identity, rational intermediate intervals, ideal predicted sets, outcome intersections/exclusions, dependencies and explicit uncertainty placement. Software produces and freshly recomputes it. |
| Condition declaration/evidence review | Typed proposition, governed hypothesis/procedure/phase, subject/context/time, declarer and state; supplied evidence; exact review bindings, reviewer/rule, relevance, support/opposition/unresolved relation and rationale. A declaration is not a review of itself. |
| Applicability | Completed reviewed relation, review completeness, governing condition state, reasons, all contributing and excluded-item references, and policy-derived use decision. |
| Selection | Checked derivation/applicability references, explicit score domain, exact survivor branches/scores, tied preferred procedures and limitations. |
| Conditional reassessment | Retained checked selection and original derivation, new admitted result, bound interpretation, current applicability, intersecting branches, compatibility dispositions and limitations. |
| Authority/adoption | Separate purpose-specific evaluation, execution and adoption records with exact target, scope/time/basis and local issuer declarations. Mechanical packaging can draft a target but cannot issue permission. |

Bind system/model ID, component/entity and variable/state anchors, public structural-model revision, source/adapter/subject/property path, instrument identity/mapping provenance, quantity/unit editions, assertion context, scenario, evidence digests, procedure/decoder editions, as-of cutoff, acquisition interval and model-applicability interval. Predictive-model revision differs from public structural-model revision. Recorded, declared exposure and acquisition times remain distinct; hashes do not certify chronology.

The retained example uses baseline 60.1, H2 offset [5,15], b_ref=0 and declared hold. Reference mapping was declared using the suspect sensor path, not independently established. The synthetic August acquisition clock and October exposure declarations have no verified clock relationship. These limitations remain visible in any new request based on the historical material.

## 4. F1 correction: exact selection score domain

The score domain is `ideal_measurand_decoder_branches`. For each hypothesis and procedure, derive the complete conditional ideal measurand set from captured model inputs and parameter intervals. For each exact decoder outcome region, permit that hypothesis if the sets intersect; exclude it only if a complete justified intersection is empty. Endpoint rules and exclusion bases are retained. Partial positive coverage cannot license a complement exclusion. Incomplete cells or blocked applicability withhold ranking over the whole nominated set; do not silently prune a hypothesis or procedure.

With a complete eligible matrix, an outcome's survivor set contains the nominated hypotheses that permit it. The procedure score is the maximum survivor cardinality across its declared outcome branches. Empty branches and repeated survivor sets remain retained; ties are preserved. The captured selection explicitly reports `score_domain = ideal_measurand_decoder_branches` and `post_measurement_elimination_guaranteed = false`. These labels are computed output obligations, not caller-controlled permission or evidence.

The required presentation is: "Preferred for worst-case separation of ideal modelled decoder branches among these supplied hypotheses. Measurement uncertainty can leave multiple hypotheses unresolved; this score does not guarantee elimination, a settled reassessment or the actual cause." The score must not be labelled operational worst-case surviving hypotheses, expected information gain, probability of diagnosis or guaranteed real-world discrimination. No probability, cost, error-frequency or empirical calibration claim is introduced.

Parameter ranges are included once in the ideal predicted set. Observation uncertainty is not folded into that score. The selection nevertheless captures the proposed interpretation plan and reports `observation_uncertainty_not_in_score`, its exact bounds and governing applicability conditions. This prevents the plan being hidden; it does not turn the ideal score into an operational guarantee. A missing required plan withholds a new scalar-procedure selection rather than supplying a default. Valid model arithmetic may still be inspected separately. The non-scalar T2 indicator uses its own fixed interpretation edition; no temperature-error interval is invented for it.

Reassessment applies the admitted scalar observation's hard interval once, requires containment of the admitted scalar, and intersects every decoder branch reached by that interval. A hypothesis is compatible only if all intersecting branches permit it; conditionally incompatible only if all have qualified exclusions; missing/conflicting qualification or mixed permits/exclusions is unresolved. Baseline-ineligible accounts remain baseline-ineligible within the captured assessment, not permanently across future revisions. Unresolved accounts are never described as eliminated.

Result interpretation must match the retained selection plan's rule, bounds, units and edition. A different observation value or acquisition interval is normal new evidence; a different interpretation rule/bound is not an inherited plan. It needs an explicit immutable successor request and newly scoped authority, reports the plan change and references the former selection historically. It cannot claim execution of the original unchanged plan. Nor can a result-time review retroactively upgrade selection-time applicability. Preparing that successor does not automatically rerank or adopt anything.

**Analytical witnesses; none executed by this correction.** With the retained decoder low <=56, gap (56,59], high >59, H1/T1 {60.1} permits high and H2/T1 [45.1,55.1] permits low. The ideal score is 1; T2's common heater_off branch gives 2. That conditional ideal preference remains, irrespective of whether a admitted interpretation subsequently resolves an account.

For a newly scoped plan with hard half-width 2.5, if admitted by the eventual exact numeric contract, H1 true=60.1/offset=0 with reference error -2.5 and H2 true=55.1/offset=5 with reference error +2.5 both yield scalar 57.6 under b_ref=0. The interpreted interval [55.1,60.1] reaches low/gap/high. Both hypotheses are unresolved by the mixed-branch rule. The new presentation reports ideal score 1 and explicitly does not promise one operational survivor. Error is applied once to the observation; this is not a new parser test or an error distribution.

With half-width 0.5 and reading 60.0, [59.5,60.5] reaches only high: H1 is conditionally compatible, H2 conditionally incompatible. Conversely, measurand 55.1 plus legal error +0.5 yields reading 55.6 and interval [55.1,56.1], reaching low and gap: H2 is unresolved, even though only one hypothesis is non-excluded. Thus an ideal survivor score and a settled compatibility answer are distinct even at the retained bound.

Future uncertainty-aware selection would require an explicitly different score domain, attainable interpretation branches, a rule counting unresolved accounts and exact planned-error bindings. It is deferred, not implied by reuse of the pure minimax ranker or silently added here.

## 5. F2 correction: evidence aggregation and use precedence

Aggregation is per exact typed condition, affected hypothesis/procedure/phase and assessment context/time. The closure contains every evidence item supplied for that condition and every supplied bound review; removing an item creates a different captured graph, not the same assessment. The application cannot know about unsupplied evidence and does not claim completeness of a physical investigation.

For each supplied condition-bound evidence item, determine which reviews apply through exact evidence/condition identity and explicit typed scope/time checks. A valid in-scope completed review can contribute support, opposition or unresolved relation. Mutually inconsistent applicable reviews are retained; there is no newest-timestamp winner. Human judgments remain identified as human judgments. The application checks and aggregates them; it does not infer calibration or relevance by reading an attachment.

Missing required bytes or malformed required identities refuse structurally before aggregation. They cannot be treated as irrelevant or policy-tolerable pending evidence. For each otherwise well-formed condition-bound item, use this exact item-level order before computing the condition-level axes:

1. **Conclusive typed exclusion.** Exact profile-defined subject/context or declared applicability-validity intervals can establish that the item does not apply to this assessment, such as a non-overlapping validity interval. Retain that basis and all reviews; the item contributes neither completed relation nor pending status here. Raw publication, acquisition or attachment time alone is not an applicability-validity interval. A review that does not satisfy the exact assessed scope/time is not an applicable opposing review for this assessment. Conclusive exclusion is a typed scope check, not an interpretation of attachment contents or a newest-review choice.
2. **Collect every potentially applicable review of all remaining items.** Applicable completed reviews explicitly finding relevance can contribute their completed support or opposition relations. Do not erase these contributions because another review calls that same item irrelevant. If a completed relation is unresolved, relevance is unknown/unresolved, or a required review is missing/incomplete, that item is pending. An unreviewed bound attachment is potentially relevant and pending. Unknown or partially overlapping scope that does not establish exclusion remains pending until an applicable review resolves it.
3. **Order competing relevance judgments.** A completed irrelevant/out-of-scope judgment does not suppress another still-potentially-applicable unresolved judgment. Their combination is pending, with the competing judgments retained. Completed relevant and irrelevant judgments of the same item are also pending due to disputed relevance; still retain completed relevant support/opposition in the relation axis. There is no newest-timestamp or preferred-reviewer winner. This disputed relevance does not itself manufacture empirical opposition or the condition-level `conflicting` relation: it affects completeness. If support and opposition coexist, the condition is conflicting independently of completeness.
4. **Reviewed exclusion only after those checks.** An item may be excluded on review judgment, contributing neither relation nor pending status, only when every potentially applicable supplied relevance judgment is completed and agrees that it is irrelevant/outside scope, with no unresolved judgment, relevant judgment or missing required review. One unopposed completed irrelevant review suffices if no other review is required by the captured profile. Retain the excluded item, every review and the exclusion reason. Otherwise use the retained relation contributions and pending rule above.

Thus all reviews of a single item are aggregated before its status is set, and all item contributions then feed the condition. Expired or conclusively out-of-scope support cannot settle current applicability; an applicable completed opposing judgment cannot disappear because an irrelevant or unresolved judgment was added. The application does not claim physical certainty for a human relevance judgment or detect reviews/evidence not supplied in the graph.

The two independently visible axes are:

- `reviewed_relation`: `support_only`, `opposition_only`, `support_and_opposition`, or `none`. This is computed from applicable completed support/opposition reviews only. A completed unresolved relation supplies neither side and leaves a pending item.
- `review_completeness`: `pending` if any potentially relevant item remains pending, otherwise `complete` for the supplied graph. `complete` does not mean all evidence that might exist has been acquired. Retain exact pending-item and excluded-item lists.

The governing empirical state is computed in this exact precedence; declaration, binding and authority checks are separate mandatory gates:

| Applicable completed reviews | Review completeness | Governing empirical state | Use effect |
|---|---|---|---|
| Support and opposition | Either | `conflicting` | Always block affected use. |
| Opposition only | Either | `contradicted` | Always block affected use. |
| Support only | Complete | `supported` | Conditional use may proceed if declaration, scope and separate authority pass. |
| Support only | Pending | `unresolved` | May proceed only under the exact policy allowlist for that unresolved condition, with pending reasons disclosed. |
| Neither support nor opposition | Either | `unresolved` | Same explicit unresolved-condition policy; no positive empirical support is invented. |

Pending evidence never downgrades known contradiction or conflict into policy-permitted unresolved. A declaration of true/applicable never erases reviewed opposition. Conflicting applicable declarations block; false, unknown or missing required declarations and out-of-scope required conditions block. An allowlist for unresolved empirical support cannot repair any of these independent failures.

For each governing condition the captured deployment policy explicitly permits or forbids `unresolved` use. That same decision applies to no-reviewed-support, incomplete relation/relevance, and support-plus-pending; there is no hidden extra exemption for the last case. It cannot permit `contradicted` or `conflicting`. This correction recommends conditional synthetic use of explicitly declared unresolved calibration/hold/mapping only where the owner selects those conditions. It does not select reviewers, issuers or a deployment allowlist on the owner's behalf. Omitted entries mean unresolved use is forbidden, not permitted by default.

If any governing condition blocks selection, withhold ranking across the entire nominated set. For reassessment, report applicability blocked and affected compatibility not assessed; do not silently drop candidates, resurrect baseline-ineligible accounts or overwrite prior results. If all gates pass with at least one governing unresolved condition, the use disposition is `conditional_use_with_unresolved_conditions`, enumerating assumed conditions and pending evidence. A `supported` label cannot stand in for physical verification or permission.

**Exact aggregation twins; design expectations, not passing tests:**

| Captured same-condition graph | Computed relation / completeness / state | If unresolved calibration is forbidden |
|---|---|---|
| One applicable completed supporting review | support_only / complete / supported | May proceed subject to all other gates. |
| Same support plus a new unreviewed bound attachment | support_only / pending / unresolved | Block; a pending badge alone is insufficient. |
| Same pending graph, policy explicitly permitting unresolved calibration | support_only / pending / unresolved | Conditional use only; list pending evidence and all other unresolved governing conditions. |
| Opposition plus pending attachment | opposition_only / pending / contradicted | Block regardless of unresolved allowlist. |
| Support plus opposition plus pending attachment | support_and_opposition / pending / conflicting | Block regardless of unresolved allowlist. |
| Support plus an explicitly reviewed irrelevant attachment, no other pending items | support_only / complete / supported | May proceed; retain irrelevant attachment/review and exclusion reason. |
| Only expired support, conclusively non-overlapping with this assessment | none / complete / unresolved | Block; historical support remains readable. |
| Support on item A; item B has completed irrelevant plus unresolved-relevance reviews | support_only / pending / unresolved | Block; B's irrelevant judgment cannot suppress B's unresolved judgment. |
| Same item has completed relevant support plus completed irrelevant review | support_only / pending / unresolved | Block; disputed relevance remains pending, and completed support is retained. |
| Same item has completed relevant opposition plus completed irrelevant review | opposition_only / pending / contradicted | Block; disputed relevance does not erase opposition. |
| Support on A; B is conclusively outside typed scope, with an unresolved review retained historically | support_only / complete / supported | May proceed subject to other gates; B's independent exclusion basis remains explicit. |

Changed attachment, review, declaration, policy or assessment context creates a successor applicability/request identity. Old condition states, results, exposures and permissions remain preserved. A newly completed opposition review can turn unresolved into contradicted; it cannot retroactively make an older captured assessment know the review. Reusing a previously supported record in a new graph without recomputation is prohibited.

## 6. Enforced consumer, verification and replay boundary

The sibling checked-selection and checked-reassessment routes validate typed closure, exact joins, maintained rule/build identities, declared conditions, captured policy and purpose-specific authority before consumption. They freshly derive ideal predictions and their exclusions, recompute section 5 aggregation and gate use, then calculate the section 4 selection or interval-based reassessment. A UI badge, caller-supplied matrix, preapproved table or asserted `checked=true` cannot substitute for this boundary. Missing numeric inputs produce derivation unavailable, not guesses. Complete conditional mathematics may remain inspectable when applicability blocks its use.

| Operation | Required responsibility |
|---|---|
| Evaluate | Fresh derivation/applicability and downstream calculation. Optional submitted cached records are comparison artifacts; a mismatch refuses. Produce explicit score-domain and conditional-use limitations. |
| Verify | Integrity, complete typed closure, exact subject/model/rule/authority joins and permitted builds; freshly recompute derivations/exclusions and aggregation/policy gates; compare canonical records; validate downstream references and mandatory score-domain/uncertainty-plan metadata. Report `derivation_checked`, `applicability_policy_checked`, `downstream_result_not_replayed`. Do not claim fresh ranking or compatibility computation. |
| Replay | All verify checks plus independent downstream selection or observation interpretation/compatibility and semantic-trace recomputation/comparison. Produce a separate bundle without overwriting history. Physical work evidence remains retained and checked against limits but need not be byte-identical. |

Fresh computation is from captured inputs, not retained calculated tables/results. It is not an independently authored scientific model or independent empirical validation. Completed evidence reviews remain inputs; replay reproduces policy treatment, not a physical investigation.

Correctly rehashed altered tables with unchanged inputs fail fresh derivation comparison. A correctly rehashed altered downstream score may survive a verify operation that expressly does not replay it; replay must detect it. Mandatory misleading score-domain metadata is outside that weaker-result allowance and refuses verification. Changed inputs/model/conditions produce a distinct exactly scoped request. Unknown calculator editions or caller-uploaded code cannot acquire authorization through a self-declared hash.

Expected request/authority pins must be supplied through a trusted external entry-point boundary, not solely recovered from an attacker-rehashed bundle. A changed authority record cannot match an unchanged externally expected pin. A fresh locally coherent request and pin is still a declared new assessment, not authenticated ownership or permission to replace history. No credential/authentication service is added here.

## 7. Concrete historical-example interpretation

These are proposed conditional calculations using retained values, not runs of new software. Baseline 60.1, H2 offset [5,15], b_ref=0 and hold yield the ideal T1/T2 preference in section 4. Calibration, hold and mapping remain empirically unresolved unless applicable reviews support them; selection/reassessment use depends on the exact captured allowlist and separate permissions.

| Case | Conditional result under the retained 0.5 plan | Effect of subsequently supplied evidence |
|---|---|---|
| Baseline, scalar 60.0 | Interval [59.5,60.5] is high; H1 compatible, H2 conditionally incompatible. | Synthetic reveal is not independent model/calibration validation. |
| A2, scalar 59.2 | [58.7,59.7] spans gap/high; H1 unresolved, H2 conditionally incompatible; assessment incomplete. | Offset 1 is omitted from the nominated [5,15] range, not eliminated as a general explanation. No third small-offset account can be nominated in this fixed profile. Revised parameters need a new post-result request. |
| A3, scalar 52.3 | [51.8,52.8] is low; H2 conditionally compatible before contrary evidence. | Unreviewed bound cooling reveal makes review completeness pending, not completed opposition. Governing state follows section 5; unresolved policy may withhold or permit explicitly conditional use. A completed opposing hold review makes it contradicted and blocks use. Prior conditional result remains historical. |
| A4, scalar 60.1 | [59.6,60.6] is high; H1 conditionally compatible before contrary evidence. | Unreviewed bound reference-bias +8 reveal is pending. A completed applicable review opposing b_ref=0 makes applicability contradicted and blocks use. The application does not acquire a faulty-reference causal kind or physically certify the suspect sensor. |

A raw attachment does not itself become reviewed support or opposition. It does change review completeness and potentially the governing state, as section 5 specifies. Post-result reveals retain that exposure label, never becoming pre-acquisition evidence. A3/A4 are limitations under violated assumptions, not observed software defects. The displayed conclusion remains: "One of the supplied hypotheses is compatible under this model and these conditions; actual cause is not established." Show applicability, pending items, unresolved accounts, evaluation/execution permissions and adoption state alongside it.

## 8. Legacy and product boundaries

Existing NM supplied-support and NR v2 contracts, parsers, commands, support grammar, retained bundles and historical interpretations remain unchanged. The new route does not insert a new origin into the legacy closed grammar or serialize computed tables as adopted `supplied_synthetic` premises. Legacy verify/replay do not gain checked model-to-table derivation claims.

Current application build identity includes the tracked application source tree and checkpoint. New modules or dispatch change current identities even with unchanged old semantics. Historical replay therefore still requires the original source/checkpoint, contract editions and executable environment; leaving schema text unchanged is insufficient. Do not relabel old synthetic premises or upgrade old bundles in place. Pure ranking, interval mathematics and public evidence validation may be reused where their semantics match, without importing legacy supplied-support qualification as the checked route's trust decision.

Public-result producer/test-builder dependence remains open; this design does not deliver an end-to-end physical acquisition route. Parameter proposing, model adequacy, omitted causes, evidence review judgments and manual disposition remain human responsibilities. General hypothesis discovery, action coupling, causal confirmation, arbitrary simulators, backend additions and autonomous reranking/adoption remain outside scope.

## 9. Finding dispositions and focused confirmation request

| Finding | Corrected rule | Confirmation target |
|---|---|---|
| F1, score domain | Section 4 explicitly chooses ideal-measurand decoder branches, captures but does not rank observation uncertainty, prohibits operational guarantees and preserves conservative reassessment. | Re-evaluate 2.5 and 0.5 analytical twins; attempt misleading score labels and changed interpretation inheritance. |
| F2, pending evidence and consequential same-item ambiguity | Section 5 first gives exact item-level review/exclusion precedence, then relation/completeness axes, governing-state precedence and uniform explicit unresolved-condition policy. Contradiction/conflict always block. | Challenge support+pending, opposition+pending, both+pending, irrelevant-plus-unresolved or relevant reviews on the same item, conclusive typed exclusion, expired evidence and changed-graph reuse. |

The focused reviewer must have no authorship role in this successor. Read frozen inputs and this candidate completely; inspect source where necessary without executing repository code. Confirm or reopen F1/F2, identify any consequential defect introduced by these corrections, and distinguish contractual ambiguities from observed failures. Reviewer endorsement is not owner approval. Do not add unrelated product requirements as new blockers.

## 10. Concrete prerequisites before executable contract freeze

The six prerequisites identified in the independent review remain explicitly open preparation work, not additional resolved defects or implementation authority:

1. Exact H1/H2 parameter and kind constraints, positive-offset domain and low criterion, admissible reference-bias intervals, baseline eligibility, rational/decimal endpoints and units. The historical experimental calculator is not the new account-kind validator.
2. Exact decoder partitions and literal procedure/interpretation editions, T2's held-suspect threshold and equality rule, scalar-plan containment and any numeric admission bounds. The ideal-score rule is fixed here; uncertainty-aware optimization is not included.
3. Finite governing-condition catalogue, unique typed proposition/subject/phase identity and contradictory declaration detection. No general natural-language theorem prover is implied. Section 5 aggregation is normative for that catalogue, not left to later implementer choice.
4. Exact external expected-pin carriage and evaluate/verify/replay interfaces, plus deployment reviewer/issuer roles and explicit unresolved-condition allowlist. Local declarations/pins remain unauthenticated.
5. Explicit source/module/build capture and preserved historical execution/replay environments. No default promise that an old bundle replays in a changed checkout.
6. Complete finite byte/object/review/history/rational/work/trace/retention limits, exact delivery schemas and a bounded preparation/verification plan before implementation. Resource exhaustion refuses before omitted dependencies or unbounded work; existing old-profile ceilings are not new capacity evidence.

The next gate is focused independent confirmation of this correction, followed by owner consideration of the semantic candidate and separately scoped contract/fixture/resource preparation. No application implementation, experiment, tests, runtime/ledger mutation, cleanup, staging, commit, export or remote operation is authorized or performed by this document.

END OF CHECKED-DERIVATION AND APPLICABILITY CORRECTED DESIGN V2
