# FL-001 Codex Lead Proposal — Adversarial Challenger Audit

**Audit role:** single adversarial architecture challenger; this is an audit,
not a competing proposal and not implementation.

**Proposal under audit:**
`docs/superpowers/proposals/2026-09-02-fl001-codex-lead-proposal.md`

**Proposal digest (verified):** `4ab663af9e5766bb088353c95878b9115fb96973939778fc0fb42ac195dac092`
(2,149 lines / 23 numbered sections / ends exactly with
`END OF FL-001 CODEX LEAD PROPOSAL`).

**Audit date:** 2026-09-02.

This report uses **MUST**, **MUST NOT**, and **SHOULD** in their ordinary
normative senses. It modifies nothing outside this file.

## 1. Verified baseline and proposal digest

Baseline, verified independently in this session from a clean working tree:

- `HEAD`, local `main`, and `origin/main` resolve to
  `1d53d8adb22aada01bf808adb7dc7454a688543d`.
- `models/demo-printer/records/` contains exactly 34 committed records.
  Recomputing `compute_revision_id("demo-printer", <sorted 34 ids>)` from the
  on-disk records yields
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41` —
  an exact match to the accepted revision. Zero `trg_`, zero `trd_`, zero
  `trw_` records; zero `frg_`, `fld_`, `flw_` records.
- Proposal file digest re-verified byte-for-byte: SHA-256
  `4ab663af9e5766bb088353c95878b9115fb96973939778fc0fb42ac195dac092`;
  23 numbered sections; exact ending marker present; 2,149 lines.

Authoritative contracts consulted and re-verified in-source during this audit:

- `backend/model_kernel/port_results.py` (literal sets,
  `_ConnectionsResult._bind` forged-payload comparisons);
- `backend/model_kernel/queries.py`
  (`port_interface` lines 757–804; `connections_exact` lines 878–936;
  `connections_of_port`; `connections_containing`);
- `backend/model_kernel/contracts.py` (`MODEL_RECORD_ID_PATTERN`;
  `ModelRecordEvidence` regex line 118 — confirmed to admit `trg|trd` and to
  exclude `trw`/`flw`-style withdrawals; six `EvidenceRef` arms);
- `backend/system_identity/minting.py` (uuid4-only keyword-only minters; no
  I/O, no lookup, no clock);
- the authoritative demo records themselves (`pcn_4861…`, both `prg_`, all six
  `pif_` records — contexts, dimensions, values, and citations read directly).

No proposal claim that could be checked against these sources failed the
check except as detailed in Sections 5–7 below.

## 2. Executive verdict

**Verdict: APPROVE WITH CORRECTIONS.**

- Blocking defects: **0**.
- Required corrections: **3** (RC1–RC3, Section 6).
- Non-blocking observations: **8** (NB1–NB8, Section 7).
- Genuine owner decisions remaining: the nine proposal owner questions are all
  properly framed; the audit adjudicates each in Section 17. Six endorse as
  written, three endorse with a stated correction or explicit deferral note.

The lead architecture — one opaque durable `FlowAnchor` owning a permanent
`(source port set, sink port set, FlowKindToken)` signature, with exact
correctable PCN/PIF support pins in the declaration layer and **no**
prerequisite `ConnectionAnchor` — survives this adversarial pass. It is
coherent, it stays inside every accepted boundary it touched in this audit,
and its refusal inventory is genuinely enforced by its own admission gates and
acceptance matrix, not merely asserted in prose.

The three required corrections are bounded: one vocabulary bug (`inactive`
mis-worded as "structurally unreachable"), one missing normative rule for
view-independent PCN coverage in `flows_involving_port()`, and one missing
acceptance-matrix row for FRG evidence sufficiency-at-admission under PCN/PIF
absence. None of them reopens the design.

## 3. The strongest case for the lead architecture

1. **Permanent identity is put exactly where the accepted pattern puts it.**
   Every accepted kernel family (MK-001, PT-001, VP-001, BH-001, ST-001,
   ST-002) anchors durable meaning in a permanent opaque registration whose
   content is selected once and cannot be corrected, and pushes all
   correctable, evidence-backed, context-relative assertion content into a
   separate declaration layer with lineage keys and `supersedes` DAGs.
   FL-001 clones that shape precisely: FRG is context-free and permanent; FLD
   carries `(flow_anchor_id, exact AssertionContext)` and the exact pins.
   This is not stylistic mimicry — it is what makes replay, correction,
   corroboration, conflict, and withdrawal derivable by reuse of the accepted
   `_pt_dag_indexes` machinery rather than by new machinery.

2. **Identity is correctly divorced from correctable meaning (question set
   B).** Because the FRG signature contains only permanent facts (the role
   partition and the token), a correction to any supporting PCN/PIF, a
   withdrawal of a pinned PCN, or a conflict in the pinned root cannot mutate
   what the `flo_` anchor denotes. The identity-trap attack on every immutable
   field was run in Section 8 (A–G of the question set); each attack either
   (a) correctly forces a new anchor (which is the intended semantic) or (b)
   correctly survives as an alignment/status disclosure. The signature is
   minimal and exactly sufficient.

3. **The exact-union PCN pin is the right defense against the strongest
   available attack (question set C).** The only way to get pairwise claims
   from a hyperedge is to admit a containing or overlapping PCN as support.
   §10.1 rule 3 requires `endpoint_port_anchor_ids == sorted(source ∪ sink)`
   *exactly*, and R04/R05 make the subset/superset/`connections_containing()`
   bypass typed rejections. A `(A,B,C)` bus PCN cannot launder an `(A)→(B)`
   flow. This is the load-bearing rule of the whole proposal and it is
   enforced at admission, not at query time, which is where it must be.

4. **The lead honestly declines to do things the current stack cannot do.**
   §16's ten-point binding-facts list is correct against source (verified
   against TS-001 temporal semantics and BH-001 cohort semantics in this
   session). The deferral of measured/occurrence/conservation/causal claims
   is not caution theater; every deferred claim has a specific, named
   prerequisite contract. Nothing is permanently collapsed into the
   declaration record (question set J): the FLD carries no field that a later
   occurrence or measurement layer would need to reinterpret, and §22.3's
   future-compatibility guarantees forbid the reinterpretation paths.

5. **The lifecycle/query layer is honest about what it discloses.**
   §10's three orthogonal axes (FLD lifecycle; pinned record activity;
   pinned lineage health) and §10.4's explicit requirement to derive PT facts
   through the *accepted* PT derivations (not a parallel implementation) are
   verified in this audit to be implementable against the current
   `queries.py` and `port_results.py` (Section 14). The critical
   attack — another active PCN root hiding that the *pinned* root is
   conflicted or withdrawn — is defeated structurally: Q10 requires the two
   derivations to be disclosed side by side, and the verified
   `_ConnectionsResult._bind` derivation collapses subject conclusions to
   `asserted` whenever any root anywhere has an active tip, so a forged row
   that hides pinned-root failure is caught by the parity comparison.

## 4. The strongest case against the lead architecture

1. **Exact-signature uniqueness is a real expressiveness cost with a
   permanent price.** §4.3 accepts that two genuinely distinct same-kind
   mechanisms sharing exactly the same role sets cannot be represented as two
   v1 flow identities — an owner would have to pick one anchor or defer the
   domain's second mechanism to a later additive-discriminator contract. The
   proposal knows this (§4.3 third bullet, question 5), so this is an
   acknowledged limitation, not a defect. But it is the sharpest thing the
   design gives up, and it is given up permanently for v1 identities.

2. **Mandatory direction-role pinning excludes honest non-directional
   interfaces.** The §10.2 table admits source{output,bidirectional} and
   sink{input,bidirectional} only. A real directed claim supported by an
   interface the owner honestly declared `non_directional` cannot be admitted
   — even with an exact-union PCN and full evidence. This is a deliberate
   boundedness (§10.2 final paragraph says so), but it means a real class of
   legitimate declarations will be refused until the owner relaxes the rule,
   and the refusal will look like a data-entry error to an authority that
   has honestly described its port.

3. **The exact-union PCN rule imposes a record-tax on layered topologies.**
   A containing bus PCN over (extruder, heater, sensor, fan) does not support
   an (extruder)→(heater) flow; a separate exact (extruder, heater) PCN must
   also exist and be pinned. This is correct and safe, but it means domains
   described only at bus granularity cannot declare individual flows without
   first adding per-pair PCN records. The proposal knows this (§22.2 row 4).

4. **The proposal is not a physical truth claim — but it must be read that
   way to be used, and nothing in the kernel can force that reading.** The
   `declared` conclusion is model-membership-relative, but a downstream
   reader can still misread a healthy/current/aligned disclosure as "flow is
   flowing." §2.2 and §12's refusal vocabulary mitigate this; they cannot
   eliminate it. This is inherent to any declaration-only architecture and is
   the residual risk the owner accepts by approving any declaration plane.

None of these four rises to a blocking defect or a required correction. All
four are either explicitly owned limitations in the proposal or residual
risks the current kernel design already accepts elsewhere.

## 5. Blocking defects

**None found.**

Zero blocking defects were confirmed against:
- question set A (FlowAnchor as enduring referent): no counterexample
  survives that requires a ConnectionAnchor to resolve;
- question set B (identity vs correctable meaning): every immutable field
  checked against a hostile mutation scenario either forces a new anchor
  correctly or survives as an alignment disclosure;
- question set D (evidence pinning and staleness): R09/R10 stale-pin
  admission is explicitly correct, disclosure-only, and parity-checked;
- question set H (canonical integrity / replay): the proposal reuses the
  exact accepted canonicalization and `mrv_` algorithm, verified in Section
  1 by recomputation.

## 6. Required corrections

Each correction identifies the proposal section, the unsafe or incomplete
statement, the concrete failing scenario, and the smallest normative fix.

### RC1 — §10.5's "`inactive` plus `current` is structurally unreachable" claim is wrong and must be reworded

**Affected section:** §10.5 (the paragraph after the connection-alignment
precedence table), and by symmetry §10.6's implied mirror claim about direction
alignments.

**Unsafe / incomplete statement:** "`inactive` plus `current` is structurally
unreachable and must be rejected by outer-result validation if forged."

**Concrete failing scenario:** the claim conflates two different things that
do not have the same reachability. (a) A pinned-record *activity* of
`current` while the containing lineage health is `inactive` IS structurally
unreachable in honest data — an inactive lineage has zero current tips, so
any pinned record in it is necessarily superseded or withdrawn; both accepted
kernel derivations (queries.py lines 886–901 and the verified `_bind`
recomputation) make this impossible. (b) But the table row above the claim
says "`inactive` | `superseded` or `withdrawn` | `connection_lineage_inactive`",
meaning the proposal *itself* already treats `(inactive, withdrawn)` and
`(inactive, superseded)` as real reachable table rows. The sentence says
"`inactive` plus `current`" as if `inactive` itself were the unreachable
member; the precise statement is that only the **(inactive, current)** pair
is unreachable, and the sentence must say exactly that so the acceptance
matrix row covers the right forgery and not the wrong one. As written, a
reviewer could read §10.5 as declaring `inactive`-root pinned rows themselves
unreachable, which contradicts the table two lines above it and would make
L12/Q08 unpinnable.

**Smallest normative correction:** replace the sentence with the exact pair
formulation — e.g. "Only the `(inactive, current)` (lineage, activity) pair is
structurally unreachable in honest data, because an inactive lineage has zero
current tips; it remains a mandatory forgery-rejection row. `(inactive,
superseded)` and `(inactive, withdrawn)` are real reachable rows and produce
`connection_lineage_inactive`."

**Adversarial acceptance row needed:** add (or sharpen Q08 to require) an
executable row: an honest result with lineage `inactive` and pinned activity
`superseded` or `withdrawn` *admits* and yields `connection_lineage_inactive`;
a forged result asserting `(inactive, current)` *rejects* typed; and no row
may treat `inactive` lineage alone as unreachable.

### RC2 — §11.6/`flows_involving_port()` is under-specified for view-independent PCN support

**Affected section:** §11.6 (`PortFlowsResult`) and, implicitly, §9.1 (exact
context equality).

**Incomplete statement:** §11.6 defines the port query over "the requested
context" and §9.1 establishes exact-equality so that an FLD under
`view_independent` matches only a `view_independent` PCN. Neither section
states which context the *incident-flow collection* uses when the caller
asks for a lifecycle view and the flow's only exact-equality PCN is
view-independent. The union-arm rule already exists (§9.1), but the
collection query's behavior under mixed available contexts is silent.

**Concrete failing scenario:** suppose a later authorized demo has an FRG
over the two existing demo ports, one FLD under
`LifecycleViewContext(as_designed)` supported by the existing PCN, and a
second, separate, correctly admitted FLD under `ViewIndependentContext`
supported by a view-independent PCN covering the same union. A caller asks
`flows_involving_port(prt_91a3…, context=as_designed)`. Two readings are both
defensible: (i) return only the `as_designed` entry (strict exact-context
collection); (ii) return both entries and let the caller see the
view-independent declaration as well (scope-broadening collection). The
proposal does not say which. Reading (i) is what the rest of the proposal's
"no cross-context mapping" doctrine implies and is what query Q13's
"exact … without traversal" language presupposes, but the collection result
never states the exclusion normatively — a subsequent implementer could
"helpfully" widen it and no acceptance row would fire.

**Smallest normative correction:** add one sentence to §11.6:
"`flows_involving_port()` returns exactly the FRG/context declarations that
match the caller's exact `AssertionContext`; declarations under any other
context arm or any other lifecycle view are not included, discovered, or
summarized. There is no context widening."

**Adversarial acceptance row needed:** add a Q-row (or sharpen Q13) requiring:
a port with FLDs under both `as_designed` and `view_independent` returns only
the requested arm's entries; the other arm contributes no entry, no count, and
no finding.

### RC3 — FRG evidence sufficiency-under-absent-PCN/PIF needs an explicit admission row

**Affected section:** §6.2 (FRG checklist) and §18.2 (R-rows).

**Incomplete statement:** §6.2 correctly makes the FRG checklist PCN/PIF-free
("The FRG does not cite a PCN or PIF as a mandatory registration dependency.
Its purpose is to preserve identity even when contextual support is absent,
corrected, conflicted, or withdrawn."). This is the right rule. But no
acceptance row pins the positive direction — that an FRG *admits* when
contextual support is genuinely absent.

**Concrete failing scenario:** an FRG is proposed for a flow whose exact
participant union currently has no admitted PCN at all (and hence no
pinnable PCN). §6.2 says the FRG must admit; without a positive acceptance
row, an implementer could reject with "no PCN exists for this union" and no
row would fail — the checklist's "not a mandatory registration dependency"
is prose where R01–R17 are executable. The negative direction is pinned
(R03 rejects FLD when FRG/PCN/PIF/parent is missing); the positive FRG
direction is not.

**Smallest normative correction:** add an R-row (suggested R-row: "R21"
in §18.2): "An FRG with complete PRG citations, claim-specific owner basis,
and full evidence closure admits even when no PCN and no PIF exist over the
registered participant union; the absence of contextual support does not
block registration."

**Adversarial acceptance row needed:** the R21 row above; plus one mirrored
negative row is already present (R03).

## 7. Non-blocking observations

- **NB1 (§7.2 "Dynamic bus roles" row).** The table correctly notes that a
  PIF `bidirectional` does not choose a speaker, but does not say what a
  domain SHOULD do when it genuinely needs dynamic arbitration. The answer
  (defer to an owner-gated arbitration contract; do not encode arbitration in
  a v1 hyperedge) is implicit in §2.4/§22.3. Making it explicit in the §7.2
  table would prevent a future reviewer from reading the row as a defect.

- **NB2 (§10.4 "shared authoritative PT derivation").** The requirement is
  correct, but the verb "derive ... through the accepted PT derivations"
  leaves open whether that means *calling* `connections_exact()` /
  `port_interface()` / `port_assertion()` or *inlining* their logic.
  Verified in this audit: `queries.py` lines 878–936 and 757–804 are the
  authoritative derivations; duplicating them in flow code would be a parity
  defect even if field-equal at first. A SHOULD-wording naming the call (not
  the inline) would close this. (The proposal's "never duplicated"
  language elsewhere strongly implies call-not-inline; this is a clarity
  point only.)

- **NB3 (§12.6's reuse of `TopologyConclusion`).** Verified exact
  (`port_results.py` line 27). One consequence worth flagging: because the
  subject conclusion collapses conflicted roots to `asserted` whenever any
  tip exists on any root, the topology conclusion cannot by itself surface
  "the pinned root is conflicted." §10.4's final sentence and Q10 already
  require the per-row pinned lineage health to be disclosed alongside. This
  is the correct fix — just note that §12.6's table alone is insufficient
  without §10.5's per-pin rows, and readers should not treat the topology
  conclusion as a summary of health.

- **NB4 (§4.3 / question 5 — parallel same-signature mechanisms).** Not a
  defect, but the limitation is permanent for v1 anchors: changing it later
  forces new anchors (§4.3 final sentence, §22.3). If a domain with true
  parallel same-kind same-locus mechanisms is anticipated soon, the owner
  should know the additive discriminator is not a small patch — it is a new
  identity dimension and a new family of registrations.

- **NB5 (§8.3, deferred commodity/carrier dimensions).** The proposal
  correctly refuses to let PIF domain/type equality imply flow-kind. The
  residual trap is social, not technical: a FlowKindToken `code` such as
  `"water"` looks decomposable to a human reader. §8.2 already says the
  kernel never decomposes the token. Nothing further is needed; just note
  that the honesty burden lives in authority vocabulary discipline, where
  the kernel cannot enforce it.

- **NB6 (§11.4 lightweight support rows).** `FlowEffectiveBodyGroupResult`
  carries `support_alignment_summary`. Verified in this audit that the
  precedence in §10.7 (conflicted > inactive > stale > aligned) is
  self-consistent and matches the precedence in §12.9. One implementer
  caution: alignment rows are per-group, and a body group can span more than
  one root (corroborating roots share a body); the support rows inside the
  group must be identical across those roots or the grouping is wrong. The
  proposal's effective-body equality rule (§9.5) plus Q05's corroboration
  disclosure already force this, but it is an easy place to get a test that
  passes by construction and misses the case.

- **NB7 (§13.2 step 6 / carry-once).** The thirteen-step revalidation is
  the accepted carry-once pattern. Verified that PT sibling results
  (`_ConnectionsResult._bind`, lines 880–970) run exactly the recompute-and-
  compare discipline the proposal mandates for flow results. No new machine
  is required; the discipline is reusable, and the proposal says so.

- **NB8 (§20.2 demo evidence assessment).** Verified directly against the
  committed records this session: the demo's two PRGs, the single PCN whose
  `endpoint_port_anchor_ids` exactly equal their union in `as_designed`, and
  the two complementary direction PIFs (`output` on the subsystem-interface
  port, `input` on the extruder-interface port) in the same context
  materially satisfy the §6.2/§6.3 citation and section 10 admission
  preconditions for a future FLD. §20.2's conditional language ("admission
  evidence ... if") is exactly right and not overstated. The demo's PRG
  citations by the PIFs are also correct (each PIF cites the PRG of the port
  it describes), which is what §6.3 item 4 independently requires.

## 8. Concrete adversarial counterexamples — run to completion

This section runs the sharpest available concrete attack against each
adversarial question set and reports the outcome. None of them defeats the
architecture; two (RC1/RC2 input scenarios) expose documentation gaps, not
design flaws.

**A1 — transfer-never-occurred (question set A).** FRG/FLD exist; no
occurrence ever follows. Outcome: FRG remains permanent, FLD remains
membership-relative; §9.8 replay restores older lifecycle conclusions;
nothing anywhere escalates `declared` to `occurred`. Pass.

**A2 — replay-absent PCN support.** FLD pins PCN_X; replay membership omits
PCN_X. Outcome: L14 (replay retaining FLD while omitting a dependency
rejects) catches this at validation, before any query. Pass.

**A3 — PIF role change after FLD admission.** PIF is corrected from
`output` to `input` after the FLD pins it. Outcome: exact pin is unchanged;
the FLD's pinned activity becomes `superseded`, alignment becomes
`pinned_direction_superseded`, lifecycle stays `declared` (orthogonality,
§10.3), and Q09 forces the relation disclosure to move to `inconsistent`
without touching the conclusion. Pass — this is exactly the orthogonality
the design is for.

**A4 — endpoint replacement.** A port's physical hardware is replaced; the
owner mints a new PortAnchor and PRG. Outcome: §4.5 correctly requires a
new FRG and new FlowAnchor; the old flow identity cannot silently survive
because continuity is signature-based, not name-based. Pass.

**A5 — shared endpoints, multiple commodities.** Two flows share the same
port union but have different FlowKindToken codes. Outcome: §4.3 admits
both (different signatures); the exact-union PCN can be the same or
different PCNs; no false exclusivity is inferred. Pass.

**A6 — direction reversal.** A reversed `(sink→source)` signature coexists.
Outcome: §7.2 "Reversed direction: separate FlowAnchor and FRG" and I06 pin
this; `bidirectional` never synthesizes a reverse. Pass.

**A7 — cyclic flow graph.** FRG1 (A→B), FRG2 (B→A) coexist. Outcome:
records may coexist; no traversal, no loop conclusion, no causality — N04
pins it; §7.5 states it. Pass.

**C-attack (set C) — PCN superset laundering.** A containing PCN over
{A,B,C} used as support for (A)→(B). Outcome: R04/R05 typed rejection at
admission; `connections_containing()` result structurally cannot be
substituted for the pinned record ID. Pass — this is the attack the
exact-union rule exists to kill.

**C-attack — many-to-many branch fabrication.** FRG {A,B}→{C,D} admitted.
Outcome: §7.1's non-expansion rule and N01 pin that no pairwise record or
conclusion is produced; the hyperedge stays one group relation. Pass.

**C-attack — larger PCN supporting smaller flow.** Same as the superset
attack above, with a different framing; same outcome. Pass.

**D-attack — stale alignment vs lifecycle.** Pinned PCN withdrawn after FLD
admission. Outcome: §9.7/§10.3 keep FLD lifecycle healthy; alignment becomes
`pinned_connection_withdrawn`; summary becomes `stale`; Q11 requires the
summary never to change the lifecycle conclusion. Pass.

**D-attack — forged carry-once.** Attacker supplies a result asserting
`exact_current` for a pinned superseded PCN. Outcome: §13.3 and the verified
PT `_bind` pattern (recompute-and-compare) catch it; alignment precedence is
recomputed from the rebuilt `LoadedModel`, never trusted. Pass.

**E-attack — BH equality laundered as conservation.** N08/N09 and §16.4's
prerequisite list reject; no evaluator exists to produce a conservation
field. Pass — verified against BH-001's documented cohort semantics.

**E-attack — ST-002 transition + temporal ordering laundered as flow.**
N10/N12/N16 and §16.1 points 1/8/9/10 reject across four independent
grounds. Pass — verified against ST-002's declaration-only scope.

**K-attack — demo facts fabricated.** §20.2's PT claims are not fabricated:
verified directly against the committed records in this session (see NB8).
No fixture identity, ID, hash, membership, or revision is approved by this
audit. Pass.

## 9. Identity-boundary verdict

The identity boundary is **sound**.

The permanent signature — `(source set, sink set, complete FlowKindToken)` —
contains exactly the facts that cannot be corrected without changing what
the flow *is*, and nothing else. Every attack that would mutate those facts
requires a new anchor (which is correct). Every fact that can change under a
fixed flow identity — supporting PCN, supporting PIFs, evidence, authority,
`recorded_at`, note, correction DAG position, withdrawal state — is in the
correctable declaration layer, where it belongs under the accepted kernel
pattern.

Within-role ordering is correctly non-semantic (sorted canonical tuples; I05
pins permutation invariance). Cross-role ordering is correctly semantic
(I06 pins that reversal changes bytes and ID). The disjointness and 2–64
union bounds mirror PT's PCN bounds and are pinned by I04.

The one residual note (not a defect): because the signature is the identity,
the signature also bounds what v1 flow identities can *distinguish*. §4.3
accepts this explicitly; question set J confirms nothing is permanently
collapsed into it.

## 10. ConnectionAnchor prerequisite verdict

**No prerequisite ConnectionAnchor is required. The lead's §3.2 rejection is
correct, and its six-part justification is complete against the verified PT
contracts.**

The decisive fact — verified in `queries.py` lines 886–901 and the
`_bind` subject derivation — is that the subject-level topology conclusion
already aggregates over *all* roots of the exact subject tuple. A
ConnectionAnchor would add an identity layer only if one or more of the
following had to be said, and §3.2's list is airtight that FL-001 v1 says
none of them:

- particular cable/pipe/channel/conduit identity (§3.2 item 1);
- continuity of a connection while endpoint membership changes (item 2 —
  and §4.5 explicitly forbids this);
- distinguishing parallel same-endpoint same-context connections (item 3);
- connection-owned variables, behavior, state, metadata, observations, or
  occurrences (item 4);
- flow along *this particular connection instance* (item 5 — this is the
  occurrence plane, correctly deferred in §16.5);
- route/segment/traversal identity (item 6).

Promoting a PCN root to such an anchor would be unsound for a second,
independent reason the proposal also states: PCN roots are *evidence
lineages* within one context, not enduring physical objects. Two independent
roots can corroborate one topology subject (verified: `port_connection_`
index structure allows multiple roots per subject key). Treating a root as
a connection identity would misattribute corroboration as plurality and would
give a correction-DAG lineage physical-world meaning it does not have.

**Verdict: Alternative A is the correct lead recommendation.** A future
ConnectionAnchor remains reachable through §22.3's additive path without
reinterpretation; it is not needed now and would be harmful if added now.

## 11. Declaration-versus-occurrence vocabulary audit

The vocabulary boundary is **clean and, more importantly, enforced**.

The normative short form (§2.2) and the literal refusal list
("`flowing`/`active`/`enabled`/`open`/`running`/`occurred`/`measured`/
`balanced`/`causal`/`correct`/`healthy`/`recommended`") are not aspirational;
they are load-bearing in three places:

1. **Field level.** §5.5's FLD field inventory has no rate, amount, unit,
   occurrence, command, event, guard, action, effect, validity, diagnosis,
   or recommendation field — the claim is unmade at the schema level, which
   is the only level that cannot be regressed by documentation drift.

2. **Query-name level.** §11.1's forbidden-alias list is executable (Q01
   requires exactly the four approved method names and proves the forbidden
   ones absent). N05–N16 pin each individual laundering route separately.

3. **Forgery-rejection level.** §13.3's hidden-field rejection list
   ("`flowing`, `observed`, `rate`, `occurred`, `cause`, `safe`,
   `recommended_action`") makes an attacker unable to smuggle the vocabulary
   back in through a nested forged row.

Cross-checked against question set F: no commanded flow, no observed flow,
no calculated/inferred flow, no occurrence, no rate, no conservation, no
active state, no causal influence appears anywhere as a field, a literal, a
method, or a finding. The three-layer enforcement plus the N-row acceptance
coverage is sufficient.

## 12. Evidence-pinning and staleness audit

The pinning model is **correct and correctly disclosure-only**.

- **Admission gate.** §10.1/§10.2 require exact record IDs, exact subject
  union, exact context, exact dimension, exact allowed role. The pin is to
  the *record*, not to current content — which is what makes later
  corrections unable to silently retarget an old FLD (§3.1's core property,
  pinned by R09/R10/R11).

- **Staleness handling.** Currentness is *disclosure* (alignment rows),
  never a lifecycle override. The three-layer alignment model — pinned
  activity, pinned containing-root health, aggregate summary — has the
  correct precedence (lineage health before individual activity: §10.5/§10.6,
  then conflicted > inactive > stale > aligned: §10.7/§12.9). Verified
  self-consistent and verified against the accepted PT derivation precedence
  (`queries.py` line 890 computes lineage health from tips, which is
  exactly the "containing-root health first" rule the proposal adopts).

- **Replay.** §9.8 and L13/L14 pin replay semantics: omitting a successor
  or withdrawal makes an older FLD current again in that membership;
  omitting a pinned dependency rejects. This matches every accepted kernel
  family and uses the membership-relative replay convention verified in the
  28/29/32/34 historical memberships.

- **Validity vs stale-alignment vs historical state.** The design keeps all
  three distinct exactly as required: admission validity (record closure),
  stale alignment (disclosure), and historical state (replay-relative
  lifecycle). No axis leaks into another. Verified against §10.3's
  orthogonality bullets and Q03/Q11.

The one documentation correction needed here is RC1 (the mis-worded
unreachability sentence), which is in the staleness area but does not weaken
the model.

## 13. Hyperedge and role-semantics audit

This is the audit area where the proposal is at its strongest, because the
load-bearing rule is the simplest possible one: **the pinned PCN's exact
endpoint set must equal the exact sorted union of source ∪ sink**.

Everything in question set C is decided by that one equality, plus §9.1's
exact-context equality, plus §10.2's per-participant role table, plus
§4.2's disjointness/role-sort rules:

- **Fan-out, fan-in, many-to-many, bus partition:** all admitted as *one*
  group relation; N01 pins non-expansion; §7.1 pins non-bipartite,
  non-broadcast, non-mixing.
- **Intermediate participants / bus with dynamic talker:** the static
  partition is admitted; the dynamic arbitration is correctly deferred
  (§7.2 row, NB1).
- **Bidirectional:** never synthesizes a reverse; N03 and §7.4 pin it.
- **Cycles:** records coexist; N04 and §7.5 pin non-traversal and
  non-causal.
- **Pairwise adjacency fabrication:** killed at admission by R04/R05.
- **Larger PCN supporting smaller flow:** same admission kill; this is the
  anti-laundering defense and it is at the right layer (admission, not
  query).
- **Several PCN roots, one flow:** §12.6's subject conclusion handles it
  and §10.4/Q10 force the per-pin health to stay visible beside it, so the
  subject aggregation cannot hide pinned-root failure. Verified against the
  subject-derivation code this session.
- **Self-flow and one-port flow:** rejected by disjointness plus PCN's own
  distinct-endpoint requirement (I04, §7.2 rows).
- **Cross-root PCN corroboration vs PIF single-root rule:** correctly
  preserves PT's asymmetry (PCN allows corroborating roots, PIF forbids
  them per key) — verified against the store's comment at partitioning and
  the per-key `interface_roots_by_key` behavior reflected in the
  `port_interface` derivation.

No false pairwise claim can survive these gates. The hyperedge semantics are
sound.

## 14. Lifecycle / replay / canonical-integrity audit

**Lifecycle.** The declaration lifecycle is the accepted kernel pattern
with no novel mechanics: permanent FRG, correctable FLD with `supersedes`,
same-root merge allowed only when every parent shares the derived root
(L02/L06), cross-root corroboration only on byte-identical effective bodies
(L07), cross-root disagreement on any pin difference (L08), current-tip-only
withdrawal (L10), successor-plus-withdrawal race rejected independent of
append order (L11). All verified consistent with the accepted
`_pt_dag_indexes` discipline this pattern reuses.

**Effective-body scope.** §9.5's body — `{flow_anchor_id, context,
connection_assertion_record_id, source_direction_pins,
sink_direction_pins}` — is exactly the right scope. Including the pins in
the body is what makes L08 (different exact pin ⇒ body disagreement)
correct; this prevents independent roots from silently claiming
corroboration across different support contracts. Correct.

**Replay.** §9.8 and §19.2 pin membership-relative replay over the exact
accepted historical memberships (9/10/11/14/16/18/28/29/32/34), with the
34-record membership being verified by recomputation in this very audit.
Pre-FL structured absence is pinned by P01 and §19.3.

**Canonical integrity.** §5.8 reuses the normative canonicalization exactly
(Python-mode dump excluding `record_id`; recursive UTC `+00:00`; sorted
keys, compact separators, `ensure_ascii=False`; SHA-256 over exact bytes;
prefix). I10/I11/I12 pin this against literal golden vectors. I13 pins
non-regression of existing vectors. No new canonicalization is introduced;
no hash-seed independence issue exists (uuid4 minter, no derivation from
names, no seeds anywhere in identity or record bytes).

**Hostile construction / stale IDs / mixed revisions / evidence closure /
withdrawal-citation ban / store-independent validation / exact vocabularies:**
all pinned in §13.3's forgery list and R17 (frg/fld citable, flw and every
existing withdrawal uncitable). The evidence-grammar extension (§6.5) is
minimal and exactly correct — verified against the current regex line.

**Slice B structured absence.** §21.2 pins "exact structured absence on the
untouched authoritative 34-record ledger", which is the authoritative
zero-transition/flow query path — verified that the 34-record membership
contains zero `frg_`/`fld_`/`flw_` so the four queries return the
documented structured-absence results, not errors.

## 15. Import and ownership audit

The import direction and package ownership (§15) are **correct and
complete**.

- `backend.system_identity` owns the new anchor and minter; it imports no
  model-kernel code. Verified: existing minters (`mint_transition_anchor`,
  `mint_port_anchor`, etc.) are uuid4-only, keyword-only, no-I/O; the
  proposed `mint_flow_anchor` is the same shape.
- `backend.model_kernel` owns the contracts, generic `build_record`,
  admission, lifecycle, indexes, replay, and query derivation. It does not
  import and must not import source, temporal, binding, interpretation,
  model-state, semantic-compatibility, constraint, behavior-evaluation,
  or state-classification packages — §15.3 forbids them all and §1.3 commits
  to the dependency floor. Verified that the existing kernel already satisfies
  this floor (imports only `backend.system_identity`, Pydantic, stdlib).
- PT records and flow records are peers in the kernel; §15.2's arrow
  semantics ("may be depended on by the layer above") is the right way to
  say that same-package reuse of PT derivation helpers does not reverse the
  dependency direction. Correct.

No new ledger, no extra store, no second revision plane — §1.3 and §14.4
commit, §14.2 step 8 computes the existing `mrv_` only. Verified this is
consistent with how the 34-record membership already behaves.

## 16. Acceptance-matrix enforcement gaps

The matrix is **strong**. Counting rows: I01–I15 (15), R01–R20 (20),
L01–L16 (16), Q01–Q22 (22), N01–N16 (16), P01–P10 (10) — 99 executable rows
planned. Coverage of the accepted kernel's defensive posture is unusually
complete: canonical forgery (I), admission (R), lifecycle (L), query parity
(Q), non-inference (N), preservation (P) each have dedicated bands, and the
bands reference the exact vocabulary of the corresponding contract section.

The three genuine gaps are exactly the three required corrections:

1. **RC1 gap:** no row currently pins "honest `(inactive, superseded)` /
   `(inactive, withdrawn)` pinned rows admit as
   `connection_lineage_inactive`" *separately from* pinning
   "`(inactive, current)` rejects". Q08 comes closest but does not state the
   admit direction normatively, and the §10.5 sentence being corrected makes
   the ambiguity load-bearing.
2. **RC2 gap:** no row pins the exact-context-only exclusion inside
   `flows_involving_port()` when other context arms exist on the same port.
   Q13 pins role assignment and "without traversal" but not context-arm
   exclusion.
3. **RC3 gap:** no positive row pins FRG admission under genuinely absent
   PCN/PIF support; R-band pins the negative (FLD rejects when dependencies
   are missing) but not the positive FRG side.

No other row found missing after cross-walking every prohibition in
§2.2/§2.4/§7/§16/§17 against the matrix. The ST-002-audit-era correction
patterns (stale-pin disclosure unpinned, same-root merge/cross-root parent
rejection, withdrawal-uncitable, authoritative zero-record query path,
single-derivation-source parity) are all already absorbed into R09/R10,
L06/L02, R17, §21.2 structured-absence, and Q06/Q07 respectively — the FL
proposal demonstrably learned from that audit.

## 17. Assessment of all nine owner questions

Each question is adjudicated **endorse / endorse with correction / reject /
remains a genuine owner policy decision**, with the smallest safe decision and
its consequence.

**Q1 — Durable logical directed FlowAnchor, defer ConnectionAnchor:
ENDORSE.** Smallest safe decision: approve as §3.5 states, with the §3.5
limitation quote kept verbatim in the final spec. Consequence of approving:
v1 cannot name parallel or replaced physical connections (accepted, §22.2).
Consequence of rejecting: FL-001 cannot proceed without a ConnectionAnchor
contract that PT's own root semantics make unsound right now (Section 10).

**Q2 — Permanent `(source set, sink set, complete FlowKindToken)` identity:
ENDORSE.** Smallest safe decision: approve exactly; every attack on a
signature field forces a new anchor, which is the intended semantic
(Section 8, A4/A6). Consequence: a later commodity/carrier dimension
requires a new family of registrations, not a patch (NB4).

**Q3 — Full 1→1 / fan-out / fan-in / many-to-many as non-pairwise group
relations, not limited to 1→1: ENDORSE.** Smallest safe decision: approve
all four shapes under §7.1's non-expansion rule. Consequence of limiting to
1→1: no expressiveness gain (1→1 is not safer), and a real fan-in domain
would need N artificial anchors with no added protection.

**Q4 — One exact-union PCN plus one exact direction-role PIF per
participant, strict role table: ENDORSE.** Smallest safe decision: approve
§10.1/§10.2 as written, including the source{output,bidirectional} /
sink{input,bidirectional} table. Consequence: honest `non_directional`
interfaces cannot support a directed declaration until the owner relaxes the
rule (Section 4, point 2); this is a known, bounded refusal the proposal
already documents.

**Q5 — At most one FRG per exact semantic signature, deferring parallel
same-kind same-locus mechanisms: REMAINS A GENUINE OWNER POLICY DECISION —
but the audit's recommendation is ENDORSE-as-written.** This is the one
question where the cost is truly permanent and domain-shaped. Smallest safe
decision if approved: accept §4.3's deferral and §22.3's additive escape
hatch verbatim. Consequence: if a domain with two genuinely parallel
same-kind same-locus mechanisms appears *during* v1's service life, the only
moves are (a) choose one anchor for it, or (b) wait for the additive
discriminator contract; there is no v1-internal fix. If the owner knows now
that the first real application has such a domain, that fact belongs in the
approval record — the discriminator contract should then be scheduled early.

**Q6 — Flows spanning several exact port owners, no single subject entity,
no hierarchy inference: ENDORSE.** Smallest safe decision: approve §4.4/§7.3
exactly. R02 already pins the no-hierarchy-inference rule executably.
Consequence: a domain that wants a "system" or "plant" scope field must wait
for a later owner-gated contract; §4.4's reasoning (the port set already
bounds the locus) is correct.

**Q7 — Both exact AssertionContext arms, stale-pin admission with no
retargeting, support alignment orthogonal to lifecycle: ENDORSE WITH
CORRECTION.** Endorse the architecture; apply RC1 (the `inactive`/`current`
unreachability wording) and RC2 (the `flows_involving_port` context-arm
exclusion). Smallest safe decision: approve §9.1/§10.1/§10.2/§10.3 as
written, with the two bounded edits in Section 6 carried into the final
synthesized spec. R09/R10/R12/R13 already make the substance executable;
the corrections pin edge-case semantics the substance presupposes.

**Q8 — Prefixes `flo_`/`frg_`/`fld_`/`flw_` and exactly the four queries
with the proposed result vocabulary: ENDORSE.** Smallest safe decision:
approve §5.1/§11.1/§11.2 exactly. Q01 and §13.3 pin the forbiddens. The
`flo_` prefix choice to avoid collision with the conventional `flw_`
withdrawal prefix is verified sensible against the accepted 3-letter
withdrawal convention (`ptw_`, `vpw_`, `bhw_`, `stw_`, `trw_`).

**Q9 — Ledger stays at 34 through Slices A–C; existing synthetic PT material
is only a *possible later, separately proposed* declaration-fixture
prerequisite: ENDORSE.** Smallest safe decision: approve §20 verbatim. The
PT facts it cites were independently re-verified true in this session (NB8);
the conditional "possible later ... prerequisite" phrasing is exactly right
and invents no identity, ID, hash, membership, revision, or timestamp. P10
pins the gate.

## 18. Exact recommendation for final synthesis

1. **Adopt Alternative A** (FlowAnchor owns the logical directed locus; no
   prerequisite ConnectionAnchor) as the FL-001 v1 architecture, exactly as
   §3.5 recommends.

2. **Carry the three required corrections into the synthesized specification
   before owner approval:**
   - **RC1:** correct §10.5's unreachability sentence (and its §10.6 mirror)
     to name the `(inactive, current)` pair precisely, and add the mirrored
     admission/forgery acceptance row described in Section 6.
   - **RC2:** add the exact-context-only collection rule to §11.6 and the
     Q-row sharpening described in Section 6.
   - **RC3:** add the positive FRG-admission-under-absent-support R-row
     described in Section 6.

3. **Adjudicate §23's nine owner questions per Section 17:** endorse Q1, Q2,
   Q3, Q4, Q6, Q8, Q9 as written; endorse Q7 with RC1+RC2 applied; treat Q5
   as the one decision whose answer genuinely depends on whether the first
   real application domain has parallel same-kind same-locus mechanisms —
   approve it as written unless the owner has that domain knowledge now, in
   which case schedule the additive discriminator contract early rather than
   blocking FL-001.

4. **Preserve the proposal's own gates verbatim in the synthesis:** the
   A–C slice boundaries, the §20 pre-append owner gate (P10), the zero-trust
   reconstruction discipline (§13), and the §22.3 future-compatibility
   guarantees. None of them is weakened by this audit.

5. **Do not relax anything this audit did not flag.** In particular: do not
   relax the exact-union PCN rule (it is the load-bearing anti-laundering
   defense), do not soften the direction-role table to be "helpful" without
   a separate owner decision, and do not pre-synthesize a ConnectionAnchor
   "just in case".

6. **Scope confirmation for the record:** this audit wrote no code, no
   tests, no fixtures, no identities, no records, no ledger entries, and no
   artifacts other than this report; it modified no existing file; it ran
   only read, digest, recompute, and grep operations against the repository;
   it performed no commit, push, merge, rebase, reset, cherry-pick, or
   history operation. The lead proposal file was opened read-only; its
   SHA-256 digest was re-verified unchanged at the start of this report.

END OF FL-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
