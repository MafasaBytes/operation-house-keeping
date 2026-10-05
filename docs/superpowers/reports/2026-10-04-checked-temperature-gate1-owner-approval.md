# Checked-temperature Gate 1 — owner approval record

Date: 2026-10-04. This record transcribes the owner's Gate 1 approval, given in
the working session, so it does not live only in chat scrollback. It is a record
of the approval, not an acceptance of any result.

## Approved baseline (verified before any edit)

| Item | Value | Check |
|---|---|---|
| Package | `docs/superpowers/specs/2026-10-04-checked-temperature-contract-preparation-v3/` | — |
| `MANIFEST.json` SHA-256 | `1a9eccbd8b0191eac08b4677a087f7503ee934845425985b05686c179e1e5572` | recomputed, matches |
| Members | 10 | each SHA-256 and size matches; no extra files |
| v2 and original packages | `e7dbccec…0811`, `c3de4cb9…` | unchanged, members match |
| Corrected design v2 | `68da70f2…` | matches |
| Focused confirmation v2 | `f0259702…` | matches |
| Checkpoint HEAD | `2f0afbd368105b99f0b8548ffece107918386e3d` | matches |
| `.git/index` | `09ae83d4c39ead36e682600c851b5d355246c84708f8791080cc97b3183ff476` | matches |
| Pre-existing changes | `.gitignore` (`010b1010…`), `tests/reassessment_profile/bounded_pytest_runner.py` (`97999fad…`) | unchanged; preserved |

## Owner decisions

- **D1–D10:** accepted as proposed in v3 and its referenced decision definitions.
- **O3:** `observation_error_bound` gates both selection and reassessment.
- **O5:** claims bind the whole model revision.
- **A1:** the synthetic unresolved-use allowlist permits only
  `reference_calibration`, `reference_mapping` and `state_hold`, in their
  specified phases. It does not permit `observation_error_bound` or
  `indicator_fidelity`. Opposition and conflict always block.
- **G1:** approved.
- **G2:** approval and execution deferred.

## Gate 1 authorization (scope)

**In scope:**

- application-owned checked modules;
- dispatch integration;
- new tests under `tests/checked_temperature/`.

**Preserved unchanged:**

- legacy modules;
- existing tests and assertions;
- backend;
- dependencies;
- historical evidence.

**Not authorized:**

- Gate 2 or its witness driver;
- full suite or release qualification;
- physical acquisition;
- automatic adoption or reranking;
- staging, commits, remote operations or publication.

## G1 execution allowance

| Constraint | Value |
|---|---|
| pytest launches | at most 40 |
| Selection | `tests/checked_temperature/` and the five legacy files named in v3 `PLAN.md` |
| Workspace | fresh `--basetemp` per launch, under `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate1-tdd/` (ext4, new, outside historical qualification corpora) |
| Retained storage | 536,870,912 logical bytes, 20,000 files, 5,000 directories (cumulative). This is a storage allowance, not an address-space limit. |
| Recording | interpreter and environment bound before execution; each launch's arguments, outcome and usage recorded; failed attempts preserved; no cleanup; no allowance increase |

## Interpreter and environment binding (recorded before the first launch)

| Item | Value |
|---|---|
| Interpreter | `~/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python` (venv over `/home/mafasa/miniconda3/bin/python3.13`) |
| Version | CPython 3.13.11 (Anaconda build, GCC 14.3.0) |
| Base executable SHA-256 | `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264` |
| Installed distributions | exactly the ten pinned in `applications/bounded_decision_workflow/requirements.lock` (SHA-256 `7c87f0d7…0817`), including pytest 9.1.1 |
| Platform | Linux 5.15.167.4-microsoft-standard-WSL2, x86_64, glibc 2.39 |
| Workspace filesystem | ext4 (`/dev/sdc`, `/`) |
| Launch flags | `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`, `--basetemp=<workspace>/launch-NN` |

## Evidence boundaries

Gate 1 unit-test evidence is not executable-build qualification. Test doubles are
labelled explicitly. Gate 1 evidence is not final acceptance.

END OF GATE 1 OWNER APPROVAL RECORD
