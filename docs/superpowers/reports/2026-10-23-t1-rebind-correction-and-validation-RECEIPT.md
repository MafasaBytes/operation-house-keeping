# T1 rebind tool: correction and validation receipt

Date 2026-10-23. Grant: resolve two findings (owner dispositions A and B), then one bounded pytest run of three
modules. **Outcome: 108 collected, 107 passed, 1 failed, 0 errors, 0 skipped. Not a successful test result.**
The failure is in a new test written for disposition A (diagnosis in §4). No repair or retry was made.

- **Governing, unchanged before and after:** the specification `42d92411…4ff61` and the original implementation
  receipt `bce045ac…efe28`, which is preserved unchanged.
- **Approval boundary:** every authority, attestation and approval in these tests is TEST-ONLY synthetic data.
  None is an operational owner approval.

## 1. Corrections

- **A. Literal attestation text.** New `attestation_text(pointer, is_key)` exempts only the top-level string
  values at `/provenance/label` and `/provenance/basis`. It is applied in three places:
  - `check_completeness`;
  - the evidence scan in `check_producer`;
  - `scan_outputs`, which now classifies every such hit as `in_attestation_text` and adds
    `record: rendered|copied`.

  Anything else still refuses: structured references, keys, nested or other provenance fields, rule
  preconditions, the EV-ID rule, and the topology, canonical-form and attestation-shape checks.
- **B. Preflight versus partial output.**
  - `Writer.readback` now refuses `REBIND_PARTIAL` (exit 5) instead of `REBIND_INTERNAL` when a read is refused
    or the bytes differ.
  - `Writer.finish` recreates `PARTIAL` where possible if a failure happens after the marker has been unlinked
    (review finding M1).
  - Only `OSError` and `Refusal` are caught. Programming defects still reach `main`'s catch-all and give
    `REBIND_INTERNAL` (exit 7).
  - Preflight refusals create nothing. The post-write rescan stays `REBIND_INTERNAL`.
- **Tests:**
  - The parametrized unmodelled-dependency test drops the provenance-basis case and adds three cases:
    stale-structured-reference, other-provenance-field and nested-provenance.
  - New tests:
    - `test_t15_literal_historical_digest_in_provenance_prose_is_preserved`;
    - `test_preflight_refusal_creates_no_output`;
    - `test_readback_failure_after_creation_is_partial[differs|unreadable]`;
    - `test_failure_after_marker_removal_restores_the_marker`;
    - `test_unexpected_failure_after_creation_stays_internal`, which injects a `RuntimeError` into the write path
      (review finding M4).
  - The `record` field is asserted (review finding M5).

## 2. Focused review

One read-only `code-reviewer` pass found no Blocker or Major issue.
- **Fixed:** M1, M4 and M5. I re-read the changed portions myself after fixing them.
- **Recorded, not fixed:**
  - M2: §4.3 says prose hits are "reported in the packet", but they appear only in the review. This predates
    the corrections.
  - M3: the new evidence exemption in `check_producer` has no test either way.
  - L1: the exemption does not check the shape of the `provenance` object.
  - L2: disposition A also covers prose that the producer itself wrote into the evidence. **Owner to confirm
    this was intended.**
  - L3: an `os.close` error during readback would still exit 7.
  - L4: if creating the marker fails, the tool reports PARTIAL with no marker. A later stage still refuses.
- **Out of scope, recorded:**
  - Stage 3 copies earlier-stage records after checking only their hashes. A hand-edited earlier stage would give
    `REBIND_INTERNAL` rather than an input-class code.
  - The post-write rescan re-reads in-memory data, so it can never detect anything.

## 3. Identities frozen before the run

| Path | SHA-256 | Logical B | Allocated B | Lines |
|---|---|---|---|---|
| `tools/fixtures/t1_rebind.py` | `180858b016b9f6c9459425a10acdb73c06250bc01713d492646b665684172831` | 68,871 | 69,632 | 1,348 |
| `tests/tools/test_t1_rebind.py` | `b2ad744af3aa16d1de9ee086869fea81a6a986441cc1a2c23b97693e478ce92e` | 72,887 | 73,728 | 1,322 |
| `tests/t1_simulation/request_fixtures.py` (unchanged) | `d17270ca…92625` | 2,202 | | |
| `tests/t1_simulation/test_maintained_increment.py` (unchanged) | `a5227742…95889` | 13,074 | | |
| `tests/t1_simulation/test_command_integration.py` (unchanged; the maintained file the receipt names) | `a2d0543d…bdbde` | | | |

Before correction, the identities were `caf238d2…` (tool) and `941f70cd…` (test), as expected.

## 4. Test run (one invocation; the grant is spent)

- **Workspace:** `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-rebind-validation-20261023-1`
  - fresh, native ext4, symlink-free parent;
  - harness `inputs/rebind-validate.sh` `84cc7603…`;
  - expectations `inputs/rebind-expected.sha256` `6e8caa1e…`.
- **Environment:** the R1 environment `cp313-bdw001` (CPython 3.13.11, pytest 9.1.1, pluggy 1.6.0, no `.pth`
  files). Admission verified 1,266 recorded rows from the R1 `PINS.sha256` (the venv, the miniconda python and
  the stdlib). Nothing was reinstalled or repaired.
- **Command:** recorded exactly in `COMMAND.txt` (`fb135566…`):
  - environment: `env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC HOME=<ws>/home TMPDIR=<ws>/tmp
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1`;
  - supervision and limits: `timeout -s TERM -k 3 300 prlimit --as=2GiB --core=0 --fsize=8MiB -- time -v`;
  - interpreter: `cp313-bdw001/bin/python -I -B -X pycache_prefix=<ws>/pycache`;
  - pytest options: `-m pytest -c /dev/null --rootdir <repo> -o pythonpath=<repo> -p no:cacheprovider
    --basetemp <ws>/basetemp --junitxml <ws>/junit.xml -o junit_family=xunit2 -v --tb=short -ra` and the three
    paths.
  - `tests/conftest.py` was kept; it only injects skips for the CAD/PDF extras and is unused by these modules.
  - `-c /dev/null` excludes the `-q` addopts.
- **Outer backstop:** `timeout -s TERM -k 3 427` (KILL at 430 s).
- **Timings (wall clock, UTC):**
  - outer: 14:09:49.215 → 14:12:47.251, 178.0 s, outer exit 0;
  - admission: 4.1 s, rc 0;
  - pytest: 14:09:53.431 → 14:12:47.171, 173.7 s, rc 1 (`time -v`: 2:53.71, maximum RSS 120,240 kB);
  - post-checks: rc 0, under 0.1 s.
  - The `/proc/uptime` deltas differ by about 9 s from the wall-clock times on this WSL host. Unexplained.
- **Signals and survivors:** no timeout fired and no signal was sent. Survivors in the owned group: none.
- **Results:**

  | Module | Collected | Passed | Failed |
  |---|---|---|---|
  | `test_t1_rebind` | 80 | 79 | 1 |
  | `test_maintained_increment` | 13 | 13 | 0 |
  | `test_command_integration` | 15 | 15 | 0 |

  No test errored, was skipped or went unexecuted.
- **The failure:** `test_t15_literal_historical_digest_in_provenance_prose_is_preserved` stopped at its first
  assertion. Stage 1 refused `REBIND_INPUT_INVALID` with target `/source/objects/f124e640…`.
  - Read-only inspection of the retained fixture shows why. The test picked evidence item `0543e3f3…`
    (`ct.evidence-item.v1`), the only record that refers to the opaque object `f124e640…` (plain text). Its
    rehashed replacement is no longer reachable from the role records.
  - `Source._parse` therefore parses it only in its second pass. That pass does not register `ct.evidence-content`
    references as opaque, so the opaque text was parsed as JSON and refused.
  - So the test's choice of record exposed an existing tool limitation: opaque objects are detected only along
    reference chains reachable from the role records. Corrections A and B did not cause it.
  - Because the test stopped early, **disposition A remains untested at runtime for copied records, for packet
    lineage and for the stale-reference twin in that test.** The rendered-attestation case
    (`test_t15_attestation_citing…`) and the three new unmodelled-dependency cases passed. All four
    disposition B tests passed.

## 5. Preservation

- **Checked before and after, all matching:**
  - the 10 expected identities, covering the corrected and selected files, the specification, the original
    receipt, L2 `74a39d87…` and `6bca403b…`, and the reconciliation `7d8bff11…`;
  - 280 source files: `applications/bounded_decision_workflow` and `backend` (excluding caches), the test
    helpers, `tests/conftest.py` and `pyproject.toml`;
  - the source list itself;
  - the repository `__pycache__` listings: no change, and no cache beside the tool or the new test.
- **Not checked:** historical workspaces were not scanned. Their preservation is not claimed beyond the fact
  that the tests use only temporary directories.
- **Not run:** no Git command, K, checkout, commit or merge; no standalone tool run; no historical workflow.

## 6. Deviations and disclosures

- Tool edit 1 (A and the first B change) was applied with a Python text-replacement script run through the shell.
  It imported no repository code and executed nothing from the repository. Later edits used the editor.
- The harness and expectations were written to the session scratchpad and copied into the workspace `inputs/`.
- Storage aggregates are observed, not quota-enforced.

## 7. Accounting

- **Repository growth:**
  - tool: +936 logical, +0 allocated;
  - test: +7,517 logical, +8,192 allocated;
  - this receipt: new file, sizes reported in chat;
  - 1 file, 0 directories.
- **Test workspace (separate reservation):**
  - 5,185 files, 867 directories and 46 symlinks (pytest `*current` links and test links);
  - 48,729,334 logical bytes and 68,554,752 allocated bytes;
  - within the reservation of 8,192 entries, 4,096 directories, 128 MiB logical and 256 MiB allocated.
- **Not borrowed:** no held reservation.

L2 stays frozen. R1's 141 results, the three deferred cases, scoped L1 acceptance and scoped synthetic end-to-end
acceptance keep their attribution. D-P remains open.

END RECEIPT
