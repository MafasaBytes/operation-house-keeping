# Slice 1 verification and regression diagnosis

Date: 2026-09-19. This continuation preserves [the original completion report](2026-09-19-next-measurement-first-slice-completion.md) byte-for-byte; it does not revise its historical claims.

## Commit, package, and preservation commitments

The administrative HEAD supplied by the owner resolves to `e51fbbe86051a5d253b007af0c56d82c833873f8`. The approval commit resolves to `221793cfe7f3ffbd4a4feb6ce968073e85f86b49`. The tested Slice 1 code commit resolves to `db1e927441a9d84a5398d59f7c83a3b0f2a51d8f`. The report-only amendment supplied for this diagnosis was `e51fbbe86051a5d253b007af0c56d82c833873f8`; this continuation is recorded separately at its own documentation commit.

The completion report SHA-256 is `c03ae74fb336781261070b92ad6d2db93fbc92f718ed24d37b8965f182843bf4`. The approved preparation archive, manifest, and recovery receipt remain respectively `a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f`, `18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea`, and `ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac`. No package or oracle bytes were changed.

The pre-existing nonignored inventory remains 1,207 files with aggregate SHA-256 `38c852bb2d074d6ddf77f566358d8af6a7815b0db3da55c5ec45c31907fecfb2`; root `applications` and `backend` are clean, and no staged changes remain before this continuation is committed. Temporary comparison worktrees and their disposable dirty marker are outside the root and are removed after verification.

## Replay regression attribution

The exact failing test was `tests/applications/bounded_decision_workflow/test_s6_cli.py::test_baseline_command_and_exact_replay`. Its command is the module invocation `python -m applications.bounded_decision_workflow evaluate --request <temporary request.json> --snapshot <temporary snapshot.json> --output-dir <temporary baseline>`, followed by verify and replay assertions. The test expected exit 0 and a successful baseline result with action `aH`, minimum cost `2/1`, admitted T0 `40`, eight raw projections, and an exact replay. The observed refusal was exit 3 with the bounded diagnostic `REPLAY_BUILD_UNAVAILABLE`, stage `commitment_public_reconstruction`, target `build_identity`, retry `restore_matching_build`; no result directory was accepted.

The maintained builder in `applications/bounded_decision_workflow/build.py` rejects a dirty `applications` or `backend` tree before it can create a build witness. The original full-suite run occurred while the new Slice 1 module was still an uncommitted file under `applications/bounded_decision_workflow`; that workspace state therefore caused the refusal. This is an expected dirty-build safety refusal, not a replay semantic mismatch and not a regression in replay expectations.

The check was reproduced in comparable isolated environments:

| Environment | HEAD | Applications/backend state | Result | Build witness SHA-256 |
| --- | --- | --- | --- | --- |
| checkpoint baseline worktree | `6351750b3cacad288cb99d9d11a8b61b6fe85b71` | clean | exact test passed | `b509c6f39488b2a65bee562a4647e4d413ae9c2d9fbf3bbbb51795f52b07571e` |
| Slice 1 worktree | `db1e927441a9d84a5398d59f7c83a3b0f2a51d8f` | clean | exact test passed | `b20e996ab746965c03793888d36dbbc7a0209ae4465761f1134bd2fecefe4bd4` |
| Slice 1 worktree with disposable uncommitted marker under `applications` | same Slice 1 HEAD | dirty | exact test failed with the recorded `REPLAY_BUILD_UNAVAILABLE` | unavailable by intended refusal |
| root after Slice 1 commit | `e51fbbe86051a5d253b007af0c56d82c833873f8` | clean for `applications`/`backend` | exact test passed | `c754d203f4ccd558ac8527746a3ad8b7d830976be41b99c63d6b1d3b52b77e32` |

All three clean environments used CPython 3.13.11, pydantic 2.13.4, pytest 9.1.1, and lock SHA-256 `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`. The clean worktrees were on the `/tmp` ext filesystem; the root checkout is on the writable 9p `/mnt/d` mount. The comparison shows no dependency or filesystem failure. The build witness differs legitimately because it commits to the exact HEAD and application source inventory. No replay expectation was changed, build validation weakened, source excluded, dependency installed, or production code repaired for this finding.

## Slice 1 coverage

The focused suite now has nine passing tests. The executable coverage is:

- canonical compact JSON, duplicate-key/nonfinite rejection through the parser, profile/header/ID/revision checks, and exact approved policy identity with caller tightening;
- exact reference shape, kind and digest handling, including distinct missing-content and digest-mismatch outcomes;
- exact invocation/declaration/selection joins and cross-profile role rejection;
- duplicate exact nomination references, same logical ID across different revisions, canonical nomination order, and no silent revision collapse;
- complete required closure through typed members, request predecessor requirements, missing ancestry, request-chain limits, unique-object and edge-visit limits;
- completed-object sharing and repeated reference accounting;
- active-cycle control precedence is exercised through the malformed self-reference twin, which correctly refuses digest integrity before cycle detection. A fully SHA-256-consistent cyclic JSON fixture cannot be constructed without a hash fixed point; the packaged isolated future graph harness remains the required executable witness for the pure active-path cycle branch;
- the approved nonexecutable prepared-build witness is rejected before any production identity claim.

The tests use internal contract fixtures and resource counters; they are not public evidence admission, authority assessment, support qualification, ranking, command, replay, physical-acquisition, harness-bypass, or C tests. The public 60.1 input is intentionally not admitted by this slice. The nine tests do not constitute independent reviewer evidence; their oracle assumptions remain lead-authored and separately hand-checked.

## Runtime measurements and disposition

The direct resolver measurement remains 25 complete resolves in 9,006,160 ns total (360,246 ns per resolve), 12 edge visits, 9 reference occurrences, 9 unique objects, 3,012 unique bytes, one request context, and peak RSS 88,952 KiB. Plus-one refusals measured 134,666 ns for unique-object exhaustion and 88,899 ns for edge-visit exhaustion, both `RESOURCE_LIMIT_EXCEEDED`. The history-nearest twins refuse missing revision ancestry without truncation. These are Slice 1 fixture measurements, not full-runtime capacity evidence and not a limit amendment.

No implementation repair was required for the replay regression: the baseline/current comparison proves an intended dirty-build guard. The only Slice 1 code correction remains the previously recorded null-predecessor refusal. No semantic, resource, dependency, or scope discrepancy is open. Remaining limitations are the infeasible hash-consistent cycle fixture, unavailable executable build witness, untested measurement commands, and all later slices.

Owner gate: accept Slice 1 only after reviewing this clean/dirty build attribution, the nine-test coverage and the stated cycle-fixture limitation. Slice 2 and later work, production measurement commands, and the 142-command proof remain separately unauthorized.
