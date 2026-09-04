# EA-001 — Content-Bound Evidence Integrity and Immutable Assessment Selection

Status: Codex lead proposal; design only; not approved for implementation.

Date: 2026-09-04

The milestone name, package name, public names, ownership boundary, identities,
and persistence policy in this document are proposals. This document does not
authorize a new component, code, tests, records, fixtures, ledgers, artifacts,
or repository-history operations.

## 1. Status, authority, scope, and verified baseline

### 1.1 Authority and reading order

This proposal is subordinate to the accepted repository contracts. Where a
sketch here conflicts with an accepted contract, the accepted contract wins
until an owner-approved final synthesis explicitly changes it. The evidence
used for this proposal, in descending order of authority, is:

1. current validated code and tests at the verified baseline;
2. accepted ADRs 0001–0018;
3. accepted milestone specifications and final owner-acceptance reports;
4. the reconciled root and backend architecture documentation; and
5. this design-only proposal.

No contradiction between those accepted sources was found. Some older backend
READMEs retain historical milestone wording, but their technical boundaries
agree with the accepted ADRs and current root status.

### 1.2 Independently verified baseline

The repository was inspected rather than trusting the supplied values. At the
start of this design pass:

| Check | Verified value |
| --- | --- |
| branch | `main` |
| `HEAD` | `539f954fa759c9e20c167775b2ac906a8c867c85` |
| local `main` | `539f954fa759c9e20c167775b2ac906a8c867c85` |
| `origin/main` | `539f954fa759c9e20c167775b2ac906a8c867c85` |
| initial working tree | clean |
| authoritative model records | exactly 36 |
| authoritative model revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FRG / FLD / FLW | exactly `1 / 1 / 0` |
| TRG / TRD / TRW | exactly `0 / 0 / 0` |
| accepted flow disclosure size | 660,516 bytes |
| accepted flow disclosure SHA-256 | `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b` |
| 34-record predecessor aggregate | `cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd` |

The authoritative ledger verifier reproduced the revision, membership, flow
counts, transition absence, and predecessor aggregate. The committed FL-001
reproduction verifier reproduced the disclosure size and digest.

### 1.3 Scope of this proposal

This proposal asks one bounded question: what is the smallest architecture
that can bind an assessment's selected observation material to the stored
source bytes and exact knowledge contexts that were actually consulted?

It does not design transition assessment, flow assessment, behavior expansion,
physical occurrence, or a general provenance platform. It does not approve the
provisional `EA-001` name. It proposes no authoritative fixture and no model
record.

## 2. Repository and architecture findings

### 2.1 Implemented module boundaries

The accepted backend has thirteen modules. The relevant dependency direction
is:

```text
data_sources ────────────────┐
    ↓                        │
temporal_state               │
    ↓                        │
identity_binding             │
    ├──────────────┐         │
    ↓              ↓         │
source_interpretation        │
                   │         │
system_identity → model_kernel
                   ↓
               model_state
                   ↓
        observation_compatibility
                   ↓
          semantic_compatibility
                   ↓
       constraint / behavior evaluation
                   ↓
          state_classification
```

The diagram shows information use, not permission for foundational packages to
import upper packages. `model_kernel` remains independent of source, temporal,
binding, interpretation, and evaluation stores. Read-only composition modules
own no authoritative ledger.

### 2.2 Source evidence actually retained

`backend.data_sources` persists distinct artifacts:

- content-addressed payload bytes, addressed by `sha256:<64 hex>`;
- a `RawRecord` envelope with source, acquisition run, checksum, immutable
  payload reference, provenance, and, for API evidence, an `ApiSourceLocator`;
- one `AcquisitionAttempt` for each operational polling occurrence, including
  failures and byte-identical repeats;
- an `IngestionRun` with acquisition and quarantine counts;
- either an `ExtractionResult` with `ExtractorIdentity` or a
  `QuarantineRecord` for an acquired record; and
- optional derived artifacts, which are explicitly recomputable and are not
  raw evidence.

The raw store's `get_payload()` rereads bytes and checks their checksum. JSON
metadata files are write-once by convention and file mode, strictly parsed on
read, and conflict-checked on append. Their filenames and stored bytes are not,
however, all content-derived identities. File mode `0444` and atomic rename are
ordinary mutation guards, not tamper-proof storage, a signature, or an
attestation.

For the operational API slice, `request_canonical`, `request_fingerprint`,
sanitized `target_origin`, adapter, endpoint, item, transport mode, receipt
times, retry facts, response size, raw record, and checksum live on the
attempt. `ApiSourceLocator` preserves the extraction route. Extraction results
preserve extractor name, version, toolchain, and configuration fingerprint.
Secrets and the complete live connector configuration are deliberately not
persisted.

### 2.3 Temporal evidence actually retained

`backend.temporal_state` owns a rebuildable SQLite projection, not source
evidence. Its immutable logical rows are:

- `TemporalAttemptEvent`, the processed-attempt and coverage row, including
  failed, quarantined, empty, and nonempty outcomes; and
- `TemporalOccurrence`, one point observation per attempt and extracted
  observation, never deduplicated by payload or value.

`latest_observed()` selects on the ingestion receipt axis. It includes
occurrences with `received_at <= as_of`, then orders by `received_at`
descending and the complete `AttemptOrderKey` descending. Evidence-quality
counts use attempt `effective_wall_time <= as_of`; a failure without response
uses `finished_at`. The public result discloses staleness, intervening failures,
quarantines, later empty snapshots, later snapshots without the property,
source-time basis, clock segment, and possible reset flags.

The temporal store can be rebuilt from the raw evidence store. Its public
provenance query currently closes only the identifiers
`occurrence → attempt → observation → raw record → checksum`; it does not
reread payload bytes or carry extraction and metadata-file byte digests.

### 2.4 Identity, interpretation, and model knowledge

`identity_binding` and `source_interpretation` are independent append-only
knowledge ledgers:

- binding resolves an exact six-part source locator to a declared entity or
  variable at the occurrence's own `received_at`;
- interpretation independently resolves quantity kind, observation role, and
  unit at that same occurrence instant; and
- each result discloses its exact `rev_` or `irv_` membership.

Their records and revisions are content-derived and replayable. Their
authorities are declared authorities, not authenticated signers. The two
knowledge domains are intentionally not cross-certified.

`model_kernel` similarly validates exact content-derived model records and an
exact `mrv_` membership. Kernel public results carrying `ModelQueryMaterial`
can reconstruct that entire selected model revision in memory and reject
forged records, indices, results, and revisions without accessing a store.

### 2.5 Existing upper-layer selection and validation

`model_state` composes one loaded model, one loaded binding revision, and
`TemporalQueries`. An explicit `SourceSelector` or declared binding locator is
queried independently for its latest occurrence at or before a required
receipt-axis cutoff. Binding resolution occurs at each selected occurrence's
own receipt time. No ranking, fallback history, aggregation, or single
physical-state claim exists.

`observation_compatibility` and `semantic_compatibility` preserve the selected
occurrence and compare carried source values and declared meanings with model
declarations. Constraint, behavior, and state layers rederive their own output
from carried public results and enforce revision, context, selector, cutoff,
ordering, and index coherence.

Those upper validators intentionally own no source store. Accepted executable
tests demonstrate that a coherent mutation of a carried occurrence and its
carried checksum can remain internally valid when the raw payload is absent.
This is the demonstrated architectural gap, not a hypothetical weakness.

### 2.6 Accepted declaration boundaries remain fixed

ST-002 and FL-001 add declaration-only model knowledge. A transition
declaration is not an occurrence. A logical directed flow declaration is not
physical transfer. ADR-0017 says transition assessment needs an explicit
temporal selection/evidence contract. ADR-0018 says flow assessment needs
measurement association plus temporal selection, continuity, and immutable
evidence-selection rules. This proposal supplies at most the common evidence
selection foundation; it does not supply either assessment.

## 3. Precise problem statement

### 3.1 The gap

An upper result can currently prove:

- that its carried Pydantic graph is structurally valid;
- that content-derived model records and `mrv_` membership reconstruct;
- that the same cutoff, selectors, model revision, binding revision, and
  interpretation revision were carried consistently; and
- that its own conclusions follow deterministically from those carried facts.

It cannot, without source-store access, prove that the carried occurrence
still corresponds to the bytes named by its checksum. It also does not bind a
complete, immutable list of the attempts and exceptional outcomes considered
by selection. Consequently, it cannot later distinguish:

- “this result graph is self-consistent” from
- “these exact source-store bytes and metadata were read, their links were
  checked, and this exact bounded membership was selected.”

### 3.2 Required capability

The minimum useful capability is a read-only, deterministic selection snapshot
that names and binds:

1. the exact requested source locators and model variables;
2. the selected `TemporalOccurrence`, if any;
3. every in-scope acquisition attempt needed to rederive the selection and its
   coverage through one inclusive cutoff;
4. the raw payload checksum, raw envelope, attempt, run, extraction or
   quarantine artifact, extractor identity/configuration fingerprint, API
   locator, and their stored-file digests;
5. exact temporal projection membership and projector/schema versions;
6. exact binding, interpretation, and model revision memberships;
7. the public binding, interpretation, attachment, and semantic-compatibility
   results used for assessment admission;
8. policy version, cutoff, ordering, limits, and optional freshness threshold;
9. acquisition failure, quarantine, empty snapshot, omitted-property,
   staleness, and clock limitations; and
10. a canonical digest over all of the above.

The snapshot must be computable without creating authoritative knowledge. It
must be possible to validate its structure and digest later without a store,
and separately to recheck its named source bytes when the source store is
available. Those are different guarantees and must remain differently named.

### 3.3 What closing the gap does not prove

Even the strongest store-bound result does not prove that:

- a sensor or source was correct, calibrated, honest, or authoritative;
- a timestamp represents shared physical time;
- an extractor, interpretation authority, or binding authority was correct;
- a value is physical truth or persisted after its observation;
- a state, transition, flow, behavior, cause, fault, hazard, or diagnosis is
  true; or
- any action is required, permitted, safe, or recommended.

## 4. Existing guarantees and exact gaps

| Plane | Existing mechanical guarantee | Exact remaining gap |
| --- | --- | --- |
| payload | `get_payload()` checks bytes against a tagged SHA-256 | upper results do not carry or recheck the bytes |
| raw identity | API record ID is derived from source, item, and checksum | `RawRecord` is strict but its full stored JSON bytes have no disclosed digest |
| occurrence | every operational attempt is distinct; occurrence ID derives from attempt and observation | upper result does not prove the temporal row exists in the loaded projection |
| extraction | exact raw ID, extractor identity, manifest, observation and JSON Pointer are stored | no general public receipt binds the extraction file bytes to the selection; configuration fingerprint is not a persisted configuration object |
| field value | operational observation carries canonical `value_json`, `json_type`, and pointer | accepted upper chain does not independently resolve the pointer against raw bytes |
| temporal | latest-at-or-before and evidence quality are deterministic in one temporal query | no one-transaction public material query exposes the complete bounded attempt/occurrence membership used by a multi-target selection |
| binding | exact locator, occurrence-time resolution, record revision, lifecycle | authority is declared; public result does not carry all ledger records for independent reconstruction |
| interpretation | exact locator/dimension, occurrence-time resolution, revision | meaning remains an authority claim and is independent of binding |
| model | exact content-derived records and `mrv_`; kernel carry-once validation | model revision says what model knowledge was selected, not when evidence occurred |
| semantics | deterministic exact-token and value-shape comparison | compatibility is not correctness and does not authenticate source content |
| upper evaluation | authoritative reconstruction of carried public results | coherent lower-content substitution remains outside its store-independent boundary |
| occurrence | source says a value was observed on one attempt | no accountable physical occurrence claim exists |

The proposal must not “repair” a gap by renaming an existing weaker guarantee.

## 5. Architecture alternatives and trade-offs

### 5.1 Alternative A — new read-only sibling composition module

Create a small upper composition package, provisionally
`backend.evidence_assurance`, which receives already-loaded read-only
dependencies. It requests bounded source and temporal material through new
lower-layer read contracts, invokes existing binding/interpretation/semantic
facades, compares the results, and emits a computed snapshot and digest.

Benefits:

- one place owns cross-store selection policy and guarantee vocabulary;
- source and temporal packages retain their narrow meanings;
- model-kernel independence remains intact;
- downstream evaluators can consume one exact snapshot rather than each
  inventing provenance checks; and
- no new authoritative store, ledger, identity, or revision is required.

Costs:

- a new top-level package and public contracts exist;
- narrow public material-read seams are required in `data_sources` and
  `temporal_state`;
- the package sits above several accepted domains and therefore needs strict
  import-isolation tests; and
- snapshots can be large, although fixed count and byte limits make them
  bounded and raw payload bytes are not embedded.

### 5.2 Alternative B — bounded extension of `temporal_state`

Extend `temporal_state` to check raw bytes, resolve binding and interpretation,
pin a model revision, and emit the selection digest.

The raw-byte and one-transaction temporal-material portions fit naturally
near `temporal_state`. The full capability does not. Binding, interpretation,
model membership, and semantic compatibility are upper knowledge domains.
Importing them into `temporal_state` would invert accepted dependencies,
change a source-native projection into an assessment-composition layer, and
risk circular imports through `identity_binding` and `model_state`.

Verdict: reject as the complete boundary. Retain only a narrow temporal
prerequisite query that exposes bounded rows in one read transaction without
knowing variables, model anchors, interpretations, or assessments.

### 5.3 Alternative C — strengthen existing public result contracts only

Add raw evidence receipts independently to `model_state`, semantic
compatibility, constraint evaluation, behavior evaluation, and state
classification, with no new module.

Benefits:

- no new top-level package; and
- each consumer could choose its own exact evidence needs.

Costs and failure modes:

- raw-store access would spread into packages intentionally designed to be
  store-independent;
- checksum, coverage, TOCTOU, refusal, and digest rules would be duplicated;
- every result would grow a subtly different provenance vocabulary;
- lower contracts would acquire knowledge of upper assessment shapes; and
- consistent later transition/flow assessment would be less likely, not more.

A small strengthening of lower read APIs is necessary under any honest design,
but strengthening every upper result is not the smallest coherent solution.

### 5.4 Alternative D — persisted assessment-input ledger

A dedicated append-only ledger could give selections durable record IDs and
historical membership. No current requirement demonstrates that need. It
would duplicate source/knowledge memberships, create another revision axis,
and turn a computed input into authoritative knowledge before its lifecycle or
authority has been justified.

Verdict: reject for the first milestone. A caller may retain a snapshot and
its digest as an external artifact, but the proposed package does not persist
or canonize it as model truth.

## 6. Lead recommendation, ownership, and import map

### 6.1 Recommendation

Proceed, if separately approved, with a new read-only sibling composition
component. The provisional package name is `backend.evidence_assurance`; the
owner should approve or replace that name before implementation. The component
has exactly one purpose: compute and revalidate bounded, content-bound
assessment-input selections.

EA-001 should therefore exist as a component, but not as a new truth system.
It owns:

- the cross-domain selection request;
- the fixed v1 selection policy;
- selection-snapshot and assurance contracts;
- deterministic selection/digest derivation; and
- store-bound versus store-independent revalidation orchestration.

It owns no source, temporal, binding, interpretation, model, evaluation, or
assessment store. It creates no anchor, durable record identity, ledger,
revision, cache, database, or automatic model claim.

### 6.2 Narrow lower-layer prerequisites

Two prerequisites avoid private-field access and inconsistent multi-query
reads:

1. `data_sources` owns a public `OperationalEvidenceReader` protocol and a
   filesystem implementation that captures exact in-scope stored bytes and
   strictly parsed metadata from one bounded read view. It verifies payload
   checksums and field-level JSON Pointer values. It knows nothing about
   variables, bindings, model revisions, or selection conclusions.
2. `temporal_state` owns a public `selection_material()` query that returns
   exact in-scope attempt events, occurrences, clock openings, and
   schema/projector versions from one SQLite read transaction. It performs no
   binding, interpretation, semantic, or assessment work.

These are lower read-contract extensions, not a relocation of EA policy into
either lower module.

### 6.3 Permitted imports

If approved, `backend.evidence_assurance` may import only public contracts or
facades from:

- `backend.data_sources`;
- `backend.temporal_state`;
- `backend.identity_binding`;
- `backend.source_interpretation`;
- `backend.model_kernel`;
- `backend.model_state`;
- `backend.observation_compatibility`; and
- `backend.semantic_compatibility`.

Standard library and Pydantic imports remain permitted. Direct imports of
concrete filesystem internals or SQLite internals are forbidden; injected
public readers own those mechanisms.

### 6.4 Forbidden imports

The proposed package must not import constraint evaluation, behavior
evaluation, state classification, transition-specific or flow-specific
assessment code, UI, connectors, vendor adapter implementations, or future
reasoning packages. No existing foundational package may import
`evidence_assurance`. In particular, `model_kernel`, `system_identity`,
`data_sources`, and `temporal_state` must not import back from it.

### 6.5 Dependency injection and read ownership

The facade is constructed from explicit, already-configured read-only
dependencies. It does not discover paths, environment variables, stores,
current revisions, or clocks. It reads:

- one operational evidence store per request in v1;
- one temporal projection corresponding to that store;
- one explicitly loaded binding revision;
- one explicitly loaded interpretation revision; and
- one explicitly loaded model revision.

Multi-source selection is allowed only when all requested locators share that
same injected evidence-store namespace and the one request pins one revision
of each knowledge domain. Selection across several unrelated raw-store roots
is deferred because there is no accepted atomic or federated membership
contract.

## 7. Assurance vocabulary

The public vocabulary must name mechanisms, not imply trust. The following
terms are normative if this proposal is accepted:

| Guarantee | Exact meaning | Does not mean |
| --- | --- | --- |
| `payload_checksum_match` | bytes read during this store-bound invocation hash to the `sha256:` reference | signature, source authenticity, later immutability |
| `stored_artifact_digest_match` | named metadata file bytes match a previously carried artifact digest during revalidation | the metadata claim is true |
| `raw_provenance_closed` | attempt, run, envelope, payload, extraction/quarantine, API locator, and observation references form the required exact chain | extractor correctness or source authority |
| `observation_content_match` | the exact JSON Pointer resolves in the checked payload and canonical value/type equal the stored operational observation | the pointer has correct engineering meaning |
| `temporal_membership_reconciled` | exact temporal attempt/occurrence rows exist in the one captured projection material and agree with source material on governed fields | physical occurrence, persistence, or a trusted clock |
| `binding_coherent` | accepted binding resolution at occurrence `received_at` names the requested variable under the pinned binding revision | the authority decision is correct |
| `interpretation_coherent` | accepted interpretation resolution at occurrence `received_at` is carried under the pinned interpretation revision | the source actually has that meaning |
| `model_revision_coherent` | the injected loaded model exactly equals the request's pinned `mrv_` membership | the model is physically true or temporally current |
| `selection_integrity_complete` | the fixed policy was applied to a complete bounded in-scope membership with canonical ordering and no integrity refusal | the selected evidence is sufficient for a physical conclusion |
| `declared_semantics_compatible` | the existing ES-001 exact declared-meaning conditions hold | semantic truth, calibration, value validity, or safety |
| `accountable_occurrence_not_assessed` | this component emits no physical occurrence conclusion | absence of a physical occurrence |

The words “authenticated,” “verified,” and “authoritative” must never appear
unqualified in public EA output. Permitted phrases include “payload checksum
verified against bytes read in this invocation” and “authoritative model
revision reconstructed under the model-kernel contract.” The snapshot itself
is not an authenticated statement and has no authority rank.

## 8. Proposed public contracts

All names in this section are exact proposals, subject to the owner decision
in Section 18. Contracts are frozen, `extra="forbid"`, and
`revalidate_instances="always"`. At public boundaries every nested object is
rebuilt from plain serialized content; preconstructed Pydantic instances are
not trusted.

### 8.1 Request contracts

```python
class EvidenceSelectionTarget:
    selection_key: str                 # ^[a-z][a-z0-9_-]{0,63}$
    variable_anchor_id: str            # accepted var_ pattern
    source: SourceSelector             # exact subject + property

class EvidenceKnowledgePins:
    model_revision_id: str             # exact mrv_
    binding_revision_id: str           # exact rev_
    interpretation_revision_id: str    # exact irv_

class IndependentLatestReceiptPolicy:
    kind: Literal["independent_latest_at_or_before_cutoff"]
    version: Literal["ea001.selection.v1"]
    selection_axis: Literal["ingestion_received_at"]
    source_time_use: Literal["disclose_only"]
    maximum_staleness_seconds: CanonicalNonnegativeDecimal | None

class EvidenceSelectionRequest:
    schema_version: Literal["1"]
    targets: tuple[EvidenceSelectionTarget, ...]  # 1..64
    as_of: UtcDatetime
    knowledge: EvidenceKnowledgePins
    policy: IndependentLatestReceiptPolicy
```

Targets are canonically ordered by `selection_key`. Keys, complete source
locators, and exact `(variable_anchor_id, source)` triples are unique.
Booleans, coercible numbers, naive datetimes, duplicate targets, hidden fields,
and over-limit tuples reject before any store access. `as_of` normalizes to
UTC. The canonical decimal grammar is a nonnegative, finite, plain decimal
without exponent, leading plus, whitespace, negative zero, or trailing
fractional zero.

V1 has no caller-selectable ordering, fallback, source-time axis, time window,
aggregation, ranking, sampling, or query clock. A caller request for any
source-time comparison fails before I/O with the distinct typed error
`EA_TIME_COMPARISON_UNSUPPORTED`; it is not collapsed into a malformed cutoff.

### 8.2 Lower source material

```python
EvidenceArtifactKind = Literal[
    "ingestion_run", "acquisition_attempt", "raw_envelope",
    "raw_payload", "extraction_result", "quarantine_record"
]

class EvidenceArtifactDescriptor:
    kind: EvidenceArtifactKind
    logical_id: str
    byte_count: StrictInt              # >= 0; bool rejected
    stored_sha256: str                 # sha256:<64 hex>

class OperationalEvidenceMaterial:
    source_ids: tuple[str, ...]
    artifacts: tuple[EvidenceArtifactDescriptor, ...]
    runs: tuple[IngestionRun, ...]
    attempts: tuple[AcquisitionAttempt, ...]
    envelopes: tuple[RawRecord, ...]
    extractions: tuple[ExtractionResult, ...]
    quarantines: tuple[QuarantineRecord, ...]
    payload_checksums: tuple[str, ...]
    initial_inventory_digest: str
    final_inventory_digest: str
```

Raw payload bytes are deliberately absent. The reader parses each metadata
model from the same byte string whose descriptor it hashes. It returns a
unique ordered object once; snapshot rows use strict indices. A payload
descriptor hashes the payload bytes and its logical ID is the tagged checksum.
No absolute or relative filesystem path is public material.

The exact cross-object links are represented once as strict indices:

```python
class OperationalProvenanceRoute:
    attempt_index: StrictInt
    run_index: StrictInt
    temporal_attempt_index: StrictInt
    envelope_index: StrictInt | None
    payload_artifact_index: StrictInt | None
    extraction_index: StrictInt | None
    quarantine_index: StrictInt | None
    observation_index: StrictInt | None
    temporal_occurrence_index: StrictInt | None
    artifact_descriptor_indices: tuple[StrictInt, ...]
```

Each index is nonnegative, in range, non-boolean, and points to the exact
governed union arm. A failed attempt has no envelope, payload, extraction,
quarantine, observation, or occurrence index. A quarantined successful
attempt has envelope, payload, and quarantine indices but no extraction,
observation, or occurrence. A projected property observation has the complete
positive route. Impossible combinations reject during outer reconstruction.

### 8.3 Lower temporal material

```python
class TemporalSelectionScope:
    source_id: str
    adapter_id: str
    item_key: str

class TemporalSelectionMaterial:
    schema_version: str
    projector_version: str
    scopes: tuple[TemporalSelectionScope, ...]
    as_of: UtcDatetime
    attempt_events: tuple[TemporalAttemptEvent, ...]
    occurrences: tuple[TemporalOccurrence, ...]
    clock_segment_openings: tuple[ClockSegmentOpening, ...]
    logical_material_digest: str
```

`selection_material()` obtains all fields in one SQLite read transaction. It
returns only exact requested scopes at or before the cutoff and enforces the
global row limits before materialization. Its digest is over logical canonical
rows, never SQLite, WAL, or SHM bytes.

### 8.4 Selection snapshot rows

```python
EvidenceSelectionOutcome = Literal[
    "selected", "none_before_cutoff", "not_admitted"
]

FreshnessFinding = Literal[
    "threshold_not_declared", "within_declared_threshold",
    "exceeds_declared_threshold", "not_evaluated"
]

SemanticAdmission = Literal[
    "declared_compatible", "not_declared_compatible", "not_evaluated"
]

class EvidenceCoverageSummary:
    applicable_attempt_indices: tuple[StrictInt, ...]
    provenance_route_indices: tuple[StrictInt, ...]
    failed_attempt_indices: tuple[StrictInt, ...]
    quarantined_attempt_indices: tuple[StrictInt, ...]
    empty_snapshot_attempt_indices: tuple[StrictInt, ...]
    omitted_property_attempt_indices: tuple[StrictInt, ...]
    latest_applicable_attempt_index: StrictInt | None
    cadence_gap_assessment: Literal["not_assessed_no_cadence_contract"]

class EvidenceSelectionRow:
    target_index: StrictInt
    outcome: EvidenceSelectionOutcome
    occurrence_index: StrictInt | None
    selected_provenance_route_index: StrictInt | None
    coverage: EvidenceCoverageSummary
    staleness_seconds: CanonicalNonnegativeDecimal | None
    freshness: FreshnessFinding
    payload_integrity: Literal["matched", "not_evaluated"]
    provenance_closure: Literal["closed", "not_evaluated"]
    observation_content_relation: Literal[
        "exact_value_and_type", "not_evaluated"
    ]
    temporal_membership: Literal["reconciled", "not_evaluated"]
    binding_result_index: StrictInt | None
    binding_alignment: Literal[
        "bound_to_requested_variable", "bound_elsewhere", "unresolved",
        "conflicted", "not_evaluated"
    ]
    interpretation_result_index: StrictInt | None
    interpretation_coherence: Literal[
        "all_dimensions_interpreted", "one_or_more_dimensions_nonpositive",
        "not_evaluated"
    ]
    semantic_result_index: StrictInt | None
    semantic_admission: SemanticAdmission
    accountable_occurrence: Literal["not_assessed"]
    issue_indices: tuple[StrictInt, ...]
```

The full accepted binding, interpretation, and semantic result objects are
carried once in sibling tuples on the snapshot. Rows use strict indices and
derived scalars only. The source and temporal material are also carried once.
An occurrence is never repeated merely because several downstream claims cite
it.

### 8.5 Snapshot and outer results

```python
EvidenceSelectionStatus = Literal["complete", "incomplete", "refused"]
IssueSeverity = Literal["incomplete", "refusal"]

class EvidenceSelectionIssue:
    code: EvidenceSelectionIssueCode
    severity: IssueSeverity
    target_index: StrictInt | None
    detail: str                        # bounded, path-free, secret-free

class EvidenceSelectionSnapshot:
    schema_version: Literal["1"]
    request: EvidenceSelectionRequest
    model_revision: ModelRevision
    binding_revision: BindingRevision
    interpretation_revision: InterpretationRevision
    source_material: OperationalEvidenceMaterial
    temporal_material: TemporalSelectionMaterial
    provenance_routes: tuple[OperationalProvenanceRoute, ...]
    binding_results: tuple[ResolutionResult, ...]
    interpretation_results: tuple[PropertyInterpretationResult, ...]
    semantic_results: tuple[VariableSemanticCompatibilityResult, ...]
    rows: tuple[EvidenceSelectionRow, ...]
    issues: tuple[EvidenceSelectionIssue, ...]
    selection_digest: str              # sha256:<64 hex>

class EvidenceSelectionResult:
    status: EvidenceSelectionStatus
    request: EvidenceSelectionRequest
    snapshot: EvidenceSelectionSnapshot | None
    issues: tuple[EvidenceSelectionIssue, ...]

class EvidenceSnapshotValidationResult:
    status: Literal[
        "internally_consistent", "digest_mismatch", "invalid"
    ]
    computed_digest: str | None
    expected_digest_match: Literal["matched", "mismatched", "not_supplied"]
    store_byte_check: Literal["not_rechecked"]
    detail: str

class EvidenceStoreRevalidationResult:
    status: Literal[
        "matches_current_store", "valid_for_frozen_membership",
        "membership_changed", "refused"
    ]
    snapshot_digest: str
    current_membership_relation: Literal[
        "equal", "strict_superset", "divergent", "not_evaluated"
    ]
    artifact_results: tuple[EvidenceArtifactRevalidationResult, ...]
    issues: tuple[EvidenceSelectionIssue, ...]

class EvidenceArtifactRevalidationResult:
    descriptor_index: StrictInt
    byte_check: Literal["matched", "mismatched", "unavailable"]
    observed_byte_count: StrictInt | None
    observed_sha256: str | None
```

`complete` means every target produced assessment-admissible selected material
under the stated policy. `incomplete` means a deterministic, digestible
snapshot exists but at least one target lacks an admissible input. `refused`
means the component could not safely create a snapshot; `snapshot` is then
`None`. A semantic mismatch is not an integrity mismatch, but it makes that
target not admitted under this first assessment-input policy and is disclosed
by the exact semantic result.

### 8.6 Proposed public facade

```python
class EvidenceAssuranceQueries:
    def __init__(
        self,
        *,
        evidence: OperationalEvidenceReader,
        temporal: TemporalQueries,
        bindings: BindingResolver,
        interpretations: InterpretationResolver,
        model: LoadedModel,
        semantics: SemanticCompatibilityQueries,
    ) -> None: ...

    def select_assessment_evidence(
        self,
        request: EvidenceSelectionRequest,
    ) -> EvidenceSelectionResult: ...

    def revalidate_assessment_evidence(
        self,
        snapshot: EvidenceSelectionSnapshot,
        *,
        membership_mode: Literal["exact_current", "frozen_membership"],
    ) -> EvidenceStoreRevalidationResult: ...

def validate_evidence_selection_snapshot(
    snapshot: EvidenceSelectionSnapshot,
    *,
    expected_digest: str | None = None,
) -> EvidenceSnapshotValidationResult: ...
```

No `current_*`, `authenticate_*`, `trust_*`, `attest_*`, history, occurrence,
assessment, transition, flow, behavior, diagnosis, or recommendation alias is
added. `select_assessment_evidence` selects inputs; it does not execute an
engineering assessment.

### 8.7 Proposed exports

The first public `__all__` is limited to the contracts and functions named in
Sections 8.1–8.6, the status aliases in Sections 7 and 14, the three typed EA
errors, `OperationalEvidenceReader`, and `EvidenceAssuranceQueries`. Lower
accepted contracts are imported from their owners, not re-exported under EA
aliases.

## 9. Selection and verification lifecycle

The normative store-bound algorithm is:

1. Rebuild the request from serialized content. Validate exact literals,
   strict scalar types, target order/uniqueness, limits, and aware cutoff
   before any read.
2. Revalidate the injected `LoadedModel`, binding set, and interpretation set.
   Require their exact revision IDs and memberships to equal the three request
   pins. A pin never means “latest.”
3. Derive the unique sorted attempt scopes
   `(source_id, adapter_id, item_key)` from the exact selectors.
4. Ask `OperationalEvidenceReader` for an initial in-scope inventory. Reject
   symlinks, non-regular files, malformed names, traversal-shaped IDs,
   over-limit counts, and over-limit bytes before parsing content.
5. Read each named metadata artifact once, hash those exact bytes, and parse
   from that same byte string. Read each required payload once and check its
   tagged checksum. Recompute API raw-record and request fingerprints where
   their canonical inputs are stored.
6. Resolve every operational observation's RFC 6901 pointer against the
   checked bounded JSON payload. Require exact canonical `value_json` and
   `json_type`. A pointer mismatch is not repaired by trusting the extraction
   file.
7. Capture the exact temporal material for all scopes and the inclusive cutoff
   in one SQLite read transaction. Compare its attempt membership and governed
   row fields with the captured source material.
8. Capture a final source-store inventory and rehash every selected metadata
   artifact. If in-scope membership or selected bytes changed during the
   operation, refuse rather than presenting a mixed view.
9. For each canonical target, independently select the maximum occurrence
   satisfying `received_at <= as_of` by
   `(received_at, attempt_started_at, ingestion_run_id, sweep_position,
   attempt_id)`. No source time participates.
10. Resolve binding and interpretation at the selected occurrence's exact
    `received_at`. Invoke the accepted semantic facade with the exact variable,
    source selector, and cutoff; require it to carry the same occurrence and
    pinned knowledge revisions. Any disagreement is a refusal, not a winner
    choice.
11. Derive coverage rows, staleness, optional freshness finding, independent
    assurance axes, target outcomes, and canonically ordered issues.
12. Build all nested contracts through normal validation, serialize the
    snapshot without `selection_digest`, compute the digest, and construct the
    final snapshot through normal validation.
13. Rebuild the complete outer result from plain content and independently
    rederive every field, index, order, issue, and digest before returning it.

The function accesses no execution clock. Its answer depends only on the
explicit request and injected selected stores/revisions.

### 9.1 Read-view consistency and TOCTOU

The initial/final inventory fence detects ordinary concurrent append or
mutation in the relevant scope. Parsing and hashing the same in-memory bytes
prevents a metadata file from changing between a hash read and parse read.
All derivation uses the captured bytes, never an ambient reread.

This is not an operating-system snapshot and does not defeat a malicious
filesystem capable of adversarial races. The existing source store assumes an
honest single writer. A stronger claim would require a filesystem snapshot,
transactional evidence store, signed transparency log, or hardware-backed
attestation, none of which EA-001 introduces.

## 10. Temporal selection, clocks, freshness, gaps, and coverage

### 10.1 First authoritative selection axis

V1 uses only `ingestion_received_at`, the accepted receipt axis. An occurrence
is eligible exactly when its aware `received_at <= as_of`. The cutoff is
inclusive and normalized to UTC. Selection order is exactly:

```text
(received_at,
 attempt_started_at,
 ingestion_run_id,
 sweep_position,
 attempt_id)
```

with the lexicographically greatest tuple selected. This restates the accepted
TS-001 latest-observed rule; it does not introduce recency ranking by filename,
record ID, authority, or wall-clock execution time.

Attempt coverage uses the accepted coarser exact scope
`(source_id, adapter_id, item_key)` because failed attempts have no property,
subject, or extraction-route identity. An attempt is inside the cutoff when
its `effective_wall_time <= as_of`; successful responses use `received_at`,
and failures without a response use `finished_at`.

### 10.2 Windows

Arbitrary start/end windows are not supported initially. A maximum staleness
threshold, if approved, is only an assessment-input admission rule over the
selected latest occurrence. It does not change membership, search backward,
or imply persistence. General windows require separate policy design for
boundary inclusion, occurrence density, coverage, and cross-clock meaning.

### 10.3 Source-native clocks

Every source time marker and clock segment is preserved verbatim. Source time
does not select or reorder evidence in v1.

- A wall-clock marker is scoped by its declared basis.
- A monotonic domain is at least
  `(source_id, adapter_id, clock_id, clock_segment_id)`.
- An unavailable marker remains unavailable.
- Equal numeric values in different domains are not comparable.
- A monotonic decrease is only an observed decrease/possible reset flag.

Even two aware wall-clock values are not assumed synchronized. There is no
implicit offset, drift, uncertainty, or mapping. Any request that requires
cross-domain ordering or simultaneity is rejected before I/O with
`EA_TIME_COMPARISON_UNSUPPORTED`.

### 10.4 Repeated content and distinct occurrences

Byte-identical responses may reuse one raw record and payload. Their distinct
`AcquisitionAttempt` and `TemporalOccurrence` rows remain distinct selection
candidates. Deduplication occurs only in carried material storage: the shared
raw envelope, payload descriptor, and extraction result appear once and are
referenced by strict indices. Occurrences are never deduplicated by checksum,
value, or pointer.

### 10.5 Empty, omitted, failed, and quarantined evidence

For each attempt in scope:

| Source/temporal fact | Coverage classification | Selection meaning |
| --- | --- | --- |
| failed acquisition | `acquisition_failed` | no value manufactured |
| quarantined raw record | `quarantined` | no value admitted |
| successful, zero observations | `empty_snapshot` | not null, deletion, or unchanged |
| successful, observations exist, exact property absent | `snapshot_without_property` | property omitted in that snapshot |
| exact property occurrence exists | `property_observed` | point observation only |
| attempt has neither extraction nor quarantine | `extraction_incomplete` refusal | no snapshot issued |
| raw attempt exists but temporal event is absent | `temporal_occurrence_absent` refusal | projection cannot substantiate selection |

The snapshot carries exact attempt indices, not counts alone.

If the latest applicable attempt after the selected occurrence is failed,
quarantined, empty, or omits the exact property, the older occurrence remains
the deterministic latest observation but the target gains the incomplete
issue `incomplete_coverage`. An exceptional attempt earlier than the selected
occurrence remains disclosed and does not by itself make current coverage
incomplete. This is assessment-input admission policy, not a claim that the
source should have produced a value.

### 10.6 Freshness and gaps

Staleness is exact `as_of - received_at` in canonical decimal seconds. If the
request declares a maximum staleness, equality passes and a greater value
produces `exceeds_declared_threshold` plus the incomplete issue
`stale_evidence`. The threshold is caller policy, not a model assertion or
sensor-quality verdict.

No polling cadence or continuity contract exists. Therefore elapsed time,
missing attempts, or sparse observations cannot be labeled a physical “gap.”
Every coverage summary states
`cadence_gap_assessment="not_assessed_no_cadence_contract"`. Missing stored
artifacts or disagreement between exact source and temporal memberships is an
integrity/coverage failure, which is a different concept.

### 10.7 Late evidence and replay

A later appended attempt may have `received_at <=` an old cutoff. Re-running
selection against the current store must then produce the result for the new
membership and ordinarily a different digest. It does not rewrite the old
snapshot.

Store-bound revalidation has two explicit modes:

- `exact_current` requires current in-scope membership equal the frozen
  membership; an addition returns `membership_changed`.
- `frozen_membership` rechecks only the named frozen artifacts and selection;
  it may return `valid_for_frozen_membership` while separately disclosing that
  the current store is a strict superset. It never claims the old result is
  still the current latest selection.

## 11. Provenance closure and mechanical/declarative links

### 11.1 Exact operational chain

For every selected or coverage occurrence, the store-bound verifier traces:

```text
EvidenceSelectionTarget
  -> SourceSelector(subject, property)
  -> TemporalOccurrence
  -> TemporalAttemptEvent
  -> AcquisitionAttempt
  -> IngestionRun
  -> RawRecord
  -> checked raw payload bytes
  -> ExtractionResult or QuarantineRecord
  -> ApiExtractionManifest
  -> OperationalObservation
  -> RFC 6901 pointer resolved in checked payload
  -> BindingResolver at occurrence.received_at
  -> InterpretationResolver at occurrence.received_at
  -> requested VariableAnchor / owning EntityAnchor
  -> exact LoadedModel mrv_
  -> accepted semantic-compatibility result
```

### 11.2 Mechanically checkable links

The following are mechanically checkable with the captured material:

- artifact filename grammar and logical ID equality without accepting a
  caller path;
- metadata strict-schema reconstruction and hidden-extra rejection;
- exact stored byte count and SHA-256 for every carried metadata artifact;
- raw payload bytes against `payload_checksum` and immutable reference;
- API raw record ID from exact source, item, and payload checksum;
- request fingerprint from sanitized origin plus canonical request;
- exact attempt/run/source/adapter/item/endpoint links;
- exact extraction/raw/manifest/observation links;
- extractor identity equality between extraction envelope and manifest;
- JSON Pointer resolution and exact canonical JSON value/type equality;
- occurrence ID from attempt and observation IDs;
- governed occurrence fields against attempt and observation content;
- exact raw-attempt membership against temporal projection membership;
- exact binding and interpretation locator, instant, revision, and result;
- requested variable and entity ownership against the loaded model; and
- semantic result selector, occurrence, cutoff, and all three knowledge
  revisions.

### 11.3 Links that remain declarations or limitations

The following are not mechanically established:

- that the source, transport peer, adapter, extractor, binding authority, or
  interpretation authority was honest or correct;
- that a persisted extractor name/version corresponds to a particular binary;
- that `config_fingerprint` can be recomputed, because the complete extractor
  configuration is not generally persisted;
- that subject naming chosen by an adapter is physically correct;
- that the source-time marker is accurate or comparable to another clock;
- that an observation describes the requested real object;
- that selected evidence is complete relative to events the source never
  exposed; or
- that any physical state or occurrence followed.

The snapshot labels the extractor configuration guarantee
`declared_fingerprint_not_recomputed`. Introducing configuration identity is
explicitly excluded from EA-001.

## 12. Canonicalization and assessment-input digest

### 12.1 No durable selection identity

V1 defines no `EvidenceAnchor`, record prefix, minter, ledger, or revision. A
`selection_digest` is a content fingerprint, not a durable identity. Two
byte-identical canonical snapshots have the same digest because they state the
same captured input, not because they are one physical assessment event.

### 12.2 Canonical representation

Canonical snapshot bytes are UTF-8 JSON with:

- object keys sorted by Unicode code point;
- compact separators `,` and `:`;
- `ensure_ascii=False`;
- no NaN or infinity;
- UTC datetimes rendered with exact `+00:00`, never `Z`;
- no implicit type coercion;
- exact stored `value_json` strings preserved as strings, not reparsed for the
  snapshot encoding;
- tuples encoded as arrays in their validated canonical order; and
- `selection_digest` omitted from the digest input.

The canonicalizer must consume a fully validated model and reject unknown
types. It must not hash `model_dump(mode="json")` if doing so would change the
accepted timestamp representation. Golden tests must compare the exact bytes,
length, and SHA-256.

### 12.3 Complete digest input

The digest input includes, in exact field order before key sorting:

1. snapshot and policy schema versions;
2. all normalized request fields and targets;
3. exact model, binding, and interpretation revision objects including ordered
   memberships;
4. source material, every artifact descriptor, and each parsed metadata
   object;
5. temporal schema/projector versions, scopes, rows, clock openings, and
   logical material digest;
6. complete binding, interpretation, and semantic results;
7. all selection rows, coverage indices, assurance findings, and issue rows;
8. fixed ordering and limit constants; and
9. the digest algorithm token `sha256`.

The final value is `sha256:` plus the lowercase SHA-256 of those canonical
bytes.

Changing any target, locator, variable, cutoff, threshold, policy/version,
revision/membership, source artifact byte or digest, payload checksum,
attempt/occurrence/coverage membership, provenance fact, interpretation,
binding, semantic result, result order, or issue changes the canonical input
and therefore the digest, except for the ordinary cryptographic collision
assumption.

### 12.4 Ordering and deduplication

- Targets: `selection_key`.
- Scopes: `(source_id, adapter_id, item_key)`.
- Source artifacts: fixed kind rank, then `logical_id`.
- Attempts: complete accepted `AttemptOrderKey` ascending.
- Temporal occurrences: complete source/property key, then
  `received_at`, then `AttemptOrderKey`, then `occurrence_id`.
- Knowledge results: target order.
- Issues: normative issue-code rank, then target index, then bounded detail.

Duplicate targets, attempt IDs, occurrence IDs, descriptors, or membership
indices reject. A shared payload/extraction is stored once in source material
and cited by multiple indices; this is representation deduplication only.

### 12.5 What the digest proves

Given an independently retained expected digest, recomputation detects
ordinary mutation of the snapshot. Store-bound revalidation additionally
checks named current bytes. Without an independently trusted expected digest
or source store, an attacker can replace both snapshot and digest; pure
recomputation then proves only internal self-consistency.

The digest is not a signature, MAC, timestamp, notary receipt, identity,
authority endorsement, or proof of physical truth. EA-001 introduces no keys,
PKI, transparency service, remote attestation, or trusted time.

## 13. Store-bound and store-independent assurance

### 13.1 Assurance matrix

| Check | Snapshot construction with stores | Revalidation with stores | Pure snapshot validation |
| --- | ---: | ---: | ---: |
| strict Pydantic reconstruction | yes | yes | yes |
| snapshot canonical digest | yes | yes | yes |
| match separately supplied expected digest | optional | optional | optional |
| raw payload bytes vs checksum | yes, bytes read once | yes, bytes reread | no: `not_rechecked` |
| metadata stored bytes vs carried file digest | yes | yes | no: only bound by snapshot digest |
| field pointer vs raw JSON | yes | yes | no: raw bytes absent |
| source/temporal membership equality | yes | yes | no |
| temporal row presence in SQLite | yes | yes | no |
| selected knowledge stores equal pins | yes | yes | no; revision contracts only |
| deterministic selection derivation from carried material | yes | yes | yes |
| current store has later evidence | final inventory only | disclosed explicitly | unknowable |
| source/sensor correctness | no | no | no |
| physical occurrence | no | no | no |

### 13.2 Pydantic versus evidence-store verification

Pydantic reconstruction checks types, shapes, exact union arms, invariants,
indices, revision formulas available from carried memberships, and canonical
derivation. It does not open the source store. A `payload_checksum` field is a
claim about absent bytes until store-bound code actually reads those bytes.

Likewise, a carried model revision can be arithmetically coherent without
proving that the current model directory contains it. The store-bound facade
uses the explicitly injected, fully validated loaded revisions. Pure snapshot
validation uses the carried revisions and labels store checks as not rerun.

### 13.3 No raw payload embedding

Snapshots carry payload descriptors, checksums, exact byte counts, parsed
metadata, and selected observation values; they do not carry complete raw
payload bytes. This keeps results bounded and avoids multiplying sensitive or
large source content. A later verifier that needs byte assurance must receive
the evidence store. A caller that needs a self-contained evidence package is a
different export/archive milestone with separate security and retention
requirements.

## 14. Query, status, issue, and error vocabulary

### 14.1 Exact result issue codes and order

`EvidenceSelectionIssueCode` is the following literal union in this exact
normative order:

1. `unsupported_evidence_family`
2. `selection_limit_exceeded`
3. `evidence_unavailable`
4. `evidence_store_changed_during_read`
5. `checksum_mismatch`
6. `provenance_not_closed`
7. `observation_content_mismatch`
8. `extraction_incomplete`
9. `temporal_store_unavailable`
10. `temporal_occurrence_absent`
11. `temporal_projection_inconsistent`
12. `incompatible_revisions`
13. `none_before_cutoff`
14. `binding_unresolved`
15. `binding_conflicted`
16. `interpretation_not_established`
17. `semantic_compatibility_not_established`
18. `incomplete_coverage`
19. `stale_evidence`

Codes 1–12 are refusals because the captured evidence or knowledge plane
cannot support a trustworthy snapshot. Codes 13–19 are incomplete
conditions that may be bound into a snapshot. If a lower store is unavailable,
that is never rewritten as `none_before_cutoff`.

`binding_unresolved` covers accepted nonpositive binding states other than
conflict while the exact `ResolutionResult.status` remains carried.
`binding_conflicted` covers `ambiguous` or `conflicted` positive competition.
`interpretation_not_established` similarly preserves the three independent
dimension statuses. `semantic_compatibility_not_established` never replaces
the detailed accepted ES-001 findings.

### 14.2 Result precedence

The outer status is derived, never caller supplied in effect:

| Condition | Status | Snapshot |
| --- | --- | --- |
| any issue 1–12 | `refused` | absent |
| no refusal; any issue 13–19 | `incomplete` | present |
| no issue | `complete` | present |

Every issue that applies is disclosed in canonical order; precedence chooses
the outer status only and never hides a lower issue.

### 14.3 Typed errors

The public exception tree is limited to:

```text
EvidenceAssuranceError
├── EvidenceAssuranceConfigurationError
└── EvidenceAssuranceQueryError
```

Construction with wrong dependency types is configuration misuse. Malformed
request shape or non-strict inputs are query misuse. Expected domain absence,
storage unavailability, checksum mismatch, lifecycle conflict, and incomplete
evidence are structured result issues, not raw filesystem/SQLite exceptions.
Messages are bounded and contain no absolute path, credential, payload, or
secret.

`EvidenceAssuranceQueryError.error_code` is exactly:

```text
EA_REQUEST_INVALID
EA_SELECTION_POLICY_INVALID
EA_TIME_COMPARISON_UNSUPPORTED
EA_REQUEST_LIMIT_EXCEEDED
```

These distinguish an invalid policy, an unsupported clock comparison, and a
request whose target count exceeds the public bound. By contrast,
`selection_limit_exceeded` is a structured refusal discovered only after a
valid bounded request finds more in-scope stored material than the capture
limits permit.

In plain language these are the distinct “invalid selection policy” and
“unsupported time comparison” refusal paths requested by the architecture;
their machine vocabulary remains the exact error codes above.

## 15. Historical replay and backward compatibility

### 15.1 Existing records remain untouched

EA-001 requires no migration and adds no field to `RawRecord`,
`AcquisitionAttempt`, `ExtractionResult`, `TemporalOccurrence`, binding or
interpretation records, model records, or accepted upper results. Existing
source evidence, temporal projections, ledgers, model memberships, canonical
bytes, IDs, and revisions remain unchanged.

The proposed lower read material wraps current contracts and exact stored
bytes. It does not rewrite them. Historical source artifacts whose current
contracts can still read them may be selected; unsupported legacy forms return
`unsupported_evidence_family` rather than fabricated closure.

### 15.2 Knowledge replay

Historical selection requires the caller to load explicit model, binding, and
interpretation memberships and pin their exact revision IDs in the request.
No knowledge-time lookup and no “revision current at cutoff” inference is
introduced. `recorded_at` remains audit metadata, never the evidence cutoff.

### 15.3 Snapshot replay

Pure replay reconstructs the snapshot and digest from carried material. It
does not access a current store and reports `store_byte_check="not_rechecked"`.
Store-bound replay uses either exact-current or frozen-membership mode from
Section 10.7. A current store superset never silently retargets the old
selection.

### 15.4 Pre-EA behavior

All accepted public APIs and results remain valid and retain their documented
raw-authenticity limitation. EA integration is opt-in and occurs only in a
separately owner-gated slice. No existing CN, BH, or ST conclusion is
retroactively upgraded merely because the EA package exists.

## 16. Threat model and adversarial acceptance matrix

### 16.1 Threat model

EA-001 defends against accidental corruption and hostile caller-provided
serialized material within the process boundary, including:

- forged Pydantic instances and nested object graphs;
- replaced, missing, malformed, duplicated, or reordered metadata files;
- payload/checksum, raw ID, attempt, observation, pointer, revision, cutoff,
  selector, policy, or result substitution;
- mixed source, adapter, item, clock, binding, interpretation, or model axes;
- path traversal, symlinks, absolute-path leakage, oversized material, and
  unbounded selection;
- temporal projection/source-store disagreement and ordinary concurrent
  changes during capture; and
- filesystem and hash-seed nondeterminism.

EA-001 does not defend against a compromised process, kernel, filesystem
administrator, SHA-256 break, forged external source, dishonest declared
authority, compromised extractor binary, or absent trusted-time/signature
infrastructure. It must not state otherwise.

### 16.2 Executable adversarial acceptance matrix

| ID | Required executable acceptance |
| --- | --- |
| A01 | Baseline construction rechecks exact payload bytes and closes attempt/run/envelope/extraction/observation links. |
| A02 | Mutating a selected payload without its checksum returns `checksum_mismatch`; changing payload and carried checksum cannot pass against the store. |
| A03 | Mutating metadata bytes after snapshot creation fails store-bound artifact revalidation. |
| A04 | A forged `RawRecord` ID, immutable reference, API locator, request fingerprint, or attempt link returns `provenance_not_closed`. |
| A05 | RFC 6901 missing pointer, invalid escape, wrong array index, changed `value_json`, or wrong `json_type` returns `observation_content_mismatch`. |
| A06 | Extraction outer/manifest extractor or raw-ID disagreement fails closed. |
| A07 | Missing extraction and missing quarantine after a committed success returns `extraction_incomplete`. |
| A08 | Failed acquisition, quarantine, empty snapshot, and omitted property remain four distinct ordered coverage cases. |
| A09 | A raw attempt missing from temporal material returns `temporal_occurrence_absent`; it never becomes no observation or an ordinary incomplete-coverage case. |
| A10 | A temporal occurrence with changed attempt, raw, checksum, observation, locator, receipt, value, type, unit, or source-time fields returns `temporal_projection_inconsistent`. |
| A11 | Duplicate raw content under distinct attempts produces distinct occurrences; shared payload material appears once. |
| A12 | `received_at == as_of` is included; one microsecond later is excluded. |
| A13 | Equal receipt times use the complete accepted `AttemptOrderKey`; reversed file order and hash seeds do not change the selected occurrence. |
| A14 | Naive cutoff, boolean index/count, coercible scalar, duplicate target, noncanonical target order, or unknown policy field rejects before I/O. |
| A15 | Source-native timestamps never change receipt-axis selection. A requested source-time comparison fails before I/O with `EA_TIME_COMPARISON_UNSUPPORTED`. |
| A16 | Same `clock_id` in different source/adapter or segment domains is not treated as a shared clock. |
| A17 | An in-scope append or mutation across the inventory fence returns `evidence_store_changed_during_read`; derivation never mixes rereads. |
| A18 | Counts or bytes over fixed limits return `selection_limit_exceeded` before unbounded allocation. |
| A19 | Caller-controlled paths, `..`, separators, symlinks, devices, sockets, and unexpected names are rejected; diagnostics are path-free. |
| A20 | Exact loaded model, binding, or interpretation membership differing from a request pin returns `incompatible_revisions`. |
| A21 | Binding unresolved, bound elsewhere, ambiguous, or conflicted remains distinct and carries the exact accepted result. |
| A22 | Interpretation nonpositive in any dimension remains distinct from checksum/provenance failure. |
| A23 | Semantic token/value incompatibility remains distinct from content integrity and physical truth. |
| A24 | A no-observation target produces a digestible `incomplete` snapshot with `none_before_cutoff`; store failure produces `refused`. |
| A25 | Exact threshold equality is admitted; greater staleness yields `stale_evidence` without changing the selected occurrence. |
| A26 | Without a threshold, age is disclosed and no freshness judgment is invented. |
| A27 | No cadence contract always yields `not_assessed_no_cadence_contract`; elapsed time cannot manufacture a gap. |
| A28 | `model_construct`, `model_copy`, hidden extras, wrong union arms, cycles, stale IDs, bad indices, duplicate indices, and result substitution are rejected at every public result boundary. |
| A29 | A changed target, cutoff, policy, revision, artifact, occurrence, issue, order, or scalar changes the canonical bytes and digest. |
| A30 | UTC canonical bytes contain `+00:00`, not `Z`; filesystem and hash-seed permutations produce identical snapshots. |
| A31 | Pure validation of a genuine snapshot reports `not_rechecked` for source bytes; it never upgrades itself to a store-bound guarantee. |
| A32 | Pure validation with no separately supplied expected digest states self-consistency only; replacing snapshot and digest is not called detected. |
| A33 | Exact-current revalidation detects late in-scope evidence; frozen-membership revalidation can check named old bytes but cannot call them current latest. |
| A34 | Store-bound result creation performs no source network access, write, connector invocation, extraction rerun, model mutation, or clock read. |
| A35 | Package import tests preserve every forbidden direction and prove no dependency on transition/flow assessment or upper evaluators. |
| A36 | Public contract equality pins exact methods, fields, literal order, `__all__`, canonical ordering, and error tree. |
| A37 | Existing historical model, binding, interpretation, temporal, source, and accepted artifact hashes remain unchanged. |
| A38 | No result field or documentation equates integrity with sensor correctness, source authority, physical state, transition, flow, causality, safety, diagnosis, or action. |
| A39 | Cross-row substitution of source, adapter, item, subject, property, cutoff, policy, or revision material rejects; a valid multi-source request retains each exact scope without cross-use. |
| A40 | Duplicate JSON keys, non-finite values, malformed UTF-8, ambiguous pointer escapes, and bounded-parser limit violations cannot produce a content-matched observation. |

## 17. Owner-gated slices, exclusions, limitations, and downstream use

### 17.1 Slice A — lower read-material prerequisites

Separately authorize, if the final design is accepted:

- public operational evidence material-reader contracts in `data_sources`;
- exact stored-file digest, path hardening, inventory fence, payload checksum,
  and pointer-content verification;
- one-transaction bounded `TemporalSelectionMaterial` in `temporal_state`;
- exact source/temporal parity tests; and
- preservation of every current contract and stored artifact.

No EA facade, upper selection, assessment, fixture, or ledger change belongs in
Slice A.

### 17.2 Slice B — evidence selection component

After Slice A acceptance, separately authorize:

- the chosen package name;
- request, snapshot, assurance, issue, digest, and revalidation contracts;
- `EvidenceAssuranceQueries` and pure snapshot validation;
- exact binding, interpretation, model, and semantic pin coherence;
- complete hostile reconstruction and deterministic reproduction; and
- historical replay without persistence.

No existing evaluator consumes the result in Slice B.

### 17.3 Slice C — separately gated integration

After Slice B acceptance, a separate proposal may integrate the snapshot as an
optional mandatory input to selected existing evaluations. It must demonstrate
one shared carried snapshot, no re-selection, and no changed CN/BH/ST meaning.
Transition and flow assessment remain outside this slice. If integration is
not needed to validate the foundation, Slice C should be absent.

### 17.4 Slice D — demonstration only if later justified

A synthetic demonstration requires a separate disposable rehearsal, frozen
input/digest contract, owner approval, and then a separate append/artifact
gate. The default is no Slice D: this component needs no model record, and a
read-only selection can be tested with disposable source and knowledge stores.
No authoritative fixture or ledger mutation is authorized by this proposal.

### 17.5 Explicit exclusions

EA-001 does not add:

- transition or flow assessment or physical occurrence claims;
- observation, command, calculated/inferred flow, rate, quantity,
  conservation, or balance;
- behavior expansion, state families, state-machine execution, traversal,
  causal/influence relations, diagnosis, impact analysis, safety, health, or
  correctness;
- configuration identity;
- goals, actions, recommendations, planning, optimization, or control;
- sensor/source/extractor trust certification;
- clock synchronization, inferred offsets, drift models, or cross-domain time;
- ingestion connectors, network access, extraction reruns, or UI;
- automatic model truth derived from observations;
- a new anchor, minter, record family, ledger, revision, cache, database, or
  second truth system; or
- fixture and authoritative-ledger records during design.

### 17.6 First-milestone limitations

- Only attempt-bearing operational API evidence with canonical JSON
  observations is supported. File/CAD/PDF evidence has no accepted temporal
  occurrence chain for this policy.
- Selection is independent latest per exact locator on receipt time. It has no
  continuity, cohort, interval, persistence, or cross-source ordering claim.
- One evidence-store namespace and one temporal projection participate.
- Snapshot size is bounded by 64 targets, 4,096 unique in-scope attempts,
  16,384 occurrences, 16,384 metadata artifacts, and 64 MiB total metadata
  bytes. Any exceeded bound refuses; implementations may not silently truncate.
- Complete extractor configuration and executable identity are not persisted,
  so their fingerprints are disclosed declarations, not re-proven facts.
- The inventory fence detects ordinary changes, not a malicious kernel or
  storage administrator.
- SHA-256 provides content comparison under its collision assumption, not
  signer identity or trusted time.

### 17.7 Downstream compatibility without downstream conclusions

The snapshot could later provide common input provenance for:

- transition assessment, once an owner-approved temporal cohort, continuity,
  endpoint-classification, and occurrence contract exists;
- flow measurement association and assessment, once explicit measurement,
  sign, quantity/unit, locus, continuity, and declaration-alignment contracts
  exist;
- behavior and state evaluation, by binding their already selected occurrences
  to source bytes without changing their mathematical or classification
  semantics; and
- accountable occurrence work, only after separate occurrence identity,
  authority, lifecycle, evidentiary threshold, and contradiction contracts.

EA emits none of those conclusions. A content-bound snapshot is necessary
evidence plumbing, not sufficient evidence of any real-world event.

## 18. Genuine unresolved owner decisions

Implementation is blocked until the owner resolves these questions. The lead
recommendation is shown first in each row.

| Q | Lead recommendation | Genuine alternative and consequence |
| --- | --- | --- |
| 1 | Approve EA-001 as a new read-only sibling composition component. | Reject the component and keep the current explicitly documented authenticity gap; extending temporal with upper knowledge is not recommended. |
| 2 | Approve package `backend.evidence_assurance` and public class `EvidenceAssuranceQueries`. | Choose a narrower name such as `assessment_evidence`; names must be fixed before imports and public exports become permanent. |
| 3 | Approve v1 as attempt-bearing operational API evidence only, with mandatory raw JSON Pointer/value/type checking. | A generic all-source contract would require new occurrence and field-provenance rules for CSV, CAD, and PDF and materially expands the first slice. |
| 4 | Approve the two narrow lower read seams: `OperationalEvidenceReader` and one-transaction `TemporalQueries.selection_material()`. | Without them, EA must use private paths/SQLite or combine non-atomic public reads, neither of which closes the gap honestly. |
| 5 | Approve independent latest-at-or-before receipt cutoff, no general windows, no source-time selection, and the fixed bounds in Section 17.6. | Different bounds or a window policy change canonical inputs, coverage closure, and refusal behavior and must be decided before implementation. |
| 6 | Approve an optional caller-declared maximum-staleness threshold as the only v1 freshness admission rule. | Disclose age only and remove `stale_evidence` from v1; this is simpler but cannot express a caller's immutable freshness requirement. |
| 7 | Approve a computed snapshot with `sha256:` content fingerprint, no durable identity, no persistence, and explicit external expected-digest requirement for mutation detection without stores. | A persisted ledger or signed receipt is a substantially different authority/security milestone and is not recommended now. |

Lead conclusion: the demonstrated gap warrants a small upper composition
component, but not a new evidence authority. Its strongest claim is that exact
bytes read from the injected store matched their checksums and participated in
one deterministic, revision-pinned selection. Every stronger claim remains
explicitly outside EA-001.

END OF EA-001 CODEX LEAD PROPOSAL
