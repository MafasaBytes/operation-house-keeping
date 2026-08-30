# ST-001 Final Synthesis — Independent Challenger Audit

Auditor role: independent architectural challenger (adversarial audit only)

Audit target:
`docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-and-evidence-gated-classification-design.md`

Date: 2026-08-30

Repository baseline verified before audit: `HEAD` = `main` = `origin/main` =
`0ed77df7ea4870faec1eae9b89668add97aa855d`, working tree clean except the
untracked ST-001 proposal/synthesis documents themselves.

Boundary: this audit modifies nothing. It creates no code, test, fixture,
ledger, artifact, or documentation change other than this file, and performs
no commit, push, merge, rebase, reset, or history operation. It is not a
redesign of ST-001 and does not reopen owner-settled decisions, including the
synthesis's explicit rejection of challenger elements (synthesis §2.4).

## 1. Audit scope, method, and severity definitions

This is a bounded adversarial audit of the corrected final ST-001 synthesis
against the repository's accepted invariants and the sixteen owner-named
concentration areas. A defect requires: an identifiable violated accepted
invariant, an exact synthesis location, and a minimal counterexample world.
Stylistic preferences are excluded by construction.

Severity definitions used here:

- **blocking** — the design must not be owner-approved, or Slice A must not
  start, until repaired; an accepted invariant is violated as written.
- **major** — a normative rule is incomplete or incorrect such that two honest
  implementers can produce divergent verdicts from the same membership; must
  be repaired before the affected slice's implementation gate.
- **minor** — a clarity, reference, or wording correction with no plausible
  verdict divergence.

Method: two complete passes over all 2307 lines of the target; every
load-bearing claim about accepted behavior was cross-checked against committed
code and committed accepted documentation (Section 3). The parallel Codex
proposal was not read; nothing here evaluates it.

## 2. Audit target identity

- Path: as above.
- Extent: 2307 lines, 97273 bytes.
- SHA-256: `b1a144c6aae2a7e4e9eb499e4bfdd6cad5e757241fa062efe31af505fd96eeb3`.
- Ending marker confirmed at line 2307: `END OF ST-001 CORRECTED FINAL
  SYNTHESIS`.
- Git state: the target is untracked, as expected for an uncommitted,
  owner-gated design artifact; no tracked fixture, ledger, membership, or
  artifact differs from `0ed77df`.

## 3. Verified ground truth used by this audit

Each synthesis claim listed below was checked against a committed source:

1. The nine explicit historical memberships and revision strings (synthesis
   §1.3, lines 75–85) match `backend/model_kernel/contracts.py:38–48`
   verbatim: 9/10/11/14/16/18/28/29/32 records with the exact `mrv_` strings.
   The same strings appear independently in committed reports, plans, and
   ADR-0012.
2. CN-001 declaration lifecycle (governing synthesis §8.2 and §12.3):
   - VCN lineage key is the constraint anchor id alone
     (`docs/superpowers/specs/2026-08-15-cn001-…-design.md` §5.2, lines
     193–196); VCN records carry no `AssertionContext` field.
   - There is no VCN withdrawal record kind (CN spec §5, lines 149–222);
     synthesis line 1370 ("CN has no inactive-declaration outcome") is
     verified factually correct against the accepted lower contract.
   - Competing current tips on one `con_` are "surfaced, never resolved by
     recency, authority, record id, file order, or append order" (CN spec §8,
     lines 296–298); acyclicity is an "iterative three-colour walk" (CN spec
     §8, line 291).
   - `ConstraintDeclarationResult`
     (`backend/model_kernel/contracts.py:1224–1246`): `declaration` is the
     authoritative declaration and follows the repository's "carried exactly
     when" status pattern; `conflicting_declarations` carries competing tips
     verbatim; `declared` corresponds to one current tip and `conflicted` to
     two or more.
   - The CN spec contains no `corroborat`/`effective body`/`independent root`
     vocabulary (grep-negative): CN-001 declares no corroboration concept at
     VCN lineage level.
3. CN facade public exposure (`backend/constraint_evaluation/facade.py`):
   `self.semantic` is public (line 99); the facade builds its own
   `ModelQueries` over the publicly reachable loaded model
   (`semantic.compatibility.state.model`, line 103); it consults CN's
   declaration result at line 120. An ST facade injected with
   `ConstraintEvaluationQueries` can therefore lawfully reach the same loaded
   model and construct kernel queries over it — the exact pattern CN itself
   uses — without touching any private field. Synthesis §11.1's
   single-injection constructor is feasible and consistent with §15.2/§15.3.
4. Kernel DAG traversal is explicitly iterative (explicit-stack three-colour
   walks at `backend/model_kernel/store.py:226–239` and `430–447`).
5. The phrase "repository-approved depth bound" occurs nowhere in the
   repository except synthesis line 1649 (full-repo grep). The BH-001
   specification does not contain the phrase; the accepted precedent pins the
   algorithm (iterative; item 4 above), not a delegated bound value.
6. Demonstration constants (synthesis §1.4 lines 93–108 and §19.1–19.2):
   subject entity `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`, constraint
   `con_4b768cf843f5474cb5e564e31d239a59`, and pin
   `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`
   match the accepted pins recorded in CLAUDE.md; `60.4` satisfies the
   inclusive upper bound `80` per the committed CN spec (lines 106, 480); the
   cutoff `2026-08-07T20:30:00+00:00` is the committed demonstration cutoff
   (VP-001 Slice D plan line 142; BH-001 Slice D reports at
   `…/2026-08-30-bh001-slice-d-preappend-rehearsal-results.md:528` and
   `…/2026-08-30-bh001-slice-d-completion-report.md:302`).
7. Accepted artifact hashes (synthesis §1.4, lines 114–119): the PT/VP/BH
   SHA-256 values match CLAUDE.md; the CN artifact SHA-256
   `161a7beb…07a5d9` is pinned in committed test code
   (`tests/constraint_evaluation/test_demo_cn001.py`).
8. Source-integrity note: synthesis §1.1 (lines 25–39) transparently records
   that the on-disk challenger proposal's SHA-256 (`b701dab5…a5707b`) differs
   from the challenger's earlier delivery receipt (`3ff7c955…611f47`) and
   designates the on-disk file as the reviewed source. This audit relies only
   on committed repository truth plus the synthesis text; the disclosed
   mismatch affects no finding here, and the synthesis's handling of it is
   honest and correct.

## 4. Area-by-area findings

### 4.1 Entity-level state identity distinct from variable constraints — no defect

State identity is a first-class entity-scoped concept, never a variable
attribute (§3.2 lines 254–279; §4.1 lines 304–311; §7.1 lines 561–578;
§8.5 lines 662–672). The SRG binds one opaque anchor to one registered entity
and a permanent constraint set; constraints stay CN-owned variable knowledge.
No result or record lets a variable's region silently become an entity state,
and the CN-output-only collapse is explicitly rejected (§4.2 lines 313–320;
acceptance row Q14 line 1808, P11 line 1868). The distinction survives
classification because ST maps only CN's carried outcome into condition rows
after pin alignment (§8.3 lines 648–649).

### 4.2 Same-owner condition restriction — no defect

The restriction is fully specified and enforceable: every permanent
constraint's target variable's embedded `VariableAnchor.entity_anchor_id`
must equal the SRG subject by direct identity equality (§7.1 lines 567–569),
with an explicit prohibition on inferring scope from hierarchy, names,
topology, ports, VPA, behavior, observations, or shared ownership (§7.1
lines 571–575). Store admission enforces it (§9.1 lines 683–685; §9.3 line
722; rows O04–O05 lines 1758–1759) and authoritative reconstruction
recomputes it from carried material (§14.1 item 4, lines 1470–1471). The
committed 32-record model admits the demonstration subject.

### 4.3 Permanent identity boundary against state-meaning drift — no defect

The anchor is opaque and meaning-free (§5.1 lines 380–385); registration is
permanent, and a second SRG for one anchor, agreeing or divergent, is invalid
(§6.2 lines 466–469; §9.1 line 682; §9.3 line 723; row R08 line 1737).
Changing the subject, any condition anchor, or the family requires a new
anchor and SRG (§5.3 lines 415–419); VCN re-pinning within one permanent set
is a lineage-relative declaration correction (§5.3 lines 421–423). Identity,
naming, and condition meaning cannot drift silently.

### 4.4 Exact VCN pinning across correction, conflict, replay, corroborating roots — MAJOR DEFECT D1

The correction/conflict/replay treatment is exact: pins are content identities
(§6.3 lines 473–481); later CN correction aligns `superseded` and contributes
nothing (§8.2 lines 624–633; §12.3 line 1366; §16.3 lines 1607–1611);
automatic adoption is correctly absent (§2.4 line 215; §8.2 lines 620–622);
membership-relative replay revives old pins honestly (§16.3; row L20 line
1789). The claim that CN has no inactive outcome (line 1370) is verified true
against the accepted CN contract (Section 3, item 2).

However, the corroborating-root requirement is not completely specified on the
CN side of alignment. The synthesis normatively adopts effective-body-group
corroboration for STD lineages (§2.2 correction 5, lines 182–184; §9.5 lines
791–802) but never states the rule for a *constraint* lineage with competing
tips whose engineering content is identical. Section 12.3's only multi-tip
guidance — "even if one tip equals pin" (line 1365) — sits on the `conflicted`
row without defining what makes a CN declaration conflicted. Against the
accepted CN contract, the answer is pinned and strict (Section 3, item 2):
competing tips are conflict regardless of content equality, `declared` exists
only for one current tip, and CN has no corroboration concept. But the
synthesis text does not say so, and the normative table therefore admits a
misreading with verdict-level consequences. Full defect record: D1, Section
5.1.

### 4.5 Effective-body-group admission rather than exactly-one-declaration assumption — no defect

On the STD side the requirement is completely specified: correction 5 (lines
182–184), the exclusion of identity-bearing fields from the body projection
(§9.5 lines 766–786), the aggregate conclusion table (§9.6 lines 818–825),
result disclosure of every current tip (§10.5 lines 1037–1039), classification
admission of the unique admitted active group (§11.3 step 9, lines 1187–1195),
reconstruction of exactly one admitted group (§14.2 lines 1492–1493), and
acceptance rows L09–L11 (lines 1778–1780) and T02–T03 (lines 1839–1840). The
remaining asymmetry — different lifecycle shapes for STD (corroboration) and
VCN (strict conflict) lineages — is the subject of D1/Q1, not a defect here.

### 4.6 Composition of public ConstraintEvaluationQueries without CN duplication — no defect

The facade injects and calls the public CN facade exactly once per condition
(§8.3 lines 637–638; §11.1 lines 1140–1142; §11.3 step 5, lines 1178–1180);
parser, gate, decimal, predicate, and refusal logic are explicitly excluded
from ST (§8.3 lines 639–646; §15.2 lines 1552–1554; §17.4 lines 1663–1672;
row C14 line 1831). Pin alignment is pure identity comparison against the
kernel's declaration result — the same public seam CN uses internally
(facade.py:120) — so admission can never be silently duplicated. Verified
against the committed CN facade (Section 3, item 3).

### 4.7 Condition-source validation and entity-retarget impossibility — no defect

`StateConditionSource` carries only a constraint id and an explicit
`SourceSelector` (§11.2 lines 1146–1150); there is deliberately no entity
override (§2.2 correction 3, lines 177–179; §11.2 lines 1152–1154), and the
SRG's permanent subject is forwarded to every CN branch (§11.3 step 5; row C09
line 1826). Source-set equality with the permanent condition set is exact
(§11.2 lines 1156–1163; rows C04–C07 lines 1821–1824). A caller cannot
retarget, substitute, or reorder-forge a condition's evidence path.

### 4.8 All-of truth table mathematical and evidential honesty — no defect

The table (§12.4 lines 1385–1392) is exact three-valued conjunction: a false
conjunct determines the conjunction even with unknown siblings, yielding
`incomplete/executed/does_not_match` (row T10 line 1847), while unknowns
without violation block execution and yield `None` (row T11 line 1848).
`matches` and `does_not_match` non-claims are stated (§3.2 lines 275–279;
§12.4 lines 1394–1397): no other state is selected, no unobserved condition is
negated. Coverage, execution, and match are independently disclosed, so a
violated-plus-unknown world is neither promoted to a full evaluation nor
hidden. Lifecycle-gated states still carry per-branch CN evidence (§12.4
lines 1374–1383 with rows C11 line 1828 and T12 line 1849), consistent with
the accepted always-run composition precedent.

### 4.9 Independent latest-at-or-before evidence versus simultaneity claims — no defect

The basis literal is fixed on the record (§6.4 line 494; row R13 line 1742);
each branch independently selects latest evidence at or before one shared
UTC-normalized cutoff (§13.2 lines 1426–1434); every cohort, simultaneity,
synchronization, skew, interpolation, persistence, and causal-ordering claim
is explicitly excluded (§13.2 lines 1436–1445; rows P01–P05 lines 1858–1862).
`temporal_alignment` is always `not_asserted` for registered states and
`not_evaluated` only when no branch exists (§13.2 lines 1432–1434; §12.1
lines 1310–1313).

### 4.10 Staleness disclosure without arbitrary policy — no defect

ST carries exact lower-layer staleness, timing, candidate status, and
provenance unchanged, adds no threshold, class, max age, or veto, and never
lets staleness rewrite verdicts (§13.3 lines 1447–1459; rows P06–P07 lines
1863–1864). The challenger's `fresh/aging/stale` classes are an explicitly
adjudicated rejection (§2.4 line 219) and are not re-opened here.

### 4.11 Lifecycle, classification, physical state, safety, health, transitions separation — no defect

Mandatory non-claims (§3.3 lines 281–300), classification vocabulary
exclusions (§12.1 lines 1326–1328), exclusions (§21.1–21.2 lines 2140–2178),
acceptance rows P11–P12 (lines 1868–1869), and the mandatory demonstration
disclaimer (§19.5 lines 2002–2010) keep these axes separate. Multiple
simultaneous matches are disclosed as independent results, never ranked or
merged (§12.5 lines 1399–1405; rows T13–T14 lines 1850–1851).

### 4.12 Authoritative reconstruction from carried material without store access — no defect

Kernel results rebuild the model in memory, revalidate every content-derived
id and revision membership, and recompute every derived field — subjects,
condition closure, owner equality, roots, tips, withdrawals, body groups,
conclusions, indices, ordering (§14.1 lines 1463–1481). Classification results
rederive the complete carried `StateDeclarationResult`, every CN result
through CN's own public validation contract, request echoes, the admitted
group, pins, alignments, coverage, refusals, execution, and match (§14.2
lines 1485–1505), with no store or filesystem (§14.1 line 1469; §14.2 line
1505; row H08 line 1882). The public loaded-model derivation path for the
facade is legal and available (Section 3, item 3); naming it explicitly is
optional improvement O1.

### 4.13 Independent identical roots corroborate without merging identity — no defect

Independent-root corroboration never merges identity or creates a canonical
region (§7.2 lines 586–589; §9.5 lines 797–798); evidence and authorities stay
independently disclosed (§9.5 line 798); body comparison excludes identity,
provenance, parents, and record ids (§9.5 lines 775–786; row L12 line 1781).
The synthesis also credits the corroboration-never-merges clarification
(§2.3 line 200).

### 4.14 Record counts, historical memberships, replay closure, planned 32→34 demonstration — no defect

The §1.3 membership table matches the committed kernel constants verbatim
(Section 3, item 1). Pre-ST memberships return structured absence with no
migration artifact (§16.1 lines 1575–1587; rows D01–D02 lines 1890–1891).
Replay never derives membership from enumeration, prefix, timestamp, or append
order (§16.3 lines 1613–1615; row D03 line 1892). The demonstration appends
exactly one SRG and one parentless STD, 32→34, anchored to verified accepted
fixtures (§19.1 lines 1905–1938; rows D08–D09 lines 1897–1898; Section 3,
items 6–7), under a mandatory pre-append owner gate that defers all exact
identities to rehearsal (§19.3 lines 1968–1988).

### 4.15 No ST-002 leakage — no defect

Transition identity, from/to direction, triggers, events, guards, actions,
dwell, hysteresis, persistence, next-state selection, execution, history,
recommendation, and control are wholly deferred (§4.6 lines 346–351; §21.1
lines 2142–2158); no placeholder field, reserved discriminator, hidden graph,
or runtime hook exists (§21.1 lines 2156–2158); record contracts contain no
transition arm (rows R04 line 1733, I09 line 1724); result vocabulary contains
no transition status (§12.1 lines 1326–1328; row P12 line 1869). A value
change is explicitly not a transition (§21.1 line 2158).

### 4.16 DoS bounds, strict indices, nested-instance forgery, deterministic ordering — MINOR DEFECT D2

Condition sets are hard-capped at 64 (§6.2 lines 461–464; row R07 line 1736;
§17.6 lines 1687–1696); traversal cost is bounded by the selected membership
(§17.2 lines 1648–1649); indices are strict non-boolean with boolean-rejection
everywhere (§10.3 lines 976–977; row H04 line 1878); nested-instance forgeries
are fully revalidated (§5.1 line 378; row R18 line 1747; row H07 line 1881);
ordering is deterministic under reversed input, hash seeds, and enumeration
order (§9.7 line 856; §17.6 lines 1691–1692; row D04 line 1894).

One defect: §17.2, line 1649, conditions recursion on "a repository-approved
depth bound" that exists nowhere in the repository (Section 3, item 5), and
the accepted precedent pins the algorithm instead of delegating a bound. Full
record: D2, Section 5.2.

## 5. Confirmed defects

### 5.1 D1 — CN-side corroborated-lineage pin alignment unspecified (major)

- **Severity: major.** Not blocking; must be repaired before the Slice C
  implementation gate.
- **Exact location:** synthesis §12.3 (the normative table at lines
  1357–1367, specifically the `conflicted` row wording at line 1365 and the
  `exact_current` row at line 1367), with the same gap in the §8.2 pin-state
  bullets (lines 624–633); the classification scheduling step 9 (§11.3, lines
  1187–1188) inherits the table's rule.
- **Violated accepted invariant:** the owner's audit area 4 requirement that
  exact VCN pinning handle corroborating roots; substantively, the CN-001
  invariant that competing current tips are surfaced as conflict and never
  resolved, ranked, or merged (CN spec §8, lines 296–298;
  `backend/model_kernel/contracts.py:1224–1246`), and the architecture-wide
  determinism/honesty requirement that the same membership and evidence can
  never yield divergent verdicts.
- **Minimal counterexample world W (constructible under accepted CN-001
  semantics):** entity `e` registered; variable `v` embedded-owned by `e`;
  CRG `con_X → v`. Two parentless VCN declarations `vcn_A` and `vcn_B` share
  `con_X` and carry byte-identical predicate and expected-semantics content
  but different evidence and authorities; neither supersedes anything. The
  committed kernel contract reports this lineage `conflicted` with
  `conflicting_declarations = (vcn_A, vcn_B)` (Section 3, item 2). Now SRG `S`
  registers subject `e` with condition set `{con_X}`, and STD `D` (single
  healthy root, context `C`) pins `con_X → vcn_A`. Classify with a witness
  source whose observation satisfies the shared predicate. The synthesis's
  text under-determines the outcome: an implementer who reads the §12.3
  `conflicted` row as requiring *differing* tip content will body-merge the
  identical tips, align `exact_current`, execute, and return `matches`; the
  accepted-CN-consistent implementation aligns `conflicted`, contributes no
  condition outcome, and returns `incomplete/not_executed/None` with refusal
  `condition_declaration_conflicted` (§12.2 line 1340). Two honest
  implementations diverge on coverage, execution, and computed match for one
  membership and one evidence set — and the misreading manufactures
  corroboration that the accepted CN lifecycle deliberately does not support.
- **Smallest correction (no contract or code change):** (i) add one
  definitional sentence to §12.3 after line 1367: a `conflicted` CN
  declaration means two or more competing current tips **regardless of
  content equality**; CN-001 admits no corroborating-tip or effective-body
  concept at VCN lineage level, so identical twin tips are conflict, not
  corroboration; (ii) add one §18.7 acceptance row pinning world W end-to-end
  (alignment `conflicted`, no condition contribution, execution
  `not_executed`, `computed_match` `None`, refusal
  `condition_declaration_conflicted`); (iii) optionally point §12.3 at the
  accepted `ConstraintDeclarationResult` declared-iff-unique-tip rule so the
  comparison operand is unambiguous.
- **Blocks Slice A: no.** Slice A adds anchors, records, canonicals, store
  validation, and indexes only; pin alignment exists from Slice C onward and
  the accepted CN kernel semantics are untouched.

### 5.2 D2 — "Repository-approved depth bound" reference dangles (minor)

- **Severity: minor.**
- **Exact location:** synthesis §17.2, line 1649 ("must not recurse without a
  repository-approved depth bound").
- **Violated accepted invariant:** audit area 16's requirement that DoS/DoS-adjacent
  bounds be sufficiently and deterministically specified; a named control
  artifact must exist or the control must be stated directly.
- **Minimal counterexample world:** the phrase occurs nowhere else in the
  repository (full-repo grep; Section 3, item 5), while the accepted CN/kernel
  precedent pins the algorithm — "iterative three-colour walk" (CN spec §8,
  line 291) implemented with explicit stacks (`store.py:226–239`, `430–447`).
  An implementer reading line 1649 as license for recursion with a self-chosen
  bound produces a validator that can exhaust the interpreter stack on a deep
  hostile parent chain (limited only by generic record caps) where the
  accepted iterative walk succeeds; an implementer reading it as a blocking
  dependency stalls on a nonexistent artifact. Divergent behavior under
  identical input, or unbounded review ambiguity.
- **Smallest correction:** replace the clause with the precedent — e.g.
  "traversal is iterative, matching the accepted kernel three-colour walk;
  recursion is not permitted" — optionally adding one §18.4/D-series
  acceptance row pinning iterative-only STD/STW DAG validation.
- **Blocks Slice A: no.** The existing iterative walks already dominate any
  implementation derived from the codebase; repairing one sentence before
  Slice A's store-validation work is recommended for cleanliness, not required
  for correctness.

## 6. Questions (non-blocking; owner adjudication requested)

- **Q1 (attached to D1).** Under the synthesis as repaired per D1, CN-side
  identical-body twin tips intentionally render a state unclassifiable
  (`conflicted`) until a converging correction append, while STD-side
  identical-body independent roots corroborate (§9.5). Is this strict
  asymmetry — inherited from the accepted CN-001 lifecycle — the intended
  permanent interplay for ST-001 v1? If not, the remedy is an owner-gated
  CN-001 repair slice (effective-body-group corroboration at the VCN lineage
  level, mirroring the later PT/BH machinery) preceding ST Slice C; that is a
  CN-scope change and must not be smuggled into ST-001. This audit does not
  reopen CN-001's accepted semantics; it asks that the consequence be
  acknowledged as intentional.
- **Q2.** §20.3 assigns the authenticity-limitation demonstration to Slice C
  (lines 2083–2084, 2097). Should it re-run the committed BH-001
  coherent-mutation limitation pattern against the ST composition, or should
  Slice C author one new ST-specific disposable mutation world? The stop
  evidence covers the requirement either way; the choice affects only test
  lineage and report parity, and this audit has no preference.

## 7. Optional improvements (explicitly not defects)

- **O1.** §11.1/§11.3 step 2 could name the exact public derivation path for
  ST's kernel queries (a `ModelQueries` constructed over the same loaded model
  reached through the injected CN facade's public lower-facade chain —
  mirroring the accepted CN constructor pattern, facade.py:99–103) so no
  implementer is tempted toward the private-field access that §15.3 already
  forbids.
- **O2.** §12.2 could state in one line that the five non-`not_evaluated`
  condition-alignment values map one-to-one onto the five condition-level
  refusal reasons, making the emission rule ("every independently applicable
  reason", line 1354) visibly exhaustive against §12.1's closed literal.
- **O3.** §18.4 could add one composed lifecycle row (withdrawal of the sole
  tip of one corroborating root while the identical-body twin root stays
  healthy → aggregate remains `declared` with `inactive_roots_present`);
  rows L13 and L19 already cover the world jointly.

## 8. Verified non-findings (selected clearances)

The highest-risk checks below were probed to ground and cleared:

- duplicate-anchor SRG rejection, agreeing or divergent (§6.2 lines 466–469;
  §9.1 line 682; §9.3 line 723; row R08);
- refusal vocabulary: exactly nine reasons, closed literal, refusal emission
  policy ("every independently applicable reason remains visible", line 1354)
  plus the five-to-five status↔reason bijection makes lower typed-error
  masking structurally impossible without violating exhaustion;
- lifecycle-gated states still carry per-branch CN evidence; aggregate gating
  does not suppress disclosure (§12.4 lines 1374–1383; rows C11, T12);
- superseded-plus-withdrawn and duplicate-withdrawal shapes are rejected
  (§9.6 lines 827–831; rows L17–L18);
- cross-root convergence, cycles, self-supersession, and duplicate parents
  rejected; no time/authority/id winner selection (§9.3 lines 728–729; §9.4
  lines 754–762; row L16);
- mixed-revision, mixed-material, reordering, substitution, and nested-forgery
  rejection at both reconstruction boundaries (§14.1–14.2; rows H01–H07);
- no persisted or derived-state leakage: persist nothing (§11.3 step 11), no
  cache/projection/store (§11.1 lines 1140–1142; §15.3 line 1571; §21.2 lines
  2177–2178);
- demonstration append set is exactly two records over the verified 32-record
  baseline with all predecessor bytes and artifact hashes preserved (§19.1,
  §19.4 lines 1990–2000; rows D05–D09);
- inherited raw-source-authenticity limitation stated honestly and assigned an
  executable test (§14.3 lines 1507–1519; §17.7 lines 1698–1704; row H10);
- the §1.1 source-integrity disclosure about the challenger-file SHA mismatch
  is transparent and correctly scoped (Section 3, item 8).

## 9. Blocking determination

**No blocking defect exists.** Confirmed findings: 0 blocking, 1 major (D1 —
repairs to §12.3/§8.2 text plus one §18.7 row; required before the Slice C
gate), 1 minor (D2 — one sentence in §17.2, recommended before Slice A
store-validation work). Subject to the D1 repair and owner's answer to Q1, the
synthesis is fit for owner approval; Slices A and B are implementable as
specified.

## 10. Audit limitations

- This was a static design audit: no code was executed and no fixture,
  ledger, membership, or artifact was created or mutated.
- Cited constants, hashes, revisions, and contract semantics were verified
  against committed sources (Section 3); artifact bytes were not recomputed.
- The parallel Codex proposal was not read, per the audit boundary; the
  synthesis was assessed on its own text against committed truth only.
- The disclosed SHA mismatch between the challenger's delivery receipt and
  the on-disk challenger proposal (synthesis §1.1) is outside this audit's
  authority to resolve; it is noted, not adjudicated.

END OF ST-001 FINAL SYNTHESIS CHALLENGER AUDIT
