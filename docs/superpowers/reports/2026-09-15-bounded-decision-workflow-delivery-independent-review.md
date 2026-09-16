# Independent adversarial review of the bounded decision workflow delivery proposal

## 1. Verdict

**Verdict: `reject`.**

The proposed local application boundary is directionally correct and does not expose
a demonstrated need for a new backend contract. Its central layering is also sound:
one carried current-condition result, application-owned hypothetical premises, raw
one-step calculations, target relations, robust feasibility, finite selection and
reevaluation are kept conceptually separate.

Design approval is nevertheless premature. Five blocking findings leave admitted
evidence, the projection/policy result, retention, replay and command behavior
non-single-valued. Different reasonable implementations could accept different
`T0` evidence, calculate different uncertainty sets, report different feasibility or
selection outcomes, or handle the same output collision/interruption differently.
Those differences can change the answer or lose the retained decision. They must be
resolved in the proposal or a corrected specification before an implementation slice
is authorized.

This is a rejection of the current delivery specification, not of the bounded local
product direction. The corrections in §8 are intentionally smaller than a new
framework, service, backend package, ADR or milestone.

## 2. Reviewer provenance, independence and frozen authority

This review was performed by the separately staffed reviewer task
`/root/bounded_workflow_reviewer`. The reviewer had no proposal-authorship role and
did not edit the proposal. Independence here means an adversarial design and source
review in a separate task; it does not mean independent empirical evidence or an
independent authority for the proposal's synthetic premises.

The review began by confirming:

- branch `brc-exp001`;
- HEAD `ec027add0cb2dae5434c42f67454752eb93f7228`;
- frozen [delivery proposal](../proposals/2026-09-15-bounded-decision-workflow-delivery-proposal.md)
  SHA-256 `f48065f53f35a302d9cd1c4f3d66872bf367f0625da44bc499b3be97381b808f`;
- [post-experiment consolidation](2026-09-15-post-experiment-objective-and-architecture-consolidation.md)
  SHA-256 `08bdd577755c5e1e8b04a2780c137ae31de8a742dcdc8020f2c2097a534f9574`;
- [one-step owner acceptance](2026-09-15-one-step-intervention-projection-owner-acceptance.md)
  SHA-256 `f4e016475520bb3c1b6ce656134ef4e2e2c5fd7f5ab0a31b542e0c955702789d`;
  and
- immutable [one-step execution report](2026-09-15-one-step-intervention-projection-final-execution-report.md)
  SHA-256 `bb84cdd0743f4aa08eb6cfc58c07478493deac534db97f7c133ce93d2a77aba1`.

The full frozen proposal and consolidation were read. The accepted corrected
[one-step design](../specs/2026-09-15-one-step-intervention-projection-corrected-design.md),
owner acceptance, execution findings and recovery boundary were inspected, together
with the [CV deferral requirements](2026-09-10-cv001-deferral-owner-decision.md),
[original objectives](../../../CLAUDE.md), [current architecture](../../../README.md),
and the actual public contracts cited below. The execution report's embedded
canonical archive was treated as retained evidence, not executed source.

At entry, tracked and staged diffs were empty and 59 pre-existing untracked artifacts
were present, including the frozen proposal. Their sorted path inventory and
path-plus-content inventory digests were respectively
`78db4205cb2eedab3ab5498f523114fab104aceb0e2397f668ddc16996613383`
and `b59a23b5a11fe1da2a27ff56e08d51b4caf2ae10b94d878fabe087cdb396cffe`.
They are preservation baselines, not authenticity claims.

## 3. Source-backed findings that are already sound

### 3.1 Public-result authority is correctly placed

The proposal correctly uses
[`StateClassificationResult.model_validate`](../../../backend/state_classification/contracts.py)
as the owning reconstruction boundary. The contract rebuilds every nested public
input, reruns the authoritative classification derivation and rejects a forged
disclosure. That derivation checks the exact state anchor/context, cutoff, model
revision, permanent condition set, constraint declarations, selected candidate,
binding revision and interpretation revision. The proposal therefore need not copy
private state-classification logic.

The model boundary is also public and sufficient.
[`ModelQueryMaterial`](../../../backend/model_kernel/port_results.py) requires unique,
ordered records exactly equal to the carried revision membership, revalidates the
collection, and exposes `loaded()`. [`ModelQueries`](../../../backend/model_kernel/queries.py)
accepts that public loaded form and produces validator-locked public query results.
The application can reconstruct and query selected membership without a hidden store,
ambient ledger, source lookup or private backend call.

This supports the proposal's decision to leave backend semantics authoritative for
their own facts and to implement the law, effects, target, policy, review and retained
packet in maintained application code. No reviewed evidence demonstrates a necessary
lower-layer gap. IN-001 and CI-001 must remain open and unselected.

### 3.2 The epistemic and decision layers are correctly separated

The proposal expressly says that a state match does not select a hypothesis or prove
an effect; cost cannot enter physical projection; a calculated `T1` is not an
observation; and a content digest is not source authentication or physical truth.
Those limitations match the accepted one-step design and the repository's truth
boundary.

The result inventory also preserves the important distinctions among:

- classification at the selected cutoff;
- raw hypothesis/action projections;
- target relations;
- per-action feasibility;
- tied finite-set selection; and
- required reevaluation versus equal or changed recomputed values.

The target-only and cost-only controls are especially valuable. They retain the
accepted C7 result that a target change reevaluates downstream decisions but not raw
physics, and the accepted C5 result that a cost change affects selection only.

### 3.3 The proposed maintained-code ownership is substantially complete

The proposal identifies all computations that must become maintained application
code: strict request/result contracts, authoritative snapshot reconstruction,
evidence binding, exact arithmetic, effect application, target/feasibility/selection,
complete-world review, canonical retention, replay verification, resource guards and
the thin module adapter. It does not rely on the deleted disposable runtime as a
production dependency and expressly requires reimplementation with maintained tests.

The local command is proportionate to the named consumer. A local engineer operating
under one OS account does not require an HTTP service, account database, daemon or
network authentication system merely to evaluate explicitly supplied alternatives.
The CV security and deployment prerequisites can be satisfied by an explicit local
filesystem trust boundary, provided the remaining file and error semantics are fixed.

## 4. Blocking findings

### BF-1 — An exact pointer is not yet an evidence-admission rule

The proposal says `T0` binds to a “value-bearing candidate” and that the application
checks value, unit, subject, variable, cutoff and result index. That is necessary but
not sufficient. The shipped evidence contracts intentionally expose several
orthogonal states: a candidate can exist yet be unattached, internally inconsistent,
non-numeric, semantically incompatible, or have only a source-unit lexeme rather than
an exact interpreted unit identity. The
[`VariableStateResult`](../../../backend/model_state/contracts.py) has no aggregate
current value, and [`CandidateConstraintEvaluation`](../../../backend/constraint_evaluation/contracts.py)
only exposes an `observed_decimal` after attachment, evidence consistency, numeric
shape, declared semantic compatibility and exact constraint-unit identity pass.

The proposal does not say whether `T0` must target that reached decimal row, the raw
occurrence lexeme, or another nested candidate. It also calls for an “explicit
unit/conversion identity,” although the public
[`UnitReference`](../../../backend/model_kernel/contracts.py) is explicitly only an
identity token and asserts no dimension, convertibility, scale or offset. No shipped
conversion authority exists.

As written, one implementation could admit a parseable but semantically rejected
occurrence while another refuses it. A caller-supplied conversion could also be
mislabelled as validated backend material. This can change every projected answer.

**Required resolution:** freeze one typed binding grammar and its allowed terminal
contract. For `T0`, require the exact carried condition/evaluation/candidate indices,
bound attached occurrence, consistent evidence, numeric reached evaluation,
compatible quantity/role, exact interpreted unit identity, matching subject,
variable, cutoff and model/binding/interpretation revisions. Reparse the occurrence
and require equality with the carried authoritative decimal. Any conversion law must
be a separately versioned application assumption with source and uncertainty, never a
backend-accepted fact. Missing support should make projection unavailable; malformed,
retargeted or mismatched references should refuse the request.

### BF-2 — Projection and policy semantics exceed the accepted proof without a closed form

The accepted proof used complete Cartesian hard support, shared parameter coordinates,
an affine law and exact endpoint evaluation. The proposal instead admits “joint
uncertainty,” says dependencies or correlations may be explicit, and promises to
evaluate “all applicable joint-domain corners,” but defines neither the representable
joint-domain schema nor what constitutes a corner for a correlated domain. An interval,
a list of feasible tuples, a convex polytope and a disconnected finite set do not have
the same validation or hull semantics. Taking an interval hull of a disconnected set
can also alter target intersection.

Feasibility is similarly underdetermined. The stated rules make both `incompatible`
and `unknown` applicable when one retained row is complete and incompatible while a
different retained row is unknown. Empty or duplicate nominated/retained sets are not
resolved. The selection rule says incomplete information may not hide a “possibly
better” feasible action, but does not define whether an unknown equal-cost action can
hide a required tie, whether an unknown higher-cost action is irrelevant, or how a
missing cost combines with known infeasibility. Preconditions, global applicability,
stale references and missing effects also need an explicit total precedence.

These are answer-changing ambiguities in maintained computation, not ordinary coding
details.

**Required resolution:** keep release one at the accepted profile unless a wider form
is separately specified. The minimal safe choice is a nonempty, duplicate-free finite
hypothesis/action inventory; a nonempty retained subset; closed exact rational
Cartesian hard-support intervals with one named shared coordinate per parameter; the
fixed affine law; and the four fixed assignment-effect forms. Freeze a total truth
table and precedence for every combination of guaranteed, possible, incompatible,
unknown and inapplicable rows. Freeze selection over all nominated actions, including
unknown feasibility/cost and tie concealment, and define exactly when
`no_feasible_action_in_supplied_set` is warranted. Reject unsupported correlations
rather than implying general support.

### BF-3 — The no-overwrite “atomic directory” promise has no implementable commit and recovery protocol

The proposal requires a new output directory, says the directory is written
atomically, promises never to overwrite an existing bundle, and publishes no success
before all files and digests are complete. It does not specify how those properties
coexist under a create/collision race, symlinked path component, same-name empty
directory, cross-filesystem rename, process interruption, `ENOSPC`, failed `fsync`, or
manifest failure. Portable `rename` is not by itself a no-replace directory commit
primitive. A check-then-rename sequence can race; replacing an existing target would
violate the proposal's strongest retention promise.

There is also no disposition for abandoned staging material. The proposal says
retention/runtime failure has a distinct exit class, but not where a diagnostic goes
when the intended bundle cannot be committed, whether a partial directory is
recognizable and recoverable, or whether retry may reuse or remove it. The optional
prior bundle receives integrity checks, but fixed filenames, symlink behavior,
manifest path rules and read-once/TOCTOU behavior are not frozen.

**Required resolution:** choose one concrete local protocol. A minimal portable
design is: open the output parent explicitly; reject unsafe/non-directory components;
create the final directory exclusively; write only fixed-name temporary files there;
flush and `fsync` each; atomically rename each within that directory; write and
`fsync` `manifest.json` last as the sole commit marker; then `fsync` the directory and
parent. Existing target means a collision refusal and is never opened or modified.
Any directory without a valid final manifest is a typed incomplete bundle, never a
result. Define whether it is preserved for manual recovery or may be removed only by
an explicit recovery command. Freeze bounded stderr diagnostics for failures that
cannot be retained, and fault-inject every write/flush/rename/fsync boundary. An
equivalent stronger platform-specific no-replace protocol is acceptable if its
platform restriction is explicit.

### BF-4 — Resource and path authority remain caller-controlled or post hoc

The request includes `scope_and_limits`, while the proposal also says measured limits
must return for owner approval and enforcement must occur before expansion. It never
states that request-carried limits must exactly equal or be no greater than
build-owned approved ceilings. An oversized or hostile request cannot be allowed to
raise the parser's own limit. Nor can a complete JSON parser run before the wire-byte,
depth, duplicate-key and scalar checks it is supposed to protect.

Request and `--compare-to` path handling are also not defined for special files,
symlinks, concurrent mutation, huge files, deeply nested JSON, hostile Unicode names
or manifests that name paths outside the bundle. The repository's binding guidance
requires source payloads to be treated as untrusted and size/path/parsing limits to be
applied; local use does not remove that obligation.

**Required resolution:** make approved hard ceilings application/build authority,
not caller authority. If limits are echoed in a request, require exact equality or a
stricter caller value. Open each admitted file once, incrementally enforce wire bytes
before JSON construction, reject special files or explicitly document their
semantics, freeze maximum depth/nodes/scalars/string bytes before expansion, and use
only fixed bundle basenames with no manifest-controlled traversal. Define whether
symlinks are rejected or resolved once and retained by resolved identity. Measure the
complete command and retained forms before proposing the ceilings, as the proposal
already requires.

### BF-5 — Replay and command behavior do not yet form an acceptance contract

The bundle retains implementation and schema digests but does not say what bytes those
digests cover or how the matching build is recovered. `pyproject.toml` permits
`pydantic>=2.7`; therefore a Git commit and application version alone do not reproduce
the validation environment. The optional comparison verifies a prior manifest and
digests but does not expressly revalidate and recompute the prior world with a
compatible schema/profile before deriving changes. Internal hash agreement is not
semantic compatibility.

The exit contract omits usage errors and exact stdout/stderr behavior. It defers all
numeric codes and diagnostic ordering. Consequently it does not yet distinguish, at
the actual process boundary, malformed invocation, rejected request, a structurally
complete result containing unknown/no-feasible, output collision, incomplete retained
bundle and unexpected runtime failure. Section 10 describes semantic cases, but the
implementation slices require no explicit subprocess acceptance test and no named
retention/interruption/recovery test.

**Required resolution:** define the implementation commitment over application source,
schema, lower contract version/Git identity, Python and exact dependency versions;
either retain those bytes or state that the bundle is replay input requiring an
externally recoverable matching build. Revalidate and recompute a prior bundle before
comparison, and refuse incompatible versions/profiles. Freeze process exit classes,
stdout/stderr JSON or text contract, diagnostic precedence and bundle-presence rules.
Require at least one real `python -m applications.bounded_decision_workflow`
subprocess acceptance test from request file to committed manifest, plus collision,
oversize, interruption/fault-injection and incomplete-bundle recovery tests.

## 5. Result-meaning adjudication

Subject to BF-1 and BF-2, the proposed result structure can preserve the intended
meaning. A corrected result should make these headline statements unavoidable:

1. The current-condition section is a reconstructed classification **at the exact
   `as_of` cutoff**, with coverage and lower refusals. It is not the calculated next
   condition and not necessarily the physical condition at invocation time.
2. Every projection is a calculated one-step set under named supplied hypotheses,
   laws, effects, support and invariance assumptions. It is not a state-classification
   result and never enters a temporal observation contract.
3. Target relation is a property of one raw set and the supplied target; feasibility
   aggregates only the retained hypothesis set; selection minimizes only among
   guaranteed nominated actions under the supplied cost policy.
4. Ties are plural and canonically ordered. Unknown information cannot silently
   become false or infeasible. A bounded no-feasible result requires the corrected
   total policy rule and must always retain “in the supplied set.”
5. Reevaluation necessity is separate from result equality and from physical impact.

The proposal already contains most of these distinctions. The implementation must use
different field names/types and presentation labels for classification, raw
projection, target, feasibility and selection rather than a shared generic `status`
that a user could confuse.

## 6. End-to-end usefulness and minimality

At the named scale, one file-driven invocation can be useful. It can accept a complete
serialized public result plus explicit application premises, produce an inspectable
layered answer and retain it without a service. It does not require the user to
construct private backend objects: public result JSON, public validation and public
`ModelQueries(material.loaded())` are sufficient.

The release is nevertheless a deliberately narrow thermal/enclosure profile. That is
acceptable only if the documentation includes a complete canonical example request,
the exact supported hypothesis/action forms, a public-result serialization recipe,
the expected five-file bundle and a replay/compare example. “Source-agnostic” should
mean independent of connector or device source, not general behavior-law or domain
support. The command must reject any profile it does not implement.

The proposed slices are mostly well ordered, but slice 2 and slice 4 are too broad for
their answer-changing risks. Split slice 2 into raw projection and policy aggregation,
and split slice 4 into retention/recovery followed by resource/CLI delivery. This
creates reviewable seams without scaffolding a generic solver, plugin system or
enterprise deployment.

## 7. Owner-decision adjudication

| Proposed owner decision | Adjudication | Reason |
| --- | --- | --- |
| 1. Consumer and surface | **Approve in principle.** | A local module command and OS/filesystem trust boundary are proportionate. No authentication service or network deployment is needed. Exact CLI/path/error behavior remains blocked by BF-3–BF-5. |
| 2. Semantic scope | **Do not approve as written.** | The thermal one-step profile is appropriately narrow, but “joint/correlated” support, evidence binding, feasibility precedence and selection completeness are not closed semantics. |
| 3. Premise and policy authority | **Approve with correction.** | Application-local assumptions and owner policy are correctly separated from public facts. Conversion authority and admissible observed inputs must be relabelled/fixed under BF-1. |
| 4. Retention and comparison | **Do not approve as written.** | No-overwrite intent is correct, but the atomic commit, incomplete-bundle, failure-reporting, build-replay and prior-revalidation contracts are missing. |
| 5. Backend boundary | **Approve.** | Existing public contracts remain authoritative; maintained application composition is sufficient. Keep IN-001 and CI-001 open and unselected. |
| 6. Next authorization | **Approve only after correction.** | Separate implementation authorization and measured production limits are correct gates. The corrected schema, policy truth table, filesystem protocol, exits and required command/recovery tests must be reviewed first. |

Only decisions 1, 3 and 5 are currently approvable, and two of those require the
bounded corrections above. The six decisions therefore do not yet form one coherent
implementation authorization.

## 8. Minimal required corrections

The smallest correction set is:

1. Freeze the typed observed-input binding target, all exact membership/context/
   variable/unit/evidence/revision joins, and the application-assumption status of any
   conversion.
2. Restrict release-one uncertainty to the accepted Cartesian hard-support form, or
   fully specify one alternative joint-domain representation and its exact image-set
   semantics. Freeze nonempty/unique/subset cardinalities.
3. Publish a total feasibility and selection table, including mixed unknown/
   incompatible/inapplicable cases, missing costs, hidden cheaper/equal candidates,
   ties and the exact no-feasible condition.
4. Replace “atomically writes a directory” with one concrete exclusive, no-overwrite,
   manifest-last commit protocol and explicit incomplete-bundle recovery policy.
5. Make resource ceilings build-owned, define bounded read-once path/JSON admission,
   and freeze fixed-bundle filename and symlink/special-file behavior.
6. Define replay/build identity and prior-bundle compatibility/recomputation; state
   precisely what the bundle reproduces and what external bytes/environment it needs.
7. Freeze usage/refusal/unavailable/storage/runtime exit and presentation behavior,
   and require command-level, collision, retention-fault, interruption and recovery
   acceptance tests.
8. Split the calculation/policy and delivery/retention slices at the seams named in
   §6 and include a complete documented canonical request/output example.

These corrections require no implementation, experiment, production test, backend
change, authoritative fixture or ledger write, ADR, milestone or enterprise feature.

## 9. Original-objective contribution if corrected and delivered

A corrected maintained application would convert experimental evidence into genuine
production application capability for these bounded answers:

- objective 2: reconstruct and present one evidence-gated declared-state
  classification at an exact cutoff;
- objective 3: trace consequences under explicitly nominated hypotheses and supplied
  law/effect assumptions;
- objective 5: report reevaluation for a complete named decision inventory and
  separately calculate one-step conditional projected effects;
- objective 6: return every tied least-cost guaranteed action among one finite
  nominated set, or a correctly bounded unknown/no-feasible disposition; and
- objective 7: retain public declarations, observations, application assumptions,
  calculations, unknowns, inapplicability and refusals as distinct layers.

It would reuse objective 1's exact declared identity/membership and would deliver no
new objective-4 test selection. It must not claim empirical prediction accuracy,
source authenticity, causal truth, hypothesis/action generation, action execution,
safety, global impact, global minimality, multi-step reachability or general planning.
Those exclusions match the [project objectives](../../../CLAUDE.md), accepted
[one-step limits](2026-09-15-one-step-intervention-projection-owner-acceptance.md) and
[consolidation](2026-09-15-post-experiment-objective-and-architecture-consolidation.md).

## 10. Observations and readiness for final synthesis

### Non-blocking observations

- The proposal's refusal of ambient evidence and “latest policy” substitution is
  correct. A same-request digest gives deterministic identity and corruption
  detection, not independent authority; the result should keep saying so.
- A state `matches` conclusion can coexist with limitations about synchronization,
  physical currentness and completeness. Retaining condition coverage and lower
  refusals is essential.
- The application should import public symbols from package exports where available.
  Internal use of private derivation helpers by an owning public validator does not
  make the application's call private.
- No existing public contract should be weakened to accommodate request JSON. The
  application adapter owns strict preflight and then delegates reconstructed content
  to the public validators.
- A local actor label is useful declared provenance but is not authenticated identity.
  This is acceptable for the named OS-account consumer and must remain explicit.

### Readiness

The proposal is **not ready for final design approval or implementation
authorization**. It is ready for a narrow corrective synthesis using the eight items
in §8. The synthesis should preserve the local command, layered result, application
ownership, existing public-contract authority, original-objective limits and open
IN-001/CI-001 disposition. It should not add a service, plugin framework, generic
expression engine, authoritative application ledger or new backend abstraction.

No proposal edit, implementation, experiment, production test, fixture/ledger write,
milestone/ADR allocation, commit or history operation was performed by this review.
All pre-existing tracked and untracked artifacts are to remain byte-preserved; this
review alone is added and must remain untracked pending synthesis.

END OF BOUNDED DECISION WORKFLOW DELIVERY INDEPENDENT REVIEW
