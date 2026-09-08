# FM-001 Slice A Owner Acceptance

Date: 2026-09-09

Status: repaired FM-001 Slice A owner accepted; Slice B contract correction
authorized for documentation only; Slice B implementation unauthorized

## 1. Accepted implementation

The owner accepts repaired FM-001 Slice A at exact tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6` on branch `fm001`.

The accepted runtime scope consists only of the two model-ledger records,
their canonical/store/evidence/correction/withdrawal integration, immutable
indexes, replay, generic builder/export integration, and adversarial tests.
The accepted integrity repair compares current effective-body sets between
distinct active roots and completes positive coverage for all four immutable
orientation literals. It preserves context-independent VSM.

## 2. Frozen completion evidence

The accepted completion report is:

`docs/superpowers/reports/2026-09-07-fm001-slice-a-completion-report.md`

Immediately before this acceptance commit it was verified as 363 lines and
17,533 UTF-8 bytes at SHA-256
`93c089269b90499de1b7aabf748c13a7f5ba53d5898bdea80347ce9eb6a460de`.
Its 18 numbered sections are contiguous and it ends with
`END OF FM-001 SLICE A COMPLETION REPORT`. It is committed without changing
its reviewed bytes.

The byte-identical pre-repair historical receipt remains at
`docs/superpowers/reports/2026-09-08-fm001-slice-a-pre-repair-completion-report.md`,
SHA-256
`9d8a0f4a075267b75d6369740b348d0f2641b66ccd221d72354abcd22a6b75fa`.

## 3. Accepted verification

The owner accepts the recorded focused 53, affected 195, model-kernel 1,707,
identity 327, and architecture/isolation 82 passing tests. The working full
suite passed 3,853 tests uninterrupted. The fresh base-only column recorded
3,817 passing tests, 35 expected optional-extra skips, and one sandbox
loopback setup error followed by one separately permitted passing rerun. The
fresh all-extras column recorded 3,852 passing tests and one sandbox loopback
setup error followed by one separately permitted passing rerun. The explicit
CAD/STEP/PDF gate passed 160 tests.

Five hash seeds and reversed construction reproduced the exact 30,485-byte
witness at SHA-256
`c880b68f0669cd8fa391ef11ebb136fb968389f718a4c57b9b16f50d16413df7`.
The owner accepts the report's split accounting: sandbox setup errors are not
relabeled as uninterrupted aggregate passes.

Immediately before this administrative commit, the applicable documentation
and status gate passed 26 tests in 3.32 seconds. Staged and milestone-range
whitespace checks passed, and staged paths were restricted to the frozen
report, this acceptance record, and current documentation status.

## 4. Preservation

The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`, TRG/TRD/TRW remains `0/0/0`, and authoritative
FMA/FMW remains `0/0`. The ledger aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.

The FL disclosure remains 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
The accepted TA result, both accepted lower-material reproductions, VSM bytes,
identities, memberships, fixtures, evidence, canonical artifacts, and owner-
local settings remain unchanged.

## 5. Accepted truth boundary

An FMA is only an evidence-backed model declaration that one exact variable
has direct-measurement relevance to one exact participant port of one exact
logical flow in one exact context and orientation under six exact support
pins. It does not establish an observation, measurement, value, amount, rate,
physical sensor location, active or occurred flow, continuity, conservation,
causality, correctness, safety, health, diagnosis, or recommendation.

The accepted Slice A implementation adds no query conclusion, evidence or
temporal access, upper composition, durable association identity, new store,
fixture, demonstration, or authoritative append.

## 6. Slice B correction authorization

The owner authorizes only a documentation-level correction of the Slice B
public contract. The five accepted query responsibilities and architecture
remain fixed. The correction must separate support activity, lineage health,
and alignment; represent forked-root body cardinality truthfully; define one
subject-level reverse entry; pin every reachable literal/model/export; and
retain carry-once, authoritative, no-I/O reconstruction.

Slice B implementation remains unauthorized until the owner accepts the exact
corrected contract. No second challenger, implementation, fixture,
demonstration, authoritative append, FA-001 work, or subsequent milestone is
authorized by this record.

## 7. Acceptance boundary

This administrative acceptance changes documentation only. It does not
modify runtime code, tests, fixtures, source evidence, temporal data, model
records, ledgers, identities, memberships, indexes, canonical bytes, or
artifact-generation logic.

This record accepts repaired Slice A, not all of FM-001. Slice B requires
separate contract acceptance and implementation authorization.

END OF FM-001 SLICE A OWNER ACCEPTANCE
