# EA-001 Slice B Completion Report

Date: 2026-09-05

## 1. Authority, checkpoint, and result

The owner authorized EA-001 Slice B implementation only on branch `ea001`
from administrative checkpoint
`b0ffc1b59fec4c4fcc93e90362f9ffe71862e8fa`. The separately accepted Slice A
integrity-repair implementation remains
`ceee1446f18ae9b7134005089046a5a4d69e10ae`.

The original exact tested Slice B implementation was
`70081b821569a82192f8e3fd100c2eec14beadb8`. The dated owner-review correction
in Sections 23–34 records the forward integrity repair and supersedes that
original stopping point. This report is intentionally uncommitted for owner
validation. Slice C, upper-layer integration,
authoritative demonstrations, ledger appends, and every other excluded scope
remain unauthorized and were not performed.

No push, merge, rebase, reset, amend, cherry-pick, or history rewrite was
performed.

## 2. Accepted contract and input verification

Before implementation, the repository guidance, actual branch and worktree,
corrected synthesis, corrected implementation plan, correction report, Slice A
repair owner acceptance, and Slice A repair completion report were read in
full. The initial checkout was clean at the authorized checkpoint.

The following accepted bytes were verified before work:

- corrected synthesis:
  `557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`;
- corrected plan before the authorized status-only reconciliation:
  `419e25c6cc752356292fdaeb98d635b01140d718f0aff2271379665a7fb93bd5`;
- contract-correction report:
  `43b205758cf3903132b5ac56a90f6536183f84cb6c92c967355c8972518ec1b1`;
- Slice A repair owner acceptance:
  `54f0306acafdbde5f663d34f85067088e3361bac5ba4e69ea4da99eb80b29f88`;
- Slice A repair completion report:
  `01c924c5fa65d21a0d14200bab09f742b139ec7b471fa5344e6e52be41dba446`.

The synthesis was not modified and still has its accepted digest. Historical
paused/candidate wording was reconciled only in `CLAUDE.md` and the Slice B
implementation plan to record the accepted repair and this authorization. The
post-reconciliation plan digest is
`2710841c73f5f30e84354580f147f086ba378008bfb9c677d164c22ed909c814`.

No installed skill applied to this repository implementation task, so no
skill changed the contract or work sequence.

## 3. Forward commit sequence

The commits after the authorized administrative checkpoint, in order, are:

1. `604f59c07e1dd62a6919bb968b5ee203bf4e7899` — `docs: authorize EA-001 Slice B implementation`
2. `c434d2e7b830572413520b7ee4c7aa0b98b59d23` — `test: specify EA-001 Slice B public contracts`
3. `f71c912997338d6e2edcb4054feb94d686b90b97` — `feat: add EA-001 Slice B public contracts`
4. `768084cd5d1a5c7871a7b71b49a6e5336f1d88e9` — `test: specify EA-001 captured-view selection`
5. `b4d63bd25dd685619eae0ebc2cda8b15d864fab8` — `feat: compose EA-001 captured evidence views`
6. `ebb1b2b165d3a7e8f06dd0b7e3c9e0870bdbae8c` — `test: specify EA-001 offline validation`
7. `ce5222eeabab0d9e9d100ed8bed8bb49d3b1dd2f` — `feat: validate EA-001 snapshots offline`
8. `3ca47ffa8ea004337875ca57b5f0af01a9949833` — `test: specify EA-001 store revalidation`
9. `71e61591b78d9b48c5571915476f3a6148789fb5` — `feat: revalidate EA-001 evidence stores`
10. `01e356aefc85d2b0a7f37f837bba0bc9309edf5d` — `test: preserve EA-001 adversarial contract defects`
11. `c85401bc5a4d6165764dec010a55dcc4075a13df` — `fix: harden EA-001 public reconstruction`
12. `d8c6e7cdf34dad9e7fd1a5792f9c320f6633c369` — `test: reject forged EA-001 inventory tokens`
13. `d9ce3e8afdc9d8462c41f97138a218c40f1a0b2b` — `test: reject forged EA-001 result relations`
14. `32619ec18ce34a893a451c36cae52d04b43beaca` — `fix: close EA-001 adversarial assurance gaps`
15. `70081b821569a82192f8e3fd100c2eec14beadb8` — `test: complete EA-001 parity and isolation coverage`

The implementation and test history is forward-only. The final report is not
part of any listed commit.

## 4. Changed files and bounded scope

The exact committed Slice B range changes these 14 paths:

- `CLAUDE.md`;
- `docs/superpowers/plans/2026-09-04-ea001-slice-b-implementation-plan.md`;
- `backend/evidence_assurance/__init__.py`;
- `backend/evidence_assurance/contracts.py`;
- `backend/evidence_assurance/queries.py`;
- `tests/evidence_assurance/__init__.py`;
- `tests/evidence_assurance/test_adversarial_contracts.py`;
- `tests/evidence_assurance/test_capture_boundaries.py`;
- `tests/evidence_assurance/test_contracts.py`;
- `tests/evidence_assurance/test_parity.py`;
- `tests/evidence_assurance/test_revalidation.py`;
- `tests/evidence_assurance/test_selection.py`;
- `tests/evidence_assurance/test_validation.py`;
- `tests/test_ea001_slice_a_architecture.py`.

The architecture assertion was narrowed only to recognize the now-authorized
EA sibling while retaining lower-seam isolation checks. No production file in
`backend/data_sources` or `backend/temporal_state` changed. No fixture,
evidence, temporal data, identity, model record, ledger, membership, or
canonical artifact changed.

## 5. Exact public API and export pin

`backend.evidence_assurance.__all__` is exactly the following ordered 33-name
list:

1. `EvidenceAssuranceError`
2. `EvidenceAssuranceConfigurationError`
3. `EvidenceAssuranceQueryError`
4. `EvidenceAssuranceConfigurationErrorCode`
5. `EvidenceAssuranceQueryErrorCode`
6. `CanonicalNonnegativeDecimal`
7. `CoverageDisposition`
8. `OperationalEvidenceIssueCode`
9. `OperationalEvidenceSelectionStatus`
10. `StoreIndependentValidationStatus`
11. `ExpectedFingerprintRelation`
12. `EmbeddedFingerprintRelation`
13. `StoreBoundMembershipMode`
14. `StoreBoundRevalidationStatus`
15. `NamedCapturedMaterialRelation`
16. `CapturedTemporalMaterialRelation`
17. `ObservedMembershipRelation`
18. `OperationalEvidenceSelectionPolicy`
19. `OperationalEvidenceSelectionRequest`
20. `OperationalEvidenceMaterialLimits`
21. `OperationalEvidenceIssue`
22. `OperationalProvenanceRoute`
23. `OperationalCoverageSummary`
24. `SelectedSourceObservation`
25. `CapturedViewFence`
26. `OperationalEvidenceAssurance`
27. `CapturedOperationalEvidenceSnapshot`
28. `OperationalNamedArtifactRevalidation`
29. `OperationalEvidenceSelectionResult`
30. `OperationalEvidenceStoreRevalidationResult`
31. `OperationalEvidenceSnapshotValidationResult`
32. `EvidenceAssuranceQueries`
33. `validate_operational_evidence_snapshot`

The facade has only the accepted constructor and these two methods:
`select_operational_evidence(request)` and
`revalidate_operational_evidence(snapshot, *, membership_mode)`.
No aliases, convenience methods, or alternative public vocabulary were added.

## 6. Exact result and support-model pins

Contract tests assert strict, frozen, extra-forbidden nested reconstruction,
field order, literal order, and exception fields. The public model fields are:

- policy: `kind`, `version`, `occurrence_axis`,
  `attempt_coverage_axis`, `source_time_use`;
- request: `schema_version`, `scope`, `horizon_started_at`, `as_of`,
  `policy`;
- limits: `schema_version`, `maximum_in_horizon_attempts`,
  `maximum_occurrence_members`, `maximum_retained_artifacts`,
  `maximum_retained_metadata_bytes`;
- issue: `code`, `detail_code`, `route_index`, `detail`;
- route: `attempt_index`, `run_index`, `temporal_attempt_index`,
  `envelope_index`, `payload_artifact_index`, `extraction_index`,
  `quarantine_index`, `observation_index`, `temporal_occurrence_index`,
  `artifact_descriptor_indices`, `coverage_disposition`;
- coverage: `attempt_route_indices`, `property_observed_route_indices`,
  `omitted_property_route_indices`, `empty_snapshot_route_indices`,
  `failed_route_indices`, `quarantined_route_indices`,
  `extraction_incomplete_route_indices`, `completeness`;
- selected observation: `outcome`, `temporal_occurrence_index`,
  `provenance_route_index`, `pre_horizon_seed`, `selected_received_at`,
  `observation_age_seconds`, `age_basis`;
- fence: `initial_source_token`, `initial_temporal_token`,
  `final_source_token`, `final_temporal_token`, `relation`;
- assurance: `payload_byte_check`, `metadata_same_read_check`,
  `provenance_closure`, `observation_content_relation`,
  `occurrence_membership_relation`, `attempt_coverage_membership_relation`,
  `captured_view_relation`, `semantic_compatibility`,
  `accountable_occurrence`;
- snapshot: `schema_version`, `request`, `fixed_limits`, `source_material`,
  `temporal_material`, `provenance_routes`, `selected`, `coverage`,
  `capture_fence`, `assurance`, `issues`, `content_fingerprint`;
- named-artifact row: `artifact_descriptor_index`, `relation`,
  `observed_byte_count`, `observed_captured_file_sha256`;
- selection result: `status`, `request`, `snapshot`, `issues`;
- store result: `status`, `membership_mode`,
  `snapshot_content_fingerprint`, `snapshot_validation_status`,
  `expected_artifact_count`, `expected_provenance_route_count`,
  `named_source_material_relation`, `captured_temporal_material_relation`,
  `source_membership_relation`, `temporal_membership_relation`,
  `named_artifact_results`, `issues`;
- offline validation result: `status`, `computed_fingerprint`,
  `embedded_fingerprint_relation`, `expected_fingerprint_relation`,
  `source_bytes`, `temporal_store_membership`, `detail_code`, `detail`.

The exception tree exposes exactly `error_code` and `message`. Strict indices
reject booleans and enforce nonnegative, in-range, ordered/unique forms where
required. The result validators enforce carry-once rules and impossible
status/relation combinations without store access.

## 7. Captured-view implementation

Selection performs the accepted sequence:

1. deep-reconstruct and validate request and fixed policy before I/O;
2. capture the initial seed-aware source inventory token;
3. capture the initial temporal inventory token;
4. read temporal material through the public one-transaction query seam;
5. read named source material once with the temporal seed ID;
6. validate source closure, content, routes, and both parity axes;
7. independently capture the final source and temporal tokens;
8. refuse changed membership or material/fence disagreement; and
9. derive the result only from already captured material.

The implementation reconstructs tokens returned by dependencies rather than
trusting Pydantic instances, including forged `model_construct` values. It
uses the accepted source-side seed discovery and seed parity behavior without
changing either lower implementation.

The fence claim is only `equal_at_observed_fences`. It does not claim a
distributed transaction, a global atomic snapshot, current evidence, or
detection after the final observed fences.

## 8. Selection, parity, and coverage behavior

The composition recomputes the inclusive cutoff, receipt-time occurrence
membership, complete `AttemptOrderKey`, optional one-item pre-horizon seed,
effective-time attempt coverage, `finished_at_no_response`, all accepted
coverage dispositions, source/temporal attempt parity, source/temporal
observation parity, strict provenance indices, the selected observation,
disclosure-only age, coverage summary, ordered issues, and assurance fields.

A pre-horizon seed is selected but excluded from in-horizon attempt coverage.
Receipt time and effective time remain separate. Reused byte-identical raw
payloads retain distinct acquisition-attempt occurrences while shared carried
material remains indexed once.

Issues 1–14 yield `refused` with no snapshot. Issues 15–16 yield one canonical
incomplete snapshot and no duplicate outer issues. With no applicable issue,
the result is `complete_within_declared_horizon`. Tests retain every applicable
issue in canonical order, including crossed source/temporal changes and the
simultaneous no-observation/no-attempt case.

No freshness, suitability, semantic, state, transition, flow, correctness,
or physical-occurrence judgment is made.

## 9. Canonicalization and fingerprint proof

Canonical snapshot input contains every Section 13 normative field except the
fingerprint itself, uses deterministic UTF-8 JSON ordering and exact scalar
normalization, and embeds no raw payload bytes. The fingerprint is tagged
SHA-256 over those canonical bytes.

Executable proof establishes:

- mutation of every bound leaf changes both canonical bytes and fingerprint;
- mapping insertion order does not change bytes or fingerprint;
- replacing a snapshot and its embedded fingerprint together can remain
  structurally self-consistent;
- mutation detection without stores requires a separately retained expected
  fingerprint;
- matching and mismatching independent expected fingerprints are distinct;
- no artifact outside the exact request/fence scope is claimed detected.

The fingerprint is not a signature, durable identity, authority endorsement,
trusted time, truth claim, or authentication of absent source bytes.

## 10. Store-independent validation

`validate_operational_evidence_snapshot(...)` performs no I/O. It converts
serialized values into a fresh graph, detects cycles, reconstructs every
nested model and union arm, rejects hidden extras and forged Pydantic
instances, and recomputes routes, selections, summaries, issues, assurance,
canonical bytes, and fingerprint.

It rejects boolean, missing, duplicate, reordered, and out-of-range indices;
stale derived values; substituted results; wrong union arms; forged nested
objects; cycles; and embedded fingerprint mismatch. It carries no snapshot
and always reports source bytes and temporal-store membership as
`not_rechecked`. Expected fingerprint relation is exactly `not_supplied`,
`matched`, or `mismatched` as applicable.

## 11. Store-bound revalidation

Both modes first validate the snapshot without I/O and then use the accepted
public named-material reread. They do not reselect evidence and repeat neither
the snapshot nor complete source/temporal material.

`require_equal_final_observed_membership` requires exact named material,
stable revalidation fences, and current source/temporal memberships equal to
the snapshot's final observed memberships. Stable growth is disclosed as
`observed_membership_changed` and does not pass this mode.

`named_captured_artifacts` separates exact named rereading from current
membership observation. It can return
`valid_for_named_captured_artifacts` when the frozen named bytes match even if
current membership differs or cannot be fully observed. It never calls the
historical evidence current or latest. Changed/unavailable named material is
reported separately and stops before membership I/O; source and temporal
membership relations remain distinct.

## 12. Red-before and adversarial repair evidence

The following failures were preserved in forward test commits before their
corresponding implementation or repair:

- `c434d2e`: public contract tests could not import
  `backend.evidence_assurance` (`ModuleNotFoundError`) before `f71c912`;
- `768084c`: nine selection cases failed at the deliberate unimplemented
  facade before `b4d63bd`;
- `ebb1b2b`: six offline-validation cases failed at the deliberate
  unimplemented validator before `ce5222e`;
- `3ca47ff`: seven store-revalidation cases failed at the deliberate
  unimplemented revalidation method before `71e6159`;
- `01e356a`: four adversarial regressions failed: an overly broad source
  import, missing public annotations, stale direct snapshot reconstruction,
  and substituted direct result reconstruction; `c85401b` repaired all four;
- `d8c6e7c`: a forged lower source inventory token was accepted and later
  misreported as a store change; it remained red pending the bounded repair;
- `d9ce3e8`: impossible public result/relation combinations were accepted;
  at this point both the prior forged-token and new relation regression were
  red; `32619ec` repaired both through deep token reconstruction and exact
  result invariants.

Each genuine adversarial defect has a permanent regression. The final
`70081b8` commit adds missing parity vocabulary and import/static coverage
without changing runtime behavior.

## 13. A01–A50 acceptance mapping

The executable matrix is complete and has no missing or extra row. Evidence
for each row is:

1. A01 — complete capture and exact selected closure:
   `test_complete_capture_protocol_routes_age_and_assurance` plus the accepted
   lower reader happy-path test.
2. A02 — payload checksum mutation:
   `test_payload_checksum_mutation_fails_closed` and parameterized structured
   source-integrity results.
3. A03 — payload/checksum substitution and named growth:
   named-reread mutation/growth lower tests plus named-mode revalidation.
4. A04 — metadata and every seed dependency bind the source token:
   the exact discrepancy regression and seed-dependency mutation matrix.
5. A05 — forged IDs, references, locators, fingerprints, and links:
   lower cross-row/stale-identity forgery tests and structured
   `provenance_closure_failure` selection cases.
6. A06 — extraction wrapper/content disagreements:
   nested-manifest and source-integrity parameter tests.
7. A07 — committed success without extraction/quarantine:
   structured `extraction_incomplete` selection coverage.
8. A08 — same-read metadata hashing:
   lower same-stored-bytes and exactly-once read tests, including named reread.
9. A09 — RFC 6901 escaping and malformed pointer refusal:
   lower malformed-pointer regression.
10. A10 — exact pointer value/type and no coercion:
    lower observation substitution and structured content-mismatch cases.
11. A11 — duplicate keys/malformed JSON classes:
    lower duplicate-key and parser refusal regressions.
12. A12 — distinct ordered coverage dispositions:
    nonobserving, failed, quarantined, omitted, empty, observed, and incomplete
    selection tests.
13. A13 — source attempt absent from temporal:
    `test_source_attempt_missing_from_temporal_coverage_fails_parity`.
14. A14 — temporal occurrence substitution/inconsistency:
    parameterized occurrence absence/inconsistency/parity test.
15. A15 — unequal valid source/temporal sets:
    parity tests for attempts and observations.
16. A16 — inclusive `as_of` cutoff:
    exact cutoff/age selection test and temporal lower regression.
17. A17 — complete `AttemptOrderKey` and order independence:
    temporal equal-receipt/order test and lower enumeration-order test.
18. A18 — separate receipt/effective axes:
    temporal separate-membership test and route/coverage selection assertions.
19. A19 — no-response failure uses `finished_at`:
    accepted temporal `finished_at_no_response` regression.
20. A20 — source time and clock segments are disclosure only:
    fixed policy and selection tests.
21. A21 — old cross-clock row disposition:
    no comparison API/error exists; altered fixed policy raises
    `EA_SELECTION_POLICY_INVALID` before I/O.
22. A22 — repeated byte-identical evidence remains distinct:
    repeated-payload selection and lower shared-payload tests.
23. A23 — exactly one pre-horizon seed:
    seed selection test and accepted source/temporal seed regressions.
24. A24 — seed excluded from attempt coverage:
    `test_pre_horizon_seed_is_selected_but_not_attempt_coverage`.
25. A25 — exact no-observation outcome:
    no-observation/no-attempt and temporal no-observation tests.
26. A26 — lifetime history above 4,096 with bounded horizon:
    accepted source and temporal bounded-lifetime tests.
27. A27 — in-horizon overflow refuses without truncation:
    accepted temporal and source limit regressions.
28. A28 — bounds and strict fixed limits:
    exact contract scalar tests and accepted aggregate-budget repair tests.
29. A29 — unsafe names/paths and path-free diagnostics:
    source unsafe-entry, named-reread unsafe/substitution, and no-leak tests.
30. A30 — pre-initial source mutation is captured consistently:
    `test_a30_change_completed_before_initial_fences_is_the_captured_view`.
31. A31 — source change after initial fence:
    `test_a31_source_change_after_initial_before_material_is_detected` plus
    the accepted seed-dependency matrix.
32. A32 — source change during named reads:
    `test_a32_source_change_during_named_material_read_is_detected` and named
    reader exactly-once/mutation tests.
33. A33 — source change after read/before final fence:
    `test_a33_source_change_after_material_before_final_fence_is_detected`
    plus seed-candidate replacement.
34. A34 — temporal change after initial/during transaction:
    first phase of the parameterized A34/A35 boundary regression.
35. A35 — temporal change after transaction/before final token:
    second phase of the A34/A35 boundary regression.
36. A36 — crossed source/temporal changes retain both issues:
    `test_a36_crossed_source_and_temporal_changes_retain_both` and seed parity.
37. A37 — change after both final fences is outside the claim:
    `test_a37_change_immediately_after_both_final_fences_is_not_claimed_detected`.
38. A38 — unsupported file/CAD/PDF routes:
    accepted lower non-DS-004 route refusals and EA issue vocabulary.
39. A39 — strict import isolation:
    exact AST dependency allowlist and no existing-consumer import tests.
40. A40 — exact fields/exports and no upper-layer vocabulary:
    contract field/literal/export tests and static package inspection.
41. A41 — exact age disclosure without admission judgment:
    inclusive-cutoff and age-decimal selection test.
42. A42 — incomplete horizon coverage:
    disposition and multi-issue incomplete snapshot tests.
43. A43 — source, temporal, named, membership, absence distinctions:
    unavailability selection and all store-revalidation relation tests.
44. A44 — exact scope and separate occurrence/coverage axes:
    accepted lower exact-scope test and EA parity substitutions.
45. A45 — hostile reconstruction at every public boundary:
    offline hostile tests, all-public-model extras test, direct snapshot/result
    tests, forged token test, and accepted lower hostile-reread tests.
46. A46 — snapshot-plus-fingerprint replacement remains structurally
    self-consistent: dedicated offline replacement test.
47. A47 — independent expected fingerprint comparison:
    dedicated matched/mismatched validation test.
48. A48 — store-independent no-I/O validation:
    serialized validation test with I/O bombs and exact `not_rechecked` fields.
49. A49 — deterministic serialization:
    reversed mapping/enumeration tests, accepted lower reproduction, and
    explicit hash seeds 1, 7, and 12345.
50. A50 — no network, connector, extraction, write, ambient clock, or
    environment discovery: runtime AST isolation plus dependency test doubles
    and accepted lower no-side-effect tests.

## 14. Captured-boundary mutation results

The A30–A37 boundary matrix passed as follows:

| Row | Injected boundary | Result |
| --- | --- | --- |
| A30 | Same-length valid source metadata mutation completed before initial fences | Complete captured view; no concurrent-change claim |
| A31 | Source mutation after initial token, before material | Refused with `source_store_changed_during_capture` |
| A32 | Source mutation during named material read | Refused with source-store-change or same-read typed integrity failure |
| A33 | Source mutation after material, before final source fence | Refused with `source_store_changed_during_capture` |
| A34 | Temporal mutation after initial token, before/during transaction | Refused with `temporal_store_changed_during_capture` unless coherently captured |
| A35 | Temporal mutation after transaction, before final temporal fence | Refused with `temporal_store_changed_during_capture` |
| A36 | Crossed source and temporal mutations | Both issues retained in normative order |
| A37 | Source mutation immediately after final fences | Complete fence-limited result; post-fence detection not claimed |

The accepted Slice A repair regressions additionally passed mutation of the
seed attempt, attempt run, raw-origin run, envelope, payload, extraction, and
observation content; each mutation changes the token or produces a typed
refusal. Source-selected and temporal-supplied seed disagreement fails closed.

## 15. Focused and component verification

All commands below ran against exact HEAD
`70081b821569a82192f8e3fd100c2eec14beadb8`, with bytecode and pytest cache
generation disabled.

- EA-only:
  `.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/evidence_assurance -q`
  — `58 passed in 10.25s`.
- EA plus the accepted 69-test Slice A repair/lower gate:
  `.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/evidence_assurance tests/data_sources/test_ea001_operational_evidence_integrity_repair.py tests/data_sources/test_ea001_operational_evidence_reader.py tests/test_ea001_slice_a_reproduction.py tests/test_ea001_slice_a_architecture.py tests/temporal_state/test_ea001_selection_material.py -q`
  — `127 passed in 15.85s`.
- Complete temporal suite plus architecture assertion:
  — `100 passed in 17.92s`.
- Complete data-source suite under restricted sandbox:
  — `384 passed, 1 error in 340.03s`; the sole error was localhost socket
  creation denied by the sandbox in
  `TestRealLoopbackTransport.test_get_redirect_refusal_and_proxy_isolation`.
- The exact loopback test rerun with separately permitted localhost binding:
  — `1 passed in 1.94s`.
- Complete model-kernel suite:
  — `1654 passed in 678.09s (0:11:18)`.
- Focused ledger and full FL deterministic reproduction preservation gate:
  — `13 passed in 153.14s (0:02:33)`.

The first combined focused run exposed one obsolete historical architecture
assertion that required the EA directory not to exist. It was updated narrowly
to assert the authorized sibling relationship while preserving lower-package
isolation. The final combined result above is the post-repair result.

## 16. Working full-repository verification

Command:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -ra`

Restricted-sandbox result: `3607 passed, 1 error in 1321.41s (0:22:01)`.
The only error was the same denied localhost socket setup. No test body failed.
The exact test was separately rerun with permitted loopback and passed:
`1 passed in 1.94s`.

Thus the reconciled working-tree result is 3,608 passing tests with one test
requiring the separately permitted loopback capability; there are no product
failures.

## 17. Fresh base-only verification

A detached clean worktree at exact HEAD was created at
`/tmp/ea001-sliceb-base-20260905` with a fresh virtual environment and only
the base plus development lock files installed.

- full suite under restricted sandbox:
  `3572 passed, 35 skipped, 1 error in 855.01s (0:14:15)`;
- all 35 skips were the declared unavailable CAD/PDF extras;
- the sole error was the same sandbox-denied localhost socket setup;
- separately permitted exact loopback rerun: `1 passed in 0.73s`;
- `venv/bin/pip check`: `No broken requirements found`;
- `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m compileall -q backend`:
  exit 0;
- detached HEAD exactly
  `70081b821569a82192f8e3fd100c2eec14beadb8`;
- `git status --short` empty and `git diff --check` passed.

The reconciled base-only column has 3,573 passing runnable tests, 35 expected
optional skips, and no product failure.

## 18. Fresh all-extras and CAD/STEP/PDF verification

A separate detached clean worktree at exact HEAD was created at
`/tmp/ea001-sliceb-extras-20260905` with a separate fresh virtual environment,
base plus development locks, and both hash-pinned CAD and PDF extra locks.

- full suite under restricted sandbox:
  `3607 passed, 1 error in 892.92s (0:14:52)`;
- the sole error was the same sandbox-denied localhost socket setup;
- separately permitted exact loopback rerun: `1 passed in 0.74s`;
- explicit CAD/STEP/PDF marked gate:
  `35 passed, 577 deselected in 43.12s`;
- `venv/bin/pip check`: `No broken requirements found`;
- `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m compileall -q backend`:
  exit 0;
- detached HEAD exactly
  `70081b821569a82192f8e3fd100c2eec14beadb8`;
- `git status --short` empty and `git diff --check` passed.

The reconciled all-extras column has all 3,608 tests passing with the loopback
capability supplied separately and no skips or product failures.

## 19. Determinism and lower-material preservation

Independent EA snapshot reproduction under `PYTHONHASHSEED=1`, `7`, and
`12345` produced identical values in all three processes:

- canonical snapshot bytes: `19,235`;
- canonical-bytes SHA-256:
  `36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`;
- embedded content fingerprint:
  `sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`.

The accepted lower-material regression gate remained green. It preserves both
documented Slice A reproductions:

- original non-seed lower material: `24,766` bytes, SHA-256
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
- corrected seed-aware token plus material: `11,528` bytes, SHA-256
  `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

No accepted lower serialization was rewritten or relabelled.

## 20. Authoritative preservation evidence

The complete suite and focused immutable gates verify:

- exactly 36 authoritative model records;
- revision exactly
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW counts exactly `1/1/0`;
- ledger aggregate exactly
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure exactly `660,516` bytes and SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- historical memberships replay and all accepted evidence, fixtures,
  artifacts, record identities, and revisions remain unchanged.

The accepted synthesis, correction report, Slice A acceptance, and Slice A
completion report digests also remain unchanged as listed in Section 2.

## 21. Dependency, isolation, whitespace, and checkout state

Working-tree `.venv/bin/pip check` reports `No broken requirements found`, and
working-tree backend compilation exits 0. AST isolation tests prove EA imports
only the approved public source and temporal modules plus its own sibling
module. No existing backend package imports EA. Static tests find no network,
connector, extraction, write, ambient-clock, environment-discovery, private
store, SQLite, or upper-layer dependency.

The following whitespace checks all pass with no output:

- working tree: `git diff --check`;
- Slice B range:
  `git diff --check b0ffc1b59fec4c4fcc93e90362f9ffe71862e8fa..HEAD`;
- full EA milestone range:
  `git diff --check 873df5bfc4fef2b6c8136612c7a9655048dd6b1b..HEAD`.

Immediately before this report was created, `git status --short` was empty.
After creation, the only expected worktree entry is this untracked completion
report. `.claude/settings.local.json` remains ignored and byte-identical at
SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 22. Exact assurance limits and unresolved decisions

This Slice B establishes only deterministic, read-only composition and
captured-view consistency at observed fences. It does not establish global
atomicity, currentness beyond the final fences, source truth, authentication,
semantic suitability, freshness admission, physical occurrence, identity or
authority endorsement, state, transition, or flow meaning.

No architecture layer, durable identity, persistence mechanism, cache,
database, ledger, receipt, signature, minter, connector, or write path was
added. No existing consumer was integrated. Slice C remains unauthorized.

There was no unresolved implementation discrepancy or owner design question
at this original stopping point. Owner review subsequently authorized only the
bounded integrity repairs recorded below; the corrected owner gate is stated
in Section 34.

## 23. Dated owner-review correction authority and starting evidence

Correction date: 2026-09-05.

The owner authorized only bounded R1–R4 integrity repairs on branch `ea001`
from exact starting HEAD
`70081b821569a82192f8e3fd100c2eec14beadb8`. Slice A remained accepted and was
not reopened. Slice C, upper-layer integration, authoritative demonstrations,
ledger appends, and Slice B acceptance remained unauthorized.

Repository guidance and the accepted synthesis were read again. The synthesis
remained byte-identical at SHA-256
`557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`.
The owner review and executable probes were read completely and verified as:

- `2026-09-05-ea001-slice-b-owner-review.md`: 175 lines, 8,984 bytes,
  SHA-256
  `675277b033bac0285eb258baac24fbbbff506f1cff4b9077b21f06baac5ff238`;
- `2026-09-05-ea001-slice-b-review-probes.py`: 153 lines, 6,497 bytes,
  SHA-256
  `c09384a15b2cc695f4bd118bb6391fb73f1b5ce6f97820d38c71f3d11b0e4b43`.

The starting worktree contained only this untracked completion report. Its
pre-correction digest was
`6ea322b5f6959fc25697876ed8785ab38c5ef4c21c2f0f8193c49f62f1f54337`.
`.claude/settings.local.json` was preserved outside scope.

Running the unmodified owner probes against the exact starting HEAD reproduced
the reviewed behavior:

- valid capture was complete; named revalidation was
  `valid_for_named_captured_artifacts`; equality revalidation was
  `matches_final_observed_membership`;
- rejected temporal capture leaked `IndexError`, and rejected source capture
  leaked `AttributeError`;
- rejected current temporal material supported a false fully observed/equal
  claim in named mode and leaked `ValidationError` in equality mode;
- an ordinary wrong expected fingerprint mismatched, while a caller-defined
  `str` equality object manufactured `matched`;
- an inadmissible membership-mode object caused six dependency calls before a
  late `ValidationError`;
- missing-fingerprint and unjustified-refusal result shapes reconstructed;
- substituted occurrence value produced generic parity, substituted
  observation identity produced absence, and a missing expected temporal event
  produced only generic parity.

## 24. Forward repair commits and exact changed files

The owner-review repair is the following forward-only sequence:

1. `d1d8ae06ed7ac12b6d76dd579934c05bd67fb0fb` —
   `test: reproduce EA-001 Slice B owner review defects`;
2. `a114d7956d08eab0fb6b3ee09364d3dfc044942b` —
   `fix: repair EA-001 Slice B integrity boundaries`;
3. `54a7f988c5123567058a0520e45359eb90056a6c` —
   `test: reject hostile EA membership strings`;
4. `932514a456bcafe690a94d2d774b61913c352fbf` —
   `fix: normalize EA public scalar inputs`.

The exact tested repaired implementation and final runtime/test HEAD is
`932514a456bcafe690a94d2d774b61913c352fbf`.

The repair range changes exactly:

- `backend/evidence_assurance/contracts.py`;
- `backend/evidence_assurance/queries.py`;
- `tests/evidence_assurance/test_owner_review_repairs.py`;
- `tests/evidence_assurance/test_parity.py`.

No lower reader, temporal implementation, accepted contract, public export,
fixture, evidence, ledger, membership, model record, or artifact-generation
file changed. The completion report remains uncommitted.

## 25. R1 rejected-material repair and valid twins

The permanent red-before command was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/evidence_assurance/test_owner_review_repairs.py \
  tests/evidence_assurance/test_parity.py -q
```

At `d1d8ae0`, it produced `10 failed, 3 passed in 8.06s`. The failures include
both rejected capture objects, both rejected-current-material modes, strict
scalar admission, normative diagnostics, and compact result invariants.

R1 now keeps dependency return values in candidate state until full nested
reconstruction succeeds. Invalid temporal capture returns a structured
`refused` selection with no snapshot and exactly
`invalid_bounded_material`; it does not index rejected material and does not
read source material. The observed call sequence is exactly source inventory,
temporal inventory, temporal material, final source inventory, and final
temporal inventory.

Invalid source capture likewise returns structured `refused` with no snapshot
and exactly `invalid_bounded_material`; it cannot derive a token or selection
from rejected content. Rejected current temporal material is
`not_fully_observed`: named mode may remain
`valid_for_named_captured_artifacts` solely when its separate exact source
reread matches, while equality mode is `refused`. Neither path claims temporal
membership equality.

The valid twin proves unchanged admission: a valid capture remains
`complete_within_declared_horizon`, pure validation is
`structurally_self_consistent`, named revalidation is
`valid_for_named_captured_artifacts`, and equality revalidation is
`matches_final_observed_membership`.

## 26. R2 strict scalar admission and adversarial follow-up

Expected fingerprints and membership modes are reconstructed before comparison
or dependency access. A wrong ordinary fingerprint and a hostile `str`
subclass with caller-defined equality both produce `fingerprint_mismatch` and
`mismatched`; a valid expected fingerprint remains `matched`. A non-string
expected fingerprint raises typed `EA_REQUEST_INVALID`.

An inadmissible membership-mode object raises typed `EA_REQUEST_INVALID`
before any source or temporal call. Its valid twin enters named rereading and
returns `valid_for_named_captured_artifacts`.

The first repair green run exposed one residual defect during the required
bounded adversarial review: Pydantic literal admission could still be fooled
by an invalid `str` subclass whose equality and hash imitated a valid mode.
The permanent regression at `54a7f98` failed alone as `1 failed in 5.25s`.
`932514a` repairs it by converting string subclasses to base-string content
before strict accepted-type reconstruction. The hostile mode now raises
`EA_REQUEST_INVALID` with zero dependency calls; accepted literal strings and
tagged fingerprints retain their exact public types and vocabulary.

## 27. R3 normative A13–A15 diagnostics

This correction supersedes the brief A13–A15 descriptions in Section 13 with
the following executable mapping:

- A13: removal of the expected temporal occurrence emits first
  `temporal_occurrence_absent / expected_temporal_event_absent`;
- A14: substituted observation identity, substituted value content, and
  substituted occurrence fields emit
  `temporal_occurrence_inconsistent` rather than absence or generic parity;
- A15: every independently applicable parity issue is retained after A13 in
  normative order:
  `attempt_membership_parity_failure`,
  `observation_membership_parity_failure`, then
  `retained_attempt_parity_failure`.

The missing-event regression therefore returns four ordered issues: A13 first,
then all three applicable A15 details. The substituted-occurrence regressions
return A14. Existing valid unequal-set parity vocabulary remains unchanged;
there was no global parity rename.

## 28. R4 compact result invariants and proof boundary

`OperationalEvidenceStoreRevalidationResult` now enforces the accepted local
status/field/issue table:

- a successful valid-snapshot result must carry its required snapshot content
  fingerprint;
- `invalid_snapshot` requires exactly its invalid-snapshot issue and the
  prescribed not-evaluated relations;
- named success and equality success require the relations that justify their
  status;
- named failure cannot be rewritten as success;
- an otherwise successful result cannot be rewritten as refusal without a
  refusal condition.

Permanent hostile reconstruction tests reject missing fingerprints,
unjustified refusal/success substitutions, and an invalid result with its
required issue removed. Valid named, equal-membership, and invalid-snapshot
twins reconstruct exactly from their compact serialized form.

Validation is intentionally limited to content carried by this compact result.
It does not invent authentication of an uncarried snapshot or absent stores.

## 29. Repair green evidence and exact public contract

After `a114d79`, the owner-review and parity modules passed `13 passed in
24.95s`, and the complete EA suite passed `67 passed in 80.20s`. The original
owner probe script then produced structured R1 outcomes, strict R2 outcomes,
the ordered A13–A15 diagnostics, and rejected both impossible R4 shapes.

After the adversarial regression and `932514a`, the owner-review repair module
passed `10 passed in 14.31s`, and the complete EA suite passed `68 passed in
41.37s`. No further genuine defect was found in the bounded review.

At the exact final HEAD, an independent export assertion confirms
`backend.evidence_assurance.__all__` is exactly the ordered 33-name list in
Section 5. No aliases, new public vocabulary, changed limits, or changed
canonical contract fields were introduced. The repaired implementation still
covers the complete A01–A50 matrix; the precise A13–A15 reconciliation is in
Section 27 and R1, R2, and R4 add permanent hostile boundary coverage.

## 30. Final focused, lower-repair, affected, and isolation verification

All commands below ran against exact HEAD
`932514a456bcafe690a94d2d774b61913c352fbf` after the last runtime/test change.

The combined EA and accepted Slice A lower-repair gate:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/evidence_assurance \
  tests/data_sources/test_ea001_operational_evidence_integrity_repair.py \
  tests/data_sources/test_ea001_operational_evidence_reader.py \
  tests/test_ea001_slice_a_reproduction.py \
  tests/test_ea001_slice_a_architecture.py \
  tests/temporal_state/test_ea001_selection_material.py -q
```

passed `137 passed in 48.73s`. Complete temporal plus architecture coverage
passed `100 passed in 45.20s`. Complete model-kernel coverage passed `1654
passed in 692.21s`.

Complete data-source coverage in the restricted sandbox collected 385 tests
and produced `384 passed, 1 error in 321.72s`; the sole error was the known
loopback socket setup `PermissionError`. The exact loopback test, rerun with
separately permitted socket access at the same HEAD, passed `1 passed in
2.17s`. The reconciled data-source column is therefore 385/385.

## 31. Working full-repository verification

The working full suite at the exact final HEAD collected 3,618 tests and
produced:

```text
3617 passed, 1 error in 1311.40s (0:21:51)
```

The only error was the same sandbox loopback setup restriction, not an
assertion failure. The exact failing loopback test passed separately with
permitted socket access (`1 passed in 2.17s`) at the same HEAD. Reconciled
working coverage is 3,618/3,618 with no test failure.

The focused immutable-preservation gate, including the authoritative 36-record
ledger and complete FL reproduction file, passed `13 passed in 158.20s`.

## 32. Fresh base-only checkout and environment

A separate detached worktree at
`/tmp/ea001-sliceb-repair-base-20260905` was verified at exact HEAD
`932514a456bcafe690a94d2d774b61913c352fbf` with a fresh virtual environment.
The repository's ordinary base and development requirements installed
successfully. The preliminary attempt to apply `--require-hashes` to the
range-based base requirement files correctly refused before installing
anything; those files are not hash-pinned, so the repository-prescribed
ordinary install was then used.

The base-only full suite produced:

```text
3582 passed, 35 skipped, 1 error in 823.04s (0:13:43)
```

All 35 skips were the expected unavailable CAD/PDF optional-extra cases. The
only error was the sandbox loopback socket setup restriction. The exact test
passed with separately permitted socket access as `1 passed in 0.75s`.
`pip check` reported no broken requirements, backend compilation exited 0,
the checkout was clean, and `git diff --check` passed.

## 33. Fresh all-extras checkout and optional coverage

A separate detached worktree at
`/tmp/ea001-sliceb-repair-extras-20260905` was likewise verified at exact HEAD
`932514a456bcafe690a94d2d774b61913c352fbf` with a distinct fresh virtual
environment. Base/development requirements installed normally; the hash-pinned
CAD and PDF requirement files installed separately with `--require-hashes`.

The all-extras full suite produced:

```text
3617 passed, 1 error in 868.12s (0:14:28)
```

The only error was the sandbox loopback setup restriction. Its exact permitted
rerun passed `1 passed in 0.75s`, reconciling the column to 3,618/3,618. The
explicit CAD/STEP/PDF selection passed `35 passed, 577 deselected in 43.85s`.
`pip check` reported no broken requirements, backend compilation exited 0,
the checkout was clean, and `git diff --check` passed.

## 34. Corrected determinism, preservation, checks, and owner gate

Independent valid-case EA snapshot reproductions under `PYTHONHASHSEED=1`,
`7`, and `12345` remained identical in all processes:

- canonical bytes: 19,235;
- canonical SHA-256:
  `36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`;
- embedded fingerprint:
  `sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`.

The valid-case digest did not change. The combined 137-test gate preserved
both accepted lower reproductions: original 24,766-byte material SHA-256
`ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`
and corrected 11,528-byte seed-aware token/material SHA-256
`494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

Preservation verification remained exact:

- 36 authoritative model records;
- revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW `1/1/0`;
- ledger aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure 660,516 bytes and SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- historical memberships, evidence, fixtures, and artifacts unchanged.

Working `.venv/bin/pip check` reported no broken requirements and backend
compilation exited 0. All final whitespace checks passed with no output:

- `git diff --check`;
- `git diff --check 70081b821569a82192f8e3fd100c2eec14beadb8..HEAD`;
- `git diff --check b0ffc1b59fec4c4fcc93e90362f9ffe71862e8fa..HEAD`;
- `git diff --check 873df5bfc4fef2b6c8136612c7a9655048dd6b1b..HEAD`.

The final worktree contains only this untracked report. The settings file is
byte-identical at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

The correction is confined to `backend/evidence_assurance` and focused EA
tests. It adds no acceptance record and makes no contract, lower-reader,
temporal, consumer-integration, or authoritative artifact change. Nothing was
pushed, merged, rebased, reset, amended, cherry-picked, or history-rewritten.
Slice C remains unauthorized. There is no unresolved owner decision other than
whether to accept repaired Slice B at
`932514a456bcafe690a94d2d774b61913c352fbf`.

END OF EA-001 SLICE B COMPLETION REPORT
