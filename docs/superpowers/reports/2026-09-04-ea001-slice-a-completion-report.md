# EA-001 Slice A Completion Report

Date: 2026-09-04

Status: implementation and verification complete; owner validation pending

## 1. Authority, baseline, and outcome

The owner accepted the final EA-001 architecture and authorized Slice A only.
The normative design is:

`docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`

The accepted repository base is:

`539f954fa759c9e20c167775b2ac906a8c867c85`

The implementation branch is `ea001`. The final committed Slice A HEAD before
this intentionally uncommitted report is:

`873df5bfc4fef2b6c8136612c7a9655048dd6b1b`

Slice A adds exactly two lower, read-only seams:

1. a DS-004 operational API evidence reader owned by `data_sources`; and
2. a bounded, one-transaction temporal selection-material query owned by
   `temporal_state`.

It does not create `backend.evidence_assurance`, captured-view cross-store
orchestration, an EA snapshot or content fingerprint, evaluator integration,
semantic admission, a store, a ledger, an anchor, a revision, a cache, a
persistent receipt, or an authoritative demonstration artifact. Slice B and
all consumer integration remain unauthorized.

The accepted baseline and final preservation state are both:

| Property | Exact value |
|---|---|
| Authoritative model records | 36 |
| Model revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FRG / FLD / FLW | `1 / 1 / 0` |
| TRG / TRD / TRW | `0 / 0 / 0` |
| 36-record stored-file aggregate | `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a` |
| Accepted FL disclosure bytes | 660,516 |
| Accepted FL disclosure SHA-256 | `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b` |

## 2. Accepted design preservation

The three owner-approved design inputs remain byte-exact in the committed
history:

| Input | SHA-256 |
|---|---|
| Codex lead proposal | `97ddef4ac9a8ee4248fa9d2ffe7e47225172bb741a0a02c5a03f78bee99dbd98` |
| Challenger audit | `14ac3fab976aa007785b2876a035a636306b1ad55ef0a236f12e675977353b81` |
| Final synthesis | `a33e8bbea1869889c082ec49f8e9f9966d98f72fc70286f8381f1d7f32db52a0` |

The challenger audit is an accepted CRLF artifact. Repository text
normalization would otherwise change its committed bytes. The first commit
therefore adds one narrow `docs/superpowers/reports/.gitattributes` rule that
treats only that file as binary. The working copy and staged blob were both
verified against the accepted digest before commit. Neither the audit nor the
other two design inputs was edited.

## 3. Commit sequence

The bounded commit sequence after the accepted base is:

| Commit | Purpose |
|---|---|
| `18c7d6d86867ad221153f9cf0dde84a2e9265f94` | Accept the three exact EA-001 design records and preserve the audit bytes. |
| `d6a67156142f7f2b7d540deeb9c01e11a8857976` | Add the Slice A implementation plan and acceptance-row mapping. |
| `07f9a42f1b5f3d08de18b5ddd8ea23f818fec59c` | Add the DS-004 operational evidence contracts, reader, exports, and focused tests. |
| `ca6bfd653f9820666274aac2cc9d1b578c1120c8` | Add bounded temporal selection contracts, queries, and focused tests. |
| `873df5bfc4fef2b6c8136612c7a9655048dd6b1b` | Harden both seams, add architecture/parity/determinism tests, and repair reproduced defects. |

No commit was amended. No push, merge, rebase, reset, cherry-pick, or history
rewrite was performed.

## 4. Changed-file inventory

### 4.1 Production lower seams

- `backend/data_sources/contracts/__init__.py`
- `backend/data_sources/contracts/operational_evidence.py`
- `backend/data_sources/evidence/__init__.py`
- `backend/data_sources/evidence/operational_api.py`
- `backend/temporal_state/contracts.py`
- `backend/temporal_state/queries.py`

### 4.2 Slice A tests

- `tests/data_sources/test_ea001_operational_evidence_reader.py`
- `tests/temporal_state/test_ea001_selection_material.py`
- `tests/test_ea001_slice_a_architecture.py`
- `tests/test_ea001_slice_a_reproduction.py`

### 4.3 Accepted design and plan records

- `docs/superpowers/plans/2026-09-04-ea001-slice-a-implementation-plan.md`
- `docs/superpowers/proposals/2026-09-04-ea001-codex-lead-proposal.md`
- `docs/superpowers/reports/.gitattributes`
- `docs/superpowers/reports/2026-09-04-ea001-codex-lead-proposal-challenger-audit.md`
- `docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`

The milestone range contains no model, fixture, raw-evidence, temporal
database, identity, ledger, membership, canonical-record, or accepted
demonstration-artifact change.

## 5. DS-004 operational evidence seam

The new bounded public reader surface exports exactly:

```text
Ds004OperationalEvidenceReader
FilesystemDs004OperationalEvidenceReader
```

The new source contract module exports exactly:

```text
Ds004OperationalEvidenceMaterial
Ds004OperationalEvidenceScope
OperationalApiArtifactDescriptor
OperationalApiArtifactKind
OperationalApiInventoryToken
OperationalEvidenceReadError
```

The exact request scope is source ID, adapter ID, endpoint ID, item key,
subject identifier, extraction route, and RFC 6901 pointer. Scope values are
strict strings; hidden fields and scalar coercion reject.

The implementation:

- reads only the configured `FilesystemRawStore`, never caller-supplied paths;
- supports only the accepted DS-004 `api:moonraker:v1` route;
- reads every retained metadata artifact through a read-only, no-follow file
  descriptor and parses the same byte string that it hashes;
- distinguishes every metadata-file digest from the stored raw-payload
  checksum and requires raw payload bytes to match that checksum;
- validates the exact `ExtractionResult -> ApiObservationsResult ->
  ApiExtractionManifest` wrapper;
- closes attempts, both attempt and raw-origin ingestion runs, envelopes,
  payload references, extraction or quarantine rows, API locators, request
  fingerprints, observations, and content-derived IDs;
- resolves RFC 6901 object and array pointers exactly and compares canonical
  `value_json` and `json_type` without coercion;
- keeps byte-identical shared content distinct from its attempts and
  occurrences while deduplicating the shared raw artifact;
- produces canonical material and inventory order independent of filesystem
  enumeration order;
- binds inventory membership to captured content digests as well as logical
  names and sizes;
- rejects malformed, duplicate-key, non-finite, over-deep, over-wide, or
  over-large JSON through the accepted bounded parser;
- rejects traversal-shaped references, symlinks, non-regular entries,
  unexpected names, unsupported families/routes, and unsanitized request
  disclosure;
- redacts filesystem paths and source secrets from typed public errors;
- refuses rather than truncates at 4,096 in-horizon attempts, 16,384 retained
  artifacts, or 64 MiB retained metadata; and
- performs no network call, connector execution, extraction rerun, clock read,
  environment discovery, or write.

Failed attempts remain distinct from successful extracted and quarantined
attempts. A requested pre-horizon seed must predate the horizon, belong to the
exact scope, be successful, and carry the exact requested observation.

## 6. Temporal selection-material seam

`TemporalQueries` adds exactly these methods:

```python
selection_inventory_token(
    scope,
    *,
    horizon_started_at,
    as_of,
) -> TemporalSelectionInventoryToken

selection_material(
    scope,
    *,
    horizon_started_at,
    as_of,
) -> TemporalSelectionMaterial
```

The inventory token field order is:

```text
schema_version
projector_version
scope
horizon_started_at
as_of
occurrence_membership_sha256
attempt_coverage_membership_sha256
clock_opening_membership_sha256
```

The material field order is:

```text
schema_version
projector_version
scope
horizon_started_at
as_of
selected_occurrence_index
selected_occurrence_is_pre_horizon_seed
occurrence_membership
attempt_coverage_membership
clock_segment_openings
transaction_membership_sha256
```

Both methods reject non-datetime values, naive datetimes, reversed horizons,
invalid scopes, and hidden/coercible inputs before database work. Aware inputs
are normalized to UTC.

Every logical material read occurs inside one explicit SQLite read
transaction. The query:

- selects the latest occurrence at or before inclusive `as_of` by
  `received_at` and the complete accepted `AttemptOrderKey`;
- joins each occurrence to its parent attempt to preserve the otherwise absent
  endpoint dimension of the exact request;
- keeps receipt-time occurrence membership separate from effective-time
  attempt-coverage membership;
- carries at most one labelled selected occurrence before the horizon and
  excludes it from coverage;
- uses `finished_at` with `finished_at_no_response` for a failure without a
  response;
- preserves failures, quarantines, empty snapshots, omitted properties,
  observations, source-time markers, and clock-segment openings as distinct
  disclosures;
- returns exact empty material when no observation exists at or before the
  cutoff;
- succeeds with 4,099 lifetime attempts when only two are in the requested
  horizon;
- refuses 4,097 in-horizon attempts without truncation or sampling; and
- returns canonical logical digests bound to the complete material.

Public reconstruction deep-revalidates nested occurrences, attempts, and
clock openings, exact scope and horizon membership, selected-index semantics,
cross-row attempt/occurrence parity, ordering, uniqueness, bounds, and the
transaction digest. Boolean indices, stale digests, duplicate or reordered
rows, substituted raw IDs, and hostile `model_construct`/`model_copy` values
reject.

## 7. Architecture and scope isolation

Executable architecture tests prove:

- `data_sources` does not import `temporal_state`;
- neither lower seam imports identity binding, source interpretation, model
  kernel/state, observation or semantic compatibility, constraint or behavior
  evaluation, state classification, transition, flow, or EA composition;
- no `backend/evidence_assurance` package exists;
- the source reader imports no socket, HTTP client, subprocess, connector
  runtime, or write API;
- source contracts and reader exports are exact and bounded; and
- lower material contains no model, semantic, physical-occurrence, freshness,
  suitability, diagnosis, control, or recommendation field.

`temporal_state` imports only the exact source-owned scope contract, preserving
the accepted `data_sources -> temporal_state` direction. No schema, projector
row, checkpoint meaning, existing query, or root-package aggregate facade was
changed.

## 8. Red-before and fixed-after evidence

The first focused run was intentionally red before any production surface
existed:

```text
2 errors during collection in 4.51s
ImportError: cannot import name 'Ds004OperationalEvidenceMaterial'
ImportError: cannot import name 'Ds004OperationalEvidenceScope'
```

The first source implementation made its initial 14 tests green. The first
temporal implementation then exposed a genuine exact-scope defect:

```text
1 failed, 7 passed
test_scope_is_exact_and_view_does_not_merge_endpoints
```

`TemporalOccurrence` does not carry endpoint ID. Selection had filtered only
the six occurrence dimensions and could admit the same property from another
endpoint. The repair requires the occurrence's parent attempt to match the
requested endpoint. The temporal module checkpoint then passed 88 tests and
the expanded temporal suite ultimately passed 95.

The first bounded hostile review produced four deliberate failures among 36
tests:

1. a source inventory token accepted a stale membership digest;
2. a raw-payload descriptor accepted unequal captured and stored checksums;
3. temporal occurrence membership could claim that no occurrence was selected;
4. a hostile nested temporal attempt instance could bypass child validation.

All four were reproduced before repair. Digest recomputation, raw checksum
equality, selected-index invariants, and explicit nested reconstruction made
the same selection pass `36 passed`.

Subsequent red-first findings and repairs were:

| Finding | Red evidence | Repair |
|---|---|---|
| Same-length metadata mutation left the source inventory token unchanged. | `1 failed, 43 passed` | Inventory member keys now include the captured file digest and payload checksum. |
| Shared byte-identical payloads caused distinct attempts to fail material validation. | `1 failed, 36 passed` | Attempt identity remains distinct while the shared envelope, payload, extraction, and observation are deduplicated exactly once. |
| A reused payload's raw envelope referenced an originating run before the requested horizon, which was omitted. | `1 failed, 45 passed` | Material now carries both the selected attempt's run and the reused raw envelope's originating run, and validates each role separately. |

Additional hardening covers actual datetime types, seed-plus-membership bounds,
attempt request sanitization, stale observation IDs, cross-row substitutions,
duplicate JSON keys, malformed pointer escapes, single-open artifact reads,
reversed filesystem enumeration, and hash seeds `1`, `7`, and `12345`.

The final focused gate is:

`46 passed in 7.42s`

## 9. Cross-seam parity and deterministic reproduction

A disposable two-attempt DS-004 source is projected through the accepted
temporal projector. The source and temporal seams independently return exact
attempt IDs and exact observation provenance/value/type/source-time parity.
Neither lower module reads the other's store.

Two independently initialized working-checkout reproductions, the base-only
clean checkout, and the all-extras clean checkout all produced:

| Property | Exact value |
|---|---|
| Combined lower-material serialization bytes | 24,766 |
| Combined lower-material SHA-256 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` |
| Source artifacts / attempts / observations | `10 / 2 / 2` |
| Temporal occurrences / coverage attempts | `2 / 2` |

The focused subprocess test reconstructs and reserializes the strict public
contracts under Python hash seeds `1`, `7`, and `12345`; all three outputs are
byte-identical. Reversed filesystem enumeration also yields byte-identical
source material.

## 10. Verification results

### 10.1 Working implementation checkout

| Gate | Result |
|---|---|
| Final focused EA-001 Slice A | 46 passed in 7.42s |
| Complete `temporal_state` | 95 passed in 14.78s |
| Complete `data_sources`, restricted sandbox | 361 passed; one localhost-bind setup error in 290.70s |
| Isolated `data_sources` loopback rerun | 1 passed in 1.93s |
| Effective complete `data_sources` | 362 passed; zero functional failures |
| Identity/binding/source/observation downstream selection | 588 passed in 37.63s |
| Semantic/constraint/behavior/state/model-state downstream selection | 594 passed in 444.09s |
| Complete model kernel | 1,654 passed in 1,053.13s |
| Complete repository | 3,527 passed in 1,352.63s |
| Backend compilation | 113 Python files compiled successfully |
| Public import smoke check | pass |
| Working-tree `git diff --check` before this report | pass |
| Full `539f954..873df5b` `git diff --check` | pass |

The complete working repository run itself had permission to execute the
loopback test and therefore finished directly with 3,527 passes. The isolated
rerun above reconciles the expected restricted result from the separately
invoked `data_sources` suite.

### 10.2 Fresh base-only clean checkout

Resolved checkout before cleanup:

`/tmp/ea001-base-clean-0ixHx8/checkout`

- exact detached HEAD:
  `873df5bfc4fef2b6c8136612c7a9655048dd6b1b`;
- installed only `requirements.txt` and `requirements-dev.txt` into a fresh
  virtual environment;
- restricted complete suite: 3,491 passed, 35 optional-dependency skips, and
  one localhost-bind setup error in 883.97s;
- exact isolated loopback rerun: 1 passed in 0.72s;
- effective result: 3,492 passed, 35 skipped, zero functional failures;
- `pip check`: no broken requirements;
- backend compilation: pass;
- deterministic lower serialization: exact 24,766 bytes and
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
- authoritative model count, revision, ledger aggregate, and read-only snapshot:
  exact;
- working and milestone-range whitespace: pass; and
- Git status: clean.

### 10.3 Fresh all-extras clean checkout

Resolved checkout before cleanup:

`/tmp/ea001-extras-clean-44Wb5S/checkout`

- exact detached HEAD:
  `873df5bfc4fef2b6c8136612c7a9655048dd6b1b`;
- installed base/dev and then the separate hash-pinned CAD and PDF requirement
  sets into a fresh virtual environment;
- restricted complete suite: 3,526 passed and one localhost-bind setup error in
  930.95s;
- exact isolated loopback rerun: 1 passed in 0.71s;
- effective result: 3,527 passed, zero skips or functional failures;
- focused optional marker selection: 33 passed, 329 deselected in 36.54s;
- `pip check`: no broken requirements;
- backend compilation: pass;
- deterministic lower serialization: exact 24,766 bytes and
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
- authoritative model count, revision, ledger aggregate, and read-only snapshot:
  exact;
- working and milestone-range whitespace: pass; and
- Git status: clean.

The sole restricted error in the module/base/extras columns was
`PermissionError: [Errno 1] Operation not permitted` while binding
`127.0.0.1`. Every exact isolated loopback rerun passed under the established
local-socket permission. No test was omitted.

## 11. Historical, model, evidence, and artifact preservation

`verify_authoritative_ledger("proposed")` passed and a byte snapshot taken
immediately before and after that verification was identical. Every model
record retained its content-derived identity.

Exact retained model facts are:

- 36 records;
- revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- whole-ledger stored-file aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- accepted 34-record predecessor aggregate
  `cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd`;
- one FRG, one FLD, zero FLW; and
- zero TRG, TRD, or TRW.

The accepted FL disclosure remains exactly 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
Existing accepted tests also retain the PT, VP, BH, ST, ST-002, and FL
historical memberships, revisions, record bytes, and disclosure hashes.

The implementation reads only disposable source and temporal stores created
under test temporary directories. The milestone diff and final Git status show
that no existing evidence store, temporal database fixture, source fixture,
model record, identity, ledger, membership, canonical artifact, or accepted
disclosure changed.

## 12. Acceptance-row disposition

The final-spec rows allocated to Slice A are executable as follows:

| Final rows | Slice A result |
|---|---|
| A01-A15 | DS-004 byte, checksum, wrapper, provenance, pointer, value/type, outcome, and absence distinctions are closed or refused typed. |
| A16-A28 | Inclusive cutoff, full tie-break, separate temporal axes, no-response basis, pre-horizon seed, exact absence, and bounded-history twins pass. |
| A29-A40 | Safe filesystem behavior, redacted errors, deterministic tokens, unsupported families, import isolation, and semantic/model absence pass at the lower seams. |
| A42-A45 | Coverage categories, exact scope/horizon, policy-free parity inputs, and hostile public reconstruction pass. |
| A49-A50 | Enumeration/hash-seed determinism and no network/connector/extraction/write/clock behavior pass. |

A30-A37 are implemented only to the extent of each independent lower token and
material contract. Their combined captured-view boundary orchestration remains
Slice B. A41 and A46-A48 are Slice B-only age, snapshot, fingerprint, and
replacement-twin rows and were not implemented.

## 13. Limitations and non-claims

The source seam checks named stored bytes and mechanical provenance closure in
one invocation. It does not authenticate a sensor, source, operator, clock, or
physical event. A matching checksum is not a signature or a truth claim.

The temporal seam returns a one-transaction view of one SQLite store. It does
not create a distributed snapshot with the filesystem store, compare unrelated
clock domains, establish freshness, or claim complete lifetime history.

The two lower materials are sufficient inputs for a future owner-authorized EA
composition, but Slice A itself does not perform source/temporal fencing,
derive an EA snapshot/fingerprint, classify evidence, or admit an engineering
conclusion.

## 14. Final status and owner gate

EA-001 Slice A is implemented, adversarially hardened, deterministic, fully
regression-tested, dual-clean-checkout verified, and preservation-checked at
committed HEAD `873df5bfc4fef2b6c8136612c7a9655048dd6b1b`.

This completion report is intentionally uncommitted for the owner gate. There
is no unresolved implementation question within Slice A. The remaining owner
decision is whether to accept this report and, separately, whether to authorize
Slice B. No Slice B or integration work has started.

END OF EA-001 SLICE A COMPLETION REPORT
