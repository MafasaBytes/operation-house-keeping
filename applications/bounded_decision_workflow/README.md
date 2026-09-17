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

The [version-only lock](requirements.lock) specifies the already approved set;
the retained [hashed installation lock](../../docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt)
pins the same ten versions and their approved wheel bytes. The interpreter and
wheels remain external prerequisites, not files supplied by Git. A build identifier
is a reproducibility witness, not executable
authentication. Public evidence can be carried without authenticating unavailable
raw source bytes. Physical accuracy, causal truth and global planning are not claimed.

## Release verification and recovery

Provide Linux CPython **3.13.11**, the ten approved wheels matching the retained
hash lock, and an existing isolated installer with the recorded `pip==25.3`.
The [environment report](../../docs/superpowers/reports/2026-09-15-bounded-decision-workflow-persistent-environment-report.md)
records interpreter identity, wheel tags/hashes and the observed platform. Its
account/group, UID, absolute paths, interpreter location and device assignment
identify the historical host; they are not installation requirements. Select your
own private paths and compatible interpreter/wheels. Exact historical replay
still requires the recorded build/environment witnesses; a different platform is
not established as equivalent by these instructions.

From this retention checkout, substitute caller-selected absolute paths below.
The environment destination must be new. Use a verified local ext4/XFS workspace,
with private ownership/permissions and no symlink components; source may reside on
DrvFS, but runtime inputs/results may not. This installs offline into a separate
venv without acquiring artifacts or modifying the existing installer:

```bash
BDW_PYTHON=/absolute/path/to/approved/python3.13
BDW_INSTALLER=/absolute/path/to/existing/isolated/installer/bin/python
BDW_WHEELS=/absolute/path/to/approved/wheelhouse
BDW_ENV=/absolute/supported-filesystem/new-environment
BDW_HASH_LOCK="$PWD/docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt"
"$BDW_PYTHON" -m venv --without-pip "$BDW_ENV"
"$BDW_INSTALLER" -m pip --python "$BDW_ENV/bin/python" install \
  --no-index --no-cache-dir --no-deps --only-binary=:all: --require-hashes \
  --find-links "$BDW_WHEELS" -r "$BDW_HASH_LOCK"
```

Use the new environment's interpreter for the example commands above, with new
input filenames and output directories on the supported filesystem. Historical
replay must run from a separate clean checkout at
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`; the retained lock is available in this
later documentation checkout and may be referenced by its absolute path. Never
repurpose the persistent environment or an existing result directory. Observed
verification is CPython 3.13.11 on ext4; XFS, other platforms, reboot and power-loss
behavior remain unverified. Manifest-last completion is not a crash-durability
guarantee.

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

## Authority and historical evidence navigation

The retained [corrected delivery design](../../docs/superpowers/specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md),
[delivery review](../../docs/superpowers/reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md)
and [implementation readiness report](../../docs/superpowers/reports/2026-09-15-bounded-decision-workflow-implementation-readiness-report.md)
complete the governing authority chain. The review's rejection is historical and
was resolved by the corrected design and subsequent S1–S7 acceptance.

The historical one-step proof [package](../../docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-package.json)
and [manifest](../../docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-manifest.json)
are reproduction inputs for that accepted experiment, not maintained runtime
inputs. For the 27 exact archive-recoverable duplicates, use each artifact's
`exact_recovery_locations` in the committed [inventory](../../docs/superpowers/reports/2026-09-16-bounded-decision-workflow-post-delivery-inventory.json):
the path before ` :: ` identifies the committed report, followed by its archive
fence and member locator. Decode as specified by that report and verify the
inventory's byte size and SHA-256; do not execute archived source to recover data.
Those duplicate standalone files are not required in a fresh checkout.

The [publication-readiness investigation](../../docs/superpowers/reports/2026-09-16-bounded-decision-workflow-publication-readiness.md)
records isolated installation/command evidence and classifies the other 30
unmatched files as external historical context in §7. Full review of that context
still requires its original bytes; no cleanup is implied. Historical links and
status statements inside frozen reports remain unchanged. The later
[owner retention approval](../../docs/superpowers/reports/2026-09-16-bounded-decision-workflow-retention-approval.md)
authorizes the exact additions and metadata disclosure; integration and push
remain separate owner gates.
# Governed command boundary (Slices 1–3)

The explicitly named `governed-evaluate`, `governed-verify` and `governed-replay`
commands select the immutable governed contract; the existing `evaluate`, `verify`
and `replay` commands remain legacy and do **not** claim admissibility enforcement.
There is no auto-detection fallback from a governed invocation to legacy behavior.

`governed-evaluate --invocation I.json --objects-dir OBJECTS --authority-pin SHA256
--output-dir NEW [--compare-to PRIOR]` consumes canonical invocation bytes and a
private directory of exact objects named `SHA256.kind` (for example
`<digest>.finite-declaration.v1`). Allowed kinds are the approved D/S/A/T/I/Q/B and
`captured-basis` roles. No object path comes from JSON; all files are captured with
the maintained no-follow regular-file/ext4/xfs boundary. The external selection pin
is mandatory owner input, not inferred from whichever selection is supplied.

`governed-verify --bundle PATH` checks complete retained integrity and bounded work
evidence, not permission or numerical truth. `governed-replay --bundle PATH
--output-dir NEW` requires the exact historical executable/environment and
reconstructs, re-admits and recomputes the complete chain. It never discovers a
newer declaration, upgrades policy, fetches a checkout or claims current adoption.

Completed governed evaluation/replay has exit 0 and explicit `evaluation_permitted`
in its receipt; false means no current numerical projection, not a failed process.
Technical refusals have nonzero exit, bounded stderr and empty stdout. An admitted
no-feasible-action result is distinct from denial. Publication never overwrites or
automatically removes incomplete evidence. Runtime storage/pin selection remain
local-owner responsibilities, not authenticated identity. Implementation is not
final milestone acceptance; IN-001 and CI-001 remain open/unselected.
