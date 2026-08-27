# VP-001 Slice A — implementation plan

Status: implemented and adversarially reviewed; awaiting owner acceptance. The
completed slice contains claims, withdrawals, canonical identity, validation,
indexes, replay, builders, exports, tests, and documentation only. It does not
implement Slices B, C, or D.

Accepted base: `8a20dc82ef9445c311e89106ad10572c5c259df1`.

## Gate 0 — preserve the accepted baseline

1. Verify `main` and `origin/main` at the accepted base and create `vp001`.
2. Load the demo model through the public store and pin 28 records at
   `mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`.
3. Freeze every existing model record byte, every explicit historical
   membership/revision, and PT artifact SHA-256
   `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
4. Record the pre-change hash of `.claude/settings.local.json` and never stage
   or modify it.

## Gate 1 — documentation commit

Commit before implementation:

- final VP-001 specification;
- ADR-0014;
- this Slice A plan;
- complete adversarial acceptance matrix.

The documents record all four owner-gated slices, exact Slice A contracts,
reserved Slice B/C public contracts, and the one-record Slice D bound.

## Gate 2 — red-first contract tests

Add focused tests for:

- exact VPA/VPW fields, discriminators, prefixes, and prohibited fields;
- malformed IDs, duplicate/self parents, canonical parent order, and extras;
- nonempty canonical evidence and VPW uncitability;
- content-derived IDs, literal canonical bytes, and hostile nested instances;
- `ModelRecord`, filename, citable-evidence, builder, and exact export widening;
- unchanged golden bytes and IDs for every accepted record kind.

Run the focused tests and retain their expected missing-contract failures before
production edits.

## Gate 3 — contracts and canonical identity

1. Add VPA and VPW using existing frozen/revalidated contracts.
2. Widen only the accepted record/evidence ID grammars.
3. Extend the discriminated `ModelRecord` union and record adapter.
4. Extend canonical kind-prefix mapping and public `build_record` path.
5. Export only the two accepted Slice A record contracts.
6. Pin canonical bytes and record IDs for both kinds.

Run contract/canonical tests until green before store integration.

## Gate 4 — red-first store and replay tests

Add tests for endpoint/entity/evidence closure, same-owner equality, independent
roots, same-root forks/convergence, cross-root refusal, cycles, withdrawals,
replay revival, immutable indexes, hostile files, and atomic append failure.
Run them red against the contract-only implementation.

## Gate 5 — validating store and indexes

1. Add VPA/VPW dispatch buckets without refactoring accepted lifecycle paths.
2. Validate variable and port registration closure, both entity registrations,
   exact owner equality, and evidence closure.
3. Validate the subject-preserving multi-root correction DAG iteratively.
4. Derive deterministic root and complete ancestry indexes.
5. Validate VPW only after successor indexes exist.
6. Derive membership-relative active tips without reviving parents.
7. Materialize every required immutable sorted index.
8. Return the widened `LoadedModel`; preserve all-or-nothing append/load/replay.

## Gate 6 — regression and isolation

Run focused VP, model-kernel, identity, PT, downstream, historical replay,
architecture, and import-isolation suites. Confirm:

- no existing record bytes or IDs changed;
- all explicit historical revisions replay exactly;
- the demo remains exactly 28 records;
- no queries, result contracts, state composition, or fixture records exist;
- the kernel imports only accepted dependencies.

## Gate 7 — independent adversarial review

Have the architecture, backend, test, and code-review specialists attack the
green implementation. Record concrete failing-before and fixed-after evidence
for every genuine defect. Stop for owner adjudication if a repair would change
an accepted architectural decision.

## Gate 8 — final verification

Run:

1. focused VP Slice A tests;
2. complete model-kernel tests;
3. identity and PT tests;
4. affected downstream and isolation suites;
5. full repository suite;
6. fresh base-only clean checkout;
7. fresh all-extras clean checkout;
8. focused OCP/STEP and PDF suites;
9. permitted loopback test separately if sandbox denied;
10. `git diff --check` and branch/worktree topology checks.

## Reviewable commits

Preferred sequence:

1. `docs: record accepted VP-001 design`
2. `test: add VP-001 Slice A contract reds`
3. `feat: add variable-port association records`
4. `test: add VP-001 store and replay reds`
5. `feat: validate variable-port association lifecycle`
6. `fix: harden VP-001 adversarial boundaries` when genuine defects exist
7. `docs: record VP-001 Slice A verification`

Tests and their minimal matching production changes may be combined where that
keeps commits green and reviewable, but red-before evidence must be recorded.

## Stop condition

Stop after Slice A is green, independently reviewed, clean-checkout verified,
and committed. Do not begin the reserved queries, state composition, or fixture.
