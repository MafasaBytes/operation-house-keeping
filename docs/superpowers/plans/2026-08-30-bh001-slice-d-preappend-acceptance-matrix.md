# BH-001 Slice D Pre-Append Acceptance Matrix

Status: exact pre-append contract owner approved; bounded authoritative append and final verification authorized

Owner resolution: add the narrowly scoped public `mint_variable_anchor()` API, commit it green before candidate allocation, then resume only the disposable pre-append rehearsal.

Historical gate: the authoritative append remained prohibited until the exact
rehearsal contract received owner approval. That gate is now satisfied; only
the approved three-record append and final verification are authorized.

Owner approval: the exact Slice D candidate identities, canonical records,
32-record revision, and 122406-byte disclosure-artifact contract are approved;
the bounded authoritative append and final verification are authorized.

## 1. Public minter gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D01 | Exact keyword-only signature and return annotation | Pinned public signature |
| D02 | UUID decoding | `var_` plus 32 lowercase hex, RFC-4122 version 4 and variant |
| D03 | Repeated calls | Distinct opaque values |
| D04 | Owner/name/optional role | Preserved exactly after contract validation |
| D05 | Invalid owner, namespace, display, role, extra, coercion | Existing contract or Python call rejection |
| D06 | Side-effect/import audit | No file, store, ledger, DB, network, environment, authority, or persistence |
| D07 | Public surface | `mint_variable_anchor` after `mint_port_anchor`; exactly one added name |
| D08 | Existing anchors/minters/vectors | Byte and behavior unchanged |
| D09 | Candidate allocation attempted before green minter commit | Gate failure |

The implementation uses one UUID4 using standard-library `uuid4().hex` and
returns the unchanged `VariableAnchor`.

No candidate may be minted before the minter commit is green.

## 2. Candidate freeze gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D10 | Allocation count | `mint_variable_anchor` once; `mint_behavior_anchor` once |
| D11 | Manifest status | Exact `non_authoritative_candidate` |
| D12 | Manifest content | Base revision, full anchors, exact API names only |
| D13 | Runtime metadata | Timestamp/path/seed/environment/process absent |
| D14 | Reconstruction | Both mappings validate through public anchor contracts |
| D15 | Remint or post-write alteration | Prohibited; stop rather than replace |
| D15a | Manifest encoding | Sorted-key compact ASCII UTF-8 canonical JSON plus one newline; byte count and SHA pinned |

After the green implementation commit, invoke each public minter exactly once,
freeze the manifest, and never invoke either minter again. Reuse only the
frozen manifest content.

## 3. Record and membership gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D16 | New record kinds | Exactly VRG, BRG, parentless BHD |
| D17 | Any VSP/VSM/entity/port/VPA/constraint/BHW/correction/binding/source/temporal record | Absent |
| D18 | Build path | Public `build_record()` only |
| D19 | Rehearsal append path before owner approval | Disposable public `ModelStore.append()` only |
| D20 | Membership | Exact `tuple(sorted((*VP001_MEMBERSHIP, *BH001_MODEL_RECORDS)))`; append order remains VRG then BRG then BHD |
| D21 | Parents/roots | Empty BHD parents; exactly one root |
| D22 | Evidence closure | Exact required citations and claim-bearing evidence |

## 4. Two-independent-disposable-ledger determinism gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D23 | Independent disposable ledger roots | Separately created temporary ledgers from identical predecessor bytes |
| D24 | Frozen anchors | Direct serialized equality |
| D25 | Record bytes/IDs/hashes | Exact equality for all three records |
| D26 | Membership/revision | Exact equality |
| D27 | Query/evaluator serialization | Exact equality |
| D28 | Artifact bytes/size/SHA | Exact equality |
| D29 | Predecessor hashes | Same aggregate before/after in both roots |
| D30 | Paths, mtimes, enumeration, hash seed, runtime clock | No artifact influence |

Each disposable ledger contains exactly one parentless BHD and exactly one
behavior lineage root.

## 5. Query and evaluator gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D31 | 29-record behavior lookup | Not registered / empty reverse / assertions absent |
| D32 | 32-record behavior lookup | Registered |
| D33 | Exact-context declaration | Declared, one healthy root |
| D34 | Reverse discovery | Exactly one row from each participant |
| D35 | BHD assertion | Current, root self, no successor/withdrawal |
| D36 | Explicit selectors | Exactly two, no discovery/cross-product |
| D37 | Evaluation | `not_executed`, no computed relation |
| D38 | Existing participant | Independently available lower evidence preserved |
| D39 | New participant | Missing admissions disclosed; none fabricated |
| D40 | Equal/different | Absent from candidate artifact |

## 6. Binding seam and preservation gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D41 | Pinned exception | Exactly candidate variable plus candidate VRG |
| D42 | Existing anchor declarations | All exact matches preserved |
| D43 | Second undeclared variable | Prospective fixture/artifact seam gate fails; model/state layers may still disclose absence |
| D44 | Divergent/substituted candidate | Prospective fixture/artifact seam gate fails; no claim of store/evaluator rejection |
| D45 | Candidate model state | `binding_declaration_absent` |
| D46 | Binding files/revisions/hashes | Unchanged |
| D47 | Explicit 9/10/11/14/16/18/28/29 histories | Unchanged |
| D48 | All 29 predecessor bytes | Unchanged in source and both roots |
| D49 | PT artifact | Accepted bytes and SHA unchanged |
| D50 | VP artifact | Accepted bytes and SHA unchanged |
| D51 | Authoritative ledger/fixture paths during pre-approval rehearsal | No writes |

## 7. Artifact and stop gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D52 | Exact accepted disclaimer | Present verbatim |
| D53 | `not_executed` explanation | Honest admission, not false relation |
| D54 | Non-inference warnings | Ownership/names/topology/VPA/semantics/constraints/correlation do not create declaration |
| D55 | Candidate identities/hashes/revision/artifact | Owner approved exactly as committed at `0905de0` |
| D56 | Authoritative append before owner approval | Historical prohibition satisfied; clean pre-append reproduction required before write |
| D57 | Push/merge/rebase/reset/cherry-pick/amend/history rewrite | Prohibited |

## 8. Approved append gate

| ID | Assertion or attack | Required result |
|---|---|---|
| D58 | Approved report | SHA-256 `0a559255359440f54f370eaf11645122089d4c0744e537c9446e20c12ffd4778` |
| D59 | Immutable allocation manifest | SHA-256 `8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07`; historical status label unchanged |
| D60 | Clean pre-append reproduction | Exact VRG/BRG/BHD bytes, hashes, membership, revision, and artifact before authoritative write |
| D61 | Authoritative physical append sequence | VRG, then BRG, then BHD through public builders and `ModelStore` |
| D62 | Per-file immediate check | Approved ID, byte count, and SHA after each append; stop on mismatch |
| D63 | Canonical membership | Exact sorted 32-record membership; physical order is not revision order |
| D64 | Approved final revision | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |
| D65 | Approved artifact | 122406 bytes, SHA-256 `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |
| D66 | Scope | Exactly three model records; no binding/VSP/VSM/port/VPA/constraint/BHW/correction/evidence mutation |
| D67 | Final owner gate | Completion report delivered and BH-001 owner accepted |

All D1-D66 fixture, replay, query, evaluator, seam, preservation, and artifact
rows are implemented and verified. D67 is closed by the final owner decision.

## Final BH-001 owner acceptance

BH-001 complete, owner accepted, adversarially reviewed, full-suite verified,
and dual-clean-checkout verified. The accepted implementation boundary is
`6fdf4d009538ddd169c1342508a104c9d61560b6`. The accepted completion-report
SHA-256 is
`3d0485e92dff57df43f31fcd2774acf6099f4f61102246dc6d8777c7ee326b5a`.
The exact 32-record revision and 122406-byte artifact remain frozen, and the
accepted evaluator disclosure remains `not_executed`.

END OF BH-001 SLICE D PRE-APPEND ACCEPTANCE MATRIX
