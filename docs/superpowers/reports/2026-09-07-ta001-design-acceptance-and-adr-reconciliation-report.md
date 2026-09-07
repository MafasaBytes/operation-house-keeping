# TA-001 Design Acceptance and ADR Reconciliation Report

Date: 2026-09-07

Status: documentation gate complete; TA-001 implementation not started

## 1. Authority and verified starting checkpoint

This documentation-only gate records final owner acceptance of the corrected
TA-001 design, closes the accepted EA-001 ADR debt, allocates the TA-001 ADR,
documents the existing evidence-assurance package, and reconciles current
status. It implements no TA behavior.

Work began from branch `main` with `HEAD`, `main`, and `origin/main` all equal
to accepted base `948374eec3cd49596fe19548a58a4fb10760a433`, subject
`docs: reconcile root README through EA-001`. No local or remote `ta001`
branch and no `ta001` worktree existed. Local branch `ta001` was created from
that exact base without reset, rebase, merge, cherry-pick, or history rewrite.

The starting working tree contained only the three expected untracked TA-001
design documents. The ignored owner-local
`.claude/settings.local.json` was present at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`
and was never staged or edited.

## 2. Accepted frozen design evidence

All three inputs were verified before mutation and rechecked after the first
documentation commit:

| Document | Lines | UTF-8 bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `docs/superpowers/proposals/2026-09-07-ta001-codex-lead-proposal.md` | 877 | 49,616 | `a8130d3146af7c159d739b6c63b9e0c398fd0bf4f1fa363d99559c476a0cf146` |
| `docs/superpowers/reports/2026-09-07-ta001-codex-lead-proposal-challenger-audit.md` | 469 | 28,641 | `b87d607d7ab17bf59bff10678175443303dc81c41726923f40d29034032fdad1` |
| `docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md` | 1,068 | 60,204 | `99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062` |

The synthesis is the normative design authority. It resolves both required
audit corrections and all six observations, fixes the strict independent
expected-fingerprint gate, accepts the exact 134,217,728-byte / 200,000-node /
depth-128 limit triple, adds the forged-index and exhaustive-reachability
acceptance rows, requires disposable positive worlds, and closes every owner
question. The proposal and audit remain frozen historical review evidence.

## 3. First documentation commit and exact files

The first commit is
`733fd8cdade96510caae6e8b7b155dfdd2ab776f`, subject
`docs: accept TA-001 design and reconcile evidence ADRs`.

It changed exactly these ten documentation files:

1. `CLAUDE.md`;
2. `README.md`;
3. `backend/evidence_alignment/README.md`;
4. `backend/evidence_assurance/README.md`;
5. `docs/adr/0019-content-bound-operational-evidence-selection-and-assurance.md`;
6. `docs/adr/0020-evidence-gated-declared-transition-assessment.md`;
7. `docs/superpowers/proposals/2026-09-07-ta001-codex-lead-proposal.md`;
8. `docs/superpowers/reports/2026-09-07-ta001-codex-lead-proposal-challenger-audit.md`;
9. `docs/superpowers/reports/2026-09-07-ta001-final-design-owner-approval.md`; and
10. `docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`.

The complete staged name set and diff were reviewed before commit. No runtime
source, test, fixture, model, ledger, evidence, temporal data, identity,
membership, generated artifact, requirement, or package export was staged.

## 4. Owner approval and ADR sequence

The final design owner-approval record is 73 lines and 3,149 UTF-8 bytes at
SHA-256
`0497a328e683487e70a19f61e11203272364097677ab01ff379b78a0c1f06021`.
It records the strict fingerprint rule, exact limits, pure leaf composition,
no-facade/no-demonstration/no-occurrence boundary, zero unresolved questions,
ADR order, and separate implementation gate.

ADR filenames are contiguous and unique from `0001` through `0020`.
ADR-0019 records already accepted EA-001 at status `EA-001 complete and owner
accepted`; it does not redesign EA. ADR-0020 records exact status `TA-001
design owner accepted; implementation not started`; it does not claim that a
TA package or TA tests exist.

The ADR receipts at the first commit are:

- ADR-0019: 127 lines, 6,720 UTF-8 bytes, SHA-256
  `f58496bc03f788c154118c4b64193e2bf5987d0724560179ced76407078519a9`;
- ADR-0020: 104 lines, 5,702 UTF-8 bytes, SHA-256
  `d49ec30107de83e33ea3d9d45545d75ec1adb6c8d1876eddcdaa3a516f96517f`.

Their final lines are exactly `END OF ADR-0019` and `END OF ADR-0020`. The
owner-approval record ends exactly with
`END OF TA-001 FINAL DESIGN OWNER APPROVAL`.

## 5. Status and package-documentation reconciliation

Root status continues to describe the implemented milestone sequence as
complete through EA-001, not through TA-001. It separately identifies TA-001
as an owner-accepted design, links both the synthesis and ADR-0020, states that
implementation has not started, and states that no transition-assessment
runtime capability exists.

`CLAUDE.md` preserves historical guidance and accepted status guard phrases.
Its current status records ADR-0019 and ADR-0020, the exact TA limit triple,
strict matched-fingerprint gate, and no facade, demonstration, occurrence,
store, identity, or persistence. It explicitly says that no TA Slice A or B is
complete under this documentation status.

The new `backend/evidence_assurance/README.md` is 147 lines and 6,290 UTF-8
bytes at SHA-256
`b28b89a168e393052b9401eec8b7f770bb5d8d52214631c01ba71a42f1a6021d`.
It documents the actual two query methods, pure validator, accepted ordered
33-name export surface, horizon/seed/fence behavior, fingerprint and
validation boundaries, both store-revalidation modes, allowed dependencies,
issues/statuses, and explicit non-claims. It changes no package code.

The evidence-alignment README links ADR-0019 and preserves its exact single
v1 consumer. It notes that the accepted, unimplemented TA design may later
consume carried alignment results without changing alignment or adding a
second alignment consumer.

## 6. Pre-commit verification

All commands used `PYTHONDONTWRITEBYTECODE=1`, disabled repository pytest
addopts, and disabled the pytest cache where applicable.

- established six-module documentation/status gate: `26 passed in 3.23s`;
- complete `tests/evidence_assurance`: `68 passed in 15.36s`;
- complete `tests/evidence_alignment`: `62 passed in 30.21s`;
- immutable ledger and C40 preservation twins: `2 passed in 4.33s`;
- changed-document Markdown link check: seven files checked, zero missing
  local links;
- ending-marker checks: all three required new markers exact;
- staged `git diff --check`: passed with no output;
- working and accepted-base-to-first-commit `git diff --check`: passed with no
  output after commit.

No full repository suite or dual clean-checkout matrix was run because this is
a documentation-only gate and the prompt explicitly excludes unnecessary
expensive reruns. Compilation and dependency checks were not run because no
Python source, dependency file, or package export changed.

## 7. Authoritative preservation

The two immutable preservation tests loaded the authoritative model and proved
exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remain `1/1/0`; TRG/TRD/TRW remain `0/0/0`. The record-file
aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The flow disclosure remains exactly 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.

No `backend/transition_assessment` path exists. No accepted EA source,
temporal, model, binding, interpretation, fixture, membership, ledger,
canonical byte, deterministic reproduction, or artifact was modified.

## 8. Git and local-state integrity

The first commit is a linear child of the exact accepted base. Nothing was
pushed or merged. No rebase, reset, amend, cherry-pick, force operation, or
history rewrite was performed.

Before this report was created, `git status --short` was empty. The ignored
owner-local settings file retained SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`
and remained unstaged. Post-report-commit status, whitespace, marker, link,
test, and settings checks are recorded in the terminal receipt rather than by
mutating this committed report.

## 9. Scope and next owner gate

This checkpoint is documentation only. It accepts and records the TA-001
design but does not implement or finally accept the TA milestone. It adds no
TA contract, function, package, test, fixture, positive world, model record,
alignment consumer, facade, demonstration, result artifact, or lower-layer
change.

The next possible gate is an explicit owner decision to accept this exact
documentation checkpoint and separately authorize TA-001 Slice A. Until then,
TA implementation remains not started.

END OF TA-001 DESIGN ACCEPTANCE AND ADR RECONCILIATION REPORT
