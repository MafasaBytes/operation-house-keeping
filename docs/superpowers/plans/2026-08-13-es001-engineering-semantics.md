# ES-001 implementation plan — 14 groups, docs first

Authoritative design:
`docs/superpowers/specs/2026-08-13-es001-engineering-semantics-design.md`
(owner-accepted 2026-08-13). ADR: `docs/adr/0011-…`. Acceptance matrix:
`docs/superpowers/plans/2026-08-13-es001-acceptance-matrix.md`.

Branch `es001` from `main` at `8cb5f1e` (all-extras baseline
1435 / 0 / 0). Every completed implementation group leaves the branch
green in both clean-checkout columns. Failing tests are demonstrated
before their fix but committed with the corresponding fix; red-baseline
documentation may be committed separately (doc-only). Records are
authored only through the canonical builders; ids are never fabricated.
`.claude/settings.local.json` is owner-local state: never staged,
modified, or committed.

## Groups (mandated order)

1. **Docs**: this plan, the specification, ADR-0011, the acceptance
   matrix. (Doc-only commit.)
2. **Failing-before integrity evidence** (doc-only): (a) enumerate the
   byte-freeze gap — the accepted freeze maps pin only 11/14 model and
   7/11 binding records; list the unpinned files and their sha256
   digests; (b) reproduce that a `VariableValueSpecification` carrying
   `ModelRecordEvidence` for an absent model record currently loads
   (`validate_record_collection` checks evidence only for
   relationship assertions), with the captured output.
3. **Model-kernel integrity repair**: one uniform evidence-closure rule
   for every evidence-bearing model claim (`rel`, `vsp`, and — when it
   lands — `vsm`): every `ModelRecordEvidence.record_id` must belong to
   the supplied collection (`MODEL_REFERENCE_INVALID`), across load,
   prospective append, and explicit replay subsets. Tests: the Group-2
   reproduction flips red→green; committed-ledger regression (all
   records load, all ids verify); replay-subset omission of cited
   evidence invalidates; the completed byte-freeze pins (3 model + 4
   binding digests added; no existing digest altered).
4. **Part A**: `QuantityKindReference`/`ObservationRoleReference`,
   `VariableSemanticDeclaration` (`vsm`), canonical prefix, pattern and
   union and bucket and evidence-pattern widening, validation pass
   (registration closure; same-variable same-dimension multi-parent
   lineage; acyclicity; per-(variable, dimension) tips; evidence
   closure), `LoadedModel` mappings, `variable_semantics` query +
   result contracts, `__all__` 54→62. Focused run:
   `tests/model_kernel`.
5. **Part B1**: `backend/source_interpretation/` errors, contracts
   (`spi`/`spr`/`spc`/`spj`, `InterpretationRevision`), canonical
   identity (hardened `build_record`; domain-tagged `irv_` material;
   golden byte-parity vectors with the accepted canonicalization).
6. **Part B2**: validating store (append validates the prospective
   collection; all-or-nothing load; explicit-id `load_revision`),
   lifecycle validation (multi-parent same-locator same-dimension
   supersession; retraction; narrowing-only closure, max one;
   standalone rejection), `LoadedInterpretationSet` indexes.
7. **Part B3**: `membership()` promotion in identity_binding (docstring
   + README note + behaviour-vector contract test; zero behavior
   change), then the convergent resolver: per-dimension eight-case
   classification keyed by canonical body bytes over active current
   tips, `PropertyInterpretationResult` contracts
   (`revalidate_instances="always"`), naive-`at` refusal, permutation
   and boundary vectors. Focused run: `tests/source_interpretation`
   (+ the identity-binding suite unchanged).
8. **Part C**: `backend/semantic_compatibility/` contracts (authoritative
   dimensional verdicts with per-dimension reason chains incl. the
   evidence-consistency gate; the total findings derivation; the
   eight-clause `declared_semantics_compatible`; verbatim-carriage and
   revision invariants) and facade; isolation/AST tests. Focused run:
   `tests/semantic_compatibility`.
9. **Red-baseline evidence for the ledger appends** (doc-only): apply
   the five authored records in a full worktree copy through the
   validating stores; run the complete suite from the copy; enumerate
   every failing pin and map each to its Group-10 migration.
10. **Appends**: two `vsm` records to `models/demo-printer` (14→16) via
    `build_record` + `ModelStore.append`; the new
    `interpretations/demo-printer` set with three `spi` records (0→3)
    via the new builders + validating store. In the same commit: every
    pin migrates — new CURRENT model revision constant; count literals;
    per-record authority map entries (`es001_demo_fixture`); byte-freeze
    map extensions (existing digests untouched); the 14-record revision
    becomes an explicit-id replay pin; the `irv_` first-revision golden.
11. **Completion demonstration**:
    `tests/semantic_compatibility/test_demo_semantics.py` — the full
    chain over committed fixtures with per-arrow disclosures, the exact
    findings set {declared_semantics_compatible, unit_identity_exact,
    source_unit_absent_but_interpreted}, and the negative guards
    (pre-vsm replay; empty interpretation set; early cutoff;
    evidence-subtree sweeps; whole-object VS-001 equality). Offline.
12. **Docs**: new module READMEs (limitations verbatim-asserted),
    touched-module README notes, and the exact proposed CLAUDE.md
    status paragraph — presented to the owner, NOT applied.
    **Checkpoint: stop for owner approval before Groups 13–14.**
13. **Adversarial review and bounded repairs** where findings are
    reproduced (regression-first).
14. **Dual clean-checkout verification**: base-only and all-extras
    columns from fresh clones and fresh venvs; all-extras must exercise
    OCP without skips; one demo query's result JSON byte-identical
    across columns.

## Acceptance gates

- The acceptance matrix is the test plan; every row lands as a test or
  is explicitly mapped to one.
- Accepted tests change only via the matrix's extend-only register
  (freeze maps, authority maps, count guards, FORBIDDEN import lists);
  deleting, skipping, or loosening an accepted assertion is a rejection.
- Ledger evolution is fixed: models 14→16, interpretations 0→3, both
  binding sets unchanged, no committed `spj`.
- Every pre-existing record byte-identical; historical revisions replay
  from explicit id lists; no prefix-filter membership anywhere.
