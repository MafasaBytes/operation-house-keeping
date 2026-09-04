# EA-001 Slice A Implementation Plan

Date: 2026-09-04

Status: authorized implementation plan for Slice A only.

Accepted base: `539f954fa759c9e20c167775b2ac906a8c867c85`

Design-acceptance commit: `18c7d6d` (`docs: accept EA-001 architecture`)

Normative design:
`docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`

## 1. Scope and stop conditions

Slice A adds exactly two lower, read-only seams:

1. a DS-004 operational API evidence reader owned by `data_sources`; and
2. a bounded, one-transaction temporal selection-material query owned by
   `temporal_state`.

It does not create `backend.evidence_assurance`, captured-view orchestration,
an EA snapshot/fingerprint, evaluator integration, a new store, or any model
record. Work stops if either seam would require changing an accepted source
artifact, temporal row schema, projector meaning, model/canonical contract, or
foundational import direction.

## 2. Public contract additions

### 2.1 `data_sources`

Add strict, frozen contracts for:

- `Ds004OperationalEvidenceScope`;
- `OperationalApiArtifactKind`;
- `OperationalApiArtifactDescriptor`;
- `OperationalApiInventoryToken`;
- `Ds004OperationalEvidenceMaterial`; and
- `OperationalEvidenceReadError`.

Add `Ds004OperationalEvidenceReader` as the narrow public protocol and
`FilesystemDs004OperationalEvidenceReader` as its read-only filesystem
implementation. Export contracts through `backend.data_sources.contracts` and
the reader through a bounded `backend.data_sources.evidence` surface. Do not
turn the empty root package into an unrelated aggregate facade.

The implementation reads only DS-004 attempt-bearing API material. It scans
accepted store directories without accepting caller paths, reconstructs every
metadata object from the same byte sequence it hashes, rereads payload bytes
through a read-only safe path, verifies stored checksums, validates the exact
`ExtractionResult -> ApiObservationsResult -> ApiExtractionManifest` wrapper,
resolves RFC 6901 pointers, and emits deterministic deduplicated material.

### 2.2 `temporal_state`

Add strict, frozen contracts for:

- `TemporalSelectionInventoryToken`; and
- `TemporalSelectionMaterial`.

Add exactly two `TemporalQueries` methods:

- `selection_inventory_token(scope, *, horizon_started_at, as_of)`; and
- `selection_material(scope, *, horizon_started_at, as_of)`.

Both use the `Ds004OperationalEvidenceScope` owned by `data_sources`, preserving
the existing `data_sources -> temporal_state` direction. The material method
performs every logical read in one explicit SQLite read transaction, selects
latest-at-or-before by receipt time plus the complete `AttemptOrderKey`, keeps
receipt membership separate from effective-time coverage membership, carries
one labelled pre-horizon seed when applicable, and returns deterministic
logical digests. It changes no schema or projector row.

## 3. Bounds and error behavior

The source material limits are 4,096 in-horizon attempts, 16,384 occurrence-
capable observations, 16,384 retained artifacts, and 64 MiB retained metadata.
The temporal limits are 4,096 in-horizon attempt events and 16,384 occurrence
members including the optional seed. Valid over-limit material raises a typed,
path-free lower-seam error; it is never truncated or sampled.

Naive datetimes, reversed horizons, malformed scope, and coercible invalid
inputs reject before database work. Missing/corrupt artifacts, unsupported
families/routes, checksum mismatch, closure mismatch, pointer mismatch, and
limit refusal remain distinct typed error codes. Raw SQLite/filesystem errors
must not leak paths or implementation details.

## 4. Red-first test plan

Create focused suites under `tests/data_sources` and `tests/temporal_state`.
Initial public-import, signature, field-order, read-only, selection, and hostile
tests must fail because the contracts and methods do not yet exist. Preserve
that command/output as red-before evidence in the completion report.

Implement in this order:

1. strict source/temporal contracts and exact exports;
2. source reader happy path and deterministic material;
3. source closure, pointer, family, path, limit, and no-write hardening;
4. temporal transaction, memberships, seed, ordering, version, and digest;
5. temporal horizon/limit and hostile revalidation hardening; and
6. import-isolation, cross-seam parity, hash-seed, and preservation checks.

Every reproduced defect after first green receives a failing regression test
before repair.

## 5. Final-spec acceptance-row mapping

| Final row | Slice A executable coverage |
| --- | --- |
| A01 | Source reader closes the complete DS-004 source chain; temporal query returns the exact selected occurrence. |
| A02–A03 | Payload mutation/checksum substitution fails through exact stored checksum and raw-ID closure. |
| A04 | Source inventory token and captured metadata digest change under ordinary metadata mutation; cross-store fence orchestration remains Slice B. |
| A05–A07 | Raw/run/locator/request/extraction/quarantine link attacks fail typed. |
| A08 | Instrumented reader proves one metadata byte read supplies both hash and parse. |
| A09–A11 | RFC 6901 escaping, missing/index errors, canonical value/type, malformed UTF-8, duplicate keys, non-finite values, and parser bounds fail closed. |
| A12–A15 | Failure, quarantine, empty, omitted, observed, temporal absence/inconsistency, and source/temporal parity remain distinguishable in lower material. |
| A16–A19 | Inclusive cutoff, full tie-break, separate axes, and no-response `finished_at_no_response` are exact. |
| A20–A22 | Source time is disclosure-only and duplicate bytes do not collapse attempts/occurrences. |
| A23–A25 | One labelled pre-horizon seed, no seed coverage, and exact no-observation result are represented by the temporal seam. |
| A26–A28 | Lifetime >4,096 with bounded horizon succeeds; in-horizon excess and other bounds refuse without materialization/truncation. |
| A29 | Path traversal, symlink/device/socket, unexpected name, and diagnostic redaction tests. |
| A30–A37 | Individual source and temporal inventory tokens are deterministic; combined captured-view boundary injection is deferred to Slice B. |
| A38 | CSV/Excel/PDF/STEP/CAD/generic file routes reject. |
| A39–A40 | Architecture tests prove no forbidden imports and no semantic/model/physical fields in lower results. |
| A42–A44 | Lower rows preserve coverage categories, absence, exact scope, horizon, and policy-free parity inputs. EA issue/status mapping remains Slice B. |
| A45 | `model_construct`, `model_copy`, hidden extras, wrong unions, stale IDs, duplicate/reordered rows, and boolean indices fail public reconstruction. |
| A49 | Reversed enumeration and hash seeds 1, 7, and 12345 yield identical lower tokens/material serialization. |
| A50 | Filesystem and SQLite instrumentation proves no network, connector, extraction, write, environment, or clock access. |

A41 and A46–A48 are Slice B-only age/snapshot/fingerprint acceptance rows and
are deliberately not implemented here.

## 6. Commit plan

1. `docs: accept EA-001 architecture` — already created; exact accepted design
   blobs only, plus the narrow audit byte-preservation attribute.
2. `docs: plan EA-001 Slice A lower seams` — this plan.
3. `feat: add DS-004 operational evidence reader` — source contracts, reader,
   exports, and focused source tests.
4. `feat: add bounded temporal selection material` — temporal contracts,
   queries, exports, and focused temporal tests.
5. `test: harden EA-001 Slice A lower seams` — cross-seam/adversarial/import-
   isolation/determinism/preservation tests and only reproduced repairs.

The completion report stays uncommitted for the owner gate.

## 7. Review and verification

After first green, conduct bounded architecture, backend-contract, test, and
adversarial reviews against the accepted specification. Record each finding;
reproduce every genuine defect red-first before repair.

Verification columns:

- focused EA-001 Slice A;
- complete `data_sources`;
- complete `temporal_state`;
- architecture/import-isolation and affected downstream suites;
- complete repository suite;
- backend compilation/static import checks;
- fresh base-only clean checkout;
- fresh all-extras clean checkout;
- separately permitted loopback test if sandbox denied; and
- working-tree/full-range `git diff --check`.

Before and after, compare authoritative model count/revision/FRG-FLD-FLW,
accepted FL disclosure bytes/hash, model-record aggregate, source/temporal
fixtures, and protected artifact hashes. No model, evidence, temporal database,
fixture, identity, ledger, membership, or canonical artifact may change.

END OF EA-001 SLICE A IMPLEMENTATION PLAN
