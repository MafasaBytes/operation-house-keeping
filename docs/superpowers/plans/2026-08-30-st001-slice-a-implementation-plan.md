# ST-001 Slice A — Identity and Model-Record Foundation Implementation Plan

Status: Slice A owner accepted at `9adcf4d9613ac96e5fb430a4b750f3053679b64d`; Slice B separately authorized; Slices C-D unstarted and unauthorized

Date: 2026-08-30

Accepted base: `0ed77df7ea4870faec1eae9b89668add97aa855d`

Branch: `st001`

Authoritative design SHA-256:
`febe18fa291896021708d09c10d5cf4ef955201bcd3e59199e74c6c4e630cc95`

## 1. Objective and stop boundary

Implement only the state identity and append-only model-kernel record
foundation accepted in ADR-0016. Finish with verified identity, contracts,
canonical support, store validation, immutable indexes, lifecycle replay,
adversarial tests, documentation, and a file-first completion report.

Do not implement Slice B queries, Slice C classification, or Slice D fixtures.
The demo ledger must remain 32 records.

## 2. Gate 0 — accepted design administration

Commit in one documentation-only group:

- both independent proposals;
- corrected final synthesis;
- accepted challenger audit and correction report;
- ADR-0016;
- this plan;
- the Slice A adversarial acceptance matrix;
- accurate project status wording.

Verify the accepted base, branch, synthesis hash, ending marker, and ignored
`.claude/settings.local.json` before commit.

## 3. Gate 1 — state identity, red first

Add failing tests that pin:

- exact `StateAnchor` field set, frozen/extra-forbidden/revalidation behavior;
- `sta_` plus 32 lowercase hex characters;
- exact minter signature and export order;
- UUID version/variant, distinct calls, and preserved valid naming fields;
- malformed IDs, invalid names, extra/coercible arguments, forged nested
  instances, and absence of I/O.

Implement only additive System Identity changes in:

- `backend/system_identity/anchors.py`;
- `backend/system_identity/minting.py`;
- `backend/system_identity/__init__.py`;
- `backend/system_identity/README.md`.

Run focused identity tests and commit the green group.

## 4. Gate 2 — record contracts and canonical identity, red first

Add failing tests for:

- exact SRG/STD/STW field sets, literals, schemas, prefixes, and extra-field
  rejection;
- 1, 64, zero, 65, duplicate, malformed, and reordered constraint IDs;
- exact pin tuple coverage and canonical ordering;
- canonical multi-parent STD ordering, duplicate parent and self-parent refusal;
- STW minimal shape and absence from `ModelRecordEvidence`;
- record builder parity, stale IDs, filename grammar, canonical bytes, and
  existing golden-vector preservation;
- hostile nested `model_construct` and `model_copy` instances.

Implement additive changes in model-kernel contracts, canonical mapping,
builders, unions/adapters, and package exports. Preserve all existing records.

Run focused record/canonical suites and commit the green group.

## 5. Gate 3 — store closure and ownership, red first

Add failing tests for:

- unknown subject, constraint, target variable, and owner;
- exact embedded-owner equality and cross-entity refusal;
- agreeing and divergent duplicate SRG;
- required SRG citations and claim-bearing evidence;
- exact STD SRG/CRG/VCN citations and claim-bearing evidence;
- missing, extra, duplicate, wrong-kind, substituted, and cross-constraint
  pins;
- atomic failed append and filename/content mismatch;
- STW uncitability and invalid targets.

Implement validation in the existing `ModelStore` and collection validator.
Add no store or transaction abstraction. Run focused store/evidence tests and
commit the green group.

## 6. Gate 4 — lifecycle, indexes, replay, red first

Add failing tests for:

- exact `(state_anchor_id, AssertionContext)` lineage keys;
- iterative explicit-stack three-colour traversal, including a deep chain;
- cross-state/context parents, cycles, and cross-root convergence;
- same-root fork, partial convergence, and full convergence;
- independent identical-body corroboration and differing-body conflict;
- effective-body comparison excluding audit/evidence/identity fields exactly
  as designed;
- selective/current-tip/all-tip withdrawal, invalid/non-tip/duplicate
  withdrawal, and successor-withdrawal race;
- immutable canonical indexes under reversed inputs/hash seeds;
- historical revival without later successor/withdrawal;
- exact 9/10/11/14/16/18/28/29/32 memberships and revisions;
- every predecessor record byte unchanged.

Implement only immutable `LoadedModel` state indexes and lifecycle validation.
Do not add query/result contracts. Run focused replay/lifecycle suites and
commit the green group.

## 7. Adversarial specialist review

After the initial implementation is green, request three bounded reviews:

1. architecture/import direction and Slice A scope;
2. model-kernel canonical/store/lifecycle integrity;
3. adversarial test coverage and hostile reconstruction.

For each genuine finding:

- reproduce it with a failing test first;
- repair the smallest Slice A defect;
- retain the reproduction as regression coverage;
- rerun focused and affected suites;
- reject suggestions that broaden into Slices B-D.

Commit genuine repair groups separately.

## 8. Verification columns

Run and record exact commands/counts for:

1. focused ST Slice A tests;
2. complete System Identity and model-kernel tests;
3. affected identity, CN, PT, VP, BH, replay, and documentation suites;
4. architecture/import-isolation tests;
5. backend compilation;
6. complete repository suite;
7. fresh base-only checkout at final HEAD;
8. fresh all-extras checkout at final HEAD;
9. focused OCP/STEP tests;
10. focused PDF tests;
11. `git diff --check`;
12. branch, topology, remote, and working-tree checks.

Report a sandbox-denied loopback separately and rerun it with accepted
permission. A denied setup is not a pass.

## 9. Preservation gates

Pin and verify:

- model ledger count exactly 32;
- model revision
  `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`;
- no committed `srg_`, `std_`, or `stw_` records;
- all 32 model record bytes unchanged;
- all explicit historical revision IDs unchanged;
- accepted CN/PT/VP/BH artifact hashes unchanged;
- no binding, interpretation, temporal, source, structural, or fixture change;
- `.claude/settings.local.json` ignored and untouched.

## 10. Commit groups

Target reviewable subjects:

1. `docs: accept ST-001 design and plan Slice A`
2. `test: define ST-001 state identity contracts`
3. `feat: add ST-001 state identity`
4. `test: define ST-001 state record contracts`
5. `feat: add ST-001 state model records`
6. `test: define ST-001 store and lifecycle contracts`
7. `feat: add ST-001 state store validation and indexes`
8. `test: harden ST-001 replay and forgery boundaries`
9. `fix: repair ST-001 adversarial findings` only when reproduced
10. `docs: record ST-001 Slice A verification`

Small test/implementation pairs may be combined only when the red-before
evidence is preserved in the completion report and the commit remains
reviewable.

## 11. Completion report and stop

Write:

`docs/superpowers/reports/2026-08-30-st001-slice-a-completion-report.md`

Include branch/base/HEAD/commits, changed files, red-before/fixed-after,
contracts, prefixes, canonical golden IDs, lifecycle/replay evidence, every
verification count, preservation hashes/revisions, specialist findings,
limitations, clean status, no remote operation, and confirmation that Slices
B-D remain unstarted.

This stop gate was satisfied: Slice A was owner accepted at
`9adcf4d9613ac96e5fb430a4b750f3053679b64d`, and Slice B was separately
authorized. Slices C and D remain unauthorized.

END OF ST-001 SLICE A IMPLEMENTATION PLAN
