# TA-001 Codex Lead Proposal — Independent Challenger Audit

Status: adversarial audit only. No implementation, acceptance, model record,
fixture, demonstration, ADR, or persistence is authorized or created by this
report. The audit is read-only and does not modify the proposal.

## 1. Frozen-subject and baseline verification

Verified directly against the working tree at audit time:

- branch `main`; `git rev-parse HEAD` = `git rev-parse origin/main` =
  `948374eec3cd49596fe19548a58a4fb10760a433` — matches the assigned baseline.
- `docs/superpowers/proposals/2026-09-07-ta001-codex-lead-proposal.md` is
  exactly 877 lines / 49,616 bytes, SHA-256
  `a8130d3146af7c159d739b6c63b9e0c398fd0bf4f1fa363d99559c476a0cf146`, and its
  final line is exactly `END OF TA-001 CODEX LEAD PROPOSAL`. All match the
  assigned expectations.
- `CLAUDE.md` (repository copy) confirms the milestone sequence through
  EA-001, "EA-001 is complete and owner accepted", the 36-record ledger at
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
  FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and "No successor milestone is
  currently approved or in implementation."
- `backend/transition_assessment` does not exist; `backend/evidence_assurance
  /README.md` does not exist — both match the proposal's stated checkpoint
  facts.
- Root `README.md` line 77 confirms ADR-0019 reconciliation is pending for
  EA-001, matching Section 1's claim that the missing ADR is pre-existing
  documentation debt, not something this proposal introduces.
- `git status --short` at audit start showed only the two pre-existing
  untracked entries (`.claude/settings.local.json`, the proposal file itself);
  no other tracked file was modified. The subject was not moving.

Baseline verification passes; the audit proceeds on the frozen subject.

## 2. Verdict and finding counts

**Verdict: `approve_with_corrections`.**

- Blocking contradictions: **0**
- Required corrections before design approval: **2**
- Non-blocking observations: **6**

No public-join, semantic, temporal, architectural, or preservation
contradiction was found against the accepted code inspected. The required
corrections concern an unjustified hostile-graph resource bound and one
terminology-consistency gap that must be resolved in the implementation plan,
not the pure architecture.

## 3. Public-join audit (Section 5)

Traced the exact field chain in the real contracts (not the proposal's
prose) across:
`backend/state_classification/contracts.py`,
`backend/constraint_evaluation/contracts.py`,
`backend/semantic_compatibility/contracts.py`,
`backend/observation_compatibility/contracts.py`,
`backend/evidence_alignment/contracts.py`,
`backend/model_kernel/transition_results.py`,
`backend/evidence_assurance/contracts.py`.

Findings:

- `StateClassificationConditionResult.constraint_evaluation_index` selects a
  row of `StateClassificationResult.constraint_evaluations`; its optional
  `candidate_index` selects a row of that `ConstraintEvaluationResult
  .candidates`. `constraint_evaluation/contracts.py:230-235`'s
  `_authoritative` validator enforces `row.semantic_candidate_index == index`
  for every candidate row (contiguity), so `candidate_index` is provably the
  same position as `CandidateConstraintEvaluation.semantic_candidate_index`.
  `state_classification/derivation.py:47-54` further shows a registered
  explicit condition always carries exactly one candidate at index `0` (or
  `None` when unregistered/no-candidate), matching Section 5 step 2's claim.
- `semantic_compatibility/contracts.py`'s `CandidateSemanticCompatibility` has
  no explicit index field; its `candidates` tuple is required to be
  position-parallel to `VariableValueCompatibilityResult.candidates`
  (confirmed by direct read of `semantic_compatibility/contracts.py:285-307`).
  Therefore `semantic_candidate_index` legitimately locates the same-position
  value candidate as Section 5 step 4 claims, **not** because index domains
  are assumed identical across layers, but because each layer's own
  validator enforces the positional correspondence explicitly. This is the
  correct distinction the audit was asked to test, and the proposal draws it
  correctly (Section 5 explicitly says "Equal values, timestamps, checksums,
  occurrence IDs, record IDs, or locators alone never satisfy a step" and
  requires full nominal object equality, not index-domain identity).
- `evidence_alignment/contracts.py`'s `aligned_candidate_index` is derived by
  enumerating `request.compatibility.candidates` itself
  (`evidence_alignment/derivation.py:153-165, 216-227`), i.e. it is an index
  into the *same* compatibility object the alignment request carries, not a
  cross-layer assumption. The proposal's required check — "an alignment's
  `request.compatibility` must equal the condition's complete
  `VariableValueCompatibilityResult`, and its `aligned_candidate_index` must
  equal the condition's candidate index" — is therefore a coherent,
  fully-grounded design: full-object equality first, then a same-object index
  match. There is deliberately no foreign-key chain from a
  `StateClassificationConditionResult` straight to an
  `OperationalEvidenceAlignmentResult`; bridging by carried-object equality
  (rather than an ID/index shortcut) is exactly what the proposal repeatedly
  states it does, and it is real in the code.
- Missing/duplicate/extra/reordered/substituted alignments (checks 6): the
  proposal's requirement of "exactly one distinct alignment row per distinct
  required compatibility, no unmatched row" is checkable purely from
  `OperationalEvidenceAlignmentResult.request.compatibility` object equality;
  no contract gap prevents detecting any of these five attack shapes.
- Observation-absent conditions (check for §5 step 5): confirmed via
  `observation_compatibility/contracts.py` that `CandidateValueCompatibility
  .state_candidate` (a `CandidateObservation`, `model_state/contracts.py:98-
  110`) carries `bound: BoundLatestObserved | None`; when `bound is None` the
  condition genuinely has no governing occurrence, so requiring "no EA
  alignment for that condition" and reaching a `not_applicable` TA trace is
  reachable and does not require any invented lower fact.
- The EA "six-field locator" terminology used throughout the proposal
  (Sections 5, 8, 13) is **inherited, not invented**: the accepted EA public
  contract itself literally names the field
  `scope_relation: Literal["six_field_locator_equal", ...]`
  (`evidence_alignment/contracts.py`), even though the underlying
  `Ds004OperationalEvidenceScope` actually carries seven fields (`source_id,
  adapter_id, endpoint_id, item_key, subject_identifier, extraction_route,
  json_pointer` — `data_sources/contracts/operational_evidence.py:81-90`).
  This is a pre-existing accepted-vocabulary quirk from EA-001, not a defect
  TA-001 introduces (non-blocking observation #1, Section 13).

Conclusion: Section 5's join proof is implementable exactly as written against
the real accepted contracts. No blocking contradiction found here.

## 4. Semantic and temporal audit (Sections 6-7, checks 2-3)

- `model_kernel/transition_results.py:270-311` was traced concretely: for
  `TransitionDeclarationConclusion == "declared"`, the derivation guarantees
  `conflicted` (same-root fork tuple) is empty and all healthy roots share one
  body (`len(set(healthy_bodies)) <= 1`), and `effective_body_groups` is built
  only from tip bodies of currently-active tips, which for a declared result
  come only from the (single-bodied) healthy roots. This *proves* — rather
  than merely asserts — Section 7's claim "it has exactly one effective-body
  group" for every declared transition; the proposal's admission rule is
  sound, not an unverified assumption.
- Model-revision comparability (Section 7 "the transition and both
  classifications carry the exact same complete `ModelRevision`"): confirmed
  reachable. `TransitionDeclarationResult.material: ModelQueryMaterial` and
  `StateDeclarationResult.material: ModelQueryMaterial` (nested inside each
  `StateClassificationResult.state`) both carry `revision: ModelRevision`
  (`model_kernel/port_results.py:77-97`, `model_kernel/state_results.py:580-
  600`), so a full `ModelRevision` object-equality check across all three
  inputs is directly expressible without inventing a field.
- Subject-entity comparability: `TransitionLookupResult`/registration payload
  exposes `subject_entity_registration_index`
  (`model_kernel/transition_results.py:94-104`), and the analogous state
  lookup/declaration path exposes the same concept
  (`model_kernel/state_results.py:551-577`). The comparison the proposal
  requires is expressible through these carried registration indices resolved
  against the shared `ModelQueryMaterial`, not through an invented field.
- Temporal claims (Section 6): `independent_latest_at_or_before_cutoff`/
  `independent_latest_at_or_before_as_of` and `source_time_use:
  "disclosure_only"` are real accepted literals
  (`evidence_assurance/contracts.py:242-247`); the proposal's refusal to
  compare source-native clocks and its "not a temporal cohort" disclosure are
  consistent with this accepted policy shape, not an extension of it.
- No evidence was found that TA's proposed conclusions imply occurrence,
  continuity, or path; Section 2's exhaustive non-objectives list and Section
  12.4's table keep both conclusions confined to "bounded evidence
  (does/does not) support the declared endpoint pattern," matching the ST-002/
  ST-001 non-occurrence discipline already enforced at the lower layers.

No blocking contradiction found in semantic or temporal claims.

## 5. Evidence/fingerprint audit (Section 8)

- `evidence_alignment/contracts.py` confirms `OperationalEvidenceAlignmentResult`
  carries exactly `status` (`aligned_with_complete_evidence`,
  `aligned_with_incomplete_evidence`, `not_aligned`, `not_evaluated`),
  `evidence_selection_status`, `evidence_coverage_completeness`,
  `expected_fingerprint_relation`, and `snapshot_validation` fields — all
  distinct fields the proposal's evidence-gate rule (Section 8) individually
  requires. The gate correctly requires all five to hold simultaneously and
  treats `aligned_with_incomplete_evidence` as a **successful lower
  alignment that still fails the TA gate** — this is a real, expressible
  distinction and not a status collapse.
- `evidence_assurance/contracts.py`'s `OperationalEvidenceSnapshotValidationResult`
  carries `computed_fingerprint`, `embedded_fingerprint_relation`,
  `expected_fingerprint_relation`, confirming Section 8's claim that a
  coherently-replaced snapshot-plus-embedded-fingerprint can remain
  "structurally self-consistent" while an independently retained expected
  value (supplied only by the TA caller, never derived from the snapshot)
  still catches the substitution — and that if the caller's retained
  expected value is itself replaced too, pure validation cannot detect it.
  The proposal states this limitation explicitly (Sections 8, 13, 17) instead
  of overclaiming authentication; this matches the accepted EA boundary
  ("EA-001 ... adds no ... authentication," CLAUDE.md).
- `evidence_completeness` is never conflated with the fingerprint relation:
  Section 12.3's table keeps aggregate evidence-completeness derivation
  (from classification/alignment coverage) independent of the
  fingerprint-relation gate, matching the real contract's separate fields.

No blocking contradiction found.

## 6. Contract/status reachability audit (Section 9, checks 5)

- Every literal cited in Section 9 corresponds to a distinct, independently
  reachable real-world condition traced above (declaration admission via
  `TransitionDeclarationConclusion`/`TransitionDeclarationLineageSummary`;
  endpoint pin alignment via the real `TransitionEndpointPinAlignment`
  literal, confirmed identical string-for-string to
  `model_kernel/transition_results.py:34-41`; alignment/evidence literals
  confirmed against `evidence_alignment/contracts.py` and
  `evidence_assurance/contracts.py`).
- `TransitionAssessmentConditionTrace` proposes both `semantic_candidate_index`
  and `value_candidate_index` as separate fields even though the underlying
  contracts guarantee they are always numerically equal by construction
  (Section 3 finding). This is redundant but not incoherent: carrying both
  independently-sourced values and comparing them is a legitimate
  defense-in-depth disclosure consistent with the project's "never trust an
  assumed index domain" ethos (non-blocking observation #2).
- `TransitionAssessmentInputErrorCode` has exactly one literal
  (`TRANSITION_ASSESSMENT_INPUT_INVALID`) covering every malformed-input,
  hostile-graph, and invalid-alignment-collection case (T22, T29-33, T50-53).
  This single-code pattern for "malformed input" is consistent with the
  project's established practice of separating typed input errors (single
  code, safe fixed text) from structured non-executed results (many
  literals) — it does not collapse any status the acceptance matrix actually
  needs to distinguish, since T29 vs T30 vs T31 etc. are distinguished by
  test assertions on message content/count, not by separate codes, and the
  proposal never claims otherwise.

No blocking contradiction found; no necessary status is collapsed.

## 7. Hostile-input/resource-bound audit (Section 6, check 6)

- The 134,217,728-byte (128 MiB) aggregate canonical-request bound has a
  direct, defensible precedent: EA-001's accepted
  `maximum_retained_metadata_bytes` is `67108864` (64 MiB) — a per-snapshot
  bound (`evidence_assurance/contracts.py:284,660`). TA-001's 128 MiB
  aggregate bound (covering an entire request with two classifications, one
  transition result, and up to 128 alignments) being exactly double a single
  EA metadata cap is a defensible, conservative extrapolation, not an
  arbitrary number.
- **No comparable precedent exists** for the proposed 2,000,000-node or
  128-depth aggregate hostile-graph bounds. The only related constant found
  anywhere in `backend/` is `data_sources/extractors/operational.py`'s
  `max_depth: int = 64`, which governs raw JSON nesting depth during
  operational-evidence *extraction* — a different layer, different object
  kind, and half the proposed TA depth bound. No existing package in this
  repository demonstrates that a strict Pydantic `model_validate` boundary
  can safely reconstruct 2,000,000 nested nodes at 128 levels of depth
  without unsafe allocation, recursion-limit exhaustion, or repeated-
  reconstruction amplification (Section 10's "full-instance reconstruction"
  reconstructs at least twice: once at request admission, once again at
  `DeclaredTransitionAssessmentResult.model_validate`). This is a genuine gap
  between what Section 6 asserts ("can actually be enforced") and what has
  been demonstrated anywhere in the codebase (**required correction #1**,
  detailed in Section 12).
- Owner question 2 (Section 19) asks only about the byte bound; it does not
  ask about the node/depth bounds at all, even though those are the harder
  bounds to defend. This is itself a gap in the proposal's own owner-question
  scoping (folded into required correction #1).
- Cycle rejection, hidden-extra/private-cache laundering rejection, and
  boolean-index rejection are all real, already-implemented patterns reused
  from EA/ST (`_reject_hostile_supplied_graph` wrap validators,
  `_inspect_supplied_graph`, per-field `StrictInt`/`Field(ge=0)` patterns
  visible in `model_kernel/transition_results.py:67-76` and
  `state_classification/contracts.py`). TA-001 proposes reusing this same
  proven pattern rather than inventing a new one — this is a positive
  finding, not a gap.

## 8. Architecture/import audit (Section 4, check 7)

- Confirmed by direct search: no file under `backend/` imports
  `backend.transition_assessment` or `backend.evidence_alignment` from a
  lower package (`evidence_alignment`, `model_kernel`, `state_classification`,
  `observation_compatibility`, `semantic_compatibility`,
  `constraint_evaluation` do not reference either). The proposed leaf
  placement (`backend.transition_assessment` importing only
  `model_kernel`, `state_classification`, `evidence_alignment` public roots)
  does not currently create or require any reverse dependency.
- `backend/transition_assessment` does not exist yet, so the "no existing
  package may import it" constraint is trivially true today and only needs
  enforcement going forward (an import-isolation test, which the proposal's
  Section 15 test-plan closing paragraph already requires).
- The proposal's rejection of an orchestration facade (Section 3, Section 16
  point 3) is architecturally coherent: the pure composition operates only on
  already-computed public results supplied by the caller, and no accepted
  public fact in `model_kernel`, `state_classification`, or
  `evidence_alignment` requires TA-001 to compute those results itself. No
  concrete accepted fact was found that makes the "no facade" position
  incoherent.

No blocking contradiction found.

## 9. Preservation/determinism audit (Section 14, check 8)

- The proposal explicitly requires all pre-TA canonical IDs, records,
  memberships, revisions, FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and prior
  EA/ST/CN contracts to remain unchanged, and requires positive TA tests to
  use disposable synthetic worlds "because the authoritative demo has no TRG,
  TRD, or TRW" — this matches the verified baseline (Section 1) exactly; the
  demo genuinely has zero TRG/TRD/TRW, so no positive TA row can be tested
  against the authoritative fixture without inventing an unauthorized
  ledger append. The proposal correctly avoids that trap.
- Canonical-byte determinism claims (Section 11: sorted keys, `ensure_ascii
  =False`, `allow_nan=False`, UTC-normalized shortest fractional form,
  forbidden floats) match the pattern already established by prior
  milestones' canonical-serialization sections (e.g., FL-001/EA-001's
  documented canonical byte rules), so this is a reused, previously-validated
  approach rather than a new invented scheme.

No blocking contradiction found.

## 10. T01-T62 matrix audit (Section 15, check 10)

Full architecture-level verification (Sections 3-9 above) plus targeted spot
checks of the highest-risk rows:

- **T01-T03** (positive/negative conclusion): grounded in Section 12.4's
  table, itself grounded in real `StateComputedMatch` literals
  (`matches`/`does_not_match`, `state_classification/contracts.py:39-42`
  reported by sub-investigation). Executable and correctly scoped.
- **T29-T34** (alignment-collection attacks: omit/duplicate/add/reorder/
  substitute/repeat-instead-of-reuse): all six are expressible purely from
  object-equality checks on `request.compatibility` per Section 3's proof;
  no lower contract gap prevents any of them from being constructed as a
  genuinely distinct, executable test.
- **T39-T40** (fingerprint substitution limits): correctly scoped to the real
  `expected_fingerprint_relation` and `embedded_fingerprint_relation` fields
  confirmed in Section 5 of this audit; T40's "may remain structurally
  coherent... no authentication claimed" wording is honest given the real
  contract has no mechanism to detect a fully coherent triple substitution.
- **T50-T53** (hostile-graph/forged-result rejection): reuse the
  already-proven `_reject_hostile_supplied_graph` / `_inspect_supplied_graph`
  pattern (Section 7 of this audit); executable without a new detection
  mechanism.
- **T59-T60** (historical replay / preservation inventory): directly
  checkable against the verified baseline in Section 1 of this audit.
- No duplicate row was found presenting identical coverage under a different
  ID; T02/T03 test the two independent endpoints separately with an explicit
  distinct expectation ("no non-occurrence wording" is asserted per-row,
  which is a genuine, non-duplicated check per Section 15's own text).
- One coverage gap: the matrix has no dedicated row asserting that the two
  redundant index fields identified in Section 6 of this audit
  (`semantic_candidate_index` vs `value_candidate_index` on
  `TransitionAssessmentConditionTrace`) are cross-checked against each other
  and reject on divergence rather than silently trusting one. This is a
  genuine but narrow matrix gap (non-blocking observation #3; recommended
  addition, not a blocking finding, since Section 10's general reconstruction
  rule already implies the check).

No row was found that requires an invalid lower result to reach a public
status, and no row was found requiring an attack the proposal's own contracts
do not actually expose.

## 11. Exact blocking findings

None. No contradiction was found between the frozen proposal and the
accepted public contracts, derivations, exports, or historical acceptance
records inspected during this audit.

## 12. Exact required corrections

1. **Unjustified hostile-graph node/depth bounds (Section 6; Section 7 of
   this audit).** The proposed `maximum_reconstructed_nodes = 2000000` and
   `maximum_nesting_depth = 128` have no precedent anywhere in `backend/`
   (the only related constant, `data_sources/extractors/operational.py`'s
   `max_depth = 64`, governs a different layer/object kind at half the
   proposed depth) and no accompanying memory/CPU analysis, unlike the byte
   bound which is a defensible 2x extrapolation of EA-001's accepted
   `maximum_retained_metadata_bytes = 67108864`. **Smallest correction:**
   before Slice A implementation, either (a) run a bounded implementation
   spike measuring actual Pydantic `model_validate` cost (time and peak
   memory) at the proposed node/depth bounds for the two-pass reconstruction
   Section 10 requires, and record the result in the accepted design, or
   (b) lower the node/depth bounds to values with a demonstrated-safe
   precedent (e.g., derive them from the existing 64-condition/128-trace/
   128-alignment structural limits already in Section 6's own limits table,
   which bound the graph shape far more tightly than 2,000,000 nodes would
   suggest). Owner question 2 must be expanded to cover the node/depth
   bounds explicitly, not only the byte bound.
2. **Owner question 2 is scoped too narrowly (Section 19).** As written, it
   asks the owner to approve only the 134,217,728-byte bound. Given finding
   1, the genuine open policy decision is the full hostile-graph bound triple
   (bytes, nodes, depth), not the byte figure alone. **Smallest correction:**
   restate owner question 2 to request approval of all three limits together,
   with the byte figure's EA-001 precedent cited explicitly and the node/depth
   figures either justified by a spike or lowered as in correction 1.

## 13. Non-blocking observations

1. The "six-field locator" terminology used throughout the proposal is
   inherited verbatim from EA-001's accepted `scope_relation:
   Literal["six_field_locator_equal", ...]`, even though the underlying
   `Ds004OperationalEvidenceScope` has seven fields. This predates TA-001 and
   is not a defect the proposal introduces; a future documentation pass could
   rename the EA literal, but that is out of TA-001's scope.
2. `TransitionAssessmentConditionTrace` carries both `semantic_candidate_index`
   and `value_candidate_index`, which are always numerically equal by the
   accepted contracts' own invariants (Section 3/6 of this audit). This is
   redundant but harmless disclosure, consistent with the project's
   never-assume-index-identity discipline.
3. The acceptance matrix has no row explicitly asserting rejection when the
   two redundant index fields in observation 2 diverge on a forged input;
   recommend adding one row under the T50-T54 forged-derivation family.
4. Section 19 owner question 1 (strict matched-fingerprint requirement for
   both positive and negative conclusions) is a genuine, owner-appropriate
   policy question; nothing in the accepted architecture forces one answer
   over the other, so this audit defers to the proposal's own recommendation
   rather than substituting a different policy preference.
5. The proposal's explicit statement that a positive TA test must use a
   disposable synthetic world (Section 14) is correctly forced by the
   verified baseline fact that the authoritative demo has zero TRG/TRD/TRW;
   this should be reiterated in the Slice A/B owner gate text so a future
   implementer does not mistake "disposable" for "may be committed as a
   fixture."
6. Section 9's `TransitionAssessmentIssueCode` list has 21 literals covering
   every admission/evidence failure path enumerated in Sections 7-8; no gap
   was found, but the list's completeness could only be finally confirmed by
   an implementation-time exhaustiveness test (already required by the
   proposal's own Section 12.5 reachability claim), so this is left as an
   implementation-time verification item rather than a design defect.

## 14. Owner-question adjudication

1. **Strict matched independent fingerprint required for every governing
   observation (positive and negative execution).**
   Adjudication: `endorse_as_written`.
   Consequence: this permanently forbids any TA execution — positive or
   negative — over a governing observation whose expected fingerprint was
   omitted or not evaluated, at the cost of leaving otherwise-well-formed
   negative conclusions unexecuted when only fingerprint discipline is
   missing. Nothing in the accepted EA/alignment contracts requires a weaker
   rule, and the proposal's stated rationale (permitting `not_supplied` would
   materially weaken the evidence gate) is sound given EA-001's own
   assurance boundary.
2. **Aggregate 134,217,728-byte canonical-request bound.**
   Adjudication: `endorse_with_correction`.
   Consequence: approving the byte figure alone (as literally asked) would
   leave the harder node/depth bounds unapproved and unjustified by
   precedent (Section 12, correction 1-2). The permanent contract
   consequence of approving all three together is that a future increase to
   any of them becomes an explicit, re-gated admission-policy change; the
   correction only changes what gets approved now, not the mechanism.
3. **TA-001 v1 ends after pure composition plus adversarial hardening, no
   orchestration facade, no demonstration.**
   Adjudication: `endorse_as_written`.
   Consequence: this permanently defers per-condition source/horizon/
   fingerprint policy and any second consumer to a separately gated design;
   no accepted architectural fact makes a facade necessary now, and omitting
   it keeps the leaf-package import boundary (Section 8 of this audit)
   trivially satisfiable.

## 15. Corrected recommendation

Approve the TA-001 design **with** the two required corrections in Section
12 resolved before Slice A implementation begins: (1) either an
implementation spike demonstrating the 2,000,000-node/128-depth bound is
safely enforceable before unsafe allocation, or a replacement bound derived
from the existing structural limits, and (2) a restated owner question 2
covering the full hostile-graph bound triple rather than the byte figure
alone. No other section of the frozen proposal requires a design-level
change based on the accepted contracts, derivations, exports, tests, or
acceptance records inspected during this audit.

## 16. Scope confirmation

This audit created exactly one new file (this report) and modified no other
file. It did not create, alter, or append to any implementation, test,
fixture, ledger, identity, artifact, ADR, branch, commit, push, merge,
rebase, reset, cherry-pick, or history rewrite. The frozen proposal file was
read only; its bytes and digest are unchanged from Section 1's verification.
`.claude/settings.local.json` was left untouched. All investigation used
read-only `git`/`grep`/file-view commands and one read-only exploration
sub-task; no disposable probe wrote outside this report.

END OF TA-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
