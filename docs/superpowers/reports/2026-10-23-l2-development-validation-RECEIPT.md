# L2 development validation receipt: personal-path correction and one test run

Date 2026-10-23. Grant: correct the L2 personal-path check, then make one bounded development test
run over seven L2, L1 and rebinding modules.

**Outcome: NOT a successful development checkpoint.**
- **Counts:** 291 collected, 255 passed, 36 failed, 0 errors, 0 skipped.
- **Causes:** the failures come from three source defects, two of them in L2 code, all reported
  here without repair.
- **Compliance:** execution and preservation checks all passed. The attempt is spent; there was no
  retry.

- **Preserved unchanged:** the L2 implementation receipt `a99bbe92…`, both earlier rebind receipts
  (`bce045ac…`, `db6dbf8b…`), Codex's receipt `6e386e7a…`, both L2 documents, the reconciliation
  and the rebind specification.

## 1. Correction (before the run)

**Pins:** the pinned identities matched before editing (builder `e442d7b8…`, tests `00e8f704…`,
runbook `03aeb44d…`).

**Changes:**
- **Builder:**
  - configure now adds `--disable-test-modules`;
  - the dynamic ELF objects are selected by content through `release_manifest.py elf-objects`;
  - `ldd` and `readelf -d` evidence is written as `== FILE` blocks, and a failing tool refuses
    with `DEPENDENCY_EVIDENCE_FAILED`;
  - the blanket `grep -rlF /home/ /mnt/` refusal is replaced by
    `release_manifest.py portability` → `PORTABILITY_CHECK_FAILED`.
- **`release_manifest.py` `portability`** compares every path after normalization. It refuses as
  `PERSONAL_PATH_DEPENDENCY`, or as `UNEXPECTED_DEPENDENCY` for a path outside the release and the
  system:
  - a personal release root;
  - shebang interpreters, including `env`'s argument;
  - run-time sysconfig keys, all of which are required;
  - absolute pkg-config values and `-L`/`-I` flags;
  - libraries resolved or loaded by absolute path (`ldd`);
  - RUNPATH/RPATH entries, with `$ORIGIN` expanded.

  It also refuses:
  - `TEST_MODULES_PRESENT`, if the CPython test package is still installed;
  - `EVIDENCE_MISSING` / `EVIDENCE_MALFORMED`, unless every dynamic ELF object has exactly one
    `ldd` and one `readelf` block.

  Every other `/home/` or `/mnt/` literal is listed as a review finding only.
- **Tests and runbook:** tests added for each class (real dependency, harmless literal,
  missing/malformed evidence, test-module exclusion); runbook wording updated.

**Review:**
- **Focused read-only review:** no Blocker. Three Majors were fixed: `..` and `$ORIGIN` escapes,
  ldd absolute-path lines, ELF objects without evidence. Minors m1–m4 were also fixed.
- **Readback:** my own static readback of the rewritten function.
- **Not repeated after those fixes:** an independent re-review. The run then exposed defect D1
  (section 4) in that rewrite.

## 2. Frozen identities (before = after; checked by admission and post-checks)

| Path | SHA-256 | Logical B (alloc) |
|---|---|---|
| `tools/release/build_release.sh` | `c29a1e757a3e003787ced15e0364a9eb32645f795a3b028619e6de6d6eba9dbb` | 14,240 (16,384) |
| `tools/release/release_manifest.py` | `431e3e74bae49171806ed38b51ad6c9b5d77c3f9cab69feea91b1898f804c218` | 35,304 (36,864) |
| `tests/tools/test_release_manifest.py` | `52592a83ac84ed18d0e41878f8c6f5a672a634a34ac46dc880b2039da453c39f` | 38,857 (40,960) |
| `docs/deployment/README.md` | `4996042e4f3df65c3791b106a1aba245c24be50b3e5d29a68dd6e7cb0bdad6ef` | 17,895 (20,480) |

- **Also frozen, unchanged:** `deployment.py` `407a9576…`, `release_check.py` `e0031ebd…`,
  `install_release.sh` `fa11cb85…`, the two L2 test modules `e662c5bb…` / `06753aa4…`, L1
  `release_identity.py` `2dfb4fca…`, `measurement_build.py` `5c3619e4…`, the L1 test `807b08ed…`,
  the record tool `b30a2cd8…`, the rebind tool `180858b0…` and its test `88147043…`, and the T1
  helper `d17270ca…` and modules `a5227742…` / `a2d0543d…`.
- **Admission file:** 26 rows, `l2-expected.sha256` `7dbfb361…`.
- **Source snapshot:** 292 files (applications, backend, tools/release, tools/fixtures, the selected
  modules and helpers, conftest, pyproject).

## 3. Run

- **Workspace (fresh, native ext4):**
  `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-l2-dev-validation-20261023-1`.
- **Harness:** `inputs/l2-validate.sh` `1f63d5f2…`, written in the session scratchpad and copied in.
- **Command:** `COMMAND.txt` `d7bc0650…`.
  - environment: `env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC HOME=<ws>/home TMPDIR=<ws>/tmp
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1`;
  - limits: `timeout -s TERM -k 3 600 prlimit --as=2GiB --core=0 --fsize=16MiB -- time -v`;
  - interpreter: `cp313-bdw001/bin/python -I -B -X pycache_prefix=<ws>/pycache`;
  - pytest options: `-m pytest -c /dev/null --rootdir <repo> -o pythonpath=<repo> -p
    no:cacheprovider --basetemp <ws>/basetemp --junitxml <ws>/junit.xml -o junit_family=xunit2 -v
    --tb=short -ra` and the seven modules;
  - `tests/conftest.py` was kept.
- **Outer:** `timeout -s TERM -k 3 792`.
- **Environment:**
  - CPython 3.13.11, pytest 9.1.1, pluggy 1.6.0, no `.pth` files;
  - 1,266 R1 `PINS.sha256` rows matched before and after;
  - `/usr/bin/git` `eb54b535…`, used only by the fixture repositories.
- **Timings (UTC):**
  - outer 15:50:31.445 → 15:53:54.407, 202.96 s, exit 0;
  - admission 3.2 s;
  - pytest 15:50:34.709 → 15:53:51.938, rc 1 (`time -v` 3:17.21, maximum RSS 124,016 kB; pytest
    reported 207.80 s on this host's faster-running monotonic clock);
  - post-checks 2.5 s.
- **Signals and survivors:** none.

| Module | Collected | Passed | Failed |
|---|---|---|---|
| `test_deployment` | 44 | 42 | 2 |
| `test_release_check` | 15 | 15 | 0 |
| `test_release_manifest` | 104 | 70 | 34 |
| `test_release_identity` (L1) | 20 | 20 | 0 |
| `test_t1_rebind` | 80 | 80 | 0 |
| `test_maintained_increment` | 13 | 13 | 0 |
| `test_command_integration` | 15 | 15 | 0 |
| **Total** | **291** | **255** | **36** |

No test errored or was skipped.

## 4. Defects found (not repaired)

- **D1 (34 failures, `release_manifest.py:516, :534, :536`):** `portability.located(path, where, …)`
  is called with a detail keyword `path=…`, which collides with its own `path` parameter
  (`TypeError: got multiple values for argument 'path'`).
  - Every portability test reaches the shebang loop and fails there.
  - In a real build the uncaught `TypeError` would end the tool with a traceback, and the builder
    would refuse `PORTABILITY_CHECK_FAILED`. That fails closed, but no release could be built.
  - Introduced by the review-fix rewrite in section 1.
- **D2 (1 failure, `deployment.py:181`):** `load_config` passes the opened descriptor to
  `os.fdopen(fd, 'rb')` before its `fstat` regular-file check.
  - For a directory configuration path, `os.fdopen` raises `IsADirectoryError` instead of
    `CONFIG_INVALID`. Under `release_check` that becomes `INTERNAL_ERROR`, exit 7, not exit 5.
  - It still refuses, but with the wrong code. The same pattern exists in `read_text` (`:78`),
    where that error is caught.
- **D3 (1 failure, test defect):** `test_admission_is_stdlib_only_and_runs_no_git` parses lines
  beginning with `import ` or `from `. The narrowed docstring added to `deployment.py` during the
  L2 review has a line beginning `import of this package…`, so the test sees a spurious module,
  `of`. The test has been stale since that docstring edit.
- **Every other case passed:**
  - all 15 `test_release_check` cases, including the installed-copy initialization with Git-mode
    digest equality and no git on PATH;
  - the 20 L1 tests on the new tree;
  - the 80 rebinding cases and both T1 modules.

## 5. Preservation and compliance

- **Post-checks, all matching:**
  - the 26 frozen identities;
  - the 292-file source snapshot, with an unchanged file list;
  - the repository `__pycache__` listings: no change, and none beside the tools or new tests;
  - the 1,266 environment pins.
- **Git:** none against the maintained repository. Fixture Git ran only in temporary checkouts
  under the basetemp.
- **Not run:** no real build, installer run, service, VM or standalone rebinding.
- **Not claimed:** preservation of the historical workspaces, which were not scanned.
- **Unmeasured:** child-interpreter bytecode writes in unpinned cache locations. The tests' `-I`
  children ignore `PYTHON*` variables; the pinned files are unchanged.
- **Disclosure:** for diagnosis, the system `python3` parsed `junit.xml` as data. It imported no
  repository code.

## 6. Evidence

| File | SHA-256 (prefix) |
|---|---|
| `junit.xml` (136,818 B) | `a4fbe86b98b318eb…` |
| `pytest.stdout` (132,938 B) | `436f7d18543c6c4b…` |
| `pytest.stderr` (empty) | `e3b0c44298fc1c14…` |
| `time.txt` | `13bdc80b8e182305…` |
| `SUPERVISOR.log` | `d4a01daa5f4b9cdc…` |
| `admission.log` | `568d5b6fd80f73a5…` |
| `post.log` | `b379b8545c5f8dc2…` |

## 7. Accounting

- **Correction growth:**

  | File | Logical B | Allocated B |
  |---|---|---|
  | `build_release.sh` | +1,193 | +0 |
  | `release_manifest.py` | +12,295 | +12,288 |
  | `test_release_manifest.py` | +12,328 | +12,288 |
  | README | +693 | +0 |
  | **Total** | **+26,509** | **+24,576** |

  This receipt's sizes are reported in chat. 1 file, 0 directories.
- **Supplement for Codex's earlier writes** (a prior omission, separate from this grant):
  - the test edit was +487 logical B; allocation unchanged at 73,728 B;
  - its completion receipt is 4,162 logical / 8,192 allocated B;
  - together, 4,649 / 8,192, charged once here as a supplement.
- **Test workspace (separate reservation, observed only):**
  - 9,925 files, 3,517 directories, 207 other entries;
  - 77,753,883 logical and 122,155,008 allocated bytes;
  - within 16,384 / 8,192 / 256 MiB / 512 MiB.
- **Not borrowed:** no held capacity.

L2 implementation acceptance is not claimed. R1's 141 results, the three deferred cases, scoped L1
and scoped synthetic end-to-end acceptance keep their attribution. D-P remains open.

END RECEIPT
