# Measurement-result reassessment: Slice 5 and milestone owner acceptance

Date: 2026-09-30. Authority: the owner's conditional administrative-closeout
instruction in this session. Verification was read-only; no tests or application
commands were rerun. Everything remains local.

## 1. Two distinct decisions

**Slice 5 acceptance:** accepted after verification of the retained qualification,
matrix, controls, delivery and recovery evidence described below.

**Maintained measurement-result reassessment milestone acceptance:** accepted
separately, incorporating the retained earlier slice acceptances and the verified
Slice 5 release closure. No unresolved release obligation remains within this
approved scope. These decisions do not authorize a successor milestone.

The accepted claim is bounded reassessment of supplied scalar observations
against nominated hypotheses and qualified support, with explicit uncertainty,
provenance, manual adoption and independently recomputing replay. Acceptance
does not establish empirical accuracy, causal diagnosis, automatic hypothesis
generation, automatic adoption or general robustness. The finite qualification
and same-author oracle limitations remain disclosed. IN-001 and CI-001 remain
open and unselected.

## 2. Exact source, execution and environment identities

These identities have different roles and must not be substituted for one another.

| Role | Exact identity |
|---|---|
| Accepted application candidate | `c321f2e096a71a43bf65787f6f1605c4031266e7` |
| FINAL execution revision | `f28de9e900c700d910eb5edf2b0e6f8c336472fe` |
| Verified local harness commit | `509a43b1f71a3ed83bdcff7055512c28535b2b37` |
| Harness commit parent | `29fa81648a35e66525a8172775d5954dfc92390b` |
| Fresh matrix administrative harness revision | `8d0f09f4449fe3c3eaa21460c75f4d41a9446c69` |
| Approved environment identity | `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a` |
| Installed wheel-set commitment | `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1` |
| Provisioning manifest SHA-256 | `da87127a571195b4129e6fefd393da39d57819667ecba4f1f8a37d5f1984bc34` |
| Lock text commitment | `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e` |

The approved interpreter is
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python`,
CPython 3.13.11, SOABI `cpython-313-x86_64-linux-gnu`. Read-only identity
verification matched the retained parent/child identities, installed dependency
commitments and absence of OCP, pdfplumber, pypdf and pypdfium2. No dependency
changes occurred. Qualification children were bound by the frozen absolute-path
launcher, including replacement-environment Python descendants.

Git comparison establishes identical `applications/` and `backend/` trees at
the candidate, FINAL revision and verified harness commit. All 172 entries of
the retained reassessment build's source manifest were independently checked
against committed blobs at `509a43b1f71a3ed83bdcff7055512c28535b2b37`.
FINAL's fixture, reporting and harness repairs do not relabel the older runs.
The acceptance commit is an administrative descendant, not a new execution.

## 3. Preserved commitments and recovery locations

The owner-supplied completion-report SHA-256 verified exactly:
`447fccef3a26fad37965bc6c28278bd446866238e3bd4bd984d1d66f0412d95d`.
The immutable report is
[approved-environment continuation result](2026-09-29-reassessment-slice5-approved-environment-continuation-result.md).
Every file commitment linked in that report and every artifact in manifest v9
was rehashed successfully.

- Manifest v9: `ba9c6badf0ace3744bcd4c40eae972c929ab4964112f66d91dd54aba6c3757f0`.
- Exact successor diff v9: `219e6f89f545ea5df09e6ff549658c64980de039ab918aea6ecd0cdd427d6255`.
- Manifest v8: `c1e280203f0db4bdc37055431ea5e0190ab3070b087e4c093036bc9b50e9bd09`.
- Repair diff v8: `f8845787925b1bd6769a51201cfab9bc675b9d07b2d559bb6aa836612b058acf`.
- Environment stop report: `41161b77f57862e06eda2c0148228759fc665b83ee1fe1807c0eee4d716f5df9`.

In this record, **R** means
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1`.
The retained local evidence under R and registered external reports remains
recoverable in place; this is not a claim that every runtime artifact is in Git
or recoverable from a repository-only clone. Registered external exports passed
their byte-count and SHA-256 census checks. Source revisions remain in local Git.
The original provisioning environment remains a reproduction prerequisite.

Pre-acceptance ledger tip: `R/indexes/3589-record.json`, SHA-256
`07bb65962db717fd761e4aba2beec13d603621cdaea35021189e273bbec25ffc`.
Historical branching links are preserved under the existing ordered-file
reconciliation in record 0282; every listed historical file commitment verified.
The subsequent chain verifies through record 3589. No unbroken-chain claim is
made about the reconciled earlier records.

## 4. Replacement prerequisites and FINAL

| Attempt | Retained outcome | Qualification disposition |
|---|---|---|
| `rel5-control-env-replacement-1-accounting` | Seven checks passed | Compliant outer closeout |
| `rel5-V2-env-replacement-1-boundary` | RED: 30 passes and the intended MemoryError; GREEN: 31 passes | All ten gates and closeout passed |
| `rel5-V3-skips-bytecode` | 111 passed, 35 expected skips, 146 nodes | All seven gates and closeout passed |
| `rel5-FINAL-full-release` | 5,269 passed, 35 expected skips, 5,304 nodes | All sixteen gates and closeout passed |

FINAL collection and results were independently parsed: indices are unique,
each collected identity's SHA-256 matches, and every index has exactly one
matching terminal outcome. There are zero failed, errored, incomplete or
never-executed nodes. All 19 nodes in
`tests/reassessment_profile/test_delivery.py` are present and passed.
Three long identities are omitted from the compact detail view; their full
identities are retained and verified in the authoritative collection stream.
They are not missing executions.

The exact 35 skipped identities match the frozen optional-extra manifest: 23 PDF
and 12 CAD nodes. All retained diagnostic chunks were decoded and checked
against their byte counts, hashes and expected absence reasons, in both V3 and
FINAL. No skip exception was introduced.

FINAL stream commitments:

- `R/regressions/rel5-FINAL-full-release/run/collection.jsonl`:
  `2a15e8118d8212c5a54a7db918a85e8704b935a7b15acd4c8e614a94f2c3c93d`.
- `R/regressions/rel5-FINAL-full-release/run/results.jsonl`:
  `6bd19b4bda84da2469df4efbe4ffc816c104ba4cb99cec7851d18939a4bd70a4`.
- `R/regressions/rel5-FINAL-full-release/run/storage-observations.json`:
  `24e8051f61c751e259a095d408dc8269ff615d9b6d5fb41516a71b5a9ea3d808`.
- Final gate record 3581:
  `bd7e94e1a883415b4c747ad3422de701388afa14637f1ef576fd7e2ff01b201e`.
- Final closeout record 3583:
  `c44101dc2b7abe9e3afba207383ac111e2fc266a6b5daa740cd3679e368f876e`.

The controller control evidence hash is
`7cca2236b585685c890c97726668b2ec2c1088e46d4650d626e43e9843958eb7`.
It retains a deliberate two-byte write against a one-byte child allowance,
stopped as `storage_reservation_exceeded`, plus duplicate-destination and
parent-composition refusals. Its outer allocation remained compliant.
Journal, symlink and internal/external accounting were exercised. Literal
temporary-path and replacement-environment routing used the actual wrappers.

V2 retained matched ballast, the intended RED failure, and GREEN's applied and
restored 1 GiB node allowance. FINAL independently retained application and
restoration of that approved node allowance. Production caps and assertions
were unchanged. FINAL used the separately fresh delivery corpus with ROOT
substitution recorded; the historical corpus and pre-existing bytecode remained
unchanged. The release root was Git-clean, not byte-for-byte pristine.

## 5. Resource verification

Closeouts were recomputed from reservation baselines, final inventory and the
closeout record itself, rather than treating pre-closeout measurements as totals.
Entries count all non-directory objects; directories are separate.

| Stage | Logical bytes actual / allowance | Physical bytes actual / allowance | Entries actual / allowance | Directories actual / allowance |
|---|---:|---:|---:|---:|
| Replacement control | 16918 / 1376256 | 81920 / 1769472 | 18 / 64 | 5 / 16 |
| Replacement V2 | 141718 / 13893632 | 299008 / 14630912 | 31 / 80 | 19 / 50 |
| V3 | 2056389 / 72613888 | 5824512 / 82853888 | 523 / 900 | 509 / 800 |
| FINAL in R | 802510156 / 1082130432 | 1015218176 / 1508114432 | 39903 / 48000 | 22407 / 28000 |
| FINAL separate corpus | 5878900 / 8388608 | 8179712 / 13631488 | 634 / 1024 | 28 / 40 |
| FINAL negative destination | 2 / 2097154 | 0 / 2207746 | 1 / 17 | 2 / 5 |

The corpus has 633 regular files and one symlink. External destinations and
prior Git growth are charged once. FINAL's combined descendant envelope remains
1092616194 logical bytes, 1523953666 physical bytes, 49041 entries and 28045
directories. Category allocations, descendant composition, captured child
identities and storage records were checked. FINAL retains 1,416 storage samples
with no observed violations; reporting has no truncation or incomplete-evidence
waiver. Monitoring measures sampled allocation, not hard filesystem enforcement
or an exact transient/unlinked-allocation peak. Physical bytes use `st_blocks *
512`; zero blocks on the negative destination does not mean zero filesystem
overhead.

The read-only pre-administration census including registered exports was
5687528935 logical bytes, 6466990080 physical bytes, 161723 entries and 72561
directories. Including the separately charged Git growth, FINAL corpus and
negative destination once leaves headroom of 2309319562 logical bytes,
3275259904 physical bytes, 77801 entries and 24154 directories. The unchanged
fixed-parent charge is 76560100 logical bytes. No reservation was pending.

Administrative record/status/Git work receives a distinct draw from unused
original preparation capacity: 4194304 export bytes, 2097152 index bytes,
8388608 physical bytes, 100 entries and 16 directories. The complete draw is
reserved before writing. After reserving it, conservative global headroom is
2303028106 logical bytes, 3266871296 physical bytes, 77701 entries and 24138
directories. Ledger records retain composition, preservation baseline and the
final actual closeout. These figures do not refund any consumed attempt.

## 6. Matrix, controls, delivery and recovery applicability

The fresh M180 schedule hash is
`6a945fb2726d75efc2380434c37c31f67570793144a0193aabbf9dab295a9430`.
Its 180 unique identities exactly match the 180 passing comparison records:
72 E, 40 B, 40 V/R and 28 D rows. Recorded command stream hashes were checked,
successful result projections and traces matched frozen schedule commitments,
and receipts bound actual result and manifest bytes. Expected refusal rows
retain their original classifications. Complete E bundles, clean delivery
bundles and four recovery copies passed manifest-member verification.

The six C6 comparisons retain the expected member/root race refusals, write
fault, durability-unknown fsync outcome, interruption and publication ordering.
Their command logs and published manifests verify. G-clean retains three
isolated evaluate/verify/replay children and matching semantic files. G-app's
qualified rerun at c321 retains two passing nodes (43 descendant operations),
including historical S6 recovery and complete/sparse-root delivery. Its first
attempt remains noncompliant for uncharged bytecode growth.

H4 retains four copies, eight verify/replay children and six recomputed semantic
files per case. All four copies remain byte-identical to their source bundles;
all six replay files per case agree. H-v1 retains its separate historical
verify/replay execution and four matching replay files. Historical environments
and source identities have not been renamed as FINAL runs.

| Evidence | Actual revision | Actual retained build identity |
|---|---|---|
| M180, C6, G-clean and H4 reassessment | `c321f2e096a71a43bf65787f6f1605c4031266e7` | `nr.build.v2` ID `08fbcdd783743a64d306d07f45195cc8db8b3570fceaaf04a73788be35792d50`; build file SHA-256 `2ed7cdf000d26937e5b2ba6f36c18561c15c2642231be1e739a64ae0ea7fb918` |
| G-app current delivery | `c321f2e096a71a43bf65787f6f1605c4031266e7` | Build file SHA-256 `d1ebb41d0c547dbe663dbc5455f3ef2b3f7fcbfebf5cb8069f46269b6af20980` |
| G-app historical S6 recovery | `c37c24ee50667121d6b2dc4739aa3b7d12825c96` | Build file SHA-256 `7bd8cb7906f82f16b18ca28a5356b815f365cbe97c760a222eca56818786126d` |
| H-v1 historical governed replay | `250da5e66479ee1dd2e7c24cd81905509ffe5969` | `governed-executable-build.v1`; build file SHA-256 `6d25dea1635567f4a6838b5252f25d448f1a4194657cb54ba30bbc705f8afafb` |
| FINAL reassessment | `f28de9e900c700d910eb5edf2b0e6f8c336472fe` | `nr.build.v2` ID `67a1f1265ffc04f0a89b5419f612b2bea3e613072ba76a04579ee32ae9ce9b60`; build file SHA-256 `3a4d021f1f8d35e4ae53d5b06a9faabbdc8b17e7558fc071250889b6e3f0c289` |

The c321 and FINAL reassessment build descriptors differ only in checkpoint
and derived ID. Source and environment manifests, contract, resource-policy
and supported next-measurement-contract commitments are equal. This exact
comparison, the committed-source comparison, and FINAL's fresh 19 delivery
tests establish applicability without asserting that M180 or historical
recovery ran at f28. H-v1 used its recorded historical interpreter under
`s7-release-Gvdefi/environment/bin/python`; its build records CPython 3.13.11
and dependency lock SHA-256
`7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`.
It is not relabelled as a cp313-bdw001 qualification launch.

## 7. Release closure and preserved adverse history

The fresh matrix, six controls, clean delivery, G-app rerun and recovery close
the earlier readiness obligations. The repaired release fixture and dispatcher
expectation, diagnostic capture, pinned fetch, node accounting, optional skips,
temporary routing, environment binding and resource closeouts are covered by
the frozen correction and successful prerequisite/FINAL records. The scoped
harness commit contains only the three approved adapters. Source recovery,
local evidence retention and environment prerequisites remain explicit above.

Both V1 attempts remain consumed and failed/noncompliant. Original V1 started
no pytest child. Replacement V1 retains its 19 functional passes, corpus-entry
overrun, controller logical/physical/entry overruns and missing peak evidence.
Its exception satisfied only the continuation prerequisite; FINAL passed all
19 again compliantly. Wrong-environment control and V2 remain consumed with
qualification withdrawn. No refund, retroactive reservation change or new
qualification exception is made by either acceptance decision.

The unauthorized unaccounted memory probe in ledger record 3440, correction
3442 and ensuing disclosure remain preserved and excluded from qualification.
The original campaign report and its later correction remain separate artifacts:
the earlier F-full actually had 4470 passes, 75 failures, two errors, 35 skips,
one incomplete and 721 never-executed nodes. Its withdrawn completion claim is
not used here. Earlier noncompliant attempts, abandoned repairs, bytecode,
corpus material and evidence corrections remain untouched.

## 8. Administrative preservation receipt

Only this acceptance record and necessary README/CLAUDE status reconciliation
are selected for the acceptance commit. The unrelated modified historical
`bounded_pytest_runner.py` and all pre-existing untracked evidence are excluded.
The pre-operation Git metadata inventory commitment is
`c0206a35f106300ade6c159681e7b509b99e1ea26474b6ff56bb677f97ab03dd`.
The separately accounted final ledger receipt records the resulting commit,
this record's digest, exact selected paths, actual administrative growth and
preservation checks. The commit identity is reported externally to avoid a
self-referential record.

Verification used SHA-256 over retained bytes, JSON/JSONL parsing, diagnostic
base64 decoding, manifest-member comparisons, ledger baseline/closeout
arithmetic, lstat allocation census, read-only environment provisioning checks
and Git object/tree comparisons. Repeating those read-only checks requires
the paths and commitments above; no application or pytest rerun is needed.

No cleanup, production change, dependency change, push, merge, history rewrite
or successor milestone is part of this closeout. All consumed charges remain
consumed. Both acceptance decisions retain the bounded claim in section 1.

END OF ACCEPTANCE RECORD
