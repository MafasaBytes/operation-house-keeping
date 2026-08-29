# BH-001 Slice C — preimplementation discrepancy report

Status: **OWNER ACCEPTED; ALL FOUR QUESTIONS RESOLVED; SLICE C RESUMED AFTER
DOCUMENTATION ASSERTIONS**

Date: 2026-08-30

## 1. Outcome

BH-001 Slice C could not be implemented exactly as originally authorized
without silently changing accepted public semantics. Repository inspection and
three independent specialist reviews found two hard contradictions and one
public-surface pin missing from the authoritative specification:

1. the fixed refusal vocabulary cannot truthfully encode several accepted
   lower-layer states that must refuse numeric comparison;
2. a store-independent BH result cannot authenticate a fully coherent mutation
   of lower temporal value content because the carried identity fields do not
   bind that content; and
3. the authorization requires exact public errors and `__all__`, but the
   specification does not enumerate them.

The stop was owner accepted at
`eedae19a9b2542958f44e66af7117a981c7faeef`. The owner subsequently resolved
all four questions exactly in Sections 6, 8, 9, and 10 below. The original
findings remain here as the audit trail. Slice C may resume only after the
resolution documentation and focused assertions pass. Slice D has not started.

## 2. Authority and verified starting state

The work began from branch `bh001` at the accepted Slice B HEAD:

```text
05177f7306ce745d093bd5f11abafc13a6274d0f
```

The working tree was clean. Before any action, the three authoritative files
were read completely and their owner-supplied hashes were verified:

```text
04cb7115c1303fd766a77d569ff968f73362166b0c4aaf68a4f1861a01faf574  CLAUDE.md
2b2f21335e4deff8989efc47498659bc990321566f972bfc0abb69130d49a8ba  docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
465c14056be33fe6e52e2537132cf1fee0dfb2616058d7de2c33244301c16b26  docs/superpowers/reports/2026-08-29-bh001-slice-b-completion-report.md
```

The accepted design was inspected together with the Slice A and Slice B plans,
acceptance matrices and completion reports; applicable module READMEs; public
model, state, observation, semantic, temporal, binding, and constraint APIs;
hostile-revalidation tests; and the explicit historical memberships.

## 3. Administrative step completed

Slice B owner acceptance was recorded separately, before Slice C work, in:

```text
cc8fcf085cf1c490d4773d8972f469159329c527
docs: record owner acceptance of BH-001 Slice B
```

That status-only commit records Slice B as accepted at `05177f7`, Slice C as
authorized but not implemented, and Slice D as unstarted. It changed only
applicable BH status documentation. No history was rewritten and nothing was
pushed or merged.

## 4. Repository facts constraining the evaluator

The accepted composition path is implementable in principle:

```text
SemanticCompatibilityQueries
  -> compatibility.state.model
  -> ModelQueries(...).behavior_declaration(...)
  -> variable_semantic_compatibility(...) once per explicit selector
```

The public lower results expose the required model, binding, interpretation,
temporal, attachment, semantic, unit, and staleness evidence. An explicit
`SourceSelector` produces one candidate rather than a discovered or ranked
candidate set.

The exact acquisition envelope is also repository-grounded at these paths:

```text
occurrence.subject.source_id
occurrence.subject.adapter_id
occurrence.attempt_id
occurrence.raw_record_id
occurrence.payload_checksum
```

No timestamp is necessary or permitted to establish the cohort.

The accepted public numeric boundary is
`backend.constraint_evaluation.parse_observed_decimal`. Its public result and
typed failure contracts are reusable without copying private constants or
parser logic. The public parser itself performs the accepted bounded lexical
and expansion preflight.

## 5. Hard discrepancy one — fixed refusal vocabulary is incomplete

Section 18.2 says a refusal is present only when its exact source fact fails.
The fixed list contains `evidence_not_assessable`,
`numeric_specification_not_available`, `source_semantics_not_admitted`, and
`numeric_value_out_of_bounds`, but it has no value-shape mismatch, explicit
null, nonnumeric model shape, or unavailable model-unit reason.

Accepted lower layers can produce each of those facts without evidence
inconsistency.

### 5.1 Numeric VSP with a consistent nonnumeric observation

With a registered variable and owner, a current numeric VSP, current quantity
and role declarations, positive interpretations, exact unit identity, and an
explicit selector, these `value_json` values are lower-layer-consistent:

| Value | JSON shape | Evidence consistency | Numeric VSP shape result | ES finding |
|---|---|---|---|---|
| `true` | boolean | `consistent` | `does_not_satisfy_value_shape` | `declared_semantics_compatible` |
| `null` | null | `consistent` | `does_not_satisfy_value_shape` | `declared_semantics_compatible` |
| `"text"` | string | `consistent` | `does_not_satisfy_value_shape` | `declared_semantics_compatible` |
| `[1]` | array | `consistent` | `does_not_satisfy_value_shape` | `declared_semantics_compatible` |
| `{"x":1}` | object | `consistent` | `does_not_satisfy_value_shape` | `declared_semantics_compatible` |

An exact explicit-selector reproduction returned:

```text
1 explicit_selector consistent boolean does_not_satisfy_value_shape
('declared_semantics_compatible',
 'source_unit_absent_but_interpreted',
 'unit_identity_exact')
```

None of the fixed reasons is truthful:

- `evidence_not_assessable` is false because evidence consistency is
  `consistent` and shape was assessed;
- `numeric_specification_not_available` is false because the numeric VSP is
  current and unique;
- `source_semantics_not_admitted` is false because ES admitted the declared
  semantics;
- `numeric_value_out_of_bounds` is false because the numeric parser must not
  receive a known nonnumeric JSON shape.

Calling the public numeric parser anyway would convert a lower-consistent shape
refusal into a typed parser parity failure, contradicting the accepted gate
order and the requirement that malformed or nonnumeric values never reach
numeric comparison.

### 5.2 Nullable numeric VSP with explicit null

The lower contracts can assess explicit null consistently for a nullable
numeric specification. `null` is still not a numeric operand. The BH vocabulary
has no exact `numeric_value_absent` equivalent, and the parser must not receive
it.

### 5.3 Unique current nonnumeric VSP

A current, unique boolean or string VSP is neither absent nor conflicted.
`numeric_specification_not_available` could represent “no current unique
numeric VSP” only if the owner explicitly defines it that way. The accepted
text does not currently do so.

### 5.4 Numeric VSP with no declared unit identity

The accepted VSP unit contract permits `unit.kind="not_declared"`. That is not
an exact match and is not a unit mismatch between two known identities. The BH
unit-admission vocabulary has only `not_evaluated`, `exact`, and `mismatch`, and
the refusal vocabulary has no `model_unit_not_available` fact.

### 5.5 Existing CN distinction

The public CN evaluator already distinguishes the relevant lower facts with
reasons including:

```text
model_value_shape_not_numeric
value_shape_not_satisfied
numeric_value_absent
```

BH need not copy those names, but it needs owner-approved meanings that cover
the same reachable facts honestly.

## 6. Owner resolution for discrepancy one

The original resolution choices were:

1. add exact BH refusal reasons for nonnumeric model shape, observed shape
   mismatch, explicit null, and unavailable model unit; or
2. normatively define which existing reason covers each fact, including any
   needed change to the unit-admission or numeric-admission literals.

The implementation must continue to refuse these facts before invoking the CN
parser. `different` cannot be used for any of them.

The lead recommendation is the following minimal, explicit pin:

| Reachable fact | Recommended refusal | Admission state |
|---|---|---|
| Consistent nonnull observation whose JSON shape does not satisfy a numeric VSP | add `numeric_value_shape_mismatch` | `numeric_admission="not_evaluated"` |
| Explicit null where a numeric operand is required | add `numeric_value_absent` | `numeric_admission="not_evaluated"` |
| Unique current VSP has a nonnumeric governing shape, or no current unique numeric VSP exists | retain `numeric_specification_not_available`, normatively define it as “no current unique numeric specification is available” | `numeric_admission="not_evaluated"` |
| Governing numeric VSP has no declared unit identity | add `model_unit_not_available` | `unit_admission="not_evaluated"`, `numeric_admission="not_evaluated"` |

The owner accepted that recommendation with these exact additions and
clarifications:

- add `model_unit_not_available`, `numeric_value_absent`, and
  `numeric_value_shape_mismatch` at their pinned positions in the 22-reason
  vocabulary;
- define `numeric_specification_not_available` as no uniquely current numeric
  specification due to absence, inactive lineage, or one uniquely current
  nonnumeric governing shape;
- keep conflicted specification under
  `numeric_specification_conflicted`;
- give explicit null precedence: emit `numeric_value_absent`, never additionally
  emit shape mismatch, even for a nonnullable specification;
- preserve every lower nullable/nonnullable finding and independent earlier
  refusal;
- map the first three numeric-unavailable/absent/shape cases to numeric
  `not_evaluated`, and map unavailable model unit to both unit and numeric
  `not_evaluated`;
- never call the parser or produce `different` for these cases.

The exact ordered vocabulary now appears in the authoritative specification
and Slice C plan.

## 7. Hard discrepancy two — coherent occurrence mutation is unauthenticable

Section 19 and the acceptance matrix require store-independent reconstruction
to reject candidate or occurrence substitution. Inconsistent substitutions
are rejectable. A fully coherent value substitution is not.

### 7.1 Identity derivation does not bind the observed value

The accepted temporal projector derives:

```text
occurrence_id = derive_entity_id(attempt_id, "temporal", observation_id)
```

The Moonraker observation ID derives from:

```text
raw_record_id + extractor_version + property path
```

Neither identity binds `value_json`, `json_type`, or `declared_unit`.
`payload_checksum` binds raw payload bytes, but those bytes and the extraction
manifest are not carried in `VariableSemanticCompatibilityResult` or the
proposed BH result. The Slice C validator is explicitly forbidden from using a
store or filesystem to retrieve them.

`TemporalOccurrence` validates field types and frozen shape but does not
rederive a content-bound occurrence identity.

### 7.2 Reproduced coherent mutation

A genuine `VariableSemanticCompatibilityResult` carried one occurrence through
three accepted nested paths. A read-only specialist serialized it, replaced
every duplicate `value_json` from `60.1` to `987.654`, left all identity and
cohort fields unchanged, and reconstructed it:

```text
mutated_duplicate_occurrence_copies=3
revalidation_accepted=True copies=3
stable_identity=True
forged_value=987.654
```

A BH validator can rederive all lower statuses, parse the substituted number,
and recompute the resulting `equal` or `different` relation. Because every
carried duplicate agrees, no contradiction remains in the serialized result.
The validator cannot prove that the substituted value came from the payload
named by the unchanged checksum.

### 7.3 Integrity boundary

Slice C can and must reject:

- stale content-derived model record IDs;
- inconsistent nested copies;
- mixed revisions or cutoffs;
- selector/variable/source retargeting that breaks carried coherence;
- missing, duplicate, extra, or reordered rows;
- forged derived gates, decimals, refusals, cohort findings, execution, or
  relations that disagree with the carried lower material.

It cannot authenticate coherent lower evidence content beyond the guarantees
already provided by that lower public result.

## 8. Owner resolution for discrepancy two

The original resolution choices were:

1. narrow the Slice C rejection promise to substitutions detectable from the
   carried material, explicitly documenting that lower-evidence authenticity is
   inherited and not re-proven by serialized BH validation; or
2. separately authorize a lower-layer content-bound occurrence identity or
   authenticated raw/extraction proof carry.

The first option preserves Slice C scope and dependency direction. The second
changes an accepted lower-layer contract and therefore requires its own owner
gate; it must not be improvised inside `backend/behavior_evaluation`.

The lead recommendation is option 1, stated normatively as:

> BH authoritative validation proves the internal coherence of the carried
> lower public results and every BH-derived field. It inherits, and does not
> independently re-prove, raw-source authenticity. A fully coherent content
> mutation accepted by the lower public contracts is outside BH's
> store-independent detection boundary.

The owner accepted option 1 and the quoted scoped contract exactly. This
preserves every detectable construct/copy, stale-model-ID,
mixed-revision, ordering, indexing, and derived-result attack while making no
cryptographic guarantee the carried material cannot support. Slice C must add
an executable limitation test. Temporal identity, raw evidence, extraction,
and lower-result contracts remain unchanged; content-bound lower occurrence
authentication is separately owner-gated future work.

## 9. Owner resolution for the public surface

The specification fixes:

- `backend/behavior_evaluation`;
- `BehaviorEvaluationQueries` and `behavior_evaluation(...)`;
- the status alias names and ordered literal values;
- `BehaviorParticipantSource`, `BehaviorEvaluationRefusal`, participant result,
  and top-level result names and fields.

It does not enumerate public evaluator exception names or the exact ordered
`backend.behavior_evaluation.__all__`. The authorization nevertheless requires
exact public exports and forbids invented aliases. The specification requires
typed rejection in several places, but that does not by itself require those
exception classes to be new public exports.

Repository convention suggests the following trio, but they are not currently
owner-approved BH contracts:

```text
BehaviorEvaluationError
BehaviorEvaluationConfigurationError
BehaviorEvaluationInputError
```

The owner pinned all three classes as public with the stated inheritance. The
configuration code is `BEHAVIOR_EVALUATION_CONFIGURATION_INVALID`; the query
input/participant-set code is `BEHAVIOR_EVALUATION_INPUT_INVALID`.

The exact CN `NumericParityBreachError` class object is re-exported without
subclassing, wrapping, translation, or replacement. The parser and canonical-
decimal constructor are not re-exported. The exact ordered 21-name `__all__`
is now recorded in the authoritative specification and plan. Ordinary
evaluation refusals remain result data; direct Pydantic construction may retain
ordinary `ValidationError`.

## 10. Owner-resolved gate order

The accepted text requires all participant-local gates, then cohort, then CN
numeric admission, while also requiring a typed parser parity breach in one
participant not to be hidden by an ordinary refusal in the other.

The specialists recommended this deterministic interpretation:

1. validate request and known-registration participant equality;
2. call both ES branches exactly once in canonical variable order, attempting
   both even if one raises, then propagate the first canonical typed error
   unchanged and fabricate no result;
3. derive lifecycle and all lower participant-local ordinary refusals;
4. evaluate cohort whenever both required occurrences exist, even if a peer
   has another ordinary local refusal; if either occurrence is absent, leave it
   not evaluated;
5. only for an admitted cohort, call the public parser on every participant
   whose own evidence is observation-present, non-null, governed by one
   uniquely current numeric VSP with a declared model-unit identity, and
   numeric-shaped, in canonical order, even if the peer has another ordinary
   refusal;
6. propagate the first typed parser failure unchanged;
7. execute equality only if every ordinary gate admitted.

The owner accepted this scheduling. Attachment, semantic, unit, lock, and peer
ordinary refusals do not hide a typed parity failure for an otherwise eligible
participant. A different cohort blocks parser calls. This never sends known
boolean, string, object, array, null, malformed, or nonnumeric-model-shape
cases, or model-unit-unavailable cases, to the parser. Equality executes only
after every ordinary gate and the cohort gate admit.

## 11. Reproduction and test evidence

The lead ran this focused accepted lower-layer reproduction:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/observation_compatibility/test_compatibility.py::TestValueShape::test_shape_matrix \
  tests/observation_compatibility/test_compatibility.py::TestValueShape::test_explicit_null_follows_nullable \
  tests/observation_compatibility/test_compatibility.py::TestFullShapeMatrix::test_every_cell \
  tests/observation_compatibility/test_compatibility.py::TestFullShapeMatrix::test_explicit_null_against_every_shape \
  tests/semantic_compatibility/test_semantic_matrix.py -q
```

Result:

```text
44 passed in 9.86s
```

No full suite or clean-checkout run is represented as Slice C verification,
because no implementation exists. Running completion gates would not resolve
the contract contradictions.

## 12. Specialist review synthesis

### Software architect

Confirmed that the accepted composition and dependency direction are otherwise
feasible. Rejected treating consistent nonnumeric evidence as
`evidence_not_assessable`. Confirmed that store-independent validation cannot
authenticate a coherent value mutation without carried proof authority.

### Backend engineer

Independently confirmed the missing refusal coverage, including model-unit
absence, and the non-content-bound temporal identity seam. Recommended a
bounded discrepancy stop rather than an invented implementation meaning.

### Software test engineer

Reproduced the explicit-selector nonnumeric cases and coherent three-copy
occurrence mutation. Supplied a disposable equal/different fixture strategy
that remains viable once the contract is corrected. Identified the missing
public error/`__all__` pin and the parser-order interaction.

### Code reviewer

Confirmed both hard discrepancies as technically reproduced and honestly
scoped. Required the plan and matrix to stop treating a five-file private
layout as normative, distinguish propagation semantics from exception object
identity, narrow the numeric-regex prohibition to copied/private parser logic,
and expose cohort/parser scheduling as an owner decision. Also required this
report to distinguish typed rejection from a necessarily public BH error tree.
All corrections are incorporated here and in the two planning artifacts.

## 13. Planning artifacts

The preimplementation Slice C plan and adversarial matrix were written before
production code, as authorized. At the original stop they were explicitly
marked blocked and did not invent answers. They now record the owner-accepted
resolutions and form the active pre-code authority:

```text
docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md
docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md
```

The matrix preserves the planned C01-C100 coverage. Rows that originally
exposed blockers now pin the accepted resolutions for:

- exact public errors and exports;
- consistent nonnumeric/null observations;
- nonnumeric model VSP;
- unavailable model unit;
- coherent occurrence-value substitution.

## 14. Scope and preservation

No file under these areas was modified:

```text
backend/
models/
bindings/
interpretations/
tests/
```

No model, binding, interpretation, source, temporal, structural, PT, VP, or BH
record was appended or changed. No committed fixture or artifact was generated.
The current demo therefore remains at the accepted 29-record pre-BH boundary.

No push, merge, rebase, reset, cherry-pick, amend, or history rewrite occurred.

## 15. Owner resolution and resume gate

The owner answered:

1. Is the minimal refusal/admission table in Section 6 accepted, including
   explicit-null precedence; if not, what exact replacement mapping applies?
2. Is the scoped integrity statement in Section 8 accepted, or is a separately
   gated lower-layer content-authentication change authorized?
3. Are BH-specific exception classes public; if so, what are their exact names,
   and what is the exact ordered `backend.behavior_evaluation.__all__`?
4. When one participant has an ordinary local refusal but both occurrences
   exist, is cohort still computed or `not_evaluated`; and, if cohort admits,
   must the parser still run for every numeric-eligible participant so a typed
   parity failure cannot be hidden?

All four answers are incorporated into the specification, implementation plan,
and acceptance matrix. Slice C resumes only after their documentation
assertions pass. The implementation remains bounded to Slice C; Slice D remains
unstarted.

END OF BH-001 SLICE C PREIMPLEMENTATION DISCREPANCY REPORT
