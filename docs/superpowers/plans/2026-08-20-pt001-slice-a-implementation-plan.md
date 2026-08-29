# PT-001 Slice A implementation plan

Status: PT-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. Slice A is owner accepted. The qualified-token
repair is owner accepted. Slice B is owner accepted. The public-contract repair
is owner accepted. The accepted Slice B HEAD is
`ec9ea7d8c20016e267fae16a2554d5e7f1a0ebce`. Slice C is owner accepted. The
accepted PT-001 membership contains exactly 28 records. Its model revision is
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`.
The deterministic artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
Slice A appended no committed PT fixture and implemented no public PT query
surface.

## Step 1 — Persist the accepted architecture

Commit the complete specification, ADR-0013, this plan, and the adversarial
matrix. Verify that only the final corrected design and amendments are normative.

## Step 2 — Port identity, red first

Add failing contract, minting, export, golden, and forgery tests. Implement
`PORT_ANCHOR_ID_PATTERN`, `PortAnchor`, and `mint_port_anchor()` using existing
anchor validation and UUID4 conventions. Run focused system-identity tests and
commit green.

## Step 3 — PT claim contracts and canonicalization, red first

Add tests for the five exact record kinds, token discrimination, endpoint and
basis canonicalization, evidence, field exclusions, content IDs, exports, and
forgeries. Implement contracts, canonical prefixes/unions/adapters, and public
builders without altering accepted record kinds. Run focused kernel contract and
canonical suites and commit green.

## Step 4 — Validating store and indexes, red first

Add store tests for reference/evidence closure; DAG forks/convergence/replay;
PCN roots; structural PCM citations including stale-but-loadable membership;
withdrawal restrictions; immutability; atomic append; hostile records; file/time
order independence; and historical replay. Implement full prospective/load/replay
validation and immutable deterministic indexes. Do not add ModelQueries methods.

## Step 5 — First green and adversarial repair

Run focused and affected suites. Invoke architect, backend, test, and reviewer
roles against the real diff. Encode every genuine defect red before fixing it.
Stop for adjudication if any fix would change an accepted decision.

## Step 6 — Verification and status

Run system-identity, model-kernel, PT, affected composition, isolation, full,
base-only, all-extras, OCP/STEP, PDF, and loopback gates; `git diff --check`;
branch/worktree checks. Document exact counts and limitations. Final wording:

> PT-001 Slice A, including the qualified-token repair, is owner accepted.

Do not start Slice B or C, append a ledger record, push, merge, rebase, reset,
cherry-pick, or rewrite history.
