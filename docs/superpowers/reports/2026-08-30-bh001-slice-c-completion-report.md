# BH-001 Slice C completion report

Status: BH-001 Slices A and B are owner accepted. Slice C is implemented and
adversarially reviewed; awaiting owner acceptance. Slice D has not started.

Date: 2026-08-30

Authoritative design:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`

## 1. Outcome and stop gate

BH-001 Slice C is implemented on branch `bh001`. It adds the separate,
read-only `backend.behavior_evaluation` composition layer and exactly one
public query facade, `BehaviorEvaluationQueries`, for evidence-gated
evaluation of the Slice A/B `exact_numeric_equality` declaration.

The evaluator:

- accepts exactly two explicit participant source selectors;
- invokes the existing public semantic-compatibility pipeline exactly once
  for each participant in canonical variable order;
- preserves declaration lifecycle, participant model admission, observation
  availability, attachment, binding, evidence assessability, semantic
  admission, unit admission, declaration-lock admission, numeric admission,
  acquisition-cohort admission, execution, and computed relation as separate
  disclosures;
- compares only two admitted canonical numeric values from the same exact
  acquisition envelope;
- returns only `equal` or `different` after every gate admits execution;
- owns no store, ledger, cache, projection, database, filesystem path, socket,
  or write capability; and
- persists no evaluation result.

The verified implementation-and-review HEAD before this completion report was
persisted is:

```text
cc0c509fdd66bb4d59e3d004868992b154a2e9a6
```

The commit containing this report necessarily receives its content-addressed
identity only after the report is written. That terminal administrative HEAD
is recorded in the concise delivery receipt rather than falsely
self-referenced here.

Slice D remains unstarted. No committed behavior demonstration, behavior
artifact, model record, binding declaration, temporal occurrence, source
evidence, interpretation evidence, or fixture mutation was introduced.

## 2. Authority and repository boundary

The accepted implementation boundary was:

```text
branch: bh001
accepted Slice B HEAD: 05177f7306ce745d093bd5f11abafc13a6274d0f
accepted main baseline: 46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
accepted discrepancy HEAD: eedae19a9b2542958f44e66af7117a981c7faeef
```

The owner-supplied pre-resumption discrepancy artifact was read completely
and verified before documentation or code changed:

```text
docs/superpowers/reports/2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md
SHA-256: 2a0efaf625ca5f836cbcb6c2baba6e1e2a2f2a8c2e7b99447fd51a37ac31d9cb
```

The current status-amended authoritative documents at the verified
implementation HEAD are:

```text
CLAUDE.md
SHA-256: 51c4712ec708ca9310727b06436aad497e821ebd2d4bc14e47ad9263607410be

docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
SHA-256: a5e0c8abb0cb96f432f5ad5b69298f12c3ea718a71b57f6872e22179dba70310

docs/superpowers/reports/2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md
SHA-256: fc9b1bd540345daa976a7607d5ccacadebfe4c2a0ecc1d2def57d1b9d2f8e99a
```

Those hash changes are documentation-only status and accepted-resolution
updates. The original discrepancy findings remain in the report; its status
now records the four owner decisions that resolved the preimplementation
blockers.

## 3. Owner-resolution documentation gate

Production code did not begin until the specification, Slice C plan, Slice C
acceptance matrix, discrepancy status, and focused documentation assertions
were amended and green.

The separate documentation commit is:

```text
59c9c7fb2b6931a53ca432837eaef507659e4374
docs: resolve BH-001 Slice C contract discrepancy
```

It records these normative resolutions.

1. The refusal vocabulary gained `model_unit_not_available`,
   `numeric_value_absent`, and `numeric_value_shape_mismatch`, with explicit
   null precedence and exact admission mappings.
2. BH authoritative validation proves internal coherence of carried lower
   public results and every BH-derived field, while inheriting rather than
   independently proving raw-source authenticity.
3. The three BH error classes and exact 21-name `__all__` are public;
   `NumericParityBreachError` is the exact CN class object.
4. Cohort derivation and parser scheduling follow the exact thirteen-step
   deterministic order fixed by the owner.

The documentation assertions were red before the amendments and became green
before production code began. Their final focused reproduction is included in
the `143 passed` Slice C result in Section 15.

## 4. Commit sequence

The reviewable commit sequence after the accepted Slice B HEAD is:

```text
cc8fcf085cf1c490d4773d8972f469159329c527
docs: record owner acceptance of BH-001 Slice B

eedae19a9b2542958f44e66af7117a981c7faeef
docs: record BH-001 Slice C contract discrepancy

59c9c7fb2b6931a53ca432837eaef507659e4374
docs: resolve BH-001 Slice C contract discrepancy

da4c479a1c4bd5f6c987a996df867466b882778e
test: define BH-001 Slice C evaluator contracts

f2d11aaa13027bb6861f9f4f395a34af82965f55
feat: add evidence-gated behavior evaluation

8866de1591bd02f429efe984104d739aef4fe86f
fix: harden BH-001 evaluator integrity

964bdaaaee9d68d15d8ac674ec00ea2f2526119d
test: complete BH-001 evaluator input matrix

d3ec7aa0cc401e5457b5ba8bdd85839f63815ef3
docs: record BH-001 Slice C reviewed status

d1e8e51a92e8bfd337136859c3a464613e61b7a1
docs: align BH-001 slice status assertions

ba3be133ad20ec24e40fd696f84a39ef01186fca
test: close BH-001 Slice C adversarial matrix

cc0c509fdd66bb4d59e3d004868992b154a2e9a6
test: pin BH null parser exclusion
```

No commit was amended or rewritten. Nothing was pushed, merged, rebased,
reset, or cherry-picked.

## 5. Changed files

Relative to accepted Slice B HEAD, Slice C changes exactly these files before
this report:

```text
M  CLAUDE.md
A  backend/behavior_evaluation/README.md
A  backend/behavior_evaluation/__init__.py
A  backend/behavior_evaluation/contracts.py
A  backend/behavior_evaluation/derivation.py
A  backend/behavior_evaluation/errors.py
A  backend/behavior_evaluation/facade.py
M  backend/model_kernel/README.md
M  docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md
M  docs/superpowers/plans/2026-08-29-bh001-slice-b-adversarial-acceptance-matrix.md
M  docs/superpowers/plans/2026-08-29-bh001-slice-b-implementation-plan.md
A  docs/superpowers/plans/2026-08-29-bh001-slice-c-adversarial-acceptance-matrix.md
A  docs/superpowers/plans/2026-08-29-bh001-slice-c-implementation-plan.md
M  docs/superpowers/reports/2026-08-29-bh001-slice-b-completion-report.md
A  docs/superpowers/reports/2026-08-30-bh001-slice-c-preimplementation-discrepancy-report.md
M  docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
A  tests/behavior_evaluation/__init__.py
A  tests/behavior_evaluation/helpers.py
A  tests/behavior_evaluation/test_architecture.py
A  tests/behavior_evaluation/test_documentation.py
A  tests/behavior_evaluation/test_evaluation.py
A  tests/behavior_evaluation/test_hostile_matrix.py
A  tests/behavior_evaluation/test_lifecycle_and_refusals.py
A  tests/behavior_evaluation/test_numeric_and_cohort.py
A  tests/behavior_evaluation/test_public_contract.py
A  tests/behavior_evaluation/test_revalidation.py
M  tests/model_kernel/test_behavior_query_contracts.py
M  tests/model_kernel/test_behavior_query_revalidation.py
M  tests/model_kernel/test_behavior_revalidation.py
A  tests/model_kernel/test_behavior_slice_c_resolution_documentation.py
```

The three Slice B model-kernel test files received only stronger public
boundary/status assertions and repair coverage. Accepted Slice A records,
Slice B production queries, canonicalization, store admission, indexes, and
historical membership constants are unchanged.

## 6. Exact public surface

`backend.behavior_evaluation.__all__` is pinned to exactly this ordered list:

```text
1.  BehaviorEvaluationError
2.  BehaviorEvaluationConfigurationError
3.  BehaviorEvaluationInputError
4.  NumericParityBreachError
5.  BehaviorParticipantSource
6.  BehaviorEvaluationExecution
7.  BehaviorComputedRelation
8.  BehaviorParticipantAdmission
9.  BehaviorParticipantModelAdmission
10. BehaviorParticipantObservationAvailability
11. BehaviorParticipantAttachmentAdmission
12. BehaviorParticipantSemanticAdmission
13. BehaviorParticipantUnitAdmission
14. BehaviorParticipantLockAdmission
15. BehaviorParticipantNumericAdmission
16. BehaviorAcquisitionCohortAdmission
17. BehaviorEvaluationRefusalReason
18. BehaviorEvaluationRefusal
19. BehaviorEvaluationParticipantResult
20. BehaviorEvaluationResult
21. BehaviorEvaluationQueries
```

There are no aliases, convenience wrappers, alternate query names, parser
exports, or canonical-decimal constructor exports.

The sole facade method is:

```python
behavior_evaluation(
    behavior_anchor_id,
    *,
    context,
    as_of,
    participants,
) -> BehaviorEvaluationResult
```

Facade construction accepts one existing public
`SemanticCompatibilityQueries` composition. Invalid construction raises:

```text
BehaviorEvaluationConfigurationError
code = BEHAVIOR_EVALUATION_CONFIGURATION_INVALID
```

Malformed query structure or participant-set misuse raises:

```text
BehaviorEvaluationInputError
code = BEHAVIOR_EVALUATION_INPUT_INVALID
```

Both inherit `BehaviorEvaluationError`. Direct Pydantic contract construction
retains ordinary `ValidationError`. Typed lower-layer failures propagate
unchanged.

## 7. Exact contract fields

All contracts use the repository's frozen, extra-forbidden,
`revalidate_instances="always"` convention.

`BehaviorParticipantSource` carries exactly:

```text
variable_anchor_id
entity_anchor_id
source
```

`BehaviorEvaluationRefusal` carries exactly:

```text
reason
participant_index
```

`BehaviorEvaluationParticipantResult` carries exactly:

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

`BehaviorEvaluationResult` carries exactly:

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

Required tuples have canonical empty values where applicable. Optional values
use explicit `None`. Indices are strict, nonnegative integers; booleans are
rejected.

## 8. Literal vocabularies

The public status aliases are exactly:

```text
BehaviorEvaluationExecution:
  not_executed | executed

BehaviorComputedRelation:
  equal | different

BehaviorParticipantAdmission:
  admitted | not_admitted

BehaviorParticipantModelAdmission:
  admitted | not_admitted

BehaviorParticipantObservationAvailability:
  observed | none_before_cutoff | not_evaluated

BehaviorParticipantAttachmentAdmission:
  not_evaluated | attached | not_attached

BehaviorParticipantSemanticAdmission:
  not_evaluated | admitted | not_admitted

BehaviorParticipantUnitAdmission:
  not_evaluated | exact | mismatch

BehaviorParticipantLockAdmission:
  not_evaluated | matched | mismatched

BehaviorParticipantNumericAdmission:
  not_evaluated | admitted | out_of_bounds

BehaviorAcquisitionCohortAdmission:
  not_evaluated | same_acquisition_cohort | different_acquisition_cohort
```

The ordered `BehaviorEvaluationRefusalReason` vocabulary is exactly:

```text
1.  behavior_not_registered
2.  behavior_not_declared
3.  behavior_inactive
4.  behavior_conflicted
5.  participant_model_not_registered
6.  observation_absent
7.  observation_not_attached
8.  binding_not_positive
9.  evidence_not_assessable
10. numeric_specification_not_available
11. numeric_specification_conflicted
12. model_quantity_kind_not_available
13. model_observation_role_not_available
14. model_unit_not_available
15. source_semantics_not_admitted
16. quantity_kind_lock_mismatch
17. observation_role_lock_mismatch
18. unit_lock_mismatch
19. numeric_value_absent
20. numeric_value_shape_mismatch
21. numeric_value_out_of_bounds
22. acquisition_cohort_mismatch
```

Ordinary absence, refusal, behavior conflict, inactivity, cohort mismatch, and
numeric bounds are result data, not exceptions.

## 9. Deterministic evaluation schedule

The implemented schedule follows the owner-fixed order.

1. Rebuild and strictly validate the request, including the behavior anchor,
   exact context, aware UTC-normalized cutoff, and exactly two distinct
   participant selectors.
2. Canonically sort selectors by variable anchor ID.
3. Query the accepted kernel `behavior_declaration(...)` facade at the
   injected model revision and exact context.
4. When registered, require the selectors' variable set to equal the
   permanent registered pair.
5. Invoke both explicit semantic branches exactly once in canonical variable
   order.
6. If either branch raises, finish both branch invocations and propagate the
   first typed failure in canonical participant order without fabricating a
   BH result.
7. Derive every independently applicable participant-local ordinary finding.
8. If both selected occurrences exist, compute acquisition-cohort admission
   even when another ordinary local refusal exists. If either is absent,
   cohort admission is `not_evaluated`.
9. A different cohort yields `different_acquisition_cohort` and prevents all
   numeric parser calls.
10. For a same cohort, call the public CN parser in canonical participant
    order for each numeric-eligible participant.
11. Known boolean, string, array, object, null, or nonnumeric-model-shape
    values never reach the parser.
12. Propagate the first typed CN parity failure in canonical participant order
    unchanged.
13. Execute equality only when every ordinary gate for both participants and
    the cohort admits; otherwise return every independently applicable
    refusal in deterministic order.

Staleness remains carried in the lower result. It is not an arbitrary BH
execution veto.

## 10. Exact acquisition-cohort boundary

The acquisition-cohort key is derived only from the selected occurrences'
accepted public fields:

```text
occurrence.subject.source_id
occurrence.subject.adapter_id
occurrence.attempt_id
occurrence.raw_record_id
occurrence.payload_checksum
```

All five fields must match exactly. Tests independently vary each field and
prove it changes admission to `different_acquisition_cohort`.

The following do not establish a cohort and do not participate in the key:

- source-native timestamps;
- receipt-time equality or proximity;
- resolution times;
- ordering;
- age or staleness;
- clock segment;
- model revision timestamps; and
- temporal directory order.

Same acquisition cohort means only that both properties were emitted from
the same accepted acquisition envelope. It does not prove physical
simultaneity, synchronized clocks, causal ordering, equal sensor sampling
times, flow, influence, control, or behavior at a port.

## 11. Participant and numeric admission

Each participant is evaluated through its exact explicit `SourceSelector`.
There is no source discovery, fallback, implicit selection, permutation
search, candidate-order selection, or cross-product.

Participant admission requires all of these independently disclosed gates:

- the variable and owner are admitted in the selected model revision;
- one explicitly selected observation exists before the cutoff;
- the observation is attached through an accepted positive binding;
- evidence is assessable through the existing lower pipeline;
- one uniquely current numeric VSP governs the variable;
- current unique quantity-kind and observation-role declarations exist;
- the numeric specification declares a model-unit identity;
- the selected source semantics are admitted;
- quantity kind, observation role, and unit match the participant's exact BH
  semantic lock;
- the value is non-null and has numeric JSON shape;
- the public CN parser admits the numeric lexeme; and
- both participants share the exact acquisition cohort.

Quantity-kind and unit identities match across the declaration locks.
Observation-role identities may differ. No unit conversion, ontology
inference, dimensional algebra, tolerance, residual, affine arithmetic,
coefficient, offset, quantization, rounding, or ambient Decimal context is
used.

Explicit JSON null has precedence:

```text
refusal: numeric_value_absent
numeric_admission: not_evaluated
```

It does not also yield `numeric_value_shape_mismatch`, including for a
nonnullable governing specification. Lower nullable/nonnullable disclosure is
carried unchanged. Independent earlier refusals remain present in gate order.

A present non-null value with the wrong observed JSON shape yields:

```text
refusal: numeric_value_shape_mismatch
numeric_admission: not_evaluated
```

No uniquely current numeric specification yields:

```text
refusal: numeric_specification_not_available
numeric_admission: not_evaluated
```

A numeric specification without a declared model unit yields:

```text
refusal: model_unit_not_available
unit_admission: not_evaluated
numeric_admission: not_evaluated
```

None of those cases invokes the CN parser or produces `different`.

## 12. CN parser reuse and equality

The evaluator imports only the public CN `parse_observed_decimal` function,
the public canonical result type used in its result contract, and the exact
public `NumericParityBreachError` class object. The BH package re-exports only
that exception class, not the parser or canonical-decimal constructor.

BH neither copies, forks, permissively wraps, privately imports, nor
reimplements the parser. CN's bounded lexical preflight runs before any
numeric construction. Tests pin admitted and one-step-over twins for every
inherited limit:

- input bytes;
- coefficient digits;
- fraction digits;
- exponent representation length;
- exponent magnitude;
- expanded integer digits;
- expanded fraction digits; and
- canonical output bytes.

Boolean, object, array, null, malformed, oversized, and expansion-hostile
`value_json` values never reach comparison as numbers. An ordinary parser
bounds refusal becomes `numeric_value_out_of_bounds`. A parser parity breach
propagates as the exact CN exception and never becomes `different`.

Equality compares the two canonical numeric results directly. It performs no
float conversion, subtraction, absolute difference, rounding, quantization,
tolerance, unit conversion, or dependence on ambient decimal precision or
rounding mode.

`equal` means only exact mathematical equality of those two admitted operands
under this one evaluation request. `different` means only exact mathematical
inequality. Neither result asserts behavior validity, consistency, fault,
health, safety, correctness, causality, control, or continued operation.

## 13. Authoritative result reconstruction

`BehaviorEvaluationResult` reconstructs every nested public object from
serialized field content. Its after-validation then rederives every BH-owned
field without filesystem or store access.

Revalidation proves:

- exact behavior anchor, context, and normalized cutoff echo;
- exact model-revision equality between behavior material and both semantic
  branches;
- one binding revision across participants;
- one interpretation revision across participants;
- exact participant-source ordering and selector-to-candidate identity;
- exact variable, requested entity, selected subject, and property identity;
- exact model registrations, owners, VSP result, and VSM result reconstructed
  from the carried behavior material through public model queries;
- exact registration participant pair;
- exact current declaration semantic locks;
- exact candidate and occurrence linkage through carried lower results;
- every participant gate, refusal, index, canonical decimal, and aggregate
  admission;
- the exact five-field cohort key and cohort admission;
- deterministic refusal ordering;
- execution state; and
- computed relation.

Hostile tests reject `model_construct`, `model_copy`, stale content-derived
model IDs, mixed model/binding/interpretation revisions, mixed cutoffs,
substituted contexts, selector retargeting, duplicated/swapped participants,
wrong union arms, forged records, indices, candidate links, gates, locks,
decimals, refusals, ordering, cohorts, execution states, relations, and extra
fields.

## 14. Honest carried-material integrity boundary

BH authoritative result validation proves the internal coherence of the
carried lower public results and every BH-derived field. It inherits, and does
not independently re-prove, raw-source authenticity. A fully coherent
lower-evidence content mutation accepted by the lower public contracts is
outside BH's store-independent detection boundary.

An executable limitation test demonstrates that boundary. It mutates coherent
lower occurrence content and the related carried checksum fields together,
allows the accepted lower contracts to revalidate the coherent mutation, and
then proves BH can only derive a result coherent with that carried world. The
test does not call the mutation authentic.

BH does not claim that `payload_checksum` authenticates an uncaptured payload,
does not consult a store or filesystem to broaden the claim, and does not
change temporal occurrence identity, raw-evidence contracts, extraction
contracts, or lower-layer result contracts. Content-bound lower occurrence
authentication remains separately owner-gated future work.

## 15. Red-before and fixed-after evidence

The red-first sequence was preserved at each gate.

### 15.1 Documentation resolution

The owner-resolution assertions initially failed against the unresolved
documents. Successive focused runs recorded `5`, then `3`, then `2`, then `1`
failure as the normative sections were made consistent. The documentation
gate then passed (`6 passed`) before production implementation began.

### 15.2 Public package and contracts

The first production-contract collection failed with exactly two import-time
errors because `backend.behavior_evaluation` did not exist. After the minimum
package and contracts were implemented, the initial focused surface passed
`23` tests.

### 15.3 Specialist reproductions and repairs

Independent adversarial review reproduced three integrity defects at the
first implementation commit:

1. stale carried VSP/model facts could remain internally coherent while
   differing from the behavior model material;
2. a unit-only source mismatch could report contradictory semantic admission;
3. a known lock mismatch could be hidden when another lock dimension was
   unavailable.

The repair commit `8866de1` closes all three. Model facts are now recomputed
from carried behavior material through public kernel queries; source unit
mismatch refuses both unit and semantic admission; and every known lock
mismatch survives an unavailable peer dimension.

The test reviewer then identified matrix coverage gaps for inconsistent
evidence scheduling, hostile JSON shapes, conflicted source interpretation,
the one-present/one-absent cohort case, full lower-package import scanning,
and explicit-null parser exclusion. Those gaps were closed in `ba3be13` and
`cc0c509` without broadening production scope.

The final explicit-null twins prove for both `nullable=False` and
`nullable=True` that:

```text
parser calls: eligible peer only
participant refusal_reasons: ("numeric_value_absent",)
numeric_admission: not_evaluated
canonical_decimal: None
execution: not_executed
computed_relation: None
```

### 15.4 Final focused result

The final focused command at exact implementation HEAD was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/behavior_evaluation \
  tests/model_kernel/test_behavior_slice_c_resolution_documentation.py \
  -q
```

Result:

```text
143 passed in 75.03s
```

## 16. Lifecycle and refusal demonstrations

Disposable tests independently demonstrate evaluation over declarations that
are:

- not registered;
- registered but not declared in the exact context;
- inactive because no current declaration tip remains;
- conflicted by a same-root fork;
- conflicted by different effective bodies across independent roots;
- declared by one healthy root;
- declared by multiple independent corroborating roots with identical
  effective engineering bodies; and
- historically revived when an explicit earlier membership omits a later
  successor or withdrawal.

For every structurally valid request, the evaluator still invokes and carries
both explicit lower semantic branches when the declaration is absent,
inactive, or conflicted. Declaration lifecycle never erases independently
available observation, binding, semantic, or staleness evidence.

Each of the 22 ordinary refusal reasons is independently reachable. Combined
tests prove deterministic ordering first by the public reason order and then
by canonical participant index. An inactive or conflicted declaration cannot
execute, but it does not suppress participant-local findings.

Equal and different worlds exist only in disposable tests. They establish:

```text
equal:
  both participants admitted
  cohort = same_acquisition_cohort
  execution = executed
  computed_relation = equal

different:
  both participants admitted
  cohort = same_acquisition_cohort
  execution = executed
  computed_relation = different
```

The genuine-ingestion equality test uses an accepted acquisition envelope
containing both explicit properties. It does not mutate or append committed
evidence.

## 17. Adversarial validation matrix

The executable matrix covers the following attack families.

### 17.1 Request and facade attacks

- invalid dependency construction;
- malformed behavior anchor IDs;
- malformed or forged assertion contexts;
- naive or coercible cutoffs;
- non-tuple, missing, extra, duplicated, or same-variable participants;
- boolean and coercible IDs or indices;
- participant variables that do not equal the permanent registration pair;
- swapped input order, proving canonical reconstruction rather than
  order-dependent behavior; and
- extra implication-bearing fields.

### 17.2 Lower-result and material substitution

- mixed model revisions;
- revision substitution with a valid alternate membership;
- mixed binding revisions;
- mixed interpretation revisions;
- mixed cutoffs;
- context and behavior-anchor substitution;
- variable and entity retargeting;
- selector subject/property retargeting;
- registration, owner, VSP, or VSM substitution;
- stale content-derived model IDs;
- candidate and occurrence substitution;
- duplicated, missing, reordered, or extra carried rows;
- wrong union arms;
- forged indices, including boolean indices; and
- inconsistent duplicate occurrences.

### 17.3 Derived-field forgeries

- model, observation, attachment, semantic, unit, lock, numeric, and aggregate
  admission;
- refusal reasons, participant association, and deterministic ordering;
- canonical numeric results;
- cohort admission and five-field key identity;
- execution state; and
- computed relation.

All detectable substitutions fail at the public `BehaviorEvaluationResult`
boundary without store or filesystem access.

### 17.4 Numeric denial-of-service and integrity attacks

- every inherited CN boundary and its one-step-over twin;
- excessive bytes, coefficient digits, fraction digits, exponent spelling,
  exponent magnitude, expanded digits, and canonical output;
- boolean, string, object, array, null, and malformed values;
- expansion-hostile numeric lexemes;
- an ordinary out-of-bounds first participant followed by a typed parity
  failure in the eligible peer;
- a participant-local attachment, semantic, unit, or lock refusal alongside
  an otherwise numeric-eligible peer parity failure;
- canonical first-error propagation order; and
- ambient decimal precision and rounding mutations.

No hostile nonnumeric value reaches behavior comparison as a number. A parity
breach is never translated into ordinary refusal data or `different`.

### 17.5 Determinism

Tests reverse caller participant order, vary hash seeds in subprocesses, and
revalidate repeated serialized results. Output order remains canonical by
variable anchor ID; lower branches and parsers run in that same order.

## 18. Specialist review synthesis

Four independent specialist perspectives were incorporated.

### 18.1 Software architecture

The architecture specialist approved the separate read-only upper-layer
composition and found no dependency-direction or store-ownership violation.
The review confirmed that kernel, model-state, temporal, binding, source,
semantic, observation, and constraint semantics remain owned by their
existing layers. It made no repository edits.

### 18.2 Backend engineering

The backend specialist independently reproduced the three defects listed in
Section 15.3. After the shared repair it reran the focused evaluator surface
(`66 passed` at that review point) and found no further Slice C production
defect. It specifically confirmed model-material closure, unit-only source
refusal, and preservation of known lock mismatches.

### 18.3 Software testing

The test specialist independently ran the focused surface, exercised source
conflict, nonnumeric shape, null, and genuine equality worlds, and challenged
the matrix against every Slice C acceptance item. Its final remaining C34a
observation led to the `cc0c509` nullable/nonnullable parser-spy twins. That
test-only closure produced the final `143 passed` focused result.

### 18.4 Final code integrity

The code reviewer found no Slice C production blocker. It confirmed the exact
21-name public surface, read-only boundary, model-material closure,
independent admission disclosures, demo preservation, accepted coherent
lower-evidence limitation, and Slice D exclusion. Its focused runs were green;
the subsequent change was only the additional C34a test proof.

The lead reconciled all specialist findings. No accepted finding was deferred
within Slice C, and no reviewer broadened the slice.

## 19. Verification results

All final commands use the explicit no-cache form so repository content is not
changed by pytest.

### 19.1 Focused and affected suites

```text
BH Slice C plus owner-resolution documentation: 143 passed in 75.03s
complete model-kernel:                         1102 passed in 100.09s
model-state + observation + ES + CN:            463 passed in 167.76s
binding + temporal + interpretation:            474 passed in 19.68s
architecture/import isolation:                   51 passed in 18.76s
PT/VP demo and revalidation preservation:         45 passed in 55.58s
OCP/STEP and PDF focused suites:                  120 passed in 388.60s
```

The affected lower-layer commands were:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_state tests/observation_compatibility \
  tests/semantic_compatibility tests/constraint_evaluation -q

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding tests/temporal_state tests/source_interpretation -q
```

The architecture command was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_isolation.py \
  tests/model_state/test_isolation.py \
  tests/observation_compatibility/test_isolation.py \
  tests/semantic_compatibility/test_isolation.py \
  tests/structural_evidence/test_isolation.py \
  tests/behavior_evaluation/test_architecture.py -q
```

The artifact-preservation command was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_demo_model.py \
  tests/model_kernel/test_demo_pt001.py \
  tests/model_kernel/test_demo_vp001.py \
  tests/model_state/test_demo_vp001.py \
  tests/model_kernel/test_variable_port_revalidation.py -q
```

The OCP/STEP and PDF focused surface was:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/structural_evidence/test_step_claims.py \
  tests/data_sources/test_ingestion_runner_step.py \
  tests/data_sources/test_step_extractor.py \
  tests/data_sources/test_ingestion_runner_pdf.py \
  tests/data_sources/test_pdf_extractor.py \
  tests/data_sources/test_pdf_detection_availability.py \
  tests/data_sources/test_pdf_coordinates.py \
  tests/data_sources/test_pdf_contracts.py -q
```

### 19.2 Full implementation-worktree suite

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q
```

Final exact result at `cc0c509fdd66bb4d59e3d004868992b154a2e9a6`:

```text
2741 passed in 719.02s
```

### 19.3 Compilation and diff hygiene

Backend compilation passed:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend
```

Both commands passed without output:

```bash
git diff --check
git diff --cached --check
```

## 20. Dual clean-checkout verification

Two fresh detached worktrees were created and advanced to the exact verified
implementation HEAD:

```text
/tmp/bh001-slice-c-base-clean-3MIRDy/checkout
/tmp/bh001-slice-c-extras-clean-X3ayR0/checkout

HEAD: cc0c509fdd66bb4d59e3d004868992b154a2e9a6
```

Both installed base and development dependencies from committed requirement
files:

```bash
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

The extras checkout additionally installed the CAD and PDF dependencies with
hash checking:

```bash
venv/bin/pip install --require-hashes \
  -r requirements-cad.txt -r requirements-pdf.txt
```

Each checkout ran:

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q
```

The restricted sandbox denied exactly one local-socket fixture in each
checkout:

```text
tests/data_sources/test_http_api_connector.py::
TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation

PermissionError: [Errno 1] Operation not permitted
```

All other results were:

```text
base-only:  2705 passed, 35 skipped, 1 sandbox-denied error in 258.07s
all-extras: 2740 passed, 1 sandbox-denied error in 322.83s
```

The one test was rerun with the required permission in each checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation \
  -q
```

Authorized results:

```text
base-only loopback:  1 passed in 0.73s
all-extras loopback: 1 passed in 0.75s
```

Therefore the effective final columns are:

```text
base-only:  2706 passed, 35 skipped
all-extras: 2741 passed
```

Both detached worktrees were clean at the exact implementation HEAD after the
run. Neither checkout used implementation-worktree files, uncommitted report
content, directory-derived model history, or a locally installed BH package.

## 21. Historical replay and artifact preservation

Every accepted explicit model membership remains unchanged and replays
without migration or inferred behavior:

```text
9 records
10 records
11 records
14 records
16 records
18 records
28 records
29 records
```

Pre-BH memberships return structured behavior absence through the accepted
Slice B kernel API. Evaluation carries those exact model revisions and never
uses `as_of` to select or reconstruct model membership.

The committed demo remains:

```text
model record count: 29
BRG records:         0
BHD records:         0
BHW records:         0
model revision:      mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

Pinned identities and hashes remain:

```text
VPA:
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49

VPA stored-file SHA-256:
95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e

pre-VP 28-record revision:
mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2

current 29-record revision:
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652

VP artifact SHA-256:
a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3

PT artifact SHA-256:
53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8
```

The VPA stored-file hash was recomputed directly. The model revision,
historical memberships, and deterministic PT/VP artifact hashes were
regenerated and pinned by the 45-test preservation surface. No model, binding,
interpretation, source, temporal, structural, PT, or VP file changed.

## 22. Architecture and import-direction evidence

The production dependency direction is:

```text
system_identity
      ↑
model_kernel
      ↑
model_state / observation_compatibility / semantic_compatibility
      ↑
behavior_evaluation
```

`behavior_evaluation` has one narrowly documented dependency on the public CN
numeric parser. It imports no CN declarations, query facade, verdicts, or
constraint semantics.

AST and import-isolation tests prove:

- model-kernel does not import behavior evaluation, state, temporal, binding,
  ES, CN evaluation, interpretation, or data-source modules;
- no lower layer imports behavior evaluation;
- behavior evaluation does not import model, binding, interpretation,
  temporal, source, or evidence stores;
- it constructs no repository, store, ledger, database, cache, or projection;
- it contains no filesystem path, SQLite, socket, subprocess, network, or
  write API;
- it accesses no private field of a composed foreign query object;
- it introduces no graph traversal or behavior inference; and
- evaluation results are never persisted.

The exact 51-test architecture/isolation surface is green.

## 23. Explicit exclusions and limitations

Slice C does not implement or assert:

- behavior inference from names, ownership, hierarchy, CAD, topology, PIF,
  PCN, PCM, VPA, semantics, constraints, or temporal correlation;
- port participation, behavior at a port, value at a port, signal direction,
  flow, influence, cause, effect, command, response, control, or state
  transition;
- affine behavior, expressions, tolerances, inequalities, residuals,
  arithmetic graphs, dimensional algebra, or external executable models;
- unit conversion, ontology inference, interpolation, resampling, range
  search, lag compensation, synchronization, persistence assumptions, or
  cross-clock claims;
- behavioral validity, engineering consistency, correctness, diagnosis,
  recommendation, health, safety, fault, normality, or operating condition;
  or
- committed evaluation truth.

The accepted limitation is explicit: BH validates the internal coherence of
carried lower public results, not cryptographic raw-source authenticity.
Separately owner-gated lower-layer content-bound occurrence authentication may
strengthen that boundary in a future project, but BH-001 does not silently
invent it.

## 24. Slice D and remaining owner gates

Slice D has not started. Specifically, this slice minted or appended no:

- `VariableRegistration`;
- `BehaviorRegistration`;
- `BehaviorRuleDeclaration`;
- `BehaviorRuleWithdrawal`;
- VSP or VSM;
- port or VPA;
- binding `AnchorDeclaration`;
- interpretation or temporal record; or
- demonstration artifact.

No Slice D identity, canonical record hash, membership order, final model
revision, artifact size, or artifact SHA-256 was invented.

If Slice C is accepted, Slice D remains a separate owner gate. Its disposable
rehearsal must first derive deterministic identities, membership, revision,
and artifact bytes using public APIs. The authoritative 29-to-32 ledger append
may occur only after the rehearsal identities receive owner approval. The
committed demonstration remains declaration-only and must honestly return
`not_executed`; disposable fixtures alone demonstrate `equal` and `different`.

## 25. Reproduction command summary

From repository root at the implementation HEAD:

```bash
git status --short --branch
git rev-parse HEAD

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/behavior_evaluation \
  tests/model_kernel/test_behavior_slice_c_resolution_documentation.py -q

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/model_kernel -q

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend
git diff --check
git diff --cached --check
```

Clean-checkout reproduction additionally installs committed base/development
requirements in both environments and the two hash-pinned optional lock files
in the all-extras environment, then runs the same full-suite command.

## 26. Repository and remote status before report commit

Immediately before this report was staged:

```text
branch: bh001
implementation HEAD: cc0c509fdd66bb4d59e3d004868992b154a2e9a6
tracked implementation changes: none
untracked content: this completion report only
origin fetch URL: https://github.com/MafasaBytes/operation-house-keeping.git
origin push URL:  https://github.com/MafasaBytes/operation-house-keeping.git
bh001 upstream: none
main: 46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 [origin/main]
```

No remote operation was performed. No commit was pushed or merged.

## 27. Final status

BH-001 Slices A and B are owner accepted. Slice C is implemented,
adversarially reviewed, full-suite verified, and reproduced in base-only and
all-extras clean checkouts; it is awaiting owner acceptance. Slice D has not
started.

The only genuine next owner question is whether to accept Slice C at the exact
implementation HEAD recorded above. Acceptance would authorize only a future,
separately bounded Slice D request; it would not itself authorize fixture or
ledger mutation.

END OF BH-001 SLICE C COMPLETION REPORT
