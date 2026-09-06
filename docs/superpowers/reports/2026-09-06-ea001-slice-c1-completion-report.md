# EA-001 Slice C1 Completion Report

Date: 2026-09-07

Status: original C1 completion evidence, supplemented by the bounded
expected-fingerprint integrity repair at
`867cfb9c4c374f0603ad7db1827ba09d6a511308`; repaired C1 owner acceptance
pending; Slice C2 unauthorized

## 1. Authority and exact checkpoints

The owner approved only Slice C1 from the corrected design: contracts, one pure
derivation, and red-first adversarial tests. Work ran on branch `ea001` from
accepted base `c34fc6868be9a554095b2fb10dae17436c617a71`.

The exact final runtime/test implementation checkpoint is
`4216981c393921da6d05ec06f736b52e3584297e`. Every final verification command
in this report ran at that checkpoint. The later completion-report/status
commit is documentation-only and is intentionally identified in the terminal
receipt rather than represented as a tested runtime change.

Before work, all accepted design files matched their required digests:

- corrected proposal:
  `dd7200df0ab500a6d1366ae77b629ac13e9c7a710c2b0c63a78b733aeed804a4`;
- proposal correction report:
  `eac53c09eacaa6b47a29f6248a313540a56061e88761cb6ccf848835ab4fec56`;
- checkpoint discrepancy report:
  `3b4f9e22d8934e3a33088a02f49c421f07fd8a64169d976941f22b934dc9d402`;
- accepted EA synthesis:
  `557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`.

## 2. Commits and changed files

The ordered C1 commits before this documentation-only completion record are:

1. `2304b71740ccf9eb68ab9a949acbf880f86c38d9` —
   `docs: authorize EA-001 Slice C1`.
2. `a6da5dd75d32e45eceda0155c9ef4b8771808914` —
   `test: define EA-001 Slice C1 alignment contract`.
3. `162e83c1727ce48cb026b29792c6e340c9187553` —
   `feat: add pure evidence alignment derivation`.
4. `f4534f02690f47b6529919c40602d7457dd1eed2` —
   `fix: reject boolean alignment indices`.
5. `6529eb0791a3e5d6d0a5dd6fa4ab19469c72a007` —
   `test: permit approved evidence alignment consumer`.
6. `4216981c393921da6d05ec06f736b52e3584297e` —
   `test: prove alignment hash-seed determinism`.

Production additions are exactly:

- `backend/evidence_alignment/__init__.py` — marker only; no C2 exports;
- `backend/evidence_alignment/contracts.py`;
- `backend/evidence_alignment/derivation.py`.

Focused tests are confined to `tests/evidence_alignment/`, except for the
necessary historical Slice B architecture assertion update in
`tests/evidence_assurance/test_adversarial_contracts.py`, which permits only
the newly approved alignment leaf as an EA consumer. Documentation additions
are the accepted design/audit records, C1 authorization, C1 plan, this report,
and the minimal current-status wording in `CLAUDE.md`.

No runtime or public contract changed in evidence assurance, observation
compatibility, model state, identity binding, temporal state, or data sources.

## 3. Exact C1 public definitions

`contracts.py` defines exactly the corrected C1 names:

- `EvidenceAlignmentError`;
- `EvidenceAlignmentQueryError`;
- `EvidenceAlignmentQueryErrorCode = Literal["ALIGNMENT_REQUEST_INVALID"]`;
- `OperationalEvidenceAlignmentStatus`, ordered as
  `aligned_with_complete_evidence`, `aligned_with_incomplete_evidence`,
  `not_aligned`, `not_evaluated`;
- the nine-reason `OperationalEvidenceAlignmentReason` in accepted precedence;
- `OperationalEvidenceAlignmentRequest` with fields, in order:
  `schema_version`, `selection`, `compatibility`,
  `expected_snapshot_fingerprint`;
- `OperationalEvidenceAlignmentResult` with the accepted nineteen fields in
  exact Section 9 order.

`derivation.py` defines only
`align_operational_evidence_with_value_compatibility(request)` as the public
function. The root `backend.evidence_alignment` package deliberately has no
`__all__` and exposes none of the final eight C2 names. Package-level exports
remain a separate Slice C2 gate.

Both public models are frozen, forbid extras, and revalidate instances. The
query error exposes exactly `error_code` and `message`; messages are nonempty,
bounded to 300 characters, and reject paths, credential forms, and hostile
string subclasses.

## 4. Derivation and integrity behavior

The request boundary converts every carried Pydantic object to ordinary public
field content with cycle, hidden-extra, unsupported-value, hostile-subclass,
and boolean-index checks. It then reconstructs the accepted EA selection and
accepted `VariableValueCompatibilityResult` through their public types before
derivation. Forged `model_construct`/`model_copy` instances do not retain
trusted instance state.

For a non-refused selection, the function calls the public pure
`validate_operational_evidence_snapshot(...)` exactly once, supplies the
independent expected fingerprint, and carries the computed result exactly once
in the output. There is no caller validation field and no store-revalidation
input or output.

Alignment requires the same normalized UTC cutoff, a matching six-field
consumer locator, exactly one field-equal public `TemporalOccurrence`, and
recomputed EA-internal closure from that occurrence's attempt to the snapshot
scope endpoint. The consumer never supplies or implies the endpoint. Value,
unit, checksum, timestamp, name, or occurrence ID alone never aligns.

Attachment and shape/unit/specification outcomes are disclosed but do not gate
identity alignment. Complete and incomplete EA selections remain distinct;
`aligned_with_incomplete_evidence` means only exact occurrence alignment and
does not mean complete, usable, current, semantically correct, or assured
assessment evidence. Result reconstruction recomputes every compact derived
field without I/O.

## 5. C01-C38 executable mapping

| Rows | Permanent focused evidence |
| --- | --- |
| C01 | Happy complete alignment plus exact request/result fields and literal order. |
| C02 | Pre-horizon incomplete selection aligns only under the incomplete status. |
| C03 | No EA observation produces `no_selected_observation`. |
| C04-C05 | Pre-horizon seed and in-horizon selected roles are distinct. |
| C06 | Same value under a different occurrence ID does not align. |
| C07-C14 | Every listed occurrence field class is mutated through a valid consumer twin; same-ID changes produce exact sorted mismatch fields. |
| C15 | All six shared locator fields are independently required. |
| C16 | Broken selected-attempt/endpoint closure is typed invalid; the closed twin aligns. |
| C17 | Different cutoffs fail; differently zoned representations of the same instant normalize equal. |
| C18 | Consumer revisions/identity disclosures are derived from and equal their carried result; stale echoes reject. |
| C19 | Refused EA selection is not evaluated and carries no snapshot validation. |
| C20 | Invalid/hidden/substituted snapshot content is typed request misuse; the valid twin reaches pure validation. |
| C21 | Coherent snapshot-plus-embedded-fingerprint replacement remains self-consistent without an independent expectation; the retained original expectation detects mismatch. |
| C22 | Expected fingerprint matched/mismatched/absent twins and exactly-once internal validation. |
| C23-C24 | No candidates and locator-equal no-observation are distinct. |
| C25-C26 | Unattached evidence and conflicted specification do not upgrade or suppress exact occurrence alignment. |
| C27-C29 | One/zero/duplicate exact matches and explicit selector behavior, including reachable duplicate refusal. |
| C30-C33 | Forged models, cycles, extras, hostile scalars, boolean/negative indices, and stale/oversized result fields reject. |
| C34-C36 | No I/O, store access, query-facade call, reselection, or reverse import; only approved public lower surfaces are imported. |
| C37 | Reversed mapping construction and independent hash seeds 1, 7, and 12345 produce equal results. |
| C38 | Exact exception tree, fields, formatting, code admission, and safe-message behavior. |

The focused suite asserts that the combined row map is exactly C01 through C38.
C39 root-package `__all__` is intentionally not implemented; C1 instead proves
that it remains absent. C40 preservation is covered by the immutable gates in
Sections 7 and 8.

## 6. Red-before, first green, and adversarial repair

At red-first commit `a6da5dd75d32e45eceda0155c9ef4b8771808914`, before any
production package existed, the focused command produced exactly `44 failed, 1
passed in 9.21s`. All 44 failures were `ModuleNotFoundError` at the deliberately
absent package; the one passing test proved the C01-C38 matrix map was complete.

The initial implementation then reached `45 passed in 4.59s`. Before that
first green, a falsey empty-candidate test helper had accidentally selected its
fallback input; the helper was corrected explicitly and did not require a
production change.

The bounded post-green adversarial review reproduced one genuine product
defect: an older lower `TemporalOccurrence` contract accepts boolean
`sweep_position` through integer coercion. The new upper strict-reconstruction
boundary initially allowed that hostile nested value to reach comparison. A
permanent targeted test failed exactly `1 failed in 4.32s` with “DID NOT RAISE
EvidenceAlignmentQueryError”. The repair rejects boolean `sweep_position`,
singular `_index`, and members of `_indices` collections before lower
reconstruction. The targeted repair/C21 twins passed `2 passed in 3.27s`, and
the then-complete focused suite passed `47 passed in 5.04s`.

The review also made the C37 proof explicitly cross-process. The three-seed
test passed before its test-only commit. No other production defect was
reproduced. No lower contract or architecture was reopened.

## 7. Final C1 verification at the exact implementation HEAD

All commands below ran at
`4216981c393921da6d05ec06f736b52e3584297e` with bytecode-cache generation
disabled for test runs.

1. Complete focused C1:
   `pytest tests/evidence_alignment` — `48 passed in 16.24s`.
2. Accepted EA/Slice A lower-repair gate:
   `pytest tests/evidence_assurance` plus both focused data-source repair files,
   Slice A reproduction/architecture, and temporal selection material —
   `137 passed in 18.89s`.
3. Explicit architecture/no-I/O gate: C1 isolation, Slice A architecture, and
   EA adversarial contracts — `20 passed in 15.77s`.
4. Complete relevant consumer/model regressions:
   `pytest tests/observation_compatibility tests/model_state` —
   `219 passed in 60.93s`.
5. Immutable model/FL/lower reproduction gate: committed-ledger tests,
   authoritative aggregate test, complete FL reproduction file, and Slice A
   lower reproduction — `18 passed in 157.18s`.
6. `.venv/bin/pip check` — `No broken requirements found` (the sandbox-disabled
   pip-cache warning was informational).
7. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend` — exit
   0 with no output.

No test in these authorized columns requires loopback socket setup, and no
loopback error occurred. The full repository suite and separate clean base/all-
extras checkouts were deliberately not run or claimed; they belong to the
unauthorized C2 verification gate.

## 8. Determinism and preservation

Independent disposable reproductions under hash seeds 1, 7, and 12345 were
byte-identical in all three processes:

- valid EA canonical snapshot: 19,235 bytes, SHA-256
  `36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`,
  with equal embedded `sha256:` fingerprint;
- accepted original lower material: 24,766 bytes, SHA-256
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
- accepted corrected seed-aware token/material: 11,528 bytes, SHA-256
  `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

The authoritative ledger remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remain `1/1/0`, and the record-file aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The FL disclosure remains exactly 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.

The proposal, correction report, checkpoint discrepancy report, and accepted
EA synthesis retain the Section 1 hashes. No historical membership, evidence,
fixture, ledger record, artifact, accepted lower serialization, or accepted
contract was altered.

## 9. Limitations and excluded claims

Slice C1 is one pure join for one already-computed
`VariableValueCompatibilityResult`. It introduces no generic multi-consumer
framework, digest, store, cache, database, ledger, receipt, identity, revision,
writer, reader, query facade, clock, or connector. It neither selects evidence
nor recomputes compatibility.

Occurrence alignment is not source authentication, semantic suitability,
freshness, currentness, physical occurrence, state, transition, flow,
correctness, safety, health, diagnosis, causality, recommendation, or control.
Store-bound EA revalidation remains an independent caller operation and does
not participate in this v1 result.

Package-level exports, final full-repository verification, base/all-extras
clean checkouts, and any authoritative demonstration remain Slice C2 or later
work and require separate owner authorization.

## 10. Git integrity and owner gate

Before this documentation-only completion commit, the working tree was clean,
`git diff --check` passed, and
`git diff --check c34fc6868be9a554095b2fb10dae17436c617a71..HEAD` passed.
The same working and full-C1-range checks are rerun after the report commit and
reported in the terminal receipt. `.claude/settings.local.json` remains
ignored, untouched, and byte-identical at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

This original report is supplemented by
`docs/superpowers/reports/2026-09-07-ea001-slice-c1-integrity-repair-report.md`;
the repaired C1, rather than this report's earlier implementation checkpoint
alone, is the pending owner gate. It does not authorize or accept Slice C2.
Nothing was pushed, merged, rebased, reset, amended, cherry-picked, forced, or
history-rewritten.

END OF EA-001 SLICE C1 COMPLETION REPORT
