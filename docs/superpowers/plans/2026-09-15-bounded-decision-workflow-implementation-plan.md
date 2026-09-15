# Bounded decision-workflow implementation plan

## 1. Plan status and frozen authority

Current delivery status (2026-09-15): S1 remains
[accepted](../reports/2026-09-15-bounded-decision-workflow-s1-owner-acceptance.md);
the owner has [accepted S2 and authorized S3 only](../reports/2026-09-15-bounded-decision-workflow-s2-owner-acceptance.md).
The prepared resource policy, dependency lock and persistent environment were
approved separately. S4–S7 remain unauthorized. Historical preparation/gate
statements below describe the plan's original issuance, not a renewed blocker.
The [S2 completion evidence](../reports/2026-09-15-bounded-decision-workflow-s2-raw-projection-completion-report.md)
remains frozen; its historical acceptance-pending statement is superseded by the
owner-acceptance record, not edited in place.
S3 target and policy is [blocked before implementation by frozen fixture contradictions](../reports/2026-09-15-bounded-decision-workflow-s3-target-and-policy-blocker-report.md).
The accepted S1/S2 validation and frozen expectations have not been weakened or
silently amended. The report consolidates the four affected case entries for
owner correction approval; S3 is not complete.

This is implementation preparation, not implementation authorization. The maintained
target remains the local command:

    python -m applications.bounded_decision_workflow

It is one source-agnostic application over one selected serialized public
StateClassificationResult and one caller-supplied, explicitly synthetic application
world. No backend extension is proposed.

The baseline was verified on 2026-09-15 as branch brc-exp001, HEAD
ec027add0cb2dae5434c42f67454752eb93f7228, with clean tracked and staged state.
The approved [corrected design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
matches SHA-256
54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab.
Its frozen [independent review](../reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md)
matches
2bc917bee36a4e0db9b8b07b5a650455f98008e7d286a482c1127bdb8a7ddf29.

The corrected [candidate package](../reports/2026-09-15-bounded-decision-workflow-candidate-package.json)
is canonical compact JSON with SHA-256
199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4.
Its [manifest](../reports/2026-09-15-bounded-decision-workflow-candidate-manifest.json)
has SHA-256
5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a. The original package and manifest remain retained under the
`pre-obs3-decimal-correction` historical names. The correction separates a
commitment mismatch from a hostile snapshot that reaches authoritative public
reconstruction; it does not change application semantics.
The package is preparation evidence and a future test oracle. It is never runtime
input to the application.

## 2. Exact dependency and build candidate

The runtime resolution candidate is:

    annotated-types==0.8.0
    pydantic==2.13.4
    pydantic-core==2.46.4
    typing-extensions==4.16.0
    typing-inspection==0.4.2

The focused test resolution adds:

    iniconfig==2.3.0
    packaging==26.3
    pluggy==1.6.0
    Pygments==2.20.0
    pytest==9.1.1

Their combined canonical lock-text commitment is
aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e.
The inspected interpreter is CPython 3.13.11. The package records version, wheel
tag metadata and an installed-file-tree digest for every listed distribution.

This freezes exact dependency resolution but is not yet a hash-enforced installation
lock: no locally retained wheel or sdist hashes were available. No download or
installation was authorized or performed. Before clean-build reproduction is
claimed, the owner must authorize acquisition of the named artifacts, review their
SHA-256 values, and approve the resulting require-hashes lock. Proposed installation
is a separate operation from this lock specification.

Build identity will not be circular. build.json will commit the clean Git commit;
the final application/schema source paths and digests after they exist; the directly
used public-module digests already recorded in the package; application, schema,
profile and limit-policy versions; and exact CPython minor and dependency-lock
digest. It will not claim that a recorded identifier authenticates the executable.
The currently absent future source digests must be closed after implementation and
before replay acceptance.

## 3. Platform locations and guarantees

The four location roles are separate:

| Role | Inspected location | Actual backing | Prepared disposition |
| --- | --- | --- | --- |
| Development checkout | /mnt/d/operation-house-keeping | WSL 9p/DrvFS (v9fs) | May host source preparation; unsupported as a runtime-input or retained-result guarantee boundary. |
| Runtime input | Not nominated | Unknown | Owner must nominate regular files on writable local ext4/XFS with no symlink components. |
| Result retention | Not nominated | Unknown | Owner must nominate a persistent writable local ext4/XFS parent. /mnt/d is refused; volatile /tmp is not nominated for production retention. |
| Disposable tests | /tmp | ext4 (/dev/sdc[/tmp]) | Available for narrowly scoped acceptance tests and probes only. |

Linux and CPython 3.13 are available. A supported persistent runtime/result
environment is not yet demonstrated. No repository relocation, mount change,
dependency installation or system alteration is part of this plan.

On disposable ext4, the probe observed:

- exclusive directory creation followed by FileExistsError;
- preserved file, directory and symlink targets on collision;
- exactly one winner and one collision from two concurrent creators;
- regular-file O_NOFOLLOW success and symlink ELOOP;
- a SIGKILL before manifest leaving a visible, typed incomplete directory;
- manifest absence before its final rename, digest-valid visibility afterward; and
- successful regular-file, directory and parent fsync calls.

These observations support the proposed implementation and future tests. They do
not prove power-loss durability. Manifest-last publication defines application
completeness; the directory can appear earlier and does not atomically appear as a
whole.

## 4. Frozen application forms

The package freezes complete canonical examples for all request and result field
sets. REQUEST.json has exactly the eleven top-level fields in the design, including
requested_limits=null to mean use immutable build ceilings. A non-null limit object
must name every build dimension and may only tighten it.

The baseline snapshot was produced through public acquisition, projection, binding,
semantic, constraint and state-classification facades using a synthetic in-memory
temperature value of 40. It was reconstructed by public
StateClassificationResult.model_validate; public parse_observed_decimal admitted
the carried value_json as 40. A second publicly produced snapshot carries coherent
unavailable observation results. These are non-authoritative examples, not
application premises or empirical evidence.

The request separately retains:

- public-result commitment and exact observed-value joins;
- caller-owned law, parameter bounds, hypotheses, effects, preconditions, timing,
  applicability and invariance assumptions;
- target, retained hypothesis set, feasibility rule, costs and selection policy; and
- declared actor/purpose provenance, which is not authenticated identity.

The result has distinct current_condition, observed_value_admission,
raw_projections, target_relations, feasibility, selection, reevaluation,
epistemic_manifest, and commitments_and_limits sections. The trace has the exact
22-decision inventory. No caller number substitutes for the selected public
candidate.

Complete bundle filenames are request.json, snapshot.json, resolved-input.json,
result.json, trace.json, build.json and manifest.json. A refusal bundle has only
diagnostic.json, input-metadata.json, build.json and manifest.json. JSON and
manifests never name filesystem paths.

## 5. CLI and diagnostic contract

The exact modes are:

    python -m applications.bounded_decision_workflow evaluate --request REQUEST.json --snapshot SNAPSHOT.json --output-dir OUTPUT_DIR [--compare-to PRIOR_BUNDLE]
    python -m applications.bounded_decision_workflow verify --bundle BUNDLE
    python -m applications.bounded_decision_workflow replay --bundle BUNDLE --output-dir NEW_OUTPUT_DIR

Exit 0 writes exactly one compact JSON stdout receipt and empty stderr. Valid
unavailable, unknown, inapplicable and no_feasible_action_in_supplied_set are
successful semantic results. Nonzero exits write empty stdout and exactly one
bounded compact JSON diagnostic line: 2 usage, 3 input/integrity/profile/build/
prior/replay, 4 resource, 5 path/filesystem/collision, 6 retention/durability
sequence, and 7 unexpected internal failure.

The package freezes 42 codes, each with stage, target, message key, retry class,
bundle state and exit. Their order is usage; path/file safety; wire resource;
lexical/schema; commitment/public reconstruction; profile/cardinality/edition;
semantic calculation; output resource; collision; retention I/O; internal failure.
Lower public diagnostics remain causes. A refusal never carries a partial semantic
conclusion.

## 6. Measured candidate corpus and proposed build policy

Preparation materialized 27 acceptance cases as 69 complete variants. Large
canonical objects are retained once in a content-addressed zlib/base64 object store;
each object recovers to declared canonical bytes and SHA-256. This deduplication is
retention packaging only and cannot bypass runtime resolved-byte or reference
charges.

| Dimension | Measured complete maximum | Proposed immutable limit | Rationale |
| --- | ---: | ---: | --- |
| Request wire bytes | 16,475 | 32,768 | Next practical binary boundary, 1.98x measured. |
| Snapshot wire bytes | 84,979 | 131,072 | Next binary boundary, 1.54x measured. |
| Prior complete bundle bytes | 220,807 | 262,144 | Next binary boundary, 1.19x measured. |
| Resolved comparison input bytes | 202,950 | 262,144 | Next binary boundary, 1.29x measured. |
| Input nodes | 6,459 | 8,192 | Next binary boundary, 1.27x measured. |
| Input depth | 16 | 32 | Twofold structural headroom. |
| Reference occurrences | 1,382 | 2,048 | Next binary boundary, 1.48x measured. |
| Reconstruction charges | 7,895 | 8,192 | Next binary boundary under the frozen charge rule. |
| Maximum string bytes | 71 | 256 | Bounded label headroom without large payload fields. |
| Result bytes / nodes | 9,366 / 469 | 16,384 / 1,024 | Less than twofold bytes and slightly over twofold nodes. |
| Trace bytes / rows | 7,873 / 30 | 16,384 / 64 | About twofold headroom; rows are 22 decisions plus eight projections. |
| Diagnostic bytes | 248 | 1,024 | Fourfold bounded cause/context headroom. |
| Stdout/stderr bytes | 212 / 246 | 512 shared cap | More than twofold presentation headroom. |
| Complete retained comparison bundle | 322,266 | 393,216 | 384 KiB, 1.22x measured. |
| Refusal bundle | 913 | Included in 393,216 | Independently measured, not inferred from success. |

Fixed collection limits are two hypotheses, four actions, eight raw rows, eight
target rows, four feasibility rows, 22 decisions, at most 128 corner evaluations,
32 application premise declarations, 32 public model records, eight conditions,
eight constraint evaluations, four candidates per evaluation, seven prior-bundle
files, 64 changed paths and 128 digits per rational integer.

Counting is root-depth-one; every map/list/scalar is one node; keys are separate;
each schema-declared identity/reference/digest occurrence is charged even when
duplicated. A resolution charge is one per reconstructed JSON node, one per
reference/index lookup and one per public validator row visited. Wire bytes are
captured before decode; resolved bytes count full current and prior semantic
material despite references.

These are proposed, not approved production limits. Static preparation did not run
the command. Implementation must independently measure actual runtime maxima and
return any excess rather than silently raise a ceiling.

## 7. Acceptance map

Every row maps to exact package arguments, complete materializable inputs, an
independent expected process/result/trace or diagnostic, and its verifying slice.

| Case | Prepared coverage | Slice |
| --- | --- | --- |
| CMD-1 | Full evaluate, admitted T0=40, 8+8+4+1 decisions, seven-file bundle | S6 |
| CMD-2 | Usage, rejected input, valid unavailable, no-feasible, collision, retention failure | S6 |
| OBS-1 | Positive exact public join and decimal reparse | S1 |
| OBS-2 | Absent, unattached, inconsistent, nonnumeric and semantic/unit unavailable twins | S1 |
| OBS-3 | Retarget, context, cutoff, unit and index substitutions; revision, forged-result and hostile-decimal public refusals; stale snapshot commitment | S1 |
| OBS-4 | Conversion refusal and positive interpreted-unit/source-lexeme case | S1 |
| NUM-1 | Exact endpoints, float, reversed interval, correlation and digit overflow | S2 |
| UNC-1 | Complete widened beta support | S2 |
| UNC-2 | Missing/unknown support and stale refusal | S2 |
| POL-1 | Mixed unknown/incompatible and false-gate precedence | S3 |
| POL-2 | Preconditions, timing, effects, invariance and dependency-not-effect | S3 |
| POL-3 | Cost-only change, unchanged physical rows and tie | S3 |
| POL-4 | Target-only reevaluation, unchanged raw rows and bounded no-feasible | S3 |
| POL-5 | Unknown cost/feasibility, hidden tie/cheaper action and plural ties | S3 |
| REV-1 | Verified/recomputed prior and incompatible-prior refusal | S4 |
| RES-1 | Every measured ceiling and dimension-specific plus-one twin | S6 |
| RES-2 | Equal/tighter request limits and relaxation refusal | S6 |
| PATH-1 | Symlinks, traversal, FIFO, basename, manifest name and mutation | S5 |
| PATH-2 | 9p refusal and ext4 primitive evidence | S5 |
| RET-1 | File/directory/symlink collision preservation | S5 |
| RET-2 | Two creators, one winner, one collision | S5 |
| RET-3 | Every pre-manifest fault/interruption boundary | S5 |
| RET-4 | Directory/parent fsync after-manifest failures | S5 |
| RET-5 | Incomplete verification and new-path replay | S5 |
| REP-1 | Exact-build replay and build-identity refusal | S6 |
| REP-2 | Clean-build recovery requirement and honest unavailable build | S7 |
| DET-1 | Stable semantic bytes and enumerated run-metadata differences | S7 |

OBS-2 producer recipes are acceptance inputs, not forged public results.
Implementation tests must materialize them through public facades. Static expected
values do not count as command-level passes.

## 8. Independently specified expected reasoning

The preparation oracle uses standard-library Fraction, exhaustive distinct Cartesian
endpoint corners and separately written target/feasibility/cost set logic. It does
not import or call the future application. It shares the approved equation,
assumptions, identifiers and canonical rules and has same-author provenance; it is
independent implementation checking, not independent empirical evidence.

It fixes baseline raw results:

- H_H: a0=42, aF=42, aH=32, aHF=32;
- H_F: a0=36, aF=32, aH=36, aHF=32; and
- target [31,33], retained {H_H}, costs 0,3,2,5: select {aH} at cost 2.

It also fixes beta [1/10,3/10] giving H_H/aH=[30,34], cost-only raw
invariance, target-only raw invariance, closed endpoint relations and every total
policy disposition. Runtime code must not read package expectations or branch on
case IDs, paths or commitments.

## 9. Reviewable implementation slices

Slices are review checkpoints, not partial releases:

1. S1 — strict input and public admission: streaming preflight, request models,
   public reconstruction, exact joins and complete example generation.
2. S2 — raw projection: exact rational/profile validator, gates, effects,
   Cartesian corners and raw traces only.
3. S3 — target and policy: relation, feasibility and selection total functions;
   no filesystem code.
4. S4 — decision review: fixed 22-decision dependencies, prior recomputation,
   changed/equal-after-reevaluation distinctions.
5. S5 — retention and recovery: descriptor-relative safe paths, exclusive
   manifest-last publisher, verifier and fault-injection seams.
6. S6 — resource and CLI delivery: immutable policy, incremental counters,
   evaluate/verify/replay, exact diagnostics and real subprocess coverage.
7. S7 — release gate: clean source/lock identity, ext4/XFS recovery,
   deterministic semantics and exact scope inspection.

Maintained source is limited to applications/bounded_decision_workflow/ and tests
to tests/applications/bounded_decision_workflow/, plus the reviewed dependency lock
and narrow user documentation. No disposable driver is imported. The first release
exists only after S1–S7 and delivers the actual command and retained result; no
callable-only experiment is called a release.

## 10. Authorization gate

Production implementation remains gated on one consolidated owner action:

1. approve or amend the proposed measured limit policy;
2. approve the exact version lock and authorize acquisition of hash-identified
   dependency artifacts plus any environment creation/installation;
3. nominate a persistent writable local ext4/XFS runtime-input and result parent,
   or explicitly approve a different platform contract through design change;
4. authorize maintained source/tests in the exact boundaries above; and
5. require final source digests, actual runtime measurements, real command tests
   and clean-build replay to return for production acceptance.

No semantic amendment was required. IN-001 and CI-001 remain open and unselected.
No implementation, production test, dependency installation or history operation
is authorized by this plan.
