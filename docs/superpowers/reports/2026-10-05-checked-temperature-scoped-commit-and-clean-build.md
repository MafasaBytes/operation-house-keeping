# Checked-temperature scoped local commit and bounded clean-build checks

Date: 2026-10-05. The owner authorized "the scoped local commit and bounded
clean-build checks as described" (C2 report §6). Owner choices:

- documentation scope: code, tests and the §6 C documentation;
- branch: local commit on `main`.

Not done: push, remote operation, Gate 2, full suite or Gate 1 acceptance.

## 1. Pre-commit blocker (owner-directed resolution)

`git add` first failed because `.git/index.lock` existed. The cause was a
**suspended** (`T` state) `git rm -rf _to_delete` (PID 81747), started
2026-10-05 03:55 in the owner's own shell. The lock file was empty.

By owner choice, that process received SIGTERM followed by SIGCONT. It exited,
and git's own cleanup removed the lock. No lock was deleted manually.

Verified afterwards:

- index unchanged, `09ae83d4…`;
- HEAD unchanged, `2f0afbd`;
- no git process running.

`_to_delete` remains on disk as it was, and none of it was staged.

## 2. Commit

| Item | Value |
|---|---|
| Commit | `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8` on `main` (parent `2f0afbd`) |
| Content | 75 paths: 74 added, 1 modified (`cli.py`: the 3-line `checked-` dispatch); 36,900 insertions, 0 deletions |
| Scope | Every path re-verified against the C2 report §6 hashes immediately before staging. No out-of-scope path was staged. `git diff --cached --check` was clean. |
| Excluded and still modified | `.gitignore` (`010b1010…`), `tests/reassessment_profile/bounded_pytest_runner.py` (`97999fad…`) |

**The 75 paths:**

- implementation: 9 paths;
- tests: 16 files;
- the six contract packages;
- the governing design v2 and confirmation v2;
- five checked-temperature reports.

After the commit, `git status --porcelain --untracked-files=all -- applications
backend` is empty, so the tree is a clean committed executable.

## 3. Bounded clean-build checks (Gate 1 environment and allowance)

| Launch | Selection | Exit | Result |
|---|---|---|---|
| 17 | The five named legacy files | 0 | **221 passed**. This includes the 9 identity-dependent tests that failed in launch 07: `test_real_captured_semantic_path` × 5, `test_production_capture_then_admit` × 4. They now compute the maintained executable identity at `8414f4d`. |
| 18 | `tests/checked_temperature` | 0 | **198 passed**. DG1 took its clean-tree branch: the real `ExecutableBuild` identity was computed and refused `BUILD_NOT_PERMITTED` at `/build`, because the fixture policy permits only the labelled test double. |

The tree was still clean after both launches.

Launch 07's failures are retained as historical evidence; they are not
reinterpreted. They were caused by the then-uncommitted tree, and launch 17
supersedes them on the committed tree.

**Not run:** a real-entry-point **success** path. No test exists that permits the
real build identity in a captured policy, and adding one would change the
committed test scope. It remains a separately authorizable step.

Every in-process bundle still uses the labelled `TestDoubleBuild`.

## 4. Cumulative accounting (not reset)

**Launches: 18 of 40 used, 22 remain.**

| Measure | Used | Allowance |
|---|---:|---:|
| Logical bytes | 21,557,599 | 536,870,912 |
| Physical bytes | 36,581,376 | — |
| Files | 3,724 | 20,000 |
| Directories | 659 real | 5,000 |

Nothing was deleted.

## 5. Remaining owner decisions

- Gate 1 acceptance.
- Whether to add and run a real-identity success-path test.
- Gate 2, including re-sizing for the 217-invocation matrix and G2 authorization.
- Publication or push. None is authorized.

END OF SCOPED COMMIT AND CLEAN-BUILD REPORT
