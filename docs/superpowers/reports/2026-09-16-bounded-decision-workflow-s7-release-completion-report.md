# Bounded decision workflow S7 release verification

S7 verification is complete at tested commit
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`. Final application acceptance remains
the separate owner decision established by the
[S6 acceptance and S7 authorization](2026-09-15-bounded-decision-workflow-s6-owner-acceptance.md).
No successor or backend extension is selected by this report.

## Tested scope and recovered checkpoint

The resumed checkout was branch `brc-exp001`, with no tracked modifications. The
interrupted session had already committed the S7 tests and documentation. This
continuation changes only this report, its evidence file and plan status.

Relative to S7 authorization commit `e1293ad54c24211f5a651bb217a37c3635d7dea4`,
the tested changes are exactly:

- `applications/bounded_decision_workflow/README.md`: offline environment,
  clean-checkout verification, exact-build recovery and narrow user instructions;
- `tests/applications/bounded_decision_workflow/test_s5_retention_recovery.py`:
  explicitly nominated unsupported input/output mounts for checks from ext4 clones;
- `tests/applications/bounded_decision_workflow/test_s7_release.py`: two clean
  roots, twelve constructions, real commands, historical recovery and build refusal.

Application Python source, backend, dependency lock and approved policies are
unchanged from accepted S6. Inspection found no application import of preparation
drivers or test oracles, and no acquisition/network path. Production file access
remains in the existing capture/retention/build boundaries.

The earlier `fresh-base-junit.xml` in persistent test workspace
`s7-release-o6VVgQ` records 4,645 passes, four failures and 35 skips. One failure
attempted the unsupported-output check from an ext4 checkout; commit `64f4389`
corrected its setup. Three FL-001 reproduction failures required paths beneath the
system temporary directory. That run is not a passing final release run. Its
later `final-green` attempt has no completed result record and is not counted.
All four failing cases are included in the completed current run below. The full
repository suite was not repeated; the required affected selection was completed.

## Clean environment and verification

The persistent provisioning verifier passed before and after verification:
ten retained wheel artifacts, artifact-set commitment
`26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`,
environment identity
`693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`.

A new CPython 3.13.11 venv was created with `--without-pip` under
`/tmp/bdw-s7-resume-CBFUxO`. The existing installer targeted that new environment
using the retained provisioning `requirements-hashed.txt` with
`--no-index --no-deps --only-binary=:all: --require-hashes`. Its inventory contains
exactly the ten approved versions. No dependency was fetched or changed.
The committed version lock SHA-256 remains
`7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`.

The exact tested commit was cloned independently with `--no-hardlinks` and a
detached checkout. Source, fresh environment and disposable test children were on
verified `/dev/sdc` ext4. The separately nominated unsupported mount was WSL 9p;
its isolated output-parent probe remained empty. Existing persistent input/result
directories were not used as test destinations. No XFS execution is claimed.

**696 passed, zero failures/errors/skips, in 641.45 seconds.** This comprises
684 required application/public-contract checks (including three retained historical
policy-conflict witnesses) plus all 12 FL-001 reproduction checks. The complete
per-module counts and pytest log are retained in the evidence file.

The command ran from the clean clone with bytecode disabled, user site disabled,
pytest cache disabled, a new ext4 `--basetemp`, and both unsupported-mount test
variables set:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
  BDW_UNSUPPORTED_FILE=/mnt/d/operation-house-keeping/applications/bounded_decision_workflow/examples/request.json \
  BDW_UNSUPPORTED_OUTPUT_PARENT=/mnt/d/operation-house-keeping/.bdw-s7-unsupported-NyMLTk \
  /tmp/bdw-s7-resume-CBFUxO/env/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/applications/bounded_decision_workflow \
  tests/constraint_evaluation/test_decimal_parser.py \
  tests/state_classification/test_architecture.py \
  tests/semantic_compatibility/test_isolation.py \
  tests/model_kernel/test_fl001_slice_d_reproduction.py \
  -q --basetemp=/tmp/bdw-s7-resume-CBFUxO/checks \
  --junitxml=/tmp/bdw-s7-resume-CBFUxO/verification-junit.xml
```

These paths identify the completed run, not reusable destinations. Reproduction
requires newly created paths; pytest can remove an existing basetemp.

The release cases exercise seeds 1/7/313, normal/reversed mapping construction,
two independent Git clones and distinct output times. All twelve evaluations,
cross-root verifications and recomputing replays agree on complete result/trace
bytes and build identity. Evaluate manifests differ only in the enumerated
`run_metadata` fields. Missing source refuses replay while verification remains
available; restoring it restores replay. The accepted S6 archive was extracted
into a new directory, verified and replayed at its matching historical commit;
the current commit correctly refused replay of that older build.

## Runtime measurements and recoverable evidence

A separate real baseline command sequence measured elapsed time and Linux
`wait4` peak resident set size. Every command returned 0, with one stdout JSON
line and empty stderr:

| Command | Elapsed seconds | Peak RSS (KiB) | Stdout bytes |
| --- | ---: | ---: | ---: |
| evaluate | 2.046 | 88,112 | 251 |
| verify | 1.209 | 82,436 | 146 |
| replay | 1.846 | 87,736 | 249 |

These are observations on this machine during concurrent test execution, not
new resource ceilings or timing guarantees. Suite peak RSS in the retained time
record includes the test harness and is not a per-invocation application limit.

An independent standard-library census checked each manifest's file digests and
sizes before counting JSON nodes (map/list/scalar; keys not additional nodes) and
depth (root one). The retained set includes intentional adversarial and
post-publication failure fixtures; byte integrity is not semantic acceptance.

The census found 57 current-build digest-consistent file sets. Maximum total
retained bytes were 356,420, below the unchanged 393,216-byte ceiling.

| File | Maximum bytes | Nodes | Depth |
| --- | ---: | ---: | ---: |
| request.json | 17,227 | 576 | 8 |
| snapshot.json | 84,979 | 2,679 | 15 |
| resolved-input.json | 224,672 | 7,692 | 17 |
| result.json | 13,688 | 668 | 8 |
| trace.json | 12,652 | 832 | 7 |
| build.json | 3,871 | 51 | 3 |
| manifest.json | 1,091 | 30 | 4 |

Application-reported semantic counter maxima were 1,382 references, 7,898
resolution charges, 16 corners, 22 decisions and 30 trace rows. Existing independent
accounting twins pass. The 202,875-byte semantic resolved count is distinct from
the 224,672-byte complete retained resolved-input wrapper.

No resource ceiling was raised. The approved terminal failure allowance remains
512 bytes including LF, separately from caller-tightened success/retention limits.
Existing boundary and refusal checks are part of the passing application suite.

The [machine-readable release evidence](2026-09-16-bounded-decision-workflow-s7-release-evidence.json)
has SHA-256 `8db348f00d36e1f75de3798b9f404cdb20d9a2141509a086402f57dd65f6747b`. It retains the test summary, environment inventory,
all twelve command measurements, independent byte/node/depth census, source and
lock hashes from the actual build, and a complete seven-file baseline archive.

To recover the archive, decode `baseline_archive.data` from base64, decompress
zlib, and verify `baseline_archive.uncompressed_sha256` before parsing the JSON
map. Values are exact UTF-8 file contents. Require exactly the seven fixed bundle
filenames and validate every digest against `command_measurements.files`. Write
only to a new exclusive ext4 destination, with `manifest.json` last, then run
`verify`; run `replay` from the exact tested commit and matching environment.
The archive was decoded back and compared to the original bytes during evidence
creation. Source and interpreter recovery remain external prerequisites.

The new baseline result digest differs from S6 only because its embedded build
identity changes. After excluding that one field, its result is identical to the
accepted S6 baseline, and its complete trace is byte-identical. Within the tested
S7 build, result and trace bytes are identical across roots and replays.

## Preservation and acceptance boundary

The pre-edit inventory covered 919 existing tracked and untracked files. Its
post-edit comparison found only the intentional plan-status edit; all other
pre-existing files remain byte-identical. The two new report/evidence files are
administrative additions. Frozen fixtures, prior reports, backend and ledgers were
preserved. No application or test source was edited during this continuation.

Documentation or report commits made after the tested commit are administrative
changes, not newly tested build identities. Exact-build recovery must use the
commit above even when a later checkout contains identical application code.

The delivered command evaluates the nominated synthetic hypotheses/actions,
derives the fixed one-step projections, applies supplied target and cost policy,
and exposes 22 dependency-review decisions with retained provenance. It does not
generate actions, choose measurements, authenticate unavailable source bytes,
prove physical accuracy or causal truth, or close the stronger original project
objectives. IN-001 and CI-001 remain open and unselected. Manifest-last completion
does not establish whole-directory atomic visibility or power-loss durability.

S7 evidence is ready for the owner's separate final application-acceptance decision.

END OF BOUNDED DECISION WORKFLOW S7 RELEASE VERIFICATION
