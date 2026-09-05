# EA-001 Slice B Implementation Plan

Date: 2026-09-04 (authorization status reconciled 2026-09-05)

Status: corrected contract and Slice A integrity repair owner accepted; Slice B
implementation authorized from administrative checkpoint
`b0ffc1b59fec4c4fcc93e90362f9ffe71862e8fa`; Slice C remains unauthorized

Accepted Slice A HEAD: `873df5bfc4fef2b6c8136612c7a9655048dd6b1b`

Accepted discrepancy-stop HEAD:
`b3e27cb41d9d69bf1545b50fb5aaa693ca7586f6`

Accepted discrepancy-report SHA-256:
`cc5999e2d1f4d7191b4c4dba047f4420793f86a03f7b7cbe1801116dde486574`

Corrected normative synthesis:
`docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`

Accepted corrected synthesis SHA-256:
`557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`

Accepted Slice A integrity-repair HEAD:
`ceee1446f18ae9b7134005089046a5a4d69e10ae`

## 1. Current authorization boundary

The owner accepted the corrected synthesis and the completed Slice A integrity
repair. The owner then separately authorized Slice B implementation only from
administrative checkpoint
`b0ffc1b59fec4c4fcc93e90362f9ffe71862e8fa`. Slice C remains unauthorized.

## 2. Dependency and scope boundary

The eventual Slice B remains a read-only `backend.evidence_assurance`
composition package. It may consume only public DS-004 operational-evidence
contracts/reader methods, public temporal contracts/query methods, Pydantic,
and the standard library.

It owns no store, cache, database, ledger, revision, anchor, minter,
persistent receipt, signature, connector, ambient clock, environment
discovery, or write path. It imports no identity, interpretation, model,
observation/semantic compatibility, constraint, behavior, state, transition,
flow, connector/vendor, UI, planning, control, private filesystem-store, or
private SQLite module. No existing package imports EA during Slice B.

## 3. Owner-accepted Slice A integrity repair

The completed and separately accepted repair is limited to the existing public
DS-004 reader seam:

1. Keep the exact `inventory_token(scope, *, horizon_started_at, as_of)`
   signature.
2. Independently discover the source-side latest eligible exact-property
   observation at/before `as_of` by receipt time and the complete
   `AttemptOrderKey`.
3. If it is pre-horizon, bind exactly its complete mechanical closure in each
   token under the accepted member-key/content rules.
4. Keep lifetime discovery streaming and bounded per artifact; charge only
   retained in-horizon attempts to the 4,096 limit.
5. Require the seed ID later supplied to `read_material(...)` to equal the
   independently discovered source candidate.
6. Add exactly
   `reread_named_material(expected_material) ->
   Ds004OperationalEvidenceMaterial` to the existing protocol and filesystem
   reader.
7. Reconstruct expected material before I/O; derive all paths internally;
   reread exactly its named set with same-read hashing/parsing and checksum,
   closure, equality, byte, artifact-count, safety, and redaction checks.
8. Ignore unrelated additions and do not apply current horizon growth to the
   original frozen named-material attempt set.

The repair adds no source export, temporal import, caller path, caller seed
parameter, schema, projector change, EA package, or upper integration.

Repair tests must cover every seed dependency, source candidate/temporal seed
disagreement, reused raw content/originating run, more than 4,096 lifetime
attempts, enumeration/hash-seed determinism, exact named matches, every named
artifact mutation/absence/substitution, unrelated additions, current horizon
overflow, hostile expected material, no I/O before reconstruction, and no
network/connector/extraction/clock/environment/write behavior.

If token bytes change, the repair report must record the new exact lower-
token/material reproduction size and digest while preserving the accepted
Slice A material contract and historical digest as historical evidence.

## 4. Exact eventual Slice B public surface

After repair acceptance, Slice B implements only the exact Section 11 models,
vocabularies, errors, facade, and validator. The result/support pins now
include:

- `OperationalEvidenceMaterialLimits`;
- `OperationalEvidenceIssue`;
- `OperationalNamedArtifactRevalidation`;
- `OperationalEvidenceSelectionResult`;
- `OperationalEvidenceStoreRevalidationResult`; and
- `OperationalEvidenceSnapshotValidationResult`.

All fields, types, order, literal order, carry-once invariants, and the exact
33-name `backend.evidence_assurance.__all__` are normative. Lower source and
temporal types are not re-exported. There are no aliases or alternative public
names.

A successful/incomplete result carries one snapshot and no outer issues. A
refused result carries no snapshot and its refusal issues once. Offline and
store revalidation results repeat neither the snapshot nor complete source or
temporal material.

The exception tree exposes only `error_code` and `message`. Configuration
misuse is `EA_DEPENDENCY_INVALID`; query misuse is exactly
`EA_REQUEST_INVALID` or `EA_SELECTION_POLICY_INVALID`.
`EA_TIME_COMPARISON_UNSUPPORTED` is removed. V1 has no cross-clock input or
method; fixed `source_time_use="disclosure_only"` is policy validation.

## 5. Captured-view selection protocol

The eventual facade sequence is fixed:

1. deep-reconstruct/validate the request before I/O;
2. capture the seed-aware initial source token;
3. capture the initial temporal token;
4. read temporal material in one transaction;
5. supply its optional seed ID to one source-material read, which independently
   checks the source candidate;
6. verify source closure, separate parity axes, routes, and content;
7. capture seed-aware final source and final temporal tokens;
8. refuse changed stores, material/fence disagreement, or seed-ID parity
   failure; and
9. derive only from captured material.

The claim remains captured-view consistency at observed fences. It is not a
distributed transaction, global snapshot/currentness claim, or detector for
post-final-fence changes.

## 6. Selection, canonicalization, and validation

The implementation recomputes exact horizon/cutoff membership, full ordering,
one optional seed, separate receipt/effective axes, coverage dispositions,
routes/indices, selected observation, disclosure-only age, summaries, ordered
issues, assurance, canonical bytes, and `sha256:` content fingerprint.

Issues 1–14 refuse without a snapshot. Issues 15–16 remain ordered in an
incomplete snapshot. A complete result requires at least one in-horizon
attempt, every route observed, a selected observation, and no issue.

Offline validation performs no I/O, deep-reconstructs all content, recomputes
every derived field and fingerprint, carries no snapshot, and always reports
`source_bytes="not_rechecked"` and
`temporal_store_membership="not_rechecked"`. Expected fingerprint state is
exactly matched, mismatched, or not supplied.

## 7. Store-bound revalidation

Both modes first validate the snapshot without I/O and then call the exact
named-material reread. Current source and temporal memberships are observed
separately.

`require_equal_final_observed_membership` succeeds only when named/carried
material matches and stable current source/temporal memberships equal the
snapshot's final tokens. A stable difference is
`observed_membership_changed`; an unobservable bounded membership refuses.

`named_captured_artifacts` may return
`valid_for_named_captured_artifacts` when the exact named source material
matches even if current membership differs or cannot be fully observed. Its
source/temporal membership and carried-temporal-material relations remain
explicit. It never calls the historical selection current or latest.

## 8. Red-first and commit sequence under Slice B authorization

The completed Slice A repair followed this sequence:

1. add failing seed-fence/named-reread lower tests;
2. implement the bounded Slice A repair;
3. adversarially review, reproduce every defect red-first, repair, verify, and
   stop for repair acceptance.

The separately authorized Slice B follows this sequence:

1. add failing exact contracts/exports/errors tests;
2. implement contracts and canonical derivation;
3. add failing captured-view selection tests and implement the facade;
4. add failing pure/store-bound revalidation tests and implement both modes;
5. run an adversarial review and encode every genuine defect before repair;
6. commit in small reviewable checkpoints and leave the completion report
   uncommitted.

## 9. Acceptance and verification mapping

The corrected synthesis retains A01–A50. Old A21 is explicitly reconciled as
the absence of a cross-clock API plus fixed disclosure-only policy behavior.
A03/A04/A28/A31–A33/A36/A40/A43/A45/A48 now cover named reread, seed-aware
fences, fixed limits, exact public pins, relation distinctions, carry-once
validation, and offline no-I/O fields.

Final verification remains:

- focused repair/EA and complete data-source/temporal suites;
- architecture/import isolation and affected downstream suites;
- complete model-kernel and repository suites;
- fresh base-only and all-extras clean checkouts;
- permitted loopback reconciliation where required;
- backend compilation/dependency checks;
- working/full-milestone `git diff --check`;
- exact model count/revision, FRG/FLD/FLW, ledger aggregate, FL disclosure,
  accepted historical artifacts, and deterministic lower-material evidence.

No Slice C or authoritative demonstration work is included.

END OF EA-001 SLICE B IMPLEMENTATION PLAN
