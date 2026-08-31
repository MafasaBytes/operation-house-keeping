# ST-001 Slice A — Adversarial Acceptance Matrix

Status: owner-approved design; Slice A owner accepted at `9adcf4d9613ac96e5fb430a4b750f3053679b64d`; Slice B separately authorized; Slices C-D unstarted

Date: 2026-08-30

## 1. Scope invariant

Slice A contains identity, records, canonical/store integration, immutable
indexes, lifecycle, replay, tests, and documentation only. Any kernel state
query, state-classification package, CN runtime composition, temporal
classification, fixture record, state family, or transition capability fails
the slice.

## 2. Identity controls

| ID | Required result |
|---|---|
| A01 | `sta_` requires exactly 32 lowercase hex characters. |
| A02 | Wrong prefix, case, length, non-hex, boolean, and coercion reject. |
| A03 | `StateAnchor` exact fields are frozen, extra-forbidden, and revalidated. |
| A04 | `model_construct` and `model_copy` forged anchors reject at outer boundaries. |
| A05 | `mint_state_anchor()` exact keyword-only signature and return type are pinned. |
| A06 | Minter produces RFC-4122 UUID4 identity and distinct repeated calls. |
| A07 | Valid namespace/display/role values preserve exactly; invalid values reject. |
| A08 | Minter performs no I/O, storage, environment, network, authority, or time access. |
| A09 | Exact System Identity exports grow only by the accepted state names. |

## 3. Record and canonical controls

| ID | Required result |
|---|---|
| B01 | `srg_`, `std_`, and `stw_` ID/filename grammars are exact. |
| B02 | Kind/prefix mapping and record union gain exactly three ST arms. |
| B03 | `ModelRecordEvidence` gains SRG/STD and never STW. |
| B04 | Exact record field sets reject every extra implication-bearing field. |
| B05 | SRG embeds one complete valid StateAnchor and one subject. |
| B06 | SRG admits 1 and 64 canonical unique constraints. |
| B07 | SRG rejects zero, 65, duplicate, malformed, boolean, and coercible constraints. |
| B08 | Valid reversed constraint order yields identical bytes and ID. |
| B09 | Duplicate SRG rejects whether agreeing or divergent. |
| B10 | STD pin set exactly equals permanent SRG constraint set. |
| B11 | Pins reject missing, extra, duplicate, absent, wrong-kind, substituted, or cross-constraint VCN. |
| B12 | Valid reversed pins and parents yield identical bytes and ID. |
| B13 | Duplicate parents, self-parent, and malformed parents reject. |
| B14 | STW exact minimal fields are pinned; evidence/context/parents/outcome/reason reject. |
| B15 | Public builders match direct canonical construction and revalidate nested content. |
| B16 | Stale content-derived IDs reject after any mutation. |
| B17 | Filename/content mismatch rejects. |
| B18 | Existing record canonical bytes, schemas, IDs, and hashes remain unchanged. |

## 4. Closure, ownership, and evidence controls

| ID | Required result |
|---|---|
| C01 | Unknown subject entity rejects. |
| C02 | Unknown CRG, target VRG, or owner closure rejects. |
| C03 | Every constraint target variable embedded owner must exactly equal subject. |
| C04 | Cross-entity target rejects despite hierarchy, names, evidence, port, VPA, or behavior. |
| C05 | Shared ownership alone creates no state record or index entry. |
| C06 | SRG evidence cites subject and every CRG and contains a claim-bearing arm. |
| C07 | STD evidence cites SRG, every CRG/VCN, and contains a claim-bearing arm. |
| C08 | Every additional model-record evidence dependency closes exactly. |
| C09 | STW is uncitable; citing it rejects. |
| C10 | Failed append writes nothing and preserves prior revision exactly. |

## 5. DAG and lifecycle controls

| ID | Required result |
|---|---|
| D01 | Lineage key is exact `(state_anchor_id, AssertionContext)`. |
| D02 | Cross-state and cross-context parents reject. |
| D03 | Cross-root convergence rejects. |
| D04 | Cycles reject under iterative explicit-stack three-colour traversal. |
| D05 | A deep hostile chain validates without Python recursion. |
| D06 | One parentless root/one tip is healthy. |
| D07 | Same-root fork conflicts even when bodies are identical. |
| D08 | Partial convergence remains conflicted. |
| D09 | Full same-root convergence restores one healthy tip. |
| D10 | Independent healthy identical effective bodies corroborate without merging identity. |
| D11 | Independent healthy differing effective bodies conflict. |
| D12 | Effective body contains only state, exact context, pin mapping, and basis. |
| D13 | Evidence, authority, time, note, parents, filename, and append order do not affect body equality. |
| D14 | Selective current-tip withdrawal is valid. |
| D15 | Withdrawing every root tip leaves inactive roots indexed. |
| D16 | Unknown, wrong-kind, superseded, non-tip, duplicate, and already-withdrawn targets reject. |
| D17 | Successor and withdrawal of one tip in the same membership reject. |
| D18 | Earlier membership without successor/withdrawal revives the earlier tip. |
| D19 | Timestamp, authority, ID, filename, hash, and append order never choose a winner. |

## 6. Index and determinism controls

| ID | Required result |
|---|---|
| E01 | State registration, subject, condition, declaration, ancestry, tip, successor, and withdrawal indexes are immutable. |
| E02 | Index values are canonical tuples and contain no duplicate registration. |
| E03 | Reversed collection input produces identical indexes and revision. |
| E04 | Hash seeds and filesystem enumeration order do not affect bytes or indexes. |
| E05 | Hostile nested records revalidate before any index is trusted. |
| E06 | No query/result contract or later-slice export appears. |

## 7. Replay and preservation controls

| ID | Required result |
|---|---|
| F01 | Explicit 9-record membership/revision is unchanged. |
| F02 | Explicit 10-record membership/revision is unchanged. |
| F03 | Explicit 11-record membership/revision is unchanged. |
| F04 | Explicit 14-record membership/revision is unchanged. |
| F05 | Explicit 16-record membership/revision is unchanged. |
| F06 | Explicit 18-record membership/revision is unchanged. |
| F07 | Explicit 28-record membership/revision is unchanged. |
| F08 | Explicit 29-record membership/revision is unchanged. |
| F09 | Explicit 32-record membership/revision is unchanged. |
| F10 | Replay always uses explicit caller membership and exact reference closure. |
| F11 | Directory enumeration, prefix, kind, timestamp, and append order never reconstruct history. |
| F12 | Every pre-ST record byte remains identical. |
| F13 | CN/PT/VP/BH artifacts retain accepted hashes. |
| F14 | Authoritative demo remains exactly 32 records with zero SRG/STD/STW. |

## 8. Architecture and scope controls

| ID | Required result |
|---|---|
| G01 | Kernel import direction remains downward only. |
| G02 | No `backend.state_classification` package exists. |
| G03 | No state query methods/results exist. |
| G04 | No state ledger, store, database, cache, projection, or revision exists. |
| G05 | No condition-source, temporal selection, or CN evaluation composition exists. |
| G06 | No state family, exclusivity, completeness, winner, priority, or rollup exists. |
| G07 | No transition/from/to/trigger/action/event/guard/history/execution/control/recommendation exists. |
| G08 | No fixture, candidate state identity, model membership, or artifact mutation exists. |
| G09 | `.claude/settings.local.json` remains ignored, untouched, and uncommitted. |

## 9. Verification controls

| ID | Required result |
|---|---|
| H01 | Focused Slice A tests pass with exact count recorded. |
| H02 | Complete identity/model-kernel and affected suites pass. |
| H03 | Architecture/import-isolation and backend compilation pass. |
| H04 | Full repository suite passes. |
| H05 | Base-only clean checkout passes. |
| H06 | All-extras clean checkout passes. |
| H07 | OCP/STEP and PDF focused suites pass. |
| H08 | `git diff --check` passes. |
| H09 | Branch is `st001`; base/topology are exact; worktree is clean after report commit. |
| H10 | Nothing is pushed, merged, rebased, reset, cherry-picked, amended, or rewritten. |

## 10. Slice A stop gate

Slice A completes only when every applicable row above is green, genuine
specialist findings are reproduced red-first and retained, the completion
report is committed, the ledger remains 32 records, and Slices B-D remain
unstarted.

The owner accepted Slice A at
`9adcf4d9613ac96e5fb430a4b750f3053679b64d` and separately authorized Slice B.
Slices C and D remain unauthorized.

## 11. Final ST-001 owner acceptance

The subsequent owner-gated Slices B-D are complete. ST-001 is owner accepted,
adversarially reviewed, full-suite verified, and dual-clean-checkout verified
at implementation HEAD `0f05903af4f11fd94d6e6987247ceb9795faebd6`.
The accepted completion-report SHA-256 is
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
All historical Slice A acceptance rows remain unchanged.

END OF ST-001 SLICE A ADVERSARIAL ACCEPTANCE MATRIX
