# L2 D1-D3 corrections and Codex development validation

Date: 2026-10-23 (Europe/Amsterdam). The owner authorized D1-D3 fixes, the affected modules first, then the seven-module suite if they passed. Claude's independent adversarial validation is a subsequent activity and has not been performed by this receipt.

## Changes

Only three existing files changed:

| File | Correction | Final SHA-256 | Bytes |
|---|---|---|---:|
| `tools/release/release_manifest.py` | D1: rename both dependency helper path parameters to `candidate_path`, allowing diagnostic `path` metadata without duplicate-argument errors. Preserve diagnostic keys and dependency rules. | `1b42b6b32aa30035e4c14b0ce261be8643a439d4d04a129807c2b7de9d4baac2` | 35,384 |
| `applications/bounded_decision_workflow/deployment.py` | D2: fstat and validate the opened descriptor before wrapping it as a stream. Expected I/O failures map to CONFIG_INVALID; a finally block closes the descriptor even on refusal. | `7ac1c842a085b5c259ee88de9b70d9075543464e4451567dc2dcb4cb38542323` | 12,747 |
| `tests/applications/bounded_decision_workflow/test_deployment.py` | D3: use AST Import/ImportFrom nodes rather than line prefixes. Docstrings no longer masquerade as imports; relative imports remain prohibited and the exact stdlib-import assertion remains. | `3c2fc51824031c99ac2efabb2d1e1977b25db96b9a2e52eed9bf86878e451a87` | 15,568 |

The initial hashes were inspected and matched Claude's reported checkpoint. No unrelated repair or test assertion weakening was performed.

## Execution and results

Existing interpreter: `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python`.

The interpreter's executable bytes were hashed before and after and matched `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`. This run did not reverify the full historical environment pin set. Test headers and captured commands provide additional environment attribution; this is not an independent environment qualification.

Two sequential authorized pytest invocations, with no failed-run retry:

1. Affected modules: `test_deployment.py` and `test_release_manifest.py`: **148 passed in 4.67 seconds**, exit 0.
2. The seven selected modules: **291 passed in 215.15 seconds**, exit 0.

| Suite module | Passed |
|---|---:|
| `tests/applications/bounded_decision_workflow/test_deployment.py` | 44 |
| `tests/applications/bounded_decision_workflow/test_release_check.py` | 15 |
| `tests/tools/test_release_manifest.py` | 104 |
| `tests/applications/bounded_decision_workflow/test_release_identity.py` | 20 |
| `tests/tools/test_t1_rebind.py` | 80 |
| `tests/t1_simulation/test_maintained_increment.py` | 13 |
| `tests/t1_simulation/test_command_integration.py` | 15 |

No failed, error or skipped cases were reported. Timings above are pytest's reported durations; clock-source differences previously observed on this host are not explained or independently qualified here. Per-process elapsed/resource data is retained separately.

Both invocations used a clean environment, plugin autoload disabled, `-I -B`, a fresh workspace-specific pycache prefix, `-c /dev/null`, explicit repository pythonpath, cacheprovider disabled, fresh basetemp, verbose output and JUnit capture. Each was bounded by timeout TERM at 600 seconds/KILL after 3, 2 GiB address space, disabled core dumps and 16 MiB per-file limits. No timeout fired. Fixture-local Git operations occurred only as required by selected tests. No maintained-repository Git command was run.

## Evidence and attribution

Fresh native runtime workspace:

`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-l2-codex-validation-20261023-1`

Commands are recorded in `commands.log`; the source identities were frozen before the affected invocation and checked before the full suite and afterward.

| Evidence | SHA-256 |
|---|---|
| `source-before.sha256` | `09305a770fe5662ef69c39b20bd46ff403daae0b98d8119b482d65ea38fa0775` |
| `application-before.sha256` | `eafe5a99f9990d0d5de89dcd6b325a56b6485c6ab6a7d376ed164f20c9e78066` |
| `interpreter.sha256` | `10997260977429da12b02647255aba3e4a7f25d9dd67f38654b63cfa57581592` |
| `commands.log` | `ba05de845f84d656872bb6a05bf174df78aea63ef725be08eb4b46305ffec727` |
| `affected-junit.xml` | `56ede7bff1e19ccdfbb7ad71137c339430b84dc128676c48fd7372b0142adc1a` |
| `affected.stdout` | `8a0a5dfe26394c1aa1e25296c9c9b0c7c6cedbdc349240ef1225dc7cce957cb2` |
| `suite-junit.xml` | `2e5393b9dc91b0602b568d90b3af91b0ee162ccc34dc58a5ef7cb1318592f61c` |
| `suite.stdout` | `1db2840a169cefe457d186c14dc81b7134bf60b0ca004cc68b56bf76753f1073` |
| `suite-time.txt` | `741b2d624776d2514668e1f3159be8449efcf651b1ed66ab5fb26e0f0c2d581c` |
| `final-preservation.txt` | `50382b5ac211c4dad27ef6cd46a289968abc9909e86fba75e7995781f394f354` |

Both stderr captures are empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`); both rc files contain 0. `evidence.sha256` inventories these and other command, timing and preservation records.

Preservation checks passed for the 13 explicitly named source/test/governing files, 195 application/backend Python source files and interpreter executable. This includes the original failed L2 receipt and the two frozen L2 design documents. Historical workspaces and arbitrary other repository files were not scanned; no complete preservation claim is made.

## Scope, accounting and remaining work

This is a passing focused development checkpoint, not a real CPython release build, root installation or VM qualification. No operational attestations or rebound runtime inputs were generated. No K, checkout, commit, merge, unrelated repair or standalone historical workflow run occurred. Existing failed-run evidence was preserved, not relabelled.

Corrected file growth totals 460 logical bytes (80 + 114 + 266), plus this new receipt. Allocated repository growth was not independently measured. A post-run workspace observation was 78,088,904 logical bytes including directory sizes and 130,678,784 allocated bytes; no peak-storage enforcement or measurement is claimed. Aggregate process counts, separate survivor scans and session overhead were not measured. None is treated as zero. This run did not reproduce Claude's full bounded admission/environment-preservation harness.

R1/L1 and synthetic historical end-to-end acceptances retain their original attribution and limitations; D-P stays open. Independent adversarial validation by Claude is next. No release commit or build is authorized by these results.

END RECEIPT
