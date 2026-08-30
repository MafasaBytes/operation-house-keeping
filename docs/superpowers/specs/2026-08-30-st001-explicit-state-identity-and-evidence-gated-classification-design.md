# ST-001 — Explicit State Identity and Evidence-Gated Classification

Status: Slices A and B are owner accepted. Slice C is implemented and adversarially reviewed; awaiting owner acceptance. Slice D remains unstarted and unauthorized.

Date: 2026-08-30

Repository baseline: `main` at `0ed77df7ea4870faec1eae9b89668add97aa855d`

Scope: design and contracts only; this document authorizes no implementation,
test, fixture, ledger, branch, or history change

## 1. Source integrity and repository findings

### 1.1 Reviewed sources

This synthesis reconciles these complete, independently authored proposals:

1. `docs/superpowers/proposals/2026-08-30-st001-codex-lead-proposal.md`
2. `docs/superpowers/proposals/2026-08-30-st001-kimi-k3-challenger-proposal.md`

The Codex proposal is the architectural foundation, as owner-adjudicated.
Challenger ideas are incorporated only where they improve naming, disclosure,
or boundary precision without changing the fixed entity-scoped architecture.

The complete Kimi file reviewed from disk has SHA-256:

```text
b701dab533c3340d085428185b3661ba1a2396c55ec86a760708d93197a5707b
```

Its earlier delivery receipt claimed:

```text
3ff7c9555841625911d5808eef8851c54df5808e707f8706a8fcca1eee611f47
```

Those values do not match. This is recorded as a source-receipt integrity
mismatch, not as a content judgment. The complete on-disk file identified by
`b701...a5707b` is the challenger source reviewed here.

The complete Codex source reviewed from disk has SHA-256:

```text
4eb466e89af0203ccd6a2ffc7a1b0feb762d69b575e5286ce0cfeb549077a8f1
```

### 1.2 Verified repository boundary

The repository facts constraining this design are:

- `HEAD`, `main`, and `origin/main` are accepted at
  `0ed77df7ea4870faec1eae9b89668add97aa855d`.
- The authoritative demo model contains exactly 32 model-record JSON files.
- Its accepted model revision is
  `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
- The repository has no state anchor, state registration, state declaration,
  state withdrawal, state query surface, state-classification package,
  transition identity, or state-machine execution contract.
- The model kernel is the accepted append-only ledger for explicit model
  knowledge. There is one model revision mechanism, `mrv_`.
- Read-only compositions sit above the kernel and preserve import direction.
- `ConstraintEvaluationQueries.constraint_evaluation()` is the accepted
  public facade for source-backed numeric constraint evaluation.
- `ModelQueryMaterial` is the accepted carry-once, store-independent,
  hostile-revalidation pattern for kernel query results.
- Computed CN and BH results are not persisted as model or temporal truth.

This synthesis changes none of those facts.

### 1.3 Explicit historical model memberships

The accepted history is represented by explicit membership constants, never
by directory enumeration:

| Records | Milestone | Revision |
|---:|---|---|
| 9 | MK-001 | `mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d023e3da83227f` |
| 10 | VM-001 | `mrv_105658072294bad92f83e3d536863cb46d6d7ae83f271fb59d5026839d002686` |
| 11 | VS-001 | `mrv_25afc0ebf17ed12bd6ef0a95795798a53ef2731983410136d3da15c4d0f98093` |
| 14 | SN-001 | `mrv_702c840f7da00617feb1be252838105d8b001b2e19978842bdcbec56996c99ff` |
| 16 | ES-001 | `mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a40099e8032ca8135b` |
| 18 | CN-001 | `mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51` |
| 28 | PT-001 | `mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2` |
| 29 | VP-001 | `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652` |
| 32 | BH-001 | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |

Every one must retain its exact record IDs, bytes, and revision after ST-001.
Pre-ST replay must return structured state absence, never migrated or inferred
state knowledge.

### 1.4 Existing model and evidence facts useful to a bounded demonstration

The accepted 32-record model contains:

- five registered entities;
- two registered variables, both with embedded owner
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- one current numeric VSP, quantity-kind declaration, and observation-role
  declaration for `var_b7e2d3c4f5a6172839405a6b7c8d9e0f`;
- permanent constraint anchor
  `con_4b768cf843f5474cb5e564e31d239a59` targeting that variable;
- current constraint declaration
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`
  with an inclusive exact numeric upper bound of `80`;
- an accepted explicit source path whose latest observation at the established
  demonstration cutoff is `60.4` and whose CN result is `satisfied`;
- a separate neutral BH variable deliberately lacking the lower evidence
  needed for source-backed evaluation.

The binding ledgers, interpretation fixture, temporal evidence, source data,
and structural evidence remain independently versioned and out of scope for
ledger mutation in ST-001 Slices A-C.

Accepted artifact hashes that any later Slice D must preserve include:

- CN: `161a7beba5b836246f8d0500bd286cff488cc18b037997a6d02548e7c107a5d9`;
- PT: `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP: `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH: `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.

### 1.5 Repository conventions that are binding on ST-001

ST-001 must preserve these accepted conventions:

1. System Identity owns opaque, frozen, extra-forbidden anchors and UUID4
   minters. A minter performs no registration, authority claim, or I/O.
2. Model-record IDs remain
   `<prefix>_<sha256(canonical record content excluding record_id)>`.
3. Existing record canonical bytes, schemas, IDs, and hashes never change.
4. Valid evidence and parent tuples canonicalize before hashing. Caller order
   cannot affect identity.
5. Loaded records and public results fully revalidate nested instances from
   serialized content; existing Pydantic instances are not trusted.
6. The kernel owns no source, binding, temporal, semantic, constraint-
   evaluation, behavior-evaluation, or state-classification dependency.
7. Explicit `SourceSelector` values select one accepted source path; they do
   not infer, rank, or create evidence.
8. Model state is latest per locator at or before an aware cutoff on the
   accepted receipt axis. It does not claim persistence or present physical
   truth.
9. Semantic compatibility performs exact declared-identity admission; it does
   not infer ontology or convert units.
10. CN owns numeric predicate evaluation and detailed CN refusal semantics.
11. BH establishes that upper result revalidation proves carried-material
    coherence, not raw-source authenticity.

## 2. Reconciliation and change log

### 2.1 Decisions retained from the Codex foundation

The corrected synthesis retains these Codex architectural choices:

- first-class `StateAnchor` identity;
- entity-scoped state registration;
- a permanent constraint-anchor set and `all_of_constraints` condition family;
- exact VCN pins in correctable contextual declarations;
- the existing model ledger and `mrv_` revision;
- minimal withdrawal events;
- BH-style correction DAGs, independent-root corroboration, and conflict;
- exactly four read-only kernel queries;
- classification by composing the public CN facade;
- explicit source selection per permanent condition;
- independent latest-at-or-before-cutoff temporal semantics;
- a three-valued all-of truth table;
- store-independent authoritative reconstruction;
- a two-record, 32-to-34 bounded demonstration;
- four separately owner-gated implementation slices.

### 2.2 Corrections to the Codex proposal

Owner adjudication makes these corrections normative:

1. The upper package is named `backend/state_classification`, not
   `backend/state_evaluation`.
2. Its facade is `StateClassificationQueries`, and its error/result type names
   use “Classification” consistently.
3. A `StateConditionSource` has no caller-provided entity override. The SRG's
   permanent `subject_entity_anchor_id` is authoritative and is forwarded to
   every CN branch.
4. Every permanent constraint must target a variable whose embedded owner is
   exactly the subject entity. Cross-entity conditions are not admitted in v1.
5. Classification of a declared state does not require exactly one current
   STD record. Multiple healthy independent roots with the same effective
   body form one admitted effective-body group and corroborate.
6. The no-current-tip aggregate conclusion is `inactive`; inactive roots are
   disclosed beside any active roots.
7. Exact status names are `matches` and `does_not_match`, not `matched` and
   `not_matched`.
8. There are no implementation-blocking owner questions in the corrected
   design.

### 2.3 Challenger improvements incorporated

The synthesis accepts these challenger improvements:

- the package term “classification,” which better distinguishes a read-only
  conclusion from model declaration and temporal evidence;
- particularly explicit vocabulary prohibitions against FSM, health, fault,
  and operating-state readings;
- the statement that independent-root corroboration never merges identity;
- explicit recognition that a fully coherent lower-evidence mutation may be
  outside upper store-independent detection;
- threat-model emphasis on DAG attacks, nested forgeries, and denial of
  service;
- a clear requirement that demonstration prose be synthetic and neutral.

These improvements are incorporated within the owner-fixed entity-scoped,
constraint-pinned design, not the challenger's variable-scoped model.

### 2.4 Challenger elements explicitly rejected

The following challenger elements are superseded and are not normative:

- state identity belonging only to one variable;
- a declaration that follows a constraint anchor's newest VCN automatically;
- directly embedding or privately evaluating CN predicates in ST;
- bypassing `ConstraintEvaluationQueries` and using only CN's parser;
- a `numeric_membership_via_constraint` criterion that lacks exact VCN pins;
- arbitrary `fresh | aging | stale` classes or 300/3600-second thresholds;
- `matched_state_anchor_ids` or another aggregate rollup;
- optional multi-context classification;
- an inline numeric interval arm in v1 or a predeclared “v1.5” arm;
- `states_of_variable()` as the reverse kernel query;
- a variable-wide classifier or implicit source discovery;
- a state family or state space;
- three demo records and an incorrect 32-to-35 record evolution.

They may appear here or in exclusions only to document adjudication. They do
not define ST-001 behavior.

## 3. Core problem, terminology, and truth boundaries

### 3.1 Core problem

ST-001 must make the smallest honest addition that permits the model to say:

> In this selected model revision, an accountable authority registered this
> named state identity for this entity over this permanent set of model
> constraints, and in this exact assertion context declared the state region
> by pinning these exact constraint declarations.

It must separately permit a read-only classifier to say:

> At this temporal cutoff, the explicitly selected evidence produced these
> independently disclosed CN outcomes; under the admitted state declaration's
> all-of rule, the evidence matches or does not match the declared region.

The first statement is model knowledge. The second is a derived,
revision-relative, evidence-relative conclusion. Neither is a transition or a
persisted physical state.

### 3.2 Exact definitions

**State identity** is an opaque `StateAnchor`. It supplies continuity across
renames and declaration correction but contains no subject, condition, context,
evidence, lifecycle, or transition meaning.

**State registration** is the one permanent model record that binds a state
anchor to one registered entity, a complete set of 1–64 constraint anchors,
and the `all_of_constraints` family.

**State declaration** is a context-specific, evidence-bearing positive claim
that pins the exact VCN record governing each permanent condition and selects
the fixed independent-latest evaluation basis.

**Declaration lifecycle** is membership-relative correction, conflict,
corroboration, inactivity, and withdrawal disclosure over STD records.

**Condition result** is the authoritative CN result for one registered
constraint and one explicit source selector.

**Classification** is the pure all-of conclusion derived from the admitted
state declaration and the carried CN results.

**Match** means only that the admitted all-of expression evaluates true under
the stated revisions, context, selectors, and cutoff.

**Does not match** means only that at least one admitted conjunct is false.
It does not identify another state.

### 3.3 Mandatory non-claims

No ST-001 record or result asserts or implies:

- that an observation is a state;
- that an entity is currently or physically “in” a state;
- that a value change is a state transition;
- transition identity, from/to direction, trigger, event, guard, or action;
- causality, control, command, influence, flow, or behavior;
- simultaneity, clock synchronization, observation persistence, or ordering;
- mutual exclusivity, completeness, ranking, or a winning state;
- health, safety, correctness, fault, alarm, diagnosis, or recommendation;
- that failing to match state A establishes state B;
- that matching names, owners, hierarchy, CAD, ports, VPA, topology, semantic
  compatibility, constraint satisfaction alone, temporal correlation, or BH
  behavior created a state declaration.

Multiple registered states may match the same evidence simultaneously. That is
ordinary independent disclosure, not a conflict unless their declaration
lineages themselves meet the exact conflict rules in Section 9.

## 4. Alternatives and adjudication

### 4.1 Generic relationship or variable attribute — rejected

A generic relationship loses a stable state-specific identity, exact
condition closure, contextual correction lineage, and tailored evidence rules.
A variable attribute incorrectly makes a system/component state just another
variable annotation and cannot honestly express a region over several
entity-owned variables. Neither representation supplies the required
classification boundary.

### 4.2 Constraint-evaluation output only — rejected

CN already answers whether an admitted observation satisfies one numeric
predicate. It does not create a named entity state, evidence for registering
that region, a permanent multi-condition set, contextual lifecycle, or
independent corroboration. Treating CN output itself as state would collapse
declaration truth into computation and would silently promote variable regions
to component/system state.

### 4.3 First-class entity state with constraint-referenced declarations — accepted

This is the recommended architecture. It adds identity and explicit model
knowledge without duplicating numeric logic. Registration fixes one entity and
its permanent condition set. Contextual declarations pin exact CN declarations.
The classifier composes public CN results without importing evaluation into the
kernel.

### 4.4 State family or state space — rejected for v1

No accepted evidence establishes exclusivity or completeness. A family would
invite ranking, “current state,” or FSM semantics without a supported claim.
ST-001 therefore has no state-family identity, membership record,
exclusive/complete flag, or family query. Multiple states remain independent.
Any future family concept requires a new owner-gated design and must not change
existing ST-001 meaning retroactively.

### 4.5 Direct predicates duplicated inside state declarations — rejected

Copying bounds or operators into STD would fork CN's numeric semantics,
canonical decimal limits, parser defenses, and refusal vocabulary. ST-001 pins
exact `vcn_` identities and invokes the public CN facade. Conditions CN cannot
express are honestly unsupported.

### 4.6 Executable state machine — rejected and assigned to ST-002

Transitions, from/to arcs, triggers, events, guards, actions, dwell time,
hysteresis, next-state selection, and execution are not state identity or
classification. They are wholly deferred to ST-002. ST-001 adds no preparatory
transition fields.

### 4.7 Separate ledger, store, or persisted classifier — rejected

State declarations are model knowledge and fit the existing model ledger.
Classification is a read-only composition. A new ledger, store, projection,
cache, database, or persisted result would add a second truth source and a
new revision without need.

## 5. Exact identity contracts

### 5.1 Prefix and public contract

Add one opaque identity kind:

```python
STATE_ANCHOR_ID_PATTERN = r"^sta_[0-9a-f]{32}$"

class StateAnchor(...):
    anchor_id: Annotated[str, pattern=STATE_ANCHOR_ID_PATTERN]
    namespace: BoundedName
    display_name: BoundedText
    role_name: BoundedName | None = None
```

The exact concrete bounded types must reuse the current System Identity anchor
conventions rather than inventing new coercion or length semantics. The model
is frozen, extra-forbidden, and uses full nested-instance revalidation.

The anchor contains no:

- entity, variable, constraint, context, condition, or evidence;
- owner, hierarchy, role semantics, exclusivity, or completeness;
- lifecycle, recorded time, authority, declaration, or withdrawal;
- transition, source, observation, temporal, or computed fields.

Human-facing names aid disclosure only. They do not establish identity,
condition meaning, matching, or classification.

### 5.2 Public minter

Add exactly:

```python
def mint_state_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> StateAnchor:
    ...
```

The minter calls standard-library `uuid4()` once, uses `uuid4().hex`, prefixes
it with `sta_`, constructs the existing public contract, and returns it. It
performs no I/O, storage, lookup, registration, authority assertion, timestamp
capture, deterministic seeding, name-derived identity, or persistence.

### 5.3 Continuity, rename, and replacement

The embedded anchor in one SRG is the authoritative human-facing naming
snapshot for that state identity. Names and role metadata do not create a
second identity and do not participate in condition comparison.

The following require a new state anchor and SRG:

- changing the subject entity;
- changing any member of the permanent constraint-anchor set;
- changing `all_of_constraints` to any other condition family.

Changing exact VCN pins within the same permanent anchor set is a declaration
correction within the same `(state_anchor_id, context)` lineage. Claims in a
different context are independent roots under a different lineage key.

## 6. Exact model-record contracts and canonical integration

### 6.1 Prefixes, kinds, evidence eligibility

Add exactly:

| Prefix | Record kind | Citable as `ModelRecordEvidence` |
|---|---|---|
| `srg_` | `state_registration` | yes |
| `std_` | `state_declaration` | yes |
| `stw_` | `state_declaration_withdrawal` | no |

All three prefixes enter the canonical model-record ID grammar, filename
grammar, discriminator-to-prefix mapping, and `ModelRecord` union. Only `srg_`
and `std_` enter `ModelRecordEvidence`. Existing discriminators, bytes,
schemas, hashes, and mappings remain unchanged.

### 6.2 `StateRegistration`

```python
class StateRegistration(...):
    record_kind: Literal["state_registration"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^srg_[0-9a-f]{64}$"]

    anchor: StateAnchor
    subject_entity_anchor_id: EntityAnchorId
    condition_constraint_anchor_ids: CanonicalStateConstraintAnchorIdTuple
    condition_family: Literal["all_of_constraints"]

    evidence: NonEmptyCanonicalEvidenceTuple
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: BoundedText
```

`condition_constraint_anchor_ids` contains 1–64 distinct valid constraint IDs,
canonicalized lexicographically. Reversed valid caller order yields identical
canonical bytes and record ID. Empty, duplicate, oversized, malformed, or
coercible values reject.

The registration has no context, parents, lifecycle, withdrawal, outcome,
source selector, temporal cutoff, transition, or computed state. It is
permanent. A second registration for the same `sta_`, identical or divergent,
is invalid.

### 6.3 `StateConstraintDeclarationPin`

```python
class StateConstraintDeclarationPin(...):
    constraint_anchor_id: ConstraintAnchorId
    constraint_declaration_record_id: VariableConstraintDeclarationId
```

A declaration contains a canonical tuple of these pins, unique and sorted by
`constraint_anchor_id`. A pin is an exact content identity. It is not an
instruction to find the newest declaration later.

### 6.4 `StateDeclaration`

```python
class StateDeclaration(...):
    record_kind: Literal["state_declaration"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^std_[0-9a-f]{64}$"]

    state_anchor_id: StateAnchorId
    context: AssertionContext
    conditions: CanonicalStateConstraintDeclarationPinTuple
    evaluation_basis: Literal["independent_latest_at_or_before_cutoff"]

    evidence: NonEmptyCanonicalEvidenceTuple
    supersedes: CanonicalStateDeclarationIdTuple
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: BoundedText
```

The pin tuple must equal the SRG's permanent constraint-anchor set exactly:
one pin for every anchor and no missing, extra, duplicate, or substituted
anchor. Every pinned ID must be a `vcn_` in the selected membership and must
declare the corresponding `con_`.

STD contains no inline predicate, bounds, unit conversion, state family,
exclusivity, transition, source selector, cutoff, observation, match, or
persisted classification.

### 6.5 `StateDeclarationWithdrawal`

```python
class StateDeclarationWithdrawal(...):
    record_kind: Literal["state_declaration_withdrawal"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^stw_[0-9a-f]{64}$"]

    withdraws: StateDeclarationId
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: BoundedText
```

It has no evidence, context, parents, outcome, reason code, replacement,
alternate target, or negative state claim. Context and subject are inherited
only for lifecycle disclosure from the target.

A withdrawal means only:

> This positive state declaration tip is no longer asserted in this selected
> model membership.

It does not mean the state was false, impossible, exited, or physically
removed. `stw_` is not citable.

### 6.6 Canonical identity behavior

Record IDs remain:

```text
<prefix>_<sha256(canonical record content excluding record_id)>
```

ST canonicalization must:

1. reject malformed IDs before indexing;
2. reconstruct nested anchors, contexts, pins, evidence, parents, authority,
   and timestamps from serialized content;
3. canonicalize valid evidence, pins, constraint IDs, and parent tuples;
4. reject duplicate parents and self-supersession;
5. derive identical IDs regardless of valid caller order;
6. reject stale IDs after any content mutation;
7. preserve every existing record's canonical bytes and ID.

No new canonical serializer or revision algorithm is introduced.

## 7. State subject, ownership, family, and exclusivity

### 7.1 Permanent entity subject

A first-class ST-001 state belongs permanently to exactly one registered
entity. It does not belong to one variable, one port, one VPA, one behavior,
one source, one observation, or the model revision itself.

The SRG's `subject_entity_anchor_id` is authoritative. For v1, every referenced
constraint registration must target a registered variable whose embedded
`VariableAnchor.entity_anchor_id` is exactly equal to the state subject.

This comparison is direct identity equality. The store must not infer scope
from hierarchy, common ancestors, relationships, names, namespace, CAD,
ports, VPA, interface topology, behavior, observations, or shared ownership
facts elsewhere. A condition whose target variable owner differs rejects the
model collection. Cross-entity conditions are deferred.

Shared ownership does not create a state, prove a condition set, strengthen
evidence, or make states exclusive.

### 7.2 No family, state space, exclusivity, or completeness in v1

ST-001 adds no family or space anchor and no grouping record. There is no
exclusive, exhaustive, default, fallback, priority, winner, or preferred
state contract.

Multiple state identities for the same entity may have overlapping constraint
regions and may match simultaneously. Independent-root corroboration concerns
multiple declarations of one state identity; it does not merge identities or
create a canonical region identity.

If exclusivity or completeness is needed later, it requires a separate,
explicit, evidence-bearing owner-gated contract. Existing ST-001 records must
not acquire that meaning retroactively.

## 8. Condition representation and CN boundary

### 8.1 V1 condition family

ST-001 supports exactly:

```text
all_of_constraints
```

The permanent SRG supplies the complete unordered constraint-anchor set. The
contextual STD supplies one exact VCN pin per anchor. Classification applies
logical all-of over the independently obtained public CN outcomes using the
truth table in Section 12.

There is no `any_of`, negation, nested group, weighting, ranking, expression,
operator graph, or user-defined predicate in v1.

### 8.2 Why exact VCN pins are necessary

A constraint anchor supplies continuity across CN correction. That is useful
for constraint identity but insufficient for state-declaration meaning. If an
STD referenced only `con_`, a later VCN correction could silently move the
state region without a state authority making a new contextual claim.

Therefore each STD pins exact `vcn_` identities. Later CN correction never
silently redefines the state. Classification contributes a condition only
when the uniquely current CN declaration is exactly the pinned record.

Pin states are:

- absent constraint registration: `not_registered`;
- no current CN declaration: `not_declared`;
- conflicted CN declaration: `conflicted`;
- unique current CN declaration differs from pin: `superseded`;
- unique current CN declaration equals pin: `exact_current`.

CN conflict remains conflict even if one conflicted tip equals the pin. ST
does not rank or pick it.

Under accepted CN-001 semantics, two or more current VCN tips make
`ConstraintDeclarationResult.status == "conflicted"` regardless of whether
their predicates, expected semantic signatures, or any other engineering-body
content are identical. CN-001 has no effective-body grouping,
identical-body corroboration, or independent-root agreement mechanism. ST must
never compare, merge, or treat identical VCN tips as corroborating.

When CN is conflicted, ST pin alignment is `conflicted`, no condition outcome
contributes, and `condition_declaration_conflicted` is emitted. This remains
true when one or every conflicting tip has the same engineering body as the
pinned declaration.

The strict asymmetry is intentional. Independent identical STD roots may
corroborate under ST’s explicitly defined lifecycle, while identical current
VCN tips remain conflict under accepted CN-001. ST-001 does not modify or
reinterpret CN lifecycle semantics. Any future CN corroboration would require
a separate owner-gated CN repair milestone.

### 8.3 Public CN composition only

`backend/state_classification` injects and calls the public
`ConstraintEvaluationQueries.constraint_evaluation()` facade exactly once per
registered condition. It does not:

- import or copy the CN parser;
- reproduce CN gate order, decimal logic, predicate comparison, or refusals;
- reach through CN into semantic, model-state, binding, interpretation, or
  temporal internals;
- evaluate an old pinned predicate when CN's current declaration differs;
- reinterpret `satisfied` as safety, compliance, health, or validity.

The complete CN result is carried unchanged. ST maps only its authoritative
outcome into the condition row after exact pin alignment.

### 8.4 Honestly unsupported conditions

If CN-001 cannot express a desired condition, ST-001 cannot classify it. V1
does not support categorical equality, strings, booleans, null membership,
sets, enums, text patterns, temporal duration, rate of change, hysteresis,
history, external models, arbitrary expressions, or cross-variable formulas.

No inline criterion or reserved v1.5 union arm is added. A future condition
family needs a separately owner-gated design and new explicit discriminator;
it must not reinterpret existing `all_of_constraints` records.

### 8.5 Independent meanings

These facts remain separate:

- SRG establishes permanent state identity and condition scope;
- STD establishes a contextual positive state-region declaration;
- VCN establishes one constraint predicate;
- CN evaluates one selected observation against one constraint;
- ST classification applies the declared all-of expression;
- temporal evidence remains an observation, not a state;
- a match remains a computed conclusion, not persisted model truth.

## 9. Evidence, store admission, lifecycle, and indexes

### 9.1 Registration evidence and reference closure

For every `StateRegistration`, the selected membership must contain:

- the exact registered subject entity;
- one and only one SRG for the state anchor;
- every exact referenced `ConstraintRegistration`;
- each constraint's registered target variable and registered embedded owner;
- exact embedded-owner equality between every target variable and the subject;
- `ModelRecordEvidence` citations to the subject entity registration and every
  referenced CRG;
- at least one claim-bearing `OwnerDeclarationEvidence` stating that the
  authority registers this entity/condition skeleton as a named state;
- closure for every additional model-record evidence reference.

Evidence tuples are nonempty and canonical. A tuple containing only
registration citations and no claim-bearing arm is insufficient. Names,
ownership equality, hierarchy, topology, VPA, behavior, constraint
satisfaction, observations, and temporal correlation neither create nor
strengthen the registration claim.

### 9.2 Declaration evidence and reference closure

For every `StateDeclaration`, the selected membership must contain:

- exactly one matching SRG;
- exactly one pin for each permanent constraint and no extra pin;
- every exact pinned VCN and its corresponding CRG;
- `ModelRecordEvidence` citations to the SRG, every referenced CRG, and every
  pinned VCN;
- at least one claim-bearing `OwnerDeclarationEvidence` supporting the exact
  contextual declaration and evaluation basis;
- every parent STD and every cited model-record dependency.

The store validates pin existence and con↔VCN coherence, not membership-
relative VCN currentness. A later valid VCN correction must not retroactively
invalidate an earlier append-only state record. Currentness, conflict, and pin
alignment are query/classification data.

### 9.3 Registration and declaration admission failures

The store rejects:

- an unregistered subject entity;
- zero, duplicate, malformed, or more than 64 condition anchors;
- unknown or wrong-kind constraint registrations;
- an unregistered target variable or owner;
- any target variable whose embedded owner differs from the subject;
- a second SRG for one state anchor, agreeing or divergent;
- missing, extra, duplicate, substituted, wrong-kind, or cross-constraint VCN
  pins;
- non-claim-bearing or dangling evidence;
- a parent of the wrong record kind, state anchor, or exact context;
- duplicate parents, self-supersession, cross-root convergence, and cycles;
- invalid withdrawal targets under Section 9.6.

Every failure is typed through the existing model-validation error boundary.
Atomic append writes nothing if the prospective full membership is invalid.

### 9.4 Lineage key, roots, and correction DAG

The lineage key is exactly:

```text
(state_anchor_id, exact AssertionContext)
```

Declarations in different contexts do not supersede, corroborate, or conflict
with one another. A parentless STD starts an independent root.

Within one root:

| Current membership shape | Root health | Meaning |
|---|---|---|
| no current tips | `inactive` | no positive tip is currently asserted |
| exactly one current tip | `healthy` | one current correction tip |
| two or more current tips | `conflicted` | unresolved same-root fork |

The rules are:

- a same-root fork conflicts even if fork bodies are identical;
- multi-parent convergence is allowed only within that root;
- partial convergence remains conflicted;
- complete convergence restores one healthy current tip;
- cross-root convergence is invalid;
- cycles and self-ancestry are invalid;
- no timestamp, authority, record ID, filename, or append order selects a tip.

### 9.5 Effective engineering bodies and independent roots

The effective engineering body contains exactly:

```text
state_anchor_id
exact AssertionContext
canonical constraint-anchor -> exact VCN pin mapping
evaluation_basis
```

It excludes:

```text
record_id
evidence
authority
recorded_at
note
supersedes
filename
append order
```

The subject entity, permanent constraint set, and all-of family resolve from
the unique SRG and are not duplicated in the body projection.

Across independent active roots for one lineage key:

- healthy roots with identical effective bodies corroborate;
- healthy roots with different effective bodies conflict;
- any active same-root conflict makes the aggregate declaration conflicted;
- inactive roots remain disclosed beside active roots;
- identical roots never merge state identity or create a canonical region;
- all evidence and authorities remain independently disclosed.

Classification operates on the unique admitted active effective-body group,
not on a requirement for exactly one current declaration record. Two or more
healthy independent roots with the same body are admissible corroboration.

### 9.6 Aggregate conclusion and withdrawal

The exact declaration conclusion is:

```python
StateDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]
```

| Registration / active shape | Conclusion |
|---|---|
| SRG absent | `not_registered` |
| SRG present, no exact-context roots | `not_declared` |
| roots exist, no current tips anywhere | `inactive` |
| same-root active fork exists | `conflicted` |
| two or more active effective-body groups exist | `conflicted` |
| exactly one active effective-body group, one or more healthy roots | `declared` |

An STW targets one current STD tip. Reject unknown, wrong-kind, registration,
withdrawal, superseded, non-tip, already-withdrawn, and duplicate targets.
Reject a membership where the same tip is both superseded and withdrawn.
Selective withdrawal of one fork tip is allowed. Historical replay that omits
a later STW revives its target relative to that explicit membership.

### 9.7 Immutable indexes

Extend `LoadedModel` with deterministically built, read-only indexes sufficient
to support validation and queries, including the conceptual mappings:

```text
state_registrations
state_registrations_by_anchor
state_anchor_ids_by_subject_entity
state_condition_constraint_ids_by_anchor
state_declarations
state_declaration_ids_by_key
state_declaration_parent_ids
state_declaration_successor_ids
state_declaration_root_by_id
current_state_declaration_tips_by_root
state_declaration_withdrawals
state_declaration_withdrawn_by
```

Concrete internal names may follow existing kernel naming conventions, but no
additional public API is implied. Mappings are immutable and values are frozen
records or canonical tuples. Reversed collection input, filesystem order,
append order, and hash seed must not change indexes or revision.

`ModelStore.append()` revalidates the current and prospective collections
before atomic promotion. ST adds no store, multiappend protocol, transaction
type, cache, or revision.

## 10. Exact read-only kernel query surface

### 10.1 Public `ModelQueries` methods

Add exactly:

```python
def state(
    self,
    state_anchor_id,
) -> StateLookupResult:
    ...

def state_declaration(
    self,
    state_anchor_id,
    *,
    context,
) -> StateDeclarationResult:
    ...

def states_of_entity(
    self,
    entity_anchor_id,
    *,
    context,
) -> EntityStatesResult:
    ...

def state_assertion(
    self,
    record_id,
) -> StateAssertionDisclosureResult:
    ...
```

There are no aliases, variable/port/family queries, bulk classifier, “current
state” query, transition query, graph traversal, discovery wrapper, or
persistence method. Each query operates only over one injected `LoadedModel`,
owns no store, performs no write, and carries `ModelQueryMaterial` exactly once.

### 10.2 Exact public kernel vocabularies

```python
StateLookupStatus = Literal[
    "not_registered",
    "registered",
]

StateDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]

StateDeclarationLineageSummary = Literal[
    "not_applicable",
    "healthy",
    "conflicted",
    "inactive",
]

StateAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]

EntityStatesStatus = Literal[
    "entity_not_registered",
    "registered",
]

StateAssertionLookupStatus = Literal[
    "not_found",
    "found",
]
```

Reuse the accepted `AssertionActivity` and `ContainingLineageHealth` aliases.
Do not add winner, preferred, exclusive, active-state, normality, health,
transition, validity, or safety vocabularies.

### 10.3 Lightweight indexed disclosure rows

```text
StateConditionReferenceResult
  condition_index
  constraint_anchor_id
  constraint_registration_index
  pinned_declaration_index
  target_variable_registration_index
  target_owner_registration_index

StateEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices
  conditions

StateDeclarationRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices
```

All indices are non-boolean strict integers greater than or equal to zero.
`condition_index` and `group_index` are contiguous from zero. Rows contain no
duplicate authoritative record. Convenience properties, if any, are read-only
and resolve only through carried material.

Deterministic ordering is:

- roots by root record ID;
- lineage records, current tips, and withdrawals by record ID;
- body groups by canonical effective-body bytes;
- conditions by constraint anchor ID.

Record IDs decide display ordering only and never select truth.

### 10.4 `StateLookupResult`

```text
StateLookupResult
  material
  state_anchor_id
  status
  registration_index
  subject_entity_registration_index
  condition_constraint_registration_indices
  condition_variable_registration_indices
  condition_owner_registration_indices
```

For `not_registered`, optional indices are `None` and tuples are empty. For
`registered`, condition tuples align exactly with the SRG's canonical
constraint tuple. Owner indices may repeat when several variables have the
same owner; the entity record appears only once in material.

### 10.5 `StateDeclarationResult`

```text
StateDeclarationResult
  material
  state_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices
```

Rules:

- absent registration → `not_registered` / `not_applicable` / empty rows;
- no exact-context root → `not_declared` / `not_applicable`;
- roots and no current tips → `inactive` / `inactive`;
- same-root fork or cross-root effective-body disagreement → `conflicted`;
- one active effective-body group across one or more healthy roots →
  `declared` / `healthy`;
- inactive roots remain disclosed and add `inactive_roots_present` without
  overriding an otherwise declared result;
- a healthy root never hides a conflicted root.

For corroborating roots, `current_declaration_indices` contains every current
tip in deterministic ID order. The effective-body group, not one chosen STD,
is the authoritative engineering declaration.

### 10.6 `EntityStatesResult`

```text
EntityStateEntry
  entry_index
  state_anchor_id
  state_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

EntityStatesResult
  material
  entity_anchor_id
  context
  status
  entity_registration_index
  entries
```

An absent entity returns `entity_not_registered`, `None`, and empty entries. A
registered entity with no state registrations returns `registered` and empty
entries. Include every state registered directly to that exact entity,
including not-declared, inactive, and conflicted states in the requested
context.

Entries are ordered by `state_anchor_id`, then first root ID as a deterministic
tie-break, with contiguous `entry_index` from zero. Entries are not inferred
from variable owners, hierarchy, constraint targets, names, ports, VPA,
behavior, sources, or observations.

### 10.7 `StateAssertionDisclosureResult`

```text
StateAssertionDisclosureResult
  material
  record_id
  lookup_status
  record_index
  activity
  containing_lineage_health
  containing_subject_conclusion
  containing_agreement_findings
  root_record_index
  successor_indices
  withdrawal_indices
```

It accepts valid `srg_`, `std_`, and `stw_` identities only. A valid-shaped
absent ID returns `not_found`, `None` lifecycle fields, and empty tuples. A
found SRG or STW has no declaration activity or root fields. A found STD has:

- direct successor → `superseded`;
- withdrawal → `withdrawn`;
- otherwise → `current`;
- independently recomputed containing-root health and subject conclusion;
- direct successors and withdrawals in record-ID order.

Conflict belongs to a root or subject, never to an individual STD. Malformed
or non-ST IDs raise typed `ModelQueryError` before any model index access.

## 11. Read-only state-classification architecture

### 11.1 Module and facade

Add a separate read-only package:

```text
backend/state_classification
```

It exposes one facade:

```python
class StateClassificationQueries:
    def __init__(
        self,
        constraints: ConstraintEvaluationQueries,
    ) -> None:
        ...

    def state_classification(
        self,
        state_anchor_id,
        *,
        context,
        as_of,
        condition_sources,
    ) -> StateClassificationResult:
        ...
```

No other public query method is authorized. In particular there is no bulk,
entity-wide, variable-wide, port, multi-context, transition, discovery,
ranking, recommendation, or persistence API.

The facade injects and composes the public `ConstraintEvaluationQueries`. It
owns no store, ledger, database, cache, projection, repository, path, socket,
or write capability.

The legal model-derivation path is exact: `StateClassificationQueries`
receives a public `ConstraintEvaluationQueries`; it reaches the same
`LoadedModel` through that injected facade’s public lower-facade chain; and it
constructs public `ModelQueries` over that exact membership. Concretely, the
accepted public chain is `constraints.semantic.compatibility.state.model`.
The classifier accesses no private foreign field and constructs no store.

### 11.2 Explicit condition source

```python
class StateConditionSource(...):
    constraint_anchor_id: ConstraintAnchorId
    source: SourceSelector
```

There is deliberately no entity override. For each CN call, the facade resolves
the state SRG's permanent subject entity and forwards that exact ID as CN's
requested entity. A caller cannot retarget a condition to another entity.

For a registered state, `condition_sources` must contain exactly one row for
each permanent constraint anchor, unique and canonically sorted by constraint
ID. Missing, extra, duplicate, malformed, substituted, or retargeted rows are
typed input misuse. Reversed valid input order canonicalizes.

For an unregistered state, only an empty source tuple is accepted. Without an
SRG there is no authoritative participant set against which nonempty source
rows could be validated.

There is no source discovery, candidate ranking, locator fallback, permutation
search, or cross-product.

### 11.3 Deterministic branch scheduling

For a structurally valid request:

1. validate the state ID, exact context, aware cutoff, and source-row shape;
2. obtain authoritative state lookup and exact-context declaration results
   from the same loaded model used by the injected CN stack;
3. if unregistered, require empty sources and return structured absence without
   invoking CN;
4. if registered, require exact source-set equality with SRG;
5. invoke each registered constraint branch exactly once, in canonical
   constraint-anchor order, with the exact same normalized cutoff and the SRG
   subject entity;
6. attempt all scheduled branches even when the state declaration is absent,
   inactive, or conflicted;
7. if typed lower failures occur, propagate the first failure in canonical
   constraint order unchanged after all scheduled attempts; fabricate no ST
   result;
8. carry every complete CN result exactly once;
9. if and only if the state has one admitted active effective-body group,
   derive exact VCN pin alignment and condition outcome for each branch;
10. derive coverage, temporal disclosure, refusals, execution, and optional
    match through Section 12's table;
11. persist nothing.

Multiple corroborating current declaration records with the same effective
body pass step 9. No representative record is treated as a winner; the body
group supplies the pins, and all roots/records remain disclosed.

### 11.4 Result contracts

```text
StateClassificationConditionResult
  condition_index
  constraint_anchor_id
  source_index
  constraint_evaluation_index
  candidate_index
  declaration_alignment
  outcome

StateClassificationRefusal
  reason
  condition_index

StateClassificationResult
  state
  state_anchor_id
  context
  as_of
  ruleset_version
  condition_sources
  constraint_evaluations
  conditions
  condition_coverage
  temporal_alignment
  execution
  refusals
  computed_match
```

`state` is one complete `StateDeclarationResult` and carries model material
once. Each complete CN result appears exactly once in
`constraint_evaluations`. Condition rows use strict indices and do not
duplicate occurrences, semantic results, bindings, decimals, predicates,
boundaries, evidence, or provenance.

`ruleset_version` is exactly `Literal["st001.1"]`. `candidate_index` is
`None` only when the corresponding CN result has no selected candidate.
`computed_match` is explicitly `None` unless execution reaches a mathematical
all-of conclusion.

### 11.5 Public errors and exact export surface

Public errors are:

```python
StateClassificationError
StateClassificationConfigurationError(StateClassificationError)
StateClassificationInputError(StateClassificationError)
```

Codes are:

```text
STATE_CLASSIFICATION_CONFIGURATION_INVALID
STATE_CLASSIFICATION_INPUT_INVALID
```

Direct Pydantic construction may raise ordinary `ValidationError`. Facade
construction and request misuse use the ST error tree. Ordinary absence,
conflict, inactivity, stale pins, CN refusal, and nonmatching are result data.
Typed lower exceptions propagate as the exact same class object and are not
wrapped, translated, or re-exported.

Pin `backend.state_classification.__all__` to exactly this ordered list:

1. `StateClassificationError`
2. `StateClassificationConfigurationError`
3. `StateClassificationInputError`
4. `StateConditionSource`
5. `StateConditionDeclarationAlignment`
6. `StateConditionOutcome`
7. `StateConditionCoverage`
8. `StateTemporalAlignment`
9. `StateClassificationExecution`
10. `StateComputedMatch`
11. `StateClassificationRefusalReason`
12. `StateClassificationRefusal`
13. `StateClassificationConditionResult`
14. `StateClassificationResult`
15. `StateClassificationQueries`

No CN parser, decimal contract, lower facade, derivation helper, alias, or
convenience wrapper is public through this package.

## 12. Exact classification status and truth contracts

### 12.1 Exact public literal vocabularies

```python
StateConditionDeclarationAlignment = Literal[
    "not_evaluated",
    "not_registered",
    "not_declared",
    "conflicted",
    "superseded",
    "exact_current",
]

StateConditionOutcome = Literal[
    "satisfied",
    "violated",
    "not_evaluated",
]

StateConditionCoverage = Literal[
    "not_evaluated",
    "complete",
    "incomplete",
]

StateTemporalAlignment = Literal[
    "not_evaluated",
    "not_asserted",
]

StateClassificationExecution = Literal[
    "not_executed",
    "executed",
]

StateComputedMatch = Literal[
    "matches",
    "does_not_match",
]
```

`computed_match` is `StateComputedMatch | None`. There is no `current`,
`active`, `in_state`, `consistent`, `valid`, `healthy`, `normal`, `safe`,
`fault`, `passed`, `failed`, or transition status.

### 12.2 Exact ordered ST refusal vocabulary

```python
StateClassificationRefusalReason = Literal[
    "state_not_registered",
    "state_not_declared",
    "state_inactive",
    "state_conflicted",
    "condition_not_registered",
    "condition_declaration_not_declared",
    "condition_declaration_conflicted",
    "condition_declaration_superseded",
    "condition_evaluation_not_evaluated",
]
```

ST refusals identify only state lifecycle, pin-alignment, or aggregate
condition-admission gates. Detailed CN reasons—observation absence, attachment,
semantic mismatch, value shape, numeric bounds, and so on—remain authoritative
and visible inside the carried CN result. ST neither renames nor duplicates
that taxonomy.

Refusals are sorted by the literal order above and then by condition index.
State-level reasons carry `condition_index=None`; condition-specific reasons
carry the exact canonical index. Every independently applicable reason remains
visible.

### 12.3 Pin-alignment table

For one admitted active STD effective body:

| Current CN declaration | Pin comparison | Alignment | Condition contribution |
|---|---|---|---|
| constraint absent | n/a | `not_registered` | none |
| registered, no declaration | n/a | `not_declared` | none |
| conflicted declaration | even if one tip equals pin | `conflicted` | none |
| unique current declaration | ID differs from pin | `superseded` | none |
| unique current declaration | ID equals pin | `exact_current` | authoritative CN outcome |

Under accepted CN-001 semantics, `ConstraintDeclarationResult.status` is
`conflicted` whenever two or more VCN tips are current. Tip predicate equality,
expected-semantic-signature equality, or equality of any other engineering
content does not change that status. CN-001 defines no effective-body grouping,
identical-body corroboration, or independent-root agreement. ST therefore
never compares or merges VCN tip bodies. A conflicted CN result always aligns
`conflicted`, contributes no condition outcome, and emits
`condition_declaration_conflicted`, even if one or every current tip has the
same body as the pinned VCN.

`superseded` is membership-relative alignment, not approval of the newer VCN
and not evaluation of the older one. CN has no inactive-declaration outcome.

The strict asymmetry is intentional. Independent identical STD roots may
corroborate under ST’s explicitly defined lifecycle, while identical current
VCN tips remain conflict under accepted CN-001. ST-001 does not modify or
reinterpret CN lifecycle semantics. Any future CN corroboration would require
a separate owner-gated CN repair milestone.

The exact alignment-to-condition-refusal ownership mapping is:

| Non-`not_evaluated` alignment | Corresponding condition-level refusal |
|---|---|
| `not_registered` | `condition_not_registered` |
| `not_declared` | `condition_declaration_not_declared` |
| `conflicted` | `condition_declaration_conflicted` |
| `superseded` | `condition_declaration_superseded` |
| `exact_current` | `condition_evaluation_not_evaluated` exactly when the carried CN outcome is `not_evaluated` |

The first four alignments always emit their mapped refusal. `exact_current`
with CN `satisfied` or `violated` emits no condition-level refusal; the fifth
reason is owned exclusively by `exact_current` with CN `not_evaluated`.

### 12.4 Exact all-of truth table

State lifecycle gates first. A state conclusion of `not_registered`,
`not_declared`, `inactive`, or `conflicted` always yields:

```text
condition_coverage = not_evaluated
execution = not_executed
computed_match = None
```

Registered CN branches still run and remain carried where an SRG exists.

For a `declared` state with one admitted effective-body group:

| Admitted outcomes | Other conditions | Coverage | Execution | Match |
|---|---|---|---|---|
| all `satisfied` | none | `complete` | `executed` | `matches` |
| one or more `violated` | all siblings evaluated | `complete` | `executed` | `does_not_match` |
| one or more `violated` | one or more unknown siblings | `incomplete` | `executed` | `does_not_match` |
| no `violated` | one or more unknown conditions | `incomplete` | `not_executed` | `None` |

This is exact three-valued conjunction. A false conjunct determines an all-of
expression even when another conjunct is unknown. Every unknown condition and
refusal remains disclosed. `does_not_match` proves neither another state nor
the negation of any unobserved condition.

### 12.5 Multiple matching states

Classification is one state identity per call. Two calls may independently
return `matches` for two states of the same entity. ST-001 intentionally offers
no aggregate result, matched-ID tuple, winner, preference, exclusivity check,
or completeness verdict. Consumers must not collapse independent results into
“the entity's current state.”

## 13. Temporal and source-selection policy

### 13.1 Model revision and cutoff are separate axes

The injected `LoadedModel` selects model membership explicitly. `as_of` is an
aware temporal receipt-axis cutoff passed to lower public facades. It never
selects, reconstructs, mutates, or reinterprets model membership.

The result keeps distinct:

- model revision inside `state.material.revision` and every CN result;
- binding revision inside lower model-state material;
- interpretation revision inside lower source-semantic material;
- temporal cutoff `as_of` normalized to UTC;
- each occurrence's source-native and receipt/resolution metadata;
- exact declaration `AssertionContext`.

`recorded_at` is audit time, not a validity interval or temporal selector.

### 13.2 Independent latest-at-or-before-cutoff basis

Every condition receives the same UTC-normalized cutoff and its own exact
`SourceSelector`. Each CN branch independently selects its latest evidence at
or before that cutoff through accepted lower layers.

The classifier reports `temporal_alignment="not_asserted"` whenever registered
condition branches are carried. If no branch exists because the state is
unregistered, it reports `not_evaluated`.

The fixed basis does not assert:

- acquisition-cohort equality;
- physical simultaneity or co-temporality;
- synchronized source clocks;
- source-time or receipt-time equivalence;
- acceptable skew;
- interpolation, resampling, lag compensation, or range search;
- value persistence after observation;
- causal or transition ordering.

### 13.3 Staleness and incomplete evidence

Exact lower-layer staleness, source time, receipt time, clock domain, candidate
status, and provenance remain carried unchanged. ST adds no freshness class,
hard-coded 300/3600-second threshold, max age, or silent veto.

Staleness does not by itself change `satisfied`, `violated`, `matches`, or
`does_not_match`. Missing/refused evidence is disclosed through the lower CN
result and ST's condition outcome/coverage. No historical fallback is tried.

Changing only context may change state-declaration lifecycle without filtering
temporal evidence. Changing only cutoff may change CN results without changing
the model revision or state roots.

## 14. Authoritative result reconstruction boundary

### 14.1 Kernel result reconstruction

Every public kernel result must:

1. reconstruct every material record from serialized field content;
2. validate every content-derived record ID and exact revision membership;
3. rebuild `LoadedModel` in memory without `ModelStore` or filesystem access;
4. recompute registrations, subjects, condition closure, exact owner equality,
   roots, ancestry, successors, tips, withdrawals, and root health;
5. recompute effective-body projections, groups, corroboration, conflict,
   aggregate conclusions, and agreement findings;
6. recompute every strict index and deterministic ordering;
7. reject missing, duplicate, extra, reordered, cross-context, mixed-revision,
   wrong-union-arm, or substituted content;
8. reconstruct nested objects rather than trusting Pydantic instances.

This rejects hostile `model_construct`, `model_copy`, stale-ID, forged index,
forged root, forged body-equivalence, forged finding, forged status, and
revision-substitution attacks at the public boundary.

### 14.2 Classification result reconstruction

`StateClassificationResult` must rebuild and rederive from carried content:

- the complete `StateDeclarationResult`;
- every complete CN result through its own public validation contract;
- exact request echoes and normalized cutoff;
- exact registered subject and condition-source set;
- canonical branch order and exactly-once result coverage;
- one unique admitted active effective-body group, allowing multiple
  corroborating healthy roots with the same body;
- every VCN pin and current declaration alignment;
- condition candidate index and CN outcome mapping;
- coverage, temporal alignment, refusals, execution, and optional match;
- deterministic serialization and no duplicate carried records.

It rejects mixed model, binding, interpretation, semantic, temporal, or cutoff
material; selector retargeting; subject substitution; candidate or occurrence
substitution detectable from carried data; forged conditions, indices, pins,
outcomes, refusals, execution, or relation; booleans used as indices; extra
fields; reordered sources; and nested forgeries.

Validation owns no store, filesystem, network, or write capability.

### 14.3 Inherited authenticity limitation

ST authoritative validation proves internal coherence of carried lower public
results and every ST-derived field. It inherits, and does not independently
re-prove, raw-source authenticity. A fully coherent lower-evidence content
mutation accepted by lower public contracts is outside ST's store-independent
detection boundary.

`payload_checksum` must not be described as authenticating an uncaptured
payload. Content-bound occurrence authentication remains separately
owner-gated future work. Slice C must create a new ST-specific disposable
coherent-mutation limitation test, modeled on the accepted BH methodology,
that exercises `StateClassificationResult` and demonstrates ST’s exact
carried-material authentication boundary. The BH test is precedent and may
supply reusable test patterns, but passing the BH test is not a substitute for
exercising ST composition. The ST test must demonstrate this boundary honestly
rather than claiming detection it cannot provide.

## 15. Import direction and architectural isolation

### 15.1 Permitted dependency graph

```text
system_identity
      ↑
model_kernel
      ↑
model_state / observation_compatibility / semantic_compatibility
      ↑
constraint_evaluation
      ↑
state_classification
```

Arrows indicate “may be depended on by the layer above.” Existing accepted CN
internals retain their current graph; ST does not create a new lower edge.

### 15.2 Permitted ST dependencies

`backend/state_classification` may import only public contracts/facades it
needs from:

- `backend.system_identity`;
- `backend.model_kernel`;
- `backend.model_state` only for already public selector/result types if the
  CN facade signature requires them;
- `backend.constraint_evaluation` public facade and result contracts;
- its own package, Pydantic, and the standard library.

It must use `ConstraintEvaluationQueries` as the evaluation seam. It must not
import a private CN parser, private decimal constructor, predicate evaluator,
or gate helper.

### 15.3 Forbidden imports and capabilities

Architecture tests must prove:

- `model_kernel` does not import state classification, model state, temporal
  state, identity binding, observation compatibility, semantic compatibility,
  constraint evaluation, behavior evaluation, source interpretation, data
  sources, structural evidence, CAD, or PDF;
- lower accepted modules do not import `state_classification`;
- state classification does not import stores, source connectors, ingestion,
  structural evidence, CAD, PDF, behavior evaluation, or private lower code;
- state classification does not construct a repository or access a private
  field of an injected foreign object;
- there is no filesystem, SQLite, network, environment, dynamic import, cache,
  path, or write capability;
- no classification result is persisted.

## 16. Historical replay, migration, and preservation

### 16.1 Structured absence before ST

Every accepted explicit 9/10/11/14/16/18/28/29/32-record membership replays
unchanged. For a canonical state ID absent from those revisions:

- `state()` returns `not_registered`;
- `state_declaration()` returns `not_registered` with empty lifecycle rows;
- `states_of_entity()` returns `registered` and empty entries for a registered
  entity, or `entity_not_registered` for an absent entity;
- `state_assertion()` returns `not_found` for a valid-shaped absent ST ID.

No migration, default state, inferred state, compatibility record, or synthetic
historical artifact is introduced.

### 16.2 Reference closure for ST memberships

An explicit membership containing an SRG must also contain:

- its subject entity registration;
- every constraint registration;
- every target variable registration and embedded owner registration;
- every model-record evidence dependency.

A membership containing an STD must also contain its SRG, exact pinned VCNs,
their CRGs, parents, and all evidence dependencies. A membership containing an
STW must contain its target and the target's closure.

Reference closure is evaluated against the explicitly selected membership,
not records discoverable in a directory.

### 16.3 Replay after correction or withdrawal

An older explicit membership omitting a later STD successor exposes the older
tip as current. An older membership omitting a later STW revives its target.
An older membership with the pinned VCN current may classify; a later
membership with a different current VCN exposes `superseded` until a new STD
correction explicitly pins it.

This is intentional. A corrected CN declaration does not silently rewrite the
state region, and historical membership is never reconstructed from timestamp,
append order, filename prefix, or directory contents.

### 16.4 Byte and artifact preservation

Slices A-C must change no committed model, binding, interpretation, temporal,
source, structural, PT, VP, or BH fixture. Slice D may append only after its
separate owner gate. All 32 predecessor model records and accepted artifacts
must remain byte-identical. Existing membership constants stay exact and gain
no directory-based reconstruction.

## 17. Security and denial-of-service model

### 17.1 Identity, content, and membership forgery

Threats include malformed or wrong-prefix identities, stale content-derived
IDs, filename/content mismatch, forged nested anchors and records, mixed
revisions, substituted evidence, wrong union arms, and coerced booleans.

Controls are exact identifier grammars, canonical serialization, complete
nested reconstruction, content-ID verification, exact explicit membership,
strict types, extra-field rejection, and reference closure before indexing.
No filename, timestamp, or append order is trusted as identity or truth.

### 17.2 DAG and lifecycle attacks

Threats include huge parent fan-out, duplicate parents, self-parenting, cycles,
cross-state or cross-context parents, cross-root convergence, concealed forks,
partial convergence presented as healthy, forged tips, double withdrawals, and
successor-plus-withdrawal races.

Controls are canonical unique parent tuples, existing ledger record/collection
bounds, root identity validation, exact-context lineage keys, complete tip
recomputation, and atomic full-collection append validation. State declaration
DAG validation uses an iterative explicit-stack three-colour traversal matching
the accepted model-kernel precedent. Recursive traversal is not permitted.
Traversal complexity remains bounded by the selected membership size.

### 17.3 Condition-set and branch-scheduling attacks

Threats include zero or more than 64 conditions, duplicates, reordered sources,
missing or extra selectors, cross-entity targets, substituted VCN pins, invoking
one condition repeatedly, candidate cross-products, hidden winner selection,
and early ordinary refusal suppressing later typed failures.

Controls are permanent canonical 1–64 sets, exact set equality, direct embedded
owner equality, canonical branch order, exactly one CN invocation per condition,
no discovery or cross-product, attempting every scheduled branch, and
propagating the first typed lower failure in canonical constraint order.

### 17.4 Numeric and expression denial of service

ST contains no expression language, parser, arithmetic, decimal expansion,
regex predicate, script, external model, plugin operator, recursion, or
user-defined import. It delegates one bounded numeric predicate evaluation per
condition to the public CN facade, inheriting CN's lexical limits, decimal
limits, parity failures, and hostile-input protections without copying them.

ST must never catch a typed CN parser-integrity failure and turn it into
`condition_evaluation_not_evaluated` or `does_not_match`.

### 17.5 Result reconstruction attacks

Threats include duplicate carried records, forged indices, index-to-wrong-arm,
reordered roots/groups/conditions, forged effective-body equivalence, mixed
contexts/cutoffs/revisions, subject retargeting, selector substitution,
candidate/occurrence substitution, fabricated CN results, forged refusals,
coverage, temporal alignment, execution, or match.

Controls are carry-once material, strict non-boolean indices, exact deterministic
ordering, nested field-content reconstruction, in-memory model rebuild, lower
public-result revalidation, and complete derived-field recomputation without a
store or filesystem.

### 17.6 Resource limits and nondeterminism

The condition count is hard-bounded at 64. Evidence, parents, text, records,
and result collections inherit existing repository bounds. Hash seed, caller
source order, filesystem enumeration, append order, timezone spelling after UTC
normalization, and ambient decimal context must not affect canonical output.

Classification performs O(number of permanent conditions plus carried lower
result validation) public calls and no pairwise source cross-product. It owns no
cache whose eviction or concurrency could affect truth.

### 17.7 Inherited authenticity and trust boundary

ST can detect every inconsistency derivable from carried public material. It
cannot cryptographically authenticate raw content not captured by lower public
contracts. This limitation is tested and documented, not hidden. Expanding it
would require separately owner-gated lower-layer occurrence authentication,
not an ST store or filesystem escape.

## 18. Adversarial acceptance matrix

Every row is an observable acceptance criterion. Implementation must be
red-first, then fixed, and independently reviewed. A slice may implement only
the rows within its gate while retaining prior rows as regressions.

### 18.1 Identity and public surface

| ID | Acceptance criterion |
|---|---|
| I01 | `sta_` accepts exactly 32 lowercase hexadecimal characters; wrong prefix, case, length, and non-hex reject. |
| I02 | `mint_state_anchor()` has the exact keyword-only signature and return type. |
| I03 | Minter output is RFC-4122 UUID4 `.hex`, `sta_`-prefixed, and repeated calls are distinct. |
| I04 | Namespace, display name, and optional role name preserve valid inputs exactly after contract validation. |
| I05 | Invalid names, empty display name, extra arguments, positional misuse, booleans, and coercible objects reject. |
| I06 | Minter performs no file, store, ledger, database, environment, network, authority, or time access. |
| I07 | `StateAnchor` is frozen, extra-forbidden, and fully revalidates hostile nested instances. |
| I08 | System Identity `__all__` grows only by the exact accepted anchor and minter names in pinned order. |
| I09 | No state-family, transition, variable-state, or alternate minter symbol leaks publicly. |

### 18.2 Record, canonical, and evidence contracts

| ID | Acceptance criterion |
|---|---|
| R01 | `srg_`, `std_`, and `stw_` record/filename grammars reject malformed prefix, case, length, and hex. |
| R02 | Model kind↔prefix mappings are exact and all existing mappings remain byte-identical. |
| R03 | `ModelRecord` gains exactly SRG/STD/STW arms; evidence gains SRG/STD but not STW. |
| R04 | Extra fields reject, including state family, exclusivity, transition, observation, outcome, and inline-predicate fields. |
| R05 | SRG requires exactly one embedded valid `StateAnchor`, one subject entity, 1–64 unique constraints, and `all_of_constraints`. |
| R06 | Constraint IDs canonicalize lexicographically; caller order does not change SRG ID or bytes. |
| R07 | Empty, duplicate, 65-member, malformed, boolean, and coercible condition sets reject. |
| R08 | A second SRG for one state anchor rejects whether content agrees or differs. |
| R09 | SRG has no context, parents, withdrawal, evaluation result, or transition fields. |
| R10 | SRG evidence cites exact subject registration and every CRG and contains a claim-bearing arm. |
| R11 | STD pin set equals the SRG permanent condition set exactly. |
| R12 | Each pin is a present `vcn_` for the matching `con_`; missing, extra, duplicate, substituted, or wrong-kind pins reject. |
| R13 | STD uses exact `AssertionContext` and only `independent_latest_at_or_before_cutoff`. |
| R14 | STD evidence cites exact SRG, every CRG and pinned VCN, plus claim-bearing evidence. |
| R15 | STW contains only target, time, authority, and note beyond identity fields; it is uncitable. |
| R16 | Evidence and parents canonicalize; valid reversed input order produces identical record IDs. |
| R17 | Duplicate parents and self-supersession reject before canonical hashing. |
| R18 | `model_construct`/`model_copy` nested forgeries and stale IDs after content mutation reject. |
| R19 | Filename/content mismatch rejects and failed append writes no file. |
| R20 | Every pre-ST canonical vector, record byte, schema, and hash remains unchanged. |

### 18.3 Ownership, store closure, and indexes

| ID | Acceptance criterion |
|---|---|
| O01 | Unknown subject entity rejects. |
| O02 | Unknown constraint registration rejects. |
| O03 | Unknown target variable or embedded owner rejects through accepted closure. |
| O04 | Every constraint target variable's embedded owner must exactly equal the SRG subject. |
| O05 | A cross-entity condition rejects even with evidence, hierarchy, matching names, or another relationship. |
| O06 | Common ownership never creates an SRG or reverse state entry. |
| O07 | Immutable state indexes are exact under reversed record input and hash seeds. |
| O08 | Index keys/values expose no mutable collections and no duplicated registrations. |
| O09 | Prospective append revalidates the full collection before atomic promotion. |
| O10 | No state-specific store, ledger, revision, transaction, or cache exists. |

### 18.4 Lifecycle, correction, corroboration, and withdrawal

| ID | Acceptance criterion |
|---|---|
| L01 | Parent must be STD with the same state anchor and exact context. |
| L02 | Cross-context and cross-state parents reject. |
| L03 | Cross-root convergence rejects. |
| L04 | A cycle rejects deterministically. |
| L05 | One parentless root with one tip is healthy and declared. |
| L06 | Same-root fork is conflicted even with identical effective bodies. |
| L07 | Partial same-root convergence remains conflicted. |
| L08 | Full same-root convergence restores one healthy tip. |
| L09 | Independent healthy roots with identical effective bodies corroborate and aggregate to declared. |
| L10 | Classification admits the unique effective-body group from L09 and does not require one current STD record. |
| L11 | Independent healthy roots with different pin bodies conflict. |
| L12 | Evidence, authority, time, note, parent IDs, and record IDs do not distinguish effective bodies. |
| L13 | Inactive roots remain disclosed beside active healthy roots without making the subject inactive. |
| L14 | All roots with no current tip aggregate to inactive. |
| L15 | A healthy root never hides a same-root conflict or cross-root body disagreement. |
| L16 | No timestamp, authority, filename, ID, append order, or hash chooses a winner. |
| L17 | STW rejects unknown, wrong-kind, superseded, non-tip, and already-withdrawn targets. |
| L18 | Duplicate withdrawal and successor-plus-withdrawal of one tip reject. |
| L19 | Selective withdrawal of one fork tip is allowed and recomputes remaining health. |
| L20 | Earlier explicit membership without a successor or withdrawal revives the older positive tip. |
| L21 | Two independent healthy STD roots with identical bodies remain aggregate `declared` when the sole tip of one is withdrawn: that root is inactive and disclosed, `inactive_roots_present` is emitted, the other root remains healthy, and classification may execute from the remaining unique effective-body group. |
| L22 | A deep hostile STD declaration chain is validated by iterative explicit-stack three-colour traversal without Python recursion or recursion-depth dependence. |

### 18.5 Kernel query contracts

| ID | Acceptance criterion |
|---|---|
| Q01 | Exactly the four accepted method names/signatures exist; no aliases or port/variable/family query. |
| Q02 | Exact result names, fields, literal order, and model-kernel `__all__` are pinned. |
| Q03 | `state()` absent returns structured `not_registered`; present discloses exact SRG/subject/condition indices. |
| Q04 | Lookup condition/variable/owner index tuples align exactly with canonical constraint order. |
| Q05 | `state_declaration()` independently demonstrates not-registered, not-declared, declared, conflicted, and inactive. |
| Q06 | Root, lineage, tip, withdrawal, body-group, and condition ordering is deterministic. |
| Q07 | One healthy root and corroborating healthy roots are distinguishable. |
| Q08 | Same-root conflict and cross-root body disagreement are distinguishable. |
| Q09 | Inactive roots are disclosed alongside active roots. |
| Q10 | `states_of_entity()` absent entity returns `entity_not_registered`. |
| Q11 | Registered entity with no states returns `registered` and empty entries. |
| Q12 | Entity collection includes declared, not-declared, inactive, and conflicted state registrations in exact context. |
| Q13 | Collection entries are ordered by state anchor then first root ID with contiguous non-boolean indices. |
| Q14 | No entity-state entry is inferred from constraints, variable ownership, hierarchy, names, ports, VPA, BH, or evidence. |
| Q15 | Assertion lookup accepts only valid SRG/STD/STW IDs and rejects malformed/non-ST IDs before index access. |
| Q16 | Found SRG and STW use event shape; found STD discloses current/superseded/withdrawn separately from lineage health. |
| Q17 | Valid-shaped absent assertion returns `not_found`, explicit `None`, and empty tuples. |
| Q18 | All results carry complete records/evidence once and rows carry indices only. |

### 18.6 Classification structure and scheduling

| ID | Acceptance criterion |
|---|---|
| C01 | Package and facade are exactly `backend.state_classification` and `StateClassificationQueries`. |
| C02 | The only public method is `state_classification(state_anchor_id, *, context, as_of, condition_sources)`. |
| C03 | `StateConditionSource` has exactly constraint ID and explicit `SourceSelector`; no entity override. |
| C04 | Registered state requires an exact source set equal to permanent constraints. |
| C05 | Missing, extra, duplicate, retargeted, reordered-forgery, and coercible source rows reject typed. |
| C06 | Valid reversed source order canonicalizes deterministically. |
| C07 | Unregistered state accepts only an empty source tuple and invokes no CN branch. |
| C08 | Every registered constraint branch is invoked exactly once in canonical order. |
| C09 | SRG subject entity is forwarded unchanged to every CN branch. |
| C10 | No source discovery, implicit candidate, fallback, permutation, ranking, or cross-product occurs. |
| C11 | Branches run even when STD is not-declared, inactive, or conflicted, preserving independent evidence. |
| C12 | All scheduled branches are attempted before the first typed lower failure in canonical order propagates unchanged. |
| C13 | Ordinary lower refusal remains result data and does not suppress sibling branches. |
| C14 | CN is composed through the public facade; private parser, gate, decimal, and predicate logic are absent. |
| C15 | Complete CN results are carried once and lightweight ST rows index them. |

### 18.7 Classification lifecycle, pins, and truth table

| ID | Acceptance criterion |
|---|---|
| T01 | Unregistered, not-declared, inactive, and conflicted states return `not_executed` and no match. |
| T02 | Corroborating healthy roots with one identical effective-body group may execute. |
| T03 | Same-root fork remains non-executable even when bodies match. |
| T04 | Missing constraint aligns `not_registered`; no CN declaration aligns `not_declared`. |
| T05 | CN conflict aligns `conflicted` even if one tip equals the state pin. |
| T06 | Unique current VCN differing from pin aligns `superseded` and contributes no outcome. |
| T07 | Only exact current VCN alignment contributes the authoritative CN outcome. |
| T08 | All satisfied conditions produce complete/executed/`matches`. |
| T09 | One or more violations with all siblings evaluated produce complete/executed/`does_not_match`. |
| T10 | Violation plus unknown siblings produces incomplete/executed/`does_not_match`. |
| T11 | No violation plus any unknown produces incomplete/not-executed/`None`. |
| T12 | Every unknown condition and independently applicable refusal remains visible. |
| T13 | `does_not_match` never creates or selects another state. |
| T14 | Two independent state calls may both match; no aggregate winner or matched-ID rollup exists. |
| T15 | ST refusal order is exact; detailed CN refusals remain only in carried CN material. |
| T16 | Two parentless current engineering-identical VCNs for one constraint, an STD pin naming either one, and satisfying evidence still yield alignment `conflicted`, no condition contribution, incomplete coverage, `not_executed`, `computed_match=None`, and `condition_declaration_conflicted`. |
| T17 | Pin-alignment/refusal ownership is exact: `not_registered`→`condition_not_registered`, `not_declared`→`condition_declaration_not_declared`, `conflicted`→`condition_declaration_conflicted`, `superseded`→`condition_declaration_superseded`, and only `exact_current` plus CN `not_evaluated`→`condition_evaluation_not_evaluated`; admitted `exact_current` outcomes emit none. |

### 18.8 Time, non-inference, and provenance

| ID | Acceptance criterion |
|---|---|
| P01 | Naive cutoff rejects; aware cutoff normalizes to UTC. |
| P02 | Every branch receives the identical normalized cutoff. |
| P03 | Each selector independently obtains latest evidence at or before cutoff. |
| P04 | Registered-condition evaluation always discloses temporal alignment `not_asserted`. |
| P05 | No cohort, skew, source-clock, timestamp-proximity, interpolation, resampling, or persistence rule appears. |
| P06 | Exact lower staleness and time/provenance fields remain unchanged. |
| P07 | No 300/3600 threshold, freshness class, max age, or staleness veto exists. |
| P08 | Changing context can change STD lifecycle without changing carried CN evidence. |
| P09 | Changing cutoff can change CN evidence without changing model membership or declaration roots. |
| P10 | `as_of` never selects a model revision; `recorded_at` never acts as validity time. |
| P11 | Names, ownership, hierarchy, CAD, ports, VPA, PIF, PCN, PCM, BH, semantics, constraint satisfaction alone, temporal correlation, and value changes create no state. |
| P12 | Result vocabulary never claims physical current state, transition, cause, control, safety, health, fault, correctness, or recommendation. |

### 18.9 Hostile reconstruction and architecture

| ID | Acceptance criterion |
|---|---|
| H01 | Kernel results reject missing, extra, duplicate, or reordered material and mixed revision. |
| H02 | Context, state, subject, constraint, VCN pin, owner, and record substitutions reject. |
| H03 | Forged roots, ancestry, successors, withdrawals, tips, body groups, corroboration, conflict, and conclusions reject. |
| H04 | Boolean or wrong-arm indices reject everywhere. |
| H05 | Classification rejects mixed model, binding, interpretation, temporal, source, selector, and cutoff material. |
| H06 | Forged condition rows, candidate indices, outcomes, coverage, temporal status, refusals, execution, and match reject. |
| H07 | Nested `model_construct`, `model_copy`, stale-ID, and extra implication-bearing-field attacks reject. |
| H08 | Outer reconstruction performs no store, filesystem, network, environment, clock, or write access. |
| H09 | AST checks enforce the exact permitted import graph and no private foreign access. |
| H10 | A coherent lower-evidence mutation accepted by lower contracts is executable evidence of the documented authenticity limitation. |

### 18.10 Replay, determinism, and preservation

| ID | Acceptance criterion |
|---|---|
| D01 | Explicit 9/10/11/14/16/18/28/29/32 memberships retain exact revision IDs. |
| D02 | Every pre-ST membership returns structured absence and no migration artifact. |
| D03 | Historical membership is never derived from directory enumeration, prefix, timestamp, or append order. |
| D04 | Reversed inputs, hash seeds, and file enumeration order do not change IDs, indexes, results, or bytes. |
| D05 | All pre-ST record files and accepted CN/PT/VP/BH artifacts remain byte-identical. |
| D06 | Base-only and all-extras clean checkouts reproduce all authorized deterministic outputs. |
| D07 | `git diff --check`, compilation, focused suites, architecture checks, and full suite pass at each implementation gate. |
| D08 | Slice D append set difference is exactly one SRG and one parentless STD, yielding 34 records. |
| D09 | Slice D contains zero STW, correction, fork, second root, family, transition, or lower-evidence record. |
| D10 | The deterministic artifact preserves all provenance axes and the exact mandatory disclaimer. |

## 19. Bounded synthetic demonstration

### 19.1 Proposed model evolution

The current model has enough accepted knowledge for a bounded singleton
declaration and evidence-relative match. Slice D should evolve:

```text
32 records -> 34 records
```

Append exactly:

1. one `StateRegistration`;
2. one parentless `StateDeclaration`.

The `StateAnchor` is embedded in SRG and is not a ledger record. The candidate
must use:

- a once-minted, owner-frozen neutral synthetic state anchor/name;
- subject entity `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- singleton permanent condition set
  `con_4b768cf843f5474cb5e564e31d239a59`;
- condition family `all_of_constraints`;
- exact pin
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`;
- exact context `lifecycle_view/as_operated`;
- basis `independent_latest_at_or_before_cutoff`;
- synthetic fixture authority and claim-specific evidence.

The name must be neutral. It must not use hot, ready, operating, normal, safe,
fault, alarm, target, command, control, sensor, actuator, or a real-printer
mode.

Do not append any entity, variable, VSP, VSM, CRG, VCN, port, VPA, behavior,
relationship, state family, STW, correction, fork, second root, binding,
interpretation, observation, temporal/source record, transition, trigger,
event, action, or state-machine record.

### 19.2 Classification disclosure

Using the already accepted explicit source selector and complete observation
timeline at cutoff `2026-08-07T20:30:00+00:00`, the direct CN result remains:

```text
current VCN pin: exact_current
observed canonical value: 60.4
predicate: inclusive upper bound 80
CN outcome: satisfied
```

The ST demonstration may therefore disclose:

```text
state declaration: declared / healthy
condition coverage: complete
temporal alignment: not_asserted
execution: executed
computed match: matches
```

This applies a selected model revision to evidence at a temporal cutoff. It
does not claim that the state declaration existed at that cutoff or that the
observation persists. `does_not_match`, incomplete multi-condition evidence,
simultaneous multiple matches, stale pins, conflict, and withdrawal remain
disposable test worlds and do not expand the committed fixture.

### 19.3 Mandatory Slice D pre-append gate

This design intentionally invents no exact state anchor, record ID, record
hash, 34-record revision, artifact byte count, or artifact SHA-256. Slice D
must first:

1. allocate one candidate anchor through `mint_state_anchor()` exactly once;
2. freeze its complete identity in a candidate manifest;
3. make at least two independent byte-identical copies of the accepted
   32-record ledger;
4. construct the exact SRG/STD through public builders and append through
   public `ModelStore` only;
5. use explicit candidate membership and public kernel/CN/ST queries;
6. generate the proposed deterministic disclosure artifact independently;
7. prove identical anchors, canonical records, IDs, stored-file hashes,
   membership, revision, query/classifier disclosures, artifact bytes, and
   predecessor aggregate across runs and clean environments;
8. present the exact candidate contract at an owner gate;
9. perform no authoritative append before explicit approval.

This is a Slice D gate, not an unresolved blocker for Slices A-C.

### 19.4 Preservation and artifact content

The proposed artifact must carry model, binding, interpretation, and temporal
provenance separately; exact SRG/STD records and evidence; exact 32-record
predecessor and 34-record memberships; direct kernel and CN disclosures;
classification conditions, refusals, coverage, temporal alignment, execution,
and match; predecessor file hashes; and the raw-authenticity limitation.

It must be generated twice in the implementation tree and in base-only and
all-extras clean checkouts, with direct byte equality. The accepted CN/PT/VP/BH
artifacts remain unchanged.

### 19.5 Mandatory disclaimer

> This is an illustrative synthetic ST-001 state declaration and evidence classification fixture. `matches` means only that the explicitly selected admitted observation satisfied the referenced synthetic constraint under the stated context, cutoff, and revisions. It does not claim that a real printer is currently in this state, that the state is exclusive or complete, that any transition occurred, or that temporal order establishes cause, control, safety, health, diagnosis, correctness, or recommended action.

The artifact and documentation must also state that names, shared ownership,
hierarchy, CAD, ports, VPA, PIF/PCN/PCM, BH declarations, semantic
compatibility, CN satisfaction alone, temporal correlation, and observation
changes did not create the state. Displaying an observation beside a state
does not make the observation a persisted state fact.

## 20. Four owner-gated implementation slices

Each slice starts from the last owner-accepted HEAD, writes its plan and
acceptance matrix before production code, develops red-first, uses independent
architecture/backend/test/integrity review, commits only authorized scope in
reviewable groups, runs proportionate verification, writes a file-first report,
and stops for owner acceptance. Acceptance of one slice does not authorize the
next.

### 20.1 Slice A — identity, records, canonical integration, and replay

Implement only:

- `StateAnchor`, `sta_`, and `mint_state_anchor()`;
- SRG, STD, and STW frozen record contracts;
- canonical prefixes, filename/ID grammars, record union, evidence arms, and
  public builders/exports;
- exact canonical condition/pin/parent tuple handling;
- model-store reference, evidence, ownership, pin, DAG, and withdrawal
  validation;
- immutable indexes and historical replay;
- hostile record/store tests, architecture checks, and documentation.

Slice A must not add kernel query results or methods, state classification,
source selection, CN calls, temporal composition, demo records, memberships,
or artifacts.

Required stop evidence includes golden identity/record IDs from disposable
tests, canonical-order parity, same-entity enforcement, lifecycle/corroboration
replay, hostile nested-instance rejection, atomic no-write, complete historical
revision preservation, existing-byte hashes, exact public exports, focused and
full suite results, and clean working-tree status.

### 20.2 Slice B — four read-only kernel queries

Implement only:

- `state()`;
- `state_declaration()`;
- `states_of_entity()`;
- `state_assertion()`;
- exact result/literal/export contracts;
- carry-once `ModelQueryMaterial`;
- roots, tips, withdrawals, effective-body groups, corroboration, conflict,
  inactive history, and assertion disclosure;
- deterministic ordering and authoritative store-independent reconstruction;
- hostile query-result tests and documentation.

Slice B must not add `backend/state_classification`, source selection, CN
composition, temporal evidence, demo records, memberships, or artifacts. It
must not change accepted Slice A canonical bytes, store rules, or indexes
except to stop on a demonstrated blocking integrity defect.

Required stop evidence includes every conclusion and agreement combination,
multiple corroborating roots, same-root conflict, cross-root disagreement,
historical revival, collection ordering, assertion activity, stale-ID and
nested-forgery attacks, exact method signatures/exports, historical revisions,
focused/full suites, clean checkouts, and clean status.

### 20.3 Slice C — read-only evidence-gated classifier

Implement only:

- `backend/state_classification`;
- exact errors, source contract, literal vocabularies, result fields, exports,
  and `StateClassificationQueries` facade;
- injection and exact public composition of `ConstraintEvaluationQueries`;
- exact source-set validation and permanent subject forwarding;
- canonical exactly-once branch scheduling and typed-failure propagation;
- pin alignment, condition outcomes, coverage, temporal disclosure, refusals,
  execution, and all-of match table;
- authoritative store-independent hostile revalidation;
- import/capability isolation and a new ST-specific disposable coherent-
  mutation limitation test over `StateClassificationResult`, modeled on BH but
  not satisfied merely by the BH test;
- disposable satisfied, violated, incomplete, stale-pin, conflict,
  corroboration, and multi-condition worlds.

Slice C must not append or alter any model, binding, interpretation, temporal,
source, structural, PT, VP, BH, or demonstration fixture. It must not create a
numeric parser, unit conversion, source discovery, bulk classifier,
state-family logic, transition contract, or persisted result.

Required stop evidence includes exact public surface, every refusal and truth-
table arm, multiple corroborating-root execution, same-root non-execution,
one-call-per-condition scheduling, lower typed-failure ordering, direct CN
equivalence, independent evidence disclosure when lifecycle blocks, mixed-
revision/context/cutoff/selector attacks, coherent-mutation limitation,
architecture checks, focused/affected/full suites, dual clean checkouts, and
clean status.

### 20.4 Slice D — rehearsal, exact approval, and bounded demonstration

Slice D has two distinct gates:

1. **Pre-append rehearsal.** Allocate one candidate StateAnchor once, freeze
   it, construct exactly one SRG and one parentless STD in two independent
   disposable ledger roots, and reproduce exact canonical bytes, IDs, hashes,
   34-record membership/revision, queries, classification, artifact, and
   predecessor preservation. Present the complete candidate contract for owner
   approval and stop.
2. **Authoritative append.** Only after candidate approval, append SRG then STD
   through public builders and `ModelStore`, verify each file immediately,
   pin explicit predecessor/current memberships, add deterministic fixture/
   artifact tests and documentation, run full and dual-clean-checkout
   verification, report, and stop for final owner acceptance.

Slice D may add no record beyond the approved SRG and STD. It must preserve all
32 predecessor bytes and all accepted artifact hashes. It must never imply
that `matches` is a real printer operating state.

### 20.5 Verification baseline for every authorized slice

Verification grows with scope and includes, where applicable:

- focused ST identity/record/store/query/classification/demo tests;
- complete model-kernel, model-state, constraint-evaluation, semantic,
  observation, binding, temporal, PT, VP, and BH affected suites;
- architecture/import-isolation and hostile-revalidation suites;
- every explicit historical replay and artifact-preservation assertion;
- complete repository suite;
- fresh base-only and all-extras clean checkouts;
- deterministic artifact generation in clean environments;
- backend compilation;
- `git diff --check`, branch topology, and working-tree status.

Sandbox-denied loopback tests must be reported separately and rerun with the
required permission. Test counts, commands, failures, repairs, hashes, and
limitations belong in file-first completion reports.

## 21. Explicit exclusions and known limitations

### 21.1 ST-002 transition boundary

ST-002, not ST-001, owns any future design for:

- transition identity;
- from-state and to-state direction;
- triggers, events, guards, actions, and effects;
- transition occurrence or detection;
- causal interpretation of a transition;
- state-machine execution;
- next-state selection;
- dwell time, debounce, hysteresis, and persistence;
- transition history, recommendations, commands, or control.

ST-001 contains no placeholder field, reserved discriminator, hidden graph,
or runtime hook for these capabilities. A value change, later observation, or
different classification is not a transition.

### 21.2 Other v1 exclusions

ST-001 deliberately excludes:

- variable-scoped state identity;
- cross-entity condition sets;
- state families/spaces and exclusivity/completeness declarations;
- any-of, negation, nested Boolean expressions, and weighted conditions;
- non-CN conditions and inline predicates;
- unit conversion, ontology inference, dimensional algebra, or tolerance;
- automatic adoption of corrected VCNs;
- cohort, skew, synchronization, interpolation, resampling, or persistence;
- hard-coded staleness categories or admission thresholds;
- aggregate classification or a matched-state rollup;
- port/VPA qualification or “state at a port”;
- behavior, flow, influence, causality, control, safety, health, fault,
  diagnosis, correctness, or recommendation;
- persisted classifications, stores, ledgers, projections, caches, or state
  revisions.

### 21.3 Known limitations

- V1 can represent only all-of conjunctions over 1–64 accepted CN constraint
  identities.
- Later VCN correction deliberately blocks an old pin until an explicit STD
  correction is admitted.
- Independent latest observations need not be co-temporal; temporal alignment
  is always not asserted.
- Stale evidence remains visible but has no ST freshness policy.
- Multiple states may match and ST supplies no exclusivity or winner.
- Classification proves carried-evidence coherence, not raw-source
  authenticity.
- `matches` is evidence-relative and revision-relative, never persistent
  physical truth.

These limitations are honest scope boundaries, not implied future behavior.

## 22. Proposed ADR-0016 outline

### 22.1 Title and status

```text
ADR-0016 — Explicit state identity and evidence-gated classification

Status: Proposed; owner-gated implementation
```

### 22.2 Context

- CN owns accepted evidence-gated numeric predicate evaluation.
- BH demonstrates stable explicit model knowledge plus upper read-only
  evaluation.
- The kernel lacks state identity or state declaration.
- Observation, state declaration, classification, and transition are distinct.
- ST-001 must establish entity state identity and bounded classification while
  reserving transition semantics for ST-002.

### 22.3 Decisions

1. Add opaque `StateAnchor` (`sta_`) and UUID4 `mint_state_anchor()`.
2. Add permanent evidence-bearing entity-scoped SRG with a canonical 1–64
   constraint set and `all_of_constraints` family.
3. Require every condition target variable's embedded owner to equal the
   subject entity.
4. Add exact-context correctable STD with one exact VCN pin per permanent
   constraint and independent-latest basis.
5. Add minimal uncitable STW for one current declaration tip.
6. Use the existing model ledger and `mrv_`; add no ST store or revision.
7. Reuse BH-style correction DAGs: same-root forks conflict; identical
   independent healthy bodies corroborate; different bodies conflict.
8. Classify an admitted unique effective-body group, not exactly one STD.
9. Add exactly four read-only kernel methods and carry-once authoritative
   results.
10. Add `backend/state_classification` with one exact-state facade method,
    explicit per-condition source selectors, and no caller entity override.
11. Compose the public CN facade once per condition and never duplicate numeric
    evaluation.
12. Apply the fixed three-valued all-of truth table with `matches` /
    `does_not_match` and independent coverage/execution/refusal disclosure.
13. Use independently latest observations at one cutoff and always disclose
    temporal alignment as not asserted.
14. Persist no computed classification and inherit the carried-material
    authenticity limitation honestly.
15. Preserve all historical memberships and use a separately approved 32-to-34
    two-record synthetic demonstration.
16. Exclude every transition capability to ST-002.

### 22.4 Consequences

Positive consequences:

- entities can own stable, named, evidence-bearing state regions;
- exact constraint meaning cannot drift silently after CN correction;
- several conditions and several simultaneously matching states are disclosed
  honestly;
- numeric admission remains in CN and runtime composition stays above kernel;
- all declaration and classification results are revision-relative,
  deterministic, and reconstructible from carried public material.

Costs and limitations:

- the ledger gains three record kinds and nontrivial lifecycle indexes;
- every condition needs explicit evidence and source selection;
- CN correction requires explicit state declaration correction;
- no co-temporality, exclusivity, completeness, transition, or current-state
  claim is available;
- raw-source authenticity is inherited, not expanded.

### 22.5 Rejected alternatives

Record the rejection of generic relationships, variable attributes,
constraint-output-only state, state families/spaces, inline predicates,
automatic VCN following, private CN evaluation, arbitrary staleness classes,
aggregate matched-state rollups, a new ledger/store, and executable state
machines.

### 22.6 Follow-on

ST-002 may be proposed later for explicit transition identity and declarations.
It must begin from these non-transition semantics and must not reinterpret
ST-001 matches or value changes as transitions.

## 23. Final design status and owner questions

This corrected synthesis resolves every implementation-blocking architectural
question posed for ST-001:

- identity is stable, opaque, and entity-scoped;
- registration permanently fixes subject, condition set, and family;
- declarations pin exact VCNs under exact context;
- lifecycle and corroboration are deterministic and winner-free;
- classification composes the public CN facade with explicit sources;
- multiple corroborating declaration roots and multiple matching state
  identities are handled honestly;
- temporal alignment, provenance, coverage, execution, and match remain
  separate;
- historical replay, threat boundaries, demo size, and ST-002 exclusion are
  explicit;
- implementation is split into four owner-gated slices.

Exact Slice D candidate identities, canonical record IDs, final revision, and
artifact hashes are intentionally deferred to the Slice D rehearsal/owner
gate. That is a planned gate, not an unresolved design or implementation
blocker for Slices A-C.

Slice A is owner accepted at
`9adcf4d9613ac96e5fb430a4b750f3053679b64d`. Slice B is owner accepted at
`23eca10a52c0124d22b4e90d80bef952ef5f9381`. Slices A and B are owner
accepted. Slice C is implemented and adversarially reviewed; awaiting owner
acceptance. Slice D remains unstarted and unauthorized.

Genuine unresolved owner questions: none within authorized Slice C.

END OF ST-001 CORRECTED FINAL SYNTHESIS
