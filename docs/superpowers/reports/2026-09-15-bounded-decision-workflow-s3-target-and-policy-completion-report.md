# Bounded decision workflow S3 — target and policy completion

## Checkpoint, scope and authority

Branch: `brc-exp001`. This resumption began at
`7270dacf5567209923530b64c5f75b89832ae07f`.
S2 remains accepted at implementation `aa454b53063c1e6a88f4fe398dbd787873241d0e`,
with [owner acceptance](2026-09-15-bounded-decision-workflow-s2-owner-acceptance.md)
committed separately at `0a2864c63cc64b8be7b16aa4f19d69e167778daf`.

The owner authorized correction of four documented fixtures and resumption of the
existing [S3 slice](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md),
not a replacement slice or S4–S7. Correction commit:
`78c4aa75624f03e2017632aadd8aa8375a8ed69d` (also the S3 implementation starting HEAD).
Exact implementation/test HEAD:
**`17095402b4aea11f526d430c6ee8e568ce180f48`**.
The later completion/status commit is administrative only.

The frozen [design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The [blocker report](2026-09-15-bounded-decision-workflow-s3-target-and-policy-blocker-report.md)
remains `5fbae38608d6a04d3967d6f4bdb86eaa1842bf72e20f324a9b6e57691a0c8d66`;
its historical blocked disposition is superseded here, not edited away.

## Fixture correction and actual branch reachability

The [correction report](2026-09-15-bounded-decision-workflow-s3-policy-fixture-correction-report.md)
records every field change, old/new request and expected-result commitment,
normative diagnostic and nearest valid twin. No cost, target, effect, numerical
semantics or validation precedence was changed.

- Corrected package: `df9766b51dea3339b9b2096ab3a96ea75ff01b130b6eb913da86d337c5d7cb1e`.
- Corrected manifest: `9b9effe6809bb49ad2f0a7cd1096eeef688ef17dee1a87f44b0832af1e478de9`.
- Historical pre-S3 package: `199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`.
- Historical pre-S3 manifest: `5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.

All 44 canonical objects recover with exact lengths/hashes; the 38 original
objects remain byte-identical, including the three stale cost requests. The
original 27 acceptance IDs and 69 variants remain intact. Additional stale
admission controls are separately labelled, never counted as policy coverage.

| Corrected case | Actual result through maintained S3 | Separate control |
| --- | --- | --- |
| POL-2-missing-effect | Omitted E-aH refuses `REQUEST_SCHEMA_INVALID`, lexical schema, request, exit 3. | Baseline admits; envelope present with missing/unknown body produces unknown aH/aHF outcomes, not edition refusal. |
| POL-3 | Observation admitted; eight raw rows ready; aH/aHF guaranteed for retained H_H; both selected at cost 5. | Original stale nested commitment refuses before policy; baseline selects aH at 2. |
| POL-5-tie | Observation admitted; aH/aHF both selected at cost 2. | Original stale commitment refuses before policy; baseline is valid. |
| POL-5-missing-cost | Observation admitted; aH/aHF guaranteed, but missing aH cost leaves selection unknown. | Original stale commitment refuses before policy; baseline is valid. |

All active request premise commitments were swept. No additional semantic
contradiction or mechanical repair was needed. The POL-1 “mixed” frozen request
has two unknown rows, so its name is not used as evidence for mixed
unknown/incompatible precedence: the explicit decision-table tests cover that
otherwise unreachable combination independently.

## Maintained S3 capability

The additive public function
`assess_request_and_snapshot(request_wire: bytes, snapshot_wire: bytes) -> PolicyReview`
in [policy.py](../../../applications/bounded_decision_workflow/policy.py) accepts
wire bytes, not caller-created admitted objects. It reuses authoritative S1
admission and the accepted S2 projection core. No backend private API, ledger,
source adapter or deleted disposable implementation is used.

[Policy validation](../../../applications/bounded_decision_workflow/policy_profile.py)
checks exact policy identities, application-policy provenance, editions,
availability, retained-set membership, cost inventory, fixed policy meanings,
units, closed endpoints and bounded reduced rational values. Policy numeric JSON
shapes now participate in S1 lexical validation before public reconstruction;
this completes the prepared input schema without changing admission order. S2's
core was factored privately so S3 can validate both premise profiles before
projection arithmetic. The S2 public path and its raw semantics remain intact.

S3 returns eight target relations, four robust-feasibility decisions and one
finite selection. `PolicyReview` retains the S2 review, admitted current-condition
answer and full caller-premise provenance, with immutable canonical policy/trace
bytes and detached JSON accessors. These are slice results, **not** the final
retained `result.json`/`trace.json` or a released command.

Exact closed-set subset/intersection/disjointness determines target relations;
endpoint contact is intersection. Explicit false gates dominate missing support;
unknown retained outcomes dominate incompatible outcomes for robust feasibility.
Missing target/cost/policy support never receives a default. Only guaranteed
nominated actions are eligible. Unknown eligibility with absent or lower/equal
cost blocks selection; a known higher cost cannot conceal a tied minimum. Every
minimum-cost tie remains plural, in canonical action order. “No feasible action”
is explicitly scoped to the nominated set and robust policy, not global
impossibility. Malformed, stale or unsupported premises refuse rather than
becoming scientific unknowns.

Raw predictions do not depend on targets or costs. Target changes recompute fresh
target/feasibility/selection values; cost changes preserve raw, target and
feasibility values. S3 does **not** compute a prior-world reevaluation set or claim
that unchanged values mean no reevaluation is needed; that is S4.

## Verification and independent reasoning

At the exact tested HEAD, the persistent interpreter ran:

```text
python -m pytest -q -o addopts='' -p no:cacheprovider
  --basetemp=<fresh-ext4-test-root>/pytest
  tests/applications/bounded_decision_workflow
  tests/constraint_evaluation/test_decimal_parser.py
  tests/state_classification/test_architecture.py
  tests/semantic_compatibility/test_isolation.py
```

Actual result: **387 passed in 87.33s**: 20 S1, 94 S2, five fixture-correction,
194 S3 and 74 affected regression/isolation tests. Rerunning S1/S2 was warranted by
the lexical-schema addition and private projection factoring; no full unrelated
production suite or completed disposable experiment was rerun.

[S3 tests](../../../tests/applications/bounded_decision_workflow/test_s3_target_and_policy.py)
cover all ten frozen successful semantic variants across NUM-1, UNC-1/2 and
POL-1–5, both POL-2 refusal recipes, and distinct supplemental obligations:

- 81 finite-set interval comparisons independently check subset, intersection,
  disjointness and endpoint inclusion; exact [30,34] uncertainty tests check
  containment, contact, disjointness and nominal-only optimism.
- All 16 two-row feasibility combinations, each also with false-gate and
  unsupported-policy variants, include unknown-plus-incompatible precedence.
- Independent enumeration of possible eligibility/cost completions checks hidden
  cheaper/equal/higher actions; integration tests exercise those branches through
  genuine S1/S2 results. Missing noneligible cost is disclosed but ignored.
- True/false/missing/unknown action-support twins, missing policy envelopes versus
  missing bodies, retained H_F/H_H/both, absent admitted observation, exact
  fractional ties, unsupported policy and stale/edition/inventory attacks.
- Target/cost-only and irrelevant-provenance changes, immutable/detached results,
  deterministic semantic and trace bytes, admission-before-policy assertions,
  numeric-shape diagnostic precedence and public application import isolation.

The frozen expectations predate this implementation. Additional expected reasoning
uses finite sets, independently specified tables and possible-completion
enumeration, not the implementation's relevant helper. The independent arithmetic
for H_H/aH is `40 - 4 - beta*(40-20) = 36-20*beta`; beta [1/10,3/10] gives [30,34].
The approved equation, hard-support assumptions and finite policy are shared;
same-author oracle provenance remains disclosed. This is mathematical/software
consistency, not empirical evidence or causal identification.

Red/fixed evidence: the first S3 development run had 174 passing and five failing
tests because new resource tests tried to modify baseline `requested_limits=null`.
An intermediate partial-object repair correctly triggered required-field schema
refusals (four failing, one passing targeted tests). The tests were repaired to
supply the complete build-limit object; the five targeted tests then passed.
The initial precedence test's incomplete object could have masked its intended
branch; the complete object now isolates numeric-shape precedence. No production
semantic change, lowered cap, oracle change or validation bypass was used to fit
these test-harness errors. No unresolved defect remains in the tested S3 scope.

## Resource and environment evidence

Build-owned limits are unchanged. S3 charges combined raw+policy result bytes and
nodes, and combined raw+policy trace bytes/rows, not a separate full allowance per
layer. Serialization is incremental; refused calls return no partial successful
review. Independent counters test each exact output boundary and boundary-minus-one.
The maximum 128-corner workload is also tested through S3.

Measured supplemental output census: ten frozen successful semantic variants plus
the 128-corner box (not a universal worst-case claim):

| Quantity | Observed maximum | Approved bound |
| --- | ---: | ---: |
| Combined raw+policy result bytes | 2,815 | 16,384 |
| Combined result nodes | 160 | 1,024 |
| Combined trace bytes | 15,175 | 16,384 |
| Top-level raw+policy trace rows | 21 | 64 |
| Corner evaluations | 128 | 128 |

Trace nodes peaked at 1,669 (not result nodes); measured result/trace depths were
6/8, with root counted as one. The 128-corner trace's nodes do not violate the
result-only node cap. These are current slice outputs; S6 must still account for
the final complete CLI/retention forms, not substitute these partial measurements.

Verified workspace:
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`.
Actual backing filesystem outside the sandbox was `/dev/sdc`, ext4, read/write;
the checkout remains on `/mnt/d`. Tests used only the fresh directory
`test-workspaces/s3-policy-verification-yYmS4Z/pytest`, not runtime inputs/results.
Interpreter: `environments/cp313-bdw001/bin/python`, CPython 3.13.11.
The provisioning verifier returned `verified`, with unchanged identities:

- Environment: `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`.
- Dependency artifact set: `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
- Lock text: `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e`.

For reproduction, use that interpreter from the checkout and a **new** exclusive
test directory under the verified ext4 workspace; never reuse pytest's basetemp
against existing material. No dependency installation or physical operation ran.

## Preservation and acceptance gate

The 870-file starting inventory was checked: no original file disappeared; only
the authorized application, candidate package/manifest, test and plan files
changed. All pre-existing unrelated untracked artifacts, authoritative fixtures,
backend/ledger files, S1/S2 accepted evidence and frozen design/review bytes were
preserved. Historical archives recover without disposable tooling. Scoped staging,
local links, markers, digests and whitespace were checked. Temporary correction
tooling was removed only after recovery verification; the environment, inputs,
results and dependency artifacts remain in place.

S3 target/policy implementation is complete and awaits owner acceptance. S4
named-decision review, S5 retention/recovery, S6 evaluate/verify/replay CLI and full
resource delivery, and S7 release gate remain pending and unauthorized. No CLI,
retention/replay acceptance, backend extension, physical accuracy, automatic action
generation, multi-step planning or global minimality is claimed. IN-001 and CI-001
remain open and unselected. No successor, push, merge or history rewrite occurred.

END OF BOUNDED DECISION WORKFLOW S3 TARGET-AND-POLICY COMPLETION REPORT
