# Slice 2 evidence and authority completion

## Scope and ownership

The approved immediate slice was **Slice 2: evidence and authority**. This implementation adds `measurement_admission.py`, an application-owned adapter that first resolves the closed measurement invocation, then reuses maintained `admit_request_and_snapshot` for public reconstruction and observed-value admission. It records local declaration/selection permission, current-condition status, observed-value status, nominated hypothesis IDs, and procedure applicability states. It stops before prediction qualification, ranking, command dispatch, retention/replay, or physical acquisition.

The administrative Slice 1 acceptance commit is `1185b250212e84bfb7674d3d6a18a9d5a2149018`; the Slice 2 implementation/test commit is `93048e81bce754353afa9c1f7a9c567a885f4bd1`. The current and tested HEAD is `93048e81bce754353afa9c1f7a9c567a885f4bd1`. The earlier Slice 1 implementation remains `db1e927441a9d84a5398d59f7c83a3b0f2a51d8f`, and the cycle-closure evidence remains at `ece8050da7b1760ded154af89ef6b5da51da8368` with report SHA-256 `a10be58c009ab7f008cd488ef213d8bf7306e99d002443cbb75d642f9a289849`.

## Red/fixed evidence and coverage

The initial Slice 2 test run was red because the base procedure twin omitted `conditions`; the adapter incorrectly indexed the absent field. The in-scope repair treats absent declared conditions as procedure inapplicability with an explicit `*_missing` reason. No accepted semantic, resource, dependency, backend, or authority boundary changed.

The final focused run passed 15 tests:

* Slice 2 admission tests cover maintained public-admission reuse, authority denial with zero downstream work, baseline-unavailable whole-set withholding, context-join mismatch, and all-declared-condition procedure inapplicability.
* Slice 1 contract tests cover canonical references, typed joins, nomination identity, ancestry, sharing/cycles, and resource refusal.
* The clean legacy replay regression `tests/applications/bounded_decision_workflow/test_s6_cli.py::test_baseline_command_and_exact_replay` passes.

The unavailable baseline path returns no procedure or hypothesis assessments and performs no downstream work. Authority denial likewise returns no downstream assessments. Procedure applicability retains every nominated procedure; it does not prune a candidate. Context mismatch is an explicit `EVIDENCE_JOIN_MISMATCH`. Local attestation remains permission/support provenance only and does not authenticate an issuer or establish empirical validity.

## Measurements and boundaries

The focused command completed in approximately 19.3 seconds wall time in the existing environment; this is test-process time, not a capacity claim. No new numerical limit was introduced or increased. Resolver/resource measurements and approved package ceilings remain those recorded by Slice 1. No production measurement command, full proof, support qualification, minimax ranking, retention/replay path, backend extension, or physical work was executed.

The implementation does not yet qualify support, assess prediction cells, adjudicate conflicts, or produce a recommendation. The prepared nonexecutable build witness and synthetic digest seam remain unavailable through production interfaces. Thermal and governed commands, schemas, retained results, replay interpretation, backend contracts, ledger, package/oracle bytes, and unrelated artifacts are unchanged.

## Preservation and next gate

The prior verification and cycle-closure report bytes and hashes remain unchanged. Existing untracked artifacts remain present; the only new tracked changes are the separately committed Slice 1 acceptance record and this authorized Slice 2 module/tests/report. Slice 2 owner review must confirm the zero-downstream-work gates, public join reuse, all-candidate inapplicability handling, and the absence of prediction/ranking leakage before any further slice is authorized. Slice 3 and later work, the 142-command proof, dependencies, backend changes, ADR allocation, push, merge, and history rewrite remain unauthorized.
