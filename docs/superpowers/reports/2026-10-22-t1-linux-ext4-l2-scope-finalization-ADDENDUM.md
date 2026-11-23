# T1 Linux/ext4 L2: scope finalization (preparation addendum)

Date 2026-10-22. Branch `claude/t1-startup-chain-repair`. Preparation only.

- Nothing in this file was implemented, executed, tested, built, provisioned or committed. No Git,
  repository code, interpreter or probe was run.
- It supplements `docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md`
  (`74a39d87586b50e91fb5862579f28c02f86c498a6fa69e02bfb97e487d059a1b`, verified), which stays
  unchanged.
- Where this addendum differs from that proposal, **this addendum governs the L2 slice**. Every
  difference is listed in section 9.

Labels: **[ACC]** accepted; **[SRC]** from reading the cited source; **[REC]** recommended and
resolved here; **[EXT]** external fact still to verify; **[est]**; **[unmeasured]**.

## 1. Initialization boundary, traced from source

### 1.1 What the maintained code does [SRC]

**Process entry.** `python -m applications.bounded_decision_workflow` runs `__main__.py`, which
calls `cli.main` (`cli.py:254`). `cli.main` routes on the first argument's prefix:
- `t1-` → `t1_cli.main`;
- `reassessment-` → `reassessment_cli.main`;
- `checked-` → `checked_cli.main`;
- `measurement-` → `measurement_cli.main`;
- anything else goes to the legacy S1–S7 workflow (`cli._arguments` and `execute`).

**Import-time initialization.** These checks run when a command family is imported:
- `checked_contracts._load_schemas()` (`checked_contracts.py:95–103`) reads
  `checked_temperature_schemas.json` and refuses unless its SHA-256 equals `SCHEMAS_SHA256`
  `43c2af0b…`. It also fixes `POLICY_EDITION` and `POLICY_EDITION_SHA256`. It is imported by
  `checked_runtime`, and therefore by the checked, T1 and reassessment families.
- `t1_contracts.py:68–71` reads `t1_companion_schemas.json` and refuses with
  `SIM_EDITION_NOT_PERMITTED` unless its digest equals `e6fef4ad…`.
- Importing the package `applications.bounded_decision_workflow` (`__init__`) imports the S-series
  modules. None of them runs Git at import (checked by grep for `subprocess` across
  `applications/`). The review's grep for module-level `read_bytes` and `open` found only the two
  pinned schema reads above. `governed_closure.SCHEMA_PATH` is a path constant and is not read at
  import.

**Per-command initialization.** This happens before any request input is read:

| Family | Steps |
|---|---|
| checked (`checked_cli.main`, `checked_cli.py:184`) | Constructs `checked_runtime.ExecutableBuild()`, then parses arguments. `build_wire = _current_build(build)` is the first step of the selection and reassessment bundle paths (`checked_runtime.py:793, 916`). Verify reads and checks the bundle first and acquires the build afterwards (`checked_runtime.py:994–996`). It calls `ExecutableBuild.wire()`, which calls `measurement_build.identity()` (`checked_runtime.py:45–66`). `_current_build` then parses the wire and **validates it against the integrity-checked `ct.build.v1` schema** (`checked_runtime.py:62–66`). Output goes through `checked_cli.publish` (create new, `O_EXCL`, fsync) |
| T1 (`t1_cli.execute`) | `t1_package.safe_new_dir` admits the output directory *before* the build is used: no `..`, no symlink component, absent, parent exists (`t1_package.py:12–22`; `t1_cli.py:72, 86`). The same `ExecutableBuild` provider is used later |
| measurement and reassessment | `measurement_build.identity()` is called inside operations (`measurement_runtime._build_check`, `reassessment_build.identity`) |

**Where Git is used:**
- `measurement_build.identity()` uses Git only when `release_identity.present(build.ROOT)` is
  false (`measurement_build.py:19–37`). In an installed release, L1's
  `release_identity.verified_source` supplies the checkpoint and file list without Git. That is
  how installed L1 identity enters the maintained path.
- `build.identity()` (legacy S1–S7, `build.py:23–57`) and `governed_build.identity()`
  (`governed_build.py:30`) are **Git-only**. Installed, they refuse.

### 1.2 Finding

**There is no coherent, command-independent initialization boundary.** Initialization is spread
across:
- import-time contract loading;
- argument parsing;
- the first step of each operation, which acquires the build;
- output admission, which differs per family.

No existing command initializes without also requiring operation inputs: pins, a request, a
bundle or objects.

### 1.3 Selected L2 initialization check [REC]

**Implementation:** a thin adapter, `applications/bounded_decision_workflow/release_check.py`.
It calls only maintained behaviour and **stops before reading any operation input**.

**Order:** its order is its own, not that of any single command. The checked selection and
reassessment paths acquire the build first, while T1 admits output first. The adapter does
deployment admission, then the imports, then the build, then output admission.

1. **Deployment admission:** `deployment.admit(config)`, with the checks of section 3.
2. **Dispatcher-equivalent imports.** It imports `checked_cli`, `t1_cli`, `measurement_cli` and
   `reassessment_cli` exactly as `cli.main` would. This executes the pinned-schema integrity
   loads of `checked_contracts` and `t1_contracts`. A digest mismatch surfaces as their existing
   refusals.
3. **Build acquisition:** `build = checked_runtime.ExecutableBuild()`, then
   `wire = checked_runtime._current_build(build)`, which is the first step of the checked
   selection and reassessment bundle paths. That covers installed L1 verification, `nm.build.v1` and `ct.build.v1` assembly,
   and validation against the loaded `ct.build.v1` schema.
4. **Output admission** through the maintained T1 output path:
   - `t1_package.safe_new_dir(<data_root>/evidence/<run-id>)`;
   - `mkdir` with mode 0700;
   - the maintained filesystem label, `checked_cli.filesystem_of` (`checked_cli.py:97`),
     recorded in the receipt;
   - then one receipt written with `O_CREAT | O_EXCL | O_NOFOLLOW`, fsync of the file and the
     directory (the same discipline as `checked_cli.publish`).
5. **Receipt** `ohk-bdw.startup-receipt.v1` on stdout and in the evidence directory, exit 0. It
   holds:
   - `release_root`, commit, and `sha256(wire)` for `ct`;
   - `sha256` of the embedded `nm` fields: `checkpoint`, `source_manifest`,
     `environment_manifest`;
   - `SCHEMAS_SHA256` for checked and T1 as loaded;
   - the evidence directory, filesystem label, euid and account name;
   - the process's `/proc/self/limits` text, recorded only;
   - `core_pattern` as observed (record only; section 3.2) and UTC timestamps.

**Exact claim:** in an installed release, the maintained command families initialize through
build-identity acquisition and output admission. That means:
- the pinned contract and schema files load and pass their digest checks;
- the installed L1 witness yields the checkpoint and exact source tree without Git;
- the maintained `ct.build.v1` record assembles and validates against its schema;
- a fresh output directory on the admitted data root passes the maintained output admission and
  receives a durable record.

**Not claimed:** request or bundle admission, evaluation, verification, replay, T1 simulation,
authoring, any complete workflow, the S1–S7 or governed commands (which are Git-only), or
containment. Computing identities alone is *not* the claim; the claim is the maintained
initialization sequence above.

**Failure behaviour:**
- Admission refusals: the `ct.diagnostic.v1` shape on stderr, exit 5. Codes are in section 3.
- Schema digest refusals: the existing `CheckedRefusal`/T1 codes.
- Build failures: `BUILD_IDENTITY_UNAVAILABLE`, stage 5, exit 3 (existing).
- Output admission: `SIM_OUTPUT_UNSAFE`, exit 5 (existing).
- Any other exception: `INTERNAL_ERROR`, exit 7.
- Partial output is never deleted.

**Side effects:** exactly one new directory, `<data_root>/evidence/<run-id>`, holding one file,
`startup-receipt.json`.
- Nothing is written under the release. `-B`, root ownership and L1 refusing `__pycache__` all
  guard this.
- Nothing is written to `TMPDIR`, which equals `<data_root>/tmp` and is unused by this path.
- Nothing is written elsewhere.

**`<run-id>`:** `startup-<UTC yyyymmddthhmmssz>-<pid>`, all lowercase (for example
`startup-20261022t164121z-4242`). It matches the adapter's own rule, `[a-z0-9][a-z0-9._-]{0,127}`;
`safe_new_dir` has no name rule.

### 1.4 Interfaces

| Function | Signature | Contract |
|---|---|---|
| `deployment.load_config` | `(path: str) -> Config` | `Config` is a frozen dataclass: `release_root`, `runtime_account`, `data_root`. It raises a `CheckedRefusal`-compatible error |
| `deployment.admit` | `(config: Config) -> dict` | Runs the 3.1 checks in order. Returns an admission record (account, uid, fstype, mount options, `core_pattern` observed) |
| `release_check.main` | `(argv: list[str] \| None = None) -> int` | argv is exactly `['--config', PATH]`. Writes nothing outside 1.3; exit codes as above |

No new command is added to `cli.main`. The wrapper (proposal 3.5) calls `release_check.main`, so
the existing dispatch table and its pinned behaviour stay unchanged.

## 2. Interpreter and installation [REC]

### 2.1 Interpreter

**Choice:** CPython **3.13.11**, built from the python.org source tarball `Python-3.13.11.tar.xz`
on a reference Ubuntu Server 24.04 amd64 build machine, for the release prefix.

**Why 3.13.11:**
- It is the only version observed with the lock.
- The code requires 3.13.x (`measurement_build.py:20`, `build.py`).
- A patch-release change means a new release and environment identity, never a relabel.

**Source identity policy:**
- The tarball's SHA-256 is recorded in the release notes.
- It must equal the digest published on python.org for 3.13.11 **[EXT: obtain and verify; not
  present in local records]**.
- **Integrity versus provenance:** a matching digest establishes integrity relative to that
  publication. Verifying python.org's release signature (Sigstore or GPG, per python.org policy)
  would be a provenance step. That is **[EXT: which signatures 3.13.11 carries]**, and it is
  outside L2. D-P stays open.

**Construction, recorded so a rebuild is comparable** (bit-for-bit reproducibility is **not
claimed** [unmeasured]):

```text
export SOURCE_DATE_EPOCH=<tarball mtime>   LC_ALL=C   TZ=UTC
./configure --prefix=R_REL/python --enable-shared --with-ensurepip=no --without-static-libpython \
            LDFLAGS=-Wl,-rpath,R_REL/python/lib
make -j"$(nproc)" && make install
```

- PGO and LTO are omitted (`--enable-optimizations` is not used). That gives less
  nondeterminism, at some speed cost.
- The `dpkg-query -W` package list of the build machine is retained as build evidence.

**Build packages on the reference host [EXT: confirm noble names]:**
`build-essential`, `pkg-config`, `libssl-dev`, `libffi-dev`, `zlib1g-dev`, `libbz2-dev`,
`liblzma-dev`, `libsqlite3-dev`, `libreadline-dev`, `uuid-dev`, `libncurses-dev`, `libgdbm-dev`.

**Optional modules not needed** by the application (for example `_tkinter`) may be absent. The
build log records which modules were skipped, and the manifest is authoritative.

### 2.2 Locked dependencies

- **Source of truth:** `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt`
  (`6bcc7bd80022ce38d984ada0b4e4d4986272befea760ae895c76a8c6f3937fcf`, verified). It holds ten
  pinned distributions with SHA-256 hashes, including `pydantic-core==2.46.4`.
- **Installed-name check:** names and versions must equal `requirements.lock` (`7c87f0d7…`),
  because `measurement_build` checks the version of every locked name.
- **Wheels:** collected into a wheelhouse **[EXT: obtain the exact wheel files matching the
  pinned hashes, for cp313 manylinux x86_64 where binary]**. They are installed into
  `R_REL/python` with:

  ```text
  R_REL/python/bin/python3.13 pip.pyz install --no-index --find-links wheelhouse --require-hashes \
      --only-binary=:all: --no-compile -r requirements-hashed.txt
  ```

- **`pip.pyz`:** a build-only zipapp, never installed into the prefix. Its version and digest
  are recorded **[EXT: choose and verify a pip zipapp compatible with Python 3.13]**.
- **The builder refuses** any non-locked distribution, any `direct_url.json`, or the deletion of
  any RECORD-listed file.
- **Test dependencies:** pytest and its dependencies stay in the runtime environment because the
  lock includes them. ID-4 is not reopened.

### 2.3 Offline package, prefix and relocation

- **Offline:** the tarball is built on the reference host and installed offline. The target needs
  no compiler, network, Git or package installation, only the noble runtime libraries
  (`required_sonames`, checked with `ldconfig -p`).
- **Expected runtime packages [EXT: confirm on noble; the t64 renames apply]:** `libssl3t64`,
  `libffi8`, `zlib1g`, `libsqlite3-0`, `libbz2-1.0`, `liblzma5`, `libreadline8t64`, `libuuid1`,
  `libncursesw6`, `libgdbm6t64`.
- **Prefix:** a build parameter. Each prefix is its own release, and installing elsewhere is
  refused by L1's `install_root`. The rpath, console-script shebangs and `sysconfig` all embed the
  prefix. Relocation is unsupported.
- **No personal paths:** the release contains no miniconda, no `/home/...`, no `/mnt/d/...`, no
  WSL venv and no checkout.
- **Builder self-check [REC]:** the build refuses if any release file contains the byte strings
  `/home/` or `/mnt/` (a grep over the staged tree, excluding the manifest), or if
  `sys.prefix != R_REL/python` in the staged interpreter's `sysconfig` data file. That staged
  check needs execution authority on the build host, which is later.

### 2.4 Locations and account (unchanged from the proposal; restated)

| Location | Rule |
|---|---|
| Release | Immutable, root-owned |
| Configuration | `/etc/ohk-bdw/deployment.json`, root 0644, path via `--config` |
| Writable state | `data_root`, ext4, runtime account, 0700 |

The runtime account is created by `adduser --system`, with no fixed UID.

## 3. Proportional platform admission

### 3.1 Checks kept, with the property each protects

Checks run in this order, each with its own code; all exit 5.

| # | Check | Property protected | Why the L2 slice needs it |
|---|---|---|---|
| A1 | euid ≠ 0 (`RUNTIME_ACCOUNT_INVALID`) | Release immutability under the runtime identity. Root would also write `__pycache__` without `-B` | The slice claims to run as the unprivileged account, and that writes go only to the data root |
| A2 | Linux, x86_64, CPython 3.13.11 (`PLATFORM_UNSUPPORTED`) | Clear early diagnosis. `measurement_build` also refuses non-3.13, and the wheels are x86_64 | Cheap; turns a late identity failure into an explicit platform refusal |
| A3 | Configuration file and keys valid (`CONFIG_INVALID`) | Paths come from administrator configuration, not the environment | The slice uses `release_root` and `data_root` |
| A4 | euid equals the configured account's uid (`RUNTIME_ACCOUNT_INVALID`) | The intended account, not merely "not root" | Same as A1 |
| A5 | `release_root` equals the running release, with no symlink component (`CONFIG_INVALID`) | L1's `install_root` equality; no confusion between releases | Without it, a mismatch surfaces only as a generic identity refusal |
| A6 | `data_root` is ext4 (`FILESYSTEM_UNSUPPORTED`), owned by the euid with mode 0700 (`CONFIG_INVALID`), and `TMPDIR` equals `<data_root>/tmp` | Writable-state separation on the declared target filesystem | The output-admission step writes there. The maintained retention accepts ext4 or xfs; ext4-only is the declared target |
| A7 | No release file or directory is writable by the euid; symlinks are root-owned with targets inside (`RELEASE_TREE_UNSAFE`) | Immutability of the parts L1 does not cover (`python/`) | The slice claims an immutable release. L1 covers only `app/` |

### 3.2 `core_pattern` acknowledgement: removed from L2 admission

**Origin:**
- **The maintained, pinned T1 launcher.** `tools/launch/t1_startup.sh::core_policy()`, under its
  v1 profile, strictly refuses pipe handlers. It is a maintained control for T1 qualification
  runs. It stays unchanged and in force for those runs, but it does not apply to the L2 startup
  check, which is not a T1 launch.
- **The earlier vertical-slice proposal**, sections 2.6 and 2.7, and ID-7. Both are **proposals,
  never accepted**.
- No accepted owner decision makes it an L2 initialization requirement.

**Is it needed for initialization?** No. Initialization involves no crash, and nothing in the
1.3 path reads or depends on `core_pattern`.

**Retained safety concern:** core dumps of a process holding evidence could be captured by an
unreviewed handler. That is relevant to long-running qualification workloads, not to one bounded
initialization check.

**Recommendation [REC]:**
- Do not refuse on `core_pattern` in L2.
- The receipt records the observed value.
- The runbook documents the concern.
- The acknowledgement mechanism (and ID-7) belongs to a later qualification or workload scope.
- The validation sets RLIMIT_CORE 0 for the check process, which suppresses non-pipe cores only.
  It is not a containment claim.

**Owner disposition:** none is required to waive an accepted requirement, because none existed.
This addendum only withdraws the earlier L2 proposal's own `core_pattern_ack` field and
`CORE_HANDLER_UNACKNOWLEDGED` code (section 9). ID-7 stays open, and the historical T1 launcher
check stays unchanged.

### 3.3 Limited claim

L2 establishes **no containment**. The validation's per-process limits (prlimit AS, FSIZE and
CORE) and `timeout` bound only the check process. They prove nothing about workload isolation,
cgroup ceilings or other processes. Slice and cgroup containment belong to a later workload scope.

## 4. Disposable validation VM

### 4.1 Image and identity

- **Image:** Ubuntu Server 24.04 LTS amd64, the official cloud image or ISO **[EXT: exact image
  build or serial and its published SHA-256]**.
- **Verification:** the provisioner verifies the image's SHA-256 against Ubuntu's published
  `SHA256SUMS` (signature verification of `SHA256SUMS` is optional and provenance-level). The VM
  records `/etc/os-release`, `uname -r -m` and the root `findmnt` row.
- **Minimum sizing [est]:** 2 vCPU, 2 GiB RAM, a 20 GiB ext4 root disk, no swap requirement, and
  network only for transferring artifacts.
- **No git package:** `ubuntu-server` images may include git **[EXT: check]**. If they do, the
  provisioner purges it before the artifacts arrive, and the purge is recorded.

### 4.2 Responsibilities

| Role | Provides |
|---|---|
| Provisioner (later authority) | VM, image verification, git absence, artifact transfer, and the operator account with sudo |
| Artifacts | Release tarball, its manifest digest (out-of-band), `install_release.sh`, `release_manifest.py`, configuration template, the expected `ct` and `nm` digests from build-host staging (5.4), and a validation script (inert text, created under the later grant) |

**Privileges:**
- **Install** uses root (`sudo`): installer and manifest verifier.
- **Runtime** uses `runuser -u ohk-bdw` only.
- The runtime account never gets sudo.

### 4.3 Steps (a refinement of proposal 6.2)

| # | Check | Evidence | Pass |
|---|---|---|---|
| V0 | Git and checkout absent: `command -v git` fails; `dpkg-query -W git` reports not installed; no `/usr/bin/git`; no `/mnt/d`; `find / -xdev -name .git -type d` is empty | rc and output | All absent |
| V1 | Fresh install: `R_REL`, `/etc/ohk-bdw` and `/var/lib/ohk-bdw` absent beforehand; installer rc 0 | Installer output, install record | rc 0; no `.partial` remains |
| V2 | Manifest verify (root, read-only) | Verifier JSON | rc 0; zero differences |
| V3 | Sonames resolve (installer check, plus `ldd` showing no "not found") | Output | All resolve |
| V4 | One initialization check (1.3) as the account: `cd / && timeout -k 3 60 runuser -u ohk-bdw -- prlimit --as=1073741824 --fsize=8388608 --core=0 -- env -i PATH=/usr/bin:/bin TMPDIR=/var/lib/ohk-bdw/tmp R_REL/bin/ohk-bdw-check --config /etc/ohk-bdw/deployment.json`. `prlimit` sits inside `runuser`, so `pam_limits` cannot reset it, and the receipt records the process's `/proc/self/limits` | Receipt (stdout and file), rc, `id -u ohk-bdw` | rc 0; `ct` and `nm` digests equal the build-host staging values; both schema digests match; the receipt file exists only under `data_root/evidence/` |
| V5 | Immutability and state separation: as the account, `touch` under `R_REL/app` and `R_REL/python` fails with EACCES; no `__pycache__` under `R_REL/app`; `find / -xdev -user ohk-bdw -newer <install-record> -not -path '/var/lib/ohk-bdw/*' -not -path '/proc/*'` is empty | Output | All hold |
| N1 | euid 0 | Diagnostic | `RUNTIME_ACCOUNT_INVALID`, exit 5 |
| N2 | A configuration with an unknown key (in a separate root-owned 0644 file) | Diagnostic | `CONFIG_INVALID`, exit 5 |
| N3 | A data root on tmpfs (owned by the account, 0700) | Diagnostic | `FILESYSTEM_UNSUPPORTED`, exit 5 |
| V6 | Manifest re-verify after the negatives | Verifier JSON | rc 0 |

**Outcomes:**

| Outcome | Condition |
|---|---|
| PASS | All rows pass, with complete evidence |
| FAILED | A row ran and contradicted its expectation |
| INCOMPLETE | A row did not run, timed out, or its evidence is missing; or V0 could not be shown |

There is no retry.

**Bounds** (estimates, labelled; nothing measured):

| Item | Bound | Type |
|---|---|---|
| Wall time | Per-step `timeout -k 3`: V1 300 s, V2 and V6 120 s each, V4 and N1–N3 60 s each, others 30 s; outer 900 s | Enforceable |
| Processes | At most 64 TGIDs | Sampled only |
| Check process limits | AS 1 GiB, FSIZE 8 MiB, CORE 0 | Enforced, per process |
| Release size | At most 400 MiB [est; unmeasured] | Sampled |
| Data root | At most 16 MiB written | Sampled |
| Evidence | At most 32 MiB in total | Sampled |
| Cleanup | Copy the evidence out, then destroy the VM. The current host is untouched | Procedural |

## 5. Source identity and release checkpoint

### 5.1 Implementation scope

| File | Change |
|---|---|
| `applications/bounded_decision_workflow/deployment.py` | New, about 200 lines |
| `applications/bounded_decision_workflow/release_check.py` | New, about 150 lines |
| `tools/release/release_manifest.py` | New, stdlib only |
| `tools/release/build_release.sh` | New; build host only |
| `tools/release/install_release.sh` | New; root, offline |
| `tests/applications/bounded_decision_workflow/test_deployment.py` | New |
| `tests/applications/bounded_decision_workflow/test_release_check.py` | New |
| `tests/tools/test_release_manifest.py` | New |
| `docs/deployment/README.md` | New (runbook) |

**Existing-file edits: none.** `release_identity.py`, `measurement_build.py`, the L1 tool, the
dispatcher and all historical gates stay unchanged. The proposal's OL-1 option (a), placing the
two modules under `applications/`, is adopted [REC]. It keeps the initialization code inside the
L1 identity witness.

### 5.2 Effect on L1 identity and attribution

- **New source set:** adding two files under `applications/` changes the source manifest and
  `ls-files`, so the source-set digest is no longer `e6c9f2a3…`.
- **L1 acceptance:** it stays tied to its tested bytes and environment. It does **not** cover the
  changed tree.
- **L1 tests to re-run: all 20 in `test_release_identity.py`.**
  - The `matched` fixture copies the *entire* `applications/` and `backend/` trees. Its three
    production-boundary cases assert installed-mode equals Git-mode `nm`/`ct` over that tree, so
    they must be re-established for the new bytes.
  - The other 17 depend on `release_identity.py` (unchanged) but run in the same file and cost
    seconds, so re-running the whole file avoids partial attribution.
- **Other existing tests:**
  - Git-mode tests that require a clean committed tree (for example
    `test_governed_build.py:24`, `test_s7_release.py:48`, `checked_temperature/test_real_build_success.py`)
    already refuse while the working tree is dirty, as they have since L1 under OD-K2.
  - They are not part of the L2 claim. They belong to the later commit and regression authority,
    and are not re-run here.

### 5.3 New L2 tests (pytest; tmp dirs; no root; no network)

**`test_deployment.py`:**
- the full A1–A7 refusal order and codes, with injected `pwd`, uid, mountinfo and `core_pattern`
  readers;
- configuration validation edges: an unknown key, a non-root owner, group write, symlinked
  paths, a relative path, `release_root` mismatch, xfs refused, tmpfs refused;
- A7 ignores symlink modes but refuses an out-of-tree target.

**`test_release_check.py`:**
- **Positive:** a `matched`-style installed copy (reusing L1's fixture pattern: a committed
  fixture tree, `release_identity_record.py`, `PATH` without git) with a temporary data root runs
  `release_check.main`. It asserts:
  - the receipt fields: `ct`/`nm` digests equal a Git-mode computation on the same fixture, and
    the schema digests;
  - exactly one new directory and file are created;
  - no write occurs under the installed copy.
- **Negatives:** an existing evidence directory gives `SIM_OUTPUT_UNSAFE`; a tampered
  `checked_temperature_schemas.json` in the copy gives the existing schema refusal (L1 identity
  refuses first, and the test asserts whichever code the order yields, documented).

**`test_release_manifest.py`:**
- create and verify round-trip;
- refusals: an extra file, a missing file, a changed byte, a changed mode, a symlink target
  escaping the tree, group write on a file;
- symlink modes are ignored.

### 5.4 Sequence: reviewed bytes, tests, release commit, package

1. **Implement** in the working tree (later grant). Code review.
2. **Development test run** (later grant). One pytest invocation of the 20 L1 tests and the three
   L2 test files, in the approved development environment. Record:
   - `D_dev`, the source-set digest by the 1.3 rule of the proposal (sorted `[path, sha256,
     bytes]` over the non-`__pycache__` files of `applications/` and `backend/`);
   - the SHA-256 of each `tools/release/*` file.
3. **Release commit `C`** (later explicit commit authority, not a prerequisite for implementation).
4. **Build-host staging** (later grant):
   1. export `C` with `git -c tar.umask=022 archive C applications backend tools/release`, on the
      build host only. The default `tar.umask` of 0002 would yield group-writable entries, which
      the manifest refuses. Owner-exec stays as Git records it;
   2. require `D(C export) == D_dev`, and equal `tools/release` hashes;
   3. build the release from `C` at `R_REL` (section 2), and **create the manifest now**;
   4. run the same 20 L1 tests and the L2 tests against an export of `C`, using a **separate copy
      of the staged interpreter** (`cp -a R_REL/python` into a scratch prefix). Tests write
      bytecode (wheels were installed `--no-compile`, and the bytecode case's child runs without
      `-B`), so they must never touch the packaged prefix. Re-verify the manifest after the tests.
      Byte-identical copies give matched-environment attribution for the release environment's
      executable and distributions;
   5. run `release_check` in staging against the packaged `R_REL`, as a non-root account with
      `-B`, to record the expected `ct` and `nm` digests, then re-verify the manifest.
5. **Package:** the manifest records `commit = C`, `source_set = D_dev`, and the release-notes
   digests. The manifest digest is published through the owner-designated channel.
6. **VM validation** (section 4).

**Equivalence checks that tie the final package to the validated bytes:**

| Check | Ties |
|---|---|
| (i) `D(C export) == D_dev` | Committed bytes to tested working-tree bytes |
| (ii) L1 `verified_source` at V4 recomputes `C`'s Git object chain from the installed `app/` | Installed tree to `C` |
| (iii) Manifest `app/` entries equal `C` export file hashes (builder check) | Package to `C` |
| (iv) VM `ct`/`nm` digests equal the staging digests from step 4.5 | Same source, same `python3.13` executable bytes and same locked distribution files in staging and on the VM, for this prefix. libpython and the stdlib are covered only by the manifest (ID-3) |
| (v) Manifest digest equals the out-of-band digest | Delivered package to the published one |

None of these is provenance. D-P stays open.

### 5.5 Integrity, not signing [REC]

- **For engineering validation:** checksum verification only. The trust claim is "the installed
  bytes equal those whose digest was delivered through the owner-designated channel".
- **What it does not authenticate:** the builder, the build host or the source origin.
- **Signing:** stays deferred to ID-2. No keys are established, and this is not distribution
  readiness.

## 6. Read-back of the fixes made after the first review (proposal `74a39d87…`)

Each fix is confirmed present in the proposal text:

| Fix | Where |
|---|---|
| Symlink modes are excluded from writability checks, and symlink owner and target are checked | 3.4, 4.6 |
| Explicit refusal order with euid 0 first | 4.3 |
| prlimit in V4 and N1–N3; rlimits are process attributes | 5.2, 6.2, 6.3 |
| `mv -T -n` plus a result check | 4.5 step 6 |
| pip as a zipapp; RECORD files never deleted | 4.4 |
| ext4-only comparison, with an xfs refusal test | 4.3 item 5 |
| OL-1(b) moves to `app/deploy/` | 3.5, 7 |

This addendum carries them forward. A3/A6 add `TMPDIR`, and A7 is the symlink-aware walk.

## 7. Focused review

**Reviewer:** one focused, independent `code-reviewer` subagent, the same one that reviewed the
proposal.

**Restrictions it worked under:** read-only; `grep`, `sed` and `cat`; no Python, imports, Git,
tests or writes; no review file.

**Final text reviewed:** yes, the draft as written (29,887 B).

### 7.1 Confirmed sound

- **Source trace:**
  - the `cli.main` dispatch;
  - both import-time schema checks;
  - `ExecutableBuild` constructed before argument parsing;
  - `_current_build` validating `ct.build.v1`;
  - `ExecutableBuild` mapping identity errors to `BUILD_IDENTITY_UNAVAILABLE`;
  - `safe_new_dir`;
  - the Git-only `build` and `governed_build`;
  - importing the four CLIs only reads the two pinned schema files, with no writes and no Git.
- **Adapter:** it calls only maintained functions, stops before inputs, and its claim is narrow.
- **Admission:** A1–A7 are each justified.
- **`core_pattern`:** no accepted decision makes it an L2 requirement, and nothing accepted is
  waived.
- **Sequencing:**
  - re-running all 20 L1 tests is justified;
  - leaving the Git-mode clean-tree tests out of the L2 claim is honest;
  - checks (i)–(iii) and (v) are correct, and none claims provenance.
- **Interfaces:** the V4 digests are compared with staging at the same prefix; the receipt fields
  are all available.
- **Section 6 read-back:** all seven prior fixes are present in the proposal at the cited
  sections.

### 7.2 Findings and dispositions (all fixed in this file)

| Severity | Finding | Fix |
|---|---|---|
| Minor | "First step in every checked path" was false for verify; the T1 order was misstated (output admission comes before the build) | **Fixed.** Only selection and reassessment acquire the build first; the adapter's order is declared its own |
| Minor | The run-id with uppercase `T`/`Z` failed its own lowercase pattern | **Fixed.** Lowercase run-id |
| Minor | Tests under the release interpreter would write `.pyc` files into the packaged prefix | **Fixed.** Tests run on a separate interpreter copy; manifest created before and re-verified after |
| Minor | `git archive` defaults to umask 0002, giving group-writable modes | **Fixed.** `-c tar.umask=022` |
| Low | Weak evidence for "no file I/O at import" | **Fixed.** The module-level read grep is cited |
| Low | The T1 launcher is maintained and pinned, not merely historical | **Fixed** (3.2) |
| Low | `pam_limits` could reset `prlimit` | **Fixed.** `prlimit` moved inside `runuser`; limits recorded |
| Low | Check (iv) said "same interpreter" | **Fixed.** Executable bytes and distributions only; libpython and stdlib are manifest-only (ID-3) |

### 7.3 Re-review and verification status

- **Re-review:** these fixes were applied after the review and were **not re-reviewed**. They
  follow the reviewer's stated minimal fixes.
- **Not verified:** the [EXT] items; apport behaviour on noble; the exit class `refuse()` assigns
  to `BUILD_IDENTITY_UNAVAILABLE` (section 1.3 states exit 3 from the earlier correction record).

## 8. Implementation decision table

| Category | Items |
|---|---|
| Already accepted [ACC] | ID-1; OD-K2; scoped L1 acceptance tied to its bytes and environment; D-P open; R1 attribution; historical T1 gates unchanged; L2 claims no containment |
| Resolved here [REC] | Initialization adapter and claim (1.3, 1.4); OL-1(a) placement; CPython 3.13.11 source build, configure flags, no PGO; wheel install by hash with a zipapp pip; noble runtime sonames checked; build-time prefix, no relocation; A1–A7 admission; `core_pattern` record-only; VM steps and criteria; tests to run; the source-to-package sequence and checks (i)–(v); checksum-only integrity |
| Material owner decisions | **OD-L2-A:** accept withdrawing `core_pattern_ack` from L2 (ID-7 stays open). **OD-L2-B:** designate the digest-delivery channel for the manifest digest |
| External inputs to verify (not owner decisions; needed before building) | The python.org 3.13.11 tarball digest; the ten wheel files matching the hashed lock; a pip zipapp version and digest; noble build and runtime package names; the Ubuntu image ID and digest, and whether it ships git |
| Later authorities | Implementation; the development test run; the release commit `C`; reference build-host access and builds; VM provisioning; the VM validation run |

**No blocker remains** for implementation, apart from the later grants. Building needs the
external inputs above.

## 9. Changes from the proposal `74a39d87…` (this addendum governs)

| Proposal | Now |
|---|---|
| 5.2 identity-only startup check | The maintained-initialization adapter (1.3), with its narrower, exact claim |
| `core_pattern_ack` key and `CORE_HANDLER_UNACKNOWLEDGED` | Removed from L2 (3.2). The configuration keys are now `schema`, `release_root`, `runtime_account`, `data_root` |
| OL-1 (open) | (a) adopted. OL-4 is restated in 5.5; OL-5 becomes OD-L2-A; OL-6 is accepted as the limited claim (3.3) |
| V-step table | Refined in 4.3 |

Everything else in the proposal stands.

## 10. Preparation accounting

### 10.1 Charge for this file

| Item | Grant | Notes |
|---|---|---|
| Files | 1 | This file only |
| Directories | 0 | |
| Logical bytes | At most 131,072 | Charged against the unreserved preparation-byte balance |
| Allocated bytes | At most 147,456 | Same balance |

**Arithmetic, verified read-only:**
- **Starting point:** 13,276,326 / 27,975,680, outside the L1 partition (L1 ACCOUNTING
  `647f64a7…`).
- **Four preparation partitions since:** the revision, pin-cap and finalization addenda and the
  L2 proposal, each 131,072 / 147,456. That leaves 12,752,038 / 27,385,856 before this file.
- **After this partition:** **12,620,966 / 27,238,400**.

**Final size and SHA-256:** reported in chat after the readback, so this file contains no
self-hash.

**How it was written:** exclusive creation (`O_CREAT | O_EXCL | O_NOFOLLOW`) by a standalone
writer reading stdin, after the path was confirmed absent. Later edits were made only inside this
unsealed file.

**Not used or not created:**
- Not used: held reservations and spent validation reservations.
- Not created: no script, configuration, scratch or review file, and no memory note.

### 10.2 Actions in this task

| Kind | What was done |
|---|---|
| Read-only | Hashing of the governing proposal and the hashed requirements file; `grep`, `sed` and `cat` reads of the maintained sources cited; existence checks of this path |
| Not done | No implementation, execution, test, probe, build, provisioning, K, Git, commit or merge |

### 10.3 Host and session scope

These are separate, not charged here, and not zero: the session transcript, the reviewer pass
(about 273k tokens, about 122 s) and harness files.

END ADDENDUM
