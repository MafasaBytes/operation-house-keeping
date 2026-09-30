# Maintained bounded next-measurement selection

Slices 1–6 are owner accepted. [Final release verification](../superpowers/reports/2026-09-23-next-measurement-final-release-verification.md)
is recorded; [final owner acceptance](../superpowers/reports/2026-09-23-next-measurement-final-owner-acceptance.md)
covers tested implementation `23b60a42c2279fc228168967d47491b8983658fb`.
The local source-agnostic consumer answers: given admitted evidence, explicitly
retained hypotheses and nominated procedures, which measurement best separates
those hypotheses under justified supplied predictions, or why must ranking be
withheld? This is the bounded objective-4 contribution. Archived experimental
selectors are not production dependencies.

The [selection and reassessment user guide](../reassessment/README.md) explains
the seven-objective scope, exact cross-profile handoff and authority boundaries.
Selection permits ext4/XFS; reassessment is ext4-only. A fresh selection-to-result
workflow needs manual artifact composition and new request-bound reassessment
authority; the example below does not supply that grant.

Permission under D/A/T, prediction qualification under supplied S premises, and
ranking under K are separate authorities. Admissibility is not predictive validity;
positive support cannot imply exhaustive coverage or complement exclusions.
The first profile uses qualified supplied predictions and prior-free finite
compatibility minimax: minimize the largest surviving hypothesis count. There is
no cost ranking. All tied best procedures, repeated branches and empty branches
are retained; equal scores need not mean equivalent survivor multisets. Only a
unique best procedure with positive reduction receives a recommendation.

Whole-nominated-set withholding retains exact denial, unknown permission,
unavailable baseline, inapplicability, missing support or conflicting support
reasons. No inconvenient candidate is pruned. An explicitly changed nominated set
is a different request. One procedure can discriminate two hypotheses. Missing
support cannot become discrimination or a shortcut to a zero/one-hypothesis result.
Manual unresolved C has no automatic adjudicator or executable case.

## Commands and interpretation

Use the approved external Linux CPython 3.13.11 environment and locked dependencies
from the application [installation/recovery instructions](../../applications/bounded_decision_workflow/README.md#release-verification-and-recovery).
Git does not supply that interpreter or dependency artifacts. A clean committed
application/backend scope and exact installed artifact identities are required.
No command installs dependencies, acquires measurements or fetches history.
Reinstalling the same wheels at another environment prefix can change installed
script hashes and therefore the actual build identity. A freshly bound invocation
is not evidence of compatibility with an older retained environment witness.

Here `PY` denotes the absolute path to the intended interpreter; shell activation
is not an identity check. These signatures require already valid, authorized inputs.

```text
PY -m applications.bounded_decision_workflow measurement-evaluate --invocation FILE --objects-dir DIR --authority-pin SHA --output-dir NEWDIR [--limits FILE]
PY -m applications.bounded_decision_workflow measurement-verify --bundle DIR
PY -m applications.bounded_decision_workflow measurement-replay --bundle DIR --output-dir NEWDIR [--limits FILE]
```

I references Q; Q explicitly nominates H/P/S; E carries the owning public snapshot
and bindings. The authority pin must equal I.selection.sha256. Required object
filenames are `<sha256>.<kind>`; extraneous files never nominate candidates.
Exact kinds, canonical bytes, joins and full required closure are validated.
Case-sensitive logical H/P IDs are unique within their respective nominations;
revision comparison requires separate requests. Synthetic build witnesses,
caller-computed results, bypass flags, implicit discovery and compare-to are not
accepted measurement interfaces. The six thermal/governed commands remain distinct.

Exit 0 includes completed withholding and valid ties; it does not mean permission,
a recommendation or permission to perform a measurement. Stdout is one canonical
JSON receipt plus LF and stderr empty. Technical refusal emits empty stdout and a
bounded JSON diagnostic plus LF: usage 2; integrity/profile/input 3; resource 4;
path/filesystem/collision 5; retention 6; internal 7. Failed output channels cannot
promise delivery. Completed visible bundles and incomplete publication are
reported honestly; publication never overwrites, cleans up or resumes a directory.

Evaluate/replay retain invocation, complete closure, result, trace, build, policy
and a final manifest. Verify checks captured integrity/build/policy/completeness;
it does not recompute the recommendation. Replay independently reconstructs,
publicly re-admits, requalifies and recomputes minimax, comparing fresh result/trace
with retained evidence under the exact historical build/environment. It needs no
original input directory or prior result chain and makes no present adoption claim.

## Bounded history and resources

All required typed dependencies and declared ancestors through revision 1 must be
present. Four complete revisions per chain, eight request contexts and 128 unique
objects are the approved first-release envelope. Shared dependencies are not
cycles; every reference/context still incurs its prescribed work. Exceeding history
or any resource bound refuses, without truncation, squashing or dropping ancestry.
Optional historical dossiers/results are not required or claimed recovered.

The immutable 24-dimension policy is recoverable as `resource-policy.json` from
the committed package below and implemented in
[measurement_contracts.py](../../applications/bounded_decision_workflow/measurement_contracts.py).
It includes 1 MiB capture and bundle ceilings, 512 KiB closure, 256 KiB per object,
16 KiB invocation/manifest, 64 KiB build/result, 128 KiB trace, 2 KiB diagnostic,
1 KiB receipt, 4,096 references/edge visits, 1,024 scoped expansions, depth 32 for
active traversal, JSON depth 40/nodes 65,536, strings 4,096 bytes, integer digits
128, reconstruction nodes 131,072 and contextual scans 16 MiB. Public-input lower
limits still apply. `--limits` can only tighten known positive ceilings. These are
bounds, not a promise that all dimensions can simultaneously reach their maximum.
Logical capture/traversal/reconstruction and fresh physical I/O are distinguished.

Observed qualification is ext4 on this Linux/WSL environment; DrvFS/9p is refused
for runtime inputs/results. The implementation's XFS allowance is not empirical
XFS qualification. Symlinks, special files and unsafe path components refuse.
Manifest-last publication is not whole-directory atomic visibility or evidence
of reboot/power-loss durability. Local attestation is not authenticated identity.
Same-author hand oracles and separately written checks share declared premises;
they are not independent empirical/reviewer evidence. No empirical prediction
accuracy, correct diagnosis, globally optimal test, physical acquisition,
generated hypotheses/tests, probabilistic model or multi-step planning is claimed.

## Recoverable synthetic example from committed material

This route uses committed example inputs plus the approved external environment;
Git alone does not supply its runtime prerequisites. Use a checkout containing
this guide/helper with clean application/backend sources, and a new private ext4
parent. Binding records that checkout's actual HEAD; it does not reproduce the
identity of an older selection merely because the source is equal. For a separately
authorized example execution, substitute the approved interpreter's absolute path:

```bash
PY=/absolute/path/to/approved/python
"$PY" -c "import runpy; runpy.run_path('docs/next-measurement/recover.py', run_name='__main__')" --example-dir /absolute/ext4/new-input
NM_PIN=$(cat /absolute/ext4/new-input/authority-pin.txt)
"$PY" -m applications.bounded_decision_workflow measurement-evaluate --invocation /absolute/ext4/new-input/invocation.json --objects-dir /absolute/ext4/new-input/objects --authority-pin "$NM_PIN" --output-dir /absolute/ext4/new-result
"$PY" -m applications.bounded_decision_workflow measurement-verify --bundle /absolute/ext4/new-result
"$PY" -m applications.bounded_decision_workflow measurement-replay --bundle /absolute/ext4/new-result --output-dir /absolute/ext4/new-replay
```

[recover.py](recover.py) is documentation/fixture recovery, not a production command
or new trust boundary. It verifies exact package/manifest/recovery commitments
inside the committed `frozen-authority.zip`, decodes the synthetic P input and
binds only its prepared build/I to the actual clean executable. It never supplies
expected computed outputs to production. P should yield scores T1=1/T2=2 and a
conditional T1 recommendation. All candidate identities, supplied support and
local authority premises originate in the frozen input; nothing is inferred from
files present in a directory. New destinations are mandatory. Recovery is not a
replacement for production safe file admission. The example is synthetic, not an
empirical claim. Keep its material immutable after binding.

This P example and historical reassessment P8-before are separate recovery routes.
Changing P's build changes its invocation digest. Using that new selection in NR
changes request/exposure references and requires a newly attested NR authority;
the helper neither creates nor authorizes that handoff. See the
[example/recovery distinctions](../reassessment/README.md#examples-and-recovery-routes).

For offline contract/test review, the same helper's `--package-dir NEWDIR` restores
all 1,191 exact manifest-bound members plus the original archive, manifest and
receipt. At the current accepted checkpoint,
`docs/superpowers/reports/2026-09-19-next-measurement-preparation` is already
committed and byte-identical to those 1,194 recovered files. It was added by
`b085e0ee65cefd770bb2cba82e834aebb82c50e4`, after the older 23b60a4/c321 candidates
where it was absent. Do not recover over that existing directory:
`mkdir(exist_ok=False)` raises an uncaught `FileExistsError`. For an older checkout
that needs recovery, use an absent destination under a separately approved setup.
The two qualification overlays remain separately committed; recovery never
rewrites the original package or supplies new authority.

## Repository test setup is not portable by default

The full suite also collects 19 reassessment delivery tests whose accounting
module hard-codes a historical host corpus. Do not use that corpus. A separately
authorized full-coverage setup needs a fresh private ext4 corpus with all seven
categories, a valid genesis and complete accounting; make
`tests/reassessment_profile` importable, set `REL5_CORPUS_ROOT`, and load
`-p slice5_delivery_root_adapter` before collection. Setting the environment
variable, TMPDIR or `--basetemp` alone does not substitute the imported ROOT.
Alternatively, explicitly exclude `tests/reassessment_profile/test_delivery.py`
with `--ignore=tests/reassessment_profile/test_delivery.py`, disclosing the
19-node coverage loss; this is not equivalent to full qualification.
See the [complete boundary and prerequisites](../reassessment/README.md#application-paths-versus-existing-test-requirements).

Other application release gates still need disabled bytecode/cache writes, a new
ext4 `--basetemp`, and nominated read-only/isolated unsupported-mount paths for
`BDW_UNSUPPORTED_FILE` and `BDW_UNSUPPORTED_OUTPUT_PARENT`. Historical source,
archive and environment prerequisites also remain. Optional CAD/PDF dependencies
are separate; skips are not coverage. These are setup requirements, not an
instruction or authorization to launch tests during documentation work.

Authority and qualification: [Slice 6 acceptance](../superpowers/reports/2026-09-23-next-measurement-slice6-owner-acceptance.md),
[closure report](../superpowers/reports/2026-09-23-next-measurement-slice6-oracle-closure.md),
[coverage map](coverage.md),
[final owner acceptance](../superpowers/reports/2026-09-23-next-measurement-final-owner-acceptance.md).
