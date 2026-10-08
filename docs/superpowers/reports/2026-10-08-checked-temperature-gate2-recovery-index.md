# Checked temperature Gate 2 recovery index

Gate 2 acceptance and preservation are separate statuses. Acceptance record v2 was hash-verified and preserved byte-for-byte at `docs/superpowers/reports/2026-10-08-checked-temperature-gate2-owner-acceptance-record-v2.md`, SHA-256 `9868857bd6c752fb0d2c1872e198e7e3ac65744af81a00a894e6faebc86104f5`. The owner recommends confirmation of this bounded record; its original draft and pending-confirmation wording is preserved, not silently changed into issued authority. The completed results remain 233 unique manifest IDs, four internal controls, two static checks and the recorded five-file L2 run (221 passed), with all original failures and coverage limits retained.

Preservation status: the authorized script and interpreter-byte preservation is complete locally, subject to the hash and sizing checks in the successor retention manifest. This does not establish repository-only recovery or portable execution.

## Local recovery map

| Dependency | Retention and limit |
|---|---|
| Gate 2 bulk evidence | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13`; successor `reports/gate2-retention-manifest-v4.json` enumerates regular-file hashes and literal symlink targets. Prior manifests and every existing file remain unchanged. |
| Volatile scripts | Missing copies now under `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13/recovery-preservation/scripts`; original driver reused at `metadata/driver.py`. Source and copy hashes match. The external `/tmp` originals remain in place. |
| Interpreter target | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13/recovery-preservation/interpreter/python3.13.target-bytes`, 32,003,680 bytes, SHA-256 `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`. This is a regular byte copy of `/home/mafasa/miniconda3/bin/python3.13`, not the venv symlink. Mode 0444 guards accidental writes; it is not an immutable archive. |
| Environment | Existing cp313-bdw001 environment, ten retained wheels, pyvenv.cfg and provisioning records are mapped by full hashes in retention v4. Standard library, dynamic libraries and OS environment remain external dependencies; the interpreter copy alone is not a runnable environment. |
| Source and fixture producers | Repository checkpoint `4d6ab13c46642e9771199dced7d312ac94bbbb2f`; 179 candidate-build source pins, frozen manifest sources and packet producer dependencies remain at their recorded paths. No new build identity was generated. |
| Gate 1 | Separate `ct-gate1-tdd` workspace, launch-log and historical launch-19 build `d81acac6f40f97670c23d08df15b3d1f568df5433bdb8ac3b55961f33d27f23c`; no consumption reset, transfer or bulk copy. |
| Preflight and memory control | Three named external preflight records remain hash-mapped; retained admin setup script explains the isolated cgroup. The cgroup requires administrator setup for a future launch and is not archival evidence or permission. |

The four absolute pytest symlinks are recorded literally, without following or changing them. Recovery to another location would require explicit target remapping. Bulk evidence has one local retention location; environment/provisioning and Gate 1 remain separate. Lost earlier harness versions and the unrecorded first L2 supervisor data remain missing exactly as disclosed in acceptance v2 and the cleanup disclosures. This step does not repair those gaps.

## Proposed commit scope

The exact machine-readable scope is [proposed commit scope](2026-10-08-checked-temperature-gate2-proposed-commit-scope.json): 16 named existing repository dependencies plus this index, the unchanged acceptance copy and the scope file itself, 19 paths total. Of the original 16, three already tracked package manifests remain unchanged; they are dependencies, not new changes. No broad directory selection is proposed. Frozen dependencies and historical labels follow.

| Path | Status |
|---|---|
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-consolidated-plan.md` | frozen execution dependency; unchanged |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-manifest.json` | frozen execution dependency; unchanged |
| `docs/superpowers/reports/2026-10-05-checked-temperature-gate1-owner-acceptance.md` | Gate1 acceptance; original no-execution-at-checkpoint statement is historical |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b/AMENDMENT.md` | superseded F1b package v1; v2 governs driver-bound fields |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b/inventory.json` | superseded F1b package v1; v2 governs driver-bound fields |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b/MANIFEST.json` | superseded F1b package v1; v2 governs driver-bound fields |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b-v2/AMENDMENT.md` | frozen execution dependency; unchanged |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b-v2/inventory.json` | frozen execution dependency; unchanged |
| `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b-v2/MANIFEST.json` | frozen execution dependency; unchanged |
| `docs/superpowers/reports/2026-10-08-checked-temperature-gate2-continuation-stop-report.md` | historical intermediate stop at F5a; later completion is separately recorded |
| `docs/superpowers/plans/2026-10-05-checked-temperature-gate2-consolidated-plan.md` | superseded pre-execution proposal; preserve original bytes |
| `docs/superpowers/plans/2026-10-05-checked-temperature-gate2-manifest.json` | superseded pre-execution proposal; preserve original bytes |
| `docs/superpowers/specs/2026-10-04-checked-temperature-contract-preparation-v4/MANIFEST.json` | already tracked frozen package dependency; unchanged, no new diff expected |
| `docs/superpowers/specs/2026-10-05-checked-temperature-contract-amendment-c1/MANIFEST.json` | already tracked frozen package dependency; unchanged, no new diff expected |
| `docs/superpowers/specs/2026-10-05-checked-temperature-contract-amendment-c2/MANIFEST.json` | already tracked frozen package dependency; unchanged, no new diff expected |
| `docs/superpowers/reports/2026-10-05-checked-temperature-scoped-commit-and-clean-build.md` | frozen-manifest source dependency and historical build report |

The owner-authorized preservation expands the historical three-file document path scope to these 19 named paths; the 1 MiB logical and 4 MiB allocated document byte ceilings are unchanged. No bulk workspace or interpreter bytes enter the proposed repository scope.

## Verification and boundaries

Standalone standard-library checks verified hashes, literal links, repository checkpoint and unchanged index/protected files. Before any copies, `reports/preservation-precopy-reservation.json` recorded measured usage and reserved copy plus manifest space. All new runtime copies and reports are charged to L1; L2 is untouched, and original-script/interpreter coexistence is included conservatively. Final `gate2-retention-manifest-v4.json` excludes only its own file from its recursive inventory and reserves 8 MiB for itself; its full digest is delivered separately.

No tests, application commands, identity generation, installation, launch, ledger mutation, staging, commit, deletion, publication or remote operation occurred. The exact copied interpreter bytes do not imply deployment, adoption, operational permission or portable execution.
