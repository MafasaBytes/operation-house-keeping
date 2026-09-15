# Local bounded decision workflow (S6; release gate pending)

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

Six canonical payload files and a final manifest constitute a completed result.
Manifest-last completion is not whole-directory atomic visibility or proof of
power-loss durability. Incomplete bundles remain visible and require a new output
path for retry. `verify` checks bytes, not semantics or source authenticity. `replay`
requires the same committed application/backend source witnesses, CPython version
and locked dependencies, then reconstructs and recomputes. A clean executable scope
is required; unrelated untracked evidence is not a dirty executable. No installation
or checkout is performed by the application. Full clean-build recreation and final
release acceptance remain S7, not claimed by this S6 invocation documentation.

The version-only lock here specifies the already approved set; it is not a command
to install packages. Provisioning retains the separate hash-verified artifacts and
installation lock. A build identifier is a reproducibility witness, not executable
authentication. Public evidence can be carried without authenticating unavailable
raw source bytes. Physical accuracy, causal truth and global planning are not claimed.
