# BH-001 Slice C — evidence-gated evaluator implementation plan

Status: **BLOCKED BEFORE PRODUCTION CODE.** Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`, with acceptance recorded by the
separate administrative commit
`cc8fcf0`. Slice C was owner-authorized and planned here before production
code, but repository-grounded specialist review found two contradictions in
the accepted evaluator contract. They are recorded in
`docs/superpowers/reports/2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md`.
No Slice C production code or red tests may begin until the owner resolves
them. Slice D remains unstarted.

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

## 2. Public package surface — owner pin required

The specification fixes the package, facade, method, status aliases, selector,
refusal, participant result, and top-level result names. It does **not** fix an
exact module count, public error class names, or the exact ordered
`backend.behavior_evaluation.__all__`. Because the authorization requires exact
exports with no invented aliases, those details require an owner pin before
implementation.

A conventional implementation could use:

```text
backend/behavior_evaluation/__init__.py
backend/behavior_evaluation/contracts.py
backend/behavior_evaluation/errors.py
backend/behavior_evaluation/facade.py
backend/behavior_evaluation/README.md
```

Possible public errors, **not yet normative**:

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

Pin the eventual `backend.behavior_evaluation.__all__` to the owner-approved
names. Add no
alternate facade, helper, wrapper, convenience query, overload, port API,
aggregate validity result, or persisted result.

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

The constructor accepts only the public semantic facade. Once exact typed
error classes are owner-pinned, the query validates
and normalizes the behavior ID, exact `AssertionContext`, aware UTC cutoff,
and exactly two structurally reconstructed participant selectors.

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
failure propagates unchanged and no outer result is fabricated.

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

The accepted refusal vocabulary does not presently provide an honest result
for every state that these public lower layers can produce. In particular:

- a numeric VSP can assess a boolean, string, object, array, or explicit null
  consistently while refusing its value shape;
- a nullable numeric VSP can assess explicit null consistently;
- a unique current nonnumeric VSP is neither absent nor conflicted; and
- a numeric VSP can have `unit.kind="not_declared"`.

None is truthfully `evidence_not_assessable`; some are also not
`numeric_specification_not_available`, `source_semantics_not_admitted`, or
`numeric_value_out_of_bounds`. The CN parser must not receive them. The owner
must add exact reasons or normatively broaden named reasons before this gate
can be implemented.

## 8. Acquisition cohort — cross-gate timing unresolved

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

The specification orders cohort after participant-local gates but also requires
independent disclosure of failed dimensions. It does not pin whether cohort is
`not_evaluated` whenever either participant has an ordinary local refusal or is
still computed whenever both occurrences exist. That timing remains blocked
for an owner decision.

## 9. Numeric boundary

Eventually invoke only the public
`backend.constraint_evaluation.parse_observed_decimal()` API, after all prior
gates. Its public implementation is the bounded lexical/expansion preflight;
BH adds no regex, parser, numeric conversion, Decimal arithmetic, or private
constant import.

The accepted text also says a numeric parity error cannot be hidden by a peer
ordinary refusal. Whether the parser runs for a numeric-eligible participant
when its peer has an earlier ordinary local refusal, and whether cohort must be
admitted first in that case, is not fully pinned. No parser scheduling will be
implemented until the owner resolves that interaction. Public CN typed errors
must then propagate without permissive translation.

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
tuple. `not_executed_reasons` carries typed refusal rows. No aggregate validity
or preferred refusal exists.

The ordering of already-derived refusals is fixed above. Whether cohort and
numeric gates are derived at all after a peer's earlier local refusal remains
the explicit unresolved question in Sections 8 and 9.

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

This promise is blocked for a fully coherent lower occurrence-value mutation.
The carried lower result contains neither the raw payload bytes nor extraction
manifest, and the accepted `TemporalOccurrence.occurrence_id` and
`observation_id` do not bind `value_json`. A hostile caller can consistently
replace every carried copy of one numeric `value_json`, reconstruct the lower
results, and recompute the BH decimal/relation without creating any
store-independent contradiction. The owner must either narrow the rejection
promise to substitutions detectable from carried material or separately
authorize content binding/raw-evidence carry in a lower layer.

## 12. Red-first test groups

The groups below remain the implementation plan after the two contract
decisions above. They have not been started. Writing tests that invent a
refusal meaning or an unauthenticable integrity guarantee would silently
reinterpret the accepted design.

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

The only completed Slice C-era commits are the separate Slice B acceptance
administrative commit and, if committed after review, the documentation-only
discrepancy package. Once the owner resolves both contradictions, use the
remaining reviewable groups:

```text
docs: plan BH-001 Slice C
test: define BH-001 Slice C evaluator contracts
feat: add BH-001 evidence-gated evaluator
test: harden BH-001 Slice C reconstruction
fix: repair BH-001 Slice C adversarial findings  # only if reproduced
docs: record BH-001 Slice C reviews
docs: record BH-001 Slice C verification
```

Write the final report to
`docs/superpowers/reports/2026-08-29-bh001-slice-c-completion-report.md`, commit
it, and stop for owner acceptance. Do not begin Slice D.

Until then, the discrepancy report is the authoritative stop artifact. It is
not a completion report and does not claim Slice C acceptance.

END OF BH-001 SLICE C IMPLEMENTATION PLAN
