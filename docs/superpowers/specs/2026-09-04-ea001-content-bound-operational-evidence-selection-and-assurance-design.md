# EA-001 — Content-Bound Operational Evidence Selection and Assurance

Date: 2026-09-04

Status: owner-resolved contract-correction candidate; implementation remains
paused pending separate owner acceptance and authorization.

Authority order:

1. the fixed owner resolutions issued after the accepted Slice B discrepancy
   stop at `b3e27cb41d9d69bf1545b50fb5aaa693ca7586f6`;
2. the fixed owner decisions in the original final-synthesis instruction;
3. this corrected final synthesis;
4. the challenger audit, where consistent with the owner decisions;
5. the Codex lead proposal, where consistent with all higher authorities;
6. accepted repository contracts and ADRs cited by those documents.

Frozen inputs were read completely and verified before synthesis:

- Codex lead proposal:
  `docs/superpowers/proposals/2026-09-04-ea001-codex-lead-proposal.md`,
  SHA-256
  `97ddef4ac9a8ee4248fa9d2ffe7e47225172bb741a0a02c5a03f78bee99dbd98`;
- challenger audit:
  `docs/superpowers/reports/2026-09-04-ea001-codex-lead-proposal-challenger-audit.md`,
  SHA-256
  `14ac3fab976aa007785b2876a035a636306b1ad55ef0a236f12e675977353b81`.

The owner accepted the Slice B preimplementation discrepancy stop at
`b3e27cb41d9d69bf1545b50fb5aaa693ca7586f6` and its report at SHA-256
`cc5999e2d1f4d7191b4c4dba047f4420793f86a03f7b7cbe1801116dde486574`.
The owner then authorized this bounded design-contract correction only. No
Slice A repair or Slice B implementation is authorized by this document.

Verified design baseline:

- `main` and `origin/main` resolve to
  `539f954fa759c9e20c167775b2ac906a8c867c85`;
- the authoritative model contains exactly 36 records at
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- authoritative FRG/FLD/FLW counts are exactly `1/1/0`; and
- the accepted FL disclosure is 660,516 bytes with SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.

This design changes none of those facts.

## 1. Change log against the lead proposal

This synthesis retains the lead proposal's core recommendation—a small,
read-only sibling component—but narrows its responsibility and corrects its
temporal and consistency contracts.

| Change | Final disposition |
| --- | --- |
| Milestone name | Replaced with **Content-Bound Operational Evidence Selection and Assurance** so the title does not imply engineering assessment admission. |
| Component | Retained as `backend.evidence_assurance`, with no store, cache, database, ledger, anchor, durable identity, or revision. |
| Semantic admission | Removed completely. EA does not resolve or carry binding, interpretation, model, observation-compatibility, semantic-compatibility, constraint, behavior, state, transition, or flow results. |
| Evidence family | Narrowed to DS-004-style attempt-bearing operational API evidence. File, CSV, Excel, PDF, STEP, CAD, and other evidence families are unsupported in v1. |
| Selection interval | Replaced unbounded history-through-cutoff with a required inclusive bounded horizon, plus at most one explicitly labelled pre-horizon selected occurrence. |
| Temporal material | Split into receipt-time occurrence membership and effective-time attempt-coverage membership. |
| Cross-store guarantee | Replaced “one immutable cross-store selection” with a bounded captured-view consistency protocol using source and temporal before/after fences. |
| Freshness | Removed maximum-staleness admission and every fresh/stale/suitable verdict. EA discloses time and calculated age only. |
| Snapshot name | Uses a computed captured-evidence snapshot and `sha256:` content fingerprint, not an assessment-input identity or attestation. |
| Lower seams | Keeps two narrowly scoped additions: a DS-004 operational API evidence reader in `data_sources` and a bounded one-transaction selection-material query in `temporal_state`. |
| Issue vocabulary | Removes model, binding, interpretation, semantics, engineering suitability, freshness, and physical-occurrence codes. |
| Implementation plan | Separates lower read seams, EA composition, optional later consumer integration, and any separately gated demonstration. |

The audit reported six non-blocking observations as constraints distributed
across its raw-content, digest, API-seam, and security analysis. They are
reconciled individually here:

| NB | Audit observation | Resolution |
| --- | --- | --- |
| NB1 | RFC 6901 resolution and canonical observation comparison must be exact. | Adopted in Sections 10, 11, and A09–A11: `~0`/`~1`, array indices, `value_json`, and `json_type` are checked without coercion. |
| NB2 | Metadata must be hashed and parsed from the same byte read. | Adopted in Sections 9–11 and A08. A check-then-second-read pattern is forbidden. |
| NB3 | A captured metadata-file digest is distinct from the raw payload checksum. | Adopted in Sections 6, 10, 11, and 14. Both values and their separate guarantees are carried. |
| NB4 | Extractor identity and configuration fingerprints are declarations where full executable/configuration material is unavailable. | Adopted in Sections 6, 10, 14, and 19. EA checks stored equality and linkage but does not certify the extractor or recompute unavailable configuration. |
| NB5 | An operational-only reader must reject file/CAD/PDF routes rather than posing as a universal provenance layer. | Adopted in Sections 4, 10–12, 17 A38, and 19. |
| NB6 | Inventory scope, filesystem races, bounded allocation, and path-free diagnostics require explicit treatment. | Adopted in Sections 9, 13, 16, and 17 A24–A31. Tokens bind exact observed fields; symlink/metadata races outside the fences remain limitations. |

No non-blocking observation creates new semantic or assessment scope.

### 1.1 Owner-resolved Slice B discrepancy change log

| Resolution | Corrected contract |
| --- | --- |
| Seed-aware source fence | The unchanged `inventory_token(scope, *, horizon_started_at, as_of)` signature now requires independent source-side discovery of the latest eligible observation. When that candidate is pre-horizon, every artifact needed for its mechanical closure is included in the token. |
| Exact named-material reread | `Ds004OperationalEvidenceReader` gains only `reread_named_material(expected_material)`. It reconstructs before I/O and rereads exactly the carried logical artifact set without accepting paths or claiming current membership. |
| Exact public result contracts | Sections 11 and 12 now pin all support/result fields, types, invariants, carry-once rules, literal order, exception fields, and exact package exports. |
| Cross-clock vocabulary | `EA_TIME_COMPARISON_UNSUPPORTED` and the requested-cross-clock A21 behavior are removed. V1 has no such input or method; altered `source_time_use` is `EA_SELECTION_POLICY_INVALID`. |

These are bounded contract corrections. They add no architecture layer,
semantic or assessment responsibility, persistence, durable identity,
authority, trusted time, or truth claim.

## 2. Challenger finding reconciliation

| Finding | Audit disposition | Final normative correction |
| --- | --- | --- |
| B1: unbounded history with a 4,096-attempt limit | Blocking | Every request supplies `horizon_started_at` and inclusive `as_of`. Only in-horizon material counts against material bounds; a selected occurrence before the horizon is one labelled seed. No summary or silent truncation is introduced. |
| RC1: cross-store TOCTOU/global atomicity | Required | Source and temporal memberships are fenced before and after capture. Any observed change refuses. The result is not a distributed transaction and cannot see a commit after the final fences. |
| RC2: semantic admission re-enters live temporal selection | Required | All live binding, interpretation, model-state, semantic, constraint, behavior, state, transition, and flow composition is absent from EA contracts, imports, issues, and results. |
| RC3: temporal parity requires two axes | Required | Occurrences are selected and ordered by receipt time plus the complete `AttemptOrderKey`; coverage attempts are included by `effective_wall_time`, including `finished_at_no_response`. The memberships never share one filter or count. |
| Raw-content constraints | Required implementation constraints | Same-read metadata hashing/parsing, exact payload checksum, union-wrapper closure, RFC 6901 validation, and declared extractor limitations are normative. |
| Digest/replay distinctions | Required wording constraints | A content fingerprint is not a signature, identity, authority, trusted time, or mutation detector when it and its snapshot are replaced together. |

The original audit's A01–A40 matrix is replaced by the corrected executable
matrix in Section 17. It retains the useful negative twins and adds explicit
bounded-horizon, boundary-mutation, temporal-axis, semantic-absence, file-
family, and expected-fingerprint cases. There are no unresolved blocking
findings in this synthesis.

## 3. Final architecture recommendation

EA-001 should exist as a new read-only sibling composition component named:

```text
backend.evidence_assurance
```

Its single purpose is to produce and revalidate bounded captured evidence
material for one exact operational API source/property scope under an
explicit horizon and cutoff. It composes two lower public read seams; it does
not own either store.

This boundary is smaller and safer than either rejected alternative:

- extending `temporal_state` would make a rebuildable temporal projection own
  raw-file verification and cross-store orchestration; and
- adding fields to existing upper results would duplicate selection and
  verification across consumers while leaving no single captured-material
  contract.

EA-001 introduces no second truth system. It computes a result from injected
read-only dependencies, returns it, and persists nothing. Its strongest claim
is qualified: named bytes read during a store-bound capture matched their
stored checksums and metadata, the captured source and temporal material
closed mechanically, the accepted TS-001 selection rules were applied
deterministically, and the observed memberships did not change between the
defined capture fences.

That claim is not source authentication, semantic admission, or evidence that
anything happened in the physical world.

## 4. Exact responsibility boundary

### 4.1 Owned responsibility

`backend.evidence_assurance` owns only:

- strict validation of one bounded operational evidence request;
- orchestration of one DS-004 operational API evidence reader and one
  temporal selection-material reader;
- bounded source-artifact byte/checksum checks;
- source artifact, extraction, observation, and temporal provenance parity;
- captured-view before/after consistency checks;
- deterministic selection of the accepted TS-001 latest occurrence at or
  before `as_of`;
- separate, complete-within-horizon occurrence and attempt-coverage
  memberships;
- a canonical captured-evidence snapshot and computed content fingerprint;
- store-bound assurance disclosures; and
- store-independent structural and canonical revalidation.

### 4.2 Explicitly not owned

EA does not perform, carry live, or re-export:

- binding or interpretation resolution;
- model membership or model-state composition;
- observation or semantic compatibility;
- constraint or behavior evaluation;
- state classification;
- transition or flow assessment;
- any physical occurrence claim; or
- any freshness, suitability, correctness, safety, health, diagnosis, action,
  or recommendation verdict.

Source-native `SourceSubjectRef`, `SourcePropertyRef`, `ApiSourceLocator`, and
`OperationalObservation` fields may be carried because they are already in
the operational evidence chain. They remain unresolved source-native values.
They are never bound to an entity anchor, variable anchor, state, transition,
or flow.

### 4.3 No authoritative ownership

EA owns no authoritative store, cache, database, ledger, revision, anchor,
record prefix, minter, durable identity, or truth claim. It performs no
network acquisition, connector execution, extraction rerun, write, or clock
read. `as_of` and `horizon_started_at` are explicit caller inputs.

## 5. Dependency and import map

The permitted foundational direction is:

```text
backend.data_sources  <--- backend.temporal_state
          ^                         ^
          |                         |
          +--- backend.evidence_assurance
```

`backend.evidence_assurance` may import only public DS-004 contracts,
`Ds004OperationalEvidenceScope`, and the new public reader protocol from
`backend.data_sources`, and public temporal contracts/queries from
`backend.temporal_state`, plus standard-library and Pydantic facilities.

It must not import:

- `backend.identity_binding`;
- `backend.source_interpretation`;
- `backend.model_kernel` or `backend.model_state`;
- `backend.observation_compatibility` or
  `backend.semantic_compatibility`;
- constraint, behavior, state-classification, transition, or flow facades;
- connector/vendor implementations, UI, planning, or future assessment
  packages; or
- private filesystem-store or SQLite implementation modules.

No existing foundational or upper package imports EA during Slices A or B.
Later consumers may import EA only in a separately approved integration slice;
EA never imports back into them. Architecture tests must enforce both halves.

The facade receives exactly one configured, read-only
`Ds004OperationalEvidenceReader` and one configured, read-only temporal query
dependency. Both refer to the corresponding source namespace/projection.
EA never discovers dependencies from paths, environment variables, global
registries, or “current” aliases.

## 6. Assurance taxonomy

Terms describe mechanisms, never trust or physical truth.

| Assurance name | Exact guarantee | Explicit non-guarantee |
| --- | --- | --- |
| `store_bound_payload_checksum_match` | Raw payload bytes read in this invocation hash to their exact stored `sha256:` checksum. | Signature, source identity, source honesty, later immutability, sensor correctness. |
| `captured_metadata_digest` | Exact metadata bytes read once were hashed and parsed from that same byte string. | Prior attestation or truth of the parsed statement. |
| `operational_provenance_closed` | Attempt, run, envelope, raw record, payload, extraction/quarantine, API locator, and observation references form the required exact DS-004 chain. | Correct extraction meaning, correct adapter behavior, or complete reality. |
| `observation_content_match` | The RFC 6901 pointer resolves in the checked payload and exact canonical `value_json` and `json_type` match the observation. | Engineering interpretation or correct physical measurement. |
| `temporal_occurrence_membership_reconciled` | Captured occurrence rows match governed source fields and the requested receipt-time membership. | Persistence, simultaneity, trusted clock, or physical occurrence. |
| `attempt_coverage_membership_reconciled` | Captured attempt rows match governed source fields and the requested effective-time horizon membership. | A polling promise, adequate cadence, or lifetime completeness. |
| `captured_view_consistent_at_fences` | Initial and final observed source/temporal memberships match for the defined scope and horizon. | A global atomic snapshot or immunity to a commit after the final fence. |
| `deterministic_selection_reproduced` | The fixed EA policy derives the same selected occurrence and memberships from the captured material. | Semantic compatibility or assessment suitability. |
| `content_fingerprint_match` | Canonical snapshot bytes hash to an independently supplied expected fingerprint. | Signer identity, authority endorsement, trusted time, or physical truth. |
| `store_independent_structural_revalidation` | Carried types, unions, indices, memberships, invariants, canonical bytes, and fingerprint are self-consistent. | Rechecking absent source bytes or current stores. |
| `semantic_compatibility_not_assessed` | EA emits no semantic result. | Compatibility or incompatibility. |
| `accountable_occurrence_not_assessed` | EA emits no real-world occurrence result. | Occurrence or non-occurrence. |

The unqualified words “authenticated,” “verified,” “authoritative,” “fresh,”
“stale,” “current,” and “complete” are forbidden in public EA conclusions.
Permitted formulations identify the mechanism, invocation, and boundary, such
as “store-bound payload checksum matched” and “complete within the declared
horizon.”

## 7. Bounded horizon semantics

### 7.1 Required request interval

Every request contains:

- `horizon_started_at`: an aware UTC datetime;
- `as_of`: an aware UTC datetime, inclusive;
- the invariant `horizon_started_at <= as_of`;
- one exact DS-004 source/adapter/endpoint/item/subject/property scope; and
- the fixed policy version `ea001.operational_selection.v1`.

Naive datetimes, reversed bounds, coercible scalars, hidden fields, or a
different policy fail as query misuse before store access. Accepted aware
datetimes are normalized to UTC and rendered with `+00:00`.

### 7.2 Three distinct temporal concepts

1. **Selected occurrence.** The accepted TS-001 latest occurrence at or
   before inclusive `as_of`, ordered by `received_at` and the complete
   `AttemptOrderKey`. It may predate `horizon_started_at`.
2. **Occurrence membership.** Every exact-property occurrence whose
   `received_at` lies in `[horizon_started_at, as_of]`, plus the selected
   occurrence as one labelled `pre_horizon_seed` when it predates the horizon.
3. **Attempt-coverage membership.** Every exact attempt-scope event whose
   `effective_wall_time` lies in `[horizon_started_at, as_of]`.

The selected pre-horizon seed supports only the latest-at-or-before result. It
does not assert coverage, continuity, absence, or completeness before the
horizon. It appears once even if referenced by multiple closure rows.

The source reader discovers its own latest eligible exact-property
observation at or before `as_of` using `received_at` and the complete
`AttemptOrderKey`. If that observation predates `horizon_started_at`, its one
attempt and complete source closure are added to both source inventory tokens.
This discovery is independent of the later temporal selection. The seed ID
supplied to `read_material(...)` after the temporal transaction must equal the
source-side candidate; disagreement is source/temporal parity failure.

If no observation exists at or before `as_of`, the store-bound result says
exactly `no_observation_at_or_before_as_of`. It must not be rewritten as “no
observation inside the horizon,” because those claims have different bounds.

### 7.3 Fixed limits and honest refusal

V1 retains these public material bounds from the lead design:

- one exact request scope;
- at most 4,096 attempt-coverage members inside the requested horizon;
- at most 16,384 occurrence members, including a seed;
- at most 16,384 retained metadata artifacts; and
- at most 64 MiB of retained metadata bytes.

The implementation checks counts and byte sizes before retained
materialization and uses bounded per-artifact parsing. It may stream past
out-of-horizon history to identify exact membership; out-of-horizon rows do
not consume the retained in-horizon attempt bound.

A source with more than 4,096 lifetime attempts but no more than 4,096
attempts in the requested horizon is valid. More than 4,096 attempts inside
the horizon returns `excessive_bounded_material`. The result never truncates,
samples, chooses the newest 4,096, or claims completeness. The caller may make
a new request with a narrower explicit horizon.

EA defines no temporal summary, retained checkpoint, or substitute for omitted
history. A read-fence token is an invocation-local consistency value, not a
temporal summary/checkpoint or new stored projection record.

## 8. Separate temporal memberships

### 8.1 Occurrence selection and ordering

An occurrence is eligible for selection exactly when
`occurrence.received_at <= as_of`. The selected occurrence is the
lexicographically greatest tuple:

```text
(
  received_at,
  attempt_started_at,
  ingestion_run_id,
  sweep_position,
  attempt_id
)
```

The final four fields are the complete accepted `AttemptOrderKey`. Equality at
the cutoff is included. Filenames, filesystem enumeration, record IDs,
authority, source time, and execution time never break a tie.

Occurrence membership is independently filtered by `received_at` inside the
inclusive horizon, then augmented with the one selected pre-horizon seed when
required. It preserves empty distinction between “no in-horizon occurrences”
and “no observation at or before `as_of`.”

### 8.2 Attempt-coverage membership

Attempt coverage uses the accepted coarser source/adapter/endpoint/item scope
because a failed attempt has no subject/property observation. Membership is
filtered by `effective_wall_time` inside the inclusive horizon and ordered by
the complete `AttemptOrderKey`.

- A response-bearing attempt uses its accepted `received_at` basis.
- A no-response failure uses `finished_at` and carries
  `effective_time_basis="finished_at_no_response"`.

The implementation must not infer a property, subject, receipt time, or
source-time marker for a failed attempt.

### 8.3 Honest coverage categories

Every in-horizon attempt is disclosed as exactly one of:

- `property_observed`;
- `snapshot_without_property`;
- `empty_snapshot`;
- `acquisition_failed`;
- `quarantined`; or
- `extraction_incomplete`.

The first five are preserved operational evidence conditions.
`extraction_incomplete` means required stored closure is absent and refuses
the snapshot. Failed, quarantined, empty, and omitted attempts produce
`incomplete_coverage_within_declared_horizon`; that issue reports operational
coverage only, not source quality or engineering suitability. A horizon with
no attempt members also reports incomplete coverage.

Byte-identical responses remain distinct occurrences when their attempts are
distinct. Shared raw payload material may be carried once and referenced by
strict indices, but checksums, values, or pointers never deduplicate attempts
or occurrences.

Source-time markers and clock-segment disclosures are carried verbatim. They
do not select, filter, or order evidence. Unrelated clock domains are never
compared without an explicit accepted mapping, and EA-001 defines no mapping.

## 9. Captured-view consistency protocol

EA uses this exact store-bound protocol:

1. Rebuild and strictly validate the request before I/O.
2. Capture an initial source inventory token for the exact permitted DS-004
   namespace, request scope, horizon membership, and the complete closure of
   the independently rediscovered source-side latest eligible pre-horizon
   seed, when one exists.
3. Capture an initial temporal logical inventory/watermark token for the exact
   request axes.
4. Read `TemporalSelectionMaterial` in one SQLite read transaction.
5. Derive the temporal-selected seed attempt ID from the temporal material,
   then read every named source artifact once for material capture. The source
   reader independently requires that supplied seed ID to equal its own
   source-side candidate. Hash metadata and parse its model from the same byte
   string; hash each raw payload and parse/check that same bounded payload byte
   string.
6. Verify checksums, stored artifact linkage, raw/extraction/observation
   closure, RFC 6901 content, and source/temporal parity.
7. Capture final source and temporal inventory/watermark tokens over the same
   defined fields; the source token independently rediscovers and binds its
   possible seed again.
8. Refuse with the exact changed-store issue if either final token differs
   from its initial token, if the transaction's carried logical membership
   does not equal the fenced membership, or if the source-side and temporal-
   selected seed IDs disagree. Seed disagreement maps to
   `source_temporal_parity_failure`, not a query exception.
9. Derive the snapshot only from already captured source bytes and temporal
   rows. No ambient reread participates in derivation.

### 9.1 Token contents

The source token canonically binds, for the exact request scope and interval:

- ordered logical IDs and artifact kinds;
- attempt IDs and their accepted effective-time basis/value;
- dependency logical IDs for in-horizon attempts and the possible seed;
- ordinary store-entry identity/change facts, including kind and byte count,
  sufficient for the accepted single-writer filesystem fence; and
- the fixed inventory-schema version.

It contains no absolute path, credential, secret, raw payload byte, mtime-only
claim, or unbounded directory listing. Each token invocation binds the
captured same-read file digest, payload checksum where applicable, kind,
logical ID, and byte count through the accepted member-key construction. The
material read in step 5 independently captures its own descriptors; token
bytes are not reused as material bytes. Changing an unselected artifact
outside the exact token scope is not detected and is not claimed to be
detected.

Source-side seed discovery scans older exact-scope history without retaining
all lifetime rows and without charging them to the 4,096 in-horizon retained-
attempt limit. Each candidate artifact is opened and parsed under the same
per-artifact byte/parser bounds used by ordinary capture. Candidate ordering
is deterministic and independent of filesystem enumeration. Only the greatest
eligible exact-property observation is retained, and only when it predates the
horizon. If the greatest eligible observation is already in-horizon, no
additional seed closure is added. Initial and final token calls repeat this
discovery independently, so mutation of any retained seed dependency changes
the member keys/digest or produces a typed lower refusal.

The temporal token canonically binds:

- temporal schema and projector versions;
- exact request axes and interval;
- ordered attempt-coverage IDs and logical row digests;
- ordered occurrence IDs and logical row digests, including any seed; and
- clock-segment-opening IDs needed by those rows.

The token is computed read-only for the invocation. It is not persisted,
trusted time, a database/WAL/SHM-byte digest, or a new temporal checkpoint.

### 9.2 Exact guarantee and limitation

This protocol detects defined membership/content changes across the observed
capture boundaries. It is not a filesystem snapshot, a distributed
transaction, or an atomic global present. It cannot detect a commit that
occurs after both final fences. “Matches final observed membership” means
equality with those final tokens only.

A mutation before initial capture may legitimately become part of the
captured view. A mutation between any initial fence, read, parity step, or
final fence either changes a token/parity fact and refuses, or—where an
adversarial filesystem defeats ordinary open/read identity—falls under the
explicit filesystem threat limitation. A mutation immediately after the
final fences does not retroactively invalidate the self-consistency of the
captured result, but the result may not call itself globally current.

## 10. Source provenance closure

### 10.1 Supported operational chain

For a selected observation and every in-horizon coverage attempt, the source
reader closes only this DS-004 chain:

```text
Ds004OperationalEvidenceScope
  -> AcquisitionAttempt
  -> IngestionRun
  -> RawRecord / ApiSourceLocator (when response-bearing)
  -> exact raw payload bytes read in this invocation
  -> ExtractionResult(ApiObservationsResult(ApiExtractionManifest))
     or QuarantineRecord
  -> OperationalObservation
  -> RFC 6901 pointer resolved against the same checked payload bytes
  -> TemporalAttemptEvent
  -> TemporalOccurrence (when the exact property was observed)
```

The exact `ExtractionResult.result` union wrapper is retained. EA must not
pretend that `ApiExtractionManifest` is the top-level stored extraction
record.

### 10.2 Mechanically checked links

Store-bound capture checks:

- accepted filename grammar and logical ID without accepting caller paths;
- strict reconstruction, exact union arms, and hidden-extra rejection;
- metadata byte count and SHA-256 from the same bytes parsed;
- payload bytes against the exact tagged payload checksum and immutable
  reference;
- source, adapter, endpoint, item, run, attempt, raw-record, and request-
  fingerprint links whose canonical inputs are stored;
- extraction envelope/manifest raw ID and extractor-identity equality;
- quarantine exclusivity and required success/failure shapes;
- exact subject, property, route, item, pointer, observation, and occurrence
  links;
- RFC 6901 decoding (`~0`, then `~1`), exact object/array traversal, and
  missing/invalid index rejection;
- canonical JSON `value_json`, exact `json_type`, declared unit, and governed
  occurrence fields without coercion; and
- source attempt/observation membership against both temporal memberships.

### 10.3 Declarations and limitations

Mechanical closure does not establish that the source, peer, adapter,
extractor, subject label, property label, value, unit, or clock was correct.
Extractor name/version and stored configuration fingerprint are checked for
equality where carried, but an executable binary is not identified and an
unpersisted full configuration cannot be recomputed. The exact disclosure is
`declared_extractor_identity_not_independently_reproven`.

CSV, Excel, PDF, STEP, CAD, and other file evidence reject as
`unsupported_operational_evidence`, even if some bytes are content-addressed.
They lack the accepted DS-004 attempt, API locator, property pointer, and
temporal occurrence chain required by this contract.

## 11. Contract sketches

The following names and field order are normative for v1 design. Every model
is frozen, `extra="forbid"`, and `revalidate_instances="always"`. Public
boundaries rebuild nested models from plain serialized content and reject
booleans as integers.

### 11.1 Request

```python
class Ds004OperationalEvidenceScope:
    source_id: str
    adapter_id: str
    endpoint_id: str
    item_key: str
    subject_identifier: str
    extraction_route: str
    json_pointer: str

class OperationalEvidenceSelectionPolicy:
    kind: Literal["independent_latest_at_or_before_as_of"]
    version: Literal["ea001.operational_selection.v1"]
    occurrence_axis: Literal["received_at"]
    attempt_coverage_axis: Literal["effective_wall_time"]
    source_time_use: Literal["disclosure_only"]

class OperationalEvidenceSelectionRequest:
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: UtcDatetime
    as_of: UtcDatetime
    policy: OperationalEvidenceSelectionPolicy
```

The seven fields of `Ds004OperationalEvidenceScope` together form the exact
source-native request scope. The type is owned by `data_sources`; it is made
from fields already present across `RawRecord`, `ApiSourceLocator`, and
`OperationalObservation`. It does not import a temporal or EA type. The
request has no entity, variable, model, binding, interpretation, semantic,
freshness, or assessment field.

### 11.2 Lower source contracts owned by `data_sources`

```python
OperationalApiArtifactKind = Literal[
    "ingestion_run",
    "acquisition_attempt",
    "raw_envelope",
    "raw_payload",
    "extraction_result",
    "quarantine_record",
]

class OperationalApiArtifactDescriptor:
    kind: OperationalApiArtifactKind
    logical_id: str
    byte_count: StrictInt
    captured_file_sha256: TaggedSha256
    payload_checksum: TaggedSha256 | None

class OperationalApiInventoryToken:
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: UtcDatetime
    as_of: UtcDatetime
    ordered_member_keys: tuple[str, ...]
    canonical_membership_sha256: TaggedSha256

class Ds004OperationalEvidenceMaterial:
    schema_version: Literal["1"]
    scope: Ds004OperationalEvidenceScope
    artifacts: tuple[OperationalApiArtifactDescriptor, ...]
    runs: tuple[IngestionRun, ...]
    attempts: tuple[AcquisitionAttempt, ...]
    envelopes: tuple[RawRecord, ...]
    extractions: tuple[ExtractionResult, ...]
    quarantines: tuple[QuarantineRecord, ...]
    observations: tuple[OperationalObservation, ...]

class Ds004OperationalEvidenceReader(Protocol):
    def inventory_token(
        self,
        scope: Ds004OperationalEvidenceScope,
        *,
        horizon_started_at: UtcDatetime,
        as_of: UtcDatetime,
    ) -> OperationalApiInventoryToken: ...

    def read_material(
        self,
        scope: Ds004OperationalEvidenceScope,
        *,
        horizon_started_at: UtcDatetime,
        as_of: UtcDatetime,
        selected_seed_attempt_id: str | None,
    ) -> Ds004OperationalEvidenceMaterial: ...

    def reread_named_material(
        self,
        expected_material: Ds004OperationalEvidenceMaterial,
    ) -> Ds004OperationalEvidenceMaterial: ...
```

`captured_file_sha256` is the digest of bytes seen during the capture. For a
raw payload descriptor, `payload_checksum` is the separately stored DS-004
checksum and must match those bytes. `selected_seed_attempt_id` is a plain
logical ID supplied after the temporal read; the reader independently checks
that it is the exact source-side pre-horizon candidate. Disagreement raises
`OperationalEvidenceReadError` with
`error_code="OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH"`; EA maps it to
`source_temporal_parity_failure`. The
source seam never imports `temporal_state` or EA. No path is public material.

`inventory_token(...)` automatically and independently discovers the exact
source-side latest eligible observation at or before `as_of`. It uses receipt
time and the complete `AttemptOrderKey`. When that candidate predates the
horizon, the token retains exactly its attempt, attempt run, raw envelope,
originating run when reused content requires it, raw payload, extraction
result, exact observation-bearing extraction content, and all other required
mechanical closure. Those artifacts use the same member-key, byte-count,
captured-digest, and payload-checksum rules as in-horizon material. Historical
discovery is streaming/bounded per artifact; older candidates do not consume
the retained in-horizon attempt count.

Eligibility is evaluated per successful acquisition attempt whose closed
extraction contains the exact subject/pointer observation. Distinct attempts
that reuse one raw payload remain distinct candidates and use their own
receipt/order keys; representation-level reuse of the shared envelope,
payload, extraction, and observation never collapses attempt occurrences.

`reread_named_material(...)` first converts `expected_material` to plain
serialized content and fully reconstructs every nested model before any
filesystem access. It then derives all names internally from the exact
artifact kinds/logical IDs, rereads exactly that set, hashes and parses each
metadata file from the same bounded byte string, rereads raw payload bytes,
checks their stored checksums, reconstructs the complete material, and
requires the returned material to equal the expected scope, artifacts, runs,
attempts, envelopes, extractions, quarantines, and observations. It accepts no
path and ignores unrelated artifacts, including newly added in-horizon rows.
The expected snapshot's limits of 16,384 artifacts and 64 MiB retained
metadata apply; current horizon growth and the 4,096 capture-attempt bound do
not prevent an exact named reread. Missing/unsafe/invalid bytes raise the
existing `OperationalEvidenceReadError` with the exact existing fields
`error_code` and `message` and a bounded path-free code distinguishing
`OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE` from
`OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH`. No new lower exception class
or exported name is added.

The method makes only a named frozen-material statement. Current membership
is separately observed through `inventory_token(...)`; named equality never
means current or latest.

### 11.3 Lower temporal contracts owned by `temporal_state`

```python
class TemporalSelectionInventoryToken:
    schema_version: str
    projector_version: str
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: UtcDatetime
    as_of: UtcDatetime
    occurrence_membership_sha256: TaggedSha256
    attempt_coverage_membership_sha256: TaggedSha256
    clock_opening_membership_sha256: TaggedSha256

class TemporalSelectionMaterial:
    schema_version: str
    projector_version: str
    scope: Ds004OperationalEvidenceScope
    horizon_started_at: UtcDatetime
    as_of: UtcDatetime
    selected_occurrence_index: StrictInt | None
    selected_occurrence_is_pre_horizon_seed: StrictBool
    occurrence_membership: tuple[TemporalOccurrence, ...]
    attempt_coverage_membership: tuple[TemporalAttemptEvent, ...]
    clock_segment_openings: tuple[ClockSegmentOpening, ...]
    transaction_membership_sha256: TaggedSha256

class TemporalQueries:
    def selection_inventory_token(...) -> TemporalSelectionInventoryToken: ...
    def selection_material(...) -> TemporalSelectionMaterial: ...
```

`selection_material()` performs its complete logical read in one SQLite read
transaction. `selection_inventory_token()` is the matching read-only fence
operation. Neither knows EA policy literals, model anchors, bindings,
interpretations, assessments, transitions, or flows. Both enforce the
accepted TS-001 ordering and separate memberships.

### 11.4 EA captured material

```python
CanonicalNonnegativeDecimal = Annotated[
    StrictStr,
    StringConstraints(pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$"),
]

CoverageDisposition = Literal[
    "property_observed",
    "snapshot_without_property",
    "empty_snapshot",
    "acquisition_failed",
    "quarantined",
    "extraction_incomplete",
]

class OperationalEvidenceMaterialLimits:
    schema_version: Literal["1"]
    maximum_in_horizon_attempts: Literal[4096]
    maximum_occurrence_members: Literal[16384]
    maximum_retained_artifacts: Literal[16384]
    maximum_retained_metadata_bytes: Literal[67108864]

class OperationalEvidenceIssue:
    code: OperationalEvidenceIssueCode
    detail_code: Annotated[
        StrictStr,
        StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,63}$"),
    ]
    route_index: Annotated[StrictInt, Field(ge=0)] | None
    detail: Annotated[StrictStr, StringConstraints(min_length=1, max_length=300)]

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
    coverage_disposition: CoverageDisposition

class OperationalCoverageSummary:
    attempt_route_indices: tuple[StrictInt, ...]
    property_observed_route_indices: tuple[StrictInt, ...]
    omitted_property_route_indices: tuple[StrictInt, ...]
    empty_snapshot_route_indices: tuple[StrictInt, ...]
    failed_route_indices: tuple[StrictInt, ...]
    quarantined_route_indices: tuple[StrictInt, ...]
    extraction_incomplete_route_indices: tuple[StrictInt, ...]
    completeness: Literal[
        "complete_within_declared_horizon",
        "incomplete_within_declared_horizon",
    ]

class SelectedSourceObservation:
    outcome: Literal[
        "selected_source_observation",
        "no_observation_at_or_before_as_of",
    ]
    temporal_occurrence_index: StrictInt | None
    provenance_route_index: StrictInt | None
    pre_horizon_seed: StrictBool
    selected_received_at: UtcDatetime | None
    observation_age_seconds: CanonicalNonnegativeDecimal | None
    age_basis: Literal["received_at", "not_applicable"]

class CapturedViewFence:
    initial_source_token: OperationalApiInventoryToken
    initial_temporal_token: TemporalSelectionInventoryToken
    final_source_token: OperationalApiInventoryToken
    final_temporal_token: TemporalSelectionInventoryToken
    relation: Literal["equal_at_observed_fences"]

class OperationalEvidenceAssurance:
    payload_byte_check: Literal["matched", "not_applicable"]
    metadata_same_read_check: Literal["matched"]
    provenance_closure: Literal["closed"]
    observation_content_relation: Literal[
        "exact_value_and_type", "not_applicable"
    ]
    occurrence_membership_relation: Literal["reconciled"]
    attempt_coverage_membership_relation: Literal["reconciled"]
    captured_view_relation: Literal["equal_at_observed_fences"]
    semantic_compatibility: Literal["not_assessed"]
    accountable_occurrence: Literal["not_assessed"]

class CapturedOperationalEvidenceSnapshot:
    schema_version: Literal["1"]
    request: OperationalEvidenceSelectionRequest
    fixed_limits: OperationalEvidenceMaterialLimits
    source_material: Ds004OperationalEvidenceMaterial
    temporal_material: TemporalSelectionMaterial
    provenance_routes: tuple[OperationalProvenanceRoute, ...]
    selected: SelectedSourceObservation
    coverage: OperationalCoverageSummary
    capture_fence: CapturedViewFence
    assurance: OperationalEvidenceAssurance
    issues: tuple[OperationalEvidenceIssue, ...]
    content_fingerprint: TaggedSha256
```

Complete source and temporal records are carried once. Nested rows contain
strict indices and derived scalars only. An index is nonnegative, in range,
non-boolean, unique where required, and points to the exact union arm.

`CanonicalNonnegativeDecimal` is a finite plain decimal string with no sign,
exponent, whitespace, leading zero, negative zero, or trailing fractional
zero. Age zero is exactly `"0"`. Issue detail is path-free, secret-free, and
must not contain an absolute path, URI user information, credential, or raw
exception. Snapshot issues may contain only codes 15 and 16. Any code 1–14
prevents snapshot construction.

Every model in Sections 11.1–11.5 is frozen with `extra="forbid"` and
`revalidate_instances="always"`. Before validation, every nested Pydantic
value is converted to plain Python content with explicit cycle detection and
rebuilt through its declared public type. Tuple order, complete source and
temporal closure, route indices, selected values, coverage partitions,
assurance values, issue order, canonical bytes, and the fingerprint are
recomputed. A caller cannot make a forged instance valid through
`model_construct`, `model_copy`, a subclass, a wrong union arm, or substituted
derived fields.

### 11.5 Public facade and validation results

```python
class OperationalNamedArtifactRevalidation:
    artifact_descriptor_index: Annotated[StrictInt, Field(ge=0)]
    relation: Literal["matched"]
    observed_byte_count: Annotated[StrictInt, Field(ge=0)]
    observed_captured_file_sha256: TaggedSha256

class OperationalEvidenceSelectionResult:
    status: OperationalEvidenceSelectionStatus
    request: OperationalEvidenceSelectionRequest
    snapshot: CapturedOperationalEvidenceSnapshot | None
    issues: tuple[OperationalEvidenceIssue, ...]

class OperationalEvidenceStoreRevalidationResult:
    status: StoreBoundRevalidationStatus
    membership_mode: StoreBoundMembershipMode
    snapshot_content_fingerprint: TaggedSha256 | None
    snapshot_validation_status: StoreIndependentValidationStatus
    expected_artifact_count: Annotated[StrictInt, Field(ge=0)]
    expected_provenance_route_count: Annotated[StrictInt, Field(ge=0)]
    named_source_material_relation: NamedCapturedMaterialRelation
    captured_temporal_material_relation: CapturedTemporalMaterialRelation
    source_membership_relation: ObservedMembershipRelation
    temporal_membership_relation: ObservedMembershipRelation
    named_artifact_results: tuple[OperationalNamedArtifactRevalidation, ...]
    issues: tuple[OperationalEvidenceIssue, ...]

class OperationalEvidenceSnapshotValidationResult:
    status: StoreIndependentValidationStatus
    computed_fingerprint: TaggedSha256 | None
    embedded_fingerprint_relation: EmbeddedFingerprintRelation
    expected_fingerprint_relation: ExpectedFingerprintRelation
    source_bytes: Literal["not_rechecked"]
    temporal_store_membership: Literal["not_rechecked"]
    detail_code: Annotated[
        StrictStr,
        StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,63}$"),
    ]
    detail: Annotated[StrictStr, StringConstraints(min_length=1, max_length=300)]

class EvidenceAssuranceQueries:
    def __init__(
        self,
        *,
        source: Ds004OperationalEvidenceReader,
        temporal: TemporalQueries,
    ) -> None: ...

    def select_operational_evidence(
        self,
        request: OperationalEvidenceSelectionRequest,
    ) -> OperationalEvidenceSelectionResult: ...

    def revalidate_operational_evidence(
        self,
        snapshot: CapturedOperationalEvidenceSnapshot,
        *,
        membership_mode: StoreBoundMembershipMode,
    ) -> OperationalEvidenceStoreRevalidationResult: ...

def validate_operational_evidence_snapshot(
    snapshot: CapturedOperationalEvidenceSnapshot,
    *,
    expected_fingerprint: TaggedSha256 | None = None,
) -> OperationalEvidenceSnapshotValidationResult: ...
```

The selection result carries issues exactly once. A complete or incomplete
result has `issues=()` and carries one snapshot; its snapshot carries all and
only applicable incomplete issues. A refused result has `snapshot=None` and
carries all and only applicable refusal issues in `issues`. Its request is the
strict reconstructed request. Because a refused result carries no route table,
all of its issue `route_index` values are `None`. Query misuse raises before a
result exists.

The named-artifact rows are ordered by `artifact_descriptor_index`. On a
complete named match they contain every integer from zero through
`expected_artifact_count - 1` exactly once and every row is `matched` with
both observed fields present and equal to the corresponding expected
descriptor. When the aggregate named relation is `changed`, `unavailable`, or
`not_evaluated`, the row tuple is exactly empty; the aggregate relation and
ordered issue express the failure without parsing a lower exception message.
No row repeats an expected logical ID or source object.

Store-bound revalidation does not carry the snapshot or complete source or
temporal material. Its fingerprint/counts and strict indices are sufficient
to validate its own shape without store access; issue route indices are less
than `expected_provenance_route_count`. Semantic comparison to the caller-
retained snapshot occurs only while deriving the result. Store-
independent validation likewise carries no snapshot. Its two `not_rechecked`
fields are unconditional and cannot be upgraded.

Every result reconstructs its nested content and validates without dependency
access. `EvidenceAssuranceQueries` alone performs store I/O after its input is
strictly reconstructed. Result construction and later result validation
perform no store access.

There are no aliases named `authenticate_evidence`, `verify_state`,
`assessment_evidence`, `current_evidence`, `fresh_evidence`, `history`,
`occurrence`, `transition`, or `flow`.

### 11.6 Exact exports

`backend.data_sources.evidence.__all__` remains exactly:

```python
[
    "Ds004OperationalEvidenceReader",
    "FilesystemDs004OperationalEvidenceReader",
]
```

The correction adds `reread_named_material(...)` to both exported reader
types; it adds no lower exported name. The operational source-contract
module's accepted `__all__` is unchanged.

`backend.evidence_assurance.__all__` is exactly this ordered list:

```python
[
    "EvidenceAssuranceError",
    "EvidenceAssuranceConfigurationError",
    "EvidenceAssuranceQueryError",
    "EvidenceAssuranceConfigurationErrorCode",
    "EvidenceAssuranceQueryErrorCode",
    "CanonicalNonnegativeDecimal",
    "CoverageDisposition",
    "OperationalEvidenceIssueCode",
    "OperationalEvidenceSelectionStatus",
    "StoreIndependentValidationStatus",
    "ExpectedFingerprintRelation",
    "EmbeddedFingerprintRelation",
    "StoreBoundMembershipMode",
    "StoreBoundRevalidationStatus",
    "NamedCapturedMaterialRelation",
    "CapturedTemporalMaterialRelation",
    "ObservedMembershipRelation",
    "OperationalEvidenceSelectionPolicy",
    "OperationalEvidenceSelectionRequest",
    "OperationalEvidenceMaterialLimits",
    "OperationalEvidenceIssue",
    "OperationalProvenanceRoute",
    "OperationalCoverageSummary",
    "SelectedSourceObservation",
    "CapturedViewFence",
    "OperationalEvidenceAssurance",
    "CapturedOperationalEvidenceSnapshot",
    "OperationalNamedArtifactRevalidation",
    "OperationalEvidenceSelectionResult",
    "OperationalEvidenceStoreRevalidationResult",
    "OperationalEvidenceSnapshotValidationResult",
    "EvidenceAssuranceQueries",
    "validate_operational_evidence_snapshot",
]
```

Lower source/temporal contracts are imported from their owners for type use;
EA does not re-export them or define aliases for them.

## 12. Query, status, issue, and error vocabulary

### 12.1 Exact result statuses

```python
OperationalEvidenceSelectionStatus = Literal[
    "complete_within_declared_horizon",
    "incomplete_within_declared_horizon",
    "refused",
]

StoreIndependentValidationStatus = Literal[
    "structurally_self_consistent",
    "fingerprint_mismatch",
    "invalid",
]

ExpectedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_supplied",
]

EmbeddedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_computed",
]

StoreBoundMembershipMode = Literal[
    "require_equal_final_observed_membership",
    "named_captured_artifacts",
]

StoreBoundRevalidationStatus = Literal[
    "matches_final_observed_membership",
    "valid_for_named_captured_artifacts",
    "observed_membership_changed",
    "refused",
]

NamedCapturedMaterialRelation = Literal[
    "matched",
    "changed",
    "unavailable",
    "not_evaluated",
]

CapturedTemporalMaterialRelation = Literal[
    "matched",
    "changed",
    "not_fully_observed",
    "not_evaluated",
]

ObservedMembershipRelation = Literal[
    "equal_to_snapshot_final",
    "different_from_snapshot_final",
    "not_fully_observed",
    "not_evaluated",
]
```

`complete_within_declared_horizon` requires a selected source observation,
closed captured material, and no incomplete horizon-coverage issue.
`incomplete_within_declared_horizon` means a canonical snapshot exists but no
observation existed at/before `as_of` or the operational coverage categories
inside the horizon are incomplete. `refused` means no snapshot is returned
because integrity, parity, support-family, mutation, or material-bound checks
could not safely produce one.

Selection carry-once state is exact:

| Applicable issue state | Status | `snapshot` | Result `issues` | Snapshot `issues` |
| --- | --- | --- | --- | --- |
| no issue | `complete_within_declared_horizon` | one snapshot | `()` | `()` |
| one or both codes 15–16, no code 1–14 | `incomplete_within_declared_horizon` | one snapshot | `()` | all applicable codes 15–16 in order |
| any code 1–14 | `refused` | `None` | all applicable refusal issues in order | not applicable |

`complete_within_declared_horizon` additionally requires at least one in-
horizon attempt route, every in-horizon route to be `property_observed`, and a
selected source observation. A pre-horizon seed with no in-horizon attempts is
therefore incomplete, never complete.

Store-independent validation state is exact:

| Condition | Status | Computed fingerprint | Embedded relation |
| --- | --- | --- | --- |
| fully reconstructed and all derived/canonical fields match | `structurally_self_consistent` | present | `matched` |
| structurally derivable but embedded or supplied expected fingerprint differs | `fingerprint_mismatch` | present | `matched` or `mismatched` as observed |
| reconstruction, cycle, union, index, ordering, closure, or derived-field failure | `invalid` | `None` | `not_computed` |

`expected_fingerprint_relation` is `not_supplied` exactly when the argument is
`None`; otherwise it is the strict equality result against the embedded
fingerprint, even when structural reconstruction later fails. Both store-
independent check fields are always `not_rechecked`.

Store-bound revalidation state is exact:

| Mode and condition | Status | Named material | Source/temporal membership |
| --- | --- | --- | --- |
| either mode; snapshot invalid | `refused` | `not_evaluated` | both `not_evaluated` |
| either mode; named source material changed or unavailable | `refused` | exact `changed`/`unavailable` | both `not_evaluated` |
| equality mode; named/temporal material matched and both observed memberships equal snapshot final tokens | `matches_final_observed_membership` | `matched` | both `equal_to_snapshot_final` |
| equality mode; either fully observed membership differs | `observed_membership_changed` | `matched` | each exact equal/different relation |
| equality mode; either current membership cannot be fully produced | `refused` | `matched` | at least one `not_fully_observed` |
| named mode; named source material matched, regardless of equal/different/not-fully-observed current membership | `valid_for_named_captured_artifacts` | `matched` | each exact observed relation |

In named mode, `valid_for_named_captured_artifacts` asserts only the named
source-byte/material match. `captured_temporal_material_relation` separately
reports `matched`, `changed`, or `not_fully_observed`; it is never hidden by
the outer status. The result cannot use “current” or “latest” for the older
selection when either membership relation is not equal.

For a structurally invalid or fingerprint-mismatched snapshot, store-bound
revalidation performs no I/O, sets `snapshot_content_fingerprint=None`,
both expected counts to zero, all store relations to `not_evaluated`, rows to
`()`, and returns one ordered `invalid_bounded_material` issue with no route
index. For a valid snapshot those fields equal its fingerprint, artifact
count, and provenance-route count.

`captured_temporal_material_relation="matched"` means every carried temporal
occurrence, attempt event, and clock opening is present with equal logical
content in the separately read bounded temporal material; additional current
rows affect only `temporal_membership_relation`. Missing or substituted
carried rows are `changed`. A lower unavailability or bound refusal is
`not_fully_observed`.

A stable difference from the snapshot's final membership is expressed by the
membership relation/status and is not itself a capture-mutation issue. A
token pair that changes during this revalidation uses the applicable source-
or temporal-store-changed issue and `not_fully_observed`. Lower unavailability
uses the corresponding source/temporal unavailable issue. In named mode these
issues are retained even when the outer status remains
`valid_for_named_captured_artifacts`; that status is deliberately limited to
the successful named source-material check. All result issues retain Section
12.2 ordering and are carried only in the revalidation result.
Issues already carried by the input snapshot are never copied into the store-
revalidation result; only conditions encountered by that revalidation appear
there.

### 12.2 Exact issue codes and order

`OperationalEvidenceIssueCode` is this literal union in normative order:

```python
OperationalEvidenceIssueCode = Literal[
    "unsupported_operational_evidence",              # 1
    "invalid_bounded_material",                      # 2
    "excessive_bounded_material",                    # 3
    "source_evidence_unavailable",                   # 4
    "temporal_evidence_unavailable",                 # 5
    "source_store_changed_during_capture",           # 6
    "temporal_store_changed_during_capture",         # 7
    "checksum_mismatch",                             # 8
    "provenance_closure_failure",                    # 9
    "observation_content_mismatch",                  # 10
    "extraction_incomplete",                         # 11
    "temporal_occurrence_absent",                    # 12
    "temporal_occurrence_inconsistent",              # 13
    "source_temporal_parity_failure",                # 14
    "no_observation_at_or_before_as_of",             # 15
    "incomplete_coverage_within_declared_horizon",   # 16
]
```

Codes 1–14 are refusals. Codes 15–16 are incomplete conditions that may be
included in a snapshot. `temporal_evidence_unavailable` is the temporal twin
of source evidence unavailability; it prevents a lower-store failure from
being mislabeled as occurrence absence. Issues carry only a bounded detail
code, optional strict route index, and path-free, secret-free bounded text.
They do not carry raw exceptions.

Issues are sorted by the rank above, then route index (`None` before integer),
then bounded detail code. Every applicable issue is retained; precedence
selects only the outer status.

### 12.3 Typed misuse errors

```text
EvidenceAssuranceError
├── EvidenceAssuranceConfigurationError
└── EvidenceAssuranceQueryError
```

The public error-code aliases are exactly:

```python
EvidenceAssuranceConfigurationErrorCode = Literal[
    "EA_DEPENDENCY_INVALID",
]

EvidenceAssuranceQueryErrorCode = Literal[
    "EA_REQUEST_INVALID",
    "EA_SELECTION_POLICY_INVALID",
]
```

Every exception instance has exactly the public instance fields `error_code`
and `message`. Both are strings; `message` is nonempty, path-free, secret-free,
contains no raw exception text, and is capped at 300 characters. `str(error)`
is exactly `"{error_code}: {message}"`. Configuration errors accept only the
configuration code and query errors accept only the two query codes above.

Wrong dependency types/configuration are configuration misuse. Invalid
request shape, reversed bounds, non-strict fields, unsupported selection
policy, or any alteration of fixed `source_time_use="disclosure_only"` are
query misuse and fail before I/O. V1 has no cross-clock comparison input,
method, result, or exception path. Valid but unsupported evidence, absent
evidence, too much in-horizon
material, store changes, checksum failures, and incomplete coverage are
structured results.

No public status or issue names binding, interpretation, model admission,
semantic compatibility, freshness, physical activity, engineering
correctness, or occurrence.

## 13. Canonicalization and fingerprint rules

### 13.1 Canonical bytes

The fingerprint input is the canonical UTF-8 JSON encoding of exactly:

```python
{
    "algorithm": "sha256",
    "snapshot": <all CapturedOperationalEvidenceSnapshot fields except
                 content_fingerprint>,
}
```

It uses:

- object keys sorted by Unicode code point;
- compact separators `,` and `:`;
- `ensure_ascii=False`;
- strict types and no NaN/infinity;
- UTC datetimes rendered with `+00:00`, never `Z`;
- exact canonical source `value_json` retained as a string rather than
  reparsed into the outer document;
- tuples encoded as arrays in their normative order; and
- `content_fingerprint` omitted from its own input.

The term “canonical snapshot bytes” in this contract means these complete
wrapper bytes. The nested `snapshot` value has exactly the normative snapshot
field set minus `content_fingerprint`; no other envelope or metadata is added.

The canonicalizer consumes a fully revalidated model and rejects unknown
types. It must not use a generic JSON-mode dump when that changes the accepted
datetime form.

### 13.2 Complete fingerprint input

The fingerprint binds:

1. snapshot schema and fixed EA policy version;
2. complete normalized scope, horizon, and inclusive cutoff;
3. fixed count/byte limits;
4. initial and final source/temporal fence tokens;
5. every source artifact descriptor and parsed metadata object;
6. every temporal occurrence, attempt-coverage event, and required clock
   opening;
7. all provenance routes and strict indices;
8. selected outcome, selected seed flag, time, calculated age, and age basis;
9. complete horizon-coverage categories;
10. assurance disclosures and ordered issues; and
11. the exact wrapper key/value `"algorithm":"sha256"`.

The value is lowercase `sha256:` plus SHA-256 of the canonical bytes. Any
change in a bound input changes the fingerprint except under the ordinary
collision assumption. An artifact outside the token's exact scope is not a
bound input and is not claimed to change it.

### 13.3 Ordering and deduplication

- Artifact descriptors: fixed artifact-kind rank, then logical ID.
- Attempts and attempt routes: complete `AttemptOrderKey` ascending.
- Occurrences: exact subject/property key, then `received_at`, complete
  `AttemptOrderKey`, then occurrence ID.
- Clock openings: exact clock domain, segment start order, then opening ID.
- Issues: Section 12 rank, route index, detail code.

Duplicate logical IDs, attempt IDs, occurrence IDs, indices, or unordered
membership reject. Shared payload/extraction objects may be represented once
and cited by multiple strict indices. This is representation deduplication,
not occurrence deduplication.

### 13.4 Meaning of the content fingerprint

The fingerprint is not a signature, MAC, durable identity, model record,
authority endorsement, trusted timestamp, ledger revision, or proof of
real-world truth. It does not detect replacement when an attacker replaces
both snapshot and fingerprint unless a separately retained expected
fingerprint or source store is supplied.

## 14. Store-bound versus store-independent guarantees

| Check | Store-bound capture | Store-bound revalidation | Store-independent structural revalidation |
| --- | ---: | ---: | ---: |
| strict nested reconstruction | yes | yes | yes |
| canonical bytes/fingerprint | yes | yes | yes |
| separately supplied expected fingerprint | via pure validator | via pure validator before call | optional |
| raw payload bytes vs stored checksum | yes, bytes read | yes, named bytes reread | no: `not_rechecked` |
| metadata bytes vs captured file digest | yes | yes | no: digest field only |
| RFC 6901 pointer vs raw JSON | yes | yes | no: raw bytes absent |
| source operational closure | yes | yes | structural carried closure only |
| temporal rows in SQLite | yes | yes when bounded current material can be observed; exact relation disclosed | no |
| source/temporal parity | yes | yes | carried parity only |
| before/after membership fences | yes | yes | no |
| deterministic selection from carried material | yes | yes | yes |
| content/fingerprint pair self-consistent | yes | yes | yes |
| current global store state | no | no | no |
| binding/interpretation/model/semantics | no | no | no |
| sensor/source/extractor correctness | no | no | no |
| accountable physical occurrence | no | no | no |

Store-independent revalidation first serializes the caller object to plain
content, reconstructs every nested model, rejects hidden extras/cycles/wrong
unions/boolean indices, rechecks every cross-index and derived field,
recomputes canonical bytes, and compares the embedded fingerprint. If an
expected fingerprint is supplied, it also compares that independently
retained value. With no expected fingerprint, success says only
`structurally_self_consistent`.

Store-bound revalidation additionally rereads named evidence and captures new
source/temporal fences. It proceeds in this order:

1. run the pure structural/fingerprint validator without store access;
2. when valid, call `reread_named_material(snapshot.source_material)` exactly
   once and compare its returned material to the snapshot material;
3. separately attempt initial source and temporal inventory tokens for the
   snapshot request;
4. when bounded temporal material is available, check every carried temporal
   row and required opening against it without substituting newly selected
   rows for the snapshot rows;
5. capture final source and temporal tokens when their corresponding initial
   token was available; and
6. derive only relation/status/issue rows, never another snapshot.

A missing, changed, unsafe, checksum-invalid, or structurally invalid named
artifact makes the named relation `changed` or `unavailable` and refuses both
modes. Newly added unrelated artifacts do not participate in the named reread.

`require_equal_final_observed_membership` requires both stable current token
pairs and equality with the snapshot's final observed memberships. A stable
difference returns `observed_membership_changed`; an unavailable or bounded-
inventory refusal returns `refused` with `not_fully_observed`. The result does
not claim a global current state.

`named_captured_artifacts` succeeds as
`valid_for_named_captured_artifacts` after an exact named reread even when a
stable current membership differs or either current bounded inventory cannot
be fully produced. The source/temporal membership and carried-temporal-
material relations remain separate mandatory disclosures. This status never
calls the historical selection current or latest.

Raw payload bytes are not embedded in the snapshot. A self-contained evidence
archive would be a different security, privacy, export, and retention
milestone.

## 15. Historical replay

EA changes no existing source artifact, temporal row, model record,
membership, canonical byte sequence, ID, or accepted result. It adds no
migration and does not retroactively strengthen existing upper-layer
authenticity statements.

Pure replay accepts an explicitly carried snapshot and optional expected
fingerprint. It deterministically reconstructs the same selected occurrence,
separate memberships, routes, coverage categories, assurance fields, issues,
canonical bytes, and fingerprint without store access. Its source-byte and
temporal-store checks are `not_rechecked`.

Store-bound replay operates against explicitly injected stores. A late
attempt with a receipt/effective time inside an old request interval changes
the observed membership and normally the derived fingerprint. It does not
rewrite the older snapshot. Evidence after `as_of`, or outside the exact
scope, is outside that request and is not claimed to be detected.

The policy version is part of the canonical input. A future policy version
creates a different result contract; it must not reinterpret a historical v1
fingerprint. Pre-EA callers and all accepted upper results continue to work
with their existing explicitly documented raw-authenticity limitations.

## 16. Threat model

EA-001 is designed to reject or disclose:

- forged Pydantic instances, nested objects, hidden extras, wrong union arms,
  cycles, stale IDs, and substituted derived fields;
- payload/checksum substitution, metadata replacement, and wrong artifact
  linkage;
- mixed sources, adapters, endpoints, items, subjects, properties, routes,
  pointers, horizons, cutoffs, policy versions, or temporal projection rows;
- missing, duplicated, reordered, or out-of-range membership and boolean
  indices;
- ambiguous JSON, duplicate keys, non-finite values, malformed UTF-8,
  invalid RFC 6901 escapes/array indices, and bounded-parser violations;
- caller-controlled paths, traversal, absolute-path disclosure, symlinks,
  devices, sockets, credentials, and secrets;
- oversized in-horizon material and unbounded retained allocation;
- source/temporal time-of-check/time-of-use changes visible at the defined
  fences;
- reuse of one raw record across distinct attempts/occurrences; and
- filesystem enumeration and hash-seed nondeterminism.

EA does not defend against a compromised process, kernel, SQLite engine,
filesystem administrator, SHA-256 break, dishonest source/adapter/extractor,
forged external values, or absent signature/trusted-time infrastructure.
Ordinary filesystems do not prevent malicious metadata/symlink races between
operations. The reader rejects symlinks and hashes/parses the same opened
bytes, while honestly limiting its claim to observed capture boundaries.

A post-final-fence commit is intentionally an explicit non-detection case.
The absence of detection is not evidence that no later commit occurred.

## 17. Corrected adversarial acceptance matrix

This matrix replaces the lead proposal's A01–A40 and is normative executable
acceptance coverage.

| ID | Required executable acceptance |
| --- | --- |
| A01 | A valid DS-004 selection closes attempt, run, envelope, payload, extraction, observation, temporal event, and occurrence links and returns the exact selected source observation. |
| A02 | Mutating payload bytes without changing the stored checksum returns `checksum_mismatch`. |
| A03 | Replacing payload and carried checksum cannot pass `reread_named_material`; unrelated additions and current membership beyond the capture bound do not prevent an otherwise exact named reread. |
| A04 | Metadata bytes changed between captured views—including any independently discovered pre-horizon seed dependency—produce a changed source token or typed digest refusal. |
| A05 | A forged raw record ID, immutable payload reference, API locator, request fingerprint, attempt link, or run link returns `provenance_closure_failure`. |
| A06 | Extraction envelope, `ApiObservationsResult`, manifest, raw ID, adapter, item, or extractor disagreement fails closed. |
| A07 | Missing extraction and missing quarantine after a committed success returns `extraction_incomplete`. |
| A08 | Each metadata file is hashed and parsed from the same byte read; a test double that returns different bytes on a second access cannot create a successful capture. |
| A09 | RFC 6901 `~0` and `~1` are decoded in order; malformed escapes reject. |
| A10 | Missing object member, invalid array index, changed `value_json`, changed `json_type`, or coercible equality returns `observation_content_mismatch`. |
| A11 | Duplicate JSON keys, malformed UTF-8, non-finite values, and parser-limit violations cannot yield a content match. |
| A12 | Failed acquisition, quarantine, empty snapshot, omitted property, and property observation remain five distinct ordered coverage dispositions. |
| A13 | A source attempt missing its expected temporal event returns `temporal_occurrence_absent`, never “no observation.” |
| A14 | A temporal occurrence with substituted attempt, raw, checksum, observation, subject, property, locator, receipt, value, type, unit, or source-time field returns `temporal_occurrence_inconsistent`. |
| A15 | Source and temporal attempt/occurrence sets that are individually valid but unequal return `source_temporal_parity_failure`. |
| A16 | `received_at == as_of` is eligible; one microsecond after `as_of` is not. |
| A17 | Equal receipt times use the full `AttemptOrderKey`; reversed file/row order does not change selection. |
| A18 | Occurrence membership uses receipt time while attempt coverage uses effective time; one filter or combined count cannot pass parity tests. |
| A19 | A no-response failure is included by `finished_at` with `effective_time_basis="finished_at_no_response"`. |
| A20 | Source-time values and clock segments are disclosure only and never change selection or coverage membership. |
| A21 | Final disposition of the former cross-clock request row: V1 exposes no comparison input/method/error; `source_time_use` is exactly `disclosure_only`, any altered policy raises `EA_SELECTION_POLICY_INVALID` before I/O, and source-time/clock values do not affect selection or coverage. |
| A22 | Byte-identical payload reuse under distinct attempts yields distinct temporal occurrences; carried shared payload material is indexed once. |
| A23 | A selected occurrence before `horizon_started_at` is carried once with `pre_horizon_seed=true`. |
| A24 | The pre-horizon seed does not enter attempt coverage and cannot produce a completeness claim before the horizon. |
| A25 | With no occurrence at or before `as_of`, the result is exactly `no_observation_at_or_before_as_of`, even when in-horizon failed attempts exist. |
| A26 | More than 4,096 lifetime attempts with at most 4,096 attempts inside the requested horizon succeeds without silent history loss. |
| A27 | More than 4,096 attempts inside the requested horizon returns `excessive_bounded_material`; no row is truncated or sampled. |
| A28 | Each metadata/occurrence/byte bound is checked before retained materialization; the exact fixed-limits model rejects altered, boolean, and coercible values. Seed discovery is bounded per artifact and does not charge lifetime rows to the in-horizon count. |
| A29 | Caller paths, `..`, separators, unexpected names, symlinks, devices, and sockets reject, and diagnostics expose no path or secret. |
| A30 | A source mutation before initial capture may be consistently captured; it is not falsely labelled a concurrent change. |
| A31 | Source mutation after initial source token and before source reads refuses, including mutation of the selected seed attempt, either run, envelope, payload, extraction, or observation content. |
| A32 | Source mutation during named metadata/payload reads refuses or fails same-read identity/content checks; both ordinary capture and exact named reread are injected. |
| A33 | Source mutation after reads and before final source token refuses, including source-side seed-candidate replacement. |
| A34 | Temporal mutation after initial temporal token and before/during the one-transaction read either appears coherently in both compared memberships or refuses. |
| A35 | Temporal mutation after the transaction and before the final temporal token refuses. |
| A36 | Crossed source/temporal mutations between their respective capture phases cannot yield equal false parity; changed token, material/fence disagreement, or independently discovered seed-ID disagreement refuses. |
| A37 | A mutation immediately after both final fences is not detected; the result remains limited to final observed memberships and never claims global atomic currentness. |
| A38 | CSV, Excel, PDF, STEP, CAD, and generic file-source evidence return `unsupported_operational_evidence`. |
| A39 | Import tests prove EA imports no binding, interpretation, model, observation/semantic compatibility, evaluator, state, transition, or flow package. |
| A40 | Exact public fields and `backend.evidence_assurance.__all__` equal the Section 11 pins and contain no model revision, anchor, variable, binding, interpretation, semantic, freshness, suitability, or physical-occurrence field. |
| A41 | Calculation of `observation_age_seconds` uses `as_of - received_at` exactly and changes no selection or status based on its magnitude. |
| A42 | Empty, omitted, failed, and quarantined in-horizon attempts produce the exact incomplete-coverage disclosure without becoming a source-quality verdict. |
| A43 | Missing/unavailable source evidence, changed/unavailable named material, unavailable temporal evidence, not-fully-observed current membership, no observation, and incomplete coverage remain distinct. |
| A44 | Mixed source, adapter, endpoint, item, subject, property, route, pointer, horizon, cutoff, or policy material rejects rather than merges. |
| A45 | `model_construct`, `model_copy`, hidden extras, cycles, wrong union arms, stale derived IDs, duplicate/missing/reordered indices, boolean indices, result substitution, and carry-once violations reject at every public request/snapshot/result/lower-reread boundary. |
| A46 | Replacing a snapshot and its embedded fingerprint together can remain `structurally_self_consistent`; the result does not claim mutation detection. |
| A47 | Supplying the exact independently retained expected fingerprint yields `matched`; any different expected fingerprint yields `mismatched`. |
| A48 | Store-independent revalidation marks `source_bytes` and `temporal_store_membership` exactly `not_rechecked`, carries no snapshot, and performs no I/O. |
| A49 | Reversed filesystem/row enumeration and hash seeds 1, 7, and 12345 produce identical canonical bytes and content fingerprints. |
| A50 | Store-bound selection performs no network access, connector execution, extraction rerun, store write, model mutation, environment discovery, or execution-clock read. |

All public contract tests use exact method, field, literal-order, `__all__`,
exception-tree, and canonical-byte equality rather than subset assertions.

## 18. Owner-gated implementation plan

This specification authorizes no implementation. Each slice requires a
separate owner authorization and later acceptance.

### Slice A — lower read-material seams

Only:

- the DS-004-specific `Ds004OperationalEvidenceReader` contracts and a
  read-only implementation in `data_sources`;
- exact same-read metadata hashing/parsing, raw payload checksum, RFC 6901,
  source inventory token, closure, and bounds behavior;
- the bounded one-transaction `TemporalSelectionMaterial` query and logical
  inventory token in `temporal_state`;
- separate occurrence and attempt-coverage memberships;
- source/temporal parity and bounded-horizon tests; and
- preservation/import-isolation tests.

No `backend.evidence_assurance` facade exists in Slice A.

### Slice A integrity repair — owner gated

Only after separate owner acceptance of this corrected contract, a bounded
repair may implement:

- automatic source-side latest-eligible observation discovery and complete
  pre-horizon seed dependency binding in both source inventory tokens;
- exact source-side/temporal-supplied seed-ID agreement in
  `read_material(...)`;
- `reread_named_material(expected_material)` on the existing reader protocol
  and filesystem implementation;
- focused seed-fence, named-reread, hostile reconstruction, bounds,
  determinism, no-side-effect, and preservation tests; and
- an updated deterministic lower-token/material reproduction digest if and
  only if the corrected seed-aware token changes the accepted serialization.

The repair may not add a temporal import to `data_sources`, a caller path or
seed parameter to `inventory_token`, another lower export, an EA package, a
store/schema/projector change, or any upper-layer integration. It receives its
own completion report and owner gate before Slice B may resume.

### Slice B — evidence assurance component

Paused. Only after separate owner acceptance of this corrected synthesis and
separate implementation and owner acceptance of the Slice A integrity repair:

- request, captured material, provenance routes, coverage, assurance, issue,
  result, validation, and revalidation contracts;
- captured-view orchestration and before/after fence enforcement;
- canonical snapshot and content fingerprint;
- store-bound capture/revalidation and pure store-independent validation;
- hostile reconstruction, deterministic ordering, and full matrix coverage;
  and
- preservation and clean-checkout verification.

No evaluator or upper semantic layer consumes EA in Slice B.

### Preservation and compatibility consequences

The correction changes no production byte today. A later authorized Slice A
repair keeps the existing source token type/signature and all existing source
material fields. Existing in-horizon requests without a pre-horizon candidate
retain their member-key meaning. A request with a selected pre-horizon source
candidate intentionally gains that candidate's complete closure in its token;
that corrected token digest is not byte-compatible with the previously empty
seed fence and must receive a new recorded deterministic reproduction value.

`reread_named_material(...)` is additive on the existing two exported reader
types. It adds no export, persistence, identifier, store entry, temporal row,
or current-selection claim. Pre-EA callers need not call it. No accepted
source artifact, temporal projection, model record, ledger membership,
canonical model byte, historical result, or disclosure is rewritten.

### Slice C — optional future integration proposal

Slice C is absent unless separately proposed and owner authorized. It may
specify how one existing consumer combines one already selected EA content
fingerprint/snapshot with that consumer's independently carried model,
binding, interpretation, and evaluation material without reselecting
evidence. EA itself remains free of those imports and conclusions.
Transition and flow assessment remain excluded.

### Demonstration gate

No authoritative model-ledger append is expected or authorized. Disposable
evidence stores and deterministic test material are preferred. Any committed
demonstration artifact requires a separate proposal, disposable rehearsal,
exact frozen digest, and explicit owner approval. No demo identity, record,
revision, or artifact hash is minted or frozen by this design.

## 19. Explicit exclusions and limitations

EA-001 does not add or decide:

- transition or flow evidence assessment or occurrence;
- observed, commanded, calculated, or inferred flow;
- causal/influence relations, conservation, or balance;
- behavior or constraint evaluation, state classification, state families,
  or state-machine execution;
- binding, interpretation, variable/entity admission, model composition, or
  semantic compatibility;
- configuration identity;
- source, adapter, extractor, sensor, or clock trust certification;
- clock synchronization, inferred clock mapping, drift/offset models, or a
  shared physical time axis;
- freshness, staleness, cadence adequacy, engineering suitability,
  correctness, safety, health, diagnosis, impact analysis, goals, actions,
  recommendations, planning, optimization, or control;
- new ingestion connectors, extraction reruns, network reads, or UI;
- automatic model truth derived from observations; or
- any anchor, ledger record, revision, durable selection identity, persisted
  receipt, signature, key infrastructure, or trusted timestamp.

V1 supports one exact DS-004 operational API scope per request, one source
store namespace, and its corresponding temporal projection. It has no
multi-property cohort, cross-source simultaneity, interval persistence,
continuity, sampling, aggregation, arbitrary window, fallback, ranking, or
source-time selection policy.

Captured-view fences detect only changes observable under their defined
tokens and ordinary store assumptions. They are not distributed locking or
global atomicity. Completeness is only operational membership/coverage inside
the declared horizon, not complete lifetime history or complete real-world
evidence.

Future consumers may use an independently retained EA fingerprint alongside
their own model and semantic material. Transition assessment, flow
measurement/assessment, behavior/state evaluation, and accountable occurrence
claims each require later owner-gated contracts. EA emits none of their
conclusions and this document does not design those milestones in detail.

## 20. Final owner decisions

All design questions are resolved for EA-001 v1:

| Decision | Final ruling |
| --- | --- |
| Component existence | Retain a new read-only sibling composition component. |
| Title | `EA-001 — Content-Bound Operational Evidence Selection and Assurance`. |
| Package | `backend.evidence_assurance`. |
| Persistence | None: no store, cache, database, ledger, revision, anchor, or durable identity. |
| Evidence family | DS-004 attempt-bearing operational API evidence only. |
| Semantic boundary | No model, binding, interpretation, compatibility, evaluator, state, transition, or flow composition. |
| Time boundary | Required aware-UTC inclusive bounded horizon and cutoff. |
| Selection | Accepted TS-001 latest occurrence at/before `as_of`; one labelled pre-horizon seed is permitted. |
| Source seed fence | Both unchanged-signature source token calls independently discover and bind the complete source-side pre-horizon candidate closure; the later temporal seed ID must agree. |
| Membership | Receipt-time occurrence and effective-time attempt coverage are separate. |
| Cross-store claim | Captured-view consistency at observed fences, never global atomicity. |
| Named reread | One exact, path-free `reread_named_material(expected_material)` operation; named equality is separate from current membership. |
| Cross-clock API | None. Source time is disclosure-only; altered policy is `EA_SELECTION_POLICY_INVALID`. |
| Freshness | Disclose time and calculated age only; no admission threshold or label. |
| Snapshot | Computed, deterministic, no raw payload bytes, with `sha256:` content fingerprint. |
| Results and exports | Exact fields, carry-once invariants, literal order, exception fields, and `__all__` are pinned in Sections 11–12. |
| Lower seams | One DS-004 source reader with the bounded integrity repair and one temporal material/fence seam, owned by their existing layers. |
| Sequencing | Corrected contract acceptance, then separately authorized/accepted Slice A repair, then separately resumed Slice B. |
| Integration | Optional future proposal only; not part of EA Slices A or B. |
| Demonstration | Disposable by default; any committed artifact is separately owner gated; no ledger append is expected. |

The four reported discrepancies are resolved by this candidate. The sole
remaining owner decision is whether to accept this exact corrected synthesis
and its correction report. Acceptance would approve the corrected contract
only; it would not authorize the Slice A integrity repair, resume Slice B, or
authorize integration, demonstration, fixture, ledger, or history work.

END OF EA-001 FINAL SYNTHESIS
