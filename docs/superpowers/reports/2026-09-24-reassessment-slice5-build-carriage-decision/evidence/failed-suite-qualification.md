# Reassessment Slice 5 — consolidated qualification after the single full-regression attempt

**Qualification remains blocked.** The authorized full-regression attempt ended
with exit **1** after **934.359648433 seconds**. Retained evidence establishes
**1,839 passed, one product failure, 33 skipped and zero observed setup errors**.
A reporting-harness error then aborted the run: one additional node started but
has no retained call outcome, and **3,424 selected nodes never started**. No repair
or rerun was performed. Slice 5 acceptance and final milestone acceptance remain
separate, pending owner gates.

## Commitments, approval and source identity

Verified approved continuation SHA-256:
`3490d34cb2909f6b7e47710630cab0a0e8e312bf6bb5938714a47bb590e74d84`.
The separately retained owner approval raises only the full-suite envelope to
268,435,456 bytes, regression category to 335,544,320 bytes, directories to 24,576,
files to 65,536 and physical reservation to 1,572,864,000 bytes. The aggregate new
retained-byte ceiling remains 1,274,019,840 and the H/Q-inclusive ceiling remains
1,350,579,940. Every other category and every production policy limit is unchanged.

Tested candidate: **`40fbb7b0a5ea5251179a9661c782a41cf7356ed6`**.
Administrative HEAD before and after: **`358d2867db478494ca8b6e6475b83fdd53a9750c`**.
No checkpoint moved, no history was rewritten and no new checkout was created.
Both existing candidate checkouts remain at F and tracked/untracked clean; the
historical checkout remains at `c37c24ee50667121d6b2dc4739aa3b7d12825c96` and clean.
Main tracked status is clean, and applications/backend still match F exactly.
The earlier “administrative HEAD, restored” described returning from detached
preparations before this continuation, not a restoration performed here.

The complete repository test/input view was mounted read-only. Existing source-0
supplied its candidate Git database and original applications/backend directories;
all collected tests match F. Exactly three administrative-only qualification
drivers added at A were explicitly accounted for and were not collected tests.
The production reassessment witness independently matched SHA-256
`6cef6e1f4915e95ac4a02058e86bfe88cd8eea05cd6c7f2d027bc5780754b4b8` before collection.
All 1,191 measurement preparation members (17,819,590 bytes) were rechecked against
the committed authority archive and manifest. No unrelated loose preparation was
accepted as authority. Existing CPython 3.13.11/dependencies were used unchanged.
Only the new, charged regression root was writable inside the suite namespace;
original runtime evidence, frozen parents, source, ledger stores and unrelated
artifacts were read-only there. Existing local-loopback tests had their normal
executor access; no external acquisition or installation occurred.

## Matrix coverage and completed obligations

| Evidence class | Identities | Attribution |
| --- | ---: | --- |
| Direct candidate matrix checks | **173** | E72, V20, R20, D21, B40 at F |
| Justified historical matrix checks | **7** | Original tested heads retained with source/input-path applicability audits |
| Matrix identities with recorded direct-or-justified checks | **180** | Not 180 fresh executions and not full Slice 5 closure |

There are 174 candidate matrix attempts: 173 matched and the preserved original
manifest-fit failure. The sixteen specifically authorized D executions remained
16/16 matched and were not repeated during this continuation. All 72 current core
passes and 19/19 named retry results remain intact. The original 971-byte fixture
and failure remain separate from the approved 972-byte correction and passing
single retry. That exhausted retry was not repeated.

The seven historical identities are D-v1-header, D-unknown-flag, D-escape,
D-collision, D-wrong-build, D-prepared-build and D-wrong-policy. Their exact heads,
commands, diagnostics, input/build/policy commitments and applicable execution-path
justifications remain in the unchanged [historical D audit](2026-09-24-reassessment-slice5-historical-d-audit.json),
SHA-256 `4b654866e7ee92c5f0acb1be610f19251572488886d606c71a9bb14cbdf2e302`.
They have not been relabelled as new candidate executions or runtime measurements.

Previously completed member-race, root-race, write-fault, interrupt, fsync-fault and
ordering controls retain their outcomes. The two S7 application-gate tests, isolated
clean delivery, four recovery copies and their independent recomputations likewise
retain their prior evidence. None of those allocated checks was repeated. The full
regression's own node identities remain a separate evidence population.

## Preflight and single execution

Initial accounting exactly matched the approved receipt: 832,557,284 logical bytes,
903,241,728 physical bytes, 20,974 files and 1,879 directories. Approval was appended
before amended producers. A separate test-only accounting adapter applies the new
ceilings; the original qualification helper remains unchanged for its isolated
unit tests. The delivery harness's I/O was routed into the full-suite root rather
than the frozen Slice 4 corpus. Its original non-fsync record behavior was preserved
so publication-fault tests would not fault the accounting writer first.

The first collection preflight failed before collecting or running tests because
an ext4 Git index with file-mode checking saw 221 apparent 100644-to-100755 mode
changes in the 9p source view. Its exact stderr and unused controller versions are
retained. Binding the existing candidate's production directories corrected only
that operational view; source bytes, file modes and Git configuration were not
changed. An intervening read-only diagnostic probe also lacked its required /dev
mapping and failed opening /dev/null; that preparation result is recorded separately.
These were pre-launch preparation results, not suite retries or fresh capacity.

Corrected collection preflight exited 0: **5,300 collected, two completed S7 nodes
deselected, 5,298 selected**, with 35 predeclared optional-dependency skips. The
actual execution collection matched every selected node and skip marker exactly.
The exact two excluded nodes are the previously passed reciprocal clean-root and
accepted-S6 recovery tests in `test_s7_release.py`; their F evidence remains separate.
No other node was deselected.

The durable `full-regression-once` transaction reserved the remaining portion of
**268,435,456 bytes**, including the already charged 815,779 preflight bytes. It
registered one full-repository slot before the child launch, with expected base
outcomes of 5,263 passes/35 declared skips, zero setup errors, and zero retries.
Category, aggregate, file, directory, conservative physical allocation and available
filesystem headroom were checked before writing or launching. Serial execution,
unique basetemp below the dedicated TMPDIR, disabled cache/bytecode and unchanged
function isolation were used. No runner cleanup, evidence pruning or unsafe fixture
reuse was introduced.

## Actual results and attribution

| Actual retained disposition | Nodes |
| --- | ---: |
| Passed calls with completed teardown | **1,839** |
| Product failure with completed teardown | **1** |
| Observed skips | **33** |
| Setup errors observed | **0** |
| Teardown errors observed | **0** |
| Started, without retained call/teardown outcome | **1** |
| Never started | **3,424** |

The 33 observed skips comprise 23 PDF and 10 CAD tests because those extras are
not installed. Two additional CAD-marked nodes are among the unstarted nodes;
they are not counted as observed skips. This is an incomplete base-environment
run, not a full-suite pass or a completed optional-dependency qualification.

**Product compatibility failure:**
`tests/applications/bounded_decision_workflow/test_governed_build.py::test_actual_identity_or_explicit_dirty_refusal`.
On the clean candidate, `governed_build.identity` raised `WorkflowInputError:
OUTPUT_LIMIT_EXCEEDED` at its unchanged final **8,192-byte build_bytes ceiling**.
The complete pytest traceback is in the raw node record and results JSON. Static
wire-length derivation from the 48 committed application paths, literal envelope
fields, pinned versions and fixed-width SHA-256 fields gives **8,592 bytes**, an
excess of **400 bytes**. The derivation is retained separately; it neither invokes
the builder again nor constitutes a replacement witness or oracle. The candidate's
governed identity cannot fit its current limit. This is a product compatibility
blocker, independent of the newly approved test-retention ceilings. No production
limit, validation order, backend behavior or source was altered.

**Harness abort introduced by this continuation:**
`tests/identity_binding/test_state_anchor.py::test_minter_has_no_io_store_network_environment_or_backend_dependency`
intentionally replaces `builtins.open` and `Path.open` with a function raising
`AssertionError: forbidden side effect` while checking its minter. The added
`pytest_runtest_logreport` recorder attempted `Path.open` before fixture teardown
removed that patch. Its exception caused pytest's INTERNALERROR. Session finish
then attempted XML writing through the still-patched `builtins.open` and failed
again. This is the qualification recorder's incompatibility with the test's fault
seam, not evidence of a product minter failure. The node's setup is recorded, but
its call outcome is not; no pass is inferred. **No XML or child final-usage file
was created**, and neither was fabricated afterward. Raw stdout/stderr preserve
both error chains. The controller recorded child exit 1 and preserved the failed
run; its own bookkeeping process then returned normally. No repair, repeat launch,
selective rerun or continuation of the unstarted nodes occurred.

The complete 3,424-node unstarted list, the single incomplete identity, passed and
skipped node identities, exact collection manifests and raw phase reports are in
[full-regression results](2026-09-24-reassessment-slice5-full-regression-results.json).

## Usage, peak coexistence and remaining allocations

The full-suite tree, including preparations, streams, partial node logs, temporary
material and surviving fixtures, retains **109,121,935 bytes**, **13,492 files** and
**6,868 directories**, with **176,926,720 allocated physical bytes**. Its unused
159,313,521 bytes are not an execution allowance. The application-gate envelope
still retains **10,325,139 / 67,108,864 bytes**, unchanged.

Peak coexistence was reserved for the entire prior corpus plus the full 256-MiB
suite allowance and file/directory allocation overhead. The parent sampled the
suite every five seconds and observed the highwater above; that is not a claim to
have measured every instantaneous peak. The suite additionally checked storage
between tests with finite next-test margins. There was no timeout, stream-limit
kill or storage-budget stop. The incomplete run does not validate the earlier
forecast of a completed full-suite peak. No storage was reclaimed to make capacity.

Consolidated evidence checkpoint after results, matrix and ZIP publication, before
this Markdown and its final append-only receipt:

| Category | Retained bytes | Amended/current ceiling | Headroom |
| --- | ---: | ---: | ---: |
| outputs | 37,993,222 | 103,809,024 | 65,815,802 |
| inputs | 29,056,969 | 71,303,168 | 42,246,199 |
| repairs | 59,223,603 | 188,743,680 | 129,520,077 |
| regressions | 119,447,074 | 335,544,320 | 216,097,246 |
| checkouts | 612,016,995 | 620,756,992 | 8,739,997 |
| recovery | 1,703,784 | 4,194,304 | 2,490,520 |
| logs | 132,256 | 8,388,608 | 8,256,352 |
| indexes | 1,568,710 | 8,388,608 | 6,819,898 |
| exports | 82,909,905 | 134,217,728 | 51,307,823 |

| Other dimension | Actual at checkpoint | Ceiling |
| --- | ---: | ---: |
| Full-suite envelope | 109,121,935 | 268,435,456 |
| Application-gate envelope | 10,325,139 | 67,108,864 |
| New aggregate logical bytes | 944,052,518 | 1,274,019,840 |
| Combined H/Q plus new bytes | 1,020,612,618 | 1,350,579,940 |
| Physical allocation bytes | 1,082,728,448 | 1,572,864,000 |
| Files | 34,524 | 65,536 |
| Directories | 8,747 | 24,576 |

Full-run streams and temporary files are charged inside the regression category;
the logs category above holds the other retained command streams. This report's
publication is separately charged under exports/indexes. The final append-only
receipt binds its SHA-256 and post-publication census; the returned closing census
also includes that receipt itself. Every final category and global dimension is
checked under the amended ceilings. All producer reservations are closed.

All execution allocations are now consumed: the original matrix, core refreshes,
19 named retries, manifest-fit retry, sixteen D executions, historical/additional
repair allowances, six named controls, both regression slots, three checkouts and
four recovery-copy slots. **No retry, repair, checkout, recovery or regression
execution remains authorized.** Unused byte headroom creates no new allocation.

## Evidence and residual owner gates

The verified evidence ZIP has **65 members** and a complete **20,360-entry**
file/directory/special-file inventory binding the retained suite tree. It preserves
raw streams, phase reports, all runner versions, approval, ledger records, exact
candidate source for the failures and the static size derivation. Live fixture
bytes remain untouched in the runtime corpus; the archive inventories them rather
than duplicating the entire tree. Original failures, all historical commitments,
72 core passes, 19 retries, sixteen D outcomes and unrelated artifacts remain intact.

- [2026-09-24-reassessment-slice5-full-regression-owner-approval.json](2026-09-24-reassessment-slice5-full-regression-owner-approval.json): `3c9aaa5e03c1a52a6488319cd0f6f67806ee943a2a3738e6203b1e11860bf3de`.
- [2026-09-24-reassessment-slice5-full-regression-results.json](2026-09-24-reassessment-slice5-full-regression-results.json): `c342ba63b6e71fc500f5e0d1e0b668fc3933fd621c52547125751e40d2ff92a6`.
- [2026-09-24-reassessment-slice5-final-qualification-matrix.json](2026-09-24-reassessment-slice5-final-qualification-matrix.json): `bb5350bddfe735ef81475cb953da9c07d44deba541ae51785352df33157aab66`.
- [2026-09-24-reassessment-slice5-full-regression-evidence.zip](2026-09-24-reassessment-slice5-full-regression-evidence.zip): `ce7a710bd6de4a5a06eb0c24d49a7ace74b2fbbd7320032d55772dade2bd3d7e`.

Residual blockers are the governed-build compatibility defect, the uncorrected
reporting-harness incompatibility, and the incomplete regression evidence (one
failed, one indeterminate and 3,424 unstarted node dispositions). Any repair and
further execution require separate authorization; none is presumed. Optional CAD/PDF
execution remains outside the existing dependency qualification. No successor work,
production change, cleanup, dependency change, push, merge or history rewrite was
performed. Slice 5 acceptance and final milestone acceptance remain pending.
