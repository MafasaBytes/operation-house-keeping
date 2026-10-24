# L2 N1–N5 hardening and development validation receipt

Date 2026-10-24 (UTC). Grant: resolve findings N2–N5 of the independent L2 review, run the affected
modules, then the seven-module suite only if they passed.

**Outcome: passing development checkpoint.**
- **Affected stage:** 162 collected, 162 passed, no failures, errors or skips.
- **Seven-module stage:** 305 collected, 305 passed, no failures, errors or skips.
- **Checks:** every admission, between-stage and post-run check passed.

This is not a real CPython build, an installation, a VM qualification, an installed workflow run or
provenance.

**Preserved unchanged:** the Codex D1–D3 receipt `ed6f37b3…` (checked before editing and frozen),
the failed 255/36 receipt `dcbb227f…`, the L2 implementation receipt `a99bbe92…`, the 291-pass
evidence workspace, and the independent review, which was delivered in chat only.

## 1. N1 disposition (owner decision, recorded here only)

- The owner accepts the independent reviewer's historical/current-file attribution bridge for the
  prior 291-pass development checkpoint.
- That run's manifests did not cover all loaded source, configuration and environment inputs.
- The bridge supports attribution. It does not prove that no transient change occurred.
- The old result was not rerun and its receipt was not rewritten.
- This run captured its known input set before and after execution (section 4). A finite list does
  not prove complete host integrity.

## 2. N2–N5 changes

| Finding | Change |
|---|---|
| N2 | New `test_dependency_refusals_name_the_file_that_carries_them` (4 cases), through `rm.portability`. Asserts `detail` `where`, `path` and `value` for a shebang (`python/bin`, and `env` form in `bin/`) and for pkg-config (variable value and `-L` flag). Existing code and location assertions are kept. |
| N3 | New `test_a_configuration_fifo_refuses_promptly_without_a_writer`, and `test_the_configuration_descriptor_is_closed_after_every_outcome` with 4 cases: directory, FIFO, group-writable and admitted. |
| N4 | Runbook section 9 step 14 now gives all four replay flags. |
| N5 | New `PTH_FILE_PRESENT` refusal, plus 2 new tests (4 + 1 cases) and a runbook rule. |

**N3 detail:**
- The descriptor test tracks the loader's own descriptor through pass-through `os.open`/`os.close`
  wrappers, which are restored before the assertions.
- It asserts exactly one open, exactly one close and `EBADF` afterwards.
- A SIGALRM `deadline` ends a blocking call with `pytest.fail`, and restores the handler and timer.
- Production admission is unchanged.

**N4 detail:**
- The command is `--bundle <step-12 --output-dir>/bundle --expected-request-pin R′
  --expected-authority-pin A′ --output-dir /var/lib/ohk-bdw/work/replay`.
- R′ and A′ are the pins approved at AP-S3/AP-S4 and used in steps 12–13.
- The staging/VM identity-equality gate and the approval pauses are unchanged.
- This command has not been run from an installed release.

**N5 detail:**
- In `release_manifest.py` `portability`, the release tree is scanned once, after the test-package
  check.
- An absent or symlinked `python/lib/python3.13/site-packages` refuses as `EVIDENCE_MISSING`.
- Any entry named `*.pth` anywhere in the tree refuses `PTH_FILE_PRESENT`, whatever its type and
  even if hidden. There is no allowlist in the first release. Nothing is interpreted or deleted.
- An unreadable or rule-violating entry keeps scan's refusal; through the CLI, an `OSError` is
  `IO_ERROR` exit 1, and the builder then refuses `PORTABILITY_CHECK_FAILED`.
- The literal-findings loop reuses the same scan.
- The rule covers the `.pth` mechanism only: a `sitecustomize`/`usercustomize` module is not
  refused. This is stated in the code comment and the runbook.
- The builder changed by one comment line.
- Tests cover: an absolute entry, an executable `import` line, a relative entry, a hidden name, a
  symlink (`type == 'l'`), an absent site-packages, a non-0755 directory, and a text file mentioning
  `.pth`, which stays a literal finding only.

## 3. Focused independent review (read-only subagent)

| Severity | Finding | Disposition |
|---|---|---|
| Major | The FIFO deadline raised `TimeoutError`, an `OSError` subclass, which the loader turns into `CONFIG_INVALID`; a removed `O_NONBLOCK` would still pass after 5 s. | Fixed: the handler now calls `pytest.fail`. |
| Minor | A test comment called a 0700 directory "unreadable". | Fixed: reworded as a non-0755 directory refused by the scan rule. |
| Minor | `sitecustomize`/`usercustomize` also run at startup and are outside the `.pth` rule. | Wording narrowed. A refusal rule for them is left to the owner (section 7). |
| Nit | No symlink `.pth` case. | Added. |
| Nit | Refusal order changed: scan-rule codes now precede shebang/sysconfig/pkg-config codes. | Recorded. No test depends on the old order; the builder refuses on any nonzero exit. |

The review found no defect in the N2, N4 or N5 production logic, and no expected false refusal of
a real `make install` or of the locked wheels. No re-review followed these fixes.

## 4. Freeze and run

**Changed files (frozen; the expected-identity list matched at admission, between stages and
after):**

| Path | SHA-256 | Logical B (Δ) | Allocated B (Δ) |
|---|---|---|---|
| `tools/release/release_manifest.py` | `c1d8bc7ad6c8981bff56845ea1e515c22492ff34e12dc1fb186d0f2a1f4bb4ff` | 36,478 (+1,094) | 36,864 (+0) |
| `tests/tools/test_release_manifest.py` | `cf93169d1f4a5d95505f2ec33b03197bd29baed8a9687ff5014513549b4da6eb` | 42,151 (+3,294) | 45,056 (+4,096) |
| `tests/applications/bounded_decision_workflow/test_deployment.py` | `dbc66dea1336b070b6d3921f8cdc78139328d647edaa363b0bd1c2e8b14ab2a5` | 17,796 (+2,228) | 20,480 (+4,096) |
| `docs/deployment/README.md` | `fb9fc319d271599b98d065e00c44835776dfbf3c5f5952b2c2b65da09ea557d8` | 18,651 (+756) | 20,480 (+0) |
| `tools/release/build_release.sh` | `a352befd5ba310fbdacf4888ebf56d6e894a411b73288013836ef1f0fb3e56c2` | 14,256 (+16) | 16,384 (+0) |

`deployment.py` is unchanged at `7ac1c842…`.

**Manifests (taken at admission):**
- **Expected identities:** `n5-expected.sha256` `86d0aa81…`, 29 rows: the earlier 26 rows updated
  for the current files, plus the Codex receipt, the failed-run receipt and the R1 `PINS.sha256`.
- **Sources:** 438 files. That is the reviewer's earlier 292-file list (no removals; 5 rows changed,
  which are the five files above) plus 146 additions:
  - `applications/__init__.py` and the whole `applications/` tree;
  - the runbook;
  - the helper modules found by a static import closure (`tests/behavior_evaluation`,
    `data_sources`, `identity_binding`, `model_kernel`, `model_state`, `state_classification`);
  - the helpers' data inputs (`capture.json` and the v3 contract-preparation specification
    directory).

  Shell scripts, schema JSON files, `requirements.lock`, `tools/release`, `tools/fixtures`,
  `tests/conftest.py`, the package initializers and `pyproject.toml` are included.
- **Environment:**
  - the 1,266 R1 pin rows (venv, miniconda `python3.13`, standard library);
  - the interpreter, a venv symlink to `/home/mafasa/miniconda3/bin/python3.13`, `47f615b1…`;
  - a new observation, not a historical pin: 296 `miniconda3/lib/*.so*` entries, 101 of them regular
    files hashed;
  - pytest 9.1.1 and pluggy 1.6.0, with no `.pth` in the environment.

**Run:**
- **Workspace (fresh, native ext4):**
  `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-l2-n1n5-validation-20261024-1`.
- **Charge point:** creation of the workspace.
- **Harness:** `inputs/n5-validate.sh` `84885f98…`. Its own `bash -n` was run once before launch;
  no repository code was checked or probed.
- **Outer backstop:** `timeout -s TERM -k 3 947`.
- **Each stage:**
  - environment: `env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC HOME=<ws>/home TMPDIR=<ws>/tmp
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1`;
  - limits: `timeout -s TERM -k 3 {120|600} prlimit --as=2GiB --core=0 --fsize=16MiB -- time -v`;
  - interpreter: `cp313-bdw001/bin/python -I -B -X pycache_prefix=<ws>/<stage>-pycache`;
  - pytest options: `-m pytest -c /dev/null --rootdir <repo> -o pythonpath=<repo> -p no:cacheprovider
    --basetemp <ws>/<stage>-basetemp --junitxml <ws>/<stage>-junit.xml -o junit_family=xunit2 -v
    --tb=short -ra`;
  - `tests/conftest.py` was kept.

  The exact text is in `affected-COMMAND.txt` `fc8babe5…` and `suite-COMMAND.txt` `1c15aff2…`.
- **Timings (UTC):**

  | Step | Start → end | Duration | Result |
  |---|---|---|---|
  | Outer | 00:19:53.52 → 00:23:03.12 | 189.6 s | exit 0 |
  | Admission | — | 8.2 s | rc 0 |
  | Affected stage | 00:20:01.80 → 00:20:05.15 | `time -v` 0:03.33 | rc 0 |
  | Between-stage checks | — | 3.7 s | rc 0 |
  | Suite stage | 00:20:08.96 → 00:22:58.99 | `time -v` 2:50.02 | rc 0 |
  | Post-checks | — | 3.6 s | rc 0 |

  - Pytest itself reported 4.70 s for the affected stage and 180.88 s for the suite, longer than
    the wall clock.
  - The same divergence was seen in both earlier runs. It is recorded as an observation, not
    explained.
- **Signals and survivors:** none. No signals were delivered, both stderr captures are empty, no
  survivors were found and no cleanup signals were needed.
- **Peak RSS:** 102,332 kB (affected stage) and 125,272 kB (suite).

| Module | Affected stage | Suite stage | Earlier 291 run |
|---|---|---|---|
| `test_deployment` | 49 | 49 | 44 |
| `test_release_check` | — | 15 | 15 |
| `test_release_manifest` | 113 | 113 | 104 |
| `test_release_identity` (L1) | — | 20 | 20 |
| `test_t1_rebind` | — | 80 | 80 |
| `test_maintained_increment` | — | 13 | 13 |
| `test_command_integration` | — | 15 | 15 |
| **Total (all passed)** | **162** | **305** | **291** |

- The 14 new cases are N3 (5) and N2 + N5 (9).
- Test identities are unique, JUnit and verbose stdout agree, and there is no xfail, skip or
  deselection.

**Before/after checks, between stages and after the suite (all rc 0):**
- the 29 expected identities and the 438 sources, with an unchanged file list;
- the 1,266 environment pins, the native-library hashes and their listing, and the interpreter;
- the repository `__pycache__` listings: no change;
- the in-repo rebinding probe path stayed absent.

Historical workspaces were not scanned. Child-interpreter bytecode in unpinned locations was not
measured.

## 5. Evidence (workspace)

| File | SHA-256 |
|---|---|
| `affected-junit.xml` | `ca1f72a3dc7260595324fe127c62d5ffcea2dc18270c29fdc01d2e6def6d474f` |
| `affected.stdout` | `2e9b67bb2c3bdceae2c2e10aa87cee68c4e7a6cedbe1dababbe50f8a70bf0a94` |
| `suite-junit.xml` | `7d6f9f7fa560f65f1ae117d2d8fe6897e5dada8fef990cd0a7be9a4990501a2f` |
| `suite.stdout` | `859f2dacddd3bfc67aa157cfef55a2af524de608a1732c41d940bbd0018bd8e6` |
| `affected-time.txt` | `e74b98203cef76ce02d95a5203cd331d68e56fb4220e1189e02810337edee573` |
| `suite-time.txt` | `ab3943f8bd4116ea5053873dd71b4f70d0cbe235124a1aa74df8cb2f8205768f` |
| both stderr (empty) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `SUPERVISOR.log` | `abd7fba82fa8ddea75f230a74c114d4b5e1b8e1c98272d2af35b4328e1b456bd` |
| `admission.log` | `1a465771053b7aa7fad3ac2052e18d8832a3d22c26ea06c3a4e155f5d257de61` |
| `between.log` | `5dcc342ab50397722a9eba187f5e8999842dde4567e1b5d4eae9c74eb93e3b39` |
| `post.log` | `bb043300f02336414b4fdad89ed2510952af21517a4010abdb515b6fdbd61430` |
| `sources-before.sha256` | `8fe31b544b187b5eb95de9531b402729c43e547e9ea6768c55dff61d27ee699c` |
| `env-pins.sha256` | `795287f7d99d26ecd1f5ec48ea4ccc75c69047299cdde75747a6f110d3d3a12b` |
| `native-before.sha256` | `df1bb4afed1bd938f14a0816abaa4801965d806246522b6a17c9106d7757674a` |

## 6. Accounting

- **Correction growth:** +7,388 logical / +8,192 allocated (section 4 table), plus this receipt.
  1 new file, 0 new directories. The receipt's own sizes are reported in chat.
- **Test workspace (fresh reservation, observed, not quota-enforced):**
  - 11,187 files, 5,059 directories, 363 other entries;
  - 78,862,373 logical and 134,647,808 allocated bytes;
  - within 32,768 / 16,384 / 512 MiB / 1 GiB.
- **Not charged here:** Codex's D1–D3 growth (+460 logical plus its 6,616-byte receipt; its
  allocated growth was not measured). That remains an open accounting item for the owner.
- No held capacity was borrowed and no spent reservation was reused.

## 7. Deviations, open items and attribution

- **Deviation:** none from the authorized sequence. Both planned stages ran once, the second only
  after the first and its checks passed.
- **Disclosure:** the system `python3` read JUnit/stdout as data, and a static AST pass over the
  test files built the helper list. No repository code was imported or run outside the two pytest
  stages.
- **New defects:** none observed.
- **Open owner decision:** whether `sitecustomize`/`usercustomize` modules in the release should
  also refuse.
- **Claims:** this establishes a development checkpoint only.

R1's 141 results, the three deferred cases, scoped L1 acceptance and scoped synthetic end-to-end
acceptance keep their attribution and limitations. D-P remains open. No unrelated repair, retry, K,
maintained-repository Git command, checkout, commit, merge, real build, installation or provisioning
took place.

END RECEIPT
