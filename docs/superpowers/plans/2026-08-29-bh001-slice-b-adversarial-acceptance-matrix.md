# BH-001 Slice B — adversarial acceptance matrix

Status: all B01-B60 controls are green. Slices A and B are owner accepted;
Slice B is accepted at `05177f7306ce745d093bd5f11abafc13a6274d0f`. BH-001
Slices A and B are owner accepted. Slice C is implemented and adversarially
reviewed; awaiting owner acceptance. Slice D has not started.

## 1. Public contract

| ID | Assertion or attack | Required result |
|---|---|---|
| B01 | Four method names/signatures | Exact accepted surface; `context` keyword-only |
| B02 | Six new aliases and literal order | Exact public vocabulary |
| B03 | Seven result names and ordered fields | Exact contracts, no extra field |
| B04 | `AssertionActivity` and `ContainingLineageHealth` | Reused, not duplicated |
| B05 | Exact `backend.model_kernel.__all__` | Only accepted Slice B additions |
| B06 | Alias, port query, evaluator, state, or outcome name | Absent |
| B07 | Malformed behavior/variable/record/context input, including unhashable and boolean values | Typed `ModelQueryError` before lookup |

## 2. Registration and reverse discovery

| ID | Assertion or attack | Required result |
|---|---|---|
| B08 | Valid absent behavior | `not_registered`; optional index absent; tuples empty |
| B09 | Permanent BRG present | Exact BRG, two VRGs, and aligned owner indices |
| B10 | Same owner for both variables | Repeated owner index is valid; owner record carried once |
| B11 | Cross-owner BRG | Both distinct owner indices disclosed |
| B12 | Missing variable reverse query | `variable_not_registered`; no indices/entries |
| B13 | Registered variable with no BRG | `registered`; exact VRG/owner; entries empty |
| B14 | Multiple BRGs for variable | One entry per anchor, canonical order, contiguous indices |
| B15 | Exact context has no BHD | Entry remains and says `not_declared` |
| B16 | Common owner/names/topology/VPA/semantics/values only | No inferred entry |

## 3. Roots, groups, conclusion, and findings

| ID | Assertion or attack | Required result |
|---|---|---|
| B17 | Registered behavior with no root | `not_declared` / `not_applicable` |
| B18 | One healthy root | `declared` / `healthy`; `one_healthy_root` |
| B19 | Multiple identical healthy roots | one body group; `corroborating_healthy_roots`; `declared` |
| B20 | Independent differing healthy roots | multiple groups; cross-root disagreement; `conflicted` |
| B21 | Same-root fork, identical body | same-root conflict despite one body group |
| B22 | Same-root fork, differing body | same-root conflict and multiple body groups |
| B23 | Full convergence | one healthy current tip; prior branches remain in lineage |
| B24 | Partial convergence | uncovered fork remains; root conflicted |
| B25 | Inactive roots only | `inactive`; inactive finding; no active group |
| B26 | Active plus inactive roots | active conclusion preserved; inactive root/finding disclosed |
| B27 | Context differs | independent structured `not_declared` or its own lifecycle |
| B28 | Audit-only differences | same effective body and corroboration |
| B29 | Lock/context/rule/basis difference | effective body differs |
| B30 | Root/lineage/tip/withdrawal/group ordering | Canonical IDs/bytes only; no winner |
| B30a | Conflicted-root tips | Grouped for disclosure but excluded from healthy-root corroboration/disagreement voting |
| B30b | Healthy A/A/B roots | Corroboration and cross-root disagreement both disclosed |

## 4. Assertion lifecycle and replay

| ID | Assertion or attack | Required result |
|---|---|---|
| B31 | Found BRG | Permanent event; lifecycle/root fields absent |
| B32 | Found current BHD | `current`; root and subject dimensions exact |
| B33 | Found superseded BHD | `superseded`; direct successors exact |
| B34 | Found withdrawn BHD | `withdrawn`; withdrawals exact |
| B35 | BHD in healthy root but conflicted subject | Both dimensions disclosed independently |
| B36 | Found BHW | Event; lifecycle/root fields absent |
| B37 | Valid-shaped absent BRG/BHD/BHW | `not_found`; optional lifecycle fields `None`; successor/withdrawal tuples empty |
| B38 | Earlier membership omits successor | predecessor revives as current |
| B39 | Earlier membership omits withdrawal | target revives as current |

## 5. Authoritative revalidation

| ID | Assertion or attack | Required result |
|---|---|---|
| B40 | Outer/nested `model_construct` | Reconstructed and rejected if forged |
| B41 | Outer/nested `model_copy` mutation | Reconstructed and rejected if forged |
| B42 | Stale content-derived record ID | Material reconstruction fails |
| B43 | Mixed/replaced revision or membership | Exact membership validation fails |
| B44 | Reordered/missing/duplicate/extra material | Validation fails |
| B45 | Behavior, variable, context, or record substitution | Validation fails |
| B46 | Wrong union arm at any index | Validation fails |
| B47 | Forged root/lineage/tip/withdrawal | Validation fails |
| B48 | Forged representative/group/root membership | Validation fails |
| B49 | Forged health/finding/conclusion/activity | Validation fails |
| B50 | Missing/duplicate/reordered entry or noncontiguous index | Validation fails |
| B51 | Boolean or coercible index | Strict validation fails |
| B52 | Result serialization repeated | Byte-identical deterministic JSON |

## 6. Preservation and architecture

| ID | Assertion or attack | Required result |
|---|---|---|
| B53 | Explicit 9/10/11/14/16/18/28/29 replay | Exact old revisions; structured BH absence |
| B54 | Current demo inspection | 29 records; zero BRG/BHD/BHW; unchanged revision |
| B55 | Existing record/artifact hashes | Byte-identical |
| B56 | Query object store/filesystem ownership | None |
| B57 | Kernel upward import | None |
| B58 | Store/index/canonical/record diff | None |
| B59 | Behavior inference or graph traversal | None |
| B60 | Slice C evaluator or Slice D fixture | Absent |

## 7. Stop gate

Every B01-B60 row must be green, all specialist findings reconciled, all
verification columns complete, and the file-first completion report committed.
Stop for owner acceptance without beginning Slice C or D.

END OF BH-001 SLICE B ADVERSARIAL ACCEPTANCE MATRIX
