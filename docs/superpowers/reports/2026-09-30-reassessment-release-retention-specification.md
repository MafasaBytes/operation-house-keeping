# Reassessment release evidence — local retention specification

2026-09-30. **Proposal only.** This authorizes neither package creation nor
execution. The only products of this task are this specification, the
[canonical manifest](2026-09-30-reassessment-release-retention-manifest.json)
and the [decision receipt](2026-09-30-reassessment-release-retention-decision.md).

## 1. Checkpoint and answer

HEAD is `e795844b441d8e5471494e715f936892f311e0e8`, exactly the supplied
checkpoint; there are no intervening commits. The committed
[corrected reconciliation](2026-09-30-post-reassessment-corrected-reconciliation.md)
verifies as `ea300dd6ba8b7d8057adde1c646fef555dc9bc664669c7812150546cd51a0b91`.
The [acceptance record](2026-09-30-reassessment-slice5-and-final-owner-acceptance.md)
verifies as `a98286666e9de0e24db10e6c6dda5fd7719510442151ce3e9b76b03d4cee7a9c`.
Its historical checkpoint/untracked observations are not rewritten.

**Retain 3,688 additional unique byte sequences (72,143,771 bytes), plus this
manifest and its interpretation.** Another checkout also needs the exact Git
objects and committed archives named in the manifest. A checkout containing
only a source-tree export, or a shallow checkout missing the historical commits,
is insufficient. No fresh remote availability is asserted.

The manifest inventories 13,238 source aliases: 13,173 regular files, 63 symlinks
as inert metadata and two special objects as inert metadata. It also records
64 actual directory observations for the abandoned first V1 preparation and
both delivery corpora. Directory observations describe the present retained
topology, not a reconstruction of its historical state. This is an evidence
closure, not a filesystem backup or an executable environment image.

## 2. Retention boundary and existing recovery

| Evidence obligation | Minimum retained material / recovery |
|---|---|
| Accepted authority | Exact acceptance and reconciliation from Git; preparation package and prior NM authority from committed archives; owner approval, consolidated plan, fresh schedule and later funding/exception records. Fixture permissions remain historical declarations, not newly issued authority. |
| Fixture/oracle amendments | Preparation authority, carriage amendment and receipt, overlays, corrected revision/retention/dispatcher expectations, frozen manifests and exact repair diffs. Existing nested archive members are referenced by container and member hashes. Additional missing historical evidence ZIPs are retained once as blobs. |
| Executable and harness provenance | Exact application, execution and harness commits; transitive campaign driver/launcher/controller/routing sources; historical versions, preflights and amendments. All 172 source entries in each of the fresh matrix and FINAL build descriptors match their respective Git commits. Another 114 historical application/public-module file hashes match their actual commits. |
| Fresh qualification and functional scope | M180 inputs and outputs, boundary artifacts, C6 controls, G-clean, qualified G-app recovery/delivery bundles, H4 copies/replays and H-v1 source/replay; logs and comparison records, not just receipts. |
| Final qualification | Replacement control and V2, V3 and FINAL collection/result/diagnostic streams; detail/specification files, parent/child environment observations, routing, substitution, ballast/fetch/address-space evidence, corpus inventories and closeouts. Both external delivery corpora and negative-destination observations remain distinct. |
| Honest adverse history | Full retained ledger and command logs; original failed full-suite streams and correction, prior repair outcomes, both consumed V1 failures, wrong-environment control/V2 stop, withdrawn claims, resource violations, missing peak disclosure and the narrowly limited V1 functional exception. No refund or retrospective compliance. |
| Accounting and administrative closeout | All 3,592 numbered ledger records through 3595, the six other index files, ordered-file reconciliation 0282, external export registrations, Git-growth and owner-acceptance closeout records. Historical gaps/branching are preserved. |

Providers are resolved per byte identity: 93 aliases use direct Git blobs,
7,852 use committed ZIP members, 485 use members of four additional ZIP blobs,
and 4,743 use the 3,688 new unique blobs. The other 65 aliases are metadata-only.
The manifest's archive table has 12 existing Git archive providers and four
additional archive providers. Earlier slice archives also remain directly
recoverable where listed as Git members; they are not recopied merely because
their loose runtime aliases exist.

Each `members` array uses the declared `member_columns`. Its source prefix,
relative locator, role IDs, byte length, SHA-256, observed source allocation,
provider and destination rule are explicit. The exact logical destination for
`PREFIX:REL` is `evidence/PREFIX/REL`; physical deduplication uses
`objects/<sha256>`. Provider IDs refer to the `providers` map. ZIP member chains
are ordered from outer to inner archive; each outer archive has its own size
and digest. `source_recovery` separately names historical Git commit/path bytes.
Aliases are mappings, not instructions to overwrite the original absolute path.

The complete closure does not mean every historical scratch file is required.
Checkout/venv forests, interpreter installations, wheels, caches and temporary
test workspaces are excluded. Superseded loose pre-campaign input/output copies
are omitted in favor of retained archives, original records and the accepted
fresh campaign evidence. The manifest names excluded scratch roots and counts
omitted aliases. Abandoned repairs and all excluded material remain untouched
in place. No exclusion repairs a historical violation or changes its outcome.

## 3. Found evidence, missing evidence and limits

The environment stop report was located at
`R/regressions/rel5-V2-boundary/continuation-stop.json`: 6,064 bytes,
`41161b77f57862e06eda2c0148228759fc665b83ee1fe1807c0eee4d716f5df9`.
It is selected as additional bytes. No replacement report was synthesized.
Here and in the manifest, R is the qualification root in `source_prefixes`.

Record 3440 explicitly says the unauthorized memory probe had **no retained raw
evidence in R**; its figures appeared only in the session transcript. Record
3442 corrects their use. The raw probe output/transcript is not recovered by
this package. Preserve the disclosure and correction; do not turn their
statements into a qualified observation. Likewise, V1's missing peak evidence
remains missing. The first V1 started no pytest child; the replacement's 19
functional passes did not make either V1 attempt compliant.

Static inspection verified 81 selected successful bundle manifests and 486
member commitments, with no missing/mismatching members. It decoded 237 retained
diagnostic chunks (1,401,652 bytes) without executing their content. All 113
registered external exports still match their recorded length and hash.
The package references the accepted FINAL outcome of 5,304 nodes, 5,269 passed
and 35 expected skips, including all 19 delivery tests. This planning task is
not a new qualification or a new acceptance decision.

### Evidence inspection is not execution reproduction

| Role | Exact revision |
|---|---|
| Accepted application / fresh M180, C6, G-clean, H4 | `c321f2e096a71a43bf65787f6f1605c4031266e7` |
| FINAL execution | `f28de9e900c700d910eb5edf2b0e6f8c336472fe` |
| Verified harness | `509a43b1f71a3ed83bdcff7055512c28535b2b37` |
| Historical S6 recovery | `c37c24ee50667121d6b2dc4739aa3b7d12825c96` |
| Historical H-v1 | `250da5e66479ee1dd2e7c24cd81905509ffe5969` |

Historical build files remain unchanged and separately identified in
`accepted_builds`. The archive supplies no portable runtime. Qualification used
CPython 3.13.11, Linux x86_64, SOABI `cpython-313-x86_64-linux-gnu`, the approved
absolute cp313-bdw001 interpreter, environment identity
`693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`,
and wheel-set commitment
`26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
Provisioning manifests, lock material and verification source are retained as
data. Installed binaries, distribution trees and wheel files are not included.
OCP, pdfplumber, pypdf and pypdfium2 were absent in the approved environment.
Historical replay additionally requires its own build/environment identity.

Reassessment's application boundary is ext4; shared selection retention accepts
ext4/XFS, but qualification establishes local ext4 evidence, not XFS testing.
Machine-specific delivery-test ROOT and descendant routing are separate test
requirements. Neither this package nor copying fixture permissions authorizes
fresh execution. No tests, examples, provisioning verifier or recovery helper
were run to prepare this specification.

## 4. Disclosure and distribution screen

Selected regular bytes and decoded diagnostics were screened for private-key
headers, AWS access-key forms, GitHub token forms and credential-bearing HTTP
URLs. The 16 archive providers were also inspected recursively as data: 22 ZIP
containers, 20,311 members and 305,719,332 expanded bytes; no matches or unsafe
absolute/parent-traversal member names were found. Additional payload blobs
were checked for credential assignments, authorization-header tokens and email
forms; none matched. This is pattern triage, not a proof of absence.

Host locators occur in 1,296 selected source files. Username, absolute runtime,
interpreter and checkout paths, timestamps, environment versions, hashes,
Git metadata inventories and local evidence references are deliberately
unredacted. The payload carries synthetic engineering examples, fixture
attestations/permission pins, diagnostics and failure traces. Fixture attestations
are not credentials and confer no new authority; their provenance still needs
appropriate disclosure. Raw `.git/config`, credentials directories and installed
third-party runtime bytes are excluded.

No root LICENSE file was found. Existing committed material and nested fixture
or source excerpts do not by themselves establish redistribution permission.
Third-party provenance and rights require separate review before distribution.
The owner's prior local approval for the reconciliation's metadata does not
approve this broader evidence package for publication. Obtain explicit approval
for local retention of the full manifest-selected contents. Any later redacted
export would be a separately identified derivative, never a rewrite of evidence.

## 5. Bounded future creation and static recovery

The proposed format is deliberately simple and uncompressed: a 32-byte header,
the exact canonical manifest, then each additional blob once in ascending
lowercase SHA-256 order. The 16-byte magic is `OHK-RETENTION-1` followed by LF;
two unsigned 64-bit big-endian values give manifest length and blob count.
There is no alignment padding, compression, trailer, ownership or executable
metadata. The manifest specifies every offset by cumulative byte length.
The package's eventual digest is unknown until creation; none is invented here.

This indexed format avoids tar padding and duplicate per-member headers in a
tight export category. It needs a small, separately reviewed, one-off standard
library reader/writer; no maintained recovery helper or dependency is selected.
No such implementation or archive has been created by this task.

Proposed destinations, both already-existing category directories:

- `R/exports/reassessment-release-evidence-v1.pack` — export category, once.
- `R/recovery/reassessment-release-evidence-v1-verification.json` — recovery
  category, once, at most 65,536 bytes, including a failed-verification receipt.
- Five new ledger records in `R/indexes`, collectively at most 81,920 bytes:
  one reservation start, three planning-document export registrations and one
  terminal closeout. Reserve record overhead before writing. This proposal is
  not permission to mutate or bypass the accounting controller.

After separate approval:

1. Recheck HEAD, both starting commitments, all selected source hashes and
   providers, current census, backing space, no pending reservation and exact
   unused allocation. Stop on drift. Register the three planning documents once;
   preserve consumed charges and historical links. Do not backdate registration.
2. Reserve the complete creation/verification/ledger envelope. Use exclusive
   creation in the category directory with no symlink traversal. Stream sources
   through a 1 MiB buffer directly into the single package. No copied runtime
   staging tree, temporary archive or second final archive is needed. Recheck
   each digest while writing; changed bytes cause a retained failure, not repair.
3. Flush the package and its directory; independently read its header, verify
   the externally approved manifest hash and canonical bytes, exact size and
   blob count, sorted unique object keys, cumulative offsets and every blob hash.
   Refuse truncation, overlaps, duplicate names, unexpected trailing data,
   unsupported version or excess declared sizes. No application import occurs.
4. Resolve existing providers only from the specified local Git commits/paths,
   verify outer archive hashes and bounded nested member chains, and compare
   the selected leaf length/hash. Do not execute `reconstruct.py`,
   `seal_and_recover.py`, provisioning scripts or archived Python. The largest
   ZIP member observed in this provider scan is 4,461,128 bytes; total scan and
   depth bounds are in the manifest. Use at most 256 MiB for static nested-archive
   buffers; this is a planned working-memory limit, not a measured RSS claim.
5. Check manifest-to-member closure, the original ordered ledger reconciliation
   and subsequent hash links, frozen amendments, environment observations,
   collection-to-terminal-node equality and expected skips. Preserve distinctions
   between raw-file hashes and structured build/environment commitments.
   Emit a concise receipt with all provider/mismatch counts and actual storage.
   This is inspection of retained outcomes, not execution or requalification.
6. Close out actual logical bytes, `st_blocks * 512`, non-directory entries and
   directories, including the closeout itself. If anything fails, retain the
   partial package and failed receipt, stop, and request a decision. No retry,
   cleanup or contingency is part of the recommended minimum.

**Safe extraction, if separately selected:** use a new private destination and
exclusive no-follow regular files named only `objects/<64 lowercase hex>` plus
the manifest. Reject absolute paths, `..`, backslashes, drive prefixes, NULs,
duplicate normalized names, links, devices and FIFOs. Do not apply archived
modes, owner IDs or timestamps. Validate lengths/hashes before making a member
available. Preserve logical source aliases in the manifest instead of creating
multiple copies or symlinks. Nested ZIPs are inspected for the exact selected
member only, never passed to bulk `extractall`. Do not restore to historical
runtime paths. Full extraction is excluded from the minimum allocation below.

## 6. Storage and ledger decision

The manifest's `storage` fields give exact package/payload lengths and the
full-extraction alternative. The decision receipt supplies final planning-file
sizes and the combined request. Format size is arithmetic over measured source
bytes, not a compressed-size estimate. Source aliases represent 228,916,282
logical bytes and 268,656,640 observed physical bytes; they are not charged again
as newly created data. Of that allocation, regular files occupy 268,398,592
bytes. Duplicate aliases do not imply duplicate new package objects.

Fresh R census including all registered exports: 5,688,119,189 logical bytes,
6,467,600,384 physical bytes, 161,730 entries and 72,561 directories. Add once
both external delivery corpora, the negative-filesystem root and positive Git
growth since record 3563: 11,883,152 logical bytes, 16,523,264 physical bytes,
1,296 entries and 63 directories. Git growth includes later administrative
commits; it is not silently omitted because the runtime ledger stopped earlier.
The fixed-parent charge remains 76,560,100 logical bytes.

Before registering these planning files, available global headroom is
2,302,729,691 logical bytes, 3,266,322,432 physical bytes, 77,138 entries and
24,121 directories. Export headroom, after that Git growth, is 82,381,004 bytes;
recovery headroom is 59,506,994 bytes; index headroom is 134,389,805 bytes.
The runtime backing filesystem reported 868,364,992,512 available bytes at the
read. These are snapshots, not a future reservation or free-space guarantee.

Unused original preparation capacity is only 24,693,882 export bytes,
4,053,805 index bytes, 151 entries and eight directories. It cannot fund the
proposed package. Request a **new local administrative retention allocation
within the existing category/global ceilings**, not a refund or reuse of a
consumed qualification attempt. No category/global increase is proposed.

The minimum has zero temporary disk coexistence beyond the final package,
planning documents, one verification receipt and five ledger records. Existing
sources remain throughout. Creation adds seven filesystem files and zero
directories; registering the three existing planning files adds three accounted
external entries. The package's 3,689 logical members are not 3,689 filesystem
entries. Directory topology and special-object descriptions live in the manifest.

Future physical allocation cannot be known exactly before writing. Report exact
measured source allocation separately from the 4,096-byte data-rounding estimate
and the conservative reservation bound: total charged logical growth plus
4,096 bytes per accounted file, with zero new directories. Actual allocation,
metadata changes and any transient/unlinked allocation must be observed and
closed out; this is not hard filesystem enforcement. No ledger change occurred
during planning. Full object-pool extraction exceeds current recovery headroom;
it would require its own allocation decision and is not a hidden prerequisite
for streaming inspection.

## 7. Owner gates

Approve or revise the exact manifest-selected local retention scope, including
host metadata and the stated unrecoverable probe/peak gaps. Approve the indexed
format, one creation and one static streaming verification, the one-off
reader/writer review and the separately requested administrative allocation.
Decide separately whether historical Git reachability needs a future Git bundle;
that export, its size and its rights review are outside this minimum. Do not
claim independence from Git when relying on the listed Git providers.

Publication, a portable runtime, full filesystem extraction, maintained helper,
test portability and diagnostic implementation remain deferred. There is no new
semantic capability, qualification campaign or successor milestone. Slice 5 and
milestone acceptance are unchanged; IN-001 and CI-001 remain open and unselected.
