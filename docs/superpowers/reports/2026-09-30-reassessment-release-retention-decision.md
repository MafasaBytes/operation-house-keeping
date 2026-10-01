# Local release-evidence retention: decision receipt

2026-09-30. Planning complete; package creation remains pending owner approval.
Only the [specification](2026-09-30-reassessment-release-retention-specification.md),
[canonical manifest](2026-09-30-reassessment-release-retention-manifest.json)
and this receipt are new task artifacts.

## Commitments and scope

- Checkpoint: `e795844b441d8e5471494e715f936892f311e0e8`; no intervening commits.
- Manifest SHA-256: `89b12af58a5d8ad547114de429af6009d0b14262153d8945015ed9a99b8c58c6`.
- Specification SHA-256: `e35d54224f2794964592f4bb3e7722f7bac1e71588e121b95633ff2e073107aa`.
- Reconciliation and acceptance commitments match the supplied hashes and remain unchanged.
- Retain 3,688 unique additional blobs: 72,143,771 logical bytes; their selected source files occupy 84,529,152 physical bytes. Existing Git/archive providers are referenced, not recopied.
- The indexed package would contain 3,689 logical members in one filesystem file, exactly 76,298,002 bytes. Its digest cannot be known before creation.

## Exact proposed allocation

| Item | Bytes |
|---|---:|
| Manifest already prepared | 4,154,199 |
| Specification already prepared | 19,202 |
| This receipt already prepared | 4388 |
| Three planning files, register once | 4177789 |
| New package | 76,298,002 |
| Export-category request (package + three planning files) | 80475791 |
| Recovery-category verification receipt, maximum | 65,536 |
| Index-category five ledger records, maximum | 81,920 |
| Total charged logical envelope | 80623247 |
| Conservative physical envelope: logical + 10 * 4,096 | 80664207 |
| Future-write logical envelope excluding existing planning files | 76,445,458 |

There are seven future filesystem files (package, verification receipt and five
ledger records), plus three existing external planning entries to register;
zero new directories and zero temporary disk bytes. Sources coexist unchanged.
Package data alone rounds to 76,300,288 bytes on 4 KiB allocation. Future actual
physical allocation is unknown; close it out using lstat, without claiming hard
filesystem enforcement or exact transient peaks.

After this full proposed envelope, snapshot headroom would be:

- Exports: 1905213 bytes.
- Recovery: 59,441,458 bytes.
- Indexes: 134,307,885 bytes.
- Global logical: 2222106444 bytes; physical: 3185658225 bytes.
- Entries: 77,128; directories: 24,121.

Original preparation has only 24,693,882 unspent export bytes. A new explicit
administrative retention allocation is required within existing ceilings.
Consumed charges cannot fund it. These figures are proposals, not ledger entries.
Recheck all headroom and source identities before any future write.

Full extraction is outside the minimum: 76,297,970 additional logical bytes,
88,657,920 bytes of 4 KiB rounded file data, 3,689 files and two directories,
before metadata/receipt overhead. It exceeds current recovery headroom by
16,790,976 logical bytes. Streaming inspection needs no such copy.

## Decisions required

1. Approve exact local retention contents, including the broader host metadata,
   historical fixture authority and failure traces. Publication remains separate.
2. Approve this indexed format and review a one-off non-executing reader/writer.
3. Approve the allocation above, one creation and one static streaming
   verification, including durable accounting and retained failure evidence.
4. Acknowledge the unrecovered raw unauthorized-probe output and missing V1 peak
   evidence; preserve disclosures without reconstructing results.
5. Decide separately on a historical Git bundle or full extraction, if wanted.
   Neither is necessary when the specified Git objects are already available.

All existing modifications, historical failures and source evidence remain in
place. No runtime evidence was copied, archive built, ledger mutated, helper or
application executed, test run, dependency changed, commit made or remote used.
The pre-existing 2,428 untracked paths remain; only these three planning files
are added. The unrelated historical runner modification and empty staged scope
are preserved. The numbered ledger remains at the same 3,592 records through
3595. Final byte/preservation checks accompany the task response.

No new qualification, publication readiness or successor is claimed.
IN-001 and CI-001 remain open and unselected.
