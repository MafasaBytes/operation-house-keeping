# FM-001 Slice A Implementation Plan

Status: corrected design accepted; Slice A authorized; Slice B and
demonstration unauthorized

Authoritative synthesis:
`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`
at SHA-256 `4179a46a9413ad7a666171572db058a7b71f8d8734af39ae3650e6bf100238e2`.
ADR-0021 records the accepted architecture.

## 1. Scope and stops

Slice A adds only `FlowMeasurementAssociation` (`fma_`) and
`FlowMeasurementAssociationWithdrawal` (`fmw_`) to the existing model-kernel
ledger. It includes exact contracts, canonical IDs, union/store dispatch,
evidence closure, correction DAGs, withdrawals, replay, immutable indexes,
generic `build_record` support, exports, and adversarial integrity tests.

Slice A does not add the five FM queries or any result class, fixture, identity
mint, authoritative append, demo, evidence/temporal access, numeric work,
FA-001, Slice B, or upper-layer import. It stops for owner validation.

## 2. Implementation sequence

1. Add strict positive/withdrawal contracts in the existing contract module.
2. Extend the exact model-record union, ID pattern, canonical dispatch, and
   store bucket/load validation without changing existing record semantics.
3. Add `fma_` evidence admission and explicitly exclude `fmw_` from
   ModelRecordEvidence.
4. Implement same-revision FRG/VRG/PRG/FLD/VPA/VSM closure, with
   context-independent VSM support and exact FMA context on FLD/VPA, plus FRG-derived
   source/sink validation.
5. Implement immutable subject, effective-body, root, parent, tip,
   corroboration, disagreement, and withdrawal indexes.
6. Add generic builder and public exports only; no FM-specific builder.
7. Add red-first hostile/replay/append-atomicity tests and valid twins.
8. Run bounded adversarial review and repair only genuine Slice A defects.
9. Run all required focused, affected, full, clean-checkout, compilation,
   dependency, determinism, and preservation checks.

## 3. Acceptance matrix

| ID | Slice A witness |
|---|---|
| FM-S01 | Positive class, kind, `fma_` ID regex, frozen fields, and exact serialization order. |
| FM-S02 | Withdrawal class, kind, `fmw_` ID regex, no evidence, and exact order. |
| FM-S03 | Generic `build_record` constructs both records; no FM-specific builder or alias exists. |
| FM-S04 | Existing prefix inventory remains collision-free; new union dispatch is exact. |
| FM-S05 | Content-derived IDs change when any normative field changes and reject forged IDs. |
| FM-S06 | Exact FRG/VRG/PRG/FLD/VPA/VSM pins are required in one selected membership; VSM is context-independent while FLD/VPA match FMA context. |
| FM-S07 | Port must belong to the FRG source or sink set; role is derived, never stored. |
| FM-S08 | Exact FLD/VPA context and subject mismatches refuse; VSM variable, dimension, token, revision, and ID mismatches refuse, with no VSM context comparison. |
| FM-S09 | Only measured-actual VSM observation role admits; command/estimate/derived roles refuse. |
| FM-S10 | Orientation is one immutable literal; invalid/unknown/boolean/subclass values refuse. |
| FM-S11 | Null, aggregate, whole-flow, storage, boundary, and control-volume loci refuse. |
| FM-S12 | Subject mutation with retained parent refuses; a changed subject requires a new root. |
| FM-S13 | Same-subject parentless roots are accepted and independently indexed. |
| FM-S14 | Identical independent bodies corroborate; different bodies disagree without winner selection. |
| FM-S15 | Same-root fork produces conflict; complete same-root convergence is accepted. |
| FM-S16 | Partial same-root repair remains conflicted; cross-root convergence, foreign parent, cycle, self-parent, and duplicate parent refuse. |
| FM-S17 | Successor of withdrawn parent refuses; sibling fork tips remain selectively withdrawable. |
| FM-S18 | Withdrawal accepts exactly one eligible current tip and is uncitable. |
| FM-S19 | Unknown, foreign, superseded, withdrawn, and duplicate withdrawal targets refuse. |
| FM-S20 | FM withdrawal is excluded from ModelRecordEvidence and evidence closure. |
| FM-S21 | Evidence references are non-empty, canonical, reference-closed, and deterministic. |
| FM-S22 | Support records may be superseded/withdrawn/conflicted without retargeting historical pins. |
| FM-S23 | Effective-body grouping includes all six support-pin IDs and excludes ancestry/evidence/audit fields. |
| FM-S24 | Append validates all dependencies before writing; every refusal leaves no file or membership change. |
| FM-S25 | Existing 36-record revision loads/replays byte-identically with no FM records. |
| FM-S26 | Explicit FM membership replay uses sorted IDs and never directory enumeration. |
| FM-S27 | Immutable indexes cover subject, flow, variable, port, context, root, and record ID for Slice B. |
| FM-S28 | Index construction is deterministic across insertion order and hash seeds. |
| FM-S29 | Hostile nested records, wrong union arms, hidden state, cycles, stale values, and scalar subclasses refuse. |
| FM-S30 | Slice A exposes no public result/index fields; this row is a negative boundary. Boolean/negative/out-of-range result-index testing belongs to Slice B. |
| FM-S31 | Canonical/store/load/append failure does not mutate existing records, IDs, or revisions. |
| FM-S32 | Public `__all__` adds only the exact Slice A names once and preserves prior order. |
| FM-S33 | Model-kernel import isolation excludes evidence, temporal, upper evaluation, connectors, and UI. |
| FM-S34 | Pure contract/canonical reconstruction and in-memory validation perform no I/O; authorized ModelStore append/load may perform filesystem I/O at its explicit boundary. |
| FM-S35 | No result/query class or five public FM query method is added in Slice A. |
| FM-S36 | No fixture, demo, identity mint, authoritative append, or FA-001 artifact is created. |

## 4. Verification gates

The focused Slice A suite must cover every FM-S row and valid twin. Complete
model-kernel and identity suites, affected FL/VP/VS/ES and architecture/
isolation suites, full repository, fresh base/all-extras checkouts, permitted
loopback reruns, CAD/STEP/PDF gates, dependency checks, compilation, multiple
hash seeds, construction-order determinism, preservation, and whitespace all
run after the final runtime change.

Completion evidence records exact commands, red-before/fixed-after defects,
changed files, commit hashes, and limitations. The completion report remains
uncommitted for owner validation unless the owner checkpoint explicitly
requires otherwise.

END OF FM-001 SLICE A IMPLEMENTATION PLAN
