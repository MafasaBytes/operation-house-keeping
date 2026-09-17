# Maintained admissibility — final release verification

2026-09-17. Bounded release verification and delivery reconciliation only.
**Final owner acceptance remains pending.** No capability, operational limit,
dependency, backend contract, ledger or ADR was changed.

## Authority and exact candidates

Verified starting HEAD/main `6204c74b088c812f50db7db9d87e0c6eb6d1328f`,
Slice 2 acceptance `5e7278e85dc23acf59b88435598e03a717f32a69`, and Slice 3
completion SHA-256 `e3261e6867573812c7aff081dcf85c180ef8d60fe310ea1048ba1d8947ca7333`.
Read the complete consolidated contract/plan, corrected allocation and completion
report. Verified its final-head 163-test/60-command records and recovered all
467 archived files, 198 byte objects, 34 payload inventories and 13 closure recipes.
The earlier 765-pass/one-skip regression was explicitly not final-head evidence.

[Slice 3 acceptance](2026-09-17-admissibility-slice3-owner-acceptance.md) is separately
committed at `8ca8b2e91cb24dd6c426e3e321a865c4a81f9dc2`; record SHA-256
`04939139095fff30fc3c56dc6bedbce89f06d28ad42702b54c4908a7ba5a33e3`.
No tests were repeated merely to record that acceptance; the new owner instruction
separately authorizes the release runs below. Completion-report bytes are unchanged.

Exact final tested candidate: **`15f773ba9c675b553283669fbf72c76407c0eabd`**.
Its only change after acceptance is the application README's delivery reconciliation.
All executable implementation/test bytes remain those accepted in Slice 3.
The administrative commit adding this report/evidence is identified by
`git log -1 --format=%H --` this report and the final receipt, not a self-reference.
It is not relabeled as a tested build: even documentation commits change the exact
Git identity required for governed replay.

The consolidated plan plus [allocation correction](../plans/2026-09-16-governed-slice-allocation-correction.md)
defines three functional slices. All are owner accepted; there is no remaining
functional slice to implement under this instruction. Historical status/gate text
in frozen design and preparation remains untouched. This report reconciles current
delivery status, not historical bytes or authorizations.

## Fresh verification

The complete repository invocation collected **4,845 tests**: **4,807 passed,
35 skipped, three failed**, exit 1, in 1,652.07 seconds. The three failures were
the FL-001 reproduction fixture's system-temporary-root requirement: the initial
`--basetemp` was private ext4 storage but not beneath `tempfile.gettempdir()`.
The safety guard correctly refused before reproduction; the nonempty-root test
also encountered that earlier diagnostic. No backend or fixture guard was changed.

A permitted isolated rerun of the entire 12-test FL-001 reproduction module at
the **same candidate and interpreter**, under a new `/tmp` ext4 directory, passed
all 12 in 139.34 seconds. Both JUnit files and the original exit-1 evidence are
retained. This is not a claim of one green full-suite invocation. Across those
executions all **4,810 non-skipped cases have passing evidence**. No product
repair or source change was needed; nine already-passing module tests were
repeated to retain coherent module-level regression evidence.

The full run passed all **771 application tests with zero skips**, including
S7; the 66 decimal-parser, five state-classification architecture and three
semantic-isolation tests also passed. Together with the isolated 12-test FL-001
module, all 857 required application/affected-regression cases have passing
evidence. The 35 remaining skips are exactly 23 PDF and 12 CAD optional-extra
tests; no extra was installed and no all-extras qualification is claimed.

All runs use new exclusive paths beneath
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/s7-release-Gvdefi`.
The source is a clean local clone at the tested candidate. A fresh CPython 3.13.11
venv was populated offline with the ten already-retained hash-locked wheels, using
the existing pip 25.3 installer and `--no-index --no-cache-dir --no-deps
--only-binary=:all: --require-hashes`. No network acquisition or existing environment
modification occurred. Bytecode, user site and pytest cache were disabled. The
interpreter, dependency versions, exact commands and JUnit are retained in the
[release evidence](2026-09-17-admissibility-final-release-evidence.json).
Evidence SHA-256: `0ecd090f37787849bc7eefc1d0576058e5b37fa67c0e3c4d2335ddb2054f4983`.

The previous broader-regression skip was an unnominated unsupported-output-parent
probe, not an application defect. This run supplies an isolated empty parent on
verified 9p plus the read-only unsupported-input fixture; both rejection probes
run. Production accepts no filesystem override. All runtime inputs/results use
verified ext4. An escalated isolated invocation permits the local socket fixture;
the older release's sandbox socket error is not attributed to this fresh run.

The fresh **60-command** governed harness passes every expected outcome at the
tested candidate: 47 exit 0, one 2, seven 3, one 4, three 5 and one deliberate
interruption 91. Its 12 primary evaluations contain 276 slots, 234 performed
assessments, 42 blocked slots, 89 required reviews, 25 typed-value changes and nine
comparable numeric pairs. Five ancestor reconstructions add 115 slots, not primary
cases. Duplicate observation/lifecycle/replay runs produce 29 new governed bundles
(667 current slots) and two legacy bundles (22 rows each); these are not independent
world-domain cases. No-prior change flags remain null, not asserted unchanged.

W0/J1 admit and select aH. D1-X denies before current numerical projection. Revised
D2-X admits and yields no feasible supplied action, with complete W0/D1-X/D2-X
history and 8+0+8 corners. All four nominations in the four-pair table, unavailable
observation, unknown applicability and working adoption complete as specified.
Numerical non-comparability never means an unchanged comparable number.

Real subprocess observers record zero numerical entries for denial and authority
refusal. D2 records only W0 and D2-X numerical policy entries. Rehashed false
recommendation bytes pass byte verification but fail recomputing replay. Concurrent
publication yields one success/one collision; interruption before manifest rename
leaves inspectable incomplete evidence, no receipt and no overwrite on retry.

## Complete obligation mapping

All named tests below are in `tests/applications/bounded_decision_workflow/` and
were executed at the final candidate. A/B/C/R/P/L denote respectively
`test_governed_admission.py`, `test_governed_build.py`, `test_governed_closure.py`,
`test_governed_review.py`, `test_governed_persistence.py`, `test_governed_cli.py`.
CMD denotes the fresh committed `measure_governed_commands.py` harness. Unit tests
using explicit synthetic build providers are not executable-build witnesses;
B's actual-identity test and CMD use the real builder.

| Approved obligation / historical cases | Executable evidence and boundary |
| --- | --- |
| W0, J1, X-denied, X-denied-no-prior | A gate twins; R outcomes and complete three-world comparison; P replay; CMD w0/j1/d1-x/j1-review. R standalone X supplies the no-prior obligation, CMD d1-x the prior-bound one. |
| D2-W0, D2-X and full intended revision comparison | A gate twins; R complete comparison; P full comparison/replay; CMD d2-x semantic completion, not historical old-policy refusal. |
| time-alias, presentation-alias; changed world cannot collide | A determinism/presentation and gate twins; R valid-scope twins; X denial and J1 distinct world key. Equal membership still requires renewed authority. |
| applicability-unknown/false, beta-missing, fixed-policy-changed, issuer-context-changed | A gate twins; R outcomes/no-dispatch; L command composition; CMD unknown. Unknown versus false reasons remain distinct. |
| working-adopted, missing/stale adoption, adoption-on-hypothetical | A gate/refusal twins; R exact refusals/no-dispatch; CMD working. No authenticated identity claim. |
| missing-authority, stale-external-pin/declaration, role-misuse, revision-gap | A refusal twins/omitted pin; R exact refusals/carried hostile twins; L wrong-pin; CMD missing/wrong-pin. |
| fraction-alias-rejected, beta-key-omitted, time-unknown-offset, changed-cutoff-public-mismatch, snapshot-commitment-mismatch | A exact refusal twins; R public-integrity precedence. These are technical refusals, not denials. |
| four-pair-cap-valid; duplicate/empty/five pairs; non-singleton-box | A gate/refusal twins; R four valid-scope twins; CMD four-0..3. Four is functional scope, not simultaneous-maxima capacity. |
| wrong-build; code/dependency/policy/edition integrity | B actual identity and mismatch/oversize twins; A no fallback; P mismatch-before-dispatch; CMD historical byte verification plus replay refusal. |
| sharing-diamond, active-path direct/indirect cycles, invalid role/context, deterministic order | A sharing/scopes, gate/refusal twins, determinism and numeric array order; R valid-scope twins. Cycle probes use the trusted traversal seam, not fictitious hash-fixed-point fixtures. |
| repeated-reference-boundary/over | A hash-valid 128/129 twins, counter and zero-copy guards; R 128, 129 and supplied-root occurrence checks. Frozen 64/65 inputs are not boundary evidence. |
| Complete carried authority/adoption/declaration/build/policy closure | C seven required files, recipes, tamper/build and capture-before-decode; R carried output/pin/work/recipe/edition attacks; P full comparison; CMD complete retained three-world closure. No validation-flag shortcut. |
| 23 ordered slots, 21 blocked descendants, current-condition independence | R outcomes/result-trace shape and review tests; C closed row predicates; L receipt agreement; CMD actual rows/counts. No fabricated numerical execution for blocked slots. |
| All numerical availability transitions; changed reasons | R numeric truth parameters, changed-unavailability reason and available/unavailable review. Comparable numeric change is null for every unavailable/blocked side. |
| Scoped lower/application budgets, before-work refusal | A lower guard, cap tightening, no raising/no favorable refund; R 11847/11846 boundary, 12288/12289 extra-charge guard via A, changed-path preflight; C capture guard; CMD oversized-wire control. Synthetic counters are labeled, not natural boundary worlds. |
| Stable counters versus actual work/instrumentation | A physical evidence/observer/serialization tests; R required floor and observer failure; P cache evidence and bad physical reports; CMD fresh physical summaries and bounded denied/refused observations. |
| Output/retention caps and bounded refusal | P caller-tightened output, missing reservation and fault twins; legacy S5/S6 output/terminal tests; CMD actual seven-file totals and bounded stdout/stderr. Late publication failures are not zero-work claims. |
| Path/capture/publication/recovery/concurrency/interruption | P hostile path/inventory/fsync twins; L object-inventory race; legacy S5; CMD collision/concurrency/abrupt-exit/race controls. No power-loss guarantee. |
| replay-D1-X-after-D2, replay-D1-W0-after-D2 | P historical denial/recompute; CMD both after-D2 replays plus all primary replays. Captured authority is not current adoption. |
| Exact historical checkout/environment recovery | Six separate verify/replay commands for recovered W0/D1-X/D2-X at original `250da5e...`; same semantic bytes, fresh physical reports. S7 additionally recovers accepted legacy S6 under its original checkout. |
| No bypass and legacy interpretation | L explicit routing/usage/no fallback; A version refusal; R/P all-path guards; CMD current/hypothetical/working/comparison/replay and legacy commands; full S1–S7 regressions. Legacy 22-row invocation is not governed enforcement. |
| Clean build, deterministic reconstruction and preservation | S7 two independent clones, seeds 1/7/313, 12 normal/reversed constructions, cross-root verify/replay and missing-source/refusal/restoration; committed authority recovery and this report's preservation checks. |

This maps all 36 historical evaluation obligations, both historical replay
obligations, all nine amended witnesses, six numeric truth witnesses and five
abstract graph obligations. Overlapping cases are not added into a fictitious
command total. Original preparation output bytes are not presented as v2 runtime
outputs. Earlier red/fixed development evidence remains in the accepted reports;
no application defect or repair was needed for this release candidate.

## Measurements, recovery and reproduction

The actual governed build is 6,224 bytes, SHA-256
`1ea7cb56c172687c174a210ca3403c0b970b4d3b4ccfe46963cc00fc74098c50`.
Startup separately measures 210 source read/hash operations / 2,241,494 bytes and
seven contract reads / 160,643 bytes. These are not free lower-reconstruction units.

| Fresh observed maximum | Actual | Unchanged ceiling |
| --- | ---: | ---: |
| Complete primary seven-file bundle | 355022 | 393216 |
| Lower charges / references / resolved bytes | 11847 / 2073 / 304321 | 12288 / 2304 / 393216 |
| Charged context nodes / bytes | 126178 / 3646827 | 131072 / 4194304 |
| Prior capture / reconstruction bytes | 304273 / 908056 | 393216 / 1048576 |
| Capture bytes | 659295 | 786432 |
| Edge visits / scope expansions | 80 / 27 | 128 / 64 |

R/trace replay equality includes deterministic accounting; each fresh physical
report is checked independently, including `charged=logical+extra`, `actual<=charged`
and positive scope excess. All 32 recovered governed physical reports satisfy
that arithmetic, including deliberately hostile byte fixtures whose arithmetic
does not establish semantic truth. The D2 test observer retains 879 events,
maximum 261 bytes, under its 4096-event/512-byte test-sink bounds. Ordinary bundles
have no eighth instrumentation file. Publication reservation is not a claim of
its own future fsync success. Backend limits remain unchanged.

Maximum timed serial command: 2.23 seconds; cumulative harness children:
67.84 user / 4.61 system seconds, maximum RSS 106080 KiB. These are observations,
not per-command worst-case capacity or throughput guarantees; concurrent and
interrupted commands are not falsely assigned serial timing fields.

The final command archive recovers **467 files / 198 distinct byte objects**;
raw SHA-256 `cb6e378b5328ce47fb15222f2bed1e2e9073e3eee532384ae907e8c332b2245e`.
All objects, file references, 34 payload inventories and 13 closure recipes verify.
The release evidence retains lossless XZ chunks, exact commands, JUnit, S7 records,
historical replay records/output and recovery tooling. Decode ordered chunks,
verify compressed/raw sizes and SHA-256, decompress, then verify each content
object and path mapping. Archived commands are evidence, not automatic execution
instructions. Deliberately invalid fixtures remain invalid after exact recovery.

The fresh clone also verifies the existing 105-file/36-part authority recovery,
including committed-parent historical source and embedded preparation dependencies.
The unchanged command harness's historical-source location was supplied from the
committed Slice 3 W0 archive in this new workspace, not an unrelated runtime path.
The historical replay checkout is separately `250da5e...`; its successful six
commands are historical compatibility evidence, not final-candidate executions.
The new candidate byte-verifies old bundles and refuses their mismatching build
for replay; no migration or policy reinterpretation occurs.

## Preservation, delivered boundary and owner gate

The pre-edit inventory covers 1,195 repository files (taken after the separate
acceptance commit). Only the authorized README differs among those files;
all frozen reports, authority/preparation bytes, implementation/tests, backend,
dependency files and ledger remain unchanged. All 242 unrelated untracked paths
and their byte commitments are preserved. Final tracked/index state is clean;
the exact `git status --short --untracked-files=all` equals the retained
[first-slice status receipt](2026-09-16-admissibility-first-slice-git-status.txt).

All 1,151 inventoried non-cache regular files in existing runtime inputs, results,
provisioning, dependency artifacts and the existing environment are unchanged.
New verification outputs are isolated under the new release root and the new
`/tmp/admissibility-release-fl001-dG9Uqw` root; no earlier test workspace/result
was repurposed. Only our empty unsupported-output probe directory was removed.
The fresh source and historical clones remain clean. No dependency acquisition,
backend extension, ADR, ledger mutation, remote operation, push, merge or history
rewrite occurred.

The final administration commit contains only this report and its recoverable
evidence JSON, following explicit staged-path, whitespace, link, marker, digest
and archive inspection. It does not restage preparation or unrelated artifacts.

The governed route is explicitly `governed-evaluate`/`governed-verify`/
`governed-replay`; legacy commands do not enforce declarations. Completed gate
exit 0 is not permission: mandatory false permission prevents current projection.
Local exact pins and attestations do not authenticate an identity or establish
physical truth. Immutable revisions and explicit working adoption preserve prior
evidence; replay means captured authority, not current adoption. Finite-world
membership is not general joint-support reasoning or continuous robustness.

Observed support remains CPython 3.13.11 on ext4. XFS, other platforms, reboot and
power-loss durability are unverified; manifest-last publication is not atomic
whole-directory visibility. Optional extras are not qualified by skipped tests.
No assumption discovery, conflicting-evidence adjudication, causal inference,
automatic environment restoration or physical acquisition/actuation is delivered.
Same-author oracle and shared synthetic premises remain disclosed. C remains
unresolved/dossier-only; F historical/analytical; IN-001 and CI-001 open/unselected.

No unresolved in-scope product failure or new design/resource contradiction is
known after these checks. The release-verification gate is complete within the
stated platform and coverage limitations; it is not final owner acceptance.
**Separate owner gate: grant or withhold final maintained-admissibility acceptance.**

END OF MAINTAINED ADMISSIBILITY FINAL RELEASE VERIFICATION
