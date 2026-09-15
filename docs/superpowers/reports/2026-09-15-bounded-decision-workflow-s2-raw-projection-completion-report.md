# Bounded decision-workflow S2 raw-projection completion report

Date: 2026-09-15

Status: S2 implemented and verified; awaiting owner acceptance. S3–S7 remain
unauthorized. This is a maintained application slice, not the complete release.

## 1. Checkpoint, acceptance and exact implementation identities

The starting branch was `brc-exp001` at administrative HEAD
`682e0ff5907da3dd543b796b83120c5712d9d587`, exactly the owner checkpoint.
The accepted S1 implementation/test ID resolves to
`160bfc597655fc24b97301b8d1d400df86e68887`. Its only subsequent change at that
checkpoint was its administrative completion report. Git retains the entire S1
source/test implementation; no deleted experimental driver is needed.

The unchanged [S1 report](2026-09-15-bounded-decision-workflow-s1-input-public-admission-completion-report.md)
matches `a9c0dea75c17184d7ce00d40b08d3d3ce842ff44481013851fc9cbd13c9d24ab`.
The owner acceptance was recorded separately in
[S1 acceptance](2026-09-15-bounded-decision-workflow-s1-owner-acceptance.md), SHA-256
`b30f16f6b1b3f84dcc61351c54b8d1ebe9b89c8eeeb472c212271c622bc0e2ce`.

| Commit | Scope |
| --- | --- |
| `e5168a5e3d6fd14745fe9a2bb57649baabd5f21d` | Separate S1 owner acceptance and plan status; S2 starting HEAD. |
| `1ab7e4a382f502d9cda48291e69268bc9203e14e` | Maintained S2 code, readonly limit mapping, and additive public-surface assertion. |
| `27f6a2011c1f02aef9d771e6e19e98583730643f` | Independent S2 tests; initial tested implementation/test HEAD. |
| `c7e4955ae12bdc12312c6e5ae59a3dd90d19a027` | Initial completion record; followed by the final two-fault precedence check below. |
| `aa454b53063c1e6a88f4fe398dbd787873241d0e` | Numeric schema-order repair and regression; exact final tested implementation/test HEAD. |

The final report update after `aa454b5` is administrative only.
Each staged scope was inspected; no unrelated artifact was staged.

## 2. Governing contracts and preserved evidence

The complete [corrected design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The [implementation plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
defines S2 as exact rational/profile validation, gates, effects, Cartesian corners
and raw traces only. Its historical preparation restrictions are superseded only
by the separately recorded authorizations, not by implementation self-approval.

The corrected [package](2026-09-15-bounded-decision-workflow-candidate-package.json)
and [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) remain
`199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`
and `5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.
The [correction report](2026-09-15-bounded-decision-workflow-obs3-decimal-fixture-correction.md)
and original `pre-obs3-decimal-correction` package/manifest remain intact. The
original commitments remain
`0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`
and `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`.
Recovery tests rechecked all current and historical content-addressed objects.
Neither the package nor its oracle was edited for S2.

Admission precedence is preserved: stale snapshot/reference pairing refuses with
`SNAPSHOT_COMMITMENT_MISMATCH`; matching hostile snapshot content reaches and is
refused by authoritative reconstruction as `PUBLIC_RECONSTRUCTION_REFUSED`;
decimal reparsing follows successful reconstruction. S2 numeric JSON shape
validation occurs in request schema admission, before snapshot reconstruction;
it does not bypass or reorder these commitment/public-admission checks.

## 3. Delivered S2 scope

The additive public function `project_request_and_snapshot(request_wire,
snapshot_wire)` returns a `RawProjectionReview`. It always reenters S1 with the
captured canonical bytes; it does not trust a caller-created admission object or
caller-supplied observed number. It returns the separate S1 assessment/admission,
canonical raw-projection bytes, canonical raw-trace bytes and corner count.
Detached JSON accessors cannot mutate those result bytes.

Maintained code is limited to
[projection](../../../applications/bounded_decision_workflow/projection.py),
[profile validation](../../../applications/bounded_decision_workflow/projection_profile.py),
and narrow S1 input/export integration. There is no filesystem I/O, store, source
connector, dynamic expression evaluation or expected-result import in S2.

The implementation:

- validates the exact fixed profile, application IDs/edition, synthetic authority,
  units, hypothesis/action inventories, effect bodies, timing and invariance forms;
- represents numbers as reduced integer rationals and closed intervals, refusing
  floats, booleans-as-integers, invalid denominators, unreduced/reversed support,
  open endpoints, unsupported correlation, unit substitution and stale premises;
- uses only the publicly admitted decimal for singleton `T0`, with bounded exact
  conversion; missing support remains missing even when a multiplier is zero;
- applies false-gate precedence, then missing/unknown-frontier handling, before
  applying supported before-step assignments and the fixed equation once;
- evaluates every distinct Cartesian corner, sharing repeated coordinates, and
  derives the exact minimum/maximum without rounding, clipping or a decoder; and
- retains distinct raw rows and a trace of effect IDs, premise IDs, frontiers,
  pre/post assumed `h/f`, coordinate endpoints and each corner's indices/value.

Trace request/snapshot commitments bind complete retained S1 bytes, including
all premise editions, assumptions, issuer assertions and observed provenance.
These are carried application premises, not backend registrations. Command states
and effects remain assumptions, not issued commands, execution or causal proof.

Raw rows match the frozen result field set. The S2-only detailed trace is an
application-service seam, not a claim to have delivered the final combined
`trace.json`, policy decisions, bundle or command. S3–S6 must integrate their
separate layers within the unchanged aggregate policy.

## 4. Acceptance coverage and independent expected reasoning

The maintained [S2 tests](../../../tests/applications/bounded_decision_workflow/test_s2_raw_projection.py)
contain 94 collected cases. Package mutations are materialized only in test memory;
their enclosing premise hashes are recomputed, preserving original valid twins.
The prose reversed-interval recipe is concretized as beta lower `3/10`, upper
`1/10` (not a no-op reversal of the baseline singleton).

| Obligation | Verified S2 coverage |
| --- | --- |
| NUM-1 | Frozen baseline rows, singleton endpoints, exact nonterminating `1/3` result; float, reversed, correlation and 129-digit refusals; additional denominator, reduction, boolean, unit and negative-zero controls. Target contact remains S3. |
| UNC-1 | Frozen widened beta raw rows; `H_H/aH=[30,34]`; overlapping rows remain separate. Target feasibility remains S3. |
| UNC-2 | Frozen missing-support rows, each of four coordinates missing/unknown, stale refusal, no nominal fallback; malformed versus unavailable distinction. |
| S2 gates/effects | True/false/missing/unknown global, precondition, timing and invariance twins; false dominates unknown; structural refusal dominates gates; each missing/stale effect; missing law/support/commands/hypothesis/action premises. Only raw portions of POL-1/2 are exercised. |
| Sensitivity and provenance | Changed command assumptions, all four uncertain coordinates, sign-crossing supports, target/cost-only raw invariance, exact effect order and provenance changes. No S3 selection or S4 reevaluation claim. |
| Admission and isolation | Public unavailable observation has no fallback; corrected hostile/stale snapshots stop before projection; lexical float refusal precedes a later bad snapshot commitment; no backend/private/oracle access in S2. |
| Bounds and outputs | 128 corners at ceiling; tightened seven-corner refusal before enumeration; 128-digit valid and 129-digit invalid twins; bounded intermediates; result byte/node and trace byte/row exact/tightened refusals with no partial result. |

The frozen same-author preparation oracle uses `Fraction` and Cartesian corners.
Tests compare all raw rows and raw portions of the frozen trace, never the
not-yet-implemented target/policy output. An additional independently written
Decimal oracle factors the interval into heating, cooling and `beta*(T0-A)`
extrema; it does not call the runtime's arithmetic helpers. For two full-box
cases it checks all eight exact ranges and every corner using the algebraically
rearranged expression `(1-beta)*T0 + beta*A + alpha*h - gamma*f`.
These fixtures use terminating decimals and precision 80, exceeding their exact
digit requirement. The separate `1/3` case uses a literal exact rational expected
answer, not an approximate Decimal comparison. Assumptions and authorship are
shared; this is implementation/mathematical checking, not independent empirical
evidence.

## 5. Verification and resource measurements

Before acceptance, the recovered S1 boundary and the exact previously reported
regression selection passed **233 tests in 43.42s**: 20 focused plus 213 affected.
This confirms the recorded results without running the full production suite.

The first S2 run passed 91 tests; added corner-trace, digit-boundary and
observational-claim checks brought that to **93 passed in 48.41s**. At exact HEAD
`27f6a2011c1f02aef9d771e6e19e98583730643f`, initial verification passed
**187 tests in 56.70s**: 20 S1, 93 S2, and 74 affected decimal/architecture/import-
isolation tests. The final schema-order regression described below was then added
and the same focused selection rerun at `aa454b5`: **188 passed in 54.74s**
(20 S1, 94 S2, 74 affected). The earlier 213-test selection was not repeated after
S2; backend bytes were unchanged.

Final command from the checkout (use a new, nonexisting ext4 test basename for
any later rerun):

```text
PYTHONDONTWRITEBYTECODE=1 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/applications/bounded_decision_workflow tests/constraint_evaluation/test_decimal_parser.py tests/state_classification/test_architecture.py tests/semantic_compatibility/test_isolation.py --basetemp=/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/s2-final-20260915b -q
```

Independent recursive counters (root depth one, maps/lists/scalars as nodes, keys
not nodes) measured seven representative complete S2 pairs: baseline, widened
beta, four-coordinate box, sign-crossing box, missing beta, false applicability
and 128-digit alpha. These are measurements of this named set, not universal
maxima for every test input or the future complete workflow.

| Quantity | Measured maximum in that set | Approved boundary applied |
| --- | ---: | ---: |
| Request bytes / nodes / depth | 16,712 / 550 / 8 | 32,768 / 8,192 / 32 |
| Snapshot bytes / nodes / depth | 84,979 / 2,679 / 15 | 131,072 / 8,192 / 32 |
| Current request + snapshot bytes | 101,691 | 262,144 resolved bytes |
| Raw result bytes / nodes / depth | 2,267 / 105 / 5 | 16,384 bytes / 1,024 nodes |
| Raw trace bytes / nodes / depth | 13,065 / 1,570 / 7 | 16,384 bytes; no invented trace-node cap |
| Projection trace rows / corners | 8 / 128 | 64 rows / 128 corners |

Baseline raw bytes commit to
`04fbf31cf87cd3d860510f3c8b9472fe7942ba2410b3a3a7b6456cc8d19d3d19`;
baseline S2 trace bytes to
`95f678ea75c6196e4600f0b42a7df129856f8116fca96bc313ab28dc04ea8919`.
The full-box measurement uses A `[15,25]`, alpha `[8,12]`, gamma `[3,5]`,
beta `[1/10,3/10]`; the sign-crossing case uses A `[35,45]`, alpha `[-2,3]`,
gamma `[-3,4]`, beta `[-1/2,1/2]`. All otherwise preserve the baseline.
The 128-digit case sets both alpha endpoints to `10^127`. These definitions and
the committed tests recover the measurement inputs without an extra archive.

Numeric operands are bounded before fraction construction, and intermediates are
bounded after each fixed operation. Total corner work is checked before
enumeration. Result/trace serialization checks each encoded chunk before extending
its bounded byte buffer. A refusal returns only the existing typed diagnostic,
not partially successful rows. S6 still owns complete command-level, aggregate
input/output, resolution-accounting and release resource verification.

One ordinary implementation-order defect was reproduced before closeout: beta
lower `0.2` combined with requested `corner_evaluations=129` returned the inherited
profile-limit diagnostic `REQUESTED_LIMIT_RELAXATION`, concealing the earlier
`REQUEST_SCHEMA_INVALID` numeric shape failure. The new regression failed once
at the initial implementation. Moving the new S2 shape check ahead of the existing
limit-profile check produced **2 targeted passes in 2.29s** (including the nearest
float/bad-snapshot ordering control). The committed regression retains the red
input; no expectation or approved precedence was weakened. Public reconstruction,
snapshot commitment and decimal defense ordering are unchanged.

Code inspection
found that S1's exported build-limit table was a mutable dictionary despite the
immutable-policy intent; S2 wraps the exact unchanged values in a readonly mapping.
Its mutation-refusal regression passes. No premise, oracle, numerical ceiling or
backend contract was changed to fit the implementation. No unresolved S2 defect
or necessary new premise remains.

## 6. Environment, preservation and remaining gates

Tests used the approved isolated CPython 3.13.11 environment under
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`.
`findmnt` reconfirmed ext4 on `/dev/sdc`; `namei` confirmed the private owned
workspace and test parent contain no symlink components. Test writes were limited
to new `test-workspaces/s2-s1-acceptance-20260915a` and
`test-workspaces/s2-final-20260915a` and `test-workspaces/s2-final-20260915b`
roots. S2 projection itself performs no I/O.

The provisioner passed before and after verification, reproducing environment
identity `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`
and artifact set `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
No dependencies or runtime locations changed. Runtime `inputs/` and `results/`
remain untouched and empty; dependency artifacts and provisioning evidence remain
verified. The checkout remains on `/mnt/d`. No filesystem durability or retained-
decision acceptance is claimed from these application tests.

A pre-edit SHA-256 inventory covered 863 existing repository files. Only the
authorized plan status, application exports/input integration and S1 surface
assertion changed among those files; all other existing bytes, including backend,
authoritative evidence and unrelated untracked artifacts, were preserved.
Focused link, frozen/historical digest, archive-recovery, staged-scope and
`git diff --check` checks passed.

S2 adds maintained conditional raw calculation, not empirical accuracy, actual
effects or causal identification. IN-001 and CI-001 remain open and unselected.
The next gate is **owner acceptance of S2**. S3 target/feasibility/selection,
S4 decision review, S5 retention/recovery, S6 resource/CLI/replay integration and
S7 release checks remain unimplemented and unauthorized. No backend extension,
physical acquisition, ledger mutation, new dependency, ADR, push, merge or history
rewrite occurred.

END OF BOUNDED DECISION WORKFLOW S2 RAW-PROJECTION COMPLETION REPORT
