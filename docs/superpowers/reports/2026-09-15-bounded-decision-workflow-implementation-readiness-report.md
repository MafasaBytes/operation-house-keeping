# Bounded decision-workflow implementation readiness report

## 1. Verdict and scope

**Verdict: READY FOR OWNER REVIEW; NOT YET AUTHORIZED OR ENVIRONMENT-COMPLETE
FOR PRODUCTION IMPLEMENTATION.**

The approved semantic design has been converted into an exact preparation package,
diagnostic policy, measured candidate resource policy, filesystem evidence and
seven reviewable implementation slices. No production application or test was
created, and no command-level acceptance case has been run. Preparation does not
count as delivery.

Three matters remain at the implementation-authorization gate:

1. owner approval of the proposed numeric limits;
2. owner approval of the exact dependency versions plus authorization to obtain
   hash-identified installation artifacts; and
3. nomination of persistent writable local ext4/XFS paths for runtime input and
   result retention.

These are resource, supply and platform decisions. No changed semantic premise was
found.

## 2. Verified baseline and frozen inputs

Read-only inspection confirmed:

- branch brc-exp001;
- HEAD ec027add0cb2dae5434c42f67454752eb93f7228;
- clean tracked and staged state before preparation;
- approved [corrected design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
  SHA-256
  54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab;
- frozen [independent review](2026-09-15-bounded-decision-workflow-delivery-independent-review.md)
  SHA-256
  2bc917bee36a4e0db9b8b07b5a650455f98008e7d286a482c1127bdb8a7ddf29;
  and
- every pre-existing untracked artifact was inventoried by path and SHA-256 before
  writing the four authorized files.

The [implementation plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
defines the proposed sequence. The canonical compact
[candidate package](2026-09-15-bounded-decision-workflow-candidate-package.json)
has SHA-256
0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365.
The canonical compact
[candidate manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json)
has SHA-256
6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959.
Both JSON files are sorted-key UTF-8 without a trailing newline.

## 3. Prepared application and authority boundary

The retained invocation is:

    python -m applications.bounded_decision_workflow

The application remains a local, maintained composition layer. It will import
public StateClassificationResult and parse_observed_decimal contracts, and will not
open backend stores or call private backend helpers. No backend extension is
justified.

The package keeps three input classes distinct:

- request structure and selected public-result commitment;
- caller-owned synthetic effects, equations, bounds, applicability, target and
  cost/feasibility policy; and
- one nominated observation admitted only from a reconstructed public result.

The complete baseline snapshot was generated through the public acquisition,
temporal projection, identity binding, semantic compatibility, constraint
evaluation and state-classification chain. Its synthetic source value was changed
in memory to 40 before acquisition. Public reconstruction succeeded and the public
decimal parser returned admitted 40. The snapshot commitment is
782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f.

A second public-facade snapshot was produced with no temporal evidence. It
reconstructs coherently with unavailable condition outcomes and has commitment
72c057d8707f4904cf2dfb658937a4610c56b364217ec073239530756f128ea6.
Recipes for unattached, inconsistent, nonnumeric and semantic/unit-incompatible
twins name the exact source construction change and require the same public facade
chain during implementation tests. Caller numbers never repair those conditions.

These synthetic snapshots test carried-result integrity and application admission.
They do not authenticate unavailable source bytes, equipment, acquisition or
physical truth.

## 4. Complete forms and expected reasoning

The package freezes:

- the ten REQUEST.json top-level fields and every nested premise/policy envelope;
- exact integer numerator/positive denominator rational representation;
- exact observed candidate indices, subject, variable, constraint, context, cutoff,
  revision, quantity, observation-role and unit joins;
- the fixed affine equation, two hypotheses, four actions and closed Cartesian hard
  support;
- total target, feasibility and selection precedence, including plural ties;
- the nine result sections and three trace fields;
- evaluate, verify and replay arguments;
- fixed complete and refusal bundle filenames;
- stdout/stderr roles and exits 0, 2, 3, 4, 5, 6 and 7;
- 42 exact diagnostic codes with stage, target, message key, retry class, bundle
  state and precedence; and
- replay identity and exact release-one compatibility.

requested_limits=null explicitly selects immutable build limits. If an object is
provided, every dimension is required and may only tighten the build policy.
Input content cannot raise a ceiling.

The independent preparation oracle uses standard-library Fraction and exhaustive
corner enumeration; a separately implemented Decimal/set audit checked 44 rows and
relations against the retained results. Neither calls a future runtime. Both share
the approved premises and have same-author provenance.

The baseline expected values are:

| Hypothesis | a0 | aF | aH | aHF |
| --- | ---: | ---: | ---: | ---: |
| H_H | 42 | 42 | 32 | 32 |
| H_F | 36 | 32 | 36 | 32 |

With target [31,33], retained {H_H} and costs a0=0, aF=3, aH=2, aHF=5,
the expected selection is {aH} at cost 2. Beta [1/10,3/10] gives
H_H/aH=[30,34]. Cost-only and target-only changes leave all eight raw rows
unchanged. These are conditional synthetic expectations, not execution findings
or empirical predictions.

## 5. Exact acceptance coverage

There are exactly 27 acceptance IDs and 68 materializable variants. Each package
row carries complete command arguments or producer/fault setup, exact request and
snapshot object references, an independently specified complete result/trace or
diagnostic, and one implementation slice:

| ID | Prepared result boundary | Slice |
| --- | --- | --- |
| CMD-1 | Full useful command, seven files, admitted observation and selected action | S6 |
| CMD-2 | All process classes: usage, refusal, unavailable, no-feasible, collision, retention | S6 |
| OBS-1 | Positive public-result admission | S1 |
| OBS-2 | Five coherent unavailable forms with public-producer twins | S1 |
| OBS-3 | Eight exact substitution/forgery mutations and refusal points | S1 |
| OBS-4 | Conversion refusal and interpreted source-lexeme success | S1 |
| NUM-1 | Exact endpoint plus float, reversal, correlation and digit attacks | S2 |
| UNC-1 | Widened complete hard support | S2 |
| UNC-2 | Missing/unknown support and stale refusal | S2 |
| POL-1 | Mixed unknown/incompatible and explicit-false precedence | S3 |
| POL-2 | Preconditions, timing, effects, invariance and dependency-not-effect | S3 |
| POL-3 | Cost-only change, unchanged raw rows and plural tie | S3 |
| POL-4 | Target-only change, downstream reevaluation and bounded no-feasible | S3 |
| POL-5 | Missing costs, unknown feasibility, concealed ties and all selections | S3 |
| REV-1 | Verified/recomputed prior, 22 decisions and incompatibility refusal | S4 |
| RES-1 | At-limit and plus-one twins for every counted dimension | S6 |
| RES-2 | Equal/tighter request limits and relaxation refusal | S6 |
| PATH-1 | Component/final symlink, traversal, FIFO, basename, manifest and mutation | S5 |
| PATH-2 | 9p refusal and supported-filesystem probe | S5 |
| RET-1 | No-overwrite for file, directory and symlink | S5 |
| RET-2 | Concurrent winner/collision | S5 |
| RET-3 | Every pre-manifest publication fault | S5 |
| RET-4 | Post-manifest directory/parent-fsync faults | S5 |
| RET-5 | Incomplete verification and fresh-path replay | S5 |
| REP-1 | Exact-build replay and missing/changed-build refusal | S6 |
| REP-2 | Clean-build recovery boundary | S7 |
| DET-1 | Semantic determinism separated from run metadata | S7 |

The baseline result and trace contain exactly one current-condition decision, eight
raw projections, eight target assessments, four feasibility decisions and one
selection decision. A target-only comparison requires reevaluation of the eight
target, four feasibility and selection decisions but not raw projection. A cost-only
comparison requires selection reevaluation without changing physical projections.
Output equality alone is never the reevaluation oracle.

Static preparation is not marked as passing any subprocess, collision, replay,
fault-injection or command test. Those checks require the separately authorized
maintained application.

## 6. Measured inputs, outputs and proposed policy

The counters use root depth one; every map, list and scalar is a node; mapping keys
are counted separately; and every schema-declared ID, reference or commitment
occurrence is charged even when repeated. A resolution charge is one per
reconstructed node, one per reference/index lookup and one per public validator row
visited. References cannot hide resolved bytes or charges.

| Dimension | Measured maximum | Proposed limit |
| --- | ---: | ---: |
| Request bytes / nodes / depth / references | 16,475 / 550 / 8 / 104 | 32,768 / 8,192 shared input nodes / 32 / 2,048 |
| Snapshot bytes / nodes / depth / references | 84,979 / 2,679 / 15 / 587 | 131,072 / same node/depth/reference ceilings |
| Prior bundle aggregate bytes | 220,807 | 262,144 |
| Resolved comparison bytes / nodes / references | 202,950 / 6,459 / 1,382 | 262,144 / 8,192 / 2,048 |
| Comparison reconstruction charges | 7,895 | 8,192 |
| Maximum input string bytes | 71 | 256 |
| Result bytes / nodes | 9,366 / 469 | 16,384 / 1,024 |
| Trace bytes / rows | 7,873 / 30 | 16,384 / 64 |
| Diagnostic bytes | 248 | 1,024 |
| Stdout / stderr bytes | 212 / 246 | 512 each |
| Comparison retention total | 322,266 | 393,216 |
| Refusal retention total | 913 | 393,216 shared total |

The proposed exact collection ceilings are 32 model records, eight conditions,
eight constraint evaluations, four candidates per evaluation, 32 application
premise declarations, two hypotheses, four actions, eight raw rows, eight target
rows, four feasibility rows, 22 decisions, 128 corners, seven prior-bundle files,
64 changed paths and 128 digits in each rational integer.

The limit headroom is derived from the measured corpus, generally the next practical
binary boundary. It does not inherit an earlier experiment. Actual implementation
measurements remain mandatory and may force a new owner decision; the application
may not silently raise the approved limits.

Enforcement order is safe type/path, wire limit-plus-one, bounded lexical preflight,
schema/cardinality, reference/index counts, public reconstruction and resolution
charges, premise/work counts, then incremental result/trace limits before output
directory creation. Refused input or output has no partial conclusion.

## 7. Filesystem capability findings

The host is Ubuntu 24.04.2 under WSL2 Linux 5.15.167.4. CPython 3.13.11 is
available both as python3 and in the existing .venv.

findmnt and statfs identify the development checkout on /mnt/d as 9p/DrvFS, not
ext4/XFS. It is therefore outside the approved runtime-input and retention
guarantee. /tmp is backed by ext4 and is writable for disposable tests.

The disposable ext4 probe observed all intended ordinary-process behaviors:
exclusive creation, no replacement, one concurrent winner, O_NOFOLLOW symlink
rejection, incomplete state after SIGKILL, manifest-last publication, digest
verification and successful file/directory/parent fsync calls. The disposable root
was removed after the observation was captured.

This establishes neither an atomic whole-directory appearance nor power-loss
durability. It also does not make /tmp a persistent result-retention choice.
A persistent writable local ext4/XFS parent and supported runtime-input location
remain required owner inputs.

## 8. Dependency and replay readiness

The candidate locks exact runtime and focused-test versions and commits their
combined text. Installed distribution trees are fingerprinted as preparation
witnesses. Existing requirements use lower bounds, and no local wheel/sdist hashes
were available. Consequently:

- no dependency was installed or changed;
- no clean-build reproduction is claimed;
- installation must be separately authorized;
- downloaded artifacts must be SHA-256 locked before installation; and
- final build identity must include post-implementation source digests and that
  approved artifact lock.

verify can check retained bytes without the matching executable. replay may
recompute only under an externally recoverable exact build. A build identifier
alone does not authenticate an executable.

## 9. Retention and failure boundary

The implementation must exclusively create the final basename and never open or
replace an existing target. It writes and fsyncs fixed temporary files, renames each
within the directory and publishes manifest.json last. Exit 0 follows successful
file, directory and parent fsync returns.

Manifest-last publication is an application completeness marker. The directory
appears before the manifest. If a pre-manifest operation fails, the preserved
directory is incomplete and never presented as a decision. If a later directory or
parent fsync fails, the command reports complete_visible_durability_unknown and
does not claim durable success. verify never promotes or repairs incomplete
material; replay always uses a new exclusive output.

## 10. Reviewable code boundary

The seven slices are:

1. strict input and public observation admission;
2. exact raw projection;
3. total target/feasibility/selection policy;
4. 22-decision prior/proposed review;
5. safe retention, verification and recovery;
6. measured resource enforcement and the real CLI; and
7. clean-build, replay and release acceptance.

Maintained code is limited to applications/bounded_decision_workflow/ and focused
tests to tests/applications/bounded_decision_workflow/, plus an approved dependency
lock and narrow command documentation. The first completed release includes all
slices and the real evaluate command with retained output. There is no experiment
driver, private API, service, UI, authentication system, generic solver or backend
store.

## 11. Preservation, limitations and owner gate

The package and manifest recovered all 32 content-addressed objects byte-for-byte;
every digest matched. All 27 case IDs were unique and all 68 variants were
reachable. Public reconstruction and decimal admission were repeated from recovered
bytes. The pre-existing tracked and untracked inventory is checked again at
closeout; only the four authorized untracked artifacts may differ from the baseline.

This preparation supports future implementation and mathematical consistency
testing only. It does not establish physical execution, source authentication,
empirical accuracy, causal truth, generated alternatives, multi-step planning or
global minimality. IN-001 and CI-001 remain open and unselected.

Owner authorization for implementation must explicitly:

1. approve the proposed build-owned limits and counting policy;
2. approve the exact version resolution and authorize hash-locked artifact
   acquisition/environment installation;
3. nominate persistent writable local ext4/XFS runtime-input and retention paths;
4. authorize the maintained source/test scope and seven slices; and
5. retain final production acceptance as a later gate after actual command tests,
   runtime measurements, filesystem recovery and exact-build replay.

END OF BOUNDED DECISION WORKFLOW IMPLEMENTATION READINESS REPORT
