# Bounded decision workflow S7 final release verification

The additional full-repository verification is complete at the exact candidate
commit below. The full invocation recorded **4,648 passed, 35 skipped and one
sandbox setup error**, with zero test failures. The affected loopback test then
**passed in its permitted isolated rerun**; no product repair was needed.

Final application acceptance remains pending. This report completes the separately
authorized final release-verification work; it does not grant acceptance or select
a successor. IN-001 and CI-001 remain open and unselected.

## 1. Authority, candidate and historical evidence

Started on branch `brc-exp001` at
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`, with one unstaged plan modification,
66 untracked files and nothing staged. Of those untracked files, 63 are unrelated
artifacts preserved unchanged. The starting owner-review receipt SHA-256 was
`ed6ae233e7bf603090d6b2dc923d3cf5638aec102aba4b00ab58615cc7954c2b`.

The owner separately instructed: preserve/correct the report ending marker, run
the full repository suite, document the evidence, and stage/commit only authorized
S7 material. The earlier receipt's scope conclusion does not discharge that new
instruction. Its historical bytes are preserved, not rewritten as new evidence.

The exact full-suite tested candidate is
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`. A new clean local clone
at that revision was used. The release checkpoint containing this report is a
documentation-only descendant; it is not relabelled as a tested executable build.
Obtain that administrative checkpoint ID with:

```text
git log -1 --format=%H -- docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-final-release-verification.md
```

The prior [696-pass evidence](2026-09-16-bounded-decision-workflow-s7-release-evidence.json)
remains SHA-256
`8db348f00d36e1f75de3798b9f404cdb20d9a2141509a086402f57dd65f6747b`.
Its fresh-environment recreation, clean-build compatibility, evaluate/verify/replay,
historical recovery, 27-row acceptance mapping and deterministic result/trace
evidence are reused. The requested complete test selection naturally includes
the maintained S7 tests; no additional standalone repetition was commissioned.

## 2. Exact marker correction

The original [pre-marker report](2026-09-16-bounded-decision-workflow-s7-release-completion-report-pre-marker.md)
is a byte-for-byte preservation of the 178-line, 10,052-byte original report:

`4e90e82b56f1d25227c23506a80e18b43cdae62c183dfde1835bbd7349664aec`

The [corrected report](2026-09-16-bounded-decision-workflow-s7-release-completion-report.md)
is 180 lines, 10,110 bytes, SHA-256:

`6e2ff01b9172559b3914938b9d9c9e1d41215cfa3771cc2844144f61bd72b9c1`

Exactly 58 UTF-8 bytes were appended: one LF, the marker below, and a final LF.
No existing byte, claim, test result or section order was changed.

```text
END OF BOUNDED DECISION WORKFLOW S7 RELEASE VERIFICATION
```

The original owner-review receipt's report digest identifies the preserved
pre-marker file. Its statement that the report lacked a marker is historical;
this correction resolves that documentation omission.

## 3. Full repository run: scope and environment

**4,684 tests collected; 4,648 passed, 35 skipped, zero failures and one
setup error**, in 2,600.324 seconds as recorded by JUnit. The
full invocation exits 1 because of that setup error. The isolated permitted rerun
adds a passing execution for that same case; it does not rewrite the full-run
record or add another distinct test. All 4,649 non-skipped cases therefore
have passing execution evidence across the full run and that one rerun.

| Test group | Collected | Passed in full run | Skipped | Setup errors |
| --- | ---: | ---: | ---: | ---: |
| tests.applications | 610 | 610 | 0 | 0 |
| tests.behavior_evaluation | 137 | 137 | 0 | 0 |
| tests.constraint_evaluation | 183 | 183 | 0 | 0 |
| tests.data_sources | 385 | 351 | 33 | 1 |
| tests.evidence_alignment | 62 | 62 | 0 | 0 |
| tests.evidence_assurance | 68 | 68 | 0 | 0 |
| tests.identity_binding | 327 | 327 | 0 | 0 |
| tests.model_kernel | 1928 | 1928 | 0 | 0 |
| tests.model_state | 103 | 103 | 0 | 0 |
| tests.observation_compatibility | 116 | 116 | 0 | 0 |
| tests.semantic_compatibility | 61 | 61 | 0 | 0 |
| tests.source_interpretation | 145 | 145 | 0 | 0 |
| tests.state_classification | 110 | 110 | 0 | 0 |
| tests.structural_evidence | 227 | 225 | 2 | 0 |
| tests.temporal_state | 95 | 95 | 0 | 0 |
| tests.test_ea001_slice_a_architecture | 5 | 5 | 0 | 0 |
| tests.test_ea001_slice_a_reproduction | 2 | 2 | 0 | 0 |
| tests.transition_assessment | 120 | 120 | 0 | 0 |


This is `pytest tests` across the entire repository test tree, without `-k`,
`-m`, ignored directories or other deselection. It is a base-dependency run,
not the earlier 610 application plus 86 affected-regression selection.

The unchanged, previously recreated isolated environment was
`/tmp/bdw-s7-resume-CBFUxO/env`, CPython 3.13.11. Its inventory was rechecked as
exactly the ten approved locked distributions. No dependencies, optional extras,
policies or numeric limits were installed or changed. Source and fresh disposable
test children were on `/dev/sdc` ext4 under `/tmp/bdw-s7-full-mOQjBy`.
Using the system temporary boundary also satisfies FL-001 reproduction guards.

The exact command, from `/tmp/bdw-s7-full-mOQjBy/source`, was:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
BDW_UNSUPPORTED_FILE=/mnt/d/operation-house-keeping/applications/bounded_decision_workflow/examples/request.json \
BDW_UNSUPPORTED_OUTPUT_PARENT=/mnt/d/operation-house-keeping/.bdw-s7-full-unsupported-1tnIvm \
/usr/bin/time -v -o /tmp/bdw-s7-full-mOQjBy/full-suite-time.txt \
/tmp/bdw-s7-resume-CBFUxO/env/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests -q -ra \
  --basetemp=/tmp/bdw-s7-full-mOQjBy/tests \
  --junitxml=/tmp/bdw-s7-full-mOQjBy/full-suite-junit.xml \
  > /tmp/bdw-s7-full-mOQjBy/full-suite.log 2>&1
```

These are completed-run paths, not destinations to reuse. The unsupported file
was read-only; the output-parent refusal probe used its own new directory on 9p.
Existing sources, evidence and runtime result directories were not probe targets.

## 4. Failures, restrictions and isolated reruns

The one error was
`tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation`.
Its fixture could not create an AF_INET socket for `127.0.0.1` inside the sandbox:
`PermissionError: [Errno 1] Operation not permitted`, before the product transport
ran. A targeted sandbox diagnostic reproduced the same setup error (one error,
0.37 seconds); that duplicate diagnostic is not an additional distinct case.

The tool-permitted rerun used the same interpreter, source revision and test node,
outside the sandbox so the local test socket could be created. It returned
**one pass, zero failures/errors/skips, 0.81 seconds**, without source, dependency
or policy changes. No remote endpoint was contacted. The original full-suite
error and both isolated execution records are retained separately.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
/usr/bin/time -v -o /tmp/bdw-s7-full-mOQjBy/loopback-rerun-time.txt \
/tmp/bdw-s7-resume-CBFUxO/env/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation \
  -q --basetemp=/tmp/bdw-s7-full-mOQjBy/loopback-permitted \
  --junitxml=/tmp/bdw-s7-full-mOQjBy/loopback-rerun-junit.xml \
  > /tmp/bdw-s7-full-mOQjBy/loopback-rerun.log 2>&1
```

This restriction did not justify changing the backend, weakening the test or
substituting a mocked transport. There is no unresolved product failure.

The full run retained the existing optional-extra skips:

- **12**: CAD extra not installed — run: pip install --require-hashes -r requirements-cad.txt.
- **23**: PDF extra not installed — run: pip install --require-hashes -r requirements-pdf.txt.


No optional dependency acquisition or change of application policy is inferred
from a skip. No final all-extras, XFS, WSL reboot or power-loss result is claimed.

## 5. Retained evidence and reproduction

[Full-suite evidence](2026-09-16-bounded-decision-workflow-s7-full-suite-evidence.json)
SHA-256: `1e75847a3311eb24d5b5635fb6a88fd33fe5d502d037a689f04468cfd77da274`.
It retains the complete suite summary, per-package counts, failure/skip details,
stdout log, measured time/RSS record, environment identity and compressed original
JUnit XML with its uncompressed digest. Decode base64 then zlib and check that
digest to recover the exact per-test record. It also retains source/ledger hashes,
the unrelated-artifact inventory and the persistent-result preservation inventory.

The [user documentation](../../../applications/bounded_decision_workflow/README.md)
and the persistent ext4 example in the
[historical owner-review receipt](2026-09-16-bounded-decision-workflow-s7-final-owner-review-receipt.md)
remain applicable at the exact tested commit. Reproducing the recorded S7 build
requires that commit and the locked environment, even after this administrative
checkpoint is committed. Verification checks retained bytes; replay additionally
requires the matching executable and recomputes semantics. No source installation,
migration, physical acquisition or causal claim is added.

## 6. Preservation, staged scope and checkpoint

The 63 unrelated untracked artifacts match their retained SHA-256 inventory.
The pre-suite inventory has 923 existing files, including the already preserved
pre-marker copy. Final comparison permits only the explicitly authorized plan
status update. The earlier receipt and 696-pass evidence remain byte-identical.
Backend/application source, public contracts, tests, dependency lock and all 36
authoritative model records remain unchanged. The model revision remains
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.

The persistent `inputs/` and `results/` directories remain empty; all seven files
of the accepted S6 baseline bundle match the pre-run inventory. Existing runtime
test workspaces were not repurposed. The full suite used only new disposable
children and its explicitly isolated unsupported-mount probe. No new durable
application result was written among the owner's existing results.

The checkpoint stages exactly these seven release-documentation paths:

- `docs/superpowers/plans/2026-09-15-bounded-decision-workflow-implementation-plan.md`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-completion-report.md`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-completion-report-pre-marker.md`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-release-evidence.json`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-final-owner-review-receipt.md`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-full-suite-evidence.json`
- `docs/superpowers/reports/2026-09-16-bounded-decision-workflow-s7-final-release-verification.md`

No repair file is included because no product repair was needed. Staged paths
and whitespace were inspected before the commit; no broad directory staging was
used. The final status is expected to contain only the 63 preserved unrelated
untracked artifacts, with no staged or unstaged tracked changes. The final
owner-facing receipt records the actual checkpoint SHA and checked Git status.

## 7. Remaining owner gate and limitations

The separately authorized full-suite verification, marker correction and
release-documentation work are complete, with the environment restriction and
optional-extra exclusions explicitly recorded. Final application acceptance is
**pending**, and this checkpoint must stop at that owner gate.

Manifest-last publication is not whole-directory atomic visibility or proof of
power-loss durability. Conditional synthetic correctness is not physical accuracy,
source authenticity, causal truth, global planning or actuation. IN-001 and CI-001
remain open and unselected. No backend change, new dependency/policy, successor,
push, merge or history rewrite was performed.

END OF BOUNDED DECISION WORKFLOW S7 FINAL RELEASE VERIFICATION
