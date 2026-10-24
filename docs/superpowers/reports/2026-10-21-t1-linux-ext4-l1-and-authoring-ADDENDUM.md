# Addendum: revised L1 and maintained authoring contract (Linux/ext4 vertical slice)

Status: PREPARATION ONLY. Nothing here is implemented, applied, executed, tested, syntax-checked,
staged or committed, and nothing here grants execution authority. The embedded patch is unapplied.

**Governing package (preserved unchanged):** prefix `docs/superpowers/reports/2026-10-21-t1-linux-ext4-vertical-slice-`.
- MANIFEST `8982738e7219103fc2e790bb25769c5c1a580c40e0c4f4c1253e31ebe720dcf6`
- RECEIPT `db63c022db14aca8761287b6617a4d1b23be020cd68bd66c73e014374de071b5`
- Original L1 patch block `8863919cce816bd4853c5ad8e574dc4835e44b9200985096ce987095a235d3e3` (15,896 B), historical.

**Recorded state:**
- branch `claude/t1-startup-chain-repair`, HEAD `07055c63…`, index `43dca87c…`;
- accepted checkpoint: `record.py` `b790cf22…`, successor test `f60636f5…`, launcher `228509f4…`;
- disposition `7699f017…`.

**Evidence labels:**
- **[SRC]** source-derived;
- **[OBS]** observed runtime evidence;
- **[PROP]** proposed;
- **[EST]** estimate;
- **[MISSING]** missing evidence or owner decision;
- **[INF]** inference from source.

## 0. What this addendum supersedes (the sealed files are not edited)

| Sealed statement | Superseded by |
|---|---|
| PROPOSAL §5.2 patch, §5.3 identities, plan L1 `post_images` / `patch_block_sha256` | §A3 successor patch and identities (the originals stay historical) |
| PROPOSAL §5.4 and plan L1 `prospective_tests` | §A4 |
| PROPOSAL §4.2 "weaker: permission bits are not compared" | §A1: the successor compares the owner-execute bit as Git records it |
| PROPOSAL §1 item 2, the build-identity bullet of §2.7 (the generic L2 "exit 5" admission shape is not affected), §7 N4 and plan N4: "`BUILD_IDENTITY_UNAVAILABLE` exit 5" | **Correction:** raised with *stage* 5 and **exit 3** (`checked_runtime.py:53` `refuse('BUILD_IDENTITY_UNAVAILABLE', 5, …)`; `checked_contracts.py:58,64-71` default `EXIT_INTEGRITY = 3`) [SRC]. `SIM_BUILD_UNAVAILABLE` is order 2, exit 3 (unchanged). |
| PROPOSAL §8 ID-6 row, plan `genuine_coupling`, and plan base `k_and_checkpoint_consequences` ("K precedes every commit") as it applies to portability work: applying L1 "breaks … `ls-files`" | §C. `ls-files` lists the index, so it changes only when the index changes, not when an untracked file is added. |
| PROPOSAL §9 ID-1 and ID-5 wording | §A1 (refined ID-1) and §B (concrete authoring decisions AU-1 to AU-8) |
| plan stage L3 `changes` | §B4 |

Everything else in the sealed package stands, including PD-1 to PD-4 and ID-2, ID-3, ID-4 and ID-7, all
still unresolved.

---

## Part A: revised L1

### A1. Source-witness equivalence, defined precisely

**What the identity asserts.** `nm.build.v1` (`measurement_build.py:72-75`) and its `ct.build.v1`
wrapper (`checked_runtime.py:55-59`) carry these assertions [SRC]:

| # | Assertion | Field(s) | Git path establishes it by | Installed witness establishes it by | Equal? |
|---|---|---|---|---|---|
| F1 | The source checkpoint is commit C | `checkpoint` (40 hex digits) | `git rev-parse HEAD` in the checkout, trusting the local object store under SHA-1 | `sha1("commit <n>\0"+object) == C`, using the embedded commit object, under the same hash | same fact, same hash strength |
| F2 | `applications/` and `backend/` are exactly C's trees | `clean_application_backend: true` (ct) | `git status --porcelain --untracked-files=all -- applications backend` is empty, meaning tracked content and modes match HEAD and there are no untracked unignored files | Each installed file's blob id, recomputed from its bytes, plus its owner-execute bit, rebuild the two subtree ids. Those must equal the entries of C's root tree (embedded object, verified under F1). The installed file set must be exactly the listed set. | same fact; see the differences below |
| F3 | Per-file SHA-256 of the `.py` files and the lock among those paths | `source_manifest` | hashes the paths from `git ls-files` | hashes the paths listed in the verified record. Under F2 this is the same path set, read from the same bytes. | equal |
| F4 | The running environment | `environment_manifest`: interpreter implementation/version, executable SHA-256 and size; platform system/machine/`libc_ver()`; per-distribution manifests of the files listed in RECORD, with bytes hashed (no `.pyc`); lock SHA-256 | computed from the running process | **identical code, unchanged by L1** | equal under the same environment |
| F5 | Declared constants | `schema`, `profile`, `id`, `revision`, `entrypoint`, `contract_sha256`, `resource_policy_sha256`, ct `contract_editions` | literals | literals, unchanged | equal |

**Differences in F2, stated rather than hidden:**
- **Ignored files.** Git ignores files matched by `.gitignore` (for example `__pycache__`); the witness
  refuses them. The witness is stricter, which can only refuse more trees, never admit a different one.
- **Index stat cache.** Git may trust its index stat cache; the witness re-reads every byte. The witness
  is at least as strong.
- **Modes.** Git records `100755` when the owner-execute bit is set (with `core.filemode=true`). The
  successor witness compares exactly that bit. That removes the sealed proposal's "weaker on modes"
  caveat.
  - Where a checkout runs with `core.filemode=false` (common on DrvFS), Git ignores mode drift and the
    witness does not.
  - So the witness is stricter there, never weaker.
- **Other cases where Git is weaker:** `.git/info/exclude` and `core.excludesFile`, the assume-unchanged
  and skip-worktree index bits, and clean/smudge or eol filters. In each, Git can report clean while the
  bytes differ from the blobs. The witness compares bytes, so it is stricter in all of them.
- **Time-of-check gap.** The SHA-1 pass and the later SHA-256 pass read the files separately. This is the
  same gap the Git path has between `status` and hashing. In the proposed deployment it is mitigated by a
  root-owned release; that mitigation is still unverified (L2 `RELEASE_TREE_UNSAFE`).

**Equality of the resulting wire.** With the same committed sources (same commit and bytes), the same
interpreter, the same distributions and the same platform strings, both witnesses produce a
**byte-identical** `nm.build.v1` wire. That follows from F1-F5, because no field records which witness
was used. The A2 test makes this a checked expectation, not an assumption. Nothing differs by design.

**What equality does not establish:**
- **Runtime-environment equivalence.** F4 covers only the interpreter executable, the platform strings,
  the files listed in the RECORDs of the **locked** distributions (excluding `.pyc`), and the lock. It does
  **not** cover:
  - other site-packages distributions, `.pth` files (processed even under `-I`), `sitecustomize` or
    `pyvenv.cfg`;
  - distribution `.pyc` files;
  - standard-library bytes or `lib-dynload` extension modules;
  - `libpython` (if shared), or system shared libraries such as SQLite, OpenSSL, libffi, zlib and
    liblzma;
  - the kernel, or locale and environment variables.

  Matching source, interpreter executable and glibc version string therefore do **not** establish equal
  bytes or behaviour for those components.
- **Bytecode self-poisoning.** Imports write `__pycache__` into any writable tree before `identity()`
  runs, and the witness then refuses (the A2 bytecode test witnesses this).
  - Installed operation therefore depends on an unwritable release tree, `-B` or
    `PYTHONDONTWRITEBYTECODE` (L2).
  - Precompiled bytecode cannot ship, since it is not in the Git tree.
- **Release provenance or authentication.** Neither witness authenticates anything. Git trusts a local,
  writable object store; the witness trusts a record whose objects hash correctly. Authenticity is
  install-time signature verification (sealed ID-2, unresolved).
- **Cross-host portability or replay.** An equal wire on two hosts admits checked replay's byte-equality
  gate (`checked_runtime.py:1007-1008`), but behavioural equality across hosts is unproven. Portability
  and replay claims stay limited to the same installed release on the evidenced target.

**Schema judgement.** Preserving `ct.build.v1` / `nm.build.v1` is technically defensible for this
narrowly defined equivalence: every asserted fact F1-F5 keeps its meaning and its value, and F2 is
established at least as strictly. A schema change would be warranted only to **add** a fact, for example
an explicit `source_witness` field. That is a design choice, not a correction of a changed fact.

**Refined ID-1 (proposed owner decision, still open):**
> Accept that, for `nm.build.v1` / `ct.build.v1`, an installed release verified by
> `bdw.release-identity.v1` establishes F1 and F2 with the same meaning as a clean Git checkout.
> The wire is unchanged, and the witness mode is recorded in deployment admission evidence (L2), not in
> the build wire. This acceptance makes no claim of runtime-environment equivalence beyond F4, of
> provenance, or of cross-host behavioural equality.
>
> **Alternative:** require `ct.build.v2` with an added `source_witness` field. That migrates nine record
> schemas and `schemas_sha256`, and changes every build digest.

### A2. Production-boundary coverage (revised test design)

The test file grows to **20 cases**. Run it with an isolated ext4 `--basetemp`, since the mode cases rely
on POSIX permission bits.

**Production boundary (3 cases, sharing one module fixture):**
- **Matched fixture:**
  - the working-tree `applications/` and `backend/` (with L1 applied) are copied into a fresh temporary
    Git repository;
  - file modes are **normalized** (directories 0755, files 0644), so the result does not depend on the
    source filesystem;
  - the copy is committed;
  - a copy of that commit's two directories becomes the installed root;
  - `RELEASE-IDENTITY.json` comes from the recorder, using **real Git objects** of the fixture repository.
- **Probe:** each case runs the production functions in a subprocess with the same interpreter:
  `measurement_build.identity()` and `checked_runtime._current_build(ExecutableBuild())`, which validates
  `ct.build.v1`.

1. **`test_installed_identity_equals_git_identity_without_git`** covers obligations 1 and 2.
   - One probe runs against the checkout (Git on PATH). The other runs against the installed root with
     **PATH set to an empty directory**. A runtime Git call would raise `FileNotFoundError` inside
     `identity()`; nothing catches it, so the probe would exit non-zero.
   - **Assertions, kept separate to localize failures:**
     - each probe reports its own `build.ROOT`;
     - the installed side shows no refusal;
     - the Git-side checkpoint is the fixture commit;
     - the installed `nm.build.v1` bytes equal the Git side's exactly;
     - the installed `ct.build.v1` bytes equal the Git side's exactly.
   - **Same everything:** same commit, bytes, interpreter, distributions and platform. No difference is
     intended.
   - **Oracle:** the independent oracle is the maintained Git path on identical bytes. The installed-source
     verification is not mocked.
2. **`test_checkout_with_release_record_refuses`** covers obligation 3.
   - A copy of the fixture checkout (including `.git`) is probed first as a **twin control**, and must
     admit.
   - Then a `RELEASE-IDENTITY.json` is added at its root, where `git status` for
     `applications`/`backend` stays clean. The probe must now report:
     - `measurement_build.identity()` → `WorkflowInputError`;
     - `ExecutableBuild` → `CheckedRefusal('BUILD_IDENTITY_UNAVAILABLE', stage 5, exit_class 3)`.
3. **`test_writable_installed_root_without_bytecode_suppression_refuses`.**
   - A writable copy of the installed root is probed with `-I` only, without `-B` and without
     `PYTHONDONTWRITEBYTECODE`.
   - Imports write `__pycache__`, and identity must refuse. This witnesses the A1 bytecode dependence.

**Unit (17 cases):**
- published Git vectors and the real-Git oracle;
- **installed-mode accounting:** `verified_source(root, Work())` counts one read per file and the exact
  bytes read, and leaves `build_hash_bytes` absent;
- **14 divergence refusals**, including:
  - **`installed_exec_added` and `installed_exec_removed`:** record and tree stay valid, and only the
    installed owner-execute bit differs. These are the witnesses of the new mode gate. The fixture
    includes one `100755` entry, copied with its permission bits.
  - **`record_mode_flip`:** refused by the recomputed-tree gate.
  - **`consistent_byte_change` and `consistent_drop`:** these isolate the tree gate.

**Fixture Git:** fixture setup uses Git only in temporary repositories (with timeouts), under a later
explicit test grant. Nothing here was run.

**What the tests cover:**
- **Covered (unit/fixture):** the witness algorithm and its gates, including modes; production integration
  through `measurement_build` and `ExecutableBuild`; no runtime Git; wire equality under one environment;
  the stray-record refusal with its control; bytecode self-poisoning; and installed-mode counters.
- **Needs clean-install runtime evidence (L4):** the Ubuntu target, root-owned install modes, signing,
  systemd containment, ext4 admission, the complete workflow and cross-host behaviour.
- **Not qualified:** deployment, signing and the workflow.

### A3. Exact successor candidate

**Changed responsibilities versus the reviewed round-3 candidate (sealed `8863919c…`):**
- **`release_identity.py`:**
  - compares the owner-execute bit with the recorded mode (`100755` ⇔ `S_IXUSR`), using `fstat` on the
    same `O_NOFOLLOW` descriptor that is hashed;
  - maps `RecursionError` (a deeply nested record) to the refusal;
  - installed-mode reads add only `build_bytes_read` and `build_read_operations`;
  - `build_hash_bytes` keeps its SHA-256-only meaning, which
    `test_production_build_hash_accounting_matches_actual_calls` (`tests/reassessment_profile/test_capture.py:343-358`)
    pins. The SHA-1 witness work is visible only as bytes read. This replaces the round-3 counting, which
    also overcounted the record JSON.
- **Test file:** adds the matched fixture (normalized modes), the probe, three production-boundary tests,
  the accounting case and two exec-bit cases. It factors the Git environment and commit into helpers,
  with timeouts.
- **Unchanged from round 3:** `measurement_build.py` and `tools/release/release_identity_record.py`.

**Pre-images:**
- `applications/bounded_decision_workflow/measurement_build.py` `172efff48f88f6f9236259a694d623145cf95fda1b0693e458c809ba83e55d25` (4,627 B);
- the other three paths are absent;
- new directory required: `tools/release/`, created by the future application, not now.

**Post-images, patch block identity and downstream consequences:** see A3-TABLE below (computed by
strict in-memory application only; no file or scratch tree was written).

| Path | Pre-image | Post-image SHA-256 | Bytes | Git blob |
|---|---|---|---|---|
| `applications/bounded_decision_workflow/measurement_build.py` | `172efff4…5d25` (4,627 B) | `5c3619e4e9435bbc9ced21898bbb9806161dbab03a265f8221376ed574520267` | 4,987 | `ca566e2da98e5b7c06ad285881f15c385039bded` |
| `applications/bounded_decision_workflow/release_identity.py` | absent | `2dfb4fca907ebd8dfc3c36dc22b27c93dfa0f98b5ddddffed65a69ddc2d28092` | 6,458 | `10dcaae2aa959283c4c9b6aaa9e39d831551492a` |
| `tools/release/release_identity_record.py` | absent | `b30a2cd8341fae2544e0f8ded48a90ab35cbe2ebf25cea73f3d08dfd9cfe6bf6` | 2,460 | `7da7d0123b2d95d46c23cde725311dbab7f45414` |
| `tests/applications/bounded_decision_workflow/test_release_identity.py` | absent | `807b08edf51d4edad978623619337268ef933d89e5e7929cedf1613f4904825c` | 10,414 | `3dfecce110e8a8736420114e18536ea33dc3f44c` |

- **Patch block:** the bytes strictly between the two marker lines (markers excluded). SHA-256
  `7bf112ec71a285bc1037eca0a90f86653e1c9ab05ecabbf63b177031a8ca4d07`, 22,043 B.
- **Unchanged from the reviewed round-3 candidate:** `measurement_build.py` (`5c3619e4…`) and
  `release_identity_record.py` (`b30a2cd8…`).
- **Changed:** `release_identity.py` and the test file.
- **Superseded as candidate commitments, all retained as historical preparation:**
  - round-1 identities (`cf566810…`, `7674f031…`, `bb57510a…`, `de545e0f…`) and the round-1 block
    `8c85d8b6…`;
  - round-3 identities `fed983ca…` (`release_identity.py`) and `a7c3a35b…` (test), and block `8863919c…`;
  - this addendum's own first-review draft identities `618bbdc5…` (`release_identity.py`) and `b69098ab…`
    (test), and block `6a445cea…`.
- **Downstream consequences if applied and later committed:** Git-mode build digests change once, and
  `0fc2cd25…` stops being current (sealed §4.4). The K source manifest and Route B `current_sources` no
  longer match (§C). Integration and commit identities are decided only under a later grant.

<<<BEGIN L1 SUCCESSOR PATCH>>>
--- a/applications/bounded_decision_workflow/measurement_build.py
+++ b/applications/bounded_decision_workflow/measurement_build.py
@@ -6,7 +6,7 @@
 import platform
 import subprocess
 import sys
-from . import build
+from . import build, release_identity
 from .measurement_contracts import PROFILE, APPROVED_POLICY_SHA, canonical_json_bytes
 from .measurement_wire import fail
 
@@ -19,14 +19,21 @@
         return subprocess.check_output(['git','--no-optional-locks','-C',str(build.ROOT),*args],timeout=10).decode().strip()
     if platform.python_implementation()!='CPython' or platform.python_version_tuple()[:2]!=('3','13'):
         raise build.unavailable()
-    if git('status','--porcelain','--untracked-files=all','--','applications','backend'):
+    installed=release_identity.present(build.ROOT)
+    if installed:
+        # Installed release: the same checkpoint and exact-tree facts, recomputed
+        # from installed bytes; no mutable checkout and no Git child.
+        checkpoint,names=release_identity.verified_source(build.ROOT,work)
+    elif git('status','--porcelain','--untracked-files=all','--','applications','backend'):
         raise build.unavailable()
-    checkpoint=git('rev-parse','HEAD')
+    else:
+        checkpoint=git('rev-parse','HEAD')
     def digest_bytes(data):
         if work is not None:work.physical['build_hash_bytes']=work.physical.get('build_hash_bytes',0)+len(data)
         return hashlib.sha256(data).hexdigest()
-    names=subprocess.check_output(['git','--no-optional-locks','-C',str(build.ROOT),
-                                  'ls-files','applications','backend'],timeout=10).decode().splitlines()
+    if not installed:
+        names=subprocess.check_output(['git','--no-optional-locks','-C',str(build.ROOT),
+                                      'ls-files','applications','backend'],timeout=10).decode().splitlines()
     def digest_file(path):
         h=hashlib.sha256();size=0
         with path.open('rb') as stream:
--- /dev/null
+++ b/applications/bounded_decision_workflow/release_identity.py
@@ -0,0 +1,167 @@
+"""Installed-release source witness: the Git object chain recomputed from installed bytes.
+
+Used only when the application root has no .git and carries RELEASE-IDENTITY.json.
+It establishes the same two facts as the maintained Git path (the checkpoint, and
+that applications/ and backend/ equal that commit exactly) without a mutable
+checkout. It is not a signature or provenance check: release authenticity is
+verified separately at installation. Ignored files are refused, not ignored.
+File modes are compared by the owner-execute bit, as Git records them.
+"""
+import base64
+import hashlib
+import json
+import os
+import re
+import stat
+
+from . import build
+
+NAME = 'RELEASE-IDENTITY.json'
+SCHEMA = 'bdw.release-identity.v1'
+TOPS = ('applications', 'backend')
+RECORD_BYTES = 1048576
+FILE_BYTES = 67108864
+MAX_ENTRIES = 4096
+MAX_PARTS = 16
+MAX_PATH = 240
+HEX40 = re.compile('[0-9a-f]{40}\\Z')
+PART = re.compile('[A-Za-z0-9_.-]+\\Z')
+MODES = ('100644', '100755')
+FIELDS = {'schema', 'install_root', 'commit', 'commit_object', 'root_tree_object', 'entries'}
+
+
+def present(root):
+    return os.path.lexists(root / NAME)
+
+
+def _object_id(kind, data):
+    return hashlib.sha1(b'%s %d\0' % (kind, len(data)) + data).hexdigest()
+
+
+def _read(path, cap, work=None, executable=None):
+    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
+    with os.fdopen(fd, 'rb') as stream:
+        mode = os.fstat(stream.fileno()).st_mode
+        if not stat.S_ISREG(mode):
+            raise build.unavailable()
+        if executable is not None and bool(mode & stat.S_IXUSR) != executable:
+            raise build.unavailable()
+        data = stream.read(cap + 1)
+    if len(data) > cap:
+        raise build.unavailable()
+    if work is not None:
+        # One operation per file. build_hash_bytes keeps its SHA-256-only meaning;
+        # the SHA-1 witness work is visible as bytes read.
+        work.physical['build_bytes_read'] = work.physical.get('build_bytes_read', 0) + len(data)
+        work.physical['build_read_operations'] = work.physical.get('build_read_operations', 0) + 1
+    return data
+
+
+def _tree(entries):
+    """Git tree id of {name: (mode, blob) | {...}} in Git's name order."""
+    body = b''
+    def order(name):
+        return name.encode() + (b'/' if isinstance(entries[name], dict) else b'')
+    for name in sorted(entries, key=order):
+        value = entries[name]
+        if isinstance(value, dict):
+            mode, oid = b'40000', _tree(value)
+        else:
+            mode, oid = value[0].encode(), value[1]
+        body += mode + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)
+    return _object_id(b'tree', body)
+
+
+def _tree_entries(data):
+    found = {}
+    at = 0
+    while at < len(data):
+        space = data.index(b' ', at)
+        nul = data.index(b'\0', space)
+        if nul + 21 > len(data):
+            raise build.unavailable()
+        found[data[space + 1:nul]] = (data[at:space], data[nul + 1:nul + 21].hex())
+        at = nul + 21
+    return found
+
+
+def verified_source(root, work=None):
+    """Return (checkpoint, sorted paths) or refuse REPLAY_BUILD_UNAVAILABLE."""
+    try:
+        return _verified(root, work)
+    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as e:
+        if isinstance(e, build.WorkflowInputError):
+            raise
+        raise build.unavailable() from e
+
+
+def _verified(root, work):
+    if os.path.lexists(root / '.git'):
+        raise build.unavailable()
+    record = json.loads(_read(root / NAME, RECORD_BYTES, work))
+    if type(record) is not dict or set(record) != FIELDS or record['schema'] != SCHEMA:
+        raise build.unavailable()
+    if record['install_root'] != str(root):
+        raise build.unavailable()
+    commit = record['commit']
+    if type(commit) is not str or not HEX40.fullmatch(commit):
+        raise build.unavailable()
+    commit_object = base64.b64decode(record['commit_object'], validate=True)
+    root_tree = base64.b64decode(record['root_tree_object'], validate=True)
+    head = re.match(rb'tree ([0-9a-f]{40})\n', commit_object)
+    if _object_id(b'commit', commit_object) != commit or head is None:
+        raise build.unavailable()
+    if _object_id(b'tree', root_tree) != head.group(1).decode():
+        raise build.unavailable()
+    top = _tree_entries(root_tree)
+    entries = record['entries']
+    if type(entries) is not list or not 0 < len(entries) <= MAX_ENTRIES:
+        raise build.unavailable()
+    nested = {name: {} for name in TOPS}
+    paths = []
+    for item in entries:
+        if type(item) is not list or len(item) != 3 or not all(type(v) is str for v in item):
+            raise build.unavailable()
+        path, mode, blob = item
+        parts = path.split('/')
+        if not 2 <= len(parts) <= MAX_PARTS or len(path) > MAX_PATH or parts[0] not in TOPS \
+                or mode not in MODES or not HEX40.fullmatch(blob) \
+                or any(p in ('.', '..') or not PART.fullmatch(p) for p in parts):
+            raise build.unavailable()
+        node = nested[parts[0]]
+        for part in parts[1:-1]:
+            node = node.setdefault(part, {})
+            if not isinstance(node, dict):
+                raise build.unavailable()
+        if parts[-1] in node:
+            raise build.unavailable()
+        node[parts[-1]] = (mode, blob)
+        paths.append(path)
+    if paths != sorted(paths):
+        raise build.unavailable()
+    for name in TOPS:
+        if top.get(name.encode()) != (b'40000', _tree(nested[name])):
+            raise build.unavailable()
+    installed = []
+    def walk(relative, depth):
+        if depth >= MAX_PARTS:
+            raise build.unavailable()
+        with os.scandir(root / relative) as listing:
+            for entry in listing:
+                name = relative + '/' + entry.name
+                if entry.is_dir(follow_symlinks=False):
+                    walk(name, depth + 1)
+                elif entry.is_file(follow_symlinks=False):
+                    installed.append(name)
+                else:
+                    raise build.unavailable()
+    for name in TOPS:
+        if not stat.S_ISDIR(os.lstat(root / name).st_mode):
+            raise build.unavailable()
+        walk(name, 1)
+    if sorted(installed) != paths:
+        raise build.unavailable()
+    for path, mode, blob in entries:
+        if _object_id(b'blob', _read(root / path, FILE_BYTES, work, mode == '100755')) != blob:
+            raise build.unavailable()
+    return commit, paths
--- /dev/null
+++ b/tools/release/release_identity_record.py
@@ -0,0 +1,56 @@
+"""Write RELEASE-IDENTITY.json for one commit (build host only; reads Git, creates one new file).
+
+Usage: release_identity_record.py REPOSITORY COMMIT INSTALL_ROOT OUTPUT
+INSTALL_ROOT must be the absolute, normalized, symlink-free prefix of app/ on the
+target, because the verifier compares it with the resolved root. The file records
+Git objects only. Release authenticity is the separately signed
+RELEASE-MANIFEST.json; this file proves nothing about who built the release.
+"""
+import base64
+import json
+import os
+import re
+import subprocess
+import sys
+
+
+def git(repository, *args):
+    return subprocess.check_output(['git', '--no-optional-locks', '-C', repository, *args], timeout=60)
+
+
+def main(argv=None):
+    repository, commit, install_root, output = sys.argv[1:] if argv is None else argv
+    if not os.path.isabs(install_root) or os.path.normpath(install_root) != install_root:
+        raise SystemExit('install root must be an absolute normalized path')
+    commit = git(repository, 'rev-parse', '--verify', commit + '^{commit}').decode().strip()
+    commit_object = git(repository, 'cat-file', 'commit', commit)
+    tree = re.match(rb'tree ([0-9a-f]{40})\n', commit_object).group(1).decode()
+    root_tree = git(repository, 'cat-file', 'tree', tree)
+    entries = []
+    listing = git(repository, 'ls-tree', '-r', '-z', '--full-tree', commit, '--', 'applications', 'backend')
+    for line in listing.split(b'\0'):
+        if not line:
+            continue
+        meta, path = line.split(b'\t', 1)
+        mode, kind, oid = meta.decode().split(' ')
+        if kind != 'blob' or mode not in ('100644', '100755'):
+            raise SystemExit('unsupported tree entry: ' + path.decode())
+        entries.append([path.decode(), mode, oid])
+    record = dict(schema='bdw.release-identity.v1', install_root=install_root, commit=commit,
+                  commit_object=base64.b64encode(commit_object).decode(),
+                  root_tree_object=base64.b64encode(root_tree).decode(), entries=sorted(entries))
+    data = (json.dumps(record, sort_keys=True, indent=1) + '\n').encode()
+    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
+    try:
+        with os.fdopen(fd, 'wb') as stream:
+            stream.write(data)
+            stream.flush()
+            os.fsync(stream.fileno())
+    except BaseException:
+        os.unlink(output)
+        raise
+    return 0
+
+
+if __name__ == '__main__':
+    raise SystemExit(main())
--- /dev/null
+++ b/tests/applications/bounded_decision_workflow/test_release_identity.py
@@ -0,0 +1,214 @@
+"""L1 installed-release source witness. Real Git is used only as an independent oracle.
+
+The production-boundary tests run the production identity functions in subprocesses
+against one committed fixture tree observed through both witnesses. Run with an
+isolated ext4 --basetemp: the mode cases rely on POSIX permission bits.
+"""
+import json
+import os
+from pathlib import Path
+import shutil
+import subprocess
+import sys
+
+import pytest
+
+from applications.bounded_decision_workflow import release_identity
+from applications.bounded_decision_workflow.errors import WorkflowInputError
+from applications.bounded_decision_workflow.measurement_wire import Work
+
+ROOT = Path(__file__).parents[3]
+TOOL = ROOT / 'tools/release/release_identity_record.py'
+FILES = {'applications/__init__.py': b'', 'applications/pkg/a.py': b'A = 1\n',
+         'applications/pkg-data.json': b'{}\n', 'backend/__init__.py': b'', 'backend/b.py': b'B = 2\n',
+         'docs/outside.md': b'not installed\n'}
+DEFECTS = ['extra_pycache', 'changed_byte', 'missing_file', 'symlink', 'git_directory', 'relocated',
+           'forged_commit_object', 'record_mode_flip', 'consistent_byte_change', 'consistent_drop',
+           'unsorted_entries', 'duplicate_entry', 'installed_exec_added', 'installed_exec_removed']
+PROBE = '''import json, sys
+sys.path.insert(0, sys.argv[1])
+from applications.bounded_decision_workflow import measurement_build
+from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
+from applications.bounded_decision_workflow.checked_runtime import ExecutableBuild, _current_build
+from applications.bounded_decision_workflow.errors import WorkflowInputError
+out = {'root': str(measurement_build.build.ROOT)}
+try:
+    out['nm'] = measurement_build.identity().decode()
+except WorkflowInputError as e:
+    out['nm_refused'] = type(e).__name__
+try:
+    out['ct'] = _current_build(ExecutableBuild()).decode()
+except CheckedRefusal as e:
+    out['ct_refused'] = [e.code, e.stage, e.exit_class]
+sys.stdout.write(json.dumps(out))
+'''
+
+
+def git_env(home):
+    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
+    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME='t',
+               GIT_AUTHOR_EMAIL='t@example.invalid', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@example.invalid')
+    return env
+
+
+def commit_all(repository, env, *paths):
+    for args in (['init', '-q'], ['add', '-A', '--', *paths], ['commit', '-q', '-m', 'fixture']):
+        subprocess.run(['git', '-C', str(repository), *args], check=True, env=env, timeout=60)
+    return subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], env=env,
+                                   timeout=60).decode().strip()
+
+
+def probe(root, env, flags=('-I', '-B')):
+    done = subprocess.run([sys.executable, *flags, '-c', PROBE, str(root)], env=env,
+                          capture_output=True, timeout=300)
+    assert done.returncode == 0, done.stderr.decode(errors='replace')
+    return json.loads(done.stdout)
+
+
+def test_object_ids_match_published_git_vectors():
+    assert release_identity._object_id(b'blob', b'') == 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
+    assert release_identity._object_id(b'blob', b'hello\n') == 'ce013625030ba8dba906f756967f9e9ca394464a'
+    assert release_identity._tree({}) == '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
+
+
+@pytest.fixture
+def installed(tmp_path):
+    repository = tmp_path / 'repository'
+    for name, data in FILES.items():
+        (repository / name).parent.mkdir(parents=True, exist_ok=True)
+        (repository / name).write_bytes(data)
+        os.chmod(repository / name, 0o644)
+    os.chmod(repository / 'applications/pkg/a.py', 0o755)   # one 100755 entry
+    env = git_env(tmp_path)
+    commit = commit_all(repository, env, '.')
+    root = (tmp_path / 'install').resolve()
+    for name in FILES:
+        if name.split('/')[0] in release_identity.TOPS:
+            (root / name).parent.mkdir(parents=True, exist_ok=True)
+            shutil.copy(repository / name, root / name)   # bytes and permission bits
+    subprocess.run([sys.executable, '-I', str(TOOL), str(repository), commit, str(root),
+                    str(root / release_identity.NAME)], check=True, env=env)
+    return root, commit
+
+
+def test_installed_tree_yields_the_commit_and_exact_paths(installed):
+    root, commit = installed
+    assert release_identity.verified_source(root) == (commit, [
+        'applications/__init__.py', 'applications/pkg-data.json', 'applications/pkg/a.py',
+        'backend/__init__.py', 'backend/b.py'])
+
+
+def test_installed_mode_reads_are_counted_without_sha256_hash_bytes(installed):
+    root, commit = installed
+    record = json.loads((root / release_identity.NAME).read_bytes())
+    work = Work()
+    release_identity.verified_source(root, work)
+    sizes = [(root / release_identity.NAME).stat().st_size] + [(root / p).stat().st_size for p, _, _ in record['entries']]
+    assert work.physical['build_read_operations'] == len(sizes)
+    assert work.physical['build_bytes_read'] == sum(sizes)
+    assert 'build_hash_bytes' not in work.physical
+
+
+@pytest.mark.parametrize('defect', DEFECTS)
+def test_any_divergence_refuses(installed, defect):
+    root, commit = installed
+    record_path = root / release_identity.NAME
+    record = json.loads(record_path.read_bytes())
+    entries = record['entries']
+    if defect == 'extra_pycache':
+        (root / 'applications/pkg/__pycache__').mkdir()
+        (root / 'applications/pkg/__pycache__/a.cpython-313.pyc').write_bytes(b'x')
+    elif defect == 'changed_byte':
+        (root / 'backend/b.py').write_bytes(b'B = 3\n')
+    elif defect == 'missing_file':
+        (root / 'applications/pkg/a.py').unlink()
+    elif defect == 'symlink':
+        (root.parent / 'b-copy.py').write_bytes(FILES['backend/b.py'])
+        (root / 'backend/b.py').unlink()
+        (root / 'backend/b.py').symlink_to(root.parent / 'b-copy.py')
+    elif defect == 'git_directory':
+        (root / '.git').mkdir()
+    elif defect == 'relocated':
+        record['install_root'] = str(root) + '-elsewhere'
+    elif defect == 'forged_commit_object':
+        record['commit_object'] = record['commit_object'][:-4] + 'AAAA'
+    elif defect == 'record_mode_flip':
+        # A record-only mode change alters the recomputed tree, so the tree gate refuses.
+        entries[-1][1] = '100755'
+    elif defect == 'consistent_byte_change':
+        (root / 'backend/b.py').write_bytes(b'B = 3\n')
+        entries[-1][2] = release_identity._object_id(b'blob', b'B = 3\n')
+    elif defect == 'consistent_drop':
+        (root / 'backend/b.py').unlink()
+        del entries[-1]
+    elif defect == 'unsorted_entries':
+        entries.reverse()
+    elif defect == 'duplicate_entry':
+        entries.append(list(entries[-1]))
+    elif defect == 'installed_exec_added':
+        # Record and tree stay valid; only the installed owner-execute bit differs.
+        os.chmod(root / 'backend/b.py', 0o755)
+    elif defect == 'installed_exec_removed':
+        os.chmod(root / 'applications/pkg/a.py', 0o644)
+    if record != json.loads(record_path.read_bytes()):
+        record_path.write_bytes(json.dumps(record).encode())
+    with pytest.raises(WorkflowInputError):
+        release_identity.verified_source(root)
+
+
+@pytest.fixture(scope='module')
+def matched(tmp_path_factory):
+    """One committed tree observed through both witnesses: same commit, bytes, interpreter, environment."""
+    base = tmp_path_factory.mktemp('matched')
+    checkout = base / 'checkout'
+    for top in release_identity.TOPS:
+        shutil.copytree(ROOT / top, checkout / top, ignore=shutil.ignore_patterns('__pycache__'))
+    for path in checkout.rglob('*'):
+        os.chmod(path, 0o755 if path.is_dir() else 0o644)   # deterministic modes on any source filesystem
+    env = git_env(base)
+    commit = commit_all(checkout, env, *release_identity.TOPS)
+    installed = (base / 'installed').resolve()
+    for top in release_identity.TOPS:
+        shutil.copytree(checkout / top, installed / top)
+    subprocess.run([sys.executable, '-I', str(TOOL), str(checkout), commit, str(installed),
+                    str(installed / release_identity.NAME)], check=True, env=env)
+    no_git = base / 'empty-path'
+    no_git.mkdir()
+    return checkout.resolve(), installed, commit, env, no_git
+
+
+def test_installed_identity_equals_git_identity_without_git(matched):
+    checkout, installed, commit, env, no_git = matched
+    git_side = probe(checkout, env)
+    installed_side = probe(installed, dict(env, PATH=str(no_git)))
+    assert (git_side['root'], installed_side['root']) == (str(checkout), str(installed))
+    assert 'nm_refused' not in installed_side and 'ct_refused' not in installed_side, installed_side
+    assert json.loads(git_side['nm'])['checkpoint'] == commit
+    assert installed_side['nm'] == git_side['nm']
+    assert installed_side['ct'] == git_side['ct']
+
+
+def test_checkout_with_release_record_refuses(matched, tmp_path):
+    checkout, installed, commit, env, no_git = matched
+    stray = tmp_path / 'stray-checkout'
+    shutil.copytree(checkout, stray, symlinks=True)
+    control = probe(stray, env)   # twin: the same copied checkout admits before the record appears
+    assert 'nm_refused' not in control and json.loads(control['nm'])['checkpoint'] == commit
+    shutil.copyfile(installed / release_identity.NAME, stray / release_identity.NAME)
+    result = probe(stray, env)
+    assert result.get('nm_refused') == 'WorkflowInputError'
+    assert result.get('ct_refused') == ['BUILD_IDENTITY_UNAVAILABLE', 5, 3]
+
+
+def test_writable_installed_root_without_bytecode_suppression_refuses(matched, tmp_path):
+    """Imports write __pycache__ into a writable tree before identity runs; the witness refuses it."""
+    checkout, installed, commit, env, no_git = matched
+    writable = (tmp_path / 'writable-installed').resolve()
+    shutil.copytree(installed, writable)
+    record = json.loads((writable / release_identity.NAME).read_bytes())
+    record['install_root'] = str(writable)
+    (writable / release_identity.NAME).write_bytes(json.dumps(record).encode())
+    clean_env = {k: v for k, v in env.items() if k != 'PYTHONDONTWRITEBYTECODE'}
+    result = probe(writable, dict(clean_env, PATH=str(no_git)), flags=('-I',))
+    assert result.get('nm_refused') == 'WorkflowInputError'
+    assert any(writable.rglob('__pycache__'))
<<<END L1 SUCCESSOR PATCH>>>

### A4. Proportionate future validation (prospective; no authority requested)

**Pre-commit (working tree with L1 applied; no commit needed):** all 20 cases in
`tests/applications/bounded_decision_workflow/test_release_identity.py`.
- The production-boundary cases build their own fixture commit from the working-tree bytes.

**Post-commit (clean committed executable scope; separate owner commit grant first):** regression
cases that compute the repository's real identity and would refuse on a dirty tree.

| Selected regression | Why it depends on the changed mechanism |
|---|---|
| `tests/checked_temperature/test_real_build_success.py` (6 cases) | real `ExecutableBuild` through the command entry point; it detects any change to the Git-mode derivation or wire |
| `tests/reassessment_profile/test_capture.py::test_production_capture_actual_build_exact_prior_and_measurements` | real `reassessment_build` → `measurement_build` identity inside capture; checks `build_bytes_read > 0` |
| `…::test_production_build_hash_accounting_matches_actual_calls` | pins `build_hash_bytes` equal to SHA-256-observed bytes, the counter semantics A3 preserves |
| `tests/measurement_profile/test_delivery_contract_mapping.py::test_supported_delivery_and_standalone_recomputation` | real `measurement_build.identity()` in delivery recomputation |

- **Dropped after review:** `test_production_root_capture_limit_precedes_build_work`, which monkeypatches
  the identity away and so does not exercise the change.
- **Excluded:** R1 and R3; the full suite; governed and S6 tests (those builders are unchanged); T1 command
  tests (they reach the build only through `ExecutableBuild`); harness tests.
- **Sequence:** these stay distinct steps, each with its own owner grant.
  1. Implementation (apply exactly; verify post-image hashes).
  2. Pre-commit validation (20 cases).
  3. Commit authorization.
  4. Post-commit regression (9 cases).
- **Stop conditions:**
  - any post-image mismatch;
  - any failure among the 20 cases stops before commit;
  - any regression failure stops and is retained; there is no repair under the same grant.
  - No retry beyond the granted attempts.
- **Estimates [EST], static, not measured:**
  - pre-commit: 1 pytest attempt, 20 instances, under 300 s (each of about 6 production probes hashes the
    distribution files);
  - post-commit: 1 attempt, 9 instances, under 300 s;
  - storage under 96 MiB of temporary fixture trees;
  - 1 driver each.

---

## Part B: maintained authoring contract

### B1. Build-bound input graph (traced from source; the historical helper was read, not run)

Sources:
- `checked_runtime.py`, `checked_cli.py`, `checked_selection.py`;
- `t1_records.py`, `t1_cli.py`, `t1_simulation.py`, `t1_workflow.py`, `t1_reassessment_handoff.py`, `t1_acquisition.py`, `t1_package.py`, `t1_contracts.py`;
- `checked_temperature_schemas.json`, `t1_companion_schemas.json`;
- pilot `gate-helper.py`, `PILOT-PROPOSAL.md`, `EXECUTION-RECEIPT.md`;
- `showcases/t1-positive/plan.py`, `retained-v3.json`;
- T1 contract v3 `CONTRACT.md` §3.13, §4.3, §7.2.

**Column key:**
- **Kind:** *static* = build-independent scenario material; *build* = depends on the build digest only;
  *output* = depends on actual preceding output.
- **Who:**
  - *S* = supplied premise;
  - *D* = mechanically derived;
  - *H* = externally authorized by a human (issuance);
  - *C* = computed by a maintained command.

| Object | Schema (owning file) | Producer → consumer (checks) | Required inputs | Build/identity bindings | Kind | Who | Earliest lawful point |
|---|---|---|---|---|---|---|---|
| Build wire | `ct.build.v1` (checked schemas :1153) | `ExecutableBuild.wire()` → `_permitted_build` (`checked_runtime.py:363-365`) in selection/reassessment/verify/replay; T1 preflight `J.producer_build == sha(build)` (`t1_records.py:261-274`); replay equality (:1007-1008) | committed or installed tree, environment | is the digest | build | C (never supplied) | after the code is committed or installed |
| Checked policy | `ct.policy.v1` (:3052; `permitted_builds` :3067, 1-8 entries) | policy owner → `admit` (:257-263), `_permitted_build`, T1 order 2 `J.captured_policy` equality (`t1_records.py:279`), verify/replay `policy.json` equality (:1002-1004) | limits, `unresolved_allowlist: []` (T1 requires empty, `t1_records.py:281`) | `permitted_builds = [digest]` | build | S/D, approved by the policy owner | after the build digest |
| Simulator policy S | `ct.t1-simulator-policy.v1` (companion :2822) | policy owner → T1 order 2 (`t1_records.py:268-298`); G scope | spec `simulator-policy.json` minus `x-unresolved`, plus `companion_schemas_sha256` | `permitted_producer_builds = permitted_checker_builds = [digest]` (:2831, :2840) | build | S/D, approved by the policy owner | after the build digest |
| Static scenario set | W `ct.t1-world.v1` (:3683), C `ct.t1-context.v1` (:1273), rule `ct.t1-simulator-rule.v2` (:2927; `RULE_SHA256`), preset `ct.t1-carrier-preset.v1` (:759; `PRESET_SHA256`), model `ct.model.v1`, plan P0 `ct.interpretation-plan.v1`, explanations H1/H2, baseline `nm.evidence.v1`, claim/declaration/item/review graphs | scenario owner → preflight orders 4-6, carrier derivation (`t1_acquisition.py:131-133`), selection and reassessment stages | retained bytes (W `13ec18…`, C `c29ebd…`, rule `529b18…`, preset `c6f0ca…`, others in the retained catalogue) | none | static | S (pinned) | any time |
| Selection request P | `ct.request.v1` (:3491) | proposer → `checked-selection-evaluate` (`checked_runtime.py:709-734`; `--expected-request-pin`) | static set, `as_of`, policy | references the checked policy | build | D (proposer record) | after the policy |
| A0 | `ct.authority.v1` (:912), role `local_evaluation_issuer` | **human** → `_selection_stage5` (`checked_runtime.py:737-746`) | target P, scope selection `[T1, T2]`, `valid` covering `P.as_of` | targets P | build | **H** | after P |
| Prior bundle B0 | 9 files, `ct.bundle-manifest.v1` (:1334) plus invocation, closure, derivation, applicability, `ct.selection.v1`, trace, build, policy | `checked-selection-evaluate` → every T1 command (`--prior-bundle`; `t1_records.py:299-304,324-329`; `t1_cli.py:117-119`), delegated `_intake_prior` (`checked_runtime.py:831-867`) | P, A0, objects | `build.json` = wire; `invocation.build`; derivation/selection `build_ref`; **manifest carries wall-clock `created_at_utc` and `filesystem`** (`checked_runtime.py:628-630,650-651`) | output | C | after A0 |
| X | `ct.execution-target.v1` (:2505), role `local_model_proposer` | proposer → T1 order 4 (`t1_records.py:321-334`), reassessment stage 5 (`checked_runtime.py:466-475`), carriage | **actual B0** manifest and selection refs, model, P0, T1, `inherited`, `instrument_id` | through B0 | output | D | after B0 |
| E | `ct.authority.v1`, role `local_execution_issuer` | **human** → order 3 (`t1_records.py:307-317`); reassessment window checks (`checked_runtime.py:448-450,492-495`) | target X, scope reassessment `[T1]`, `valid` covering the J window | targets X | output | **H** | after X |
| J | `ct.t1-simulation-target.v1` (:2685; `producer_build` :2734) | proposer → `--expected-target-pin`; preflight (`t1_records.py:70-75,176,261-269`) | refs to X, W, C, rule, S, checked policy; `producer_build`; `companion_schemas_sha256`; `t0`; 120 s window; resource bounds ≤ S maxima | `producer_build = digest` | output | D | after X and S |
| G | `ct.t1-simulation-permission.v1` (:2560), role `local_execution_issuer` | **human** → order 3 (`t1_records.py:308-320`) | target J; `execution_authority` E; `scope = J.{rule, simulator_policy, producer_build, captured_policy}`; `valid` | scope carries the build | output | **H** | after J and E |
| M (with O) | `ct.t1-producer-manifest.v1` (:1814), `ct.t1-producer-receipt.v1` (:1954), `nm.evidence.v1` O, DB/raw | `t1-simulation-run` (`t1_simulation.py:127-179`) → simulation-verify, prepare, evaluate | J, G, E, B0 | receipt copies `J.producer_build`; O's id derives from `digest(J)` | output | C; the M pin is custodied after the run (CONTRACT §4.4) | after G |
| R (+ reachable claim graph) | `ct.request.v1`, role `local_model_proposer` | proposer → `t1-reassessment-prepare` (`t1_cli.py:100-108`; `t1_reassessment_handoff.py:76-108`), delegated reassessment stage 5 (`checked_runtime.py:441-499`) | model, reassessment claim graph, policy, actual B0, X, `result` from **actual M**: `scalar = receipt.r`, `public_evidence = receipt.public_evidence`, window, E, P0; no free objects | through B0 and M | output | D | after M is verified |
| H | `ct.t1-handoff.v1` (:1658) | `t1-reassessment-prepare` (`t1_workflow.py:55-73`) → evaluate/verify | R, M, J/G/E, X, B0, prior pins, O | through its inputs | output | C | after R |
| A | `ct.authority.v1`, role `local_evaluation_issuer` | **human** → `_reassessment_stage5`; F `evaluation_authority`; workflow-verify `_intake_authority` (`t1_workflow.py:248-283`) | target R, scope reassessment `[T1]`, `valid` containing `acquisition.ended` (`checked_runtime.py:489-491`) | targets R | output | **H**, issued only **after H is checked** (pilot `gate-helper.py:582-584`; `plan.py:368-377`) | after H |
| F, reassessment bundle B | `ct.t1-workflow-receipt.v1` (:3540; `checker_build` :3543, `producer_build` :3623) | `t1-reassessment-evaluate` → workflow-verify; `checked-reassessment-replay` (same build) | H, A, objects | `checker_build = ref(wire)`; producer and checker are the same build, because order 2 re-runs in evaluate and verify and requires `J.producer_build == sha(current build)` (`t1_records.py:265`) [SRC] | output | C | after A |

**Findings that shape the contract:**
- Every object from the checked policy onward is build-bound. The policy, S and therefore P cannot be
  fixed before the actual build digest exists.
- **Authored records need attestation fields.** Every authored record requires `id`, `revision`,
  `predecessor` and `provenance{role, label, authenticated, basis}` (checked schemas
  `definitions.attestation`).
  - The policy and S allow only role `local_policy_owner`; X, P and R carry `local_model_proposer`.
  - Reassessment declarations and reviews (inside R's closure) are support judgements by
    `local_condition_declarer` and `local_evidence_reviewer`.
- From B0 onward, inputs depend on **actual** outputs. B0's manifest is not reproducible, because it
  carries a timestamp and a filesystem field. X, E, J, G, R and A therefore **cannot** be precomputed from
  the build alone.
- Producer and checker builds are the same build [SRC `t1_records.py:265`]. One installed release produces
  and checks.
- **The pilot helper is not suitable production code.** It imports test modules (`fx1`, `CAPTURE`, `Case`,
  `phase_graph`, `authority`, `REF_INST` …) from `tests.checked_temperature.fixtures` (imports at
  `gate-helper.py:228,318`) and monkeypatches a frozen seed (`:212-221`). Its ids (`xt-1`, `request-R`) and
  windows are fixture conventions (`:204-221,243-262`). It also authors human authorities (A0, E, G, A)
  synthetically. It was not invoked.
- The guarded `t1-simulation-prepare` (`t1_cli.py:17,31-36,69-70`; contract §4.3 :455-473) covers **one**
  point, between B0 and the run:
  - it **validates** X, J and a candidate `ct.build.v1` supplied by the proposer, and does not author them;
  - it checks the unpinned orders;
  - it emits two unissued `ct.t1-authority-template.v1` drafts (E, G) and four claim-core templates;
  - it never issues authority (§7.2).

### B2. Recommended entry point

**Alternatives:**
- **Complete `t1-simulation-prepare` as contracted.**
  - It is the right semantics for its one point: it validates proposer-supplied X, J and build, emits
    provenance-free E/G templates and never issues.
  - It does not cover the build policies, P/A0, R or A. Those would still need another mechanism (today,
    the test-fixture helper).
  - Stretching it across stages contradicts its contract (§4.2 fixes its arguments; its preflight needs a
    prior bundle).
- **Recommended [PROP]: one narrower maintained command, `t1-authoring-prepare`,** with a closed
  `--stage` enum over the five lawful preparation points.
  - It emits **provenance-free templates only**.
  - Each later stage verifies the **human-completed** records against the templates recorded earlier.
  - **Reason:** one owner module, one publication path and one refusal family, covering exactly the inputs
    the maintained commands consume, with no attestation written by the tool.
  - **Consequence: it is a semantic change, not a re-implementation of §4.3.** It prepares X and J
    templates rather than validating proposer-supplied ones.
  - **AU-1** is therefore a contract amendment naming §3.15, §4.2, §4.3, §10.3 and §10.4.

**Contract (proposed):**

**Name and ownership:**
- CLI `t1-authoring-prepare`; logic in a new `applications/bounded_decision_workflow/t1_authoring.py`.
- It is dispatched **before** the existing T1 parser: `cli.py` routes `t1-authoring-` ahead of `t1-`.
- Its usage, diagnostic and completion records are its own kinds, so the closed enums of
  `ct.t1-diagnostic.v1` and `ct.t1-completion-record.v1` and `SCHEMAS_SHA256 e6fef4ad…`
  (`t1_contracts.py:9`, checked against J/S `companion_schemas_sha256` at `t1_records.py:270-273`) stay
  untouched.
  - Adding a command or codes there would change the companion edition and every J/S.
- Under AU-1 the guarded `t1-simulation-prepare` **stays in the code and its enum unchanged**: still
  refused, and declared withdrawn by the contract amendment. A new companion edition is deliberately
  avoided.

**Template rule (closed):** every schema-required field of a templated record is exactly one of:
- (a) derived from a named field of a pinned, verified predecessor;
- (b) a fixed contract constant (for example `unresolved_allowlist: []` for T1, `t1_records.py:281`;
  `question_as_of = window.to`, `t1_records.py:70-75`);
- (c) a premise field supplied by the responsible human;
- (d) an attestation field (`id`, `revision`, `predecessor`, `provenance`) left **absent** in the template
  and completed only by the human role that owns the record.

There are no defaults. The exact field-by-field table is a required implementation-design artifact
(see B4). It is derived from the schemas, and is not invented here.

**Stages, inputs and outputs (closed):**

| `--stage` | Required inputs | Templates emitted (all provenance-free, unissued) |
|---|---|---|
| `policies` | `--scenario-dir`, `--expected-scenario-pin`, `--premises`, `--spec-dir` (pinned `simulator-policy.json` etc.) | checked-policy template, S template |
| `selection` | scenario; `--completed-dir` holding the policy-owner-completed policy, with `--expected-checked-policy-pin` and `--expected-policy-template-pin`; `--premises` | P template, A0 template |
| `simulation` | scenario; `--prior-bundle` with `--expected-prior-request-pin` and `--expected-prior-authority-pin` (completed P, issued A0); completed policy and S pins with their template pins; `--premises` | X template, J template, E and G templates (contract §3.13 shape), plus the reassessment claim-core templates (contract §4.3) |
| `request` | scenario; B0 plus pins; `--producer-package` with `--expected-producer-manifest-pin` (custodied M); completed J and issued E, G pins; `--completed-dir` with the human-authored reassessment claims, declarations, evidence items and reviews and their expected pins (AU-8); `--scratch-dir` (fresh workspace for M re-verification, `t1_simulation.py:182,198`) | R template only. Its `claims`, `declarations`, `evidence_items` and `reviews` lists are class (a), derived from those pinned inputs. |
| `evaluation-template` | `--handoff-package` with `--expected-handoff-pin`, `--expected-request-pin` | A template |

- **Conformance check:** each stage verifies every human-completed input against its earlier template.
  The completed record must equal the template plus attestation fields only (`AUTH_TEMPLATE_DIVERGED`
  otherwise).
- **Scenario index:** `ct.t1-authoring-scenario.v1` lists static objects by role and digest, supplied and
  pinned.
- **Premises:** `ct.t1-authoring-premises.v1` carries per-stage closed fields. The known set from the
  schemas:
  - **policies:** policy `limits`, `required_reviews_per_item`, and S `resource_maxima`/`record_caps` where
    not taken from the pinned spec;
  - **selection:** P `as_of`;
  - **simulation:** X `instrument_id`, `inherited`; J `t0`, the exact 120 s window, `logical_run_id`,
    `clock_rule` and resource bounds ≤ S maxima;
  - **request** and **evaluation-template:** none beyond the actual predecessor outputs.
  - **Never premises:** observations, θ/β/ε, evidence, declarations or reviews.
  - Authority `valid` windows are chosen at issuance by the issuing human, not by the tool.

**Common arguments:** `--output-dir` (must be absent); optional `--diagnostic-dir`; duplicate flags
refused; every pin is 64 lowercase hex.

**Outputs:**
- `<output-dir>/objects/templates/<64-hex>` (template objects);
- `<output-dir>/objects/static/<64-hex>` (scenario objects, byte-unchanged).

  These paths satisfy the existing `member_path` rule `(objects|evidence|receipt)(/[A-Za-z0-9_.-]+)+`
  (`t1_package.py:28`); no regex change is needed.
- `<output-dir>/authoring-manifest.json` (`ct.t1-authoring-manifest.v1`), written last.
- The outputs are **not** an objects directory: consumers refuse unreachable members
  (`UNREFERENCED_MEMBER`, `checked_runtime.py:134-136`; `SIM_REFERENCE_INVALID`,
  `t1_records.py:232-234`), and `checked-selection-evaluate` takes the request through `--request`
  (`checked_cli.py:35`).
- The human assembles each consumer's inputs from the completed records, the issued authorities and the
  static objects.

**Publication:** through `t1_package.Publication` (`O_EXCL`/`O_NOFOLLOW`, file and directory fsync,
`PARTIAL` marker; `t1_package.py:40-131`). This needs one change: its final-file allow-list
(`t1_package.py:51-53`) gains `authoring-manifest.json`.

`Publication` and `safe_new_dir` raise `SIM_OUTPUT_UNSAFE`, `SIM_PUBLICATION_INCOMPLETE` and
`SIM_REFERENCE_INVALID` internally (`t1_package.py:16-21,62,74,90,99,114`). `t1_authoring` catches these
and maps them to `AUTH_OUTPUT_UNSAFE`, so no SIM-family diagnostic leaks from the authoring command.

**Manifest contents:** stage; the computed build digest and its `ct.build.v1` reference; every input pin,
including the template pins of completed inputs; every output with role `template | static-unchanged`;
and the fixed statement "TEMPLATES ONLY; UNATTESTED; UNISSUED; no command has consumed these; no outcome
is asserted".

**Bindings:**
- The build digest is computed in-process by `ExecutableBuild` and never supplied.
- Predecessors are bound by custodied pins and re-verified with the existing verifiers:
  - B0 by `checked_runtime.verify` under the P/A0 pins;
  - M by the simulation-verify logic in the supplied scratch workspace;
  - H by `_intake_handoff`.

**Validation order and refusals:** these use the authoring family's own codes, in
`t1_authoring_schemas.json`.
0. argv (`AUTH_USAGE`);
1. output destination absent, with no symlink path (`AUTH_OUTPUT_UNSAFE`, wrapping the `safe_new_dir`
   rules);
2. current build (`AUTH_BUILD_UNAVAILABLE`);
3. bounded reads (`AUTH_RESOURCE_LIMIT`);
4. pins (`AUTH_PIN_MISMATCH`);
5. template conformance of completed inputs (`AUTH_TEMPLATE_DIVERGED`);
6. predecessor verification (`AUTH_PREDECESSOR_UNVERIFIED`);
7. premises (`AUTH_PREMISE_INVALID`);
8. derivation;
9. schema validation of each template against its record schema with the attestation fields excluded
   (`AUTH_SCHEMA_INVALID`);
10. publication (`AUTH_OUTPUT_UNSAFE` on failure, with `PARTIAL`).

The exit classes follow the T1 family's numbering. A pre-existing contract/code mismatch is disclosed
here, not fixed: CONTRACT §10.3 gives `SIM_OUTPUT_UNSAFE` exit 6, while the code uses 5
(`t1_package.py:16-21`).

**Bounds:** each input uses its existing reader's caps. Selection prior bundle ≤ 2 MiB
(`checked_contracts.py:26`); producer package under `t1_workflow.read_package`'s caps; scenario and
completed objects ≤ 196,608 B each and ≤ 64 objects; output ≤ 64 templates; one process, no subprocess.

**Existing destinations and partials:** an existing output refuses. A failure after creation leaves
`PARTIAL` plus the diagnostic. There is no implicit retry, overwrite or cleanup.

**Evidence:** on success, the manifest and templates; on failure, the diagnostic (code, order, target)
and `PARTIAL`; in both cases, the authoring completion line.

**Example shapes (inert; digests elided; no real attestation or authority):**

```json
{"schema":"ct.t1-authoring-premises.v1","stage":"simulation",
 "execution_target":{"instrument_id":"<supplied>","inherited":["<supplied>"]},
 "target":{"t0":"2026-10-05T09:00:00Z","window_seconds":120,"logical_run_id":"<supplied>",
           "clock_rule":"<supplied>","bounds":{"<each S maximum>":"<supplied, <= maximum>"}}}
```

```json
{"schema":"ct.t1-authoring-manifest.v1","stage":"simulation",
 "build":{"kind":"ct.build.v1","sha256":"<computed>"},
 "inputs":{"scenario":"<pin>","prior_bundle":"<pin>","prior_request":"<completed P pin>",
           "prior_request_template":"<P template pin>","prior_authority":"<issued A0 pin>",
           "checked_policy":"<completed pin>","checked_policy_template":"<pin>",
           "simulator_policy":"<completed pin>","simulator_policy_template":"<pin>","premises":"<pin>"},
 "outputs":[{"role":"template","kind":"ct.execution-target.v1","sha256":"<X template>"},
            {"role":"template","kind":"ct.t1-simulation-target.v1","sha256":"<J template>"},
            {"role":"template","kind":"ct.t1-authority-template.v1","sha256":"<E template>"},
            {"role":"template","kind":"ct.t1-authority-template.v1","sha256":"<G template>"},
            {"role":"static-unchanged","kind":"ct.t1-world.v1","sha256":"<W>"}],
 "statement":"TEMPLATES ONLY; UNATTESTED; UNISSUED; no command has consumed these; no outcome is asserted"}
```

### B3. Human authority and semantic boundaries

**The mechanism never:**
- writes attestation fields for any role (policy owner, proposer, declarer, reviewer, issuer);
- issues A0, E, G or A;
- approves policies or permissions for its own execution;
- manufactures customer or operator authority;
- adopts results;
- derives or edits observations, evidence, θ/β/ε, declarations, reviews or applicability premises:
  - R's `scalar` and `public_evidence` are copied verbatim from the custodied, verified M receipt;
  - reassessment declarations and reviews are human-authored support judgements (**AU-8**);
- re-pins historical requests or authorities;
- treats `historical_A_reference_only` or any authority for build `0fc2cd25…` as permission for a new
  build;
- states outcomes or exits that have not occurred.

**Human approval points, in order:**
1. **Policy owner:** completes and attests the policy and S templates and custodies their pins (identity
   question: AU-6).
2. **Proposer:** completes P.
3. **Evaluation issuer:** issues A0.
4. **After B0:** the proposer completes X and J; the execution issuer issues E, then G.
5. **After M is verified:**
   1. custody of the M pin;
   2. the proposer, declarer and reviewer roles supply the reassessment claims, declarations, evidence
      items and reviews (completed from the claim-core templates), and these are pinned;
   3. the `request` stage runs;
   4. the proposer completes R.
6. **After H is checked:** the evaluation issuer issues A.

**Binding:** each later stage accepts a predecessor only through its pin, the template-conformance check
and re-verification. The manifest records which completed records and issued authorities were consumed.

**Kept separate:** model derivations and applicability stay as supplied and are judged by the maintained
commands. Evidence stays synthetic.

### B4. First authoring implementation boundary (plan only; no code proposed yet)

**Files:**
- `t1_authoring.py` (new): stages, the template rule and conformance checking. It reuses
  `canonical_bytes`, `ref`, `sha`, schema validation, `checked_runtime.verify`, `t1_simulation.verify`,
  the `t1_workflow` intake functions and `t1_package.Publication`.
- `t1_authoring_schemas.json` (new; a separate file keeps `SCHEMAS_SHA256` stable, **AU-3**):
  - scenario index, premises and manifest;
  - authoring diagnostic and completion records;
  - templates for the policy, S, P, X, J, R and the reassessment claim cores;
  - an evaluation-authority template, or an extension of `ct.t1-authority-template.v1` (**AU-2**).
- `t1_package.py`: adds `authoring-manifest.json` to the final-file allow-list (one line).
- `cli.py`: routes `t1-authoring-`.
- Contract amendment (AU-1).
- `tests/t1_simulation/test_t1_authoring.py` (new).
- A versioned scenario set: static objects exported byte-identically from the retained catalogue, plus
  the scenario index. Its location is **AU-4**.
- **Required design artifact before coding:** the field-by-field template table, classifying every
  required field of each templated schema as (a) to (d).

**Contract and schema changes:** the AU-1 amendment and the new kinds above. No existing record schema
changes, and `SCHEMAS_SHA256` stays unchanged.

**Tests and evidence [PROP]:**
- determinism;
- one refusal per validation step, including `AUTH_TEMPLATE_DIVERGED` for a completed record that alters
  a derived field;
- templates never contain attestation fields, and the outputs never contain an issued `ct.authority.v1`;
- static objects byte-unchanged;
- the X and J templates, completed with synthetic test attestations, pass `t1_records.preflight(prepare=True)`.
  That runs orders 0-2 and 4-6, including `checked_runtime.verify` of B0, and skips order 3.

**Regression comparison:**
- With the pilot's retained build wire `0fc2cd25…`, retained B0 and M, and completion with the pilot's
  attestations as **labelled synthetic test premises** (CONTRACT §7.3), the derived (non-attestation)
  fields of completed P, J and R should equal those of retained P `f32c2ce2…`, J `11669422…` and
  R `5f72989d…`. The retained catalogue pins no separate policy digests, only `prior/policy.json`.
- **This is not an independent oracle.** It compares against the same lineage, which was authored with
  fixture conventions (ids, windows), and differences in convention are expected.
- Mismatches are reported and classified, not tuned away (**AU-5**).
- The independent checks are the schemas and the maintained preflights and verifiers accepting the
  completed records.

**Dependencies:**
- **Independent of L2.** Design and implementation can proceed in the development checkout through the
  labelled in-process build seam.
- **L1 is needed for installed use.**
- **An actual installed build is needed for:**
  - the real digest, and so the policy, S and P templates and everything after;
  - actual B0, M and H, including the `filesystem` value that `checked_cli.filesystem_of` records on the
    target;
  - the effect of the installed environment on M's DB and evidence bytes (sealed ID-3).

**Excluded:** issuance and signing tools, operator UI, multiple scenarios, and any change to evaluation
semantics.

**Remaining authoring decisions:**
- **AU-1:** new command plus contract amendment (§3.15, §4.2, §4.3, §10.3, §10.4), with the old command
  kept guarded and its enum unchanged (recommended); or complete the old command and keep two mechanisms.
- **AU-2:** evaluation-authority template kind.
- **AU-3:** separate schema file (recommended).
- **AU-4:** scenario set location.
- **AU-5:** evidence status and mismatch handling of the regression comparison.
- **AU-6:** policy-owner identity.
- **AU-7:** whether a maintained command may ever attest as `local_model_proposer`. Recommended no:
  templates plus human completion.
- **AU-8:** who authors the reassessment claims, declarations, evidence items and reviews, from the
  simulation-stage claim-core templates. The proposal makes them pinned human-authored inputs to the
  `request` stage, so R's reference lists stay template class (a).

**Estimate [EST]:** about 800-1,100 lines of code and about 50 test cases; 1 pytest attempt of about
50 instances, in under 300 s.

---

## Part C: K sequencing and attribution

**Correction:**
- Applying L1 adds untracked files and modifies `measurement_build.py`.
  - That makes `git status --porcelain --untracked-files=all -- applications backend` non-empty, so
    K's empty-status expectation (judge `kj2_queries`/`query_stdout`, `k-judge.py:303-320`) would fail and Git-mode
    `ExecutableBuild` would refuse.
  - It also invalidates pinned source commitments: K's 1,923-row source manifest pins
    `measurement_build.py` `172efff4…` (derived from `PINS-CANDIDATE.sha256` row 1637), as does Route B
    `current_sources`.
- `git ls-files` (`LS_FILES` 245 lines, `27f787dc…`, `k-judge.py:70`) lists the **index**. It changes
  only when the index changes (staging or commit), not when an untracked file is added.
- This corrects the sealed PROPOSAL §8.

**Proposed owner disposition OD-K2 [PROP; not enacted here]:**
> Portability implementation (L1, and later the authoring work) may proceed in the working tree,
> notwithstanding the K amendment's "K precedes every commit" integration rule, which is suspended for
> portability work only. Historical K stays **unexecuted** and its sealed preparation stays preserved
> unchanged. Its premises remain bound to HEAD 07055c6, index 43dca87c and the pre-L1 source bytes.
>
> K is not run merely because its package exists, and it is not presumed to need re-preparation. Should
> a later owner decision require K, that decision states whether the pinned state is restored exactly
> or a successor is prepared for a specific need.
>
> The deferred status of K, R3 and D-COV is unchanged: nothing is passed or waived. D-P and D-W stay
> separately scoped. This disposition grants no application or commit authority by itself.

**Attribution:** R1's 141 accepted results keep their original tested-byte attribution and limitations.
No acceptance transfers to L1, the authoring work or the installed deployment. D-COV stays unenacted;
handoff stays deferred.

---

## D. Remaining owner decisions before implementation

| Decision | Status |
|---|---|
| ID-1 (refined, A1) | open; prerequisite of L1 |
| OD-K2 (C) | open; prerequisite of applying L1 |
| AU-1 to AU-8 (B) | open; prerequisites of authoring implementation |
| PD-1 to PD-4, ID-2, ID-3, ID-4, ID-7 | carried forward unresolved from the sealed package |
| Implementation, validation and commit grants | separate, not requested here |

## E. Review record

**Mechanism and restrictions:**
- Independent Claude Code subagents in this session; no CLI reviewer workload.
- Each was given the owner restrictions: no Git; no imports; no tests or collection; no execution,
  compilation or syntax checks of candidates, historical helpers or K scripts; no builds, installs or
  network; no probes; no file writes. Read-only `.git` file reads as data were allowed for the scope
  auditor.
- One read-only investigation agent traced the B1 input graph beforehand (source reads only).
- Reviews are not owner approval.

**Reviewers:**
- **RW:** code-reviewer, on source-witness semantics and production-boundary tests.
- **RB:** software-architect, on the authoring contract and authority boundaries.
- **RC:** evidence-integrity-auditor, on scope, sequencing, evidence and capacity.

**Bytes reviewed:**
- **Round 1:** addendum `612c53ca85487cd7910a2b63db8d3ad5371d30728ab899ca66453a8c5faa7a2c`, patch block
  `6a445cea…`.
- **Round 2:** `cb9371dc41400dff6cf05e8ac291ac20cefc1716c7395fa581268fad3b6f2eec`, block `7bf112ec…`.
- **Round 3 (RB):** `28b90f17039e8af8ad545804646bbb29a9d934a23d6629ae8d268e7671ae4faf`.
- **Final bytes:** these add only the approval-point-5 reordering (RB's Low point) and the filled §E and
  §F. The patch block is unchanged since round 2.

**Round 1:**

- **RW: NOT CLEAR (1 Major, 3 Minor, 5 Low).** All hashes were re-derived and agreed. Corrections:
  - **MAJOR:** `record_mode_flip` was caught by the tree gate, not the new mode gate, and the mode gate was
    untested → `installed_exec_added` and `installed_exec_removed` added; comment corrected.
  - the fixture depended on DrvFS 0777 modes → modes normalized before commit;
  - bytecode self-poisoning undisclosed → disclosed, and a bytecode test added;
  - F4 coverage list incomplete → extended, with "files listed in RECORD";
  - Git-weaker F2 cases → listed;
  - an unjustified regression case → dropped;
  - installed-mode accounting untested → test added;
  - no twin control for the stray record → added;
  - `lstat` gap, RecursionError, Git timeouts → `fstat` on the hashed descriptor, mapped, timeouts added.
- **RB: NOT CLEAR (5 High, 5 Medium, 2 Low).** Corrections:
  - closed T1 enums and `SCHEMAS_SHA256` → own AUTH kinds in a separate schema file; old command kept
    guarded with its enum unchanged;
  - `Publication` allow-list → change listed;
  - mixed refusal families → AUTH codes; the pre-existing `SIM_OUTPUT_UNSAFE` exit mismatch disclosed;
  - premises could not fill required fields → closed template rule (a) to (d) plus an expanded premise
    list, with the field table required before coding;
  - tool-written policy-owner and proposer attestation → provenance-free templates and human completion
    (AU-7);
  - "usable as objects-dir" → removed;
  - §4.3 overclaim → semantic change admitted, contract sections named;
  - M re-verification workspace and bounds → `--scratch-dir`, existing reader caps;
  - oracle honesty → relabelled as a same-lineage comparison;
  - declarations and reviews → human-authored (AU-8);
  - anchors → corrected;
  - installed-build list → extended.
- **RC: CLEAR**, with 4 Low advisories, all applied: §0 names the plan's `k_and_checkpoint_consequences`;
  the §2.7 correction is limited to the build-identity bullet; the Part C citation is 303-320; the final
  size is to be re-verified. It verified all seals, governing pins, absence of the candidate paths, and
  the capacity arithmetic.

**Round 2 readbacks:**
- **RW: CLEAR**, 9/9, with exact accounting counts confirmed. Residual notes, not defects: the bytecode
  test has no twin; `Work()` sets a context variable, as existing tests already do.
- **RB: NOT CLEAR on 3 new points**, all 12 earlier findings resolved:
  - N1: `member_path` regex → outputs under `objects/templates|static/`;
  - N2: internal SIM codes → mapped to `AUTH_OUTPUT_UNSAFE`;
  - N3: R reference lists outside the template rule → human-authored records become pinned `request`
    inputs; claim-core templates move to the `simulation` stage.
- **RC: CLEAR.**

**Round 3:** RB CLEAR on N1-N3. Its one Low ordering point in approval step 5 was applied in the final
bytes and was not re-read.

**Limitations:**
- No candidate was executed, compiled or syntax-checked, so the passing of all 20 tests is reasoned, not
  established.
- RW and RC did not re-read the round-3 Part B changes. RB did not re-read the final reordering.
- Intermediate addendum bytes are not retained; only their hashes are.
- Disagreements: none outstanding.

## F. Accounting

**Capacity:**
- **Unreserved preparation allowance before:** 1 file / 0 directories / 13,483,284 logical /
  28,315,648 allocated.
  - This is derived from the measured vertical-slice files and verified independently by RC.
  - No other new file appeared after that receipt.
- **Untouched:** the held application reservation and the conditional failure capacity.

**This addendum:**
- 1 file, 0 directories;
- logical 0075886 B, allocated 0077824 B (measured with `stat` after the final
  write, and written in at fixed width so the file length does not change);
- within the 262,144 B bound.

**After:** 0 files / 0 directories, with byte capacity reduced by the figures above. Any further
preparation file needs a new owner allowance.

**Not created:** no manifest, receipt, scratch file, directory, review file or memory note. The file's
SHA-256 is reported in chat, which avoids a circular self-reference.

**Separate scope:** host and session records, including 1 investigation and 3 reviewer subagent
transcripts. Process and time consumption are unknown, not zero.

**Not performed:** no implementation, source change, installation, build, test, collection, import,
candidate or helper execution, syntax check, probe, control change, signal, administrator action, Git,
staging, commit or merge.

END ADDENDUM
