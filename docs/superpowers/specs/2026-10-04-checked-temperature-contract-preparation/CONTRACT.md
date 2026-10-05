# Checked-temperature contract preparation (`bdw.checked-temperature.v1`)

Date: 2026-10-04, Europe/Amsterdam. Status: **preparation package for owner
evaluation**. It is not an executable contract freeze, an implementation, a test
result or authorization to implement. Every value marked **PROPOSED** is a
concrete minimal proposal awaiting owner decision. Values marked **FIXED** are
carried unchanged from the owner-accepted semantic candidate.

## 0. Governing inputs

| Input | SHA-256 |
|---|---|
| Corrected design v2 (`docs/superpowers/proposals/2026-10-04-checked-derivation-and-applicability-corrected-design-v2.md`) | `68da70f2cc64d837e45e8534da0eba7d95d94686ab40806099c5f06a0e4a02da` |
| Focused confirmation v2 (`docs/superpowers/reports/2026-10-04-checked-derivation-and-applicability-focused-confirmation-v2.md`) | `f0259702892f52f3e61dda3f665bb6c31298e276f9fdd86b10cd9e685f8fcc55` |
| Repository checkpoint | `2f0afbd368105b99f0b8548ffece107918386e3d` |

Below, *design §n* refers to the corrected design v2. The score domain (§4),
evidence aggregation and governing-state precedence (§5) and the
evaluate/verify/replay boundary (§6) are **FIXED** and are not reopened here.
This package supplies the six prerequisites of design §10.

Retained source material consulted, read-only:

- `applications/bounded_decision_workflow/measurement_ranking.py`: the pure
  minimax ranker. It preserves empty and repeated branches and withholds the
  whole set (lines 36–75).
- `reassessment_compute.py`: the all-intersecting-branches reassessment and its
  disposition rules (lines 105–176).
- `measurement_wire.py`: the canonical rational form (lines 144–154).
- `measurement_build.py`: build identity (lines 16–78).
- The committed P case (`docs/superpowers/reports/2026-09-19-next-measurement-preparation/inputs/P/capture.json`).
- The 2026-10-01 experiment model (`sim-investigation-2026-10-01/frozen/model-baseline.json`,
  SHA-256 `22fd12052da868e2511ea6b1710a91804550130cd13fdcaf1ce4436d8c854f90`).

**Discrepancy disclosed.** The committed P case's scalar decoder `O1` has two
regions: low ≤ 50 and high > 50. The three-region decoder that the design calls
"retained" (low ≤ 56, gap (56, 59], high > 59) exists only in the experiment's
model file. §2 below proposes it as a new literal edition. It does not claim it
as committed legacy material.

## 1. Prerequisite 1 — accounts, parameters, baseline, reference bias, units, endpoints

### 1.1 Fixed relations (FIXED, design §2)

- `T_true = baseline − b_suspect`
- T1 ideal measurand `= T_true + b_ref`
- T2 reports `heater_on` iff the held suspect baseline `< target`, otherwise
  `heater_off`. Equality gives off. The hidden true temperature is never
  compared with the target.

### 1.2 Account kinds

The two account kinds come from a closed enumeration. A nominated hypothesis
carries exactly one kind. It also carries one `b_suspect` interval, a statement,
a proposer and a rationale.

| Kind | Meaning | `b_suspect` constraint |
|---|---|---|
| `high_underlying_faithful_baseline` (H1) | The true temperature equals the baseline reading; the suspect baseline sensor carries no offset. | **PROPOSED:** exactly `[0, 0]`. A non-zero tolerance would be a different account kind (an owner decision; not offered). |
| `low_underlying_positive_offset` (H2) | The true temperature is strictly lower than the baseline reading because the suspect sensor carries a strictly positive offset. | **PROPOSED:** closed `[lo, hi]` with `0 < lo ≤ hi ≤ 50` °C. `lo = 0` refuses, because it would include the H1 account. |

- **"Low" criterion.** "Low" means `T_true < baseline` for every admitted offset.
  The `lo > 0` constraint guarantees this. No further temperature threshold is
  implied.
- **Nomination limits.** At most two hypotheses are nominated, at most one per
  kind (**FIXED** profile limit). Nomination does not assert truth or
  exhaustiveness.

### 1.3 Baseline eligibility

A hypothesis is `baseline_eligible` only if both checks hold:

1. The admitted public baseline evidence carries a finite decimal scalar equal,
   exactly as a rational, to the model's declared `baseline`.
2. The baseline constraint verdict in that evidence equals the declared verdict
   (`violated` in the retained example).

The two checks reuse the legacy requirement meanings (`baseline_decimal_equals`,
`baseline_cn_verdict_equals`). Each check yields `true`, `false` or `unknown`:

- Any `false` gives `baseline_ineligible`.
- Any `unknown` gives `baseline_unknown`.

An ineligible or unknown hypothesis is retained in the nominated set:

- It contributes no permits to the ideal matrix.
- Its cells are marked `baseline_ineligible` or `baseline_unknown`, and the
  selection is withheld.
- It is not pruned.

Eligibility is per captured assessment only (design §4).

### 1.4 Reference bias (`b_ref`)

`b_ref` is a model parameter of the T1 reference instrument: a closed interval
`[lo, hi]`, required, with no default.

- **PROPOSED:** `−10 ≤ lo ≤ hi ≤ 10` °C.
- It enters the ideal predicted set exactly once, as parameter uncertainty.
- It is distinct from the observation interpretation plan (§2.3), which is
  applied once at reassessment. Neither is folded into the other.
- Its validity is governed by the `reference_calibration` condition (§3).
- A non-zero interval is legal. It widens predictions; it does not change the
  score domain.

### 1.5 Units and numbers

- **Unit.** The only unit is `degree_celsius`, under the
  `ohk-units-1/project_local` edition. No unit conversion happens. Any other unit
  refuses with `UNIT_UNSUPPORTED`.
- **Numbers.** Every model number is a canonical reduced rational
  `{numerator, denominator}`, using the legacy grammar. **PROPOSED** new limits
  (not inherited):
  - at most 32 digits in each of numerator and denominator;
  - every denominator must divide 10⁶, so scalars are finite decimals with at
    most 6 fractional digits.
- **Observation scalars.** These are finite decimal strings (grammar in
  `schemas.json#/definitions/decimal`), with at most 6 fractional digits. They
  are admitted only within the **PROPOSED** domain `[−200, 1000]` °C.
  Out-of-domain values refuse with `SCALAR_OUT_OF_ADMISSION_DOMAIN`. They are
  never clamped.
- **Parameter bounds (PROPOSED).**
  - `baseline` and the T2 `target` lie in the admission domain.
  - `b_suspect` and `b_ref` lie within the per-kind bounds above.

### 1.6 Endpoint rules

- Parameter intervals are closed; degenerate `lo = hi` is allowed.
- The derived predicted interval for hypothesis h under T1 is closed:
  `[baseline − b_suspect.hi + b_ref.lo, baseline − b_suspect.lo + b_ref.hi]`.
- Decoder regions carry explicit open or closed flags (§2.1).
- An intersection is non-empty iff its lower bound is below its upper bound, or
  both are equal with both sides closed.
- Exact rational comparison is used throughout. Floating point is never used.

## 2. Prerequisite 2 — decoders, editions, T2 rule, containment, admission

### 2.1 Literal procedure and decoder editions (PROPOSED)

| Edition | Content |
|---|---|
| `ct.procedure.T1.v1` | Method `reference_scalar`; measurand `T_true + b_ref`; decoder `ct.decoder.T1.v1`; interpretation `ct.interpretation.hard-interval.v1`; governing conditions `reference_calibration`, `reference_mapping`, `state_hold`. |
| `ct.decoder.T1.v1` | Exactly three ordered regions forming a partition of the reals: `low (−∞, 56]`, `gap (56, 59]`, `high (59, +∞)`. Cut points are literals of the edition, not caller parameters. |
| `ct.procedure.T2.v1` | Method `nonspecific_code`; `heater_on` iff held suspect baseline `< target`, else `heater_off`; target is a required rational parameter of the request, with no default; decoder `ct.decoder.T2.v1`; interpretation `ct.interpretation.exact-code.v1`; governing conditions `state_hold`, `indicator_fidelity`. |
| `ct.decoder.T2.v1` | Exactly two literal regions: `heater_off`, `heater_on`. |

Rules for the editions:

- Any other decoder content under these edition IDs refuses with
  `EDITION_CONTENT_MISMATCH`.
- A changed cut point requires a new edition ID and owner approval of that
  edition.
- Partition validity is checked: contiguous, non-overlapping and covering, with
  exactly one closed side at each cut point.

**Alternative, not proposed:** caller-supplied cut points validated as a
partition. That moves decoder choice into the request and enlarges the review
surface.

### 2.2 T2 held-suspect rule

- The held suspect baseline is the admitted baseline scalar.
- `heater_on` iff `baseline < target`; equality gives `heater_off`.
- The outcome is identical for every eligible hypothesis, so T2's survivor
  multiset is `{all eligible}` and `{}`. It is retained and scored, never
  dropped.
- T2's validity requires `state_hold`, because the held reading is unchanged,
  and `indicator_fidelity`, because the indicator implements the rule.

### 2.3 Observation interpretation plans

**`ct.interpretation.hard-interval.v1`** applies to T1. It is a declared
symmetric hard error with half-width `w`.

- **PROPOSED:** `0 < w ≤ 5` °C, a canonical rational within §1.5.
- `w = 0` refuses with `INTERPRETATION_POINT_UNSUPPORTED`. An exact-point
  edition would be a separate future edition.
- Unknown and confidence-only error have no plan in this profile. A T1 nominated
  without a plan withholds selection with
  `observation_interpretation_plan_missing`. The derivation remains inspectable.
- The interpreted interval is `[r − w, r + w]`, closed, applied once.
- **Scalar containment:** the admitted scalar `r` must lie inside the
  interpreted interval. This holds trivially for the symmetric form and is still
  checked. It also requires `r` to lie in the admission domain.

**`ct.interpretation.exact-code.v1`** applies to T2. An admitted code must be
exactly one decoder literal; anything else refuses with `CODE_NOT_IN_DECODER`.
No temperature-error interval exists for T2.

The selection captures the plan by reference. A result whose plan reference
differs refuses with `INTERPRETATION_PLAN_MISMATCH` (design §4). A changed plan
requires an immutable successor request with newly scoped authority.

### 2.4 Numeric admission summary (PROPOSED)

| Item | Admitted | Refused (plus-one) |
|---|---|---|
| Fractional digits | 6 | 7 |
| Rational digits per part | 32 | 33 |
| Scalar domain | `[−200, 1000]` | `1000.000001` |
| Half-width `w` | `(0, 5]` | `0` (`INTERPRETATION_POINT_UNSUPPORTED`), `5.000001` (`INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE`) |
| H2 `b_suspect` | `0 < lo ≤ hi ≤ 50` | `lo = 0`, `hi = 50.000001` |
| `b_ref` | `[−10, 10]` | `10.000001` |

## 3. Prerequisite 3 — finite governing-condition catalogue

### 3.1 Catalogue `ct.conditions.v1` (PROPOSED; closed)

| ID | Typed proposition | Governs |
|---|---|---|
| `reference_calibration` | The T1 reference instrument's bias lies within the declared `b_ref` interval over the acquisition interval. | T1, all hypotheses |
| `reference_mapping` | The T1 reference instrument observes the declared subject entity and variable anchor. | T1, all hypotheses |
| `state_hold` | `T_true` and `b_suspect` are unchanged between the baseline as-of time and the end of the acquisition interval. | T1 and T2, all hypotheses |
| `indicator_fidelity` | The heater indicator implements the `ct.procedure.T2.v1` rule for the declared target. | T2, all hypotheses |

No other condition ID is accepted. Natural-language propositions are not
parsed; the proposition text is fixed by the edition.

### 3.2 Identity and phase binding

The condition key is `(catalogue_edition, condition_id, subject_entity_anchor,
variable_anchor, procedure_edition, phase, assessment_context)`. Its parts:

- `phase` ∈ {`selection`, `reassessment`};
- `assessment_context` = `(as_of, scenario_label, assertion_context)`.

The request derives the set of required keys from the nominated procedures and
phases. A selection-phase state is never upgraded by a reassessment-time review,
which is evaluated under its own key (design §4).

### 3.3 Declarations

- **States.** Each required key needs at least one declaration with state in
  {`true`, `false`, `unknown`}.
- **Retention.** All declarations are retained.
- **Effects:**
  - Two or more declarations with different states for the same key give
    `conflicting_declarations`, which blocks.
  - Identical-state duplicates are consistent; both are retained.
  - A missing required declaration gives `declaration_missing`, which blocks.
  - `false` or `unknown` blocks.
  - A declaration for an unknown condition ID or an out-of-scope key refuses
    structurally.
- **Independence from evidence.** A declaration is not a review of itself. A
  `true` declaration never erases reviewed opposition. An unresolved-use
  allowlist cannot repair a declaration failure (design §5).

### 3.4 Evidence aggregation (FIXED)

The item-level order and the condition-level axes and state of design §5 apply
verbatim per condition key. The one remaining preparation choice is the
conclusive typed exclusion predicate, **PROPOSED** as follows:

- **Conclusive exclusion.** An evidence item is conclusively excluded for a key
  iff either:
  - (a) its declared applicability-validity interval `[valid_from, valid_to]`
    lies entirely outside the assessment window, which runs from baseline as-of
    to the end of acquisition (or to as-of for selection); or
  - (b) it declares a subject entity anchor or a variable anchor that differs
    exactly from the key's.
- **Pending.** A missing validity interval, a partial overlap, or a missing
  anchor is not exclusion; the item stays pending.
- **What is not a validity interval.** Raw publication, acquisition or
  attachment times are never applicability-validity intervals.

## 4. Prerequisite 4 — pins, interfaces, roles and unresolved policy

### 4.1 Commands (PROPOSED dispatch names; new sibling routes)

```
python -m applications.bounded_decision_workflow checked-selection-evaluate \
    --request R --objects-dir D --expected-request-pin SHA \
    --expected-authority-pin SHA --output-dir NEW
python -m applications.bounded_decision_workflow checked-selection-verify \
    --bundle B --expected-request-pin SHA --expected-authority-pin SHA
python -m applications.bounded_decision_workflow checked-selection-replay \
    --bundle B --expected-request-pin SHA --expected-authority-pin SHA --output-dir NEW
checked-reassessment-{evaluate,verify,replay}   (same argument shape;
    --request references the retained checked-selection bundle by digest)
```

**External pins.** The two expected pins are trusted entry-point arguments.
Neither may be recovered from the bundle; each must equal the canonical SHA-256
of the request and the authority record respectively. On a mismatch the command
refuses with `REQUEST_PIN_MISMATCH` or `AUTHORITY_PIN_MISMATCH` before any
computation. A rehashed substitute authority cannot match an unchanged external
pin. A fresh coherent request with a fresh pin is accepted as a new declared
assessment, not as authenticated ownership.

**Responsibilities.** These are design §6 exactly:

- **evaluate:** fresh derivation, aggregation and downstream computation.
  Optional cached records are compared, and refuse on mismatch.
- **verify:** recomputes derivation and applicability. It reports
  `derivation_checked`, `applicability_policy_checked` and
  `downstream_result_not_replayed`. Misleading mandatory metadata refuses.
- **replay:** everything verify does, plus downstream recomputation into a new
  bundle.

**Exit codes.** These reuse the legacy classes:

| Code | Meaning |
|---|---|
| 0 | completed (including `withheld`) |
| 2 | usage |
| 3 | integrity / input |
| 4 | resource |
| 5 | filesystem |
| 6 | retention |
| 7 | output channel |

### 4.2 Local roles (PROPOSED; unauthenticated labels)

| Role | Records |
|---|---|
| `local_model_proposer` | explanations, model/input graph |
| `local_evidence_reviewer` | evidence reviews |
| `local_condition_declarer` | condition declarations |
| `local_evaluation_issuer` | evaluation authority |
| `local_execution_issuer` | execution authority (for the selected procedure) |
| `local_adoption_decider` | adoption record (never automatic) |

- Every record carries `{role, label, authenticated: false, basis}`.
- No real person is assigned. No identity is authenticated.
- The software checks only that each record's role matches its record type.
  **PROPOSED:** no label-separation rule, since it would be unverifiable.

### 4.3 Synthetic unresolved-condition policy (PROPOSED example; owner selects)

Policy `ct.policy.synthetic-unresolved.v1` permits `unresolved` use for:

- `reference_calibration`, `reference_mapping` and `state_hold`, in both phases;
- not `indicator_fidelity`.

Omitted entries are forbidden. The policy can never permit `contradicted` or
`conflicting`. It is labelled synthetic and is not a deployment policy. With it,
the use disposition becomes `conditional_use_with_unresolved_conditions`, which
enumerates the conditions and pending items. The alternative is the empty
allowlist, which forbids every unresolved use; it is the safest default and the
one the schema applies when no policy is captured.

## 5. Prerequisite 5 — source/build capture and historical replay

### 5.1 Capture

The checked route's build record `ct.build.v1` carries:

- **Source:**
  - the checkpoint commit;
  - a clean-status requirement for `applications/` and `backend/`;
  - the source manifest (path, SHA-256 and bytes of every tracked `.py` file
    under `applications/` and `backend/`, plus the dependency lock).
- **Environment:** the environment manifest (interpreter digest and bytes,
  platform, and each distribution's version and artifact-manifest digest).
- **Editions:** the contract edition set, meaning the digests of `schemas.json`
  and `policy.json` editions as frozen at implementation, and the calculator
  edition `ct.calculator.v1`.

This matches `measurement_build.identity()` in structure, adding the contract
edition set and calculator edition.

### 5.2 Verification and replay environment

**Permitted builds.** verify and replay accept only build identities listed in
the captured policy's `permitted_builds`. An unknown calculator edition, or any
caller-supplied code, refuses with `BUILD_NOT_PERMITTED`. A self-declared hash
grants nothing.

**Historical replay.** This requires the exact recorded build (checkpoint,
source manifest, environment manifest and editions). Otherwise it refuses with
`HISTORICAL_BUILD_UNAVAILABLE`. There is no default promise that an old bundle
replays in a changed checkout.

**Legacy routes.** These stay separate.

| Aspect | Status |
|---|---|
| Preserved legacy behaviour | The NM/NR modules, parsers, support grammar and commands remain byte-unchanged. This is checkable by tree digests of the legacy files. |
| Availability of the original executable environment | Adding checked-route modules changes the tracked source manifest. NM/NR bundles produced at `2f0afbd` (for example the experiment's NM build `a49ae732…` and NR build `91dc0894…`) will then refuse current-checkout replay. They remain replayable only in an environment reconstructed at `2f0afbd` with the matching interpreter (the existing local `cp313-bdw001`, SHA-256 `47f615b1…`, present as of 2026-10-01 but not a guaranteed asset). |

This consequence must be accepted before implementation (owner decision D9).

## 6. Prerequisite 6 — schemas, limits and plan

### 6.1 Schemas

The machine-readable proposed schemas are in `schemas.json`, covering these
record kinds:

- `ct.explanation.v1`, `ct.model.v1`, `ct.interpretation-plan.v1`;
- `ct.condition-declaration.v1`, `ct.evidence-item.v1`, `ct.evidence-review.v1`;
- `ct.policy.v1`, `ct.request.v1`, `ct.authority.v1`;
- `ct.derivation.v1`, `ct.applicability.v1`, `ct.selection.v1`;
- `ct.reassessment.v1`, `ct.adoption.v1`, `ct.build.v1`;
- `ct.bundle-manifest.v1`.

Every record has the header `{schema, profile, id, revision, predecessor}` and a
canonical content digest; typed references are `{kind, sha256}`.

Computed outputs carry these mandatory fields:

- `score_domain = "ideal_measurand_decoder_branches"`;
- `post_measurement_elimination_guaranteed = false`;
- `observation_uncertainty_not_in_score`;
- `derived_not_adopted`.

### 6.2 Limits

The limits are in `policy.json#/limits`, with their basis in `RESOURCES.md`.
Exhaustion refuses with `RESOURCE_LIMIT_EXCEEDED` before omitting any dependency
or doing unbounded work. Old-profile ceilings are not evidence of capacity.

### 6.3 Plan

The implementation and verification plan is in `PLAN.md`. The witness matrix is
in `WITNESSES.md` and `witnesses.json`.

## 7. Fixed rules restated (non-negotiable for implementation)

1. Selection scores ideal-measurand decoder branches. It makes no guarantee of
   post-measurement elimination.
2. The interpretation plan is captured, and is neither scored nor double-counted.
3. Item-level review precedence follows design §5.
4. An irrelevant judgment cannot suppress an applicable unresolved judgment.
5. Opposition or conflict is never policy-permitted.
6. A blocked selection withholds the whole nominated-set ranking.
7. verify does not replay downstream; replay recomputes it.
8. Changes require immutable successors and exact authority scope.
9. Legacy profiles and claims are preserved.
10. There is no automatic adoption, no physical-truth claim, no hypothesis
    discovery and no backend extension.

END OF CHECKED-TEMPERATURE CONTRACT PREPARATION
