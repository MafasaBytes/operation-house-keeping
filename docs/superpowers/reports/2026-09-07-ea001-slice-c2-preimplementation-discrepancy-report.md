# EA-001 Slice C2 Preimplementation Checkpoint Discrepancy Report

Date: 2026-09-07

Status: fail-closed checkpoint stop; C2 not started

## 1. Authority and stop condition

The owner authorized EA-001 Slice C2 only from exact starting HEAD
`64c0a8ba7678c7567c2b596947167535cf8fbab3` on branch `ea001`. The handoff
requires the branch, HEAD, clean tracked tree, and four frozen document hashes
to be verified before the administrative C1-acceptance commit, and requires a
discrepancy stop if a material fact differs.

The branch and HEAD match. `git status --short` was empty. The ignored
owner-local `.claude/settings.local.json` remains untouched at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.
The accepted synthesis, repaired proposal, and C1 integrity-repair report
match their stated hashes. The current C1 completion-report path does not.

## 2. Exact mismatch

The handoff freezes:

```text
docs/superpowers/reports/2026-09-06-ea001-slice-c1-completion-report.md
expected SHA-256 5c728116fbc458352d9ce7967d3286ce96ce82991e678d1a3469306fb52310e6
```

At required starting HEAD
`64c0a8ba7678c7567c2b596947167535cf8fbab3`, that path is 269 lines and
14,122 UTF-8 bytes with SHA-256:

```text
cb32954e76e5b4fcdb718a20f1af2f072fd9a7743d7b577a09700db3edc8b031
```

The expected digest is reproducible from the historical blob at original C1
completion commit `c94b5629bea928e976779be6cb4cf035264dc88d`:

```text
git show c94b5629bea928e976779be6cb4cf035264dc88d:docs/superpowers/reports/2026-09-06-ea001-slice-c1-completion-report.md | sha256sum
5c728116fbc458352d9ce7967d3286ce96ce82991e678d1a3469306fb52310e6  -
```

The current digest is independently reproducible from the required starting
HEAD:

```text
git show 64c0a8ba7678c7567c2b596947167535cf8fbab3:docs/superpowers/reports/2026-09-06-ea001-slice-c1-completion-report.md | sha256sum
cb32954e76e5b4fcdb718a20f1af2f072fd9a7743d7b577a09700db3edc8b031  -
```

## 3. Cause and compatibility consequence

Forward documentation commit
`43084ceaff1fdc57143b7499b93c006e4e1fef86` amended the report during the
owner-authorized C1 integrity repair. It changed only the status paragraph and
terminal owner-gate wording so the original evidence points to the repair
report and does not request acceptance of the superseded implementation alone.
That commit is an ancestor of the exact owner-specified C2 starting HEAD.

Therefore both facts are preserved, but they identify different blobs:

- `5c728116...` is the reviewed original C1 completion-report blob in history;
- `cb32954e...` is the status-amended file at the required repaired-C1 HEAD.

Treating the historical digest as if it were the current path digest would be
false. Restoring the older bytes in a new commit would remove the accepted
repair-status linkage, while resetting or rewriting history is expressly
forbidden. No such change is authorized or attempted.

## 4. Work not performed

No C1 owner-acceptance record or administrative acceptance commit was made.
No root `backend.evidence_alignment` export, `__all__`, README, C39/C40 test,
runtime repair, fixture, ledger, evidence, artifact, or lower-layer file was
created or changed. No full-suite or clean-checkout verification was started,
because it would verify an implementation gate whose frozen administrative
checkpoint has not been reconciled.

Nothing was pushed, merged, rebased, reset, amended, cherry-picked, forced, or
history-rewritten. Slice C2 remains unimplemented and final EA-001 acceptance
has not occurred.

## 5. Required owner resolution

One explicit resolution is required before C2 can begin:

1. confirm that the accepted original C1 completion report is the historical
   blob at `c94b5629...` with SHA-256 `5c728116...`, and separately accept the
   current status-amended path at starting HEAD `64c0a8ba...` with SHA-256
   `cb32954e...`; or
2. provide a different exact current-path digest and narrowly authorize any
   required forward documentation treatment.

After that resolution, C2 can resume from the unchanged required HEAD without
reopening C1 implementation or altering accepted history.

END OF EA-001 SLICE C2 PREIMPLEMENTATION DISCREPANCY REPORT
