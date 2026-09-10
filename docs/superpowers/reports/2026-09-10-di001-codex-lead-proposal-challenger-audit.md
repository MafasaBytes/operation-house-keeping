# DI-001 Codex Lead Proposal — Independent Challenger Audit

One adversarial audit of the frozen DI-001 lead proposal — 2026-09-10.
Audit-only. This report modifies no existing file, implements nothing, and
allocates no ADR.

## 1. Frozen proposal verification

| Check | Expected | Observed |
| --- | --- | --- |
| Path | `docs/superpowers/proposals/2026-09-10-di001-codex-lead-proposal.md` | Present, read-only input |
| Lines | 739 | 739 |
| Bytes | 74,874 | 74,874 |
| SHA-256 | `447a345417dbd6ff4ff88685fffdfe20fc677a6f5517527e564165609e5cffe7` | Identical |
| Line endings | LF (house convention) | LF only; no CR present |
| Numbered sections | 13 | 13 (`## 1.` through `## 13.`) |
| Ending marker | `END OF DI-001 CODEX LEAD PROPOSAL` | Exact final line |

The frozen file matches the receipt exactly; no checkpoint discrepancy.

## 2. Independent baseline verification

All checks rerun by the challenger against the live tree:

- Branch `main`; `HEAD = origin/main = 181f5c8484ce31b7f4ef377e4af2399ed946dfa0`;
  latest commit subject `docs: close CS-001 as application policy`.
- `models/demo-printer/records`: exactly 36 record files; zero `fcd_`/`fcw_`
  (and zero `fma_`/`fmw_`). Accepted revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`
  unchanged (`models/README.md:72-73`, `models/demo-printer/README.md:204-205`).
- `backend/model_kernel/__init__.py` `__all__` parsed statically: exactly 236
  unique names; compact-JSON-list SHA-256 recomputed as
  exactly `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`.
- ADR-0001 through ADR-0022 contiguous and unique (22 files); ADR-0023 absent
  and unallocated.
- Document digests recomputed and identical to the proposal's table:
  reconciliation `95935321…`, CS owner decision `8557f225…`, CS correction
  report `b28c7750…`, CS challenger audit `ebbe4526…`, corrected CS proposal
  `ab816af9…`, FC final acceptance `1436b12a…`, FC final verification
  `eb67c083…`.
- All six protected tree inventories independently recomputed using the
  documented serialization (sorted repository-relative-path → file-SHA-256
  mapping, compact sorted-key JSON plus one newline). Every claimed digest
  and file count matched exactly: `models/demo-printer` 37 files
  `ea13596e…`; `bindings/demo-printer` 6 `11ccbed0…`;
  `bindings/demo-printer-model` 5 `1c861155…`; `interpretations/demo-printer`
  3 `819a2191…`; `showcases/demo-printer` 9 `dd7d8c98…`; `var/raw_store`
  (ignored) 5 `16ff9454…`.

No baseline discrepancy found.

## 3. Audit method

The audit traced the proposal's claims to live code, not prose: the public
reconstruction seam (`backend/model_kernel/port_results.py:77-112`,
`contracts.py:1868-1917`, `canonical.py:328-330`), the FC subject derivation
(`queries.py:1342-1478`), FM store integration and effective-body projection
(`store.py:2043-2290`, `canonical.py:85-99,238-256`), withdrawal rule families
(`store.py:1146-1172` strict versus `:1270-1295` REL-loose), RTD fork refusal
(`store.py:1210-1220`), PCM citation currency (`port_results.py:1176-1194`),
state-classification exact-current VCN enforcement
(`state_classification/derivation.py:30-77`), the 32-arm `ModelRecord` union
(`contracts.py:1868-1886`, counted: 32), cited `LoadedModel` index names
(`store.py:101-299`), and the disposable helper modules
(`tests/model_kernel/fc001_slice_a_helpers.py`,
`tests/model_kernel/test_flow_measurement_slice_a.py:80`).

## 4. Answerability and public-API sufficiency

The decisive seam is public and exactly as the proposal describes:

- `ModelRevision` is a public export; its validator enforces sorted unique
  IDs, count, and `revision_id == compute_revision_id(model_id, ids)` with
  `"\n".join([model_id, *sorted(ids)])` and no trailing newline
  (`contracts.py:1888-1917`, `canonical.py:328-330`). A caller can construct
  an exact proposed revision from explicit membership without private
  builders: `compute_revision_id` is confirmed not exported, and the
  algorithm is two public lines.
- `ModelQueryMaterial` is a public export; its validator enforces exact
  ordered membership, canonical record validity, and full closure through
  `validate_record_collection` (`port_results.py:83-112`);
  `validate_record_collection` is confirmed not a root export, matching the
  proposal's "implementation detail" classification; `LoadedModel` and
  `ModelQueries` are public exports.
- `ModelQueries(material.loaded()).flow_operating_criterion(...)` rederives
  the owning result for any exact membership without store access; the FC
  result's own `_authoritative` validator independently re-derives the
  subject from carried material
  (`flow_operating_criterion_results.py:133-153`).

The before/proposed comparison question is therefore genuinely answerable
with public APIs: validate both complete memberships, derive exact ID deltas,
requery owning selectors in both worlds, and compare exact result fields.

## 5. Field-level dependency edge verification

The proposal's section 5 taxonomy was sampled adversarially across the
families that carry the worked examples and the mandated audit cases. Every
sampled row matched live code:

| Proposal claim | Live verification |
| --- | --- |
| FMA = five subject fields + six pins; measured-actual VSM rule `project_local / ohk-observation-roles-1 / measured_actual` | `contracts.py:1709-1760`; store checks at `store.py:2071-2131` including exact role exclusivity and the VSM system/edition/code triple |
| FM effective body excludes evidence/authority/note/recorded_at | `_FLOW_MEASUREMENT_EFFECTIVE_BODY_FIELDS` is exactly the five subject fields plus six pins (`canonical.py:85-99`) |
| FC effective body wraps FM body plus exact CRG/VCN record IDs | `store.py:2278-2286` |
| FM support rows disclose activity/lineage health/alignment separately; inactive lineage forces `unaligned` | `flow_measurement_results.py:190-222` |
| FC reasons `vcn_not_current`, `fm_body_not_current`, `typed_support_not_current/inactive/conflicted/unaligned`, `fm_same_root_conflict`, `fm_cross_root_disagreement` | All present in the derivation and reason ordering (`queries.py:1397-1436`) |
| Same-body healthy independent root preserves applicability after witness withdrawal | `matching` computed over current same-body FM records independent of the retained witness (`queries.py:1404-1406`); `witness_record_indices` retains the exact old FMA |
| Strict withdrawal families reject superseded targets and duplicates; REL uniquely permits multiple withdrawals and coexistence with supersession | Strict rule at `store.py:1159-1168` (VPW shown; identical pattern at PTW/BHW/STW/TRW/FLW/FMW/FCW sites); REL path checks only target presence (`store.py:1275-1295`) |
| RTD fork is membership-invalid (`revision_invalid`), unlike VCN multi-tip query conflict | `MODEL_DUPLICATE_TYPE_NAME` at `store.py:1214-1219` |
| PCM S-compatibility requires each cited PIF to be the unique exact current edition | `port_results.py:1176-1187`: tip is `stale` unless `len(current) == 1 and current[0].record_id == citation_id` |
| STD remains kernel-declared after VCN correction; state classification enforces the exact current pin | `state_classification/derivation.py:30-77`: `declaration.declaration.record_id != pinned_id` yields `superseded`/`condition_declaration_superseded` without rewriting STD validity |
| Cited `LoadedModel` index names (FM subject/context/body maps, FC subject/successor/withdrawn/body maps, VSP/VSM/VCN tip maps, SRG condition map, TRG ordered-endpoint map, FL role map) | All present (`store.py:101-299` and construction sites) |
| All 32 `ModelRecord` union arms inspected | Count confirmed: 32 (`contracts.py:1868-1886`) |

The rejected edge bases (shared names, anchors, tokens, contexts, temporal
proximity) are genuinely excluded: the taxonomy's I/E/L/H/S/Q edges all
resolve to exact typed record fields, and section 5.1 explicitly denies edges
from display names, semantic tokens, and prose authority. The audit finds no
edge in the proposal that rests on name equality or proximity.

## 6. Kernel-semantics duplication analysis

The decisive question: does application composition force re-implementation
of accepted kernel semantics in an unverifiable way? Findings:

- **Not duplicated**: membership/closure validation (public
  `ModelQueryMaterial`), lifecycle/currentness/conflict computation
  (recomputed by `ModelQueries` on each world), effective-body semantics
  (kernel-computed indexes behind `.loaded()`), result revalidation (public
  outer validators), revision digests (public two-line algorithm).
- **Duplicated as documentation, not as semantics**: the edge taxonomy —
  which public field references which kind, with which consequence profile.
  This is a finite, reviewable map of public record content, not hidden
  validator logic. Its drift risk is process-bound: new record families can
  only arrive through new owner-gated milestones, which must update the
  taxonomy. Recorded as non-blocking observation NBO-3.
- **Duplicated as generic machinery**: traversal worklist, SCC detection,
  simple-path enumeration, deterministic ordering, and budgets are
  graph-generic code containing no kernel semantics.

Conclusion: the named consumer does not recreate a hidden second model
kernel. The correctness-sensitive lifecycle, effective-body, currentness,
closure, and result-revalidation semantics remain kernel-side and are
exercised through public seams. Outcome 1 survives this challenge.

## 7. Before/proposed comparison and append-only challenge

- Complete before and proposed memberships are both validated by the same
  public material contract; no mutation of immutable bytes is possible
  (content-derived IDs; changed content under an old ID fails
  `verify_record_id` inside collection validation).
- Correction successors, withdrawals, replacement identities, and historical
  replay follow the verified per-family rules (section 5); the append mode's
  subset requirement and the historical mode's explicit reference-closed
  selection are honest formulations of the existing architecture.
- The eight mandated distinctions map to the proposal's vocabulary with live
  backing: invalid proposed revision (`revision_invalid` via material
  admission failure), stale retained support (`declaration_stale`, e.g.
  `vcn_not_current`), inapplicable declaration (`declaration_inapplicable`
  with FC's actual reasons), lineage conflict (`lineage_conflicted`
  preserving same-root conflict versus cross-root disagreement — both exist
  in live literals), changed decision selection (selector recomputation over
  complete proposed membership), reevaluation (Q-path rule), unaffected
  (scoped only), unknown (inventory/foreign gaps). No distinction requires
  semantic rules absent from public contracts; the application supplies only
  scope and inventory, not semantics.
- Combined multi-change non-additivity (case 14) is real and verified
  against the derivation: two individually harmless withdrawals of equal-body
  corroborating roots jointly empty `matching` and trigger `fm_inactive`/
  `fm_body_not_current` (`queries.py:1404-1411`, `:1469-1472`). A union of
  singleton impacts is genuinely unsound; the proposal refuses it.

## 8. Completeness boundary challenge

The strongest honest claim in the proposal is: all decisions supplied in an
explicit bounded inventory, over the admitted typed relation scope. The
wording was attacked for global-completeness leakage:

- `unaffected` is explicitly scoped ("Never global, never physical") and
  requires both no path in the admitted relation and no owning-query evidence
  of effect.
- Unlisted decisions are `unknown`, never `unaffected`; the manifest key-set
  comparison (section 7, T21) prevents silent omission including
  no-longer-evaluable decisions.
- Foreign (X) material terminates at a labelled frontier; unsupported scopes
  cannot return `unaffected`.
- The EA boundary is correct: EA selection requests carry no model revision
  (verified in the EA contracts), so a model-only change cannot stale source
  evidence, while model-bearing results (CN/VS/FC/alignment) carry exact
  revisions that force recomputation under a proposed membership — the
  proposal's Q-membership disclosure is accurate and necessary.

A typed decision-inventory contract is not required for one named consumer;
the explicit application-owned inventory plus manifest key comparison is
sufficient. If a second consumer or cross-application completeness claims
appear, that would be a new demonstrated need. No wording implying global
completeness was found.

## 9. Transitive traversal challenge

The proposal's traversal discipline survives the mandated attacks:

- Admitted edge kinds restricted to typed I/E/L/H/S/Q; X terminates at the
  frontier; direction is prerequisite→dependent reverse review with preserved
  field-path labels (including TRD from/to roles and distinct FCD→FMA→FLD→PIF
  paths) — verified these are distinct live field paths.
- Cycles: correction DAG cycles refuse at membership validation; derived
  relation cycles are handled by visited-worklist/SCC diagnosis, and cyclic
  reachability is never presented as infinite impact. This is the correct
  treatment; the audit specifically notes the proposal does not assume
  acyclicity of the combined derived graph.
- All simple labelled paths within budget are disclosed (no silent
  shortest-path substitution); exact dedup keys; deterministic ordering rules
  exclude hash-seed nondeterminism.
- Limits are measured, not borrowed: the profile (64 records, 16 changes,
  16 decisions, 256 nodes, 512 edges, 512 paths, depth 64, 8,192 path-edge
  references) is justified by the disposable measurements (15–18 records,
  40–57 reference occurrences, ~12.6–15.7 KiB material) and the 36-record
  authoritative model, explicitly disclaimed as TA's limits or production
  sizing, with whole-review refusal (`analysis_limit_exceeded`) instead of
  truncation. Aggregate accounting across seeds is specified. This satisfies
  the mandate's "measured justification or application-owned limits."
- A reusable traversal utility is not justified today: the
  correctness-sensitive semantics stay kernel-side (section 6); what remains
  is generic graph code plus a documented field map for one consumer. If a
  second consumer or demonstrated divergence appears, the proposal's own
  reopening rule applies.

## 10. Adversarial cases and threat matrix verification

The twenty mandated cases were each traced:

1. VCN correction → verified live path (`vcn_not_current`, `queries.py:1432-1436`); renewal twin valid.
2. FMA body correction → `fm_body_not_current` via empty `matching`; typed support staleness via superseded VPA pin; renewal twin valid.
3. Healthy same-body root preserves applicability → `matching` independence from witness verified; negative control (no corroborating root) fires `fm_body_not_current`; the "E does not rescue W+E+P2+A2" warning is correct because differing current bodies across active roots trigger `flow_measurement_disagreeing_root_ids_by_subject` → `fm_cross_root_disagreement` (`store.py:2235-2247`, `queries.py:1410`).
4. FLD correction/withdrawal → `typed_support_not_current`/`typed_support_inactive` verified in the support-row loop; no physical-flow claim.
5. VPA correction → same support-row mechanism; no port-observation inference.
6. Identical-body VSM correction → FM semantic alignment can stay exact while FC requires exact-pin renewal; consistent with the separate alignment/activity disclosures.
7. Same-root conflict versus independent roots → `fm_same_root_conflict` from lineage health; equal-body independent roots remain applicable; verified.
8. Historical replay reviving an ancestor → reference-closed subset selection through the same public material contract; no ledger deletion; verified as a property of `ModelRevision`/`ModelQueryMaterial`.
9. Identity replacement → duplicate same-anchor registration refused; no dependent migration; verified against registration permanence rules.
10. Evidence-only correction with unchanged body → body projection excludes evidence (`canonical.py:85-99`); applicability preserved; provenance change disclosed.
11. Unrelated change → no typed path; Q revision-binding effect separately disclosed; correct and subtle — verified that model-bearing results carry exact revisions.
12. Decision reevaluation without verdict reversal → Q rule; old result remains historical.
13. Structurally invalid proposed membership → closure failure at material validation; `revision_invalid`, not partial impact; verified closure enforcement.
14. Multi-change non-additivity → verified live (section 7 above).
15. Omitted decision falsely labelled unaffected → manifest key-set comparison (T21); correct.
16. Provenance-only path as semantic impact → E versus H/S separation (T03); correct.
17. Cross-context leakage → exact family/key/context selectors (T05); correct.
18. Mixed before/proposed revisions → role-bound commitments (T06); correct.
19. Cyclic/explosive path material → SCC plus aggregate refusal (T14/T16); correct.
20. Forged consequence/path/index/ordering → rederivation and canonical-order checks (T15/T17); correct.

Every attack in the section 11 matrix (T01–T26) has a valid twin, and the
twins are constructible through public builders. The section 9.1 example uses
only public exports plus existing test helpers whose signatures the audit
verified line-by-line (`world()`, `declaration(witness, crg, vcn, **overrides)`,
`replace(record, **updates)`, `withdrawal(target, *, note="")`); its
assertions were traced through the live FC derivation and are consistent
(applicable → `vcn_not_current` inapplicable → renewed applicable;
single-withdrawal applicable twice; double-withdrawal inapplicable).

## 11. Alternatives and "no milestone" adjudication

| Alternative | Concrete integrity property it would add | Audit position |
| --- | --- | --- |
| 1. Existing APIs + application composition | None missing; all correctness-sensitive semantics kernel-side | **Confirmed sufficient** |
| 2. Typed application-owned comparison protocol | Schema discipline only; the proposal's labels/modes already fix semantics | Not required; may be adopted by the consumer without any milestone |
| 3. Reusable pure traversal utility | Deduplicates generic graph code, not kernel semantics | Not justified for one consumer; reopen on demonstrated second consumer or divergence |
| 4. Additive kernel reverse indexes/queries | Packaging of public field scans; no new fact | Rejected correctly — convenience only |
| 5. Sibling read-only impact component | A new aggregate boundary without a demonstrated missing property | Rejected correctly |
| 6. Durable dependency records | Duplicates canonical edges into a second authority — correction-divergence risk | Rejected correctly and concretely |
| 7. Prerequisite repair | None identified; every required field and consequence path is public | Not needed |

The no-milestone recommendation survives because the reverse question —
"what would force the application to duplicate accepted lifecycle,
effective-body, currentness, closure, or result-revalidation semantics
unverifiably?" — has no instance. Each of those semantics is exercised
through a public, self-revalidating seam.

## 12. Original-objective audit

| Objective | Proposal claim | Audit verdict |
| --- | --- | --- |
| 1. What exists / connected | Reviewable explicit declared dependency paths from existing facts | Confirmed; scoped, no new connectivity capability |
| 2. Current state | Model support currentness/applicability and decision reuse under exact memberships | Confirmed partial; no physical state claim |
| 3. Why behaving | Explains dependency-based refusal/staleness, not physical cause | Confirmed foundational only |
| 4. Next best measurement | May reveal decisions needing reevaluation; no selection | Confirmed unchanged; no inflation |
| 5. Change impact | Exact declaration/support/selection and named decision dependencies reviewable before acceptance | Confirmed partial and bounded. The mandated separations hold: explicit declaration dependency ≠ decision reevaluation ≠ configuration validity ≠ physical propagation ≠ behavioral consequence ≠ causal impact ≠ safety/risk ≠ cost/schedule; the proposal states each exclusion explicitly |
| 6. Smallest change set | Rejects structurally invalid supplied sets; does not generate or minimize | Confirmed absent for planning |
| 7. Epistemic separation | Separates canonical facts, calculated differences, application completeness assertions, unknown foreign scope | Confirmed partial |

DI-001 adds no new backend capability; it makes an existing composition
precise and reviewable. The proposal says this itself ("there is no newly
answerable backend question: the design makes an existing composition
precise"). No inflated contribution found for objectives 1, 2, 5, or 7.

## 13. Findings register and verdict

- **Blocking findings: 0.**
- **Required corrections: 0.** No concrete missing public field, semantic
  duplication, counterexample, invalid completeness claim, unreachable state,
  or violated accepted boundary was identified. Every load-bearing claim
  sampled against live code matched exactly (sections 4–10).
- **Non-blocking observations: 4.**
  - NBO-1: the section 9 in-memory experiments were executed in the
    proposal's authoring environment; this audit environment (Windows host,
    Linux-only project venv) cannot re-execute them. The decisive semantics
    were instead verified by reading the live FC/FM derivation, and the
    helper signatures and example logic were traced line-by-line. The owner
    can reproduce under the documented Linux environment.
  - NBO-2: the capacity counts (15/40/12,604; 17/46/14,528; 18/57/15,713;
    18/51/14,945; 14,692-byte FC result) are not independently reproducible
    here and are not load-bearing; they are honestly presented as
    observations, not identities. Note the 14,692-byte figure differs from
    the FC verification report's 14,677-byte witness because they measure
    different disposable worlds (15-record helper world versus the 19-record
    A/B proof world); no contradiction.
  - NBO-3: the section 5 edge taxonomy is a maintained document; future
    record families arrive only through new owner-gated milestones, which
    must extend the taxonomy. This drift control is process-bound and
    adequate.
  - NBO-4: the design-review profile limits remain owner-gated exploratory
    choices, explicitly not production limits — as disclosed; an owner needing
    larger scale must measure the actual consumer payload first.

**Verdict: `approve`.**

## 14. Owner-decision adjudication and DI-001 disposition

1. **Exact review scope**: endorse as written — bounded before/proposed
   complete-membership pair with explicit intent and independent commitments.
2. **Decision-inventory authority and completeness**: endorse as written —
   application-owned inventory, manifest key-set comparison, `unknown` never
   `unaffected` for unlisted decisions.
3. **Current-membership versus before/proposed comparison**: endorse as
   written — append-candidate and historical-comparison modes with their
   respective guards match the append-only architecture.
4. **Foreign-material scope**: endorse as written — X frontier with `unknown`
   unless independently supplied supported foreign context exists.
5. **Direct versus transitive traversal**: endorse as written — typed
   labelled edges only, all simple paths within budget, SCC cycle handling,
   refusal never truncation.
6. **Measured capacity and refusal behavior**: endorse as written — small
   measured exploratory profile; owner measurement gate for scale.
7. **Reusable typed composition**: endorse the rejection for now — no missing
   integrity property; correctness-sensitive semantics remain kernel-side.
   Revisit only with a demonstrated second consumer or concrete divergence.
8. **Final DI-001 disposition**: **cancelled because existing APIs suffice**,
   equivalently reclassified as application composition; the proposal stands
   as the retained documentation guidance for the named change-review
   consumer. Not deferred — no prerequisite is missing. No milestone, package,
   index, record, or ADR is authorized.

## 15. Verification, preservation and audit-only scope

This audit independently reran the frozen-receipt checks, all baseline
checks, the six protected tree inventories, four document digests, the export
digest, and the field-level source inspection recorded above. It created
exactly one file — this report — and modified none. No code, test, fixture,
record, branch, commit, push, merge, or history operation was performed.
ADR-0023 remains absent and unallocated. The only other working-tree entries
observed are the pre-existing untracked `.claude/settings.local.json` and the
frozen proposal's companion CS files already tracked at HEAD; nothing was
touched. Post-write size, digest, and marker confirmation are reported in the
terminal receipt; this file does not embed its own hash.

END OF DI-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
