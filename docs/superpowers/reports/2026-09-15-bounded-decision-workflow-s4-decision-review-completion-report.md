# Bounded decision workflow S4 — decision review completion

## Checkpoint and commit authority

Started on `brc-exp001` at `99d6f6693945c392bd9fe5eb3b602ac3943a9dc2`.
S3 owner acceptance is `ba967d6cab8195442c5b5090f0417cb2913a8185`, accepting
implementation `17095402b4aea11f526d430c6ee8e568ce180f48`. The S3 completion report
remains `c4fe6effeb3649a7cf2aa399e60a3f279c24de9f53cec981dade0a69a8338eca`.
The preserved [S4 discrepancy report](2026-09-15-bounded-decision-workflow-s4-decision-review-discrepancy-report.md)
remains `8dc27ca1f691b58e45bc6ed3bacce9d3415931deea845b173260c0a1e0244f1a`;
the [approved design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.

The owner authorized bounded expectation/dependency corrections and S4 resumption,
not acceptance or S5–S7. The [plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
assigns S4 the fixed 22-decision inventory, prior recomputation and separation of
required review, equal-after-review and changed values.

| Commit | Scope |
| --- | --- |
| `3b2f8cdbe0bcbc5370f9bb9d537d6921402275fa` | Initial expectation/dependency correction, original historical bytes, independent specification and tests. |
| `4d7508cf25ad220d1f2f0b8aed43f2911a68f34c` | Initial maintained S4 service and tests; not the final tested implementation. |
| `8f6c74fce8b7d4608ddb7bdd664df0573d8b4089` | Separate complete-recipe correction for two further unavailable-with-prior expectations. |
| **`49ab8778882007886ce95646e2e8fa6d0b0cd28d`** | **Exact final tested implementation/test HEAD**, including opaque public-snapshot diff and actual admission-index accounting. |

The administrative commit containing this report and the plan status follows the
tested HEAD; it changes documentation only and is not a different tested build.
Resolve its full ID with `git log -1 --format=%H --` followed by this report's path.

## Implemented boundary

Maintained public application exports are `DecisionReview`, `PriorDecisionInput`
and `review_request_and_snapshot(request_wire, snapshot_wire, *, build_identity,
prior=None)` in [decision_review.py](../../../applications/bounded_decision_workflow/decision_review.py).
No caller-created admission object or observed number is accepted. Current and
captured prior request/snapshot bytes pass the accepted S1 parsing, commitment,
public reconstruction and exact observation joins. S2 effect equations and exact
Cartesian projection and S3 target/feasibility/cost policy remain authoritative.
Private composition seams are application-local, not private backend APIs.

`PriorDecisionInput` carries exact request, snapshot, review and trace bytes,
matching build identity and optional complete ancestry. Prior review/trace bytes
are compared against recomputation, never used as the decision oracle. Bad build,
profile, stale/forged public input or retained output refuses with the existing
`PRIOR_INCOMPATIBLE` diagnostic; resource refusals keep their resource class.
Cycles/malformed prior objects cannot become trusted success flags. Full prior
ancestry remains bounded: three baseline-sized worlds exceed the resolved-byte
cap and refuse before public reconstruction, rather than hiding work by reference.

The integrating application supplies its expected 64-hex build identity. This is
neither executable authentication nor an on-disk bundle verifier. S5/S6 must verify
complete manifests, derive build identity, retain all final forms and enforce the
aggregate seven-file bundle boundary. S4 only handles captured in-memory material.
`DecisionReview` exposes detached canonical review, trace and accounting values,
alongside the admitted S1–S3 result. These are slice results, not final CLI bundle
field sets. No evaluate/verify/replay or filesystem publication is delivered here.

## Corrected expectations versus runtime findings

The [initial correction record](2026-09-15-bounded-decision-workflow-s4-review-fixture-correction-report.md)
retains all 11 original specification reds and exact before/after remapping.
The [complete-sweep correction](2026-09-15-bounded-decision-workflow-s4-complete-sweep-correction-report.md)
discloses the two missed prior recipes and preserves the intermediate package.
No S1–S3 value, request, snapshot, cost, target or effect was changed to fit S4.

Current canonical package: `89ba39623a72326d876740d624af501b467179c608ae89ce9e40f66806ec0d4e`.
Manifest: `e0a94c429d69dff69d7b00351dac52ba125e858683f41c0f585c0aafbabd10fc`.
All 68 objects recover; 72 variants retain the same 27 acceptance IDs. Historical
pre-S4, pre-complete-sweep, pre-S3 and pre-OBS package/manifest bytes remain intact.
Expected command recipes are preparation authority, not command execution evidence.

The independent [test-only specification](../../../tests/applications/bounded_decision_workflow/s4_expected_reasoning.py)
uses explicit action-support tables, nominated retained sets and policy-root
propagation. It never calls the runtime dependency builder. Same-author provenance
and shared approved synthetic semantics are disclosed; this is not independent
empirical evidence. Independent set/equality checks reject missing **and** spurious
dependencies; output equality does not decide whether review is required.

| Executed service case | Required / changed / equal-after-review | Result |
| --- | --- | --- |
| No prior / identical valid prior | 0 / null / null; or 0 / 0 / 0 | Distinct no-prior and compared dispositions. |
| POL-3 cost change | 1 / 1 / 0 | Selection alone; plural aH/aHF tie. All physical and target/feasibility values unchanged. |
| POL-4 and REV-1 target change | 13 / 7 / 6 | Eight raw rows remain unchanged and not review-required; eight targets, four feasibility and selection reviewed. |
| CMD-2-unavailable and OBS-2-absent **with specified prior** | 22 / 22 / 0 | Public match becomes null with separate unavailable disposition; raw support, targets, feasibility and selection become unavailable/unknown. |
| Target change retaining the same relations | 13 / 0 / 13 | Review propagates despite all values remaining equal. |
| Relevant losing-action cost change | 1 / 0 / 1 | Selection reviewed even though the chosen action/minimum remain equal. |
| Actor, receipt or complete noneligible-cost change | 0 / 0 / 0 | Exact changed input/provenance retained without unnecessary review. |

The six formerly omitted support groups—applicability, uncertainty support, heater
effect, precondition, timing and invariance—are tested with valid baseline twins.
Global unknown support changes 21 decision values; heater-specific unknown support
changes the 11 affected aH/aHF/downstream values. Retained-hypothesis changes use
the union of prior/proposed dependencies. Parameter sensitivity includes both
changed predictions and equal predictions whose required support changed.
Unknown eligible cost still yields unknown selection; no feasible nominated action
does not mean no plan exists. Dependencies never supply effects or certify execution.

The public snapshot is one opaque `/snapshot` changed input; its entire exact
serialization remains a classification/observation support and is reconstructed
and charged. Request changes use exact leaf/frontier JSON pointers, with escaping,
deterministic ordering and the unchanged 64-path bound. No nested backend records
are silently reinterpreted as application edits.

## Red/fixed and verification evidence

At `49ab8778882007886ce95646e2e8fa6d0b0cd28d`, **474 passed in 137.89s**:
20 S1, 94 S2, 194 S3, five S3 fixture-correction, 16 S4 fixture-correction,
71 S4 service tests, and 74 affected decimal/architecture/isolation tests.
Immediately preceding focused S4 verification: **71 passed in 59.94s**.
Correction-only recovery/expectation checks: **21 passed in 4.81s**.

The exact tested command used the persistent interpreter, `PYTHONDONTWRITEBYTECODE=1`,
`-m pytest -o addopts='' -p no:cacheprovider`, the fresh ext4 `--basetemp` documented
below, and these paths:

    tests/applications/bounded_decision_workflow/
    tests/constraint_evaluation/test_decimal_parser.py
    tests/state_classification/test_architecture.py
    tests/semantic_compatibility/test_isolation.py

This is the complete affected verification, not a claim to have rerun the entire
repository suite. No unresolved defect remains in the executed S4 scope.

Implementation repairs were kept distinct from expectation corrections:

- Six initial service tests failed before the public S4 implementation existed;
  their corrected implementation passed all six.
- Three malformed public-collection cases exposed `AttributeError`/`TypeError`
  in pre-reconstruction cardinality counting. Counting now handles actual lists
  without repairing the supplied material; malformed bytes still reach and fail
  public validation. Both current and prior hostile cases and valid twins pass.
- Two frozen unavailable cases caught an incorrect string substituted for the
  null public match. The implementation now preserves the match and disposition
  separately; no oracle change was made for that defect.
- The initial 471-test run at `4d7508c` missed two supplied-prior invocations.
  Corrected expectation tests and an invocation-faithful run exposed them. The
  opaque snapshot diff and two corrected comparison expectations close that gap.
- A five-failure targeted run exposed those two snapshot comparisons and three
  index-accounting assertions. Independent call tracing observed five S1 index
  lookups for admitted observations, four for unavailable observations, not the
  earlier three-field count. S4 now reserves/charges that path under the same cap.
- Ordinary test-authoring repairs fixed an actor field/name, OBS variant labels,
  which hypothesis has a nonzero heater state, node additions for explicit limits,
  the earlier resolved-byte refusal for three worlds, and a reserved pytest argument.
  These were harness errors, not reasons to alter equations or policy.

## Resource and environment evidence

All 26 build-owned limits compare exactly with the approved package. Current and
prior semantic input is charged in full, even when identical; no reference grants
a second budget. Incremental ancestry parsing stops before unbounded accumulation;
aggregate byte/reference/charge checks precede public reconstruction and combined
corner-work checks precede arithmetic. Stricter current limits also constrain the
prior work. Result/trace serialization is bounded; refusals expose no partial
successful review. Independent counters exercise exact limits and limit-minus-one.

Measured service-output census: the 11 distinct successful `(request, snapshot,
prior-present)` combinations among prepared evaluate recipes; duplicate variants
are counted once. Each actual result was recomputed, not copied from its oracle.

| Quantity | Census maximum | Approved bound |
| --- | ---: | ---: |
| Resolved current+prior bytes | 202,875 | 262,144 |
| Prior captured request/snapshot/review/trace bytes | 122,982 | 262,144 aggregate prior budget |
| Reference occurrences / reconstruction charges | 1,382 / 7,898 | 2,048 / 8,192 |
| Combined raw+policy+review result bytes / nodes | 11,423 / 598 | 16,384 / 1,024 |
| Review trace bytes / rows | 13,586 / 30 | 16,384 / 64 |
| Corner evaluations / named decisions | 16 / 22 | 128 / 22 |

Result and trace depths peak at 8; trace nodes at 872 (distinct from result nodes).
An identical-world comparison additionally measured 202,878 resolved bytes.
The complete explicit limits map adds 26 input nodes; the exact-charge boundary
test admits 7,924 and rejects a requested ceiling of 7,923. These are measured
slice cases, not universal maxima or a substitute for S5/S6 complete output/bundle
accounting. The census can be repeated by iterating the package's successful
request-bearing variants, honoring each prior recipe, deduplicating that triple,
and counting canonical `raw_projections + policy + reevaluation` and `trace_bytes`.

Persistent workspace is
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`.
Outside the sandbox the actual backing filesystem was `/dev/sdc`, ext4, read/write;
the development checkout remains `/mnt/d`. CPython is 3.13.11 from
`environments/cp313-bdw001/bin/python`. Provisioning verification returned `verified`:

- Environment identity: `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`.
- Retained artifact set: `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
- Lock text: `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e`.

Only the newly exclusive `test-workspaces/s4-final-uTfqQ3` directory was used for
test files; existing runtime inputs, results, environment and artifacts were not
repurposed. Final pytest used its new `pytest-complete` child, not an existing
basetemp. Reproduction must likewise use a new exclusive ext4 test directory.
No filesystem publication, crash-durability, command or replay claim follows.

## Preservation and owner gate

The 880-file starting inventory is preserved except authorized application/test,
plan and candidate corrections. No original file disappeared. All 63 unrelated
untracked artifacts, accepted S3/discrepancy/design/review bytes, backend contracts,
authoritative fixtures/ledgers and retained runtime evidence remain unchanged.
Canonical JSON, object recovery, historical hashes, local links, markers, exact
staged scope and whitespace are checked. Disposable correction tooling is removed
only after recovery; no retained runtime material is cleared.

S4 delivers bounded application-owned named-decision review, not full application
delivery. It claims neither empirical accuracy nor causal identification, physical
execution, generated alternatives, multi-step planning or global optimality.
IN-001 and CI-001 remain open and unselected. Owner gate: **accept S4**;
S5 retention/recovery, S6 CLI/replay and S7 release acceptance remain unauthorized.
No backend extension, dependency change, physical operation, push, merge or history
rewrite occurred.

END OF BOUNDED DECISION WORKFLOW S4 DECISION REVIEW COMPLETION REPORT
