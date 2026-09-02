# ST-002 — Explicit State Transition Identity and Evidence-Gated Transition Disclosure

**Status:** Codex lead architecture proposal; owner decision pending

**Date:** 2026-09-01

**Repository baseline:** `main = origin/main = e44a18641ba6b440adcf9c10cd86d28376886942`

**Accepted model baseline:** 34 records at `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`

**Scope:** design only; no implementation, identity allocation, record append, fixture, artifact, or history operation

## 1. Executive decision

### 1.1 Recommendation

ST-002 should establish only:

1. an opaque transition identity;
2. a permanent, evidence-bearing registration of one directed transition
   between two state identities owned by the same subject entity;
3. a correctable, exact-context transition declaration that pins the exact
   governing from-state and to-state declaration records;
4. bounded correction, corroboration, conflict, withdrawal, and
   membership-relative replay semantics; and
5. authoritative, read-only model-kernel disclosure.

ST-002 should **not** implement transition assessment, occurrence detection,
or an occurrence record. Those capabilities are not supportable from the
accepted ST-001 `independent_latest_at_or_before_cutoff` classification
contract. They require a later, separately owner-gated temporal
cohort/continuity contract.

The phrase **evidence-gated transition disclosure** therefore means that an
explicit transition registration or declaration is admitted only with
accepted evidence and that public results disclose the complete authoritative
model material. It does not mean that observations are evaluated to infer a
transition.

### 1.2 Normative short form

> A transition declaration says that an identified authority has declared a
> directed transition possibility between two exact state-declaration
> meanings in one exact context. It does not say that the transition is
> enabled, executable, occurring, completed, observed, caused, safe, correct,
> or recommended.

### 1.3 Why the assessment boundary is mandatory

Two ST-001 classifications at two cutoffs are two independent,
revision-relative evidence comparisons. Conditions within either result may
come from different acquisition times. Evidence may be stale. Multiple state
identities may simultaneously return `matches`. No accepted contract proves
continuous occupancy of the from-state, exit from it, entry into the to-state,
absence of an intervening state, endpoint exclusivity, or causal order.

A changed source value, a temporal `change_class="changed"`, receipt order,
or different classifications at two cutoffs therefore remains insufficient.

## 2. Repository and architecture findings

### 2.1 Verified starting state

The architecture inspection established the following baseline facts:

| Finding | Repository evidence and consequence |
|---|---|
| Branch and topology | `main`, local `main`, and `origin/main` resolve to `e44a18641ba6b440adcf9c10cd86d28376886942`. |
| Working tree | Clean before this proposal was created. |
| Authoritative model | `models/demo-printer` loads through public `ModelStore` as exactly 34 records at the accepted revision. |
| Existing state content | Exactly one `StateRegistration`, one parentless `StateDeclaration`, and zero `StateDeclarationWithdrawal` records. |
| Existing state identity | `sta_ec739d80d5a843d28a91f4cf96de3883`. |
| Existing state declaration | `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`, context `lifecycle_view / as_operated`. |
| Identity architecture | Opaque anchors live in `backend.system_identity`; names are human-facing metadata, not semantics. |
| Ledger architecture | Evidence-bearing engineering knowledge lives in the model ledger and participates in the existing `mrv_` membership revision. |
| Record identity | `<prefix>_<sha256(canonical_bytes)>`; `record_id` is excluded from the payload; UTC is canonicalized with `+00:00`. |
| Result authority | Kernel results carry complete `ModelQueryMaterial` exactly once and rederive every conclusion from that material. |

### 2.2 Accepted ST-001 semantics

The accepted state layer already distinguishes:

- opaque `StateAnchor` identity;
- permanent entity-scoped `StateRegistration` (`srg_`);
- correctable exact-context `StateDeclaration` (`std_`);
- current-tip withdrawal (`stw_`);
- authoritative model disclosure; and
- an upper-layer classification whose only positive computed value is an
  evidence-relative `matches` conclusion.

The state classifier deliberately has no state-family, aggregate-current-state,
transition, persistence, or temporal-alignment policy. Its temporal alignment
is always `not_asserted` when it executes.

### 2.3 Lower-layer temporal limits

`TemporalOccurrence` is an immutable point fact and expressly does not prove
that a value persisted until a later poll. `latest_observed()` selects one
latest point for one complete source locator at or before a cutoff. Attempt
coverage discloses failures, quarantines, omissions, and staleness but does not
turn samples into validity intervals.

Behavior evaluation can require two observations to share one acquisition
envelope. That is a point-cohort gate for one evaluation, not longitudinal
continuity, endpoint occupancy, or transition order.

### 2.4 Existing store and lifecycle pattern

The model kernel already supplies the appropriate pattern:

- immutable content-addressed records;
- one permanent registration per anchor;
- exact-context correction DAGs;
- canonical parent tuples;
- same-root forks that remain conflicts even when bodies are equal;
- cross-root corroboration only when healthy effective bodies are identical;
- current-tip-only withdrawal;
- full-membership replay and validation; and
- sorted, index-based public disclosures over complete model material.

ST-002 should extend that pattern rather than create a transition-specific
store or revision family.

### 2.5 Demo consequence

The accepted ledger has only one state identity. If self-transitions are
rejected, as this proposal recommends, the existing authoritative ledger
cannot support an honest non-self transition fixture. ST-002 must not invent a
second endpoint, weaken the identity policy, or mislabel a self-transition to
force a demo.

## 3. Revised objective and capability boundary

### 3.1 Project objective

Create a minimal, deterministic, evidence-bearing model vocabulary for saying:

> transition identity T is permanently registered as a directed relation from
> state identity A to state identity B for subject entity E; in exact context C,
> an authority declares T using exact state-declaration records DA and DB.

The public kernel must disclose that statement, its evidence, exact endpoint
pins, correction lineage, agreement or conflict, withdrawal state, complete
membership, and endpoint-pin alignment without inference.

### 3.2 Included capability

- opaque transition identity and public minting contract;
- same-entity directed endpoint registration;
- exact state-declaration pinning;
- exact-context declaration lifecycle;
- evidence admission through existing evidence kinds;
- content-derived record identity and the existing model revision;
- deterministic public lookup, contextual declaration, entity collection, and
  assertion disclosure;
- endpoint pin alignment against the selected model membership;
- historical replay over any admitted membership; and
- hostile outer-result revalidation.

### 3.3 Excluded capability

- observation-derived transition assessment;
- transition occurrence identity, record, store, or detector;
- execution, enablement, next-state choice, graph traversal, or state machine;
- triggers, semantic events, guards, actions, effects, dwell, debounce,
  hysteresis, persistence, or continuity;
- exclusivity, completeness, priority, ranking, arbitration, or parallel-edge
  selection;
- control, commands, recommendations, diagnosis, safety, health, fault,
  correctness, or causality.

### 3.4 Layer boundary

The model kernel may answer only what the selected model membership says. It
must not read bindings, interpretations, source data, temporal data,
observations, classifications, files, clocks, or network resources while
deriving transition conclusions.

## 4. Concepts and truth planes

### 4.1 Distinct concepts

| Concept | Meaning | Persistence location | ST-002 status |
|---|---|---|---|
| Observation | A source reported a value at one occurrence. | Raw/temporal evidence layers | Existing; not changed |
| State declaration | An authority declared one state meaning in an exact context. | Model ledger | Existing; not changed |
| State classification | Selected admitted observations satisfy or do not satisfy one declared state condition set under explicit revisions and cutoff. | Returned result only | Existing; not changed |
| Transition declaration | An authority declared a directed possibility between exact endpoint declaration meanings. | Model ledger | Included |
| Transition assessment | Evidence is consistent with a declared transition under an explicit temporal policy. | Returned result only, if later designed | Deferred |
| Transition occurrence | An accountable claim that a particular transition occurred. | A future explicit evidence contract, not inferred model knowledge | Deferred |

### 4.2 Three statements that must never collapse

1. **Declared transition possibility** — supported in ST-002.
2. **Evidence consistent with a transition** — unsupported in ST-002.
3. **Asserted transition occurrence** — unsupported in ST-002.

No positive or negative result in one plane is a substitute for another.

### 4.3 Non-creation rules

None of the following creates a transition identity, declaration, assessment,
or occurrence:

- endpoint names;
- shared subject ownership;
- hierarchy or relationship edges;
- CAD, ports, VPA, PIF, PCN, PCM, behavior declarations, or semantic
  compatibility;
- state constraints or CN satisfaction;
- one or more ST `matches` results;
- a value change or `change_class`;
- receipt-time or source-time order;
- temporal proximity or correlation;
- a later state correction; or
- displaying two states or observations beside one another.

## 5. Alternatives considered and architecture decision

### 5.1 Alternative A — infer transitions from two classifications

Rejected. It would treat independently selected point evidence as continuous
state occupancy. It also fails when both endpoint states match, when a reused
stale observation supplies either cutoff, or when model revisions differ.

### 5.2 Alternative B — reuse temporal `change_class`

Rejected. `change_class` compares exact source-native serialized values along
one source locator. It carries no state anchor, state-declaration pin,
constraint evaluation, exclusivity rule, or transition authority.

### 5.3 Alternative C — use BH same-acquisition cohort

Rejected for transition assessment. A BH cohort proves only shared acquisition
envelope for its participant observations. It provides no ordered endpoint
cohorts, inter-cohort continuity, or persistence.

### 5.4 Alternative D — add a model-ledger occurrence record

Rejected. The model ledger records engineering knowledge, not a stream of
derived observations. An occurrence would also require authenticity,
continuity, time-axis, gap, and replay rules that do not exist.

### 5.5 Alternative E — identity and declaration disclosure only

Accepted. It adds a useful explicit concept without overstating the evidence
contracts. It preserves the existing layer boundaries and leaves a clear
extension point for a later temporal milestone.

### 5.6 Architecture decision

ST-002 v1 is a model-kernel extension only. There is no
`backend.transition_assessment` package, transition evaluator, occurrence
detector, transition history projection, or separate transition ledger in this
milestone.

## 6. Exact transition identity policy

### 6.1 Anchor contract

Add a future `TransitionAnchor` to `backend.system_identity` with this exact
shape:

| Field | Contract | Identity role |
|---|---|---|
| `anchor_id` | `trn_[0-9a-f]{32}` | Opaque continuity token |
| `namespace` | Existing bounded local identifier contract | Human organization only |
| `display_name` | Existing bounded human-facing name contract | Non-semantic |
| `role_name` | Existing bounded human-facing role contract | Non-semantic |

The model is frozen, forbids extras, and revalidates nested instances. No
endpoint, context, trigger, event, guard, action, effect, condition, outcome,
or temporal field belongs in the anchor.

### 6.2 Minting

The future public `mint_transition_anchor()`:

- allocates one opaque UUID4-derived `trn_` identity;
- accepts only human-facing metadata;
- performs no I/O and consults no ledger;
- has no deterministic or name-derived mode; and
- is never called during replay or reproduction of a frozen candidate.

This proposal allocates no identity.

### 6.3 Continuity rule

One transition anchor means continuity of one same-subject directed endpoint
pair only. Registration permanently fixes:

`(subject_entity_anchor_id, from_state_anchor_id, to_state_anchor_id)`.

Changing the subject or either state anchor requires a new transition anchor.
Changing only the exact endpoint state declarations may be expressed by a
corrected transition declaration under the same transition anchor.

### 6.4 Direction

Endpoint order is semantic. `A → B` and `B → A` are different registrations
and require different transition anchors. Endpoint fields are never sorted.

### 6.5 Same-subject restriction

Both endpoint `StateRegistration` records must exist and must permanently name
the same subject entity as the transition registration. Cross-entity
transitions are rejected in v1.

### 6.6 Self-transition restriction

`from_state_anchor_id` must differ from `to_state_anchor_id`. A self-transition
normally conveys event, trigger, action, or re-entry semantics, all of which
are deferred. A same-state edge without those semantics would be an opaque
duplicate with no honest disclosed distinction.

### 6.7 Parallel-transition restriction

Within one selected membership, at most one transition registration may use
the same ordered `(subject, from-state, to-state)` tuple. Independent
authorities corroborate or disagree through multiple declaration roots under
the same transition identity, not through indistinguishable duplicate edges.

This restriction is an owner decision because a future event/trigger contract
may later justify multiple distinguished transitions between the same states.

### 6.8 Names do not select identity

Equal names do not merge anchors. Different names do not split or correct an
anchor. Queries accept exact opaque IDs only and never discover or select a
transition by name.

## 7. Proposed model record contracts and prefixes

### 7.1 Record set

| Record | Kind | Prefix | Purpose |
|---|---|---|---|
| `TransitionRegistration` | `transition_registration` | `trg_` | Permanent identity, subject, and directed endpoints |
| `TransitionDeclaration` | `transition_declaration` | `trd_` | Correctable exact-context declaration with exact endpoint declaration pins |
| `TransitionDeclarationWithdrawal` | `transition_declaration_withdrawal` | `trw_` | Membership-relative withdrawal of one current TRD tip |

No transition occurrence, assessment, correction record, fork record, second
root record, event record, or execution record is introduced. A correction is
another `trd_` with `supersedes`; an independent root is a parentless `trd_`.
TRG and TRD records may be cited by later model records. TRW records are not
citable, matching the existing withdrawal boundary.

### 7.2 `TransitionRegistration`

Exact fields:

| Field | Contract |
|---|---|
| `record_kind` | Literal `transition_registration` |
| `schema_version` | Literal `1` |
| `record_id` | `trg_[0-9a-f]{64}` |
| `anchor` | Complete frozen `TransitionAnchor` |
| `subject_entity_anchor_id` | Existing entity anchor pattern |
| `from_state_anchor_id` | Existing state anchor pattern |
| `to_state_anchor_id` | Existing state anchor pattern; must differ from from-state |
| `evidence` | Nonempty canonical tuple of existing admitted evidence refs |
| `recorded_at` | Aware datetime normalized to UTC |
| `authority` | Existing `AuthorityRef` |
| `note` | String, default empty; non-semantic |

The registration has no context, parents, withdrawal target, endpoint
declaration pins, classification, trigger, event, guard, action, effect,
priority, timing, or outcome.

Store admission requires:

- exact registered subject entity;
- exact registered from-state and to-state;
- exact same subject on both state registrations;
- uniqueness of the transition anchor;
- uniqueness of the ordered endpoint tuple;
- non-self endpoints;
- direct evidence citations to the subject entity registration and both state
  registrations; and
- at least one accepted owner/authority declaration describing this synthetic
  or engineering claim.

### 7.3 Endpoint declaration pin

`TransitionStateDeclarationPin` has exactly:

| Field | Contract |
|---|---|
| `state_anchor_id` | Existing state anchor pattern |
| `declaration_record_id` | `std_[0-9a-f]{64}` |

It is frozen, forbids extras, and always revalidates nested input. Role is
carried by the containing field (`from_endpoint` or `to_endpoint`), not by a
mutable string inside the pin.

### 7.4 `TransitionDeclaration`

Exact fields:

| Field | Contract |
|---|---|
| `record_kind` | Literal `transition_declaration` |
| `schema_version` | Literal `1` |
| `record_id` | `trd_[0-9a-f]{64}` |
| `transition_anchor_id` | `trn_[0-9a-f]{32}` |
| `context` | Exact existing `AssertionContext` |
| `from_endpoint` | Exact `TransitionStateDeclarationPin` |
| `to_endpoint` | Exact `TransitionStateDeclarationPin` |
| `evidence` | Nonempty canonical tuple of existing admitted evidence refs |
| `supersedes` | Canonical tuple of `trd_` parents; empty means independent root |
| `recorded_at` | Aware datetime normalized to UTC |
| `authority` | Existing `AuthorityRef` |
| `note` | String, default empty; non-semantic |

There is deliberately no `evaluation_basis` field. ST-002 declares no
observation evaluation algorithm. There is also no field for possibility
status, enabled status, occurrence, trigger, event, guard, action, effect,
duration, priority, confidence, probability, or recommendation.

Store admission requires:

- exact transition registration exists;
- pin state anchors equal the registration's ordered endpoints;
- both pinned `std_` records exist in the selected membership;
- each `std_` names the pinned state anchor;
- each `std_` context exactly equals the transition declaration context;
- required direct citations to the `trg_`, both `srg_` records, and both exact
  `std_` records;
- at least one accepted owner/authority declaration;
- every parent exists, is a `trd_`, and has the same transition/context key;
- no self-parent, cycle, duplicate parent, or noncanonical parent order; and
- the complete selected membership satisfies all lifecycle invariants.

A pinned STD need not remain current forever. Requiring currentness at store
load would make an admitted historical TRD invalid when the state declaration
is later corrected. Instead, pin alignment is disclosed at query time.

### 7.5 `TransitionDeclarationWithdrawal`

Exact fields:

| Field | Contract |
|---|---|
| `record_kind` | Literal `transition_declaration_withdrawal` |
| `schema_version` | Literal `1` |
| `record_id` | `trw_[0-9a-f]{64}` |
| `withdraws` | Exact `trd_[0-9a-f]{64}` target |
| `recorded_at` | Aware datetime normalized to UTC |
| `authority` | Existing `AuthorityRef` |
| `note` | String, default empty; non-semantic |

The withdrawal contains no evidence tuple, context, anchor copy, replacement,
outcome, or reason code, matching the bounded accepted state lifecycle shape.
It may target only an unsuperseded current TRD tip, and a membership may contain
at most one withdrawal for that tip.

## 8. Endpoint and state-declaration pinning rules

### 8.1 Why both identity and declaration are pinned

State anchors provide endpoint continuity. Exact `std_` pins provide endpoint
meaning. If a later STD correction changes VCN pins, condition membership, or
any other effective state-declaration content, it must not silently rewrite an
existing transition declaration.

### 8.2 Admission-time checks

For each endpoint, the model store checks:

1. the state registration exists;
2. its subject matches the transition subject;
3. the pin's state anchor matches the directed registration endpoint;
4. the exact STD exists;
5. the STD names that state anchor; and
6. the STD context equals the transition declaration context.

The store does not run state classification and does not inspect current
observations.

### 8.3 Correction behavior

| Change | Required identity/lifecycle action |
|---|---|
| Correct an endpoint STD but keep both state anchors | New TRD superseding the old TRD and pinning the new exact STD |
| Correct both endpoint STDs | One new TRD pins both new exact records |
| Change from-state anchor | New transition anchor and TRG |
| Change to-state anchor | New transition anchor and TRG |
| Change subject | New transition anchor and TRG |
| Rename any anchor metadata | No semantic change and no automatic record correction |
| State correction occurs but transition is not corrected | Existing TRD remains meaningful; the pin activity becomes `superseded` and alignment becomes `pinned_declaration_superseded` |

### 8.4 Alignment is orthogonal to declaration lifecycle

A healthy current TRD can remain `declared` while one exact endpoint pin's
activity is `superseded` or `withdrawn`. That is an honest statement: the
transition declaration itself is still current, but it intentionally
references historical endpoint meaning. Endpoint alignment must not silently
withdraw it or adopt a corrected STD.

### 8.5 Conflict precedence

If the contextual state declaration is conflicted or inactive, the endpoint
alignment reports that state conclusion even if the pinned STD is among a
conflicted tip set or exists historically. No record ID tie-break chooses a
state winner.

## 9. Correction, corroboration, conflict, withdrawal, and replay

### 9.1 Lifecycle key

The exact transition declaration key is:

`(transition_anchor_id, context)`.

Different contexts have independent correction DAGs. Cross-context parentage
is invalid.

### 9.2 Roots and corrections

- `supersedes=()` creates an independent root.
- A nonempty parent tuple creates a correction/merge in the same key.
- Parent IDs are unique and lexicographically sorted.
- Every parent in a declaration belongs to the same existing root;
  cross-root convergence is invalid.
- The graph must remain acyclic.
- All records remain immutable and visible in historical material.

### 9.3 Effective body

The transition effective body consists of exactly:

1. `transition_anchor_id`;
2. `context`;
3. `from_endpoint`; and
4. `to_endpoint`.

Evidence, authority, `recorded_at`, note, and parents do not belong to the
effective body. They remain identity-bearing audit content of the record.

### 9.4 Root health

| Active tips in one root | Root health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2 or more | `conflicted` |

Same-root forks are conflicted even when their effective bodies are
byte-identical. IDs order disclosure only; they never select a winner.

### 9.5 Cross-root agreement

| Healthy roots | Effective bodies | Result |
|---|---|---|
| One | One | Declared; `one_healthy_root` |
| Two or more | Identical | Declared; `corroborating_healthy_roots` |
| Two or more | Different | Conflicted; `cross_root_effective_body_disagreement` |
| Any plus inactive roots | As above for healthy roots | Add `inactive_roots_present` |

Independent roots represent independent claims about the same registered
transition identity. They do not create parallel transition identities.

### 9.6 Withdrawal

A TRW may withdraw only a current unsuperseded TRD tip. It cannot withdraw a
TRG, an STD, another TRW, a superseded declaration, or a nonmember. A later
successor of a withdrawn tip is invalid in the same selected membership.

### 9.7 Historical replay

All conclusions are membership-relative, never wall-clock-relative. Replaying
an older membership without a later correction or withdrawal reproduces the
older conclusion. Removing a withdrawal by selecting an earlier historical
membership is not mutation; it is revision-relative replay.

Historical memberships and predecessor record bytes remain unchanged when
transition records are later appended.

## 10. Temporal and evidence requirements

### 10.1 Model evidence in ST-002

Evidence proves only that a registration or declaration has explicit cited
support. The kernel validates evidence structure, direct model-record
references, and admitted authority kinds. It does not authenticate raw source
bytes or interpret a citation as occurrence evidence.

Required citations are role-specific and exact. Citation order is canonical,
not semantic. Additional admitted evidence may be carried, but it cannot relax
or replace any mandatory direct citation.

### 10.2 No cutoff in model queries

The four proposed transition model queries take no temporal cutoff. They
operate over one caller-injected `LoadedModel` revision. `recorded_at` is audit
metadata and content identity, not a model selection clock.

### 10.3 Why current ST classifications cannot be composed

| Available fact | What it proves | Missing transition prerequisite |
|---|---|---|
| From-state `matches` at cutoff A | Selected evidence satisfied one declared condition set | Persistence before/after A, exclusivity, exit |
| To-state `matches` at cutoff B | Selected evidence satisfied another declared condition set | Entry, continuity, endpoint order |
| Different results at A and B | Two derived calls differed | Same model/interpretation/binding cohort and causal explanation |
| `change_class="changed"` | Exact source value differs from its previous point | State meaning and transition identity |
| Receipt A before receipt B | Ingestion-axis order | Source-time order, continuity, causality |
| Same acquisition envelope | Point evidence shared one envelope | Longitudinal interval coverage |
| Complete sampled history | Ordered observations and acquisition attempts | Rules converting samples/gaps to continuous occupancy |

### 10.4 Later assessment prerequisites

Before a future milestone may return “evidence consistent with transition,” it
must separately define and owner-accept:

- two explicit ordered assessment instants and the governing time axis;
- cohort-aligned evidence for every condition at each endpoint;
- cross-source skew/cohort policy where one envelope cannot contain all facts;
- interval coverage and explicit gap, failure, quarantine, and omission rules;
- state overlap/exclusivity policy;
- persistence, dwell, debounce, and hysteresis algorithms if used;
- deterministic bounded window selection and resource limits;
- exact binding, interpretation, model, and temporal revision pins;
- raw-occurrence authenticity boundary; and
- separate contracts for evidence consistency and accountable occurrence.

### 10.5 Explicit feature adjudication

| Feature | ST-002 decision | Reason |
|---|---|---|
| Directed transition identity | Include | Pure model identity and authority claim |
| Endpoint state identity | Include | Existing accepted StateAnchor contract |
| Exact endpoint STD pins | Include | Prevent silent semantic drift |
| Trigger | Defer | No accepted semantic event predicate or temporal relation |
| Event | Defer | Temporal occurrences are acquisition facts, not semantic events |
| Guard | Defer | Needs an assessment instant and cohort-aligned evaluation |
| Action | Exclude/defer | Would introduce command/control semantics |
| Effect | Exclude/defer | Would introduce unsupported causal claims |
| Dwell | Defer | Needs intervals, duration axis, and gap policy |
| Debounce | Defer | Needs a windowed sampling/acceptance algorithm |
| Hysteresis | Defer | No historical predicate or hysteresis contract exists |
| Persistence | Defer | Point observations explicitly do not prove persistence |
| Occurrence detection | Defer | Neither value nor classification difference proves occurrence |

## 11. Exact public query surface

ST-002 adds exactly four read-only `ModelQueries` methods:

```text
transition(transition_anchor_id) -> TransitionLookupResult

transition_declaration(
    transition_anchor_id,
    *,
    context,
) -> TransitionDeclarationResult

transitions_of_entity(
    entity_anchor_id,
    *,
    context,
) -> EntityTransitionsResult

transition_assertion(
    record_id,
) -> TransitionAssertionDisclosureResult
```

No query accepts names, endpoint discovery criteria, cutoff, source selector,
classification result, graph traversal direction, path length, priority, or
automatic context.

### 11.1 `transition()`

Discloses whether the exact transition anchor is registered and, when it is,
indices for the TRG, subject entity registration, and both state registrations.

### 11.2 `transition_declaration()`

Discloses the exact-context lifecycle, roots, tips, withdrawals, effective-body
groups, current declaration indices, and exact from/to pin alignment for each
effective body.

### 11.3 `transitions_of_entity()`

Discloses every transition registration whose permanent subject is the exact
entity, with the same contextual lifecycle and endpoint alignment as the
single-transition query. It does not return transitions merely because an
entity occurs in hierarchy, evidence, or a state name.

### 11.4 `transition_assertion()`

Discloses one exact `trg_`, `trd_`, or `trw_` record ID. For a TRD it also
discloses activity, containing root health, containing transition conclusion,
agreement findings, root, successors, and withdrawals.

### 11.5 Forbidden query aliases

No `current_transition`, `detect_transition`, `assess_transition`,
`possible_transitions`, `enabled_transitions`, `next_state`, `transition_path`,
or `transition_history` alias is added.

## 12. Exact result vocabulary and shape

### 12.1 Literal vocabulary

| Type | Exact literals |
|---|---|
| `TransitionLookupStatus` | `not_registered`, `registered` |
| `TransitionDeclarationConclusion` | `not_registered`, `not_declared`, `declared`, `conflicted`, `inactive` |
| `TransitionDeclarationLineageSummary` | `not_applicable`, `healthy`, `conflicted`, `inactive` |
| `TransitionAgreementFinding` | `one_healthy_root`, `corroborating_healthy_roots`, `same_root_conflict`, `cross_root_effective_body_disagreement`, `inactive_roots_present` |
| `TransitionEndpointRole` | `from`, `to` |
| `TransitionEndpointPinAlignment` | `exact_current`, `pinned_declaration_superseded`, `pinned_declaration_withdrawn`, `endpoint_state_conflicted`, `endpoint_state_inactive` |
| `EntityTransitionsStatus` | `entity_not_registered`, `registered` |
| `TransitionAssertionLookupStatus` | `not_found`, `found` |
| Existing `AssertionActivity` | `current`, `superseded`, `withdrawn` |
| Existing `ContainingLineageHealth` | `healthy`, `conflicted`, `inactive` |

No literal named `possible_now`, `enabled`, `executable`, `triggered`,
`detected`, `occurred`, `completed`, `valid`, `safe`, `healthy_transition`, or
`recommended` is admitted.

### 12.2 Material ownership

Every outer result carries exactly one complete `ModelQueryMaterial`:

- exact `ModelRevision`;
- every selected record exactly once;
- unique record IDs in lexicographic order; and
- record IDs exactly equal revision membership.

Nested rows carry strict integer indices into that material, never duplicate
record objects or a second model snapshot.

### 12.3 Transition endpoint disclosure row

Each effective body contains exactly two endpoint rows in fixed field order:

| Field | Meaning |
|---|---|
| `role` | Exact `from` or `to` role |
| `state_anchor_id` | Exact endpoint state identity |
| `state_registration_index` | Exact SRG in material |
| `declaration_index` | Exact pinned STD in material |
| `state_declaration_conclusion` | Current exact-context ST model conclusion |
| `pinned_declaration_activity` | Existing exact STD activity: `current`, `superseded`, or `withdrawn` |
| `alignment` | Exact revision-relative pin-alignment literal |

In a valid loaded model, the pinned state and STD necessarily exist and have a
contextual declaration lineage. Endpoint rows exist only for an active
effective-body group, so the vocabulary contains no structurally unreachable
absence or `not_evaluated` literal.

### 12.4 Transition effective-body group

Each group discloses:

- deterministic `group_index`;
- representative TRD index;
- sorted current tip indices;
- sorted root record indices;
- exact from endpoint row; and
- exact to endpoint row.

The representative is the lexicographically smallest record ID in the group.
It is a disclosure device, not a winner.

### 12.5 Roots

Each root row discloses:

- root record index;
- sorted lineage record indices;
- sorted current tip indices;
- sorted withdrawal indices;
- lineage health; and
- sorted effective-body group indices.

### 12.6 Entity entries

Each entity transition entry repeats no material. It carries an `entry_index`,
transition anchor, TRG index, exact declaration conclusion and lineage summary,
agreement findings, roots, groups, and current declaration indices.

## 13. Decision tables for every public conclusion

### 13.1 Transition lookup status

| Exact TRG for requested anchor | `status` | Registration/endpoint indices |
|---|---|---|
| Absent | `not_registered` | Null/empty |
| Present and admitted | `registered` | Exact indices |

### 13.2 Transition declaration conclusion

| Registration | Contextual roots | Active-tip state | Healthy body groups | `conclusion` |
|---|---:|---|---:|---|
| Absent | Any | Not evaluated | 0 | `not_registered` |
| Present | 0 | Not applicable | 0 | `not_declared` |
| Present | 1+ | No active tips in any root | 0 | `inactive` |
| Present | 1+ | Any same-root fork | Any | `conflicted` |
| Present | 2+ healthy | One tip each, different bodies | 2+ | `conflicted` |
| Present | 1+ healthy | One tip each, identical body | 1 | `declared` |

Inactive roots do not defeat an otherwise healthy declared conclusion; they
remain visible through `inactive_roots_present`.

### 13.3 Lineage summary

| Declaration conclusion | `lineage_summary` |
|---|---|
| `not_registered` | `not_applicable` |
| `not_declared` | `not_applicable` |
| `declared` | `healthy` |
| `conflicted` | `conflicted` |
| `inactive` | `inactive` |

### 13.4 Agreement findings

Each finding is independently derived and emitted in the fixed vocabulary
order shown below.

| Condition | Finding present |
|---|---|
| Exactly one healthy root | `one_healthy_root` |
| At least two healthy roots share one effective body | `corroborating_healthy_roots` |
| At least one root has two or more active tips | `same_root_conflict` |
| Healthy roots expose two or more effective bodies | `cross_root_effective_body_disagreement` |
| At least one root has no active tips | `inactive_roots_present` |

No finding chooses a winner. A result can contain both a conflict finding and
`inactive_roots_present`.

### 13.5 Endpoint pin alignment

Endpoint alignment is derived separately for each endpoint and each effective
body group.

| Current contextual state conclusion | Pinned STD activity | `alignment` |
|---|---|---|
| `conflicted` | Any | `endpoint_state_conflicted` |
| `inactive` | Any | `endpoint_state_inactive` |
| `declared` | `superseded` | `pinned_declaration_superseded` |
| `declared` | `withdrawn` | `pinned_declaration_withdrawn` |
| `declared` | `current` and exact pin is an admitted current tip | `exact_current` |

Conflict and inactivity take precedence in the single alignment summary, but
the separate `pinned_declaration_activity` field preserves the exact record's
own lifecycle state. Endpoint alignment never changes the transition
declaration conclusion.

### 13.6 Root health

| Current tips after withdrawals | `lineage_health` |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

### 13.7 Entity collection status

| Entity registration | `status` | Entries |
|---|---|---|
| Absent | `entity_not_registered` | Empty |
| Present | `registered` | Every exact-subject TRG, possibly empty |

Each entry's declaration conclusion, lineage summary, findings, groups, and
alignment are derived by the same functions as `transition_declaration()`.

### 13.8 Assertion lookup status

| Requested ID | Exact selected record | `lookup_status` |
|---|---|---|
| Syntactically valid `trg_`, `trd_`, or `trw_` | Absent or wrong kind | `not_found` |
| Syntactically valid transition record ID | Present with matching kind | `found` |

### 13.9 Assertion activity

Activity applies only to a found TRD. A found TRG or TRW has null lifecycle
fields.

| TRD successors | TRD withdrawals | `activity` |
|---:|---:|---|
| 1+ | Any valid membership state | `superseded` |
| 0 | 1 | `withdrawn` |
| 0 | 0 | `current` |

Store invariants make a current-tip withdrawal plus a later successor invalid
in one membership. The first row preserves deterministic defensive precedence.

### 13.10 Assertion containing lineage health

| Containing root current tips | Health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

`containing_subject_conclusion` and
`containing_agreement_findings` are exactly those derived for the TRD's
transition/context key.

## 14. Authoritative outer-result revalidation

### 14.1 Trust rule

Public result validation trusts none of the supplied derived fields, nested
Pydantic instances, private attributes, or cached objects. A successfully
constructed result is proof only that all supplied content equals a fresh
derivation from its carried material.

### 14.2 Required revalidation sequence

Each outer result validator must:

1. reject hidden instance extras before ordinary Pydantic normalization;
2. reject cyclic or pathologically deep container graphs with deterministic
   bounded traversal;
3. require strict integers for revision counts, indices, group indices, and
   entry indices; booleans are not integers;
4. reconstruct the `ModelRevision` and every record from serialized content;
5. require unique lexicographically ordered records;
6. require exact equality between records and revision membership;
7. call authoritative full-set `validate_record_collection()`;
8. require the recomputed revision to equal the carried revision;
9. reconstruct context and nested rows from plain serialized content;
10. derive the complete expected payload from the reconstructed loaded model;
11. compare every supplied field to that expected payload; and
12. bind private material access only after equality succeeds.

### 14.3 Forgery cases that must fail

- altered conclusion or lineage summary;
- omitted conflict or inactive root;
- fabricated corroboration;
- reordered roots, groups, tips, entries, findings, or membership;
- substituted endpoint state, STD, role, or alignment;
- a hidden extra field attached through `model_copy`;
- a forged record type with a valid-looking ID;
- a bool used as an index;
- a nested result built against different material;
- duplicate material or a second revision snapshot; and
- tampered canonical record content or revision.

## 15. Canonicalization, record IDs, revision, and store ownership

### 15.1 Canonical record bytes

Transition records use the existing normative kernel algorithm:

1. validate the complete record;
2. exclude `record_id` only;
3. serialize model data in Python mode;
4. normalize every datetime to UTC `isoformat()` with `+00:00`;
5. recursively preserve list/tuple order and dictionary meaning;
6. JSON-encode with sorted keys, compact separators, UTF-8, and
   `ensure_ascii=False`; and
7. hash the exact bytes with SHA-256.

Every record ID suffix must equal the SHA-256 of
`backend.model_kernel.canonical.canonical_bytes(record)`. JSON-mode `Z`
serialization must never be mislabeled canonical.

### 15.2 Prefix map

The canonical prefix map gains exactly:

```text
transition_registration             -> trg
transition_declaration              -> trd
transition_declaration_withdrawal   -> trw
```

Unknown kinds remain rejected.

### 15.3 Effective-body canonicalization

One private deterministic `_transition_effective_body_bytes()` includes only
the four fields in section 9.3 and uses the same UTC and JSON rules. It is not
a persisted record and has no public identity.

### 15.4 Model revision

Transition records join the existing model ledger and existing `mrv_`
algorithm. No `trv_`, occurrence revision, transition store revision, or
secondary root is introduced. The model revision remains a hash over model ID
and sorted exact record membership.

### 15.5 Public construction and persistence

- Records are constructed only by public model-kernel builders.
- IDs are verified by `compute_record_id()` and `verify_record_id()`.
- Append occurs only through public `ModelStore`.
- Full-set validation runs before persistence and again on load.
- The store writes no transition-specific cache, index file, or mutable tip.

## 16. Import direction and package ownership

### 16.1 Ownership

| Concern | Owning package |
|---|---|
| `TransitionAnchor`, pattern, minter | `backend.system_identity` |
| TRG/TRD/TRW contracts, builders, canonical identity | `backend.model_kernel` |
| Admission, indexes, lifecycle, revision | `backend.model_kernel.store` |
| Read-only transition queries/results | `backend.model_kernel` |
| Observations and point history | Existing lower data/temporal packages; unchanged |
| State classification | `backend.state_classification`; unchanged |
| Future transition assessment | A later upper layer, not created in ST-002 |

### 16.2 Legal import direction

```text
system_identity
      ↑
model_kernel
      ↑
future transition_assessment (later milestone only)
```

`system_identity` must not import model-kernel code. The model kernel must not
import state classification, constraint evaluation, behavior evaluation,
binding stores, interpretation stores, temporal stores, data-source runtime,
filesystem paths, sockets, or clocks for transition disclosure.

### 16.3 Read/write capability boundary

`ModelQueries` receives one already loaded model and is read-only. Public
result validation reconstructs from carried material in memory. Only
`ModelStore` owns model-ledger persistence. Identity minting performs no I/O.

## 17. Deterministic ordering, replay, and clean-checkout obligations

### 17.1 Ordering rules

- model records: lexicographic record ID;
- evidence: existing canonical evidence key;
- parents: unique lexicographic record ID;
- roots: root record ID;
- lineage records, tips, successors, withdrawals: record ID;
- effective-body groups: canonical body bytes;
- representative: smallest record ID in group;
- agreement findings: fixed literal rank from section 13.4;
- entity entries: transition anchor ID, then first root ID;
- endpoint fields: fixed `from`, then `to`; never sorted by anchor ID.

No dictionary insertion order, filesystem enumeration order, append order,
thread schedule, current clock, locale, timezone, hash seed, or Pydantic JSON
timestamp rendering may affect public bytes.

### 17.2 Historical replay obligations

Tests must replay explicit historical memberships, including the accepted
9/10/11/14/16/18/28/29/32/34 record memberships, plus transition lifecycle
memberships introduced by the implementation slices. Every earlier revision
and result must remain byte-for-byte reproducible.

### 17.3 Disposable-root obligations

Any candidate append rehearsal must use at least two independently initialized
disposable model roots copied from byte-identical accepted predecessors. One
column must copy predecessor files in reverse order. Candidate records must be
reconstructed through public builders and appended through public `ModelStore`;
record files must not be copied between roots.

### 17.4 Clean-checkout columns

Every implementation slice and any later candidate must pass:

1. the working repository;
2. a fresh base-only clean checkout; and
3. a fresh all-extras clean checkout.

Across columns, prove equality of canonical bytes, record IDs, stored bytes,
membership, revision, query serialization, historical replay, and predecessor
hash aggregates. Run backend compilation, focused paths, complete repository
suite, whitespace checks, exact topology checks, and loopback separately when
sandbox permissions require it.

## 18. Threat model

| Threat | Required defense |
|---|---|
| Name-derived transition | Opaque ID only; names non-semantic |
| Endpoint reversal | Fixed directed fields; no sorting |
| Cross-entity edge | Exact same-subject admission check |
| Silent endpoint correction adoption | Exact STD pins and alignment disclosure |
| Duplicate indistinguishable edge | Ordered endpoint tuple uniqueness |
| Self-transition smuggling | Explicit unequal endpoint check |
| Hidden trigger/action field | `extra="forbid"` on every contract |
| Classification-as-occurrence | No assessment API or occurrence vocabulary |
| Value-change-as-transition | Explicit non-creation rule and architecture tests |
| Timestamp-order causality | Recorded times excluded from conclusion logic |
| Same-root deterministic winner | Fork remains conflicted regardless of IDs/bodies |
| Cross-root winner | Different bodies conflict; IDs only order output |
| Withdrawal as deletion | Immutable TRW plus historical replay |
| Correction after withdrawal | Full-membership rejection |
| Parent across subject/context | Exact lifecycle-key validation |
| Missing endpoint record | Full-set admission failure |
| Forged result conclusion | Full outer rederivation from material |
| Forged endpoint alignment | Recompute using authoritative state query derivation |
| Hidden Pydantic extras | Pre-normalization instance traversal |
| Bool/index coercion | Strict integer contracts |
| Cyclic hostile payload | Bounded cycle/depth rejection |
| Partial model material | Exact revision membership validation |
| Record content tamper | Canonical SHA-256 ID verification |
| `Z`/`+00:00` canonical mismatch | Normative `canonical_bytes()` parity assertions |
| Nondeterministic output | Explicit ordering and dual-root byte comparison |
| Lower-store access from kernel | Import/capability architecture tests |
| Unbounded graph traversal | No graph/path query; bounded lifecycle validation |
| Ledger split | Existing ModelStore and `mrv_` only |
| Demo overclaim | Mandatory synthetic disclaimer and no occurrence artifact |

## 19. Adversarial acceptance matrix

The implementation is not acceptable until each row is executable and passes.

### 19.1 Identity and contracts

| ID | Acceptance requirement |
|---|---|
| I01 | Transition anchor matches only `trn_` plus 32 lowercase hex digits. |
| I02 | Minting returns opaque UUID4-derived identities and performs no I/O. |
| I03 | Names never affect identity, endpoint selection, or query conclusions. |
| I04 | Reversed endpoints require a different anchor/registration. |
| I05 | Self-transition registration rejects. |
| I06 | Cross-entity endpoint registration rejects. |
| I07 | Duplicate ordered endpoint tuple registration rejects. |
| I08 | All transition contracts are frozen, forbid extras, and revalidate instances. |
| I09 | Trigger/event/guard/action/effect/timing/outcome fields reject. |

### 19.2 Record and canonical identity

| ID | Acceptance requirement |
|---|---|
| R01 | Public builders alone construct admitted TRG/TRD/TRW records. |
| R02 | Each ID suffix equals SHA-256 of normative kernel canonical bytes. |
| R03 | UTC canonical timestamp uses `+00:00`, not JSON-mode `Z`. |
| R04 | Equal instants under different offsets produce identical canonical bytes. |
| R05 | Any identity-bearing edit changes the record ID. |
| R06 | From/to order changes bytes and record ID. |
| R07 | Effective-body bytes exclude evidence, parents, audit time, authority, and note. |
| R08 | Unknown transition kinds and wrong prefixes fail typed. |
| R09 | Existing non-transition golden vectors remain unchanged. |

### 19.3 Store admission and lifecycle

| ID | Acceptance requirement |
|---|---|
| S01 | Missing entity, SRG, STD, TRG, or required citation rejects. |
| S02 | Endpoint anchor/STD mismatch rejects. |
| S03 | Endpoint STD context mismatch rejects. |
| S04 | Parent with different transition or context rejects. |
| S05 | Duplicate, unsorted, self, missing, or cyclic parents reject. |
| S06 | One healthy root declares. |
| S07 | Same-root fork conflicts even with byte-identical effective bodies. |
| S08 | Identical healthy independent roots corroborate. |
| S09 | Different healthy root bodies conflict. |
| S10 | Current-tip withdrawal makes that root inactive. |
| S11 | Withdrawal of non-tip, missing record, TRG, TRW, or STD rejects. |
| S12 | Duplicate withdrawal and successor-after-withdrawal reject. |
| S13 | Historical replay before correction/withdrawal reproduces old conclusion. |
| S14 | Later STD correction does not invalidate stored historical TRD. |

### 19.4 Queries and revalidation

| ID | Acceptance requirement |
|---|---|
| Q01 | Four and only four transition query methods are public. |
| Q02 | Lookup distinguishes exact unregistered and registered anchors. |
| Q03 | Contextual query covers every conclusion truth-table row. |
| Q04 | Entity collection uses permanent exact subject only. |
| Q05 | Assertion lookup accepts only exact transition record prefixes. |
| Q06 | Registration/withdrawal assertions carry null declaration lifecycle fields. |
| Q07 | TRD activity covers current, superseded, and withdrawn. |
| Q08 | Endpoint state conclusion, exact pinned STD activity, and alignment cover every literal and precedence row. |
| Q09 | Superseded endpoint pin does not silently retarget or change TRD conclusion. |
| Q10 | Conflicted endpoint state never selects a pinned/current winner. |
| Q11 | All rows reference one material through strict indices. |
| Q12 | Forged conclusions, indices, findings, ordering, or alignment reject. |
| Q13 | Hidden extras, bool indices, cycles, and excessive depth reject deterministically. |
| Q14 | Serialized round-trip revalidates from plain content. |

### 19.5 Temporal and non-inference

| ID | Acceptance requirement |
|---|---|
| T01 | Model queries accept no cutoff or source selector. |
| T02 | No transition assessment/occurrence public symbol exists. |
| T03 | Two `matches` results cannot be passed to any transition API. |
| T04 | Temporal `change_class` creates no model or transition result. |
| T05 | Receipt/source timestamps do not affect transition declaration conclusion. |
| T06 | Staleness, cohort, continuity, persistence, and causality are never asserted. |
| T07 | Multiple matching states do not produce selection or transition. |

### 19.6 Preservation and reproducibility

| ID | Acceptance requirement |
|---|---|
| P01 | Existing 34 predecessor bytes and aggregate remain unchanged. |
| P02 | All accepted historical memberships replay exactly. |
| P03 | Existing binding, interpretation, temporal, source, PT, VP, BH, and ST artifacts remain unchanged. |
| P04 | Reverse predecessor copy order yields identical candidate outputs. |
| P05 | Base-only and all-extras clean columns produce identical results. |
| P06 | Full suite, compilation, focused paths, whitespace, status, and topology checks pass. |
| P07 | No transition-specific store, revision, cache, or mutable projection appears. |
| P08 | No push, merge, or unauthorized history operation occurs. |

## 20. Bounded synthetic-demo policy

### 20.1 Default policy

ST-002 does not require or authorize an authoritative demo append. Contract and
query tests should use disposable, synthetic two-state model fixtures created
through public APIs.

### 20.2 Current-ledger limitation

The authoritative 34-record model has one state identity. It cannot produce a
non-self transition. The following are forbidden ways to manufacture a demo:

- treat the same state as both endpoints;
- infer a second state from a constraint complement;
- create a state from a name, observed value, or classification;
- reuse one STD under a different state ID;
- weaken same-subject or exact-pin checks; or
- append a transition occurrence because observations differ.

### 20.3 Optional later demo prerequisite

An authoritative transition demo may begin only after a separate owner gate
accepts a legitimate second state identity, registration, and exact-context
declaration for the same subject. That prerequisite is not part of ST-002 and
must not be smuggled into a transition slice.

### 20.4 Candidate policy if prerequisite exists

A future owner-authorized candidate is bounded to exactly:

- one frozen `TransitionAnchor` allocated once;
- one TRG;
- one parentless TRD;
- zero TRW, corrections, forks, extra roots, occurrences, or assessments; and
- TRG then TRD append order.

Allocation, pre-append rehearsal, authoritative append, and final acceptance
remain separate gates. Reproductions consume the frozen anchor and never
remint.

### 20.5 Mandatory future demo disclaimer

Any future transition fixture or artifact must state:

> This is an illustrative synthetic ST-002 transition declaration fixture. A
> `declared` result means only that the selected model revision contains an
> admitted declaration connecting the exact pinned from-state and to-state
> declarations in the stated context. It does not claim that a real system is
> in either state, that either state is exclusive or complete, that the
> transition is enabled, executable, occurring, observed, or completed, or
> that temporal order establishes cause, control, safety, health, diagnosis,
> correctness, or recommended action.

It must also say that names, ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM,
BH declarations, semantic compatibility, CN satisfaction, ST matches, temporal
correlation, and observation changes did not create the transition. Displaying
endpoint observations beside a transition does not persist an occurrence.

## 21. Owner-gated implementation slices

### 21.1 Gate 0 — architecture acceptance

Owner accepts this proposal's capability boundary, identity policy, record
shape, vocabulary, and unresolved decisions. No code begins before this gate.

### 21.2 Slice A — identity, records, canonicalization, and store admission

Bounded work:

- `TransitionAnchor`, pattern, and minter;
- TRG/TRD/TRW contracts and public builders;
- evidence-reference extension for TRG/TRD only;
- canonical prefix/effective-body support;
- full-set store validation and deterministic indexes;
- lifecycle and historical replay tests; and
- documentation of the non-assessment boundary.

Stop for owner acceptance. No public transition queries and no demo identity.

### 21.3 Slice B — authoritative read-only disclosure

Bounded work:

- exact result contracts and literals;
- four public query methods;
- endpoint alignment derived through the accepted state model logic;
- outer-result hostile revalidation;
- truth-table and serialization coverage; and
- import/capability tests.

Stop for owner acceptance. No classification composition or assessment.

### 21.4 Slice C — integrated hardening and reproduction

Bounded work:

- adversarial tests from section 19;
- deterministic-order and reversed-copy checks;
- full historical replay;
- base-only/all-extras clean-checkout verification;
- full-suite and focused-path verification; and
- completion report for code/query readiness.

Stop for owner acceptance. The authoritative ledger remains 34 records.

### 21.5 Optional Slice D — separately authorized demo

Slice D does not exist unless the owner separately accepts a legitimate second
state prerequisite and then authorizes candidate-anchor allocation. It must
follow the pre-append, append, and final-acceptance gates in section 20.

### 21.6 Later milestone — temporal transition assessment

This is not an ST-002 slice. It starts from the prerequisites in section 10.4
and requires a new design review. It must not reinterpret ST-002 declarations
or old ST-001 results as occurrence evidence.

## 22. Explicit exclusions and known limitations

### 22.1 Explicit exclusions

ST-002 v1 does not implement:

- transition assessment or occurrence;
- transition families, state families, state spaces, or aggregate selection;
- cross-entity or self-transitions;
- parallel transitions with identical directed endpoints;
- trigger, event, guard, action, or effect semantics;
- executable state machines or automatic next-state selection;
- graph traversal, path finding, reachability, cycles, priority, arbitration,
  or routing;
- dwell, debounce, hysteresis, persistence, continuity, windows, interpolation,
  resampling, or freshness vetoes;
- commands, control, recommendations, safety, diagnosis, health, fault,
  correctness, or causal conclusions;
- hidden transition fields on SRG, STD, STW, classification, CN, BH, temporal,
  binding, interpretation, port, or relationship records;
- a transition-specific database, ledger, revision, cache, artifact store, or
  mutable projection; or
- authoritative demo modification without separate owner authority.

### 22.2 Known limitations

- A declared transition possibility can reference endpoint STD meanings that
  are later superseded; alignment discloses this but does not auto-correct it.
- The model can declare a directed relation but cannot say whether it is
  enabled or physically possible now.
- Rejecting duplicate endpoint tuples prevents parallel edges until a later
  accepted differentiating semantic exists.
- Rejecting self-transitions postpones eventful re-entry semantics.
- Same-subject restriction postpones workflows or transfers between entities.
- No query lists outgoing/incoming graph adjacency; entity collection is the
  only bounded collection query.
- The current authoritative demo cannot represent a valid v1 transition
  without a separately admitted second state.

### 22.3 Compatibility promise

No ST-001 record gains a transition field. Existing state record identity,
canonical bytes, classification contracts, and all accepted memberships remain
unchanged. ST-002 consumes exact state declarations by reference; it does not
reinterpret or rewrite them.

## 23. Genuine unresolved owner decisions

The following decisions materially change the contract and require owner
answers before Slice A.

### Q1. Ratify the declaration-only milestone boundary?

**Recommendation:** yes. Keep ST-002 v1 to identity, TRG/TRD/TRW lifecycle, and
authoritative model disclosure. Assign evidence-consistency assessment and
occurrence to a later temporal cohort/continuity milestone.

Alternative: expand ST-002 to design and implement the lower temporal contract
first. That would be a materially larger milestone and this proposal would
need revision before implementation.

### Q2. Restrict v1 to same-subject endpoints?

**Recommendation:** yes. Both endpoint SRGs must name the exact TRG subject.
Defer cross-entity workflows or transfers even when hierarchy or relationships
connect the entities.

Alternative: admit cross-entity endpoints, which requires a new permanent
subject/participant policy and collection semantics not specified here.

### Q3. Reject self-transitions in v1?

**Recommendation:** yes. Without event, trigger, action, or re-entry semantics,
a self-transition has no honest disclosed distinction from a state declaration.

Alternative: permit them as opaque directed declarations, accepting that v1
cannot explain what makes one meaningful.

### Q4. Enforce one transition identity per ordered same-subject endpoint tuple?

**Recommendation:** yes. Multiple authorities should use independent TRD roots
under one transition identity. Revisit parallel identities only when a future
accepted trigger/event/action discriminator can distinguish them.

Alternative: permit duplicate anchors for the same tuple, accepting that v1
has no semantic field that distinguishes them.

### Q5. Keep state families and context mapping out of v1?

**Recommendation:** yes. Endpoints are exact StateAnchors, and both endpoint
STDs must use the exact TRD context. No family, exclusivity, completeness, or
cross-context resolution is inferred.

Alternative: add family-relative endpoints or context mapping, which requires
new identity, lifecycle, winner, and ambiguity contracts before Slice A.

### Q6. Keep endpoint pin alignment orthogonal to TRD conclusion?

**Recommendation:** yes. A current TRD remains `declared` even when its exact
STD pin is `superseded`; the result exposes both facts and never silently
retargets.

Alternative: mark the whole transition inactive or stale when either endpoint
pin is no longer current. That would conflate transition lifecycle with state
correction and add a new implicit invalidation policy.

### Q7. Keep the authoritative demo at 34 records through ST-002 by default?

**Recommendation:** yes. Use disposable two-state fixtures. Consider a demo
only after separately accepting a legitimate second state prerequisite and
authorizing the full candidate gate sequence.

Alternative: authorize a second state as part of ST-002, which expands scope
beyond transition architecture and requires its own state-design evidence.

### Q8. Ratify the exact vocabulary and prefixes?

**Recommendation:** accept `trn_`, `trg_`, `trd_`, and `trw_`; the four query
names in section 11; and the literal sets in section 12. This keeps transition
concepts distinct from `sta_`/`srg_`/`std_`/`stw_` and avoids occurrence-like
language.

## 24. Proposed acceptance statement

If the owner answers the questions above as recommended, the architecture gate
may be recorded as:

> ST-002 architecture is accepted as a model-only transition identity and
> declaration-disclosure milestone. It adds opaque same-subject directed
> transition identity, evidence-bearing TRG/TRD/TRW lifecycle, exact endpoint
> STD pins, deterministic replay, and authoritative read-only kernel results.
> It adds no transition assessment or occurrence, makes no inference from
> changed observations or ST classifications, leaves the authoritative
> 34-record ledger unchanged unless separately authorized, and defers all
> temporal cohort/continuity semantics to a later owner-gated milestone.

No implementation, identity allocation, candidate preparation, or ledger
change is authorized by accepting this proposal alone. Each implementation
slice remains separately owner-gated.

END OF ST-002 CODEX LEAD PROPOSAL
