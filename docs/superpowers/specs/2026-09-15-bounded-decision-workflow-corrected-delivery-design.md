# Corrected bounded decision-workflow delivery design

## 1. Decision, baseline and reviewer provenance

**Corrected design:** deliver one maintained local application, invoked through
`python -m applications.bounded_decision_workflow`, that evaluates one selected
public model/evidence result and one complete application-owned supplied-alternative
world. It reconstructs the current-condition answer, derives bounded one-step raw
outcomes, assesses a supplied target, evaluates robust feasibility, preserves tied
least-cost nominated actions, reports named-decision reevaluation, and retains a
verifiable local bundle.

The first release is intentionally one narrow thermal/enclosure profile. It is
source-agnostic with respect to acquisition and connectors; it is not a general
behavior language. Existing public backend contracts remain authoritative for
their own facts. No backend extension is justified by this design.

Verified on 2026-09-15: branch `brc-exp001`, HEAD
`ec027add0cb2dae5434c42f67454752eb93f7228`, exactly the expected checkpoint.
Tracked and staged state was clean. Sixty pre-existing untracked artifacts were
inventoried before this synthesis and are preserved.

The frozen [lead proposal](../proposals/2026-09-15-bounded-decision-workflow-delivery-proposal.md)
was read completely and matches SHA-256
`f48065f53f35a302d9cd1c4f3d66872bf367f0625da44bc499b3be97381b808f`.
The frozen [independent review](../reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md)
was read completely and matches SHA-256
`2bc917bee36a4e0db9b8b07b5a650455f98008e7d286a482c1127bdb8a7ddf29`.
The review was produced by separately staffed task
`/root/bounded_workflow_reviewer`, which had no proposal-authorship role. This is
independent adversarial design review, not independent empirical evidence.

Governing boundaries remain the [post-experiment consolidation](../reports/2026-09-15-post-experiment-objective-and-architecture-consolidation.md),
[CV deferral requirements](../reports/2026-09-10-cv001-deferral-owner-decision.md),
[accepted one-step design](2026-09-15-one-step-intervention-projection-corrected-design.md),
[one-step acceptance](../reports/2026-09-15-one-step-intervention-projection-owner-acceptance.md),
[project objectives](../../../CLAUDE.md) and [current architecture](../../../README.md).
Disposable experimental implementations remain evidence, not shipped code.

## 2. Finding-by-finding reconciliation

### 2.1 Five blocking findings

| Review finding | Corrected contract | Acceptance evidence |
| --- | --- | --- |
| **BF-1: an index/pointer was not an observation-admission rule.** | Section 5 defines one typed `T0` binding into a reached public `CandidateConstraintEvaluation`, exact joins, public decimal reparsing, no conversion, and unavailable-versus-refused outcomes. | `OBS-1` through `OBS-4` in §12. |
| **BF-2: joint support, feasibility and selection were non-total.** | Sections 6–8 restrict support to Cartesian closed rational hard bounds, reject correlations, fix all cardinalities and give total applicability, feasibility and selection precedence. | `NUM-1`, `UNC-1/2`, `POL-1` through `POL-5`. |
| **BF-3: “atomic directory” lacked a no-overwrite/recovery protocol.** | Section 9 defines exclusive directory creation, fixed temporary names, file-by-file same-directory publication, manifest-last completion, no automatic deletion and incomplete-bundle verification/replay recovery. It separates visibility from durability. | `RET-1` through `RET-5`, including injected interruption at every publication boundary. |
| **BF-4: caller-controlled limits and path ambiguity.** | Section 10 makes ceilings build-owned, admits only read-once regular files through no-symlink paths, bounds wire content before parsing, fixes bundle basenames and forbids manifest traversal. Values that need measurement stay gated. | `RES-1/2` and `PATH-1/2`. |
| **BF-5: replay/build/CLI behavior was not an acceptance contract.** | Section 11 freezes modes, stdout/stderr, exit classes, build compatibility, prior recomputation and replay versus verification. Section 12 requires real subprocess tests. | `CMD-1/2`, `REP-1/2` and `DET-1`. |

### 2.2 Eight required corrections

| Required correction | Resolution |
| --- | --- |
| **RC-1 typed observed-input binding** | §5 names the exact public terminal row and every model/evidence/context/unit/revision check; `OBS-1` is its positive control and `OBS-2/3` its negative twins. |
| **RC-2 close uncertainty/cardinality** | §6 admits exactly two hypothesis forms, four action forms and Cartesian closed rational intervals; empty/duplicate inventories and unsupported correlation are refused. |
| **RC-3 total feasibility/selection** | §§7–8 define ordered truth tables, mixed unknown/incompatible handling, relevant missing cost, hidden cheaper/equal actions, plural ties and the exact bounded no-feasible result. |
| **RC-4 concrete retention protocol** | §9 replaces directory-atomic wording with exclusive creation and manifest-last file-set publication; incomplete directories are never results and are never automatically removed. |
| **RC-5 build-owned resource/path authority** | §10 separates immutable approved ceilings from optional stricter request values and fixes file, symlink, traversal and read-once behavior. |
| **RC-6 replay/build identity** | §11 retains exact semantic input plus build/dependency identities, requires exact release-one compatibility and recomputes both prior and replayed results. It does not claim the bundle embeds an executable build. |
| **RC-7 process/error and command tests** | §11 fixes exit/stdout/stderr and bundle-presence behavior; §12 requires real command, collision, oversize, interruption, fault and recovery tests. |
| **RC-8 slice seams and complete example** | §13 splits raw calculation, policy, retention and command/resource work. §4 defines every input file/section and §12 `CMD-1` requires checked-in complete canonical example input/output documentation, with no placeholders or private construction. |

### 2.3 Five observations retained

1. No ambient evidence or “latest policy” substitution is allowed. Digests prove
   byte identity, not authority or truth.
2. A current-state `matches` result remains cutoff-relative and may carry coverage,
   synchronization or physical-currentness limitations.
3. Application code imports public package exports. An owning public validator may
   call its private derivation internally; the application does not.
4. Application preflight adapts strict JSON to existing contracts; no lower public
   contract is weakened or re-expressed.
5. The local actor label is declared provenance under an OS account, not
   authenticated identity.

### 2.4 Six owner-decision adjudications after correction

| Owner decision | Corrected disposition |
| --- | --- |
| 1. Consumer/surface | **Resolved:** one local owner/engineer and the module command in §11; no service or network identity. |
| 2. Semantic scope | **Corrected for approval:** exact public-value admission, fixed profile, Cartesian hard support and total policy in §§5–8 replace the rejected ambiguity. |
| 3. Premise/policy authority | **Corrected for approval:** application assumptions and owner policy remain distinct from public facts; release one performs no conversion. |
| 4. Retention/comparison | **Corrected for approval:** §§9–11 fix no-overwrite publication, incomplete recovery, build compatibility and complete prior recomputation. |
| 5. Backend boundary | **Resolved:** application composition only; IN-001 and CI-001 remain open and unselected. |
| 6. Next authorization | **Still gated:** design approval does not authorize implementation. Measured limits, exact dependency lock and slice scope must return at the final implementation-authorization gate. |

## 3. Precise public application boundary

The supported operation answers only:

> At the exact cutoff represented by this selected public result, does the named
> declared state match; and, under this complete synthetic application profile,
> what one-step sets, target relations, robust feasibility and tied minimum-cost
> choices follow for the four nominated actions?

The application consumes two explicit files and, optionally, one earlier bundle:

- `REQUEST.json`: the complete application world, target and policy;
- `SNAPSHOT.json`: one complete serialized public `StateClassificationResult`;
- `PRIOR_BUNDLE`: optional complete prior application bundle for review.

No file contains a store path, connector configuration or ambient lookup. The
caller obtains `SNAPSHOT.json` by serializing the public result returned by
[`StateClassificationQueries.state_classification`](../../../backend/state_classification/facade.py)
or an equivalent already-retained public result. The application accepts serialized
content, reconstructs it through the public
[`StateClassificationResult`](../../../backend/state_classification/contracts.py),
and uses its carried `state.material`; it does not require a private backend object
or open a model, temporal, binding or interpretation store.

The public reconstruction checks internal content integrity and authoritative
derivation from the carried lower results. It does not authenticate the caller,
prove that referenced raw source bytes still exist, verify a payload checksum
against unavailable bytes, prove the source was honest, or requery whether the
occurrence was truly latest in an external store. Those limitations are retained.

Application-owned content is never relabeled as model material. Each law,
hypothesis, parameter domain, effect, precondition, timing rule, applicability
claim, invariance, target, retained set and cost has an application-local ID,
edition, `epistemic_kind="synthetic_assumption"` or `"application_policy"`, issuer
assertion, basis and canonical commitment. These are not backend registrations,
observations or accepted causal facts.

### 3.1 Complete request form

`REQUEST.json` has exactly these top-level keys:

| Key | Required content |
| --- | --- |
| `schema_version` | Literal `bdw001.1`. |
| `workflow_profile` | Literal `hypothetical_enclosure_one_step.v1`. |
| `request_id` | One bounded local identifier; receipt identity only. |
| `application_identity` | Expected application semantic version and build-policy ID. |
| `actor_assertion` | Local actor label and purpose; declared, not authenticated. |
| `snapshot_commitment` | SHA-256 of canonical reconstructed `SNAPSHOT.json`. |
| `current_condition_question` | Exact state anchor, assertion context and UTC `as_of` that must equal the carried result. |
| `observed_input_binding` | The typed index/identity form in §5; exactly one binding for `T0`. |
| `premises` | Exact law, coordinates, hypotheses, commands, actions/effects, gates and provenance in §6. |
| `target_policy` | Target, retained hypotheses, feasibility rule, costs and selection rule in §§7–8. |
| `requested_limits` | Optional values no greater than every approved build ceiling; omission selects the build ceilings. |

Every nested field is required, including explicit `present|missing|unknown|
stale_reference` availability where allowed. Omission is schema invalid, not
scientific unknown. Extra fields, implicit defaults, duplicate keys, unsupported
profiles and noncanonical IDs are refused.

`SNAPSHOT.json` is the ordinary complete public serialization of one
`StateClassificationResult`; no application wrapper is embedded around it. A
release example must document how to serialize that public result, provide the full
canonical file without ellipses, and pair it with a full `REQUEST.json`, expected
result, trace and manifest. This example is a required implementation deliverable,
not an authoritative project fixture.

## 4. End-to-end workflow and result form

One `evaluate` invocation performs these steps in order:

1. safely open and bound all CLI paths under §10;
2. stream-preflight and capture immutable wire bytes once;
3. parse strict JSON and enforce build-owned schema/cardinality limits;
4. reconstruct the public snapshot through its owning public contract;
5. answer the current-condition question and execute §5 value admission;
6. validate the complete application profile without upgrading its authority;
7. derive raw projections under §6;
8. derive target relations, feasibility and selection under §§7–8;
9. if a prior bundle was supplied, verify, revalidate and recompute it, derive the
   complete changed-field set, and evaluate the fixed decision dependency map;
10. build the semantic result/trace under output limits; and
11. publish a completed or bounded-refusal bundle under §9.

A complete semantic result has separately typed sections:

- `current_condition`: exact cutoff, `matches|does_not_match|unavailable`, coverage,
  lower refusals and public-result commitment;
- `observed_value_admission`: admitted canonical `T0` and provenance, or one exact
  unavailable frontier;
- `raw_projections`: eight hypothesis/action rows with `ready|unknown|inapplicable`,
  effect source, operands, corner trace and exact closed interval or null;
- `target_relations`: eight distinct rows with
  `guaranteed|possible_not_guaranteed|incompatible|unknown|inapplicable`;
- `feasibility`: four action rows under the exact retained set;
- `selection`: one bounded finite-set disposition from §8;
- `reevaluation`: `not_applicable_no_prior` or all 22 named decisions with
  reevaluation disposition, equality-after-reevaluation and changed-value flags;
- `epistemic_manifest`: public declarations/observations, application assumptions,
  calculations, unused evidence, unknowns, inapplicability and refusals; and
- `commitments_and_limits`: all content/build/policy commitments and actual counts.

The current-condition answer is an observed-evidence classification at `as_of`.
It is not a projected state. The current-condition value neither selects `H_H` nor
gates projection in release one. Projection proceeds only if §5 admits `T0` and
all relevant application premises allow it. A projected `T1` is calculated and is
never written into a temporal observation or state-classification contract.

The fixed decision inventory is exactly one current-condition decision, eight raw
decisions, eight target decisions, four feasibility decisions and one selection
decision. Raw decisions exclude target/cost dependencies; target decisions depend
on their raw row and target; feasibility depends on retained target rows and gate
policy; selection depends on feasibility, nominated-set identity, relevant costs
and tie policy. Changed input can require reevaluation even when the recomputed
value remains equal.

## 5. Exact observed-value admission

### 5.1 Binding grammar

`observed_input_binding` contains only:

- literal role `T0`;
- `condition_index`, `constraint_evaluation_index` and
  `semantic_candidate_index`, each a bounded nonnegative integer;
- expected `constraint_anchor_id`, `variable_anchor_id` and
  `subject_entity_anchor_id`;
- expected exact public `QuantityKindReference`, `ObservationRoleReference` and
  [`UnitReference`](../../../backend/model_kernel/contracts.py) tokens; and
- application premises mapping those three exact tokens to this profile's
  temperature/measured-actual/unit roles, each with its own edition and issuer
  assertion.

There is no generic JSON pointer, caller numeric override or conversion field.
Release one performs no unit conversion. The application premise says only that
the exact public unit token is the equation's temperature role; the public token
itself asserts no dimension, scale, offset, SI traceability or convertibility.

### 5.2 Required public checks before arithmetic

The application first reconstructs the entire snapshot with
`StateClassificationResult.model_validate`. It then requires all of the following:

1. question state anchor, context and normalized UTC `as_of` exactly equal the
   result echo; the result's `state.material` is valid exact revision membership;
2. the named condition row exists at `condition_index`, names the expected
   constraint, has `declaration_alignment="exact_current"`, and its recorded
   evaluation/candidate indices exactly equal the binding;
3. the named `ConstraintEvaluationResult` exists, has the same cutoff and model
   revision, targets the expected registered variable and contains the candidate;
4. its public [`CandidateConstraintEvaluation`](../../../backend/constraint_evaluation/contracts.py)
   has `verdict="satisfied"|"violated"`, no not-evaluated reason and a non-null
   `observed_decimal`;
5. the parallel semantic/value/state candidate is the same indexed candidate, has
   a bound observation, `attachment="attached"`, bound resolution `status="bound"`
   to the expected variable, `evidence_consistency="consistent"`, numeric value
   shape and `declared_semantics_compatible`;
6. quantity-kind and observation-role comparisons are token-identical and name the
   binding's expected exact public tokens; unit comparison is
   `unit_identity_exact`; model specification, constraint expected semantics and
   positive source interpretation all name the binding's exact `UnitReference`;
7. variable registration owner and requested entity both equal the expected subject;
   source selector, occurrence locator and binding-resolution locator agree;
8. model, binding and interpretation revisions are the exact carried revisions;
   the occurrence `received_at` does not exceed `as_of`, carried staleness equals
   their difference, and the `LatestObservedState` is explicitly understood only
   as latest for that locator at that cutoff; and
9. public [`parse_observed_decimal`](../../../backend/constraint_evaluation/__init__.py)
   reparses the carried occurrence `value_json` as admitted and returns exactly the
   carried canonical `observed_decimal`.

Checks already guaranteed by authoritative reconstruction are deliberately
reasserted as admission predicates, not reimplemented lower derivations. The
application imports public result types and `parse_observed_decimal`; it never calls
private helpers or opens a lower store.

### 5.3 Unavailable, refused and authenticated meanings

- If the addressed row is coherent but public evaluation did not reach a decimal
  because observation, attachment, evidence, numeric shape or semantic support is
  unavailable, the workflow is structurally complete: value admission is
  `unavailable`, every raw/target/feasibility row and selection requiring `T0` is
  `unknown`, and exit is success.
- An out-of-range index, retargeted anchor, conflicting question echo, unit-token
  substitution, revision mismatch, forged result, stale exact reference or decimal
  disagreement refuses the request. No caller number repairs it.
- A source-unit lexeme may differ only when the carried positive interpretation
  still establishes the exact unit identity. The original lexeme and interpretation
  provenance remain disclosed. No conversion is performed.
- The occurrence, IDs, raw-record ID and payload checksum are carried evidence.
  Without the external source/raw bytes and authority, the application cannot
  authenticate them. It validates carried-result integrity and arithmetic input,
  not real-world truth or actual external currentness.

## 6. Projection, uncertainty and applicability semantics

### 6.1 Fixed profile and numbers

The sole law is:

`T1 = T0 + alpha*h - gamma*f - beta*(T0-A)`.

All numeric application values are exact rationals encoded as signed integer
numerator and positive integer denominator. Negative zero is forbidden and fractions
are reduced. Each coordinate support is one nonempty closed interval `[lower,upper]`
with `lower <= upper`; a singleton has equal endpoints. Arithmetic is unbounded
integer rational arithmetic subject to build resource limits. Output intervals are
closed, exact and reduced. There is no floating point, tolerance, rounding,
clipping, probability or confidence interpretation.

The complete support premise is literal `cartesian_hard_support.v1`: every tuple in
the Cartesian product of the five coordinate intervals `T0,A,alpha,gamma,beta` is
admitted. Repeated uses of a named coordinate use the same value. No other
correlation, dependence constraint, disconnected set or distribution is supported;
requesting one is an unsupported-profile refusal. The law is multi-affine on this
box, so the exact scalar image is the closed interval whose endpoints are the
minimum and maximum over all distinct endpoint corners. Singleton endpoints are
enumerated once.

`T0` support is constructed only as the singleton admitted in §5; `REQUEST.json`
has no caller-supplied `T0` numeric field. `A`, `alpha`, `gamma` and `beta` are
explicit synthetic hard-support assumptions. Missing/unknown support for any law
coordinate makes every raw row unknown; no nominal value substitutes. A malformed,
empty, reversed or stale interval refuses the request.

The hypothesis inventory is exactly the two unique IDs/forms `H_H` and `H_F`; the
action inventory is exactly the four unique IDs/forms `a0`, `aH`, `aF`, `aHF`, in
canonical ID order. The retained hypothesis set is a nonempty unique subset of the
two. Missing, extra or duplicate IDs are refused. Commands are supplied assumptions,
not execution evidence.

The request's complete `premises` object has this closed content; every row has the
common ID/edition/epistemic/provenance/availability envelope from §3:

| Premise group | Exact release-one value/form |
| --- | --- |
| Law/support | Literal law and edition above; `cartesian_hard_support.v1`; one modeled step; closed endpoints. |
| Coordinates | `A`, `alpha`, `gamma`, `beta` each has one exact rational interval and profile unit role; `T0` is absent because §5 supplies it. |
| Commands | `u_h` and `u_f`, each exactly integer `0` or `1`; these are assumed command states only. |
| `H_H` | Before action, `h=1` and `f=u_f`. |
| `H_F` | Before action, `h=u_h` and `f=0`. |
| `a0` / `E-a0` | Identity effect; requires global applicability; all law inputs invariant for the step. |
| `aH` / `E-aH` | Before-step assignment `h:=0`; isolation-capability and synthetic-permission preconditions; `T0,A,f,beta,gamma` and law form invariant. |
| `aF` / `E-aF` | Before-step assignment `f:=1`; restoration-capability and synthetic-permission preconditions; `T0,A,h,alpha,beta` and law form invariant. |
| `aHF` | Canonical `E-aH` then `E-aF`; both preconditions; effects target distinct variables; `T0,A,beta` and law form invariant. |
| Global applicability | Three-way present true/false or missing/unknown support for this configuration, law edition and one step; stale edition is invalid. |

No other operator, assignment target, action composition, hypothesis mapping or
effect order is admitted. Each action cites the exact effect edition, before-step
timing, precondition, global applicability and invariants in this table. Topology
and dependency edges never provide an effect.

### 6.2 Total gate precedence per action

Edition/identity/schema conflicts are whole-request refusals before semantic gates.
For a structurally valid action, apply this precedence:

1. explicit false global model applicability makes all action rows inapplicable and
   selection `inapplicable_for_declared_model`;
2. explicit false action precondition, timing applicability or required invariance
   makes that action's raw/target/feasibility rows inapplicable;
3. otherwise any missing/unknown global applicability, action precondition, timing,
   invariance, law/support declaration, required command, effect body or hypothesis
   mapping makes affected raw rows unknown;
4. otherwise apply the effect once at step start, hold invariants, and evaluate the
   law once.

An explicit false dominates missing/unknown in another gate because it already
proves the action cannot be applied in the declared step. Missing effect support is
unknown; an exact effect edition mismatch is refusal. No observation after the
hypothetical step changes a premise or proves the effect.

Overlapping or identical raw outcome intervals remain separate hypothesis/action
rows. They do not select, eliminate or merge hypotheses and do not establish cause.

## 7. Target relation and feasibility truth tables

The target is one exact closed rational interval with availability. Malformed,
reversed or stale target content refuses. Missing/unknown target support produces
unknown target rows without changing raw rows.

For a ready raw interval `Y` and present target `G`:

| Exact set relation | Target result |
| --- | --- |
| `Y` is a subset of `G`, including equal endpoints | `guaranteed` |
| `Y` intersects `G` but is not a subset | `possible_not_guaranteed` |
| `Y` and `G` are disjoint | `incompatible` |

An inapplicable raw row gives `inapplicable` even if target support is absent;
otherwise unknown raw or target support gives `unknown`. Endpoint contact counts as
intersection. No coarse decoder exists.

Feasibility is robust feasibility across exactly the retained hypothesis rows for
one action. Apply this total precedence after structural refusal:

| Retained target rows / action gate | Feasibility |
| --- | --- |
| Action/global gate explicitly false | `inapplicable` |
| Any retained row `unknown`, with no explicit false gate | `unknown` |
| All retained rows ready and all `guaranteed` | `guaranteed` |
| All retained rows ready, none `incompatible`, at least one `possible_not_guaranteed` | `possible_not_guaranteed` |
| All retained rows ready and at least one `incompatible` | `incompatible` |

Thus mixed `unknown` plus `incompatible` is conservatively `unknown`: complete
support is required for a bounded incompatibility conclusion. Empty retained sets
are refused, not vacuously feasible.

## 8. Cost and selection truth table

Each nominated action has exactly one explicit cost entry whose availability is
`present|missing|unknown|stale_reference`. Present costs are nonnegative exact
rationals in one declared cost token and exact policy edition. Negative, malformed,
duplicate, incomparable-token or stale entries refuse. Missing/unknown is retained
as incomplete policy information; no zero/default is supplied.

Selection considers only actions with feasibility `guaranteed`. Let `E` be those
actions and `U` actions with feasibility `unknown`.

1. If global model applicability is false, return
   `inapplicable_for_declared_model`.
2. If `E` is empty and `U` is nonempty, return `unknown`.
3. If `E` and `U` are empty, return `no_feasible_action_in_supplied_set`. This means
   no guaranteed-feasible action among the four nominated actions under this robust
   policy; it does not mean no plan exists. `possible_not_guaranteed`, incompatible
   and inapplicable actions are complete non-eligible outcomes.
4. If any action in `E` has missing/unknown cost, return `unknown`.
5. Otherwise let `m` be the minimum known cost in `E`. For every action in `U`, a
   missing/unknown cost or known cost `<= m` can conceal a cheaper or tied eligible
   action, so return `unknown`; a known cost `> m` cannot affect the minimum.
6. Otherwise return `selected_from_supplied_set`, `minimum_cost=m`, and every action
   in `E` with cost `m`, canonically ordered. Ties are never collapsed.

Missing cost on a complete non-eligible action (`possible_not_guaranteed`,
`incompatible` or `inapplicable`) cannot affect selection and is disclosed but
ignored. Cost never affects raw prediction, target relation or feasibility. A
cost-only change requires selection reevaluation even when the selected set remains
equal.

## 9. Retention, publication and recovery contract

### 9.1 Supported guarantee boundary

Release one supports CPython 3.13 on Linux and local ext4 or XFS filesystems that
provide exclusive directory creation, `O_NOFOLLOW`, same-directory atomic rename,
regular-file `fsync` and directory `fsync`. Preparation must exercise and record
these primitives on each approved filesystem. Windows, WSL DrvFS, NFS, SMB, FUSE,
removable FAT/NTFS and any filesystem without those verified semantics are refused
as unsupported; no network storage guarantee is implied.

The guarantee has two layers:

- **atomic complete visibility:** a directory is a completed bundle only after a
  valid `manifest.json` appears as the final same-directory rename. Before that the
  directory may be visible but is explicitly incomplete;
- **best-effort crash durability on supported filesystems:** exit 0 is emitted only
  after every file, the bundle directory and its parent have successfully returned
  from `fsync`. Filesystem, kernel, mount, storage-controller and hardware behavior
  can still defeat power-loss durability; the bundle does not authenticate those
  layers.

If manifest publication succeeds but a later directory/parent `fsync` fails, the
command returns retention failure and reports `complete_visible_durability_unknown`.
That is a complete visible file set, not a partial result or a durability claim.

### 9.2 Exclusive no-overwrite publication

Semantic computation and bounded serialization finish before output creation. The
application opens the already-existing output parent under §10 and creates the exact
final basename once with exclusive `mkdirat`, mode `0700`. If it already exists—file,
directory, symlink or concurrent winner—the command returns collision and never
opens, changes, removes or replaces it.

Inside the exclusively created directory, the application uses only fixed basenames.
A completed result bundle contains:

`request.json`, `snapshot.json`, `resolved-input.json`, `result.json`, `trace.json`,
`build.json`, `manifest.json`.

Every retained JSON file is canonical compact UTF-8 with lexicographically sorted
mapping keys, schema-defined array order and no trailing newline. Run-specific fields
are excluded from semantic result/trace files as specified in §11.

For each non-manifest file it creates a fixed hidden temporary basename with
`O_CREAT|O_EXCL|O_NOFOLLOW` and mode `0600`, writes bounded canonical bytes, flushes
and `fsync`s the descriptor, closes it, then renames it to its final basename within
the same directory. `manifest.json` contains the exact fixed file inventory, byte
counts and SHA-256 digests. It is written/fsynced under its temporary name and
renamed last. The directory and parent are then fsynced before success is reported.

A bounded input/integrity/resource refusal may publish a smaller refusal bundle with
only `diagnostic.json`, `input-metadata.json`, `build.json`, `manifest.json` under
the same protocol. For an oversized file that was not fully read, metadata records
only `wire_bytes_at_least=ceiling+1` and no full-input digest. Usage and unsafe-path/
collision failures occur before safe output ownership and therefore produce no
bundle.

### 9.3 Interruption, cleanup and recovery

No directory lacking a valid final manifest is presented as a decision or refusal
bundle. On a write, rename, flush, `fsync`, signal or process failure before manifest,
descriptors are closed where possible and the exclusively created incomplete
directory is preserved. There is no automatic deletion, resume or overwrite; retry
must use a new basename. This avoids deleting evidence after an ambiguous fault.

`verify --bundle` treats a missing/invalid manifest as `incomplete_bundle`, reports
the recognized fixed files and safe digests it can bound, and never promotes or
repairs them. The owner may inspect and explicitly remove an incomplete directory
outside the application. If a complete-visible bundle has uncertain durability,
`verify` can establish its current byte integrity and `replay` can publish a fresh
bundle at a new path; neither proves past crash durability. An incomplete bundle's
retained request/snapshot may be manually resubmitted, but its partial result/trace
is never trusted.

Fault injection must cover each create/write/flush/file-fsync/rename/manifest/
directory-fsync/parent-fsync boundary. Concurrent publishers to one basename must
yield exactly one owner and one collision without replacement.

## 10. Path and resource controls

### 10.1 Path authority

Only CLI arguments supply filesystem paths. JSON and manifests contain no usable
path references. Input, snapshot, prior-bundle and output-parent paths are opened
component by component relative to directory descriptors; `.`/`..`, symlinked
components and final symlinks are rejected. Inputs must be regular files; prior
bundle and output parent must be regular directories. FIFOs, sockets, devices and
other special files are refused before read. Hard-link identity is recorded but is
not authenticated.

The final output basename must match `[a-z0-9][a-z0-9._-]{0,127}`, be one path
segment and not exist. Bundle readers use only the fixed basename set in §9; a
manifest with extra, duplicate, absolute or traversal names is invalid. Files are
opened once with `O_NOFOLLOW`; pre/post `fstat` device, inode, size and modification
metadata must remain equal while bounded bytes are captured, otherwise detected
concurrent mutation is refused. Subsequent parsing and hashing use only the captured
byte sequence, which becomes the invocation's input authority. Same-account mutation
engineered to evade metadata checks is outside this local trust model and is not
authenticated by the application.

### 10.2 Build-owned ceilings and enforcement order

The release contains an owner-approved immutable limit policy identified in
`build.json`. Input content cannot raise it. `requested_limits`, when present, must
equal or tighten every build ceiling; a missing dimension or higher value is
refused.

Enforcement order is:

1. safe file type/path and build-owned wire byte limit, reading no more than
   `limit+1`;
2. bounded streaming UTF-8/JSON lexical preflight for nesting depth, token/string
   bytes, node/scalar/key counts and duplicate keys before building the object;
3. strict schema and cardinality validation;
4. reference/index counts before public reconstruction;
5. reconstructed public-result/model-record/evidence-candidate and resolution-charge
   counts;
6. hypotheses/actions/effects, corners, decisions, changed paths and trace-work
   counts before calculation; and
7. incremental result/trace serialization with output byte/node/depth/row limits
   before output-directory creation.

The streaming preflight is application input hardening, not duplicated lower
semantic validation. Public content is still reconstructed by its owning contract.
Every refusal is bounded and contains no partial semantic conclusion.

No numeric ceiling is justified in this design. Preparation must measure complete
baseline/adverse/refusal/replay inputs and outputs separately for request and
snapshot wire bytes, prior bundle bytes, resolved bytes, nodes, depth, keys/scalars,
maximum string, references, model records/results, evidence candidates, reconstruction
charges, exact arithmetic digits, corner evaluations, 22 decision rows, dependency
paths, result/trace rows, refusal envelopes and total retention bytes. It must also
measure elapsed time, peak memory, filesystem operations and two-process collision
behavior on each supported filesystem. Fixed semantic cardinalities—two hypotheses,
four actions, eight raw rows, eight target rows, four feasibility rows and 22 review
decisions—are contracts, not measured maxima.

Measured maxima, explicit headroom, exact Python/dependency versions and proposed
hard ceilings return for owner approval before implementation execution or release.
No prior experiment's budgets are inherited.

## 11. CLI, diagnostics, verification and replay

### 11.1 Exact modes

```text
python -m applications.bounded_decision_workflow evaluate \
  --request REQUEST.json --snapshot SNAPSHOT.json \
  --output-dir OUTPUT_DIR [--compare-to PRIOR_BUNDLE]

python -m applications.bounded_decision_workflow verify \
  --bundle BUNDLE

python -m applications.bounded_decision_workflow replay \
  --bundle BUNDLE --output-dir NEW_OUTPUT_DIR
```

`evaluate` is the complete useful workflow. `verify` is read-only byte/inventory
checking and does not recompute conclusions. `replay` first verifies and then
reconstructs public content and recomputes current condition, value admission, all
projections, target relations, feasibility, selection and any prior-world review;
it publishes a new bundle and compares the new semantic result/trace commitments
with the retained ones.

### 11.2 Process contract

| Exit | Meaning | stdout | stderr / bundle |
| ---: | --- | --- | --- |
| `0` | Completed evaluation, successful verification or exact replay. A complete evaluation may contain unavailable, unknown, inapplicable or `no_feasible_action_in_supplied_set`. | Exactly one bounded compact JSON line naming operation, completed bundle/result commitment and headline semantic disposition; verify names integrity state. | Empty; evaluation/replay bundle has valid manifest and fsync sequence returned. |
| `2` | CLI usage error. | Empty. | One bounded compact JSON diagnostic line; no output directory is created. |
| `3` | Input/integrity/profile/build/prior/replay rejection. | Empty. | One bounded JSON diagnostic; a manifest-valid refusal bundle exists only if safe exclusive output publication succeeded. |
| `4` | Build-owned resource refusal. | Empty. | One bounded JSON diagnostic; optional bounded refusal bundle as above. |
| `5` | Unsafe path, unsupported filesystem or output collision. | Empty. | One bounded JSON diagnostic; existing target is untouched and no new bundle is promised. |
| `6` | Retention I/O or durability-sequence failure. | Empty. | One bounded JSON diagnostic with bundle state `absent|incomplete|complete_visible_durability_unknown`. |
| `7` | Unexpected internal failure. | Empty. | One bounded JSON diagnostic; any directory without valid manifest remains incomplete. |

Application diagnostics have exact code, stage, target, message key, retry class and
bundle state. Precedence is: usage; path/file safety; wire resource; lexical/schema;
commitment/public reconstruction; profile/cardinality/edition; semantic calculation;
output resource; collision; retention I/O; internal failure. Lower typed codes are
retained as causes, not translated into staleness or policy failure. Preparation
freezes the finite code catalogue and maximum diagnostic size without changing this
ordering.

### 11.3 Build identity and replay boundary

`build.json` records the clean Git commit, application semantic version, SHA-256 and
relative path of every application source/schema file, SHA-256 of each directly used
public contract module, implementation/profile/limit-policy IDs, CPython
implementation and exact version, exact installed dependency names/versions and the
committed dependency-lock digest. Platform/filesystem/inode/time details are
run-specific and belong only in `manifest.json`. Release one
requires exact equality of schema, profile, application semantic version, public
contract identities, Python minor and dependency lock; it defines no migration.

The bundle retains all semantic inputs in canonical `resolved-input.json`, including
the complete prior world when comparison was requested. It does not embed Python,
dependencies, application source, the Git repository or unavailable raw source
payload bytes. Therefore:

- `verify` can check current retained byte integrity without an executable match;
- `replay` requires an externally recoverable checkout and environment whose build
  identity exactly matches; otherwise it returns `replay_build_unavailable`/exit 3;
- release acceptance must prove a clean checkout plus exact dependency lock can
  recreate the matching build; and
- replay validates carried evidence and recomputes conditional mathematics. It does
  not reacquire/authenticate a source or establish empirical truth.

For `--compare-to`, the application verifies the prior manifest, requires exact
release-one compatibility, reconstructs and recomputes the prior result from its
retained resolved input, checks the retained result/trace commitments, then compares
complete prior and proposed worlds. Digest agreement alone is insufficient.

Semantic `result.json` and `trace.json` exclude invocation timestamp, output path,
process ID, inode and host metadata. Identical semantic inputs/build produce identical
semantic bytes. `manifest.json` contains run-specific time and filesystem metadata
and is expected to differ.

## 12. Command-level acceptance matrix and finding trace

Every test invokes the real module command in a subprocess unless marked as a
lower application-service unit test. Complete examples use only public serialization
recipes; no private constructors, deleted drivers or oracle files are runtime input.
An independent exact-rational/policy oracle supplies expected semantics and shares
only the approved premises and canonical encoding rules.

| ID | Required case and exact acceptance | Findings/corrections |
| --- | --- | --- |
| `CMD-1` | Full documented baseline request plus full public snapshot runs through `evaluate`, publishes all seven files, reconstructs current `D-HOT=matches`, admits observed `T0=40`, derives raw HH `42,32,42,32` and HF `36,36,32,32`, selects `{aH}` at cost 2, and is inspectable without private assembly. Documentation contains literal canonical input/output/trace examples with no ellipses. | RC-8, BF-5 |
| `CMD-2` | Usage error, lower input refusal, valid unavailable result, bounded no-feasible result, collision and retention failure each produce the exact exit/stdout/stderr/bundle behavior in §11. | BF-5, RC-7 |
| `OBS-1` | Reached public candidate passes every §5 join; reparsed `value_json` exactly equals carried decimal and all source/public/application provenance stays distinct. | BF-1, RC-1 |
| `OBS-2` | Nearest coherent twins for absent observation, unattached candidate, inconsistent evidence, nonnumeric value and semantic/unit incompatibility produce valid unavailable results and no caller-value fallback. | BF-1, observations 1–2 |
| `OBS-3` | Retargeted condition/candidate, wrong entity/variable/context/cutoff/revision/unit token, index mismatch, forged result and decimal disagreement refuse before arithmetic. | BF-1, RC-1 |
| `OBS-4` | A caller conversion is refused as unsupported; differing source lexeme with exact positive interpreted unit remains admitted and discloses that interpretation. Missing raw source bytes prevent authentication claims but not carried-result integrity checking. | BF-1, observation 3 |
| `NUM-1` | Exact rational endpoints, singleton coordinates, endpoint target contact and all fixed-law corners match an independent rational oracle; floats, reversed intervals, unsupported correlations and oversized rationals refuse. | BF-2, RC-2 |
| `UNC-1` | Complete beta `[1/10,3/10]` yields accepted closed ranges and `possible_not_guaranteed` where expected; overlapping hypothesis results remain distinct. | BF-2 |
| `UNC-2` | Missing/unknown coordinate support yields raw/target/feasibility/selection unknown with no nominal fallback; stale support refuses. | BF-2, RC-2 |
| `POL-1` | Exhaust every feasibility table row, including mixed unknown plus incompatible => unknown and false gate dominating a separate unknown gate => inapplicable. | BF-2, RC-3 |
| `POL-2` | True, false, missing and unknown global/action precondition, timing, effect and invariance twins follow §6 precedence; dependency never supplies effect. | BF-2 |
| `POL-3` | Baseline feasible action and cost-only `aH:2->5` retain unchanged physics and plural `{aH,aHF}` tie; selection alone reevaluates. | BF-2, RC-3 |
| `POL-4` | Target `[31,33]->[25,27]` leaves all eight raw rows unchanged, reevaluates all eight target/four feasibility/selection decisions, and returns bounded no-feasible. | BF-2, RC-3 |
| `POL-5` | Unknown feasibility at lower/equal/higher known cost, missing cost on guaranteed/unknown/noneligible actions, multiple guaranteed ties and no guaranteed/unknown actions exercise every §8 branch. | BF-2, RC-3 |
| `REV-1` | Full prior bundle is verified, reconstructed and recomputed before target-only/cost-only review; incompatible build/profile/prior result refuses. Required reevaluation remains distinct from equal or changed output. | BF-5, RC-6 |
| `RES-1` | Request, snapshot and prior bundle at each measured ceiling are accepted; `+1` wire byte, depth, node, scalar, string, reference, reconstruction, corner, result and trace cases refuse at the declared stage without partial conclusions. | BF-4, RC-5 |
| `RES-2` | Request limits equal to or stricter than build limits work; any omitted/higher requested dimension refuses and cannot relax preflight. Peak time/memory stays within later-approved measured bounds. | BF-4 |
| `PATH-1` | Symlinked component/final file, traversal, special file, invalid basename, extra manifest name and detected pre/post metadata mutation refuse after bounded read-once checks; parsing uses only captured bytes. | BF-4, RC-5 |
| `PATH-2` | Unsupported filesystem refuses; approved ext4/XFS runs record and pass the required primitive probe. | BF-3/4 |
| `RET-1` | Pre-existing file/directory/symlink output target is unchanged and returns collision. | BF-3, RC-4 |
| `RET-2` | Two simultaneous publishers to one basename yield exactly one manifest-valid winner and one collision; winner bytes are uncorrupted. | BF-3/4 |
| `RET-3` | Inject failure/interruption at every create/write/flush/file-fsync/rename/manifest boundary: no manifest means incomplete and never a presented decision. | BF-3, RC-4/7 |
| `RET-4` | Inject directory/parent-fsync failure after manifest: exit 6 reports complete-visible/durability-unknown; no exit-0 durability claim is emitted. | BF-3 |
| `RET-5` | `verify` classifies incomplete directories without promotion or deletion; valid uncertain bundle verifies current integrity; replay republishes to a new exclusive path. | BF-3, RC-4/6 |
| `REP-1` | Exact matching build replays every semantic computation and matches result/trace; changed/missing source, contract, Python or lock identity refuses recomputation while byte verification remains available. | BF-5, RC-6 |
| `REP-2` | Clean checkout plus exact lock recreates matching build; absent external build is honestly `replay_build_unavailable`, not claimed reproducible. | BF-5, RC-6 |
| `DET-1` | Same semantic inputs across approved construction orders, hash seeds, roots and two output times have identical `result.json`/`trace.json`; manifests differ only in enumerated run metadata. | BF-5, RC-7 |

Acceptance also runs focused existing public-contract and isolation tests. It does
not rerun physical acquisition or treat synthetic expectations as empirical evidence.
Preparation must map every test to the exact diagnostic and resource policy before
implementation execution is approved.

## 13. Bounded implementation slices

No slice is authorized by this design. If separately approved, implement in these
reviewable units:

1. **Input/public admission:** strict wire preflight, request contracts, public
   snapshot reconstruction, §5 binding and complete canonical example.
2. **Raw projection only:** fixed rational law/effects, Cartesian corners,
   applicability gates and raw trace; no target/cost code.
3. **Policy only:** target relations, total feasibility and total selection with an
   independent oracle; no filesystem code.
4. **Decision review:** fixed 22-decision dependency map and complete prior/proposed
   comparison, including target-only and cost-only controls.
5. **Retention/recovery:** exclusive no-overwrite manifest-last publisher, verifier,
   fault injection and supported-filesystem probe; no CLI presentation yet.
6. **Resource/CLI delivery:** measured build ceilings, modes, diagnostic/exit
   contract, replay compatibility and real subprocess tests.
7. **Release gate:** inspect exact source/test/document scope, dependency lock,
   measured policy, recovery evidence and clean-checkout reproduction before
   production acceptance.

New maintained code belongs only in `applications/bounded_decision_workflow/` and
focused `tests/applications/bounded_decision_workflow/`. Public backend imports come
from package exports. Experimental archive source is not copied or imported. No
generic expression engine, plugin framework, service, UI, authentication system,
new store or application ledger is included.

## 14. Objective contribution, backend isolation and limits

If implemented and accepted, this becomes maintained production **application**
capability for bounded readings:

| Objective | Delivered bounded answer | Still outside delivery |
| --- | --- | --- |
| 1. Identity/connectivity | Exact selected public membership and cited declarations reused. | Physical completeness, mechanism or wiring truth. |
| 2. Current state | One reconstructed declared-state classification at exact cutoff plus admitted observation. | Complete physical state, authenticated source or present-time truth. |
| 3. Explanation | Consequences under two nominated hypotheses and explicit assumed effects. | Hypothesis generation, causal identification and empirical adequacy. |
| 4. Next test | No new answer. | Candidate-test generation/ranking remains separate. |
| 5. Change impact | Named-decision reevaluation and distinct conditional one-step projection. | Complete blast radius, actual effects and multi-step propagation. |
| 6. Smallest valid change | All tied least-cost guaranteed actions among four supplied actions. | Action generation, safety authorization, global minimality and multi-step planning. |
| 7. Epistemic status | Public facts, carried observations, assumptions, policy, calculations, unknown, inapplicable and refused remain separate and retained. | Truth authentication or universal epistemic ontology. |

The application does not duplicate lower authority: it reconstructs the public
result, checks its suitability for one application role and calls public numeric
parsing. No hidden store is owned. Acquisition stays outside the workflow.

IN-001 remains open and unselected. A shared directed influence declaration could
be justified only by a concrete model-owned identity/lifecycle/replay need; it would
still not supply this effect equation, timing, magnitude, uncertainty or causal
truth. CI-001 remains open and unselected. It could be justified only if application
decision inventories fail a concrete completeness, scale, lifecycle or cross-consumer
integrity requirement. This workflow demonstrates neither need.

Physical acquisition, empirical accuracy, causal truth, generated hypotheses/tests/
actions, physical execution, multi-step reachability and global planning remain
outside the claim. Source-agnostic delivery does not make evidence source-authentic.

## 15. Remaining owner decisions and next gate

Corrected-design approval is requested for:

1. the exact two-file public/application boundary and no-conversion observed-value
   admission in §§3–5;
2. the fixed equation, Cartesian hard-support meaning, two hypotheses, four actions
   and total target/feasibility/selection policy in §§6–8;
3. the Linux local ext4/XFS, exclusive no-overwrite, manifest-last, incomplete-
   preservation and limited crash-durability contract in §§9–10;
4. the exact command modes, exit/presentation meanings and external-build replay
   boundary in §11; and
5. the acceptance matrix and separately reviewable slices in §§12–13.

Decision 6 remains the final implementation-authorization gate. Before that gate,
preparation must return the exact dependency lock, complete literal example,
diagnostic catalogue, measurements, proposed hard limits/headroom, supported-
filesystem probe evidence and exact implementation/test scope. A changed semantic
premise, wider profile, different platform guarantee or backend ownership claim
requires renewed design approval; measured numeric caps consistent with §10 do not.

No implementation, experiment, production test, fixture/ledger change, milestone,
ADR, commit or history operation occurred. Only this corrected design is created and
remains untracked. Stop for corrected-design approval.

END OF BOUNDED DECISION WORKFLOW CORRECTED DELIVERY DESIGN
