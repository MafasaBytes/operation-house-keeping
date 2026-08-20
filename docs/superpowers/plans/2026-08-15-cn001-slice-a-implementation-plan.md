# CN-001 Slice A — Implementation Plan

Branch `cn001` from accepted `main` at `7ffddca`. Red-first TDD: each bounded
group is written failing first, then implemented, then committed green.
No push, merge, reset, cherry-pick, or history rewrite. No demonstration
records appended in Slice A. No `backend/constraint_evaluation/` (Slice B).
Those statements describe the historical Slice A boundary; Slices B and C
were separately owner-authorized after acceptance.

## Commit order

### Commit 1 — Specification, ADR, plan, acceptance matrix
- `docs/superpowers/specs/2026-08-15-cn001-…-design.md`
- `docs/adr/0012-explicit-variable-constraints-and-evidence-gated-evaluation.md`
- `docs/superpowers/plans/2026-08-15-cn001-slice-a-implementation-plan.md`
- `docs/superpowers/plans/2026-08-15-cn001-acceptance-matrix.md`
- Docs only; suite unaffected.

### Commit 2 — ConstraintAnchor + public UUID4 minter + forgery tests
- `backend/system_identity/anchors.py`: `ConstraintAnchor`,
  `CONSTRAINT_ANCHOR_ID_PATTERN`.
- `backend/system_identity/minting.py`: `mint_constraint_anchor`.
- `backend/system_identity/__init__.py`: exports.
- `tests/identity_binding/test_constraint_anchor.py` (the existing red
  baseline; turns green here).
- Red-first: run the existing test (ImportError), implement, green.
- Existing `EntityAnchor`/`VariableAnchor` unchanged.

### Commit 3 — CanonicalDecimal + numeric boundary predicates
- `backend/model_kernel/contracts.py`: `CanonicalDecimal`,
  `canonical_constraint_decimal`, `NumericBoundary`,
  `ExactNumericLowerBound`, `ExactNumericUpperBound`,
  `ExactNumericInterval`, `ConstraintPredicate`.
- `backend/model_kernel/__init__.py`: exports.
- `tests/model_kernel/test_constraint_value_contracts.py` (the existing red
  baseline; turns green here).

### Commit 4 — ConstraintRegistration + VariableConstraintDeclaration + ripple
- `backend/model_kernel/contracts.py`: `ConstraintSemanticSignature`,
  `ConstraintRegistration`, `VariableConstraintDeclaration`; extend `MODEL_RECORD_ID_PATTERN`,
  `ModelRecordEvidence.record_id` pattern, `ModelRecord` union; add
  `CONSTRAINT_ANCHOR_ID_PATTERN` re-export.
- `backend/model_kernel/canonical.py`: `_PREFIX_BY_KIND` (`crg`,`vcn`).
- `backend/model_kernel/__init__.py`: exports.
- Red-first tests for record envelopes, evidence, supersedes, and semantic
  signature. Declaration lineage is keyed only by constraint anchor; predicate
  form, boundaries, inclusivity, and tokens may change.
- No store/ripple yet → suite still green (no `crg_`/`vcn_` in any collection).

### Commit 5 — Store: buckets, indexes, validation, evidence closure
- `backend/model_kernel/store.py`: `_FILENAME`, bucket dispatch,
  `LoadedModel` indexes, `validate_record_collection` (registration
  uniqueness + target closure + DAG + cycles + tips + conflicts + convergence
  + superseded history + uniform evidence closure for both kinds),
  `LoadedModel(...)` construction.
- Red-first tests: C1–C7, D1–D13 (append/load/replay/refusal).

### Commit 6 — Query: exact lookup + structured discovery
- `backend/model_kernel/contracts.py`: `ConstraintDeclarationResult`,
  `VariableConstraintCollectionResult` (carrying full `ModelRevision`,
  membership validators).
- `backend/model_kernel/queries.py`: `constraint_declaration`,
  `constraints_of_variable`.
- `backend/model_kernel/__init__.py`: exports.
- Red-first tests: E1–E8.

### Commit 7 — Forgery + ledger preservation + full suite
- `tests/model_kernel/test_constraint_revalidation.py` (and/or extend the
  above): F1–F5 (model_construct/model_copy/forged nested anchor/predicate/
  evidence/revision).
- F5: assert every existing record id / byte / revision / authority
  unchanged (freeze comparison against `7ffddca`).
- Run the focused groups, then the full accepted suite (F7).

## Ripple-site reconciliation (both kinds)

| # | Site | File | Change |
|---|------|------|--------|
| 1 | `_PREFIX_BY_KIND` | canonical.py | `crg`,`vcn` |
| 2 | `MODEL_RECORD_ID_PATTERN` | contracts.py | add `crg\|vcn` |
| 3 | `ModelRecordEvidence.record_id` | contracts.py | add `crg\|vcn` |
| 4 | `ModelRecord` union | contracts.py | 2 classes |
| 5 | record classes | contracts.py | §5 |
| 6 | `_FILENAME` (distinct literal) | store.py | add `crg\|vcn` |
| 7 | bucket dispatch | store.py | 2 buckets |
| 8 | `LoadedModel` indexes | store.py | 5 indexes |
| 9 | `validate_record_collection` | store.py | §7, §8 |
| 10 | `constraint_declaration` / `constraints_of_variable` + results | queries.py, contracts.py | §9 |
| 11 | `__init__` exports | model_kernel, system_identity | new names |
| 12 | `_check_model_record_evidence` | store.py | both kinds |

`_RECORD_ADAPTER` (TypeAdapter) auto-picks the union members — no edit.
`compute_revision_id`, `_canonical_parents`, `revalidate` are kind-agnostic —
no edit.

## Definition of done (Slice A)

- Every red-first bounded group (A–F) is green.
- The existing ledger is byte-identical: every record id, revision id, and
  authority unchanged vs `7ffddca`; no `crg_`/`vcn_` appended.
- No accepted module outside `system_identity`/`model_kernel` is modified.
- Both `crg_` and `vcn_` receive uniform evidence closure at append, load, and
  replay.
- Structural revalidation proven against `model_construct`, `model_copy`,
  forged nested anchors, predicates, evidence, records, revisions.
- The full accepted suite is green.

## Slice C bounded completion

After owner acceptance of Slices A and B, Slice C alone may append two demo
records: registration
`crg_870fe60d91056b6b1da9e3f734e5156cbb52722f6a0fc5f366f66cd40102a3df`
and declaration
`vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`.
The append was rehearsed in a disposable ledger, then repeated through public
APIs. Regression coverage freezes the prior sixteen bytes, replays every
explicit historical membership, demonstrates stored `60.4` as satisfied and
noncommitted synthetic `85` as violated, compares exact lookup with discovery,
and generates the same deterministic artifact in two clean columns.
