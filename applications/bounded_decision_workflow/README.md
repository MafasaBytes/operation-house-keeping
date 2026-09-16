# Local bounded decision workflow (S1–S7 owner accepted)

The owner [accepted S1–S7](../../docs/superpowers/reports/2026-09-16-bounded-decision-workflow-final-owner-acceptance.md)
at tested implementation `64f4389b6d93484339afa29cbb7f7f21f6ef2758`.
Observed platform evidence is locked CPython 3.13.11 on ext4; XFS, reboot and
power-loss durability remain unverified. Reproduce the accepted build and its
retained replays from that exact implementation commit and locked environment;
later documentation commits are administrative, not newly tested build identities.

Use the approved Linux CPython 3.13 environment and a local ext4/XFS runtime
location. The source checkout may remain on WSL DrvFS; input and result files
may not. No service, device connection or credential is used.

The [request](examples/request.json) and [snapshot](examples/snapshot.json) are
complete canonical synthetic examples. The snapshot came from public backend
producers, not real equipment. They match SHA-256
`24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` and
`782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`.
Copy them to new filenames in an owner-selected ext4/XFS input directory without
overwriting existing data. Never edit a snapshot commitment to authenticate a
forged nested public result.

From the checkout, with the approved isolated interpreter as `python`:

```text
python -m applications.bounded_decision_workflow evaluate --request /absolute/ext4/request.json --snapshot /absolute/ext4/snapshot.json --output-dir /absolute/ext4/new-result
python -m applications.bounded_decision_workflow verify --bundle /absolute/ext4/new-result
python -m applications.bounded_decision_workflow replay --bundle /absolute/ext4/new-result --output-dir /absolute/ext4/new-replay
```

`evaluate` optionally accepts `--compare-to /absolute/ext4/prior-result`. Output
parents must already exist; final basenames must be new. No path component may be
a symlink, `.` or `..`. A collision never replaces an existing artifact. No command
performs cleanup or resumes an incomplete directory. No network/source acquisition.

The baseline classifies the nominated current condition as `matches`, admits
`T0=40`, projects H_F actions a0/aF/aH/aHF to 36/32/36/32 and H_H to 42/42/32/32,
then selects aH at cost 2 among the nominated robust-feasible actions. Outcomes are
conditional on explicit synthetic assumptions. The retained result separates current
condition, raw outcomes, target relation, feasibility, selection and all 22 review
decisions. A required reevaluation need not change a value; cost does not alter physics.

Success writes one compact JSON stdout receipt and empty stderr. Unavailable,
unknown, inapplicable and no-feasible-nominated-action conclusions may still succeed.
Failures write empty stdout and one bounded JSON stderr diagnostic: exit 2 usage;
3 input/integrity/build/replay; 4 resource; 5 unsafe path/filesystem/collision;
6 retention/durability sequence; 7 unexpected internal failure. Input refusals do
not promise a retained refusal bundle. They never retain partial semantic results.

The terminal failure line has a fixed build-owned allowance of 512 UTF-8 bytes
including its LF, independent of caller-tightened successful-output limits. Those
caller limits remain unchanged. A malformed or over-envelope diagnostic becomes
the fixed `INTERNAL_ERROR`, exit 7, `bundle_state="unknown"` fallback; no arbitrary
exception contents are printed. A broken stderr sink returns 7 without recursive
reporting; receipt of a complete line requires a writable channel.

For incomplete bundles, `verify` emits only its fixed exit-3 stderr diagnostic,
not a file inventory; stdout is empty. `bundle_state="absent"` means no new output
bundle, not that the inspected directory is absent. Missing manifest produces
`BUNDLE_INCOMPLETE`; invalid manifest produces `MANIFEST_INVALID`. The existing
public `verify_bundle` API still exposes bounded captured recognized files with
explicit incomplete status for local inspection. It never promotes partial data.

Six canonical payload files and a final manifest constitute a completed result.
Manifest-last completion is not whole-directory atomic visibility or proof of
power-loss durability. Incomplete bundles remain visible and require a new output
path for retry. `verify` checks bytes, not semantics or source authenticity. `replay`
requires the same committed application/backend source witnesses, CPython version
and locked dependencies, then reconstructs and recomputes. A clean executable scope
is required; unrelated untracked evidence is not a dirty executable. No installation
or checkout is performed by the application. The maintained S7 release checks cover
clean-build recreation and recovery. Final application acceptance is recorded in
the owner decision linked above, with its explicit scope and limitations.

The version-only lock here specifies the already approved set; it is not a command
to install packages. Provisioning retains the separate hash-verified artifacts and
installation lock. A build identifier is a reproducibility witness, not executable
authentication. Public evidence can be carried without authenticating unavailable
raw source bytes. Physical accuracy, causal truth and global planning are not claimed.

## Release verification and recovery

The approved environment can be reproduced in a separate Linux CPython 3.13 venv
using only the retained wheels and provisioning `requirements-hashed.txt`, with
`--no-index --no-deps --only-binary=:all: --require-hashes`. The version-only lock
in this directory does not replace that artifact-hash check. Never repurpose the
persistent environment or an existing result directory for release tests.

From a clean local clone at the exact selected commit, run the application test
directory and affected decimal-parser, state-classification architecture and
semantic-compatibility isolation tests with the fresh interpreter. Disable bytecode
and pytest's cache provider, and select a new `--basetemp` under the verified ext4
test workspace. Set `BDW_UNSUPPORTED_FILE` to an existing read-only fixture on a
verified unsupported mount when exercising that platform rejection. This is a test
setting only; also nominate a new isolated directory on that unsupported mount as
`BDW_UNSUPPORTED_OUTPUT_PARENT` for the output-parent refusal probe. The probe must
not use an existing source/evidence directory as its attempted output location.
The production command accepts no filesystem-policy overrides.

`tests/applications/bounded_decision_workflow/test_s7_release.py` exercises two
independent local clones, seeds 1/7/313 and normal/reversed mapping construction,
with actual evaluate/verify/replay commands. It compares complete semantic bytes,
retains per-command elapsed times and file sizes, and permits only enumerated
manifest run-metadata differences. It also recovers the accepted S6 archive with
its matching historical build and rejects replay under a different build.

The complete canonical baseline input, output, trace and manifest can be recovered
from the accepted [S6 report](../../docs/superpowers/reports/2026-09-15-bounded-decision-workflow-s6-resource-and-cli-completion-report.md).
Its explicit digest and exact-build requirements apply. Extract only to a new
exclusive destination; incomplete bytes are not trusted merely because they can be
read. Verification checks integrity; replay additionally reconstructs/recomputes.
Original objectives are answered only within the nominated synthetic hypotheses,
actions, hard bounds and policy. The workflow does not select measurements or
generate alternatives, and does not establish actual physical effects.
