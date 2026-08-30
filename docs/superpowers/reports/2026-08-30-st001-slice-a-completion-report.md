# ST-001 Slice A Completion Report

Date: 2026-08-30
Status: owner accepted at `9adcf4d9613ac96e5fb430a4b750f3053679b64d`; Slice B separately authorized
Scope: Slice A only — state identity and model-kernel record foundation

## 1. Executive result

ST-001 Slice A is implemented on branch `st001` from the exact accepted base
`0ed77df7ea4870faec1eae9b89668add97aa855d`. The implementation adds opaque
state identity, the three accepted state record kinds, canonical integration,
store admission, immutable lifecycle indexes, hostile reconstruction checks,
and explicit historical replay coverage.

The verified implementation/status HEAD before this completion-report commit is
`bc5fe1880ced27724c4201fa50aa98a8b7769586`. The report commit and resulting
final administrative HEAD are supplied in the file-delivery receipt because a
committed file cannot truthfully contain the hash of the commit that contains
it.

The authoritative demo ledger remains unchanged at exactly 32 records and
revision
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
It contains no `srg_`, `std_`, or `stw_` record. Slices B, C, and D have not
started.

## 2. Boundary and authority verification

Before implementation:

- `HEAD`, `main`, and `origin/main` were all
  `0ed77df7ea4870faec1eae9b89668add97aa855d`;
- the only ordinary untracked project files were the five intentional ST-001
  design and provenance artifacts;
- the accepted corrected synthesis matched owner-supplied SHA-256
  `febe18fa291896021708d09c10d5cf4ef955201bcd3e59199e74c6c4e630cc95`;
- branch `st001` was created from that exact base while preserving those five
  files;
- `.claude/settings.local.json` remained ignored, untouched, and uncommitted.

The accepted synthesis now hashes to
`fad6fb16da61aab4ed2d1837674802dcbef3dfbfacec327a2ea66041d571e19f`
because the authorized Slice A status annotation was committed after design
acceptance. No architecture, schema, or adjudicated meaning was changed.

## 3. Commit sequence

The implementation was divided into reviewable documentation, red-test,
production, hardening, and status commits:

1. `d2d5191f81eb40935e3936fabb8349b52f477459` — `docs: accept ST-001 design and plan Slice A`
2. `e9acc6a7522f9ac0811ee9f03aac5c8942c33d04` — `test: define ST-001 state identity contracts`
3. `62fc24da12c72ff95b92e88ad1e0b2b66ea215e8` — `feat: add ST-001 state identity`
4. `84ff801ae48e81968c3e9acb54ac5c6f21df0d8a` — `test: define ST-001 state record contracts`
5. `15b65eec13fccc055b233810757809b3b1a66f83` — `feat: add ST-001 state record contracts`
6. `a4081631739a250f5fff4ba7201938c0e710de3d` — `test: define ST-001 store and lifecycle invariants`
7. `369dc6ae834918f91c14bef171bd8b714d5f6094` — `feat: integrate ST-001 state lifecycle store`
8. `ebca1fca4b6a939008354f09437b9ad20f76a1c2` — `test: harden ST-001 replay and persistence boundaries`
9. `fb92915b23dc4b944d33166d9ec247b5350833a9` — `docs: document ST-001 Slice A kernel boundary`
10. `b142a780b54c6ec78d993c6eb620ef080648c719` — `test: expand ST-001 adversarial integrity coverage`
11. `20ce733f4cef193d8e67cbffb5c492003797e205` — `fix: reject hidden nested model extras`
12. `a408f4f211a06c7ac619911161a5d7be059814c1` — `test: pin complete ST index ordering`
13. `bc5fe1880ced27724c4201fa50aa98a8b7769586` — `docs: record ST-001 Slice A implementation status`

No commit was amended or rewritten.

## 4. Exact changed files before this report

Thirty-five files differ from the accepted base:

### 4.1 Status, architecture, plans, and accepted design provenance

- `CLAUDE.md`
- `docs/adr/0016-explicit-state-identity-and-evidence-gated-classification.md`
- `docs/superpowers/plans/2026-08-30-st001-slice-a-implementation-plan.md`
- `docs/superpowers/plans/2026-08-30-st001-slice-a-adversarial-acceptance-matrix.md`
- `docs/superpowers/proposals/2026-08-30-st001-codex-lead-proposal.md`
- `docs/superpowers/proposals/2026-08-30-st001-kimi-k3-challenger-proposal.md`
- `docs/superpowers/reports/2026-08-30-st001-final-synthesis-challenger-audit.md`
- `docs/superpowers/reports/2026-08-30-st001-final-synthesis-correction-report.md`
- `docs/superpowers/specs/2026-08-30-st001-explicit-state-identity-and-evidence-gated-classification-design.md`

### 4.2 System identity

- `backend/system_identity/README.md`
- `backend/system_identity/__init__.py`
- `backend/system_identity/anchors.py`
- `backend/system_identity/minting.py`

### 4.3 Model kernel

- `backend/model_kernel/README.md`
- `backend/model_kernel/__init__.py`
- `backend/model_kernel/canonical.py`
- `backend/model_kernel/contracts.py`
- `backend/model_kernel/store.py`

### 4.4 Tests

- `tests/identity_binding/test_state_anchor.py`
- `tests/model_kernel/st001_slice_a_helpers.py`
- `tests/model_kernel/test_state_canonical.py`
- `tests/model_kernel/test_state_records.py`
- `tests/model_kernel/test_state_revalidation.py`
- `tests/model_kernel/test_state_store.py`
- narrow exact-public-surface expectation updates in:
  `tests/identity_binding/test_behavior_anchor.py`,
  `tests/identity_binding/test_port_anchor.py`,
  `tests/identity_binding/test_variable_anchor_minter.py`,
  `tests/model_kernel/test_behavior_query_contracts.py`,
  `tests/model_kernel/test_behavior_records.py`,
  `tests/model_kernel/test_port_records.py`,
  `tests/model_kernel/test_structural_evidence_arm.py`,
  `tests/model_kernel/test_variable_port_query_contracts.py`,
  `tests/model_kernel/test_variable_port_records.py`,
  `tests/model_kernel/test_variable_registration.py`, and
  `tests/model_kernel/test_variable_value_specification.py`.

This completion report is the only additional file in the final report commit.

## 5. Public identity contract

Slice A adds exactly:

- `STATE_ANCHOR_ID_PATTERN = r"^sta_[0-9a-f]{32}$"`;
- frozen, extra-forbidden, fully revalidated `StateAnchor`;
- `mint_state_anchor(*, namespace, display_name, role_name=None)`.

The minter calls standard-library UUID4 once, uses `uuid4().hex`, prefixes it
with `sta_`, and constructs the existing public contract. It performs no I/O,
registration, persistence, authority assertion, evidence construction, or
business-meaning derivation. Names and optional role metadata do not determine
identity. The anchor carries no subject, condition, context, lifecycle,
classification, transition, evidence, or authority.

## 6. Public model-record contracts

Slice A adds these canonical model records:

| Contract | Kind | Prefix | Citable |
|---|---|---|---|
| `StateRegistration` | `state_registration` | `srg_` | yes |
| `StateDeclaration` | `state_declaration` | `std_` | yes |
| `StateDeclarationWithdrawal` | `state_declaration_withdrawal` | `stw_` | no |

`StateRegistration` permanently fixes the complete embedded `StateAnchor`, one
registered subject entity, a sorted and unique tuple of 1–64 constraint anchor
IDs, `condition_family="all_of_constraints"`, nonempty canonical evidence,
recorded time, authority, and note. A different subject, condition set, or
condition family requires a different state identity.

`StateConstraintDeclarationPin` contains exactly a constraint anchor ID and an
exact `vcn_` declaration ID. `StateDeclaration` contains one canonical pin for
every permanent constraint, exact `AssertionContext`,
`evaluation_basis="independent_latest_at_or_before_cutoff"`, nonempty canonical
evidence, canonical multi-parent `supersedes`, recorded time, authority, and
note.

`StateDeclarationWithdrawal` contains only its `stw_` identity, the current
`std_` target, recorded time, authority, and note. It has no evidence, context,
parent, outcome, reason code, replacement, or physical-state assertion.

All new public tuple contracts, record classes, builder support, and package
exports are pinned exactly. `ModelRecordEvidence` admits `srg_` and `std_` and
continues to reject `stw_`.

## 7. Canonical identity and golden vectors

Record identity continues to be:

`<prefix>_<sha256(canonical record content excluding record_id)>`

Canonical serialization remains deterministic ASCII JSON with the accepted
key and tuple ordering. Existing kinds retain their prior bytes and identities.
The deterministic ST vectors are:

| Kind | Golden record ID | Canonical payload bytes excluding `record_id` |
|---|---|---:|
| SRG | `srg_c87954c50e92c35d4143e016bf90383d6a6a5f64347741336218bcbcaa027b73` | 1000 |
| STD | `std_2c3cb8783acadd8add368efcbf2782a165f591e06c6a77109caad7de018f4bb8` | 1409 |
| STW | `stw_b811c3b4c435aff8421a4ebdb4fa133ff3b86a8b8b5d4d9dc228aff312fe0cd0` | 297 |

The SHA-256 of each payload is exactly the suffix of its record ID. Reversed
valid constraint, pin, parent, and evidence inputs canonicalize to the same
bytes and IDs. Malformed, duplicate, self-parent, and cross-kind identities are
rejected before they can influence canonical output.

## 8. Store admission and ownership invariants

The existing `ModelStore` is the only store. There is no ST ledger, state
database, projection, cache, or revision type. Collection validation now
enforces:

- exactly one agreeing registration per `sta_` identity; divergent or duplicate
  registration rejects;
- registered subject entity and complete evidence closure;
- every condition constraint registration exists;
- each constraint's target variable registration exists;
- the target variable's embedded owner entity is exactly the state subject;
- no hierarchy, relationship, port, VPA, behavior, name, CAD, or topology is
  consulted to infer ownership;
- every declaration pin exactly covers the permanent constraint set;
- every `vcn_` pin exists and belongs to the named constraint;
- every declaration and parent has the exact same state/context lineage key;
- withdrawals target current STD tips and cannot race a successor in the same
  membership;
- failed append is atomic: no file, accepted collection, or revision changes.

The generic public `revalidate()` boundary was hardened to inspect the complete
nested Pydantic object graph iteratively. Hidden unknown fields injected through
`model_copy`, including nested instances, now fail closed rather than bypassing
`extra="forbid"`. The traversal is cycle-safe and preserves every accepted
existing contract.

## 9. Immutable loaded-model indexes

`LoadedModel` carries read-only, deterministically ordered state indexes for:

- registrations by record and anchor;
- state anchors by subject entity;
- permanent condition constraint IDs by state anchor;
- declarations by record and exact `(state_anchor_id, context)` key;
- parent and successor IDs;
- root and ancestry membership;
- current tips by root;
- withdrawals by record and target.

The tests pin complete mappings, tuple order, immutability, strict key/value
identity, and deterministic reconstruction under reversed physical append order
and multiple hash seeds.

## 10. Declaration lifecycle evidence

The accepted STD lifecycle is implemented without winner selection:

| Situation | Store/index result |
|---|---|
| one root, one current tip | healthy root |
| same-root fork | conflicted root |
| partial fork convergence | still conflicted |
| complete same-root convergence | healthy current tip |
| cross-root convergence | rejected |
| one selectively withdrawn fork tip | remaining current tip disclosed |
| every root tip withdrawn | inactive root retained |
| identical effective bodies in independent healthy roots | corroborating groups retained separately |
| differing effective bodies in independent healthy roots | disagreement retained |

The effective engineering body uses exactly state anchor, exact context,
canonical constraint-declaration pins, and evaluation basis. Evidence,
authority, recorded time, note, record ID, filename, hash, and append order do
not distinguish effective bodies. Full-record equality is not used.

Parent/ancestry validation uses the accepted model-kernel iterative explicit-
stack three-colour traversal. Recursive traversal is prohibited. A deep hostile
chain is exercised under a deliberately low Python recursion limit and remains
deterministic; a cycle fails closed.

## 11. Red-before and fixed-after record

The principal implementation groups began with deliberately failing public
tests:

| Group | Red evidence | Fixed-after evidence |
|---|---|---|
| state identity | 33 target failures with 62 existing identity checks still passing | identity surface green; final focused column included |
| state record contracts | 35 target failures before contracts and canonical arms existed | record and canonical contract suites green |
| store/lifecycle | 21 target failures before dispatch, closure, lifecycle, and indexes existed | store/lifecycle target reached 63 green checks, then expanded |
| documentation boundary | one focused status assertion failed before Slice A boundary was recorded | documentation target reached 102 green checks |
| nested hostile extras | specialist reproduction failed because `model_copy` could preserve an undeclared nested field | one regression green after iterative full-graph hardening |
| additive prefix surface | one broad legacy expectation failed while 1,341 peers passed | corrected to the accepted additive 22-prefix surface |

The final focused ST column is 116 passed. The canonical/persistence and later
specialist reproductions were added as hardening groups after the initial core
red/green sequence; this report does not mislabel those later additions as the
first production-driving tests.

## 12. Adversarial coverage

The retained tests cover at least:

- malformed, uppercase, wrong-prefix, wrong-length, and nonhex `sta_`, `srg_`,
  `std_`, and `stw_` identities;
- forged anchors and nested records produced with `model_construct`,
  `model_copy`, hidden extras, wrong union arms, stale content IDs, and mutated
  canonical content;
- absent subject, zero/one/64/65 conditions, duplicate and reordered inputs,
  cross-entity constraints, and missing CRG/VRG/owner closure;
- missing, extra, duplicate, substituted, wrong-constraint, absent, and stale
  VCN pins;
- cross-state/context parents, duplicate parents, self-parent, cycle,
  cross-root convergence, same-root forks, partial/full convergence,
  identical-body roots, and differing-body roots;
- selective/complete withdrawal, duplicate/invalid/non-tip/wrong-kind targets,
  and successor-withdrawal races;
- evidence closure and the uncitable STW boundary;
- hostile on-disk records, filename/content mismatch, atomic failed append,
  hash-seed stability, enumeration/physical-order stability, and the iterative
  deep-DAG boundary;
- complete immutable-index content and ordering;
- byte- and revision-identical replay for every explicit pre-ST membership.

No test derives historical membership from directory enumeration, prefixes,
timestamps, kinds, or append order.

## 13. Specialist reviews and reconciled repairs

Three internal specialists independently reviewed the green implementation:

### 13.1 Backend/model-kernel review

The reviewer found no production blocker in the identity, record, canonical,
ownership, lifecycle, or import boundary. It confirmed that the implementation
stayed within Slice A and used the existing store/revision architecture.

### 13.2 Canonical-integrity/adversarial review

The reviewer identified one genuine integrity gap: an undeclared field injected
into a nested Pydantic instance by `model_copy` could survive the former shallow
revalidation path. The finding was reproduced as a failing public regression,
then repaired by iterative full-object-graph extra detection. The reviewer
reran the focused and legacy hostile suites and reported no remaining blocker.

### 13.3 Test-coverage review

The reviewer requested stronger proof for full index ordering, nontrivial DAG
determinism under hash seeds and physical append order, semantic hostile-disk
mutations, whole-ledger failure snapshots, pin/citation parity, and the exact
64-condition boundary. Each accepted request was added without extending into
queries or classification. The final focused column reached 116 passed and the
reviewer reported no remaining Slice A blocker.

No external Kimi review was requested; the previously completed design pass
was not reopened.

## 14. Verification matrix

All commands used `PYTHONDONTWRITEBYTECODE=1`, disabled the cache provider where
shown, and ran against the verified implementation/status HEAD
`bc5fe1880ced27724c4201fa50aa98a8b7769586`.

| Column | Result |
|---|---|
| focused ST identity/record/store/revalidation/isolation | 116 passed in 17.45 s |
| architecture and import isolation | 51 passed in 14.99 s |
| backend compilation | clean |
| affected identity binding, CN, behavior evaluation, and model state | 722 passed in 164.36 s |
| focused OCP/STEP/PDF | 120 passed in 291.64 s |
| complete model-kernel suite | 1,215 passed in 170.46 s |
| PT/VP/BH demo, replay, and artifact preservation | 44 passed in 42.22 s |
| complete repository, implementation worktree | 2,904 passed in 691.77 s |
| fresh base-only checkout | 2,868 passed, 35 expected optional skips, one sandbox-denied loopback setup; isolated permitted rerun 1 passed in 0.68 s |
| fresh all-extras checkout | 2,903 passed, one sandbox-denied loopback setup in 425.91 s; isolated permitted rerun 1 passed in 0.70 s |

The base-only skips are the dependency-gated CAD/PDF paths. The all-extras
column installed the repository's hash-pinned CAD and PDF dependency sets and
exercised those paths. In both clean checkouts, the only aggregate-suite error
was the known `PermissionError: [Errno 1] Operation not permitted` while binding
`127.0.0.1`; it was reported separately and rerun with the accepted localhost
permission. A denied setup was not counted as a pass.

Both clean checkout trees remained clean and at
`bc5fe1880ced27724c4201fa50aa98a8b7769586` after verification.

### 14.1 Reproduction commands

Representative commands were:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider <focused ST files> -q
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel -q
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q
PYTHONDONTWRITEBYTECODE=1 <clean-venv>/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q
PYTHONDONTWRITEBYTECODE=1 <clean-venv>/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation -q
.venv/bin/python -m compileall -q backend
git diff --check
```

## 15. Historical and byte preservation

The explicit memberships at 9, 10, 11, 14, 16, 18, 28, 29, and 32 records
all replay with their accepted record IDs and revision IDs. Closure is evaluated
against the exact caller-supplied membership. Pre-ST revisions return no
migration artifacts and no inferred state knowledge.

Preservation checks establish:

- authoritative model record count: exactly 32;
- current revision:
  `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`;
- committed ST records: zero `srg_`, zero `std_`, zero `stw_`;
- all 32 predecessor record files remain present and byte-identical to their
  accepted frozen hashes;
- PT artifact SHA-256 remains
  `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP artifact SHA-256 remains
  `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH artifact remains 122,406 bytes with SHA-256
  `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`;
- no model, binding, interpretation, temporal, source, structural, PT, VP, or
  BH fixture file changed.

The added prefixes and discriminators are purely additive. Tests preserve the
canonical bytes, IDs, schemas, and hash vectors for all previous record kinds.

## 16. Architecture and import boundary

Dependency direction remains foundational:

```text
system_identity
      ↑
model_kernel
```

The kernel does not import model state, temporal state, identity binding,
semantic compatibility, constraint evaluation, behavior evaluation, source
interpretation, data sources, or the future state-classification layer. No ST
component constructs an additional store or accesses the filesystem outside
the existing `ModelStore` boundary.

## 17. Explicit exclusions and limitations

Slice A intentionally does not include:

- the four Slice B kernel query methods or result contracts;
- `backend/state_classification`, CN composition, condition sources, temporal
  classification, or computed matching;
- any demo/fixture state identity or `srg_`, `std_`, or `stw_` ledger append;
- state family, state space, exclusivity, completeness, priority, or winner;
- ports, VPA admission, behavior inference, flow, direction, causality,
  influence, control, safety, health, diagnosis, or recommendations;
- transitions, from/to direction, triggers, guards, events, actions, transition
  occurrence, state-machine execution, or persistence of derived results;
- any new ledger, database, projection, cache, or revision.

The store validates the whole selected collection and materializes ancestry;
therefore its worst-case work and memory grow with declaration graph size. The
iterative traversal removes Python recursion risk but does not claim an
application-level unbounded-work guarantee. Slice A establishes model knowledge
only; it cannot classify observations and cannot say a system is in a state.

## 18. Git and remote-operation status

Immediately before writing this report:

- branch: `st001`;
- implementation/status HEAD:
  `bc5fe1880ced27724c4201fa50aa98a8b7769586`;
- `main`: `0ed77df7ea4870faec1eae9b89668add97aa855d`;
- `origin/main`: `0ed77df7ea4870faec1eae9b89668add97aa855d`;
- accepted base is an ancestor of HEAD;
- `git diff --check`: passed;
- `git status --short`: empty;
- no push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
  performed.

The report is committed separately, after which `git diff --check`, branch,
topology, and clean working-tree status are rechecked and recorded in the
delivery receipt.

## 19. Owner handoff

ST-001 Slice A was implemented and adversarially reviewed, then owner accepted
at `9adcf4d9613ac96e5fb430a4b750f3053679b64d`. Slice B was separately
authorized. Slices C and D remain unstarted and unauthorized.

END OF ST-001 SLICE A COMPLETION REPORT
