# Conditional predictions: corrected comparative disposable-proof design

## Current status — owner accepted, 2026-09-13

The comparative proof is complete and owner accepted. Existing application
composition suffices for the examined bounded case; a backend extension was not
justified. Predictive validity and native premise derivation remain open. No
successor or ADR is authorized; ADR-0023 remains unallocated.
The [owner acceptance](../reports/2026-09-13-conditional-prediction-comparative-proof-owner-acceptance.md)
records the decision and the self-contained execution-evidence commitment.

The original design below is retained as historical authority, not a current
execution gate. Historical input links identify original artifact paths; inputs
not committed separately are recoverable from the completion report's archive,
including its nested historical archive. This status addendum changes no proof
contract, premise or resource limit.

Original design-stage status: Codex lead · 2026-09-13 · design only · proof execution not authorized

## 1. Decision and authority

Recommend a **comparative disposable proof**, not a backend declaration extension.
Compare an application-owned reviewed premise workflow with an experimental
accountable-claim representation, giving both the same evidence, authority,
applicability information and validation requirements. Determine whether the
second representation supplies a concrete capability or packages checks that the
application can already perform. Do not preselect that result.

The question remains: “For an explicitly nominated hypothesis H, measurement
procedure M and applicable conditions C, what outcomes O are supported, by which
evidence or derivation, and what remains unknown?” Conditional declarations can
make an asserted answer accountable and traceable. Their citations, content
integrity and authority do not establish prediction accuracy.

This document reconciles the frozen lead and full challenger audit. It defines
future proof cases and expected outcomes; none has been implemented, constructed
as a new runtime artifact or executed here. No new public contract, production
record, anchor, milestone, ADR, ledger, backend extension or general reasoner is
authorized. BRC-EXP-001 remains accepted and closed as a bounded experiment.

## 2. Actual checkpoint, input commitments and commit clarification

Actual branch: `brc-exp001`. Actual HEAD:
`08bcd16137355dc3e12273f38ac5574adad7bfa6`.
Both tracked and staged diffs are empty. There are 41 ordinary untracked files:
the 39 historical owner-gate artifacts, the lead proposal and the audit. All are
read-only checkpoint exceptions for this task.

| Completely read frozen input | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [Lead investigation](../proposals/2026-09-12-conditional-prediction-codex-lead-investigation.md) | 610 | 49,518 | `a43f843d93729881e9254d0ddb060444e06f95e1ad29a6aef1c288234e24e97c` |
| [Challenger audit](../reports/2026-09-12-conditional-prediction-codex-lead-investigation-challenger-audit.md) | 81 | 12,270 | `5b9517f17ee03c748a455d4c93b1d251ef21b0fa60756e6ea90d0c96f4741399` |

The audit receipt's “committed” is not supported as a Git commit: the audit is
`??`, has no index entry, and `git log --all -- <audit-path>` returns no history.
HEAD and the recent reflog still end at the BRC closeout. The audit itself says
no commit occurred. Thus the evidenced event is file creation, not a new Git
commit. No history repair is needed or authorized. This finding concerns the
inspected repository refs/index/reflog, not inaccessible external repositories.

The existing HEAD is the documented administrative commit
`docs: accept and close BRC-EXP-001`. Its six-file scope is the BRC synthesis,
Slice A execution plan, Mode B execution plan, final owner acceptance, Mode B
execution report and Mode B output-resource amendment report. It contains neither
conditional-prediction input. No new commit is created by this reconciliation.

The accepted [BRC synthesis](2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md)
is the unchanged algorithm/admission reference. These accepted evidence digests
were reverified, not inferred from the audit receipt:

| Evidence | SHA-256 |
| --- | --- |
| [BRC final acceptance](../reports/2026-09-12-brc-exp001-final-owner-acceptance.md) | `74f833a1dd2f119d417c97a8b4b78590d9fd4c71fc3d04b7a35c3fd08c10ba78` |
| [Slice A execution](../reports/2026-09-12-brc-exp001-slice-a-final-execution-report.md) | `5a101e9815d4561d1b2fad6a678eb93c3250d395385efe044d270c85840ea5b2` |
| [Mode B execution](../reports/2026-09-12-brc-exp001-mode-b-final-execution-report.md) | `39afa882cd41bd01b1c39047ff651732770c326b62c03a56c8ab9925d4a495ca` |

Archive recovery and execution evidence recorded in those accepted reports and
the lead investigation are reused with attribution. No experiment replay or new
prediction evaluation is required to reconcile this design.

## 3. Individual reconciliation of all nine audit findings

The full verdict is `approve_with_corrections`: zero blocking findings, five
required corrections and four non-blocking observations. The audit uses CP-1
through CP-9; none is merged away here. Its §4 control requirements are mapped
to the concrete control register in §9.

| Finding | Disposition and reason | Correction to lead / destination |
| --- | --- | --- |
| CP-1 — declaration utility | Accept. The positive synthetic row proves faithful handling of supplied premises, not better predictions or a backend need | Replace lead §§1/10–12 extension-first recommendation with equal-strength comparison; exact accountability answers and measurable differences in §§4/10/13 |
| CP-2 — exclusion justification | Accept. Positive support, authority and citations do not establish complement exclusion | Add decisive attractive-invalid-ranking triplet, empty/all-excluded, surprise and other controls; no scores for incomplete coverage, §§6/8/9 |
| CP-3 — subject sufficiency | Accept. Existing nominated finite subjects suffice without durable identity, but C needs separate fact/assumption/contradiction/unknown axes | Partition C by owner and source; bind complete procedure/domain/edition/context/basis; exact substitution twins, §§5/9 |
| CP-4 — algorithm compatibility | Accept. A claimed envelope does not prove BRC vocabulary, decoder or full matrix admission | Explicit claim-to-cell mapping followed by every BRC admission gate; exact missing/unknown/conflict, alias, tie and zero/one outcomes, §§6–9 |
| CP-5 — backend ownership | Accept. No concrete backend necessity has been demonstrated; one-off application premises remain viable | Strong application baseline, no production identities/contracts; evidence threshold and four-way outcome gate, §§4/13 |
| CP-6 — objectives | Retain with qualification. Claim/applicability/exclusion/conflict traces must be independently committed to show any refinement beyond BRC | Objective 3 compares supplied explanations, 4 ranks only admitted finite sets, 7 preserves epistemic origin; 5/6 stay open, §14 |
| CP-7 — alternatives | Retain. A future behavior or influence derivation could be stronger with justified laws; BRC supplied no such laws | Do not interpret inactive influence control as unnecessary influence; this proof compares representation, not transfer-law engines, §§4/14 |
| CP-8 — integrity versus validity | Retain and make executable later. Citation integrity cannot upgrade uncertainty or validate a forecast | Separate source-integrity/applicability/support-origin fields in both workflows; ranked cells retain assumed exclusion basis, §§5/6/12 |
| CP-9 — finite scope | Retain. No API inventory, fault taxonomy, durable identities or general influence framework is needed | Exactly one bounded case with small single-change controls; no lifecycle simulation or new lower contracts, §§5/9/13 |

Audit §4 items 1–5 map respectively to controls C1, C4–C7, C2–C3,
C8, and C9–C12. The lead's original positive, inapplicable, substitution,
unknown, conflict and citation attacks remain covered. “Commit” wording is
resolved by repository evidence in §2, independently of the technical verdict.

## 4. Two equivalent alternatives, one consumer question

Use local labels **Application** and **Claim** only for this comparison; they are
not BRC Mode A/B names, new milestones or outcome labels supplied to the ranker.

| Dimension | Application-supplied premises | Experimental accountable claims |
| --- | --- | --- |
| Representation | Application-owned reviewed H/M/C/outcome premise table, complete source packet and explicit validation policy | Experimental claim entries with subject/scope, positive/exclusion/envelope basis and the same complete source packet |
| Source evidence and authority | Exact same selected bytes, authorities, contrary claims and declared limits | No extra evidence, trusted approver, hidden semantic input or privileged authenticity |
| Validation | Public lower reconstruction plus explicit application checks for every applicability, support, decoder, conflict and mapping rule in this design | Same requirements implemented over claim entries; a stricter format is not a stronger truth source |
| Retention | Full requests, policy, review decisions, traces and independent commitments permitted and required | Same retention entitlement; no simulated authoritative ledger or automatic lifecycle advantage |
| Consumer | Complete BRC-compatible premise handoff or an explicit stop | Same handoff and stops; ranking algorithm unchanged |

The application may retain structured per-cell evidence, reject stale editions,
check source claims, and implement exactly the same exclusions/conflict rules.
Do not compare an unchecked spreadsheet against a fully validated claim reader.
Both receive the same implementation/repair opportunity and must pass the same
control suite. Ordinary implementation defects are not architectural evidence.

Freeze one representation-neutral source packet per case before preparing either
alternative. It includes full lower inputs, reviewed H/M/C/decoder meanings,
source assertions, explicit completeness/exclusion bases and contradictory or
unknown material. The two preparations must prove field-by-field lossless
correspondence to that packet. Both may share lower public validators and the
accepted ranker; the independent mapping oracle must not call either reader.

Measure whether Claim changes an answer the Application cannot adequately give,
or only locates/standardizes already possible checks. Exact source linkage,
reviewability or reduced duplicated policy may be useful, but do not by themselves
demonstrate backend placement. Do not disadvantage Application by withholding
an explicit policy and then credit Claim with “discovering” it.

BRC B0 examined 17 disposable records; B2 populated 23 and made a BH declaration
and observed equality available without deriving conditional predictions. The
authoritative fixture has 36 records. Population absence is not contract
inexpressibility. The [BH public result](../../../backend/behavior_evaluation/contracts.py)
and [evaluator](../../../backend/behavior_evaluation/facade.py) evaluate observed
equality, not an unobserved H-conditioned outcome. Entity/flow direction alone
does not supply a transfer law. Neither prospective behavior derivation nor
influence is tested by this comparison; directed influence remains untested.

## 5. Pin the shared subject, procedure, conditions and sources

Use the lead §3 / accepted Mode B conditional-rule meanings, not a real fault.
Retained request `8073466a9561b2c035d5c1388e6b63b443cdb68beab8c398757b6415f217caaa`
identifies the complete existing example. Later comparison artifacts are separately
versioned candidates; no accepted BRC request or premise bytes are edited.

| Subject | Meaning and source | Epistemic boundary |
| --- | --- | --- |
| H1 | “High underlying-level / faithful baseline-channel explanation.” | Nominated synthetic hypothesis, level 3 assumed; not established cause |
| H2 | “Low underlying-level / positive baseline-channel-offset explanation.” | Same level; distinct reviewed granularity, not a fault diagnosis |
| Baseline | Carried public governing CN upper bound 50 is violated by observed 60.1; both H admit those checks | Synthetic evidence/evaluation level 1; exact governing/model declarations level 2. Not a future reference reading |
| T1 | Reference-channel scalar procedure, exact nominated variable, `T1_scenario`, temperature, `degC`; finite-decimal domain | Method/domain meaning level 4 assumed; reference fidelity is not supplied by its name |
| T1 decoder | `high` iff value >50; `low` iff value ≤50; total and disjoint over the declared domain | Level 4 supplied decoder, not a measurement or independent physical law |
| T2 | Nonspecific two-code procedure, same nominated subject, `T2_scenario`; successful domain `code_a,code_b` | Level 4 assumed; quantity label temperature and procedural unit `code` are retained, never coerced to numeric temperature |
| T2 decoder | Each literal code maps to its same-named outcome | Total disjoint supplied decoder; no inferred conversion |
| Outcome envelopes | H1/T1 permits high only; H2/T1 low only; both H/T2 permit both codes, under the supplied complete-envelope rule | Level 4 synthetic conditional premise; evidence for software assumptions, not predictive accuracy |

Hypotheses may denote ordinary alternatives, need not be faults, and are neither
globally exhaustive nor guaranteed mutually exclusive. Simultaneous hypotheses
are outside this first proof; do not construct their conjunctions implicitly.
Two H, two M, two primary outcomes suffice; the explicit other control uses a
third outcome within BRC's existing bound. No probabilities, hidden priors or
secondary costs are admitted.

### Condition partition (never a single “verified” Boolean)

For every condition retain its question, source, exact subject, asserted value,
assessment and scope. Its **origin** and **assessment** are separate: a synthetic
assumption can be affirmed without becoming a measured fact.

| Class | Concrete content / owner | Treatment |
| --- | --- | --- |
| Exact lower fact | Model membership/context and governing pins: model kernel; occurrence/binding/interpretation/cutoff: their public owners; evidence selection/alignment: EA/alignment | Reconstruct complete public results and exact joins. Passing establishes their accepted limited meaning, not method applicability |
| External applicability assumption | Scenario, operating regime, availability, calibration and hold/fidelity statements from the selected synthetic source packet | Level 4 affirmed assumption when explicitly supplied and approved; never filled from a citation count or baseline reading |
| Contradiction | Supplied denied condition or exact required condition disagrees with selected fact/basis | Retain contradiction and source; candidate cannot enter original-set comparison |
| Unknown | Absent condition/basis, unknown calibration/regime, or unavailable required evidence | Level 7 unknown; no default affirmation and no ranking over the original set |

Method/decoder edition for this proof means the exact versioned complete
experimental content plus its commitment; it is not a new production identity.
Bind subject, unit, readout domain, scenario, decoder regions, context, model
revision and condition basis—not only labels or digests. Changed content with a
recomputed digest still fails an independent expected-content/subject join.
Condition-source substitution fails even when the same displayed value remains.
A genuinely newly approved source/context would need a separately frozen case.

T1's decoder boundary and governing bound both use 50 but remain independent
claims. A satisfied ungoverned criterion cannot replace the governing one.
Complete public results remain authoritative for their existing validation;
no mocked observed values or fabricated BH result is used to supply predictions.

## 6. Exact support distinctions and claim-to-cell mapping

The following is the common experimental interpretation policy for **both**
alternatives. It is not a backend API or a new scientific validation method.
Every source assertion retains its complete text/typed content, author, scope,
evidence, limitations and whether it is assumed, declared, observed or derived.

| Meaning | Required interpretation |
| --- | --- |
| Positive support | A selected source asserts permission for this outcome under H/M/C. An observed association alone is historical evidence, not automatic future permission; any forecasting generalization must be separately supplied |
| Explicit exclusion | A source asserts that an outcome is outside its permitted envelope, with a separately identifiable exclusion basis and applicable complete envelope over the exact decoder vocabulary |
| Exhaustive coverage | Two different obligations: decoder covers all successful raw values in its declared domain; claim envelope classifies every outcome in that decoder vocabulary. Neither establishes global hypothesis completeness or empirical certainty |
| Unknown | No admitted permission/exclusion basis, missing scope, or insufficient coverage; omission cannot become excludes |
| Conflict | Nonidentical applicable complete envelopes or contradictory support for the same subject/scope; retain all claims and prevent full comparison, even where envelopes overlap |

For an exact H/M pair let V be the independently admitted decoder vocabulary.
Let P be explicitly supported permissions in the selected source packet.
A complete-envelope source specifies a nonempty A ⊆ V and explicitly asserts
that outcomes outside A are excluded, with the exact V and exclusion basis.
“Complete for a smaller source vocabulary” does not assert completeness for V.

The mapping order is fixed:

1. Preflight, reconstruct lower inputs and check baseline/subject/condition joins.
   Reject malformed or substituted claims; denied/unknown candidate conditions
   stop the BRC comparison with `candidate_unavailable` rather than being repaired.
2. Validate source scope and decoder. Preserve integrity validation separately
   from support origin and predictive validity. Do not parse prose into laws.
3. Detect unresolved applicable support conflict before selecting any envelope.
   For a conflicted H/M row emit unknown relations for all its V outcomes,
   retaining the competing support in the comparison trace; never union,
   intersect, vote, choose latest or prefer more citations.
4. For a nonconflicted row with an admissible complete envelope: members of A
   become permits; members of V\A become excludes, each with the envelope and
   exact exclusion-basis reference. This is conditional on the supplied premise.
5. Without that complete basis: an explicitly admitted forecast permission in P
   becomes permits; every other outcome becomes unknown. Merely recording an
   exclusion without the required scope/envelope does not make it admissible.
6. Produce exactly one cell for each H/M/O in the actual product. Mapping traces
   identify source assertion, completeness/exclusion basis, conditions, vocabulary
   and rule step for each relation. Independently check the whole mapping before
   passing a candidate request to unchanged BRC admission.

Conflicting or incomplete support produces explicit unknown cells, not a new
ranker conflict resolver. Use existing `application_policy` or the applicable
existing missing-premise GapCode for unresolved supplied support, with exact
subjects and retained reason; do not extend BRC enums. Supplied Mode A handoff
predictions remain level 4 assumed, with mapping computation separately level 5.
Unknown cells remain level 7 with required reasons. No empirical-validity flag
may become true simply because the mapping validates.

The mapping checker is essential: BRC cannot detect that a syntactically complete
matrix contains an unjustified exclusion if its upstream source trace is omitted.
An attractive but dishonest matrix may pass arithmetic admission in isolation.
The proof must catch the unauthorized transformation at the support-to-cell
boundary, not claim the unchanged ranker understands source justification.

## 7. Complete BRC admission and unchanged algorithm

The handoff uses the accepted experimental Mode A request/result contracts in
BRC §§3–7, 10, 17–19. It is neither a new exported contract nor a production
ranking API; the disposable BRC driver was deleted. A future implementation must
reproduce the accepted algorithm independently of expected outcomes.

Admission is mandatory for both alternatives, including positive cases:

- Closed schema/mode/algorithm/policy arms; exact types, no Boolean indices,
  hidden fields, nonfinite values, unapproved priors/costs or global-best wording.
- Bounded preflight and independent commitments precede full owning reconstruction.
  Complete F/N/E and any genuinely required BH are retained, with exact revision,
  context, subject/owner/flow/port/orientation, CRG/VCN, occurrence, binding and
  interpretation revisions, cutoff, fingerprint and alignment coherence.
- Applicable governing FC, usable evidence/alignment and evaluated governing CN
  are required. Valid lower unavailability yields `baseline_unavailable`;
  satisfied governing CN yields `baseline_not_violated`, not a candidate edit.
- Reviewed semantic H and M distinctness; exact duplicates/aliases reject before
  scoring. Renaming or adding citations cannot multiply a hypothesis. Distinct
  meanings with identical predictions remain valid and disclosed.
- Each decoder has a nonempty vocabulary and total, disjoint regions over the
  exact successful domain. Gaps, overlap, duplicate regions and inconsistent
  domain/unit refuse. Failure/absent acquisition is not a successful other token.
- One relation per actual H×M×O triple; duplicates and outside-domain triples
  refuse. Missing cells produce an explicit missing list and
  `insufficient_information`; unknown cells produce `insufficient_information`
  and ordered `coverage/cell_unknown` diagnostics. Neither has scores, best sets
  or a recommendation. Conflicting support follows this unknown-cell path.
- All supplied rows, including later-refuted H, require complete known coverage
  before ranking. Every known H/M row permits at least one outcome; otherwise
  `input_refused` / `row_all_excluded`. Unknown is not an all-excluded row.
- All required baseline checks are evaluated at their public paths. Contradiction
  and unavailable reasons remain separate; a required unknown blocks comparison
  even if another check contradicts that H. Complete zero viable H gives
  `no_viable_hypotheses`; complete one viable H gives `no_discrimination_needed`.
  Both retain consistency evidence without scores, best sets or recommendation.
- No silent removal of an unusable measurement or outcome. A smaller list needs
  a separately approved request. Global H/M completeness stays unknown.

For ≥2 viable H and only after complete admission:
`S(M,O) = {H : cell(H,M,O) = permits}` and
`score(M) = max(|S(M,O)| over O in V(M))`.
All minimum-score measurements remain in the best set; no secondary cost policy.
Zero best reduction gives `no_discriminating_measurement` with no recommendation.
Positive reduction gives `preferred_within_supplied_set` for one best measurement
or `tied_best_within_supplied_set` for multiple, with no selected winner.

Every outcome's S remains explicit, including an empty S for a successful
unexplained surprise. That empty branch participates in max but does not itself
refuse ranking or assert impossibility. At least one nonempty branch per viable
H/M follows from row coverage. An explicit other permitted by both H contributes
2; it cannot be hidden to manufacture a score of 1.

Canonical cells sort by H/M/O; H/M/O sets use ASCII publication order. Checks
sort by check ID; steps topologically by depth then step ID. Public arrays keep
their owning order. Refusals use BRC phase order, RefusalCode order, then canonical
target bytes; gaps use GapCode order, target and attempted rule. Refusal targets
must be derived from the actual subject, not defaulted null. Ordering publishes
ties; it does not break them. No ranking algorithm change is proposed.

## 8. Worked attractive-invalid-ranking triplet

All following are expected mathematical/semantic outcomes, not executed results.
H2/T1 and both T2 rows retain the original fully scoped synthetic rules. Both
alternatives receive exactly the same source difference for H1/T1.

| Version | H1/T1 source and mapping | Expected consumer outcome |
| --- | --- | --- |
| Partial-support valid baseline | Explicit synthetic positive permission for high; no admissible low exclusion or complete-envelope assertion. Cells: high permits, low unknown | `insufficient_information`, `coverage/cell_unknown` on H1/T1/low; no scores, best set or preference for either measurement |
| Attractive invalid mapping | Same partial source, but a faulty reader maps omitted low to excludes | Independent mapping check rejects the unjustified H1/T1/low cell before accepted ranking. The illicit complete matrix would have T1=1 versus T2=2, which explains the attraction—not a valid result |
| Separately justified valid twin | Add the exact independently identified synthetic complete-envelope/exclusion premise for H1/T1 over V={high,low}; scope and conditions match | high permits, low excludes; all eight cells complete; expected T1=1, T2=2 and T1 preferred within the supplied set |

“Justified” here means entailed by the separately supplied and approved synthetic
exclusion premise under the fixed mapping policy—not empirically established.
The source for the valid twin is the explicit BRC conditional rule, not the
mere fact that an authority signed a positive-support statement. The partial
case's selected evidence scope must not secretly contain that full rule; the
omitted rule is a disclosed case difference available equally to both alternatives.
Case labels/digests and expected scores never enter the readers or ranker as
behavioral instructions.

Future execution must retain a genuine fault-injected omission→exclusion reader
and the corrected valid-nearest-twin check. Restoring the mapping restores the
unknown/no-score output; adding the separate complete premise yields the positive
output. Do not weaken oracle comparisons or edit the ranker to accommodate the
fault. Support selection and exact premise variants require later owner approval.

## 9. Minimal paired control register

One base case and the following single-distinction families cover the audit.
Each is run through **both** alternatives after approval. Parameterized attacks
are reported individually, with a valid nearest twin; this is not a claim of a
globally minimum set cover or an inflated count of distinct worlds. The same
base may serve several twins. No cross-product resource stress corpus is required.

| Control | Precise difference / nearest valid twin | Expected outcome |
| --- | --- | --- |
| C0 — complete base | Four original complete envelopes, two H/two M/two outcomes | Eight cells; T1=1, T2=2; bounded preference and complete assumed-premise trace |
| C1 — unsupported exclusion | §8 partial / faulty mapping / separate complete-basis triplet | Partial no-score unknown; faulty mapping rejected; full-basis twin C0 passes |
| C2 — condition partition | Independently deny or make unknown each required applicability/availability/calibration/hold condition; restore its exact affirmed assumption | No original-set comparison, `candidate_unavailable`; source retained as denied/unknown, not observed or silently affirmed |
| C3 — substitutions | Independently replace subject, unit, domain, scenario/regime, decoder edition, context, revision or condition basis while keeping labels/scores; restore exact complete matched content | Support join rejection before scoring; stale commitments reject earlier at commitment check. Use valid lower reconstructed variants for semantic attacks so malformed IDs do not mask the intended join failure |
| C4 — decoder | T1 low upper becomes exclusive at 50 (gap); high lower becomes inclusive (overlap); duplicate region; empty vocabulary; restore original | `input_refused` / `decoder_invalid` (or earlier schema/count failure for empty vocabulary, pinned in preexecution oracle); original total disjoint decoder passes |
| C5 — explicit other | Version T2 successful literal domain/decoder to include code_other. Source explicitly covers only code_a/code_b, with completeness limited to that subdomain; exact new method binding retained | Both other cells unknown; no scores. Valid twin separately supplies permits for other for both H, with full vocabulary envelope: T2=2, T1=1. Other is a successful outcome, not missing input |
| C6 — empty envelope | Empty complete H1/T1 envelope; or direct all-excludes handoff attack. Restore one or both permissions | Empty complete claim rejected; direct known row rejected `row_all_excluded`, not H elimination. No successful scores |
| C7 — surprise/no partition | Separately scoped complete T1 claims permit low and exclude high for both H; T2 unchanged | S(T1,high)=empty explicitly unexplained, S(T1,low)={H1,H2}; T1=T2=2, `no_discriminating_measurement`, recommendation null. Valid twin C0 covers the high branch; surprise is not impossible |
| C8 — conflict | Add incompatible H1/T1 envelope {low}, or overlapping nonidentical envelope {high,low}, beside {high}; exact same scope | H1/T1 unknown row, no scores. Reorder authority names/counts/times/IDs without choosing a winner. Single-claim C0 twin passes; no implicit reconciliation |
| C9 — aliases versus tie | Relabel an identical H or M semantic body; separately create justified T2 code_a-only for H1 and code_b-only for H2 while keeping genuinely distinct methods | Alias `semantic_alias` refusal; valid distinct partition twin T1=T2=1, plural tied best, recommendation null |
| C10 — cell product | Delete a required handoff cell; duplicate it identically or with opposite relation; use outside-domain outcome | Missing → insufficient_information with exact missing triple; duplicates → cell_duplicate; outside → cell_outside_domain; restore exact eight cells as twin |
| C11 — zero/one viable | Separately version only baseline expected-value checks so one or both supplied H contradict the unchanged observed 60.1; keep complete prediction rows | One → no_discrimination_needed; zero → no_viable_hypotheses; no scores/best/recommendation. Original expected checks restore C0. An unknown required check instead blocks full comparison |
| C12 — provenance/reconstruction | Stale source content, changed content-derived lower ID, assumed→observed relabelling, hidden field, Boolean index, wrong arm, omitted/reordered trace or forged score | Commitment/lower/epistemic/result rejection at first applicable gate; restoring the exact valid bytes passes. New self-hash alone cannot bless a substituted source |

C5/C7/C9/C11 are explicitly proposed synthetic premise variants, not historical
BRC facts or newly approved operational assumptions. Exact strings, commitments,
diagnostic targets and complete static result forms are frozen at the future
preexecution gate. Where an earlier gate can mask a later one, retain distinct
attacks: stale-hash for commitment, correctly recomputed candidate hash for
semantic checking. Do not claim coverage of a semantic rejection from a byte-limit
or stale-hash rejection. No new real-device evidence is invented.

## 10. Comparison criteria and independent oracle

The common pass criteria are: same source completeness; identical applicability
decisions and cell mapping; same full BRC admission disposition; exact expected
S/score/tie only when admitted; complete accountable trace; no unsupported
exclusion, omitted surprise or invented confidence; bounded deterministic results.
Each alternative must answer “which claim, which exclusion basis, under which
conditions, and what contrary/unknown material?” with exact references, not prose
alone. Both are allowed to satisfy all criteria.

Separately record any difference in capabilities, validation responsibilities,
review operations and repeated policy. Fewer fields/lines of code or a nicer
container is not evidence of stronger predictions. If results and guarantees are
equivalent, state that the claim form packages application checks. If one fails,
repair ordinary defects before attributing the failure to its architecture.
Measured convenience may support retaining the claim form experimentally while
backend placement stays unproved.

Before execution, an independent oracle must bind each shared packet to:

1. Exact source permissions, exclusion basis, declared completeness and competing
   support; exact condition partitions and decoder coverage.
2. Hand-derived relation for every actual H/M/O, with reason and source. The
   oracle must not import either mapper or the ranker.
3. Expected earliest stage, exact ordered issues/targets and absent successful
   fields for every stop; complete static success/refusal forms, not just statuses.
4. For complete admitted forms only, independent set enumeration. For C0:
   S(T1,high)={H1}, S(T1,low)={H2}; both T2 branches={H1,H2}. Maxima 1 and 2.
   For C7 and C9 use the exact sets stated in §9. For unknown/one/zero forms,
   assert the required absence of scores rather than invent a hypothetical score.
5. Full provenance, trace identities/order and exact handoff commitments. Output
   wrappers may differ by representation; the independently specified semantic
   projection and all declared representation-specific fields are checked, not
   an open-ended list of permitted differences.

Preexecution checks must construct and revalidate every required complete input
and static output arm, including supplemental conflicts, other/surprise and
trace-heavy forms. Resolve any contract/oracle conflict together before freezing
the package. Dynamic semantic-read mutation proof belongs to later execution;
schema coverage alone is not evidence that implementation consumes each field.

## 11. Resource measurement gate before execution

No new input/output maximum is measured or certified by this design. Historical
BRC maxima (A 11,567/13,453 input/result; B 11,410/13,735) describe accepted
experiments, not headroom for these extra justification traces.

Proposed proof stopping budgets, requiring explicit approval with the measured
package: input 12,000 charged nodes, result 13,453; safety ceiling 16,384.
These reuse the Slice A budget rather than silently borrowing Mode B's larger
result policy. Full request/result bytes remain at most 524,288/786,432,
generated trace allowance 131,072 and bounded refusal reserve 1,024. Keep BRC's
other literal bounds: H≤2, M≤2, O/M≤3, cells≤12, model records≤32,
Statements≤24, direct citations/check-support refs≤4, steps≤64, derivation
depth≤4, JSON depth≤48, experimental text≤512 UTF-8 bytes, labels≤32 ASCII
bytes, plus the narrower per-field/public constraints of BRC §10. No automatic
cap amendment, truncation or new evidence population follows if a form does not fit.

Measure the complete source packet, each independently admitted reader request,
each full handoff and complete result, and the report-level retention bundle
separately. Any source/trace needed to validate a result must be carried within
that result's measured boundary, not hidden in uncharged side telemetry. A
transport bundle is not a runtime request; bounded extraction must deliver a
self-contained request with its own admission. Equal evidence cannot be withheld
from Application to make its carriage smaller or supplied to Claim for free.

Use the accepted additive formula: canonical wire nodes (including keys and
references) plus complete resolved Statement body charge **per typed reference
occurrence**. Ordinary IDs do not recursively expand; validator-created copies
do not alter the canonical tree. Count actual lookup/owning reconstruction work
separately, with no unproved memoization discount. New experimental reference
forms cannot be used to hide equivalent resolution work.

Preflight raw bytes → shallow types/cardinalities/product/depth → wire count →
bounded reference shapes/lookup → resolution charge → total and output reserve
→ full authoritative reconstruction → semantic admission. During future result
construction reserve each fragment's bytes and charges before appending, and
enforce result budget before authoritative result reread. Fixed bounded refusal
contains no partial success and cannot recursively exceed its own reserve.

Before execution require two independent counters, full input/output role
inventory and agreement across seeds 1/7/313, two disposable roots and forward/
reverse permissible construction order. Measure both alternatives; no padded
domain object to hit a numerical limit. Use naturally reachable under/over-limit
evidence where constructible and clearly separate counting-primitive tests.
Over-limit refusal must precede owning calls. Resource failure makes the affected
comparison inconclusive; it does not prove missing prediction semantics or a
backend need. A complete measured package is a separate owner gate.

## 12. Provenance, isolation and retention

Keep observation/accepted evaluation at level 1, existing declared model facts at
2, nominated H at 3, synthetic method/conditions/forecast permissions and
exclusions at 4, mapping/arithmetic at 5, bounded compatibility/preference at 6,
unknown at 7. Calculating a cell never erases assumed antecedents. Cited authority
does not make a premise observed, and BRC software verification does not establish
empirical predictive support. Association, authority declaration, experimental
support, model derivation and causality must remain distinct classifications.

Both alternatives use only existing public APIs for lower reconstruction and
composition. No private indexes, store/filesystem/network/device/clock reads
during final validation, production imports of experimental code, source reselection,
ledger appends or simulated observations. Source/meaning/lifecycle ownership
remains with existing packages; application policy selects supplied support, not
engineering truth. Hypothesis generation, control, diagnosis and planning remain
outside the proof.

After separately authorized execution, retain a self-contained report/archive
with exact canonical source packets, both prepared representations, complete
handoffs/results, policy, oracle, case/twin mapping, fault-injection evidence,
counter/resource data and full execution reproduction commitments. Preserve
origin/version of every new synthetic premise and exact lower memberships.
Verify archive recovery before deleting disposable drivers/tests. Digests bind
bytes, not durable engineering identity or authenticity. No standalone candidate
is made authoritative merely by retention; any later commit needs explicit
authority. No artifact except this design is created in the present task.

## 13. Four-way outcome gate; no predetermined backend result

Publish exactly one comparison disposition, with its concrete evidence and all
limitations. Use this evidence order: assess validity/completeness first; assess
a specific backend requirement only if actually demonstrated; otherwise distinguish
useful representation from sufficient application composition. Multiple unresolved
architecture questions remain disclosed, not forced into a new milestone.

| Outcome | Evidence required | Permitted recommendation |
| --- | --- | --- |
| Existing application composition suffices | Application passes all safety, trace and handoff criteria with equivalent evidence/effort; Claim adds no independently demonstrated required capability | Retain reviewed application-supplied premises and explicit policy for this one-off use; no backend extension |
| Accountable claim representation useful; backend placement unproved | Both are valid, but concrete review/trace/policy-reuse benefit of the representation is demonstrated without an ownership gap | Keep the representation experimental/application-owned; no kernel necessity claim |
| Specific backend requirement demonstrated | A named actual consumer requires a precise model fact, shared lifecycle or integrity invariant, with a reproducible counterexample that existing public composition cannot adequately preserve and an explicit explanation why | Report that exact requirement for a separate owner design decision; no implementation/identity/milestone allocation |
| Comparison inconclusive | Missing equivalent inputs, unapproved premises, unresolved contract conflict, resource violation, uncorrected implementation defect or incomplete oracle/measurement evidence | Retain findings and the specific blocker; no architectural winner |

The backend gate cannot be met merely by recording a claim or inventing a future
second consumer. It requires, for example, an **actually required** correction/
withdrawal/replay obligation across named consumers that must be anchored to exact
model subject/context and evidence closure, plus evidence that complete
application-carried inputs and current public validation fail that obligation.
State the counterexample, existing alternative attempted and missing owner of
the invariant. Convenience, hypothetical reuse, a self-consistent schema or an
application bug is insufficient. Do not introduce a production lifecycle in this
proof to manufacture the requirement.

No such requirement is established at this checkpoint. If discovered during
later work, record it without silently broadening this comparison. The existing
model declaration/revision boundary would be a candidate owner, not a second
ledger; EA authentication, temporal applicability, BH/CN numerical meaning and
source authority must not be reassigned. Existing public composition suffices
when exact reviewed inputs, explicit policy and independently retained commitments
meet the concrete one-off need. The useful answer may be identical in both forms.

## 14. Objectives, remaining owner gates and current verification

Objective 3 gains inspection/comparison of supplied explanations and their claimed
consequences, not actual-cause identification. Objective 4 gains only conditional
worst-case discrimination within the fully admitted supplied set, not global
best-test selection, utility, safety or execution. Objective 7 gains a potential
refinement only if independently committed claim, exclusion, applicability and
conflict traces improve the answer; otherwise this is BRC's premise handling in
another representation. Objectives 1/2 reuse existing model/baseline evidence
without new structural/state truth. **Objectives 5 and 6 remain open**: citation
dependence is not change-impact propagation; a preferred test is not a plan.
Prediction accuracy, real diagnosis, law derivation and causal influence remain
unproved. No successor is selected.

The next owner decision is approval of this concrete comparative-proof design.
Approval must not be interpreted as execution authorization. Later preparation
must freeze both equivalent input representations, all proposed premise variants,
the independent oracle, full measurements and exact output forms for one
consolidated preexecution approval. No need to reopen durable identity or allocate
an ADR to approve this disposable comparison.

Current focused verification comprises branch/HEAD/index/status and audit path
history checks; full reading and digest checks of both frozen inputs; accepted
BRC report digest checks; local-link, numbered-section and marker checks;
working-tree and new-file whitespace checks; and whole baseline-file preservation.
No test suite or proof ran. History was inspected, never modified.

The start inventory contains 808 tracked/ordinary-untracked regular files.
Sorted `(relative path, file SHA-256)` pairs serialized as compact JSON hash to
`209411d9ee05bc4d8e4bb41d14b30392fd4cac0d3f388c8e2816005e090c6890`.
The final check excludes only this new design and must reproduce that exact
count/digest. Thus the lead, audit, accepted reports, 41 untracked inputs,
production and authoritative files remain byte-for-byte unchanged. Ignored
runtime directories are not claimed as an audited inventory and are not written.
Final intended status is no tracked/staged changes and 42 untracked files: the
original 41 plus this design. No commit, push, merge, reset, amendment, revert,
new branch, milestone or ADR allocation occurred.

END OF CONDITIONAL-PREDICTION COMPARATIVE PROOF DESIGN
