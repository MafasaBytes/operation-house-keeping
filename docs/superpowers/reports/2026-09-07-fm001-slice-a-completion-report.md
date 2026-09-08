# FM-001 Slice A Completion Report

## 1. Completion status and owner gate

FM-001 Slice A, including the owner-directed bounded integrity repair, is
complete and submitted for owner validation on local branch `fm001` at exact
tested repair and final HEAD
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`.

The repair began from exact tested implementation
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf`. Slice A has not yet been owner
accepted. This report is deliberately untracked and is not part of the tested
implementation. The owner gate remains acceptance of repaired Slice A and a
separate decision about Slice B.

No Slice B surface, fixture, demonstration, authoritative append, identity,
VSM migration or wrapper, lower-layer change, FA-001 work, facade, UI, or
connector was added. Nothing was pushed, merged, rebased, reset, amended,
cherry-picked, or history-rewritten.

## 2. Starting checkpoint and historical-report preservation

The starting checkout was verified as branch `fm001`, HEAD
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf`, with only the untracked original
completion report outside the clean tracked tree. That report was verified at
468 lines, 25,801 UTF-8 bytes, and SHA-256
`9d8a0f4a075267b75d6369740b348d0f2641b66ccd221d72354abcd22a6b75fa`.

Its bytes were preserved unchanged at:

`docs/superpowers/reports/2026-09-08-fm001-slice-a-pre-repair-completion-report.md`

The preserved file remains 468 lines and 25,801 bytes at the same SHA-256.
Commit `513fd699d460d59001940718bfbc609ca0ce52cd` records that historical receipt
separately with subject `docs: preserve FM Slice A pre-repair report`. The
historical file retains the pre-repair conclusions; this corrected report does
not rewrite them retroactively.

## 3. Authority and normative correction

The bounded repair follows the accepted FM synthesis, ADR-0021, Slice A plan,
and the owner resolution preserving context-independent VSM. Current digests
are:

| Authority | SHA-256 |
| --- | --- |
| corrected synthesis | `baca77b5c6080075f8dc59ba58c0574d6421cc27eb1b9a3d899883be3e5e0d18` |
| ADR-0021 | `b9fe17dbd59fce45e10ee8cd0f18008be1cdb7ecb1f1c1bae10cb1134538ce15` |
| Slice A plan | `8935c6473db8a94fb469bcbe2ab87b25ecc88ed330dcdfae95878143767a97f1` |
| VSM context owner resolution | `68a7d7c095d90661478e35459f7791cb0d64a3d15cb700d095b35569ef5a8ee6` |

Only the synthesis wording implicated by R3 changed. It now names exact VSM
variable/dimension/system/edition/code/revision/ID substitution and states
that VSM has no context. ADR-0021, the plan, the owner resolution, historical
discrepancy/checkpoint reports, and accepted record contracts remain
unchanged.

## 4. Repair commits and changed files

The repair consists of three forward commits after the starting implementation:

| Commit | Subject | Content |
| --- | --- | --- |
| `513fd699d460d59001940718bfbc609ca0ce52cd` | `docs: preserve FM Slice A pre-repair report` | byte-identical historical receipt |
| `ea947c8ec55d8e968836606ed3e76a6b0f42f3eb` | `fix: compare FM disagreement across active roots` | R1 production fix and permanent R1/R2 tests |
| `6210d3c250b96f54b764a365cb0a3a988d9bf9f6` | `docs: correct FM context-independent VSM wording` | R3 synthesis correction |

The repair range changes exactly four tracked files:

- `backend/model_kernel/store.py`;
- `tests/model_kernel/test_flow_measurement_integrity_repair.py`;
- `docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`; and
- `docs/superpowers/reports/2026-09-08-fm001-slice-a-pre-repair-completion-report.md`.

The repair range is 688 insertions and 7 deletions. The sole production change
is 8 insertions and 5 deletions in the existing FM index derivation. No schema,
record ID, canonical bytes, subject, effective body, lifecycle rule, export,
query, persistence seam, or package boundary changed.

## 5. R1 failing-before evidence

The permanent R1 tests were run against the exact starting production at
`530637ee4aa147c4e6a85c15e12e24c1c40d7faf` before the production repair:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel/test_flow_measurement_integrity_repair.py -k 'r1_' -q`

Result: 3 failed, 2 passed, 5 deselected in 5.81 seconds. The failures exactly
reproduced the defect:

1. one internally conflicted root was falsely indexed as cross-root
   disagreement;
2. two active roots with equal two-body sets were falsely indexed; and
3. a mixed world falsely included an inactive third root.

The valid twins passed before repair: an active root plus an inactive root did
not disagree, and two active singleton roots with unequal bodies did disagree.
This isolated the defect to unioning tip bodies and then returning every
subject root, rather than comparing per-root current body sets.

## 6. R1 repaired rule and fixed evidence

Production now derives one non-empty current effective-body set per active
root, compares those sets between distinct active roots, and publishes the
deterministically sorted active root IDs only when at least two distinct body
sets exist. Same-root multiplicity remains lineage conflict. Roots with no
current tip are inactive and do not participate. No winner is selected.

The five retained R1 tests now pass. They prove:

- one forked root with two current bodies is not cross-root disagreement;
- one active and one inactive root do not disagree;
- two active singleton roots with unequal bodies yield exactly both roots;
- two active internally conflicted roots with equal body sets do not disagree;
- a mixed three-root world includes only the active unequal participants in
  deterministic record-ID order.

The complete new repair file passes 10 tests, and the combined FM Slice A
files pass 53 tests. Inspection of the adjacent root-by-body and
root-by-subject derivations found no second root-versus-lineage aggregation
defect: those indexes intentionally disclose their independent dimensions,
whereas only the disagreement index performs cross-root set comparison.

## 7. R2 four-orientation evidence

R2 was a missing positive-evidence and report defect, not a production
narrowing defect. Before the production fix, the five collected R2 cases
already passed against `530637e` in 4.66 seconds. The pre-repair report's claim
that only `aligned` and `opposite` were accepted was therefore wrong.

The permanent tests pin the exact ordered literals:

1. `aligned`;
2. `opposite`;
3. `unsigned_magnitude`;
4. `not_applicable`.

All four construct through the generic builder, have distinct immutable
subjects and content-derived IDs, append under valid support, survive full
plain-content reconstruction, retain exact spelling/order, index correctly,
and survive explicit reversed replay. Cross-orientation supersession from
`aligned` to each other literal refuses as immutable-subject drift. Null,
Boolean, empty, unknown, mixed-case, hyphenated, and `str`-subclass forms
refuse; exact `not_applicable` is the valid twin.

The final five-seed gate ran both FM files under `PYTHONHASHSEED=1`, `7`,
`12345`, `2468`, and `97531`; every run passed all 53 tests.

## 8. R3 stale contextual-VSM correction

The red-before repository search found a stale FM-A35 sentence asserting a
context/subject substitution check at synthesis line 669 and an equivalent
ambiguous threat phrase at line 615. The current synthesis replaces both
without altering any VSM record or lower contract.

FM-A35 now reads exactly:

`Exact measured-actual VSM variable/dimension/system/edition/code/revision/ID substitution rejects; VSM has no context.`

A repository-wide current-authority search found only affirmative
context-independent wording in the synthesis, Slice A plan, ADR/owner
resolution, and current report. Every live contract scopes VSM checks to its
own exact fields and assigns context matching only to FLD/VPA. The historical
discrepancy, incomplete checkpoint, continuation checkpoint, and preserved
pre-repair report were deliberately excluded from normative correction and
remain byte-preserved history.

## 9. Contract and acceptance-row consequences

R1 corrects the implementation evidence for independent-root disagreement;
it does not change the accepted FM subject or lifecycle. The rows most directly
closed are FM-S13 through FM-S16, FM-S27 through FM-S29, and corresponding
FM-A37 behavior. Same-root fork/conflict, complete convergence, withdrawal,
support history, and no-winner behavior remain as previously reported.

R2 completes positive and hostile evidence for FM-S10 and the public contract:
all four accepted orientation literals are exact immutable dimensions. R3
corrects FM-A35 to the already owner-resolved context-independent VSM model.
All other FM-S01 through FM-S36 evidence remains recorded in the preserved
pre-repair receipt and is re-exercised by the final focused, affected,
model-kernel, architecture, and full-repository suites.

The public Slice A surface remains exactly two FM records,
`FlowMeasurementAssociation` and
`FlowMeasurementAssociationWithdrawal`, appended to the accepted 203-name
model-kernel export prefix for 205 total names. `ModelQueries` has no
`flow_measurement*` method and no Slice B result/status/index model exists.

## 10. Focused and affected verification

Every final gate in this section used exact HEAD
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`, with bytecode writes and pytest
cache disabled where applicable.

| Gate | Result |
| --- | --- |
| R1-only red-before at `530637e` | 3 failed, 2 passed, 5 deselected in 5.81s; exact defect reproduced |
| R2-only valid/hostile twins before production repair | 5 passed, 5 deselected in 4.66s |
| new integrity-repair file after repair | 10 passed in 4.36s |
| complete FM Slice A files | 53 passed in 9.98s |
| FM plus affected FL/VP/VS/ES files | 195 passed in 24.56s |
| complete model-kernel suite | 1,707 passed in 1,057.73s |
| complete system-identity/identity-binding suite | 327 passed in 9.62s |
| architecture/import-isolation selection | 82 passed in 62.70s |
| frozen artifacts/revision preservation test | 1 passed in 8.72s |

The affected selection contains both FM files plus flow records/store,
variable-port records/store, and variable semantics. Static inspection of the
production repair found no new import and no reference to evidence assurance,
transition assessment, temporal state, data sources, connectors, SQLite,
sockets, environment discovery, or an ambient clock.

## 11. Working-tree full repository verification

Command:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`

Final aggregate: 3,853 passed in 2,782.36 seconds (46:22), with no skip or
error.

No separate working-tree loopback reconciliation was required: the loopback
test passed inside this uninterrupted aggregate.

## 12. Fresh base-only verification

A newly recreated detached checkout at
`/tmp/fm001-base-clean-final` was verified at exact HEAD
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`. It used the independently
installed base/dev environment at `/tmp/fm001-base-clean-20260908/venv`.

Final sandbox aggregate: 3,817 passed, 35 expected optional-extra skips, and
one localhost-bind setup error in 2,198.97 seconds (36:38). The error was
`PermissionError: [Errno 1] Operation not permitted` while the fixture tried
to bind `127.0.0.1`.

Separate permitted loopback reconciliation at the same commit: 1 passed in
0.84 seconds. The split accounting therefore reconciles 3,818 runnable tests
plus the 35 expected skips; it is not described as one uninterrupted pass.

`pip check` returned `No broken requirements found`; backend compilation,
exact HEAD, clean status, and full-milestone whitespace checks passed.

## 13. Fresh all-extras and optional-format verification

A separate newly recreated detached checkout at
`/tmp/fm001-extras-clean-final` was verified at the same exact HEAD. It used
the independently installed base/dev plus hash-pinned CAD/PDF environment at
`/tmp/fm001-extras-clean-20260908/venv`.

Final sandbox aggregate: 3,852 passed and one localhost-bind setup error in
2,266.79 seconds (37:46), with no skip. The error was the same sandbox
`PermissionError` while binding `127.0.0.1`.

Separate permitted loopback reconciliation at the same commit: 1 passed in
0.92 seconds. The split accounting reconciles all 3,853 runnable tests; it is
not described as one uninterrupted pass.

The explicit all-extras CAD/STEP/PDF gate selected data-source contracts and
format detection, STEP ingestion/extraction, PDF ingestion/contracts/
coordinates/detection/extraction/redaction, and structural STEP claims. It
passed 160 tests in 72.18 seconds. `pip check`, backend compilation, exact
HEAD, clean status, and full-milestone whitespace checks also passed.

## 14. Determinism and independent reproductions

Both complete FM test files passed 53 tests under each of five hash seeds:
`1`, `7`, `12345`, `2468`, and `97531`. The independent witness constructs a
withdrawn independent root and a forked-and-merged root, reconstructs forward
and reverse membership, and compares the revision plus all 17 FM indexes.
Working runs under all five seeds and independent base/all-extras runs produced
identical content:

- 30,485 UTF-8 bytes;
- SHA-256 `c880b68f0669cd8fa391ef11ebb136fb968389f718a4c57b9b16f50d16413df7`;
- revision
  `mrv_c277c9222c98b3212b36ac0327df1b5b71934309516d5e07f79aca791a90e602`.

The repair does not alter record, effective-body, or revision bytes. Three
independent environments reproduced the accepted lower and TA evidence:

| Reproduction | Bytes | SHA-256 |
| --- | ---: | --- |
| original in-horizon lower material | 24,766 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` |
| corrected seed-aware token plus source material | 11,528 | `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f` |
| accepted TA private canonical result | 195,429 | `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97` |

The original lower shape remained source artifacts/attempts/observations
`10/2/2` and temporal occurrence/attempt coverage `2/2`. The seed-aware shape
remained token members/material artifacts/attempts/runs/observations
`5/5/1/1/1`. The TA bytes retained no trailing newline.

## 15. Dependency, compilation, whitespace, and repository state

Working, fresh base-only, and fresh all-extras `pip check` each returned
`No broken requirements found`. `python -m compileall -q backend` exited zero
without diagnostics in all three environments.

These whitespace checks passed without output before the report was sealed:

- working tracked and unstaged diff;
- repair range `530637ee4aa147c4e6a85c15e12e24c1c40d7faf..HEAD`;
- full FM milestone range `a069cb6..HEAD`;
- working-tree report whitespace; and
- full milestone range in both detached clean checkouts.

Both detached worktrees were at the exact tested HEAD and reported empty
`git status --short`. The branch has no upstream. `origin` remains configured
for fetch/push, but no network history operation was performed. Final working
status contains only this corrected untracked report.

`.claude/settings.local.json` was not staged or modified and remains at
SHA-256 `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 16. Protected-state preservation

Direct checks, the dedicated preservation test, and each final full suite
establish:

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
- accepted lower-material, TA, memberships, evidence, identities, fixtures,
  ledgers, revisions, disclosures, and canonical artifacts unchanged.

The authoritative ledger contains no FMA or FMW record. Every FM world is
disposable or reconstructed in memory.

## 17. Truth boundary, limitations, and exact scope

An admitted FMA remains only an evidence-backed declaration of direct
measurement relevance between one exact variable and one exact participant
port of one exact logical flow in one exact context and orientation, under six
pinned model records. It does not establish observation, amount, rate,
current flow, occurrence, physical connection, transport, continuity,
conservation, causality, correctness, health, safety, or recommended action.

R1 changes only derived disagreement indexing. R2 changes only permanent test
coverage and this report's description. R3 changes only current normative
wording to match the accepted context-independent VSM resolution. No accepted
lower behavior or public signature changed.

Slice B remains unauthorized. There is no Slice B query/result/status surface,
no fixture or demo, zero authoritative FMA/FMW records, no FA-001 work, no
identity mint, no VSM migration/context wrapper, no lower-layer or upper-layer
integration, and no push or merge.

## 18. Owner question

Accept the repaired FM-001 Slice A at exact tested repair HEAD
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6` and separately authorize Slice B?

END OF FM-001 SLICE A COMPLETION REPORT
