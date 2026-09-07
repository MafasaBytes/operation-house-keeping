# FM-001 Slice A Preimplementation Discrepancy Report

Date: 2026-09-07

## 1. Checkpoint

The accepted documentation checkpoint is on branch `fm001` at
`22eabcf`, based on the owner-authorized baseline
`a069cb664af1638cef2168ced6034eb2d30f2f14`. The corrected synthesis is
SHA-256 `4179a46a9413ad7a666171572db058a7b71f8d8734af39ae3650e6bf100238e2`.
The lead proposal and challenger audit remain frozen at their accepted
digests. No production Slice A file, test, fixture, ledger, model record, or
artifact was changed.

## 2. Blocking lower-contract conflict

The accepted corrected synthesis requires every positive FM record to pin an
exact same-revision, exact-context model-side semantic declaration carrying
the `measured_actual` observation-role reference. It names this as the sixth
support pin:

```text
VSM -> variable_anchor_id + exact AssertionContext + measured_actual role
```

The accepted repository contract `backend.model_kernel.VariableSemanticDeclaration`
does not contain an `AssertionContext` field. Its public fields are
`record_kind`, `schema_version`, `record_id`, `variable_anchor_id`,
`declaration`, `evidence`, `supersedes`, `recorded_at`, `authority`, and
`note`. Its canonical identity and lifecycle are therefore context-independent.
The existing `VariableSemanticDeclaration` union and store/query validation
provide no context-bearing VSM value to compare.

This is not a Slice A implementation detail. Enforcing the corrected synthesis
literally would require changing the accepted VSM lower contract, its canonical
bytes/IDs, replay membership, store validation, and dependent semantic tests.
Using the VSM variable and role while silently treating it as context-
independent would instead weaken the owner-approved exact-context support
matrix. Adding a parallel context field or FM-specific semantic wrapper would
also expand the lower architecture beyond authorization.

## 3. Evidence and disposition

The conflict was established by direct inspection of:

- `backend/model_kernel/contracts.py`, `VariableSemanticDeclaration`;
- `backend/model_kernel/store.py` semantic declaration validation and indexes;
- the corrected FM-001 synthesis Sections 10, 13, and 15;
- the owner correction D5 and mandatory same-revision support matrix.

No runtime production change was attempted. The documentation checkpoint
commit remains valid and records the accepted synthesis/ADR/plan, but Slice A
implementation is stopped. No Slice B query/result class, fixture, append,
demo, FA-001 integration, or lower-contract expansion was started.

## 4. Required owner resolution

The owner must choose one bounded contract resolution before implementation:

1. amend the accepted lower semantic contract to carry exact context, with a
   separately approved canonical/replay/test repair; or
2. amend FM-001 D5/synthesis so VSM support is exact variable plus
   measured-actual role while context is supplied only by the FM/FLD/VPA
   assertion, with a new accepted synthesis digest.

This report does not choose between those alternatives and does not authorize
either repair. Until resolved, claiming Slice A completion would be false.

END OF FM-001 SLICE A PREIMPLEMENTATION DISCREPANCY REPORT
