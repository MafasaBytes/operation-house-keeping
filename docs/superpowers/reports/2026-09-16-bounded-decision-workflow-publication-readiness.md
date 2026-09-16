# Bounded decision workflow publication-readiness investigation

## 1. Outcome and verified controls

The maintained application runs from committed material without the 63 untracked
artifacts. The branch is not yet self-contained for its governing authority,
historical one-step proof inputs and documented offline installation. The smallest
recommended retention change is six existing untracked documents/data files plus
the already approved 981-byte hashed installation lock, listed exactly in §5.
Retain the remaining artifacts locally; none is declared safely disposable.
No history rewrite, archive relocation or LFS migration is needed for file size.
Fresh remote-main verification is blocked by unavailable HTTPS credentials.

Before any report edit: branch `brc-exp001`, HEAD
`3bbb8204d6362a9399523dc1eca0e29c68c77542`, clean tracked/index state, exactly
63 untracked files, all matching the committed inventory. The
[reconciliation report](2026-09-16-bounded-decision-workflow-post-delivery-reconciliation.md)
matches SHA-256 `4b3a538237b63658593c8fc630d0cb25e696459ced728d249c9f8e0be0bdbadb`.
Accepted implementation remains `64f4389b6d93484339afa29cbb7f7f21f6ef2758`.
The earlier [inventory](2026-09-16-bounded-decision-workflow-post-delivery-inventory.json)
remains SHA-256 `6c337255aa7ba9b545ed0153b7ec4fad4807d81c107183b6911cfd1b36f4a4df`.
This investigation changes only this new report, which is left uncommitted.

## 2. Dependency findings

The four files previously classified as unique external authority/input material
are the corrected application design, persistent-environment report and one-step
candidate package/manifest. Their complete identities appear in §5.

| File | Actual dependency and consumers | Runtime / current build or test requirement |
| --- | --- | --- |
| Corrected application design | Governing acceptance authority: S1 authorization; S2/S3/S4 acceptance; implementation plan; S6 policy proposal/approval; S1–S6 completion, blocker and correction reports; S7 owner-review matrix. Six committed candidate package/manifest editions carry its digest. The untracked readiness report also cites it. | No file read by application or maintained tests. Digest metadata and references do not recover the design's full bytes. |
| Persistent-environment report | S1 authorization explicitly approves/pins it; the S1 blocker links it. It documents the external interpreter, ten wheels, hash lock, provisioning manifests and restart procedure. | The report itself is not loaded. The interpreter, installed distributions and external wheel/hash-lock assets are setup dependencies. Publishing the report alone does not publish those assets. |
| One-step candidate package | Historical reproduction input: committed one-step plan, execution report and acceptance pin it; its manifest and untracked preexecution report reference it. The recovered execution archive explicitly carries only its external commitment, while retained experimental sources require its objects/oracles/field map/corpus. | No maintained application or current test dependency. Required to reproduce the accepted historical 73-role proof, which is part of the proposed branch history. |
| One-step candidate manifest | Historical exact-package verification: the same three committed one-step documents pin it; the untracked preexecution report references it. The execution archive names its external digest. | No maintained runtime/build/test dependency. Needed with the package for the historical proof's declared recovery/verification procedure. |

This distinguishes consumed inputs from links: reading the design is necessary
to audit approved behavior, but the command does not open it. The current build
witness reads Git HEAD, tracked application files, selected backend public files,
interpreter/version inventory and the committed version lock. Application tests
read the committed bounded-workflow candidate packages, not the similarly named
untracked one-step experimental package. Searches of maintained Python sources
found no path/digest reference to any of the 36 unmatched files. Seven focused
fixture checks and actual commands below exercised these boundaries with the
original checkout hidden.

The previous classification “superseded” was about chronology, not disposal.
Two more files are needed for a self-contained application authority chain:
the readiness report explicitly pinned by S1 authorization and the independent
delivery review pinned by the approved plan/design and candidate metadata.
The review's rejection is historical and resolved by the corrected design;
retention does not reinstate its old gate.

The other 30 unmatched files are historical context for this publication scope,
not missing maintained runtime inputs or operative authority. In particular:

- The BRC Slice A output-resource amendment's operative policy is already
  retained in the committed synthesis §19; final BRC acceptance §6 explicitly
  distinguishes it from the separately committed Mode B amendment witness.
- Old BRC oracle/matrix backups and stop/rehearsal reports explain corrections;
  accepted final canonical requests/results and policy are already archived.
  Their full narrative/backup bytes remain valuable and are not all recoverable.
- The one-step lead design, review, preexecution report and source-gap assessment
  are explicitly cited reasoning/provenance context. The governing corrected
  design/plan are committed. Their absence limits inspection of that historical
  reasoning chain, but does not supply missing runtime objects or governing
  rules once the exact package/manifest are retained.
- The rejected application proposal and older objective consolidation are
  historical rationale, not the accepted specification or delivered code.

For all 36, the per-file disposition is recorded in §7. “Historical context”
does not mean deletable: full forensic review of a cited draft/rehearsal still
requires its original bytes. No cleanup is recommended or authorized.

## 3. Fresh-checkout execution and recovery

Created a new `git clone --quiet --no-hardlinks` at
`/tmp/bdw-publication-w6njx0/release`. The clone had no alternates and no untracked
files. None of the 63 artifact paths existed in it. All checks ran in bubblewrap
with the original `/mnt` tree hidden, the root filesystem read-only, a private
`/dev`, network namespace isolation and only the new investigation workspace
writable. No missing untracked file was copied into the clone. The approved
interpreter, provisioning lock and retained wheels were explicitly available
read-only outside the checkout; they were not claimed to come from Git.

The first sandbox attempt could not create bubblewrap's NETLINK_ROUTE socket.
A tool-permitted retry reached Git but exposed a harness error: read-only
`/dev/null`. A private `/dev` corrected that harness setup. Neither attempt ran
product commands. The completed isolated run recorded:

| Check | Actual result |
| --- | --- |
| Filesystem and new environment | Observed ext4; fresh CPython 3.13.11 venv, `--without-pip`. |
| Documented offline installation | Existing installer targeted the fresh venv with `--no-index --no-cache-dir --no-deps --only-binary=:all: --require-hashes`, retained wheels and the approved external hash lock; exit 0, exactly the ten locked distributions. `pip check` passed; its disabled-cache warning reflects the read-only home. |
| Committed examples at administrative `3bbb820…` | Both examples present; evaluate/verify/replay each exit 0, empty stderr; baseline T0=40, projections 36/32/36/32 and 42/42/32/32, aH selected, 22 review decisions. Result/trace bytes equal their recomputing replay. |
| Recovered S7 bundle at administrative `3bbb820…` | Seven exact files recovered from committed S7 evidence; verify exit 0. Replay correctly refuses with exit 3 / `REPLAY_BUILD_UNAVAILABLE`; no output directory created. |
| Exact accepted implementation `64f4389…` in the isolated clone | Fresh evaluate/verify/replay each exit 0 with the same baseline expectations; new result/trace equal their replay. Recovered S7 bundle verify/replay also exit 0, with exact historical result/trace equality. |
| Focused committed-fixture checks at `64f4389…` | **7 passed in 3.22 seconds**: public admission/example reconstruction, complete corrected-package recovery, and S3 correction/commitment twins. |
| Additional read-only archive checks at `3bbb820…` | S6 seven-file archive: 256,728 decoded bytes, SHA-256 `336b1ffed263df47067238b233fa564d354b9552e3ab404e9748bf9424739a30`. One-step archive: 14 exact files, 2,129,379 decoded bytes, SHA-256 `e2f5781b1ae1a8c615587e9a633cfee71669e0d0a404bdc98e56143a5136d112`; external package/manifest remain absent. Full-suite and isolated-loopback JUnit archive sizes/digests also verify. |

The exact ten installed versions match the existing application lock: no extra
distribution or new dependency was selected. The clone ended clean, restored to
the administrative revision; no branch/ref in the original repository changed.
This is proportional dependency verification, not a rerun of S7 determinism,
durability, the 73-role experiment or the full repository suite.

Reproduction recipe, using a **new** workspace in place of the completed run's
path, the retained approved assets, and a clean clone at the indicated revision:

```bash
# Run inside the isolated mount namespace described above.
# W is a new verified ext4 workspace; R is the approved persistent runtime root.
/home/mafasa/miniconda3/bin/python3.13 -m venv --without-pip "$W/env"
"$R/environments/cp313-bdw001/bin/python" -m pip --python "$W/env/bin/python" install \
  --no-index --no-cache-dir --no-deps --only-binary=:all: --require-hashes \
  --find-links "$R/dependency-artifacts" -r "$R/provisioning/requirements-hashed.txt"
# Copy only the two committed examples into new input files under W.
"$W/env/bin/python" -m applications.bounded_decision_workflow evaluate \
  --request "$W/inputs/request.json" --snapshot "$W/inputs/snapshot.json" --output-dir "$W/result"
"$W/env/bin/python" -m applications.bounded_decision_workflow verify --bundle "$W/result"
"$W/env/bin/python" -m applications.bounded_decision_workflow replay --bundle "$W/result" --output-dir "$W/replay"
"$W/env/bin/python" -m pytest -o addopts='' -p no:cacheprovider \
  tests/applications/bounded_decision_workflow/test_s1_input_public_admission.py::test_obs_1_public_result_is_admitted_and_exactly_reserializes \
  tests/applications/bounded_decision_workflow/test_s1_input_public_admission.py::test_corrected_package_objects_and_s1_valid_twins_are_recoverable \
  tests/applications/bounded_decision_workflow/test_s3_fixture_correction.py -q --basetemp "$W/pytest"
```

Actual commands, stdout/stderr and elapsed times are retained in the new local
`/tmp/bdw-publication-w6njx0/checks.json`, SHA-256
`39815149f65b2940333b49f03c20fc6553661cc9f01708d76e13e6e2e19332ba`.
The driver was `/tmp/bdw-publication-w6njx0/check_release.py`; it set
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONNOUSERSITE=1`, unset `PYTHONPATH`, and gave
pip a private TMPDIR. S7 recovery strictly decoded base64/zlib and checked both
compressed and decoded commitments before writing seven files exclusively.
No archived experimental source was executed. Temporary logs are supplemental;
the result, exact commands, identities and limitations are retained in this report.

**Missing setup dependency:** the clone contains the version lock but not
`provisioning/requirements-hashed.txt`, the ten wheels or a Python interpreter.
Thus “works with the approved external environment” is demonstrated; “offline
installable from Git alone” is not. Even retaining the environment report cannot
make binaries/interpreter appear in a fresh clone. Publishing the exact hash lock
and a portable acquisition/offline-install recipe closes the textual setup gap;
the interpreter/wheel distribution remains an explicit external prerequisite.

## 4. Publication size and remote-main status

Read-only enumeration used `git rev-list --objects BASE..HEAD` and
`git cat-file --batch-check` over the complete 60-commit proposed range from
locally recorded base `debcffec5a77ae270bbf8822f82ef1aa7556c5bd` to `3bbb820…`.
This covers historical blob versions, including ones absent from the current
tree: **207 blobs / 65,877,049 uncompressed bytes**, and **588 total Git objects /
66,641,246 bytes**. The tree diff has 120 paths, 140,444 inserted and 24 deleted
lines. Remote authentication failure prevents confirming this is the exact
currently unpublished set; it is the conservative inspected proposed range.

The largest blob is the conditional-prediction completion report,
`f603a638d40d8c6318a02cb9d8c4ad45c5c57b60`, **46,008,166 bytes / 43.8768 MiB**.
No blob reaches 50 MiB or 100 MiB. GitHub's authoritative
[large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
states a warning above 50 MiB, a block above 100 MiB and a 25 MiB browser-upload
limit. The intended Git publication path is below the warning/hard file limits;
browser upload is unsuitable for this archive. GitHub's
[single-push limit](https://docs.github.com/en/get-started/using-git/troubleshooting-the-2-gb-push-limit)
is 2 GiB. The complete enumerated objects total about 63.55 MiB before transport
compression, far below that bound; no push/pack was transmitted or measured.

These are not grounds for LFS, deleting evidence or rewriting accepted history.
They are review/maintenance concerns: the
[repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)
recommend small objects and impose UI limits on raw diffs and rendered text.
This diff exceeds the documented 1 MB/20,000-line PR display budget; the large
archive may not render as Markdown. Local/raw-file review and digest recovery
are required. These display limits do not prohibit a normal Git push. Sources
were checked on 2026-09-16; repository-specific permissions, rulesets and secret
protection are not established by generic hosting documentation.

Remote attempts: `git ls-remote origin refs/heads/main` first failed sandbox DNS
resolution; the permitted outside-sandbox retry reached GitHub and failed with
`could not read Username for 'https://github.com': No such device or address`.
No credential was requested from hidden files or printed. No GitHub connector or
authenticated gh client was available. No fetch, ref update or config change
was attempted. **The current remote tip remains unverified.** Local main and
recorded origin/main remain `debcffe…`, an ancestor with 0/60 left/right counts.
Fast-forward readiness is therefore local and conditional, not freshly remote
verified. An authenticated read-only query must succeed before integration;
if its tip differs, inspect that exact ancestry/scope before any owner gate.

## 5. Exact minimal retention recommendation and sensitive-data review

For a self-contained governing application record and the branch's accepted
one-step reproduction inputs, retain the six exact files below in their current
paths. They total **1,192,833 bytes**. This is a recommendation, not staging or
retention authorization. Full paths and hashes are the proposed scope.

| Exact path | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md` | 26,970 | `2bc917bee36a4e0db9b8b07b5a650455f98008e7d286a482c1127bdb8a7ddf29` |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-implementation-readiness-report.md` | 15,852 | `3792d9ade000b83c9226d50217b4b35154e8abfc780c39d6d9c3ce797f568d93` |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-persistent-environment-report.md` | 12,752 | `4e83517a4ee3ec360ed681c336c71cd94dbf58b76bc98bddc541f5f70c3935e2` |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-manifest.json` | 64,151 | `3f66828ee716c74e464862433fd9c62016cc758428f5a6a8c52952c7bbf97079` |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-package.json` | 1,020,759 | `97a78717e1964463a2e2ed41d6dd65291e4b0bc6272d8884b0c4bbf8ec24257b` |
| `docs/superpowers/specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md` | 52,349 | `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab` |

Also retain the **existing**, unmodified installation input from
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/provisioning/requirements-hashed.txt`
as proposed documentation evidence path
`docs/superpowers/reports/2026-09-15-bounded-decision-workflow-requirements-hashed.txt`:
**981 bytes**, SHA-256
`6bcc7bd80022ce38d984ada0b4e4d4986272befea760ae895c76a8c6f3937fcf`.
This freezes the already approved ten versions/wheel hashes; it adds no dependency
or policy. It has not been copied into the repository in this pass.

Pre-publication screening of all six proposed files and that lock found no
private-key blocks, recognizable provider tokens, credential-bearing URLs or
literal secret/password assignments. JSON/source-bearing data was inspected as
data, not executed. Content is synthetic premises, public-contract examples,
preparation/review evidence and local provisioning detail. No raw device capture,
customer data or endpoint credentials were found. Automated patterns are not a
universal secret guarantee; the owner must review the exact bytes before release.

The environment report discloses the account name `mafasa`, UID 1000, absolute
home/workspace paths, WSL/kernel/platform information and public PyPI origin.
These are operational/personal metadata, not credentials. The other five files
and hash lock have no discovered email/address credentials or home-account paths.
Exact frozen retention therefore needs the owner's explicit agreement to publish
that metadata. If it must remain private, do not silently redact the pinned
report: retain its authoritative bytes in controlled storage and publish a clearly
separate sanitized setup companion, accepting that public authority recovery will
then remain external. This privacy choice is the only retention alternative
identified here; wholesale staging or archive migration is unnecessary.

After separate approval, the smallest correction is one additive documentation
checkpoint containing these seven exact additions, this investigation report and
a portable setup/recovery navigation amendment to the existing README. Explain
external Python/wheel prerequisites, keep the accepted implementation pinned for
historical replay, and distinguish archive-recoverable links from deliberately
external historical context. No frozen report needs editing. The 27 exact
duplicates need not be republished as standalone files just to repair navigation;
point current navigation to their committed recovery locations. Historical links
in immutable evidence remain historical and must not be rewritten.

## 6. Preservation and owner decision

All 63 original paths, sizes and hashes remain unchanged, as do acceptance and
execution reports, backend/application sources, tests, dependencies and the
36-record ledger/revision. Persistent inputs/results and the accepted S6 retained
bundle remain unchanged. New command results exist only beneath the new
investigation workspace. Original branch/main/remote-tracking refs are unchanged;
no artifacts were removed, moved, renamed, ignored or staged.

Accepted verification remains 4,648 passes, 35 optional CAD/PDF skips and one
sandbox socket setup error followed by its permitted isolated pass; no recorded
product failures. The earlier command, clean-build, recovery, determinism and
27-row acceptance evidence remains applicable. This investigation adds only its
bounded fresh-checkout findings. XFS, reboot and power-loss behavior remain
unverified. Empirical accuracy, causal truth, generated alternatives, multi-step
planning and global optimality remain unestablished. IN-001 and CI-001 remain
open and unselected; no successor or architecture expansion is selected.

**Exact next owner decision:** approve an additive retention/setup checkpoint for
the seven specified files and existing status/setup navigation, including the
environment metadata disclosure, or choose the private-authority/sanitized-setup
alternative. Separately provide authenticated read-only remote access so the main
tip can be verified. Integration/push needs its own later approval after that
verification. No cleanup decision is needed to make this bounded correction.

## 7. Disposition of every unmatched artifact

The committed inventory supplies byte sizes, digests and historical purpose for
each exact path. R = retain for governing authority or setup audit; E = retain for
accepted historical experiment reproduction; H = historical context, with no
missing operative rule or current execution dependency identified. H still needs
preservation and separate owner disposition; no file is certified disposable.

| Exact path | Disposition and reason |
| --- | --- |
| `docs/superpowers/proposals/2026-09-15-bounded-decision-workflow-delivery-proposal.md` | H — superseded proposal/consolidation; current governing authority and application acceptance are separate. |
| `docs/superpowers/proposals/2026-09-15-one-step-intervention-projection-proof-design.md` | H — cited historical reasoning/review/preparation; corrected governing design/plan committed; full-context audit still needs this file. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-complete-output-resource-correction-review.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-manifest-pre-hostile-target-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-manifest-pre-unknown-single-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-pre-hostile-target-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-expected-oracle-pre-unknown-single-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-final-preexecution-closure-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-preexecution-rehearsal-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-redesigned-execution-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-redesigned-preexecution-rehearsal-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-request-carriage-redesign-investigation-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-resource-calibration-continuation-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-satisfied-governing-premise-discrepancy-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-discrepancy-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-manifest-pre-hostile-target-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-manifest-pre-unknown-single-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-pre-hostile-target-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-static-output-proof-pre-unknown-single-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-structural-read-matrix-pre-hostile-target-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-structural-read-matrix-pre-unknown-single-correction.json` | H — superseded oracle/proof/matrix lineage; accepted corrected objects retained separately; preserve original backup. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-unknown-single-output-correction-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-11-brc-exp001-slice-a-unknown-single-output-discrepancy-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-12-brc-exp001-mode-b-preexecution-rehearsal-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-12-brc-exp001-slice-a-completion-report.md` | H — historical BRC preparation, failure, calibration or correction context; final accepted rules/results retained separately. |
| `docs/superpowers/reports/2026-09-12-brc-exp001-slice-a-output-resource-amendment-report.md` | H — operative amendment retained in committed synthesis §19; this full historical verification narrative is not retained there. |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-delivery-independent-review.md` | R — frozen review authority pinned by the approved application plan/design. |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-implementation-readiness-report.md` | R — S1-approved measured preparation/resource-policy authority. |
| `docs/superpowers/reports/2026-09-15-bounded-decision-workflow-persistent-environment-report.md` | R — S1-approved environment/provisioning authority and setup audit. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-manifest.json` | E — external input/manifest required by the accepted proof recovery boundary. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-candidate-package.json` | E — external input/manifest required by the accepted proof recovery boundary. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-independent-review.md` | H — cited historical reasoning/review/preparation; corrected governing design/plan committed; full-context audit still needs this file. |
| `docs/superpowers/reports/2026-09-15-one-step-intervention-projection-preexecution-report.md` | H — cited historical reasoning/review/preparation; corrected governing design/plan committed; full-context audit still needs this file. |
| `docs/superpowers/reports/2026-09-15-post-experiment-objective-and-architecture-consolidation.md` | H — superseded proposal/consolidation; current governing authority and application acceptance are separate. |
| `docs/superpowers/reports/2026-09-15-source-agnostic-backend-gap-assessment.md` | H — cited historical reasoning/review/preparation; corrected governing design/plan committed; full-context audit still needs this file. |
| `docs/superpowers/specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md` | R — approved semantic/acceptance authority; referenced throughout S1–S7. |

END OF BOUNDED DECISION WORKFLOW PUBLICATION READINESS
