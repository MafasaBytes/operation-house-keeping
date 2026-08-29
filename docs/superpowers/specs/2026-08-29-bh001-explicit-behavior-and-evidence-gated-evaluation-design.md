# BH-001 — Explicit Behavior Declarations and Evidence-Gated Evaluation

Status: corrected final synthesis and Slice A owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. Slice B is owner accepted
at `05177f7306ce745d093bd5f11abafc13a6274d0f`. Slice C is owner-authorized but
not yet implemented. Slice D has not started.

Repository baseline: `main` at
`46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`.

BH-001 defines a deliberately narrow first behavior primitive: an explicit,
evidence-backed, context-specific exact numeric-equality relation between two
registered variables. Declarations are model knowledge. Evaluation is a
separate read-only composition over explicitly selected source-backed state.
Neither layer infers behavior from topology, observations, semantics, names,
ownership, or compatibility.

## 1. Repository findings

The accepted repository establishes the following constraints.

1. System identities are opaque UUID4-backed anchors. Human-facing names and
   roles are descriptive and are never matching criteria. Newer anchor types
   use frozen, extra-forbidden, full-instance revalidation.
2. The model kernel owns revision-relative explicit model knowledge in one
   append-only model ledger. Runtime kernel code imports only
   `backend.system_identity`, Pydantic, and the standard library.
3. `AssertionContext` is the existing canonical context contract for model
   assertions.
4. Existing correctable claims use content-addressed records, correction DAGs,
   explicit withdrawals, deterministic replay, and immutable indexes.
5. `VariablePortAssociation` is intentionally positive and role-free. It does
   not establish flow, behavior, input/output direction, causal influence, or
   an observation at a port.
6. `ModelStateQueries.variable_state()` keeps observations attached to
   variables through the identity-binding and temporal-evidence pipeline.
   Displaying variable state beside a port does not relocate the observation.
7. Semantic compatibility composes model declarations, source interpretation,
   and variable state without unit conversion or ontology inference.
8. CN-001 exposes the accepted public bounded exact-number parser,
   `parse_observed_decimal`, and its canonical result type,
   `CanonicalObservedDecimal`.
9. The accepted `TemporalOccurrence` carries the repository facts needed to
   identify an acquisition envelope: `subject.source_id`,
   `subject.adapter_id`, `attempt_id`, `raw_record_id`, and
   `payload_checksum`.
10. An explicit `SourceSelector` produces one selected source locator
    candidate. Selection does not create a binding and does not establish
    attachment.
11. Authoritative kernel results carry complete `ModelQueryMaterial` once,
    rebuild the selected model without filesystem or store access, and
    reconstruct nested Pydantic instances from serialized field content.
12. The committed demo currently contains exactly 29 model records at
    `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`
    and has only one registered variable.
13. Historical model memberships are explicitly pinned at 9, 10, 11, 14, 16,
    18, 28, and 29 records. They are never reconstructed by directory
    enumeration or chronology.
14. The committed fixture seam currently requires registered model anchors to
    match committed identity-binding `AnchorDeclaration` records. BH-001's
    declaration-only demonstration has an owner-authorized exception for
    exactly one new synthetic variable. That exception must be pinned exactly
    and must not become a general weakening of the seam.
15. No BH record, package, prefix, query, evaluator, or fixture exists at the
    accepted baseline.

These facts mean BH-001 needs neither a new dependency nor a new store. They
also mean the current committed model is insufficient for an honest
two-variable evaluation demonstration without additional model knowledge.

## 2. Core problem statement

The smallest honest BH-001 declaration says only:

> In this selected model revision and exact assertion context, an accountable
> authority declares, with explicit evidence, that two distinct registered
> variables participate in an exact numeric-equality relationship.

It is explicit model knowledge, not a finding derived from values, topology,
names, semantics, compatibility, or shared ownership.

Evaluation asks a separate question:

> Given two explicitly selected source-backed observations that independently
> pass all model, binding, semantic, unit, numeric, and acquisition-envelope
> gates, are their canonical numeric values mathematically equal or different?

Declaration and evaluation are separate truth dimensions and separate
owner-gated implementation slices.

## 3. Architectural alternatives and explicit exclusions

### 3.1 Stable anchor, existing-ledger declarations, upper evaluator

A permanent `BehaviorAnchor` and evidence-bearing `BehaviorRegistration`
define enduring identity and the fixed unordered variable pair. Correctable,
context-specific declarations live in the existing model ledger. A separate
read-only composition evaluates explicitly selected evidence.

This is the accepted recommendation.

### 3.2 Declaration-lineage identity only

A smaller alternative would identify a behavior only by a root `bhd_` record.
That makes continuity ambiguous when a declaration is corrected, renamed, or
replaced and leaves no permanent identity boundary for the participant pair.
It is rejected.

### 3.3 Separate behavior ledger or executable-model layer

A separate behavior ledger would introduce another revision axis and
cross-ledger closure problem. Executable expressions, scripts, external model
references, or plugin-defined operators would introduce canonicalization,
security, reproducibility, and denial-of-service risks. These alternatives are
rejected.

Widening generic relationship records or VPA is also rejected because their
accepted meanings cannot carry BH-001's declared rule truth.

## 4. Lead recommendation and normative meaning

BH-001 uses:

- `BehaviorAnchor` / `bhv_`;
- `BehaviorRegistration` / `brg_`;
- `BehaviorRuleDeclaration` / `bhd_`;
- `BehaviorRuleWithdrawal` / `bhw_`;
- the existing model ledger and `mrv_` revision;
- a separate read-only `backend/behavior_evaluation` package;
- exactly one rule family: `exact_numeric_equality`.

It creates no behavior-specific ledger, store, revision, projection, cache,
database, expression engine, or executable model.

Normative declaration meaning:

> Under the exact `AssertionContext` and selected model membership, an
> accountable authority declares, with cited evidence, that the two distinct
> registered variables identified by the behavior registration participate in
> the exact numeric-equality relation described by the current declaration.

This does not declare input/output direction, source/dependent ordering,
cause/effect, command/response, control, signal direction, flow, state
transition, physical simultaneity, correctness, safety, health, or expected
operation.

Evaluation may establish only `equal` or `different` for two admitted
canonical numbers. It does not establish whether the declared behavior is
valid, correct, healthy, safe, causal, satisfied, or operational.

## 5. Exact identity and record contracts

### 5.1 BehaviorAnchor

```python
class BehaviorAnchor:
    anchor_id: Annotated[str, pattern=r"^bhv_[0-9a-f]{32}$"]
    namespace: BoundedNamespace
    display_name: NonEmptyText
    role_name: BoundedRoleName | None = None
```

It follows the newer `ConstraintAnchor` and `PortAnchor` convention:

```python
ConfigDict(
    frozen=True,
    extra="forbid",
    revalidate_instances="always",
)
```

`mint_behavior_anchor()` uses `uuid4().hex` and performs no persistence or
I/O. The anchor contains no owner, variable, context, rule, evidence,
authority, state, direction, participant role, or lifecycle field.

Names are human context only. A rename does not create a new identity, but
BH-001 v1 does not mutate the label embedded in a permanent registration. A
future non-identity metadata mechanism may disclose aliases. Replacing either
participant or the rule family requires a new behavior anchor.

### 5.2 BehaviorRegistration

```python
class BehaviorRegistration:
    record_kind: Literal["behavior_registration"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^brg_[0-9a-f]{64}$"]

    anchor: BehaviorAnchor
    participant_variable_anchor_ids: CanonicalTwoVariableAnchorIds
    rule_family: Literal["exact_numeric_equality"]

    evidence: NonEmptyCanonicalEvidenceTuple
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

The participant tuple is exactly length two, contains two distinct valid
`var_` IDs, is unordered in engineering meaning, and is canonicalized by
variable ID before identity derivation. It is permanent for the behavior
anchor.

Registration has no `AssertionContext`, parents, correction, withdrawal,
lifecycle, state, owner, port, or direction field.

Store admission requires:

1. both exact variable registrations;
2. both exact owner entity registrations;
3. `ModelRecordEvidence` citations to both exact variable-registration IDs;
4. at least one `OwnerDeclarationEvidence` that explicitly supports the
   authority's decision to register the relationship;
5. reference closure for every additional evidence item.

Other evidence arms may supplement but never replace the two exact VRG
citations and explicit owner declaration. Raw evidence, topology, semantics,
VPA, names, or common ownership cannot create the registration.

Cross-owner variable pairs are allowed only through an explicit evidence-
backed BRG. Shared ownership neither creates nor strengthens behavior. A
selected membership admits at most one BRG for a `bhv_`.

### 5.3 BehaviorVariableSemanticLock

```python
class BehaviorVariableSemanticLock:
    variable_anchor_id: VariableAnchorId
    signature: ConstraintSemanticSignature
```

The declaration carries exactly two locks, unique and canonically sorted by
`variable_anchor_id`. The lock IDs must equal the BRG participant pair.
Signatures are never stored as a separately sorted tuple because doing so
would allow quantity, observation-role, or unit locks to be substituted
between variables.

The two locks must have identical quantity-kind identities and identical unit
identities. Observation-role identities may differ. Locks do not create or
replace VSP, VSM, source-interpretation, or unit declarations.

### 5.4 ExactNumericEqualityRule

```python
class ExactNumericEqualityRule:
    kind: Literal["exact_numeric_equality"]
```

No other field is permitted.

### 5.5 BehaviorRuleDeclaration

```python
class BehaviorRuleDeclaration:
    record_kind: Literal["behavior_rule_declaration"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^bhd_[0-9a-f]{64}$"]

    behavior_anchor_id: BehaviorAnchorId
    context: AssertionContext
    participant_semantics: CanonicalTwoBehaviorVariableSemanticLocks
    rule: ExactNumericEqualityRule
    evaluation_basis: Literal["same_acquisition_cohort"]

    evidence: NonEmptyCanonicalEvidenceTuple
    supersedes: CanonicalBehaviorRuleDeclarationIdTuple
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

Admission requires the corresponding BRG, exact participant-lock equality,
equal quantity-kind identities, equal unit identities, a citation to the exact
BRG, at least one `OwnerDeclarationEvidence` for the declaration, evidence
closure, and valid same-subject parents.

The model store does not require current VSP or VSM records and does not test
locks against source interpretation. Those are evaluation-time gates. This
separation permits a declaration-only fixture without inventing evaluability.

All nested inputs—including context, locks, signatures, rule, evidence, and
authority—must be reconstructed from serialized fields. Existing nested
Pydantic instances cannot be trusted merely because their type is correct.

### 5.6 BehaviorRuleWithdrawal

```python
class BehaviorRuleWithdrawal:
    record_kind: Literal["behavior_rule_withdrawal"]
    schema_version: Literal["1"]
    record_id: Annotated[str, pattern=r"^bhw_[0-9a-f]{64}$"]

    withdraws: BehaviorRuleDeclarationId
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

BHW has no evidence, context, parents, outcome, replacement, reason code, or
negative-behavior field. It is uncitable. Its subject and context are inherited
from the target declaration.

A withdrawal means only that the targeted positive declaration is no longer
asserted in the selected membership. It does not mean the relationship was
false, impossible, physically removed, or operationally stopped.

## 6. Canonical prefixes and serialization impact

Add exactly:

```text
bhv_  BehaviorAnchor
brg_  BehaviorRegistration
bhd_  BehaviorRuleDeclaration
bhw_  BehaviorRuleWithdrawal
```

Required additive identity changes are:

- `bhv_` in system-identity grammar and the public minter;
- `brg_`, `bhd_`, and `bhw_` in model-record and filename grammars;
- all three record discriminators in `ModelRecord`;
- exact canonical kind-to-prefix mappings;
- `brg_` and `bhd_` in `ModelRecordEvidence`;
- `bhw_` excluded from citable evidence.

Record IDs remain:

```text
<prefix>_<sha256(canonical record content excluding record_id)>
```

No existing canonical bytes, hashes, schemas, prefixes, or IDs change.

Caller ordering of the BRG pair, semantic locks, evidence, and valid parent
IDs cannot affect canonical bytes. Duplicate participants or parents are
rejected before canonical ordering.

The effective engineering body used for corroboration is a separate canonical
projection. It is not persisted as an identity or digest.

## 7. Participant and role semantics

BH-001 has exactly two variable participants and no participant-role field.
The pair is symmetric and unordered. It contains no `input`, `output`,
`parameter`, `command`, `state`, `disturbance`, `source`, `dependent`,
`sensor`, or `actuator` label.

Observation-role identities inside semantic locks describe declared variable
meaning in the existing semantic vocabulary. They are not BH participation
roles and do not make the equality relation directional, causal, or
operational.

Variables may belong to the same or different entities. Ports and VPAs are
irrelevant to BH admission.

## 8. Behavior-rule representation

BH-001 v1 supports exactly `exact_numeric_equality`. It declares no operator
beyond exact equality and carries no operand/result distinction.

The following are prohibited in BH-001:

- affine coefficients or offsets;
- tolerance or approximate equality;
- arbitrary expressions, ASTs, bytecode, or scripts;
- inequalities, predicates, or constraint verdicts;
- lookup tables;
- state transitions, delays, derivatives, histories, or windows;
- external model references;
- behavior chaining or recursion;
- executable code or user-defined imports.

BH-002 may later introduce directional functional dependencies, affine
predictors, tolerances, dimensional algebra, or another bounded rule family.
Existing BH-001 records never acquire those meanings retroactively.

## 9. Lifecycle, correction, conflict, and corroboration

The lineage key is:

```text
(behavior_anchor_id, exact AssertionContext)
```

Claims in different contexts do not supersede, corroborate, or conflict with
one another. They are queried independently.

A parentless BHD starts an independent declaration root. Within one root:

- zero active tips means `inactive`;
- one active tip means `healthy`;
- multiple active tips mean `conflicted`, even when their effective bodies are
  identical;
- multi-parent convergence may cite tips from that same root;
- partial convergence leaves remaining forks conflicted;
- cross-root convergence is invalid.

The effective engineering body is the canonical projection of exactly:

```text
behavior_anchor_id
context
participant_semantics  # variable-keyed and variable-sorted
rule
evaluation_basis
```

It excludes:

```text
record kind
schema version
record ID
evidence
supersedes
authority
recorded_at
note
filename
append order
```

The projection is serialized through the accepted canonical JSON rules and
compared by bytes. Whole-record bytes, Pydantic equality, `repr`, record IDs,
timestamps, and file ordering must not determine engineering-body equality.

Across active healthy roots:

- one effective-body group means the declaration is `declared`;
- multiple roots in that one group are independent corroboration;
- more than one effective-body group means `conflicted`.

Any active same-root conflict makes the aggregate conflicted. Inactive roots
remain disclosed but do not vote. With roots but no active tips, the aggregate
is `inactive`. With no roots, it is `not_declared`.

No authority, timestamp, ID, filename, or append order selects a winner.

Corrections and withdrawals are membership-relative. Replaying a membership
without a later successor revives the predecessor as current. Replaying one
without a later withdrawal revives the target.

Extra citations to correctable model records prove historical support in the
selected membership; they do not silently establish currentness. Current
VSP/VSM/source semantics are independently reassessed during evaluation.

## 10. Withdrawal rules

A BHW may target one unsuperseded, unwithdrawn current BHD tip. Reject:

- malformed or unknown targets;
- non-BHD targets;
- BRG or BHW targets;
- superseded targets;
- already-withdrawn targets;
- duplicate withdrawals;
- a successor and withdrawal of the same target in one membership;
- a correction from a target that remains withdrawn in the selected
  membership.

Selective withdrawal of one fork tip is allowed and may resolve a same-root
conflict. Withdrawing all active tips makes the root inactive. It never asserts
that behavior was false or that physical behavior stopped.

## 11. Port and VPA boundary

BH-001 contains no:

- port field;
- VPA field or citation requirement;
- port qualification;
- behavior query by port;
- signal-path model;
- value-at-port result.

A variable may participate without a registered port. VPA correction or
withdrawal has no effect on BH declaration or evaluation.

A caller may display BH and VP results independently. It must not merge them
into `behavior at this port`, `value travelling through this port`, signal
direction, behavior inferred from connectivity, or port-mediated causality.

Any future port qualification requires a separately named contract and owner
gate. Existing BHD records cannot silently acquire port meaning.

## 12. Semantic and unit admission

For each evaluated participant, evaluation requires:

1. a registered variable and registered owner;
2. a current unique numeric VSP;
3. a current unique quantity-kind declaration;
4. a current unique observation-role declaration;
5. a current exact declared unit identity;
6. source interpretation admitted through the existing pipeline;
7. candidate-local declared-semantics compatibility;
8. exact correspondence with that participant's variable-keyed BH lock.

Across participants:

- quantity-kind identities must be exactly equal;
- unit identities must be exactly equal;
- observation-role identities may differ;
- no conversion is attempted;
- no token aliasing or ontology inference is attempted;
- no dimensional algebra is introduced.

These gates admit exact mathematical comparison. They do not prove the
behavior declaration or transform equality into engineering truth.

CN constraints and findings remain independent. Constraint satisfaction or
violation cannot create, corroborate, refute, or evaluate a BH declaration.

## 13. Temporal alignment policy

BH-001 uses exact same-acquisition-cohort admission. The cohort key is exactly:

```python
(
    occurrence.subject.source_id,
    occurrence.subject.adapter_id,
    occurrence.attempt_id,
    occurrence.raw_record_id,
    occurrence.payload_checksum,
)
```

No other occurrence field participates. Specifically excluded are:

- source-native time;
- received, finished, or attempt-start time;
- receipt-time proximity;
- clock segment;
- ingestion run or sweep position;
- subject identifier;
- property, observation, or occurrence IDs;
- value or unit;
- quality or change flags.

Equality of the cohort key means only:

> Both properties were emitted from the same accepted acquisition envelope.

It does not prove physical simultaneity, synchronized clocks, equal sampling
times, causal ordering, or temporal persistence.

There is no configurable skew, interpolation, resampling, lag compensation,
range search, historical fallback, persistence assumption, or receipt-time
tolerance. There is no `max_receipt_age_seconds` field or arbitrary age gate.

`as_of` selects temporal evidence only. It never chooses, mutates, or
reinterprets model membership. Staleness remains disclosed through accepted
lower-layer results and does not silently change mathematical equality.

## 14. Explicit participant-source selection

Evaluation requires exactly two explicit participant selectors:

```python
class BehaviorParticipantSource:
    variable_anchor_id: VariableAnchorId
    entity_anchor_id: EntityAnchorId | None
    source: SourceSelector
```

The tuple is exactly length two, distinct by variable ID, and canonically
sorted. `source` is required; only `entity_anchor_id` is optional.

If the behavior exists, the selector variable set must equal the BRG pair.
Substitution is a typed input error before lower evidence access. If a valid-
shaped behavior anchor is absent, the supplied two selectors define the two
independent evidence queries.

There is no implicit discovery, authority ranking, recency ranking, record-ID
ranking, candidate-order selection, or candidate cross-product. Each explicit
selector yields one accepted lower state/semantic path or an explicit refusal.

For every structurally valid request, participant evidence is preserved when
the behavior is not registered, not declared, inactive, or conflicted.
Declaration failure never erases independent observations. A typed lower-layer
failure propagates unchanged; the evaluator does not manufacture a result
after such a failure.

## 15. Numeric evaluation and parser boundary

BH-001 reuses the public CN-001 exact-number parser:

```text
backend.constraint_evaluation.parse_observed_decimal
backend.constraint_evaluation.CanonicalObservedDecimal
```

The dependency is limited to this public numeric parsing API. BH does not
import constraint registrations, queries, verdicts, or semantics and does not
copy private CN parser logic. Slice C must reuse the public parser and its
public typed failures exactly. BH must not copy, fork, wrap permissively, or
privately reimplement that parser.

The accepted bounded lexical preflight must occur before numeric work or large
numeric allocation. Slice C must demonstrate exact parity with the inherited
CN limits. The public CN parser remains the authoritative lexer, bounds
checker, canonicalizer, and parity boundary.

BH must not use:

- `float`;
- ambient `Decimal` context;
- rounding or quantization;
- tolerance;
- subtraction or absolute difference;
- unit conversion;
- a copied regex or private parser implementation.

After both values are admitted, exact equality is comparison of the two
canonical numeric strings. CN canonicalization therefore handles equivalent
numeric spellings and negative zero without BH arithmetic.

Parser parity failures are typed integrity failures and propagate honestly.
They never become `different`, `not_executed`, or an ordinary participant
refusal.

Mandatory Slice C boundary tests include admitted twins and one-step-over
hostile values for every inherited CN limit dimension:

- input byte count;
- coefficient or mantissa digit count as named by the CN grammar;
- fractional digit count;
- exponent representation length;
- absolute exponent magnitude;
- expanded digit count;
- expanded fractional digit count;
- canonical output byte size.

Boolean, object, array, null, malformed, oversized, and expansion-hostile
`value_json` values must never reach behavior comparison as numbers. Ambient
decimal context must not affect admission, canonicalization, or equality.

The accepted semantic pipeline already parses `value_json` before BH receives
its result. BH can guarantee bounded work for its own numeric parsing, but it
cannot claim a new whole-stack hostile-input bound without a separately
authorized lower-layer change. Within BH-001, public-parser reuse, bounded
preflight, parity tests, hostile-shape refusal, and honest typed-failure
propagation are a mandatory Slice C hardening gate, not a separate
implementation slice. BH must not duplicate model-state reads merely to
manufacture a broader claim.

## 16. Evaluation architecture and gate order

Evaluation belongs in:

```text
backend/behavior_evaluation
```

with one read-only facade:

```python
class BehaviorEvaluationQueries:
    def __init__(self, semantic: SemanticCompatibilityQueries): ...

    def behavior_evaluation(
        self,
        behavior_anchor_id,
        *,
        context,
        as_of,
        participants,
    ) -> BehaviorEvaluationResult:
        ...
```

The facade constructs `ModelQueries` over the exact `LoadedModel` behind the
injected semantic facade. It invokes each participant's public semantic query
exactly once and carries each result exactly once. It performs no direct store,
resolver, temporal-database, interpretation-store, or filesystem access.

For valid input, both participant evidence branches are executed before
ordinary lifecycle or admission outcomes are returned. If a lower typed error
aborts one branch, that error propagates and no BH result is fabricated.

Execution gates are evaluated in this order:

1. behavior registration and exact-context declaration lifecycle;
2. both participant-local model, observation, attachment, semantics, unit,
   lock, and numeric-shape gates;
3. exact acquisition-cohort equality;
4. public CN numeric admission for both lexemes in canonical participant
   order;
5. canonical numeric equality.

Cohort mismatch blocks execution and cannot become `different`. Numeric parity
errors cannot be hidden by an ordinary refusal from the other participant.

The evaluator owns no store, cache, projection, database, or file. It writes
nothing and never persists an evaluation as model or temporal truth.

## 17. Exact kernel query APIs and vocabularies

Add exactly four read-only `ModelQueries` methods:

```python
behavior(
    behavior_anchor_id,
) -> BehaviorLookupResult
```

```python
behavior_declaration(
    behavior_anchor_id,
    *,
    context,
) -> BehaviorRuleResult
```

```python
behaviors_involving_variable(
    variable_anchor_id,
    *,
    context,
) -> VariableBehaviorsResult
```

```python
behavior_assertion(
    record_id,
) -> BehaviorAssertionDisclosureResult
```

There are no aliases, alternate names, overloads, or port-scoped methods.

### 17.1 Public literals

```python
BehaviorLookupStatus = Literal[
    "not_registered",
    "registered",
]
```

```python
BehaviorDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]
```

```python
BehaviorRuleLineageSummary = Literal[
    "not_applicable",
    "healthy",
    "conflicted",
    "inactive",
]
```

```python
BehaviorAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]
```

```python
VariableBehaviorsStatus = Literal[
    "variable_not_registered",
    "registered",
]
```

```python
BehaviorAssertionLookupStatus = Literal[
    "not_found",
    "found",
]
```

Reuse accepted `AssertionActivity` and `ContainingLineageHealth`. The word
`healthy` is confined to declaration-DAG health. It is never an evaluation or
real-system finding.

### 17.2 Root and effective-body results

```text
BehaviorEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices
```

```text
BehaviorRuleRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices
```

All indices are strict nonnegative integers. Body groups are ordered by their
canonical projected bytes. Records inside each row are ordered by record ID.
Inactive roots have no active body-group vote but remain present in `roots`.

Agreement findings are a canonical tuple because more than one may apply. For
example, a same-root conflict may coexist with inactive historical roots.

### 17.3 BehaviorLookupResult

```text
BehaviorLookupResult
  material
  behavior_anchor_id
  status
  registration_index
  participant_variable_registration_indices
  participant_owner_registration_indices
```

The two participant and owner index tuples align with the canonical BRG pair.
Owner indices may repeat for same-owner variables while the authoritative
entity registration occurs only once in material.

For a valid absent anchor, status is `not_registered` and all indices are
`None` or canonical empty tuples as appropriate.

### 17.4 BehaviorRuleResult

```text
BehaviorRuleResult
  material
  behavior_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices
```

Conclusion derivation is:

| Registration | Roots | Active-root state | Effective bodies | Conclusion |
|---|---:|---|---|---|
| absent | any | not evaluated | not evaluated | `not_registered` |
| present | 0 | none | none | `not_declared` |
| present | >0 | no active tips | none | `inactive` |
| present | >0 | any same-root fork | any | `conflicted` |
| present | >0 | healthy active roots | one group | `declared` |
| present | >0 | healthy active roots | multiple groups | `conflicted` |

When declared, `lineage_summary="healthy"`. When conflicted or inactive it
matches that state. It is `not_applicable` for `not_registered` and
`not_declared`.

### 17.5 VariableBehaviorsResult

```text
VariableBehaviorEntry
  entry_index
  behavior_anchor_id
  other_variable_anchor_id
  behavior_registration_index
  other_variable_registration_index
  other_owner_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices
```

```text
VariableBehaviorsResult
  material
  variable_anchor_id
  context
  status
  variable_registration_index
  owner_registration_index
  entries
```

The reverse query returns every registered behavior containing the requested
variable in canonical behavior-anchor order, including exact-context
`not_declared` and inactive entries. It never infers registrations from common
owners or model facts. A registered variable with no behaviors returns
`status="registered"` and `entries=()`.

`entry_index` is contiguous from zero. There is no operand, result, input, or
output position field.

### 17.6 BehaviorAssertionDisclosureResult

```text
BehaviorAssertionDisclosureResult
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

`behavior_assertion()` accepts valid `brg_`, `bhd_`, and `bhw_` IDs:

- a found BRG is permanent and has lifecycle/root fields `None` and empty
  successor/withdrawal tuples;
- a found BHD discloses its activity, direct successors, withdrawals,
  containing-root health, and aggregate subject conclusion separately;
- a found BHW is an event with lifecycle/root fields `None` and empty tuples;
- a valid-shaped absent ID returns `not_found` with optional fields `None` and
  collections empty;
- malformed or non-BH IDs raise a typed query-input error before index access.

A BHD may be current in a healthy root while the aggregate subject is
conflicted by another root's different effective body. The result must not
collapse those dimensions.

## 18. Exact evaluator result contracts

### 18.1 Public status literals

```python
BehaviorEvaluationExecution = Literal[
    "not_executed",
    "executed",
]
```

```python
BehaviorComputedRelation = Literal[
    "equal",
    "different",
]
```

```python
BehaviorParticipantAdmission = Literal[
    "admitted",
    "not_admitted",
]
```

```python
BehaviorParticipantModelAdmission = Literal[
    "admitted",
    "not_admitted",
]
```

```python
BehaviorParticipantObservationAvailability = Literal[
    "observed",
    "none_before_cutoff",
    "not_evaluated",
]
```

```python
BehaviorParticipantAttachmentAdmission = Literal[
    "not_evaluated",
    "attached",
    "not_attached",
]
```

```python
BehaviorParticipantSemanticAdmission = Literal[
    "not_evaluated",
    "admitted",
    "not_admitted",
]
```

```python
BehaviorParticipantUnitAdmission = Literal[
    "not_evaluated",
    "exact",
    "mismatch",
]
```

```python
BehaviorParticipantLockAdmission = Literal[
    "not_evaluated",
    "matched",
    "mismatched",
]
```

```python
BehaviorParticipantNumericAdmission = Literal[
    "not_evaluated",
    "admitted",
    "out_of_bounds",
]
```

```python
BehaviorAcquisitionCohortAdmission = Literal[
    "not_evaluated",
    "same_acquisition_cohort",
    "different_acquisition_cohort",
]
```

There is no behavioral validity, correctness, consistency, health, safety,
control, or operating-state status.

### 18.2 Refusal vocabulary

```text
BehaviorEvaluationRefusal
  reason
  participant_index: strict nonnegative integer | None
```

The exact reason vocabulary is:

```text
behavior_not_registered
behavior_not_declared
behavior_inactive
behavior_conflicted
participant_model_not_registered
observation_absent
observation_not_attached
binding_not_positive
evidence_not_assessable
numeric_specification_not_available
numeric_specification_conflicted
model_quantity_kind_not_available
model_observation_role_not_available
source_semantics_not_admitted
quantity_kind_lock_mismatch
observation_role_lock_mismatch
unit_lock_mismatch
numeric_value_out_of_bounds
acquisition_cohort_mismatch
```

Multiple failed gates remain independently disclosed in deterministic
behavior-gate, participant, and gate-precedence order. A refusal is present
only when its exact source fact fails. It never stands in for a hidden winner
or aggregate validity verdict.

### 18.3 Participant result

```text
BehaviorEvaluationParticipantResult
  participant_index
  variable_anchor_id
  source_index
  semantic_result_index
  candidate_index
  model_admission
  observation_availability
  attachment_admission
  semantic_admission
  unit_admission
  lock_admission
  numeric_admission
  admission
  refusal_reasons
  canonical_decimal
```

The explicit source selector produces one lower candidate, so
`candidate_index` identifies that candidate and cannot represent ranking.
`canonical_decimal` is present exactly when numeric admission succeeds.

### 18.4 Top-level evaluation result

```text
BehaviorEvaluationResult
  behavior
  behavior_anchor_id
  context
  as_of
  ruleset_version
  participant_sources
  participant_semantic_results
  participants
  cohort_admission
  execution
  not_executed_reasons
  computed_relation
```

`ruleset_version` is exactly `bh001.1`.

The result carries the kernel behavior result once and exactly two lower
semantic results once. Participant rows refer to them using strict indices and
do not duplicate model, state, binding, interpretation, occurrence, or raw
evidence.

`computed_relation` is `None` exactly when execution is `not_executed`. It is
`equal` or `different` exactly when execution is `executed`. There is no
derived TemporalOccurrence, variable state, command, prediction, constraint
finding, or persisted result.

### 18.5 Independent result dimensions

The evaluator must keep these questions separate:

1. Is the behavior registered?
2. Is an exact-context declaration current, conflicted, or inactive?
3. Is each participant registered and owned?
4. Is an observation available for each explicit selector?
5. Is each observation attached to the requested variable?
6. Are source and model semantics admitted?
7. Is unit identity exact?
8. Does each participant match its BH semantic lock?
9. Is each numeric lexeme admitted?
10. Do the occurrences share the exact acquisition cohort?
11. Was comparison executed?
12. If executed, is the relation `equal` or `different`?

No one field is allowed to collapse these dimensions into `behavior valid` or
another engineering verdict.

## 19. Authoritative result validation

Every public kernel or evaluator result uses frozen, extra-forbidden,
full-instance-revalidation conventions. Validation is store-independent and
must first serialize nested supplied instances and reconstruct them from field
content. Calling `model_validate()` on an already-created nested object is not
sufficient.

Kernel result validation must:

- reconstruct every model record and verify its content-derived ID;
- verify exact revision membership and deterministic record ordering;
- rebuild `LoadedModel` through the accepted in-memory collection validator;
- rerun the exact kernel query;
- recompute registrations, owner closure, contexts, subjects, roots, ancestry,
  successors, withdrawals, current tips, effective-body projections, groups,
  findings, conclusions, indices, and ordering;
- reject missing, extra, duplicate, reordered, or substituted rows;
- reject bools and coercible values for strict indices.

Evaluator result validation must additionally:

- reconstruct both participant selectors and both ES results;
- require selector/result variable, entity, source, and cutoff coherence;
- require the behavior material revision to equal both participants' model
  revisions;
- require equal participant binding revisions;
- require equal participant interpretation revisions;
- require the same normalized UTC cutoff everywhere;
- require exactly one explicit candidate per participant;
- recompute every model, observation, attachment, semantic, unit, lock, and
  numeric admission;
- recompute the five-field acquisition-cohort key;
- invoke the public CN parser under the accepted parity policy;
- recompute canonical decimals, execution, refusals, and relation.

Reject at the public boundary:

- nested or outer `model_construct` forgeries;
- nested or outer `model_copy` mutations;
- stale content-derived IDs;
- mixed model, binding, or interpretation revisions;
- model revision substitution;
- context or cutoff substitution;
- variable, semantic-lock, source, candidate, occurrence, or owner
  substitution;
- missing, duplicate, extra, or reordered roots, groups, entries,
  participants, or material records;
- forged current tips, withdrawals, activity, root health, effective-body
  equality, corroboration, aggregate conclusion, cohort, canonical decimal,
  refusal, execution, or relation;
- record indices pointing to the wrong union arm;
- implication-bearing extra fields.

Validation accesses no filesystem or store and performs no writes.

## 20. Store validation and immutable indexes

Add these deterministic immutable indexes to `LoadedModel`:

```text
behavior_registrations
behavior_registrations_by_anchor
behavior_anchor_ids_by_variable

behavior_rule_declarations
behavior_rule_ids_by_key
behavior_rule_root_by_id
behavior_rule_ancestry_by_id
behavior_rule_superseded_by
current_behavior_rule_tips_by_root

behavior_rule_withdrawals
behavior_rule_withdrawn_by
behavior_rule_withdrawals_by_target
```

All mappings are defensive immutable copies. All tuple values and mapping-key
iteration are deterministic.

Variable reverse discovery starts from `behavior_anchor_ids_by_variable` and
then resolves the exact `(behavior_anchor_id, context)` declaration key. A
redundant variable/context declaration index is unnecessary.

Effective-body groups are derived from current tips using the canonical
projection. They require no persistent index or stored digest.

Collection validation order must be stable:

1. validate model ID and mapping shape;
2. reconstruct every supplied record through the authoritative discriminated
   union;
3. validate key/record-ID equality and content hashes;
4. bucket records by kind;
5. validate all pre-BH record kinds through their unchanged paths;
6. validate BRG variable and owner closure, permanent uniqueness, and evidence;
7. validate BHD registration, locks, evidence, exact subject, and parents;
8. derive DAG roots, ancestry, successors, and detect cycles or cross-root
   convergence;
9. validate BHW targets after successors and roots are known;
10. derive current tips and immutable indexes;
11. compute the model revision from sorted membership.

No chronology, authority, filename, or append order participates in lifecycle
validity.

## 21. Import-direction boundary

Required dependency direction:

```text
backend.system_identity
          ↑
backend.model_kernel
          ↑
backend.model_state
backend.observation_compatibility
backend.semantic_compatibility
          ↑
backend.behavior_evaluation
          │
          └── public CN exact-number parser only
```

Forbidden:

- model kernel importing behavior evaluation;
- model kernel importing model state, temporal state, identity binding,
  semantic compatibility, constraint evaluation, source interpretation, data
  sources, CAD, PDF, or structural evidence;
- lower layers importing behavior evaluation;
- behavior evaluation importing or constructing model, binding,
  interpretation, temporal, evidence, or source stores;
- behavior evaluation reading paths or enumerating repositories;
- behavior evaluation writing derived findings;
- cutoff-driven model-revision selection.

Evaluation results are never persisted as model or temporal truth.

## 22. Historical replay and preservation rules

Every existing explicit membership must replay unchanged:

```text
9
10
11
14
16
18
28
29
```

Before BH records, queries return structured absence:

- behavior lookup: `not_registered`;
- registered variable collection: `registered` with `entries=()`;
- assertion lookup: `not_found`.

No migration, inferred record, compatibility conversion, or behavior artifact
is fabricated.

A BH membership must remain reference-closed over:

- both participant variable registrations;
- both owner entity registrations;
- the behavior registration;
- declaration parents;
- every cited model record and other evidence reference;
- applicable withdrawals.

Historical membership is never reconstructed from directory enumeration,
filename prefixes, timestamps, current directory contents, append order, or
"all records before BH" logic.

`as_of` never selects model membership. The selected `LoadedModel` is an
explicit injected revision and remains one independent provenance axis.

All existing record bytes, historical revision IDs, binding revisions,
interpretation revisions, temporal evidence, source evidence, structural
evidence, VP artifact, and PT artifact remain frozen unless a later owner gate
explicitly authorizes a bounded demonstration append.

## 23. Security and denial-of-service model

BH-001 eliminates expression-language risks by having no expression language.
The following controls remain mandatory.

### 23.1 Record and identity attacks

- exact bounded identifier grammars;
- complete nested reconstruction before trust;
- content-hash and filename/key agreement;
- exact variable-pair, lock, registration, and context coherence;
- evidence and reference closure;
- immutable sorted indexes;
- explicit historical membership.

### 23.2 Graph attacks

- bounded record size through existing contracts;
- duplicate/self/cross-subject parents rejected;
- cycles rejected;
- cross-root convergence rejected;
- no recursive behavior references or evaluator graph traversal;
- no behavior chaining.

### 23.3 Numeric attacks

- no declaration constants, coefficients, offsets, or expressions;
- no float or ambient decimal arithmetic;
- public bounded CN parser only;
- canonical output limits inherited from CN;
- parser parity failures remain typed integrity errors;
- no tolerance, division, exponentiation, overflow-prone arithmetic, or
  pathological decimal expansion performed by BH.

### 23.4 Candidate and temporal attacks

- exactly two explicit selectors;
- one candidate per selector;
- no candidate cross-product or hidden winner;
- exact five-field cohort comparison;
- no time tolerance, interpolation, or source-clock inference;
- mixed cutoffs and revisions rejected.

### 23.5 Result and dependency attacks

- carry authoritative lower results once;
- strict indices reject booleans;
- all derived fields recomputed;
- no store or filesystem access from validators;
- no dynamic imports, external models, scripts, plugins, callbacks, or code
  execution;
- no persisted computed result.

### 23.6 Inherited limitations

Accepted lower layers may parse a stored `value_json` before BH invokes the CN
numeric parser, and model stores necessarily read record bytes before contract
validation. BH bounds its own records, graph work, and numeric path. It does
not claim constant or bounded work for all hostile lower-layer storage input.
Slice C must nevertheless enforce the mandatory bounded-preflight, inherited-
limit parity, hostile-shape refusal, typed-failure propagation, and ambient-
context gates defined in Section 15. Those gates require no new slice and do
not silently change an accepted lower-layer contract. Any future modification
of the lower-layer parser or storage boundary remains separately owner-gated.

## 24. Adversarial acceptance matrix

| Area | Required red-first and adversarial coverage |
|---|---|
| Identity and exports | Exact `bhv_` grammar and UUID4 minter; frozen/extra-forbid/revalidate anchor; no semantic fields; exact public exports; no premature query/evaluator exports |
| Record IDs | Malformed `brg_`, `bhd_`, `bhw_`; wrong case, prefix, length, hex; stale hash; filename/key mismatch; hostile on-disk instances |
| BRG shape | Exactly two distinct variables; reversed input gives identical bytes/ID; duplicate or missing variable rejected; rule family fixed; no context/lifecycle/owner/port field |
| BRG closure | Unknown variable; missing owner; exact two VRG citations required; missing owner declaration; missing extra citation; same-owner and cross-owner valid twins |
| BHD locks | Exactly two variable-keyed locks; canonical order; IDs equal BRG pair; quantity and unit equal; roles equal and differing valid; swapped variable-role mapping detected |
| BHD exclusions | Reject coefficient, offset, tolerance, expression, direction, role, port, VPA, value, state, outcome, or behavior-validity fields |
| Nested trust | Forged context, signature, lock, rule, evidence, authority, selector, ModelQueryMaterial, ES result, occurrence, and revision through construct/copy attacks |
| Parent input | Malformed, duplicate, self, unknown, wrong-kind, cross-anchor, cross-context parents; caller-order canonicalization |
| Same-root lifecycle | Chain; fork; identical-body fork still conflicts; partial convergence conflicts; full convergence healthy; cycle rejected |
| Independent roots | Same projected body corroborates; evidence/authority/time/note differences do not split bodies; changed lock/body conflicts; cross-root convergence rejected |
| Effective-body disclosure | Exact canonical projection; deterministic body-group order; forged representative, group membership, root membership, and findings rejected |
| Withdrawal | Unknown/wrong/non-tip/superseded/already-withdrawn target; duplicate; successor plus withdrawal; selective fork-tip withdrawal; all tips withdrawn; replay revival |
| Kernel lookup | Registered/absent behavior; exact-context absence; inactive/conflicted/declared; registered-empty reverse variable discovery; malformed input typed |
| Assertion disclosure | BRG permanent; BHD activity plus root and aggregate dimensions; BHW event; valid absent; direct successors and withdrawals exact |
| Carry-once material | Complete material once; strict contiguous row indices; bool/coercion rejected; missing/duplicate/reordered/substituted material or rows rejected |
| Selectors | Exactly two; distinct; canonical order; source required; forged SourceSelector; known-behavior participant mismatch typed; absent behavior still discloses supplied pair |
| Evidence preservation | Both participant lower paths called for absent, undeclared, inactive, and conflicted behavior; lifecycle never suppresses observations; lower errors propagate |
| Participant admission | Registered/owner closure; observation absent; attachment failure; evidence inconsistency; VSP absent/conflict; VSM absent/conflict; source semantics refusal; each lock mismatch |
| Unit boundary | Exact identity admits; any mismatch refuses; no conversion, ontology inference, name matching, or dimensional algebra |
| Cohort | Mutate each of source ID, adapter ID, attempt ID, raw record ID, checksum independently; each mismatch refuses execution |
| Non-cohort fields | Source/receipt times, clock segment, run/sweep, occurrence/property IDs, values, units, and quality flags do not redefine cohort |
| Staleness | Different staleness remains disclosed but does not change exact equality or create an age gate |
| Numeric parser | Reuse the public CN parser and typed failures without copy, fork, or permissive wrapper; admitted boundary twins and one-step-over hostile values for input bytes, coefficient/mantissa digits, fraction digits, exponent representation and magnitude, expanded digits/fraction, and canonical output bytes; boolean/object/array/null/malformed/oversized/expansion-hostile `value_json`; whitespace and negative-zero twins; ambient Decimal changes; parity failures propagate and never become `different` |
| Execution | Cohort mismatch never returns `different`; all gates passing yields `equal` or `different`; relation absent exactly when not executed |
| Vocabulary | No consistent/inconsistent, valid/invalid, pass/fail, healthy/fault, normal/abnormal computed outcome; no safety or control result |
| Reconstruction | Mixed models/bindings/interpretations/cutoffs; candidate/occurrence substitution; forged decimal, cohort, refusal, execution, relation all rejected |
| Import/isolation | Kernel remains downward-only; evaluator owns no store/path/cache/database and performs no writes; public CN parser is the only CN dependency |
| Non-inference | Names, owner, hierarchy, CAD, PIF, PCN, PCM, VPA, ES compatibility, CN result, temporal correlation create no behavior |
| Replay | Explicit 9/10/11/14/16/18/28/29 memberships unchanged; pre-BH structured absence; no enumeration-derived membership |
| Demo | Rehearse VRG+BRG+BHD and artifact generation through public APIs in a disposable ledger before authoritative append; repeat to prove identical identities, hashes, membership order, revision, artifact bytes/size/SHA; present those values at the Slice D owner gate; append only after approval; current result not executed; equal/different fixtures disposable only |
| Binding seam | Exactly one pinned BH variable may lack AnchorDeclaration; all old anchors exact; second undeclared variable fails; binding bytes/revisions unchanged |

Acceptance requires deterministic serialized output under reversed input maps,
record iteration order, hash seeds, and clean-checkout environments. No
timestamp, authority, record ID, or filename may act as a winner.

## 25. Bounded synthetic demonstration

Slice D evolves the model ledger only after Slices A-C are separately owner
accepted:

```text
29 records -> exactly 32 records
```

Exact anchors, content-derived record IDs, membership order, model revision,
record hashes, artifact bytes, artifact size, and artifact SHA-256 are
intentionally not invented during design.

Before any authoritative ledger mutation, Slice D must rehearse the complete
append and disclosure-artifact generation in a disposable copy of the accepted
29-record model ledger. The rehearsal uses only public identity minters,
canonical record builders, `ModelStore` append/load/replay operations, and
public query APIs. It hashes every predecessor file before and after the
rehearsal and performs no write to the authoritative ledger.

The complete rehearsal is repeated in independent disposable roots. The runs
must produce byte-identical records and artifact output, the same canonical
membership order, and the same final model revision. Slice D then presents the
derived anchors, canonical record IDs and file hashes, explicit membership,
final revision, artifact byte count, and artifact SHA-256 at its owner gate.

The authoritative append may occur only after the owner approves those exact
rehearsal results. This is a Slice D pre-append gate, not an unresolved blocker
for Slices A-C.

Append exactly:

1. one neutrally named synthetic `VariableRegistration`;
2. one `BehaviorRegistration` linking that variable with the existing
   registered variable;
3. one parentless `BehaviorRuleDeclaration`.

Do not append:

- VSP or VSM;
- entity;
- port or VPA;
- constraint;
- BHW, correction, or second root;
- temporal record;
- binding `AnchorDeclaration` or binding assertion;
- source interpretation;
- real-printer target, command, control, sensor, or actuator meaning.

The new variable uses an existing registered owner to avoid fabricating an
entity. Documentation must state explicitly that shared ownership did not
create or corroborate the behavior.

The new variable is the sole owner-authorized committed exception to the
binding-declaration fixture seam:

- its exact anchor and VRG are pinned;
- no committed binding set contains an AnchorDeclaration for it;
- every pre-existing registration continues to match its declaration exactly;
- a second undeclared variable fails the seam test;
- a divergent pinned anchor fails;
- all binding memberships, revisions, and bytes remain unchanged;
- model state discloses `binding_declaration_absent` for the new variable.

The committed evaluator demonstration must return `not_executed` because the
new participant lacks accepted binding, specification, and semantic evidence.
Any independently available evidence for the existing variable remains fully
disclosed.

`equal` and `different` demonstrations exist only in disposable test fixtures.
Those fixtures must include:

- two registered variables and owners;
- explicit VSP and VSM records;
- explicit bindings and source interpretations;
- one accepted acquisition envelope containing both selected properties;
- exact participant `SourceSelector` values;
- same-cohort and non-cohort twins;
- exact-equal and exact-different numeric twins.

No disposable record or evidence is committed to the demo ledgers.

Recommended demonstration disclaimer:

> This is an illustrative synthetic BH-001 exact-numeric-equality declaration.
> It does not describe or claim any real printer physics, target, command,
> response, control loop, wiring, signal path, flow, causality, simultaneity,
> correctness, safety, health, real-machine behavior, or operating condition.
> Shared ownership, names, topology, VPA associations, semantic compatibility,
> constraints, and observed correlation did not create this declaration.

The demonstration must additionally state that evaluation being
`not_executed` is an honest admission result, not evidence that the declared
relation is false.

## 26. Owner-gated implementation slices

Every slice begins with persisted design/acceptance criteria, develops tests
red-first, commits in reviewable groups, obtains independent specialist review,
and stops for owner acceptance. Authorization of one slice does not authorize
the next.

### 26.1 Slice A — identity and kernel records

Implement only:

- `BehaviorAnchor`, `bhv_`, and `mint_behavior_anchor()`;
- BRG/BHD/BHW contracts;
- canonical prefixes, record union, filename grammar, and evidence arms;
- public builders through the existing canonical API;
- model-store validation and immutable indexes;
- correction, corroboration, withdrawal, and replay semantics;
- all historical replay and byte-preservation tests;
- design, ADR, implementation plan, acceptance matrix, and module docs.

Do not add kernel query methods, query result contracts, evaluator code, or
fixtures. Stop for owner acceptance.

Implementation status: owner accepted at
`57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. No Slice B query surface, Slice C
evaluator, or Slice D fixture existed at that accepted boundary.

### 26.2 Slice B — read-only kernel queries

Implement only:

- the exact four `ModelQueries` methods;
- carry-once result contracts;
- roots, current tips, withdrawals, effective-body groups, corroboration, and
  conflict disclosure;
- individual BRG/BHD/BHW assertion disclosure;
- authoritative outer-result reconstruction;
- deterministic ordering and hostile revalidation tests.

Do not add the evaluator or fixture. Stop for owner acceptance.

Implementation status: owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`. The exact four-query surface, carry-once results, lifecycle and
effective-body agreement disclosure, deterministic ordering, historical
revival, and store-independent hostile revalidation are present. Slice C is
owner-authorized but not yet implemented. Slice D remains unstarted.

### 26.3 Slice C — evidence-gated evaluator

Implement only:

- `backend/behavior_evaluation`;
- `BehaviorParticipantSource` and exact evaluator result contracts;
- the read-only `BehaviorEvaluationQueries` facade;
- explicit two-source selection;
- independent admission dimensions and refusal provenance;
- exact five-field acquisition-cohort gate;
- public CN parser and typed-failure reuse without copy, fork, private
  reimplementation, or permissive wrapping;
- bounded numeric preflight and exact canonical comparison;
- admitted and one-step-over parity tests for input bytes,
  coefficient/mantissa digits, fractional digits, exponent representation and
  magnitude, expanded digits/fraction, and canonical output bytes;
- refusal of boolean, object, array, null, malformed, oversized, and
  expansion-hostile `value_json` before comparison;
- ambient-decimal-context and parser-parity failure tests;
- store-independent hostile result reconstruction;
- disposable equal, different, cohort-mismatch, and admission-refusal tests;
- import, non-write, preservation, and resource-bound tests.

Do not modify the committed model, binding, interpretation, temporal, source,
or structural fixtures. Stop for owner acceptance.

### 26.4 Slice D — bounded synthetic demonstration

Only after Slices A-C acceptance:

1. write the bounded fixture and artifact-generation specification without
   inventing final content-derived identities;
2. rehearse the complete append and artifact generation in a disposable copy
   using public minters, builders, stores, replay, and query APIs;
3. repeat the rehearsal in independent disposable roots and require identical
   anchors, record IDs, hashes, membership order, final revision, artifact
   bytes, artifact size, and artifact SHA-256;
4. prove every existing record byte is unchanged;
5. present the exact rehearsal results at the Slice D owner gate;
6. only after that approval, append exactly one VRG, one BRG, and one BHD to
   the authoritative ledger through public APIs;
7. pin explicit 29- and 32-record memberships and revisions;
8. pin the exact one-variable binding-seam exception without changing a
   binding ledger;
9. demonstrate declaration query behavior and honest `not_executed`
   evaluation;
10. preserve every earlier historical replay and artifact byte;
11. commit the owner-approved deterministic disclosure artifact contract;
12. stop for final owner acceptance.

No BHW, correction, second root, binding record, VSP, VSM, port, VPA,
constraint, temporal record, interpretation, or source datum is committed.

## 27. Explicit exclusions and known limitations

BH-001 does not provide or imply:

- causality, influence, direction, control, flow, command, or signal semantics;
- physical simultaneity or source-clock synchronization;
- ports, VPA qualification, or behavior-at-port truth;
- unit conversion, dimensional algebra, or ontology inference;
- tolerance, approximate equality, residuals, or affine arithmetic;
- prediction, expected-operation assessment, or observed-result validation;
- constraint satisfaction, correctness, health, fault, safety, or severity;
- derived temporal state or a new observation;
- behavior chaining, recursion, graph execution, or state transitions;
- executable expressions, scripts, plugins, or external models;
- persistence of computed relations;
- a real-machine behavior demonstration.

Exact equality applies only to two admitted canonical numeric observations in
the exact accepted acquisition envelope. A result of `different` is not a
fault, violation, inconsistency, or refutation of the declaration. A result of
`equal` is not proof of causality, correctness, or continuing behavior.

The committed demonstration is intentionally not executable. It proves only
that the model can carry and disclose an explicit declaration honestly.

The evaluator inherits accepted lower-layer resource behavior. BH bounds its
own records, indexing, graph derivation, and numeric parser path but does not
claim a new whole-stack bound for hostile stored source or model bytes.

## 28. Specialist review and reconciliation

Four repository specialists independently reviewed the owner-corrected design.

### 28.1 Software architect

The architecture review accepted the existing-ledger declaration and separate
read-only evaluator. It required:

- the exact five-field repository-backed cohort key;
- a canonical projected-body helper rather than whole-record equality;
- effective-body groups and agreement findings sufficient to disclose one
  healthy root, corroborating roots, same-root conflict, cross-root body
  disagreement, and inactive history;
- `OwnerDeclarationEvidence` as the explicit claim-bearing evidence arm;
- full-instance revalidation for the new anchor and nested contracts;
- no ports or VPA dependency;
- an honest declaration-only demonstration.

These corrections are incorporated.

### 28.2 Backend engineer

The backend review confirmed the contracts, closure rules, indexes,
carry-once results, explicit selectors, cross-owner registration, and 29-to-32
demonstration are implementable without a new store, dependency, or runtime
execution mechanism. It additionally required variable-keyed lock
reconstruction, strict indices, and exact separation of store-time declaration
admission from evaluation-time VSP/VSM/source admission.

These corrections are incorporated.

### 28.3 Software test engineer

The independent test review found two important risks:

- bare sorted signatures permit variable-to-lock substitution, so locks must
  be keyed by variable ID;
- the declaration-only demo conflicts with the existing committed binding
  seam unless one exact exception is pinned and a second exception fails.

Both corrections are incorporated. Non-normative alternatives raised during
the challenge pass are recorded only in the explicit change log in Section 30.

### 28.4 Code reviewer

The final integrity review accepted the corrected lifecycle, corroboration,
selector, numeric, reconstruction, isolation, and demo boundaries. It required
explicit distinction between containing-root health and aggregate subject
conflict and required complete serialized reconstruction of nested results.

These corrections are incorporated. The final specialist verdict is green
with no remaining architectural blocker.

## 29. Resolved owner questions and remaining gates

No BH-001 design question remains unresolved.

Slice D identities and artifact values are intentionally derived rather than
invented during design. Disposable rehearsals using public minters, builders,
stores, replay, and query APIs must deterministically establish the exact
anchors, canonical record IDs and hashes, membership order, final revision,
artifact bytes, artifact size, and artifact SHA-256. Those results are
presented for owner approval before any authoritative append. This is the
mandatory Slice D pre-append gate and does not block Slices A-C.

Hostile lower-layer numeric input is resolved as a mandatory Slice C hardening
gate. Slice C reuses the public CN exact-number parser and typed failures,
performs bounded preflight, proves exact inherited-limit parity with boundary
and one-step-over tests, refuses nonnumeric and expansion-hostile JSON values,
propagates parser parity failures honestly, and proves ambient decimal context
cannot affect comparison. It is not a separate implementation slice and does
not authorize a private parser fork or permissive wrapper.

These decisions authorize no implementation during the current documentation
phase. Each implementation slice still requires its explicit owner gate.

## 30. Decision change log

This corrected synthesis supersedes the following earlier alternatives. They
are recorded here only to prevent accidental reintroduction:

- A general affine rule was narrowed to `exact_numeric_equality`; affine
  predictors, coefficients, offsets, tolerances, and dimensional algebra are
  deferred to BH-002.
- The initial rule that all independent roots conflict was replaced by
  engineering-body corroboration: identical active healthy bodies corroborate,
  while differing bodies conflict. Same-root forks still conflict.
- Context-free declarations were rejected; exact `AssertionContext` remains
  part of BHD and its lineage key.
- Optional port/VPA participant qualification was rejected from BH-001.
- Implicit source discovery and candidate cross-products were rejected in
  favor of exactly two explicit selectors.
- Receipt-time tolerance and arbitrary seven-day or
  `max_receipt_age_seconds` gates were rejected in favor of exact acquisition-
  envelope identity. Staleness remains disclosure only.
- General expression, typed-operator-graph, lookup-table, and external-model
  execution were rejected.
- A binding `AnchorDeclaration` for the Slice D synthetic variable was rejected
  to keep the committed fixture declaration-only. One exact seam exception is
  required instead.
- An evidence-bearing BHW alternative was rejected. BHW follows the accepted
  withdrawal convention: no evidence, no context, no parents, no outcome, and
  uncitable.
- Persisted derived values, equality-as-constraint, and real-printer target or
  control demonstrations were rejected.

The normative behavior of BH-001 is defined by Sections 4 through 29. This
document authorizes no code, test, fixture, ledger, artifact, or history change.

END OF BH-001 CORRECTED FINAL SYNTHESIS
