# ST-001 — Explicit State Declarations and Evidence-Gated Classification

Status: Codex lead proposal for owner review

Date: 2026-08-30

Repository baseline: `main` at `0ed77df7ea4870faec1eae9b89668add97aa855d`

Scope: architecture and contracts only; no implementation is authorized by this document

## 1. Repository findings

### 1.1 Verified boundary

The repository boundary was verified before design work:

- `HEAD`, `main`, and `origin/main` all resolve to
  `0ed77df7ea4870faec1eae9b89668add97aa855d`.
- The accepted demo model contains exactly 32 JSON record files.
- `ModelStore("models/demo-printer").load()` returns exactly 32 records at
  `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
- The repository contains no state anchor, state registration, state
  declaration, state-withdrawal record, state query facade, state-evaluation
  package, transition contract, or state-machine runtime.
- This was a read-only design inspection. No suite was rerun because no
  implementation or verification claim is being made here.

An independently authored Kimi/other ST-001 proposal was not read. This design
is grounded in the accepted repository and the specialist reviews requested by
the owner.

### 1.2 Accepted explicit historical memberships

The model history is already represented by explicit membership constants,
not by directory enumeration:

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

Every pre-ST membership must remain explicit, reference-closed, byte-frozen,
and replayable with the same revision ID.

### 1.3 Existing facts relevant to ST-001

The accepted 32-record model has:

- five registered entities;
- two registered variables, both owned by
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- one current numeric variable specification, one current quantity-kind
  declaration, and one current observation-role declaration for
  `var_b7e2d3c4f5a6172839405a6b7c8d9e0f`;
- one permanent constraint registration,
  `con_4b768cf843f5474cb5e564e31d239a59`, targeting that variable;
- one current constraint declaration,
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`,
  containing the inclusive exact numeric upper bound `80`;
- one accepted, explicitly selected source/identity/semantic path whose latest
  observation at the established demonstration cutoff is `60.4` and whose CN
  result is `satisfied`;
- one neutral BH variable,
  `var_ab2d312466054c20b0ac764e9bc0114e`, deliberately lacking binding, VSP,
  VSM, interpretation, and observation evidence.

The binding boundaries remain two independent ledgers: six records in
`bindings/demo-printer` and five records in
`bindings/demo-printer-model`. The interpretation fixture has three records.
ST-001 must not alter these ledgers or invent a combined revision.

Accepted artifact hashes that constrain any future demonstration include:

- CN disclosure: `161a7beba5b836246f8d0500bd286cff488cc18b037997a6d02548e7c107a5d9`;
- PT disclosure: `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP disclosure: `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH disclosure: `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.

### 1.4 Contract patterns ST-001 must preserve

Repository contracts impose these constraints:

1. `system_identity` owns pure opaque anchor values and UUID4 minters only.
   New anchors use frozen, extra-forbidden, full-instance revalidation.
2. The model kernel is an append-only ledger of explicit model knowledge. It
   imports only `system_identity`, Pydantic, the standard library, and itself.
3. Model record identity remains
   `<kind-prefix>_<sha256(canonical content excluding record_id)>`.
4. Parent/evidence tuples are canonicalized before hashing; valid caller order
   cannot affect bytes or IDs.
5. `ModelQueryMaterial` carries one complete selected membership, verifies
   content-derived IDs, reconstructs `LoadedModel` without a store, and is the
   accepted authoritative query-result pattern.
6. `ConstraintDeclarationResult` has exactly
   `not_registered | not_declared | declared | conflicted`. CN has no
   constraint withdrawal and no `inactive` constraint status.
7. `ConstraintEvaluationQueries.constraint_evaluation()` is the accepted
   source-backed numeric predicate evaluator. Its candidate outcomes are
   `satisfied | violated | not_evaluated`; `violated` means predicate falsity
   only.
8. An explicit `SourceSelector` makes model state inspect one locator. It does
   not create a binding, rank candidates, or infer a source.
9. Model state is latest-per-locator at or before an aware receipt-axis cutoff.
   It never claims present physical state or persistence after observation.
10. Semantic compatibility admits exact declared token identity only. It does
    no ontology inference, unit conversion, dimensional algebra, or value
    validation.
11. Computed CN and BH outputs are read-only results and are never appended as
    model or temporal records.
12. The BH authoritative-validation limitation is binding on ST: upper-layer
    reconstruction proves carried-material coherence, not raw-source
    authenticity.

### 1.5 Specialist review reconciliation

Architecture/integrity, backend, testing, and adversarial reviews were run
independently over the corrected design, not over another proposal. They
converged on first-class state identity, the existing model ledger, CN-backed
conditions, no state family, a separate read-only evaluator, four kernel
queries, explicit source selection, and a two-record demo.

The lead accepted these important reviewer corrections:

- registration, not declaration, permanently fixes the subject entity,
  constraint-anchor set, and all-of condition family;
- each contextual declaration pins the exact `vcn_` record for every permanent
  constraint, preventing silent predicate drift after CN correction;
- currentness of a pinned VCN is evaluation data, not a timeless store-validity
  rule;
- lower CN branches remain disclosed even when the state declaration is
  absent, inactive, or conflicted;
- classification uses independently latest explicitly selected observations
  and makes temporal alignment explicitly not asserted;
- ST carries CN refusals rather than translating them into a duplicate detailed
  taxonomy.

One test reviewer recommended returning aggregate `not_evaluated` whenever any
condition is unevaluated. The lead instead recommends the exact three-valued
all-of rule in Section 13: one admitted false conjunct is enough for
`does_not_match`, while incomplete coverage and every refusal remain separately
visible. This does not establish any other state and does not conceal missing
evidence. Owner ratification is explicitly requested in Section 22.

## 2. Problem statement

ST-001 must add the smallest honest foundation that can say:

> In this selected model membership and exact assertion context, an
> accountable authority has registered this named state for this entity and
> declared that the state is classified by the all-of satisfaction of these
> exact, evidence-backed constraint declarations.

Separately, a read-only classifier may say:

> Under this model revision, binding and interpretation evidence, explicit
> source selections, and temporal cutoff, the admitted condition results
> `matches`, `does_not_match`, or cannot yet be evaluated against the declared
> state.

The first sentence is explicit model knowledge. The second is a computed,
evidence-relative conclusion. Neither says that the entity is physically or
currently in a state. An observation is not a state; a value change is not a
transition; ordering is not causality; failing one state does not establish a
different state; and multiple independently declared states may match.

## 3. Decision boundaries and terminology

The following terms are normative:

- **State identity**: an opaque `StateAnchor`. It names one enduring state
  concept and contains no state claim.
- **State registration**: a permanent evidence-backed model claim fixing the
  state anchor's subject entity, bounded constraint-anchor set, and v1
  condition family.
- **State declaration**: a correctable exact-context model claim pinning the
  exact constraint-declaration versions used to classify the registered state.
- **Declaration lifecycle**: membership-relative roots, tips, corrections,
  conflict, corroboration, withdrawal, and historical revival of state
  declarations.
- **Constraint result**: CN's independent `satisfied | violated |
  not_evaluated` result over one selected observation path.
- **Classification**: ST's read-only aggregation of admitted condition results
  into `matches | does_not_match | not_evaluated`.
- **Subject**: the one registered entity permanently named by the state
  registration. Existing entity anchors already cover physical/logical
  instances, types, and subsystems.
- **Condition variable**: the variable permanently targeted by a referenced
  `ConstraintRegistration`; it is not the owner of the state.
- **Exact context**: one `AssertionContext` on a state declaration. It scopes
  model knowledge only and never filters observations.
- **Temporal cutoff**: one aware `as_of` applied independently to each explicit
  source path. It never chooses a model membership.
- **Matches**: every required all-of condition is mathematically established as
  satisfied under the admitted evidence, or the aggregate is false through an
  admitted violated conjunct as defined in Section 13. It is not the phrase
  “the system is currently in this state.”

The following are prohibited synonyms or collapsed conclusions: `current
state`, `active state`, `entered`, `left`, `transitioned`, `normal`, `abnormal`,
`healthy`, `fault`, `valid`, `invalid`, `safe`, `unsafe`, `operating`, `control
mode`, and `recommended action`.

## 4. Alternatives and recommendation

### 4.1 State as a generic relationship or variable attribute — reject

A generic relationship would not provide stable state identity, permanent
subject identity, a bounded condition skeleton, declaration lifecycle, or
evidence-gated classification. A variable attribute would wrongly make a
multi-variable entity condition a property of one variable and would tempt
value-to-state inference. Existing relationships and variable registrations
must not acquire state semantics retroactively.

### 4.2 State as constraint-evaluation output only — reject

CN `satisfied` is a result about an explicit constraint. It is not a named
state, does not bind an entity subject, has no state-specific authority or
context, and cannot express that a selected group of conditions constitutes a
declared state. Constraint existence or satisfaction alone creates no state.

### 4.3 First-class state identity with constraint-referenced declarations — accept

This is the recommendation. It adds one opaque identity, three model record
kinds, four read-only kernel queries, and one upper read-only classifier. It
reuses CN's accepted predicates, numeric parser, semantics, and source-backed
evaluation without duplicating them.

The permanent registration fixes the entity subject, the canonical constraint
set, and `all_of_constraints`. A contextual declaration pins one exact VCN per
constraint. This makes identity continuity explicit and prevents constraint
correction from silently changing an unchanged state declaration.

### 4.4 State-family or state-space abstraction — defer

A family could eventually express explicit membership, exclusivity,
completeness, or coverage, but ST-001 needs none of those to classify a named
state. Adding it now would invite winner selection and false exhaustiveness.
If introduced later, it requires its own stable identity and separately
evidence-backed family-membership, exclusivity, and coverage claims.

### 4.5 Direct predicates duplicated in state declarations — reject

Copying lower/upper/interval predicates into state records would create a
second predicate authority, parser parity problem, and security surface. ST
references exact CN declarations instead. Boolean, string, null, any-of,
negation, equality between variables, changes, rates, windows, duration, and
hysteresis are honestly unsupported in v1.

### 4.6 Executable state-machine model — reject for ST-001

Transition identity, from/to direction, triggers, guards-as-transitions,
transition occurrence, actions, entry/exit behavior, causal interpretation,
machine execution, and persistence belong exclusively to ST-002 or later.

### 4.7 Separate state ledger/store — reject

State registration and declaration are explicit, revision-relative model
knowledge and fit the existing append-only model ledger. A separate ledger or
revision would add cross-ledger coherence without a distinct ownership or time
axis. Classification is derived and belongs only in a read-only composition
module.

## 5. Exact identity contracts

### 5.1 Prefix and contract

Add to `backend.system_identity`:

```python
STATE_ANCHOR_ID_PATTERN = r"^sta_[0-9a-f]{32}$"

class StateAnchor(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        revalidate_instances="always",
    )

    anchor_id: Annotated[str, Field(pattern=STATE_ANCHOR_ID_PATTERN)]
    namespace: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
    display_name: Annotated[str, Field(min_length=1)]
    role_name: Annotated[
        str | None,
        Field(default=None, pattern=r"^[a-z0-9-]+$"),
    ]
```

The anchor contains no subject, entity, variable, constraint, state family,
context, evidence, condition, lifecycle, value, observation, temporal field,
classification, transition, direction, trigger, action, causal meaning,
exclusive meaning, or currentness.

### 5.2 Public minter

Add exactly:

```python
def mint_state_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> StateAnchor:
    return StateAnchor(
        anchor_id=f"sta_{uuid4().hex}",
        namespace=namespace,
        display_name=display_name,
        role_name=role_name,
    )
```

It is standard-library UUID4 only, with no I/O, store, registry, seed,
timestamp, path, authority, registration, or persistence. Place the state
anchor/pattern and minter after the port equivalents and before the variable
equivalents in the ordered public exports.

### 5.3 Continuity semantics

- Human-facing rename does not change the opaque state referent, although the
  append-only v1 model has no metadata-update record.
- Changing the subject entity, permanent constraint-anchor set, or
  `all_of_constraints` family requires a new `StateAnchor` and registration.
- Correcting a referenced VCN may preserve the state anchor only through an
  explicit successor `StateDeclaration` that pins the new VCN.
- A genuinely replacement state concept receives a new anchor.
- Similar names, same owners, similar constraints, or matching results never
  prove continuity.

## 6. Exact model-record sketches

### 6.1 Canonical prefixes and discriminators

Add exactly:

| Contract | Record kind | ID/file prefix |
|---|---|---|
| `StateRegistration` | `state_registration` | `srg_` |
| `StateDeclaration` | `state_declaration` | `std_` |
| `StateDeclarationWithdrawal` | `state_declaration_withdrawal` | `stw_` |

All use `schema_version: Literal["1"]`. Add all three prefixes to the model
record and filename grammars, the exact discriminator-to-prefix mapping,
canonical builders, the `ModelRecord` union, and package exports. Add `srg_`
and `std_` to `ModelRecordEvidence`; `stw_` is not citable.

Existing record payloads, canonical bytes, record IDs, filenames, model
memberships, and revision IDs must remain unchanged. The new kinds extend the
union and prefix grammar; they do not rewrite any existing schema.

### 6.2 Permanent registration

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

`CanonicalStateConstraintAnchorIdTuple` contains 1–64 distinct, well-formed
`con_` identities, sorted lexicographically. Duplicate input rejects; it is not
silently deduplicated. Valid caller order does not affect canonical bytes.

Registration contains no context, declaration pin, predicate, source selector,
value, temporal cutoff, parent, correction, withdrawal, classification,
exclusive/completeness claim, state family, transition, trigger, direction,
action, or result.

Changing its subject, constraint set, or family is not a correction. It is a
new state identity.

### 6.3 Exact constraint-declaration pin

```python
class StateConstraintDeclarationPin(...):
    constraint_anchor_id: ConstraintAnchorId
    constraint_declaration_record_id: VariableConstraintDeclarationId
```

Pins are nested immutable values with full-instance revalidation. The canonical
pin tuple:

- contains exactly one pin for every constraint in the registration;
- contains no other constraint;
- is unique by `constraint_anchor_id`;
- is sorted by `constraint_anchor_id`;
- requires each `vcn_` to exist in the selected membership and belong to the
  corresponding `con_`.

The VCN record ID deliberately pins the complete canonical declaration,
including engineering predicate and audit/evidence-bearing content. Two VCNs
with identical predicates but different IDs are different pins. This is not a
conflict with effective-body comparison: the effective state body contains the
pin ID, while evidence/authority on the `std_` itself remains excluded.

### 6.4 Contextual declaration

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

The declaration does not duplicate the subject, constraint predicates,
constraint variables, all-of family, source selectors, results, observations,
or state-family semantics. It has no port, VPA, behavior, transition, from/to,
trigger, action, causality, control, safety, health, diagnostic, or current
operation field.

`evaluation_basis` is explicit even though v1 supports one value. A future
basis must not reinterpret v1 bytes. The phrase means that each condition uses
the latest observation at or before the same cutoff under its own exact source
selector; it does not mean the observations are simultaneous.

### 6.5 Withdrawal event

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

It contains no evidence, context, parents, outcome, replacement, reason code,
negative-state assertion, transition, or claim that physical circumstances
changed. Context and subject are inherited only for lifecycle disclosure of
the targeted declaration.

### 6.6 Canonical identity behavior

Every new record ID is:

```text
<prefix>_<sha256(canonical record content excluding record_id)>
```

The accepted canonical JSON rules remain unchanged. State inputs must:

1. reject malformed IDs before lookup;
2. reject duplicate constraint IDs, pins, parents, and evidence;
3. reject self-supersession;
4. canonicalize valid constraint IDs, pins, parents, and evidence;
5. derive identical record IDs regardless of valid caller order;
6. reconstruct all nested instances from serialized field content;
7. reject stale IDs after content mutation and hostile `model_construct` or
   `model_copy` instances.

## 7. State subject, family, exclusivity, and completeness

### 7.1 Permanent subject

A state belongs permanently to exactly one registered **entity**. Existing
entity anchors are the repository's explicit subject abstraction for physical
instances, logical instances, type definitions, and subsystems. There is no
model anchor, and a variable is too narrow for a potentially multi-variable
state.

The state is not propagated through hierarchy. A state registered to an entity
does not apply to its parent, child, type, instance, port, variable, or owner by
inference. A constraint in its permanent set may target a variable owned by a
different registered entity only because the evidence-bearing registration
explicitly includes that constraint. Cross-entity use is not inferred from
hierarchy or connectivity.

### 7.2 No state family in v1

ST-001 adds no `StateFamilyAnchor`, state space, group, partition, exclusivity,
completeness, priority, default, winner, or preferred-state status.

Multiple state identities may independently return `matches`, including for
the same subject and context. That is not conflict. Declaration conflict exists
only inside one state anchor/context lineage.

If exclusivity or completeness is introduced later, it must use separately
evidence-backed contracts that explicitly declare:

- stable family identity;
- exact member identities;
- whether members are mutually exclusive;
- whether the member set is complete for an exact context;
- lifecycle and correction semantics for each claim.

None of those meanings may be retrofitted onto ST-001 registrations,
declarations, names, constraint overlap, or classification results.

## 8. Condition representation and CN boundary

### 8.1 Reuse without reinterpretation

ST-001 reuses public CN identities, declarations, query results, and evaluator.
It does not create a second predicate language and does not evaluate a pinned
historical predicate privately.

For each registered condition:

1. `StateRegistration` names the permanent `ConstraintAnchor`.
2. `StateDeclaration` pins the exact `VariableConstraintDeclaration` record.
3. `ConstraintEvaluationQueries.constraint_evaluation()` evaluates the
   membership-relative current declaration through the public CN facade.
4. ST compares the current declaration's record ID with the exact state pin.
5. Only exact current alignment allows the CN verdict to contribute to state
   classification.

A current CN result under a different VCN remains fully disclosed but cannot
support the pinned state condition. A CN fork is `conflicted` even if one tip
equals the state pin; the pin never selects a winner.

### 8.2 Why anchor-only reference is insufficient

Referencing only `ConstraintAnchor` would let a VCN correction silently change
the state predicate while the state declaration bytes remained unchanged.
Exact VCN pins prevent that. Because `ModelStore.append()` appends one record,
a VCN correction creates an honest intermediate revision in which:

- the new VCN is membership-current;
- the existing state declaration remains structurally valid;
- its pin is disclosed as superseded;
- classification cannot use that condition;
- a later state-declaration correction may pin the new VCN and restore
  admission.

No atomic multi-record append is invented to conceal this interval.

### 8.3 Supported v1 conditions

The condition family is exactly nonempty `all_of_constraints`. Through CN-001,
each condition can express only one-variable exact numeric:

- lower bound;
- upper bound;
- interval;
- constant equality as an inclusive equal-endpoint interval.

The tuple may contain 1–64 different constraint anchors. One condition is the
all-of singleton. Multiple constraints may target the same variable; each is a
separate condition and receives its own explicit selector row. The selectors
may intentionally identify the same locator, but uniqueness is by constraint
anchor, not locator.

### 8.4 Honestly unsupported in ST-001

Unsupported means no record or evaluator may infer or emulate it:

- `any_of`, negation, nested groups, implication, priority, weights, defaults;
- boolean, string, enumeration, object, array, or null predicates;
- equality or arithmetic between variables;
- affine equations, expressions, user code, tables, or external models;
- tolerance, approximate equality, unit conversion, or dimensional algebra;
- delta, rate, derivative, trend, duration, dwell, hysteresis, debounce;
- sequence, event, temporal order, transition, trigger, or causality;
- CN withdrawal or inactive-constraint state, because CN has neither.

A future predicate family requires a separate owner gate. Existing ST-001
records must retain their exact v1 meaning.

### 8.5 Constraint meaning remains independent

Reusing a CN constraint does not weaken or relabel the original constraint
claim. The state authority explicitly chooses that already-declared normative
predicate as one condition of a named state. CN `satisfied`/`violated` remains
visible as CN truth; ST only derives the bounded all-of match result.

An authority must not create a misleading “constraint” solely to smuggle an
unsupported descriptive predicate into ST. If the intended state condition is
not honestly an accepted CN numeric constraint, ST-001 cannot represent it.

## 9. Evidence and store admission invariants

### 9.1 Registration admission

For every `StateRegistration`, the selected membership must contain:

- the exact registered subject entity;
- one and only one state registration for the state anchor;
- every exact referenced `ConstraintRegistration`;
- each constraint's registered target variable and registered owner, as already
  required by CN/model closure;
- `ModelRecordEvidence` citations to the exact subject entity registration and
  every referenced CRG;
- at least one claim-bearing `OwnerDeclarationEvidence` stating that the
  authority registers this subject/condition skeleton as a state identity;
- closure for every additional model-record evidence reference.

The evidence is the admission basis. Common ownership, hierarchy, names,
topology, VPA, semantic compatibility, CN satisfaction, or observation data do
not create or strengthen registration.

### 9.2 Declaration admission

For every `StateDeclaration`, the selected membership must contain:

- exactly one matching `StateRegistration`;
- exactly one pin for each registered constraint and no extra pin;
- every pinned VCN and its same-constraint CRG relationship;
- `ModelRecordEvidence` citations to the exact SRG, every referenced CRG, and
  every pinned VCN;
- at least one claim-bearing `OwnerDeclarationEvidence` supporting the exact
  contextual state declaration;
- every parent declaration and all evidence dependencies.

The store validates VCN existence and con↔VCN coherence, not currentness.
Requiring timeless currentness would make a later valid VCN correction
retroactively invalidate the whole append-only model. Current, conflicted, and
superseded alignment is query/evaluation data.

### 9.3 Registration uniqueness and cross-entity conditions

There is exactly one `StateRegistration` per `sta_`. A duplicate is invalid
whether its bytes agree or differ; no authority, timestamp, filename, or ID
breaks the tie.

Constraint targets may be owned by the subject entity or by another registered
entity. Cross-entity conditions are allowed only because the SRG explicitly
and evidentially lists the constraint anchors. This allowance asserts no flow,
causality, hierarchy, influence, control, or subsystem composition.

### 9.4 Store and immutable index impact

Extend `LoadedModel` with immutable, deterministically constructed state
indexes analogous to the accepted BH indexes:

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

Mappings are read-only; values are canonical tuples or frozen records. Indexes
derive only from a fully validated selected record collection. Reversed input
maps, filesystem order, append order, and hash seed must produce identical
indexes and revision.

`ModelStore.append()` continues to revalidate the complete current and
prospective collections before atomic promotion. No state-specific store,
ledger, transaction, multiappend, cache, or revision is added.

## 10. Declaration lifecycle, correction, conflict, and withdrawal

### 10.1 Lineage key and roots

The lineage key is exactly:

```text
(state_anchor_id, exact AssertionContext)
```

Claims in different contexts do not supersede, corroborate, or conflict with
one another. A parentless `std_` starts one independent root.

Within one root:

- zero current tips → `inactive`;
- one current tip → `healthy`;
- multiple current tips → `conflicted`, even when their bodies are identical;
- multi-parent convergence is allowed only within that root;
- partial convergence remains conflicted;
- full convergence restores one healthy tip;
- cross-root convergence is invalid;
- cycles are invalid.

### 10.2 Effective engineering body

The state declaration's effective body contains exactly:

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

The subject, permanent constraint set, and all-of family are resolved from the
unique SRG and need not be duplicated in each declaration body.

Across independent active roots in one lineage key:

- identical effective bodies corroborate;
- different effective bodies conflict;
- evidence and authority remain disclosed but do not distinguish engineering
  bodies;
- no timestamp, authority, record ID, or append order selects a winner.

### 10.3 Aggregate declaration conclusion

The anchor/context conclusion is exactly:

```text
not_registered
not_declared
declared
conflicted
inactive
```

The result separately discloses root health and agreement findings sufficient
to distinguish one healthy root, corroborating healthy roots, same-root
conflict, cross-root effective-body disagreement, and inactive roots.

### 10.4 Withdrawal rules

An `stw_` targets one current `std_` tip. Reject an unknown, wrong-kind,
cross-subject, superseded, non-tip, already-withdrawn, or duplicate target.
Reject a membership in which the same tip is both superseded and withdrawn.
Selective withdrawal of one fork tip is allowed. Omitting a later withdrawal
from an explicit historical membership revives the target relative to that
membership.

A withdrawal means only that the positive state declaration is no longer
asserted in the selected revision. It does not mean the state was false,
impossible, exited, or physically removed.

## 11. Kernel queries and authoritative result contracts

### 11.1 Exact `ModelQueries` surface

Add exactly four methods:

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

There is no alias, port query, variable reverse query, condition evaluator,
classification query, “current states” query, transition query, or graph
traversal. Variable involvement is obtained by resolving the permanent
constraint registrations carried in a state lookup. It is not a new permanent
variable-to-state relation.

All four methods operate over one injected `LoadedModel`, own no store, perform
no writes, and use `ModelQueryMaterial` exactly once per public result.

### 11.2 Kernel literal vocabularies

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

Reuse the exact public `AssertionActivity` and `ContainingLineageHealth`
aliases. Do not add winner, preferred, exclusive, active-state, normality,
health, transition, or validity vocabularies.

### 11.3 Lightweight condition and lineage rows

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

Every index is a non-boolean `StrictInt >= 0`. `condition_index` and
`group_index` are contiguous from zero. Rows contain no duplicate authoritative
records. Read-only convenience properties may resolve indices only through the
carried material.

Roots are ordered by root record ID; lineage records, tips, and withdrawals by
record ID; body groups by canonical effective-body bytes; condition references
by constraint anchor ID. IDs determine display order only, never truth.

### 11.4 Exact lookup result

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

For `not_registered`, every optional index is `None` and every tuple is empty.
For `registered`, the three condition tuples align exactly with the SRG's
canonical constraint-anchor tuple. Owner indices may repeat when multiple
conditions target variables of the same owner; the entity record still appears
only once in `material`.

### 11.5 Exact declaration result

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

- absent registration → `not_registered`, `not_applicable`, empty rows;
- registered with no exact-context root → `not_declared`, `not_applicable`;
- roots but no current tips → `inactive`, `inactive`;
- any same-root fork or active cross-root body disagreement → `conflicted`;
- otherwise one or more identical active body groups → `declared`, `healthy`;
- inactive roots remain disclosed beside active roots and add
  `inactive_roots_present` without suppressing a declared result;
- a healthy root never hides a conflicted root.

### 11.6 Entity collection

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

An absent entity returns `entity_not_registered`, no index, and empty entries.
A registered entity with no states returns `registered` and empty entries. One
entry is returned for every state permanently registered to the exact entity,
including not-declared, inactive, and conflicted states in the requested
context. Entries are ordered by `state_anchor_id`, then the first root record ID
as a deterministic tie-break, and receive contiguous indices.

No entry is inferred from a variable owner, hierarchy, constraint target,
port, VPA, behavior, name, source, or observation.

### 11.7 Assertion disclosure

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
absent ID returns `not_found`, `None` lifecycle fields, and canonical empty
tuples. A found SRG or STW is an event and has no declaration activity/root
fields. For a found STD:

- direct successor exists → `superseded`;
- withdrawal exists → `withdrawn`;
- otherwise → `current`;
- containing-root health and aggregate subject conclusion are recomputed
  independently;
- conflict belongs to a root/subject, not to the individual STD.

Malformed or non-state record IDs raise a typed `ModelQueryError` before model
index access.

## 12. Classification architecture and exact API

### 12.1 New read-only module

Add a separate `backend/state_evaluation`. This is justified because it
combines model declarations with binding, interpretation, semantic, temporal,
and numeric evidence. None of those dependencies may enter `model_kernel`.

The facade is constructed with one public `ConstraintEvaluationQueries` and
owns no store, ledger, revision, projection, cache, path, socket, database, or
write capability. It composes the exact public CN facade; it never imports CN
private functions or evaluates a predicate itself.

### 12.2 Exact source selector

```python
class StateConditionSource(...):
    constraint_anchor_id: ConstraintAnchorId
    entity_anchor_id: EntityAnchorId | None = None
    source: SourceSelector
```

The source is mandatory. The optional entity request is forwarded unchanged to
CN/ES/VM. Selecting a source creates no binding or model fact.

For a registered state, source rows must exactly equal the registration's
permanent constraint set, one row per constraint, unique and canonically sorted
by `constraint_anchor_id`. Missing, extra, duplicate, or retargeted rows are a
typed input error. Reversed valid caller order canonicalizes. Two condition
rows may carry equal locators because uniqueness is by constraint identity.

For an unregistered state, the only admitted selector tuple is `()`: no
authoritative condition set exists, so caller-supplied conditions must not be
presented as state participants.

### 12.3 Exact facade method

```python
class StateEvaluationQueries:
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

There are no aliases, collection classifiers, discovery wrappers, port
variants, transition APIs, or persistence methods.

### 12.4 Deterministic branch scheduling

For a structurally valid request:

1. validate state ID, exact context, aware cutoff, and source-row structure;
2. obtain the authoritative state lookup/declaration from the exact model used
   by the injected CN stack;
3. if unregistered, require empty sources and return structured absence without
   invoking CN;
4. if registered, require exact source-set equality with SRG;
5. invoke every public CN `constraint_evaluation()` exactly once in canonical
   constraint order, even when the state declaration is not declared,
   inactive, or conflicted;
6. if lower branches raise typed failures, attempt all branches, then propagate
   the first failure in canonical constraint order unchanged and fabricate no
   ST result;
7. carry every complete CN result once;
8. only for one admitted current state declaration, derive each exact VCN-pin
   alignment and condition outcome;
9. derive coverage, temporal disclosure, refusals, execution, and computed
   match through the exact truth table in Section 13;
10. persist nothing.

There is no implicit discovery, candidate ranking, authority ranking, fallback,
permutation search, cross-product, winner, source-time matching, or recency
tie-break.

### 12.5 Exact result fields

```text
StateEvaluationConditionResult
  condition_index
  constraint_anchor_id
  source_index
  constraint_evaluation_index
  candidate_index
  declaration_alignment
  outcome

StateEvaluationRefusal
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

`state` is one complete `StateDeclarationResult`. `ruleset_version` is exactly
`Literal["st001.1"]`. `candidate_index` is `None` only when the corresponding
CN result has no candidate; an explicit valid source normally yields exactly
one. `computed_match` is explicitly `None` unless aggregate execution reaches a
mathematical result.

The complete state model material appears once inside `state`. Each complete CN
result appears once in `constraint_evaluations`; condition rows carry indices
only. ST does not duplicate occurrences, semantic results, bindings, decimals,
predicates, boundaries, or provenance.

### 12.6 Public errors and exports

Public errors are exactly:

```text
StateEvaluationError
StateEvaluationConfigurationError(StateEvaluationError)
StateEvaluationInputError(StateEvaluationError)
```

Codes are:

```text
STATE_EVALUATION_CONFIGURATION_INVALID
STATE_EVALUATION_INPUT_INVALID
```

Direct Pydantic model construction may retain ordinary `ValidationError`.
Facade construction and request misuse use the ST error tree. Ordinary absence,
conflict, inactivity, stale pins, CN refusal, and nonmatching are result data.
Typed lower errors, including CN `NumericParityBreachError`, propagate as the
same class object and are not wrapped, translated, or re-exported by ST.

Pin `backend.state_evaluation.__all__` to exactly this order:

1. `StateEvaluationError`
2. `StateEvaluationConfigurationError`
3. `StateEvaluationInputError`
4. `StateConditionSource`
5. `StateConditionDeclarationAlignment`
6. `StateConditionOutcome`
7. `StateConditionCoverage`
8. `StateTemporalAlignment`
9. `StateClassificationExecution`
10. `StateComputedMatch`
11. `StateEvaluationRefusalReason`
12. `StateEvaluationRefusal`
13. `StateEvaluationConditionResult`
14. `StateClassificationResult`
15. `StateEvaluationQueries`

No derivation helper, CN parser, decimal contract, lower facade, alias, or
convenience wrapper is public through this package.

## 13. Temporal policy, statuses, refusals, and truth table

### 13.1 Exact evaluation and admission vocabularies

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

`computed_match` is optional; absence represents aggregate `not_evaluated`.
There is intentionally no `current`, `active`, `in_state`, `consistent`,
`healthy`, `normal`, `valid`, `safe`, `fault`, `passed`, or `failed` result.

### 13.2 Exact ordered refusal vocabulary

```python
StateEvaluationRefusalReason = Literal[
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

State refusals identify state lifecycle or condition admission gates only. The
detailed CN reason—observation absence, attachment failure, semantic mismatch,
numeric bounds, and so on—remains authoritative in the carried CN result and is
not renamed or duplicated.

### 13.3 Exact pin-alignment mapping

For one uniquely current state declaration:

| Current CN declaration state | Pin comparison | Alignment | Contribution |
|---|---|---|---|
| constraint absent | n/a | `not_registered` | none |
| no declaration | n/a | `not_declared` | none |
| conflicted | even if a tip equals pin | `conflicted` | none |
| one declaration | record ID differs | `superseded` | none |
| one declaration | record ID equals pin | `exact_current` | CN verdict |

The term `superseded` describes membership-relative pin alignment. It does not
rank the new VCN or evaluate the old predicate. CN has no inactive condition
status.

### 13.4 Exact all-of truth table

State lifecycle gates first. `not_registered`, `not_declared`, `inactive`, or
`conflicted` always yields `not_executed` and `computed_match=None`, while all
registered-condition CN results remain carried where the registration exists.

For one `declared` state:

| Admitted condition outcomes | Other conditions | Coverage | Execution | Computed match |
|---|---|---|---|---|
| all `satisfied` | none | `complete` | `executed` | `matches` |
| one or more `violated` | all other conditions evaluated | `complete` | `executed` | `does_not_match` |
| one or more `violated` | one or more not evaluated | `incomplete` | `executed` | `does_not_match` |
| no `violated` | one or more not evaluated | `incomplete` | `not_executed` | `None` |

This is exact three-valued conjunction: one admitted false conjunct makes the
all-of false even when another conjunct is unknown. Every unknown condition and
refusal remains disclosed; `does_not_match` establishes no other state.

### 13.5 Independent temporal evidence

Every branch receives the same UTC-normalized `as_of`, but each explicit source
is queried independently for its latest observation at or before that cutoff.
The result sets `temporal_alignment="not_asserted"` whenever registered
condition branches are carried. It does not compute or require a BH acquisition
cohort.

ST makes no claim of:

- physical simultaneity or co-temporality;
- synchronized source clocks;
- receipt-time or source-time equivalence;
- acceptable skew;
- interpolation, resampling, lag compensation, or range search;
- value persistence after receipt;
- causal order.

Each lower occurrence retains its own receipt time, source marker, clock
segment, and staleness disclosure. Close timestamps do not create alignment;
widely separated observations do not automatically veto the fixed independent
basis. ST introduces no staleness threshold. Staleness remains visible and
does not silently admit or refuse a condition.

Changing only `AssertionContext` may change declaration lifecycle but must not
filter CN/temporal evidence. Changing only `as_of` may change lower observations
but must not alter the selected model revision. `recorded_at` is audit time,
not model validity time or a temporal selector.

## 14. Authoritative result reconstruction

### 14.1 Kernel results

Every public kernel state result must reconstruct every nested object from
serialized content, rebuild `LoadedModel` from its one `ModelQueryMaterial`, and
recompute:

- canonical record IDs and exact revision membership;
- state registration, subject, constraints, target variables, and owners;
- exact context and lineage key;
- roots, ancestry, successors, tips, withdrawals, and root health;
- effective-body bytes, body groups, corroboration, and disagreement;
- aggregate conclusion and agreement findings;
- every strict index and deterministic ordering.

No result validator accesses `ModelStore`, a path, directory enumeration, or
the filesystem.

### 14.2 Classification result

`StateClassificationResult` must reconstruct its state result, sources, every
CN result, condition row, and refusal from serialized field content. Its
validator must:

1. rebuild the model from state material;
2. rerun the exact state lookup and declaration query;
3. run direct kernel constraint lookups over that same rebuilt membership;
4. verify each CN result uses the exact constraint, target variable, model
   revision, cutoff, entity request, source selector, and candidate;
5. enforce one common model revision, binding revision, interpretation revision,
   and cutoff while preserving independent occurrence times;
6. recompute selector-set equality, order, branch indices, pin alignment, CN
   outcome mapping, coverage, temporal disclosure, refusals, execution, and
   truth table;
7. reject record indices that point to the wrong union arm;
8. reject boolean, string, float, or coercible indices;
9. operate with every store constructor and filesystem API unavailable.

It must reject missing, duplicate, extra, or reordered model material, roots,
body groups, tips, withdrawals, sources, CN results, conditions, and refusals;
mixed model/binding/interpretation revisions; mixed contexts/cutoffs; state,
constraint, variable, entity, source, candidate, occurrence, or pin
substitution; stale content-derived IDs; forged lifecycle, alignment, coverage,
temporal status, execution, or match; and nested `model_construct`/`model_copy`
forgeries.

### 14.3 Inherited authenticity boundary

Normative limitation:

> ST authoritative result validation proves the internal coherence of the
> carried lower public results and every ST-derived field. It inherits, and
> does not independently re-prove, raw-source authenticity. A fully coherent
> lower-evidence content mutation accepted by the lower public contracts is
> outside ST's store-independent detection boundary.

ST must reject every substitution detectable from carried material, but it
must not claim that `payload_checksum` authenticates an uncaptured payload or
access a store/filesystem to broaden that claim. An executable limitation test
must demonstrate this boundary honestly. Content-bound occurrence
authentication remains separate future work.

## 15. Import direction and architectural isolation

### 15.1 Permitted dependency graph

```text
system_identity
      ↑
model_kernel
      ↑
model_state → observation_compatibility → semantic_compatibility
                                                   ↑
                                      constraint_evaluation
                                                   ↑
                                          state_evaluation

data_sources → temporal_state → identity_binding → model_state
source_interpretation ───────────────────────→ semantic_compatibility
```

Arrows point from a dependency toward its consumer in the vertical chain;
existing horizontal arrows retain the repository's accepted composition.

### 15.2 Exact evaluator permissions

`backend/state_evaluation` may import public APIs from:

- `backend.system_identity`;
- `backend.model_kernel`;
- `backend.model_state` only for `SourceSelector`;
- `backend.constraint_evaluation`;
- itself, Pydantic, and the standard library.

It may reach the exact loaded model only through public attributes of the
injected public composition chain, then construct public `ModelQueries` for the
same membership. No private foreign attribute is allowed.

### 15.3 Forbidden dependencies and capabilities

The evaluator must not import directly from:

- temporal state;
- identity binding;
- observation compatibility;
- semantic compatibility;
- source interpretation;
- data sources;
- behavior evaluation;
- structural evidence;
- any `store` module;
- `sqlite3`, `pathlib`, `socket`, subprocess, or networking packages.

It must contain no store constructor, filesystem path, `open`, write call,
database, cache, projection, repository, environment lookup, dynamic import,
or persistence capability.

The kernel must not import state evaluation, model state, temporal state,
identity binding, observation/semantic compatibility, constraint evaluation,
source interpretation, data sources, behavior evaluation, or structural
evidence. Every lower package must be AST-checked not to import
`backend.state_evaluation`.

## 16. Historical replay and preservation rules

### 16.1 Structured pre-ST absence

Every explicit 9/10/11/14/16/18/28/29/32-record membership must replay with
the exact count and revision in Section 1. A pre-ST replay must return:

- `state(known-shaped-sta).status == "not_registered"`;
- `states_of_entity(registered_entity, context=...).status == "registered"`
  with `entries == ()`;
- `state_assertion(valid-shaped-new-id).lookup_status == "not_found"`;
- an unregistered state classification with empty condition sources,
  `execution="not_executed"`, and `computed_match=None`.

No migration record, synthetic state, inferred state, or directory-derived
membership is permitted.

### 16.2 Reference closure

An ST membership is valid only when it closes over:

- subject entity registration;
- every condition CRG;
- every target VRG and target owner registration through existing CN closure;
- state registration;
- every pinned VCN and its ancestry;
- every STD parent;
- every cited model record;
- every STW target.

Replay membership is always caller-supplied, pattern-checked, unique, and
canonicalized. Historical membership is never reconstructed from directory
enumeration, filename prefixes, timestamps, record kinds, or append order.

### 16.3 Separate provenance axes

The caller explicitly selects one `LoadedModel` membership before constructing
the query stack. `as_of` never selects, extends, or rewrites that membership.
The state result preserves:

- model revision in `state.material.revision` and every CN model revision;
- binding revision in each lower semantic path;
- interpretation revision in each lower semantic path;
- temporal cutoff in `as_of`;
- occurrence receipt and source-time evidence inside each CN result.

There is no temporal revision, shared model/temporal timestamp, validity
interval, or cross-clock synchronization claim.

### 16.4 Preservation gates

Before any eventual fixture append, freeze all 32 predecessor files and all
accepted binding, interpretation, temporal, source, structural, PT, VP, CN, and
BH artifacts. After append, every predecessor byte and identity must remain
unchanged. Existing canonical vectors and public contracts are immutable unless
a separately owner-gated integrity defect is demonstrated.

## 17. Security and denial-of-service model

### 17.1 Bounded structures

- A registration admits 1–64 constraints; 64/65 boundary twins are mandatory.
- A declaration has exactly one pin per registered constraint; it cannot add a
  nested predicate or expression tree.
- Source rows have the same bounded cardinality and are validated before lower
  calls.
- Duplicate-heavy input rejects before evaluation.
- Parent DAG validation must be iterative or depth-bounded consistently with
  existing model-kernel lifecycle validation.
- Output contains one CN branch per permanent constraint, never a cross-product.

### 17.2 Numeric and expression attacks

ST has no parser, expression language, evaluator for arbitrary predicates,
dynamic import, executable script, recursion, functions, coefficients, or
external-model reference. All numeric lexical bounds, expansion limits, parity
failures, Decimal-context independence, division avoidance, and canonical
output limits remain owned by public CN.

ST must never privately import or copy CN's parser or comparator. A typed CN
parity failure propagates unchanged; it cannot become `does_not_match` or an
ordinary ST refusal.

### 17.3 Lifecycle and identity attacks

Threats include malformed/cross-kind IDs, stale content-derived IDs,
filename/content mismatch, duplicate registrations, constraint-set
substitution, con↔VCN substitution, parent cycles, cross-root convergence,
same-tip successor/withdrawal, forged corroboration, and record ordering used
as a winner. All fail closed or remain explicit conflict.

### 17.4 Composition attacks

Threats include missing/extra/duplicate/retargeted selectors; candidate or
occurrence substitution; mixed model, binding, interpretation, and cutoff
material; source-locator substitution; CN-result substitution; forged pin
alignment, condition outcome, coverage, temporal alignment, refusal, execution,
or match; booleans as indices; and nested construction/copy forgeries.

### 17.5 Resource and authenticity limitations

ST does not solve the repository's inherited pre-parse Python/Pydantic object
size boundary or the existing model store's general untrusted-file read-size
boundary. It must not overclaim those protections. It does bound its own
condition fanout and introduces no new unbounded expansion.

Likewise, coherent lower-evidence mutation accepted by lower contracts remains
outside store-independent ST detection. This is a disclosed trust boundary,
not a reason to access stores in result validation.

## 18. Adversarial acceptance matrix

The following matrix is normative for implementation planning. Reviewers must
add independent reproductions without broadening the authorized slice.

### 18.1 Identity and public surface

| ID | Acceptance condition |
|---|---|
| I01 | `sta_` plus 32 lowercase hex is the only valid state-anchor grammar. |
| I02 | Wrong prefix, case, separator, length, hex, whitespace, and cross-kind IDs reject. |
| I03 | `StateAnchor` field set is exactly anchor ID, namespace, display name, optional role. |
| I04 | Anchor extra fields for subject, conditions, context, state, currentness, transition, or outcome reject. |
| I05 | Anchor `model_construct` and `model_copy` forgeries fail full revalidation. |
| I06 | `mint_state_anchor` exact keyword-only signature and return type are pinned. |
| I07 | Minter emits RFC-4122 UUID4 IDs; repeated calls differ; names do not determine identity. |
| I08 | Minter performs no file, store, ledger, database, network, environment, or authority action. |
| I09 | Invalid namespace/name/role and coercion attacks reject through the existing contract. |
| I10 | Exact ordered `system_identity.__all__` grows only by state pattern, anchor, and minter. |

### 18.2 Record and canonical contracts

| ID | Acceptance condition |
|---|---|
| R01 | Exact SRG/STD/STW kind, schema, field sets, prefixes, builders, exports, and filename grammar are pinned. |
| R02 | Malformed SRG/STD/STW ID prefix, case, length, and hex reject. |
| R03 | Registration accepts 1 and 64 constraints; 0 and 65 reject. |
| R04 | Duplicate constraint IDs reject; reversed valid input canonicalizes to identical bytes/ID. |
| R05 | Registration subject must be exactly one registered entity. |
| R06 | Every condition constraint must have one CRG in membership. |
| R07 | Missing target VRG or target owner closure fails through existing CN/model admission. |
| R08 | Duplicate state registration fails whether bodies agree or differ. |
| R09 | SRG requires exact subject-registration and all-CRG citations plus claim-bearing evidence. |
| R10 | Missing, substituted, wrong-kind, or extra required citation fails. |
| R11 | Explicit same-owner and cross-owner condition worlds both admit only through exact SRG evidence. |
| R12 | Shared owner or hierarchy without SRG produces no state. |
| R13 | STD pins exactly the SRG constraint set; missing, extra, duplicate, or substituted pins reject. |
| R14 | Every pinned ID is a `vcn_` belonging to the matching `con_`. |
| R15 | STD requires exact SRG, all CRG, and all pinned-VCN citations plus claim-bearing evidence. |
| R16 | A stale but structurally coherent VCN pin keeps the ledger valid and is disclosed by evaluation. |
| R17 | A state correction cannot cite a VCN absent from the selected membership. |
| R18 | `all_of_constraints` and the one evaluation-basis literal are the only v1 values. |
| R19 | Any-of, negation, direct predicates, nested groups, expressions, tolerances, and transition fields reject. |
| R20 | STW exact minimal field set is pinned; evidence/context/parent/outcome/reason/negative fields reject. |
| R21 | SRG and STD are citable; STW used as evidence rejects. |
| R22 | Hostile nested anchor, pin, context, evidence, authority, and parent instances reject. |
| R23 | Stale record ID after any content mutation rejects. |
| R24 | Filename/content mismatch and wrong discriminator reject all-or-nothing. |
| R25 | Existing record bytes, IDs, schemas, and hashes remain unchanged. |

### 18.3 Lifecycle and corroboration

| ID | Acceptance condition |
|---|---|
| L01 | Lineage key is exact `(sta_, AssertionContext)`. |
| L02 | Unknown, wrong-kind, cross-state, cross-context, duplicate, and self parent reject. |
| L03 | Parent order canonicalizes; valid reversed parent input yields identical ID. |
| L04 | State-declaration DAG cycle rejects. |
| L05 | One parentless current declaration is one healthy root. |
| L06 | Same-root fork conflicts even when effective bodies are identical. |
| L07 | Partial convergence remains conflicted; full same-root convergence is healthy. |
| L08 | Cross-root convergence rejects. |
| L09 | Independent healthy roots with identical effective bodies corroborate. |
| L10 | Independent healthy roots with different VCN pins or basis conflict. |
| L11 | STD evidence, authority, time, note, parent list, and record ID do not distinguish effective bodies. |
| L12 | A different exact VCN ID distinguishes bodies even if dereferenced predicates appear equal. |
| L13 | Inactive roots remain disclosed beside active roots. |
| L14 | No timestamp, authority, record ID, filename, append order, or hash seed chooses a winner. |
| L15 | STW unknown, wrong-kind, superseded, non-tip, and already-withdrawn targets reject. |
| L16 | Selective fork-tip withdrawal is valid; withdrawing all tips makes the root inactive. |
| L17 | A tip both superseded and withdrawn in one membership rejects. |
| L18 | Earlier replay omitting a successor or withdrawal revives the earlier declaration. |
| L19 | Context A roots never affect context B query or lifecycle. |

### 18.4 Store, index, and replay integrity

| ID | Acceptance condition |
|---|---|
| S01 | Indexes cover registration, subject, constraint skeleton, declarations, key, roots, parents, successors, tips, withdrawals, and entity reverse lookup. |
| S02 | Every public loaded mapping is defensively immutable. |
| S03 | Reversed mappings and hash seeds produce identical indexes and revision. |
| S04 | Failed prospective append promotes no record and preserves prior revision. |
| S05 | Identical reappend is a no-op only after validating the whole existing collection. |
| S06 | Hostile JSON, symlink, directory, unexpected file, and filename mismatch fail all-or-nothing. |
| S07 | Replay rejects duplicate membership IDs before constructing paths. |
| S08 | Replay rejects omitted subject, CRG, VRG, owner, SRG, VCN, parent, target, or evidence dependency. |
| S09 | Currentness is membership-relative under explicit replay. |
| S10 | No state-specific ledger, store, cache, database, or revision exists. |

### 18.5 Kernel query contracts

| ID | Acceptance condition |
|---|---|
| Q01 | Exact four method names, keyword-only context signatures, return types, exports, and no aliases are pinned. |
| Q02 | Absent state returns structured `not_registered`. |
| Q03 | Registered state with no exact-context root returns `not_declared`. |
| Q04 | Exact-context declared, conflicted, and inactive conclusions are independently demonstrated. |
| Q05 | Registered entity with no states is registered-empty; absent entity is distinct. |
| Q06 | Entity collection includes every registered state and no inferred state. |
| Q07 | Roots disclose complete lineage, tips, withdrawals, health, body groups, and agreement findings. |
| Q08 | One healthy root does not hide a conflicted root. |
| Q09 | Assertion lookup distinguishes SRG event, current/superseded/withdrawn STD, STW event, and valid absence. |
| Q10 | Complete `ModelQueryMaterial` is carried once; nested rows contain strict indices only. |
| Q11 | Boolean, float, string, negative, wrong-arm, and out-of-range indices reject. |
| Q12 | Missing, duplicate, extra, or reordered roots/body groups/entries reject. |
| Q13 | Mixed revision, context, state, subject, constraint, or VCN substitution rejects. |
| Q14 | Forged current tips, withdrawals, health, body equality, corroboration, conclusion, or ordering rejects. |
| Q15 | Malformed query input rejects before model-index access. |
| Q16 | Query validation succeeds with store/filesystem access disabled. |

### 18.6 Classification input and lower composition

| ID | Acceptance condition |
|---|---|
| E01 | Wrong facade dependency raises exact ST configuration error. |
| E02 | Malformed state/context/cutoff/source structures raise exact ST input error. |
| E03 | Registered state requires one source row per permanent constraint, unique by constraint ID. |
| E04 | Missing, extra, duplicate, reordered-after-normalization, and retargeted source sets reject. |
| E05 | Reversed valid source order canonicalizes. |
| E06 | Unregistered state admits only empty source tuple and invokes no CN branch. |
| E07 | Every registered constraint branch is invoked exactly once in canonical order. |
| E08 | No implicit source discovery, fallback, ranking, permutation, or cross-product occurs. |
| E09 | All lower typed failures are collected by schedule and first canonical failure propagates unchanged. |
| E10 | State declaration absence, inactivity, or conflict does not suppress registered-condition CN evidence. |
| E11 | Explicit selector produces exactly one candidate; inconsistent cardinality fails integrity validation. |
| E12 | Each complete CN result is carried once; CN records/evidence/decimals are not duplicated. |

### 18.7 Pin alignment and truth table

| ID | Acceptance condition |
|---|---|
| C01 | Exact current VCN pin plus CN `satisfied` yields condition `satisfied`. |
| C02 | Exact current VCN pin plus CN `violated` yields condition `violated`. |
| C03 | Exact current VCN pin plus CN refusal yields condition `not_evaluated`. |
| C04 | Current VCN different from pin yields `superseded`; current result remains visible but cannot contribute. |
| C05 | CN fork remains `conflicted` even if one tip equals the pin. |
| C06 | A uniquely current CN declaration after full convergence contributes only when its ID equals the pin. |
| C07 | All satisfied yields executed `matches` and complete coverage. |
| C08 | All evaluated with at least one violated yields executed `does_not_match`. |
| C09 | One admitted violation plus an unevaluated sibling yields executed `does_not_match` and incomplete coverage. |
| C10 | No violation plus any unevaluated condition yields not-executed and no computed match. |
| C11 | State not registered/not declared/inactive/conflicted never yields a computed match. |
| C12 | Every independently applicable refusal remains ordered and visible. |
| C13 | `does_not_match` never establishes another state. |
| C14 | Multiple state identities may simultaneously `matches`; no winner is derived. |
| C15 | CN parser parity failure propagates and never becomes a refusal or `does_not_match`. |

### 18.8 Time, provenance, and hostile reconstruction

| ID | Acceptance condition |
|---|---|
| T01 | Aware cutoff is UTC-normalized; naive or offset-less cutoff rejects. |
| T02 | Changing `as_of` can change evidence but not model membership. |
| T03 | Changing context can change declaration lifecycle but not filter temporal candidates. |
| T04 | Different receipt/source times and clock domains remain disclosed and may be used under the independent basis. |
| T05 | Close timestamps do not create cohort/synchronization; wide separation does not create a silent staleness veto. |
| T06 | No interpolation, resampling, lag compensation, range search, persistence, or source-time equality exists. |
| T07 | Model, binding, interpretation, cutoff, and occurrence times remain separate axes. |
| T08 | Mixed model/binding/interpretation revisions or cutoffs reject. |
| T09 | Selector, candidate, occurrence, raw record, and provenance substitution reject when detectable from carried material. |
| T10 | Forged pin alignment, outcome, coverage, temporal status, refusal, execution, or match rejects. |
| T11 | Nested `model_construct`, `model_copy`, stale IDs, and extra implication-bearing fields reject. |
| T12 | Full validator works with stores and filesystem monkeypatched to fail. |
| T13 | Executable limitation twin documents a fully coherent lower mutation outside raw-authentication scope. |
| T14 | No claim says payload checksum authenticates uncaptured bytes. |

### 18.9 Non-inference and ST-002 exclusion

| ID | Acceptance condition |
|---|---|
| N01 | No state registration/declaration is inferred from constraint existence or satisfaction. |
| N02 | No state is inferred from observation value, change, order, correlation, or field name. |
| N03 | No state is inferred from same owner, hierarchy, CAD, geometry, port, VPA, PIF, PCN, or PCM. |
| N04 | No state is inferred from semantic/unit compatibility or BH equality. |
| N05 | Failing state A never establishes state B. |
| N06 | Public contracts contain no transition anchor, from/to, trigger, event, action, guard, entry/exit, executor, or next-state recommendation. |
| N07 | Two classifications at different cutoffs never produce a transition occurrence. |
| N08 | No result uses current-state, flow, cause, control, health, safety, diagnosis, correctness, or recommendation fields. |

### 18.10 Historical and fixture preservation

| ID | Acceptance condition |
|---|---|
| H01 | Explicit 9/10/11/14/16/18/28/29/32 memberships retain exact revisions. |
| H02 | Every pre-ST membership returns structured state absence. |
| H03 | Later cutoff cannot discover state records in a pre-ST membership. |
| H04 | Historical membership is never reconstructed by enumeration, prefix, timestamp, or append order. |
| H05 | All 32 predecessor model bytes are frozen before demo append and identical afterward. |
| H06 | Binding, interpretation, source, temporal, structural, CN, PT, VP, and BH fixtures remain unchanged. |
| H07 | Accepted CN/PT/VP/BH artifact hashes remain exact. |
| H08 | Base-only and all-extras clean checkouts reproduce revisions, tests, and deterministic artifacts. |
| H09 | Hash seed, file enumeration order, source-row order, and clean environment do not change serialized output. |
| H10 | `git diff --check`, compilation, architecture checks, focused suites, and full suite pass at every authorized completion gate. |

## 19. Bounded synthetic demonstration scope

### 19.1 Recommended model evolution

The current repository can honestly demonstrate one state without adding new
variables, specifications, semantics, constraints, bindings, interpretations,
or observations. Recommend an owner-gated evolution:

```text
32 records → 34 records
```

Append exactly:

1. one `StateRegistration`;
2. one parentless `StateDeclaration`.

The proposed state is a neutrally named synthetic state with:

- one newly minted and owner-frozen `StateAnchor`;
- subject `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- permanent singleton condition set
  `con_4b768cf843f5474cb5e564e31d239a59`;
- family `all_of_constraints`;
- exact VCN pin
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`;
- exact `lifecycle_view/as_operated` context;
- evaluation basis `independent_latest_at_or_before_cutoff`;
- synthetic `test_fixture / st001_demo_fixture / manual_declaration`
  authority and claim-specific evidence.

The human-facing name must be neutral, for example “Synthetic constraint-match
state.” It must not say hot, ready, operating, normal, safe, fault, alarm,
command, target, control, or any real-printer mode.

Do not append:

- another entity, variable, VSP, VSM, CRG, VCN, port, VPA, behavior, or
  relationship;
- state family, exclusivity, completeness, withdrawal, correction, fork, or
  second root;
- binding declaration/assertion;
- source interpretation, observation, temporal record, or source evidence;
- transition, trigger, action, event, or state-machine record.

Shared ownership does not create the state. The existing CN satisfaction does
not create it. Only the explicit SRG and STD do.

### 19.2 Demonstration classification

Using the accepted explicit source selector and complete committed observation
timeline at cutoff `2026-08-07T20:30:00+00:00`, the direct CN result remains:

```text
current VCN pin: exact_current
observed canonical value: 60.4
predicate: inclusive upper bound 80
CN verdict: satisfied
```

The ST result may therefore demonstrate:

```text
state declaration: declared / healthy
condition coverage: complete
temporal alignment: not_asserted
execution: executed
computed_match: matches
```

This is an evidence-relative application of a later selected model knowledge
revision to an earlier temporal cutoff. It does not claim that the declaration
existed at the cutoff, because `recorded_at` is not a validity interval.

`does_not_match`, incomplete evidence, multiple conditions, simultaneous
matching states, stale VCN pins, CN conflict, state conflict, and withdrawal
remain disposable test worlds. They must not expand the committed demo.

### 19.3 Mandatory pre-append gate

Exact state anchor, record IDs, canonical bytes, file hashes, 34-record
membership, final revision, artifact bytes, and artifact SHA-256 must not be
invented in this design. Before authoritative append, Slice D must:

1. allocate one candidate StateAnchor through the public minter exactly once;
2. freeze it in a candidate manifest;
3. copy the exact 32-record ledger into at least two independent disposable
   roots;
4. construct records only through public builders and append only through
   public `ModelStore`;
5. replay the explicit candidate membership and run public kernel/CN/ST APIs;
6. generate the deterministic disclosure artifact twice;
7. prove exact identity, bytes, hashes, query results, classifier result, and
   predecessor preservation across both roots and clean environments;
8. present the candidate identities and artifact contract for owner approval;
9. perform no authoritative append until that approval is granted.

This pre-append approval is a Slice D gate, not a blocker for Slices A–C.

### 19.4 Mandatory disclaimer

> This is an illustrative synthetic ST-001 state declaration and evidence classification fixture. `matches` means only that the explicitly selected admitted observation satisfied the referenced synthetic constraint under the stated context, cutoff, and revisions. It does not claim that a real printer is currently in this state, that the state is exclusive or complete, that any transition occurred, or that temporal order establishes cause, control, safety, health, diagnosis, correctness, or recommended action.

Documentation and artifact warnings must also state that names, shared
ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM, BH declarations, semantic
compatibility, CN satisfaction alone, temporal correlation, and observation
changes did not create the state; and that displaying an observation beside a
state does not make the observation a persisted state fact.

## 20. Owner-gated implementation plan

Every slice begins with design/status documentation and red tests, uses
specialist review, commits in reviewable groups only when authorized, runs the
specified verification, and stops for owner acceptance. No later slice begins
implicitly.

### 20.1 Slice A — identity and model-record foundation

Implement only:

- `StateAnchor`, pattern, and UUID4 minter;
- SRG/STD/STW and nested pin contracts;
- canonical prefixes, builders, evidence arms, and exports;
- hostile nested-instance revalidation;
- store admission, immutable indexes, lifecycle, withdrawal, and explicit
  historical replay;
- documentation, golden vectors, red-first store/canonical/adversarial tests.

Do not implement kernel state queries, state evaluation, source selection, or a
fixture. Stop for owner acceptance.

### 20.2 Slice B — read-only kernel queries

Implement only:

- exactly `state`, `state_declaration`, `states_of_entity`, and
  `state_assertion`;
- carry-once result contracts and exact public vocabularies;
- lifecycle, body-group, corroboration, disagreement, inactive-history, and
  assertion disclosure;
- deterministic ordering and authoritative store-independent reconstruction;
- hostile material/index/revision/context/ordering tests.

Do not implement the evaluator or fixture. Stop for owner acceptance.

### 20.3 Slice C — evidence-gated classifier

Implement only:

- `backend/state_evaluation` and the exact public surface in Section 12;
- explicit condition sources and deterministic public-CN scheduling;
- exact VCN-pin alignment, independent temporal-basis disclosure, truth table,
  refusals, and carried-material revalidation;
- disposable satisfied, violated, missing, conflicted, stale, mixed,
  multi-condition, and multiple-state worlds;
- architecture/import, DoS, lower-error, and coherent-mutation limitation
  tests.

Do not append fixtures or persist classifications. Stop for owner acceptance.

### 20.4 Slice D — bounded synthetic demonstration

Slice D has two mandatory owner gates:

1. **Pre-append rehearsal gate**: mint/freeze the candidate once, reproduce two
   disposable append/artifact runs, and present exact candidate IDs, bytes,
   hashes, membership, revision, classifier disclosure, and artifact contract.
2. **Authoritative append gate**: only after exact candidate approval, append
   the one SRG then one STD through public APIs, verify after each append, pin
   explicit 32/34 memberships, generate the accepted artifact, run full and
   dual-clean-checkout verification, and stop for final acceptance.

No transition work is part of Slice D.

### 20.5 Verification expectations per implementation slice

As applicable, run focused ST tests, complete system-identity/model-kernel/CN
and state-evaluation tests, model-state/binding/temporal/semantic affected
suites, architecture/import-isolation tests, all explicit historical replay
tests, PT/VP/BH artifact-preservation tests, full repository suite, base-only
and all-extras clean checkouts, backend compilation, `git diff --check`, and
branch/topology/status checks. Sandbox-denied loopback tests must be reported
separately and rerun with required permission.

## 21. Explicit exclusions and known limitations

### 21.1 ST-002 boundary

ST-001 deliberately contains no:

- transition anchor or stable transition identity;
- from-state or to-state direction;
- trigger, event, guard-to-transition mapping, transition occurrence, or
  transition timestamp;
- entry/exit action, command, side effect, actuator instruction, or executor;
- state-machine graph, runtime, next-state recommendation, or persistence;
- causal interpretation of value changes or classification order.

A later `matches` after an earlier `does_not_match` is two classification
results, not a transition. A value change is not a transition. Temporal order is
not cause. ST-002 must introduce its own explicit identities, evidence,
contexts, lifecycle, occurrence semantics, and safety boundary.

### 21.2 Other v1 limitations

- Named states are entity-subject only; variable-level numeric findings remain
  CN results.
- The condition set and all-of family are permanent for one state identity.
- Conditions are limited to accepted CN exact numeric predicates.
- A VCN correction makes an old exact state pin stale until an explicit STD
  correction; the append-only intermediate revision is intentional.
- The classifier uses independently latest observations and asserts no temporal
  alignment or simultaneity.
- No staleness threshold, sampling policy, interpolation, or historical fallback
  exists.
- No unit conversion, ontology inference, tolerance, or dimensional algebra
  exists.
- No state family, exclusivity, completeness, priority, or winner exists.
- No bulk “classify all states” facade or variable/port reverse query exists.
- Human-facing anchor metadata has no ledger correction record in v1.
- Constraint use retains CN's normative meaning; arbitrary descriptive state
  predicates are unsupported.
- Upper authoritative validation inherits lower raw-authenticity limitations.
- Computed classification is never persisted as model or temporal truth.

## 22. Genuine unresolved owner questions

The lead recommendation is complete, but implementation must not begin until
the owner adjudicates these genuine contract choices:

1. **Permanent identity boundary** — approve that one state identity permanently
   fixes its entity subject, canonical constraint-anchor set, and
   `all_of_constraints` family; changing any requires a new `sta_`.
2. **Cross-entity conditions** — approve explicit evidence-bearing SRG inclusion
   of constraints targeting variables owned by other entities, with no inferred
   hierarchy, flow, or causality.
3. **Exact VCN pins** — approve pinning one exact VCN per condition and treating
   a later unique VCN as `superseded` state-condition alignment until STD
   correction.
4. **Bound** — approve the 1–64 condition limit and mandatory 64/65 tests.
5. **Temporal basis** — approve
   `independent_latest_at_or_before_cutoff`, no cohort requirement, and explicit
   `temporal_alignment="not_asserted"`.
6. **Mixed truth precedence** — approve that one admitted `violated` conjunct
   yields `does_not_match` even with an unevaluated sibling, while coverage
   remains incomplete and every refusal remains disclosed.
7. **No family** — approve deferring all exclusivity/completeness/family
   semantics beyond ST-001.
8. **Exact public names** — approve `sta_`/`srg_`/`std_`/`stw_`, the four kernel
   methods, and the single `state_classification` facade method.
9. **Demonstration** — approve planning a two-record 32→34 singleton-condition
   demo that returns only evidence-relative `matches`, subject to a separate
   pre-append identity/artifact gate.

No candidate identity, canonical record ID, final 34-record revision, or ST
artifact hash is an unresolved blocker for Slices A–C; those are intentionally
deferred to the Slice D owner gate.

## 23. Proposed ADR-0016 outline

Title:

```text
ADR-0016 — First-Class State Identity and Evidence-Gated Classification
```

Status: `Proposed` until owner acceptance.

### Context

- The repository has explicit variables, semantics, constraints, ports,
  associations, behavior declarations, and read-only evidence composition, but
  no first-class state identity.
- Observation, constraint satisfaction, value change, and temporal order must
  not be relabeled as state or transition.
- The kernel cannot import temporal/binding/semantic/evaluation layers.

### Decision

- Add opaque `StateAnchor` in `system_identity`.
- Add SRG/STD/STW to the existing model ledger; no new ledger/store/revision.
- Permanently bind state identity to one entity, 1–64 constraint anchors, and
  `all_of_constraints`.
- Pin exact VCN records in exact-context declarations.
- Use BH-style multi-root lifecycle/corroboration and minimal withdrawal.
- Add four read-only kernel queries with carry-once authoritative results.
- Add read-only `backend/state_evaluation` over explicit public CN branches.
- Use independently latest evidence at one cutoff with temporal alignment not
  asserted.
- Return only `matches | does_not_match | not_evaluated`; allow multiple
  matches; persist no result.
- Add no state family or transition semantics.

### Consequences

- State declaration becomes explicit, evidence-backed model knowledge.
- Classification is reproducible and revision/cutoff/source relative.
- Exact VCN correction cannot silently alter a state declaration.
- VCN correction creates an honest intermediate stale-pin revision.
- v1 is intentionally limited to all-of exact numeric CN conditions.
- Multiple states may match and no current-state winner exists.
- Raw-source authenticity remains inherited, not re-proven.

### Rejected alternatives

- generic relationship/variable attribute;
- constraint result alone;
- duplicated predicates;
- state family/exclusivity in v1;
- separate state ledger/store;
- executable state machine.

### Follow-on

ST-002, under a separate owner-approved design, may consider transition
identity, from/to direction, triggers, transition occurrences, actions, and
execution. It must not retroactively reinterpret ST-001 records or derive
transitions from classification changes.

END OF ST-001 CODEX LEAD PROPOSAL
