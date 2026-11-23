# L2 Option B: implementation receipt

Date 2026-10-23. Grant: implement L2 under Option B (installed full synthetic workflow).
Implementation only.

**Nothing ran:** no application execution, tests, collection, imports, compilation, syntax checks,
probes, builds, downloads, installation, provisioning, K, Git command, checkout, commit or merge.
Verification was static reading only. No release-readiness or installed-workflow pass is claimed.

- **Governing documents, re-hashed before and after and unchanged:**
  - proposal `74a39d87586b50e91fb5862579f28c02f86c498a6fa69e02bfb97e487d059a1b`;
  - scope addendum `6bca403bf936cf47da0eea373af8b587578a4b995d2b6ffdd7cb48fb1b77425e`, which governs
    where the two differ;
  - reconciliation `7d8bff11889078b99ce927f1977459862a88b2f1f840136ddff54c9858dd4b42`.
- **Dispositions applied:**
  - Option B;
  - OD-L2-A: `core_pattern` is withdrawn from admission and recorded only;
  - OD-L2-B stays open: the manifest digest is an explicit input and no channel is named;
  - signing stays deferred.
  - No release commit was made, and OD-K2 is not resolved here.

## 1. Files (all new; no existing file edited)

| Path | SHA-256 | Logical B | Allocated B | Lines |
|---|---|---|---|---|
| `applications/bounded_decision_workflow/deployment.py` | `407a9576a6bb8983c4c968b5087463d2482ef1fe9e8b1ecc166b6775790a120e` | 12,633 | 16,384 | 320 |
| `applications/bounded_decision_workflow/release_check.py` | `e0031ebdbb565a641ecff750e3c751154a92992636cf832ece939a4ccc543ccd` | 9,254 | 12,288 | 204 |
| `tools/release/release_manifest.py` | `2ddf327c1ab0afc5489853b7c0c6a95c88b1fc27f1b04841924b58afc9eab175` | 23,009 | 24,576 | 508 |
| `tools/release/build_release.sh` | `e442d7b8a364c8a75aa4bbb38d362005eeea3e87522e8fdb502c5534911441d5` | 13,047 | 16,384 | 215 |
| `tools/release/install_release.sh` | `fa11cb85287306fa373a1d6ffdfb1774afbaad4854e7b542eb402527f7dd8b1f` | 8,471 | 12,288 | 172 |
| `tests/applications/bounded_decision_workflow/test_deployment.py` | `e662c5bb5d4f7981602f3b2cc71bd65f8bb13bb83c5d0e97c9a7c85a6579efa6` | 15,302 | 16,384 | 307 |
| `tests/applications/bounded_decision_workflow/test_release_check.py` | `06753aa48093a1f1d63e90be7ae0ea99fd55c89b4021d47c27ce95d46854875e` | 16,651 | 20,480 | 301 |
| `tests/tools/test_release_manifest.py` | `00e8f7047cff47d4b4e70abb1a0aa713ffe7e4ff7988698147bcc696072b7f56` | 26,529 | 28,672 | 532 |
| `docs/deployment/README.md` (runbook) | `03aeb44df4858e0dca29912526776cb50e051e55b38c9cd74c0eb8672c86c67a` | 17,202 | 20,480 | 237 |

- **New directories:** `docs/deployment` (1 of 3).
- **No `__pycache__`** exists beside the new modules or under `tools/release`.
- **Paths:** the test and runbook paths are exactly those in addendum §5.1.

## 2. Interfaces

- **`deployment.py`** (stdlib only):
  - `preflight` runs A1 then A2. `load_config` is A3: file and closed keys. `admit` runs A3
    (account exists) and A4–A7. `admit_path` runs all of them.
  - An injectable `Host` supplies the account database, euid, platform, mount reader, running
    release, clock, pid and record-only reads.
  - `DeploymentRefusal` carries the `CheckedRefusal` fields, so admission imports no contract module.
  - The data root must be exactly ext4, checked through the descriptor's mount, for the root
    itself and for `tmp` and `evidence`.
  - The A7 release-tree walk excludes symlink modes.
- **`release_check.main`:**
  - Order: admission, then imports of the four command families, then
    `checked_runtime._current_build(ExecutableBuild())`, then `t1_package.safe_new_dir` and one
    `startup-receipt.json` (0600, fsync), printed on stdout too.
  - Diagnostics are `ct.diagnostic.v1`; exits are 5, 3, 2 or 7, as in addendum 1.3.
- **`release_check.workflow_main`:**
  - The same admission, then the maintained `checked_cli.main` / `t1_cli.main`, for the `checked-`
    and `t1-` families only.
  - `--output-dir`, `--scratch-dir` and `--diagnostic-dir` must name paths below the data root.
    This is a textual check.
- **`release_manifest.py`** (stdlib only) subcommands:
  - `create`, `verify` (expected digest checked before parsing), `source-set` (the L1 rule) and
    `sonames`;
  - `check-archive` and `extract` (members validated first, then the `'data'` filter);
  - `publish` (`renameat2 RENAME_NOREPLACE`);
  - `config` (exclusive, template must equal the arguments) and `record` (descriptor-anchored,
    exclusive).
- **`build_release.sh`** (build host only):
  - Every external input is an argument with its own expected SHA-256. All digests are checked
    before anything is created.
  - Then: the `git archive` export with `tar.umask=022`, check (i) source set == `D_dev`, committed
    tooling == running tooling, CPython built for `R_REL/python`, wheels installed through a
    build-only zipapp pip, lock-set equality, the `direct_url`/bytecode refusals, the L1 record,
    check (iii), two fixed `-I -B` wrappers (`ohk-bdw-check`, `ohk-bdw-run`), sonames, the
    self-checks, the manifest, the tarball and `BUILD-RECORD.json`.
- **`install_release.sh`** (root, offline): steps 1–7, matching proposal 4.5. No deletion on
  failure, and `--signature` refuses with `SIGNATURE_POLICY_UNDEFINED`.

## 3. Tests written (not run)

| File | What it covers |
|---|---|
| `test_deployment.py` | A1–A7 order and codes; configuration syntax, size, owner, mode and symlink edges; xfs/tmpfs/ext3 refusal before owner and mode; separately mounted subdirectories; `TMPDIR`; release-tree writability, symlink targets, FIFOs, foreign owners; mount-row parsing; stdlib-only admission |
| `test_release_check.py` | **Subprocess** installed copy of the current trees (L1 record, PATH without git): the receipt's `ct` and `nm` digests equal a Git-mode computation, exactly one new directory and file, no release writes, no bytecode. Existing evidence directory → `SIM_OUTPUT_UNSAFE`. Extra file → `BUILD_IDENTITY_UNAVAILABLE` with no output. Tampered schema → `EDITION_CONTENT_MISMATCH` before the build. Admission precedes the checked/T1/build imports. Usage and root; `workflow_main` family restriction, confinement and dispatch to the maintained checked CLI |
| `test_release_manifest.py` | Round trip; tamper, mode, exec-bit, type, symlink and bytecode refusals; digest checked before parsing; archive traversal, hard links, devices, FIFOs, symlink chains, members below symlinks, modes; overwrite refusal; partial retention; no-replace publish, including the kernel path; exclusive configuration and record; CLI exit codes; builder refusals of absent or unverified inputs, executed up to the refusal; the installer refusing non-root and signatures; static checks for no network and no embedded external digest |

- **Requirements:** a non-root user; an ext4 basetemp that supports `RENAME_NOREPLACE`; a
  development interpreter that is exactly CPython 3.13.11 on x86_64. The tests use Git only to
  build fixture repositories.
- **What the tests guarantee:** unit-level logic only. Real interpreter build, installation and
  VM evidence are later work.

## 4. Focused review

**First pass** (read-only `code-reviewer`): no Blocker.

**Fixed:**
- M1: archive members written through symlink members. Parents must now be directory members,
  and symlink targets may not contain `..`.
- M2: the root installer followed a path inside the account's data root. The record is now written
  descriptor-anchored, and the path-based chmod is gone.
- M3: the staging runbook would have failed. It now does `chown -R -h root:root`, uses a
  root-owned staging configuration and verifies as root.
- m1: the import-ordering claim is narrowed to what holds, and its test was renamed and extended.
- m2: modes the extraction filter would rewrite are refused at build time.
- m3: the kernel no-replace path is now tested.
- m4/m5: a working `run()` function in the runbook, with `timeout` and `prlimit --core=0`.
- m6: the runbook now says `-m pytest`.
- m8: pip runs with `--isolated` and `PIP_CONFIG_FILE=/dev/null`.
- Low items fixed: empty `--output-dir=`, the tool list, the builder header, runbook flags, the
  trust and diagnostic-shape notes, test docstrings.

**Readback** (separate read-only pass over the changed portions): every fix was confirmed. Its four
Low residuals were then fixed and re-read by me:
- the pip configuration claim;
- execute-bit modes the filter rewrites;
- the record docstring, plus an existing data root's parent must now be root-owned;
- the step 12/13 wording.

**Unresolved, owner decisions:**
- **M4.** The designed personal-path self-check (addendum 2.3) scans the whole staged tree.
  `make install` installs `Lib/test`, which very likely contains `/home/…` literals, so the build
  would refuse. Amend the construction (for example `--disable-test-modules`) or narrow the check.
  Implemented as designed, not changed.
- **m7, interface extension beyond addendum 1.4:** `workflow_main`, the `bin/ohk-bdw-run` wrapper,
  and the codes `INSTALLED_COMMAND_UNSUPPORTED` and `OUTPUT_OUTSIDE_DATA_ROOT`. This is added for
  the Option B installed workflow; the dispatcher and existing commands are unchanged.

**Other low notes:**
- The installer and `release_manifest.py` are trusted as delivered.
- The `ldconfig` soname match ignores architecture.
- `git archive` attributes could make the export differ from the blobs; check (ii) on staging
  covers that.
- Whether CPython's `make install` creates a `..` symlink, which would now refuse, is
  unverified until a real build.

**Outside the grant (recorded, not changed):**
- The working tree's modified `measurement_build.py`, untracked `release_identity.py` and the L1
  test match the L1-attributed working-tree bytes (`5c3619e4…`, `2dfb4fca…`, `807b08ed…`;
  record tool `b30a2cd8…`). They predate this grant.
- The patch level of noble's `python3` for the tarfile data-filter CVEs.
- The L1 tool docstring still says "signed" (disclosed in the runbook).

## 5. Departures from the design

- **Publication:** `renameat2(RENAME_NOREPLACE)` in `release_manifest.py publish`, in place of
  `mv -T -n` plus a result check. The property is the same, the exit status is unambiguous, and
  the step can be tested without root. The result check is kept.
- **Extraction:** archive validation and extraction use stdlib `tarfile` (validate first, then the
  `'data'` filter) under the system `python3`, rather than GNU `tar -x`.
- **Release identity:** written with the staged interpreter (`-I -B`); git still runs only on the
  build host.
- **Sonames:** `ldd` also covers site-packages extension modules.
- **Configuration:** the template is validated against the installer arguments and written by
  `release_manifest.py config`.
- **Owner decision noted in section 4 (m7):** the `workflow_main` / `ohk-bdw-run` installed entry
  for Option B.

## 6. Accounting

- **This grant:**
  - new logical bytes 142,098 for the nine files, plus this receipt (reported in chat);
  - allocated 167,936 plus this receipt;
  - directories 1 (0 blocks reported);
  - positive growth of existing files 0.
- **Caps:** 1,048,576 logical and 1,310,720 allocated. Final remaining capacity is in chat, so
  this file holds no self-hash.
- **Balance:** charged against the unreserved implementation/preparation balance, starting from
  11,510,757 / 25,989,120 (after the rebind correction).
- **Not charged here:** Codex's later test edit (+487 B) and its receipt (4,162 B) were not
  accounted by Codex. They are noted, and not charged in this grant.
- **Not borrowed:** no held capacity or spent execution reservation.
- **Edit method:** one early batch of edits to `release_check.py` was a plain-text replacement
  made by a shell-invoked `python3` script that imported no repository code. All other edits used
  the editor.
- **No scratch files** were created.

## 7. Preservation

- **Unchanged:**
  - the governing documents and both L2 documents;
  - the rebinding tool `180858b0…` and its tests `88147043…`;
  - both earlier rebind receipts;
  - sealed packages and runtime evidence;
  - the L1 sources;
  - the dispatcher and every historical gate.
- **Attribution kept:** R1's 141 results, the three deferred cases, scoped L1 and the historical
  synthetic end-to-end acceptance. Adding the L2 modules changes the application source set, so
  existing L1 and workflow acceptance do not cover the new tree. D-P remains open.

END RECEIPT
