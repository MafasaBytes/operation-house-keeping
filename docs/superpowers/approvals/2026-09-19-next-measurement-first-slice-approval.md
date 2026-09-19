# Next-measurement preparation and first-slice authorization

Date: 2026-09-19

Approved checkpoint: `6351750b3cacad288cb99d9d11a8b61b6fe85b71`.

The exact preparation archive, manifest, and recovery receipt were recovered into an isolated directory and verified against the owner-supplied digests:

- package `a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f`;
- manifest `18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea`;
- recovery receipt `ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac`.

The exact manifest-bound first-release policy is approved: at most 128 unique objects, four complete revisions per declared chain, eight request contexts, and the specified 1 MiB capture/bundle ceilings. Required ancestry remains complete through revision 1; an over-envelope or over-budget closure refuses without truncation, squashing, or ancestry erasure. Existing thermal, governed, backend, dependency, ledger, and retained-result policies are unchanged.

This approval authorizes only slice 1 from the packaged plan:

1. closed measurement-profile contract parsing and canonical-byte checks;
2. exact typed-reference and version/content identity resolution;
3. immutable measurement resource-policy validation, with caller limits only tightening approved limits;
4. bounded transitive required closure from invocation through authority, declared request members, all request ancestors and required dependencies, including sharing, active-path cycle detection, deterministic missing/mismatch diagnostics, and complete closure accounting.

The slice may not implement public evidence admission, authority/procedure/hypothesis assessment, support qualification, prediction mapping, minimax ranking, result construction, measurement command dispatch, bundle publication, replay, physical acquisition, the bypass control, manual C, or any later proof fixture execution. The prepared build witness is nonexecutable and is rejected as production build identity. No backend extension, dependency acquisition, numerical-limit amendment, or thermal-command change is in scope.

The implementation must use red-first tests and nearest valid twins. It must measure actual slice runtime work, exercise applicable exact-limit and plus-one refusals and history-boundary cases without increasing approved limits, retain red/fixed evidence, and preserve oracle provenance. A semantic, resource, dependency, or scope discrepancy stops the slice for owner review. The 142-command proof remains unauthorized.

This document records approval and authorization only; it is not evidence that the implementation, runtime build, or full proof has passed.
