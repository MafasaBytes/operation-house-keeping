# First-slice completion report

Date: 2026-09-19

Administrative approval HEAD before implementation: `221793cfe7f3ffbd4a4feb6ce968073e85f86b49` (`docs: approve next-measurement first slice`). Final tested implementation HEAD: `db1e927` (`fix: require complete measurement ancestry`). The approved package archive, manifest, and recovery receipt were independently recovered into `/tmp/next-measurement-slice-JJFbop` and verified before editing. The pre-existing nonignored inventory remained 1,207 files with aggregate SHA-256 `38c852bb2d074d6ddf77f566358d8af6a7815b0db3da55c5ec45c31907fecfb2`; tracked/index changes outside the explicit approval and slice files are absent.

## Scope delivered

The maintained first slice is [measurement_contracts.py](../../../applications/bounded_decision_workflow/measurement_contracts.py). It owns only:

- canonical UTF-8 JSON parsing with duplicate-key, nonfinite-value, profile, header, ID and revision checks;
- exact typed references and content digests;
- immutable approved-policy identity (`a4a4c8016b35ab78a2b98797234a9a014f46a9bd891e45977477efd3be4ae22c`), caller-tightening validation, and the approved 128-object/four-revision/eight-context/1 MiB ceilings;
- bounded transitive closure from invocation through exact authority/request members, required ancestors and typed dependencies;
- per-reference and per-edge accounting, active-path cycle detection, legitimate completed sharing, deterministic missing/digest/kind/profile/identity/predecessor/resource diagnostics, exact authority joins, nomination uniqueness/order, and rejection of the prepared nonexecutable build witness.

No evidence admission, public reconstruction, authority/procedure/hypothesis assessment, support qualification, prediction mapping, minimax ranking, result/trace publication, command dispatch, replay, physical acquisition, bypass flag, C adjudication, backend extension or dependency was added. The prepared build witness remains test material and cannot establish production build identity.

## Red/fixed evidence and tests

Red-first collection failed as expected before implementation with `ModuleNotFoundError: applications.bounded_decision_workflow.measurement_contracts`. After implementation, the focused slice suite passed: `7 passed` in [test_contracts_and_closure.py](../../../tests/measurement_profile/test_contracts_and_closure.py). It covers canonical/profile rejection, exact approved policy and tightening, typed joins, duplicate nomination references and IDs, shared closure, active-cycle handling, missing closure, cross-profile roles, nonexecutable build rejection, plus-one object/edge limits, and the history envelope.

The existing `tests/applications` regression run reached 84% before the first failure in the pre-existing thermal/governed CLI test `test_baseline_command_and_exact_replay`: `REPLAY_BUILD_UNAVAILABLE` (`restore_matching_build`). The failure is outside this slice and occurred in the existing command path; the new module is not imported by that path. The full regression suite is therefore not green and is not reported as passing evidence. No measurement production command or end-to-end proof command was executed.

After the initial implementation commit, a focused nearest-twin test exposed that a revision greater than one with a null predecessor could pass when its chain did not yet exceed the numeric envelope. The resolver now refuses that case as `REQUIRED_REFERENCE_MISSING`; the focused suite was rerun green. This is a uniquely determined closure-integrity correction, with no policy or semantic change.

The static preparation oracle remains hand-derived with a separately written same-author check. It is not independent reviewer evidence. The six harness-only controls remain absent from production interfaces, and C remains manual/unresolved.

## Runtime measurements

The authorized slice was measured directly through the contract resolver, without application command execution. On CPython 3.13, 25 complete resolves of the nine-object fixture took 9,006,160 ns total (360,246 ns/resolve), with 12 edge visits, 9 reference occurrences, 9 unique objects, 3,012 unique bytes, one request context and chain revision one. Peak process RSS was 88,952 KiB. Single refusals measured 134,666 ns for unique-object limit exhaustion and 88,899 ns for edge-visit exhaustion; both returned `RESOURCE_LIMIT_EXCEEDED` before successful closure. The revision-five history test separately verifies refusal without truncation; the one-revision fixture is deliberately below that boundary. These measurements describe this slice and fixture only; they do not validate full runtime capacity or the proposed watchdog/address-space ceilings.

No approved limit was increased. The exact prepared policy remains the only accepted policy identity. Required ancestry is not squashed or silently omitted. The resolver retains shared completed objects while charging each incoming reference and rejects active-path cycles.

## Administrative and remaining gates

The approval record is committed separately from this implementation. The implementation commit is the exact tested HEAD after this report and explicit staging; the final receipt supplies its hash. Staging was inspected before commit and contained only this slice module, its focused tests, and this report. Existing artifacts, runtime results, dependencies, backend contracts, ledger, and unrelated untracked files were preserved.

The packaged first-slice acceptance boundary is met for contract/closure behavior. A real executable build witness and environment manifest are still required before any runtime command can accept an invocation. Evidence/authority/support/ranking/command-retention/replay slices remain unimplemented and separately gated. The 142-command proof remains unauthorized.
