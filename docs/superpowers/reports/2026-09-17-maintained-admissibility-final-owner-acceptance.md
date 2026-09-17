# Final owner acceptance — maintained admissibility enforcement

2026-09-17. The owner grants final acceptance of tested implementation
**`15f773ba9c675b553283669fbf72c76407c0eabd`**. Verified administrative HEAD/main:
`8c7557e886e5aeb1f396766a97c672ec22ddc272`. This documentation closeout is not a
newly tested executable; historical replay still requires its exact recorded
checkout, contract, policy and environment. No successor work is authorized.

## Verified evidence and accounting

Read the complete [final verification report](2026-09-17-admissibility-final-release-verification.md),
SHA-256 `cce621d5bd8026678f23d20ab1b75e2ee2f3cf3fb7e9f317d2f75bcfa877a7fb`.
Its unchanged [release evidence](2026-09-17-admissibility-final-release-evidence.json)
has SHA-256 `0ecd090f37787849bc7eefc1d0576058e5b37fa67c0e3c4d2335ddb2054f4983`.
Verified compressed/raw commitments, every archived byte object and file reference:
467 command-evidence files / 198 objects, 34 supplemental files / 30 objects,
34 command payload inventories and 13 closure recipes. The existing 105-file
authority recovery also verifies; hashes alone are not substituted for recovery.

The original full invocation remains **exit 1: 4,807 passed, 35 optional skips,
three failures** out of 4,845 cases. The two forward/reverse FL-001 disposable
reproduction cases and its nonempty-root guard case encountered the requirement
that their root lie beneath `tempfile.gettempdir()`. The full run's ext4 root was
outside that directory; in the guard case this diagnostic preceded the expected
nonempty-root diagnostic. This is a verification-location restriction, not a
product repair or a waived safety guard.

The isolated **12-test rerun passed** under a fresh `/tmp` root, using the same
candidate, clean source checkout and interpreter. Recovered JUnit identities
confirm that all three failed cases passed there. Git history between the tested
candidate and administrative checkpoint contains only the release report/evidence;
no undisclosed implementation or test change is present. Across the two executions,
all **4,810 non-skipped cases have passing evidence**; this is not a claim of one
green full-suite invocation. The 35 skips remain 23 PDF and 12 CAD optional-extra
cases. The original failed invocation, diagnostics and both JUnit files are preserved.

Accepted accounting also includes **771 passing application tests**, **60
current-build commands with their expected success/refusal/interruption outcomes**,
and **six passing historical verify/replay commands**, separately identified as
historical-build evidence. Maximum primary bundle: **355,022 of 393,216 bytes**.
No test or application command was rerun for this acceptance.

## Accepted capability and limitations

Accepted delivery is application-owned finite-world admissibility enforcement
with exact declaration, local-attestation, adoption and executable-build references;
governed evaluation and 23-row dependency review; persistent no-overwrite
publication, byte verification and reconstructing/recomputing replay. Denied
scenarios cannot reach prohibited numerical work. Completed gate exit 0 is not
granted permission: permission is explicit. Technical refusal and an admitted
no-feasible-action result remain distinct.

Legacy behavior is preserved. Only the explicit `governed-evaluate`,
`governed-verify` and `governed-replay` route supplies the governed contract;
legacy commands do not claim admissibility enforcement. Immutable revisions and
exact working adoption preserve history; historical replay uses captured authority,
not proof of current adoption. Semantic replay equality and retained physical-work
evidence remain separate.

Declared admissibility is not physical truth. Local attestation is not authenticated
identity. Finite-world membership is not general correlated-support projection,
statistical correlation or continuum robustness; admitted worlds retain Cartesian
projection semantics. The application neither discovers valid assumptions nor
adjudicates conflicting evidence, and establishes no causality or empirical validity.
Same-author oracle provenance remains disclosed. Four pairs is a functional scope
cap, not a resource-capacity guarantee.

Observed platform evidence remains CPython 3.13.11 on ext4. XFS, other platforms,
reboot and power-loss durability remain unverified; manifest-last publication is
not whole-directory atomic visibility. Optional extras remain unqualified, and
automatic historical environment restoration is not provided. C remains
unresolved/dossier-only; F historical/analytical. IN-001 and CI-001 remain open
and unselected.

## Documentation closeout and preservation

Only this acceptance record and the application README's current delivery status
are committed. Frozen reports, execution evidence and historical pending-gate
statements remain byte-exact; this owner decision supersedes their status without
rewriting them. Links, ending marker, digests, staged scope, archive recovery and
whitespace are checked. Runtime results, provisioning, dependencies, backend
contracts, ledger and all 242 unrelated untracked entries are preserved.

After commitment the tracked worktree/index are clean. Exact
`git status --short --untracked-files=all` matches the retained
[status receipt](2026-09-16-admissibility-first-slice-git-status.txt), SHA-256
`dbb1d1168b6f2c40582c1a388ac6f9f7f963c437006ad6c6329311da5adab50e`.
The acceptance commit is identified by `git log -1 --format=%H --` this record
and the final receipt, avoiding self-reference. No ADR allocation, broader
architecture reconciliation, capability, successor, push, merge or history rewrite
is authorized or performed. **The final maintained-admissibility owner-acceptance
gate is closed by this explicit owner decision.**

END OF MAINTAINED ADMISSIBILITY FINAL OWNER ACCEPTANCE
