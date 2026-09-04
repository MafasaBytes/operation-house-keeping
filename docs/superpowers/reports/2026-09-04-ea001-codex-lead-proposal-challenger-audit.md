# EA-001 Codex Lead Proposal Challenger Audit

Date: 2026-09-04

Audited proposal:
`docs/superpowers/proposals/2026-09-04-ea001-codex-lead-proposal.md`

Expected proposal SHA-256:
`97ddef4ac9a8ee4248fa9d2ffe7e47225172bb741a0a02c5a03f78bee99dbd98`

Audit role: one bounded adversarial architecture audit. This report is an
audit of the Codex lead proposal, not an independent replacement proposal.
No proposal, implementation, fixture, ledger, or history file was modified.

## 1. Executive verdict

**Verdict: reject pending bounded corrections.**

The proposal identifies a genuine gap: store-independent upper results can be
internally coherent without proving that their carried operational observation
still matches the source bytes and bounded evidence membership that were
consulted. A read-only sibling is a reasonable direction.

The proposal is not acceptable as written for three reasons:

1. A valid long-lived source that has more than 4,096 in-scope attempts cannot
   be selected at all, because the proposal has no lower boundary, checkpoint,
   coverage summary, or selection horizon. This is a blocking feasibility
   defect, not merely a fixed-limit implementation choice.
2. The proposed source fences and one SQLite read transaction do not create
   one immutable cross-store selection. They detect some ordinary mutations,
   but do not provide a global atomic snapshot across the filesystem and
   SQLite projection. The guarantee language and A17/A33 must be narrowed or a
   real coherence protocol must be added.
3. EA is made responsible for binding, interpretation, and ES-001 semantic
   admission even though the existing semantic facade re-enters
   `model_state` and `TemporalQueries`. Without a new pure carried-result seam,
   EA cannot prove that its semantic result was derived from the captured
   selection rather than a second live read. The smallest correction is to
   keep EA as content/temporal evidence selection and leave semantic admission
   to its consumer.

Required corrections: **4**.

Blocking findings: **1**.

Non-blocking observations: **6**.

## 2. Baseline and proposal digest

The supplied baseline was independently checked:

| Item | Result |
|---|---|
| `main` | `539f954fa759c9e20c167775b2ac906a8c867c85` |
| `origin/main` | `539f954fa759c9e20c167775b2ac906a8c867c85` |
| authoritative records | exactly 36 |
| model revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FRG / FLD / FLW | `1 / 1 / 0` |
| accepted FL disclosure | 660,516 bytes |
| disclosure SHA-256 | `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b` |

The proposal was independently hashed as 72,404 bytes and 1,467 lines. Its
SHA-256 matches the expected digest exactly:

`97ddef4ac9a8ee4248fa9d2ffe7e47225172bb741a0a02c5a03f78bee99dbd98`

The working tree already contained the untracked proposal and
`.claude/settings.local.json`; no existing file was changed by this audit.

## 3. Architectural boundary

### 3.1 What is coherent

The proposed sibling placement in Sections 5.1 and 6.1 is preferable to
putting source-byte verification, binding, interpretation, model membership,
and semantic compatibility into `temporal_state` or `model_kernel`.
`docs/adr/0005-temporal-state-sqlite-projection.md` explicitly makes
`temporal_state` a sibling that reads source contracts and remains separate
from later knowledge and assessment layers. The proposal correctly preserves
that direction and forbids lower packages from importing EA.

The coherent core responsibility is:

> Produce and revalidate a bounded, content-bound selection of operational
> evidence for a caller-supplied request.

That responsibility includes source artifact closure, temporal selection,
receipt-axis ordering, explicit revision pins, and a computed digest.

### 3.2 Boundary overreach

Sections 3.2, 6.1, 8.4, 9 step 10, and 14.1 make binding resolution,
interpretation establishment, and ES-001 semantic compatibility part of the
evidence foundation. Those are not byte or temporal integrity facts.

Repository evidence:

- `backend/model_state/facade.py` owns the binding/temporal composition and
  deliberately keeps evidence available even when identity is unresolved.
- `backend/semantic_compatibility/facade.py` calls
  `ObservationCompatibilityQueries`, constructs `ModelQueries`, and resolves
  interpretations. It is an upper semantic composition layer, not a source
  evidence reader.
- `backend/observation_compatibility/facade.py` calls
  `ModelStateQueries.variable_state()`, which calls
  `BoundTemporalQueries.latest_observed()`, which calls the live
  `TemporalQueries`.

Therefore an EA implementation that invokes the existing semantic facade
after capturing material performs a second temporal selection. It cannot
honestly claim that its semantic result was derived from the carried
selection, particularly while the temporal store is changing. This also
duplicates `model_state` orchestration and turns EA into a dependency hub for
current semantic layers.

**Smallest boundary correction:** remove binding/interpretation/semantic
admission from the EA evidence foundation. EA may carry the caller's exact
source locator and variable/model revision pin, and may optionally expose
purely structural binding/interpretation revision references. A consumer may
later admit the snapshot using existing semantic facades. If semantic
admission is required in the same call, a separate owner-approved pure seam
that assesses already-carried candidates is required; it is not one of the
two proposed lower read seams.

## 4. Dependency direction and feasibility

The intended import direction in Sections 2.1, 6.3, and 6.4 is sound:

```text
data_sources -> temporal_state
EA -> data_sources, temporal_state, binding, interpretation, model and
      existing upper read-only facades
```

The following risks remain:

1. Importing `model_state` and `semantic_compatibility` is not a circular
   import today, but it makes EA depend on an upper composition chain whose
   temporal selection is not injectable as carried material.
2. The proposal says EA may import `model_state` and
   `observation_compatibility`, but its constructor takes `LoadedModel`,
   `BindingResolver`, and `SemanticCompatibilityQueries`. This is a mixture
   of lower loaded state and upper orchestration, not a minimal seam.
3. Sections 8.2 and 9 imply an `OperationalEvidenceReader` can expose every
   source artifact while v1 is operational-API-only. The reader must be
   explicitly API-scoped or it will become an accidental general provenance
   abstraction.
4. The proposal correctly forbids private filesystem/SQLite access. That
   makes the missing pure semantic seam visible rather than allowing an
   implementation to hide it through private fields.

No current repository evidence requires a new foundational import or a
second ledger. The sibling direction is feasible only after the boundary is
reduced as above.

## 5. Guarantee vocabulary accuracy

The proposal is unusually careful about its words. Sections 7, 9.1, 12.5,
13.2, and 17.6 correctly state that checksums are not signatures, that
Pydantic reconstruction is not store verification, that declared authority
is not authenticated authority, and that source correctness and physical
truth remain outside scope.

The following claims still need narrowing:

| Proposal language | Problem | Required wording discipline |
|---|---|---|
| “one immutable selection” in Sections 3.1 and 3.2 | No global transaction spans filesystem and SQLite. | “one bounded selection reconstructed from captured source material and one temporal read view” |
| “complete bounded in-scope membership” in `selection_integrity_complete` | Completeness is only relative to the selected source-store read and adopted horizon; a source may have older history beyond the cap. | Name the exact coverage horizon and say “complete within declared horizon” |
| “authoritative model revision reconstructed” | The model revision is a declared, content-derived membership supplied by the caller; it is not authenticated authority. | “requested model membership reconstructed under the model-kernel contract” |
| “verified” in output | It is safe only when qualified by the mechanism and invocation. | Keep the proposal’s qualified forms; ban bare “verified” |
| “current” in exact-current revalidation | Current means current at the final read, not a stable global present. | “matches the observed current membership at revalidation” |

The words `integrity`, `replay`, `content-bound`, and `snapshot` are usable
when qualified. `immutable` must describe the source-store write-once
assumption or a carried value, not a globally frozen multi-store view.

## 6. Blocking finding: unbounded-history selection is infeasible

**Affected proposal sections:** 3.2 item 3, 8.3, 9 steps 3 and 7, 10.1,
10.2, 10.5, 10.7, 16.2 A18/A24/A33, 17.6, and owner question Q5.

**Repository evidence:** TS-001 selection distinguishes two axes in
`backend/temporal_state/queries.py`:

- occurrence selection uses `received_at <= as_of` and the full
  `(received_at, attempt_started_at, ingestion_run_id, sweep_position,
  attempt_id)` ordering;
- attempt-quality coverage uses `effective_wall_time <= as_of`, where a
  no-response failure uses `finished_at`.

The temporal projection stores every attempt and occurrence as immutable
logical rows. It does not expose a precomputed bounded coverage summary or a
lower-bound checkpoint that can replace old attempt rows for this policy.

**Concrete failure mode:** a valid source has 4,097 attempts for one requested
scope before the requested cutoff. The proposal requires all in-scope attempts
through the inclusive cutoff, but caps material at 4,096 and provides no
starting boundary. The implementation must return
`selection_limit_exceeded`. Every later query for that source and scope also
refuses, even when the latest occurrence is otherwise valid and only one
additional attempt was added. It cannot reproduce the accepted quality
counts, because those counts depend on all effective-time attempts after the
selected occurrence. It also cannot safely drop older attempts: an older
failed, quarantined, empty, or omitted attempt can be part of the required
coverage membership, and the proposal has no trusted summary contract for
compressing it.

This is not equivalent to a harmless denial-of-service bound. It makes
ordinary long-lived sources permanently unusable under the stated v1 policy.
The proposal also cannot claim that a refused selection is merely a temporary
limit condition when there is no way to request a valid bounded subhistory.

**Smallest acceptable correction:** choose and specify one of these bounded
contracts before implementation:

1. add an explicit caller-supplied coverage lower boundary/checkpoint and make
   the policy a declared bounded horizon, returning a distinct incomplete
   coverage issue when history before that boundary is needed; or
2. add a temporal coverage-summary/checkpoint contract that is itself
   versioned, integrity-checked, and sufficient to reproduce the omitted
   quality counts, with the summary's coverage interval carried in the
   snapshot.

Either option is a real selection-horizon contract. It must not be smuggled in
as an implementation optimization. “No general windows” can remain if the
chosen horizon is a fixed, explicit retention boundary, but a query with no
lower boundary cannot honestly support a fixed maximum over arbitrary source
lifetimes.

**Acceptance invariant:** construct a source with 4,097 attempts, including
failures, quarantines, empty snapshots, omitted properties, and late
receipt/effective-time order differences. A request after the 4,096th attempt
must either (a) return a bounded result whose carried horizon and summary
reproduce every required quality component, or (b) return a typed,
documented “history outside declared horizon” result. It must not silently
drop rows, permanently refuse all later selections, or call the result
complete.

## 7. Required correction: cross-store TOCTOU guarantee

**Affected proposal sections:** 3.1–3.2, 8.2–8.3, 9 steps 4–8, 9.1,
12.5, 13.1, 16.2 A01/A03/A17/A33, and 17.6.

**Repository evidence:** `FilesystemRawStore` uses independent files and
write-once conventions. `TemporalStore` uses SQLite WAL and one-transaction
reads. ADR-0005 explicitly says SQLite/WAL/SHM bytes are outside the logical
determinism claim. There is no transaction spanning the raw filesystem and
SQLite projection. Binding, interpretation, and model revisions are also
independently loaded in memory.

**Concrete failure mode:** EA captures source inventory and metadata, then
SQLite returns a valid temporal read transaction. A projector commits a new
attempt after the SQLite transaction and before EA's final source inventory.
The source inventory is unchanged, so the fence passes; the temporal material
is internally consistent but no longer represents the source-store membership
at return time. The inverse ordering is also possible. A replacement or
append immediately after the final fence is likewise outside the claimed
view. A source filesystem fence cannot make the SQLite snapshot atomic with
it, and a SQLite transaction cannot make the filesystem reads atomic with it.

The proposal acknowledges ordinary races in Section 9.1 but still uses
“immutable selection,” “complete membership,” and “detects late evidence” in
places where only a bounded comparison between separately observed views is
available.

**Smallest acceptable correction:** either:

- narrow all guarantees to “cross-store consistency checked across captured
  views; no global atomicity or stable-current guarantee,” add a temporal
  before/after logical membership fence, and make any mismatch a refusal; or
- introduce a real coordinated snapshot/version protocol across both stores.

The first option is the minimum correction and fits the existing architecture.
It must explicitly say that a concurrent commit after the final fence is not
detected and that `exact_current` means equality with the observed final
membership, not an atomic present.

**Acceptance invariant:** inject append/replacement at each boundary:
before source capture, during metadata reads, during temporal transaction,
between temporal capture and final source fence, and immediately after the
final fence. The result must either refuse on a detected mismatch or use the
narrowed language. No test may assert a globally immutable cross-store view
without a coordinated snapshot mechanism.

## 8. Required correction: separate evidence integrity from semantic admission

**Affected proposal sections:** 3.2 items 6–7, 6.1, 8.4, 8.5,
8.6, 9 step 10, 11.1, 14.1 codes 14–19, 16.2 A20–A27, 17.2–17.3,
and owner questions Q1/Q2/Q4/Q6.

**Repository evidence:** `model_state` is already the accepted composition
of loaded model, binding resolver, and temporal queries. `semantic_compatibility`
is a later facade over observation compatibility and interpretation. Neither
facade accepts an already selected temporal occurrence as its sole input.
`SemanticCompatibilityQueries.variable_semantic_compatibility()` invokes the
lower state pipeline and can select from the temporal store again.

**Concrete failure mode:** EA captures occurrence O and temporal material M.
Between capture and the semantic call, a new occurrence O2 is projected. The
existing semantic facade selects O2, while EA carries O. EA then either:

- returns a semantic result for O2 alongside a snapshot row for O;
- rejects only after doing a second uncontrolled selection; or
- adds private/internal seams to force the facade to use O.

All three violate the proposed “one exact selection” contract or the stated
public-only dependency rule. The same issue applies to binding/interpretation
results if they are treated as assessment admission rather than independent
knowledge disclosures.

**Smallest acceptable correction:** make EA's v1 result an evidence snapshot
whose target row may contain the selected occurrence, source/temporal closure,
and exact knowledge revision pins, but no semantic admission result or
`semantic_compatibility_not_established` issue. Existing consumers may assess
the carried snapshot later. If the owner insists that EA itself perform
semantic admission, add a separately specified pure facade that consumes
already-carried public candidate/result material; do not reuse the live
`model_state` selection path.

Maximum staleness is likewise a caller admission policy, not evidence
integrity. It may remain as a caller-provided selection qualification, but its
issue must be named as “outside requested freshness threshold,” not as a
source-quality or truth verdict.

**Acceptance invariant:** mutate the temporal store after EA material capture
and before any downstream compatibility call. EA's returned snapshot must
contain only the captured occurrence, or the operation must refuse. No
semantic result may contain an occurrence absent from the snapshot's
temporal material.

## 9. Required correction: preserve exact temporal parity in the seam

**Affected proposal sections:** 8.3, 9 steps 7 and 9, 10.1, 10.5, 16.2
A08–A13, and 17.1.

**Repository evidence:** TS-001's `latest_observed()` selects occurrences by
`received_at`, while quality windows select attempts by
`effective_wall_time`. `TemporalAttemptEvent` records
`effective_time_basis` as either `received_at` or `finished_at_no_response`.
Clock segments are derived from observation source markers; zero-observation
attempts have no source-clock marker and remain acquisition-axis evidence.

**Concrete failure mode:** an attempt has a response received before the
cutoff but a later effective ordering position; a failed no-response attempt
has `finished_at` before the cutoff; or two occurrences have equal receipt
times but different `ingestion_run_id`/`sweep_position`/`attempt_id`. A seam
that filters all rows by one timestamp, orders by only receipt time, or
includes only occurrences will select the wrong occurrence or compute the
wrong failure/quarantine/empty/omitted counts. Late evidence and clock
resets expose the same simplification.

**Smallest acceptable correction:** make `selection_material()` normative
about two independent memberships:

- occurrence membership: `received_at <= as_of`, with the complete accepted
  selection order;
- attempt coverage membership: `effective_wall_time <= as_of`, with
  `finished_at` used for no-response failures and the complete
  `AttemptOrderKey`.

The seam must carry empty snapshots, omitted properties, quarantines, failed
attempts, source-time markers, clock openings, schema/projector versions, and
the exact scope. It must not collapse those into one cutoff field.

**Acceptance invariant:** a parity corpus containing equal cutoffs, late
receipt, no-response failures, clock segments/resets, empty snapshots,
omitted properties, quarantines, and byte-identical repeated responses yields
byte-identical selection and quality material through both TS-001 and EA.

## 10. Raw-content verification audit

The raw-content direction is mostly sound for the explicitly restricted v1:

- `data_sources` uses strict UTF-8 and rejects duplicate JSON keys,
  non-finite values, and parser-limit violations in
  `backend/data_sources/extractors/operational.py`.
- `OperationalObservation.value_json` is canonical extractor output, while
  the raw payload and RFC 6901 pointer remain source evidence.
- DS-004 API observations use the response envelope and pointers such as
  `/result/status/...`; the proposal correctly requires route and item
  scoping rather than treating arbitrary JSON as Moonraker semantics.
- API extraction is nested as `ExtractionResult.result.manifest`, specifically
  `ApiObservationsResult.manifest`; the proposal's chain must retain this
  union wrapper and must not pretend that `ApiExtractionManifest` is the
  top-level stored extraction file.
- Reused payloads are correctly distinct from repeated attempts and
  occurrences.

The following are required implementation constraints, but not separate
blocking findings:

1. Pointer resolution must preserve RFC 6901 `~0` then `~1` escaping, reject
   missing array indices, and compare exact canonical `value_json` and
   `json_type`.
2. The reader must hash and parse the same byte string for each metadata file;
   otherwise a replacement between separate reads remains possible.
3. The reader must distinguish stored-file digest from payload checksum. The
   current raw store checks payload bytes but does not persist a digest for
   every metadata file; EA may compute one for the captured invocation, not
   claim an older authenticated digest.
4. Extractor identity and configuration fingerprints remain declared metadata.
   The proposal correctly says the configuration cannot be recomputed when
   the configuration object is not persisted.
5. The API-only restriction must prevent CSV, PDF, STEP, and CAD artifacts
   from entering the same temporally authenticated result through a generic
   reader.

## 11. Snapshot, digest, and replay semantics

Sections 12 and 13 correctly reject treating `sha256:` as a signature,
identity, authority endorsement, trusted time, or physical truth. Full
membership carriage, deterministic ordering, strict indices, and pure
validation are compatible with the accepted model-kernel carry-once pattern.

The following distinctions must remain explicit:

- a computed digest detects mutation only against an independently retained
  expected digest or a reread source store;
- a snapshot and a digest replaced together are self-consistent, not
  mutation-detected;
- a stored artifact digest is a digest of bytes observed by the reader, not a
  durable attestation;
- a “frozen-membership” result can be valid for named material while current
  membership is a strict superset; it cannot be current-latest;
- policy-version changes alter the selection contract and digest but do not
  retroactively alter the source evidence;
- no durable selection identity is acceptable for v1, provided all output
  names it as a content fingerprint.

One wording correction is needed: Section 12.3 says changing “any ... source
artifact byte or digest” changes the digest. That is true for the carried
snapshot, but it does not mean that changing an unselected artifact is
detected unless the inventory fence includes its membership and relevant
content digest. The contract must state exactly which inventory fields are in
the fence.

## 12. Lower-layer API seams

`OperationalEvidenceReader` is a reasonable minimum source seam only if its
v1 protocol is explicitly limited to API evidence and exposes:

- one bounded source namespace;
- deterministic artifact inventory;
- same-read metadata bytes/model parse;
- payload bytes and checksum result;
- exact attempts, runs, envelopes, extraction/quarantine records;
- route and item scoping; and
- a before/after inventory token with defined coverage.

`TemporalQueries.selection_material()` is also a reasonable minimum temporal
seam, provided it is a read-only, one-transaction material query and preserves
the two-axis TS-001 rules in Section 9 of this report. It must not import EA
policy, semantic facades, variables, or model anchors.

Neither seam can provide cross-store atomicity by itself. That guarantee must
be narrowed as required in Section 7.

## 13. Security, privacy, and limits

The proposal correctly addresses path-free diagnostics, no credentials in
material, strict scalar validation, path traversal, symlinks/devices,
duplicate JSON keys, malformed UTF-8, parser limits, forged Pydantic
instances, stale IDs, mixed revisions, and bounded materialization.

Additional constraints to retain:

1. Inventory enumeration must not disclose absolute paths or unbounded
   directory contents through errors.
2. `Path.exists()` followed by a second read is not sufficient for a
   same-read guarantee; the reader must read bytes once and compare its
   observed identity/size/hash consistently.
3. Metadata substitution and symlink races remain outside an honest
   non-snapshot filesystem reader's guarantee. The proposal must say so.
4. Memory bounds must be checked before collecting all artifact bytes,
   parsed objects, or index arrays.
5. A legitimate large history must follow the explicit horizon/summary
   correction, not be silently truncated.
6. Mixed source namespaces, adapters, item keys, revisions, policy versions,
   and cutoffs must remain typed mismatches rather than being merged.

## 14. Scope honesty

The operational-API-only v1 restriction is honest and valuable. DS-004
already supplies the required attempt, response, extraction, pointer, and
canonical-value concepts. CSV, Excel, PDF, STEP, CAD, and other file evidence
must not enter this contract merely because a raw payload exists. Their
format-specific provenance and temporal semantics are not equivalent to the
DS-004 operational occurrence chain.

The proposal must also keep “raw bytes exist” separate from “an operational
observation can be checked against raw bytes.” A file source may be
content-addressed and still be outside EA's temporal-authentication policy.

No transition assessment, flow assessment, physical occurrence, configuration
identity, causal reasoning, diagnosis, planning, or general provenance
platform is authorized by this audit.

## 15. Acceptance matrix audit

The A01–A40 matrix is broad and mostly mutually coherent. Its strongest
coverage is the strict distinction between payload checksum, metadata
closure, temporal membership, pure digest validation, and physical truth.

The matrix is not sufficient as written because:

- A01, A17, and A33 assume a stronger cross-store fence than the architecture
  provides. They must use the narrowed guarantee or a coordinated protocol.
- A18 does not cover the valid >4,096-history case as a usable policy. It must
  prove the explicit horizon/summary behavior.
- A20–A27 include downstream binding, interpretation, semantic, and freshness
  admission in the evidence foundation. If those remain, a pure carried-result
  seam and separate acceptance rows are mandatory.
- A12/A13 are insufficient without the effective-time coverage axis and
  failed-attempt `finished_at` twin.
- A03 must include metadata replacement after initial read and before final
  fence, plus the limitation that a post-fence mutation can go undetected.
- A31/A32 are good negative twins and should be retained exactly.
- A39 must include a valid multi-source request that shares one allowed
  namespace while keeping source/adapter/item scopes separate.

After the corrections, the matrix needs at least these explicit additional
rows:

| New row | Required proof |
|---|---|
| A41 | >4,096 attempts use the declared horizon/summary or return typed horizon incompleteness; no silent truncation |
| A42 | source and temporal mutations at every capture boundary either refuse or remain described as non-atomic |
| A43 | semantic admission cannot select an occurrence absent from carried temporal material |
| A44 | occurrence receipt membership and attempt effective-time coverage remain separate |

## 16. Owner-question adjudication

### Q1 — New sibling component

**Endorse with correction.**

A sibling is the least disruptive placement for cross-store evidence selection.
Its responsibility must be narrowed to content-bound evidence selection and
revalidation. It must not become the owner of semantic admission or a general
evidence authority.

### Q2 — Package and public class names

**Endorse with correction.**

`backend.evidence_assurance` and `EvidenceAssuranceQueries` are descriptive
enough for the bounded proposal. The public name must not imply authentication,
trust certification, or physical assurance. If semantic admission is removed,
the package name remains acceptable because the proposal defines “assurance”
as qualified mechanical checks.

### Q3 — Operational-API-only v1

**Endorse.**

The restriction matches DS-004's actual contracts and avoids pretending that
raw file bytes provide the same temporal/field provenance as operational API
observations. It is enforceable if the reader rejects non-API artifact routes.

### Q4 — Two lower public read seams

**Endorse with correction.**

The source reader and one-transaction temporal material query are the minimum
lower seams for the narrowed foundation. They are not enough to support
semantic admission over already captured material. That requires either
removing semantic admission from EA or separately approving a pure carried
candidate seam.

### Q5 — Receipt-axis selection, no general window, fixed bounds

**Reject as written.**

Receipt-axis selection and no arbitrary window are reasonable. The combination
of “all history through cutoff,” no lower boundary, and a hard 4,096 cap is
not feasible for long-lived sources. Approve only after an explicit horizon or
reproducible coverage-summary contract is added.

### Q6 — Optional maximum-staleness threshold

**Endorse with correction.**

The threshold is a caller admission policy and should not be described as
source freshness truth, sensor quality, or semantic correctness. Equality
must pass, and the selected occurrence must remain unchanged when the
threshold fails.

### Q7 — Computed digest with no persistence or durable identity

**Endorse.**

A content fingerprint is appropriate for this foundation. It must remain
clearly distinct from a signature, authenticated receipt, model identity,
authority rank, or physical event identity. The expected-digest requirement
for mutation detection is correct.

## 17. Final recommendation

Do not approve implementation of the proposal in its current form.

The smallest acceptable final design would:

1. retain the new sibling and operational-API-only source scope;
2. make EA a content-bound evidence selection/revalidation component;
3. remove live semantic admission from EA, or separately specify a pure
   carried-result seam;
4. define a bounded coverage horizon or a reproducible temporal summary;
5. narrow cross-store language from immutable/global snapshot to captured-view
   consistency unless a coordinated snapshot protocol is introduced;
6. make the temporal seam preserve receipt selection and effective-time
   quality as separate rules; and
7. revise A01–A44 and the issue vocabulary to prove those exact guarantees.

These corrections do not enlarge EA-001 into transition assessment, flow
assessment, physical occurrence, configuration identity, causal reasoning,
diagnosis, planning, or a general provenance platform.

END OF EA-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
