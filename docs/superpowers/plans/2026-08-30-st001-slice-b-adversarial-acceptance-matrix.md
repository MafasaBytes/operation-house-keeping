# ST-001 Slice B — Adversarial Acceptance Matrix

Status: Slices A-B owner accepted; Slice C separately authorized; Slice D unauthorized and unstarted

Slice B is owner accepted at `23eca10a52c0124d22b4e90d80bef952ef5f9381`.

Date: 2026-08-30

## 1. Public contract surface

| ID | Acceptance criterion |
|---|---|
| B01 | Exactly four state query method names exist with exact keyword-only context signatures and named return types. |
| B02 | Six state-specific public literal aliases have the exact accepted values and order. |
| B03 | Eight result contracts have exact field names and declaration order. |
| B04 | Models are frozen, extra-forbidden, and fully revalidate nested instances. |
| B05 | `backend.model_kernel.__all__` grows by exactly the accepted ordered names; aliases and obsolete names do not leak. |
| B06 | Malformed state/entity/record inputs raise typed `ModelQueryError` before model index access. |

## 2. State lookup

| ID | Acceptance criterion |
|---|---|
| B07 | Valid-shaped absent state returns `not_registered`, explicit `None`, and canonical empty tuples. |
| B08 | Registered state discloses exact SRG, subject ERG, CRGs, target VRGs, and target-owner ERGs by indices only. |
| B09 | Condition-aligned tuples follow permanent canonical constraint order. |
| B10 | Repeated owner indices are allowed and resolve the one carried ERG without duplicating records. |
| B11 | Boolean, float, string, negative, coercible, out-of-range, and wrong-arm indices reject. |

## 3. Declaration lifecycle

| ID | Acceptance criterion |
|---|---|
| B12 | Absent registration yields `not_registered / not_applicable` with empty lifecycle rows. |
| B13 | Registered state without an exact-context root yields `not_declared / not_applicable`. |
| B14 | One healthy root yields `declared / healthy` and `one_healthy_root`. |
| B15 | Same-root fork conflicts even with identical effective bodies. |
| B16 | Partial convergence remains conflicted; complete convergence restores one healthy tip. |
| B17 | Independent healthy identical bodies corroborate in one effective-body group without merging roots or records. |
| B18 | Independent healthy different bodies yield cross-root disagreement and aggregate conflict. |
| B19 | Inactive-only roots yield `inactive / inactive`; inactive roots beside a live declared group remain disclosed and emit `inactive_roots_present`. |
| B20 | A healthy root never hides a same-root conflict or cross-root disagreement. |
| B21 | Current declaration indices contain every active tip in deterministic record-ID order. |
| B22 | Root, lineage, tip, withdrawal, group, and condition order follows only the accepted canonical display rules. |
| B23 | Timestamp, authority, record ID, filename, append order, and hash never select a winner. |

## 4. Entity reverse discovery

| ID | Acceptance criterion |
|---|---|
| B24 | Absent entity yields `entity_not_registered`, no registration index, and empty entries. |
| B25 | Registered entity with no direct SRG yields `registered` and empty entries. |
| B26 | Every directly registered state is included for exact context, including not-declared, declared, inactive, and conflicted. |
| B27 | Entries order by state anchor then first root ID and use contiguous strict `entry_index` values. |
| B28 | Constraints, variable ownership, hierarchy, names, ports, VPA, BH, evidence, observations, and satisfaction never infer an entry. |

## 5. Assertion disclosure

| ID | Acceptance criterion |
|---|---|
| B29 | Only valid-shaped `srg_`, `std_`, and `stw_` IDs are accepted. |
| B30 | Valid-shaped absent assertion returns `not_found`, explicit `None`, and empty tuples. |
| B31 | Found SRG and STW disclose event/permanent shape without declaration lifecycle fields. |
| B32 | STD with direct successor is `superseded`; withdrawn tip is `withdrawn`; otherwise it is `current`. |
| B33 | Activity remains independent from containing-root health and aggregate subject conclusion. |
| B34 | Direct successors and withdrawals are ordered by record ID; root/subject truth is recomputed independently. |

## 6. Replay and determinism

| ID | Acceptance criterion |
|---|---|
| B35 | Explicit 9/10/11/14/16/18/28/29/32 memberships return structured ST absence and retain exact revisions. |
| B36 | Earlier explicit membership without successor/withdrawal revives the older tip. |
| B37 | Historical membership is never reconstructed from directory enumeration, kind, prefix, timestamp, or append order. |
| B38 | Reversed physical record order and multiple hash seeds produce byte-identical serialized query results. |

## 7. Authoritative hostile reconstruction

| ID | Acceptance criterion |
|---|---|
| B39 | Material must be complete, unique, exact-revision, and canonical order; missing, duplicate, extra, reordered, or substituted records reject. |
| B40 | Mixed revision, state, entity, context, condition, pin, variable, owner, root, or union arm rejects. |
| B41 | Forged roots, ancestry, successors, tips, withdrawals, health, body equality, corroboration, conclusions, findings, indices, counts, and order reject. |
| B42 | Nested `model_construct`, `model_copy`, hidden-extra, and stale-content-ID attacks reject. |
| B43 | Outer validation reconstructs nested rows from serialized content and never trusts existing model instances. |
| B44 | Result material occurs exactly once; nested rows contain indices and no duplicate authoritative records. |
| B45 | Validation succeeds with `ModelStore`, filesystem reads, database/network calls, and write APIs monkeypatched to fail. |

## 8. Architecture and scope

| ID | Acceptance criterion |
|---|---|
| B46 | Kernel imports no state-classification, model-state, temporal, binding, semantic, CN, source, CAD, or PDF module. |
| B47 | Queries own no store, path, filesystem, database, cache, projection, network, clock, or write capability. |
| B48 | No classifier, source selector, computed match, transition, state family, exclusivity, completeness, priority, winner, or persistence symbol is added. |
| B49 | No fixture, ledger record, identity, membership, canonical byte, store rule, or Slice A index changes. |

## 9. Preservation and verification

| ID | Acceptance criterion |
|---|---|
| B50 | Demo remains exactly 32 records at the accepted `mrv_d7d...` revision with zero SRG/STD/STW. |
| B51 | All predecessor bytes and CN/PT/VP/BH artifacts retain accepted hashes. |
| B52 | Focused Slice B, all ST, model-kernel, affected downstream, architecture, compile, and full repository suites pass. |
| B53 | Fresh base-only and all-extras checkouts pass; sandbox-denied loopback setup is reported and rerun separately. |
| B54 | Focused OCP/STEP/PDF paths pass where dependencies are installed. |
| B55 | Both clean-tree and full milestone-range `git diff --check` pass after the final report commit. |
| B56 | Branch and topology remain exact; tree is clean; nothing is pushed, merged, rebased, reset, cherry-picked, amended, or rewritten. |

## 10. Stop gate

Every applicable row must be demonstrated before Slice B handoff. Confirm
explicitly that Slices C and D remain unstarted and unauthorized.

Owner question after delivery: accept Slice B and separately authorize Slice C?

## 11. Final ST-001 owner acceptance

The subsequent owner-gated Slices C-D are complete. ST-001 is owner accepted,
adversarially reviewed, full-suite verified, and dual-clean-checkout verified
at implementation HEAD `0f05903af4f11fd94d6e6987247ceb9795faebd6`.
The accepted completion-report SHA-256 is
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
All historical Slice B acceptance rows remain unchanged.

END OF ST-001 SLICE B ADVERSARIAL ACCEPTANCE MATRIX
