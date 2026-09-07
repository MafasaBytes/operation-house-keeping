# FM-001 Slice A Completion Report

## 1. Authorization and checkpoint

Slice A was resumed after the owner’s VSM context resolution. Branch: `fm001`.
Documentation resolution commit: `80aec84`. Runtime implementation commit:
`64eaf8a`. Slice B, fixtures, demonstrations, ledger appends, and FA-001
remain unauthorized.

## 2. VSM resolution applied

The existing context-independent `VariableSemanticDeclaration` was preserved.
FM support validates exact variable, dimension, system, edition, code,
revision, and record ID. Only FLD and VPA compare the exact FMA context.
No VSM migration or wrapper was introduced.

## 3. Implemented Slice A surface

Added `FlowMeasurementAssociation` (`fma_`) and
`FlowMeasurementAssociationWithdrawal` (`fmw_`) contracts with frozen,
extra-forbidden fields, exact field order, strict IDs, canonical evidence and
parent handling. Added canonical prefix dispatch, model-record ID admission,
union dispatch, store bucket dispatch, and public exports.

## 4. Red-first and fixed evidence

The accepted discrepancy was reproduced before repair as the missing-context
lower-contract mismatch. The documentation resolution corrected the contract
without changing the lower model. Runtime smoke validation confirms both new
classes import and expose the exact declared fields. Existing model-kernel
tests reach the historical exact-export-count assertion because the two
authorized Slice A exports are now present; that expected baseline test must
be updated by the owner-approved FM test tranche before claiming a green
milestone.

## 5. Acceptance-row mapping

FM-S01–S05 are covered by the new contracts, canonical prefix table, union,
and generic builder path. FM-S06–S23, FM-S24–S31, and FM-S33–S36 remain
implementation/test work beyond this bounded forward commit and are not
claimed complete.

## 6. Verification commands

`python -m compileall -q backend/model_kernel` passed.
`git diff --check` passed after the runtime commit. Focused
`python -m pytest -q tests/model_kernel --disable-warnings --maxfail=1`
stopped at the existing exact-export-count assertion (`203` expected versus
`205` after the two authorized exports). No full-suite or clean-checkout
claim is made.

## 7. Preservation and limitations

No evidence, fixture, ledger, identity, temporal, EA, TA, or VSM data was
changed. The accepted model revision, historical records, and protected
artifacts were not regenerated. Store lifecycle closure, indexes, append
atomicity, replay witnesses, and adversarial FM tests remain to be completed
under Slice A authorization.

## 8. Changed files and commits

Documentation resolution: `80aec84`.
Runtime Slice A contracts: `64eaf8a`.
Changed runtime files: `backend/model_kernel/contracts.py`,
`backend/model_kernel/canonical.py`, `backend/model_kernel/store.py`, and
`backend/model_kernel/__init__.py`.

END OF FM-001 SLICE A COMPLETION REPORT
