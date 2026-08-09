# VS-001 — Explicit Variable Value Specification and Observation Compatibility

Status: owner-approved for implementation (2026-08-09), including seven
contract corrections and two final consistency conditions. Base commit
`3842175` on `main`, implemented on the isolated `vs001` branch in a linked
worktree. Baseline gate recorded: **921 passed** at `3842175`.

This specification is self-contained: it supersedes design discussion and
carries every decision needed to implement, review, and validate the slice.

## Supersession of an accepted exclusion

MK-001 and VM-001 state that variables "carry no units, no datatype, no
meaning". VS-001 supersedes **exactly that sentence, and only for a
separate record**: the kernel gains a record that declares what value
representation a registered variable is intended to carry. The
`VariableRegistration` record itself is unchanged and still carries no
units, datatype, or meaning. Every other MK-001 and VM-001 exclusion
stands.

## The question VS-001 answers

> Given an observation honestly attached to a registered model variable,
> what has been explicitly declared about that variable's value type and
> unit, and is this particular observation compatible with those
> declarations?

This is not constraint evaluation, conversion, inference, aggregation, or
diagnosis. An attached observation is **not** automatically a semantically
usable value, and VS-001 exists to preserve that distinction.

## Non-negotiable semantic rule

The canonical variable specification and the source observation describe
different facts:

- **Variable specification** — what the model says this variable is
  intended to represent.
- **Source observation** — what the source actually supplied.
- **Compatibility assessment** — whether the supplied evidence matches the
  explicit specification.

A model specification saying "a number in degree_celsius" does **not**
prove that an unlabelled source number is in that unit. The model unit is
never inherited into source evidence. Units are never inferred from
property names, JSON pointers, display names, role names, adapter ids,
subject identifiers, device type, common engineering practice, an LLM, or
numeric plausibility.

## Architecture

Two seams:

- **Part A** — a sixth model-kernel record kind
  `VariableValueSpecification` (prefix `vsp`) plus one kernel query,
  inside `backend/model_kernel/`.
- **Part B** — a new read-only package
  `backend/observation_compatibility/` that composes the kernel
  specification query with the VM-001 model-state result, both carried
  verbatim.

```text
system_identity ─→ model_kernel ──────┐
identity_binding ─→ model_state ──────┼─→ observation_compatibility
temporal_state (contract types) ──────┘        read-only, holds no state
```

`observation_compatibility` may import `backend.system_identity`,
`backend.model_kernel`, `backend.model_state`, `backend.temporal_state`,
pydantic, and the standard library. Forbidden and AST-enforced:
`backend.data_sources`, `backend.identity_binding` (its types travel
inside carried objects), `sqlite3`, construction of `ModelStore`,
`BindingStore`, or `TemporalStore`, path literals, dynamic imports,
private-attribute access on injected objects, and device vocabulary in
contracts. Constructing `ModelQueries` is explicitly permitted — it is the
composition seam. Reverse rules: `model_kernel` and `model_state` both
forbid importing `backend.observation_compatibility`.

## Part A — `VariableValueSpecification`

```python
_LOCAL_IDENTIFIER = r"^[a-z0-9][a-z0-9._-]*$"

class UnitReference(_Frozen):
    """An identity TOKEN for a unit, not a unit definition."""
    system_id: Literal["project_local"]
    system_edition: Annotated[str, AfterValidator(_identifier)] = Field(
        min_length=1, pattern=_LOCAL_IDENTIFIER)
    code: Annotated[str, AfterValidator(_identifier)] = Field(
        min_length=1, pattern=_LOCAL_IDENTIFIER)

class DeclaredUnit(_Frozen):
    kind: Literal["declared"]
    unit: UnitReference

class UnitNotDeclared(_Frozen):
    kind: Literal["not_declared"]

UnitDeclaration = Annotated[
    Union[DeclaredUnit, UnitNotDeclared], Field(discriminator="kind")]

class VariableValueSpecification(_Frozen):
    record_kind: Literal["variable_value_specification"] = (
        "variable_value_specification")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vsp_[0-9a-f]{64}$")
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    value_shape: Literal["boolean", "number", "string"]
    nullable: bool = False
    unit: UnitDeclaration
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

The anchor is **referenced, not embedded** — it is already embedded
verbatim in the `vrg` record, and a second copy would create an
in-revision divergence class. This also leaves the cross-layer seam test
untouched by construction: a `vsp` record embeds no anchor and never
enters that sweep.

`nullable` is retained in v1 because adding a field to an accepted record
kind is impossible after the fact — it would change the canonical payload
of every already-committed record of that kind and break its
content-derived id. Every field VS-001 will ever need exists in v1.

### Identifier grammar

`system_edition` and `code` must accept a first character that is a
lowercase ASCII letter or digit, then only lowercase ASCII letters,
digits, `.`, `_`, `-`, and nothing else. The `pattern=` constraint is
correct under pydantic's default `rust-regex` engine, but the guarantee
must not rest on an engine default: an explicit `AfterValidator` performs
`re.fullmatch` plus a character-set check. `\A…\Z` is **not** a usable
hardening — it raises `SchemaError` on the default engine. The acceptance
tests are authoritative over the regex text.

## Part A — multi-parent lineage and convergence

`supersedes` is a canonically sorted, unique tuple of `vsp_` ids that
participates in the record digest. Normalization is: **accept any input
order → reject duplicates → sort canonically**. Permuted unique inputs
therefore produce the identical in-memory tuple and the identical
`record_id`; only duplicates are rejected. No raw-JSON-order rule is
introduced for `vsp`: a hand-written file with an unsorted array whose
`record_id` matches the normalized content loads and is normalized in
memory, exactly as accepted `evidence` tuples already do; a file whose id
matches the *unsorted* bytes is rejected as `MODEL_RECORD_HASH_MISMATCH`.

- **Empty tuple** — root specification.
- **One parent** — ordinary revision.
- **Multiple parents** — explicit convergence of competing tips.
- Every parent must exist in the selected collection and be a
  `VariableValueSpecification` for the **same** `variable_anchor_id`.
- Self-reference and cycles are invalid; detection is a DAG traversal, not
  a chain walk.
- **Current tips** = specifications for that variable that no other
  specification in the selected collection lists in its `supersedes`.
- **One tip ⇒ `specified`. Two or more tips ⇒ `conflicted`.** A conflict
  **never invalidates the revision**: the model loads, every query
  answers, and replay works.
- A new record listing **every** current tip as a parent restores exactly
  one tip. A record listing only some tips becomes an additional tip and
  the lineage remains `conflicted` — partial convergence does not
  converge.
- **Repeated contention converges**: if two writers each append a
  convergence record over the same tips, those two records become the
  competing tips, the revision stays usable, and a later record
  superseding both restores one tip.
- Zero tips for a lineage containing at least one specification is
  structural corruption. It is unreachable once acyclicity holds (a finite
  acyclic graph always has an unreferenced node), so it is defence in
  depth and its test asserts the cycle check fires rather than fabricating
  the state.
- Tips are **never** ordered or chosen by `recorded_at`, authority, record
  id, file order, or append order.
- Ancestry is reference-closed: replaying any specification requires its
  complete ancestor set in the subset.

The accepted `RelationshipTypeDefinition` single-parent lineage is **not**
touched by VS-001; its non-convergence is recorded as a separate
pre-existing concern.

## Part A — validation, hashing, replay, queries

Hashing ripple, all hash-safe: `_PREFIX_BY_KIND` gains
`"variable_value_specification": "vsp"`; `MODEL_RECORD_ID_PATTERN` and
`store._FILENAME` widen to `(reg|rtd|rel|rwd|vrg|vsp)`; the `ModelRecord`
union gains the class; **the record-kind bucket dispatch gains an arm** —
omitting it raises a raw `KeyError` that escapes the typed-error contract
through `load`, `append`, and `replay`; `ModelRecordEvidence.record_id`
widens to `(reg|rtd|rel|vrg|vsp)` so a specification is citable
symmetrically (`rwd` stays excluded). **No existing record hash changes.**

Validation lives in `validate_record_collection`, so it applies identically
at load, prospective append, and replay-subset validation. It slots
immediately after the variable-registration pass and before the type-lineage
pass, because it needs `variable_registrations_by_anchor` and nothing else.
`variable_anchor_id` must key that mapping, else `MODEL_REFERENCE_INVALID`
— so a subset containing a `vsp` must contain its `vrg` and that vrg's
owner `reg`, and append order is reg → vrg → vsp. Lineage failures raise
`MODEL_SPECIFICATION_LINEAGE_INVALID`. Byte-identical re-append remains the
inherited idempotent no-op.

`LoadedModel` gains three defaulted read-only mappings:
`specifications`, `current_specification_tips_by_variable` (canonically
ordered by record id), and `specification_superseded_by`.

Replay behaviour: no specification → `not_specified`; only an ancestor
present → that ancestor is the tip and governs (**replay can revive a
superseded specification** — coherent under "a revision is a knowledge
context", but an older unit can become current again); a successor without
its full ancestry → `MODEL_REFERENCE_INVALID`; a linked chain or converged
DAG → the single tip governs; two unlinked tips → `conflicted`, revision
valid and replayable; `vsp` without its `vrg` → `MODEL_REFERENCE_INVALID`.

```python
class VariableSpecificationResult(_Frozen):
    status: Literal["specified", "not_specified", "conflicted",
                    "not_registered"]
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    specification: VariableValueSpecification | None = None
    conflicting_specifications: tuple[VariableValueSpecification, ...] = ()
    superseded_specification_ids: tuple[str, ...] = ()
    revision: ModelRevision
```

`ModelQueries.variable_value_specification(anchor_id)` returns it, with the
tip verbatim when `specified`, every tip verbatim when `conflicted`, and
`MODEL_ANCHOR_ID_INVALID` for malformed input. This is the **single**
source of specification status in the system.

## Part B — the compatibility facade

```python
class ObservationCompatibilityQueries:
    def __init__(self, state: ModelStateQueries) -> None:
        # typed configuration error on a wrong dependency
        self.state = state
        self.model_queries = ModelQueries(state.model)   # EXACT public LoadedModel

    def variable_value_compatibility(
        self, variable_anchor_id: str, *, as_of: datetime,
        entity_anchor_id: str | None = None,
        source: SourceSelector | None = None,
    ) -> VariableValueCompatibilityResult: ...
```

One injected object; the kernel query is constructed from `state.model`,
the same public `LoadedModel` the VM-001 facade already uses, so a
model/specification revision mismatch is **unconstructible**. The facade
computes no tips, no conflict determination, no superseded set, and no
registration status; it reads `specification_result.status` and never
serializes a second vocabulary for that fact.

```python
class VariableValueCompatibilityResult(_Frozen):
    variable_anchor_id: str
    as_of: UtcDatetime
    ruleset_version: Literal["vs001.1"]
    state: VariableStateResult                          # VM-001, VERBATIM
    specification_result: VariableSpecificationResult   # kernel, VERBATIM
    model_unit_specification: Literal["declared", "not_declared",
                                      "not_evaluated"]
    candidates: tuple[CandidateValueCompatibility, ...] = ()

class CandidateValueCompatibility(_Frozen):
    state_candidate: CandidateObservation               # VM-001, VERBATIM

    value_presence: Literal["value_present", "explicit_null",
                            "no_observation", "indeterminate"]
    evidence_consistency: Literal["consistent", "json_type_unrecognized",
                                  "shape_disagreement", "value_json_malformed",
                                  "not_evaluated"]
    observed_shape: Literal["boolean", "number", "string",
                            "null", "array", "object"] | None

    value_shape_compatibility: Literal["satisfies_specification",
                                       "does_not_satisfy_specification",
                                       "not_evaluated"]
    value_shape_finding: Literal["shape_matches", "shape_differs",
                                 "explicit_null_allowed",
                                 "explicit_null_not_allowed",
                                 "unsupported_observed_structure"] | None
    value_shape_not_evaluated_reason: Literal[
        "no_observation", "observation_not_attached", "specification_conflicted",
        "specification_not_available", "evidence_not_assessable"] | None

    source_unit_evidence: Literal["present", "absent", "not_evaluated"]
    declared_unit_lexeme_relation: Literal["declared_lexeme_identical",
                                           "declared_lexeme_differs",
                                           "not_evaluated"]
    unit_lexeme_not_evaluated_reason: Literal[
        "no_observation", "observation_not_attached", "specification_conflicted",
        "specification_not_available", "model_unit_not_declared",
        "source_unit_absent"] | None
```

Everything about the observation — subject, property, occurrence,
attachment, resolution, declaration, provenance — is reached through
`state_candidate`, exactly once, unreconstructed. No echoed convenience
fields exist. `model_unit_specification` and `source_unit_evidence` are the
only derived values retained and both are validator-locked to their
sources.

## Value-shape and evidence-consistency rules

Evidence is parsed with `json.loads(value_json, parse_float=Decimal,
parse_int=int, parse_constant=<reject>)` — the accepted ingestion policy,
stdlib only. This is lossless, rejects `NaN`/`Infinity`/`-Infinity`, and
never produces `inf`. **`float()` is never called on a parsed value**:
`1E+999` would become `inf`, and a 400-digit integer raises
`OverflowError`, which is not a `ValueError` and would escape untyped.
`bool` is tested before `int` everywhere, so a Python `bool` never enters
number handling.

Order of evaluation:

1. `json_type` outside `{object, array, string, number, boolean, null}` →
   `evidence_consistency = "json_type_unrecognized"`, presence
   `"indeterminate"`.
2. `value_json` fails the strict parse → `"value_json_malformed"`,
   presence `"indeterminate"`.
3. Parsed shape disagrees with the stored `json_type` →
   `"shape_disagreement"`, presence `"indeterminate"`. **Neither field is
   repaired and neither is preferred.**
4. Otherwise `"consistent"`; `observed_shape` is the parsed shape; presence
   is `explicit_null` for null, else `value_present`.

In cases 1–3 no shape verdict is computed
(`evidence_not_assessable`) — *evidence internally contradictory and
therefore not assessable* is never reported as *evidence incompatible with
the specification*.

| observed_shape | vs `boolean` | vs `number` | vs `string` |
|---|---|---|---|
| `boolean` | satisfies / `shape_matches` | does_not_satisfy / `shape_differs` | does_not_satisfy / `shape_differs` |
| `number` | does_not_satisfy | satisfies / `shape_matches` | does_not_satisfy |
| `string` | does_not_satisfy | does_not_satisfy | satisfies / `shape_matches` |
| `null` | `nullable` ? satisfies / `explicit_null_allowed` : does_not_satisfy / `explicit_null_not_allowed` | same | same |
| `array` / `object` | does_not_satisfy / `unsupported_observed_structure` | same | same |

A numeric-looking JSON string parses to `str` and remains a string.
Arrays and objects are **unsupported, not missing**. JSON `null` is
**explicit null, not absence**. Later property omission remains coverage
evidence inside the VM-001 result (`later_snapshots_without_property`) and
is never synthesized into a presence arm here. Mathematical integrality is
never inferred; `integer` is not a value shape in VS-001 because the
accepted pipeline classifies integers and decimals alike as JSON `number`
and canonicalization erases the distinction (`1e0` → `1`, `6e2` → `6E+2`).
Integer support is a future question requiring either preserved source
numeric-kind evidence or an explicitly approved integrality rule.

## Unit identity and lexical-relation rules

Three independent dimensions:

- **`model_unit_specification`** (result level): `declared` when the
  governing tip carries `DeclaredUnit`; `not_declared` for
  `UnitNotDeclared`; `not_evaluated` when no single tip governs.
- **`source_unit_evidence`** (per candidate): `present` when
  `occurrence.declared_unit is not None`; `absent` when `None`;
  `not_evaluated` when there is no observation. This is evidence
  disclosure, not a verdict, so it is computed whenever an observation
  exists — **including for unattached candidates**.
- **`declared_unit_lexeme_relation`** (per candidate): computed only when
  an observation exists, the candidate is attached, one specification
  governs, that specification declares a unit, and the observation supplies
  a unit string. The comparison is exactly
  `observation.declared_unit == specification.unit.code` — byte-exact,
  case-sensitive, no trimming, folding, mapping, parsing, dimensional
  analysis, or conversion.

`declared_lexeme_identical` means **only that the two strings match**. It
is not a claim that the source uses the specified unit system, edition,
dimension, or scale. The source string is never compared against
`system_id` or `system_edition`, and the design never pretends the source
supplied a namespace or an edition.

**Closed exclusion list.** A unit may be read **only** from
`occurrence.declared_unit`. Never from `source_time.unit` (the clock's
unit, which already rides inside the carried result), `display_name`,
`role_name`, `json_pointer`, `adapter_id`, `subject_identifier`, or the
specification itself.

A project-local code is an identity token, not a computational unit
definition. VS-001 claims no dimensional equivalence, no convertibility, no
scale or offset, no SI traceability, and no equivalence to any external
standard. UCUM and QUDT are not adopted; `system_id` is a widenable
`Literal` and any external system must arrive with its own edition
semantics.

## Independent reason precedence

Each dimension has its own chain; the first matching clause wins.

**`value_shape_not_evaluated_reason`** — depends on `value_json` and
`json_type`:

1. no observation → `no_observation`
2. attachment not `attached` → `observation_not_attached`
3. specification `conflicted` → `specification_conflicted`
4. specification `not_specified` / `not_registered` →
   `specification_not_available`
5. evidence not `consistent` → `evidence_not_assessable`
6. otherwise `None` and a verdict is computed

**`unit_lexeme_not_evaluated_reason`** — depends on `declared_unit` only:

1. no observation → `no_observation`
2. attachment not `attached` → `observation_not_attached`
3. specification `conflicted` → `specification_conflicted`
4. specification `not_specified` / `not_registered` →
   `specification_not_available`
5. `model_unit_specification != "declared"` → `model_unit_not_declared`
6. `source_unit_evidence != "present"` → `source_unit_absent`
7. otherwise `None` and a relation is computed

Clause 5 precedes clause 6 deliberately: when neither side supplies a
unit, the model-side absence governs, because no comparison could exist
regardless of the source.

**Independence is enforced, not merely described.** `evidence_consistency`
appears only in the shape chain — a malformed or self-contradictory
`value_json` never erases an explicitly supplied `declared_unit`, and the
lexical comparison still runs when its own prerequisites hold. Conversely a
missing source unit never suppresses a shape verdict.

**A conflicted specification suppresses verdicts but does not override
earlier precedence.** `specification_result.status == "conflicted"` implies
**no candidate receives a shape or unit verdict**; the reason recorded is
still the first applicable clause — `no_observation` when there is no
observation, `observation_not_attached` when the observation is unattached,
and `specification_conflicted` only when the observation is present and
attached.

## Cross-field invariants

1. `specification_result.revision == state.model_revision`.
2. `specification_result.anchor_id == variable_anchor_id`.
3. `specification_result.status == "not_registered"` ⇔
   `state.model_membership == "not_registered"`.
4. `len(candidates) == len(state.candidates)` and
   `candidates[i].state_candidate == state.candidates[i]` for every index.
5. `model_unit_specification == "not_evaluated"` ⇔
   `specification_result.status != "specified"`; `"declared"` ⇔ the tip
   carries `DeclaredUnit`; `"not_declared"` otherwise.
6. `source_unit_evidence == "not_evaluated"` ⇔ no observation;
   `"present"` ⇔ `occurrence.declared_unit is not None`; `"absent"`
   otherwise — independent of attachment.
7. `declared_unit_lexeme_relation != "not_evaluated"` requires: an
   observation; `attachment == "attached"`; status `specified`;
   `model_unit_specification == "declared"`;
   `source_unit_evidence == "present"`. It does **not** depend on
   `evidence_consistency`.
8. `value_shape_compatibility != "not_evaluated"` requires: an
   observation; `attachment == "attached"`; status `specified`;
   `evidence_consistency == "consistent"`.
9. Each reason field is non-null exactly when its dimension is
   `not_evaluated`, and equals its own precedence chain applied to that
   candidate. The two fields are computed independently and may differ.
10. `value_shape_finding is None` ⇔ shape is `not_evaluated`;
    `satisfies_specification` ⇔ finding ∈ {`shape_matches`,
    `explicit_null_allowed`}.
11. `value_presence == "no_observation"` ⇔ no observation;
    `"indeterminate"` ⇔ evidence not consistent and an observation exists;
    `"explicit_null"` ⇔ consistent with `observed_shape == "null"`;
    `observed_shape is not None` ⇔ `evidence_consistency == "consistent"`.
12. status `conflicted` ⇒ `conflicting_specifications` carries every tip
    verbatim (length ≥ 2) and **no** candidate receives a shape or unit
    verdict.
13. No lower-layer object is mutated or reconstructed.
14. No field named `value`, `current_value`, `normalized_value`,
    `unit_filled_value`, `winner`, `current`, or `usable` exists.

## Public error surface

```python
class ObservationCompatibilityError(Exception): ...          # code + message
class ObservationCompatibilityConfigurationError(ObservationCompatibilityError): ...
#   OBSERVATION_COMPATIBILITY_INPUT_INVALID
```

One code, one subclass. Wrong constructor dependency types fail typed and
path-free. Request objects are structurally revalidated **once**, at the
accepted VM-001 boundary the facade delegates to; its typed
`ModelStateQueryError` propagates unchanged, so a `model_construct`
forgery never leaks a raw `ValidationError`. `ModelKernelError`,
`ModelStateError`, `IdentityBindingError`, and `TemporalError` propagate
with classes and codes unchanged. Malformed or self-contradictory
observation content becomes a compatibility **outcome**, never an
exception. The strict parse catches a narrowly scoped
`(json.JSONDecodeError, ValueError, decimal.InvalidOperation)` around the
parse call only — never a bare `Exception` — so a programming error
surfaces as itself rather than being relabelled as evidence
incompatibility.

## Time and revision semantics

One `mrv_` revision covers membership **and** specification. `rev_` covers
identity binding. `as_of` is the ingestion-receipt cutoff, historically
closed. Identity resolution runs at each occurrence's own `received_at`.
Source-native time remains evidence only.

A specification has **no applicability interval**. `recorded_at` is audit
information: it never becomes engineering validity and never selects a tip.
If a variable's intended representation genuinely changed at a wall-clock
instant, VS-001 cannot express that — supersede the specification and
select revisions explicitly. A later specification cannot reach an
explicitly selected older revision, because tip computation is
membership-relative.

Reproducibility requires naming the model revision id, the binding revision
id, `as_of`, an identical temporal projection, and `ruleset_version`. One
honest gap: `projector_version` exists on `TemporalAttemptEvent` but not on
`TemporalOccurrence`, so the carried state does not itself name the
projection version.

## Committed fixture — exact permanent content

```text
record_kind        = variable_value_specification
schema_version     = 1
variable_anchor_id = var_b7e2d3c4f5a6172839405a6b7c8d9e0f
value_shape        = number
nullable           = false
unit.kind          = declared
unit.system_id     = project_local
unit.system_edition= ohk-units-1
unit.code          = degree_celsius
supersedes         = ()
recorded_at        = 2026-08-09T12:00:00Z
authority.kind     = test_fixture
authority.agent    = mk001_demo_fixture
authority.method   = manual_declaration
note               = ""
```

Evidence is exactly one `OwnerDeclarationEvidence` with this statement:

> Model-side value specification only. This record states that the model
> requires this variable to carry a JSON number and the project-local unit
> identity ohk-units-1/degree_celsius. It makes no claim about any source,
> adapter, connector, observation, or supplied source unit. The unit code
> is an identity token, not a unit definition: it asserts no dimension,
> convertibility, scale or offset, SI traceability, or equivalence to an
> external standard.

The `vsp_` id is computed through the accepted canonical builder, never
hand-authored. The record contains no Moonraker, Klipper, printer,
extruder, or hotend vocabulary, no source locator, no JSON pointer, no
observed value, and no source-unit assertion. It must not cite
`TemporalOccurrenceEvidence` — the committed-ledger sweep bans the
substring `occurrence`.

## Demonstration

Over the accepted three-occurrence timeline (60.1 / 60.1 / **60.4**), the
committed demonstration proves:

```text
registered model variable
→ one governing VariableValueSpecification
→ attached latest observation 60.4
→ internally consistent JSON number
→ satisfies value-shape specification
→ model unit declared
→ source unit absent
→ lexical relation not evaluated
→ unit reason source_unit_absent
→ unchanged raw provenance
```

and, across committed and synthetic fixtures: the model unit never appears
inside source evidence; numeric-looking strings remain strings; booleans
never satisfy number; arrays and objects are present but unsupported;
explicit null follows `nullable`; malformed or contradictory evidence is
not ordinary incompatibility; source-unit evidence survives malformed value
evidence; unattached evidence remains visible; multiple candidates remain
separate and ordered; no value is normalized, converted, filled, ranked, or
selected; pre-specification replay remains attached but reports
`not_specified`; competing tips keep the revision usable; partial
convergence remains conflicted; full multi-parent convergence restores one
tip; repeated contention converges again; lower-layer results are carried
whole-object equal; and no accepted record hash changes.

Fixture tiers: real committed data where possible; synthetic payloads
through the **real** ingestion path at the real committed binding target
where a value must be shaped; crafted store rows only for what no adapter
can produce — every non-`None` `declared_unit`, non-finite constants,
unrecognized `json_type`, and `json_type`/shape disagreements. **Every
unit-relation row is synthetic**, because no producer in the repository
ever sets a non-`None` `declared_unit`.

## Verification

```bash
.venv/bin/python -m pytest -o addopts="" tests/observation_compatibility \
    tests/model_kernel tests/model_state
.venv/bin/python -m pytest -o addopts="" tests/
```

plus base-only and all-extras clean-checkout runs from fresh clones and
fresh virtual environments.

## Exclusions

No unit conversion, dimensional analysis, interpolation, aggregation,
sensor fusion, authority ranking, constraint evaluation, alarms, operating
envelopes, calculated or inferred variables, equations, behaviours,
diagnosis, hierarchy-wide state views, commands, control, API or UI work,
ontology generation, LLM-derived semantics, or unrelated ingestion. No
`quantity_kind`, `semantic_kind`, or placeholder for them; no `integer`
value shape; no `display_symbol`; no source-property interpretation record;
no hard-coded device unit; no adapter change; no UCUM or QUDT adoption; no
new runtime dependency; no aggregate state cache.

Unchanged and byte-identical: `backend/system_identity/`,
`backend/data_sources/`, `backend/temporal_state/`,
`backend/identity_binding/`, and `backend/model_state/`.
`VariableRegistration` and every accepted record kind are unmodified; all
existing committed record ids remain valid.

## Next open question (future milestone)

> How can an authority-backed source-property interpretation declare a
> source unit and value representation without pretending it was supplied
> in each observation?

Its home is pre-decided: a new sibling ledger, never merged into
`identity_binding`, `model_kernel`, or a read-only facade.
