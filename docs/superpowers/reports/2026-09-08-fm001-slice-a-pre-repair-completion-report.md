# FM-001 Slice A Completion Report

## 1. Completion status and owner gate

FM-001 Slice A is complete and is submitted for owner validation at exact
tested implementation commit
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf` on local branch `fm001`.

The continuation started at the owner-directed partial checkpoint
`2d63f167590bffe3b365ee0f54ee606f151f40c3`. The accepted FM-001 design base
is `a069cb6`; no history was rewritten. This report is intentionally left
untracked and is not part of the tested implementation.

The requested owner decision is limited to acceptance of Slice A at the exact
tested commit and, only if the owner chooses, separate authorization of Slice
B. This report records no Slice B authorization or acceptance.

## 2. Authority and frozen design inputs

Implementation followed the accepted final synthesis, ADR-0021, corrected
Slice A plan, and the owner resolution preserving context-independent VSM.
Their final bytes are:

| Input | SHA-256 |
| --- | --- |
| `docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md` | `557e3b99bf80a05e4c205558f1cdb971805950c46524954b9a2ca959b3031518` |
| `docs/adr/0021-explicit-flow-to-measurement-association.md` | `b9fe17dbd59fce45e10ee8cd0f18008be1cdb7ecb1f1c1bae10cb1134538ce15` |
| `docs/superpowers/plans/2026-09-07-fm001-slice-a-implementation-plan.md` | `8935c6473db8a94fb469bcbe2ab87b25ecc88ed330dcdfae95878143767a97f1` |
| `docs/superpowers/reports/2026-09-07-fm001-vsm-context-owner-resolution.md` | `68a7d7c095d90661478e35459f7791cb0d64a3d15cb700d095b35569ef5a8ee6` |

The plan received one narrow wording reconciliation: FM-S16 now says that a
partial same-root repair remains conflicted, while cross-root convergence,
foreign parents, cycles, self-parenting, and duplicate parents refuse. This
matches synthesis Section 14 and the accepted challenger statement that
partial same-root convergence remains conflict. The synthesis and ADR were
not changed.

The two previously committed incomplete reports remain historical and were
not rewritten:

| Report | SHA-256 |
| --- | --- |
| `docs/superpowers/reports/2026-09-07-fm001-slice-a-incomplete-checkpoint-report.md` | `247514723c9de19b6e6df3959fb8335a7b560e252c847ecede4323ed96c0d8da` |
| `docs/superpowers/reports/2026-09-08-fm001-slice-a-continuation-checkpoint-report.md` | `96d8d3c4d33d77224c72ac1508ea2e063fdd603e4f0dc7ab7a1a5929c297b4d7` |

## 3. Slice A commit record

The partial checkpoint already contained the accepted record-contract and
export work at `64eaf8a` and `7f2e6cb`. The implementation continuation added
these forward commits, in order:

| Commit | Subject | Purpose |
| --- | --- | --- |
| `5fab14e975f5e06f4c4c8dc3adebcc92ef47a390` | `feat: validate FM-001 association lifecycles` | support admission, lifecycle, indexes, replay, atomicity, and first focused suite |
| `4fa319c8b630110f3dcaf6bfc97c3f5b78dbd415` | `test: harden FM-001 Slice A integrity boundaries` | hostile twins, exact predecessor export order, support/context/evidence/withdrawal coverage |
| `f903ae4e95a768a3a39fa5c2cf09d0055f4851c6` | `test: complete FM-001 export count reconciliation` | repair six exact 203-to-205 public-count assertions |
| `23881df8fb3dcb79398b80e146fe663b662336ac` | `test: include FM records in flow export inventory` | include the two new records in the exact Flow export set |
| `a11576d1167d27930cd49e5989bc7d381ba3fda4` | `test: reconcile aggregate model-kernel exports for FM` | include FM records in the aggregate contract inventory |
| `6636af36d4cd4069afb2dda23a47057a66150a3a` | `test: reconcile FM record prefix inventory` | pin exact 30 record classes/prefixes after adding `fma_`/`fmw_` |
| `68172f0c3c1f6c0d19f781eed6e3a867fff0986c` | `test: pin FM partial-convergence behavior` | retain partial-same-root conflict and complete-convergence valid twin |
| `530637ee4aa147c4e6a85c15e12e24c1c40d7faf` | `test: close FM Slice A adversarial coverage` | explicit support-history, ancestry, effective-body, locus, hostile reconstruction, and no-I/O twins |

No commit was amended. Nothing was pushed, merged, rebased, reset,
cherry-picked, or history-rewritten.

## 4. Changed files

From the directed starting checkpoint through the tested implementation, the
tracked change is 1,083 insertions and 13 deletions in these 14 files:

- `backend/model_kernel/__init__.py`;
- `backend/model_kernel/canonical.py`;
- `backend/model_kernel/contracts.py`;
- `backend/model_kernel/store.py`;
- `docs/superpowers/plans/2026-09-07-fm001-slice-a-implementation-plan.md`;
- `tests/model_kernel/test_flow_architecture.py`;
- `tests/model_kernel/test_flow_measurement_slice_a.py`;
- `tests/model_kernel/test_flow_query_contracts.py`;
- `tests/model_kernel/test_port_records.py`;
- `tests/model_kernel/test_state_query_contracts.py`;
- `tests/model_kernel/test_structural_evidence_arm.py`;
- `tests/model_kernel/test_transition_query_contracts.py`;
- `tests/model_kernel/test_variable_registration.py`; and
- `tests/model_kernel/test_variable_value_specification.py`.

Production changes are confined to the existing `backend.model_kernel`
contract, canonicalization, store-validation/index, and package-export seams.
There is no new package, facade, consumer, query module, fixture, model file,
identity, or persistent artifact.

## 5. Exact public record surface

Slice A exposes exactly two new names:

- `FlowMeasurementAssociation`; and
- `FlowMeasurementAssociationWithdrawal`.

`FlowMeasurementAssociation` has, in order: `record_kind`, `schema_version`,
`record_id`, `flow_anchor_id`, `variable_anchor_id`,
`participant_port_anchor_id`, `context`, `orientation`,
`flow_registration_record_id`, `variable_registration_record_id`,
`port_registration_record_id`, `flow_declaration_record_id`,
`variable_port_association_record_id`,
`variable_semantic_declaration_record_id`, `evidence`, `supersedes`,
`recorded_at`, `authority`, and `note`.

`FlowMeasurementAssociationWithdrawal` has, in order: `record_kind`,
`schema_version`, `record_id`, `withdraws`, `recorded_at`, `authority`, and
`note`. It has no evidence field and is not citable through
`ModelRecordEvidence`.

The root export list contains exactly 205 unique names. The original 203-name
prefix remains byte-order exact with digest
`7821c7582f1332addca8fd467004c477262ea4e679c33f6bbe0a22831db83ce1`;
the two FM record names are appended once, in the order above. There is no
FM-specific builder or alias: both records use the existing generic
`build_record` boundary.

No `ModelQueries` method begins with `flow_measurement`; no Slice B result,
status, row, index model, query method, or alternative public name exists.

## 6. Canonical identity and admission

Both records use the existing content-derived full-SHA-256 record-ID
mechanism and exact `fma_`/`fmw_` prefixes. Authoritative reconstruction
rejects stale IDs, unknown fields, malformed unions, scalar subclasses, and
forged Pydantic state before the object reaches semantic indexing.

Positive admission requires exact, membership-present FRG, VRG, PRG, FLD,
VPA, and VSM pins. The FMA flow, variable, participant port, and context must
agree with those exact records. FLD and VPA match the FMA context. VSM remains
context-independent and must match the exact variable plus:

`project_local / ohk-observation-roles-1 / measured_actual`.

No temporal import or contextual VSM wrapper was added. VSP, quantity kind,
unit, names, topology, PIF, PCN, observations, EA, and TA cannot admit FM.

The participant port must occur in exactly one FRG side and in the matching
FLD pins. `source` or `sink` is derived into an immutable index and is never a
serialized caller field. Only the exact `aligned` or `opposite` orientation
literals are accepted. Null, Boolean, aggregate, whole-flow, storage,
boundary, control-volume, flow-ID, non-port, and unknown locus forms refuse.

## 7. Lifecycle, DAG, withdrawal, and support history

Each parentless association is an independent root. Parents are canonical,
unique, membership-present FMA records with the same six-dimensional subject
and the same derived root. Same-root forks expose multiple current tips.
Partial same-root repair remains a conflict; a later record superseding every
remaining same-root tip completes convergence.

Missing, foreign, cross-root, duplicate, self, cyclic, changed-subject, and
withdrawn-parent lineages refuse. Independent roots may have identical
effective bodies and corroborate, or different effective bodies and disclose
disagreement. No timestamp, authority, ID, filename, construction order, or
append order selects a winner.

Withdrawal targets exactly one eligible current tip. Unknown targets fail
reference closure; superseded, already-withdrawn, duplicate, and other
ineligible targets fail the FM withdrawal invariant. A sibling fork tip can
be withdrawn without withdrawing the other tip.

The six pins remain historical bytes. A pinned VPA that later becomes
superseded, withdrawn, or conflicted remains a valid exact dependency in the
same selected membership; it is not retargeted to a newer support record.
This is model-record history, not a currentness or truth claim.

## 8. Immutable indexes, replay, and append atomicity

`LoadedModel` now carries immutable mappings for:

- association and withdrawal records;
- exact subject;
- flow/context, variable/context, and port/context;
- parent IDs, successor IDs, root IDs, and ancestry;
- current tips by root;
- withdrawal IDs by target and withdrawn-by IDs;
- derived participant role;
- canonical six-pin effective body by record;
- record IDs and root IDs by effective body;
- root IDs by subject; and
- cross-root disagreeing root IDs by subject.

All tuple members and mapping keys are deterministically ordered. The
effective body includes the exact six support record IDs and excludes
ancestry, evidence, note, authority, timestamps, record IDs, and filenames.

Replay consumes an explicit membership only. Reversed input produces the
same revision and indexes. A pre-FM 36-record membership reconstructs with
empty FM mappings; a disposable later FM membership reconstructs its own
fixed dependencies without enumerating the authoritative model directory or
retargeting support.

`ModelStore.append` validates the prospective complete membership before its
atomic file write. Tests snapshot record bytes before each refused append and
prove no record file or membership change afterward.

## 9. Red-before and adversarial repair record

The directed starting checkpoint lacked FM support closure, lifecycle,
derived indexes, withdrawal handling, and replay behavior. Focused tests for
those paths were first exercised red against that partial implementation;
the missing `LoadedModel` mappings and absent FM validation prevented the
valid and hostile worlds from satisfying the Slice A rows. Commit `5fab14e`
made those retained tests green.

The first-green review then exposed six genuine integration or contract-test
defects, each retained as a regression with a valid twin:

1. FM names interrupted the accepted 203-name export order; the new digest
   gate failed until `4fa319c` moved the two names to the end.
2. Six exact export-count assertions still expected 203; each failed and was
   corrected to the accepted 205 in `f903ae4`.
3. The exact Flow-family export inventory omitted FMA/FMW; its failing set
   comparison was repaired in `23881df`.
4. The aggregate model-record contract inventory omitted the new classes;
   the failing inventory was repaired in `a11576d`.
5. Prefix/union inventory assertions still expected 28 record classes and
   prefixes; their failing exact comparisons were repaired to 30 in
   `6636af3`.
6. A test/plan draft treated a partial same-root repair as a refused append;
   the accepted lifecycle instead retains conflict until complete
   convergence. `68172f0` pins the red partial-conflict and green complete-
   convergence twins without changing the already-correct production DAG.

The final bounded review added explicit hostile tests at `530637e`. Its first
run was `41 passed, 2 failed`: both failures were test-oracle defects. Unknown
withdrawal IDs correctly fail generic membership reference closure, and a
wrong union supplied directly to Pydantic correctly raises `ValidationError`.
After correcting only those expectations, the file passed all 43 tests.

The final review proves support-history retention, exact corroboration and
disagreement, missing/duplicate/self/cyclic parents, unknown/foreign
withdrawals, every excluded locus class, exact orientation, flow/variable/
port/context parent drift, `model_construct`, hidden state, wrong nested
union, and pure no-I/O validation. It exposed no production defect after the
first green.

## 10. FM-S01 through FM-S12 mapping

| Row | Retained evidence |
| --- | --- |
| FM-S01 | exact positive fields/order, frozen Pydantic contract, `fma_` builder ID, stale-ID refusal |
| FM-S02 | exact withdrawal fields/order, no evidence, `fmw_` builder ID, uncitable union |
| FM-S03 | generic `build_record` constructs both; export/query negative assertions forbid aliases |
| FM-S04 | exact 30-prefix inventory, collision checks, record-union dispatch, full model-kernel gate |
| FM-S05 | content-derived canonical builder tests plus stale orientation and forged-field IDs refuse |
| FM-S06 | six parameterized missing-pin refusals and valid exact-support twin |
| FM-S07 | nonparticipant refusal; source role derived from FRG and indexed; no caller role field |
| FM-S08 | FLD/VPA cross-context substitutions, wrong-variable/wrong-kind/wrong-token VSM, and valid context-independent shared VSM |
| FM-S09 | wrong edition, command-target, quantity-kind arms refuse; exact measured-actual twin admits |
| FM-S10 | null, Boolean, unknown, case-changed, and subclass orientations refuse; two exact literals are immutable |
| FM-S11 | null/Boolean/aggregate/whole-flow/storage/boundary/control-volume/flow-ID/nonparticipant loci refuse before store access |
| FM-S12 | retained-parent flow, variable, port, context, and orientation drift refuse; new parentless root is the valid twin |

## 11. FM-S13 through FM-S24 mapping

| Row | Retained evidence |
| --- | --- |
| FM-S13 | multiple same-subject parentless roots admit and are independently indexed |
| FM-S14 | identical six-pin root bodies corroborate; alternate exact VSM pin produces body disagreement without a winner |
| FM-S15 | same-root fork has two tips; full two-tip convergence leaves one tip |
| FM-S16 | partial same-root repair remains two-tip conflict; missing, duplicate, self, cyclic, foreign, and cross-root parents refuse |
| FM-S17 | successor of a withdrawn parent refuses; one sibling tip remains eligible after selective withdrawal |
| FM-S18 | one current-tip withdrawal admits, is indexed, and has no evidence/citability |
| FM-S19 | unknown, superseded, already-withdrawn, duplicate, and wrong-prefix targets refuse |
| FM-S20 | exact `ModelRecordEvidence` union excludes FMW while admitting FMA |
| FM-S21 | empty positive evidence refuses; canonical owner/model-record evidence and reference closure admit |
| FM-S22 | FMA keeps its exact VPA pin when that VPA is later superseded, withdrawn, or conflicted |
| FM-S23 | effective-body equality ignores audit/ancestry fields and changes for an alternate one-of-six support pin |
| FM-S24 | refused support, participant, lineage, and withdrawal appends preserve the pre-call file snapshot |

## 12. FM-S25 through FM-S36 mapping

| Row | Retained evidence |
| --- | --- |
| FM-S25 | authoritative 36-record revision loads/replays with empty FM maps; preservation gate passes |
| FM-S26 | explicit reversed membership replay is deterministic and does not enumerate a directory |
| FM-S27 | all record/subject/flow/variable/port/context/root/body/ancestry/tip/withdrawal indexes have exact content and immutable mappings |
| FM-S28 | reverse construction and five hash seeds produce identical indexes, revision, and witness bytes |
| FM-S29 | forged nested instances, `model_copy`, `model_construct`, hidden state, wrong union, stale ID, scalar subclass, duplicate, self, and cycle attacks refuse |
| FM-S30 | no public result or result-index type exists in Slice A; Boolean result-index testing remains Slice B work |
| FM-S31 | validation precedes writing and every refused append leaves existing bytes/revision unchanged |
| FM-S32 | exact 205 unique exports, original 203-name digest, and two-name append order pass |
| FM-S33 | 82-test architecture/isolation gate and static import scan exclude every prohibited sibling/upper dependency |
| FM-S34 | spies forbid built-in/Path file access and sockets while contract, canonical builder, and collection validation pass; `ModelStore` remains the explicit I/O boundary |
| FM-S35 | `ModelQueries` has no `flow_measurement*` method and no Slice B model is exported |
| FM-S36 | milestone diff and authoritative inventory show no fixture, demo, identity mint, ledger append, or FA-001 artifact |

## 13. Focused, affected, kernel, identity, and isolation verification

All final commands used exact implementation
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf` with bytecode writes disabled and
pytest cache disabled.

| Gate | Final result |
| --- | --- |
| FM-specific Slice A file | 43 passed in 6.55 seconds |
| FM plus affected FL/VP/VS/ES model-kernel files | 185 passed in 25.55 seconds |
| Complete model-kernel suite | 1,697 passed in 1,238.32 seconds (20:38) |
| Complete system-identity/identity-binding suite | 327 passed in 7.42 seconds |
| Architecture/import-isolation selection | 82 passed in 63.45 seconds |
| Frozen artifact/revision preservation test | 1 passed in 10.62 seconds before the final test-only commit; repeated inside every final full suite |

The architecture selection covered all repository isolation modules plus
model-kernel flow and transition architecture. Static inspection of the
production diff found no new import and no reference to evidence assurance,
transition assessment, temporal state, data sources, connectors, SQLite,
sockets, environment discovery, or an ambient clock.

## 14. Working-tree full repository verification

Command:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`

Final sandbox result: 3,842 passed and one loopback setup error in 2,883.36
seconds (48:03), with no skip. The error was `PermissionError: [Errno 1]
Operation not permitted` while the fixture attempted to bind `127.0.0.1`.
The exact loopback test was rerun separately with permission at the same
commit and passed 1 test in 2.79 seconds. The split accounting therefore
reconciles all 3,843 runnable tests; it is not described as one uninterrupted
aggregate pass.

The only permitted reconciliation, if present, is the exact real-loopback
transport test. A sandbox `PermissionError` while opening `127.0.0.1` is
recorded as a setup restriction, never as an implementation pass. Its
separately permitted rerun result is recorded after the aggregate completes.

## 15. Fresh base-only verification

A new detached worktree at the exact tested commit used the independently
created base environment at
`/tmp/fm001-base-clean-20260908/venv`. That environment was installed from
`requirements.txt` and `requirements-dev.txt`. Initial sandboxed package
installation encountered restricted network/DNS access; the separately
permitted installation completed successfully.

Final sandbox aggregate: 3,807 passed, 35 expected optional-extra skips, and
one sandbox-denied loopback setup error in 2,110.08 seconds (35:10).

Separate permitted loopback reconciliation: 1 passed in 0.84 seconds at the
same commit. The split accounting reconciles 3,808 runnable tests plus the 35
expected skips.

`pip check`, backend compilation, exact HEAD, milestone whitespace, and clean
Git status are recorded in Section 18.

## 16. Fresh all-extras and optional-format verification

A separate new detached worktree at the exact tested commit used
`/tmp/fm001-extras-clean-20260908/venv`, installed in the required sequence
from base/dev, hash-pinned CAD, and hash-pinned PDF requirement sets. Initial
sandboxed dependency download encountered the same restricted network/DNS
condition; the separately permitted install completed successfully.

Final sandbox aggregate: 3,842 passed and one sandbox-denied loopback setup
error in 2,174.36 seconds (36:14), with no skip.

Separate permitted loopback reconciliation: 1 passed in 0.82 seconds at the
same commit. The split accounting reconciles all 3,843 runnable tests.

The explicit all-extras CAD/STEP/PDF gate selected data-source format,
detection, STEP ingestion/extraction, PDF ingestion/contracts/coordinates/
detection/extraction/redaction, and structural STEP-claim tests. Final result:
160 passed in 63.00 seconds.

## 17. Determinism and independent reproductions

The final FM test file ran independently with `PYTHONHASHSEED` values `1`, `7`,
`12345`, `2468`, and `97531`: every seed passed all 43 tests, in 16.36, 7.27,
7.31, 7.04, and 7.21 seconds respectively.

An independent disposable witness created one withdrawn independent root and
one forked-and-merged root, reconstructed forward and reverse membership,
compared all 17 FM index mappings and revision content, then serialized the
six FM records, revision, and indexes as deterministic canonical JSON. It
produced the same result for working seeds `1`, `7`, `12345`, fresh-base seed
`2468`, and fresh-all-extras seed `97531`:

- 30,485 UTF-8 bytes;
- SHA-256 `c880b68f0669cd8fa391ef11ebb136fb968389f718a4c57b9b16f50d16413df7`;
- merged-root revision
  `mrv_c277c9222c98b3212b36ac0327df1b5b71934309516d5e07f79aca791a90e602`.

Both accepted lower reproductions were independently rerun in working, base,
and all-extras environments and remained exact:

| Lower material | Bytes | SHA-256 | Shape |
| --- | ---: | --- | --- |
| original in-horizon source plus temporal | 24,766 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` | source artifacts/attempts/observations `10/2/2`; temporal occurrence/attempt coverage `2/2` |
| corrected seed-aware token plus material | 11,528 | `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f` | token 5 members; material artifacts/attempts/runs/observations `5/1/1/1` |

The accepted TA result also independently reproduced in all three
environments at 195,429 bytes and SHA-256
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.
No expected deterministic byte sequence changed.

## 18. Dependencies, compilation, whitespace, and Git state

Working, fresh base-only, and fresh all-extras `pip check` each returned
`No broken requirements found`. `python -m compileall -q backend` exited zero
without diagnostics in all three environments.

The following whitespace checks exited zero without output before this report:

- working tracked diff;
- continuation range `2d63f167590bffe3b365ee0f54ee606f151f40c3..HEAD`;
- full FM milestone range `a069cb6..HEAD`; and
- full milestone range in both clean checkouts.

Both clean worktrees reported empty `git status --short`. Final report
whitespace, section-continuity, ending-marker, digest, and working status are
recorded after the report bytes are sealed.

The local branch has no upstream tracking relationship. `origin` remains
configured for fetch and push, but no push or merge was performed.
`.claude/settings.local.json` was never staged or modified.

## 19. Protected baseline preservation

Direct checks and the final full suites establish:

- exactly 36 authoritative record files;
- revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW `1/1/0`;
- TRG/TRD/TRW `0/0/0`;
- FMA/FMW `0/0`;
- whole-ledger aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure 660,516 bytes at SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- VSM `vsm_053882...` at SHA-256
  `371527c7bd45c3118043b3da3ab2f17bb34769eacea4dd48e84eb148c71ea33a`;
- VSM `vsm_3b4b829...` at SHA-256
  `b04377e1a5385a2a301ef288a0a211fcf06602914a36a2da334615915659730f`;
- all accepted memberships, evidence, identities, fixtures, ledgers,
  revisions, disclosures, and canonical artifacts unchanged; and
- `.claude/settings.local.json` at SHA-256
  `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

The authoritative ledger contains no FM record. Every FM lifecycle world used
temporary model stores or pure in-memory reconstruction.

## 20. Limitations, exact scope, and owner question

An admitted FMA is only an evidence-backed model declaration that one exact
variable is directly-measurement-relevant to one exact participant port of
one exact logical flow in one exact context and orientation, under six pinned
model records. It does not establish a measurement, observation, amount,
rate, current flow, occurrence, physical connection, transport, continuity,
conservation, causality, correctness, health, safety, or recommended action.

Slice A added no query conclusions and makes no currentness judgment about
support. It did not read EA, TA, temporal, observation, connector, vendor,
identity, or upper-layer state. It added no store beyond the existing model
ledger, no database/cache, no fixture/demo, and no authoritative append.

Slice B remains unauthorized. FA-001, a demonstration, a second consumer,
ledger append, identity mint, VSM migration/context wrapper, numeric/unit
work, occurrence/history, UI, facade, and connector work remain absent.

Owner question: accept FM-001 Slice A at exact tested implementation
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf` and separately authorize Slice B?

END OF FM-001 SLICE A COMPLETION REPORT
