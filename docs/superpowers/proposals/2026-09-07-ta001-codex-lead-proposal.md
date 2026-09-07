# TA-001 — Evidence-Gated Declared Transition Assessment

Status: lead architecture proposal only. No implementation, acceptance, model
record, fixture, demonstration, or persistence is authorized by this document.

## 1. Verified baseline and architectural findings

The investigation was performed on clean branch `main` at
`948374eec3cd49596fe19548a58a4fb10760a433`, whose subject is
`docs: reconcile root README through EA-001`. `main`, `HEAD`, and
`origin/main` were equal. The authoritative demo model loaded as exactly 36
records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The record inventory contained FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`.
Its accepted aggregate and the accepted flow disclosure remained unchanged.
EA-001 was complete and owner accepted, and no successor milestone was
approved or in implementation.

The following accepted facts control this proposal:

| Layer | Public fact used by TA-001 | Fact deliberately not inferred |
|---|---|---|
| ST-002 model query | `TransitionDeclarationResult` carries one complete `ModelQueryMaterial`, exact context, lifecycle, effective-body groups, and exact endpoint STD-pin alignment | transition occurrence, execution, trigger, guard, or action |
| ST-001 classification | `StateClassificationResult` carries one exact state declaration and every CN result used at one normalized cutoff | simultaneity, cohort, persistence, dwell, or current physical state |
| CN/ES/VS chain | each condition row has strict indices to one CN candidate; the CN result carries the semantic result; the semantic result carries the exact `VariableValueCompatibilityResult` and value candidate | source authority, physical truth, or generic evidence identity |
| EA selection | each non-refused selection carries a bounded captured snapshot, selected occurrence, declared horizon, coverage, and content fingerprint | global atomicity, later immutability, trusted time, or authentication |
| EA alignment | `OperationalEvidenceAlignmentResult` aligns one exact EA selection to one exact `VariableValueCompatibilityResult` and identifies the exact candidate | a registry, generic adapter, or second consumer |

The repository has no `backend/evidence_assurance/README.md` at this
checkpoint; its accepted synthesis, public contracts, exports, tests, and
final acceptance records provide the governing EA evidence. The root README
correctly reserves the missing EA decision reconciliation as ADR-0019 work.
This proposal does not create or modify that ADR. A later ADR-0019 must record
the accepted EA captured-view, fingerprint, named-reread, pure-validation, and
single-consumer alignment decisions on which TA-001 depends. A later TA-001
ADR, numbered only after that reconciliation, must record the pure endpoint-
pattern composition and its non-occurrence boundary.

## 2. Objective and exact non-objectives

The objective is one bounded, deterministic, read-only answer to this
question: do exact accepted inputs support the declared from-state at an
explicit earlier cutoff and the declared to-state at an explicit later
cutoff, under the fixed v1 policies and complete governing operational
evidence?

The strongest positive answer is exactly
`bounded_evidence_supports_declared_endpoint_pattern`. It describes two
separately classified endpoint views at two ordered cutoffs. It does not say
that the transition occurred between them.

TA-001 does not establish or infer transition occurrence or non-occurrence;
an occurrence identity, history, interval, duration, continuity, dwell,
debounce, hysteresis, or path; a trigger, guard, enablement, executability,
action, effect, command, or control; causality, mechanism, diagnosis, fault,
safety, correctness, or recommendation; exclusivity or completeness of the
state vocabulary; flow, transfer, conservation, or balance; source, sensor,
signer, or clock authority; physical truth; or a generic immutable assessment
identity. It neither ranks conflicting declarations nor manufactures missing
facts from timestamps, IDs, filenames, append order, authority labels, or
lexical order.

## 3. Recommendation and prerequisite decision

TA-001 is the smallest coherent next capability and is viable without a new
lower contract. The recommended v1 is a pure upper composition over already-
computed public results. It must require complete evidence alignment and a
matched independently supplied EA snapshot fingerprint for every governing
observed candidate before assessment executes.

No new temporal, source, model, state, CN, semantic, observation, EA, or
alignment operation is required. In particular, TA-001 must not extend
`evidence_alignment` to a second consumer: it consumes its existing nominal
`OperationalEvidenceAlignmentResult` and joins that result to the exact
`VariableValueCompatibilityResult` already nested in each ST classification.
The join is therefore evidence-backed rather than value-, timestamp-, ID-,
checksum-, or locator-based.

A facade that computes all lower results is not recommended for v1. Such a
facade would need new caller policy for per-condition sources, horizons, and
independently retained fingerprints and would misleadingly suggest a cross-
store snapshot. The pure composition is complete on its own; orchestration is
not a prerequisite.

## 4. Module placement and import direction

The proposed package is `backend.transition_assessment`. Its only runtime
dependencies are the public roots of `backend.model_kernel`,
`backend.state_classification`, and `backend.evidence_alignment`, plus
Pydantic and the standard library.

```text
backend.model_kernel ---------------------+
                                          |
backend.state_classification -------------+--> backend.transition_assessment
                                          |
backend.evidence_alignment ---------------+
    |                    |
    v                    v
evidence_assurance   observation_compatibility
```

The arrows point from consumer to dependency. No existing package may import
`backend.transition_assessment`. TA-001 may not import a private model store,
filesystem evidence reader, temporal SQLite implementation, connector,
projector, writer, UI, planner, controller, or any private module of a lower
package. The package owns no store, cache, database, ledger, identity, anchor,
minter, signature, clock, connector, network client, or write path.

The root module re-exports only the exact public names pinned in Section 9.
Importing it performs no I/O, environment discovery, clock read, or dependency
construction.

## 5. Exact inputs and public join proof

One request carries these four lower-result inputs exactly once each: one
`TransitionDeclarationResult`, one from `StateClassificationResult`, one to
`StateClassificationResult`, and one bounded tuple of distinct
`OperationalEvidenceAlignmentResult` values. It also carries explicit echo
fields for the requested transition anchor, exact context, and two cutoffs so
a substituted lower result cannot redefine the question.

For every classification condition, the join is derived as follows:

1. `StateClassificationConditionResult.constraint_evaluation_index` selects
   the exact `ConstraintEvaluationResult` carried by the classification.
2. Its `candidate_index` selects the exact
   `CandidateConstraintEvaluation`. The accepted ST derivation requires one
   semantic candidate for every registered explicit condition.
3. The CN result's `semantic_compatibility` carries one
   `VariableSemanticCompatibilityResult`; the same index selects its
   `CandidateSemanticCompatibility`.
4. That semantic candidate's `value_candidate` must equal the same-index
   candidate in `semantic_compatibility.value_compatibility`, as enforced by
   the accepted ES and VS contracts.
5. If the value candidate's state candidate has a bound observation, its full
   public `TemporalOccurrence` is the classification's governing selected
   occurrence. If it has no bound observation, that condition has no governing
   selected occurrence and requires no EA alignment.
6. Exactly one distinct alignment input must carry a `request.compatibility`
   equal to that complete `VariableValueCompatibilityResult`. The alignment's
   `aligned_candidate_index` must equal the condition's candidate index before
   it can pass the assessment gate.
7. The accepted alignment result then traces that candidate to an EA selection
   with the exact cutoff, six-field locator, complete occurrence equality,
   endpoint closure, selection status, snapshot validation, expected-
   fingerprint relation, selected-occurrence role, and snapshot content
   fingerprint.

This graph proves the candidate join sufficient. Equal values, timestamps,
checksums, occurrence IDs, record IDs, or locators alone never satisfy a step.
The complete nominal lower objects must compare equal at their designated
join. The TA result carries strict trace indices into the request rather than
duplicating lower material or raw payload bytes.

If multiple conditions use an equal complete value-compatibility result, one
alignment is carried once and multiple condition traces may cite its index.
The alignment collection contains exactly one row per distinct required
compatibility. It contains no row for an observation-absent condition and no
unmatched extra row. Rows are ordered by their first governing coordinate:
from endpoint before to endpoint, then ascending condition index. A missing,
duplicate, extra, reordered, or substituted alignment collection is an
invalid request, not an invitation to guess.

## 6. Bounded temporal policy, axes, cohort treatment, and limits

The fixed policy is
`declared_endpoint_pattern_at_ordered_cutoffs` version
`ta001.endpoint_pattern.v1`. The from cutoff must be strictly earlier than the
to cutoff after UTC normalization. Equal and reversed aware cutoffs are valid
facts but make assessment not execute. Naive datetimes and non-datetime
subclasses are malformed input.

Each endpoint retains ST-001's
`independent_latest_at_or_before_cutoff` behavior. Receipt time governs
occurrence selection within each carried EA result. Source-effective wall time
governs attempt coverage within each EA horizon. Source-native observation
time and clock segment remain disclosure only. TA performs no cross-clock or
source-time comparison and never substitutes one axis for another.

Different conditions may therefore use different receipt times, source times,
clock segments, pre-horizon seeds, source locators, and declared horizons.
The typed disclosure is
`independent_latest_per_condition_not_a_temporal_cohort`; continuity is always
`not_assessed`. No common instant, acquisition cohort, synchronization,
persistence, or dwell is implied.

The fixed limits are:

| Limit | Value | Rule |
|---|---:|---|
| endpoint classifications | 2 | exactly from and to |
| conditions per endpoint | 64 | inherited ST-001 bound |
| condition traces | 128 | one per carried classification condition |
| distinct alignment results | 128 | one per distinct governing compatibility at most |
| canonical request bytes | 134,217,728 | aggregate, checked before result derivation |
| reconstructed nodes | 2,000,000 | aggregate hostile-graph bound |
| nesting depth | 128 | aggregate hostile-graph bound |

The byte limit measures the canonical serialized request after strict scalar
admission and before a result is retained. It does not replace any lower EA
limit. Exceeding any fixed limit produces the typed input error and no partial
assessment.

## 7. Declaration, pin, context, subject, and currentness handling

Assessment admission requires all of the following:

- the transition result answers for the request's exact transition anchor and
  context;
- its conclusion is `declared`, its lineage summary is `healthy`, and it has
  exactly one effective-body group;
- that group's from and to endpoints both disclose `exact_current` pin
  alignment in the carried model membership;
- the from and to classifications answer for those exact ordered endpoint
  state anchors and the request context;
- the transition and both classifications carry the exact same complete
  `ModelRevision`, not merely the same revision ID string;
- both endpoint state registrations have the transition registration's exact
  subject entity; and
- each classification cutoff equals its corresponding explicit request cutoff.

`exact_current` means current only within the carried model membership. TA does
not query a current filesystem ledger and must never relabel historical
membership-relative currentness as globally current. Independent healthy roots
that corroborate one effective body remain visible in the carried transition
result. A same-root fork, cross-root effective-body disagreement, inactive
lineage, undeclared transition, or unregistered transition produces a
structured non-executed result. No authority, timestamp, ID, or lexical rule
selects a winner.

A wrong endpoint, subject, context, revision, or pin is independently
disclosed. Status precedence never erases another applicable issue. Shapes
that contradict the authoritative lower result contracts are malformed input
and fail before derivation rather than becoming a synthetic lifecycle state.

## 8. Governing evidence completeness rule

Every condition with a bound governing observation must have its exact
alignment entry. An entry passes the TA evidence gate only when all of these
are true:

- its complete carried compatibility equals the classification's nested
  complete value-compatibility result;
- its aligned candidate index equals the classification condition's governing
  candidate index;
- its status is `aligned_with_complete_evidence`;
- its EA selection status is `complete_within_declared_horizon`;
- its expected snapshot fingerprint was supplied and its relation is
  `matched`; and
- its lower snapshot validation is structurally self-consistent with matched
  embedded and expected fingerprints.

`aligned_with_incomplete_evidence` remains a successful lower occurrence
alignment but fails the TA execution gate. It yields
`incomplete_within_one_or_more_declared_horizons`; it never becomes complete
transition evidence. EA refusal, fingerprint mismatch, fingerprint omission,
fingerprint not evaluated, or a non-aligned governing occurrence also prevents
execution. All independently applicable issues are retained in normative
order.

The endpoint classifications themselves must have `condition_coverage ==
complete` and `execution == executed`. This deliberately refuses to turn an
ST negative produced by one violated condition plus unknown siblings into a
TA conclusion. When all gates pass, two matches produce the positive
conclusion; either complete endpoint non-match produces the negative
conclusion. The negative wording means only that this bounded evidence does
not support the declared endpoint pattern. It is not transition
non-occurrence.

An independently retained expected fingerprint detects a coherently replaced
snapshot plus embedded fingerprint when the retained value itself is not
replaced. If an attacker replaces the snapshot, embedded fingerprint, and
supposedly independent expected value together, pure TA validation cannot
authenticate the original. The result must state this limitation and make no
signature, authority, trusted-time, or truth claim.

## 9. Exact proposed public contracts and export surface

All models are frozen Pydantic models with `extra="forbid"` and
`revalidate_instances="always"`. All indices are `StrictInt`, non-boolean,
nonnegative, and range-checked. All scalar strings are ordinary strings rather
than subclasses. Literal order below is normative.

```python
TransitionAssessmentInputErrorCode = Literal[
    "TRANSITION_ASSESSMENT_INPUT_INVALID",
]
TransitionAssessmentEndpointRole = Literal["from", "to"]
TransitionAssessmentDeclarationAdmission = Literal[
    "not_admitted", "admitted",
]
TransitionAssessmentContextRelation = Literal["exact", "different"]
TransitionAssessmentModelRevisionRelation = Literal["exact", "different"]
TransitionAssessmentCutoffRelation = Literal[
    "ordered_earlier_to_later", "equal", "reversed",
]
TransitionAssessmentEndpointRelation = Literal[
    "exact", "different", "not_evaluated",
]
TransitionAssessmentSubjectRelation = Literal[
    "exact", "different", "not_evaluated",
]
TransitionAssessmentObservationPresence = Literal["present", "absent"]
TransitionAssessmentAlignmentRelation = Literal[
    "aligned_with_complete_evidence",
    "aligned_with_incomplete_evidence",
    "not_aligned",
    "not_evaluated",
    "not_applicable",
]
TransitionAssessmentExpectedFingerprintRelation = Literal[
    "matched", "mismatched", "not_supplied", "not_evaluated",
    "not_applicable",
]
TransitionAssessmentEvidenceCompleteness = Literal[
    "not_evaluated",
    "complete_within_all_declared_horizons",
    "incomplete_within_one_or_more_declared_horizons",
]
TransitionAssessmentSourceTimeUse = Literal[
    "disclosure_only_not_compared",
]
TransitionAssessmentTemporalCohort = Literal[
    "independent_latest_per_condition_not_a_temporal_cohort",
]
TransitionAssessmentContinuity = Literal["not_assessed"]
TransitionAssessmentExecution = Literal["not_executed", "executed"]
TransitionAssessmentConclusion = Literal[
    "bounded_evidence_supports_declared_endpoint_pattern",
    "bounded_evidence_does_not_support_declared_endpoint_pattern",
]
TransitionAssessmentIssueCode = Literal[
    "transition_anchor_mismatch",
    "transition_not_registered",
    "transition_not_declared",
    "transition_conflicted",
    "transition_inactive",
    "context_mismatch",
    "model_revision_mismatch",
    "from_state_anchor_mismatch",
    "to_state_anchor_mismatch",
    "endpoint_subject_mismatch",
    "endpoint_pin_not_exact_current",
    "endpoint_classification_cutoff_mismatch",
    "cutoffs_equal",
    "cutoffs_reversed",
    "endpoint_classification_not_executed",
    "endpoint_classification_incomplete",
    "governing_selection_refused",
    "governing_expected_fingerprint_not_supplied",
    "governing_expected_fingerprint_not_evaluated",
    "governing_expected_fingerprint_mismatched",
    "governing_occurrence_not_aligned",
    "governing_evidence_incomplete",
]
```

Exact model field order and types are:

```python
class TransitionAssessmentPolicy:
    kind: Literal["declared_endpoint_pattern_at_ordered_cutoffs"]
    version: Literal["ta001.endpoint_pattern.v1"]
    endpoint_selection: Literal[
        "independent_latest_per_condition_at_or_before_cutoff"]
    evidence_requirement: Literal[
        "complete_alignment_with_matched_expected_fingerprint"]
    source_time_use: Literal["disclosure_only"]
    temporal_cohort: Literal["not_asserted"]
    continuity: Literal["not_assessed"]

class TransitionAssessmentLimits:
    schema_version: Literal["1"]
    maximum_endpoint_conditions: Literal[64]
    maximum_condition_traces: Literal[128]
    maximum_distinct_alignments: Literal[128]
    maximum_canonical_request_bytes: Literal[134217728]
    maximum_reconstructed_nodes: Literal[2000000]
    maximum_nesting_depth: Literal[128]

class DeclaredTransitionAssessmentRequest:
    schema_version: Literal["1"]
    transition_anchor_id: StrictStr
    context: AssertionContext
    from_as_of: UtcDatetime
    to_as_of: UtcDatetime
    policy: TransitionAssessmentPolicy
    transition: TransitionDeclarationResult
    from_classification: StateClassificationResult
    to_classification: StateClassificationResult
    evidence_alignments: tuple[OperationalEvidenceAlignmentResult, ...]

class TransitionAssessmentIssue:
    code: TransitionAssessmentIssueCode
    endpoint_role: TransitionAssessmentEndpointRole | None
    condition_index: StrictNonnegativeInt | None
    evidence_alignment_index: StrictNonnegativeInt | None

class TransitionAssessmentConditionTrace:
    trace_index: StrictNonnegativeInt
    endpoint_role: TransitionAssessmentEndpointRole
    condition_index: StrictNonnegativeInt
    constraint_evaluation_index: StrictNonnegativeInt
    semantic_candidate_index: StrictNonnegativeInt | None
    value_candidate_index: StrictNonnegativeInt | None
    observation_presence: TransitionAssessmentObservationPresence
    evidence_alignment_index: StrictNonnegativeInt | None
    alignment_relation: TransitionAssessmentAlignmentRelation
    evidence_selection_status: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "refused",
        "not_applicable",
    ]
    evidence_completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "not_applicable",
    ]
    expected_fingerprint_relation: (
        TransitionAssessmentExpectedFingerprintRelation
    )
    selected_occurrence_role: Literal[
        "in_horizon_member", "pre_horizon_seed", "not_applicable",
    ]
    source_time_use: Literal["disclosure_only", "not_applicable"]

class TransitionAssessmentEndpointDisclosure:
    role: TransitionAssessmentEndpointRole
    declared_state_anchor_id: StrictStr | None
    classified_state_anchor_id: StrictStr
    state_anchor_relation: TransitionAssessmentEndpointRelation
    subject_relation: TransitionAssessmentSubjectRelation
    pin_alignment: TransitionEndpointPinAlignment | None
    classification_context_relation: TransitionAssessmentContextRelation
    classification_cutoff_relation: TransitionAssessmentEndpointRelation
    state_declaration_conclusion: StateDeclarationConclusion
    condition_coverage: StateConditionCoverage
    classification_execution: StateClassificationExecution
    computed_match: StateComputedMatch | None
    condition_trace_indices: tuple[StrictNonnegativeInt, ...]

class DeclaredTransitionAssessmentResult:
    schema_version: Literal["1"]
    request: DeclaredTransitionAssessmentRequest
    ruleset_version: Literal["ta001.1"]
    fixed_limits: TransitionAssessmentLimits
    declaration_admission: TransitionAssessmentDeclarationAdmission
    context_relation: TransitionAssessmentContextRelation
    model_revision_relation: TransitionAssessmentModelRevisionRelation
    cutoff_relation: TransitionAssessmentCutoffRelation
    from_endpoint: TransitionAssessmentEndpointDisclosure
    to_endpoint: TransitionAssessmentEndpointDisclosure
    condition_traces: tuple[TransitionAssessmentConditionTrace, ...]
    evidence_completeness: TransitionAssessmentEvidenceCompleteness
    source_time_use: TransitionAssessmentSourceTimeUse
    temporal_cohort: TransitionAssessmentTemporalCohort
    continuity: TransitionAssessmentContinuity
    execution: TransitionAssessmentExecution
    issues: tuple[TransitionAssessmentIssue, ...]
    conclusion: TransitionAssessmentConclusion | None
```

`TransitionAssessmentError` is the base exception.
`TransitionAssessmentInputError` is its only v1 subclass and accepts exactly
`error_code: TransitionAssessmentInputErrorCode` and `message: StrictStr`.
Instances expose exactly `error_code` and `message`; messages are fixed safe
text of 1–300 characters with no paths, credentials, payload content, or raw
lower exception. Malformed requests, hostile graphs, invalid alignment
collections, and fixed-limit violations raise
`TRANSITION_ASSESSMENT_INPUT_INVALID`. Valid lower statuses and relational
failures return structured non-executed results.

The sole operation is:

```python
assess_declared_transition_endpoints(
    request: DeclaredTransitionAssessmentRequest,
) -> DeclaredTransitionAssessmentResult
```

The exact ordered root `__all__` is:

```python
[
    "TransitionAssessmentError",
    "TransitionAssessmentInputError",
    "TransitionAssessmentInputErrorCode",
    "TransitionAssessmentEndpointRole",
    "TransitionAssessmentDeclarationAdmission",
    "TransitionAssessmentContextRelation",
    "TransitionAssessmentModelRevisionRelation",
    "TransitionAssessmentCutoffRelation",
    "TransitionAssessmentEndpointRelation",
    "TransitionAssessmentSubjectRelation",
    "TransitionAssessmentObservationPresence",
    "TransitionAssessmentAlignmentRelation",
    "TransitionAssessmentExpectedFingerprintRelation",
    "TransitionAssessmentEvidenceCompleteness",
    "TransitionAssessmentSourceTimeUse",
    "TransitionAssessmentTemporalCohort",
    "TransitionAssessmentContinuity",
    "TransitionAssessmentExecution",
    "TransitionAssessmentConclusion",
    "TransitionAssessmentIssueCode",
    "TransitionAssessmentPolicy",
    "TransitionAssessmentLimits",
    "DeclaredTransitionAssessmentRequest",
    "TransitionAssessmentIssue",
    "TransitionAssessmentConditionTrace",
    "TransitionAssessmentEndpointDisclosure",
    "DeclaredTransitionAssessmentResult",
    "assess_declared_transition_endpoints",
]
```

No convenience alias, query facade, canonical-byte function, lower type, or
alternate public name is exported.

## 10. Full-instance reconstruction and forgery resistance

The public operation first serializes caller content to an ordinary bounded
graph, rejects cycles, hidden model extras, private/cache laundering,
unsupported containers, non-string mapping keys, scalar subclasses, booleans
in every index/count field, excessive nodes/depth/bytes, and unexpected union
arms, and only then reconstructs every nominal nested public contract.

Reconstruction order is request scalars and fixed policy, transition result,
from classification, to classification, and alignment entries. It uses the
public `model_validate` boundary of each exact lower type. It does not trust
`isinstance`, `model_construct`, `model_copy`, a lower cached property, or a
caller-defined equality method. Serialized shape before and after lower
reconstruction must be identical, apart from the documented UTC
normalization. Any dropped hidden key is invalid.

After reconstruction, request validation re-derives the complete required
compatibility set from both classifications, validates the exact distinct
alignment set and first-use ordering, and checks every index before access.
Only validated working state is published to derivation. A rejected lower
object cannot support a trace, admission, fingerprint match, or conclusion.

`DeclaredTransitionAssessmentResult.model_validate(...)` repeats full nested
request reconstruction and recomputes every limit, admission, relation,
endpoint disclosure, condition trace, evidence summary, issue, execution
state, and conclusion. A supplied derived field is compared against this
authoritative derivation. Missing, duplicated, reordered, out-of-range, or
boolean trace/issue/alignment indices; stale IDs; mixed contexts or cutoffs;
substituted revisions; forged lower instances; hidden extras; and wrong union
arms reject. Result validation performs no store, filesystem, network,
environment, connector, or clock access.

This validates only carried content. It cannot authenticate lower source bytes
or current store membership absent those stores. It does not repeat the
request's lower material outside the request and does not embed raw payload
bytes.

## 11. Deterministic ordering and canonical serialization

Normative order is:

- endpoints: from, then to;
- classification conditions: accepted ST condition order;
- traces: from condition index ascending, then to condition index ascending;
- distinct alignments: first trace that governs them, with reuse by later
  trace indices;
- endpoint trace indices: ascending global trace index;
- issues: issue-code literal order from Section 9, then endpoint role from/to
  with `None` first, then condition index, then alignment index, using `None`
  before zero;
- lower tuples: their already accepted lower canonical order, never resorted
  by TA; and
- no ordering rule selects a lifecycle winner.

Canonical TA bytes are an internal testing representation, not a public
identity. They are the reconstructed result's JSON-mode field graph encoded as
UTF-8 JSON with keys sorted by Unicode code point, no insignificant
whitespace, `ensure_ascii=False`, `allow_nan=False`, arrays in normative
order, integers in base ten, and aware datetimes normalized to UTC with `Z`
and the shortest exact fractional-second form. Floats and non-finite numbers
are forbidden. The bytes end with no newline.

TA-001 creates no result fingerprint, record ID, anchor, signature, receipt,
or persistent artifact. Canonical-byte equality is tested across mapping-key
construction orders and hash seeds. A permutation of the semantically ordered
alignment tuple is consistently rejected rather than silently reinterpreted.

## 12. Refusal, disclosure, and conclusion tables

### 12.1 Structural admission

| Input condition | Outcome |
|---|---|
| malformed anchor, policy, context, datetime, lower object, scalar, union arm, or graph | typed input error; no result |
| more than a fixed bound | typed input error; no partial allocation or result |
| missing, duplicate, extra, reordered, or substituted alignment collection | typed input error; no guessed join |
| valid lower lifecycle or relational status | reconstruct all inputs and return structured result |

### 12.2 Declaration and endpoint admission

| Carried facts | Admission | Execution |
|---|---|---|
| exact anchor/context/revision, declared healthy one body, exact-current pins, exact endpoint states/subjects/cutoffs | `admitted` | continue to evidence gate |
| unregistered, undeclared, conflicted, or inactive transition | `not_admitted` | `not_executed`; exact lifecycle issue retained |
| stale pin, wrong anchor/state/subject/context/revision/cutoff | `not_admitted` | `not_executed`; every applicable issue retained |
| equal or reversed request cutoffs | declaration admission remains independent | `not_executed`; cutoff relation and issue retained |

### 12.3 Evidence summary

| State/alignment facts | Evidence completeness | Execution effect |
|---|---|---|
| both classifications complete; every selection and alignment complete | `complete_within_all_declared_horizons` | continue if fingerprints and all other gates pass |
| either classification incomplete or any aligned selection incomplete | `incomplete_within_one_or_more_declared_horizons` | `not_executed` |
| either classification not evaluated or any selection refused | `not_evaluated` | `not_executed` |
| expected fingerprint omitted, not evaluated, or mismatched | completeness remains independently derived | `not_executed` |
| governing occurrence not aligned | completeness remains independently derived | `not_executed` |

The evidence summary never suppresses condition-level issues or lower statuses
carried through trace indices.

### 12.4 Conclusion

| All admission and evidence gates pass | Endpoint classifications | Execution | Conclusion |
|---|---|---|---|
| yes | matches / matches | `executed` | `bounded_evidence_supports_declared_endpoint_pattern` |
| yes | does-not-match / matches | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| yes | matches / does-not-match | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| yes | does-not-match / does-not-match | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| no | any | `not_executed` | `None` |

No conclusion is named `occurred`, `observed_transition`, `completed`, or an
equivalent physical-event term.

### 12.5 Reachability of every proposed status

Every non-fixed public literal is reachable through valid public inputs:
admitted/not-admitted use healthy declared versus valid absent/lifecycle
worlds; exact/different relations use coherent results from equal versus
different requests or memberships; ordered/equal/reversed use aware cutoffs;
present/absent use bound versus observation-absent candidates; every alignment,
selection, expected-fingerprint, coverage, and selected-occurrence role is an
accepted reachable lower result; all three aggregate completeness values arise
from complete, incomplete, and refused/not-evaluated lower cases; both
execution values and both conclusions arise from the table above.

The fixed source-time, cohort, and continuity literals each have one reachable
value in every result. `not_applicable` trace literals are reachable for a
condition without a bound observation. Endpoint `not_evaluated` is reachable
when the transition has no effective endpoint body. No public status is merely
defensive-unreachable. Contradictory lower shapes are rejected during nominal
reconstruction and therefore do not require invented public statuses.

## 13. Threat and failure model

| Threat or failure | Required behavior and claim boundary |
|---|---|
| forged Pydantic object, hidden extra, private cache, cycle, wrong union arm | reject through typed input error before derivation |
| boolean index, negative/out-of-range index, scalar subclass with hostile equality | reconstruct strict scalar and reject before comparison or access |
| lower result with stale derived values | lower nominal reconstruction rejects; TA publishes no working state |
| transition, state, context, subject, cutoff, or revision substitution | exact full-object joins fail and structured issues prevent execution |
| equal value/time/checksum/ID/locator substituted for occurrence | insufficient; full compatibility and full occurrence alignment required |
| missing, duplicate, extra, reordered, or substituted alignment | typed invalid exact collection; never best-effort matched |
| EA refusal or unavailable snapshot | lower status disclosed; TA does not execute |
| incomplete EA horizon or ST condition coverage | incompleteness retained; TA does not execute |
| snapshot and embedded fingerprint replaced together | structural validation alone can remain self-consistent; no authentication claimed |
| independently retained expected fingerprint remains original | lower mismatch is retained and TA does not execute |
| expected fingerprint replaced with snapshot | outside pure detection boundary; no independence claim is made |
| source data changes after EA's final fences | not detected by the historical snapshot; no currentness claim |
| current stores differ from historical carried material | result reconstruction remains unchanged; no stores are consulted |
| different receipt/source times or clock segments | disclosed independently; no cohort or cross-clock comparison |
| valid conflicting declarations | no winner; declaration not admitted and TA does not execute |
| oversized graph or alignment fanout | reject at fixed pre-derivation bounds |
| exception contains path, credential, or raw payload | replace with fixed safe typed message |
| hash-seed, mapping insertion order, locale, timezone environment | no result-byte effect after UTC and canonical reconstruction |

The in-process caller and supplied retained fingerprint are trust-boundary
inputs. TA does not make them authoritative. Cryptographic signatures,
trusted clocks, external attestations, and source/sensor authority are out of
scope.

## 14. Historical replay and preservation consequences

A TA result is a pure function of its carried request. Its transition and state
results already carry complete selected model memberships; its alignments
already carry complete accepted EA selections and value-compatibility results.
Reconstruction never calls a current model, source, temporal, binding,
interpretation, or evidence store. Later filesystem growth, model append,
projection, or evidence capture cannot rewrite the prior result.

Historical replay remains membership-relative. A pin described as exact
current is exact current only in the carried revision. If a caller wants a
later view, it must compute new lower results and a new TA request; TA never
silently reselects. A retained result plus canonical bytes is not a durable
receipt or authenticated artifact.

Implementation must leave all accepted canonical IDs, record bytes,
memberships, revisions, evidence, temporal data, fixtures, artifacts, and
lower deterministic digests unchanged. In particular, the 36-record ledger,
its accepted revision, FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, the accepted
ledger aggregate, the 660,516-byte flow disclosure and its digest, both
accepted EA lower-material reproductions, and every pre-TA historical
membership remain exact.

Positive transition-assessment tests must use disposable synthetic public
worlds because the authoritative demo has no TRG, TRD, or TRW. No TA fixture,
demo record, result artifact, or ledger append is implied by a test world.

## 15. Adversarial executable acceptance matrix

Every attack row requires its stated valid twin. Rows are intended as
permanent executable tests, not prose-only review items.

| ID | Valid twin | Attack or case | Required result |
|---|---|---|---|
| T01 | healthy declared transition, both complete matches, complete aligned EA, matched expected fingerprints | unchanged input | executes with the exact positive bounded-support conclusion |
| T02 | T01 | from endpoint is a complete non-match | executes with exact negative bounded-support conclusion; no non-occurrence wording |
| T03 | T01 | to endpoint is a complete non-match | same negative conclusion and boundary |
| T04 | valid absent transition result | unregistered transition | structured not admitted/not executed |
| T05 | valid registered declaration | no exact-context declaration | `transition_not_declared` |
| T06 | valid declared lineage | same-root fork conflict | `transition_conflicted`; no winner |
| T07 | valid declared lineage | cross-root effective-body disagreement | conflict retained; no winner |
| T08 | valid declared lineage | all roots withdrawn | `transition_inactive` |
| T09 | T01 | from STD pin superseded | endpoint pin issue, not executed |
| T10 | T01 | to STD pin withdrawn | endpoint pin issue, not executed |
| T11 | T01 | endpoint state conflicted or inactive | exact lower pin alignment retained; not executed |
| T12 | T01 | request transition anchor differs from carried result | anchor mismatch, not executed |
| T13 | T01 | from classification uses wrong state | from-state and subject issues retained as applicable |
| T14 | T01 | to classification uses wrong state | to-state and subject issues retained as applicable |
| T15 | T01 | wrong but valid subject state | subject mismatch independent of state-anchor issue |
| T16 | T01 | transition result has different exact context | context mismatch, not executed |
| T17 | T01 | either classification has different exact context | endpoint and aggregate context disclosures disagree, not executed |
| T18 | T01 | transition result answers for another valid transition | exact anchor mismatch; no structural inference |
| T19 | T01 | equal aware cutoffs | relation `equal`, not executed |
| T20 | T01 | reversed aware cutoffs | relation `reversed`, not executed |
| T21 | T01 represented with UTC | equal instants represented with different timezone offsets | normalize once and produce byte-identical result |
| T22 | T01 | naive from or to cutoff | typed input error before lower dependency access |
| T23 | T01 | classification cutoff differs from explicit endpoint cutoff | endpoint cutoff issue, not executed |
| T24 | T01 | transition and classification carry different valid model revisions | revision mismatch, not executed |
| T25 | T01 | from classification refused/not executed | structured endpoint issue, no conclusion |
| T26 | T01 | to classification refused/not executed | structured endpoint issue, no conclusion |
| T27 | T01 | from classification has violated plus unknown conditions | incomplete classification issue; TA does not reuse ST's partial negative execution |
| T28 | T01 | to classification condition coverage incomplete | incompleteness retained; no conclusion |
| T29 | exact two-condition classification and two distinct alignments | omit one governing alignment | typed exact-collection input error |
| T30 | T29 | duplicate one alignment | typed input error |
| T31 | T29 | add unmatched valid alignment | typed input error |
| T32 | T29 | reverse alignment order | typed input error; no order-dependent remapping |
| T33 | T29 | substitute another valid compatibility/alignment | typed input error; equal scalar facts do not rescue join |
| T34 | one compatibility shared by two conditions and carried once | repeat it twice instead of reusing one index | duplicate input error; valid twin traces both conditions to one row |
| T35 | T01 | EA selection refused | selection refusal retained; not executed |
| T36 | T01 | expected fingerprint omitted | not-supplied relation and issue; not executed |
| T37 | T01 | expected fingerprint supplied but not evaluated after EA refusal | both independently applicable issues retained |
| T38 | T01 | expected fingerprint mismatched | mismatch retained; not executed |
| T39 | T01 | snapshot and embedded fingerprint replaced but original independent expected value retained | lower mismatch; not executed |
| T40 | T01 | snapshot, embedded fingerprint, and expected value all replaced coherently | may remain structurally coherent; limitation is explicit and no authentication is claimed |
| T41 | complete aligned selection | alignment is successful but EA horizon incomplete | aggregate incomplete, not executed |
| T42 | T01 | alignment status `not_aligned` for a governing compatibility | exact lower reason retained through trace; not executed |
| T43 | T01 | EA aligns a different candidate than classification's governing candidate | not admitted even if another occurrence aligns |
| T44 | T01 | same occurrence ID but changed occurrence content | lower content mismatch retained; not executed |
| T45 | two conditions with exact separate alignments | different receipt times | valid; discloses independent latest, not a cohort |
| T46 | T45 | different comparable-looking source times | valid disclosure only; does not alter selection or conclusion |
| T47 | T45 | non-comparable source clock segments | valid disclosure only; no cross-clock result or refusal invented |
| T48 | valid pre-horizon seed alignment | selected occurrence is the exact seed | role retained; complete/incomplete lower coverage still governs |
| T49 | T01 | source changes after the EA final fence | historical result unchanged; post-fence change is not claimed detected |
| T50 | ordinary reconstructed request | `model_construct`, `model_copy`, hidden extra, private cache, or cycle at each public boundary | typed input rejection before derivation |
| T51 | strict zero index | boolean in every input/result index or count position | reject; `True` is never index one |
| T52 | ordinary exact strings | hostile string subclass makes equality always true | reconstruct exact strings before comparison; reject malformed subclass |
| T53 | T01 | missing, duplicate, reordered, or stale result trace/issue index | `DeclaredTransitionAssessmentResult` reconstruction rejects |
| T54 | T01 | forged derived admission, relation, evidence summary, execution, issue, or conclusion | authoritative result reconstruction rejects |
| T55 | T01 | input mappings constructed in reverse key order | canonical result bytes unchanged |
| T56 | T01 | multiple `PYTHONHASHSEED` values | canonical result bytes unchanged |
| T57 | canonical alignment order | tuple permutation | consistently typed rejection in every seed/environment |
| T58 | T01 | filesystem, socket, connector, clock, environment, or write operations patched to fail | assessment and result validation still succeed without I/O |
| T59 | accepted pre-TA memberships | replay each historical membership before and after package addition | identical public lower results and revision IDs |
| T60 | accepted repository baseline | run preservation inventory | exact 36 records, accepted revision/hashes, FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0` |
| T61 | T01 | scan serialized result and public vocabulary | forbidden occurrence/completion/physical-event claims absent |
| T62 | T02/T03 | negative conclusion wording scan | no transition non-occurrence claim |

The implementation plan must map every row to an exact test and include
focused, affected, architecture/import-isolation, full repository, compilation,
dependency, base-only clean-checkout, all-extras clean-checkout, CAD/STEP/PDF,
deterministic reproduction, preservation, and whitespace gates. Loopback
sandbox setup failures and separately permitted reruns must be recorded by
column rather than blended.

## 16. Owner-gated implementation slices

No slice is authorized by this proposal. If the design is accepted, use these
small forward gates:

1. **Slice A — contracts and pure derivation.** Add only
   `backend.transition_assessment` with the exact Section 9 public surface,
   strict reconstruction, limits, joins, decision tables, canonical internal
   serializer, red-first contract tests, and pure assessment operation. Use
   disposable transition worlds; add no facade or authoritative fixture.
2. **Slice B — adversarial integrity and verification.** Add hostile boundary,
   fingerprint-replacement, collection-order, temporal-axis, no-I/O,
   determinism, wording, historical replay, import-isolation, and preservation
   tests for T01–T62; encode every discovered defect red before repair; run the
   complete working and dual-clean verification matrix. Production repair is
   confined to the new package.
3. **Optional demonstration — separate owner gate only.** A demo, committed
   result, transition record, ledger append, UI, or second consumer is not part
   of TA-001 Slices A or B and requires its own design and authorization.

A computation facade is omitted, not deferred by default. If later use proves
one necessary, it must be proposed separately with explicit per-condition
source, horizon, expected-fingerprint, dependency, and captured-view semantics.
It must not be smuggled into adversarial hardening.

## 17. Explicit exclusions and known limitations

TA-001 excludes lower-contract changes, model records, transition identities,
fixture appends, EA store revalidation, current-store lookup, source reread,
temporal queries, new evidence selection, source extraction, connectors,
networking, writes, persistence, caching, signatures, trusted time, UI,
planning, control, flow assessment, and authoritative demonstrations.

The assessment is limited by its inputs:

- endpoint classifications are independent sets of latest-per-condition views,
  not synchronized state snapshots;
- two ordered endpoint views do not prove an intervening path or event;
- complete means complete only within each exact carried EA horizon and fixed
  lower limits;
- source-native clocks may be unrelated and are never compared;
- the state vocabulary may be incomplete or non-exclusive;
- historical carried bytes are not authenticated by pure reconstruction;
- a coherently replaced snapshot and expected value may evade pure fingerprint
  comparison if the expected value was not actually retained independently;
- transition declaration currentness is relative to a carried model revision;
  and
- the result cannot say what happened between, before, or after the cutoffs.

If implementation reveals that a valid accepted lower result cannot expose the
exact join in Section 5, work must stop with a discrepancy report. It must not
read a private field, weaken equality, add a generic adapter, alter accepted
lower contracts, or redefine TA-001 silently.

## 18. Consequences for later accountable occurrence and flow assessment

TA-001 deliberately does not solve accountable transition occurrence. A later
occurrence milestone would need owner-approved facts absent here: an occurrence
identity and lifecycle, explicit interval/event semantics, trusted or clearly
qualified temporal authority, continuity/gap policy, trigger/guard/action
meaning where applicable, durable provenance and signing policy if
accountability requires them, and explicit treatment of late or corrected
evidence. It must not reinterpret a TA endpoint-pattern conclusion as a stored
occurrence.

Likewise, a later flow assessment requires its own explicit flow variables,
directions, quantities, units, temporal windows, evidence alignments,
participant semantics, and conservation/balance policy. Neither declared
transition endpoint support nor the existing FRG/FLD declaration implies
physical flow, transfer, causality, or mechanism. TA should remain a narrow
input that such later work may disclose, never an implicit proof.

The absence of a generic assessment identity in TA keeps those later designs
honest: if durable accountability is required, it must be designed and
owner-gated rather than inferred from canonical TA bytes.

## 19. Genuine owner questions

1. Approve or reject the strict rule that **every** governing observed
   condition must carry a matched independently supplied EA snapshot
   fingerprint before either positive or negative TA execution. The
   recommendation is approve; permitting `not_supplied` would materially
   weaken the stated evidence gate.
2. Approve or adjust the aggregate 134,217,728-byte canonical-request bound.
   The recommendation is approve as a conservative whole-assessment cap in
   addition to lower EA bounds; changing it later changes admission policy but
   no lower canonical meaning.
3. Confirm that TA-001 v1 ends after pure composition plus adversarial
   hardening, with no orchestration facade and no demonstration. The
   recommendation is confirm; either addition introduces separate caller and
   authority questions.

END OF TA-001 CODEX LEAD PROPOSAL
