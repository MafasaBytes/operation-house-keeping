# VS-001 implementation plan

Spec: `docs/superpowers/specs/2026-08-09-vs001-variable-value-specification-design.md`
(authoritative). ADR-0009. Branch `vs001` from `3842175` in an isolated
linked worktree; the primary checkout, the retained `vm001` worktree, and
`origin/codex/wip-pre-vm001-20260809` are never touched. Baseline gate
recorded before the first commit: fresh venv, **921 passed**. Nothing is
pushed at any point.

## Task order (small local commits, red-first per slice)

0. **Docs**: spec, ADR-0009, this plan, additive CLAUDE.md status.
1. **Kernel contracts + canonical golden vectors (red-first)**:
   `UnitReference` with the behavioural identifier-grammar guard,
   `DeclaredUnit`/`UnitNotDeclared`, `VariableValueSpecification`,
   `_canonical_parents`, prefix `vsp`, pattern/union/evidence widenings,
   **the bucket-dispatch arm** (its omission raises a raw `KeyError`),
   golden canonical vector.
2. **Multi-parent lineage (red-first)**: reference closure to `vrg`,
   same-variable parents, self-reference, DAG cycle detection, tip
   computation, `conflicted` surfacing with the revision still loadable,
   partial and full convergence, repeated contention.
3. **Kernel query**: `ModelQueries.variable_value_specification` and
   `VariableSpecificationResult`.
4. **Demo fixture**: append the single permanent `vsp_` record through the
   accepted canonical builder using the approved exact content; byte-freeze
   it; pin the pre-specification and post-specification revisions; fix the
   `test_demo_join.py` replay filter to exclude `("vrg_", "vsp_")`.
5. **Boundary tests before the facade**: the new package's AST isolation
   suite written and failing against an empty package.
6. **Result contracts and the typed error surface.**
7. **Strict evidence-consistency assessment.**
8. **Value-shape assessment.**
9. **Independent unit-evidence and lexical-relation assessment.**
10. **Complete real-timeline demonstration.**
11. **Gates**: software-test-engineer acceptance audit; adversarial
    code-review pass; every accepted finding repaired red-first.
12. **Verification**: focused, full, base-only clean checkout, all-extras
    clean checkout; boundary proof; untouched-primary proof; completion
    report. Stop for owner validation.

## Known ripple sites (verified by inspection before implementation)

`canonical.py:20-26`; `contracts.py:36`, `:98`, `:247-250`, insertion point
between `:245` and `:247`, results after `:420`; `store.py:46`, `:119-123`,
**`:146-152` bucket dispatch**, `:60-75` `LoadedModel` defaults, new pass
between `:184` and `:186`; `queries.py:72-78` guard, new method after
`:221`; `__init__.py:19-63` and `:67-117`.

## Tests that must change (deliberate, enumerated)

`test_variable_registration.py:234` prefix count 5→6; `:478` `__all__`
count; `test_mk_repairs.py` `SUPPORTED_EXPORTS`; `test_demo_model.py:12-13`
golden revision (keep the 10-record revision pinned as a new constant),
`:30` count 10→11, add `FROZEN_VS001_RECORD`;
`test_isolation.py:150-151` count and prefix tuple;
`tests/model_state/test_isolation.py:100` count 10→11;
**`tests/model_state/test_demo_join.py:162-164` replay filter must exclude
`vsp_` as well as `vrg_`**.

## Must not change

The nine `FROZEN_MK001_RECORDS` digests; `FROZEN_VM001_RECORD`;
`PRE_VARIABLE_REVISION` and its 9-record replay; the `vrg` golden vector;
`test_cross_layer_seam.py`; all of `tests/data_sources/`,
`tests/temporal_state/`, `tests/identity_binding/`; every module outside
`backend/model_kernel/` and the new package.

## Verification commands

```bash
.venv/bin/python -m pytest -o addopts="" tests/observation_compatibility \
    tests/model_kernel tests/model_state
.venv/bin/python -m pytest -o addopts="" tests/
# clean checkouts: fresh clone of branch vs001, fresh venv
#   base-only : requirements.txt + requirements-dev.txt
#   all-extras: + requirements-cad.txt + requirements-pdf.txt
```
