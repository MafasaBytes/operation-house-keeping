# BRC-EXP-001 — Baseline Reasoning Closure Spike

Codex lead proposal — 2026-09-11. Design only; not implementation approval.

## 1. Recommended experiment and necessity

**Recommend outcome 1: proceed, after separate owner approval, with one disposable
implementation spike containing Mode A and Mode B.** Use a prior-free finite
diagnostic matrix and exact minimax survivor counts. Do not implement a production
package, shared facade, solver, public application entry point, durable record,
ledger, fixture append, ADR, UI, HTTP API or hardware integration.

The new experimental decision is not another FC/CS aggregate. It is: given an
explicit finite set of conjectures and conditional predictions, which conjectures
are contradicted by admitted facts, and which nominated measurement most reduces
the worst-case number of remaining conjectures? Existing tests demonstrate
observation admission, equality/constraint evaluation and lower joins, but not
this hypothesis-elimination and measurement-discrimination computation. Searching
the live backend/tests found no diagnostic-matrix, minimax, information-gain or
hypothesis-generation implementation. This negative search is corroborated by
the public contracts below, not treated as proof by keyword alone.

Mode A supplies the missing hypothetical semantics explicitly and tests the
algorithm. Mode B attempts the same derivation from public model/results only
and must expose every missing premise. A useful negative Mode B result must not
erase a successful Mode A algorithm experiment, nor may Mode A assumptions be
smuggled into Mode B and called model-derived knowledge.

The expected finding is **algorithmically feasible with supplied predictions;
model-derived diagnostic predictions are not currently established**. This is
an inspection-based expectation, not a performed spike or a new accepted
architecture decision. In particular, BH-001 has no directed input/output rule
or fault-conditioned predictor. That does not by itself prove IN-001 is needed:
the selected algorithm requires compatibility predictions, not a causal graph.

The initial experimental consumer is the owner reviewing reasoning feasibility,
not a deployed commissioning application. CV-001's application prerequisites
remain binding for any later delivery. No independent challenger runs in this task.

## 2. Verified baseline and protected material

All material checkpoints matched before this file was written:

| Checkpoint | Verified live value |
| --- | --- |
| Branch and initial worktree | `main`; completely clean |
| HEAD and origin/main | Both `debcffec5a77ae270bbf8822f82ef1aa7556c5bd` |
| Latest commit | `docs: defer CV-001 pending application requirements` |
| Remote relation | Equal, not trailing; parent is accepted DI closeout `1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675` |
| FC / CS / DI / CV | FC complete and owner accepted; CS closed as application policy; DI closed as bounded application composition; CV backend additions cancelled and application delivery deferred |
| Authoritative model | 36 records; exact load and replay agree |
| Accepted revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Model-kernel exports | Exactly 236, unique; ordered export digest below |
| FMA/FMW; FCD/FCW | `0/0`; `0/0` |
| ADR sequence | 22 accepted files, unique and contiguous ADR-0001 through ADR-0022 |
| ADR-0023 | Absent, unallocated and unreserved |
| Last full accounting | 4,074 passes in the accepted FC verification report; historical, not rerun |

Freshly checked document/public-surface digests include:

| Protected input | SHA-256 |
| --- | --- |
| [DI owner decision](../reports/2026-09-10-di001-application-composition-owner-decision.md) | `ca5413a558ec5512c34845715fc1c63a8b403f31f0ccf5e505c8e2eb081bfaa0` |
| [CV owner decision](../reports/2026-09-10-cv001-deferral-owner-decision.md) | `7960868e4367e112f7d7dcb275d344ec7e95337be67f29ee9d8cb57d2e7a97bb` |
| [CS owner decision](../reports/2026-09-10-cs001-application-policy-owner-decision.md) | `8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3` |
| [Post-FC reconciliation](../reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md) | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| [FC acceptance](../reports/2026-09-09-fc001-final-owner-acceptance.md) | `1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` |
| [FC verification](../reports/2026-09-09-fc001-slice-b-final-verification-report.md) | `eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71` |
| Ordered compact-JSON export list, no newline | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |

Protected inventories were recomputed as sorted repository-relative pathname →
file SHA-256, compact sorted-key JSON plus one newline:

| Tree | Files | SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

The accepted FC witnesses remain documented at 14,677 bytes /
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`
and 174,490 bytes /
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`.
Their accepted verification records and producing repository code are unchanged;
this proposal task does not claim a new witness acquisition or spike execution.

## 3. Live public-capability audit

Classification: **public** = authoritative within the owning carried-result
boundary, not authenticated physical truth; **derived** = pure public-material
composition; **test-only** = disposable population/helper, not runtime API;
**missing** = no accepted contract for the required semantics; **ambiguous** =
public refusal or unresolved selection; **policy** = explicit caller choice;
**inappropriate** = must not be promoted to authoritative engineering truth.

| Required input | Exact public supply and inspected evidence | Classification and limit |
| --- | --- | --- |
| Observed variable state | `ModelStateQueries.variable_state` → `VariableStateResult`; `model_revision`, `binding_revision`, variable/owner registrations, candidates and bound observation occurrences. [Facade](../../../backend/model_state/facade.py). | Public. Latest-at-cutoff evidence, not current physical truth. Absence, attachment failure and multiple selection remain ambiguous/unavailable. |
| Value and semantic nomination | `ObservationCompatibilityQueries.variable_value_compatibility` → `VariableValueCompatibilityResult`; `SemanticCompatibilityQueries.variable_semantic_compatibility` → `VariableSemanticCompatibilityResult`; exact candidate path, VSP/VSM and source interpretation. [ES facade](../../../backend/semantic_compatibility/facade.py). | Public plus caller nomination policy. No automatic preferred source or diagnostic test selection. |
| Evidence assurance | `EvidenceAssuranceQueries.select_operational_evidence`, `OperationalEvidenceSelectionResult`, public snapshot validation; scope/horizon/cutoff, selected occurrence, fingerprint, attempts, seed/reuse closure. [EA queries](../../../backend/evidence_assurance/queries.py). | Public. `complete_within_declared_horizon` describes captured attempts, not all reality or hypothesis coverage. |
| Alignment | `align_operational_evidence_with_value_compatibility` over full E and nominated VS, with independent expected fingerprint. [Derivation](../../../backend/evidence_alignment/derivation.py). | Public/derived. Exact occurrence/scope/cutoff relation, no source agreement or prediction. |
| Violated or satisfied criterion | `ConstraintEvaluationQueries.constraint_evaluation` → `ConstraintEvaluationResult`; exact CRG/VCN, ES, candidate index, `verdict`, `not_evaluated_reason`, `observed_decimal`, boundary assessments. [Facade](../../../backend/constraint_evaluation/facade.py), [contracts](../../../backend/constraint_evaluation/contracts.py). | Public. Evaluates admitted observations; it does not simulate an unmeasured value or establish a cause. |
| Behavior declarations | `ModelQueries.behavior_declaration`, `.behaviors_involving_variable`, `.behavior_assertion`; BRG `participant_variable_anchor_ids` and `rule_family`; BHD `participant_semantics`, `rule`, `evaluation_basis`, context. [Kernel contracts](../../../backend/model_kernel/contracts.py). | Public unordered two-variable equality. Directed input/output, transfer function, fault-conditioned rule and intervention semantics are missing. |
| Behavior evaluation | `BehaviorEvaluationQueries.behavior_evaluation` → `BehaviorEvaluationResult`; exact sources, carried semantic results, cohort, execution, `computed_relation`. [Facade](../../../backend/behavior_evaluation/facade.py), [derivation](../../../backend/behavior_evaluation/derivation.py), [tests](../../../tests/behavior_evaluation/test_evaluation.py). | Public `equal`/`different` only after two observed participants pass all gates. Missing observation gives `not_executed`, not an inferred output. |
| State classifications | `StateClassificationQueries.state_classification` and owning result; exact STD pins to CN and candidate paths. [Facade](../../../backend/state_classification/facade.py). | Public conjunction assessment, not exclusive/exhaustive fault modes or diagnosis. |
| Transitions | `ModelQueries.transition_declaration` and TRG/TRD endpoint STD pins; `assess_declared_transition_endpoints` with carried state/alignment results. [TA derivation](../../../backend/transition_assessment/derivation.py). | Public directed declaration and endpoint-pattern assessment, not dynamics, occurrence, action effects or future state prediction. |
| Flows/ports | `ModelQueries.flow_declaration`, `.flows_involving_port`, `.port`, `.port_interface`; FRG source/sink groups and FLD PCN/PIF pins. [Queries](../../../backend/model_kernel/queries.py). | Public declared topology. Direction is not engineering influence or causal propagation. |
| Flow-measurement relevance | `ModelQueries.flow_measurement_association` and `.flow_measurement_assertion`; FMA exact FRG/VRG/PRG/FLD/VPA/VSM pins and effective body. [FM results](../../../backend/model_kernel/flow_measurement_results.py). | Public declared relevance, not sensor transfer function, acquisition action or diagnostic utility. |
| Governing criterion | `ModelQueries.flow_operating_criterion` → `FlowOperatingCriterionResult`; applicable governing body group, exact CRG/VCN and retained FMA witness. [FC results](../../../backend/model_kernel/flow_operating_criterion_results.py). | Public. Selects or refuses explicit designation; no implicit criterion selection. |
| Dependencies | `ModelQueryMaterial.records`, `.record_at`, `.loaded()` and public loaded-model indexes; exact pins, evidence refs, `supersedes`, withdrawal targets, carried-result paths. | Public/derived. DI permits bounded declaration/decision dependency composition; dependencies known only to caller code require supplied inventory. Never infer an edge from shared names/owners/context or ordering. |
| Revision/context/identity/provenance | Full `ModelRevision` and material; typed contexts/registrations; exact binding/interpretation revisions, cutoff and occurrence; evidence/authority records. | Public within carried boundary. Corrected/withdrawn/conflicted support must retain lower reasons. Hashes cannot authenticate uncarried ledgers, source bytes or authority. |
| Neutral full-path proof population | FC, EA/alignment and BH disposable helpers and accepted integrated witness. [FC helper](../../../tests/model_kernel/fc001_slice_a_helpers.py), [BH helper](../../../tests/behavior_evaluation/helpers.py). | Test-only reusable construction patterns. Authoritative fixture has no FMA/FCD; no real equipment is established. |
| Hypotheses, fault modes and conditional predictions | No hypothesis/abnormality contract or `predict(h,t,o)` operation; numeric equality does not supply them. | Missing for Mode B; explicit assumed request-carried material for Mode A. Inappropriate as observed/model truth merely because supplied. |
| Candidate measurement actions and outcome vocabulary | Variable/port/source identities exist, but no diagnostic action, outcome set, calibration/availability/persistence semantics or complete test inventory. | Policy/request material in A; partly model population and partly missing semantics in B. A variable alone is not a measurement procedure. |
| Priors, cost, minimax preference, coverage claims | No accepted statistical/cost authority for this question. | Policy; no hidden uniform prior. Global hypothesis/candidate completeness is unknown. |

The code audit establishes a particularly important negative: BRG registers an
**unordered** pair and its only rule family is `exact_numeric_equality`; BHD has
no direction, input/output role or computed output. BH compares canonical numbers
only after exact revision, semantic locks, observation attachment and five-field
acquisition-cohort admission. Its result validator reconstructs the whole owned
derivation. A declaration of equality is a constraint to test, not a guarantee
that observations obey it: `different` is an accepted evaluated outcome.

## 4. Mode separation and what counts as derivation

**Mode A:** retain complete accepted lower facts plus an explicitly non-authoritative
diagnostic matrix. Human approval authorizes use of that matrix for the experiment,
not its truth. Every hypothesis, conditional prediction, cost and outcome-exhaustion
claim has a provenance/justification reference and epistemic label. An LLM may
have drafted text, but it is not admitted until the experiment owner explicitly
supplies/approves the exact bytes; no LLM executes during reconstruction.

**Mode B:** remove the prediction/observation-compatibility assertions supplied by
A. Keep the same nominated subject and exact model/result inputs. H1/H2 and T1/T2
may be retained only as *requested query labels* to ask what the model can support;
their assumed meanings and truth tables cannot be used as premises. Also attempt
to find public declarations that could generate/validate their meanings. Distinguish
“no model hypothesis semantics” from “explicit labels were provided.”

For every B cell, produce either a public derivation with exact premises and
rule, or `unknown` with a precise missing-property category. Copying an A cell,
reading a BHD note as executable code, interpreting a display name as a fault,
or reporting one latest observation as all future outcomes fails the mode boundary.
Mode B never silently falls back to A. Insufficient B cells mean no B ranking.

Mathematical equality may support a conditional logical statement such as
“if this equality holds and Y is v, Q equals v.” The additional premise *this
equality holds for the proposed measurement under h* is not supplied merely by
BHD existence. This proposal permits reporting that conditional as such, but
not using it to fill a B prediction cell without an admitted rule applicability,
time/domain and hypothesis premise. No private kernel algorithm is duplicated.

## 5. One disposable neutral micro-world

### 5.1 Fixed baseline and construction boundary

Use one synthetic scalar monitoring case, not a printer diagnosis. It has one
entity, two logical participant ports and a declared logical flow, a nominated
measured-actual variable Y, and one exact governing criterion A: Y ≤ 50 inclusive.
The scripted source observation is Y = 60.1, so admitted CN reports `violated`.
The unit/quantity identity is explicit and identical in VSP/VSM/VCN/interpretation;
temperature/degree-Celsius is acceptable but makes no equipment claim.

Build through `build_record`, public identity/record constructors, `ModelStore`
in a temporary directory, public binding/interpretation/source/temporal production,
and the FC/CN/EA/alignment public join. Reuse the patterns in the existing helpers,
not their device-specific default meanings. The future temporary driver must
parameterize neutral namespace/source/subject labels at construction, preserve
the adapter's actual provenance and use scripted transport only. It must not
rename already-produced IDs/occurrences or retrofit neutral labels into signed/
content-bound results. Any helper hard-coding `demo-printer`/`printer-1` must be
used only as a construction reference, not evidence about real equipment.

The future builder freezes **one exact complete ModelRevision R** and its full
record-ID tuple before producing either mode; both modes receive byte-identical
lower inputs. R is the computed content-derived revision of this not-yet-built
disposable world, not the authoritative 36-record revision or a fabricated hash.
The experiment receipt must print the full R and all fingerprints. One exact
context is `LifecycleViewContext(kind='lifecycle_view', view='as_designed')`.
Use explicit receipt cutoff C = `2026-08-07T21:00:00+00:00`, receipt
`2026-08-07T20:00:06+00:00`, and EA horizon `[19:00:00,21:00:00]` UTC on that date.
Model recorded-at time does not become a temporal cutoff filter: membership is
explicit. Source-effective time remains separately disclosed.

Admission requires applicable FC, its exact governing CRG/VCN matching CN,
candidate 0 explicitly nominated with exact occurrence, complete EA coverage,
and matched independent expected fingerprint/attached alignment to N's carried VS.
If caller receipt-usability policy is included, retain the exact approved test
profile: inclusive maximum age 3,600 seconds and complete two-hour attempt horizon;
age 3,594 seconds passes. These are synthetic experimental assumptions, not
operational commissioning defaults. No stable CV application is created.

### 5.2 Hypotheses and nominated measurements

H1 and H2 are local experiment labels, not engineering anchors:

- **H1:** “high underlying-level / faithful baseline-channel explanation.”
- **H2:** “low underlying-level / positive baseline-channel-offset explanation.”

Their numerical intuition (60.1 + 0 versus 40 + 20.1) is an explicitly supplied
toy justification, not an accepted transfer equation or a claim that either is
the cause. Both assert compatibility with the exact observed Y = 60.1 and CN A
`violated`. Their required baseline checks refer to those public result paths.
There is no claim of complete fault coverage, mutual exclusivity in reality,
or probability. Viability means passing the supplied finite checks only.

**T1:** a nominated reference-channel scalar measurement concerning Y's case;
outcomes `low` (finite numeric value ≤ 50) and `high` (> 50). Exact reference-method
label, unit, value-to-outcome rule, hypothetical sampling scenario, calibration
and hold assumptions are request-carried. No reference sensor is asserted installed
or available. These assumptions make T1 informative in A; their absence is visible in B.

**T2:** a nominated nonspecific two-code indicator measurement for the same case;
outcomes `code_a` and `code_b`, exact literal codes under a supplied decoding rule.
Both hypotheses explicitly permit either code. The candidate is associated with
this experiment by an explicit request reference, not by shared entity/context.
Its acquisition procedure/availability is assumed, not inferred from a port or
variable registration. T1/T2 remain unexecuted candidate procedures, not observations.

This minimum uses one observed model variable and two experimental measurement
descriptions. Registering extra prospective variables would not supply the missing
procedure/outcome/prediction semantics. It is not necessary for A. B must disclose
that limitation rather than pretending those descriptions are model facts.

### 5.3 Complete matrix and hand-derived oracle

Every cell is an explicit `permits` or `excludes` statement, labelled **assumed**
with justification; a blank is never `excludes`.

| Hypothesis | T1 low | T1 high | T2 code_a | T2 code_b |
| --- | --- | --- | --- | --- |
| H1 | excludes | permits | permits | permits |
| H2 | permits | excludes | permits | permits |

The request carries explicit justification records: J1 is the assumed calibrated
reference/hold rule connecting T1 low/high to the conjectured underlying level;
J2 is the assumed nonspecific-indicator rule allowing either T2 code under either
hypothesis. Each T1 cell references J1 plus the full H1/H2 statement; each T2 cell
references J2 plus that statement. The hypotheses' baseline expectations cite
the exact Y occurrence and CN A row, but those citations do not substantiate the
latent level or offset conjecture. J1/J2 and the conjectures remain assumed,
approved only for the experiment, with an explicit supplying actor and rationale.

Both baseline checks pass, so H = {H1,H2}. The four survivor sets are
S(T1,low)={H2}, S(T1,high)={H1}, and S(T2,code_a)=S(T2,code_b)={H1,H2}.
Worst-case survivors are respectively 1 and 2; guaranteed reductions are 1 and 0.
T1 is the unique best discriminator within this matrix; no outcome occurred.

The same world has these explicitly separately identified variants:

| Variant | Exact change in temporary request | Expected result |
| --- | --- | --- |
| Tie | T2 permits only code_a under H1 and only code_b under H2. | Both scores 1; disclose {T1,T2}, no ID-based winner. |
| Incomplete | Replace cell (H2,T1,low) by `unknown` with missing-justification reason. | Refuse full-set ranking; do not treat unknown as exclusion or silently recommend T2. |
| One survivor | Change H2's baseline expected CN verdict to `satisfied`, with explicit new hypothesis content/commitment. | H2 inconsistent with actual violated A; H1 remains, but no discriminating test recommendation. |
| No survivors | Both hypotheses explicitly require CN A `satisfied` while carried CN A is validly `violated`. | Both inconsistent; no viable supplied hypothesis, no minimax ranking or “true cause.” |
| Model-rule conflict | Populate a small BH exact-equality control in the same disposable construction: second registered scalar, valid locks and observed source from the same acquisition cohort. Rebuild R for this separately frozen variant. A hypothesis asserts `different` for an actually admitted BH `equal` result. | Reject that hypothesis using the exact BH result path; valid twin asserts `equal`. Do not inject predictions as synthetic BH observations. |

The BH control uses the public construction patterns and equal/different tests
already inspected. If cohort, quantity/role/unit, attachment or observation
admission fails, the control is `not_executed` and cannot reject a hypothesis
as false; record an unavailable prerequisite. No variant mixes its R with another.

### 5.4 Epistemic accounting

| Material | Classification |
| --- | --- |
| Captured synthetic Y occurrence | Observed within the disposable evidence world, explicitly synthetic; not real equipment truth |
| VRG/VSM/VSP, flow/port/FM/FC/VCN and optional BH rule | Declared, backed by the disposable declaration authority |
| CN verdict, BH comparison, alignment, receipt age, S sets and scores | Calculated from exact carried inputs under named public/experimental rules |
| Hypotheses, predicted outcome relation, method availability/calibration/hold, cost | Assumed; provenance and explicit approving experiment actor retained |
| Surviving/rejected hypothesis and preferred/tied measurement | Inferred relative to supplied assumptions and calculated comparisons; not actual cause |
| Actual cause, missing hypotheses/tests, real availability, absent B prediction premises | Unknown |

Each individual assertion has its own label/source references; a container label
must not relabel assumed prediction cells as observed evidence.

## 6. Algorithm comparison

| Approach | Required semantics and honest contribution | Decision for this spike |
| --- | --- | --- |
| Deterministic diagnostic matrix / minimax discrimination | Explicit finite compatibility sets and baseline consistency checks; minimize worst-case survivors, no probabilities. | Selected. Eight main cells, exact integers, transparent exhaustive derivation. |
| Uniform-prior information gain | Requires an explicit uniform hypothesis prior; nondeterministic predictions additionally require outcome likelihoods, not merely permission sets. | Not default. Uniformity is a substantive assumption and likelihoods are absent. |
| Explicit-prior Bayesian information gain | Requires authorized priors and normalized conditional likelihoods P(o\|h,t), plus updating semantics. | Reject for now; no such evidence/policy. A compatibility bit is not a likelihood. |
| Reiter-style diagnosis / minimal conflicts | System description, observations and component normality/abnormality semantics; consistency/conflicts and minimal diagnoses relative to that model. | Premature for two supplied H rows. Current BRG/BHD are not fault assumptions, and no conflict/minimality semantics may be invented. |
| CSP or SAT/SMT | Encoded variables/domains, constraints, alternative hypotheses and theory semantics. | No solver dependency. Finite enumeration is sufficient; solver satisfiability would still depend on supplied semantics. |
| Dependency-graph backward slicing | Explicit record/computation edges can locate potentially relevant inputs. | Useful provenance aid only. Reachability neither generates hypotheses nor supplies predicted outcomes/discrimination. |
| Hybrid: public fact admission + supplied matrix + minimax | Accepted layers validate engineering/evidence facts; tiny experiment validates its own assumptions/joins and computes sets. | This is the selected boundary, not a second inference engine or graph package. No Bayesian/solver stage. |

Entropy and conditional entropy require probabilities; assigning equal weights
cannot be hidden under a “neutral” information-gain score. This follows the
probability-based definitions in [Shannon's original paper](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf),
sections 6 and the conditional-entropy discussion. Reiter's framework explicitly
relates diagnoses to a system description and observations through consistency
and minimality; a list of externally supplied compatible scenarios is not that
algorithm. See [Reiter's original paper](https://www.cs.ru.nl/P.Lucas/teaching/KeR/Theorist/reiteraij87.pdf).
These references inform the comparison only; no external challenger or solver
has been used. The selected minimax rule is defined completely below.

## 7. Exact minimax semantics and result vocabulary

Algorithm name/version, local to the experiment: `finite_compatibility_minimax/v1`.
Policy is explicit: `prior=none`, `candidate_scope=explicit_supplied_set`,
`missing_cell=refuse_comparison`, `secondary=none` or `minimum_cost_after_minimax`.
No implicit default may be used when a field is absent.

Let H be the supplied hypotheses whose required finite baseline checks are known
and consistent; T the admitted supplied measurement set. For every t and o:

`S(t,o) = {h in H | compatible(h,t,o) = permits}`

`worst(t) = max(|S(t,o)| for o in O(t))`

`reduction(t) = |H| - worst(t)`

Minimize worst(t). Do not multiply probabilities, prefer a hypothesis by ID,
or maximize favorable-case elimination. Retain every S row and its contributing
cell references, not just the winning score.

Admission and edge cases are exact:

1. Require unique hypothesis/test labels, exact outcome vocabularies, and one
   explicit cell for each supplied h,t,o. `unknown` is a representable missing
   prediction, not false. Missing/unknown cells anywhere in the supplied matrix
   prevent full-set ranking, including rows for later-refuted hypotheses; this
   conservative first-spike policy prevents selective omissions.
2. Every h,t must permit at least one outcome. An all-excluded row is an invalid
   predictive model for an admitted measurement, not a magical hypothesis elimination.
3. An outcome permitted by no H has S=empty and count 0. Preserve it as an
   **unexplained outcome under supplied hypotheses**, not a physically impossible
   outcome or a useful confirmation. It does not by itself invalidate a complete
   matrix. If that outcome were later actually observed, return no viable supplied
   hypothesis and require hypothesis/prediction review; do not choose a cause.
4. Nondeterministic hypotheses may permit multiple outcomes. Survivor sets may
   overlap; they need not partition H. Minimax still uses their cardinalities.
   No uniform probabilities over those outcomes are invented.
5. The outcome alphabet is explicitly exhaustive only within the supplied test
   abstraction. T1 has complete finite numeric low/high mapping under its unit;
   malformed values, missing observations and failed acquisition are separate
   unavailable-input states, not forcibly mapped to low or assigned zero probability.
6. No viable hypotheses: no score/recommendation; report the exact conflicts.
   One viable hypothesis: report conditional survival and `no_discrimination_needed`;
   never “cause proven.” Validation still checks the supplied request, but ranking
   is not needed to identify which test distinguishes one member from itself.
7. With ≥2 H but best reduction 0, disclose scores and `no_discriminating_measurement`.
   Even a cheaper test is not recommended as a discriminator. T2 alone exemplifies
   this only in a separately authorized singleton-candidate request, not by silently
   dropping T1 from the original two-test experiment.
8. Equal minimum scores retain the entire primary best set. With secondary `none`,
   disclose a tie. Explicit cost policy may select the least-cost members of the
   primary best set only; report both sets, costs and policy. Equal costs remain tied.
   Never trade worse worst-case discrimination for lower cost in v1.
9. Cost is optional only when secondary=`none`; then costs must be absent, not
   silently used. For cost tie-breaking require all candidate costs in one explicit
   artificial unit, integer strings `0` or `[1-9][0-9]*`, 0…100 inclusive. Reject
   Boolean/int/float coercion, negative, non-finite, fractional, excessive or
   missing costs and mixed units. Zero is valid, not unknown. No cost normalization.
10. Presentation order is ASCII local label order, then outcome order. Stable labels
    may sort a tied set, but the first row must not be marked selected. Lower arrays
    preserve their accepted canonical order; no sorting may repair forged lower rows.

Separate axes: admission; baseline evidence usability; per-hypothesis consistency;
matrix completeness; model-derivation availability; measurement ranking. Primary
terminal experiment statuses, in precedence order, are:

| Status | Exact meaning |
| --- | --- |
| `input_refused` | Malformed, hostile, over-budget, substituted, incoherent or wrongly claimed authoritative input; retain bounded diagnostic code. |
| `baseline_unavailable` | Valid lower refusal/ambiguity, FC not applicable, CN not evaluated, or explicit receipt/coverage admission not met. Preserve lower reason; not hypothesis falsity. |
| `baseline_not_violated` | Admitted governing A is satisfied; this spike's triggering question is absent. Not input corruption. |
| `model_semantics_unavailable` | B cannot derive required hypothesis/prediction/test semantics. Enumerate cells/premises; no B ranking. |
| `insufficient_information` | A has unknown required baseline checks, incomplete/unknown predictions or unestablished admitted candidate scope; no full-set winner. |
| `no_viable_hypotheses` | Complete admitted finite checks refute every supplied hypothesis. |
| `no_discrimination_needed` | Exactly one checked hypothesis remains; no test preference. |
| `no_discriminating_measurement` | ≥2 hypotheses, complete admitted matrix, best reduction 0. |
| `preferred_within_supplied_set` | Positive best reduction and one final best member under explicit policy. |
| `tied_best_within_supplied_set` | Positive best reduction and ≥2 final best members; no arbitrary winner. |

Per hypothesis: `compatible_with_supplied_facts`, `inconsistent_with_supplied_facts`,
or `unresolved`; keep both conflicts and unknowns if present. A known contradiction
can refute a hypothesis despite another unknown, but any unknown required matrix
cell still blocks the original comparison. These are experimental labels, not
new public backend enums or engineering verdicts.

## 8. Mode A procedure and complete explanation trace

The future disposable algorithm follows this deterministic procedure:

1. Preflight bytes, nesting and declared/actual cardinalities before constructing
   lower models or expanding compatibility cells. Check exact expected experiment
   input commitment independently; reject cycles/hooks/hostile objects.
2. Revalidate complete carried lower roots at public owning boundaries. Reconstruct
   FC material, match full CRG/VCN and relevant model facts in CN/VS/VM, and derive
   alignment from N's carried VS and E. Independently match revision, context,
   variable/owner, flow/port/orientation, occurrence, cutoff and fingerprint.
3. Admit the exact evidence-backed violated governing criterion. Valid refusal is
   unavailable, not `violated`; satisfied ungoverned B can never replace governing A.
4. Parse only the tiny fixed assertion vocabulary: exact observed-value equality,
   exact CN verdict equality, optional exact BH computed-relation equality, and
   exact declared-record membership/currentness via public query result. Every
   assertion points to a typed root/path and explicit expected value. No arbitrary
   JSONPath evaluation, expression language, model note execution or theorem prover.
5. For each H, compare all supplied required assertions to admitted facts. Reject
   contradictions with both exact values and provenance; preserve unknowns/refusals.
   A hypothesis is not exempt from a model rule merely because it calls itself a fault.
6. Validate the complete outcome/prediction matrix, epistemic labels and explicit
   policy. Compute every S set and score if eligible; apply only the admitted
   cost secondary policy, then produce the complete derivation.

The “why?” result must say:

> These hypotheses remain compatible with the supplied observations,
> declarations, behavior rules, and assumptions.

For every H retain exact supporting occurrence and semantic path, evaluated
VCN/CN path, every BH/model rule actually used (or explicit empty list), caller
assumptions/justifications, each rejected expectation versus actual finding,
unavailable dependencies, R/context/C and scope limitations. If no BH rule is used
in the minimum case, say so; do not invent a mechanism to make the explanation
sound stronger. Compatibility is a bounded consistency test, not a causal discovery.

For a preference the permitted statement is:

> Within this explicitly supplied candidate set and prediction matrix,
> measurement T1 provides the best worst-case discrimination under
> finite_compatibility_minimax/v1 and the supplied policy.

Include |H|=2, scores 1/2, guaranteed reductions 1/0, all survivor sets, both
primary/final best sets, cost policy, every assumption, inadmissible/excluded test
and reason, unknown cells and unknown global coverage. An excluded test cannot
be omitted while still claiming best over the original complete supplied set;
v1 refuses that comparison and requires a separately nominated smaller request.
No proposed outcome is ingested and no hardware command/acquisition occurs.

## 9. Mode B derivation probe and expected missing premises

For exactly the same R and lower roots, run this bounded inventory/derivation
probe, not a generic graph traversal:

| Matrix element | What B can obtain | Missing premise or expected refusal |
| --- | --- | --- |
| Trigger and baseline value | Exact FC applicability and governed CN violation; observed Y, unit, semantics, C and alignment. | No missing lower field for this admission. |
| Candidate subject/reference | Registered Y, explicitly declared flow/port relevance and exact support pins. | No method availability, calibration, outcome alphabet or full test inventory follows. |
| H1/H2 meaning | Can check exact cited records and contradictions with admitted facts if the expectations are supplied. | Cannot generate high-level/fault alternatives or their expected facts from names, VCN violation or notes. Hypothesis/fault-mode semantics absent. |
| T1 predictions | Numeric VSP/VCN gives value shape and predicate, not P(outcome\|H1/T1) or a set-valued equivalent. | Reference-method/underlying-level relation, hypothesis-conditioned executable prediction, domain/time applicability and calibration/hold assumptions absent. |
| T2 predictions | No public code-indicator diagnostic procedure/alphabet in the minimum material. | Partly missing candidate population; adding a nominal registration still would not imply compatibility with each hypothesis. |
| BH relationship | Unordered participants and exact equality declaration; current equal/different evaluation when two observations are admitted. | No directed transfer, fault-conditioned output prediction or temporal persistence. Cannot forge an unobserved participant to execute BH. |
| Dependencies | Exact explicit support/provenance/lifecycle/query joins are reconstructable. | No engineering influence or hypothesis-conditioned measurement prediction follows from reachability. |
| Score/cost/tie policy | Finite minimax is independent of kernel once a complete matrix exists. | Cost/policy authority stays supplied; no implicit prior or preference is derivable. |

A controlled population probe is allowed only inside the future disposable world:
add a valid BH pair/locks and, where needed, second observed participant through
existing constructors. It can show `equal`/`different` and result-based hypothesis
rejection. It cannot manufacture an input/output prediction API. Similarly a
registered extra measured variable fixes its identity/population absence, not a
reference-method model. Record separate “contract permits but not populated” and
“contract cannot express this premise” columns.

For unsupported requested B cells retain `unknown`, exact attempted public paths
and one or more categories: `engineering_influence_semantics`,
`behavior_input_output_semantics`, `executable_prediction`, `hypothesis_generation`,
`fault_mode_representation`, `measurement_candidate_representation`,
`model_population`, `application_policy`. Do not count mere lack of a directed
edge as the cause of every B failure: this matrix may require predictions and
fault assumptions even with a perfect directed graph. No missing value is inferred
as incompatible. Expected B terminal status is `model_semantics_unavailable`.

## 10. Disposable envelope, authoritative reconstruction and tiny budgets

### 10.1 Reproducibility without a durable contract

Use a local experiment request/result JSON envelope only in the separately
authorized spike. It is not exported from `backend`, appended to a ledger, or
assigned a permanent engineering identity. Local H/T/statement labels are scoped
to the full request content, not globally reusable names.

Request retains: experiment format and algorithm versions; A/B mode; exact R
and full lower roots; context/C; independent expected source/model/candidate/
policy commitments; hypothesis assertions; candidate procedures; outcome sets
and decoding assumptions; every compatibility cell and justification; ephemeral
authority/provenance references; classification per statement; cost/tie policy;
scope declarations and resource limits. A mode-specific content digest binds the
complete request. A and B share an equal lower-material digest but distinct mode
requests; B cannot carry A predictions as hidden premises.

Result carries its request once, ordered hypothesis checks/conflicts/unknowns,
per-cell derivations, S sets/scores and primary/final best sets, status/reasons,
epistemic labels and explicit limitations. For the base public join retain full
FC F, CN N and EA E once and derive alignment L from E and N's nested VS; do not
also carry detached VS/ES/VM copies. Optional BH control carries its complete
public result as one root and preserves any repetition required by that lower
schema; it is not a license to strip or reconstruct lower material differently.

Replay validates lower results through their owning public operations and recomputes
the experiment's equality checks, cell domain, sets, scores, costs and status.
It opens no file/store/network, reads no clock/environment, runs no solver/LLM,
and queries no hardware. Explicit disposable setup may use temporary stores and
scripted acquisition to produce the baseline, but that phase is not reasoning
or candidate-measurement execution. The prediction table never becomes a temporal
observation or a crafted CN/BH evidence result.

Canonical JSON is useful as a reproducibility checksum: UTF-8, sorted object keys,
compact separators, no newline, no NaN/Infinity, fixed explicitly ordered arrays;
lower schema serialization/content remains intact. Experimental scalars use strict
integers or canonical strings, no floats for scores/costs. Exact finite floats
required by carried lower schemas retain the owning public serialization, not
custom rounding. Reject duplicate JSON keys and hidden fields before decoding/
dumping loses them. Expected full request digest is retained outside the submitted
object; a substituted hypothesis plus its newly computed self-hash is not trusted.
The checksum is not an authority signature, source authenticator or durable ID.

### 10.2 Deliberately tiny ceilings

These are deliberately small proposed experiment caps, not measured performance
claims and not limits inherited from TA/EA/DI. All must be checked before expensive
lower reconstruction or compatibility expansion. Exceeding a cap refuses the
whole request with a bounded code; no truncation or selective omission.

| Dimension | Proposed maximum and reason |
| --- | --- |
| Supplied hypotheses | 2; exactly the proof's two candidates, not hypothesis search |
| Candidate tests | 2; main proof requires both; explicit singleton variants only test no-discrimination |
| Outcomes per test | 3; two main outcomes, one optional unexplained-outcome adversarial variant |
| Compatibility cells | 12 = 2×2×3; main proof has 8, preflight actual cross-product before constructing sets |
| Required fact checks per H | 4; value, CN, optional BH, optional exact model support |
| Explicit supporting model-record references per H | 4; full closure is carried separately, not pruned to this cap |
| Full disposable model records | 32; enough for the small FC construction and controlled BH population, not the authoritative fixture |
| Lower roots | 3 base roots F/N/E; at most one complete optional BH result |
| Additional assumption/justification statements | 24 total; 512 UTF-8 bytes per text; local labels ASCII 1–32 bytes |
| Derivation depth | 4 experimental reference levels; no recursive theorem/graph search; lower nesting has a separate cap |
| Serialized JSON nesting / expanded nodes | 48 / 12,000 across the full request, counting repeated lower content; cycles and hooks refused |
| Request bytes | 524,288 (512 KiB), checked before parsing; deliberately above inspected ~71 KiB FC/N/EA witness roots with room for the small BH control |
| Result bytes | 786,432 (768 KiB), including request once; preflight worst-case trace bound before reconstruction, verify final encoded size |
| Cost | Canonical integer string 0…100 in one supplied artificial effort unit; no physical cost claim |

The future spike must measure actual bytes/nodes/depth and reconstruction time
for base, BH variant and at-limit/one-over inputs before accepting these caps.
If an accepted lower world exceeds them, stop and report which dimension, rather
than silently enlarging a budget or stripping proof. This would be a capacity
choice, not automatic evidence for new architecture. Preflight raw JSON bytes,
bounded parser depth/token counts, and outer lengths before Pydantic construction;
never trust attacker-supplied declared counts. For in-memory input accept only
exact built-in JSON types, rejecting custom objects/`model_construct`/`model_copy`
instances at the envelope boundary; trusted callers must first supply bounded
plain content. Then owning lower validators reject stale IDs and forged nested
results. Retain lower array order, strict indices and exact revisions/cutoffs.

For result preflight reserve at most 131,072 bytes for the generated trace and
1,024 bytes for envelope framing beyond the canonical request. Verify that the
canonical request size plus both reserves fits 786,432 bytes before lower
reconstruction. Derivation text uses fixed templates, bounded codes and references
to once-carried assumptions, never unbounded exception text or copied payloads.
The future implementation must prove its trace bound against the fixed row/text
limits, then check actual output size; inability to prove that bound stops the
spike rather than weakening preflight. No production latency promise is made.

Only O(|H|×sum |O(t)|) cells are examined: at most 12 plus 8 baseline checks.
Output all paths in this fixed derivation, not arbitrary graph paths. Stable
ordering must reproduce identical request/result bytes across hash seeds 1, 7,
and 313; no ambient timestamp may enter the calculated result.

## 11. Spill register

S = structural prevention; R = runtime refusal/check in the future spike;
D = explicit disclosure; L = remaining limitation. These are proposed guards,
not a claim that an unimplemented experimental validator already exists.

| ID | Spill | Guard |
| --- | --- | --- |
| SP01 | Hypothesis presented as fact | R/D: per-statement assumed label; reject observed/authoritative label without matching public provenance. Compatibility is conditional. |
| SP02 | Prediction presented as observed outcome | S/R: matrix namespace never passed to temporal/CN/BH evidence producers; predicted branches remain unexecuted. |
| SP03 | Computational dependency presented as physical influence | D/R: typed record/result references only; no inferred engineering edge. |
| SP04 | Influence presented as causality | D/L: no causal claim or intervention semantics; even a future influence relation would need its own meaning. |
| SP05 | Best-within-set presented as globally best | R/D: explicit bounded candidate scope and unknown global completeness mandatory in result. |
| SP06 | Uniform probability introduced silently | S/R: prior=`none`; no entropy/likelihood computation or probability fields admitted in minimax v1. |
| SP07 | Tie broken silently | R: recompute full primary/final sets; IDs sort presentation only; explicit cost secondary or disclosed tie. |
| SP08 | Incomplete prediction becomes incompatibility | R: `unknown` is not `excludes`; missing/unknown matrix cell refuses full-set ranking. |
| SP09 | Unknown hypothesis coverage called complete | D/R: scope is the supplied finite list; reject a global-completeness assertion. |
| SP10 | Assumptions persisted as model truth | S: temporary envelope only; no kernel records/ledger append for hypotheses or predictions. |
| SP11 | Application policy enters lower layers | S: no lower changes/imports; experiment compares public results and owns only temporary scoring policy. |
| SP12 | Solver/calculated result presented as safety/health | S/D: no solver or safety output; neither consistency nor minimax is an operating permission. |
| SP13 | Synthetic printer helper treated as engineering knowledge | R/D: neutral disposable construction and compulsory synthetic disclaimer; retain literal provenance, never relabel protected results. |
| SP14 | Lower validation duplicated incorrectly | S/R: public owning validators and queries; no private lifecycle/canonicalization/evaluation copies. |
| SP15 | Hidden filesystem/store/network/device access | S/R: replay accepts complete plain inputs, no readers; forbid I/O/clock hooks in future isolation checks. Setup is separately identified scripted production. |
| SP16 | Unbounded search | R: tiny preflighted counts/bytes/nodes/depth; no recursive graph or solver search, no truncation. |
| SP17 | Nondeterministic output | R: canonical strings/integers, fixed ordering and cross-hash-seed byte checks; never select by set iteration. |
| SP18 | LLM hypothesis becomes accepted engineering declaration | S/R/D: explicit experiment-owner approval/assumed label; no live LLM, no accepted truth inferred from approval. |
| SP19 | Equality declaration treated as guaranteed transfer equation | R/D: BH reports observed equal/different; applicability of an unobserved prediction remains unknown without extra semantics. |
| SP20 | Mode A assumptions leak into Mode B | S/R: distinct requests/digests; B premise allowlist public material only, unknown cells preserved. |
| SP21 | Confidential data/absolute paths leak through a proof | R/L: synthetic bounded inputs only; value-free errors and no credentials/absolute paths in output. No claim of a production confidentiality boundary. |
| SP22 | Refusal or zero survivors becomes evidence falsehood | R/D: separate baseline admission, hypothesis inconsistency, matrix completeness and ranking; unknown reality remains unknown. |

## 12. Threat cases and valid twins

These are design oracles for the future spike, not newly implemented tests.
Every refusal has a coherent, explicitly authorized valid twin.

| Case | Attack or challenge and required result | Valid twin |
| --- | --- | --- |
| T01 | T1 separates H1/H2: S={H2}/{H1}, worst=1; forged score 0 refuses. | Exact score 1, both branch traces and unique T1 preference. |
| T02 | T2 leaves both viable for either code: worst=2; cannot be called informative. | Retain both overlaps and zero reduction; with T1 present prefer T1. |
| T03 | Equal-score tie: choosing lexically first silently refuses. | Both best labels retained; or explicit complete cost policy resolves only the primary tie. |
| T04 | Missing/unknown prediction cell: no false exclusion, full comparison insufficient. | Supply the exact justified assumed cell under a new independently approved request commitment. |
| T05 | Duplicate hypothesis/test label or cell: input refused even if content matches. | Unique local labels and exactly one cell per cross-product member. |
| T06 | Forged observation/CN result: full public reconstruction or independent expected join refuses. | Correct complete F/N/E with governing violated A and attached matched evidence. |
| T07 | Mixed revision/context/cutoff: refuse, no most-recent selection. | One exact R/context/C across admitted model-bearing and temporal roots, including a valid explicitly historical request. |
| T08 | Same H1 label with substituted meaning/table and self-updated digest: refuse against independent expected full request. | Explicitly approved new hypothesis content and new external commitment; its request checksum is not an engineering identity. |
| T09 | Boolean index or cost: strict input refused before lookup/coercion. | Integer candidate index 0; canonical cost string `0` under explicit cost policy. |
| T10 | NaN/Infinity, negative, fractional, excessive or mixed-unit cost: refuse. | Complete same-unit strings `0` and `100`; exact equal costs remain a tie. |
| T11 | Hidden uniform prior/averaged outcome score: wrong algorithm/policy refused. | Pure worst-case integer counts; probability-based experiment would need a separately approved explicit probability model. |
| T12 | Outcome outside vocabulary or incompatible decoder/unit: refuse cell/domain admission. | Exact low/high numeric decoder in the declared unit and code_a/code_b literal decoder. |
| T13 | Outcome allowed by no H: cannot claim physically impossible or use it to prove a cause. | Retain empty S and unexplained-outcome disclosure; observed later in a separate replay would produce no viable supplied H. |
| T14 | One H remains: an asserted optimal diagnostic test refuses. | `no_discrimination_needed`, remaining H conditional, no cause claim. |
| T15 | Zero H remain: arbitrary fallback explanation/test refuses. | `no_viable_hypotheses` with both exact contradiction traces; restore one consistent H for the one-survivor twin. |
| T16 | Incomplete candidate inventory called globally complete: refuse that assertion. | Explicit supplied scope with global coverage unknown; complete predictions within that bounded scope. |
| T17 | Reordered object keys/hash-seed iteration changes winner or bytes: fails reproducibility oracle. | Canonical envelope byte-identical for seeds 1/7/313; lower arrays never arbitrarily reordered. |
| T18 | Hostile huge dimensions/bytes, cycles or hidden object hooks: refuse before cell/lower reconstruction. | At-limit tiny plain JSON inputs; one-over counterpart refused, no partial result. |
| T19 | Supplied hypothesis expectation says admitted BH `different` while public BH computes `equal`: hypothesis inconsistent, not override of rule. | Expected `equal` with same exact BH proof. For an unobserved future branch, BH cannot evaluate: report missing prediction semantics rather than fabricate this contradiction. |
| T20 | Assumed H/prediction labelled observed: input refused as epistemic/provenance incoherence. | Explicit assumed labels, provenance/approval, observed label only on carried occurrence facts. |
| T21 | All outcomes excluded for one h,t: invalid prediction row cannot eliminate h artificially. | At least one permitted outcome; nondeterministic multiple permissions are also valid. |
| T22 | A table copied into B and called model-derived: mode boundary refused. | B unknown cells with named missing premises, separately successful A ranking. |
| T23 | Satisfied ungoverned B replaces violated governing A: exact whole CRG/VCN join refuses. | Governing A violation remains admitted; a truly different designation requires a separate valid request/revision. |
| T24 | Lower `not_executed`, EA refusal or policy age denial treated as hypothesis contradiction: refuse the derivation. | Preserve `baseline_unavailable` with lower reasons; separately admitted complete evidence permits actual consistency checks. |

## 13. Exact decision gates and interpretation

These gates are classifications of future experimental evidence, not allocations
or automatic authority to implement milestones. Multiple missing-premise gates
may apply; report each, never force a single vague “reasoning gap.”

| Gate | Required experimental evidence | Consequence |
| --- | --- | --- |
| 1 — Existing model sufficient | B derives every required hypothesis/prediction/outcome premise from public material, reproduces full S sets and correct minimax result without A leakage; all integrity/refusal twins pass. | Recommend a separately owner-gated bounded reasoning implementation. IN-001 is unnecessary for this proven question. Smallest candidate boundary is pure finite calculation over public results, not a durable layer; runtime placement remains a later decision, not authorized here. |
| 2 — Influence semantics missing | A concrete B derivation needs a directed engineering relation absent from explicit accepted contracts; identify exact source, target, condition and consequence, and show that adding only that premise enables a previously blocked step. | Recommend investigating IN-001 only for that relation after owner approval. No generic influence ontology. Absence of direction in BH alone is insufficient to pass this gate. |
| 3 — Prediction semantics missing | Dependencies/identities are available, but no rule yields allowed outcomes for h,t under the specified scenario. | Name the missing conditional diagnostic/prediction relation, fault/normal-mode applicability, domain and temporal assumptions. Do not mislabel it DI/change-impact traversal or claim an edge fixes it. Expected principal B gap. |
| 4 — Hypotheses missing | Public material cannot generate or validate the meanings of H1/H2 or their fault assumptions, though it can check explicitly supplied expectations. | Keep hypotheses request-carried and assumed for the spike. Human/LLM proposal approval is not an accepted engineering declaration; any later representation needs separate justification. |
| 5 — Population missing | An accepted public contract genuinely supports the required semantics and adding valid disposable content makes the blocked derivation work without new rules. | Use a bounded disposable/synthetic world, not new architecture or authoritative ledger append. Empty FMA/FCD fixture counts are this kind of issue for the lower join, not for conditional predictions. |
| 6 — Only application packaging missing | A full equivalent reasoning answer, not merely FC/CS evaluation, already exists and is reproducible through current operations/tests. | Stop redundant reasoning work; retain CV's concrete consumer prerequisites. No wrapper or implied delivered capability. Current audit did not find this answer. |

Mode A failure of arithmetic/set/tie or integrity cases is an algorithm/design
failure to repair or stop, not evidence for IN/CI. Failure due to absent admitted
baseline facts is a lower-admission/population problem. A success with B correctly
refusing unsupported predictions is an informative feasibility result, not full
model-derived reasoning closure. No architecture milestone follows automatically.

## 14. IN-001, CI-001 and original objectives

IN-001 and CI-001 are unallocated potential investigations here; neither is begun,
reserved or designed in full. Declaration dependency and engineering influence
remain distinct. Public BH equality supplies an undirected relation, while flow
source/sink direction supplies declared topology; neither establishes a directed
physical response, propagation magnitude, mechanism or causal intervention.

IN-001 is **not demonstrated necessary** for this minimax experiment. Gate 2 would
require an exact missing engineering relation and a controlled proof of its value;
if the missing object is really compatibility(h,t,o), a generic influence edge
is insufficient. CI-001, if later justified for bounded hypothesis elimination
and test scoring, would initially be a reasoning algorithm over explicit inputs,
not a durable model layer or a true-cause detector. Gate 1 success or an exact
algorithmic consumer need plus supplied validated prediction semantics could
justify a separate proposal; missing model predictions alone does not authorize
causal-inference implementation. Owner authorization is required in every case.

| Objective | Spike-level success criterion and honest limit |
| --- | --- |
| 1. What exists/how connected? | Preserve exact public identities, context and declared links in every derivation; no new topology capability. |
| 2. Current state? | Begin from one admitted evidence-backed governed violation at C; no new application delivery or present physical-state claim. |
| 3. Why this behavior? | Correctly retain two compatible supplied explanations, reject the explicit inconsistent variants with exact conflicts, and expose unknown premises. This tests bounded candidate consistency, not cause generation or proof of actual cause. |
| 4. Next best measurement/test? | Compute T1 worst=1 versus T2 worst=2; preserve a valid tie and refuse incomplete predictions. This is a new algorithmic within-set discrimination proof, not globally best-test selection or acquisition. |
| 5. Change impact? | No closure. Later forward counterfactual slicing would need explicit action/change and influence/prediction semantics; declaration reachability alone is not physical impact. |
| 6. Smallest desired-state change? | No closure. Later work would require explicit action sets, effects, feasibility and optimization criteria; this spike has none. |
| 7. Epistemic distinctions? | Every input/derived statement labelled observed/calculated/declared/inferred/assumed/unknown with exact provenance; reject assumed-as-observed and unknown-as-incompatible attacks. No source authentication or complete knowledge claim. |

Success is measured by these decisions and refusal oracles, not record counts,
contract count, new exported names or a larger fixture. Even a successful spike
would provide architecture/test evidence, not a delivered application workflow.

## 15. Smallest owner-gated execution and stopping rules

No implementation occurs in this proposal task. If separately approved:

1. In one disposable experiment workspace, construct/freeze the neutral baseline
   and complete public roots using accepted builders; measure limits and verify
   the exact governing violation. No authoritative fixture or append.
2. Implement only the finite Mode A checker and minimax oracle in a temporary
   experiment driver outside `backend`. Run base, tie, incomplete, no-survivor,
   BH conflict and required adversarial twins; no solver, new dependency or public API.
3. Run Mode B as a separate premise-restricted derivation attempt over the same
   material. Report precise unknown cells and the controlled population probe,
   never fabricated model predictions. Measure bytes/work/time and deterministic
   serialization across the specified hash seeds.
4. Deliver an explicitly authorized experiment receipt/artifact with mode results,
   complete derivation, failure categories, preservation and gates; stop for owner
   assessment. Approval of this proposal alone must specify whether a disposable
   artifact may be retained; no committed demonstration is presumed.

This is one experiment design, not multiple milestones. Do not expand the finite
language, add a solver, collect real evidence or design IN/CI during the spike.
If a guard cannot be enforced within the tiny design, report the exact blocker.
Neither a winning test nor a surviving explanation may issue an acquisition or
hardware command. Hypothetical outcomes are branch calculations only.

## 16. Verification, unresolved decisions and task boundary

For this proposal, fresh read-only baseline assertions checked refs/clean tree,
the two required owner-decision hashes, accepted load/replay/count/revision,
236 exports/digest, zero FMA/FMW/FCD/FCW, ADR numbering, protected document/tree
inventories, ignored settings preservation and historical 4,074 accounting.
Live facades/contracts/derivation/tests were inspected; the finite matrix results
above are hand-derived design oracles. No diagnostic algorithm, micro-world,
new test or solver was implemented or executed for this proposal.

Final document checks cover sixteen numbered sections, required ending marker,
twenty-two spill entries, twenty-four threat/twin cases, six decision gates,
seven objectives, local links, one-new-file allowlist and whitespace. A full
repository/clean-checkout matrix is unnecessary and not run for this design-only
task. Historical FC/CV/BH witness evidence is not presented as new spike execution.

Unresolved owner decisions: approve/reject this disposable experiment; authorize
the exact temporary hypothesis/method/calibration/hold assumptions and provenance;
choose secondary `none` for the base proof or separately approve the cost-tie
variant; accept the deliberately tiny caps and stop-on-excess behavior; specify
temporary artifact retention. Real application ingress/invocation, authentication/
authorization, policy authority/version/retention, result retention, actor identity,
confidentiality, capacity/latency, errors, deployment/resource ownership and scope
completeness remain CV prerequisites, not choices made here.

Repository brainstorming informed the two-mode design and algorithm comparison;
verification-before-completion informed baseline/preservation and bounded claims.
The user's explicit output path, no-implementation/no-commit and stop instructions
override default skill handoffs. Only this proposal is written. No branch, commit,
ADR allocation, existing-file edit, authoritative fixture/ledger mutation, push,
merge or history operation. ADR-0023 remains absent, unallocated and unreserved.
Stop after the receipt; the independent adversarial soundness audit is separate.

END OF BRC-EXP-001 CODEX LEAD PROPOSAL
