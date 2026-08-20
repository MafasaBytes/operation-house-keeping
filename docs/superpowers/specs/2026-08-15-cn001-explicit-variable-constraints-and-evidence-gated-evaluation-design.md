# CN-001 — Explicit Variable Constraints and Evidence-Gated Evaluation

Status: Slices A and B accepted; Slice C implemented and awaiting owner
acceptance. Supersedes the
provisional CN-001 synthesis; this document is the implementation-ready
specification after the owner correction pass and the
`ConstraintRegistration`-evidence amendment (which overrides the prior
"opaque anchor deferred" and "lock validated at append" provisional
decisions). Builds on accepted DS-001, TS-001, IB-001, MK-001, VM-001,
VS-001, SN-001, ES-001 (see ADR-0007…0011).

## 1. Purpose

A **constraint** is a model-side authority claim that one variable's value
must satisfy a static numeric predicate, named by the variable's *declared
engineering meaning* (quantity kind, observation role, unit identity). It is
not a diagnosis, an alarm, a safety grade, a recommended action, or a causal
claim.

**Evaluation** is a read-only composition (Slice B) that admits one observed
value through the accepted ES-001 semantic gate — carried exactly once,
verbatim — then performs one deterministic `Decimal` comparison and reports
exactly one of three honest words: `satisfied`, `violated`, `not_evaluated`.
`unknown` / `not_evaluated` is a valid, first-class result. No aggregation,
ranking, conversion, dimensional algebra, or LLM judgment is ever performed.

Slice A delivered the **model-kernel foundation**: the
constraint identity anchor, the predicate and decimal contracts, the two
constraint record kinds, every kernel ripple site, validation, and the
read-only constraint discovery query. The evaluator facade
(`backend/constraint_evaluation/`, ruleset `cn001.1`) is Slice B and is
implemented the accepted contracts. Slice C adds only the bounded committed
fixture and recomputable evidence-to-evaluation demonstration.

## 2. Scope

**In scope (Slice A):** `backend/system_identity/` (the constraint anchor +
public UUID4 minting helper) and `backend/model_kernel/` (two record kinds,
canonical dispatch, store validation, immutable indexes, the
`constraint_declaration` / `constraints_of_variable` queries, and result contracts).

**Implemented in Slice B:** `backend/constraint_evaluation/` (the admission
gate, predicate comparison, evaluation result contracts, and
`CanonicalObservedDecimal`). **Implemented in Slice C:** the two bounded
committed demonstration records and recomputable demonstration. Still out of
scope: the 3D/conversational UI, diagnosis, recommended actions, control, and
any hardware interaction.

**Unchanged upstream authorities (confirmed by audit):** `identity_binding/`
remains the sole property-to-variable authority and the sole binder of
observations to variables; CN-001 adds no identity-binding declaration,
changes no binding ledger, and extends no identity-binding behavior.
Their ledgers and fixture bytes, together with source, temporal, structural,
CAD, and PDF evidence, are untouched. The accepted `mrv_` revision namespace
admits the two new record ids and deterministically yields a new revision id.

## 3. Constraint identity (corrections 1, 11; amendment)

A constraint identity is a canonical `ConstraintAnchor`, minted through the
**public** `system_identity` UUID4 minter and **first persisted** by a
`ConstraintRegistration` record. The anchor is a pure identity value — it
carries no target variable, no unit, no predicate, no severity — exactly
mirroring the accepted `EntityAnchor` / `VariableAnchor` discipline.

```python
# backend/system_identity/anchors.py
CONSTRAINT_ANCHOR_ID_PATTERN = r"^con_[0-9a-f]{32}$"

class ConstraintAnchor(_Frozen):
    anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    namespace: str = Field(pattern=_NAME_PATTERN)
    display_name: str = Field(min_length=1)
    role_name: str | None = Field(default=None, pattern=_NAME_PATTERN)
```

The public minter (the first minting helper in `system_identity`; existing
anchors are unchanged):

```python
# backend/system_identity/minting.py
def mint_constraint_anchor(*, namespace, display_name, role_name=None) -> ConstraintAnchor:
    return ConstraintAnchor(anchor_id=f"con_{uuid4().hex}", ...)
```

Identity is the opaque `con_` id. `namespace`, `display_name`, `role_name`
are human context and are never used for matching. The
`constraint identity → target variable` association is a **permanent
membership claim** carried by `ConstraintRegistration`, never by the anchor
and never by the (correctable) declaration — so the association cannot become
an unsupported model fact when a declaration is superseded.

## 4. The decimal and predicate contracts (corrections 2, 4; Slice A)

### 4.1 `CanonicalDecimal` (stored declaration bounds)

Every authored boundary is a `StrictStr`, never a JSON number or Python
`Decimal`. Direct construction and load accept only this canonical plain
grammar:

```
^(?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))$
```

The validator applies these limits before constructing `Decimal`: at most
386 UTF-8 bytes, 256 coefficient digits, 256 integer digits, and 128
fractional digits. It accepts `0`, `1`, `-1`, `0.25`, `-0.25`, and `60.4`.
It rejects `-0`, `-0.0`, `+1`, `01`, `.5`, `1.`, `1.0`, `60.40`, exponent
notation, whitespace, trailing newlines, non-finite spellings, Unicode
digits, and non-strings. Positive and negative sub-unit values are pinned at
contract, builder, canonical-byte, append, and load boundaries.

The separate pure `canonical_constraint_decimal()` authoring helper may
normalize strict decimal inputs before record construction (`60.40 -> 60.4`,
`-0 -> 0`, `0e99 -> 0`). Direct contracts and load never call it and never
repair stored bytes. It performs exact coefficient/exponent processing,
never `float`, context-dependent `normalize`, quantization, or rounding.

### 4.2 v1 predicate vocabulary

```python
class NumericBoundary(_Frozen):
    value: CanonicalDecimal
    inclusion: Literal["inclusive", "exclusive"]

class ExactNumericLowerBound(_Frozen):
    kind: Literal["lower_bound"] = "lower_bound"
    lower: NumericBoundary

class ExactNumericUpperBound(_Frozen):
    kind: Literal["upper_bound"] = "upper_bound"
    upper: NumericBoundary

class ExactNumericInterval(_Frozen):
    kind: Literal["interval"] = "interval"
    lower: NumericBoundary
    upper: NumericBoundary

ConstraintPredicate = Annotated[
    Union[ExactNumericLowerBound, ExactNumericUpperBound,
          ExactNumericInterval], Field(discriminator="kind")]
```

An interval with `lower < upper` is valid. Equal endpoints are valid only
when both are inclusive, producing a singleton. Reversed bounds and equal
bounds with either endpoint exclusive are rejected as empty predicates.
There is no tolerance, equality operator, hysteresis, formula, second
variable, severity, conversion target, or implicit unit field.

## 5. The two constraint record kinds (corrections 1, 3; amendment)

Both follow the accepted kernel envelope: `record_kind: Literal[...] = ...`,
`schema_version: Literal["1"] = "1"`, a `record_id` with a kind-specific
`^<prefix>_[0-9a-f]{64}$` pattern, `recorded_at: UtcDatetime`, `authority:
AuthorityRef`, `note: str = ""`. Both inherit the global kernel `_Frozen`
(`frozen=True, extra="forbid"`; **no** `revalidate_instances` override —
forgery defense is the boundary `revalidate()` / `_RECORD_ADAPTER` path used
by every other kernel record). `record_kind` is part of the content hash
(only `record_id` is excluded), so the kind literal is identity-bearing.

### 5.1 `ConstraintRegistration` (prefix `crg_`)

A **permanent membership claim**: one constraint identity (`con_` anchor)
targets one variable. It is evidence-bearing (amendment): the
identity→variable association must not become an unsupported model fact
merely because entity and variable registrations historically used
membership-only envelopes. It has **no `supersedes`, no withdrawal, no
lifecycle field** — a mistaken target is not correctable in-kernel; the
constraint must be retired by declaration supersession / a new identity, not
by rewriting the registration.

```python
class ConstraintRegistration(_Frozen):
    record_kind: Literal["constraint_registration"] = "constraint_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^crg_[0-9a-f]{64}$")
    anchor: ConstraintAnchor                 # the con_ identity being persisted
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

The evidence tuple is nonempty and uses the **complete accepted `EvidenceRef`
union**; `_canonical_evidence` sorts and de-duplicates it. The committed CN
fixture carries the full synthetic disclaimer in
`OwnerDeclarationEvidence.statement` and may repeat it in its pinned
nonempty `note`. `supersedes=()` is not present (no lineage field at all).

### 5.2 `VariableConstraintDeclaration` (prefix `vcn_`)

The correctable numeric claim of one constraint identity. The **only lineage
key is the constraint anchor id** (`con_`). Predicate form, boundaries,
inclusivity, and expected semantic tokens may all be corrected beneath the
same anchor. Retargeting cannot: the immutable registration owns the target.

```python
class ConstraintSemanticSignature(_Frozen):
    quantity_kind: QuantityKindReference
    observation_role: ObservationRoleReference
    unit: UnitReference
```

```python
class VariableConstraintDeclaration(_Frozen):
    record_kind: Literal["variable_constraint_declaration"] = "variable_constraint_declaration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vcn_[0-9a-f]{64}$")
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    expected_semantics: ConstraintSemanticSignature
    predicate: ConstraintPredicate
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self): ...   # parents are vcn_ ids; no self-supersede
```

The declaration does not duplicate `variable_anchor_id`; its registration is
the sole authoritative target. Token locks are not compared with VSP/VSM at
append or load. A mismatch is a Slice-B `not_evaluated` result, not model
invalidity.

## 6. Kernel ripple sites (both kinds)

A new model record kind touches twelve sites. For CN-001 there are **two**
kinds, so each site is extended for `crg_` and `vcn_` together:

1. `_PREFIX_BY_KIND` (`canonical.py`) — `constraint_registration: "crg"`,
   `variable_constraint_declaration: "vcn"`.
2. `MODEL_RECORD_ID_PATTERN` (`contracts.py`) — add `crg|vcn`; this is what
   admits the new ids into `mrv_` membership (no new revision namespace).
3. `ModelRecordEvidence.record_id` pattern (`contracts.py`) — add
   `crg|vcn`; both are evidence-bearing claims and therefore citable (the
   `rwd_` "non-claim" precedent stays omitted).
4. `ModelRecord` union (`contracts.py`) — add `ConstraintRegistration`,
   `VariableConstraintDeclaration`.
5. The record classes themselves (`contracts.py`) — §5.
6. `_FILENAME` regex (`store.py`) — a **distinct literal** from
   `MODEL_RECORD_ID_PATTERN`; add `crg|vcn`.
7. Store bucket dispatch (`store.py`) — two new buckets.
8. `LoadedModel` mappings (`store.py`) —
   `constraint_registrations_by_anchor`, `constraint_anchor_ids_by_variable`,
   `constraint_declarations`, `current_constraint_tips_by_anchor`,
   `constraint_superseded_by`.
9. `validate_record_collection` body (`store.py`) — §7, §8.
10. `ModelQueries.constraint_declaration` and `constraints_of_variable` +
    result contracts (`queries.py`, `contracts.py`) — §9.
11. `__init__.py` imports + `__all__` (`model_kernel`, `system_identity`).
12. Evidence closure §7 — `_check_model_record_evidence` for both kinds.

`_RECORD_ADAPTER = TypeAdapter(ModelRecord)` auto-picks the new union
members (no edit). `compute_revision_id` and `_canonical_parents` are
kind-agnostic (no edit).

## 7. Registration uniqueness and immutable target validation (correction 6)

In `validate_record_collection`, for `crg_`:

- **Reference closure:** the target `variable_anchor_id` must be a registered
  variable in the same collection (`MODEL_REFERENCE_INVALID` otherwise).
- **Uniqueness:** at most one `ConstraintRegistration` per `con_` anchor id
  (`MODEL_DUPLICATE_REGISTRATION`). Two registrations of the same anchor —
  agreeing or divergent embedded fields alike — are never tie-broken by
  `recorded_at`, authority, or record id.
- **Anchor integrity:** the embedded `ConstraintAnchor` is revalidated with
  the record; a forged anchor never reaches the index.
- **Evidence closure:** every `EvidenceRef` of kind `model_record` names a
  member of the supplied collection (`MODEL_REFERENCE_INVALID`); foreign
  evidence arms remain declared references, never dereferenced.

## 8. Declaration DAG: closure, cycles, tips, conflicts, convergence, replay,
superseded history (correction 7)

In `validate_record_collection`, for `vcn_`, mirroring the accepted
`vsm` three-colour multi-parent DAG exactly, with the lineage key generalized
from `(variable, dimension)` to the **constraint anchor id**:

- **Reference closure:** `constraint_anchor_id` must name a registered
  constraint (`crg_` present with that `anchor.anchor_id`); that registration
  already proves the target variable is registered.
- **Lineage invariant:** every parent must be a `vcn_` declaration with the
  same `constraint_anchor_id`. This is the only lineage key. Predicate form,
  boundaries, inclusivity, and expected semantic tokens may change.
- **Acyclicity:** iterative three-colour walk over `supersedes`;
  `MODEL_CONSTRAINT_LINEAGE_INVALID` on a cycle.
- **Tips:** records with no successor in the collection, grouped by
  `constraint_anchor_id`. Zero tips on a key that has members is
  unreachable while acyclic (defence-in-depth failure).
- **Conflicts:** competing current tips on the same `con_` are **surfaced**,
  never resolved by recency, authority, record id, file order, or append
  order. A successor superseding every tip converges the lineage; partial
  convergence remains conflicted. Parent SET is identity; replay is
  membership-relative and may revive an earlier tip.
- **Superseded history:** the `constraint_superseded_by` reverse index is
  built from sorted record ids; superseded-but-historical declarations remain
  queryable and disclosed per result.
- **Evidence closure:** uniform `_check_model_record_evidence` for `vcn_`,
  identical to `crg_`, `vsp`, `vsm`, and assertions.

## 9. Constraint discovery query (corrections 3, 4, 9)

`ModelQueries.constraint_declaration(constraint_anchor_id)` supplies exact
lookup. `ModelQueries.constraints_of_variable(variable_anchor_id)` supplies
structured discovery. Both validate identifier format before mapping access.

```python
class ConstraintDeclarationResult(_Frozen):
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    registration: ConstraintRegistration | None = None
    status: Literal["not_registered", "not_declared", "declared", "conflicted"]
    declaration: VariableConstraintDeclaration | None = None   # iff declared
    conflicting_declarations: tuple[VariableConstraintDeclaration, ...] = ()
    superseded_declaration_ids: tuple[str, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _consistent(self): ...   # registration present iff not not_registered;
                                 # declared IFF declaration; conflicted IFF >=2;
                                 # every carried id ∈ revision.record_ids

class VariableConstraintCollectionResult(_Frozen):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    status: Literal["registered", "not_registered"]
    constraints: tuple[ConstraintDeclarationResult, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _consistent(self):
        # not_registered carries no constraints; registered entries are
        # ordered by constraint_anchor_id; every registration, declaration,
        # conflict, and superseded id belongs to revision.record_ids
```

- A syntactically valid but **unregistered** variable →
  `status="not_registered"`, `constraints=()`.
- A **registered** variable with no constraints → `status="registered"`,
  `constraints=()`.
- A registered variable with constraints → one `ConstraintDeclarationResult`
  per `con_` anchor whose registration targets it, each reporting that
  anchor's declaration lineage status.
- Both results carry the **complete `ModelRevision`** (never a bare id; no
  `ModelRevisionId` type exists). Validators prove every registration,
  declaration, conflict, and superseded id belongs to `revision.record_ids`.
- The evaluation-discovery wrapper (`VariableConstraintEvaluationCollectionResult`,
  Slice B) preserves this `registered` / `not_registered` distinction through
  evaluation so an empty tuple is never ambiguous; it is specified, not
  implemented in Slice A.
- Exact lookup of a valid unknown `con_` returns `not_registered` with no
  registration, declarations, conflicts, or superseded ids. Malformed
  `con_` input is typed misuse before mapping access.

## 10. The evaluation admission gate and honest vocabulary (corrections 5, 6, 8;
Slice B)

Specified for Slice B; the contracts it consumes (`ConstraintDeclarationResult`,
the carried ES result, `CanonicalDecimal`) are fixed by Slice A.

CN-001 relies on the **complete carried VS/ES result** for detailed
lower-layer model/source refusal causes — it never duplicates them. The
admission precedence is a single, reachable, non-duplicative chain; the
predicate runs only at the final step:

1. constraint not declared (`not_declared` lineage);
2. constraint conflicted (competing tips);
3. observation absent;
4. observation not attached;
5. evidence not assessable (carried VS reason verbatim);
6. VS shape not evaluated (carried VS `value_shape_not_evaluated_reason`
   verbatim);
7. governing VSP exists but `value_shape != "number"` →
   `model_value_shape_not_numeric` (a CN-only reason; the constraint can only
   compare numbers);
8. VS shape evaluated mismatch (`does_not_satisfy_value_shape`);
9. numeric value absent, including an admitted nullable `null`;
10. ES lacks `declared_semantics_compatible` (the full ES `semantic_findings`
    carried verbatim — CN adds no second copy and never dereferences model
    tokens until this proves the necessary declarations are positive);
11. constraint quantity-kind lock mismatch;
12. constraint observation-role lock mismatch;
13. constraint unit-identity lock mismatch;
14. valid numeric JSON exceeds CN resource limits →
    `numeric_value_out_of_bounds` (CN adds narrower limits than VS);
15. otherwise compare exactly → `satisfied` | `violated`.

`numeric_value_malformed` is **removed** as a normal candidate outcome: after
accepted VS reports consistent number-shaped JSON, malformed JSON is
impossible; a parity breach is a typed internal integrity/configuration
failure, never an honest candidate verdict. `numeric_value_out_of_bounds` is
retained because CN adds narrower resource limits than VS.

`CanonicalObservedDecimal` (Slice B) is a constraint-evaluation-owned contract
with the same canonical plain-number grammar as `CanonicalDecimal` but
observation-output limits coherent with exponent expansion: exact lexical
coefficient, exponent, and expanded-output limits are defined and
**preflight expansion is checked before allocation** (so `1E+999` never
allocates a billion-character string). It never uses `float` or an ambient
`Decimal` context. The source lexeme is parsed with the accepted VS strict
helper (`json.loads(parse_float=Decimal, parse_int=int, parse_constant=reject)`):
legal JSON whitespace around exactly one number is permitted (matching VS and
standard JSON), the byte limit applies to the full stored lexeme, and the
original evidence is preserved unchanged. Quoted numbers, booleans, `null`,
arrays, objects, trailing values, `NaN`, and `Infinity` remain rejected.

## 11. Honest language (correction 10)

The vocabulary is restricted by construction to `satisfied` / `violated` /
`not_evaluated`.

- `satisfied` asserts **only**: the admitted observed value satisfies the
  declared numeric predicate.
- `violated` asserts **only**: the admitted observed value does not satisfy
  the declared numeric predicate.
- `not_evaluated` asserts: the admission gate did not admit a value, with a
  specific reason.

None of these may be misrepresented as safe/unsafe, normal/abnormal,
in-spec/out-of-spec, healthy/faulty, alarming, a diagnosis, a causal claim, a
recommended action, a failure, a test result, a pass/fail grade, or a reason
to control hardware. The evaluator emits no `severity`, `grade`,
`normality`, `alarm`, `recommendation`, or `cause` field, ever.

## 12. CM3 — carried result parity (correction 10)

The complete accepted ES result is carried **exactly once**. CN-001 adds no
second `CandidateSemanticCompatibility` or `CandidateValueCompatibility`
copy. The accepted ES contract already embeds the complete VS result
(`value_compatibility: VariableValueCompatibilityResult`, and each candidate's
`value_candidate: CandidateValueCompatibility`, cross-validated "carried
verbatim"); that internal carriage remains verbatim and is outside CN-001's
modification scope. CN reads `es_result.value_compatibility` and
`es_result.candidates[i].value_candidate`; it never re-fetches or duplicates.

## 13. What must remain excluded

Unit conversion and dimensional algebra; alarms, safety grading, severity,
normality; behaviors, equations, state machines, lookups; diagnosis and
causal reasoning; recommended actions, planning, control; aggregation,
ranking, winners, "current" selection; non-numeric predicates; per-candidate
lock comparison; lock validation against `vsm`/`vsp` at append; an opaque
anchor field added to an accepted record kind; UI, conversational interface,
LLM judgment; executing acquired content; serializing credentials. A unit
mismatch is `not_evaluated`, never a converted comparison. The predicate is
deterministic code; an LLM never judges a value; the model-centric principle
is preserved.

## 14. Threat and failure model

- **Untrusted source payload** — parsed with the VS strict helper; size, type,
  and non-finite guards inherited; no acquired content executed.
- **Pathological decimal** — bounded grammar + 128-digit boundary + golden
  vectors; `CanonicalObservedDecimal` (Slice B) preflight expansion.
- **Forged / malformed on-disk record** — `validate_record_collection`
  validates the prospective collection before any byte is staged; a crafted
  on-disk state fails `load()` all-or-nothing; `revalidate()` re-validates
  from data at every public boundary so a `model_construct` / `model_copy`
  forgery can never reach hashing or the index.
- **Revision desync** — unconstructible: every result embeds the full
  `ModelRevision` from one immutable `LoadedModel`; validators prove carried
  ids belong to `revision.record_ids`.
- **Anachronistic evaluation** — `as_of` + pinned revisions (Slice B).
- **Conflicted lineage / unregistered variable** — `not_evaluated` /
  `not_registered`, never blocking unrelated keys or variables (failure
  isolation).

## 15. Demonstration (Slice C)

`models/demo-printer/records/` 16 → 18: one `crg_` (registering a `con_`
anchor targeting the hotend temperature variable) and one `vcn_` (declaring
an exact inclusive upper boundary of `"80"`, locking to the model's
declared quantity kind / observation role / degree-Celsius unit). All 16
pre-CN-001 records byte-frozen (freeze maps). The trace: source bytes →
occurrence → binding → model variable → semantics → constraint declaration →
`Decimal("60.4") <= Decimal("80")` → `satisfied`. A second case `value="85"`
→ `violated` (asserting only predicate-falsity). The demonstration records are
**not** appended in Slice A or Slice B. Slice C appends them through the
public minter, builder, store, and canonical serialization paths. The fixture
authority is exactly `test_fixture/cn001_demo_fixture/manual_declaration`.
The declaration disclaimer is:

> This declaration is an illustrative synthetic test fixture used only to demonstrate CN-001 evaluation mechanics. It makes no claim about a real printer, safe operating limit, manufacturer specification, alarm threshold, recommended setting, or required action.

Pinned identities are `con_4b768cf843f5474cb5e564e31d239a59`,
`crg_870fe60d91056b6b1da9e3f734e5156cbb52722f6a0fc5f366f66cd40102a3df`,
`vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`,
and model revision
`mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51`.
Historical explicit memberships still replay their original revisions.

## 16. Acceptance

See `docs/superpowers/plans/2026-08-15-cn001-acceptance-matrix.md` for the
row-by-row adversarial acceptance matrix, and
`docs/superpowers/plans/2026-08-15-cn001-slice-a-implementation-plan.md` for
the Slice A commit order. Slice A acceptance: every red-first bounded group
green; the existing ledger byte-identical (every record id, revision,
authority unchanged); no accepted module outside `system_identity` /
`model_kernel` modified; both CN evidence-bearing record kinds receive
uniform evidence closure; structural revalidation proven against
`model_construct`, `model_copy`, forged nested anchors, predicates,
evidence, records, and revisions.
