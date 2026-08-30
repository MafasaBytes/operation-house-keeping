# BH-001 Slice C — evidence-gated evaluator implementation plan

Status: Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`, with acceptance recorded by the
separate administrative commit
`cc8fcf0`. The repository-grounded contradictions recorded in
`docs/superpowers/reports/2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md`
are owner accepted and resolved at the documentation gate. The normative
documentation amendments and focused assertions passed before production
work began. BH-001 Slices A, B, and C are owner accepted. Slice C is accepted
at `8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. Only the Slice D pre-append
rehearsal gate is owner authorized; the authoritative append has not started.

Date: 2026-08-30

Authoritative specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`.

## 1. Slice boundary

Slice C adds only the separate read-only `backend/behavior_evaluation`
package. It composes the accepted public `ModelQueries.behavior_declaration()`
and `SemanticCompatibilityQueries.variable_semantic_compatibility()` results.
It owns no store, ledger, projection, cache, database, path, socket, or write
capability.

Slice C does not alter model-kernel records, canonicalization, store admission,
indexes, Slice B queries, model state, observation compatibility, source
interpretation, semantic compatibility, temporal evidence, bindings, source
data, constraints, ports, VPA, or any committed fixture.

## 2. Exact public package surface

Private module layout is not a public contract. The bounded implementation may
use:

```text
backend/behavior_evaluation/__init__.py
backend/behavior_evaluation/contracts.py
backend/behavior_evaluation/errors.py
backend/behavior_evaluation/facade.py
backend/behavior_evaluation/README.md
```

Public errors are exactly:

```text
BehaviorEvaluationError
BehaviorEvaluationConfigurationError
BehaviorEvaluationInputError
```

Public literal aliases, in specification order:

```text
BehaviorEvaluationExecution
BehaviorComputedRelation
BehaviorParticipantAdmission
BehaviorParticipantModelAdmission
BehaviorParticipantObservationAvailability
BehaviorParticipantAttachmentAdmission
BehaviorParticipantSemanticAdmission
BehaviorParticipantUnitAdmission
BehaviorParticipantLockAdmission
BehaviorParticipantNumericAdmission
BehaviorAcquisitionCohortAdmission
BehaviorEvaluationRefusalReason
```

Public models and facade:

```text
BehaviorParticipantSource
BehaviorEvaluationRefusal
BehaviorEvaluationParticipantResult
BehaviorEvaluationResult
BehaviorEvaluationQueries
```

The exact ordered `backend.behavior_evaluation.__all__` is:

```text
BehaviorEvaluationError
BehaviorEvaluationConfigurationError
BehaviorEvaluationInputError
NumericParityBreachError
BehaviorParticipantSource
BehaviorEvaluationExecution
BehaviorComputedRelation
BehaviorParticipantAdmission
BehaviorParticipantModelAdmission
BehaviorParticipantObservationAvailability
BehaviorParticipantAttachmentAdmission
BehaviorParticipantSemanticAdmission
BehaviorParticipantUnitAdmission
BehaviorParticipantLockAdmission
BehaviorParticipantNumericAdmission
BehaviorAcquisitionCohortAdmission
BehaviorEvaluationRefusalReason
BehaviorEvaluationRefusal
BehaviorEvaluationParticipantResult
BehaviorEvaluationResult
BehaviorEvaluationQueries
```

`NumericParityBreachError` is the exact CN class object. BH does not re-export
the parser or canonical-decimal constructor. Add no alternate facade, helper,
wrapper, convenience query, overload, port API, aggregate validity result, or
persisted result.

## 3. Exact request and result fields

`BehaviorParticipantSource` fields:

```text
variable_anchor_id
entity_anchor_id
source
```

`BehaviorEvaluationRefusal` fields:

```text
reason
participant_index
```

`BehaviorEvaluationParticipantResult` fields:

```text
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

`BehaviorEvaluationResult` fields:

```text
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

All models use frozen, extra-forbidden, full-instance-revalidation. All
indices are strict nonnegative integers. Optional values use explicit `None`;
collections use canonical tuples.

## 4. Constructor and query contract

Implement exactly:

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
    ) -> BehaviorEvaluationResult: ...
```

The constructor accepts only the public semantic facade. Invalid dependency
construction raises `BehaviorEvaluationConfigurationError` with exact code
`BEHAVIOR_EVALUATION_CONFIGURATION_INVALID`. The query validates
and normalizes the behavior ID, exact `AssertionContext`, aware UTC cutoff,
and exactly two structurally reconstructed participant selectors.

Structurally invalid query input or participant-set misuse raises
`BehaviorEvaluationInputError` with exact code
`BEHAVIOR_EVALUATION_INPUT_INVALID`. Direct Pydantic construction may retain
ordinary `ValidationError`. Ordinary evaluation refusals remain result data.

Selectors are distinct by variable ID and canonically sorted by that ID.
When registration exists, their variable set must equal the permanent BRG
pair before either semantic evidence branch is called. When registration is
absent, the supplied valid pair defines the two independent evidence queries.

## 5. Composition data flow

Use only public lower-layer objects and methods:

```text
SemanticCompatibilityQueries
    └─ compatibility.state.model: exact public LoadedModel
          └─ ModelQueries(...).behavior_declaration(...)

SemanticCompatibilityQueries.variable_semantic_compatibility(...)
    ├─ participant 0 exact SourceSelector
    └─ participant 1 exact SourceSelector

                         ↓

BehaviorEvaluationResult
```

Each participant semantic query executes exactly once in canonical participant
order. Both branches execute for every structurally valid request, including
behavior not registered, not declared, inactive, or conflicted. A typed lower
failure does not suppress the other branch call. After both attempts, propagate
the first typed failure in canonical participant order unchanged and fabricate
no outer result.

## 6. Declaration admission

Map the exact-context kernel conclusion to top-level refusal:

```text
not_registered -> behavior_not_registered
not_declared   -> behavior_not_declared
inactive       -> behavior_inactive
conflicted     -> behavior_conflicted
declared       -> no behavior refusal
```

Execution requires `declared` with one authoritative effective body. Multiple
independent corroborating records may remain current because their accepted
effective bodies are identical. Use the representative declaration from the
single active effective-body group only after authoritative Slice B result
validation. Do not rank current declarations.

## 7. Participant-local gate derivation

For each carried semantic result and its sole explicit-selector candidate,
derive independently:

1. model registration and owner closure;
2. observation availability;
3. binding positivity and attachment;
4. observation evidence assessability and numeric shape;
5. current unique numeric VSP and exact model unit;
6. current unique quantity-kind and observation-role declarations;
7. source quantity, role, and unit semantic admission;
8. exact current-model-to-BH-lock equality for quantity, role, and unit;
9. numeric admission, only after cohort admission.

Participant refusal order follows exactly that precedence. Source semantic
failure is reported only when the source/model comparison is actually refused,
not when an earlier gate made it unevaluable. `unit_admission` remains separate
from semantic and lock admission. Observation roles may differ across the two
participants; each must match its own variable-keyed lock.

Apply these exact resolved mappings:

- `numeric_specification_not_available`: no current specification, inactive
  specification lineage, or one uniquely current specification with a
  nonnumeric governing shape; `numeric_admission="not_evaluated"`;
- `numeric_specification_conflicted`: the specification result is conflicted;
- `model_unit_not_available`: the governing numeric VSP has no model-unit
  identity; exactly `unit_admission="not_evaluated"` and
  `numeric_admission="not_evaluated"`;
- `numeric_value_absent`: selected `value_json` is explicit null;
  `numeric_admission="not_evaluated"`;
- `numeric_value_shape_mismatch`: a present non-null selected observation does
  not satisfy numeric JSON shape; `numeric_admission="not_evaluated"`.

Explicit null takes precedence over shape mismatch even for a nonnullable VSP.
Do not add the shape-mismatch refusal for that participant. Preserve the lower
nullable/nonnullable finding and every independently applicable earlier
refusal. Each mapping makes aggregate participant admission `not_admitted` and
none invokes the CN parser.

The exact refusal order is:

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
model_unit_not_available
source_semantics_not_admitted
quantity_kind_lock_mismatch
observation_role_lock_mismatch
unit_lock_mismatch
numeric_value_absent
numeric_value_shape_mismatch
numeric_value_out_of_bounds
acquisition_cohort_mismatch
```

## 8. Acquisition cohort

The cohort key itself is exact and settled:

```python
(
    occurrence.subject.source_id,
    occurrence.subject.adapter_id,
    occurrence.attempt_id,
    occurrence.raw_record_id,
    occurrence.payload_checksum,
)
```

Exact equality produces `same_acquisition_cohort`; any field mismatch produces
`different_acquisition_cohort` and the exact
`acquisition_cohort_mismatch` refusal. No other occurrence field participates.
Source time, receipt time, staleness, ordering, clock segment, run, sweep,
occurrence ID, value, unit, and quality flags never establish a cohort.

Compute cohort whenever both selected occurrences exist, even when either
participant has another ordinary local refusal. If either occurrence is
absent, cohort is `not_evaluated`. A different cohort blocks all parser calls.

If either occurrence is absent, no cohort identity is invented.

## 9. Numeric boundary

Invoke only the public
`backend.constraint_evaluation.parse_observed_decimal()` API, after all prior
gates. Its public implementation is the bounded lexical/expansion preflight;
BH adds no copied/private numeric regex or parser, numeric conversion, Decimal
arithmetic, or private constant import.

After an admitted cohort, invoke the parser in canonical participant order for
every participant whose own carried evidence establishes an occurrence,
non-null value, uniquely current numeric VSP with a declared model-unit
identity, and numeric observed JSON shape. Attachment, semantic, known
source/model unit mismatch, unit-lock mismatch, another lock refusal, or peer
ordinary refusal does not suppress an otherwise eligible parser call. Known
boolean, string, array, object, null, nonnumeric-model-shape, or model-unit-not-
available cases never reach it. Propagate the first public
`NumericParityBreachError` unchanged. No peer refusal hides a typed parity
failure for an otherwise eligible participant.

Map admitted parser results to `canonical_decimal`; map ordinary bounds refusal
to `numeric_value_out_of_bounds`. Compare two admitted canonical strings by
exact string equality only. Do not use float, Decimal, subtraction, tolerance,
rounding, quantization, unit conversion, or ambient numeric context.

## 10. Deterministic refusal and execution contract

Top-level refusal order is:

1. behavior refusal, participant index `None`;
2. participant 0 local refusals in gate order;
3. participant 1 local refusals in gate order;
4. cohort refusal, participant index `None`.

`participant.refusal_reasons` carries that participant's exact local reason
tuple as `tuple[BehaviorEvaluationRefusalReason, ...]`.
`not_executed_reasons` carries
`tuple[BehaviorEvaluationRefusal, ...]`. No aggregate validity or preferred
refusal exists.

The ordering of derived refusals is fixed above. Cohort and parser scheduling
follow Sections 8 and 9 even when peer ordinary refusals already exist.

Execution is `executed` exactly when the declaration is admitted, both
participants are admitted, the cohort is exact, and both canonical decimals
exist. `computed_relation` is then exactly `equal` or `different`; otherwise
execution is `not_executed` and relation is `None`.

## 11. Authoritative reconstruction

The outer result validator must first serialize and reconstruct:

- the kernel `BehaviorRuleResult`;
- both `BehaviorParticipantSource` instances and nested `SourceSelector`s;
- both `VariableSemanticCompatibilityResult` instances and every nested lower
  result.

Then, without a store or filesystem, require:

- exact behavior, context, and UTC cutoff echoes;
- exact canonical participant order and source/result/row index mapping;
- exact selector-to-state subject/property/entity/variable coherence;
- one explicit candidate per participant;
- equal behavior/participant model revisions;
- equal participant binding revisions;
- equal participant interpretation revisions;
- exact lower cutoff coherence;
- exact registered pair, semantic locks, cohort, gates, refusals, decimals,
  execution, and relation.

Use one pure authoritative derivation shared by the facade and validator.
Reject missing, duplicate, extra, reordered, substituted, mixed-revision, and
forged content at the public boundary.

The validator proves internal coherence of carried lower public results and
every BH-derived field. It inherits and does not re-prove raw-source
authenticity. A fully coherent lower-evidence mutation accepted by lower public
contracts is outside its store-independent detection boundary. Add one
executable limitation test that demonstrates this boundary; do not change
temporal identity or access raw stores.

## 12. Red-first test groups

The groups below use the owner-resolved contracts. They begin only after the
documentation assertion gate passes.

Commit tests before production code:

1. exact public names, literal order, field order, signatures, and `__all__`;
2. constructor and typed input errors;
3. disposable full-admission equal and different worlds;
4. every declaration and participant refusal independently;
5. exact five-field cohort mismatch twins and excluded-time-field twins;
6. CN boundary parity and parser-failure propagation;
7. nested construct/copy/stale-ID/mixed-revision/coercion attacks;
8. architecture, no-write, no-private-parser, and non-inference assertions;
9. historical and committed-ledger/artifact preservation.

The disposable full world uses two registered variables, unique numeric VSPs,
unique VSM dimensions, exact bindings, exact interpretations, and the accepted
Moonraker acquisition envelope containing both `temperature` and `target`.
Nothing from that world is committed to a ledger fixture.

## 13. Inherited numeric boundary twins

Pin exact public-parser parity at:

```text
source bytes:              512 admitted / 513 out_of_bounds
coefficient digits:        256 admitted / 257 out_of_bounds
fraction digits:           128 admitted / 129 out_of_bounds
exponent representation:   4 digits admitted / 5 out_of_bounds
absolute exponent:         1024 admitted zero / 1025 out_of_bounds
expanded digits:           384 admitted / 385 out_of_bounds
expanded fraction digits:  384 admitted / 385 out_of_bounds
canonical output bytes:    386 admitted / 387 out_of_bounds
```

Also pin booleans, strings, objects, arrays, null, malformed JSON,
non-finite constants, oversized hostile prefixes, and expansion-hostile
lexemes. Such shapes are refused before behavior comparison. Parser parity
errors remain the original public CN exception and never become `different`.

## 14. Specialist review sequence

Before production code, obtain independent software-architect,
backend-engineer, and software-test-engineer reviews of this exact plan and
repository fit. Reconcile their findings without broadening Slice C.

After production and adversarial tests are green, obtain a separate
code-reviewer integrity review. Reviewer-added reproductions must run before
completion.

## 15. Verification matrix

Run and record exact counts for:

1. focused `tests/behavior_evaluation/`;
2. inherited CN parser and Slice C parity tests;
3. complete model-kernel and model-state suites;
4. binding, temporal, semantic, observation, and constraint affected suites;
5. architecture/import-isolation tests;
6. historical replay and artifact-preservation tests;
7. complete repository suite;
8. fresh base-only checkout at final committed HEAD;
9. fresh all-extras checkout at final committed HEAD;
10. focused OCP/STEP and PDF suites;
11. backend compilation;
12. `git diff --check`, branch topology, remote status, and clean worktree.

Report a sandbox-denied real-loopback test separately and rerun it with the
required permission.

## 16. Reviewable commits and stop gate

The completed Slice C-era commits before resumed implementation are the
separate Slice B acceptance administrative commit and the documentation-only
discrepancy package. Add the owner-resolution documentation commit, then use
the remaining reviewable groups:

```text
docs: resolve BH-001 Slice C contract discrepancy
test: define BH-001 Slice C evaluator contracts
feat: add BH-001 evidence-gated evaluator
test: harden BH-001 Slice C reconstruction
fix: repair BH-001 Slice C adversarial findings  # only if reproduced
docs: record BH-001 Slice C reviews
docs: record BH-001 Slice C verification
```

Write the final report to
`docs/superpowers/reports/2026-08-30-bh001-slice-c-completion-report.md`, commit
it, and stop for owner acceptance. Do not begin Slice D.

The discrepancy report remains the historical stop artifact and now records
its owner resolution. It is not a completion report and does not claim Slice C
acceptance.

## 17. Final BH-001 owner acceptance

The later owner-gated Slice D is complete. BH-001 complete, owner accepted,
adversarially reviewed, full-suite verified, and dual-clean-checkout verified.
The accepted implementation boundary is
`6fdf4d009538ddd169c1342508a104c9d61560b6`.
The accepted evaluator demonstration remains `not_executed`; final acceptance
does not convert it into observed equality or real-machine truth.

END OF BH-001 SLICE C IMPLEMENTATION PLAN
