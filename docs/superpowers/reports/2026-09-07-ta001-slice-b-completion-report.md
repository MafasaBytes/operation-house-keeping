# TA-001 Slice B Adversarial-Hardening Completion Report

Date: 2026-09-07

## 1. Outcome and owner gate

TA-001 Slice B adversarial hardening is complete at exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`. The later branch HEAD
`4d1452074e968a534762c019c2dfb328e064e3fa` changes documentation only. It
does not change the tested implementation.

The branch is `ta001`. Slice A remains accepted at
`76738ac0d098eb59b0fec4f6970aa862528647d9`; its documentation-only owner
acceptance is `2e92b3a89287f4b5f04938c13ea562180f838b19`. This report is deliberately
uncommitted for owner review. Final TA-001 acceptance is not recorded here.

No Slice C or demonstration slice exists. No facade, second consumer,
authoritative demonstration, occurrence claim, persistent result artifact,
or ledger append was created. Nothing was pushed or merged, and no history
operation was performed.

## 2. Authority and accepted inputs

The implementation was hardened strictly against:

- `docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`, verified SHA-256
  `3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`;
- the accepted Slice A implementation
  `76738ac0d098eb59b0fec4f6970aa862528647d9`;
- the owner-authorized Slice B prompt, 402 lines, 16,750 UTF-8 bytes, SHA-256
  `228b9f907c198b7c90171d853ed7ae9de5139315abe7c467fd2f375b7e9ed4c8`;
- the committed Slice B plan
  `docs/superpowers/plans/2026-09-07-ta001-slice-b-adversarial-hardening-plan.md`.

The design synthesis was not changed. Accepted lower production packages were
not changed. The work started from documentation checkpoint
`b9e506fe918fee860707cd57e08502e62194c3dc` with a clean tracked tree and the
ignored local settings file preserved.

## 3. Forward commit record

The complete forward-only commit sequence is:

1. `2e92b3a89287f4b5f04938c13ea562180f838b19` — `docs: accept TA-001 Slice A`
2. `13299e4bce70181d7929a568d110ef20c391ecf8` — `docs: plan TA-001 Slice B hardening`
3. `fbdfab4174cd22464f56f6a5dd0e894200d30cfa` — `test: expose TA-001 Slice B validation defects`
4. `a141a9028706019319d4a56ff9f34438756f464a` — `fix: harden TA-001 result preflight`
5. `7d5e5210d285866abc0ab4aa1feefaa116d7a0b9` — `test: expose TA-001 reconstruction scheduling defects`
6. `a91f93e06dc2ecaa9ce80682fe0536e531807455` — `fix: enforce TA-001 structural scheduling`
7. `5ed7c769d58931f11e097b7c05e2ce263299a9ad` — `test: close TA-001 endpoint and evidence matrix`
8. `3d739c20b24b5df062d0dad88c510f9763e4f8db` — `test: expose TA-001 scalar subclass dispatch`
9. `7593235b0ae8df6d6b925d0456f7eea9f7f553fa` — `fix: reject hostile TA-001 scalar subclasses early`
10. `c7547ace140355984e1d1b238adac54ff2c2264f` — `test: expose TA-001 compact model private state`
11. `5943869e5649ff919166f0aaf81632e2906fe019` — `fix: reject TA-001 compact model hidden state`
12. `fc227ece0b7f7b011a821a704367afb4062232d1` — `test: close TA-001 Slice B adversarial matrix`
13. `c6827dac4ea10c83a4efe1861a5ef4c200e8c70e` — `test: expose final TA-001 reconstruction defects`
14. `9bf28abc0d0755c725225a9c264f994ef257bfdb` — `fix: close final TA-001 reconstruction bypasses`
15. `8abee3cccd46190a692655536d3b5c3a1e7a4857` — `test: expose nested TA-001 union scheduling gap`
16. `4bba81b3ee7e644a4c6af7e0e0e17288cb38fb6f` — `test: expose TA-001 cross-union substitution`
17. `4060b55d500757fae4ce72c07353818b16e5b82b` — `fix: enforce nested TA-001 union arms precisely`
18. `bc34d750b8ddfa5e5cd0fb5c6d8e56c99a54fc20` — `test: expose TA-001 exact-model union substitution`
19. `2028bcdd138ba5f01ac8972bac8093841b6de1d5` — `fix: reject exact-model TA-001 union substitutions`
20. `2ec18f7234273dba98098d268df4568d5cc84d85` — `test: complete TA-001 final coverage witnesses`
21. `4d1452074e968a534762c019c2dfb328e064e3fa` — `docs: record TA-001 Slice B verification state`

Every defect commit is preceded by a permanent red test commit. The final two
commits contain no production changes: one completes green witnesses at the
tested implementation, and one truthfully reconciles status documentation.

## 4. Changed files and production boundary

Slice B production changes are confined to:

- `backend/transition_assessment/preflight.py`;
- `backend/transition_assessment/contracts.py`;
- `backend/transition_assessment/derivation.py`.

Adversarial tests and test-only builders changed under:

- `tests/transition_assessment/`;
- `tests/behavior_evaluation/helpers.py`.

The behavior-evaluation file is a test helper only; no existing production
consumer imports TA. Documentation changes comprise the Slice A acceptance,
the Slice B plan, and current status wording in package/root guidance and
ADR-0020. No source/temporal/model/evidence lower implementation, schema,
fixture, membership, record, ledger, or artifact-generation file changed.

The ordered public contract, public limit values, error vocabulary, and
single function surface were preserved. No new persistence, I/O, connector,
clock, environment, identity, registry, cache, or write facility was added.

## 5. Red-before chronology and fixed-after evidence

Eight red runs established 25 failing pytest cases before their repairs:

1. Five failures exposed incorrect compact-result cardinality handling, fixed
   cardinality scheduling, unbounded huge-integer conversion, hidden-key
   representation access, and falsey/private Pydantic state. The permanent red
   commit is `fbdfab4`; the five-test repair gate passed at `a141a90`.
2. Ten failures exposed boolean fixed counts, booleans in integer collections,
   wrong context union arms, repeated lower reconstruction, and result-cycle
   scheduling after lower work. The red commit is `7d5e521`; all ten passed at
   `a91f93e`.
3. One failure exposed hostile `datetime` subclass dispatch before strict
   scalar admission. It is preserved at `3d739c2`; the hostile and valid
   datetime twins passed at `7593235`.
4. One failure exposed hidden private state in a compact public result model.
   It is preserved at `c7547ac`; all compact model arms rejected hidden state
   after `5943869`.
5. Five failures from the final independent backend review exposed an ambient
   preflight-bypass flag, raw exception cause/context retention, mutable shared
   limit poisoning, a wrong lower predicate union arm, and coercible floats in
   fixed integer literals. They are preserved at `c6827da`; the focused repair
   gate passed after `9bf28ab`.
6. One nested-record union scheduling failure is preserved at `8abee3c`.
7. One same-field cross-union substitution failure is preserved at `4bba81b`.
   Both nested union failures passed after `4060b55`.
8. One exact trusted-model wrong-union-arm failure is preserved at `bc34d75`;
   it passed after `2028bcd`.

Valid twins remained green throughout: exact built-in strings, integers,
booleans, finite floats, and datetimes; candidate index zero; correct union
arms as both plain values and exact models; ordinary hidden-free models;
correct compact partitions; and the accepted alignment order.

The original accepted Slice A gate was 57 passed in 146.24 seconds. After the
first repair batch the focused suite was 62 passed in 153.29 seconds; after the
structural scheduling batch it was 72 passed in 111.27 seconds. The final
complete TA package gate is 120 passed.

## 6. Repair behavior

The repairs do not alter TA policy. They make the existing boundary enforce
the accepted contract before lower derivation:

- structural preflight owns one aggregate byte/node/depth budget and rejects
  cycles, unsupported containers, hidden extras/private state, hostile scalar
  subclasses, and wrong union arms before using dependency material;
- unbounded integer-to-string conversion and hostile `repr`, equality, hash,
  length, iteration, and serialization hooks are not invoked for rejected
  inputs;
- strict fixed integers reject booleans and floats without coercion;
- exact built-in finite floats remain admitted and canonically encoded as JSON
  numbers; subclasses, NaN, and infinities reject typed;
- lower state-classification and evidence-alignment values are reconstructed
  once per endpoint/alignment under the original aggregate budget;
- compact result partitions are independently rederived and validated without
  I/O, and hidden/private state cannot manufacture a valid result;
- the preflight completion marker is invocation-local rather than ambient
  mutable state;
- typed TA input failures suppress raw exception cause and context so paths,
  credentials, and hostile text are not leaked; and
- trusted exact model instances still undergo exact union-arm admission and
  cannot bypass structural scheduling.

These are integrity repairs to accepted behavior, not new architecture or a
new conclusion vocabulary.

## 7. T01-T25 acceptance reconciliation

Each row below has a permanent direct TA witness. “Structured” means a valid
lower world returns the accepted issue/result rather than raising a malformed
input exception.

| Row | Final evidence |
|---|---|
| T01 | Complete matched endpoints execute and return bounded evidence support through the full gate. |
| T02 | A from-only endpoint non-match executes and returns bounded non-support, without occurrence wording. |
| T03 | The symmetric to-only endpoint non-match executes and returns bounded non-support. |
| T04 | An unregistered transition maps to structured `transition_not_registered` and does not execute. |
| T05 | Registered-but-undeclared maps to `transition_not_declared`. |
| T06 | A same-root declaration fork maps to structured conflict; no winner is selected. |
| T07 | Cross-root declaration disagreement maps to structured conflict; no winner is selected. |
| T08 | A withdrawn declaration lineage maps to inactive and does not execute. |
| T09 | A superseded from-pin produces the exact pin issue. |
| T10 | A withdrawn to-pin produces the symmetric pin issue. |
| T11 | Valid lower conflicted/inactive classification is retained and prevents execution. |
| T12 | A valid distinct request-anchor world yields `transition_anchor_mismatch`. |
| T13 | From-state substitution retains from-anchor and independently applicable subject issues in order. |
| T14 | To-state substitution proves the symmetric ordered diagnostics. |
| T15 | Same-anchor, different-subject material yields only the distinct subject relation/issue. |
| T16 | A valid other transition context yields `context_mismatch`. |
| T17 | From and to endpoint/global context mismatches are independently witnessed. |
| T18 | A valid substituted transition result yields the exact anchor issue and no malformed-input escape. |
| T19 | Equal cutoffs are structured non-execution while independent declaration admission remains disclosed. |
| T20 | Reversed cutoffs are structured non-execution. |
| T21 | Equivalent timezone offsets normalize to UTC and produce identical canonical bytes. |
| T22 | Naive and hostile datetime inputs reject before lower access; exact aware datetimes remain valid. |
| T23 | Isolated from/to classification cutoff substitutions yield the endpoint cutoff issue. |
| T24 | A valid divergent model revision yields `model_revision_mismatch`. |
| T25 | Isolated from-classification non-execution yields the from-side classification issue. |

## 8. T26-T49 acceptance reconciliation

| Row | Final evidence |
|---|---|
| T26 | Isolated to-classification non-execution yields the symmetric issue. |
| T27 | Violation plus unknown across two conditions stays incomplete and does not reuse a partial negative conclusion. |
| T28 | A to-only incomplete condition remains incomplete with no conclusion. |
| T29 | Omission of a required alignment, including a two-condition omission, is the sole typed input error. |
| T30 | Duplicate alignment rows reject typed. |
| T31 | An extra unmatched alignment row rejects typed. |
| T32 | Reversed alignment order rejects deterministically and is never normalized/remapped. |
| T33 | A foreign full compatibility/alignment object rejects despite resembling accepted scalar coordinates. |
| T34 | Two traces carry indices to one shared compatibility row; duplicating the row rejects. |
| T35 | A lower evidence-selection refusal remains structured and prevents TA execution. |
| T36 | Missing expected fingerprint keeps completeness independent but prevents execution with the exact issue. |
| T37 | Refusal plus fingerprint-not-evaluated issues are both retained in normative order. |
| T38 | A fingerprint mismatch blocks execution without rewriting evidence completeness. |
| T39 | Coherent replacement is detected when compared with the independently retained original fingerprint. |
| T40 | Replacement of carried material and expected fingerprint together may remain structurally self-consistent; no authentication is claimed. |
| T41 | Lower incomplete alignment is retained as incomplete and prevents execution. |
| T42 | Lower not-aligned content preserves its exact reason path and prevents execution. |
| T43 | Candidate zero is the valid twin; alternate or substituted candidate inputs reject typed before derivation. |
| T44 | Occurrence-content mismatch maps to not-aligned/content mismatch and does not execute. |
| T45 | Valid different receipt times remain independent latest-per-condition selections, not a cohort. |
| T46 | Source-time-only divergence changes disclosure but not the assessment gate or conclusion. |
| T47 | Distinct/noncomparable source clock segments remain disclosure only; no cross-clock issue exists. |
| T48 | A valid pre-horizon seed role is retained while effective-time coverage alone governs completeness. |
| T49 | A post-final-fence source/model mutation does not rewrite the historical carried result; revalidation is byte-identical. |

## 9. T50-T74 acceptance reconciliation

| Row | Final evidence |
|---|---|
| T50 | Every public nesting level is attacked through plain reconstruction, construct/copy, hidden/private state, cache, cycle, and wrong union arms; all reject typed before derivation. |
| T51 | Every TA integer index/count and carried lower integer coordinate rejects booleans. |
| T52 | Equality/hash/iteration/length/repr/serialization scalar subclasses reject without caller code execution. |
| T53 | Missing, duplicate, reordered, stale, substituted, out-of-range, negative, and boolean trace/issue indices reject. |
| T54 | Mutation of every fixed and derived result partition, endpoint disclosure, trace, or relation rejects authoritative reconstruction. |
| T55 | Independently constructed nested mappings with reversed insertion order yield identical canonical private bytes. |
| T56 | Seeds 1, 7, 12,345, 2,468, and 97,531 reproduce the same receipt. |
| T57 | Reversed tuple/collection input rejects identically across subprocess hash seeds; rejection is not normalization. |
| T58 | Runtime and AST gates cover filesystem, sockets, SQLite, environment, clocks, stores, selectors, connectors, writes, forbidden imports, and reverse consumers; no access occurs. |
| T59 | Disposable TA evaluation leaves lower results and model revisions unchanged before/after. |
| T60 | Immutable lower suites, inventories, accepted hashes, and preservation receipt all pass. |
| T61 | Public names, literals, exceptions, README, and positive serialization use only bounded-support language. |
| T62 | Negative results and documentation contain no transition-occurrence, causality, safety, probability, or confidence claim. |
| T63 | Independently forged semantic coordinates and cross-request rows reject; neither coordinate is selected as authoritative. |
| T64 | A private graph with exactly 134,217,728 canonical request bytes is admitted. |
| T65 | 134,217,729 bytes reject before copy, lower access, equality, or conversion. |
| T66 | Exactly 200,000 reconstructed expanded nodes are admitted. |
| T67 | Node 200,001 rejects before lower work. |
| T68 | Root-relative nesting depth 128 is admitted. |
| T69 | Depth 129 rejects before lower work. |
| T70 | Shared acyclic subgraphs count once per reference occurrence; active-path cycles reject. |
| T71 | Distributed sibling content uses one aggregate budget with no reset/rebudget; each lower object is reconstructed once. |
| T72 | Oversize scalars, mappings, sequences, keys, bytes, unsupported containers, and deep stacks refuse incrementally before lower work. |
| T73 | All status/fixed-result arms and all 22 issue codes are independently reachable; multi-issue order is exact. |
| T74 | Exact built-in finite floats round-trip deterministically in real lower material; subclasses, NaN, infinities, and invalid positions reject before derivation. |

All T01–T74 rows are therefore closed with permanent executable evidence.

## 10. Complete issue reachability and order

The T73 truth/reachability test constructs valid disposable worlds that reach
all 22 issue literals in their normative order:

1. `transition_anchor_mismatch`
2. `transition_not_registered`
3. `transition_not_declared`
4. `transition_conflicted`
5. `transition_inactive`
6. `context_mismatch`
7. `model_revision_mismatch`
8. `from_state_anchor_mismatch`
9. `to_state_anchor_mismatch`
10. `endpoint_subject_mismatch`
11. `endpoint_pin_not_exact_current`
12. `endpoint_classification_cutoff_mismatch`
13. `cutoffs_equal`
14. `cutoffs_reversed`
15. `endpoint_classification_not_executed`
16. `endpoint_classification_incomplete`
17. `governing_selection_refused`
18. `governing_expected_fingerprint_not_supplied`
19. `governing_expected_fingerprint_not_evaluated`
20. `governing_expected_fingerprint_mismatched`
21. `governing_occurrence_not_aligned`
22. `governing_evidence_incomplete`

The same test proves exact multi-issue retention and ordering. Status
precedence does not hide independently applicable diagnostics. Malformed
structure remains a typed input error and is not converted into a structured
domain issue.

## 11. Public surface and contract pin

`backend.transition_assessment.__all__` remains exactly 28 names, in order:

1. `TransitionAssessmentError`
2. `TransitionAssessmentInputError`
3. `TransitionAssessmentInputErrorCode`
4. `TransitionAssessmentEndpointRole`
5. `TransitionAssessmentDeclarationAdmission`
6. `TransitionAssessmentContextRelation`
7. `TransitionAssessmentModelRevisionRelation`
8. `TransitionAssessmentCutoffRelation`
9. `TransitionAssessmentEndpointRelation`
10. `TransitionAssessmentSubjectRelation`
11. `TransitionAssessmentObservationPresence`
12. `TransitionAssessmentAlignmentRelation`
13. `TransitionAssessmentExpectedFingerprintRelation`
14. `TransitionAssessmentEvidenceCompleteness`
15. `TransitionAssessmentSourceTimeUse`
16. `TransitionAssessmentTemporalCohort`
17. `TransitionAssessmentContinuity`
18. `TransitionAssessmentExecution`
19. `TransitionAssessmentConclusion`
20. `TransitionAssessmentIssueCode`
21. `TransitionAssessmentPolicy`
22. `TransitionAssessmentLimits`
23. `DeclaredTransitionAssessmentRequest`
24. `TransitionAssessmentIssue`
25. `TransitionAssessmentConditionTrace`
26. `TransitionAssessmentEndpointDisclosure`
27. `DeclaredTransitionAssessmentResult`
28. `assess_declared_transition_endpoints`

No alias, alternate public entry point, facade, or consumer was added.
Field/literal order, strict types, fixed values, carry-once rules, and the sole
`TRANSITION_ASSESSMENT_INPUT_INVALID` typed error code remain pinned by the
public-contract gate.

## 12. Limit and scheduling evidence

Permanent production-number tests establish the accepted limits rather than
only testing reduced injectable values:

- canonical request bytes: 134,217,728 admitted; 134,217,729 refused;
- reconstructed expanded graph nodes: 200,000 admitted; 200,001 refused;
- root-relative nesting depth: 128 admitted; 129 refused.

The tests use bounded generated structures and instrumentation to show that
plus-one refusal happens before lower reconstruction, equality, hostile
conversion, or expensive retained allocation. An active-path cycle refuses;
a shared acyclic subgraph is expanded and charged per occurrence. Aggregate
sibling content cannot evade the byte budget, and no nested boundary resets or
re-budgets the graph.

A 129-alignment attack refuses before any lower reconstruction. Valid result
reconstruction visits the carried request under one aggregate budget and
performs exactly two state-classification and two evidence-alignment lower
derivations—one for each carried endpoint/alignment—not repeated speculative
work.

## 13. Hostile reconstruction and purity

The hostile matrix covers every public boundary using serialized values,
exact trusted instances, `model_construct`, `model_copy`, subclasses, hidden
extras, private attributes, wrong union arms, cycles, stale derived values,
wrong indices, and cross-request substitution. Result validation derives only
from what the compact result carries. It does not claim authentication of
uncarried lower bytes.

All invalid inputs surface the one bounded typed TA input exception. Its code
and message are reconstructed from accepted built-ins, and raw cause/context
is cleared. Tests prove that absolute paths, URI credentials, secret-like
content, and hostile object representations do not leak.

Runtime spies and static import checks prove no filesystem read/write, socket,
SQLite, connector, store query, environment lookup, ambient clock, selector,
or lower mutation. No reverse production consumer imports TA. The function is
a pure sibling composition over supplied public lower results and the public
model query seam.

## 14. Deterministic serialization receipt

Across the working tree and both fresh clean checkouts, including subprocesses
with `PYTHONHASHSEED=1`, `7`, `12345`, `2468`, and `97531`, the same valid-case
private canonical result was reproduced:

- UTF-8 byte count: `195429`;
- SHA-256: `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`;
- trailing newline: `False`.

Equivalent-offset datetimes normalize to the same UTC content. Recursive
mapping insertion order does not affect bytes. Valid float representatives
`0.0`, `-0.0`, `1794.0`, `1.25`, `1e-20`, and `1e20` are deterministic JSON
numbers. Reversed ordered collections reject instead of being normalized.

Both accepted lower deterministic reproductions also remain exact in each
fresh checkout:

- original lower material: 24,766 bytes, SHA-256
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
- seed-aware lower material: 11,528 bytes, SHA-256
  `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

## 15. Focused and affected verification

The final focused command was equivalent to:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/transition_assessment -q
```

Result: **120 passed in 394.06 seconds**.

The final architecture/status selection covered TA public contracts and
isolation plus model-kernel transition architecture, evidence-alignment
isolation, and state-classification architecture. Result: **32 passed in
20.95 seconds**.

Before the final production repair, the explicit affected gate spanning
model-kernel, state-classification, evidence-alignment, evidence-assurance,
temporal-state, and model-state was **2,092 passed in 813.85 seconds**. Every
one of those packages was then covered again after the final production
change by the final working full-repository run and both clean-checkout full
runs.

The final independent backend re-review at production commit `2028bcd` ran
the final-review, preflight, and revalidation selection: **62 passed in 142.56
seconds**. It verified fresh invocation-local limits, exact union arms, no raw
exception chains, and exactly two state plus two alignment reconstructions.

## 16. Working full-repository verification

At exact tested implementation `2ec18f7234273dba98098d268df4568d5cc84d85`,
the uninterrupted all-extras working repository run was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q
```

Result: **3,800 passed in 1,424.70 seconds**. No test was skipped and no
loopback setup error occurred in the working column; no reconciliation rerun
was needed.

This final run followed the last runtime and behavioral-test change and covers
all focused, affected, architecture, optional-feature, and preservation tests
present in the repository.

## 17. Fresh base-only clean checkout

A separate detached worktree at exact implementation
`2ec18f7234273dba98098d268df4568d5cc84d85` used a fresh base-only virtual
environment installed from repository requirements.

Its full repository result was **3,764 passed, 35 skipped, 1 error in 1,137.20
seconds**. The sole error was the known sandbox denial while the real-loopback
transport test attempted to create its local listener. The exact test was then
rerun under the separately permitted loopback setup and was **1 passed in 0.71
seconds**. The reconciled base column is therefore **3,765 runnable tests
passed, 35 optional-extra skips, zero product failures**.

The detached checkout remained at the exact implementation and clean after
the run. Its dependency check reported no broken requirements; backend
compilation succeeded; its TA deterministic receipt and both lower receipts
matched Section 14.

## 18. Fresh all-extras clean checkout and CAD/STEP/PDF

A second separate detached worktree at exact implementation
`2ec18f7234273dba98098d268df4568d5cc84d85` used a fresh all-extras virtual
environment. The first combined install attempt exposed pip option leakage:
the hashed optional requirements caused the unpinned base requirements to be
treated as hash-required. No package or test ran under that failed setup. The
environment was rebuilt using the repository's intended sequence—base/dev,
then CAD, then PDF—and all installations succeeded.

Its full repository result was **3,799 passed, 1 error in 1,153.65 seconds**.
Again, the sole error was the sandbox-denied local loopback listener. The exact
separately permitted rerun was **1 passed in 0.70 seconds**, reconciling the
column to **all 3,800 tests passed, zero skips, zero product failures**.

Explicit CAD/STEP/PDF coverage in that environment was **120 passed in 41.06
seconds**. The checkout stayed detached at the exact tested implementation
and clean. `pip check`, backend compilation, the TA receipt, and both lower
deterministic reproductions passed independently.

## 19. Compilation, dependencies, whitespace, and repository state

Working, fresh base, and fresh all-extras environments each reported:

- `pip check`: `No broken requirements found.`;
- backend compilation, including `backend/transition_assessment`: exit 0 with
  no errors;
- deterministic receipt checks: exact match.

Before creating this report, all of these whitespace checks returned no
errors:

- working tracked tree: `git diff --check`;
- Slice B range: `git diff --check b9e506fe918fee860707cd57e08502e62194c3dc..HEAD`;
- complete TA milestone range: `git diff --check a4754d8..HEAD`.

The tracked working tree was clean before this report. After report creation,
the intended status is exactly the untracked completion report and no other
entry. The ignored `.claude/settings.local.json` remains byte-identical at
SHA-256 `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 20. Preservation inventory

The final working and clean-checkout receipts preserve:

- exactly 36 authoritative model records;
- model revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- authoritative ledger aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FRG/FLD/FLW membership counts `1/1/0`;
- TRG/TRD/TRW membership counts `0/0/0`;
- the FL disclosure at 660,516 bytes and SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- both accepted lower deterministic receipts in Section 14; and
- historical records, memberships, fixtures, evidence, and accepted artifacts.

TA evaluation against disposable test worlds did not append model records,
change lower results, or create a result artifact. The valid-case TA snapshot
digest is unchanged at the value in Section 14.

## 21. Independent adversarial review

Three bounded independent reviews were completed:

- architecture/import review found no public-surface or dependency-boundary
  defect; its focused public/isolation/determinism gate was 16 passed;
- coverage review identified missing direct witnesses, which were added as
  green tests through T01–T74 without changing production behavior;
- backend integrity review found the five final reconstruction defects listed
  in Section 5 and drove the subsequent union-arm follow-ups. Its re-review of
  final production commit `2028bcdd138ba5f01ac8972bac8093841b6de1d5`
  found no remaining production defect in scope.

Every genuine review defect was first encoded as a failing permanent test.
Review did not reopen architecture, change a lower contract, or add a new
public name.

## 22. Limitations and exact claims

TA-001 assesses whether bounded, supplied, validated evidence supports the
declared endpoint pattern at ordered cutoffs. It does not assert that a
transition occurred or did not occur. It does not establish continuity,
causality, freshness, semantic truth, safety, confidence, probability,
physical occurrence, or global/current evidence.

Pure reconstruction can establish internal structural and derivational
consistency only for carried content. A coherent replacement of content and
its expected fingerprint can remain self-consistent; authentication requires
an independently retained expected fingerprint and is still not a signature
or authority endorsement. Post-fence store changes are outside the carried
historical result and are not reread by TA.

No unresolved implementation or contract discrepancy remains. The only open
owner decision is whether to accept final TA-001 at exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`.

## 23. Completion artifact

This report is the sole intended uncommitted file. Its final receipt records
the measured line count, UTF-8 byte count, SHA-256 digest, contiguous section
count, ending marker, final whitespace checks, and exact Git status after the
file is written.

END OF TA-001 SLICE B COMPLETION REPORT
