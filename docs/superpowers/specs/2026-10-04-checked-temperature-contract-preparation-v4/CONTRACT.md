# Checked-temperature contract preparation, successor v4 (`bdw.checked-temperature.v1`)

v4 = the v3 text below, unchanged, plus §12, which **supersedes the clauses it cites**. v3 (`MANIFEST.json` `1a9eccbd…5572`) is preserved byte-for-byte.

Date: 2026-10-04, Europe/Amsterdam. Status: **documentation-only preparation for
owner evaluation**. This is not an executable contract freeze, implementation or
test evidence. Passing JSON parsing and hash checks does not establish executable
readiness.

## 0. Inputs and predecessor

| Input | SHA-256 |
|---|---|
| Corrected design v2 | `68da70f2cc64d837e45e8534da0eba7d95d94686ab40806099c5f06a0e4a02da` (unchanged) |
| Focused confirmation v2 | `f0259702892f52f3e61dda3f665bb6c31298e276f9fdd86b10cd9e685f8fcc55` (unchanged) |
| Original package `…-contract-preparation/MANIFEST.json` | `c3de4cb9d5868454e8d666267d9dd9cf58f33d69500065c1f648005bf3da48c2` (preserved unchanged) |
| Predecessor v2 `…-contract-preparation-v2/MANIFEST.json` | `e7dbccec4c7fc65947cd1847f36b6306daed10597399bec8106a82660c2b0811` (preserved unchanged) |
| Checkpoint | `2f0afbd368105b99f0b8548ffece107918386e3d` |

*Design §n* refers to the corrected design v2. The following are **FIXED** and
not reopened:

- the score domain (design §4);
- item-level review precedence, condition axes and governing-state precedence
  (design §5);
- the evaluate/verify/replay boundary (design §6).

`CORRECTIONS.md` maps every v3 change from v2 (correction A: acyclic authority; correction B: closure roots and prior carriage). The v2 map from the original package stays at `../2026-10-04-checked-temperature-contract-preparation-v2/CORRECTIONS.md`. The disclosed
decoder discrepancy (the committed P case splits at 50; the proposed edition
splits at 56 and 59, taken from the experiment model) is unchanged.

## 1. Record identity, provenance and typed references

### 1.1 Record classes (`schemas.json#/record_classes`)

| Class | Kinds | Identity | Provenance |
|---|---|---|---|
| Authored | explanation, model, interpretation-plan, condition-declaration, evidence-item, evidence-review, policy, request, authority, execution-target, adoption | `(schema, id, revision)` unique in a closure; canonical digest. `predecessor` is null for revision 1. Otherwise it references the same schema and id at revision − 1, and that predecessor must be present in the closure (`PREDECESSOR_INVALID`). Revision ≤ 4. | Mandatory `provenance` attestation. Role from the kind's `x-allowed-roles` (`ROLE_MISMATCH`). `authenticated: false` always. |
| Derived-canonical | `ct.claim.v1` | digest only | none; fully determined by request inputs |
| Computed | derivation, applicability, selection, reassessment, retained-selection, build, invocation, trace, closure, bundle-manifest | digest only; each bundle file is exactly its record's canonical bytes, so file SHA-256 = record digest | produced only by the application, with `build` reference where applicable; a reassessment closure carries the prior bundle's computed records as members (§7.3) |
| Opaque / legacy-validated | `ct.evidence-content` (opaque bytes), `nm.evidence.v1` (public evidence, validated by the existing public-evidence validator semantics) | digest of bytes | carried by the referencing record |

### 1.2 Typed references

A typed reference is `{kind, sha256}`.

- `kind` is one of the 24 `typed_reference_kinds` (v3 adds `ct.execution-target.v1`).
- Each reference field restricts it through `x-target`; a different kind refuses
  with `REFERENCE_KIND_MISMATCH`.
- `sha256` is the SHA-256 of the target's canonical bytes (or raw bytes for
  opaque content).
- A referenced digest absent from the closure refuses with `REFERENCE_MISSING`.
  This covers a missing policy, model revision or predecessor.
- A closure member that is not reachable from the closure roots (§7.3) refuses
  with `UNREFERENCED_MEMBER`. Only reachability edges (§7.3) count; a
  `ct.trace.v1` entry target is an annotation, not an edge.

### 1.3 Semantic validation responsibilities

| Stage | Responsibility | Failure |
|---|---|---|
| 1 Wire | Size caps, then canonical JSON parsing: duplicate keys, depth and nodes | `RESOURCE_LIMIT_EXCEEDED`, `SCHEMA_INVALID` |
| 2 Structure | Closed schema per kind: required fields, enumerations, closed nested objects, pattern grammars | `SCHEMA_INVALID` |
| 3 Reference | Kind match, digest match, transitive closure, no unreferenced members, predecessor chain, role match | codes in §1.2 |
| 4 Profile semantics | Edition content, account-kind bounds, rational/decimal domains, window ordering, at most one hypothesis per kind and one per procedure edition, policy edition and limits (only tightening) | `EDITION_CONTENT_MISMATCH`, `ACCOUNT_KIND_CONSTRAINT_VIOLATED`, `SCALAR_OUT_OF_ADMISSION_DOMAIN`, `POLICY_*` |
| 5 Authority | In this order (§6.5): request pin, authority pin, authority targets, prior material, plan admission, execution-target agreement, authority scope and plan change | `REQUEST_PIN_MISMATCH`, `AUTHORITY_PIN_MISMATCH`, `AUTHORITY_TARGET_MISMATCH`, `PRIOR_BUNDLE_MISMATCH`, `INTERPRETATION_PLAN_MISMATCH`, `PLAN_CHANGE_INVALID`, `EXECUTION_TARGET_MISMATCH`, `AUTHORITY_SCOPE_MISMATCH` |
| 6 Computation | Derivation, required claims, aggregation, gates, then selection or reassessment. Withholding and blocking are completed outcomes, not refusals. | (results) |
| 7 Comparison | Cached or retained computed records against fresh computation | `CACHED_DERIVATION_MISMATCH`, `DERIVATION_MISMATCH`, `APPLICABILITY_MISMATCH`, `SCORE_METADATA_INVALID`, `DOWNSTREAM_REPLAY_MISMATCH` |

Structural refusals precede aggregation. A missing or malformed required item is
never treated as pending (design §5).

## 2. Accounts, parameters, baseline, reference bias, units, endpoints

This section is unchanged in substance from the predecessor (owner choices
D1–D4).

- **H1** `high_underlying_faithful_baseline`: `b_suspect` exactly `[0,0]`.
- **H2** `low_underlying_positive_offset`: `0 < lo ≤ hi ≤ 50` °C. "Low" means
  `T_true < baseline` for every admitted offset.
- **Nomination:** at most one hypothesis per kind, at most two in total.

**Baseline eligibility.** This is the rational equality of the admitted baseline
scalar with the model `baseline`, plus equality of the constraint verdict. Each
check is `true`, `false` or `unknown`. Any `false` makes the hypothesis
ineligible; otherwise any `unknown` makes it unknown. Ineligible and unknown
hypotheses are retained and withhold selection; they are never pruned.

**Numbers.**

- `b_ref` is a required closed interval within `[−10, 10]` °C.
- The only unit is `degree_celsius`.
- Rationals are canonical and reduced, with at most 32 digits per part and
  denominators dividing 10⁶.
- Observation decimals are admitted in `[−200, 1000]` °C.
- Parameter intervals are closed. Decoder regions carry open or closed flags.
  Arithmetic is exact.

## 3. Procedures, decoders and the two distinct uncertainties

**Editions.** Procedure, decoder and interpretation editions are as in
`policy.json#/editions`:

- T1 decoder: low `(−∞,56]`, gap `(56,59]`, high `(59,∞)`;
- T2: `heater_on` iff held suspect baseline `< target`, with equality giving
  off.

**Two uncertainties, each applied exactly once, never conflated:**

| Quantity | Kind | Where it enters | Governing claim |
|---|---|---|---|
| `b_ref` | systematic model bias of the reference instrument (a model parameter) | ideal predicted set only: `[baseline − b_suspect.hi + b_ref.lo, baseline − b_suspect.lo + b_ref.hi]` | `reference_calibration` (binds `instrument_id`, `b_ref`) |
| `w` | random reading error, the declared hard observation-error bound of the interpretation plan | reassessment interval only: `[r − w, r + w]` | `observation_error_bound` (binds `instrument_id`, `plan`, `half_width`) |

The selection score never contains `w`. The reassessment interval never contains
`b_ref`. Witness OB4 shows both applied once with `b_ref = [−1/2, 1/2]` and
`w = 1/2`. The plan is captured by the selection and reported in
`observation_uncertainty_not_in_score`, together with its `plan_claim` and
`plan_state`.

**Plan admission.**

- `0 < w ≤ 5` °C.
- `w = 0` refuses with `INTERPRETATION_POINT_UNSUPPORTED`.
- `w > 5` refuses with `INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE`.
- A null T1 plan withholds selection with
  `observation_interpretation_plan_missing`.
- Unknown or confidence-only error has no plan in this profile.

## 4. Conditions, claims, declarations, evidence and reviews

### 4.1 Catalogue `ct.conditions.v2` (PROPOSED, closed; five conditions)

| Condition | Governs | Bound parameters (claim `binding.parameters`) |
|---|---|---|
| `reference_calibration` | T1 | `instrument_id`, `b_ref` |
| `reference_mapping` | T1 | `instrument_id`, `structural_model_revision`, `subject_entity_anchor_id`, `variable_anchor_id` |
| `state_hold` | T1, T2 | `baseline_as_of`, per-hypothesis `b_suspect` |
| `indicator_fidelity` | T2 | `instrument_id` (indicator), `target` |
| `observation_error_bound` | T1 | `instrument_id`, `plan`, `half_width` (new in v2) |

`observation_error_bound` governs T1 in both phases (owner choice O3; recommended
conservative). Its state is reported at selection and gates interpretation at
reassessment.

### 4.2 Claims bind the exact proposition

A claim core (`ct.claim.v1`) consists of:

- catalogue and condition (via `binding.condition`);
- procedure edition and phase;
- **exact model revision** (typed reference to the `ct.model.v1` record);
- subject entity and variable anchors;
- the bound parameters above, including plan references.

The application derives the required claim cores from the request:

- one per nominated procedure × governing condition, for the request's phase;
- at most 6 per request.

It also computes the **assessment time scope**:

| Phase | Time scope |
|---|---|
| Selection | `[model.context.as_of, request.as_of]` |
| Reassessment | `[model.context.as_of, result.acquisition.ended]` |

Supplied claims that are not canonically equal to a required core are retained
and listed under `applicability.unbound`. So are declarations, items and reviews
that bind only to such claims. They contribute nothing.

**Consequence: a changed `b_ref` or plan means a changed claim.** A model
revision that changes `b_ref` produces a new calibration claim core, because both
the parameters and the model reference differ. The old calibration declaration
and review bind to the old core; they become `unbound` and **cannot silently
support the changed claim**. Witnesses CB1–CB3 cover this:

- **CB1:** no declaration for the new claim, so `declaration_missing`.
- **CB2:** a new declaration but only the old review, so
  `none/complete/unresolved`.
- **CB3:** a fresh supporting review, so `supported`.

The same rule applies to a successor plan (PB1). Per owner wording, binding
includes the model revision, so *any* model revision re-binds every claim (owner
choice O5 records the narrower alternative).

### 4.3 Time coverage

Declarations and reviews carry a `covers` window. Evidence items carry an
optional `validity` window.

| Record | Full cover of the time scope | Partial cover | Disjoint | Validity `null` |
|---|---|---|---|---|
| Review | applies | item pending (`partial_or_unknown_scope`) | `inapplicable: covers_disjoint`; never an applicable opposing review | — |
| Declaration | applies | `inapplicable: declaration_covers_partial` | `inapplicable: covers_disjoint` | — |
| Evidence item | — | pending | conclusive exclusion (`validity_non_overlapping`) | pending, unless reviewed |

A declaration that does not fully cover the scope is not applicable. If no
applicable declaration remains, the result is `declaration_missing`.

### 4.4 Declarations and aggregation

**Declaration states.** Applicable declarations of a claim give
`declaration_state`:

| Applicable declarations | `declaration_state` | Effect |
|---|---|---|
| None | `missing` | blocks |
| Differing states | `conflicting` | blocks |
| `false` | `false` | blocks |
| `unknown` | `unknown` | blocks |
| Consistent `true` | `true` | — |

**Aggregation (FIXED).** Item-level order, the condition axes
(`reviewed_relation`, `review_completeness`) and the governing state follow
design §5 verbatim:

- pending evidence never weakens `contradicted` or `conflicting`;
- an irrelevant judgment never suppresses an applicable unresolved judgment.

**Review consistency** (stage 4):

- `incomplete` requires relevance `unresolved` and relation `unresolved`;
- `irrelevant` requires `not_applicable`;
- `relevant` requires `support`, `opposition` or `unresolved`;
- relevance `unresolved` requires relation `unresolved`.

The required number of reviews per item is a captured-policy field.

## 5. Captured policy material

`request.policy` must reference a `ct.policy.v1` record present in the closure.
Absence refuses with `REFERENCE_MISSING`, and **no default policy is ever
applied**.

The record must satisfy all of the following:

- `edition = ct.policy-edition.v3`, otherwise `POLICY_EDITION_MISMATCH`;
- the full limits object, every value ≤ the edition value, otherwise
  `POLICY_LIMIT_INVALID`;
- non-empty `permitted_builds`;
- `required_reviews_per_item` ∈ [1, 4];
- an explicit `unresolved_allowlist`.

An **empty allowlist is a recorded policy choice** that forbids every unresolved
use (PO2). It is not inferred from an omission. The allowlist can never permit
`contradicted` or `conflicting`. The synthetic example in `policy.json` is
labelled as an example for owner selection.

## 6. Requests, authority and changed plans

### 6.1 Request purposes (`ct.request.v1`, closed `oneOf`)

- **Selection request:** model, claims, declarations, evidence items, reviews,
  policy and `as_of`.
- **Reassessment request:** the same without `as_of`, plus `selection_basis`,
  `prior_selection {manifest, selection}` (typed references to the prior bundle
  manifest record and its selection; v2 carried a raw manifest digest),
  `plan_change` (null or `{former_plan, new_plan, reason}`), `execution_target`
  and `result`. The result consists of procedure, observation, acquisition
  `{started, ended, public_evidence, instrument_id}`, `interpretation_plan` and
  `execution_authority`.

### 6.2 Execution target, execution authority and evaluation authority

v2 defect: the reassessment request referenced its execution authority while
that authority's `target_request_sha256` was the same request's digest. Neither
digest could be computed first. v3 removes `target_request_sha256` and splits the
three bindings so every reference points to a record constructed earlier.

**Execution target `X` (`ct.execution-target.v1`, authored, role
`local_model_proposer`).** An immutable pre-result statement of what will be
executed. Drafting it grants no permission (design: packaging can draft a target
but cannot issue permission). It carries:

- `prior_selection {manifest, selection}`;
- `selection_basis` and `plan_change`;
- `model`;
- `procedure_edition` and `instrument_id`;
- `interpretation_plan` (T1: the plan to execute, whose `instrument_id` must
  equal `instrument_id`; T2: null).

It references no authority, request, observation or result.

**Execution authority `E` (`ct.authority.v1`, purpose `execution`, role
`local_execution_issuer`):**

- `target` is a typed reference to `X`; any other kind refuses with
  `REFERENCE_KIND_MISMATCH`;
- `scope.phase = reassessment`, and `scope.procedure_editions` must contain
  `X.procedure_edition`;
- `plan_change` must equal X's plan change as digests;
- `valid` must contain `[acquisition.started, acquisition.ended]`.

**Reassessment request `R`:**

- references `X` (`execution_target`) and `E` (`result.execution_authority`);
- `E.target` must be `X`, otherwise `AUTHORITY_TARGET_MISMATCH`;
- `R.model`, `selection_basis`, `prior_selection`, `plan_change`,
  `result.procedure_edition`, `result.interpretation_plan` and
  `result.acquisition.instrument_id` must equal X's fields, otherwise
  `EXECUTION_TARGET_MISMATCH`.

**Evaluation authority `A` (`ct.authority.v1`, purpose `evaluation`, role
`local_evaluation_issuer`):**

- `target` is a typed reference to the completed request (`R`, or the selection
  request); any other kind refuses with `REFERENCE_KIND_MISMATCH`;
- `scope.phase` must equal the request purpose and cover the procedure;
- `plan_change` must equal R's plan change as digests;
- A is the record pinned by `--expected-authority-pin`. R is not changed to
  reference A.

`schemas.json` splits `ct.authority.v1` into a closed `oneOf` by purpose. The
allowed provenance role is now bound per purpose (v2 allowed either issuer role
for either purpose); this is a tightening.

**Preserved enforcement:**

| Binding | v3 mechanism |
|---|---|
| Instrument | `X.instrument_id` = result instrument = T1 plan instrument |
| Model | `X.model` = `R.model` |
| Procedure | `X.procedure_edition` = result procedure, within E and A scope |
| Plan change | `X`, `R`, `E` and `A` agree (§6.3) |
| Phase and time scope | E: reassessment and acquisition within `valid`; A: phase of the request |
| External pins | `--expected-request-pin` = digest(R); `--expected-authority-pin` = digest(A). E and X are fixed transitively because R contains their digests (EO13). |

### 6.3 One admission rule for changed plans

Let `P0` be the plan captured by the prior selection for
`R.result.procedure_edition` (T1: the captured hard-interval plan; T2: null),
`R` the reassessment request, `X` its execution target, `E` its execution
authority and `A` the evaluation authority.

| `R.selection_basis` | Required | Otherwise |
|---|---|---|
| `inherited` | `R.plan_change = null` and `R.result.interpretation_plan = P0` | `INTERPRETATION_PLAN_MISMATCH` (unauthorized substitution, witness PS1) |
| `historical_reference_with_plan_change` | `R.plan_change = {former_plan = P0, new_plan = P1 ≠ P0, reason}` and `R.result.interpretation_plan = P1` | `PLAN_CHANGE_INVALID` (PS4, PS5) |
| either | X carries the same `selection_basis`, `plan_change` and plan | `EXECUTION_TARGET_MISMATCH` (EO11) |
| either | `A.plan_change` and `E.plan_change` are `null` (inherited) or `{former_plan_sha256 = P0, new_plan_sha256 = P1}` | `AUTHORITY_SCOPE_MISMATCH` (PS3 for A, EO12 for E) |

A completed changed-plan successor (PS2) records:

- `selection_basis = historical_reference_with_plan_change`;
- `prior_selection = P0's selection` (historical reference);
- `former_plan = P0`;
- `executed_plan = P1`;
- `plan_changed = true`;
- `original_plan_executed = false`;
- `ranking = not_reassessed`;
- `adoption = derived_not_adopted`.

It does not recompute or rerank the selection and adopts nothing. Its
`observation_error_bound` claim binds `P1`. Reviews of `P0`'s claim are unbound
(PB1), so P1 needs its own applicable review or an explicit allowlist entry.

### 6.4 Construction order (acyclic)

Every reassessment follows this order (witness CO1/EO1). Each step references only
records from earlier steps.

| Step | Record | References |
|---|---|---|
| 1 | Prior selection bundle (manifest `M0`, selection `S0`) | — |
| 2 | Plan `P1` (only for a changed plan) | — |
| 3 | Execution target `X` | `M0`, `S0`, model, `P0` or `P1` |
| 4 | Execution authority `E` | `X` |
| 5 | Acquisition, public evidence `O` | — |
| 6 | Reassessment request `R` | `X`, `E`, `O`, `M0`, `S0`, model, claims, declarations, items, reviews, policy |
| 7 | Evaluation authority `A` | `R` |
| 8 | Evaluate with pins `digest(R)` and `digest(A)` | — |
| 9 | Application computes descriptor `D` and closure roots `{R, A, D}` (§7.3) | — |

**Worked example** (`construction-example.json`). Upstream digests are labelled
placeholders. The digests below are computed from canonical bytes, and the five
records validate against `schemas.json` with no errors:

| Record | SHA-256 |
|---|---|
| X | `44f43d6b8ee5610a8ef21c6746b6eeb26e0958f844b402c2974eebadd0f0a155` |
| E | `6492c6f1dc4851b2a853bf9a78005cda6b2787cf5e4851f75650c6fa8832e01e` (target X) |
| R | `9b8bd27e069df3c86f860cd7c1d43b1d75be1e9b8a9cc188b468a0e90eb6e6cf` (references X and E) |
| A | `2c25730a20a27d5755f19e51bd0fcc148903dbefb76b183e0395d02f4f60509d` (target R) |
| D | `709fd8a3fced26d7d154261e778e42e61f0e1c194f2dda43d1e31a326761a927` |

None of X, E, R or A contains its own digest or a later record's digest.

### 6.5 Stage-5 check order

Each witness case has exactly one defect, so this order decides which code is
reported when several defects coexist:

1. request pin (`REQUEST_PIN_MISMATCH`);
2. authority pin (`AUTHORITY_PIN_MISMATCH`);
3. `A.target` = pinned request, then `E.target = R.execution_target`
   (`AUTHORITY_TARGET_MISMATCH`);
4. prior material (§7.3, `PRIOR_BUNDLE_MISMATCH`);
5. plan admission (§6.3 rows 1–2);
6. execution-target agreement (`EXECUTION_TARGET_MISMATCH`);
7. authority scope, validity and plan change (`AUTHORITY_SCOPE_MISMATCH`).

Plan admission precedes target agreement, so PS1 keeps its v2 code.

## 7. Commands, bundles and closure carriage

### 7.1 Commands

The six commands are `checked-{selection,reassessment}-{evaluate,verify,replay}`.

**Arguments:**

- `--expected-request-pin` and `--expected-authority-pin`, which are trusted
  entry-point arguments and are never read from the bundle;
- `--request` and `--objects-dir` (evaluate);
- `--bundle` (verify, replay);
- `--prior-bundle` (reassessment evaluate);
- `--output-dir NEW` (evaluate, replay).

**Exit classes:** 0 completed (including withheld or blocked), 2 usage,
3 integrity/input, 4 resource, 5 filesystem, 6 retention, 7 output channel.

### 7.2 Bundle files (fixed names; the manifest is written last)

| File | Record |
|---|---|
| `invocation.json` | `ct.invocation.v1` |
| `closure.json` | `ct.closure.v1` |
| `derivation.json` | `ct.derivation.v1` |
| `applicability.json` | `ct.applicability.v1` |
| `result.json` | `ct.selection.v1` or `ct.reassessment.v1` |
| `trace.json` | `ct.trace.v1` |
| `build.json` | `ct.build.v1` |
| `policy.json` | the captured `ct.policy.v1` |
| `manifest.json` | `ct.bundle-manifest.v1` (lists the other 8 by name, role, SHA-256 and bytes) |

Every file is exactly the canonical bytes of its record (sorted keys, separators `,` and `:`, UTF-8, no trailing newline). File SHA-256 therefore equals the record digest. This is what lets a carried prior record be checked against the prior manifest.

### 7.3 Closure carriage, roots and reachability

v2 defect: the closure had a single request root, but the invocation references
the evaluation authority (which the request cannot reference), and the
retained-selection descriptor had no request-reachable reference.

**Member form.** Members are `{kind, sha256, decoded_bytes, encoding: base64,
data}`, sorted by `(kind, sha256)` and unique by digest. Decoded and encoded
(file) sizes are limited separately.

**Authorized root set (`ct.closure.v1.roots`).**

| Bundle | `request` | `evaluation_authority` | `retained_selection` |
|---|---|---|---|
| Selection | selection request (= request pin) | A (= authority pin; purpose evaluation; target = request) | `null` |
| Reassessment | R (= request pin) | A (= authority pin) | descriptor `D` |

Nothing else is a root. In particular, these are not roots:

- the invocation, which is a bundle file whose `request` and `authority` must
  equal the roots and the pins;
- a supplied but unpinned authority (CL8).

**Reachability edges.** Every typed-reference field (`x-target`) of a closure
member is an edge, including:

- `predecessor`;
- `authority.target`;
- `request.execution_target` and `result.execution_authority`;
- all descriptor references, including each `D.prior_closure.members` entry and
  `D.prior_closure.roots`.

These are **not** edges:

- `ct.trace.v1` entry targets: annotations that must resolve to a member or to a
  record file named in the same manifest;
- raw-digest fields: the pins, `authority.plan_change` digests,
  `D.prior_closure.sha256` and `bytes`, manifest file entries, and
  `invocation.replay_of`.

The member set must **equal** the reachable set, roots included:

- a reachable digest that is absent refuses with `REFERENCE_MISSING` (CL4);
- any other member refuses with `UNREFERENCED_MEMBER` (CL2, CL8).

**Allowed member kinds:**

- Selection closure: the 12 input kinds (explanation, model, plan, claim,
  declaration, evidence item, evidence content, review, policy, request,
  authority, `nm.evidence.v1`).
- Reassessment closure: additionally execution target, retained-selection,
  invocation, derivation, applicability, selection, trace, build and bundle
  manifest.
- Never members: `ct.closure.v1`, `ct.reassessment.v1`, `ct.adoption.v1`.

**Exact prior-material carriage (reassessment).** At evaluate, prior-bundle
intake (steps 1–3) runs after R passes stages 1–2 and the request pin check, and
before the new closure is assembled. Its failures are therefore always
`PRIOR_BUNDLE_MISMATCH`, never `REFERENCE_MISSING`. At verify and replay, the same
checks run as stage-5 step 4 (§6.5). The application:

1. Reads `--prior-bundle`. The manifest file's digest must equal
   `R.prior_selection.manifest`.
2. Checks every prior file against that manifest.
3. Checks the prior closure at stages 1–3 under its own roots (selection kinds
   only, member set = reachable set). Any failure refuses with
   `PRIOR_BUNDLE_MISMATCH` (CL9, IN10).
4. Carries into the new closure, deduplicated by digest:
   - every prior closure member;
   - the prior manifest, invocation, selection (`result.json`), derivation,
     applicability, trace and build records. The prior captured policy is
     already a prior closure member.
   - The prior `closure.json` is **not** carried as a member. It is rebuilt.
5. Computes `D` (`ct.retained-selection.v1`) with:
   - `prior_manifest`;
   - `prior_closure {sha256, bytes, roots, members}`, where `members` lists the
     exact prior member references;
   - references to each carried prior record.

Verify and replay (with `--bundle` only, no prior bundle) recheck all of the
following from the closure alone. Any failure refuses with
`PRIOR_BUNDLE_MISMATCH`:

- `D.prior_manifest = R.prior_selection.manifest`, so the prior manifest is
  pinned through the request pin (CL6);
- `D.selection = R.prior_selection.selection`;
- each prior manifest entry equals the digest and canonical length of the carried
  record for that file (CL5);
- rebuilding a `ct.closure.v1` record from `D.prior_closure.roots` and the carried
  members named in `D.prior_closure.members` yields exactly the manifest's
  `closure.json` digest and length (CL3);
- the prior invocation's request and authority equal `D.prior_closure.roots`.

Verify then reports `prior_material_checked` (CL1).

An unrelated object therefore cannot be added:

- as a free member (`UNREFERENCED_MEMBER`);
- through `D` (prior closure rebuild mismatch);
- as an extra root (the external pins and the fixed root fields).

Object and byte accounting includes the full prior closure, the carried prior
records and `D` (§9, `RESOURCES.md`).

### 7.4 Responsibilities (FIXED, design §6)

- **evaluate:** fresh computation. A submitted cached record is a comparison
  artifact only.
- **verify:** recomputes derivation, required claims, aggregation and gates;
  checks the mandatory score metadata. It reports `derivation_checked`,
  `applicability_policy_checked` and `downstream_result_not_replayed`, plus
  `prior_material_checked` for a reassessment bundle (§7.3). It needs no prior
  bundle.
- **replay:** everything verify does, plus downstream recomputation into a new
  bundle.

## 8. Build capture and historical replay

The `ct.build.v1` fields are exact in `schemas.json`:

- checkpoint and clean `applications/` and `backend/`;
- source manifest of every tracked `.py` under those trees plus the dependency
  lock;
- environment manifest (CPython 3.13 digest, platform, distributions);
- contract editions (`schemas_sha256`, `policy_edition_sha256`, catalogue,
  calculator).

Rules:

- verify and replay accept only `permitted_builds` from the captured policy
  (`BUILD_NOT_PERMITTED`).
- Historical replay needs the exact recorded build, otherwise
  `HISTORICAL_BUILD_UNAVAILABLE`.
- Preserved legacy NM/NR behaviour (byte-unchanged modules) is distinct from the
  availability of their original environment. Adding modules re-baselines
  current identities (owner choice D9).

## 9. Limits

All limits are in `policy.json#/limits`, with basis and derivation for each.

- Selection and reassessment have **separate** object and closure caps, because a
  reassessment carries the entire prior closure.
- Decoded closure bytes and encoded file bytes are separate caps.
- v3 adds `retained_selection_bytes` = 32,768 (39 limits). The schema bounds the
  descriptor at 23,472 B.
- v3 re-derives `reassessment_unique_objects` (395 ≤ 400) and
  `reassessment_closure_decoded_bytes` (= 2,621,440) to include the carried prior
  records, the descriptor and the execution target. Both values are unchanged.
- Basis labels are `fixed_profile`, `analytical` (only where the value follows
  from fixed profile limits), `engineering`, `engineering_derived` (arithmetic
  over engineering caps) and `proposed_semantic`.

Unmeasured new-route sizes are estimates, never maxima (`RESOURCES.md`).

## 10. Fixed rules (unchanged)

These are design §4–§6 restated in the predecessor §7:

- ideal-branch score with no elimination guarantee;
- the plan is captured, never scored or double-counted;
- item-level precedence;
- opposition and conflict are never permitted;
- whole-set withholding;
- verify ≠ replay;
- immutable successors with exact authority;
- legacy preserved;
- no automatic adoption, physical-truth claim, discovery or backend extension.

## 11. Conflicts with accepted semantics

None found. Corrections A and B are expressible inside the accepted design:

- design: "Separate purpose-specific evaluation, execution and adoption records
  with exact target, scope/time/basis". v3 gives each purpose its own exact
  target kind, and the execution target is the explicit "immutable successor
  request" scope that design §4 requires before a result exists;
- design §6 verify "complete typed closure, exact … authority joins". v3 makes
  the closure roots explicit and the prior material checkable without the prior
  bundle.

The following are specification completions, not departures. Each is flagged so
the owner can see it:

- **c1:** per-purpose issuer roles (a tightening);
- **c2:** E's validity window must contain the acquisition interval (design
  "scope/time");
- **c3:** `P0` is defined per procedure (T2: null);
- **c4:** bundle files are exactly canonical bytes;
- **c5:** `ct.adoption.v1`, `ct.reassessment.v1` and `ct.closure.v1` are never
  closure members.

Owner choices that remain pending and are **not** decided here:

- **O3:** the selection-phase gating of `observation_error_bound`.
- **O5:** whether claim binding should include the whole model revision (as
  worded) or only the governing parameters.
- **D1–D10, A1:** see `README.md`.
- **G1, G2 (execution allowances):** see `PLAN.md` and `RESOURCES.md`.

## 12. v4 amendments (supersede the cited v3 clauses)

### 12.1 Policy identity (supersedes §5 bullet 1 and the schema label)

The captured `ct.policy.v1.edition` is `ct.policy-edition.v4` in both
`schemas.json` (const) and this contract. The edition content is `policy.json`
(`ct.policy-edition.v4`): the v3 limits plus the v4 refusal codes and exit
classes.

The label is checked before structural validation, so any other label refuses
with `POLICY_EDITION_MISMATCH`. The Gate 1 v2-label workaround is removed.

### 12.2 Diagnostics, exits and precedence (supersedes §7.1 exit list; amends F12b)

**Diagnostic record.** Every refusal writes one `ct.diagnostic.v1` record
`{schema, code, stage, target, exit_class}` to stderr, and nothing to stdout.

| Code | Exit | When |
|---|---|---|
| `CLI_USAGE` | 2 | unknown command, missing, duplicate or malformed argument, or malformed pin |
| `BUILD_IDENTITY_UNAVAILABLE` | 3 | the maintained executable identity cannot be computed (unclean or uncommitted `applications/`/`backend/`, wrong interpreter or lock, or identity tooling failure). Distinct from `BUILD_NOT_PERMITTED`, which means an identity exists but is absent from `permitted_builds`. |
| `BUILD_NOT_PERMITTED` | 3 | as v3 |
| `RESOURCE_LIMIT_EXCEEDED` | 4 | as v3 |
| `OUTPUT_COLLISION` | 6 | output directory exists, or cannot be created or written |
| `INTERNAL_ERROR` | 7 | any unclassified failure; no partial claim |

**Precedence.** Structural (stage 2) schema bounds precede stage-4 count limits.
Where the schema's `maxItems` equals the edition ceiling (for example
`request.reviews` = 64), exceeding it refuses with `SCHEMA_INVALID`.

- F12b is **amended** to `SCHEMA_INVALID`; its original expectation is retained
  in `witnesses.json`.
- A captured policy that tightens such a count below the schema bound refuses at
  stage 4 with `RESOURCE_LIMIT_EXCEEDED` (new witness F12c).

### 12.3 Result evidence bindings (supersedes §6.1 acquisition semantics; resolves Gate 1 F3)

**T1 (`nm.evidence.v1`, reconstructed by the owning legacy validator):**

- **Value binding:** the admitted canonical decimal equals
  `result.observation.scalar` (rational equality).
- **Instrument binding:** `result.acquisition.instrument_id` equals
  `model.reference_instrument_id` (and, as before, X's and the plan's instrument).
  The evidence binding's subject and variable anchors equal the model context
  anchors, which the `reference_mapping` claim governs. Its question must also
  join under the model's assertion context; only the evidence's own `as_of` is
  used, pending C1.
- **Distinct-occurrence binding:** the result evidence is not the model's
  baseline evidence, and its admitted `occurrence_id` differs from the baseline's.
- **Not a value:** temperature evidence is never accepted for a T2 result.

**T2 (application-owned `ct.code-evidence.v1`):**

- **Value binding:** `code` equals `result.observation.code`.
- **Instrument binding:** `instrument_id` equals `result.acquisition.instrument_id`
  and the model's T2 `indicator_instrument_id`.
- **Acquisition binding:** `observed_at` lies within the closed
  `[acquisition.started, acquisition.ended]`.
- **Not a value:** code evidence is never accepted for a T1 result.

The backend is not extended. Every failure refuses with
`RESULT_EVIDENCE_MISMATCH` (stage 5, after execution-target agreement).

**Pending owner choice C1 (T1 acquisition-time binding).** This rule is not yet
specified or enforced. Which T1 evidence instant must lie within the acquisition
window? Candidates are the snapshot `as_of`, the question `as_of`, and the
occurrence `finished_at`. And must it follow `model.context.as_of`? Every
committed or reproducibly derivable `nm.evidence.v1` carries the retained
synthetic baseline instant (`2026-08-07T20:30:00Z`), so no genuine temporally
subsequent T1 evidence exists to support a positive witness.

### 12.4 Applicability scope (clarifies §4.2)

**Selection** requires the whole nominated set: every nominated procedure ×
governing condition. That is unchanged.

**Post-observation reassessment** requires only the **executed** procedure's
governing conditions for phase `reassessment`. Claims for other procedures are
retained as `unbound`.

### 12.5 Encoded carriage (supersedes Gate 1 F5)

- `string_bytes` applies to every JSON string **except** the designated base64
  payload field `ct.closure.v1.members[*].data`.
- That field is limited by its decoded size: `decoded_bytes` ≤ `object_bytes`;
  `data` equals the canonical base64 of exactly `decoded_bytes` bytes.
- The closure decoded and file caps and the bundle caps still apply.
- Decoded members are re-parsed under every ordinary limit.

### 12.6 Derived claim references (supersedes Gate 1 F6; amends §7.3 edge list)

References to `ct.claim.v1` inside computed records are **derived references**,
not reachability edges:

- `applicability.claims[*].claim`;
- `applicability.assumed_conditions[*]`;
- `selection.observation_uncertainty_not_in_score[*].plan_claim`.

They are verified by fresh recomputation, and a mismatch refuses
(`APPLICABILITY_MISMATCH`, or `PRIOR_BUNDLE_MISMATCH` for carried priors).

A withheld or blocked selection whose required claim cores were not supplied
therefore remains self-contained. It is verifiable, replayable and usable as a
reassessment prior.

### 12.7 Evaluation authority validity (resolves Gate 1 F8)

`A.valid` (closed) must contain the end instant of the assessment time scope
(§4.2):

- selection: `request.as_of`;
- reassessment: `result.acquisition.ended`.

Otherwise the refusal is `AUTHORITY_SCOPE_MISMATCH` (stage 5, step 7). This uses
only recorded instants. There is no wall clock, and no physical chronology is
certified.

### 12.8 Cached derivation (adds the interface §7.1 lacked; IN1)

Both evaluate commands accept an optional `--cached-derivation PATH` (in process:
`cached_derivation` bytes). The cache is parsed canonically and checked
structurally (`SCHEMA_INVALID`). The fresh derivation is always computed
independently and the cache is never used as input. Any byte difference refuses
with `CACHED_DERIVATION_MISMATCH`.

### 12.9 Captured limits (supersedes "only tightening" retention)

After the captured policy is admitted (stage 4), every closure member is
re-checked against the **captured** limits as well as the edition ceilings:

- `object_bytes`;
- `string_bytes` (with the §12.5 exception);
- `json_depth`, `json_nodes`, `integer_digits`;
- the count and unique-object limits;
- `hypotheses`, `procedures`, `outcomes_per_procedure`, `successor_chain`
  (revision) and `retained_selection_bytes`;
- `fractional_digits`, for rationals that are edition-valid but exceed the
  captured value. Edition-invalid rationals remain `RATIONAL_INVALID`.
- `derivation_cells`, after derivation.

The work limits are defined exactly:

- **`trace_entries`:** the number of entries in the computed `ct.trace.v1`.
- **`rational_operations`:** one unit per exact rational addition, subtraction or
  comparison. The count covers T1 predicted-set arithmetic (4 per prediction),
  each T2 code comparison (1), each decoder-region intersection test (4), and
  the reassessment interval arithmetic (2) plus its region intersection tests (4
  each).

Exceeding a captured work limit refuses with `RESOURCE_LIMIT_EXCEEDED` before
any output is published.

END OF CHECKED-TEMPERATURE CONTRACT PREPARATION V4
