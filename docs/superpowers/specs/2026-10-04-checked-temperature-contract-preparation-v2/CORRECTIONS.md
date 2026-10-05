# Correction map: predecessor package to successor v2

The predecessor package (`MANIFEST.json` `c3de4cb9…`) is preserved unchanged.
Its members' digests are re-verified in `README.md`.

## Correction 1: complete contracts and schemas

| Predecessor | Successor v2 |
|---|---|
| Computed records (`ct.derivation.v1`, `ct.applicability.v1`, `ct.selection.v1`, `ct.reassessment.v1`, `ct.build.v1`, `ct.bundle-manifest.v1`) used `x-note` annotations | Every field has an exact name, type, requiredness and enumeration, with closed nested objects (`additionalProperties: false` throughout; checked statically). |
| No closure, invocation, trace or retained-selection records | Added `ct.closure.v1` (member carriage with decoded size and base64), `ct.invocation.v1`, `ct.trace.v1` and `ct.retained-selection.v1`. |
| One header applied loosely to every kind | Four record classes (authored, derived-canonical, computed, opaque/legacy-validated) with their identity and provenance rules (CONTRACT §1.1). Every reference field names its allowed `x-target` kinds. Validation responsibilities are staged (§1.3). |
| CONTRACT §4.3 said the empty allowlist was "the one the schema applies when no policy is captured" | Withdrawn. A missing policy refuses with `REFERENCE_MISSING`. An empty allowlist is only a recorded choice (§5; witnesses PO1–PO5). |

## Correction 2: bind reviews to the exact claim

| Predecessor | Successor v2 |
|---|---|
| Declarations and reviews bound to `(condition, procedure_edition, phase, context)` only | Bound to a claim core carrying exact model revision, subject and variable anchors, instrument and governing parameters or plan, plus an explicit `covers` window (§4.2–4.3). Claims that are not required are listed as `unbound`. |
| No twin for a changed `b_ref` | CB1–CB3: an old calibration review does not support the changed claim. |
| Observation-error bound applicability not represented | New catalogue entry `observation_error_bound` (`ct.conditions.v2`), with `b_ref` and `w` each applied once and kept distinct (§3; OB2–OB4). Precedence is unchanged. |

## Correction 3: reconcile changed-plan requests

| Predecessor | Successor v2 |
|---|---|
| B2/B2b described in prose; no schema field distinguished substitution from successor | `selection_basis` and `plan_change` in the request; `plan_change` in the authority; `selection_basis`, `former_plan`, `executed_plan`, `original_plan_executed` and `plan_changed` in the reassessment. One admission table (§6.3). Witnesses PS1–PS5 and PB1. |

## Correction 4: verification and resource plan

| Predecessor | Successor v2 |
|---|---|
| "52 witnesses" conflated witnesses, cases and calls | 17 witnesses, 82 cases, 154 invocations and 2 launches, each counted separately (PLAN). |
| Legacy regression tests unnamed | Five named and statically screened; `test_delivery.py` excluded with its reason. |
| `unique_objects` 192 ignored prior-bundle closure | Separate selection (192) and reassessment (400, including the prior closure) limits. |
| "Analytical" hand counts (rational ops, trace entries, unique objects) | Relabelled as estimates or engineering-derived. |
| "about 0.8 MB each at most" for unmeasured bundles | Withdrawn. Caps are engineering refusal limits; sizes are labelled estimates. |
| Decoded closure only | Separate decoded and encoded-file caps, all nine files, refusals, partial outputs, replay coexistence, and physical allocation (RESOURCES §3–4). |
| "Implementation approval" implied unscoped test runs | Gate 1 needs an explicit TDD allowance (40 launches, 512 MiB). Gate 2 and later qualification are separately gated. |

## Witness ID changes

Predecessor IDs are mapped in the `predecessor_ids` field of `witnesses.json`
and the "Was" column of `WITNESSES.md`.

| Old | New |
|---|---|
| A1 | SC1 |
| A2 | UN1 |
| A3 | merged into PS2 |
| A4, A4b | UN3, UN4 |
| A5 | LB1 |
| B1 | PM1 |
| B2 | PS1 |
| B2b | PS2 (made exact) |
| B3 | HW0 |
| C1–C14 | AG1–AG14 |
| E1–E3 | DC1–DC3 |
| D1–D8 | IN1–IN9 |
| G1 | BE1 |
| F1–F13 | F*a / F*b |

Three of these changed their expected outcome or input, not just their ID:

- **D6 → IN6:** the expected code is corrected from `REFERENCE_DIGEST_MISMATCH`
  to `REFERENCE_MISSING`, because the referenced digest is absent.
- **D8 → IN9:** the authority scope is tested at reassessment.
- **F7 (`w` bounds):** now case HW5p, in witness W08.

END OF CORRECTION MAP
