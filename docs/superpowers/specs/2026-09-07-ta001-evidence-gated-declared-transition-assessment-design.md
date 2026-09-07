# TA-001 — Evidence-Gated Declared Transition Assessment

Status: corrected final synthesis for owner review. This document reconciles
the frozen Codex lead proposal, its independent challenger audit, and the
owner's final adjudication. It authorizes no implementation, fixture, ledger
change, demonstration, ADR, commit, or history operation.

## 1. Change log and complete audit reconciliation

This synthesis is self-contained. The lead proposal and audit remain frozen
evidence; neither is amended by this design.

| Item | Final resolution | Normative location |
|---|---|---|
| Required correction 1: unjustified 2,000,000-node graph limit | Replaced by exactly 200,000 nodes. The final limit triple is 134,217,728 canonical-request bytes, 200,000 reconstructed nodes, and depth 128. The direct precedents are 100,000 nodes/depth 128 in `backend/model_kernel/result_revalidation.py` and 200,000 nodes/depth 128 in `backend/state_classification/contracts.py`. No preliminary spike is required. | Sections 2 and 9 |
| Required correction 2: unresolved/incomplete limit question | Removed. The owner approved the complete limit triple as one admission-policy decision. Any future change to any member requires a separately reviewed contract change. | Sections 9 and 23 |
| Observation 1: inherited six-field wording over seven-field scope | Preserved the accepted lower literals `six_field_locator_equal` and `six_field_locator_different`. TA states explicitly that `Ds004OperationalEvidenceScope` has seven fields including `endpoint_id`; the accepted six-field relation and independent endpoint closure together cover their distinct duties. No lower rename occurs. | Sections 6 and 8 |
| Observation 2: semantic/value indices are numerically equal in accepted worlds | Retained both coordinates as distinct provenance fields. The design derives each from its own public contract and never describes the index domains as intrinsically identical. | Sections 6 and 11 |
| Observation 3: no dedicated divergent-index attack | Added T63 without renumbering T01–T62. A forged divergence between `semantic_candidate_index` and `value_candidate_index` must fail authoritative result reconstruction. | Section 18 |
| Observation 4: fingerprint rule was owner-selectable | Resolved to the strict gate for positive and negative execution: every governing observation requires a supplied expected fingerprint and relation `matched`. | Section 8 |
| Observation 5: disposable positive worlds | Repeated as a mandatory condition in every implementation gate and in the permanent no-demonstration decision. Positive worlds may not become committed fixtures, records, memberships, or artifacts. | Sections 17 and 19 |
| Observation 6: reachability needed executable exhaustion | Added a mandatory exhaustive public-literal and 22-issue-code reachability test, including fixed single-value disclosures and `not_applicable` arms. | Sections 15 and 18 |

The audit found zero blocking contradictions. Both required corrections and all
six observations are incorporated. The owner also fixed the strict fingerprint
gate and the absence of a facade or demonstration. There are zero unresolved
owner questions.

## 2. Verified baseline and accepted decision dependencies

The synthesis was produced on branch `main` with `HEAD`, `main`, and
`origin/main` all equal to
`948374eec3cd49596fe19548a58a4fb10760a433`, subject
`docs: reconcile root README through EA-001`. The only pre-existing untracked
design inputs were the frozen proposal and audit.

The authoritative demo model loaded as exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW were exactly `1/1/0`; TRG/TRD/TRW were exactly `0/0/0`.
EA-001 was complete and owner accepted, and no successor implementation was
approved.

The frozen inputs were verified before synthesis:

- lead proposal: 877 lines, 49,616 bytes, SHA-256
  `a8130d3146af7c159d739b6c63b9e0c398fd0bf4f1fa363d99559c476a0cf146`;
- challenger audit: 469 lines, 28,641 bytes, SHA-256
  `b87d607d7ab17bf59bff10678175443303dc81c41726923f40d29034032fdad1`;
  verdict `approve_with_corrections`, zero blocking findings, two required
  corrections, and six non-blocking observations.

The hostile-graph limits use actual accepted code precedents:

- `backend.model_kernel.result_revalidation` fixes result graphs at 100,000
  container nodes and depth 128; and
- `backend.state_classification.contracts` fixes serialized shapes at 200,000
  nodes and depth 128.

The 200,000-node value is therefore the largest accepted result-graph
precedent, while depth 128 has two direct precedents. The earlier 2,000,000
proposal value has no authority and is superseded by this synthesis.

TA-001 depends on the accepted meanings of ST-002 transition declaration,
ST-001 state classification, the CN/ES/VS carried-result chain, EA-001 bounded
selection and fingerprint validation, and the sole existing evidence-
alignment consumer. It changes none of those meanings.

## 3. Objective and exact non-objectives

TA-001 answers one bounded question: do exact accepted carried results support
the declared from-state at an explicit earlier cutoff and the declared
to-state at an explicit later cutoff under the fixed v1 policies and complete
governing operational evidence?

The strongest positive answer is
`bounded_evidence_supports_declared_endpoint_pattern`. The strongest negative
answer is
`bounded_evidence_does_not_support_declared_endpoint_pattern`. Both are about
two separately classified endpoint views at exact stated cutoffs. Neither is a
claim about what physically happened between those cutoffs.

TA-001 does not establish or infer:

- transition occurrence or non-occurrence;
- an occurrence identity, event history, start or end instant, interval,
  duration, continuity, dwell, debounce, hysteresis, or path;
- trigger, guard, enablement, executability, action, effect, command, or
  control;
- causality, influence, mechanism, diagnosis, fault, safety, health,
  correctness, or recommendation;
- exclusivity or completeness of the state vocabulary;
- flow, transfer, conservation, or balance;
- source, sensor, signer, or clock authority, trusted time, authentication, or
  physical truth; or
- a generic immutable assessment identity.

It never uses authority, timestamps, record IDs, append order, filenames, or
lexical order to choose a winner among conflicting declarations.

## 4. Final recommendation and prerequisite decision

TA-001 is viable without a runtime prerequisite. The final recommendation is
a pure, read-only leaf composition over already-computed public results.
Complete exact evidence alignment and a matched independently supplied
snapshot fingerprint are mandatory for every governing observed condition
before either positive or negative execution.

No new source, temporal, model, state, constraint, semantic, observation, EA,
or alignment contract is needed. TA consumes the existing nominal
`OperationalEvidenceAlignmentResult`; it does not make
`backend.evidence_alignment` a registry or add a second consumer.

TA-001 v1 ends after pure composition and adversarial hardening. It has no
orchestration facade and no demonstration. Per-condition source selection,
horizon construction, expected-fingerprint retention, and lower query
coordination remain caller responsibilities outside the package. This avoids
inventing a cross-store transaction or a false global snapshot.

No speculative preimplementation spike is required. Task 0 becomes active
only if implementation discovers a concrete discrepancy in enforcing the
accepted exact limits without unsafe allocation or repeated reconstruction.
Such a discrepancy must be documented and owner-gated rather than answered by
silently changing the contract.

## 5. Package ownership and import direction

The sole proposed package is `backend.transition_assessment`. It owns only
strict contracts, pure reconstruction, pure derivation, and the one public
assessment function.

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

Arrows point from consumer to dependency. TA imports only the accepted public
roots of `backend.model_kernel`, `backend.state_classification`, and
`backend.evidence_alignment`, plus Pydantic and the standard library. It may
not import private store or derivation modules from those packages.

No existing package may import TA. TA owns no model or evidence ledger, store,
cache, database, persistent receipt, identity, anchor, minter, signature,
connector, temporal projection, source reader, filesystem path, network
client, clock, environment discovery, writer, UI, planner, or controller.
Root import is pure and exposes only the exact Section 11 `__all__`.

## 6. Exact carried-result join proof and distinct index domains

One request carries one `TransitionDeclarationResult`, one from
`StateClassificationResult`, one to `StateClassificationResult`, and one
exact bounded tuple of distinct `OperationalEvidenceAlignmentResult` values.
It also carries explicit transition-anchor, context, and cutoff echoes so a
substituted lower result cannot redefine the question.

For each state condition, TA derives the join through this exact chain:

1. `StateClassificationConditionResult.constraint_evaluation_index` selects
   one `ConstraintEvaluationResult`. The condition's `candidate_index` selects
   one `CandidateConstraintEvaluation` in that CN result.
2. The selected CN candidate explicitly names its own
   `semantic_candidate_index`. TA derives and records this semantic coordinate
   from that field; it does not assume it is an index into another domain.
3. The semantic result validator requires its candidates tuple to remain
   position-parallel with its carried
   `VariableValueCompatibilityResult.candidates` and requires each semantic
   candidate to carry the same-position value candidate verbatim. TA derives
   a separate `value_candidate_index` from that enforced positional
   correspondence. The two coordinates are distinct provenance facts even
   though accepted valid worlds make their integer values equal.
4. TA matches the complete exact
   `VariableValueCompatibilityResult` to
   `OperationalEvidenceAlignmentResult.request.compatibility`. It does not
   match a scalar summary or candidate alone.
5. Only after full compatibility equality does TA compare the alignment's
   `aligned_candidate_index`, which indexes that alignment request's exact
   compatibility object, with the explicitly derived value-candidate
   coordinate.
6. For a bound value candidate, the full public `TemporalOccurrence` is the
   classification's governing selected observation. The accepted alignment
   binds that occurrence to its EA selection, snapshot, cutoff, scope
   relation, endpoint closure, coverage, validation, and content fingerprint.
   For an unbound candidate, no governing observation exists and no alignment
   is permitted.

No equality of values, timestamps, checksums, occurrence IDs, model record
IDs, or locators substitutes for this chain. A forged difference between the
semantic and value coordinates rejects authoritative result reconstruction;
TA does not choose one coordinate as the winner.

The exact alignment collection has one entry per distinct required complete
value-compatibility result. Equal compatibilities used by multiple conditions
are carried once and cited by multiple trace indices. No alignment is carried
for an observation-absent condition. No unmatched entry is allowed. Alignment
order is the first governing coordinate: from before to, then condition index.
Missing, duplicate, extra, reordered, or substituted collections are malformed
requests and do not trigger best-effort matching.

## 7. Temporal policy, axes, and non-cohort disclosure

The fixed policy is
`declared_endpoint_pattern_at_ordered_cutoffs`, version
`ta001.endpoint_pattern.v1`. The normalized UTC from cutoff must be strictly
earlier than the normalized UTC to cutoff for execution. Equal or reversed
aware cutoffs produce structured non-execution; naive datetimes or hostile
datetime subclasses are malformed.

Each endpoint preserves ST-001's independent latest-at-or-before selection per
condition. Within every carried EA selection:

- `received_at` governs occurrence membership and latest selection;
- source-effective wall time governs acquisition-attempt horizon coverage;
- source-native time and clock segment are disclosure only; and
- observation age is disclosure only.

TA never collapses those axes, performs no cross-clock comparison, and does not
use source-native time for selection or coverage. Different conditions may
have different receipt times, source times, clock segments, sources, locators,
pre-horizon seeds, and declared horizons.

Every result therefore states
`independent_latest_per_condition_not_a_temporal_cohort` and continuity
`not_assessed`. It establishes no simultaneity, synchronization, acquisition
cohort, persistence, dwell, interval, or path. Two ordered endpoint cutoffs do
not prove traversal of the declared transition.

## 8. Exact evidence and fingerprint execution gate

Every condition with a bound governing observation must have its exact
alignment entry. That condition passes the evidence gate only if all of these
facts hold simultaneously:

1. the complete carried compatibility equals the classification's nested
   complete `VariableValueCompatibilityResult`;
2. the alignment's candidate index equals the separately derived value-
   candidate coordinate after the full-object match;
3. alignment status is `aligned_with_complete_evidence`;
4. EA selection status is `complete_within_declared_horizon`;
5. EA evidence coverage is `complete_within_declared_horizon`;
6. an independently supplied expected snapshot fingerprint is present;
7. expected-fingerprint relation is `matched`; and
8. carried snapshot validation is structurally self-consistent with matched
   embedded and expected fingerprints.

This rule governs positive and negative TA execution identically. A missing,
not-evaluated, or mismatched expected fingerprint prevents execution but does
not rewrite evidence completeness. An
`aligned_with_incomplete_evidence` lower result remains a successful exact
occurrence alignment and is disclosed as incomplete; it cannot satisfy the TA
gate.

The accepted inherited `scope_relation` vocabulary remains exactly
`six_field_locator_equal`, `six_field_locator_different`, and
`not_evaluated`. The underlying `Ds004OperationalEvidenceScope` carries seven
fields: `source_id`, `adapter_id`, `endpoint_id`, `item_key`,
`subject_identifier`, `extraction_route`, and `json_pointer`. The six-field
locator relation compares every field except `endpoint_id`; the separately
derived `endpoint_closure == bound_by_snapshot_closure` binds the selected
occurrence's attempt to the exact scoped endpoint. TA requires the accepted
alignment result and changes neither lower literal nor lower scope.

A snapshot and embedded fingerprint can be coherently replaced while remaining
structurally self-consistent. An independently retained original expected
fingerprint detects that replacement. If the snapshot, embedded fingerprint,
and claimed expected value are all replaced together, pure validation may
remain coherent. TA makes no signature, authentication, authority,
trusted-time, or truth claim.

## 9. Exact limits and preflight enforcement order

The final normative limits are one indivisible admission-policy decision:

| Limit | Exact value | Basis |
|---|---:|---|
| `maximum_canonical_request_bytes` | 134,217,728 | accepted whole-request policy; twice EA's single-snapshot 64 MiB retained-metadata bound |
| `maximum_reconstructed_nodes` | 200,000 | largest accepted result-graph precedent in state classification |
| `maximum_nesting_depth` | 128 | accepted state-classification and model-result precedent |

The structural cardinalities remain exactly two endpoint classifications, at
most 64 conditions per endpoint, at most 128 condition traces, and at most 128
distinct alignments. Any future change to bytes, nodes, or depth requires a
separately reviewed public contract change.

The byte bound alone cannot prevent unsafe allocation before serialization.
Every public TA boundary must enforce this order:

1. Admit only the expected outer ordinary mapping/model shape without calling
   `model_dump`, Pydantic validation, lower validation, equality, hashing, or
   canonical serialization.
2. Traverse the supplied graph iteratively. Reject cycles by active-path
   identity, unexpected private or hidden model state, unsupported containers,
   non-string mapping keys, and unexpected union arms. Enforce depth before
   descending.
3. During that same traversal, enforce strict scalar kinds, reject hostile
   subclasses and boolean indices/counts, apply known container cardinalities,
   count the expanded serialization-tree occurrences, and stop at node
   200,001. A mapping or sequence occurrence and each scalar value are nodes;
   mapping keys are validated names and are not separately counted. Root depth
   is zero and depth 129 rejects.
4. Treat a shared acyclic subgraph as repeated serialized content: count it
   once per reference. Do not use global de-duplication to turn repeated
   content into a smaller canonical request. Track only the active path for
   cycle rejection and keep traversal stack memory bounded by depth rather
   than container length.
5. Count scalar and structural UTF-8 JSON contributions incrementally with a
   bounded encoder/counter so one huge string, byte value, mapping, or sequence
   can refuse before a complete plain copy or canonical byte string is
   allocated. Stop at byte 134,217,729.
6. Only after node, depth, scalar, container, and preliminary byte admission,
   create the ordinary content graph. Canonically encode through a streaming
   sink, enforce the exact canonical byte count, and retain bytes only after
   the complete size is known to be within the limit.
7. Only then invoke nominal Pydantic reconstruction of the policy, context,
   transition, classifications, and alignments. Publish validated working
   state only after every nested reconstruction succeeds.
8. Only after full reconstruction perform indices, equality joins,
   fingerprint relations, issue derivation, and conclusion derivation.

The 200,000-node budget is aggregate across the complete request and is not
reset per endpoint, alignment, or lower result. Result reconstruction applies
the same aggregate budget to its carried request once, then validates the
compact derived fields against their fixed cardinalities; it must not multiply
the request budget by reconstructing the same subtree through multiple TA
passes. Lower contracts may perform their own accepted validation, but TA may
not duplicate lower reconstruction for convenience.

Exact-limit twins, limit+1 attacks, cycles, shared-subgraph expansion,
repeated-reconstruction instrumentation, and huge scalar/container attacks are
mandatory. Spies must prove limit rejection occurs before lower Pydantic
validation, lower equality, fingerprint work, or derived-field access.

## 10. Transition declaration and endpoint admission

Declaration admission requires all of the following:

- the transition result answers for the request's exact transition anchor and
  exact context;
- conclusion is `declared`, lineage summary is `healthy`, and exactly one
  effective-body group exists;
- the group's from and to pins each disclose `exact_current` within the carried
  membership;
- the classifications answer for the exact ordered endpoint state anchors and
  request context;
- transition and classifications carry equal complete `ModelRevision`
  objects, not merely equal revision ID strings;
- both endpoint state registrations have the transition registration's exact
  subject entity; and
- classification cutoffs equal the corresponding explicit request cutoffs.

`exact_current` is membership-relative. TA performs no current ledger read and
does not call a historical pin globally current. Independent healthy roots may
corroborate one effective body. A same-root fork, cross-root body disagreement,
inactive lineage, undeclared transition, or unregistered transition is
structured non-admission; no winner is selected.

Both endpoint classifications must have `condition_coverage == complete` and
`execution == executed`. A state classification that executed a negative
result because one condition violated while another remained unknown is still
incomplete for TA and cannot produce a TA conclusion.

Anchor, lifecycle, context, revision, endpoint state, subject, pin, cutoff,
classification execution, and classification coverage remain separate
disclosures and issues. All independently applicable issues are retained in
normative order.

## 11. Exact public contracts, literals, errors, and exports

All public models are frozen Pydantic models with `extra="forbid"` and
`revalidate_instances="always"`. All indices are `StrictInt`, non-boolean,
nonnegative, and range-checked. All strings must be ordinary strings, not
subclasses. Literal order is normative.

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

There are exactly 22 issue-code literals. Their displayed order is their
normative precedence.

Exact model field order and types are:

```python
_UtcDatetime = Annotated[
    AwareDatetime,
    AfterValidator(lambda value: value.astimezone(UTC)),
]
_StrictNonnegativeInt = Annotated[StrictInt, Field(ge=0)]
_TransitionAnchorId = Annotated[
    StrictStr,
    StringConstraints(pattern=r"^trn_[0-9a-f]{32}$"),
]

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
    maximum_reconstructed_nodes: Literal[200000]
    maximum_nesting_depth: Literal[128]

class DeclaredTransitionAssessmentRequest:
    schema_version: Literal["1"]
    transition_anchor_id: _TransitionAnchorId
    context: AssertionContext
    from_as_of: _UtcDatetime
    to_as_of: _UtcDatetime
    policy: TransitionAssessmentPolicy
    transition: TransitionDeclarationResult
    from_classification: StateClassificationResult
    to_classification: StateClassificationResult
    evidence_alignments: tuple[OperationalEvidenceAlignmentResult, ...]

class TransitionAssessmentIssue:
    code: TransitionAssessmentIssueCode
    endpoint_role: TransitionAssessmentEndpointRole | None
    condition_index: _StrictNonnegativeInt | None
    evidence_alignment_index: _StrictNonnegativeInt | None

class TransitionAssessmentConditionTrace:
    trace_index: _StrictNonnegativeInt
    endpoint_role: TransitionAssessmentEndpointRole
    condition_index: _StrictNonnegativeInt
    constraint_evaluation_index: _StrictNonnegativeInt
    semantic_candidate_index: _StrictNonnegativeInt | None
    value_candidate_index: _StrictNonnegativeInt | None
    observation_presence: TransitionAssessmentObservationPresence
    evidence_alignment_index: _StrictNonnegativeInt | None
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
    condition_trace_indices: tuple[_StrictNonnegativeInt, ...]

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
`TransitionAssessmentInputError` is its only v1 subclass. Its constructor
accepts exactly `error_code: TransitionAssessmentInputErrorCode` and
`message: StrictStr`; instances expose exactly `error_code` and `message`.
Messages are fixed safe ordinary text of 1–300 characters with no path,
credential, payload, secret, or raw lower exception. Every malformed request,
hostile graph, invalid exact alignment collection, or limit violation maps to
`TRANSITION_ASSESSMENT_INPUT_INVALID`. Valid lower lifecycle and relational
statuses return structured results.

The sole public operation is:

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

No alias, alternate operation, facade, canonical-byte export, lower type,
registry, or convenience name is public.

## 12. Authoritative full-instance reconstruction

The operation runs the Section 9 bounded preflight before any serialization,
lower validation, or equality. It then reconstructs request scalars and fixed
policy, transition result, from classification, to classification, and every
alignment through their exact nominal public models. Serialized shape before
and after reconstruction must agree except for documented UTC normalization.
No lower object is published to working state until all reconstruction
succeeds.

The boundary does not trust `isinstance`, caller equality, `model_construct`,
`model_copy`, hidden extras, unexpected Pydantic private state, cached
properties, or caller serialization. It rejects cycles, unsupported
containers, non-string mapping keys, scalar subclasses, wrong union arms,
booleans in every index/count position, and missing/duplicate/extra/reordered
content. Exact permitted lower private material bindings are checked by their
nominal lower reconstruction and may not point to substituted material.

After full reconstruction, request validation derives the distinct required
compatibility set and exact alignment order. Every trace index is checked
before access. It separately derives semantic and value coordinates and
requires the lower-enforced correspondence; neither is copied from a supplied
trace.

`DeclaredTransitionAssessmentResult.model_validate(...)` reconstructs its
complete nested request once and recomputes every limit, admission, relation,
endpoint disclosure, condition trace, evidence summary, issue, execution, and
conclusion. Any stale, missing, duplicate, extra, reordered, substituted,
boolean, out-of-range, divergent semantic/value coordinate, or forged derived
field rejects. Result validation performs no filesystem, store, database,
network, connector, environment, clock, or write operation.

Complete lower material is carried once in the request. Endpoint and trace rows
carry only strict indices and derived scalar disclosures. The result repeats
neither a lower result nor raw payload bytes. Validation proves internal
carried-content coherence, not current store membership or authentication of
absent source bytes.

## 13. Deterministic ordering and internal canonical test bytes

Normative order is:

- endpoints: from, then to;
- conditions: accepted ST order within each endpoint;
- traces: all from conditions by ascending condition index, then all to
  conditions by ascending condition index;
- distinct alignments: the first trace that governs each distinct complete
  compatibility, with later traces reusing its strict index;
- endpoint trace indices: ascending global trace index;
- issues: Section 11 issue-code order, then endpoint role with `None` first,
  then condition index, then evidence-alignment index, with `None` before zero;
- lower tuples: their accepted lower order, never resorted by TA; and
- no ordering rule ranks or selects a declaration winner.

Canonical TA bytes are private test evidence, not a public identity. They are
the reconstructed result's JSON-mode field graph encoded as UTF-8 JSON with
mapping keys sorted by Unicode code point, no insignificant whitespace,
`ensure_ascii=False`, `allow_nan=False`, arrays in normative order, base-ten
integers, and aware datetimes normalized to UTC using `Z` and the shortest
exact fractional-second form. Floats and non-finite numbers are forbidden. The
bytes have no final newline.

Construction order, mapping insertion order, locale, system timezone, and
`PYTHONHASHSEED` do not change canonical bytes. A permutation of the normative
alignment tuple rejects consistently rather than being silently remapped.
TA creates no result fingerprint, record ID, anchor, signature, receipt,
ledger row, or persistent artifact.

## 14. Complete refusal, disclosure, and conclusion tables

### 14.1 Structural admission

| Input condition | Outcome |
|---|---|
| malformed anchor, policy, context, datetime, lower result, scalar, union arm, or graph | typed input error; no result |
| node/depth/container/scalar/byte/cardinality limit exceeded | typed input error before lower validation or equality; no partial result |
| missing, duplicate, extra, reordered, or substituted alignment collection | typed input error; no guessed join |
| valid lower lifecycle or relation | reconstruct all inputs and return structured result |

### 14.2 Declaration and endpoint admission

| Carried facts | Admission | Execution |
|---|---|---|
| exact anchor/context/revision, declared healthy one body, exact-current pins, exact states/subjects/cutoffs | `admitted` | continue to classification/evidence gates |
| unregistered, undeclared, conflicted, or inactive transition | `not_admitted` | `not_executed`; lifecycle issue retained |
| stale pin or wrong anchor/state/subject/context/revision/cutoff | `not_admitted` | `not_executed`; all applicable issues retained |
| equal or reversed request cutoffs | declaration admission remains independently derived | `not_executed`; cutoff relation and issue retained |

### 14.3 Classification and evidence completeness

| Facts | `evidence_completeness` | Execution effect |
|---|---|---|
| both classifications complete; every selection/alignment complete | `complete_within_all_declared_horizons` | continue if fingerprints and all other gates pass |
| either classification incomplete or any aligned selection incomplete | `incomplete_within_one_or_more_declared_horizons` | `not_executed` |
| either classification not evaluated or any selection refused | `not_evaluated` | `not_executed` |
| expected fingerprint omitted, not evaluated, or mismatched | completeness is unchanged and independently disclosed | `not_executed` |
| governing occurrence not aligned | completeness is unchanged and independently disclosed | `not_executed` |

An aggregate completeness value never suppresses lower statuses or trace-level
issues.

### 14.4 Conclusion

| Every admission, classification, evidence, and fingerprint gate passes | Endpoint matches | Execution | Conclusion |
|---|---|---|---|
| yes | matches / matches | `executed` | `bounded_evidence_supports_declared_endpoint_pattern` |
| yes | does-not-match / matches | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| yes | matches / does-not-match | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| yes | does-not-match / does-not-match | `executed` | `bounded_evidence_does_not_support_declared_endpoint_pattern` |
| no | any | `not_executed` | `None` |

The negative conclusion means only that the bounded evidence fails to support
the declared endpoint pattern. It is not a transition non-occurrence finding.

### 14.5 Fingerprint relation

| Lower relation | Completeness effect | Execution effect |
|---|---|---|
| `matched` with independently supplied expected fingerprint | none | passes this gate |
| `not_supplied` | none | corresponding issue; not executed |
| `not_evaluated` | none | corresponding issue; not executed |
| `mismatched` | none | corresponding issue; not executed |
| `not_applicable` on observation-absent trace | none | no governing-observation fingerprint gate exists for that trace |

## 15. Public status and issue reachability

Implementation must enumerate every public literal from `typing.get_args` in
normative order and prove each arm reachable through a valid public input, or
prove a fixed one-value disclosure present in every valid result. It must also
enumerate all 22 issue codes, construct a valid public lower world for each,
and prove exact issue order and multi-issue retention. No status may be left as
an unexplained defensive arm.

Reachability is:

- `not_admitted`/`admitted`: valid absent or lifecycle transition versus valid
  declared healthy exact-pin transition;
- exact/different/not-evaluated endpoint and subject relations: exact endpoint,
  valid substituted endpoint, and transition with no effective body;
- ordered/equal/reversed cutoff relations: three aware cutoff pairs;
- present/absent observation: bound versus unbound value candidate;
- all lower alignment, selection, coverage, expected-fingerprint, and selected-
  occurrence roles: their accepted lower valid worlds;
- aggregate completeness: complete, incomplete, and refused/not-evaluated
  lower worlds;
- execution: all gates pass versus any structured gate failure;
- both conclusions: complete match/match versus a complete endpoint
  non-match;
- `not_applicable`: an observation-absent trace; and
- fixed source-time, cohort, and continuity literals: present in every valid
  result.

Every issue code is independently reachable. Codes that may co-occur—such as
selection refusal with fingerprint not evaluated, or wrong state with wrong
subject—must be retained together in Section 11 order. Transition lifecycle
codes are mutually exclusive because the accepted lower conclusion is a
single literal; the test still reaches each in a separate valid lower world.

Contradictory lower shapes, forged index-domain divergence, and invalid exact
alignment collections are typed malformed input rather than invented result
statuses.

## 16. Threat and failure model

| Threat or failure | Required behavior and proof boundary |
|---|---|
| huge/cyclic/deep/shared raw graph | iterative aggregate preflight; active-path cycle refusal; shared content counted per occurrence; reject before serialization or lower work |
| huge scalar, mapping, or sequence | bounded incremental scalar/structure counting; no complete copy or byte string before admission |
| hostile Pydantic object, hidden extra, private cache, wrong union arm | typed rejection before working state is published |
| boolean, negative, or out-of-range index; scalar subclass with hostile equality | strict reconstruction before index access or comparison |
| rejected lower object | cannot support a trace, fingerprint relation, admission, or conclusion |
| stale lower derived value | exact nominal lower reconstruction rejects |
| transition/state/context/subject/cutoff/revision substitution | exact object and scalar joins disclose issues and prevent execution |
| semantic/value trace-coordinate divergence | authoritative result rederivation rejects; neither coordinate wins |
| equal value/time/checksum/ID/locator substitution | insufficient; full compatibility and occurrence alignment remain mandatory |
| missing/duplicate/extra/reordered/substituted alignment | typed exact-collection error; no best effort |
| incomplete alignment or state coverage | incompleteness retained; not executed |
| expected fingerprint absent/not evaluated/mismatched | completeness unchanged; not executed |
| snapshot plus embedded fingerprint replaced | may remain structurally self-consistent; no authentication claimed |
| original independent expected fingerprint retained | mismatch prevents execution |
| expected fingerprint replaced with snapshot | outside pure detection boundary; no independence claim |
| source changes after EA final fences | historical TA unchanged; post-fence detection not claimed |
| current stores differ from carried historical material | no store read; no currentness claim |
| different receipt/source times or clock segments | independent disclosures; no cohort or cross-clock inference |
| valid declaration conflict | no winner; not admitted |
| exception contains path, credential, secret, or payload | fixed safe typed message replaces raw failure |
| hash seed, mapping construction, locale, timezone environment | canonical bytes unchanged |

The caller and the supplied expected fingerprint are inputs at the in-process
trust boundary. TA records their relation but does not make them authoritative.

## 17. Historical replay and preservation consequences

A result is a pure function of its carried request. The transition and state
results already carry complete selected model memberships; alignments already
carry accepted EA selections and complete value-compatibility results. Result
reconstruction never consults current model, source, temporal, binding,
interpretation, or evidence stores.

Later ledger appends, evidence capture, projection, or filesystem growth do not
rewrite a prior result. A caller seeking a later view must compute new lower
results and submit a new request. `exact_current` remains relative to the
carried model revision. Canonical bytes are neither a durable receipt nor an
authenticated artifact.

TA implementation must preserve every accepted canonical ID, record byte,
membership, revision, fixture, evidence file, temporal database, artifact, and
lower deterministic digest. Mandatory inventory includes:

- exactly 36 model records;
- revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`;
- ledger aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- the 660,516-byte flow disclosure at SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- both accepted EA lower-material reproductions; and
- every pre-TA historical membership and public lower contract.

Every positive test world is disposable. It may exist only in bounded test
temporary storage and must be destroyed after the test. It may not be
committed as a fixture, model record, membership, evidence artifact, TA result,
or demonstration.

## 18. Corrected adversarial executable acceptance matrix

T01–T62 retain their frozen meanings and numbering. T63 is the audit-requested
distinct-index attack. T64–T72 add the owner-required exact-limit and preflight
proofs without renumbering ambiguity. Every attack has the stated valid twin.

| ID | Valid twin | Attack or case | Required result |
|---|---|---|---|
| T01 | healthy declared transition, complete endpoint matches, complete alignments, matched expected fingerprints | unchanged input | exact positive bounded-support conclusion |
| T02 | T01 | from endpoint is a complete non-match | exact negative bounded-support conclusion; no non-occurrence wording |
| T03 | T01 | to endpoint is a complete non-match | exact negative conclusion and boundary |
| T04 | valid absent transition result | unregistered transition | structured not admitted/not executed |
| T05 | valid registered transition | no exact-context declaration | `transition_not_declared` |
| T06 | valid declared lineage | same-root fork | `transition_conflicted`; no winner |
| T07 | valid declared lineage | cross-root body disagreement | conflict retained; no winner |
| T08 | valid declared lineage | all roots withdrawn | `transition_inactive` |
| T09 | T01 | from STD pin superseded | pin issue; not executed |
| T10 | T01 | to STD pin withdrawn | pin issue; not executed |
| T11 | T01 | endpoint state conflicted/inactive | exact lower alignment retained; not executed |
| T12 | T01 | request anchor differs from transition result | anchor issue; not executed |
| T13 | T01 | wrong from state | from-state and independently applicable subject issues |
| T14 | T01 | wrong to state | to-state and independently applicable subject issues |
| T15 | T01 | wrong valid subject state | subject issue remains distinct from state-anchor issue |
| T16 | T01 | transition result has another exact context | context issue; not executed |
| T17 | T01 | either classification has another exact context | endpoint/global context disclosure; not executed |
| T18 | T01 | another valid transition result is substituted | exact anchor issue; no structural inference |
| T19 | T01 | equal aware cutoffs | `equal`; not executed |
| T20 | T01 | reversed aware cutoffs | `reversed`; not executed |
| T21 | T01 in UTC | equal instants expressed using other aware offsets | normalize once; byte-identical result |
| T22 | T01 | naive cutoff or hostile datetime subclass | typed error before lower access |
| T23 | T01 | classification cutoff differs from explicit cutoff | endpoint cutoff issue; not executed |
| T24 | T01 | valid differing model revisions | revision issue; not executed |
| T25 | T01 | from classification not executed | endpoint issue; no conclusion |
| T26 | T01 | to classification not executed | endpoint issue; no conclusion |
| T27 | T01 | from classification has violation plus unknown sibling | incomplete classification; TA does not reuse partial ST negative |
| T28 | T01 | to classification incomplete | incomplete; no conclusion |
| T29 | exact two-condition/two-alignment request | omit governing alignment | typed exact-collection error |
| T30 | T29 | duplicate alignment | typed error |
| T31 | T29 | add unmatched alignment | typed error |
| T32 | T29 | reverse alignment order | typed error; no remap |
| T33 | T29 | substitute valid foreign compatibility/alignment | typed error; scalar equality cannot rescue |
| T34 | shared compatibility carried once | repeat it instead of reusing index | typed duplicate error; twin has two traces to one row |
| T35 | T01 | EA selection refused | refusal retained; not executed |
| T36 | T01 | expected fingerprint omitted | not-supplied issue; completeness unchanged; not executed |
| T37 | T01 | fingerprint supplied but not evaluated after EA refusal | both issues retained in order |
| T38 | T01 | expected fingerprint mismatched | mismatch; not executed |
| T39 | T01 | snapshot/embedded fingerprint replaced, original independent expectation retained | mismatch; not executed |
| T40 | T01 | snapshot, embedded fingerprint, and expectation replaced coherently | may remain coherent; no authentication claim |
| T41 | complete aligned twin | alignment succeeds with incomplete EA horizon | incomplete; not executed |
| T42 | T01 | governing compatibility has `not_aligned` result | exact lower reason trace; not executed |
| T43 | T01 | alignment identifies another candidate | fail gate despite other aligned occurrence |
| T44 | T01 | same occurrence ID with altered content | lower content mismatch; not executed |
| T45 | two-condition exact alignments | different receipt times | valid independent-latest result; not a cohort |
| T46 | T45 | different comparable-looking source times | disclosure only; no result effect |
| T47 | T45 | non-comparable clock segments | disclosure only; no invented cross-clock refusal |
| T48 | exact pre-horizon seed alignment | governing occurrence is seed | role retained; lower coverage governs |
| T49 | T01 | source changes after EA final fence | historical result unchanged; later change not detected claim absent |
| T50 | ordinary reconstructed request | `model_construct`, `model_copy`, hidden extra/private cache, or cycle | typed rejection before derivation |
| T51 | strict integer zero | boolean at every input/result index or count | reject; boolean is never an index |
| T52 | ordinary exact strings | hostile string subclass makes equality true | strict scalar rejection before comparison |
| T53 | T01 | missing/duplicate/reordered/stale result trace or issue index | result reconstruction rejects |
| T54 | T01 | forged admission/relation/completeness/execution/issue/conclusion | authoritative reconstruction rejects |
| T55 | T01 | reverse mapping-key construction order | canonical bytes unchanged |
| T56 | T01 | multiple `PYTHONHASHSEED` values | canonical bytes unchanged |
| T57 | canonical alignment tuple | tuple permutation | consistently typed rejection |
| T58 | T01 | filesystem/socket/connector/clock/environment/write hooks fail | assessment and validation remain pure and pass |
| T59 | accepted historical memberships | replay before/after TA package | identical lower results and revisions |
| T60 | accepted baseline | preservation inventory | exact 36 records/revision/hashes and record-family counts |
| T61 | T01 | scan public names/literals and serialized positive result | no wording that asserts physical transition occurrence |
| T62 | T02/T03 | scan negative public result | no wording that asserts transition non-occurrence |
| T63 | authoritative T01 trace with separately derived equal coordinates | forge `semantic_candidate_index` and `value_candidate_index` to diverge | authoritative result reconstruction rejects; neither coordinate wins |
| T64 | iterative preflight graph whose exact canonical encoding is 134,217,728 bytes | unchanged exact-limit graph | byte preflight admits; later semantic validation may proceed normally |
| T65 | T64 | add one canonical byte | reject at byte 134,217,729 before plain copy, lower validation, or equality |
| T66 | iterative preflight graph with exactly 200,000 expanded node occurrences | unchanged exact-limit graph | node preflight admits |
| T67 | T66 | add one expanded node occurrence | reject at node 200,001 before canonical serialization or lower work |
| T68 | iterative preflight graph with deepest node at root-relative depth 128 | unchanged exact-limit graph | depth preflight admits |
| T69 | T68 | add one level | reject at depth 129 before canonical serialization or lower work |
| T70 | acyclic shared-subgraph twin below aggregate limit | share the same subtree at enough references to exceed expanded limit; separate cyclic variant | count each reference; limit+1 rejects; cycle rejects immediately |
| T71 | admitted ordinary request/result reconstructed once per TA boundary | instrument repeated nested reconstruction and distribute near-limit nodes across alignments | one aggregate budget, no per-alignment reset, no repeated TA subtree pass |
| T72 | bounded scalar/container twin | huge scalar, mapping, and sequence variants | incremental preflight rejects before full copy/bytes, Pydantic, equality, or fingerprint work |
| T73 | exhaustive literal/issue worlds | enumerate every public literal and all 22 issues | exact order, reachability, fixed arms, and multi-issue retention proven |

The preflight exact-limit twins T64, T66, and T68 exercise the private bounded
walker/canonical counter with structurally admissible ordinary content at the
numeric boundary; companion public tests exercise representative nominal TA
requests. They do not require a 128 MiB committed fixture. All generated
content is disposable temporary test data.

Verification must include focused, affected lower, architecture/import-
isolation, complete repository, compilation, dependency, base-only clean-
checkout, all-extras clean-checkout, explicit CAD/STEP/PDF, deterministic
reproduction, preservation, and working/full-range whitespace gates. Sandbox
loopback setup failures and separately permitted passing reruns are reported in
separate columns.

## 19. Owner-gated implementation slices

No implementation slice is authorized by this synthesis.

### 19.1 Task 0 — conditional discrepancy spike only

No spike is planned or required. If implementation exposes a concrete mismatch
between the Section 9 enforcement order and the accepted exact limits, stop and
write a bounded discrepancy report. Any probe must use disposable generated
positive worlds in temporary storage; it must not create a committed fixture,
record, membership, artifact, or demonstration.

### 19.2 Slice A — contracts and pure derivation

Add only `backend.transition_assessment` with the exact Section 11 public
surface, bounded iterative preflight, authoritative reconstruction, exact
joins, pure derivation, and red-first tests. Positive transition worlds must be
disposable and temporary and must never be committed as fixtures, ledger
records, memberships, evidence, result artifacts, or demonstrations. Add no
facade, store access, lower-layer change, or second consumer.

### 19.3 Slice B — adversarial hardening and final verification

Implement T01–T73, including the strict fingerprint gate, distinct-index
attack, exact limits, shared graphs, repeated reconstruction, deterministic
bytes, reachability, wording, no-I/O, replay, import isolation, and preservation.
Every genuine defect is first preserved as a failing test. Positive worlds
remain disposable temporary data and must not be committed in any form. Run
the complete working and dual-clean verification matrix. Production repairs
remain confined to the new package.

### 19.4 No demonstration slice

TA-001 v1 has no demonstration, authoritative append, committed result,
fixture, UI, facade, or second consumer. Any future proposal is a separate
owner gate, and any positive world used to evaluate that proposal must remain
disposable until an explicit later authorization says otherwise. Nothing in
this synthesis grants that authorization.

## 20. ADR sequencing gate

ADR-0019 records already accepted EA-001 decisions. Its absence is
documentation debt, not a runtime prerequisite or permission to redesign EA.
ADR-0019 must be completed before TA-001 implementation begins.

A future TA-001 ADR is allocated only after ADR-0019 and only after final
TA-001 design owner acceptance. It must record the pure leaf composition,
strict fingerprint rule, exact limit triple, non-cohort semantics, no-facade
boundary, and non-occurrence language. This design task creates neither ADR
and does not modify the root README's truthful pending status.

## 21. Explicit exclusions and known limitations

TA-001 excludes lower-contract changes, model records, authoritative
transition identities, fixture appends, current-store lookup, EA store
revalidation, source reread, temporal query orchestration, new evidence
selection, extraction, connectors, network access, writes, persistence,
caching, signatures, trusted time, UI, planning, control, flow assessment,
generic frameworks, registries, and demonstrations.

Its limits are explicit:

- endpoint classifications are independent latest-per-condition views, not
  synchronized state snapshots;
- two ordered endpoint views do not prove an intervening event or path;
- complete means complete only within each exact carried EA horizon;
- source-native clocks may be unrelated and are never compared;
- the state vocabulary may be incomplete or non-exclusive;
- pure reconstruction does not authenticate absent source bytes;
- coherent replacement can evade comparison if the expected fingerprint was
  not actually retained independently;
- pin currentness is relative to the carried model membership;
- the caller is responsible for producing and retaining the lower results;
  and
- the result cannot say what happened before, between, or after the cutoffs.

If implementation finds that an accepted valid lower result cannot expose the
Section 6 join, or that Section 9 cannot be enforced without a contract change,
it must stop with a discrepancy report. It may not read a private lower field,
weaken equality, reset bounds per child, change a lower literal, add a generic
adapter, or silently expand scope.

## 22. Consequences for later accountable occurrence and flow assessment

TA-001 is not accountable transition occurrence. A later occurrence milestone
would require separately approved facts absent here: durable occurrence
identity/lifecycle, event or interval semantics, temporal authority or explicit
qualification, continuity/gap policy, late/corrected evidence treatment, and
possibly signing and provenance policy. Trigger, guard, action, and effect
semantics would also require explicit declarations. A TA conclusion must never
be reinterpreted as a stored occurrence.

A later flow assessment likewise requires explicit flow variables, direction,
quantities, units, windows, participant semantics, evidence alignment, and
conservation/balance policy. Neither TA endpoint-pattern support nor existing
FRG/FLD declaration establishes physical flow, transfer, causality, or
mechanism.

The absence of a TA identity or persistence is intentional. If later
accountability needs a durable object, that identity, canonical meaning,
authority, and storage boundary must be designed and owner-gated rather than
inferred from TA's private deterministic test bytes.

## 23. Final owner decisions and unresolved-question closure

The following decisions are final for this corrected synthesis:

| Decision | Final value |
|---|---|
| Architecture | pure read-only `backend.transition_assessment` leaf over carried public results; no runtime prerequisite |
| Fingerprint gate | supplied expected fingerprint and relation `matched` for every governing observation, for positive and negative execution |
| Limits | 134,217,728 canonical-request bytes; 200,000 reconstructed nodes; depth 128 |
| Preflight | iterative node/depth/scalar/container admission before canonical serialization, Pydantic reconstruction, lower validation, equality, or fingerprint work |
| Orchestration | no facade and no store/evidence reselection |
| Demonstration | none in TA-001 v1; all positive worlds disposable and uncommitted |
| Public meaning | bounded support or bounded non-support for the declared endpoint pattern only |
| ADR order | complete documentation-debt ADR-0019 before implementation; allocate TA ADR only after final design acceptance |

There are zero unresolved owner questions and no hidden implementation gate.
Implementation remains separately owner-gated.

END OF TA-001 CORRECTED FINAL SYNTHESIS
