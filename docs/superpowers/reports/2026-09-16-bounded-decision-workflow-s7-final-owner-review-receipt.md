# Bounded decision workflow S7 final owner-review receipt

S7 is ready for the owner's final application-acceptance decision within the
approved local ext4 scope. This receipt records verification readiness only.
**Final application acceptance is neither granted nor recorded.** No successor
work is selected. No tests were rerun to prepare this receipt.

## 1. Branch and exact revisions

| Item | Verified value |
| --- | --- |
| Branch | `brc-exp001` |
| S6 acceptance / S7 authorization commit | `e1293ad54c24211f5a651bb217a37c3635d7dea4` |
| Accepted S6 implementation/test commit | `c37c24ee50667121d6b2dc4739aa3b7d12825c96` |
| Exact S7 tested implementation/test HEAD | `64f4389b6d93484339afa29cbb7f7f21f6ef2758` |
| Current administrative HEAD | `64f4389b6d93484339afa29cbb7f7f21f6ef2758` |

There is no later administrative commit. The S7 code/tests/documentation are
committed through the tested HEAD; the completion report, evidence, updated plan
and this receipt are **uncommitted**. Nothing is staged. A later documentation
commit would create another Git build identity; replay of the recorded S7 bundle
still requires the exact tested HEAD.

Authority: [S6 owner acceptance](2026-09-15-bounded-decision-workflow-s6-owner-acceptance.md),
[plan §§7/9](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md),
and [design §§11–13](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md),
as amended by the accepted S3–S6 corrections and S6 terminal-policy resolutions.

## 2. Completion artifact identity

[Completion report](2026-09-16-bounded-decision-workflow-s7-release-completion-report.md):
`docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-completion-report.md`

- SHA-256: `4e90e82b56f1d25227c23506a80e18b43cdae62c183dfde1835bbd7349664aec`.
- Size: **10,052 bytes; 178 lines**.
- Title: “Bounded decision workflow S7 release verification”.
- Four sections, in order: “Tested scope and recovered checkpoint”;
  “Clean environment and verification”; “Runtime measurements and recoverable
  evidence”; “Preservation and acceptance boundary”.
- **No formal END OF marker is present.** The exact final nonempty line is:
  “S7 evidence is ready for the owner's separate final application-acceptance decision.”
  A final LF follows it. This is a documentation convention omission, not evidence
  of a missing test or a truncated artifact. The existing report is preserved
  unchanged; this receipt has an explicit ending marker.

[Recorded evidence](2026-09-16-bounded-decision-workflow-s7-release-evidence.json):
**52,086 bytes**, SHA-256
`8db348f00d36e1f75de3798b9f404cdb20d9a2141509a086402f57dd65f6747b`.
Its digest, seven-file archive, recorded build/source hashes and original JUnit
summary were inspected without executing the application test suite.

## 3. Verification scope and unperformed checks

**696 passed, zero failures/errors/skips, in 641.45 seconds** is an application
and affected-regression selection, not a full-repository pass:

| Selection | Passing checks |
| --- | ---: |
| Entire bounded-decision-workflow application test directory | 610 |
| Existing decimal-parser tests | 66 |
| Existing state-classification architecture tests | 5 |
| Existing semantic-compatibility isolation tests | 3 |
| Existing FL-001 reproduction tests | 12 |
| Total | 696 |

The 610 include three historical S6 conflict witnesses; those witnesses do not
alone prove policy resolution. The 28 S6 policy-resolution tests and command
tests supply the positive conformance evidence. Required application/public-contract
selection totals 684; the additional 12 FL-001 tests close earlier temporary-root
failures.

Completed: a fresh isolated CPython 3.13.11 environment, offline installation from
the retained hash-verified ten-wheel set, exact locked versions, a clean detached
checkout, and two further independent clones for cross-root replay/determinism.
This is one freshly recreated dependency environment shared by the independent
source roots, not two independently installed environments.

Not performed: a passing full-repository run at the final S7 HEAD, a CAD/PDF
all-extras run, XFS execution, a WSL reboot check, or a power-loss test. The earlier
broad run recorded 4,645 passes, four failures and 35 skips; its interrupted
successor has no completed result record. Neither is promoted to a full-suite pass.
All four earlier failed cases pass in the final 696-check selection.

No additional mandatory full-repository/all-extras or second-environment check
was found in the approved S7 scope. Design §12 calls for focused existing
public-contract/isolation checks; plan §7 nominates ext4 and 9p refusal.
CLAUDE.md's engineering workflow calls for the broader relevant suite, while
historical backend milestone statements about dual-checkout/full-suite verification
are not an additional S7 matrix row. No approved S7 environment check is omitted.

## 4. Complete approved acceptance-matrix trace

All **27** plan §7/design §12 rows have passing maintained evidence. File names
below refer to `tests/applications/bounded_decision_workflow/` and its recorded
passing test groups. S1–S4 are lower application-service/unit checks; S5 uses real
filesystem/process checks; S6/S7 add actual command subprocesses. This does not
claim every service-level variant was separately exercised through the CLI.

| Row | Passing evidence and scope |
| --- | --- |
| CMD-1 | `test_s6_cli.py` baseline evaluate/replay and `test_s7_release.py`; complete seven-file result, exact baseline and 22 review rows. |
| CMD-2 | `test_s6_cli.py`: usage, refused input, valid unavailable, no-feasible, collision and injected retention failure. |
| OBS-1 | `test_s1_input_public_admission.py`: exact public joins and decimal reparse; baseline command reaches admission. |
| OBS-2 | Same S1 file: all five unavailable forms, including public-producer twins and no fallback; S6 unavailable command. |
| OBS-3 | Same S1 file: nine corrected retarget/context/cutoff/revision/unit/index/forgery/decimal variants and valid twins; selected S6 precedence checks. |
| OBS-4 | Same S1 file: unsupported conversion refusal and interpreted-unit/source-lexeme positive twin. |
| NUM-1 | `test_s2_raw_projection.py`: exact endpoints, independent corners, floats/reversed intervals/correlations/digit limits. |
| UNC-1 | S2/S3 projection/policy tests and S6 command: widened beta interval with exact conditional outcomes. |
| UNC-2 | S2 missing/unknown support and stale refusal; S6 missing-support command. |
| POL-1 | `test_s3_target_and_policy.py`: complete feasibility table, unknown/incompatible and false-gate precedence. |
| POL-2 | S2/S3 gate and effect/precondition/timing/invariance twins; dependency does not supply an effect. |
| POL-3 | S3/S4 and S6 prior comparison: cost-only change, unchanged physics, plural tie, selection-only review. |
| POL-4 | S3/S4 and S6 prior comparison: target-only change, unchanged raw rows, required reevaluation and no-feasible result. |
| POL-5 | S3 independent hidden-completion oracle, missing/unknown costs, thresholds and ties; S6 missing-cost/tie commands. |
| REV-1 | `test_s4_decision_review.py` and S6 prior/replay tests: verified, reconstructed and recomputed prior; incompatible/forged prior refusals. |
| RES-1 | S1/S2/S4 independent counters and boundary twins; `test_s6_preflight.py`, S5 output boundaries and S6 incremental/no-partial-result tests. |
| RES-2 | S1/S6 equal/tighter limits and relaxation refusal; measured runtime/memory evidence. Observations are not a new latency/RSS hard limit. |
| PATH-1 | `test_s5_retention_recovery.py`: symlinks, traversal, FIFO, basename, manifest attacks, mutation/read-once and descriptor cleanup. |
| PATH-2 | Same S5 file: actual ext4 capture/publication primitives and actual 9p input/output-parent refusal. XFS is untested. |
| RET-1 | S5 file/directory/symlink collisions and injected occupied target; S6 collision command. |
| RET-2 | S5 two-process and S6 command concurrent publishers: one winner, one collision. |
| RET-3 | S5 each pre-manifest I/O-failure and real process-interruption boundary; incomplete material never promoted. |
| RET-4 | S5 directory/parent fsync failure and post-manifest death: complete-visible, durability unestablished; no false success. |
| RET-5 | S5 incomplete read-only inspection; S6 policy-resolution incomplete CLI behavior and new-path replay. |
| REP-1 | S6 recomputing replay and hash-consistent result/source/lock/Python attacks; S7 actual missing-source refusal/restoration. |
| REP-2 | S7 clean checkout/exact lock, historical S6 archive recovery at matching build and current-build rejection of that old build. |
| DET-1 | S7 two roots × seeds 1/7/313 × normal/reversed mapping construction: identical result/trace/build, enumerated manifest metadata differences. |

No approved matrix row is silently excluded. Qualifications: optional refusal
bundles are supported at the S5 API but not emitted by the CLI; the approved S6
resolution replaces incomplete CLI inventory with its fixed failure response.
The fixed 512-byte terminal failure allowance does not relax caller success or
retention budgets. The accepted fixture corrections and historical conflict
witnesses are not counted as independent new semantic scenarios. Platform and
physical-claim exclusions are stated in §7.

## 5. Command, build, recovery and determinism evidence

The recorded separate baseline subprocess sequence returned exit 0 for
evaluate/verify/replay, empty stderr, and one JSON stdout receipt each:

| Command | Elapsed seconds | Peak RSS KiB | Stdout bytes |
| --- | ---: | ---: | ---: |
| evaluate | 2.046 | 88,112 | 251 |
| verify | 1.209 | 82,436 | 146 |
| replay | 1.846 | 87,736 | 249 |

The twelve deterministic runs retain another twelve evaluate/verify/replay
sequences and complete semantic digests. S7 baseline result SHA-256:
`30032b1a86e94a13e3cff8274047bb9f7c1ad9287d36eef5accf049c20b1f775`;
trace SHA-256:
`3801a433cf38516072bf532eb34f1ff6068167b0e68f755bee8d2cb7f4ec0e1a`.
Result and trace agree across roots and replays. Manifest timestamps vary;
only the enumerated `created_at_utc`/`filesystem` run metadata is excluded from
the evaluate-manifest equality comparison.

Build identity SHA-256:
`d64e874a0e40ba2aff92971a86b80a8763f1f9bf073710fd8383edab146d8277`.
Verification is available without a matching executable; replay requires the exact
external source/interpreter/lock build and recomputes semantics. The old S6 archive
replays at its accepted commit and refuses at the S7 commit. Source removal refuses
S7 replay; restoration succeeds. The self-contained S7 evidence archive recovers
all seven exact files; it does not embed the source repository or interpreter.

## 6. User documentation and persistent-boundary example

The maintained [user README](../../../applications/bounded_decision_workflow/README.md)
documents the three commands, canonical input examples, output interpretation,
refusals, collision rules, offline reproduction and recovery. Its tested SHA-256 is
`1581e0bdb043aa3019091e07b5a80f795e407a091963dd782727504a2cdb7128`.
The complete request/snapshot examples and recoverable output/trace archive have
no omitted payload fragments.

The supported persistent root is
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`,
currently verified as `/dev/sdc`, ext4. The source may remain on DrvFS; inputs and
outputs must be on the supported local filesystem. The following is an unexecuted
reproduction recipe for owner use, not another claimed test. It uses new exclusive
input paths and new result basenames; existing data is never overwritten:

```bash
cd /mnt/d/operation-house-keeping
PYTHONDONTWRITEBYTECODE=1 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python - <<'PY'
from pathlib import Path
import os, subprocess, sys, uuid

source = Path.cwd()
assert subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == "64f4389b6d93484339afa29cbb7f7f21f6ef2758"
root = Path("/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow")
assert subprocess.check_output(["findmnt", "-T", str(root), "-n", "-o", "FSTYPE"], text=True).strip() == "ext4"
token = uuid.uuid4().hex
inputs = root / "inputs" / ("s7-review-" + token)
inputs.mkdir(mode=0o700)
for name in ("request.json", "snapshot.json"):
    wire = (source / "applications/bounded_decision_workflow/examples" / name).read_bytes()
    with (inputs / name).open("xb") as stream:
        stream.write(wire)
    (inputs / name).chmod(0o600)
result = root / "results" / ("s7-review-" + token)
replay = root / "results" / ("s7-replay-" + token)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
command = [sys.executable, "-m", "applications.bounded_decision_workflow"]
for args in (
    ["evaluate", "--request", inputs/"request.json", "--snapshot", inputs/"snapshot.json", "--output-dir", result],
    ["verify", "--bundle", result],
    ["replay", "--bundle", result, "--output-dir", replay],
):
    subprocess.run(command + list(map(str, args)), check=True, env=env)
print("Retained result:", result)
print("Retained replay:", replay)
PY
```

Expected interpretation: current condition `matches`, admitted T0=40, H_F raw
values 36/32/36/32 and H_H 42/42/32/32 in a0/aF/aH/aHF order, selected aH at cost 2,
and 22 review decisions. These are conditional synthetic conclusions.

## 7. Findings, exclusions and preservation

No unresolved implementation finding or unperformed required S7 check was found.
The receipt supplies the previously missing consolidated matrix and exact
administrative status. The missing formal completion-report ending marker is
disclosed, not silently invented. Tests were not rerun for formatting.

Verification is confined to local Linux/WSL CPython 3.13.11 with the ten approved
dependencies and ext4. XFS, nonlocal filesystems, cross-version migration,
power loss and reboot durability are not demonstrated. Manifest-last completeness
is not whole-directory atomic visibility or proof of power-loss durability.
Measurements are observed values, not service-level guarantees. Mathematical
consistency does not establish physical accuracy, causal truth, source authenticity,
global planning or actual actuation. IN-001 and CI-001 remain open and unselected.

Preservation was checked against the pre-resumption 919-file SHA-256 inventory:
only the intended plan edit differs; the other **918 existing files**, including
all **63 unrelated untracked artifacts**, remain byte-identical. Current source
hashes also match the recorded tested build and S7 changed-scope hashes.
No backend contract, application Python source or dependency-lock edit occurs
between accepted S6 and tested S7, or in the current worktree.

The authoritative `models/demo-printer/records` still has **36** files, unchanged
in that inventory, retaining
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`
(one FRG, one FLD, zero FLW). Recorded FL-001 checks also verify the exact
authoritative proposed gate read-only. No append, revision or ledger mutation.

The approved dependency artifact and persistent environment identities remain
those recorded in the completion evidence; no package installation occurred during
this receipt audit. The version-lock digest remains
`7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`.
Persistent `inputs/` and `results/` remain empty. All seven files of the accepted
S6 baseline under `test-workspaces/s6-resolved-gDqaVY/final/test_baseline_command_and_exac0/baseline`
were compared directly with its accepted archive and match exactly. Historical
test workspaces were not repurposed. This does not claim a new exhaustive checksum
census of every old disposable test artifact.

## 8. Exact Git status and owner stop

No commit, push, merge, reset, rebase, history rewrite, successor implementation
or acceptance record was created. The plan is the sole tracked modification.
The S7 completion report, evidence and this receipt are three untracked review
artifacts, alongside the 63 unchanged unrelated untracked artifacts. No staged
changes. `git diff --check` passes.

The following is the complete `git status --short --untracked-files=all` after
writing this receipt; all entries are preserved verbatim:

```text
 M docs/superpowers/plans/2026-09-15-bounded-decision-workflow-implementation-plan.md
?? docs/superpowers/proposals/2026-09-12-conditional-prediction-codex-lead-investigation.md
?? docs/superpowers/proposals/2026-09-14-model-derived-prediction-codex-lead-investigation.md
?? docs/superpowers/proposals/2026-09-15-bounded-decision-workflow-delivery-proposal.md
?? docs/superpowers/proposals/2026-09-15-one-step-intervention-projection-proof-design.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-candidate-assumptions-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-candidate-assumptions.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-complete-output-resource-correction-review.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-manifest-pre-hostile-target-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-manifest-pre-unknown-single-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-pre-hostile-target-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-pre-unknown-single-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-final-preexecution-closure-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-operational-cohort-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-operational-cohort.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-pending-parent-inputs-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-pending-parent-inputs.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-preexecution-rehearsal-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-redesigned-execution-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-redesigned-preexecution-rehearsal-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-request-carriage-redesign-investigation-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-resource-calibration-continuation-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-resource-guards-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-resource-guards.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-satisfied-governing-premise-discrepancy-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-discrepancy-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-manifest-pre-hostile-target-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-manifest-pre-unknown-single-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-manifest.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-pre-hostile-target-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-pre-unknown-single-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-structural-read-matrix-pre-hostile-target-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-structural-read-matrix-pre-unknown-single-correction.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-structural-read-matrix.json
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-unknown-single-output-correction-report.md
?? docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-unknown-single-output-discrepancy-report.md
?? docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-candidate-package-manifest.json
?? docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-candidate-package.json
?? docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-preexecution-rehearsal-report.md
?? docs/superpowers/reports/2026-09-12-brc-exp001-slice-a-completion-report.md
?? docs/superpowers/reports/2026-09-12-brc-exp001-slice-a-output-resource-amendment-report.md
?? docs/superpowers/reports/2026-09-12-conditional-prediction-codex-lead-investigation-challenger-audit.md
?? docs/superpowers/reports/2026-09-13-conditional-prediction-comparative-proof-candidate-manifest.json
?? docs/superpowers/reports/2026-09-13-conditional-prediction-comparative-proof-candidate-package.json
?? docs/superpowers/reports/2026-09-13-conditional-prediction-comparative-proof-final-execution-report.md
?? docs/superpowers/reports/2026-09-13-conditional-prediction-comparative-proof-preexecution-report.md
?? docs/superpowers/reports/2026-09-14-model-derived-prediction-candidate-manifest.json
?? docs/superpowers/reports/2026-09-14-model-derived-prediction-candidate-package.json
?? docs/superpowers/reports/2026-09-14-model-derived-prediction-codex-lead-investigation-challenger-audit.md
?? docs/superpowers/reports/2026-09-14-model-derived-prediction-independent-review.md
?? docs/superpowers/reports/2026-09-14-model-derived-prediction-preexecution-report.md
?? docs/superpowers/reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md
?? docs/superpowers/reports/2026-09-15-bounded-decision-workflow-implementation-readiness-report.md
?? docs/superpowers/reports/2026-09-15-bounded-decision-workflow-persistent-environment-report.md
?? docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-manifest.json
?? docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-package.json
?? docs/superpowers/reports/2026-09-15-one-step-intervention-projection-independent-review.md
?? docs/superpowers/reports/2026-09-15-one-step-intervention-projection-preexecution-report.md
?? docs/superpowers/reports/2026-09-15-post-experiment-objective-and-architecture-consolidation.md
?? docs/superpowers/reports/2026-09-15-source-agnostic-backend-gap-assessment.md
?? docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-final-owner-review-receipt.md
?? docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-completion-report.md
?? docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-evidence.json
?? docs/superpowers/specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md
```

Stop here for the owner's separate final application-acceptance decision.

END OF BOUNDED DECISION WORKFLOW S7 FINAL OWNER-REVIEW RECEIPT
