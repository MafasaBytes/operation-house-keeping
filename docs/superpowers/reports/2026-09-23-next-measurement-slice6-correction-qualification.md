# Slice 6 correction and qualification — acceptance withheld

The approved cross-profile correction is applied. Qualification is **not complete**: one frozen diagnostic expectation conflicts with the governing phase-3 ordering rule. No diagnostic oracle amendment has been applied, and no Slice 6 or release acceptance is recorded.

The final tested implementation is `96f71b7f987faacaf7f16c361018434e4ae21993`. Administrative evidence HEAD is `fbbc77d408e949945406fd40d623c9de43928d00`. This report is published in a subsequent documentation-only commit; its exact publication HEAD and SHA-256 are returned in the receipt. Administrative commits are not tested executable identities.

Starting checkpoints verified: Slice 5 acceptance `c914d13ea887d3f7b2951a2db493f1fec1bab353`, prior tested implementation `c06395859019bead8cb7cc6491fde3efd04f1524`, administrative HEAD `3c5a8a45b071f311dd1ab6464971759038d1f85f`, and qualification report SHA-256 `ce417f3b9ea69b9106b3e681544ba1105b6e1fdd5133d4cc24e18b3c781e3ae2`. The complete command/closure contract, packaged Slice 6 allocation, proposed correction and governing validation precedence were inspected. Original reports and package bytes remain unchanged.

**Approved correction.** Commit `51f45a31bae861268ad09f6cec312557eb0cb6d7` separately records the owner-authorized correction. Proposal SHA-256 is `edccbb50a2b50c2b8400652ea44148fcf6b275872ecf5d4d051478c35f350c61`.

| Fixture | Bytes | SHA-256 |
| --- | ---: | --- |
| Historical original | 16,460 | `24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` |
| Approved replacement | 16,382 | `170d3ced7bfec018ddc63b03687edcb3716661b7f9f824c8715a6eaa954456c9` |

Only request ID, actor label and descriptive purpose become `x`; all other parsed fields, including the foreign schema, public snapshot, bindings and unauthenticated assertion, are identical. The maintained thermal request parser accepts the replacement. The full production-counted invocation fits the unchanged 16,384-byte ceiling. It reaches the exact frozen PROFILE_MISMATCH diagnostic, exit 3, empty stdout and no publication. The valid measurement P twin completes with independently bound frozen results. Both cross-profile commands pass at the final HEAD. The original remains unchanged and separately produces invocation-byte refusal at attempted 16,385/limit 16,384; it is **not** counted as profile-rejection evidence.

[FIXTURE-DELTA.json](2026-09-23-next-measurement-slice6-correction-evidence/FIXTURE-DELTA.json) binds the single overlay to the unchanged package/manifest/recovery commitments. The harness checks the proposal, both fixture digests and the exact three-field delta. No semantic expected result, trace, diagnostic or command count was altered for this correction.

**Final matrix and regressions.** Exact commands, streams, captured inputs, independently bound expectations, actual bundles and per-field comparisons are recoverable in `matrix-final.zip` and its inventory/recovery records in the [evidence directory](2026-09-23-next-measurement-slice6-correction-evidence/EVIDENCE-MANIFEST.json).

| Final-HEAD evidence | Outcome |
| --- | --- |
| 68 measurement cases | 36 completed evaluations; 32 technical refusals |
| Verification/replay | 36 verifies and 36 independently recomputing replays |
| Cross-profile cases | 2 commands, both exact matches |
| Original approved matrix | 142 executed; 142 exit matches; **141 exact matches** |
| Matrix exit accounting | 108 exit 0; 32 exit 3; 2 exit 4; zero timeouts |
| Completed retained outputs | 72 seven-file bundles, 504 files |
| Focused plus affected legacy regression selection | **268 passed, zero skipped**, 337.50 seconds |
| Source-checkout reproduction at the same HEAD | **15 passed**, 164.17 seconds |
| Build comparison | 47 retained real build witnesses match byte-for-byte, including 14 from the source-checkout reproduction |

The 268 assertions comprise 99 measurement-profile tests, 40 existing CLI tests, 7 governed CLI tests and 122 retention/recovery tests. Full node IDs and raw logs are retained. This is the specified affected selection, not a claim of an unrelated repository-wide suite. Tests used the existing CPython 3.13.11 environment without dependency acquisition. The full matrix and regressions ran in `/tmp/nm-slice6-disposition-clean`, a clean checkout of the tested HEAD. The original source checkout separately reproduced the selected paths before administrative commits changed HEAD. Both used the same exact installed environment; this is not a second-platform qualification.

All completed results, traces and receipts match the frozen semantic expectations under the prescribed executable/invocation/observation bindings. Whole-set withholding, admission/support separation, missing/conflicting support, explicit exclusions, exact joins, ties, repeated and empty branches, multiset/cardinality semantics, permutations and standalone reconstruction/re-admission/requalification/minimax replay remain covered. Rehashed forged results are checked by recomputation; byte verification alone is not treated as replay.

Six harness controls remain separate: unsupported-exclusion B, active-path cycles (direct and indirect variants), legitimate sharing, stricter-context reuse, canonical construction and reverse directory order. B produces the deliberately invalid 1/2 scores only inside tests; production U withholds and the justified V twin ranks. Synthetic traversal adjacency is test-only, not public hash-consistent cycle admission. Manual C remains unresolved, with **zero** application commands and no chosen claim. The source-to-cell/finite-set oracle check is separately written but same-author; it is not independent reviewer evidence.

**Red/fixed repairs and qualification boundaries.** Commits `f94d554`, `2634775`, `276c8bf` and `96f71b7` repair observed allocation, I/O, stream, recovery and diagnostic-ordering defects; `5d4a42a` records additional qualification controls. Exact full hashes remain in Git and the final source witness. Retained red logs show:

- Seven initial failures: JSON node/string guards after document allocation, closure base64 allocation before its guard, ignored caller diagnostic tightening, and stdout/stderr shutdown-flush failures returning exit 120. Their fixed boundary tests pass.
- Failed-read and partial-write prefixes were unaccounted. Private observation-only I/O accounting now records attempted operations and returned bytes, including refused prefixes. Shared retention helpers preserve their existing default behavior when no observer is supplied; legacy regressions pass.
- Nomination subcheck and decoder/support precedence failures, followed by a cross-context selection failure. Both an internal order seam and a public, fully hashed multi-request red/fixed pair are retained. The latter selects SUPPORT_SUBJECT_MISMATCH at `5d4a42a` and DECODER_INVALID at `276c8bf`, following the normative code order. The corresponding final-HEAD traversal test passes; the graph source is unchanged between that repair and the final HEAD.
- Recovery allocated decoded members before the aggregate capture guard, and a surrogate wire escaped as an encoding exception. Pre-allocation recovery guards and input-error translation now pass their adverse tests. Caller and retained ceilings apply before recovery; stricter replay cannot waive them.
- A receipt check reset the caller's diagnostic budget before a failed stdout write. The red/fixed control and real final-HEAD commands now preserve tightening. Real `/dev/full` commands return bounded internal refusal (7), or the reserved diagnostic-exhaustion envelope (4) under a one-byte normal-envelope budget. The reserved envelope remains bounded by the unchanged build reserve; it is not a truncated original diagnostic. Failed stderr returns 7 without a shutdown traceback. Where publication already completed, the diagnostic honestly reports a visible bundle with durability unknown; verification succeeds without claiming stream delivery or crash durability.

The final suite exercises pre-write failure and SIGKILL before each of seven files, plus create/write/flush/file-fsync/rename/manifest-publication/directory-fsync/parent-fsync failures, input replacement, unsafe/special files, collisions, concurrent publishers and recovery. Pre-manifest failures leave incomplete evidence; concurrent publication has one winner; no overwrite, cleanup or resume is introduced. Post-manifest fsync failure is reported separately from an incomplete bundle. Actual runtime locations are ext4. DrvFS/9p refusal is exercised using explicitly nominated source-checkout paths. No XFS, Windows-native, power-loss or universal crash-durability claim is made.

Earlier runs are retained with their actual status. A focused run overlapped subsequent source edits and produced ten correct dirty-build refusals; it is not regression evidence. The `5d4a42a` matrix/regression runs were intentionally interrupted after the next diagnostic defect was found. The `276c8bf` matrix has the same remaining oracle conflict; its regression was 265 passed, one failed, one skipped. The failure assumed an ext4 checkout was DrvFS; the skip lacked BDW_UNSUPPORTED_FILE. Final tests nominate both the actual unsupported output parent and read-only file and pass without skips. No legacy replay expectation or executable-build validation was weakened.

**Actual work and resource findings.** [measurements.json](2026-09-23-next-measurement-slice6-correction-evidence/measurements.json), `resources-final.zip` and `observed-work-final.zip` distinguish deterministic input demand, actual logical work, physical I/O and profiled overhead. No numerical policy changed.

| Matrix measurement | Maximum / total |
| --- | ---: |
| Complete bundle | 260,474 bytes |
| Closure / result / trace | 191,366 / 11,783 / 29,882 bytes |
| Build / manifest / invocation | 26,165 / 973 / 609 bytes |
| Deterministic captured input | 140,419 bytes; 26 unique objects |
| Measured explicit reads, including build/artifact hashing | 47,910,315 bytes; 2,264 operations per command |
| Payload writes before manifest | 259,501 bytes; 6 operations |
| Command wall / process RSS high-water | 4.985135 seconds / 90,963,968 bytes |
| Matrix child CPU | 207.975521 user + 16.289013 system seconds |
| Full retained matrix corpus | 38,458,580 bytes |

Physical counters do not claim to count every interpreter/kernel metadata operation. Manifest counters are explicitly observed before the manifest write; complete seven-file accounting and read-only Work profiling separately include that write. CPU/RSS/wall observations include concurrent activity and are not a general capacity benchmark. Matrix commands used the 30-second watchdog and 512 MiB address-space ceiling. The final regression corpus is 60,726,193 regular-file bytes; each qualification corpus stays below 64 MiB. Historical corpora are separately preserved, not erased or counted as current capacity.

For P, actual work is 62 reference occurrences, 117 edge visits (55 scoped), 14 scoped expansions, 1,123,794 contextual scan bytes, one public reconstruction/2,679 nodes, 10 procedure conditions, 4 H checks, 8 source contributions, 8 mapped cells and 4 branches. Four-revision history produces 95 references, 315 edge visits, 56 expansions, 1,782,464 scan bytes and four reconstructions/10,716 nodes. Denial reconstructs its two required contexts but does no procedure/H/mapping/ranking work. Revision 5 refuses after 28,258 captured bytes, before E/H/S dependency reads and before reconstruction. Repeated contextual validation remains charged; redundant unscoped decoder checks are not double counted in this build.

Forty-four tighter-limit CLI probes cover the 23 guard dimensions reached by P; diagnostic-byte controls cover the remaining dimension. Forty-three nominal exit predictions match. The remaining nominal prediction assumed a fixed 973-byte manifest, but fresh physical metadata produced a valid **972-byte** manifest under cap 972. That raw discrepancy remains retained. A measured nearest adverse twin at cap **971** refuses at attempted **972**, with no manifest and an honest incomplete state. Closure and bundle-reserve twins include the override's own retained bytes rather than treating that overhead as free. This is resource calibration, not a changed semantic oracle.

Additional public controls show 128 unique objects succeeding with unchanged hand-derived scores 1/2 and a 314,345-byte complete bundle; 129 refuses without publication. Eight contexts succeed (268,150-byte bundle); nine refuse. Four complete revisions succeed; five refuse without truncation. Default ceilings can interact; these tests do not promise that every simultaneous combination of maximum dimensions can complete. Lowered-demand twins are distinguished from tests at the default 128/4/8 boundaries.

Resource probes, the five real stream/verify/oversize commands, two 128/129 commands, fault/regression commands and same-build reproduction are **additional qualification controls**, not a revision of the original 142-command matrix. The original oversized fixture accounts for exactly one separately labelled final resource-control command.

**Blocking contract discrepancy and smallest owner decision.** Frozen semantic candidate §4 says: “within a phase use code ASCII order then canonical target path,” except for incremental phase-2 traversal and §2A nomination subchecks. CONTRACTS.md preserves that precedence. In CL-historical-invalid, Q revisions 1 and 2 both reference decoder `af694b1d87bb1ccae75fe9ec7350532e044f33fe3e09868a02e6ec13dcdc7a93`. Its two open intervals omit 50. Both contexts therefore reach DECODER_INVALID. After the common `/predecessor/` prefix, `measurements` sorts before `predecessor`.

The frozen oracle nevertheless selects `/predecessor/predecessor/measurements/0/decoder`; the normative ordering selects `/predecessor/measurements/0/decoder`. The matrix records this one field mismatch and its consequent raw-stderr commitment mismatch—not two independent defects. Both code and exit remain correct. Reverting to first-request failure would contradict the ordering rule and the public multi-request control. Changing the oracle is outside the latest authorization to change only commitments dependent on the approved cross-profile substitution.

The exact, **unapplied** [amendment candidate](2026-09-23-next-measurement-slice6-correction-evidence/historical-diagnostic-amendment.json) has SHA-256 `013363cad50982537b1643a764354e062b29a23e54ff25b2bc1de2a18a459128`. It changes only `/target/field` in `expected/CL-historical-invalid/stderr.jsonl`:

- Original 507 bytes: `eaba7bd78c1addbb9b73800827c28f9a9d7a7d1e5129d5cade3a70c626f4fdaa`.
- Proposed 495 bytes: `ed2b2e22dee2ba86342ffe708c1a50faf477887f29905d797483f2280bb4c072`.

Inputs, authority/basis/decoder references, code, exit, empty stdout, numerical semantics and 142-command accounting remain unchanged. The proposed bytes match the observed normative diagnostic, but they are not substituted into the proof checker. Recommended owner decision: approve this single diagnostic-field correction and dependent commitments, preserving the original. Then complete affected exact comparison/reproduction under the authorized final binding. Slice 6 acceptance and final release obligations remain separate; no retrospective 142/142 pass is claimed here.

**Recovery and preservation.** The evidence manifest SHA-256 is `f6d425b8ca3cf3d6c351fa97289ec386963ce6997075347c95e6cf59876c6ddf`; it binds 95 evidence files, 57,985,268 bytes, excluding itself. Archives retain exact regular-file bytes and per-member hashes, and were reopened to verify recovery. Filesystem-control symlinks/special files are recorded as metadata, never followed or automatically recreated. `frozen-authority.zip` preserves the exact package, manifest and recovery receipt; all 1,191 frozen payload commitments were verified. Historical and proposed diagnostic bytes are separately retained.

Actual starting inventory: 2,513 regular files and 1,444 untracked paths. No inventoried file is missing. Only the ten explicitly listed source/test files changed; all historical documents, frozen inputs/oracles, backend contracts, dependencies, ledger and unrelated artifacts retain their starting bytes. The new test file and evidence are separately identified additions. Raw pytest logs retain their original trailing whitespace; diff-check warnings on those logs are not normalized away. Source/test whitespace checks pass. Staging was restricted to the new evidence directory and all staged bytes were checked against its manifest before commit. Git writes used ordinary product approvals; no permission, ownership, mount or security setting changed.

All runtime directories and historical results remain preserved. No successor work, backend extension, dependency acquisition, ledger/ADR allocation, push, merge or history rewrite occurred. IN-001 and CI-001 remain open and unselected. The only blocking finding for this continuation is the frozen diagnostic-oracle conflict above; Slice 6 remains unaccepted.
