# L2 release-commit review and accounting supplement

Date 2026-10-24. Preparation-only review for release-candidate commit `C`, plus a historical
accounting supplement.

**Not done:**
- nothing was staged or committed;
- no application, test, build, export, installation or K was run;
- no checkout, merge or push.

This file proposes; it enacts no owner disposition and authorizes no commit.

## 0. Summary

**Naming:** in this file, "commit `C`" means the release commit, called `C_rel` in the proposed
disposition. The regression integration plan on this branch has its own, unrelated group "C" (Codex
shared-controls consolidation).

- **Governing checkpoint:** `docs/superpowers/reports/2026-10-24-l2-n1-n5-hardening-validation-RECEIPT.md`,
  SHA-256 `1d8ec29dec1be4a70ec187a561dff763ee1c13eff25aac4051950f3602a9bba8` (verified):
  - affected stage 162/162 passed;
  - seven-module suite 305/305 passed;
  - no failures, errors or skips;
  - source and environment checks matched before, between and after the runs.

  That is a development checkpoint, not build, installation or installed-workflow acceptance.
- **Repository state (read-only Git with `--no-optional-locks`):**
  - branch `claude/t1-startup-chain-repair`, HEAD `07055c6357a049dba4599b527a1ce261ec529a2c`;
  - index empty of staged changes; `.git/index` SHA-256 still `43dca87c…`, last written
    2026-10-11;
  - 4 tracked modifications and 4,285 untracked files, not counting this file (4,286 with it).
    Nothing in the export roots is ignored.
- **Proposed commit `C`:** one commit of 33 paths (31 additions, 2 modifications), listed in
  section 1.
  - All 17 implementation, test, tool and runbook files equal the bytes frozen and verified by the
    305-test run.
  - The 16 records are documentation.
  - One optional, owner-selected addition (OD-C1, 3 test-data files) is listed separately.
- **Excluded and left untouched:** 2 tracked modifications and 4,255 untracked files.
- **Open owner decisions:**
  - OD-K2 applicability to `C` (section 5);
  - the integration plan's base (P/A/C/N/T/B/D) once `C_rel` moves this branch, or a separate
    branch (section 5);
  - OD-C1 (section 1.4);
  - the builder executable bit at commit time (section 1.5);
  - the `sitecustomize`/`usercustomize` build-admission policy (section 7);
  - OD-L2-B, the digest channel (still open).

## 1. Commit manifest

### 1.1 Included in `C`: the 17 implementation, test, tool and runbook files

Status codes: A = add (untracked now); M = modify (tracked).

**Exported into the release package** (builder `git archive C applications backend tools/release`;
`app/` holds `applications/` and `backend/`):

| St | Path | SHA-256 | Bytes | Why |
|---|---|---|---|---|
| A | `applications/bounded_decision_workflow/release_identity.py` | `2dfb4fca907ebd8dfc3c36dc22b27c93dfa0f98b5ddddffed65a69ddc2d28092` | 6,458 | L1 installed identity |
| M | `applications/bounded_decision_workflow/measurement_build.py` | `5c3619e4e9435bbc9ced21898bbb9806161dbab03a265f8221376ed574520267` | 4,987 | L1 installed path, without Git |
| A | `applications/bounded_decision_workflow/deployment.py` | `7ac1c842a085b5c259ee88de9b70d9075543464e4451567dc2dcb4cb38542323` | 12,747 | L2 admission A1–A7 (D2 fix) |
| A | `applications/bounded_decision_workflow/release_check.py` | `e0031ebdbb565a641ecff750e3c751154a92992636cf832ece939a4ccc543ccd` | 9,254 | L2 initialization and workflow entry |

**Exported only as builder/installer tooling** (`tools/release`, never placed in the release tree):

| St | Path | SHA-256 | Bytes | Why |
|---|---|---|---|---|
| A | `tools/release/build_release.sh` | `a352befd5ba310fbdacf4888ebf56d6e894a411b73288013836ef1f0fb3e56c2` | 14,256 | L2 builder |
| A | `tools/release/install_release.sh` | `fa11cb85287306fa373a1d6ffdfb1774afbaad4854e7b542eb402527f7dd8b1f` | 8,471 | L2 installer |
| A | `tools/release/release_manifest.py` | `c1d8bc7ad6c8981bff56845ea1e515c22492ff34e12dc1fb186d0f2a1f4bb4ff` | 36,478 | Manifest, archive, publish, portability (N5) |
| A | `tools/release/release_identity_record.py` | `b30a2cd8341fae2544e0f8ded48a90ab35cbe2ebf25cea73f3d08dfd9cfe6bf6` | 2,460 | L1 record writer (build host) |

**Committed, not exported** (tests, the rebinding tool, the runbook):

| St | Path | SHA-256 | Bytes | Why |
|---|---|---|---|---|
| A | `tests/applications/bounded_decision_workflow/test_release_identity.py` | `807b08edf51d4edad978623619337268ef933d89e5e7929cedf1613f4904825c` | 10,414 | L1 tests |
| A | `tests/applications/bounded_decision_workflow/test_deployment.py` | `dbc66dea1336b070b6d3921f8cdc78139328d647edaa363b0bd1c2e8b14ab2a5` | 17,796 | L2 admission tests (D3, N3) |
| A | `tests/applications/bounded_decision_workflow/test_release_check.py` | `06753aa48093a1f1d63e90be7ae0ea99fd55c89b4021d47c27ce95d46854875e` | 16,651 | L2 initialization and workflow-entry tests |
| A | `tests/tools/test_release_manifest.py` | `cf93169d1f4a5d95505f2ec33b03197bd29baed8a9687ff5014513549b4da6eb` | 42,151 | Packaging and portability tests (N2, N5) |
| A | `tools/fixtures/t1_rebind.py` | `180858b016b9f6c9459425a10acdb73c06250bc01713d492646b665684172831` | 68,871 | Option B rebinding tool; runs on the staging host from the repository |
| A | `tests/tools/test_t1_rebind.py` | `88147043aec497792ad6efa10d6dc5a875509c160eaf488014101e92ca6aeda7` | 73,374 | Rebinding tests |
| A | `tests/t1_simulation/request_fixtures.py` | `d17270ca20a508bba46cd2a1ed7be576eb3a76efb75781a1f4ee6c226bc92625` | 2,202 | Helper extracted unchanged from `test_maintained_increment.py` |
| M | `tests/t1_simulation/test_maintained_increment.py` | `a52277423c31427af5a979784a304fe2e8a28b2cb2d31a3425ce7ac48c395889` | 13,074 | The extraction (re-export, 38 lines moved) |
| A | `docs/deployment/README.md` | `fb9fc319d271599b98d065e00c44835776dfbf3c5f5952b2c2b65da09ea557d8` | 18,651 | Installed-release runbook (L2, Option B) |

- **Tested identity:** every row above equals its row in the 305-test run's
  `sources-before.sha256` (`8fe31b54…`), which matched at admission, between the stages and after
  (section 4).
- **Line endings:** none contains a CR byte. `.gitattributes` (`* text=auto eol=lf`) therefore
  leaves the committed blobs byte-identical.

### 1.2 Included in `C`: the 16 explanatory records (not exported)

| # | Path (`docs/superpowers/reports/`) | SHA-256 | Bytes | Role |
|---|---|---|---|---|
| 1 | `2026-10-21-t1-linux-ext4-l1-and-authoring-ADDENDUM.md` | `2957475768335f09685ac910c493b78c8dac9eb9c87825b63eaecd13a5d67e5e` | 75,886 | L1 design; ID-1; OD-K2 text |
| 2 | `2026-10-22-t1-linux-ext4-l1-implementation-RECEIPT.md` | `eb9c59aa0b65a83e6fc46e8eb4300000935b04f0e5369ea164740fe5fd39f7a7` | 4,190 | L1 implementation |
| 3 | `2026-10-22-t1-linux-ext4-l1-implementation-STATUS.json` | `b04e72447ab88907d14845f4fdebebbeeab39ee12a965c8f9a6de196a59523be` | 2,952 | L1 status |
| 4 | `2026-10-22-t1-linux-ext4-l1-implementation-ACCOUNTING.json` | `647f64a72540b4a97696521729ca45b04cb30854b50a7953c84c32c7379cf6fb` | 7,864 | L1 accounting |
| 5 | `2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md` | `74a39d87586b50e91fb5862579f28c02f86c498a6fa69e02bfb97e487d059a1b` | 43,038 | L2 design |
| 6 | `2026-10-22-t1-linux-ext4-l2-scope-finalization-ADDENDUM.md` | `6bca403bf936cf47da0eea373af8b587578a4b995d2b6ffdd7cb48fb1b77425e` | 36,340 | L2 scope |
| 7 | `2026-10-22-application-end-to-end-acceptance-and-l2-reconciliation.md` | `7d8bff11889078b99ce927f1977459862a88b2f1f840136ddff54c9858dd4b42` | 21,043 | Option B selection; OD-K2 question |
| 8 | `2026-10-22-t1-rebind-implementation-specification.md` | `42d92411d35a3d7764930ac8867329e643e3442d95dba07f2789316b03a4ff61` | 69,328 | Rebinding specification |
| 9 | `2026-10-23-t1-rebind-implementation-RECEIPT.md` | `bce045ac5a98aed9316266062934cf5ff3e42d0a877bbc32f983ebab259efe28` | 6,170 | Rebinding implementation |
| 10 | `2026-10-23-t1-rebind-correction-and-validation-RECEIPT.md` | `db6dbf8ba59b74bb49eba7e8f8d3f83758e3ef4ad974818b607b8ea5ec2e3f64` | 9,807 | Rebinding 107/108 |
| 11 | `2026-10-23-t1-rebind-codex-completion-RECEIPT.md` | `6e386e7a188d2bcfe8472b1a6aa4e48bccc31fa858e20772c644c4321fc09526` | 4,162 | Rebinding 108 |
| 12 | `2026-10-23-l2-option-b-implementation-RECEIPT.md` | `a99bbe921f5555dd2a019d0f5410fc0134c0942c99d4196337a6d62b56bf2cef` | 12,424 | L2 implementation |
| 13 | `2026-10-23-l2-development-validation-RECEIPT.md` | `dcbb227ff15dcee25221ce305251c3dede0503e989184bafd4744c0d046dd8a7` | 10,055 | Failed 255/36 run (kept as a failure) |
| 14 | `2026-10-23-l2-d1-d3-codex-validation-RECEIPT.md` | `ed6f37b34d78e0e35341fc67ab7b9a1c2422614d43f837f3ace4f0acaaba4083` | 6,616 | D1–D3 fixes, 291-pass run |
| 15 | `2026-10-24-l2-n1-n5-hardening-validation-RECEIPT.md` | `1d8ec29dec1be4a70ec187a561dff763ee1c13eff25aac4051950f3602a9bba8` | 13,394 | N1–N5, 305-pass run (governing) |
| 16 | `2026-10-24-l2-release-commit-review-and-accounting.md` | in its final receipt | — | This review; verified against the SHA-256 reported after section 8.1 was completed |

- **Why these records:** they explain the design, decisions, failures and validation chain behind
  the committed bytes.
- **Not included:** historical evidence workspaces, run outputs and the K package. Commit `C` does
  not need them to be coherent.
- **Absolute paths:** records 10 and 12–16 (at least) contain absolute local runtime paths
  (`/home/mafasa/...`) as evidence locators. They are documentation, not fixtures, and are never
  exported; the owner may want that noted at commit time.

### 1.3 Excluded and left untouched

| Group | Count | Reason |
|---|---|---|
| `.gitignore` (M, adds `/_to_delete/`) | 1 | Unrelated housekeeping |
| `tests/reassessment_profile/bounded_pytest_runner.py` (M) | 1 | R1/startup-chain work. Not in the 305-test import closure |
| `showcases/t1-positive/*` | 9 | K-amendment commit group P; governed by the K integration amendment |
| `tools/launch/*` | 4 | K-amendment commit group N and startup-chain work |
| `tools/administration/*`, `tools/qualification/bounded_launch.py` | 4 | Cgroup and launch facilities; separate history |
| `tests/reassessment_profile/*` (untracked) | 14 | Slice 5, T1-positive and Route B controllers; separate grants |
| `.claude/agents/*`, `.vscode/settings.json` | 7 | Developer configuration |
| Other `docs/superpowers/reports/**` | 3,976 | Historical packs, evidence and receipts: preserved, not shipped |
| `docs/superpowers/specs/**` | 176 | Includes the v3 package (see OD-C1) |
| `docs/superpowers/plans/**`, `docs/superpowers/proposals/**` | 65 | Separate planning history |

- **Totals:** 2 tracked and 4,255 untracked paths excluded. Nothing is deleted, cleaned or moved.
- **Caches:** `__pycache__/` and `*.py[cod]` are already ignored.
- **Runtime outputs:** these live outside the repository.

### 1.4 OD-C1 (owner choice): three test-data files read by already tracked helpers

- **The gap:** `tests/t1_simulation/admitted_fixtures.py`, tracked at HEAD `07055c6` and
  unchanged, reads three files from the untracked directory
  `docs/superpowers/specs/2026-10-09-maintained-t1-simulated-acquisition-contract-preparation-v3/`
  (127 files, `MANIFEST.json` `999966db…`).

  | File | SHA-256 | Bytes |
  |---|---|---|
  | `rule.json` | `529b18406a7daf8ed0218b72a12d031c7cca76c3fb0cc574b420da620dfb858b` | 4,504 |
  | `preset/preset.json` | `c6f0cafaed466ab8a18d3d7340632a9863d0526e4656b8311b8db55c96f03125` | 1,451 |
  | `simulator-policy.json` | `fdda9e4183c938a98d2be9345ba8bd38ddc26261eb0dcc02e4d5f8812e6f38cf` | 1,709 |

  All three were covered by the 305-test manifest.
- **Pre-existing:** the gap exists at HEAD already and is not introduced by L2. But a clean checkout
  of `C` could not run `test_t1_rebind`, `test_maintained_increment` or `test_command_integration`
  without these files.
- **Manifest rows:** `MANIFEST.json` carries two rows (predecessor and member) for each of the three
  files. The member rows match the current bytes; the predecessor rows for `rule.json` and
  `simulator-policy.json` differ.
- **Not approved:** the manifest lists `"commits"` under `not_approved`. Committing three files of that
  sealed package would be a partial import of it, which needs that explicit owner choice.
- **Options:**
  - **(a)** add exactly these three files to `C` as test inputs, stating that the package itself is
    not committed;
  - **(b)** leave them out and record a clean-checkout test limitation.
- **Recommendation:** (a). It does not affect the release export, `D_dev` or tested application
  behaviour.

### 1.5 File mode at commit (owner choice within the commit grant)

- `core.filemode` is `false`, so newly added files are recorded as 100644. All 245 tracked
  `applications/` and `backend/` blobs are 100644.
- The runbook (section 4) invokes `build_release.sh ...` directly. In a fresh checkout on the build
  host that fails with "permission denied" unless it is run as `bash build_release.sh`, which is
  how the tests run it. `install_release.sh` is invoked as `sh install_release.sh` and is
  unaffected.
- **Recommendation:** have the commit grant record `tools/release/build_release.sh` as 100755
  (index mode only). That changes no tested byte, no `D_dev` and no builder check, since tools are
  compared by content.

### 1.6 Release export boundary (inspected; rules unchanged)

- **What is exported:** `build_release.sh:100` exports only `applications backend tools/release`
  from `C`, so `git archive` exports tracked files only.
- **What enters the release:**
  - `app/` receives `applications/` and `backend/` (`:156`);
  - `tools/release` is checked against the running copy (`:106-111`) but never enters the release.
- **Builder refusals:**
  - `__pycache__` in `app/`;
  - group- or other-writable entries;
  - unsupported entry types;
  - symlinks outside `python/`;
  - `direct_url.json`;
  - non-locked distributions;
  - and now any `*.pth` file.
- **Consequences:**
  - historical packs, runtime outputs, `docs/`, `tests/`, `showcases/`, `.claude/` and `.vscode/`
    cannot reach the release;
  - the only developer-local content that could enter is a file committed under `applications/` or
    `backend/`. Commit `C` adds exactly three such files, all listed above.
  - Already tracked material is exported but does nothing in an installed release: the
    `backend/data_sources/testing/fixtures/*` files, and governed modules that read `docs/...` paths.
    `ohk-bdw-run` refuses those commands (`release_check.py:192`). This is not changed by `C`.

## 2. Commit proposal

**Title:** `Add L1/L2 installed-release portability, rebinding tool and validation records`

**Description (proposed):**

```text
L1: installed-release identity without Git (release_identity.py, measurement_build.py installed
path, release_identity_record.py) and tests.
L2: deployment admission A1-A7, release_check initialization and workflow entry, builder,
installer and release_manifest.py (manifest, archive, no-replace publish, portability incl. the
.pth rule), tests and the installed-release runbook.
Option B prerequisite: tools/fixtures/t1_rebind.py and tests; request_fixtures.py extracted
unchanged from test_maintained_increment.py.
Records: L1/L2 designs and receipts, rebinding specification and receipts, the failed 255/36 run,
the 291-pass and 305-pass development checkpoints, and the release-commit review.

All implementation, test, tool and runbook bytes equal the 305-test checkpoint
(receipt 1d8ec29d...). Development checkpoint only: no real build, installation, VM
qualification, installed-workflow run or provenance. K not executed (OD-K2). D-P open.
```

- **Shape:** one commit, recommended.
- **Why not split:**
  - the export roots must be committed together for `D_dev` to match, and the tests depend on the
    same tree;
  - splitting records from code would yield an intermediate commit whose code is tested but whose
    records are absent;
  - any split gives the release a different commit ID, so whichever commit is built becomes `C`.
- **Attribution:** separate commits would not change tested-byte attribution, which is per file.
- **Trailer:** the commit grant should end the message with the repository's required co-author
  trailer.

## 3. Package, release and evidence boundaries

| Class | Contents |
|---|---|
| 1. In commit `C` | Section 1.1 (17 paths), 1.2 (16 paths); optionally 1.4 (3 paths) |
| 2. Exported into the release package | `applications/`, `backend/` (248 files: the 245 at HEAD plus `deployment.py`, `release_check.py`, `release_identity.py`), with `measurement_build.py` modified; the built interpreter and locked wheels; `bin/` wrappers; `RELEASE-IDENTITY.json`; `RELEASE-MANIFEST.json`. `tools/release` travels separately as builder/installer tooling |
| 3. Evidence retained outside the package | The runtime validation workspaces (`.../test-workspaces/t1-l2-*`), R1 and rebinding evidence, and the historical reports not listed in 1.2 |
| 4. Unrelated work left untouched | Section 1.3 |

## 4. Tested-byte linkage

**Verified by the recorded manifests:**
- The 305-test run's `sources-before.sha256` (438 rows) covers every file under `applications/`,
  `backend/`, `tools/release/` and `tools/fixtures/`. It also covers the seven test modules, their
  static helper closure, `tests/conftest.py`, the package initializers, the schema JSON files,
  `requirements.lock`, `pyproject.toml`, the runbook, and the helpers' data inputs.
- All rows matched at admission, between the stages and after.
- Re-hashed for this review: every current file under `applications backend tools/release
  tools/fixtures` has an identical row in that manifest, and all 17 rows of section 1.1 match.

**Changed after the test freeze:**
- The only repository changes after the freeze are records: the N1–N5 receipt, and this file when
  created.
- No source, test, tool, configuration or runbook byte has changed.

**Documentation only:**
- The 16 records do not alter tested behaviour.
- No new test run is required merely for adding them.

**Missing source:** none for the release export or the 305-test closure, apart from the three
OD-C1 data files.

**Limited attribution:**
- **Interpreter and environment:** only the base executable is hashed (`47f615b1…`, through the
  venv symlink), plus the 1,266 R1 pins and a fresh native-library snapshot. The rest of the host
  is not covered.
- **Historical workspaces:** not scanned.
- **Prior checkpoint:** the 291-pass checkpoint keeps its owner-accepted N1 bridge limitation.
- **`D_dev`:** for the builder's `--expected-source-set`, I computed the working tree's source set
  read-only with an independent stdlib implementation of the recorded rule (sorted
  `[path, sha256, bytes]` of the non-`__pycache__` files under `applications/` and `backend/`,
  compact JSON, SHA-256):
  - result: 248 files, `D_dev = 6f2e9a576f901813b8b4b3845df58ba47c5cdb537bc413c715667eab070beb8d`;
  - this was not produced by `release_manifest.py source-set`. The builder's own computation is
    authoritative and refuses on any mismatch;
  - it differs from L1's tested 246-file set (`e6c9f2a3…`), so the build record will truthfully
    carry `l1_tested_source_set: null`.
  - The runbook (section 3, a committed tested byte) says `D_dev` is "recorded by the development
    test run (`release_manifest.py source-set`)". That is not satisfied: no development run recorded
    it. Before the first build, `D_dev` is to be taken from `release_manifest.py source-set` over
    `C`'s export, or the owner accepts this value. The builder fails closed either way.

**Why a commit ID needs new build-bound inputs:**
- The release's `RELEASE-IDENTITY.json` and `ct.build.v1` carry `C` as their checkpoint, so the
  build digest `B` is new.
- Every build-bound input (policy′ permitted builds, P′, A0′, simulator policy′, R′, A′) must
  therefore be rendered and approved for `B`, as runbook section 9 requires.
- Historical acceptances (R1, L1, synthetic end-to-end, rebinding 108, the development runs)
  remain attributed to their own bytes and builds. None transfers to `C`'s artifact.

**Prospective post-commit equivalence check** (specified here, not run; needs no export directory):
1. With `git --no-optional-locks -c core.fsmonitor=false`: `rev-parse C^{commit}`, and
   `diff-tree -r --raw 07055c6 C` lists exactly the approved paths. Check the modes with
   `ls-tree -r C`.
2. For every blob under `applications/`, `backend/`, `tools/release/` and `tools/fixtures/` in
   `git ls-tree -r C`, the SHA-256 of `git cat-file blob` content equals the corresponding
   `sources-before.sha256` row (computed in memory). The file set is the 248 + 4 + 1 tested files.
3. Extend that equality to every `sources-before.sha256` row whose path is in `C`'s tree. The set
   equality must hold both ways, so the clean-checkout closure is covered (helpers, `conftest.py`,
   `pyproject.toml`, `capture.json`, `tests/checked_temperature`, …). The only rows absent from `C`
   must be the v3 package files: 124 under OD-C1 (a), 127 under (b).
4. A stdlib computation of the source-set rule over those blobs gives `6f2e9a57…`.
5. `HEAD` equals `C` and nothing else was staged.

- **On mismatch:** stop, with no repair.
- **When further validation is needed:** only if a source or input actually changes, or a concern
  remains unresolved.

## 5. OD-K2 and commit governance

**K rule** (`2026-10-21-t1-k-accounting-admission-amendment-PROPOSAL.md` `bcba9f1a…`, AA2):
> the K sequence E1, E2, P3, E3-pre, E3, E4, E5, J1, run once, with no retry, fallback or
> repinning. K precedes every commit.

**OD-K2** (`2026-10-21-t1-linux-ext4-l1-and-authoring-ADDENDUM.md` `29574757…`; accepted for L1
per the L1 implementation receipt `eb9c59aa…`, "Authority: owner ID-1, OD-K2, and the revised L1
implementation only"; recorded for L2 in the L2 PROPOSAL `74a39d87…` row 80, "OD-K2, portability
before historical K | [ACC] | L2 proceeds; historical K stays unexecuted"):
> Portability implementation (L1, and later the authoring work) may proceed in the working tree,
> notwithstanding the K amendment's "K precedes every commit" integration rule, which is suspended
> for portability work only. Historical K stays **unexecuted** and its sealed preparation stays
> preserved unchanged. Its premises remain bound to HEAD 07055c6, index 43dca87c and the pre-L1
> source bytes. […] This disposition grants no application or commit authority by itself.

**Reconciliation** (`7d8bff11…`, section 5):
> […] OD-K2 grants no commit authority. Whether that suspension covers commit `C` needs explicit
> owner confirmation.

**Interpretation:**
- **Within the suspension:** commit `C` is portability work (L1 and L2), plus its records.
  Counting the Option B rebinding tool as portability work is an interpretation that needs the
  same confirmation.
- **Not covered by the text:** OD-K2's operative words authorize proceeding "in the working tree",
  and it expressly grants no commit authority. Whether the suspension extends to committing is
  therefore not settled by the text, and explicit confirmation is required.
- **Not in conflict with K groups P and N:** `C` touches none of the K integration amendment's
  group P or N paths (`showcases/t1-positive/record.py`, `tools/launch/t1_startup.sh`), so it does
  not conflict with that amendment's precondition, which governs those groups.
- **Consequence for K:** committing moves HEAD and the index away from K's pinned `07055c6` /
  `43dca87c`. K stays an unexecuted one-time witness. Any later K requires a decision on exact
  restoration or a successor, as OD-K2 already states.
- **Consequence for the integration plan:** the regression integration plan pins the same branch,
  head and index (`2026-10-21-t1-regression-and-integration/INTEGRATION-MANIFEST.json` `5fa28676…`:
  `head_ref refs/heads/claude/t1-startup-chain-repair`, head `07055c6`, index `43dca87c…`). Its
  commit groups P, A, C, N, T, B and D are kept by the K INTEGRATION-AMENDMENT `3e33ae07…`.
  Committing `C_rel` on this branch moves that plan's base. Those groups are not amended here; a
  later owner decision must re-base them on `C_rel` or place `C_rel` on another branch.

**Proposed owner disposition for the later commit grant** (not enacted here):
> **OD-K2-C.** The OD-K2 suspension of "K precedes every commit" extends to one portability
> release commit `C_rel` (L1, L2 and the Option B rebinding tool, with their records) on branch
> `claude/t1-startup-chain-repair` from HEAD `07055c6` [or on a named new branch from `07055c6`].
> K is not executed, waived or passed; its sealed preparation stays unchanged and bound to
> `07055c6` / `43dca87c`. K, R3 and D-COV keep their deferred status: nothing is passed or waived.
> D-P and D-W stay separately scoped. Committing moves the head and index pinned by the regression
> INTEGRATION-MANIFEST `5fa28676…` and its amendments. Their groups P/A/C/N/T/B/D are not amended
> here and need a later owner decision.
>
> **Scope:** exactly the 33 paths of
> `docs/superpowers/reports/2026-10-24-l2-release-commit-review-and-accounting.md`, sections 1.1 and
> 1.2 [plus the three OD-C1 paths of section 1.4, if (a) is chosen], staged by explicit path only.
> Every blob must be verified against the full SHA-256 recorded in sections 1.1, 1.2 and 1.4.
> Record 16 is verified against the SHA-256 reported in its final receipt, taken after section 8.1
> was completed. `build_release.sh` is
> recorded as mode 100755 [if section 1.5 is accepted]; every other path keeps 100644. No other
> path is staged.
>
> **Not authorized:** no K execution; no merge, push, tag, release publication, build, installation,
> deployment or VM provisioning. After the commit, run the section 4 equivalence check read-only and
> report; stop on mismatch.

**What `C` establishes:**
- **It does:** a content-addressed source identity, so a build from `C` can prove (L1 record,
  manifest) that its `app/` equals `C`'s tree.
- **It does not:**
  - who built an artifact, on what host, or from what inputs beyond those recorded;
  - signature (ID-2) or provenance (D-P stays open);
  - that any built artifact is correct.

## 6. Accounting supplement

**Historical supplement** (Codex D1–D3 grant; previously omitted; charged once, here):

| Item | Logical B | Evidence |
|---|---|---|
| `release_manifest.py` growth | +80 | 35,304 (receipt `dcbb227f…`) → 35,384 (receipt `ed6f37b3…`) |
| `deployment.py` growth | +114 | 12,633 (receipt `a99bbe92…`) → 12,747 |
| `test_deployment.py` growth | +266 | 15,302 (receipt `a99bbe92…`) → 15,568 |
| Codex completion receipt `ed6f37b3…` | 6,616 | Current size verified; content hash matches |
| **Total** | **7,076** | |

- **Not a double charge:** my N1–N5 receipt explicitly left this uncharged as an open item.
- **Historical allocated growth: unknown.**
  - It was not measured at the time.
  - **Reconstruction:** the recorded pre-edit allocations (`deployment.py` and `test_deployment.py`
    16,384 in receipt `a99bbe92…`; `release_manifest.py` 36,864 in `dcbb227f…`), set against the
    later N1–N5 bases and the receipt's current 8,192 allocated (16 × 512-byte blocks, hash
    unchanged), give an estimate x = 8,192.
  - **Why it stays an estimate:** the post-edit values in my earlier receipts were computed by
    4 KiB rounding on this drvfs mount, not measured, and the current allocation alone is not proof
    of historical growth. It is not charged as fact; the owner may choose to charge it on this
    basis.
- **Codex run workspace:** Codex's own post-run observation (78,088,904 logical / 130,678,784
  allocated) belongs to that run's separate test-workspace reservation and is not charged to this
  balance.

**This artifact:** 1 file, 0 directories. Its actual logical and allocated sizes are reported in
the final receipt (a file cannot contain its own hash).
- Allowance: 131,072 logical / 147,456 allocated.
- Charged separately from the supplement.

**Balances** (unreserved implementation/preparation):

| Step | Logical B | Allocated B |
|---|---|---|
| After the N1–N5 grant | 11,294,240 | 25,735,168 |

| Historical supplement | −7,076 | −unknown (estimate 8,192) |
| After supplement | **11,287,164** | **25,735,168 − x**, x unknown (estimated 8,192, giving 25,726,976) |
| This artifact | −(final receipt) | −(final receipt) |

Source of the N1–N5 row: the N1–N5 final chat report. It is the earlier balance 11,315,022 /
25,759,744 (D1–D3 validation report) minus (7,388 + 13,394) logical and (8,192 + 16,384) allocated.
Neither balance appears in a repository file; this table is now the file-first record.

- **Reserved vs consumed:** this grant's allowance is a ceiling; only actual usage is charged.
- No held capacity was borrowed and no spent reservation was reused. Earlier entries are not
  rewritten.

## 7. First-build prerequisites (material inputs only)

| Input | Status |
|---|---|
| Interpreter source | `Python-3.13.11.tar.xz` from python.org, with an expected SHA-256 supplied out of band. Not yet obtained or verified |
| Locked dependency artifacts | The ten wheels matching `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt` (`6bcc7bd8…`, tracked); a pip zipapp with its version and digest. Not yet obtained |
| Build tooling and native packages | The builder's `TOOLS` (git, tar, xz, make, gcc, ldd, readelf, python3, dpkg-query, …) and the noble `-dev` packages CPython needs. Package names unverified |
| Reference build environment | Ubuntu 24.04 amd64 build host or image, identity and digest; git present; `R_REL` and `--out` outside `/home` and `/mnt`. Not provisioned |
| Manifest-digest delivery channel | OD-L2-B: open |
| Startup-customization inventory | Proposed below; not implemented |

**Startup customization (proposal only):**
- **Proposed build admission:** before the first build is accepted, the operator inventories
  `sitecustomize.py`, `usercustomize.py` and any `sitecustomize`/`usercustomize` package anywhere
  in the built release tree, and stops if any is present unless the owner has listed it.
- **Expectation:** CPython `make install` and the ten locked wheels are expected to contain none.
  That expectation is not evidence.
- **Enforcement today:** the builder enforces only the `.pth` rule. Customization modules are not
  refused by code; implementing that would be a separate code change requiring its own grant and
  validation.

## 8. Focused review

Reviewer: one independent read-only `code-reviewer` subagent, limited to commit completeness and
exclusions, tested-byte linkage, export boundaries, OD-K2 applicability and accounting. It reviewed
the draft of this file. The corrections below were applied afterwards. **The final text was not
re-reviewed.**

### 8.1 Review record

**Confirmed:**
- every hash, size, count and arithmetic step in sections 1.1, 1.2, 1.3 and 6;
- `D_dev` (independently reproduced);
- the index and HEAD state;
- the export boundary;
- the K and OD-K2 quotes;
- that, apart from OD-C1, nothing in the 305-test closure or the release export is missing from
  `C`.

No Blocker.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| M1 | Major | The grant asked for verification against recorded SHA-256 values, but section 1.2 gave only prefixes and record 16 had no hash | Fixed: full hashes in 1.2; record 16 verified against its final-receipt hash |
| M2 | Major | The regression INTEGRATION-MANIFEST `5fa28676…` pins this branch, head and index, and has its own group "C" | Fixed: naming note (`C_rel`); consequence added to section 5 and OD-K2-C; a branch alternative offered |
| M3 | Major | The runbook says `D_dev` was recorded by the development run; it was not | Fixed: section 4 states the gap and how `D_dev` is to be fixed before the build |
| m1 | Minor | The equivalence check lacked modes and full manifest coverage | Fixed: `--raw` plus `ls-tree` modes; two-way set equality; expected v3 absences |
| m2 | Minor | Historical allocated growth could be reconstructed as 8,192 | Partly adopted: the reconstruction is recorded, but stays an estimate because the post-edit values were computed by rounding, not measured |
| m3 | Minor | The prior balance had no file-first source | Fixed: derivation stated |
| m4 | Minor | The Codex workspace observation was not mentioned | Fixed: stated as not charged here |
| m5 | Minor | The v3 manifest's `not_approved: commits`, and its predecessor/member rows | Fixed in 1.4 |
| m6 | Minor | OD-K2-C should mirror OD-K2's deferred-status wording, cite L2 PROPOSAL row 80, and flag the rebinding interpretation | Fixed |
| n1–n4 | Nit | Quote completeness, the untracked count including this file, inert exported material | Fixed |

## 9. Confirmations

- **No changes:** no index, source, configuration or historical-evidence change. The index hash
  after inspection is unchanged.
- **Git:** read-only only (`--no-optional-locks`; no external diff or text conversion).
- **Not run:** no application, test, build, export, installation or K.
- **Attribution:** R1's 141 results, the three deferred cases, scoped L1 acceptance and scoped
  synthetic end-to-end acceptance keep their attribution and limitations. D-P remains open.

END REVIEW
