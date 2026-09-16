# Bounded evidence and assumption proof owner acceptance

On 2026-09-16 the owner granted acceptance of this bounded proof, conditional on
verification of its retained evidence. That verification passed without tests,
application commands or experiment reruns. Starting local `main` and HEAD were
`d15debb1be89c6e25e9abe8de673d264bf6ef8ce`; no remote verification is claimed.
The unchanged [execution report](2026-09-16-bounded-decision-workflow-evidence-and-assumption-proof-execution-report.md)
has SHA-256
`b1b0a01273865d09583f803730ade6c01de8fd14b9d0a232b5571bfd0af9c401`.
This record closes its pending proof-owner-acceptance gate. Historical pending
wording in the report and frozen preparation/design remains untouched.

Accepted conclusion: the existing maintained application supports the demonstrated
paired-world assumption sensitivity and dependency review. This proof adds
integration evidence, not a new production capability or backend contract.
S1–S7 application acceptance remains at implementation
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`; the proof ran at the pinned administrative
checkpoint above. This documentation commit is not a newly tested application build.

Accepted evidence comprises exactly 16 commands: five successful evaluations,
five verifications, five replays and K's integrity refusal (exit 3,
`REQUEST_SCHEMA_INVALID`, empty stdout, exact frozen diagnostic, no success
bundle). W0/I/R/F/M contain 110 primary decision cells, including 22 no-prior
cells and 88 comparison cells. The four comparisons require 63 reevaluations
and change 36 values, exactly matching frozen expectations:

| Comparison | Required | Changed | Equal after required | Not required |
| --- | ---: | ---: | ---: | ---: |
| W0→I | 0 | 0 | 0 | 22 |
| W0→R | 21 | 2 | 19 | 1 |
| W0→F | 21 | 13 | 8 | 1 |
| W0→M | 21 | 21 | 0 | 1 |

Replay repeats the same 110 cells; verification adds no decision cells. Observed
evidence, snapshot, binding, cutoff and admission fields are preserved across
the approved worlds. Only the approved single-assumption masks and mechanical
commitment updates differ. Application behavior, all other premises, the oracle
and resource limits remain unchanged. Maximum recorded resolution charges remain
7,898/8,192; the recorded retained proof footprint is 7,207,069/8,388,608 bytes.
The W0 null-prior inspection-script correction is accepted as a tooling correction,
not an application repair. Both wrappers and the original inspection failure are
retained; command 1's original captures were reinspected, not rerun.

Before staging, the smallest self-contained documentation addition was identified
as exactly this record and the unchanged execution report. No loose duplicate
authority/input documents are needed. Recovery uses these verified byte sources:

| Needed material | Recoverable source |
| --- | --- |
| Current owner decision and bounded authorization | This record and the owner's closeout instruction; prior execution authorization is attested in the frozen execution report, not inferred from pending preparation wording. |
| Accepted design and original proposal/review | Execution report archive `frozen/docs/superpowers/{specs,proposals,reports}/`; all three complete documents match their source bytes and frozen hashes. Design SHA-256: `3a1496997595dce8f34cfe5dc6803d1087d1a7edd3e72935a94c929e3a8fbbc3`. |
| Exact package, inputs, expectations, plan and dossier | Archive `preparation/`: all 48 files, including seven input files, all expected payloads/annotations, policies and readiness. `MANIFEST.json` SHA-256: `04dd282054f8769703f0d7356945a1d5e4f8e4e411c1e743d6aa88ab9686bea2`. |
| Actual results and execution/inspection history | Archive `results/` (70 files), `captures/` (48 files), and `execution-evidence/` (43 files, including both wrapper versions, original failure, command ledger, row comparisons and preservation records). |
| Inherited fixed admission and existing authority/build | Already committed [S7 evidence](2026-09-16-bounded-decision-workflow-s7-release-evidence.json), [final application acceptance](2026-09-16-bounded-decision-workflow-final-owner-acceptance.md), [reconciliation](2026-09-16-bounded-decision-workflow-post-delivery-reconciliation.md), [retention approval](2026-09-16-bounded-decision-workflow-retention-approval.md), and source/lock/policy at the pinned Git checkpoint. |

The report's single `base64-zlib` block recovered 212 files / 5,304,145 original
bytes in memory. Compressed bytes (1,227,191) and SHA-256
`e0e46a0341c3ee032835bf731e078e3eef345f2d9519fb82a3b1638ad6a62e8a`,
decoded canonical JSON (7,102,189 bytes) and SHA-256
`e4405980ad581dccd2bcc3d7eecb2839c1ce68e8a2cb6f84713dcc7a06c594cf`,
and every member's length/hash matched. Decoding used a 16 MiB bound and rejected
absolute/parent-traversal member paths; every member also equaled its retained
source. No archived script was executed. For later filesystem recovery, follow
the report's exclusive-new-destination instructions; `frozen/` prefixes locate
the original repository paths and `preparation/` locates the original package.
Digests identify the bytes; the embedded members and existing Git blobs preserve them.

Transitive checks covered manifest entries, frozen document anchors, isolated
inputs and allowed masks, expected-result/bundle indexes, canonical C statements,
source/build/lock/policy witnesses, all command argv/environment/exit/capture
commitments, ten complete bundles, receipt hashes, exact oracle payload equality,
dependency unions and row accounting. The S7 origin was recovered from Git at
the pinned checkpoint and matched SHA-256
`8db348f00d36e1f75de3798b9f404cdb20d9a2141509a086402f57dd65f6747b`.
Its embedded baseline archive was decoded and checked through its seven bundle
files and inherited admission fields, including decoded archive SHA-256
`d524ff487399a9d9915cab610546efe89f152e0d9d6ad5c07df8154bb70131d9`.
Interpreter/wheel binaries remain existing external prerequisites, not newly
archived artifacts or promises of installation/platform reproducibility.

C remains unresolved and dossier-only: no conflicting-support winner, supported
recommendation from C, application conflict detection or application conflict
refusal is established. The design's proposed signed C resolution and independent
negative-draft review remain unperformed; this bounded acceptance does not claim
that those broader manual completion criteria were met. W0/F do not resolve C.
Single-assumption results establish no joint robustness. J1/X remain separately
gated; A/B/T remain analytical only. Same-author oracle provenance and shared
synthetic assumptions remain disclosed; no independent oracle acceptance is added.
Empirical validity, source authenticity, causal truth, generated alternatives,
multi-step planning and global optimality remain unestablished. Existing platform
and durability exclusions remain: observed locked CPython 3.13.11/ext4 only;
XFS, other platforms, reboot and power-loss behavior remain unverified. Temporary
ext4 retention is not persistence-after-reboot evidence. IN-001 and CI-001 remain
open and unselected. No successor or architecture expansion is selected.

Preservation checks matched all 874 pre-existing tracked files, all 108
pre-execution untracked files (57 historical artifacts, three frozen documents,
48 preparation files), all seven isolated inputs, 19 provisioning/wheel artifacts,
the designated seven-file existing S6 bundle and recorded runtime input/result
inventories. All 212 archived source files and the execution report retain their
bytes. This does not claim a full content census of 85,105 runtime environment/test
files. Backend contracts, ledger/revision, dependencies and existing runtime
results are unchanged. Only the two named documentation additions may be staged;
the other 108 untracked files remain in place. No production changes, tests,
experiment reruns, push, merge or history rewrite belong to this closeout.

END OF BOUNDED EVIDENCE AND ASSUMPTION PROOF OWNER ACCEPTANCE
