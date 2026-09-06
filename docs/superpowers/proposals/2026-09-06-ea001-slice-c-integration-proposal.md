# EA-001 Slice C — Bounded Integration Design Proposal

Date: 2026-09-06

Status: owner-resolved design candidate; bounded correction for owner review;
implementation unauthorized

This document proposes exactly one bounded EA-001 Slice C integration and is
not authorization to implement it. It changes no runtime code, test, fixture,
evidence, ledger, model record, accepted synthesis, or history.

## 1. Authority and verified checkpoint

The authorizing instruction is
`2026-09-06-ea001-slice-c-design-proposal.md`. It authorizes only this
design proposal. Slice C implementation, tests, fixtures, ledgers, artifacts,
branches, commits, pushes, merges, rebases, resets, cherry-picks, amendments,
and history rewrites remain unauthorized. The accepted EA-001 synthesis is not
edited.

Starting checkpoint, verified before any design work:

- branch: `ea001`;
- HEAD: `c34fc6868be9a554095b2fb10dae17436c617a71` (the Slice B administrative
  acceptance commit);
- accepted Slice B implementation:
  `932514a456bcafe690a94d2d774b61913c352fbf`;
- `git status --short` showed no tracked working-tree changes;
- the only untracked entry is the owner-local `.claude/settings.local.json`,
  which remains untouched and uncommitted.

The later checkpoint inspection found this already-written proposal as an
untracked file and correctly stopped because its ownership was then unknown.
The owner has since confirmed that the 618-line, 36,220-byte file at SHA-256
`60024fd3d5532983584a102b841263aa4ff8b827b1d44a856b267da03d7a765c`
is the intended candidate from the original design turn. The resulting
fail-safe discrepancy report remains unchanged and untracked as an audit
record. This dated correction preserves the candidate rather than regenerating
it and changes design documents only.

## 2. Materials read completely

- `CLAUDE.md` (908 lines) — binding project guidance.
- Accepted EA-001 synthesis
  `docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`,
  1,659 lines, SHA-256
  `557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`
  (unchanged from its accepted digest). Its Slice C paragraph permits exactly
  one consumer combining one already selected EA snapshot/fingerprint with
  that consumer's independently carried material, without reselecting
  evidence, with EA free of upper imports.
- Slice A integrity-repair completion report and owner acceptance; Slice B
  completion report (including the R1–R4 repair record) and Slice B owner
  acceptance.
- Public contracts, facades, and READMEs of: `backend/evidence_assurance`
  (contracts, queries, exports), `backend/data_sources` operational evidence
  (`contracts/operational_evidence.py`, reader seam),
  `backend/temporal_state` (contracts), `backend/identity_binding`
  (contracts, facade), `backend/model_state` (contracts, facade),
  `backend/observation_compatibility` (contracts, facade, README, exports),
  and the READMEs of `semantic_compatibility`, `constraint_evaluation`,
  `behavior_evaluation`, and `state_classification`.

## 3. Design question and decision summary

Question: should Slice C now bind one already-captured, content-fingerprinted
EA operational-evidence snapshot to one independently computed existing
consumer result, and if so, where?

Decision retained: **implement Slice C**, bounded to exactly one first
consumer, `backend.observation_compatibility.VariableValueCompatibilityResult`,
through one new tiny read-only composition package,
`backend.evidence_alignment`. The exact public join is **sufficient**; the
single subtlety, `endpoint_id`, is resolvable honestly from already carried EA
provenance (Section 5) and is not a blocking seam gap.

The owner has approved the proposed package name, single public function name,
and two explicit alignment-success statuses, and has deferred optional
store-bound revalidation from v1. Those decisions are incorporated below; they
do not authorize implementation.

## 4. Public join-surface inventory

Both sides were inspected at the exact public contract level. For each
required join fact, the exact public location is:

1. **Exact seven-part DS-004 scope.** EA side: complete, at
   `snapshot.request.scope` (`source_id`, `adapter_id`, `endpoint_id`,
   `item_key`, `subject_identifier`, `extraction_route`, `json_pointer`).
   Consumer side: six of seven fields, on every candidate's carried
   `TemporalOccurrence`
   (`result.candidates[i].state_candidate.bound.observed.occurrence`):
   `subject.source_id`, `subject.adapter_id`, `subject.subject_identifier`,
   `property.extraction_route`, `property.item_key`, `property.json_pointer`.
   `endpoint_id` is absent from `TemporalOccurrence`; see Section 5.
2. **Exact UTC `as_of` and EA horizon.** EA:
   `snapshot.request.as_of` and `snapshot.request.horizon_started_at`.
   Consumer: `result.as_of` (echoed from `result.state.as_of`). The consumer
   has no horizon concept; the horizon is an EA-only input and is carried
   verbatim inside the snapshot. The join compares `as_of` only.
3. **Selected occurrence identity and content.** EA:
   `snapshot.temporal_material.occurrence_membership[
   snapshot.selected.temporal_occurrence_index]`, with snapshot integrity
   enforcing that this index equals
   `snapshot.temporal_material.selected_occurrence_index`. The full public
   `TemporalOccurrence` carries `occurrence_id`, `attempt_id`,
   `observation_id`, `raw_record_id`, `payload_checksum`, `received_at`,
   `source_time`, `clock_segment_id`, `value_json`, `json_type`,
   `declared_unit`, `change_class`, `previous_occurrence_id`,
   `quality_flags`, and the complete ordering fields (`attempt_started_at`,
   `ingestion_run_id`, `sweep_position`). Consumer: the same public type at
   `result.candidates[i].state_candidate.bound.observed.occurrence`. Frozen
   Pydantic model equality over every field is the content-equality test;
   `value_json` compares as an exact string.
4. **In-horizon member versus pre-horizon seed.** EA:
   `snapshot.selected.pre_horizon_seed` and
   `snapshot.temporal_material.selected_occurrence_is_pre_horizon_seed`
   (validator-locked to agree). Consumer: no equivalent; the consumer's
   candidate is simply the locator's latest observation at or before the
   cutoff. The seed role is disclosed from the EA side only.
5. **Consumer candidate index and occurrence equality.** Recomputable:
   iterate `result.candidates`, compare each
   `candidates[i].state_candidate.bound.observed.occurrence` against the
   EA-selected occurrence by full model equality, record the index.
6. **Consumer model/binding/variable/specification identity and cutoff.**
   All present: `result.variable_anchor_id`; `result.ruleset_version`
   (`"vs001.1"`); `result.state.model_revision.revision_id`;
   `result.state.binding_revision.revision_id`;
   `result.specification_result.status` and
   `result.specification_result.revision` (validator-locked equal to the
   state model revision); per-candidate
   `candidates[i].state_candidate.attachment`; `result.as_of`.
7. **EA fingerprint and store-independent validation status.** EA:
   `snapshot.content_fingerprint`; the public pure validator
   `validate_operational_evidence_snapshot(snapshot, *,
   expected_fingerprint=...)` performs no I/O and returns
   `OperationalEvidenceSnapshotValidationResult`. The alignment function
   computes this result internally and carries it exactly once; callers do not
   supply a validation result.
8. **Store-bound revalidation.** Deliberately absent from the v1 alignment
   request and result. A caller may separately invoke the accepted
   `EvidenceAssuranceQueries.revalidate_operational_evidence(...)` API and
   display that independent, later disclosure beside an alignment. It neither
   rewrites nor participates in historical snapshot-to-consumer alignment.

One independence must be stated plainly: the consumer's `ruleset_version`,
model revision, and binding revision are consumer-side facts. The EA snapshot
contains none of them, and the consumer result contains no EA facts. The join
proves a relationship between the two carried disclosures; it never merges
their version axes.

## 5. The `endpoint_id` seam

`TemporalOccurrence` deliberately carries a six-dimension locator: the
three-field `SourceSubjectRef` plus the three-field `SourcePropertyRef`.
`endpoint_id` exists on `TemporalAttemptEvent` and on the source-side
`AcquisitionAttempt`, never on the occurrence. The consumer side therefore
cannot state the endpoint from its own carried occurrence, and this proposal
does not infer it from `item_key`, adapter, URL, or request text.

It is, however, recomputable from already carried EA provenance, honestly:

- `Ds004OperationalEvidenceMaterial` validation requires every carried
  `AcquisitionAttempt` to satisfy `attempt.endpoint_id ==
  scope.endpoint_id`, and requires each successful attempt to close to its
  envelope, API locator (which repeats `endpoint_id`), payload, extraction,
  and observations.
- EA parity (synthesis A13–A15, enforced by `_assert_snapshot_integrity` and
  the R3 diagnostics) requires the selected `TemporalOccurrence` to reconcile
  with the carried source chain, including its `attempt_id`,
  `raw_record_id`, `payload_checksum`, receipt time, value, type, unit, and
  ordering fields. This holds for a pre-horizon seed as well: the seed's
  `AcquisitionAttempt` is carried in `source_material.attempts` even though
  the seed never enters attempt-coverage membership.
- Therefore, for the exact selected occurrence, the chain
  `occurrence.attempt_id -> source_material.attempts[..].endpoint_id ==
  scope.endpoint_id` is mechanically closed inside the snapshot.

The honest claim available to the join is exactly this: when the consumer
candidate's carried occurrence is field-for-field equal to the EA-selected
occurrence, and the EA snapshot is structurally self-consistent, the shared
occurrence's attempt is bound to the snapshot's declared `endpoint_id` by
EA-internal closure. The comparison on the consumer side remains the six
locator fields plus complete occurrence content; the endpoint enters only
through EA's own validated closure. The result vocabulary names this
explicitly (Section 9) so no reader can mistake it for a consumer-carried
endpoint fact. No new lower field, consumer field, or migration is required.

## 6. First-consumer comparison

The lead hypothesis—start at `VariableValueCompatibilityResult`—was tested
against every candidate layer:

- **`model_state` (`VariableStateResult`).** Carries the occurrence and
  binding discovery, but joining here would strand the same need one layer
  up: observation compatibility is the first assessment that consumes this
  state, and it carries `VariableStateResult` verbatim. A VM-level join would
  have to be repeated or re-derived for VS. Rejected as the first consumer;
  its facts are fully available through the VS result.
- **`observation_compatibility` (`VariableValueCompatibilityResult`).**
  Narrowest existing assessment immediately above `VariableStateResult`.
  Carries the state result and the kernel specification result verbatim, adds
  `ruleset_version`, per-candidate shape/unit verdicts, and nothing else. It
  is the smallest surface at which an evidence-alignment relation is
  meaningful to every upper layer without redesign. **Selected.**
- **`semantic_compatibility`.** Adds interpretation verdicts that are
  explicitly unauthenticated authority claims. Coupling evidence alignment to
  that layer would widen the claim without adding any occurrence identity.
  Rejected for v1.
- **`constraint_evaluation`.** Composes the semantic stack for numeric
  verdicts. An identity join needs no constraint semantics; placing it here
  would skip the narrower layers without cause. Rejected for v1.
- **`behavior_evaluation`.** Composes two semantic paths under an acquisition
  cohort. Binding evidence there would require two aligned snapshots and is a
  different, later question. Rejected for v1.
- **`state_classification`.** Composes multiple constraint results into
  conjunctive classification. Far wider than the one-snapshot/one-result
  question. Rejected for v1.

Exactly one first consumer: `backend.observation_compatibility`, result
`VariableValueCompatibilityResult`.

## 7. Architecture alternatives

### 7.1 Optional consumer-side facade inside `observation_compatibility`

Import direction: `observation_compatibility -> evidence_assurance`
(downward, permitted by the synthesis for an approved integration slice).
Responsibility: one additional module deriving the alignment relation.
Public-surface impact: the accepted VS-001 package gains imports, exports,
and README truth changes; its accepted contract surface stops being
byte-stable, and—because `semantic_compatibility`, `constraint_evaluation`,
`behavior_evaluation`, and `state_classification` all compose it—every upper
package's transitive dependency closure grows to include EA permanently, even
for callers that never use alignment. Carry-once behavior: achievable.
Second-truth risk: low, but the permanent coupling of an accepted assessment
layer to an optional evidence layer is the price.

### 7.2 One tiny read-only upper composition package

Import direction: a new leaf package imports `evidence_assurance`,
`observation_compatibility` (and transitively its accepted lower contracts),
Pydantic, and the standard library. No existing package imports it; EA never
imports it or any consumer. Responsibility: exactly one pure derivation from
two already-computed public results. Public-surface impact: zero bytes change
in every accepted package; the entire new surface is one new package's own
pinned `__all__`. Carry-once behavior: achievable (Section 9). Second-truth
risk: none — it owns no store, ledger, cache, identity, or revision and
derives only from its inputs. Cost: one new governed public package name.

### 7.3 Defer Slice C

Not required: Section 4 shows every required join fact is recomputable from
existing public material, with `endpoint_id` honestly closed per Section 5.

### 7.4 Disposition

Alternative 7.1 is materially less safe on the exact grounds the instruction
reserves for 7.2: import isolation and public-surface stability of accepted
packages. **Alternative 7.2 is owner-approved as the proposal boundary**:
package `backend.evidence_alignment`, containing only pure contracts and one
pure derivation; no facade dependencies, no I/O of any kind.

## 8. Proposed boundary and exact proof statement

The integration proves, for one request pairing, at most: one EA selection
result is non-refused and its snapshot is store-independently
self-consistent; the snapshot's `as_of` equals the consumer result's `as_of`;
the snapshot's six shared locator fields equal one consumer candidate's
locator; that candidate's carried `TemporalOccurrence` is field-for-field
equal to the EA-selected occurrence; and the shared occurrence's endpoint is
bound to the snapshot scope by EA-internal closure. Everything else—consumer
attachment, shape/unit verdicts, specification status, revisions, EA coverage
completeness, and seed role—is disclosed verbatim or as derived scalars, never
gated or rewritten.

It never claims physical truth, present truth, semantic correctness,
accountable occurrence, safety, health, normality, compatibility in practice,
causal influence, flow, transition occurrence, or diagnosis. Equal values are
not identity; only complete occurrence identity/content equality aligns. A
refused, invalid, or unselected EA result is never promoted. An incomplete
snapshot may produce only `aligned_with_incomplete_evidence`, which proves
occurrence alignment and never complete, usable, current, or assured
assessment evidence. Integrity failures produce `not_evaluated`, never an
alignment. Store-independent validation is computed inside the pure function;
store-bound revalidation remains a separate caller operation outside this v1
contract. The derivation performs no source/temporal reselection, no store I/O,
no clock read, and no recalculation of the consumer from live stores.

## 9. Contract specification

All models are frozen, `extra="forbid"`, `revalidate_instances="always"`;
public boundaries convert nested content to plain values with cycle detection
and rebuild through declared public types, reusing the accepted EA hardening
idiom. No code is written in this proposal; names, fields, order, and
vocabularies below are implementation-ready.

### 9.1 Module and public API

- Package: `backend.evidence_alignment`
- Modules: `contracts.py` (models, vocabularies, errors), `derivation.py`
  (pure join), `__init__.py` (exact exports).
- Single public function:

```python
def align_operational_evidence_with_value_compatibility(
    request: OperationalEvidenceAlignmentRequest,
) -> OperationalEvidenceAlignmentResult: ...
```

The function takes no dependencies, performs no I/O, and reads no clock. It
internally calls the existing pure public
`validate_operational_evidence_snapshot(...)`; it never calls
`EvidenceAssuranceQueries`, any reader, `TemporalQueries`, or any consumer
facade.

### 9.2 Request

```python
class OperationalEvidenceAlignmentRequest:
    schema_version: Literal["1"]
    selection: OperationalEvidenceSelectionResult        # EA, VERBATIM
    compatibility: VariableValueCompatibilityResult      # VS-001, VERBATIM
    expected_snapshot_fingerprint: TaggedSha256 | None = None
```

All nested content is deep-reconstructed before derivation. A refused
selection is a structured outcome, not misuse; forged or internally
inconsistent nested instances raise the typed query error below. The expected
fingerprint is the only independent comparison input. The caller supplies
neither a prior validation result nor a store-revalidation result.

### 9.3 Result

```python
class OperationalEvidenceAlignmentResult:
    schema_version: Literal["1"]
    request: OperationalEvidenceAlignmentRequest
    status: OperationalEvidenceAlignmentStatus
    reason: OperationalEvidenceAlignmentReason | None
    snapshot_validation: OperationalEvidenceSnapshotValidationResult | None
    evidence_selection_status: OperationalEvidenceSelectionStatus
    evidence_coverage_completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
        "not_applicable",
    ]
    expected_fingerprint_relation: ExpectedFingerprintRelation
    cutoff_relation: Literal["equal", "different", "not_evaluated"]
    scope_relation: Literal[
        "six_field_locator_equal", "six_field_locator_different", "not_evaluated"
    ]
    endpoint_closure: Literal["bound_by_snapshot_closure", "not_evaluated"]
    selected_occurrence_role: Literal[
        "in_horizon_member", "pre_horizon_seed", "not_applicable"
    ]
    occurrence_relation: Literal[
        "content_equal",
        "absent_from_consumer_result",
        "content_mismatch",
        "multiple_matches",
        "not_applicable",
    ]
    mismatched_occurrence_fields: tuple[StrictStr, ...]   # max 20, sorted
    aligned_candidate_index: StrictInt | None
    candidate_attachment: Literal[
        "attached",
        "not_attachable_variable_unregistered",
        "not_attachable_anchor_divergent",
        "not_attachable_resolution_mismatch",
        "not_attachable_resolution_nonpositive",
        "not_evaluated",
        "not_applicable",
    ]
    variable_anchor_id: str        # VARIABLE_ANCHOR_ID_PATTERN
    model_revision_id: str         # derived scalar, equals carried
    binding_revision_id: str       # derived scalar, equals carried
```

Carry-once proof: the EA selection result (including its snapshot) and the
consumer result exist exactly once, inside `request`. No caller-supplied
validation or store revalidation is carried. The function computes the public
store-independent validation result and carries that object exactly once in
the output. The result otherwise adds only derived scalars, relations, and a
strict index. Validators require every derived scalar (`variable_anchor_id`,
`model_revision_id`, `binding_revision_id`, statuses, relations, candidate
index, attachment, mismatched-field list) to equal the value recomputed from
the carried inputs, so a stale or substituted derived field cannot construct.

### 9.4 Status, reason vocabulary, and precedence

```python
OperationalEvidenceAlignmentStatus = Literal[
    "aligned_with_complete_evidence",
    "aligned_with_incomplete_evidence",
    "not_aligned",
    "not_evaluated",
]

OperationalEvidenceAlignmentReason = Literal[
    "selection_refused",                      # 1
    "snapshot_fingerprint_mismatched",        # 2
    "no_selected_observation",                # 3
    "cutoff_differs",                         # 4
    "scope_differs",                          # 5
    "consumer_observation_absent",            # 6
    "occurrence_content_mismatch",            # 7
    "occurrence_absent_from_consumer_result", # 8
    "multiple_matching_candidates",           # 9
]
```

Precedence is the numeric order above; the first applicable reason is the
result's single `reason`. Reasons 1–2 produce `not_evaluated` (integrity or
validity gate; no relation fields beyond Section 9.3's status echoes are
asserted, and `scope/cutoff/occurrence` relations are `not_evaluated` /
`not_applicable`). Reasons 3–9 produce `not_aligned` with fully derived
relations. Absence of a reason (`reason=None`) is exactly the two aligned
statuses: `aligned_with_complete_evidence` when
`evidence_selection_status == "complete_within_declared_horizon"`, else
`aligned_with_incomplete_evidence`. The incomplete success requires an actual
selected occurrence and exact alignment; it proves occurrence identity only.

Derivation order: (1) strict-reconstruct the request; (2) `selection_refused`
when the selection status is `refused`; (3) for a carried snapshot, compute
the public pure snapshot validation exactly once for output, passing the
request's expected fingerprint; embedded structural/fingerprint invalidity in
an allegedly valid reconstructed selection is typed
`ALIGNMENT_REQUEST_INVALID`, while an independently expected fingerprint
mismatch is `snapshot_fingerprint_mismatched`; (4)
`no_selected_observation` when the EA outcome is
`no_observation_at_or_before_as_of`; (5) `cutoff_differs`; (6) `scope_differs`
when no candidate locator equals the six shared scope fields; (7)
`consumer_observation_absent` when every locator-equal candidate has
`bound=None`; (8) `occurrence_content_mismatch` when a locator-equal
candidate's occurrence has equal `occurrence_id` but any other field
differs, with `mismatched_occurrence_fields` naming the differing public
fields, sorted, bounded by the exact 20 public `TemporalOccurrence` fields;
(9) `occurrence_absent_from_consumer_result` when no locator-equal candidate
carries the occurrence at all; (10) `multiple_matching_candidates` when more
than one candidate is content-equal.

`multiple_matching_candidates` is retained because it is independently
reachable through otherwise valid accepted public reconstruction. The
`VariableStateResult` validator enforces `declared_locator_count ==
len(candidates)` and derives `selection="multiple"` from cardinality, but it
does not require discovery-mode candidates or their locators to be unique.
The `VariableValueCompatibilityResult` validator requires only index-parallel
equality and equal lengths between its compatibility candidates and the
carried state candidates; it likewise has no uniqueness rule. Consequently a
plain, fully reconstructable discovery result can duplicate one valid declared
candidate, set `declared_locator_count=2` and `selection="multiple"`, and
duplicate its index-parallel compatibility row. This is not emitted by the
accepted facade's normal locator discovery, but it is valid under the accepted
public result contract and yields two exact occurrence matches. The alignment
must therefore report `multiple_matching_candidates`; it may not choose one.

`endpoint_closure` is `bound_by_snapshot_closure` exactly when a
structurally self-consistent snapshot carries a selected occurrence and the
derivation has recomputed, from carried material only, that the selected
occurrence's `attempt_id` resolves to a carried `AcquisitionAttempt` whose
`endpoint_id` equals `scope.endpoint_id`; failure of that recomputation is
typed `ALIGNMENT_REQUEST_INVALID` because the already reconstructed EA
selection would violate its accepted integrity contract. It is never read from
consumer material.

### 9.5 Alignment claim boundary

Alignment requires content-equal occurrence identity and nothing else. It
does **not** require `candidate_attachment == "attached"` or any shape/unit
verdict; both are disclosed verbatim. An aligned result whose candidate is
unattached, or whose specification is conflicted, is an exact statement about
shared evidence identity beside a particular consumer result—never a
compatibility upgrade.

### 9.6 Errors and exports

```python
class EvidenceAlignmentError(Exception): ...          # error_code, message
class EvidenceAlignmentQueryError(EvidenceAlignmentError): ...
EvidenceAlignmentQueryErrorCode = Literal["ALIGNMENT_REQUEST_INVALID"]
```

One query-misuse code, raised before derivation for wrong types, forged
nested instances, boolean-as-index, hidden extras, cycles, hostile scalar
subclasses, or invalid plain content. No configuration error exists because
the function takes no dependencies. Messages are bounded, path-free, and
secret-free under the same `_bounded_safe_text` rule as EA.

`backend.evidence_alignment.__all__`, exact and ordered:

```python
[
    "EvidenceAlignmentError",
    "EvidenceAlignmentQueryError",
    "EvidenceAlignmentQueryErrorCode",
    "OperationalEvidenceAlignmentStatus",
    "OperationalEvidenceAlignmentReason",
    "OperationalEvidenceAlignmentRequest",
    "OperationalEvidenceAlignmentResult",
    "align_operational_evidence_with_value_compatibility",
]
```

No existing package's `__all__`, imports, README, or byte content changes. EA
exports are untouched; lower EA types are imported from their owners, never
re-exported.

### 9.7 Canonicalization and fingerprints

None. No new digest is introduced: the EA snapshot already carries its
content fingerprint; the alignment result is recomputed deterministically
from two carried public objects, so exact carried content—not a new
digest—is the recomputable join proof. A digest that summarized the
un-fingerprinted consumer result would add a summary without validating the
content it summarized, which the accepted EA rules forbid.

### 9.8 Deterministic ordering

The only collection added is `mismatched_occurrence_fields`, sorted by field
name. Candidate scanning is index order; the result is a pure function of its
request, independent of hash seed and input construction order.

## 10. Required case distinctions

| Case | Result |
| --- | --- |
| EA selected occurrence equals exactly one consumer candidate | `aligned_with_complete_evidence` or `aligned_with_incomplete_evidence` by EA status; `occurrence_relation="content_equal"`; exact `aligned_candidate_index` |
| EA selection valid but occurrence absent from that consumer result | `not_aligned / occurrence_absent_from_consumer_result` |
| Consumer has no observation | `not_aligned / consumer_observation_absent` when a locator-equal candidate exists with `bound=None`; `scope_differs` when no candidate locator matches |
| Multiple consumer candidates | normal: exactly one content-equal candidate aligns with its index; more than one content-equal is the independently reachable `multiple_matching_candidates` refusal and no candidate is chosen |
| Same value, different occurrence | `occurrence_absent_from_consumer_result`; value equality is never consulted |
| Same occurrence ID, mutated content | `occurrence_content_mismatch` with the exact sorted differing-field list |
| Same occurrence and content, different cutoff or scope | `cutoff_differs` or `scope_differs`; no alignment |
| Complete versus incomplete EA coverage | both may align; the statuses `aligned_with_complete_evidence` / `aligned_with_incomplete_evidence` keep them permanently distinct |
| Valid captured snapshot versus current-store revalidation mismatch | outside the v1 alignment contract; callers display the separately obtained EA revalidation disclosure without changing or recomputing historical alignment |

## 11. Adversarial acceptance matrix

All rows are executable contract tests. Every success status has a valid
twin; every refusal/status is independently reachable; public-surface tests
pin exact names and field sets.

| ID | Required executable acceptance |
| --- | --- |
| C01 | Happy path: complete EA selection, exactly one content-equal attached candidate → `aligned_with_complete_evidence`, `reason=None`, exact candidate index, all relations equal. |
| C02 | Incomplete EA coverage (code 16 issue) with an actual exact selected occurrence → `aligned_with_incomplete_evidence`; snapshot issues remain only inside the carried selection, and the result is described only as occurrence alignment, never complete, usable, current, or assured assessment evidence. |
| C03 | EA `no_observation_at_or_before_as_of` → `not_aligned / no_selected_observation`; no occurrence fields are consulted. |
| C04 | Pre-horizon seed twin: seed selected and content-equal → aligned with `selected_occurrence_role="pre_horizon_seed"`. |
| C05 | In-horizon selected twin → `selected_occurrence_role="in_horizon_member"`. |
| C06 | Same `value_json` and `declared_unit` from a different occurrence → `occurrence_absent_from_consumer_result`. |
| C07 | Same `occurrence_id`, mutated `attempt_id` → `occurrence_content_mismatch`, field list exactly `("attempt_id",)`. |
| C08 | Same ID, mutated `raw_record_id` or `payload_checksum` → content mismatch naming the exact fields. |
| C09 | Same ID, mutated `value_json` → content mismatch. |
| C10 | Same ID, mutated `json_type` → content mismatch. |
| C11 | Same ID, mutated `declared_unit` (including `None` versus supplied) → content mismatch. |
| C12 | Same ID, mutated `received_at` → content mismatch. |
| C13 | Same ID, mutated `attempt_started_at`, `ingestion_run_id`, or `sweep_position` → content mismatch naming ordering fields. |
| C14 | Same ID, mutated `source_time`, `clock_segment_id`, `change_class`, `previous_occurrence_id`, or `quality_flags` → content mismatch. |
| C15 | Differing `source_id` → `scope_differs`; likewise independently for `adapter_id`, `subject_identifier`, `extraction_route`, `item_key`, `json_pointer` (six rows, one per field). |
| C16 | The derivation never reads `endpoint_id` from consumer material; a snapshot whose selected-occurrence attempt closure disagrees with its scope cannot reconstruct as a valid EA selection and raises typed `ALIGNMENT_REQUEST_INVALID`. The valid endpoint-closed twin aligns. |
| C17 | Differing `as_of` → `cutoff_differs`, including equal instants with non-UTC awareness normalized before comparison. |
| C18 | Consumer result with a different model revision, binding revision, variable anchor, specification status, ruleset, or candidate order is simply a different input: derived result scalars equal the carried values exactly; forged internally inconsistent consumer results fail at request reconstruction via the accepted VS validators. |
| C19 | Refused EA selection → `not_evaluated / selection_refused`; the absent snapshot is never touched. |
| C20 | Structurally invalid snapshot content, hidden extras, or an internally inconsistent alleged selection raises typed `ALIGNMENT_REQUEST_INVALID`; no alignment result is constructed. Its valid reconstructed twin reaches pure validation. |
| C21 | Replacing a snapshot and embedded fingerprint together can remain structurally self-consistent when no independent expected fingerprint is supplied; supplying the retained original expected fingerprint yields `not_evaluated / snapshot_fingerprint_mismatched`. Substituting only the embedded fingerprint is typed invalid input. |
| C22 | Expected fingerprint twins: exact independently retained fingerprint → `expected_fingerprint_relation="matched"`; any other → `mismatched` with `not_evaluated / snapshot_fingerprint_mismatched`; absent → `not_supplied` and alignment unaffected. The computed validation result appears exactly once in the output. |
| C23 | Consumer variable unregistered / no candidates → `scope_differs` with `candidate_attachment="not_applicable"` and no index. |
| C24 | Locator-equal candidate with `bound=None` (consumer `none_before_cutoff`) → `consumer_observation_absent`. |
| C25 | Content-equal candidate with `attachment != "attached"` → still aligned; attachment disclosed verbatim; no verdict upgrade. |
| C26 | Conflicted specification twin → alignment unaffected; consumer verdicts remain `not_evaluated` inside the carried result. |
| C27 | Multiple candidates with exactly one content-equal candidate align at the exact index; zero content-equal yields `occurrence_absent_from_consumer_result`. |
| C28 | A fully reconstructed discovery-mode `VariableValueCompatibilityResult` with one valid candidate duplicated in both index-parallel tuples, `declared_locator_count=2`, and `selection="multiple"` reaches `not_aligned / multiple_matching_candidates`; the one-copy valid twin aligns. No candidate is chosen in the duplicate case. |
| C29 | Explicit-selector single-candidate twin behaves identically. |
| C30 | `model_construct`/`model_copy` forged nested selection, snapshot, or consumer instances → `ALIGNMENT_REQUEST_INVALID` before derivation. |
| C31 | Boolean-as-index, negative index, duplicate/reordered/extra/missing plain fields → typed misuse. |
| C32 | Hostile `str` subclass expected fingerprint or scope field → typed misuse or strict mismatch, never equality-by-`__eq__` trickery. |
| C33 | Stale derived scalars (wrong `model_revision_id`, wrong index, wrong attachment, unsorted or oversized `mismatched_occurrence_fields`) cannot construct a result; the exact 20-field bound is enforced. |
| C34 | Pure path proof: derivation performs no filesystem, SQLite, network, clock, or store I/O; the request has no validation-result, revalidation-result, path, dependency, or clock field. |
| C35 | Import isolation: `backend.evidence_alignment` imports no connector, store, or private lower module; EA imports nothing new; `observation_compatibility` and all accepted packages remain byte-frozen. |
| C36 | No reselection: the derivation never calls `TemporalQueries`, any reader, `EvidenceAssuranceQueries`, or any consumer facade; alignment uses only carried material. |
| C37 | Determinism: hash seeds 1, 7, and 12345 and permuted construction order yield equal results. |
| C38 | Error surface: public exceptions expose exactly `error_code` and `message`; messages are bounded, path-free, secret-free; `str(error)` is `"{error_code}: {message}"`. |
| C39 | Public surface: exact module names, function name, request/result field sets and order, literal order, and `__all__` equal the Section 9 pins; EA and VS `__all__` remain unchanged. |
| C40 | Preservation: the authoritative 36-record ledger, FL disclosure, accepted EA reproductions (24,766-byte and 11,528-byte digests), accepted synthesis, implementation files, and all historical artifacts remain unchanged. |

## 12. Owner-gated implementation plan

Two minimal gates; no Slice D demo is proposed.

- **Slice C1 — contracts and derivation, red-first:** create the package with
  the exact Section 9 contracts and derivation; add the Section 11 matrix as
  failing tests before implementation; no fixtures, no store builders, no
  demo; verify focused tests, the 137-test EA/lower gate, architecture and
  import-isolation tests, and preservation gates.
- **Slice C2 — public exports and full verification:** pin `__all__`, run the
  complete repository suite, fresh base-only and all-extras clean checkouts,
  whitespace gates, and preservation evidence; produce a completion report
  and stop for owner acceptance.

Either slice requires separate owner authorization. A committed deterministic
demo artifact is excluded; it would need its own later rehearsal, exact
identities/digests, and owner approval.

## 13. Explicit exclusions

No authoritative ledger or fixture append; no new durable identity, anchor,
minter, revision, store, cache, database, receipt, or signature; no
transition or flow assessment/occurrence; no semantic, constraint, behavior,
or state re-evaluation (observation compatibility is the selected existing
consumer, joined—not re-evaluated); no inference, ranking, aggregation, gap
filling, interpolation, or current-value selection; no diagnosis, causality,
impact, goals, actions, recommendations, planning, control, UI, or new
connectors; no change to accepted EA Slice A/B contracts; no EA import of any
consumer or model-side package; no second consumer in this slice.

## 14. Owner resolutions and remaining decisions

The owner resolved all proposal questions on 2026-09-06:

1. `backend.evidence_alignment` and
   `align_operational_evidence_with_value_compatibility(...)` are the approved
   proposed package and function names.
2. `aligned_with_complete_evidence` and
   `aligned_with_incomplete_evidence` remain distinct success statuses. The
   incomplete status proves only exact occurrence alignment; it never means
   complete, usable, current, or assured assessment evidence.
3. Store-bound revalidation is deferred from v1. Callers may invoke the
   accepted EA revalidation API separately, but its result is not an input to,
   output from, or participant in this alignment contract.
4. The caller-supplied pure snapshot-validation result is removed. The pure
   function computes validation internally and carries its result exactly once
   in the alignment result.

Unresolved owner decisions: **0**. This resolved proposal remains a design
candidate only. Slice C implementation requires a separate owner gate.

## 15. Verification of this proposal

Read-only checks run after correction: line and byte counts, SHA-256,
contiguous numbered sections 1–15, exact ending marker, whitespace checks, and
`git status --short`. Their observed values are reported in the turn receipt
and correction report. This file is left untracked for owner review. The
checkpoint discrepancy report is also left unchanged and untracked as an
audit record. No implementation, test, fixture, ledger, artifact, accepted
synthesis, commit, push, merge, or history operation was performed. The
accepted synthesis is byte-identical to its accepted digest.

END OF EA-001 SLICE C INTEGRATION PROPOSAL
