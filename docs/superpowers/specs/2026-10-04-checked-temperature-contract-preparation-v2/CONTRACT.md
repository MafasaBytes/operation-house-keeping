# Checked-temperature contract preparation, successor v2 (`bdw.checked-temperature.v1`)

Date: 2026-10-04, Europe/Amsterdam. Status: **documentation-only preparation for
owner evaluation**. This is not an executable contract freeze, implementation or
test evidence. Passing JSON parsing and hash checks does not establish executable
readiness.

## 0. Inputs and predecessor

| Input | SHA-256 |
|---|---|
| Corrected design v2 | `68da70f2cc64d837e45e8534da0eba7d95d94686ab40806099c5f06a0e4a02da` (unchanged) |
| Focused confirmation v2 | `f0259702892f52f3e61dda3f665bb6c31298e276f9fdd86b10cd9e685f8fcc55` (unchanged) |
| Predecessor package `…-contract-preparation/MANIFEST.json` | `c3de4cb9d5868454e8d666267d9dd9cf58f33d69500065c1f648005bf3da48c2` (preserved unchanged) |
| Checkpoint | `2f0afbd368105b99f0b8548ffece107918386e3d` |

*Design §n* refers to the corrected design v2. The following are **FIXED** and
not reopened:

- the score domain (design §4);
- item-level review precedence, condition axes and governing-state precedence
  (design §5);
- the evaluate/verify/replay boundary (design §6).

`CORRECTIONS.md` maps every change from the predecessor package. The disclosed
decoder discrepancy (the committed P case splits at 50; the proposed edition
splits at 56 and 59, taken from the experiment model) is unchanged.

## 1. Record identity, provenance and typed references

### 1.1 Record classes (`schemas.json#/record_classes`)

| Class | Kinds | Identity | Provenance |
|---|---|---|---|
| Authored | explanation, model, interpretation-plan, condition-declaration, evidence-item, evidence-review, policy, request, authority, adoption | `(schema, id, revision)` unique in a closure; canonical digest. `predecessor` is null for revision 1. Otherwise it references the same schema and id at revision − 1, and that predecessor must be present in the closure (`PREDECESSOR_INVALID`). Revision ≤ 4. | Mandatory `provenance` attestation. Role from the kind's `x-allowed-roles` (`ROLE_MISMATCH`). `authenticated: false` always. |
| Derived-canonical | `ct.claim.v1` | digest only | none; fully determined by request inputs |
| Computed | derivation, applicability, selection, reassessment, retained-selection, build, invocation, trace, closure, bundle-manifest | digest only | produced only by the application, with `build` reference where applicable |
| Opaque / legacy-validated | `ct.evidence-content` (opaque bytes), `nm.evidence.v1` (public evidence, validated by the existing public-evidence validator semantics) | digest of bytes | carried by the referencing record |

### 1.2 Typed references

A typed reference is `{kind, sha256}`.

- `kind` is one of the 23 `typed_reference_kinds`.
- Each reference field restricts it through `x-target`; a different kind refuses
  with `REFERENCE_KIND_MISMATCH`.
- `sha256` is the SHA-256 of the target's canonical bytes (or raw bytes for
  opaque content).
- A referenced digest absent from the closure refuses with `REFERENCE_MISSING`.
  This covers a missing policy, model revision or predecessor.
- A closure member that no root-reachable reference uses refuses with
  `UNREFERENCED_MEMBER`.

### 1.3 Semantic validation responsibilities

| Stage | Responsibility | Failure |
|---|---|---|
| 1 Wire | Size caps, then canonical JSON parsing: duplicate keys, depth and nodes | `RESOURCE_LIMIT_EXCEEDED`, `SCHEMA_INVALID` |
| 2 Structure | Closed schema per kind: required fields, enumerations, closed nested objects, pattern grammars | `SCHEMA_INVALID` |
| 3 Reference | Kind match, digest match, transitive closure, no unreferenced members, predecessor chain, role match | codes in §1.2 |
| 4 Profile semantics | Edition content, account-kind bounds, rational/decimal domains, window ordering, at most one hypothesis per kind and one per procedure edition, policy edition and limits (only tightening) | `EDITION_CONTENT_MISMATCH`, `ACCOUNT_KIND_CONSTRAINT_VIOLATED`, `SCALAR_OUT_OF_ADMISSION_DOMAIN`, `POLICY_*` |
| 5 Authority | External pins, authority target, scope, plan-change agreement, prior-bundle manifest | `*_PIN_MISMATCH`, `AUTHORITY_SCOPE_MISMATCH`, `PRIOR_BUNDLE_MISMATCH` |
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

- `edition = ct.policy-edition.v2`, otherwise `POLICY_EDITION_MISMATCH`;
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
- **Reassessment request:** the same, plus `selection_basis`, `prior_selection`
  `{manifest_sha256, selection}`, `plan_change` (null or
  `{former_plan, new_plan, reason}`) and `result`. The result consists of
  procedure, observation, acquisition `{started, ended, public_evidence,
  instrument_id}`, `interpretation_plan` and `execution_authority`.

### 6.2 Authority

`ct.authority.v1` carries:

- `purpose` (evaluation or execution);
- `target_request_sha256`, which equals the request digest;
- `scope {phase, procedure_editions}`;
- `plan_change` (null or `{former_plan_sha256, new_plan_sha256}`);
- `valid`.

The evaluation authority is the record pinned by
`--expected-authority-pin`. The execution authority is referenced from
`result.execution_authority`; it must have purpose `execution`, scope the
procedure and phase, and agree on `plan_change`.

### 6.3 One admission rule for changed plans

Let `P0` be the plan captured by the prior selection, `R` the reassessment
request and `A` the evaluation authority.

| `R.selection_basis` | Required | Otherwise |
|---|---|---|
| `inherited` | `R.plan_change = null` and `R.result.interpretation_plan = P0` | `INTERPRETATION_PLAN_MISMATCH` (unauthorized substitution, witness PS1) |
| `historical_reference_with_plan_change` | `R.plan_change = {former_plan = P0, new_plan = P1 ≠ P0, reason}`, `R.result.interpretation_plan = P1`, and `A.plan_change = {former_plan_sha256 = P0, new_plan_sha256 = P1}` (same for the execution authority) | `PLAN_CHANGE_INVALID` (PS4, PS5) or `AUTHORITY_SCOPE_MISMATCH` (PS3) |

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

The predecessor package's B2b described this only in prose; v2 makes `CONTRACT`,
`schemas.json` (`plan_change` in request and authority; `selection_basis`,
`former_plan`, `executed_plan`, `original_plan_executed` and `plan_changed` in
the reassessment) and witnesses PS1–PS5 and PB1 agree.

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

### 7.3 Closure carriage

The closure carries members as `{kind, sha256, decoded_bytes, encoding: base64,
data}`, sorted by `(kind, sha256)`, unique and fully referenced from the request
root. Decoded and encoded (file) sizes are limited separately.

**Prior-bundle carriage (reassessment):**

- The application reads `--prior-bundle` and checks its manifest digest against
  `prior_selection.manifest_sha256` (`PRIOR_BUNDLE_MISMATCH`).
- It builds a `ct.retained-selection.v1` descriptor of the prior bundle's nine
  files.
- It merges the prior closure members, deduplicated by digest, and the prior
  computed records (selection, derivation, applicability, build, policy) into the
  new closure.

Object and byte accounting therefore includes the full prior closure (§9).

### 7.4 Responsibilities (FIXED, design §6)

- **evaluate:** fresh computation. A submitted cached record is a comparison
  artifact only.
- **verify:** recomputes derivation, required claims, aggregation and gates;
  checks the mandatory score metadata. It reports `derivation_checked`,
  `applicability_policy_checked` and `downstream_result_not_replayed`.
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

None found. Each correction is expressible inside the accepted design:

- claim binding refines design §3/§5 bindings;
- `observation_error_bound` represents the plan applicability that design §4
  requires to be captured and governed;
- the plan-change rule implements design §4's successor requirement.

Two points are surfaced as owner choices rather than silently decided:

- **O3:** the selection-phase gating of `observation_error_bound`.
- **O5:** whether claim binding should include the whole model revision (as
  worded) or only the governing parameters.

END OF CHECKED-TEMPERATURE CONTRACT PREPARATION V2
