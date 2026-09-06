# EA-001 Slice C1 Implementation Plan

Date: 2026-09-06

Status: owner-authorized bounded implementation plan

## 1. Objective and boundary

Implement only the corrected Slice C1 contracts and pure occurrence-alignment
derivation in the new leaf package `backend.evidence_alignment`. Add focused
red-first tests for corrected rows C01-C38. Do not expose the final root-package
`__all__`, change lower packages, perform I/O or reselection, add persistence,
or begin Slice C2.

## 2. Red-first contract gate

Add focused tests that construct real accepted EA and VS results, then pin the
four request fields, nineteen result fields, ordered literals, typed error,
carry-once reconstruction, all success/refusal reasons, exact occurrence and
endpoint closure, duplicate-match reachability, no-I/O behavior, import
isolation, and deterministic output. Run them before production modules exist
and record the actual failure/pass count in the completion report.

## 3. Minimal implementation

Create `contracts.py`, `derivation.py`, and a marker-only `__init__.py`. Deeply
reconstruct public lower content at the request boundary, call the accepted
pure EA validator once for each non-refused selection, derive only the approved
relations, and make result validation recompute every compact derived field.
Import only public lower contracts/functions, Pydantic, and standard-library
facilities.

## 4. Adversarial review and bounded repair

After first green, inspect hostile reconstruction, result construction,
precedence, exact-match cardinality, endpoint closure, and I/O/import boundaries.
Turn every reproduced defect into a failing focused regression before repair.
Do not reopen architecture or introduce another consumer.

## 5. Authorized verification and stop

Run focused C1, accepted EA/lower, architecture/no-I/O, relevant VS/VM,
preservation/reproduction, compilation/dependency, and working/range whitespace
checks. Write and commit the numbered C1 completion report and an exact status
update only after verification. Stop for owner acceptance; C2 remains
unauthorized.

END OF EA-001 SLICE C1 IMPLEMENTATION PLAN
