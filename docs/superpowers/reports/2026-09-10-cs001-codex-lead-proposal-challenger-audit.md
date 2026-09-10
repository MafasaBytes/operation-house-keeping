# CS-001 Codex Lead Proposal — Independent Challenger Audit

One adversarial audit of the frozen CS-001 lead proposal — 2026-09-10.
Audit-only. This report modifies no existing file, implements nothing, and
allocates no ADR. The superseded digest `f4e0c4a3…` was not used.

## 1. Frozen proposal verification

| Check | Expected | Observed |
| --- | --- | --- |
| Path | `docs/superpowers/proposals/2026-09-10-cs001-codex-lead-proposal.md` | Present, read-only input |
| Lines | 728 | 728 |
| Bytes | 64,913 | 64,913 |
| Line endings | LF | LF only; no CR present |
| SHA-256 | `691f3ab913995100d7beb81a2327ac21f4ea42a1fe2c95e8ac68cf6128446550` | Identical |
| Numbered sections | 13 | 13 (`## 1.` through `## 13.`) |
| Ending marker | `END OF CS-001 CODEX LEAD PROPOSAL` | Exact final line |
| Correction 1 | No reliance on `mrv_7b8d1d47…` | Zero occurrences of `7b8d1d47`; section 8.1 now states no disposable revision is cited and binds content through reconstruction and independent commitments |
| Correction 2 | No "temporal value" misdescription of the satisfied-A twin | Zero occurrences of the phrase; the twin is now described as changing the nominated observed value in a disposable occurrence |

The frozen file matches the receipt exactly. Both mandated corrections are
present and correctly scoped.

## 2. Independent baseline verification

All checks were rerun by the challenger, not copied from the proposal:

- Branch `main`; `HEAD = 4ad1a5812e01490bf40aaa8079936f038488e6f9`;
  `origin/main = 7693f1acf763f652947dff28b5dbb8a8dfee2505`. No fetch or
  remote mutation performed.
- Reconciliation report SHA-256
  `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5`
  recomputed and identical.
- `models/demo-printer/records` contains exactly 36 record files; zero match
  the `fcd_`/`fcw_`/`fma_`/`fmw_` prefixes. The 36-record revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` is
  the current membership recorded in `models/README.md:72-73` and
  `models/demo-printer/README.md:204-205`.
- `backend/model_kernel/__init__.py` `__all__` parsed statically: exactly 236
  names, all unique; compact-JSON-list SHA-256 is exactly
  `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`,
  matching the accepted FC final verification report section 11.
- `docs/adr` contains exactly 22 ADR files, numbered 0001 through 0022,
  contiguous and unique. ADR-0023 is absent and unallocated.
- Accepted FC verification accounting confirmed in
  `docs/superpowers/reports/2026-09-09-fc001-slice-b-final-verification-report.md:135-160`:
  4,073 ordinary passes per complete run plus one separately rerun permitted
  loopback pass, covering 4,074; base covers 4,038 plus 35 skips.

The proposal's disposable-proof reference values were independently traced to
accepted artifacts: governing A VCN `vcn_70b5e146…`, ungoverned B VCN
`vcn_3caad214…`, FMA witness `fma_cd234041…`, occurrence `79bcec2f…`, value
`60.1`, receipt `2026-08-07T20:00:06+00:00`, cutoff `21:00:00+00:00`, bounds
50/80, age 3,594 seconds, and fingerprint `sha256:36e4c7f6…` all appear in the
FC final verification report section 9 and the frozen reconciliation. The
challenger confirms no artifact records a disposable-model revision, so the
corrected proposal's refusal to cite one is right.

## 3. Audit method and challenger independence

The audit did not assess prose consistency alone. Every decision input the
protocol needs was traced to a live public field and its validation path in:

- `backend/model_kernel/flow_operating_criterion_results.py` (FC results);
- `backend/model_kernel/port_results.py:77-112` (`ModelQueryMaterial`);
- `backend/model_kernel/contracts.py:1709-1760` (`FlowMeasurementAssociation`)
  and `:1919-1965` (`ConstraintDeclarationResult`);
- `backend/constraint_evaluation/contracts.py` (CN result and derivation);
- `backend/evidence_assurance/contracts.py` and
  `backend/evidence_assurance/queries.py:330-640,1076-1120` (EA);
- `backend/evidence_alignment/contracts.py` and
  `backend/evidence_alignment/derivation.py` (alignment);
- `backend/temporal_state/contracts.py:82-200` (`AttemptOrderKey`,
  `TemporalAttemptEvent`, `TemporalOccurrence`);
- `backend/data_sources/contracts/operational_evidence.py:81-210` (DS-004
  scope and material) and `backend/data_sources/contracts/api.py:30-55`
  (`SourceTimeMarker`).

The challenger worked from the live tree, not from the proposal's citations.

## 4. Field-by-field public-input proof

Classification: **carried** (directly present), **derived** (deterministically
recomputed from carried content), **revalidated** (reconstructed and
authoritatively re-derived at the public boundary), **private**, **missing**,
or **ambiguous**.

| Decision input | Exact public location | Class |
| --- | --- | --- |
| Applicable governing FC declaration | `FlowOperatingCriterionResult.subject.conclusion`, `.reasons`, `.governing_body_group_index`, `body_groups[].declaration_indices`/`current_declaration_indices` (`flow_operating_criterion_results.py:113-130`); outer `model_validate` re-derives the entire subject from carried material (`:133-153`) | Carried + revalidated |
| Exact VCN | Support rows with `support_kind == "vcn"`/`"crg"` and `record_index` into `material.records`; full `ConstraintRegistration`/`VariableConstraintDeclaration` records carried in `ModelQueryMaterial.records` (`port_results.py:77-112`) | Carried + revalidated |
| Exact FM effective body and retained FMA witness | Five subject fields on the FC subject plus the six FMA pins (`frg`/`vrg`/`prg`/`fld`/`vpa`/`vsm` record IDs, `contracts.py:1722-1734`); body group `witness_record_indices` and `matching_fm_current_indices` | Carried + revalidated |
| Nominated variable and measured-actual candidate | CN `constraint.registration.variable_anchor_id`; candidate chain `semantic_compatibility.candidates[i].value_candidate.state_candidate` with six-field locator (`subject.source_id/adapter_id/subject_identifier`, `property.extraction_route/item_key/json_pointer`, exercised by `evidence_alignment/derivation.py:39-48`) | Carried + revalidated |
| CN evaluation | `ConstraintEvaluationResult.candidates[].verdict/not_evaluated_reason/observed_decimal/boundary_assessments`; rows re-derived by `derive_candidate_evaluation` inside `_authoritative` (`constraint_evaluation/contracts.py:148-248`) | Carried + revalidated |
| EA selection and assurance | `OperationalEvidenceSelectionResult.status/request/snapshot/issues`; snapshot carries routes, selected, coverage, fence, assurance, fingerprint (`evidence_assurance/contracts.py:399-423,456-492`) | Carried + revalidated |
| Evidence-alignment disposition | `OperationalEvidenceAlignmentResult` fields; every derived field re-computed from the request by `_derive_alignment_fields` in `_derived_fields_are_current` (`evidence_alignment/contracts.py:248-268`) | Derived + revalidated |
| Receipt cutoff C | EA `request.as_of`; CN `as_of` with internal `as_of == es.as_of` enforcement (`constraint_evaluation/contracts.py:225-227`); alignment `cutoff_relation` compares snapshot vs compatibility cutoffs (`derivation.py:158-160`) | Carried + cross-checked |
| Receipt-side timestamp for age | `snapshot.selected.selected_received_at`, mandatory whenever a selection exists (`evidence_assurance/contracts.py:383-388`); `observation_age_seconds` as canonical nonnegative decimal; `age_basis == "received_at"` | Carried + revalidated |
| Complete `AttemptOrderKey` | All four fields (`attempt_started_at`, `ingestion_run_id`, `sweep_position`, `attempt_id`) present on every `TemporalAttemptEvent` in `temporal_material.attempt_coverage_membership` (`temporal_state/contracts.py:82-133`); canonical order enforced (`evidence_assurance/queries.py:466-471`) | Carried + revalidated |
| Attempt-coverage scope and membership | Exact seven-field `Ds004OperationalEvidenceScope` (`operational_evidence.py:81-91`); request interval `[horizon_started_at, as_of]`; `coverage.attempt_route_indices` (T) and per-disposition index sets (`contracts.py:328-348`) | Carried + revalidated |
| Failures, quarantines, empty, non-observing attempts | `OperationalProvenanceRoute.coverage_disposition` over six literals and the four non-observing coverage sets; derivation at `queries.py:559-577` | Carried + derived |
| Pre-horizon seed dependencies | `selected.pre_horizon_seed`; the seed attempt is explicitly retained in source material (`allowed_source_ids.add(seed_id)`, `queries.py:380-389`) with DS-004 closure validation of its run/envelope/payload; seed never enters T because routes are built only over `attempt_coverage_membership` (`queries.py:466-469`) | Carried + revalidated |
| Reused-payload origin closure | `payload_artifact_index`, `envelope_index`, `run_index`, `artifact_descriptor_indices` per route; shared payload artifacts are permitted and closed (`queries.py:496-535`; `operational_evidence.py:166-210`) | Carried + revalidated |
| Refusal and incomplete-selection state | `status == "refused"` carries refusal-code issues and no snapshot; incomplete carries snapshot plus `no_observation_at_or_before_as_of`/`incomplete_coverage_within_declared_horizon` issues (`contracts.py:64-125,466-492`) | Carried + revalidated |
| Selected revision and identity coherence | FC `material.revision`; CN `constraint.revision` with ES revision equality enforced; alignment `model_revision_id`/`binding_revision_id` disclosures (`derivation.py:110-117`) | Carried + cross-checked |

No required input is private, missing, or merely implied. Two classification
refinements (not gaps) are recorded as findings RC-2 and NBO-1 below.

## 5. Necessity test adjudication

The proposal's central claim survives adversarial testing: the bounded
question is answerable by composing accepted public results with an explicit
caller policy. Independent confirmation:

1. **Integrity without trust.** FC, CN, EA and alignment results each
   authoritatively re-derive their content from carried material at
   `model_validate`; EA adds expected-fingerprint binding
   (`validate_operational_evidence_snapshot`, `queries.py:1076-1120`);
   alignment re-derives every compact field from its request. No private
   field, store reread, ambient clock, or filesystem access is needed.
2. **No missing property.** Age is EA's own receipt-side disclosure; coverage
   is EA's own six-way disposition partition; applicability and verdict are
   FC/CN disclosures. The only new operation is explicit-threshold comparison
   and disposition mapping — deterministic caller policy, not model truth.
3. **No substitution path.** Full CRG/VCN record equality (not anchor
   strings), full occurrence equality over 20 fields
   (`derivation.py:19-36,191-198`), six-field locator equality, endpoint
   closure, and independent expected commitments defeat criterion, candidate,
   cutoff, coverage, and revision substitution.
4. **No fabricated coverage.** The proposal's coverage condition is exactly
   EA's `complete` definition restated (`routes` nonempty, selection present,
   all routes `property_observed`, `queries.py:564-568`), not an unexplained
   Boolean.

The challenger explicitly probed the two weakest links — pre-horizon seed
closure and reused-payload closure — and found both carried and revalidated
(section 4). The no-new-milestone conclusion is **confirmed**.

## 6. Policy boundary adjudication

Distinguishing the four questions the mandate separates:

- **No durable architecture**: confirmed. No record kind can honestly hold a
  workflow permission; overloading CRG/VCN/FCD/SPI/identity records would be
  contract theatre.
- **No milestone**: confirmed for the bounded profile. The challenger found
  no attack requiring a new integrity boundary (section 11).
- **No shared implementation**: accepted, with one non-blocking observation
  (NBO-2). The prose protocol is exact — canonical duration lexicals, fixed
  literals, explicit gate order, exact coverage condition — so a single named
  consumer can implement it faithfully. A second consumer or untrusted
  admission boundary would change that calculus and would require a new
  proposal demonstrating the concrete need; convenience alone does not reopen
  FA-001 under its accepted cancellation rule.
- **Application retention duty**: confirmed and mandatory. The caller must
  retain the full policy value, its version, its authorization reference, all
  independent expected commitments, and the decision outcome. The proposal
  assigns this duty explicitly; the audit agrees it is an application
  obligation, not a backend contract.

A typed request-carried policy model, versioned policy artifact, reproducible
decision receipt, lower-layer repair, and durable declaration were each
considered and rejected as unnecessary for one consumer under the stated
attacker model. None is forbidden; none is required.

## 7. Temporal and coverage challenge

The proposal's temporal semantics were attacked point by point against the
live derivation:

- **Receipt cutoff vs `finished_at`**: age is computed only from
  `selected_received_at`, which is non-null exactly for selected observations
  (`contracts.py:383-388`); `_canonical_age(received_at, as_of)`
  (`queries.py:554-556`). `finished_at` never feeds age. Sound.
- **Source-effective vs receipt time**: `TemporalOccurrence.source_time` is a
  `SourceTimeMarker` (wall clock with basis | monotonic with clock identity |
  unavailable, `data_sources/contracts/api.py:30-55`); EA policy fixes
  `source_time_use == "disclosure_only"`; the proposal forbids cross-domain
  subtraction. Attack 5 (recent source time rescuing stale receipt) has no
  path: no contract compares source time to C. Sound.
- **No-response attempts**: enter coverage by `effective_wall_time` with
  basis `finished_at_no_response` (`temporal_state/contracts.py:96-133`;
  `queries.py:358-361` recomputes `received_at or finished_at`). They can
  never be selected (selection requires `received_at`). Sound.
- **Future timestamps**: selection is latest-at-or-before `as_of`; a selected
  occurrence with `received_at > as_of` cannot arise from the derivation and
  fails snapshot re-derivation if forged; `CanonicalNonnegativeDecimal`
  forbids negative age. Sound.
- **Missing timestamps**: a claimed selected observation without receipt time
  violates `SelectedSourceObservation._coherent_selection` — invalid lower
  content (incoherence), matching the proposal. Sound.
- **Boundary twins**: inclusive `<=`, exclusive `<`, integer microseconds;
  the four exact-threshold twins and zero-duration cases in proposal section
  8 are arithmetically correct (3,594,000,000 µs verified) and match the
  lexical rules (`^(?:0|[1-9][0-9]*)$`-style canonical strings, 365-day
  capacity, no floats). Sound.
- **Independent clock domains**: never mixed; UTC normalization is used only
  for receipt-side aware datetimes. Sound.
- **Reused payloads**: distinct receipt occurrences sharing one payload are
  preserved with full closure; equal payload does not identify occurrence
  (`queries.py:496-535`). Sound.
- **Pre-horizon seeds**: retained with closure, disclosed via
  `pre_horizon_seed`, never enter T, cannot prove continuity. Sound.
- **Multiple matching material**: alignment reports
  `multiple_matching_candidates`/`multiple_matches` honestly and never picks
  first (`derivation.py:207-214`). Sound — but see RC-2 for the proposal's
  classification of this state.
- **Incomplete windows / other-adapter contamination / empty and
  non-observing attempts / intervening failures / refused selection**: each
  maps to a distinct live mechanism — exact seven-field scope parity
  (`queries.py:341-345`), the four non-observing coverage sets, the
  completeness definition, and the refusal result shape. The proposal's
  outcomes preserve each distinction. Sound.

Coverage under this protocol is exactly "every captured attempt in the exact
scope and exact declared interval observed the property, with a selected
observation present" — EA's `complete_within_declared_horizon`. It is not
cadence, physical continuity, multi-source completeness, or authenticated
elapsed time; the proposal names those missing prerequisites exactly. The
challenger accepts this coverage definition as honest and non-generic.

## 8. Outcome vocabulary adjudication — RC-1 (required correction)

The mandate asks whether receipt-age failure may honestly be called
`fresh_measurement_required`. The challenger finds a concrete counterexample
inside the proposal's own semantics:

- Proposal section 4.1 fixes reuse treatment as
  `receipt_occurrence_with_complete_payload_and_seed_closure` and states
  "This explicitly does not demand newly changed content"; section 4.2 states
  "a fresh receipt is not proof that the physical measurement was renewed";
  owner decision 2 asks whether byte-identical rereceipts are acceptable.
- Therefore, under the proposal's own policy, a byte-identical rereceipt of
  unchanged payload at a later cutoff within the age bound yields
  `policy_permits_use` — no fresh physical measurement occurred.

So the label `fresh_measurement_required` (proposal lines 444, 512, 515)
overclaims: what the policy requires is a **new admissible receipt
occurrence** of the nominated measurement; a fresh physical measurement is
the workflow's chosen means of obtaining one, not a policy requirement. Old
retained evidence does not prove the physical measurement is old or false —
exactly the mandate's warning.

**Required correction RC-1**: rename the outcome to a receipt-evidence
disposition (e.g., `receipt_evidence_refresh_required` or
`evidence_not_usable_under_policy` with reason `receipt_age_exceeds_bound`),
or explicitly redefine `fresh_measurement_required` in section 7 as "new
admissible receipt evidence required; the workflow may satisfy this by fresh
measurement or by any newly received admissible occurrence." The worked
examples (section 8, rows 2, 5) and attack row CS-A24 must use the corrected
semantics. This is a labeling/coherence fix; no architecture changes.

Between the mandate's candidates: `fresh_measurement_required` is rejected
as overclaiming; `new_acquisition_required` is also too strong (a rereceipt
may not require new acquisition); `evidence_not_usable_under_policy` with an
exact age reason is the honest policy-level disposition, with "request a
fresh measurement" demoted to the workflow-disposition column the proposal
already maintains.

## 9. Candidate-ambiguity classification — RC-2 (required correction)

Proposal section 5 step 5 (line 348) and the section 7
`input_or_revision_incoherent` trigger (line 436) classify "multiple exact
candidate matches" as incoherence. Concrete counterexample: two honest ES
candidates whose state candidates both attach and carry fully identical
occurrence content (the same occurrence reachable through two legitimate
candidate paths, e.g., duplicated bindings). Every input is valid,
unforged, and expectation-matching; alignment honestly returns
`not_aligned`/`multiple_matching_candidates` (`derivation.py:207-214`). The
proposal's vocabulary would report `input_or_revision_incoherent`, falsely
implying tampering or malformed input, while its own
`criterion_evaluation_unavailable` row already covers "valid lower
non-attachment/unavailability finding."

**Required correction RC-2**: map honest multiple-exact-match ambiguity
(alignment `multiple_matching_candidates` with otherwise coherent inputs) to
`criterion_evaluation_unavailable`, reserving `input_or_revision_incoherent`
for failed reconstruction and mismatched independent commitments. Amend
section 5 step 5 and the section 7 row-1 trigger accordingly. "Never pick
first" remains correct and is unchanged.

## 10. Reproducibility and authority

- **Explicit schema/version**: the protocol tag
  `commissioning.receipt_age_and_attempt_coverage.v1` plus mandatory label
  and version tokens with no latest-resolution is sufficient for
  deterministic replay; full-policy comparison defeats same-label/different-
  threshold substitution.
- **Authority**: the opaque authorization reference is disclosure, not proof;
  authority selection is an application decision. Within the stated attacker
  model (caller-retained expected context is out of scope) this is honest.
- **Durations/boundaries**: canonical decimal microsecond strings, explicit
  inclusive/exclusive token, zero and 365-day capacity behavior defined.
  Replay-deterministic.
- **Coverage dimensions**: exact scope, exact interval, exact
  complete-condition. Replay-deterministic.
- **Canonical serialization**: the policy profile's field set is closed and
  typed; a canonical byte form is not specified, but none is required because
  replay compares validated values, not policy digests. Non-blocking
  observation NBO-3: if two application components ever exchange the policy,
  define a canonical serialization then; do not add it now.
- **Retention and changed-policy replay**: section 8 example 8 (historical P1
  replay after P2 adoption) is coherent — replay supplies the historical
  policy and historical commitments and makes no claim about today's
  permission.
- **Refusal vs withheld**: distinct outcomes preserved end to end; refusal is
  never relabeled stale.

Properly application-owned: policy values, authority, retention, display,
refresh execution. Requiring an architectural contract: nothing in the
bounded profile.

## 11. Required attacks and valid twins

Each mandated attack was traced to its live rejection mechanism; every attack
has a valid twin.

| # | Attack | Live rejection path | Valid twin |
| --- | --- | --- | --- |
| 1 | Violated A, fresh, covered presented as failure | None — this is the honest positive case; CN verdict `violated` is retained and reportable with `policy_permits_use` | Itself: P1 admits A's violation; display preserves violated verdict (proposal example 1) |
| 2 | Satisfied A used despite age failure | Age gate after all availability gates; P2 (3,000 s) denies the 3,594 s receipt | Same E_A40 under P1 (3,600 s) is permitted (RC-1 semantics apply to the label only) |
| 3 | Fresh A with insufficient coverage passed | EA `complete` requires all routes `property_observed`; a failed attempt flips completeness and fingerprint-bound reconstruction rejects its omission | All-observed twin passes; retained-failure twin reports `coverage_insufficient` (example 3) |
| 4 | Satisfied ungoverned B substituted for A | Full CRG/VCN record + revision join between FC support rows and CN `constraint.registration`/`.declaration`; anchor or predicate-text equality insufficient | Original violated A permitted by P1; an independently approved newly designated B world is a different request (example 4) |
| 5 | Recent source time rescues stale receipt | No contract compares source time to C; `source_time_use == "disclosure_only"`; age basis fixed to `received_at` | Identical receipt-age outcome with recent, old, monotonic, or unavailable source time (example 5) |
| 6 | Selection refusal relabeled stale | Refusal shape carries no snapshot and refusal-code issues (`contracts.py:466-475`); alignment short-circuits to `not_evaluated`/`selection_refused` (`derivation.py:125-127`); gate order checks refusal before applicability | Valid non-refused P1 twin is example 1 |
| 7 | Off-by-one at threshold | Integer-microsecond comparison with explicit boundary token; all four twins verified arithmetically | Inclusive/exclusive ±1 µs twins (example 7) |
| 8 | Cross-version replay confusion | Full-policy comparison; historical replay uses historical policy + commitments, claims nothing current | P1 replay under P1 permitted at C; P2 value in P1 context is incoherent (example 8) |
| 9 | Pre-horizon-origin evidence as fresh | Seed disclosed via `pre_horizon_seed`; seed never enters T; age still measured from seed receipt; seed closure retained | Exact seed retained with honest age; empty horizon is `coverage_insufficient`, not vacuous pass |
| 10 | Missing policy authority/version | `policy_inapplicable`; no defaults; full-policy comparison binds content | Complete explicit policy including zero values and fixed literals |
| 11 | Multiple matching materials | Alignment `multiple_matching_candidates`/`multiple_matches`, never first | Single exact match with `attached` aligns (see RC-2 for outcome labeling) |
| 12 | Forged cutoff/coverage/candidate/VCN/FC/revision | Independent expected commitments; authoritative outer revalidation; expected-fingerprint binding; occurrence 20-field equality; revision equality across FC/CN/ES | Correctly derived content under its own independently nominated commitments |

No attack demonstrates a property that accepted public-result validation
cannot establish. FA-001's cancellation rule is not triggered.

## 12. Original-objective challenge

| Objective | Proposal claim | Challenger verdict |
| --- | --- | --- |
| 1. What exists / connected | None beyond existing declarations | Confirmed — no inflation |
| 2. Current state | Distinguishes usable-at-C-under-P from too-old/insufficient | Confirmed as partial and decision-relevant only; it is not present physical state — the proposal says so |
| 3. Why behaving this way | Explains workflow withholding, not physical causation | Confirmed as foundational only |
| 4. Next best measurement | Only "refresh this nominated measurement" | Confirmed with the RC-1 narrowing: the genuinely new bounded answer is a policy-gated usability verdict on one nominated measurement; selection/ranking among alternatives remains absent (no eligible-set, utility, cost, risk, or outcome model) — the proposal does not claim otherwise |
| 5. Change impact | Mismatch withholding; explicit policy-version comparison | Confirmed as existing partial visibility, unchanged |
| 6. Smallest change set | None | Confirmed — refresh request is not a plan |
| 7. Epistemic separation | Keeps observation, calculation, policy, and unknown distinct | Confirmed as partial; strong within the nominated result families |

Overall: CS-001 **merely documents application logic already possible** —
and the proposal says exactly that ("This conclusion does not claim that the
repository already contains a named sufficiency API"; section 1). It creates
no new backend capability and exposes no missing architectural boundary. Its
value is a precise, reviewable protocol plus the verified sufficiency proof.
The contribution claims are not inflated; the objective-4 distinction
(refresh-one-nominated vs next-best-selection) is preserved.

## 13. Findings register and verdict

- **Blocking findings: 0.**
- **Required corrections: 2.**
  - RC-1 (section 8): `fresh_measurement_required` overclaims relative to the
    proposal's own reuse semantics; concrete counterexample is the admitted
    byte-identical-rereceipt twin. Rename or explicitly re-scope to a
    receipt-evidence-refresh disposition.
  - RC-2 (section 9): honest multiple-exact-match ambiguity is misclassified
    as `input_or_revision_incoherent`; concrete counterexample is two
    legitimate candidates carrying identical occurrence content. Map to
    `criterion_evaluation_unavailable`.
- **Non-blocking observations: 4.**
  - NBO-1: `age_unavailable` is honestly reserved but unreachable under EA
    v1; acceptable as stated.
  - NBO-2: a prose-only protocol places ~10 ordered gates on one consumer;
    a typed shared boundary would reduce divergence risk but is not an
    integrity requirement and does not justify a milestone.
  - NBO-3: no canonical byte serialization of the policy is defined; not
    needed while replay compares validated values within one consumer.
  - NBO-4: the horizon-equality carve-out (interval mismatch →
    `coverage_insufficient`; cutoff/scope mismatch → incoherence) is coherent
    and conservative; keep as specified.

**Verdict: `approve_with_corrections`.** Both required corrections are narrow
documentation/labeling repairs to the frozen proposal; neither alters the
no-new-milestone conclusion, the sufficiency proof, or any accepted boundary.

## 14. Owner-decision adjudication and CS-001 disposition

1. **No-new-milestone conclusion**: confirmed. Every decision input is public
   and authoritatively revalidated; no missing integrity property exists.
2. **Receipt-age vs physical-age terminology**: confirmed as disclosed; RC-1
   sharpens the outcome label; owner decision 2 (accepting receipt-occurrence
   age including byte-identical rereceipts) must be resolved before any
   consumer adoption.
3. **Concrete age/window values**: none supplied by the proposal and none
   approved here; owner must supply explicit values per workflow.
4. **Exact coverage sufficiency**: the nonempty/all-captured-attempts-
   observed rule over one exact scope and interval is exactly EA's complete
   semantics — implementable today; whether it suffices operationally is the
   owner's decision.
5. **Policy authority and retention**: application-owned; opaque disclosure
   token acceptable under the stated attacker model.
6. **Refusal/withheld disposition**: confirmed; refusal, absence,
   inapplicability, unavailability, and age failure remain distinct.
7. **Typed composition boundary**: not required for integrity for one named
   consumer; revisit only with a demonstrated concrete need.
8. **CS-001 disposition**: reclassify as application policy. Not deferred —
   no lower prerequisite is missing for the bounded profile. Not a milestone.
   The corrected proposal (after RC-1/RC-2) should stand as the accepted
   design record for the consumer protocol.

## 15. Verification, preservation and audit-only scope

This audit reran the frozen-receipt checks, the baseline checks, and the
field-level source inspection recorded above. It created exactly one file —
this report — and modified none. No code, test, fixture, record, branch,
commit, push, merge, or history operation was performed. ADR-0023 remains
absent and unallocated. The only other working-tree entry observed is the
pre-existing untracked `.claude/settings.local.json`, untouched. Post-write
size, digest, and marker confirmation are reported in the terminal receipt;
this file does not embed its own hash.

END OF CS-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
