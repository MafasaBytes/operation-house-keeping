# Slice 5 retention correction — bounded owner-approval candidate

Static proposal only; qualification stays paused. This does not amend effective
caps, allocate a new corpus, execute a test or authorize a new dependency. It
preserves the original plan, reports, oracle history and all existing evidence.

## Verified authority and current census

HEAD/main: `1647c3931582b8183d00aedaaae2d959dd908fc8`.
Production-tested commit `eb7bd53c3ff8af0736e9ab3f3f0d61d4cbb1d3c2` and focused-test
commit `f66ac30fb95b81b265e10d2115d57d8916241109` resolve and are ancestors.
[Qualification report](2026-09-24-reassessment-slice5-revision-core-qualification.md)
was read; SHA `29ffd6aee9cdc8eaef4eb4aa923cec442ff47f322eaba34e7eb7a43a15b99a72`.
The complete [approved plan](2026-09-23-reassessment-slice5-qualification-retention-plan.md)
SHA `cf1a1e90b57d913264f9036c652b325d20b4112eaed965a9ce7dcfbe0ce23577`
requires conjunctive categories, all copies/scratch, no borrowing and stop before
unknown/excessive demand. Its full-suite row explicitly was a scheduling provision,
not measured repository-suite capacity. Nothing resets per directory or process.

R remains exactly:
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1`.
No r2. Fresh read-only census including registered external exports: 107,359,056
logical bytes, 120,356,864 allocated bytes, 3,678 files, 365 directories. Frozen
parents H+Q remain 76,560,100; combined 183,919,156. Parent bytes were not rewritten
or newly claimed exhaustively rehashed. Historical side material 1,074,767,030 bytes
remains separately disclosed and untouched. Existing archive copies count in exports.

This candidate itself is the only new file: its exact byte size/digest accompanies
the receipt. Add its size to the exports and combined census above; it is explicitly
authorized planning material, not an uncounted runtime output. Register that exact
file before any resumed runtime writes. Runtime indexes remain untouched this turn.

| Category | Current bytes | Exact remaining under old cap | Proposed cap bytes |
|---|---:|---:|---:|
| outputs | 19,646,652 | 115,619,652 | 103,809,024 |
| inputs | 18,762,363 | 107,066,757 | 71,303,168 |
| repairs | 3,309,000 | 30,245,432 | 188,743,680 |
| regressions | 0 | 134,217,728 | 134,217,728 |
| checkouts | 0 | 536,870,912 | 1,358,954,496 |
| recovery | 0 | 4,194,304 | 4,194,304 |
| logs | 36,112 | 8,352,496 | 8,388,608 |
| indexes | 181,338 | 8,207,270 | 8,388,608 |
| exports | 65,423,591 | 68,794,137 | 134,217,728 |

**No byte category is already full.** Upcoming clone writes cannot be reserved;
the independent **16/16 attempt count is exhausted**, despite 30,245,432 repair
bytes remaining. These are distinct constraints.

## Blocked writes and source accounting

Read-only `git ls-tree -rl HEAD`: 1,298 tracked files, 96 source directories,
274,469,605 payload bytes; rounded file allocation at 4 KiB is 277,377,024.
.git/objects: 2,633 files, 258 directories, 172,897,771 logical bytes;
rounded file allocation 180,764,672. Source plus objects: **447,367,376 bytes**
and **458,141,696 rounded allocated file bytes**, before other Git files/directories.
These are measured present components, not an executed clone or guaranteed future size.

`tests/applications/bounded_decision_workflow/test_s7_release.py:26–30` runs local
`git clone --quiet --no-hardlinks` then checkout. Lines 54–55 create source-0 and
source-1; line 125 creates accepted-source at historical commit
`c37c24ee50667121d6b2dc4739aa3b7d12825c96`. That historical tree has 854 files and
73,827,366 payload bytes (75,718,656 rounded file bytes). The unchanged clone first
checks out current HEAD, so its initial peak is another full current tree, even
though later historical checkout shrinks the materialized source. We budget that
peak and do not recycle its slot or delete evidence. Git's ordinary checkout of
source files is not permission to remove test results.

| Required write | Destination/purpose | Logical projection | Allocated projection | Old governing allowance |
|---|---|---:|---:|---|
| source-0 | R/regressions/full-suite/<test>/source-0; independent current Git tree | 447,367,376 + non-object Git metadata | 458,141,696 + directories/metadata | Regression category has 134,217,728 total free; checkout category not automatically applicable |
| source-1 | same test/source-1; independent construction/replay comparison | same | same | Same shared regression allowance; even hypothetical checkout slot is only 268,435,456 |
| accepted-source | R/regressions/full-suite/<historical-test>/accepted-source; actual historical replay | initial same; later 246,725,137 + Git metadata | initial same; later 256,483,328 + directories/metadata | No third old checkout slot exists |
| next repaired/calibrated invocation | R/repairs/<unique-attempt>, bounded new input/output and logs | at most 2,097,152 payload + 32,768 streams + 16,384 indexes | payload plus capped entries/blocks | 30,245,432 repair bytes free, **zero attempt slots** |
| independent clean delivery | reuse source-0, new output under R/recovery or outputs | no fourth checkout; bounded retained bundle/inputs below | measured before writes | Existing four 1-MiB recovery copies; a new whole clone is not one such copy |

The original two 256-MiB slots cannot fit even today's 274,469,605-byte working
source alone (6,034,149 over each slot), before Git data. Their old source forecast
was smaller; the newly committed 43,575,847-byte recovery archive is legitimate
tracked material. Two measured tree/object payloads are 894,734,752, exceeding
both old checkout slots together by 357,863,840. Full suite needs a third clone,
not an assumed second clean-release repair copy.

Clean clones contain only committed source/fixtures/evidence and their Git objects:
no recursive copy of the source directory, no .venv, no 3,499 untracked paths and no
ext4 runtime corpus. A repository-wide static search found this sole git-clone test
helper; the other copytree copies only a model fixture, charged as test artifacts.
Committed archives are not unrelated dirt and will not be omitted by sparse checkout
or source filtering. Git objects can also contain old/dangling local history because
local clone copies its object store: that explains separate object sizing; it does
not authorize deleting/repacking the original. Existing external interpreter and
installed dependencies are read in place, no environment copies or installations.
Fresh process environment is isolated and recorded; no new independent interpreter
provisioning or claim of a newly installed dependency environment is implied.

A read-only alternative-sizing check streamed `git --no-optional-locks pack-objects
--all --stdout --threads=1` into a byte counter/hash, without a retained pack or clone:
147,643,160 bytes, SHA-256
`6e4a41c83273d63c82d4e633219d79959ade5eab025c24b3e9d45fbe47f6e73f`, 65.34 seconds.
This is a static serialization measurement, not a tested --no-local clone, retained
transport, runtime qualification or independent recovery proof. It saves25,254,611
object bytes per copy relative to the loose store, before destination indexes and
other Git work. Even substituting that measured pack size in the three *settled*
clones gives2×274,469,605 +73,827,366 +3×147,643,160 =1,065,696,056; adding current
R gives1,173,055,112, already52,127,368 above the entire old aggregate, before
remaining qualification. Initial three-current-tree peak would be1,266,338,295.
Thus this measured alternative does not make reallocation-only feasible either.
It would additionally require changing and qualifying the test clone mechanism;
no compressed clone-capacity guarantee follows from this one stream. The proposed
correction preserves the existing test invocation and independently complete object
stores. Reuse the two current roots for clean delivery; no fourth clone or optional
repair checkout is proposed. A separately qualified packed-clone adaptation might
permit a smaller later budget, but is not silently assumed to avoid today's deficit.

## All sixteen historical attempt slots (unchanged)

Each row remains one consumed slot, including failed test assertions. Payload
includes inputs/output/scratch and symlink bytes (not followed). Streams are
separately charged to logs. Allocated column includes those paths' directory blocks
and stream blocks, not shared indexes/exports. Evidence roots are R/repairs/<name>,
R/logs/<log>, and the numbered R/indexes/*-record.json ranges. This exact-path
attribution does not relabel any attempt or remove its existing charge.

| Slot | Purpose | Payload bytes | Stream bytes | Allocated bytes | Retained evidence and index IDs |
|---:|---|---:|---:|---:|---|
| 1 | Decoder/accounting red | 1,718 | 3,088 | 184,320 | `diagnostic-red`; `diagnostic-red.log`; 0113–0114 |
| 2 | Decoder/accounting fixed | 1,730 | 99 | 184,320 | `diagnostic-fixed`; `diagnostic-fixed.log`; 0115–0116 |
| 3 | P4-gap production | 249,824 | 483 | 352,256 | `fixed-P4-gap`; `fixed-P4-gap.stdout`; 0117–0119 |
| 4 | P4-overlap production | 249,850 | 483 | 352,256 | `fixed-P4-overlap`; `fixed-P4-overlap.stdout`; 0120–0122 |
| 5 | P4-remote_gap production | 249,872 | 483 | 352,256 | `fixed-P4-remote_gap`; `fixed-P4-remote_gap.stdout`; 0123–0125 |
| 6 | P4-partition production | 626,546 | 288 | 753,664 | `fixed-P4-partition`; `fixed-P4-partition.stdout`; 0126–0128 |
| 7 | Revision red | 0 | 972 | 4,096 | `none`; `revision-red.log`; 0133 |
| 8 | Revision fixed | 0 | 98 | 4,096 | `none`; `revision-fixed.log`; 0138 |
| 9 | P9-context production | 249,806 | 395 | 352,256 | `owning-P9-context`; `owning-P9-context.stdout`; 0253–0255 |
| 10 | P10b-external production | 249,872 | 388 | 352,256 | `owning-P10b-external`; `owning-P10b-external.stdout`; 0256–0258 |
| 11 | P10-rational129 production | 250,394 | 473 | 352,256 | `owning-P10-rational129`; `owning-P10-rational129.stdout`; 0259–0261 |
| 12 | P10-context9 production | 260,897 | 469 | 380,928 | `owning-P10-context9`; `owning-P10-context9.stdout`; 0262–0264 |
| 13 | P10-objects129 production | 264,919 | 469 | 790,528 | `owning-P10-objects129`; `owning-P10-objects129.stdout`; 0265–0267 |
| 14 | P10-context8 production | 650,100 | 288 | 790,528 | `owning-P10-context8`; `owning-P10-context8.stdout`; 0268–0270 |
| 15 | Owning-request assertions red | 1,742 | 2,513 | 184,320 | `owning-focused-tmp`; `owning-request-focused.log`; 0272–0273 |
| 16 | Owning-request assertions fixed | 1,730 | 99 | 184,320 | `owning-fixed-tmp`; `owning-request-focused-fixed.log`; 0275–0276 |

The primary repair payload rows sum to 3,309,000 bytes, the entire current repair
category. Shared build witnesses remain in inputs; all 181,338 index bytes stay
charged once, and all 65,423,591 exported bytes stay charged in exports, including
copies of these same inputs/failures. No artificial apportionment makes those shared
bytes vanish. Revision assertions wrote no separate materialized scratch; their
972/98-byte logs and records are retained. The original core failures are original
matrix attempts, retained in outputs/logs/inputs; they are not secretly extra slots.
The prior interrupted input construction, unsuccessful comparisons, repaired pointer,
three decoder errors and late-registration evidence all remain unchanged.

## Smallest proposed finite envelope for this unchanged execution path

Reallocation alone is demonstrably insufficient: three initial current clone
payloads = **1,342,102,128**, before Git metadata, greater than the entire old
1,120,927,744 allocation. Adding current retained 107,359,056 yields a necessary
lower bound 1,449,461,184, already **328,533,440 above** the old aggregate, before
remaining matrix, regressions, file padding or logs. This is a lower bound, not a
complete budget. Do not infer an exact global optimum over unmeasured alternative
Git representations.

Propose the table's caps, with these explicit scheduling reductions and bounds:

- **Checkouts 1,296 MiB = 1,358,954,496:** exactly three 432-MiB envelopes for the
  three mandatory regression clones, including their Git metadata and peak source
  checkout. At 447,367,376 measured payload, each has 5,617,456 bytes headroom:
  at most 1 MiB source growth, 1 MiB object-store growth, 1 MiB other Git metadata,
  and 2,471,728 bytes residual framing/growth margin. These are proposed hard
  scheduling bounds, not measured future demand. Re-measure before clone creation;
  stop if any component/envelope is exceeded. No large new evidence archive is
  committed between sizing and clones; final evidence export follows execution.
- **Inputs 68 MiB:** current 18,762,363 + 28 one-MiB delivery-control sources +
  20 one-MiB resource-calibration sources = 69,094,011, leaving 2,209,157 bytes.
  Reuse exact frozen inputs where possible, without free validation-work assumptions.
  Changed final-core/rerun inputs are separately charged to repairs below.
- **Outputs 99 MiB:** current 19,646,652 + (20 replay + 28 delivery + 20 successful
  resource-boundary + 10 internal/fault) one-MiB slots = 101,435,580, leaving
  2,373,444. Refusals still retain exact streams/fault prefixes. Do not manufacture
  successful-output reservations as a substitute for actual no-success evidence.
- **Repairs 180 MiB:** 4 MiB encloses existing 3,309,000; **72 final-candidate core
  refresh slots × 2 MiB** plus **16 further contingency slots × 2 MiB**. Thus
  4+144+32=180 MiB. Each new slot permits at most one invocation/process with a
  one-MiB changed-input/scratch allowance and one-MiB output/scratch allowance;
  32-KiB streams and 16-KiB metadata are charged separately. Internal focused
  processes share this same two-MiB scratch bound. Failed/aborted attempts consume
  their slots permanently. Old count stays 16; maximum becomes **104 lifetime**,
  of which 88 are new, not reset. No automatic additional full matrix, suite or clone.
- **Regressions remain 128 MiB:** two 64-MiB non-clone envelopes, one full-repository
  run and one application-gate/affected-isolated-rerun envelope. Explicitly classify
  only the three registered clone subtrees into checkouts; all test outputs, model
  copies, scratch and faults remain regressions. This is a proposed category rule,
  not a reinterpretation of past accounting. Do not rerun clone-producing tests
  into new directories; repair requiring new clean roots stops for a new decision.
- **Recovery remains 4 MiB:** four one-MiB standalone bundle copies, complete required
  closure included. Reuse source-0/source-1 without original input-directory access.
- **Logs/indexes remain 8 MiB each:** remaining108 + refreshed72 + contingency16
  commands reserve 196×32 KiB=6,422,528 stream bytes; existing36,112 leaves1,929,968
  for suites/controls. At16KiB each, these196 consume3,211,264 metadata bytes;
  existing181,338 leaves4,996,006 for inventories/manual dossiers/controls.
- **Exports remain 128 MiB:** current65,423,591 + at most64 MiB future exports =
  132,532,455, leaving1,685,273 for this plan/final reports/framing. Retain raw R
  in place; export selected complete standalone bundles and exact recovery sources,
  index/log evidence and commitments. Do not duplicate every immutable archive.
  Every archive and extraction counts concurrently; no compression discount. If
  required selected recovery exceeds64MiB, stop, not omit evidence to fit.

Compared with old caps, reclaim **82 MiB** (30 outputs +52 inputs); add **784 MiB**
checkout capacity and **148 MiB** repairs. Net **850 MiB = 891,289,600** increase.
Proposed new logical/high-water cap: **2,012,217,344 bytes (1,919 MiB)**.
Frozen parents plus new cap: **2,088,777,444 bytes**. Separately disclosed historical
side material remains outside this defined corpus sum, unchanged; including it
would total3,163,544,474, not a whole-machine census.

This is the minimum aggregate increase for the particular finite category envelope
proposed here, not a claim that no independently justified alternative can be smaller.
It removes an unnecessary fourth checkout, makes no compression guess, reduces
unused reservations and preserves all failed evidence and standalone recovery.
Scheduling caps are not proof that every unknown future test artifact will fit.

## Physical, file-count and enforcement correction

Each current clone contains at least1,298 tree +2,633 object files =3,931;
three plus existing3,678 =15,471 before remaining test/matrix artifacts. The old
16,384 entry ceiling is therefore also inadequate for the bounded schedule.
Propose **32,768 file entries and 4,096 directories**, with actual counters and
stop-before-write. Basis: 3×4,100 clone entries + existing3,678 + at most
15,600 remaining changed-fixture/output/test entries +1,190 control/index margin;
this is a cap, not an assertion that uninspected full-suite behavior fits. Before
any phase, enumerate/reserve its actual file/dir demand; above cap means stop.
At4KiB, 32,768 file tails require less than128MiB; reserve an additional32MiB for
4,096 directory/metadata units at8KiB. **Physical reservation 2,179,989,504 bytes**
=1,919MiB logical +160MiB. This increases the old physical reservation by975,175,680. At the current allocated census, remaining
new free-space capacity required is2,059,632,640 bytes. Recompute this remaining
reservation from the fresh census, including this planning file, at execution preflight.
It is capacity for new work including already occupied R, not an extra logical
allowance or total including H/Q. Fresh available capacity was869,996,871,680 bytes;
read-only executor sees `/dev/sdc`, ext4, ro/nosuid/nodev. No write probe attempted.
Normal approved executor write probe and capacity recheck remain execution preflight.

Conservative per-clone allocated reservation:432MiB payload +4,100×4KiB file-tail
padding +400×8KiB directory allowance =473,055,232 bytes. Three=1,419,165,696;
actual rounded measured source/object files before directory/metadata are458,141,696
per initial clone. Per-clone entry bounds are subordinate to the global counters;
preflight rejects unbudgeted extra metadata. Count actual allocated blocks as well
as logical bytes; sparse/hardlinked/compressed material does not remove logical
charges. All coexisting original files, clones, historical transient current tree,
archives and recovery copies count at peak. No cleanup frees an allowance.

Before execution record the amended rules, register exact clone destination paths
under the full-suite basetemp and their category exception, and pre-reserve each
entire producer's bounded output. Test harness must enforce reservations before
Python writes and subprocess launch, with bounded logs, no hidden HOME/cache/tmp
spill and monitored aggregate/category/file/physical counters. Per-file RLIMIT_FSIZE
alone is not aggregate enforcement. Do not start a producer whose write demand or
termination bound is unknown; retain bounded interrupted prefixes as failures.
The existing test evidence-index append chain must also be checked before extending:
several retained later records share a previous hash because non-record JSON files
participated in lexicographic predecessor selection. Preserve those records; do not
claim an unbroken linear chain. A future append-only reconciliation manifest can
commit the exact ordered old files before corrected record selection; this is
harness bookkeeping, not production/replay authority or retroactive custody proof.

No existing cap changes until approval. No parent corpus writes, category borrowing,
replacement corpus, eviction, counter reset, new clone contingency or security
changes. Exceeding any bound or needing another source revision after clean-root
creation stops qualification with a precise discrepancy. Full-suite source must be
frozen after ordinary repairs and before the three-clone schedule.

## Remaining qualification and executable provenance

**4c68bfc72408f7232259cd32fb05d75eaa68ef2b — 35 original core commands:** P1-point60, P1-point40, P1-hardpoint, P2-below, P2-above, P2-reversed, P2-valid, P2-unit, P3-cross, P3-closed, P3-lower, P3-point50, P3-point70, P3-upper, P3b-third, P3b-half, P4-gap, P4-overlap, P4-remote_gap, P4-partition, P5-mismatch, P5-missing, P5-conflict, P5-unrelated, P5-unavailable, P5-positive, P6-mixed, P6-multiple, P6-excluded, P7-wouldpermit, P7-wouldexclude, P7-none, P7-newbaseline, P8-before, P8-absent.

**f7bf02a8e5b975576db538efc665b1e0d4b02422 — 37 original core commands:** P8-after, P8-unknown, P8-contradiction, P9-procedure, P9-decoder, P9-context, P9-coherent, P9-retrospective, P10-denied, P10-unknown_permission, P10-hold, P10-unknown_uncertainty, P10-confidence, P10-shared_four, P10-fifth, P10b-original, P10b-external, P10b-valid, P4-literal, P9-procedure-twin, P9-decoder-twin, P9-context-twin, P10-no-observation, P10-no-baseline, P10-rational128, P10-rational129, P10-context8, P10-context9, P10-objects128, P10-objects129, P10-hold-false, P10-original-inapplicable, P10-acquisition-unknown, P10-acquisition-inconsistent, P8-null-times, P8-unknown-times, P10b-result-pin.

Original decoder failures P4-gap/overlap/remote_gap and valid P4-partition were
subsequently checked at `807d0dc2214b1604d73098f87e2faff533ae06e1`.
The five repaired cases P9-context, P10b-external, P10-rational129, P10-context9,
P10-objects129 plus valid P10-context8 were run at eb7bd53. Final16 focused tests
ran at f66ac30. All originals remain in the committed recovery archive and raw R;
latest72-case comparisons are mixed-HEAD, not one final-head run.

Static `git diff eb7bd53 HEAD -- applications backend` is empty. Nevertheless
measurement_build.py includes the exact Git checkpoint along with executable source,
lock/dependency and interpreter/platform identities. Documentation commits change
build identity; earlier f7bf02a/4c68bfc also precede actual production fixes. No
complete final-build equivalence has been demonstrated. **Refresh all72 once at
one frozen final executable HEAD**, explicitly counted outside the original180,
to avoid unsupported path-equivalence assumptions and supply same-build bundles
for20 replay checks. This is post-repair coverage, not a rerun merely for a receipt.
Historical pure oracle derivations, byte recovery and failures remain reusable as
historical evidence. Earlier same-author expectations are not independent review.
Do not replay old-build bundles as if current merely because source diffs are empty.

After approved harness bookkeeping/enforcement corrections and ordinary repairs:
1. Freeze candidate; remeasure source/object growth and executable identity. Run72
   refreshed core evaluations, comparing exact diagnostics/streams/semantic outputs
   and actual accounting separately. Preserve every old/new attempt and binding.
2. Execute pending20 verify +20 replay +28 delivery +40 resource =108 original
   commands, with unchanged oracle except the approved P10 overlay. Calibration
   uses fresh measured core demands where sufficient; each additional calibration
   process consumes a contingency slot. No hidden count exemption.
3. Execute separately the10 internal/fault controls and24 internal guard pairs;
   prepare3 manual dossiers. Internal guards are not public proof. They use bounded
   reserved input/output/log/index capacity above; no production bypass.
4. Use at most16 additional attempts for bounded calibration or affected red/fixed
   repairs; stop on exhaustion. Candidate-changing repairs before the final72 sweep
   should be completed first. A repair after the sweep requires explicit accounting
   of affected reruns within remaining slots; no automatic second72 sweep.
5. Run the full suite once and application gates under the two64-MiB non-clone
   envelopes with the three explicitly registered clones. Keep failures/skips and
   isolated reruns distinct. Reuse source-0/source-1 for clean committed-only delivery,
   verification and independently recomputing replay, with no untracked input access.
   Run reassessment commands from those roots under the exact frozen candidate;
   external provisioned dependencies are explicit. Historical clone serves only its
   historical test, not current-build equivalence.
6. Reconcile exact180 original entries plus72 refreshes, up to16 new extra attempts,
   old16 consumed slots and separate controls/dossiers without double counting.
   Verify recovery, category/combined/physical usage and retained failed evidence.
   Final administrative report HEAD is distinct from the frozen executable HEAD.

## Single owner decision and preservation

Approve this candidate's **2,012,217,344-byte new / 2,088,777,444-byte combined /
2,179,989,504-byte physical** envelopes, exact category table, three mandatory clone
classification/reuse,32,768-file/4,096-directory ceilings and88 additional finite
attempt slots (72 designated refreshes +16 contingency; lifetime104), then resume
only the already-authorized Slice5 qualification under these stop rules. No production
input/output/work limits, semantic contracts or dependencies change. Approval is
not a capacity guarantee or final milestone acceptance.

This planning turn creates only this candidate. All historical oracle/report/package
bytes and failures remain unchanged; no clone, test, runtime corpus write, production
edit, cleanup, commit or remote operation. Initial tracked tree clean and3,499
pre-existing untracked paths preserved. C remains unresolved; manual adoption and
exposure limitations unchanged. Final Slice5/milestone acceptance stays separately gated.

END OF SLICE 5 RETENTION CORRECTION CANDIDATE — APPROVAL REQUIRED.
