# VM-001 implementation plan — variable membership + bound model-state query

Spec: `docs/superpowers/specs/2026-08-09-vm001-model-state-design.md`
(authoritative; this plan is ordering and verification only). ADR-0008.
Branch `vm001` from `682fa53` in an isolated linked worktree; the primary
checkout (owner WIP, 7 known failures) is never touched. Baseline gate
recorded: fresh all-extras venv, **757 passed, 0 failed** at `682fa53`.
Nothing is pushed at any point.

## Task order (small local commits, red-first per slice)

0. **Docs commit**: this plan, the spec, ADR-0008, additive CLAUDE.md
   Status correction (stale current-phase wording only; historical
   sections preserved verbatim).
1. **Temporal prerequisite (own commit)**: red tests for missing,
   corrupted, and unreadable temporal storage across representative read
   methods → wrap the seven public `TemporalQueries` reads:
   `sqlite3.Error` → `TemporalStoreError("TEMPORAL_STORE_UNAVAILABLE")`,
   path-free, cause chained. All 51 existing temporal tests stay green;
   no schema/row change.
2. **Part A contracts + store (red-first)**: matrix sections A/B —
   `VariableRegistration`, prefix map, patterns, union, evidence pattern,
   bucket dispatch, separate `LoadedModel` mapping, duplicate behaviors
   (three pinned cases), owner-entity closure at load/append/replay.
3. **Part A queries + surface**: matrix section C — `variable()`,
   `variables_of()`, result contracts, `_require_variable_anchor_id`,
   `__all__` 47, leakage-sweep extension, hierarchy-absence probe,
   seam-test widening to embedded VariableAnchors.
4. **Demo fixture**: byte-hash pin the nine records FIRST (must pass
   pre-append), append the one `vrg_` record, pin old and new goldens,
   old-revision replay → `not_registered`.
5. **IB reverse lookup (red-first)**: matrix section D —
   `DeclaredBindingSummary` (lifecycle_flags), `DeclaredLocatorEntry`,
   `DeclaredPropertyLocatorsResult`, `declared_property_locators`,
   `BINDING_ANCHOR_ID_INVALID`.
6. **model_state (red-first)**: matrix sections E/F/G/X — contracts with
   all invariants (incl. amendment-1 validators), facade pipeline,
   attachment precedence, AST isolation + no-store + no-sqlite +
   no-private-access tests, end-to-end demo join.
7. **Gates**: software-test-engineer acceptance audit; adversarial
   code-review pass; every accepted finding repaired red-first in its own
   commit.
8. **Verification**: focused (four suites), full worktree suite, base-only
   and all-extras clean checkouts from fresh clones/venvs; per-commit
   boundary proofs; primary-checkout byte-untouched proof; final owner
   report. Stop for owner validation; do not push.

## Mandatory regression pins

Old golden `mrv_c28b6301…` replayable; nine committed records
byte-identical (sha256 pins); binding sets and raw/temporal fixtures
byte-identical; hierarchy results unaffected by the vrg record; the
`test_mk_closure`/`test_mk_repairs` suites untouched and green; existing
193+ IB tests and 51 temporal tests green; kernel AST isolation unchanged
except the added `model_state` prohibition.

## Verification commands

```bash
.venv/bin/python -m pytest tests/model_state tests/model_kernel \
    tests/identity_binding tests/temporal_state -o addopts="" -q
.venv/bin/python -m pytest tests/ -o addopts="" -q
# clean checkouts: fresh clone of branch vm001, fresh venv
#   base-only: requirements.txt + requirements-dev.txt
#   all-extras: + requirements-cad.txt + requirements-pdf.txt
```
