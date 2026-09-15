# Bounded decision workflow S5 — retention and recovery completion

## Authority and exact commits

Started on `brc-exp001` at administrative HEAD
`1b54b16a0096ad1c1c778082be9755277975fd27`. Verified S4 tested implementation
`49ab8778882007886ce95646e2e8fa6d0b0cd28d` and the untouched
[S4 completion report](2026-09-15-bounded-decision-workflow-s4-decision-review-completion-report.md),
SHA-256 `59cbc7541cf1fb6a6400bbe2dd5b55555da1fc5cbaf706c2adb937bbf5bf23ec`.
The intervening administrative commit changed only report/plan documentation.

| Commit | Authority/scope |
| --- | --- |
| `f4f9748f560d878b01e83dc071be781a309099d9` | Separate [S4 owner acceptance](2026-09-15-bounded-decision-workflow-s4-owner-acceptance.md); separately authorizes S5 only. Acceptance reran 24 targeted checks, 63 deselected, passing in 9.08s; confirms the recorded 474-test selection, historical reds, archive recovery and all 22 decisions. |
| `ea5c752a0c763cbc1b0ee5b61f09b94fca34df34` | Separate mechanical S5 recipe correction and historical evidence preservation; no semantic objects changed. |
| `702a4cbd143950e4fc2e6d724760e0a2723301f2` | Exact tested S5 implementation/test HEAD. |

The administrative commit containing this report and plan status follows the tested
HEAD and changes documentation only. Its full ID is recoverable with
`git log -1 --format=%H -- docs/superpowers/reports/2026-09-15-bounded-decision-workflow-s5-retention-and-recovery-completion-report.md`.
It is not a different tested implementation.

Read the complete [approved design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md),
[implementation plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
and S4 report before editing. The design remains
`54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The plan assigns S5 descriptor-relative safe paths, exclusive manifest-last
publication, verification and fault-injection seams—not command integration.

## Implemented application boundary

[retention.py](../../../applications/bounded_decision_workflow/retention.py)
adds five public exports: `CapturedFile`, `BundleInspection`,
`capture_file(path, *, kind, fault=None)`,
`publish_bundle(output_dir, files, *, bundle_kind="complete", operation="evaluate", fault=None)`
and `verify_bundle(path, *, fault=None)`. Fault hooks are trusted test code, never
serialized request data. Existing S1–S4 exports and semantics are unchanged.

- Capture opens path components descriptor-relatively without following symlinks,
  accepts only regular files on a descriptor-identified ext4/XFS mount, records
  device/inode/mode/size/mtime/ctime/link count, reads at most the fixed ceiling+1,
  compares pre/post metadata, and returns immutable captured bytes and SHA-256.
  Arithmetic/admission still belongs to S1–S4; capture does not admit observations.
- Publication validates bounded canonical file-set bytes before exclusive final
  directory creation. It uses fixed temporary names, file mode 0600, directory
  mode 0700, write/flush/file-fsync/close and Linux no-replace same-directory rename.
  `manifest.json` is published last; directory and parent fsync follow. The existing
  output path is never opened, overwritten, resumed or deleted on collision.
- Complete bundles contain the six fixed payload files plus manifest; refusal
  bundles contain only diagnostic, input metadata, build and manifest. File hashes,
  byte counts, build-material hash and result/trace commitments are checked. Manifest
  names cannot authorize path traversal or additional files. No partial conclusion
  is returned as a complete result after a publication failure.
- Verification is read-only fixed-name byte/inventory checking. It reports recognized
  captured files from an incomplete bundle, never repairs/promotes them, and does not
  reconstruct public records or recompute a decision. S6 must apply S1–S4 when consuming
  these bytes as a prior or replay input. A self-consistent forged result may pass
  byte integrity; that is explicitly **not** semantic admission or authentication.

Filesystem identity comes from the open descriptor's kernel mount ID and mountinfo,
not a Linux-looking path or ext-family magic (ext2/ext3 share ext4's magic). Fixed
kernel metadata reads are bounded. Linux `renameat2(RENAME_NOREPLACE)` adds protection
against a final file unexpectedly appearing inside the owned directory.

Manifest completion is atomic visibility of the final completion marker, not atomic
appearance of the entire directory. Post-manifest fsync failure returns the existing
`complete_visible_durability_unknown` diagnostic. Verification establishes current
byte integrity, never prior crash durability. No WSL restart, power-loss, XFS device
or adversarial same-account metadata-evasion guarantee was tested.

## Mechanical corrections, not implementation findings

The [correction report](2026-09-15-bounded-decision-workflow-s5-retention-fixture-correction-report.md)
and package `s5_fixture_correction.changes` retain exact before/after fields:

1. RET-3 now maps each already-nominated create/write/flush/fsync/rename/manifest
   boundary to its exact existing catalogue diagnostic, instead of using write
   failure for every stage.
2. RET-4 distinguishes directory fsync from parent fsync failure.
3. PATH-1-manifest-extra now supplies a bundle to verification; its old evaluate
   recipe could not reach manifest validation. The valid bundle twin remains.

All 68 content-addressed objects are unchanged; 72 variants and 27 acceptance IDs
remain. S1–S4 observations, premises, targets, costs, dependencies, policy, rejection
controls and diagnostic catalogue are unchanged. RET-5's existing evaluate recipe
supports fresh resubmission, not an S5 claim to have implemented the S6 replay command.

| Evidence | SHA-256 |
| --- | --- |
| [Pre-correction package](2026-09-15-bounded-decision-workflow-candidate-package-pre-s5-retention-correction.json) | `89ba39623a72326d876740d624af501b467179c608ae89ce9e40f66806ec0d4e` |
| [Pre-correction manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-s5-retention-correction.json) | `e0a94c429d69dff69d7b00351dac52ba125e858683f41c0f585c0aafbabd10fc` |
| [Current package](2026-09-15-bounded-decision-workflow-candidate-package.json) | `355b169df2805fa09eaba8865eea1a89e02071cc56c302a078677789fad616bf` |
| [Current manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) | `6f1c6103cbc834e089c839f6e3a4503e0a6d91408dccb70972f40a628784fb57` |

## Red/fixed evidence and acceptance coverage

The first five real-filesystem S5 tests failed in 3.53s because the public retention
exports did not exist. The same five passed in 2.35s after implementation. Expanded
runs passed 104 tests in 10.33s and 120 tests in 12.31s. A final independently added
read-fault test exposed an ordinary defect:

```text
test_input_read_fault_closes_descriptor_and_returns_path_diagnostic
capture_file -> _read_at -> _event -> fail
E OSError: read fault
1 failed, 1 passed, 120 deselected in 3.46s
```

The descriptor already closed in `finally`, but the exception escaped. The fix
maps read/fstat I/O failure through the same existing `PATH_COMPONENT_UNSAFE`
diagnostic used by safe-path acquisition; no catalogue or policy change. The
two targeted tests then passed in 2.55s. Tests retain the injected error, valid
twin and descriptor-count assertion. No unresolved defect remains in tested S5 scope.

| Planned coverage | Executed evidence |
| --- | --- |
| PATH-1/2 | Actual ext4 capture/publication; actual checkout 9p refused; component/final symlinks, traversal, dot components, FIFO/directory inputs, basename, read mutation and manifest attacks; valid twins. |
| RET-1/2 | Real file/directory/symlink collisions preserved; two actual concurrent forked publishers yield one complete winner and one collision; an inserted final file cannot be overwritten. |
| RET-3 | 35 exact diagnostic checks: seven files × five publication boundaries. Separately, 35 actual SIGKILL child-process checks at those boundaries. Each pre-manifest result remains incomplete; no overwrite/resume; valid fresh-path twins. Root creation failure is separately absent, not incomplete. |
| RET-4 | Both post-manifest fsync failures have distinct exact diagnostics; bytes remain verifiable with durability unknown. A SIGKILL immediately after manifest rename leaves a complete byte set without establishing durability. |
| RET-5 | Incomplete verification is read-only; complete-visible bytes can be republished at a new path; captured request/snapshot feed the accepted S4 public service and recover identical review/trace and 22 rows. This is not the pending CLI replay engine. |
| Integrity/refusal | Extra/traversal/absolute/duplicate manifest names, malformed lengths, wrong hashes/build/semantic commitments, missing/extra files, noncanonical JSON and invalid metadata; no symlink following. Four-file refusal contains no result/trace. |
| Relevant resources | Cap+1 bounded capture; exact 16,384-byte output and over-limit twin; 1,024-node, depth-32, 64-trace-row and 256-byte-string boundaries and over-limit twins; aggregate bundle overflow independent of per-file bounds. No caller limit override. |
| S1–S4 regression | Public reconstruction/admission, rational projection, policy/ties/unknowns, 22-decision review, cost/target separation, historical rejection controls, fixture recovery and import isolation. |

At exact tested HEAD `702a4cbd143950e4fc2e6d724760e0a2723301f2`, the complete
affected selection passed **597 tests in 149.64s**: the previous 474-test selection,
one S5 fixture-correction test and 122 S5 filesystem/resource/recovery tests.
The command below is the exact selection; its executed basetemp was the fresh
`s5-retention-0jew4K/tested-head` child. No full unrelated production suite was run.

The test-only fixture uses exact frozen request/snapshot/result/trace examples.
Its build object explicitly says `preparation_example` and
`not_executable_authentication`; final release build assembly is S6/S7 work.
Tests independently compare bytes, file hashes, metadata, catalogue diagnostics,
process outcomes and filesystem contents. Existing independent S2–S4 mathematical/
decision tables remain separate from runtime code. Same-author tests are not
independent empirical evidence.

## Environment, resource policy and recovery

Used the persistent CPython 3.13.11 environment at
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001`.
Outside the read-only sandbox view, `findmnt` confirms `/dev/sdc`, ext4, rw,
`relatime,discard,errors=remount-ro,data=ordered`. All filesystem writes, concurrency
and interruption probes used newly created children of
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/s5-retention-0jew4K`.
Existing runtime inputs/results were not test destinations. Retained test directories
are isolated evidence, not completed user decisions.

Provisioning verification again passed: environment
`693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`,
10-artifact set `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`,
lock `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e`.
No dependency installation, Python change, mount change or repository relocation.

Build ceilings remain unchanged: request 32,768 bytes; snapshot 131,072; resolved
262,144; result/trace 16,384 each; diagnostic 1,024; retained bundle 393,216.
S5 bounds captured reads before parsing, lexical nesting before JSON allocation,
canonical serialization, node/string/trace counts and complete payload+manifest size
before directory creation. Build/input-metadata/manifest syntax uses existing
request/result ceilings, not caller-supplied maxima. The fixed filename inventory
also bounds directory enumeration. S6 still owns complete invocation-wide streaming
preflight, requested-limit tightening, reconstruction accounting and command outputs.

A measured normal seven-file byte-retention fixture totals 226,787 bytes: request
16,460; snapshot 84,979; resolved input 101,476; result 12,104; trace 10,614; synthetic
build 65; manifest 1,089. This is a concrete S5 fixture measurement, not a claim that
all final application results/build material have been measured or released.

Recovery needs no disposable driver. The committed tests recover all 68 package
objects and historical commitments; the package/manifest retain the exact examples.
Checkout the exact tested implementation in a separate workspace with the approved
environment, nominate a fresh ext4 test child, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python -m pytest -o addopts='' -p no:cacheprovider --basetemp=FRESH_EXT4_TEST_CHILD tests/applications/bounded_decision_workflow/ tests/constraint_evaluation/test_decimal_parser.py tests/state_classification/test_architecture.py tests/semantic_compatibility/test_isolation.py -q
```

Do not reuse an existing pytest basetemp: pytest clears that explicitly nominated
test directory. These tests are environment-specific and require the actual supported
filesystem; mocked filesystem detection is not the acceptance evidence. Semantic
file bytes are retained exactly; manifest UTC time is run-specific and not expected
to reproduce. No restart/power-loss test or backup guarantee is claimed.

## Preservation and remaining gates

Digest comparison covers 891 starting tracked/untracked files. Only authorized
existing files changed: application exports, the exact-public-surface test, plan,
candidate package and manifest. Historical copies preserve the candidate originals.
All 63 unrelated untracked files remain byte-identical. Backend code/contracts,
authoritative fixtures/ledgers, dependency artifacts, earlier accepted reports and
design/review bytes remain unchanged. Scoped commits were inspected explicitly;
whitespace, local links, commitments, archive recovery and post-commit scope checked.
Disposable correction tooling is removed only after recovery verification.

S5 delivers maintained application retention/recovery primitives, not the complete
application. S6 evaluate/verify/replay CLI, final build/result assembly and process
presentation are pending; S7 clean-build/release acceptance is pending. No physical
execution, source authenticity, empirical accuracy, causal truth or backend necessity
is established. IN-001/CI-001 remain open and unselected.

Owner gate: accept S5. S6–S7 remain unauthorized.

END OF BOUNDED DECISION WORKFLOW S5 RETENTION AND RECOVERY COMPLETION REPORT
