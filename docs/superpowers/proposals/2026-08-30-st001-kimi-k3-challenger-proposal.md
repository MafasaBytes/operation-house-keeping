# ST-001 — Independent Architectural Challenger Proposal

**State Identity and Evidence-Gated Classification**

| | |
|---|---|
| Author | Kimi K3 (independent challenger) |
| Date | 2026-08-30 |
| Repository baseline verified | `main` = `origin/main` = `0ed77df7ea4870faec1eae9b89668add97aa855d`, clean tree |
| Authoritative model ledger | 32 records |
| Model revision | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |
| Classification | Independent architectural proposal, implementation-ready, non-authoritative until owner-gated |

This document is a complete alternative architecture for ST-001. It exists
because the owner explicitly requested an independent challenger pass in
parallel with another model's proposal. It does **not** read, summarize,
modify, or react to that proposal, and it derives every claim directly from
the accepted repository.

The fixed owner direction is: stable state identity and evidence-gated state
classification, established **before** any transition system, explicit
exclusion of transitions, from/to identity, triggers, actions, causal
inference, control, state-machine execution, and persisted computed state.

---

## 1. Repository Findings

These findings come from direct inspection of `backend/`, the accepted ADRs
(`docs/adr/0001`–`0015`), the accepted specs (`docs/superpowers/specs/`), and
the committed demo ledger. Every consequence in later sections cites one of
these facts.

### 1.1 Anchor, identity, and ledger discipline

- **F1.1** System identities are opaque UUID4-backed anchors (`ent_`, `var_`,
  `con_`, `prt_`, `bhv_`). Names, namespaces, and role names are human-facing
  context only and never participate in matching.
- **F1.2** The model kernel (`backend/model_kernel/`) is an append-only ledger
  of explicit model knowledge. Runtime kernel code imports only
  `backend.system_identity`, Pydantic, and the standard library — enforced by
  AST-isolation tests.
- **F1.3** Registrations (`reg`, `vrg`, `prg`, `crg`, `brg`) are permanent,
  evidence-bearing membership claims with **no lifecycle, no correction path,
  no withdrawal field**. The `vrg` precedent is explicit: "no lifecycle, no
  correction path, no units, no datatype, no meaning, no state."
- **F1.4** Correctable claims (`vcn`, `bhd`, `vpa` assertions, port/interface
  claims) ride multi-parent correction DAGs keyed by an identity anchor. Tips
  are never ranked by `recorded_at`, authority, record id, filename, or append
  order. Competing tips surface as `conflicted`; the revision remains valid.
- **F1.5** Every evidence-bearing model claim is subject to the ES-001 uniform
  evidence-reference closure rule: any `model_record` evidence arm must name a
  member of the same collection, or the collection fails load/append/replay
  with `MODEL_REFERENCE_INVALID`.

### 1.2 The accepted evidence pipeline and its facades

- **F2.1** The evidence path is exactly:
  `data_sources` → `temporal_state` → `model_state` →
  `observation_compatibility` → `semantic_compatibility` →
  (`constraint_evaluation`, `behavior_evaluation`).
  Each layer composes the layer below it and carries its result **verbatim and
  exactly once**.
- **F2.2** An **observation** is a `TemporalOccurrence`: a source-attributed,
  time-bound payload (`value_json`, `source_time`, `received_at`,
  `payload_checksum`, `raw_record_id`, `attempt_id`). The projection is
  rebuildable and is never a claim about actual system state.
- **F2.3** Binding resolution runs at each occurrence's **own `received_at`**,
  never at query `as_of`. Binding applicability is interval-gated
  (`AppliesScope`); membership is the accepted `identity_binding.resolver.membership`
  helper.
- **F2.4** VS-001 assesses value-shape compatibility (JSON boolean/number/
  string/null/array/object) against a per-variable `VariableValueSpecification`.
  ES-001 composes VS with per-dimension model semantics (`vsm`) and
  source-property interpretation (`spi`). Neither performs any numeric
  comparison of `value_json`.
- **F2.5** CN-001 is the only accepted place where an observed value is
  numerically compared to a declared predicate. Its verdict vocabulary is
  exactly `{satisfied, violated, not_evaluated}`. BH-001 compares two observed
  values for exact numeric equality, also evidence-gated, and returns
  `{equal, different, not_executed}`.
- **F2.6** Staleness is disclosed as `staleness_seconds =
  (as_of − occurrence.received_at).total_seconds()` inside
  `LatestObservedState`/`BoundLatestObserved`/`CandidateObservation`. It is a
  derived disclosure, never a gate, never a verdict. BH-001 explicitly states:
  "Staleness remains disclosed through accepted lower-layer results and does
  not silently change mathematical equality."

### 1.3 The constraint predicate vocabulary is already sufficient

This is the single most consequential finding for ST-001.

The accepted CN-001 predicate union (`backend/model_kernel/contracts.py:497–527`)
is:

```text
ExactNumericLowerBound  →  lower: NumericBoundary(value, inclusion)
ExactNumericUpperBound  →  upper: NumericBoundary(value, inclusion)
ExactNumericInterval    →  lower: NumericBoundary, upper: NumericBoundary
```

`NumericBoundary.value` is the strict `CanonicalDecimal` grammar
(backend/model_kernel/contracts.py, §4.1 of the CN-001 spec). This union covers

- one-sided "x is at least/at most …" classes,
- two-sided "x is in (a, b)" classes (closed, open, half-open),
- singletons (interval with equal inclusive endpoints),

with explicit inclusivity. `CanonicalObservedDecimal` and the public parser
`parse_observed_decimal()` in `backend/constraint_evaluation/decimal.py`
already handle admission, exponent safety, and canonical equality without
floats or ambient context. **Nothing in ST-001 requires a new condition
language.**

### 1.4 Explicit lifecycle disclosure dimensions the proposal must reuse

The accepted BH-001 vocabulary (§17 of the BH-001 spec) separates:

- registration presence (`not_registered` / `registered`),
- declaration lifecycle (`not_declared` / `declared` / `conflicted` /
  `inactive`),
- DAG health (`healthy` / `conflicted` / `inactive` / `not_applicable`),
- agreement findings (corroborating roots vs same-root forks vs effective-body
  disagreement),

from the evaluator's execution vocabulary (`executed` / `not_executed`) and
computed relation (`equal` / `different`). ST-001 must reproduce this
separation. In particular the word `active`/`inactive` today describes the
**lifecycle of a model declaration**, never the physical system. Any ST-001
vocabulary that reuses `active` to mean "the system is in this state" creates
an immediate collision.

### 1.5 What is demonstrably absent today

- No `state`, `StateFamily`, `state_space`, `classification`, `classifier`,
  or transition module exists anywhere in `backend/`. Verified by grep.
- CN evaluation is **per (constraint, candidate)** and reports one verdict per
  candidate. It has no cross-candidate aggregation, ranking, or "current state"
  rollup. VM-001 explicitly states there is **no aggregate value field and no
  attachment rollup anywhere**.
- Multi-variable behavior evaluation exists only under BH-001's
  `same_acquisition_cohort` gate. There is no accepted mechanism for combining
  asynchronously-observed variables into one claim. ST-001 must not silently
  widen this.

### 1.6 The authoritative reconstruction boundary and the authenticity
### limitation

BH-001 §19 fixes the accepted reconstruction discipline:

- Every public result carries complete `ModelQueryMaterial` (BH) or a full
  `ModelRevision` plus carried lower-layer results (CN/VS/ES). Validation is
  store-independent and reconstructs all nested instances from serialized
  fields. `model_construct`, `model_copy`, mismatched model/binding/
  interpretation revisions, mixed cutoffs, and stale content-derived ids are
  rejected.
- BH-001 §23.6 and ADR-0015 line 141 fix an **accepted limitation**: BH
  validation proves carried-material coherence **and does not independently
  authenticate raw source content**. `payload_checksum` is not authentication;
  content-bound occurrence authentication is "separately owner-gated future
  work."

Any ST-001 classification that claims "the system is in state S" inherits
exactly this limitation. It can never, at ST-001 scope, prove that an
admitted numeric evidence was itself authentic at the raw byte level.

### 1.7 Current ledger content available for a bounded demonstration

The 32-record committed model contains:

- exactly two registered variables,
- one `crg_`/`vcn_` constraint pair (upper bound 80 on hotend temperature),
- one `brg_`/`bhd_` behavior pair (exact numeric equality),
- ports, interfaces, VPA, and ES-001 `vsm_`/VN tokens.

The BH-001 evaluator is committed as `not_executed` for that behavior (a
deliberate seam exception). CN-001's fixture is executable: `60.4` against an
upper bound of `80` yields `satisfied`. **There is no second variable with
both a committed binding, a value specification, and semantic declarations.**
This hard-shapes what an honest ST-001 demo can show.

### 1.8 Consequences that must shape the design

1. State identity must follow the accepted opaque-anchor + permanent
   registration + correctable declaration DAG pattern. Anything else
   contradicts F1.1–F1.4.
2. State **conditions** must reuse `ConstraintPredicate` (F1.3). Inventing a
   parallel predicate language duplicates CN and creates semantic drift.
   The clean alternative is *reference*, not restatement.
3. C`lassification must not collapse into a CN verdict. CN is "does this value
   satisfy this predicate on this variable"; classification is "of the
   explicitly declared states that target this subject, which matched this
   observation set under the gate?" — a different claim, distinct vocabulary.
4. Multi-variable classification inherits BH-001's cohort discipline
   (F2.1, F1.5) or explicitly refuses.
5. Staleness is carried, never thresholds (F2.6).
6. Authoritative reconstruction must be carried-material-only and must restate
   the raw-authenticity limitation (F1.6).

---

## 2. The Precise Definition of State

This is the section most likely to be wrong if rushed, so it is stated
operationally and then ontologically.

### 2.1 Operational definition (normative)

A **state** in ST-001 is:

> An explicitly declared, evidence-bearing, opaque model identity that names a
> static membership criterion over one specific modeled subject (a registered
> variable, in this slice). The criterion is expressed by **reference to
> existing correctable model knowledge**, not by embedding a fresh predicate
> language. Classification is the separate, read-only, per-observation,
> evidence-gated answer to the question "did this admitted observation satisfy
> this state's referenced criterion at classification time?"

The words are load-bearing:

- **Explicitly declared** — state exists only because an authority wrote a
  `StateDeclaration` (see §6). Nothing is inferred from values, names,
  topology, constraints, behaviors, or shared ownership.
- **Opaque model identity** — a `StateAnchor` (`sta_`) that carries no
  subject, no criterion, no severity, and no role field.
- **Static membership criterion** — no duration, no hysteresis, no rate of
  change, no persistence requirement, no temporal qualifier. A state is a
  pointwise predicate reference, always.
- **One specific modeled subject** — v1 = one `var_` anchor. Entities,
  subsystems, systems, and state families are deliberately excluded (see §3).
- **By reference** — the state record names a constraint anchor (`con_`) whose
  declaration lineage carries the predicate. The state record embeds no
  boundary digits of its own.
- **Static vs dynamic** — `Static` is the discriminator; it pins the absence
  of time operators, not a claim about the real world being static.

This definition deliberately rejects three ontological ambitions:

1. **States-as-kinds** (a state would be a type of variable, entity, or
   subsystem). Rejected: kinds are not supported by any accepted record kind,
   and introducing them in ST-001 welds a domain ontology into the kernel.
2. **States-as-views** (a state is an aggregated projection over multiple
   variables). Rejected for v1: no multi-variable composition exists below ST;
   accepting it here would secretly implement ST-002 temporal alignment.
3. **States-as-FSM-nodes** (states are nodes in a graph with edges). Rejected:
   from/to identity is explicitly excluded by the owner direction.

### 2.2 Answers to the challenger questions (applied)

The fixed owner direction listed twenty questions. Each is answered here, in
order. Where two options were left to ST-002 they are named explicitly.

1. **Ontological, operational, or predicate label?** Operationally a
   **referenced-predicate wrapper identity**. Ontologically the state is the
   *named region* in the variable's declared value space; the name is the
   `sta_` anchor and it has no independent semantics. It is not merely a
   predicate label because it carries authorship, evidence, and revision
   lineage.
2. **Belongs to entity, variable, subsystem, system, or state family?** In
   ST-001 it belongs to **exactly one registered variable** (the subject). Not
   an entity, subsystem, or system. There is no state family in v1.
3. **Can states overlap?** Yes. Two distinct `sta_` anchors over the same
   variable may reference predicates whose intervals overlap (e.g. `x < 90`
   and `60 < x < 85`). Both may match the same observation. Overlap does not
   make either false, does not make them equal, and creates no conflict in
   the lifecycle DAG.
4. **Can no state match?** Yes, and this is a first-class outcome. Every
   registered state that targets the variable is evaluated independently; the
   classification result carries zero matched entries honestly. There is no
   fallback state, no "unknown state" synthesized token, and no
   catch-all.
5. **What evidence would justify mutual exclusivity or exhaustiveness?** None
   accepted today. No record kind expresses it. ST-001 therefore never claims
   them. If they become needed, they arrive as an owner-gated `StateFamily`
   and a separate exclusivity record kind in ST-002+, with its own evidence
   and its own honesty vocabulary. No current fixture supports them, so
   nothing they say can be demonstrated.
6. **Would a `StateFamily` create a false FSM assumption?** Yes. Any primitive
   that groups states invites a default reading of "at most one of these is
   active at a time", which is an FSM claim. ST-001 excludes the primitive
   entirely to prevent that reading from becoming load-bearing. See §5.
7. **Would referencing CN constraints make state identity dependent on
   correctable constraint identity?** No — state identity is the `sta_`
   registration (permanent). The referenced constraint anchor is a separate
   identity with its own lineage. When the constraint lineage changes (its
   tips supersede, converge, or become conflicted), the state record is
   untouched; what changes is only which predicate the classifier admits.
   This separation mirrors exactly how BH-001's declaration references
   variable anchors without owning them.
8. **Does using direct predicates duplicate CN and create semantic drift?**
   Yes — and it is the rejected alternative (see §4). Duplicating the
   `CanonicalDecimal` grammar, the inclusivity enum, and the interval
   validation inside ST records would silently create two sources of truth
   for "what is a bound". Referencing `con_` reuses CN's authority, evidence,
   lifecycle, and honest vocabulary.
9. **Can numeric-only CN predicates support a credible first state slice?**
   Yes. The existing fixture already demonstrates an executable constraint
   evaluation over the same variable the demo state will target. The slice
   needs no string, boolean, or enumerated state. Non-numeric states are
   owner-gated future work.
10. **Should ST-001 be deliberately restricted to constraint-referenced
    numeric classification?** Yes. That is the recommended v1 (see §4, §6).
11. **How classify multi-variable state from asynchronously observed values
    without claiming simultaneity?** You cannot, and ST-001 does not try.
    v1 classification is strictly single-subject. Multi-variable composite
    state is explicitly deferred (§14), where the BH cohort gate or a new
    owner-approved temporal-alignment rule will apply.
12. **Is same-acquisition-cohort admission too strict, or independent-as-of
    admission too weak?** For v1 neither applies, because there is only one
    observation. The deeper question is deferred: when multi-variable state
    arrives, ST-002 must choose. BH chose strictness. A later ST slice may
    choose a bounded `as_of` window but must name the honesty cost (the
    result stops being pointwise).
13. **Can classification use the current semantic facade without bypassing
    evidence selection?** Yes, by **composing** `SemanticCompatibilityQueries`
    exactly once per subject per candidate, the accepted VS/ES seam. ST must
    not construct new VS or ES calls outside that facade, must not bypass
    `SourceSelector`-driven candidate discovery, and must not re-read stores.
14. **Does the current temporal history API matter for classification, or
    only for ST-002?** Only for ST-002. ST-001 classification is
    latest-per-locator/candidate at an explicit `as_of`, the same temporal
    basis as every other accepted query. History, windows, and persistence
    are the transition problem.
15. **How should staleness alter disclosure without silently changing truth?**
    By carrying `staleness_seconds` and `evidence_quality` verbatim from the
    candidate, adding one derived disclosure field on the ST result
    (`evidence_staleness_class`, see §9), and **never** letting staleness
    change the classification outcome. A stale match stays a match with a
    stale disclosure.
16. **Can a classification result be authoritatively reconstructed from
    carried material?** Yes, if the result carries (a) the complete selected
    model membership for the subject variable and the referenced constraint
    lineage, (b) the carried ES result once, (c) the kernel-side declaration
    lifecycle disclosure, and (d) derived fields recomputed by an outer
    store-independent validator. See §12.
17. **How does the accepted raw-content authenticity limitation affect state
    claims?** Classification never claims raw-source authenticity. The result
    states only: *given this admitted observation and this selected revision,
    these registered states' referenced predicates matched / did not match /
    were not evaluated*. A fully coherent lower-evidence mutation accepted by
    lower public contracts remains outside ST's store-independent boundary,
    identical to BH-001 §23.6.
18. **Could state matching accidentally become a diagnosis, health
    assessment, or operating-normality verdict?** Only if vocabulary leaks.
    ST-001 forbids `health`, `fault`, `normal`, `abnormal`, `alarm`,
    `severity`, `recommended`, `diagnosis`, `operating_normality`, and
    `state_change` anywhere in its public surface. Matched does **not** mean
    safe. Non-match does **not** mean faulty or wrong.
19. **What terminology prevents declaration "active/inactive" from being
    confused with system state?** The public ST contract never exposes the
    word `active`. Lifecycle statuses are `registered`/`not_registered` on the
    identity axis and `declared`/`conflicted`/`inactive`/`not_declared` on
    the assertion axis — exactly the accepted BH vocabulary. The verdict
    vocabulary is `matched`/`not_matched`/`not_evaluated` — never
    `satisfied` (CN) and never `on`/`off` (FSM).
20. **What minimal demonstration provides real architectural evidence without
    fabricating printer operating states?** One synthetic state targeting the
    existing hotend-temperature variable by referencing the accepted CN
    constraint anchor (`con_4b768cf843f5474cb5e564e31d239a59`), evaluated
    honestly against the committed `60.4` observation, and reported as
    `matched` with full staleness disclosure. No claim about "printing",
    "hot", "safe", or any machine behavior.

---

## 3. Architectural Invariants

These are non-negotiable. Every public contract, every validator, and every
fixture must preserve them.

**Inv-1 (Identity opacity).** A `StateAnchor` is a pure identity. Its
embedded namespace, display name, and role name are carried verbatim into
results but never participate in matching, classification, or evidence
selection. Renaming a state does not create a new identity.

**Inv-2 (Registration permanence).** `StateRegistration` pins the
`(StateAnchor, variable_anchor_id)` association. It is permanent, evidence-
bearing, has no lifecycle, no correction path, no withdrawal, and no
supersession field. Two distinct registrations for one anchor invalidate the
revision (`MODEL_DUPLICATE_REGISTRATION`).

**Inv-3 (Declaration-by-reference).** A `StateDeclaration` embeds no
predicate. Its only criterion fields are the `constraint_anchor_id` reference
and the rule-family discriminator (`literal` v1: `"numeric_membership_via_constraint"`).
It carries evidence and `supersedes`, exactly like `VariableConstraintDeclaration`.
State lineage and constraint lineage are independent DAGs; neither may cite
the other as parent.

**Inv-4 (No FSM fields).** No record, query, result, or validator may carry
`from`, `to`, `trigger`, `action`, `event`, `guard`, `next_state`,
`previous_state`, `entry_condition`, `exit_condition`, or their synonyms. AST
isolation tests forbid them.

**Inv-5 (Single-subject v1).** Every state registration targets exactly one
variable. Composite/entity-level/multi-variable state records do not exist in
v1. The record constructor and collection validator reject tuple-of-variables
forms.

**Inv-6 (Composition-only evaluation).** Classification is a read-only facade
(`backend/state_classification/`) that injects only accepted query facades
(`SemanticCompatibilityQueries`, per the ES seam; CN's public
`parse_observed_decimal` for numeric admission, exactly as BH does). It
constructs no store, opens no file, owns no cache, and issues no writes.

**Inv-7 (Carry-once, no rollup).** Classification results carry the ES result
for the subject exactly once and the kernel declaration-lifecycle result
exactly once. Per-candidate rows use strict indices into the ES candidates.
There is no aggregate "the state of the system" field, no count of matched
states, no ranking, no winner.

**Inv-8 (Staleness is disclosure).** `staleness_seconds` and
`evidence_quality` are carried verbatim per candidate. The only derived field
is a coarse disclosure class (`evidence_staleness_class`), deterministic from
a small published threshold table over `staleness_seconds`. It never changes
a verdict; it is never an admission gate.

**Inv-9 (Honest vocabulary by construction).** The only verdict literals are
`matched`, `not_matched`, `not_evaluated`. The only lifecycle literals are
`registered` / `not_registered` (identity axis) and `declared` /
`not_declared` / `conflicted` / `inactive` (assertion axis). Nothing with
safety, health, fault, alarm, diagnostics, correction, or transition
connotation appears in any public contract, fixture prose, or demo statement.

**Inv-10 (Authoritative reconstruction).** Every public result is frozen,
extra-forbidden, revalidated from serialized field content at the outer
boundary, and carries enough material for a store-independent validator to
recompute every derived field from carried records. Raw-source authenticity
remains the accepted BH-001 limitation.

**Inv-11 (Failure isolation).** An unregistered state, a conflicted state
lineage, or a referenced-conflicted constraint never blocks classification
of other states on the same variable, other variables, or other candidates.
Each `(state, candidate)` row is independent.

---

## 4. Alternatives

### 4.1 Alternative A — Embed the predicate directly in the state record

A `StateDeclaration` would carry its own `ConstraintPredicate` body (bounds,
inclusion, canonical decimals). Evaluation would compare the observed value to
those stored bounds directly.

**Why it is rejected.** This duplicates CN exactly. It drags the
`CanonicalDecimal` grammar, the empty-predicate validation, the inclusivity
semantics, and the parser parity rules into a second module. It creates two
independent predicates that can silently diverge in meaning while both
claiming to be "the bounds for this variable". It defeats the entire point of
having CN be the authoritative numeric-meaning layer. It also blocks the
natural upgrade where a constraint is corrected once and every state that
references it sees the same corrected predicate.

### 4.2 Alternative B — State as a kind of constraint (inheritance)

Make `StateDeclaration` a subclass or variant of `VariableConstraintDeclaration`,
with `matched` = `satisfied`.

**Why it is rejected.** CN's verdict is a predicate verdict, not a named-state
verdict. The two questions are different: "does this value violate this
bound?" and "which of my named classes contains this value?" Squeezing the
second through the first forces the CN vocabulary to absorb classification
responsibilities (`matched`, `not_matched`, `no_state_match`, overlap
disclosure) and breaks CN's already-accepted honest-language contract (§11 of
CN-001). Inheritance also violates the accepted composition-over-inheritance
principle for kernel record kinds.

### 4.3 Alternative C — `StateFamily` as the primary primitive, states as
### members

Introduce a separate `fam_` anchor and a family record that groups states,
with exhaustiveness and mutual-exclusivity flags.

**Why it is rejected.** No repository fixture supports exclusivity or
exhaustiveness evidence; inventing the primitive to support two unsupported
flags is scaffolding. It also immediately invites the FSM reading the owner
direction forbids. It is the rejected branch (see §5).

### 4.4 Alternative D — Classification writes its own evidence records

The classifier would persist "on 2026-08-30T12:00:00Z state S matched"
records into a new ledger.

**Why it is rejected.** Persisting computed state is explicitly excluded by
the owner direction. It also breaks Inv-10 (results must be reconstructible
from carried material: a persisted computed record is a second source of
truth for what was decided).

### 4.5 Alternative E — Recommended: permanent `sta_` registration +
### correctable `std_` declaration-by-reference, read-only classifier

This is the recommended design. It is the only option that

- reuses CN's exact predicate truth,
- composes ES exactly once per candidate without bypassing evidence
  selection,
- separates declaration lifecycle from verdict,
- never suggests an FSM,
- and keeps every rejected alternative reachable later as an owner-gated
  change without migration pain.

---

## 5. Is a State-Family / State-Space Primitive Required?

**No. ST-001 v1 contains no `StateFamily` and no `StateSpace`.**

Reasoning:

- **Evidence absence.** No accepted record kind supports exclusivity or
  exhaustiveness claims. Introducing a primitive without supporting evidence
  is fabrication.
- **FSM risk.** Any grouping primitive becomes the natural hook for transition
  semantics. Removing it eliminates a whole class of accidental future scope
  creep; adding it does nothing v1 classification actually needs.
- **Ontology slide.** A family record would silently introduce a kind-of-kind.
  That is exactly the thin-kernel violation ADR-0007 D3 warns against.
- **Upgrade path.** If the owner later approves a `StateFamily`, it arrives
  as an owner-gated ST-002 record kind with its own evidence requirement, its
  own "this does not imply FSM" vocabulary, and an explicit non-claim that
  current v1 state records never acquire family membership retroactively.

Concretely: a state registered against the hotend temperature variable can
have its predicate corrected, can be superseded, and can overlap with another
state over the same variable — and **none of those things requires a family
container**. The family is not necessary for v1 and its absence is load-
bearing for honesty.

---

## 6. Recommended Identity Model and Record Sketches

### 6.1 Prefixes

Add exactly:

```text
sta_  StateAnchor
srg_  StateRegistration
std_  StateDeclaration
stw_  StateWithdrawal
```

No other prefix. `stw_` is present in v1 to preserve parity with BH/VP/Pt
correctable claim families (withdrawal is not supersession), but no committed
fixture uses it. `stw_` is uncitable in `ModelRecordEvidence`, mirroring
`rwd_`/`bhw_`.

### 6.2 `StateAnchor` (`backend/system_identity/anchors.py`)

```text
STATE_ANCHOR_ID_PATTERN = r"^sta_[0-9a-f]{32}$"

class StateAnchor(_Frozen):
    anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)
```

`ConfigDict(frozen=True, extra="forbid", revalidate_instances="always")` —
the newer anchor convention, same as `ConstraintAnchor` and `BehaviorAnchor`.

A public minter follows the BH minter discipline:

```python
def mint_state_anchor(*, namespace, display_name, role_name=None) -> StateAnchor
```

No persistence, no I/O, no authority assertion. `mint_state_anchor` is placed
in the same ordered sequence position discipline as the BH additions.

### 6.3 `StateRegistration` (`srg_`)

```text
class StateRegistration(_Frozen):
    record_kind: Literal["state_registration"] = "state_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^srg_[0-9a-f]{64}$")
    anchor: StateAnchor                       # embedded verbatim
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    evidence: NonEmptyCanonicalEvidenceTuple
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

Admission:

1. The embedded anchor must be a valid-state identity.
2. The target `variable_anchor_id` must name a registered variable in the same
   collection (`MODEL_REFERENCE_INVALID`).
3. **At most one registration per `sta_` anchor**
   (`MODEL_DUPLICATE_REGISTRATION`), agreeing embedded fields or divergent —
   the existing CN discipline.
4. Uniform evidence closure (`_check_model_record_evidence`).
5. Foreign evidence arms declared, never dereferenced.

No lifecycle, no correction, no supersession, no withdrawal.

### 6.4 `StateDeclaration` (`std_`)

```text
class StateDeclaration(_Frozen):
    record_kind: Literal["state_declaration"] = "state_declaration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^std_[0-9a-f]{64}$")
    state_anchor_id: str = Field(pattern=STATE_ANCHOR_ID_PATTERN)
    context: AssertionContext
    criterion: StateCriterion             # discriminated union
    evidence: NonEmptyCanonicalEvidenceTuple
    supersedes: CanonicalStateDeclarationIdTuple     # multi-parent, canonical sort
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

`StateCriterion`, v1, has exactly one arm. The discriminator makes later arms
explicitly owner-gated (v2 could add a direct numeric interval *only* if the
owner separately decides direct predicates are safe):

```python
class ConstraintReferenceCriterion(_Frozen):
    kind: Literal["numeric_membership_via_constraint"] = (
        "numeric_membership_via_constraint")
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)

StateCriterion = Annotated[
    Union[ConstraintReferenceCriterion],
    Field(discriminator="kind")]
```

A v1 declaration therefore names only: (state anchor, context, constraint
anchor, evidence, supersedes). No bounds, no decimals, no unit, no severity.
When the referenced constraint anchor's declaration lineage is superseded or
becomes conflicted, the state record's identity and content are untouched.

Admission rules:

1. `state_anchor_id` must name a registered state in the same collection
   (`MODEL_REFERENCE_INVALID`).
2. `criterion.constraint_anchor_id` must name a registered constraint in the
   same collection, and that registration's `variable_anchor_id` must equal
   the state registration's `variable_anchor_id`. (Reference closure across
   kinds, mirroring BRG→BHD lock equality.)
3. `context` is reconstructed from serialized content — never trusted by
   type alone.
4. Parents must all be `std_` records with the same `state_anchor_id` and
   same exact `context`. Cross-context supersession is
   `MODEL_STATE_LINEAGE_INVALID`. Cross-root convergence is rejected.
5. Acyclic three-colour walk, identical to BH.
6. Uniform evidence closure.

### 6.5 `StateWithdrawal` (`stw_`)

```text
class StateWithdrawal(_Frozen):
    record_kind: Literal["state_withdrawal"] = "state_withdrawal"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^stw_[0-9a-f]{64}$")
    withdraws: str = Field(pattern=r"^std_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

No evidence, no context, no parents, no outcome, no reason code, and uncitable
in `ModelRecordEvidence`. Targets one unsuperseded, unwithdrawn current `std_`
tip. The exact BH withdrawal target rules apply (unknown/non-tip/superseded/
already-withdrawn/duplicate rejected; successor plus withdrawal of the same
target in one membership rejected).

### 6.6 Lifecycle and replay

Per key `(state_anchor_id, exact AssertionContext)`:

- Zero roots → `not_declared`.
- At least one root, zero active tips → `inactive`.
- One healthy root → `declared` (and corroborating healthy roots with
  identical effective bodies are disclosed via agreement findings, exactly
  as BH).
- Any same-root fork or cross-root effective-body disagreement → `conflicted`.

Replay is membership-relative. An ancestor-only subset revives the predecessor.
The BH §9 table (registration × roots × active-tip state × effective bodies
→ conclusion) is reused verbatim. Withdrawal of all active tips makes the
root inactive; withdrawal never claims the declaration was false.

The effective-body projection for state corroboration is:

```text
state_anchor_id
context
criterion            # the discriminated StateCriterion body
```

Evidence, `supersedes`, authority, `recorded_at`, and `note` are always
excluded. Whole-record bytes and Pydantic equality are never used. Canonical
JSON serialization of the projection decides effective-body equality.

---

## 7. Kernel Ripple Surface

Adding two new record kinds touches the same twelve sites CN-001 lists
(§6 of the CN-001 design). For each:

1. `_PREFIX_BY_KIND` — `state_registration: "srg"`,
   `state_declaration: "std"`, `state_withdrawal: "stw"`.
2. `MODEL_RECORD_ID_PATTERN` — add `srg|std|stw`.
3. `ModelRecordEvidence.record_id` — add `srg|std` (and **not** `stw`).
4. `ModelRecord` union — three new members.
5. The record classes above.
6. `_FILENAME` regex — add `srg|std|stw` (distinct literal, as before).
7. Store bucket dispatch — three new buckets.
8. `LoadedModel` mappings:

   ```text
   state_registrations_by_anchor:    sta_ -> StateRegistration
   state_anchor_ids_by_variable:     var_ -> tuple[sta_, ...] sorted
   state_declarations:               std_ (id) -> StateDeclaration
   state_root_by_id:                 std_ -> std_ (root id)
   state_ancestry_by_id:             std_ -> tuple[std_, ...]
   state_superseded_by:              std_ -> tuple[std_, ...]
   current_state_tips_by_root:       root std_ -> tuple[std_, ...]
   state_withdrawals:                stw_ (id) -> StateWithdrawal
   state_withdrawn_by:               std_ -> tuple[stw_, ...]
   state_withdrawals_by_target:      std_ -> tuple[stw_, ...]
   ```
9. `validate_record_collection` — registration pass then declaration DAG pass
   then withdrawal target pass, in that order, reusing the accepted three-
   colour walker.
10. New `ModelQueries` methods (§8).
11. `__init__.py` imports and `__all__` — additive.
12. Evidence closure — `_check_model_record_evidence` for `srg_`/`std_`.

`_RECORD_ADAPTER`, `compute_revision_id`, and `_canonical_parents` need no
edits. **No existing record hash changes**, and historical memberships
(9/10/11/14/16/18/28/29/32) replay unchanged because prefix-filtered replay is
never a membership selector in the accepted architecture.

---

## 8. Kernel Query Surface (Read-Only)

Exactly four `ModelQueries` methods, mirroring the BH four-query shape:

```python
state(state_anchor_id) -> StateLookupResult
state_declaration(state_anchor_id, *, context) -> StateRuleResult
states_of_variable(variable_anchor_id, *, context) -> VariableStatesResult
state_assertion(record_id) -> StateAssertionDisclosureResult
```

The contracts:

```text
StateLookupStatus           = Literal["not_registered", "registered"]
StateDeclarationConclusion  = Literal["not_registered", "not_declared",
                                      "inactive", "declared", "conflicted"]
StateRuleLineageSummary     = Literal["not_applicable", "healthy",
                                      "conflicted", "inactive"]
StateAgreementFinding       = Literal["one_healthy_root",
                                      "corroborating_healthy_roots",
                                      "same_root_conflict",
                                      "cross_root_effective_body_disagreement",
                                      "inactive_roots_present"]
VariableStatesStatus        = Literal["variable_not_registered", "registered"]
StateAssertionLookupStatus  = Literal["not_found", "found"]
```

`StateRuleResult` carries: material (complete selected membership once),
state anchor id, context echo, conclusion, lineage summary, agreement
findings (tuple, possibly multi-arm), registration index, roots,
effective-body groups, current tip indices. The validator recomputes every
derived row from material, rejecting forged tips, forged activity, forged
effective-body equality, forged conclusions, and forged index alignment.

`state_assertion(record_id)` accepts valid `srg_`, `std_`, `stw_` ids:

- found `srg_` → permanent-shaped disclosure (no lifecycle fields).
- found `std_` → activity, containing root health, aggregate subject
  conclusion, direct successors, withdrawals, agreement findings.
- found `stw_` → event-shaped disclosure (no lifecycle fields).
- valid-shaped absent → `not_found` with optional fields None/empty.
- malformed or non-ST id → typed input error.

There are no aliases, no port/family scoping, and no overloads.

---

## 9. The Classifier: `backend/state_classification/`

### 9.1 Import direction and composition

```text
backend.system_identity    ─→ backend.model_kernel ──────────┐
                                              backend.model_state
                                              backend.observation_compatibility
                                              backend.semantic_compatibility ─┐
                                                                             ▼
                                              backend.state_classification   (NEW)
                                                                         │
                                              public CN parser only ─────┘
```

- `state_classification` imports only: `system_identity`, `model_kernel`,
  `model_state`, `observation_compatibility`, `semantic_compatibility`, the
  public `parse_observed_decimal` from `constraint_evaluation`, Pydantic,
  and the standard library.
- It never imports `data_sources`, `identity_binding` (its types travel
  inside carried objects), `temporal_state` runtime code, `structural_evidence`,
  or any store module.
- Reverse rules: no accepted module imports `state_classification`. Kernel
  AST isolation is widened to forbid it in both directions.

This exactly matches the BH composition shape: the facade injects one
`SemanticCompatibilityQueries` instance and constructs `ModelQueries` per
call from the exact `LoadedModel` the injected stack already uses, so a
revision mismatch between membership/lineage and evidence is
unconstructible.

### 9.2 Query surface

```python
class StateClassificationQueries:
    def __init__(self, semantic: SemanticCompatibilityQueries) -> None: ...

    def classifications_of_variable(self, variable_anchor_id: str, *,
                                    as_of: datetime,
                                    entity_anchor_id: str | None = None,
                                    source: SourceSelector | None = None,
                                    context: AssertionContext) \
        -> VariableClassificationResult: ...
```

`source: SourceSelector | None` follows the VM/ES seam: an explicit selector
produces an `explicit_selector` discovery, never bypassing the pipeline.
`context` is required — classification is always exact-context.

Exact-anchor lookup is deliberately **not** a separate public method in v1;
an owner-approved addition later can add `classification(state_anchor_id, …)`.
Keeping v1 to one compositional shape reduces the surface where scope can
creep.

### 9.3 Admission gate order

The classifier performs, in this exact order, for each candidate in the
carried ES result:

1. State identity check: subject variable registered →
   `state_registration_status` disclosed per state. Any
   `state_not_registered` refuses that state alone.
2. Lifecycle check: the state's exact-context declaration lineage is
   queried through the kernel (`state_declaration`). Conclusions
   `not_declared` / `inactive` / `conflicted` → per-state refusal, never a
   global failure.
3. Criterion closure check: the referenced constraint anchor must be
   registered (otherwise `state_criterion_unavailable`). Its declaration
   must, on its own lineage, resolve `declared`; `not_declared` /
   `conflicted` → per-state refusal (`state_criterion_not_resolvable`).
4. Evidence admission: the accepted CN gate clauses 3–15 (observation present,
   attached, evidence assessable, value-shape OK, `model_value_shape` numeric,
   numeric present, ES `declared_semantics_compatible` present where required,
   lock equality for the referenced constraint's `expected_semantics`,
   numeric parsing inside CN bounds) → per-state refusal vocabulary.
5. Comparison: the admitted `CanonicalObservedDecimal` (from the public CN
   parser on the candidate's `value_json`) satisfies the referenced CN
   predicate → `matched`; otherwise → `not_matched`.

Crucially:

- Cohort admission never appears in v1 because only one candidate enters one
  state's comparison. The phrase `same_acquisition_cohort` does not appear
  anywhere in ST-001 contracts.
- A state with `state_conflicted` classification is **still returned as a
  row**, with verdict `not_evaluated` and the conflicted lineage disclosed in
  the carried kernel material. Never suppressed.
- Refusal reasons are an independent tuple per row, exactly in the BH pattern.
  A refusal reason is not a synonym for `not_matched`.

### 9.4 Result contracts

```text
StateVerdict                  = Literal["matched", "not_matched",
                                        "not_evaluated"]
StateClassificationStatus     = Literal["declared", "not_declared", "inactive",
                                        "conflicted", "not_registered"]
StateRefusalReason            = Literal[
    "state_not_registered",              # anchor not in selected revision
    "state_not_declared",                # exact-context declaration lineage empty
    "state_inactive",                    # roots exist, no active tips
    "state_conflicted",                  # fork / body disagreement
    "state_criterion_unavailable",       # referenced constraint not registered
    "state_criterion_not_resolvable",    # constraint lineage not cleanly declared
    "observation_absent",
    "observation_not_attached",
    "evidence_not_assessable",
    "value_shape_not_evaluated",
    "model_value_shape_not_numeric",
    "value_shape_not_satisfied",
    "numeric_value_absent",
    "declared_semantics_not_compatible",
    "constraint_quantity_kind_mismatch",
    "constraint_observation_role_mismatch",
    "constraint_unit_identity_mismatch",
    "numeric_value_out_of_bounds",
]
EvidenceStalenessClass        = Literal["fresh", "aging", "stale",
                                        "undetermined"]
```

The state-specific reasons (`state_*`) are ST's own; the rest are carried
from CN's vocabulary verbatim (same spelling, same meaning). ST **does not**
re-export CN; it uses the strings as data within its own refusal tuple. This
avoids the cross-layer vocabulary import that BH §18.0 carefully rejected for
the parser while still refusing to coin new names for identical facts.

```text
StateClassificationRow (_Frozen, per (state, candidate)):
  state_index                 # strict nonneg int into carried state list
  semantic_candidate_index    # strict nonneg int into carried ES candidates
  state_anchor_id
  state_lifecycle             # StateClassificationStatus
  verdict                     # StateVerdict
  refusal_reasons             # ordered tuple[StateRefusalReason, ...]
  canonical_decimal           # CanonicalObservedDecimal | None
  evidence_staleness_class    # EvidenceStalenessClass
```

```text
VariableClassificationResult (_Frozen):
  variable_anchor_id
  as_of                       # UtcDatetime, == ES as_of
  ruleset_version             # Literal["st001.1"]
  entity_anchor_id            # echo or None
  source_selector             # echo or None
  context                     # exact AssertionContext
  material                    # ModelQueryMaterial, complete, once
  semantic_result             # VariableSemanticCompatibilityResult, once
  state_results               # tuple[StateRuleResult, ...] — per-state kernel
                              #  disclosure (only for states present)
  classifications             # tuple[StateClassificationRow, ...]
  evaluated                   # bool — any row with verdict != "not_evaluated"
  matched_state_anchor_ids    # tuple of sta_ ids, sorted, derived
```

Cross-field invariants (validator-pinned):

1. `material.revision == semantic_result.semantics_result.revision == each
   state_results[i].material.revision` (all one selected model revision).
2. `state_results[i].material is material` (identity reuse, no second copy).
3. `state_results[i].conclusion` exactly equals the corresponding row's
   `state_lifecycle` when a row exists.
4. `classifications[i].semantic_candidate_index` is strict, in-range into
   `semantic_result.candidates`, and unique per `(state_index)` row.
5. `canonical_decimal` is present exactly when `verdict == "matched"` or
   `"not_matched"` with numeric admission.
6. `matched_state_anchor_ids` equals the sorted set of `state_anchor_id` over
   rows with `verdict == "matched"`, recomputed, never trusted.
7. `evidence_staleness_class` derives only from the candidate's
   `staleness_seconds`, through the published threshold table, and never
   modifies a verdict.
8. `evaluated` ⇔ at least one row has verdict in {`matched`, `not_matched`}.
9. A `not_evaluated` row carries a non-empty `refusal_reasons`; a matched or
   not-matched row carries an empty refusal tuple.

**There is precisely one aggregate-ish field**, `matched_state_anchor_ids`,
and it is a *derived convenience set*, not a rollup verdict. It cannot
support the sentence "the system is in state S", only the sentence "the set
of states that matched this observation set is exactly these".

### 9.5 Staleness disclosure class

Published, deterministic, and the only derived policy in v1:

| Bound (seconds since `received_at`) | Class |
|---|---|
| `staleness_seconds < 300` | `fresh` |
| `300 ≤ staleness_seconds < 3600` | `aging` |
| `staleness_seconds ≥ 3600` | `stale` |
| observation absent / cutoff not evaluable | `undetermined` |

The thresholds are constants in `state_classification/derivation.py`,
governed by the same "no time-axis truth" doctrine as BH: staleness never
gates, never thresholds, and the class **never** changes a verdict. The class
exists so UI and downstream consumers do not silently interpret a stale match
as current truth. The numbers 300/3600 are deliberately arbitrary and
flagged for owner review in §19.

---

## 10. Relationship to CN Constraints

- The constraint is the **subject's numeric specification**. The state is a
  **named membership claim** that references that constraint. Authority over
  the predicate stays with CN; the state layer adds identity, evidence, and
  context, not arithmetic.
- Constraint satisfaction (`satisfied`/`violated` on `vcn_`) is **never**
  re-expressed as a state verdict. `matched`/`not_matched` is a distinct,
  weaker claim: "this admitted observation falls inside this declared
  region" — without implying violation, fault, or compliance significance of
  not matching.
- The CN evaluator (`backend/constraint_evaluation/`) is **not invoked** by
  the ST classifier. ST composes the ES stack, runs its own gate-order over
  the referenced predicate stored in the kernel's `vcn_` records, and calls
  only the public CN parser for numeric admission. This is precisely the
  import discipline BH uses.
- A corrected `vcn_` (new bounds, new inclusion, same anchor) updates the
  criterion meaning without touching the `sta_`/`std_` records. That is
  exactly the separation BH-001 demanded for its `participant_semantics`
  relative to current VSP/VSM (see BH §12, "the model store does not require
  current VSP or VSM records"), mirrored here for constraints.

---

## 11. Temporal and Cohort Policy

- **`as_of`** remains the ingestion-receipt cutoff. It selects evidence, never
  model membership. A naive `as_of` is typed-refused before any evidence
  query (the accepted VM boundary).
- **Resolution instants** are the per-occurrence `received_at` inside carried
  ES candidates. ST never invents a new resolution instant.
- **Cohort.** The v1 classifier does not combine observations. The BH cohort
  key exists as precedent when multi-variable state arrives; ST-001 does not
  use it, does not reference it, and does not preempt its choice.
- **`Staleness`.** Carried per candidate, disclosed via
  `evidence_staleness_class`, never a gate.
- **No history.** The classifier never calls `TemporalQueries.history`,
  `change_history`, or `attempt_coverage`. History and persistence are
  ST-002's problem.

---

## 12. Authoritative Reconstruction Boundary

Following BH §19 exactly:

Public-result validators must:

- Reconstruct every carried `ModelRecord` and verify its content-derived id.
- Rebuild `LoadedModel` through the accepted in-memory collection validator
  on `material.records`.
- Re-run `state_declaration` per state, recomputing roots, ancestry,
  successors, withdrawals, tips, effective-body projections, groups,
  findings, conclusion, lineage summary. Reject reordered, missing, extra,
  or substituted rows.
- Reconstruct the carried ES result by serializing its nested instances and
  revalidating from field content (the accepted mechanism).
- Require `state_results[i].material.revision == semantic_result.
  semantics_result.revision` and `semantic_result.value_compatibility.
  specification_result.revision` (all one revision).
- Recompute every per-row verdict, refusal, canonical decimal, and staleness
  class. Reject forged values.
- Reject `model_construct` / `model_copy` forgeries at every nesting depth.
- Access no store, filesystem, or network; issue no writes; capture no
  timestamps of its own.

**Limitation (verbatim restatement of BH §23.6):** ST validation proves
carried-material coherence, not raw-source authenticity. A fully coherent
lower-evidence mutation accepted by lower public contracts lies outside ST's
store-independent detection boundary. `payload_checksum` does not
authenticate the uncaptured payload. Content-bound occurrence authentication
remains separately owner-gated future work, which ST-001 neither performs nor
claims.

---

## 13. Import-Direction Analysis

Forbidden reverse edges, all AST-enforced:

- `model_kernel` must not import `model_state`, `observation_compatibility`,
  `semantic_compatibility`, `constraint_evaluation`, `behavior_evaluation`,
  `state_classification`, or any store module.
- All lower facades must not import `state_classification`.
- `state_classification` must not construct `ModelStore`, `BindingStore`,
  `TemporalStore`, or `InterpretationStore`; must not contain path literals;
  must not dynamically import; must not touch private attributes of injected
  objects.
- `state_classification` must not persist any result (Inv-10).

The existing kernel AST-isolation tests gain forbid-list entries for the new
package. `system_identity` additions (the anchor) are additive and do not
change any existing export ordering beyond `mint_state_anchor` in its pinned
position.

---

## 14. Explicit Exclusions (v1)

These belong to ST-002 or later. Nothing in the v1 contracts, records,
queries, or fixtures supports them.

- State transitions, from/to identity, transition identity anchors.
- Triggers, actions, guards, events, entry/exit conditions.
- Causal inference of any kind.
- Control, command issuance, or hardware interaction.
- State-machine execution and persistence of computed state.
- Entity-level, subsystem-level, or system-level aggregated state.
- Multi-variable composite states.
- `StateFamily` / `StateSpace` primitives, exhaustiveness, mutual
  exclusivity.
- Non-numeric state criteria (string, boolean, enumerated, semantic-token
  criteria).
- History, persistence, dwell time, hysteresis, rate-of-change, debounce,
  windowing, sampling.
- Severity, health, fault, alarm, operating-normality verdicts, recommended
  actions, diagnosis.
- FSM nodes, FSM edges, FSM fields of any name.
- Cohort admission across observations (see §11).
- Any new ledger, store, projection, cache, or persisted classification
  result.
- Any new public minter outside the one `mint_state_anchor`.

---

## 15. Hostile Acceptance Matrix

Each row pins observable behavior, not implementation. Every row is
red-first tested before its implementation commit.

### 15.1 Identity and records

| Row | Requirement |
|---|---|
| A1 | `sta_`/`srg_`/`std_`/`stw_` grammars: lowercase only, exact length, hex only, malformed at any position rejected typed. |
| A2 | Anchor frozen, extra-forbidden, full-instance revalidation; forged nested `StateAnchor` rejected on outer revalidation. |
| A3 | `mint_state_anchor` produces UUID4-hex; no I/O; preserves supplied fields; rejects invalid display/role names. |
| A4 | `srg_` requires the target `var_` registered in the same collection; orphan target → `MODEL_REFERENCE_INVALID`. |
| A5 | Second `srg_` for one anchor → `MODEL_DUPLICATE_REGISTRATION`, agreeing embedded fields included. |
| A6 | `std_` parent closure: parent must exist, must be `std_`, same anchor, same exact context. Wrong-kind parent → typed refusal. |
| A7 | `std_` DAG acyclicity via three-colour walk; cycle → `MODEL_STATE_LINEAGE_INVALID`. |
| A8 | `std_` evidence closure via `_check_model_record_evidence`; dangling `model_record` evidence → `MODEL_REFERENCE_INVALID`. |
| A9 | `stw_` may not cite a `std_` in `ModelRecordEvidence` (uncitable kind). |
| A10 | Content-derived ids: mutating any byte changes the id; a forged record with a stale id fails load. |
| A11 | Filename regex: `srg|std|stw` arms present; wrong-bucket filename rejected. |
| A12 | No record carries `from`/`to`/`trigger`/`action`/`next_state`/`previous_state`/`severity`/`health`/`alarm`/`normal` — asserted by path-scoped sweep over the ST diff. |

### 15.2 Kernel queries

| Row | Requirement |
|---|---|
| B1 | `state()` on unregistered anchor returns `not_registered` with no registration, no indices, canonical empty tuples. |
| B2 | `state_declaration()` on registered state with no exact-context declaration returns `not_declared`. |
| B3 | Same-root fork → `conflicted` with both tips and the fork structure disclosed. |
| B4 | Two independent healthy roots with identical effective bodies → `declared` with `corroborating_healthy_roots`. |
| B5 | Two roots with differing effective bodies → `conflicted`, each tip disclosed, never ranked. |
| B6 | All tips withdrawn → `inactive`, root present and disclosed. |
| B7 | Partial convergence → still `conflicted`. Full convergence → one tip, `declared`. |
| B8 | Replay without later successor revives predecessor as current. |
| B9 | Replay without later withdrawal revives target. |
| B10 | No tip ordering by `recorded_at`, authority, record id, file order, or append order. |
| B11 | `states_of_variable()` on unregistered variable → `variable_not_registered`. |
| B12 | `states_of_variable()` on registered variable with no states → `variable_not_registered` is `registered` with empty entries. |
| B13 | Reverse discovery in canonical state-anchor order, never inferred from names or owners. |
| B14 | `state_assertion()` on a found `srg_` discloses permanent shape; on a found `std_` discloses activity + root health + aggregate conclusion as separate fields; on a found `stw_` discloses event shape; on valid-shaped absent id returns `not_found`; malformed id is typed misuse. |
| B15 | Record indices in results point to the correct union arm. |

### 15.3 Classifier

| Row | Requirement |
|---|---|
| C1 | The ES facade is invoked exactly once per query, regardless of how many states exist. No extra VS/ES calls. |
| C2 | The candidate count in the carried ES result equals the candidate count in every row's `semantic_candidate_index` coverage. No candidate is silenced. |
| C3 | Each state produces rows only for admitted candidates — never for nonexistent ones. |
| C4 | `state_conflicted` rows carry the conflicted kernel disclosure verbatim in `state_results`; verdict is `not_evaluated`, refusals contain `state_conflicted`. |
| C5 | `state_not_declared` / `state_inactive` / `state_not_registered` are per-state refusals and never block other states on the same variable. |
| C6 | CN gate clauses 3–15 produce the same refusals as the CN `not_evaluated` reason names; no renaming of CN facts. |
| C7 | `state_criterion_unavailable` for missing referenced `con_`; `state_criterion_not_resolvable` for a registered `con_` whose lineage is not cleanly declared. |
| C8 | The public CN parser is reused identically to BH: no copy, no fork, no permissive wrapper, no re-export. |
| C9 | `CanonicalObservedDecimal` admitted-bounds parity with CN: the byte-count, coefficient-digit, fraction-digit, exponent-field, exponent-magnitude, expanded-digit, expanded-fraction, and canonical-output-bytes limits, with the accepted one-step-over hostile suite. |
| C10 | Boolean, object, array, null, malformed, oversized, expansion-hostile `value_json` never reaches comparison. |
| C11 | Numeric parity breaches propagate as the public `NumericParityBreachError` class, never as a `not_evaluated` row. |
| C12 | Staleness class threshold table pinned; the three boundary twins (299.999…/300, 3599.999…/3600, missing observation) are explicit tests. |
| C13 | `evidence_staleness_class` never changes a verdict: a stale `matched` stays `matched`. |
| C14 | `matched_state_anchor_ids` is derived, sorted, and recomputed; a forged tuple is rejected by outer validation. |
| C15 | All refusal tuples are in deterministic gate order and contain only independently applicable reasons; no hidden-winner collapse. |
| C16 | `material.revision == semantic_result.semantics_result.revision` and equality of every per-state material revision is enforced by the outer validator; mixed revisions rejected. |
| C17 | A `model_construct` or `model_copy` forgery at any nesting level is rejected. |

### 15.4 Vocabulary and boundaries

| Row | Requirement |
|---|---|
| D1 | Public literal exhaustiveness for `StateVerdict`, `StateClassificationStatus`, `StateRefusalReason`, `EvidenceStalenessClass`, `StateLookupStatus`, `StateDeclarationConclusion`, `StateRuleLineageSummary`, `StateAgreementFinding`, `VariableStatesStatus`, `StateAssertionLookupStatus` — no extras, no aliases. |
| D2 | `satisfied`/`violated` (CN) and `equal`/`different` (BH) never appear in any ST public contract or demo statement. |
| D3 | The words `active`/`on`/`off`/`enabled`/`disabled` never describe a system-operating condition inside the ST surface. |
| D4 | Import-direction AST isolation: kernel upward-import forbidden; lower facades importing ST forbidden; ST constructing stores forbidden. |
| D5 | No writes: ST public APIs issue no filesystem, database, or ledger mutation. Verified by tracing. |
| D6 | `as_of` never selects model membership; the selected `LoadedModel` is explicit injected revision. |
| D7 | The selected `LoadedModel`, binding revision, interpretation revision, and `as_of` are echoed on the result; none is hidden. |
| D8 | `staleness_seconds` and `evidence_quality` carried verbatim per candidate. |
| D9 | Classification emits no `current_state`, `system_state`, `operating_state`, `health`, `fault`, or `safe` field. |
| D10 | Rejected alternatives remain rejected: embedded predicates, constraint inheritance, state families, persistence. |

### 15.5 Coherent-mutation / revalidation

| Row | Requirement |
|---|---|
| E1 | Mixed model, binding, and interpretation revisions across `state_results` and `semantic_result` rejected. |
| E2 | Context substitution between request and any carried kernel result rejected. |
| E3 | Variable, semantic-lock, source-locator, candidate, occurrence, or owner substitution detectable from carried material rejected. |
| E4 | Forged `matched_state_anchor_ids`, forged verdicts, forged refusal tuples, forged staleness classes, forged canonical decimals rejected. |
| E5 | Outer validator re-runs each state's lifecycle derivation from `material.records` alone; no store, no path, no network. |
| E6 | A fully coherent lower-evidence mutation accepted by lower public contracts (BH §23.6 limitation) is acknowledged as outside ST's detection boundary; an executable test proves the boundary honestly. |

---

## 16. Bounded Demonstration

The demonstration proves architectural evidence without fabricating printer
operating states.

### 16.1 Append set (owner-gated slice, exact set fixed in §18 after rehearsal)

Exactly:

1. One `StateAnchor` under `ohk-demo-1` with a neutral
   display name (e.g. `"demonstration-region-1"`).
2. One `StateRegistration` binding that anchor to the existing hotend
   temperature variable `var_b7e2d3c4f5a6172839405a6b7c8d9e0f`.
3. One parentless `StateDeclaration` in `view_independent` context whose
   criterion is `numeric_membership_via_constraint` referencing
   `con_4b768cf843f5474cb5e564e31d239a59` (the existing committed CN
   constraint, an inclusive upper bound of `80` on that variable).

Never appended: `stw_`, corrections, second roots, `StateFamily`, new `vrg_`,
new `vcn_`, temporal records, binding records, interpretation records, VPA,
ports. **The demonstration reuses the committed constraint identity,
rehearsal discipline, fixture seam exception, and pre-append freeze
machinery** rather than inventing a parallel one.

### 16.2 Evaluation demonstration

Two cases, both over the accepted `60.4` / `85` evidence axis:

1. **Committed happy path:** candidate observation `"60.4"` at the committed
   `received_at=2026-08-07T20:00:18Z`, `as_of` a far-future cutoff.
   The classifier is called, the ES stack yields a satisfied-shape,
   `declared_semantics_compatible` candidate, the referenced `vcn_` is
   `declared` with upper bound `80`, and the verdict is `matched` with
   `evidence_staleness_class = "stale"` (committed data is months old as of
   2026-08-30). The result carries the CN vocabulary in its refusals:
   empty tuple. The demo test asserts whole-object-equality against a
   directly computed lower result, the pinned revision, and the pinned
   staleness class.
2. **Non-committed synthetic `85` case:** an ad-hoc ES-compatible evidence
   set constructed via fixture, never committed, yields `not_matched`. This
   demonstrates the verdict's opposite arm without fabricating a real
   machine state.

`not_evaluated` demonstrations exist only in synthetic tests (state lineage
conflicted, state criterion unresolvable, observation absent, observation
unattached, constraint semantics lock mismatch). No committed record is
mutated to produce them.

### 16.3 Disclosure artifact

Following BH-001's 122406-byte pattern, the demo artifact:

- Echoes the request (variable, `as_of`, `entity`, `source`, `context`).
- Carries the selected model membership exactly once (`ModelQueryMaterial`,
  including the three new records).
- Carries the ES result once, with the admitted candidate visible.
- Carries the per-state kernel lifecycle disclosure once per state.
- Carries the classifier decision summary per row, with no rollup verdict.
- Discloses staleness via `evidence_staleness_class`, with the constants
  inline.
- Restates the raw-authenticity limitation verbatim.
- Is reproducible byte-for-byte from the committed ledger and injected
  facades, with independent regeneration producing identical bytes.

The demo statement, present in the `OwnerDeclarationEvidence`, says exactly
that: it is a synthetic demonstration of classification mechanics over a
committed numeric constraint, it makes no claim about a real printer, safe
operating limit, manufacturer specification, alarm threshold, recommended
setting, required action, operating normality, health, fault, safety, or
control, and a match does not indicate correct, safe, or nominal behavior.

---

## 17. Replay and Migration Consequences

- **Historical memberships replay unchanged.** All explicit memberships
  (9/10/11/14/16/18/28/29/32 records) replay with their pinned revisions.
  Pre-ST replay returns structured absence (`state_declaration` →
  `not_registered`, `states_of_variable` → empty entries on registered
  variables, `state_assertion` → `not_found`).
- **No migration.** No accepted record is rewritten, re-tagged, re-hashed,
  or moved. No existing byte changes.
- **Membership closure.** An ST replay subset containing `srg_` must contain
  the target `vrg_` and its owner `reg_` (the accepted VM closure rule),
  and the referenced `crg_`/`vcn_` records if those are cited from the
  criterion closure path (admission, not evidence). A subset containing `std_`
  must contain its `srg_` and any cited model evidence. Withdrawal targets
  must be present; foreign evidence remains declared references.
- **A revised constraint revises classification behavior, not state records.**
  If a later owner-approved `vcn_` supersedes the demo's bound, replays of
  the old membership still classify `60.4` against the old predicate; the
  current membership classifies against the new one. No retro-invalidity.
- **Explicit membership pinning.** The new membership and revision (32 + 3
  records = 35) becomes a pinned constant after owner gate. Old constants
  remain pinned. Prefix filters never select membership.

---

## 18. Owner-Gated Implementation Slices

Each slice begins with persisted design/acceptance criteria, red-first tests,
reviewable commit groups, independent review, and owner acceptance. One slice
does not authorize the next.

### Slice A — identity, records, store validation (no queries, no evaluator)

Implement:

- `StateAnchor`, `sta_`, `mint_state_anchor`.
- `StateRegistration`/`srg_`, `StateDeclaration`/`std_`, `StateWithdrawal`/`stw_`.
- Canonical prefixes, record union, filename grammar, evidence arms.
- Public builders through the existing canonical API.
- Model-store validation and immutable indexes.
- DAG lifecycle: correction, corroboration, withdrawal, replay.
- All byte-preservation and historical replay tests.
- ADR-0016 outline, implementation plan, acceptance matrix, module READMEs.

Stop at owner acceptance.

### Slice B — kernel query surface (no evaluator)

Implement:

- The exact four `ModelQueries` methods.
- Carry-once `ModelQueryMaterial` result contracts.
- Roots, tips, withdrawals, effective-body groups, corroboration, conflict.
- Per-assertion disclosure.
- Authoritative outer-result reconstruction.
- Deterministic ordering and hostile revalidation tests.

Stop at owner acceptance.

### Slice C — evidence-gated classifier (no committed fixture)

Implement:

- `backend/state_classification/`.
- Constructor dependency injection, error tree, exact public literal
  vocabularies, public `__all__`.
- Admission gate-order implementation.
- Public CN parser reuse, hostile-input parity tests.
- Exact per-row refusal vocabulary and ordering.
- Staleness disclosure class with pinned thresholds.
- Store-independent authoritative reconstruction.
- Import-direction AST isolation tests.
- The BH §23.6-style executable coherent-mutation limitation test.
- Disposable `matched`/`not_matched`/`not_evaluated` fixtures.

No committed model, binding, interpretation, temporal, source, or structural
mutation. Stop at owner acceptance.

### Slice D — bounded committed demonstration

Only after Slices A–C are owner accepted:

1. Owner freeze of the exact candidate anchors (rehearsed through the minter
   once; reconstruction used thereafter — the BH §31 discipline).
2. Two independent disposable ledger rehearsals reconstruct the frozen
   mappings and exercise the append and disclosure artifact; both produce
   identical anchors, record ids, hashes, membership order, revision, and
   artifact bytes.
3. The exact rehearsal results are presented at the Slice D owner gate.
4. Only after approval, one `srg_` and one `std_` are appended through the
   public builders and `ModelStore`, in that physical order, using only
   public APIs.
5. The 35-record revision id is pinned and replayed.
6. The deterministic disclosure artifact is produced and pinned by SHA-256.
7. Every earlier historical replay and record byte remains unchanged,
   mechanically checkable.
8. The demo evaluation shows `matched` for `60.4` and the synthetic `85`
   `not_matched` case as a disposable test only.
9. Final verification, report, owner acceptance.

---

## 19. Security and Denial-of-Service Analysis

Threats, mapped to accepted patterns and to the new ST surface:

- **Record/identity forgery.** Bounded identifier grammars, content-derived
  hashes, complete nested reconstruction before trust, evidence closure, and
  immutable sorted indexes — same controls as CN/PT/VP/BH. The ST diff adds
  no new attack surface here.
- **DAG attacks.** Cycles, self/cross-subject parents, cross-root convergence —
  same rejection path as BH. Zero-tip-unreachable defends in depth.
- **Expression-language risk.** There is no expression language. v1's
  criterion is a single identity-token reference. No AST, no bytecode, no
  scripts, no external model references, no plugin operators, no dynamic
  imports.
- **Numeric attacks.** Reuses the public CN parser with byte-count,
  coefficient-digit, fraction-digit, exponent-field-length, exponent-magnitude,
  expanded-digit, expanded-fraction, and canonical-output-bytes limits; one-
  step-over hostile tests; ambient Decimal and float forbidden. Identical to
  BH-001 §23.3 and the mandatory BH-001 Slice C hardening gate.
- **Candidate and selection attacks.** Exactly one ES facade invocation per
  query; one candidate per explicit selector; no cross-product; no hidden
  winner. Identical to BH-001 §23.4.
- **Result/dependency attacks.** Carry material once; strict indices
  rejecting booleans; every derived field recomputed; validators access no
  store or filesystem; no dynamic imports.
- **Inherited limitations.** Reuse the BH §23.6 statement verbatim: lower
  layers may parse `value_json` before ST accesses the CN parser; ST bounds
  its own records, graph work, and numeric path only. The mandatory hardening
  gate from BH Slice C (bounded preflight, parity suite, hostile-shape
  refusal, honest typed-failure propagation, ambient-context test) carries
  over into ST Slice C exactly.
- **Staleness misdirection.** The `evidence_staleness_class` constants are
  plain numbers in the committed module; forged values in an outer result are
  rejected by the outer validator's recomputation. No time-axis truth is
  claimed.

---

## 20. Prerequisite Repairs and Design Spikes

These are owner decisions required before Slice A code lands. Each is small
and reversible; together they are the only prerequisite work I believe must
precede implementation.

### Spike P1 — Resolve the overlap/corroboration semantic for state identity

Question: when two healthy independent roots produce identical effective
bodies (same anchor, context, criterion), does that corroboration mean the
underlying declared states are *the same* state claimed twice, or two
co-existing claims that happen to share a body? BH-001 chose the latter
(disclosure-only). For state identity this matters more, because the
engineering intuition "we mean the same region" is stronger than for behavior
equality. I recommend BH's disclosure-only answer (no identity merge), but
the owner should explicitly confirm. If the owner wants identity merge, the
record design changes (a canonical region-identity key would be required,
which violates Inv-3) — hence the spike.

### Spike P2 — Pin the `evidence_staleness_class` constants

The 300/3600 second thresholds in §9.5 are placeholders. The owner should
approve exact constants (or a different policy: e.g. "no classification of
staleness at all, pure pass-through of seconds"). This is a policy, not an
architectural choice.

### Spike P3 — Decide whether `state_lifecycle` on `StateClassificationRow`
### should echo or restate

Options: (a) echo the kernel `state_results[i].conclusion` verbatim,
validator-locked; (b) forbid the field. I recommend (a) with the lock, but
the kernel's honest separation between lifecycle and verdict can support
either. Owner chooses.

### Repair R1 — None required

No accepted module's contract, boundary, or record requires repair to host
ST-001. Every upstream ledger (model, binding, interpretation, temporal,
source, structural) is untouched beyond additive AST-isolation widenings.

---

## 21. Owner Questions (Exact, Unresolved)

These are genuine open questions, listed for the owner gate. None of these
is rhetorical framing.

1. **Overlap and corroboration (P1).** Should the design adopt BH-001's
   disclosure-only answer for identical-body independent roots, or should it
   require a distinct canonical region identity (which would restructure the
   record content and violate Inv-3)?
2. **Staleness policy (P2).** The 300 and 3600 constants? A different policy
   (e.g. "class omitted, seconds only")? Or a policy field on the result
   (governed) rather than constants?
3. **Criterion reference form.** v1 allows exactly `numeric_membership_via_
   constraint`. Should a v1.5 owner-gated addition permit a direct
   `ExactNumericInterval` inline criterion (Alternative A), and if so should
   that be gated behind a new discriminator arm (`kind:
   "inline_exact_numeric_interval"`) so records can never silently switch?
4. **Context surface in v1.** Should `classifications_of_variable` require
   `context` (always exact-context), or accept `context: AssertionContext |
   None` and treat `None` as a multi-context disclosure query? v1 requires
   the former; I recommend keeping it.
5. **`matched_state_anchor_ids`.** Keep the derived convenience tuple on the
   result, or forbid it as too close to a rollup? It is the only derived
   cross-row content.
6. **Registration evidence shape.** `srg_` follows the CN `crg_` precedent
   (`NonEmptyCanonicalEvidenceTuple`). Should it follow the older `vrg_`
   precedent (no evidence field) instead? I recommend following `crg_`.
7. **Explicit exact-anchor classifier method.** Should Slice C add
   `classification(state_anchor_id, …)` as a second public method (the BH
   symmetric shape), or keep v1 to only `classifications_of_variable`?
   I recommend the latter for scope discipline.
8. **Slice D fixture seam.** Do you authorize one owner-visible seam
   exercise mirroring BH-001's public-minter pattern, or should Slice D
   commit hand-authored anchors (in which case the freeze/rehearsal discipline
   changes)?
9. **Naming of the discriminator arm.** `numeric_membership_via_constraint`
   vs. `via_constraint_numeric_membership` vs. another phrasing — a wording
   choice that becomes contract-permanent the moment Slice A lands.

---

## 22. Hard Disagreements I Expect Another Architect May Raise

Listed honestly, with my position.

1. **"A state without a `StateFamily` is under-modeled and will need
   retrofitting."** I agree that composite and FSM-adjacent needs will
   arrive. My position is that ST-001's job is identity + evidence-gated
   classification first; retrofitting a family later is cheaper than
   defending against an FSM that was introduced for aesthetic completeness.
2. **"Reference-by-constraint blocks non-numeric states."** True, and
   deliberate. Non-numeric states come behind a new `StateCriterion` arm on
   an owner gate; v1 deliberately refuses them to keep CN's numeric
   authority undiluted.
3. **"`matched_state_anchor_ids` is a slip toward a rollup."** I agree it is
   adjacent. Owner question 5 exists to let the owner forbid it. My
   recommendation keeps it because "which states matched this observation"
   is the natural question classification answers, and forbidding the set
   merely forces every consumer to re-derive it unverified.
4. **"The staleness class creates an arbitrary time policy in a time-free
   layer."** I agree. Owner question 2 names it as a placeholder. My
   recommendation keeps the class because silence on staleness was
   repeatedly identified in earlier milestones as the path to consumers
   inventing their own thresholds; giving them one disclosed, deterministic,
   recomputable class reduces that drift.
5. **"The demonstration is under-powered (a single matched verdict)."`**
   True, but the alternative — a composite or multi-variable demo — would
   invent the temporal-alignment semantics the owner direction explicitly
   defers. A single matched verdict on a committed constraint is honest
   architectural evidence; anything more would fabricate it.
6. **"Kernel-level `state_` prefixes leak the word 'state' into the typed
   ledger before the transition design exists."` This is the most
   consequential point. I expect another architect to propose alternatives
   (e.g. `region_`, `class_`, `category_`). I accept this risk but use
   `state_` because (a) the owner direction names it explicitly, (b)
   vocabulary hygiene (Inv-9) does the actual FSM defense, and (c) any
   alternative coinage would still need to be named "state" in prose, just
   with different record kinds. The honest path is to name the thing and
   forbid the fields.

---

## 23. Proposed ADR-0016 Outline

```text
# ADR-0016 — Explicit state identity and evidence-gated classification

Status: Proposed (owner gate).

## Context
- After BH-001 the model kernel carries anchors, registrations,
  correctable declarations with correction DAGs, evidence closure, and
  carry-once authoritative reconstruction. CN-001 owns the only accepted
  numeric predicate vocabulary. No state primitive exists. The owner has
  authorized ST-001 (identity + classification) and gated ST-002
  (transitions).

## Decisions
1. A state identity is a canonical StateAnchor (sta_), opaque, pure
   identity, minted through the public System Identity minter and first
   persisted by StateRegistration.
2. StateRegistration (srg_) is the permanent, evidence-bearing
   membership claim of one sta_ anchor to one registered variable, with
   no lifecycle, no correction path, no withdrawal.
3. StateDeclaration (std_) is the correctable claim keyed by
   (state_anchor_id, exact AssertionContext). Its v1 criterion is only
   numeric_membership_via_constraint, carrying a con_ anchor reference.
4. StateWithdrawal (stw_) retracts one current std_ tip. No evidence,
   no context, no parents, uncitable.
5. Effective-body projection for corroboration: state_anchor_id, context,
   criterion. Same BH rule: identical-body roots corroborate, differing
   bodies conflict, forks within a root conflict, ranking forbidden.
6. The kernel gains exactly four read-only queries: state(),
   state_declaration(), states_of_variable(), state_assertion().
7. backend.state_classification is a read-only facade composing the
   accepted ES stack and reusing the public CN parser only. Admission
   gate order is fixed. Verdict vocabulary is {matched, not_matched,
   not_evaluated}. Lifecycle vocabulary is kernel-side and never reused as
   a system-state claim.
8. Staleness is carried and disclosed via a published, deterministic
   evidence_staleness_class; it never gates.
9. No StateFamily, no StateSpace, no entity/subsystem/system-level state,
   no multi-variable composite state, no non-numeric criteria, no
   transition machinery, no persisted computed state.
10. Authoritative reconstruction boundary and the BH raw-authenticity
    limitation are restated verbatim.
11. Historical memberships replay unchanged; no migration; explicit 32→35
    membership pinned at the Slice D gate.

## Consequences
- The system can answer "which explicitly declared states, targeting this
  variable, satisfied their referenced CN predicate under this admitted
  observation set?" with full lifecycle and evidence disclosure.
- Nothing can yet answer "what state is the system in" above one variable,
  "what changed", "what caused what", or "what happens next".
- The FSM vocabulary is structurally absent, not merely discouraged.
```

---

## 24. Summary

ST-001 as proposed here is two new record kinds anchored in the accepted
opaque-anchor/correction-DAG pattern, four read-only kernel queries, and a
single-argument read-only classifier facade that composes the ES stack and
reuses the CN parser. It contains no `StateFamily`, no transition machinery,
no numeric arithmetic beyond what CN already admits, no persisted computed
state, and no vocabulary that could be misread as safety, health, fault,
normality, or machine truth. It deliberately restricts criteria to
constraint-referenced numeric membership so that CN's truth remains the
single source. It answers the classification question honestly: matched does
not mean safe, not_matched does not mean faulty, and the result can always
be reconstructed from carried material while never claiming raw-source
authenticity.

END OF ST-001 KIMI K3 CHALLENGER PROPOSAL
