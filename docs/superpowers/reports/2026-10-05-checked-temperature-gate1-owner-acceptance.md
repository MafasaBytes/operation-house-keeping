# Checked-temperature Gate 1 — owner acceptance record

Date: 2026-10-05. **Gate 1 is owner accepted.** The owner authorized the
recommended closeout in the working session. This record transcribes that
decision; it is not itself evidence.

## 1. Accepted pins

| Item | Value |
|---|---|
| Tested implementation | `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8` |
| Real executable build identity (`ct.build.v1`) | `d81acac6f40f97670c23d08df15b3d1f568df5433bdb8ac3b55961f33d27f23c` (checkpoint `8414f4d…`; CPython 3.13.11 `cp313-bdw001`; lock `7c87f0d7…`) |
| Administrative closeout commit (test file plus unchanged report) | `4d6ab13c46642e9771199dced7d312ac94bbbb2f` |
| Contract base | v4 `9e0afa32…`, amended by C1 `791b4035…` and C2 `6252a2da…` |

**Attribution.** Launch 19, the real-build success path with 6 passed, executed
at `8414f4d` with identity `d81acac6…`. It did **not** test the administrative
HEAD `4d6ab13`. That commit adds only `tests/` and `docs/` files and changes no
application or backend source. However, a newly generated identity at
`4d6ab13` would carry a different checkpoint, and therefore a different digest.
No launch has been run at `4d6ab13`.

## 2. Evidence accepted (separately attributed)

| Class | Evidence |
|---|---|
| Real build | Launch 19 at `8414f4d`. Real command entry point: selection and reassessment evaluate, verify and replay all complete; the unpermitted-build twin refuses `BUILD_NOT_PERMITTED` (`…-real-build-success-path.md`). |
| Clean build | Launches 17–18 at `8414f4d`: the 5 named legacy files (221 passed, including the 9 identity-dependent tests) and `tests/checked_temperature` (198 passed) |
| Test double | In-process unit tests in launches 01–16 and 18 using the labelled `TestDoubleBuild`. They prove nothing about a clean build. |
| Historical failures (retained, not reinterpreted) | Launches 01, 02, 05, 11 and 13 (application, fixture and harness defects, fixed); launch 07 (9 identity-dependent legacy failures in the uncommitted tree, superseded by launch 17) |

**Reports:**

- Gate 1 TDD report `02e3b29f…`;
- repair report `57756c0d…`;
- C1 report `f975a387…`;
- C2 report `c37462f6…`;
- scoped-commit and clean-build report `60e47562…`;
- real-build report `63dd13e1…`.

## 3. Limits of this acceptance

**Gate 1 acceptance covers:**

- the checked-temperature application route at `8414f4d`;
- its unit, clean-build and real-build evidence.

**It does not cover:**

- authenticated chronology;
- physical acquisition or empirical accuracy;
- causal diagnosis;
- automatic adoption or reranking;
- Gate 2;
- any later commit.

**Not performed:** Gate 2, a full suite, push and publication. Gate 2 sizing for
the 217-invocation v4 matrix and G2 authorization remain open owner decisions.
IN-001 and CI-001 remain open and unselected.

**Accounting:** 19 of 40 Gate 1 launches used. Nothing was deleted. The
`ct-gate1-tdd` workspace is retained.

This record is untracked. It was not part of commit `4d6ab13`.

END OF GATE 1 OWNER ACCEPTANCE RECORD
