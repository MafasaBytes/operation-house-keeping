# Slice 5 retention budget review

Recommendation: **approve the existing cap unchanged as a conditional scheduling
ceiling, not as a target or measured requirement**. The allocation includes two
complete clean-checkout slots and all-copy high-water accounting that Slice 4's
11,126,112-byte actual evidence did not include. A smaller guaranteed allowance
cannot be derived from the available full-suite artifact measurements. This is not
a claim that the whole allocation will be used, or that every possible run fits.
The original plan remains unchanged; this review explains its finite reservations.
No corpus, test, execution, operational limit or approval is created by this review.

## Verified commitments and arithmetic

HEAD: `6fe6dba27704e1a6536b00adfe71014f9bc75509`.
The complete [plan](2026-09-23-reassessment-slice5-qualification-retention-plan.md)
was read and verified at SHA-256
`cf1a1e90b57d913264f9036c652b325d20b4112eaed965a9ce7dcfbe0ce23577`.
MiB below means 1,048,576 bytes; KiB means 1,024 bytes.

| Existing category | Arithmetic | Hard candidate cap bytes | Interpretation |
| --- | --- | ---: | --- |
| Matrix/internal/fault outputs | (51 + 20 + 28 + 20 + 10) × 1 MiB | 135,266,304 | Conservative publication/control slots, not 129 expected successful outputs |
| Bound inputs/control/calibration | (72 + 28 + 20) × 1 MiB | 125,829,120 | Capture-equivalent source slots; share exact content where already supported |
| Failed/repaired attempts | 16 × (1 MiB changed input + 1 MiB output) | 33,554,432 | At most 16 additional paired attempt slots; no whole-matrix rerun allowance |
| Suite/application-gate artifacts | 2 × 64 MiB | 134,217,728 | Two bounded run envelopes, not measured suite maxima |
| Clean checkout/metadata | 2 × 256 MiB | 536,870,912 | Initial and, only if needed, repaired final checkout; includes scratch/metadata/transport copies |
| Recovery copies | 4 × 1 MiB | 4,194,304 | Four complete additional bundle copies; originals remain charged |
| Logs/streams/work/refusals | 180 × 32 KiB + 2,490,368 | 8,388,608 | Matrix streams plus supplementary/suite/termination logs |
| Indexes/manifests/dossiers | 1,024 × 8 KiB | 8,388,608 | Metadata slots, not 1,024 authorized runtime retries |
| Exports/archives | 128 × 1 MiB | 134,217,728 | Selective evidence plus framing; every archive copy counted |
| **Total new material** | **1,069 MiB** | **1,120,927,744** | Sum; no category borrowing |

Combined retained maximum = 65,433,988 historical H + 11,126,112 frozen Slice 4 Q
+ 1,120,927,744 new R = **1,197,487,844 bytes**. No unused Q capacity transfers.
This is an explicit proposed combined-retention exception, not a directory reset.
The previously disclosed 1,074,767,030 bytes of historical side material remains
preserved separately: including it yields 2,272,254,874 bytes, not a whole-disk census.

Physical reservation = 1,120,927,744 payload/high-water + 67,108,864 file-tail
reserve + 16,777,216 directory/metadata reserve = **1,204,813,824 bytes**.
Limits are 16,384 file entries and 2,048 directories. At 4-KiB allocation granularity,
16,384 × 4,095 = 67,092,480 bytes of maximum file-tail padding. The 16-MiB metadata
allowance is a conservative estimate, not an ext4 guarantee. Actual blocks must
also fit. Physical allowance is not another logical evidence allowance.

## Measured facts versus reservations

Fresh static enumeration at the accepted administrative HEAD found **1,287 tracked
regular files totaling 230,803,451 bytes**. The previous plan's 230,801,427-byte
measurement preceded the 2,024-byte acceptance record; the difference is exactly
that record, not unexplained growth. Each 256-MiB checkout slot now leaves
37,632,005 bytes for metadata and generated/transport material. Two raw source
copies would total 461,606,902 bytes, before their metadata.

Large tracked members include the 46,008,166-byte historical conditional-prediction
report, the 33,618,258-byte reassessment package and several roughly nine-MiB
selector evidence archives. This explains why copying a complete committed tree
costs far more than copying the application source alone. These bytes are historical
committed material, not newly generated reassessment results. The plan permits a
straightforward full checkout; this review does not assert every historical report
is an executable dependency or that two copies are always necessary.

Preparation measurements are **18,311,104 bytes** for the 72 original captures,
**19,498,609 bytes** for 51 prepared completed bundles, and **7,758,078 bytes** for
20 prepared replay bundles. They contain the prepared witness and are not current
runtime predictions. Slice 4 measured admitted/replay bundles at 421,258 bytes and
withholding at 375,902 bytes. Neither those examples nor their mean establishes
Slice 5's general maximum. The one-MiB slot is the unchanged bundle/capture guard;
actual executable binding and aggregate fit still need verification.

The new cap is approximately 100.75 times Q's actual 11,126,112 bytes. Comparing a
worst-case all-copy ceiling with one slice's realized usage exaggerates the expected
increase. Clean-checkout slots alone account for 512/1,069 = about 47.90% of the
new cap; they were not created under Slice 4. Regression and export slots add
256 MiB. The remaining 301 MiB covers the larger matrix, inputs, faults, repairs,
recovery and bookkeeping. None of this is a measured forecast of one GiB of results.

The 128-MiB regression allowance and 128-MiB export allowance are bounded scheduling
estimates, not minima derived from completed full-suite runs. Keeping them avoids
claiming a smaller guaranteed capacity from absent measurements, while the unchanged
stop rules prohibit using that uncertainty as permission for uncontrolled execution.
A suite's write plan must be bounded before it runs; unknown demand must stop.
Exports are optional selections with exact recovery references, not a second full
corpus. Their ceiling does not justify filling it with redundant archives.

## What must be retained, and what may be referenced

The exact 180-command matrix consists of 72 evaluations, 20 verifications,
20 replays, 28 public delivery controls and 40 calibrated-boundary invocations.
It expects 51 completed core reports (including withholding), 21 core refusals,
and 20 independent replay results. Every executed command retains its own argv,
build, streams, exit, work, reservations and observed publication state. Refusal
records and incomplete files remain evidence even when no bundle is produced.

Completed production bundles preserve their complete seven-file format and closure.
Do not replace closure bytes inside a published standalone bundle with a new
external-reference format. Different bound requests, histories, authorities,
observations and replay manifests must remain separately identified. Replayed
semantic members can equal evaluation members, but fresh work/publication evidence
must still be retained. Every physical duplicate actually written is charged.

The 20 verification commands reuse the evaluation bundles; they do not need 20
new bundle copies. Inspecting the 28 public controls shows 27 expect no successful
publication, while forged-verify examines a deliberately changed existing bundle.
Its valid/forged bytes and forged-replay references must remain exact. Collision
controls refer to retained originals; do not copy an original just for convenience.
The 28 output slots are conservative space for controls/observed failed states,
including unexpected publication by a defect, not instructions to manufacture 28
bundles. Internal graph/guard checks normally need records rather than bundles.
Any unused slots remain unused; they do not authorize additional commands.

Byte-identical input objects, policies, original prior-bundle members and frozen
oracle/package content may be recovered from an explicitly retained exact member
reference, with digest, role and complete content verified. Capture and contextual
validation charges still occur. The supported v2 prior recipe already shares members;
there is no need to write another 232,849-byte original bundle per case merely to
prove reconstruction. If a standalone/fault test requires writing such a copy,
reserve and count it. A digest without available content is insufficient.

Input directories required by the public CLI must nevertheless present the complete
required files; reference reuse does not create a new production loader or permit
hidden access to the original directory. Test evidence may reference exact immutable
inputs across commands where the command contract permits. No new hard-link,
compression or deduplication policy is introduced. Do not delete actual duplicate
outputs or failure artifacts after execution to retroactively lower charges.

## Temporary files, exports and peak coexistence

Clean checkouts are temporary in purpose but **retained and fully charged** under
this no-cleanup plan. Create only the initial checkout unless a repaired final
candidate requires the second. The existing provisioned interpreter/dependencies
remain external read-only prerequisites with exact identities; no new environment
copy or installation is included. Any necessary new bytes must be explicitly
charged before writing, not excluded under the label environment or temporary.
Full-repository Git history duplication is not assumed to fit a 256-MiB slot;
choose the approved clean-checkout route, inventory its metadata, and stop if it
cannot fit. No sparse/source omission may invalidate the required release check.

Source evidence and exported archives are **both charged**: raw inputs/outputs in
their categories, archives and any second archive copy in exports, extraction copies
in recovery or the appropriate pre-reserved input/checkout category. Charge each
physical logical copy once, with an explicit category mapping, rather than charging
a single file twice or failing to charge a duplicate. Framing and temporary archive
construction bytes also count. No compression savings are assumed.

The total is a simultaneous logical high-water allowance, not merely final retained
files. Consequently the physical reservation covers the planned coexistence of
source evidence, exported archive, recovery copy and checkout bytes. For example,
an archive cannot be built outside R and then counted only after transfer; both
construction and destination copies must fit simultaneously. There is no separate
scratch pool. Unbounded allocator/filesystem overhead is not guaranteed by the
estimate: preflight and live allocated-block guards remain necessary.

## Reruns and enforcement

The existing plan permits at most **16 additional paired input/output attempt
slots**, **two 64-MiB suite/gate envelopes**, **two checkout versions**, and **four
standalone recovery copies**. Initial matrix/control/calibration reservations are
not a new full-matrix rerun entitlement. Any extra calibration execution or rerun
must have a numbered reservation and consume the appropriate remaining allowance;
if it needs a new input/output pair beyond initial slots, it consumes a repair slot.
The two suite envelopes are byte budgets for the required suite/gate commands,
not permission to rerun whole suites indefinitely. Smaller artifacts do not create
unlimited attempt counts. No discretionary repetitions merely to use spare capacity.

Before every write, reserve worst-case growth in its category, total/combined,
file/directory counts, physical blocks and streams/error evidence. Orchestrated
children must use the reserved paths and bounded producers; detecting an excess
only after writing is insufficient. Unknown-write tests must be statically bounded
or deferred with an explicit gap before launching. Stream overflow preserves the
bounded actual prefix and incomplete/termination record, never a claimed full pass.
This static review confirms the required policy, not that a future harness already
enforces it. Enforcement readiness is an execution precondition.

No deletion recycles failed-attempt capacity. No borrowing, replacement corpus,
automatic extension, hidden /tmp spill, uncounted exported copy or changed expectation
may bypass the combined limit. If required evidence does not fit, stop for a precise
owner decision while preserving all existing bytes.

## Access and decision

Exact intended root:
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1`.
It remains absent. Fresh read-only observation on the existing parent reports
ext4 `/dev/sdc`, read-only in this execution context; statvfs also reports read-only,
with 870,077,407,232 available bytes. Capacity is not evidence of writable access.
A later preflight may propose a uniquely named create/read/remove probe through
the normal product approval boundary in the approved runtime parent, recording the
actual executor result. No probe or permission/mount/security change occurred here.

**Owner recommendation:** approve the existing 1,120,927,744-byte new cap,
1,197,487,844-byte combined maximum and 1,204,813,824-byte physical reservation,
with all existing category/count/stop constraints and only necessary copies. These
remain conditional planning ceilings. Separately authorize Slice 5 execution after
write-access and before-write enforcement preflight. Final milestone acceptance
remains pending. No package regeneration or operational-cap change is proposed.

The current plan and prior evidence were preserved. This review is the only new
file; no tests, production edits, commits or remote operations were performed.

END OF SLICE 5 STATIC RETENTION BUDGET REVIEW.
