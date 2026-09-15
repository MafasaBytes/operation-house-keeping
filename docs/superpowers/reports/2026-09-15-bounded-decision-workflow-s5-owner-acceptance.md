# Bounded decision workflow S5 owner acceptance

Verified `brc-exp001` at administrative HEAD
`e38d7d73d6922257b73d62cbb30d89ee8bcfadaa`. The owner accepts S5 at exact tested
implementation `702a4cbd143950e4fc2e6d724760e0a2723301f2`.
Only completion-report and plan documentation followed that tested commit.
S4 acceptance remains `f4f9748f560d878b01e83dc071be781a309099d9`.

The preserved [S5 completion report](2026-09-15-bounded-decision-workflow-s5-retention-and-recovery-completion-report.md)
matches SHA-256 `a2d8307c8d8fcaf9a5a7a313d8534bae6d55684f136d742f42e358d0aa5dcc90`.
Its 597 passing tests comprise the previous 474, one S5 correction test and 122
S5 filesystem/resource/recovery tests. Acceptance rechecked 139 tests in 13.31s:
S5 filesystem tests plus S5/S4 correction and archive recovery. Existing results
were not reused as writable test destinations; a new isolated ext4 test root was
created. The recorded missing-export and read-error red/fixed evidence remains.

Accept descriptor-relative safe paths, bounded read-once capture, exclusive
no-overwrite publication, fixed inventories, manifest-last completeness, read-only
byte verification and incomplete preservation. Tests include real concurrent
publishers and 35 pre-manifest SIGKILL boundaries, plus post-manifest interruption
and separate directory/parent-fsync diagnostics. The three mechanical recipe
[corrections](2026-09-15-bounded-decision-workflow-s5-retention-fixture-correction-report.md)
preserve original package/manifest bytes and all 68 content-addressed objects.

Manifest-last completeness is not atomic visibility of the entire directory and
does not guarantee power-loss durability. Hash verification does not authenticate
sources, executable code or semantic conclusions. S5 does not implement command
integration or replay recomputation. No final application acceptance is recorded.

Separately authorize only S6 from the [approved plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md):
immutable policy and incremental accounting, evaluate/verify/replay command modes,
exact diagnostics, build compatibility and real subprocess tests. Replay must
reconstruct and recompute, not merely compare stored hashes. S7 clean-checkout
reproduction and final release acceptance remain unauthorized.

The approved CPython 3.13/ext4 environment and ten dependency artifacts reverified
with unchanged environment/lock commitments. S1–S5 semantics, limits, backend
contracts, ledgers, existing inputs/results and 63 unrelated untracked artifacts
remain protected. No new dependency, backend extension or physical activity.

END OF BOUNDED DECISION WORKFLOW S5 OWNER ACCEPTANCE
