# Implementation and verification plan (proposed; not authorized)

Implementation authorization and execution authorization are separate owner
gates. This plan grants neither.

## Gate 0 — owner decisions (before any code)

The owner resolves decisions D1–D10 in `README.md`. Accepted values are then
frozen by re-issuing `schemas.json` and `policy.json` as editions, recording
their digests and taking `status: proposed` out of the frozen copies.

## Gate 1 — implementation (requires implementation authorization)

The work is TDD against the witness matrix. Each step adds tests first, from
`witnesses.json`.

| Step | Scope | New modules (application only) |
|---|---|---|
| 1 | Canonical records, rational and decimal admission, edition and catalogue checks, limits | `checked_contracts.py` |
| 2 | Pure derivation: predicted intervals, cells, baseline eligibility, T2 rule | `checked_derivation.py` |
| 3 | Pure aggregation: item-level order, condition axes, governing state, declarations, policy gate | `checked_applicability.py` |
| 4 | Selection: reuse `measurement_ranking.rank_measurements` on application-owned checked cells; mandatory score metadata | `checked_selection.py` |
| 5 | Reassessment: interval interpretation, containment and plan match, reusing the all-intersecting-branches rule | `checked_reassessment.py` |
| 6 | Evaluate/verify/replay, external pins, build capture (`ct.build.v1`), retention | `checked_runtime.py`, `checked_cli.py`, dispatch entry |

Boundaries for the implementation:

- **Unchanged:** legacy NM/NR modules, the backend, existing tests and existing
  assertions.
- **Re-baseline:** adding modules changes the current build identity of every
  route (CONTRACT §5.2), and that is accepted at Gate 0 (decision D9).
- **Test scope:** new unit tests for the witness matrix, plus named legacy
  NM/NR regression files. A full-suite run is not part of this plan.

## Gate 2 — one bounded verification step (requires separate execution authorization)

**Scope.** Exactly the 52 witnesses in `witnesses.json`, exercised through the
public CLI in one launch, plus the named legacy regression files listed at
authorization time. The workspace is new, on ext4, outside every existing
qualification root and ledger.

**Allowance.** The allowance is 128 MiB logical, 4,000 files and 800
directories. It covers temporary directories, bytecode, logs and records, and is
checked before and after each child. There is one launch and no contingency.

**Expectations.** The expected outcome of each witness is frozen and hashed
before the launch. Expectations are never weakened afterwards.

**Stop rules.** Any one of these stops the step:

- any witness outcome differing from its frozen expectation, which is then
  classified as a software defect, a witness error or a contract ambiguity, and
  never re-interpreted as a pass;
- any allowance crossed between samples, which is reported as noncompliant and
  not retried;
- any write outside the workspace;
- any legacy regression failure.

**Explicitly excluded:**

- full-suite runs and release qualification;
- physical acquisition;
- owner-issued or authenticated authority;
- deployment policy;
- XFS/durability claims.

**Deliverable.** One report giving actual outcomes per witness, resource usage
against the allowance, and every refusal. It asserts no capability beyond the
synthetic profile.

## Not in this plan

The following stay outside this plan and are not implied by preparation or
verification success:

- general hypothesis discovery;
- uncertainty-aware selection;
- action coupling;
- automatic adoption;
- backend extension;
- IN-001 / CI-001;
- an end-to-end physical producer.

END OF PLAN
