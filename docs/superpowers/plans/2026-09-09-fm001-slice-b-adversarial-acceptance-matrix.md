# FM-001 Slice B Adversarial Acceptance Matrix

Date: 2026-09-09

Status: corrected future executable matrix; Slice B implementation
unauthorized pending owner approval

This matrix is governed by the corrected FM synthesis at SHA-256
`6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7` and the accepted Slice A implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`. Every row requires exact public
field/literal equality and a valid twin. No row is claimed implemented by this
documentation checkpoint.

## 1. Public surface and query boundary

| ID | Future executable acceptance |
|---|---|
| FM-B01 | The accepted 205-name Slice A export prefix remains exact and Slice B appends the exact ordered 20 names for 225 total. |
| FM-B02 | Exactly 11 new aliases expose their complete literal tuples in normative order; no subset assertion is accepted. |
| FM-B03 | Exactly four nested rows and five outer results expose only the exact ordered fields and required types. |
| FM-B04 | All fields are required; omitted null or empty derived fields reject rather than acquiring defaults. |
| FM-B05 | The five query names and signatures are exact; none is exported as a free function or convenience alias. |
| FM-B06 | No FM-specific builder, store, ledger, identity, cache, facade, fixture, demo, or second consumer exists. |
| FM-B07 | Exact lookup has no redundant relationship parameter; v1 direct-measurement relevance remains implicit. |
| FM-B08 | Every malformed identifier, context, or orientation reaches the existing typed query-error boundary rather than structured absence. |

## 2. Exact lookup and structured absence

| ID | Future executable acceptance |
|---|---|
| FM-B09 | All three endpoints registered plus no exact subject yields `all_registered`, `not_declared`, `not_evaluated`, null role, and empty findings/roots/groups/current indices. |
| FM-B10 | Each single missing endpoint yields its exact endpoint-registration literal and the same no-declaration cardinality. |
| FM-B11 | Every two- or three-endpoint absence yields `multiple_not_registered`; no lower-precedence singleton status leaks. |
| FM-B12 | A registered port outside the selected FRG participant set remains structured no declaration and does not manufacture relevance. |
| FM-B13 | One healthy root yields declared direct-measurement relevance and the exact `one_healthy_root` finding. |
| FM-B14 | Exact lookup returns only the complete subject selected by flow, variable, participant port, exact context, fixed relation, and orientation. |
| FM-B15 | Otherwise identical subjects with different orientations never merge, substitute, or share roots/groups. |

## 3. Root, body-group, and mixed-state cardinality

| ID | Future executable acceptance |
|---|---|
| FM-B16 | One conflicted root with two current bodies has one root row, two group indices, two groups/support sets, and no cross-root disagreement. |
| FM-B17 | One conflicted root whose tips share one body has one group and retains `same_root_conflict`. |
| FM-B18 | Independent healthy roots with one body group disclose `corroborating_healthy_roots` without selecting a winner. |
| FM-B19 | Independent healthy roots with unequal singleton body sets disclose every root/group plus cross-root disagreement. |
| FM-B20 | Healthy plus conflicted roots retain `one_healthy_root` and `same_root_conflict`; aggregate conclusion is `conflicted`. |
| FM-B21 | Healthy plus inactive roots retain `one_healthy_root` and `inactive_roots_present`; aggregate conclusion remains declared. |
| FM-B22 | Conflicted roots with equal body sets do not disclose cross-root disagreement. |
| FM-B23 | Conflicted roots with unequal body sets retain same-root conflict and cross-root disagreement in normative order. |
| FM-B24 | All-inactive roots remain visible, have no body groups/current indices, and yield aggregate `inactive`. |
| FM-B25 | A conflicted root may participate in several groups; each root/group back-reference is complete, unique, and reciprocal. |
| FM-B26 | Root rows order by root record ID; groups order by canonical body bytes; representatives use lowest current-tip record ID. |
| FM-B27 | Finding precedence/order is exact for every mixture of healthy, corroborating, conflicted, inactive, and disagreeing roots. |

## 4. Support-row reachability

| ID | Future executable acceptance |
|---|---|
| FM-B28 | Every positive effective-body group and found positive assertion has exactly six rows ordered FRG/VRG/PRG/FLD/VPA/VSM. |
| FM-B29 | FRG/VRG/PRG expose only `permanent` / `not_applicable` / `exact`; every lifecycle alternative rejects. |
| FM-B30 | Current FLD/VPA pins reach healthy or conflicted health and exact alignment, never permanent/not-applicable lifecycle. |
| FM-B31 | Superseded FLD/VPA pins reach healthy/conflicted exact or inactive unaligned states with valid worlds. |
| FM-B32 | Withdrawn FLD/VPA pins reach healthy/conflicted exact when sibling tips remain and inactive/unaligned otherwise. |
| FM-B33 | Current VSM reaches healthy/exact and conflicted exact-or-unaligned according to the complete current tip set. |
| FM-B34 | Superseded VSM reaches healthy/conflicted and exact/unaligned according to current measured-actual alignment. |
| FM-B35 | VSM exposes no context, withdrawal row, withdrawn activity, inactive health, or fabricated not-applicable alignment. |
| FM-B36 | Missing, extra, duplicate, reordered, wrong-kind, or substituted support rows reject; unrelated records cannot enter the six rows. |
| FM-B37 | Support activity, containing health, and current alignment are independently recomputed and cannot substitute for one another. |

## 5. Reverse-entry semantics

| ID | Future executable acceptance |
|---|---|
| FM-B38 | Flow reverse uses only the flow/context index and orders one entry per subject by variable, port, orientation rank. |
| FM-B39 | Variable reverse uses only the variable/context index and orders one entry per subject by flow, port, orientation rank. |
| FM-B40 | Port reverse uses only the port/context index and orders one entry per subject by flow, variable, orientation rank. |
| FM-B41 | Different orientations are separate entries; several roots/assertions of one subject remain one entry. |
| FM-B42 | Unregistered reverse endpoint yields `not_registered`, `not_declared`, empty entries; registered-but-empty yields `registered`, `not_declared`, empty entries. |
| FM-B43 | Positive reverse entries require `registered`/`declared`, carry no material/context duplicate, and match exact lookup subject payload. |
| FM-B44 | Every otherwise matching cross-context subject is excluded from all three reverse methods. |
| FM-B45 | Entry indices are contiguous only after semantic sorting; insertion order, hash seed, filenames, and authority cannot reorder them. |

## 6. Assertion disclosure

| ID | Future executable acceptance |
|---|---|
| FM-B46 | A syntactically valid absent FMA/FMW ID yields `not_found`, null optional fields, and empty index/support tuples. |
| FM-B47 | A found positive yields exact record/root/successor/withdrawal indices, activity, root health, subject conclusion/findings, role, orientation, and six support rows. |
| FM-B48 | A found withdrawal yields only `record_index`; positive-only fields remain null/empty and the carried record discloses its target. |
| FM-B49 | Exact, all three reverse methods, and assertion lookup derive byte-equal shared subject payload for the same material. |

## 7. Reconstruction, indices, purity, and preservation

| ID | Future executable acceptance |
|---|---|
| FM-B50 | Full plain-content reconstruction rejects forged Pydantic instances, `model_construct`, `model_copy`, hidden/private state, and wrong union arms. |
| FM-B51 | Boolean, negative, out-of-range, duplicate, missing, extra, reordered, or substituted material/root/group/entry indices reject. |
| FM-B52 | Forged record IDs, revision IDs, material, contexts, subjects, conclusions, findings, roles, orientations, rows, and cycles reject authoritatively. |
| FM-B53 | Material reconstruction completes before dependency access or derivation; rejected material cannot support a matched result. |
| FM-B54 | Every outer carries complete `ModelQueryMaterial` exactly once; nested rows are index-only and cannot smuggle records/material. |
| FM-B55 | Result construction and validation perform no filesystem/store/database/network/connector/clock/environment access or writes. |
| FM-B56 | Five hash seeds and reversed construction yield byte-identical results, root/group/entry order, and indices. |
| FM-B57 | The accepted 36-record pre-FM membership returns exact structured absence from all five methods with unchanged material. |
| FM-B58 | The 36-record revision, ledger aggregate, FRG/FLD/FLW and TRG/TRD/TRW counts, zero FMA/FMW, disclosures, lower digests, identities, fixtures, and artifacts remain exact. |

## 8. Execution gate

Every row requires a permanent failing-before test when it exposes missing or
defective implementation behavior, followed by the smallest repair and a
valid twin. Public contract tests compare exact fields, aliases, literal
orders, exports, and result cardinality; subset assertions are insufficient.

After owner authorization, implementation completes only after focused,
affected, isolation, full working, fresh base-only, fresh all-extras,
CAD/STEP/PDF, deterministic, dependency, compilation, whitespace, and
protected-state verification at one exact runtime commit. Until then this
matrix records design obligations only.

END OF FM-001 SLICE B ADVERSARIAL ACCEPTANCE MATRIX
