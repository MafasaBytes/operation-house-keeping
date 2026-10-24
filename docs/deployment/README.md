# Installed release runbook (L2, Option B)

Operator runbook for one offline release of the bounded decision workflow on Ubuntu Server 24.04
amd64 with ext4, and for running the full synthetic workflow from that installed release.

**Status:** implemented, not built, not installed and not tested. Every step below that builds,
installs, provisions, runs or approves something needs its own owner grant. Nothing here is a
release-readiness or installed-workflow claim.

Governing design (unchanged): proposal
`docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md`
(`74a39d87…`), scope addendum `…-l2-scope-finalization-ADDENDUM.md` (`6bca403b…`), and the
reconciliation `2026-10-22-application-end-to-end-acceptance-and-l2-reconciliation.md`
(`7d8bff11…`), Option B.

## 1. What the pieces establish, and what they do not

| Piece | Establishes | Does not establish |
|---|---|---|
| `RELEASE-MANIFEST.json` checked against an out-of-band digest | The installed bytes equal those whose digest you received | Who built them; signature (ID-2 open); provenance (D-P open) |
| L1 `RELEASE-IDENTITY.json`, checked at every start | `app/` equals commit `C` exactly, without Git | Anything outside `app/` |
| `ohk-bdw-check` receipt | The maintained command families initialize in this release: pinned schemas load, the `ct.build.v1` identity assembles and validates, the output path admits | Evaluation, verification, replay, authoring, containment, physical validity |
| `ohk-bdw-run` | The maintained `checked-` and `t1-` commands run under deployment admission; output, scratch and diagnostic arguments must name paths below the data root (a textual check: the maintained publishers do not refuse a symlink planted inside the data root) | New commands, identity providers or build overrides (there are none) |

The legacy S1–S7 and governed commands use Git-only build identity and refuse when installed;
`ohk-bdw-run` refuses them with `INSTALLED_COMMAND_UNSUPPORTED`. No containment is claimed:
per-process limits bound one process only.

## 2. Layout

```text
R_REL/                      chosen at build time, e.g. /opt/ohk-bdw/releases/<commit12>-<tag>-<seq>
  python/                   CPython 3.13.11 built for R_REL/python, plus the 10 locked wheels
  app/applications/  app/backend/  app/RELEASE-IDENTITY.json
  bin/ohk-bdw-check  bin/ohk-bdw-run
  RELEASE-MANIFEST.json
/etc/ohk-bdw/deployment.json   root:root 0644, closed keys: schema, release_root, runtime_account, data_root
/var/lib/ohk-bdw/              runtime account, 0700, ext4; tmp/ and evidence/ inside, both 0700
```

A release is bound to its prefix. Installing at another path is refused (L1 `install_root`).
Relocation is not supported.

## 3. External inputs (needed before any build; none is embedded in the tools)

Each is passed explicitly with its expected SHA-256. The builder refuses a missing input, a
digest mismatch, a malformed digest or an unexpected wheelhouse entry before creating anything.

| Input | Flag | Identity to obtain and verify |
|---|---|---|
| `Python-3.13.11.tar.xz` | `--cpython-tarball`, `--cpython-sha256` | The digest python.org publishes for 3.13.11 [external, not in local records] |
| pip zipapp | `--pip-zipapp`, `--pip-zipapp-sha256` | A Python 3.13–compatible `pip.pyz` and its digest [external] |
| Wheelhouse | `--wheelhouse` | Exactly the 10 wheels matching the hashed lock (pip `--require-hashes` enforces each hash) [external] |
| Hashed requirements | `--requirements-hashed`, `--requirements-hashed-sha256` | `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt`, recorded `6bcc7bd8…` |
| Release commit `C` | `--repository`, `--commit` | Owner-authorized commit (not yet authorized) |
| Development source set `D_dev` | `--expected-source-set` | Recorded by the development test run (`release_manifest.py source-set`) |

Also external and unverified: the noble build-package and runtime-package names, the Ubuntu
image identity, and whether that image ships git.

## 4. Build host (reference Ubuntu 24.04 amd64; later grant)

```text
build_release.sh --repository REPO --commit C --release-root R_REL \
  --cpython-tarball Python-3.13.11.tar.xz --cpython-sha256 H --pip-zipapp pip.pyz --pip-zipapp-sha256 H \
  --wheelhouse WHEELS --requirements-hashed REQ --requirements-hashed-sha256 6bcc7bd8… \
  --expected-source-set D_dev --out /srv/ohk-bdw-build/<id>
```

- `R_REL` and `--out` must be outside `/home` and `/mnt`, because the interpreter build embeds
  build paths. Both must be absent beforehand.
- The builder exports `C` with `git -c tar.umask=022 archive`, refuses unless its source set
  equals `D_dev` (check i) and the running `tools/release` equals the committed copy, builds
  CPython (no PGO/LTO, `--disable-test-modules`), installs the wheels by hash offline with `--no-compile` through a
  build-only pip zipapp, refuses any non-locked distribution or `direct_url.json`, copies `app/`,
  writes the L1 record, the two wrappers, the soname list and the manifest, and writes
  `release.tar` and `BUILD-RECORD.json`.
- It prints the manifest digest. That digest is the identity of record. The release-id is a label.
- Bit-for-bit reproducibility is not claimed.

## 5. Staging on the build host (later grant; before packaging is final)

1. Run the 20 L1 tests and the L2 tests against an export of `C` using a **copy** of the staged
   interpreter (`cp -a R_REL/python` to a scratch prefix), always as `<copy>/bin/python3.13 -m
   pytest …`. The copy's console scripts (`bin/pytest`) and its rpath still name `R_REL/python`,
   so running `pytest` directly would execute the packaged prefix and write bytecode into it.
   Re-verify the manifest afterwards.
2. As root, `chown -R -h root:root R_REL` (the builder leaves it owned by the build user, which
   startup admission refuses as `RELEASE_TREE_UNSAFE`). The manifest records no owners, so its
   digest is unchanged. Write a root-owned 0644 staging configuration, and a staging data root
   (ext4, 0700, with `tmp/` and `evidence/`) owned by a non-root staging account.
3. As that account, run `R_REL/bin/ohk-bdw-check --config <staging config>` (section 7 form)
   and record `ct_build_sha256` and `nm_fields_sha256` from the receipt. These are the expected
   VM values.
4. Re-verify the manifest as root (symlinks are now root-owned):
   `python3 -I -B tools/release/release_manifest.py verify --root R_REL --expect-sha256 D`.
5. Publish the manifest digest through the owner-designated channel. **OD-L2-B is open:** no
   channel is named here, and nothing in the tools assumes one.

The installer and `release_manifest.py` are transferred alongside the tarball and are trusted as
delivered; nothing checks their digests. Deliver them through the same owner-designated channel
or compare them with the build record's commit by hand.

## 6. Installation (root, offline; later grant)

```text
sudo sh install_release.sh --tarball release.tar --manifest-sha256 D --release-root R_REL \
  --config-template deployment.json --data-root /var/lib/ohk-bdw --account ohk-bdw
```

The installer refuses unless it runs as root on Linux x86_64. `R_REL`, `R_REL.partial` and the
configuration must all be absent, the parent of `R_REL` and the tarball must be root-owned and not
group- or other-writable, and every path must be absolute, normalized and symlink-free. It then:

1. validates every archive member before extraction (no `..`, no absolute names, no hard links,
   devices or FIFOs, no group/other-writable or setuid modes, symlinks only under `python/`
   with relative targets inside the release) and extracts into the new `R_REL.partial`;
2. verifies the manifest against `D` and checks every required soname with `ldconfig -p`;
3. creates the account if absent (`adduser --system`, UID allocated by the system), and creates
   the data root, `tmp` and `evidence` (0700, account-owned) if absent. An existing data root is
   only checked, never changed. All three must be ext4 (`findmnt`);
4. writes the configuration exclusively (root, 0644) after checking that the template matches
   the arguments exactly;
5. publishes with a no-replace rename (`renameat2 RENAME_NOREPLACE`), verifies again at the final
   path, and writes `evidence/install-<stamp>-<pid>.json`.

On any refusal nothing is deleted: `R_REL.partial`, created directories and the configuration
remain for inspection, and nothing is activated. A signature option is reserved and refuses with
`SIGNATURE_POLICY_UNDEFINED` until ID-2 is decided.

## 7. Startup check

```text
cd / && timeout -k 3 60 runuser -u ohk-bdw -- prlimit --as=1073741824 --fsize=8388608 --core=0 -- \
  env -i PATH=/usr/bin:/bin TMPDIR=/var/lib/ohk-bdw/tmp R_REL/bin/ohk-bdw-check --config /etc/ohk-bdw/deployment.json
```

Admission order (each refusal exits 5 with a `ct.diagnostic.v1` line on stderr):
euid 0 (`RUNTIME_ACCOUNT_INVALID`, before the configuration is opened) → platform
(`PLATFORM_UNSUPPORTED`) → configuration file and keys (`CONFIG_INVALID`) → account uid
(`RUNTIME_ACCOUNT_INVALID`) → running release (`CONFIG_INVALID`) → data root ext4
(`FILESYSTEM_UNSUPPORTED`), then owner/mode/subdirectories/`TMPDIR` (`CONFIG_INVALID`) →
release tree (`RELEASE_TREE_UNSAFE`).

After admission: the four command families import (a pinned-schema mismatch gives the existing
refusal), the build identity is acquired (`BUILD_IDENTITY_UNAVAILABLE`, exit 3), and one new
`evidence/startup-<utc>-<pid>/startup-receipt.json` is written (`SIM_OUTPUT_UNSAFE`, exit 5, if
it cannot be). The receipt is also printed on stdout.

`core_pattern` is recorded in the receipt, never checked (OD-L2-A). RLIMIT_CORE 0 suppresses
non-pipe cores only. If a pipe handler is configured, cores of long-running workloads could
reach it; deciding who may accept that is ID-7, outside L2.

## 8. The root `-B` rule

Root must never import from `R_REL/app` without `-B`. A `__pycache__` under `app/` makes L1
refuse at every later start. The wrappers always use `-I -B`, and the release is root-owned and
read-only to the account as a second defence.

## 9. Option B: the full synthetic workflow from the installed release

The order is fixed by identity: inputs can only be bound to a build digest that exists, and the
producer evidence exists only after acquisition. No tool here approves anything. Each pause needs
a digest-bound owner approval record written by the owner (or a delegate on explicit instruction)
as a separate file, covering every candidate in the stage packet. Historical build permissions
are never carried forward: policy′ permits exactly the new release digest.

The rebinding tool (`tools/fixtures/t1_rebind.py`, specification `42d92411…`) runs on the
staging host with the repository, not inside the release. Its 108-test result keeps its own
attribution and limits, including the disconnected-opaque-object limitation.

All workflow commands run as the account through `ohk-bdw-run`, with inputs copied to a location
the account can read and every `--output-dir`/`--scratch-dir`/`--diagnostic-dir` below the data
root (for example `/var/lib/ohk-bdw/work/...`; create `work/` as the account, mode 0700). As
root, define a function (a variable cannot carry `cd /` and `&&`):

```text
run() { (cd / && timeout -k 3 600 runuser -u ohk-bdw -- prlimit --core=0 -- \
  env -i PATH=/usr/bin:/bin TMPDIR=/var/lib/ohk-bdw/tmp R_REL/bin/ohk-bdw-run --config /etc/ohk-bdw/deployment.json "$@"); }
```

`prlimit --core=0` suppresses non-pipe cores for these longer commands; a pipe handler in
`core_pattern` is still not controlled (ID-7). The 600 s bound is an operator choice, not a
measured duration. In the table, `$RUN` means this `run` function.

Command diagnostics keep each family's own shape (the `t1-` commands emit
`ct.t1-diagnostic.v1`). Only `ohk-bdw-check` and `ohk-bdw-run`'s own admission refusals use
`ct.diagnostic.v1`, with a T1 refusal's order reported as its stage.

| # | Step | Command or action | Output |
|---|---|---|---|
| 1 | Release identity | `ohk-bdw-check` on the staging install; take `ct_build_sha256` as `B` | `B` |
| 2 | Stage 1 rendering | `python3 -I -B tools/fixtures/t1_rebind.py stage1 --source-dir … --source-pins … --expected-source-pins-sha256 … --attestations <owner text> --expected-attestations-sha256 … --build-digest B --out S1` | policy′, P′, A0′ candidates and packet |
| 3 | **Pause AP-S1** | Owner approves the exact policy′, P′ and A0′ bytes | Approval record |
| 4 | Selection | `$RUN checked-selection-evaluate --request S1/selection/request.json --objects-dir S1/selection/objects --expected-request-pin P′ --expected-authority-pin A0′ --output-dir /var/lib/ohk-bdw/work/b0` | B0′ |
| 5 | Stage 2 rendering | `t1_rebind.py stage2 … --stage1-dir S1 --expected-stage1-review-sha256 … --prior-bundle B0′ --expected-prior-manifest-sha256 … --out S2` | simulator policy′, X′, E′, J′, G′ |
| 6 | **Pause AP-S2** | Owner approves the exact stage-2 bytes | Approval record |
| 7 | Acquisition | `$RUN t1-simulation-run --objects-dir S2/simulation-input --prior-bundle B0′ --expected-target-pin J′ --expected-execution-authority-pin E′ --expected-permission-pin G′ --expected-prior-request-pin P′ --expected-prior-authority-pin A0′ --output-dir /var/lib/ohk-bdw/work/m` | M′ with the actual evidence′ |
| 8 | Stage 3 rendering | `t1_rebind.py stage3 … --stage1-dir S1 --expected-stage1-review-sha256 … --stage2-dir S2 --expected-stage2-review-sha256 … --producer-package M′ --expected-producer-manifest-sha256 … --out S3` | R′ from M′'s evidence |
| 9 | **Pause AP-S3** | Owner approves R′ | Approval record |
| 10 | Handoff | `$RUN t1-reassessment-prepare --producer-package M′ --expected-producer-manifest-pin … --objects-dir S3/request-input --expected-target-pin J′ --expected-execution-authority-pin E′ --expected-permission-pin G′ --expected-prior-request-pin P′ --expected-prior-authority-pin A0′ --prior-bundle B0′ --scratch-dir /var/lib/ohk-bdw/work/scratch-h --output-dir /var/lib/ohk-bdw/work/h` | H′ |
| 11 | **Pause AP-S4** | The evaluation authority A′ is prepared outside these tools after the handoff and approved by its issuer | A′ |
| 12 | Evaluation | `$RUN t1-reassessment-evaluate` with the step-10 flags, its `--objects-dir` **replaced** by the directory holding A′ and its closure, plus `--handoff-package H′ --expected-handoff-pin … --expected-request-pin R′ --expected-authority-pin A′`, with a new `--scratch-dir` and `--output-dir` below the data root | Bundle and workflow receipt |
| 13 | Verification | `$RUN t1-workflow-verify` with the step-12 flags **except** `--objects-dir` (so: the target, execution-authority, permission and prior pins, `--prior-bundle`, `--producer-package`, `--expected-producer-manifest-pin`, `--handoff-package`, `--expected-handoff-pin`, `--expected-request-pin`, `--expected-authority-pin`), plus `--bundle … --expected-workflow-receipt-pin …` and a new `--scratch-dir` and `--output-dir` | Report |
| 14 | Replay | `$RUN checked-reassessment-replay --bundle <step-12 --output-dir>/bundle --expected-request-pin R′ --expected-authority-pin A′ --output-dir /var/lib/ohk-bdw/work/replay`, with R′ and A′ exactly the pins approved at AP-S3 and AP-S4 and used in steps 12–13 (all four flags are required by the maintained parser; the output directory is new and below the data root) | Replay bundle |

## 10. Fresh VM and reuse of inputs (later grant)

Run the addendum's V0–V6 and N1–N3 steps on a disposable Ubuntu 24.04 amd64 VM without git and
without a checkout. **Before any rebound input is used on the VM**, run `ohk-bdw-check` there and
compare `ct_build_sha256` and `nm_fields_sha256` with the staging receipt. Equality requires
identical release bytes, the same prefix and the same glibc version string.

- If they differ, stop. The staged inputs do not apply; render and approve new ones for the VM's
  build.
- If acquisition is repeated on the VM, its evidence must be byte-identical to staging's, or R′
  must be re-rendered and re-approved.

## 11. Uninstall (manual, owner disposition)

There is no uninstall, upgrade or `current` link in L2. To remove a release, the owner decides
whether to keep evidence, then as root removes `R_REL` and the configuration that names it. The
data root and the account are shared state and are removed only by explicit decision.

## 12. Known limits

- A root-level change outside `app/` and outside the locked distributions, between manifest
  checks, is not detected at startup; the startup walk checks ownership and writability only.
- Personal paths (owner-corrected rule, 2026-10-23): the interpreter is configured with
  `--disable-test-modules`, and the builder's portability step (`PORTABILITY_CHECK_FAILED`)
  refuses an actual dependency, every path compared after normalization: a personal release
  or build prefix; a shebang interpreter (or `env`'s argument) of a script in `python/bin` or
  `bin` outside the release and the system shells; a run-time sysconfig path outside the
  prefix; an absolute pkg-config value or `-L`/`-I` flag outside the prefix; a library
  resolved or loaded by absolute path (`ldd`), or searched (RUNPATH/RPATH, `$ORIGIN`
  expanded), outside the release and the system library directories; the CPython `test`
  package still present; or any `*.pth` file anywhere in the release (`PTH_FILE_PRESENT`: `site`
  would add its absolute lines to `sys.path` and execute its `import` lines at every start; the
  first release allows none, and the builder never interprets or deletes one). An absent
  `python/lib/python3.13/site-packages` refuses as missing evidence. This covers the `.pth`
  mechanism only: a `sitecustomize` or `usercustomize` module is not refused by this rule. Missing or malformed evidence also refuses: every dynamic ELF object
  (found by content) needs one `ldd` and one `readelf` block, and every run-time sysconfig key
  must be present. Release-rule refusals found while scanning keep their own codes. Every
  other `/home/` or `/mnt/` literal (documentation examples, build-directory metadata) is
  listed in `<out>/portability.json` for review and is not by itself treated as
  non-portability.
- Build size, `nm.build` hashing time on the target, and noble library effects are unmeasured.
- The L1 record tool's docstring mentions a "separately signed" manifest. The actual policy is
  checksum verification only; the tool is unchanged because its bytes are L1-tested.
