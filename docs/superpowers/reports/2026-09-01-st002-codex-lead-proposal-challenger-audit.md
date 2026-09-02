# ST-002 Codex Lead Proposal — Independent Challenger Audit

**Status:** challenger audit report; owner decision pending

**Date:** 2026-09-01

**Audited artifact:**
`docs/superpowers/proposals/2026-09-01-st002-codex-lead-proposal.md`
(untracked design artifact, 1467 lines, SHA-256
`2a26a9409a9307c49c9e665b3db70274b5c69546bde9871ae255d4a26bd6e34e`)

**Repository baseline:** `main = origin/main = e44a18641ba6b440adcf9c10cd86d28376886942`

**Authoritative model:** 34 records at
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
zero transition records exist.

**Scope:** audit only. This report is a single challenger pass, not a second
architecture proposal. It does not rewrite or modify the Codex proposal and
it authorizes no implementation, identity allocation, fixture, record,
ledger, artifact, commit, push, merge, rebase, or other history operation.

---

## 1. Executive verdict

**`approve_with_corrections`.**

The proposal is safe, internally coherent, future-compatible, and — after the
corrections below — implementation-ready as a declaration-only ST-002
milestone. Every load-bearing claim was re-verified against the accepted
repository contracts: the lifecycle pattern the proposal extends is the exact
accepted BH/ST pattern; the identity, canonicalization, evidence, store,
replay, and hostile-revalidation machinery it names exists and behaves as
described; no introduced symbol, prefix, union arm, or literal collides with
or mutates any accepted contract; and the deferral of transition assessment
and occurrence is not merely defensible but forced by the accepted
ST-001/temporal evidence contracts.

No blocking finding survives verification. The five required corrections are
all acceptance-matrix enforcement gaps against normative statements the
proposal itself already makes — the architecture text needs no contract
change. The failure mode they defend against is the recurring historical one:
an implementation that drifts from its own stated semantics because no
executable row pinned the statement.

Findings: **0 blocking, 5 required corrections, 7 non-blocking observations.**

---

## 2. Repository verification and inspected sources

All baseline facts in proposal §2.1 were independently reproduced:

- Branch topology: `git rev-parse HEAD main origin/main` all resolve to
  `e44a18641ba6b440adcf9c10cd86d28376886942`; working tree otherwise clean
  (only the audited proposal is untracked).
- Public load: `backend.model_kernel.store.ModelStore('models/demo-printer').load()`
  returned exactly **34 records** at
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`.
- Store file inventory confirms 34 record files: 5 `reg_`, 3 `rtd_`, 4 `rel_`,
  2 `vrg_`, 1 `vsp_`, 2 `vsm_`, 1 `crg_`, 1 `vcn_`, 2 `prg_`, 6 `pif_`,
  1 `pcn_`, 1 `pcm_`, 1 `vpa_`, 1 `brg_`, 1 `bhd_`, 1 `srg_`, 1 `std_` —
  exactly one state identity, one parentless STD, **zero withdrawals of any
  kind**.
- State facts: SRG names `sta_ec739d80d5a843d28a91f4cf96de3883` with subject
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`; STD
  `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` names
  the same anchor, context `lifecycle_view / as_operated`, `supersedes=()`.
  Proposal §2.1/§2.5 hold: with self-transitions rejected, the authoritative
  ledger cannot host an honest non-self transition.

Inspected sources (all at baseline HEAD):

| Source | What it verified |
|---|---|
| `backend/model_kernel/canonical.py` | `_PREFIX_BY_KIND` has 22 kinds, none transition; `canonical_bytes()` algorithm is exactly §15.1 (exclude `record_id`, python-mode dump, UTC `+00:00`, sorted keys, compact separators, `ensure_ascii=False`, SHA-256); `compute_revision_id()` is exactly §15.4; `_behavior_effective_body_bytes`/`_state_effective_body_bytes` are the precedent for §15.3's `_transition_effective_body_bytes`. |
| `backend/model_kernel/contracts.py` | Anchor patterns; `AuthorityRef`; `AssertionContext` = `lifecycle_view \| view_independent`; six `EvidenceRef` arms with `ModelRecordEvidence` regex admitting 17 citable kinds and excluding every withdrawal kind; `_canonical_evidence` / `_canonical_parents` normalizers; `StateRegistration`/`StateDeclaration`/`StateDeclarationWithdrawal` shapes — the proposal's §7.2/§7.4/§7.5 templates are field-for-field precedented, including frozen + `extra="forbid"` + `revalidate_instances="always"` and the per-family parent-pattern/self-parent model validators; `ModelRecord` union has 21 arms, no transition kinds (additive extension point). |
| `backend/model_kernel/store.py` | `_pt_dag_indexes` enforces parent existence, same lineage key, acyclicity, and **single-root parentage** ("correction crosses independent roots" rejects); withdrawal admission is tip-only, single-withdrawal-per-target, and successor-after-withdrawal rejects via the superseded-target check (lines 1415–1433); STD admission pins are exact-record existence + anchor-naming checks with **no currentness gate** (lines 1354–1381); the uniform `_check_model_record_evidence` closure rule applies to every evidence-bearing claim; `validate_record_collection` docstring binds replay subsets ("reference-closed… currentness is membership-relative"); `append()` revalidates, verifies hash, validates the prospective full set, and promotes atomically with idempotent no-op re-append (§15.5 verified). |
| `backend/model_kernel/port_results.py` | `ModelQueryMaterial` carries the complete membership, revalidates via `validate_record_collection`, requires unique sorted IDs exactly equal to revision membership, recomputes the revision, and rejects bool/bad indices in `record_at` — §14.2's machinery exists as specified. |
| `backend/model_kernel/state_results.py` | `StateDeclarationConclusion` = `not_registered/not_declared/declared/conflicted/inactive`; `_state_declaration_payload` decision branches verified line-by-line against §13.2–§13.5; activity precedence `superseded → withdrawn → current` (lines 433–436) is exactly §13.9's defensive rule; entity-entry ordering `(anchor_id, first_root_id)` (lines 386–388) is §17.1's rule; payload recomparison ("disclosure is forged") is §14.2 step 11; the pre-normalization hidden-extras traversal is §14.2 steps 1–2. |
| `backend/system_identity/anchors.py`, `minting.py` | `StateAnchor`/`BehaviorAnchor` are the exact §6.1 template; `mint_state_anchor` is the exact §6.2 precedent; public minters mint UUID4 metadata-only anchors with no I/O. `system_identity` imports no model-kernel code (§16.2 direction holds today). |
| `backend/state_classification/contracts.py` | `StateComputedMatch` = `matches \| does_not_match` only; `StateTemporalAlignment` = `not_evaluated \| not_asserted` — §1.3/§2.2 claims hold: no persistence, exclusivity, or temporal alignment exists to compose. |
| `backend/temporal_state/` | `TemporalOccurrence` is a point fact with `change_class`; `latest_observed` selects one point at/before a cutoff — §2.3/§10.3 claims hold. |
| `docs/superpowers/specs/2026-08-30-st001-…-design.md` | §21.1 of the accepted ST-001 spec delegates the entire transition design space (identity, direction, triggers, occurrence, execution, dwell, history) to ST-002; its exclusions/limitations sections are consistent with every deferral the proposal makes. |
| Accepted adversarial matrices and rehearsal plans (VP/BH/ST) | The explicit historical membership list 9/10/11/14/16/18/28/29, extended to +32 by ST-001 Slice A and +34 by Slice D, is the standing replay convention — §17.2's list is correct and complete. |
| Prefix collision sweep | `grep -rn "trn_\|trg_\|trd_\|trw_"` over `backend/`, `models/`, `docs/adr/`: zero hits. §15.2's map extension is collision-free. |

---

## 3. Findings classified

| ID | Class | One-line summary |
|---|---|---|
| RC1 | Required correction | Matrix pins no row for a new TRD admitted against an already-stale (superseded/withdrawn) pinned STD, although §7.4/§8.3/§13.5 normatively require admission-with-honest-disclosure. |
| RC2 | Required correction | Matrix pins no parity row proving endpoint alignment is derived by delegating to the accepted ST derivation, not a parallel reimplementation. |
| RC3 | Required correction | Matrix pins neither the same-root merge arc (fork → merged → healthy) nor the cross-root-parent rejection, although §9.2 states both. |
| RC4 | Required correction | Matrix pins no negative row that `trw_` stays non-citable when the `ModelRecordEvidence` regex gains `trg_`/`trd_`. |
| RC5 | Required correction | Matrix pins no executable row for the four-query surface against the untouched authoritative 34-record ledger — v1's only authoritative behavior by default. |
| NB1 | Non-blocking | `declared` coexisting with stale endpoint pins is honest by design (Q6); disclosed, never retargeted; depends on RC1 for enforcement. |
| NB2 | Non-blocking | A transition whose every declaration root is withdrawn still reports `registered` at lookup — accepted registration-permanence precedent (SRG/BRG/entity), worth one Slice B documentation line. |
| NB3 | Non-blocking | The audit brief's "`stale`" disclosure is realized as two finer literals (`pinned_declaration_superseded`, `pinned_declaration_withdrawn`) plus the separate activity field — strictly more honest than a single stale flag. |
| NB4 | Non-blocking | §17.1's entity-entry tie-break "then first root ID" is unreachable under anchor uniqueness; harmless — it mirrors the accepted `states_of_entity` keying exactly. |
| NB5 | Non-blocking | §7.2's admission bullet list does not restate the uniform model-record evidence-closure rule (stated generally in §10.1); restate it in the Slice A checklist so a checklist-reading implementer cannot omit it. |
| NB6 | Non-blocking | Optional strengthening rows: idempotent equal-record re-append, contradictory same-ID append, `view_independent` context pin equality, and a forged alignment/activity precedence swap. |
| NB7 | Non-blocking | §9.2's cross-root prohibition is design text whose matrix row is carried by RC3; listed here only for traceability. |

---

## 4. Findings in detail

### 4.1 RC1 — stale pin at admission: admission and disclosure are unpinned

- **Exact proposal sections:** §7.4 (admission requirements), §8.3 (correction
  table, final row), §13.5 (alignment rows 3–4), §19.3/§19.4 (matrices).
- **Violated invariant / risk:** The proposal normatively states "A pinned STD
  need not remain current forever" and requires alignment, never gating, to
  disclose staleness. §19 has a row (S14) only for the *historical-replay*
  side of this (a later STD correction must not invalidate a stored TRD).
  Nothing pins the symmetric admission-side case: a **new** TRD pinning an
  STD that is already superseded or already withdrawn at admission time.
- **Minimal counterexample:** Disposable two-state fixture: admit SRGs, STDs,
  then correct STD_B → STD_B2 (superseding it), then append TRG and a new TRD
  pinning the *original* STD_B. Per §7.4 this must be admitted (existence,
  anchor-naming, and context checks all pass; there is deliberately no
  currentness check). An implementation that silently adds a currentness gate
  rejects it — diverging from the accepted architecture without detection —
  and an implementation that reports `exact_current` for the stale pin
  overclaims. No existing row fails either way.
- **Precise required amendment:** Add acceptance rows (proposed S15/Q15):
  new-TRD admission against an already-superseded pinned STD succeeds and
  discloses conclusion `declared` with that endpoint's alignment
  `pinned_declaration_superseded`; the withdrawn-pin twin succeeds with
  `pinned_declaration_withdrawn`; and no automatic retarget to STD_B2 occurs.
- **Required test:** The fixture sequence above, asserted end-to-end through
  `transition_declaration()` on the resulting membership.

### 4.2 RC2 — single derivation source for endpoint alignment is unpinned

- **Exact proposal sections:** §21.3 ("endpoint alignment derived through the
  accepted state model logic"), §13.5, threat-table row "Forged endpoint
  alignment / Recompute using authoritative state query derivation" (§18),
  §19.4.
- **Violated invariant / risk:** One authoritative lifecycle/conclusion
  derivation per concept. The accepted ST conclusion derivation
  (`state_results._state_declaration_payload` and its root-health,
  agreement-finding, and activity branches) is the only place the five-literal
  state conclusion exists. If Slice B re-implements that logic inside the
  transition module instead of importing it, a later ST repair changes state
  semantics while transition alignment silently disagrees — producing results
  that are internally consistent yet contradict `state_declaration()` on the
  same `(anchor, context, material)`. This is precisely the defect class of
  past owner-mandated repair slices.
- **Minimal counterexample:** A conflicted state lineage (same-root fork) for
  the from-endpoint anchor. A copied derivation that mis-ranks the precedence
  in §13.5 (e.g., reports `pinned_declaration_superseded` instead of
  `endpoint_state_conflicted`) passes every transition-internal fixture while
  disagreeing with the public ST result on identical material.
- **Precise required amendment:** Add an acceptance row requiring value parity
  between each endpoint row's `state_declaration_conclusion` in the
  transition results and the public `state_declaration()` result for the same
  `sta_` anchor, exact context, and carried material — across fixtures
  producing every state conclusion literal — and require the Slice B plan to
  name the shared derivation entry points it imports.
- **Required test:** Parametric parity test over disposable fixtures spanning
  `declared` / `conflicted` / `inactive` state conclusions ×
  `current` / `superseded` / `withdrawn` pin activities, asserting equality
  of conclusion and precedence against the public ST query result.

### 4.3 RC3 — same-root merge arc and cross-root parent rejection are unpinned

- **Exact proposal sections:** §9.2 ("A nonempty parent tuple creates a
  correction/merge… cross-root convergence is invalid"), §19.3 (S04–S09).
- **Violated invariant / risk:** The accepted lifecycle (`_pt_dag_indexes`)
  admits multi-parent corrections **within** one root and rejects parent
  tuples spanning roots ("correction crosses independent roots"). §9.2
  restates both. But S04 pins only wrong-key parents, S05 pins
  duplicate/unsorted/self/missing/cyclic parents — neither pins the
  **cross-root parent rejection**, and no row pins the positive merge arc.
- **Minimal counterexample:** (i) In one root: fork T1←T3 and T2→T3-style tips
  T1,T2 (distinct bodies); append T4 with `supersedes=(T1,T2)` — must admit
  and return the root to `healthy` with T1/T2 `superseded`. (ii) With two
  roots R1,R2: append T5 with one parent in each root — must reject with the
  typed lineage-invalid error. An implementation that rejects all multi-parent
  corrections, or fails to detect cross-root parentage, passes every existing
  §19.3 row.
- **Precise required amendment:** Add rows (proposed S16/S17): same-root
  two-parent merge admitted and resolves the fork to healthy; cross-root
  parent tuple rejects typed.
- **Required test:** Disposable lifecycle fixture asserting admission, tip
  recomputation, root health transitions, and the typed cross-root rejection.

### 4.4 RC4 — `trw_` non-citability after the evidence-regex extension is unpinned

- **Exact proposal sections:** §7.1 ("TRW records are not citable"), §21.2
  ("evidence-reference extension for TRG/TRD only"), §10.1, §19.2.
- **Violated invariant / risk:** The accepted `ModelRecordEvidence` regex
  admits exactly 17 record kinds and excludes every withdrawal kind
  (`stw_`, `bhw_`, `vpw_`, `ptw_`, `rwd_`). Slice A must extend it to admit
  `trg_` and `trd_` — itself required, since §7.4's mandatory TRD→TRG
  citation is `model_record` evidence. A regex overshoot admitting `trw_`
  silently makes withdrawals citable; because no happy-path fixture ever
  cites a `trw_`, nothing fails.
- **Minimal counterexample:** Extension written as `tr[gd]w?` or
  `(trg|trd|trw)`: a synthetic record whose `model_record` evidence names a
  well-formed `trw_` ID then validates — a contract violation invisible to
  every other row.
- **Precise required amendment:** Add a row (proposed R10): a `trw_`-shaped
  `model_record` evidence citation fails pattern validation; `trg_`- and
  `trd_`-shaped citations are admitted (the R09 golden-vector row continues
  to prove all 17 existing arms unchanged).
- **Required test:** Unit-level `EvidenceRef` validation tests for all three
  transition prefixes (two positive, one negative), plus a store-level
  citation-closure test proving a TRD's mandatory TRG citation validates.

### 4.5 RC5 — the authoritative zero-transition query path is unpinned

- **Exact proposal sections:** §20.1–§20.2 (34-record default), §17.2, §19.6
  (P01/P02), §11, §13.
- **Violated invariant / risk:** With the ledger held at 34 records, the only
  transition behavior v1 exhibits against the authoritative store is the
  *absence* surface: lookup `not_registered`, entity collection `registered`
  with zero entries, assertion `not_found`. P01/P02 pin byte preservation and
  replay, but no row executes the four new public queries against the real
  34-record membership.
- **Minimal counterexample:** An entity-collection implementation that
  implicitly assumes ≥1 transition (indexing `roots[0]`, say) passes all
  disposable fixtures yet crashes or mis-reports on the real ledger's
  zero-transition entity. Nothing in §19 detects this.
- **Precise required amendment:** Add rows (proposed Q16–Q18 or P09): on the
  untouched authoritative ledger at
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`:
  `transition()` with a syntactically valid absent `trn_` returns
  `not_registered`; `transitions_of_entity()` for
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` returns `registered` with empty
  entries; `transition_assertion()` with syntactically valid absent
  `trg_`/`trd_`/`trw_` IDs returns `not_found` for each prefix.
- **Required test:** A demo-ledger test module in the accepted
  `test_demo_pt001.py` / `test_demo_st001.py` style asserting the three
  behaviors against the real store without mutating it.

### 4.6 Non-blocking observations

- **NB1 (§8.4, Q6):** A `declared` transition beside a
  `pinned_declaration_superseded` endpoint is an honest compound statement
  ("the declaration is current; the pinned meaning is historical"). The
  rejected alternative (implicit invalidation) would make state corrections
  silently rewrite transition lifecycle — the conflation the accepted ST pin
  architecture exists to prevent. No amendment; enforce through RC1/RC2.
- **NB2 (§11.1, §13.1):** Lookup status is registration-scoped: a transition
  identity with all declaration roots withdrawn is still `registered`. This
  matches the accepted precedent exactly (an entity, state, or behavior
  registration is likewise permanent and withdrawal-free). Slice B
  documentation should keep the one sentence making clear that lookup answers
  registration existence, never lifecycle.
- **NB3 (§12.3, §13.5):** The brief's "`stale`" requirement is realized by
  the pair of exact pin-activity literals in `alignment` **plus** the
  independent `pinned_declaration_activity` field, which survives even under
  conflict/inactive precedence. This is strictly more informative than a
  single stale flag and needs no generic literal.
- **NB4 (§17.1):** "entity entries: transition anchor ID, then first root ID"
  — the tie-break is dead code because anchor uniqueness is a store
  invariant. Harmless; it is byte-for-byte the accepted
  `states_of_entity` ordering discipline.
- **NB5 (§7.2, §10.1):** The uniform model-record evidence closure rule is
  stated generally in §10.1 but omitted from §7.2's bullet list. The Slice A
  checklist should restate it so no checklist-reading implementer omits the
  mandatory `_check_model_record_evidence` call for the new families.
- **NB6 (§19):** Optional strengthening rows, none required for acceptance:
  idempotent re-append of an equal TRD/TRW (store no-op), contradictory
  same-record-ID append rejection, a `view_independent` instance of the
  context-equality admission check (§7.4), and a forged
  alignment↔activity precedence swap under §14.3.
- **NB7 (§9.2, §19.3):** The cross-root convergence prohibition exists as
  design text; its executable row is folded into RC3. Traceability only.

---

## 5. Direct adjudication of the eight owner questions

**Q1 — ratify the declaration-only boundary? Endorse.** Independently
re-verified: the classifier's only positive computed value is
`matches` (`StateComputedMatch`), its temporal alignment is always
`not_asserted` in this configuration, `TemporalOccurrence` is an immutable
point fact, `change_class` compares exact serialized values along one
locator, and the BH cohort gate proves shared acquisition envelope only.
The proposal's §1.3 impossibility argument is correct: no accepted contract
proves endpoint occupancy, exit, entry, exclusivity, or causal order, so
evidence-consistency assessment genuinely cannot be built from existing
evidence. The deferral is forced, not tactical.

**Q2 — same-subject endpoints? Endorse.** Enforcement is complete at all
four points the brief names: append (§7.2 admission), load (full-set
`validate_record_collection`), replay (replay subsets pass the same
validation; currentness is membership-relative), and result reconstruction
(§14.2 step 7 re-runs full-set validation over carried material). The
restriction mirrors the accepted ST-001 subject rule (every state target
variable's embedded owner must equal the SRG subject) and relaxes additively
later: a future cross-entity participant policy permits new registrations
without invalidating any historical membership.

**Q3 — reject self-transitions in v1? Endorse.** Without event, trigger,
action, or re-entry semantics a self-edge has no honest disclosed
distinction from the state declaration itself; §6.6's reasoning is sound.
Relaxation is additive (a future accepted discriminator admits new
registrations) and does not rewrite history. Note this constraint is what
makes the current 34-record ledger incapable of hosting any valid transition
— §2.5's honest consequence, correctly accepted rather than worked around.

**Q4 — one identity per ordered same-subject endpoint tuple? Endorse, with
the mechanism distinction spelled out.** The three concepts the brief
demands not be conflate are in fact kept distinct by this proposal:

- *Multiple evidence roots about one transition* — supported today:
  independent parentless TRDs under one anchor corroborate (identical bodies)
  or conflict (different bodies). Correct and sufficient for multi-authority
  claims.
- *Genuinely different transition mechanisms sharing endpoints* — v1 has no
  mechanism vocabulary, so two such TRGs would be semantically
  indistinguishable duplicate edges; rejecting them is the honest behavior.
  The uniqueness invariant is a **membership-relative admission rule**, not
  an identity-encoding, so when a future accepted trigger/event/action
  discriminator exists, relaxing it admits new registrations without
  invalidating or reinterpret­ing any historical membership. The residual
  debt — an "undifferentiated" anchor predating the discriminator — remains
  disclosable (its lineage can be corrected/withdrawn) and past conclusions
  stay honest because they quote the anchor *as declared at the time*. No
  permanent collapse results.
- *Future occurrence instances of one declared transition* — outside the
  identity plane entirely; they belong to the deferred assessment/occurrence
  milestone and are unaffected by this invariant.

**Q5 — state families and context mapping stay out? Endorse.** Exact-context
STD pinning (context equality at admission, exact-context lifecycle key with
cross-context parentage invalid) is the anti-drift mechanism; family or
cross-context semantics would require new identity, lifecycle, winner, and
ambiguity contracts that do not exist and cannot be inferred. Because
transition identity is not context-encoded, a future family milestone is a
new declaration family or context kind — additive.

**Q6 — alignment orthogonal to TRD conclusion? Endorse.** The transition
lifecycle and the state lifecycle are independently correctable; gating one
on the other would let a routine STD correction silently rewrite transition
history — the precise silent-meaning-change failure the pin architecture
exists to prevent. Both facts are disclosed (conclusion + per-endpoint
`state_declaration_conclusion` / `pinned_declaration_activity` /
`alignment`), nothing is retargeted. This stays honest only with RC1's
admission-side rows and RC2's parity rows in force.

**Q7 — hold the authoritative demo at 34 records? Endorse.** The new
contract surface is fully exercisable in disposable roots: a synthetic
two-state model built through public builders/minters covers TRG/TRD/TRW
admission, forks, merges, corroboration, withdrawal, alignment precedence,
queries, revalidation, and replay (precedent: the accepted BH-001/ST-001
disposable rehearsal roots). Nothing about content-addressed records makes
the authoritative ledger necessary for contract coverage — and §20.2
correctly enumerates and forbids every dishonest way of manufacturing a
demo. Endorsement stands provided RC5 makes the zero-transition
authoritative path itself executable evidence rather than an assumption.

**Q8 — ratify `trn_`/`trg_`/`trd_`/`trw_` and the four-query surface?
Endorse.** Verified collision-free (zero hits across `backend/`, `models/`,
`docs/adr/`); the four names mirror the accepted ST-001 surface
(`state` / `state_declaration` / `states_of_entity` / `state_assertion`)
one-for-one; the literal vocabularies reuse the accepted five-literal
conclusion grammar and contain no occurrence-flavored words; §11.5's
forbidden-alias list is complete against the obvious smuggling paths.

---

## 6. Contract and identity audit

- **Anchor (§6.1):** `TransitionAnchor` is field-for-field the accepted
  `StateAnchor`/`BehaviorAnchor` template (opaque 32-hex ID, bounded
  namespace/display/role metadata, frozen, extras forbidden, always
  revalidated, no semantic fields). `trn_[0-9a-f]{32}` does not collide with
  any existing pattern.
- **Minting (§6.2):** `mint_transition_anchor()` is the accepted
  `mint_state_anchor` precedent: UUID4, metadata-only, no I/O, no
  deterministic mode, never called during replay. Consistent.
- **Permanence split (§6.3, §8.1):** permanent registration pins opaque
  endpoint *anchors*; correctable declarations pin exact STD *records*. This
  is precisely the accepted SRG/STD split (SRG permanently names constraint
  anchors; STDs pin exact VCN records correctably) and is the correct answer
  to the brief's question: permanent endpoint identity survives endpoint
  *meaning* corrections without churn, while exact pins prevent silent
  meaning drift. The rejected alternatives (permanent record pins → identity
  churn per correction; anchor-only pins → silent drift) are correctly
  identified.
- **Direction (§6.4):** ordered fields, never sorted; reversal requires a new
  anchor — matches the accepted BH participant-order precedent. Verified the
  canonical algorithm preserves tuple order, so order changes change bytes
  and therefore IDs (R06 sound).
- **Record shapes (§7.2–§7.5):** TRG mirrors the registration template
  (anchor, permanent subject/links, evidence, audit fields; no context,
  parents, or lifecycle); TRD mirrors the declaration template (key fields,
  exact-context, canonical parent tuple via the `_canonical_parents`
  precedent, per-family parent-pattern and self-parent validators
  precedented in STD/VCN); TRW mirrors STW exactly: `withdraws` target plus
  audit fields only, no evidence — confirmed against the accepted
  `StateDeclarationWithdrawal` fields. The deliberate omission of an
  `evaluation_basis` field from TRD (§7.4) is the correct distinguishing
  decision: ST's STD and BH's BHD carry that field because upper layers
  evaluate them; ST-002 defines no evaluation algorithm.
- **Effective body (§9.3, §15.3):** four fields including the anchor —
  consistent with the accepted state body (`state_anchor_id`, `context`,
  `conditions`, `evaluation_basis`); evidence/parents/audit excluded; the
  private-bytes primitive has direct precedent.
- **Evidence policy (§7.2, §7.4, §10.1):** mandatory role-specific direct
  citations (TRG→ subject `reg_` + both `srg_`; TRD→ `trg_` + both `srg_` +
  both pinned `std_`) plus at least one owner-declaration basis, with the
  uniform closure rule — field-for-field the accepted SRG/STD admission
  pattern (store lines 1292–1325, 1354–1381). The deeper closure
  (CRG/VCN behind the pinned STDs) is correctly left to the STD's own
  ST-001 admission rather than re-checked by TRD admission — correct
  layering. The required regex extension for the TRD→TRG citation is exactly
  RC4's subject.
- **Vocabulary (§12.1):** every transition literal maps to an accepted
  five-literal conclusion grammar instance; forbidden occurrence-like
  literals are absent — verified the ST equivalents exist and the proposal's
  tables use them with identical meaning.

---

## 7. Lifecycle, replay, and store-integrity audit

- **DAG rules (§9.1–§9.6)** match `_pt_dag_indexes` exactly: parent exists in
  family, same `(anchor, context)` key, acyclic, **single-root parentage**
  (cross-root convergence rejects — store line 280–284), canonical sorted
  unique parents. The proposal's §9.2 statement is accurate; RC3 pins it
  executably.
- **Root health / cross-root agreement (§9.4–§9.5)** match the accepted
  derivation branch-for-branch — including the subtle verified behaviors:
  same-root forks conflict even with byte-identical bodies; `one_healthy_root`
  coexists with `same_root_conflict` or `inactive_roots_present`; conflicted
  or body-disagreeing healthy sets force `conflicted` regardless of how many
  roots corroborate; IDs order disclosure only, never select winners. No
  cross-root convergence, partial convergence, winner selection, or
  authority/time-based resolution exists anywhere — confirmed against both
  the proposal's tables and the accepted code.
- **Withdrawal (§9.6)** matches the accepted admission exactly: current
  unsuperseded tip only, at most one withdrawal per target, and
  successor-after-withdrawal invalid in one membership (the store rejects it
  via the superseded-target check regardless of append order — verified at
  lines 1415–1433); membership-relative, never deletion.
- **Replay (§9.7, §17.2):** conclusions are membership-relative; no
  wall-clock enters any decision table; the historical membership list is the
  standing accepted convention (verified across VP/BH/ST matrices and
  rehearsal plans); predecessor bytes and aggregate immutability are pinned
  by P01–P03. Exact-context rules prevent silent meaning change **without**
  impeding replay: admission-time context equality binds only the membership
  being admitted; a historical membership replaying its own historical STD
  re-derives its own historical conclusion.
- **Store integrity (§15):** existing `ModelStore`, `mrv_` revision, no new
  store/cache/revision; full-set validation at load, at every prospective
  append, and inside `ModelQueryMaterial` revalidation — all verified in
  code. The tuple-uniqueness and anchor-uniqueness invariants (§6.7, §7.2)
  are ordinary per-membership full-set invariants, enforced identically at
  append, load, replay, and result reconstruction; they require no new
  machinery beyond indexes of the accepted kind.

---

## 8. Query/result revalidation audit

- **Surface (§11):** four read-only `ModelQueries` methods over one injected
  `LoadedModel`; no names, discovery, cutoff, source selector, traversal, or
  context inference — matches the accepted ST surface constraints.
- **Carry-once (§12.2):** one complete `ModelQueryMaterial` per outer result
  with strict-integer indices and full-membership reconstruction — the
  machinery exists (`ModelQueryMaterial` revalidates the complete collection
  through `validate_record_collection`, requires unique sorted IDs exactly
  equal to revision membership, and recomputes the revision). Store-independent
  reconstruction of every conclusion is therefore guaranteed: material
  revalidation alone re-derives registration existence, same-subject
  enforcement, pin existence, lineage roots/tips, activities, and withdrawals,
  and the payload recomparison binds every disclosed field to that derivation.
- **Forgery coverage (§14.2–§14.3):** the 12-step sequence is the accepted
  one (hidden-instance-extra rejection before normalization, strict ints with
  booleans excluded, exact membership/revision equality, full-set validation,
  plain-content reconstruction, complete payload recomputation and equality,
  private-material binding only after equality). Every forgery class the
  brief names — membership, endpoints, contexts, roots, tips, alignment,
  ordering, indices, IDs, nested models — is rejected either by material
  revalidation (ID/content/membership/lineage classes) or by payload
  recomparison (conclusion/alignment/ordering/role/activity classes). Verified
  against the accepted `StateDeclarationResult`/`StateAssertionDisclosureResult`
  coherent-validators.
- **Decision-table completeness (§13):** checked against the accepted ST
  derivation line-by-line. All five conclusion literals are reachable and
  partitioned; the §13.5 alignment lattice is structurally complete — the
  unpinned-context cases (`not_registered`/`not_declared`) are unreachable
  because admission and full-set validation guarantee every pinned STD's
  lineage exists in the TRD's exact context, and `declared + current` implies
  the pin is an admitted current tip (a current record is by definition an
  active tip of its root); the conflicted/inactive precedence is preserved
  without destroying per-record activity truth, which survives in the
  separate `pinned_declaration_activity` field. §13.9's successors-first
  precedence is the accepted defensive rule for the unreachable
  successor-and-withdrawal combination.
- **Representative/group ordering (§12.4–§12.5, §17.1):** smallest-ID
  representative and canonical-body-bytes group ordering are the accepted
  deterministic disclosure devices; no winner semantics.

---

## 9. Temporal and non-inference audit

- No model query takes a cutoff; `recorded_at` is audit metadata only and
  appears in no conclusion derivation (verified: §13 tables reference no
  time field; §10.2/§18 forbid timestamp semantics — consistent with the
  accepted pattern where ordering is ID/bytes-based).
- The proposal introduces no occurrence, current-state, causality, control,
  safety, health, or recommendation semantics (§3.3, §4.2–§4.3, §12.1, §18,
  T01–T07) — and neither does any contract it names: the four-result
  vocabulary contains no literal capable of asserting them.
- The impossibility claim the brief asks about — whether any transition
  assessment could honestly rest on existing independent-latest ST-001
  evidence — was independently verified: **no.** `matches` is revision- and
  evidence-relative point satisfaction with `not_asserted` temporal
  alignment, multiple simultaneous `matches`, no persistence, no exit/entry,
  no exclusivity; `TemporalOccurrence`/`latest_observed`/`change_class`
  supply none of the missing prerequisites. §1.3 and §10.3 state this
  accurately and §10.4 correctly enumerates the gating prerequisites a future
  milestone must separately owner-accept.
- The bounded exclusions (families, self/cross-entity edges, parallel edges,
  triggers/guards/actions) are all additive-later: none is encoded into a
  permanent identity or contract in a way that a future accepted extension
  cannot relax for new memberships while preserving every historical replay.

---

## 10. Import-direction and scope audit

- **Package ownership (§16.1)** places anchor/minter in `system_identity`,
  records/store/queries in `model_kernel`, and defers assessment to a later
  upper layer. Verified the current direction holds: `system_identity`
  imports no kernel code; the transition result module will import the
  kernel-internal state derivation (RC2) without touching
  `state_classification`, `constraint_evaluation`, binding, interpretation,
  temporal, or data-source packages.
- **Union/dispatch/extension additivity (§15.2, §16):** the `ModelRecord`
  union gains three arms (existing-kind rejection preserved — unknown kinds
  still fail via `_PREFIX_BY_KIND` and the discriminated adapter); store
  family dispatch gains parallel maps/indexes of the accepted kind; the
  evidence regex extension is two tokens; golden vectors of all 21 existing
  kinds are untouched (R09); the 22-prefix map gains three non-colliding
  entries (grep-verified). Historical replay is byte-identical because
  canonicalization is per-record-class and the revision hash inputs
  (model ID + sorted record IDs) are unchanged in form.
- **Scope discipline:** no transition-assessment package, evaluator,
  occurrence record, store, ledger, revision, cache, projection, query
  alias, or demo append is introduced; §20/§21 keep the authoritative ledger
  at 34 records and fence every demo path behind separate owner gates. The
  proposal remains strictly inside the space the accepted ST-001 spec §21.1
  delegated to ST-002.
- **Same-subject enforcement completeness** (append, load, replay, result
  reconstruction): complete by construction — all four paths run the same
  full-set validation; there is no fourth unvalidated path because results
  are bound to revalidated material before any disclosed field is readable.

---

## 11. Missing adversarial acceptance cases

Ranked; the first five are the required corrections of section 4, the rest
optional strengthenings:

1. **(RC1)** New TRD admitted against an already-*superseded* pinned STD →
   admitted; `declared` + alignment `pinned_declaration_superseded`; no
   retarget to the successor STD.
2. **(RC1)** Same with an already-*withdrawn* pinned STD → admitted;
   alignment `pinned_declaration_withdrawn`.
3. **(RC2)** Parity: every endpoint row's `state_declaration_conclusion`
   equals public `state_declaration()` output for the same anchor, context,
   and material, across all state conclusions × pin activities.
4. **(RC3)** Same-root two-parent merge resolves a fork to healthy; both
   parents become `superseded`; tips recompute.
5. **(RC3)** Parent tuple spanning two independent roots rejects with the
   typed lineage error (distinct from S04's wrong-key case).
6. **(RC4)** `model_record` evidence citing a `trw_`-shaped ID fails pattern
   validation; `trg_`/`trd_` citations validate; TRD admission validates its
   mandatory TRG citation through the store.
7. **(RC5)** On the untouched authoritative 34-record ledger:
   `transition()` → `not_registered`; `transitions_of_entity()` →
   `registered` with empty entries; `transition_assertion()` → `not_found`
   for each of `trg_`/`trd_`/`trw_`.
8. (Optional) Idempotent equal-record re-append and contradictory same-ID
   append rejection for the three new kinds.
9. (Optional) Context-equality admission proven on a `view_independent`
   instance, not only `lifecycle_view`.
10. (Optional) Forged alignment↔activity precedence swap (e.g., reporting
    `pinned_declaration_superseded` while the state conclusion is
    `conflicted`) rejects under §14 revalidation.
11. (Optional) Reversed registrations A→B and B→A coexist with distinct
    anchors and no tuple collision (positive companion to I04).

---

## 12. Concise correction checklist for Codex synthesis

No architecture-text contract changes are required. Amend only the acceptance
matrix (§19) and, optionally, one restatement:

1. **§19.3 add S15:** new TRD against an already-superseded pinned STD is
   admitted and discloses `pinned_declaration_superseded`; against an
   already-withdrawn pinned STD, `pinned_declaration_withdrawn`; no
   automatic retarget. (RC1)
2. **§19.4 add parity row:** endpoint `state_declaration_conclusion` equals
   public `state_declaration()` on identical `(anchor, context, material)`
   across all conclusion × pin-activity combinations; Slice B plan names the
   shared derivation functions it imports. (RC2)
3. **§19.3 add S16/S17:** same-root two-parent merge admitted and resolves
   to healthy; cross-root parent tuple rejects typed. (RC3)
4. **§19.2 add R10:** `trw_` model-record citation fails pattern validation;
   `trg_` and `trd_` citations admitted; existing 17 arms and golden vectors
   unchanged. (RC4)
5. **§19.4/§19.6 add authoritative-path rows:** the four queries executed
   against the untouched 34-record ledger return exactly `not_registered` /
   `registered`-with-empty-entries / per-prefix `not_found`. (RC5)
6. (Optional, NB5) Restate the uniform model-record evidence closure rule in
   §7.2's admission bullet list.
7. (Optional, NB6) Add the idempotent-append, `view_independent` context,
   precedence-swap-forgery, and reversed-pair coexistence rows.

---

## 13. Final recommendation and exact stopping boundary

**Recommendation:** record this audit as `approve_with_corrections`. The
owner may proceed to proposal-level acceptance **only after** the five
acceptance-matrix corrections in section 12 are incorporated (a bounded
edit to §19 plus at most one §7.2 restatement — no record contract, identity
policy, vocabulary, query surface, or lifecycle rule changes). All eight
lead recommendations (§5) are individually endorsed; Q4's endorsement stands
on the membership-relative relaxability of the tuple-uniqueness invariant
and on the honest separation of evidence roots, future mechanism
discriminators, and occurrence instances.

**Exact stopping boundary for everything that follows this audit:**

- This audit authorizes nothing: no code, test, fixture, identity, record,
  ledger, artifact, commit, push, merge, rebase, or history operation.
- No implementation begins before owner Gate 0 ratifies Q1–Q8 *and* the
  corrected §19 matrix.
- Slice A stops at identity, records, canonicalization, store admission,
  and lifecycle/replay tests — no public transition queries, no demo
  identity — and halts for owner acceptance.
- Slice B stops at the four read-only queries with revalidation — no
  classification composition, no assessment — and halts for owner
  acceptance.
- Slice C stops at hardening and reproduction with the authoritative ledger
  still at exactly 34 records at
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`,
  and halts for owner acceptance.
- Slice D does not exist unless the owner separately accepts a legitimate
  second state identity prerequisite and then authorizes candidate-anchor
  allocation under the full pre-append → append → acceptance gate sequence.
- Transition assessment, occurrence, triggers, guards, actions, effects,
  families, self-transitions, cross-entity endpoints, and parallel endpoint
  tuples each remain an independent future owner gate; none may be
  introduced by reinterpretation of any ST-002 record or ST-001 result.

END OF ST-002 CODEX LEAD PROPOSAL CHALLENGER AUDIT
