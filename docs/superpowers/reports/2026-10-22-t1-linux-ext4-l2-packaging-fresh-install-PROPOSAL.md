# T1 Linux/ext4 L2: packaging and fresh-install startup slice (proposal)

Date 2026-10-22. Branch `claude/t1-startup-chain-repair`. Preparation only.

- Nothing in this file is implemented, built, installed, activated or validated.
- No test, import, compilation, syntax check, interpreter probe, Git, K or commit was run.
- Labels: **[ACC]** accepted by the owner; **[PROP]** proposed here; **[PRIOR-PROP]** proposed
  earlier and not approved; **[est]** estimate; **[unmeasured]**.

## 1. Scoped L1 acceptance (owner decision recorded here)

### 1.1 Evidence verified read-only (2026-10-22)

The evidence root is
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-linux-ext4-l1-validation-20261022-3/`.
All five named records are accessible and match:

| Record | SHA-256 |
|---|---|
| DRIVER.py | `30bbcd8197d83b1dc7675f4c95a146f9d90d9bc583ea5f4d4c5fa186c5894035` |
| RECEIPT.md | `b4931168c1aa3d4aedf84072676669da5cd9da52470b81a8c890ec9bc86ee1c2` |
| STATUS.json | `87cb53652064f8403e562bfd60199f933d31d4e6cb437839ea1283b2fc12bfaa` |
| ACCOUNTING.json | `7e45b34f4443758d450518bcc3667e93022b238216d55a86a13e02fd854314e5` |
| junit.xml | `42e32f9fd3fb5a13cb56efc8d831cc27c9c57e8aa3b7aee55d8f29edce7436eb` |

**What "verified" means here:** the hashes match the owner's figures. Pytest's results are not
independently re-verified; the file contents were produced by the run itself, and I re-ran
nothing.

### 1.2 Accepted result [ACC]

| Item | Value |
|---|---|
| Cases | Exactly 20 selected L1 cases passed. Failed, errors, skipped, unexecuted and unexpected were all 0 |
| Pytest | Launched once; reported "20 passed in 11.82s" |
| Outer exit | 0 |
| Overall | About 21.39 s |
| Preservation | The enumerated checks passed before and after: 19 pinned repository records, 5 captures, 5 Git identities, the applications/backend tree, the 10 environment identities and all 1,378 pins |
| Enforcement | No deadline, TERM or KILL enforcement was exercised |

### 1.3 Attribution

**Source:**
- `test_release_identity.py` `807b08ed…`, `measurement_build.py` `5c3619e4…`,
  `release_identity.py` `2dfb4fca…`, `release_identity_record.py` `b30a2cd8…`, and lock
  `7c87f0d7…`.
- These were working-tree bytes on HEAD `07055c63…` with index `43dca87c…`. **They are not a
  repository commit.**

**Applications/backend tree, from the run's journal (`repository_before`, unchanged after):**
- 510 entries (445 files, 65 directories) and 5,468,787 B.
- Excluding `__pycache__`: 246 source files, 2,804,908 B.
- This file defines the **L1 tested source-set digest** as the SHA-256 of the compact JSON
  (`separators=(',',':')`) of the sorted list of `[path, sha256, bytes]` for those 246 files:
  `e6c9f2a342c70b2aace64315442707b3cb1783cc18a5e54f5f95ccf205ed47c0`. It was computed by plain
  parsing of the retained journal.

**Environment:**
- `/home/mafasa/miniconda3/bin/python3.13` `47f615b1…` (CPython 3.13.11), venv `pyvenv.cfg`
  `e957ced4…`, and the 1,378 R1 environment pins (`PINS.sha256` `841490aa…`).
- WSL2, kernel 5.15.167.4-microsoft-standard, ext4 workspace.
- Git `/usr/bin/git` `eb54b535…` was used as the test oracle only.

**The accepted claim:** L1 source-witness behaviour and matched-environment production
integration. That includes installed-copy behaviour without runtime Git: installed-mode `nm` and
`ct` identities equal Git-mode ones for the same commit, bytes and interpreter, and the fourteen
divergence refusals hold.

**Not established:** packaging, fresh installation, deployment-target support, containment,
authoring, the complete workflow or enterprise readiness.

**Unchanged:** R1's 141 results keep their attribution, and the three deferred cases stay deferred.
D-P is open. Both failed attempts and all historical records are unchanged and not relabelled.

## 2. Inputs reused and their status

| Decision | Status | Use in L2 |
|---|---|---|
| ID-1, installed-release witness equivalence under `nm.build.v1`/`ct.build.v1` | [ACC] | Installed runs use `release_identity`, not Git. Installed runs start through a fixed `-c` string |
| OD-K2, portability before historical K | [ACC] | L2 proceeds; historical K stays unexecuted |
| L1 result (section 1) | [ACC] | The verifier and record schema `bdw.release-identity.v1` are reused unchanged |
| PD-1 Ubuntu Server 24.04 amd64, cgroup v2, systemd 255 | [PRIOR-PROP] | The owner names the 24.04 amd64 ext4 target as proposed initial target; not qualified |
| PD-2 x86_64 only | [PRIOR-PROP] | Retained: the hashed lock pins a `manylinux_2_17_x86_64` pydantic-core wheel |
| PD-3 CPython 3.13.11 built from python.org source at a prefix and shipped | [PRIOR-PROP] | Retained as the recommendation (OL-3) |
| PD-3b the 10 wheels of the hashed lock, installed by hash, offline | [PRIOR-PROP] | Retained. pytest and its deps stay in the runtime identity because the lock includes them (ID-4 open) |
| PD-4 one offline tarball plus manifest plus detached signature | [PRIOR-PROP] | Tarball and manifest retained. The signature is unresolved (ID-2), see 3.6 |
| Fixed prefix "installing elsewhere is refused" | [PRIOR-PROP] | **Superseded by this proposal:** prefix configurable at build time (3.3) |
| ID-2 signing; ID-3 stdlib/libpython in identity; ID-4 lock split; ID-5 authoring; ID-7 crash handler | Open | ID-2, ID-3 and ID-7 are addressed narrowly in 3.6, 4.6 and OL-5; ID-4 and ID-5 are untouched |
| D-P provenance | Open | Hashes establish integrity relative to the stated reference, never provenance |

## 3. Release contents and identity [PROP]

### 3.1 Release layout

Relative to the release root `R_REL` (section 3.3):

```text
R_REL/
  python/                    CPython 3.13.11 built for prefix R_REL/python (stdlib, lib-dynload, libpython, site-packages with the 10 locked wheels)
  app/
    applications/            exactly the committed release-input tree
    backend/                 exactly the committed release-input tree
    RELEASE-IDENTITY.json    L1 record, install_root = R_REL/app
  bin/ohk-bdw-check          3-line POSIX sh wrapper (3.5); its only variable part is R_REL
  RELEASE-MANIFEST.json      package-integrity manifest (3.4)
```

**Excluded:**
- `tests/`, `docs/`, `tools/`, `showcases/`, `.git`, `.vscode/` and `.claude/`;
- every `__pycache__` under `app/`;
- the developer checkout, the personal miniconda and the WSL venv;
- pip, `ensurepip`, `wheel` and setuptools, which are removed after the build;
- build logs and wheelhouse paths, and any `direct_url.json`.

Wheels are installed by name and hash from a local wheelhouse, never by file URL.

**Configuration** is not part of the release (section 4).

### 3.2 What each mechanism covers

| Release part | L1 release identity (`release_identity.verified_source`, at every startup) | `nm.build.v1` environment manifest (computed at startup) | RELEASE-MANIFEST (install time, and the validation re-check) |
|---|---|---|---|
| `app/applications`, `app/backend` | **Yes:** Git commit, root tree, subtree ids, blob ids, owner-exec bit, no extras, no symlinks, no `.git` | Source manifest (SHA-256 of `.py` files and lock) | Yes |
| `app/RELEASE-IDENTITY.json` | Self-consistency (commit/tree chain, `install_root`) | No | Yes |
| `python/bin/python3.13` | No | **Yes** (executable SHA-256) | Yes |
| The 10 locked distributions (their RECORD files, excluding `.pyc`) | No | **Yes** (per-distribution artifact manifest) | Yes |
| stdlib, `lib-dynload`, `libpython3.13.so*`, `.pyc` everywhere, and non-distribution site-packages files | No | No (ID-3 open) | **Yes, manifest only** |
| `bin/ohk-bdw-check` | No | No | Yes |
| System shared libraries (glibc, libssl, libffi, zlib, libsqlite3 and others) | No | `libc_ver` only | **No.** Recorded as a required soname list, checked by the installer (4.4) |

Two of the columns run at every startup check. The manifest is verified by the installer and
re-verified in the fresh-install validation (section 6). It is not repeated at every startup;
that is a deliberate bound, OL-4.

### 3.3 Prefix: configurable at build time

- The release root `R_REL` is a **build parameter**. Recommended example:
  `/opt/ohk-bdw/releases/<release-id>`.
- **Why build time:** the record's `install_root` must equal the resolved `R_REL/app`, and
  console-script shebangs in distribution RECORDs embed `R_REL/python`. Those RECORD files are
  hashed into `nm.build.v1`.
- **Consequence:** a release is bound to one prefix, and a different prefix means a different
  release. Installing at another path is refused, because the identity check fails on
  `install_root`.
- **Rejected:** install-time relocation by rewriting `install_root`. It would mutate a record
  after packaging, and console-script bytes would still name the build prefix.
- **`<release-id>`:** `<commit[:12]>-<prefix-tag>-<build-seq>`. It is a label only, and the
  manifest digest is the identity of record.

### 3.4 RELEASE-MANIFEST.json (`ohk-bdw.release-manifest.v1`)

**Content** (canonical JSON with sorted keys):
- `release_root`, `commit`, and the L1 tested source-set digest when applicable (3.7);
- `python_version` `3.13.11` and `platform` `linux-x86_64`;
- `required_sonames` (from `ldd` at build);
- `entries`: one per file or directory under `R_REL` except the manifest itself:
  - `path` (relative), `type` (`f`, `d` or `l`);
  - `mode` (octal permission bits; files and directories only);
  - `bytes` and `sha256` for files, and `target` for symlinks.

**Symlinks:**
- Allowed under `python/` only. For example, `python/bin/python3 -> python3.13`. Targets must stay
  inside `R_REL`.
- Under `app/` they are forbidden, and L1 refuses them anyway.

**Verifier:** `tools/release/release_manifest.py verify --root R_REL --expect-sha256 <digest>`.
- It is stdlib only and runs with the system `python3` at install, or with the release's own
  interpreter.
- Each check passes only if the manifest file's SHA-256 equals the expected digest, the file set
  equals the entries exactly (no extras), every type, mode, size, hash and link target matches,
  and no file or directory is group- or other-writable.
- **Symlinks are excluded from mode and writability checks.** On Linux every symlink reports
  0777, so applying the rule to them would refuse every legitimate release. Instead, each symlink
  must be root-owned, its target must match the manifest, and its resolved target must stay inside
  `R_REL`. Its mode is not recorded.
- Exit 0 on success, 1 on mismatch with a one-line JSON diagnostic, 2 on usage error.

### 3.5 Startup wrapper `bin/ohk-bdw-check`

```text
#!/bin/sh
exec R_REL/python/bin/python3.13 -I -B -c 'import sys; sys.path.insert(0, "R_REL/app"); from applications.bounded_decision_workflow.release_check import main; raise SystemExit(main())' "$@"
```

- **`R_REL`** is substituted literally at build time.
  - The builder refuses an `R_REL` outside `[A-Za-z0-9/._-]`, so the quoted `-c` string cannot be
    broken.
  - `R_REL` must have no symlink component on the target, because `install_root` must equal the
    resolved path. The installer checks this, and so does the startup check (4.3).
- **OL-1(b):** under that option the L2 module lives in a separate top directory, `app/deploy/`,
  which L1 does not walk. The wrapper then imports `deploy.release_check`, with `app/` on
  `sys.path`.
- **`-I -B` with the fixed `-c` string** is the ID-1 start form. It means no `.pth` file, and no
  `PYTHONPATH`, user site or cwd import.
- **Root:** must never import from `app/` without `-B`. That would create `__pycache__` and
  permanently fail L1 identity; the read-only ownership is a second defence. This is the runbook
  rule.

### 3.6 Integrity versus signature

- **Checksum verification [PROP, implementable now]:** the builder publishes the manifest's
  SHA-256 through a channel the owner designates. The installer refuses unless the downloaded
  manifest matches that digest and every entry verifies. This establishes integrity only relative
  to the channel that delivered the digest. It does not authenticate the builder, and D-P stays
  open.
- **Signature verification [unresolved]:** ID-2 is still open, so this design sets no keys, signer,
  tool or trust anchor. If ID-2 is resolved later, a detached signature over the manifest digest is
  verified *before* the checksum step. The installer's interface reserves `--signature` and fails
  with `SIGNATURE_POLICY_UNDEFINED` if it is passed before the policy exists. No signing service is
  established here.

### 3.7 Making the tested source a release input

The L1-tested bytes are uncommitted working-tree bytes. The release record needs a real commit, so
nothing may pretend that commit already exists.

1. **Commit [owner grant, OL-1]:** an owner-authorized commit `C` in the maintained repository,
   containing the exact intended `applications/` and `backend/` content. That content is the
   L1-tested 246 files plus the L2 code of section 5, if the owner keeps it under `applications/`.
2. **Build-host gate [PROP]:** before packaging, the builder computes the tested-set digest rule
   (1.3) over `C`'s `applications/` and `backend/` files.
   - If `C` contains only the L1-tested bytes, the digest must equal `e6c9f2a3…`, and the manifest
     records it as `l1_tested_source_set`.
   - If `C` adds L2 files, the digest differs. The manifest then records `l1_tested_source_set:
     null`, and the release relies on re-running the L1 tests (and the L2 tests) against `C`,
     because L1 acceptance does not transfer to changed bytes.
3. **Release identity:** `release_identity_record.py C … R_REL/app` runs on the build host, the
   only place Git runs. That is L1 unchanged.

Equality of content links tested bytes to `C`. It is not provenance.

### 3.8 Bytecode, modes and post-install mutation

| Mechanism | Behaviour |
|---|---|
| `app/` | No `.pyc` is shipped. Imports run with `-B`, and the tree is root-owned and read-only to the runtime account. Any `__pycache__` that appears (for example, root importing without `-B`) makes L1 refuse at the next startup. **Fail-closed by design** |
| `python/` | Stdlib `.pyc` from `make install` are shipped and listed in the manifest. Wheels are installed with `--no-compile`. The runtime account cannot write there, and the startup check's `RELEASE_TREE_UNSAFE` walk (4.6) checks that |
| Modes | Release files are root:root 0644, executables 0755, directories 0755. The owner-exec bit under `app/` must equal Git's `100644`/`100755` (L1). The installer extracts with `--no-same-owner`, then sets ownership explicitly, preserving permission bits |
| Post-install change | Under `app/`, refused at every startup (L1). Elsewhere, detected by manifest re-verification (install and validation), plus the `RELEASE_TREE_UNSAFE` writability check at every startup. Between manifest checks, a root-level change outside `app/` and outside the distributions is undetected. This limit is disclosed |

## 4. Installation and configuration [PROP]

### 4.1 Locations (all configurable; none hard-coded in the startup code)

| Purpose | Recommended | Owner / mode | Rule |
|---|---|---|---|
| Release | `/opt/ohk-bdw/releases/<release-id>` | root:root, 0755 directories, 0644 or 0755 files | Immutable; bound at build (3.3) |
| Configuration | `/etc/ohk-bdw/deployment.json`, path passed with `--config` | root:root 0644 | Not writable by the runtime account |
| Writable state | `/var/lib/ohk-bdw` (the `data_root`) | runtime account, 0700 | Local ext4; no symlink components |
| Scratch | `<data_root>/tmp` | runtime account, 0700 | `TMPDIR` for the check |
| Evidence | `<data_root>/evidence/<run-id>/` | runtime account, 0700 | Startup receipts |

The portable path removes these host-specific dependencies:
- `/mnt/d/operation-house-keeping` and personal home directories;
- dated cgroup names, UID 1000 and the exact WSL core handler.

### 4.2 Runtime account

- **Creation:** `adduser --system --group --home /var/lib/ohk-bdw --shell /usr/sbin/nologin
  ohk-bdw`. The UID is allocated by the system, never fixed.
- **No privileges:** no sudo, no extra groups, no capabilities.
- **Resolution:** the startup check reads the configured account **name** through `pwd`. It
  requires euid equal to that account's uid, and euid not 0.

### 4.3 Configuration `ohk-bdw.deployment.v1` (closed key set; at most 64 KiB)

```text
{"schema": "ohk-bdw.deployment.v1",
 "release_root": "/opt/ohk-bdw/releases/<release-id>",
 "runtime_account": "ohk-bdw",
 "data_root": "/var/lib/ohk-bdw",
 "core_pattern_ack": "<exact /proc/sys/kernel/core_pattern text the administrator accepts>"}
```

**Check order and codes.** The startup check refuses at the first failure, before any other work,
in this order:

1. **Euid 0:** `RUNTIME_ACCOUNT_INVALID`. This is the first check, before the configuration is
   even opened.
2. **Platform:** `PLATFORM_UNSUPPORTED`.
3. **Configuration items 1–4 and 6 below:** `CONFIG_INVALID`.
4. **Euid not equal to the account's uid:** `RUNTIME_ACCOUNT_INVALID`.
5. **Item 5 below (data root):** `FILESYSTEM_UNSUPPORTED` if it is not ext4; `CONFIG_INVALID` for
   owner or mode.
6. **The core-handler acknowledgement, then the release-tree walk.**

All refusals exit 5.

**Configuration validation:**

1. **The configuration file itself:**
   - is a regular file reached without following symlinks;
   - is owned by root, mode with no group or other write bits, and not writable by the euid;
   - is at most 64 KiB, UTF-8 JSON and an object with exactly these keys.
2. **Paths:** absolute, normalized, without `..` components, with no symlink component (checked
   by an `lstat` walk).
3. **`release_root`** equals the release that is actually running, derived from
   `os.path.realpath(sys.executable)` minus `/python/bin/python3.13`.
4. **`runtime_account`** exists in `pwd`.
5. **`data_root`** is checked by an open directory descriptor's mountinfo row, using the same
   method as `retention._filesystem`. That function accepts ext4 *or* xfs (`retention.py:100`).
   L2 requires exactly **ext4**, so `deployment.py` applies its own ext4-only comparison to the
   same row, and a test covers xfs refusal. The data root must also be owned by the euid, mode
   0700.
6. **`core_pattern_ack`** is a string of at most 4,096 B (see 4.6).

`tmp` and `evidence` are fixed subdirectories of `data_root`, created by the installer and checked
by the startup check.

### 4.4 Interpreter and dependency provisioning (offline install)

**Build host** (a reference Ubuntu 24.04 amd64 machine, not the target):
1. Build CPython 3.13.11 from the python.org tarball (SHA-256 recorded) with
   `./configure --prefix=R_REL/python --enable-shared --with-ensurepip=no` and
   `LDFLAGS=-Wl,-rpath,R_REL/python/lib`.
2. Install the 10 wheels from the hashed lock (`6bcc7bd8…`) with:
   `R_REL/python/bin/python3.13 -m pip install --no-index --find-links wheelhouse --require-hashes --only-binary=:all: --no-compile -r requirements-hashed.txt`.
   The pip used here runs as a build-only zipapp (`python3.13 pip.pyz …`). It is never installed
   into the prefix, so no residue removal is needed.
3. **Never delete a file listed in a locked distribution's RECORD.** `measurement_build` requires
   every RECORD-listed file to exist, otherwise `BUILD_IDENTITY_MISMATCH`. The builder refuses if
   any non-locked distribution (pip, setuptools, wheel) or any `direct_url.json` is present.
4. Record `required_sonames` from `ldd` over `python3.13`, `libpython3.13.so.1.0` and
   `lib-dynload/*.so`.

**Target:**
- The installer is a root-run POSIX shell script using only base-system tools: `tar`, `sha256sum`,
  `install`, `adduser`, `chown`, `chmod`, `mkdir` and `ldconfig -p`, plus the release's own
  interpreter for `release_manifest.py`.
- It needs no network, no compiler, no Git and no package installation.
- It refuses unless every `required_soname` is present in `ldconfig -p`. If a library is missing
  (libssl3, libffi8, zlib1g, libsqlite3-0, libbz2, liblzma, libreadline), that is a provisioning
  decision for the administrator, outside the product.

**Native dependencies:**
- pydantic-core needs glibc ≥ 2.17 (manylinux_2_17); noble ships 2.39 [DOC].
- The interpreter's extension modules link the noble libraries listed above.
- Noble sqlite/glibc effects on T1 output bytes are unmeasured, but they are out of the L2 startup
  slice.

### 4.5 Installer behaviour (`tools/release/install_release.sh`, root, offline)

```text
install_release.sh --tarball T --manifest-sha256 D --release-root R_REL --config-template C --data-root DR --account ohk-bdw
```

**Steps:**
1. Refuse unless the platform is Linux x86_64 and the parent of `R_REL` is root-owned and not
   writable by others.
2. Extract into `R_REL.partial` (exclusive; refuse if it exists) with `--no-same-owner`, then
   `chown -R root:root`.
3. Verify the manifest (3.4) against `D` and check the sonames (4.4).
4. Create the account if it is absent. Create `DR`, `DR/tmp` and `DR/evidence` with mode 0700,
   owned by the account. Refuse unless `findmnt -n -o FSTYPE --target DR` prints `ext4` (`stat -f`
   cannot tell ext4 from ext2/3).
5. Write the configuration from `C` with exclusive creation, mode 0644, root-owned.
6. Move `R_REL.partial` to `R_REL` with `mv -T -n R_REL.partial R_REL`. `-T` stops the move
   *into* an existing directory, and `-n` refuses to replace. Then refuse unless `R_REL` exists and
   `R_REL.partial` does not. The `R_REL` absence is also checked in step 1.
7. Write an install record (manifest digest, sonames, config digest) to
   `/var/lib/ohk-bdw/evidence/install-<id>.json`.

**Failure handling:**
- On any failure the partial directory stays for inspection, and nothing is activated.
- There is no `current` symlink and no automatic upgrade or uninstall in L2. Uninstall is a
  documented manual step under owner disposition.

### 4.6 Host-specific checks replaced, not dropped

| Old host-specific check | Safety property it served | Portable replacement in L2 |
|---|---|---|
| Path pins under `/mnt/d/...` | Exact code under execution | L1 release identity at every startup, plus manifest verification |
| Personal-home runtime paths | Isolated writable state | Configured `data_root` (ext4, owner-only); writes only under it |
| Dated memory cgroup and slice names | Resource containment | **Not needed for one startup check.** The check runs under per-process rlimits (RLIMIT_AS 1 GiB, RLIMIT_FSIZE 8 MiB, RLIMIT_CORE 0) and a `timeout`. Containment for workloads (slice ceiling, cgroup v2) stays a later slice, **unresolved** for workloads (OL-6). L2 claims no containment |
| UID 1000 | The run as the intended unprivileged account | Account name resolved through `pwd`; euid must match; euid 0 refused |
| Exact WSL core handler | No unreviewed core capture | The administrator records the exact `core_pattern` they accept in `core_pattern_ack`. The startup check refuses with `CORE_HANDLER_UNACKNOWLEDGED` on mismatch and records the value. RLIMIT_CORE 0 stops non-pipe cores. **Who may accept a pipe handler (ID-7) stays open (OL-5)** |
| `.git` absence by convention | No runtime Git | L1 refuses `.git` under the root. The check runs with a `PATH` that has no git. The fresh-install target has no git installed (section 6) |

**Refusal codes**, using the existing diagnostic shape and emitted before any application input
is read:
- `PLATFORM_UNSUPPORTED` (not Linux x86_64 CPython 3.13.11);
- `CONFIG_INVALID`;
- `RUNTIME_ACCOUNT_INVALID`;
- `FILESYSTEM_UNSUPPORTED` (existing);
- `RELEASE_TREE_UNSAFE`: any file or directory under the release that is not root-owned, or is
  writable by the euid (checked with `os.access(W_OK)` on directories and files). The walk does not
  follow symlinks. Symlinks are checked only for root ownership and for a target inside the
  release; their mode is ignored;
- `CORE_HANDLER_UNACKNOWLEDGED`;
- `BUILD_IDENTITY_UNAVAILABLE` (existing; exit 5 through `ExecutableBuild`).

The exit codes follow the existing diagnostic table: 5 for platform, path and refusal codes; 7 for
internal errors.

## 5. Startup boundary [PROP]

### 5.1 Maintained entry points

| Entry point | Build-identity path | Installed release |
|---|---|---|
| `python -m applications.bounded_decision_workflow` (`__main__` → `cli.main`, the S1–S7 workflow) | `build.identity()`: **Git only** | Would refuse with `REPLAY_BUILD_UNAVAILABLE` |
| Governed commands | `governed_build.identity()`: **Git only** | Would refuse |
| Measurement, reassessment, checked and T1 commands | Through `measurement_build.identity()` and `ExecutableBuild` | Use the L1 installed witness |

So installed-mode support is currently limited to the `measurement_build` family. L2 establishes
nothing for the first two rows. Extending installed mode to them is later work, not part of this
slice.

### 5.2 The L2 startup check

**New module:** `applications/bounded_decision_workflow/release_check.py`, about 150 lines.
`main(argv)` accepts exactly `--config PATH` and `--evidence` (optional; writes the receipt under
`<data_root>/evidence/`).

**What it does, in order:**
1. **Admission checks, in the exact order and with the codes of 4.3:**
   1. euid 0;
   2. platform;
   3. configuration;
   4. account match;
   5. data root, plus `TMPDIR` must equal `<data_root>/tmp`;
   6. core-handler acknowledgement;
   7. the `RELEASE_TREE_UNSAFE` walk of `release_root`.
2. **One identity computation:**
   - It calls `checked_runtime._current_build(ExecutableBuild())` once
     (`checked_runtime.py:37–66`).
   - That calls `measurement_build.identity()`, which takes the installed path, so
     `release_identity` verifies `app/` with no Git.
   - It wraps the `nm` wire. Every identity failure maps to `BUILD_IDENTITY_UNAVAILABLE`, stage 5.
   - The `nm` digest is taken from the same `measurement_build` wire. Identity is not computed a
     second time.
3. **Emit** one canonical-JSON receipt on stdout (`ohk-bdw.startup-receipt.v1`), exit 0. The
   receipt holds: schema, `release_root`, commit, the `nm` and `ct` build wire SHA-256s, the
   manifest digest from the install record if present, `core_pattern` observed, euid and account,
   `data_root` fstype and mount options, and timestamps. Each refusal emits the diagnostic on
   stderr and exits 5. An internal error exits 7.

**What it establishes:** successful initialization only. That is admission, an L1-verified
release, and computable `nm`/`ct` build identities in installed mode without Git.

**What it does not establish:** evaluate, verify or replay; any T1 command; authoring; the full
workflow; containment.

**Optional systemd [not required]:**
- A transient `systemd-run --uid=ohk-bdw --property=… ohk-bdw-check` is a convenience, not a
  requirement. The basic requirement is:
  `cd / && timeout -k 3 60 prlimit --as=1073741824 --fsize=8388608 --core=0 -- runuser -u ohk-bdw -- env -i PATH=/usr/bin:/bin TMPDIR=<data_root>/tmp <R_REL>/bin/ohk-bdw-check --config …`.
  Rlimits are inherited across `runuser`; the `cd /` gives a cwd the account can reach.
- Per-account slice ceilings and lingering stay with the later containment slice.

**Historical gates:** the T1 qualification harness, launcher and gates are not touched, reused or
bypassed. Admission lives in the new module; demonstration and compatibility flags are unchanged.

## 6. Fresh-install validation (inert procedure) [PROP]

### 6.1 Environment (OL-2)

A **disposable Ubuntu Server 24.04 amd64 virtual machine**, with:
- a fresh ext4 root;
- no `git` package installed;
- no copy of the repository;
- no WSL;
- no network needed after the artifacts are transferred.

**Transferred:** the release tarball, its manifest digest, the installer, `release_manifest.py`
and a configuration template.

**Why not the WSL host:** a WSL-host isolated install could not show that the developer checkout
or Git are absent without changing the host. It is therefore **not** proposed as equivalent.

### 6.2 Steps and evidence

Every step's output goes to `<evidence-dir>/<step>.{out,err,rc}` on the VM, and the evidence is
copied back afterwards.

| # | Claim | Action (inert) | Minimal evidence | Pass |
|---|---|---|---|---|
| V0 | No checkout, no Git, fresh target | `command -v git`; `test ! -e /usr/bin/git`; `dpkg-query -W git`; `test ! -e /mnt/d`; record `/etc/os-release`, `uname -m` and the root fstype | rc and output | git absent, no checkout, noble, x86_64, ext4 |
| V1 | Install into a fresh location | `install_release.sh …` with `R_REL=/opt/ohk-bdw/releases/<id>` (path absent beforehand) | Installer output and install record | rc 0; `R_REL` exists; no `.partial` remains |
| V2 | Declared contents complete; package integrity | `release_manifest.py verify --root R_REL --expect-sha256 D` (run as root, read-only) | Verifier JSON | rc 0, with zero extra, missing or mismatched entries |
| V3 | Dependencies complete | Installer soname check; `ldd R_REL/python/bin/python3.13` shows no "not found" | Output | Every soname resolves |
| V4 | Bounded startup as the non-fixed-UID account | `cd / && timeout -k 3 60 prlimit --as=1073741824 --fsize=8388608 --core=0 -- runuser -u ohk-bdw -- env -i PATH=/usr/bin:/bin TMPDIR=/var/lib/ohk-bdw/tmp R_REL/bin/ohk-bdw-check --config /etc/ohk-bdw/deployment.json --evidence`; record `id -u ohk-bdw` and `prlimit` output | Receipt; rc; uid | rc 0. The receipt's commit equals the manifest commit, and its `nm`/`ct` digests equal the digests the build host recorded in the release notes (computed by running the same check in the build host's staging copy at `R_REL`). The uid is not 1000 by requirement; whatever was allocated is recorded |
| V5 | Release identity without Git | Covered by V4 (installed path), with `PATH` lacking git and V0 proving git is absent | V0 plus V4 | Both pass |
| V6 | Immutable release, writable state separated | As the account: `touch R_REL/app/x` and `touch R_REL/python/x` both fail with EACCES; `find R_REL -newer <install-record>` is empty; after V4, `find R_REL -name __pycache__ -path '*/app/*'` is empty; `find / -xdev -user ohk-bdw -newer <install-record> -not -path '/var/lib/ohk-bdw/*' -not -path '/proc/*'` is empty | Output | All hold |
| N1 | Root refused | V4 without `runuser` (euid 0) | Diagnostic | `RUNTIME_ACCOUNT_INVALID` (the first check, before the configuration is read), exit 5 |
| N2 | Invalid configuration refused | V4 with a copy of the configuration (root-owned, 0644) adding an unknown key | Diagnostic | `CONFIG_INVALID` |
| N3 | Non-ext4 data root refused | V4 with a configuration pointing at a tmpfs directory owned by the account (mounted in the VM) | Diagnostic | `FILESYSTEM_UNSUPPORTED` |
| V7 | Integrity re-check after the negatives | Repeat V2 | Verifier JSON | rc 0, so no mutation |

**Outcomes:**

| Outcome | Condition |
|---|---|
| PASS | Every V and N row passes and the evidence is complete |
| FAILED | Any row ran and contradicted its expectation, for example an unexpected refusal, a manifest mismatch or a writable release |
| INCOMPLETE | A row did not run, timed out, or left evidence missing. The VM could not be shown fresh (V0) is INCOMPLETE, not PASS |

There is no retry within an attempt. L1 cases, tampering cases and broad qualification are out of
scope: L1 has already accepted the divergence refusals.

### 6.3 Bounds (estimates labelled; nothing measured)

| Item | Bound | Type |
|---|---|---|
| Procedure wall time | At most 900 s overall: V1 ≤ 300 s, V2 and V7 ≤ 120 s each, V4 and N1–N3 ≤ 60 s each [est] | Enforceable with `timeout -k 3` per step and an outer `timeout -k 3 900` |
| Processes | Installer: one shell plus base tools, sequential, ≤ 32 TGIDs. Each startup check: one Python process, no children (it never runs git). Total ≤ 64 TGIDs [est] | Sampled only (no cgroup in L2); the startup check additionally records a `/proc` child scan |
| Startup check memory | RLIMIT_AS 1 GiB, RLIMIT_FSIZE 8 MiB, RLIMIT_CORE 0, set by the `prlimit --as --fsize --core` prefix in V4 and N1–N3 and inherited across `runuser` (rlimits are process attributes, not environment) | Enforceable per process |
| Release size | Interpreter, stdlib and dependencies at most 400 MiB [est; unmeasured] | Sampled (`du`) |
| Writable state | At most 16 MiB under `data_root`; each log at most 8 MiB | Sampled; `RLIMIT_FSIZE` enforces per file for the check |
| Cleanup | Discard the VM after copying out the evidence; nothing on the current host is changed | Procedural |

The L1 driver's limits are not inherited, and L1's 21 s says nothing about this target. The
startup check reads `app/` (about 2.8 MB) and the distribution files hashed by `nm.build` (size
unmeasured). The release size is unknown until a build exists.

## 7. Implementation proposal (files and interfaces) [PROP]

| File | Purpose | Interface |
|---|---|---|
| `applications/bounded_decision_workflow/deployment.py` (new, about 200 lines) | Configuration schema and platform admission (4.3, 4.6) | `load_config(path) -> Config`; `admit(config) -> Admission`; raises `WorkflowInputError` diagnostics |
| `applications/bounded_decision_workflow/release_check.py` (new, about 150 lines) | Startup check (5.2) | `main(argv) -> int`; receipt on stdout |
| `tools/release/release_manifest.py` (new, about 150 lines, stdlib only) | Create and verify RELEASE-MANIFEST | `create --root R_REL`; `verify --root R_REL --expect-sha256 D` |
| `tools/release/build_release.sh` (new; build host only) | Build the interpreter and wheels, apply the 3.7 gate, call `release_identity_record.py`, write the wrapper and manifest, make the tarball | `--commit C --release-root R_REL --cpython-tarball P --wheelhouse W --out DIR` |
| `tools/release/install_release.sh` (new; root, offline) | 4.5 | As shown in 4.5 |
| `tests/applications/bounded_decision_workflow/test_deployment.py`, `test_release_check.py`, `tests/tools/test_release_manifest.py` (new) | Unit tests with temporary directories; no root; account and fstype simulated through injected `pwd`/mountinfo readers | pytest |
| `docs/deployment/README.md` (new) | Operator runbook: install, check, the root `-B` rule, uninstall | — |

No existing file needs editing. `release_identity.py`, `measurement_build.py` and the L1 tool stay
unchanged.

**Disclosed inconsistency:** the L1 tool's docstring (`release_identity_record.py`) mentions a
"separately signed RELEASE-MANIFEST.json". Under OL-4 the L2 manifest is checksum-verified and
unsigned until ID-2 is decided. The docstring is left as it is, because editing it would change
L1-tested bytes. The runbook states the actual policy.

**Under OL-1(b):** the two new modules would move to `app/deploy/` (a new top directory, outside
L1's identity walk and covered by the manifest only), and the wrapper changes as in 3.5.

**Where the decisions stand:**

| Category | Items |
|---|---|
| Already accepted | ID-1; OD-K2; L1 acceptance |
| Resolved here (routine) | Manifest schema; refusal codes; layout; wrapper form; configuration keys and validation; the installer's extraction and rename sequence; `--no-compile`; the soname check; validation step evidence |
| Owner decisions | Section 8 |
| Later authority | The commit (OL-1), building on a reference host, provisioning the VM, transferring artifacts and executing the validation. Each needs its own grant |

## 8. Material owner decisions (short list)

- **OL-1, release input:** authorize the commit `C`, and choose placement of the L2 code:
  - **(a) recommended:** under `applications/`, so it is covered by the release identity, but L1
    and L2 tests must re-run on `C`;
  - **(b):** outside `applications/` and `backend/`, so the L1-tested set digest `e6c9f2a3…` can
    hold exactly, but the startup code is covered by the manifest only.
- **OL-2, fresh-install environment:** a disposable Ubuntu 24.04 amd64 VM without git
  (recommended), and who provisions it.
- **OL-3, interpreter:** accept PD-3 (a python.org 3.13.11 source build for the release prefix on
  a reference build host), plus PD-3b and the current lock including test dependencies (ID-4 kept).
- **OL-4, integrity:** accept checksum verification against an owner-designated digest channel
  for L2, with signatures deferred to ID-2. Also accept manifest verification at install and
  validation only, not at every startup.
- **OL-5, core handling:** accept `core_pattern_ack` as the L2 mechanism, while ID-7 (who may
  accept a pipe handler) stays open.
- **OL-6, containment:** confirm that L2 claims no containment, and that slice and cgroup
  ceilings move to a later workload slice.

## 9. Unresolved risks

- **Startup scope:** the S1–S7 and governed commands remain Git-only (5.1). The startup check
  says nothing about them.
- **Build effects:** the interpreter build and reproducibility, the release size, the
  `nm.build` hashing time on the target, and noble library effects are all **unmeasured**.
- **Root-level tampering:** a change outside `app/` and the distributions between manifest checks
  is undetected (3.8).
- **Provenance:** D-P and ID-2 are open, so the checksum gives integrity only.
- **systemd:** user-manager behaviour and swap accounting on noble remain unverified. They are not
  needed for L2.

## 10. Focused review

**Reviewer:** one focused, independent `code-reviewer` subagent in this session.

**Restrictions it worked under:** read-only; `grep`, `sed`, `cat` and `stat` reads; no Python,
imports, Git, tests, writes or review file.

**Scope:** whether the draft (33,588 B) suffices for one fresh-install startup slice, preserves
L1 semantics, avoids host-specific runtime dependencies and claims accurately.

### 10.1 Verified sound by the reviewer

- **L1 semantics:**
  - `build.ROOT` resolves to `R_REL/app`, and `install_root` equality is exact.
  - The record is generated only on the build host from a real commit, and section 3.7 is honest
    that no commit exists.
  - The bytecode, mode, symlink and `.git` rules are consistent with `release_identity.py`.
- **Installed-mode `measurement_build`:** the lock and `importlib.metadata` checks work against
  the shipped site-packages under `-I`.
- **Usable as designed:** `_current_build` and `ExecutableBuild` work standalone; `--enable-shared`
  with an rpath is sound; the 5.1 Git-only claim is correct.
- **Claims:** the section 1 attribution is accurate, and there is no containment, provenance or
  performance overclaim. Host-specific dependencies are each replaced or marked unresolved.

### 10.2 Findings and dispositions (all fixed in this file unless noted)

| Severity | Finding | Fix |
|---|---|---|
| **Major** | Symlinks report mode 0777, so the writability rules would refuse every release (manifest 3.4, `RELEASE_TREE_UNSAFE` 4.6) | **Fixed.** Symlinks are excluded from mode and writability checks; they must be root-owned with targets inside `R_REL` |
| Minor | N3 expected `FILESYSTEM_UNSUPPORTED`, but the config order would emit `CONFIG_INVALID` | **Fixed.** Explicit order and codes in 4.3; non-ext4 gives `FILESYSTEM_UNSUPPORTED` |
| Minor | The euid-0 refusal code and position were ambiguous | **Fixed.** It is the first check, `RUNTIME_ACCOUNT_INVALID` |
| Minor | The rlimits were claimed but never applied | **Fixed.** `prlimit --as --fsize --core` added to the V4/N commands and 5.2 |
| Minor | `mv` onto an existing directory moves into it | **Fixed.** `mv -T -n`, then a result check |
| Minor | OL-1(b) contradicted the wrapper and L1's refusal of extra files | **Fixed.** Under (b), use an `app/deploy/` top directory and an adjusted wrapper (3.5, 7) |
| Minor | Deleting RECORD-listed residue breaks `measurement_build` | **Fixed.** pip runs as a zipapp; RECORD-listed files are never deleted; the builder refuses a non-locked distribution or `direct_url.json` |
| Minor | `retention._filesystem` also accepts xfs | **Fixed.** `deployment.py` applies an ext4-only comparison, and a test covers xfs refusal |
| Low | Double identity computation and unmapped exceptions | **Fixed.** A single `_current_build` call; all failures give `BUILD_IDENTITY_UNAVAILABLE` |
| Low | `runuser` cwd | **Fixed.** `cd /` |
| Low | V4 checked only that digests were present | **Fixed.** Compared with the build-host recorded digests |
| Low | V6 had no evidence command for "writes only under `data_root`" | **Fixed.** A `find -user … -newer …` command |
| Low | `R_REL` character set and symlink components | **Fixed** (3.5) |
| Low | L1 tool docstring mentions a signed manifest | **Disclosed** (7); not edited |
| Low | `stat -f` cannot identify ext4 | **Fixed.** `findmnt -o FSTYPE` |

### 10.3 Not verified, by reviewer or author

- Build feasibility, release size and `nm.build` hashing time.
- Default Ubuntu `core_pattern`/apport behaviour against `core_pattern_ack`.
- Whether every committed path fits L1's `PART` character set.

**Re-review status:** the fixes after review were not re-reviewed. They are text corrections
following the reviewer's stated minimal fixes, but **this final text has not been independently
re-read.** That is disclosed as a limitation.

## 11. Preparation accounting

### 11.1 Authority

The owner instruction of 2026-10-22 authorized a scoped L1 acceptance record and L2 design
preparation only.

### 11.2 Charge for this file

| Item | Grant | Notes |
|---|---|---|
| Files | 1 | This file only |
| Directories | 0 | |
| Logical bytes | At most 131,072 | Charged against the unreserved preparation-byte balance |
| Allocated bytes | At most 147,456 | Same balance |

- **Balance before:** 12,883,110 logical / 27,533,312 allocated, after the finalization
  addendum's partition. That is the governing arithmetic chain, from 13,276,326 / 27,975,680 in
  the L1 ACCOUNTING (`647f64a7…`), less three 131,072 / 147,456 partitions.
- **Balance after this partition:** **12,752,038 / 27,385,856**.
- **Final size and SHA-256:** reported in chat after the readback, so this file contains no
  self-hash.

**How it was written:** exclusive creation (`O_CREAT | O_EXCL | O_NOFOLLOW`) by a standalone
writer reading stdin, after the path was confirmed absent. Later edits were made only inside this
unsealed file.

**Not used or not created:**
- Not used: held reservations and spent validation reservations.
- Not created: no script, scratch, manifest or review file, and no memory note.

### 11.3 Actions in this task

| Kind | What was done |
|---|---|
| Read-only | Hashing of the five attempt-3 records; reads of the vertical-slice proposal and the maintained sources named in section 5; plain JSON parsing of the attempt-3 journal to derive the tested source-set digest |
| Not done | No test, import, compilation, syntax check, interpreter probe, build, install, service activation, Git, K, commit or merge |

### 11.4 Host and session scope

These are separate, not charged here, and not zero: the session transcript, the reviewer pass
(about 232k tokens, about 141 s) and harness files.

END PROPOSAL
