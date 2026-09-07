# TA-001 Final Owner Acceptance

Date: 2026-09-07

## 1. Acceptance decision

The owner accepts corrected TA-001 at the exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`.

The current branch documentation HEAD is
`4d1452074e968a534762c019c2dfb328e064e3fa`. That HEAD contains only the
truthful Slice B verification-status documentation commit after the tested
implementation; it is not a different runtime implementation. This final
administrative closeout records acceptance without changing the tested code,
tests, fixtures, evidence, ledgers, identities, memberships, canonical
bytes, or artifact generators.

TA-001 is complete, owner accepted, adversarially hardened, and
dual-clean-checkout verified. The accepted Slice A implementation is
`76738ac0d098eb59b0fec4f6970aa862528647d9`, with acceptance commit
`2e92b3a89287f4b5f04938c13ea562180f838b19`.

## 2. Accepted documents and immutable report

The corrected synthesis remains byte-identical at SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`.

The frozen Slice B completion report remains unchanged at 557 lines, 30,391
UTF-8 bytes, SHA-256
`3765001e5ebae2bd22211f0108cb7d0bd03e71fad9645ecf4e472d291b1233b3`, ending
with `END OF TA-001 SLICE B COMPLETION REPORT`.

The Slice A completion report and owner acceptance record remain unchanged at
their accepted repository digests. No historical report was rewritten and no
accepted digest was replaced by a later representation.

## 3. Resolved corrections

The owner accepts the finite-float correction: exact built-in finite floats
are admitted and deterministically encoded as JSON numbers; subclasses,
NaN, and infinities are rejected before derivation. Lower models remain
unchanged.

The owner accepts corrected T43: candidate zero remains the valid twin, while
substituted or malformed candidate inputs reject through the typed malformed-
input path before derivation. No global parity or issue vocabulary was
renamed.

The exact ordered 28-name `backend.transition_assessment.__all__` remains
preserved. No alias, facade, second consumer, or alternative public name was
added.

## 4. Adversarial closure

T01–T74 are closed with permanent executable evidence. The final reachability
matrix independently reaches all 22 issue codes, verifies their normative
order, and retains independently applicable multi-issue diagnostics.

The red-first record contains 25 failing pytest cases across eight red runs.
Each genuine defect was encoded as a permanent failing test before its narrow
repair, and every repaired path has a valid twin. The repaired categories
include structural scheduling, aggregate-budget admission, hostile scalar and
model handling, invocation-local preflight, raw-error suppression, strict
union-arm reconstruction, compact-result hidden-state rejection, and the
finite-float/T43 boundary.

Independent architecture/import review, coverage review, backend review, and
final backend re-review were completed. The final backend review found no
remaining in-scope production defect.

## 5. Verification accepted before closeout

The focused TA suite was 120 passed in 394.06 seconds. The architecture and
isolation selection was 32 passed in 20.95 seconds. The affected-package gate
was 2,092 passed in 813.85 seconds. The final backend review gate was 62
passed in 142.56 seconds.

The working all-extras repository suite was 3,800 passed in 1,424.70 seconds
with no loopback setup error. A fresh base-only checkout produced 3,764
passed, 35 optional-extra skips, and one sandbox loopback setup error; the
exact permitted rerun passed, reconciling 3,765 runnable passes. A fresh
all-extras checkout produced 3,799 passed and one sandbox loopback setup
error; its exact permitted rerun passed, reconciling all 3,800 tests.

Explicit CAD/STEP/PDF coverage was 120 passed in 41.06 seconds. The base and
all-extras installation sequence was corrected after pip hash-option leakage;
the intended fresh installations then succeeded. Dependency checks reported
no broken requirements, and backend compilation passed in working, base, and
all-extras environments.

The TA deterministic result remained 195,429 bytes with SHA-256
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97` and no
trailing newline across five hash seeds and all three environments. The
accepted lower reproductions remained unchanged at their recorded digests.

## 6. Preservation

The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The ledger aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
Family counts remain FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`.

The FL disclosure remains 660,516 bytes with SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
Historical records, memberships, evidence, fixtures, canonical artifacts,
and accepted lower deterministic material remain unchanged.

The owner-local `.claude/settings.local.json` remains ignored and byte-
identical at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.
It is not staged.

## 7. Architectural meaning and exclusions

TA-001 is a pure, read-only carried-result leaf. Its only public conclusion
is bounded evidence support or bounded evidence non-support for the declared
endpoint pattern. It makes no transition occurrence or non-occurrence claim,
continuity claim, temporal-cohort claim, causal or flow claim, control claim,
diagnosis, recommendation, safety, probability, confidence, persistence,
identity, or truth endorsement.

TA owns no store, cache, ledger, durable identity, facade, demonstration,
second consumer, connector, ambient clock, or write path. Positive test worlds
are disposable and uncommitted. No authoritative result artifact was added.

TA-001 has no Slice C and no demonstration slice. No subsequent milestone is
opened or authorized by this acceptance. Nothing was pushed or merged in this
closeout.

## 8. Administrative verification

Before this record was written, the branch was `ta001` at
`4d1452074e968a534762c019c2dfb328e064e3fa`; the only ordinary untracked file
was the unchanged Slice B completion report. All required digests, line and
byte counts, ending markers, preservation values, and settings hash matched
the owner checkpoint.

The staged closeout will contain only this acceptance record and the minimum
current-status documentation edits in `CLAUDE.md`, `README.md`,
`backend/transition_assessment/README.md`, ADR-0020, and the Slice B plan.
The corrected synthesis and frozen Slice B report are not staged as modified
content. `git diff --check` is required for the staged closeout and the full
TA milestone range. The final tracked and ordinary untracked tree must be
clean after commit, with only ignored owner-local state remaining.

Required current status is:

> TA-001 complete, owner accepted, adversarially hardened, and
> dual-clean-checkout verified.

## 9. Closeout boundary

This record is one documentation-only administrative acceptance. It does not
modify runtime or behavioral tests, fixtures, source evidence, temporal data,
model records, ledgers, memberships, accepted canonical bytes, or artifact
generation logic. A later architecture or ADR decision requires a separate
owner instruction.

END OF TA-001 FINAL OWNER ACCEPTANCE
