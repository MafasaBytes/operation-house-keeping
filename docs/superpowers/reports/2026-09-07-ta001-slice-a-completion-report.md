# TA-001 Slice A Completion Report

Date: 2026-09-07

Status: corrected Slice A implementation complete and awaiting owner
validation; Slice B unauthorized

## 1. Authority and checkpoint

Work was performed on branch `ta001` from the owner-accepted discrepancy stop
`47a747ad9df020d631318b09f24a0d2a2c39fc6a`. The accepted Slice A base remains
`a4754d8659c08af8fb86bf18bd3c5aac4ea355fe`.

The owner authorized two bounded contract resolutions before Slice A resumed:

1. admit only exact built-in finite floats during schema-independent TA
   preflight, preserve them as numbers, and encode them with the deterministic
   `float.__repr__` JSON token; and
2. correct T43 so a forged alternate candidate index is typed malformed input,
   while candidate zero remains the valid twin.

The normative corrected synthesis is
`docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`
at SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`.
The historical pre-correction digest
`99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062`
remains recorded and was not rewritten.

## 2. Contract-correction record

The documentation-only correction commit is
`c2adc46853fdd0e088ef6d211d4f4c4604d8fd5e`. It amended only the corrected
synthesis and implementation plan and added:

`docs/superpowers/reports/2026-09-07-ta001-slice-a-contract-correction-and-owner-resolution.md`.

That report remains exactly 163 lines and 7,884 UTF-8 bytes at SHA-256
`10605da5dd2a104db2daf883f1bb19d5276ede996af6a6e225ce1934848cb5ff`.
Its eight numbered sections are contiguous and its final line remains exactly
`END OF TA-001 SLICE A CONTRACT CORRECTION AND OWNER RESOLUTION`.

The accepted historical discrepancy report remains byte-identical at SHA-256
`857ceb224b9fd15799276ccaa94d88042fc3876b1ce740e01f6a407916877f64`.
The corrected plan is at SHA-256
`da9e426d52348203bed716bcc7d11d4deb2dde7d8d303c7a4e98392b1ec9d0a8`.

## 3. Exact implementation checkpoint

The last runtime or behavioral-test change is exact commit
`76738ac0d098eb59b0fec4f6970aa862528647d9`. The later final HEAD
`b9e506fe918fee860707cd57e08502e62194c3dc` changes package and project status
documentation only. All full-suite clean checkouts were detached at the exact
implementation commit.

The implementation creates only the pure sibling leaf package
`backend.transition_assessment`. It consumes public carried contracts from
`backend.model_kernel`, `backend.state_classification`, and
`backend.evidence_alignment`, plus Pydantic and the standard library. No lower
production package changed.

## 4. Commit sequence

The forward-only commit sequence after the accepted discrepancy stop is:

| Commit | Subject | Purpose |
| --- | --- | --- |
| `c2adc46853fdd0e088ef6d211d4f4c4604d8fd5e` | `docs: correct TA-001 Slice A admission contract` | owner-resolved R1/R2 contract correction |
| `7d7290aa70803a1a34bcf043eb6beae6bdbcb081` | `test: define TA-001 Slice A admission contracts` | initial red public/preflight contract evidence |
| `d84e8eb5834ebe82814c60cfc7037c1bf7cf9b7a` | `feat: add TA-001 contracts and bounded preflight` | exact public models, limits, preflight, canonical support |
| `0f7494c32d750c6e768f418559929100861d8de2` | `test: define TA-001 endpoint assessment joins` | red disposable public join worlds |
| `a8de2d99a87784bd8fa0633d5dc64f1f028e3e05` | `feat: derive TA-001 endpoint pattern assessments` | pure join, disclosures, issues, gate, conclusion |
| `3f3d9b92e0e155b9c884b7af5303dc637def7f8a` | `test: harden TA-001 reconstruction and isolation` | hostile reconstruction, determinism, purity tests |
| `62c7afe772fa4ad8971bcc586b4548d330875a25` | `fix: reject forged TA-001 nested material` | private-material binding repair |
| `c9c34d80f5ac13cb7a256148215a58913c12d326` | `test: capture TA-001 adversarial review defects` | eight permanent failing review reproductions |
| `4cc161c9a3e2cb82192e6eb1acd05745ab16d4ea` | `test: strengthen TA-001 boundary proofs` | T43-before-derivation, canonical-pass, nested-order proofs |
| `a5f261218f19fcc4763640ec63e06b06e0a9fc8a` | `test: pin TA-001 root depth boundary` | root-depth-zero red twin |
| `240aff57607b7ed414aef32130d068bd896ced9d` | `fix: harden TA-001 bounded reconstruction` | all review repairs and streaming boundedness |
| `76738ac0d098eb59b0fec4f6970aa862528647d9` | `test: reconcile TA-001 import direction` | authorized upper-consumer architecture assertions |
| `b9e506fe918fee860707cd57e08502e62194c3dc` | `docs: describe TA-001 Slice A boundary` | package README and current-status reconciliation |

No commit was amended, reordered, squashed, rebased, reset, or otherwise
rewritten.

## 5. Changed files

Production files added:

- `backend/transition_assessment/__init__.py`;
- `backend/transition_assessment/contracts.py`;
- `backend/transition_assessment/preflight.py`; and
- `backend/transition_assessment/derivation.py`.

Focused test files added:

- `tests/transition_assessment/helpers.py`;
- `tests/transition_assessment/test_public_contracts.py`;
- `tests/transition_assessment/test_preflight.py`;
- `tests/transition_assessment/test_derivation.py`;
- `tests/transition_assessment/test_revalidation.py`;
- `tests/transition_assessment/test_isolation.py`; and
- `tests/transition_assessment/test_determinism.py`.

Three stale lower architecture assertions were narrowed to admit only the new
authorized upper leaf:

- `tests/model_kernel/test_transition_architecture.py`;
- `tests/evidence_alignment/test_isolation.py`; and
- `tests/evidence_alignment/test_c2_public_surface.py`.

Documentation changes are the corrected synthesis and plan, the resolution
report, `backend/transition_assessment/README.md`, and narrowly reconciled
status wording in `CLAUDE.md`, `README.md`, the evidence-alignment README, and
ADR-0020. The completion report is intentionally uncommitted.

## 6. Exact public surface

`backend.transition_assessment.__all__` is ordered, unique, and contains
exactly these 28 names:

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

Tests pin every model field in normative order, every literal in normative
order, all 22 issue codes, frozen/extra/revalidation policy, strict indices,
the sole typed input error, the exact operation signature, and the absence of
alternate public names.

## 7. Structural admission and deterministic floats

The request boundary performs these TA-owned stages in order:

1. exact ordinary mapping or allowlisted nominal public-model admission;
2. iterative active-path traversal;
3. aggregate node, depth, scalar, fixed-cardinality, and preliminary canonical
   byte admission;
4. one ordinary graph copy only after admission;
5. a streaming canonical counter/encoder agreement pass;
6. nominal reconstruction through every exact lower public model;
7. exact serialized-shape comparison, allowing only documented UTC
   normalization and ordinary list/tuple serialized-sequence equivalence; and
8. index, equality, fingerprint-relation, issue, and conclusion derivation.

Exact model-type identity prevents a caller from spoofing a `backend.*`
module name. Public model fields are read from validated stored dictionaries
without caller attribute dispatch. A substituted lower private material
binding rejects.

Exact built-in finite floats are admitted and retained only where nominal
lower schemas also retain a float. `0.0`, `-0.0`, `1794.0`, `1.25`, `1e-20`,
and `1e+20` produce exact deterministic JSON number tokens. Float subclasses,
NaN, positive infinity, and negative infinity reject. The permanent
`observation_count` attack proves that a schema-invalid `0.0` is not coerced
to integer zero.

## 8. Limits and hostile boundedness

The public fixed limits are exactly:

- canonical request: 134,217,728 bytes;
- reconstructed graph: 200,000 expanded occurrence nodes; and
- root-relative nesting depth: 128.

The production-number probe admitted an exact 134,217,728-byte string graph,
an exact 200,000-node expanded list graph, and an exact depth-128 graph. Their
byte-, node-, and depth-plus-one twins each refused with the corresponding
typed lower preflight condition. Root depth zero is accepted.

Private injected-limit tests separately prove inexpensive exact/plus-one
boundaries, shared acyclic occurrence expansion, cycle refusal, non-string key
refusal, boolean-index refusal, and exact UTF-8 counting. A huge string with
an invalid far suffix refuses as soon as the byte budget is crossed; a mapping
whose minimum child nodes exceed the budget refuses before scanning a later
hostile key. Known 129-alignment input refuses before any lower alignment
validator is called.

## 9. Pure join and conclusion behavior

For every endpoint condition, TA resolves the exact classification constraint
evaluation, classification candidate, semantic candidate coordinate, separate
value candidate coordinate, complete carried compatibility, governing bound
occurrence, and exact alignment row. Distinct equal complete compatibilities
are carried once in first-governing-trace order.

Execution requires declaration admission, ordered cutoffs, complete endpoint
classification, complete aligned evidence, and an independently supplied
expected fingerprint whose lower relation is `matched` for every governing
observed condition. Completeness is derived independently of fingerprint
state. An incomplete classification now produces
`incomplete_within_one_or_more_declared_horizons`; only not-evaluated
classification coverage or refused selection produces aggregate
`not_evaluated`.

The positive conclusion is bounded support for the declared endpoint pattern.
The negative conclusion is bounded non-support for that pattern. Neither is an
occurrence or non-occurrence claim. Equal or reversed cutoffs never execute.
Without an effective transition body, endpoint anchor and subject relations
are `not_evaluated` rather than inferred from registration coincidence.

## 10. Authoritative result reconstruction

`DeclaredTransitionAssessmentResult.model_validate(...)` reconstructs and
budgets its carried request exactly once, then validates only the compact
derived fields against their fixed shapes and cardinalities. It does not apply
the request budget to a second copy of the complete result graph.

Every top-level result partition is rederived. Endpoint disclosures, traces,
strict coordinates, issue tuples, fixed limits, execution, and conclusion are
authoritative. Missing, duplicated, reordered, stale, substituted, boolean,
out-of-range, divergent semantic/value-coordinate, hidden, extra, wrong-union,
or forged content rejects without I/O. The result repeats neither complete
lower material nor any raw payload.

## 11. Red-before and fixed-after evidence

The recorded red/green sequence is:

| Stage | Red-before | Fixed-after |
| --- | --- | --- |
| public contracts, R1 floats, T43 preflight group | 20 failed because the package did not exist | 20 passed after contracts/preflight implementation |
| endpoint derivation group | 5 failed, 2 passed before derivation | 7 passed after pure derivation |
| forged lower private-material binding | 1 failed because substitution was accepted | targeted 21 passed after identity binding check |
| first complete green | n/a | 47 passed |
| independent architecture/preflight review | 8/8 permanent probes failed | 8/8 passed after bounded repairs |
| root-depth-zero twin | 1 failed as configuration-invalid | 1 passed after root-relative depth correction |
| final focused gate | n/a | 57 passed in 169.62 seconds |

Corrected T43 has a valid candidate-zero twin that executes. Candidate one
fails nominal lower reconstruction, maps to
`TRANSITION_ASSESSMENT_INPUT_INVALID`, and a spy proves TA derivation is never
entered. R1's accepted lower world carries the six finite staleness values
unchanged as floats; hostile and schema-invalid twins refuse before derivation.

## 12. Independent adversarial review and repairs

Three bounded independent reviews were performed after first green: an
architecture/join review, a hostile preflight review, and a contract/test
review. Their overlapping concrete findings were consolidated into these
permanent repair groups:

1. schema-invalid integral floats could be coerced in lower integer fields;
2. 129 alignments reached lower validation before fixed-cardinality refusal;
3. a caller-spoofed Pydantic subclass could dispatch hostile attribute code;
4. huge strings and mappings were scanned beyond an already crossed budget;
5. result reconstruction charged compact derived fields against the request
   budget;
6. incomplete classification was incorrectly collapsed to not evaluated;
7. subject equality was overclaimed when no effective transition body existed;
8. request reconstruction repeated TA plain-copy work and omitted the required
   canonical counter agreement pass; and
9. root depth zero was rejected by the private boundary configuration.

Each genuine defect was reproduced by a failing test before its production
repair. Final review confirmed the approved import direction, pure carried
join, deterministic float tokens, shared-DAG occurrence counting, and bounded
endpoint-pattern language.

## 13. Corrected acceptance matrix T01-T18

| Rows | Evidence |
| --- | --- |
| T01 | disposable complete/matched public world executes exact bounded support |
| T02-T03 | complete non-match world executes bounded non-support; from/to endpoint branches share the same symmetric gate and are exercised by lower classification worlds |
| T04-T08 | accepted model-kernel transition lifecycle suite constructs unregistered, not-declared, same-root/cross-root conflicted, and inactive public results; TA lifecycle mapping and normative issue vocabulary are pinned |
| T09-T11 | accepted model-kernel/state-classification suites preserve superseded/withdrawn pins and conflicted/inactive states; TA admits only exact-current endpoints and executed complete classifications |
| T12-T18 | authoritative nested reconstruction plus exact anchor, state, subject, context, and complete-object checks prevent substitution; no effective-body subject disclosure has a direct repaired test |

All lifecycle and relation failures remain structured results when the lower
objects themselves are valid. Malformed or forged lower objects remain typed
input rejection.

## 14. Corrected acceptance matrix T19-T40

| Rows | Evidence |
| --- | --- |
| T19-T21 | equal cutoffs are structured non-execution; ordered cutoffs execute; equivalent aware offsets normalize to byte-identical results; reversed branch is pinned by the exact literal/derivation table |
| T22-T24 | strict datetime, cutoff equality, complete model-revision equality, and hostile reconstruction are enforced before derivation |
| T25-T28 | incomplete/not-evaluated endpoint classification gates remain separate; direct absent-observation world proves incomplete aggregate behavior |
| T29-T34 | missing/reordered collections reject directly; cardinality, exact length/order/complete-object equality, unique correspondence, and carry-once indices reject duplicate, extra, substituted, or repeated rows |
| T35-T40 | accepted EA/alignment suites cover refused selection, omitted/not-evaluated/mismatched expectation, original-expectation replacement detection, and coherent replacement limitations; TA directly proves omitted expectation blocks without rewriting completeness |

The complete affected EA, alignment, classification, and model-kernel suites
were rerun together after architecture reconciliation, not assumed from prior
milestone reports.

## 15. Corrected acceptance matrix T41-T57

| Rows | Evidence |
| --- | --- |
| T41-T42 | accepted alignment incomplete/not-aligned valid worlds feed the exact status and coverage mapping; both block TA execution without changing lower meaning |
| T43 | direct candidate-zero valid twin and candidate-one typed-malformed attack; derivation call count remains zero for the attack |
| T44 | accepted evidence-alignment altered-content test preserves complete occurrence equality rather than ID-only alignment |
| T45-T49 | carried receipt/source-time/clock/seed roles remain disclosures; TA performs no selection, clock comparison, or post-fence read and always discloses independent non-cohort semantics |
| T50-T54 | direct model-construct/copy, hidden/private, cycle, hostile string, boolean index, stale trace/issue, and forged derived-partition reconstruction attacks reject |
| T55-T56 | recursively reversed mappings, equivalent offsets, independent roots, and hash seeds 1/7/12345 produce byte-identical canonical results |
| T57 | reversed exact alignment order rejects and is never silently remapped |

## 16. Corrected acceptance matrix T58-T74

| Rows | Evidence |
| --- | --- |
| T58 | runtime filesystem, socket, and SQLite hooks fail closed while valid assessment/result validation still pass; AST isolation bans connector/store/environment/clock/write paths |
| T59-T60 | full historical replay and immutable preservation suites pass; direct hashes and record-family counts are reported below |
| T61-T62 | public names, result literals, package README, and positive/negative conclusions contain only bounded pattern support/non-support language |
| T63 | independent trace-coordinate forgery rejects during authoritative result reconstruction |
| T64-T65 | production-number 134,217,728-byte exact twin admits and byte 134,217,729 refuses; injected exact twins also pass |
| T66-T67 | production-number 200,000-node exact twin admits and node 200,001 refuses |
| T68-T69 | production-number depth-128 exact twin admits and depth 129 refuses; root depth zero admits |
| T70 | shared acyclic subtree counts per occurrence; over-limit sharing and a direct cycle refuse |
| T71 | instrumentation proves one aggregate request budget, one full TA plain copy, one canonical agreement pass, and no outer-result rebudgeting |
| T72 | huge scalar and mapping tests prove incremental refusal before invalid suffix/key or lower validation; ordinary sequence node lower bound is O(1) |
| T73 | exact public literal and all 22 issue vocabularies are enumerated in normative order; lower lifecycle/status suites plus TA structured worlds cover the corresponding valid arms and multi-issue retention rules |
| T74 | exact finite tokens, lower carried floats, subclass/non-finite attacks, and non-float-field substitution are directly tested |

No acceptance row authorizes a physical occurrence assertion, store read, lower
migration, demonstration, or Slice B surface.

## 17. Focused, affected, and architecture verification

At the final source state:

- complete `tests/transition_assessment`: 57 passed in 169.62 seconds;
- complete model-kernel, state-classification, evidence-alignment,
  evidence-assurance, EA Slice A architecture, and behavior architecture:
  1,905 passed in 526.10 seconds; and
- dedicated TA/model-kernel/evidence-alignment/EA/behavior/state-classification
  architecture and isolation gate: 39 passed in 41.73 seconds.

The applicable documentation/status gate passed 26 tests before the durable
documentation commit and passed 26 tests again afterward, with the final run
completing in 2.05 seconds.

## 18. Full and clean-checkout verification

The working all-extras environment ran:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`

It completed uninterrupted with 3,737 passed in 1,451.81 seconds (24:11). The
loopback test passed inside this column; there was no skip, error, or separate
reconciliation.

A fresh detached base-only checkout at exact implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9` installed `requirements.txt` and
`requirements-dev.txt`. Its aggregate suite produced 3,701 passed, 35 expected
optional-extra skips, and one sandbox-denied loopback setup error in 931.76
seconds. The exact loopback test was separately rerun with permission at the
same commit and passed 1 test in 0.74 seconds. This reconciles 3,702 runnable
tests plus 35 expected skips; it is explicitly not described as one
uninterrupted aggregate pass.

A separate fresh detached all-extras checkout at that same exact commit
installed base/dev requirements plus both hash-pinned `requirements-cad.txt`
and `requirements-pdf.txt`. Its aggregate suite produced 3,736 passed and the
same single sandbox-denied loopback setup error in 977.33 seconds. The exact
permitted rerun passed 1 test in 0.74 seconds, reconciling all 3,737 tests with
the same split accounting.

The all-extras checkout separately ran the explicit PDF ingestion, STEP
ingestion, PDF contract/coordinate/detection/extractor, STEP extractor, and
structural STEP-claim files: 120 passed in 39.65 seconds. Both disposable
worktrees were clean and were removed after verification.

## 19. Dependencies, compilation, and determinism

Working, fresh base-only, and fresh all-extras `pip check` each returned
`No broken requirements found`. Backend plus focused TA test compilation used
an external `PYTHONPYCACHEPREFIX` in all three environments and exited zero
without output.

Independent disposable canonical-result reproductions under working hash seeds
`1`, `7`, and `12345`, fresh base seed `2468`, and fresh all-extras seed `97531`
all produced exactly:

- 195,429 bytes; and
- SHA-256
  `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.

The bytes have no final newline and are private verification evidence only.
They create no public fingerprint, identity, record, receipt, or artifact.

Both clean columns also independently reproduced both accepted lower-material
serializations:

- original in-horizon material: 24,766 bytes, SHA-256
  `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`;
  source shape `10/2/2`, temporal shape `2/2`; and
- corrected seed-aware token plus source material: 11,528 bytes, SHA-256
  `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

No expected deterministic bytes changed.

## 20. Preservation, scope, and owner gate

Direct verification and the full immutable suites confirm:

- exactly 36 authoritative model records;
- model revision
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`;
- ledger aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure exactly 660,516 bytes at SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- historical model memberships, accepted evidence, fixtures, lower artifacts,
  and revisions unchanged; and
- `.claude/settings.local.json` unchanged at SHA-256
  `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

Working-tree, full Slice A range from
`a4754d8659c08af8fb86bf18bd3c5aac4ea355fe`, and correction range from
`47a747ad9df020d631318b09f24a0d2a2c39fc6a` whitespace checks all passed
without output before this report. Both clean checkout whitespace checks and
statuses were empty. This report will receive its own untracked whitespace and
ending-marker checks after writing.

Scope is exactly the owner-resolved documentation correction plus TA-001 Slice
A contracts, bounded pure derivation, authoritative reconstruction, tests, and
documentation. There is no facade, demo, fixture append, ledger mutation,
persistence, identity, lower migration, transition occurrence/non-occurrence,
Slice B implementation, push, or merge. Slice B remains unauthorized.

The next gate is owner validation of corrected TA-001 Slice A at exact tested
implementation `76738ac0d098eb59b0fec4f6970aa862528647d9`. No Slice B work may
start without a separate owner decision.

END OF TA-001 SLICE A COMPLETION REPORT
