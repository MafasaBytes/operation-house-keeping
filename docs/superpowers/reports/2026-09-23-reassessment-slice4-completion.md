# Reassessment Slice 4 completion

**Slice 4 — Maintained commands, retention and semantic replay** is implemented.
Owner acceptance remains pending. Production implementation/tested HEAD:
`57e2142464019ac1f1aa823d41832048c1d8e656`. Administrative completion HEAD is the
commit containing this report, identified separately in the delivery receipt.
The later accounting-harness-only checkpoint is `98f4a66dbd53399ea5b2c7721f839ec46bf005a1`; application and
backend sources are identical to the tested implementation. No later slice or
full 180-command proof is claimed.

## Authority and implementation checkpoints

Slice 3 acceptance remains `fd37f93a4f5d35d7a4030ff62bfb56117f68a9f6`, at tested
implementation `433077d717719921d89fe5f882c83bf93f55c18e`. Its frozen report remains
SHA-256 `b86af00be5bcb13e60ff6eca823d3ff258d7d18b829b7267f166e828d106bce0`.
Starting administrative HEAD was `8f0c6ea92d973cc77acc4d4cded9dc86eb826581`.

The complete [retention plan](2026-09-23-reassessment-slice4-retention-plan.md)
was verified at `ff24c608ddf2b3bc5278b29d56743f8af033284db4afa190ab4a7862c0035071`.
Approval was separately committed in `bf201961d00b7181c0d4ebca7c1feec7f6b042af`.
The named ext4 corpus was created exclusively after verifying H and free space.
No directory-based reset, production policy edit or historical mutation occurred.

Implementation commits: `ea77f30` (commands, retention, independent replay),
`ebd0d9b` (real delivery/adverse twins), `57e2142` (two red-tested boundary fixes).
The approved package, CONTRACTS.md, plan and resource semantics remain unchanged.
The old policy is preserved; only the explicit qualification-retention amendment
is in force. Physical reservation is not an additional logical allowance.

## Delivered behavior and scope-to-evidence map

The maintained entrypoint supports exactly:

```text
python -m applications.bounded_decision_workflow reassessment-evaluate --invocation FILE --objects-dir DIR --authority-pin SHA --output-dir NEWDIR [--limits FILE]
python -m applications.bounded_decision_workflow reassessment-verify --bundle DIR
python -m applications.bounded_decision_workflow reassessment-replay --bundle DIR --output-dir NEWDIR [--limits FILE]
```

Unknown, repeated and abbreviated flags refuse. There is no caller result, build
assertion, bypass, callback, synthetic witness, adoption or rerank option. Evaluation
uses owning Slice 1 capture, Slice 2 public admission and Slice 3 full-envelope
computation. Retention uses captured bytes, exact seven-file closure and real
executable/policy binding. It reserves output plus the complete manifest allowance
before directory creation, writes manifest last and retains honest failure states.
Safe I/O reuses the maintained no-follow descriptor-relative primitives; nr requires
ext4, checks directory identity, regular files and before/open/after metadata.
Legacy filesystem and command policies were not changed.

Verification checks stored integrity, required closure, actual build/policy, public
admission and joins. It reports stored disposition; it does not establish the truth
of that disposition by recomputation. Replay decodes only retained members, rejects
missing/extra/duplicate or substituted material, reconstructs E0/E1, repeats baseline,
permission, uncertainty and support qualification, and independently computes the
result and trace before comparing them with stored bytes. The original inputs are
not a fallback. Canonical evaluation counters are reproduced for semantic equality;
additional transport/recovery work is charged to aggregate guards and separately
measured. Tightened replay limits cannot rewrite retained closure semantics.

| Obligation | Concrete evidence |
| --- | --- |
| Real complete delivery | P8-before: actual executable-bound input, admitted observation, model-relative one-compatible result; actual module command, seven files and exact streams |
| Standalone replay | Original input path renamed to a retained path; subprocess runs from isolated recovery location with only bundle/output arguments. All six semantic files equal evaluation bytes; physical manifest is fresh |
| Independent computation | Rehashed forged summary passes byte-integrity verification but replay refuses `REPLAY_SEMANTIC_MISMATCH`, with no output directory |
| Whole-set withholding | P10-denied returns exit 0/evaluation_denied, both H retained, null cells, zero qualified cells and derived_not_adopted |
| Exact authority/closure/build/policy/profile | Five correctly rehashed retained-envelope adverse copies refuse at their owning boundary; admitted bundle is the valid twin |
| Real build rather than prepared witness | Actual source/dependency producer used throughout; prepared witness receives NONEXECUTABLE_BUILD_WITNESS through the CLI |
| Paths and publication | Symlink/traversal refusal, no-overwrite collision with unchanged existing bytes; write/file-fsync/directory-fsync injected failures use real filesystem writes and preserve incomplete or complete-visible-durability-unknown states |
| Logical/work/output bounds | Complete recovery counters, stricter closure-limit refusal before publication, actual largest required case, immutable original uncertainty/support/ancestry semantics |
| Compatibility | Fresh legacy usage dispatch checks; 487 affected reassessment, selector, thermal and governed reasoning/admission/review regressions |

Publication-fault injection is test-only monkeypatching, not a production option
or evidence of actual power loss/process kill. The relative-parent and malformed
output-shape checks are internal boundary tests, separately identified from CLI
admission. No internal seam is claimed as end-to-end adversarial admission.

## Verification and ordinary repairs

`initial-red.log` records the absent delivery module. The first real path passed
at `ea77f30`. The expanded **14 tests passed** at `ebd0d9b` (48.83 seconds), including
substitutions and filesystem faults. Two additional tests then failed:
`_output` raised AttributeError for a list instead of an input refusal; `_stable`
rejected its internal current-directory parent for a valid single-component path.
The fixes add the explicit dictionary guard and support that internal parent only;
public traversal/dot-path rejection remains intact. `boundary-red.log` is preserved.

At exact implementation `57e2142464019ac1f1aa823d41832048c1d8e656`:

- **11 delivery checks passed**, 8 deliberately deselected, 71.58 seconds. Fresh
  real command/replay, forgery, withholding, prepared-build refusal, both fixed
  boundaries, stricter limits, largest case and legacy usage were covered.
- **487 regressions passed**, 29 deliberately deselected, 258.35 seconds. Selection
  spans Slices 1–3, selector contracts/admission/qualification/ranking, thermal
  decision review and governed admission/review. The omitted earlier production
  fixture tests would duplicate retained inputs; they are not counted as fresh.
- **498 fresh passes**, zero product failures or skips in these completed runs.

The eight earlier substitution/fault checks are reused evidence at `ebd0d9b`, not
fresh final-HEAD passes. Both production fixes affect only list-valued envelopes
or the internal `.` parent; those earlier cases use dictionaries and absolute paths.
The complete earlier run remains retained. This is not a full repository suite,
full legacy delivery rerun or the full proof matrix; those release/qualification
gates remain Slice 5. Existing positive legacy delivery evidence stays historical.

An initial regression launch was interrupted to explicitly route its one empty
pytest tmp_path fixture into Q. Its retained zero-byte log is an incomplete prefix,
not passing evidence; cancellation exit 130 is separately recorded. The corrected
launch used Q/inputs/regressions-final and completed. No old pytest basetemp was
reused. Runtime aggregate pytest durations are not per-command wall measurements.

The accounting harness was subsequently corrected to include a directory-symlink's
170 bytes and registered exports outside Q. The link was already covered by the
16 KiB fixture reservation; no cap was exceeded. An independent filesystem census
matched the corrected counters. This test-harness-only change does not change the
executable or the earlier semantic results; its checkpoint is separate above.

## Actual measurements and retention

Actual final build: **27,632 bytes**, SHA-256
`237daca7b894343ed4f2ae3e46ad791053b218e464ac020f325b4aa05f5a5a78`.
Build producer measured 47,751,035 bytes read, 2,215 read operations and
47,861,663 hash-input bytes. The 65,536-byte component ceiling is independent of
aggregate fit; no future build size is frozen by this observation.

P7-newbaseline, actually captured/admitted/qualified/computed: closure **479,864**,
captured raw bytes **354,668**, result **7,333**, trace **6,589**; complete output
plus manifest-ceiling reservation **539,253 / 1,048,576 bytes**. This probe did not
publish another bundle. It recorded 45 objects, four contexts, two revisions,
786 edge visits, 258 reference occurrences, 4,144,089 context-scan bytes, four
public reconstructions and three qualified cells. Wider history/resource boundary
qualification remains assigned to Slice 5; accepted four/five-revision internal
checks were included among the fresh regressions.

Final real bundles: admitted **421,258 bytes**, replay **421,258**, withholding
**375,902**, rehashed-forgery control **421,269**. Original historical seven-file
material recovers as **232,849 bytes**; sharing never removes its reconstruction
work. Replay transport observed 375,920 encoded input bytes, 281,921 decoded bytes
and aggregate reference/edge charges beyond canonical evaluation counts.

Admitted command manifest: 48,032,956 physical input/build bytes, 2,308 read calls,
420,286 pre-manifest bytes written in six data-file writes, 2,238,077,929 ns,
100,622,336-byte process peak RSS. Replay: 48,172,293 bytes read, 2,278 read calls,
420,286 pre-manifest written bytes, 2,087,587,066 ns, same measured RSS. Withholding:
1,916,611,189 ns and 105,390,080-byte RSS. These are the specified observed-before-
manifest-write fields, not invented final fsync totals. Complete retained size
includes the manifest. OS-internal metadata/provisioning overhead is not represented
as a universal physical-I/O measurement. No alternate-platform/durability guarantee.

Final all-copy category accounting (including this report and registration):

| Category | Actual bytes | Cap |
| --- | ---: | ---: |
| outputs | 5,390,946 | 14,680,064 |
| repairs | 1,639,687 | 4,194,304 |
| inputs | 1,984,223 | 6,291,456 |
| logs | 4,414 | 1,048,576 |
| recovery | 0 | 2,097,152 |
| indexes | 268,009 | 1,048,576 |
| exports | 1,838,833 | 4,194,304 |

Total new logical retention: **11,126,112 / 33,554,432 bytes**.
Combined H + new: **76,560,100 / 98,988,420 bytes**.
No separate temporary allowance exists. The export is ZIP_STORED, with no assumed
compression saving, and there is only one archive copy. Recovery was checked by
reading and comparing every archived member; no extraction copy was created.
The physical reservation remains 54,525,952 bytes, not extra evidence capacity.
Allocated bytes immediately before this report were 14,942,208; final observed
allocation is recorded by the final corpus census/receipt. Counts and free-space
checks remained below the approved file/directory/physical ceilings.

## Recovery, preservation and remaining gate

[Evidence archive](2026-09-23-reassessment-slice4-evidence.zip): **1,825,025 bytes**,
SHA-256 `c078f207b122e520119baffd1594daf09c08e0a87a6697b9a212a651e75804dd`.
All 725 members recovered exactly. It contains three complete standalone bundles,
the independent replay manifest (semantic members equal the admitted bundle), raw
red/fixed/final/interrupted logs, indexed argv/streams/HEADs, actual work records,
source patch and a complete pre-export Q inventory. Unexported prior attempts and
input variants remain in Q at their exact indexed paths; the archive does not
claim to contain every Q byte. Complete core delivery recovery does not require
the original input directory or loose preparation files. The committed package,
exact code checkout, external provisioned CPython 3.13/dependencies and supported
Linux filesystem remain explicit prerequisites. Same-build replay requires the
tested checkout; administrative HEADs are not substituted for its build witness.

H remains **65,433,988 bytes**, with its exact combined tree commitment
`0ae693f44e5ca9edf0ab94e9958a436ab32e74a12d43c09703c171c89d62dd14` reverified.
No historical file was deleted, moved, recompressed, chmodded or overwritten.
All 3,499 original untracked paths remain. Against the preserved 4,773-file earlier
inventory, only the authorized application cli.py changed; other pre-existing
bytes remain identical. The approved plan, reports, packages, oracle histories,
dependencies, provisioning, backend contracts and project ledger remain unchanged.
Only authorized implementation/tests and documentation/evidence were staged.
No dependency acquisition, physical acquisition, ADR, push/merge or history rewrite.

No known Slice 4 production defect remains. Full runtime qualification, exact
180-command proof, complete repository/legacy delivery and clean-release gates
remain Slice 5, not silently claimed here. Conclusions remain model-relative,
manual and not adopted; no pruning or reranking occurs. Exposure is declared,
not authenticated custody; same-author oracle provenance and the unresolved review-
digest discrepancy remain disclosed. C remains unresolved; IN-001/CI-001 remain
open and unselected.

Owner gate: accept Slice 4; subsequent slices and full proof remain unauthorized.

END OF REASSESSMENT SLICE 4 COMPLETION REPORT.
